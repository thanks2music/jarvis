# Step 06: テスト — pytest で読み込みと検索を確かめる

> 出典（一次情報）:
> - [Good Integration Practices (docs.pytest.org)](https://docs.pytest.org/en/stable/explanation/goodpractices.html) — テストの見つけ方の規則、import mode の推奨、strict mode
> - [How to use fixtures (docs.pytest.org)](https://docs.pytest.org/en/stable/how-to/fixtures.html) — fixture の scope、`conftest.py` での共有、factory を返す fixture
> - [Writing plugins — conftest.py (docs.pytest.org)](https://docs.pytest.org/en/stable/how-to/writing_plugins.html) — `conftest.py` から import しないこと
> - [Configuration / Changelog 9.0.0 (docs.pytest.org)](https://docs.pytest.org/en/stable/reference/customize.html) — ネイティブな TOML の `[tool.pytest]`
> - [Hypothesis API reference (hypothesis.readthedocs.io)](https://hypothesis.readthedocs.io/en/latest/reference/api.html) — `@given` と `HealthCheck.function_scoped_fixture`
> - [pytest-cov Configuration (pytest-cov.readthedocs.io)](https://pytest-cov.readthedocs.io/en/latest/config.html) — `--cov` と `--cov-report`
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・pytest 9.2.0・pytest-cov 7.1.0・Hypothesis 6.170.15 で検証）

Node.js / Bun では、Vitest・Jest・`bun test` で `describe` / `it` / `expect` を書き、`beforeEach` で準備し、`test.each` で表を回す。
Python の標準は **pytest** である。テストは `test_` で始まる普通の関数で、確かめるのは素の `assert` 文、準備は **fixture**（引数の名前で注入される関数）、表は `@pytest.mark.parametrize` で書く。
このステップでは、[Step 05: 品質ツール](05-quality.md) の `faq-app` に `tests/` を足し、読み込み・検証エラー・検索・`main()` の出力をテストし、Hypothesis で性質を確かめ、カバレッジを測る。
シリーズ全体は [Python 学習ガイド](../README.md)、次は [Step 07: スクリプトと CLI](07-cli.md)。コマンドと設定の早見表は [pytest](../topics/pytest.md) にある。

---

## 1. TL;DR

- **`uv add --dev pytest pytest-cov hypothesis` で入れ、`uv run pytest` で回す**。`uvx pytest` ではプロジェクトの依存が見えない（§3.1）。
- **期待値は素の `assert` で書く**。pytest が `assert` 文を書き換え、失敗したときに `assert 3 == 4` と中間の値まで表示する。matcher の API は要らない（§3.5）。
- **共有の準備は `tests/conftest.py` の fixture に置き、テストは引数で受け取る**。`conftest.py` から import すると `ModuleNotFoundError: No module named 'tests'` で落ちた（検証中に発生、§3.3）。
- **設定は `[tool.pytest]`**（pytest 9 からのネイティブな TOML）に書き、`strict = true` で登録していないマーカーなどを誤りにする（§3.2）。
- **Hypothesis の `@given` に function スコープの fixture（`tmp_path` など）を渡さない**。入力ごとに作り直されないので、health check で止まる（§3.7）。
- カバレッジは `--cov=faq --cov-report=term-missing` で 93%。mypy の対象に `tests` も足す（§3.8）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Vitest / Jest / `bun test` | pytest |
|---|---|---|
| テストを書く | `it("...", () => { ... })` / `test(...)` | `def test_xxx() -> None:` |
| 期待値を確かめる | `expect(a).toBe(b)` / `toEqual` | `assert a == b`（`==` は値の比較。`toEqual` に近い） |
| 例外を確かめる | `expect(() => f()).toThrow(E)` | `with pytest.raises(E):` |
| 毎テストの準備と後片付け | `beforeEach` / `afterEach` | function スコープの fixture（`yield` の後が後片付け） |
| 一度だけの準備 | `beforeAll` | `@pytest.fixture(scope="session")` など |
| 共有の準備を置く場所 | `setupFiles` / ヘルパーを import | `tests/conftest.py`（import しない。自動で読まれる） |
| 表でまとめて回す | `test.each([...])` | `@pytest.mark.parametrize(...)` |
| 名前で絞る | `-t <pattern>` | `-k <式>`（`and` / `or` / `not` が使える） |
| 関数や環境を差し替える | `vi.spyOn` / `vi.stubEnv` / `vi.mock` | `monkeypatch.setattr` / `setenv` / `chdir` |
| 性質ベースのテスト | fast-check | Hypothesis（`@given`） |
| カバレッジ | `--coverage` / `bun test --coverage` | pytest-cov（`--cov`。中身は coverage.py） |

---

## 3. ハンズオン

[Step 05](05-quality.md) の `faq-app/` で作業する。テストは `tests/` に置き、`tests/` には `__init__.py` を置かない。

### 3.1 テストの道具を入れる

pytest・pytest-cov・Hypothesis を dev グループに入れる（検証済み）。

実行結果:

```text
$ uv add --dev pytest pytest-cov hypothesis
Resolved 37 packages in 553ms
…（中略: 5 行）…
 + coverage==7.17.2
 ~ faq==0.1.0 (from file:///path/to/faq-app)
 + hypothesis==6.170.15
 + iniconfig==2.3.1
 + packaging==26.3
 + pluggy==1.7.0
 + pytest==9.2.0
 + pytest-cov==7.1.0
 + sortedcontainers==2.4.0
```

pytest-cov は coverage.py を pytest から動かすプラグインで、`coverage` も一緒に入った。pytest は `uv run pytest` で動かす。uv の公式 docs は "If the tool should not be isolated from the project, e.g., when running `pytest` or `mypy`, then `uv run` should be used instead of `uv tool run`." と書き、pytest の公式の手順も uv では `uv sync` → `uv run pytest` である。

### 3.2 pytest の設定を `[tool.pytest]` に書く

`pyproject.toml` に設定を足し、mypy の対象にも `tests` を加える（抜粋・単体では動かない）。

```toml
[tool.mypy]
files = ["src", "tests"]
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest]
testpaths = ["tests"]
addopts = ["-ra"]
strict = true
```

- `[tool.pytest]` は pytest 9.0 からの**ネイティブな TOML** の表で、値を TOML の型（配列・真偽値）で書く。従来の `[tool.pytest.ini_options]` は値を文字列として扱う INI 互換モードで、changelog は "The `[tool.pytest.ini_options]` table remains supported, but both tables cannot be used at the same time." と書いている
- `testpaths` は引数なしの `pytest` が探し始める場所、`-ra` は通った以外のテスト（失敗・skip など）を最後に一覧する指定
- `strict = true` は `strict_config`・`strict_markers`・`strict_parametrization_ids`・`strict_xfail` をまとめて有効にする

登録していないマーカー `@pytest.mark.slow` を付けたテストで、strict の効き目を確かめる（検証で再現）。`-p no:cacheprovider` はキャッシュを残さないための指定で、結果には関係しない。

実行結果:

```text
$ uv run pytest -q try/test_marker.py -p no:cacheprovider
…（中略: 3 行）…
'slow' not found in `markers` configuration option
=========================== short test summary info ============================
ERROR try/test_marker.py - Failed: 'slow' not found in `markers` configuratio...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.42s
```

strict でないと、`@pytest.mark.slwo` のような打ち間違いも警告だけで素通りする。使うマーカーは `markers = ["slow: 遅いテスト"]` のように登録する。公式 docs は "you should only enable strict mode if you use a pinned/locked version of pytest" とも注意している（新しい版で増えた検査も有効になるため）。`uv.lock` で版を固定しているので条件を満たす。

### 3.3 共有の fixture を `conftest.py` に置く

`tests/conftest.py` を作る（検証済み）。

```python
from collections.abc import Callable
from pathlib import Path

import pytest

from faq import Faq, load_faqs


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent.parent / "data" / "faq.jsonl"


@pytest.fixture(scope="session")
def faqs(data_path: Path) -> list[Faq]:
    return load_faqs(data_path)  # Faq は frozen なので、テストの間で使い回してよい


@pytest.fixture
def write_jsonl(tmp_path: Path) -> Callable[..., Path]:
    def _write(*lines: str) -> Path:
        path = tmp_path / "faq.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    return _write
```

- **scope** は作り直す頻度を決める。既定の `function` はテストごと、`session` は実行全体で 1 回。読むだけの `data_path` と `faqs` は `session` にした（`beforeAll` にあたる）
- fixture は別の fixture を引数で受け取れる。`write_jsonl` は組み込みの `tmp_path`（テストごとに別の一時ディレクトリ）を受け取り、値ではなく**関数を返す**。公式 docs が "factory as fixture" と呼ぶ形で、テストの中で好きな中身のファイルを何度でも作れる
- テスト側は `def test_loads_all_faqs(faqs: list[Faq]) -> None:` のように、名前で受け取るだけでよい

最初は、データのパスを `conftest.py` に定数 `DATA` として置き、`tests/test_main.py` から import していた。その結果（検証中に発生）。

実行結果:

```text
$ uv run pytest
…（中略: 5 行）…
collected 10 items / 1 error

==================================== ERRORS ====================================
_____________________ ERROR collecting tests/test_main.py ______________________
ImportError while importing test module '~/faq-app/tests/test_main.py'.
…（中略: 5 行）…
tests/test_main.py:7: in <module>
    from tests.conftest import DATA
E   ModuleNotFoundError: No module named 'tests'
…（中略: 3 行）…
=============================== 1 error in 0.93s ===============================
```

- 既定の import mode（`prepend`）は、`__init__.py` の無いディレクトリのテストを読むとき、**そのディレクトリ（`tests/`）を `sys.path` の先頭に足す**。プロジェクトのルートは足さないので、`tests` というパッケージは見つからない。`pytest` コマンドは、`python -m pytest` と違ってカレントディレクトリも足さない（公式 docs: "calling via `python` will also add the current directory to `sys.path`"）
- 公式 docs は "It is thus good practice for projects to either put `conftest.py` under a package scope or to never import anything from a `conftest.py` file." と書いている。通し課題は**定数をやめて `data_path` の fixture にした**

直した後、全体が通った（検証済み）。

実行結果:

```text
$ uv run pytest
…（中略: 10 行）…
collected 11 items
…（中略: 5 行）…
============================== 11 passed in 0.44s ==============================
```

> **ポイント**: pytest の公式は、新しいプロジェクトに `importlib` の import mode を推奨している（"For new projects, we recommend to use `importlib` import mode"）。`sys.path` を変えないモードで、通し課題のテストも `uv run pytest --import-mode=importlib` でそのまま 11 件通った。採用するなら `addopts` に `"--import-mode=importlib"` を足す。

### 3.4 検証エラーを `parametrize` と `pytest.raises` で確かめる

`tests/test_loader.py` に、空行を飛ばすことと 3 種の不正な値が弾かれることを書く。import（`json`・`Callable`・`Path`・`pytest`・`ValidationError`・`Faq`・`load_faqs`）と冒頭の `test_loads_all_faqs`（件数と先頭の `id`）は省いて載せる（抜粋・単体では動かない）。

```python
VALID = {
    "id": "faq-01",
    "category": "経費",
    "question": "締め日は？",
    "answer": "25 日",
}


def test_skips_blank_lines(write_jsonl: Callable[..., Path]) -> None:
    path = write_jsonl(json.dumps(VALID, ensure_ascii=False), "", "  ")
    assert load_faqs(path) == [Faq(**VALID)]


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("category", "経理", "literal_error"),
        ("question", "", "string_too_short"),
        ("id", "faq-1", "string_pattern_mismatch"),
    ],
)
def test_rejects_invalid_values(
    write_jsonl: Callable[..., Path], field: str, value: str, error_type: str
) -> None:
    path = write_jsonl(json.dumps({**VALID, field: value}, ensure_ascii=False))
    with pytest.raises(ValidationError) as exc_info:
        load_faqs(path)
    assert exc_info.value.errors()[0]["type"] == error_type
```

- `parametrize` の第 1 引数は引数名の組、第 2 引数は値の組のリストで、1 組ごとに別のテストになる。`{**VALID, field: value}` は JS の `{ ...VALID, [field]: value }` にあたる
- Pydantic の `ValidationError.errors()` は、誤りごとに `type`・`loc`・`msg`・`input` などを持つ辞書のリストを返す。**文言ではなく機械向けの `type` を比べる**と、版が上がって文言が変わっても壊れない

`-v` を付けると、`parametrize` で生まれたテストが ID 付きで並ぶ（検証済み）。

実行結果:

```text
$ uv run pytest -v
…（中略: 12 行）…
tests/test_loader.py::test_rejects_invalid_values[category-\u7d4c\u7406-literal_error] PASSED [ 27%]
tests/test_loader.py::test_rejects_invalid_values[question--string_too_short] PASSED [ 36%]
tests/test_loader.py::test_rejects_invalid_values[id-faq-1-string_pattern_mismatch] PASSED [ 45%]
…（中略: 7 行）…
============================== 11 passed in 0.44s ==============================
```

ID は値をハイフンでつないで作られ、**日本語は `\u7d4c\u7406` のようにエスケープされる**。公式 docs: "pytest by default escapes any non-ascii characters used in unicode strings for the parametrization because it has several downsides." 読みやすい ID が要るなら、`ids=[...]` か `pytest.param(..., id="bad-category")` で ASCII の名前を付ける。

### 3.5 `assert` が失敗したときの表示

`IT` の期待値をわざと 4 に変えたコピーで、`-k IT` で 1 件だけ回した（検証で再現）。

実行結果:

```text
$ uv run pytest tests/test_search.py -k IT
…（中略: 10 行）…
collected 5 items / 4 deselected / 1 selected
…（中略: 4 行）…
________________________ test_by_category_counts[IT-4] _________________________
…（中略: 2 行）…
category = 'IT', expected = 4

    @pytest.mark.parametrize(("category", "expected"), [("IT", 4), ("出張", 1), ("経費", 2)])
    def test_by_category_counts(faqs: list[Faq], category: Category, expected: int) -> None:
>       assert len(by_category(faqs, category)) == expected
E       AssertionError: assert 3 == 4
…（中略: 3 行）…
tests/test_search.py:21: AssertionError
```

- 素の `assert` なのに、両辺の値（`3 == 4`）と引数の値が出る。pytest が**テストモジュールの `assert` 文を実行前に書き換えて**、途中の値を記録しているからである。省いた行には `+  where 3 = len([...])` と `by_category(...)` の戻り値まで出ている
- 書き換えは、pytest が集めたテストモジュールと `conftest.py`（とプラグイン）だけに効く。公式 docs: "asserts in supporting modules which are not themselves test modules will not be rewritten"

### 3.6 カレントディレクトリと標準出力を差し替える

`faq.main()` はカレントディレクトリの `data/faq.jsonl` を読み、件数を `print` する。`tests/test_main.py` で、一時ディレクトリに移って出力を確かめる（検証済み）。

```python
import shutil
from pathlib import Path

import pytest

from faq import main


def test_main_prints_count(
    data_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "data").mkdir()
    shutil.copy(data_path, tmp_path / "data" / "faq.jsonl")
    monkeypatch.chdir(tmp_path)  # main() はカレントディレクトリの data/ を読む
    main()
    assert capsys.readouterr().out == "12 件の FAQ を読み込んだ\n"
```

- `monkeypatch` は組み込みの fixture で、`chdir`・`setattr`・`setenv` などの変更を**テストが終わると元に戻す**。`vi.restoreAllMocks()` にあたる後片付けを書かなくてよい
- `capsys.readouterr()` は、そこまでの標準出力と標準エラーを取り出す。`.out` が標準出力である

### 3.7 Hypothesis で性質を確かめる

`tests/test_search.py` には、ID での検索（`find_by_id`）とカテゴリごとの件数（§3.5 の `parametrize`）に加えて、「`by_category` が返すのはそのカテゴリだけ」という性質を書く。その部分を載せる（抜粋・単体では動かない）。

```python
from hypothesis import given
from hypothesis import strategies as st

CATEGORIES: list[Category] = ["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]


@given(category=st.sampled_from(CATEGORIES))
def test_by_category_returns_only_that_category(
    faqs: list[Faq], category: Category
) -> None:
    result = by_category(faqs, category)
    assert all(faq.category == category for faq in result)
```

- `@given` は、strategy（ここでは 6 つのカテゴリから選ぶ `st.sampled_from`）が作る入力でテストを何度も呼ぶ。fast-check の `fc.assert(fc.property(...))` にあたる。`@given` の引数と fixture の引数は同じ関数に並べられる
- `CATEGORIES` は `Category` の値を写したものなので、カテゴリを増やしても追従しない。`list(get_args(Category.__value__))`（[Step 04](04-typing.md) の §5）で引けば、写し忘れが起きない

`faqs` を session スコープにしたのには理由がある。function スコープの fixture を `@given` のテストに渡すと、Hypothesis が止める。`tmp_path` を受け取るテストで確かめた（検証済み）。

```python
from hypothesis import given
from hypothesis import strategies as st


@given(n=st.integers(min_value=1, max_value=3))
def test_writes_lines(tmp_path, n):  # tmp_path は function スコープ
    path = tmp_path / "faq.jsonl"
    path.write_text("x\n" * n, encoding="utf-8")
    assert len(path.read_text(encoding="utf-8").splitlines()) == n
```

実行結果:

```text
$ uv run pytest try/test_health.py -p no:cacheprovider
…（中略: 12 行）…
E   hypothesis.errors.FailedHealthCheck: 'try/test_health.py::test_writes_lines' uses a function-scoped fixture 'tmp_path'.

    Function-scoped fixtures are not reset between inputs generated by `@given(...)`, which is often surprising and can cause subtle test bugs.
…（中略: 7 行）…
============================== 1 failed in 0.91s ===============================
```

- function スコープの fixture は、**生成された入力ごとではなく、テスト関数 1 回につき 1 回**しか作られない。入力ごとに空の `tmp_path` が来ると思って書くと、前の入力のファイルが残る
- 省いた行は、入力ごとの準備をテストの中の context manager で作るよう勧め、問題が無いと確信できる場合だけ `@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])` で黙らせられると案内している。公式 docs はこれを性能ではなく正しさの問題として扱う: "We recommend treating these particular health checks with more care, as suppressing them may result in an unsound test."

### 3.8 カバレッジを測り、テストのコードも品質ツールにかける

pytest-cov でカバレッジを測る（検証済み）。

実行結果:

```text
$ uv run pytest --cov=faq --cov-report=term-missing
…（中略: 14 行）…

Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
src/faq/__init__.py       7      0   100%
src/faq/__main__.py       2      2     0%   1-3
src/faq/loader.py         5      0   100%
src/faq/models.py         8      0   100%
src/faq/search.py         6      0   100%
---------------------------------------------------
TOTAL                    28      2    93%
============================== 11 passed in 0.49s ==============================
```

`--cov=faq` は測る対象のパッケージ、`term-missing` は通らなかった行番号も出す指定である。0% の `__main__.py` は `python -m faq` の入口で、テストから呼んでいない。下限を決めるなら `--cov-fail-under=90` で、下回ったときに失敗にできる。

テストのコードも Ruff と mypy にかける。`ruff check` は通ったが、`ruff format --check` が自分で書いたテスト 3 ファイルを指摘した（検証中に発生）。

実行結果:

```text
$ uv run ruff format --check
unformatted: File would be reformatted
  --> tests/test_loader.py:10:10
…（中略: 32 行）…
  --> tests/test_search.py:19:26
   |
18 |
   - @pytest.mark.parametrize(("category", "expected"), [("IT", 3), ("出張", 1), ("経費", 2)])
19 + @pytest.mark.parametrize(
20 +     ("category", "expected"), [("IT", 3), ("出張", 1), ("経費", 2)]
21 + )
…（中略: 10 行）…
3 files would be reformatted, 9 files already formatted
```

1 行が 88 文字（Ruff の既定の `line-length`）を超えた `parametrize` や引数の並びを、折り返すよう求めている。`uv run ruff format` で直すと `3 files reformatted` となり、その後も `uv run pytest -q` は 11 件通り、`uv run mypy` は `Success: no issues found in 9 source files` を返した（検証済み）。本ステップのコード例は整形後のものである。

`9 source files` は `src/faq/` の 5 つと `tests/` の 4 つである。strict の mypy は型の無い関数を報告するので、テスト関数にも `-> None` と引数の型（`pytest.MonkeyPatch`・`pytest.CaptureFixture[str]` など）を付けた。

> **ポイント**: 非同期の関数のテスト（pytest-asyncio・AnyIO のプラグイン）は [Step 08: 非同期と並行処理](../README.md#4-学習ロードマップ) で扱う。

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| `uv run pytest` で回す | `uvx pytest`・グローバルの pytest | 隔離された環境ではプロジェクトの依存が見えない（uv の公式 docs、§3.1） |
| 設定は `[tool.pytest]` に TOML の型で書き、`strict = true` を付ける | `[tool.pytest.ini_options]` と併記する・マーカーの打ち間違いを警告のまま流す | 2 つの表は同時に使えない（pytest 9.0 の changelog）。strict は pytest の版を `uv.lock` で固定して使う（§3.2） |
| 共有の準備は `conftest.py` の fixture にし、引数で受け取る | `conftest.py` から定数やヘルパーを import する | 公式 docs が "never import anything from a `conftest.py` file" を勧めている。import mode によっては import できない（§3.3） |
| 新しいプロジェクトでは `--import-mode=importlib` を検討する | `tests/` のヘルパーをテストどうしで import し合う | 公式の推奨。`sys.path` を変えず、テストのファイル名が重複してもよい。ただし既定は今後も `prepend` のままである（[pytest の import の仕組みの解説](https://docs.pytest.org/en/stable/explanation/pythonpath.html): "the default will remain prepend for the foreseeable future"） |
| 重い読み込みは広い scope の fixture で 1 回にし、中身は書き換えない | session スコープのリストをテストの中で `append` / `sort` する | 次のテストに変更が漏れる。`Faq` は frozen だが、`list[Faq]` 自体は変更できる |
| 検証エラーは `errors()[0]["type"]` で比べる | `str(exc)` の文言を比べる | `type` は機械向けの識別子である（Pydantic の docs） |
| Hypothesis では入力ごとの準備をテストの中で作る | `suppress_health_check` で function スコープの警告を黙らせる | 正しくないテストになりうる（Hypothesis の docs、§3.7） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `from tests.conftest import DATA` が `ModuleNotFoundError: No module named 'tests'`（検証中に発生） | 既定の import mode は `tests/` 自体を `sys.path` に足すだけで、`tests` はパッケージにならない。`pytest` はカレントディレクトリも足さない | `conftest.py` から import せず、fixture で渡す（§3.3） |
| `ruff format --check` がテスト 3 ファイルを指摘した（検証中に発生） | 長い `parametrize` や引数の並びが 88 文字を超えた | `uv run ruff format` で直す。pre-commit に入れておけば commit の前に直る（[Step 05](05-quality.md)） |
| `-v` の ID が `\u7d4c\u7406` のように読めない（検証中に発生） | pytest は `parametrize` の ID の非 ASCII 文字を既定でエスケープする | `ids=` か `pytest.param(..., id="...")` で ASCII の ID を付ける |
| `git status` に `.coverage` が出る（検証中に発生） | pytest-cov が測定のデータを書く。`.pytest_cache/` と `.hypothesis/` は中に `*` だけの `.gitignore` を自分で置くが、`.coverage` には無い。`uv init` の `.gitignore` にも入っていない | `.gitignore` に `.coverage` を足す |
| `FailedHealthCheck: ... uses a function-scoped fixture 'tmp_path'`（検証で再現） | `@given` のテストに function スコープの fixture を渡した | 入力ごとの準備はテストの中で作るか、読むだけの fixture を広い scope にする（§3.7） |
| `'slow' not found in markers configuration option`（検証で再現） | `strict = true` で、登録していないマーカーが誤りになった | `[tool.pytest]` の `markers` に登録する |
| `fixture 'faq' not found`（検証で再現） | fixture は引数名で引くので、1 文字違えば見つからない。また `tests/conftest.py` の fixture は `tests/` の下のテストにしか見えない。`tests/` の外に置いたテストでは、一覧（`available fixtures:`）に `faqs` も `data_path` も出なかった | 名前を直し、テストは `tests/` の下に置く。使える fixture は `uv run pytest --fixtures` で一覧できる |

---

## 6. 次のステップ

- [Step 07: スクリプトと CLI](07-cli.md) — Typer で `faq search` と `faq stats` を作り、`CliRunner` でテストする
- コマンドと設定を一覧で見たい場合は [pytest](../topics/pytest.md)、`ValidationError` の扱いは [Pydantic](../topics/pydantic.md)

---

## 出典

| 情報源 | URL |
|---|---|
| pytest — Good Integration Practices | https://docs.pytest.org/en/stable/explanation/goodpractices.html （2026-11-08 確認、Context7 `/pytest-dev/pytest/9.2.0` と GitHub の `doc/en` の原文。発見の規則、uv での手順、`importlib` の推奨、strict mode） |
| pytest — How to use fixtures / Writing plugins / import mechanisms | https://docs.pytest.org/en/stable/how-to/fixtures.html ・ https://docs.pytest.org/en/stable/how-to/writing_plugins.html ・ https://docs.pytest.org/en/stable/explanation/pythonpath.html （2026-11-08 確認。scope の種類、"Factories as fixtures"、`conftest.py` から import しないこと、`prepend` が既定であること、`python -m pytest` との違い） |
| pytest — Configuration / Reference / Changelog 9.0.0 | https://docs.pytest.org/en/stable/reference/customize.html ・ https://docs.pytest.org/en/stable/reference/reference.html ・ https://docs.pytest.org/en/stable/changelog.html （2026-11-08 確認。`[tool.pytest]`、`strict` が有効にする 4 つの設定と注意） |
| pytest — assert / parametrize / monkeypatch / capture / tmp_path | https://docs.pytest.org/en/stable/how-to/assert.html ・ https://docs.pytest.org/en/stable/how-to/parametrize.html ・ https://docs.pytest.org/en/stable/how-to/monkeypatch.html ・ https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html ・ https://docs.pytest.org/en/stable/how-to/tmp_path.html （2026-11-08 確認。assert の書き換えの範囲、ID のエスケープ、変更の巻き戻し） |
| Hypothesis — API reference（HealthCheck） | https://hypothesis.readthedocs.io/en/latest/reference/api.html （2026-11-08 確認。`function_scoped_fixture` が正しさの health check であること） |
| pytest-cov — Configuration / Reporting | https://pytest-cov.readthedocs.io/en/latest/config.html ・ https://pytest-cov.readthedocs.io/en/latest/reporting.html （2026-11-08 確認。`--cov`・`--cov-report`・`--cov-fail-under`） |
| Pydantic — Validation Errors | https://docs.pydantic.dev/latest/errors/errors/ （2026-11-08 確認、Context7 `/pydantic/pydantic/v2.14.1` 経由。`errors()` の各項目） |
| uv — Tools | https://docs.astral.sh/uv/concepts/tools/ （2026-11-08 確認。pytest を `uv run` で動かす理由） |

### 確認できなかった事項

- **`.coverage` を `.gitignore` に入れるべきだと明記した公式 docs**。coverage.py と pytest-cov の docs では見つけられなかった。`.pytest_cache/` と `.hypothesis/` が自分で `.gitignore` を置き、`.coverage` には無いことを実測しただけである

- 関連: [Python 学習ガイド](../README.md) / [Step 05: 品質ツール](05-quality.md) / [Step 07: スクリプトと CLI](07-cli.md) / [pytest](../topics/pytest.md) / [Pydantic](../topics/pydantic.md) / [uv](../topics/uv.md)
