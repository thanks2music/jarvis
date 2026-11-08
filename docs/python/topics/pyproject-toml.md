# pyproject.toml — package.json にあたる設定ファイル

> 出典（一次情報）:
> - [pyproject.toml specification (packaging.python.org)](https://packaging.python.org/en/latest/specifications/pyproject-toml/) — `[project]`・`[build-system]`・`[tool]` の仕様（PEP 518 / 621 の現行版）
> - [Version specifiers (packaging.python.org)](https://packaging.python.org/en/latest/specifications/version-specifiers/) と [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/) — `~=`・プレリリース・環境マーカー（PEP 440 / 508 の現行版）
> - [Dependency Groups (packaging.python.org)](https://packaging.python.org/en/latest/specifications/dependency-groups/) / [PEP 517](https://peps.python.org/pep-0517/) / [PEP 639](https://peps.python.org/pep-0639/) — `[dependency-groups]`（PEP 735）/ ビルドバックエンド / ライセンスの SPDX 式
> - [The uv build backend](https://docs.astral.sh/uv/concepts/build-backend/) と [Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)（docs.astral.sh）— `uv_build` と `[tool.uv.sources]`
>
> 最終更新: 2026-11-08（uv 0.13.7・Python 3.15.2・Node.js 26.13.0 で検証）

Node.js の `package.json` にあたるのが `pyproject.toml` である。名前・版・依存・コマンドを書く点は同じだが、TOML で書き、**標準の表（`[project]` など）とツールごとの表（`[tool.*]`）が分かれ**、配布物を作る道具（`[build-system]`）も自分で宣言する。版の書き方は semver ではなく PEP 440 である。
`uv init` が作る最小の形は [Step 03](../steps/03-project.md) の §3.2 で読んだ。ここでは各項目の書き方を引けるようにする。

---

## 1. TL;DR

- **`[project]` は標準の表で、どのツールも読む**。`[tool.uv]`・`[tool.ruff]` はそのツールだけが読む。`package.json` に `eslintConfig` を書くのと同じく、設定を 1 つのファイルに集められる。
- **開発用の依存は `[dependency-groups]`、利用者が選んで入れる機能は extras（`[project.optional-dependencies]`）**。前者は配布物のメタデータに載らず、後者は載る（§4）。npm の `optionalDependencies`・`peerDependencies` は、どちらとも別物である（§2）。
- **`~=` は npm の `^` でも `~` でもない**。最後の桁を外した前方一致で、`~=1.4.5` は `>=1.4.5, ==1.4.*`、`~=1.4` は `>=1.4, ==1.*` になる。npm の `^1.4.5` を写すなら `>=1.4.5,<2` と書く（§3.2）。
- **`==2.14` は `2.14.0` だけに一致する**（npm の `2.14` は `2.14.x`）。範囲なら `==2.14.*`。プレリリースは、明示したときか、安定版で条件を満たせないときだけ選ばれる（§3.2）。
- **`[build-system]` はビルドバックエンドの宣言**。`uv init` が書く `uv_build` は pure Python 専用で、拡張モジュールや build script が要るなら hatchling・setuptools・maturin などに替える（§5.1）。

---

## 2. Node.js / Bun との対応

| `package.json` | `pyproject.toml` | 違い |
|---|---|---|
| `name` / `version` / `description` | 同じ名前のキー | 名前の比較では大小文字と `-`・`_`・`.` を区別しない（name normalization の仕様）。版は PEP 440（`1.0.0b1`・`1.0.0.post1`） |
| `engines.node` | `requires-python` | npm の `engines` は `engine-strict` を付けない限り "advisory only"。Python のインストーラは版を選ぶのに使い、uv は依存の解決にも使う（§6） |
| `dependencies` | `dependencies` | オブジェクトではなく文字列の配列（`"pydantic>=2.14,<3"`） |
| `devDependencies` | `[dependency-groups]` の `dev` | 配布物のメタデータに載らない |
| `optionalDependencies` / `peerDependencies` | 対応するものは無い | extras は別の仕組み（下のポイント） |
| `bin` / `scripts` | `[project.scripts]` / 無い | `faq = "faq:main"`（`モジュール:関数`）。`npm run` 用のタスクは uv にも無い（[uv](uv.md) §6） |
| `license` | `license` + `license-files` | SPDX の式（PEP 639）。古い表の形（`{ text = "MIT" }`）は非推奨だが、uv_build 0.13.7 は警告を出さずにビルドした（検証済み） |
| `"private": true` | `classifiers = ["Private :: Do Not Upload"]` | PyPI: "PyPI will always reject packages with classifiers beginning with `Private ::`." |
| `homepage` / `repository` / `bugs` | `[project.urls]` | ラベルは自由だが、`Homepage`・`Source`・`Issues`・`Changelog`・`Documentation` などは意味の決まったラベルで、仕様は "users are *encouraged* to pick meaningful labels that normalize to well-known labels" とする（Well-known Project URLs） |
| `eslintConfig` / `prettier` など | `[tool.<名前>]` | 仕様: "a project can use the subtable `tool.$NAME` if, and only if, they own the entry for `$NAME` in the Cheeseshop/PyPI." |
| `"x": "file:../x"` / `workspaces` | `[tool.uv.sources]` / `[tool.uv.workspace]` | 標準ではなく uv だけが読む（§3.4）。npm に無い `[build-system]` は §5.1 |

> **ポイント**: npm の `optionalDependencies` は「既定で入れるが、入らなくても失敗にしない」依存、`peerDependencies` は「ホストが入れているはずの依存」である（npm 7 からは自動で入る。npm docs）。extras は**既定では入れず、利用者が `faq[yaml]` と名前で頼んだときだけ入れる**追加の依存で、配布物のメタデータに `Provides-Extra` として載る。pandas の `excel`・`plot` が例である（uv docs）。

---

## 3. 早見表（コマンド・設定）

### 3.1 uv のコマンドと書き込む先

| コマンド | 書き込む先・効果 |
|---|---|
| `uv add x` / `uv add --optional yaml x` / `uv add --dev x` / `uv add --group lint x` | `dependencies` / `[project.optional-dependencies]` の `yaml` / `[dependency-groups]` の `dev` / `lint` |
| `uv add --bounds major rich` / `--bounds minor orjson` | 上限も書く。`"rich>=15.0.0,<16.0.0"` / `"orjson>=3.13.0,<3.14.0"` になった（検証済み）。既定（`lower`）は下限だけ |
| `uv sync --extra yaml` / `--all-extras` / `--group lint` / `--all-groups` / `--no-dev` | extras やグループを足して入れる / `dev` を外す。素の `uv sync` は extras を入れない（検証済み） |
| `uv version --bump minor` / `--bump patch --bump beta` | `version` を上げる。`--dry-run` で `faq 0.1.0 => 0.2.0` / `faq 0.1.0 => 0.1.1b1` と表示した（検証済み） |

### 3.2 版の指定（PEP 440）

各指定を `echo "<指定>" | uv pip compile - --no-deps` で、2026-11-08 の PyPI に対して解決した（検証済み。ログは `06_resolve.log`）。

| 書き方 | 意味 | 選ばれた版 |
|---|---|---|
| `pydantic>=2.12,<2.14` | 範囲。`,` は「かつ」 | 2.13.5 |
| `pydantic~=2.13` / `pydantic~=2.13.0` | `>=2.13, ==2.*` / `>=2.13.0, ==2.13.*` | 2.14.3 / 2.13.5 |
| `pydantic==2.12.*` | 前方一致 | 2.12.5 |
| `pydantic==2.14` | 完全一致。足りない桁は 0 で埋めるので `2.14.0` | 2.14.0 |
| `pydantic!=2.14.3` | その版を除く | 2.14.2 |
| `httpx` / `httpx>0.28.1` | 安定版から選ぶ / 安定版では満たせないので、プレリリースに下がる | 0.28.1 / 1.0.dev6 |
| `httpx>=1.0` / `httpx>=1.0.dev0` | `1.0.dev6` は `1.0` より前なので満たす版が無い / プレリリースを明示する | 解決できない / 1.0.dev6 |

npm の `^`・`~` と、Python の `~=` を同じ 10 個の版に当てて比べる。上が npm の semver 7.8.5（`semver.satisfies`）、下が PyPA の packaging 26.3（`SpecifierSet`）である（検証済み）。

実行結果:

```text
$ node semver-npm/ranges.mjs
^1.4.5       1.4.5 1.4.9 1.5.0 1.9.0
~1.4.5       1.4.5 1.4.9
^0.2.3       0.2.3 0.2.9
~0.2.3       0.2.3 0.2.9
$ uv run --no-project --with packaging==26.3 python specifiers.py
Installed 1 package in 4ms
>=1.4.5,<2   1.4.5 1.4.9 1.5.0 1.9.0
~=1.4.5      1.4.5 1.4.9
~=1.4        1.4.4 1.4.5 1.4.9 1.5.0 1.9.0
~=0.2.3      0.2.3 0.2.9
~=0.2        0.2.3 0.2.9 0.3.0 0.9.0
>=0.2.3,<0.3 0.2.3 0.2.9
```

- `~=` は、書いた版の**最後の桁を外した前方一致**に下限を足したものである（仕様: `~= V.N` は "approximately equivalent to the pair of comparison clauses" で、`>= V.N, == V.*` と同じ）。桁数で意味が変わり、`~=1.4` は 1.4.4 も含む。npm の `^1.4.5` にあたるのは `>=1.4.5,<2` である
- 差が大きいのは 0.x である。npm の `^0.2.3` は 0.2.x に絞るが（"Allows changes that do not modify the left-most non-zero element"）、`~=0.2` は 0.9.0 まで許す。0.x の依存は `~=0.2.3` か `>=0.2.3,<0.3` と書く
- 版の順序は `1.0.dev456 < 1.0a1 < 1.0b2 < 1.0rc1 < 1.0 < 1.0.post456`（仕様の例から抜粋）。semver の `1.0.0-beta.1` は `1.0.0b1` と書く。`<3` は 3.0 のプレリリースも除く（仕様: "`<V` MUST NOT allow a pre-release of the specified version"）。uv のプレリリースの既定は 0.12 から `if-necessary` で、"uv prefers stable versions over pre-releases, falling back to pre-releases only if every stable candidate that satisfies the active constraints is rejected during resolution."（uv docs）。`[tool.uv] prerelease = "allow"` などで変えられる

### 3.3 環境マーカー（PEP 508）

`;` の後ろに条件を書くと、その環境でだけ依存が入る。`requires-python = ">=3.15"` のプロジェクトの `dependencies` に、`'typing-extensions>=4.15; python_version < "3.16"'`・`'appnope>=0.1.4; sys_platform == "darwin"'`・`'colorama>=0.4.6; sys_platform == "win32"'` の 3 つを書き（中に `"` があるので TOML の文字列は `'` で囲む）、`uv lock` の後で Windows の Python 3.16 として依存のツリーを見た（検証済み）。

実行結果:

```text
$ uv tree --python-platform windows --python-version 3.16
Using CPython 3.15.2
Resolved 4 packages in 6ms
markers-demo v0.1.0
└── colorama v0.4.6
```

- 手元の macOS で素の `uv tree` を打つと appnope と typing-extensions が、`--python-platform linux` では typing-extensions だけが並んだ（検証済み）。`uv lock` は手元の環境に関係なく 3 つすべてを解決し、`uv.lock` にマーカー付きで記録する（`python_version < "3.16"` は `python_full_version < '3.16'` に書き換わる）。lockfile は全環境で 1 つで、`uv sync` が今の環境に合うものだけを入れる
- よく使う変数は `python_version`（`3.15`）・`python_full_version`（`3.15.2`）・`sys_platform`（`darwin`・`linux`・`win32`）・`platform_machine`（`arm64`・`x86_64` など。OS ごとに表記が違う）。OS の判定は `sys_platform` で行う（仕様: "the most well defined field for use when declaring platform specific dependencies"）。npm では依存される側が `os`・`cpu` を宣言するが、Python では依存する側が条件を書く

### 3.4 `[tool.uv]` でよく使う設定

| 設定 | 何をするか |
|---|---|
| `default-groups = ["dev", "lint"]`（`"all"` も可） | `uv sync`・`uv run` が既定で入れるグループ。既定は `dev` だけ。`lint` を足して `uv sync` すると、それまで消されていた `ruff` が `+ ruff==0.17.4` と入った（検証済み） |
| `[tool.uv.sources]` | 依存の取得元を、PyPI から path・git・workspace・別の index に替える。`uv add ../faq-core` は `faq-core = { path = "../faq-core" }` を、`uv add git+https://github.com/encode/httpx --tag 0.28.1` は `httpx = { git = "https://github.com/encode/httpx", tag = "0.28.1" }` を書いた（検証済み）。`[tool.uv.workspace]` はモノレポのメンバー（[uv](uv.md) §4） |

- `dependencies` には `"faq-core"` と `"httpx"` の名前しか残らない。wheel のメタデータも `Requires-Dist: faq-core` と `Requires-Dist: httpx` だけで、取得元は載らなかった（検証済み）。公式 docs: "Sources are only respected by uv." 配布前は `uv build --no-sources` で、sources なしでもビルドできるかを確かめる（同 docs）
- ディレクトリの path 依存は、既定では editable ではない（"An editable installation is not used for path dependencies by default."）。編集をすぐ反映させたいなら `uv add --editable ../faq-core`

---

## 4. 推奨の使い方（2026-11）

[Step 04](../steps/04-typing.md) の faq を、配布できる形まで書き足した例である。`uv lock` と `uv build` が通った（検証済み）。

```toml
[project]
name = "faq"                       # 配布名。比較では大小文字と - _ . を区別しない
version = "0.1.0"                  # PEP 440 の版。uv version --bump で上げる
description = "社内 FAQ を読み込んで検索する CLI"
readme = "README.md"
license = "MIT"                    # SPDX の式（PEP 639）
license-files = ["LICENSE"]        # 配布物に同梱するライセンスの文書
authors = [{ name = "FAQ Team" }]
requires-python = ">=3.15"         # engines.node にあたる。上限は付けない
classifiers = ["Private :: Do Not Upload"]  # "private": true にあたる
dependencies = ["pydantic>=2.14,<3"]        # 実行時の依存
urls = { Source = "https://github.com/example/faq" }  # homepage / repository にあたる

[project.optional-dependencies]    # extras。faq[yaml] と頼まれたときだけ入る
yaml = ["pyyaml>=6.0"]

[project.scripts]                  # bin にあたる
faq = "faq:main"

[dependency-groups]                # 開発用。配布物には載らない（PEP 735）
test = ["pytest>=9.2"]
lint = ["ruff>=0.17"]
dev = ["ipython>=9.18.1", { include-group = "test" }, { include-group = "lint" }]

[tool.ruff]                        # ツールの設定も同じファイルに置ける
line-length = 100

[build-system]                     # wheel と sdist を作る道具
requires = ["uv_build>=0.13.7,<0.14.0"]
build-backend = "uv_build"
```

実行結果:

```text
$ uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/faq-0.1.0.tar.gz
Successfully built dist/faq-0.1.0-py3-none-any.whl
$ unzip -p dist/faq-0.1.0-py3-none-any.whl "faq-0.1.0.dist-info/METADATA" | sed -n "1,/^$/p"
…（中略: 5 行）…
License-Expression: MIT
License-File: LICENSE
Classifier: Private :: Do Not Upload
Requires-Dist: pydantic>=2.14,<3
Requires-Dist: pyyaml>=6.0 ; extra == 'yaml'
Requires-Python: >=3.15
Project-URL: Source, https://github.com/example/faq
Provides-Extra: yaml
…（中略: 1 行）…
```

- `uv build` は、ソース一式の sdist（`.tar.gz`）を作り、そこから、そのまま入れられる wheel（`.whl`）を作る。`npm pack` の `.tgz` 1 つとは違い、配布物は 2 種類ある。wheel のメタデータに入るのは `[project]` の中身だけである。extras は `Provides-Extra` と `extra == 'yaml'` 付きの `Requires-Dist` になり、dependency groups（ipython・pytest・ruff）は載らない。`uv tree --depth 1` では、`include-group` で取り込んだ pytest と ruff も `(group: dev)` と表示された（検証済み）
- `LICENSE` は wheel の `faq-0.1.0.dist-info/licenses/` に入った。sdist には、uv_build が書き直した `pyproject.toml` と元の `pyproject.toml.orig` が入る（公式 docs: "The `pyproject.toml`, rewritten using TOML 1.0-compatible syntax. The original file is also included as `pyproject.toml.orig`."）

| 推奨 | 理由 |
|---|---|
| 依存には下限を付ける（`uv add` の既定）。アプリの版は `uv.lock` が固定する | uv docs: "Lower bounds are particularly critical when writing a library." 下限が無いと、依存が衝突したときに resolver が古い版まで戻ることがある |
| `requires-python` は下限だけを書く | uv docs: "When evaluating `requires-python` ranges for dependencies, uv only considers lower bounds and ignores upper bounds entirely." |
| uv_build の `requires` の上限は残す（`uv init` の既定のまま） | uv docs: "Including an upper bound on the `uv_build` version ensures that your package continues to build correctly as new versions are released." |

---

## 5. 選び方・代替との比較

### 5.1 ビルドバックエンド

PEP 517 は、ビルドを 2 つの役に分ける: "A build frontend is a tool that users might run that takes arbitrary source trees or source distributions and builds wheels from them. The actual building is done by each source tree’s build backend." `uv build`・`python -m build`・pip がフロントエンドで、`[build-system]` の `requires` に書いた道具を入れ、`build-backend` に書いたものを呼ぶ。下の値は `uv init --lib --build-backend <名前>` が書いたものである（検証済み）。

| バックエンド | `requires` / `build-backend` | 選ぶ場面 |
|---|---|---|
| uv_build | `["uv_build>=0.13.7,<0.14.0"]` / `"uv_build"` | pure Python の新しいプロジェクト。0.7.19 で安定し、0.8.0 で `uv init --package` / `--lib` の既定、0.12.0 で素の `uv init` でも使われるようになった（uv の changelog） |
| hatchling | `["hatchling"]` / `"hatchling.build"` | build script や柔軟な配置が要る（uv docs の tip）。版をコードから読む（下） |
| setuptools | `["setuptools>=61"]` / `"setuptools.build_meta"` | `setup.py`・`setup.cfg` を持つ既存のプロジェクト。`license = "MIT"` の形は 77.0.3 から（PyPA のガイドの表。hatchling は 1.27.0、uv_build は 0.7.19） |
| maturin / scikit-build-core | — | Rust / C・C++・Fortran・Cython の拡張モジュール（uv docs）。uv_build は "only supports pure Python code" |

版をコードから読ませる（`dynamic = ["version"]`）なら hatchling を使う。`[tool.hatch.version]` の `path` に `__version__ = "0.3.0"` を書いたファイルを指すと、`uv build` は `demo_hatchling-0.3.0` を作った。ただし `uv version` は "We cannot get or set dynamic project versions" で失敗し、`--bump` も使えない（検証済み）。uv だけで回すなら、`version` を静的に書いて `uv version --bump` で上げる方が単純である。

### 5.2 extras と dependency groups

| | extras（`[project.optional-dependencies]`） | dependency groups（`[dependency-groups]`） |
|---|---|---|
| 配布物のメタデータ | 載る（`Provides-Extra`） | 載らない（PEP 735: "Build backends MUST NOT include Dependency Group data in built distributions as package metadata."） |
| 選ぶ人・選び方 | 利用者（`uv add "faq[yaml]"`） | 開発者（`uv sync --group lint`）。uv は既定で `dev` だけ入れる |
| パッケージ本体なしで入れられるか / 用途 | 入れられない / 任意の機能（YAML 対応・GUI など） | 入れられる（PEP 735: "installation of a Dependency Group does not imply installation of a package’s dependencies (or the package itself)"）/ テスト・リンター・ドキュメントの道具 |

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `uv add ./packages/faq-core` が "Added `packages/faq-core` to workspace members" と出し、`{ workspace = true }` になった（検証中に発生） | プロジェクトの中のディレクトリを足すと、uv は workspace のメンバーにする | path 依存にしたいなら `--no-workspace` を付けるか、外のディレクトリ（`../faq-core`）を指す |
| `pydantic^2.14` が "Expected one of `@`, `(`, `<`, `=`, `>`, `~`, `!`, `;`, found `^`" で失敗する。`pydantic~=2` も "The ~= operator requires at least two segments in the release version" で失敗する（検証で再現） | PEP 440 に `^` は無い。`~=` は仕様で "MUST NOT be used with a single segment version number" | `"pydantic>=2.14,<3"` と書くか、`uv add --bounds major pydantic` |
| `requires-python = ">=3.10"` で `uv lock` が失敗し、"Consider using a more restrictive `requires-python` value (like >=3.11)" と出る（検証で再現） | uv は `requires-python` の範囲のすべての版で依存を解決する。pandas 3.1 は Python 3.11 以上 | `requires-python` の下限を上げる |
| `uv build` が "License classifiers are ambiguous and deprecated per PEP 639" と警告する（検証で再現） | `license = "MIT"` と `License ::` の分類子を両方書いた。PEP 639 は、この場合ビルドの道具が失敗させてもよいとする（"MAY raise an error"） | 分類子を消す |
| `license = "MIT License"` で "`project.license` is not a valid SPDX expression" になる（検証で再現） | SPDX の識別子ではない | `"MIT"`・`"Apache-2.0"`・`"MIT OR Apache-2.0"` のように書く |
| uv_build で `dynamic = ["version"]` にすると、`uv build` が "missing field `version`" で失敗する（検証で再現） | uv 0.13.7 の uv_build は、`version` を静的に書く必要がある | `version` を書いて `uv version --bump` で上げるか、hatchling に替える（§5.1） |

---

## 出典

| 情報源 | URL |
|---|---|
| PyPA の仕様（pyproject.toml / Version specifiers / Dependency specifiers / Dependency Groups / Names and normalization / Well-known Project URLs / Core metadata） | https://packaging.python.org/en/latest/specifications/ 以下の `pyproject-toml/`・`version-specifiers/`・`dependency-specifiers/`・`dependency-groups/`・`name-normalization/`・`well-known-project-urls/`・`core-metadata/` （2026-11-08 確認、Context7 `/pypa/packaging.python.org` と原文） |
| Writing your pyproject.toml | https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ （2026-11-08 確認。表の形の `license` が非推奨、PEP 639 に対応したバックエンドの版） |
| PEP 440 / 508 / 517 / 518 / 621 / 639 / 735 | https://peps.python.org/pep-0440/ ・ https://peps.python.org/pep-0508/ ・ https://peps.python.org/pep-0517/ ・ https://peps.python.org/pep-0518/ ・ https://peps.python.org/pep-0621/ ・ https://peps.python.org/pep-0639/ ・ https://peps.python.org/pep-0735/ （2026-11-08 確認。いずれも Final） |
| uv docs（build backend / dependencies / resolution / init / package） | https://docs.astral.sh/uv/concepts/build-backend/ ・ https://docs.astral.sh/uv/concepts/projects/dependencies/ ・ https://docs.astral.sh/uv/concepts/resolution/ ・ https://docs.astral.sh/uv/concepts/projects/init/ ・ https://docs.astral.sh/uv/guides/package/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` と 0.13.7 の原文） |
| uv changelog 0.8.x / 0.10.x / 0.12.x | https://github.com/astral-sh/uv/tree/main/changelogs （2026-11-08 確認。uv_build の既定化、`--bounds` の安定化、`if-necessary`、TOML 1.0 の sdist） |
| Hatch — Versioning / PyPI classifiers | https://hatch.pypa.io/latest/version/ ・ https://pypi.org/classifiers/ （2026-11-08 確認。`[tool.hatch.version]` の `path`、`Private ::` の拒否） |
| package.json — npm Docs / node-semver | https://docs.npmjs.com/cli/v11/configuring-npm/package-json ・ https://github.com/npm/node-semver （2026-11-08 確認。`engines`・`optionalDependencies`・`peerDependencies`・`private`・`os`、`^` と `~` の定義。比較は semver 7.8.5 で実行） |

### 確認できなかった事項

- **uv_build が `dynamic` を受け付けないことの公式な記述**。uv 0.13.7 の docs には書かれていない。`missing field version` で失敗することを実測しただけである
- **`Private :: Do Not Upload` を付けたパッケージの、実際のアップロードの拒否**。PyPI の分類子のページの記述までで、アップロードは試していない

- 関連: [Python 学習ガイド](../README.md) / [Step 03: プロジェクト構成](../steps/03-project.md) / [Step 04: 型](../steps/04-typing.md) / [uv](uv.md) / [pip と venv](pip-venv.md) / [Step 11: 配布とデプロイ](../README.md#4-学習ロードマップ)
