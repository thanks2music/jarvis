# Step 05: 品質ツール — Ruff と型チェッカーを毎回同じ設定で回す

> 出典（一次情報）:
> - [Tutorial / The Ruff Linter / The Ruff Formatter (docs.astral.sh)](https://docs.astral.sh/ruff/tutorial/) — 既定のルールから始める方針、`lint.select` と `lint.extend-select`、`# noqa`
> - [Ruff v0.16.0 (astral.sh)](https://astral.sh/blog/ruff-v0.16.0) — 既定で有効なルールが 59 から 413 に増えたこと
> - [The mypy configuration file (mypy.readthedocs.io)](https://mypy.readthedocs.io/en/stable/config_file.html) — `[tool.mypy]`・`files`・`strict`
> - [Mypy (docs.pydantic.dev)](https://docs.pydantic.dev/latest/integrations/mypy/) — `pydantic.mypy` プラグインと `init_typed`
> - [pre-commit (pre-commit.com)](https://pre-commit.com/) ・ [prek README (github.com/j178/prek)](https://github.com/j178/prek) — フックの設定と、`language: unsupported`
> - [ruff-pre-commit README](https://github.com/astral-sh/ruff-pre-commit) ・ [Using uv in pre-commit (docs.astral.sh)](https://docs.astral.sh/uv/guides/integration/pre-commit/) — Ruff と `uv-lock` のフック
> - [Editor setup (docs.astral.sh)](https://docs.astral.sh/ruff/editors/setup/) ・ [Python (zed.dev)](https://zed.dev/docs/languages/python) ・ [vscode-mypy README](https://github.com/microsoft/vscode-mypy) — エディタの設定
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・Ruff 0.17.4・mypy 2.4.1・prek 0.5.10・pre-commit 4.7.0 で検証）

Node.js / Bun では、ESLint で lint し、Prettier で整形し、`tsc --noEmit` で型を検査し、husky と lint-staged で commit の前にそれらを回す。
Python では、lint と整形を **Ruff** 1 つが受け持ち、型は **mypy**（など）が検査し、commit の前に回す仕組みは **pre-commit**（または互換の **prek**）が受け持つ。
このステップでは、[Step 04: 型](04-typing.md) の `faq-app/` に Ruff と mypy を dev 依存として入れ、設定を `pyproject.toml` にまとめ、commit のたびに同じ検査が走るようにする。
シリーズ全体は [Python 学習ガイド](../README.md)、次は [Step 06: テスト](06-testing.md) を参照。

---

## 1. TL;DR

- **lint も整形も Ruff 1 つ**。`ruff check` が ESLint、`ruff format` が Prettier にあたる。Step 02 でわざと残した未使用の import を、設定ゼロの既定のルールだけで `F401` として見つけ、`--fix` で消した（§3.2・§3.3）。
- **ルールは既定から始める**。Ruff 0.16 から既定で 413 のルールが有効になった。足すときは `lint.select` ではなく `lint.extend-select` を使う。`select` は既定を置き換えるので、`--select I` だけにすると `F401` すら出なくなった（§3.4）。
- **mypy は `[tool.mypy]` に `files`・`strict`・`plugins` を書き、`uv run mypy` を引数なしで回す**。`strict` が無いと、型を書いていない関数は黙って通った（§3.5）。
- **Pydantic のモデルを検査するなら `pydantic.mypy` プラグインを入れる**。プラグインが無いと `frozen=True` のモデルへの代入を見逃し、プラグインだけだとフィールドの型の誤りを見逃した。`init_typed = true` を足すと 3 件すべてを報告した（§3.6）。
- **commit の前に回すのは pre-commit か prek**。設定ファイルは共通で、両方で同じ結果になった。Ruff が直したら commit は止まるので、`git add` してもう一度 commit する（§3.7）。
- エディタは Ruff の language server と型チェッカーの拡張機能を入れる。Zed は Ruff を最初から使い、型の表示は basedpyright が担う（§3.8）。CI で同じ検査を回すのは [Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ) で扱う。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js / Bun | Python | 補足 |
|---|---|---|---|
| lint | ESLint（`eslint .`） | `uv run ruff check` | 引数なしでカレントディレクトリ以下を検査する |
| lint の自動修正 | `eslint --fix` | `uv run ruff check --fix` | 直せるものには `[*]` が付く |
| 整形 | Prettier（`prettier --write .`） | `uv run ruff format` | Black 互換を目指した formatter |
| 整形済みか確かめる | `prettier --check .` | `uv run ruff format --check` | 差分を表示して終了コード 1 |
| lint の設定 | `eslint.config.js` | `pyproject.toml` の `[tool.ruff.lint]` | `ruff.toml` にも書ける |
| 1 行だけ黙らせる | `// eslint-disable-next-line no-unused-vars` | 行末に `# noqa: F401` | `noqa` は**同じ行**にしか効かない。前の行に書くなら `# ruff: ignore[F401]`（0.16 から。[Ruff](../topics/ruff.md)） |
| 型の検査 | `tsc --noEmit` | `uv run mypy` | 検査する場所は `[tool.mypy]` の `files` |
| 厳しい型検査 | `tsconfig.json` の `"strict": true` | `[tool.mypy]` の `strict = true` | どちらも複数のフラグをまとめて有効にする |
| commit の前に回す | husky + lint-staged | pre-commit / prek と `.pre-commit-config.yaml` | どちらも、変更したファイルだけを渡すのが既定 |
| フックを入れる | `npm install` で `prepare` が husky を入れる | 各自が 1 回 `prek install` | 自動では入らない（§5） |
| `npm run lint` | `package.json` の `scripts` | 無い | uv にタスク機能は無い。コマンドを直接書く |

ツールの全体像は [Ruff](../topics/ruff.md) と [型チェッカーの比較](../topics/type-checkers.md) で扱う。用語は [用語集](../README.md#8-用語集) を参照。

---

## 3. ハンズオン

Step 04 の確かめ用のファイル（`try_*.py`・`type_mistakes.py`・`broken/`）は片付けてから始める。`faq-app/` で作業する。

### 3.1 Ruff と mypy を dev 依存に入れる

開発のときだけ使うツールは、`--dev` で dev グループに入れる（検証済み）。

```bash
uv add --dev ruff mypy
```

実行結果:

```text
$ uv add --dev ruff mypy
Resolved 29 packages in 749ms
   Building faq @ file:///path/to/faq-app
      Built faq @ file:///path/to/faq-app
Prepared 1 package in 37ms
Uninstalled 1 package in 2ms
Installed 7 packages in 49ms
 + ast-serialize==0.13.1
 ~ faq==0.1.0 (from file:///path/to/faq-app)
 + librt==0.16.0
 + mypy==2.4.1
 + mypy-extensions==1.2.0
 + pathspec==1.1.1
 + ruff==0.17.4
```

- `pyproject.toml` の `[dependency-groups]` の `dev` に `"mypy>=2.4.1"` と `"ruff>=0.17.4"` が足された。`devDependencies` にあたる
- `uvx ruff` でも動くが、プロジェクトに入れておくと全員が lockfile の同じ版を使う。mypy はプロジェクトを import するので、`uvx` ではなく `uv run` で動かす（[Step 04](04-typing.md) §3.7）

### 3.2 `ruff check` で未使用の import を見つけ、`--fix` で直す

設定を何も書かずに lint する（検証済み）。

実行結果:

```text
$ uv run ruff check
F401 [*] `pathlib.Path` imported but unused
 --> categories.py:3:21
  |
1 | import json
2 | from collections import Counter
3 | from pathlib import Path
  |                     ^^^^
help: Remove unused import: `pathlib.Path`
…（中略: 6 行）…
Found 1 error.
[*] 1 fixable with `--fix`.
$ uv run ruff check --fix
Found 1 error (1 fixed, 0 remaining).
```

- [Step 02](02-language.md) の `categories.py` にわざと残した `from pathlib import Path` を、既定のルールだけで見つけた。`F401` の `F` は Pyflakes 由来のルールを表す
- `[*]` は自動で直せる印である。`--fix` で import の行が消えた。ESLint と同じく、直せない指摘は残り、終了コードが 1 になる
- 公式の tutorial も "If you're introducing a linter for the first time, **the default rule set is a great place to start**" と書いている。通し課題は既定のルールのままにする

### 3.3 `ruff format` で整形する

通し課題の 8 ファイルは、`ruff format --check` で `8 files already formatted` だった（検証済み）。整形が何をするかを見るため、崩した `fmt_demo.py` を作る（検証済み）。

```python
labels = {'IT':'情報システム部','経費':'経理部'}
def owner(category:str)->str:
    return labels.get(category,'総務部')
```

実行結果:

```text
$ uv run ruff format --check fmt_demo.py
unformatted: File would be reformatted
 --> fmt_demo.py:1:11
  |
  - labels = {'IT':'情報システム部','経費':'経理部'}
  - def owner(category:str)->str:
  -     return labels.get(category,'総務部')
1 + labels = {"IT": "情報システム部", "経費": "経理部"}
2 +
3 +
4 + def owner(category: str) -> str:
5 +     return labels.get(category, "総務部")
  |

1 file would be reformatted
$ uv run ruff format fmt_demo.py
1 file reformatted
```

- 引用符は `"` にそろい、トップレベルの定義の前には空行が 2 行入る（PEP 8 の流儀）。行の長さの既定は 88 で、超えると括弧の中で折り返す
- `--check` は直さずに差分を出し、終了コード 1 で終わる。commit の前や CI では `--check` を使う
- 公式 docs は Ruff の formatter を "designed as a drop-in replacement for Black" としている。Prettier と同じく、設定項目は少ない

### 3.4 ルールを足すときは `extend-select`

ルールの選び方は 2 つある。`select` は**既定を置き換え**、`extend-select` は**既定に足す**。違いを確かめるため、`categories.py` に未使用の import を戻し、import の並び順のルール群 `I` を 2 通りで指定した（検証済み）。並び順の `I001` は 0.16 から既定に入っているので、ここで見るのは `select` と `extend-select` の違いだけである。

実行結果:

```text
$ uv run ruff check --select I
All checks passed!
$ uv run ruff check --extend-select I --output-format concise
categories.py:3:21: F401 [*] `pathlib.Path` imported but unused
Found 1 error.
[*] 1 fixable with `--fix`.
```

`--select I` では既定の 413 のルールが外れ、`F401` が出なくなった。確かめた後は `uv run ruff check --fix` で import を消して元に戻した。`pyproject.toml` に書くときも同じである（公式 docs 準拠・未実行: 通し課題は既定のルールのままにするため）。

```toml
[tool.ruff.lint]
extend-select = ["S"]  # 既定に flake8-bandit（セキュリティ）を足す

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # テストでは assert を許す
```

- 1 行だけ止めるなら、その行の末尾に `# noqa: F401` と書く。`noqa` は同じ行にしか効かない。前の行に書くなら `# ruff: ignore[F401]`（0.16 から。[Ruff](../topics/ruff.md)）
- 公式 docs の linter のページの guidelines は "Prefer `lint.select` over `lint.extend-select` to make your rule set explicit." と書き、tutorial は既定のルールから始めるよう勧める。どちらも公式の方針である。本ガイドは、既定の 413 のルールを残したまま足せる `extend-select` を使う。`select` を使うなら、残したい既定のルールも自分で並べる。0.16 の告知は、旧来の既定に戻したい場合に `select = ["E4", "E7", "E9", "F"]` を示している
- ルールの分類・`ALL`・`target-version` の決まり方は [Ruff](../topics/ruff.md) で扱う

### 3.5 mypy の設定を `pyproject.toml` にまとめる

Step 04 では `mypy src type_mistakes.py` のように毎回場所を渡した。設定に書けば、誰が回しても同じ検査になる。`pyproject.toml` の末尾に足す（検証済み）。

```toml
[tool.mypy]
files = ["src"]
strict = true
plugins = ["pydantic.mypy"]
```

実行結果:

```text
$ uv run mypy
…（中略: 4 行）…
Success: no issues found in 5 source files
```

- `files` は、コマンドラインで場所を渡さなかったときに検査する場所である。公式 docs: "A comma-separated list of paths which should be checked by mypy if none are given on the command line."
- `strict = true` は `tsconfig.json` の `"strict": true` と同じく、複数のフラグをまとめて有効にする。中身は `mypy --help` に一覧がある
- `plugins` は §3.6 で扱う

`strict` の効き目を見るため、型を書かない関数を `src/faq/search.py` の末尾に足す（検証済み）。

```python
def count_by_category(faqs):
    counts = {}
    for faq in faqs:
        counts[faq.category] = counts.get(faq.category, 0) + 1
    return counts
```

実行結果:

```text
$ uv run mypy
src/faq/search.py:14: error: Function is missing a type annotation  [no-untyped-def]
src/faq/search.py:15: error: Need type annotation for "counts" (hint: "counts: dict[<type>, <type>] = ...")  [var-annotated]
Found 2 errors in 1 file (checked 5 source files)
```

- `strict = false` に戻して同じコードを回すと、`Success: no issues found in 5 source files` で通った（検証済み）。mypy は既定で、型の無い関数を検査しない（[Step 04](04-typing.md) §5）。`strict` はそれを誤りにする
- 引数と戻り値に `faqs: Iterable[Faq]` と `-> dict[Category, int]`、`counts` に `dict[Category, int]` を書くと通った（検証済み）。確かめた後は関数を消して元に戻した

### 3.6 Pydantic のモデルを mypy に正しく読ませる

`pydantic.mypy` プラグインの効き目を、Step 04 の `Faq`（`frozen=True`・`extra="forbid"`）で確かめる。3 つの誤りを入れた `pydantic_demo.py`（検証済み）。

```python
from faq.models import Faq

faq = Faq(id="faq-13", category="経理", question="締め日は？", answer="25 日")
faq.question = "変更"  # frozen=True のモデルへの代入
Faq(id="faq-14", category="IT", question="q", answer="a", owner="総務部")  # 未知のキー
```

プラグインあり（§3.5 の設定）と、`pyproject.toml` の `plugins = ["pydantic.mypy"]` の行を一時的に外したプラグインなしで、それぞれ回した（外した行は後で戻した）。1 本目がプラグインあり、2 本目がプラグインなしである。

実行結果:

```text
$ uv run mypy pydantic_demo.py
pydantic_demo.py:4: error: Property "question" defined in "Faq" is read-only  [misc]
pydantic_demo.py:5: error: Unexpected keyword argument "owner" for "Faq"  [call-arg]
Found 2 errors in 1 file (checked 1 source file)
$ uv run mypy pydantic_demo.py
pydantic_demo.py:3: error: Argument "category" to "Faq" has incompatible type "Literal['経理']"; expected "Literal['経費', '勤怠', 'IT', '総務', '出張', 'セキュリティ']"  [arg-type]
pydantic_demo.py:5: error: Unexpected keyword argument "owner" for "Faq"  [call-arg]
Found 2 errors in 1 file (checked 1 source file)
```

どちらも 2 件で、見逃したものが違う。プラグインありは `frozen=True` への代入を見つけたが、`"経理"` を見逃した。プラグインなしはその逆である。

- プラグインが `"経理"` を見逃すのは、Pydantic が既定で値を変換する（`"1"` → `1`）からである。公式 docs: "the plugin will use `Any` for field annotations when synthesizing the `__init__()` method, unless `init_typed` is set or strict mode is enabled on the model."
- `pyproject.toml` に `[tool.pydantic-mypy]` と `init_typed = true` を足すと、3 件すべてを報告した。`src` の検査も `Success` のままだった（検証済み）。通し課題の設定はプラグインだけにしている。`init_typed = true` にすると、`Faq(**d)` のように dict を展開して作るコードも、値が `str` に広がるため `arg-type` として報告される（[Step 06](06-testing.md) のテストの `Faq(**VALID)` で出た。検証済み）。足すなら、そうした箇所を `Faq.model_validate(d)` に直す
- Pydantic の docs は、プラグインを "tested against the latest mypy version" としている。mypy を上げるときは Pydantic も上げる

> **ポイント**: 通し課題が型チェッカーに mypy を使うのは、この Pydantic のプラグインがあるからである。mypy は Python の GitHub 組織（`python/mypy`）で開発されている。pyright・ty などとの比較は [型チェッカーの比較](../topics/type-checkers.md) で扱う。

### 3.7 commit の前に回す（pre-commit / prek）

Ruff・`uv.lock` の更新・mypy を commit のたびに回す `.pre-commit-config.yaml`（検証済み）。

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.4
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.13.7
    hooks:
      - id: uv-lock
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: unsupported  # pre-commit 4.4.0 より前は system
        types: [python]
        pass_filenames: false
```

- `ruff-check` は `--fix` 付きで、`ruff-format` より**前**に置く。ruff-pre-commit の README: "When running with `--fix`, Ruff's lint hook should be placed _before_ Ruff's formatter hook"
- `uv-lock` は、`pyproject.toml` を変えたのに `uv.lock` を更新し忘れるのを防ぐ（uv の docs が案内するフック）
- mypy は `repo: local` にし、`uv run mypy` で `.venv` の mypy とプロジェクトを使う。`pass_filenames: false` で、変えたファイルではなく `files` 全体を検査する
- ruff-pre-commit 0.17.4 の `ruff-format` は、既定で Markdown のコードブロックも整形する。README.md の `python` のブロックが書き換わって commit が止まることがある。避け方は [Ruff](../topics/ruff.md) の §6
- `language: unsupported` は、pre-commit 4.4.0 で `system` から改名されたものである。公式 docs は `system` を "the alias will be removed in a future version" としている。この節の記録は `system` で取ったが、`unsupported` でも prek・pre-commit の両方で全部 Passed だった（検証済み）

git の作業ツリーで、フックを入れて全ファイルに回す（検証済み）。

実行結果:

```text
$ uvx prek@0.5.10 install
…（中略: 3 行）…
Installed Git hook at `.git/hooks/pre-commit`
$ uvx prek@0.5.10 run --all-files
ruff check...............................................................Passed
ruff format..............................................................Passed
uv-lock..................................................................Passed
mypy.....................................................................Passed
```

次に、`src/faq/search.py` の先頭に `import os` を足して `git add` し、commit する（検証済み）。

実行結果:

```text
$ git commit -m "add search helpers"
ruff check...............................................................Failed
- hook id: ruff-check
- description: Run 'ruff check' for extremely fast Python linting
- files were modified by this hook

  Found 1 error (1 fixed, 0 remaining).
ruff format..............................................................Passed
uv-lock..............................................(no files to check)Skipped
mypy.....................................................................Passed
$ git diff --stat
 src/faq/search.py | 1 -
 1 file changed, 1 deletion(-)
```

- フックがファイルを書き換えると、直せても `Failed` になり commit は止まる。直した結果は作業ツリーに残る（`git diff` の 1 行の削除）ので、確かめて `git add` し、もう一度 commit する。lint-staged と違い、自動では stage し直さない
- `uv-lock` が `Skipped` なのは、`pyproject.toml` も `uv.lock` も変えていないからである。フックは既定で、commit するファイルだけを対象にする
- 同じ設定を `uvx pre-commit@4.7.0 run --all-files` でも回し、4 つとも Passed だった（検証済み）。prek の README は "It is fully compatible with pre-commit configurations and hooks, so you can use it as a drop-in replacement without changing your setup." と書き、Python を必要としない単一のバイナリとして配っている
- ここでは版を固定するため `uvx prek@0.5.10 install` で入れた。こうして入れたフックは uv のキャッシュの中の `prek` を絶対パスで指すので、`uv cache clean` の後は commit が止まる（§5）。長く使うなら、先に `uv tool install prek` してから `prek install` する
- 版を上げるときは、pre-commit は `autoupdate`、prek 0.5.10 は `update` を使う（`--help` で確認）。`rev: v0.17.4` と dev 依存の `ruff>=0.17.4` は別々に固定しているので、片方だけ上げない

### 3.8 エディタでも同じ設定を使う

どちらのエディタも、Ruff は `pyproject.toml` の `[tool.ruff]` を読む。型の表示は、エディタが使う型チェッカーしだいで、commit の前に回す mypy と同じとは限らない。

Zed は Ruff を最初から使い、保存のたびに整形する。保存時に lint の自動修正と import の整列も行う設定（抜粋・単体では動かない）。

```json
{
  "languages": {
    "Python": {
      "code_actions_on_format": {
        "source.organizeImports.ruff": true,
        "source.fixAll.ruff": true
      }
    }
  }
}
```

- Zed の型の表示は basedpyright が担う。Zed の docs: "By default, basedpyright is the primary language server, and Ruff is used for formatting and linting." Zed は basedpyright を pyright と同じ `standard` モードで動かす。mypy の language server は組み込まれていない
- ty や pyrefly に替えるなら、`languages.Python.language_servers` に `["ty", "!basedpyright", "..."]` のように並べる。Zed は `.venv` を toolchain として見つけ、ターミナルでも有効にする

VS Code は、Ruff の拡張機能（`charliermarsh.ruff`）と mypy の拡張機能（`ms-python.mypy-type-checker`）を入れる（抜粋・単体では動かない）。

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "mypy-type-checker.importStrategy": "fromEnvironment"
}
```

- mypy の拡張機能の `importStrategy` は、既定の `useBundled` だと拡張機能に同梱の mypy を使う。`fromEnvironment` にすると、選んだ環境（`.venv`）の mypy を使う。`.venv` の mypy 2.4.1 と、`.venv` に入った `pydantic.mypy` で検査できる
- Python の拡張機能が使う Pylance の `python.analysis.typeCheckingMode` は、既定が `off` である。mypy の拡張機能と両方で型の誤りを出させると、同じ誤りが 2 回並ぶ

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| Ruff と mypy は dev 依存に入れ、`uv run` で回す | `uvx ruff`・`uvx mypy` を人ごとの版で回す | lockfile の版が全員に効く。mypy は `uvx` からプロジェクトを import できない（[Step 04](04-typing.md) §3.7） |
| lint は既定のルールから始め、足すときは `extend-select` | 既定を残すつもりで `select` に 1 グループだけ書く。`ALL` を考えずに入れる | tutorial が既定から始めるよう勧めている。`select` は既定を置き換える（§3.4）。docs は `ALL` を "Use `ALL` with discretion." とし、"will implicitly enable new rules whenever you upgrade" と書く |
| 例外は `per-file-ignores` か、その行の `# noqa: <code>` にする | コードなしの `# noqa`・ファイル全体の無効化 | コードなしの `# noqa` はその行のすべての違反を隠す（公式 docs の例 "Ignore _all_ violations."） |
| `[tool.mypy]` に `files` と `strict = true` を書き、`uv run mypy` を引数なしで回す | 人ごとに場所とフラグを渡す | 誰が回しても同じ検査になる。`strict` が無いと型の無い関数が通る（§3.5） |
| Pydantic を使うなら `plugins = ["pydantic.mypy"]`。コンストラクタでモデルを作るなら `init_typed = true` も足す | プラグイン無しでモデルを検査する | プラグイン無しでは `frozen` への代入を、プラグインだけではフィールドの型の誤りを見逃した（§3.6） |
| `ruff-check --fix` を `ruff-format` の前に置く | 整形の後に自動修正を置く | ruff-pre-commit の README の指示。修正の結果を整形し直すため |
| ローカルのフックは `language: unsupported`・`entry: uv run mypy`・`pass_filenames: false` | `language: system` を新しく書く | pre-commit 4.4.0 で改名され、`system` は将来消える別名になった（§3.7） |
| フックの `rev` と dev 依存の版を一緒に上げる | 片方だけ上げる | 手元とフックで Ruff の版が食い違い、結果が変わる |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| commit すると `ruff check ... Failed` と `files were modified by this hook` で止まる（検証中に発生） | `--fix` がファイルを直した。直したものは作業ツリーにあり、まだ stage されていない | `git diff` で確かめて `git add` し、もう一度 commit する |
| `ruff check --select I` が `All checks passed!` になり、未使用の import を報告しない（検証で再現） | `select` は既定のルールを置き換える | `extend-select` を使う。`select` を使うなら既定にあたるルールも書く |
| 型を書いていない関数があるのに、mypy が `Success` になる（検証で再現） | mypy は既定で、型の無い関数を検査しない | `strict = true`。段階的に入れるなら `check_untyped_defs = true` |
| `Faq(category="経理", ...)` を mypy が報告しない（検証で再現） | Pydantic のプラグインは、既定でコンストラクタのフィールドを `Any` として扱う | `[tool.pydantic-mypy]` に `init_typed = true` |
| `frozen=True` のモデルへの代入を mypy が報告しない（検証で再現） | `pydantic.mypy` プラグインを入れていない | `[tool.mypy]` に `plugins = ["pydantic.mypy"]` |
| clone した直後の環境で、commit してもフックが走らない | git のフックはリポジトリに入らない。husky の `prepare` のように自動で入れる仕組みも無い | 各自が 1 回 `prek install`（または `pre-commit install`）を実行する。README に書いておく。`uvx prek install` で入れたフックは uv のキャッシュの中の `prek` を絶対パスで指すので、`uv cache clean` の後や、`prek` が PATH に無い環境では `exec: prek: not found` で commit が止まる。長く使うなら `uv tool install prek` してから `prek install` する（検証で再現） |
| エディタの型の表示と `uv run mypy` の結果が食い違う | Zed は basedpyright、VS Code は Pylance か同梱の mypy を使い、`.venv` の mypy とは別物である | 合否は `uv run mypy` で決める。VS Code は `mypy-type-checker.importStrategy` を `fromEnvironment` |

---

## 6. 次のステップ

- [Step 06: テスト](06-testing.md) — pytest でテストを書き、mypy の `files` に `tests` も足す。自分で書いたテストも `ruff format --check` にかける
- Ruff のルールと設定を詳しく引くなら [Ruff](../topics/ruff.md)、mypy 以外の型チェッカーを選ぶなら [型チェッカーの比較](../topics/type-checkers.md)
- 同じ検査を GitHub Actions で回すのは [Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ)

---

## 出典

| 情報源 | URL |
|---|---|
| Ruff — Tutorial / The Ruff Linter / The Ruff Formatter / Configuring Ruff | https://docs.astral.sh/ruff/tutorial/ ・ https://docs.astral.sh/ruff/linter/ ・ https://docs.astral.sh/ruff/formatter/ ・ https://docs.astral.sh/ruff/configuration/ （2026-11-08 確認、Context7 `/astral-sh/ruff/0.17.3` と GitHub のタグ 0.17.4 の `docs/` から原文を確認。既定のルールから始める方針、`select` と `extend-select`、`# noqa`、Black 互換） |
| Ruff v0.16.0 | https://astral.sh/blog/ruff-v0.16.0 （2026-11-08 確認。"Ruff now enables 413 rules by default, up from 59 in previous versions."） |
| Ruff — Editor setup | https://docs.astral.sh/ruff/editors/setup/ （2026-11-08 確認。Zed の `source.fixAll.ruff`・`source.organizeImports.ruff`、VS Code の拡張機能） |
| ruff-vscode README | https://github.com/astral-sh/ruff-vscode （2026-11-08 確認。`editor.defaultFormatter`・`editor.codeActionsOnSave`） |
| mypy — The mypy configuration file / README | https://mypy.readthedocs.io/en/stable/config_file.html ・ https://github.com/python/mypy （2026-11-08 確認。`files`・`strict`・`pyproject.toml` の `[tool.mypy]`） |
| Pydantic — Mypy | https://docs.pydantic.dev/latest/integrations/mypy/ （2026-11-08 確認。`plugins = ["pydantic.mypy"]`、`init_typed`・`init_forbid_extra`、最新の mypy で試験していること） |
| pre-commit | https://pre-commit.com/ （2026-11-08 確認。`pass_filenames`、`language: unsupported` と `system` の別名、`autoupdate`、git のフックでは変更したファイルだけを対象にすること） |
| prek README | https://github.com/j178/prek （2026-11-08 確認。pre-commit との互換、単一のバイナリ、`uv add --dev prek` での導入） |
| ruff-pre-commit README / Using uv in pre-commit | https://github.com/astral-sh/ruff-pre-commit ・ https://docs.astral.sh/uv/guides/integration/pre-commit/ （2026-11-08 確認。`ruff-check` と `ruff-format` の順序、`uv-lock`） |
| Zed — Python | https://zed.dev/docs/languages/python （2026-11-08 確認、GitHub の `docs/src/languages/python.md`。basedpyright が既定、`standard` モード、`language_servers`、toolchain） |
| VS Code — Linting Python / Settings Reference / vscode-mypy README | https://code.visualstudio.com/docs/python/linting ・ https://code.visualstudio.com/docs/python/settings-reference ・ https://github.com/microsoft/vscode-mypy （2026-11-08 確認。`ms-python.mypy-type-checker`、`importStrategy`、`typeCheckingMode` の既定 `off`） |

### 確認できなかった事項

- **Ruff 0.17.4 で既定のルールが何個か**。413 は 0.16.0 の告知の数である。`ruff check --show-settings` の一覧を数えた値は数え方で揺れたので、載せていない
- **VS Code の mypy の拡張機能が、いま何版の mypy を同梱しているか**。README の記載が最新のリリースと合っているかを確かめていない。そのため本文では版を書かず、`fromEnvironment` を勧めるだけにした
- **Zed・VS Code での実際の表示**。エディタの設定は公式 docs から写した抜粋で、このステップでは動かしていない

- 関連: [Python 学習ガイド](../README.md) / [Step 04: 型](04-typing.md) / [Step 06: テスト](06-testing.md) / [Ruff](../topics/ruff.md) / [型チェッカーの比較](../topics/type-checkers.md) / [uv](../topics/uv.md)
