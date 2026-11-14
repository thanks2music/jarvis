# 選定の判断基準

> 出典: 各サービスの仕様は詳細ページ（[github-pages.md](github-pages.md)・[cloudflare.md](cloudflare.md)・[vercel.md](vercel.md)・[netlify.md](netlify.md)・[others.md](others.md)）の出典欄に挙げた公式ページによる。
>
> 最終更新: 2026-11-14

静的サイトのホスティングを選ぶときに、上から順に確かめる観点をまとめる。結論と比較表は [静的サイトホスティングの選び方](../static-hosting.md)、金額の試算は [cost-estimates.md](cost-estimates.md) にある。

---

## 1. 収益化するか（最初に決める）

無料プランでの商用利用の扱いはサービスで分かれ、ここで候補が大きく絞られる。

| 扱い | サービス |
|---|---|
| **無料プランは非商用に限る** | Vercel Hobby（"personal or non-commercial use"） |
| **商取引・SaaS・広告が主目的のサイトは不可** | GitHub Pages |
| 個人・趣味向けと位置づけ（明示的な禁止は確認できず） | Azure Static Web Apps Free、Firebase Spark（本番は Blaze を案内）、`workers.dev` のサブドメイン |
| 無料プランでの商用利用を禁じる条文なし | Cloudflare（独自ドメインで運用）、Netlify、Render、AWS S3 + CloudFront |

広告やアフィリエイトを置くなら、規約で迷わないサービスを最初から選ぶ方が、後で移すより安い。

## 2. 転送量に課金されるか

アクセスが増えたときの費用は、ほぼ転送量の扱いで決まる。

| 扱い | サービス |
|---|---|
| **転送量・静的リクエストとも課金なし** | Cloudflare Workers Static Assets / Pages |
| 上限まで無料、超えると停止（GitHub Pages はソフトリミットで、停止か連絡の可能性） | GitHub Pages（100 GB・ソフト）、Vercel Hobby（100 GB・100 万リクエスト）、Netlify Free（300 credit）、Firebase Spark（10 GB）、Azure SWA Free（100 GB） |
| 無料枠を超えた分が従量課金 | AWS CloudFront（1 TB まで無料）、Render（5 GB まで無料）、Firebase Blaze、Netlify・Vercel の有料プラン |

- 「超えると停止」型は、想定外のアクセス急増でサイトが止まる。Netlify Free はアカウントの **全サイト** が止まる。
- 「従量課金」型は止まらない代わりに請求が増える。予算の通知（Vercel は既定で $200）や支出上限を設定しておく。

## 3. 更新の頻度とビルドの枠

毎日更新するサイトでは、デプロイの回数そのものが費用や制限に効く。

| サービス | 毎日 1 回（月 30 回）のデプロイ |
|---|---|
| Cloudflare Workers Builds | 月 3,000 分の枠。1 回 5 分なら 150 分で余裕 |
| Cloudflare Pages | 月 500 回の枠で余裕 |
| GitHub Pages | 公開リポジトリの Actions は無料。ソフトリミット（10 回/時）も独自 workflow なら対象外 |
| Vercel Hobby | 1 日 100 回の枠で余裕 |
| **Netlify Free** | **本番デプロイ 1 回 15 credit → 月 450 credit で Free（300）を超える** |
| Render | ビルド月 500 分の枠 |
| GitLab Pages | CI 月 400 分の枠 |

## 4. ページが増え続けるときの上限

ページを足し続けるサイトは、ファイル数と総容量の上限に注意する。

- 総容量に上限がある: GitHub Pages（1 GB）、GitLab Pages（1 GB）、Azure SWA Free（1 環境 250 MB）、Firebase（保存 10 GB。過去のリリースも数える）
- ファイル数に上限がある: Cloudflare Free（20,000）、Azure SWA（15,000）
- 1 ページ 1 MB の画像を付けると、GitHub Pages は 3 年弱、Azure SWA Free は 1 年もたずに上限に届く（[cost-estimates.md §4](cost-estimates.md#4-毎日-1-ページ追加するサイトの容量ファイル数)）
- 全ページを毎回ビルドする静的サイトジェネレーターでは、ページ数に比例してビルド時間も伸びる。ビルドの上限時間（GitHub Pages のデプロイ 10 分、Cloudflare 20 分、Vercel 45 分）にも注意する

## 5. サーバー処理・プレビューが要るか

| 要件 | 対応するサービス |
|---|---|
| PR ごとのプレビュー（無料） | Cloudflare、Vercel、Netlify、Render、Firebase（GitHub Action）、Azure SWA。**GitHub Pages と GitLab Pages Free は無い** |
| リダイレクト・ヘッダーの設定 | Cloudflare（`_redirects` / `_headers`）、Netlify、Vercel、GitLab（`_redirects`）。GitHub Pages は無い |
| サーバー処理（API・SSR・フォーム） | Cloudflare Workers、Vercel、Netlify、Firebase（Functions は Blaze）、Azure SWA。GitHub Pages・GitLab Pages は不可 |

## 6. 独自ドメインと移行のしやすさ

- 静的サイトはビルド出力（HTML ファイル群）がそのまま持ち運べるため、どのサービスでも移行しやすい。サービス固有の機能（Vercel の Middleware、Netlify の Forms など）を使うほど移しにくくなる。
- 独自ドメインを付けておけば、サービスを移しても URL は変わらない。`github.io`・`pages.dev`・`vercel.app` などの既定ドメインで公開すると、移行時に URL が変わる。
- Cloudflare Workers の独自ドメインは、DNS を Cloudflare に置く必要がある。

## 7. 提供状況

- **Cloudflare Pages** は廃止ではないが、新規は Workers Static Assets が推奨である。
- **Deno Deploy** は 2027-04 に提供終了する。新規には使わない。
- **Netlify** は 2025-09-04 以降の新規アカウントが credit 制である。古い記事の「月 100 GB 無料」は旧プランの条件である。
