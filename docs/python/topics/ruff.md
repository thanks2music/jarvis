# Ruff — linter と formatter を 1 つで

> 出典（一次情報）:
> - [The Ruff Linter / The Ruff Formatter / Configuring Ruff / Tutorial (docs.astral.sh)](https://docs.astral.sh/ruff/) — ルールの選び方・カテゴリ・抑止コメント・設定ファイルの探し方・formatter
> - [Ruff v0.16.0 (astral.sh)](https://astral.sh/blog/ruff-v0.16.0) — 既定のルールが 59 から 413 に増えたこと、Markdown のコードブロックの整形
> - [BREAKING_CHANGES.md (github.com/astral-sh/ruff)](https://github.com/astral-sh/ruff/blob/main/BREAKING_CHANGES.md) — 0.16・0.17 の既定の変更
> - [astral-sh/ruff README](https://github.com/astral-sh/ruff) — Ruff が置き換えるツール
>
> 最終更新: 2026-11-08（Ruff 0.17.4・uv 0.13.7・Python 3.15.2 で検証）

Ruff は、Astral が Rust で書いた Python の linter 兼 formatter である。Node.js で言えば **ESLint と Prettier を 1 つにしたもの**で、1 つのバイナリが両方を受け持つ点は Biome に近い。
通し課題での導入（dev 依存・pre-commit・エディタ）は [Step 05: 品質ツール](../steps/05-quality.md) で行った。このページは、そこで扱わなかったルールの体系と設定を引くためのものである。

---

## 1. TL;DR

- **Flake8（とプラグイン）・isort・pyupgrade・pydocstyle・autoflake・Black を 1 つで置き換える**。lint は `ruff check`、整形は `ruff format`。
- **ルールは既定から始める**。0.16 から既定で 413 のルールが有効になり、0.17 で少し入れ替わった（§3.2）。足すときは `extend-select`、`select` は既定を置き換える。
- 1 行だけ止めるなら `# noqa: F401`（同じ行）か `# ruff: ignore[F401]`（同じ行か、**前の行**）。
- `target-version` は書かなくてよい。`pyproject.toml` の `requires-python` から決まる（§3.4）。
- **`ruff format` は Markdown の中の Python のコードブロックも整形する**（0.16 から既定）。README を書き換えられて驚かないように（§5）。

---

## 2. Node.js / Bun との対応

| やりたいこと | ESLint / Prettier | Biome | Ruff |
|---|---|---|---|
| lint | `eslint .` | `biome lint` | `ruff check` |
| lint の自動修正 | `eslint --fix` | `biome lint --write` | `ruff check --fix`（危険な修正は `--unsafe-fixes` も要る） |
| 整形 | `prettier --write .` | `biome format --write` | `ruff format` |
| 整形済みか確かめる | `prettier --check .` | `biome format` | `ruff format --check` |
| 変更を見張って lint し直す | 別のツールで見張る | — | `ruff check --watch` |
| ルールの説明を見る | Web のルールのページ | Web のルールのページ | `ruff rule F401`（端末に出る） |
| 1 行だけ止める | `// eslint-disable-next-line no-unused-vars` | `// biome-ignore lint/...: 理由` | `# noqa: F401`（同じ行）/ `# ruff: ignore[F401]`（同じ行か前の行） |
| 範囲で止める | `/* eslint-disable */` 〜 `/* eslint-enable */` | `// biome-ignore-start` 〜 `// biome-ignore-end` | `# ruff: disable[N803]` 〜 `# ruff: enable[N803]` |
| ファイルの種類ごとに変える | `overrides`（flat config では `files` を持つ設定オブジェクト） | `overrides` | `[tool.ruff.lint.per-file-ignores]` |
| 別の設定を継ぐ | `extends` | `extends` | `extend = "../pyproject.toml"` |
| 設定ファイル | `eslint.config.js` / `.prettierrc` | `biome.json` | `pyproject.toml` の `[tool.ruff]` / `ruff.toml` / `.ruff.toml` |

> **ポイント**: ESLint の旧来の設定と違い、Ruff は親ディレクトリの設定を**合成しない**。公式 docs: "Unlike ESLint, Ruff does not merge settings across configuration files; instead, the "closest" configuration file is used, and any parent configuration files are ignored." 継ぎたいなら `extend` を明示する。

---

## 3. 早見表（コマンド・設定）

### 3.1 コマンド

| コマンド | 何をするか |
|---|---|
| `ruff check` / `ruff check --fix` | lint / 直せるもの（`[*]` が付く）を直す |
| `ruff check --select I` / `--extend-select I` | その回だけルールを置き換える / 足す（[Step 05](../steps/05-quality.md) §3.4） |
| `ruff check --add-noqa` / `--add-ignore` | 今ある違反すべてに抑止コメントを書き足す（途中から入れるとき） |
| `ruff check --show-settings <file>` | そのファイルに効く設定をすべて出す |
| `ruff format` / `ruff format --check` | 整形 / 差分を出して終了コード 1 |
| `ruff rule F401` | ルールの説明を出す |
| `ruff clean` | `.ruff_cache` を消す |

ルールの説明を端末で読む。続きには、何を検査するか・なぜ悪いか・`__init__.py` での再エクスポートの書き方・修正が安全な条件が並ぶ（検証済み）。

実行結果:

```text
$ uv run ruff rule F401
# unused-import (F401)

Derived from the **Pyflakes** linter.
…（中略: 121 行）…
```

### 3.2 ルールコードと既定のルール

ルールコードは「英字の接頭辞 + 数字」で、接頭辞が由来を表す。`select` などには `F401` のような完全なコードも、`F` のような接頭辞も書ける。

| 接頭辞 | 由来 | 例 |
|---|---|---|
| `F` | Pyflakes | `F401` 未使用の import |
| `E` / `W` | pycodestyle | `E501` 行が長すぎる |
| `I` | isort | `I001` import の並び順 |
| `UP` | pyupgrade | `UP017` `datetime.UTC` を使う |
| `B` | flake8-bugbear | `B006` 可変な値を引数の既定にする |
| `RUF` | Ruff 独自 | `RUF100` 使われていない `noqa` |

既定のルールの移り変わり（BREAKING_CHANGES.md と 0.16 の告知）:

| 版 | 変更 |
|---|---|
| 0.16.0（2026-07-23） | 既定が 59 から **413** に増えた。原文: "Ruff now enables 413 rules by default, up from 59 in previous versions." `B`・`UP`・`RUF` などが入った。一方で、意見の分かれる `E`・`F` の 18 個（`E401`・`E402`・`E701`〜`E703`・`E711`〜`E714`・`E721`・`E731`・`E741`〜`E743`・`F403`・`F405`・`F406`・`F722`）は既定から外れた |
| 0.17.0 | `DTZ001`・`DTZ005`・`DTZ006`・`DTZ007`・`DTZ011`・`DTZ012`・`DTZ901` を既定から外した（"timezone-naive dates and datetimes ... are appropriate in many applications"）。他の `DTZ` は残る。構文エラーにあたる `F406` は既定に戻った |

> **ポイント**: 0.16 より前の既定に戻すなら `select = ["E4", "E7", "E9", "F"]`（0.16 の告知）。全部の一覧は公式 docs の [Default Rules](https://docs.astral.sh/ruff/default-rules/) にある。

### 3.3 ルールのカテゴリ（preview）

接頭辞とは別に、**問題の種類で分けたカテゴリ**がある。公式 docs: "In preview, Ruff supports rule categories in addition to the Flake8-style linter groups"。

| カテゴリ | 中身 | 既定 |
|---|---|---|
| `correctness` | 書いたとおりに間違っているコード。抑止せずに直す | 有効 |
| `suspicious` | ほぼ間違いだが、わざと書く場合もある。非推奨の API もここ | 有効 |
| `complexity` / `performance` / `style` | もっと簡単に・速く・慣用的に書ける | 有効 |
| `security` | 脆弱性につながりうる。見逃しより誤検知を選ぶので多めに出る | 無効 |
| `formatting` / `pedantic` / `restriction` | formatter と重なる / 意見が強い / 機能の使用を制限する | 無効 |

カテゴリで選ぶには preview が要る。`--preview` 無しの `ruff check --select security` は `Selecting rules by category requires preview mode` で失敗し、`--preview` を付けると通った（検証で再現）。公式 docs は、セキュリティを重視するプロジェクトなら `security` を丸ごと有効にしてよいとしている。安定版だけで足すなら、近い接頭辞 `S`（flake8-bandit）を `extend-select` に書く。

### 3.4 設定

`pyproject.toml` に書く例（公式 docs 準拠・未実行: 通し課題は既定のままにするため）。

```toml
[tool.ruff.lint]
extend-select = ["I", "S"]  # 既定に import の並び順と flake8-bandit を足す

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]       # テストでは assert を許す

[tool.ruff.format]
docstring-code-format = true  # docstring の中のコード例も整形する
```

| 設定 | 既定 | 補足 |
|---|---|---|
| `target-version` | `requires-python` から推定。どこにも無ければ 3.11（0.17.0 から） | 推定させるなら書かない |
| `line-length` | 88 | Black と同じ。lint の `E501` と formatter の両方に効く |
| `lint.select` / `lint.extend-select` / `lint.ignore` | 既定のルール / なし / なし | `select` は置き換え、`extend-select` は追加 |
| `format.docstring-code-format` | `false` | `>>>` の例や Markdown・reST のコードブロックを整形する |
| `cache-dir` | `.ruff_cache` | 中に `*` だけの `.gitignore` を自分で置くので、git の対象に入らない（検証済み）。`--no-cache` で使わない |

**`target-version` は `requires-python` から決まる**。通し課題（`requires-python = ">=3.15"`）では 3.15 になった（検証済み）。

実行結果:

```text
$ uv run ruff check --show-settings categories.py | grep -E "linter.unresolved_target_version|linter.line_length"
linter.unresolved_target_version = 3.15
linter.line_length = 88
```

版によって結果が変わるルールもある。`datetime.UTC` は 3.11 からなので、`UP017` は既定の 3.11 では出て、3.10 を指定すると出ない（検証済み）。

実行結果:

```text
$ ruff check --select UP017 --output-format concise b.py
b.py:2:5: UP017 [*] Use `datetime.UTC` alias
Found 1 error.
[*] 1 fixable with `--fix`.
$ ruff check --select UP017 --output-format concise --target-version py310 b.py
All checks passed!
```

**設定ファイルの優先順位**: 同じディレクトリに複数あれば `.ruff.toml` > `ruff.toml` > `pyproject.toml`。`[tool.ruff]` の無い `pyproject.toml` は設定ファイルとして扱わない。`[tool.ruff]` に `line-length = 100`、隣の `ruff.toml` に `line-length = 120` を書くと、`ruff.toml` が勝った。`ruff.toml` に版を書かなくても、隣の `pyproject.toml` の `requires-python = ">=3.13"` は効いた（`--show-settings` で `line_length = 120`・`unresolved_target_version = 3.13`。検証済み）。

---

## 4. 推奨の使い方（2026-11）

| 推奨 | 理由 |
|---|---|
| 既定のルールから始め、必要なグループを `extend-select` で 1 つずつ足す | tutorial: "If you're introducing a linter for the first time, **the default rule set is a great place to start**"。`select` は既定を置き換え、`F401` すら消える（[Step 05](../steps/05-quality.md) §3.4 で確認） |
| `select = ["ALL"]` は避ける | 公式 docs: "Enabling `ALL` will implicitly enable new rules whenever you upgrade." |
| 抑止は `per-file-ignores` か、コード付きの行単位のコメント | コードなしの `# noqa` はその行の違反をすべて隠す。`correctness` のルールは抑止せずに直す（公式 docs） |
| `target-version` を書かず、`requires-python` に任せる | 版の宣言が 1 か所で済む（§3.4） |
| Ruff は dev 依存に入れ、pre-commit の `rev` と同じ版にそろえる | 版で既定のルールが変わる（0.16・0.17）。手順は [Step 05](../steps/05-quality.md) §3.7 |
| エディタは Ruff の language server（`ruff server`。各エディタの拡張機能が起動する）を使う | 0.17 で旧来の `ruff-lsp` のサポートは削除された。設定は [Step 05](../steps/05-quality.md) §3.8 |
| CI では `ruff check` と `ruff format --check` を両方回す | `format --check` も `--output-format github` で注釈を出せる（0.16 から）。CI の組み方は [Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ) で扱う |
| `uv format` は使うなら版を固定する | `uv format` は experimental で、プロジェクトの Ruff ではなく uv が選んだ版の Ruff（検証時 0.15.22）を取ってくる（[uv](uv.md) §4）。`uv format --version 0.17.4` で版を指定できる（`uv format --help` で確認） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 前の行に `# noqa: F401` を書いたのに、次の行の `F401` が出る。しかも `RUF100` が増える（検証で再現。下の実行結果） | `noqa` は**同じ行**にしか効かない。効かない `noqa` は `RUF100`（既定で有効）で報告される | 同じ行に書くか、前の行に `# ruff: ignore[F401]` と書く |
| `ruff format` が README などの Markdown を書き換えた（検証で再現） | 0.16 から、`.md` の `python`・`py`・`pyi`・`pycon` などのコードブロックを既定で整形する。通し課題でも `README.md` が整形の対象に入り、`python` のブロックの `labels={"IT":"情報システム部"}` は `labels = {"IT": "情報システム部"}` に直された（`bash` のブロックはそのまま） | 整形させたくなければ `extend-exclude = ["*.md"]`。一部だけなら `<!-- fmt: off -->` 〜 `<!-- fmt: on -->` で囲む |
| pre-commit の `ruff-format` は Markdown を整形しない | フックの既定の対象に Markdown が入っていない | 公式 docs のとおり `types_or: [python, pyi, jupyter, markdown]` を足す |
| Ruff を 0.16 以降に上げたら、急に違反が増えた | 0.16 で既定のルールが 59 から 413 に増えた | 直すか、`--add-ignore` で今ある違反に抑止を書いてから少しずつ消す。旧来に戻すなら `select = ["E4", "E7", "E9", "F"]` |
| `select = ["security"]` で `Invalid selector` | カテゴリでの選択は preview の機能 | `preview = true` を書くか、接頭辞（`S` など）で選ぶ |
| 子ディレクトリの `ruff.toml` を置いたら、親の設定が全部効かなくなった | Ruff は設定を合成せず、一番近い 1 つだけを使う | 子の設定に `extend = "../pyproject.toml"` |

前の行の `noqa` と `ruff: ignore` を比べた（検証済み）。

```python
# noqa: F401
import os
import sys  # noqa: F401
# ruff: ignore[F401]
import json
```

実行結果:

```text
$ ruff check --output-format concise sup.py
sup.py:1:1: RUF100 [*] Unused `noqa` directive (unused: `F401`)
sup.py:2:1: I001 [*] Import block is un-sorted or un-formatted
sup.py:2:8: F401 [*] `os` imported but unused
Found 3 errors.
[*] 3 fixable with `--fix`.
```

`sys`（同じ行の `noqa`）と `json`（前の行の `ruff: ignore`）は止まり、`os` だけが出た。`I001` も既定で有効なので、並び順も報告される。

---

## 出典

| 情報源 | URL |
|---|---|
| Ruff — The Ruff Linter | https://docs.astral.sh/ruff/linter/ （2026-11-08 確認、GitHub のタグ 0.17.4 の `docs/linter.md` から原文を確認。ルールの選び方、`ALL`、カテゴリ（preview）、`noqa` と `ruff: ignore`） |
| Ruff — Configuring Ruff | https://docs.astral.sh/ruff/configuration/ （2026-11-08 確認、Context7 `/astral-sh/ruff/0.17.3` とタグ 0.17.4 の `docs/configuration.md`。設定ファイルの探し方と優先順位、`extend`、`requires-python` からの推定、`--watch`） |
| Ruff — The Ruff Formatter | https://docs.astral.sh/ruff/formatter/ （2026-11-08 確認、タグ 0.17.4 の `docs/formatter.md`。Black の drop-in replacement、`docstring-code-format`、Markdown の整形と `types_or`） |
| Ruff — Tutorial | https://docs.astral.sh/ruff/tutorial/ （2026-11-08 確認、タグ 0.17.4 の `docs/tutorial.md`。既定のルールから始める方針） |
| Ruff — Default Rules | https://docs.astral.sh/ruff/default-rules/ （2026-11-08 確認。既定のルールの一覧の場所） |
| Ruff v0.16.0 | https://astral.sh/blog/ruff-v0.16.0 （2026-11-08 確認、2026-07-23 公開。413 のルール、外れた 18 個、旧来の既定、Markdown の整形） |
| BREAKING_CHANGES.md | https://github.com/astral-sh/ruff/blob/0.17.4/BREAKING_CHANGES.md （2026-11-08 確認。0.17.0 の 3.11 既定・`DTZ`・`F406`・`ruff-lsp` 削除、0.16.0 の `ruff: ignore`、0.15.0 の範囲の抑止） |
| astral-sh/ruff README | https://github.com/astral-sh/ruff （2026-11-08 確認、タグ 0.17.4。置き換えるツールの一覧） |
| Biome — Suppressions | https://biomejs.dev/analyzer/suppressions/ （2026-11-08 確認。`biome-ignore`・`biome-ignore-start` / `-end`。ESLint・Biome のコマンドは公式 docs の記載に拠り、手元では動かしていない） |

### 確認できなかった事項

- **Ruff 0.17.4 で既定のルールがちょうど何個か**。413 は 0.16.0 の数で、0.17.0 で 7 個外れ 1 個戻った。その後の版での増減は数えていない
- **カテゴリ（`correctness` など）が安定版になる時期**。0.17.4 では preview のままである
- **Biome・ESLint の対応表の列**。両者の公式 docs の記載に拠り、このページでは実行していない
- **`ruff check --watch` の実際の動き**。`--help` に載っていることだけを確かめた

- 関連: [Python 学習ガイド](../README.md) / [Step 05: 品質ツール](../steps/05-quality.md) / [型チェッカーの比較](type-checkers.md) / [uv](uv.md) / [pyproject.toml](pyproject-toml.md)
