# Cloudflare — Workers Static Assets と Pages

> 出典:
> - [Workers Best Practices (developers.cloudflare.com)](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/) — 新規プロジェクトは Pages ではなく Workers Static Assets を使う `[MCP]`
> - [Static Assets: Billing and limitations (developers.cloudflare.com)](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/) — 静的アセットへのリクエストは無料・無制限、`run_worker_first` の扱い `[MCP]`
> - [Workers Pricing (developers.cloudflare.com)](https://developers.cloudflare.com/workers/platform/pricing/) — Workers Paid は月 $5 から、Workers Caching を有効にした場合の課金 `[MCP]`
> - [Workers Limits (developers.cloudflare.com)](https://developers.cloudflare.com/workers/platform/limits/) — リクエスト数・静的アセットのファイル数・`_headers` / `_redirects` の上限 `[MCP]`
> - [Workers Builds: Limits & pricing (developers.cloudflare.com)](https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/) — ビルド時間と同時ビルド数 `[MCP]`
> - [Workers custom domains (developers.cloudflare.com)](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/) — Cloudflare のゾーンが必要、証明書の自動発行、ワイルドカード不可 `[MCP]`
> - [DNS zone setups (developers.cloudflare.com)](https://developers.cloudflare.com/dns/zone-setups/) / [Partial setup (developers.cloudflare.com)](https://developers.cloudflare.com/dns/zone-setups/partial-setup/) — Free / Pro は full setup のみ、partial は Business 以上 `[MCP]`
> - [Pages: Redirecting www to domain apex (developers.cloudflare.com)](https://developers.cloudflare.com/pages/how-to/www-redirect/) — Bulk Redirects による www の転送 `[MCP]`
> - [workers.dev (developers.cloudflare.com)](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/) — 本番は独自ドメインで運用する推奨 `[MCP]`
> - [Build branches / Previews (developers.cloudflare.com)](https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/) — ブランチごとのプレビュー `[MCP]`
> - [Migrate from Pages (developers.cloudflare.com)](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) — Pages と Workers の機能差 `[MCP]`
> - [Pages Limits (developers.cloudflare.com)](https://developers.cloudflare.com/pages/platform/limits/) — ビルド回数・ファイル数・プロジェクト数 `[MCP]`
> - [Pages Functions pricing (developers.cloudflare.com)](https://developers.cloudflare.com/pages/functions/pricing/) — Pages の静的リクエストは無料・無制限 `[MCP]`
> - [Pages custom domains (developers.cloudflare.com)](https://developers.cloudflare.com/pages/configuration/custom-domains/) — サブドメインなら Cloudflare のゾーン不要 `[MCP]`
> - [Service-Specific Terms: Developer Platform (cloudflare.com)](https://www.cloudflare.com/service-specific-terms-developer-platform/) — 対象製品（Workers・Pages ほか）、コンテンツのホスト、過大な負荷での一時的な制限 `[Web]`
> - [Service-Specific Terms: Application Services (cloudflare.com)](https://www.cloudflare.com/service-specific-terms-application-services/) — CDN で動画や大きなファイルを配る場合の条件 `[Web]`
> - [Deno is joining Cloudflare (deno.com)](https://deno.com/blog/cloudflare) — Deno Deploy の終了（[others.md](others.md) で扱う） `[Web]`
>
> 最終更新: 2026-11-14（独自ドメイン・サブドメインで運用する場合の仕様を追加）

`[MCP]` は提供元の公式ドキュメント MCP（Cloudflare docs MCP）経由、`[Web]` は公式ページを直接読んだ記述を指す。横断の比較と結論は [静的サイトホスティングの選び方](../static-hosting.md) にまとめている。

---

## 1. Workers Static Assets と Pages のどちらを使うか

**新規なら Workers Static Assets を使う。** Workers Best Practices は次のように書く。

> Workers Static Assets is the recommended way to deploy static sites, single-page applications, and full-stack apps on Cloudflare. If you are starting a new project, use Workers instead of Pages. Pages continues to work, but new features and optimizations are focused on Workers.

- Pages は**廃止ではない**。終了日は告知されておらず、2026-08 にも機能追加がある。ただし Pages のドキュメントの冒頭には「Workers で新規プロジェクトを始めるように」という案内が出ている。
- 純粋な静的サイトなら Worker のスクリプトは要らない。設定ファイルで `assets.directory` にビルド出力のディレクトリを指定するだけで配信できる（"No Worker script is needed."）。

```jsonc
// wrangler.jsonc（静的サイトの最小構成）
{
  "name": "my-static-site",
  "compatibility_date": "2026-11-14", // 作成する日の日付にする（公式の例も "Set this to today's date"）
  "assets": { "directory": "./dist" }
}
```

両者の主な違い:

| | Workers Static Assets | Pages |
|---|---|---|
| 公式の位置づけ | 推奨（新機能はこちら） | 継続提供（新規は非推奨） |
| 既定のドメイン | `<name>.<subdomain>.workers.dev` | `<project>.pages.dev` |
| 独自ドメイン | Cloudflare に DNS を置いたゾーンが必要 | サブドメインなら CNAME だけで可（apex は Cloudflare のゾーンが必要） |
| ビルドの上限（Free） | Workers Builds: 月 3,000 分・同時 1・1 回 20 分 | 月 500 回・同時 1・1 回 20 分 |
| プレビュー | 本番以外のブランチごとに Preview URL（PR にコメント） | プレビューデプロイ無制限 |

## 2. 料金（静的サイトなら無料のまま）

> Requests to static assets are free and unlimited. Requests to the Worker script (for example, in the case of SSR content) are billed according to Workers pricing.

- **静的ファイルへのリクエストは、無料プランでも有料プランでも無料・無制限。** 保存にも費用はかからない（"There is no additional cost for storing Assets."）。
- **転送量（egress）は課金されない。** 料金ページは "There are no additional charges for data transfer (egress) or throughput (bandwidth)." と明記している。Workers の課金対象はリクエスト数と CPU 時間である。
- 無料プランの「1 日 100,000 リクエスト」は Worker のスクリプトを動かすリクエストの上限である。`run_worker_first` を設定してスクリプトを先に動かす経路だけが、上限超過で HTTP 429 になる。静的ファイルの配信は止まらない。
- 例外: **Workers Caching を有効にすると、キャッシュから返した静的アセットのリクエストも課金対象になる**（Pricing の脚注）。静的サイトでは有効にしない。
- 有料の Workers Paid は月 $5（最低料金）。静的サイトで上げる理由は、ファイル数の上限（20,000 → 100,000）とビルドの枠くらいである。

## 3. 制限

| 項目 | Free | 有料 |
|---|---|---|
| 静的アセットのファイル数（1 バージョン） | 20,000 | 100,000（Wrangler 4.34.0 以上） |
| 1 ファイルの最大サイズ | 25 MiB | 25 MiB |
| `_redirects` | 静的 2,000 + 動的 100 | 同じ |
| `_headers` | 100 ルール | 同じ |
| Worker の数（アカウント） | 100 | 500 |
| Workers Builds | 月 3,000 分・同時 1 | 月 6,000 分（超過 $0.005/分）・同時 6 |
| Pages のビルド | 月 500 回・同時 1 | Cloudflare の Pro プランで月 5,000 回（Workers Paid の $5 では増えない） |
| Pages のファイル数 | 20,000 | 100,000（`PAGES_WRANGLER_MAJOR_VERSION=4` の設定が要る） |
| Pages のプロジェクト数 | 100（アカウント） | 同じ |

- 25 MiB を超えるファイルは R2 に置くよう公式が案内している。
- **ファイル数の上限は、ページが増え続けるサイトで効いてくる。** 1 ページあたり HTML 1 枚 + 画像数枚なら、1 ページ 5 ファイルなら、毎日 1 ページの追加で 20,000 ファイルに届くまで約 11 年かかる（[cost-estimates.md §4](cost-estimates.md#4-毎日-1-ページ追加するサイトの容量ファイル数)）。

## 4. 商用利用

- 無料プランを非商用に限る条文は見当たらない。Developer Platform の規約は Workers と Pages を対象製品に含め、"Unlike most Cloudflare products, the Developer Platform can be used to host content." とする。
- 同じ規約は、処理が "an undue burden on the Cloudflare network" になる場合に、保存量やリクエスト数を一時的に制限できるとしている。「無料・無制限」は課金の話であり、極端な負荷まで保証するものではない。
- `workers.dev` のサブドメインは "intended for personal or hobby projects that aren't business-critical" とされる。**収益化するサイトは独自ドメインで運用する。**
- CDN の規約は、Enterprise 以外が **動画や大きなファイルの配信が大半を占める使い方** をする場合、Developer Platform・Images・Stream などの有料サービスを使うよう求めている。Workers / Pages は上記のとおり Developer Platform に含まれるが、無料プランの Workers がこの "Paid Services" に当たるかは、規約からは判断できない（未確認）。HTML と通常の画像が中心のサイトなら問題にならない。

## 5. 独自ドメインで運用する場合

**Workers と Pages で、DNS を Cloudflare に移す必要があるかが違う。**

| 項目 | Workers Static Assets | Pages |
|---|---|---|
| 独自ドメイン（apex: `example.com`） | ドメインを Cloudflare のゾーンにする必要がある（ネームサーバーを Cloudflare に移す） | 同じく Cloudflare のゾーンが必要（"you will need to add your site as a Cloudflare zone and configure your nameservers"） |
| サブドメイン（`www.example.com` など） | **これも Cloudflare のゾーンが必要。** DNS を他社に置いたままでは使えない | **DNS を他社に置いたまま、CNAME で `<project>.pages.dev` を指せば使える**（"it is not necessary for your site to be a Cloudflare zone"）。先に Pages のダッシュボードでドメインを追加する（順番を逆にすると 522 エラー） |
| DNS レコード | Cloudflare が自動で作る | apex とゾーン内のサブドメインは Cloudflare が作る（apex は CNAME flattening） |
| HTTPS | 証明書を自動発行（"Creating a Custom Domain will also generate an Advanced Certificate"） | 証明書を自動発行。CAA を使う場合は `letsencrypt.org`・`pki.goog`・`ssl.com` を許可する |
| apex と www の転送 | 自動では無い。Redirect Rules を作るか、両方のホスト名を Worker に付ける | 自動では無い。Bulk Redirects で www → apex の 301 を作る手順が公式にある |
| 上限（Free） | 1 ゾーンに Custom Domains 100 個。ワイルドカードは不可 | 1 プロジェクトに独自ドメイン 100 個。ワイルドカードは不可 |
| 費用 | 無料プランのゾーンで使える。追加料金の記載なし | 同じ |

- **無料プランで「DNS は他社のまま、一部だけ Cloudflare」にする方法は無い。** DNS を他社に残す CNAME setup（partial）は "only available to customers on a Business or Enterprise plan" で、Free / Pro は full setup（ネームサーバーの移管）だけである。
- Workers の Custom Domains は、既に CNAME レコードがあるホスト名には作れない。既存のレコードを消してから追加する。

## 6. 向いている用途

- 転送量が読めない、または大きくなりうるサイト。静的配信が無料・無制限なので、アクセスが増えても費用が変わらない。
- 広告やアフィリエイトで収益化するサイト（独自ドメインで運用）。
- 毎日更新するサイト。月 3,000 分のビルド枠は、1 回 5 分のビルドを毎日しても 150 分で収まる。
