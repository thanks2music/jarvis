# JAX 入門 — 関数変換（grad / jit / vmap）で学習を書き、条件を並べて一括で回す

> 出典（一次情報）:
> - [JAX README (github.com)](https://github.com/jax-ml/jax/blob/main/README.md) — JAX の定義と、`grad` / `jit` / `vmap` の位置づけ
> - [Installation (docs.jax.dev)](https://docs.jax.dev/en/latest/installation.html) — 対応プラットフォームの表と、CPU / NVIDIA GPU / TPU の導入コマンド
> - [Just-in-time compilation (docs.jax.dev)](https://docs.jax.dev/en/latest/201/jit.html) — トレース時にだけ走る副作用と、非同期実行の測り方
> - [Flax NNX (flax.readthedocs.io)](https://flax.readthedocs.io/en/latest/) / [Optax (github.com)](https://github.com/google-deepmind/optax) — モデルの部品と、更新の規則
> - [jax-metal (pypi.org)](https://pypi.org/project/jax-metal/) — Apple GPU 用のプラグイン。最終版の日付と対応表
>
> 最終更新: 2026-11-08（JAX 0.12.0.1 で検証。★と最新版は 2026-11-08 時点）

JAX は、NumPy とほぼ同じ書き方の配列計算に「関数を変換する」仕組みを足したライブラリである。微分（`grad`）・コンパイル（`jit`）・バッチ化（`vmap`）は
どれも関数を受け取って新しい関数を返し、自由に重ねられる。[PyTorch 入門](pytorch.md) と同じ題材で身に付ける。地図は [AI フレームワーク学習ガイド](README.md) を参照。

---
## 1. TL;DR

- **JAX は「NumPy 風の配列＋関数変換」である**。`jit(vmap(grad(f)))` のように組み合わせる（§5.2〜§5.4）。
- **NumPy との違い**: 配列は書き換えられず、乱数は「鍵」を渡し、精度の既定は 32 bit（§5.1）。`jit` の中の `print` はトレースのとき（初回と、入力の形や型が変わったとき）にしか走らない（§5.3）。
- 学習は「パラメータを受け取り、新しいパラメータを返す」関数として書く。更新の規則は **Optax**、モデルの部品は **Flax NNX**（§5.5・§5.6）。
- **Mac では CPU 版を使う**。jax-metal（最終版 0.1.1、2024-10-08）は GPU を認識したが、最初の計算で失敗した（§4.3）。
- 実務の強みは **条件だけ違う計算を `vmap` で並べて一度に回すこと**。学習率 8 通りの学習を 1 回の呼び出しで比べた（§6.2）。

---
## 2. 前提知識

- Python の基本（関数・辞書・`lambda`）と NumPy の配列。§5.5 は [PyTorch 入門 §5.2](pytorch.md#52-自動微分--勾配で直線を当てる) の書き直しである。用語は [用語集](README.md#61-基礎学習) を参照

---
## 3. 位置づけと比較

JAX はシリーズの最下層「深層学習の基盤」で、PyTorch と同じ層に並ぶ。本体は配列と関数変換だけで、モデルの部品（Flax）・更新の規則（Optax）・チェックポイント（Orbax）は
別ライブラリである。これらは「JAX AI Stack」として配布され、JAX AI Stack の README には、Google の研究者が Imagen や Gemini の背後のモデルの実装に役立ててきたと書かれている。

| フレームワーク | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **JAX** | 関数変換を自由に組み合わせられる。XLA でコンパイルし、TPU でも動く | 関数型の書き方に慣れが要る。Mac の GPU は使えない（§4.3） | TPU で学習する、Google 系の研究コードを読む、一括計算 |
| NumPy | 配列計算の標準。その場で書き換えられ、64 bit が既定 | 微分・コンパイル・GPU を持たない | 前処理や小さな計算 |
| [PyTorch](pytorch.md) | 書いたとおりに動き、デバッグしやすい。LLM 周辺の主要な OSS が前提 | TPU 上での大規模学習は JAX ほど素直ではない | 迷ったらこれ |
| [Keras 3](keras.md) | 少ないコードで書け、バックエンドに JAX を選べる（§5.7） | 細かい制御は下のフレームワークに降りる | 定番の構成を素早く作る |
| MLX（Apple） | 関数変換の考え方が似ている Apple の配列ライブラリ。公式 docs は PyTorch・JAX・ArrayFire を参考にしたと書く | 対応デバイスは CPU と GPU で、TPU は使えない | Mac でモデルを動かす（[MLX-LM](README.md#2-ドキュメント一覧)） |

> **ポイント**: Transformers は v5 の移行ガイドで「TensorFlow と JAX の部分を取り除く」と明記した。LLM の道具立ては PyTorch が中心で、
> JAX を学ぶ目的は「関数変換という考え方」「TPU」「Google 系のコードの読解」にある。

---
## 4. セットアップ

### 4.1 検証環境とインストール

全体は [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。版は jax / jaxlib 0.12.0.1、flax 0.12.12、optax 0.2.8、numpy 2.5.4、scikit-learn 1.9.1、
Python 3.12.16（jax 0.12.0.1 は Python 3.12 以上が必要）である。Mac では CPU 版を入れる（検証済み）。
```bash
uv init --bare --python 3.12 jax-hello && cd jax-hello
uv python pin 3.12
uv add "jax[cpu]==0.12.0.1" "flax==0.12.12" "optax==0.2.8" scikit-learn numpy
```
公式 docs の CPU の手順は `pip install -U jax` で、`cpu` extra に追加の依存はない。flax は Orbax とその依存も連れてくるため、合計 70 パッケージになった。

> **注意**: プロジェクト名を `jax` にすると、`uv add` が `Requirement name `jax` matches project name `jax`, but self-dependencies are not permitted` で失敗する（実測）。

### 4.2 動作確認

JAX が使うデバイスを確かめる（検証済み）。
```python
import platform
import jax
import jax.numpy as jnp

print("jax:", jax.__version__, "/ python:", platform.python_version())
print("default backend:", jax.default_backend())  # cpu / gpu / tpu
print("devices:", jax.devices())
x = jnp.arange(3.0)
print("x =", x, "| dtype:", x.dtype, "| on:", x.devices())
```
実行結果:
```text
$ uv run python 01_devices.py
jax: 0.12.0.1 / python: 3.12.16
default backend: cpu
devices: [CpuDevice(id=0)]
x = [0. 1. 2.] | dtype: float32 | on: {CpuDevice(id=0)}
```
### 4.3 Apple GPU（jax-metal）は動かなかった

公式のインストール手順は、対応表で Mac の Apple GPU を「experimental」としつつ、Mac GPU の節では「JAX is not supported on Mac/OSX GPU」と書いている。
jax-metal の最終版は 0.1.1（2024-10-08）で、対応表は `jaxlib>=0.4.34` までである。`jax.devices()` と `jnp.arange(4.0)` を実行するだけの `09_jax_metal_try.py` を、`uv run --with` の一時環境で 1 回だけ試した（検証済み）。
```text
$ timeout 180 uv run --with jax-metal==0.1.1 python 09_jax_metal_try.py
…（中略: 11 行）…
jax: 0.12.0.1
devices: [METAL(id=0)]
…（中略: 29 行）…
jax.errors.JaxRuntimeError: UNKNOWN: -:0:0: error: unknown attribute code: 22
-:0:0: note: in bytecode version 6 produced by: StableHLO_v1.16.3
…（中略: 4 行）…
```
「Platform 'METAL' is experimental」の警告のあと `METAL(id=0)` を認識したが、最初の計算（`jnp.arange(4.0)`）で `JaxRuntimeError` になり、終了コード 1 で止まった。以降はすべて CPU で実行した。

---
## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。

### 5.1 `jax.numpy` と NumPy の違い — 書き換えられない配列と、乱数の鍵

`jnp` は NumPy とほぼ同じ関数名で使える。違いが出る 3 点を確かめる（検証済み）。
```python
import jax
import jax.numpy as jnp
import numpy as np

a = np.arange(5)
a[0] = 100                       # NumPy は配列をその場で書き換えられる
print("numpy :", a)
x = jnp.arange(5)
try:
    x[0] = 100                   # JAX の配列は書き換えられない
except TypeError as e:
    print("jax   : TypeError:", str(e).split(".")[0])
y = x.at[0].set(100)             # 書き換えた「新しい配列」を返す
print("x =", x, "/ y =", y)
print("default float:", np.array([1.0]).dtype, "(numpy) vs", jnp.array([1.0]).dtype, "(jax)")
key = jax.random.key(0)          # 乱数の「鍵」。グローバルな乱数の状態は持たない
print("same key twice :", jax.random.normal(key, (3,)), jax.random.normal(key, (3,)))
key, sub1, sub2 = jax.random.split(key, 3)  # 使うたびに鍵を分けて、新しい鍵で引く
print("split keys     :", jax.random.normal(sub1, (3,)), jax.random.normal(sub2, (3,)))
```
実行結果:
```text
$ uv run python 02_arrays_random.py
numpy : [100   1   2   3   4]
jax   : TypeError: JAX arrays are immutable and do not support in-place item assignment
x = [0 1 2 3 4] / y = [100   1   2   3   4]
default float: float64 (numpy) vs float32 (jax)
same key twice : [ 1.6226422   2.0252647  -0.43359444] [ 1.6226422   2.0252647  -0.43359444]
split keys     : [-2.4424558  -2.0356805   0.20554423] [ 1.2956359   1.3550105  -0.40960556]
```
`.at[].set()` は新しい配列を返す（`jit` の中ではその場の更新に最適化される、と公式 docs）。乱数は鍵だけで決まる。同じ鍵で引くと毎回同じ値が出る（上の `same key twice`）。違う値が欲しいときは `split` で新しい鍵を作って使い、最初の鍵（シード）を記録しておけば結果を再現できる。

### 5.2 `grad` — 関数を微分する

`jax.grad(f)` は導関数を計算する関数を返す。パラメータを辞書で渡すと、勾配も同じ形の辞書で返る（検証済み）。
```python
import jax
import jax.numpy as jnp

def f(x):
    return x**3 + 2 * x  # f'(x) = 3x^2 + 2, f''(x) = 6x

df = jax.grad(f)  # 関数を受け取り、導関数（を計算する関数）を返す
print("f'(2.0)  =", df(2.0))  # 3*4 + 2 = 14
print("f''(2.0) =", jax.grad(df)(2.0))  # 変換は重ねられる: 6*2 = 12
# パラメータを辞書で渡すと、勾配も同じ形の辞書で返る
loss = lambda p, x, y: jnp.mean((p["w"] * x + p["b"] - y) ** 2)
x = jnp.array([0.0, 1.0, 2.0])
grads = jax.grad(loss)({"w": 0.0, "b": 0.0}, x, 3 * x + 2)
print("grads:", {k: round(float(v), 4) for k, v in grads.items()})
```
実行結果:
```text
$ uv run python 03_grad.py
f'(2.0)  = 14.0
f''(2.0) = 12.0
grads: {'b': -10.0, 'w': -14.0}
```
辞書・リストの入れ子を JAX は pytree と呼び、変換はその中の配列をまとめて扱う。

### 5.3 `jit` — コンパイルで速くする（`print` が 1 回しか出ない落とし穴）

`jax.jit(f)` は最初の呼び出しで計算の流れを記録（トレース）し、XLA でまとめてコンパイルする（検証済み、速度は参考値）。
```python
import time
import jax
import jax.numpy as jnp

def f(x):  # 要素ごとの小さな計算を 50 回重ねる（演算は 200 回）
    for _ in range(50):
        x = x * 0.9 + jnp.sin(x) * 0.1
    return x

x = jax.random.normal(jax.random.key(0), (10_000,))
fast = jax.jit(f)
for label, fn in [("eager", f)] * 2 + [("jit  ", fast)] * 3:  # jit の 1 回目はコンパイルを含む
    t0 = time.perf_counter()
    fn(x).block_until_ready()  # JAX は非同期に動くので、終わるのを待ってから時間を止める
    print(f"{label}: {(time.perf_counter() - t0) * 1000:6.1f} ms")

@jax.jit
def g(x):
    print("  [print] tracing, x =", x)  # Python の処理はトレースの時にしか走らない
    jax.debug.print("  [debug.print] x = {x}", x=x)  # こちらは実行のたびに走る
    return x * 2

for v in (jnp.array([1.0]), jnp.array([2.0]), jnp.array([1.0, 2.0])):  # 3 回目は形が変わる
    g(v).block_until_ready()
    jax.effects_barrier()  # debug.print の出力を待つ
```
実行結果:
```text
$ uv run python 04_jit.py
eager:   37.9 ms
eager:    3.0 ms
jit  :   68.9 ms
jit  :    0.6 ms
jit  :    0.5 ms
  [print] tracing, x = JitTracer(float32[1])
  [debug.print] x = [1.]
  [debug.print] x = [2.]
  [print] tracing, x = JitTracer(float32[2])
  [debug.print] x = [1. 2.]
```
- **1 回目はコンパイルの分だけ遅く、2 回目からは速い**。`jit` なし（2 回目 3.0 ms）に対し、200 回の演算を 1 回の呼び出しにまとめた `jit` ありは 0.5〜0.6 ms だった。計算は非同期に進むので、`block_until_ready()` で終わりを待って測る
- **`print` は 1 回目しか出ない**。トレース中の `x` は形と型だけの `JitTracer` で、2 回目はコンパイル済みの結果が使われる。**形が変わると**トレースからやり直す（3 回目）

### 5.4 `vmap` — 1 件ぶんの関数をバッチに広げる

`jax.vmap(f)` は、1 件ぶんを前提に書いた関数を、たくさんの入力へまとめて適用する関数に変える（検証済み）。
```python
import jax
import jax.numpy as jnp

def predict_one(w, x):  # 1 件ぶんの入力 x（形は (3,)）だけを考えて書いた関数
    return jnp.tanh(w @ x)

w = jax.random.normal(jax.random.key(0), (4, 3))
xs = jax.random.normal(jax.random.key(1), (2000, 3))  # 2,000 件
batched = jax.vmap(predict_one, in_axes=(None, 0))  # w は共有、xs は 0 軸で分ける
print("one:", predict_one(w, xs[0]).shape, "-> batch:", batched(w, xs).shape)
looped = jnp.stack([predict_one(w, x) for x in xs])  # Python のループで 1 件ずつ
print("same as loop:", bool(jnp.allclose(looped, batched(w, xs))))
# grad と組み合わせると、1 件ごとの勾配が一度に求まる
ys = xs.sum(axis=1)
loss_one = lambda w, x, y: (predict_one(w, x).sum() - y) ** 2
per_example = jax.vmap(jax.grad(loss_one), in_axes=(None, 0, 0))(w, xs, ys)
print("per-example grads:", per_example.shape)
```
実行結果:
```text
$ uv run python 05_vmap.py
one: (4,) -> batch: (2000, 4)
same as loop: True
per-example grads: (2000, 4, 3)
```
`in_axes=(None, 0)` は「`w` は共有、`xs` は 0 番目の軸で 1 件ずつ」の指定である。`vmap(grad(...))` で 1 件ごとの勾配もまとめて求まる。

### 5.5 Optax で線形回帰 — PyTorch 版と書き比べる

PyTorch 版 §5.2 と同じく `y = 3x + 2` のデータから `w` と `b` を当てる。更新の規則（SGD、学習率 0.1）は Optax に任せる（検証済み）。
```python
import jax
import jax.numpy as jnp
import optax

# 正解は y = 3x + 2。ノイズを足した 100 点を作る（乱数は鍵から引く）
x = jnp.linspace(-1, 1, 100).reshape(-1, 1)
y = 3 * x + 2 + 0.1 * jax.random.normal(jax.random.key(0), x.shape)
params = {"w": jnp.zeros(1), "b": jnp.zeros(1)}  # 学習するパラメータ（ただの辞書）
optimizer = optax.sgd(learning_rate=0.1)
opt_state = optimizer.init(params)                # 更新の規則が使う状態も、外で持つ
loss_fn = lambda p: jnp.mean((x * p["w"] + p["b"] - y) ** 2)  # 平均二乗誤差

@jax.jit
def step(params, opt_state):
    loss, grads = jax.value_and_grad(loss_fn)(params)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)  # 新しいパラメータを「返す」
    return params, opt_state, loss

for i in range(200):
    params, opt_state, loss = step(params, opt_state)
    if i % 50 == 0 or i == 199:
        print(f"step {i:3d}  loss={loss:.4f}  w={params['w'][0]:.3f}  b={params['b'][0]:.3f}")
```
実行結果:
```text
$ uv run python 06_optax_linreg.py
step   0  loss=7.1136  w=0.204  b=0.402
step  50  loss=0.0115  w=2.918  b=2.011
step 100  loss=0.0089  w=2.998  b=2.011
step 150  loss=0.0089  w=3.000  b=2.011
step 199  loss=0.0089  w=3.000  b=2.011
```
| 観点 | PyTorch（§5.2） | JAX ＋ Optax |
|---|---|---|
| パラメータ | `requires_grad=True` のテンソル | ただの辞書（pytree） |
| 勾配 | `backward()` で `.grad` に溜まり、`zero_()` で消す | `value_and_grad` が返す。溜まらない |
| 更新と状態 | その場で書き換え、状態は optimizer の中 | 新しいパラメータを返し、`opt_state` も自分で持ち回す |

状態がすべて引数と戻り値に出ているので、`step` 全体を `jit` でき、§6.2 のように `vmap` で並べることもできる（`b` が PyTorch 版の 2.004 と違うのはノイズの乱数が違うため）。

### 5.6 Flax NNX で数字を分類する

Flax NNX は `nn.Module` に近いオブジェクトでモデルを書ける API で、README によると 2024 年に Flax Linen から発展して公開された。Flax の公式ドキュメントは、新しく使う人に NNX を勧めている（Linen も近い将来に非推奨にはならないとしている）。PyTorch 版 §5.3 と同じデータ・構成（64→128→10）・AdamW（1e-3、バッチ 64、30 エポック）で学習する。ただし weight decay の既定値は optax が 1e-4、PyTorch が 0.01 で、完全に同じ設定ではない（検証済み）。
```python
import numpy as np
import optax
from flax import nnx
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

class DigitClassifier(nnx.Module):
    def __init__(self, rngs: nnx.Rngs):
        self.l1 = nnx.Linear(64, 128, rngs=rngs)
        self.l2 = nnx.Linear(128, 10, rngs=rngs)
    def __call__(self, x):
        return self.l2(nnx.relu(self.l1(x)))  # 出力は 10 クラスぶんのスコア（logits）

@nnx.jit  # モデルと optimizer の中の値の更新を、jit の外へ自動で反映する
def train_step(model, optimizer, x, y):
    print("  compiling train_step for batch shape", x.shape)  # トレースの時だけ出る
    loss_fn = lambda m: optax.softmax_cross_entropy_with_integer_labels(m(x), y).mean()
    loss, grads = nnx.value_and_grad(loss_fn)(model)
    optimizer.update(model, grads)  # パラメータをその場で更新する
    return loss
X, y = load_digits(return_X_y=True)  # 8x8 の手書き数字 1,797 枚（scikit-learn に同梱。ダウンロード不要）
X_tr, X_te, y_tr, y_te = train_test_split((X / 16.0).astype(np.float32), y, test_size=0.2, random_state=0)
model = DigitClassifier(nnx.Rngs(0))
optimizer = nnx.Optimizer(model, optax.adamw(1e-3), wrt=nnx.Param)
rng = np.random.default_rng(0)
for epoch in range(30):
    perm = rng.permutation(len(X_tr))  # エポックごとに順番を混ぜる
    for i in range(0, len(X_tr), 64):
        loss = train_step(model, optimizer, X_tr[perm[i : i + 64]], y_tr[perm[i : i + 64]])
acc = (model(X_te).argmax(axis=1) == y_te).mean()
print(f"last loss={loss:.4f}  test accuracy={acc:.3f}")
```
実行結果:
```text
$ uv run python 07_nnx_digits.py
  compiling train_step for batch shape (64, 64)
  compiling train_step for batch shape (29, 64)
last loss=0.1255  test accuracy=0.972
```
- 正解率は PyTorch 版と同じ 97.2%。**コンパイルは 2 回走った**。1,437 件を 64 件ずつに分けると最後だけ 29 件になり、形が変わるためである
- `nnx.jit` はモデルと optimizer の値の更新を関数の外へ自動で反映する。`optimizer.update(model, grads)` が PyTorch の `optimizer.step()` にあたる

### 5.7 Keras 3 の JAX バックエンドとの関係

Keras 3 は同じコードを JAX・TensorFlow・PyTorch の上で動かせる高水準の API で、`KERAS_BACKEND=jax` を設定してから `import keras` すると JAX で動く。
Keras の公式サイトは、自社のベンチマークで JAX が多くの場合もっとも速かった（モデルによる）と書いている。詳しくは [Keras 3](keras.md) を参照。

---
## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | JAX を使う理由 | 本番で足すもの |
|---|---|---|---|
| Google 系の研究コードの読解 | 論文・リポジトリ → 再現コード | JAX AI Stack（JAX・Flax・Optax・Orbax）で書かれている | 依存の版の固定、乱数の鍵の記録 |
| Cloud TPU での学習（未実行） | データ → 学習済みの重み | 公式の対応表で TPU に対応する（`jax[tpu]`） | sharding、Orbax によるチェックポイント |
| 科学計算・最適化での一括探索（§6.2） | 条件の一覧 → 条件ごとの結果 | `grad` と `vmap` を重ね、条件の数だけの計算を 1 回にまとめる | 結果の保存、数値誤差の許容範囲 |
| Keras の高速なバックエンド（§5.7） | Keras のモデル → JAX で実行 | Keras 公式のベンチマークで多くの場合もっとも速い | バックエンドごとの計測 |

### 6.2 代表例: 学習率を 8 通り並べて一度に学習し、検証用データで選ぶ

学習率のような設定値は、データと目的が変わるたびに試して決め直す。条件ごとにスクリプトを回す代わりに、「学習率を 1 つ受け取って学習する関数」を `vmap` で
学習率の配列に広げれば、8 本の学習が 1 回の呼び出しで済む。学習率は**検証用**の正解率で選び、**テスト用**は選んだ 1 本の評価に 1 回だけ使う（検証済み）。
```python
import jax
import jax.numpy as jnp
import numpy as np
import optax
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype(np.float32)
X_rest, X_te, y_rest, y_te = train_test_split(X, y, test_size=0.2, random_state=0)  # テスト用は最後まで触らない
X_tr, X_va, y_tr, y_va = train_test_split(X_rest, y_rest, test_size=0.2, random_state=0)  # 検証用で選ぶ

def predict(params, x):
    return jax.nn.relu(x @ params["w1"] + params["b1"]) @ params["w2"] + params["b2"]

def loss_fn(params, x, y):
    return optax.softmax_cross_entropy_with_integer_labels(predict(params, x), y).mean()

def train(lr, steps=500):  # 学習率 lr で学習し、(検証用の正解率, パラメータ) を返す。lr 以外は全部同じ
    optimizer = optax.adam(lr)
    k1, k2 = jax.random.split(jax.random.key(0))
    params = {"w1": jax.random.normal(k1, (64, 128)) * 0.1, "b1": jnp.zeros(128),
              "w2": jax.random.normal(k2, (128, 10)) * 0.1, "b2": jnp.zeros(10)}
    def step(carry, _):
        params, opt_state = carry
        grads = jax.grad(loss_fn)(params, X_tr, y_tr)
        updates, opt_state = optimizer.update(grads, opt_state)
        return (optax.apply_updates(params, updates), opt_state), None
    (params, _), _ = jax.lax.scan(step, (params, optimizer.init(params)), length=steps)  # Python の for の代わり
    return (predict(params, X_va).argmax(axis=1) == y_va).mean(), params

lrs = jnp.array([1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1])
val_acc, params = jax.jit(jax.vmap(train))(lrs)  # 学習率の軸に沿って、学習全体を 8 本並べる
train_one = jax.jit(train)
looped = [train_one(lr)[0] for lr in lrs]  # 比較用: 1 条件ずつ順番に学習する
for lr, acc, acc_one in zip(lrs, val_acc, looped):
    print(f"lr={lr:7.4f}  val accuracy={acc:.3f}  (one-by-one: {acc_one:.3f})")
best = int(val_acc.argmax())
best_params = jax.tree.map(lambda a: a[best], params)  # 8 本ぶんのパラメータから 1 本を取り出す
test_acc = (predict(best_params, X_te).argmax(axis=1) == y_te).mean()
print(f"best lr={lrs[best]:.4f}  test accuracy={test_acc:.3f}")
```
実行結果:
```text
$ uv run python 08_lr_sweep.py
lr= 0.0001  val accuracy=0.889  (one-by-one: 0.889)
lr= 0.0003  val accuracy=0.965  (one-by-one: 0.965)
lr= 0.0010  val accuracy=0.990  (one-by-one: 0.990)
lr= 0.0030  val accuracy=0.990  (one-by-one: 0.990)
lr= 0.0100  val accuracy=0.986  (one-by-one: 0.986)
lr= 0.0300  val accuracy=0.986  (one-by-one: 0.986)
lr= 0.1000  val accuracy=0.979  (one-by-one: 0.979)
lr= 0.3000  val accuracy=0.594  (one-by-one: 0.580)
best lr=0.0010  test accuracy=0.975
```
- 0.0001 は学び切れず、0.3 は崩れた。0.001 と 0.003 が同点の 99.0% で、`argmax` は先の 0.001 を返し、テスト用は 97.5% だった
- `train` は 1 条件ぶんしか書いていない。`vmap` はパラメータも 8 本ぶん返し、`jax.tree.map` で 1 本を取り出せる。`jax.lax.scan` は `jit` の中で同じ処理を繰り返す関数である

> ⚠️ **`vmap` で並べた結果と 1 本ずつの結果は完全には一致しない**。学習率 0.3 だけ 0.594 と 0.580 に分かれた。パラメータの差を測ると（`08b_sweep_numerics.py`）、
> 1 ステップ目は 3.0e-08〜3.1e-06 と float32 の丸め誤差の大きさで、500 ステップ後は 3.6e-05〜2.3e+01（最大は 0.3）に広がった。小さな誤差が学習の中で増幅されたものと考えられる。
> 誤差で順位が入れ替わらない程度の差があるかを見て選び、選んだ条件は単独で学習し直して確かめる。

### 6.3 その他のユースケースの素描

- **価格・需要モデルの掃引やシナリオ計算**: 1 商品・1 シナリオぶんの関数を `vmap` で並べ、`grad` で利益が増える方向へ価格を動かす。乱数のシナリオは `split` した鍵の配列に `vmap` を当てる

---
## 7. 本番運用の要点

- **GPU / TPU**: NVIDIA GPU は `pip install -U "jax[cuda13]"`（CUDA 12 は `jax[cuda12]`、wheel は Linux 向けだけ）、Cloud TPU は `pip install "jax[tpu]"`（公式 docs 準拠・未実行: NVIDIA GPU と Cloud TPU が必要）
- **入力の形をそろえる**。形が変わるたびにコンパイルが走る（§5.3・§5.6）。端数のバッチは捨てるか、詰め物（padding）で同じ形にする
- **コンパイル結果の再利用**は `jax_compilation_cache_dir`、**64 bit** は起動時の `jax.config.update("jax_enable_x64", True)`、**保存**は Orbax で `nnx.State` を保存・復元する（いずれも公式 docs 準拠・未実行）

---
## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `TypeError: JAX arrays are immutable` | 配列をその場で書き換えようとした | `x = x.at[i].set(v)`（§5.1） |
| `jit` した関数の `print` が 2 回目から出ない（実測） | Python のコードはトレースの時にしか走らない | `jax.debug.print`（§5.3） |
| 時間を測ると異常に速い | 計算が非同期に進む | `block_until_ready()`（§5.3） |
| コンパイルが何度も走る（実測） | 入力の形が呼び出しごとに違う | 形をそろえる（§5.6・§7） |
| 乱数が毎回同じ / `float64` が `float32` になる | 同じ鍵の使い回し / 既定で 64 bit が無効 | `jax.random.split`（§5.1） / `jax_enable_x64`（§7） |
| `uv add` が self-dependency で失敗（実測） | uv のプロジェクト名が `jax` | 名前を変える（§4.1） |
| jax-metal で `JaxRuntimeError`（実測） | jax-metal 0.1.1 と JAX 0.12.0.1 の組み合わせ | CPU 版を使う（§4.3） |
| `vmap` 版と 1 本ずつで結果が少し違う（実測） | 小さな数値誤差の増幅 | 誤差を許容して比べ、選んだ条件は単独で学習し直す（§6.2） |

---
## 9. 次のステップ

- [Keras 3](keras.md) で `KERAS_BACKEND=jax` を試す / [JAX のドキュメント](https://docs.jax.dev/en/latest/) と Flax の [MNIST Tutorial](https://flax.readthedocs.io/en/latest/mnist_tutorial.html) / Mac でモデルを動かすなら [MLX-LM](README.md#2-ドキュメント一覧)

---
## 出典

| 情報源 | URL |
|---|---|
| JAX README | https://github.com/jax-ml/jax/blob/main/README.md （2026-11-08 確認、Context7 `/jax-ml/jax` 経由） |
| Installation | https://docs.jax.dev/en/latest/installation.html （2026-11-08 確認、Context7 `/jax-ml/jax` 経由。対応表と Mac GPU の節、`jax[cuda13]` / `jax[cuda12]` / `jax[tpu]`） |
| PyPI jax 0.12.0.1 / jax-metal | https://pypi.org/project/jax/0.12.0.1/ ・ https://pypi.org/project/jax-metal/ （2026-11-08 確認。`requires_python >=3.12`、`cpu` extra。jax-metal 0.1.1 が 2024-10-08、対応表は `jaxlib>=0.4.34`） |
| JAX arrays / Default dtypes / Common Gotchas | https://docs.jax.dev/en/latest/101/arrays.html ・ https://docs.jax.dev/en/latest/101/default_dtypes.html ・ https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html （2026-11-08 確認、Context7 `/websites/jax_dev_en` 経由） |
| Pseudorandom numbers | https://docs.jax.dev/en/latest/random-numbers.html （2026-11-08 確認、Context7 `/websites/jax_dev_en` 経由） |
| Just-in-time compilation / Compilation cache | https://docs.jax.dev/en/latest/201/jit.html ・ https://docs.jax.dev/en/latest/501/compilation-cache.html （2026-11-08 確認、Context7 `/websites/jax_dev_en` 経由） |
| JAX FAQ | https://docs.jax.dev/en/latest/faq.html （2026-11-08 確認。「jit changes the exact numerics of outputs」） |
| Flax README / Flax NNX docs | https://github.com/google/flax ・ https://flax.readthedocs.io/en/latest/ （2026-11-08 確認、Context7 `/websites/flax_readthedocs_io_en` 経由。`nnx.jit`、`nnx.Optimizer`、Orbax による保存） |
| Optax / JAX AI Stack | https://github.com/google-deepmind/optax ・ https://github.com/jax-ml/jax-ai-stack （2026-11-08 確認、Optax は Context7 `/google-deepmind/optax` 経由） |
| Keras 3 / MLX | https://keras.io/keras_3/ ・ https://ml-explore.github.io/mlx/build/html/index.html （2026-11-08 確認、Context7 `/websites/keras_io` ・ `/websites/ml-explore_github_io_mlx_build_html` 経由） |
| Transformers v5 Migration guide | https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md （2026-11-08 確認） |
| GitHub `jax-ml/jax` | ★36,584・jax-v0.12.0.1（2026-10-22 公開）（2026-11-08 に GitHub API で取得） |

### 確認できなかった事項

- **jax-metal の今後**と、**インストール手順の食い違い**（対応表は「experimental」、Mac GPU の節は「not supported」）について、Apple と JAX の公式の説明は見つけられなかった。PyPI の説明文にある `ENABLE_PJRT_COMPATIBILITY=1` は、1 回だけ試す方針のため試していない
- **`vmap` で数値がずれる理由**。公式 FAQ は `jit` について説明しているが、`vmap` に触れた記述は見つけられなかった。§6.2 の説明は測定からの推定である
- **速度**（§5.3）はこの Mac での 1 回の計測である

- 関連: [AI フレームワーク学習ガイド](README.md) / [PyTorch](pytorch.md) / [Keras 3](keras.md) / [TensorFlow](tensorflow.md) / [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md)
