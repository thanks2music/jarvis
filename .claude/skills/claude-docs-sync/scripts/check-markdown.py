#!/usr/bin/env python3
"""Markdown 構文検査 — claude-docs-sync フェーズ2 の横断自己検証で使う。

文章の「内容」ではなく「構文」を検査する。内容の正しさは公式ソースとの照合で担保するが、
構文の破損はレンダリング結果を見ないと気付けないため機械検査に回す。

検出する 5 種:
  1. table-broken      テーブルが block-level 構造で分断され、後続行が段落化している
  2. orphan-delimiter  delimiter 行の直前にヘッダ行がない
  3. link-outside-repo 相対リンクの解決先がリポジトリルートの外
  4. link-missing      相対リンク先のファイルが存在しない
  5. anchor-missing    `#anchor` / `file.md#anchor` の anchor が対象ファイルに存在しない
                       （同一ファイル内リンクも検査する。見出し由来のスラグに加えて
                         手動の `<a id="x">` / `<a name="x">` も有効なアンカーとして扱う）

使い方:
    python3 .claude/skills/claude-docs-sync/scripts/check-markdown.py
    python3 .../check-markdown.py docs/best-practices.md   # 対象を絞る

検査対象は **リポジトリルート基準**で解決する（`git rev-parse --show-toplevel`）。
cwd 基準にすると、別ディレクトリから実行された際に対象 0 件のまま「成功」を返し、
SKILL.md 側の必須ゲート（0 件になるまで修正する）を実質スキップできてしまうため。
**対象が 0 件だった場合はエラー（exit 1）**として扱う。

exit code: 問題 0 件で 0、1 件以上で 1、検査対象 0 件でも 1。
"""

from __future__ import annotations

import glob
import os
import re
import subprocess
import sys

