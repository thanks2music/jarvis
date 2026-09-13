# LLM API 料金・スペック比較(Anthropic / OpenAI / Google)

> 出典:
> - [Pricing (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/pricing) — Claude 全モデルの単価 / キャッシュ倍率 / Batch / tool use トークン `[Web]`
> - [Models overview (platform.claude.com)](https://platform.claude.com/docs/en/models/overview) — Claude の context / 最大出力 / 用途 `[C7]`
> - [Migration guide (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/migration-guide) — Sonnet 5 / Opus 5 の価格差と tokenizer 世代 `[C7]`
> - [Vision (platform.claude.com)](https://platform.claude.com/docs/en/build-with-claude/vision) — 28x28 パッチによる画像トークン換算 `[C7]`
> - [Pricing (developers.openai.com)](https://developers.openai.com/api/docs/pricing) — OpenAI の標準 / Batch 単価 `[Web]`
> - [GPT-5.6 Sol (developers.openai.com)](https://developers.openai.com/api/docs/models/gpt-5.6-sol) — context 1,050,000 / 出力 128,000 / cutoff 2026-02-16 `[Web]`
> - [GPT-5.6 Terra (developers.openai.com)](https://developers.openai.com/api/docs/models/gpt-5.6-terra) — 単価と 272k 超の割増 `[C7]`
> - [GPT-5 mini (developers.openai.com)](https://developers.openai.com/api/docs/models/gpt-5-mini) — context 400,000 / 出力 128,000 / cutoff 2024-05-31 `[C7]`
> - [GPT-5 nano (developers.openai.com)](https://developers.openai.com/api/docs/models/gpt-5-nano) — context 400,000 / 出力 128,000 / cutoff 2024-05-31 / text + image 入力 `[Web]`
> - [Images and vision (developers.openai.com)](https://developers.openai.com/api/docs/guides/images-vision) — 32x32 パッチによる画像トークン換算 `[C7]`
> - [Gemini API pricing (ai.google.dev)](https://ai.google.dev/gemini-api/docs/pricing) — Gemini の Paid tier 単価と階層 `[Web]`
> - [Gemini 3 (ai.google.dev)](https://ai.google.dev/gemini-api/docs/gemini-3) — context 1M / 出力 64k / knowledge cutoff `[C7]`
> - [Image understanding (ai.google.dev)](https://ai.google.dev/gemini-api/docs/vision) — 258 トークン / タイルの換算 `[C7]`
>
> 最終更新: 2026-09-03（Fable 5.1 / Mythos 5.1 を反映）

Anthropic / OpenAI / Google の **API 料金体系**と、各モデルの**要点スペック**を 1 箇所に集約する。Node.js を含む自作アプリケーションから API を直接叩く場合のモデル選定とコスト見積もりを目的とした資料であり、サブスクプラン(Claude Pro / Max)側の話題は扱わない。

> 出典欄の `[C7]` は Context7 MCP 経由で取得した記述、`[Web]` は公式料金ページを直接取得した記述を指す。Context7 は集約された料金表と一部の階層別料金を要約してしまい数値が落ちるため、その箇所のみ公式ページで補完している。**本ドキュメントは公式が数値で明示している事実のみを扱い、二次情報(ブログ・料金比較サイト)は出典に採らない。**

> ⚠️ **料金は改定される。** 本ドキュメントは **2026-08-16 時点**の公表価格に基づく。特に **Gemini 3.6 Flash は 2027-01-01 に入出力とも 2 倍**になることが公式に予告済みである(§3)。

---

## 1. TL;DR

- **同一ワークロードでも単価は 100 倍以上開く。** 入力:出力 = 3:1 のブレンド単価で見ると、最安の `gpt-5-nano`($0.1375 / MTok 相当)と最高の Claude Fable 5($20 / MTok 相当)で **約 145 倍**の差がある(§3)。
- **Claude Sonnet 5 の $2 / $10 は恒久価格**。launch 時に「2026-08-31 までの introductory」と案内されていた価格がそのまま標準価格になり、**2026-09-01 に予定されていた $3 / $15 への引き上げは中止された**(§3)。
- **3 社とも Batch API はちょうど 50% 引き**。非同期で構わない処理を同期 API で回すのは、それだけで倍額を払っていることになる(§4)。
- **プロンプトキャッシュの効きは 3 社で桁が違わない**。Anthropic はキャッシュ読取が基本入力の **0.1x**、OpenAI も cached input が概ね **0.1x**。ただし Anthropic は**書き込みに 1.25x(5m) / 2x(1h) の前払い**が要る(§4)。
- **長コンテキストの割増は OpenAI と Google にあり、Anthropic には無い。** OpenAI は **272k 入力超で入力 2x・出力 1.5x**、Gemini 3.1 Pro は **200k 超で単価が上がる**。Claude は 1M まで一律(§4)。
- **Claude 4.7 以降は tokenizer が変わり、同一テキストのトークン数が約 30% 増える。** 単価が据え置きでも実コストは上がるため、旧世代 Claude からの移行時は単価比較だけでは誤る(§4)。
- **画像 1 枚のトークン数は 3 社で大きくは変わらない。** 1024x1024 の画像は Claude 1,369 / OpenAI 1,024 / Gemini 1,032 トークンで、差が出るのは換算式ではなく**モデル単価**の方である(§5)。

---

## 2. 現行モデル一覧(2026-08-16 時点)

### 2.1 Anthropic

| 項目 | Claude Fable 5.1 / Mythos 5.1 | Claude Opus 5 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **モデル ID** | `claude-fable-5-1` / Mythos 5.1（ID 未公開）※11 | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5` |
| **context** | 1M tokens | 1M tokens | 1M tokens | 200k tokens |
| **最大出力** | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **tokenizer 世代** | 新(Opus 4.7 世代) | 新(Opus 4.7 世代) | 新(Sonnet 4.6 比 約 +30%)※10 | 旧 |
| **位置づけ** | 長時間稼働エージェント向け。adaptive thinking が always on | 複雑なエージェント的コーディング / 企業タスク | 速度と知性のバランス。汎用の主力 | 最速・最安 |

※1: Mythos 5 / Mythos 5.1 は [limited availability](https://anthropic.com/glasswing)(Project Glasswing)。API 仕様と料金は同世代の Fable と同一。
※11: **Fable 5.1（`claude-fable-5-1`）が現行**であり、`platform.claude.com` の Models overview では **Fable 5 は `Legacy models (still available)` へ移動**した（**2026-09-03 確認**）。**Mythos 5.1 の存在は pricing 脚注でのみ確認でき、モデル ID・仕様の専用ページは未公開**である（裏取り不可）。ClaudeCode 側の alias は v2.1.255 以降 `fable` → Fable 5.1。単価（$10 / $50）と context（1M）は Fable 5 から変わっていない。**knowledge cutoff は Jun 2026**（Fable 5 は Jan 2026）。
※12: **cache read の割引率が Fable 5.1 / Mythos 5.1 だけ優遇されている**。公式 pricing の脚注は「prompt cache reads cost 10% of base input price (**2.5% on Claude Fable 5.1 and Claude Mythos 5.1**)」。**Fable 5 は 0.1x のまま**で、cache write は据え置き。キャッシュヒット率が高い長時間エージェントでは実効コストが大きく変わる。
※2: Opus / Sonnet の一部バージョンは Message Batches API で beta ヘッダ指定時に最大 300k tokens の出力に対応する。

### 2.2 OpenAI

| 項目 | gpt-5.6-sol | gpt-5.6-terra | gpt-5-mini | gpt-5-nano |
|---|---|---|---|---|
| **エイリアス** | `gpt-5.6` が解決 | — | — | — |
| **context** | 1,050,000 tokens | 1,050,000 tokens | 400,000 tokens | 400,000 tokens |
| **最大入力** | 922,000 tokens | 922,000 tokens | 未確認 | 未確認 |
| **最大出力** | 128,000 tokens | 128,000 tokens | 128,000 tokens | 128,000 tokens |
| **knowledge cutoff** | 2026-02-16 | 2026-02-16 | 2024-05-31 | 2024-05-31 |
| **入出力** | text + image → text | text + image → text | text + image → text | text + image → text |
| **位置づけ** | GPT-5.6 系の frontier。複雑な専門業務向け | 知性とコストの均衡。旧 mini 相当のティア | 定義の明確なタスク向けの低レイテンシ・大量処理 | GPT-5 系で最速・最安。要約 / 分類向けで複雑な推論には不向き |

※3: 「未確認」は公式ページで数値を確認できなかった項目。**推測値は置かない**。
※4: `reasoning.effort` は明示指定しない限りモデル既定に従う。reasoning トークンは出力トークンとして課金される。

### 2.3 Google(概算)

| 項目 | Gemini 3.1 Pro | Gemini 3.6 Flash | Gemini 3.5 Flash |
|---|---|---|---|
| **提供状態** | Preview | Stable | Stable(legacy 扱い) |
| **context** | 1M tokens | 1M tokens | 1M tokens |
| **最大出力** | 64k tokens | 64k tokens | 65k tokens |
| **knowledge cutoff** | 2025-01 | 2025-01 | 未確認 |
| **無料枠** | **なし** | あり | あり |

※5: **上表の context / 最大出力 / cutoff は、公式 FAQ が「Gemini 3 models」として一括で示している値**(1M token input context / 最大 64k output / knowledge cutoff 2025 年 1 月)であり、マイナーバージョン単位では公開されていない。**個別ページで確認できたのは Gemini 3.5 Flash の 65k output と Gemini 3 Pro Preview の 1,048,576 / 65,536 のみ**。本節は**概算**として扱い、正確な値が要る場合は `client.models.get()` で実機から取得する。

---

## 3. 料金表

すべて **USD / MTok**(100 万トークンあたり)。円は **150 円/USD** の固定換算による参考値であり、実勢レートとは乖離する。

| モデル | 入力 | キャッシュ読取 | 出力 | Batch 入力 | Batch 出力 | ブレンド単価 ※6 | 最安比 |
|---|---|---|---|---|---|---|---|
| **Claude Fable 5 / Mythos 5** | $10 | $1 | $50 | $5 | $25 | $20 | 145.5x |
| **Claude Opus 5** | $5 | $0.50 | $25 | $2.50 | $12.50 | $10 | 72.7x |
| **Claude Sonnet 5** | $2 | $0.20 | $10 | $1 | $5 | $4 | 29.1x |
| **Claude Haiku 4.5** | $1 | $0.10 | $5 | $0.50 | $2.50 | $2 | 14.5x |
| **gpt-5.6-sol** | $5 | $0.50 | $30 | $2.50 | $15 | $11.25 | 81.8x |
| **gpt-5.6-terra** | $2 | $0.20 | $12 | $1 | $6 | $4.50 | 32.7x |
| **gpt-5-mini** | $0.25 | $0.025 | $2 | $0.125 | $1 | $0.6875 | 5.0x |
| **gpt-5-nano** | $0.05 | $0.005 | $0.40 | $0.025 | $0.20 | $0.1375 | 1.0x |
| **Gemini 3.1 Pro**(≤200k) | $2 | $0.20 | $12 | $1 | $6 | $4.50 | 32.7x |
| **Gemini 3.1 Pro**(>200k) | $4 | $0.40 | $18 | $2 | $9 | $7.50 | 54.5x |
| **Gemini 3.6 Flash**(〜2026-12-31) | $0.75 | $0.075 | $3.75 | $0.375 | $1.875 | $1.50 | 10.9x |
| **Gemini 3.6 Flash**(2027-01-01〜) | $1.50 | $0.15 | $7.50 | $0.75 | $3.75 | $3 | 21.8x |

※6: ブレンド単価は **入力:出力 = 3:1** を想定した加重平均 `(3 × 入力 + 1 × 出力) / 4`。実際の比率はワークロードによるため、あくまで横並び比較用の指標である。
※7: 「最安比」は `gpt-5-nano` のブレンド単価($0.1375)を 1.0 とした倍率。
※8: Batch 欄は 3 社とも標準単価のちょうど 50%。

> **Sonnet 5 の価格に関する注意**: 公式 Pricing ページは「The $2/$10 per million input/output token pricing for Claude Sonnet 5, announced at launch as introductory pricing through August 31, 2026, **is now the standard price**. The previously scheduled increase to $3/$15 per million input/output tokens on September 1, 2026 **will not occur**.」と明記している。$3 / $15 と記載した資料は 2026-08-10 以前の情報である。

### 3.1 Anthropic のキャッシュ書き込み単価

Anthropic はキャッシュ読取が安い代わりに、**書き込み時に前払いの割増**がある。

| モデル | 5m 書込 | 1h 書込 | 読取 |
|---|---|---|---|
| **Claude Fable 5.1 / Mythos 5.1** | $12.50 | $20 | **$0.25**（base input の **0.025x**）※12 |
| Claude Fable 5 / Mythos 5（legacy） | $12.50 | $20 | $1（0.1x） |
| Claude Opus 5 | $6.25 | $10 | $0.50 |
| Claude Sonnet 5 | $2.50 | $4 | $0.20 |
| Claude Haiku 4.5 | $1.25 | $2 | $0.10 |

---

## 4. 割引と課金の効き方

### 4.1 プロンプトキャッシュ

| 項目 | Anthropic | OpenAI | Google |
|---|---|---|---|
| **読取単価** | 基本入力の **0.1x** | cached input(概ね **0.1x**) | モデルにより $0.075〜$0.40 |
| **書込単価** | **1.25x**(5m) / **2x**(1h) | **1.25x** | — |
| **保存料** | なし | なし | **あり**(Gemini 3.1 Pro で $4.50 / 1M tok / hour) |
| **損益分岐** | 5m は**読取 1 回**、1h は**読取 2 回**で元が取れる | 明示なし | 保存時間しだい |

Anthropic の損益分岐は公式が明記している。5m 書込が 1.25x、読取が 0.1x なので、1 回読み取れば `1.25 + 0.1 = 1.35` < `1.0 + 1.0 = 2.0` となり回収できる。**キャッシュ倍率は Batch 割引やデータレジデンシー倍率と積算される。**

### 4.2 Batch API

3 社とも**入出力ともちょうど 50% 引き**。Anthropic は Batch とプロンプトキャッシュを**併用できる**と明記している。ただし Anthropic の fast mode は Batch と併用できない。

### 4.3 長コンテキストの割増

| プロバイダ | 割増 |
|---|---|
| **Anthropic** | **なし**。1M context まで一律(900k のリクエストも 9k と同レート) |
| **OpenAI** | **272,000 入力トークン超**で入力 **2x** / 出力 **1.5x** |
| **Google** | **Gemini 3.1 Pro は 200k 超**で入力 $2 → $4、出力 $12 → $18 |

長い文脈を常時投げるワークロードでは、この差が単価表以上に効く。

### 4.4 tokenizer 世代差(Anthropic のみ)

**Claude 4.7 以降のモデルと Mythos Preview は新しい tokenizer を使い、同一テキストが約 30% 多くトークン化される**(公式 Pricing ページ明記)。Sonnet 4.6 以前は旧 tokenizer である。

| 区分 | 該当モデル | 公式が示している増加率 |
|---|---|---|
| 新 tokenizer(Opus 4.7 世代) | Fable 5 / Mythos 5 / Opus 5 / Opus 4.8〜4.7 | 1x〜1.35x ※9 |
| 新 tokenizer(別基準で記載) | **Sonnet 5** | **Sonnet 4.6 比 約 +30%** ※10 |
| 旧 tokenizer | Sonnet 4.6 / Sonnet 4.5 / **Haiku 4.5** | — |

※9: Migration guide が Opus 4.7 世代について示している比率。
※10: **Sonnet 5 を Opus 4.7 世代と同一 tokenizer と断定してはならない。**公式 Pricing ページは「Claude 4.7 and later models ... use a newer tokenizer」と一括りに記述する一方、[What's new in Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5) は「approximately 30% more tokens than on **Claude Sonnet 4.6**」と **Sonnet 4.6 を基準**に記載しており、Opus 4.7 世代と同一 tokenizer かどうかは公式に明示がない。この保留の経緯は [docs/model-comparison.md](model-comparison.md) §3.2 を参照。

つまり **Sonnet 4.5($3 / $15、旧 tokenizer)から Sonnet 5($2 / $10、新 tokenizer)への移行は、単価だけ見ると 33% 減だが、トークン数が約 30% 増えるため実コストの低下はそれより小さい**。同様に Haiku 4.5 から Sonnet 5 へ移すと、単価 2 倍・トークン約 1.3 倍で実質 2.6 倍前後になる。

> ⚠️ **増加率を他社 tokenizer からの換算に流用しない。** 「約 30% 増」はいずれも **Anthropic の旧世代モデルとの比較**であり、OpenAI / Google の tokenizer で数えたトークン数に掛けてよい係数ではない。他社からの移行コストを見積もる場合は [token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting) で実測する。

### 4.5 その他の課金要素(Anthropic)

| 要素 | 課金 |
|---|---|
| データレジデンシー | `inference_geo: "us"` で全カテゴリ **1.1x** |
| fast mode(Opus 5 / 4.8) | $10 / $50。Batch とは併用不可 |
| tool use | `tools` 定義ぶんの入力トークンが加算(Opus 5 は `auto`/`none` で 286 tokens、`any`/`tool` で 406 tokens) |
| web search | **$10 / 1,000 検索** + 標準トークン課金 |
| web fetch | 追加課金なし(取得内容のトークンのみ) |
| code execution | web search / web fetch と併用時は無料。単体利用は月 1,550 時間無料、超過 $0.05 / 時間 |

Google の Grounding with Google Search は Paid tier で **1,500 RPD まで無料**、超過は **$35 / 1,000 プロンプト**。

---

## 5. Vision / 画像解析の課金

### 5.1 3 社のトークン換算式

| プロバイダ | 換算式 | 備考 |
|---|---|---|
| **Anthropic** | `ceil(w / 28) × ceil(h / 28)` | 28x28px パッチ 1 個 = 1 トークン。標準解像度層は長辺 1,568px / 1,568 トークンの上限を超えると自動縮小 |
| **OpenAI** | `ceil(w / 32) × ceil(h / 32)` | 32x32px パッチ。パッチ数の上限を超える画像は縮小される。GPT-4o / o 系は 512px タイル方式で `detail` 依存 |
| **Google** | 両辺 384px 以下は **258 トークン固定**。超える場合は 768x768 タイルに分割し**タイルごと 258 トークン** | 動画は 263 トークン/秒、音声は 32 トークン/秒 |

Anthropic は**トークン上限が先に効いて縮小が起きる**ケースがある点に注意が要る。長辺が上限内でも、総パッチ数が 1,568 を超えれば縮小される。

### 5.2 同一画像でのトークン数と単価

1024x1024 の画像 1 枚を渡した場合:

| プロバイダ | 計算 | トークン |
|---|---|---|
| Anthropic | `ceil(1024/28)² = 37² ` | **1,369** |
| OpenAI | `ceil(1024/32)² = 32²` | **1,024** |
| Google | `ceil(1024/768)² = 2² タイル × 258` | **1,032** |

換算式が違ってもトークン数は同程度に収まる。したがって**画像解析のコスト差はほぼモデル単価の差**に還元される。

| モデル | 画像 1 枚あたり |
|---|---|
| gpt-5-mini | $0.000256 |
| Gemini 3.6 Flash(〜2026-12-31) | $0.000774 |
| Claude Haiku 4.5 | $0.00137 |
| gpt-5.6-terra | $0.00205 |
| Claude Sonnet 5 | $0.00274 |

※9: 画像トークンのみの単価。実際には指示プロンプトと出力のトークンが上乗せされる。

### 5.3 画像入力を安くする順序

1. **送信前に縮小する。** トークン数はパッチ数に比例するので、長辺を半分にすればトークンは約 1/4 になる。上限超過による自動縮小に任せると、上限ぎりぎりまで課金される。
2. **枚数を絞る。** 1 リクエストに何枚渡しても、課金は枚数ぶん積み上がる。
3. **プロンプトをキャッシュする。** 画像は毎回変わってもプロンプトは変わらないことが多い。**静的なテキストを画像より前に置く**とプレフィックスとしてキャッシュに乗る。
4. **安いモデルで足りるか確かめる。** OCR や単純な分類ならティアを 1 段下げても品質が落ちないことがある。

---

## 6. Node.js からの利用

### 6.1 公式 SDK

| プロバイダ | パッケージ | 備考 |
|---|---|---|
| Anthropic | `@anthropic-ai/sdk` | 画像は base64 のほか **URL 直渡し**に対応 |
| OpenAI | `openai` | Responses API / Chat Completions API |
| Google | `@google/genai` | 新 SDK。旧 `@google/generative-ai` からの移行対象 |

### 6.2 課金に効くパラメータ

| パラメータ | 効き方 |
|---|---|
| `max_tokens` / `max_output_tokens` | 上限であって課金額ではない。**実際に生成された分だけ課金**される |
| reasoning / thinking | 思考トークンは**出力トークンとして課金**される。effort を上げるほど出力が増える |
| `cache_control`(Anthropic) | 静的な接頭辞に付ける。**1,024 トークン未満は無言でキャッシュされない** |
| `service_tier`(OpenAI) | `flex` は低速・低価格、`priority` / `fast` は高速・高価格 |
| `detail`(OpenAI Vision) | `low` は固定の低トークン、`high` はタイル分割で増える |

### 6.3 使用量の取得

3 社ともレスポンスに使用量が入るので、**推定値ではなく実測値でコストを集計できる**。

| プロバイダ | フィールド |
|---|---|
| Anthropic | `usage.input_tokens` / `output_tokens` / `cache_creation_input_tokens` / `cache_read_input_tokens` |
| OpenAI | `usage.input_tokens` / `output_tokens` / `input_tokens_details.cached_tokens` / `output_tokens_details.reasoning_tokens` |
| Google | `usageMetadata.promptTokenCount` / `candidatesTokenCount` / `totalTokenCount` |

**キャッシュ関連のフィールドを合算に含め忘れると実コストを過小に見積もる。** Anthropic はキャッシュ書き込み・読み取りが別フィールドなので特に注意が要る。

事前見積もりには OpenAI の `POST /v1/responses/input_tokens`、Google の `client.models.countTokens` が使える。

---

## 7. 既存ドキュメントとの関係

| ドキュメント | 扱う範囲 |
|---|---|
| **本ドキュメント** | **Anthropic / OpenAI / Google の API 料金と要点スペックの横断比較。** API を直接叩く場合のモデル選定とコスト見積もりが対象 |
| [docs/model-comparison.md](model-comparison.md) | **Claude 専用**。サブスクプラン(Pro / Max / Team)の weekly limit がどう減るか、Claude Code でのモデル使い分けが主題 |
| [docs/best-practices.md](best-practices.md) | ClaudeCode のベストプラクティス。モデル世代ごとの差分を追記形式で保持 |

Claude 単体の話題(プラン制限・Claude Code のエイリアス解決・fast mode の挙動)は `model-comparison.md` を参照する。**3 社横断の API 料金は本ドキュメントを正とする。**

---

## 出典

- [Pricing — platform.claude.com](https://platform.claude.com/docs/en/about-claude/pricing)(**2026-09-03 再確認**)
- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/models/overview)(**2026-09-03 再確認**)
- [Migration guide — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/migration-guide)(2026-08-16 確認)
- [Vision — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/vision)(2026-08-16 確認)
- [Prompt caching — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)(2026-08-16 確認)
- [Pricing — developers.openai.com](https://developers.openai.com/api/docs/pricing)(2026-08-16 確認)
- [GPT-5.6 Sol — developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-sol)(2026-08-16 確認)
- [GPT-5.6 Terra — developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-terra)(2026-08-16 確認)
- [GPT-5 mini — developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5-mini)(2026-08-16 確認)
- [GPT-5 nano — developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5-nano)(2026-08-16 確認)
- [Images and vision — developers.openai.com](https://developers.openai.com/api/docs/guides/images-vision)(2026-08-16 確認)
- [Gemini API pricing — ai.google.dev](https://ai.google.dev/gemini-api/docs/pricing)(2026-08-16 確認)
- [Gemini 3 — ai.google.dev](https://ai.google.dev/gemini-api/docs/gemini-3)(2026-08-16 確認)
- [Image understanding — ai.google.dev](https://ai.google.dev/gemini-api/docs/vision)(2026-08-16 確認)
- 関連: `docs/model-comparison.md` / `docs/best-practices.md`
