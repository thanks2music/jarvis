# 静的サイトホスティングの選び方（2026-11）

> 出典: 各サービスの公式ドキュメント・料金ページ・利用規約。一覧は詳細ページの出典欄にある。
> - [GitHub Pages](static-hosting/github-pages.md) — docs.github.com `[C7]` `[Web]`
> - [Cloudflare（Workers Static Assets / Pages）](static-hosting/cloudflare.md) — developers.cloudflare.com `[MCP]` `[Web]`
> - [Vercel](static-hosting/vercel.md) — vercel.com/docs・利用規約 `[Web]`
> - [Netlify](static-hosting/netlify.md) — docs.netlify.com・netlify.com/pricing `[Web]`
> - [その他（AWS S3 + CloudFront・Firebase Hosting・Azure Static Web Apps・Render・GitLab Pages）と対象外にしたもの](static-hosting/others.md) — aws.amazon.com・firebase.google.com・learn.microsoft.com ほか `[MCP]` `[Web]`
>
> 最終更新: 2026-11-14（独自ドメイン・サブドメインで運用する場合の仕様を追加）

Git リポジトリと連携して自動でビルド・公開できる静的サイトホスティング（Jamstack ホスティング・フロントエンドクラウド）を、**恒久的な無料枠があるサービスに絞って**比較し、用途ごとの選び方とコストの目安をまとめる。本ページは結論と比較表だけを置き、根拠と詳細は次のページに分けた。

| ページ | 内容 |
|---|---|
| [選定の判断基準](static-hosting/selection-criteria.md) | 収益化・転送量の課金・更新頻度・ページ数の上限・プレビュー・移行のしやすさ |
| [コストの目安](static-hosting/cost-estimates.md) | 月 1 万 / 10 万 / 100 万 PV の試算と計算式、毎日更新するサイトの容量 |
| [GitHub Pages](static-hosting/github-pages.md) / [Cloudflare](static-hosting/cloudflare.md) / [Vercel](static-hosting/vercel.md) / [Netlify](static-hosting/netlify.md) / [その他](static-hosting/others.md) | サービスごとの仕様・制限・商用条件 |

> 出典欄の `[MCP]` は提供元の公式ドキュメント MCP、`[C7]` は Context7 MCP、`[Web]` は公式ページを直接読んだ記述を指す。**数値は公式が明示しているものだけを使い、確認できなかった項目は「未確認」と書いた。**

⚠️ 料金と無料枠は改定される。2026-11-14 時点の公表値である。円は 150 円/USD の固定換算による参考値。

---

## 1. TL;DR

