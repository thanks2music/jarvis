# Step 01: 環境構築 — uv で Python を入れ、最初のスクリプトを動かす

> 出典（一次情報）:
> - [Installing uv (docs.astral.sh)](https://docs.astral.sh/uv/getting-started/installation/) — uv の入れ方と更新の仕方
> - [Python versions (docs.astral.sh)](https://docs.astral.sh/uv/concepts/python-versions/) — uv が Python を入れる・探す仕組みと `python-preference`
> - [Tools (docs.astral.sh)](https://docs.astral.sh/uv/concepts/tools/) — `uvx` が使い捨ての環境でツールを動かすこと
> - [Status of Python versions (devguide.python.org)](https://devguide.python.org/versions/) — 版ごとのサポート期間
>
> 最終更新: 2026-11-08（uv 0.13.7・Python 3.15.2 で検証）

Node.js では、ランタイムの版を nvm や fnm・Volta・mise で切り替え、パッケージを npm や pnpm で入れる。Bun は 1 つのバイナリがランタイムとパッケージ管理を兼ねる。
Python では **uv** がその両方を受け持つ。Python 本体を入れ、版を固定し、スクリプトを動かし、ツールを一度だけ実行するところまで、uv のコマンドで済む。
このステップでは、通し課題の社内 FAQ（12 件の JSONL）を読み込んで件数を数える、1 ファイルのスクリプトを動かす。
シリーズ全体の地図は [Python 学習ガイド](../README.md) を、次は [Step 02: 文法の差分](02-language.md) を参照。

---

## 1. TL;DR

- **Python 本体も uv で入れる**。`uv python install 3.15` でダウンロードし、`uv python pin 3.15` で版を `.python-version` に書く。以降の `uv run` はこの版を使う（§3.2・§3.3）。
- **新しく始めるなら 3.15 か 3.14**。どちらも bugfix 期間（2 か月ごとにバグ修正版が出る）にある。3.15 で動かないライブラリに出会ったら 3.14 にする（§4）。
- **`uv run app.py` が `node app.js` / `bun app.ts` にあたる**。プロジェクトの外では仮想環境を作らず、選んだ Python でそのまま実行する（§3.5）。
- **`uvx` が `npx` / `bunx` にあたる**。ツールを使い捨ての環境に入れて一度だけ動かす（§3.7）。
- macOS に最初から入っている `/usr/bin/python3` は 3.9 で、2025-10-31 にサポートが終わっている。使わない（§5）。

---

## 2. Node.js / Bun との対応

| やりたいこと | Node.js | Bun | Python（uv） |
|---|---|---|---|
| ランタイムを入れる | 公式インストーラ / nvm / fnm / Volta / mise | 公式のインストーラ（Bun 本体がランタイム） | `uv python install 3.15` |
| プロジェクトの版を固定する | `.nvmrc` / `.node-version` / `engines` | — | `.python-version`（`uv python pin 3.15`） |
| 1 ファイルを実行する | `node app.js` | `bun app.ts` | `uv run app.py` |
| 対話モード（REPL） | `node` | `bun repl` | `uv run python` |
| ツールを一度だけ動かす | `npx <pkg>` | `bunx <pkg>` | `uvx <pkg>` |
| どのランタイムで動くか確かめる | `which node` / `process.execPath` | `which bun` / `process.execPath` | `uv python find` / `sys.executable` |

> **ポイント**: Python にはビルドの工程が無い。TypeScript のように型を消してから実行する必要はなく、`.py` ファイルをそのまま実行する。型ヒントは実行時には検査されない（[Step 04](04-typing.md) で扱う）。

---

## 3. ハンズオン

作業ディレクトリを `faq-app/` とし、以降のステップもここで育てる。

### 3.1 uv を入れる

公式の手順は 2 通りある（公式 docs 準拠・未実行: 手元には Homebrew で導入済みのため）。

```bash
# 公式のインストーラ（macOS / Linux）
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew
brew install uv
```

入ったかを確かめる（検証済み）。

実行結果:

```text
$ uv --version
uv 0.13.7 (Homebrew 2026-11-03 aarch64-apple-darwin)
```

uv の更新は、公式のインストーラで入れた場合は `uv self update`、Homebrew で入れた場合は `brew upgrade uv` で行う。

### 3.2 Python を入れる

uv で Python 3.15 を入れる（検証済み）。

実行結果:

```text
$ uv python install 3.15
Downloading cpython-3.15.2-macos-aarch64-none (download) (26.5MiB)
 Downloaded cpython-3.15.2-macos-aarch64-none (download)
Installed Python 3.15.2 in 1.07s
 + cpython-3.15.2-macos-aarch64-none (python3.15)
```

- `3.15` と書くと、その系列の最新（ここでは 3.15.2）が入る。入れた本体は `~/.local/share/uv/python` に置かれる
- 末尾の `(python3.15)` は、`~/.local/bin` に `python3.15` というコマンドを置いたことを表す（uv 0.8.0 からの既定。止めるなら `--no-bin`）
- `uv python list --only-installed` で、uv が見つけた Python を一覧できる。uv が入れたものに加えて、Homebrew・asdf・macOS 付属の Python も並ぶ

> **注意**: 本ガイドの検証では、手元の環境を汚さないように、uv の Python とツールの置き場所を作業用のディレクトリに切り替えた（`UV_PYTHON_INSTALL_DIR` など）。実行結果に出るパスは、既定の置き場所（`~/.local/share/uv/python`・`~/.local/bin`）と、読者の作業ディレクトリ（`~/faq-app`）に読み替えて載せている。

### 3.3 プロジェクトの版を固定する

作業ディレクトリを作り、Python の版を固定する（検証済み）。

```bash
mkdir faq-app && cd faq-app
uv python pin 3.15
```

実行結果:

```text
$ uv python pin 3.15
Pinned `.python-version` to `3.15`
$ cat .python-version
3.15
$ uv run python -V
Python 3.15.2
```

`.python-version` は `.nvmrc` にあたる。uv はこのファイルを読み、書かれた版の Python を選ぶ（無ければダウンロードする）。pyenv も同じ名前のファイルを読む。`-v` を付けると、読んだことが分かる（検証済み）。

実行結果:

```text
$ uv run -v python -V 2>&1 | grep -iE "python version file|python-version|Using|Python 3"
DEBUG Reading Python requests from version file at `~/faq-app/.python-version`
DEBUG Searching for Python 3.15 in virtual environments, managed installations, or search path
DEBUG Using Python 3.15.2 interpreter at: ~/.local/share/uv/python/cpython-3.15-macos-aarch64-none/bin/python3.15
Python 3.15.2
```

### 3.4 通し課題のデータを置く

シリーズ共通のデータ（架空の社内 FAQ・12 件）を `data/faq.jsonl` として保存する。中身は [AI フレームワーク学習ガイドの §7.4](../../ai-frameworks/README.md#74-通し課題のデータ架空の社内-faq) にある 12 行をそのまま使う。1 行に 1 件、`id`・`category`・`question`・`answer` を持つ JSON である。

```bash
mkdir data
# エディタで data/faq.jsonl を作り、§7.4 の 12 行を貼り付ける
```

### 3.5 最初のスクリプトを動かす

`count.py` を作り、FAQ を読み込んで件数を数える（検証済み）。

```python
import json
from pathlib import Path

text = Path("data/faq.jsonl").read_text(encoding="utf-8")
faqs = [json.loads(line) for line in text.splitlines() if line.strip()]

print(f"{len(faqs)} 件の FAQ を読み込んだ")
print("最初の質問:", faqs[0]["question"])
```

実行結果:

```text
$ uv run count.py
12 件の FAQ を読み込んだ
最初の質問: 経費精算の締め日はいつですか？
```

- `import json` と `from pathlib import Path` は、どちらも標準ライブラリである。Node の `node:fs` や `node:path` と同じく、追加のインストールは要らない
- `[... for line in ... if ...]` は**内包表記**で、`text.split("\n").filter(...).map(...)` を 1 つの式で書く（[Step 02](02-language.md) で扱う）
- `f"..."` は **f-string** で、JS のテンプレートリテラル `` `${len}` `` にあたる
- このディレクトリにはまだ `pyproject.toml` が無いので、uv は仮想環境を作らず、`.python-version` の版の Python でそのまま実行する。依存を入れるプロジェクトにするのは [Step 03](03-project.md) である

### 3.6 どの Python で動いたかを確かめる

実行に使われた Python を確かめる（検証済み）。

実行結果:

```text
$ uv run python -c "import sys; print(sys.executable)"
~/.local/share/uv/python/cpython-3.15-macos-aarch64-none/bin/python3.15
```

uv が理由まで含めて教えてくれる `-v` も覚えておく（検証済み）。

実行結果:

```text
$ uv python find -v 2>&1 | grep -E "Found|Skipping"
DEBUG Found managed installation `cpython-3.15.2-macos-aarch64-none`
DEBUG Found `cpython-3.15.2-macos-aarch64-none` at `~/.local/share/uv/python/cpython-3.15-macos-aarch64-none/bin/python3.15` (managed installations)
```

> **ポイント**: uv の `python-preference` の既定は `managed` で、**uv が入れた Python を、システムにある Python より優先する**（ただし、ダウンロードするよりは手元にあるシステムの Python を使う）。思った版で動かないときは、まず `uv python find -v` を見る（§5）。

### 3.7 `uvx` でツールを一度だけ動かす

Ruff（Python の linter と formatter。[Step 05: 品質ツール](../README.md#4-学習ロードマップ) で扱う）を、インストールせずに一度だけ動かす（検証済み）。

実行結果:

```text
$ uvx ruff@0.17.4 --version
ruff 0.17.4
```

- `uvx` は `uv tool run` の別名である。ツールを使い捨ての環境に入れて実行し、その環境は uv のキャッシュに残すだけで、プロジェクトには何も足さない
- `@0.17.4` で版を固定できる。`npx ruff@0.17.4` と同じ感覚で使える
- ただし、**プロジェクトの依存を読み込む道具（pytest や mypy など）は `uvx` ではなく `uv run` で動かす**。公式 docs も "If the tool should not be isolated from the project, e.g., when running `pytest` or `mypy`, then `uv run` should be used instead of `uv tool run`." と書いている

### 3.8 対話モード（REPL）

`uv run python` で対話モードに入る（抜粋・単体では動かない）。

```text
$ uv run python
>>> 0.1 + 0.2
0.30000000000000004
>>> exit
```

Python 3.13 から、色付きの表示と複数行の編集ができる新しい対話モードが既定になった。`exit` や `help` は、関数として呼ばなくてもそのまま打てば効く。

---

## 4. ベストプラクティス

| 推奨 | 避ける | 理由 |
|---|---|---|
| Python 本体を `uv python install` で入れ、`.python-version` で固定する | プロジェクトごとに「たまたま PATH にあった `python3`」で動かす | 版がそろわないと、依存の解決結果も変わる。uv は既定で自分が入れた Python を優先する |
| 新しいプロジェクトは 3.15 か 3.14 で始める | 3.10 以前で始める | 3.10 は 2026-10-01 にサポートが終わった。3.11〜3.13 はセキュリティ修正だけの期間にある（[サポート期間](https://devguide.python.org/versions/)） |
| ツールの一度きりの実行は `uvx`、プロジェクトの依存を読む道具は `uv run` | `pip install` で道具をグローバルに入れる | グローバルに入れると、別のプロジェクトの依存とぶつかる（[pip と venv](../topics/pip-venv.md)） |
| uv 自体を定期的に更新する | 古い uv のまま新しい Python を使う | 新しい Python の対応（例: 3.15）は uv の新しい版で入る |

版の選び方の詳細は [Python の版の選び方](../topics/python-versions.md)、uv のコマンドの一覧は [uv](../topics/uv.md) を参照。

---

## 5. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `uv python list` の先頭に `Failed to inspect Python interpreter ... ~/.asdf/shims/python3.10` という警告が並ぶ（検証中に発生） | asdf の shim は、そのディレクトリで版が決まっていないと終了コード 126 を返す。uv は PATH 上の Python を 1 つずつ問い合わせるため、警告になる | 警告であり、一覧と実行には影響しない。気になる場合は、uv に任せる版の asdf の設定を外す |
| uv で入れたのに、`uv run python` が asdf や Homebrew の Python を使う（検証中に発生） | ユーザー設定 `~/.config/uv/uv.toml` に `python-preference = "system"` がある。`uv python find -v` に `Skipping managed installation ...: system installation preferred` と出る | 設定を見直す。`--no-config`（環境変数 `UV_NO_CONFIG=1`）は設定ファイルと一緒に `.python-version` の読み込みも止める（公式 docs: "Discovery of `.python-version` files can be disabled with `--no-config`."）ので、版の確認には向かない |
| `python` コマンドが無い。`python3 -V` が `Python 3.9.6` | macOS 付属の `/usr/bin/python3` が使われている | `uv run python` を使う。どうしても `python` という名前が要るなら `uv python install --default`（experimental） |
| `uv python install` の後に `~/.local/bin` が PATH に無いと警告される | シェルの設定に `~/.local/bin` が入っていない | `uv python update-shell` を実行して、シェルを開き直す |
| `uv run count.py` が `FileNotFoundError: data/faq.jsonl` で落ちる | 相対パスは、スクリプトの場所ではなく**実行したディレクトリ**を基準にする（Node の `process.cwd()` と同じ） | `faq-app/` で実行する。スクリプトの場所を基準にするなら `Path(__file__).parent / "data/faq.jsonl"` と書く |

---

## 6. 次のステップ

- [Step 02: 文法の差分](02-language.md) — JS / TS と違うところ・罠を、FAQ のカテゴリ集計を書きながら押さえる
- 先に道具を知りたい場合は [uv](../topics/uv.md) と [Python の版の選び方](../topics/python-versions.md)

---

## 出典

| 情報源 | URL |
|---|---|
| Installing uv | https://docs.astral.sh/uv/getting-started/installation/ （2026-11-08 確認、Context7 `/astral-sh/uv/0.13.5` 経由） |
| Python versions — uv | https://docs.astral.sh/uv/concepts/python-versions/ （2026-11-08 確認。`python-preference` の既定、探索の順番） |
| uv 0.8.0 changelog | https://github.com/astral-sh/uv/blob/main/changelogs/0.8.x.md （2026-11-08 確認。`~/.local/bin` に Python を置く既定と `--no-bin`） |
| Tools — uv | https://docs.astral.sh/uv/concepts/tools/ （2026-11-08 確認。`uvx` と `uv run` の使い分け） |
| Status of Python versions | https://devguide.python.org/versions/ （2026-11-08 確認） |
| What's New In Python 3.13 | https://docs.python.org/3/whatsnew/3.13.html （2026-11-08 確認。新しい対話モード） |

### 確認できなかった事項

- **asdf の shim が出す警告の扱い**。uv 側に、問い合わせに失敗した PATH 上の Python を黙って飛ばす設定があるかは、公式 docs で見つけられなかった。警告は実行に影響しなかったという観測だけを載せた

- 関連: [Python 学習ガイド](../README.md) / [uv](../topics/uv.md) / [Python の版の選び方](../topics/python-versions.md) / [pip と venv](../topics/pip-venv.md)
