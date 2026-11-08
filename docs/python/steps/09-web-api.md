# Step 09: Web API — FastAPI で FAQ を HTTP から引けるようにする

> 出典（一次情報）:
> - [FastAPI (fastapi.tiangolo.com)](https://fastapi.tiangolo.com/) — インストール（`fastapi[standard]`）・パスとクエリのパラメータ・Response Model・Dependencies・Lifespan Events・Testing・FastAPI CLI・Deployment
> - [Starlette — Lifespan (starlette.dev)](https://starlette.dev/lifespan/) — lifespan state（`yield` した辞書を `request.state` で受け取る）
> - [Granian (GitHub)](https://github.com/emmett-framework/granian) — Rust 製の HTTP サーバーの CLI
> - [Django](https://docs.djangoproject.com/en/6.1/) ・ [Flask](https://flask.palletsprojects.com/en/stable/) ・ [Litestar](https://docs.litestar.dev/2/) の公式 docs — 比較表（§3.8）
>
> 最終更新: 2026-11-09（Python 3.15.2・uv 0.13.7・FastAPI 0.162.2・Starlette 1.10.0・Uvicorn 0.54.0・Granian 2.8.7 で検証）

Node.js では、Hono・Express・Fastify でルートを書き、`app.listen()`（Hono なら `@hono/node-server` か `Bun.serve`）でそのまま HTTP を受ける。検証は Zod を挟み、OpenAPI は別のパッケージで作ることが多い。
Python では、**フレームワーク（FastAPI）と HTTP サーバー（Uvicorn などの ASGI サーバー）が別の部品**である。FastAPI は関数の型ヒントから、引数の検証・レスポンスの整形・OpenAPI の定義をまとめて作る。検証には [Step 04](04-typing.md) から使っている Pydantic のモデルをそのまま使う。
このステップでは、`faq-app` に `GET /faqs`・`GET /faqs/{id}`・`GET /search` の 3 本を持つ API を足し、Swagger UI で確かめ、`TestClient` でテストする。この API は [Step 11: 配布とデプロイ](11-deploy.md) でコンテナに入れる。
前は [Step 08: 非同期と並行処理](08-async.md)、全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **`uv add "fastapi[standard]"` で FastAPI・`fastapi` コマンド・Uvicorn がまとめて入る**。テスト用の HTTP クライアントや FastAPI Cloud の CLI も一緒に入る（§3.1）。
- **共有のデータは lifespan で起動時に 1 回だけ読み、`Annotated[..., Depends(...)]` で各ハンドラに注入する**。`@app.on_event("startup")` は非推奨である（§3.2）。
- **関数の引数の型がそのまま検証になる**。パスの `{faq_id}`・クエリの `category: Category | None`・`Query(min_length=1)` に合わないリクエストは、ハンドラに届く前に 422 で返る（§3.3）。
- **返り値の型（または `response_model`）がレスポンスの形を決める**。`response_model` は返り値の型より優先され、余分なフィールドを落とす（§3.3）。
- **開発は `fastapi dev`（127.0.0.1・自動リロード）、本番は `fastapi run`（0.0.0.0・リロードなし）**。`/docs` に Swagger UI が自動で付く（§3.4・§3.5）。
- **テストは `with TestClient(app) as client:`**。`with` を付けないと lifespan が動かない（§3.6）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Hono / Express / Fastify | FastAPI |
|---|---|---|
| HTTP を受ける | フレームワークが Node の `http` か `Bun.serve` に乗る | 別の ASGI サーバー（Uvicorn・Granian など）がアプリを読み込む |
| パスのパラメータ | `c.req.param("id")` / `req.params.id` | 関数の引数 `faq_id: str`（パスの `{faq_id}` と同じ名前） |
| クエリのパラメータ | `c.req.query("category")` / `req.query.category` | パスに無い名前の引数（`category: Category \| None = None`） |
| 入力の検証 | Zod（`@hono/zod-validator`）/ Fastify の JSON Schema | 引数の型ヒントと Pydantic のモデル |
| レスポンスの形 | `c.json(obj)`。形の保証は自分で書く | 返り値の型か `response_model` で検証・整形する |
| 依存の注入 | ミドルウェアで `c.set()` / Fastify の `decorate` | `Depends()`（`Annotated` で別名にして使い回す） |
| 起動時・終了時の処理 | `listen()` の前に書く / Fastify の `onReady`・`onClose` | `lifespan`（`yield` の前が起動時、後が終了時） |
| OpenAPI と UI | `@hono/zod-openapi` / `@fastify/swagger` を足す | 何も足さずに `/openapi.json` と `/docs` |
| テスト | `app.request()`（Hono）/ `app.inject()`（Fastify）/ supertest | `TestClient(app)` |

---

## 3. ハンズオン

[Step 07](07-cli.md) までの `faq-app/` を使う。`src/faq/` の `load_faqs`（`loader.py`）と `by_category`・`find_by_id`・`search`（`search.py`）は変えずに使い回す。サーバーは**ポート 8010** で動かし、記録を取ったら止めた。

### 3.1 FastAPI を入れる

**狙い**: `fastapi[standard]` が何を入れるのかを知ってから使う。

実行結果:

```text
$ uv add "fastapi[standard]"
Resolved 91 packages in 17ms
…（中略: 4 行）…
Installed 42 packages in 66ms
…（中略: 8 行）…
 + fastapi==0.162.2
 + fastapi-cli==0.0.32
 + fastapi-cloud-cli==0.27.1
…（中略: 36 行）…
 + starlette==1.10.0
…（中略: 5 行）…
 + uvicorn==0.54.0
```

`[standard]` は extras（npm の optional な依存のまとまりに近い）である。何が付くかは、入ったパッケージのメタデータ（`importlib.metadata.requires("fastapi")`）から読める（検証済み。12 行のうち 6 行）。

実行結果:

```text
opentelemetry-sdk>=1.44.0; extra == "standard"
fastapi-cli[standard]>=0.0.32; extra == "standard"
httpx2>=2.0.0; extra == "standard"
jinja2>=3.1.5; extra == "standard"
uvicorn[standard]>=0.12.0; extra == "standard"
pydantic-settings>=2.0.0; extra == "standard"
```

- FastAPI の docs の説明: `uvicorn[standard]` はアプリを動かすサーバー（uvloop など高速化の依存も入る）、`fastapi-cli[standard]` は `fastapi` コマンド（FastAPI Cloud へデプロイする `fastapi-cloud-cli` を含む）、`httpx2`（または `httpx`）は `TestClient` が使う HTTP クライアント。`jinja2`・`python-multipart`・`email-validator` はテンプレート・フォーム・メールアドレスの検証用である
- FastAPI の本体は **Starlette**（ルーティング・リクエスト・テストクライアント）と **Pydantic**（検証）の上に作られている。`fastapi` だけを入れると、これらの追加の依存は入らない
- FastAPI Cloud の CLI が要らなければ `uv add "fastapi[standard-no-fastapi-cloud-cli]"` もある（docs の "Without fastapi-cloud-cli"）

### 3.2 lifespan と `Depends` で FAQ を 1 回だけ読む

**狙い**: リクエストのたびに JSONL を読まず、起動時に読んだ一覧をハンドラに渡す。`src/faq/api.py` の前半（検証済み）。

```python
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, TypedDict

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

from faq.loader import load_faqs
from faq.models import Category, Faq
from faq.search import by_category, find_by_id, search


class State(TypedDict):
    faqs: list[Faq]


class FaqSummary(BaseModel):  # 検索結果では回答を返さない
    id: str
    category: Category
    question: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    path = Path(os.environ.get("FAQ_DATA", "data/faq.jsonl"))
    yield {"faqs": load_faqs(path)}  # 起動時に 1 回だけ読む


def get_faqs(request: Request) -> list[Faq]:
    faqs: list[Faq] = request.state.faqs
    return faqs


Faqs = Annotated[list[Faq], Depends(get_faqs)]

app = FastAPI(title="社内 FAQ API", lifespan=lifespan)
```

| 書き方 | 意味 | Node で言うと |
|---|---|---|
| `@asynccontextmanager` + `yield` | `yield` の前が起動時、後が終了時に 1 回ずつ動く | `await init(); app.listen()` と、`SIGTERM` での後片付け |
| `yield {"faqs": ...}` | lifespan state。各リクエストの `request.state` に浅いコピーで渡る | Hono の `c.set()` を全リクエストに共通で行う |
| `Depends(get_faqs)` | ハンドラの前に `get_faqs` を呼び、戻り値を引数に入れる | ミドルウェアで `c.get("faqs")` |
| `Faqs = Annotated[...]` | 依存の宣言に名前を付け、3 つのハンドラで使い回す | 共通の型と取得関数をまとめる |

- FastAPI の docs は lifespan を推奨し、`startup` / `shutdown` のイベントを "Alternative Events (deprecated)" に置いている。原文: "The recommended way to handle the startup and shutdown is using the lifespan parameter of the FastAPI app as described above."。両方は併用できない（"It's all lifespan or all events, not both."）
- 依存の書き方も docs は `Annotated` を勧める: "Prefer to use the Annotated version if possible."（`= Depends(...)` を既定値の位置に書く旧来の形より）
- `State` と `yield` した辞書は Starlette の docs の書き方である。Starlette は 0.52.0 から `Request[State]` と `request.state["faqs"]` で型を付けて読めるようにしたが、FastAPI 0.162.2 のハンドラや依存の引数に `Request[State]` と書くと起動時に落ちた（§5）。そのため属性で読み、変数の注釈で `list[Faq]` に絞っている（`return request.state.faqs` と書くと、mypy の strict が `Returning Any from function declared to return "list[Faq]"  [no-any-return]` と報告した。検証で再現）

### 3.3 パスとクエリのパラメータ、レスポンスのモデル

**狙い**: 3 本のエンドポイントを書き、型ヒントが検証とレスポンスの形になることを確かめる。`api.py` の後半（検証済み）。

```python
@app.get("/faqs")
def list_faqs(faqs: Faqs, category: Category | None = None) -> list[Faq]:
    return faqs if category is None else by_category(faqs, category)


@app.get("/faqs/{faq_id}")
def get_faq(faq_id: str, faqs: Faqs) -> Faq:
    faq = find_by_id(faqs, faq_id)
    if faq is None:
        raise HTTPException(status_code=404, detail=f"{faq_id} は無い")
    return faq


@app.get("/search", response_model=list[FaqSummary])
def search_faqs(faqs: Faqs, q: Annotated[str, Query(min_length=1)]) -> list[Faq]:
    return search(faqs, q)
```

| 引数・指定 | FastAPI の解釈 |
|---|---|
| `faq_id: str` | パスに `{faq_id}` があるので**パスのパラメータ** |
| `category: Category \| None = None` | パスに無いので**クエリ**。既定値があるので省略できる。`Literal` の外の値は 422 |
| `q: Annotated[str, Query(min_length=1)]` | 既定値が無いので**必須のクエリ**。空文字は 422 |
| `faqs: Faqs` | `Depends` なので、リクエストからは読まない |
| `-> Faq` / `-> list[Faq]` | レスポンスのモデル。返す値を検証し、OpenAPI にも載る |
| `response_model=list[FaqSummary]` | 返り値の型より優先される。`Faq` を返しても `answer` は落ちる |

ハンドラを `def`（同期）で書いたのは、中で `await` するものが無いからである。FastAPI は `def` のハンドラをスレッドプールで動かすので、イベントループは止まらない（[Step 08](08-async.md)）。

`uv run fastapi dev --port 8010` で起動し（§3.4）、curl で叩いた（検証済み）。

実行結果:

```text
$ curl -s "http://127.0.0.1:8010/faqs?category=IT" | jq -c ".[] | [.id, .question]"
["faq-05","社内 VPN につながりません。"]
["faq-06","パスワードを忘れました。"]
["faq-07","新しい PC のセットアップは誰がしますか？"]
$ curl -s -w "\n" http://127.0.0.1:8010/faqs/faq-06
{"id":"faq-06","category":"IT","question":"パスワードを忘れました。","answer":"ログイン画面の「パスワードを忘れた場合」から再設定できます。多要素認証の端末を紛失した場合はヘルプデスクへ連絡してください。"}
$ curl -s -w "\n" -G http://127.0.0.1:8010/search --data-urlencode "q=パスワード"
[{"id":"faq-06","category":"IT","question":"パスワードを忘れました。"}]
```

`/search` だけ `answer` が無いのが `response_model` の効果である。docs の原文: "If you declare both a return type and a response_model, the response_model will take priority and be used by FastAPI."。存在しない ID と、検証に通らない入力も確かめた（検証済み）。

実行結果:

```text
$ curl -s -i -w "\n" http://127.0.0.1:8010/faqs/faq-99
HTTP/1.1 404 Not Found
…（中略: 4 行）…

{"detail":"faq-99 は無い"}
$ curl -s -w "\n" -G http://127.0.0.1:8010/faqs --data-urlencode "category=人事"
{"detail":[{"type":"literal_error","loc":["query","category"],"msg":"Input should be '経費', '勤怠', 'IT', '総務', '出張' or 'セキュリティ'","input":"人事","ctx":{"expected":"'経費', '勤怠', 'IT', '総務', '出張' or 'セキュリティ'"}}]}
$ curl -s -w "\n" "http://127.0.0.1:8010/search?q="
{"detail":[{"type":"string_too_short","loc":["query","q"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
```

- `HTTPException` は `raise` するとその場で応答になる（`return` しない）。本文は `{"detail": ...}` の形
- 422 の本文は Pydantic の検証エラーそのものである。`type`（`literal_error`・`string_too_short`）は [Step 06](06-testing.md) でテストしたものと同じで、`loc` の先頭が `query` か `path` か `body` かで、どこの値が悪いかが分かる

### 3.4 `fastapi dev` と `fastapi run`

**狙い**: コマンドにアプリの場所を教え、開発用と本番用の起動の違いを知る。`pyproject.toml` に足した表（抜粋・単体では動かない）。

```toml
[tool.fastapi]
entrypoint = "faq.api:app"
```

docs は、毎回 `fastapi dev src/faq/api.py` や `--entrypoint` を渡すより、ここに書くことを勧めている（他のツールも読めるため）。

実行結果:

```text
$ uv run fastapi dev --port 8010

 ⚡️ Starting FastAPI in development mode

 🐍 Using import string: faq.api:app

 🌐 Server started at http://127.0.0.1:8010
    Documentation at http://127.0.0.1:8010/docs
…（中略: 4 行）…
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
INFO:     Started reloader process [71214] using WatchFiles
INFO:     Started server process [71242]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

`Application startup complete.` が出た時点で、lifespan の `yield` の前（FAQ の読み込み）が終わっている。止めると `Waiting for application shutdown.` の後に `yield` の後ろが動く。同じアプリを `fastapi run` でも起動した（検証済み）。

実行結果:

```text
$ uv run fastapi run --port 8010

 ⚡️ Starting FastAPI in production mode
…（中略: 8 行）…
INFO:     Started server process [72390]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8010 (Press CTRL+C to quit)
```

| | `fastapi dev` | `fastapi run` |
|---|---|---|
| 用途 | 開発 | 本番（コンテナの中など） |
| 待ち受けるアドレス | `127.0.0.1`（自分のマシンからだけ） | `0.0.0.0`（すべてのアドレス） |
| 自動リロード | 有効（WatchFiles が監視し、別プロセスで動かす） | 無効 |
| `FASTAPI_ENV` | `development` を入れる（既に値があれば残す） | 変えない |

- docs の原文（`fastapi dev`）: "By default, auto-reload is enabled, automatically reloading the server when you make changes to your code. This is resource-intensive and could be less stable than when it's disabled. You should only use it for development."
- `fastapi run` は 0.0.0.0 で待ち受けるので、手元で試すときも同じネットワークから届く。[Step 11](11-deploy.md) のコンテナではこちらを使う

### 3.5 自動の OpenAPI と Swagger UI

**狙い**: 何も書かずに API の定義とドキュメントが付くことを確かめる。

`http://127.0.0.1:8010/docs` を Playwright（ヘッドレスの Chromium）で開いた。タイトルは「社内 FAQ API - Swagger UI」で、`/faqs`・`/faqs/{faq_id}`・`/search` の 3 本と、`Category`・`Faq`・`FaqSummary`・`HTTPValidationError`・`ValidationError` のスキーマが並んだ。ブラウザのコンソールにエラーと警告は 0 件だった。UI の元になる `/openapi.json` も見る（検証済み）。

実行結果:

```text
$ curl -s http://127.0.0.1:8010/openapi.json | jq -r ".openapi, (.paths | keys[]), (.components.schemas | keys[])"
3.1.0
/faqs
/faqs/{faq_id}
/search
Category
Faq
FaqSummary
HTTPValidationError
ValidationError
```

- 出力は OpenAPI 3.1.0。`Category` は `type Category = Literal[...]`（[Step 04](04-typing.md)）から、`Faq` は Pydantic のモデルから作られた
- `/search` の 200 の応答は `{"type": "array", "items": {"$ref": "#/components/schemas/FaqSummary"}}` になっていた。`response_model` がドキュメントにも効く
- `/docs` の他に ReDoc の `/redoc` も付く。外したいときは `FastAPI(docs_url=None, redoc_url=None)`

### 3.6 `TestClient` でテストする

**狙い**: サーバーを起動せずに、HTTP のリクエストからレスポンスまでを確かめる。`tests/test_api.py` の 5 本のうち 2 本（検証済み。残りは `?category=IT` の 3 件、`/faqs/faq-05` の 200、未知のカテゴリの 422）。`data_path` は [Step 06](06-testing.md) の `conftest.py` の fixture である。

```python
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from faq.api import app


@pytest.fixture
def client(data_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("FAQ_DATA", str(data_path))
    with TestClient(app) as client:  # with で lifespan が動く
        yield client


def test_missing_id_is_404(client: TestClient) -> None:
    res = client.get("/faqs/faq-99")
    assert res.status_code == 404
    assert res.json() == {"detail": "faq-99 は無い"}


def test_search_hides_answer(client: TestClient) -> None:
    res = client.get("/search", params={"q": "VPN"})
    assert res.status_code == 200
    assert res.json() == [
        {"id": "faq-05", "category": "IT", "question": "社内 VPN につながりません。"}
    ]
```

- `TestClient` はアプリを同じプロセスの中で呼ぶ（Hono の `app.request()`、Fastify の `app.inject()` と同じ考え方）。`requests` と同じ形の API（`get`・`params=`・`.json()`）を持つ
- docs の原文: "When you need lifespan to run in your tests, you can use the TestClient with a with statement:"。lifespan で読むデータを使うので、`with` は必須である（§5）。`FAQ_DATA` は `monkeypatch.setenv` でテスト用のパスに向けた

Step 05〜07 の検査をまとめて回した（検証済み）。19 本だったテストが 24 本になった。

実行結果:

```text
$ uv run ruff check && uv run ruff format --check && uv run mypy && uv run pytest -q
All checks passed!
19 files already formatted
Success: no issues found in 14 source files
........................                                                 [100%]
24 passed in 1.71s
```

### 3.7 ASGI サーバー: Uvicorn と Granian

**狙い**: FastAPI と HTTP サーバーが別の部品であることを、サーバーを差し替えて確かめる。

ASGI は、Python の非同期の Web アプリとサーバーのつなぎ方の標準である（同期の時代の標準が WSGI）。FastAPI の docs は ASGI サーバーとして Uvicorn・Hypercorn・Daphne・Granian を挙げ、`fastapi run` には Uvicorn が入っている。Granian をプロジェクトに足さずに `--with` で一度だけ入れて動かした（検証済み）。

実行結果:

```text
$ uv run --with granian granian --interface asgi --port 8010 faq.api:app
Downloading granian (4.1MiB)
 Downloaded granian
Installed 2 packages in 9ms
[INFO] Starting granian (main PID: 72759)
[INFO] Listening at: http://127.0.0.1:8010
[INFO] Spawning worker-1 with PID: 72791
[INFO] Started worker-1
$ curl -s -i -w "\n" http://127.0.0.1:8010/faqs/faq-99
HTTP/1.1 404 Not Found
content-length: 29
content-type: application/json
server: granian
…（中略: 2 行）…
{"detail":"faq-99 は無い"}
```

| | Uvicorn 0.54.0 | Granian 2.8.7 |
|---|---|---|
| 実装 | Python（`[standard]` で uvloop・httptools を使う） | Rust（FastAPI の docs: "A Rust HTTP server for Python applications."） |
| 起動 | `fastapi run` / `uvicorn faq.api:app` | `granian --interface asgi faq.api:app` |
| 対応する方式 | ASGI | ASGI・WSGI・RSGI（Granian 独自） |

- Granian の `--interface` の既定は `rsgi` である。FastAPI では `asgi` を必ず渡す（`asginl` は lifespan を動かさない ASGI）
- アプリのコードは 1 行も変えていない。応答のヘッダー `server:` だけが `uvicorn` から `granian` に変わった。速さは測っていない

### 3.8 他のフレームワークとの比較

**狙い**: FastAPI 以外の候補が何を得意とするかを知る。どれも**インストールしていない**（公式 docs の記述だけから書いた。理由: 通し課題は FastAPI で作るため。3 つを同じ課題で作り直す分量はこのステップに収まらない）。

| | 版（PyPI） | 公式の自己紹介 | 方式 | 向いている場面 | 状態 |
|---|---|---|---|---|---|
| FastAPI | 0.162.2 | "high performance, easy to learn, fast to code, ready for production" | ASGI | 型ヒントで検証と OpenAPI を書きたい JSON の API | 検証済み（このステップ） |
| Django | 6.1.3 | "a high-level Python web framework that encourages rapid development and clean, pragmatic design" | WSGI・ASGI の両方 | ORM・管理画面・認証・テンプレートまで揃ったフルスタックの Web サイト。API は Django REST framework を足す | 未実行（docs のみ） |
| Flask | 3.1.3 | "a lightweight WSGI web application framework" | WSGI | 小さなアプリや、部品を自分で選びたいとき | 未実行（docs のみ） |
| Litestar | 2.25.0 | "a powerful, flexible, highly performant, and opinionated ASGI framework" | ASGI | FastAPI と同じ型ヒント中心の書き方で、依存の注入・OpenAPI・MessagePack などを最初から持つものが欲しいとき | 未実行（docs のみ） |

- Django は ASGI で動かせば、リクエストの処理を通しで非同期にできる。WSGI でも非同期のビューは動くが、原文: "Under a WSGI server, async views will run in their own, one-off event loop."
- Flask の非同期のビューはスレッドの中で動く。原文: "Flask's async support is less performant than async-first frameworks due to the way it is implemented."。非同期が中心なら、docs は Flask を ASGI で作り直した Quart を案内している

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| 起動時の初期化と後片付けは `lifespan` に書く | `@app.on_event("startup")` / `"shutdown"` | docs が非推奨（"Alternative Events (deprecated)"）とし、lifespan を推奨している。両方を混ぜると events は呼ばれない |
| 依存は `Annotated[T, Depends(f)]` で書き、別名にして使い回す | `faqs: list[Faq] = Depends(get_faqs)` | docs: "Prefer to use the Annotated version if possible."。型と依存を 1 か所にまとめられ、関数を普通に呼んでも壊れない |
| 応答の形は返り値の型で書き、外に出したくないフィールドがあるときだけ `response_model` で絞る | dict を組み立てて返す | 返す値が検証され、OpenAPI にも載る。`response_model` は返り値の型より優先される |
| 入力の制約（`Literal`・`Query(min_length=1)`）は型で書く | ハンドラの中で `if not q: return ...` | 422 とその理由（`type`・`loc`）を FastAPI が揃えて返し、OpenAPI にも制約が載る |
| 開発は `fastapi dev`、本番やコンテナは `fastapi run` | 本番で `--reload` | docs: 自動リロードは "resource-intensive and could be less stable"、"You should only use it for development." |
| lifespan を使うアプリは `with TestClient(app) as client:` でテストする | `client = TestClient(app)` をモジュールの先頭で作る | `with` が無いと lifespan が動かず、state が空のままになる（§5） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| curl に `Invalid HTTP request received.` と返り、サーバーのログに `WARNING:  Invalid HTTP request received.` が出る（検証中に発生） | `curl "http://.../faqs?category=人事"` のように、日本語をエンコードせずに URL に入れた。HTTP のリクエスト行として不正である | `curl -G --data-urlencode "category=人事"` で送る。ブラウザや HTTP クライアントのライブラリは自動でエンコードする |
| テストで `AttributeError: 'State' object has no attribute 'faqs'`（検証で再現） | `TestClient(app)` を `with` 無しで使い、lifespan が動いていない | `with TestClient(app) as client:` にする（§3.6） |
| 依存に `request: Request[State]` と書くと、import の時点で `FastAPIError: Invalid args for response field!`（検証で再現） | Starlette 1.10 は `Request` を state の型で総称化しているが、FastAPI 0.162.2 は `Request[State]` を `Request` として扱わず、エラーの文面のとおり Pydantic のフィールドとして解釈しようとして失敗する | `request: Request` と書き、`request.state.faqs` を注釈付きの変数で受ける（§3.2） |
| `FileNotFoundError: [Errno 2] No such file or directory: 'nope.jsonl'` の後に `ERROR:    Application startup failed. Exiting.` で止まる（検証で再現。`FAQ_DATA=nope.jsonl` で起動） | データのパスが間違っている。既定の `data/faq.jsonl` もカレントディレクトリが基準。lifespan で読むので、リクエストを受ける前の起動の時点で失敗する | `FAQ_DATA` で絶対パスを渡すか、プロジェクトの直下で起動する |

---

## 6. 次のステップ

- [Step 10: データ処理](10-data.md) — Polars などで FAQ や CSV を集計する
- [Step 11: 配布とデプロイ](11-deploy.md) — この API を `fastapi run` でコンテナに入れる
- 道具の側から整理したい場合は [Pydantic](../topics/pydantic.md)（モデルと検証エラー）と [pytest](../topics/pytest.md)（fixture と `monkeypatch`）、ライブラリの全体像は [ライブラリ地図](../topics/libraries.md)

---

## 出典

| 情報源 | URL |
|---|---|
| FastAPI — トップページ（Dependencies / `standard` Dependencies / Without fastapi-cloud-cli） | https://fastapi.tiangolo.com/ （2026-11-09 確認。`fastapi[standard]` が入れるものと役割、`standard-no-fastapi-cloud-cli`） |
| FastAPI — Lifespan Events / Testing Events | https://fastapi.tiangolo.com/advanced/events/ ・ https://fastapi.tiangolo.com/advanced/testing-events/ （2026-11-09 確認、Context7 `/websites/fastapi_tiangolo` 経由。原文はページから写した。lifespan の推奨、events の非推奨、併用できないこと、`with` 付きの `TestClient`） |
| FastAPI — Dependencies | https://fastapi.tiangolo.com/tutorial/dependencies/ （2026-11-09 確認。`Annotated` の推奨、0.95.0 から対応） |
| FastAPI — Response Model / Query Parameters and String Validations / Testing / Async | https://fastapi.tiangolo.com/tutorial/response-model/ ・ https://fastapi.tiangolo.com/tutorial/query-params-str-validations/ ・ https://fastapi.tiangolo.com/tutorial/testing/ ・ https://fastapi.tiangolo.com/async/ （2026-11-09 確認。`response_model` の優先順位、`Query(min_length=...)`、`TestClient`、`def` のハンドラはスレッドプールで動くこと） |
| FastAPI — FastAPI CLI | https://fastapi.tiangolo.com/fastapi-cli/ （2026-11-09 確認。`fastapi dev` / `fastapi run` の違い、`[tool.fastapi] entrypoint`、`FASTAPI_ENV`、中身が Uvicorn であること） |
| FastAPI — Run a Server Manually | https://fastapi.tiangolo.com/deployment/manually/ （2026-11-09 確認。ASGI サーバーの候補 Uvicorn・Hypercorn・Daphne・Granian） |
| Starlette — Lifespan | https://starlette.dev/lifespan/ （2026-11-09 確認。lifespan state、浅いコピー、0.52.0 からの `Request[State]` と辞書形式のアクセス） |
| Granian — README | https://github.com/emmett-framework/granian （2026-11-09 確認、Context7 `/emmett-framework/granian` 経由。`--interface` の既定 `rsgi`、`asginl`、既定のホストとポート） |
| Django — トップページ / Asynchronous support | https://www.djangoproject.com/ ・ https://docs.djangoproject.com/en/6.1/topics/async/ （2026-11-09 確認。自己紹介、WSGI での非同期ビュー）。API 用の Django REST framework は https://www.django-rest-framework.org/ |
| Flask — トップページ / Using async and await | https://flask.palletsprojects.com/en/stable/ ・ https://flask.palletsprojects.com/en/stable/async-await/ （2026-11-09 確認。WSGI、非同期の性能と Quart） |
| Litestar — Documentation | https://docs.litestar.dev/2/ （2026-11-09 確認。自己紹介と同梱の機能） |
| PyPI（各パッケージの最新版） | https://pypi.org/ （2026-11-08 確認。FastAPI 0.162.2・Django 6.1.3・Flask 3.1.3・Litestar 2.25.0・Uvicorn 0.54.0・Granian 2.8.7） |

### 確認できなかった事項

- **Django・Flask・Litestar は動かしていない**。§3.8 の表は公式 docs の記述だけから書いた。同じ FAQ API を各フレームワークで書いた場合の行数や挙動は確かめていない
- **Uvicorn と Granian の速度**は測っていない。どちらが速いかは書かない
- **Hono・Express・Fastify の API**（`c.req.param()`・`app.inject()`・`@fastify/swagger` など）は、各プロジェクトの docs の原文で確かめていない（対応表の目安として載せた）
- **FastAPI が `Request[State]` を受け付けるようになる予定**は、FastAPI のリリースノートと Issue で確かめていない。0.162.2 で起動に失敗したことだけを記録した

- 関連: [Python 学習ガイド](../README.md) / [Step 04: 型ヒント](04-typing.md) / [Step 06: テスト](06-testing.md) / [Step 07: スクリプトと CLI](07-cli.md) / [Step 08: 非同期と並行処理](08-async.md) / [Pydantic](../topics/pydantic.md) / [pytest](../topics/pytest.md)