- **迷ったら Cloudflare Workers Static Assets。** 静的ファイルの配信は無料プランでも無料・無制限で、転送量の課金も無い（規約上、ネットワークに過大な負荷をかける場合は一時的に制限されうる）。商用利用を禁じる条文も無く、月 100 万 PV でも $0 で済む。新規なら Cloudflare Pages ではなく Workers Static Assets を使うよう公式が推奨している。
- **GitHub に置いた非商用のサイトなら GitHub Pages が最も手軽。** 公開リポジトリなら無料で、帯域は月 100 GB（ソフトリミット）。ネットショップ・SaaS など商取引が主目的のサイトは規約で不可で、広告・宣伝が主眼のサイトも利用規定（Acceptable Use Policies）上は不可。PR ごとのプレビューは無い。
- **Vercel の Hobby は非商用に限る。** 広告やアフィリエイトで収益化するなら Pro（月 $20〜）が要る。リクエスト枠（月 100 万件）は、1 PV 20 リクエストなら月 5 万 PV で尽きる。
- **Netlify の Free は毎日の更新に向かない。** 2025-09 以降の新規アカウントは credit 制で、Free は月 300 credit、本番デプロイが 1 回 15 credit。毎日デプロイするだけで超え、超えるとアカウントの全サイトが止まる。
- **無料枠を超えたときの挙動は「止まる」か「課金」かに分かれる。** Vercel Hobby（多くの場合 30 日間）・Netlify Free・Firebase Spark・Azure SWA Free は止まり、GitHub Pages はソフトリミットで、配信停止か GitHub からの連絡の可能性がある。AWS CloudFront・Render・Firebase Blaze は従量で課金される（Render は支払い方法が未登録なら止まる）。
- **毎日ページが増えるサイトは容量の上限に注意。** 1 ページ 1 MB なら、GitHub Pages（1 GB）は 3 年弱、Azure SWA Free（250 MB）は 1 年もたずに上限に届く。
- **独自ドメインで運用するなら、DNS をどこに置くかで選択肢が変わる。** Cloudflare Workers は独自ドメインもサブドメインもネームサーバーを Cloudflare に移す必要がある（Free では DNS を他社に残す方式が使えない）。DNS を今の業者に残したいなら、GitHub Pages・Cloudflare Pages（サブドメインのみ）・Vercel・Netlify・Firebase・Render は A / CNAME レコードの追加だけで使える（[§5](#5-独自ドメインで運用する場合)）。
- **Deno Deploy は 2027-04 に提供終了**、AWS Amplify Hosting は無料枠が 12 か月かクレジットだけのため、比較対象から外した。

## 2. 用途別のおすすめ

| 用途 | 非商用 | 収益化（広告・アフィリエイト・販売） |
|---|---|---|
| **単体ページ**（プロフィール・LP） | GitHub Pages（$0） | Cloudflare Workers Static Assets（$0） |
| **50 ページ程度**（ドキュメント・小規模サイト） | GitHub Pages か Cloudflare（$0）。PR プレビューやリダイレクト設定が要るなら Cloudflare | Cloudflare（$0） |
| **毎日 1 ページずつ増やすサイト** | Cloudflare（$0） | Cloudflare（$0） |
| SSR・API を含むサイト（Next.js など） | Vercel Hobby（$0） | Vercel Pro（$20〜）か Cloudflare Workers |

月額の目安（[試算の前提](static-hosting/cost-estimates.md#1-前提): 1 PV = 1 MB・20 リクエスト）:

| サービス | 月 1 万 PV | 月 10 万 PV | 月 100 万 PV |
|---|---|---|---|
| Cloudflare Workers Static Assets | $0 | $0 | $0 |
| GitHub Pages（非商用） | $0 | $0（ソフトリミットに到達） | 不適 |
| AWS S3 + CloudFront（S3 は従量） | $0.1 未満 | $0.1 未満 | 約 $12〜$20 |
| Vercel（収益化は Pro） | $0（Hobby）/ $20（Pro） | 約 $21（Pro） | 約 $120（Pro・Flat Rate CDN） |
| Netlify | $0〜$9 | $20 | 約 $170 |
| Render | 約 $0.75 | 約 $14 | 約 $149 |
| Firebase Hosting | $0（上限ぎりぎり） | 約 $13.5 | 約 $148.5 |
| Azure Static Web Apps | $0 | $0（Free の上限ちょうど） | 約 $189 |

- **単体ページ・50 ページのサイト** は、どのサービスでも無料枠に収まりやすい。違いが出るのは収益化の可否と、アクセスが増えたときの挙動である。
- **毎日更新するサイト** は、デプロイ回数（Netlify は 1 回 15 credit）と、ページが増え続けたときの容量・ファイル数の上限で差が出る。Cloudflare は Free でも 20,000 ファイルまで置け、1 ページ 5 ファイルなら 10 年以上もつ。

## 3. 横断の比較表（無料プラン）

| サービス | 転送量の無料枠 | 超過時 | 無料での商用 | ビルド・デプロイの枠 | 容量・ファイル数 | PR プレビュー | 有料の最低月額 |
|---|---|---|---|---|---|---|---|
| Cloudflare Workers Static Assets | **無制限（課金なし）** | — | 可（独自ドメインで運用） | Workers Builds 月 3,000 分 | 20,000 ファイル・1 ファイル 25 MiB | あり | $5 |
| Cloudflare Pages | **無制限（課金なし）** | — | 可 | 月 500 回 | 20,000 ファイル・1 ファイル 25 MiB | あり（無制限） | —（新規は Workers を推奨） |
| GitHub Pages | 月 100 GB（ソフト） | 停止・連絡の可能性 | 商取引・SaaS が主目的なら不可。広告が主眼も不可 | 公開リポジトリの Actions は無料 | 1 GB | なし | 無料（非公開リポジトリから公開する場合は有料プラン） |
| Vercel Hobby | 月 100 GB・100 万リクエスト | 停止（多くの場合 30 日間） | **不可** | 1 日 100 デプロイ・1 回 45 分 | ビルド出力のファイル数の上限なし（CLI でのアップロードは別に上限あり） | あり | $20（Pro） |
| Netlify Free | 300 credit（約 15 GB 相当） | **全サイト停止** | 禁止条文なし | 本番デプロイ 1 回 15 credit | 未確認 | あり（無制限） | $9（Personal） |
| AWS S3 + CloudFront | 月 1 TB・1,000 万リクエスト（CloudFront のみ。S3 は無料枠なし） | 従量課金 | 可 | 自前（GitHub Actions など） | S3 は無制限（保存は課金） | なし | 従量 |
| Firebase Hosting Spark | 月 10 GB（360 MB/日） | 停止 | 禁止条文なし（本番は Blaze を案内） | 自前（GitHub Action・CLI） | 保存 10 GB | あり（beta） | 従量（Blaze） |
| Azure Static Web Apps Free | 月 100 GB | 配信不可 | 個人向けと位置づけ | GitHub Actions | 1 環境 250 MB・15,000 ファイル | あり（3 環境） | $9（Standard） |
| Render | 月 5 GB | 従量課金（$0.15/GB）。支払い方法が未登録なら停止 | 禁止条文なし | 月 500 分 | 未確認 | あり | 従量 |
| GitLab Pages | 公開値なし | 未確認 | 配布が主目的の利用は不可 | CI 月 400 分 | 1 GB | なし（Premium のみ） | $29/人（Premium） |

## 4. GitHub Pages の URL の決まり方

| リポジトリ | 公開 URL |
|---|---|
| `<owner>/<owner>.github.io` | `https://<owner>.github.io/`（ユーザーサイト。アカウントに 1 つ） |
| `<owner>/<repository>`（上記以外すべて） | `https://<owner>.github.io/<repository>/`（プロジェクトサイト） |

- プロフィール README 用の `<owner>/<owner>` リポジトリもプロジェクトサイト扱いで、`https://<owner>.github.io/<owner>/` になる（公式 docs にこのケースの記述は無く、URL 規則からの帰結）。`https://github.com/<owner>/<owner>` はリポジトリの画面であり、公開先にはならない。
- ユーザーサイトに独自ドメインを付けると、同じアカウントのプロジェクトサイトもその独自ドメインの下（`https://<独自ドメイン>/<repository>/`）に移る。

詳細は [GitHub Pages](static-hosting/github-pages.md#1-url-の決まり方ユーザーサイトとプロジェクトサイト) にある。

## 5. 独自ドメインで運用する場合

`example.com` のような apex（ルート）ドメインと、`www.example.com`・`blog.example.com` のようなサブドメインとで、必要な DNS の設定が違う。apex には CNAME レコードを置けないため、A レコードか、ALIAS / ANAME / CNAME flattening（apex で CNAME のように別名を指せる DNS 業者独自の機能）を使う。

| サービス | apex（`example.com`） | サブドメイン（`www.example.com`） | DNS を今の業者に残せるか | apex と www の自動転送 | 無料プランの独自ドメイン数 |
|---|---|---|---|---|---|
| GitHub Pages | A ×4（+ AAAA）か ALIAS | CNAME → `<owner>.github.io` | 残せる | **あり** | 記載なし |
| Cloudflare Workers | Cloudflare のゾーンが必要 | Cloudflare のゾーンが必要 | **残せない**（ネームサーバーの移管が必要） | なし（Redirect Rules で作る） | 1 ゾーン 100 |
| Cloudflare Pages | Cloudflare のゾーンが必要 | CNAME → `<project>.pages.dev` | サブドメインなら残せる | なし（Bulk Redirects で作る） | 1 プロジェクト 100 |
| Vercel | A（値はプロジェクトごと） | CNAME（値はプロジェクトごと） | 残せる | 追加時に促される。www を主にする推奨 | Hobby 50 / プロジェクト |
| Netlify | ALIAS → `apex-loadbalancer.netlify.com` か A `75.2.60.5` | CNAME → `<site>.netlify.app` | 残せる（apex を主にするなら Netlify DNS を推奨） | **あり** | 50 を推奨 |
| AWS S3 + CloudFront | Route 53 の Alias か、ALIAS 対応の業者 | CNAME → `dxxxx.cloudfront.net` | サブドメインなら残せる | なし | 100 / ディストリビューション |
| Firebase Hosting | A + TXT | A（CNAME ではない） | 残せる | ウィザードで設定 | 1 apex にサブドメイン 20 |
| Azure Static Web Apps | TXT + ALIAS（または Azure DNS） | CNAME → `<app>.azurestaticapps.net` | ALIAS 対応の業者なら残せる | 既定のドメインへ転送 | 2 |
| Render | ALIAS か A `216.24.57.1` | CNAME → `<service>.onrender.com` | 残せる | **あり** | 2（超過 1 個月 $0.25） |
| GitLab Pages | A `35.185.44.232` + TXT（必須） | CNAME → `<namespace>.gitlab.io` + TXT | 残せる | なし | 記載なし |

- どのサービスも、独自ドメインの HTTPS 証明書は無料で自動発行される（AWS は ACM で us-east-1 に発行）。
- DNS の値（IP・CNAME の宛先）は変わることがある。設定するときは各サービスのダッシュボードに表示された値を優先する。
- サービスごとの詳細（証明書・所有確認・ワイルドカード・注意点）は各詳細ページの「独自ドメインで運用する場合」にある。
