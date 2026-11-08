# Step 10: データ処理 — 問い合わせログを Polars・pandas・DuckDB で集計する

> 出典（一次情報）:
> - [Polars user guide — Lazy API・Coming from pandas (docs.pola.rs)](https://docs.pola.rs/user-guide/concepts/lazy-api/) — 式・lazy API・pandas との違い
> - [What's new in 3.0.0 (pandas.pydata.org)](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) — 既定の文字列型 `str` と Copy-on-Write
> - [DuckDB Python client (duckdb.org)](https://duckdb.org/docs/2.0/clients/python/overview.html) と [Data Ingestion](https://duckdb.org/docs/2.0/clients/python/data_ingestion.html)・[Integration with Polars](https://duckdb.org/docs/2.0/guides/python/polars.html)・[CSV Auto Detection](https://duckdb.org/docs/2.0/data/csv/auto_detection.html)
> - [What is NumPy? (numpy.org)](https://numpy.org/doc/stable/user/whatisnumpy.html)
> - [marimo docs — FAQ・CLI・Outputs (docs.marimo.io)](https://docs.marimo.io/faq.html) と [Using uv with Jupyter (docs.astral.sh)](https://docs.astral.sh/uv/guides/integration/jupyter/)
> - [mypy — Missing imports](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports) と [pandas-stubs (GitHub)](https://github.com/pandas-dev/pandas-stubs)
>
> 最終更新: 2026-11-09（Python 3.15.2・uv 0.13.7・Polars 2.1.0・pandas 3.1.1・DuckDB 2.0.0・NumPy 2.5.4・PyArrow 26.0.1・marimo 0.25.2 で検証）

JavaScript / TypeScript では、表のデータを配列とオブジェクトのまま `reduce` で集計することが多く、定番の DataFrame は無い。
Python には列ごとに型を持つ表（DataFrame）のライブラリが複数あり、**Polars**（式と lazy API）・**pandas**（最も広く使われてきた DataFrame）・**DuckDB**（プロセス内で動く SQL エンジン）を目的で使い分ける。
このステップでは、通し課題に決まった内容の問い合わせログ（CSV）を作り、月 × カテゴリの集計を 3 つの方法で書いて結果の一致をテストで固定し、marimo のノートブックで眺める。
前は [Step 09: Web API](09-web-api.md)、全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **新しく書く集計は Polars の lazy API が第一候補**。`scan_csv()` → `group_by()` → `agg()` と計画を組み、`collect()` で初めて実行する。使わない列は読まれない（§3.3）。
- **pandas 3 は文字列の列が `str` 型になり、Copy-on-Write だけになった**。連鎖代入（`df["a"][mask] = ...`）は効かないので、1 回の `.loc[...]` で書く（§3.4）。
- **SQL で書くなら DuckDB**。CSV・Parquet はファイル名、Polars / pandas の DataFrame は変数名のまま `FROM` に書ける。DataFrame を読むには PyArrow が要る（§3.5）。
- **3 つの集計は同じ結果になった**。小さな CSV を `tmp_path` に書き、`parametrize` で 3 つの関数に同じ期待値を当てる（§3.6）。
- **mypy strict で引っかかるのは pandas だけ**。Polars・DuckDB・NumPy は `py.typed` を同梱し、pandas は `pandas-stubs` を dev に足す（§3.7）。
- **marimo のノートブックは素の `.py`** で、依存するセルだけが自動で再実行される。`marimo run --headless --port 2718` でアプリとして動く（§3.8）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js / Bun | Python |
|---|---|---|
| 表のデータを集計する | 配列 + `reduce` / `Object.groupBy` | Polars / pandas の `group_by` / `groupby` |
| 計画を組んでから実行する | 標準の対応物は無い | Polars の `LazyFrame` と `collect()` |
| SQL でファイルを直接集計する | DuckDB の Node クライアント | DuckDB（`FROM 'data.csv'`） |
| 数値の配列をまとめて計算する | `Float64Array` などの TypedArray | NumPy の `ndarray` |
| 乱数の種を固定する | 標準には無い（`Math.random()` は種を取れない） | `random.Random(seed)` |
| ノートブック | 一般的ではない | Jupyter（`.ipynb`）/ marimo（`.py`） |
| ライブラリの型 | 本体同梱か `@types/*` | 本体同梱（`py.typed`）か `*-stubs`（例 `pandas-stubs`） |

---

## 3. ハンズオン

[Step 07](07-cli.md) までの `faq-app/` を使う。確かめ用のスクリプト（`../demos/*.py`）は通し課題の外に置き、`faq-app/` の環境で動かした。

### 3.1 ライブラリを足し、3.15 用の wheel があるかを確かめる

**狙い**: 重いライブラリがソースからのビルド（C / Rust のツールチェーンが要る）にならないかを知る。`uv add polars pandas duckdb` で、NumPy も pandas の依存として入った。入った wheel のタグを見た（検証済み）。

実行結果:

```text
$ cd .venv/lib/python3.15/site-packages && grep -H "^Tag:" duckdb-*/WHEEL numpy-*/WHEEL pandas-*/WHEEL polars-*/WHEEL polars_runtime_32-*/WHEEL
duckdb-2.0.0.dist-info/WHEEL:Tag: cp312-abi3-macosx_11_0_arm64
numpy-2.5.4.dist-info/WHEEL:Tag: cp315-cp315-macosx_14_0_arm64
pandas-3.1.1.dist-info/WHEEL:Tag: cp315-cp315-macosx_11_0_arm64
polars-2.1.0.dist-info/WHEEL:Tag: py3-none-any
polars_runtime_32-2.1.0.dist-info/WHEEL:Tag: cp311-abi3-macosx_11_0_arm64
```

- `cp315-cp315` は 3.15 専用、`cp312-abi3` は「3.12 以上の安定 ABI」で 3.15 でも使える。Polars は Python 部分と Rust の本体（`polars-runtime-32`）に分かれている。後で足す PyArrow 26.0.1 も `cp315-cp315`、marimo と pandas-stubs は `py3-none-any` で、どれもビルドは起きていない
- free-threaded 版（`python3.15t`）は abi3 の wheel を使えず、Polars と DuckDB には 2026-11-08 時点で 3.15t 用の wheel が無い（[Python の版の選び方](../topics/python-versions.md)）

### 3.2 決まった内容の問い合わせログを作る

**狙い**: 何度実行しても同じ CSV を作り、集計を比べる土台にする。`scripts/gen_inquiries.py` は標準ライブラリだけで書く（検証済み）。

```python
"""data/faq.jsonl を元に、問い合わせログの CSV を決まった内容で作る。"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20261109
ROWS = 1500
START = date(2026, 1, 1)
DAYS = 181  # 2026-01-01〜2026-06-30

faqs = [
    json.loads(line)
    for line in Path("data/faq.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
rng = random.Random(SEED)  # 自前の乱数生成器。グローバルの random を汚さない
rows = []
for _ in range(ROWS):
    faq = rng.choice(faqs)
    day = START + timedelta(days=rng.randrange(DAYS))
    resolved = "yes" if rng.random() < 0.8 else "no"
    rows.append((day.isoformat(), faq["category"], faq["id"], resolved))
rows.sort()

out = Path("data/inquiries.csv")
with out.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "category", "faq_id", "resolved"])
    writer.writerows(rows)
print(f"{out} に {len(rows)} 行を書いた")
```

実行結果:

```text
$ shasum -a 256 data/inquiries.csv && uv run python scripts/gen_inquiries.py && shasum -a 256 data/inquiries.csv
a1e981e983b6ddd4314be6bd6e12393b874eb5d58382b90796f4c27577ac8ff8  data/inquiries.csv
data/inquiries.csv に 1500 行を書いた
a1e981e983b6ddd4314be6bd6e12393b874eb5d58382b90796f4c27577ac8ff8  data/inquiries.csv
```

- 作り直してもハッシュが変わらない。先頭行は `2026-01-01,IT,faq-05,yes` のような形になる。`random.Random(SEED)` は専用の生成器で、他のコードの `random.seed()` に影響されない
- ただし同じ種で同じ列になるのは**同じ Python の版の中だけ**と考える。docs: "Most of the random module's algorithms and seeding functions are subject to change across Python versions"。版をまたいで保証されるのは `random()` の列だけで、`choice()` や `randrange()` は含まれない。だから CSV（約 46KB）もコミットし、スクリプトは作り直す手段として残す

### 3.3 Polars: 式と lazy API

**狙い**: 月 × カテゴリの件数と解決数を、計画を組んでから 1 回で実行する形で書く。`src/faq/analytics.py` の前半（検証済み）。

```python
"""問い合わせログ（data/inquiries.csv）を月 × カテゴリで集計する。"""

from pathlib import Path

import duckdb
import pandas as pd
import polars as pl

type Row = tuple[str, str, int, int]  # (月, カテゴリ, 件数, 解決数)


def monthly_polars(path: Path) -> list[Row]:
    df = (
        pl.scan_csv(path, try_parse_dates=True)  # まだ読まない（LazyFrame）
        .group_by(pl.col("date").dt.strftime("%Y-%m").alias("month"), "category")
        .agg(
            pl.len().alias("inquiries"),
            (pl.col("resolved") == "yes").sum().alias("resolved"),
        )
        .sort("month", "category")
        .collect()  # ここで初めて計画を最適化して実行する
    )
    return [(m, c, int(n), int(r)) for m, c, n, r in df.iter_rows()]
```

`pl.col(...).dt.strftime(...)` や `(pl.col("resolved") == "yes").sum()` は値ではなく「列への計算の指示」（**式**）で、Rust 側でまとめて並列に実行される。戻り値を `list[tuple]` にしたのは、3 つの結果を `==` で比べるためである。

`LazyFrame` は `explain()` で最適化後の計画を見せる。`IT` だけに絞る確かめ用のクエリで試した（検証済み）。

実行結果:

```text
$ uv run python ../demos/lazy_explain.py
LazyFrame
AGGREGATE[maintain_order: false]
  [len().alias("inquiries")] BY [col("date").dt.month().alias("month")]
  FROM
  simple π 1/1 ["date"]
    Csv SCAN [data/inquiries.csv]
    PROJECT 2/4 COLUMNS
    SELECTION: col("category") == "IT"
    ESTIMATED ROWS: 1785
```

`PROJECT 2/4 COLUMNS` は 4 列のうち 2 列だけを読むこと（projection pushdown）、`SELECTION` は読みながら行を絞ること（predicate pushdown）である。Polars の docs: "In general, the lazy API should be preferred unless you are either interested in the intermediate results or are doing exploratory work and don't know yet what your query is going to look like."

### 3.4 pandas 3: 同じ集計と 3.0 の変更点

**狙い**: pandas の書き方と、3.0 で変わった 2 つの動作を確かめる。`analytics.py` の続き（抜粋・単体では動かない: 先頭の import と `Row` が要る）。

```python
def monthly_pandas(path: Path) -> list[Row]:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.assign(
        month=df["date"].dt.strftime("%Y-%m"),
        is_resolved=df["resolved"].eq("yes"),
    )
    out = (
        df.groupby(["month", "category"])  # 既定でキーの順に並ぶ
        .agg(inquiries=("faq_id", "size"), resolved=("is_resolved", "sum"))
        .reset_index()
    )
    return [
        (str(m), str(c), int(n), int(r)) for m, c, n, r in out.itertuples(index=False)
    ]
```

pandas はすぐに実行する（eager）。`groupby` の結果はキーが**インデックス**になるので `reset_index()` で列に戻す。Polars にはインデックスが無い（docs: "Polars does not use an index and each row is indexed by its integer position in the table."）。

3.0 の変更は確かめ用の `pandas3.py` で見た（検証で再現）。部分集合 `sub` への代入・連鎖代入・`.loc` の 3 通りで、元の `df` が変わるかを数える。省いた 1 行目は `pandas3.py:10: ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment.`、もう 1 行は移行ガイドへのリンクである。

実行結果:

```text
$ uv run python ../demos/pandas3.py
…（中略: 1 行）…
Such chained assignment never works to update the original DataFrame or Series, because the intermediate object on which we are setting values always behaves as a copy (due to Copy-on-Write).

Try using '.loc[row_indexer, col_indexer] = value' instead, to perform the assignment in a single step.

…（中略: 1 行）…
  df["resolved"][df["category"] == "IT"] = "no"  # 連鎖代入（chained assignment）
str python
元の df は変わらない: 0
連鎖代入は効かない: 72
.loc なら効く: 364
```

- **文字列の列は `str` 型**（2.x までは `object`）。原文: "Starting with pandas 3.0, a dedicated string data type is enabled by default (backed by PyArrow under the hood, if installed, otherwise falling back to being backed by NumPy object-dtype)." 出力の `python` が実装の置き場所で、§3.5 で PyArrow を入れた後は `str pyarrow` に変わった
- **Copy-on-Write が唯一の動作**。原文: "any subset or returned series/dataframe always behaves as a copy of the original, and thus never modifies the original"。`SettingWithCopyWarning` は無くなり、連鎖代入は警告を出すだけで**何も変えない**（72 は IT の未解決の件数のまま。`.loc` の後は 364 件すべてが `no`）
- 3.0.0 は 2026-01-21 のリリース。2.x から上げるときは、まず 2.3 で警告を出し切るよう公式が勧めている

**NumPy の位置づけ**: 同じ型の値を並べた多次元配列 `ndarray` と数値計算の土台で（docs: "NumPy is the fundamental package for scientific computing in Python."）、pandas の数値列の中身でもある。表の集計は DataFrame に任せ、行列・統計・シミュレーションのように同じ型の数値をまとめて計算するところで直接使う。集計結果を `np.array()` に入れ、`resolved / n` のようにループなしで解決率（平均 0.794）を計算できた（検証済み）。

### 3.5 DuckDB: SQL で CSV・Parquet・DataFrame を読む

**狙い**: 同じ集計を SQL で書く。DuckDB は SQLite と同じくサーバーを持たずプロセスの中で動く、分析向けの DB である。`analytics.py` の残り（抜粋・単体では動かない: 先頭の import と `Row` が要る）。

```python
SQL = """
SELECT strftime(date, '%Y-%m') AS month,
       category,
       count(*) AS inquiries,
       count_if(resolved = 'yes') AS resolved
FROM read_csv($path, types = {'resolved': 'VARCHAR'})  -- yes/no を文字列で読む
GROUP BY ALL
ORDER BY ALL
"""


def monthly_duckdb(path: Path) -> list[Row]:
    with duckdb.connect() as con:  # インメモリの DB。抜けると閉じる
        rows = con.execute(SQL, {"path": str(path)}).fetchall()
    return [(str(m), str(c), int(n), int(r)) for m, c, n, r in rows]
```

`GROUP BY ALL` / `ORDER BY ALL` は「集計していない列すべて」「すべての列」を表す DuckDB の拡張である。パスは f-string で埋め込まず、名前付きのパラメータ `$path` で渡す。`types` を書いたのは、CSV リーダーが `yes` / `no` を**真偽値と推測する**ためである（検証で再現）。

実行結果:

```text
$ uv run python ../demos/duck_sniff.py
[('date', 'DATE', 'YES', None, None, None), ('category', 'VARCHAR', 'YES', None, None, None), ('faq_id', 'VARCHAR', 'YES', None, None, None), ('resolved', 'BOOLEAN', 'YES', None, None, None)]
[(True, False)]
```

docs は型の推測を "attempting to convert the values in each column to the candidate types" と説明し、候補の最優先が BOOLEAN である。`'yes'` が `true` に変換されるので型を書かなくても件数は同じだったが、列の意味がデータしだいで変わるのを避けて明示した。

DataFrame を変数名のまま `FROM` に書くと、最初は PyArrow が無くて止まった（検証で再現）。docs にも "Note that the pyarrow library must be installed for the integration to work." とある。

実行結果:

```text
$ uv run python ../demos/duck_pl.py
…（中略: 17 行）…
_duckdb.InvalidInputException: Invalid Input Error: reading the Python object 'pl_df' as Arrow data failed: ModuleNotFoundError: No module named 'pyarrow'
```

`uv add pyarrow` の後は、Polars（`FROM pl_df`）・pandas（`FROM pd_df`）・Parquet のファイルに同じ形の SQL が書けた（検証済み）。

実行結果:

```text
$ uv run python ../demos/duck_frames.py
[('IT', 364), ('セキュリティ', 262)]
[('IT', 364), ('セキュリティ', 262)]
…（中略: 1 行）…
$ uv run python ../demos/parquet.py
[('no', 308), ('yes', 1192)]
```

変数名で読む仕組みは replacement scan と呼ばれ、`SET python_enable_replacements = false;` で止められる。結果を Polars で受ける `.pl()` は `duckdb.sql()` の結果（relation）にあり、docs: "Results of con.execute() have no .pl() method."

### 3.6 3 つの結果を比べ、テストで固定する

**狙い**: 3 つの書き方が同じ答えを出すことを確かめ、テストにする。`scripts/compare_engines.py` は 3 つを呼んで `==` で比べる（検証済み）。

実行結果:

```text
$ uv run python scripts/compare_engines.py
polars: 36 行 先頭 ('2026-01', 'IT', 64, 48) 末尾 ('2026-06', '総務', 52, 40)
pandas: 36 行 先頭 ('2026-01', 'IT', 64, 48) 末尾 ('2026-06', '総務', 52, 40)
duckdb: 36 行 先頭 ('2026-01', 'IT', 64, 48) 末尾 ('2026-06', '総務', 52, 40)
3 つの結果は同じ
```

6 か月 × 6 カテゴリで 36 行。テストは `tests/test_analytics.py` に 1 つ書く。月末と月初の行を入れ、月の境目で数え間違えないことも確かめる（検証済み）。

```python
from collections.abc import Callable
from pathlib import Path

import pytest

from faq.analytics import Row, monthly_duckdb, monthly_pandas, monthly_polars

CSV = """\
date,category,faq_id,resolved
2026-01-05,経費,faq-01,yes
2026-01-20,経費,faq-02,no
2026-01-31,IT,faq-05,yes
2026-02-01,経費,faq-01,yes
2026-02-14,IT,faq-06,no
"""
EXPECTED: list[Row] = [
    ("2026-01", "IT", 1, 1),
    ("2026-01", "経費", 2, 1),
    ("2026-02", "IT", 1, 0),
    ("2026-02", "経費", 1, 1),
]


@pytest.mark.parametrize("monthly", [monthly_polars, monthly_pandas, monthly_duckdb])
def test_monthly(tmp_path: Path, monthly: Callable[[Path], list[Row]]) -> None:
    path = tmp_path / "inquiries.csv"
    path.write_text(CSV, encoding="utf-8")
    assert monthly(path) == EXPECTED
```

実行結果:

```text
$ uv run pytest -q tests/test_analytics.py
...                                                                      [100%]
3 passed in 1.18s
```

参考値として、100 万行（約 30MB）の CSV で 3 つを 3 回ずつ動かした最短の時間を測った（Apple M2 Max。データの形・件数・マシンで大きく変わる）。

実行結果:

```text
$ uv run python ../demos/bench.py
monthly_polars: 0.030 秒
monthly_pandas: 0.368 秒
monthly_duckdb: 0.072 秒
結果は同じ: True
```

### 3.7 mypy strict と型スタブ

**狙い**: [Step 05](05-quality.md) の mypy strict を通したまま重いライブラリを足す。最初の `uv run mypy` は pandas だけを報告した（検証中に発生）。

実行結果:

```text
$ uv run mypy
src/faq/analytics.py:6: error: Library stubs not installed for "pandas"  [import-untyped]
src/faq/analytics.py:6: note: Hint: "python3 -m pip install pandas-stubs"
…（中略: 2 行）…
Found 1 error in 1 file (checked 16 source files)
```

`site-packages` を見ると、Polars・DuckDB・NumPy は本体に `py.typed` を同梱し、pandas には無い。pandas の型は別パッケージ `pandas-stubs`（PEP 561 の stub-only パッケージ）が持つ。通し課題は `uv add --dev pandas-stubs`（3.1.0.261029）を選び、`uv run mypy` が `Success: no issues found in 11 source files` になった（検証済み）。スタブは実行時に要らないので dev に入れる。版は `x.y.z.yymmdd` の形で、README は "If you **pin pandas**, pin `pandas-stubs` to the **same major/minor version**" としている。

スタブを入れずにモジュール単位で黙らせる方法も、別の小さなプロジェクトで試した（検証済み）。

実行結果:

```text
$ sed -n 10,15p pyproject.toml
[tool.mypy]
strict = true

[[tool.mypy.overrides]]
module = ["pandas", "pandas.*"]
ignore_missing_imports = true
$ uv run mypy demo.py
demo.py:6: note: Revealed type is "Any"
demo.py:7: error: Returning Any from function declared to return "int"  [no-any-return]
Found 1 error in 1 file (checked 1 source file)
```

import のエラーは消えるが、`pd.read_csv()` の結果が `Any` になり、別の場所で `no-any-return` が出る。mypy の docs: "the imported module will continue to be of type Any, and mypy may not catch errors in its use." 黙らせるなら `module = [...]` でそのライブラリだけに絞る。

### 3.8 ノートブック: marimo（と Jupyter）

**狙い**: 集計を対話的に眺める場所を作る。`uv add --group notebook marimo` で、アプリの依存とも dev とも分けた。`notebooks/inquiries.py` のセル 2 つ（抜粋・単体では動かない: 先頭の `app = marimo.App()` と import のセルが要る）。

```python
@app.cell
def _(mo):
    categories = ["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]
    category = mo.ui.dropdown(categories, value="IT", label="カテゴリ")
    category
    return (category,)


@app.cell
def _(category, pl):
    # category を変えると、このセルだけが自動で再実行される
    monthly = (
        pl.scan_csv("data/inquiries.csv", try_parse_dates=True)
        .filter(pl.col("category") == category.value)
        .group_by(pl.col("date").dt.strftime("%Y-%m").alias("month"))
        .agg(pl.len().alias("inquiries"))
        .sort("month")
        .collect()
    )
    monthly
    return
```

- セルは関数で、引数が「使う変数」、戻り値が「他のセルに渡す変数」である。marimo はこの依存関係から、ドロップダウンを変えたときに再実行するセルを決める
- セルの**最後の式が出力**になる（docs: "A cell's output is by default its last expression."）。そのため Ruff 0.17 の既定のルールが `B018`（意味の無い式）と `PLR1711`（不要な `return`）を出した（検証中に発生）。`[tool.ruff.lint.per-file-ignores]` に `"notebooks/*.py" = ["B018", "PLR1711"]` と書いてノートブックだけ外し、ノートブックの検査は `marimo check --strict` に任せた

ブラウザを開かずポート 2718 で起動し、応答を確かめてから PID を指定して止めた（検証済み）。

実行結果:

```text
$ uv run --group notebook marimo run notebooks/inquiries.py --headless --port 2718

        Running inquiries.py ⚡

        ➜  URL: http://localhost:2718


        Thanks for using marimo! 🌊🍃

$ curl -s -o /dev/null -w "%{http_code} %{content_type}\n" http://localhost:2718/
200 text/html; charset=utf-8
```

`marimo run` は読み取り専用のアプリ、`marimo edit` は編集画面で、どちらも `--headless` でブラウザを開かない。セルが動くことは `marimo export html` で書き出した HTML に `2026-01`〜`2026-06` が並ぶことで確かめた（検証済み）。

**Jupyter との違い**: Jupyter の `.ipynb` は JSON で、セルを好きな順に実行でき、消したセルの変数もメモリに残る。marimo の FAQ: "Unlike Jupyter notebooks, marimo notebooks are stored as pure Python files that can be executed as scripts, deployed as interactive web apps, and versioned easily with Git." Jupyter を使うなら、uv の docs は `uv run --with jupyter jupyter lab` を案内している（公式 docs 準拠・未実行: このステップは marimo だけを起動した）。

最後に [Step 05〜07](07-cli.md) の検査をまとめて回した（検証済み）。

実行結果:

```text
$ uv run ruff check && uv run ruff format --check && uv run mypy && uv run pytest -q
All checks passed!
24 files already formatted
Success: no issues found in 16 source files
...........................                                              [100%]
27 passed in 12.03s
```

---

## 4. ベストプラクティス

どれを使うかの目安（2026-11）:

| 場面 | 選ぶもの | 根拠 |
|---|---|---|
| 新しく書く集計・変換 | Polars（lazy API） | 計画が最適化される（"the lazy API is preferred in most cases"）。型に厳しく、欠損で整数が浮動小数点に変わるような暗黙の変換をしない（Coming from pandas の "Polars is strict"） |
| 既存の pandas のコード、pandas の DataFrame を受け取るライブラリ | pandas 3 | 3.0 で Copy-on-Write と `str` 型に揃い、動作が予測しやすくなった。移行は 2.3 で警告を出し切ってから |
| SQL で書きたい、CSV / Parquet をそのまま集計したい、DataFrame をまたいで結合したい | DuckDB | ファイルと DataFrame を `FROM` に直接書ける（Data Ingestion）。サーバーが要らない |
| 同じ型の数値をまとめて計算する | NumPy | `ndarray` は "homogeneous data types" を前提に、計算をコンパイル済みのコードで行う |
| 集計を対話的に眺めて共有する | marimo / Jupyter | marimo は `.py` なので Git で差分が読め、スクリプトとアプリにもなる。既存の `.ipynb` の資産があるなら Jupyter |

| 推奨 | 避ける | 理由 |
|---|---|---|
| Polars は `scan_*` で始めて最後に `collect()` | `read_csv()` で全部読んでから絞る | 使わない列・行を読まずに済む（§3.3 の `PROJECT 2/4 COLUMNS`） |
| pandas の更新は `df.loc[mask, "col"] = value` の 1 回で書く | `df["col"][mask] = value`（連鎖代入） | 3.0 では元の `df` が変わらない。警告だけで処理は続くので気づきにくい（§3.4） |
| 文字列の列は `pd.api.types.is_string_dtype()` で判定する | `df[c].dtype == object` | 3.0 の既定は `str` 型で `object` にならない（手元でも `True` / `False` に分かれた） |
| DuckDB の `read_csv` は意味が決まっている列に `types` を書く | 推測に任せる | `yes` / `no` が BOOLEAN になった（§3.5）。推測はファイルの一部（サンプル）だけを見て決まる |
| SQL の値は `$name` / `?` のパラメータで渡す | f-string で SQL に埋め込む | SQL インジェクションと引用符のエスケープ漏れを避ける |
| 型の無いライブラリは `*-stubs` を dev に足す。無ければ `[[tool.mypy.overrides]]` でそのモジュールだけ `ignore_missing_imports` | 全体で `ignore_missing_imports = true` | 黙らせたモジュールは `Any` になり、使う側の誤りを見逃す（mypy の docs） |
| 乱数は `random.Random(seed)` で作り、生成したデータはコミットする | `random.seed()` でグローバルの状態を変える | 他のコードの乱数とぶつからない。同じ種の結果は版をまたいで保証されない |
| ノートブックの依存は `--group notebook` に分ける | `dependencies` に marimo を入れる | アプリの利用者に、ノートブックのサーバー一式（Starlette・uvicorn など）を入れさせない |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `uv run mypy` が `Library stubs not installed for "pandas"` で止まる（検証中に発生） | pandas は `py.typed` を同梱しない | `uv add --dev pandas-stubs`。版は pandas と同じ `x.y` に揃える |
| marimo のノートブックに Ruff が `B018 Found useless expression` と `PLR1711` を出す（検証中に発生） | marimo はセルの最後の式を出力にし、末尾に `return` を書く | `per-file-ignores` でノートブックのディレクトリだけ外す |
| DuckDB で `FROM pl_df` が `No module named 'pyarrow'` で止まる（検証で再現） | DataFrame は Arrow 経由で読まれる | `uv add pyarrow`（3.15 用の wheel がある） |
| DuckDB で `yes` / `no` の列が BOOLEAN になる（検証で再現） | CSV の型の推測で BOOLEAN が最優先の候補 | `read_csv(..., types = {'col': 'VARCHAR'})`。全部を文字列にするなら `all_varchar = true` |
| pandas で書き換えたのに元の DataFrame が変わらず `ChainedAssignmentError` が出る（検証で再現） | 3.0 の Copy-on-Write。途中の結果はいつもコピーとして振る舞う | `.loc[行, 列] = 値` の 1 回で書く |
| pandas の文字列の列の実装が `python` になっている（検証で再現） | PyArrow が無いと `str` 型は NumPy の object 配列で実装される | PyArrow を入れると `pyarrow` になる |
| `con.execute(...).pl()` が使えない | DuckDB 2.0 では `.pl()` は relation にだけある | `duckdb.sql(...)` / `con.sql(...)` の結果に `.pl()` を付ける |

---

## 6. 次のステップ

- [Step 11: 配布とデプロイ](11-deploy.md) — faq-app をビルドしてコンテナに入れる。重いライブラリを足した後のイメージの大きさにも注意する
- ライブラリの全体像は [ライブラリ地図](../topics/libraries.md)、型チェッカーの違いは [型チェッカーの比較](../topics/type-checkers.md)

---

## 出典

| 情報源 | URL |
|---|---|
| Polars — Lazy API | https://docs.pola.rs/user-guide/concepts/lazy-api/ （2026-11-09 確認、Context7 `/websites/pola_rs` 経由。原文はページから写した。lazy を推す理由、pushdown、`explain()`） |
| Polars — Coming from pandas | https://docs.pola.rs/user-guide/migration/pandas/ （2026-11-09 確認。インデックスが無いこと、lazy、型に厳しいこと） |
| pandas — What's new in 3.0.0 | https://pandas.pydata.org/docs/whatsnew/v3.0.0.html （2026-11-09 確認、Context7 `/pandas-dev/pandas` 経由。3.0.0 は 2026-01-21、`str` 型、Copy-on-Write、連鎖代入、2.3 経由の移行） |
| pandas-stubs — README | https://github.com/pandas-dev/pandas-stubs （2026-11-09 確認。stub-only パッケージ、版の付け方と固定の勧め） |
| DuckDB — Python overview / Data Ingestion / Integration with Polars | https://duckdb.org/docs/2.0/clients/python/overview.html ・ https://duckdb.org/docs/2.0/clients/python/data_ingestion.html ・ https://duckdb.org/docs/2.0/guides/python/polars.html （2026-11-09 確認、Context7 `/duckdb/duckdb-web` 経由。replacement scan、PyArrow が要ること、`.pl()` と `con.execute()`） |
| DuckDB — CSV Auto Detection | https://duckdb.org/docs/2.0/data/csv/auto_detection.html （2026-11-09 確認。型の候補と BOOLEAN の優先、`all_varchar`） |
| NumPy — What is NumPy? | https://numpy.org/doc/stable/user/whatisnumpy.html （2026-11-09 確認） |
| marimo — FAQ / CLI / Outputs | https://docs.marimo.io/faq.html ・ https://docs.marimo.io/cli ・ https://docs.marimo.io/api/outputs （2026-11-09 確認、Context7 `/websites/marimo_io` 経由。Jupyter との違い、`--headless` と `--port`、最後の式が出力） |
| uv — Using uv with Jupyter | https://docs.astral.sh/uv/guides/integration/jupyter/ （2026-11-09 確認） |
| mypy — Missing imports | https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports （2026-11-09 確認。per-module の `ignore_missing_imports` と `Any`） |
| random — Notes on Reproducibility | https://docs.python.org/3/library/random.html （2026-11-09 確認） |
| PyPI — pyarrow / pandas-stubs | https://pypi.org/project/pyarrow/ ・ https://pypi.org/project/pandas-stubs/ （2026-11-09 確認。pyarrow 26.0.1 は cp315 と cp315t の wheel を配布） |

### 確認できなかった事項

- **Jupyter の起動**と **`marimo edit` の起動**は試していない（`marimo run` だけを起動した）
- **free-threaded 版（3.15t）での動作**は試していない。Polars・DuckDB に 3.15t 用の wheel が無いことは共有の事実シート（2026-11-08 時点の PyPI）による
- **速さ**は 1 台・1 種類のデータでの参考値で、Polars の docs にある速さの主張は検証していない
- `random` の `choice()` / `randrange()` の列が 3.14 以前と 3.15 で同じかは確かめていない（docs が保証していないことだけを確かめた）

- 関連: [Python 学習ガイド](../README.md) / [Step 05: 品質ツール](05-quality.md) / [Step 06: テスト](06-testing.md) / [型チェッカーの比較](../topics/type-checkers.md) / [ライブラリ地図](../topics/libraries.md)
