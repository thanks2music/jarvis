# その他のサービス — AWS・Firebase・Azure・Render・GitLab Pages ほか

> 出典:
> - [CloudFront pay-as-you-go pricing (aws.amazon.com)](https://aws.amazon.com/cloudfront/pricing/pay-as-you-go/) — Always Free（毎月 1 TB・1,000 万リクエスト）と日本の単価 `[Web]`
> - [CloudFront flat-rate pricing plans (docs.aws.amazon.com)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html) — 定額プラン（Free $0 / Pro $15 ほか）の内容と条件 `[MCP]`
> - [AWS Free Tier (docs.aws.amazon.com)](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier.html) — 2025-07-15 以降のクレジット制と Always Free `[MCP]`
> - [AWS Price List API: Amazon S3 ap-northeast-1 (pricing.us-east-1.amazonaws.com)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-northeast-1/index.json) — S3 Standard の東京の保存単価 `[Web]`
> - [AWS Amplify pricing (aws.amazon.com)](https://aws.amazon.com/amplify/pricing/) — 無料枠が 12 か月またはクレジット `[Web]`
> - [Firebase pricing (firebase.google.com)](https://firebase.google.com/pricing) — Spark / Blaze の Hosting の枠と単価 `[MCP]`
> - [Hosting usage, quotas, and pricing (firebase.google.com)](https://firebase.google.com/docs/hosting/usage-quotas-pricing) — 月 10 GB の無料転送と超過時のサイト停止 `[MCP]` `[Web]`
> - [Firebase FAQ (firebase.google.com)](https://firebase.google.com/support/faq) — Blaze は本番アプリ向け、Spark の超過で月末まで停止 `[MCP]` `[Web]`
> - [Hosting: GitHub integration (firebase.google.com)](https://firebase.google.com/docs/hosting/github-integration) — PR ごとのプレビューチャネル `[MCP]`
> - [Azure Static Web Apps hosting plans (learn.microsoft.com)](https://learn.microsoft.com/azure/static-web-apps/plans) — Free（個人プロジェクト向け）と Standard `[MCP]`
> - [Azure Static Web Apps quotas (learn.microsoft.com)](https://learn.microsoft.com/azure/static-web-apps/quotas) — 帯域・アプリ数・ファイル数 `[MCP]` `[Web]`
> - [Azure Retail Prices API (prices.azure.com)](https://prices.azure.com/api/retail/prices) — Standard の月額と超過帯域の単価（japaneast） `[Web]`
> - [CloudFront: Add a domain to an existing distribution (docs.aws.amazon.com)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/add-domain-existing-distribution.html) / [Alternate domain names (docs.aws.amazon.com)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html) — apex は Route 53 の Alias を推奨、ワイルドカード `[MCP]`
> - [ACM overview (docs.aws.amazon.com)](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html) / [Route 53 pricing (aws.amazon.com)](https://aws.amazon.com/route53/pricing/) — CloudFront 用の証明書は us-east-1、ホストゾーン月 $0.50、Alias 問い合わせは無料 `[MCP]` `[Web]`
> - [Firebase: Connect a custom domain (firebase.google.com)](https://firebase.google.com/docs/hosting/custom-domain) — A / TXT レコード、証明書、20 サブドメインの制限 `[MCP]` `[Web]`
> - [Static Web Apps: custom domains (learn.microsoft.com)](https://learn.microsoft.com/azure/static-web-apps/custom-domain) / [apex domain with external DNS (learn.microsoft.com)](https://learn.microsoft.com/azure/static-web-apps/apex-domain-external) — TXT + ALIAS、既定のドメインへの転送 `[MCP]`
> - [Render: Custom domains (render.com)](https://render.com/docs/custom-domains) / [Configure other DNS providers (render.com)](https://render.com/docs/configure-other-dns) — レコード、apex と www の自動転送、ドメイン数と料金 `[Web]`
> - [GitLab Pages custom domains (docs.gitlab.com)](https://docs.gitlab.com/user/project/pages/custom_domains_ssl_tls_certification/) — A / CNAME、TXT による所有確認 `[Web]`
> - [Render: Static Sites (render.com)](https://render.com/docs/static-sites) / [Outbound Bandwidth (render.com)](https://render.com/docs/outbound-bandwidth) / [Pricing (render.com)](https://render.com/pricing) — 無料の静的サイトと帯域 `[Web]`
> - [GitLab Pages (docs.gitlab.com)](https://docs.gitlab.com/user/project/pages/) / [GitLab.com settings (docs.gitlab.com)](https://docs.gitlab.com/user/gitlab_com/) / [Compute minutes (docs.gitlab.com)](https://docs.gitlab.com/ci/pipelines/compute_minutes/) — サイト容量・CI の分数 `[Web]`
> - [GitLab Acceptable Use Policy (handbook.gitlab.com)](https://handbook.gitlab.com/handbook/legal/acceptable-use-policy/) — コンテンツ配布を主目的とした利用の禁止 `[Web]`
> - [Deno Deploy pricing and limits (docs.deno.com)](https://docs.deno.com/deploy/pricing_and_limits/) / [Deno is joining Cloudflare (deno.com)](https://deno.com/blog/cloudflare) — 2027-04 の提供終了 `[Web]`
>
> 最終更新: 2026-11-14（独自ドメイン・サブドメインで運用する場合の仕様を追加）

`[MCP]` は提供元の公式ドキュメント MCP（AWS / Firebase / Microsoft Learn）経由、`[Web]` は公式ページ・公式 API を直接読んだ記述を指す。横断の比較と結論は [静的サイトホスティングの選び方](../static-hosting.md) にまとめている。

本ドキュメントは **恒久的な無料枠があるサービス** だけを比較対象にしている（AWS S3 + CloudFront は、配信の CloudFront にだけ恒久的な無料枠がある構成として例外的に含めた）。期間限定の無料枠やクレジットしか無いものは §6 に理由を書いて外した。

---

## 1. AWS S3 + CloudFront

S3 にファイルを置き、CloudFront（CDN）から配信する構成。ビルドと Git 連携は自分で用意する（GitHub Actions など）。

**無料の範囲は CloudFront の Always Free にある。** 毎月更新される枠で、12 か月の期限は無い。

| 項目 | 値 |
|---|---|
| CloudFront の Always Free | 毎月 転送量 1 TB・HTTP/HTTPS リクエスト 1,000 万件・CloudFront Functions 200 万回・SSL 証明書無料 |
| 超過時（日本の閲覧者） | 転送量 $0.114/GB（次の 9 TB）、HTTPS リクエスト $0.0120/1 万件 |
| S3 からの取得 | CloudFront へのオリジン取得の転送は無料 |
| S3 の保存（東京、Standard） | $0.025/GB・月（最初の 50 TB）。**S3 には恒久的な無料枠が無い** |

- 2025-07-15 以降、AWS の新規アカウントの無料枠はクレジット制（最大 $200）に変わった。「無料アカウントプラン」は 6 か月かクレジットを使い切った時点で終わる。CloudFront の Always Free はこれとは別枠である。
- **定額プラン（flat-rate pricing plans）も選べる。** Free（$0）は月 100 万リクエスト・100 GB・S3 クレジット 5 GB、Pro（$15）は月 1,000 万リクエスト・50 TB。超過しても追加料金は発生しない（枠を大きく超え続けると配信の品質が落とされる）。ただし AWS WAF の Web ACL の関連付けが必須で、**AWS Free Tier を使っているアカウントは対象外** である。小規模な静的サイトでは、従量の Always Free の方が枠が大きい。
- 商用利用の制限は無い。プレビュー環境と Git 連携は付いていない。

### 独自ドメインで運用する場合（S3 + CloudFront）

| 項目 | 独自ドメイン（apex: `example.com`） | サブドメイン（`www.example.com` など） |
|---|---|---|
| DNS レコード | apex には CNAME を置けないため、Route 53 の Alias レコード（A / AAAA）で CloudFront を指す。外部 DNS なら ALIAS / ANAME / CNAME flattening に対応した業者が必要 | CNAME で `dxxxx.cloudfront.net` を指す。DNS は外部のままでよい |
| CloudFront 側 | ディストリビューションの代替ドメイン名（alternate domain name）にドメインを登録 | 同じ |
| HTTPS | ACM の証明書（**us-east-1 で発行する**）。DNS の CNAME で検証し、72 時間以内に検証しないと失効。発行は無料 | 同じ（1 ディストリビューションに証明書は 1 枚なので、apex と www を SAN にまとめる） |

- 公式は "Because most DNS providers don't support ALIAS records, we recommend creating an ALIAS record in Route 53." とする。**Route 53 を使うとホストゾーンが月 $0.50**（最初の 25 ゾーン）かかる。CloudFront を指す Alias レコードへの問い合わせは無料。
- apex と www の転送は自動では無い。S3 の公式チュートリアルは www 用のバケットを作ってリダイレクトさせるが、S3 のウェブサイトエンドポイントは HTTP しか扱えない。HTTPS で転送するなら CloudFront Functions などで自作する。
- 代替ドメイン名は 1 ディストリビューション 100 個まで。ワイルドカード（`*.example.com`）も使えるが、1 階層分だけで apex は含まない。
- 定額プランの "Apex-level domains per plan | 1" は、1 プランが 1 ディストリビューションと最大 1 つの apex ドメインを対象にするという意味である（"Each pricing plan covers one CloudFront distribution with up to one apex (root) domain"）。同じ apex のサブドメインを同じプランに入れられるかは明記されていない（未確認）。

## 2. Firebase Hosting

| 項目 | Spark（無料） | Blaze（従量） |
|---|---|---|
| 保存 | 10 GB | 10 GB まで無料、以降 $0.026/GB |
| 転送量 | 360 MB/日（月 10 GB） | 月 10 GB まで無料、以降 $0.15/GB |
| 独自ドメイン + SSL | 対応 | 対応 |
| 支払い方法の登録 | 不要 | 必要 |

- 料金ページは「360 MB/日」、Hosting のドキュメントは「10 GB/月」と書く。どちらも公式の表記である。
- **無料枠を超えるとサイトが止まる。** "If you are not on the Blaze plan, and you reach the 10 GB/month limit ... we offer a short grace period but then your sites will be disabled ... until the start of the next month"。
- プレビューチャネル（`SITE_ID--CHANNEL_ID-HASH.web.app`）があり、GitHub Action で PR ごとに作れる（既定 7 日、最長 30 日で失効。beta）。ビルドは GitHub Actions かローカルで行い、Firebase CLI でデプロイする。
- Spark での商用利用を禁じる記述は見当たらない。公式 FAQ は Blaze を "designed for production apps" と位置づける。

### 独自ドメインで運用する場合（Firebase Hosting）

| 項目 | 独自ドメイン（apex: `example.com`） | サブドメイン（`www.example.com` など） |
|---|---|---|
| DNS レコード | A レコード（例: `199.36.158.100`。値はコンソールのウィザードに従う）+ 所有確認の TXT レコード | **CNAME ではなく A レコード**（例: `www` → `199.36.158.100`。値はコンソールのウィザードに従う） |
| HTTPS | 証明書を自動発行。DNS を向けてから最大 24 時間、多くは数時間 | 同じ |

- DNS は外部のままでよい（Cloudflare・Google Cloud DNS・Namecheap などの例が公式にある）。apex に ALIAS は要らない。
- 所有確認の TXT レコードは**消さずに残す**（証明書の更新に使う）。apex を確認すると、そのサブドメインもまとめて確認済みになる。
- 他の業者を指す A / CNAME レコードと、**AAAA レコードは消す**。残っていると証明書を発行できない。CAA を使う場合は `letsencrypt.org` と `pki.goog` を許可する。
- ウィザードで「別のドメインへリダイレクトする」を選べば、apex と www を同じ内容にそろえられる。
- 無料の Spark でも独自ドメインと SSL を使える（料金ページの Spark 列に "Custom domain & SSL ✓"）。1 つの apex につきサブドメインは 20 個まで（証明書の発行数の制限）。

## 3. Azure Static Web Apps

| 項目 | Free | Standard |
|---|---|---|
| 料金 | 無料 | 月 $9（japaneast） |
| 帯域 | 月 100 GB（**超過分は配信されない**: "we will not be able to serve your site"） | 月 100 GB、超過 $0.20/GB |
| アプリ数（サブスクリプション） | 10 | 100 |
| 容量 | 1 環境 250 MB、合計 500 MB | 合計 2 GB |
| ファイル数 | 15,000 | 15,000 |
| 独自ドメイン | 2 | 6（plans のページは 5 と書く。公式内で食い違い） |
| プレビュー環境 | 3 | 10 |
| SLA | なし | あり |

- Free は "For personal projects"、料金ページの FAQ は "intended for hobby/personal usage and does not come with SLA" とする。商用を明示的に禁じる条文は確認できなかったが、収益化するなら Standard が前提である。
- GitHub / Azure DevOps と連携し、GitHub Actions / Azure Pipelines でビルドする。PR ごとに staging 環境ができる。

### 独自ドメインで運用する場合（Azure Static Web Apps）

| 項目 | 独自ドメイン（apex: `example.com`） | サブドメイン（`www.example.com` など） |
|---|---|---|
| DNS レコード | 所有確認の TXT レコード + ALIAS（または ANAME / CNAME flattening）で `<app>.azurestaticapps.net` を指す。業者が対応していなければ Azure DNS に移すか、A レコード（グローバル配信の恩恵が無くなる）か、apex を www へ転送する | CNAME で `<app>.azurestaticapps.net` を指す |
| HTTPS | 無料の証明書を自動発行・自動更新（Free でも Standard でも） | 同じ |

- Azure DNS を使うと、必要な CNAME / TXT / ALIAS レコードが自動で作られる。
- apex の変更が反映されるまで最大 72 時間かかる。
- 「既定のドメイン（default domain）」を 1 つ決めると、他のドメインへのアクセスはそこへ自動で転送される。
- 独自ドメインの数は Free 2 個。Standard は plans のページが 5、quotas のページが 6 と食い違う。プレビュー環境には独自ドメインを付けられない。

## 4. Render（Static Sites）

| 項目 | Hobby（$0 + 使用量） | Pro（$25/月 + 使用量） |
|---|---|---|
| 静的サイト | 無料（"Deploy websites for free, forever"） | 同じ |
| 含まれる帯域 | 月 5 GB | 月 25 GB |
| 超過帯域 | $0.15/GB（支払い方法の登録が無ければ翌月までサービス停止） | $0.15/GB |
| ビルド（pipeline minutes） | 月 500 分 | 月 1,000 分 |
| 独自ドメイン | 2（追加 1 つ月 $0.25） | 15 |

- 無料の静的サイトの PR プレビューも無料。TLS 証明書は自動発行。
- 規約に非商用の制限は無い（Hobby は「個人プロジェクトとプロトタイプ向け」という位置づけ）。

### 独自ドメインで運用する場合（Render）

| 項目 | 独自ドメイン（apex: `example.com`） | サブドメイン（`www.example.com` など） |
|---|---|---|
| DNS レコード | ANAME / ALIAS（CNAME flattening）で `<service>.onrender.com` を指す。使えない業者なら A レコードで `216.24.57.1`。AAAA は消す | CNAME で `<service>.onrender.com` を指す |
| HTTPS | Let's Encrypt / Google Trust Services の証明書を無料で自動発行。HTTP は自動で HTTPS へ転送 | 同じ |

- DNS は外部のまま使う（Render は DNS サービスを提供していない）。Cloudflare の DNS を使う場合は、apex でも A ではなく CNAME を使う。
- **www を追加すると apex も自動で追加されて www へ転送され、apex を追加すると www が追加されて apex へ転送される。**
- 独自ドメインは Hobby 2 個まで含まれ、超えた分は 1 ドメインあたり月 $0.25。自動で追加された apex / www の片割れが 2 個目として数えられるかは明記されていない（未確認）。ワイルドカードも使える。

## 5. GitLab Pages（GitLab.com Free）

| 項目 | 値 |
|---|---|
| サイト容量 | 1 GB（アーティファクトの上限） |
| CI の分数 | 月 400 分（Free の名前空間） |
| 独自ドメイン | 1 サイト 150 個、Let's Encrypt の証明書を自動発行 |
| リダイレクト | `_redirects` で最大 1,000 ルール（Free でも可） |
| MR ごとのプレビュー | **Premium 以上のみ**（parallel deployments） |
| 帯域・ファイル数の上限 | 公開値なし（未確認） |

- URL は `<username>.gitlab.io/<project>` だが、既定で `https://<project>-<id>.gitlab.io/` のような固有ドメイン（unique domains）にリダイレクトされる。
- 利用規約は、コンテンツの配布を主目的にした使い方（"for the primary purpose of distributing content"）や、他の利用者を大きく上回る使い方を禁じている。

### 独自ドメインで運用する場合（GitLab Pages）

| 項目 | 独自ドメイン（apex: `example.com`） | サブドメイン（`www.example.com` など） |
|---|---|---|
| DNS レコード | A レコード `35.185.44.232`（IPv6 は AAAA `2600:1901:0:7b8a::`）。apex に CNAME は使わない | CNAME で `<namespace>.gitlab.io` を指す |
| 所有確認 | **GitLab.com では必須。** `_gitlab-pages-verification-code.example.com` に TXT レコードを置き、残し続ける。確認できないドメインは 7 日後に削除される | 同じ（ドメインごとに TXT が要る） |
| HTTPS | Let's Encrypt の連携を有効にすると自動発行・自動更新（最大 1 時間）。"Force HTTPS" で HTTP を転送 | 同じ |

- DNS は外部のままでよい。apex と www の自動転送は公式に記載が無い。1 プロジェクトに複数のドメインを付けられる（上限は未確認）。

## 6. 比較対象から外したもの

| サービス | 外した理由 |
|---|---|
| **AWS Amplify Hosting** | 無料枠が "Free for 12 months" か、新規アカウントのクレジット（最大 $200）でしか使えない。恒久的な無料枠は無い。従量はビルド $0.01/分・保存 $0.023/GB・配信 $0.15/GB |
| **Deno Deploy** | **2027-04 に提供終了する。** 公式ドキュメントに "Deno Deploy will be sunset in April 2027" と表示され、2026-10-09 の公式ブログは "Deno Deploy will continue operating for six months before shutting down" と書く（Deno チームは Cloudflare に合流し、有料顧客の Cloudflare Workers への移行を支援する） |
