# TRL + PEFT 入門 — LoRA で小さなモデルに仕事を教え、配信できる形にするまで

> 出典（一次情報）:
> - [TRL documentation (huggingface.co)](https://huggingface.co/docs/trl/index) — TRL の全体と、SFT / DPO / GRPO などの学習方法
> - [SFT Trainer (huggingface.co)](https://huggingface.co/docs/trl/sft_trainer) — データの形式、`assistant_only_loss`、学習率の目安
> - [PEFT Integration (huggingface.co)](https://huggingface.co/docs/trl/peft_integration) — TRL と PEFT の組み合わせ方、LoRA の学習率は約 10 倍、アダプタの保存と統合
> - [LoRA Without Regret (huggingface.co)](https://huggingface.co/docs/trl/lora_without_regret) — LoRA を全部の線形層に付けるべき理由
> - [GRPO Trainer (huggingface.co)](https://huggingface.co/docs/trl/grpo_trainer) — 報酬関数の書き方
> - [PEFT documentation (huggingface.co)](https://huggingface.co/docs/peft/index) — LoRA などの「一部だけ学習する」方法の本体
> - [LoRA Adapters (docs.vllm.ai)](https://docs.vllm.ai/en/latest/features/lora.html) — 学習したアダプタを vLLM で配信する方法
>
> 最終更新: 2026-11-08（trl v1.17.1・peft v0.21.2 で検証。★と最新版は 2026-11-08 時点）

TRL は、公開された LLM を自前のデータで追加学習（ファインチューニング）するための Hugging Face のライブラリである。
PEFT は、モデル全体ではなく一部の小さな重みだけを学習する方法（代表が LoRA）をまとめたライブラリで、TRL と組み合わせて使う。
シリーズでは 2 層目の「モデルと学習」にあたり、[Transformers](transformers.md) で読み込んだモデルを学習させ、その結果を上の推論サーバーに渡す。
本ドキュメントは、[Transformers の §5.6](transformers.md#56-バッチで問い合わせを分類する) で 0.6B のモデルができなかった問い合わせの分類を、LoRA で教えるところまでを扱う。
複数 GPU での学習や、ゼロからの事前学習は扱わない。シリーズ全体の地図は [AI フレームワーク学習ガイド](README.md) を参照。

---

## 1. TL;DR

- **まず、追加学習が本当に要るかを確かめる**。プロンプトの工夫、資料を検索して渡す方法（RAG）、一段大きなモデルで足りるなら、学習は要らない（§3.1）。
- **TRL は学習の手順（SFT・DPO・GRPO など）を、PEFT は「一部だけ学習する」仕組み（LoRA など）を受け持つ**。`SFTTrainer` に `LoraConfig` を渡すだけで組み合わせられる。
- **LoRA なら、学習するパラメータは全体の 1〜2% で済む**。0.6B のモデルで約 1,000 万個、保存したアダプタは 40MB だった（§5.2・§5.4）。
- **48 件の例を MPS で 23 秒学習させただけで、0.6B の分類の正解率が 17% から 67% に上がった**。学習していない 4B は 75% で、統合後の 0.6B はそれより約 5 倍速い（§5.5・§6.2）。
- **学習と評価で精度（dtype）を揃える**。揃えないと、同じアダプタで正解率が 67% から 58% に下がった（§5.5）。
- **アダプタは元の重みに統合（merge）すると、普通のモデルとして推論サーバーに渡せる**。統合せずに vLLM の `--enable-lora` で載せる方法もある（§5.6）。

---

## 2. 前提知識

- **[Transformers](transformers.md) で、モデルの読み込み・チャットテンプレート・`generate()` を動かしたことがある**
- **[PyTorch](pytorch.md) の学習ループの考え方**（誤差を測り、誤差が小さくなる方向へ重みを少し動かす）
- **学習データと評価データを分ける理由**。学習に使った例で測ると、暗記しただけでも正解率が高く見える
- SFT・DPO・GRPO・LoRA・アダプタ・量子化などの用語は、索引の [用語集](README.md#62-モデルファインチューニング) にまとめた

---

## 3. 位置づけと比較

### 3.1 その前に: 追加学習が要るかを確かめる

追加学習は、データを用意し、学習させ、評価し、学習済みのモデルを管理し続ける手間がかかる。次の順に試し、足りなかったときだけ学習に進むのがよい（本シリーズの推奨。各手段の効果は §5・[Transformers](transformers.md) の実測による）。

| 順 | 手段 | 効く場面 | 本シリーズでの実測 |
|---|---|---|---|
| 1 | プロンプトを直す（指示を明確に、回答例を入れる） | 指示の解釈がぶれている | 0.6B では回答例を入れても分類できなかった（[Transformers の §5.6](transformers.md#56-バッチで問い合わせを分類する)） |
| 2 | 資料を渡す（RAG） | モデルが知らない事実（社内の決まり）を答えさせたい | 資料を渡せば 0.6B でも締め日を正しく答えた（[Transformers の §5.4](transformers.md#54-generate--資料を渡して答えさせる)） |
| 3 | 一段大きなモデルに替える | モデルの力が足りない | 4B に替えると、学習なしで 75% になった（§5.3） |
| 4 | 追加学習（本ドキュメント） | 決まった形式・決まった判断を、小さく速いモデルで大量にこなしたい | 0.6B が 17% → 67% になり、4B より約 5 倍速く動いた（§6.2） |

> **注意**: 追加学習は、モデルに新しい事実を覚えさせる手段としては向かない。事実は変わるたびに学習し直しになるので、RAG で渡す。学習で教えるのは「答え方の形」と「判断の癖」である。

### 3.2 道具の比較

TRL + PEFT は 2 層目「モデルと学習」にあたる。入力は元のモデルと学習データ、出力は LoRA のアダプタ（数十 MB）か、統合した重み（safetensors）である。

| 道具 | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **TRL + PEFT** | SFT・DPO・GRPO などの主要な学習方法がそろい、Transformers のモデルをそのまま使える | 大きなモデルの学習は NVIDIA GPU が前提になりやすい | 標準的な方法で追加学習する。まずはこれ |
| [MLX-LM](README.md#2-ドキュメント一覧) の `mlx_lm.lora` | Apple Silicon で LoRA の学習が速い | 学習方法の種類は TRL より少ない | Mac だけで学習から配信まで済ませる |
| Unsloth / Axolotl / LLaMA-Factory | 設定ファイルや最適化で、学習を速く・省メモリにする。中で TRL や PEFT を使うものもある | 道具ごとの作法を覚える必要がある | 学習を何度も回す・GPU を節約したい |
| フルの微調整（全パラメータを学習） | 表現力が最も高い | メモリと時間が桁違いに要り、モデル全体を保存し直す | 大きな計算資源があり、LoRA で足りないと分かったとき |

---

## 4. セットアップ

### 4.1 検証環境

検証環境の全体は索引の [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。本ドキュメント固有の版とモデルは次のとおり。

| 項目 | 版・モデル |
|---|---|
| trl / peft | 1.17.1 / 0.21.2 |
| transformers / torch | 5.22.2 / 2.15.0 |
| datasets / accelerate（TRL と一緒に入る） | 5.1.0 / 1.15.0 |
| モデル | `Qwen/Qwen3-0.6B`（学習する側）、`Qwen/Qwen3-4B-Instruct-2507`（比べる相手） |

### 4.2 インストール

（検証済み）

```bash
uv init --bare --python 3.12 trl-hello && cd trl-hello
uv python pin 3.12
uv add "trl==1.17.1" "peft==0.21.2" "transformers==5.22.2" "torch==2.15.0"
```

TRL の公式 docs には MPS（Apple Silicon の GPU）についての記述が無い。本ドキュメントでは、SFT と LoRA の学習が MPS で動くことを実際に確かめた（§5.4）。

### 4.3 動作確認

§5.2 のスクリプトが動けば、TRL・PEFT・Transformers の組み合わせが揃っている。

---

## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。
実行結果からは、モデルの読み込み・学習・書き出しの進捗表示（プログレスバー）の行を省いた。

### 5.1 学習方法の地図 — SFT・DPO・GRPO と LoRA

| 方法 | 学習データ | 何を学ぶか | 本ドキュメント |
|---|---|---|---|
| SFT（教師ありファインチューニング） | 入力と、望ましい出力の組 | 手本の出力をそのまま真似る | §5.4 で実行 |
| DPO（直接選好最適化） | 入力と、良い出力・悪い出力の組 | 悪い出力より良い出力を選ぶ | 扱わない（データの形だけ §6.3） |
| GRPO | 入力と、出力を採点する報酬関数 | 自分で何通りか答え、点の高い答え方を強める | §5.7 で MPS での動作を試した |

- いずれも、モデル全体を学習することも、LoRA で一部だけ学習することもできる
- **LoRA** は、元の重みを固定したまま、各層に小さな行列の組（アダプタ）を足して、それだけを学習する。足す行列の幅を**ランク（`r`）**と呼ぶ
- 実務の典型は「SFT で答え方の形を教え、必要なら DPO や GRPO で好みに寄せる」という順番である

### 5.2 LoRA で学習するパラメータの数を見る

`LoraConfig` の設定で、学習するパラメータがどれだけになるかを見る（検証済み）。

```python
"""LoRA を付けると、学習するパラメータがどれだけ減るかを見る。"""
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

from common import MODEL

ATTENTION = ["q_proj", "k_proj", "v_proj", "o_proj"]
for r, targets in ((16, ATTENTION), (8, "all-linear"), (16, "all-linear")):
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype="auto")
    config = LoraConfig(
        r=r,                      # 追加する小さな行列の幅（ランク）
        lora_alpha=2 * r,         # 学習した差分を何倍して足すか
        target_modules=targets,   # どの線形層に付けるか。"all-linear" は出力層以外のすべて
        task_type="CAUSAL_LM",
    )
    peft_model = get_peft_model(model, config)
    print(f"r={r:2d} {'attention' if targets is ATTENTION else targets:10s}: ", end="")
    peft_model.print_trainable_parameters()
```

実行結果:

```text
$ uv run python 01_lora_params.py
…（中略: 1 行。macOS での Redirects の注意）…
r=16 attention : trainable params: 4,587,520 || all params: 600,637,440 || trainable%: 0.7638
r= 8 all-linear: trainable params: 5,046,272 || all params: 601,096,192 || trainable%: 0.8395
r=16 all-linear: trainable params: 10,092,544 || all params: 606,142,464 || trainable%: 1.6650
```

- 学習するのは全体の 1% 前後で、残りの約 5.96 億個は固定される。勾配と最適化の状態を持つのも 1% 分だけなので、メモリが大きく減る
- `common.py` は、モデル名・ラベル・プロンプト・評価の関数をまとめた共通の部品である（§5.3）
- TRL の [LoRA Without Regret](https://huggingface.co/docs/trl/lora_without_regret) は、Attention の層だけに付ける方式は、ランクを上げてパラメータ数を揃えても全部の層に付ける方式に劣るとして、`target_modules="all-linear"` を勧めている。本ドキュメントの学習はこれに従った

### 5.3 データを用意し、学習前の実力を測る

学習データ（`train.jsonl`、48 件）と評価データ（`test.jsonl`、12 件）を、6 つのラベルで同じ数ずつ作った。両者に同じ文は入れていない（抜粋・単体では動かない）。

```text
{"text": "新幹線代の立て替えを精算したい", "label": "経費"}
{"text": "経費申請が差し戻されました", "label": "経費"}
…（中略: 46 行）…
```

共通の部品。評価は、[Transformers の §5.6](transformers.md#56-バッチで問い合わせを分類する) と同じプロンプトでまとめて分類し、正解率を返す（検証済み）。

```python
"""ハンズオンで共通に使う、ラベル・プロンプト・評価の関数。"""
import json

import torch

MODEL = "Qwen/Qwen3-0.6B"
LABELS = ["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]
SYSTEM = f"問い合わせを次のどれか 1 つに分類し、ラベルだけを答えてください: {'、'.join(LABELS)}"
device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"


def load_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def to_messages(text: str) -> list[dict]:
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]


def accuracy(model, tok, rows: list[dict]) -> float:
    """rows をまとめて分類し、1 件ずつ結果を表示して正解率を返す。"""
    tok.padding_side = "left"
    prompts = [
        tok.apply_chat_template(to_messages(r["text"]), tokenize=False, add_generation_prompt=True, enable_thinking=False)
        for r in rows
    ]
    batch = tok(prompts, padding=True, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(**batch, max_new_tokens=8, do_sample=False)
    correct = 0
    for r, ids in zip(rows, out[:, batch["input_ids"].shape[1]:]):
        pred = tok.decode(ids, skip_special_tokens=True).strip()
        correct += pred == r["label"]
        print(f"  {'○' if pred == r['label'] else '×'} {pred} (正解 {r['label']}) ← {r['text']}")
    return correct / len(rows)
```

学習前のモデルで測る。引数でモデルを替えられる（検証済み）。

```python
"""学習前のモデルで、評価データを分類する。引数でモデルを替えられる。"""
import sys

from transformers import AutoModelForCausalLM, AutoTokenizer

from common import MODEL, accuracy, device, load_jsonl

name = sys.argv[1] if len(sys.argv) > 1 else MODEL
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name, dtype="auto", device_map=device)
print(f"{name} 正解率: {accuracy(model, tok, load_jsonl('test.jsonl')):.0%}")
```

実行結果:

```text
$ uv run python 02_baseline.py
  × IT (正解 経費) ← タクシー代の精算方法を教えてください
  × IT (正解 勤怠) ← 明日の午後に半休を取りたいです
  ○ IT (正解 IT) ← Wi-Fi が頻繁に切れます
…（中略: 8 行）…
  × IT (正解 総務) ← 会議室の椅子が壊れています
Qwen/Qwen3-0.6B 正解率: 17%
```

```text
$ uv run python 02_baseline.py Qwen/Qwen3-4B-Instruct-2507
…（中略: 2 行。HF_TOKEN の警告と macOS での Redirects の注意）…
  ○ 経費 (正解 経費) ← タクシー代の精算方法を教えてください
…（中略: 6 行）…
  × 総務 (正解 勤怠) ← 育児休業の手続きを知りたい
  ○ IT (正解 IT) ← キーボードの一部のキーが反応しない
  ○ 出張 (正解 出張) ← 出張先から直帰してもいいですか
  × 総務 (正解 セキュリティ) ← USB メモリを拾いました
  × IT (正解 総務) ← 会議室の椅子が壊れています
Qwen/Qwen3-4B-Instruct-2507 正解率: 75%
```

0.6B は 12 件すべてを「IT」と答え、IT の 2 件だけが当たって 17% になった。4B は学習なしで 75% である。これが学習の効果を測る基準になる。

### 5.4 SFT で LoRA を学習させる

会話の形のデータ（`messages`）を `SFTTrainer` に渡す。`assistant_only_loss=True` で、誤差を assistant の発言（＝ラベル）だけで測る（検証済み）。

```python
"""48 件の問い合わせとラベルで、0.6B に LoRA で分類を教える（SFT）。"""
import time

from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

from common import MODEL, load_jsonl, to_messages

rows = load_jsonl("train.jsonl")
dataset = Dataset.from_list(
    [{"messages": to_messages(r["text"]) + [{"role": "assistant", "content": r["label"]}]} for r in rows]
)

args = SFTConfig(
    output_dir="out/sft-lora",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=2e-4,          # LoRA はフルの学習の約 10 倍が目安（TRL の PEFT ガイド）
    assistant_only_loss=True,    # 誤差は assistant の発言（= ラベル）だけで測る
    logging_steps=3,
    save_strategy="no",
    report_to="none",
    seed=0,
)
peft_config = LoraConfig(r=16, lora_alpha=32, target_modules="all-linear", task_type="CAUSAL_LM")  # 全部の線形層に付ける

trainer = SFTTrainer(model=MODEL, args=args, train_dataset=dataset, peft_config=peft_config)
print(f"device={trainer.model.device}  dtype={trainer.model.dtype}  examples={len(dataset)}")
ex = trainer.train_dataset[0]  # 学習に使う 1 件目を、モデルに渡る形で見る
tok = trainer.processing_class
print("入力:", repr(tok.decode(ex["input_ids"])))
print("誤差を測る部分:", repr(tok.decode([t for t in ex["labels"] if t != -100])))  # -100 の位置は学習しない
t0 = time.perf_counter()
trainer.train()
print(f"train: {time.perf_counter() - t0:.1f}s")
trainer.save_model("out/sft-lora")  # 保存されるのはアダプタ（LoRA の重み）だけ
```

実行結果:

```text
$ uv run python 03_train_sft.py
…（中略: 1 行。macOS での Redirects の注意）…
device=mps:0  dtype=torch.float32  examples=48
入力: '<|im_start|>system\n問い合わせを次のどれか 1 つに分類し、ラベルだけを答えてください: 経費、勤怠、IT、総務、出張、セキュリティ<|im_end|>\n<|im_start|>user\n新幹線代の立て替えを精算したい<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n経費<|im_end|>\n'
誤差を測る部分: '<think>\n\n</think>\n\n経費<|im_end|>\n'
…（中略: 3 行。MPS の pin_memory の警告〈2 行〉と HF_TOKEN の警告）…
{'loss': '1.029', 'grad_norm': '3.606', 'learning_rate': '0.0001778', 'entropy': '0.1925', 'mean_token_accuracy': '0.8405', 'num_tokens': '1799', 'epoch': '0.5'}
{'loss': '0.3996', 'grad_norm': '6.323', 'learning_rate': '0.0001444', 'entropy': '0.1575', 'mean_token_accuracy': '0.9175', 'num_tokens': '3608', 'epoch': '1'}
…（中略: 3 行）…
{'loss': '0.08177', 'grad_norm': '0.9191', 'learning_rate': '1.111e-05', 'entropy': '0.159', 'mean_token_accuracy': '0.9799', 'num_tokens': '1.082e+04', 'epoch': '3'}
{'train_runtime': '23', 'train_samples_per_second': '6.262', 'train_steps_per_second': '0.783', 'train_loss': '0.3272', 'epoch': '3'}
train: 23.1s
```

- **MPS で学習できた**（`device=mps:0`）。48 件 × 3 エポック = 18 ステップで 23 秒だった（参考値）
- `SFTTrainer` にモデル名を文字列で渡すと、TRL がモデルを読み込む。このとき精度は `float32` になった。§5.5 で効いてくる
- 「入力」は、チャットテンプレートを当てた学習データの 1 件目である。推論のとき（`enable_thinking=False`）と同じく、空の `<think></think>` の後にラベルが続く形になっている
- 「誤差を測る部分」は assistant の発言だけで、system と user の部分は `-100` で除かれている。公式 docs によると、Qwen3 のように TRL が知っているモデルでは、`assistant_only_loss` に必要なテンプレートの修正を TRL が自動で当てる
- 学習率の `2e-4` は、TRL の PEFT ガイドの表にある「SFT を LoRA で行うときの目安」である（フルの学習は `2e-5`）
- `loss`（誤差）は 1.03 から 0.08 まで下がった。ただし、これは学習データでの値である。本当の実力は §5.5 で評価データを使って測る

`out/sft-lora/` に保存されたアダプタの本体（`adapter_model.safetensors`）は 40MB だった。元のモデル（1.2GB）は含まれない。

### 5.5 アダプタを載せて評価する — 精度を学習時と揃える

元のモデルにアダプタを載せ、学習に使っていない評価データで測る（検証済み）。

```python
"""学習したアダプタを元のモデルに載せ、同じ評価データで分類する。"""
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import MODEL, accuracy, device, load_jsonl

tok = AutoTokenizer.from_pretrained(MODEL)
base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32, device_map=device)  # 学習時と同じ精度
model = PeftModel.from_pretrained(base, "out/sft-lora")  # 元の重みはそのまま、差分だけを足す
print(f"正解率: {accuracy(model, tok, load_jsonl('test.jsonl')):.0%}")
```

実行結果:

```text
$ uv run python 04_eval_adapter.py
  ○ 経費 (正解 経費) ← タクシー代の精算方法を教えてください
  ○ 勤怠 (正解 勤怠) ← 明日の午後に半休を取りたいです
  ○ IT (正解 IT) ← Wi-Fi が頻繁に切れます
  ○ 出張 (正解 出張) ← 来月の大阪出張の新幹線を手配したい
  × 総務 (正解 セキュリティ) ← 知らない差出人から添付ファイル付きのメールが来た
  ○ 総務 (正解 総務) ← 名刺の在庫が残りわずかです
  × セキュリティ (正解 経費) ← セミナーの参加費は会社負担になりますか
  × 育児休業 (正解 勤怠) ← 育児休業の手続きを知りたい
  ○ IT (正解 IT) ← キーボードの一部のキーが反応しない
  ○ 出張 (正解 出張) ← 出張先から直帰してもいいですか
  × IT (正解 セキュリティ) ← USB メモリを拾いました
  ○ 総務 (正解 総務) ← 会議室の椅子が壊れています
正解率: 67%
```

- 学習前の 17% から 67% に上がった。全部を「IT」と答える癖が消え、6 つのラベルを使い分けている
- 「育児休業」のように、ラベルの一覧に無い言葉を答えた例が 1 件ある。学習しても出力の形は保証されないので、受け取る側で一覧と照らす
- 最初は元のモデルを `dtype="auto"`（bfloat16）で読み込んで評価し、正解率は 58% だった。学習は float32 で行われており、bfloat16 の元の重みに float32 のアダプタを載せた状態では、境目の数件で判断が変わる。float32 で読み込むと 67% になった（検証済み、ログは `04b_dtype_check.log`）

> **ポイント**: 学習させたモデルは、学習時と同じ精度・同じプロンプト・同じチャットテンプレートで評価する。どれかがずれると、学習の良し悪しではなく、ずれの影響を測ってしまう。

### 5.6 アダプタを統合し、配信の層へ渡す

アダプタを元の重みに足し込んで（merge）、PEFT が無くても読める普通のモデルとして保存する（検証済み）。

```python
"""アダプタを元の重みに統合し、PEFT なしで読める普通のモデルとして保存する。"""
from pathlib import Path

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import MODEL, accuracy, device, load_jsonl

base = AutoModelForCausalLM.from_pretrained(MODEL, dtype="auto")
merged = PeftModel.from_pretrained(base, "out/sft-lora").merge_and_unload()  # 差分を足し込んで LoRA の層を外す
merged.save_pretrained("out/merged")
AutoTokenizer.from_pretrained(MODEL).save_pretrained("out/merged")

size = sum(f.stat().st_size for f in Path("out/merged").glob("*.safetensors"))
print(f"merged: {type(merged).__name__}  dtype={merged.dtype}  safetensors={size / 1e9:.2f} GB")

# 推論サーバーと同じく、PEFT を使わずに読み込めることを確かめる
model = AutoModelForCausalLM.from_pretrained("out/merged", dtype="auto", device_map=device)
tok = AutoTokenizer.from_pretrained("out/merged")
print(f"正解率: {accuracy(model, tok, load_jsonl('test.jsonl')):.0%}")
```

実行結果:

```text
$ uv run python 05_merge.py
…（中略: 1 行。macOS での Redirects の注意）…
merged: Qwen3ForCausalLM  dtype=torch.bfloat16  safetensors=1.19 GB
…（中略: 12 行。§5.5 と同じ 12 件の結果）…
正解率: 67%
```

- 統合後は、ただの `Qwen3ForCausalLM` である。PEFT を入れていない推論サーバーでも、元のモデルと同じように読める
- 統合は bfloat16 で行ったが、正解率は float32 でアダプタを載せたときと同じ 67% だった。それでも、統合した後にもう一度評価する手順は省かない
- `out/merged` は MLX-LM で MLX 形式に変換して配信できる（[MLX-LM](README.md#2-ドキュメント一覧) で扱う）

統合せず、アダプタのまま推論サーバーに載せる方法もある。vLLM は、1 つの元のモデルに複数のアダプタを載せ、リクエストの `model` で切り替えられる（公式 docs 準拠・未実行: vLLM の LoRA 配信は [vLLM](README.md#2-ドキュメント一覧) のドキュメントで扱う）。

```bash
vllm serve Qwen/Qwen3-0.6B \
    --enable-lora \
    --lora-modules ticket-classifier=./out/sft-lora
```

| 渡し方 | 向く場面 |
|---|---|
| 統合した重みを渡す | アダプタが 1 つだけ。推論を最も単純にしたい |
| アダプタのまま渡す（`--enable-lora`） | 用途別のアダプタを複数持ち、元のモデルを 1 つで共有したい |

### 5.7 GRPO を MPS で試す

GRPO は、学習の途中でモデル自身に何通りか答えさせ、報酬関数の点が高い答え方を強める。正解のラベルを返したら 1 点を与える報酬関数を書いた（抜粋・単体では動かない）。

```python
def reward_label(completions, label, **kwargs):
    """正解のラベルなら 1、ラベルの一覧にあるが不正解なら 0.1、それ以外は 0。"""
    answers = [c[0]["content"].strip() for c in completions]
    return [1.0 if a == y else 0.1 if a in LABELS else 0.0 for a, y in zip(answers, label)]
```

報酬関数は `completions`（生成された答え）と、データセットの列（ここでは `label`）をキーワード引数で受け取り、答えごとの点数のリストを返す。
この関数と `GRPOConfig(num_generations=4, max_completion_length=8, chat_template_kwargs={"enable_thinking": False}, ...)` を `GRPOTrainer` に渡し、12 ステップ動かした（スクリプトの全体は検証用の `07_grpo.py`）。

結果は次のとおりで、**MPS で最後まで動いたが、学習は進まなかった**（ログは `07_grpo.log`・`07b_grpo_from_sft.log`）。

| 出発点 | 所要時間 | `grad_norm` | 報酬の平均（3 ステップごと） | `frac_reward_zero_std` |
|---|---|---|---|---|
| 元の 0.6B | 17.5 秒 | 最初から最後まで 0 | 0.62 → 0.25 → 0.10 → 0.10 | 0.67 → 1 |
| §5.6 の統合済みモデル | 17.3 秒 | 最初から最後まで 0 | 0.62 → 0.25 → 0.10 → 0.10 | 0.67 → 1 |

- `frac_reward_zero_std` が 1 は、同じ問い合わせへの 4 通りの答えが、どの問い合わせでも同じ点だったことを示す。GRPO は答え同士の点の差から学ぶので、差が無ければ学習の手がかりが無い
- ただし、`grad_norm`（重みを動かす量）が最初の、点に差があったステップから 0 であることと、出発点を変えても報酬の推移が同じであることは、この理屈だけでは説明できない。原因は切り分けられていない（確認できなかった事項）
- 1 回は、12 ステップ中 8 ステップ目で CPU を使わないまま止まり、強制終了した（ログは `07_grpo_hang.log`）

> **注意**: GRPO の学習は、生成を何度も繰り返すぶん重い。公式 docs は、生成を vLLM に任せる設定（`use_vllm=True`）を用意している。Mac で本格的に回すより、NVIDIA GPU の環境で試すほうが確実である（公式 docs 準拠・未実行: NVIDIA GPU が必要）。

---

## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | TRL + PEFT を使う理由 | 本番で足すもの |
|---|---|---|---|
| 小さなモデルで分類・抽出を安く速くする | 文章 → 決まったラベル・項目 | 大きなモデルと同程度の精度を、小さく速いモデルで出せる | 評価データ、定期的な再学習、誤りの人手確認 |
| 出力の書式を揃える | 指示 → 決まった形式（JSON・社内の文書の型） | プロンプトで何度言っても崩れる書式を、例で覚えさせられる | 受け取る側での書式の検証 |
| ツール呼び出しの書式を安定させる | 会話 → 正しい形式のツール呼び出し | 小さなモデルが呼び出しの形式を崩す場合に、例で教えられる | エージェントの層での再試行 |
| 回答の好みを寄せる | 良い答えと悪い答えの組 → 好まれる答え方 | DPO で「こちらが良い」を学ばせられる | 好みのデータを集める仕組み |

### 6.2 代表例: 0.6B に分類を教え、4B と比べて採否を決める

§5.3〜§5.6 が、そのまま代表例の流れである。最後に、同じような正解率になった 2 つ（LoRA で学習して統合した 0.6B と、学習していない 4B）の速さと大きさを比べ、どちらを使うかを決める（検証済み）。

```python
"""同じ正解率になった 2 つ（0.6B + LoRA を統合したもの / 学習していない 4B）の速さと大きさを比べる。"""
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import device, load_jsonl, to_messages

rows = load_jsonl("test.jsonl")
for name in ("out/merged", "Qwen/Qwen3-4B-Instruct-2507"):
    tok = AutoTokenizer.from_pretrained(name, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(name, dtype="auto", device_map=device)
    prompts = [tok.apply_chat_template(to_messages(r["text"]), tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in rows]
    batch = tok(prompts, padding=True, return_tensors="pt").to(model.device)
    times = []
    for _ in range(4):  # 1 回目は準備の時間を含むので捨てる
        t0 = time.perf_counter()
        with torch.inference_mode():
            model.generate(**batch, max_new_tokens=8, do_sample=False)
        torch.accelerator.synchronize()
        times.append(time.perf_counter() - t0)
    gb = model.num_parameters() * model.dtype.itemsize / 1e9
    print(f"{name:30s} params={model.num_parameters() / 1e9:.2f}B  weights≈{gb:.1f} GB  {len(rows)} 件: {min(times[1:]):.2f}s")
    del model
```

実行結果:

```text
$ uv run python 06_speed.py
…（中略: 1 行。macOS での Redirects の注意）…
out/merged                     params=0.60B  weights≈1.2 GB  12 件: 0.36s
Qwen/Qwen3-4B-Instruct-2507    params=4.02B  weights≈8.0 GB  12 件: 1.88s
```

結果をまとめる（速さは参考値）。

| モデル | 学習 | 評価データの正解率 | 12 件の処理時間 | 重みの大きさ |
|---|---|---|---|---|
| Qwen3-0.6B | なし | 17%（2/12） | — | 1.2GB |
| Qwen3-0.6B + LoRA（統合） | 48 件 × 3 エポック、23 秒 | 67%（8/12） | 0.36 秒 | 1.2GB |
| Qwen3-4B-Instruct-2507 | なし | 75%（9/12） | 1.88 秒 | 8.0GB |

判断の仕方:

- **件数が少ないなら 4B をそのまま使う**。学習データの用意も、学習済みモデルの管理も要らず、正解率もやや高い
- **毎日大量に処理する、または小さな機械で動かしたいなら 0.6B + LoRA を検討する**。約 5 倍速く、メモリは 1/7 で済む。正解率の差（1 件分）は、学習データを増やして縮められるかを試す
- **12 件の評価は小さい**。1 件で 8 ポイント動くので、67% と 75% の差は誤差の範囲かもしれない。採否を決める前に、実際の問い合わせから評価データを数百件集めて測り直す

> **ポイント**: 追加学習の価値は「大きなモデルと比べて、同じ仕事をどれだけ安く速くこなせるか」で測る。学習前と学習後だけを比べると、学習しない選択肢を見落とす。

### 6.3 その他のユースケースの素描

- **書式を揃える SFT**: 学習データの assistant の発言を、望む書式（JSON など）で書く。§5.4 のスクリプトはそのまま使える。書式の検証は、エージェントの層の構造化出力（[Pydantic AI](README.md#2-ドキュメント一覧) など）と組み合わせる
- **好みを寄せる DPO**: データは `{"prompt": [...], "chosen": [...], "rejected": [...]}` の形で、同じ入力への良い答えと悪い答えを並べる。`DPOTrainer` に `peft_config` を渡す使い方は SFT と同じで、LoRA のときの学習率の目安は `5e-6` である（TRL の PEFT ガイド）
- **大きなモデルを省メモリで学習する QLoRA**: 元のモデルを 4bit に量子化して読み込み、その上で LoRA を学習する。bitsandbytes を使うため NVIDIA GPU が前提である（公式 docs 準拠・未実行: NVIDIA GPU が必要）

---

## 7. 本番運用の要点

- **評価データを先に作り、学習データと混ぜない**。学習データで測った正解率は、暗記を見ているだけかもしれない（§5.4 の `loss` が下がっても、評価では 67% だった）
- **学習の条件を記録する**。元のモデルのリビジョン、データの版、`LoraConfig` と `SFTConfig` の値、ライブラリの版を残すと、同じアダプタを作り直せる。TRL は出力先に `training_args.bin` と README を書き出す
- **アダプタは元のモデルの版と対で管理する**。アダプタは特定の元のモデルに対する差分なので、別の版の元のモデルには載らないか、載っても結果が変わる
- **ライセンスを引き継ぐ**。学習したモデルも、元のモデルのライセンス（Qwen3 なら Apache-2.0）の条件に従う
- **NVIDIA GPU での本格的な学習**では、bfloat16 での学習、`gradient_checkpointing`、複数 GPU（accelerate・DeepSpeed）、生成を vLLM に任せる GRPO などを使う（公式 docs 準拠・未実行: NVIDIA GPU が必要）

---

## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 学習後の評価が、思ったより低い（実測） | 学習は float32、評価は bfloat16 と、精度がずれていた | 学習時と同じ精度で読み込んで評価する（§5.5） |
| `SFTConfig.__init__() got an unexpected keyword argument 'chat_template_kwargs'`（実測） | SFT には設定として無い（GRPO の `GRPOConfig` にはある） | 会話の形のデータなら、Qwen3 は指定しなくても推論時と同じ形で学習された（§5.4 の「入力」） |
| GRPO の `grad_norm` が 0 のまま、報酬が上がらない（実測） | 同じ入力への答えの点に差が無いと学習できない。それ以外の原因は切り分けていない | まず SFT で答え方を教える。報酬に段階を付ける。生成数（`num_generations`）を増やす |
| GRPO が途中で止まり、CPU を使わないまま進まない（実測、1 回） | 不明 | 強制終了してやり直したら完走した |
| 学習中に `'pin_memory' argument is set as true but not supported on MPS` という警告が出る（実測） | MPS ではピン留めのメモリが使えない | 無視してよい。学習は進む |
| 学習データでは正解するのに、評価データで外れる | 学習データが少ない・偏っている | 評価で外れた種類の例を学習データに足す。評価データそのものは足さない |

---

## 9. 次のステップ

- 学習したモデルを配信する: [MLX-LM](README.md#2-ドキュメント一覧)（Mac。統合したモデルを MLX 形式に変換する）、[vLLM](README.md#2-ドキュメント一覧)（`--enable-lora` でアダプタのまま配信する）
- 学習方法を広げる: TRL の [DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer) と [GRPO Trainer](https://huggingface.co/docs/trl/grpo_trainer)
- LoRA の設定を詰める: [LoRA Without Regret](https://huggingface.co/docs/trl/lora_without_regret)（ランク・学習率・対象の層の選び方）

---

## 出典

| 情報源 | URL |
|---|---|
| TRL documentation | https://huggingface.co/docs/trl/index （2026-11-08 確認） |
| SFT Trainer | https://huggingface.co/docs/trl/sft_trainer （2026-11-08 確認、Context7 `/huggingface/trl` 経由。会話データへのチャットテンプレートの自動適用・`assistant_only_loss` と Qwen3 のテンプレートの自動修正・アダプタの学習率 1e-4 の目安） |
| PEFT Integration | https://huggingface.co/docs/trl/peft_integration （2026-11-08 確認。LoRA の学習率の表〈SFT 2e-4・DPO 5e-6・GRPO 1e-5〉・アダプタの保存・`merge_and_unload`） |
| LoRA Without Regret | https://huggingface.co/docs/trl/lora_without_regret （2026-11-08 確認。Attention だけに付ける方式が劣る旨と `all-linear` の推奨） |
| GRPO Trainer | https://huggingface.co/docs/trl/grpo_trainer （2026-11-08 確認。報酬関数の引数・`chat_template_kwargs`） |
| Dataset formats | https://huggingface.co/docs/trl/dataset_formats （2026-11-08 確認。DPO の chosen / rejected の形） |
| PEFT Quantization | https://huggingface.co/docs/peft/developer_guides/quantization （2026-11-08 確認。QLoRA と bitsandbytes） |
| vLLM LoRA Adapters | https://docs.vllm.ai/en/latest/features/lora.html （2026-11-08 確認、Context7 `/vllm-project/vllm` 経由。`--enable-lora` と `--lora-modules`） |
| GitHub `huggingface/trl` | ★19,685・v1.17.1（2026-10-30 公開）（2026-11-08 に GitHub API で取得） |
| GitHub `huggingface/peft` | ★21,877・v0.21.2（2026-10-01 公開）（2026-11-08 に GitHub API で取得） |

### 確認できなかった事項

- **TRL の MPS 対応の公式な位置づけ**。公式 docs には MPS の記述が見つからなかった（`sft_trainer.md`・`peft_integration.md`・`grpo_trainer.md` を全文検索）。本ドキュメントは、SFT と LoRA の学習が MPS で動いた事実だけを書いた
- **§5.7 の GRPO で `grad_norm` が 0 のままだった原因**。報酬の差が無いことだけでは説明できない点が残る。報酬関数が受け取る答えは出発点のモデルで変わっていた（デバッグ出力で確認）が、報酬の推移は同じだった。MPS 固有の問題かどうかも切り分けていない
- **「追加学習の前にプロンプト・RAG・大きなモデルを試す」順番**は、本シリーズの推奨であり、TRL の公式 docs の記述ではない。根拠は §3.1 の表に挙げた実測である
- **§6.2 の正解率の差**は、12 件の評価による。1 件で 8 ポイント動くため、統計的な差かどうかは言えない

- 関連: [AI フレームワーク学習ガイド](README.md) / [Transformers](transformers.md) / [PyTorch](pytorch.md) / [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md)
