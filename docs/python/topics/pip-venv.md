# pip と venv — uv を使っていても出会う、標準の道具

> 出典（一次情報）:
> - [venv — Creation of virtual environments (docs.python.org)](https://docs.python.org/3/library/venv.html) — 仮想環境の仕組み、activate と `VIRTUAL_ENV`、移動できないこと
> - [User Guide (pip.pypa.io)](https://pip.pypa.io/en/stable/user_guide/) / [Install packages in a virtual environment using pip and venv (packaging.python.org)](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) — `python -m pip`、requirements file、constraints file、dependency groups、標準の手順
> - [PEP 668](https://peps.python.org/pep-0668/) / [Externally Managed Environments (packaging.python.org)](https://packaging.python.org/en/latest/specifications/externally-managed-environments/) — `externally-managed-environment` の仕様
> - [pipx (pipx.pypa.io)](https://pipx.pypa.io/stable/) / [The pip interface (docs.astral.sh)](https://docs.astral.sh/uv/pip/) / [Migrating from pip to a uv project (docs.astral.sh)](https://docs.astral.sh/uv/guides/migration/pip-to-project/) — 代わりの道具と移行の手順
>
> 最終更新: 2026-11-08（Python 3.15.2・pip 26.2.2（venv が入れる版）・uv 0.13.7・pipx 1.18.16・Docker 29.9.2 で検証）

Node.js で言えば、**venv はプロジェクト専用の `node_modules/` と、それを使う `node` へのリンクをまとめたもの**、pip は `npm install` だけを受け持つインストーラである。どちらも Python の標準の道具で、uv が作る `.venv` も同じ形をしている。
README・Dockerfile・CI の設定・ライブラリの docs は今も pip と venv で書かれていることが多い。このページは、uv を使う読者がそれを読み解き、出会うエラーを直すためのものである。uv のコマンドは [uv](uv.md)、`.venv` の中身は [Step 03](../steps/03-project.md) を参照。

---

## 1. TL;DR

- **venv は「Python へのリンク・pip だけの `site-packages`・`pyvenv.cfg`」の組**。activate は PATH の先頭・`VIRTUAL_ENV`・プロンプトを変えるだけで、無くても `.venv/bin/python` で動く（§3.1）。
- **pip は `python -m pip` で呼ぶ**。手元の PATH には、別々の Python に属する `pip3` が 4 つあった（§3.2）。
- **`error: externally-managed-environment` は PEP 668 による正しい拒否**。Homebrew と uv が入れた Python、Debian の `python3` が該当する。`--break-system-packages` で押し通さず、venv を作る（§4.1）。
- **requirements.txt のプロジェクトは `uv add -r requirements.in -c requirements.txt` で、版を変えずに uv へ移せる**（§4.3）。コマンドラインのツールは pipx か `uv tool install` で入れる（§5）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js（npm） | 標準の道具 |
|---|---|---|
| 依存の置き場所を作る | `npm install` が `node_modules/` を作る | `python -m venv .venv` |
| ローカルのコマンドを動かす | `npx x`（`node_modules/.bin/x`） | `source .venv/bin/activate` してから `x`、または `.venv/bin/x` |
| 依存を入れる | `npm install x`（`package.json` に書く） | `python -m pip install x`（どこにも書かない） |
| 自分のパッケージをつなぐ | `npm link` | `python -m pip install -e .` |
| コマンドをグローバルに入れる / 一度だけ動かす | `npm install -g x` / `npx x` | `pipx install x` / `pipx run x` |

> **ポイント**: Node は依存を「読み込むファイルの場所」から探すので、どの `node` で動かしても同じ `node_modules/` が見える。Python は**起動した Python が自分の `site-packages` だけを見る**（[Step 03](../steps/03-project.md) §3.6）。activate は「どの Python を起動するか」を PATH で切り替える仕組みにすぎない。

---

## 3. 早見表

### 3.1 venv と activate

Python 3.15 で venv を作って中を見たあと、activate の前後と `deactivate` の後で、`python` の解決先・`VIRTUAL_ENV`・プロンプトを表示する `show-activate.sh` を動かす（検証済み。パスの `$PWD` は `.` と表示する）。

```bash
PS1='$ '   # 対話シェルのプロンプトの代わり
show() { echo "$1: python=$(command -v python | sed "s|$PWD|.|") VIRTUAL_ENV=${VIRTUAL_ENV/#$PWD/.} PS1='$PS1'"; }
show "activate の前"; source .venv/bin/activate; show "activate の後"
deactivate; show "deactivate の後"
```

実行結果:

```text
$ python3.15 -m venv .venv
$ cat .venv/pyvenv.cfg
home = ~/.local/bin
include-system-site-packages = false
version = 3.15.2
…（中略: 2 行）…
$ for f in .venv/bin/python*; do echo "$f -> $(readlink $f)"; done
.venv/bin/python -> python3.15
.venv/bin/python3 -> python3.15
.venv/bin/python3.15 -> ~/.local/bin/python3.15
$ bash show-activate.sh
activate の前: python=~/.asdf/shims/python VIRTUAL_ENV= PS1='$ '
activate の後: python=./.venv/bin/python VIRTUAL_ENV=./.venv PS1='(.venv) $ '
deactivate の後: python=~/.asdf/shims/python VIRTUAL_ENV= PS1='$ '
```

- Python 本体はコピーされず、元の Python（ここでは uv が `~/.local/bin` に置いた `python3.15`）へのリンクが置かれる。`pyvenv.cfg` の `home` が元のありかを指し、これがあると Python は `sys.prefix` を venv に向ける。venv の中かは `sys.prefix != sys.base_prefix` で判定できる（公式 docs）。`site-packages` に最初からあるのは pip（26.2.2）だけである
- activate がするのは、**`.venv/bin` を PATH の先頭に足す・`VIRTUAL_ENV` を立てる・プロンプトに `(.venv)` を付ける**の 3 つで、`deactivate` で戻る。今のシェルに `source` で読み込むスクリプトなので、`bash .venv/bin/activate` と子プロセスで動かしても効かない。公式 docs も "You don't specifically _need_ to activate a virtual environment, as you can just specify the full path to that environment's Python interpreter when invoking Python." と書く。uv では `uv run` が activate の代わりをする

### 3.2 pip の基本

requirements.txt（`requests>=2.32` と `rich`）に、constraints file（`urllib3<2.8`）を添えて入れる（検証済み）。

実行結果:

```text
$ .venv/bin/python -m pip install -r requirements.txt -c constraints.txt
Collecting requests>=2.32 (from -r requirements.txt (line 1))
…（中略: 29 行）…
Successfully installed certifi-2026.10.23 charset_normalizer-3.5.2 idna-3.20 markdown-it-py-4.2.0 mdurl-0.1.2 pygments-2.21.0 requests-2.34.2 rich-15.0.0 urllib3-2.7.0
…（中略: 3 行）…
```

- constraints file は版の範囲を絞るだけで、それ自体は入れない（pip docs: "Including a package in a constraints file does not trigger installation of the package."）。requests の依存の urllib3 が、最新の 2.8.0 ではなく 2.7.0 になった（`pip freeze` も `urllib3==2.7.0` を書き出した）。`pip freeze` は、自分で選んだ依存と推移的な依存を区別せずに `名前==版` を並べる。これを `requirements.in`（直接の依存）と `requirements.txt`（固定した全体）に分けたのが pip-tools で、uv の移行ガイドは `pyproject.toml` が "replaces `requirements.in` files"、`uv.lock` が "replaces `requirements.txt` files" と書く

**素の `pip` ではなく `python -m pip` で呼ぶ**。pip docs は "`python -m pip` executes pip using the Python interpreter you specified as python." と書き、Homebrew の docs も "Use `python3 -m pip` instead of a bare `pip` command when it is important to select the same interpreter and installer." と勧める。素の `pip3` は PATH で最初に見つかったものが動く。手元では asdf・Homebrew・python.org のインストーラ・macOS 付属の 4 つが、同じ名前で別々の Python に入れた（検証済み）。

実行結果:

```text
$ for p in $(which -a pip3 | uniq); do echo "$p -> $($p --version 2>&1)"; done
~/.asdf/shims/pip3 -> pip 26.2.2 from ~/.asdf/installs/python/3.15.2/lib/python3.15/site-packages/pip (python 3.15)
/opt/homebrew/bin/pip3 -> pip 26.2.2 from /opt/homebrew/lib/python3.15/site-packages/pip (python 3.15)
/usr/local/bin/pip3 -> pip 24.3.1 from /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/pip (python 3.12)
/usr/bin/pip3 -> pip 21.2.4 from /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages/pip (python 3.9)
…（中略: 1 行）…
```

[Step 03](../steps/03-project.md) の faq-app も、uv を使わずに `python3.15 -m venv .venv` と `.venv/bin/python -m pip install -e .` で入り、`.venv/bin/faq` が動いた（検証済み）。pip は `Installing build dependencies` と出して、`[build-system]` の `uv_build` を一時的な環境に入れてからビルドする（pip の build isolation）。ただし `[dependency-groups]` は入れないので、pip 25.1 からの `python -m pip install --group dev` が別に要る（`--dry-run` で ipython を含む 16 個を入れると表示した）。uv なら `uv sync` 1 つで両方が済む。

### 3.3 uv との対応表

| 標準の道具 | uv の pip 互換（`uv pip`） | uv のプロジェクト |
|---|---|---|
| `python -m venv .venv` | `uv venv`（**pip は入らない**。要るなら `--seed`） | `uv sync` / `uv run` が自動で作る |
| `source .venv/bin/activate` | 不要（カレントか親の `.venv` を探す） | `uv run` |
| `python -m pip install x` / `-r requirements.txt` | `uv pip install x` / `-r requirements.txt` | `uv add x` / `uv add -r requirements.txt`（§4.3） |
| `python -m pip install -e .` / `--group dev` | `uv pip install -e .` / `--group dev` | `uv sync`（editable と `dev` が既定） |
| `python -m pip freeze` | `uv pip freeze` | `uv export --format requirements.txt` |
| `pip-compile requirements.in`（pip-tools） | `uv pip compile requirements.in -o requirements.txt` | `uv lock` |
| `pip-sync requirements.txt`（pip-tools） | `uv pip sync requirements.txt`（ファイルに無いものを消す。検証済み） | `uv sync` |
| `pipx install x` / `pipx run x` | — | `uv tool install x` / `uvx x` |

---

## 4. 推奨の使い方（2026-11）

### 4.1 `externally-managed-environment` には venv で応える

Homebrew の Python 3.15 で、venv の外に入れようとする（検証済み）。メッセージは venv と pipx を案内する。pip は何も変えずに終了コード 1 で止まり、その後も `import requests` は `ModuleNotFoundError` のままだった。拒否するかは、標準ライブラリのディレクトリにある `EXTERNALLY-MANAGED` というファイルで決まり、venv の中では見ない（PEP 668）。手元と Docker で確かめた結果は、実行結果の下の表のとおり（検証済み）。

実行結果:

```text
$ /opt/homebrew/bin/python3.15 -m pip install requests
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
…（中略: 28 行）…
hint: See PEP 668 for the detailed specification.
```

| Python | `EXTERNALLY-MANAGED` | venv の外への `pip install` |
|---|---|---|
| Homebrew の `python3.15` | あり | 拒否（上の実行結果） |
| uv が入れた `python3.15` | あり（"This Python installation is managed by uv and should not be modified."） | 拒否 |
| Debian 13（trixie）の apt の `python3`（3.13.5） | あり（`/usr/lib/python3.13/EXTERNALLY-MANAGED`） | 印の有無だけを確かめた |
| Docker の公式イメージ `python:3.15-slim` | なし | 通る（root の警告が出る。§6） |

- **`--break-system-packages` は直し方にならない**。PEP 668 は、この上書きの手段を "should carry some connotation that its use is risky" と定めている（pip.conf の `break-system-packages = true` や `PIP_BREAK_SYSTEM_PACKAGES` は、保護をずっと外す）。守っているのは OS や Homebrew が入れたパッケージである。手元の Homebrew の `python3.15 -m pip list` には、formula が入れた numpy・pydantic・cryptography・mercurial が並んでいた（検証済み）。PEP 668 は、pip で入れると "you may end up removing packages that are shipped by the system's package manager" と書く
- 直し方は、ライブラリなら venv（uv なら `uv add` / `uv venv`）、コマンドなら pipx か `uv tool install`、OS のパッケージで足りるなら `brew install` / `apt install` である

### 4.2 出会う場面ごとの読み方

| 場面 | よく見る書き方 | 読み方・uv での書き換え |
|---|---|---|
| ライブラリの README・古いプロジェクト | `pip install "fastapi[standard]"`・`pip install -r requirements.txt` | プロジェクトでは `uv add "fastapi[standard]"`。一度だけ試すなら `uv run --with ...`。requirements.txt は venv と `pip install -r` でそのまま動き、uv へは §4.3 の手順で移せる |
| Dockerfile | `FROM python:3.15-slim` の後に `RUN pip install -r requirements.txt` | 公式イメージには印が無いので通るが、root の警告が出る（§6）。uv を使う書き方は [Step 11: 配布とデプロイ](../steps/11-deploy.md) |
| Debian 系のイメージ | `apt-get install python3-pip` の後に `pip install …` | 印がある（検証済み）ので、PEP 668 どおりなら拒否される。`python3 -m venv /opt/venv` を作り、その中の pip を使う |
| CI の設定例 | `pip install -r requirements.txt` | `uv pip` に替えるとき、venv を作らない CI では `--system` か `UV_SYSTEM_PYTHON` が要る（uv の GitHub Actions の docs: "uv requires a virtual environment by default"） |

### 4.3 requirements.txt から uv のプロジェクトへ移す

uv の移行ガイドの手順を試す。題材は `requests>=2.32` と `rich` の `requirements.in` と、それを `uv pip compile requirements.in -o requirements.txt --exclude-newer 2026-06-01` で 2026-06-01 時点の版に固定した `requirements.txt` である（古いプロジェクトの代わり。`.venv` は `uv pip sync requirements.txt` で作ってある。検証済み）。

実行結果:

```text
$ uv init --bare
Initialized project `legacy-app`
$ uv add -r requirements.in -c requirements.txt
Resolved 10 packages in 8ms
Checked 9 packages in 0.78ms
$ uv run app.py
requests 2.34.2
rich 15.0.0
urllib3 2.7.0
```

- `uv init --bare` は `pyproject.toml` だけを作る（公式 docs）。移行ガイドの例は素の `uv init` だが、uv 0.12 からは `src/<名前>/` まで作る（[Step 03](../steps/03-project.md)）ので、コードが既にあるなら `--bare` が合う。`dependencies` には `"requests>=2.32"` と `"rich>=15.0.0"` が書かれた
- `-c requirements.txt` で、`uv.lock` は requirements.txt の版を引き継いだ（urllib3 は 2.7.0）。`-c` を付けないと、その日の最新（urllib3 2.8.0 など）で解決し直した（検証済み）。後から上げるなら `uv lock --upgrade-package urllib3`（`Updated urllib3 v2.7.0 -> v2.8.0` と出た。検証済み）。開発用は `uv add --dev -r requirements-dev.in -c requirements-dev.txt` で dev グループに移す。ただし `requirements-dev.in` が `-r requirements.in` で本体の依存を取り込んでいるなら、その行を除いてから渡す（移行ガイド: "it will need to be stripped to avoid adding the base requirements to the dev dependency group"）

---

## 5. 選び方・代替との比較（pipx と `uv tool install`）

| 項目 | pipx 1.18.16 | `uv tool install`（uv 0.13.7） |
|---|---|---|
| すること | ツールごとに venv を作り、実行ファイルを PATH に出す（pipx docs: "creates a separate virtual environment for each application"） | 同じ（uv docs: "similar to `pipx`"） |
| venv の置き場所（macOS の既定） | `~/Library/Application Support/pipx/venvs/` | `~/.local/share/uv/tools/` |
| 実行ファイルの置き場所 | `~/.local/bin`（`PIPX_BIN_DIR`） | `~/.local/bin`（`UV_TOOL_BIN_DIR`） |

両方で pre-commit 4.7.0 を入れると、どちらもツール専用の venv と、そこへの実行ファイルのリンクを作った（検証済み。置き場所は作業用のディレクトリに向けた）。uv を使っているなら `uv tool install` で足りる。なお、どちらも既定では同じ `~/.local/bin` に実行ファイルを置く。

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `error: externally-managed-environment`（検証中に発生） | venv の外の Python に pip で入れようとした。Homebrew と uv の Python には PEP 668 の印がある | venv を作るか `uv add`。`--break-system-packages` は使わない（§4.1） |
| `uv venv` で作った venv で `python -m pip` が `No module named pip`（検証中に発生） | `uv venv` は既定で pip を入れない（`--seed` の説明: "Install seed packages (one or more of: `pip`, `setuptools`, and `wheel`)"） | `uv pip install x` を使う。pip 自体が要るなら `uv venv --seed` |
| venv のディレクトリを改名したら、`bin/pip` が `bad interpreter: No such file or directory`（検証中に発生） | `bin/pip` の shebang と `activate` に、作ったときの絶対パスが書かれている。`bin/python` と `bin/python -m pip` は動いた | 作り直す。公式 docs: "Not considered as movable or copyable – you just recreate the same environment in the target location." |
| `PIP_INDEX_URL` を設定した CI で、`uv pip` が社内の index を見ない | uv は `pip.conf` と `PIP_*` の環境変数を読まない。uv の docs も `uv pip` は元の道具を "do not _exactly_ implement" と断っている | `UV_DEFAULT_INDEX`（`--default-index`）か `[[tool.uv.index]]` に書き直す。`UV_INDEX_URL` と `--index-url` も効くが、uv 0.13.7 の `--help` は "Deprecated: use `--default-index` instead" と表示する |
| `docker run --rm python:3.15-slim pip install -q requests` で `WARNING: Running pip as the 'root' user can result in broken permissions …`（検証中に発生） | 公式イメージには印が無く、root のままイメージの `site-packages` に入れている。警告は "It is recommended to use a virtual environment instead" と続く | イメージの中でも venv を作るか uv を使う。警告だけ消すなら `--root-user-action=ignore`（`PIP_ROOT_USER_ACTION`） |

---

## 出典

| 情報源 | URL |
|---|---|
| venv / Virtual Environments and Packages / Install packages in a virtual environment using pip and venv | https://docs.python.org/3/library/venv.html ・ https://docs.python.org/3/tutorial/venv.html ・ https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/ （2026-11-08 確認。Python 3.15.2 の docs。pip の警告の https://pip.pypa.io/warnings/venv はチュートリアルへ転送される） |
| pip — User Guide / pip install / Build System Interface / Changelog | https://pip.pypa.io/en/stable/user_guide/ ・ https://pip.pypa.io/en/stable/cli/pip_install/ ・ https://pip.pypa.io/en/stable/reference/build-system/ ・ https://pip.pypa.io/en/stable/news/ （2026-11-08 確認、Context7 `/websites/pip_pypa_io_en_stable` 経由。`--group` は 25.1 で追加） |
| PEP 668 / Externally Managed Environments / Homebrew — Language Runtimes and Packages | https://peps.python.org/pep-0668/ ・ https://packaging.python.org/en/latest/specifications/externally-managed-environments/ ・ https://docs.brew.sh/Language-Runtimes-and-Packages （2026-11-08 確認。PEP 668 は Final） |
| pipx / pip-tools | https://pipx.pypa.io/stable/ ・ https://pip-tools.pypa.io/en/latest/ ・ https://github.com/pypa/pip-tools （2026-11-08 確認。pipx の既定の置き場所は `pipx environment` で確認。pip-tools のリポジトリは jazzband から pypa へ移っている） |
| uv — The pip interface / Compatibility with pip / Using Python environments / Locking environments / Migrating from pip / Creating projects / Tools / GitHub Actions | https://docs.astral.sh/uv/pip/ ・ https://docs.astral.sh/uv/pip/compatibility/ ・ https://docs.astral.sh/uv/pip/environments/ ・ https://docs.astral.sh/uv/pip/compile/ ・ https://docs.astral.sh/uv/guides/migration/pip-to-project/ ・ https://docs.astral.sh/uv/concepts/projects/init/ ・ https://docs.astral.sh/uv/concepts/tools/ ・ https://docs.astral.sh/uv/guides/integration/github/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由） |
| Docker Official Image — python | https://hub.docker.com/_/python （2026-11-08 確認。`python:3.15-slim` と `debian:trixie-slim` を実際に動かした） |

### 確認できなかった事項

- **Debian の pip が実際に拒否するか**。`python3` に `EXTERNALLY-MANAGED` があることは確かめたが、`python3-pip` を入れて `pip install` するところまでは動かしていない。Ubuntu のイメージは調べていない
- **venv が入れる pip の版の決まり方**。Python 3.15.2 の venv は pip 26.2.2 を入れた（最新は 26.3）。`ensurepip` が同梱する版を上げる規則は確かめていない

- 関連: [Python 学習ガイド](../README.md) / [uv](uv.md) / [Step 01: 環境構築](../steps/01-setup.md) / [Step 03: プロジェクト構成](../steps/03-project.md) / [Python の版の選び方](python-versions.md) / [pyproject.toml](pyproject-toml.md)
