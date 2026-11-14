# Vercel — Hobby と Pro

> 出典:
> - [Hobby plan (vercel.com)](https://vercel.com/docs/plans/hobby) — Hobby の無料枠（転送量・リクエスト）と超過時の扱い `[Web]`
> - [Limits (vercel.com)](https://vercel.com/docs/limits) — 1 日のデプロイ数・ビルド時間・アップロードの上限 `[Web]`
> - [Fair use guidelines (vercel.com)](https://vercel.com/docs/limits/fair-use-guidelines) — 公正利用の例と禁止例 `[Web]`
> - [Terms of Service (vercel.com)](https://vercel.com/legal/terms) — Hobby は個人・非商用に限る（2026-10-19 更新版） `[Web]`
> - [Pro plan (vercel.com)](https://vercel.com/docs/plans/pro-plan) — 月 $20 の platform fee と $20 の利用クレジット `[Web]`
> - [Flat Rate CDN (vercel.com)](https://vercel.com/docs/pricing/flat-rate-cdn) — Pro の CDN 容量の階層 `[Web]`
> - [Regional pricing (vercel.com)](https://vercel.com/docs/pricing/regional-pricing) — 従量の転送量・リクエスト単価（東京 hnd1） `[Web]`
> - [Working with SSL (vercel.com)](https://vercel.com/docs/domains/working-with-ssl) — 証明書の自動発行 `[Web]`
> - [Environments (vercel.com)](https://vercel.com/docs/deployments/environments) — PR ごとのプレビューデプロイ `[Web]`
>
> 最終更新: 2026-11-14

Vercel の公式ドキュメント MCP（`search_vercel_documentation`）は本件に関係の薄い断片しか返さなかったため、すべて公式ページを直接読んで確認した（`[Web]`）。横断の比較と結論は [静的サイトホスティングの選び方](../static-hosting.md) にまとめている。

---

## 1. Hobby（無料）

| 項目 | 値 |
|---|---|
| 転送量（Fast Data Transfer） | 月 100 GB |
| CDN リクエスト | 月 1,000,000 |
| デプロイ | 1 日 100 回 |
| ビルド時間 | 1 デプロイ 45 分まで、同時 1 |
| CLI でアップロードできるファイル | ソース 15,000 ファイル・100 MB（ビルド出力のファイル数には上限なし） |
| プロジェクト | 200 |
| 超過時 | **課金されず、その機能が 30 日間使えなくなる**（"you will have to wait until 30 days have passed before you can use the feature again"） |

- 静的ファイルを配るだけなら関数の実行は発生しない。効いてくるのは転送量とリクエスト数である。
- **リクエスト数の枠（月 100 万）が先に尽きやすい。** 1 ページの表示で HTML・CSS・JS・画像を合わせて 20 リクエストなら、月 5 万 PV で枠に届く（[cost-estimates.md](cost-estimates.md)）。

## 2. 商用利用（Hobby は不可）

利用規約 §4 は次のように書く。

> You shall only use the Services under a Hobby plan for your personal or non-commercial use.

- **収益化するサイトは Pro が必要である。**
- 以前の Fair use guidelines には、広告・アフィリエイトなど何を「商用」とみなすかの定義があった。**2026-11-14 時点の Fair use guidelines にはこの定義が無い**（"commercial" という語自体が無い）。現行の公式文書で根拠にできるのは規約の "personal or non-commercial use" の一文だけである。広告やアフィリエイトを置くサイトは商用とみなされうるため、Hobby には置かない方がよい。
- 規約は Hobby のプロジェクトを "with or without notice" で無効化・削除できるともしている。

## 3. Pro（有料）

| 項目 | 値 |
|---|---|
| 料金 | 月 $20 の platform fee（デプロイできるメンバー 1 人込み）。追加メンバーは 1 人月 $20、閲覧のみは無料 |
| 利用クレジット | 月 $20 分が platform fee に含まれる |
| CDN の課金 | 既定は従量（東京で転送量 $0.16/GB・リクエスト $2.60/100 万件。$20 の利用クレジットから差し引く）。Billing で Flat Rate CDN を有効にすると、月 100 万リクエスト・1 TB まで追加料金なし |
| Flat Rate CDN の上位階層 | 月 $20: 1,000 万リクエスト・50 TB／$100: 5,000 万・50 TB／$300: 1 億 5,000 万・50 TB |
| 従量単価（東京 hnd1） | 転送量 $0.16/GB、リクエスト $2.60/100 万 |
| 支出通知 | 既定で 1 請求期間 $200 で通知 |

- Flat Rate CDN の容量を月の合計で超えると、**翌月から上の階層に移る**。1 日だけの急増では移らない。最上位を超えると従量課金になる。
- 上位階層の料金が platform fee の $20 の利用クレジットで相殺されるかは、公式ページに記載が無い（未確認）。本ドキュメントの試算では相殺されない前提で書いた。

## 4. 機能

| 機能 | 対応 |
|---|---|
| 独自ドメイン + HTTPS | 対応。追加したドメインに Let's Encrypt の証明書を自動発行する |
| PR ごとのプレビュー | 対応。GitHub・GitLab・Bitbucket の PR で自動作成 |
| リダイレクト・ヘッダー・サーバー処理 | 対応（`vercel.json`、Functions、Middleware） |
| Git 連携 | GitHub・GitLab・Bitbucket |

## 5. 向いている用途

- Next.js など、静的出力とサーバー処理が混ざるサイト。プレビューと Git 連携の体験が最もそろっている。
- 非商用で、月数万 PV までの静的サイト（Hobby）。

向かない用途: 収益化するが月 $20 を払いたくないサイト、PV が多く安く配りたい静的サイト（Cloudflare の方が安い）。
