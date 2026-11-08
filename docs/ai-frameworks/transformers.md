# Transformers 入門 — 公開モデルの読み込みから推論・埋め込み検索・OpenAI 互換の配信まで

> 出典（一次情報）:
> - [Transformers documentation (huggingface.co)](https://huggingface.co/docs/transformers/index) — 公式ドキュメントの入口
> - [Transformers v5 Migration guide (github.com)](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) — v5 の変更点。TensorFlow と JAX の除去、`apply_chat_template` の戻り値、`batch_decode` の統合
> - [Chat templates (huggingface.co)](https://huggingface.co/docs/transformers/chat_templating) — 会話をモデルの書式に変換する仕組み
> - [Text generation (huggingface.co)](https://huggingface.co/docs/transformers/llm_tutorial) — `generate()` の使い方と、バッチ生成で padding を左に寄せる理由
> - [Serve CLI (huggingface.co)](https://huggingface.co/docs/transformers/serving) — `transformers serve` の位置づけ（評価・実験・中程度の負荷向け）
> - [Qwen/Qwen3-0.6B (huggingface.co)](https://huggingface.co/Qwen/Qwen3-0.6B) ・ [intfloat/multilingual-e5-small (huggingface.co)](https://huggingface.co/intfloat/multilingual-e5-small) — 使ったモデルのカード
>
> 最終更新: 2026-11-08（transformers v5.22.2 で検証。★と最新版は 2026-11-08 時点）

Transformers は、Hugging Face Hub に公開された学習済みモデルを、同じ書き方で読み込んで使うための Python ライブラリである。
LLM の文章生成、文章を数値にする埋め込み、分類などを、モデルが変わってもほぼ同じコードで動かせる。
シリーズでは 2 層目の「モデルと学習」にあたり、下の [PyTorch](pytorch.md) の上で動き、上の推論サーバー（vLLM・SGLang・MLX-LM）にモデルを渡す。
本ドキュメントは推論・埋め込み・簡易な配信までを扱い、追加学習は [TRL + PEFT](trl-peft.md) に回す。
シリーズ全体の地図は [AI フレームワーク学習ガイド](README.md) を参照。

---

## 1. TL;DR

- **Transformers は「Hub のモデルを `from_pretrained()` 1 行で読み込み、推論する」ためのライブラリ**である。モデルごとの違い（構造・トークナイザ・会話の書式）を吸収してくれる。
- **v5 から PyTorch 専用**になった。TensorFlow と JAX の対応は外された。`apply_chat_template` の戻り値など、古い記事と書き方が違う箇所がある（§8）。
- **使う前にモデルカードでライセンスと用途を確かめる**（§5.1）。同じ「0.6B」でも、得意なこと・できないことはモデルごとに違う。
- **小さなモデルは、思ったよりできないことが多い**。0.6B のモデルに問い合わせを分類させたら、6 件すべてを「IT」と答えた。4B に替えると分類できた（§5.6）。
- **埋め込みモデルは、自分のデータで測ってから選ぶ**。手元の FAQ では、大きい e5-base が小さい e5-small を上回らなかった（12 問中 1 問の差で、優劣は付けられない。§6.2）。
- **`transformers serve` で OpenAI 互換の API を立てられる**。ただし公式は大規模な本番には vLLM や SGLang を勧めている（§5.7・§7）。

---

## 2. 前提知識

- **[PyTorch](pytorch.md) のテンソル・dtype・デバイス**の感覚。Transformers のモデルは PyTorch の `nn.Module` である
- **LLM は「次のトークンを予測する」ことを繰り返して文章を作る**。1 回の予測で 1 トークンずつ伸びる
- **埋め込み（embedding）**: 文章を固定長の数値の並び（ベクトル）にしたもの。意味の近い文章ほどベクトルも近くなる
- トークン・トークナイザ・チャットテンプレート・safetensors・RAG などの用語は、索引の [用語集](README.md#62-モデルファインチューニング) にまとめた

---

## 3. 位置づけと比較

Transformers は 2 層目「モデルと学習」の中心である。入力は Hub のモデル名（またはローカルの重みファイル）とテキスト、出力は生成した文章・埋め込みのベクトル・分類の結果である。
同じ重み（safetensors）を、推論サーバーもそのまま読む。

| 道具 | 得意なこと | 苦手なこと | 選ぶ場面 |
|---|---|---|---|
| **Transformers** | ほぼすべての公開モデルを同じ書き方で動かせる。モデルの中身（トークン・確率・中間の値）まで触れる | 多数の利用者からのリクエストを同時に捌く配信は、専用の推論サーバーに劣る | モデルを試す・評価する・前処理を挟んだバッチ処理をする |
| [vLLM](README.md#2-ドキュメント一覧) / [SGLang](README.md#2-ドキュメント一覧) | 多数の同時リクエストを速く捌く配信（Mac では MLX を計算に使う版がある） | モデルの中身を触る用途には向かない | 本番の API として配信する |
| [MLX-LM](README.md#2-ドキュメント一覧) | Apple Silicon で LLM を速く動かす。量子化した重みを扱いやすい | MLX 形式（mlx-community など）の重みが前提 | Mac の上で LLM を動かす・配信する |
| sentence-transformers | 埋め込み・類似度・再ランキングを短いコードで書ける。中で Transformers を使う | 文章生成はしない | 埋め込み検索を手早く組む |
| Transformers.js | ブラウザや Node.js で Transformers のモデルを動かす | 大きなモデルは重い | 利用者の端末側で小さなモデルを動かす |

> **ポイント**: Transformers は「モデルを理解し、選ぶ」ための道具で、推論サーバーは「選んだモデルを大勢に配る」ための道具である。まず Transformers で試し、配信は上の層に渡すのが基本の流れになる。

---

## 4. セットアップ

### 4.1 検証環境

検証環境の全体は索引の [ローカル検証環境](README.md#7-ローカル検証環境シリーズ共通) を参照。本ドキュメント固有の版とモデルは次のとおり。

| 項目 | 版・モデル |
|---|---|
| transformers | 5.22.2（`[serving]` 付き。fastapi 0.162.2 / uvicorn 0.54.0 が入る） |
| torch | 2.15.0 |
| huggingface-hub / tokenizers / safetensors | 2.4.0 / 0.23.3 / 0.8.0 |
| openai（§5.7 のクライアント） | 3.46.0 |
| モデル | `Qwen/Qwen3-0.6B`、`Qwen/Qwen3-4B-Instruct-2507`（§5.6・§5.7）、`intfloat/multilingual-e5-small`・`-base`（§5.5・§6.2） |

### 4.2 インストール

`[serving]` は §5.7 の `transformers serve` に要る FastAPI と Uvicorn を足す（検証済み）。

```bash
uv init --bare --python 3.12 transformers-hello && cd transformers-hello
uv python pin 3.12
uv add "transformers[serving]==5.22.2" "torch==2.15.0" openai
```

モデルは初回の `from_pretrained()` で自動的にダウンロードされ、`~/.cache/huggingface/hub/` に保存される。
先にまとめて落としておくなら `hf download` を使う。必要なファイルだけに絞ると、ディスクを節約できる（検証済み）。

```bash
uv run hf download Qwen/Qwen3-4B-Instruct-2507 --include "*.json" --include "*.safetensors" --include "merges.txt"
```

`--include` は 1 回に 1 つのパターンしか取らない。`--include "*.json" "*.safetensors"` のように並べると、2 つ目以降はファイル名として扱われ、`--include` そのものが無視される（`Ignoring --include since filenames have been explicitly set` という警告が出る）。パターンごとに `--include` を繰り返す。`--dry-run` を付けると、落とすファイルの一覧だけを確かめられる（ログは `01c_download_include.log`）。

> **注意**: 何も絞らずに落とすと、ONNX 版などの使わないファイルまで入る。`intfloat/multilingual-e5-small` は、全体を落としたら 2.3GB になった（重み本体は 0.5GB 弱）。

### 4.3 動作確認

キャッシュにあるモデルを一覧する（検証済み）。

```bash
uv run hf cache ls
```

実行結果:

```text
$ uv run hf cache ls
id	size	last_accessed	last_modified	refs
model/Qwen/Qwen3-0.6B	1.5G	9 hours ago	12 hours ago	['main']
model/Qwen/Qwen3-4B-Instruct-2507	8.1G	9 hours ago	9 hours ago	['main']
…（中略: 1 行）…
model/intfloat/multilingual-e5-small	2.3G	9 hours ago	12 hours ago	['main']
…（中略: 3 行）…

Found 7 repo(s) for a total of 7 revision(s) and 17.2G on disk.
```

§4.2 の 4B を落とした後に実行した。中略した行は、§6.2 の e5-base と、本シリーズのほかのドキュメントで使う MLX 版などのモデルである。

---

## 5. ハンズオン

コードはすべて同じ uv プロジェクトの `src/` に置き、`src/` の中で実行した。
通し課題の FAQ（`faq.jsonl`）は索引の [7.4](README.md#74-通し課題のデータ架空の社内-faq) にある 12 行の架空データで、`../../_shared/faq.jsonl` に置いた。

> **注意**: 生成結果は、`do_sample=False`（毎回いちばん確率の高いトークンを選ぶ）で固定した 1 回分の例である。Qwen3 のモデルカードは、実際の利用では `temperature=0.7` などのサンプリングを推奨しており、考える過程を出す thinking モードでは「greedy decoding を使うな」と書いている。ここでは再現しやすさを優先した。

### 5.1 モデルカードとライセンスを確かめる

使う前に、ライセンス・利用規約への同意の要否（gated）・用途を確かめる（検証済み）。

```python
"""Hub のモデル情報から、使う前に確かめる項目だけを表示する。"""
from huggingface_hub import model_info

for repo in ("Qwen/Qwen3-0.6B", "intfloat/multilingual-e5-small"):
    info = model_info(repo)
    card = info.card_data or {}
    params = info.safetensors.total if info.safetensors else None
    print(f"{repo}")
    print(f"  license      : {card.get('license')}")
    print(f"  gated        : {info.gated}")
    print(f"  pipeline_tag : {info.pipeline_tag}")
    print(f"  library      : {info.library_name}")
    print(f"  parameters   : {params:,}" if params else "  parameters   : (不明)")
    print(f"  files        : {sorted(s.rfilename for s in info.siblings if s.rfilename.endswith(('.json', '.safetensors')))}")
```

実行結果:

```text
$ uv run python 01_hub_info.py
Qwen/Qwen3-0.6B
  license      : apache-2.0
  gated        : False
  pipeline_tag : text-generation
  library      : transformers
  parameters   : 751,632,384
  files        : ['config.json', 'generation_config.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json', 'vocab.json']
intfloat/multilingual-e5-small
  license      : mit
  gated        : False
  pipeline_tag : sentence-similarity
  library      : sentence-transformers
…（中略: 2 行）…
```

- `gated: False` は、利用規約への同意なしでダウンロードできることを示す。Llama などの gated なモデルは、Hub で同意してからトークン（`HF_TOKEN`）を使って落とす
- ライセンスは用途を縛る。Apache-2.0 と MIT は商用にも使えるが、独自ライセンスのモデルは条文を読む
- 同じ情報は CLI の `hf models info Qwen/Qwen3-0.6B` でも取れる（JSON がとても長いので、ここでは Python で必要な項目だけに絞った）

### 5.2 pipeline() — いちばん短い使い方

`pipeline()` は、モデルとトークナイザの読み込み・前処理・生成・後処理をまとめて引き受ける（検証済み）。

```python
"""pipeline() で、モデルの読み込みから生成までを 1 行で済ませる。"""
import time

from transformers import pipeline

t0 = time.perf_counter()
chat = pipeline("text-generation", model="Qwen/Qwen3-0.6B", device="mps", dtype="auto")
print(f"load: {time.perf_counter() - t0:.1f}s  device={chat.device}  dtype={chat.model.dtype}")

messages = [{"role": "user", "content": "経費精算の締め日を確認したい社員に、一文で返事をしてください。"}]
t0 = time.perf_counter()
out = chat(
    messages,
    max_new_tokens=60,
    do_sample=False,
    tokenizer_encode_kwargs={"enable_thinking": False},  # Qwen3 の思考モードを切る
)
print(f"generate: {time.perf_counter() - t0:.1f}s")
print(out[0]["generated_text"][-1])  # 会話の末尾に assistant の発言が足される
```

実行結果:

```text
$ uv run python 02_pipeline.py
…（中略: 3 行。MacOS の Redirects の注意・読み込みの進捗・HF_TOKEN の警告）…
load: 3.9s  device=mps  dtype=torch.bfloat16
generate: 1.9s
{'role': 'assistant', 'content': '経費精算の締め日を確認していただけますように。'}
```

- `dtype="auto"` は、モデルの `config.json` に書かれた精度（ここでは bfloat16）で読み込む。v4.56 以降は `torch_dtype` ではなく `dtype` と書く（`torch_dtype` も動くが、非推奨の警告が出る）
- 会話（`messages` のリスト）を渡すと、チャットテンプレート（§5.3）が自動で適用される
- 返事は締め日に答えていない。モデルは社内の締め日を知らないので、知らないことは正しく答えられない。§5.4 で資料を渡して直す

### 5.3 トークナイザとチャットテンプレート

LLM に実際に渡るのは、文字列ではなくトークンの番号の並びである。日本語と英語のトークン数と、会話がどんな文字列に変換されるかを見る（検証済み）。

```python
"""トークナイザーの中身と、チャットテンプレートが作る実際の入力を見る。"""
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
print(f"{type(tok).__name__}  vocab={tok.vocab_size:,}  eos={tok.eos_token!r}  pad={tok.pad_token!r}")

for text in ("How do I submit an expense report?", "経費精算はどうやって申請しますか？"):
    ids = tok(text)["input_ids"]
    pieces = [tok.decode([i]) for i in ids]
    print(f"{len(text):3d} 文字 → {len(ids):3d} トークン  {pieces}")

messages = [
    {"role": "system", "content": "あなたは社内ヘルプデスクです。"},
    {"role": "user", "content": "有給休暇の申請方法は？"},
]
prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
print("--- apply_chat_template(tokenize=False) ---")
print(prompt, end="")
print("--- apply_chat_template() の戻り値 ---")
enc = tok.apply_chat_template(messages, add_generation_prompt=True, enable_thinking=False, return_tensors="pt")
print(type(enc).__name__, {k: tuple(v.shape) for k, v in enc.items()})
```

実行結果:

```text
$ uv run python 03_tokenizer.py
Qwen2Tokenizer  vocab=151,643  eos='<|im_end|>'  pad='<|endoftext|>'
 34 文字 →   8 トークン  ['How', ' do', ' I', ' submit', ' an', ' expense', ' report', '?']
 17 文字 →  11 トークン  ['�', '�', '費', '精', '算', 'はどう', 'やって', '申請', 'します', 'か', '？']
--- apply_chat_template(tokenize=False) ---
<|im_start|>system
あなたは社内ヘルプデスクです。<|im_end|>
<|im_start|>user
有給休暇の申請方法は？<|im_end|>
<|im_start|>assistant
<think>

</think>

--- apply_chat_template() の戻り値 ---
BatchEncoding {'input_ids': (1, 36), 'attention_mask': (1, 36)}
```

- **英語は 1 単語がほぼ 1 トークン、日本語は 1〜2 文字が 1 トークン**になりやすい。API の料金やコンテキスト長はトークン数で決まるので、日本語は同じ内容でも多めに数える
- 「経」が `'�', '�'` の 2 つに分かれているのは、UTF-8 のバイト単位で分割されたためである。1 トークンずつ `decode` すると文字の途中で切れて表示が崩れるが、並びごと `decode` すれば元に戻る
- チャットテンプレートは、役割（system / user / assistant）を `<|im_start|>` のような特殊なトークンで区切った文字列を作る。書式はモデルごとに違うため、自分で組み立てずに `apply_chat_template` に任せる
- `enable_thinking=False` は Qwen3 のテンプレートが受け取る引数で、空の `<think></think>` を先に入れて「考える過程」を省かせる
- **v5 では `apply_chat_template` が `BatchEncoding`（`input_ids` と `attention_mask` の辞書）を返す**。v4 では `input_ids` だけを返していたため、古い記事のコードはそのままでは動かないことがある

### 5.4 generate() — 資料を渡して答えさせる

`AutoModelForCausalLM` と `generate()` を直接使う。同じ質問に、資料なしと、FAQ の答えを system に入れた場合とで答えを比べる（検証済み）。

```python
"""AutoModelForCausalLM と generate() を直接使い、参考資料の有無で答えが変わるのを見る。"""
import json
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-0.6B"
device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype="auto", device_map=device)
print(f"device={model.device}  dtype={model.dtype}  params={model.num_parameters():,}")

faq = [json.loads(line) for line in open("../../_shared/faq.jsonl", encoding="utf-8")]
question = "経費精算の締め日はいつですか？"


def ask(system: str) -> None:
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    inputs = tok.apply_chat_template(
        messages, add_generation_prompt=True, enable_thinking=False, return_tensors="pt"
    ).to(model.device)
    t0 = time.perf_counter()
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
    elapsed = time.perf_counter() - t0
    new_tokens = out[0, inputs["input_ids"].shape[1]:]  # 入力部分を除いた、生成された部分だけ
    print(f"[入力 {inputs['input_ids'].shape[1]} トークン → 出力 {len(new_tokens)} トークン, {len(new_tokens) / elapsed:.1f} tok/s]")
    print(tok.decode(new_tokens, skip_special_tokens=True))


print("--- 参考資料なし ---")
ask("あなたは社内ヘルプデスクです。")
print("--- 参考資料あり ---")
ask("あなたは社内ヘルプデスクです。次の資料だけを根拠に答えてください。\n" + faq[0]["answer"])
```

実行結果:

```text
$ uv run python 04_generate.py
…（中略: 2 行）…
device=mps:0  dtype=torch.bfloat16  params=596,049,920
--- 参考資料なし ---
[入力 41 トークン → 出力 62 トークン, 97.0 tok/s]
経費精算の締め日は、社内制度によって異なります。ご社内制度によって、締め日は異なる場合があります。ご社内制度の詳細は、社内ヘルプデスクや経費管理課にご相談ください。
--- 参考資料あり ---
[入力 94 トークン → 出力 51 トークン, 90.8 tok/s]
経費精算の締め日は、毎月 25 日です。25 日までに経費システムで申請すると、翌月 10 日に給与口座へ振り込まれます。
```

- **資料を入力に入れれば、小さなモデルでも正しく答えられる**。これが RAG（検索で資料を探して入力に足す方法）の基本である。資料を探す部分は §5.5 の埋め込みが担う
- `generate()` の戻り値は「入力＋生成」の全体なので、入力の長さで切って生成部分だけを取り出す
- `params=596,049,920` は、§5.1 の 751,632,384 より約 1.56 億少ない。Qwen3-0.6B は入力側の埋め込み表と出力側の `lm_head` で同じ重みを共有する（`tie_word_embeddings: true`）が、配布ファイルには両方が入っている。`num_parameters()` は共有分を 1 回だけ数える
- 速度（約 90〜97 トークン/秒）は参考値である

### 5.5 埋め込みで FAQ を検索する

`intfloat/multilingual-e5-small` で FAQ と質問をベクトルにし、近いものを探す。モデルカードの指示どおり、文書には `passage: `、質問には `query: ` を付け、パディングを除いた平均を取る（検証済み）。

```python
"""multilingual-e5-small で FAQ を埋め込み、言い換えた質問から近い FAQ を探す。"""
import json

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

MODEL = "intfloat/multilingual-e5-small"
device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModel.from_pretrained(MODEL, device_map=device).eval()


def embed(texts: list[str]) -> torch.Tensor:
    batch = tok(texts, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
    with torch.inference_mode():
        hidden = model(**batch).last_hidden_state
    mask = batch["attention_mask"].unsqueeze(-1)
    pooled = (hidden * mask).sum(1) / mask.sum(1)  # パディングを除いた平均（モデルカードの average_pool）
    return F.normalize(pooled, dim=-1)  # 長さ 1 にそろえると、内積がそのままコサイン類似度になる


faq = [json.loads(line) for line in open("../../_shared/faq.jsonl", encoding="utf-8")]
doc_vecs = embed([f"passage: {f['question']} {f['answer']}" for f in faq])
print(f"FAQ {len(faq)} 件 → {tuple(doc_vecs.shape)}")

queries = ["レシートを紛失してしまいました", "来週お休みを取りたい", "パスワードを忘れた"]
scores = embed([f"query: {q}" for q in queries]) @ doc_vecs.T
for q, row in zip(queries, scores):
    best = row.topk(3)
    print(q)
    for s, i in zip(best.values.tolist(), best.indices.tolist()):
        print(f"  {s:.3f}  {faq[i]['id']}  {faq[i]['question']}")
```

実行結果:

```text
$ uv run python 05_embed_search.py
…（中略: 2 行）…
FAQ 12 件 → (12, 384)
レシートを紛失してしまいました
  0.849  faq-06  パスワードを忘れました。
  0.844  faq-12  不審なメールを受け取りました。
  0.839  faq-02  領収書をなくした場合はどうすればよいですか？
来週お休みを取りたい
  0.819  faq-04  在宅勤務は週に何日までできますか？
  0.815  faq-03  有給休暇はどうやって申請しますか？
  0.812  faq-06  パスワードを忘れました。
パスワードを忘れた
  0.897  faq-06  パスワードを忘れました。
  0.857  faq-12  不審なメールを受け取りました。
  0.838  faq-05  社内 VPN につながりません。
```

- 「パスワードを忘れた」は正しく 1 位になった。一方、「レシート→領収書」「お休み→有給休暇」の言い換えは 1 位を外し、正解は 3 位と 2 位にある
- 実装の誤りを疑い、同じモデルを sentence-transformers 6.2.0（埋め込み用の定番ライブラリ）で動かして比べた。上位 3 件のスコアは小数第 3 位まで一致した（検証済み、ログは `05b_crosscheck.log`）。**実装の誤りではなく、このデータとこの入れ方での結果である**
- スコアが 0.8 前後に固まっているのは e5 の特徴で、モデルカードにも「スコアの絶対値ではなく順位で使う」旨の説明がある。しきい値を決め打ちにせず、上位 k 件を取る
- 実務では、上位 3 件ほどを LLM に渡せば、1 位を外しても資料は入力に入る（§6.2 で recall@3 として測る）

### 5.6 バッチで問い合わせを分類する

複数の入力をまとめて `generate()` に渡すと、1 件ずつより速い。長さの違う入力を揃えるため、**詰め物（パディング）を左に寄せる**（検証済み）。

```python
"""問い合わせ文をまとめて分類する。バッチ生成では padding を左に寄せる。"""
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3-4B-Instruct-2507"
LABELS = ["経費", "勤怠", "IT", "総務", "出張", "セキュリティ"]
device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")  # 末尾から生成を続けるため、詰め物は左
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype="auto", device_map=device)

tickets = [
    "タクシー代の精算方法を教えてください",
    "明日の午後に半休を取りたいです",
    "Wi-Fi が頻繁に切れます",
    "来月の大阪出張の新幹線を手配したい",
    "知らない差出人から添付ファイル付きのメールが来た",
    "会議室のプロジェクターが映りません",
]
system = f"問い合わせを次のどれか 1 つに分類し、ラベルだけを答えてください: {'、'.join(LABELS)}"
prompts = [
    tok.apply_chat_template(
        [{"role": "system", "content": system}, {"role": "user", "content": t}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False,
    )
    for t in tickets
]
batch = tok(prompts, padding=True, return_tensors="pt").to(model.device)
print(f"{MODEL}  batch input_ids: {tuple(batch['input_ids'].shape)}")

t0 = time.perf_counter()
out = model.generate(**batch, max_new_tokens=8, do_sample=False)
print(f"generate: {time.perf_counter() - t0:.2f}s for {len(tickets)} tickets")
for t, ids in zip(tickets, out[:, batch["input_ids"].shape[1]:]):
    label = tok.decode(ids, skip_special_tokens=True).strip()
    print(f"{label if label in LABELS else '?' + label} ← {t}")
```

まず 0.6B で動かした。

実行結果:

```text
$ uv run python 06_batch_classify.py Qwen/Qwen3-0.6B
…（中略: 2 行）…
Qwen/Qwen3-0.6B  batch input_ids: (6, 74)
generate: 0.25s for 6 tickets
IT ← タクシー代の精算方法を教えてください
IT ← 明日の午後に半休を取りたいです
IT ← Wi-Fi が頻繁に切れます
IT ← 来月の大阪出張の新幹線を手配したい
IT ← 知らない差出人から添付ファイル付きのメールが来た
IT ← 会議室のプロジェクターが映りません
```

すべて「IT」になった。1 件ずつ生成しても、各ラベルの確率を直接比べても、全件「IT」のままだった。回答例を会話に入れる（few-shot）と、半休の 1 件だけが「勤怠」に直った（検証済み、ログは `06c_fewshot.log`・`06d_one_by_one.log`・`06e_label_logprob.log`）。
0.6B は、このプロンプトでは分類できなかった。原因がモデルの大きさか、プロンプトの書き方かは切り分けていない。そこで、同じ Qwen3 の 4B で考える過程を出さない版（`Qwen3-4B-Instruct-2507`）に替えた。

実行結果:

```text
$ uv run python 06_batch_classify.py
…（中略: 2 行）…
Qwen/Qwen3-4B-Instruct-2507  batch input_ids: (6, 70)
generate: 1.26s for 6 tickets
経費 ← タクシー代の精算方法を教えてください
勤怠 ← 明日の午後に半休を取りたいです
IT ← Wi-Fi が頻繁に切れます
出張 ← 来月の大阪出張の新幹線を手配したい
セキュリティ ← 知らない差出人から添付ファイル付きのメールが来た
IT ← 会議室のプロジェクターが映りません
```

- 4B では、意図したラベルが付いた（プロジェクターの件は「IT」と「総務」のどちらとも取れる）
- `batch input_ids: (6, 70)` は、6 件を最も長い 70 トークンに揃えたことを示す。短い入力の左側に `pad` トークンが詰められ、`attention_mask` が 0 になってモデルに無視される
- 公式の [Text generation](https://huggingface.co/docs/transformers/llm_tutorial) は、LLM は詰め物の後ろから生成を続けるように学習されていないため、`padding_side="left"` にするよう書いている
- 出力をラベルの一覧と照らし、一覧に無い答えは `?` を付けて区別している。LLM の出力は決まった形になる保証が無いので、受け取る側で必ず確かめる

> **ポイント**: 小さなモデルで動かないとき、プロンプトを延々と直す前に、一段大きなモデルで同じことができるかを試すと早い。ただし、ここでは大きさと版（考える過程を出さない Instruct-2507）を同時に替えたので、どちらが効いたかは分からない。原因を切り分けたいなら、替えるものを 1 つずつにする。

### 5.7 transformers serve — OpenAI 互換の API として配信する

`transformers serve` は、読み込んだモデルを OpenAI 互換の API（`/v1/chat/completions` など）として配信する。上の層のエージェントは、この API を呼ぶだけでよい（検証済み）。

```bash
uv run transformers serve Qwen/Qwen3-4B-Instruct-2507 --port 8001
```

モデル名を引数に渡すと、そのモデルを最初から読み込み、すべてのリクエストに使う。省略すると、リクエストの `model` に応じて読み込み、使われなくなると一定時間（既定 300 秒）で外す。
既定のポートは 8000 だが、シリーズでは vLLM と分けるため 8001 にした。

curl で呼ぶ（検証済み）。

```bash
#!/usr/bin/env bash
# transformers serve の /v1/chat/completions を curl で呼ぶ
curl -s http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-4B-Instruct-2507",
    "messages": [{"role": "user", "content": "社内 VPN につながらないときに最初に確かめることを 1 つだけ挙げてください。"}],
    "max_tokens": 60,
    "temperature": 0
  }' | python3 -m json.tool --no-ensure-ascii
```

実行結果:

```text
$ ./07_serve_curl.sh
{
    "id": "367ca132-d93f-4b59-8948-f534735d1063",
    "choices": [
        {
            "finish_reason": "length",
            "index": 0,
            "message": {
                "content": "社内 VPN につながらないときに最初に確かめることとして、**インターネット接続が正常か**を確認します。\n\n理由：VPN が使えない原因の多くは、そもそもネットワークが接続されていない（Wi-Fi が落ちている、回線が切れている",
                "role": "assistant"
            }
        }
    ],
…（中略: 3 行）…
    "usage": {
        "completion_tokens": 60,
        "prompt_tokens": 33,
        "total_tokens": 93
    }
}
```

`finish_reason: "length"` は、`max_tokens` の 60 トークンに達して途中で切れたことを示す。最後まで答えさせるなら上限を上げる。

OpenAI の公式クライアントからも、`base_url` を変えるだけで呼べる。ストリーミング（生成された順に少しずつ受け取る）も使える（検証済み）。

```python
"""OpenAI の公式クライアントで transformers serve を呼ぶ。base_url を変えるだけで配信の層を差し替えられる。"""
import time

from openai import OpenAI

client = OpenAI(base_url="http://localhost:8001/v1", api_key="local-dummy")  # キーは検証されないが、引数は必須
t0 = time.perf_counter()
first = None
stream = client.chat.completions.create(
    model="Qwen/Qwen3-4B-Instruct-2507",
    messages=[{"role": "user", "content": "会議室の予約方法を、手順 3 つの箇条書きで答えてください。"}],
    max_tokens=120,
    temperature=0,
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content if chunk.choices else None
    if delta:
        first = first or time.perf_counter() - t0
        print(delta, end="", flush=True)
print(f"\n[最初のトークンまで {first:.2f}s / 全体 {time.perf_counter() - t0:.2f}s]")
```

実行結果:

```text
$ uv run python 07_serve_openai.py
- **予約希望の日時を確認する**：会議室の利用可能な日時を、事前に管理システムや担当者に確認します。曜日、時間帯、会議室のサイズや設備（プロジェクター、白板など）に応じて選択します。

- **予約申請を提出する**：会議室の予約フォームやメール、オンラインシステムに必要情報を入力し、申請を提出します。担当者に確認が必要な場合は、その旨を明記します。

- **予
[最初のトークンまで 0.77s / 全体 4.48s]
```

- 答えが一般論なのは、社内の手順を知らないためである（§5.4 と同じ）。FAQ を渡すのは、上の層のエージェントの仕事になる
- `api_key` は検証されないが、OpenAI クライアントは空だと起動しないので、ダミーを入れる
- `GET /v1/models` は、ローカルのキャッシュにあるモデルを一覧に出す（公式の Serve CLI のページに "scans your local Hugging Face cache" とある）。手元では MLX 形式のものまで並んだ（検証済み、ログは `07_serve_models.log`）
- 同じクライアントのコードは、`base_url` を MLX-LM（8080）や vLLM（8000）に向けても動く。これが索引の [§3](README.md#3-全体像--4-つの層とつなぎ目) の「③ → ④ のつなぎ目は OpenAI 互換 API」である

---

## 6. 実務での使いどころ

### 6.1 ユースケース

| ユースケース | 入力 → 出力 | Transformers を使う理由 | 本番で足すもの |
|---|---|---|---|
| 社内文書の埋め込み検索（RAG の検索部分） | 文書と質問 → 近い文書の上位 k 件 | 埋め込みモデルを手元で動かせ、データを外に出さない | ベクトル DB、文書の分割、再ランキング |
| 埋め込みモデル・LLM の選定 | 候補のモデルと手元のデータ → 正解率・速度 | 同じコードで候補を入れ替えて比べられる | 評価データを増やす、定期的な再評価 |
| 問い合わせの分類・情報の抽出 | 文章 → ラベル・項目 | 小さめのモデルを手元でバッチ処理できる | 出力の検証、人の確認、件数が多ければ推論サーバー |
| 新しいモデルの試用 | モデル名 → 出力・トークン数・メモリ | 公開直後のモデルもすぐ動くことが多い | ライセンスの確認、本番は推論サーバーへ |

### 6.2 代表例: 埋め込みモデルを選ぶための評価 CLI

§5.5 で、e5-small は言い換えた質問の一部で 1 位を外した。大きい e5-base に替えれば良くなるのか。思い込みで選ばず、手元の FAQ と言い換えた質問 12 件で測る。

評価用の質問は、FAQ 1 件につき 1 つ、言い回しを変えて作り、正解の FAQ の ID を付ける（抜粋・単体では動かない）。

```text
{"query": "交通費の精算はいつまでに出せばいい？", "expected": "faq-01"}
{"query": "レシートを紛失してしまいました", "expected": "faq-02"}
{"query": "来週お休みを取りたい", "expected": "faq-03"}
…（中略: 9 行）…
```

評価のスクリプト。モデル名を並べて渡すと、それぞれの recall@1・recall@3（正解が上位 1 件・3 件に入った割合）と、1 件あたりの処理時間を出す（検証済み）。

```python
"""埋め込みモデルの候補を、手元の FAQ と言い換えた質問で比べる（recall@k と速度）。

usage: python eval_embeddings.py <faq.jsonl> <queries.jsonl> <model>...
"""
import json
import sys
import time

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"


def load_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate(name: str, faq: list[dict], queries: list[dict], ks=(1, 3)) -> None:
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModel.from_pretrained(name, device_map=device).eval()

    def embed(texts: list[str]) -> torch.Tensor:
        batch = tok(texts, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
        with torch.inference_mode():
            hidden = model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1)
        return F.normalize((hidden * mask).sum(1) / mask.sum(1), dim=-1)

    docs = embed([f"passage: {f['question']} {f['answer']}" for f in faq])
    embed(["query: warmup"])  # 初回呼び出しの準備時間を計測から外す
    t0 = time.perf_counter()
    q = embed([f"query: {x['query']}" for x in queries])
    ms = (time.perf_counter() - t0) * 1000 / len(queries)

    ranked = (q @ docs.T).argsort(dim=1, descending=True).cpu()
    ids = [f["id"] for f in faq]
    recall = {k: sum(x["expected"] in [ids[i] for i in row[:k]] for x, row in zip(queries, ranked)) for k in ks}
    misses = [(x["query"], ids[row[0]]) for x, row in zip(queries, ranked) if ids[row[0]] != x["expected"]]
    print(f"{name}  params={model.num_parameters() / 1e6:.0f}M  {ms:.1f} ms/query  "
          + "  ".join(f"recall@{k}={recall[k]}/{len(queries)}" for k in ks))
    for query, got in misses:
        print(f"  miss: {query} → {got}")


if __name__ == "__main__":
    faq_path, query_path, *models = sys.argv[1:]
    faq, queries = load_jsonl(faq_path), load_jsonl(query_path)
    for name in models:
        evaluate(name, faq, queries)
```

実行結果:

```text
$ uv run python eval_embeddings.py ../../_shared/faq.jsonl eval_queries.jsonl intfloat/multilingual-e5-small intfloat/multilingual-e5-base
…（中略: 2 行）…
intfloat/multilingual-e5-small  params=118M  0.9 ms/query  recall@1=10/12  recall@3=12/12
  miss: レシートを紛失してしまいました → faq-06
  miss: 来週お休みを取りたい → faq-04
…（中略: 1 行。読み込みの進捗）…
intfloat/multilingual-e5-base  params=278M  0.8 ms/query  recall@1=9/12  recall@3=11/12
  miss: レシートを紛失してしまいました → faq-06
  miss: 来週お休みを取りたい → faq-04
  miss: 打ち合わせ部屋を押さえたい → faq-09
```

- **このデータでは、パラメータが 2 倍以上の e5-base でも成績は良くならなかった**。差は recall@1・recall@3 とも 12 問中 1 問で、どちらが優れているとは言えない。言えるのは「大きいモデルが自分のデータで良いとは限らない」までである
- e5-small は recall@3 が 12/12 なので、上位 3 件を LLM に渡す設計なら、この FAQ では取りこぼしが無い。1 位だけを使う設計（答えをそのまま返すなど）なら 2 件外れる
- 処理時間は 12 件を 1 回にまとめて処理したときの 1 件あたりで、参考値である。どちらも 1 ミリ秒前後で、この規模では差にならない
- 12 件は判断材料としては少なく、文書の入れ方（質問だけにするか、質問と答えを連結するか）でも結果は変わり得る。本番の前には、実際の問い合わせから質問を集めて評価データを増やし、モデルを替えるたびに同じスクリプトで測り直す

> **ポイント**: 評価のスクリプトとデータを先に用意しておくと、「新しいモデルが出たから替えるか」を、毎回同じ物差しで数分で判断できる。

### 6.3 その他のユースケースの素描

- **RAG の組み立て**: §5.5 の検索で上位 3 件を取り、§5.4 のように system に入れて答えさせる。エージェントの層（[LangGraph](README.md#2-ドキュメント一覧) など）で組むと、検索をツールとして呼ばせられる
- **分類の大量処理**: §5.6 を数万件に広げるなら、Transformers のバッチ処理より、[vLLM](README.md#2-ドキュメント一覧) のオフライン推論のほうが速い。少量なら Transformers で十分である
- **出力の書式を揃えたい**: プロンプトで足りなければ、[TRL + PEFT](trl-peft.md) で追加学習する。その前に、本ドキュメントのように一段大きなモデルを試す

---

## 7. 本番運用の要点

- **大規模な配信は推論サーバーに任せる**。公式の Serve CLI のページは `transformers serve` を「評価・実験・中程度の負荷」向けとし、"For large scale production deployments, use vLLM or SGLang with a Transformer model as the backend." と書いている
- **モデルのリビジョンを固定する**。Hub のモデルは同じ名前のまま更新されることがある。`from_pretrained(name, revision="<コミットの SHA>")` で版を固定すると、ある日突然出力が変わる事故を防げる（`model_info(repo).sha` で最新の SHA を取れる）
- **`trust_remote_code=True` は中身を読んでから使う**。Hub のリポジトリに置かれた Python コードを手元で実行する設定である。既定は `False` で、Transformers に組み込まれたモデルなら不要である
- **重みは safetensors 形式を使う**。読み込み時にコードを実行しないため、pickle 形式（`.bin`）より安全である
- **オフラインの本番環境**では、事前にモデルを落としておき、`HF_HUB_OFFLINE=1` で Hub への通信を止める
- **NVIDIA GPU では** `device_map="auto"` で複数の GPU に分けて載せたり、bitsandbytes で 4bit / 8bit に量子化して載せたりできる（公式 docs 準拠・未実行: NVIDIA GPU が必要）

---

## 8. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 小さなモデルが、指示を無視して同じ答えを返す（実測） | モデルの力が足りない可能性がある（本ドキュメントでは未切り分け） | 一段大きなモデルで同じ処理を試し、原因を切り分ける（§5.6） |
| 言い換えた質問で、埋め込み検索が 1 位を外す（実測） | 埋め込みモデルの限界。大きいモデルで直るとは限らない | 上位 k 件を使う。自分のデータで評価してから選ぶ（§6.2） |
| v4 の記事のコードで、`apply_chat_template` の戻り値をテンソルとして扱うとエラーになる | v5 から `BatchEncoding`（辞書）を返す | `model.generate(**inputs)` のように展開して渡す（§5.4） |
| `torch_dtype` は非推奨という警告が出る | v4.56 で `dtype` に改名された | `dtype="auto"` と書く |
| 古い記事の `batch_decode` を使い続けてよいか迷う | v5 で `decode` がバッチをそのまま受け取るようになった。`batch_decode` も互換のために残る | 新しく書くなら `tok.decode(ids)` に統一する |
| バッチ生成の出力が崩れる | 詰め物が右にある | `padding_side="left"` でトークナイザを作る（§5.6） |
| `Warning: You are sending unauthenticated requests to the HF Hub` | トークン無しで Hub に問い合わせている | 公開モデルならそのままで動く。回数制限を緩めたい・gated なモデルを使うときは `hf auth login` か `HF_TOKEN` を設定する |
| Qwen3 の出力に `<think>` が混ざる | 思考モードが既定で有効 | `enable_thinking=False` を渡す。`Qwen3-4B-Instruct-2507` は思考モードの無い版で、指定は要らない |

---

## 9. 次のステップ

- 自前のデータで追加学習する: [TRL + PEFT](trl-peft.md) で、本ドキュメントのモデルに LoRA で FAQ の答え方を学ばせる
- 配信を本格的にする: [MLX-LM](README.md#2-ドキュメント一覧)（Mac）・[vLLM](README.md#2-ドキュメント一覧)・[SGLang](README.md#2-ドキュメント一覧)。§5.7 のクライアントのコードは `base_url` を変えるだけで使い回せる
- 公式ドキュメントの続き: [Tool use](https://huggingface.co/docs/transformers/chat_extras)（チャットテンプレートでのツール呼び出しの書式）、[Text generation](https://huggingface.co/docs/transformers/llm_tutorial) の生成戦略

---

## 出典

| 情報源 | URL |
|---|---|
| Transformers documentation | https://huggingface.co/docs/transformers/index （2026-11-08 確認） |
| Transformers v5 Migration guide | https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md （2026-11-08 確認、Context7 `/huggingface/transformers` 経由。TensorFlow と JAX の除去・`apply_chat_template` が `BatchEncoding` を返す・`batch_decode` の統合・`use_auth_token` から `token` へ） |
| Chat templates | https://huggingface.co/docs/transformers/chat_templating （2026-11-08 確認） |
| Tool use | https://huggingface.co/docs/transformers/chat_extras （2026-11-08 確認） |
| Text generation | https://huggingface.co/docs/transformers/llm_tutorial （2026-11-08 確認。`padding_side="left"` の理由） |
| Serve CLI | https://huggingface.co/docs/transformers/serving （2026-11-08 確認。用途の位置づけ・大規模な本番には vLLM / SGLang を勧める記述・`/v1/models` がキャッシュを走査すること） |
| Pipelines | https://huggingface.co/docs/transformers/main_classes/pipelines （2026-11-08 確認） |
| `from_pretrained` の `dtype` | https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_utils.py （2026-11-08 確認、Context7 経由。`torch_dtype` は後方互換のために残る。非推奨の警告は v4.56.0 のソースから入っている） |
| Qwen/Qwen3-0.6B | https://huggingface.co/Qwen/Qwen3-0.6B （2026-11-08 確認。`enable_thinking`・推奨のサンプリング設定・thinking モードで greedy を避ける注意） |
| Qwen/Qwen3-4B-Instruct-2507 | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 （2026-11-08 確認。思考モードの無い版で、`enable_thinking=False` が不要） |
| intfloat/multilingual-e5-small | https://huggingface.co/intfloat/multilingual-e5-small （2026-11-08 確認。`query: ` / `passage: ` の接頭辞・average_pool・スコアの分布） |
| GitHub `huggingface/transformers` | ★168,629・v5.22.2（2026-11-06 公開）（2026-11-08 に GitHub API で取得） |

### 確認できなかった事項

- **§6.2 の e5-small と e5-base の差**は 12 問中 1 問で、統計的な差かどうかは言えない
- **§5.6 で 0.6B が分類できなかった理由**のうち、モデルの力とプロンプトの書き方のどちらがどれだけ効いているかは切り分けていない。4B では同じプロンプトで分類できたことだけを確かめた
- **MPS 上の速度**は、この Mac での 1 回の計測である（索引 [7.3](README.md#73-コード例の状態ラベル) の参考値の扱い）

- 関連: [AI フレームワーク学習ガイド](README.md) / [PyTorch](pytorch.md) / [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md) / [モデル比較](../model-comparison.md)
