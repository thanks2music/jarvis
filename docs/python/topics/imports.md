# import の仕組み — sys.path・パッケージ・相対 import

> 出典（一次情報）:
> - [The import system](https://docs.python.org/3/reference/import.html) / [Modules — Tutorial](https://docs.python.org/3/tutorial/modules.html)（docs.python.org） — `sys.modules`、`sys.path` の初期値、パッケージ
> - [sys.path](https://docs.python.org/3/library/sys.html#sys.path) / [`-P`](https://docs.python.org/3/using/cmdline.html#cmdoption-P)（docs.python.org） — 先頭に足される「安全でないかもしれない」パスと、その外し方
> - [importlib](https://docs.python.org/3/library/importlib.html) / [importlib.resources](https://docs.python.org/3/library/importlib.resources.html) / [importlib.metadata](https://docs.python.org/3/library/importlib.metadata.html) — 動的 import・同梱データ・配布名
> - [PEP 328](https://peps.python.org/pep-0328/) / [PEP 366](https://peps.python.org/pep-0366/) / [PEP 420](https://peps.python.org/pep-0420/) / [PEP 810](https://peps.python.org/pep-0810/) と [What's New In Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) — 絶対・相対 import / `-m` / namespace package / `lazy import`
> - [Modules](https://nodejs.org/api/modules.html) / [ECMAScript modules](https://nodejs.org/api/esm.html) / [Packages](https://nodejs.org/api/packages.html)（nodejs.org） — 比較用
>
> 最終更新: 2026-11-08（Python 3.15.2・uv 0.13.7 で検証。JS 側は Node.js 26.13.0・Bun 1.4.4 で確認）

Node.js は `import "x"` を、読み込む側のファイルから親へ `node_modules/` をたどって探し、`./x.js` はそのファイルからの相対パスになる。Python の `import x` は、どのファイルに書いても **`sys.path` というリストを先頭から探す**だけで、先頭には実行したスクリプトのディレクトリが入る。同名ファイルの衝突も、`python pkg/mod.py` で相対 import が落ちるのも、ここから来る。
通し課題では [Step 03](../steps/03-project.md) でパッケージに分けるときに効く（editable install の `.pth`・`__main__.py`・`__all__` はそちら）。用語は[用語集](../README.md#8-用語集)を参照。

---

## 1. TL;DR

- **`import x` は `sys.modules`（読み込み済みのキャッシュ）を見て、無ければ `sys.path` を先頭から探す**。モジュールは 1 プロセスで 1 回だけ実行される（§3.2）。
- **`sys.path` の先頭はスクリプトのディレクトリ**で、標準ライブラリより前にある。隣の `random.py` や `json.py` が標準ライブラリの代わりに読まれる。`python -P` で外せる（§4.1）。
- **パッケージの中のファイルは `python -m pkg.mod` で動かす**。`python pkg/mod.py` では相対 import が落ち、`.venv` に入れていないパッケージは絶対 import でも見つからない（§4.2）。
- **循環 import は "partially initialized module" になる**。モジュールごと import する・関数の中で import する・型のためだけなら `TYPE_CHECKING` か 3.15 の `lazy from` でほどく（§4.3）。
- 同梱データは `importlib.resources.files("pkg")` で読む。配布名と import 名は別物で（`pyyaml` → `yaml`）、`packages_distributions()` で引ける（§4.4・§4.5）。
- 3.15 の **`lazy import`** は最初に使うまで読み込みを遅らせる。`await import()` と違って同期で、使う側は変わらない（§4.6）。

---

## 2. Node.js / Bun との対応

| 観点 | Node.js / Bun | Python |
|---|---|---|
| 探す場所 | 読み込む側のファイルから親へ `node_modules/` をたどる | `sys.path` を先頭から。どのファイルの `import` でも同じリスト（§3.1） |
| キャッシュ | `require.cache`（CJS）。ESM は URL ごと | `sys.modules`（§3.2） |
| 隣のファイルを指す | `./pricing.js`（ファイルからの相対。ESM は拡張子が必須） | `from . import pricing`（**パッケージ**からの相対。拡張子は書かない） |
| パッケージの入口と公開範囲 | `package.json` の `exports` / `main`、無ければ `index.js`。`exports` に無いパスは `ERR_PACKAGE_PATH_NOT_EXPORTED` | `__init__.py`（無いと namespace package。§3.3）。公開範囲の制限は無く、`_` で始まる名前は内部用の印（PEP 8）、`__all__` は `import *` と型チェッカー向け |
| 循環 import | CJS は未完成の `exports`、ESM は `ReferenceError: Cannot access 'a' before initialization`（検証済み） | 途中まで実行したモジュールを返し、まだ無い名前で `ImportError`（§4.3） |
| 動的・遅延 | `await import(name)`（非同期）/ `import defer * as ns`（TC39 Stage 3。Bun 1.4.4 は評価を遅らせ、Node 26.13.0 は `SyntaxError`。検証済み） | `importlib.import_module(name)`（同期。§4.4）/ `lazy import x`（3.15。§4.6） |
| トップレベルの `await` | ESM で使える | `SyntaxError: 'await' outside function`（検証済み）。import は同期で、トップレベルが副作用ごとその場で動く |
| 同梱データ | `import x from "./x.json" with { type: "json" }`（検証済み）/ `new URL("./x.json", import.meta.url)` | `importlib.resources.files("pkg") / "x.json"`（§4.4） |

---

## 3. 早見表（コマンド・設定）

### 3.1 `sys.path` と調べ方

| やりたいこと | コマンド |
|---|---|
| どのファイルが読まれたか | `print(yaml.__file__)` / `importlib.util.find_spec("yaml").origin`（実行せずに場所だけ調べる） |
| スクリプトのディレクトリを足さない | `python -P` / `PYTHONSAFEPATH=1`（3.11 から）。`-I`（isolated）も `-P` を含む |
| 読み込みを 1 つずつ表示する / 時間を測る / import 名から配布名を引く | `python -v` / `python -X importtime` / `importlib.metadata.packages_distributions()`（§4.5） |

`~/lab` は、検証用に `uv init --no-package` で作ったプロジェクトである。その中で `sys.path` を表示する。`tools/show_path.py` は `sys.path` に番号を付けて表示するだけのスクリプトである（検証済み）。

実行結果:

```text
$ uv run python -c "import sys; print(*enumerate(sys.path), sep='\n')"
(0, '')
…（中略: 4 行）…
$ uv run python tools/show_path.py
0 '~/lab/tools'
1 '~/.local/share/uv/python/cpython-3.15.2-macos-aarch64-none/lib/python315.zip'
2 '~/.local/share/uv/python/cpython-3.15.2-macos-aarch64-none/lib/python3.15'
3 '~/.local/share/uv/python/cpython-3.15.2-macos-aarch64-none/lib/python3.15/lib-dynload'
4 '~/lab/.venv/lib/python3.15/site-packages'
```

0 番は、`-c` では `''`（カレントディレクトリ）、スクリプトではそのディレクトリで、`python -m tools.show_path` ではカレントディレクトリ、`-P` では何も入らなかった。1〜3 番が標準ライブラリ、最後が `.venv` の `site-packages` である（すべて検証済み）。**手元のファイルが標準ライブラリにも依存にも勝つ順番**になっている。

### 3.2 `sys.modules` — モジュールは 1 回だけ実行される

`print()` と `count = 0` だけの `greet.py` を 2 回 import しても、表示は 1 回だった。`import greet as again` も同じオブジェクト（`again is sys.modules["greet"]` が `True`）で、状態も共有した（検証済み）。言語リファレンスは `sys.modules` を "a cache of all modules that have been previously imported" とし、モジュールは**実行する前に** `sys.modules` へ入る（§4.3 の原因）。直したファイルが REPL に反映されないのもこのためで、Tutorial は再起動か `importlib.reload()` を挙げる。

### 3.3 モジュール・パッケージ・namespace package

| 種類 | 実体 | `__file__` |
|---|---|---|
| モジュール | `x.py`（C 拡張の `.so` なども） | そのファイル |
| 通常のパッケージ | `__init__.py` を持つディレクトリ | `__init__.py` |
| namespace package（PEP 420） | `__init__.py` の無いディレクトリ | `None`（検証済み） |

- **`__init__.py` を忘れても、ただのデータ置き場でも import が通る**。FAQ の JSONL を置いただけの `data/` で `import data` が成功し、`print(data)` は `<module 'data' (namespace) from [...]>` を表示した（検証で再現）
- `sys.path` の別々の場所にある同名のディレクトリは 1 つに合わさった（`PYTHONPATH=ns_a:ns_b` で `plugins.__path__` に 2 つ並んだ。検証済み）。PEP 420 の目的は、1 つのパッケージを複数のディレクトリ（配布物）に分けることである。優先度は最も低い。`sys.path` を最後まで探して通常のパッケージもモジュールも無かったときだけ作られる（PEP 420）。隣に `json/` を置いても標準ライブラリの `json` が読まれた（検証済み）。複数の配布物で分け合うとき以外は `__init__.py` を置く

---

## 4. 推奨の使い方（2026-11）

### 4.1 標準ライブラリやライブラリと同じ名前のファイルを作らない

乱数を試すつもりで、`import random` と `print(random.randint(1, 6))` だけのスクリプトを `random.py` と名付けた（検証で再現）。

実行結果:

```text
$ uv run python shadow/random.py
Traceback (most recent call last):
…（中略: 5 行）…
AttributeError: module 'random' has no attribute 'randint' (consider renaming '~/lab/shadow/random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)
```

`sys.path[0]` が `shadow/` なので、`import random` は**このファイル自身**を読み込み、途中までしか実行していない自分を受け取る。括弧の中のヒント（3.13 から）は、いつも出るわけではない（すべて検証済み）。

| 置いたもの | 結果 |
|---|---|
| 隣に `json.py`（`dumps` だけ定義） | **エラーにならず**、`json.dumps` が自作の関数になる。`python -P` で動かすと、標準ライブラリの `json/__init__.py` が読まれた |
| 隣に `yaml.py`（PyYAML を入れた環境） | `AttributeError: module 'yaml' has no attribute 'safe_load'` で、**ヒントは出ない**。自分自身が `yaml.py` のときだけ "if it has the same name as a library you intended to import" と出る |
| 隣に `os.py` | 影響なし。`os` は起動時に読み込み済みで（`'os' in sys.modules` が `True`）、`sys.modules` から返る |

- ファイル名を標準ライブラリや依存と同じにしない。Ruff の `A005`（stdlib-module-shadowing）は Ruff 0.17.4 の既定に入っておらず、`--select A005` で初めて `random.py` を指摘した。サブディレクトリの中まで拾うには `lint.flake8-builtins.strict-checking = true` が要る（どちらも検証済み）。`-P` は隣のファイルの import も止める。手元のコードはパッケージにして `.venv` に入れ（`uv init` の既定）、`-P` は信頼できないディレクトリで動かすときに使う。docs はこの先頭のパスを "a potentially unsafe path" と呼ぶ

### 4.2 パッケージの中のモジュールは `-m` で動かす

`shop/` パッケージ（`__init__.py`・`pricing.py` がある）に、相対 import を使う `cart.py` を置く（検証済み）。

```python
from . import pricing  # 同じパッケージ（shop）の pricing
from .pricing import total

print(f"{__name__=} {__package__=}")
print(total([100, 200]), pricing.TAX)
```

実行結果:

```text
$ uv run python shop/cart.py
Traceback (most recent call last):
…（中略: 3 行）…
ImportError: attempted relative import with no known parent package
$ uv run python -m shop.cart
__name__='__main__' __package__='shop'
330 0.1
```

- `.` は**ファイルの場所ではなく `__package__`** から決まる。ファイル名で実行すると `__package__` は `None` で親が分からず、`-m` なら `runpy` が入れる（PEP 366）。`shop/orders/checkout.py` の `from ..pricing import total` も `-m shop.orders.checkout` で動いた（検証済み）。絶対 import（`from shop.pricing import total`）でも、パッケージが `.venv` に入っていなければ、ファイル名で実行すると `sys.path[0]` が `shop/` 自身になり `ModuleNotFoundError: No module named 'shop'` になる。`shop/` に `cd` して `-m orders.checkout` とすると `ImportError: attempted relative import beyond top-level package` になる（どちらも検証で再現）。`-m` はプロジェクトの直下で実行する。書き方は PEP 8 が勧める絶対 import を基本にする（[Step 03](../steps/03-project.md) の §4）。Python 3 の `import json` は、パッケージの中でも常に最上位の `json` を指す（PEP 328: "all import statements be absolute by default"）

### 4.3 循環 import をほどく

`circ/models.py` の 1 行目が `from circ.services import price_with_tax`、`circ/services.py` の 1 行目が `from circ.models import Item` で、互いに import し合う（検証で再現）。

実行結果:

```text
$ uv run python -c "from circ.models import Item; print(Item(1000).total())"
Traceback (most recent call last):
…（中略: 8 行）…
ImportError: cannot import name 'Item' from partially initialized module 'circ.models' (most likely due to a circular import) (~/lab/circ/models.py)
```

`circ.models` は 1 行目を実行する前に `sys.modules` に入る（§3.2）。`services` はそれを受け取るが、`Item` はまだ無い。Node の CJS が未完成の `exports` を返すのと同じである。同じ 2 ファイルを次のように直し、どれも `1100` を表示した（共通部分の分離以外は検証済み）。

| 直し方 | 書き方 | 向いている場面 |
|---|---|---|
| 型のための import を `if TYPE_CHECKING:` に入れる | `services.py` の `if TYPE_CHECKING:` の中で `Item` を import する。3.14 から注釈は遅延評価（PEP 649）なので、引用符も要らない。ただし `typing.get_type_hints()` のように実行時に注釈を評価すると `NameError: name 'Item' is not defined` になる（検証で再現） | 相手を型注釈にしか使わず、実行時に注釈を読まない |
| 3.15 の `lazy from` | `lazy from circ_lazy.models import Item`。PEP 810 は "Lazy imports eliminate the common need for `TYPE_CHECKING` guards." とする一方、"Lazy imports don't automatically solve circular import problems." とも書く（初期化中に使えば失敗する） | 3.15 以上だけが対象 |
| 名前ではなくモジュールを import する | `from circ_mod import models` と書き、関数の中で `models.Item` を引く | 互いの関数を呼び合うだけ |
| 関数の中で import する | `total()` の中で `price_with_tax` を import する。読み込みは最初の 1 回だけ | 片方だけ直したい |
| 共通の部分を 3 つ目のモジュールに移す | `models` と `services` の両方が `base` を import する | 依存の向きを一方通行にして根本から直す |

### 4.4 名前を実行時に決めて import する・同梱データを読む

`exporters/` に `csv.py` と `json.py`（どちらも `export()` を持つ）を置き、`mod = importlib.import_module(f"exporters.{sys.argv[1]}")` で選ぶ。JS の `` await import(`./exporters/${name}.js`) `` にあたるが、同期でモジュールそのものを返す。`json` を渡すと `exporters.json` が動き、無い名前は `ModuleNotFoundError: No module named 'exporters.xml'. Did you mean: 'exporters.csv'?` になった（検証済み）。`exporters/json.py` の中の `import json` は、自分ではなく標準ライブラリを読んだ（§4.2 の PEP 328）。

同梱データは、`uv init --lib` で作った `shoplib` の `src/shoplib/data/prices.json` で試す。`load_prices()` は `files("shoplib") / "data" / "prices.json"` を、`load_prices_from_cwd()` は `Path("src/shoplib/data/prices.json")` を読む。プロジェクトの外から `--project` で呼ぶ（検証で再現）。

実行結果:

```text
$ uv run --project ../shoplib python -c "from shoplib.catalog import *; print(load_prices()); print(load_prices_from_cwd())"
Traceback (most recent call last):
…（中略: 12 行）…
FileNotFoundError: [Errno 2] No such file or directory: 'src/shoplib/data/prices.json'
{'apple': 120, 'milk': 210}
```

最後の行が `load_prices()` の結果で、こちらは成功した（標準出力は終了時にまとめて出た）。`files()` は Node の `new URL("./data/prices.json", import.meta.url)` にあたり、`open()` や `Path()` の相対パスは `fs.readFile("./...")` と同じくカレントディレクトリ基準である。`uv build` した wheel にも `prices.json` が入った。3.15 で `files(package=...)` は削除され、`TypeError` になる（どちらも検証済み）。通し課題の `main()`（[Step 03](../steps/03-project.md)）も `Path("data/faq.jsonl")` で読むので、`faq-app/` の外から `uv run --project` で `faq` を動かすと `FileNotFoundError` になった（検証で再現）。

### 4.5 配布名と import 名

`uv add pyyaml pillow python-dotenv` した後、`importlib.metadata.packages_distributions()`（import 名 → 配布名のリスト）を引くと、`yaml` は `['PyYAML']`、`PIL` は `['pillow']`、`dotenv` は `['python-dotenv']` だった（検証済み）。`uv add` には配布名を、`import` には import 名を書く。名前に `-` は使えないので、少なくとも `-` は変わる（`uv init` も `faq-app` を `faq_app` にする）。PEP 794（Accepted）でコアメタデータに `Import-Name`（メタデータ 2.5）が加わったが、上の 3 つはメタデータ 2.4 で、持っていなかった（検証済み）。

### 4.6 `lazy import`（3.15、PEP 810）

`heavy.py` は、読み込まれると `heavy.py を読み込んだ` と表示し、`"done"` を返す `work()` を持つモジュールである（検証済み）。

```python
import sys

lazy import heavy  # この時点では読み込まない
lazy from json import dumps

print("起動した", "heavy" in sys.modules, "heavy" in sys.lazy_modules)
print(type(globals()["heavy"]).__name__)  # 名前には代理のオブジェクトが入っている
print(heavy.work())  # 初めて使ったところで読み込む
print("heavy" in sys.modules, dumps({"lazy": True}))
```

実行結果:

```text
$ uv run python lazy/app.py
起動した False True
lazy_import
heavy.py を読み込んだ
done
True {"lazy": true}
```

- 名前には代理のオブジェクト（`types.LazyImportType`）が入り、最初に使ったときに本物に置き換わる。`sys.lazy_modules` は、lazy に import してまだ読み込んでいない名前の集合である（docs はデバッグ用とする）。効果の例（参考値）: `-X importtime` で `import PIL.Image` は累計 58146 µs、`lazy import PIL.Image` では PIL の行が 1 つも出なかった（検証済み）
- **失敗も使った行まで遅れる**。`lazy import no_such_module` の後の `print` は動き、使った行で `ModuleNotFoundError` になった。原因の `ImportError: lazy import of 'no_such_module' raised an exception during resolution` が、`lazy import` の行とともに traceback に残る（検証で再現）。import の副作用も遅れるので、PEP 810 は "users should be wary of modules that rely on import time side effects." とする
- 書けるのはモジュールのトップレベルだけで、関数の中は `SyntaxError: lazy import not allowed inside functions`、`try` の中は `... inside try/except blocks` になる（検証で再現）。関数の中は普通の `import` で、呼ぶまで遅れる。`lazy` はソフトキーワードで、変数名にも使える
- 3.14 以前も対象にするライブラリは `__lazy_modules__ = ["json"]` と書く。3.15 では次の `import json` が lazy になり、3.14 では普通に読み込まれた（検証済み）。全体を lazy にする `-X lazy_imports=all`（値は `all` と `normal` だけ）や `sys.set_lazy_imports()` はアプリ側で使う（docs: "Library developers should generally not use this function"）

---

## 5. つまずきポイント

（検証で再現）は、罠を確かめるためにわざと書いたコードで出たものである。

| 症状 | 原因 | 対処 |
|---|---|---|
| `AttributeError: module 'random' has no attribute 'randint' (consider renaming ...)`（検証で再現）。隣に `json.py` があると、エラーも無く自作の方が使われる | 自分や隣のファイルが標準ライブラリより先に見つかった | `print(json.__file__)` で確かめ、ファイル名を変える。Ruff の `A005` を有効にする（§4.1） |
| `ImportError: attempted relative import with no known parent package`（検証で再現） | パッケージの中のファイルを `python shop/cart.py` で動かした | プロジェクトの直下で `python -m shop.cart`（§4.2） |
| `ModuleNotFoundError: No module named 'shop'`（検証で再現） | ファイル名で実行し、`sys.path[0]` がパッケージの中になった | `-m` で動かす。`sys.path` を書き換えて通さない。`from models import Faq` の誤りは [Step 03](../steps/03-project.md) の §5 |
| `ImportError: cannot import name 'Item' from partially initialized module ...`（検証で再現） | 2 つのモジュールが互いに `from ... import 名前` した | §4.3 の表のどれかでほどく |
| `ModuleNotFoundError: No module named 'pyyaml'. Did you mean: '_yaml'?`（検証で再現） | 配布名で import した | `import yaml`。対応は `packages_distributions()` で引く（§4.5） |
| `FileNotFoundError: [Errno 2] No such file or directory: 'data/faq.jsonl'`（検証で再現） | 相対パスはカレントディレクトリが基準 | 同梱するデータは `importlib.resources.files("pkg")` で読む。3.15 は `files(package=...)` を `TypeError` にする（§4.4） |

---

## 出典

| 情報源 | URL |
|---|---|
| The import system / Tutorial — Modules | https://docs.python.org/3/reference/import.html ・ https://docs.python.org/3/tutorial/modules.html （2026-11-08 確認。`sys.modules` が最初に見る場所で実行前に入ること / `sys.path` の初期値、1 回だけ実行されること、`importlib.reload()`） |
| sys / Command line and environment | https://docs.python.org/3/library/sys.html ・ https://docs.python.org/3/using/cmdline.html （2026-11-08 確認、Context7 `/python/cpython` 経由。`sys.path`・`sys.lazy_modules`・`sys.set_lazy_imports`、`-P`・`-I`・`-v`・`-X importtime`） |
| importlib / importlib.resources / importlib.metadata | https://docs.python.org/3/library/importlib.html ・ https://docs.python.org/3.15/library/importlib.resources.html ・ https://docs.python.org/3/library/importlib.metadata.html （2026-11-08 確認、Context7 経由を含む。3.15 で `package` 引数が削除されたこと） |
| What's New In Python 3.15 / 3.13 | https://docs.python.org/3.15/whatsnew/3.15.html ・ https://docs.python.org/3/whatsnew/3.13.html （2026-11-08 確認。`lazy import` の制限と `-X lazy_imports` の値 / 同名のスクリプトへのヒント） |
| PEP 8 / 328 / 366 / 420 / 649 / 794 / 810 | https://peps.python.org/pep-0008/ ・ https://peps.python.org/pep-0328/ ・ https://peps.python.org/pep-0366/ ・ https://peps.python.org/pep-0420/ ・ https://peps.python.org/pep-0649/ ・ https://peps.python.org/pep-0794/ ・ https://peps.python.org/pep-0810/ （2026-11-08 確認。https://peps.python.org/api/peps.json で 794 は Accepted、8 は Active、ほかは Final） |
| Core metadata specifications / Ruff A005 | https://packaging.python.org/en/latest/specifications/core-metadata/ ・ https://docs.astral.sh/ruff/rules/stdlib-module-shadowing/ （2026-11-08 確認。`Import-Name` はメタデータ 2.5 / `strict-checking` の意味） |
| Node.js — Modules / ECMAScript modules / Packages / TC39 | https://nodejs.org/api/modules.html ・ https://nodejs.org/api/esm.html ・ https://nodejs.org/api/packages.html ・ https://github.com/tc39/proposal-defer-import-eval （2026-11-08 確認。v26.13.0 の docs。キャッシュ・循環・拡張子・`exports`・トップレベルの `await` / `import defer` は "Stage: 3"） |

### 確認できなかった事項

- **Bun の `import defer` の対応範囲**（Bun 1.4.4 で評価が遅れることだけを確かめ、Bun の docs は見ていない）、**`Import-Name` を書く配布物がどれだけあるか**（確かめたのは 3 つだけ）と、**`lazy import` の一般的な速度の効果**（測ったのは `PIL.Image` 1 つだけ）

- 関連: [Python 学習ガイド](../README.md) / [Step 02: 文法の差分](../steps/02-language.md) / [Step 03: プロジェクト構成](../steps/03-project.md) / [Step 04: 型](../steps/04-typing.md) / [uv](uv.md) / [pyproject.toml](pyproject-toml.md)
