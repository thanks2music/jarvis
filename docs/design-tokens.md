# デザイントークン — 概念・規格・AI への渡し方

> 出典:
> - [Design Tokens Format Module 2025.10 — designtokens.org](https://www.designtokens.org/tr/2025.10/format/) — 仕様本文。`$value` / `$type` / エイリアス / 型 / グループ
> - [Design Tokens specification reaches first stable version — w3.org](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/) — 2025-10-28 の安定版到達告知、参加企業、参照実装
> - [Design Tokens Community Group — Style Dictionary Docs](https://styledictionary.com/info/dtcg/) — Style Dictionary の DTCG 対応状況
> - [Modes for variables — help.figma.com](https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables) — Figma Variables の入出力とプラン条件
> - [registry-item.json — ui.shadcn.com](https://ui.shadcn.com/docs/registry/registry-item-json) — registry によるトークン配布
>
> 最終更新: 2026-09-13

デザイントークンは、Claude Design / Figma Make / v0 / Google Stitch といった AI デザインツールに
「自分たちの意匠」を食わせるための**共通の入力形式**である。ツールごとの仕様は
[AI デザイン制作ツール](ai-design-tools.md) を SSOT とし、本ドキュメントは
**概念と規格、および正本の置き場所の設計**に絞る。

---

## 1. TL;DR

- **デザイントークンとは**、「色 `#0B5FFF`」のような生の値ではなく「`color.action.primary` という名前の決定」を、ツール非依存の形式で持つもの。名前と値の対応表であり、デザインツールとコードの両方から同じものを参照できる点に価値がある。
- **2025-10-28、DTCG（Design Tokens Community Group）が初の安定版 `2025.10` を公開した**。Adobe / Amazon / Google / Microsoft / Meta / Figma / Sketch / Shopify など 20 社超が参加している。
- ⚠️ **ただしこれは「W3C 標準」ではない**。W3C Community Group の Final Report であり、W3C 勧告（Recommendation）ではない。§3.5 を参照。
- ⚠️ **変換ツールの追随は完了していない**。デファクトの Style Dictionary は v4 で DTCG を first-class サポートするが、`2025.10` への完全対応は **v5 で作業中**である。
- 設計判断の本体は「**正本（source of truth）をどこに置くか**」の一択に集約される。現実的な置き場は Figma / コード / 中立な JSON の 3 つ（§4）。
- AI ツールはいずれも「デザインシステムを食わせる口」を持っている。裸で使うと毎回ゼロから発明するが、繋げば既存の意匠に従う（§5）。

---

## 2. デザイントークンとは何か

### 2.1 定義

DTCG の定義では、デザイントークンは「人間が読める名前に紐づいた情報」であり、最小構成は**名前と値のペア**である。

```
color-text-primary: #000000
font-size-heading-level-1: 44px
```

重要なのは値そのものではなく、**「この決定に名前を付けて、複数のツール・プラットフォームで共有する」という構造**のほうである。仕様はこれを「プラットフォーム非依存の形式で設計上の決定を表現し、分野・ツールを横断して共有するもの」と位置づけている。

### 2.2 CSS 変数・Figma スタイルとの違い

| | スコープ | 読める相手 | 型情報 |
|---|---|---|---|
| CSS カスタムプロパティ | ブラウザ / Web のみ | ブラウザ、コード | なし（すべて文字列） |
| Figma のスタイル・変数 | Figma ファイル内 | Figma、Figma API | Figma 独自の型 |
| **デザイントークン（DTCG）** | **ツール非依存** | **仕様に対応した全ツール** | **`$type` で明示** |

CSS 変数は「Web の実装手段」であり、Figma スタイルは「Figma の内部表現」である。どちらも**それ単体では他方へ渡せない**。デザイントークンはこの往復のための中間形式にあたる。

> **ポイント**: 単一プラットフォームの個人開発であれば、CSS 変数（Tailwind v4 の `@theme` 等）だけで十分に足りる。トークン規格が効き始めるのは「2 つ目のプラットフォームが現れたとき」か「デザインツールとコードの往復が発生したとき」である。

### 2.3 プリミティブ / セマンティック / コンポーネントの 3 層

実務で使われる層構造。DTCG 仕様が規定するものではなく、**エイリアス機能（§3.4）を使って組み立てる慣行**である。

| 層 | 例 | 役割 |
|---|---|---|
| プリミティブ（Global / Core） | `color.blue.500 = #0B5FFF` | 素の値のパレット。意味を持たない |
| セマンティック（Alias） | `color.action.primary = {color.blue.500}` | 用途に名前を与える。テーマ切替はここで吸収する |
| コンポーネント | `button.primary.background = {color.action.primary}` | 個別コンポーネント固有の決定 |

この 3 層に分けておくと、ダークモードやブランド差し替えの際に**セマンティック層の参照先だけを差し替えればよくなる**。プリミティブを直接コンポーネントから参照すると、この切り替え点が失われる。

---

## 3. DTCG 2025.10 — 初の安定版

### 3.1 2025-10-28 に何が起きたか

Design Tokens Community Group が、仕様の初の安定版 `2025.10` を公開した。告知は安定版の中身を 3 点にまとめている。

1. **Theming and multi-brand support** — ライト/ダーク、アクセシビリティ対応、ブランドテーマをファイル複製なしで扱える（⚠️ §3.6 に注意点あり）
2. **Modern color specification** — Display P3、Oklch、CSS Color Module 4 の全色空間に対応
3. **Rich token relationships** — 継承、エイリアス、コンポーネント単位の参照

参照実装は **Style Dictionary / Tokens Studio / Terrazzo** の 3 つ。対応済みまたは実装中のデザインツールは 10 以上あり、Penpot / Figma / Sketch / Framer / Knapsack / Supernova / zeroheight が挙げられている。

参加企業は 20 社超。Adobe、Amazon、Google、Baidu、Sony、Microsoft、Meta、Sketch、Salesforce、Shopify、Figma、Framer、Cisco、Intuit、New York Times、GM、Disney、Anima、Pinterest、Tokens Studio、Penpot、Knapsack、Supernova、zeroheight ほか。

### 3.2 仕様の構成

仕様本文（Final Community Group Report、2025-10-28 公開）は「This specification is considered stable」と明記している。目次は以下の 9 章。

| 章 | 内容 |
|---|---|
| Conformance | 適合性の定義 |
| Introduction | 位置づけと目的 |
| Terminology | 用語定義 |
| File format | JSON をベースとするファイル形式 |
| Design token | トークン 1 件の構造（§3.3） |
| Groups | グループ化と継承（§3.5） |
| Aliases / References | 参照の 2 記法（§3.4） |
| Types | プリミティブ型（§3.3） |
| Composite types | 複合型（§3.3） |

### 3.3 トークン 1 件の構造と型

すべてのトークンは以下のプロパティを持つ。`$` 接頭辞が予約語であることが DTCG 形式の外見上の特徴である。

| プロパティ | 必須 | 内容 |
|---|---|---|
| `$value` | ⭕ | トークンの値本体 |
| `$type` | ⭕（グループから継承する場合は省略可） | `color` / `dimension` 等のカテゴリ |
| `$description` | ❌ | 用途を説明する平文 |
| `$extensions` | ❌ | ベンダー固有データ。逆ドメイン記法で名前空間を切る |
| `$deprecated` | ❌ | 真偽値、または非推奨理由の文字列 |

**プリミティブ型**: `color`（`colorSpace` / `components` / `alpha` / `hex` を持つオブジェクト）、`dimension`（数値 + `px` または `rem`）、`fontFamily`（文字列または配列）、`fontWeight`（1〜1000、または `bold` 等の別名）、`duration`（数値 + `ms` または `s`）、`cubicBezier`（4 数値の配列）、`number`（単位なし）。

**複合型（composite）**: `shadow`、`border`、`strokeStyle`、`transition`、`gradient`、`typography`。複数のプリミティブをまとめた 1 つの決定として扱う。

> **色がオブジェクトになった点は破壊的**。旧来の `"#0B5FFF"` という文字列ではなく `colorSpace` / `components` を持つオブジェクトになったことが、Display P3 / Oklch 対応の実体である。変換ツール側の対応が遅れる主因もここにある（§4.4）。

### 3.4 エイリアス — 2 つの記法

トークンは他のトークンを参照できる。仕様は**2 つの記法を定め、ツールは両方をサポートしなければならない**としている。

| 記法 | 形 | 参照先 |
|---|---|---|
| 波括弧 | `{colors.blue}` | トークン全体。自動的に `$value` へ解決される |
| JSON Pointer | `$ref: "#/colors/blue/$value"` | プロパティ単位。RFC 6901 準拠 |

参照の連鎖（参照先がさらに参照）は可能だが、**循環参照は禁止でエラーにしなければならない**。

### 3.5 グループと `$extends`

グループは**組織化のためだけのもの**で、型を強制しない。仕様は「ツールはグループへの所属からトークンの型を推論すべきではない」と明記している。

- `$extends` — 別のグループからトークンとプロパティを継承する（JSON Schema の `$ref` 相当）
- `$root` — グループ内に、子トークンと並ぶ「そのグループ自体の値」を置ける予約名
- 継承はディープマージ。同一パスではローカル定義が継承元を上書きし、異なるパスは共存する

### 3.6 ⚠️ 「W3C 標準」ではない — 2 つの注意点

**(1) W3C 勧告ではない。** `2025.10` は **Final Community Group Report**（2025-10-28）であり、仕様本文自身が以下を明記している。

> While not a W3C recommendation, this classification is intended to clarify that, after extensive consensus-building, this specification is intended for implementation.

「W3C 標準になった」と書く二次情報が散見されるが、正確には「W3C のコミュニティグループが、実装を意図した安定版を出した」である。実務上の影響は小さい（主要ベンダーが揃って支持しているため）が、社内説明で「W3C 標準」と称すると誤りになる。

**(2) テーマ / モードの専用機構は仕様本文に存在しない。** 告知は "Theming and multi-brand support" を安定版の目玉に挙げているが、**仕様本文には `$modes` のようなテーマ専用プロパティも、モードを表す章も存在しない**。実現手段は §3.5 の `$extends`（ベースグループを継承して差分だけ上書き）と `$extensions`（ツール固有の拡張）である。

> **検証方法**: 仕様本文の HTML 全文（約 356,000 文字）を取得し、`theming` と `$modes` を全文検索したところ **いずれもヒット 0 件**だった（2026-09-13 実測）。

> **2026-09-13 時点の確認結果**: 告知文と仕様本文のあいだにこの温度差がある。「DTCG がテーマ機構を標準化した」と理解すると、実装時に期待した機能が見つからない。**テーマ切替は `$extends` による構造化か、Figma Variables のモード（§5.2）のようなツール側の機構に依存する**、と理解しておくのが正確である。

---

## 4. 正本（source of truth）をどこに置くか — 3 系統

デザイン管理の設計は、突き詰めると「**正本をどこに置き、他をどう従わせるか**」に集約される。現実的な置き場は 3 つ。

### 4.1 A: Figma を正本にする

```
Figma Variables（正本）
  ├─ Export modes（JSON）      → コードの CSS 変数 / Tailwind
  ├─ Code Connect              → 実装コンポーネントと相互参照
  ├─ Figma MCP                 → Claude Code / Cursor が設計を読んで実装
  └─ Make kits                 → Figma Make が同じライブラリで生成
```

- **向くケース**: 人間が Figma で絵を描く時間が長い。デザイナーが複数いる
- **必要なもの**: Variables のモードは **Education / Professional / Organization / Enterprise プラン限定**（無料の Starter は対象外）
- **弱点**: Figma を開かないと正本が読めない。Git の差分レビューに乗らない

### 4.2 B: コードを正本にし、registry で配る

```
コードのコンポーネント + トークン（正本）
  └─ shadcn registry（HTTP で JSON を配信）
       ├─→ v0 が消費（Design Systems 2.0 の source として）
       ├─→ MCP 経由で Cursor / Claude Code が消費
       └─→ CLI がファイルを書き込む
```

shadcn の registry は、`registry.json` に `items[]` を並べ、各 item が `registry-item.json` スキーマに従う仕組み。トークンは **`cssVars`**（`theme` / `light` / `dark` の 3 区画）として運ばれる。

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "type": "registry:block",
  "registryDependencies": ["button", "@acme/input-form", "https://example.com/r/foo"],
  "cssVars": {
    "theme": { "font-heading": "Poppins, sans-serif" },
    "light": { "brand": "oklch(0.205 0.015 18)" },
    "dark":  { "brand": "oklch(0.205 0.015 18)" }
  }
}
```

`registryDependencies` が `@acme/input-form` という**名前空間付き参照**と**完全 URL** の両方を受けるため、自前の private registry を混ぜて配布できる。

- **向くケース**: 実装者が少人数でコードが主戦場。AI ツールを複数使い分ける
- **必要なもの**: shadcn/ui ベースのコンポーネント構成、registry のホスティング
- **弱点**: Figma 側が「絵」に留まり、デザインの意思決定がコードレビューに乗る

### 4.3 C: DTCG JSON を中立の正本にする

```
DTCG JSON（正本・Git 管理）
  ├─ Style Dictionary → CSS 変数 / Tailwind / iOS / Android
  └─ Figma へ import  → Variables として反映（Export modes で逆も可）
```

- **向くケース**: 複数プラットフォーム（Web + ネイティブアプリ）を持つ。ツールの乗り換えを前提にする
- **弱点**: ⚠️ §4.4 の通り、**変換ツールが `2025.10` に未対応**

### 4.4 ⚠️ 変換ツールの追随状況（採用可否に直結する）

Style Dictionary の公式ドキュメントは以下を明記している。

> As of version 4, Style Dictionary has first-class support for the DTCG format.

> the latest format 2025.10 does not have full support yet in Style Dictionary. This is a work in progress in v5

つまり **2026-09-13 時点で、DTCG `2025.10` をそのまま流し込める変換パイプラインは既製品として存在しない**。選択肢 C を今すぐ採るなら、旧フォーマットで妥協するか、変換層を自作することになる。

補足として、Style Dictionary v4 の仕様上の制約も押さえておく。

- DTCG 形式（`$value` / `$type` / `$description`）と独自形式（`value` / `type` / `comment`）の**どちらも使えるが、1 インスタンスにつき 1 形式**。公式は「In version 4 you can use either format, pick one though as they cannot be combined inside a single Style Dictionary instance.」と明記している
- 相互変換ユーティリティとして `convertToDTCG` / `convertJSONToDTCG` がある。ただし `convertToDTCG` を **Preprocessor フック内で既定設定のまま使ってはならない**（`typeDtcgDelegate` と逆方向の操作になるため）

### 4.5 判断軸

| 問い | A: Figma | B: コード + registry | C: DTCG JSON |
|---|---|---|---|
| プラットフォームは Web だけか | ⭕ | ⭕ | ❌ 過剰 |
| Web + ネイティブがあるか | △ | ❌ | ⭕ |
| 絵を描く人間が複数いるか | ⭕ | ❌ | △ |
| 実装者が 1 人でコードが主戦場か | ❌ | ⭕ | △ |
| Git の差分レビューに乗せたいか | ❌ | ⭕ | ⭕ |
| 2026-09-13 時点で既製品が揃うか | ⭕ | ⭕ | ⚠️ §4.4 |

> **ポイント**: 「いずれ必要になるから」で C を先取りすると、変換層の自作コストを先払いすることになる。**2 つ目のプラットフォームが実在してから移る**判断で足りる。

---

## 5. AI ツールへの「食わせる口」

4 ツールすべてが、デザインシステムを受け取る口を持っている。**繋がなければ、生成のたびに意匠が変わる。** 各ツールの詳細仕様は [AI デザイン制作ツール](ai-design-tools.md) を参照し、ここでは「トークンがどの形で入るか」だけを並べる。

| ツール | 口 | 受け取る形 |
|---|---|---|
| **Claude Design** | デザインシステム型プロジェクト | GitHub repo / デザインファイル / raw upload / ローカルコードベース。`is_default=true` のものが新規プロジェクトに自動適用される |
| **Figma Make** | Make kits | npm パッケージ + 公開済み Figma ライブラリの**変数・スタイル** + guidelines（Markdown） |
| **v0** | Design Systems 2.0 の source | GitHub repo / Figma フレーム・ノード / Storybook・docs へのリンク / `.tgz` 等の添付。旧方式は shadcn registry |
| **Google Stitch** | `DESIGN.md` | 色・タイポグラフィ・スペーシング・コンポーネントパターンを記述した Markdown。プロジェクト間で入出力できる |

### 5.1 共通する性質

- **どれも DTCG JSON を直接の入力形式にしていない。** 各ツールが自前の表現（Claude Design のデザインシステムプロジェクト、Make kit、v0.json、DESIGN.md）を持つ
- **一方で、どれも「コードそのもの」を受け取れる。** GitHub repo / npm パッケージ / ローカルコードベースが共通の入り口になっている
- つまり **2026-09-13 時点では、選択肢 B（コードを正本にする）が AI ツールとの相性で最も広く通る**

### 5.2 Figma Variables の入出力（選択肢 A と C の接続点）

Figma はプラグイン不要でトークンの往復ができる。

- **書き出し**: Variables ビューでモードを右クリック →「Export mode」。コレクションごとなら「Export modes」で JSON が出る
- **読み込み**: JSON をドラッグ&ドロップで新規コレクション作成、またはモードを右クリック →「Import mode」で既存モードを更新
- ⚠️ **読み込みは DTCG フォーマット必須**。「Design tokens must be in a JSON file and follow the Design Tokens Community Group (DTCG) format」
- 取り込み時、ネストしたグループ名はスラッシュに正規化される（`color.accent.light` → `color/accent/light`）
- `$extensions` のうち Figma 固有のキーは `com.figma` 接頭辞が付く。`com.figma.aliasData` で別コレクションの変数をエイリアス参照できる
- 取り込み時にサポートされる型: color / dimension / font family / duration / number / string
- ⚠️ **プラン制約**: Variables のモードを作成・使用できるのは **Education / Professional / Organization / Enterprise** プラン。**無料の Starter プランは対象外**

---

## 6. 既存ドキュメントとの関係

| ドキュメント | 何の SSOT か |
|---|---|
| 本ドキュメント | デザイントークンの**概念と規格**、正本の置き場所の設計 |
| [AI デザイン制作ツール](ai-design-tools.md) | 各 AI デザインツールの**仕様と現在地** |
| [デザインワークフロー](design-workflow.md) | 「どのツールをいつ使うか」の**選択指針**と外部ツールの採否基準 |
| [使用ツールスタック](tool-stack.md) | 「何を導入済みか」の棚卸し |

---

## 7. 出典

### 一次情報

| 出典 | URL |
|---|---|
| Design Tokens Format Module 2025.10（Final Community Group Report） | https://www.designtokens.org/tr/2025.10/format/ （2026-09-13 確認） |
| Design Tokens specification reaches first stable version（2025-10-28） | https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ （2026-09-13 確認） |
| Design Tokens Community Group | https://www.designtokens.org/ （2026-09-13 確認） |
| Style Dictionary — Design Tokens Community Group | https://styledictionary.com/info/dtcg/ （2026-09-13 確認、Context7 `/style-dictionary/style-dictionary` 経由） |
| Style Dictionary — DTCG Utils（`convertToDTCG` 等） | https://styledictionary.com/reference/utils/dtcg/ （2026-09-13 確認、Context7 経由） |
| Style Dictionary — Design Tokens（形式の混在不可） | https://styledictionary.com/info/tokens/ （2026-09-13 確認） |
| Modes for variables — Figma Help Center | https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables （2026-09-13 確認） |
| registry-item.json — shadcn/ui | https://ui.shadcn.com/docs/registry/registry-item-json （2026-09-13 確認、Context7 `/websites/ui_shadcn` 経由） |
| registry.json — shadcn/ui | https://ui.shadcn.com/docs/registry/registry-json （2026-09-13 確認、Context7 経由） |

### 確認できなかった事項

- **Figma Variables のプラン別モード上限数**。公式ヘルプは「the number of modes you can create per variable collection depends on your plan」と述べるのみで、当該記事に具体的な数値の記載がない。数値は掲載しない
- **DTCG `2025.10` のテーマ機構**。§3.6 の通り、告知文と仕様本文で記述に温度差がある。仕様本文側を正として扱った

- 関連: `docs/ai-design-tools.md` / `docs/design-workflow.md`
