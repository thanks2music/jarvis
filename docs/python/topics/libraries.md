# ライブラリ地図 — 用途から引く定番と、2026-11 時点の状態

> 出典（一次情報）:
> - [PyPI JSON API](https://docs.pypi.org/api/json/) — 各パッケージの最新版・公開日・`requires_python`
> - [GitHub REST API — Repositories / Commits](https://docs.github.com/en/rest/repos/repos) — アーカイブの有無・既定ブランチの最新コミット
> - 各プロジェクトの README と公式の告知（Material for MkDocs・Zensical・arq・HTTPX2・Starlette の release notes・psycopg の docs）
> - [The Python Standard Library — logging / zoneinfo (docs.python.org)](https://docs.python.org/3/library/)
>
> 最終更新: 2026-11-09（Python 3.15.2・uv 0.13.7 で検証。版と状態は 2026-11-09 に PyPI と GitHub の API で取得）

npm で「用途ごとの定番パッケージ」を探すのと同じことを、Python で引くための表である。各行に、このガイドでの既定・代替・npm での相当・最新版と保守の状態を並べる。
既定はこのガイドのステップ編で使うものに合わせた（[索引の推奨構成](../README.md#3-推奨構成2026-11)）。版と状態は**取得した日の事実**で、選び方の評価は書かない。

---

## 1. TL;DR

- **既定**: HTTP は HTTPX2、Web API は FastAPI（サーバーは uvicorn）、CLI は Typer、検証は Pydantic、DB は SQLAlchemy 2.1、データは Polars / DuckDB / pandas、テストは pytest（§2）。
- **httpx は 0.28.1（2024-12-06）から新しいリリースが無い**。Pydantic が fork を `httpx2` の名前で引き継ぎ、Starlette 1.10.0 の `TestClient` は `httpx` を使うと `StarletteDeprecationWarning` を出す（検証済み、§4.1）。
- **Material for MkDocs は 2027-05-05 に end of life**。同じチームの後継が Zensical（0.1.0、2026-11-05）である（§4.2）。
- **arq は保守だけのモード**（README の告知、§4.3）。
- 表のうち 14 パッケージと標準の zoneinfo を Python 3.15.2 で `uv run --with` して、入って動くことを確かめた（§3.2）。

---

## 2. Node.js / Bun との対応

「既定」はこのガイドで使うもの。`—` はこのガイドで既定を決めていない用途である。

| 用途 | 既定 | 代替 | npm での相当 | 扱うページ |
|---|---|---|---|---|
| HTTP クライアント | HTTPX2 | httpx / requests（同期のみ）/ aiohttp / niquests | `fetch` / undici / axios / ky | [Step 08](../steps/08-async.md) |
| Web フレームワーク | FastAPI | Django / Flask / Litestar | Hono / Express / Fastify | [Step 09](../steps/09-web-api.md) |
| ASGI サーバー | uvicorn（`fastapi[standard]` に入る） | granian | `node:http` / `@hono/node-server` | [Step 09](../steps/09-web-api.md)・[Step 11](../steps/11-deploy.md) |
| CLI | Typer | Click / 標準の argparse。出力の装飾は Rich、TUI は Textual | commander / yargs / chalk / Ink | [Step 07](../steps/07-cli.md) |
| 実行時の検証 | Pydantic | msgspec / attrs / 標準の dataclasses | Zod / Valibot | [Pydantic](pydantic.md) |
| DB・ORM | SQLAlchemy 2.1 | SQLModel。マイグレーションは Alembic。PostgreSQL のドライバは psycopg 3 / asyncpg | Drizzle / Prisma / Kysely・drizzle-kit・pg | — |
| データ処理 | Polars / DuckDB / pandas を用途で選ぶ | NumPy（配列計算の土台） | — | [Step 10](../steps/10-data.md) |
| ログ | 標準の logging | structlog / loguru | pino / winston | [Step 11](../steps/11-deploy.md) |
| 設定 | pydantic-settings | python-dotenv | dotenv + Zod / `node --env-file` | [Pydantic](pydantic.md) §3.5 |
| 日時 | 標準の datetime + zoneinfo | whenever / pendulum | Temporal / date-fns / Luxon | — |
| テスト | pytest | Hypothesis（プロパティベース）/ respx（httpx のモック）/ pytest-cov | Vitest / fast-check / msw / `vitest --coverage` | [Step 06](../steps/06-testing.md)・[pytest](pytest.md) |
| タスクキュー | — | Celery / Dramatiq / arq / taskiq | BullMQ | — |
| ドキュメント | — | Zensical / Sphinx / mkdocs-material | VitePress / Docusaurus | — |
| ノートブック | marimo | JupyterLab | — | [Step 10](../steps/10-data.md) |
| ひな形 | `uv init` | `django-admin startproject` / `zensical new` / Copier / Cookiecutter | `npm init` / `bun init` / `create-*` | [uv](uv.md) |

---

## 3. 早見表（版・状態・動作確認）

### 3.1 最新版と保守の状態

最新版と公開日は PyPI の JSON API、最終コミットは GitHub の既定ブランチの最新コミットの日付（どちらも 2026-11-09 取得）。GitHub でアーカイブされたリポジトリは 1 つも無かった。「3.15」の列は §3.2 で Python 3.15.2 に入れて動かしたもの。

| 用途 | パッケージ | 最新版（公開日） | 最終コミット | `requires_python` | 3.15 | 状態の注記 |
|---|---|---|---|---|---|---|
| HTTP | httpx | 0.28.1（2024-12-06） | 2026-02-23 | >=3.8 | ✅ | §4.1 |
| HTTP | httpx2 | 2.16.0（2026-10-21） | 2026-11-07 | >=3.11 | ✅ | Pydantic が管理（§4.1） |
| HTTP | requests | 2.34.2（2026-05-14） | 2026-10-26 | >=3.10 | | |
| HTTP | aiohttp | 3.14.5（2026-10-11） | 2026-11-07 | >=3.10 | | |
| HTTP | niquests | 3.21.2（2026-09-23） | 2026-09-23 | >=3.7 | | README: requests の fork |
| Web | fastapi | 0.162.2（2026-11-07） | 2026-11-07 | >=3.10 | | |
| Web | django | 6.1.3（2026-11-03） | 2026-11-06 | >=3.12 | ✅ | |
| Web | flask | 3.1.3（2026-02-19） | 2026-10-30 | >=3.9 | | |
| Web | litestar | 2.25.0（2026-10-18） | 2026-11-08 | >=3.8,<4.0 | | |
| ASGI | uvicorn | 0.54.0（2026-09-25） | 2026-11-01 | >=3.10 | | リポジトリは `Kludex/uvicorn`（`encode/uvicorn` から転送される） |
| ASGI | granian | 2.8.7（2026-10-28） | 2026-11-04 | >=3.10 | ✅ | |
| CLI | typer | 0.28.0（2026-11-06） | 2026-11-07 | >=3.10 | | |
| CLI | click | 8.5.1（2026-11-06） | 2026-11-06 | >=3.10 | | |
| CLI | rich | 15.0.0（2026-04-12） | 2026-11-07 | >=3.9.0 | | |
| CLI | textual | 8.2.8（2026-06-30） | 2026-10-09 | >=3.9,<4.0 | | |
| 検証 | pydantic | 2.14.3（2026-11-05） | 2026-11-08 | >=3.10 | | |
| 検証 | msgspec | 0.22.0（2026-09-29） | 2026-11-08 | >=3.10 | ✅ | リポジトリは `msgspec/msgspec`（`jcrist/msgspec` から転送される） |
| 検証 | attrs | 26.1.0（2026-03-19） | 2026-11-02 | >=3.9 | | |
| DB | sqlalchemy | 2.1.8（2026-11-04） | 2026-11-08 | >=3.11 | ✅ | |
| DB | sqlmodel | 0.0.48（2026-10-06） | 2026-11-07 | >=3.10 | | |
| DB | alembic | 1.20.1（2026-10-22） | 2026-10-27 | >=3.10 | | |
| DB | psycopg | 3.3.8（2026-11-04） | 2026-11-08 | >=3.10 | ✅ | `[binary]` で検証（§5） |
| DB | asyncpg | 0.32.0（2026-10-06） | 2026-10-08 | >=3.9.0 | | |
| データ | polars | 2.1.0（2026-10-25） | 2026-11-08 | >=3.11 | ✅ | |
| データ | pandas | 3.1.1（2026-11-04） | 2026-11-08 | >=3.11 | ✅ | |
| データ | duckdb | 2.0.0（2026-10-21） | 2026-11-06 | >=3.11.0 | ✅ | |
| データ | numpy | 2.5.4（2026-10-10） | 2026-11-07 | >=3.12 | ✅ | |
| ログ | structlog | 26.1.0（2026-06-06） | 2026-11-02 | >=3.10 | ✅ | |
| ログ | loguru | 0.7.3（2024-12-06） | 2026-11-06 | >=3.5,<4.0 | | 最新リリースは 2024-12 |
| 設定 | pydantic-settings | 2.16.2（2026-10-28） | 2026-11-06 | >=3.11 | | |
| 設定 | python-dotenv | 1.2.4（2026-10-01） | 2026-10-28 | >=3.10 | | |
| 日時 | whenever | 0.11.0（2026-10-02） | 2026-11-07 | >=3.10 | ✅ | |
| 日時 | pendulum | 3.3.0（2026-10-12） | 2026-10-12 | >=3.10 | | |
| テスト | pytest | 9.2.0（2026-10-27） | 2026-11-08 | >=3.10 | | |
| テスト | hypothesis | 6.170.15（2026-11-06） | 2026-11-06 | >=3.11 | | |
| テスト | respx | 0.23.1（2026-04-08） | 2026-04-23 | >=3.8 | | 依存は `httpx>=0.25.0`（§4.1） |
| テスト | pytest-cov | 7.1.0（2026-03-21） | 2026-10-18 | >=3.9 | | |
| キュー | celery | 5.7.0（2026-11-05） | 2026-11-08 | >=3.10 | | |
| キュー | dramatiq | 2.2.1（2026-09-02） | 2026-11-04 | >=3.10 | | |
| キュー | arq | 0.28.0（2026-04-16） | 2026-04-16 | >=3.9 | | 保守だけのモード（§4.3） |
| キュー | taskiq | 0.13.0（2026-09-26） | 2026-11-07 | >=3.10,<4 | | |
| 文書 | mkdocs-material | 9.8.1（2026-11-07） | 2026-11-07 | >=3.11 | | 2027-05-05 に EOL（§4.2） |
| 文書 | zensical | 0.1.0（2026-11-05） | 2026-11-06 | >=3.11 | ✅ | §4.2 |
| 文書 | mkdocs（本体） | 1.6.1（2024-08-30） | 2025-10-20 | >=3.8 | | |
| 文書 | sphinx | 9.2.0（2026-10-21） | 2026-10-29 | >=3.13 | | |
| ノート | jupyterlab | 4.6.6（2026-11-06） | 2026-11-06 | >=3.10 | | |
| ノート | marimo | 0.25.2（2026-10-19） | 2026-11-08 | >=3.10 | | |
| ひな形 | copier | 9.19.1（2026-10-13） | 2026-11-06 | >=3.10 | | |
| ひな形 | cookiecutter | 2.7.1（2026-03-04） | 2026-03-04 | >=3.10 | | |

`requires_python` の下限に注意する。Django 6.1 は 3.12 以上、Sphinx 9.2 は 3.13 以上を求める。

### 3.2 Python 3.15.2 で動かす（代表の 1 行）

プロジェクトを作らずに、版を固定して試す（検証済み。作業ディレクトリの `.python-version` は `3.15`）。

```bash
uv run python --version
uv run --with polars==2.1.0 python -c "import polars as pl; print(pl.DataFrame({'cat': ['a', 'b', 'a'], 'n': [1, 2, 3]}).group_by('cat').agg(pl.col('n').sum()).sort('cat'))"
```

実行結果:

```text
$ uv run python --version
Python 3.15.2
$ uv run --with polars==2.1.0 python -c "import polars as pl; print(pl.DataFrame({'cat': ['a', 'b', 'a'], 'n': [1, 2, 3]}).group_by('cat').agg(pl.col('n').sum()).sort('cat'))"
Installed 2 packages in 11ms
shape: (2, 2)
┌─────┬─────┐
│ cat ┆ n   │
│ --- ┆ --- │
│ str ┆ i64 │
╞═════╪═════╡
│ a   ┆ 4   │
│ b   ┆ 2   │
└─────┴─────┘
```

ほかの 1 行と出力（すべて検証済み。`Installed …` の行は省いた）:

| パッケージ | 1 行 | 出力 |
|---|---|---|
| httpx2 2.16.0 | `t = httpx2.MockTransport(lambda req: httpx2.Response(200, json={'path': req.url.path}))` → `httpx2.Client(transport=t).get('https://example.test/faqs').json()` | `3.15.2 2.16.0 {'path': '/faqs'}` |
| httpx 0.28.1 | 同じ内容を `httpx` で | `3.15.2 0.28.1 {'path': '/faqs'}` |
| duckdb 2.0.0 | `duckdb.sql('select 40 + 2 as answer').fetchall()` | `2.0.0 [(42,)]` |
| pandas 3.1.1 | `pd.DataFrame(...).groupby('cat')['n'].sum().to_dict()` | `{'a': 4, 'b': 2}`（numpy は 2.5.4 が入った） |
| msgspec 0.22.0 | `msgspec.json.decode(b'{"id": 1, "q": "hi"}', type=Faq)` | `Faq(id=1, q='hi')` |
| sqlalchemy 2.1.8 | `create_engine('sqlite://')` で `select(literal(42))` | `2.1.8 42` |
| 標準の zoneinfo | `datetime(2026, 11, 9, tzinfo=UTC).astimezone(ZoneInfo('Asia/Tokyo'))` | `2026-11-09 09:00:00+09:00` |
| whenever 0.11.0 | `Instant.from_utc(2026, 11, 9).to_tz('Asia/Tokyo')` | `2026-11-09T09:00:00+09:00[Asia/Tokyo]` |
| structlog 26.1.0 | `structlog.get_logger().info('faq_loaded', count=3)` | `2026-11-09 01:49:52 [info     ] faq_loaded                     count=3` |
| psycopg[binary] 3.3.8 | `psycopg.__version__, psycopg.pq.__impl__` | `3.3.8 binary` |
| granian 2.8.7 / django 6.1.3 | `granian --version` / `django-admin --version` | `granian 2.8.7` / `6.1.3` |
| zensical 0.1.0 | `zensical --help` | コマンドは `build`・`new`・`serve` |

上の表に無いもの（FastAPI・Typer・pytest など）は、各ステップ編で通し課題に入れて動かしている。

### 3.3 状態を自分で調べる

最新版と公開日は PyPI、アーカイブと最終コミットは GitHub で引く（検証済み。`gh` は認証済みのもの）。

```bash
curl -s https://pypi.org/pypi/httpx/json | jq -r '.info.version, .urls[0].upload_time'
gh api repos/encode/httpx --jq '.archived, .pushed_at'
gh api 'repos/encode/httpx/commits?per_page=1' --jq '.[0].commit.committer.date'
```

実行結果:

```text
$ curl -s https://pypi.org/pypi/httpx/json | jq -r '.info.version, .urls[0].upload_time'
0.28.1
2024-12-06T15:37:21
$ gh api repos/encode/httpx --jq '.archived, .pushed_at'
false
2026-10-02T12:53:43Z
$ gh api 'repos/encode/httpx/commits?per_page=1' --jq '.[0].commit.committer.date'
2026-02-23T10:40:42Z
```

`pushed_at`（2026-10-02）と既定ブランチの最新コミット（2026-02-23）は一致しない。2026-10-02 は `version-1.0` ブランチの最新コミットの日付だった（§5）。

---

## 4. 推奨の使い方（2026-11）

| 推奨 | 理由 |
|---|---|
| 使う前に、PyPI の最新版の日付・GitHub のアーカイブの有無・README の告知を見る | 保守の終了は README の告知だけで示されることがある（§4.2・§4.3） |
| 新しい 3.15 の環境では、まず `uv run --with <pkg>==<ver>` で入るか試す | `requires_python` の下限と wheel の有無は、パッケージごとに違う（§3.1） |
| 標準ライブラリで足りる用途（ログ・タイムゾーン・小さな CLI）は、まず標準を使う | 標準の logging の入口は `logging.getLogger(__name__)`。zoneinfo は "By default, zoneinfo uses the system's time zone data if available; if no system time zone data is available, the library will fall back to using the first-party tzdata package available on PyPI." |

### 4.1 httpx と HTTPX2

- **httpx**（`encode/httpx`）: 最新リリースは 0.28.1（2024-12-06）。それ以降リリースは無く、既定ブランチの最新コミットは 2026-02-23。アーカイブはされておらず、README に保守終了の告知は無い。PyPI の classifier は `Development Status :: 4 - Beta`
- **HTTPX2**（`pydantic/httpx2`、PyPI の `httpx2`）: 2.0.0 は 2026-05-12。README の原文: "With HTTPX itself seeing limited activity recently, Pydantic is picking up stewardship under the HTTPX2 name so that users have a reliably maintained path forward - including timely security updates for a library that sits in the critical path of so many production systems."
- 移行の docs の原文: "`httpx2` is a fork of `httpx 0.28.1`. It has the same public API." / "`httpx` and `httpx2` are different packages, with different import names. They don't conflict."。手順は依存の名前と `import httpx` を `httpx2` に置き換えるだけで、`import httpx2 as httpx` でもよい
- **Starlette**（FastAPI の土台）: 1.2.0（2026-05-28）の release notes に "Support httpx2 in the test client"。FastAPI 0.162.2 の `standard` extra は `httpx` と `httpx2` の両方に依存する
- **respx** 0.23.1 の依存は `httpx>=0.25.0` だけで、httpx2 への対応は PR（#334・#317）が open のまま（2026-11-09 時点）

Starlette 1.10.0 の `TestClient` を `httpx` で使うと警告が出る（検証済み）。

```bash
uv run --with starlette==1.10.0 --with httpx==0.28.1 python -c "import starlette.testclient"
uv run --with starlette==1.10.0 --with httpx2==2.16.0 python -c "import starlette.testclient; print('ok')"
```

実行結果:

```text
$ uv run --with starlette==1.10.0 --with httpx==0.28.1 python -c "import starlette.testclient"
Installed 7 packages in 7ms
<string>:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
$ uv run --with starlette==1.10.0 --with httpx2==2.16.0 python -c "import starlette.testclient; print('ok')"
Installed 7 packages in 9ms
ok
```

### 4.2 Material for MkDocs と Zensical

Material for MkDocs の README（2026-11-09 確認）の原文:

> "Material for MkDocs reaches end of life on May 5, 2027. Critical fixes and security updates continue until that date."
>
> "We're continuing our work with Zensical, a maintained successor built by the team behind Material for MkDocs."
>
> "You can evaluate Zensical alongside MkDocs using your existing `mkdocs.yml`."

Zensical の告知（What changed on November 5, 2026）の原文: "Material for MkDocs has received a six-month end-of-life extension, with critical maintenance continuing until May 5, 2027." / "Version 0.1.0 marks its transition out of the 0.0.x alpha series and begins a dependable release line. Zensical will remain on the 0.x release line while we shape its module system and ecosystem together with the community."
Zensical は MIT ライセンスで、移行は公式の migration guide（下の出典）にある。土台の mkdocs 本体は、最新リリースが 1.6.1（2024-08-30）、既定ブランチの最新コミットが 2025-10-20 である。

### 4.3 arq

README の原文: "**In maintenance only mode**: arq is in maintenance only mode, see #510."。Issue #510（2025-10-18）の原文: "We'll continue to fix critical security issues, and we won't archive this repo so you can comment and submit fixes, but don't expect work on new fixes."

### 4.4 ひな形（`uv init` ほか）

`uv init` には `--app`・`--lib`・`--package` / `--no-package`・`--script`・`--bare`・`--build-backend`・`--vcs`・`--no-readme` がある（uv 0.13.7 の `uv init --help` で確認）。既定と各オプションの違いは [uv](uv.md) にある。フレームワークの公式のひな形は、`django-admin startproject`（Django）、`zensical new`（Zensical）、`fastapi/full-stack-fastapi-template`（GitHub の "Use this template"）。Copier と Cookiecutter は汎用のテンプレートツールである。

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `import starlette.testclient` で `StarletteDeprecationWarning: Using \`httpx\` with \`starlette.testclient\` is deprecated; install \`httpx2\` instead.`（検証で再現） | Starlette 1.10.0 は `httpx2` を優先し、`httpx` での利用を非推奨にした | テスト用の依存を `httpx2` にする（§4.1） |
| `uv run --with psycopg==3.3.8` で `ImportError: no pq wrapper available.`（検証で再現。下のログ） | extra なしの psycopg は純 Python の実装だけで、libpq を探す。手元の Homebrew の libpq は keg-only（`/opt/homebrew` にリンクされない）で、見つからなかった | 開発では `psycopg[binary]`（docs: "The quickest way to start developing with Psycopg 3 is to install the binary packages"）。本番は docs が "the preferred way to install Psycopg for a production site" とする `psycopg[c]` |
| GitHub の `pushed_at` が新しいのに、既定ブランチは何か月も更新されていない（検証中に発生） | httpx では、`pushed_at` の日付が既定ブランチでなく `version-1.0` ブランチへのコミットの日付だった | 既定ブランチの `commits?per_page=1` の日付を見る（§3.3） |
| Python 3.11 の環境で Django 6.1 や Sphinx 9.2 が入らない | `requires_python` がそれぞれ >=3.12・>=3.13 | §3.1 の列を見て、Python を上げるか前の版を使う |

実行結果（psycopg を extra なしで入れたとき。検証で再現）:

```text
$ uv run --with psycopg==3.3.8 python -c "import psycopg"
Installed 1 package in 5ms
Traceback (most recent call last):
…（中略: 12 行）…
ImportError: no pq wrapper available.
Attempts made:
- couldn't import psycopg 'c' implementation: No module named 'psycopg_c'
- couldn't import psycopg 'binary' implementation: No module named 'psycopg_binary'
- couldn't import psycopg 'python' implementation: libpq library not found
```

---

## 出典

| 情報源 | URL（確認日） |
|---|---|
| PyPI JSON API（全パッケージの最新版・公開日・`requires_python`・classifier・依存） | https://pypi.org/pypi/<パッケージ名>/json （2026-11-09 取得） |
| GitHub REST API（アーカイブ・既定ブランチの最新コミット・説明文） | https://api.github.com/repos/<owner>/<repo> （2026-11-09 取得） |
| encode/httpx | https://github.com/encode/httpx （2026-11-09 確認） |
| pydantic/httpx2 — README / Migrating from HTTPX | https://github.com/pydantic/httpx2 ・ https://github.com/pydantic/httpx2/blob/main/docs/migration.md （2026-11-09 確認） |
| Starlette release notes / `testclient.py` | https://github.com/Kludex/starlette/blob/main/docs/release-notes.md （2026-11-09 確認） |
| FastAPI — Testing | https://fastapi.tiangolo.com/tutorial/testing/ （2026-11-09 確認） |
| lundberg/respx（PR #334・#317） | https://github.com/lundberg/respx/pull/334 （2026-11-09 確認） |
| squidfunk/mkdocs-material README | https://github.com/squidfunk/mkdocs-material （2026-11-09 確認） |
| Zensical — What changed on November 5, 2026 / migration guide | https://zensical.org/upcoming-changes/ ・ https://zensical.org/docs/compatibility/mkdocs/migration/ （2026-11-09 確認） |
| python-arq/arq README・Issue #510 | https://github.com/python-arq/arq ・ https://github.com/python-arq/arq/issues/510 （2026-11-09 確認） |
| psycopg 3 — Installation | https://www.psycopg.org/psycopg3/docs/basic/install.html （2026-11-09 確認） |
| zoneinfo / Logging HOWTO（Python docs） | https://docs.python.org/3/library/zoneinfo.html ・ https://docs.python.org/3/howto/logging.html （2026-11-09 確認） |
| whenever — README / examples | https://github.com/ariebovenberg/whenever （2026-11-09 確認、Context7 `/ariebovenberg/whenever` 経由） |
| fastapi/full-stack-fastapi-template | https://github.com/fastapi/full-stack-fastapi-template （2026-11-09 確認） |

### 確認できなかった事項

- **httpx の保守方針についての、`encode/httpx` 側の公式の告知**。README・docs サイト（python-httpx.org）には見つからなかった。HTTPX2 の README の "limited activity" は Pydantic 側の記述である
- **3.15 で動くかの確認は、§3.2 の 14 パッケージと zoneinfo だけ**。残りは `requires_python` が 3.15 を含むことしか確かめていない（wheel の有無は未確認）
- npm での相当は対応の目安で、機能が一対一で同じとは限らない

- 関連: [Python 学習ガイド](../README.md) / [Step 07: スクリプトと CLI](../steps/07-cli.md) / [Step 08: 非同期と並行処理](../steps/08-async.md) / [Step 09: Web API](../steps/09-web-api.md) / [Step 10: データ処理](../steps/10-data.md) / [Step 11: 配布とデプロイ](../steps/11-deploy.md) / [Pydantic](pydantic.md) / [pytest](pytest.md) / [uv](uv.md)
