# Keras 3 入門 — 1 つのコードを JAX / PyTorch / TensorFlow で動かし、保存したモデルを別のバックエンドで使う

> 出典（一次情報）:
> - [Keras 3.15.1 Release (github.com)](https://github.com/keras-team/keras/releases/tag/v3.15.1) — 3.15.1 の変更点。`.keras` 展開時の防御など安全性の修正が中心
> - [keras-team/keras README (github.com)](https://github.com/keras-team/keras) — バックエンドの設定方法、`tf.keras` からの移行の考え方、各バックエンドの最低版
> - [Getting started with Keras (keras.io)](https://keras.io/getting_started/) — インストール、`KERAS_BACKEND`、`tf.keras` と Keras 2（`tf_keras`）の関係
> - [Migrating Keras 2 code to multi-backend Keras 3 (keras.io)](https://keras.io/guides/migrating_to_keras_3/) — `tf.*` から `keras.ops` への置き換え、保存形式の変更
> - [What's new in TensorFlow 2.21 (developers.googleblog.com)](https://developers.googleblog.com/whats-new-in-tensorflow-221/) — TensorFlow が保守中心になり、新しい生成 AI の開発に Keras 3 / JAX / PyTorch を勧めたこと
>
> 最終更新: 2026-11-08（Keras 3.15.1 で検証。★と最新版は 2026-11-08 時点）

Keras 3 は、モデルの定義と学習を短く書くための高水準 API である。下で実際に計算するフレームワーク（バックエンド）を
JAX・PyTorch・TensorFlow から選べ、**同じコードのまま差し替えられる**のが最大の特徴である。本ドキュメントでは、[PyTorch 入門](pytorch.md) と同じ手書き数字の分類を Keras 3 で書き、3 つのバックエンドで動かし比べ、保存したモデルを別のバックエンドで読み込むところまでを手で確かめる。
分散学習や独自の学習ループ（`train_step` の上書き）は扱わない。シリーズ全体の地図は [AI フレームワーク学習ガイド](README.md) を参照。

---

## 1. TL;DR

- **Keras 3 は「モデルを書く層」で、計算は JAX / PyTorch / TensorFlow のどれかに任せる**。バックエンドは環境変数 `KERAS_BACKEND` で選び、**`import keras` より前に**決める。後からは変えられない（§4.3）。
- `compile` → `fit` → `evaluate` の 3 行で学習と評価が済む。PyTorch では自分で書いた学習ループを、Keras は肩代わりする（§5.1）。
- **同じスクリプトが 3 つのバックエンドでそのまま動いた**。精度はほぼ揃うが、同じシードでも数字は一致しない（§5.2）。
- **`keras.ops` だけで書いた独自レイヤーは、どのバックエンドでも動き、`.keras` で保存すれば別のバックエンドで読み込んで同じ予測が出る**（§5.3・§5.4）。
- Mac の torch バックエンドは、**何も指定しなくても MPS（Apple Silicon の GPU）を使う**。小さなモデルではそれが CPU より遅かった（§5.5）。
- TensorFlow 2.21 の公式発表は、新しい生成 AI の開発に「Keras 3, JAX, and PyTorch」を勧めている。`tf.keras` で書かれた既存のコードを Keras 3 に移す場面が、実務での主な出番になる（§6）。

---

## 2. 前提知識

- **Python の基本**と、[PyTorch 入門](pytorch.md) の §5.3（学習ループの 4 行）程度の理解。**NumPy の配列**（Keras はそのまま `fit` / `predict` に渡せる）
- バックエンド・バッチ・エポック・logits などの用語は、索引の [用語集](README.md#61-基礎学習) にまとめた

---

## 3. 位置づけと比較

Keras 3 は、シリーズの最下層「深層学習の基盤」のうち、**基盤フレームワークの上に被せる高水準 API** にあたる。
入力はデータとモデルの定義、出力はバックエンドに依存しない `.keras` ファイル（構造と重み）と、配信用に書き出した成果物（SavedModel など）である。

| フレームワーク | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **Keras 3** | 少ないコードで書ける。バックエンドに JAX / PyTorch / TensorFlow を選べ、`.keras` はどのバックエンドでも読める | 細かい制御は下のフレームワークに降りる必要がある。LLM 周辺の主要な OSS は PyTorch を前提にしている | 定番の構成を素早く作る、バックエンドの選択を後に回したい、`tf.keras` のコードを移す |
| `tf.keras`（Keras 2 系） | 既存の資産がそのまま動く | TensorFlow 2.16 以降の `tf.keras` は Keras 3 を指す。Keras 2 は `tf_keras` パッケージとして保守のみ（新機能なし） | 手を入れずに既存のコードを動かし続ける |
| [PyTorch](pytorch.md) | 書いたとおりに動き、デバッグしやすい。LLM 周辺の主要な OSS が前提にしている | 学習ループ・ログ・保存を自分で書く | 迷ったらこれ。LLM 周辺の道具を使うなら事実上の前提 |
| PyTorch Lightning | 素の PyTorch のコードを `LightningModule` と `Trainer` に整理し、ログ・複数 GPU などの定型部分を自動化する | PyTorch 専用。バックエンドは選べない | PyTorch のまま定型部分を減らしたい |
| Flax（NNX） | [JAX](jax.md) の上のニューラルネット用ライブラリ。JAX の関数変換をそのまま使える | JAX 専用。学習ループは optax などと組み合わせて自分で書く | JAX と TPU で研究・大規模学習をする |

> **ポイント**: TensorFlow 2.21 の公式発表（2026-03-06）は、TensorFlow 自体をセキュリティ修正・依存の更新などに絞ると述べたうえで、
> "we recommend exploring our latest updates for Keras 3, JAX, and PyTorch for new work in Generative AI." と書いている。TensorFlow の資産を持つチームにとって、Keras 3 は同じ書き方のまま移れる先になる。

`tf.keras` と Keras 3 の関係（公式の Getting started より）: TensorFlow 2.15 までは `tf.keras` が Keras 2 だったが、**2.16 以降は Keras 3 を指す**。
Keras 2 のまま動かすには `tf_keras` を入れて `import tf_keras` に替える（公式の推奨）か、`TF_USE_LEGACY_KERAS=1` で `tf.keras` を `tf_keras` に向ける（プロセス内の他のパッケージにも効く）。

---

## 4. セットアップ

### 4.1 検証環境

検証環境の全体（ハードウェア・uv の方針）は索引の [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。
本ドキュメント固有の版は次のとおり。**3 つのバックエンドは 1 つの環境に同居できた**ので、環境は分けていない。

| 項目 | 版 |
|---|---|
| keras | 3.15.1 |
| jax / jaxlib | 0.12.0.1 / 0.12.0.1 |
| torch / tensorflow | 2.15.0 / 2.21.0 |
| numpy / scikit-learn | 2.5.4 / 1.9.1 |
| Python | 3.12.16（uv で管理） |

### 4.2 インストール

Keras 本体とバックエンドは別のパッケージである。使うバックエンドだけを入れればよい（検証済み）。

```bash
uv init --bare --python 3.12 keras-hello && cd keras-hello
uv python pin 3.12
uv add "keras==3.15.1" "jax==0.12.0.1" "torch==2.15.0" "tensorflow==2.21.0" scikit-learn
```

> **注意**: uv のプロジェクト名（ディレクトリ名）を `keras` にすると、`uv add keras` が自己依存のエラーで止まる。検証では `name` を `keras-verify` に変えた。
> NVIDIA GPU で複数のバックエンドを使う場合、公式は CUDA の版の食い違いを避けるため**バックエンドごとに環境を分ける**ことを勧めている（公式 docs 準拠・未実行: NVIDIA GPU が必要）。

### 4.3 動作確認 — バックエンドは import の前に決める

`KERAS_BACKEND` を設定してから `keras` を読み込み、`keras.config.backend()` で確かめる（検証済み）。

```python
import os

os.environ["KERAS_BACKEND"] = "jax"  # 必ず import keras より前に書く

import keras  # noqa: E402

print("keras:", keras.__version__)
print("backend:", keras.config.backend())

os.environ["KERAS_BACKEND"] = "torch"  # import した後に変えても…
print("after setting KERAS_BACKEND=torch:", keras.config.backend())  # 変わらない
```

実行結果:

```text
$ uv run python 01_backend_first.py
keras: 3.15.1
backend: jax
after setting KERAS_BACKEND=torch: jax
```

`KERAS_BACKEND` を付けずに起動すると、設定ファイル `~/.keras/keras.json` の値（この環境では `tensorflow`）が使われた（`01b_default_backend.log`）。
優先順位は **`KERAS_BACKEND` → `~/.keras/keras.json` → 既定の `tensorflow`** で、`keras.json` が無ければ初回の import で既定値の入ったものが作られる（3.15.1 のソース `keras/src/backend/config.py` で確認）。以降は `env KERAS_BACKEND=<名前>` を前に付けて切り替える。

---

## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。

### 5.1 Functional API で数字を分類する — `compile` / `fit` / `evaluate`

[PyTorch 入門](pytorch.md) §5.3 と同じデータ（scikit-learn 同梱の手書き数字 1,797 枚）・同じ分け方・同じ構成（64→128→10）にする。
Functional API は、`keras.Input` から層を関数のように呼んでつなぎ、最後に `keras.Model(入力, 出力)` で包む書き方である。
§5.2〜§5.5 と §7 でも読み込むので、`digits.py` として置く（検証済み）。

```python
"""digits を Functional API で分類する。§5.1〜§5.5 と §7 で共有する。"""
import time

import keras
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


def load_data():
    digits = load_digits()  # 8x8 の手書き数字 1,797 枚（scikit-learn に同梱。ダウンロード不要）
    X = (digits.data / 16.0).astype("float32")
    y = digits.target.astype("int32")  # JAX は既定で 64 ビット整数を使わない（§8）
    return train_test_split(X, y, test_size=0.2, random_state=0)  # pytorch.md と同じ分け方


def build_model():
    keras.utils.set_random_seed(0)  # Python・NumPy・バックエンドの乱数をまとめて固定する
    inputs = keras.Input(shape=(64,))
    x = keras.layers.Dense(128, activation="relu")(inputs)
    outputs = keras.layers.Dense(10)(x)  # 10 クラスぶんのスコア（logits）
    return keras.Model(inputs, outputs, name="digit_classifier")


def train(model, epochs=30):
    X_tr, X_te, y_tr, y_te = load_data()
    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=0.01),  # PyTorch の既定値に合わせる
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    start = time.perf_counter()
    history = model.fit(X_tr, y_tr, batch_size=64, epochs=epochs, verbose=0)
    elapsed = time.perf_counter() - start
    _, acc = model.evaluate(X_te, y_te, verbose=0)
    print(f"backend={keras.config.backend():10s} last loss={history.history['loss'][-1]:.4f}  "
          f"test accuracy={acc:.3f}  train time={elapsed:.2f}s")
    return model
```

`model.summary()` で数えたパラメータは 9,610 個で（`02_functional.log`）、PyTorch 版の `DigitClassifier` と同じ構成である（実行は §5.2）。PyTorch で 4 行書いた「予測 → 誤差 → 勾配 → 更新」は `fit` の中で行われる。`compile` で最適化手法・損失・指標を決め、`fit` で学習し、`evaluate` で評価する、という分担を覚えればよい。

### 5.2 中心の実演 — 同じスクリプトを 3 つのバックエンドで動かす

次のスクリプトを、`KERAS_BACKEND` だけを替えて 3 回実行する（検証済み）。

```python
from digits import build_model, train

model = train(build_model())
print("weights on:", model.weights[0].value.device)  # 重みがどのデバイスに置かれたか
```

実行結果（3 回の実行のログを順に並べた）:

```text
$ env KERAS_BACKEND=jax uv run python 03_same_script.py
backend=jax        last loss=0.0769  test accuracy=0.975  train time=0.39s
weights on: cpu:0
$ env KERAS_BACKEND=torch uv run python 03_same_script.py
backend=torch      last loss=0.0765  test accuracy=0.981  train time=4.25s
weights on: mps:0
$ env KERAS_BACKEND=tensorflow uv run python 03_same_script.py
backend=tensorflow last loss=0.0780  test accuracy=0.967  train time=0.95s
weights on: /job:localhost/replica:0/task:0/device:CPU:0
```

- **コードは 1 行も変えていない**。同じ実行をもう一度繰り返すと、損失と精度は 3 つとも同じ値になり、時間も同じ順位だった（`03_backend_*_run2.log`）
- **同じシードでも、バックエンドが違うと精度は揃わない**。差はテスト 360 件で最大 5 件にあたる。torch の MPS と CPU の間では、重みの初期値そのものが違った（§5.5）
- torch だけが遅いのは、Keras が自動で MPS を選び、この小さなモデルでは GPU の起動と転送の手間が勝ったためである（§5.5）。PyTorch 入門 §5.4 と同じ現象である
- JAX と TensorFlow は、この環境では CPU だけを認識していた（`jax.devices()` は `[CpuDevice(id=0)]`、TensorFlow の物理デバイスは `['CPU']`。`06b_jax_tf_devices.log`）
- Keras 公式は「モデルによって最速のバックエンドは変わる」としている。ここでの時間はこの Mac の小さなモデルの値で、一般論にはならない

### 5.3 `keras.ops` だけで独自レイヤーを書く

組み込みに無い層は `keras.layers.Layer` を継承して書く。公式は、**どのバックエンドでも動かすには `keras.ops` など Keras の名前空間の API だけを使う**よう求めている（`tf.nn` や `jax.numpy` を使うとそのバックエンド専用になる）。
LLM でよく使う正規化 RMSNorm を書き、§5.1 のモデルに差し込む。`rmsnorm.py` として置く（検証済み）。

```python
import keras
from keras import ops


@keras.saving.register_keras_serializable(package="demo")  # 保存したモデルを読み戻すために登録する
class RMSNorm(keras.layers.Layer):
    """LLM でよく使う正規化。keras.ops だけで書くので、どのバックエンドでも動く。"""

    def __init__(self, epsilon=1e-6, **kwargs):
        super().__init__(**kwargs)
        self.epsilon = epsilon

    def build(self, input_shape):
        self.scale = self.add_weight(shape=(input_shape[-1],), initializer="ones", name="scale")

    def call(self, x):
        rms = ops.sqrt(ops.mean(ops.square(x), axis=-1, keepdims=True) + self.epsilon)
        return x / rms * self.scale

    def get_config(self):  # 保存時に epsilon も書き出す
        return {**super().get_config(), "epsilon": self.epsilon}


def build_rms_model():
    keras.utils.set_random_seed(0)
    inputs = keras.Input(shape=(64,))
    x = keras.layers.Dense(128, activation="relu")(inputs)
    x = RMSNorm()(x)  # 独自レイヤーも組み込みのレイヤーと同じように差し込める
    outputs = keras.layers.Dense(10)(x)
    return keras.Model(inputs, outputs, name="digit_classifier_rms")
```

`04_custom_layer.py` で、この層の出力が NumPy で計算した正解と一致すること（`np.allclose`）と、モデルに差し込んで学習できることを 3 つのバックエンドで確かめた。
テスト精度は jax 0.978・torch 0.983・tensorflow 0.972 だった（`04_custom_layer_*.log`）。`get_config` と登録（`register_keras_serializable`）は、次の §5.4 で保存したモデルを読み戻すために要る。

### 5.4 `.keras` で保存し、別のバックエンドで読み込む

JAX で学習して `.keras` に保存し、torch と TensorFlow で読み込んで、予測が同じになるかを確かめる（検証済み）。

```python
"""save: 学習して .keras と予測を保存する / load: 別のバックエンドで読み込み、予測を比べる"""
import sys

import keras
import numpy as np

from digits import load_data, train
from rmsnorm import build_rms_model  # import した時点で RMSNorm が登録され、読み込みに使える

_, X_te, _, _ = load_data()
if sys.argv[1] == "save":
    model = train(build_rms_model())
    model.save("digits_rms.keras")  # 構造・重み・compile の設定を 1 ファイルにまとめる
    np.save("pred_saved.npy", model.predict(X_te, verbose=0))
    print(f"saved with backend={keras.config.backend()}")
else:
    model = keras.saving.load_model("digits_rms.keras")
    pred = model.predict(X_te, verbose=0)
    saved = np.load("pred_saved.npy")
    print(f"loaded with backend={keras.config.backend():10s} max abs diff={np.abs(pred - saved).max():.1e}  "
          f"same predicted labels={np.array_equal(pred.argmax(1), saved.argmax(1))}")
```

実行結果（3 回の実行のログを順に並べた）:

```text
$ env KERAS_BACKEND=jax uv run python 05_cross_backend.py save
backend=jax        last loss=0.0076  test accuracy=0.978  train time=0.44s
saved with backend=jax
$ env KERAS_BACKEND=torch uv run python 05_cross_backend.py load
loaded with backend=torch      max abs diff=2.9e-06  same predicted labels=True
$ env KERAS_BACKEND=tensorflow uv run python 05_cross_backend.py load
…（中略: TensorFlow の XLA のログ 5 行）…
loaded with backend=tensorflow max abs diff=3.8e-06  same predicted labels=True
```

JAX で学習したモデルを torch と TensorFlow で読み込み、360 件すべてで同じラベルを予測した。出力の差は 100 万分の数程度で、浮動小数点の計算順序の違いの範囲である。
`.keras` の中身は `metadata.json`・`config.json`・`model.weights.h5` の 3 つを入れた zip で（`unzip -l` で確認。`05c_archive_contents.log`）、バックエンドに固有の情報を持たない。
公式 FAQ も同じことを述べたうえで、独自の部品を含むモデルを別のバックエンドで読むには、その部品を `keras.ops` などで書く必要があるとしている。§5.3 で `keras.ops` だけを使ったのはこのためである。

> ⚠️ **他人が配布した `.keras` ファイルは、`safe_mode=False` で読まない**。`keras.saving.load_model` は既定の `safe_mode=True` で、任意のコードを含み得る lambda の復元を拒む。
> 3.15.1 では、`.keras` の展開時に圧縮爆弾を拒む修正も入った（リリースノートより）。

### 5.5 torch バックエンドは MPS を使うか

§5.2 の `weights on: mps:0` のとおり、torch バックエンドは何も指定しなくても MPS を使った。`keras.device` はバックエンドに依存しない置き場所の指定で、
この中で作った変数とデータはそのデバイスに置かれる。`06_torch_device.py` では、§5.2 と同じ学習を既定（MPS）で 1 回、`with keras.device("cpu"):` の中でもう 1 回行って比べた。

実行結果:

```text
$ env KERAS_BACKEND=torch uv run python 06_torch_device.py
torch: 2.15.0 | mps available: True
backend=torch      last loss=0.0765  test accuracy=0.981  train time=2.85s
weights on: mps:0
backend=torch      last loss=0.0749  test accuracy=0.967  train time=0.83s
weights on: cpu
```

- **torch バックエンドは MPS を使う**。3.15.1 のソース（`keras/src/backend/torch/core.py`）は、環境変数 `KERAS_TORCH_DEVICE` が無ければ MPS → CUDA → XPU → CPU の順に既定の置き場所を決めている
- この小さなモデルでは CPU のほうが約 3.4 倍速かった
- **同じシードでも、MPS と CPU では重みの初期値が違った**（最大 0.35 の差。`06c_init_weights.py`）。そのため精度も変わった。デバイスを替えて結果を比べるときは、この差を織り込む

### 5.6 KerasHub — 事前学習済みモデルの入り口

[KerasHub](https://keras.io/keras_hub/)（旧 KerasNLP）は、Gemma・Qwen3・BERT・Stable Diffusion などのモデルを Keras 3 で実装し、事前学習済みの重みと組み合わせて提供するライブラリである。`keras_hub.models.CausalLM.from_preset("<プリセット名>")` のように 1 行で読み込め、モデル定義が 1 つなので JAX / TensorFlow / PyTorch のどれでも動く。重みは Kaggle Models を主に、Hugging Face Hub にも置かれている。
Gemma など利用規約への同意が要るモデルがあるため、本ドキュメントではダウンロードしていない（公式 docs 準拠・未実行: モデルの利用規約への同意が要る）。

---

## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | Keras 3 を使う理由 | 本番で足すもの |
|---|---|---|---|
| `tf.keras` で書かれた既存コードの移行（§6.2） | 古い学習スクリプト → どのバックエンドでも動くコード | TensorFlow のバックエンドならほぼそのまま動き、`tf.*` を `keras.ops` に替えれば JAX / PyTorch でも動く | 移行前後で精度を比べる評価データ、保存形式の切り替え |
| バックエンドの選択を後に回すチーム標準 | モデルのコード → 速いバックエンドでの学習 | コードを変えずに測り比べられる（§5.2）。`.keras` は別のバックエンドで読める（§5.4） | バックエンドごとの CI、版の固定 |
| 表データ・画像の素早い試作 | CSV・画像 → 分類器 | `compile` / `fit` / `evaluate` で、学習ループを書かずに済む | 評価指標の監視、再学習の仕組み |
| KerasHub のモデルの微調整 | 事前学習済みモデル＋社内データ → 微調整したモデル | `from_preset` で読み、`fit` で学習できる。LoRA などの省メモリの手法も用意されている | 利用規約の確認、GPU、評価データ |

### 6.2 代表例: 数年前の `tf.keras` スクリプトを Keras 3 に移す

TensorFlow が保守中心になった今、社内に残る `tf.keras` の学習スクリプト（数値データの分類器など）を引き継いで、
「TensorFlow 以外でも動く形にしておきたい」という場面がある。移行前のスクリプト `08_legacy_tfkeras.py` は、`from tensorflow import keras` で読み込み、
独自レイヤーの中で `tf.reduce_mean` などを直接使い、`tf.random.set_seed(0)` で乱数を固定し、`model.save("legacy_model")` で SavedModel のフォルダに保存する。
TensorFlow 2.21 で動かすと、`tf.keras` は Keras 3 なので学習まで動き（精度 0.981）、最後の保存で
`ValueError: Invalid filepath extension for saving.`（`.keras` か `.h5` の拡張子を付けるよう求めるエラー）で止まった（`08a_legacy_tensorflow.log`）。
`KERAS_BACKEND=jax` で動かすと、`tf.reduce_mean` に JAX の値が渡り、モデルを組み立てる時点で `AttributeError: Exception encountered when calling Standardize.call().` で止まった（`08a_legacy_jax.log`）。
`tf.*` を含むコードは、TensorFlow のバックエンドでしか動かない。移行後のスクリプト全体は次のとおりである（検証済み）。

```python
"""移行後: import keras と keras.ops に置き換え、.keras 形式で保存する。"""
import keras
from keras import ops
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


@keras.saving.register_keras_serializable(package="legacy")  # 読み戻すときにクラスを探せるようにする
class Standardize(keras.layers.Layer):
    def call(self, x):  # tf.* を keras.ops.* に置き換えた
        mean = ops.mean(x, axis=-1, keepdims=True)
        std = ops.std(x, axis=-1, keepdims=True)
        return (x - mean) / (std + 1e-6)


digits = load_digits()
X_tr, X_te, y_tr, y_te = train_test_split(
    digits.data.astype("float32"), digits.target.astype("int32"), test_size=0.2, random_state=0)
keras.utils.set_random_seed(0)  # tf.random.set_seed の代わり。どのバックエンドでも効く
model = keras.Sequential([keras.Input(shape=(64,)), Standardize(),
                          keras.layers.Dense(128, activation="relu"), keras.layers.Dense(10, activation="softmax")])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(X_tr, y_tr, epochs=30, batch_size=64, verbose=0)
backend = keras.config.backend()
print(f"backend={backend:10s} test accuracy: {model.evaluate(X_te, y_te, verbose=0)[1]:.3f}")
model.save(f"migrated_{backend}.keras")  # 構造と重みを 1 ファイルに。どのバックエンドでも読める
```

実行結果（3 回の実行のログを順に並べた）:

```text
$ env KERAS_BACKEND=jax uv run python 08_migrated.py
backend=jax        test accuracy: 0.975
$ env KERAS_BACKEND=torch uv run python 08_migrated.py
backend=torch      test accuracy: 0.981
$ env KERAS_BACKEND=tensorflow uv run python 08_migrated.py
backend=tensorflow test accuracy: 0.978
```

変えたのは 4 か所である。`from tensorflow import keras` → `import keras`、`tf.reduce_mean` などの `tf.*` → `keras.ops.*`（NumPy に近い名前の、どのバックエンドでも動く演算）、`tf.random.set_seed` → `keras.utils.set_random_seed`、`model.save("dir")` → `model.save("x.keras")`（配信用の SavedModel は `model.export`。§7）。

移行後は 3 つのバックエンドで 97.5〜98.1% と、移行前（98.1%）と同等の精度が出た。**学習し直すと、バックエンドごとに数件の差は出る**（§5.2）。予測まで揃えたいときは、学習済みの `.keras` を別のバックエンドで読み込む（§5.4）。
移行の確認は「評価データでの精度が、先に決めた許容範囲に収まるか」で判断する。公式 README も、独自の部品を含まない `tf.keras` のモデルならそのまま JAX や PyTorch で動かせ、含む場合も通常は数分で移せると述べている。

---

## 7. 本番運用の要点

学習の途中経過を `ModelCheckpoint` で残し、配信用に `model.export` で書き出す。3 つのバックエンドで、`tf_saved_model` と `torch` の 2 形式を試した（検証済み）。

```python
import keras

from digits import build_model, load_data

X_tr, _, y_tr, _ = load_data()
model = build_model()
model.compile(optimizer="adam", loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=["accuracy"])
ckpt = keras.callbacks.ModelCheckpoint(
    "ckpt/best.keras", monitor="val_accuracy", mode="max", save_best_only=True)  # 最良の時点だけを残す
history = model.fit(X_tr, y_tr, validation_split=0.2, epochs=30, batch_size=64, verbose=0, callbacks=[ckpt])
val = history.history["val_accuracy"]
best = val.index(max(val))
print(f"best epoch={best + 1}/30  val_accuracy={val[best]:.3f}  -> ckpt/best.keras")

backend = keras.config.backend()
for fmt in ("tf_saved_model", "torch"):
    path = f"export/{backend}_{fmt}" + (".pt2" if fmt == "torch" else "")
    try:
        model.export(path, format=fmt, verbose=False)
        print(f"export format={fmt:14s} OK -> {path}")
    except Exception as e:  # 対応していない組み合わせは例外になる
        print(f"export format={fmt:14s} {type(e).__name__}: {str(e).splitlines()[0][:70]}")
```

実行結果（3 回の実行のログを順に並べた）:

```text
$ env KERAS_BACKEND=jax uv run python 07_checkpoint_export.py
best epoch=29/30  val_accuracy=0.979  -> ckpt/best.keras
export format=tf_saved_model OK -> export/jax_tf_saved_model
export format=torch          ValueError: Torch export requires PyTorch backend.
$ env KERAS_BACKEND=torch uv run python 07_checkpoint_export.py
best epoch=25/30  val_accuracy=0.979  -> ckpt/best.keras
export format=tf_saved_model UserError: Detected mismatch between the structure of `inputs` and `dynamic_shape
export format=torch          OK -> export/torch_torch.pt2
$ env KERAS_BACKEND=tensorflow uv run python 07_checkpoint_export.py
best epoch=30/30  val_accuracy=0.986  -> ckpt/best.keras
export format=tf_saved_model OK -> export/tensorflow_tf_saved_model
export format=torch          ValueError: Torch export requires PyTorch backend.
```

書き出した成果物を、Keras を import せずに各ランタイムだけで読み込んだ（`07b_load_exported.py`）。TensorFlow から書き出した SavedModel は `tf.saved_model.load` で精度 0.967、`.pt2` は `torch.export.load` で精度 0.972 と、どちらも推論できた。JAX から書き出した SavedModel は `InvalidArgumentError` で推論できなかった（下の箇条書き）。

- **`ModelCheckpoint`** は、`save_best_only=True` で監視する指標が最良のときだけ上書きする。`.keras` で終わるパスならモデル全体、`.weights.h5` で終わり `save_weights_only=True` なら重みだけを残す。学習の中断からの再開には、エポック数も残す `BackupAndRestore` がある
- **JAX から書き出した SavedModel は、TensorFlow 2.21 で推論できなかった**。エラーは、JAX 0.12 が書いた StableHLO（v1.18.0）を TensorFlow 側（v1.13.7）が読めないというものである。JAX で学習して TF Serving で配る構成では、書き出した成果物を配信側の版で必ず読み込んで確かめる
- **torch バックエンドからの `tf_saved_model`** は、この版の組み合わせでは `torch.export` の段階で失敗した（3.15.1 のソースでは、この経路は `torch_xla` も必要とする）。`.pt2` は、何も指定しないとバッチの大きさが 1 に固定されて書き出され、2 件を入れると `AssertionError: Guard failed: args_0.size()[0] == 1` になった（`07c_pt2_batch.log`）
- 形式は `tf_saved_model`（既定）・`onnx`・`openvino`・`litert`・`torch` の 5 つで、`torch` は torch バックエンドだけ、`litert` は TensorFlow と torch のバックエンドだけが対応する（3.15.1 のソース）。`onnx` などは追加のパッケージが要るため試していない（公式 docs 準拠・未実行: 追加のパッケージが要る）
- **版を固定する**。Keras は TensorFlow 2.16.1・JAX 0.4.20・PyTorch 2.6.0 以上を求めている（README の対応表）。書き出しは Keras とバックエンドの両方の版に左右される

---

## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `KERAS_BACKEND` を設定したのにバックエンドが変わらない | `import keras` の後に設定している | import より前に設定する（§4.3）。別のライブラリが先に `keras` を import していないかも確かめる |
| JAX で `Explicitly requested dtype int64 … will be truncated to dtype int32` という警告が出る（実測） | JAX は既定で 64 ビット整数を使わない。scikit-learn のラベルは int64 | ラベルを `astype("int32")` にする（§5.1）。64 ビットが要るなら `JAX_ENABLE_X64` を設定する |
| torch バックエンドが遅い（実測） | Mac では自動で MPS を使い、小さなモデルでは転送の手間が勝つ | `with keras.device("cpu"):` で CPU に固定して測る（§5.5） |
| バックエンドを替えると精度が少し変わる（実測） | 同じシードでも、バックエンド・デバイスごとに学習の経過が違う（MPS と CPU では初期値も違った） | 学習し直さず、学習済みの `.keras` を読み込めば予測は揃う（§5.4） |
| `model.save("dir")` で `Invalid filepath extension for saving`、または JAX / torch で `Exception encountered when calling …call()` | Keras 3 の `model.save` は SavedModel を書かない。独自レイヤーの中で `tf.*` を使っている | `.keras` で保存し、配信用は `model.export`。`tf.*` は `keras.ops.*` に置き換える（§6.2・§7） |

---

## 9. 次のステップ

- 下の層と周辺を知る: [JAX](jax.md)（関数変換と TPU）・[PyTorch](pytorch.md)（学習ループを自分で書く）・[TensorFlow](tensorflow.md)（SavedModel・LiteRT）
- 公式の続き: [Introduction to Keras for engineers](https://keras.io/getting_started/intro_to_keras_for_engineers/) と [KerasHub Getting started](https://keras.io/keras_hub/getting_started/)

---

## 出典

| 情報源 | URL |
|---|---|
| Keras 3.15.1 Release | https://github.com/keras-team/keras/releases/tag/v3.15.1 （2026-11-08 確認。`.keras` 展開時の圧縮爆弾対策などの安全性修正） |
| keras-team/keras README | https://github.com/keras-team/keras （2026-11-08 確認。`KERAS_BACKEND` と `keras.json`、`tf.keras` からの移行、各バックエンドの最低版） |
| Getting started with Keras | https://keras.io/getting_started/ （2026-11-08 確認、Context7 `/websites/keras_io` 経由。`tf.keras` と `tf_keras`・`TF_USE_LEGACY_KERAS`、バックエンドごとの環境） |
| Introducing Keras 3.0 / About Keras 3 | https://keras.io/keras_3/ ・ https://keras.io/about/ （2026-11-08 確認、Context7 `/websites/keras_io` 経由。別のバックエンドでの読み込みに関する FAQ、最速のバックエンドはモデルによる） |
| Migrating Keras 2 code to multi-backend Keras 3 | https://keras.io/guides/migrating_to_keras_3/ （2026-11-08 確認、Context7 `/websites/keras_io_guides` 経由。`keras.ops` への置き換え、SavedModel の保存・読み込みの変更、`TFSMLayer`） |
| Keras ガイド（独自レイヤー・保存） | https://keras.io/guides/making_new_layers_and_models_via_subclassing/ ・ https://keras.io/guides/serialization_and_saving/ （2026-11-08 確認、Context7 `/websites/keras_io_guides` 経由。バックエンドに依存しないレイヤー、`.keras` の中身） |
| Keras API（読み込み・書き出し・コールバック・`keras.device`） | https://keras.io/api/models/model_saving_apis/model_saving_and_loading/ ・ https://keras.io/api/models/model_saving_apis/export/ ・ https://keras.io/api/callbacks/model_checkpoint/ ・ https://keras.io/api/callbacks/backup_and_restore/ ・ https://keras.io/api/scope/context_managers/ （2026-11-08 確認、Context7 `/websites/keras_io_api` 経由。`safe_mode`、形式の一覧。対応する組み合わせは 3.15.1 のソース `keras/src/models/model.py` で確認） |
| keras-team/keras-hub README | https://github.com/keras-team/keras-hub （2026-11-08 確認。KerasNLP からの改名、対応バックエンド、Kaggle Models。Hugging Face Hub への複製は DeepWiki で確認） |
| What's new in TensorFlow 2.21 | https://developers.googleblog.com/whats-new-in-tensorflow-221/ （2026-11-08 確認。2026-03-06 公開。Keras 3 / JAX / PyTorch を勧める一文） |
| PyTorch Lightning README / Flax | https://github.com/Lightning-AI/pytorch-lightning ・ https://flax.readthedocs.io/en/latest/ （2026-11-08 確認、Context7 `/lightning-ai/pytorch-lightning`・`/websites/flax_readthedocs_io_en` 経由） |
| GitHub `keras-team/keras` | ★64,416・v3.15.1（2026-07-29 公開）（2026-11-08 に GitHub API で取得） |

### 確認できなかった事項

- **書き出しの回避策**: torch バックエンドからの `tf_saved_model` が `torch_xla` を入れれば動くか、JAX から書き出した SavedModel を TensorFlow 2.21 で読む方法（古い StableHLO を書かせる設定など）。公式の記述を見つけられず、失敗した事実だけを書いた
- **同じシードでもバックエンド・デバイスで初期値や結果が違う理由**。公式の記述を見つけられなかったため、違うという事実だけを書いた
- **§5.2・§5.5 の速度**は、この Mac での小さなモデルの計測である。機種・電源の状態・他の処理で変わる
- 関連: [AI フレームワーク学習ガイド](README.md) / [PyTorch](pytorch.md) / [JAX](jax.md) / [TensorFlow](tensorflow.md)
