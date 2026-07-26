#!/usr/bin/env python3
"""Markdown 構文検査 — claude-docs-sync フェーズ2 の横断自己検証で使う。

文章の「内容」ではなく「構文」を検査する。内容の正しさは公式ソースとの照合で担保するが、
構文の破損はレンダリング結果を見ないと気付けないため機械検査に回す。

検出する 5 種:
  1. table-broken      テーブルが block-level 構造で分断され、後続行が段落化している
  2. orphan-delimiter  delimiter 行の直前にヘッダ行がない
  3. link-outside-repo 相対リンクの解決先がリポジトリルートの外
  4. link-missing      相対リンク先のファイルが存在しない
  5. anchor-missing    `file.md#anchor` の anchor が対象ファイルの見出しに存在しない

使い方:
    python3 .claude/skills/claude-docs-sync/scripts/check-markdown.py
    python3 .../check-markdown.py docs/best-practices.md   # 対象を絞る

exit code: 問題 0 件で 0、1 件以上で 1。
"""

from __future__ import annotations

import glob
import os
import re
import sys

# 既定の検査対象。docs/ 直下 + ルートの 2 ファイル（サブディレクトリは対象外）
DEFAULT_TARGETS = sorted(glob.glob("docs/*.md")) + ["README.md", "CLAUDE.md"]

TABLE_ROW = re.compile(r"^\|.*\|$")
DELIMITER_ROW = re.compile(r"^\|[\s:\-|]+\|$")
BLOCK_LEVEL_START = re.compile(r"^(>|#{1,6}\s|[-*+]\s|\d+\.\s)")
# [text](target) — target が http(s): / mailto: / # 単独 で始まらないものを相対リンクとみなす
RELATIVE_LINK = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)\s]+)\)")
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
    """ファイル内の全見出しからアンカー候補を集める（重複見出しの -1 サフィックス付き）。"""
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
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if not m:
            continue
        base = github_slug(m.group(2))
        n = counts.get(base, 0)
        slugs.add(base if n == 0 else f"{base}-{n}")
        if n > 0:
            slugs.add(f"{base}-{n}")
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


def main() -> int:
    repo_root = os.path.realpath(os.getcwd())
    targets = sys.argv[1:] or DEFAULT_TARGETS
    findings: list[tuple[str, int, str, str]] = []

    checked = 0
    for path in targets:
        if not os.path.isfile(path):
            continue
        checked += 1
        check_file(path, repo_root, findings)

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
