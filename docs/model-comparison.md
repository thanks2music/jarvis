# Claude モデル別トークン消費とプラン制限

> 出典:
> - [Models overview (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/overview) — 現行モデルの ID / pricing / context / thinking / tokenizer
> - [What's new in Claude Opus 5 (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5) — Opus 5 の仕様と Opus 4.8 からの破壊的変更
> - [Introducing Claude Opus 5 (anthropic.com)](https://www.anthropic.com/news/claude-opus-5) — Opus 5 リリースアナウンス(2026-07-24)
> - [Introducing Claude Fable 5 and Claude Mythos 5 (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — Fable 5 / Mythos 5 の API 仕様と課金ルール
> - [Claude Fable 5 promotional access (support.claude.com)](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access) — サブスクプラン上でのプロモーショナルアクセス(**2026-07-01 〜 07-19 23:59:59 PT で終了済み**)
> - [Model configuration (code.claude.com)](https://code.claude.com/docs/en/model-config) — Claude Code のエイリアス解決 / effort 既定 / classifier fallback
> - [Effort (platform.claude.com)](https://platform.claude.com/docs/en/build-with-claude/effort) — モデル別の effort 推奨
> - [Migration guide (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/migration-guide) — **Opus 5 の tokenizer 世代**(Opus 4.7 系、1x〜1.35x)
> - [Fast mode (code.claude.com)](https://code.claude.com/docs/en/fast-mode) — fast mode の課金モデル(usage credits 直課金)
> - [Why Claude switched models in your conversation with Opus 5 (support.claude.com)](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5) — claude.ai 側の自動フォールバック
>
> 最終更新: 2026-08-04

**Claude Opus 5 の GA(2026-07-24)** を反映し、Fable 5 / Opus 5 / Sonnet 5 / Haiku 4.5 の **消費トークン特性** と **サブスクプランの weekly limit がどう減るか** を、公式一次情報のみに基づいて整理する。Claude Code / claude.ai の Pro / Max / Team ユーザーが「どのモデルをどこで使うか」を判断するための資料。

> 本ドキュメントは公式が数値で明示している事実のみを扱う。「Fable 5 は 2 倍速く減る」といった倍率の断定は、公式が明示していないため行わない。

---

## 1. TL;DR

- **Claude Opus 5 (`claude-opus-5`) が 2026-07-24 に GA**。**$5 / $25 per MTok**(Opus 4.8 と同額)で、`opus` / `default` エイリアスの解決先が Opus 5 になった。**Claude Code は v2.1.219 以上が必須**。
- Fable 5 の API 料金は **$10 / $50 per MTok**。Opus 5 / Opus 4.8 (**$5 / $25**) の 2 倍、Sonnet 5 (**$3 / $15**) の約 3.3 倍、Haiku 4.5 (**$1 / $5**) の 10 倍。
- Fable 5 の tokenizer は Opus 4.7 と同じ世代。**Opus 4.7 より前のモデルと比べ、同じテキストが約 30% 多くトークン化される**(公式 tooltip 明記)。旧世代 tokenizer は Opus 4.6 系・Sonnet 4.5 以前・Haiku 4.5 が該当。
- **Opus 5 は thinking が既定 ON**(Opus 4.8 からの破壊的変更)。加えて **effort `xhigh` / `max` では thinking を無効化できない**(400 エラー)。思考トークンが常に乗る前提でコストを見積もる必要がある。
- **Fable 5 のプロモは 2026-07-19 23:59:59 PT で終了済み**。終了後は **Max / Team premium seat のみ weekly limit の 50% まで追加費用なしで継続**、**Pro / Team standard seat は usage credits が必要**になった(§5.3)。
- Fable 5 は「Fable 5 draws from your plan's regular weekly usage limit and **uses it faster than other Claude models**」と公式が明記。倍率は非公開だが、原因は① per-token 料金が高い、② tokenizer が Opus 4.7 世代、③ Adaptive thinking が always on の 3 点。
- Claude Code で Fable 5 を使うには **v2.1.170 以上**が必須。
- API 経由は promotion の対象外で、常時**標準の API レートで課金**される。

---

## 2. 現行モデル一覧(2026-07-26 時点)

**2026-07-24 の Opus 5 GA に伴い、公式 Models overview では Opus 4.8 / 4.7 が Legacy models アコーディオンへ移動した**。本表もそれに合わせ、Opus 5 を現行列に、Opus 4.8 を Legacy 側に移している(Opus 4.8 の記述自体は履歴として下の Legacy 注記に保全する)。

| 項目 | Claude Fable 5 | Claude Opus 5 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **API ID** | `claude-fable-5` | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` |
| **Claude API alias** | `claude-fable-5` | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5` |
| **位置づけ** | Next-generation intelligence for long-running agents | Complex agentic coding and enterprise work(公式の第一候補) | Best combination of speed and intelligence | Fastest model with near-frontier intelligence |
| **入力料金** | **$10** / MTok | $5 / MTok | $3 / MTok ※1 | $1 / MTok |
| **出力料金** | **$50** / MTok | $25 / MTok | $15 / MTok ※1 | $5 / MTok |
| **Context window** | **1M tokens** | **1M tokens(既定かつ最大。小さい context variant なし)** | 1M tokens | 200k tokens |
| **Max output(Messages API 同期)** | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **Max output(Batch API、`output-300k-2026-03-24` beta)** | — ※2 | 300k tokens | 300k tokens | — ※2 |
| **Extended thinking** | No | No | No | **Yes** |
| **Adaptive thinking** | **Yes (always on)** | **Yes(既定 ON)** ※3 | Yes | No |
| **Comparative latency** | Slower | Moderate | Fast | Fastest |
| **Reliable knowledge cutoff** | Jan 2026 | **May 2026** | Jan 2026 | Feb 2025 |
| **Data retention** | 30-day、**ZDR 非対応**(Covered Model) | 通常設定に従う ※4 | 通常設定に従う | 通常設定に従う |
| **Claude Code 最低バージョン** | v2.1.170 | **v2.1.219** | v2.1.197 | — |

※1: Sonnet 5 は **2026-08-31 まで introductory 価格 $2 / $10 per MTok** が適用される。9/1 以降は表の $3 / $15 に戻る。**2026-08-04 時点で公式 overview の脚注に変更はなく、終了まで 1 ヶ月未満**である(「$2 / $10 per MTok applies to Claude Sonnet 5 **through August 31, 2026**」)。Sonnet 5 を主力にしたコスト見積もりは、9 月以降 **入力 1.5 倍・出力 1.5 倍**になる前提で組み直す必要がある。
※2: 公式 note で 300k output beta の対象として明記されているのは **Opus 5** / Opus 4.8 / 4.7 / 4.6・Sonnet 5 / 4.6。Fable 5 / Haiku 4.5 は対象外。
※3: Opus 4.8 からの**破壊的変更**。詳細は §3.3。
※4: Opus 5 は **Web fetch 非対応 / Priority Tier 非対応**。ZDR 非対応(Covered Model)の明記は公式にないため、Fable 5 と異なり通常設定に従うものとして扱う。

> **Legacy(現行と併売中)**: **Opus 4.8 ($5 / $25、1M、Adaptive Yes / Extended No、knowledge cutoff Jan 2026 — Opus 5 GA 前の既定 Opus)**、Opus 4.7 ($5 / $25、1M、Adaptive Yes / Extended No)、Opus 4.6 ($5 / $25、1M)、Sonnet 4.6 ($3 / $15、1M)、Sonnet 4.5・Opus 4.5 (200k)。**Opus 4.1 は既に deprecated 済みで、2026-08-05 が retirement 日**(移行先は Opus 5)。Opus 5 の tentative retirement は **2027-07-24 以降**。

> **Opus 4.1 の retirement 状況(2026-08-04 確認)**: `claude-opus-4-1-20250805` は依然 **Deprecated のまま retirement 未実行**で、tentative date も **2026-08-05 で据え置き**である。
>
> ⚠️ **移行先の表記に公式内で揺れがある**: [model-deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) の履歴表は代替を **`claude-opus-4-8`** としているのに対し、[models overview](https://platform.claude.com/docs/en/about-claude/models/overview) の Warning は **「Opus 5 へ移行せよ」**と記載している。**実務上は最新の Opus 5 を選べば問題ない**（4.8 も併売中なので誤りではなく、記述の更新ラグと判断できる）。
>
> ⚠️ **「Legacy」と「Deprecated」は別軸である**: overview の "Legacy models" アコーディオンには Opus 4.8 / 4.7 / 4.6 / 4.5 / Sonnet 4.6 / 4.5 が入っているが、deprecations ページの表では**同じモデルが Active** である。前者は「推奨世代かどうか」の表示区分、後者は「ライフサイクル上の状態」であり、**Legacy = 廃止予定ではない**。混同すると「Opus 4.8 はもう使えない」と誤読するため注意する。

### 2.1 モデル ID とエイリアス

- **バージョン付き ID**(例: `claude-opus-5`)は pinned snapshot。バージョンレスなエイリアス的表記でも同じ snapshot を指す(Claude 4.6 世代以降は dateless format も pinned snapshot 扱い)。
- Claude Code の `/model` メニューには、Fable 5 導入と同時に **`fable`(= Fable 5)** と **`best`**(組織にアクセスがあれば Fable 5、なければ最新 Opus)というエイリアスが追加されている(要 v2.1.170 以上)。v2.1.219 では merged Opus 行の表示が「Opus (1M context)」に変わり、最新モデル名のみがハイライトされる。
- `opus` / `sonnet` / `haiku` エイリアスの解決先は **プロバイダ依存**。**v2.1.219 以降、`opus` は Anthropic API / Claude Platform on AWS / Bedrock / Google Cloud すべてで Opus 5 に解決される**(それ以前は Opus 4.8)。**プロバイダ別解決表は `docs/best-practices.md` の「model alias のプロバイダ別解決」を参照**。
- **`default` の解決先はアカウント種別で分岐する**(v2.1.219 以降):

| アカウント種別 | `default` の解決先 |
|---|---|
| Max / Team Premium / Enterprise pay-as-you-go / Anthropic API | **Opus 5** |
| Claude Platform on AWS / Bedrock / Google Cloud | **Opus 5** |
| Pro / Team Standard / Enterprise subscription seat | **Sonnet 5** |
| Microsoft Foundry | Sonnet 4.5 |

> Fable 5 は**どのアカウント種別でも `default` にならない**。使う場合は `/model fable` または `/model best` で明示的に選択する。

---

## 3. トークン消費を決める 3 つの軸

「Fable 5 は他モデルより速くプラン枠を消費する」という公式表現の内訳を、事実として確認できる 3 つの軸に分解する。

### 3.1 per-token API 料金

| モデル | 入力 | 出力 | Opus 基準の倍率(入力) | Opus 基準の倍率(出力) |
|---|---|---|---|---|
| Fable 5 | $10 | $50 | **2.0x** | **2.0x** |
| **Opus 5** | **$5** | **$25** | **1.0x** | **1.0x** |
| Opus 4.8 (legacy) | $5 | $25 | 1.0x | 1.0x |
| Sonnet 5(通常) | $3 | $15 | 0.6x | 0.6x |
| Sonnet 5(〜 8/31) | $2 | $10 | 0.4x | 0.4x |
| Haiku 4.5 | $1 | $5 | 0.2x | 0.2x |

> **Opus 5 は Opus 4.8 と同額**($5 / $25)であるため、世代交代による per-token 料金の上昇はない。倍率の基準は据え置きで比較できる。

API 経由(pay-as-you-go)では、この料金差がそのままドル単価に反映される。サブスクプランの weekly limit もこの料金体系をベースに設計されているため、**同じトークン数を消費した場合、Fable 5 は Sonnet 5 の 3〜5 倍、Haiku 4.5 の 10 倍のペースで枠が減る**と推測できる(公式は正確な倍率を明示していない)。

**fast mode の料金は別体系**である。Opus 5 / Opus 4.8 の fast mode はいずれも **$10 / $50 per MTok**(通常の 2 倍の価格で約 2.5 倍の速度)で、1M context の全域にフラット適用される。**Opus 5 の fast mode は Claude API のみ**で、Bedrock / Google Cloud / Microsoft Foundry では利用できない(research preview)。詳細は §6.5。

### 3.2 tokenizer 世代差(Opus 4.7 以降で 約 30% 増)

公式は Fable 5 の context window(1M tokens)の tooltip で次を明記している。

> Claude Fable 5 uses the tokenizer introduced with Claude Opus 4.7; compared to models before Claude Opus 4.7, the same text produces roughly 30% more tokens.

| Tokenizer 世代 | 対象モデル | 同一テキストのトークン数 |
|---|---|---|
| Opus 4.7 世代(新) | **Opus 5** / Fable 5 / Mythos 5 / **Opus 4.8** / Opus 4.7 | 基準 |
| Opus 4.6 以前世代(旧) | Opus 4.6 / Sonnet 4.6 / Sonnet 4.5 / Opus 4.5 / Opus 4.1 / **Haiku 4.5** | 約 30% 少ない |

Sonnet 5 は tooltip での言及が「~555k words / ~2.5M unicode characters」と Fable 5 / Opus 4.8 と同じ文言のため、新 tokenizer の可能性が高いが、公式は Sonnet 5 について tokenizer 世代を明示していない。**Sonnet 5 は依然として tokenizer 世代が明示されていない**。

> **Opus 5 の tokenizer 世代が確定した(2026-08-04 更新)**: 2026-07-26 時点では「公式の明示がない(未確認)」としていたが、公式 [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) が次のように明記していることを確認した。
>
> > **Claude Opus 4.7 introduced a new tokenizer, which later Opus models, including Claude Opus 5, also use.** … it may use roughly **1x to 1.35x** as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content).
>
> つまり **Opus 5 は Opus 4.7 世代の tokenizer を継承**しており、Opus 4.7 / 4.8 / Opus 5 / Fable 5 / Mythos 5 はすべて同一 tokenizer である。増加率は Fable 5 の tooltip が言う「約 30%」より幅を持たせた **1x 〜 1.35x(最大 ~35%、内容によって変動)** が公式の表現である。
>
> **実務上の含意**: 旧世代から Opus 5 に移す際は ① `max_tokens` の再調整 ② compaction トリガ閾値の再調整 ③ クライアント側トークン推定ロジックの再テスト が公式に推奨されている。
>
> なお **prompt cache の最小長は Opus 5 で 1,024 → 512 トークンに引き下げられた**(Opus 4.8 は 1,024)ため、短いプロンプトでもキャッシュが効くようになり、実効コストはこの分だけ下がる余地がある。

### 3.3 Adaptive thinking / Extended thinking

| モデル | Extended thinking | Adaptive thinking | 意味 |
|---|---|---|---|
| Fable 5 / Mythos 5 | No | **Yes (always on)** | `thinking` パラメータを disabled にできない。effort で深さを制御 |
| **Opus 5** | No | **Yes(既定 ON)** | `thinking` 未指定でも adaptive thinking が走る。無効化は effort `high` 以下でのみ可能 |
| Opus 4.8 (legacy) | No | Yes | `thinking` 未指定なら thinking なしで実行 |
| Sonnet 5 | No | Yes | 同上 |
| Haiku 4.5 | **Yes** | No | Extended thinking を有効化して思考時間を確保できる。Adaptive はなし |

Fable 5 は **Adaptive thinking を無効化できない**設計のため、単純なタスクでも一定の思考トークンが生成される可能性が高い。これも「速く枠を消費する」要因の 1 つになる。

#### Opus 5 における thinking の破壊的変更(2 点)

Opus 4.8 から移行する際、以下 2 点は **API リクエストの書き換えが必要**になる。

| # | 変更点 | Opus 4.8 | **Opus 5** |
|---|---|---|---|
| 1 | **thinking の既定** | `thinking` 未指定なら thinking なしで実行 | **未指定で adaptive thinking が走る**。`max_tokens` は「thinking + response」合計に対する hard limit なので再調整が必要 |
| 2 | **thinking 無効化の可否** | effort と独立に無効化可 | **effort `high` 以下でのみ無効化可**。`thinking:{"type":"disabled"}` × effort `xhigh` / `max` は **400 エラー** |

> **thinking を無効化する場合の注意**: 公式は thinking 無効時の既知アーティファクトとして「tool call が構造化された `tool_use` ではなくテキストとして漏れる」「`<thinking>` 等の内部 XML タグが可視出力に混入する」を挙げている。**回避策は thinking を有効に保ったまま effort を下げること**であり、公式は「thinking ON + `low` effort は thinking OFF と同程度のコストでより高性能」と明言している。コスト削減目的で thinking を切るのは Opus 5 では逆効果になりやすい。

出典: [What's new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5) / [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) / [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

---

## 4. サブスクプランでの weekly limit の消費速度

Claude Code / claude.ai の Pro / Max / Team は「週次の使用制限」で運用される。**Fable 5 の promotion は API ではなくこのサブスクプラン層に対する施策**である点に注意。

### 4.1 公式が明言していること

- **Fable 5 draws from your plan's regular weekly usage limit** and **uses it faster than other Claude models**.(サポート記事)
- promotion 期間中に **Fable 5 に振り分けられる上限は weekly limit の 50%**。追加課金なし。
- **promotion 終了後(2026-07-19 以降)の扱いはプランで分岐する**。Max / Team premium seat は **50% 枠が標準機能として継続**、Pro / Team standard seat は **weekly limit の対象外となり usage credits が必要**になった(詳細は §5.3)。

### 4.2 「速く消費する」の内訳(推測)

公式は倍率を明示していないが、§3 の 3 つの軸を組み合わせると次のように分解できる。

```
Fable 5 の 1 リクエスト当たりの weekly-limit 消費量 ≒
   トークン数(tokenizer 世代差で +30%)
 × 単価係数(Opus 4.8 の 2 倍相当)
 × 思考量(Adaptive thinking always on による思考トークン増)
```

Sonnet 5 と比べれば、単価差だけで **入力 3.3 倍・出力 3.3 倍** の消費速度差が生じる。ここに tokenizer と思考トークンが加わるため、公式が「uses it faster」と一言で片付けているのは妥当である。

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
| **usage credits で継続** | Fable 5 の追加使用は usage credits(サブスク外の別課金)から自動的に引き落とし。usage credits を有効化していれば billing が自動で切り替わる |
| **他モデルに切替** | 残っている weekly limit の範囲内で Opus 4.8 / Sonnet 5 / Haiku 4.5 を継続利用 |

usage credits の管理は [Manage usage credits for paid Claude plans](https://support.claude.com/en/articles/12429409) 参照。

---

## 5. Fable 5 プロモーショナルアクセス(2026-07-01 〜 07-19、**終了済み**)

> **2026-07-26 時点で本プロモは終了している**。公式 support 記事は「that promotion **ends on July 19, 2026 at 11:59:59 PM PT**」と過去形で記載しており、**最終的な終了日は 2026-07-19 23:59:59 PT**(当初 07-07 → 07-12 → 07-19 と 2 回延長された)。**さらなる延長・恒久化は行われなかった**。終了後の扱いは §5.3 を参照。

### 5.0 前史(2026-06-12 停止 → 06-30 再開)

本プロモは「復帰記念プロモ」の位置づけである。2026-06-09 GA 時のプラン同梱と混同しないため、時系列で整理する。

| 日付 | 事象 | 出典 |
|---|---|---|
| 2026-06-09 | Fable 5 / Mythos 5 GA。当初は Pro / Max / Team / seat-based Enterprise に **06-22 まで** 追加費用なしで含まれる予定 | Fable 5 / Mythos 5 リリースアナウンス |
| **2026-06-12** | 米国 export controls により、Anthropic が **Fable 5 のグローバル提供を全面停止**(全ユーザー影響) | redeploying-fable-5 |
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
- Claude Design / Claude for Microsoft 365 / Claude for Teams / Claude Tag

Claude on the web / Desktop / Mobile ではモデルピッカーから "Fable 5" を選択。Claude Code では `/model fable` または `/model best` で切り替える(§2.1)。

### 5.3 promotion 終了後の扱い(2026-07-19 以降・確定)

promotion 終了後の扱いは、当初想定されていた「全プラン一律で usage credits 必須」ではなく、**プラン別に分岐する形で確定した**。

| プラン | promotion 終了後の Fable 5 |
|---|---|
| **Max** | **プランの標準機能として継続。weekly limit の 50% まで追加費用なし** |
| **Team premium seat** | Max と同じ(50% まで included) |
| **Pro** | **プランの usage limit に含まれない。usage credits が必要** |
| **Team standard seat** | Pro と同じ(usage credits が必要) |

- 対象となる Pro / Team standard seat には、変更の緩和措置として **one-time credit** が付与される(公式: 「Eligible Pro and Team standard seats qualify for a one-time credit to help with the change」)。
- 50% 枠のロジック自体は §4.3 のまま維持される。Max / Team premium seat でも「他モデルと同じ枠から引かれ、weekly limit 全体を超えることはできない」点は変わらない。
- Fable 5 は他モデルより枠を速く消費するという公式表現も維持されている。

> **BOSS 環境への影響**: Max プランであれば promotion 終了後も 50% 枠が無償で継続するため、実務上の変化はない。Pro / Team standard seat を併用している場合のみ usage credits の有効化を検討する。

### 5.4 admin の制御

- Claude on the web / Desktop / Mobile: 組織 admin は **promotion 自体を無効化できない**(既定モデルは指定可能)。
- Claude Code: admin は **managed settings で Fable 5 を含むモデル可用性を制御可能**。Claude Code で Fable 5 が見えない場合、admin が制限している可能性がある。

---

## 6. Claude Code での実務上の使い分け

### 6.1 モデル選択の指針

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| 通常のコーディング / 小規模 PR / コードレビュー | **Opus 5** | 公式の第一候補(「start with Claude Opus 5 for complex agentic coding and enterprise work」)。Opus 4.8 と同額でコードレビューの実バグ検出率が向上 |
| 長時間の自律エージェンティックタスク(数時間〜、大規模 migration) | **Opus 5** または **Fable 5** | Opus 5 は agentic coding / long-horizon が最大の伸び幅で、stub や placeholder を残さず完遂する。Fable 5 の半額で済むため、まず Opus 5 を試すのが合理的 |
| 高速レスポンスが必要なドラフト生成 / スニペット拡張 | **Sonnet 5** | 通常価格でも Opus 5 の 0.6 倍、8/31 まで introductory で 0.4 倍 |
| バッチ処理・簡易分類 / メタデータ抽出 | **Haiku 4.5** | 最安 $1 / $5。Extended thinking で複雑推論も部分的にカバー |
| サイバー系の専門ワークロード | **Opus 4.8** 直接指定 or Mythos 5(Project Glasswing 適格者のみ) | Fable 5 / Opus 5 はいずれも cybersecurity フラグで Opus 4.8 に fallback される(§6.5)。公式ベンチでも Opus 5 は cybersecurity exploitation で Mythos 5 に劣る |
| 生物・化学の専門ワークロード | Mythos 5(Project Glasswing 適格者のみ) | **Opus 5 は biology フラグで fallback されず refusal が確定する**(§6.5)。Opus 5 を選ぶと作業が止まる |
| ZDR(zero data retention)下 | Opus 5 / Opus 4.8 等 | Fable 5 は **ZDR 非対応**(30-day retention 固定) |

### 6.2 promotion 終了後(2026-07-20 以降)の運用

promotion が終了したため、Fable 5 の 50% 枠を前提とした運用は **Max / Team premium seat のみ**に限られる(§5.3)。

1. **既定は Opus 5** に置く。Opus 4.8 と同額で agentic coding の完遂率が上がっており、Fable 5 の半額であるため、まず Opus 5 で足りるかを試す。
2. Fable 5 は「Opus 5 で足りなかった長時間タスク」に限定して投入する。Max / Team premium seat なら weekly limit の 50% まで無償、Pro / Team standard seat は usage credits が必要。
3. 定型作業や lint 対応など軽量タスクは **Sonnet 5 / Haiku 4.5** に切替える。Opus 5 では **effort を `low` / `medium` に下げる**のも有効な節約手段になる(§6.3)。
4. **auto mode 併用**が推奨。長時間セッションで確認プロンプトが挟まると思考トークンを無駄にしがち。auto mode の分類器で安全性は担保できる(`docs/best-practices.md` §4「auto mode 詳細」参照)。

> **履歴**: promotion 期間中(2026-07-01 〜 07-19)は「weekly limit の前半 50% を Fable 5 に振り分け、軽量タスクは Sonnet 5 / Haiku 4.5 に流す」という運用が推奨されていた。終了後も Max / Team premium seat では同じ配分が使えるが、Opus 5 の登場により「まず Opus 5」が先に来る点が変わった。

### 6.3 effort 設定の注意

- **Fable 5 のデフォルト effort は `high`**(Opus 4.8 と同じ)。新モデル初回起動時に自動適用される。
- **Opus 5 のデフォルト effort も `high`** で、公式は「**`high` から始め、`low` / `medium` をコスト・レイテンシの主制御として積極的に使う**」ことを推奨する。demanding な coding / agentic タスクで `xhigh`、正当化できる場合のみ `max`。**Opus 4.7 / 4.8 世代の「`xhigh` から始める」という推奨とは逆方向**であり、公式は「旧モデルから effort 設定を引き継いだ場合は、自分の eval で effort sweep をやり直せ」と明記している。
- **⚠️ Opus 5 には model-default hold が無い**。Fable 5 / Opus 4.8 / Opus 4.7 は初回起動時にモデル既定の effort を強制適用して保持するが、**Opus 5 は以前設定したレベルをそのまま引き継ぐ**。旧世代で `xhigh` を設定していた場合、Opus 5 に切り替えても黙って `xhigh` のまま動くため、`/effort` で明示的に確認・再設定する必要がある。
- `xhigh` / `max` を使う場合は `max_tokens` を大きめに取る(公式は 64k 起点を推奨)。Opus 5 は thinking が既定 ON で `max_tokens` が「thinking + response」の合計上限になるため、旧世代の値を流用すると出力が切れる。
- 単純タスクなら `low` / `medium` に落とすことで、Fable 5 / Opus 5 でも weekly limit を大きく節約できる(公式 [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) / [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) が明言)。Opus 5 は **test-time compute scaling の効率が歴代 Opus で最良**とされ、低 effort でも code review の精度が落ちにくい。
- `ultrathink` キーワード・`ultracode` 設定は Fable 5 / Opus 5 でも同じく機能する(モデル横断)。ただし **`ultrathink` は in-context の指示を足すだけで、API に送る effort は変えない**点に注意。

### 6.4 API 利用時の追加要件(参考)

サブスクプランではなく Claude API 経由で Fable 5 を使う場合、以下の対応が必要になる(promotion 対象外・標準レート課金)。

- `stop_reason: "refusal"` を成功レスポンスとして受け取る新しい応答形状への対応
- `fallbacks` パラメータ(API / Claude Platform on AWS で beta)または SDK middleware / 手動リトライで、別モデルへの fallback ロジック
- refusal 発生時は課金なし、リトライ先モデルの prompt-cache コストは fallback credit で相殺される新しい billing ルール

詳細は [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) と [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) を参照。

Opus 5 の GA に伴い、API 側では以下も追加された(いずれも Opus 5 と同時)。

| 追加項目 | 内容 |
|---|---|
| **prompt cache 最小長の引き下げ** | 1,024 → **512 トークン**。短いプロンプトでもキャッシュが効く |
| **mid-conversation tool changes(beta)** | beta header `mid-conversation-tool-changes-2026-07-01`。**prompt cache を保ったまま turn 間で tool を追加・削除できる**。MCP サーバーを動的に着脱するエージェントでキャッシュを捨てずに済む |
| **`fallbacks: "default"` モード** | beta header `server-side-fallback-2026-07-01`。fallback 先を明示列挙せずサーバー側の既定に委ねる |

### 6.5 fast mode と classifier fallback(Opus 5 で変更)

#### fast mode の対象モデル

**v2.1.219 で `/fast` の対象が変わった**。

| モデル | fast mode | 料金 | 提供範囲 |
|---|---|---|---|
| **Opus 5** | **対応**(research preview) | **$10 / $50 per MTok**(1M 全域フラット) | **Claude API のみ**(Bedrock / Google Cloud / Microsoft Foundry 非対応) |
| Opus 4.8 | 対応 | $10 / $50 per MTok | — |
| Opus 4.7 | **API 側では削除済み** | — | 2026-06-25 に deprecated → **2026-07-24 に削除** |

- **fast mode の既定モデルは v2.1.219 以降 Opus 5**(v2.1.154〜v2.1.218 は Opus 4.8、v2.1.142〜v2.1.153 は Opus 4.7)。
- ⚠️ **Opus 4.7 の扱いには公式内で表現の揺れがある**。CHANGELOG v2.1.219 は「Removed Opus 4.7 from fast mode; `/fast` now applies to Opus 5 and Opus 4.8」とする一方、公式 [Fast mode](https://code.claude.com/docs/en/fast-mode) は「**Claude Code は 4.7 を fast model として扱い続けるが API が reject する**」と説明している。実機(v2.1.220)の内部説明でも fast mode の対象に 4.7 が残る。矛盾ではなく「**API 側では削除済み、ClaudeCode の UI 表示だけが追従していない**」と理解するのが正確で、実務上 Opus 4.7 の fast mode は使えない。

#### fast mode の課金モデル(本ドキュメントの主題に直結)

**サブスクリプションプランでは、fast mode はプランの使用枠を一切消費せず usage credits から直接引き落とされる**。公式の記述は次の 2 文である。

> For Claude Code users on subscription plans (Pro/Max/Team/Enterprise), fast mode is available **via usage credits only and not included in the subscription rate limits**.

> **Fast mode usage draws directly from usage credits, even if you have remaining usage on your plan.** This means fast mode tokens do not count against your plan's included usage and are charged at the fast mode rate **from the first token**.

| 論点 | 内容 |
|---|---|
| **プラン枠との関係** | 消費しない。**プランに使用量が残っていても credits 側から課金される**。「weekly limit を節約するために fast mode を使う」は成立しない（逆に実費が出る） |
| **初回有効化のコスト** | fast mode を ON にした時点で、**その会話のコンテキスト全体の uncached input を fast 料金で支払う**。深い会話の途中で ON にすると高額になる。この課金は 1 会話につき 1 回のみ |
| **rate limit の共有** | **対応する全 Opus モデルが 1 つの fast mode rate limit プールを共有**する。Opus 5 と Opus 4.8 を使い分けても限度は分かれない |
| **Team / Enterprise** | **既定で無効**。Owner が明示的に有効化する必要がある |
| **無効化・回避** | `CLAUDE_CODE_DISABLE_FAST_MODE=1` で完全に無効化。設定キーは `fastMode` / `fastModePerSessionOptIn` |
| **LLM gateway 配下の既知問題** | `/fast` が「network connectivity issues」になる場合、`CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1`（接続が拒否される / gateway 資格情報が reject される場合）または `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1`（ネットワークがリクエストを傍受する場合）で回避する |

> **v2.1.221 以降、セッション途中で usage credits が尽きた場合はストリーム上に報告される**(それ以前は silent failure だった)。fast mode を常用する場合はこの版以降が実用的である。

#### 安全分類器の fallback がカテゴリ別になった

**v2.1.219 以降、fallback 先がフラグのカテゴリごとに分岐する**。それ以前は「フラグされた Fable 5 リクエストは一律で provider 既定の Opus に再実行」であり、Opus 5 は fallback 先ではなかった。

| 元のモデル | フラグのカテゴリ | fallback 先 |
|---|---|---|
| **Fable 5** | biology | **Opus 5** で再実行 |
| **Fable 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | biology | **fallback なし。refusal で確定終了** |

> **実務上の注意**: Opus 5 は自身が biology classifier を持つため、生物・化学系のワークロードでは **fallback による救済がなく作業が止まる**。該当領域を扱う場合は最初から別モデル(Mythos 5 の適格者、または明示的に Opus 4.8)を選ぶ。カテゴリ別 fallback は **v2.1.219 以上が必須**で、それ未満のバージョンでは旧来の一律 fallback として動作する。

#### claude.ai(Claude アプリ)側にも別レイヤの自動フォールバックがある

上表は **ClaudeCode / API レイヤ**の挙動である。これとは別に、**claude.ai の会話では Opus 5 が分類器にフラグされた際 Opus 4.8 へ自動で切り替わり、以降その会話は下位モデルのまま固定される**。

- 気付かないうちに「Opus 5 で始めた会話が Opus 4.8 で続いている」状態になり得る
- **Settings > Capabilities の「Switch models when a message is flagged」で無効化できる**
- ClaudeCode の classifier fallback（上表）とは発生条件も切替先の固定挙動も異なるため、混同しない
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

- 本ドキュメントは `docs/best-practices.md` §8 の世代別章(「Opus 4.7 を活用する」→ Opus 4.8 → Fable 5 / Mythos 5 → Sonnet 5 → **Opus 5**)の補足として、**課金・プラン制限側面**を切り出したもの。Opus 5 のプロンプト作法・ハーネス設計への影響は best-practices.md §8 側で扱う。
- `docs/harness.md` 4.6 節「モデル世代によるハーネス進化」は **Opus 5 まで反映済み**(2026-07-26)。Opus 5 は「検証ステップをハーネスから外す方向の世代」として整理されている。
- **Opus 5 のプラン別 weekly limit 消費速度は未確認**。Fable 5 のような専用 support 記事が存在せず、[Models, usage, and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code) も Opus 5 を名指ししていない。「Opus は quota を meaningfully more 消費する」以上の定量情報は公式にないため、本ドキュメントでは倍率を断定しない。

---

## 出典

- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/overview)(2026-07-26 確認)
- [What's new in Claude Opus 5 — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5)(2026-07-26 確認)
- [Introducing Claude Opus 5 — anthropic.com](https://www.anthropic.com/news/claude-opus-5)(2026-07-24)
- [Migration guide — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/migration-guide)(2026-07-26 確認)
- [Model deprecations — platform.claude.com](https://platform.claude.com/docs/en/about-claude/model-deprecations)(2026-07-26 確認)
- [Effort — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/effort)(2026-07-26 確認)
- [Prompting Claude Opus 5 — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)(2026-07-26 確認)
- [Model configuration — code.claude.com](https://code.claude.com/docs/en/model-config)(2026-07-26 確認)
- [Fast mode — code.claude.com](https://code.claude.com/docs/en/fast-mode)(2026-07-26 確認)
- [Introducing Claude Fable 5 and Claude Mythos 5 — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5)(2026-07-11 確認)
- [Claude Fable 5 promotional access — support.claude.com](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)(**2026-07-26 確認: 07-19 終了**)
- [Prompting Claude Fable 5 — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Manage usage credits for paid Claude plans — support.claude.com](https://support.claude.com/en/articles/12429409)
- 関連: `docs/best-practices.md` / `docs/harness.md` / `docs/config-files.md`
