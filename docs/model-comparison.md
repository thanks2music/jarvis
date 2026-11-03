# Claude モデル別トークン消費とプラン制限

> 出典:
> - [Models overview (platform.claude.com)](https://platform.claude.com/docs/en/models/overview) — 現行モデルの ID / pricing / context / thinking / tokenizer
> - [Claude Opus 5 (platform.claude.com)](https://platform.claude.com/docs/en/models/opus-5/overview) — Opus 5 の仕様カード(**2026-10-11 時点で Legacy**。旧 What's new in Claude Opus 5 ページから移転)
> - [Thinking (platform.claude.com)](https://platform.claude.com/docs/en/build-with-claude/thinking) — モデル別の thinking 既定と `thinking.type` の受け付け可否(Opus 5 の thinking 破壊的変更の現行出典)
> - [Introducing Claude Opus 5 (anthropic.com)](https://www.anthropic.com/news/claude-opus-5) — Opus 5 リリースアナウンス(2026-07-24)
> - [Claude Fable 5 (platform.claude.com)](https://platform.claude.com/docs/en/models/fable-5/overview) — Fable 5 の仕様カード(Legacy。旧 Introducing Claude Fable 5 and Claude Mythos 5 ページから移転)
> - [Refusals and fallback (platform.claude.com)](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) — classifier refusal の応答形状・fallback・**refusal の課金ルール**(2026-09-24 改定)
> - [Claude Fable 5 promotional access (support.claude.com)](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access) — サブスクプラン上でのプロモーショナルアクセス(**2026-07-01 〜 07-19 23:59:59 PT で終了済み**)
> - [Model configuration (code.claude.com)](https://code.claude.com/docs/en/model-config) — Claude Code のエイリアス解決 / effort 既定と解決順 / classifier fallback
> - [Effort (platform.claude.com)](https://platform.claude.com/docs/en/build-with-claude/effort) — モデル別の effort 推奨と API 既定値
> - [Migration guides (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/migration-guide) — **2026-10-11 時点でモデル別ガイドへの索引ページ**(旧来の Opus 5 tokenizer の記述は下記 Opus 5.5 migration guide に移った)
> - [Claude Opus 5.5 migration guide (platform.claude.com)](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide) — Opus 5.5 の破壊的変更・tokenizer 世代(Opus 4.7 系、1x〜1.35x)
> - [Claude Sonnet 5.5 migration guide (platform.claude.com)](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide) — Sonnet 5.5 の破壊的変更・**Sonnet 4.6 比 約 +30% の tokenizer**
> - [Claude Haiku 5.5 migration guide (platform.claude.com)](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide) — Haiku 5.5 の thinking 設定・tokenizer
> - [Introducing Claude Opus 5.5 (anthropic.com)](https://www.anthropic.com/claude-opus-5-5) — Opus 5.5 リリースアナウンス(2026-09-22)
> - [Introducing Claude Sonnet 5.5 (anthropic.com)](https://www.anthropic.com/claude-sonnet-5-5) — Sonnet 5.5 リリースアナウンス(2026-09-28)
> - [Introducing Claude Haiku 5.5 (anthropic.com)](https://www.anthropic.com/claude-haiku-5-5) — Haiku 5.5 リリースアナウンス・Sonnet 5.5 cache read 値下げ・Max / Team の月次 API credits(2026-10-07。2026-11-01 確認時点では Ultra の $200 も記載)
> - [API credits for Max, Ultra, and Team plans (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers) — Max / Ultra / Team に付く月次 API credits(2026-10-11 時点のページ名は「API credits for Max and Team plans」)
> - [Claude pricing (claude.com)](https://claude.com/pricing) — 個人プランの現行構成(Free / Pro / Max / Ultra)
> - [What is the Ultra plan? (support.claude.com)](https://support.claude.com/en/articles/17728952-what-is-the-ultra-plan) — Max 20x から Ultra への改称と Ultra の利用上限
> - [Unified Claude Enterprise (claude.com)](https://claude.com/resources/articles/unified-claude-enterprise) — 編集注記で Max / Ultra の改称日(2026-10-30)を確認
> - [Introducing Claude Duet (claude.com)](https://claude.com/resources/articles/claude-duet) / [Claude Duet Safety, Privacy, and Security (claude.com)](https://claude.com/resources/articles/claude-duet-safety-privacy-and-security) — プランの利用上限を共有する Claude Duet(2026-10-21 / 10-23)
> - [The full Claude Platform, available on Google Cloud (claude.com)](https://claude.com/resources/articles/claude-models-on-google-cloud-anthropic-managed) — Claude Models on Google Cloud (Anthropic managed) の GA(2026-10-22)
> - [Manage costs and demonstrate ROI for Claude Code on Google Cloud (claude.com)](https://claude.com/resources/articles/how-to-manage-costs-and-demonstrate-roi-for-claude-code-on-google-cloud) / [Smart reports, surveys, and pooled group budgets (claude.com)](https://claude.com/resources/articles/smart-reports-surveys-pooled-budgets) / [Expanding Claude for Nonprofits (claude.com)](https://claude.com/resources/articles/expanding-claude-for-nonprofits) — 組織のコスト統制(2026-10-26〜28)
> - [Strengthening our defenses against distillation attacks (anthropic.com)](https://www.anthropic.com/news/distillation-defenses) — preserved thinking と蒸留対策(2026-10-12)
> - [Claude Mythos 5.1 (platform.claude.com)](https://platform.claude.com/docs/en/models/mythos-5-1/overview) — Mythos の提供対象(verification programs で検証された組織)
> - [Environment variables (code.claude.com)](https://code.claude.com/docs/en/env-vars) — `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK`
> - [Introducing the Life Sciences Verification Program (anthropic.com)](https://www.anthropic.com/news/life-sciences-verification-program) — LSVP(2026-09-17)
> - [Expanding the Cyber Verification Program (anthropic.com)](https://www.anthropic.com/news/cyber-verification-program) — CVP の 3 tier 化(2026-10-06)
> - [Claude for Government is now generally available (claude.com)](https://claude.com/resources/articles/claude-for-government-is-now-generally-available) — Claude for Government の GA(2026-09-30)
> - [Fast mode (code.claude.com)](https://code.claude.com/docs/en/fast-mode) — fast mode の課金モデル(usage credits 直課金)
> - [What's new in Claude Fable 5.1 (platform.claude.com)](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1) — **Fable 5.1 の仕様と破壊的変更**
> - [Claude text watermark (anthropic.com)](https://www.anthropic.com/news/claude-text-watermark) — 生成テキストへの透かし埋め込み
> - [Why Claude switched models in your conversation with Opus 5 (support.claude.com)](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5) — claude.ai 側の自動フォールバック
> - [Pricing (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/pricing) — **Sonnet 5 の $2 / $10 恒久化**(2026-08-10)・5.5 世代の料金・Haiku 5.5 の prompt 長別料金
> - [Model deprecations (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/model-deprecations) — Sonnet 4.5 の Deprecated(2026-09-30)
> - [Claude Platform release notes (platform.claude.com)](https://platform.claude.com/docs/en/release-notes/overview) — Opus 4.1 の retirement 実行 / Sonnet 5 価格改定 / 5.5 世代のリリース / refusal 課金の再開
> - [Claude Code changelog (code.claude.com)](https://code.claude.com/docs/en/changelog) — 5.5 世代の対応版数・launch-default effort hold の停止(2.1.280)
> - [Improving Fable 5's biology safeguards (anthropic.com)](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards) — biology 分類器の false positive 約 85% 削減(2026-08-07)
>
> 最終更新: 2026-11-01（ClaudeCode v2.1.316 / Ultra プラン新設時点。版数は CHANGELOG による。前回は 2026-10-11・v2.1.296 時点）

**Claude 5.5 世代(Opus 5.5 = 2026-09-22 / Sonnet 5.5 = 09-28 / Haiku 5.5 = 10-07)** を反映し、現行の Fable 5.1 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 と、Legacy に移った Opus 5 / Sonnet 5 / Haiku 4.5 / Fable 5 の **消費トークン特性** と **サブスクプランの weekly limit がどう減るか** を、公式一次情報のみに基づいて整理する。Claude Code / claude.ai の Pro / Max / Ultra / Team ユーザーが「どのモデルをどこで使うか」を判断するための資料(Ultra は 2026-10-30 に Max 20x から改称されたプラン。§4.5)。2026-07-24 の Opus 5 GA 時点の整理は、各節に履歴として残している。

> 本ドキュメントは公式が数値で明示している事実のみを扱う。「Fable 5 は 2 倍速く減る」といった倍率の断定は、公式が明示していないため行わない。

---


## 0. 生成テキストの透かし（全モデル共通・今後）

EU AI Act 対応として、**今後の Claude モデルは生成テキストに知覚不能な透かしを埋め込む**。単語選択の乱数源を変える方式で、**出力品質・可読性・提供コストはいずれも変わらない**と公式が明言している。検出 API は規制当局・法執行・研究者向けのプライベートプレビューであり、一般利用者が自分の出力を検証する手段としては提供されていない。

本ドキュメントのトークン消費・料金の議論に影響はないが、**Claude Code が生成した成果物にも及ぶ**ため、生成物の由来を隠したい用途には向かないという前提として記録する。

出典: [Claude text watermark](https://www.anthropic.com/news/claude-text-watermark)(2026-08-14 公開。前回同期時点で既に公開されていたが取りこぼしていた)

## 1. TL;DR

- **2026-11-01 追記**: **2026-10-30 に Max 20x が Ultra に改称された**($200/月。既存契約は価格据え置きで自動移行。週次枠は Pro の 10 倍、verified accounts は 5 時間制限なし、月次 API credits $200)。Max は $100(Pro の 5 倍、API credits $100)で、Max と Ultra はどちらも Fable を週次枠の半分まで使える(§4.5)。**Opus 5.5 の fast mode は 2026-10-15 に research preview を外れ**、**Opus 4.8 の fast mode は 2026-10-30 に deprecated、2026-11-30 に削除される**(§6.5)。Claude Code v2.1.311 以降、ターミナルの `ultrathink` はそのターンを `xhigh` に上げられる(§6.3)。
- **Claude 5.5 世代が出そろった(2026-10-11 追記)**。**Opus 5.5 (`claude-opus-5-5`、2026-09-22)は $4 / $20 per MTok** で Opus 5 より 20% 安く、cache read は **$0.20(base input の 0.05x)**。公式は「既定設定の典型的なワークロードで Opus 5 より 40% 安い」とする。**Sonnet 5.5 (`claude-sonnet-5-5`、09-28)は $2 / $10**、cache read は 2026-10-07 に $0.20 → **$0.10(0.05x)** へ値下げされた。**Haiku 5.5 (`claude-haiku-5-5`、10-07)は prompt 100K 以下で $0.10 / $0.50、100K 超で $0.50 / $2.50** という prompt 長別の料金で、Haiku として初めて effort に対応した。Opus 5 / Sonnet 5 / Haiku 4.5 は Legacy に移った(§2)。
- Claude Code の要求版数は **Opus 5.5 = v2.1.280 / Sonnet 5.5 = v2.1.284 / Haiku 5.5 = v2.1.293**。v2.1.280 以降、`opus` と `default` は Pro / Team Standard を含む全プランで Opus 5.5 に解決される(Microsoft Foundry を除く。§2.1)。
- **既定 effort が世代で変わった**。API の既定は Opus 5.5 / Haiku 5.5 が `medium`、その他は `high`。Claude Code の既定は Opus 5.5 / Sonnet 5.5 / Haiku 5.5 が `medium`(§6.3)。
- **Opus 5.5 は thinking を一切無効化できない**(`disabled` も `enabled` + `budget_tokens` も 400)。`tool_choice` の `any` / `tool` も 400 になる(§3.3)。
- **Claude Opus 5 (`claude-opus-5`) が 2026-07-24 に GA**(当時の記録)。**$5 / $25 per MTok**(Opus 4.8 と同額)で、`opus` / `default` エイリアスの解決先が Opus 5 になった(v2.1.219〜v2.1.279。v2.1.280 以降は Opus 5.5)。**Claude Code は v2.1.219 以上が必須**。
- Fable 5.1 / Fable 5 の API 料金は **$10 / $50 per MTok**。Opus 5.5 (**$4 / $20**) の 2.5 倍、Opus 5 / Opus 4.8 (**$5 / $25**) の 2 倍、Sonnet 5.5 / Sonnet 5 (**$2 / $10**) の **5.0 倍**、Haiku 4.5 (**$1 / $5**) の 10 倍、Haiku 5.5 の 100 倍(prompt 100K 以下。100K 超なら 20 倍)。
- Fable 5 の tokenizer は Opus 4.7 と同じ世代。**Opus 4.7 より前のモデルと比べ、同じテキストが約 30% 多くトークン化される**(公式明記。§3.2)。旧世代 tokenizer は Opus 4.6 系・Sonnet 4.5 以前・Haiku 4.5 が該当。Haiku 5.5 は新しい tokenizer に移り、Haiku 4.5 比 約 +30% になる。
- **Opus 5 は thinking が既定 ON**(Opus 4.8 からの破壊的変更)。加えて **effort `xhigh` / `max` では thinking を無効化できない**(400 エラー)。思考トークンが常に乗る前提でコストを見積もる必要がある。
- **Fable 5 のプロモは 2026-07-19 23:59:59 PT で終了済み**。終了後は **Max / Team premium seat のみ weekly limit の 50% まで追加費用なしで継続**、**Pro / Team standard seat は usage credits が必要**になった(§5.3)。2026-10-30 以降の個人プランでは、Max と Ultra(旧 Max 20x)がこの 50% 枠の対象である(公式 pricing「Both plans include Fable, our top model, for up to half your weekly limit」)。
- Fable 5 は「Fable 5 draws from your plan's regular weekly usage limit and **uses it faster than other Claude models**」と公式が明記。倍率は非公開だが、原因は① per-token 料金が高い、② tokenizer が Opus 4.7 世代、③ Adaptive thinking が always on の 3 点。
- Claude Code で Fable 5 を使うには **v2.1.170 以上**、Fable 5.1 には **v2.1.257 以上**が必須。
- API 経由は promotion の対象外で、常時**標準の API レートで課金**される。**2026-10-07 から Max / Team プランに月次の API credits が付く**ようになったが、この credits は **Claude Code の利用には充当されない**(§4.5)。2026-11-01 時点の公式ページ名は「API credits for Max, Ultra, and Team plans」で、額は Max $100 / Ultra $200 / Team 上限 $500 である。

---

## 2. 現行モデル一覧(2026-10-11 時点)

**2026-07-24 の Opus 5 GA に伴い、公式 Models overview では Opus 4.8 / 4.7 が Legacy models アコーディオンへ移動した**。本表もそれに合わせ、Opus 5 を現行列に、Opus 4.8 を Legacy 側に移している(Opus 4.8 の記述自体は履歴として下の Legacy 注記に保全する)。

**2026-09-03 更新: Fable 5.1 が登場し、`platform.claude.com` の Models overview では Fable 5 が Legacy models へ移動した**。本表も Fable 5.1 を現行列に置き、Fable 5 を Legacy 注記へ移している。⚠️ ただし **`code.claude.com` の ClaudeCode docs では Fable 5 が現役として並記されており、両者に温度差がある**（fallback 表・effort 表はいずれも「Fable 5.1 and Fable 5」と両方を対象に記載している）。

**2026-10-11 更新: Claude 5.5 世代(Opus 5.5 / Sonnet 5.5 / Haiku 5.5)が登場し、Models overview の現行 4 モデルは Fable 5.1 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 になった**。Opus 5 / Sonnet 5 / Haiku 4.5 は Legacy models へ移った。本表は世代の変化を追えるよう、5.5 世代の 3 列を現行として足し、Legacy に移った 3 列は 2026-09-03 時点の値を基本に右側へ残している(公式で誤りが判明したセルだけ、注記を付けて直した)。公式 overview の推奨は「迷ったら Opus 5.5 から始め、要求の厳しい推論や長時間の agentic 作業、あるいは Opus 5.5 を高 effort にしても eval が足りない場合に Fable 5.1 を使う」である。

| 項目 | Claude Fable 5.1 | **Claude Opus 5.5** | **Claude Sonnet 5.5** | **Claude Haiku 5.5** | Claude Opus 5(Legacy) | Claude Sonnet 5(Legacy) | Claude Haiku 4.5(Legacy) |
|---|---|---|---|---|---|---|---|
| **API ID** | `claude-fable-5-1` | `claude-opus-5-5` | `claude-sonnet-5-5` | `claude-haiku-5-5` | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` |
| **Claude API alias** | `claude-fable-5-1` | `claude-opus-5-5` | `claude-sonnet-5-5` | `claude-haiku-5-5` | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5` |
| **リリース日** | 2026-09-01 | **2026-09-22** | **2026-09-28** | **2026-10-07** | 2026-07-24 | 2026-06-30 | 2025-10-15 |
| **位置づけ** | For demanding reasoning and long-horizon agentic work | For long-running agentic coding and knowledge work(**公式の第一候補**) | The best combination of speed and intelligence | For high-volume, latency-sensitive tasks such as classification, extraction, and routing | Complex agentic coding and enterprise work(Legacy 化前の第一候補) | Best combination of speed and intelligence | Fastest model with near-frontier intelligence |
| **入力料金** | **$10** / MTok | **$4** / MTok | **$2** / MTok | **$0.10** / MTok(prompt 100K 超は $0.50)※8 | $5 / MTok | **$2** / MTok ※1 | $1 / MTok |
| **出力料金** | **$50** / MTok | **$20** / MTok | **$10** / MTok | **$0.50** / MTok(prompt 100K 超は $2.50)※8 | $25 / MTok | **$10** / MTok ※1 | $5 / MTok |
| **Cache read** | **$0.25 / MTok（base input の 0.025x）** ※5 | **$0.20 / MTok(0.05x)** ※5 | **$0.10 / MTok(0.05x)** ※5 | $0.01 / MTok(prompt 100K 超は $0.05。0.1x) | $0.5 / MTok(0.1x) | $0.2 / MTok(0.1x) | $0.1 / MTok(0.1x) |
| **Context window** | **1M tokens** | 1M tokens | 1M tokens | **1M tokens**(100K 超は割増料金)※8 | **1M tokens(既定かつ最大。小さい context variant なし)** | 1M tokens | 200k tokens |
| **Max output(Messages API 同期)** | 128k tokens | 128k tokens | 128k tokens | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **Max output(Batch API、`output-300k-2026-03-24` beta)** | — ※2 | 300k tokens | 300k tokens | 300k tokens | 300k tokens | 300k tokens | — ※2 |
| **Extended thinking** | No | No | No | No | No | No | **Yes** |
| **Adaptive thinking** | **Yes (always on)** | **Yes (always on)** ※3 | Yes(既定 ON)※3 | Yes(既定 ON)※3 | **Yes(既定 ON)** ※3 | Yes(既定 ON)※3 | No |
| **Default effort** | `high` | **`medium`** | API: `high` / Claude Code: `medium` ※6 | **`medium`** ※6 | `high` | `high` | **Not supported** ※6 |
| **Comparative latency** | Slower | Moderate | Fast | Fastest | Moderate ※9 | Fast ※9 | Fastest ※9 |
| **Reliable knowledge cutoff** | **Jun 2026** | **Jun 2026** | **Jun 2026** | **Jun 2026** | May 2026 | Jan 2026 | Feb 2025 |
| **Data retention** | 30-day、**ZDR 非対応**(Anthropic が明示的に認めた場合を除く。Covered Model) | ZDR で利用可(公式アナウンス明記。Priority Tier は非対応) | ZDR で利用可(公式アナウンス明記) | 公式アナウンスに明記なし(Priority Tier は非対応) | 通常設定に従う ※4 | ZDR で利用可(公式アナウンス明記) | 通常設定に従う |
| **Tentative retirement** | 2027-09-01 以降 | 2027-09-22 以降 | 2027-09-28 以降 | 2027-10-07 以降 | 2027-07-24 以降 | 2027-06-30 以降 | **2026-10-15 以降** ※7 |
| **Claude Code 最低バージョン** | **v2.1.257** ※10 | **v2.1.280** | **v2.1.284** | **v2.1.293** | **v2.1.219** | v2.1.197 | — |

※1: **Sonnet 5 の恒久価格は $2 / $10 per MTok である**(2026-09-03 更新: 表のセルを実売価格に直した。以前は launch 時の定価表記 $3 / $15 を載せていた)。当初 introductory pricing として「2026-08-31 まで」とされていたが、**2026-08-10 に恒久化された**。公式は「The $2/$10 … announced at launch as introductory pricing through August 31, 2026, **is now the standard price. The previously scheduled increase to $3/$15 per million input/output tokens on September 1, 2026 will not occur.**」と明記している。**9 月以降の値上げを前提にコストを組み直す必要はない**。

> **経緯の保全(2026-08-12 更新)**: 2026-08-04 時点では「2026-08-31 で introductory 終了 → 9/1 以降 $3 / $15 に戻る」と記載していた。これは当時の公式表記に基づく正しい記述だったが、**2026-08-10 の release notes で値上げ中止が announced** されたため事実が反転した。Sonnet 5 は前世代 Sonnet 4.6($3 / $15)より**恒久的に 33% 安い**ことになる。出典: [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview) / [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

※2: 公式 note で 300k output beta の対象として明記されているのは **Opus 5.5** / **Opus 5** / Opus 4.8 / 4.7 / 4.6・**Sonnet 5.5** / Sonnet 5 / 4.6・**Haiku 5.5**。Fable 5.1 / Fable 5 / Haiku 4.5 は対象外(2026-10-11 更新: 5.5 世代の 3 モデルが加わった)。
※3: 各世代の**破壊的変更**。Opus 5 は Opus 4.8 から「未指定で thinking が走る」ようになった。Opus 5.5 は Opus 5 からさらに「thinking を無効化できない」ようになった。Sonnet 5.5 は `disabled` を受け付けず `between_tools` で up-front thinking を切る。Haiku 5.5 は Haiku 4.5 の extended thinking(`budget_tokens`)を受け付けない。詳細は §3.3。**2026-10-11 訂正**: Sonnet 5 のセルは以前「Yes」(thinking 未指定なら thinking なし)としていたが、現行の公式 [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) と Sonnet 5.5 migration guide はいずれも Sonnet 5 を「`thinking` 未指定で adaptive thinking が走る」モデルとしているため直した。
※4: Opus 5 は **Web fetch 非対応 / Priority Tier 非対応**と以前は書いていたが、**2026-11-01 時点の根拠ページ([Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview))からこの記述は消えており、現行の公式では未確認である**。ZDR 非対応(Covered Model)の明記は公式にないため、Fable 5.1 と異なり通常設定に従うものとして扱う。Opus 5.5 / Sonnet 5.5 / Sonnet 5 の ZDR は、Sonnet 5.5 のアナウンスが「As with Opus 5.5 and Sonnet 5, Claude Sonnet 5.5 is available with zero data retention」と明記している。Haiku 5.5 の Priority Tier 非対応は Haiku 5.5 migration guide、Opus 5.5 の Priority Tier 非対応は Opus 5.5 migration guide(「Priority Tier is not supported on Claude Opus 5.5」)による(2026-11-01 追記)。Fable 5.1 / Mythos 5.1 の ZDR は、What's new in Claude Fable 5.1 が「aren't available under zero data retention unless expressly authorized by Anthropic」とする。
※5: **cache read の割引率はモデルで 3 段階ある**(2026-10-11 訂正: 以前は「Fable 5.1 と Mythos 5.1 だけが優遇」と書いていたが、5.5 世代で対象が増えた)。公式 pricing の脚注は「prompt cache reads cost 10% of the base input price (**2.5% on Claude Fable 5.1 and Claude Mythos 5.1, 5% on Claude Opus 5.5 and Claude Sonnet 5.5**)」。つまり Fable 5.1 / Mythos 5.1 = 0.025x、Opus 5.5 / Sonnet 5.5 = 0.05x、その他(Fable 5 / Opus 5 / Sonnet 5 / Haiku 5.5 / Haiku 4.5 など)= 0.1x である。**Sonnet 5.5 は launch 時 $0.20(0.1x)で、2026-10-07 に $0.10(0.05x)へ値下げされた**(cache write ほかの料金は据え置き)。長時間の agent ループでキャッシュヒット率が高い用途では、この差が実効コストを大きく変える。
※6: **effort の既定は API と Claude Code で異なる**(2026-10-11 訂正: 以前は「effort 対応モデルの既定は一律 `high` で、例外は Opus 4.7 のみ `xhigh`」と書いていた)。**API**(公式 [Effort](https://platform.claude.com/docs/en/build-with-claude/effort))では Opus 5.5 / Haiku 5.5 が `medium`、それ以外の effort 対応モデルは `high` である(Opus 4.7 も API の既定は `high` で、`xhigh` は明示指定が要る)。**Claude Code**(公式 [Model configuration](https://code.claude.com/docs/en/model-config))では Opus 5.5 / Sonnet 5.5 / Haiku 5.5 が `medium`、Opus 4.7 が `xhigh`、それ以外は `high` である。**Sonnet 5.5 だけ両者が食い違う**(API = `high`、Claude Code = `medium`)が、Sonnet 5.5 のアナウンスも「In Claude Code and our apps, the default effort is set to Medium, while the Claude Platform defaults to High」と書いており、意図的な差と読める。**Haiku 4.5 は effort に非対応**（公式 effort 表で `Not supported`）で、**Haiku 5.5 は Haiku 系で初めて effort に対応した**(5 段階)。
※7: **Haiku 4.5 の retirement は 2026-10-15 以降と近い**(2026-10-11 更新: 以前は「現行 4 モデル中で最も近い」と書いていたが、Haiku 5.5 の登場で Haiku 4.5 は Legacy に移った)。**2026-11-01 追記**: その日付を過ぎた 2026-11-01 時点でも、deprecations ページは `claude-haiku-4-5-20251001` を Active・「Not sooner than October 15, 2026」のまま載せており、Deprecated にも Retired にもなっていない。実際の退役日は未確認である。他の Legacy は Fable 5 = 2027-06-09 以降、Opus 5 = 2027-07-24 以降、Sonnet 5 = 2027-06-30 以降、Opus 4.8 = 2027-05-28 以降。**Sonnet 4.5 は 2026-09-30 に Deprecated となり、2026-11-30 に Claude API で退役する**(移行先は `claude-sonnet-5-5`)。
※8: **Haiku 5.5 は prompt 長で料金が変わる**。公式 pricing は「a request whose prompt is over 100,000 tokens pays higher prices」とし、prompt 長には cache read / cache write を含む全 input tokens を数える。100K を超えたリクエストは、その一部が cache hit でも高い料金になる。100K 以下では Haiku 4.5($1 / $5)の 10 分の 1、100K 超でも半額である。他の Claude 4.6 以降のモデルは 1M 全域が標準料金で、この割増があるのは Haiku 5.5 だけである。
※9: Comparative latency は「現行ラインナップ内での相対値」である。Legacy 列は現行だった時点の表記をそのまま残しており、5.5 世代との比較には使えない。
※10: **2026-10-11 訂正**: Fable 5.1 の Claude Code 最低版数を以前は v2.1.255 と書いていたが、公式 model-config は「Fable 5.1 requires Claude Code v2.1.257 or later」としている。

> **Legacy(現行と併売中。2026-10-11 時点)**: **Claude Opus 5 / Sonnet 5 / Haiku 4.5**(上表の Legacy 列。5.5 世代の登場で Legacy に移った)、**Claude Fable 5 (`claude-fable-5`、$10 / $50、1M、Adaptive Yes always on、knowledge cutoff Jan 2026、cache read 0.1x、tentative retirement 2027-06-09 以降、要 v2.1.170 — Fable 5.1 登場前の Fable)**、**Opus 4.8 ($5 / $25、1M、Adaptive Yes / Extended No、knowledge cutoff Jan 2026 — Opus 5 GA 前の既定 Opus)**、Opus 4.7 ($5 / $25、1M、Adaptive Yes / Extended No)、Opus 4.6 ($5 / $25、1M)、Opus 4.5 (200k)、Sonnet 4.6 ($3 / $15、1M)。**Sonnet 4.5 は 2026-09-30 に Deprecated となり、overview の Legacy 一覧から外れた**(Claude API での退役は 2026-11-30、移行先は Sonnet 5.5)。**Opus 4.1 は 2026-08-05 に retirement 済み**(移行先の表記は下記のとおり公式内で揺れている)。Opus 5 の tentative retirement は **2027-07-24 以降**。

> **Opus 4.1 の retirement は実行された(2026-08-12 更新)**: `claude-opus-4-1-20250805` は公式 [model-deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) で Current state = **`Retired`** となり、履歴節にも「This model **was retired** August 5, 2026.」と記載された。**現在は全リクエストがエラーを返す**。models overview の Legacy 表からも消えている。
>
> 2026-08-04 時点では「Deprecated のまま retirement 未実行、tentative date は 2026-08-05 で据え置き」と記録していたが、予定通り実行された形である。移行先の表記揺れ(deprecations 側が `claude-opus-4-8`、overview 側が Opus 5)については、以前「release notes 側が Opus 5 で統一されたことで解消した」と書いていた。**2026-10-11 訂正**: release notes の retirement 項目は Opus 5 を推奨しているが、deprecations ページの履歴表は 2026-10-11 時点でも推奨移行先を `claude-opus-4-8` としており、**揺れは解消していない**。
>
> ⚠️ **「Legacy」と「Deprecated」は別軸である**: overview の "Legacy models" 一覧には Fable 5 / Opus 5 / Opus 4.8 / 4.7 / 4.6 / 4.5 / Sonnet 5 / Sonnet 4.6 / Haiku 4.5 が入っているが(2026-10-11 時点。2026-08-12 時点の一覧は Opus 4.8 / 4.7 / 4.6 / 4.5 / Sonnet 4.6 / 4.5 だった)、deprecations ページの表では**同じモデルが Active** である。前者は「推奨世代かどうか」の表示区分、後者は「ライフサイクル上の状態」であり、**Legacy = 廃止予定ではない**。混同すると「Opus 4.8 はもう使えない」と誤読するため注意する。**2026-11-01 追記**: deprecations ページは Legacy をライフサイクルの用語として定義した(「Legacy: The model will no longer receive updates and might be deprecated in the future.」。Active → Legacy → Deprecated → Retired の 4 段)。つまり Legacy は「更新されなくなり、将来 Deprecated になりうる」状態で、廃止日が決まった状態ではない。ただし同ページの Model status 表は、overview で Legacy とされるモデルを 2026-11-01 時点でも Active と表示している。逆に Sonnet 4.5 は 2026-09-30 に Deprecated になった時点で Legacy 一覧から外れており、Legacy を経て Deprecated に進む例になっている。

### 2.1 モデル ID とエイリアス

- **バージョン付き ID**(例: `claude-opus-5`)は pinned snapshot。バージョンレスなエイリアス的表記でも同じ snapshot を指す(Claude 4.6 世代以降は dateless format も pinned snapshot 扱い)。
- Claude Code の `/model` メニューには、Fable 5 導入と同時に **`fable`** と **`best`** というエイリアスが追加された(要 v2.1.170 以上)。**v2.1.257 以降、`fable` は Fable 5.1 に解決される**(Claude apps gateway セッションでは `fable` / `best` とも Fable 5)。v2.1.257 未満では `fable` = Fable 5 だった。`best` は Fable が使えれば `fable` の解決先、使えなければ `opus` と同じモデルになる。Fable 5 を使うには `/model claude-fable-5` のようにモデル ID で指定する。v2.1.219 では merged Opus 行の表示が「Opus (1M context)」に変わり、最新モデル名のみがハイライトされる。**v2.1.311 で、`[1m]` suffix が意味を持たないモデル(ネイティブ 1M のモデル)ではモデル名と ID から suffix とラベルが外れた**(suffix 自体は引き続き受け付ける。CHANGELOG 2.1.311)。「Opus (1M context)」の表示が現在も残るかは未確認である。
- `opus` / `sonnet` / `haiku` エイリアスの解決先は **プロバイダ依存**。**v2.1.280 以降、`opus` は Anthropic API / Claude Platform on AWS / Bedrock / Google Cloud's Agent Platform で Opus 5.5 に解決される**(Microsoft Foundry は Opus 4.6)。v2.1.219〜v2.1.279 はこの 4 プロバイダで Opus 5、それ以前は Opus 4.8 だった。Anthropic API では **`sonnet` が v2.1.284 から Sonnet 5.5、`haiku` が v2.1.293 から Haiku 5.5** に解決される(他プロバイダでは Sonnet 4.6 / 4.5・Haiku 4.5 のまま)。**プロバイダ別解決表は `docs/best-practices.md` の「model alias のプロバイダ別解決」を参照**。
- **`default` の解決先**(アカウント種別の既定。v2.1.280 で Pro / Team Standard の分岐がなくなった):

| アカウント種別 | v2.1.280 以降 | v2.1.219〜v2.1.279(履歴) |
|---|---|---|
| Pro / Team Standard | **Opus 5.5** | Sonnet 5 |
| Max / Ultra / Team Premium / Enterprise / Anthropic API | **Opus 5.5** | Opus 5 |
| Claude Platform on AWS / Bedrock / Google Cloud's Agent Platform | **Opus 5.5** | Opus 5 |
| Microsoft Foundry | Sonnet 4.5 | Sonnet 4.5 |

> 出典は公式 [Model configuration](https://code.claude.com/docs/en/model-config) の「Before v2.1.280, `default` resolved to Sonnet 5 on Pro and Team Standard, and to Opus 5 on Max, Team Premium, Enterprise, the Anthropic API, ...」と、CHANGELOG 2.1.280 の「Changed the default model on Pro and Team Standard plans from Sonnet to Opus」。旧表は Enterprise を pay-as-you-go(Opus 5)と subscription seat(Sonnet 5)に分けていたが、現行の公式記述は Enterprise を分けていない。Enterprise の管理者が organization default model を設定していれば、`default` はそちらに解決される。2026-11-01 更新: 現行の model-config は Ultra(2026-10-30 に Max 20x から改称)を Max と並べて記載しているため、表の行に足した。
>
> Microsoft Foundry の既定は Sonnet 4.5 のままだが、**Sonnet 4.5 は 2026-09-30 に Deprecated となり、2026-11-30 に Claude API で退役する**。公式 overview によれば Foundry は Claude API のライフサイクルに従う。
>
> Fable 5.1 / Fable 5 は**どのアカウント種別でも `default` にならない**。使う場合は `/model fable` または `/model best` で明示的に選択する。

### 2.2 1M context を抑制する環境変数(v2.1.223 で意味が変わった)

`CLAUDE_CODE_DISABLE_1M_CONTEXT` は 1M context を 200K に抑制する環境変数だが、**v2.1.223 で対象範囲が変わった**。

| 版 | 挙動 |
|---|---|
| v2.1.222 以前 | **固定のモデルリスト**に対してのみ 200K へ抑制 |
| **v2.1.223 以降** | **ネイティブ 1M context を持つ全モデル**を 200K へ抑制。抑制が効いていない状態は**起動時に警告**される |

- 上表の現行 4 モデル(Fable 5.1 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5)は**すべてネイティブ 1M** であり、v2.1.223 以降は事実上「現行モデルの全部が 200K になる」と考えてよい(2026-10-11 更新: 以前は「Haiku 4.5 以外はすべてネイティブ 1M」と書いていたが、Haiku 5.5 も 1M になった。Haiku 5.5 は prompt 100K 超で割増料金になる点だけが他と違う)。ネイティブ 1M のモデルは、既定で約 967K トークンで auto-compact される(公式 model-config)。
- 併せて **未知の model ID のセッションも、想定されるコンテキスト量の範囲内で auto-compact されるようになった**。旧挙動に戻すには `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` を設定する。
- 設定ファイル側の記述は [config-files.md](config-files.md) を参照。

---

## 3. トークン消費を決める 3 つの軸

「Fable 5 は他モデルより速くプラン枠を消費する」という公式表現の内訳を、事実として確認できる 3 つの軸に分解する。

### 3.1 per-token API 料金

| モデル | 入力 | 出力 | Opus 5 基準の倍率(入力) | Opus 5 基準の倍率(出力) | Opus 5.5 基準の倍率(入出力とも) |
|---|---|---|---|---|---|
| Fable 5.1 / Fable 5 | $10 | $50 | **2.0x** | **2.0x** | **2.5x** |
| **Opus 5.5** | **$4** | **$20** | 0.8x | 0.8x | **1.0x** |
| Opus 5 (legacy) | $5 | $25 | 1.0x | 1.0x | 1.25x |
| Opus 4.8 (legacy) | $5 | $25 | 1.0x | 1.0x | 1.25x |
| **Sonnet 5.5** | **$2** | **$10** | 0.4x | 0.4x | 0.5x |
| Sonnet 5 (legacy、**現行の標準価格**) | **$2** | **$10** | **0.4x** | **0.4x** | 0.5x |
| Sonnet 5(launch 時の定価表記) | $3 | $15 | 0.6x | 0.6x | 0.75x |
| **Haiku 5.5**(prompt 100K 以下) | **$0.10** | **$0.50** | 0.02x | 0.02x | 0.025x |
| **Haiku 5.5**(prompt 100K 超) | $0.50 | $2.50 | 0.1x | 0.1x | 0.125x |
| Haiku 4.5 (legacy) | $1 | $5 | 0.2x | 0.2x | 0.25x |

> **Opus 5 は Opus 4.8 と同額**($5 / $25)であるため、世代交代による per-token 料金の上昇はなかった。**Opus 5.5 は Opus 5 より per-token で 20% 安い**($4 / $20)。公式アナウンスは、1 タスクあたりのトークン数も減るため「既定設定の典型的なワークロードで Opus 5 より 40% 安い」とする。2026-10-11 更新で「Opus 5.5 基準」の列を足し、旧来の「Opus 5 基準」の列は比較の連続性のため残した。

API 経由(pay-as-you-go)では、この料金差がそのままドル単価に反映される。サブスクプランの weekly limit もこの料金体系をベースに設計されているため、**同じトークン数を消費した場合、Fable は Opus 5.5 の 2.5 倍、Sonnet 5.5 / Sonnet 5 の 5 倍、Haiku 4.5 の 10 倍、Haiku 5.5 の 100 倍(prompt 100K 超なら 20 倍)のペースで枠が減る**と推測できる(公式は正確な倍率を明示していない)。**2026-10-11 訂正**: 以前は「Sonnet 5 の 3〜5 倍」と書いていたが、これは実施されなかった値上げ後の $3 / $15 を含めた幅だった。Sonnet 5 の $2 / $10 は恒久価格(※1)で、Sonnet 5.5 も同額のため 5 倍で確定する。

**cache read の割引率は 3 段階ある**。Fable 5.1 / Mythos 5.1 は base input の 0.025x（$0.25 / MTok）、**Opus 5.5 / Sonnet 5.5 は 0.05x**(Opus 5.5 = $0.20、Sonnet 5.5 = $0.10 / MTok)、その他は 0.1x である（Fable 5 は 0.1x のまま）。cache write は据え置き。公式アナウンスは、Opus 5.5 の cache read が Opus 5 より 60% 安く、Sonnet 5.5 の値下げ(2026-10-07)で Sonnet 5.5 は「most agentic work で約 20% 安くなる」とする(2026-10-11 更新: 以前は Fable 5.1 / Mythos 5.1 だけが優遇されていると書いていた)。

**fast mode の料金は別体系**である。**Opus 5.5 の fast mode は $8 / $40 per MTok**、Opus 5 / Opus 4.8 の fast mode はいずれも **$10 / $50 per MTok** で、いずれも通常の 2 倍の価格で、1M context の全域にフラット適用される。速度は Opus 5 / 4.8 が約 2.5 倍、Opus 5.5 も公式アナウンスが「up to 2.5x speed」とする。(2026-10-11 時点の記述)**fast mode は Claude API(first-party)のみ**で、Claude Platform on AWS / Bedrock / Google Cloud / Microsoft Foundry では利用できない(research preview)。

**2026-11-01 更新**: **Opus 5.5 の fast mode は 2026-10-15 に research preview を外れた**(research preview は Opus 5 / 4.8 のみ)。API では、Opus 5.5 の fast mode を Claude API に加えて **Microsoft Foundry(Azure ホストの deployment、2026-10-15)と Claude Models on Google Cloud (Anthropic managed)(2026-10-22)** でも $8 / $40 で使える(公式 pricing)。一方、Claude Code の公式 Fast mode ページは今も「It is not available on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or Claude Platform on AWS」と書くため、**API の提供範囲と Claude Code の提供範囲は分けて読む**。**Opus 4.8 の fast mode は 2026-10-30 に deprecated となり、2026-11-30 に削除される**。詳細は §6.5。

### 3.2 tokenizer 世代差(Opus 4.7 以降で 約 30% 増)

公式 [What's new in Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1) は Fable 5.1 の tokenizer を次のように書いている。

> Tokenizer: the same as Claude Fable 5 (introduced with Claude Opus 4.7). Compared with models older than Claude Opus 4.7, the same text produces roughly 30% more tokens.

(履歴: 2026-09-03 までは、Models overview の Fable 5 の context window の tooltip にある「Claude Fable 5 uses the tokenizer introduced with Claude Opus 4.7; compared to models before Claude Opus 4.7, the same text produces roughly 30% more tokens.」を引用していた。2026-10-11 時点の overview と各モデルの仕様カードは、この tooltip の代わりに「1M tokens is roughly 555k words ... on the current tokenizer (introduced with Claude Opus 4.7); models before it fit about 750k words in 1M tokens」という注記を置いている。)

| Tokenizer 世代 | 対象モデル | 同一テキストのトークン数 |
|---|---|---|
| Opus 4.7 世代(新) | **Opus 5.5** / **Sonnet 5.5** / **Haiku 5.5** / Fable 5.1 / Mythos 5.1 / **Opus 5** / **Sonnet 5** / Fable 5 / Mythos 5 / **Opus 4.8** / Opus 4.7(Sonnet 5 / 5.5 は 2026-11-01 に追加。下記) | 基準 |
| Opus 4.6 以前世代(旧) | Opus 4.6 / Sonnet 4.6 / Sonnet 4.5 / Opus 4.5 / Opus 4.1(**2026-08-05 retired**) / **Haiku 4.5** | 約 30% 少ない |

> **5.5 世代の tokenizer(2026-10-11 追記)**: Opus 5.5 は Opus 5.5 migration guide が「Claude Opus 4.7 introduced a new tokenizer, which later Opus models, including Claude Opus 5.5, also use.」と明記している。Haiku 5.5 は Haiku 5.5 の仕様カードが「It uses the same newer tokenizer as Claude 4.7 and later models, so the same text counts as approximately 30% more tokens than on Claude Haiku 4.5」と明記している。**Haiku 4.5 から Haiku 5.5 に移ると、同じテキストが約 30% 多くトークン化される**ため、per-token 単価の値下げ幅がそのまま実費の削減にはならない。Sonnet 5.5 は下記の Sonnet 5 と同じ扱いで、表には入れていない(2026-10-11 時点。2026-11-01 に表へ追加した。下記の解消注記を参照)。

> **Sonnet 5 も新 tokenizer だと確認できた(2026-08-16 更新)**: 従来「tooltip の文言から新 tokenizer の可能性が高いが公式の明示なし」としていたが、公式が **Sonnet 5 は新しい tokenizer を使用し、同一テキストで Sonnet 4.6 比 約 +30% のトークンになる**と明記していることを確認した(当時の出典は What's new in Sonnet 5 ページ)。**2026-10-11 出典張替え**: What's new in Sonnet 5 は [Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview) の仕様カード(Legacy)に移り、この記述は載っていない。現行の出典は [Claude Sonnet 5.5 migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide) の「Claude Sonnet 5.5 uses Claude Sonnet 5's tokenizer. Against Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5, the same text produces about 30% more tokens」であり、Sonnet 5.5 も同じ tokenizer である。
>
> - **1M context に実際に収まるテキスト量は減る**ため、`max_tokens` の見直しが要る。
> - per-token 単価の低下分は、このトークン増加で相殺される。
> - (2026-10-11 時点の記述・履歴)⚠️ **ただし「Opus 4.7 世代の tokenizer と同一かどうか」は依然として公式に明示がない**（増加率が Opus 4.7 世代の「1x〜1.35x」ではなく「Sonnet 4.6 比 +30%」という別の基準で書かれているため）。上表の世代区分に Sonnet 5 / Sonnet 5.5 を機械的に入れないのはこのためである。
> - **2026-11-01 解消**: 公式 [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) が「Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer ... This tokenizer produces approximately 30% more tokens for the same text. ... Claude Sonnet 4.6 and earlier models use the previous tokenizer.」と書いており、Sonnet 5 / Sonnet 5.5 は Claude 4.7 以降の新 tokenizer 側に入る。これを受けて上表の新世代の行に Sonnet 5 / Sonnet 5.5 を足した。

> **Opus 5 の tokenizer 世代が確定した(2026-08-04 更新)**: 2026-07-26 時点では「公式の明示がない(未確認)」としていたが、当時の公式 Migration guide が「Claude Opus 4.7 introduced a new tokenizer, which later Opus models, including Claude Opus 5, also use.」と明記していることを確認した。**2026-10-11 出典張替え**: [Migration guides](https://platform.claude.com/docs/en/about-claude/models/migration-guide) はモデル別ガイドへの索引ページになり、同じ記述は現在 [Claude Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide) に次の形で載っている。
>
> > **Claude Opus 4.7 introduced a new tokenizer, which later Opus models, including Claude Opus 5.5, also use.** … it may use roughly **1x to 1.35x** as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content).
>
> つまり **Opus 5 / Opus 5.5 は Opus 4.7 世代の tokenizer を継承**しており、Opus 4.7 / 4.8 / Opus 5 / Opus 5.5 / Fable 5 / Fable 5.1 / Mythos 5 はすべて同一 tokenizer である。増加率は Fable の記述が言う「約 30%」より幅を持たせた **1x 〜 1.35x(最大 ~35%、内容によって変動)** が公式の表現である。
>
> **実務上の含意**: 旧世代から Opus 5 / Opus 5.5 に移す際は ① `max_tokens` の再調整 ② compaction トリガ閾値の再調整 ③ クライアント側トークン推定ロジックの再テスト が公式に推奨されている。
>
> なお **prompt cache の最小長は Opus 5 で 1,024 → 512 トークンに引き下げられた**(Opus 4.8 は 1,024)ため、短いプロンプトでもキャッシュが効くようになり、実効コストはこの分だけ下がる余地がある。Opus 5.5 も 512 トークンで、**Sonnet 5.5 も Sonnet 5 の 1,024 から 512 トークンに下がった**(各 migration guide)。

### 3.3 Adaptive thinking / Extended thinking

| モデル | Extended thinking | Adaptive thinking | 意味 |
|---|---|---|---|
| Fable 5.1 / Mythos 5.1 | No | **Yes (always on)** | `thinking` パラメータを disabled にできない。effort で深さを制御。**さらに 5.1 固有の破壊的変更が 4 つある**(下記。2026-10-11 時点は 3 つとしていた) |
| **Opus 5.5** | No | **Yes (always on)** | `thinking` 未指定で adaptive thinking が走り、**一切無効化できない**(`disabled` も `enabled` + `budget_tokens` も 400)。effort が唯一の制御。`tool_choice` の `any` / `tool` も 400 |
| **Sonnet 5.5** | No | **Yes(既定 ON)** | `disabled` は 400。up-front thinking を切るには `thinking: {"type": "between_tools"}` を送る(effort `high` 以下。`xhigh` / `max` では 400)。`tool_choice` の `any` / `tool` は 400 |
| **Haiku 5.5** | No | **Yes(既定 ON)** | API では `disabled` を effort `high` 以下でのみ受け付ける(`xhigh` / `max` では 400)。Haiku 4.5 の `enabled` + `budget_tokens` は 400。**Claude Code では thinking を切れない**(下記) |
| Fable 5 / Mythos 5 | No | **Yes (always on)** | `thinking` パラメータを disabled にできない。effort で深さを制御 |
| **Opus 5** (legacy) | No | **Yes(既定 ON)** | `thinking` 未指定でも adaptive thinking が走る。無効化は effort `high` 以下でのみ可能 |
| Opus 4.8 (legacy) | No | Yes | `thinking` 未指定なら thinking なしで実行 |
| Sonnet 5 (legacy) | No | Yes(既定 ON) | `thinking` 未指定でも adaptive thinking が走る。`disabled` で無効化でき、effort による制約はない(2026-10-11 訂正: 以前は「同上」= thinking 未指定なら thinking なしと書いていたが、公式 Thinking ページの表は Sonnet 5 を既定 ON としている) |
| Haiku 4.5 (legacy) | **Yes** | No | Extended thinking を有効化して思考時間を確保できる。Adaptive はなし |

> **Fable 5.1 / Mythos 5.1 固有の破壊的変更(4 件。2026-11-01 更新)**:
>
> 1. **`tool_choice` の `any` / `tool` が 400 エラーになる。** ツールの使用を強制する呼び出し方はできず、`auto` 相当に設計を寄せる必要がある。
> 2. **Fable 5.1 の thinking block を読めるのは Fable 5.1 と Mythos 5.1 だけである。** 別モデルへ切り替える router や fallback が Fable 5.1 の thinking block を含むリクエストを送ると、API はそのブロックを**黙って落として**処理する(エラーにはならず、落ちたブロックは課金されない)。マルチモデル構成で「Fable 5.1 の推論を別モデルに引き継ぐ」実装は、その推論が失われる前提で組む必要がある。`thinking-binding-controls-2026-08-01` beta header を付けると、落とした block が top-level の `input_transformations` 配列で報告される(2026-11-01 追記)。
> 3. **thinking block より前を書き換えると、その block は無効になる。** `system` / `tools` / 以前のメッセージを改変して再送すると 400 になる。**2026-08-31 以降に作成されたアカウントでは強制**される。会話は append-only に保ち、指示やツールの変更は mid-conversation system message で行う。**2026-11-01 追記**: 同じ beta header で `thinking.block_binding.prefix_mismatch_behavior` を指定できる。`"error"` は 400 で拒否し、**`"drop_block"` は無効な block とそれ以降の thinking block を落としてリクエストを成功させる**(落とした block は `input_transformations` に `reason: "prefix_binding_mismatch"` で載る)。未指定時は Mythos 5.1 で 400、Fable 5.1 では 2026-08-31 以降に作成したアカウントで 400 になる。
> 4. **advisor tool(beta)の一部の組み合わせが 400 になる(2026-11-01 追記)。** advisor は executor 以上の能力が要る。Mythos 5 / Fable 5 / Opus 5.5 / Opus 5 の advisor は Fable 5 / Mythos 5 の executor とは組めるが、**Fable 5.1 / Mythos 5.1 の executor と組むと 400 `invalid_request_error`** になる。
>
> **2026-10-11 訂正**: 以前は破壊的変更を 2 件とし、2 件目を「thinking block は生成したモデル以降でしか読めない。履歴を改変して渡すと 400」と書いていた。公式は「別モデルが読めない」(黙って落とす)と「履歴の改変で無効になる」(400)を別々の破壊的変更として 3 件に数えている。**2026-11-01 訂正**: 公式は「If you already call Claude Fable 5, four changes are breaking」とし、advisor tool の組み合わせ(上記 4)を加えた 4 件に数えている。
>
> 出典: [What's new in Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1)

Fable 5 は **Adaptive thinking を無効化できない**設計のため、単純なタスクでも一定の思考トークンが生成される可能性が高い。これも「速く枠を消費する」要因の 1 つになる。

#### Opus 5 における thinking の破壊的変更(2 点)

Opus 4.8 から移行する際、以下 2 点は **API リクエストの書き換えが必要**になる。

| # | 変更点 | Opus 4.8 | **Opus 5** |
|---|---|---|---|
| 1 | **thinking の既定** | `thinking` 未指定なら thinking なしで実行 | **未指定で adaptive thinking が走る**。`max_tokens` は「thinking + response」合計に対する hard limit なので再調整が必要 |
| 2 | **thinking 無効化の可否** | effort と独立に無効化可 | **effort `high` 以下でのみ無効化可**。`thinking:{"type":"disabled"}` × effort `xhigh` / `max` は **400 エラー** |

> **thinking を無効化する場合の注意**: 公式は thinking 無効時の既知アーティファクトとして「tool call が構造化された `tool_use` ではなくテキストとして漏れる」「`<thinking>` 等の内部 XML タグが可視出力に混入する」を挙げている。**回避策は thinking を有効に保ったまま effort を下げること**であり、公式は「thinking ON + `low` effort は thinking OFF と同程度のコストでより高性能」と明言している。コスト削減目的で thinking を切るのは Opus 5 では逆効果になりやすい。

出典: [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) / [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) / [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)(2026-10-11 出典張替え: 旧出典の What's new in Claude Opus 5 は Opus 5 の仕様カードに移り、thinking の記述は Thinking ページに移った。旧 Migration guide はモデル別ガイドの索引になった)

#### 5.5 世代の thinking と互換性の変更(2026-10-11 追記)

| # | 変更点 | Opus 5 → **Opus 5.5** | Sonnet 5 → **Sonnet 5.5** | Haiku 4.5 → **Haiku 5.5** |
|---|---|---|---|---|
| 1 | **thinking の無効化** | **不可**(`disabled` / `enabled` とも 400) | `disabled` は 400。代わりに `between_tools`(effort `high` 以下) | `budget_tokens` は 400。`disabled` は effort `high` 以下で可 |
| 2 | **強制ツール使用**(`tool_choice` の `any` / `tool`) | 400 | 400 | **受け付ける**。ただし応答は tool call から始まり、`thinking` block は付かない(2026-11-01 更新: 以前は「migration guide に記載なし」) |
| 3 | **thinking block の互換性** | Opus 5.5 の block を読めるのは、Opus 5.5 自身を除けば Claude API 上の Fable 5.1 / Mythos 5.1 だけ。会話の改変で無効になる | Sonnet 5.5 の block は生成したアカウント(または連携アカウント)でしか効かない。会話の改変で無効になる | 生成したアカウントでしか効かない。会話の改変で 400 |
| 4 | **ツール呼び出し間の文章** | `text` ではなく progress-update の `thinking` block で返る(既定 `display: "omitted"` では空) | **1〜2 文を超えるメモだけ** progress-update の `thinking` block になり、短い発言は `text` のまま。`between_tools` では `display` を指定しなくても返る(2026-11-01 更新: 以前は「同上」) | — |

> **Haiku 5.5 の thinking 無効化は API と Claude Code で扱いが違う**(公式ソース間の差): API の公式 [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) は「You can also send `thinking: {"type": "disabled"}` at `high` effort or below」とする。一方 Claude Code の公式 [Model configuration](https://code.claude.com/docs/en/model-config) は「You can't turn thinking off on Opus 5.5, Sonnet 5.5, Haiku 5.5, or the Fable models」とし、`alwaysThinkingEnabled: false` や `MAX_THINKING_TOKENS=0` も効かない。**API 仕様としては無効化できるが、Claude Code の挙動としては無効化できない**と読み分ける。
>
> 出典: [Claude Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide) / [Claude Sonnet 5.5 migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide) / [Claude Haiku 5.5 migration guide](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide) / [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)

> **thinking の可否は Models API で取得できる(2026-11-01 追記)**: `GET /v1/models` と `GET /v1/models/{model_id}` の `capabilities.thinking.types.disabled`(2026-10-05 追加)と `capabilities.thinking.types.between_tools`(2026-10-15 追加)が、モデルごとに `thinking: {"type": "disabled"}` / `{"type": "between_tools"}` を受け付けるかを返す。上表のようなモデル別の分岐をハードコードせず、実行時に確かめられる。ただし `supported` が `true` でも、effort の組み合わせなど別の理由で 400 になることはある。出典: [Models overview](https://platform.claude.com/docs/en/models/overview) / [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)

#### preserved thinking と蒸留対策(2026-11-01 追記)

Anthropic は 2026-10-12 に蒸留(distillation)対策をまとめて公表した。thinking の扱いに次の制約が入っている。

| 対策 | 内容 | 影響 |
|---|---|---|
| **preserved thinking**(Fable 5.1 / Opus 5.5 で導入) | **2026-08-31 以降に作成した API アカウントは、Claude の過去の文脈を編集できない**。これらのモデルの推論は、蒸留対策の弱い旧モデルからは読めない | 上記の「会話の改変で無効」「別モデルは block を読めない」の背景である。会話は append-only に保つ |
| **Sonnet 5.5 の推論の組織限定** | Sonnet 5.5 の推論は、そのリクエストを出した組織だけが読める | 組織やアカウントをまたいで会話を移すと thinking が効かない |
| **推論抽出を防ぐ分類器** | 二段の分類器を Sonnet 5.5 / Opus 5 / Opus 5.5 / Fable 5 / Fable 5.1 で動かす。false positive は 0.1% 未満 | 出力前に止められた `reasoning_extraction` などのカテゴリは課金される(§6.4) |

- Sonnet 5.5 の公式アナウンスは、**Claude Code でセッションの途中にアカウントを切り替えると preserved thinking の影響を受ける**と書いている(「If you move conversations between accounts, including switching accounts mid-session in Claude Code, our docs article explains the change」)。
- 同じアナウンスの脚注は、FrontierCode で **Sonnet 5.5 の Max effort のスコアが Xhigh より低かった**と書く(Max では Claude Code の code-review skill を多く走らせ、タイムアウトや範囲外の編集につながった)。effort を上げれば必ず良くなるわけではない例である。

出典: [Strengthening our defenses against distillation attacks](https://www.anthropic.com/news/distillation-defenses) / [Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5)

---

## 4. サブスクプランでの weekly limit の消費速度

Claude Code / claude.ai の Pro / Max / Ultra / Team は「週次の使用制限」で運用される(Ultra は 2026-10-30 に Max 20x から改称。§4.5)。**Fable 5 の promotion は API ではなくこのサブスクプラン層に対する施策**である点に注意。

### 4.1 公式が明言していること

- **Fable 5 draws from your plan's regular weekly usage limit** and **uses it faster than other Claude models**.(サポート記事)
- promotion 期間中に **Fable 5 に振り分けられる上限は weekly limit の 50%**。追加課金なし。
- **promotion 終了後(2026-07-19 以降)の扱いはプランで分岐する**。Max / Team premium seat は **50% 枠が標準機能として継続**、Pro / Team standard seat は **weekly limit の対象外となり usage credits が必要**になった(詳細は §5.3)。2026-10-30 以降は Ultra(旧 Max 20x)も Max と同じく Fable を週次枠の半分まで使える。Ultra のヘルプ記事は「a weekly usage limit that applies across all models, and a separate weekly limit for Fable」と書く。

### 4.2 「速く消費する」の内訳(推測)

公式は倍率を明示していないが、§3 の 3 つの軸を組み合わせると次のように分解できる。

```
Fable 5 の 1 リクエスト当たりの weekly-limit 消費量 ≒
   トークン数(tokenizer 世代差で +30%)
 × 単価係数(Opus 4.8 の 2 倍相当)
 × 思考量(Adaptive thinking always on による思考トークン増)
```

Sonnet 5 と比べれば、単価差だけで **入力 5.0 倍・出力 5.0 倍** の消費速度差が生じる（$10 / $50 対 $2 / $10。2026-09-03 訂正: 旧記述の 3.3 倍は実施されなかった値上げ後の $3 / $15 を基準にした誤りだった）。ここに tokenizer と思考トークンが加わるため、公式が「uses it faster」と一言で片付けているのは妥当である。

### 4.3 50% 上限のロジック

サポート記事の FAQ から引用:

> No. You can use up to 50% of your weekly limit on Fable 5, but your use of other models draws from the same usage limits and you can never use more than your weekly limit.
>
> For example, if you've already used half of your weekly limit on other models, you have half of your overall limit left—so you can use Fable 5 up to that remaining amount, even though Fable 5's own limit is higher.

つまり:

- 「Fable 5 用の 50% 枠」は独立した割り当てではなく、**weekly limit 全体の残りに対する天井**。
- 他モデルで既に 50% 使っていたら、Fable 5 で使えるのは残りの 50% すべてが上限になる。
- 一方、他モデルを一切使わなくても Fable 5 単独で使えるのは 50% まで。残り 50% は他モデル用として温存される(または usage credits に切替)。

### 4.4 上限到達後の選択肢

| 選択肢 | 挙動 |
|---|---|
| **usage credits で継続** ⚠️ | Fable 5.1 / Fable 5 の追加使用は usage credits(サブスク外の別課金)から自動的に引き落とし。**ただし Claude Code は課金前に同意プロンプトを表示する**(Enterprise の組織課金メンバーは除外)。**無応答のまま `dialogExpiry`(既定 5 分)を過ぎると、ターンを送らずに終了する** — Remote Control / background session / agent team のような無人実行では、これが**サイレントな停止要因**になる。長時間の自律ループで Fable を既定モデルにしないこと。逆に **`-p` の非対話モードと、同意プロンプトを出さない Agent SDK アプリでは同意を求めずに usage credits へ課金される**(公式 model-config)。usage credits を有効化していれば billing が自動で切り替わる |
| **他モデルに切替** | 残っている weekly limit の範囲内で Opus 5.5 / Sonnet 5.5 / Haiku 5.5 などを継続利用(2026-10-11 更新: 以前の例示は Opus 4.8 / Sonnet 5 / Haiku 4.5 だった) |

usage credits の管理は [Manage usage credits for paid Claude plans](https://support.claude.com/en/articles/12429409) 参照。

### 4.5 プランまわりの更新(2026-09〜10)

| 日付 | 更新 | Claude Code への影響 |
|---|---|---|
| **2026-09-30** | **Claude for Government が GA**。FedRAMP High 認可環境で、連邦・州の機関向けに提供される。同じ環境・同じ管理コントロールで **Claude Code CLI の early access** も始まった | 公的機関の環境で Claude Code CLI が使えるようになった(early access への参加は public sector チーム経由) |
| **2026-10-07** | **Max / Team プランに月次の API credits が付く**。Max 5x = $100、Max 20x = $200、Team = Standard seat $20・Premium seat $100 を合算し上限 $500(組織でプール)。Claude Console の organization をプランに紐付けて受け取り、繰り越しはない(「Max 5x / Max 20x」は当時の表記。2026-10-30 以降の公式は Max $100 / Ultra $200 と書く。新規加入者は加入から 7 日経つまで受け取れない) | **Claude Code と Claude アプリの追加利用(extra usage)には充当されない**。自作のアプリやエージェントから Claude API を呼ぶ用途の credits である |
| **2026-10-21** | **Claude Duet(research preview)**。Opus 5.5 を前提に、クラウドの VM で先回りして動くエージェントアプリ。米国の Pro / Max / Ultra 加入者から waitlist 制で始まった | **プランの利用上限を Claude 全体と共有する**。数時間ごとのバックグラウンドのチェックも枠を消費し、大きなタスクほど多く減る。公式は提供開始を米国の利用者からとしており、それ以外の地域への提供は 2026-11-01 時点で記載がない |
| **2026-10-30** | **Max 20x が Ultra に改称**。既存の Max 20x 契約者は価格据え置きで Ultra へ自動移行した。Ultra = $200/月(月払いのみ)で、Max の全機能に加えて**週次枠が Pro の 10 倍**、**verified accounts は 5 時間制限なし**(未 verify のアカウントには一時的な制限がかかる)、月次 API credits $200。Max は $100/月で、Pro の 5 倍(5 時間ごと・週ごと)、API credits $100 | Claude Code も同じ枠を使う。Ultra は 5 時間制限がない代わりに、全モデル共通の週次枠と Fable 用の週次枠を持つ。Max と Ultra はどちらも Fable を週次枠の半分まで使える |

> Ultra の改称を告げる発表記事(news)は見つかっていない。改称日は、Enterprise 統合記事の編集注記「Mentions of Max in this post from before October 30, 2026 include what are now the Max and Ultra plans」による。Claude Duet は Claude アカウントの memory・skills・connector を引き継ぎ、操作の承認には Claude Code の auto mode 分類器を Duet 向けに拡張したチェックを使う。

出典: [Claude for Government is now generally available](https://claude.com/resources/articles/claude-for-government-is-now-generally-available) / [API credits for Max, Ultra, and Team plans](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers) / [Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5) / [Claude pricing](https://claude.com/pricing) / [What is the Ultra plan?](https://support.claude.com/en/articles/17728952-what-is-the-ultra-plan) / [Unified Claude Enterprise](https://claude.com/resources/articles/unified-claude-enterprise) / [Introducing Claude Duet](https://claude.com/resources/articles/claude-duet) / [Claude Duet Safety, Privacy, and Security](https://claude.com/resources/articles/claude-duet-safety-privacy-and-security)

### 4.6 組織のコスト統制(2026-10-26〜28)

Team / Enterprise やクラウド経由の組織向けに、Claude Code の支出を抑える仕組みが増えた。

| 仕組み | 内容 |
|---|---|
| **Claude apps gateway の spend cap** | user / IdP group / 組織ごとに、日・週・月の spend cap を掛けられる(group と組織の cap は各メンバーが継承する既定値で、共有プールではない)。Claude Code は cap の 75% と 95% を超えたところで CLI 上に警告を出し、cap に達すると gateway が期間のリセットか admin の引き上げまで **429** を返す。IdP group ごとにモデルの allowlist と既定モデルを決められる |
| **pooled group budgets**(Enterprise) | グループで 1 つの月次予算を共有する。member limit と併用でき、各リクエストは両方に数えられ、先に尽きた方で止まる。billing 権限を持つ admin には予算の 50 / 75 / 95 / 100% でメールが届く。**Claude Code v2.1.316 で Claude apps gateway にも入った**(spend limits admin API の `pooled_budget`) |
| **smart reports**(Enterprise) | チームの transcript のサンプルを分析して作業を workstream にまとめ、skill にすべき反復作業やリポジトリに足すべき rules を推奨する |
| **OpenTelemetry の内訳** | 最近の Claude Code は使用量と推定コストを skill / plugin / agent / MCP server 別に出す。`OTEL_RESOURCE_ATTRIBUTES`(例 `department=engineering,cost_center=eng-123`)で部門タグを全メトリクスとイベントに付けられる |
| **非営利プラン** | 非営利プランには Claude Code が追加費用なしで含まれる |

出典: [Manage costs and demonstrate ROI for Claude Code on Google Cloud](https://claude.com/resources/articles/how-to-manage-costs-and-demonstrate-roi-for-claude-code-on-google-cloud)(2026-10-27) / [Smart reports, surveys, and pooled group budgets for Claude Enterprise](https://claude.com/resources/articles/smart-reports-surveys-pooled-budgets)(2026-10-28) / [Expanding Claude for Nonprofits](https://claude.com/resources/articles/expanding-claude-for-nonprofits)(2026-10-26) / [Claude Code changelog](https://code.claude.com/docs/en/changelog)(2.1.316)

---

## 5. Fable 5 プロモーショナルアクセス(2026-07-01 〜 07-19、**終了済み**)

> **2026-07-26 時点で本プロモは終了している**。公式 support 記事は「that promotion **ends on July 19, 2026 at 11:59:59 PM PT**」と過去形で記載しており、**最終的な終了日は 2026-07-19 23:59:59 PT**(当初 07-07 → 07-12 → 07-19 と 2 回延長された)。**さらなる延長・恒久化は行われなかった**。終了後の扱いは §5.3 を参照。

### 5.0 前史(2026-06-12 停止 → 06-30 再開)

本プロモは「復帰記念プロモ」の位置づけである。2026-06-09 GA 時のプラン同梱と混同しないため、時系列で整理する。

| 日付 | 事象 | 出典 |
|---|---|---|
| 2026-06-09 | Fable 5 / Mythos 5 GA。当初は Pro / Max / Team / seat-based Enterprise に **06-22 まで** 追加費用なしで含まれる予定 | Fable 5 / Mythos 5 リリースアナウンス |
| **2026-06-12** | 米国 export controls により、Anthropic が **Fable 5 のグローバル提供を全面停止**(全ユーザー影響)。Anthropic は指令に従いつつ、狭い jailbreak 手法を理由に商用モデルをリコールする判断には反対と表明。他モデルへの影響はなし | [fable-mythos-access](https://www.anthropic.com/news/fable-mythos-access) / redeploying-fable-5 |
| 2026-06-22 | 当初の同梱終了予定日。ただし 06-12 停止が継続中で、同梱終了は事実上凍結 | 推定 |
| **2026-06-30** | export controls 解除 + Amazon researchers 発見の jailbreak 対策 safety classifier 導入(該当技術を 99% 以上ブロック)で **redeploy 発表** | redeploying-fable-5 |
| **2026-07-01 00:00 PT** | 本 §5 で扱う新プロモ開始 | support 15424964 |
| **2026-07-07** | 当初終了予定日。**ユーザーバックラッシュを受けて Anthropic が 5 日間延長を発表** | support 15424964 |
| 2026-07-12 23:59:59 PT | 1 回目の延長後の終了予定日。**さらに 7 日間延長された** | support 15424964 |
| **2026-07-19 23:59:59 PT** | **最終的な終了日(実績)**。以降の扱いはプラン別に分岐(§5.3) | support 15424964 |

- 出典: [Redeploying Fable 5 and Mythos 5 — anthropic.com](https://www.anthropic.com/news/redeploying-fable-5)(2026-07-11 確認) / [Claude Fable 5 promotional access — support.claude.com](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)(**2026-07-26 に終了日 07-19 を確認**)

### 5.1 期間と対象プラン

- **期間**: 2026-07-01 〜 **2026-07-19 23:59:59 PT**(終了済み。当初 07-07 → 07-12 → 07-19 と 2 回延長)
- **対象**:
  - Pro / Max / Team
  - Seat-based Enterprise の **Premium seat**(組織で有効化されている場合)
- **対象外**:
  - Free プラン
  - Seat-based Enterprise の **Standard seat**(usage credits を有効化していれば動作するが、全消費が credits 引き落とし)
  - **Usage-based Enterprise** プラン
  - **API 利用**(常に標準レート課金)

### 5.2 利用できる Claude 製品

- Claude on the web / Claude Mobile / Claude Desktop
- Claude Cowork(最新版の Claude Desktop 必須)
- **Claude Code**(**v2.1.170 以上必須**)
- Claude Design / Claude for Microsoft 365 / Claude for Teams / [Claude Tag](claude-tag.md)(Team / Enterprise のみ)

Claude on the web / Desktop / Mobile ではモデルピッカーから "Fable 5" を選択。Claude Code では `/model fable` または `/model best` で切り替える(§2.1)。

### 5.3 promotion 終了後の扱い(2026-07-19 以降・確定)

promotion 終了後の扱いは、当初想定されていた「全プラン一律で usage credits 必須」ではなく、**プラン別に分岐する形で確定した**。

| プラン | promotion 終了後の Fable 5 |
|---|---|
| **Max** | **プランの標準機能として継続。weekly limit の 50% まで追加費用なし** |
| **Team premium seat** | Max と同じ(50% まで included) |
| **Pro** | **プランの usage limit に含まれない。usage credits が必要** |
| **Team standard seat** | Pro と同じ(usage credits が必要) |
| **Ultra**(2026-10-30 に Max 20x から改称) | Max と同じ(週次枠の半分まで included)。2026-11-01 追記 |

- 対象となる Pro / Team standard seat には、変更の緩和措置として **one-time credit** が付与される(公式: 「Eligible Pro and Team standard seats qualify for a one-time credit to help with the change」)。
- 50% 枠のロジック自体は §4.3 のまま維持される。Max / Team premium seat でも「他モデルと同じ枠から引かれ、weekly limit 全体を超えることはできない」点は変わらない。
- Fable 5 は他モデルより枠を速く消費するという公式表現も維持されている。

> **利用環境への影響**: Max プランであれば promotion 終了後も 50% 枠が無償で継続するため、実務上の変化はない。Pro / Team standard seat を併用している場合のみ usage credits の有効化を検討する。

### 5.4 admin の制御

- Claude on the web / Desktop / Mobile: 組織 admin は **promotion 自体を無効化できない**(既定モデルは指定可能)。
- Claude Code: admin は **managed settings で Fable 5 を含むモデル可用性を制御可能**。Claude Code で Fable 5 が見えない場合、admin が制限している可能性がある。
- **新しいリリースの自動許可に注意(2026-10-11 追記)**: `availableModels` の `claude-opus-5` のようなエントリは、Claude Code が対応した時点で Opus 5.5 のような後続リリースも許可する。特定リリースを止めるには、**`deniedModels`**(列挙したモデルをブロック)か **`availableModelsMatch: "exact"`**(各エントリが名指しした版だけを許可)を managed settings に置く。どちらも **Claude Code v2.1.283 以降**が必要である(公式 [Model configuration](https://code.claude.com/docs/en/model-config))。

---

## 6. Claude Code での実務上の使い分け

### 6.1 モデル選択の指針

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| 通常のコーディング / 小規模 PR / コードレビュー | **Opus 5.5** | 公式の第一候補(Models overview「If you're unsure which model to use, start with Claude Opus 5.5 for most workloads」)。Opus 5 より per-token で 20% 安く、既定 effort `medium` で Opus 5 の `high` と同等以上の結果を出すと公式 model-config は述べる。2026-10-11 更新: 以前は Opus 5 を推奨し、当時の公式文言「start with Claude Opus 5 for complex agentic coding and enterprise work」を引用していた |
| 長時間の自律エージェンティックタスク(数時間〜、大規模 migration) | **Opus 5.5** または **Fable 5.1** | 公式 overview は「Use Claude Fable 5.1 for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher effort still fall short」とする。Opus 5.5 は Fable 5.1 の 0.4 倍の per-token 料金で済むため、まず Opus 5.5 を試すのが合理的。以前は同じ理由で「まず Opus 5、足りなければ Fable 5」としていた |
| 高速レスポンスが必要なドラフト生成 / スニペット拡張 | **Sonnet 5.5** | $2 / $10 で Opus 5.5 の 0.5 倍。cache read は 2026-10-07 に $0.10 へ値下げされた。以前は Sonnet 5 を推奨していた(Sonnet 5 の $2 / $10 は恒久価格化済みで、9/1 の値上げは中止) |
| バッチ処理・簡易分類 / メタデータ抽出 | **Haiku 5.5** | prompt 100K 以下なら $0.10 / $0.50 で Haiku 4.5 の 10 分の 1。Haiku として初めて effort に対応した。100K 超は割増料金になる(§2 ※8)。以前は Haiku 4.5($1 / $5、Extended thinking で複雑推論を部分的にカバー)を推奨していた |
| サイバー系の専門ワークロード | **Opus 4.8** 直接指定、または Cyber Verification Program / Project Glasswing 経由のアクセス | cybersecurity フラグで **Fable 5.1 / Fable 5 / Opus 5.5 / Opus 5 は Opus 4.8 に、Sonnet 5.5 は Sonnet 5 に fallback** される(§6.5)。公式は一般提供モデル(Opus 5.5 / Fable 5.1 / Sonnet 5.5)の cyber safeguard を「block most cyber work」と説明しており、検証済みの組織は 3 tier の CVP を申請できる(§6.5)。2026-10-11 更新: 以前は対象を「Fable 5 / Opus 5」とだけ書いていた。公式ベンチでは Opus 5 は cybersecurity exploitation で Mythos 5 に劣る(Opus 5 GA 時点の記録) |
| 生物・化学の専門ワークロード | Life Sciences Verification Program 経由のアクセス、または Mythos(Anthropic の verification programs(CVP など)で検証された組織のみ。2026-11-01 更新: 以前は「Project Glasswing 適格者のみ」と書いていた) | biology フラグで Fable 5.1 / Fable 5 / Opus 5.5 は Opus 5 に fallback されるが、**Opus 5 と Sonnet 5.5 は fallback されず refusal が確定する**(§6.5)。検証済みの life science 組織は LSVP を申請できる(§6.5) |
| ZDR(zero data retention)下 | Opus 5.5 / Sonnet 5.5 / Opus 5 / Sonnet 5 / Opus 4.8 等 | Fable 5.1 / Fable 5 は **ZDR 非対応**(30-day retention。Anthropic が明示的に認めた場合を除く)。Opus 5.5 / Sonnet 5.5 / Sonnet 5 の ZDR 対応は公式アナウンスに明記がある(§2 ※4) |

### 6.2 promotion 終了後(2026-07-20 以降)の運用

promotion が終了したため、Fable 5 の 50% 枠を前提とした運用は **Max / Ultra / Team premium seat** に限られる(§5.3。Ultra は 2026-10-30 に Max 20x から改称。それ以前の表記は「Max / Team premium seat のみ」)。

1. **既定は Opus 5.5** に置く(v2.1.280 以降は全プランの `default`)。Opus 5 より安く、Fable 5.1 の 0.4 倍の per-token 料金であるため、まず Opus 5.5 で足りるかを試す。
2. Fable(5.1 / 5)は「Opus 5.5 で足りなかった長時間タスク」に限定して投入する。Max / Ultra / Team premium seat なら weekly limit の 50% まで無償、Pro / Team standard seat は usage credits が必要。
3. 定型作業や lint 対応など軽量タスクは **Sonnet 5.5 / Haiku 5.5** に切替える。Opus 5.5 は既定が `medium` なので、さらに **effort を `low` に下げる**のも有効な節約手段になる(§6.3)。
4. **auto mode 併用**が推奨。長時間セッションで確認プロンプトが挟まると思考トークンを無駄にしがち。auto mode の分類器で安全性は担保できる(`docs/best-practices.md` §4「auto mode 詳細」参照)。

> **履歴**: promotion 期間中(2026-07-01 〜 07-19)は「weekly limit の前半 50% を Fable 5 に振り分け、軽量タスクは Sonnet 5 / Haiku 4.5 に流す」という運用が推奨されていた。終了後も Max / Team premium seat では同じ配分が使えるが、Opus 5 の登場により「まず Opus 5」が先に来る点が変わった。
>
> **2026-10-11 更新**: 5.5 世代の登場に合わせて 1〜3 を書き換えた。以前は「既定は Opus 5 / Fable 5 は Opus 5 で足りないタスクに限定 / 軽量タスクは Sonnet 5・Haiku 4.5、Opus 5 は effort を `low` / `medium` に下げる」としていた。

### 6.3 effort 設定の注意

- **5.5 世代の既定 effort(2026-10-11 追記)**: **Opus 5.5 の既定は `medium`**(API・Claude Code とも)で、Opus 5 の `high` より 1 段低い。公式 model-config は「In Anthropic's testing, Opus 5.5 at `medium` matches or exceeds Opus 5 at `high` on coding and knowledge-work evaluations」とし、Opus 5 から移るときは Opus 5 の値を持ち込まず `medium` から始めるよう求めている。**Haiku 5.5 の既定も `medium`**(API・Claude Code とも)。**Sonnet 5.5 は API の既定が `high`、Claude Code の既定が `medium`** で、公式ソース間で値が違う(§2 ※6)。API 側の公式 Effort は Sonnet 5.5 について「agentic coding と多段の tool use では、仕様が明確なタスクは `medium` から始める」としている。
- **Fable 5.1 / Fable 5 のデフォルト effort は `high`**(Opus 4.8 と同じ)。なお **Haiku 4.5 は effort 非対応**である。(model-default hold については下記の訂正を参照)
- **Opus 5 のデフォルト effort も `high`** で、公式は「**`high` から始め、`low` / `medium` をコスト・レイテンシの主制御として積極的に使う**」ことを推奨する。demanding な coding / agentic タスクで `xhigh`、正当化できる場合のみ `max`。**Opus 4.7 / 4.8 世代の「`xhigh` から始める」という推奨とは逆方向**であり、公式は「旧モデルから effort 設定を引き継いだ場合は、自分の eval で effort sweep をやり直せ」と明記している。Opus 5.5 / Sonnet 5.5 でも、公式は旧モデルの値を持ち込まず effort sweep をやり直すよう求めている。
- **⚠️ effort の解決順(2026-11-01 更新)**: 現行の公式 model-config は、セッションの effort を次の **5 段**で解決し、最初に当てはまったものを使う。
  1. 環境変数 `CLAUDE_CODE_EFFORT_LEVEL`
  2. セッション内で選んだレベル(`/effort`・`/model` picker・Agent SDK の `applyFlagSettings()`)
  3. 起動時の `--effort`
  4. 設定(モデル別の保存値 or `effortLevel` キー)
  5. モデル既定(Opus 5.5 / Sonnet 5.5 / Haiku 5.5 は `medium`、Opus 4.7 は `xhigh`、その他は `high`。組織が organization default model に既定 effort を設定していればそれ)
  - **環境変数は `/effort` より優先される**。skill の `effort` frontmatter はそのスキルが走るターンの終わりまで、subagent の `effort` はその subagent の実行中だけ効くが、`CLAUDE_CODE_EFFORT_LEVEL` が設定されていればそちらが勝つ。`/model` picker で選んだ新しいレベルは「遅くとも次に送るメッセージから」効く。
  - **`CLAUDE_CODE_SUBAGENT_EFFORT`(v2.1.316)**: 他に指定が無いとき subagent が使う effort を決める。従来はセッションの effort を継承していた(CHANGELOG 2.1.316)。
  - (2026-10-11 時点の記述・履歴)公式 model-config は、セッションの effort を **①明示指定（`CLAUDE_CODE_EFFORT_LEVEL` / `--effort` / `/effort`）→ ②設定（モデル別の保存値 or `effortLevel` キー）→ ③モデル既定** の **3 段**で解決するとしていた。
  - CHANGELOG 2.1.280 は「Changed Opus 4.7, Opus 4.8 and Fable 5 to stop holding their launch-default effort over `/effort` in `-p` or the Agent SDK, a project, managed or `--settings` `effortLevel`, or a per-model level」と記録しており、**v2.1.280 で launch-default hold(model-default hold)は止まった**。
  - (v2.1.280 未満の挙動・履歴)2026-09-03 時点では「**hold を持つのは Fable 5 / Opus 4.8 / Opus 4.7 のみ**で、**Opus 5 と Fable 5.1 は持たない**」とし、解決順を ①明示指定 → ②model-default hold → ③設定 → ④モデル既定 の 4 段で書いていた。
  - **v2.1.251 以降、effort は `modelSettings.<model>.effortLevel` にモデルごとに保存される**ため、**モデルを切り替えても旧モデルの値は引き継がれない**。
  - **user settings の top-level `effortLevel` は Opus 5.5 以降のモデルに効かない**。公式 model-config は、この key を per-model 保存より前の旧形式とし、Opus 5 / Fable 5.1 以前のモデルには引き続き効くが、Opus 5.5 とそれ以降のモデルは `/effort` か `/model` で選ぶまで自身の既定で始まるとしている(CHANGELOG 2.1.280 にも同じ変更がある)。project / local / managed settings や `--settings` の top-level `effortLevel` は全モデルに効く。
  - `/effort auto` で当該モデルの保存値をクリアでき、`/effort` 内の `s` キーでセッション限定にできる（v2.1.257）。
  - **fallback 後の effort**: classifier fallback でモデルが切り替わっても、フラグされたリクエストの effort が引き継がれる。公式の例では、既定 `medium` の Opus 5.5 から Opus 4.8 に fallback したセッションは、Opus 4.8 の既定が `high` でも `medium` のまま動く。
  - （旧記述・履歴）以前は「**Opus 5 は以前設定したレベルをそのまま引き継ぐ**ため、旧世代で `xhigh` を設定していると黙って `xhigh` のまま動く」と記載していたが、per-model 保存により誤りになった。
- `xhigh` / `max` を使う場合は `max_tokens` を大きめに取る(公式は 64k 起点を推奨)。Opus 5 は thinking が既定 ON で `max_tokens` が「thinking + response」の合計上限になるため、旧世代の値を流用すると出力が切れる。thinking を切れない Opus 5.5 も同じで、Opus 5.5 migration guide も `xhigh` / `max` では 64k から始めるよう求めている。
- 単純タスクなら `low` / `medium` に落とすことで、Fable 5 / Opus 5 でも weekly limit を大きく節約できる(公式 [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) / [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) が明言)。Opus 5 は **test-time compute scaling の効率が歴代 Opus で最良**とされ、低 effort でも code review の精度が落ちにくい。
- **会話途中の effort 変更（per-message effort、beta）**: beta header `mid-conversation-output-config-2026-07-01` を付けると、**Fable 5.1 / Mythos 5.1 / Opus 5.5 / Opus 5 / Sonnet 5.5 / Haiku 5.5 は prompt cache を壊さずに会話の途中で effort を変更できる**(Claude API と Google Cloud。Amazon Bedrock では Fable 5.1 / Mythos 5.1 / Opus 5.5 のみ。2026-10-11 更新: 以前は対象を Fable 5.1 / Mythos 5.1 / Opus 5 と書いていた)。長時間セッションで「調査は `low`、実装は `xhigh`」と切り替える運用が、キャッシュを捨てずに可能になる。ただし Sonnet 5.5 の `between_tools` と Haiku 5.5 の `disabled` では会話途中に effort を変えられない(400)。
- `ultrathink` キーワード・`ultracode` 設定は Fable 5.1 / Fable 5 / Opus 5 でも同じく機能する(モデル横断)。(v2.1.311 未満の挙動)**`ultrathink` は in-context の指示を足すだけで、API に送る effort は変えない**。
  - **v2.1.311 以降**: ターミナルに打った `ultrathink` は、Anthropic API 上の Opus 5.5 / Sonnet 5.5 / Haiku 5.5 / Fable 5.1 で**そのターンを `xhigh` に上げられる**(上げられるときは虹色で表示される。Claude の作業中に打つと、そのターンの残りを上げる)。セッションの effort 設定は変わらない。v2.1.316 で VS Code の chat box も同じ挙動になり、`CLAUDE_CODE_DISABLE_ULTRATHINK` でキーワード自体を無効化できる。Amazon Bedrock のように上げられない環境や、`CLAUDE_CODE_EFFORT_LEVEL` が `xhigh` 未満・`maxEffortLevel` や組織の上限が `xhigh` 未満の場合は上がらない(公式 [Model configuration](https://code.claude.com/docs/en/model-config#use-ultrathink-for-one-off-deep-reasoning) / CHANGELOG 2.1.311・2.1.316)。

### 6.4 API 利用時の追加要件(参考)

サブスクプランではなく Claude API 経由で Fable 5 を使う場合、以下の対応が必要になる(promotion 対象外・標準レート課金)。2026-10-11 時点で安全分類器を持つモデルは **Fable 5.1 / Fable 5 / Opus 5.5 / Opus 5 / Sonnet 5.5 / Haiku 5.5** に広がっており、いずれにも同じ対応が要る。

- `stop_reason: "refusal"` を成功レスポンスとして受け取る新しい応答形状への対応
- `fallbacks` パラメータ(server-side fallback。2026-11-01 時点の公式は「in beta on the Claude API and on Claude Models on Google Cloud (Anthropic managed)」とする。2026-10-11 時点では「API / Claude Platform on AWS で beta」と書いていた)または SDK middleware / 手動リトライで、別モデルへの fallback ロジック。**Haiku 5.5 には server-side fallback がない**ため、SDK middleware か手動リトライを使う
- **refusal の課金ルール(2026-09-24 改定)**: 出力前の refusal は、`stop_details.category` が **`bio` / `frontier_llm` / `reasoning_extraction` なら通常のリクエストと同じく課金される**。それ以外のカテゴリ(と `null`)の出力前 refusal は課金されない。mid-stream の refusal は、入力とそれまでに出力したトークンが課金される。fallback を使うと、トリガになった refusal(mid-stream か課金カテゴリのもの)と fallback 先のリクエストの両方が課金される。リトライ先モデルの prompt-cache コストは fallback credit で相殺されるが、**Haiku 5.5 の refusal には fallback credit が付かない**。全プラットフォーム共通のルールである
- (2026-09-24 より前の挙動・履歴)以前は「refusal 発生時は課金なし、リトライ先モデルの prompt-cache コストは fallback credit で相殺される」と書いていた。release notes は 2026-09-24 の変更を「resuming billing for refusals that arrive before any output」と記録しており、fallback credit の扱いは変わっていない

詳細は [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) と [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) を参照。

Opus 5 の GA に伴い、API 側では以下も追加された(いずれも Opus 5 と同時)。

| 追加項目 | 内容 |
|---|---|
| **prompt cache 最小長の引き下げ** | 1,024 → **512 トークン**。短いプロンプトでもキャッシュが効く |
| **mid-conversation tool changes(beta)** | beta header `mid-conversation-tool-changes-2026-07-01`。**prompt cache を保ったまま turn 間で tool を追加・削除できる**。MCP サーバーを動的に着脱するエージェントでキャッシュを捨てずに済む。**2026-11-01 追記**: 会話の途中で**ツールの完全な定義**を渡す(追加・schema の変更・server tool の版上げ)には、新しい beta header `inline-tools-2026-09-15` を使う(mid-conversation system message の `tool_addition` block。参照による追加・削除も同じ header で扱える)。旧 header が扱うのは参照による変更だけである |
| **`fallbacks: "default"` モード** | beta header `server-side-fallback-2026-07-01`。fallback 先を明示列挙せずサーバー側の既定に委ねる |

**API version `2026-10-21`(2026-11-01 追記)**: 2026-10-21 に新しい API version が出て、**`temperature` / `top_p` / `top_k` が削除された**。この version で指定すると 400 になる(以前の version でも、Claude 4.7 以降のモデルで既定以外の値を指定すると 400)。同日に出た各 SDK の新しいメジャー版(Python SDK 2.0.0・TypeScript SDK 1.0.0 など)は既定でこの version を送るため、SDK を上げるだけで sampling パラメータを送るコードが壊れる。出典: [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) / [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)

**提供経路: Claude Models on Google Cloud (Anthropic managed) が GA(2026-10-22、2026-11-01 追記)**: Claude API の全機能(beta を含め、ネイティブの Claude Platform と同じ日に出る)を Google Cloud の IAM 認証と請求で使える経路。利用額は Google Cloud の commitment から消化される。Fable 5.1 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 に対応し、Opus 5.5 の fast mode($8 / $40)も使える。Anthropic が運用しデータ処理者になる点が、従来の Google managed 版(Google がデータ処理者)と違い、両者は併存する。Claude Code からこの経路を使えるかは未確認である。出典: [The full Claude Platform, available on Google Cloud](https://claude.com/resources/articles/claude-models-on-google-cloud-anthropic-managed)

### 6.5 fast mode と classifier fallback(Opus 5 で変更)

#### fast mode の対象モデル

**v2.1.219 で `/fast` の対象が変わり、v2.1.280 で既定が Opus 5.5 になった**。

| モデル | fast mode | 料金 | 提供範囲 |
|---|---|---|---|
| **Opus 5.5** | **対応(2026-10-15 に research preview を外れた)**。2026-10-11 時点は research preview | **$8 / $40 per MTok**(1M 全域フラット) | **Claude Code**: Anthropic API とサブスクのみ(Claude Platform on AWS / Bedrock / Google Cloud's Agent Platform / Microsoft Foundry 非対応)。**API**: Claude API に加え Microsoft Foundry(Azure ホスト、2026-10-15〜)と Claude Models on Google Cloud (Anthropic managed)(2026-10-22〜) |
| Opus 5 | 対応(research preview) | $10 / $50 per MTok(1M 全域フラット) | Claude API のみ(Claude Platform on AWS / Bedrock / Google Cloud / Microsoft Foundry 非対応。2026-10-11 更新: Claude Platform on AWS を追記) |
| Opus 4.8 | 対応(research preview)。**2026-10-30 に deprecated、2026-11-30 に削除** | $10 / $50 per MTok | Claude API のみ |
| Opus 4.7 | **API 側では削除済み** | — | 2026-06-25 に deprecated → **2026-07-24 に削除** |

- **fast mode の既定モデルは v2.1.280 以降 Opus 5.5**(v2.1.219〜v2.1.279 は Opus 5、v2.1.154〜v2.1.218 は Opus 4.8、v2.1.142〜v2.1.153 は Opus 4.7)。
- **Opus 5.5 の fast mode は research preview を外れた(2026-11-01 追記)**。API では 2026-10-15 に外れ、access の申請や `fast-mode-2026-02-01` beta header が不要になった(Start / Build / Scale の usage tier に既定の fast mode rate limit が付く)。Claude Code の `/fast` ダイアログからも v2.1.304 で「(research preview)」の表記が外れた。research preview のままなのは Opus 5 / Opus 4.8 で、Console の organization がこの 2 モデルで fast mode を使うには access の provisioning が要る(無いと fast mode の rate limit に当たり標準速度に落ちる)。
- **Opus 4.8 の fast mode は 2026-10-30 に deprecated、2026-11-30 に削除される(2026-11-01 追記)**。削除後、Opus 4.8 への fast mode リクエストは**エラーになり、標準速度の Opus 4.8 へは fallback しない**。移行先は Opus 5.5(CHANGELOG 2.1.316 / API release notes 2026-10-30)。⚠️ Claude Code の公式 Fast mode ページは 2026-11-01 時点で、この廃止をまだ載せていない(CHANGELOG と API release notes の 2 ソースで確認)。
- **Opus 4.7 の扱いは v2.1.221 で正常化された(2026-08-12 更新)**。現行の公式 [Fast mode](https://code.claude.com/docs/en/fast-mode) は「Claude Code treats Opus 4.7 **like any other model without fast mode support: switching to it turns fast mode off**」と記載し、原因も「**before v2.1.221**, fast mode stayed on after a switch to Opus 4.7 and the API rejected the requests」と明示している。**Opus 4.7 へ切り替えると fast mode は自動的に OFF になる**のが現在の挙動である。
  - 2026-08-04 時点では「CHANGELOG は削除済みと言うが公式 fast-mode ページは fast model として扱い続けると書いており、公式内で表現が揺れている」と注記していた。この不整合は **v2.1.221 の修正と公式ページの書き換えで解消済み**のため、警告を削除した。

#### fast mode の課金モデル(本ドキュメントの主題に直結)

**サブスクリプションプランでは、fast mode はプランの使用枠を一切消費せず usage credits から直接引き落とされる**。公式の記述は次の 2 文である。

> For Claude Code users on subscription plans (Pro/Max/Ultra/Team/Enterprise), fast mode is available **via usage credits only and not included in the subscription rate limits**.

(2026-11-01 更新: 原文のプラン列挙に Ultra が加わった。2026-10-11 時点の原文は「Pro/Max/Team/Enterprise」)

> **Fast mode usage draws directly from usage credits, even if you have remaining usage on your plan.** This means fast mode tokens do not count against your plan's included usage and are charged at the fast mode rate **from the first token**.

| 論点 | 内容 |
|---|---|
| **プラン枠との関係** | 消費しない。**プランに使用量が残っていても credits 側から課金される**。「weekly limit を節約するために fast mode を使う」は成立しない（逆に実費が出る） |
| **初回有効化のコスト** | fast mode を ON にした時点で、**その会話のコンテキスト全体の uncached input を fast 料金で支払う**。深い会話の途中で ON にすると高額になる。この課金は 1 会話につき 1 回のみ |
| **rate limit の共有** | (2026-10-11 時点の記述)**対応する全 Opus モデルが 1 つの fast mode rate limit プールを共有**する。Opus 5.5 / Opus 5 / Opus 4.8 を使い分けても限度は分かれない。**2026-11-01 時点の公式 Fast mode ページでは、この記述の裏が取れない(未確認)**。現行ページは「Fast mode has separate rate limits from standard Opus」とだけ書き、モデル間でプールを共有するかには触れていない |
| **Team / Enterprise** | **既定で無効**。Owner が明示的に有効化する必要がある |
| **無効化・回避** | `CLAUDE_CODE_DISABLE_FAST_MODE=1` で完全に無効化。設定キーは `fastMode` / `fastModePerSessionOptIn` |
| **LLM gateway 配下の既知問題** | `/fast` が「network connectivity issues」になる場合、`CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1`（接続が拒否される / gateway 資格情報が reject される場合）または `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1`（ネットワークがリクエストを傍受する場合）で回避する |

> **v2.1.221 以降、セッション途中で usage credits が尽きた場合はストリーム上に報告される**(それ以前は silent failure だった)。fast mode を常用する場合はこの版以降が実用的である。

#### 安全分類器の fallback がカテゴリ別になった

**v2.1.219 以降、fallback 先がフラグのカテゴリごとに分岐する**。それ以前は「フラグされた Fable 5 リクエストは一律で provider 既定の Opus に再実行」であり、Opus 5 は fallback 先ではなかった。

| 元のモデル | フラグのカテゴリ | fallback 先 |
|---|---|---|
| **Fable 5.1** | biology | **Opus 5** で再実行 |
| **Fable 5.1** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5.5** | biology | **Opus 5** で再実行 |
| **Opus 5.5** | cybersecurity | **Opus 4.8** で再実行 |
| **Sonnet 5.5** | cybersecurity | **Sonnet 5** で再実行 |
| **Sonnet 5.5** | biology | **fallback なし。refusal で確定終了** |
| **Fable 5** | biology | **Opus 5** で再実行 |
| **Fable 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | biology | **fallback なし。refusal で確定終了** |

> **2026-10-11 追記**: 公式 model-config の対象は「Fable models, Opus 5.5, Sonnet 5.5, and Opus 5」に広がり、Fable 5.1 / Opus 5.5 / Sonnet 5.5 の行を足した。Sonnet 5.5 は Sonnet として初めて cyber safeguard と fallback を持つモデルで、biology には fallback 先がない。Haiku 5.5 も安全分類器を持つが、Claude Code の automatic model fallback の対象には挙がっておらず、API でも server-side fallback がない(§6.4)。fallback 先が `availableModels` で除外されている場合は fallback せず refusal で終わる。fallback 後の effort の扱いは §6.3 を参照。
>
> **2026-11-01 追記(v2.1.312〜v2.1.316 の変更)**:
>
> - **v2.1.312**: 自動の切り替えが、Claude Code が認識できないモデル名(カスタム deployment 名など)にも及ぶようになった。**`CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1` で自動の切り替えそのものを止められる**(`switchModelsOnFlag` が制御する挙動を切る。公式 env-vars)。
> - **初回の確認**: `switchModelsOnFlag` を設定していない場合、対話セッションで初めて切り替えが起きるときに「以後は自動で切り替えるか」を尋ね、答えを user settings の `switchModelsOnFlag` に保存する(公式 model-config)。
> - **1 ターン限りの effort**: `ultrathink` や skill の `effort` frontmatter で上げたターンが fallback した場合、そのレベルはそのターンだけに効き、以降のターンは fallback 先のモデルに対する通常の解決順(§6.3)で決まる。
> - ⚠️ **公式ソース間の食い違い(`availableModels` で fallback 先が塞がれたとき)**: 公式 [Model configuration](https://code.claude.com/docs/en/model-config#automatic-model-fallback) は 2026-11-01 時点でも「The fallback model is checked against `availableModels`. When it is blocked, no fallback occurs.」と書く。一方 **CHANGELOG 2.1.314** は「Changed flagged requests to retry on another model, not end in a refusal, when `ANTHROPIC_DEFAULT_OPUS_MODEL`, `availableModels` or `deniedModels` leaves only an older Opus model, or none」と書く。CHANGELOG の方が新しいが、どのモデルで retry するかを docs ページが書いていないため、**本ドキュメントでは両論を併記し、docs ページが更新されるまで断定しない**。上の「fallback せず refusal で終わる」は model-config に基づく記述であり、v2.1.314 以降は CHANGELOG のとおり別モデルで retry する可能性がある。
>
> **実務上の注意**: Opus 5 は自身が biology classifier を持つため、生物・化学系のワークロードでは **fallback による救済がなく作業が止まる**。Sonnet 5.5 も同じである。該当領域を扱う場合は最初から別モデル(Mythos の適格者、Life Sciences Verification Program の検証済み組織、または明示的に Opus 4.8)を選ぶ。カテゴリ別 fallback は **v2.1.219 以上が必須**で、それ未満のバージョンでは旧来の一律 fallback として動作する。

##### Fable 5 の biology 分類器が改善され、fallback の発生頻度が下がった(2026-08-07)

Anthropic は 2026-08-07 に **Fable 5 の biology 安全分類器の false positive を約 85% 削減**したと発表した。

| 論点 | 内容 |
|---|---|
| **効果** | 製品サーフェス横断で **fallback(Fable 5 → Opus 5 への降格)が 7〜67% 減少**する見込み |
| **変わらないもの** | **上表の fallback の仕組み自体は不変**。発火する頻度だけが下がる。課金ルール(当時は refusal 時 input 非課金 / fallback は cache-read 10% レート)も、この発表では変わらなかった。(2026-10-11 追記: その後 2026-09-24 に、出力前の refusal のうち `bio` / `frontier_llm` / `reasoning_extraction` カテゴリが課金対象に戻った。§6.4) |
| **引き続きブロックされるもの** | dual-use の professional biology / 創薬系のワークロード |
| **可用性・料金** | 変更なし |

> 「Fable 5 を使うと生物系の話題で頻繁に降格する」という運用上の摩擦は軽減されたが、**降格しうる前提そのものは残る**ため、該当領域での設計方針(§6.5 冒頭)は変更しない。
>
> 出典: [Improving Fable 5's biology safeguards](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards)

##### 検証プログラムで safeguard を緩められる(LSVP 2026-09-17 / CVP 2026-10-06)

5.5 世代は safeguard が強まった一方、検証済みの組織向けに緩和された safeguard を提供する 2 つのプログラムが整った。

| プログラム | 対象 | 内容 |
|---|---|---|
| **Life Sciences Verification Program(LSVP)** | 研究資格・セキュリティ基準・倫理審査の検証を通った life science 組織(大学の研究室・スタートアップ・製薬など) | Mythos / Opus / Sonnet 系モデルを、biology 作業に寛容な safeguard で使える。チーム単位の **Standard Use** と、プロジェクト単位の **High-risk Use**(life sciences の block を外す。6 か月ごとに更新)の 2 種類の grant がある。cyber など他の safeguard は残る。Opus 5.5 のアナウンスは、Opus 5.5 を biology 研究に使う組織に LSVP への申請を案内している |
| **Cyber Verification Program(CVP)** | 防御・red team などのセキュリティ組織 | **Defense Access / Red Team Access / Specialized Access の 3 tier** に再編され、各 tier で Opus 5.5 / Sonnet 5.5 / Mythos 5.1 などを cyber の block を減らして使える。公式は一般提供モデル(Opus 5.5 / Fable 5.1 / Sonnet 5.5)の cyber safeguard を「block most cyber work」と説明する。参加組織にはデータ保持が求められる。Project Glasswing の参加組織は Specialized Access に移る |

出典: [Introducing the Life Sciences Verification Program](https://www.anthropic.com/news/life-sciences-verification-program) / [Expanding the Cyber Verification Program](https://www.anthropic.com/news/cyber-verification-program) / [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5)

#### claude.ai(Claude アプリ)側にも別レイヤの自動フォールバックがある

上表は **ClaudeCode / API レイヤ**の挙動である。これとは別に、**claude.ai の会話では Opus 5 が分類器にフラグされた際 Opus 4.8 へ自動で切り替わり、以降その会話は下位モデルのまま固定される**。

- 気付かないうちに「Opus 5 で始めた会話が Opus 4.8 で続いている」状態になり得る
- **Settings > Capabilities の「Switch models when a message is flagged」で無効化できる**
- ClaudeCode の classifier fallback（上表）とは別レイヤの機能である。**2026-10-11 訂正**: 以前は「発生条件も切替先の固定挙動も異なる」と書いていたが、現行の公式 model-config では Claude Code も fallback 後はセッションが fallback 先のモデルのまま続く(元に戻すには `/model`)。Claude Code 側でも `/config` の「Switch models when a message is flagged」を「Ask each time」にするか、`switchModelsOnFlag` を `false` にすると、切り替える前に確認を挟める。フラグの原因が CLAUDE.md・skills・MCP などのカスタマイズかを切り分けるには `claude --safe-mode` で起動する
- 出典: [Why Claude switched models in your conversation with Opus 5](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5)

#### v2.1.221 で修正された Opus 5 の thinking 周辺の不具合

Opus 5 は thinking が既定 ON で、無効化できるのは effort `high` 以下のみという制約がある（§3.3 参照）。この周辺で **v2.1.220 以前に踏みやすかった不具合が 2 件修正された**。

| 修正内容 | v2.1.220 以前の症状 |
|---|---|
| thinking off で開始したセッションで、以降 thinking トグルが無効だった | 一度 thinking を切って始めると、そのセッションでは戻せなかった |
| **`WebSearch` が effort `xhigh` / `max` かつ thinking 無効時に 400 エラーで失敗**していた | 高 effort + thinking 無効の組み合わせで web 検索が使えなかった |

出典: [Model configuration](https://code.claude.com/docs/en/model-config) / [Fast mode](https://code.claude.com/docs/en/fast-mode) / CHANGELOG v2.1.219 / v2.1.221

---

## 7. 既存ドキュメントとの関係

- 本ドキュメントは `docs/best-practices.md` §8 の世代別章(「Opus 4.7 を活用する」→ Opus 4.8 → Fable 5 / Mythos 5 → Sonnet 5 → Opus 5 → **Opus 5.5 / Sonnet 5.5 / Haiku 5.5**)の補足として、**課金・プラン制限側面**を切り出したもの。各世代のプロンプト作法・ハーネス設計への影響は best-practices.md §8 側で扱う。
- `docs/harness.md` 4.6 節「モデル世代によるハーネス進化」は **Opus 5.5 / Sonnet 5.5 / Haiku 5.5 まで反映済み**(2026-10-11)。Opus 5 は「検証ステップをハーネスから外す方向の世代」として整理されており、5.5 世代はその方向を引き継いだうえで、テキストだけで終わるターンへの対処や effort の起点 (`medium`) などを補足している。
- **3 社横断の API 料金比較は [docs/llm-api-pricing-comparison.md](llm-api-pricing-comparison.md) が正**。本ドキュメントは Claude 専用かつ**サブスクプランの消費**が主題であり、OpenAI / Google を含む API 単価・キャッシュ / Batch 割引・長コンテキスト割増・画像トークン換算式は同ドキュメントを参照する。
- **Opus 5 のプラン別 weekly limit 消費速度は未確認**。Fable 5 のような専用 support 記事が存在せず、[Models, usage, and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code) も Opus 5 を名指ししていない。「Opus は quota を meaningfully more 消費する」以上の定量情報は公式にないため、本ドキュメントでは倍率を断定しない。

---

## 出典

- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/models/overview)(2026-11-01 確認)
- [Claude Opus 5 — platform.claude.com](https://platform.claude.com/docs/en/models/opus-5/overview)(2026-11-01 確認。旧 What's new in Claude Opus 5 ページの移転先)
- [Thinking — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/thinking)(2026-11-01 確認。Opus 5 の thinking 破壊的変更の現行出典)
- [Introducing Claude Opus 5 — anthropic.com](https://www.anthropic.com/news/claude-opus-5)(2026-07-24)
- [Migration guides — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/migration-guide)(2026-11-01 確認: モデル別ガイドへの索引ページになった)
- [Claude Opus 5.5 migration guide — platform.claude.com](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)(2026-11-01 確認)
- [Claude Sonnet 5.5 migration guide — platform.claude.com](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide)(2026-11-01 確認。Sonnet 5 / 5.5 の tokenizer +30% の現行出典)
- [Claude Haiku 5.5 migration guide — platform.claude.com](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide)(2026-11-01 確認)
- [Claude Sonnet 5 — platform.claude.com](https://platform.claude.com/docs/en/models/sonnet-5/overview)(2026-11-01 確認。旧 What's new in Claude Sonnet 5 ページの移転先)
- [Introducing Claude Opus 5.5 — anthropic.com](https://www.anthropic.com/claude-opus-5-5)(2026-09-22)
- [Introducing Claude Sonnet 5.5 — anthropic.com](https://www.anthropic.com/claude-sonnet-5-5)(2026-09-28)
- [Introducing Claude Haiku 5.5 — anthropic.com](https://www.anthropic.com/claude-haiku-5-5)(2026-10-07)
- [Pricing — platform.claude.com](https://platform.claude.com/docs/en/about-claude/pricing)(2026-11-01 確認)
- [Model deprecations — platform.claude.com](https://platform.claude.com/docs/en/about-claude/model-deprecations)(2026-11-01 確認)
- [Claude Platform release notes — platform.claude.com](https://platform.claude.com/docs/en/release-notes/overview)(2026-11-01 確認)
- [Effort — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/effort)(2026-11-01 確認)
- [Prompting Claude Opus 5 — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)(2026-07-26 確認)
- [Model configuration — code.claude.com](https://code.claude.com/docs/en/model-config)(2026-11-01 確認)
- [Fast mode — code.claude.com](https://code.claude.com/docs/en/fast-mode)(2026-11-01 確認)
- [Claude Code changelog — code.claude.com](https://code.claude.com/docs/en/changelog)(2026-11-01 確認)
- [Claude Fable 5 — platform.claude.com](https://platform.claude.com/docs/en/models/fable-5/overview)(2026-11-01 確認。旧 Introducing Claude Fable 5 and Claude Mythos 5 ページの移転先)
- [Refusals and fallback — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback)(2026-11-01 確認。fallback と refusal 課金の現行出典)
- [Fallback credit — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/fallback-credit)
- [Claude Fable 5 promotional access — support.claude.com](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)(**2026-07-26 確認: 07-19 終了**)
- [Prompting Claude Fable 5 — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Manage usage credits for paid Claude plans — support.claude.com](https://support.claude.com/en/articles/12429409)
- [API credits for Max, Ultra, and Team plans — platform.claude.com](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)(2026-11-01 確認。2026-10-11 時点のページ名は「API credits for Max and Team plans」)
- [What's new in Claude Fable 5.1 — platform.claude.com](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1)(2026-11-01 確認)
- [Introducing the Life Sciences Verification Program — anthropic.com](https://www.anthropic.com/news/life-sciences-verification-program)(2026-09-17)
- [Expanding the Cyber Verification Program — anthropic.com](https://www.anthropic.com/news/cyber-verification-program)(2026-10-06)
- [Claude for Government is now generally available — claude.com](https://claude.com/resources/articles/claude-for-government-is-now-generally-available)(2026-09-30)
- [Claude text watermark — anthropic.com](https://www.anthropic.com/news/claude-text-watermark)(2026-08-14 公開)
- [Redeploying Fable 5 and Mythos 5 の前段: Fable 5 / Mythos 5 access — anthropic.com](https://www.anthropic.com/news/fable-mythos-access)(2026-06-12 公開)
- [Claude pricing — claude.com](https://claude.com/pricing)(2026-11-01 確認。Max / Ultra の構成)
- [What is the Ultra plan? — support.claude.com](https://support.claude.com/en/articles/17728952-what-is-the-ultra-plan)(2026-11-01 確認)
- [Unified Claude Enterprise — claude.com](https://claude.com/resources/articles/unified-claude-enterprise)(2026-11-01 確認。Max / Ultra 改称日の編集注記)
- [Introducing Claude Duet — claude.com](https://claude.com/resources/articles/claude-duet)(2026-10-21)
- [Claude Duet Safety, Privacy, and Security — claude.com](https://claude.com/resources/articles/claude-duet-safety-privacy-and-security)(2026-10-23)
- [The full Claude Platform, available on Google Cloud — claude.com](https://claude.com/resources/articles/claude-models-on-google-cloud-anthropic-managed)(2026-10-22)
- [Manage costs and demonstrate ROI for Claude Code on Google Cloud — claude.com](https://claude.com/resources/articles/how-to-manage-costs-and-demonstrate-roi-for-claude-code-on-google-cloud)(2026-10-27)
- [Smart reports, surveys, and pooled group budgets for Claude Enterprise — claude.com](https://claude.com/resources/articles/smart-reports-surveys-pooled-budgets)(2026-10-28)
- [Expanding Claude for Nonprofits — claude.com](https://claude.com/resources/articles/expanding-claude-for-nonprofits)(2026-10-26)
- [Strengthening our defenses against distillation attacks — anthropic.com](https://www.anthropic.com/news/distillation-defenses)(2026-10-12)
- [Claude Mythos 5.1 — platform.claude.com](https://platform.claude.com/docs/en/models/mythos-5-1/overview)(2026-11-01 確認。verification programs で検証された組織のみ)
- [Environment variables — code.claude.com](https://code.claude.com/docs/en/env-vars)(2026-11-01 確認。`CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK`)
- 関連: `docs/best-practices.md` / `docs/harness.md` / `docs/config-files.md`
