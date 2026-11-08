# Python 学習ガイド — Web 開発者のための入門とベストプラクティス（2026-11）

> 出典（一次情報）:
> - [Status of Python versions (devguide.python.org)](https://devguide.python.org/versions/) — 版ごとのサポート期間
> - [uv (docs.astral.sh)](https://docs.astral.sh/uv/) — 版・依存・実行・ツールを 1 つで扱うパッケージマネージャ
> - [uv 0.12.0 changelog (github.com)](https://github.com/astral-sh/uv/blob/main/changelogs/0.12.x.md) — `uv init` の既定が、パッケージ化された `src/` レイアウトになったこと
> - [Ruff v0.16.0 (astral.sh)](https://astral.sh/blog/ruff-v0.16.0) — 既定で有効なルールが 59 から 413 に増えたこと
> - [PEP 668 (peps.python.org)](https://peps.python.org/pep-0668/) — OS やパッケージマネージャが管理する Python に、pip で直接入れさせない仕組み
> - [Is setup.py deprecated? (packaging.python.org)](https://packaging.python.org/en/latest/discussions/setup-py-deprecated/) — `python setup.py` の直接実行が非推奨であること
> - [astral-sh/rye (github.com)](https://github.com/astral-sh/rye) — Rye の開発終了と uv への移行の案内
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7 で検証。最新版は 2026-11-08 に PyPI で取得）

JavaScript / TypeScript（Node.js・Bun）で Web 開発をしてきたエンジニアが、
**2026-11 時点の標準的な道具と書き方を、手を動かしながら順に身に付ける**ためのシリーズである。
ステップ編は 1 つの小さなアプリ（社内 FAQ）を育てながら読み進めるチュートリアル、トピック編は道具や仕組みを 1 つずつ引ける要約である。
コード例は手元の Mac で実行し、その出力を載せている（実行できなかったものは §9.2 のラベルで示す）。

LLM や機械学習のフレームワーク（PyTorch・Transformers・vLLM・LangGraph など）は [AI フレームワーク学習ガイド](../ai-frameworks/README.md) で扱う。本シリーズはその手前の土台にあたる。

---

## 1. TL;DR

- **道具は uv を中心にそろえる**。Python 本体の導入・版の固定・依存の管理・lockfile・実行・ツールの一度きりの実行まで、uv の 1 つのコマンドで済む（npm + nvm + npx を 1 つにした感覚。§3）。
- **新しく始めるなら Python 3.15 か 3.14**。どちらもバグ修正が続く期間にある。3.10 は 2026-10-01 にサポートが終わった。
- **既定の構成**: uv（依存）・Ruff（lint と format）・mypy か pyright（型チェック）・pytest（テスト）・Pydantic（実行時の検証。Zod にあたる）・FastAPI（Web API）。
- **Node / Bun との大きな違いは 3 つ**: ① ビルドが無く `.py` をそのまま実行する。型ヒントは実行時に検査されない ② 依存は `node_modules/` ではなくプロジェクトの `.venv/`（仮想環境）に入る ③ I/O は既定で同期で、非同期は `asyncio` を明示して使う。
- **ステップ編は 01 から順に読む**。応用（08〜11）は目的に合わせて選ぶ（§4）。道具を調べたいときはトピック編を引く（§5）。

---

## 2. Node.js / Bun との対応表

| 項目 | Node.js / Bun | Python（本シリーズの既定） | 詳しく |
|---|---|---|---|
| ランタイムの版を入れる・切り替える | nvm / fnm / Volta / mise | `uv python install 3.15` | [Python の版](topics/python-versions.md) |
| 版を固定するファイル | `.nvmrc` / `.node-version` | `.python-version` | [Step 01](steps/01-setup.md) |
| パッケージマネージャ | npm / pnpm / Bun | uv | [uv](topics/uv.md) |
| マニフェスト | `package.json` | `pyproject.toml` | [pyproject.toml](topics/pyproject-toml.md) |
| lockfile | `package-lock.json` / `pnpm-lock.yaml` / `bun.lock` | `uv.lock` | [uv](topics/uv.md) |
| 依存の置き場所 | `node_modules/` | `.venv/`（仮想環境）の `site-packages/` | [pip と venv](topics/pip-venv.md) |
| 開発用の依存 | `devDependencies` | `[dependency-groups]` の `dev` | [Step 03](steps/03-project.md) |
| コマンドを登録する | `package.json` の `bin` | `[project.scripts]` | [Step 03](steps/03-project.md) |
| タスクに名前を付ける | `package.json` の `scripts` | 該当なし（Makefile・just などを使う） | [uv](topics/uv.md) |
| ファイルを実行する | `node app.js` / `bun app.ts` | `uv run app.py` | [Step 01](steps/01-setup.md) |
| ツールを一度だけ動かす | `npx` / `bunx` | `uvx` | [uv](topics/uv.md) |
| モジュールの読み込み | `import` / `require`（`node_modules` を探す） | `import`（`sys.path` を探す） | [import の仕組み](topics/imports.md) |
| 型 | TypeScript（`tsc` で検査し、型を消して実行） | 型ヒント（型チェッカーで検査。実行時は無視される） | [Step 04](steps/04-typing.md) |
| 実行時の検証 | Zod | Pydantic | [Step 04](steps/04-typing.md) |
| lint / format | ESLint + Prettier / Biome | Ruff | Ruff（準備中） |
| テスト | Vitest / Jest / `bun test` | pytest | pytest（準備中） |
| Web API | Hono / Express / Fastify | FastAPI | Step 09（準備中） |
| モノレポ | npm / pnpm / Bun の workspaces | uv の workspace | [uv](topics/uv.md) |
| パッケージの公開先 | npm registry | PyPI | Step 11（準備中） |

---

## 3. 推奨構成（2026-11）

![uv を中心にした Python プロジェクトの全体図。左に開発者が書く pyproject.toml（依存の宣言）と .python-version（版の固定）、中央に uv、右に uv が作る uv.lock（解決した版の記録）と .venv（仮想環境。中に Python 本体へのリンクと site-packages）。uv は Python 本体を ~/.local/share/uv/python に入れ、uv run は .venv の中でコマンドを動かし、uvx はプロジェクトと切り離した使い捨ての環境でツールを動かす。uv.lock はコミットし、.venv はコミットしない。各要素に Node.js での相当（package.json・.nvmrc・package-lock.json・node_modules・npm exec・npx）が添えてある](../images/python/toolchain.png)

| 用途 | 既定 | 代替 | Node / Bun での相当 | 選ぶ理由 |
|---|---|---|---|---|
| Python 本体と版 | uv（`uv python`） | pyenv / mise / asdf / python.org のインストーラ | nvm / fnm / Volta | uv は既定で自分が入れた Python を優先し、`.python-version` で版をそろえる |
| 依存とプロジェクト | uv | Poetry / PDM / Hatch（Python 以外のバイナリも要るなら conda / pixi） | npm / pnpm / Bun | 版・依存・lockfile・実行・ツールを 1 つで扱う。`uv init` は src レイアウトとビルドの設定まで作る |
| ビルドバックエンド | `uv_build` | hatchling / setuptools | — | `uv init` の既定 |
| lint と format | Ruff | Black + Flake8 + isort | ESLint + Prettier / Biome | 1 つで両方を行う。0.16.0 から既定で 413 のルールを有効にする |
| 型チェック | mypy か pyright | basedpyright / ty（1.0 前）/ Pyrefly | `tsc --noEmit` | どちらも長く使われてきた安定版。手元の検証では、両方とも 4 つの誤りをすべて検出した（[Step 04](steps/04-typing.md)） |
| テスト | pytest | unittest（標準ライブラリ） | Vitest / Jest / `bun test` | 詳細は Step 06（準備中） |
| 実行時の検証 | Pydantic v2 | dataclasses / attrs / msgspec | Zod | 型ヒントから検証を作る。FastAPI も使う |
| CLI | Typer（小さなものは標準の argparse） | Click | commander / yargs | 詳細は Step 07（準備中） |
| Web API | FastAPI | Django（全部入り）/ Flask / Litestar | Hono / Express / Fastify | 型ヒントと Pydantic から、検証と OpenAPI を作る。詳細は Step 09（準備中） |
| データ処理 | Polars / DuckDB / pandas を用途で選ぶ | — | — | 使い分けは Step 10（準備中） |
| git の hook | pre-commit | prek | husky + lint-staged | 詳細は Step 05（準備中） |

道具の比較の詳細は、各トピック編（§5）に置く。

---

## 4. 学習ロードマップ

| # | ステップ | 学ぶこと | 通し課題で作るもの | Node での相当 |
|---|---|---|---|---|
| 01 | [環境構築](steps/01-setup.md) | uv の導入、Python の版、`uv run`・`uvx` | FAQ の件数を数える 1 ファイルのスクリプト | nvm + `node app.js` + `npx` |
| 02 | [文法の差分](steps/02-language.md) | JS / TS と違うところと罠 | カテゴリごとの件数 | — |
| 03 | [プロジェクト構成](steps/03-project.md) | `uv init`・`pyproject.toml`・src レイアウト・依存とロック | `faq` パッケージ（`uv run faq`） | `npm init` + `package.json` |
| 04 | [型](steps/04-typing.md) | 型ヒント・型チェッカー・Pydantic | 検証つきの `Faq` モデル | TypeScript + Zod |
| 05 | 品質ツール（準備中） | Ruff・型チェックの常時実行・pre-commit・エディタ | lint と型の設定 | ESLint + Prettier + husky |
| 06 | テスト（準備中） | pytest・fixture・parametrize・カバレッジ | 読み込みと検索のテスト | Vitest |
| 07 | スクリプトと CLI（準備中） | 単一ファイルのスクリプト・Typer・Rich・`uv tool install` | `faq search` / `faq stats` | commander + `npm -g` |
| 08 | 非同期と並行処理（準備中） | asyncio・TaskGroup・GIL と free-threaded 版 | 複数の取得を並行にする | Promise / イベントループ |
| 09 | Web API（準備中） | FastAPI・Pydantic・依存の注入・OpenAPI | FAQ 検索 API | Hono / Express |
| 10 | データ処理（準備中） | Polars・pandas・DuckDB・ノートブック | 問い合わせログの集計 | — |
| 11 | 配布とデプロイ（準備中） | wheel・PyPI・Docker・GitHub Actions・設定とログ | FAQ API の Docker イメージ | `npm publish` + Dockerfile |

- **基礎（01〜07）は順に読む**。04 までで「型付きのパッケージを作り、依存を管理する」ところまで進む
- **応用（08〜11）は目的に合わせて選ぶ**。API を作るなら 09 → 11、データを扱うなら 10 を先に読む
- 到達点: 型チェックとテストが通る FAQ の CLI と Web API を作り、Docker イメージにして配れる

---

## 5. トピック一覧（目的から引く）

| やりたいこと | トピック |
|---|---|
| どの版の Python を使うか決めたい・入れ方を比べたい | [Python の版](topics/python-versions.md) |
| uv のコマンドを npm / pnpm / Bun と対応づけて知りたい | [uv](topics/uv.md) |
| 既存の `requirements.txt` や `venv` の手順を読みたい・PEP 668 のエラーを直したい | [pip と venv](topics/pip-venv.md) |
| `pyproject.toml` の各項目と版の指定（`~=` など）を知りたい | [pyproject.toml](topics/pyproject-toml.md) |
| `import` がどこを探すか・`ModuleNotFoundError` を直したい | [import の仕組み](topics/imports.md) |
| Poetry や conda のプロジェクトに出会った・uv に移りたい | パッケージマネージャの比較（準備中） |
| lint と format の設定を決めたい | Ruff（準備中） |
| 型チェッカーを選びたい | 型チェッカーの比較（準備中） |
| テストの書き方を引きたい | pytest（準備中） |
| Zod の書き方を Pydantic に置き換えたい | Pydantic（準備中） |
| 用途ごとの定番ライブラリを知りたい | ライブラリ地図（準備中） |

---

## 6. ベストプラクティスの要約

| # | 推奨 | 根拠・詳しく |
|---|---|---|
| 1 | Python 本体は `uv python install` で入れ、`.python-version` で版を固定する | [Step 01](steps/01-setup.md) |
| 2 | 新しいプロジェクトは、バグ修正が続く版（2026-11 時点で 3.15 / 3.14）で始める | [Python の版](topics/python-versions.md) |
| 3 | プロジェクトは `uv init` で作り、依存は `uv add` で足す。`uv.lock` をコミットし、CI は `uv sync --locked` | [Step 03](steps/03-project.md) / [uv](topics/uv.md) |
| 4 | OS や Homebrew の Python に `pip install` しない（PEP 668 で拒否される）。仮想環境の中に入れる | [pip と venv](topics/pip-venv.md) |
| 5 | コードは `src/<パッケージ名>/` に置き、絶対 import で書く | [Step 03](steps/03-project.md) / [import の仕組み](topics/imports.md) |
| 6 | 関数の引数と戻り値に型ヒントを書き、型チェッカーで検査する。型ヒントは実行時に検査されないことを忘れない | [Step 04](steps/04-typing.md) |
| 7 | 外から来るデータ（JSON・設定・リクエスト）は Pydantic で検証してから使う | [Step 04](steps/04-typing.md) |
| 8 | ツールを一度だけ使うなら `uvx`、プロジェクトの依存を読む道具（pytest・型チェッカー）は dev 依存に入れて `uv run` | [Step 01](steps/01-setup.md) / [uv](topics/uv.md) |
| 9 | uv の experimental な機能（`uv audit`・`uv check`・`uv format`）は、CI の必須の検査に使わない | [uv](topics/uv.md) |
| 10 | lint と format は Ruff に任せ、型チェックとテストとあわせて CI で回す | Step 05（準備中） |

---

## 7. 新しく採用しないもの

| 名前 | 状態 | 代わり | 根拠 |
|---|---|---|---|
| Rye | 開発終了。リポジトリはアーカイブ済み。README: "Rye is no longer developed. We encourage all users to use uv" | uv | [astral-sh/rye](https://github.com/astral-sh/rye)（2026-11-08 確認） |
| `python setup.py install` などの直接実行 | 非推奨。"`python setup.py` and the use of `setup.py` as a command line tool are deprecated."（`setup.py` というファイル自体は非推奨ではない） | `uv build` / `uv add`（pip なら `python -m pip install .` と `python -m build`） | [packaging.python.org](https://packaging.python.org/en/latest/discussions/setup-py-deprecated/)（2026-11-08 確認） |
| OS や Homebrew の Python への `pip install` | PEP 668 により `externally-managed-environment` のエラーで拒否される | 仮想環境（uv のプロジェクト）に入れる。ツールは `uv tool install` | [PEP 668](https://peps.python.org/pep-0668/)（Final） |
| Python 3.10 以前で新しく始める | 3.10 は 2026-10-01 にサポートが終わった。macOS 付属の `/usr/bin/python3` は 3.9 | 3.15 / 3.14 | [Status of Python versions](https://devguide.python.org/versions/)（2026-11-08 確認） |

> **ポイント**: ここに載せるのは、開発元や標準化の文書が終了・非推奨を告げているものだけである。Poetry や pipenv のように、開発が続いていて既存のプロジェクトで出会うものは、パッケージマネージャの比較（準備中）で扱う。

---

## 8. 用語集

各ドキュメントは、一般的な用語の説明をここに任せている。「初出」は、その用語を詳しく扱うドキュメントである。

### 8.1 環境とパッケージ

| 用語 | 一言で | 初出 |
|---|---|---|
| CPython | Python の標準の実装（C で書かれている）。「Python 3.15」と言えば通常これを指す | [Python の版](topics/python-versions.md) |
| 仮想環境（venv） | プロジェクト専用の Python の環境。依存はここに入る。`node_modules/` にあたる | [pip と venv](topics/pip-venv.md) |
| site-packages | 仮想環境の中で、入れたパッケージが置かれるディレクトリ | [Step 03](steps/03-project.md) |
| PyPI | Python のパッケージの公開先（Python Package Index）。npm registry にあたる | [uv](topics/uv.md) |
| 配布パッケージと import パッケージ | PyPI に置かれる配布物（`pip install` する名前）と、コードから `import` する名前。一致しないこともある（例: `pip install pyyaml` → `import yaml`） | [import の仕組み](topics/imports.md) |
| モジュール / パッケージ | `.py` ファイル 1 つ / `__init__.py` を持つディレクトリ | [import の仕組み](topics/imports.md) |
| wheel / sdist | ビルド済みの配布物（`.whl`）/ ソースの配布物（`.tar.gz`） | Step 11（準備中） |
| ビルドバックエンド | `pyproject.toml` から wheel と sdist を作る道具（`uv_build`・hatchling・setuptools） | [pyproject.toml](topics/pyproject-toml.md) |
| lockfile | 解決した依存の版をすべて記録したファイル。uv は `uv.lock`、標準の形式は `pylock.toml`（PEP 751） | [uv](topics/uv.md) |
| editable install | プロジェクトのソースを、コピーせずに仮想環境から参照させる入れ方。`npm link` に近い | [Step 03](steps/03-project.md) |
| dependency groups / extras | 開発用など、配布物に含めない依存のまとまり（PEP 735）/ 利用者が選んで入れる追加の依存 | [pyproject.toml](topics/pyproject-toml.md) |
| PEP | Python Enhancement Proposal。言語や周辺の標準を決める文書。番号で呼ぶ（PEP 8 など） | [Step 02](steps/02-language.md) |

### 8.2 言語と型

| 用語 | 一言で | 初出 |
|---|---|---|
| dunder | `__init__` や `__name__` のような、前後に 2 つずつ `_` が付いた特別な名前（double underscore） | [Step 02](steps/02-language.md) |
| 内包表記 | `[x * 2 for x in xs if x > 0]` のように、リストなどを 1 つの式で作る書き方 | [Step 02](steps/02-language.md) |
| コンテキストマネージャ | `with` 文で使い、抜けるときに必ず後始末をするオブジェクト | [Step 02](steps/02-language.md) |
| ジェネレータ | `yield` で値を 1 つずつ返す関数 | [Step 02](steps/02-language.md) |
| デコレータ | `@dataclass` のように、関数やクラスに付けて振る舞いを足す仕組み | [Step 02](steps/02-language.md) |
| 型ヒント / 型チェッカー | 引数などに付ける型の注釈 / それを静的に検査する道具（mypy・pyright など）。実行時は注釈を検査しない | [Step 04](steps/04-typing.md) |
| `py.typed` | 「このパッケージは型ヒントを持つ」と型チェッカーに知らせる空のファイル（PEP 561） | [Step 04](steps/04-typing.md) |
| Protocol / TypedDict | 構造で互換を判定する型（TS の interface に近い）/ 辞書の形を表す型 | [Step 04](steps/04-typing.md) |

### 8.3 実行と並行処理

| 用語 | 一言で | 初出 |
|---|---|---|
| REPL | 対話モード。`uv run python` で入る | [Step 01](steps/01-setup.md) |
| GIL | 1 つのプロセスの中で、同時に 1 つのスレッドしか Python のコードを実行させない仕組み | [Python の版](topics/python-versions.md) |
| free-threaded 版 | GIL を外してビルドした CPython（`3.15t` のように `t` が付く） | [Python の版](topics/python-versions.md) |
| asyncio / イベントループ | 標準の非同期 I/O の仕組み。Node と違い、使うときに明示して起動する | Step 08（準備中） |
| ASGI / WSGI | Python の Web サーバーとアプリをつなぐ規格（非同期 / 同期） | Step 09（準備中） |

---

## 9. 検証環境と通し課題

### 9.1 検証環境

| 項目 | 内容 |
|---|---|
| マシン | Apple M2 Max / メモリ 96GB / macOS 27.2 |
| Python | 3.15.2（uv が管理するもの） |
| uv | 0.13.7 |
| Node.js / Bun / pnpm | 26.13.0 / 1.4.4 / 12.11.2（対応表のコマンドを確かめるため） |
| 各ドキュメント固有の版 | それぞれの冒頭の「最終更新」と本文に書く |

> **注意**: 検証では、手元の環境を汚さないように、uv が入れる Python とツールの置き場所を作業用のディレクトリに切り替えた（`UV_PYTHON_INSTALL_DIR` など）。また、手元のユーザー設定（`~/.config/uv/uv.toml`）を読まないようにして（`XDG_CONFIG_HOME` を空のディレクトリに向けた）、uv の既定の挙動を記録した。実行結果に出るパスは、既定の置き場所（`~/.local/share/uv/python` など）と、読者の作業ディレクトリ（`~/faq-app`）に読み替えて載せている。

### 9.2 コード例の状態ラベル

| ラベル | 意味 |
|---|---|
| （検証済み） | 手元で実行し、載せた「実行結果」はそのときの出力を写したもの。変えたのは §9.1 のパスの読み替えと `…（中略: N 行）…` の省略だけ。実行のログはリポジトリに含めない |
| （公式 docs 準拠・未実行: 理由） | アカウントが要るなど、手元で実行できないもの。公式 docs に沿って書いた |
| （抜粋・単体では動かない） | 説明のための部分的なコード |
| 参考値 | 速度などの数値。機種や状態で変わる |

### 9.3 通し課題

ステップ編では、架空の会社の「社内 FAQ」を共通の題材にする。データは AI フレームワーク学習ガイドと同じ 12 件の JSONL で、
[§7.4](../ai-frameworks/README.md#74-通し課題のデータ架空の社内-faq) を正本とする（保存の手順は [Step 01](steps/01-setup.md) の §3.4）。
1 ファイルのスクリプトから始め、型付きのパッケージ・テスト・CLI・Web API・Docker イメージへと育てる。同じデータを使うので、後で AI フレームワーク学習ガイドに進んだときも、題材をそのまま持ち込める。

---

## 10. このシリーズで扱わないもの

| 名前 | 扱わない理由 |
|---|---|
| AI・機械学習のフレームワーク | [AI フレームワーク学習ガイド](../ai-frameworks/README.md) で扱う |
| GUI（Tkinter・Qt など） | Web 開発者の業務で出会う場面が少ないため |
| C 拡張・Rust 拡張（PyO3・maturin） | 入門の範囲を超えるため |
| Django の詳しい使い方 | Web API は FastAPI を中心にし、Django は比較だけにとどめる |
| Windows 固有の手順 | 検証環境が macOS のため |

---

## 出典

| 情報源 | URL |
|---|---|
| Status of Python versions | https://devguide.python.org/versions/ （2026-11-08 確認） |
| uv — docs | https://docs.astral.sh/uv/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由） |
| uv 0.12.x changelog | https://github.com/astral-sh/uv/blob/main/changelogs/0.12.x.md （2026-11-08 確認） |
| Ruff v0.16.0 | https://astral.sh/blog/ruff-v0.16.0 （2026-11-08 確認。2026-07-23 公開） |
| PEP 668 | https://peps.python.org/pep-0668/ （2026-11-08 確認） |
| Is setup.py deprecated? | https://packaging.python.org/en/latest/discussions/setup-py-deprecated/ （2026-11-08 確認） |
| astral-sh/rye | https://github.com/astral-sh/rye （2026-11-08 確認。README の告知、アーカイブ済み） |
| 各パッケージの最新版 | PyPI の JSON API（2026-11-08 取得） |

### 確認できなかった事項

- **道具ごとの利用者の割合**。公式の統計で比べられるものが無いため、「どれが多く使われているか」は選ぶ理由にしていない。選ぶ理由は、公式 docs に書かれた機能と、手元での検証結果に限った

- 関連: [AI フレームワーク学習ガイド](../ai-frameworks/README.md) / [使用ツールスタック](../tool-stack.md) / [Zed エディタガイド](../zed.md)
