# 型チェッカー — mypy・pyright・ty・Pyrefly の選び方

> 出典（一次情報）:
> - [mypy documentation (mypy.readthedocs.io)](https://mypy.readthedocs.io/en/stable/) — 型の無い関数の扱い・設定項目・`strict`
> - [Pyright docs (microsoft/pyright)](https://github.com/microsoft/pyright/tree/main/docs) — `typeCheckingMode`・mypy との違い・プラグインを持たない理由
> - [basedpyright docs (docs.basedpyright.com)](https://docs.basedpyright.com/) / [ty docs (docs.astral.sh)](https://docs.astral.sh/ty/) / [Pyrefly docs (pyrefly.org)](https://pyrefly.org/en/docs/configuration/) — 各ツールの既定と設定
> - [Mypy plugin (docs.pydantic.dev)](https://docs.pydantic.dev/latest/integrations/mypy/) — Pydantic の mypy プラグインと `init_typed`
> - [Typing conformance results (python/typing)](https://github.com/python/typing/tree/main/conformance/results) — 型システムの仕様への適合度
>
> 最終更新: 2026-11-08（mypy 2.4.1・pyright 1.1.414・basedpyright 1.40.2・ty 0.0.99・pyrefly 1.4.1・Python 3.15.2・uv 0.13.7 で検証）

TypeScript では、型の検査は言語と同じ `tsc` が受け持つ。Python の型ヒントは言語の一部だが、**検査する道具は言語の外にあり、複数ある**。同じコードでも、道具と設定しだいで報告が変わる。
5 つを同じ誤りにかけた結果は [Step 04](../steps/04-typing.md) の §3.7–§3.8 にある（ここでは繰り返さない）。通し課題で mypy を設定するのは [Step 05](../steps/05-quality.md) である。

---

## 1. TL;DR

- **既定の選択は mypy か pyright**（索引の推奨構成と同じ）。通し課題は mypy を使う。Pydantic の mypy プラグインがあり、GitHub の python 組織が持つ型チェッカーだからである。
- **既定の厳しさがツールごとに違う**。mypy は型ヒントの無い関数の中身を検査しない。Pyrefly は設定が無いと `basic` プリセット（確度の高い誤りだけ）になる。比べるときは設定をそろえる（§3.2）。
- **mypy と Pydantic プラグインの組み合わせは、既定で `__init__` の引数を `Any` として扱う**。通し課題で、mypy の strict は通るのに、ほかの 4 つは同じ 1 行を誤りとして報告した（§4.1）。
- 速度の参考値（通し課題、手元の M2 Max）: ty 0.11 秒・Pyrefly 0.29 秒・mypy 0.48 秒（キャッシュあり）・pyright 1.63 秒（§5.2）。
- ty は 1.0 前（beta）。Pyrefly は 1.0.0 で stable を宣言済み。どちらも試す価値はあるが、CI の必須の検査には 1 つに絞る（§5.3）。

---

## 2. Node.js / Bun との対応

| TypeScript（`tsconfig.json`） | mypy（`[tool.mypy]`） | pyright（`[tool.pyright]`） | メモ |
|---|---|---|---|
| `tsc --noEmit` | `mypy` | `pyright` | Python は型を消す工程が無い。検査だけを行う |
| `"strict": true` | `strict = true` | `typeCheckingMode = "strict"` | mypy の docs: "the exact list of flags enabled by strict may change over time." |
| `"noImplicitAny": true` | `disallow_untyped_defs = true` | `reportMissingParameterType = "error"` など | 型の無い関数を誤りにする。mypy の strict に含まれる |
| （TS は常に関数の中身を検査する） | `check_untyped_defs = true` | 既定で検査する | mypy だけが既定で中身を飛ばす（§6） |
| `"skipLibCheck": true` に近い発想 | `ignore_missing_imports`（モジュール単位で） | `reportMissingTypeStubs`（既定 `"none"`） | 型情報の無い依存を許す。mypy は全体で有効にするのを勧めていない |
| `@types/*` | `types-*`（typeshed のスタブ） | 同じ | 型を持たないパッケージ用の別配布 |
| `"include"` / `"exclude"` | `files` / `exclude` | `include` / `exclude` | 通し課題は `files = ["src", "tests"]` |
| エディタ: VS Code 内蔵の TS Server | mypy は LSP を持たない（外部の拡張で使う） | Pylance の中身が pyright | 下の §3.2 |

> **ポイント**: `tsc` の型エラーはビルドを止める。Python では型チェッカーを回さなくても実行できる（[Step 04](../steps/04-typing.md) の §3.6）。CI で型チェッカーを必須にして、初めて `tsc` と同じ役目になる。

---

## 3. 早見表

### 3.1 5 つの型チェッカー

| 名前 | 開発元 | 実装 | ライセンス | 版（2026-11-08） | 状態 |
|---|---|---|---|---|---|
| mypy | GitHub の python 組織（python/mypy） | Python（mypyc でコンパイル） | MIT | 2.4.1 | 安定版。最も長く使われてきた |
| pyright | Microsoft | TypeScript（Node.js が要る） | MIT | 1.1.414 | 安定版。PyPI の `pyright` は Node.js ごと入れるコミュニティのラッパー |
| basedpyright | コミュニティ（DetachHead/basedpyright） | pyright のフォーク | MIT | 1.40.2 | 安定版。PyPI から Node.js なしで入る |
| ty | Astral（uv・Ruff の開発元） | Rust | MIT | 0.0.99 | **beta**。README: "ty is currently in beta." |
| Pyrefly | Meta | Rust | MIT | 1.4.1 | stable（1.0.0 で宣言）。ただし semver に厳密には従わない |

- pyright の docs は、VS Code では pyright 単体より Pylance を勧めている。原文は "Pylance incorporates the Pyright type checker but features additional capabilities such as semantic token highlighting and symbol indexing." Pylance 自体はソースを公開していない（Pydantic の docs: "it's closed source, but free to use"）
- 版の方針: ty は "breaking changes, including changes to diagnostics, may occur between any two versions."、Pyrefly は "any version may introduce new type errors and other breaking changes."

### 3.2 既定の厳しさ・設定の場所・エディタ

| 項目 | mypy | pyright | basedpyright | ty | Pyrefly |
|---|---|---|---|---|---|
| `pyproject.toml` の表 | `[tool.mypy]` | `[tool.pyright]` | `[tool.basedpyright]` | `[tool.ty]` | `[tool.pyrefly]` |
| 専用の設定ファイル | `mypy.ini` など | `pyrightconfig.json`（`pyproject.toml` より優先） | `pyrightconfig.json` | `ty.toml` | `pyrefly.toml` |
| 厳しさの段階 | 個別のフラグと `strict` | `off` / `basic` / `standard` / `strict` | 左の 4 つ + `recommended` / `all` | ルールごとに levels を設定 | プリセット `off` / `basic` / `legacy` / `default` / `strict` / `all` |
| 既定 | 型の無い関数の中身を飛ばす | `standard` | `recommended`（警告でも終了コードが 0 でなくなる） | 既定のルール | 設定が無いと `basic`。`[tool.mypy]` などがあれば移し替えて使う |
| 型の無い依存（`py.typed` 無し） | 解析を飛ばして報告する（[Step 04](../steps/04-typing.md)） | ライブラリのコードから推論する（`useLibraryCodeForTypes` の既定 true） | 同左 | 解析した（Step 04 の検証） | 未確認（Step 04 の検証はプリセットの差しか見ていない） |
| Pydantic | 公式のプラグイン（`pydantic.mypy`） | `dataclass_transform`（PEP 681）で理解する | 同左 | 同左 | 組み込みの対応（docs の "built-in support"） |
| 言語サーバ（LSP） | 無い | あり（VS Code では Pylance） | あり | あり | あり |

- Pyrefly の docs: 設定が無いときは "Pyrefly uses the [**basic preset**] ... This enables only high-confidence error kinds (syntax errors, missing imports, division by zero, etc.); other diagnostics are silenced." 推奨は "For most users, we recommend using the `strict` preset"
- pyright はプラグインを持たない。理由は docs にあり、代わりに型システムの側を広げる方針で、"An example of this is PEP 681, which introduced `dataclass_transform`." Pydantic の `BaseModel` は `@dataclass_transform` を付けて定義されている（pydantic のソース）
- **Zed の既定**: Python の言語サーバは basedpyright（Zed v0.204.0 から）。ただし Zed は `standard` モードで起動する。原文 "Zed configures it to use the less-strict standard mode by default, which matches the behavior of Pyright." ty・Pyrefly・pyright も組み込みで、設定で切り替える。Pyrefly は設定ファイルがあるときだけ型エラーを表示する

### 3.3 コマンド

| やりたいこと | コマンド |
|---|---|
| dev 依存に入れて動かす（通し課題の形） | `uv add --dev mypy` → `uv run mypy` |
| その 1 回だけ別のものを試す | `uv run --with pyright==1.1.414 pyright src tests`（`basedpyright` も同じ形）/ `uv run --with ty==0.0.99 ty check src tests` / `uv run --with pyrefly==1.4.1 pyrefly check src tests` |
| Pyrefly の設定を mypy / pyright の設定から作る | `pyrefly init` |
| ty をプロジェクトの環境で動かす | `uv check`（experimental） |

---

## 4. 推奨の使い方（2026-11）

### 4.1 通し課題（Step 07 の状態）に 5 つをかける

[Step 05](../steps/05-quality.md) の設定（`[tool.mypy]` に `strict = true` と `plugins = ["pydantic.mypy"]`）のまま、5 つを `src` と `tests` にかけた。mypy は通った（検証済み）。

実行結果:

```text
$ uv run mypy
Success: no issues found in 10 source files
```

pyright・basedpyright・ty・Pyrefly は、テストの同じ 1 行を報告した。ty の出力（検証済み）:

実行結果:

```text
$ uv run --with ty==0.0.99 ty check src tests
error[invalid-argument-type]: Argument is incorrect
  --> tests/test_loader.py:25:36
   |
25 |     assert load_faqs(path) == [Faq(**VALID)]
   |                                    ^^^^^^^ Expected `Literal["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]`, found `str`

Found 1 diagnostic
```

`VALID` は `dict[str, str]` と推論される辞書で、`category` は `Literal[...]` の型である。実行時は Pydantic が検証するので問題なく動くが、型の上では `str` を `Category` に渡している。

mypy が黙っていた理由は Pydantic の mypy プラグインの既定にある。docs の原文は "the plugin will use Any for field annotations when synthesizing the `__init__()` method, unless init_typed is set or strict mode is enabled on the model." `pyproject.toml` に `[tool.pydantic-mypy]` の表を作り `init_typed = true` を書くと、mypy も同じ行を報告した（検証済み）。

実行結果:

```text
$ uv run mypy
tests/test_loader.py:25: error: Argument 1 to "Faq" has incompatible type "**dict[str, str]"; expected "Literal['経費', '勤怠', 'IT', '総務', '出張', 'セキュリティ']"  [arg-type]
Found 1 error in 1 file (checked 10 source files)
```

プラグインを外しても（`dataclass_transform` だけで解釈させても）同じ 1 件になった（検証済み）。辞書から作る箇所は `Faq.model_validate(VALID)` に直すと、`init_typed = true` の mypy・pyright・ty・Pyrefly のすべてが通った（検証済み）。`model_validate` は検証する前提の入口で、引数を `Any` として受け取る。

### 4.2 推奨の表

| 推奨 | 避ける | 理由 |
|---|---|---|
| CI で回す型チェッカーは 1 つにし、dev 依存に入れて版を lockfile で固定する | 型チェッカーを `uvx` で最新版のまま回す | 版が上がると診断が変わる（ty・Pyrefly は方針として明記している）。`uvx` はプロジェクトの依存を見ない |
| mypy なら `strict = true`、pyright なら `typeCheckingMode = "strict"` から始める | 既定のまま「エラー 0 件」で安心する | mypy の既定は型の無い関数を飛ばし、Pyrefly の既定（設定なし）は `basic` である |
| mypy で Pydantic を使うなら `plugins = ["pydantic.mypy"]` と `init_typed = true` を検討する | プラグインの既定を知らずに使う | 既定ではモデルの生成時の型の誤りを見逃す（§4.1） |
| エディタとは別の型チェッカーを CI で使ってよい。差が出たら CI の結果を正とする | エディタの赤線と CI の結果が違うことに悩み続ける | Zed の既定は basedpyright（`standard`）、VS Code は Pylance（pyright）である。mypy には LSP が無い |
| ty・Pyrefly は手元で並べて試す | 1.0 前の ty を CI の唯一の検査にする | ty は beta で、診断が版ごとに変わりうる |

`uv check` は ty をプロジェクトの環境で動かす（experimental）。通し課題では `ty check src tests` と同じ 1 件を報告した（検証済み）。

実行結果:

```text
$ uv check
warning: `uv check` is experimental and may change without warning. Pass `--preview-features check-command` to disable this warning.
error[invalid-argument-type]: Argument is incorrect
…（中略: 5 行）…
Found 1 diagnostic
```

---

## 5. 選び方・代替との比較

### 5.1 型システムの仕様への適合度

python/typing リポジトリは、型システムの仕様（typing.python.org）のテスト一式を各型チェッカーにかけた結果を公開している。`conformance/results/` の TOML を、同リポジトリの `reporting.py` と同じ規則（手で付けた `conformant` を優先し、無ければ自動判定が Pass のものを Pass）で数えた（検証済み。commit `4abf23e`、2026-10-31）。

実行結果:

```text
$ python3 conformance_tally.py typing/conformance/results
mypy 2.4.0       total=146 Partial=56 Pass=82 Unsupported=8
pyright 1.1.414  total=146 Partial=5 Pass=138 Unsupported=3
pyrefly 1.4.0    total=146 Partial=4 Pass=140 Unsupported=2
ty 0.0.93        total=146 Partial=10 Pass=136
```

- 数字はテストのファイル単位で、「仕様のその節に完全に従うか」である。日々のバグの見つけやすさとは別の尺度である。試験に使われた版は、本ガイドの検証の版（mypy 2.4.1・pyrefly 1.4.1・ty 0.0.99）と少し違う。basedpyright は対象に入っていない
- Partial・Unsupported の理由は、各 TOML の `notes` に 1 項目ずつ書かれている（例: mypy の `aliases_newtype` は "`NewType`s are incorrectly considered to be classes."）

### 5.2 速度（参考値）

通し課題（Step 07、`src` と `tests` の 10 ファイル）で、各コマンドを 1 回空回ししてから 10 回測った中央値（検証済み）。`uv run true` は uv 自体のかかる時間である。

実行結果:

```text
$ python3 bench.py faq-app 10
  0.48s  (min 0.48s, n=10)  uv run mypy
  2.52s  (min 2.48s, n=10)  uv run mypy --no-incremental
  1.63s  (min 1.58s, n=10)  uv run --with pyright==1.1.414 pyright src tests
  1.43s  (min 1.37s, n=10)  uv run --with basedpyright==1.40.2 basedpyright src tests
  0.11s  (min 0.11s, n=10)  uv run --with ty==0.0.99 ty check src tests
  0.29s  (min 0.29s, n=10)  uv run --with pyrefly==1.4.1 pyrefly check src tests
  0.03s  (min 0.03s, n=10)  uv run true
```

小さなプロジェクトでは、どれも CI のボトルネックにはならない。mypy は `.mypy_cache/` の差分検査で速くなる（`--no-incremental` は毎回すべてを解析する）。pyright と basedpyright は Node.js の起動を含む。

### 5.3 どれを選ぶか

| 状況 | 選ぶもの | 理由 |
|---|---|---|
| 迷ったとき・本ガイドの通し課題 | mypy | プラグインの仕組みがあり、Pydantic は公式のプラグインを配る |
| VS Code（Pylance）や Zed と診断をそろえたい | pyright か basedpyright | エディタと CI が同じ実装になる。仕様への適合度も高い（§5.1） |
| 大きなコードベースで速さが要る | Pyrefly を試す | Rust 製で速く、stable を宣言している。`pyrefly init` で mypy / pyright の設定から移れる |
| Astral の道具（uv・Ruff）でそろえたい | ty を手元で試す | 速く、`uv check` で動く。1.0 前なので、CI の必須の検査は mypy か pyright のまま残す |

> **注意**: 2 つの型チェッカーを並べて動かすことはできる（設定の表が分かれているので衝突しない）。ただし、CI で両方を必須にすると、片方だけが報告する差を毎回なだめる作業が増える。必須は 1 つにし、もう 1 つは手元か、失敗しても止めないジョブで回す。

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| mypy の strict が通るのに、pyright・basedpyright・ty・Pyrefly は `Faq(**VALID)` を報告する（検証中に発生） | Pydantic の mypy プラグインは、既定で `__init__` の引数を `Any` にする | `[tool.pydantic-mypy]` の `init_typed = true`。辞書から作るなら `Faq.model_validate(...)`（§4.1） |
| 型ヒントの無い関数の誤りを mypy が報告しない（検証で再現） | mypy の既定は "will not type check dynamically typed functions" | `check_untyped_defs = true` か `strict = true`。pyright は既定で中身も検査する |
| Pyrefly が何も報告しない（検証で再現） | 設定が無いと `basic` プリセットになる | `pyrefly init` で設定を作るか、`[tool.pyrefly]` に `preset = "strict"` などを書く |
| 同じ Pyrefly でも、プロジェクトによって厳しさが変わる（検証中に発生） | `[tool.pyrefly]` が無く `[tool.mypy]` があると、その設定を移し替えて使う。通し課題では "using settings imported from `[tool.mypy]` ... (preset: legacy)" と出た | Pyrefly を使うなら `[tool.pyrefly]` を明示する |
| mypy が自分のパッケージを `Skipping analyzing` する | `py.typed` が無い（[Step 04](../steps/04-typing.md) の §3.7） | `src/<名前>/py.typed` を置くか、ソースのディレクトリも渡す |
| basedpyright だけ警告が大量に出て、終了コードも 0 でない | 既定が `recommended`（警告でも失敗する） | `typeCheckingMode = "standard"` にそろえるか、警告を 1 つずつ判断する |
| エディタと CI で結果が違う | エディタの言語サーバと CI の型チェッカーが別物 | §4.2。Zed なら `language_servers` で切り替えられる |

型ヒントの無い関数の例（[Step 04](../steps/04-typing.md) の検証で使った `untyped_demo.py`）。2 行目の型の無い `total` と、6 行目の型のある `total_typed` に、同じ誤り（`int + str`）がある。mypy は 6 行目だけを報告した。pyright は 2 行目と 6 行目の両方を報告した（検証済み）。

実行結果:

```text
$ uv run --with mypy==2.4.1 mypy untyped_demo.py
untyped_demo.py:6: error: Incompatible return value type (got "int", expected "str")  [return-value]
untyped_demo.py:6: error: Unsupported operand types for + ("int" and "str")  [operator]
Found 2 errors in 1 file (checked 1 source file)
```

---

## 出典

| 情報源 | URL（確認日） |
|---|---|
| mypy — Getting started / The mypy configuration file / Running mypy | https://mypy.readthedocs.io/en/stable/getting_started.html ・ https://mypy.readthedocs.io/en/stable/config_file.html ・ https://mypy.readthedocs.io/en/stable/running_mypy.html （2026-11-08） |
| python/mypy（LICENSE・README の mypyc） | https://github.com/python/mypy （2026-11-08） |
| Pyright — Configuration / Installation / Mypy comparison | https://github.com/microsoft/pyright/blob/main/docs/configuration.md ・ https://github.com/microsoft/pyright/blob/main/docs/installation.md ・ https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md （2026-11-08） |
| basedpyright — README / Config files | https://github.com/DetachHead/basedpyright ・ https://docs.basedpyright.com/latest/configuration/config-files/ （2026-11-08） |
| ty — README（beta・Version policy）/ Configuration | https://github.com/astral-sh/ty ・ https://docs.astral.sh/ty/reference/configuration/ （2026-11-08） |
| Pyrefly — README / Configuration / Pydantic Support | https://github.com/facebook/pyrefly ・ https://pyrefly.org/en/docs/configuration/ ・ https://pyrefly.org/en/docs/pydantic/ （2026-11-08） |
| Pydantic — Mypy plugin / Visual Studio Code | https://docs.pydantic.dev/latest/integrations/mypy/ ・ https://docs.pydantic.dev/latest/integrations/visual_studio_code/ （2026-11-08） |
| PEP 681（`dataclass_transform`） | https://peps.python.org/pep-0681/ （2026-11-08） |
| Typing conformance results | https://github.com/python/typing/tree/main/conformance/results （2026-11-08。commit 4abf23e） |
| Zed — Python | https://zed.dev/docs/languages/python （2026-11-08） |
| Bringing uv and ty together | https://astral.sh/blog/uv-ty-integration （2026-11-08。2026-10-13 公開） |
| 各版 | PyPI（2026-11-08） |

### 確認できなかった事項

- **適合度の数字を results.html の表示と突き合わせること**。HTML の集計表は読まず、同じリポジトリの TOML と `reporting.py` の規則から数えた。basedpyright は試験の対象に無い
- **Pyrefly の Pydantic 対応が mypy プラグインの `init_typed` に相当する挙動か**。通し課題では型どおりに検査したが、docs で設定項目までは確かめていない
- **速度の比較を大きなコードベースで行うこと**。§5.2 は 10 ファイルでの参考値で、各プロジェクトが公表するベンチマークとは条件が違う

- 関連: [Python 学習ガイド](../README.md) / [Step 04: 型](../steps/04-typing.md) / [Step 05: 品質ツール](../steps/05-quality.md) / [uv](uv.md) / [Ruff](ruff.md) / [Pydantic](pydantic.md) / [pyproject.toml](pyproject-toml.md)
