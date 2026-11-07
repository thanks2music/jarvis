# TensorFlow 入門 — 既存の資産を読み・動かし・移行を判断する

> 出典（一次情報）:
> - [What's new in TensorFlow 2.21 (developers.googleblog.com)](https://developers.googleblog.com/whats-new-in-tensorflow-221/) — 2026-03-06。今後の保守方針と、TF Lite から LiteRT への改名
> - [TensorFlow Releases (github.com)](https://github.com/tensorflow/tensorflow/releases) — v2.21.0・v2.22.0-rc0 の変更点と、v2.16.1 の Keras 3 既定化
> - [Migrating Keras 2 code to multi-backend Keras 3 (keras.io)](https://keras.io/guides/migrating_to_keras_3/) / [Using the SavedModel format (tensorflow.org)](https://www.tensorflow.org/guide/saved_model) — Keras 3 での SavedModel の扱いと `saved_model_cli`
>
> 最終更新: 2026-11-08（TensorFlow 2.21.0 で検証。★と最新版は 2026-11-08 時点）

TensorFlow は Google の深層学習フレームワークで、SavedModel・TF Serving・TF Lite（現 LiteRT）を中心に、本番で動いている資産が多い。本ドキュメントは新規開発の入門ではなく、**既存の TensorFlow 資産に出会ったときに、読める・動かせる・移行を判断できる**ことに絞る。学習ループの基本は [PyTorch 入門](pytorch.md) で扱った。シリーズ全体の地図は [AI フレームワーク学習ガイド](README.md) を参照。

---

## 1. TL;DR

- **TensorFlow は 2026-03 から保守中心になった**。Google は 2.21 の発表で、今後は「セキュリティ脆弱性と重大なバグへの迅速な対応」「依存の更新（新しい Python など）のための minor リリース」「コミュニティからの重大なバグ修正の受け入れ」に専念すると書いた。対象は tf.data・TF Serving・TFX・TensorBoard などのエコシステム全体である
- 同じ発表は本番での安定性は続けるとしつつ、**新規の生成 AI 開発には Keras 3 / JAX / PyTorch を勧めている**。TF Lite は **LiteRT** に改名され、別に開発が続く。Hugging Face Transformers も v5 で TensorFlow 対応を外した。一方でリリースは続き、2026-09-24 の v2.22.0-rc0 で Python 3.14 と CUDA 13 への初期対応が入った
- **TF 2.16 以降の `tf.keras` は Keras 3** である。Keras 2 時代の `model.save("dir")` や `load_model("<SavedModel>")` は動かない（§6.2 のチェックリスト）
- 既存の SavedModel は `saved_model_cli` で入出力を確かめ、`tf.saved_model.load` で推論できる。LiteRT に変換しても予測は 360 件すべて一致した（§5.2・§5.3）。Mac には公式の GPU 対応がなく、tensorflow-metal 1.2.0 を入れると `import tensorflow` 自体が失敗した（§4.3）

---

## 2. 前提知識

- **Python と NumPy の基本**。学習ループ（予測 → 誤差 → 勾配 → 更新）の考え方は [PyTorch 入門](pytorch.md) の §5.3 で扱った。Keras ではこれを `fit()` が中で回す
- **SavedModel** は「計算のグラフ・重み・入口（signature）」をまとめたディレクトリで、TensorFlow の資産の標準形である。モデルを定義した Python のコードがなくても推論できる。テンソル・バッチ・量子化などの用語は、索引の [用語集](README.md#61-基礎学習) にまとめた

---

## 3. 位置づけと比較

| フレームワーク | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **TensorFlow** | SavedModel を軸に、配信（TF Serving）・端末（LiteRT）・パイプライン（TFX）までそろう | 2026-03 から保守中心。Mac の GPU は公式には使えない | 既存の SavedModel・TF Serving・LiteRT の資産を保守する |
| [Keras 3](keras.md)（移行先） | 同じコードを JAX / PyTorch / TensorFlow のどれでも動かせる。TF 2.16 以降の `tf.keras` の中身 | Keras 2 の保存・読み込みの書き方の一部が動かない（§6.2） | `tf.keras` のコードを生かしつつ、TensorFlow への依存を減らす |
| [PyTorch](pytorch.md) | LLM 周辺の主要な OSS が前提にしている。Transformers v5 は PyTorch だけをバックエンドにした | SavedModel・TF Serving の資産はそのままでは使えない | 生成 AI を含む新規開発 |
| [JAX](jax.md) | 関数変換（`jit` / `grad` / `vmap`）と TPU。Keras 3 のバックエンドにもなる | 関数型の書き方に慣れが要る | TPU で学習する、Google 系の研究コードを読む |
| ONNX Runtime | ONNX に変換したモデルを、学習したフレームワークと切り離して配信できる。TensorFlow からは tf2onnx で変換する | 変換できるか、結果が一致するかをモデルごとに確かめる必要がある | 配信だけを TensorFlow から切り離したい |

---

## 4. セットアップ

### 4.1 検証環境

検証環境の全体は索引の [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。本ドキュメント固有の版は次のとおり。

| 項目 | 版 |
|---|---|
| tensorflow / keras / ai-edge-litert | 2.21.0 / 3.15.1（tensorflow の依存として入る） / 2.3.0（LiteRT の Python ランタイム） |
| numpy / scikit-learn | 2.5.4 / 1.9.1 |
| Python | 3.12.16（uv で管理） |

### 4.2 インストール

Python を 3.12 に固定して入れる。TF 2.21.0 の wheel は Python 3.10〜3.13 向けだけである（PyPI で確認）。検証では同じ手順を共通スクリプトで実行した（検証済み）。
```bash
uv init --bare --python 3.12 tf-hello && cd tf-hello
uv python pin 3.12
uv add "tensorflow==2.21.0" "ai-edge-litert==2.3.0" scikit-learn numpy
```

### 4.3 動作確認

使えるデバイスと、`tf.keras` の中身を調べる（検証済み）。
```python
import platform

import keras
import tensorflow as tf

print("tensorflow:", tf.__version__, "| keras:", keras.__version__)
print("python:", platform.python_version())
print("devices:", tf.config.list_physical_devices())
print("GPU:", tf.config.list_physical_devices("GPU"))
print("built with CUDA:", tf.test.is_built_with_cuda())
print("tf.keras is Keras 3:", tf.keras.Sequential is keras.Sequential)
```
実行結果:
```text
$ uv run python 01_env_check.py
tensorflow: 2.21.0 | keras: 3.15.1
python: 3.12.16
devices: [PhysicalDevice(name='/physical_device:CPU:0', device_type='CPU')]
GPU: []
built with CUDA: False
tf.keras is Keras 3: True
```
公式のインストール手順も「There is currently no official GPU support for MacOS.」と書いている。Apple の GPU プラグイン tensorflow-metal の最終版 1.2.0（2025-01-31）を、プロジェクトの依存を変えずに uv の一時環境で 1 回だけ試した（検証済み）。
```text
$ uv run --with tensorflow-metal==1.2.0 python 01_env_check.py
…（中略: ダウンロードの表示とトレースバック 48 行）…
tensorflow.python.framework.errors_impl.NotFoundError: dlopen(~/.cache/uv/archive-v0/cs-Pt-JLYkKRUukm/lib/python3.12/site-packages/tensorflow-plugins/libmetal_plugin.dylib, 0x0006): Library not loaded: @rpath/_pywrap_tensorflow_internal.so
…（中略: 探した場所の一覧 2 行）…
```
GPU が見えないのではなく、**`import tensorflow` の時点で失敗した**。プラグインは `_solib_darwin_arm64/` の下を探したが、TF 2.21 の site-packages にこのディレクトリはなく、`_pywrap_tensorflow_internal.so` は `tensorflow/python/` の下にあった（`01c_tf_layout.log`）。PyPI の tensorflow-metal の対応表も TF v2.18 の行で終わっている。Mac では CPU で動かす。

---

## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。

### 5.1 最小の Keras の学習と `tf.data`

データの読み込みは §5.2 以降でも使うので `digits_tf.py` に置く（検証済み）。
```python
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


def load_data(scale: float = 16.0):
    X, y = load_digits(return_X_y=True)  # 8x8 の手書き数字 1,797 枚（scikit-learn に同梱）
    return train_test_split((X / scale).astype("float32"), y, test_size=0.2, random_state=0)
```
PyTorch 版と同じ構成（64 → 128 → 10）で手書き数字を分類する。既存のコードでは、入力を `tf.data` のパイプラインで組んでいることが多いので、生の画素値から `map` / `batch` / `prefetch` で組んで学習する。`.keras` で保存し、§5.2 で使う SavedModel も書き出す（検証済み）。
```python
import keras
import tensorflow as tf

from digits_tf import load_data

keras.utils.set_random_seed(0)
X_tr, X_te, y_tr, y_te = load_data(scale=1.0)  # 画素値 0〜16 のまま受け取り、正規化は map で行う


def make_ds(X, y, training: bool) -> tf.data.Dataset:
    ds = tf.data.Dataset.from_tensor_slices((X, y))
    ds = ds.shuffle(len(X), seed=0) if training else ds  # 学習用だけ、エポックごとに並べ替える
    ds = ds.map(lambda x, y: (x / 16.0, y), num_parallel_calls=tf.data.AUTOTUNE)  # 前処理を並列に走らせる
    return ds.batch(64).prefetch(tf.data.AUTOTUNE)  # 学習中に次のバッチを先に用意する


model = keras.Sequential([keras.Input(shape=(64,)), keras.layers.Dense(128, activation="relu"),
                          keras.layers.Dense(10)])  # 出力は 10 クラスぶんのスコア（logits）
model.compile(optimizer=keras.optimizers.AdamW(1e-3), metrics=["accuracy"],
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True))
history = model.fit(make_ds(X_tr, y_tr, True), epochs=30, verbose=0)  # 学習ループは fit の中で回る
_, acc = model.evaluate(make_ds(X_te, y_te, False), verbose=0)
print(f"backend={keras.backend.backend()}  last loss={history.history['loss'][-1]:.4f}  test accuracy={acc:.3f}")
model.save("digits.keras")  # Keras 3 の保存形式。拡張子 .keras が必須
model.export("export/digits/1", verbose=False)  # SavedModel を書き出す。末尾の 1 は TF Serving が読む版番号
```
実行結果:
```text
$ uv run python 02_train_keras.py
~/work/dev/learning/ai-frameworks-verify/tensorflow/.venv/lib/python3.12/site-packages/keras/src/trainers/epoch_iterator.py:74: UserWarning: `shuffle=True` was passed, but will be ignored since the data `x` was provided as a tf.data.Dataset. The Dataset is expected to already be shuffled (via `.shuffle(buffer_size)`).
  self.data_adapter = data_adapters.get_data_adapter(
backend=tensorflow  last loss=0.0796  test accuracy=0.969
```
- 正解率は 96.9% で、PyTorch 版の 97.2% とほぼ同じである（実装の細部が違ううえ、Keras の `AdamW` の weight decay の既定値は 0.004 で PyTorch の 0.01 と違うので、完全には一致しない）。**TF 2.16 から Keras 3 が既定になり、`tf.keras` も Keras 3 を指す**（§4.3 の `True`）。新しく書くなら `import keras` でよい。Keras 2 のまま動かすには、`tf-keras` を入れて `TF_USE_LEGACY_KERAS=1` を設定する（2.16.1 のリリースノート。§6.2 で確認）
- **`prefetch`** は、学習ステップ s の実行中にステップ s+1 のデータを用意する。公式ガイドは、1 ステップの時間が「学習と読み込みの和」から「大きいほう」に縮むと説明している。警告のとおり、Dataset を `fit` に渡すと `fit` 側のシャッフルは効かないので、シャッフルは Dataset 側で `shuffle()` する

### 5.2 既存資産を読む — SavedModel

Keras 3 で SavedModel を書き出すには、§5.1 の最終行のように `model.export()` を使う（`model.save()` では書き出せない）。`export/digits/1/` には `saved_model.pb`（グラフ）・`variables/`（重み）・`assets/`・`fingerprint.pb` ができた（`04_export_tree.log`）。ここからは、これを**中身を知らない他人の資産**として扱う。最初に、入口の名前と入出力の形を CLI で確かめる（検証済み）。
```text
$ uv run saved_model_cli show --dir export/digits/1 --all
…（中略: __saved_model_init_op と serve の定義 25 行）…
signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['keras_tensor'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 64)
        name: serving_default_keras_tensor:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['output_0'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 10)
        name: StatefulPartitionedCall_1:0
  Method name is: tensorflow/serving/predict
…（中略: 演算の一覧と Concrete Functions 8 行）…
```
読むのは 3 点である。入口の名前（`serving_default`）、入力の名前と形（`keras_tensor`、`(-1, 64)` は「件数は自由、1 件 64 個の float」）、出力の名前と形（`output_0`、`(-1, 10)`）。これを使って読み込み、推論する。入力名は決め打ちせず、signature から読む（検証済み）。
```python
import keras
import tensorflow as tf

from digits_tf import load_data

_, X_te, _, y_te = load_data()
loaded = tf.saved_model.load("export/digits/1")  # Keras もモデルのクラス定義も要らない
infer = loaded.signatures["serving_default"]  # TF Serving が既定で呼ぶ入口
input_name = list(infer.structured_input_signature[1])[0]  # 入力名は決め打ちせず signature から読む
print("signatures:", list(loaded.signatures.keys()), "| input name:", input_name)
logits = infer(**{input_name: tf.constant(X_te)})["output_0"].numpy()
print("output:", logits.shape, f"| test accuracy={(logits.argmax(1) == y_te).mean():.3f}")
layer = keras.layers.TFSMLayer("export/digits/1", call_endpoint="serving_default")  # Keras 3 から包んで使う
print("TFSMLayer output keys:", list(layer(X_te[:2]).keys()))
```
実行結果:
```text
$ uv run python 04b_load_saved_model.py
signatures: ['serve', 'serving_default'] | input name: keras_tensor
output: (360, 10) | test accuracy=0.969
TFSMLayer output keys: ['output_0']
```
`tf.saved_model.load` が返すのは Keras のモデルではなく、入口の関数を持ったオブジェクトである。signature の関数は入力名をキーワード引数にして呼び、出力は辞書で返る。正解率は §5.1 と同じ 96.9% になった。

> ⚠️ **入力名はモデルの作り方で変わる**。同じモデルを `.keras` から読み直して書き出すと、入力名は `input_layer` になった（`04y_input_name_after_reload.py`）。名前を `input_layer` と決め打ちした最初の版の 04b は、`missing a required keyword-only argument: 'keras_tensor'` という `TypeError` で落ちた（`04x_input_name_mismatch_error.log`）。

### 5.3 LiteRT — `.tflite` に変換して端末向けに動かす

変換は TensorFlow 本体の `tf.lite.TFLiteConverter` で、実行は TensorFlow を使わない LiteRT のランタイム（`ai-edge-litert`）で行う。重みを int8 にした版も作り、SavedModel と予測が同じかを確かめる（検証済み）。
```python
import numpy as np
import tensorflow as tf
from ai_edge_litert.interpreter import Interpreter

from digits_tf import load_data

_, X_te, _, _ = load_data()
loaded = tf.saved_model.load("export/digits/1")  # 読み込んだオブジェクトは変数で保持する（§8）
ref = loaded.serve(tf.constant(X_te)).numpy()
for name, quantize in (("float32", False), ("int8", True)):
    converter = tf.lite.TFLiteConverter.from_saved_model("export/digits/1")  # 変換は TF で行う
    converter.optimizations = [tf.lite.Optimize.DEFAULT] if quantize else []  # 重みを int8 にする
    tflite = converter.convert()  # .tflite の中身（bytes）。端末にはこれをファイルで配る
    interpreter = Interpreter(model_content=tflite)  # 実行は TF を使わない LiteRT のランタイムで行う
    inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    interpreter.resize_tensor_input(inp["index"], X_te.shape)  # 既定の [1, 64] を 360 件ぶんに広げる
    interpreter.allocate_tensors()
    interpreter.set_tensor(inp["index"], X_te)
    interpreter.invoke()
    logits = interpreter.get_tensor(out["index"])
    print(f"{name:7s} size={len(tflite):6d} B  max abs diff={np.abs(logits - ref).max():.2e}"
          f"  same prediction={(logits.argmax(1) == ref.argmax(1)).mean():.3f}")
```
実行結果:
```text
$ uv run python 05_tflite_litert.py
…（中略: 変換時のログ 20 行）…
float32 size= 39976 B  max abs diff=4.77e-06  same prediction=1.000
int8    size= 13304 B  max abs diff=5.24e-02  same prediction=1.000
```
- macOS（arm64）でも `ai-edge-litert` 2.3.0 はそのまま動き、float 版の予測は 360 件すべて一致した。int8 版はファイルが約 1/3 になり、スコアは最大 0.052 ずれたが、予測はやはり全件一致した。実際のモデルでは量子化後の精度を必ず測り直す。旧来の `tf.lite.Interpreter` も 2.21 で動くが、「deprecated and is scheduled for deletion in TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.」と警告が出た。2.20 で削除予定と書かれたまま 2.21 に残っている。Keras 3 の `model.export(..., format="litert")` でも直接書き出せた（いずれも `05b_litert_alternatives.py`）

### 5.4 TF Serving — Docker で REST 配信する

§5.1 の `export/digits/` をそのまま TF Serving に渡し、REST の `POST /v1/models/<name>:predict` で推論する。マウントするのは版番号のディレクトリ（`1/`）の親である（公式 docs 準拠・未実行: `tensorflow/serving` の公開イメージは `latest`・`2.21.0` とも linux/amd64 だけで、この Mac 向けのイメージがないため）。
```bash
docker run -p 127.0.0.1:8501:8501 \
  --mount type=bind,source="$(pwd)/export/digits",target=/models/digits \
  -e MODEL_NAME=digits -t tensorflow/serving:2.21.0
curl -X POST http://localhost:8501/v1/models/digits:predict -d @request.json
```
`request.json` は `{"instances": [[…64 個の数値…], …]}` の形（行形式）で書く。入力が 1 つなので入力名は省ける。応答は `{"predictions": [[…10 個のスコア…], …]}` になり、入口を指定しなければ `serving_default` が使われる。この API には認証が無いため、手元での確認では `127.0.0.1` にだけ公開する。他の端末から使わせるなら、認証つきのゲートウェイを前に置く。

---

## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | TensorFlow を使う理由 | 本番で足すもの |
|---|---|---|---|
| 既存の SavedModel・TF Serving の保守 | SavedModel → REST / gRPC の推論 API | TF Serving は SavedModel をそのまま配信する。2.21 の発表でも保守の対象に入っている | 版の固定、セキュリティ修正への追従、Linux amd64 の実行環境 |
| LiteRT によるモバイル・エッジ推論 | SavedModel → `.tflite` → 端末上の推論 | 変換は TF、実行は `ai-edge-litert` に分かれ、端末側に TF 本体は要らない（§5.3） | 量子化後の精度の確認、端末ごとの速度測定 |
| 移行判断の材料集め | 既存の資産 → 入出力の仕様と、動かない箇所の一覧 | `saved_model_cli` と Keras 3 の挙動から、移行の手間を前もって見積もれる（§6.2） | 本番データでの出力一致の確認 |

### 6.2 代表例: Keras 3 への移行チェックリスト

Keras 2（TF 2.15 以前）の資産を TF 2.21 / Keras 3 で動かすときに確かめる項目を、ハンズオンで観測した結果と合わせて並べる。「根拠」列は、筆者の検証環境（このリポジトリの外）で実行したスクリプトの名前で、結果の要点を表に書いた。

| 確認すること | TF 2.21 / Keras 3 での結果 | 根拠 | 対処 |
|---|---|---|---|
| `tf.keras` を使ったコード | `tf.keras` は Keras 3 を指し、普通のモデルの学習はそのまま動いた | §4.3・§5.1 | 下の行に当たる箇所だけ直す |
| `model.save("dir")`（拡張子なし = SavedModel） | `ValueError: Invalid filepath extension for saving` | `04c_keras3_saving_errors.py` | 学習を続けるなら `.keras`、配信・変換するなら `model.export()` |
| `keras.models.load_model("<SavedModel>")` | `ValueError: File format not supported`。エラー文自体が `TFSMLayer` を案内する | 同上 | 推論だけなら `tf.saved_model.load` か `TFSMLayer`（§5.2） |
| 既存の SavedModel を配信・変換する経路 | `saved_model_cli`・`tf.saved_model.load`・`TFLiteConverter` はそのまま使えた | §5.2・§5.3 | 変更不要。ただし入力名は書き出し方で変わるので、呼ぶ側で決め打ちしない |
| `tf.lite.Interpreter` | 動くが deprecated の警告が出た | `05b_litert_alternatives.py` | `ai_edge_litert.interpreter.Interpreter` に置き換える |
| すぐには直せないコード | `tf-keras==2.21.0` と `TF_USE_LEGACY_KERAS=1` で `tf.keras` が `tf_keras` に切り替わり、`model.save("dir")` で SavedModel も書けた | `04d_legacy_tf_keras.py` | 当面の逃げ道に留める。tf-keras 2.21.0 は `tensorflow<2.22,>=2.21` を要求するので、TF を上げるたびに対応する版が要る |
| 独自の層の `tf.Variable`、`KerasTensor` への TF の演算、GPU での `jit_compile` | 本書のモデルには該当がなく、未検証 | Keras の移行ガイド | `self.add_weight()` で変数を作る、`keras.ops` を使う、XLA のエラーが出たら `jit_compile=False` |
| `tf.estimator` | TF 2.16 で削除された | 2.16.1 のリリースノート | TF 2.15 以前に留めるか、書き直す |
| `tf.summary` / TensorBoard のコールバック | 2.21 で TensorBoard が依存から外れた。2.22 では入れていないと ImportError になると明記された | リリースノート | `tensorboard` を明示的に入れる |

移行先は次の順に考えると決めやすい。
- **配信が TF Serving・端末が LiteRT で、モデルの更新が少ない** → TensorFlow のまま保守する。版を固定し、セキュリティ修正を追う
- **`tf.keras` のコードを今後も育てる** → Keras 3 に寄せる。上の表の 2〜5 行目を直せば TensorFlow バックエンドのまま動く。JAX や PyTorch へ切り替えるには、`tf.*` の演算を `keras.ops` に置き換える（移行ガイド）
- **生成 AI や Transformers と組み合わせる** → PyTorch に移す。既存の SavedModel は、移行が終わるまで TF Serving で配信し続けられる

---

## 7. 本番運用の要点

- **版を固定し、セキュリティ修正を追う**。2.21 の発表は、脆弱性と重大なバグへの対応に注力し、必要に応じて minor / patch を出すと書いている
- **他人が配布した SavedModel を信用しない**。TensorFlow の SECURITY.md は「TensorFlow models are programs」とし、信頼できないモデルを使うのは信頼できないコードを動かすのと同じだとしている。必要ならサンドボックスで動かす
- **TF Serving の公開イメージは linux/amd64 だけ**である（`docker manifest inspect` で確認）。動作確認は本番と同じ Linux amd64 の環境で行う
- **移行の前に記録を取る**。§5.2 の手順で今の SavedModel の入出力と、正解の分かっているデータでの出力を残しておけば、移行後のモデルと突き合わせられる
- **NVIDIA GPU** では、Linux で `pip install tensorflow[and-cuda]` を使う。CUDA 13 は 2.22 から `tensorflow-cuda13` で初期対応する（公式 docs 準拠・未実行: NVIDIA GPU が必要）

---

## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `uv add tensorflow` が `self-dependencies are not permitted` で失敗する（実測） | ディレクトリ名が `tensorflow` で、プロジェクト名と衝突した | `pyproject.toml` の `name` を別の名前に変える |
| tensorflow-metal を入れたら `import tensorflow` が `NotFoundError` になる（実測） | 1.2.0 のプラグインが、TF 2.21 にない場所の共有ライブラリを探す | プラグインを外し、CPU で動かす（§4.3） |
| `missing a required keyword-only argument: 'keras_tensor'`（実測） | SavedModel の入力名を決め打ちした | 入力名を signature から読む（§5.2） |
| `Called a function referencing variables which have been deleted`（実測） | `tf.saved_model.load(...).serve(...)` のように、戻り値を保持せずに呼んだ | 戻り値を変数に入れてから呼ぶ（`05x_saved_model_load_chained.py` で再現） |
| `Invalid filepath extension for saving` / `File format not supported`（実測） | Keras 3 の `save` / `load_model` は SavedModel を扱わない | `model.export()` と `tf.saved_model.load` / `TFSMLayer`（§6.2） |
| `shuffle=True was passed, but will be ignored`（実測） | `fit` に Dataset を渡すと、`fit` 側のシャッフルは効かない | Dataset 側で `shuffle()` する（§5.1） |

---

## 9. 次のステップ

- 移行先を知る: [Keras 3](keras.md)（バックエンドを選べる）・[PyTorch](pytorch.md)・[JAX](jax.md)。端末と配信を深める: [LiteRT の docs](https://developers.google.com/edge/litert)（量子化と GPU / NPU による高速化）、[TF Serving の RESTful API](https://www.tensorflow.org/tfx/serving/api_rest)（版の指定 `/versions/<N>` やモデルの状態の取得）

---

## 出典

| 情報源 | URL |
|---|---|
| What's new in TensorFlow 2.21 | https://developers.googleblog.com/whats-new-in-tensorflow-221/ （2026-11-08 確認。2026-03-06、Pradeep Kuppala / Rodney Witcher。保守方針・対象のエコシステム・Keras 3 / JAX / PyTorch の推奨・LiteRT への改名） |
| TensorFlow Releases | https://github.com/tensorflow/tensorflow/releases （2026-11-08 確認。v2.21.0: Python 3.9 と TensorBoard 依存の削除 / v2.22.0-rc0（2026-09-24）: Python 3.14・CUDA 13・TensorBoard がないときの ImportError / v2.16.1: Keras 3 の既定化・`TF_USE_LEGACY_KERAS`・`tf.estimator` の削除） |
| Install TensorFlow with pip | https://www.tensorflow.org/install/pip （2026-11-08 確認。macOS は GPU 非対応） |
| Migrating Keras 2 code to multi-backend Keras 3 / Model export for inference | https://keras.io/guides/migrating_to_keras_3/ ・ https://keras.io/api/models/model_saving_apis/export/ （2026-11-08 確認、Context7 `/websites/keras_io_guides`・`/websites/keras_io` 経由。`model.export` の `format` に `tf_saved_model` / `litert` など） |
| Using the SavedModel format / Better performance with the tf.data API | https://www.tensorflow.org/guide/saved_model ・ https://www.tensorflow.org/guide/data_performance （2026-11-08 確認、Context7 `/tensorflow/docs` 経由。prefetch と並列 map） |
| Convert TensorFlow models / Migrate to LiteRT from TensorFlow Lite | https://developers.google.com/edge/litert/conversion/tensorflow/convert_tf ・ https://developers.google.com/edge/litert/migration （2026-11-08 確認、Context7 `/websites/developers_google_edge_litert` 経由） |
| TensorFlow Serving with Docker / RESTful API | https://www.tensorflow.org/tfx/serving/docker ・ https://www.tensorflow.org/tfx/serving/api_rest （2026-11-08 確認。DeepWiki `tensorflow/serving` でも照合） |
| TensorFlow SECURITY.md | https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md （2026-11-08 確認） |
| tensorflow-metal / tf-keras | https://pypi.org/project/tensorflow-metal/ ・ https://developer.apple.com/metal/tensorflow-plugin/ ・ https://pypi.org/project/tf-keras/ （2026-11-08 確認。metal の最終版は 1.2.0 で対応表は TF v2.18 の行まで。tf-keras 2.21.0 は `tensorflow<2.22,>=2.21` を要求） |
| Getting Started - TensorFlow（ONNX Runtime） | https://onnxruntime.ai/docs/tutorials/tf-get-started.html （2026-11-08 確認、Context7 `/websites/onnxruntime_ai` 経由。tf2onnx） |
| Transformers v5 Migration guide | https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md （2026-11-08 確認。「We're removing the TensorFlow and Jax parts of the library」） |
| GitHub `tensorflow/tensorflow` / Docker Hub `tensorflow/serving` | ★201,380・最新の正式版 v2.21.0（2026-03-06 公開）・直近 13 週のコミット 5,089（自動コミットを含むかは未確認）（2026-11-08 に GitHub API で取得）。`tensorflow/serving` の `latest` と `2.21.0` は linux/amd64 のみ（2026-11-08 に `docker manifest inspect` で確認） |

### 確認できなかった事項

- **保守がいつまで続くか**。2.21 の発表は今後の方針を書いているが、終了の時期には触れていない
- **tensorflow-metal の今後**。PyPI の対応表は TF v2.18 の行で終わり、Apple のページにも版の対応表はない。本書は uv の一時環境で 1.2.0 を試して失敗した事実だけを書いた。同じ仮想環境に直接入れた場合も、探し先のディレクトリが TF 2.21 にないため失敗すると見ているが、試していない
- **TF Serving の arm64 対応**（Apple Silicon で動く公式イメージの予定は見つけられず、§5.4 は未実行）と、**tf2onnx が TF 2.21 で動くか**（ONNX Runtime の docs の手順を確かめただけで、変換は試していない）
- **GitHub のコミット数が人手の開発をどこまで表すか**、**TensorFlow.js の方針**（`tensorflow/tfjs` は最終 push 2026-06-23、最終リリース v4.22.0（2024-10-21）であることだけを確認）

- 関連: [AI フレームワーク学習ガイド](README.md) / [PyTorch](pytorch.md) / [Keras 3](keras.md) / [JAX](jax.md)
