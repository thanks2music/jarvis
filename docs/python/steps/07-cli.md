# Step 07: スクリプトと CLI — 単一ファイルのスクリプトから faq コマンドまで

> 出典（一次情報）:
> - [PEP 723 – Inline script metadata (peps.python.org)](https://peps.python.org/pep-0723/) と [Inline script metadata (packaging.python.org)](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) — スクリプトの先頭に依存を書く仕様
> - [Running scripts (docs.astral.sh)](https://docs.astral.sh/uv/guides/scripts/) と [Tools (docs.astral.sh)](https://docs.astral.sh/uv/concepts/tools/) — `uv add --script`・`uv tool install`・`uvx`
> - [Typer (typer.tiangolo.com)](https://typer.tiangolo.com/tutorial/) — コマンド・引数・終了・テスト・パッケージ化
> - [Rich (rich.readthedocs.io)](https://rich.readthedocs.io/en/latest/) — `Table` と `Console`
> - [argparse (docs.python.org)](https://docs.python.org/3/library/argparse.html) と [sys.exit (docs.python.org)](https://docs.python.org/3/library/sys.html#sys.exit) — 標準ライブラリの CLI と終了コード
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・Typer 0.28.0・Rich 15.0.0 で検証）

Node.js では、CLI を commander や yargs・citty で組み、`package.json` の `bin` で登録し、`npm install -g` や `npx` で配る。依存のある 1 ファイルのスクリプトを、`package.json` 無しで動かす標準の方法は無い（Bun は `node_modules` が無ければ import した瞬間に自動で入れる）。
Python では、1 ファイルのスクリプトは**先頭のコメントに依存を書き**（PEP 723）、`uv run` がその場で環境を作る。コマンドは **Typer** で組み、`[project.scripts]` で登録し、`uv tool install` で PATH に入れる。
このステップでは、FAQ を集計するスクリプト `scripts/report.py` と、`faq search` / `faq stats` の 2 つのサブコマンドを持つ CLI を作り、テストし、どのディレクトリからでも動くようにする。
前は [Step 06: テスト](06-testing.md)、全体の地図は [Python 学習ガイド](../README.md) を参照。

---

## 1. TL;DR

- **依存のある 1 ファイルのスクリプトは `uv add --script` で先頭に `# /// script` のブロックを書く**。`uv run` はそのブロックだけを読み、プロジェクトの依存は無視する（§3.1）。
- **CLI は Typer で組む**。関数の引数と型ヒント（`Annotated`）がそのまま引数・オプション・`--help` になる。依存を増やしたくなければ標準の argparse でも書ける（§3.2・§3.3）。
- **終了コードは 0 = 成功、1 = 処理の失敗、2 = 使い方の誤り**。Typer（Click）と argparse は、使い方の誤りを標準エラーに出して 2 で終わる（§3.4）。
- **`[project.scripts]` に `faq = "faq.cli:app"`** と書けば `faq` コマンドになり、`__main__.py` から同じ `app()` を呼べば `python -m faq` でも動く（§3.5）。
- **テストは `typer.testing.CliRunner`**。`env=` で環境変数も渡せる（§3.6）。
- **`uv tool install .` が `npm install -g .`、`uvx --from . faq` が `npx --package . faq` にあたる**。実行ファイルは `~/.local/bin` に置かれる（§3.7）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js / Bun | Python |
|---|---|---|
| 依存のある 1 ファイルのスクリプト | 標準の方法は無い（Bun は auto-install） | PEP 723 の `# /// script` ブロック + `uv run` |
| 引数の解析（標準） | `node:util` の `parseArgs` | `argparse` |
| CLI フレームワーク | commander / yargs / citty | Typer（Click の上に作られている） / Click |
| 色付きの出力・表 | chalk / cli-table3 | Rich（`Console`・`Table`） |
| コマンドを登録する | `package.json` の `bin` | `[project.scripts]` |
| パッケージを実行する | `node .` | `python -m faq`（`__main__.py`） |
| グローバルに入れる | `npm install -g .` / `bun add -g` | `uv tool install .` |
| 入れずに一度だけ動かす | `npx --package . faq` / `bunx` | `uvx --from . faq` |
| CLI のテスト | `execa` で子プロセスを起動 | `CliRunner().invoke(app, [...])`（同じプロセスで呼ぶ） |
| 異常終了 | `process.exit(1)` | `raise typer.Exit(code=1)` / `sys.exit(1)` |

---

## 3. ハンズオン

[Step 06](06-testing.md) までの `faq-app/` を使う。ログは、Rich の出力の幅と色を固定するため `COLUMNS=100` と `NO_COLOR=1` を付けて取った。端末の幅が違えば、表と `--help` の罫線の長さが変わる。

### 3.1 依存のある 1 ファイルのスクリプト（PEP 723）

**狙い**: `pyproject.toml` を持たない 1 ファイルのスクリプトに、依存を一緒に持たせる。

Rich を使う集計スクリプトを、`pyproject.toml` の無いディレクトリで、何も書かずに動かす（検証で再現）。

実行結果:

```text
$ uv run report.py faq.jsonl
Traceback (most recent call last):
  File "~/standalone/report.py", line 6, in <module>
    from rich.console import Console
ModuleNotFoundError: No module named 'rich'
```

プロジェクトの外の `uv run` は、依存を何も入れずに Python を動かす（[Step 01](01-setup.md) §3.5）。そこでスクリプトを `faq-app/scripts/report.py` に置き、`uv add --script` で依存を書き込む（検証済み）。

実行結果:

```text
$ uv add --script scripts/report.py rich
Resolved 4 packages in 7ms
$ sh -c "sed -n \"1,6p\" scripts/report.py"
# /// script
# requires-python = ">=3.15"
# dependencies = [
#     "rich>=15.0.0",
# ]
# ///
```

本体は、引数の JSONL（既定は `data/faq.jsonl`）を読んでカテゴリを数え、`Table("カテゴリ", "件数", title=...)` に `add_row()` して `Console().print()` する（検証済み。Rich の docs も見出しを位置引数で並べる書き方を載せている）。

```python
import json
import sys
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/faq.jsonl")
rows = [
    json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
table = Table("カテゴリ", "件数", title=f"{path.name} の集計")
for category, n in Counter(r["category"] for r in rows).most_common():
    table.add_row(category, str(n))
Console().print(table)
```

実行結果:

```text
$ uv run scripts/report.py
   faq.jsonl の集計    
┏━━━━━━━━━━━━━━┳━━━━━━┓
┃ カテゴリ     ┃ 件数 ┃
┡━━━━━━━━━━━━━━╇━━━━━━┩
│ IT           │ 3    │
…（中略: 4 行）…
│ 出張         │ 1    │
└──────────────┴──────┘
```

- `# /// script` から `# ///` までは TOML である。仕様の原文: "This document MAY include the top-level fields dependencies and requires-python, and MAY optionally include a [tool] table."
- uv は Rich を入れた使い捨ての環境（キャッシュに残る）で実行する。`faq-app/` の中でも**プロジェクトの依存は使わない**。uv docs: "When using inline script metadata, even if uv run is used in a project, the project's dependencies will be ignored. The --no-project flag is not required."
- ブロックに書くのは範囲だけである。固定するなら `uv lock --script scripts/report.py` で隣に `report.py.lock` を作る（"scripts must be explicitly locked using uv lock"）
- ブロックを最初から持つスクリプトは `uv init --script hello.py --python 3.15` で作れる（検証済み）。依存が無くても `# dependencies = []` が書かれる。uv docs も "The dependencies field must be provided even if empty." としている

### 3.2 標準ライブラリだけで書く（argparse）

**狙い**: 依存を足さない CLI の書き方を見て、Typer が何を肩代わりするかを知る。`faq search` と同じことを argparse で `argparse_demo/search_min.py` に書く（検証済み）。

```python
import argparse
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser(prog="faq-search", description="FAQ を検索する")
parser.add_argument("query", help="質問と回答から探す語")
parser.add_argument("--data", type=Path, default=Path("data/faq.jsonl"))
args = parser.parse_args()
if not args.data.exists():
    parser.error(f"{args.data} が無い")  # 標準エラーに出して終了コード 2

q = args.query.casefold()
lines = args.data.read_text(encoding="utf-8").splitlines()
rows = [json.loads(line) for line in lines if line.strip()]
hits = [r for r in rows if q in f"{r['question']} {r['answer']}".casefold()]
for r in hits:
    print(f"{r['id']}  {r['category']}  {r['question']}")
if not hits:
    print(f"「{args.query}」に一致する FAQ は無い", file=sys.stderr)
    sys.exit(1)
```

実行結果:

```text
$ uv run --no-project argparse_demo/search_min.py VPN
faq-05  IT  社内 VPN につながりません。
```

- `--help`（`usage: faq-search [-h] [--data DATA] query` から始まる）と使い方の誤りの処理は argparse が作る。Python 3.14 からヘルプは既定で色付きになった（`color=True`。ここでは `NO_COLOR=1` で消えている）。`--no-project` は `faq-app/` の中でもプロジェクトを入れずに動かす指定である
- ファイルの存在の検査・環境変数・終了コードは自分で書く。サブコマンドを足すなら `add_subparsers()` が要る。ここが Typer との差になる

### 3.3 Typer で `faq` コマンドを作る

**狙い**: サブコマンド `search` と `stats` を持つ CLI を、型ヒントから組み立てる。

`uv add typer` を実行すると、typer 0.28.0 と一緒に rich 15.0.0・shellingham 1.5.4 なども入った（検証済み）。Typer の docs によると、Rich は "to show nicely formatted errors automatically"、shellingham はシェル補完のための依存である。`src/faq/cli.py` の前半（検証済み）。

```python
from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from faq.loader import load_faqs
from faq.search import search as search_faqs

app = typer.Typer(help="社内 FAQ を検索・集計する", no_args_is_help=True)
console = Console()

DataOption = Annotated[
    Path,
    typer.Option(
        "--data", envvar="FAQ_DATA", help="FAQ の JSONL ファイル", exists=True
    ),
]
```

`search_faqs` は、`src/faq/search.py` に足した、質問と回答を大小文字を区別せずに探す関数である（検証済み）。

```python
def search(faqs: Iterable[Faq], query: str) -> list[Faq]:
    q = query.casefold()
    return [
        faq
        for faq in faqs
        if q in faq.question.casefold() or q in faq.answer.casefold()
    ]
```

`cli.py` の後半（検証済み）。

```python
@app.command()
def search(
    query: Annotated[str, typer.Argument(help="質問と回答から探す語")],
    data: DataOption = Path("data/faq.jsonl"),
) -> None:
    """質問か回答に QUERY を含む FAQ を表示する。"""
    hits = search_faqs(load_faqs(data), query)
    if not hits:
        console.print(f"「{escape(query)}」に一致する FAQ は無い")
        raise typer.Exit(code=1)
    table = Table("ID", "カテゴリ", "質問")
    for faq in hits:
        table.add_row(faq.id, faq.category, escape(faq.question))
    console.print(table)


@app.command()
def stats(data: DataOption = Path("data/faq.jsonl")) -> None:
    """カテゴリごとの件数を表示する。"""
    counts = Counter(faq.category for faq in load_faqs(data))
    for category, n in counts.most_common():
        console.print(f"{category}: {n} 件")
```

| 書き方 | 意味 | commander で言うと |
|---|---|---|
| `@app.command()` | 関数をサブコマンドにする。名前は関数名、説明は docstring | `program.command("search").description(...)` |
| `Annotated[str, typer.Argument(...)]` | 既定値の無い位置引数 | `.argument("<query>")` |
| `Annotated[Path, typer.Option("--data")] = 既定値` | オプション。文字列を `Path` に変換する | `.option("--data <path>")` |
| `envvar="FAQ_DATA"` | `--data` が無ければ環境変数から読む | 自分で `process.env` を読む |
| `exists=True` | ファイルが無ければ使い方の誤りとして止める | 自分で検査する |
| `no_args_is_help=True` | 引数なしで起動したらヘルプを出す | 自分で組む |

`Annotated` は [Step 04](04-typing.md) で見た、型に付加情報を添える書き方である。Typer の docs は "Prefer to use the Annotated version if possible." とし、`= typer.Option(...)` を既定値の位置に置く旧来の書き方より勧めている。`DataOption` のように別名にすれば、2 つのコマンドで同じオプションを使い回せる。

実行結果:

```text
$ uv run faq --help
…（中略: 4 行）…

 Usage: faq [OPTIONS] COMMAND [ARGS]...

 社内 FAQ を検索・集計する

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                          │
…（中略: 4 行）…
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ search  質問か回答に QUERY を含む FAQ を表示する。                                               │
│ stats   カテゴリごとの件数を表示する。                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

先頭の中略は、`pyproject.toml` が変わったので uv がプロジェクトを入れ直した 4 行（`Building faq` など）である。`--install-completion` は Typer が自動で足すシェル補完の設定。

実行結果:

```text
$ uv run faq search VPN
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ カテゴリ ┃ 質問                        ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ faq-05 │ IT       │ 社内 VPN につながりません。 │
└────────┴──────────┴─────────────────────────────┘
```

### 3.4 終了コードと、標準出力・標準エラー

**狙い**: シェルや CI から呼ばれても正しく振る舞う CLI にする。標準エラーを捨てて、何がどこに出るかを確かめる（検証済み）。ここに載せない `--data nope.jsonl`（`exists=True` に違反）と、引数なしの `uv run faq`（`no_args_is_help` でヘルプが出る）も、終了コード **2** だった。

実行結果:

```text
$ uv run faq search "宇宙" 2>/dev/null; echo "exit=$?"
「宇宙」に一致する FAQ は無い
exit=1
$ uv run faq search
Usage: faq search [OPTIONS] {query}
Try 'faq search --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'query'.                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
$ uv run faq search 2>/dev/null; echo "exit=$?"
exit=2
$ uv run --no-project argparse_demo/search_min.py "宇宙" 2>/dev/null; echo "exit=$?"
exit=1
```

| 状況 | 終了コード | 出る場所 | 根拠 |
|---|---|---|---|
| 成功 | 0 | 標準出力 | `typer.Exit()` の既定は 0 |
| 処理の失敗（一致なし） | 1（`typer.Exit(code=1)`） | 書いた側が決める | sys.exit の docs: "Unix programs generally use 2 for command line syntax errors and 1 for all other kinds of errors." |
| 使い方の誤り（Typer / Click） | 2 | 標準エラー | Click の docs: "If a help page is displayed due to incorrect user input, the program returns exit code 2." |
| `parser.error()`（argparse） | 2 | 標準エラー | argparse の docs: "prints a usage message, including the message, to sys.stderr and terminates the program with a status code of 2." |

通し課題の `faq search` は「一致なし」を**標準出力**に出している（`Console()` の既定は `sys.stdout`）。argparse 版は `print(..., file=sys.stderr)`（JS の `console.error()`）で標準エラーに出した。`faq search 語 | wc -l` のようにパイプでつなぐなら、メッセージは標準エラーに出す方が結果を汚さない。Typer と Rich の docs は、そのために `err_console = Console(stderr=True)` を別に作り、エラーだけをそちらへ `print` する書き方を示している。

### 3.5 `[project.scripts]` と `python -m faq`

**狙い**: [Step 03](03-project.md) で作った 2 つの入口（`faq` コマンドと `python -m faq`）を、Typer の `app` に付け替える。`src/faq/__main__.py` は `from faq.cli import app` と `app()` の 2 行にした。`pyproject.toml` の変わった所（抜粋・単体では動かない）。

```toml
dependencies = [
    "pydantic>=2.14",
    "typer>=0.28.0",
]

[project.scripts]
faq = "faq.cli:app"   # Step 03・04 は "faq:main"
```

実行結果:

```text
$ uv run python -m faq search "パスワード"
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ カテゴリ ┃ 質問                     ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ faq-06 │ IT       │ パスワードを忘れました。 │
└────────┴──────────┴──────────────────────────┘
```

- 右辺は `モジュール:呼び出せるもの`。Typer の `app` は呼び出せるので、関数でなくてよい。Typer の docs のパッケージ化の章も `"rick_portal_gun.main:app"` の形で書いている
- Step 03・04 の `faq.main()`（件数を表示するだけの関数）は CLI に置き換わったので消し、`__init__.py` の `__all__` からも外した。それを確かめていた Step 06 の `tests/test_main.py` は、§3.6 の `tests/test_cli.py` に置き換えた

### 3.6 `CliRunner` でテストする

**狙い**: 子プロセスを起動せずに、引数・環境変数・終了コード・出力を確かめる。`tests/test_cli.py` の 3 本のうち 2 本（検証済み。残りの 1 本は一致しないときの `exit_code == 1` を確かめる）。`data_path` は [Step 06](06-testing.md) の `conftest.py` にある session スコープの fixture である。

```python
from pathlib import Path

from typer.testing import CliRunner

from faq.cli import app

runner = CliRunner()


def test_search_finds_vpn(data_path: Path) -> None:
    result = runner.invoke(app, ["search", "VPN", "--data", str(data_path)])
    assert result.exit_code == 0
    assert "faq-05" in result.output


def test_stats_reads_env_var(data_path: Path) -> None:
    result = runner.invoke(app, ["stats"], env={"FAQ_DATA": str(data_path)})
    assert result.exit_code == 0
    assert "IT: 3 件" in result.output
```

- `typer.testing.CliRunner` は Click の `CliRunner` で、同じプロセスの中で標準入出力を差し替えて `app` を呼ぶ。`typer.Exit(code=1)` は外に漏れず `result.exit_code` に入る。`env` は Click の API リファレンスで "a dictionary with environment variables for overriding." と説明されている（`CliRunner` の引数。`invoke()` にも同じ名前の引数があり、ここではそちらを使った）。`test_stats_reads_env_var` は `--data` を渡さず `FAQ_DATA` だけで動くことを残している

Step 05・06 の検査も回すと、手で書いた `cli.py` と `search.py` が `ruff format --check` に引っかかった（検証中に発生）。1 行が Ruff の既定の 88 文字を超えていた。`uv run ruff format` で直し（§3.3 のコードは直した後の形）、全部が通った。1 回目は `scripts/report.py`（§3.1）を足す前に取った記録なので、ファイル数が 1 つ少ない。

実行結果:

```text
$ sh -c "uv run ruff check && uv run ruff format --check"
All checks passed!
unformatted: File would be reformatted
  --> src/faq/cli.py:17:18
…（中略: 21 行）…
2 files would be reformatted, 11 files already formatted
$ sh -c "uv run ruff check && uv run ruff format --check && uv run mypy && uv run pytest -q"
All checks passed!
14 files already formatted
Success: no issues found in 10 source files
.............                                                                                [100%]
13 passed in 0.52s
```

### 3.7 配布する: `uv tool install` と `uvx --from`

**狙い**: `uv run` を付けずに、どのディレクトリからでも `faq` を動かす（`/tmp` で `faq stats --data <絶対パス>` が動くことも確かめた）。

実行結果:

```text
$ uv tool install .
Resolved 13 packages in 5ms
…（中略: 17 行）…
Installed 1 executable: faq
$ uv tool dir --bin
~/.local/bin
```

- `uv tool install` は、ツールごとに専用の仮想環境を作り、実行ファイルを**実行ファイルのディレクトリ**に置く。Unix ではふつう `~/.local/bin` になる（uv docs の保存場所の表の順は `$XDG_BIN_HOME`、`$XDG_DATA_HOME/../bin`、`$HOME/.local/bin`。`UV_TOOL_BIN_DIR` で変えられる）
- uv docs: "The executable directory must be in the PATH variable for tool executables to be available from the shell." PATH に無ければ警告が出るので、`uv tool update-shell` で足す
- 入るのはその時点のコピーで、ソースを直しても反映されない

`/tmp` で `--data` を省くと、既定の `data/faq.jsonl` を**カレントディレクトリから**探して止まる（検証で再現）。環境変数で渡せば動く（検証済み）。

実行結果:

```text
$ cd /tmp && faq stats
Usage: faq stats [OPTIONS]
Try 'faq stats --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--data' (env var: 'FAQ_DATA'): Path 'data/faq.jsonl' does not exist.          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
$ cd /tmp && FAQ_DATA=~/faq-app/data/faq.jsonl faq stats
IT: 3 件
…（中略: 4 行）…
出張: 1 件
```

入れずに一度だけ動かすなら `uvx --from`（検証済み）。`--from` は「どのパッケージのコマンドか」を指定するオプションで、パッケージ名とコマンド名が違うときにも使う。PyPI に公開すれば、他の人は `uv tool install faq` や `uvx faq` で使える（ビルドと公開は [Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ)）。

実行結果:

```text
$ uvx --from . faq search "名刺"
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ カテゴリ ┃ 質問                   ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ faq-09 │ 総務     │ 名刺を発注したいです。 │
└────────┴──────────┴────────────────────────┘
```

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| 依存のある使い捨てのスクリプトは PEP 723 のブロックを書き、`uv add --script` で足す。長く使うなら `uv lock --script` | 「先に `pip install rich` して」と README に書く | 依存がスクリプトと一緒に移動し、`uv run` が毎回同じ環境を作る。書式は packaging.python.org で標準化されている |
| 引数が少なく依存を足したくなければ argparse、サブコマンド・環境変数・検証が要るなら Typer | 自分で `sys.argv` を解析する | argparse はヘルプと使い方の誤り（終了コード 2）を作る。Typer はさらに型の変換・`envvar`・`exists=True` を宣言だけで書ける |
| 利用者の入力やデータを Rich で表示するときは `rich.markup.escape()` を通す | f-string をそのまま `console.print` に渡す | Rich は `[...]` を markup として解釈する。escape を入れる前は `faq search "[/x]"` が `MarkupError` で落ちた（検証で再現）。Rich の docs: "Without escaping it may be possible to inject tags where you don't want them." |
| Typer の引数は `Annotated[...]` で書く | `name: str = typer.Option(...)` | Typer の docs: "Prefer to use the Annotated version if possible."。既定値が既定値として読め、関数を普通に呼んでも壊れない |
| 処理の失敗は 1、使い方の誤りは 2 で終わり、エラーは標準エラーに出す | 失敗しても 0 で終わる。エラーを標準出力に混ぜる | シェルや CI は終了コードで成否を判断する（sys.exit の docs の慣習）。標準エラーへは Typer の docs が示す `Console(stderr=True)` で出す。通し課題の `search` は簡単にするため、一致なしの表示を標準出力に出している（§3.4） |
| `[project.scripts]` と `__main__.py` は同じ `app` を指す | 入口ごとに別の処理を書く | どちらから呼んでも同じ動作になる。`__main__.py` は短く保つ（[Step 03](03-project.md) §4） |
| 自作の CLI を常用するなら `uv tool install .`、一度だけなら `uvx --from .` | プロジェクトの `.venv/bin` を PATH に足す | ツールごとに隔離された環境に入り、プロジェクトの依存の変更に巻き込まれない（uv docs の Tools） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 自分で書いた `cli.py` と `search.py` を `ruff format --check` が指摘する（検証中に発生） | 1 行が Ruff の既定の 88 文字を超えていた。Typer のオプションは引数が多く、1 行に収まりにくい | `uv run ruff format` で直す。pre-commit を入れていれば commit 時に直る（[Step 05: 品質ツール](05-quality.md)） |
| メタデータの無いスクリプトが、プロジェクトの外で `ModuleNotFoundError: No module named 'rich'` になる（検証で再現） | プロジェクトの外の `uv run` は依存を何も入れない | `uv add --script <ファイル> rich` でブロックを書く。一度だけなら `uv run --with rich <ファイル>` |
| `uv tool install` した `faq` が、別のディレクトリで `Path 'data/faq.jsonl' does not exist` になる（検証で再現） | 既定値 `Path("data/faq.jsonl")` はカレントディレクトリを基準にする（Node の `process.cwd()` と同じ） | `--data` か `FAQ_DATA` で絶対パスを渡す。配布するなら、データの置き場所を設定で決めるか、パッケージに同梱して `importlib.resources` で読む |
| 引数なしの `faq` がヘルプを出すのに、終了コードが 2 になる（検証で再現） | `no_args_is_help` は使い方の誤りとして扱われる。Click の docs: "returns exit code 2 since the user invoked the command incorrectly" | 意図どおりの動作である。`faq` だけを呼んで成否を見ない |
| `2>/dev/null` を付けても「一致する FAQ は無い」が出る（検証で再現） | `Console()` の既定は標準出力。`typer.Exit(code=1)` は終了コードを決めるだけ | エラーは `Console(stderr=True)` で出す（§3.4） |
| ソースを直したのに、`uv tool install` した `faq` が古いまま | その時点のコピーを入れている | `uv tool install --reinstall .` で入れ直すか `-e` で入れる。開発中は `uv run faq` を使う |

---

## 6. 次のステップ

- [Step 08: 非同期と並行処理](../README.md#4-学習ロードマップ) — `async` / `await` と asyncio を、JS のイベントループとの違いから押さえる
- 道具の側から整理したい場合は [uv](../topics/uv.md)（`uv tool`・`uvx`）と [pyproject.toml](../topics/pyproject-toml.md)（`[project.scripts]`）

---

## 出典

| 情報源 | URL |
|---|---|
| PEP 723 – Inline script metadata | https://peps.python.org/pep-0723/ （2026-11-08 確認。Status: Final） |
| Inline script metadata（仕様） | https://packaging.python.org/en/latest/specifications/inline-script-metadata/ （2026-11-08 確認。`# /// script` の書式、`dependencies`・`requires-python`・`[tool]`） |
| uv — Running scripts | https://docs.astral.sh/uv/guides/scripts/ （2026-11-08 確認。`uv add --script`・`uv init --script`・`--no-project`・プロジェクトの依存を無視すること・`uv lock --script`・空でも `dependencies` が要ること） |
| uv — Tools / Using tools / Storage | https://docs.astral.sh/uv/concepts/tools/ ・ https://docs.astral.sh/uv/guides/tools/ ・ https://docs.astral.sh/uv/reference/storage/ （2026-11-08 確認。実行ファイルのディレクトリと PATH、`uv tool update-shell`、`--from`、`uv tool dir --bin`） |
| Typer — Tutorial（Printing / Terminating / Testing / Path / Package / Commands） | https://typer.tiangolo.com/tutorial/ （2026-11-08 確認、Context7 `/websites/typer_tiangolo` 経由。原文は各ページから写した。`Console(stderr=True)`・`typer.Exit(code=...)`・`CliRunner`・`exists`・`[project.scripts]`・`no_args_is_help`・`Annotated` の推奨） |
| Typer — トップページ | https://typer.tiangolo.com/ （2026-11-08 確認。Rich と shellingham の役割） |
| Click — Exception Handling and Exit Codes / API | https://click.palletsprojects.com/en/stable/exceptions/ ・ https://click.palletsprojects.com/en/stable/api/ （2026-11-08 確認。ヘルプと終了コード 2、`CliRunner` の `env`） |
| Rich — Tables / Console API / Console Markup | https://rich.readthedocs.io/en/latest/tables.html ・ https://rich.readthedocs.io/en/latest/console.html ・ https://rich.readthedocs.io/en/latest/markup.html （2026-11-09 確認。位置引数の見出し、`stderr=True`、`NO_COLOR`・`COLUMNS`、`escape()`） |
| argparse / sys.exit | https://docs.python.org/3/library/argparse.html ・ https://docs.python.org/3/library/sys.html#sys.exit （2026-11-08 確認。`ArgumentParser.error()` の終了コード 2、`color=True` の既定、Unix の終了コードの慣習） |
| Bun — Auto-install | https://bun.com/docs/runtime/auto-install （2026-11-08 確認。`node_modules` が無いと import 時に自動で入れること） |

### 確認できなかった事項

- **`uv tool install -e .` の動作**。`uv tool install --help` の説明（"changes in the package's source directory are reflected without reinstallation"）を確かめただけで、実行していない。入れ替えると通し課題で記録した状態が変わるためである
- **シバン行 `#!/usr/bin/env -S uv run --script`** で PEP 723 のスクリプトを直接実行する方法は、uv の scripts ガイドにあることだけを確かめ、試していない
- **npm の `npx --package` と `npm install -g .`** との対応は、npm の docs の原文で確かめていない（対応表の目安として載せた）

- 関連: [Python 学習ガイド](../README.md) / [Step 03: プロジェクト構成](03-project.md) / [Step 06: テスト](06-testing.md) / [uv](../topics/uv.md) / [pyproject.toml](../topics/pyproject-toml.md)
