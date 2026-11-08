# Step 02: 文法の差分 — JS / TS と違うところと罠を押さえる

> 出典（一次情報）:
> - [The Python Tutorial (docs.python.org)](https://docs.python.org/3/tutorial/) / [Programming FAQ](https://docs.python.org/3/faq/programming.html) — 制御構文・関数・例外・スコープの基本 / ループで作った lambda・`UnboundLocalError`
> - [The Python Language Reference (docs.python.org)](https://docs.python.org/3/reference/) — 式・複合文（`with`・`match`）・実行モデル
> - [Built-in Types (docs.python.org)](https://docs.python.org/3/builtins/stdtypes.html) — 真偽値の判定・`and` / `or`・dict の順序・str
> - [PEP 8](https://peps.python.org/pep-0008/) / [PEP 636](https://peps.python.org/pep-0636/) / [PEP 557](https://peps.python.org/pep-0557/) — 書き方の規約 / `match` のチュートリアル / dataclasses
> - [What's New In Python 3.15 (docs.python.org)](https://docs.python.org/3/whatsnew/3.15.html) — 内包表記での展開（PEP 798）・`frozendict`（PEP 814）・UTF-8 が既定に（PEP 686）
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7・Ruff 0.17.4 で検証。JS 側は Node.js 26.13.0・Bun 1.4.4 で確認）

JS / TS が書ければ、Python のコードの大半は読めば分かる。ハマるのは、**見た目が同じなのに意味が違うところ**（`==`・空の `[]` の真偽・既定引数・ループの変数）である。
このステップでは、意味が同じものを 1 つの対応表（§2）にまとめ、違うところだけを短いスクリプトで動かして確かめる。通し課題では、FAQ をカテゴリごとに数える `categories.py` を書く。
地図は [Python 学習ガイド](../README.md)、前は [Step 01: 環境構築](01-setup.md)、次は [Step 03: プロジェクト構成](03-project.md)。型ヒントは [Step 04](04-typing.md)、`import` の仕組みは [import の仕組み](../topics/imports.md) で扱う。

---

## 1. TL;DR

- **ブロックは `{}` ではなくインデント（4 スペース）で表す**。名前は関数・変数が `snake_case`、クラスが `CapWords`（PEP 8）。空のブロックには `pass` を置く。
- **`==` は中身を比べる**（`[1, 2] == [1, 2]` は `True`）。同じオブジェクトかは `is` で、`None` との比較は `is None`。**空の list・dict は偽**で、JS とは逆である（§3.2）。
- **既定引数は `def` を実行したときに 1 回だけ評価される**。`tags=[]` と書くと、呼び出しをまたいで同じ list が使い回される。既定値は `None` にする（§3.4）。
- **`if` と `for` にはブロックスコープが無い**。ループの変数は外に残り、ループの中で作った関数は、呼んだ時点の（最後の）値を見る（§3.5）。
- `undefined`・`??`・`?.` は無い。dict に無いキーは `KeyError`、無い属性は `AttributeError` なので、`d.get(key, 既定値)` で読む（§3.2）。
- 罠の多くは Ruff の既定のルールで、書いた時点で指摘される（§4）。

---

## 2. Node.js / Bun との対応

書き方が違うだけで、意味がほぼ同じものをまとめる。意味が違うものは §3 で動かす。

| JS / TS | Python | 補足 |
|---|---|---|
| `const x = 1` / `let x = 1` | `x = 1` | 宣言のキーワードは無い。`const` も無く、定数は `UPPER_CASE` の名前で示す |
| `true` / `false` / `null` | `True` / `False` / `None` | 先頭が大文字。`undefined` にあたる値は無い |
| `===` / `!==`、`&&` / `\|\|` / `!` | `==` / `!=`、`and` / `or` / `not` | `==` は list も中身で比べる。`and` / `or` はオペランドを返す（§3.2） |
| `c ? a : b` / `x ?? y` | `a if c else b` / `y if x is None else x` | `??` と `?.` は無い |
| `` `${a}` `` / タグ付きテンプレート | `f"{a}"` / t-string `t"..."` | t-string は 3.14 から（PEP 750）。`Template` を返す（検証済み） |
| `arr.length` / `arr.slice(1, 3)` | `len(arr)` / `arr[1:3]` | 負の添字で後ろから数える（§3.2） |
| `arr.filter(p).map(f)` / `arr.flat()` | `[f(x) for x in arr if p(x)]` / `[*xs for xs in arr]` | 内包表記（§3.3）。後者は 3.15 から |
| `for (const x of arr)` / `arr.entries()` | `for x in arr:` / `enumerate(arr)` | `for (let i = 0; i < n; i++)` は `for i in range(n):` |
| `const [a, ...rest] = arr` / `{ ...a, ...b }` | `a, *rest = arr` / `{**a, **b}`（`a \| b`） | `for` の中でも分割代入できる（`for i, (k, v) in ...`） |
| `f(...args)` / `function f(...args)` | `f(*args)` / `def f(*args, **kwargs):` | 位置引数の残りは tuple、キーワード引数の残りは dict |
| `Map` / `Set` | `dict` / `set` | dict は入れた順を保つ。**set は保たない**（§3.3） |
| `(x) => x * 2` | `lambda x: x * 2` | 式 1 つだけ。名前を付けるなら `def` で書く（PEP 8: "Always use a def statement instead of an assignment statement that binds a lambda expression directly to an identifier"） |
| `try / catch (e) / finally`、`throw` | `try / except E as e / else / finally`、`raise` | `else` 節がある。`using` は `with`（§3.6） |
| `function*` / `yield` | `def` + `yield` | §3.6 |
| `switch` | `match` | 3.10 から。次の `case` へ落ちない（§3.7） |
| `class` + `constructor` | `@dataclass` | TS の `interface` にあたる型は [Step 04](04-typing.md) |
| `import.meta.main` | `if __name__ == "__main__":` | §3.7 |

> **ポイント**: 文末の `;` は要らない。`{}` の代わりに、`if` / `for` / `def` / `class` の行末に `:` を置き、次の行から字下げする（PEP 8: "Use 4 spaces per indentation level."）。

---

## 3. ハンズオン

作業ディレクトリは [Step 01](01-setup.md) の `faq-app/` である。通し課題に残すのは §3.1 の `categories.py` だけで、§3.2 以降は確かめるための使い捨てである。使い捨ては `faq-app/` の外に作った別のディレクトリ（例: `py-scratch/` で `uv python pin 3.15` しておく）に置き、`uv run <ファイル>` で動かす。`faq-app/` に置くと、§3.7 の `models.py` が [Step 03](03-project.md) で作る `faq/models.py` と紛らわしく、import の誤りを隠すことがある。コメントの「JS:」は、Node 26.13.0 で同じことをした結果である。

### 3.1 通し課題: FAQ をカテゴリごとに数える

狙い: この後の節で扱う要素（`with`・内包表記・`dict.get`・`lambda`・f-string）を 1 本で一通り使う。`categories.py` を作る（検証済み）。

```python
import json
from collections import Counter
from pathlib import Path


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:  # with を抜けると必ず閉じる
        return [json.loads(line) for line in f if line.strip()]


faqs = load("data/faq.jsonl")

# 1. dict で数える（JS の obj[key] = (obj[key] ?? 0) + 1 と同じ）
counts: dict[str, int] = {}
for faq in faqs:
    counts[faq["category"]] = counts.get(faq["category"], 0) + 1

# 2. 標準ライブラリの Counter なら 1 行
assert counts == Counter(faq["category"] for faq in faqs)

for category, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"{category}: {n} 件")

it_questions = [faq["question"] for faq in faqs if faq["category"] == "IT"]
print("IT の質問:", it_questions)
```

実行結果:

```text
$ uv run categories.py
IT: 3 件
セキュリティ: 2 件
勤怠: 2 件
経費: 2 件
総務: 2 件
出張: 1 件
IT の質問: ['社内 VPN につながりません。', 'パスワードを忘れました。', '新しい PC のセットアップは誰がしますか？']
```

- `with open(...) as f:` は TS の `using` と同じ役目で、ブロックを抜けると例外が起きてもファイルを閉じる。`for line in f` はファイルを 1 行ずつ読む。`from pathlib import Path` はこのスクリプトでは使っていない。消してよいが、[Step 05: 品質ツール](../README.md#4-学習ロードマップ)で Ruff に見つけさせる例として、ここでは残しておく
- `sorted` の `key=` には、JS の比較関数 `(a, b) => ...` ではなく **「並べ替えに使う値」を返す関数**を渡す。tuple は先頭から順に比べるので、`(-件数, 名前)` で「件数の多い順、同数なら名前順」になる
- `assert` は条件が偽なら `AssertionError` を投げる。`Counter` は dict の仲間で、`==` が中身を比べるので通る（§3.2）。`dict[str, int]` などの型ヒントは実行時には検査されない（[Step 04](04-typing.md)）
- 3.15 から `open()` は `encoding` を省くと UTF-8 を使う（PEP 686）。それでも What's New は "For best compatibility between versions of Python, ensure that an explicit encoding argument is always provided." と書いているので、`encoding="utf-8"` は書く

### 3.2 値: `None`・真偽値・比較・数値・文字列

狙い: `undefined` が無いこと、真偽の判定・`==`・割り算・文字列の扱いが JS と違うことを確かめる。`values.py` を作る（検証済み）。

```python
faq = {"id": "faq-01", "category": "経費"}
print(faq.get("tags"), faq.get("tags", []))  # 無いキー → None か、渡した既定値
try:
    faq["tags"]  # [] で無いキーを読むと KeyError（JS なら undefined）
except KeyError as e:
    print("KeyError:", e)
try:
    faq.category  # dict のキーは属性ではない（JS の faq.category とは違う）
except AttributeError as e:
    print("AttributeError:", e)

# 空のコンテナは偽（JS では [] も {} も真で、NaN は偽）
print([bool(v) for v in [[], {}, "", 0, None, "0", [0], float("nan")]])
a, b = [1, 2], [1, 2]
print(a == b, a is b)  # == は中身、is は同じオブジェクトか（JS の === は false）
print(0 or 10, "" or "既定", [] and "x")  # オペランドそのものを返す（|| と同じ）

print(2**100)  # int は桁あふれしない（JS: 2 ** 53 + 1 で精度が落ちる）
print(7 / 2, 7 // 2, -7 // 2, -7 % 3)  # // は負の方向へ切り捨て（JS: -7 % 3 は -1）
print(0.1 + 0.2, round(2.5), round(3.5))  # 偶数へ丸める（JS: Math.round(2.5) は 3）
try:
    "件数: " + 3  # JS は "件数: 3" に変換する
except TypeError as e:
    print("TypeError:", e)
s = "経費精算の締め日"
print(s[0], s[-1], s[:2], s[::-1], len("😀"))  # JS: "😀".length は 2
print(f"{len(s)=}", f"[{7:>5}]", f"{0.1 + 0.2:.2f}", f"{1234567:,}")
```

実行結果:

```text
$ uv run values.py
None []
KeyError: 'tags'
AttributeError: 'dict' object has no attribute 'category'
[False, False, False, False, False, True, True, True]
True False
10 既定 []
1267650600228229401496703205376
3.5 3 -4 2
0.30000000000000004 2 4
TypeError: can only concatenate str (not "int") to str
経 日 経費 日め締の算精費経 1
len(s)=8 [    7] 0.30 1,234,567
```

- 偽になるのは `None`・`False`・数値の 0・空の文字列 / list / tuple / dict / set などである（Built-in Types の Truth Value Testing）。上の 8 つのうち JS と結果が違うのは `[]`・`{}`・`NaN` の 3 つ
- `is` は参照が同じかを見る。PEP 8 は "Comparisons to singletons like None should always be done with `is` or `is not`, never the equality operators." と書いている。`or` は `||` と同じで `??` ではないので、0 や空文字列を正しい値として扱うなら `x if x is not None else 10` と書く
- `json.loads` で読んだ値は dict なので、`faq["category"]`（必ずある）か `faq.get("category")`（無いかもしれない）で読む。`.` で読みたいなら §3.7 の dataclass に詰め替える
- int は "Integers have unlimited precision."（Built-in Types）。整数どうしでも `/` は float を返し、整数が欲しいなら `//`（JS の `Math.floor(a / b)`）。`%` の結果は "the same sign as its second operand"（Language Reference）。`round` は "rounding is done toward the even choice"（Built-in Functions）
- str は変更できない（`s[0] = "X"` は `TypeError`）。スライスは `[始まり:終わり:刻み]`。f-string の `{式=}` は式と値を並べるデバッグ用の書き方で、`:` の後ろは書式（`>5` 右寄せ・`.2f` 小数 2 桁・`,` 3 桁区切り）

### 3.3 コレクションと内包表記

狙い: tuple・dict・set の違いと、分割代入・内包表記を確かめる。`collections_demo.py` を作る（検証済み）。

```python
one = ("faq-01",)  # 要素 1 個の tuple には , が要る（("faq-01") はただの str）
d = {"b": 2, "a": 1}
d["c"] = 3
print(type(one).__name__, list(d), d | {"a": 10})  # 入れた順を保つ。| は {...d, a: 10}

first, *rest = [1, 2, 3, 4]  # const [first, ...rest] = [1, 2, 3, 4]
print(first, rest)

words = ["IT", "経費", "IT", "勤怠"]
print([w.lower() for w in words if w != "経費"])  # filter + map
print({w: words.count(w) for w in words})  # dict の内包表記
print(sum(len(w) for w in words), sorted({w for w in words}))  # ジェネレータ式と set
print([*xs for xs in [["IT", "経費"], ["勤怠"]]])  # 3.15 から（PEP 798）。JS の flat()
```

実行結果:

```text
$ uv run collections_demo.py
tuple ['b', 'a', 'c'] {'b': 2, 'a': 10, 'c': 3}
1 [2, 3, 4]
['it', 'it', '勤怠']
{'IT': 2, '経費': 1, '勤怠': 1}
8 ['IT', '勤怠', '経費']
['IT', '経費', '勤怠']
```

- **tuple** は変更できない list で、関数から複数の値を返すときや dict のキーに使う。**dict** は 3.7 から、入れた順を保つことが仕様になった（"Changed in version 3.7: Dictionary order is guaranteed to be insertion order."）
- 内包表記を `(...)` で囲むとジェネレータ式になり、list を作らずに 1 つずつ値を渡す。`sum(...)` のように引数が 1 つなら、括弧を二重にしなくてよい
- **set は順番を保たない**。JS の `Set` は入れた順を保つが、Python では str の並びが起動のたびに変わる。`print({"IT", "経費", "勤怠", "総務", "出張"})` を `PYTHONHASHSEED=1` と `=2` で動かすと、`{'経費', 'IT', '出張', '総務', '勤怠'}` と `{'勤怠', '経費', '出張', '総務', 'IT'}` になった（検証済み）。表示やテストで順番が要るなら `sorted()` を通す
- 3.15 では、内包表記の中の `*` 展開（PEP 798。3.14 で動かすと `SyntaxError`）と、変更できない dict の `frozendict`（PEP 814）が入った。`frozendict` は dict の子クラスではなく、`isinstance(x, dict)` は `False` になる（検証済み）

### 3.4 関数の引数

狙い: 既定引数の罠と、キーワード専用引数を確かめる。`functions.py` を作る（検証済み）。

```python
def add_tag(tag, tags=[]):  # 罠: [] は def を実行したときに 1 回だけ作られる
    tags.append(tag)
    return tags


def add_tag_ok(tag, tags=None):  # 正しくは None を既定値にする
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def search(query, *, limit=10):  # * より後ろはキーワードでしか渡せない
    return f"{query=} {limit=}"


print(add_tag("IT"))
print(add_tag("経費"))  # 前の "IT" が残る（JS の既定引数は呼ぶたびに作り直す）
print(add_tag_ok("IT"), add_tag_ok("経費"))
print(search("VPN", limit=3))
try:
    search("VPN", 3)
except TypeError as e:
    print("TypeError:", e)
```

実行結果:

```text
$ uv run functions.py
['IT']
['IT', '経費']
['IT'] ['経費']
query='VPN' limit=3
TypeError: search() takes 1 positional argument but 2 were given
```

- Language Reference は "the expression is evaluated once, when the function is defined, and that the same “pre-computed” value is used for each call." と書いている。list・dict・set を既定値にしない
- JS でオプションを `{ limit }` のオブジェクトで渡す場面は、Python ではキーワード専用引数（`*` の後ろ）にする。dict を展開して渡すなら `search("VPN", **opts)`
- **オーバーロードは無い**。同じ名前で `def` を 2 回書くと、後の定義が前を上書きする（`greet(name)` の後に `greet(name, polite)` を書いて `greet("佐藤")` を呼ぶと `TypeError: greet() missing 1 required positional argument: 'polite'`。検証済み）。違いは既定値とキーワード引数で吸収する

### 3.5 スコープとクロージャ

狙い: ブロックスコープが無いこと、ループの中で作った関数と、外の変数への代入を確かめる。`scope.py` を作る（検証済み）。

```python
for i in range(3):
    pass
print("ループ後の i:", i)  # for にも if にもブロックスコープが無い

fs = [lambda: i for i in range(3)]
print([f() for f in fs])  # 呼んだ時点の i を見るので全部 2（JS の let なら [0, 1, 2]）
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])  # 既定値で、作った時点の値を閉じ込める

count = 0


def bump():
    count += 1  # 代入があると、関数全体で count がローカル変数になる


try:
    bump()
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
```

実行結果:

```text
$ uv run scope.py
ループ後の i: 2
[2, 2, 2]
[0, 1, 2]
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

- スコープを作るのは "a module, a function body, and a class definition"（Language Reference の Execution model）だけで、`if` や `for` の中で代入した名前は外からも見える。JS で言えば、すべてが `var` に近い
- ループで作った関数は、JS の `for (let i ...)` なら `[0, 1, 2]`、`for (var j ...)` なら `[3, 3, 3]` を返す（Node 26 で確認）。Python は `var` と同じで、Programming FAQ も既定値（`n=x`）で今の値を閉じ込める方法を示している
- 名前は「ローカル → 外側の関数 → モジュール → 組み込み」の順に探す（Tutorial 9.2）。読むだけなら外の変数も見えるが、**代入するとその関数の中ではローカル変数になる**。外に代入するなら、関数の先頭で `global count`（外側の関数の変数なら `nonlocal`）と宣言する。ただし、引数と戻り値で渡せるならそのほうがよい

### 3.6 例外とジェネレータ

狙い: 例外の受け方と包み直し、`yield` を確かめる。`errors_gen.py` を作る（検証済み）。

```python
import json


def parse(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:  # 型で絞って受ける
        raise ValueError(f"壊れた行: {line!r}") from e  # 元の例外を原因として残す


def numbered(lines):  # yield を含む def はジェネレータ関数になる（JS の function*）
    for i, line in enumerate(lines, start=1):
        yield f"{i}: {line}"


for line in ['{"id": "faq-01"}', "{oops"]:
    try:
        faq = parse(line)
    except ValueError as e:
        print(e, "/ 原因:", type(e.__cause__).__name__)
    else:  # 例外が起きなかったときだけ動く（finally は JS と同じく必ず動く）
        print("OK:", faq)

gen = numbered(["VPN", "パスワード"])
print(next(gen), list(gen), list(gen))  # 1 つ取り出す → 残り全部 → 使い切ったので空
print(list(zip(["IT", "経費"], [3, 2, 99])))  # 短い方で止まる（strict=True で例外に）
```

実行結果:

```text
$ uv run errors_gen.py
OK: {'id': 'faq-01'}
壊れた行: '{oops' / 原因: JSONDecodeError
1: VPN ['2: パスワード'] []
[('IT', 3), ('経費', 2)]
```

- JS の `catch (e)` は 1 つで、中で `instanceof` を見て分ける。Python は `except 型 as e:` を型ごとに並べる。型を書かない `except:` は PEP 8 が避けるよう求めている
- `raise ... from e` は JS の `new Error(msg, { cause: e })` にあたる。捕まえずに落ちると、traceback に "The above exception was the direct cause of the following exception:" と元の例外が並ぶ（Tutorial 8.5）
- `with` は Language Reference が `try` / `finally` と "semantically equivalent" と説明する構文で、§3.1 の `open()` のように後始末に使う。自分で作るなら `contextlib.contextmanager` を付けた、`yield` 1 つのジェネレータ関数で書ける
- ジェネレータが 1 周しか回らないのは JS と同じで、何度も使うなら `list(...)` にして持つ。`zip` は長さが違うと黙って短い方に合わせるので、そろうはずの列には `strict=True`（3.10 から）を付ける（§4）

### 3.7 `@dataclass`・`match`・`if __name__ == "__main__":`

狙い: クラスを短く書く dataclass、形で分岐する `match`、直接実行したときだけ動く部分を確かめる。`models.py` を作る（検証済み）。

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Faq:  # __init__・__repr__・__eq__ が自動で作られる
    id: str
    category: str
    tags: list[str] = field(default_factory=list)  # 可変の既定値は default_factory で


def route(faq: dict) -> str:
    match faq:
        case {"category": "IT", "question": q}:  # 形と値で分岐し、q に取り出す
            return f"IT 窓口へ: {q}"
        case {"category": "経費" | "出張"}:  # 余分なキーがあっても一致する
            return "経理へ"
        case _:  # default にあたる。break は要らない（次の case へ落ちない）
            return "総務へ"


a = Faq("faq-01", "経費")
print(a, a == Faq("faq-01", "経費"))  # 中身で比べる
print("__name__ =", __name__)
if __name__ == "__main__":  # 直接実行したときだけ真。import されたときは偽
    print(route({"category": "IT", "question": "VPN"}))
    print(route({"category": "出張", "id": "faq-12"}), route({}))
```

実行結果:

```text
$ uv run models.py
Faq(id='faq-01', category='経費', tags=[]) True
__name__ = __main__
IT 窓口へ: VPN
経理へ 総務へ
$ uv run python -c "import models"
Faq(id='faq-01', category='経費', tags=[]) True
__name__ = models
```

- `@dataclass`（PEP 557）は、型注釈を付けたクラス変数から `__init__`・`__repr__`・`__eq__` を作る。TS の `constructor(public id: string, ...)` を書く手間が無く、`==` も中身で比べる。`frozen=True` なら代入は `FrozenInstanceError` になる。型は実行時に検査されないので、JSON の検証まで要るなら [Pydantic](../README.md#5-トピック一覧目的から引く) を使う
- `match`（PEP 636）は値だけでなく形で分岐する。dict のパターンは余分なキーを無視し、`|` で候補を並べ、名前を書いた所に値を取り出す。`case Faq(category=c):` のようにクラスの属性でも分岐できる。**素の名前（`case IT:`）は比較ではなく取り出し**になるので、定数は `Category.IT` のようにドット付きの名前か、リテラルで書く（§5）
- `__name__` は、直接実行したファイルでは `"__main__"`、`import` されたファイルではモジュール名になる。Bun と Node 26 の `import.meta.main` と同じ使い方で、ライブラリとしても使うファイルの「実行したときの処理」を置く（[`__main__` の docs](https://docs.python.org/3/library/__main__.html)。`import` の仕組みは [import の仕組み](../topics/imports.md)）

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| `None` との比較は `is None` / `is not None` | `== None` | PEP 8 の "Comparisons to singletons" |
| 空かどうかは `if not items:` | `if len(items) == 0:` | PEP 8: "use the fact that empty sequences are false"。`None` と空を分けたいときは `is None` |
| 可変の既定値は `None` にして、関数の中で作る | `def f(x=[])` / `x={}` | 既定値は定義時に 1 回だけ評価される（Language Reference） |
| 例外は型を書いて受け、包み直すときは `raise ... from e` | 型の無い `except:`、元の例外を捨てる | PEP 8 と Tutorial 8.5。原因が traceback に残る |
| ファイルや接続の後始末は `with` に任せる | `open()` して `close()` を手で呼ぶ | 例外が起きても必ず閉じる（`try` / `finally` と同じ意味） |
| `match` の定数はドット付きの名前（`Category.IT`）かリテラルで書く | `case IT:` | 素の名前は取り出しのパターンになる（Tutorial 4.7） |
| 命名は PEP 8（関数・変数は `snake_case`、クラスは `CapWords`、定数は `UPPER_CASE`） | JS の `camelCase` を持ち込む | 標準ライブラリと周りのライブラリがこの規約で書かれている |
| 長さがそろうはずの列は `zip(..., strict=True)` | 黙って短い方に合わせる | 食い違いを `ValueError` で見つけられる（Built-in Functions） |
| Ruff を入れ、書いた時点で罠を指摘させる | 動かして気づくのを待つ | 既定のルールだけで、既定引数（B006）・`def` の上書き（F811）・ループの変数（B023）・`UnboundLocalError`（F823）・`is` とリテラル（F632）が出た（検証済み。[Step 05: 品質ツール](../README.md#4-学習ロードマップ)） |

---

## 5. つまずきポイント

（検証で再現）は、罠を確かめるためにわざと書いたコードで出たものである。

| 症状 | 原因 | 対処 |
|---|---|---|
| `IndentationError: expected an indented block after function definition on line 1`（検証で再現） | `def` の中身を字下げしていない。貼り付けで崩れやすい | 4 スペースで字下げする。中身が空なら `pass` |
| `ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory`（検証で再現） | dataclass に `tags: list[str] = []` と書いた | `field(default_factory=list)` にする |
| `SyntaxError: name capture 'IT' makes remaining patterns unreachable`。最後の `case` ならエラーにならず、何にでも一致して `IT` の値が `経費` に書き換わる（どちらも検証で再現） | `case IT:` は比較ではなく「何でも受けて `IT` に入れる」パターン | `case "IT":` かドット付きの名前（`Category.IT`）にする |
| `SyntaxWarning: "is" with 'int' literal. Did you mean "=="?`（検証で再現） | 値の比較に `is` を使った | 値は `==` で比べる。`is` は `None` / `True` / `False` だけ |
| `UnboundLocalError: cannot access local variable 'count' where it is not associated with a value`（検証で再現） | 関数の中で外の変数に代入した | `nonlocal` / `global` を宣言する。できれば引数と戻り値で渡す |
| set を表示するたびに順番が変わる（検証で再現） | str のハッシュは起動ごとにランダムで、set は順番を保たない | `sorted()` を通す。入れた順が要るなら list か dict |
| 3.14 で `SyntaxError: iterable unpacking cannot be used in comprehension`（検証で再現） | `[*xs for xs in ...]` は 3.15 の文法（PEP 798） | 3.14 以前も対象なら `[x for xs in ... for x in xs]` と書く |

---

## 6. 次のステップ

- [Step 03: プロジェクト構成](03-project.md) — `faq-app/` を `pyproject.toml` のあるプロジェクトにし、`categories.py` をパッケージに移す
- [Step 04: 型](04-typing.md) — このステップで書いた `dict[str, int]` や `-> str` を型チェッカーで検査する

---

## 出典

| 情報源 | URL |
|---|---|
| Tutorial — More Control Flow Tools / Errors and Exceptions / Classes | https://docs.python.org/3/tutorial/controlflow.html ・ https://docs.python.org/3/tutorial/errors.html ・ https://docs.python.org/3/tutorial/classes.html （2026-11-08 確認、Context7 `/python/cpython` 経由を含む。既定引数の警告、4.7 `match`、8.5 例外の連鎖、9.2 名前を探す順番） |
| Language Reference — Compound statements / Expressions / Execution model | https://docs.python.org/3/reference/compound_stmts.html ・ https://docs.python.org/3/reference/expressions.html ・ https://docs.python.org/3/reference/executionmodel.html （2026-11-08 確認。既定引数の評価、`with`、`match` のパターン、`%` の符号、`and` / `or`、ブロックになるもの） |
| Built-in Types / Built-in Functions | https://docs.python.org/3/builtins/stdtypes.html ・ https://docs.python.org/3/builtins/functions.html （2026-11-08 確認。真偽値、int の精度、dict の順序、set、str、`round`、`zip` の `strict`） |
| Programming FAQ | https://docs.python.org/3/faq/programming.html （2026-11-08 確認、Context7 経由。ループで作った lambda、`UnboundLocalError`） |
| `__main__` / dataclasses / contextlib | https://docs.python.org/3/library/__main__.html ・ https://docs.python.org/3/library/dataclasses.html ・ https://docs.python.org/3/library/contextlib.html （2026-11-08 確認。`default_factory` と可変の既定値の `ValueError`、`contextmanager`） |
| Command line and environment | https://docs.python.org/3/using/cmdline.html （2026-11-08 確認。str のハッシュのランダム化と `PYTHONHASHSEED`） |
| What's New In Python 3.15 / 3.14 | https://docs.python.org/3/whatsnew/3.15.html ・ https://docs.python.org/3/whatsnew/3.14.html （2026-11-08 確認。PEP 798・PEP 814・PEP 686 / PEP 750） |
| PEP 8 / PEP 636 / PEP 557 | https://peps.python.org/pep-0008/ ・ https://peps.python.org/pep-0636/ ・ https://peps.python.org/pep-0557/ （2026-11-08 確認） |

### 確認できなかった事項

- **Node.js で `import.meta.main` と `using` が使えるようになった版**。手元の Node 26.13.0 と Bun 1.4.4 で動くことだけを確かめ、導入された版は確かめていない
- **名前を探す順番の呼び名**。Tutorial 9.2 は順番を説明しているが、よく使われる「LEGB」という呼び名は docs.python.org に見つからなかったので、本文では使っていない

- 関連: [Python 学習ガイド](../README.md) / [Step 01: 環境構築](01-setup.md) / [Step 04: 型](04-typing.md) / [import の仕組み](../topics/imports.md)
