# Claude モデル別トークン消費とプラン制限

> 出典:
> - [Models overview (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/overview) — 現行モデルの ID / pricing / context / thinking / tokenizer
> - [Introducing Claude Fable 5 and Claude Mythos 5 (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — Fable 5 / Mythos 5 の API 仕様と課金ルール
> - [Claude Fable 5 promotional access (support.claude.com)](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access) — サブスクプラン上でのプロモーショナルアクセス(**当初 2026-07-01 〜 07-07 → 07-12 まで 5 日間延長**)
>
> 最終更新: 2026-07-11

「Fable 5 が改めて提供された」というアナウンスに合わせて、Fable 5 / Opus 4.8 / Sonnet 5 / Haiku 4.5 の **消費トークン特性** と **サブスクプランの weekly limit がどう減るか** を、公式一次情報のみに基づいて整理する。Claude Code / claude.ai の Pro / Max / Team ユーザーが、期間限定のプロモを含めて「どのモデルをどこで使うか」を判断するための資料。

> 本ドキュメントは公式が数値で明示している事実のみを扱う。「Fable 5 は 2 倍速く減る」といった倍率の断定は、公式が明示していないため行わない。

---

## 1. TL;DR

- Fable 5 の API 料金は **$10 / $50 per MTok**。Opus 4.8 (**$5 / $25**) の 2 倍、Sonnet 5 (**$3 / $15**) の約 3.3 倍、Haiku 4.5 (**$1 / $5**) の 10 倍。
- Fable 5 の tokenizer は Opus 4.7 と同じ世代。**Opus 4.7 より前のモデルと比べ、同じテキストが約 30% 多くトークン化される**(公式 tooltip 明記)。旧世代 tokenizer は Opus 4.6 系・Sonnet 4.5 以前・Haiku 4.5 が該当。
- サブスクプラン(Pro / Max / Team / seat-based Enterprise の Premium seat)では **2026-07-01 〜 07-12 23:59:59 PT** の間 (当初 07-07 終了予定 → **5 日間延長**)、weekly limit の **最大 50% を Fable 5 に振り分け可能**。追加課金なし。
- Fable 5 は「Fable 5 draws from your plan's regular weekly usage limit and **uses it faster than other Claude models**」と公式が明記。倍率は非公開だが、原因は① per-token 料金が高い、② tokenizer が Opus 4.7 世代、③ Adaptive thinking が always on の 3 点。
- Claude Code で Fable 5 を使うには **v2.1.170 以上**が必須。
- API 経由は promotion の対象外で、常時**標準の API レートで課金**される。

---

## 2. 現行モデル一覧(2026-07-11 時点)

| 項目 | Claude Fable 5 | Claude Opus 4.8 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **API ID** | `claude-fable-5` | `claude-opus-4-8` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` |
| **Claude API alias** | `claude-fable-5` | `claude-opus-4-8` | `claude-sonnet-5` | `claude-haiku-4-5` |
| **位置づけ** | Next-generation intelligence for long-running agents | Complex agentic coding and enterprise work | Best combination of speed and intelligence | Fastest model with near-frontier intelligence |
| **入力料金** | **$10** / MTok | $5 / MTok | $3 / MTok ※1 | $1 / MTok |
| **出力料金** | **$50** / MTok | $25 / MTok | $15 / MTok ※1 | $5 / MTok |
| **Context window** | **1M tokens** | 1M tokens | 1M tokens | 200k tokens |
| **Max output(Messages API 同期)** | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **Max output(Batch API、`output-300k-2026-03-24` beta)** | — ※2 | 300k tokens | 300k tokens | — ※2 |
| **Extended thinking** | No | No | No | **Yes** |
| **Adaptive thinking** | **Yes (always on)** | Yes | Yes | No |
| **Comparative latency** | Slower | Moderate | Fast | Fastest |
| **Reliable knowledge cutoff** | Jan 2026 | Jan 2026 | Jan 2026 | Feb 2025 |
| **Data retention** | 30-day、**ZDR 非対応**(Covered Model) | 通常設定に従う | 通常設定に従う | 通常設定に従う |

※1: Sonnet 5 は **2026-08-31 まで introductory 価格 $2 / $10 per MTok** が適用される。9/1 以降は表の $3 / $15 に戻る。
※2: 公式 note で 300k output beta の対象として明記されているのは Opus 4.8 / 4.7 / 4.6・Sonnet 5 / 4.6 のみ。Fable 5 / Haiku 4.5 は対象外。

> **Legacy(現行と併売中)**: Opus 4.7 ($5 / $25、1M、Adaptive Yes / Extended No)、Opus 4.6 ($5 / $25、1M)、Sonnet 4.6 ($3 / $15、1M)、Sonnet 4.5・Opus 4.5 (200k)。Opus 4.1 は **2026-08-05 で deprecation 予定**。

### 2.1 モデル ID とエイリアス

- **バージョン付き ID**(例: `claude-opus-4-8`)は pinned snapshot。バージョンレスなエイリアス的表記でも同じ snapshot を指す(Claude 4.6 世代以降は dateless format も pinned snapshot 扱い)。
- Claude Code の `/model` メニューには、Fable 5 導入と同時に **`fable`(= Fable 5)** と **`best`**(組織にアクセスがあれば Fable 5、なければ最新 Opus)というエイリアスが追加されている(要 v2.1.170 以上)。
- `opus` / `sonnet` / `haiku` エイリアスの解決先は **プロバイダ依存**。Anthropic API では `opus`→Opus 4.8、`sonnet`→Sonnet 5(公式表の現行)。**プロバイダ別解決表は `docs/best-practices.md` の「model alias のプロバイダ別解決」を参照**。

---

## 3. トークン消費を決める 3 つの軸

「Fable 5 は他モデルより速くプラン枠を消費する」という公式表現の内訳を、事実として確認できる 3 つの軸に分解する。

### 3.1 per-token API 料金

| モデル | 入力 | 出力 | Opus 4.8 との倍率(入力) | Opus 4.8 との倍率(出力) |
|---|---|---|---|---|
| Fable 5 | $10 | $50 | **2.0x** | **2.0x** |
| Opus 4.8 | $5 | $25 | 1.0x | 1.0x |
| Sonnet 5(通常) | $3 | $15 | 0.6x | 0.6x |
| Sonnet 5(〜 8/31) | $2 | $10 | 0.4x | 0.4x |
| Haiku 4.5 | $1 | $5 | 0.2x | 0.2x |

API 経由(pay-as-you-go)では、この料金差がそのままドル単価に反映される。サブスクプランの weekly limit もこの料金体系をベースに設計されているため、**同じトークン数を消費した場合、Fable 5 は Sonnet 5 の 3〜5 倍、Haiku 4.5 の 10 倍のペースで枠が減る**と推測できる(公式は正確な倍率を明示していない)。

### 3.2 tokenizer 世代差(Opus 4.7 以降で 約 30% 増)

公式は Fable 5 の context window(1M tokens)の tooltip で次を明記している。

> Claude Fable 5 uses the tokenizer introduced with Claude Opus 4.7; compared to models before Claude Opus 4.7, the same text produces roughly 30% more tokens.

| Tokenizer 世代 | 対象モデル | 同一テキストのトークン数 |
|---|---|---|
| Opus 4.7 世代(新) | Fable 5 / Mythos 5 / **Opus 4.8** / Opus 4.7 | 基準 |
| Opus 4.6 以前世代(旧) | Opus 4.6 / Sonnet 4.6 / Sonnet 4.5 / Opus 4.5 / Opus 4.1 / **Haiku 4.5** | 約 30% 少ない |

Sonnet 5 は tooltip での言及が「~555k words / ~2.5M unicode characters」と Fable 5 / Opus 4.8 と同じ文言のため、新 tokenizer の可能性が高いが、公式は Sonnet 5 について tokenizer 世代を明示していない。**確実に「新 tokenizer」と明言されているのは Fable 5 / Mythos 5 のみ**(Opus 4.7 の legacy 表内でも「Opus 4.7 uses a new tokenizer」と明記)。

### 3.3 Adaptive thinking / Extended thinking

| モデル | Extended thinking | Adaptive thinking | 意味 |
|---|---|---|---|
| Fable 5 / Mythos 5 | No | **Yes (always on)** | `thinking` パラメータを disabled にできない。effort で深さを制御 |
| Opus 4.8 | No | Yes | 通常。効率と品質のバランス |
| Sonnet 5 | No | Yes | 同上 |
| Haiku 4.5 | **Yes** | No | Extended thinking を有効化して思考時間を確保できる。Adaptive はなし |

Fable 5 は **Adaptive thinking を無効化できない**設計のため、単純なタスクでも一定の思考トークンが生成される可能性が高い。これも「速く枠を消費する」要因の 1 つになる。

---

## 4. サブスクプランでの weekly limit の消費速度

Claude Code / claude.ai の Pro / Max / Team は「週次の使用制限」で運用される。**Fable 5 の promotion は API ではなくこのサブスクプラン層に対する施策**である点に注意。

### 4.1 公式が明言していること

- **Fable 5 draws from your plan's regular weekly usage limit** and **uses it faster than other Claude models**.(サポート記事)
- promotion 期間中に **Fable 5 に振り分けられる上限は weekly limit の 50%**。追加課金なし。
- promotion 終了後は Fable 5 が **weekly limit の対象外**となり、usage credits(サブスクとは別課金)経由でしか使えない。

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

## 5. Fable 5 プロモーショナルアクセス(2026-07-01 〜 07-12 限定、5 日延長済)

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
| **2026-07-12 23:59:59 PT** | 延長後の終了予定日。以降 Fable 5 は weekly limit 対象外 (継続には usage credits 必須) | support 15424964 |

- 出典: [Redeploying Fable 5 and Mythos 5 — anthropic.com](https://www.anthropic.com/news/redeploying-fable-5)(2026-07-11 確認) / [Claude Fable 5 promotional access — support.claude.com](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)(2026-07-11 延長確認)

### 5.1 期間と対象プラン

- **期間**: 2026-07-01 〜 2026-07-12 23:59:59 PT (**当初 07-07 終了 → 5 日延長**)
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

### 5.3 promotion 終了後の扱い

2026-07-12 23:59:59 PT (延長後の終了日) を過ぎると、**Fable 5 は weekly limit の対象から外れる**。継続利用には usage credits の有効化が必要になる。

なおサポート記事は「promotion 終了後は usage credits 必須」と明言しているが、2026-07-07 の当初終了予定は**ユーザーバックラッシュを受けて 5 日間延長**された経緯があるため (2026-07-11 時点で最新期限が 07-12)、Anthropic が再延長する可能性も残る。**7/12 直前に support ページで再確認する**のが安全。

### 5.4 admin の制御

- Claude on the web / Desktop / Mobile: 組織 admin は **promotion 自体を無効化できない**(既定モデルは指定可能)。
- Claude Code: admin は **managed settings で Fable 5 を含むモデル可用性を制御可能**。Claude Code で Fable 5 が見えない場合、admin が制限している可能性がある。

---

## 6. Claude Code での実務上の使い分け

### 6.1 モデル選択の指針

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| 通常のコーディング / 小規模 PR / コードレビュー | **Opus 4.8** | `docs/best-practices.md` §8 の推奨。品質とコストのバランス点 |
| 長時間の自律エージェンティックタスク(数時間〜、大規模 migration) | **Fable 5** | 「any previous Claude models より長く自律動作可能」の中核能力。1M context 常時 |
| 高速レスポンスが必要なドラフト生成 / スニペット拡張 | **Sonnet 5** | 通常価格でも Opus 4.8 の 0.6 倍、8/31 まで introductory で 0.4 倍 |
| バッチ処理・簡易分類 / メタデータ抽出 | **Haiku 4.5** | 最安 $1 / $5。Extended thinking で複雑推論も部分的にカバー |
| サイバー / 生物・化学の専門ワークロード | Opus 4.8 直接指定 or Mythos 5(Project Glasswing 適格者のみ) | Fable 5 は safety classifier で refusal → fallback される可能性あり |
| ZDR(zero data retention)下 | Opus 4.8 等 | Fable 5 は **ZDR 非対応**(30-day retention 固定) |

### 6.2 promotion 期間中(7/1 〜 7/7)の推奨

1. weekly limit の **前半 50% を Fable 5** に振り分け、長時間タスク・複雑な仕様検討・多ファイル横断のリファクタなど「Opus 4.8 で追加の思考時間が必要な場面」に投入する。
2. 定型作業や lint 対応など軽量タスクは **Sonnet 5 / Haiku 4.5** に切替え、Fable 5 の 50% 枠を無駄消費しない。
3. Fable 5 の 50% を使い切ったら、残り 50% は Opus 4.8 / Sonnet 5 / Haiku 4.5 に温存。usage credits を有効化していない場合、Fable 5 継続は不可となる。
4. **auto mode 併用**が推奨。長時間 Fable 5 セッションで確認プロンプトが挟まると `xhigh` 以上の思考トークンを無駄にしがち。auto mode の分類器で安全性は担保できる(`docs/best-practices.md` §4「auto mode 詳細」参照)。

### 6.3 effort 設定の注意

- **Fable 5 のデフォルト effort は `high`**(Opus 4.8 と同じ)。新モデル初回起動時に自動適用される。
- 単純タスクなら `low` / `medium` に落とすことで、Fable 5 でも weekly limit を大きく節約できる(公式 [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) が明言)。
- `ultrathink` キーワード・`ultracode` 設定は Fable 5 でも同じく機能する(モデル横断)。

### 6.4 API 利用時の追加要件(参考)

サブスクプランではなく Claude API 経由で Fable 5 を使う場合、以下の対応が必要になる(promotion 対象外・標準レート課金)。

- `stop_reason: "refusal"` を成功レスポンスとして受け取る新しい応答形状への対応
- `fallbacks` パラメータ(API / Claude Platform on AWS で beta)または SDK middleware / 手動リトライで、別モデルへの fallback ロジック
- refusal 発生時は課金なし、リトライ先モデルの prompt-cache コストは fallback credit で相殺される新しい billing ルール

詳細は [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) と [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) を参照。

---

## 7. 既存ドキュメントとの関係

- 本ドキュメントは `docs/best-practices.md` §8「Opus 4.7 を活用する」および「Claude Fable 5 / Claude Mythos 5 への更新」の補足として、**Fable 5 の課金・プラン制限側面**を切り出したもの。
- best-practices.md 側の記述は現時点で **Sonnet 4.6 を legacy 表記のまま参照している箇所**が残っている(公式現行は Sonnet 5)。Anthropic 公式ドキュメントの更新頻度に合わせて `claude-docs-sync` skill で差分反映するのが望ましいが、本ドキュメントの範囲外とする。
- `docs/harness.md` 4.6 節「モデル世代によるハーネス進化」は Fable 5 まで反映済み。ただし Sonnet 5 の新規登場は反映されていないため、同ファイルの継続メンテが必要。

---

## 出典

- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/overview)(2026-07-11 確認)
- [Introducing Claude Fable 5 and Claude Mythos 5 — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5)(2026-07-11 確認)
- [Claude Fable 5 promotional access — support.claude.com](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)(2026-07-11 確認)
- [Prompting Claude Fable 5 — platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Manage usage credits for paid Claude plans — support.claude.com](https://support.claude.com/en/articles/12429409)
- 関連: `docs/best-practices.md` / `docs/harness.md` / `docs/config-files.md`
