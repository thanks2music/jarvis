# パッケージマネージャ — uv・Poetry・PDM・Hatch・conda の見分け方と移行

> 出典（一次情報）:
> - [uv (docs.astral.sh)](https://docs.astral.sh/uv/) / [Migration guides (docs.astral.sh)](https://docs.astral.sh/uv/guides/migration/) — uv の機能と、移行ガイドの範囲
> - [The pyproject.toml file (python-poetry.org)](https://python-poetry.org/docs/pyproject/) / [History (python-poetry.org)](https://python-poetry.org/history/) / [Announcing Poetry 2.0.0 (python-poetry.org)](https://python-poetry.org/blog/announcing-poetry-2.0.0/) — `[project]` と PEP 735 への対応
> - [PDM — Scripts / Lock file (pdm-project.org)](https://pdm-project.org/latest/usage/scripts/) / [Hatch — Environment configuration (hatch.pypa.io)](https://hatch.pypa.io/latest/config/environment/overview/) — タスクと lockfile
> - [pip-tools](https://pip-tools.pypa.io/en/latest/) / [Pipenv](https://pipenv.pypa.io/en/latest/) / [conda — Managing environments (docs.conda.io)](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) / [pixi (pixi.sh)](https://pixi.sh/latest/) / [astral-sh/rye (GitHub)](https://github.com/astral-sh/rye)
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・Poetry 2.5.1・PDM 2.29.7・Hatch 1.18.2・pipenv 2026.10.6 で検証。conda と pixi は公式 docs 準拠）

Node.js で言えば npm・pnpm・yarn・Bun のどれを使っているかにあたる話だが、Python では道具ごとに **lockfile の名前だけでなく、受け持つ範囲（Python 本体・仮想環境・ビルド・タスク）まで違う**。
本ガイドは uv を使う（[uv](uv.md)・[Step 03](../steps/03-project.md)）。このページは、他の道具で作られたリポジトリを読み、必要なら uv へ移すためのものである。pip と venv だけのプロジェクトは [pip と venv](pip-venv.md) で扱った。

---

## 1. TL;DR

- **リポジトリの道具は lockfile と `[tool.*]` の表で見分ける**。`uv.lock`・`poetry.lock`・`pdm.lock`・`Pipfile.lock`・`pixi.lock`。`[build-system]` の行はビルドの道具を示すだけで、手元の道具の手がかりにならない（§3.2）。
- **Poetry 2.0（2025-01）から依存を標準の `[project]` に書く**。Poetry 2.2.0 からは `[dependency-groups]`（PEP 735）も読む。2.5.1 の `poetry add --group dev` は `[dependency-groups]` に書いた（§3.3）。
- **`npm run` にあたるタスク機能を持つのは PDM・Hatch・pipenv・pixi**。uv と Poetry には無い（§3.1）。
- **uv の公式 docs に Poetry からの移行ガイドは無い**（2026-11-08 時点で "not yet available"）。Poetry 2 の形の `pyproject.toml` なら、`uv lock` するだけで動いた。Poetry 1 の形は `uv lock` が**黙って依存 0 個で成功する**ので、先に `[project]` へ書き換える（§4.2）。
- Python 以外のバイナリ（CUDA・GDAL・C/C++ のライブラリなど）まで 1 つの環境で揃えたいなら conda か pixi を選ぶ（§5）。Rye はアーカイブ済み。

---

## 2. Node.js / Bun との対応

| Node.js の道具 | 近い Python の道具 | 違うところ |
|---|---|---|
| npm（`package.json` + `package-lock.json`） | pip + pip-tools（`requirements.in` + `requirements.txt`） | pip だけでは lockfile が無い。pip-tools の `pip-compile` が固定した一覧を作る（[pip と venv](pip-venv.md)） |
| pnpm / Bun（速い 1 本の CLI） | uv | uv は Python 本体の版管理（nvm の役）まで持つ。タスクは持たない |
| yarn（独自 lockfile・workspace） | Poetry / PDM | どちらも独自の lockfile を持つ。PDM は `[tool.pdm.scripts]` でタスクも持つ |
| `npm run` の `scripts` | PDM scripts・Hatch の env scripts・Pipfile の `[scripts]`・pixi tasks | uv と Poetry には無い。`[project.scripts]` は `bin` にあたる別物（[uv](uv.md) §6） |
| nvm + npm + `apt`/Homebrew の C ライブラリ | conda / mamba / pixi | Python 以外のパッケージ（コンパイラ・CUDA・R など）も同じ環境に入れる。PyPI ではなく conda-forge などのチャネルから取る |

> **ポイント**: Node の道具はどれも `node_modules/` と `package.json` を共有するので、npm から pnpm へ移っても `package.json` はほぼそのままである。Python では、`[project]`（PEP 621）と `[dependency-groups]`（PEP 735）が**その共通部分**にあたる。ここに書かれた依存は uv・Poetry 2・PDM・Hatch のどれでも読める。

---

## 3. 早見表

### 3.1 何を受け持つか

| 道具 | Python の版 | 仮想環境 | lockfile | ビルド・公開 | タスク | 依存を `[project]` に書く |
|---|---|---|---|---|---|---|
| uv 0.13.7 | `uv python` | `.venv` | `uv.lock`（`uv export` で `pylock.toml` も） | `uv build` / `uv publish` | 無い | ○ |
| Poetry 2.5.1 | `poetry python`（experimental、2.1.0 から） | `poetry run`（既定の置き場所はキャッシュの下） | `poetry.lock` | `poetry build` / `poetry publish` | 無い（`scripts` は console script） | ○（2.0 から。旧来の `[tool.poetry.dependencies]` も読む） |
| PDM 2.29.7 | `pdm python` | `.venv` | `pdm.lock`（`pylock.toml` も選べる） | `pdm build` / `pdm publish` | `[tool.pdm.scripts]` | ○ |
| Hatch 1.18.2 | `hatch python` | Hatch のデータディレクトリの下 | `pylock.toml`（1.17.0 から。`locked = true` で有効） | `hatch build` / `hatch publish` | `[tool.hatch.envs.<名前>.scripts]` | ○（依存を足すコマンドは無く、手で書く） |
| pip + pip-tools 7.6.2 | 無い | 無い（`python -m venv`） | `requirements.txt`（`pip-compile` が作る） | 無い | 無い | `pip-compile pyproject.toml` で読める |
| pipenv 2026.10.6 | pyenv か asdf があれば入れる | `.venv` か専用の場所 | `Pipfile.lock` | 無い | Pipfile の `[scripts]` | ×（`Pipfile`） |
| conda / mamba | `python` も conda のパッケージ | conda 環境 | 標準では無い（`environment.yml` は宣言。固定は `conda list --explicit`） | 本体には無い | 無い | ×（`environment.yml`） |
| pixi | conda のパッケージとして | `.pixi/` | `pixi.lock` | （確かめていない） | tasks | ○（`pixi.toml` か `pyproject.toml` の `[tool.pixi]`） |
| Rye | — | — | — | — | — | アーカイブ済み。README: "Rye is no longer developed. We encourage all users to use uv" |

出典: 各ツールの CLI の `--help`（uvx で起動して確認）と公式 docs。conda と pixi は公式 docs 準拠・未実行（手元に入れていないため）。mamba は conda の C++ による再実装（mamba の README: "`mamba` is a reimplementation of the conda package manager in C++."）。

### 3.2 リポジトリが何を使っているかの見分け方

| 見つけたファイル・設定 | 使っている道具 | 補足 |
|---|---|---|
| `uv.lock` / `[tool.uv]` | uv | `.python-version` は uv も pyenv も使う |
| `poetry.lock` / `[tool.poetry]` | Poetry | 2.5.1 の `poetry new` も `[tool.poetry]` に `packages` を書いた |
| `pdm.lock` / `.pdm-python` / `[tool.pdm]` | PDM | `.pdm-python` は選んだ Python のパス（マシンごと。検証では `.venv/bin/python` の絶対パス） |
| `[tool.hatch.envs.*]` / `hatch.toml` | Hatch | `hatch new` は `[tool.hatch.version]` と `types` 環境まで書いた |
| `Pipfile` / `Pipfile.lock` | pipenv | |
| `requirements.in` と、先頭が `# This file is autogenerated by pip-compile` の `requirements.txt` | pip-tools | `uv pip compile` の出力は `# This file was autogenerated by uv` で始まる |
| `requirements.txt` だけ | pip | [pip と venv](pip-venv.md) |
| `environment.yml` | conda / mamba | |
| `pixi.toml` / `pixi.lock` / `[tool.pixi]` | pixi | |
| `pylock.toml` | 決められない | PEP 751 の共通形式。検証では Hatch が書き（`created-by = "pip"`）、uv・PDM も書き出せる |

> **注意**: `build-backend = "poetry.core.masonry.api"`・`"hatchling.build"`・`"pdm.backend"` は**ビルドの道具**（PEP 517）を示すだけである。uv で管理するプロジェクトが hatchling でビルドしてもよく、§4.2 では Poetry の poetry-core のまま uv で動かした。

### 3.3 Poetry・PDM・Hatch を動かす

それぞれ小さなプロジェクトを作り、rich を 1 つ足して動かす。どの道具も `uvx <ツール>@<版>` で起動したので、グローバルには何も入れていない。キャッシュと設定の置き場所は `POETRY_CACHE_DIR`・`PDM_HOME`・`HATCH_DATA_DIR` などで作業用のディレクトリに向けた（検証済み）。

Poetry 2.5.1（検証済み）。`^15.0.0` と表示しつつ、`pyproject.toml` には PEP 508 の範囲で書いた。uv の `uv add` と違い、上限が付く。

実行結果:

```text
$ uvx poetry@2.5.1 new demo-poetry
Created package demo_poetry in demo-poetry
$ uvx poetry@2.5.1 add rich
…（中略: 1 行）…
Using version ^15.0.0 for rich
…（中略: 11 行）…
Writing lock file
$ grep -A2 "^dependencies" pyproject.toml
dependencies = [
    "rich (>=15.0.0,<16.0.0)"
]
$ uvx poetry@2.5.1 run python -c "import rich, sys; print('rich', rich.__name__, sys.prefix.split('/')[-1])"
rich rich .venv
```

- `.venv` がプロジェクトの中にできたのは `POETRY_VIRTUALENVS_IN_PROJECT=true` を設定したためである。既定では `{cache-dir}/virtualenvs` に作る（Poetry docs の `virtualenvs.path`）。lockfile は `poetry.lock`（`lock-version = "2.1"`）
- 続けて `poetry add --group dev pytest` を動かすと、`[tool.poetry.group.dev.dependencies]` ではなく標準の `[dependency-groups]` に `dev = ["pytest (>=9.2.0,<10.0.0)"]` を書いた（検証済み）

PDM 2.29.7（検証済み）。`pdm init` は `.venv`・`pdm.lock`・`.pdm-python` を作り、**`git init` もした**（`--no-git` で止まる）。`requires-python` は `"==3.15.*"`、依存は `"rich>=15.0.0"`（下限だけ）と書いた。`[tool.pdm]` の `distribution = false` は、ビルドしないアプリの印である。`[tool.pdm.scripts]` に `hello = "python -c \"print('hello from pdm scripts')\""` を足して、タスクとして呼んだ。

実行結果:

```text
$ uvx pdm@2.29.7 init -n --python 3.15 --name demo-pdm
Creating a pyproject.toml for PDM...
…（中略: 3 行）…
Project is initialized successfully
$ uvx pdm@2.29.7 add rich
Adding packages to default dependencies: rich
…（中略: 1 行）…
Changes are written to pyproject.toml.
…（中略: 9 行）…
$ uvx pdm@2.29.7 run hello
hello from pdm scripts
```

Hatch 1.18.2（検証済み）。依存を足すコマンドが無いので、`dependencies = ["rich>=15"]` を手で書いた。lockfile は既定では作らず、`[tool.hatch.envs.default]` に `locked = true` を足すと作った。

実行結果:

```text
$ uvx hatch@1.18.2 run python -c "import rich, sys; print('rich', rich.__name__, sys.prefix.split('/')[-2:])"
Creating environment: default
Installing project in development mode
Checking dependencies
rich rich ['gPtGC2mu', 'demo-hatch']
$ uvx hatch@1.18.2 lock
Environment `default` is not configured with `locked = true`. Use `--export <path>` to generate a lockfile, or set `locked = true` on the environment (or `lock-envs = true` globally).
$ grep -E "^lock-version|^created-by|^name =|^version =" pylock.toml
lock-version = "1.0"
created-by = "pip"
…（中略: 12 行）…
$ uvx hatch@1.18.2 run hello
hello from hatch scripts
```

- 環境はプロジェクトの外（`HATCH_DATA_DIR` の `env/virtual/demo-hatch/<ハッシュ>/`）にでき、`hatch env find` で場所が分かる
- lockfile は pip の `pip lock` で作られ、"pip lock is currently an experimental command" と警告が出た。installer を uv にすると uv が作る（公式 docs: "defaults follow the environment installer"）
- `hatch new` の雛形は `requires-python = ">=3.8"` で、classifiers は 3.12 までだった。3.15 で使うなら直す。

---

## 4. 推奨の使い方（2026-11）

### 4.1 既存のリポジトリでは、その道具に合わせる

| 推奨 | 理由 |
|---|---|
| 既存のリポジトリは、lockfile のある道具で操作する | lockfile は道具ごとに形式が違い、互いに読まない。uv は `poetry.lock` を読まない（§4.2 で新しく解決し直した） |
| 依存は `[project]` と `[dependency-groups]` に書く | 標準の表なので、uv・Poetry 2.2 以降・PDM・Hatch のどれでも読める。道具を替えるときに書き換えが要らない |
| 新しく始めるなら uv を使う（本ガイドの前提） | 1 つで Python の版・`.venv`・lockfile・ビルド・公開・ツールの実行を受け持つ（[uv](uv.md)）。タスクだけは別の道具が要る |
| CI では lockfile とずれていたら止める | uv は `uv sync --locked`、Poetry は `poetry check --lock` の後に `poetry sync`、PDM は `pdm install --check`、Hatch は `hatch lock --check`、pipenv は `pipenv install --deploy`（各 `--help` で確認） |

### 4.2 Poetry から uv へ移す

uv の移行ガイドは pip からのものだけで、索引に "Other guides, such as migrating from another project management tool, or from pip to `uv pip` are not yet available." とある（追跡は [astral-sh/uv#5200](https://github.com/astral-sh/uv/issues/5200)、2026-11-08 時点で open）。手で移す手順は次のとおり。

1. `poetry check` を動かし、`[tool.poetry]` に残っている項目の警告を見る
2. Poetry 1 の形なら、`[tool.poetry.dependencies]` を `[project].dependencies` に、`[tool.poetry.group.dev.dependencies]` を `[dependency-groups]` に書き換える。`^15.0` は `>=15.0,<16` と書く（semver の記法は PEP 440 に無い）。`python = "^3.15"` は `requires-python = ">=3.15"` にする
3. `poetry.lock` を片付けて `uv lock`。版は新しく解決されるので、`poetry show` と `uv tree` で見比べる
4. `[build-system]` の poetry-core は残してよい（`uv run` は poetry-core でビルドした）。`[tool.poetry]` の `packages` は poetry-core の設定なので、`uv_build` に替えるなら `src/` の構成に合わせて消す
5. CI の `poetry sync` を `uv sync --locked` に替える

§3.3 の Poetry のプロジェクト（2.5.1 が作った形。`[dependency-groups]` に pytest がある）を `.venv` と `poetry.lock` を除いてコピーし、uv で動かした（検証済み）。省いた 2 行は `Building demo-poetry @ file://…` と `Built …` で、poetry-core がそのまま使われた。

実行結果:

```text
$ uv lock
Using CPython 3.15.2
Resolved 10 packages in 100ms
$ uv run python -c "import rich, sys; print('rich', rich.__name__, sys.prefix.split('/')[-1])"
Using CPython 3.15.2
Creating virtual environment at: .venv
…（中略: 2 行）…
Installed 9 packages in 13ms
rich rich .venv
$ uv tree
Resolved 10 packages in 6ms
demo-poetry v0.1.0
├── rich v15.0.0
…（中略: 3 行）…
└── pytest v9.2.0 (group: dev)
…（中略: 4 行）…
```

Poetry 1 の形（`[project]` が無く、依存が `[tool.poetry.dependencies]` だけ）で `uv lock` すると、エラーにならず空の lockfile ができる（検証で再現）。

実行結果:

```text
$ uv lock
Using CPython 3.15.2
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.15`.
Resolved in 6ms
$ cat uv.lock
version = 1
revision = 5
requires-python = ">=3.15"
```

手順 1 の `poetry check` は、このファイルに "Warning: [tool.poetry.name] is deprecated. Use [project.name] instead." などを出した（検証済み）。

---

## 5. 選び方・代替との比較

| 状況 | 合う道具 | 根拠 |
|---|---|---|
| Python のパッケージが PyPI の wheel で揃う（Web API・CLI・データ処理の多く） | uv | 本ガイドの通し課題はこの形 |
| Python 以外のバイナリ（コンパイラ・CUDA・GDAL・R など）も同じ環境で揃えたい | conda / mamba / pixi | conda docs: "Conda provides package, dependency, and environment management for any language." pixi の docs も C/C++・Java・Rust のパッケージを conda-forge から入れる例を挙げる（公式 docs 準拠・未実行: 手元に conda / pixi を入れていないため） |
| conda の環境に lockfile とタスクも欲しい | pixi | lockfile は `pixi.lock`。PyPI の依存は uv で扱う（pixi docs: "Support for `pyproject.toml` and PyPI through uv."）。`environment.yml` を取り込める（公式 docs 準拠・未実行: 同上） |
| `npm run` のようなタスクを道具の中に持ちたい | PDM（PDM docs: "Like npm run, with PDM, you can run arbitrary scripts"）/ Hatch | uv を使い続けるなら、Makefile・just・poe the poet などを足す |

> **注意**: conda の環境に pip を混ぜるときは、conda docs が "Only after conda has been used to install as many packages as possible should pip be used to install any remaining software." と順番を決めている。pip で入れたものを conda は把握しないため、変えるときは環境を作り直す。

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| Poetry 1 のプロジェクトで `uv lock` は成功したのに、`import` が `ModuleNotFoundError`（検証で再現） | uv は `[tool.poetry.dependencies]` を読まない。依存 0 個の `uv.lock` ができる | §4.2 の手順 2 で `[project]` に書き換えてから `uv lock` |
| `hatch lock` が `is not configured with locked = true` で失敗する（検証中に発生） | Hatch の lockfile は環境ごとの opt-in | `[tool.hatch.envs.<名前>]` に `locked = true`（全体なら `lock-envs = true`） |
| `.pdm-python` をコミットしたら、別のマシンで Python が見つからない | 中身はそのマシンでの Python の絶対パス | コミットしない。PDM docs: "Do not commit the `.pdm-python` file." |
| Rye の README どおりに `rye sync` しようとしている | Rye はアーカイブ済み。README: "no further updates are planned, including security updates." | uv に移す。`[project]` と `[dependency-groups]` はそのまま読める |

---

## 出典

| 情報源 | URL（確認日） |
|---|---|
| uv — docs / Migration guides | https://docs.astral.sh/uv/ ・ https://docs.astral.sh/uv/guides/migration/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由。原文はページの実物で確認） |
| astral-sh/uv#5200 "Write migration guides" | https://github.com/astral-sh/uv/issues/5200 （2026-11-08 確認。open） |
| Poetry — pyproject / Managing dependencies / Configuration / CLI / History / 2.0.0 の告知 | https://python-poetry.org/docs/pyproject/ ・ https://python-poetry.org/docs/configuration/ ・ https://python-poetry.org/docs/managing-dependencies/ ・ https://python-poetry.org/docs/cli/ ・ https://python-poetry.org/history/ ・ https://python-poetry.org/blog/announcing-poetry-2.0.0/ （2026-11-08 確認。2.0.0 は 2025-01-05、2.2.0 で "Add support for PEP 735 dependency groups"、`poetry python` は "Introduced in 2.1.0" で experimental） |
| PDM — Scripts / Lock file / Project / CLI | https://pdm-project.org/latest/usage/scripts/ ・ https://pdm-project.org/latest/usage/project/ ・ https://pdm-project.org/latest/usage/lockfile/ ・ https://pdm-project.org/latest/reference/cli/ （2026-11-08 確認） |
| Hatch — Environment configuration（Locking）/ History / Python management | https://hatch.pypa.io/latest/config/environment/overview/ ・ https://hatch.pypa.io/latest/history/hatch/ ・ https://hatch.pypa.io/latest/tutorials/python/manage/ （2026-11-08 確認。lockfile は 1.17.0（2026-05-31）で追加） |
| pip-tools | https://pip-tools.pypa.io/en/latest/ ・ https://github.com/pypa/pip-tools （2026-11-08 確認） |
| Pipenv — README / Scripts | https://pipenv.pypa.io/en/latest/ ・ https://pipenv.pypa.io/en/latest/scripts.html （2026-11-08 確認） |
| conda — Managing environments / mamba | https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html ・ https://docs.conda.io/projects/conda/en/latest/ ・ https://mamba.readthedocs.io/en/latest/ （2026-11-08 確認） |
| pixi — Home / Lock file / Python tutorial | https://pixi.sh/latest/ ・ https://pixi.sh/latest/workspace/lock_file/ ・ https://pixi.sh/latest/python/tutorial/ （2026-11-08 確認。GitHub の docs ソースで原文を確認） |
| astral-sh/rye | https://github.com/astral-sh/rye （2026-11-08 確認。archived） |

### 確認できなかった事項

- **conda と pixi の実際の動き**。手元に入れていないため、公式 docs の記述だけで書いた。pixi のビルド・公開の機能も確かめていない
- **Poetry の版を保ったまま uv へ移す方法**。`poetry export` は Poetry 2.0 から本体に含まれない（poetry-plugin-export が要る）ため、requirements.txt を経由する手順は試していない

- 関連: [Python 学習ガイド](../README.md) / [uv](uv.md) / [pip と venv](pip-venv.md) / [pyproject.toml](pyproject-toml.md) / [Python の版の選び方](python-versions.md) / [Step 03: プロジェクト構成](../steps/03-project.md)
