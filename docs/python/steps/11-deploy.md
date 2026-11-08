# Step 11: 配布とデプロイ — wheel を作り、FAQ API をコンテナと CI に載せる

> 出典（一次情報）:
> - [Building and publishing a package (docs.astral.sh)](https://docs.astral.sh/uv/guides/package/) と [The uv build backend (docs.astral.sh)](https://docs.astral.sh/uv/concepts/build-backend/) — `uv build`・`uv publish`・Trusted Publishing・`uv_build` が配布物に入れるファイル
> - [Using uv in Docker (docs.astral.sh)](https://docs.astral.sh/uv/guides/integration/docker/) と [astral-sh/uv-docker-example (GitHub)](https://github.com/astral-sh/uv-docker-example) — multi-stage build・キャッシュ・中間層・non-root
> - [Using uv in GitHub Actions (docs.astral.sh)](https://docs.astral.sh/uv/guides/integration/github/) と [astral-sh/setup-uv (GitHub)](https://github.com/astral-sh/setup-uv) — CI と PyPI への公開
> - [Trusted Publishers (docs.pypi.org)](https://docs.pypi.org/trusted-publishers/) と [Using TestPyPI (packaging.python.org)](https://packaging.python.org/en/latest/guides/using-testpypi/)
> - [pydantic-settings (docs.pydantic.dev)](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) と [structlog — Logging Best Practices (structlog.org)](https://www.structlog.org/en/stable/logging-best-practices.html)
>
> 最終更新: 2026-11-09（Python 3.15.2・uv 0.13.7・Docker 29.9.2・pydantic-settings 2.16.2・structlog 26.1.0・actionlint 1.7.12 で検証）

Node.js では、ライブラリは `npm pack` で tarball にして `npm publish`、アプリは `node_modules` ごとコンテナに入れ、CI は `actions/setup-node` で `pnpm install --frozen-lockfile` から始める。
Python では、配布物が **wheel（ビルド済み）と sdist（ソース）の 2 種類**あり、`uv build` で両方を作る。アプリのコンテナには、uv が lockfile から作った**仮想環境（`.venv`）だけ**を入れる。
このステップでは、[Step 09](09-web-api.md) の FAQ API を wheel にし、PyPI への公開の手順を確かめ、設定とログを本番向けに整え、Docker のイメージと GitHub Actions の CI を作る。
前は [Step 10: データ処理](10-data.md)、全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **`uv build` で `dist/` に wheel（`.whl`）と sdist（`.tar.gz`）ができる**。wheel に入るのは `src/faq/` と `.dist-info` だけで、`data/` や `tests/` は入らない（§3.1）。
- **PyPI への公開は `uv publish`。GitHub Actions からは Trusted Publishing でトークンを置かずに公開できる**。まず `--dry-run` か TestPyPI で試す（§3.2）。
- **設定は pydantic-settings の `Settings` に集める**。`env_prefix="FAQ_"` で `FAQ_DATA` がそのまま `data` に入り、型で検証される（§3.3）。
- **コンテナのログは標準出力に 1 行 1 JSON**。structlog は端末かどうかで見た目と JSON を切り替えられる（§3.4）。
- **Dockerfile は uv の公式の形に合わせる**: uv の版を固定して `COPY --from`、依存と本体を別の層で `uv sync --locked`、`--no-editable` で `.venv` だけを最終イメージへ、non-root で動かす（§3.5・§3.6）。
- **CI は `astral-sh/setup-uv` をコミット SHA で固定する**。v8.0.0 から `@v10` のようなメジャーのタグは作られていない（§3.7・§5）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js / Bun | Python（uv） |
|---|---|---|
| 配布物を作る | `npm pack`（`.tgz` を 1 つ） | `uv build`（wheel と sdist の 2 つ） |
| 配布物に入るものを決める | `package.json` の `files`・`.npmignore` | ビルドバックエンド（`uv_build`）の規則と `[tool.uv.build-backend]` |
| 公開する | `npm publish`（`--provenance`） | `uv publish`（PEP 740 の attestation もアップロードできる） |
| CI からトークン無しで公開 | npm の Trusted Publishing（OIDC） | PyPI の Trusted Publishing（OIDC） |
| 環境変数を型付きで読む | Zod で `process.env` を `parse` | pydantic-settings の `BaseSettings` |
| 構造化ログ | pino | structlog（標準の `logging` は Formatter を自分で書く） |
| コンテナに入れるもの | `node_modules` と `dist/` | `.venv`（中にアプリも入る）とデータ |
| CI のセットアップ | `actions/setup-node` + `pnpm install --frozen-lockfile` | `astral-sh/setup-uv` + `uv sync --locked` |

---

## 3. ハンズオン

[Step 09](09-web-api.md) の `faq-app/` を使う。コンテナは**ポート 8010** で動かし、記録を取ったら止めて消した（イメージ `python-guide-faq-api` は残した）。

### 3.1 `uv build` で wheel と sdist を作る

**狙い**: 配布物に何が入るのかを、中身を開いて確かめる（検証済み）。

実行結果:

```text
$ uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/faq-0.1.0.tar.gz
Successfully built dist/faq-0.1.0-py3-none-any.whl
```

`Building wheel from source distribution...` のとおり、uv は先に sdist を作り、それを展開して wheel を作る。wheel は zip なので `unzip -l` で中身が見える（§3.3・§3.4 で足した `settings.py`・`logs.py` を含む最終版）。

実行結果:

```text
$ unzip -l dist/faq-0.1.0-py3-none-any.whl
…（中略: 3 行）…
        0  01-01-1980 00:00   faq/
…（中略: 12 行）…
        0  01-01-1980 00:00   faq-0.1.0.dist-info/
       80  01-01-1980 00:00   faq-0.1.0.dist-info/WHEEL
       37  01-01-1980 00:00   faq-0.1.0.dist-info/entry_points.txt
      545  01-01-1980 00:00   faq-0.1.0.dist-info/METADATA
     1111  01-01-1980 00:00   faq-0.1.0.dist-info/RECORD
---------                     -------
    11270                     18 files
```

| 中身 | 役割 | npm で言うと |
|---|---|---|
| `faq/`（中略した 12 行は `api.py`・`analytics.py`・`fetch.py`・`py.typed` など） | `src/faq/` がそのまま入る。`src/` は外れる | `dist/` |
| `WHEEL` | `Tag: py3-none-any`（純 Python で、どの OS・CPU でも動く） | — |
| `entry_points.txt` | `[project.scripts]` の `faq = faq.cli:app` | `bin` |
| `METADATA` | 名前・版・`Requires-Dist`（依存）・`Requires-Python` | `package.json` |
| `RECORD` | 全ファイルのハッシュ | — |

- **`data/faq.jsonl` と `tests/` は wheel にも sdist にも入らない**。uv の docs の規則では、wheel に入るのは `module-root`（既定 `src/`）の下のモジュール、`license-files`、`readme`（メタデータに入る）、`tool.uv.build-backend.data` の下だけである。データを配るなら `src/faq/` の下に置くか `data` の設定を使う。この API では、データはコンテナに別に入れる（§3.5）
- sdist（`tar -tzf`）には `PKG-INFO`・`README.md`・`src/faq/*` と、**`pyproject.toml` と `pyproject.toml.orig`** が入っていた。docs: "The `pyproject.toml`, rewritten using TOML 1.0-compatible syntax. The original file is also included as `pyproject.toml.orig`."
- `uv_build` は純 Python 専用である。docs: "The uv build backend currently **only supports pure Python code**."。C 拡張などを含むなら他のバックエンド（docs は hatchling を挙げる）を使う
- `uvx --from ./dist/faq-0.1.0-py3-none-any.whl faq stats --data data/faq.jsonl` で、wheel を使い捨ての環境に入れて動かせた（検証済み）

### 3.2 `uv publish` と Trusted Publishing

**狙い**: PyPI へ出す手順を知る。**実際の公開はしていない**（PyPI のアカウントとプロジェクトの登録が要るため）。`--dry-run` だけ TestPyPI に向けて動かした（検証済み。認証情報なしで通った）。

実行結果:

```text
$ uv publish --dry-run --publish-url https://test.pypi.org/legacy/
Checking 2 files against https://test.pypi.org/legacy/
Checking faq-0.1.0-py3-none-any.whl (7.9KiB)
Checking faq-0.1.0.tar.gz (5.7KiB)
```

認証は、手元からなら API トークン（`--token` / `UV_PUBLISH_TOKEN`）、CI からなら Trusted Publishing（何も指定しない。`--trusted-publishing` の既定は `automatic`）である。

- uv の docs: "For publishing to PyPI from GitHub Actions or another Trusted Publisher, you don't need to set any credentials."。PyPI のプロジェクト設定の "Publishing" に、リポジトリ・ワークフローのファイル名・environment 名を登録する
- 仕組み（PyPI の docs）: CI が発行する OIDC トークンを PyPI が検証し、**15 分だけ有効な**プロジェクト用の API トークンを発行する。長く有効なトークンを CI の secret に置かずに済む。uv は公開の後、このトークンを無効にしようとする
- uv の docs のワークフローは `build` と `publish` を別のジョブに分け、`id-token: write` を `publish` だけに与える。原文: "This reduces the surface for supply chain attacks."
- **TestPyPI** は本番と別のデータベースを持つ練習用の PyPI で、アカウントも別に作る（PyPA の guide: "a separate instance of the Python Package Index (PyPI) that allows you to try out the distribution tools and process without worrying about affecting the real index."）。uv では `[[tool.uv.index]]` に `publish-url = "https://test.pypi.org/legacy/"` を書き、`uv publish --index testpypi` で出す
- 間違って公開したくないパッケージには、`classifiers` に `Private :: Do Not Upload` を入れておく。PyPA の guide: "PyPI will always reject packages with classifiers beginning with `Private ::`."
- `uv publish` は attestation（PEP 740）を見つければ一緒にアップロードするが、作りはしない。docs のワークフローは `astral-sh/attest-action` で作っている

### 3.3 設定を pydantic-settings にまとめる

**狙い**: `os.environ.get("FAQ_DATA", ...)` を、型と既定値を持つ設定クラスに置き換える。`src/faq/settings.py`（検証済み）。

```python
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FAQ_")

    data: Path = Path("data/faq.jsonl")  # 環境変数 FAQ_DATA で上書きできる
```

`api.py` の lifespan はこう変えた（抜粋・単体では動かない）。`import os` と `from pathlib import Path` は不要になった。

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    configure_logging()
    settings = Settings()  # ここで環境変数を読む
    faqs = load_faqs(settings.data)  # 起動時に 1 回だけ読む
    log.info("faqs_loaded", count=len(faqs), path=str(settings.data))
    yield {"faqs": faqs}
```

- `env_prefix="FAQ_"` で、フィールド `data` は環境変数 `FAQ_DATA` から読まれる。名前の大文字・小文字は既定で区別しない。Step 09 のテスト（`monkeypatch.setenv("FAQ_DATA", ...)`）は変えずに通った
- 値は `Path` に変換・検証される。Zod の `z.object({...}).parse(process.env)` を、クラスの宣言で書く形である。`tests/test_settings.py` に、既定値と環境変数の 2 本のテストを足した
- `uv add pydantic-settings structlog` で `+` と出たのは `structlog==26.1.0` だけだった。pydantic-settings は `fastapi[standard]` が既に入れている（[Step 09](09-web-api.md) §3.1）。それでも、自分のコードで import するものは直接の依存として `pyproject.toml` に書く

### 3.4 ログ: 標準の `logging` と structlog

**狙い**: コンテナでは JSON、端末では読みやすい形でログを出す。`src/faq/logs.py`（検証済み。structlog の docs の例と同じ分岐）。

```python
import sys

import structlog
from structlog.typing import Processor


def configure_logging() -> None:
    processors: list[Processor] = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    if sys.stderr.isatty():  # 端末では読みやすい形
        processors.append(structlog.dev.ConsoleRenderer())
    else:  # コンテナや CI では 1 行 1 JSON
        processors += [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    structlog.configure(processors=processors)
```

同じ 1 行のログを、端末でない場合と、`script` で端末のふりをした場合で出した（検証済み。2 つ目は色の制御文字を `sed` で消した）。

実行結果:

```text
{"count": 12, "event": "hello", "level": "info", "timestamp": "2026-11-08T17:02:36.591666Z"}
2026-11-08T17:08:02.882574Z [info     ] hello                          count=12
```

| | 標準の `logging` | structlog 26.1.0 |
|---|---|---|
| 依存 | 不要 | 1 つ足す |
| JSON | `logging` のリファレンスに JSON 用の Formatter は無い。Logging Cookbook の "Implementing structured logging" のように自分で書く | `JSONRenderer()` を並べるだけ |
| 値の渡し方 | `logger.info("loaded %d", n)`（文字列に埋める） | `log.info("faqs_loaded", count=n)`（キーと値） |
| 他のライブラリのログ | Uvicorn などはこちらで出す | 標準の `logging` を経由させる設定もある（このステップでは使っていない） |

- structlog の docs の考え方: "A simple but powerful approach is to log to unbuffered standard out and let other tools take care of the rest."。ファイルへの書き出しやローテーションはアプリでしない
- **JSON になったのは自分のログだけである**。Uvicorn の起動やアクセスのログは標準の `logging` のテキストのまま出た（§3.6）。全部を JSON に揃えるなら、Uvicorn の `log_config` か structlog の標準 `logging` 連携を設定する（未検証）

### 3.5 Dockerfile（multi-stage）

**狙い**: uv の docs の推奨を全部入れ、最終イメージには uv もソースも入れない。`Dockerfile`（検証済み）。

> **ポイント**: このイメージには [Step 10](10-data.md) のデータ処理のライブラリも入るため、784MB になる（Step 09 の状態なら 232MB）。理由と分け方は §3.6 に書いた。

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.15-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# 依存だけを先に入れる（uv.lock と pyproject.toml が変わらなければ、この層はキャッシュが効く）
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# 次にプロジェクト本体を入れる
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.15-slim
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot
WORKDIR /app
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --chown=nonroot:nonroot data /app/data
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER nonroot
EXPOSE 8010
CMD ["fastapi", "run", "--entrypoint", "faq.api:app", "--port", "8010"]
```

`.dockerignore` には `.venv`・`dist`・`.*_cache`・`.hypothesis`・`__pycache__` を書いた。

| 書き方 | 理由（uv の docs） |
|---|---|
| `COPY --from=ghcr.io/astral-sh/uv:0.13.7` | uv の公式イメージから実行ファイルだけを写す。"it is best practice to pin to a specific uv version"。再現性が要るならタグより SHA256 のダイジェストで固定する |
| `UV_COMPILE_BYTECODE=1` | `.pyc` を作っておき、起動を速くする。"typically desirable for production images"（その分、ビルドの時間とサイズが増える） |
| `UV_LINK_MODE=copy` | キャッシュ（cache mount）と `.venv` が別のファイルシステムなので、リンクできないという警告を消す |
| `--mount=type=cache,target=/root/.cache/uv` | ビルドをまたいで uv のキャッシュを使い回す |
| `--no-install-project` → `COPY .` → `uv sync` | "Since the project changes frequently, but its dependencies are generally static, this can be a big time saver." |
| `--no-editable` | プロジェクトを `.venv` の `site-packages` に実体で入れる。"removing any dependency on the source code"。これで `.venv` だけを次の段へ写せる |
| `UV_NO_DEV=1` | dev グループ（pytest・mypy など）を入れない |
| `UV_PYTHON_DOWNLOADS=0` | uv に Python をダウンロードさせず、イメージの `/usr/local/bin/python` を使う。両方の段で同じパスになるよう、同じベースイメージにする |
| `.dockerignore` に `.venv` | "The project virtual environment is dependent on your local platform and should be created from scratch in the image."（手元の macOS の `.venv` は Linux で動かない） |
| `USER nonroot` | root で動かさない（uv-docker-example と同じ作り方） |

- docs の例は 1 回目の `uv sync` を `--frozen` で、`uv.lock` だけをマウントしている。uv-docker-example は `pyproject.toml` もマウントして `--locked` にしている。ここでは後者に合わせ、lockfile が古ければビルドの時点で失敗させる
- `fastapi run` に `--entrypoint` を渡したのは、最終イメージに `pyproject.toml`（`[tool.fastapi]`）を入れていないからである

### 3.6 イメージを作り、コンテナで動かす

**狙い**: ビルドしてサイズを見て、[Step 09](09-web-api.md) と同じ curl が通ることを確かめる。`docker build -t python-guide-faq-api .` の後、`docker run -d --rm --name python-guide-faq-api -p 8010:8010 python-guide-faq-api` で起動した（`--rm` なので、止めるとコンテナも消える）。

1 回目のビルドでは、依存の層で `Installed 68 packages in 565ms` と `Bytecode compiled 4458 files in 1.75s` が出た。サイズは次のとおり（参考値。`docker images` の DISK USAGE）。

実行結果:

```text
$ docker images python-guide-faq-api
IMAGE                         ID             DISK USAGE   CONTENT SIZE   EXTRA
python-guide-faq-api:latest   d3ee1fded0d0        784MB             0B
$ docker images python:3.15-slim
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.15-slim   eb4ebf8660b6        148MB             0B
```

ベースの 148MB に、`.venv` の層（`docker history` で 636MB）と `data/` が乗った。`.venv` の大半は、[Step 10](10-data.md) で足した Polars・pandas・DuckDB・PyArrow である。[Step 09](09-web-api.md) の状態（データ処理の依存なし）で同じ Dockerfile からビルドしたときは、イメージが 232MB、`.venv` の層が 83.8MB だった（検証済み）。API だけを配るイメージなら、データ処理の依存を `[project.optional-dependencies]`（extras）に分け、イメージでは入れない形にできる（公式 docs 準拠・未実行: 通し課題は 1 つのパッケージのままにするため）。curl とコンテナの中を確かめ、最後に `docker stop` で止めた（検証済み）。

実行結果:

```text
$ curl -s "http://127.0.0.1:8010/faqs?category=IT" | jq -c ".[] | [.id, .question]"
["faq-05","社内 VPN につながりません。"]
["faq-06","パスワードを忘れました。"]
["faq-07","新しい PC のセットアップは誰がしますか？"]
$ docker exec python-guide-faq-api id
uid=999(nonroot) gid=999(nonroot) groups=999(nonroot)
$ docker exec python-guide-faq-api ls /app
data
$ docker exec python-guide-faq-api sh -c "command -v uv || echo no uv"
no uv
```

`/faqs/faq-06`・`/search?q=パスワード`・`/faqs/faq-99`（404）も Step 09 と同じ応答だった。`/app` には `data` しか無く、アプリは `.venv` の `site-packages` に入っている。ログはこう出た（検証済み）。

実行結果:

```text
$ docker logs python-guide-faq-api
…（中略: 10 行）…
INFO:     Started server process [1]
INFO:     Waiting for application startup.
{"count": 12, "path": "data/faq.jsonl", "event": "faqs_loaded", "level": "info", "timestamp": "2026-11-08T17:10:11.156646Z"}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8010 (Press CTRL+C to quit)
INFO:     192.168.65.1:36483 - "GET /faqs/faq-06 HTTP/1.1" 200 OK
…（中略: 2 行）…
```

- `docker run` に `-t` を付けていないので、`isatty()` が偽になり JSON で出た
- JSON の行と `Application startup complete.` の順序は、実行ごとに入れ替わった（取り直した上の記録では前、最初の記録では後）。**出し先が違うから**である。structlog とアクセスのログは標準出力、Uvicorn の起動のログは標準エラーに出ていた（`docker logs ... 2>/dev/null` で前者だけが残った）。`docker logs -t` の時刻では、両者の差は 11 マイクロ秒だった

ソースだけを変えて 2 回目をビルドすると、依存の層はキャッシュから使われた（検証済み。README.md に 1 行足して再ビルドし、元に戻した）。

実行結果:

```text
$ docker build --progress=plain -t python-guide-faq-api .
…（中略: 38 行）…
#12 [builder 4/6] RUN --mount=type=cache,target=/root/.cache/uv     --mount=type=bind,source=uv.lock,target=uv.lock     --mount=type=bind,source=pyproject.toml,target=pyproject.toml     uv sync --locked --no-install-project --no-editable
#12 CACHED

#13 [builder 5/6] COPY . /app
#13 DONE 0.0s

#14 [builder 6/6] RUN --mount=type=cache,target=/root/.cache/uv     uv sync --locked --no-editable
…（中略: 4 行）…
#14 0.095 Installed 1 package in 1ms
…（中略: 24 行）…
```

### 3.7 GitHub Actions の CI

**狙い**: Step 05〜07 の検査とビルドを CI で回す。`.github/workflows/ci.yml` の前半（actionlint で検証済み・**GitHub 上では未実行**: このコピーは GitHub のリポジトリではないため）。

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          version: "0.13.7"
      - run: uv sync --locked # .python-version の 3.15 を uv が入れる
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run mypy
      - run: uv run pytest -q
```

後半の `build` ジョブ（同上）。PyPI に出すなら、§3.2 のとおり別の `publish` ジョブを足す。

```yaml
  build:
    needs: check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          version: "0.13.7"
      - run: uv build
      - run: uv run --isolated --no-project --with dist/*.whl python -c "import faq.api"
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: dist
          path: dist/
```

- `actionlint .github/workflows/ci.yml`（actionlint 1.7.12）は何も出さずに終了コード 0 で終わった。CI の各コマンドは手元で同じものを回して通した（§3.8。`build` の 2 行目は `print(faq.api.app.title)` を足して `社内 FAQ API` と出た）
- setup-uv の最新は v10.3.3（2026-10-28）。README の例と同じく、**コミット SHA で固定し、版はコメントに書く**。v8.0.0 のリリースノート: "To increase **security** even more we will **stop publishing minor tags**. You won't be able to use `@v8` or `@v8.0` any longer."（§5）
- `version: "0.13.7"` で uv の版を固定する（uv の docs: "It is considered best practice to pin to a specific uv version"）。Python は `.python-version` を見て uv が入れる
- キャッシュは setup-uv の既定 `enable-cache: auto`（GitHub が用意する runner では有効。v10.0.0 から `pull_request_target`・`workflow_run`・`release` では無効）に任せた

### 3.8 検査を回す

Step 05〜07 の検査をまとめて回した（検証済み）。27 本だったテストが 29 本になった。

実行結果:

```text
$ uv run ruff check && uv run ruff format --check && uv run mypy && uv run pytest -q
All checks passed!
27 files already formatted
Success: no issues found in 19 source files
.............................                                            [100%]
29 passed in 2.92s
```

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| 公開の前に `uv build` の wheel を `unzip -l` で見て、使い捨ての環境で import する | 手元の editable install で動いたことを根拠にする | wheel に入らないファイル（`data/` など）は editable では見えない。docs のワークフローも sdist と wheel の smoke test を推奨している |
| CI からの公開は Trusted Publishing。ビルドと公開のジョブを分ける | 長く有効な API トークンを secret に置く | PyPI の docs: 発行されるトークンは 15 分で失効する。uv の docs: "This reduces the surface for supply chain attacks." |
| 初めての公開は `--dry-run` と TestPyPI で試す | いきなり本番の PyPI に出す | TestPyPI は "without worrying about affecting the real index"（PyPA の guide）で手順を試せる |
| 設定は `BaseSettings` のクラスにまとめ、lifespan の中で作る | `os.environ.get` をあちこちに書く | 型の変換と検証、既定値、テストでの差し替えが 1 か所で済む |
| コンテナでは標準出力に 1 行 1 JSON | アプリの中でファイルに書いてローテーションする | structlog の docs: "log to unbuffered standard out and let other tools take care of the rest." |
| uv は `ghcr.io/astral-sh/uv:<版>` から `COPY --from` で入れ、版を固定する | `:latest` や `pip install uv` | docs: "it is best practice to pin to a specific uv version" |
| 依存と本体を別の層にし、`--locked` で入れる | `COPY . .` の直後に `uv sync` 1 回 | ソースを変えるたびに全依存を入れ直すことになる（§3.6 で依存の層が `CACHED` になった） |
| multi-stage では `--no-editable` で入れ、`.venv` だけを写す | editable のまま `.venv` だけを写す | `.pth` が `/app/src` を指したままになり、起動できない（§5） |
| `.dockerignore` に `.venv` を書く | 手元の `.venv` をビルドの文脈に入れる | docs: 仮想環境は "dependent on your local platform" |
| GitHub Actions はコミット SHA で固定し、版をコメントに書く | `astral-sh/setup-uv@v10` | v8.0.0 からメジャー・マイナーのタグは作られていない。SHA はタグの付け替えの影響を受けない |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 最終イメージが `In /app/.venv/lib/python3.15/site-packages/faq.pth: /app/src does not exist; skipping sys.path append` の後に `ModuleNotFoundError: No module named 'faq'` で落ちる（検証で再現。`--no-editable` を外してビルド） | 既定の editable install では、`.venv` にはソースの場所（`/app/src`）を指す `.pth` しか無い。multi-stage で `.venv` だけを写すとソースが無い | 両方の `uv sync` に `--no-editable` を付ける（§3.5） |
| コンテナが `FileNotFoundError: [Errno 2] No such file or directory: 'nope.jsonl'` → `ERROR:    Application startup failed. Exiting.` で終了コード 3（検証で再現。`docker run -e FAQ_DATA=nope.jsonl`） | データのパスが違う。データは wheel に入らないので、イメージに `COPY` しないと既定のパスでも同じになる | `COPY data /app/data` と `WORKDIR /app`。別の場所なら `-e FAQ_DATA=/絶対パス` |
| `astral-sh/setup-uv@v10` と書いても actionlint は何も言わない。だが `gh api repos/astral-sh/setup-uv/git/ref/tags/v10` は `Not Found (HTTP 404)`（検証で再現） | v8.0.0 からメジャーのタグを作っていない。actionlint は action のタグが実在するかまでは見ない | `@<コミット SHA> # v10.3.3` で固定する。SHA は `gh api repos/astral-sh/setup-uv/git/ref/tags/v10.3.3` で引ける |
| `docker logs` で、JSON のログと Uvicorn のログの順番が前後する（検証中に発生） | 標準出力と標準エラーは別の流れで、`docker logs` が混ぜて見せる | 順番は `timestamp` で見る。ログの収集側で両方を集める |
| Uvicorn のログだけ JSON にならない（検証中に発生） | structlog の設定は structlog のロガーにだけ効く。Uvicorn は標準の `logging` で出す | Uvicorn の `log_config` を設定するか、structlog の標準 `logging` 連携を使う（未検証） |

---

## 6. 次のステップ

- 通し課題（`faq-app`）は、型付きのモデル・テスト・CLI・Web API・配布物・コンテナ・CI まで揃った。全体の振り返りは [Python 学習ガイド](../README.md)、道具の側からは [uv](../topics/uv.md)・[pyproject.toml](../topics/pyproject-toml.md)・[Pydantic](../topics/pydantic.md)・[ライブラリ地図](../topics/libraries.md)

---

## 出典

| 情報源 | URL |
|---|---|
| uv — Building and publishing a package | https://docs.astral.sh/uv/guides/package/ （2026-11-09 確認、Context7 `/astral-sh/uv` とページの実物。`uv build` の出力先、`uv publish` の認証、Trusted Publishing、トークンの無効化、TestPyPI の `[[tool.uv.index]]`、再試行と `--check-url`、attestation） |
| uv — The uv build backend | https://docs.astral.sh/uv/concepts/build-backend/ （2026-11-09 確認。純 Python 専用、hatchling の案内、sdist と wheel に入るファイル、`pyproject.toml.orig`） |
| uv — Using uv in Docker | https://docs.astral.sh/uv/guides/integration/docker/ （2026-11-09 確認、Context7 `/astral-sh/uv` とページの実物。版の固定と SHA256、`.dockerignore`、`UV_COMPILE_BYTECODE`、cache mount と `UV_LINK_MODE`、中間層、`--no-editable`、`UV_PYTHON_DOWNLOADS`） |
| astral-sh/uv-docker-example | https://github.com/astral-sh/uv-docker-example （2026-11-09 確認。`Dockerfile`・`multistage.Dockerfile`・`.dockerignore`。non-root のユーザー、`pyproject.toml` もマウントした `--locked`、`PYTHONUNBUFFERED`） |
| uv — Using uv in GitHub Actions | https://docs.astral.sh/uv/guides/integration/github/ （2026-11-09 確認。uv の版の固定、`uv sync --locked`、キャッシュ、`build` と `publish` を分けたワークフロー） |
| astral-sh/setup-uv — README / Releases | https://github.com/astral-sh/setup-uv ・ https://github.com/astral-sh/setup-uv/releases （2026-11-09 確認。最新 v10.3.3、v8.0.0 でメジャー・マイナーのタグを廃止、v10.0.0 で `enable-cache: auto` が一部のイベントで無効） |
| PyPI — Trusted Publishers | https://docs.pypi.org/trusted-publishers/ （2026-11-09 確認、ソース https://github.com/pypi/warehouse/blob/main/docs/user/trusted-publishers/index.md 。OIDC、15 分で失効するトークン） |
| PyPA — Using TestPyPI / Writing your pyproject.toml | https://packaging.python.org/en/latest/guides/using-testpypi/ ・ https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ （2026-11-09 確認。TestPyPI の位置づけと別アカウント、`Private :: Do Not Upload`） |
| pydantic-settings | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ （2026-11-09 確認、Context7 `/pydantic/pydantic-settings`。`env_prefix`、大文字・小文字を区別しない既定） |
| structlog — Logging Best Practices / API | https://www.structlog.org/en/stable/logging-best-practices.html ・ https://www.structlog.org/en/stable/api.html （2026-11-09 確認、Context7 `/websites/structlog_en_stable`。`isatty()` での切り替え、標準出力への出力、`TimeStamper`） |
| Python — Logging Cookbook | https://docs.python.org/3.15/howto/logging-cookbook.html （2026-11-09 確認。"Implementing structured logging"） |
| actions/checkout・actions/upload-artifact — Releases | https://github.com/actions/checkout/releases ・ https://github.com/actions/upload-artifact/releases （2026-11-09 確認。v7.0.1・v7.0.2 とそのコミット SHA） |

### 確認できなかった事項

- **実際の PyPI・TestPyPI への公開と、Trusted Publishing の動作**は確かめていない（アカウントとプロジェクトの登録が要る）。`uv publish --dry-run` が認証なしで通ることだけを確かめた
- **`ci.yml` は GitHub 上で動かしていない**。actionlint の静的な検査と、同じコマンドを手元で回した結果だけである。runner での Python 3.15 の取得時間やキャッシュの効き方は分からない
- **Uvicorn のログを JSON に揃える設定**（`log_config`・structlog の標準 `logging` 連携）は試していない
- **イメージのサイズ（784MB。Step 09 の状態では 232MB）は参考値**である。Docker 29.9.2 の `docker images` の DISK USAGE で、ベースイメージの版や圧縮の有無で変わる。Alpine や distroless との比較はしていない
- **`UV_LINK_MODE=copy` を外したときの警告**と、`.dockerignore` に `.venv` を書かなかったときの失敗は再現していない
- **対応表の npm の Trusted Publishing・`--provenance`・pino** は、各 docs の原文で確かめていない（目安として載せた）

- 関連: [Python 学習ガイド](../README.md) / [Step 05: 品質ツール](05-quality.md) / [Step 06: テスト](06-testing.md) / [Step 07: スクリプトと CLI](07-cli.md) / [Step 09: Web API](09-web-api.md) / [uv](../topics/uv.md) / [pyproject.toml](../topics/pyproject-toml.md) / [Pydantic](../topics/pydantic.md) / [ライブラリ地図](../topics/libraries.md)
