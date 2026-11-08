# Step 08: 非同期と並行処理 — 遅い API を並行に呼び、重い計算をコアに分ける

> 出典（一次情報）:
> - [Coroutines and Tasks (docs.python.org)](https://docs.python.org/3/library/asyncio-task.html) と [Runners (docs.python.org)](https://docs.python.org/3/library/asyncio-runner.html) — `asyncio.run`・`TaskGroup`・`asyncio.timeout`・`asyncio.to_thread`
> - [Developing with asyncio (docs.python.org)](https://docs.python.org/3/library/asyncio-dev.html) — ブロッキングの扱いとデバッグモード、[Python support for free threading (docs.python.org)](https://docs.python.org/3/howto/free-threading-python.html) と [concurrent.futures (docs.python.org)](https://docs.python.org/3/library/concurrent.futures.html) — GIL・free-threaded 版・スレッド / プロセスのプール
> - [Python versions (docs.astral.sh)](https://docs.astral.sh/uv/concepts/python-versions/) — uv で free-threaded 版を選ぶ方法
> - [pydantic/httpx2 (GitHub)](https://github.com/pydantic/httpx2) と [encode/httpx (GitHub)](https://github.com/encode/httpx) — HTTP クライアントの保守の状況
> - [Testing with AnyIO (anyio.readthedocs.io)](https://anyio.readthedocs.io/en/stable/testing.html) — async なテストを pytest で動かす plugin
>
> 最終更新: 2026-11-09（Python 3.15.2・3.15.2 free-threaded・uv 0.13.7・httpx2 2.16.0・AnyIO 4.16.0・pytest 9.2.0 で検証）

Node.js では、イベントループはプロセスの起動と同時に回っており、`fetch` も `setTimeout` も最初から非同期である。重い計算だけを `worker_threads` に逃がす。
Python は**既定で同期**である。イベントループは `asyncio.run()` で自分で起動し、`async def` の中でも同期の関数を呼べば、ループごと止まる。CPU の重い処理は、GIL（Global Interpreter Lock）のためスレッドでは速くならず、プロセスか free-threaded 版（`3.15t`）で分ける。
このステップでは、遅い FAQ サーバーを立て、`faq fetch` で N 件を逐次と並行で取得して時間を比べ、MockTransport でテストする。最後に、CPU の重い処理を 3.15 と 3.15t で測る。
前は [Step 07: スクリプトと CLI](07-cli.md)、全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **コルーチンは呼んだだけでは動かない**。`asyncio.run(main())` でループを起動し、中では `await` するか `TaskGroup` に渡す（§3.1）。
- **`async def` の中で `time.sleep` や同期の HTTP クライアントを呼ぶと、ループ全体が止まる**。3 件の 1 秒待ちが、`asyncio.sleep` なら 1.00 秒、`time.sleep` なら 3.02 秒になった（参考値、§3.2）。
- **並行は `asyncio.TaskGroup`**。`Promise.all` と違い、1 つ失敗すると残りを取り消し、例外を `ExceptionGroup` にまとめて投げる。受けるのは `except*`（§3.3）。
- **締め切りは `asyncio.timeout()`、同期しか無い処理は `asyncio.to_thread()`**（§3.4）。
- **HTTP クライアントは httpx2**。httpx は 2024-12 から新しいリリースが無く、Pydantic が fork を `httpx2` として保守している。API は `import` の名前が変わるだけである（§3.5）。
- **CPU の重い処理は、GIL ありの 3.15 ではスレッドで速くならない**。プロセス（`ProcessPoolExecutor`）か free-threaded 版 `uv run --python 3.15t` で分ける（§3.8）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js / Bun | Python |
|---|---|---|
| イベントループ | 起動時から回っている | `asyncio.run(main())` で自分で起動する |
| async 関数を呼ぶ | 最初の `await` まで同期で走る | コルーチンを返すだけで、何も動かない |
| トップレベルの `await` | ES Modules で書ける | `SyntaxError` |
| まとめて並行に待つ | `Promise.all([...])` | `async with asyncio.TaskGroup() as tg:` |
| 締め切り | `AbortSignal.timeout(ms)` | `async with asyncio.timeout(秒):` |
| 同期の処理を逃がす | `worker_threads` / libuv のスレッドプール | `asyncio.to_thread()` |
| CPU の重い処理を並列に | `worker_threads` | `ProcessPoolExecutor`、または free-threaded 版でスレッド |
| HTTP クライアント | `fetch` / undici / axios | httpx2 / aiohttp / niquests |
| HTTP のモック | msw / nock | `httpx2.MockTransport` / respx |
| async なテスト | Vitest がそのまま動かす | plugin が要る（AnyIO か pytest-asyncio） |

---

## 3. ハンズオン

§3.1〜3.4 と §3.8 は `faq-app/` の外の作業ディレクトリ（`lab/`）で 1 ファイルずつ動かす。§3.5〜3.7 は [Step 07](07-cli.md) までの `faq-app/` を進める。時間はすべて参考値である（Apple M2 Max、macOS 27.2）。

### 3.1 イベントループは自分で起動する

**狙い**: 「呼べば動く」JS の async 関数との違いを確かめる。`await` を付けずにコルーチン関数を呼ぶ（検証で再現）。

```python
import asyncio


async def greet() -> str:
    await asyncio.sleep(0.1)
    return "hello"


result = greet()  # await を忘れた
print(type(result))
print(asyncio.run(greet()))
```

実行結果:

```text
$ uv run never_awaited.py
<class 'coroutine'>
hello
<sys>:0: RuntimeWarning: coroutine 'greet' was never awaited
```

- `greet()` はコルーチンを作るだけで、本体は 1 行も動かない。公式 docs: "Note that simply calling a coroutine will not schedule it to be executed"。JS の async 関数は "up to and including the first await expression ... is run synchronously"（MDN）なので、ここが最初の違いになる
- `asyncio.run()` がループを作り、コルーチンを最後まで動かし、ループを閉じる。入口で 1 回だけ呼ぶ。ループの中から呼ぶと `RuntimeError: asyncio.run() cannot be called from a running event loop`、モジュールの直下に `await` を書くと `SyntaxError: 'await' outside function` になった（どちらも検証で再現）

### 3.2 async def の中の同期の待ちはループを止める

**狙い**: Node の「イベントループをブロックするな」が Python でも同じであることを、数字で見る。1 秒待つタスクを 3 つ、`time.sleep` と `asyncio.sleep` で並行に動かす（検証済み）。

```python
import asyncio
import time


async def bad() -> None:
    time.sleep(1)  # ループごと止まる


async def good() -> None:
    await asyncio.sleep(1)  # 待つ間、ループは他のタスクを進める


async def main() -> None:
    for label, worker in [("time.sleep   ", bad), ("asyncio.sleep", good)]:
        start = time.perf_counter()
        async with asyncio.TaskGroup() as tg:
            for _ in range(3):
                tg.create_task(worker())
        print(f"{label}: {time.perf_counter() - start:.2f} 秒")


asyncio.run(main())
```

実行結果:

```text
$ uv run blocking.py
time.sleep   : 3.02 秒
asyncio.sleep: 1.00 秒
```

- ループは 1 つのスレッドで、`await` に来たタスクから次のタスクへ切り替える。`time.sleep` には `await` が無いので、3 つが順番に 1 秒ずつ走った。公式 docs: "An event loop runs in a thread (typically the main thread) and executes all callbacks and Tasks in its thread." 同じことが、`requests`・同期版の `httpx2.Client`・重い計算でも起きる。`async def` に書き換えただけでは速くならない
- 見つけるには**デバッグモード**を使う。`PYTHONASYNCIODEBUG=1 uv run blocking.py` は `bad()` の 3 つのタスクについて `Executing <Task finished ... coro=<bad() ...> took 1.006 seconds` を出した（検証済み）。docs: "Callbacks taking longer than 100 milliseconds are logged."

### 3.3 TaskGroup で並行に動かす（Promise.all との違い）

**狙い**: 1 つが失敗したときの動作を確かめる。`asyncio.sleep(1)` の後に `ok(1) 完了` と出す `ok(1)` と、0.1 秒後に `ValueError("壊れた")` を投げる `fail()` を同じグループに入れる（抜粋・単体では動かない。ファイル全体は検証済み）。

```python
async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ok(1))
            tg.create_task(fail())
    except* ValueError as eg:
        print(f"捕まえた: {eg.exceptions!r}")
        print(f"ok(1) は取り消された: {t1.cancelled()}")
```

実行結果:

```text
$ uv run taskgroup_error.py
捕まえた: (ValueError('壊れた'),)
ok(1) は取り消された: True
```

- `ok(1) 完了` は出ない。公式 docs: "The first time any of the tasks belonging to the group fails with an exception other than asyncio.CancelledError, the remaining tasks in the group are cancelled." `Promise.all` は最初の reject で結果を返すが、残りの Promise を止める仕組みは無い。Python の `asyncio.gather` も同じで、docs は "Other awaitables in the aws sequence won’t be cancelled and will continue to run." としたうえで、TaskGroup を "stronger safety guarantees than gather" と勧めている
- 例外は `ExceptionGroup` に包まれて出てくる（PEP 654）。`except ValueError:` では捕まらないので `except*` で受ける
- 結果は `async with` を抜けた後に `task.result()` で取り出す。3.15 では、目的を果たしたら残りを止める `TaskGroup.cancel()` が加わった（What's New in Python 3.15）

### 3.4 締め切りとスレッドへの逃がし

**狙い**: `AbortSignal.timeout` にあたる `asyncio.timeout()` と、同期しか無い処理を逃がす `asyncio.to_thread()` を使う。`timeout.py` は 2 秒かかる `slow()` を 0.5 秒で打ち切り、`to_thread.py` は `time.sleep(1)` を含む同期の `legacy_io(n)` を 3 つ並行に動かす（抜粋・単体では動かない。ファイル全体は検証済み）。

```python
try:  # timeout.py の main() の中
    async with asyncio.timeout(0.5):
        await slow()
except TimeoutError:
    print("0.5 秒で打ち切った")

async with asyncio.TaskGroup() as tg:  # to_thread.py の main() の中
    tasks = [tg.create_task(asyncio.to_thread(legacy_io, n)) for n in range(3)]
print([t.result() for t in tasks], f"{time.perf_counter() - start:.2f} 秒")
```

実行結果:

```text
$ uv run timeout.py
0.5 秒で打ち切った
$ uv run to_thread.py
[0, 1, 2] 1.01 秒
```

- `asyncio.timeout()` は締め切りで中の処理を取り消し、組み込みの `TimeoutError` を投げる。docs: "Return an asynchronous context manager that can be used to limit the amount of time spent waiting on something." `to_thread` は I/O 待ちのためのものである。公式 docs: "Due to the GIL, asyncio.to_thread() can typically only be used to make IO-bound functions non-blocking." CPU の重い処理は §3.8 で扱う

### 3.5 HTTP クライアントを選び、httpx2 を入れる

**狙い**: 非同期で使える HTTP クライアントを、保守の状況から選ぶ。2026-11-09 に GitHub API と PyPI で確かめた事実を並べる。

| 名前 | 最新版（公開日） | PyPI の Development Status | 同期 / 非同期 | 事実 |
|---|---|---|---|---|
| httpx | 0.28.1（2024-12-06） | 4 - Beta | 両方 | 以降リリースは無く、最後にマージされた PR は 2026-02-23。2026-10-01 に作者が「Version 1.0」の PR（[#3796](https://github.com/encode/httpx/pull/3796)）を開き、"Version 1.0 is not planned to introduce breaking changes." と書いた。アーカイブはされていない |
| httpx2 | 2.16.0（2026-10-21） | 5 - Production/Stable | 両方 | Pydantic による httpx 0.28.1 の fork（2026-05 から 20 回以上リリース）。README: "With HTTPX itself seeing limited activity recently, Pydantic is picking up stewardship under the HTTPX2 name"。変更点は changelog の "Renamed package: `httpx` -> `httpx2`. ... No other public API changed." |
| aiohttp | 3.14.5（2026-10-11） | 5 - Production/Stable | 非同期のみ | クライアントとサーバーの両方を持つ。3.15 / 3.15t 用の wheel がある |
| niquests | 3.21.2（2026-09-23） | 5 - Production/Stable | 両方 | requests 互換の API に HTTP/2・HTTP/3 を足したもの。`AsyncSession` を持つ |

- **通し課題は httpx2 を使う**。根拠は、(1) 最新の httpx と同じ API を保ったまま保守されている、(2) Starlette 1.10.0（FastAPI の土台）の `TestClient` が `httpx2` を優先し、`httpx` だと `StarletteDeprecationWarning`（"Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead."）を出す（検証済み）、(3) 同期と非同期が同じ形で書け、テスト用の `MockTransport` を同梱している、の 3 点である
- 既存の httpx のコードは、依存と `import httpx` を `httpx2` に置き換えれば動く（changelog の記述どおり。通し課題も置き換えだけで検査が通った）。非同期だけでよくサーバーも同じライブラリで書きたいなら aiohttp、HTTP/3 が要るなら niquests も候補になる

依存を入れる（検証済み。anyio・idna なども一緒に入る）。httpx2 は既定の証明書の検証に certifi ではなく OS の証明書ストア（truststore）を使う（changelog 2.3.0）。

実行結果:

```text
$ uv add httpx2
…（中略: 8 行）…
 + h11==0.16.0
 + httpcore2==2.16.0
 + httpx2==2.16.0
 + idna==3.20
 + truststore==0.10.5
```

### 3.6 遅いサーバーを立て、逐次と並行で取得する

**狙い**: 1 件 0.5 秒かかる API を、N 件まとめて取るときの差を見る。サーバーは標準ライブラリだけで書いた `scripts/slow_server.py`（ポート 8011。`ThreadingHTTPServer` でリクエストごとにスレッドを分け、`GET /faqs/<id>` で 0.5 秒待ってから FAQ を返す）。取得側の `src/faq/fetch.py` は、1 件を取る `fetch_faq()`（`await client.get(f"/faqs/{faq_id}")` → `raise_for_status()` → `Faq.model_validate_json()`）と、`await` を並べるだけの `fetch_sequential()`、TaskGroup を使う `fetch_concurrent()`、クライアントと締め切りを用意する `run_fetch()` からなる（抜粋・単体では動かない。ファイル全体は検証済み）。

```python
async def fetch_concurrent(client: httpx2.AsyncClient, ids: Sequence[str]) -> list[Faq]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_faq(client, faq_id)) for faq_id in ids]
    return [task.result() for task in tasks]  # 順序は ids のまま


async def run_fetch(
    fetcher: Fetcher,
    ids: Sequence[str],
    base_url: str,
    timeout: float,
    transport: httpx2.AsyncBaseTransport | None = None,
) -> list[Faq]:
    async with httpx2.AsyncClient(base_url=base_url, transport=transport) as client:
        async with asyncio.timeout(timeout):  # 全体の締め切り
            return await fetcher(client, ids)
```

`cli.py` には `fetch` サブコマンドを足す。`--count`（1〜12）・`--base-url`（既定 `http://127.0.0.1:8011`）・`--timeout` を受け、逐次と並行を順に `asyncio.run(run_fetch(...))` で動かして時間を出す（抜粋・単体では動かない）。

```python
        try:
            faqs = asyncio.run(run_fetch(fetcher, ids, base_url, timeout))
        except* (httpx2.HTTPError, TimeoutError) as eg:  # 並行側は ExceptionGroup で届く
            err_console.print(f"{label}: 取得に失敗した: {eg.exceptions[0]!r}")
            raise typer.Exit(code=1)
        console.print(f"{label}: {len(faqs)} 件 {time.perf_counter() - start:.2f} 秒")
```

別の端末で `uv run scripts/slow_server.py` を起動し（`http://127.0.0.1:8011 で待ち受ける（遅延 0.5 秒）` と出る）、取得する（検証済み）。

実行結果:

```text
$ uv run faq fetch --count 5
逐次: 5 件 2.64 秒
並行: 5 件 0.51 秒
$ uv run faq fetch --count 12
逐次: 12 件 6.18 秒
並行: 12 件 0.51 秒
$ uv run faq fetch --count 5 --timeout 1
逐次: 取得に失敗した: TimeoutError()
```

- 逐次は「件数 × 0.5 秒」、並行は件数によらず約 0.5 秒になった（参考値）。並行の上限は、httpx2 の接続プールの既定（`max_connections` 100）とサーバー側の処理能力で決まる。多数の相手に投げるときは `httpx2.Limits` か `asyncio.Semaphore` で絞る
- `AsyncClient` は `async with` で 1 つ作って使い回す。接続を再利用するためで、httpx の docs も "make sure you're not instantiating multiple client instances" と注意している
- サーバーを止めたまま動かすと `逐次: 取得に失敗した: ConnectError('All connection attempts failed')` で終了コード 1 になった（検証済み）。`except*` は、包まれていない例外（逐次側）も `ExceptionGroup`（並行側）も受ける。使い終わったサーバーは Ctrl+C で止める

### 3.7 async なテストを書く（AnyIO の plugin と MockTransport）

**狙い**: サーバーを立てずに、取得の動作と並行であることをテストする。まず async なテストをそのまま書くと、pytest は動かさない（検証で再現）。

実行結果:

```text
$ uv run pytest -q tests/test_fetch.py -k concurrent_keeps
…（中略: 3 行）…
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
…（中略: 5 行）…
1 failed, 5 deselected in 0.61s
```

httpx2 の依存に入っている AnyIO が pytest の plugin を持つので、それを使う（FastAPI の docs の Async Tests と同じ方法）。テストが直接使うので `uv add --dev anyio` で dev グループにも書いた。`tests/conftest.py` に `anyio_backend` を返す fixture（`return "asyncio"`）を足し、テストのファイルに印を付ける（抜粋・単体では動かない）。

```python
# このファイルの async なテストを、AnyIO の pytest plugin で動かす
pytestmark = pytest.mark.anyio


def slow_transport(faqs: list[Faq], delay: float) -> httpx2.MockTransport:
    by_id = {faq.id: faq for faq in faqs}

    async def handler(request: httpx2.Request) -> httpx2.Response:
        await asyncio.sleep(delay)  # 遅いサーバーの代わり
        faq = by_id.get(request.url.path.removeprefix("/faqs/"))
        if faq is None:
            return httpx2.Response(404)
        return httpx2.Response(200, content=faq.model_dump_json())

    return httpx2.MockTransport(handler)


async def test_404_arrives_in_exception_group(faqs: list[Faq]) -> None:
    transport = slow_transport(faqs, delay=0)
    with pytest.RaisesGroup(httpx2.HTTPStatusError):  # TaskGroup が包んで投げる
        await run_fetch(fetch_concurrent, ["faq-99"], "http://test", 5, transport)
```

最後のテストを、最初は `pytest.raises(httpx2.HTTPStatusError)` で書いていた。並行側は例外が `ExceptionGroup` に包まれるので、一致せずに失敗した（検証で再現）。

実行結果:

```text
$ uv run pytest -q tests/test_fetch.py -k 404
…（中略: 2 行）…
_____________________ test_404_arrives_in_exception_group ______________________
  + Exception Group Traceback (most recent call last):
…（中略: 15 行）…
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
…（中略: 6 行）…
    | httpx2.HTTPStatusError: Client error '404 Not Found' for url 'http://test/faqs/faq-99'
…（中略: 3 行）…
FAILED tests/test_fetch.py::test_404_arrives_in_exception_group - HTTPStatusE...
1 failed, 5 deselected in 0.61s
```

`pytest.RaisesGroup`（pytest 8.4 から）に直すと通る。ほかに、並行なら 0.2 秒の遅延 5 件が 0.5 秒未満で順序どおりに返ること、逐次が遅延の合計以上かかること、`timeout=0.1` で `TimeoutError` になること、`faq fetch` が成功時に 0・締め切り切れで 1 を返すこと（`monkeypatch` で `run_fetch` に MockTransport を渡す）をテストした。Step 05〜07 の検査はすべて通る（検証済み）。

実行結果:

```text
$ uv run ruff check && uv run ruff format --check && uv run mypy && uv run pytest -q
All checks passed!
17 files already formatted
Success: no issues found in 12 source files
...................                                                      [100%]
19 passed in 1.98s
```

- `httpx2.MockTransport` は handler に async 関数も受け取る（ソースのコメント: "Allow handler to *optionally* be an `async` function."）。`await asyncio.sleep()` で遅いサーバーを真似られる。URL ごとの細かいモックが要るなら respx がある（httpx の docs が案内している。httpx2 で動くかは確かめていない）
- `anyio_backend` を `"asyncio"` に固定したのは、`fetch.py` が `asyncio.TaskGroup` を使い trio では動かないためである（AnyIO の docs: 既定の fixture は "runs everything on all supported backends"）。pytest-asyncio でもよいが、両方を auto モードにすると衝突する（同 docs）。カバレッジは 98%（`fetch.py` と `cli.py` は 100%）

### 3.8 CPU の重い処理: GIL と free-threaded 版 3.15t

**狙い**: スレッドで速くなる処理とならない処理を分ける。素数を数える関数を 4 回、逐次・スレッド 4 本・プロセス 4 つで動かし、通常版と free-threaded 版で比べる（検証済み）。

```python
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def count_primes(limit: int) -> int:
    return sum(all(n % d for d in range(2, int(n**0.5) + 1)) for n in range(2, limit))


def timed(label: str, run) -> None:
    start = time.perf_counter()
    run()
    print(f"{label}: {time.perf_counter() - start:5.2f} 秒")


if __name__ == "__main__":
    jobs = [300_000] * 4
    print(sys.version.split()[0], "GIL 有効:", sys._is_gil_enabled())
    timed("逐次", lambda: [count_primes(n) for n in jobs])
    with ThreadPoolExecutor(max_workers=4) as pool:
        timed("スレッド x4", lambda: list(pool.map(count_primes, jobs)))
    with ProcessPoolExecutor(max_workers=4) as pool:
        timed("プロセス x4", lambda: list(pool.map(count_primes, jobs)))
```

uv は free-threaded 版を `3.15t`（または `3.15+freethreaded`）で指定する。`uv python install 3.15t` で入り、`uv run --python 3.15t` で選ぶ（この環境には入れてあった）。

実行結果:

```text
$ uv python install 3.15t
Python 3.15+freethreaded is already installed
$ uv run --python 3.15 cpu_threads.py
3.15.2 GIL 有効: True
逐次:  1.46 秒
スレッド x4:  1.44 秒
プロセス x4:  0.55 秒
$ uv run --python 3.15t cpu_threads.py
3.15.2 GIL 有効: False
逐次:  1.76 秒
スレッド x4:  0.72 秒
プロセス x4:  0.67 秒
```

- **GIL ありの 3.15 では、スレッドを 4 本にしても逐次と変わらない**（1.46 → 1.44 秒、参考値）。GIL が同時に Python のコードを動かすスレッドを 1 本に限るためである。プロセスは別のインタープリタなので 0.55 秒まで縮んだ
- **free-threaded 版ではスレッドで縮む**（1.76 → 0.72 秒）。代わりに逐次は遅くなった。公式 docs: "The free-threaded build has additional overhead when executing Python code compared to the default GIL-enabled build."（pyperformance の平均で macOS aarch64 は約 1%、x86-64 Linux は 8% としている。この計測の差はそれより大きい）
- 3.15t でも `PYTHON_GIL=1` を付けると GIL が戻り、スレッド x4 は 1.86 秒になった（検証済み）。GIL に対応すると宣言していない C 拡張を import したときも、警告を出して GIL が有効になる（公式 docs）。3.15t 用の wheel が無いライブラリもある（[Python のバージョン](../topics/python-versions.md)）。free-threaded 版は 3.14 で「サポート対象」になった（PEP 779）が、uv は明示しない限り通常版を選ぶ（"The GIL-enabled build of Python will still be preferred"）
- `if __name__ == "__main__":` は外せない。macOS と Windows のプロセスの既定の起動方法は spawn で、子プロセスが本体を import し直す。ガードを外すと `RuntimeError`（"An attempt has been made to start a new process before the current process has finished its bootstrapping phase."）と `BrokenProcessPool` で落ちた（検証で再現）

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| 入口で `asyncio.run(main())` を 1 回だけ呼び、中は `await` でつなぐ | 関数ごとに `asyncio.run()` を呼ぶ。ループの中から呼ぶ | `asyncio.run` は毎回ループを作って閉じる。ループの中からは `RuntimeError` になる（§3.1） |
| 並行は `asyncio.TaskGroup` で書く | `create_task` だけして参照を捨てる。新しく `gather` を書く | 失敗時に残りを取り消し、例外を漏らさない。docs: "The event loop only keeps weak references to tasks."、TaskGroup は "stronger safety guarantees than gather" |
| `async def` の中は非同期の API で書き、同期しか無い I/O は `asyncio.to_thread` に逃がす。開発中は `PYTHONASYNCIODEBUG=1` で確かめる | `time.sleep`・`requests`・同期の DB ドライバをそのまま呼ぶ | ループが止まり、並行にしたはずの処理が直列になる（§3.2、3.02 秒 vs 1.00 秒）。docs: "Blocking (CPU-bound) code should not be called directly." |
| 締め切りは `async with asyncio.timeout(秒):` で処理のまとまりごとに付ける | 締め切りを付けない | 遅い相手に引きずられて全体が止まらないようにする。httpx から引き継いだ既定のタイムアウト（5 秒）は、1 回のリクエストごとの値である |
| 新しく HTTP クライアントを入れるなら httpx2。`AsyncClient` は 1 つ作って使い回す | 新規に httpx を入れる。リクエストごとに `AsyncClient` を作る | httpx は 2024-12 からリリースが無く、Starlette の `TestClient` は httpx を非推奨にした（§3.5）。API は同じ。接続プールは使い回してはじめて効く |
| `TaskGroup` の失敗は `except*`、テストは `pytest.RaisesGroup` で受ける | `except httpx2.HTTPError:` / `pytest.raises` で受ける | 例外は `ExceptionGroup` に包まれて届く（§3.7） |
| CPU の重い処理は `ProcessPoolExecutor`、依存が対応していれば free-threaded 版のスレッドで分ける | GIL ありの版でスレッドを増やす | GIL ありではスレッドで速くならない（§3.8） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `ruff format --check` が、足した `cli.py` と `tests/test_fetch.py` を指摘した（検証中に発生） | `Annotated[...]` のオプションや、行末に置いた日本語のコメントで 88 文字を超えた。Ruff は長いコメント付きの式を括弧で折り返した | `uv run ruff format` で直す。折り返しが読みにくければ、コメントを上の行に移す |
| async なテストが `async def functions are not natively supported.` で失敗した（検証中に発生） | pytest は async な関数を動かさない | AnyIO の `pytest.mark.anyio`（または pytest-asyncio）を使う（§3.7） |
| `pytest.raises(httpx2.HTTPStatusError)` が一致しない（検証で再現） | `TaskGroup` が例外を `ExceptionGroup` に包む | `pytest.RaisesGroup(httpx2.HTTPStatusError)` にする |
| `async def` にしたのに速くならない（検証で再現） | 中で `time.sleep` など同期の処理を呼んでいる | 非同期の API に替えるか `asyncio.to_thread` に逃がす。`PYTHONASYNCIODEBUG=1` で見つける |
| `RuntimeWarning: coroutine '...' was never awaited` / `RuntimeError: asyncio.run() cannot be called from a running event loop`（検証で再現） | `await` せずにコルーチン関数を呼んだ / ループの中から `asyncio.run` を呼んだ | `await` するか `tg.create_task()` に渡す。`asyncio.run` は入口で 1 回だけ |
| スレッドを増やしても CPU の重い処理が速くならない（検証で再現） | GIL ありの版では、Python のコードを同時に動かすスレッドは 1 本 | プロセスを使うか、`uv run --python 3.15t` で free-threaded 版を使う |
| `ProcessPoolExecutor` が `BrokenProcessPool` で落ちる（検証で再現） | `if __name__ == "__main__":` が無く、spawn で起動した子が本体を import し直した | プールを作る処理をガードの中に入れる |

---

## 6. 次のステップ

- [Step 09: Web API](09-web-api.md) — FastAPI で `async def` のエンドポイントを書き、httpx2 の `TestClient` でテストする
- ライブラリの選び方は [ライブラリ地図](../topics/libraries.md)、道具の側からは [pytest](../topics/pytest.md)（plugin・fixture）と [Python のバージョン](../topics/python-versions.md)（free-threaded 版）

---

## 出典

| 情報源 | URL |
|---|---|
| asyncio — Coroutines and Tasks / Runners | https://docs.python.org/3/library/asyncio-task.html ・ https://docs.python.org/3/library/asyncio-runner.html （2026-11-09 確認。ループの中から `asyncio.run` を呼べないこと、コルーチンを呼んだだけでは動かないこと、TaskGroup の取り消し、gather との比較、`create_task` の弱参照、`asyncio.timeout`、`to_thread` と GIL、`TaskGroup.cancel()`） |
| asyncio — Developing with asyncio | https://docs.python.org/3/library/asyncio-dev.html （2026-11-09 確認。デバッグモード、100 ミリ秒、"Blocking (CPU-bound) code should not be called directly."） |
| What's New In Python 3.15 | https://docs.python.org/3.15/whatsnew/3.15.html （2026-11-09 確認。`TaskGroup.cancel`、PEP 803） |
| Python support for free threading | https://docs.python.org/3/howto/free-threading-python.html （2026-11-09 確認。`PYTHON_GIL`・`-X gil`、C 拡張で GIL が戻ること、単一スレッドのオーバーヘッド、`sys._is_gil_enabled()`） |
| concurrent.futures / multiprocessing | https://docs.python.org/3/library/concurrent.futures.html ・ https://docs.python.org/3/library/multiprocessing.html （2026-11-09 確認。`max_workers` の既定、spawn が macOS と Windows の既定、"Safe importing of main module"） |
| PEP 654 / 703 / 779 | https://peps.python.org/pep-0654/ ・ https://peps.python.org/pep-0703/ ・ https://peps.python.org/pep-0779/ （2026-11-09 確認。すべて Final） |
| uv — Python versions | https://docs.astral.sh/uv/concepts/python-versions/ （2026-11-09 確認。`3.15t` / `+freethreaded` の指定、3.14 以降も通常版を優先すること） |
| httpx2 — README / CHANGELOG | https://github.com/pydantic/httpx2 ・ https://github.com/pydantic/httpx2/blob/main/src/httpx2/CHANGELOG.md （2026-11-09 確認。fork の経緯、改名以外の公開 API は変わらないこと、truststore、3.15 対応） |
| httpx / aiohttp / niquests — GitHub / PyPI / docs | https://github.com/encode/httpx ・ https://github.com/aio-libs/aiohttp ・ https://github.com/jawah/niquests ・ https://github.com/encode/httpx/pull/3796 ・ https://pypi.org/project/httpx/ ・ https://www.python-httpx.org/ （2026-11-09 確認。リリース日・状態・wheel・最終マージの日付（GitHub API と PyPI）、httpx の Version 1.0 の PR、`Limits` と既定のタイムアウト、MockTransport。Context7 `/encode/httpx/0.28.1`） |
| Starlette — testclient.py | https://github.com/Kludex/starlette/blob/master/starlette/testclient.py （2026-11-09 確認。httpx2 を優先し httpx を非推奨にする処理。1.10.0 の動作は手元で確認） |
| AnyIO — Testing with AnyIO | https://anyio.readthedocs.io/en/stable/testing.html （2026-11-09 確認、Context7 `/agronholm/anyio`。`pytest.mark.anyio`、`anyio_backend`、pytest-asyncio との衝突） |
| FastAPI — Async Tests | https://fastapi.tiangolo.com/advanced/async-tests/ （2026-11-09 確認。`pytest.mark.anyio` と `AsyncClient` によるテスト） |
| pytest — API Reference（RaisesGroup） | https://docs.pytest.org/en/stable/reference/reference.html （2026-11-09 確認。"Added in version 8.4."） |
| MDN — Promise.all / async function | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all ・ https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function （2026-11-09 確認。対応表の JS 側） |

### 確認できなかった事項

- **respx が httpx2 で動くか**。respx 0.23.1（2026-04-08）は httpx2 の公開より前のリリースで、httpx2 への対応を README などで確かめていない。通し課題は同梱の `MockTransport` で済ませた
- **free-threaded 版での単一スレッドの遅さ**。この計測では逐次が 1.46 → 1.76 秒と、docs の「macOS aarch64 で約 1%」より大きかった。1 種類の処理を 1 回測っただけの参考値であり、原因は調べていない。`uv python pin 3.15t` でプロジェクトごと free-threaded 版にする方法も試していない。通し課題の依存（pydantic-core など）が 3.15t で入るかも、この Step では確かめていない
- **httpx の今後**。作者の PR #3796 は 1.0 を予告しているが、リリースの時期は書かれていない。httpx2 との関係についての公式の告知も見つけていない

- 関連: [Python 学習ガイド](../README.md) / [Step 06: テスト](06-testing.md) / [Step 07: スクリプトと CLI](07-cli.md) / [Step 09: Web API](09-web-api.md) / [ライブラリ地図](../topics/libraries.md) / [pytest](../topics/pytest.md)
