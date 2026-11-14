# Netlify — credit 制のプラン

> 出典:
> - [Credit-based pricing plans (docs.netlify.com)](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/) — 2025-09-04 以降の新規アカウントは credit 制 `[Web]`
> - [How credits work (docs.netlify.com)](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/how-credits-work/) — 本番デプロイ・転送量・リクエストの credit 単価 `[Web]`
> - [Billing FAQ for credit-based plans (docs.netlify.com)](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/billing-faq-for-credit-based-plans/) — credit を使い切ったときの停止 `[Web]`
> - [Pricing (netlify.com)](https://www.netlify.com/pricing/) — Free / Personal / Pro の料金と credit 数 `[Web]`
> - [Legacy pricing plans (docs.netlify.com)](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-legacy-plans/legacy-pricing-plans/) — 2025-09-04 より前のアカウントの旧プラン `[Web]`
> - [Terms of Use (netlify.com)](https://www.netlify.com/legal/terms-of-use/) — 2026-10-14 更新版 `[Web]`
>
> 最終更新: 2026-11-14

`[Web]` は公式ページを直接読んだ記述を指す（Netlify には公式ドキュメント MCP が無い）。横断の比較と結論は [静的サイトホスティングの選び方](../static-hosting.md) にまとめている。

---

## 1. credit 制の仕組み

**2025-09-04 以降に作ったアカウントは credit 制のプランになる**（"Starting on September 4, 2025, all new Netlify accounts will use the new credit-based pricing plans."）。転送量・リクエスト・本番デプロイを、すべて 1 つの credit から差し引く。

| 消費するもの | credit |
|---|---|
| 本番デプロイ 1 回 | 15 |
| 転送量 1 GB | 20 |
| Web リクエスト 1 万件 | 2 |
| Functions の計算 1 GB 時間 | 10 |
| プレビューデプロイ・ブランチデプロイ・失敗したデプロイ・ロールバック | 0 |
| ビルド時間 | 計測しない（"Build minutes are not calculated as their own metric"） |

- プレビューのデプロイ自体は 0 credit だが、プレビューへのアクセスはリクエストとして数える。

## 2. プラン

| プラン | 料金 | credit / 月 | 備考 |
|---|---|---|---|
| Free | $0 | 300（ハードリミット） | 課金されない。同時ビルド 1 |
| Personal | $9/月 | 1,000 | 自動補充 500 credit ごとに $5 |
| Pro | $20/月〜（メンバー無制限） | 3,000〜 | 自動補充 1,500 credit ごとに $10。上位の階層の価格は未確認 |

**credit を使い切ると、アカウントの全サイトが止まる。** 公式は次のように書く。

> Once your credit balance is completely used up, all of your web projects (sites/apps) are paused and visitors ... will find a `Site not available` page

停止は次の請求期間まで続く。アップグレードか自動補充を有効にすれば再開できる。

## 3. Free で収まる範囲

300 credit を 1 つの用途だけに使った場合の上限（公式の単価からの計算）:

- 本番デプロイだけなら **月 20 回**
- 転送量だけなら **月 15 GB**
- リクエストだけなら **月 150 万件**

実際はこれらを合算する。**毎日 1 回本番デプロイするだけで 30 × 15 = 450 credit となり、Free を超える。** 毎日更新するサイトは Personal（$9/月）以上が前提になる。

## 4. 商用利用

利用規約（2026-10-14 更新）に "commercial" の語は無く、Free を非商用に限る条文は見当たらない。

## 5. 機能

| 機能 | 対応 |
|---|---|
| 独自ドメイン + HTTPS | 全プランで対応 |
| PR ごとのプレビュー | 全プランで無制限（Deploy Previews） |
| リダイレクト・ヘッダー・サーバー処理 | 対応（`_redirects` / `netlify.toml`、Functions） |
| Git 連携 | GitHub などから自動デプロイ。非公開リポジトリに複数人がコミットする場合は Pro |

## 6. 旧プラン（2025-09-04 より前のアカウント）

旧 Free は転送量 月 100 GB・ビルド 月 300 分（どちらもハードリミット）だった。旧プランのアカウントには旧条件が残るが、credit 制への切り替えは元に戻せない（"irreversible"）。

## 7. 向いている用途

- 更新頻度が低い（月 20 回未満のデプロイ）、転送量の少ないサイト。
- PR ごとのプレビューを無料で使いたいサイト。

向かない用途: 毎日更新するサイトを無料で運用したい場合、転送量が多いサイト（1 GB = 20 credit が割高）。