TABLE_ROW = re.compile(r"^\|.*\|$")
DELIMITER_ROW = re.compile(r"^\|[\s:\-|]+\|$")
BLOCK_LEVEL_START = re.compile(r"^(>|#{1,6}\s|[-*+]\s|\d+\.\s)")
# [text](target) — 外部リンク以外。`#anchor` 単独（同一ファイル内リンク）も対象に含める
RELATIVE_LINK = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:)([^)\s]+)\)")
# 手動の HTML アンカー <a id="x"> / <a name="x">。見出し由来ではないため別途収集する
HTML_ANCHOR = re.compile(r"""<a\s[^>]*\b(?:id|name)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
# inline code span（`x` / ``x`` …）。中身はリンクとして描画されないため検査対象から外す
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)


def strip_code_spans(line: str) -> str:
    """inline code span を除去する。

    `` `[a](b)` `` のような「記法そのものを例示している」箇所を実リンクと
    誤検出しないために必要。テーブル判定には適用しない（`|` が消えるため）。
    """
    return CODE_SPAN.sub("", line)


def strip_inline_markup(text: str) -> str:
    """見出しテキストから装飾を除去して素のテキストにする。"""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [text](url) -> text
    text = text.replace("`", "")
    text = re.sub(r"\*\*|__|\*|~~", "", text)
    return text.strip()


def github_slug(heading_text: str) -> str:
    """GitHub の見出しアンカー生成規則を再現する。

    小文字化 → word 文字 / ハイフン / スペース以外を削除 → スペースをハイフンに。
    `\\w` は Unicode 対応なので CJK は保持され、`.` や全角括弧は落ちる。
    例: "4.7 Dynamic Workflows（Opus 4.8〜、公式体系化）"
        -> "47-dynamic-workflowsopus-48公式体系化"
    """
    s = strip_inline_markup(heading_text).lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def collect_slugs(path: str) -> set[str]:
    """ファイル内のアンカー候補を集める。

    2 系統を収集する:
      - Markdown 見出し由来のスラグ（重複見出しは 2 個目以降に -1, -2 … が付く）
      - 手動の HTML アンカー `<a id="x">` / `<a name="x">`（見出しではないため別途拾う。
        これを漏らすと、実在するアンカーへのリンクを anchor-missing と誤検出する）
    """
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except OSError:
        return slugs
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        slugs.update(HTML_ANCHOR.findall(ln))
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if not m:
            continue
        base = github_slug(m.group(2))
        n = counts.get(base, 0)
        slugs.add(base if n == 0 else f"{base}-{n}")
        counts[base] = n + 1
    return slugs


def check_file(path: str, repo_root: str, findings: list[tuple[str, int, str, str]]) -> None:
    lines = open(path, encoding="utf-8").read().split("\n")
    in_fence = False

    for i, ln in enumerate(lines):
        lineno = i + 1
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        stripped = ln.strip()
        prev = lines[i - 1].strip() if i > 0 else ""
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""

        # 1 / 2: テーブル構造
        # GFM 仕様: "The table is broken at the first empty line, or beginning of
        # another block-level structure" かつテーブル成立にはヘッダ行 + delimiter 行が必須。
        # よって block-level 構造の直後にパイプ行が来て、その次が delimiter 行でなければ
        # そのパイプ行は段落テキストとして描画される。
        if TABLE_ROW.match(stripped) and not TABLE_ROW.match(prev):
            if BLOCK_LEVEL_START.match(prev) and not DELIMITER_ROW.match(nxt):
                findings.append(
                    (path, lineno, "table-broken",
                     f"直前が block-level 構造（{prev[:32]}…）でヘッダ/delimiter を欠くため段落化する")
                )
        if DELIMITER_ROW.match(stripped) and not TABLE_ROW.match(prev):
            findings.append(
                (path, lineno, "orphan-delimiter", "delimiter 行の直前にヘッダ行がない")
            )

        # 3 / 4 / 5: 相対リンク（code span 内の記法例示は除外）
        for target in RELATIVE_LINK.findall(strip_code_spans(ln)):
            file_part, _, anchor = target.partition("#")
            if not file_part:
                # 同一ファイル内リンク `[text](#anchor)` — 自ファイルのアンカーを検査する
                if anchor and anchor not in collect_slugs(path):
                    findings.append(
                        (path, lineno, "anchor-missing",
                         f"#{anchor} に対応する見出し / HTML アンカーが同ファイル内に無い")
                    )
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
            abs_resolved = os.path.normpath(os.path.join(repo_root, resolved))
            if not abs_resolved.startswith(repo_root + os.sep):
                findings.append(
                    (path, lineno, "link-outside-repo",
                     f"{target} → リポジトリ外（{abs_resolved}）を指すため GitHub 上で 404")
                )
                continue
            if not os.path.exists(abs_resolved):
                findings.append(
                    (path, lineno, "link-missing", f"{target} → リンク先が存在しない")
                )
                continue
            if anchor and abs_resolved.endswith(".md"):
                if anchor not in collect_slugs(abs_resolved):
                    findings.append(
                        (path, lineno, "anchor-missing",
                         f"{target} → #{anchor} に対応する見出しが {file_part} に無い")
                    )


def resolve_repo_root() -> str:
    """リポジトリルートを解決する。

    cwd 基準にすると、リポジトリルート以外から実行された場合に対象ファイルが 0 件になり、
    「何も検査していないのに成功」を返してしまう。git に解決させることで実行場所に依存しない。
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return os.path.realpath(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.path.realpath(os.getcwd())


def main() -> int:
    repo_root = resolve_repo_root()
    findings: list[tuple[str, int, str, str]] = []

    if sys.argv[1:]:
        targets = sys.argv[1:]
    else:
        # 既定の検査対象は repo root 基準で解決する（cwd に依存させない）
        targets = sorted(glob.glob(os.path.join(repo_root, "docs", "*.md")))
        targets += [os.path.join(repo_root, f) for f in ("README.md", "CLAUDE.md")]

    checked = 0
    for path in targets:
        if not os.path.isfile(path):
            continue
        checked += 1
        check_file(path, repo_root, findings)

    # フェイルセーフ: 1 件も検査できなかった場合は「成功」にしてはならない。
    # SKILL.md は「0 件になるまで修正する」を必須ゲートにしているため、
    # サイレントな 0 件成功はゲートを実質スキップさせてしまう。
    if checked == 0:
        print("❌ Markdown 構文検査: 検査対象が 0 ファイルでした（検査は行われていません）")
        print(f"   repo root: {repo_root}")
        print("   引数のパスが誤っているか、リポジトリ外で実行された可能性があります。")
        return 1

    if not findings:
        print(f"✅ Markdown 構文検査: 問題なし（{checked} ファイル）")
        return 0

    by_kind: dict[str, int] = {}
    for _, _, kind, _ in findings:
        by_kind[kind] = by_kind.get(kind, 0) + 1
    print(f"❌ Markdown 構文検査: {len(findings)} 件検出（{checked} ファイル）")
    print("   " + " / ".join(f"{k}={v}" for k, v in sorted(by_kind.items())))
    print()
    for path, lineno, kind, msg in findings:
        print(f"{path}:{lineno}  [{kind}]  {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
