# pytest — テストの書き方と設定の早見表

> 出典（一次情報）:
> - [How-to guides (docs.pytest.org)](https://docs.pytest.org/en/stable/how-to/index.html) — assert・fixture・parametrize・mark・unittest
> - [Fixtures reference / API reference (docs.pytest.org)](https://docs.pytest.org/en/stable/reference/fixtures.html) — scope、`conftest.py` の階層、組み込みの fixture
> - [Good Integration Practices (docs.pytest.org)](https://docs.pytest.org/en/stable/explanation/goodpractices.html) — import mode の推奨、src layout、strict mode
> - [Configuration / Changelog 9.0.0 (docs.pytest.org)](https://docs.pytest.org/en/stable/reference/customize.html) — `[tool.pytest]` と `pytest.toml`
> - 各プラグインの docs（pytest-cov・pytest-xdist・pytest-mock・pytest-asyncio・AnyIO）
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・pytest 9.2.0・pytest-xdist 3.8.0 で検証）

pytest は Python のテストランナーの事実上の標準で、Vitest・Jest・`bun test` にあたる。ただし `describe` / `expect` の API は無く、テストは普通の関数、確かめるのは素の `assert`、準備は引数名で注入される fixture である。
本ページは書き方・コマンド・設定を引くための早見表で、通し課題での使い方は [Step 06: テスト](../steps/06-testing.md) にある。

---

## 1. TL;DR

- **入れ方は `uv add --dev pytest`、回し方は `uv run pytest`**。`uvx pytest` ではプロジェクトの依存が見えない（[Step 06](../steps/06-testing.md) §3.1）。
- **`beforeEach` / `afterEach` は `yield` を使う fixture 1 つで書く**。`yield` の前が準備、後が後片付けで、`scope=` で `beforeAll` 相当にもなる（§3.2）。
- **設定は `[tool.pytest]`（pytest 9.0 からのネイティブな TOML）に書き、`strict = true` を付ける**。`[tool.pytest.ini_options]` と同時に書くと起動しない（§3.4、検証で再現）。
- **新しいプロジェクトでは `--import-mode=importlib` が公式の推奨**。ただし既定は今後も `prepend` のまま（§3.5）。
- `--watch` は組み込みに無い。並列実行は pytest-xdist の `-n`、カバレッジは pytest-cov の `--cov`（§3.6）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Vitest / Jest / `bun test` | pytest |
|---|---|---|
| まとまりを作る | `describe("...", () => {})` | ファイル（モジュール）か `class TestXxx:`（`__init__` を持たない普通のクラス） |
| テストを書く | `it(...)` / `test(...)` | `def test_xxx() -> None:` |
| 期待値 | `expect(a).toBe(b)` / `toEqual` | `assert a == b`（`is` は同一性。`toBe` の厳密さが要るときだけ） |
| 例外 | `expect(fn).toThrow(/msg/)` | `with pytest.raises(E, match=r"msg"):`（`match` は `re.search`） |
| 毎テストの準備・後片付け | `beforeEach` / `afterEach` | `@pytest.fixture` で `yield` の前後に書く |
| 一度だけの準備 | `beforeAll` / `afterAll` | `@pytest.fixture(scope="module")` / `"session"` |
| 表で回す | `test.each([...])("%s", ...)` | `@pytest.mark.parametrize(..., ids=[...])` |
| 飛ばす・失敗を予期する | `test.skip` / `test.todo` / `test.fails` | `skip` / `skipif(条件, reason=)` / `xfail` |
| 1 つだけ動かす | `test.only` | 無い。`-k <式>` かノード ID（`file.py::test_x`）で絞る |
| 差し替え | `vi.spyOn` / `vi.stubEnv` / `vi.mock` | `monkeypatch`（組み込み）/ `unittest.mock`（標準ライブラリ）/ pytest-mock の `mocker` |
| スナップショット | `toMatchSnapshot()` | 組み込みに無い。syrupy などのプラグイン |
| ウォッチ | `--watch` | 組み込みに無い（§3.6） |
| カバレッジ | `--coverage` | pytest-cov の `--cov` |

---

## 3. 早見表

### 3.1 よく使うオプション

| オプション | 意味 | Vitest でいうと |
|---|---|---|
| `-q` / `-v` / `-vv` | 出力を減らす / テストごとに 1 行 / 差分を省略しない | `--reporter=dot` / `verbose` |
| `-x` / `--maxfail=N` | 最初の失敗で / N 回の失敗で止める | `--bail` |
| `--lf` / `--ff` | 前回失敗したものだけ / 失敗したものから先に（`.pytest_cache/` を使う） | — |
| `-k "式"` | 名前で絞る。`and` / `or` / `not` が書ける | `-t` |
| `-m "式"` | マーカーで絞る（`-m "not slow"`） | — |
| `-s` | 出力の捕捉を止める（`--capture=no`）。`print` がその場で出る | — |
| `--durations=N` | 遅い順に N 件（`--durations-min=0` で 0.005 秒未満も出す） | — |
| `--co -q` | 集めるだけで実行しない | `vitest list` |
| `--fixtures` / `--markers` | 使える fixture / マーカーの一覧 | — |
| `-n 4` / `-n auto` | pytest-xdist で並列に回す | 既定で並列（ファイル単位） |

通し課題（[Step 07](../steps/07-cli.md) の状態）のコピーに、わざと 2 件失敗するテストを足して、`-x` と `--lf` を続けて回す（検証済み）。足したのは `try/test_fail.py` の 3 件である。

```python
def test_ok() -> None:
    assert 1 + 1 == 2


def test_broken_a() -> None:
    assert sum([1, 2]) == 4


def test_broken_b() -> None:
    assert "faq".upper() == "FAQ!"
```

実行結果:

```text
$ uv run pytest -q -x try/test_fail.py
.F
…（中略: 12 行）…
1 failed, 1 passed in 0.38s
$ uv run pytest -q --lf try/test_fail.py
F                                                                        [100%]
…（中略: 11 行）…
1 failed, 2 deselected in 0.39s
```

`-x` で止めた後の `--lf` は、記録された 1 件だけを回す。止めた先の 2 件目は未実行で、記録されていない。並列実行は、13 件の通し課題ではかえって遅くなった（参考値。`uv run --with pytest-xdist==3.8.0 pytest -q -n 4 tests` が 2.18 秒、逐次は 0.53 秒）。ワーカーの起動に時間がかかるので、遅いテストが増えてから入れる。

### 3.2 fixture

- **scope** は `function`（既定。テストごと）・`class`・`module`（ファイル）・`package`（ディレクトリと、その下）・`session`（実行全体で 1 回。`globalSetup` に近い）の 5 つ。その単位の最後のテストの後で後片付けが走る
- **`autouse=True`** を付けると、引数に書かなくても範囲内の全テストに効く（`beforeEach` を上に書くのに近い）
- **`conftest.py` の階層**: 公式 docs は "each directory can have its own conftest.py with its own fixtures, adding on to the ones provided by the conftest.py files in parent directories." と書く。import せずに見え、深い方が同名の fixture を上書きする
- 組み込みの主な fixture: `tmp_path`（テストごとの一時ディレクトリ、`pathlib.Path`）・`tmp_path_factory`（session 用）・`monkeypatch`（属性・環境変数・カレントディレクトリの差し替え。テストの後に戻る）・`capsys`（標準出力）・`caplog`（logging）・`subtests`（pytest 9.0 で本体に入った。changelog は experimental と書く）

`yield` を使う fixture で、scope ごとの準備と後片付けの順番を見る（検証済み）。

```python
from collections.abc import Iterator

import pytest


@pytest.fixture(scope="module")
def db() -> Iterator[str]:
    print("\n[module] setup")  # beforeAll
    yield "db"
    print("\n[module] teardown")  # afterAll


@pytest.fixture
def tx(db: str) -> Iterator[str]:
    print("[function] setup")  # beforeEach
    yield f"{db}-tx"
    print("[function] teardown")  # afterEach


def test_one(tx: str) -> None:
    assert tx == "db-tx"


def test_two(tx: str) -> None:
    assert tx.startswith("db")
```

実行結果:

```text
$ uv run pytest -q -s try/test_scopes.py

[module] setup
[function] setup
.[function] teardown
[function] setup
.[function] teardown

[module] teardown

2 passed in 0.38s
```

組み込みと自作の fixture は、`uv run pytest --fixtures` で定義の場所と scope（`tmp_path_factory [session scope]` など）まで一覧できる（検証済み）。

### 3.3 マーカーと strict

`ids=` を付けた `parametrize` は、`-v` で `test_parse[http]` のように名前が出る。`-k "parse and not alt"` のように、その ID でも絞れる（検証済み）。

| 設定 | `strict = true` で有効になる | 効き目 |
|---|---|---|
| `strict_markers` | ○ | 登録していないマーカーを誤りにする（CLI では `--strict-markers`） |
| `strict_xfail` | ○ | `xfail` のテストが通ったら失敗にする（`XPASS(strict)`） |
| `strict_config` | ○ | 設定の読み込み中の警告（知らないキーなど）を誤りにする |
| `strict_parametrization_ids` | ○ | `parametrize` の ID の重複を誤りにする（無効なら `0`・`1` を付けて自動で区別する） |

`[tool.pytest.ini_options]` に strict を書かずに `@pytest.mark.slwo`（`slow` の打ち間違い）を付けると、`PytestUnknownMarkWarning: Unknown pytest.mark.slwo - is this a typo?` の警告だけで通った。同じものに `--strict-markers` を付けると、集める段階で止まる（検証で再現）。設定の形だけを試すため、ここでは `uvx` で pytest を単体で動かした。

実行結果:

```text
$ uvx pytest@9.2.0 -q -p no:cacheprovider --strict-markers
…（中略: 3 行）…
'slwo' not found in `markers` configuration option
=========================== short test summary info ============================
ERROR test_marker.py - Failed: 'slwo' not found in `markers` configuration op...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.04s
```

`strict = true` の下で通ってしまった `xfail` は、`FAILED test_xpass.py::test_fixed_already - [XPASS(strict)] bug #12` と失敗に数えられた（検証で再現）。直ったら `xfail` を外せ、という合図になる。

### 3.4 設定ファイル

| 書き場所 | 値の型 | 備考 |
|---|---|---|
| `pyproject.toml` の `[tool.pytest]` | TOML の型（配列・真偽値・整数） | pytest 9.0 から。推奨 |
| `pyproject.toml` の `[tool.pytest.ini_options]` | 文字列（INI 互換） | pytest 6.0 から。引き続き使える |
| `pytest.toml` / `.pytest.toml` の `[pytest]` | TOML の型 | pytest 9.0 から。空でも最優先で選ばれる |
| `pytest.ini` / `tox.ini` / `setup.cfg` | 文字列 | 従来の形式 |

マーカーは `markers = ["slow: takes more than a second"]` のように登録し、`-m "not slow"` で外せる（検証済み）。設定の全体の例は [Step 06](../steps/06-testing.md) §3.2 にある。

2 つの表を同じ `pyproject.toml` に書くと、テストを集める前に終了コード 4 で止まる（検証で再現）。

実行結果:

```text
$ uvx pytest@9.2.0 -q -p no:cacheprovider
Installed 5 packages in 11ms
ERROR: ~/proj/pyproject.toml: Cannot use both [tool.pytest] (native TOML types) and [tool.pytest.ini_options] (string-based INI format) simultaneously. Please use [tool.pytest] with native TOML types (recommended) or [tool.pytest.ini_options] for backwards compatibility.
```

### 3.5 import mode と src layout

| mode | `sys.path` | テストのファイル名 | テストどうしの import |
|---|---|---|---|
| `prepend`（既定） | テストのディレクトリを先頭に足す | `__init__.py` が無ければ重複できない | できる |
| `append` | 末尾に足す | 同上 | できる |
| `importlib` | 変えない | 重複してよい | できない（ヘルパーはパッケージ側か `conftest.py` に置く） |

- Good Integration Practices の原文: "For new projects, we recommend to use importlib import mode"。設定は `addopts = ["--import-mode=importlib"]`
- 一方で import mode の解説は "the default will remain prepend for the foreseeable future." と書く。既定が変わるのを待たず、使うなら明示する
- src layout は "Generally, but especially if you use the default import mode prepend, it is strongly suggested to use a src layout." とされる。`uv init` の既定の構成（`src/<名前>/`）はこの形である

`tests/api/test_utils.py` と `tests/cli/test_utils.py` を `__init__.py` 無しで置くと、既定の mode では 2 つ目が集められない（検証で再現）。

実行結果:

```text
$ uvx pytest@9.2.0 -q -p no:cacheprovider
…（中略: 3 行）…
import file mismatch:
…（中略: 4 行）…
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
…（中略: 3 行）…
1 error in 0.05s
$ uvx pytest@9.2.0 -q -p no:cacheprovider --import-mode=importlib
..                                                                       [100%]
2 passed in 0.01s
```

### 3.6 よく使うプラグイン（版は 2026-11-08 の PyPI）

| パッケージ | 用途 |
|---|---|
| pytest-cov 7.1.0 | coverage.py を pytest から使う（`--cov=pkg --cov-report=term-missing`） |
| pytest-xdist 3.8.0 | `-n` で複数プロセスに分けて回す。ウォッチ相当の `--looponfail` は 3.0.2 で非推奨になり、4.0 で削除の予定 |
| pytest-mock 3.17.0 | `mocker` fixture。docs: "The mocker fixture has the same API as mock.patch"。テストの後に自動で元に戻す |
| pytest-asyncio 1.4.1.post1 | `async def` のテストを asyncio で回す |
| AnyIO 4.16.0 の pytest プラグイン | AnyIO に同梱（追加の導入は不要）。`@pytest.mark.anyio` で asyncio / Trio の両方で回す（[Step 08](../README.md#4-学習ロードマップ)） |
| syrupy 6.1.1 | スナップショットテスト |

---

## 4. 推奨の使い方（2026-11）

| 推奨 | 理由 |
|---|---|
| `[tool.pytest]` に `testpaths`・`addopts`・`strict = true`・`markers` を書く | 型が TOML のまま扱え、マーカーの打ち間違いが誤りになる。公式 docs は strict を "you should only enable strict mode if you use a pinned/locked version of pytest" と条件付きで勧める。`uv.lock` があれば満たす |
| 後片付けは fixture の `yield` の後に書く | 公式 docs が "yield fixtures (recommended)" としている |
| 差し替えは、まず `monkeypatch` | 組み込みで、テストの後に必ず戻る（"All modifications will be undone after the requesting test function or fixture has finished."）。呼び出し回数を確かめたいときに `unittest.mock` か pytest-mock |
| `pytest.raises` には `match=` を付ける | 型だけだと、別の理由で投げられた同じ型の例外でも通る |

---

## 5. 代替との比較（標準ライブラリの unittest）

標準ライブラリの `unittest` は JUnit 型（`TestCase` を継承し、`setUp` と `self.assertEqual` を使う）で、追加の導入が要らない。CPython 本体や古いライブラリのテストで見かける。
pytest は "pytest supports running Python unittest-based tests out of the box." としており、既存の `TestCase` をそのまま集める（`TestLegacy::test_len PASSED` を確認、検証済み）。ただし `TestCase` の中では fixture（autouse を除く）と `parametrize` が使えない（公式 docs）。新しく書くテストは pytest の形にし、既存の `TestCase` は少しずつ移す。`unittest.mock` は `unittest` と切り離して pytest からも普通に使う。

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `Cannot use both [tool.pytest] ... and [tool.pytest.ini_options]`（検証で再現） | 2 つの表は同時に使えない | どちらかに寄せる。新しく書くなら `[tool.pytest]` |
| マーカーの打ち間違いが警告だけで通る（検証で再現） | strict でない | `strict = true`（または `strict_markers = true`）と `markers` の登録 |
| `-x` の後の `--lf` で、まだ失敗しているはずの 2 件目が回らない（検証中に発生） | `-x` で止めた先は実行されず、失敗として記録されていない | 一度 `-x` を外して全体を回すか、`--ff` で失敗を先に回す |
| `import file mismatch`（検証で再現） | 既定の `prepend` では、`__init__.py` の無いテストのファイル名が重複できない | ファイル名を変えるか、設定の `addopts = ["--import-mode=importlib"]` で import mode を変える（§3.5） |
| `print` が出ない | pytest が出力を捕捉している（失敗したテストの分だけ表示する） | `-s`。テストの中で確かめるなら `capsys` |
| `-n 4` にしたら遅くなった（検証中に発生、参考値） | ワーカーの起動の時間が、テストの時間より長い | 小さいテストでは使わない |

---

## 出典

| 情報源 | URL（確認日） |
|---|---|
| pytest — Good Integration Practices | https://docs.pytest.org/en/stable/explanation/goodpractices.html （2026-11-08、原文を curl で確認。`importlib` の推奨、src layout、strict mode の注意） |
| pytest — import mechanisms | https://docs.pytest.org/en/stable/explanation/pythonpath.html （2026-11-08、Context7 `/pytest-dev/pytest/9.2.0` と原文。3 つの mode、既定が `prepend` のままであること） |
| pytest — How to use fixtures / Fixtures reference | https://docs.pytest.org/en/stable/how-to/fixtures.html ・ https://docs.pytest.org/en/stable/reference/fixtures.html （2026-11-08。scope の定義、autouse、yield fixtures、`conftest.py` の階層） |
| pytest — Configuration / Changelog | https://docs.pytest.org/en/stable/reference/customize.html ・ https://docs.pytest.org/en/stable/changelog.html （2026-11-08。`[tool.pytest]`・`pytest.toml`、9.0.0 の 2 つの表の扱い、subtests） |
| pytest — assert / monkeypatch / unittest | https://docs.pytest.org/en/stable/how-to/assert.html ・ https://docs.pytest.org/en/stable/how-to/monkeypatch.html ・ https://docs.pytest.org/en/stable/how-to/unittest.html （2026-11-08。`match` は `re.search`、変更の巻き戻し、`TestCase` で使えない機能） |
| pytest-xdist — Changelog | https://github.com/pytest-dev/pytest-xdist/blob/master/CHANGELOG.rst （2026-11-08。3.0.2 で `--looponfail` が非推奨） |
| pytest-mock — Usage | https://pytest-mock.readthedocs.io/en/latest/usage.html （2026-11-08） |
| AnyIO — Testing with AnyIO | https://anyio.readthedocs.io/en/stable/testing.html （2026-11-08。プラグインが同梱であること） |
| PyPI の各パッケージ | https://pypi.org/project/syrupy/ ほか（2026-11-08。版と概要） |

### 確認できなかった事項

- **公式が勧めるウォッチの手段**。pytest 本体の `--help` に watch は無く、xdist の `--looponfail` は非推奨である。後継として公式に案内されている道具は見つけられなかったので、特定の道具は勧めていない
- **syrupy 以外のスナップショットのプラグインとの比較**。名前と用途だけを載せ、選び方は扱っていない

- 関連: [Python 学習ガイド](../README.md) / [Step 06: テスト](../steps/06-testing.md) / [Step 07: スクリプトと CLI](../steps/07-cli.md) / [uv](uv.md) / [pyproject.toml](pyproject-toml.md) / [Ruff](ruff.md) / [型チェッカーの比較](type-checkers.md)
