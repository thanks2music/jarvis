# GitHub Pages — 仕様・制限・URL の決まり方

> 出典:
> - [What is GitHub Pages? (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) — ユーザー / Organization サイトとプロジェクトサイトの違い、既定の URL `[C7]`
> - [GitHub Pages limits (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) — サイト容量・帯域・ビルド回数・デプロイのタイムアウト・商用利用の禁止 `[C7]`
> - [Creating a GitHub Pages site (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) — リポジトリ名の付け方、GitHub Free では公開リポジトリが必須 `[C7]`
> - [About custom domains and GitHub Pages (docs.github.com)](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages) — ユーザーサイトの独自ドメインがプロジェクトサイトにも使われること `[C7]`
> - [Securing your GitHub Pages site with HTTPS (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https) — Let's Encrypt による証明書と HTTPS の強制 `[C7]`
> - [Configuring a publishing source (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — ブランチから公開する方式と GitHub Actions で公開する方式 `[C7]`
> - [Using custom workflows with GitHub Pages (docs.github.com)](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) — アーティファクトの条件、PR で起動したときはデプロイを飛ばすこと `[C7]`
> - [GitHub Acceptable Use Policies (docs.github.com)](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies) — 広告を主目的にしないこと（Pages を含む） `[Web]`
> - [GitHub Actions billing (docs.github.com)](https://docs.github.com/en/billing/concepts/product-billing/github-actions) — 公開リポジトリの標準ランナーは無料 `[Web]`
> - [GitHub's plans (docs.github.com)](https://docs.github.com/en/get-started/learning-about-github/githubs-plans) — 非公開リポジトリから Pages を使えるプラン `[Web]`
>
> 最終更新: 2026-11-14

出典欄の `[C7]` は Context7 MCP 経由で読んだ記述、`[Web]` は公式ページを直接読んだ記述を指す。横断の比較と結論は [静的サイトホスティングの選び方](../static-hosting.md) にまとめている。

---

## 1. URL の決まり方（ユーザーサイトとプロジェクトサイト）

GitHub Pages のサイトは 2 種類ある。どちらになるかは **リポジトリ名だけで決まる**。

| | ユーザー / Organization サイト | プロジェクトサイト |
|---|---|---|
| リポジトリ | `<owner>.github.io` という名前のリポジトリ | それ以外の任意のリポジトリ |
| 既定の URL | `https://<owner>.github.io/` | `https://<owner>.github.io/<repository>/` |
| 数 | アカウントにつき 1 つ | リポジトリにつき 1 つ |

公式の表は "Must be stored in a repository named `<owner>.github.io`" / "Default site location `http(s)://<owner>.github.io/<repositoryname>`" と書く。アカウント名に大文字が含まれる場合、リポジトリ名は小文字にする。

具体例（`<owner>` を `octocat` とする）:

| リポジトリ | Pages を有効にしたときの URL | 種類 |
|---|---|---|
| `octocat/octocat.github.io` | `https://octocat.github.io/` | ユーザーサイト |
| `octocat/my-app` | `https://octocat.github.io/my-app/` | プロジェクトサイト |
| `octocat/octocat`（プロフィール README 用のリポジトリ） | `https://octocat.github.io/octocat/` | プロジェクトサイト |

- **`<owner>/<owner>` はユーザーサイトにならない。** プロフィール README 用の特別なリポジトリだが、Pages の URL 規則で特別扱いされるのは `<owner>.github.io` という名前だけである。このため通常のプロジェクトサイトとして `https://<owner>.github.io/<owner>/` で公開される（公式 docs にこのケースの記述は無く、上の URL 規則からの帰結）。
- **`https://github.com/<owner>/<repository>` はリポジトリの画面の URL であり、Pages の公開先ではない。** Pages は常に `github.io` のドメイン（または独自ドメイン）で配信される。
- **ユーザーサイトとプロジェクトサイトは同じドメインに同居する。** ユーザーサイトを作っても、既存のプロジェクトサイトの URL（`https://<owner>.github.io/<repository>/`）は変わらない。ユーザーサイト側に、プロジェクトのリポジトリ名と同じパスのページを作るのは避ける（どちらが応答するかは公式 docs に記載が無い）。

### ユーザーサイトに独自ドメインを付けた場合

ユーザーサイトに独自ドメインを設定すると、**同じアカウントのプロジェクトサイトもそのドメインの下に移る**。公式は "if you set a custom domain for a user site or organization site, that same custom domain will be used for all project sites owned by the same account" と書き、例として `www.octocat.com` を設定するとプロジェクト `octo-project` は `www.octocat.com/octo-project` になると示す。プロジェクトごとに別の独自ドメインを設定すれば上書きできる。

---

## 2. 制限（無料で使える範囲）

| 項目 | 値 | 原文 |
|---|---|---|
| 料金 | 無料（GitHub Free は公開リポジトリのみ） | "If the account that owns the repository uses GitHub Free ... the repository must be public." |
| 公開サイトの容量 | 1 GB まで | "Published GitHub Pages sites may be no larger than 1 GB." |
| ソースリポジトリ | 推奨上限 1 GB | "recommended limit of 1 GB" |
| 帯域 | 月 100 GB（ソフトリミット） | "*soft* bandwidth limit of 100 GB per month" |
| ビルド | 1 時間に 10 回（ソフトリミット）。独自の GitHub Actions workflow で公開する場合は対象外 | "This limit does not apply if you build and publish your site with a custom GitHub Actions workflow." |
| デプロイのタイムアウト | 10 分 | "deployments will timeout if they take longer than 10 minutes" |
| Actions で渡すアーティファクト | gzip 圧縮の tar で 10 GB 未満、リンク不可 | "must be a gzip-compressed tar file under 10GB" |
| ファイル数 | 上限の記載なし（未確認） | — |
| 超過時 | 配信できなくなるか、GitHub Support から連絡が来る。レート制限は HTTP 429 | "we may not be able to serve your site, or you may receive a polite email from GitHub Support" |

- ビルドに使う GitHub Actions は、**公開リポジトリの標準ランナーなら無料**（"remains free independently and does not reduce the included compute usage"）。毎日更新しても Actions の費用はかからない。
- 非公開リポジトリから公開したい場合は有料プラン（Pro / Team / Enterprise）が要る。ただしサイト自体は公開される。サイトをアクセス制限付きで公開できるのは GitHub Enterprise Cloud の Organization だけである。

## 3. 商用利用

公式の制限ページは次のように書く。

> GitHub Pages is not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS).

Acceptable Use Policies も、Pages を含むアカウントのコンテンツについて "the primary focus ... should not be advertising or promotional marketing" とする。

- **ネットショップ・SaaS・商取引が主目的のサイトは不可。**
- 広告やアフィリエイトリンクを置くこと自体を名指しで禁止する条文は無い。ただし **広告が主目的（primary focus）になるサイトは不可** である。収益化が主目的のサイトは、規約上の判断に迷わない他サービス（[cloudflare.md](cloudflare.md) など）に置く方が安全である。

## 4. 機能

| 機能 | 対応 |
|---|---|
| 独自ドメイン + HTTPS | 対応。証明書は Let's Encrypt で自動発行し、"Enforce HTTPS" で HTTP を HTTPS へリダイレクトする。設定後、HTTPS が使えるまで最大 1 時間ほどかかる |
| PR ごとのプレビュー | なし。公式の workflow は PR で起動すると "This step is skipped if the workflow was triggered by a pull request." としてデプロイを飛ばす |
| リダイレクト・ヘッダー・サーバー処理 | 独自の `404.html` 以外は公式 docs に設定方法の記載が無い（未確認）。静的ファイルの配信のみと考える |
| 公開の方式 | ① ブランチ（ルートか `/docs`）から公開 ② GitHub Actions でビルドして `actions/upload-pages-artifact` → `actions/deploy-pages` で公開。Jekyll 以外のツールでビルドするなら ② を使う |

## 5. 向いている用途

- 非商用のポートフォリオ・ドキュメント・ツールの公開ページ。1 ページでも数百ページでも、月 100 GB 以内なら無料で済む。
- すでにコードを GitHub の公開リポジトリで管理しているもの。

向かない用途: 商取引や広告が主目的のサイト、月 100 GB を超える転送量のサイト、PR ごとのプレビューやリダイレクト設定が要るサイト。
