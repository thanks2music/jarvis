# AI フレームワーク学習ガイド — 深層学習の基盤から推論サーバー・エージェントまで

> 出典（一次情報）:
> - [What's new in TensorFlow 2.21 (developers.googleblog.com)](https://developers.googleblog.com/whats-new-in-tensorflow-221/) — TensorFlow が保守中心になったこと、新しい生成 AI の開発に Keras 3 / JAX / PyTorch を推奨していること
> - [Transformers v5 Migration guide (github.com)](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) — Transformers が PyTorch だけをバックエンドにしたこと
> - [huggingface/text-generation-inference README (github.com)](https://github.com/huggingface/text-generation-inference) — TGI がメンテナンスモードに入り、vLLM / SGLang などを推奨していること
> - [microsoft/autogen README (github.com)](https://github.com/microsoft/autogen) — AutoGen がアーカイブされ、後継が Microsoft Agent Framework であること
> - [vLLM Quickstart (docs.vllm.ai)](https://docs.vllm.ai/en/stable/getting_started/quickstart/) — Apple Silicon では vLLM-Metal を使うこと
> - [Apple Metal (docs.sglang.io)](https://docs.sglang.io/docs/hardware-platforms/apple_metal) — SGLang を Mac で動かす方法
>
> 最終更新: 2026-11-08（★・最新版・活動量は 2026-11-08 に GitHub API と PyPI / npm で取得）

LLM や機械学習のフレームワークを知らない開発者が、**どれが何をするもので、どう組み合わさり、仕事のどこで使えるのか**を
順に学ぶためのシリーズである。各ドキュメントのコード例は、手元の Mac（Apple M2 Max）で実際に実行し、その出力を載せている。
NVIDIA GPU が必要な本番構成は、公式 docs に沿って書き、未実行であることを明記した。

API の料金やモデルの選び方は [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md) と
[モデル比較とプラン制限](../model-comparison.md) を、複数のエージェントを組み合わせる設計は [ハーネス設計ガイド](../harness.md) を参照。

---

## 1. TL;DR

- 15 のフレームワークは、**4 つの層**に分かれる: 深層学習の基盤（PyTorch など）→ モデルと学習（Transformers など）→ 推論・配信（vLLM など）→ エージェント / LLM アプリ（LangGraph など）（§3）。
- **層と層は「ファイル」と「API」でつながる**。特に、推論の層とエージェントの層のつなぎ目は **OpenAI 互換 API**（`/v1/chat/completions`）である。配信に MLX-LM・vLLM・SGLang のどれを使っても、エージェントの側は `base_url` を変えるだけで済む（Claude Agent SDK は例外で、Anthropic の API か、Bedrock などのクラウド経由で Claude を使う）。
- **LLM アプリを作りたい Web 開発者は、エージェントの層から読めばよい**。モデルを自前で動かしたい人や、ML を基礎から学びたい人のための道順も用意した（§4）。
- ⚠️ **TensorFlow は 2026-03 から保守中心になった**。Google 自身が、新しい生成 AI の開発には Keras 3 / JAX / PyTorch を勧めている。本シリーズでは、既存の資産を読み・保守するための内容に絞った。
- 新しく採用しないほうがよいもの（アーカイブ済み・非推奨）を、日付つきの一次情報とともに §5.2 にまとめた。

---

## 2. ドキュメント一覧

| 層 | ドキュメント | 一言で | 主な言語 | Mac での動作 | ★ / 最新版（2026-11-08） |
|---|---|---|---|---|---|
| 深層学習の基盤 | [PyTorch](pytorch.md) | テンソル・自動微分・学習ループ。LLM 周辺の主要 OSS の土台 | Python | MPS（Apple GPU） | 105k / 2.15.0 |
| 深層学習の基盤 | [JAX](jax.md) | `jit` / `grad` / `vmap` の関数変換。TPU と Google 系の研究コード | Python | CPU | 36.6k / 0.12.0.1 |
| 深層学習の基盤 | [Keras 3](keras.md) | 高水準 API。バックエンドに JAX / PyTorch / TensorFlow を選べる | Python | バックエンド次第 | 64.4k / 3.15.1 |
| 深層学習の基盤 | [TensorFlow](tensorflow.md) | 既存資産（SavedModel・TF Serving・LiteRT）の保守。**保守中心** | Python | CPU | 201k / 2.21.0 |
| モデルと学習 | Transformers（準備中） | 学習済みモデルを読み込み、推論・埋め込み・微調整する | Python | MPS | 169k / 5.22.2 |
| モデルと学習 | TRL + PEFT（準備中） | 自前のデータで追加学習する（SFT / DPO / LoRA） | Python | MPS（一部） | 19.7k・21.9k / 1.17.1・0.21.2 |
| 推論・配信 | MLX-LM（準備中） | Mac で LLM を動かす・配信する・LoRA で微調整する | Python | Metal（ネイティブ） | 7.6k / 0.32.2 |
| 推論・配信 | vLLM（準備中） | PagedAttention と continuous batching で高スループットを出す推論サーバー | Python | vLLM-Metal（community） | 96.5k / 0.33.0 |
| 推論・配信 | SGLang（準備中） | 共通の前置き（prefix）が多い処理と構造化出力に強い推論サーバー | Python | Metal / MLX | 38.6k / 0.5.23 |
| エージェント | LangGraph（準備中） | 状態・分岐・承認・再開を持つエージェントをグラフで書く。JS 版も扱う | Python / TS | ○ | 44.6k / 1.2.20 |
| エージェント | Pydantic AI（準備中） | 型付きの出力とテストしやすさを重視したエージェント | Python | ○ | 21.1k / 2.66.0 |
| エージェント | OpenAI Agents SDK（準備中） | handoff・ガードレールを中心にした軽量な SDK | Python / TS | ○ | 30.5k / 0.24.0 |
| エージェント | Claude Agent SDK（準備中） | Claude Code と同じエージェントの仕組みをアプリに組み込む | Python / TS | Anthropic API 経由（本シリーズではローカル LLM につながない） | 8.5k / 0.2.179 |
| エージェント | Vercel AI SDK（準備中） | Next.js / Node で LLM の呼び出し・ストリーミング・ツールを書く | TS | ○ | 27.8k / ai 7.0.164 |
| エージェント | Mastra（準備中） | TS 製のエージェント・ワークフロー・メモリ・評価の一式 | TS | ○ | 29.4k / 1.82.0 |

> **注意**: ★は GitHub のスター数で、人気の目安にすぎない。版は執筆時点のもので、各ドキュメントは記載の版で検証している。
> エージェント層の「○」は、手元のローカル LLM サーバー（MLX-LM）につないで動かせることを表す。Claude Agent SDK は Claude のモデルを使う前提の SDK で、本シリーズではローカルの LLM にはつながない。

---

## 3. 全体像 — 4 つの層とつなぎ目

![4 つの層の積み上げ図。下から ① 深層学習の基盤（PyTorch・JAX・Keras 3・TensorFlow〈保守中心〉）、② モデルと学習（Transformers・TRL + PEFT）、③ 推論・配信（MLX-LM・vLLM・SGLang）、④ エージェント / LLM アプリ（LangGraph・Pydantic AI・OpenAI Agents SDK・Vercel AI SDK・Mastra・Claude Agent SDK）。層の間の上向きの矢印に、受け渡すもの（モデルの重み〈safetensors〉、重み・LoRA アダプタ、OpenAI 互換 API）が書かれている。Claude Agent SDK だけは ③ を通らず Anthropic API に直接つながる](../images/ai-frameworks/layers.png)

| 層 | 役割 | このシリーズのドキュメント |
|---|---|---|
| ① 深層学習の基盤 | テンソルの計算・自動微分・学習ループを提供する | PyTorch / JAX / Keras 3 / TensorFlow |
| ② モデルと学習 | 公開された学習済みモデルを読み込んで使う。自前のデータで追加学習する | Transformers / TRL + PEFT |
| ③ 推論・配信 | モデルを効率よく動かし、API として多数の利用者に提供する | MLX-LM / vLLM / SGLang |
| ④ エージェント / LLM アプリ | LLM にツールを使わせ、手順・状態・承認を組み立てて業務を進める | LangGraph / Pydantic AI / OpenAI Agents SDK / Claude Agent SDK / Vercel AI SDK / Mastra |

層と層の 3 つの境目と、④ の中の 1 つの取り決めで受け渡す。どの層の道具を替えても、この受け渡しの形が同じなら残りの層はそのまま使える。

| つなぎ目 | 受け渡すもの | 例 |
|---|---|---|
| ① → ② | **モデルの重み**（safetensors 形式のファイル） | PyTorch で書かれたモデルの重みを、Hugging Face Hub から Transformers で読む（Transformers v5 が読むのは PyTorch のモデルだけ） |
| ② → ③ | **重みと LoRA アダプタ** | TRL + PEFT で作ったアダプタを、vLLM や MLX-LM に載せる |
| ③ → ④ | **OpenAI 互換 API**（`/v1/chat/completions`） | MLX-LM のサーバーに、LangGraph や Vercel AI SDK から `base_url` で接続する |
| ④ の中 | **ツール呼び出しと JSON Schema の取り決め** | エージェントが「検索ツールをこの引数で呼ぶ」と LLM に返させ、フレームワークが実行する |

**通し課題**: シリーズを通して、架空の会社の「社内 FAQ」12 件（経費・勤怠・IT・セキュリティなど。§7.4）を共通の題材にする。
Transformers で文章を数値にして検索し、TRL + PEFT や MLX-LM で FAQ の答え方を学習させ、MLX-LM で API として配信し、
エージェントの層から「社内の問い合わせに答えるエージェント」として呼び出す。層を順にたどると、1 つの業務システムが組み上がる。

---

## 4. 学習ロードマップ

目的に応じて、3 つの道順を用意した。どの道順でも、§6 の用語集を手元に置いて読む。

### 4.1 LLM アプリを作りたい開発者

1. **MLX-LM**: 手元で LLM を動かし、OpenAI 互換のサーバーを立てる（以降の練習台になる）
2. **Pydantic AI** か **Vercel AI SDK**: Python なら前者、TypeScript / Next.js なら後者で、型付きの出力とツール呼び出しを書く
3. **LangGraph**（または **Mastra**）: 状態・分岐・人の承認・途中からの再開が要る業務フローを組む
4. **Claude Agent SDK** / **OpenAI Agents SDK**: ファイル操作やコマンド実行まで任せるエージェント、複数のエージェントの引き継ぎを作る

到達点: 社内 FAQ に答え、必要なら人に承認を求めるエージェントを、ローカルの LLM で動かせる（手順 4 の Claude Agent SDK だけは Anthropic API を使う）。

### 4.2 ML を基礎から学びたい人

1. **[PyTorch](pytorch.md)**: テンソル・dtype・デバイス・学習ループ・保存・メモリの見積もり
2. **Transformers**: 学習済みモデルを読み込み、推論と埋め込み検索をする
3. **TRL + PEFT**: 自前のデータで LoRA による追加学習をする
4. **vLLM**: 学習したモデルを、本番向けの推論サーバーで配信する

枝分かれ: 別の書き方を知るなら [JAX](jax.md) と [Keras 3](keras.md)、既存の TensorFlow 資産に出会ったら [TensorFlow](tensorflow.md)。

到達点: 公開モデルを選び、自前のデータで調整し、API として配信するまでの流れを説明できる。

### 4.3 推論基盤を作り・運用したい人

1. **MLX-LM**: 量子化・メモリ・速度の感覚を、手元で掴む
2. **vLLM**: PagedAttention・continuous batching・OpenAI 互換サーバー・本番構成
3. **SGLang**: 共通の前置きのキャッシュ（RadixAttention）と構造化出力。vLLM との使い分け

到達点: 用途と予算から推論サーバーを選び、構成の要点を説明できる。

---

## 5. どれを選ぶか

### 5.1 やりたいことから選ぶ

| やりたいこと | 第一候補 | 次点 | 理由 |
|---|---|---|---|
| そもそも自前で動かすべきか | API を使う | 自前で動かす | 費用・データの扱い・運用の手間で決める。[LLM API 料金・スペック比較](../llm-api-pricing-comparison.md) を先に読む |
| 新しく深層学習のコードを書く | [PyTorch](pytorch.md) | [Keras 3](keras.md) | LLM 周辺の主要 OSS が PyTorch を前提にしている |
| TPU で学習する・Google 系の研究コードを読む | [JAX](jax.md) | — | 関数変換と TPU が JAX の強み |
| バックエンドの選択を後に回したい | [Keras 3](keras.md) | — | 同じコードを JAX / PyTorch / TensorFlow で動かせる |
| 既存の TensorFlow 資産を保守する | [TensorFlow](tensorflow.md) | Keras 3 へ移行 | 新規の生成 AI 開発には Google 自身が別の選択肢を勧めている |
| 公開モデルを試す・埋め込みで検索する | Transformers | — | モデルの読み込み方が統一されている |
| 自前のデータで追加学習する | TRL + PEFT | MLX-LM（Mac） | まずはプロンプトや RAG で足りないかを確かめてから |
| Mac で LLM を動かす | MLX-LM | vLLM-Metal | Apple Silicon 向けに作られている |
| 本番で多数の利用者に配信する | vLLM | SGLang | 多数のリクエストを同時に捌く仕組み（PagedAttention・continuous batching）を中心に作られている |
| 共通の前置きが長い処理・構造化出力を大量に回す | SGLang | vLLM | 前置きのキャッシュと制約付き生成が強み |
| 状態・分岐・人の承認・再開がある業務フロー | LangGraph | Mastra | グラフとチェックポイントで明示的に書ける |
| 型付きの出力と単体テストを重視する（Python） | Pydantic AI | — | LLM を使わずにテストできる仕組みがある |
| 複数のエージェントの引き継ぎ・ガードレール | OpenAI Agents SDK | LangGraph | handoff とガードレールが中心の設計 |
| ファイル操作やコマンド実行まで任せる | Claude Agent SDK | — | Claude Code と同じ道具一式を使える |
| Next.js の画面で LLM の応答を流す | Vercel AI SDK | Mastra | UI 用のフックとストリーミングが揃っている |
| TS でワークフロー・メモリ・評価まで一式 | Mastra | LangGraph.js | 部品が一通り揃っている |

### 5.2 新しく採用しないもの

| 名前 | 状態 | 代わり | 根拠 |
|---|---|---|---|
| Hugging Face TGI | メンテナンスモード。リポジトリはアーカイブ済み（最終 push は 2026-03-21） | vLLM / SGLang（Mac なら MLX-LM / llama.cpp） | README の告知（2026-11-08 確認） |
| AutoGen | README で「アーカイブ済み・保守終了」と告知（GitHub のアーカイブ設定はされておらず、最終 push は 2026-10-28）。Microsoft は本番での利用を勧めていない | Microsoft Agent Framework | README の告知（2026-11-08 確認） |
| LlamaIndex.TS | 非推奨。保守終了 | — | README の告知（2026-11-08 確認） |
| TensorFlow.js | 終了の告知は無い。最終 push は 2026-06-23 で、活動は少ない | Transformers.js などを比べて選ぶ | GitHub API（2026-11-08 取得） |

> **ポイント**: TensorFlow 本体は「新しく採用しないもの」ではない。保守とセキュリティ対応は続き、本番の安定性も提供すると Google は述べている。
> ただし、新しい生成 AI の開発の第一候補ではない。

---

## 6. 用語集

各ドキュメントは、一般的な用語の説明をここに任せている。「初出」は、その用語を詳しく扱うドキュメントである。

### 6.1 基礎・学習

| 用語 | 一言で | 初出 |
|---|---|---|
| テンソル | 多次元の配列。数値計算とニューラルネットの基本単位 | [PyTorch](pytorch.md) |
| dtype（fp32 / bf16 / fp16） | 1 要素の数値の形式。fp32 は 4 バイト、bf16 と fp16 は 2 バイト | [PyTorch](pytorch.md) |
| デバイス（CPU / CUDA / MPS） | 計算する場所。CUDA は NVIDIA GPU、MPS は Apple Silicon の GPU | [PyTorch](pytorch.md) |
| ユニファイドメモリ | Apple Silicon で CPU と GPU が同じメモリを共有する仕組み。大きなモデルを載せやすい | MLX-LM |
| 勾配・自動微分 | 誤差を減らす方向。フレームワークが計算過程から自動で求める | [PyTorch](pytorch.md) |
| バッチ・エポック | 一度に処理するデータのまとまりと、全データを 1 周すること | [PyTorch](pytorch.md) |
| 損失（loss）・optimizer | 予測の外れ具合と、それを減らすようにパラメータを更新する規則 | [PyTorch](pytorch.md) |
| JIT コンパイル | 実行時に計算をまとめて最適化すること（`torch.compile`・`jax.jit`） | [JAX](jax.md) |
| バックエンド | 高水準 API の下で実際に計算するフレームワーク | [Keras 3](keras.md) |

### 6.2 モデル・ファインチューニング

| 用語 | 一言で | 初出 |
|---|---|---|
| 重み・チェックポイント | 学習で得たパラメータの値と、それを保存したファイル | [PyTorch](pytorch.md) |
| safetensors | 重みを保存する安全なファイル形式。読み込み時にコードを実行しない | Transformers |
| Hugging Face Hub・モデルカード | モデルの公開場所と、その説明書（用途・ライセンス・制約） | Transformers |
| トークン・トークナイザ | LLM が扱う文字列の単位と、文章をそれに分割する仕組み | Transformers |
| チャットテンプレート | 会話をモデルごとの決まった書式に変換する規則 | Transformers |
| SFT / DPO / GRPO | 手本を真似る学習 / 好ましい答えを選ばせる学習 / 報酬で強化する学習 | TRL + PEFT |
| LoRA・アダプタ | 元の重みを固定し、小さな追加の重み（アダプタ）だけを学習する方法 | TRL + PEFT |
| 量子化（4bit / 8bit） | 重みの精度を下げてメモリを減らすこと。速度と品質の兼ね合いがある | MLX-LM |
| パラメータ数とメモリ | 重みのメモリは「パラメータ数 × 1 要素のバイト数」で見積もれる | [PyTorch](pytorch.md) |

### 6.3 推論・サービング

| 用語 | 一言で | 初出 |
|---|---|---|
| prefill / decode | 入力をまとめて読む段階と、1 トークンずつ出力する段階 | vLLM |
| KV キャッシュ | それまでの文脈の中間結果。会話が長いほどメモリを使う | vLLM |
| PagedAttention | KV キャッシュを小さなブロックに分けて無駄なく管理する vLLM の仕組み | vLLM |
| prefix キャッシュ・RadixAttention | 共通の前置きの計算結果を使い回す仕組み | SGLang |
| continuous batching | 処理中のリクエストに新しいリクエストを随時加えて、GPU を遊ばせない仕組み | vLLM |
| TTFT / スループット | 最初のトークンが出るまでの時間と、単位時間あたりの処理量 | vLLM |
| OpenAI 互換 API | OpenAI の API と同じ形の HTTP API。多くの道具がこの形で接続できる | MLX-LM |
| 構造化出力・制約付き生成 | JSON Schema などに必ず従う出力を生成させること | SGLang |
| ストリーミング（SSE） | 生成したトークンを、終わるのを待たずに少しずつ返すこと | Vercel AI SDK |

### 6.4 アプリ・エージェント

| 用語 | 一言で | 初出 |
|---|---|---|
| エージェント・エージェントループ | LLM が考え、ツールを呼び、結果を見て次を決める繰り返し | LangGraph |
| ワークフローとエージェント | 手順を人が決めるものと、LLM が決めるもの | LangGraph |
| ツール呼び出し（function calling） | LLM が「この関数をこの引数で呼ぶ」と返し、アプリが実行する仕組み | Pydantic AI |
| RAG・埋め込み・ベクトル検索 | 文書を検索して答えの材料にする方法と、そのための数値化・類似検索 | Transformers |
| チェックポインタ・セッション | 会話や処理の途中の状態を保存し、後から再開する仕組み | LangGraph |
| handoff・マルチエージェント | 役割の違うエージェントに処理を引き継ぐこと | OpenAI Agents SDK |
| ガードレール | 入力や出力を検査し、問題があれば止める仕組み | OpenAI Agents SDK |
| HITL（人の承認） | 処理の途中で人の確認を挟むこと | LangGraph |
| MCP | ツールやデータを LLM に提供するための共通の規格。[MCP の設定ガイド](../mcp-setup.md) も参照 | Claude Agent SDK |
| トレーシング・評価（evals） | エージェントの動きの記録と、出力の品質の測定 | Mastra |

---

## 7. ローカル検証環境（シリーズ共通）

### 7.1 ハードウェアと方針

| 項目 | 内容 |
|---|---|
| マシン | Apple M2 Max / メモリ 96GB / macOS 27.2 / NVIDIA GPU なし |
| Python | 3.12（uv で管理する版に固定）。PyTorch 2.15 は 3.11 以上、JAX 0.12 は 3.12 以上を要求し、vLLM 0.33 は 3.15 未満を要求するため |
| パッケージ | 各ドキュメントの §4 に、検証に使った版を固定して書く |
| Node.js | 26.13（TypeScript のドキュメントで使う。パッケージ管理は pnpm 12.11） |
| 作業場所 | ドキュメントごとに別の uv / pnpm プロジェクトを作り、互いの依存がぶつからないようにする |

Python のプロジェクトは、次の形で作った。

```bash
uv init --bare --python 3.12 <name> && cd <name>
uv python pin 3.12          # これが無いと、より新しい Python が選ばれることがある（実測）
uv add "<package>==<version>"
```

### 7.2 使うモデル

ライセンスが Apache-2.0 か MIT で、利用規約への同意が要らないものを選んだ。
**最新のモデルの推薦ではなく、すべての層の道具で同じモデルを動かして比べられることを優先した選定**である（Hub には Qwen3.5 以降の世代もある）。

| モデル | 用途 | ライセンス |
|---|---|---|
| `Qwen/Qwen3-0.6B` | Transformers・TRL + PEFT の推論と学習 | Apache-2.0 |
| `intfloat/multilingual-e5-small` | 日本語を含む文章の埋め込み | MIT |
| `mlx-community/Qwen3-0.6B-4bit` | MLX-LM・vLLM-Metal・SGLang の基本動作 | Apache-2.0 |
| `mlx-community/Qwen3-4B-Instruct-2507-4bit` | エージェント層の共通の LLM（考えた過程を出力しない版で、ツール呼び出しの解析を壊しにくい） | Apache-2.0 |

### 7.3 コード例の状態ラベル

| ラベル | 意味 |
|---|---|
| （検証済み） | 手元で実行し、載せた「実行結果」はそのときの出力をそのまま写したもの |
| （公式 docs 準拠・未実行: 理由） | NVIDIA GPU が必要など、手元で実行できないもの。公式 docs に沿って書いた |
| （抜粋・単体では動かない） | 説明のための部分的なコード |

> **注意**: 速度などの数値は、この Mac での 1 回の計測による参考値である。LLM の出力は、同じ設定でも実行ごとに変わり得る。

### 7.4 通し課題のデータ（架空の社内 FAQ）

`faq.jsonl` として、1 行に 1 件ずつ置く。会社・制度はすべて架空である。

```text
{"id": "faq-01", "category": "経費", "question": "経費精算の締め日はいつですか？", "answer": "毎月 25 日締めです。25 日までに経費システムで申請すると、翌月 10 日に給与口座へ振り込まれます。"}
{"id": "faq-02", "category": "経費", "question": "領収書をなくした場合はどうすればよいですか？", "answer": "経費システムの「領収書紛失届」を提出してください。上長の承認があれば、支払いの事実が分かる明細（カード明細など）で代用できます。"}
{"id": "faq-03", "category": "勤怠", "question": "有給休暇はどうやって申請しますか？", "answer": "勤怠システムから取得日の 3 営業日前までに申請してください。当日の急な取得は、チャットで上長に連絡したうえで事後申請します。"}
{"id": "faq-04", "category": "勤怠", "question": "在宅勤務は週に何日までできますか？", "answer": "原則として週 3 日までです。チームの出社日（毎週水曜）は出社してください。"}
{"id": "faq-05", "category": "IT", "question": "社内 VPN につながりません。", "answer": "VPN クライアントを再起動し、それでもつながらなければ多要素認証アプリの時刻同期を確認してください。解決しない場合はヘルプデスクのチケットを起票してください。"}
{"id": "faq-06", "category": "IT", "question": "パスワードを忘れました。", "answer": "ログイン画面の「パスワードを忘れた場合」から再設定できます。多要素認証の端末を紛失した場合はヘルプデスクへ連絡してください。"}
{"id": "faq-07", "category": "IT", "question": "新しい PC のセットアップは誰がしますか？", "answer": "情報システム部がキッティング済みの PC を入社初日に渡します。初回ログイン後、案内メールの手順で開発ツールを入れてください。"}
{"id": "faq-08", "category": "総務", "question": "会議室はどうやって予約しますか？", "answer": "社内カレンダーで会議室をゲストとして招待すると予約できます。1 回の予約は 2 時間までです。"}
{"id": "faq-09", "category": "総務", "question": "名刺を発注したいです。", "answer": "総務ポータルの「名刺発注」フォームから申し込んでください。発注から 5 営業日で届きます。"}
{"id": "faq-10", "category": "出張", "question": "出張の申請はいつまでに出せばよいですか？", "answer": "出発の 5 営業日前までに出張申請を出してください。宿泊費の上限は 1 泊 12,000 円です。"}
{"id": "faq-11", "category": "セキュリティ", "question": "顧客の個人情報を生成 AI に入力してもよいですか？", "answer": "入力してはいけません。社外の生成 AI サービスに顧客の個人情報や機密情報を入力することは禁止です。社内で承認されたツールのみを使ってください。"}
{"id": "faq-12", "category": "セキュリティ", "question": "不審なメールを受け取りました。", "answer": "リンクや添付ファイルを開かず、メールソフトの「フィッシング報告」ボタンで情報セキュリティ担当へ報告してください。"}
```

---

## 8. このシリーズで扱わないもの

| 名前 | 扱わない理由 |
|---|---|
| llama.cpp / Ollama / LM Studio | Python / TypeScript のフレームワークではないため。推論の層のドキュメントで比較対象として触れる |
| TensorRT-LLM | NVIDIA GPU 専用で、手元で検証できないため |
| Unsloth / Axolotl / LLaMA-Factory | 追加学習の道具。TRL + PEFT のドキュメントで比較対象として触れる |
| CrewAI / smolagents / DSPy / LlamaIndex / Google ADK / Microsoft Agent Framework | 活発だが、対象を絞るため今回は選ばなかった |
| ONNX Runtime | モデルの配信形式の 1 つ。TensorFlow のドキュメントで比較対象として触れる |

---

## 出典

| 情報源 | URL |
|---|---|
| What's new in TensorFlow 2.21 — Google Developers Blog | https://developers.googleblog.com/whats-new-in-tensorflow-221/ （2026-11-08 確認。2026-03-06 公開） |
| Transformers v5 Migration guide | https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md （2026-11-08 確認、Context7 `/huggingface/transformers` 経由） |
| huggingface/text-generation-inference | https://github.com/huggingface/text-generation-inference （2026-11-08 確認。README のメンテナンスモードの告知、アーカイブ済み） |
| microsoft/autogen | https://github.com/microsoft/autogen （2026-11-08 確認。README のアーカイブの告知と移行ガイドへのリンク） |
| run-llama/LlamaIndexTS | https://github.com/run-llama/LlamaIndexTS （2026-11-08 確認。README の非推奨の告知） |
| vLLM Quickstart / Installation | https://docs.vllm.ai/en/stable/getting_started/quickstart/ （2026-11-08 確認、Context7 `/websites/vllm_ai_en_stable` 経由） |
| SGLang — Apple Metal | https://docs.sglang.io/docs/hardware-platforms/apple_metal （2026-11-08 確認） |
| 各リポジトリの★・最新版 | GitHub API（`gh api repos/<owner>/<repo>`）、PyPI の JSON API、`npm view`（2026-11-08 取得） |

### 確認できなかった事項

- **★と活動量の意味**。★は人気の目安であり、品質や将来性を保証しない。コミット数には自動化されたコミットが含まれるリポジトリもあり、本ドキュメントでは選定の根拠にしていない
- **TensorFlow.js の今後**。終了の告知は見つからなかった。最終 push の日付という観測できる事実だけを載せた

- 関連: [ハーネス設計ガイド](../harness.md) / [SubAgents ガイド](../sub-agents.md) / [LLM API 料金・スペック比較](../llm-api-pricing-comparison.md) / [モデル比較とプラン制限](../model-comparison.md) / [使用ツールスタック](../tool-stack.md)
