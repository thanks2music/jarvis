# Step 03: プロジェクト構成 — uv init でパッケージを作り、依存を管理する

> 出典（一次情報）:
> - [Creating projects (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/init/) — `uv init` の既定の構成（uv 0.12 からパッケージ化）と `--no-package`・`--lib`
> - [Project structure and files (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/layout/) — `.venv` と `uv.lock` の扱い
> - [Locking and syncing (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/sync/) — editable なインストール、exact な同期、`--locked`、`--no-dev`
> - [Managing dependencies (docs.astral.sh)](https://docs.astral.sh/uv/concepts/projects/dependencies/) — `dev` グループが既定で入ること
> - [src layout vs flat layout (packaging.python.org)](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — コードを `src/` に置く理由
> - [pyproject.toml specification (packaging.python.org)](https://packaging.python.org/en/latest/specifications/pyproject-toml/) — `[project]` の仕様（PEP 621 の現行版）
> - [PEP 735 – Dependency Groups in pyproject.toml](https://peps.python.org/pep-0735/) — `[dependency-groups]`
>
> 最終更新: 2026-11-08（uv 0.13.7・Python 3.15.2 で検証）

Node.js では `npm init` で `package.json` を作り、依存は `node_modules/` に入り、コマンドは `bin` で登録する。自分のコードは、リポジトリにあるファイルをそのまま `import` できる。
Python では `uv init` が `pyproject.toml` と `src/faq/` を作り、最初の `uv run` が `.venv/` を作って、**プロジェクト自身もそこへインストールする**。インストールしていない Python からは、自分のコードでも import できない。
このステップでは、[Step 02](02-language.md) までの 1 ファイルのスクリプトを `faq` パッケージに分け、`faq` コマンドと `python -m faq` で動かし、開発用の依存を足す。実行時の依存（pydantic）は [Step 04](04-typing.md) で足す。全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **`uv init` はパッケージの形で作る**（uv 0.12.0 からの既定）。`src/faq/__init__.py`・ビルドの設定（`uv_build`）・`faq` コマンドの登録（`[project.scripts]`）がそろう。旧来の `main.py` だけの構成は `--no-package`、ライブラリは `--lib`（§3.1・§3.2）。
- **`uv run faq` が `.venv/` を作り、プロジェクトを editable で入れる**。`.venv` の中の `faq.pth` が `src/` を指すだけなので、ソースを直しても入れ直しは要らない。`npm link` に近い（§3.4）。
- **パッケージは `.venv` の中にしか無い**。素の `python3.15 -c "import faq"` は `ModuleNotFoundError` になる。`uv run` を通す（§3.6）。
- **開発用の依存は `uv add --dev`** で `[dependency-groups]`（PEP 735）に入る。配布物のメタデータには載らない。本番の環境から外すには `uv sync --no-dev`（§3.7・§3.8）。
- **コミットするのは `pyproject.toml`・`uv.lock`・`.python-version`**。`.venv/` はしない。CI では `uv sync --locked` で lockfile のずれを止める（§3.8）。

---

## 2. Node.js / Bun との対応

| やりたいこと・ファイル | Node.js（npm / pnpm） | Bun | Python（uv） |
|---|---|---|---|
| プロジェクトを作る | `npm init` / `pnpm init` | `bun init` | `uv init` |
| メタデータと依存を書く | `package.json` | `package.json` | `pyproject.toml` の `[project]` |
| コマンドを登録する | `bin` | `bin` | `[project.scripts]` |
| lockfile | `package-lock.json` / `pnpm-lock.yaml` | `bun.lock` | `uv.lock` |
| ランタイムの版 | `.nvmrc` / `.node-version` | — | `.python-version` |
| 依存の置き場所 | `node_modules/` | `node_modules/` | `.venv/lib/python3.15/site-packages/` |
| 開発中の自分のパッケージをつなぐ | `npm link` / `file:` 依存 | `bun link` | editable install（`uv run` / `uv sync` が自動で行う） |
| 開発用の依存 | `devDependencies` | `devDependencies` | `[dependency-groups]` の `dev` |
| 開発用の依存を除いて入れる | `npm ci --omit=dev` / `pnpm install --prod` | `bun install --production` | `uv sync --no-dev` |
| lockfile どおりに入れる（CI） | `npm ci` / `pnpm install --frozen-lockfile` | `bun install --frozen-lockfile` | `uv sync --locked` |

> **ポイント**: Node は `node_modules/` を、読み込む側のファイルのディレクトリから親へ順にたどって探す。だから、プロジェクトの中で動かせば、どの `node` でも依存が見える。Python は**どの Python を起動したか**で、見える `site-packages` が決まる。プロジェクトの依存が見えるのは `.venv` の Python だけである（§3.6）。

---

## 3. ハンズオン

作業ディレクトリは Step 01・02 と同じ `faq-app/` である（`.python-version`・`count.py`・`categories.py`・`data/faq.jsonl` がある）。実行結果の絶対パスは `~/faq-app` に、`file://` の URL は `file:///path/to/faq-app` に読み替えて載せている。

### 3.1 `uv init` で骨組みを作る

狙い: 既にあるディレクトリを uv のプロジェクトにする。`faq-app/` で `uv init` を実行し、増えたファイルを見る（検証済み）。

実行結果:

```text
$ uv init --name faq
Initialized project `faq`
$ find . -type f -not -path "./.venv/*" -not -path "./data/*" | sort
./.python-version
./categories.py
./count.py
./pyproject.toml
./README.md
./src/faq/__init__.py
$ cat src/faq/__init__.py
def main() -> None:
    print("Hello from faq!")
```

- 増えたのは `pyproject.toml`・`README.md`・`src/faq/__init__.py` の 3 つ。既にある `.python-version`（`3.15`）は `requires-python` を決めるために読まれるだけで、書き換えられない（uv 0.13.7 のソース）
- `--name` を省くと、ディレクトリ名から決まる。空の `faq-app/` で試すと、配布名が `faq-app`、import する名前が `faq_app`（`-` は `_` になる）、コマンドが `faq-app = "faq_app:main"` になった（検証済み）。ここでは短く `faq` にする
- **この検証は、既にある git リポジトリの中で行った**。そのため `.gitignore` も `.git/` もできていない（§3.3）

### 3.2 `pyproject.toml` を読む

狙い: 生成された設定の各行が、`package.json` のどこにあたるかを押さえる（検証済み）。

実行結果:

```text
$ cat pyproject.toml
[project]
name = "faq"
version = "0.1.0"
…（中略: 5 行）…
requires-python = ">=3.15"
dependencies = []

[project.scripts]
faq = "faq:main"

[build-system]
requires = ["uv_build>=0.13.7,<0.14.0"]
build-backend = "uv_build"
```

| 項目 | 意味 | `package.json` で言うと |
|---|---|---|
| `name` / `version` | 配布名と版。版の書き方は semver ではなく PEP 440 | `name` / `version` |
| 中略した 5 行 | `description`・`readme`・`authors`。`authors` は git の `user.name` / `user.email` から入る（`--author-from none` で止められる） | `description` / `author` |
| `requires-python` | 対応する Python の版。`uv init` が使った Python（ここでは `.python-version` の 3.15）から決まる | `engines.node` |
| `dependencies` | 実行時の依存。まだ空 | `dependencies` |
| `[project.scripts]` | `faq` コマンドを作り、`faq` パッケージの `main()` を呼ぶ（`モジュール:関数` の形）。仕様上は entry point の `console_scripts` グループ | `bin` |
| `[build-system]` | このプロジェクトを wheel（配布物）にする道具。`uv init` を実行した uv の版（0.13.7）から、次のマイナー版の手前までが入る | 近いのは `tsc` の設定 |

> **ポイント**: `[build-system]` は「このディレクトリはインストールできるパッケージだ」という宣言である。これがあるから、§3.4 で uv がプロジェクト自身を `.venv` に入れる。各項目の書き方は [pyproject.toml](../topics/pyproject-toml.md) に任せる。

`uv init` には、ほかに 2 つの型がある。空のディレクトリで 3 つを作り比べた（検証済み。`--vcs none --author-from none` を付けた）。`--no-package` は uv 0.11 までの既定で、0.12.0 の changelog は既定を戻した理由に「テストやほかのコードから import でき、依存として入れられ、コマンドとして動かせる」ことを挙げる。

| | `uv init`（既定。`--app` と同じ） | `--no-package` | `--lib` |
|---|---|---|---|
| コードの置き場所 | `src/faq/__init__.py` | 直下の `main.py` | `src/faq/__init__.py` |
| `[build-system]` / `[project.scripts]` | あり / あり | なし / なし | あり / なし |
| `py.typed`（型情報を配る印。[Step 04](04-typing.md)） | なし | なし | あり |
| プロジェクト自身が `.venv` に入るか | 入る（editable） | 入らない | 入る（editable） |
| 公式 docs が挙げる用途 | Web サーバー・スクリプト・CLI | ビルドの設定を使わないとき | PyPI などで配るライブラリ |

### 3.3 git の外で `uv init` した場合

狙い: 新しいリポジトリを始めるときに、uv が何を用意するかを知る。別の空の `faq-app/` で試す（検証済み）。

実行結果:

```text
$ git rev-parse --is-inside-work-tree
fatal: not a git repository (or any of the parent directories): .git
$ uv init --name faq
Initialized project `faq`
$ ls -A
.git
.gitignore
.python-version
pyproject.toml
README.md
src
```

- 検証の作業場所そのものが git リポジトリの中にあるため、環境変数 `GIT_CEILING_DIRECTORIES` で git に親のディレクトリを探させないようにして「git の外」を作った。`git rev-parse` が返した `fatal` がその確認である
- `--vcs` の既定は `git` である（`uv help init`: "By default, uv will initialize a Git repository (`git`)."）。ただし uv は先に `git rev-parse --is-inside-work-tree` で調べ、**git の管理下なら `git init` も `.gitignore` の作成も飛ばす**。`--vcs git` を明示しても同じである。git が入っていない環境では、既定のままなら黙って飛ばし、`--vcs git` を明示したときだけ失敗する（いずれも uv 0.13.7 のソース）
- 作られた `.gitignore` は、`__pycache__/`・`*.py[oc]`（バイトコード）、`build/`・`dist/`・`wheels/`・`*.egg-info`（ビルドの成果物）、`.venv` の 7 項目を除外する（検証済み）。モノレポの中に作るときは、これらを親の `.gitignore` に自分で足す。`uv.lock` と `.venv/` は、最初の `uv run`（か `uv sync` / `uv lock`）で作られる

### 3.4 `uv run faq` で動かす — `.venv` と editable install

狙い: 登録された `faq` コマンドを動かし、uv が裏で何をしたかを見る（検証済み）。

実行結果:

```text
$ uv run faq
Using CPython 3.15.2
Creating virtual environment at: .venv
   Building faq @ file:///path/to/faq-app
      Built faq @ file:///path/to/faq-app
Installed 1 package in 5ms
Hello from faq!
```

`uv run` は、実行の前に `.venv/` と `uv.lock` を作り、最新にする。`npm install` を打つ工程が無い。`Building faq` / `Built faq` は、プロジェクト自身を wheel にビルドして `.venv` に入れた印である。

`.venv` の中に何が入ったかを見る（検証済み）。

実行結果:

```text
$ ls .venv .venv/lib/python3.15/site-packages
.venv:
bin
CACHEDIR.TAG
lib
pyvenv.cfg

.venv/lib/python3.15/site-packages:
faq-0.1.0.dist-info
faq.pth
$ cat .venv/lib/python3.15/site-packages/faq.pth; echo
~/faq-app/src
```

- `site-packages` にあるのは、インストールの記録（`faq-0.1.0.dist-info`）と `faq.pth` だけで、**コードのコピーは無い**
- `faq.pth` には `src/` の絶対パスが 1 行だけ書いてある。Python は起動時に `site-packages` の `.pth` を読み、各行を `sys.path`（import の探索先）に足す（`site` モジュールの仕様）。これが editable install の正体である
- Node で言えば、`npm link` で `node_modules/faq` を自分のソースへの symlink にした状態に近い。ソースを直せば、入れ直さなくても反映される（§3.5）。uv が入れ直すのは、`pyproject.toml`・`setup.py`・`setup.cfg` が変わったときか、`src` ディレクトリを足した・消したときだけである（uv の Caching の docs）
- `.venv/bin/faq` は `[project.scripts]` から作られた 10 行のラッパーで、`.venv` の Python で `from faq import main` し、`sys.exit(main())` するだけである（検証済み）。`node_modules/.bin/` の shim にあたる

### 3.5 モジュールに分ける

狙い: 1 ファイルを役割ごとに分け、パッケージの中で import し合う。4 つのファイルを書く（検証済み。1 つのブロックにまとめたが、`# src/faq/...` の行ごとに別のファイルである）。

```python
# src/faq/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Faq:
    id: str
    category: str
    question: str
    answer: str

# src/faq/loader.py
import json
from pathlib import Path

from faq.models import Faq


def load_faqs(path: Path) -> list[Faq]:
    with path.open(encoding="utf-8") as f:
        return [Faq(**json.loads(line)) for line in f if line.strip()]

# src/faq/__init__.py
from pathlib import Path

from faq.loader import load_faqs
from faq.models import Faq

__all__ = ["Faq", "load_faqs", "main"]


def main() -> None:
    faqs = load_faqs(Path("data/faq.jsonl"))
    print(f"{len(faqs)} 件の FAQ を読み込んだ")

# src/faq/__main__.py
from faq import main

main()
```

| ファイル | 役割 | TS で言うと |
|---|---|---|
| `models.py` | データの型。`@dataclass(frozen=True)` は、コンストラクタ・`==`・表示（`__repr__`）を自動で作り、属性への代入を禁じる | `readonly` なプロパティだけの class |
| `loader.py` | JSONL を読み、`Faq` のリストにする。`Faq(**d)` は dict をキーワード引数に展開する | `new Faq({ ...d })` に近い（ただし引数名と突き合わせる） |
| `__init__.py` | パッケージの入口で、`import faq` のときに実行される。下のモジュールの名前を持ち上げ、公開する名前を `__all__` に並べる | `index.ts` の `export { loadFaqs } from "./loader"` |
| `__main__.py` | `python -m faq` で実行される | `node .` で `main` を動かすこと |

- パッケージの中も `from faq.models import Faq` のように、**パッケージ名から書く絶対 import** にする。TS の `./models` の感覚で `from models import Faq` と書くと動かない（§5）
- `__all__` は `from faq import *` で入る名前を決め、型チェッカーには公開の API を伝える。`from faq import Faq` は `__all__` が無くても動く。import の探索の仕組みや相対 import は [import の仕組み](../topics/imports.md) で扱う

動かす（検証済み）。

実行結果:

```text
$ uv run faq
12 件の FAQ を読み込んだ
$ uv run python -m faq
12 件の FAQ を読み込んだ
$ uv run python -c "from faq import load_faqs; from pathlib import Path; print(load_faqs(Path('data/faq.jsonl'))[0])"
Faq(id='faq-01', category='経費', question='経費精算の締め日はいつですか？', answer='毎月 25 日締めです。25 日までに経費システムで申請すると、翌月 10 日に給与口座へ振り込まれます。')
```

§3.4 の 1 回目と違い、`Building` の行が無い。ファイルを 3 つ足し、`__init__.py` を書き換えても、入れ直さずに新しいコードが動いた。editable だからである。`faq` コマンドと `python -m faq` は、同じ `main()` を呼ぶ別の入口である。

### 3.6 `.venv` の外からは import できない

狙い: 「どの Python で動かすか」で import の結果が変わることを確かめる（検証済み）。

実行結果:

```text
$ python3.15 -c "import faq"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import faq
ModuleNotFoundError: No module named 'faq'
$ .venv/bin/python -c "import faq; print(faq.__file__)"
~/faq-app/src/faq/__init__.py
```

- `python3.15` は、Step 01 で uv が `~/.local/bin` に置いた Python 本体のコマンドで、本体の `site-packages` には `faq` が入っていない。`.venv/bin/python` は `.venv` の `site-packages` を見る。そこの `faq.pth` が `src/` を `sys.path` に足すので、`src/faq/__init__.py` が見つかる
- `faq-app/` で実行しても素の Python で見つからないのは、`faq/` が直下ではなく `src/` の下にあるからである。これが src layout の狙いで、作業中のコードではなく、インストールしたものが必ず使われる（§4）
- `source .venv/bin/activate` で `.venv/bin` を PATH の先頭に足せば `python` だけで済むが、`uv run` を使えば activate は要らない。`node_modules/.bin` を PATH に足すかどうか、と同じ話である

### 3.7 開発用の依存を足す

狙い: 開発のときだけ使う道具を、実行時の依存と分けて入れる。高機能な REPL の IPython を足す（検証済み）。

実行結果:

```text
$ uv add --dev ipython
Resolved 18 packages in 10ms
   Building faq @ file:///path/to/faq-app
      Built faq @ file:///path/to/faq-app
Prepared 1 package in 36ms
Uninstalled 1 package in 2ms
Installed 17 packages in 115ms
 + asttokens==3.0.2
 + executing==2.3.0
 ~ faq==0.1.0 (from file:///path/to/faq-app)
 + ipython==9.18.1
…（中略: 13 行）…
```

`pyproject.toml` に足された部分と、依存のツリーを見る（検証済み）。

実行結果:

```text
$ cat pyproject.toml
…（中略: 9 行）…
dependencies = []
…（中略: 8 行）…
[dependency-groups]
dev = [
    "ipython>=9.18.1",
]
$ uv tree --depth 1
Resolved 18 packages in 7ms
faq v0.1.0
└── ipython v9.18.1 (group: dev)
```

- `--dev` は `[dependency-groups]` の `dev` グループに書く。PEP 735 で標準になった表で、仕様は "Build backends MUST NOT include Dependency Group data in built distributions as package metadata." と定める。Node の `devDependencies` は公開した `package.json` に残るが、こちらは配布物のメタデータにそもそも載らない
- 実行時の依存（`dependencies`）は空のままである。pydantic を足すのは [Step 04](04-typing.md)
- 書かれるのは下限だけ（`>=9.18.1`）で、`^` のような上限は付かない（[pyproject.toml](../topics/pyproject-toml.md)）。`~ faq==0.1.0` は、`pyproject.toml` が変わったのでプロジェクト自身を入れ直した印である
- `uv tree` は `npm ls` にあたり、`(group: dev)` で開発用と分かる。`.venv/bin` に `ipython` が増え（検証済み）、`uv run ipython` で起動できる。`dev` 以外のグループも作れる（`uv add --group docs ...`。[uv](../topics/uv.md)）

### 3.8 lockfile どおりにそろえる — CI と本番

狙い: CI と本番での同期の仕方を押さえる。§3.4 の `uv run faq` の直後にできた `uv.lock` には、プロジェクト自身が `source = { editable = "." }` として入っていた（検証済み）。TOML なので人が読めるが、公式 docs は "managed by uv and should not be edited manually" とする。

CI で使う `--locked` を試す（検証済み）。2 つ目と 3 つ目のコマンドは、別のコピーで `dependencies` を手で書き換え、`uv lock` をせずに実行したものである。

実行結果:

```text
$ uv sync --locked
Resolved 18 packages in 7ms
Checked 17 packages in 16ms
$ grep "^dependencies" pyproject.toml
dependencies = ["rich>=15"]
$ uv sync --locked
Resolved 21 packages in 153ms
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

`--locked` は、lockfile が `pyproject.toml` と合っていなければ終了コード 1 で失敗する。`npm ci` が `package.json` と lockfile のずれで失敗するのと同じで、CI ではこれを使う。`--frozen` との違いは [uv](../topics/uv.md) の §4 を参照。

本番用に開発用の依存を外し、また戻す（検証済み）。

実行結果:

```text
$ uv sync --no-dev
Resolved 18 packages in 7ms
Uninstalled 16 packages in 867ms
 - asttokens==3.0.2
 - executing==2.3.0
 - ipython==9.18.1
…（中略: 13 行）…
$ uv sync
Resolved 18 packages in 7ms
Installed 16 packages in 97ms
 + asttokens==3.0.2
 + executing==2.3.0
 + ipython==9.18.1
…（中略: 13 行）…
```

- `--no-dev` で、`dev` グループの 16 個（IPython と、IPython が使う 15 個）が消えた。`uv sync` は exact に同期するので、選ばれなかったものを消す。次の素の `uv sync` で戻るのは、`dev` グループが既定で入るからである。⚠️ 素の `uv run` も既定で `dev` グループを入れる。`uv sync --no-dev` の直後に `uv run python -c "import IPython; ..."` を打つと、`Installed 16 packages` と出て入り直した（検証済み）。本番では `uv run --no-dev` か、環境変数 `UV_NO_DEV=1` を使う

最後に、何をコミットするかをまとめる。`.venv/` の中には uv が置いた `.gitignore` があり、中身は `*` の 1 行だった（検証済み）。

| ファイル | コミット | Node で言うと | 理由 |
|---|---|---|---|
| `pyproject.toml`・`src/`・`README.md` | する | `package.json`・`src/` | プロジェクトそのもの |
| `uv.lock` | する | `package-lock.json` / `pnpm-lock.yaml` / `bun.lock` | 公式 docs: "This file should be checked into version control, allowing for consistent and reproducible installations across machines." |
| `.python-version` | する | `.nvmrc` | uv が版を選ぶのに使う。GitHub Actions の `actions/setup-python` も `python-version-file` で読める（uv の GitHub Actions の docs） |
| `.venv/` | しない | `node_modules/` | 公式 docs: "It is not recommended to include the `.venv` directory in version control"。中の `.gitignore` が `*` なので、親の `.gitignore` に書かなくても git に入らない |
| `__pycache__/` | しない | ビルドのキャッシュ | Python を動かすと `src/faq/__pycache__/` ができる（本ガイドの検証では `PYTHONDONTWRITEBYTECODE=1` で止めている）。git の中で `uv init` した場合は、自分で `.gitignore` に足す |

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| アプリも既定の `uv init`（パッケージの構成）で始める | `--no-package` で始め、後からテストや import で困る | 公式 docs: ビルドの設定を持つと "adding command-line entry points, and avoids common points of confusion with the Python import system" |
| import するコードは `src/<名前>/` に置く（src layout。uv の既定） | 理由なく直下に `faq/` を置く（flat layout） | `python -m` や `-c` で動かすと、Python はカレントディレクトリを import の探索先の先頭に入れる（スクリプトを直接動かすとそのディレクトリ。[import の仕組み](../topics/imports.md) §3.1）。flat layout だと、インストールしたものではなく作業中のコピーが使われ、配布物にファイルが入っていない誤りに気付けない。src layout は "ensuring that the installed copy is used"（packaging.python.org）。ただし同じページは flat layout も有効な構成として並べ、src layout は動かす前にインストールが要る手間があるとしている。uv はその手間を `uv run` で肩代わりする |
| パッケージの中は `from faq.models import Faq` と絶対 import で書く | `from models import Faq` と書く・`sys.path` を書き換えて通す | PEP 8: "Absolute imports are recommended"。明示的な相対 import（`from .models import Faq`）も "an acceptable alternative" とされる |
| `__main__.py` は短くし、関数を呼ぶだけにする | `__main__.py` に処理を書く | Python docs: "those files are kept short and import functions to execute from other modules"。`if __name__ == "__main__":` も付けない方がよいとされる（"a minimal `__main__.py` without a `__name__` check is preferred"） |
| `__init__.py` で公開する名前を `__all__` に並べる | 内部で使うだけの名前まで公開の扱いにする | 言語リファレンス: "`__all__` should contain the entire public API"。typing の仕様でも、`__all__` は公開の API を決めるほかの規則より優先される |
| 開発用の道具は `uv add --dev` で入れる | REPL やテストの道具を `dependencies` に入れる | `dependencies` は配布物のメタデータに入り、使う側にも入る。dependency groups は入らない（Dependency Groups の仕様） |
| `uv.lock` をコミットし、CI は `uv sync --locked` | lockfile を手で直す・`.venv` をコミットする | 公式 docs が lockfile のコミットと、手で直さないことを求めている。`--locked` なら lockfile のずれで CI が止まる |
| 本番は `uv sync --no-dev`、その後の実行も `uv run --no-dev`（または `UV_NO_DEV=1`） | `uv sync --no-dev` の後に素の `uv run` を打つ | `uv run` は既定で `dev` グループを入れ直す（§3.8）。ソースを持ち込まないコンテナでは `--no-editable` も使う（公式 docs。[Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ)で扱う） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `python3.15 -c "import faq"` が `ModuleNotFoundError: No module named 'faq'`（検証中に発生） | パッケージはプロジェクトの `.venv` にだけ入っている | `uv run python -c ...` か `.venv/bin/python` を使う（§3.6） |
| 既にある git リポジトリの中で `uv init` しても `.gitignore` ができない（検証中に発生） | uv は git の管理下だと分かると、`git init` と `.gitignore` の作成を飛ばす | `__pycache__/`・`*.py[oc]`・`dist/` などを親の `.gitignore` に足す。`.venv/` は中の `.gitignore` で除外される（§3.3・§3.8） |
| `from models import Faq` と書くと `ModuleNotFoundError: No module named 'models'. Did you mean: 'codecs'?`（検証で再現） | `sys.path` に入っているのは `src/` で、`src/faq/` ではない。`models` はトップレベルの名前ではない。`Did you mean` の候補は無関係な標準ライブラリである | `from faq.models import Faq`（または `from .models import Faq`）と書く |
| CI の `uv sync --locked` が "The lockfile at `uv.lock` needs to be updated" で落ちる（検証で再現） | `pyproject.toml` を手で直し、`uv lock` していない | 依存は `uv add` / `uv remove` で変える。手で直したら `uv lock` を実行し、lockfile も一緒にコミットする |
| `uv sync --no-dev` したのに、`uv run` で IPython が入り直す（検証で再現） | `uv run` も既定で `dev` グループを入れる | `uv run --no-dev`、または `UV_NO_DEV=1` |
| パッケージ名が `faq_app` になり、コマンドが `faq-app` になった | `--name` を省くと、ディレクトリ名から決まる（検証済み） | `uv init --name faq` で名前を指定する |
| `--no-package` で作ったプロジェクトで、`[project.scripts]` が効かない・テストから import できない | ビルドの設定が無いと、プロジェクトは `.venv` に入らない。公式 docs: "If the project does not define a build system, it will not be installed." | `[build-system]` を足すか、既定の `uv init` の構成で作り直す |

---

## 6. 次のステップ

- [Step 04: 型](04-typing.md) — `Faq` を pydantic のモデルに置き換えて実行時の依存を足し、型チェッカーで誤りを見つける
- Ruff と pytest を `dev` グループに足すのは [Step 05: 品質ツール](../README.md#4-学習ロードマップ) と [Step 06: テスト](../README.md#4-学習ロードマップ)
- 設定とコマンドを引くなら [pyproject.toml](../topics/pyproject-toml.md) と [uv](../topics/uv.md)

---

## 出典

| 情報源 | URL |
|---|---|
| Creating projects — uv | https://docs.astral.sh/uv/concepts/projects/init/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由。既定の構成・`--lib`・用途） |
| uv 0.12.x changelog | https://github.com/astral-sh/uv/blob/main/changelogs/0.12.x.md （2026-11-08 確認、Context7 経由。`uv init` の既定の変更と理由） |
| Project structure and files — uv | https://docs.astral.sh/uv/concepts/projects/layout/ （2026-11-08 確認。`.venv` をコミットしないこと、中の `.gitignore`） |
| Working on projects — uv | https://docs.astral.sh/uv/guides/projects/ （2026-11-08 確認。`uv.lock` をコミットし、手で直さないこと） |
| Locking and syncing — uv | https://docs.astral.sh/uv/concepts/projects/sync/ （2026-11-08 確認。editable、exact、`--no-dev`、ビルドの設定が無いと入らないこと） |
| Configuring projects — uv | https://docs.astral.sh/uv/concepts/projects/config/ （2026-11-08 確認。`--no-editable` の用途） |
| Managing dependencies — uv | https://docs.astral.sh/uv/concepts/projects/dependencies/ （2026-11-08 確認。`dev` グループが `uv run` / `uv sync` で既定で入ること） |
| Caching — uv | https://docs.astral.sh/uv/concepts/cache/ （2026-11-08 確認。editable を入れ直す条件） |
| Using uv in GitHub Actions | https://docs.astral.sh/uv/guides/integration/github/ （2026-11-08 確認。`python-version-file: ".python-version"`） |
| uv のソース（0.13.7） | https://github.com/astral-sh/uv/blob/0.13.7/crates/uv-project-commands/src/init.rs と https://github.com/astral-sh/uv/blob/0.13.7/crates/uv-configuration/src/vcs.rs （2026-11-08 確認。git の管理下の判定、`.gitignore` の中身、既存の `.python-version` を書き換えないこと） |
| `uv help init`（0.13.7） | 手元の CLI のヘルプで確認（2026-11-08。`--vcs` の既定、`--author-from`、`--python` が `requires-python` を決めること） |
| src layout vs flat layout | https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ （2026-11-08 確認、Context7 `/pypa/packaging.python.org` 経由） |
| pyproject.toml specification | https://packaging.python.org/en/latest/specifications/pyproject-toml/ （2026-11-08 確認、Context7 経由。`[project.scripts]` と `console_scripts`） |
| Dependency Groups specification | https://packaging.python.org/en/latest/specifications/dependency-groups/ （2026-11-08 確認、Context7 経由） |
| PEP 621 | https://peps.python.org/pep-0621/ （2026-11-08 確認。Final。"This PEP is a historical document." とあり、現行の仕様は PyPA の specs にある） |
| PEP 735 | https://peps.python.org/pep-0735/ （2026-11-08 確認。Final） |
| PEP 8 — Imports | https://peps.python.org/pep-0008/#imports （2026-11-08 確認） |
| Python docs（`__main__`・`site`・import 文） | https://docs.python.org/3/library/__main__.html ・ https://docs.python.org/3/library/site.html ・ https://docs.python.org/3/reference/simple_stmts.html#the-import-statement （2026-11-08 確認。`__main__.py` の書き方、`.pth` の各行を `sys.path` に足すこと、`__all__`） |
| Distributing type information — typing spec | https://typing.python.org/en/latest/spec/distributing.html#library-interface-public-and-private-symbols （2026-11-08 確認。`__all__` と公開の API） |
| Modules — Node.js docs | https://nodejs.org/api/modules.html#loading-from-node_modules-folders （2026-11-08 確認。`node_modules` を親へたどる探索） |
| npm / pnpm / Bun のコマンド | 手元の `npm install --help`（Node 26.13.0）・`pnpm install --help`（12.11.2）・`bun install --help` / `bun link --help`（1.4.4）で確認（2026-11-08） |

### 確認できなかった事項

- **完全に git の外のディレクトリでの `uv init`**。検証の作業場所が git リポジトリの中にあるため、`GIT_CEILING_DIRECTORIES` で親を探させないようにして再現した。uv の判定は `git rev-parse --is-inside-work-tree` の結果だけによる（ソースで確認）ので、結果は同じになるはずである

- 関連: [Python 学習ガイド](../README.md) / [Step 02: 文法の差分](02-language.md) / [Step 04: 型](04-typing.md) / [uv](../topics/uv.md) / [pyproject.toml](../topics/pyproject-toml.md) / [import の仕組み](../topics/imports.md) / [pip と venv](../topics/pip-venv.md)
