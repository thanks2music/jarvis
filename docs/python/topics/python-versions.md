# Python の版 — 選び方・サポート期間・入れ方

> 出典（一次情報）:
> - [Status of Python versions (devguide.python.org)](https://devguide.python.org/versions/) — 版ごとの状態とサポート期間
> - [PEP 602 – Annual Release Cycle for Python](https://peps.python.org/pep-0602/) — 毎年 10 月のリリースと 5 年の保守
> - [Python versions (docs.astral.sh)](https://docs.astral.sh/uv/concepts/python-versions/) — `requires-python` と `.python-version`、`uv python upgrade`、free-threaded の選び方
> - [Python support for free threading (docs.python.org)](https://docs.python.org/3/howto/free-threading-python.html) — free-threaded ビルドの確かめ方と拡張モジュールの注意
> - [What's New In Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) / [3.14](https://docs.python.org/3/whatsnew/3.14.html) — 新機能
> - [nodejs/release (GitHub)](https://github.com/nodejs/release) — Node.js のリリーススケジュール（比較用）
>
> 最終更新: 2026-11-08（uv 0.13.7・Python 3.15.2 / 3.15.2 free-threaded / 3.14.10 / 3.13.18 で検証）

Node.js では、本番に LTS の版を選び、nvm などで切り替える。Python には LTS という区別が無く、**毎年 10 月に出る版が、どれも同じ 5 年間保守される**。
このページは、版の選び方、`requires-python` と `.python-version` の違い、Python の入れ方の比較、free-threaded ビルドを扱う。uv で Python を入れる手順は [Step 01](../steps/01-setup.md) を参照。

---

## 1. TL;DR

- **新しく始めるなら 3.15 か 3.14**。どちらも bugfix 期間にある。主要な依存が 3.15 の wheel を出しているかを、ビルドを禁じた dry-run で確かめてから決める（§4.1）。
- **LTS は無い**。どの版も bugfix 2 年 → security のみ → 5 年で EOL。3.11〜3.13 は security 期間、3.10 は 2026-10-01 に EOL になった（§3.1）。
- **`requires-python` は「対応する範囲」、`.python-version` は「手元で使う 1 つの版」**。lockfile は範囲全体に対して解決される。uv は範囲の外の版への pin を拒否する（§3.3）。
- **パッチ版は `uv python upgrade 3.15` で上げる**。その系列で作った仮想環境も新しいパッチ版に切り替わる（§4.2）。
- **free-threaded ビルド（GIL なし）は 3.14 から正式サポートだが、既定ではない**。`uv python install 3.15t` で試せる。C 拡張には `cp315t` か `abi3t` の wheel が要る（§4.3）。

---

## 2. Node.js / Bun との対応

| 項目 | Node.js（〜26） | Node.js（27〜） | Python |
|---|---|---|---|
| 新しい版が出る頻度 | 年 2 回（春に偶数、10 月に奇数） | 年 1 回 | 年 1 回（10 月。PEP 602） |
| 長く保守される版 | 偶数だけが LTS になる | すべての版が LTS になる | すべての版が同じ期間保守される |
| 1 つの版の期間 | 偶数で約 3 年（v26 は 2026-05-05 → 2029-04-30） | Alpha 6 か月 → Current 6 か月 → LTS 30 か月（v27 の EOL は 2030-04-30） | 5 年（bugfix 2 年 → security 3 年） |
| 対応する範囲の宣言 | `package.json` の `engines` | 同左 | `pyproject.toml` の `requires-python` |
| 範囲の外の版で動かすと | npm は既定で警告だけ（`engine-strict` で失敗） | 同左 | uv は失敗させる（§3.3） |
| 手元の版の固定 | `.nvmrc` / `.node-version` | 同左 | `.python-version` |
| ランタイムの更新 | バージョンマネージャで入れ直す。Bun は `bun upgrade` | 同左 | `uv python upgrade 3.15` |

> **ポイント**: Node.js は v27 から年 1 回のリリースに変わり、すべての版が LTS になる（README: "every release line is promoted to LTS"）。「偶数を選ぶ」のは v26 までの習慣である。Python は以前から年 1 回で、版の違いは「いつ出たか」だけである。

---

## 3. 早見表（コマンド・設定）

### 3.1 版とサポート期間（2026-11-08 時点）

| 版 | 状態 | 初回リリース | EOL（予定） | 最新のパッチ版 |
|---|---|---|---|---|
| 3.16 | feature（開発中。uv の一覧に 3.16.0a1 がある） | 2027-10-06 予定 | 2032-10 | — |
| 3.15 | bugfix | 2026-10-09 | 2031-10 | 3.15.2 |
| 3.14 | bugfix | 2025-10-07 | 2030-10 | 3.14.10 |
| 3.13 / 3.12 / 3.11 | security | 2024-10-07 / 2023-10-02 / 2022-10-24 | 2029-10 / 2028-10 / 2027-10 | 3.13.18 / 3.12.16 / 3.11.18 |
| 3.10 / 3.9 | end-of-life | 2021-10-04 / 2020-10-05 | 2026-10-01 / 2025-10-31 | — |

devguide の原文: bugfix 期間は "New binaries are built and released roughly every two months."、その後は "After two years (18 months for versions before 3.13), only security fixes are accepted and no more binaries are released."、最後に "Five years after a release, support ends."

> **注意**: security 期間の版は、python.org がソースしか配布しない。3.12.16 の配布物は "Gzipped source tarball" と "XZ compressed source tarball" の 2 つだけだった（python.org の downloads API）。uv は `cpython-3.12.16-macos-aarch64-none` のビルド済みを配布している（検証済み）。

### 3.2 uv のコマンド

| コマンド | 何をするか |
|---|---|
| `uv python install 3.15` / `uv python install 3.15t` | GIL ありのビルド / free-threaded ビルドを入れる（GIL ありに限るなら `3.15+gil`） |
| `uv python pin 3.15` | `.python-version` に書く（`requires-python` の範囲の外なら失敗する） |
| `uv python upgrade 3.15` | 3.15 の最新のパッチ版に上げる（マイナー版は上げない） |

### 3.3 `requires-python` と `.python-version`

| | `requires-python`（`pyproject.toml`） | `.python-version` |
|---|---|---|
| 意味 | 対応する版の範囲（`>=3.14`） | 仮想環境を作るときの 1 つの版（`3.14`） |
| lockfile への効き方 | 範囲**全体**で動く依存の版を選ぶ（universal resolution）。`uv.lock` の先頭に写される | 効かない |
| 公開したとき | `Requires-Python` メタデータになり、インストーラが入れる版を選ぶ手がかりにする | 配布物には入らない |
| 読む道具 | uv（プロジェクトの操作） | uv・pyenv。asdf と mise は設定で有効にしたとき（§5） |

`uv init` は両方を書く。`requires-python = ">=3.15"` のプロジェクトでは、範囲の外の版は pin も実行も拒否される（検証済み）。

実行結果:

```text
$ uv python pin 3.14
error: The requested Python version `3.14` is incompatible with the project `requires-python` value of `>=3.15`.
$ uv run --python 3.14 python -V
Using CPython 3.14.10
error: The requested interpreter resolved to Python 3.14.10, which is incompatible with the project's Python requirement: `>=3.15` (from `project.requires-python`)
```

試すなら作業中の `faq-app/` ではなくコピーで行う。下限を `">=3.14"` に下げると pin が通り（`` Updated `.python-version` from `3.15` -> `3.14` ``）、`uv run` は 3.14.10 で仮想環境を作り直し、`uv.lock` の先頭も `requires-python = ">=3.14"` に変わった（検証済み）。ただし公式 docs のとおり "the project's `requires-python` must be a subset of the `requires-python` of all its dependencies." なので、下限を下げるほど選べる依存の版は減る。

---

## 4. 推奨の使い方（2026-11）

### 4.1 新しいプロジェクトの版を決める

**3.15 を第一の候補にし**（bugfix 期間にあり、EOL が 2031-10 で最も遅い）、C 拡張を含む主要な依存が 3.15 の wheel を出しているかを確かめる。wheel が無いとソース配布物（sdist）からのビルドになり、コンパイラなどが要る。足りなければ 3.14（EOL 2030-10）にする。
確かめるには、`uv venv --python 3.15 venv315` で仮想環境を作り、`--only-binary :all:`（ビルドを禁じる）で dry-run する。wheel が足りなければ失敗する（検証済み）。

実行結果:

```text
$ uv pip install --python venv315 --dry-run --only-binary :all: numpy pydantic-core orjson polars
Using Python 3.15.2 environment at: venv315
…（中略: 3 行）…
 + numpy==2.5.4
 + orjson==3.13.0
 + polars==2.1.0
…（中略: 3 行）…
```

wheel のファイル名にある Python タグと ABI タグ（PyPI の "Download files" や JSON API で見られる）でも分かる。

| タグ（例） | 使える Python |
|---|---|
| `cp315-cp315` / `cp315-cp315t` | CPython 3.15 の GIL ありだけ / free-threaded だけ（numpy 2.5.4 は両方を出している。検証済み） |
| `cp311-abi3` | Stable ABI。3.11 以降の GIL ありのビルド（原文 "An extension compiled for Stable ABI 3.x is ABI-compatible with Python 3.x and above."）。polars-runtime-32 2.1.0 の macOS arm64 はこれだけだった（検証済み） |
| `abi3t` / `py3-none-any` | 3.15 で入った free-threaded 用の Stable ABI（PEP 803） / 純 Python で、どの Python 3 でも使える |

### 4.2 パッチ版を上げる

`uv python install 3.13.17` で古いパッチ版を入れ、`uv venv --python 3.13 venv313` で仮想環境を作ってから上げる（検証済み）。

実行結果:

```text
$ venv313/bin/python -V
Python 3.13.17
$ uv python upgrade 3.13
…（中略: 3 行）…
 + cpython-3.13.18-macos-aarch64-none (python3.13)
$ venv313/bin/python -V
Python 3.13.18
```

- 仮想環境まで上がるのは、uv が `cpython-3.13-macos-aarch64-none` という**マイナー版のディレクトリ**（実体へのシンボリックリンク）を挟むためである。古い 3.13.17 は消えずに残る。すでに最新なら、`uv python upgrade 3.15` は `Python 3.15 is already on the latest supported patch release` と出すだけである（検証済み）
- `uv venv -p 3.10.8` のようにパッチ版まで指定した仮想環境は上がらない。マイナー版をまたぐ更新（3.14 → 3.15）もしない（公式 docs: "changing minor versions can affect dependency resolution"）。`uv python upgrade` は uv 0.10 で安定版になった

### 4.3 free-threaded ビルドは、必要なときだけ使う

| 版 | 状態 |
|---|---|
| 3.13 | 初めて入った（PEP 703）。experimental の扱い（PEP 779 の "Phase I"） |
| 3.14 | 正式にサポートされた（PEP 779 の "Phase II"）。任意であり、既定は GIL ありのまま。既定にする "Phase III" は "That's left for a future PEP." |
| 3.15 | free-threaded 用の Stable ABI `abi3t` が入った（PEP 803）。python.org の macOS インストーラは `python3.15t` も既定で入れる |

`uv python install 3.15t` で入れると `python3.15t` というコマンドができる。GIL ありのビルドと比べる（検証済み）。

実行結果:

```text
$ uv run --no-project --python 3.15 python -c "import sys; print(sys.version); print(sys._is_gil_enabled())"
3.15.2 (main, Oct 26 2026, 13:59:33) [Clang 23.1.3 ]
True
$ uv run --no-project --python 3.15t python -c "import sys; print(sys.version); print(sys._is_gil_enabled())"
3.15.2 free-threading build (main, Oct 26 2026, 13:59:30) [Clang 23.1.3 ]
False
```

- `sys._is_gil_enabled()` は「いま GIL が効いているか」を返す。ビルドの種類は、公式 docs が推奨する `sysconfig.get_config_var("Py_GIL_DISABLED")` で見る（free-threaded では `1`。検証済み）
- C 拡張には `cp315t` か `abi3t` の wheel が要り、`abi3` の wheel は使えない。§4.1 の polars（polars-runtime-32）は `cp311-abi3` しか無いので 3.15t には入らなかった（§6）
- free-threading への対応を明示していない C 拡張を import すると、GIL が有効に戻り、警告が出る（公式 docs）

> **ポイント**: 依存が対応しきっておらず、単一スレッドの処理にも上乗せがある（公式 docs の pyperformance の平均で macOS aarch64 は約 1%、x86-64 Linux は約 8%。参考値）。そのため、CPU を使う処理をスレッドで並べたい場合（Node.js なら worker_threads を使う場面）に限って検討する。並行処理は [Step 08: 非同期と並行処理](../README.md#4-学習ロードマップ) で扱う。

### 4.4 3.14 と 3.15 の主な新機能

| 版 | What's New の "Release highlights" から抜粋 |
|---|---|
| 3.14 | テンプレート文字列 `t"..."`（PEP 750）、注釈の遅延評価（PEP 649・749）、標準ライブラリのサブインタプリタ（PEP 734）、`compression.zstd`（PEP 784）、括弧なしの `except A, B:`（PEP 758）、free-threaded の正式サポート（PEP 779） |
| 3.15 | `lazy import`（PEP 810）、組み込みの `frozendict`（PEP 814）と `sentinel`（PEP 661）、既定のエンコーディングが UTF-8（PEP 686。`sys.flags.utf8_mode` が 3.15 で `1`、3.14 で `0` だった）、内包表記での `*` / `**` の展開（PEP 798）、`profiling` パッケージ（PEP 799）、`TypedDict` の extra items（PEP 728）、`TypeForm`（PEP 747） |

---

## 5. 選び方・代替との比較（Python の入れ方）

| 入れ方 | 中身 | 版の固定 | 注意 |
|---|---|---|---|
| **uv**（本ガイドの既定） | Astral の python-build-standalone のビルド済み | `.python-version` と `requires-python` を読む | 可搬性のための癖がある（公式 docs が "quirks" の文書を案内している） |
| python.org のインストーラ | macOS は `/Library/Frameworks/Python.framework` に入れ、`/usr/local/bin` にリンクを置く | 版ごとに入れる | security 期間の版は出ない（§3.1）。Windows は Python install manager（`py install 3.15t`）を案内し、従来のインストーラは 3.14 で非推奨、3.16 からは作られない |
| Homebrew | `python3` は Homebrew の既定の formula を指す（手元では 3.15.2） | 既定の版は上流のリリースに合わせて変わる | PEP 668 の externally managed の印が付く。依存は venv に、コマンドは pipx で入れるよう案内している（[pip と venv](pip-venv.md)） |
| pyenv / asdf（asdf-python） | ほとんどの版をソースからビルドする（asdf-python も pyenv の python-build を使う）。ビルド依存が要る | pyenv は `.python-version`。asdf は `.tool-versions` で、`.python-version` は `legacy_version_file = yes` のときだけ | pyenv は Windows を公式には非対応（pyenv-win を案内している） |
| mise | 既定で python-build-standalone のビルド済み（`python.compile` でソースからも） | `.python-version` は `idiomatic_version_file_enable_tools` で有効にしたときだけ | free-threaded は既定では選ばない |
| macOS の `/usr/bin/python3` | Xcode / Command Line Tools 用に Apple が入れたもの | — | 3.9.6 で EOL（検証済み: `/usr/bin/python3 -V` → `Python 3.9.6`）。公式 docs: "You should never modify or attempt to delete this installation" |

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `uv python pin` したのに、`uv run` が別の版を使う（検証中に発生） | `--no-config`（`UV_NO_CONFIG=1`）は `.python-version` も読まなくする。`uv run -v` に ``Ignoring Python version file at `.python-version` due to `--no-config` `` と出る | `--no-config` を外す |
| `uv python pin 3.14` が `incompatible with the project requires-python` で失敗する（検証中に発生） | `.python-version` は `requires-python` の範囲の中でしか選べない | 先に `requires-python` の下限を下げる。lockfile の解決も変わる（§3.3） |
| 3.15t で `has no usable wheels` と出て入らない（検証中に発生） | そのパッケージに `cp315t` / `abi3t` の wheel が無い。2026-11-08 時点で orjson・polars・psycopg-binary・duckdb が該当した（numpy・pandas・pydantic-core などは入った） | GIL ありの 3.15 を使う |
| free-threaded なのに `sys._is_gil_enabled()` が `True` | 対応を明示していない C 拡張を import して GIL が戻った。`-X gil=1` や `PYTHON_GIL=1` でも戻る（`-X gil=1` は検証済み） | 警告に出たモジュールの対応状況を確かめる |
| 3.15 の GIL ありを入れたのに free-threaded が使われる | 3.14 以降は、PATH で先に見つかった free-threaded の Python を uv が使うことがある（公式 docs） | `3.15+gil` と指定する（`uv python find 3.15+gil` で確かめられる） |
| `uv python upgrade` の後も仮想環境が古いパッチ版のまま | パッチ版まで指定して作った（`-p 3.13.17`）か、別のツールがシンボリックリンクを解決して作った | マイナー版（`3.13`）を指定して作り直す |

---

## 出典

| 情報源 | URL |
|---|---|
| Status of Python versions / PEP 602 / PEP 779（PEP 703・779・803 はすべて Final） | https://devguide.python.org/versions/ ・ https://peps.python.org/pep-0602/ ・ https://peps.python.org/pep-0779/ ・ https://peps.python.org/api/peps.json （2026-11-08 確認） |
| uv — Python versions / Resolution / 0.10.x changelog | https://docs.astral.sh/uv/concepts/python-versions/ ・ https://docs.astral.sh/uv/concepts/resolution/ ・ https://github.com/astral-sh/uv/blob/main/changelogs/0.10.x.md （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由） |
| Python support for free threading / C API Extension Support for Free Threading / C API Stability（abi3・abi3t） | https://docs.python.org/3/howto/free-threading-python.html ・ https://docs.python.org/3/howto/free-threading-extensions.html ・ https://docs.python.org/3/c-api/stable.html （2026-11-08 確認） |
| What's New In Python 3.15 / 3.14、Using Python on macOS / Windows | https://docs.python.org/3/whatsnew/3.15.html ・ https://docs.python.org/3/whatsnew/3.14.html ・ https://docs.python.org/3/using/mac.html ・ https://docs.python.org/3/using/windows.html （2026-11-08 確認） |
| pyproject.toml / Core metadata（`Requires-Python`） | https://packaging.python.org/en/latest/specifications/pyproject-toml/ ・ https://packaging.python.org/en/latest/specifications/core-metadata/ （2026-11-08 確認） |
| PyPI JSON API / python.org downloads API | https://pypi.org/pypi/numpy/2.5.4/json ・ https://www.python.org/api/v2/downloads/release_file/?release=1168 （2026-11-08 確認） |
| Homebrew — Language Runtimes and Packages | https://docs.brew.sh/Language-Runtimes-and-Packages （2026-11-08 確認） |
| pyenv / asdf-python / asdf configuration / mise | https://github.com/pyenv/pyenv ・ https://github.com/asdf-community/asdf-python ・ https://asdf-vm.com/manage/configuration.html ・ https://mise.jdx.dev/lang/python.html （2026-11-08 確認） |
| nodejs/release / Node.js Releases / npm の `engines` | https://github.com/nodejs/release ・ https://nodejs.org/en/about/previous-releases ・ https://docs.npmjs.com/cli/v11/configuring-npm/package-json#engines （2026-11-08 確認）。Bun は手元の `bun --help`（1.4.4） |

### 確認できなかった事項

- **free-threaded 対応の全体像**。3.15t の wheel を確かめたのは 14 パッケージ（numpy・pandas・pydantic-core・orjson・polars・uvloop・granian・msgspec・asyncpg・psycopg-binary・lxml・pillow・cryptography・duckdb）だけである。公式の対応一覧は探していない
- **GIL が戻るときの警告の実物**。対応を明示していない C 拡張を 3.15t で import する実験はしていない。§4.3・§6 の記述は公式 docs による

- 関連: [Python 学習ガイド](../README.md) / [Step 01: 環境構築](../steps/01-setup.md) / [uv](uv.md) / [pyproject.toml](pyproject-toml.md) / [pip と venv](pip-venv.md)
