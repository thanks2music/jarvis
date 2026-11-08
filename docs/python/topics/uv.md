# uv — Python の版・依存・実行・ツールを 1 つで扱う

> 出典（一次情報）:
> - [uv (docs.astral.sh)](https://docs.astral.sh/uv/) — 機能の全体像
> - [Locking and syncing (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/sync/) — `--locked` と `--frozen`、`uv sync` の exact な同期
> - [Project structure and files (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/layout/) — `uv.lock` をバージョン管理に入れること
> - [Workspaces (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/workspaces/) — モノレポの構成
> - [Tools (docs.astral.sh)](https://docs.astral.sh/uv/concepts/tools/) — `uvx` と `uv tool install`
> - [Astral to join OpenAI (astral.sh)](https://astral.sh/blog/openai) — 開発元の状況
>
> 最終更新: 2026-11-08（uv 0.13.7 で検証）

uv は、Astral が Rust で書いた Python のパッケージマネージャである。Node.js で言えば **npm（または pnpm）・nvm・npx を 1 つのコマンドにまとめたもの**で、1 つのバイナリがランタイムの管理まで受け持つ点は Bun に近い。
pip・pip-tools・pipx・pyenv・virtualenv・Poetry が分担していた仕事を 1 つで行う。通し課題での使い方は [Step 01](../steps/01-setup.md) と [Step 03](../steps/03-project.md) を参照。

---

## 1. TL;DR

- **プロジェクトは `uv init` → `uv add` → `uv run` の 3 つで回る**。`uv run` は実行の前に lockfile と `.venv` を自動で最新にする（`npm install` を打ち忘れる問題が起きない）。
- **`uv.lock` はコミットする**。CI では `uv sync --locked`（lockfile が `pyproject.toml` とずれていたら失敗する。`npm ci` にあたる）。
- **`package.json` の `scripts`（`npm run dev`）にあたる仕組みは無い**。`[project.scripts]` は `bin` にあたる別物である（§6）。
- `uvx` は `npx` / `bunx`、`uv tool install` は `npm install -g` にあたる。
- `uv audit`・`uv check`・`uv format` は **experimental**（実行すると警告が出る）。CI の必須の検査には、まだ使わない（§4）。
- 開発元の Astral は、2026-03-19 に OpenAI の Codex チームに加わる合意を発表した（§5）。

---

## 2. Node.js / Bun との対応

| やりたいこと | npm | pnpm | Bun | uv |
|---|---|---|---|---|
| プロジェクトを作る | `npm init` | `pnpm init` | `bun init` | `uv init`（ライブラリなら `--lib`） |
| 依存を足す | `npm install x` | `pnpm add x` | `bun add x` | `uv add x` |
| 開発用の依存を足す | `npm install -D x` | `pnpm add -D x` | `bun add -d x` | `uv add --dev x` |
| 依存を外す | `npm uninstall x` | `pnpm remove x` | `bun remove x` | `uv remove x` |
| lockfile どおりに入れる（CI） | `npm ci` | `pnpm install --frozen-lockfile` | `bun install --frozen-lockfile` | `uv sync --locked` |
| lockfile を作り直す | `npm install` | `pnpm install` | `bun install` | `uv lock` |
| 依存を新しい版に上げる | `npm update` | `pnpm update` | `bun update` | `uv lock --upgrade`（1 つだけなら `--upgrade-package x`） |
| プロジェクトの環境でコマンドを動かす | `npx x`（ローカル） | `pnpm exec x` | `bun run x` | `uv run x` |
| 依存のツリーを見る | `npm ls` | `pnpm list` | `bun pm ls` | `uv tree` |
| 古い依存を探す | `npm outdated` | `pnpm outdated` | `bun outdated` | `uv tree --outdated` |
| 脆弱性を調べる | `npm audit` | `pnpm audit` | `bun audit` | `uv audit`（experimental） |
| ツールを一度だけ動かす | `npx x` | `pnpm dlx x` | `bunx x` | `uvx x` |
| ツールをグローバルに入れる | `npm install -g x` | `pnpm add -g x` | `bun add -g x` | `uv tool install x` |
| ランタイムの版を入れる・固定する | nvm / fnm / Volta | `pnpm runtime` | — | `uv python install` / `uv python pin` |
| モノレポ | `workspaces` | `pnpm-workspace.yaml` | `workspaces` | `[tool.uv.workspace]` |
| 配布物を作る・公開する | `npm pack` / `npm publish` | `pnpm publish` | `bun publish` | `uv build` / `uv publish` |

> **ポイント**: 依存の置き場所は、`node_modules/` ではなくプロジェクト直下の **`.venv/`（仮想環境）** である。中には Python 本体へのリンクと、`lib/python3.15/site-packages/` に入った依存がある。`.venv/` は `node_modules/` と同じくコミットしない。

---

## 3. 早見表

### 3.1 プロジェクト

| コマンド | 何をするか |
|---|---|
| `uv init` | アプリを `src/<名前>/` のパッケージとして作り、`[build-system]`（`uv_build`）と、`faq` のようなコマンドを登録する（[Step 03](../steps/03-project.md)）。uv 0.12.0 からの既定 |
| `uv init --no-package` | ビルドの設定を持たない平らな構成（`main.py` と `pyproject.toml`）。0.11 までの既定 |
| `uv init --lib` | ライブラリ用。`py.typed` まで作る（検証済み。[Step 04](../steps/04-typing.md)） |
| `uv add x` / `uv add --dev x` / `uv add --group docs x` | 依存を `pyproject.toml` に書き、lockfile と `.venv` を更新する |
| `uv remove x` | 依存を外す |
| `uv run <コマンド>` | lockfile と `.venv` を最新にしてから実行する |
| `uv sync` | `.venv` を lockfile どおりにする。**入っていない依存は消す**（exact） |
| `uv lock` / `uv lock --check` | lockfile を作り直す / 最新かだけ調べる（`--locked` と同じ判定） |
| `uv tree` / `uv tree --outdated` | 依存のツリー / 新しい版があるもの |
| `uv export --format requirements.txt` | lockfile を別の形式に書き出す（他に `pylock.toml`・`cyclonedx1.5`） |
| `uv version` / `uv version --bump minor` | プロジェクトの版を読む・上げる |

### 3.2 Python・ツール・その他

| コマンド | 何をするか |
|---|---|
| `uv python install 3.15` / `uv python pin 3.15` / `uv python list` / `uv python find` | Python を入れる / 固定する / 一覧する / どれが選ばれるか見る（[Step 01](../steps/01-setup.md)） |
| `uvx x` / `uvx x@1.2.3` / `uvx --from pkg cmd` | ツールを使い捨ての環境で動かす |
| `uv tool install x` / `uv tool upgrade --all` / `uv tool list` | ツールを `~/.local/bin` に入れる・上げる・一覧する |
| `uv run --with x <コマンド>` | その 1 回だけ、依存を足して動かす（プロジェクトには書かない） |
| `uv pip install` / `uv pip list` / `uv venv` | pip 互換の低水準の操作（[pip と venv](pip-venv.md)） |
| `uv build` / `uv publish` | wheel と sdist を作る / PyPI などへ上げる（[Step 11](../README.md#4-学習ロードマップ)） |
| `uv cache dir` / `uv cache clean` | キャッシュの場所（macOS では `~/.cache/uv`）/ 消す |
| `uv self update` | uv 本体を更新する（公式のインストーラで入れた場合） |

lockfile が最新かを調べ、要らない依存を除いて requirements.txt に書き出す（検証済み）。

実行結果:

```text
$ uv lock --check
Resolved 23 packages in 6ms
$ uv export --format requirements.txt --no-hashes --no-dev
Resolved 23 packages in 7ms
# This file was autogenerated by uv via the following command:
#    uv export --format requirements.txt --no-hashes --no-dev
-e .
annotated-types==0.8.0
    # via pydantic
pydantic==2.14.3
    # via faq
…（中略: 9 行）…
```

その 1 回だけ依存を足して動かす（検証済み）。

実行結果:

```text
$ uv run --with rich python -c "import rich; print(rich.__name__, 'is available only for this run')"
Installed 4 packages in 12ms
rich is available only for this run
```

---

## 4. 推奨の使い方（2026-11）

| 推奨 | 理由 |
|---|---|
| `uv.lock` をコミットする | 公式 docs: "This file should be checked into version control, allowing for consistent and reproducible installations across machines." |
| CI では `uv sync --locked` | `--locked` は lockfile が古ければ**失敗する**（`npm ci` と同じ）。`--frozen` は確かめずに使うので、Docker で依存だけを先に入れる層に限る（公式 docs: "we use `--frozen` instead of `--locked` to skip the check during the initial sync"。[Step 11](../README.md#4-学習ロードマップ) で扱う） |
| 依存は `uv add` で足し、`uv pip install` をプロジェクトに混ぜない | `uv pip install` は `pyproject.toml` と lockfile を書き換えない。次の `uv sync` で消される（exact な同期のため。下の実行結果） |
| プロジェクトの依存を読む道具（pytest・型チェッカー）は `uv add --dev` して `uv run` で動かす | `uvx` はプロジェクトから切り離した環境で動くため、プロジェクトの依存を import できない |
| experimental の機能は手元で試すにとどめる | `uv audit`・`uv check`・`uv format` は実行すると "is experimental and may change without warning" と警告する（検証済み）。`uv format` はプロジェクトに入れた Ruff ではなく、uv が決めた版の Ruff（検証時は 0.15.22）を取ってきて使う |
| 互いに依存する複数のパッケージは workspace にまとめる | lockfile が 1 つになり、メンバー同士は editable につながる。メンバーごとに依存がぶつかる・環境を分けたい場合は、workspace ではなく path 依存にする（公式 docs の "When (not) to use workspaces"） |

`uv pip install` で入れたものが記録されず、`uv sync` で消えることを確かめる（検証済み）。

実行結果:

```text
$ sh -c "uv pip install -q rich && git status --short pyproject.toml uv.lock && echo \"(pyproject.toml / uv.lock unchanged)\" && uv pip list | grep -i \"^rich\""
(pyproject.toml / uv.lock unchanged)
rich                    15.0.0
$ uv sync
Resolved 23 packages in 6ms
…（中略: 7 行）…
 - markdown-it-py==4.2.0
 - mdurl==0.1.2
 - rich==15.0.0
```

experimental の機能を実際に動かした結果（検証済み）。

実行結果:

```text
$ uv audit
warning: `uv audit` is experimental and may change without warning. Pass `--preview-features audit-command` to disable this warning.
Resolved 23 packages in 7ms
Found no known vulnerabilities and no adverse project statuses in 22 packages
$ uv format --check
warning: `uv format` is experimental and may change without warning. Pass `--preview-features format-command` to disable this warning.
Downloading ruff v0.15.22 (9.5MiB)
 Downloaded ruff v0.15.22
10 files already formatted
```

`uv check` は、Astral の型チェッカー ty（1.0 前）をプロジェクトの環境で動かす。[Step 04](../steps/04-typing.md) の `type_mistakes.py` に対して、4 件の誤りをすべて報告した（検証済み）。

---

## 5. 開発元の状況

| 項目 | 内容 |
|---|---|
| 開発元 | Astral（Ruff と型チェッカー ty も開発する） |
| 2026-03-19 の発表 | Astral が OpenAI の Codex チームに加わる合意を発表した。Astral の告知: "we've entered into an agreement to join OpenAI as part of the Codex team" / "OpenAI will continue supporting our open source tools after the deal closes." OpenAI は、完了は規制当局の承認などの条件しだいとしている |
| 完了の発表 | 2026-11-08 時点で、Astral のブログに完了の告知は無い |
| ライセンス | uv は Apache-2.0 と MIT のデュアルライセンス。オープンソースなので、開発が止まってもフォークして使い続けられる |

> **ポイント**: 2026-11 時点で uv の開発は続いている（0.13.7 は 2026-11-03 公開）。本ガイドは、開発元の状況を事実として記すにとどめ、uv を既定の道具として扱う。

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `npm run dev` のように、よく使うコマンドに名前を付けたい | uv にはタスクを登録する仕組みが無い。`uv help` のコマンド一覧にも無い（検証済み） | `uv run <コマンド>` をそのまま書くか、Makefile・just・poe the poet などを使う。`[project.scripts]` は `bin` にあたり、パッケージを入れたときに作られるコマンドを定義するものである |
| `uv add pydantic` で `pydantic>=2.14.3` と書かれ、`^` のような上限が付かない | uv は既定で下限だけを書く。Python の版指定は semver ではなく PEP 440 である | 上限が要るなら `uv add "pydantic>=2.14,<3"` と書く。詳細は [pyproject.toml](pyproject-toml.md) |
| `uv pip install` で入れたパッケージが、いつの間にか消えている | `uv sync`（と、それを呼ぶ操作）は exact に同期し、lockfile に無いものを消す | `uv add` で依存に加える。一時的に使うだけなら `uv run --with x` |
| `uvx pytest` でテストを動かすと、自分のパッケージを import できない | `uvx` はプロジェクトと切り離した環境で動く | `uv add --dev pytest` してから `uv run pytest` |
| `uv run` がいきなり依存のダウンロードを始める | `uv run` は実行の前に lockfile と `.venv` を自動で最新にする | 意図した動きである。止めたい場合は `uv run --frozen`（lockfile を確かめない）か `--no-sync` |
| どの Python が使われているか分からない | `.python-version`・`requires-python`・ユーザー設定 `~/.config/uv/uv.toml` が影響する | `uv python find -v` で理由を見る（[Step 01](../steps/01-setup.md) の §5） |

---

## 出典

| 情報源 | URL |
|---|---|
| uv — docs | https://docs.astral.sh/uv/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由） |
| Locking and syncing | https://docs.astral.sh/uv/concepts/projects/sync/ （2026-11-08 確認） |
| Project structure and files | https://docs.astral.sh/uv/concepts/projects/layout/ （2026-11-08 確認） |
| Workspaces | https://docs.astral.sh/uv/concepts/projects/workspaces/ （2026-11-08 確認） |
| Tools | https://docs.astral.sh/uv/concepts/tools/ （2026-11-08 確認） |
| Astral to join OpenAI | https://astral.sh/blog/openai （2026-11-08 確認。2026-03-19 公開） |
| OpenAI to acquire Astral | https://openai.com/index/openai-to-acquire-astral/ （2026-11-08 確認） |
| Vulnerability and malware checks in uv | https://astral.sh/blog/uv-audit （2026-11-08 確認。2026-06-08 公開） |
| Bringing uv and ty together | https://astral.sh/blog/uv-ty-integration （2026-11-08 確認。2026-10-13 公開） |
| astral-sh/uv | https://github.com/astral-sh/uv （2026-11-08 確認。ライセンス） |
| Bun / pnpm のコマンド名 | 手元の `bun --help`（1.4.4）と `pnpm help`（12.11.2）で確認（2026-11-08） |

### 確認できなかった事項

- **買収の完了**。Astral と OpenAI の公式サイトで、完了を告げる告知は見つからなかった。合意の発表までを事実として載せた
- **`uv format` が既定で選ぶ Ruff の版の決まり方**。検証では 0.15.22 が取られた。`uv format --help` には、版を指定する `--version <VERSION>`（"The version of Ruff to use for formatting"）があることまでを確かめた

- 関連: [Python 学習ガイド](../README.md) / [Step 01: 環境構築](../steps/01-setup.md) / [Step 03: プロジェクト構成](../steps/03-project.md) / [pyproject.toml](pyproject-toml.md) / [pip と venv](pip-venv.md)
