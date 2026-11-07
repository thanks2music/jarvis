# PyTorch 入門 — テンソルから学習ループ・保存・バッチ推論まで

> 出典（一次情報）:
> - [PyTorch 2.15.0 Release (github.com)](https://github.com/pytorch/pytorch/releases/tag/v2.15.0) — 2.15 の変更点。MPS は macOS 15 以降が必要、wheel は Python 3.11 以上
> - [MPS backend (docs.pytorch.org)](https://docs.pytorch.org/docs/stable/notes/mps.html) — Apple Silicon の GPU を使う方法
> - [torch.accelerator (docs.pytorch.org)](https://docs.pytorch.org/docs/stable/accelerator.html) — CUDA / MPS などを同じコードで扱うための API
> - [Learn the Basics (docs.pytorch.org)](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) — 公式チュートリアル。テンソル・データ・モデル・学習ループの基本形
> - [Serialization semantics (docs.pytorch.org)](https://docs.pytorch.org/docs/stable/notes/serialization.html) — `state_dict` の保存と `weights_only` の安全性
> - [torch.compile (docs.pytorch.org)](https://docs.pytorch.org/docs/stable/generated/torch.compile.html) — コンパイルによる高速化
> - [Transformers v5 Migration guide (github.com)](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) — Transformers v5 が PyTorch だけをバックエンドにしたこと
>
> 最終更新: 2026-11-08（PyTorch 2.15.0 で検証。★と最新版は 2026-11-08 時点）

PyTorch は、Python で数値計算と深層学習を書くための土台である。このシリーズで扱う Transformers・TRL・vLLM・SGLang は、CUDA の環境ではいずれも PyTorch の上に建っている（Mac の vLLM-Metal と SGLang は、計算に Apple の MLX を使う）。LLM を「呼ぶ」だけなら PyTorch を書く場面は少ないが、モデルを選ぶ・動かす・トラブルを調べる場面では、テンソル・dtype・デバイスの感覚が必ず要る。本ドキュメントは、その最小限を手を動かして身に付けることに絞り、分散学習や独自 CUDA カーネルは扱わない。シリーズ全体の地図は [AI フレームワーク学習ガイド](README.md) を参照。

---

## 1. TL;DR

- **PyTorch は「テンソル（多次元配列）＋自動微分＋ニューラルネットの部品」を提供するライブラリ**である。書いたとおりにその場で計算が走る（eager 実行）ため、普通の Python と同じ感覚でデバッグできる。
- **LLM 周辺の主要な OSS が前提にしている**。Transformers・TRL・vLLM・SGLang は CUDA の環境ではいずれも PyTorch の上で動き、Transformers は v5 で TensorFlow と JAX の対応を外して PyTorch だけをバックエンドにした（§3）。
- Mac では **MPS（Apple Silicon の GPU）** が使える。ただし PyTorch 2.15 から **macOS 15 以降が必要**になった。
- **小さなモデルは CPU のほうが速い**。GPU は大きな計算でないと、データ転送と起動の手間を取り返せない（§5.4 で実測）。
- 学習ループは「予測 → 誤差 → `backward()` → `step()`」の 4 行が基本形で、どの規模でも変わらない（§5.3）。
- 実務では、学習より **「保存したモデルを読み込んでバッチ推論する」「LLM のメモリを見積もる」** 場面のほうが多い（§6）。

---

## 2. 前提知識

- **Python の基本**（関数・クラス・`with` 文）。NumPy を触ったことがあれば、テンソルはすぐ分かる
- **行列の掛け算**のイメージ。ニューラルネットの計算のほとんどは行列の掛け算である
- **「学習」とは、誤差が小さくなる方向へパラメータを少しずつ動かすこと**。その方向を求めるのが勾配（微分）である
- テンソル・dtype・勾配・バッチ・エポックなどの用語は、索引の [用語集](README.md#61-基礎学習) にまとめた

---

## 3. 位置づけと比較

PyTorch はシリーズの最下層「深層学習の基盤」にあたる。入力はデータとモデルの定義、出力は学習済みの重み（`state_dict` や safetensors 形式のファイル）である。上の層の Transformers は、この重みを読み込んで使う。

| フレームワーク | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **PyTorch** | 書いたとおりに動き、デバッグしやすい。LLM 周辺の主要な OSS が前提にしている | Apple Silicon の GPU（MPS）では、未対応の演算が残っている（§8） | 迷ったらこれ。LLM 周辺の道具を使うなら事実上の前提 |
| [JAX](jax.md) | 関数変換（`jit` / `grad` / `vmap`）と TPU。Google 系の研究コード | 状態を持たない関数型の書き方に慣れが要る | TPU で学習する、Google 系のコードを読む |
| [Keras 3](keras.md) | 少ないコードで書ける。バックエンドに JAX / PyTorch / TensorFlow を選べる | 細かい制御は下のフレームワークに降りる必要がある | 定番の構成を素早く作る、バックエンドを後で決めたい |
| [TensorFlow](tensorflow.md) | 既存の SavedModel・TF Serving・LiteRT（旧 TF Lite）の資産 | 2026-03 から保守中心になった。新しい生成 AI の開発には Google 自身が Keras 3 / JAX / PyTorch を勧めている | 既存の TensorFlow 資産を保守する |
| MLX（Apple） | Apple Silicon のメモリ構造に合わせた配列ライブラリ。vLLM-Metal と SGLang の Mac 対応も MLX を計算に使う | 学習用の部品や周辺ツールは PyTorch より少ない | Mac で LLM を動かす（[MLX-LM](README.md#2-ドキュメント一覧) で扱う） |

PyTorch Lightning や Hugging Face Accelerate は、学習ループの定型部分（ログ・チェックポイント・複数 GPU）を肩代わりするラッパーである。まず素の 4 行の基本形（§5.3）を理解してから使うと、問題が起きたときに読める。

---

## 4. セットアップ

### 4.1 検証環境

検証環境の全体（ハードウェア・uv の方針・モデル）は索引の [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。本ドキュメント固有の版は次のとおり。

| 項目 | 版 |
|---|---|
| torch | 2.15.0 |
| numpy / scikit-learn | 2.5.4 / 1.9.1 |
| transformers（§5.7 だけで使う） | 5.22.2 |
| Python | 3.12.16（uv で管理） |

### 4.2 インストール

Mac 用の wheel には MPS 対応が最初から入っている（検証済み）。

```bash
uv init --bare --python 3.12 pytorch-hello && cd pytorch-hello
uv python pin 3.12
uv add "torch==2.15.0" scikit-learn numpy
```

NVIDIA GPU の Linux では、CUDA の版に合った wheel を [公式のインストール表](https://pytorch.org/get-started/locally/) で選ぶ。
2.15 の既定の wheel は CUDA 13.2 向けである（公式 docs 準拠・未実行: NVIDIA GPU が必要）。

> **注意**: PyTorch 2.15 は Python 3.10 向けの wheel を配布しなくなった。また MPS は macOS 15 以降でないと使えず、macOS 14 では `torch.backends.mps.is_available()` が `False` を返す（2.15.0 のリリースノートより）。

### 4.3 動作確認

使えるアクセラレータ（GPU など）を調べる（検証済み）。

```python
import platform

import torch

print("torch:", torch.__version__)
print("python:", platform.python_version())
print("accelerator available:", torch.accelerator.is_available())
acc = torch.accelerator.current_accelerator(check_available=True)
print("current accelerator:", acc)  # cuda / mps / None
print("mps built:", torch.backends.mps.is_built(), "/ mps available:", torch.backends.mps.is_available())
```

実行結果:

```text
$ uv run python 01_env_check.py
torch: 2.15.0
python: 3.12.16
accelerator available: True
current accelerator: mps
mps built: True / mps available: True
```

`torch.accelerator` は、CUDA でも MPS でも同じ書き方でデバイスを取れる API で、`torch.cuda` と `torch.backends.mps` で分岐を書く必要が無くなった。

---

## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。

### 5.1 テンソル — 形・dtype・デバイス

テンソルの基本操作と、精度（dtype）・置き場所（デバイス）の変え方を見る（検証済み）。

```python
import torch

device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"

x = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])  # 2x3 の行列
print("shape:", x.shape, "dtype:", x.dtype, "device:", x.device)

y = x * 10 + torch.tensor([1.0, 2.0, 3.0])  # ブロードキャスト: 1x3 が各行に足される
print("broadcast:\n", y)

print("matmul (2x3 @ 3x2):\n", x @ x.T)

x_dev = x.to(device)                 # 別のデバイスへコピー
x_bf16 = x_dev.to(torch.bfloat16)    # 精度を下げてメモリを半分に
print("on device:", x_dev.device, "| bf16 bytes/elem:", x_bf16.element_size(), "vs fp32:", x.element_size())

n = x.numpy()                        # CPU のテンソルは NumPy と相互変換できる
print("numpy:", type(n).__name__, n.sum())
```

実行結果:

```text
$ uv run python 02_tensors.py
shape: torch.Size([2, 3]) dtype: torch.float32 device: cpu
broadcast:
 tensor([[11., 22., 33.],
        [41., 52., 63.]])
matmul (2x3 @ 3x2):
 tensor([[14., 32.],
        [32., 77.]])
on device: mps:0 | bf16 bytes/elem: 2 vs fp32: 4
numpy: ndarray 21.0
```

- **dtype** は 1 要素あたりのバイト数を決める。fp32 は 4 バイト、bf16 は 2 バイトである。LLM のメモリ見積もりはこの数字から始まる（§5.7）
- **デバイスが違うテンソル同士は計算できない**。`.to(device)` で同じ場所に揃える。実務で最も多いエラーの 1 つである（§8）

### 5.2 自動微分 — 勾配で直線を当てる

`requires_grad=True` を付けたテンソルは、計算の過程が記録され、`backward()` で勾配が求まる。正解が `y = 3x + 2` のデータから、`w` と `b` を当ててみる（検証済み）。

```python
import torch

torch.manual_seed(0)
# 正解は y = 3x + 2。ノイズを足した 100 点を作る
x = torch.linspace(-1, 1, 100).unsqueeze(1)
y = 3 * x + 2 + 0.1 * torch.randn_like(x)

w = torch.zeros(1, requires_grad=True)  # 学習するパラメータ
b = torch.zeros(1, requires_grad=True)
lr = 0.1

for step in range(200):
    pred = x * w + b
    loss = ((pred - y) ** 2).mean()     # 平均二乗誤差
    loss.backward()                     # w.grad と b.grad が計算される
    with torch.no_grad():               # 更新そのものは勾配の記録に含めない
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_()
    b.grad.zero_()
    if step % 50 == 0 or step == 199:
        print(f"step {step:3d}  loss={loss.item():.4f}  w={w.item():.3f}  b={b.item():.3f}")
```

実行結果:

```text
$ uv run python 03_autograd.py
step   0  loss=7.0857  w=0.204  b=0.401
step  50  loss=0.0132  w=2.917  b=2.004
step 100  loss=0.0105  w=2.997  b=2.004
step 150  loss=0.0105  w=3.000  b=2.004
step 199  loss=0.0105  w=3.000  b=2.004
```

ニューラルネットの学習も、パラメータの数が何十億に増えるだけで仕組みは同じである。勾配は足し込まれていくため、毎回 `zero_()` で消す。

### 5.3 学習ループ — `nn.Module` と DataLoader で数字を分類する

実際の開発では、パラメータを手で管理せず、`nn.Module`（モデル）・`DataLoader`（データを小分けに渡す）・`optimizer`（更新の規則）を使う。scikit-learn に同梱の手書き数字（8×8 ピクセル、1,797 枚）を 10 クラスに分類する。このファイルは §5.5 と §6.2 でも読み込むので、`digits.py` として置く（検証済み）。

```python
import time

import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class DigitClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10))

    def forward(self, x):
        return self.net(x)  # 出力は 10 クラスぶんのスコア（logits）


def load_data():
    digits = load_digits()  # 8x8 の手書き数字 1,797 枚（scikit-learn に同梱。ダウンロード不要）
    X = torch.tensor(digits.data / 16.0, dtype=torch.float32)
    y = torch.tensor(digits.target)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
    return TensorDataset(X_tr, y_tr), TensorDataset(X_te, y_te)


def train(device: str, epochs: int = 30) -> DigitClassifier:
    torch.manual_seed(0)
    train_ds, test_ds = load_data()
    loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    model = DigitClassifier().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    start = time.perf_counter()
    for _ in range(epochs):
        model.train()
        for X, y in loader:
            X, y = X.to(device), y.to(device)
            loss = loss_fn(model(X), y)  # 1. 予測して誤差を測る
            optimizer.zero_grad()        # 2. 前回の勾配を消す
            loss.backward()              # 3. 勾配を計算する
            optimizer.step()             # 4. パラメータを更新する
    elapsed = time.perf_counter() - start

    model.eval()
    X_te, y_te = test_ds.tensors
    with torch.inference_mode():
        acc = (model(X_te.to(device)).argmax(dim=1).cpu() == y_te).float().mean().item()
    print(f"device={device:4s}  last loss={loss.item():.4f}  test accuracy={acc:.3f}  train time={elapsed:.2f}s")
    return model
```

CPU と MPS で同じ学習を回す（検証済み）。

```python
import torch

from digits import train

train("cpu")
if torch.backends.mps.is_available():
    train("mps")
```

実行結果:

```text
$ uv run python 04_train_digits.py
device=cpu   last loss=0.0559  test accuracy=0.972  train time=0.43s
device=mps   last loss=0.0559  test accuracy=0.972  train time=1.52s
```

テスト用データで 97.2% を当てた。`model.train()` と `model.eval()` は Dropout などの振る舞いを切り替えるもので、勾配の記録を止める `torch.inference_mode()` とは別物である（公式 docs も、`inference_mode` は eval モードに切り替えないと明記している）。

### 5.4 CPU と GPU のどちらが速いか

§5.3 では、MPS のほうが CPU より 3 倍以上遅かった。計算が小さすぎて、GPU にデータを送る手間と処理を起動する手間が、計算そのものより大きいためである。行列の大きさを変えて、行列の掛け算 1 回の時間を測った（検証済み、参考値）。

```python
import time

import torch


def sync(device: str) -> None:
    if device != "cpu":
        torch.accelerator.synchronize()


def bench(device: str, n: int, iters: int = 20) -> float:
    a = torch.randn(n, n, device=device)
    b = torch.randn(n, n, device=device)
    a @ b  # ウォームアップ
    sync(device)
    start = time.perf_counter()
    for _ in range(iters):
        a @ b
    sync(device)  # GPU は非同期に動くので、終わるのを待ってから時間を測る
    return (time.perf_counter() - start) / iters * 1000


devices = ["cpu"] + (["mps"] if torch.backends.mps.is_available() else [])
for n in (64, 512, 4096):
    print(f"{n:5d}x{n:<5d}", "   ".join(f"{dev}={bench(dev, n):8.3f} ms" for dev in devices))
```

実行結果:

```text
$ uv run python 04b_matmul_bench.py
   64x64    cpu=   0.002 ms   mps=   0.062 ms
  512x512   cpu=   0.163 ms   mps=   0.181 ms
 4096x4096  cpu=  69.143 ms   mps=  12.579 ms
```

小さな行列では CPU が速く、大きな行列では MPS が速い。LLM の推論は巨大な行列の掛け算の連続なので GPU が効くが、小さなモデルの学習は「GPU にすれば速くなる」と決めつけず、測ってから選ぶ。GPU は非同期に動くので、`sync()` で終わりを待ってから時間を止める（§8）。

### 5.5 保存と読み込み — `state_dict`

学習済みモデルは、重みの辞書（`state_dict`）だけを保存するのが公式の推奨である。モデルのクラスはコードの側に置く（検証済み）。

```python
import torch

from digits import DigitClassifier, load_data, train

model = train("cpu")
torch.save({"model": model.state_dict(), "classes": list(range(10))}, "digits.pt")  # 重みだけを保存する

restored = DigitClassifier()
ckpt = torch.load("digits.pt", weights_only=True)  # 任意のコードを実行させにくくするため weights_only を使う
restored.load_state_dict(ckpt["model"])
restored.eval()

X_te, _ = load_data()[1].tensors
with torch.inference_mode():
    same = torch.equal(model(X_te), restored(X_te))
print("saved keys:", list(ckpt["model"].keys()))
print("restored model gives identical outputs:", same)
```

実行結果:

```text
$ uv run python 05_save_load.py
device=cpu   last loss=0.0559  test accuracy=0.972  train time=0.38s
saved keys: ['net.0.weight', 'net.0.bias', 'net.2.weight', 'net.2.bias']
restored model gives identical outputs: True
```

> ⚠️ **他人が配布した `.pt` / `.pth` ファイルは、`weights_only=False` で読まない**。`torch.load` は内部で pickle を使うため、
> 悪意のあるファイルを読むと任意のコードが実行され得る。PyTorch 2.6 から `weights_only=True` が既定になった。
> ただし `weights_only=True` も攻撃の余地を狭めるだけで、DoS などは防げないと公式は書いている。出所の分からないファイルは、そもそも読まない。
> Hugging Face Hub のモデルは、コードを含まない safetensors 形式で配布されるのが一般的である。

### 5.6 `torch.compile` — コードを変えずに速くする

`torch.compile(model)` で包むと、最初の呼び出しで計算のグラフを捕まえ、まとめて最適化したコードに置き換える（検証済み、参考値）。

```python
import time

import torch
from torch import nn

torch.manual_seed(0)
model = nn.Sequential(nn.Linear(1024, 4096), nn.GELU(), nn.Linear(4096, 1024)).eval()
x = torch.randn(256, 1024)
compiled = torch.compile(model)  # 最初の呼び出しでグラフを捕まえて最適化する


def bench(fn, n=50):
    with torch.inference_mode():
        fn(x)  # ウォームアップ（compile はここでコンパイルが走る）
        start = time.perf_counter()
        for _ in range(n):
            fn(x)
    return (time.perf_counter() - start) / n * 1000


with torch.inference_mode():
    t0 = time.perf_counter()
    compiled(x)
    print(f"first compiled call (includes compilation): {time.perf_counter() - t0:.1f}s")
    print("outputs match:", torch.allclose(model(x), compiled(x), atol=1e-5))
print(f"eager:    {bench(model):.2f} ms/iter")
print(f"compiled: {bench(compiled):.2f} ms/iter")
```

実行結果（コンパイルのキャッシュを消した状態から実行）:

```text
$ uv run python 06_compile.py
first compiled call (includes compilation): 5.7s
outputs match: True
eager:    4.42 ms/iter
compiled: 4.12 ms/iter
```

- 初回はコンパイルに数秒かかる（2 回目以降の実行はキャッシュが効き、1.7 秒に縮んだ）。この小さなモデルでは 1 割弱しか速くならず、効果はモデルの形と規模で変わるので、本番の前に測る
- MPS でも動き、出力も一致した（`06b_compile_mps.py` で確認）

### 5.7 Hugging Face のモデルも `nn.Module` である — メモリを見積もる

Transformers で読み込む LLM も、中身は §5.3 と同じ `nn.Module` である。パラメータ数と dtype から、重みが占めるメモリを見積もれる。ここだけ `transformers==5.22.2` を追加し、Qwen3-0.6B（Apache-2.0）を読み込む（検証済み）。

```python
import torch
from torch import nn
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.bfloat16)
print("is nn.Module:", isinstance(model, nn.Module))
print("top-level children:", [name for name, _ in model.named_children()])

n_params = sum(p.numel() for p in model.parameters())
print(f"parameters: {n_params / 1e9:.3f} B")
for label, nbytes in (("fp32", 4), ("bf16", 2), ("int8", 1), ("4bit", 0.5)):
    print(f"  weights in {label}: {n_params * nbytes / 1024**3:5.2f} GiB")

# 同じ計算を大きなモデルに当てはめる（重みだけ。推論中は KV キャッシュなどが上乗せされる）
for size_b in (8, 32, 70):
    print(f"  {size_b}B model in bf16 ≈ {size_b * 1e9 * 2 / 1024**3:.0f} GiB, in 4bit ≈ {size_b * 1e9 * 0.5 / 1024**3:.0f} GiB")
```

実行結果:

```text
$ uv run python 07_hf_model_as_module.py
…（中略: macOS での警告 1 行と、読み込みの進捗表示 1 行）…
is nn.Module: True
top-level children: ['model', 'lm_head']
parameters: 0.596 B
  weights in fp32:  2.22 GiB
  weights in bf16:  1.11 GiB
  weights in int8:  0.56 GiB
  weights in 4bit:  0.28 GiB
  8B model in bf16 ≈ 15 GiB, in 4bit ≈ 4 GiB
  32B model in bf16 ≈ 60 GiB, in 4bit ≈ 15 GiB
  70B model in bf16 ≈ 130 GiB, in 4bit ≈ 33 GiB
```

**「パラメータ数 × 1 要素のバイト数」が重みのメモリ**である。70B のモデルは bf16 では 130GiB を超えて 96GB の Mac には載らないが、4bit に量子化すれば載る。推論中はこれに KV キャッシュ（会話の履歴ぶんの中間結果）が上乗せされる。量子化と KV キャッシュは、推論・配信の層（vLLM / SGLang / MLX-LM）で扱う。

---

## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | PyTorch を使う理由 | 本番で足すもの |
|---|---|---|---|
| 小さな分類・回帰モデル | 表データ・画像 → ラベル・数値 | 学習ループを自分で制御できる。LLM を呼ぶより安く速い | 評価指標の監視、再学習の仕組み、モデルの版管理 |
| 学習済みモデルのバッチ推論（§6.2） | CSV・画像の束 → 予測と確信度 | 推論専用モードとバッチ化で、普通のスクリプトとして回せる | ジョブの再実行、入力の検証、結果の保存先 |
| LLM を選ぶ前のメモリ見積もり（§5.7） | モデル名 → 必要なメモリ | パラメータ数と dtype から即座に計算できる | KV キャッシュぶんの上乗せ（推論の層で扱う） |
| 論文・OSS 実装の読解と再現 | 論文・リポジトリ → 動く再現コード | 公開されている実装を読むには、テンソル・`nn.Module`・学習ループの読み方が要る | 乱数の固定、依存の版の固定 |
| 上の層のトラブル調査 | エラーメッセージ → 原因 | Transformers や vLLM のエラーの多くは dtype・デバイス・メモリの問題である | §8 の表 |

### 6.2 代表例: 確信度の低いものだけを人に回すバッチ推論

学習済みモデルを業務に組み込むとき、全件を機械に任せず「**確信度が低いものだけ人が確認する**」形にすることが多い。問い合わせの自動分類や、画像による検品と同じ形である。§5.5 で保存した `digits.pt` を読み込み、CSV を一括で推論する（検証済み）。

```python
"""保存したモデルで CSV を一括推論し、確信度の低い行を人の確認に回す。"""
import argparse
import csv

import torch
from torch.utils.data import DataLoader, TensorDataset

from digits import DigitClassifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    parser.add_argument("--checkpoint", default="digits.pt")
    parser.add_argument("--threshold", type=float, default=0.9)
    args = parser.parse_args()

    device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
    model = DigitClassifier()
    model.load_state_dict(torch.load(args.checkpoint, weights_only=True)["model"])
    model.to(device).eval()

    with open(args.input_csv) as f:
        rows = list(csv.DictReader(f))
    features = torch.tensor([[float(r[f"px{i}"]) for i in range(64)] for r in rows])
    loader = DataLoader(TensorDataset(features), batch_size=256)

    results = []
    with torch.inference_mode():  # 勾配を記録しない推論専用モード（速く、メモリも少ない）
        for (X,) in loader:
            probs = torch.softmax(model(X.to(device)), dim=1).cpu()
            conf, pred = probs.max(dim=1)
            results += list(zip(pred.tolist(), conf.tolist()))

    review = 0
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "prediction", "confidence", "needs_review"])
        for row, (pred, conf) in zip(rows, results):
            needs_review = conf < args.threshold
            review += needs_review
            writer.writerow([row["id"], pred, f"{conf:.3f}", needs_review])
    print(f"device={device} rows={len(rows)} needs_review={review} (threshold={args.threshold})")


if __name__ == "__main__":
    main()
```

入力には、テスト用データ 360 件を `id, px0, …, px63` の列を持つ CSV に書き出したものを使った。値は §5.3 と同じく 16 で割って 0〜1 にしてある。

> **注意**: **前処理は、学習と推論で必ず揃える**。このスクリプトは前処理をしないので、16 で割る前の生の値を渡すと、エラーにならずに誤った予測を返す。しかも確信度が高く出ることがあり、要確認の振り分けもすり抜ける。前処理はモデルの側か、学習と推論で共有する関数に置く。

実行結果:

```text
$ uv run python 08_batch_predict.py new_samples.csv predictions.csv --threshold 0.9
device=mps rows=360 needs_review=67 (threshold=0.9)
```

360 件のうち 67 件が「要確認」に回った。正解ラベルと突き合わせると、次のように誤りが要確認の側に集まっていた（`08b_check_review_split.py` で集計）。

| 区分 | 件数 | 誤り | 正解率 |
|---|---|---|---|
| 機械に任せた（確信度 0.9 以上） | 293 | 1 | 99.7% |
| 人の確認に回した（確信度 0.9 未満） | 67 | 9 | 86.6% |

誤り 10 件のうち 9 件を人の確認で拾える。しきい値を上げれば確認の手間が増え、下げれば誤りが機械の側に残る。

> **ポイント**: softmax の値は「モデル自身の自信」であって、正しさの確率そのものではない。しきい値は誤りのコストと確認の手間を比べて業務ごとに決め、本番の前に、この表のように正解の分かっているデータで誤りの残り方を確かめる。

### 6.3 その他のユースケースの素描

- **社内データでの小さな分類器**: 問い合わせのカテゴリなど出力が決まった種類のラベルなら、LLM を毎回呼ぶより小さなモデルのほうが安く、速く、結果も安定する。文章を数値にする部分（埋め込み）は [Transformers](README.md#2-ドキュメント一覧) に任せ、その上に §5.3 の分類器を載せる。API で済ませるかの判断は [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md) と合わせて考える

---

## 7. 本番運用の要点

- **推論では必ず `model.eval()` を呼ぶ**。忘れると Dropout などが学習時の振る舞いのままになる。勾配の記録は `torch.inference_mode()`（速く、メモリも少ない）か `torch.no_grad()` で止める。`inference_mode` の中で作ったテンソルは学習の計算には使えないので、その場合は `no_grad` を使う
- **乱数と版を固定する**。`torch.manual_seed` に加え、`torch` と CUDA の版を固定する。それでも公式は、版・プラットフォームをまたいだ完全な再現や、CPU と GPU の間での一致は保証しないと書いている。厳密に揃えたい場合は `torch.use_deterministic_algorithms(True)` などを使う（[Reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)）
- **NVIDIA GPU の本番環境**では、CUDA の版・ドライバ・`torch` の wheel を揃える必要がある。コンテナで固定するのが一般的である（公式 docs 準拠・未実行: NVIDIA GPU が必要）
- **配信**（多数の利用者からのリクエストを捌く）は、素の PyTorch で書くより、vLLM や SGLang のような推論サーバーに任せる

---

## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| `Expected all tensors to be on the same device` | モデルと入力が別のデバイスにある | 入力も `.to(device)` で揃える（§5.1） |
| MPS にしたら遅くなった（実測） | 計算が小さく、転送と起動の手間が勝つ | 大きさを変えて測る（§5.4）。小さなモデルは CPU で十分 |
| `torch.backends.mps.is_available()` が `False` | PyTorch 2.15 は macOS 15 以降が必要 | macOS を上げるか、PyTorch 2.14 を使う |
| 時間を測ると GPU が異常に速い | GPU の処理が終わる前に時間を止めている | `torch.accelerator.synchronize()` を挟む（§5.4） |
| 損失が下がらない・発散する | 勾配を消し忘れて足し込まれている、学習率が大きすぎる | `optimizer.zero_grad()` を毎回呼ぶ。学習率を 1/10 にして試す |
| `UnpicklingError: Weights only load failed` | `weights_only=True` で読めない独自のクラスが保存されている | 信頼できるファイルに限り、エラー文の手順で許可リストに追加する。可能なら `state_dict` で保存し直す |
| MPS で未対応の演算というエラーが出る | MPS にまだ実装されていない演算がある | `PYTORCH_ENABLE_MPS_FALLBACK=1` でその演算だけ CPU に回せる（遅くなる） |

---

## 9. 次のステップ

- LLM を動かす: [Transformers](README.md#2-ドキュメント一覧) で、§5.7 のモデルを実際に推論させる
- 別の書き方を知る: [JAX](jax.md)（関数変換）と [Keras 3](keras.md)（バックエンドを選べる高水準 API）
- 公式チュートリアルの続き: [Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) の「Optimizing Model Parameters」「Save and Load the Model」

---

## 出典

| 情報源 | URL |
|---|---|
| PyTorch 2.15.0 Release | https://github.com/pytorch/pytorch/releases/tag/v2.15.0 （2026-11-08 確認。MPS の macOS 15 要件・Python 3.10 wheel の廃止・CUDA 13.2 既定・MPS 向けの compile 修正） |
| MPS backend | https://docs.pytorch.org/docs/stable/notes/mps.html （2026-11-08 確認、Context7 `/websites/pytorch` 経由） |
| MPS Environment Variables | https://docs.pytorch.org/docs/stable/mps_environment_variables.html （2026-11-08 確認。`PYTORCH_ENABLE_MPS_FALLBACK`） |
| torch.accelerator | https://docs.pytorch.org/docs/stable/accelerator.html （2026-11-08 確認） |
| Learn the Basics | https://docs.pytorch.org/tutorials/beginner/basics/intro.html （2026-11-08 確認） |
| Serialization semantics | https://docs.pytorch.org/docs/stable/notes/serialization.html （2026-11-08 確認。2.6 から `weights_only=True` が既定） |
| torch.autograd.grad_mode.inference_mode | https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html （2026-11-08 確認。eval モードには切り替えない旨） |
| torch.compile | https://docs.pytorch.org/docs/stable/generated/torch.compile.html （2026-11-08 確認） |
| Start Locally | https://pytorch.org/get-started/locally/ （2026-11-08 確認） |
| Transformers v5 Migration guide | https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md （2026-11-08 確認、Context7 `/huggingface/transformers` 経由。TensorFlow と JAX の除去） |
| GitHub `pytorch/pytorch` | ★105,233・v2.15.0（2026-10-28 公開）（2026-11-08 に GitHub API で取得） |

### 確認できなかった事項

- **MPS 上の `torch.compile` の成熟度**。2.15 のリリースノートには MPS 向けの個別の修正が並ぶが、「どこまで実用段階か」を述べた公式の記述は見つけられなかった。本ドキュメントでは、小さなモデルで動作と出力の一致を確かめた事実だけを書いた
- **§5.4・§5.6 の速度**は、この Mac での 1 回の計測である。機種・電源の状態・他の処理で変わる

- 関連: [AI フレームワーク学習ガイド](README.md) / [JAX](jax.md) / [Keras 3](keras.md) / [TensorFlow](tensorflow.md) / [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md)
