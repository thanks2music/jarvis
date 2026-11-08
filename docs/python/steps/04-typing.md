# Step 04: 型 — 型ヒントで静的に、Pydantic で実行時に守る

> 出典（一次情報）:
> - [typing — Support for type hints (docs.python.org)](https://docs.python.org/3/library/typing.html) — 実行時は型ヒントを検査しないこと、`TypedDict`・`Protocol`・`type` 文
> - [What's New In Python 3.14 (docs.python.org)](https://docs.python.org/3/whatsnew/3.14.html) — 型ヒントの遅延評価（PEP 649 / 749）と `from __future__ import annotations` の扱い
> - [Static Typing with Python (typing.python.org)](https://typing.python.org/en/latest/) — `Protocol` による構造的な部分型と、`py.typed`（PEP 561）の現行の仕様
> - [Models / Performance (docs.pydantic.dev)](https://docs.pydantic.dev/latest/concepts/models/) — `ConfigDict` と `model_validate_json`
> - [Running mypy — Missing imports (mypy.readthedocs.io)](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports) — "missing library stubs or py.typed marker" の意味と対処
> - [Tools (docs.astral.sh)](https://docs.astral.sh/uv/concepts/tools/) — mypy を `uvx` ではなく `uv run` で動かす理由
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・Pydantic 2.14.3・mypy 2.4.1 で検証）

TypeScript では、型を書いて `tsc` で検査し、外から来る JSON は Zod で検証する。Python も同じ二段構えで、**型ヒント**を書いて型チェッカー（mypy など）で検査し、外から来るデータは **Pydantic** で検証する。
違うのは、Python には型を消す工程すら無く、型ヒントを付けたまま実行し、実行時には一切検査しないことである。
このステップでは、[Step 03: プロジェクト構成](03-project.md) の dataclass の `Faq` を Pydantic のモデルに置き換えて壊れたデータを読み込み時に弾き、型の誤りを mypy で実行前に見つける。
シリーズ全体は [Python 学習ガイド](../README.md)、次は [Step 05: 品質ツール](05-quality.md) を参照。

---

## 1. TL;DR

- **型ヒントは実行時に検査されない**。`Path` を受ける関数に `str` を渡してもその場では落ちず、中で `.open()` を呼んだところで `AttributeError` になる（§3.6）。型の誤りは型チェッカーで実行前に見つける。
- **書き方は TS とよく似ている**。`list[str]`・`dict[str, int]`・`X | None`・`Literal[...]`・`type 名前 = ...`・`def first[T](xs: list[T]) -> T`（§3.1）。ただし**普通のクラスは名前で判定する**。TS のように形で判定させたいときは `Protocol` を使う（§3.2）。
- **外から来るデータは Pydantic で検証する**。Zod のスキーマにあたる。`Faq.model_validate_json(line)` が JSON の解析と検証を 1 回で行い、誤りをまとめて `ValidationError` にする（§3.3〜§3.5）。
- **mypy は、`py.typed` の無いインストール済みのパッケージを解析しない**。uv はプロジェクト自身もパッケージとして入れるので、`type_mistakes.py` だけを渡すと何も報告しない。`src` も一緒に渡すか、`src/faq/py.typed` を置くと、4 件の誤りをすべて報告した（§3.7）。pyright・ty・basedpyright も同じ 4 件、pyrefly は設定ファイルが無いと `basic` プリセットになり 0 件だった。どれを選ぶかは後で扱う（§3.8）。
- Python 3.14 から型ヒントの評価が遅延されるようになった。前方参照に引用符も `from __future__ import annotations` も要らない（§3.6）。

---

## 2. Node.js / Bun との対応

型の書き方:

| やりたいこと | TypeScript | Python | 補足 |
|---|---|---|---|
| 文字列の配列 | `string[]` | `list[str]` | 3.9 から組み込みの型に `[]` を付けられる（PEP 585）。`typing.List` は古い書き方 |
| キーと値の型が決まった辞書 | `Record<string, number>` | `dict[str, int]` | |
| 無いかもしれない値 | `T \| null` / `T \| undefined` | `T \| None` | 3.10 から（PEP 604）。`None` は 1 種類しかない |
| 文字列リテラルの合併 | `"a" \| "b"` | `Literal["a", "b"]` | PEP 586 |
| 型の別名 | `type A = ...` | `type A = ...` | 3.12 から（PEP 695）。右辺は使われるまで評価されない |
| ジェネリックな関数 | `function first<T>(xs: T[]): T` | `def first[T](xs: list[T]) -> T` | 3.12 から（PEP 695） |
| 関数の型 | `(s: string) => number` | `Callable[[str], int]` | `collections.abc` から import する |
| dict の形と、省略できるキー | `{ id: string; owner?: string }` | `TypedDict`（PEP 589）と `owner: NotRequired[str]` | 実行時はただの `dict`。引数なら `owner: str \| None = None` と既定値を書く |
| 形で判定する型 | `interface`（TS は常に構造的） | `Protocol`（PEP 544） | 普通の `class` は名前で判定する |
| 型を検査する | `tsc --noEmit` | mypy / pyright / ty など | Python 本体には付いてこない。別に入れる |

検証（Zod と Pydantic）:

| やりたいこと | Zod | Pydantic |
|---|---|---|
| スキーマを定義する | `z.object({ ... })` | `class Faq(BaseModel): ...` |
| 静的な型を得る | `z.infer<typeof Faq>` | 不要（クラスがそのまま型になる） |
| 検証する | `Faq.parse(data)` | `Faq.model_validate(data)` |
| JSON 文字列を検証する | `Faq.parse(JSON.parse(s))` | `Faq.model_validate_json(s)`（解析と検証を 1 回で行う） |
| 失敗したとき | `ZodError`（`safeParse` なら結果として返る） | `ValidationError` を投げる。`try` / `except` で受ける |
| 未知のキー | 既定で捨てる。`z.strictObject` で拒否 | 既定（`extra="ignore"`）で捨てる。`extra="forbid"` で拒否 |
| 変更を禁じる | `.readonly()`（`Object.freeze`） | `frozen=True` |
| 正規表現・最小の長さ | `z.string().regex(...)` / `.min(1)` | `Field(pattern=...)` / `Field(min_length=1)` |
| 型の変換 | `z.coerce.number()` と書いたときだけ | **既定で変換する**（lax モード。`"123"` → `123`）。`strict=True` で止める |

対応の全体は [Pydantic](../topics/pydantic.md) で扱う。用語は [用語集](../README.md#8-用語集) を参照。

---

## 3. ハンズオン

§3.1 と §3.2 は、[Step 02](02-language.md) と同じ使い捨てのディレクトリ（`py-scratch/`）で書き方を試す。§3.3 からは [Step 03](03-project.md) の `faq-app/` を進める。

### 3.1 型ヒントの書き方を TS と比べる

よく使う書き方を並べ、わざと 3 つの誤りを入れた `hints.py`（検証済み）。

```python
from collections.abc import Callable
from typing import Literal

type Level = Literal["info", "warn", "error"]  # TS: type Level = "info" | "warn" | "error"


def first[T](xs: list[T]) -> T:  # TS: function first<T>(xs: T[]): T
    return xs[0]


def parse_port(s: str) -> int | None:  # TS: number | undefined
    return int(s) if s.isdigit() else None


def apply(f: Callable[[str], int], s: str) -> int:  # TS: (f: (s: string) => number, s: string)
    return f(s)


sizes: dict[str, int] = {"faq-01": 120}  # TS: Record<string, number>
level: Level = "debug"  # 誤り 1: Literal に無い値
n: int = first(["a", "b"])  # 誤り 2: str を int に入れている
apply(len, 1)  # 誤り 3: str のところに int を渡している
```

実行結果:

```text
$ uv run hints.py
Traceback (most recent call last):
…（中略: 1 行）…
    apply(len, 1)  # 誤り 3: str のところに int を渡している
…（中略: 3 行）…
TypeError: object of type 'int' has no len()
$ uv run --with mypy==2.4.1 mypy hints.py
hints.py:20: error: Incompatible types in assignment (expression has type "Literal['debug']", variable has type "Literal['info', 'warn', 'error']")  [assignment]
hints.py:21: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
hints.py:22: error: Argument 2 to "apply" has incompatible type "int"; expected "str"  [arg-type]
Found 3 errors in 1 file (checked 1 source file)
```

- 実行すると、誤り 1 と 2 は何事もなく通った。誤り 3 も、型の誤りとしてではなく、`len(1)` を呼んだ時点の `TypeError` として落ちた。mypy は 3 件とも実行せずに報告した（pyright 1.1.414 でも同じ 3 件）
- `def first[T]` の `[T]` が TS の `<T>` にあたる（PEP 695）。3.11 以前は `T = TypeVar("T")` を別に書いていた
- `Callable` や `Iterable` は `collections.abc` から import する（`typing.Callable` は 3.9 から非推奨の別名）。`type Level = ...` は `TypeAliasType` を作り、右辺は使われるまで評価されない（遅延評価）

### 3.2 名前で判定する型と、形で判定する型

TS との一番大きな違いを確かめる `shapes.py`（検証済み）。`Draft` は `Faq` と同じ形だが、`Faq` を継承していない。

```python
from dataclasses import dataclass
from typing import NotRequired, Protocol, TypedDict


class FaqDict(TypedDict):  # dict の形を表す。実行時はただの dict
    id: str
    question: str
    owner: NotRequired[str]  # TS の owner?: string


class HasQuestion(Protocol):  # TS の interface と同じく、形で判定する
    question: str


@dataclass
class Faq:
    question: str


@dataclass
class Draft:  # Faq と同じ形だが、Faq を継承していない
    question: str


d: FaqDict = {"id": "faq-01", "question": "締め日は？"}
bad: FaqDict = {"id": "faq-02"}  # 誤り 1: question が無い
f: Faq = Draft("下書き")  # 誤り 2: Draft は Faq ではない（名前で判定する）
h: HasQuestion = Draft("下書き")  # OK: question を持つので HasQuestion を満たす
print(type(d).__name__, type(bad).__name__, f.question, h.question)
```

実行結果:

```text
$ uv run shapes.py
dict dict 下書き 下書き
$ uv run --with mypy==2.4.1 mypy shapes.py
shapes.py:26: error: Missing key "question" for TypedDict "FaqDict"  [typeddict-item]
shapes.py:27: error: Incompatible types in assignment (expression has type "Draft", variable has type "Faq")  [assignment]
Found 2 errors in 1 file (checked 1 source file)
```

- 実行時はすべて通った。Python は実行時に型を見ず、`question` 属性があれば動く（ダックタイピング）
- mypy は `f: Faq = Draft(...)` を誤りとした（pyright 1.1.414 も同じ 2 件）。**Python の普通のクラスは、継承関係（名前）で判定する**。TS はクラスでも形で判定するので、これが通る。継承しなくても形で満たせる型が欲しいときに `Protocol` を使う。PEP 544 の題名どおり "static duck typing" である
- `TypedDict` は dict の形を表すだけで、実行時は `dict` のまま（出力の先頭の `dict dict`）。公式 docs も "This expectation is not checked at runtime but is only enforced by type checkers." と書いている

### 3.3 Pydantic で `Faq` を定義し直す

Step 03 の `@dataclass(frozen=True)` の `Faq` を、Pydantic のモデルにする。`uv add "pydantic>=2.14"` で依存に加えると、pydantic 2.14.3 と pydantic-core 2.50.4 などが入り、プロジェクト自身も `~ faq==0.1.0 (from file:///path/to/faq-app)` と入れ直される（検証済み）。続けて `src/faq/models.py` を書き換える（検証済み）。

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type Category = Literal["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]


class Faq(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=r"^faq-\d{2}$")
    category: Category
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
```

`src/faq/loader.py` は、`Faq(**json.loads(line))` を `Faq.model_validate_json(line)` に変え、要らなくなった `import json` を消す。`uv run faq` は前と同じく `12 件の FAQ を読み込んだ` と出る（検証済み）。

- `type Category = Literal[...]` は 6 つのカテゴリだけを許す型である。型チェッカーにも Pydantic にも効く（Pydantic は `type` 文の別名を理解する）
- `frozen=True` は代入を禁じ、代入すると `ValidationError`（`frozen_instance`）になる。`extra="forbid"` は未知のキーを拒否する。既定の `extra="ignore"` は**未知のキーを黙って捨てる**（どちらも検証済み）
- `Field(pattern=..., min_length=1)` で、型だけでは表せない制約を足す。`model_validate_json` は JSON の解析と検証を Pydantic の中でまとめて行い、公式 docs は自分で dict にしてから検証するより "generally considered faster" としている
- `Faq` はクラスなので、そのまま型ヒントにも使える。Zod の `z.infer` にあたる手順は要らない

### 3.4 見つからないかもしれない値を `Faq | None` で返す

検索の関数を `src/faq/search.py` に足す（検証済み）。

```python
from collections.abc import Iterable

from faq.models import Category, Faq


def find_by_id(faqs: Iterable[Faq], faq_id: str) -> Faq | None:
    return next((faq for faq in faqs if faq.id == faq_id), None)


def by_category(faqs: Iterable[Faq], category: Category) -> list[Faq]:
    return [faq for faq in faqs if faq.category == category]
```

`try_search.py` で、`find_by_id(faqs, "faq-05")`・`by_category(faqs, "IT")` の id・`find_by_id(faqs, "faq-99")` を順に表示する（検証済み）。

実行結果:

```text
$ uv run try_search.py
id='faq-05' category='IT' question='社内 VPN につながりません。' answer='VPN クライアントを再起動し、それでもつながらなければ多要素認証アプリの時刻同期を確認してください。解決しない場合はヘルプデスクのチケットを起票してください。'
['faq-05', 'faq-06', 'faq-07']
None
```

- `next(ジェネレーター, None)` が `Array.prototype.find` にあたる。見つからなければ `None` を返す（TS の `find` は `undefined`）。戻り値を `Faq | None` と書いておくと、`None` を確かめずに `.question` を読んだときに型チェッカーが止める（§3.7 の `Item "None" of "Faq | None"`）。`Iterable[Faq]` はリストでもジェネレーターでも受け取れる

### 3.5 壊れたデータを読み込ませる

カテゴリが誤り・質問が空・余計なキーがある 1 行を `broken/faq.jsonl` に置き、読み込ませる（検証済み）。

```bash
mkdir -p broken && printf '%s\n' '{"id": "faq-13", "category": "経理", "question": "", "answer": "…", "owner": "総務部"}' > broken/faq.jsonl
cat > try_broken.py <<'EOF'
from pathlib import Path

from faq import load_faqs

load_faqs(Path("broken/faq.jsonl"))
EOF
```

実行結果:

```text
$ uv run try_broken.py
Traceback (most recent call last):
…（中略: 13 行）…
pydantic_core._pydantic_core.ValidationError: 3 validation errors for Faq
category
  Input should be '経費', '勤怠', 'IT', '総務', '出張' or 'セキュリティ' [type=literal_error, input_value='経理', input_type=str]
    For further information visit https://errors.pydantic.dev/2.14/v/literal_error
question
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.14/v/string_too_short
owner
  Extra inputs are not permitted [type=extra_forbidden, input_value='総務部', input_type=str]
    For further information visit https://errors.pydantic.dev/2.14/v/extra_forbidden
```

3 つの誤りが 1 回でまとめて報告された。フィールド名・理由・`type=` の識別子が並ぶので、ログからそのまま原因が分かる。`id` の `faq-13` は `pattern` に合うので通っている。

### 3.6 型ヒントは実行時に検査されない

型の誤りを 4 つ含む `type_mistakes.py`（検証済み）。

```python
from faq import load_faqs
from faq.search import by_category, find_by_id

faqs = load_faqs("data/faq.jsonl")  # Path ではなく str を渡している
hit = find_by_id(faqs, "faq-01")
print(hit.question)  # None かもしれない
print(by_category(faqs, "経理"))  # Category に無い値
print(faqs[0].categry)  # 属性名の打ち間違い
```

実行結果:

```text
$ uv run type_mistakes.py
Traceback (most recent call last):
  File "~/faq-app/type_mistakes.py", line 4, in <module>
    faqs = load_faqs("data/faq.jsonl")  # Path ではなく str を渡している
  File "~/faq-app/src/faq/loader.py", line 7, in load_faqs
    with path.open(encoding="utf-8") as f:
         ^^^^^^^^^
AttributeError: 'str' object has no attribute 'open'
```

呼び出しの時点では何も起きず、`loader.py` の中で `.open()` を呼んだところで落ちた。原因から離れた場所で、しかも最初の 1 件しか見えない。公式 docs も "The Python runtime does not enforce function and variable type annotations." と書いている。

型ヒントの評価のされ方は 3.14 で変わった。まだ定義していないクラスを型ヒントに書く `annotations_demo.py` を、§3.1 と同じ使い捨てのディレクトリで動かす（検証済み）。`faq-app/` は `requires-python = ">=3.15"` なので、そこで `--python 3.13` を付けると、uv が実行の前に拒否する（[Python の版](../topics/python-versions.md) §3.3）。

```python
def describe(faq: Faq) -> str:  # Faq はまだ定義していない（前方参照）
    return faq.question


class Faq:
    question = "締め日は？"


print(describe.__annotations__)
```

実行結果:

```text
$ uv run annotations_demo.py
{'faq': <class '__main__.Faq'>, 'return': <class 'str'>}
$ uv run --python 3.13 annotations_demo.py
Traceback (most recent call last):
…（中略: 3 行）…
NameError: name 'Faq' is not defined
$ uv run python -W error::DeprecationWarning future_demo.py
{'faq': 'Faq', 'return': 'str'}
```

- 3.13 までは型ヒントを `def` の時点で評価するので、後で定義するクラスを書くと `NameError` になる。これを避けるため、`"Faq"` と引用符で囲むか、`from __future__ import annotations`（PEP 563。型ヒントをすべて文字列のまま持つ）を書いていた
- 3.14 からは、必要になったときに評価する（PEP 649 / 749）。What's New 3.14 の原文は "It is no longer necessary to enclose annotations in strings if they contain forward references." 最後の `future_demo.py` は、先頭に `from __future__ import annotations` を足したものである。3.15 でも動き、型ヒントは文字列になった。`DeprecationWarning` を誤りにしても止まらなかった。What's New 3.14 は、この import を "now deprecated" とし、削除は 3.13 の EOL（2029 年）より後としている

### 3.7 mypy で実行前に見つける

型チェッカーを、その 1 回だけ足して動かす（検証済み）。

実行結果:

```text
$ uv run --with mypy==2.4.1 mypy type_mistakes.py
type_mistakes.py:1: error: Skipping analyzing "faq": module is installed, but missing library stubs or py.typed marker  [import-untyped]
type_mistakes.py:2: error: Skipping analyzing "faq.search": module is installed, but missing library stubs or py.typed marker  [import-untyped]
type_mistakes.py:2: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
Found 2 errors in 1 file (checked 1 source file)
```

誤りが 1 件も報告されない。uv はプロジェクト自身も `.venv` にパッケージとして入れる（§3.3 の `~ faq==0.1.0`）。mypy から見ると `faq` は「インストール済みのパッケージ」で、型情報を持つ印の `py.typed` が無いので解析を飛ばした。

直し方は 2 つある。1 つは、検査するソースも渡すことである。`uv run --with mypy==2.4.1 mypy src type_mistakes.py` とすると、`py.typed` が無くても下と同じ 4 件を報告した（検証済み）。mypy の docs も、自分のコードは "Directly specifying the directory containing the module you want to type check from the command line" で見せる方法を挙げている。もう 1 つは、型情報を持つ印を置くことである（検証済み）。

```bash
touch src/faq/py.typed
```

実行結果:

```text
$ uv run --with mypy==2.4.1 mypy type_mistakes.py
type_mistakes.py:4: error: Argument 1 to "load_faqs" has incompatible type "str"; expected "Path"  [arg-type]
type_mistakes.py:6: error: Item "None" of "Faq | None" has no attribute "question"  [union-attr]
type_mistakes.py:7: error: Argument 2 to "by_category" has incompatible type "Literal['経理']"; expected "Literal['経費', '勤怠', 'IT', '総務', '出張', 'セキュリティ']"  [arg-type]
type_mistakes.py:8: error: "Faq" has no attribute "categry"; maybe "category"?  [attr-defined]
Found 4 errors in 1 file (checked 1 source file)
```

4 件すべてを実行せずに報告し、打ち間違いには `maybe "category"?` と候補まで出した。

同じことを `uvx mypy@2.4.1 type_mistakes.py` で動かすと、`Cannot find implementation or library stub for module named "faq"` になる（検証済み）。`uvx` はプロジェクトから切り離した環境で動くからである。uv の docs の原文は "If the tool should not be isolated from the project, e.g., when running `pytest` or `mypy`, then `uv run` should be used instead of `uv tool run`." ここでは `--with` でその 1 回だけ足した。dev 依存に入れて設定を書くのは [Step 05](05-quality.md) である。

### 3.8 ほかの型チェッカーと `py.typed`

同じ `type_mistakes.py` を、ほかの型チェッカーにもかけた（検証済み）。mypy 以外は `py.typed` を置く前に実行している。

| 型チェッカー | 版 | コマンド | 報告した誤り |
|---|---|---|---|
| mypy | 2.4.1 | `uv run --with mypy==2.4.1 mypy type_mistakes.py` | `py.typed` が無いと解析を飛ばす。置くと 4 件 |
| pyright | 1.1.414 | `uv run --with pyright==1.1.414 pyright type_mistakes.py` | 4 件 |
| ty | 0.0.99 | `uv run --with ty==0.0.99 ty check type_mistakes.py` | 4 件 |
| basedpyright | 1.40.2 | `uv run --with basedpyright==1.40.2 basedpyright type_mistakes.py` | 4 件と、警告 2 件。メッセージはロケールに合わせて日本語で出た |
| pyrefly | 1.4.1 | `uv run --with pyrefly==1.4.1 pyrefly check type_mistakes.py` | 0 件。`--preset default` を付けると 4 件 |

pyrefly は、0 件の行の直後に ``No `pyrefly.toml` found — using preset `basic`.`` と出力した。`py.typed` を置いた後にプリセット無しでもう一度動かしても 0 件だったので、差を生んだのはプリセットである。どれをどの設定で使うかは [型チェッカーの比較](../topics/type-checkers.md) と [Step 05](05-quality.md) で扱い、ここでは選ばない。

`py.typed` を手で置いたのは、`uv init` の既定（アプリ）が作らないからである。ライブラリ用の `--lib` は最初から作る（検証済み）。

実行結果:

```text
$ uv init -q --lib --vcs none --author-from none libdemo && uv init -q --vcs none --author-from none appdemo && find libdemo/src appdemo/src -type f | sort
appdemo/src/appdemo/__init__.py
libdemo/src/libdemo/__init__.py
libdemo/src/libdemo/py.typed
```

- `py.typed` は中身の無いファイルで、「このパッケージは型情報を持つ」という印である。決めたのは PEP 561 で、今の仕様は typing.python.org にある。原文は "Package maintainers who wish to support type checking of their code MUST add a marker file named py.typed to their package supporting typing." 印はサブパッケージにも及ぶので、`src/faq/` に 1 つ置けば `faq.search` も対象になる
- uv の docs は、`--lib` が入れる理由を "to indicate to consumers that types can be read from the library" と書いている。`uv build` で作った wheel にもそのまま入った（`uv build` は [Step 11](../README.md#4-学習ロードマップ) で扱う）

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| `list[str]`・`dict[str, int]`・`X \| None`・`collections.abc.Callable` で書く | `typing.List`・`typing.Dict`・`typing.Callable` | typing の docs で、3.9 から非推奨の別名になっている（PEP 585） |
| 外から来るデータ（ファイル・API・設定）は、読み込む境界で Pydantic に通す | 型ヒントだけを頼りに外部のデータを信じる | 実行時は型ヒントを検査しない（§3.6）。誤りは原因から離れた場所で表に出る |
| JSON 文字列は `model_validate_json` に渡す | `model_validate(json.loads(s))` | Pydantic の Performance の docs が "In general, use `model_validate_json()` not `model_validate(json.loads(...))`" としている（`before` / `wrap` の validator がある場合は例外） |
| 自分たちで形を決めたデータは `extra="forbid"` にする | 既定の `extra="ignore"` のままにする | 既定では未知のキーを黙って捨てる（検証済み）。キーの打ち間違いに気付けない |
| mypy には検査するソース（`src`）も渡す。配る・ほかから import されるパッケージには `py.typed` を置く | `type_mistakes.py` だけを渡し、何も報告されないのを「誤りが無い」と読む | mypy は印の無いインストール済みのパッケージを解析しない（§3.7）。設定ファイルでの渡し方は [Step 05](05-quality.md) で扱う |
| 引数は `Iterable`・`Sequence`・`Mapping` で受け、戻り値は `list`・`dict` で返す | 引数を `list[Faq]` に固定する | typing の docs: "to annotate arguments, it is preferred to use an abstract collection type such as Sequence or Iterable rather than to use list"。§3.4 の `Iterable[Faq]` はリストもジェネレーターも受け取れる |
| 型チェッカーは `uv run` で動かす | `uvx mypy` | `uvx` の環境からはプロジェクトを import できない（§3.7）。uv の docs も `uv run` を指示している |
| 3.14 以上を対象にするコードには `from __future__ import annotations` を書かない | 新しいコードに足す | What's New 3.14 で非推奨になった。前方参照も引用符なしで書ける（§3.6） |
| 関数には引数と戻り値の型を書く | 型の無い関数を残す | mypy は既定で、型の無い関数の中身を検査しない（§5） |

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| mypy が `Skipping analyzing "faq": module is installed, but missing library stubs or py.typed marker  [import-untyped]` を出し、誤りを 1 件も報告しない（検証中に発生） | プロジェクト自身が `.venv` にパッケージとして入っていて、`py.typed` が無い | `mypy src type_mistakes.py` とソースも渡すか、`touch src/faq/py.typed`。ライブラリなら `uv init --lib` が最初から作る |
| pyrefly が `INFO 0 errors` で終わる（検証中に発生） | 設定ファイルが無いと `basic` プリセットになる。`py.typed` を置いても 0 件のまま | `--preset default` を付けるか、`pyrefly init` で設定ファイルを作る。設定の選び方は [型チェッカーの比較](../topics/type-checkers.md) で扱う |
| `load_faqs("data/faq.jsonl")` が `AttributeError: 'str' object has no attribute 'open'` で落ちる（検証中に発生） | 型ヒントは実行時に検査されない。誤りは呼び出しではなく `.open()` の所で表に出る | 型チェッカーで実行前に見つける。外から来る値は Pydantic で検証する |
| `uvx mypy@2.4.1 type_mistakes.py` が `Cannot find implementation or library stub for module named "faq"` を出す（検証で再現） | `uvx` はプロジェクトから切り離した環境で動く | `uv run --with mypy==2.4.1 mypy ...` か、dev 依存に入れて `uv run mypy ...` |
| `typing.get_args(Category)` が `()` を返す（検証で再現） | `type` 文の別名は `TypeAliasType` で、中身は遅延評価される `__value__` にある | `get_args(Category.__value__)` で `('経費', '勤怠', ...)` が取れる |
| `Field(pattern=r"^(?!faq-00)faq-\d{2}$")` がクラス定義の時点で `SchemaError` になり、最後の行が `error: look-around, including look-ahead and look-behind, is not supported`（検証で再現） | Pydantic v2 の `pattern` は既定で Rust の regex crate を使い、先読み・後読みと後方参照を使えない。Zod（JS の `RegExp`）の正規表現をそのまま移すと起きる | 先読みを使わない書き方にするか、`ConfigDict(regex_engine="python-re")` で Python の `re` に切り替える |
| 型を書かない関数の `sum(prices) + "円"` を mypy が報告しない（検証で再現。pyright 1.1.414 は報告した） | mypy は既定で、注釈の無い関数の中身を検査しない（"By default the bodies of functions without annotations are not type checked."） | 引数と戻り値の型を書く。すぐに書けないなら `--check-untyped-defs` |
| 3.13 以前で、後で定義するクラスを型ヒントに書くと `NameError` になる（検証で再現） | 3.13 までは型ヒントを `def` の時点で評価する | 3.14 以上を使う。3.13 以前も対象にするなら `"Faq"` と引用符で囲む |

---

## 6. 次のステップ

- [Step 05: 品質ツール](05-quality.md) — Ruff と型チェッカーを dev 依存に入れ、設定を `pyproject.toml` にまとめて、毎回同じ検査を回す
- 型チェッカーを選びたい場合は [型チェッカーの比較](../topics/type-checkers.md)、Zod との対応をもっと知りたい場合は [Pydantic](../topics/pydantic.md)

---

## 出典

| 情報源 | URL |
|---|---|
| typing — Support for type hints | https://docs.python.org/3/library/typing.html （2026-11-08 確認、Context7 `/python/cpython` 経由。実行時に検査しないこと、`TypedDict`、`typing.Callable` の非推奨、`TypeAliasType`） |
| What's New In Python 3.14 / annotationlib / Execution model | https://docs.python.org/3/whatsnew/3.14.html ・ https://docs.python.org/3/library/annotationlib.html ・ https://docs.python.org/3/reference/executionmodel.html （2026-11-08 確認。PEP 649 / 749 の遅延評価、`from __future__ import annotations` の非推奨と削除の時期） |
| What's New In Python 3.15 | https://docs.python.org/3/whatsnew/3.15.html （2026-11-08 確認。型まわりの新機能は PEP 728・747・800 で、本ステップの内容は変わらない） |
| typing.python.org — Protocols / Distributing type information | https://typing.python.org/en/latest/reference/protocols.html ・ https://typing.python.org/en/latest/spec/distributing.html （2026-11-08 確認、Context7 `/python/typing` 経由。構造的な部分型、`py.typed` の原文） |
| PEP 484 / 544 / 561 / 563 / 585 / 586 / 589 / 604 / 649 / 695 / 749 | https://peps.python.org/pep-0484/ ほか （2026-11-08 確認。状態と対象の版は https://peps.python.org/api/peps.json 。PEP 484 の "no type checking happens at runtime"） |
| Pydantic — Models / Performance / Strict Mode / Types / Standard Library Types | https://docs.pydantic.dev/latest/concepts/models/ ・ https://docs.pydantic.dev/latest/concepts/performance/ ・ https://docs.pydantic.dev/latest/concepts/strict_mode/ ・ https://docs.pydantic.dev/latest/concepts/types/ ・ https://docs.pydantic.dev/latest/api/standard_library_types/ （2026-11-08 確認、Context7 `/pydantic/pydantic/v2.14.1` 経由。`extra` の既定、`model_validate_json`、lax モード、`type` 文の別名、`pattern` の regex crate） |
| Zod — Defining schemas | https://zod.dev/api （2026-11-08 確認、Context7 `/colinhacks/zod/v4.6.7` 経由。`z.strictObject`・`z.looseObject`・`.readonly()`・`z.coerce`） |
| mypy — Running mypy / Common issues / Command line | https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports ・ https://mypy.readthedocs.io/en/stable/common_issues.html ・ https://mypy.readthedocs.io/en/stable/command_line.html （2026-11-08 確認、Context7 `/python/mypy/v2.4.0` 経由。`--check-untyped-defs`） |
| uv — Tools / Creating projects | https://docs.astral.sh/uv/concepts/tools/ ・ https://docs.astral.sh/uv/concepts/projects/init/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由。`uv run` と `uv tool run` の使い分け、`--lib` の `py.typed`） |

### 確認できなかった事項

- **pyrefly の `basic` プリセットが何を検査しないか**。公式 docs では確かめていない。0 件だったことと、プリセットを替えると 4 件になったことだけを載せた。中身は [型チェッカーの比較](../topics/type-checkers.md) で扱う
- **`from __future__ import annotations` が、いつ実行時に警告を出すようになるか**。3.15.2 で `DeprecationWarning` が出ないことは確かめた。公式 docs にあるのは「3.13 の EOL より後に削除する」までである
- **Pydantic に Zod の `safeParse` にあたる、例外を投げない検証の API があるか**。公式 docs の例が `try` / `except ValidationError` で受けていることだけを確かめた

- 関連: [Python 学習ガイド](../README.md) / [Step 03: プロジェクト構成](03-project.md) / [uv](../topics/uv.md) / [型チェッカーの比較](../topics/type-checkers.md) / [Pydantic](../topics/pydantic.md)
