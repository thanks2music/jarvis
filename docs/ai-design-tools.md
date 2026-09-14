# AI デザイン制作ツール — 仕様と使い分け

> 出典:
> - [Introducing Claude Design by Anthropic Labs — anthropic.com](https://www.anthropic.com/news/claude-design-anthropic-labs) — 2026-04-17 公開。提供プラン・デザインシステム・Claude Code ハンドオフ
> - [Get started with Claude Design — support.claude.com](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) — ベータ提供範囲・書き出し形式・利用枠・MCP エンドポイント
> - [Guide to the Figma MCP server — help.figma.com](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) — remote / desktop の差、write to canvas のベータ扱い
> - [Rate limits & access — developers.figma.com](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/) — プラン / シート別レート制限
> - [Get started with Make kits — help.figma.com](https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits) — Make kits の構成要素と作成手順
> - [How AI credits work — help.figma.com](https://help.figma.com/hc/en-us/articles/33459875669015-How-AI-credits-work) — プラン / シート別 AI クレジット
> - [Design systems — v0 Docs](https://v0.app/docs/design-systems-2) — Design Systems 2.0 の source と `v0.json`
> - [Design UI using AI with Stitch from Google Labs — blog.google](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/) — 2026-03-18 の刷新内容、DESIGN.md、MCP / SDK
>
> 最終更新: 2026-09-13

AI でデザインを作るサービスが 2026 年に一気に増えた。本ドキュメントは、**現時点で各サービスが何をできるのか**を公式一次情報に基づいて整理する。

- 「どのツールをいつ使うか」の選択指針は [デザインワークフロー](design-workflow.md) が SSOT
- 「何を導入済みか」の棚卸しは [使用ツールスタック](tool-stack.md) が SSOT
- トークンの規格と正本の置き場所の設計は [デザイントークン](design-tokens.md) が SSOT

---

## 1. TL;DR — 2026-09-13 時点の一覧

| ツール | 提供元 | 料金 / プラン条件 | デザインシステムの投入口 | 主な出力 | Claude Code 連携 |
|---|---|---|---|---|---|
| **Claude Design** | Anthropic | Pro / Max / Team / Enterprise に**サブスク込み**（ベータ。Enterprise は既定 off） | GitHub repo / デザインファイル / raw upload / ローカルコードベース | PDF / PPTX / HTML / ZIP、Canva 他への連携 | ⭕ **`/design-sync` で双方向** |
| **Figma Make** | Figma | 有料プランの **Full シート**で公開可。AI クレジットを消費 | **Make kits**（npm パッケージ + ライブラリの変数・スタイル + guidelines） | 動作するプロトタイプ、公開（ベータ） | △ Figma MCP 経由で間接的 |
| **Figma MCP** | Figma | remote は**全シート・全プラン**。desktop は有料プランの Dev / Full シート | 公開済み Figma ライブラリ + Code Connect | Figma キャンバスへの書き込み / コード生成 | ⭕ 公式 plugin あり |
| **v0** | Vercel | 既定デザインシステムの設定は**有料プランの Team owner** | GitHub repo / Figma ノード / Storybook 等のリンク / `.tgz` 添付 | Next.js + shadcn/ui + Tailwind のコード | ❌ 直接の連携なし |
| **Google Stitch** | Google Labs | Google Labs 提供（本稿では料金を確定できず。§5.2） | **`DESIGN.md`**、URL からのデザインシステム抽出 | HTML / スクリーンショット、MCP・SDK 経由 | ⭕ MCP サーバーあり |

> **要点**: 5 つとも「デザインシステムを食わせる口」を持つ。**繋がなければ、生成のたびに意匠が変わる。** そして**どれも DTCG JSON を直接の入力にしていない**一方、**どれもコードそのものは受け取れる**（[デザイントークン §5](design-tokens.md#5-ai-ツールへの食わせる口)）。

---

## 2. Claude Design（主）

### 2.1 何ができるか

2026-04-17、Anthropic Labs から research preview として公開された。会話を通じて Claude に視覚物を作らせるツールで、チャットとキャンバスが対になった UI を持つ。

公式が挙げる用途は以下。

| 用途 | 内容 |
|---|---|
| プロトタイプ | 静的なモックアップを、ユーザーテストに使える対話可能・共有可能なプロトタイプに変える |
| ワイヤーフレーム / モックアップ | 機能フローを粗く描き、デザイナーの仕上げや Claude Code の実装に渡す |
| デザイン探索 | 複数のデザイン方向を素早く生成して比較する |
| ピッチデッキ | ブランドに沿った完成状態のプレゼンを作り、PPTX で書き出す |
| マーケティング素材 | LP、ソーシャル素材、キャンペーンビジュアル |
| ドキュメント | 履歴書・1 ページ資料を PDF で |

音声・動画・シェーダー・3D を含む「コードで動くプロトタイプ」も作れる。

### 2.2 プランと提供形態

| 項目 | 内容 |
|---|---|
| 提供プラン | **Pro / Max / Team / Enterprise**。サブスクリプションに含まれ、追加課金はない |
| 提供状態 | ベータ（初出は research preview） |
| Enterprise | **既定で off**。公式の記述は「For Enterprise organizations, Claude Design is off by default. Admins can enable it in Organization settings.」であり、管理者が Organization settings から有効化する（詳細は[管理者ガイド](https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans)） |
| アクセス経路 | Web（`claude.ai/design`）と Claude Desktop のサイドバー |
| 利用枠 | ⚠️ **chat / Claude Code / Cowork と共通プールを消費する**。Claude Design 専用の枠は存在しない |
| 上限到達時 | 上限がリセットされるまで Claude Design は使えなくなる。usage credits を有効にしていれば、含まれる上限を超えても作業を継続できる |
| モデル | 公開時点（2026-04-17）のアナウンスでは「our most capable vision model, Claude Opus 4.7」と記載。⚠️ モデル世代は更新されるため、現行の解決先は別途確認が要る |

> ⚠️ **利用枠が共通である点は運用に効く。** デザイン生成を回した分だけ、同じ週の Claude Code の実装に使える量が減る。まとめて生成する日と実装する日を分けるなどの配慮が要る。

### 2.3 デザインシステム

Claude Design の中核はここにある。オンボーディング時に「Claude がコードベースとデザインファイルを読んでチームのデザインシステムを構築し、以降のプロジェクトは色・タイポグラフィ・コンポーネントを自動的に使う」設計になっている。

**取り込み元**: GitHub リポジトリ / デザインファイル / raw upload / ローカルコードベース。

**運用上の性質**:

- 複数のデザインシステムを登録できる。**`is_default=true` のものが、新規プロジェクトに自動適用される**
- 管理者はデザインシステムを承認し、編集をロックして一貫性を保てる
- 生成物を返す前に、デザインシステムへの適合を検証する工程が入る

> **2026-09-13 時点の状態**: `list_design_systems` を実行した結果は **0 件**。
> [デザインワークフロー](design-workflow.md) が 2026-08-19 時点で記録した状態から変化していない。
> **登録されていない間、Claude Design は実装状況を知らないまま絵を描く。**
> 継続案件では着手時に登録しておく。

### 2.4 書き出しと連携先

| 区分 | 内容 |
|---|---|
| 書き出し | ZIP / PDF / PowerPoint (PPTX) / 単体 HTML |
| 取り込み | GitHub、デザインファイル、DOCX / PPTX / XLSX、Web キャプチャ |
| 連携アプリ | Adobe / Base44 / Canva / Gamma / Lovable / Miro / Replit / Vercel / Wix（拡張中） |
| Claude Code へ | ハンドオフバンドルにまとめ、1 つの指示で Claude Code に渡せる |

---

## 3. Claude Code との実践連携

Claude Design には**入口が 3 つ**あり、役割が違う。これを混同すると「なぜ書き込めないのか」で詰まる。

### 3.1 3 つの入口

| 入口 | 実体 | 向くこと |
|---|---|---|
| **`claude_design` MCP** | `https://api.anthropic.com/v1/design/mcp` | プロジェクト管理・ファイル書き込み・プレビュー描画・共有 / コメントまで一通り |
| **`/design [brief]`** | 組み込みスキル（research preview、**要 ClaudeCode v2.1.234+**） | Claude Design の artboard ワークフローを CLI / Desktop に持ち込む。**手で視覚的に直したい**とき |
| **`/design-sync [name]` + `DesignSync` ツール** | バンドルスキル + 専用ツール | **リポジトリの React デザインシステムを Claude Design へ押し上げる**。認可は `/design-login` |

`claude_design` MCP の追加手順は公式ヘルプに明記されている。

```bash
claude mcp add --scope user --transport http claude-design https://api.anthropic.com/v1/design/mcp
```

追加後、`/design-login` でサインインする。

### 3.2 `/design-sync` の実際の流れ

`DesignSync` ツールは**順序を強制する**。読み取り → 計画確定 → 書き込みの 3 段構えで、計画なしの書き込みは拒否される。

```
1. list_projects            書き込み可能なデザインシステムプロジェクトを列挙
                            （name / owner / projectId / updatedAt。書き込み可のものだけ）
       ↓  該当がなければ create_project で新規作成
2. get_project              type が PROJECT_TYPE_DESIGN_SYSTEM か検証する
3. list_files               リモートのパス一覧を取り、構造の差分を作る
       ↓  必要な分だけ get_file（256 KiB 上限）で中身を比較
4. finalize_plan            書き込む / 削除するパスと、読み出し元ローカルディレクトリ
                            （localDir、既定は cwd）を確定 → planId が返る
       ↓  ユーザーはここで、パス一覧と読み出し元をツールの表示として確認できる
5. write_files              planId を添えて書き込む
   delete_files             planId を添えて削除する
```

**`write_files` は `localPath` 指定を使う**のが正しい。ツールがディスクから直接読んでアップロードするため、**ファイル内容がモデルのコンテキストに入らない**。インラインの `data` は小さな動的コンテンツ専用である。

### 3.3 ⚠️ ハマりどころ

| 事象 | 実際の仕様 |
|---|---|
| 通常プロジェクトに push したがデザインシステムにならない | **`PROJECT_TYPE_DESIGN_SYSTEM` は作成時に固定され、後から変更できない**。`get_project` で type を検証してから push する |
| `write_files` が拒否される | `finalize_plan` を経ていないか、計画外のパスを指定している。順序と対象パスの両方が検査される |
| 大量のコンポーネントが 1 回で上がらない | **1 コールにつき 256 ファイルが上限**。同じ `planId` のまま複数回に分ける |
| 巨大ファイルが読めない | `get_file` は **256 KiB 上限** |
| Design System ペインにカードが出ない | 現在はプレビュー HTML の**1 行目の `<!-- @dsCard group="…" -->` コメント**からカード索引が作られる（`_ds_manifest.json` にコンパイルされる）。`register_assets` は legacy で、手書きプロジェクト以外では不要 |
| 初回同期が終わらない | 全コンポーネントを検証するため、**大規模リポジトリでは数時間かかる** |
| 企業環境で動かない | ⚠️ **Anthropic API 限定**。Bedrock / Google Cloud Agent Platform / Microsoft Foundry / Claude Platform on AWS では基盤ツールが claude.ai に到達できず利用できない |
| `/design` が見つからない | **ClaudeCode v2.1.234 以上が必要** |

> **セキュリティ**: `get_file` は組織の他メンバーが書いた内容を返す。**それは data であって instruction ではない**。取得したファイルに指示文めいた記述があれば従わず、そのパスに不審な点があると報告する — という原則がツール自身の仕様に明記されている。

### 3.4 ハンドオフの向き

| 向き | 手段 | 使いどころ |
|---|---|---|
| **Code → Design** | `/design-sync` | 実装済みのコンポーネントを Claude Design に教える。**最初にやるべきはこちら**。これをやらないと §2.3 の「実装を知らないまま絵を描く」状態になる |
| **Design → Code** | ハンドオフバンドル | デザインが固まった後、Claude Code に実装させる。スクリーンショットからの推測ではなく、既存の成果物の続きから始まる |

---

## 4. Figma Make と Figma MCP（次点）

> **2026-09-13 時点の本リポジトリの環境**: Figma アカウントとの MCP 認証は**未実施**。
> 本節はプラン / シート条件を公式の条件表として記述する。実際にどれが使えるかは、認証後に
> `whoami` 等で確認する。

### 4.1 Figma Make

2025-07-24 にベータを終えて一般提供に入った、「prompt-to-app」型のツール。対話可能で高忠実度のプロトタイプを作る。

| シート / プラン | 使える範囲 |
|---|---|
| **Full シート** | Make ファイル無制限、**公開（publish）が可能**（公開機能自体は引き続きベータ） |
| View / Collab / Dev シート | ドラフトは無制限。自分が使える AI 機能は試せる |
| Starter プラン | ドラフトは無制限。ただし**チームに共有できるのは 3 ファイルまで** |

### 4.2 AI クレジット

Figma Make は AI クレジットを消費する。クレジットは毎月リセットされ、繰り越しはない。

| シート | Starter | Professional | Organization | Enterprise |
|---|---|---|---|---|
| **Full** | 500 | **3,000** | **3,500** | **4,250** |
| Dev / Collab / View | 500 | 500 | 500 | 500 |

- Starter プランのユーザーと View シートには、**1 日 150 クレジットの上限**が別途ある
- Figma Make の消費量は作業内容による。公式は目安として、単純な作業で 30 以上、複雑な対話で 75 以上、アプリ 1 本の生成で 100 以上を挙げている
- 参考までに他機能: Add interactions は 1 回 20、背景除去は 1〜5、FigJam のテンプレート生成は 1 プロンプト 2〜24
- クレジットが尽きると、追加の AI 操作は一切できなくなる

> ⚠️ **アプリ 1 本の生成で 100 以上**という目安を Professional の 3,000 に当てると、月 30 回程度が上限の目安になる。試行錯誤を回すツールとしては、思ったほど余裕がない。

### 4.3 Make kits — デザインシステムの投入口

Make kits は「コードとスタイルの文脈をゼロから足さずに、自社プロダクトらしい見た目と挙動で作り始められるようにする」ための仕組み。**有料プランの Full シート**が対象。

構成要素は 3 つ。

1. **npm パッケージ** — コードの文脈
2. **公開済み Figma Design ライブラリの変数とスタイル** — 意匠の文脈
3. **guidelines** — 使い方を説明する Markdown ファイル群

作成手順:

```
1. Make ファイルを開く → Settings → Create a kit
     └ "Assemble your kit"（既存パッケージを使う）か "Start from scratch" を選ぶ
2. npm パッケージとライブラリのスタイルをモーダルからインポート
3. 必要ならカスタム設定を足す
4. guidelines フォルダに Markdown を書く
     └ 公式は「Make が期待に沿ったアプリを作る」ための要と位置づけている
5. Make にコンポーネントを作らせて、デザインシステムに沿っているか検証する
6. Publish kit → 名前・サムネイル・任意のパッケージ設定を付けて組織に公開
```

公開後は「Update kit」で更新（チームメイトに自動通知）、「Unpublish」で取り下げる。組織管理者は、公開済み kit を承認し既定で有効にできる。

> **guidelines が効く理由**: npm パッケージと変数だけでは「使ってよい/いけない」の判断が入らない。
> 「どのコンポーネントをどの文脈で使うか」は Markdown でしか渡せない。
> v0 の Design Systems 2.0 が「notes」を持ち、Stitch が `DESIGN.md` を持つのも同じ理由である。

### 4.4 Figma MCP サーバー

| | remote | desktop |
|---|---|---|
| エンドポイント | `https://mcp.figma.com/mcp` | Figma デスクトップアプリ経由でローカル実行 |
| 対象 | **全シート・全プラン** | **有料プランの Dev / Full シート** |
| 機能範囲 | 最も広い。**write to canvas を含む** | 組織 / エンタープライズの特定用途向け |
| 推奨 | ⭕ 公式が推奨 | 特別な事情があるときのみ |

**write to canvas** は、フレーム・コンポーネント・**変数**・オートレイアウトを、デザインシステムを正として生成・更新できる機能。⚠️ **「いずれ従量課金の有料機能になるが、ベータ期間中は無料」**と明記されている。

**レート制限**は、シート種別で**桁が変わる**。公式の Rate limits & access が持つ表のうち、
複数回の読み取りで一致した値のみを記す（プラン別の全数値は原典を参照。§8「確認できなかった事項」）。

- **View / Collab シート（有料プラン）**: **月 6 コールまで**
- **Dev / Full シート（Professional）**: **1 日 200 コール・1 分 10 コールまで**
  （Education プランは「Dev and Full seats on the Professional plan」と同一と明記されている）
- **Dev / Full シート（Organization 以上）**: 上記より高い上限が設定されている
- `add_code_connect_map` / `create_new_file` / `whoami` は**レート制限の対象外**

> ⚠️ **View / Collab シートは月 6 コール**である。試しに触るだけでも一瞬で尽きる。
> **MCP を実務で使うなら Dev または Full シートが実質的な前提**になる。

### 4.5 公式スキル一覧 — ⚠️ `/prototype-to-figma` は存在しない

Anthropic 公式 plugin marketplace の `figma` plugin（実測: v2.2.108）が同梱するスキルは以下の 15 個。

| スキル | 向き | 役割 |
|---|---|---|
| `figma-use` | — | **全てのキャンバス書き込みの土台**。Plugin API の呼び出し規則を持つ |
| `figma-design-to-code` | Figma → コード | `get_design_context` を呼ぶ**前に必ず読む**ことが required と明記されている |
| `figma-generate-design` | **コード → Figma** | ページ / モーダル / サイドバー等の**構成済みビュー**を、公開済みデザインシステムのコンポーネント・変数・スタイルを再利用して組む |
| `figma-generate-library` | コード → Figma | 変数 / トークン、コンポーネントライブラリ、ライト/ダークのテーマ設定まで含む**デザインシステム本体**を構築する |
| `figma-code-connect` | 双方向 | Figma コンポーネントとコードスニペットを対応づける `.figma.ts` テンプレートを書く |
| `figma-create-new-file` / `figma-generate-diagram` / `figma-use-figjam` / `figma-use-slides` / `figma-use-motion` / `figma-implement-motion` / `figma-shaders` / `figma-swiftui` / `figma-generative-plugins` | — | 用途別 |

⚠️ **訂正**: 「動いているローカル実装をそのまま Figma のフレームに取り込む `/prototype-to-figma` スキル」という説明が流通しているが、**そのようなスキルは存在しない**。15 個のスキル一覧にも、Figma 公式の MCP ドキュメントにも該当する名前はない。

**実際に該当する機能は `figma-generate-design`** である。同スキルの description は発火条件として「write to Figma」「create in Figma from code」「push page to Figma」「take this app/page and build it in Figma」「update the Figma screen to match code」を挙げており、**コード → Figma の方向そのもの**を担当する。加えて Figma 側には Web ページを Figma デザインに変換する機能がロールアウト中である。

> **なぜ間違いやすいか**: 機能自体は実在するため、名前だけが誤って伝わる。
> スキル名を根拠に手順を組むと `Unsupported` で失敗する。
> [デザインワークフロー](design-workflow.md) が AIDesigner の `init claude-code` で記録したのと同じ、
> **二次情報の引数・名称を一次情報で検証せずに実行する失敗パターン**である。

### 4.6 Code Connect

Figma コンポーネントと実装コードを対応づけ、生成コードを既存コードベースと整合させる仕組み。公式スキル `figma-code-connect` が扱う。

⚠️ **成果物の形式に注意**。このスキルが書くのは **`.figma.ts`（parserless template、`figma.code` タグ付きテンプレートを default export する形）** であり、**`.figma.tsx` + `figma.connect()` は別方式（parser-based）で、公開手順も異なる**。スキルは `.figma.tsx` の出力を明確に拒否する。

なお `figma-code-connect` の利用には、対象コンポーネントが **Figma のチームライブラリに公開済み**であることが前提になる。

---

## 5. その他の選択肢

### 5.1 Vercel v0

Next.js + shadcn/ui + Tailwind を既定のスタックとして UI を生成する。デザインシステムの扱いは **Design Systems 2.0** に刷新された。

公式の定義が本質を突いている。

> a design system skill is not a copy of your docs; it is an adapter that tells v0 where your source lives, which components, props, and tokens are safe to use.

つまり**ドキュメントの複製ではなく、実ソースへのアダプタ**である。設計思想もこれに沿う。

> v0 grounds itself in the real source. If a component, prop, or token cannot be verified from the sources, v0 should not use it.

| 項目 | 内容 |
|---|---|
| source にできるもの | GitHub リポジトリ（デザインシステム本体 / 利用側アプリ）、Figma のフレーム・ノード、Storybook / docs / ガイドラインへのリンク、添付（スクリーンショット / ZIP / `.tgz`） |
| 保存形式 | **`v0.json`**。`referenceWorkspace.sources`（参照専用 GitHub ソース、**最大 3 件**）、`environment.providers`（private npm 用の環境変数）、`starter`（初期アプリ） |
| 作成フロー | source 追加 → 環境変数の設定 → notes（グローバルスタイル・非推奨パターン・規約）→ starter アプリのレビュー → 承認して skill として保存 |
| プラン条件 | **有料プランの Team owner** がチームの既定デザインシステムを選べる。private パッケージ用の Development 環境変数を使うには **Vercel の Developer ロール以上** |
| 旧方式 | shadcn registry ベース（「A registry is a distribution specification designed to pass context from your design system to AI Models」）。[デザイントークン §4.2](design-tokens.md#42-b-コードを正本にしregistry-で配る) を参照 |

### 5.2 Google Stitch

Google Labs のツール。2026-03-18、Google Labs の PM である Rustin Banks が「AI-native software design canvas」への刷新を発表した。

| 項目 | 内容 |
|---|---|
| AI ネイティブキャンバス | 画像・テキスト・コードを入力として扱う、無限かつ文脈認識のワークスペース |
| デザインエージェント | 「進捗を追跡し、複数のアイデアを並行して進めるのを助ける」推論システム |
| **`DESIGN.md`** | **デザインシステムをツール間で入出力するための、エージェントが読める Markdown 形式** |
| 対話型プロトタイプ | 静的デザインを即座にクリック可能なプロトタイプに変換し、画面フローを自動生成 |
| 音声操作 | 「メニュー案を 3 つ出して」のような発話でリアルタイムに更新・批評 |
| 連携 | AI Studio / Antigravity などの開発者ツール、**MCP サーバーと SDK**、URL からのデザインシステム抽出 |

**SDK / MCP の実装詳細**（`google-labs-code/stitch-sdk` より）:

| 項目 | 内容 |
|---|---|
| パッケージ | `@google/stitch-sdk`（TypeScript） |
| MCP エンドポイント | `stitch.googleapis.com/mcp` |
| 認証 | API キー（`STITCH_API_KEY` → `X-Goog-Api-Key` ヘッダ）または OAuth（`STITCH_ACCESS_TOKEN` + `GOOGLE_CLOUD_PROJECT` → Bearer + `X-Goog-User-Project`） |
| ドメイン API | `Project.generate(prompt, deviceType)` / `screens()` / `getScreen(id)`、`Screen.edit()` / `variants()` / `getHtml()` / `getImage()` |
| 低レベル API | `StitchToolClient.callTool(name, args)` / `listTools()` |
| エージェント統合 | `stitchTools()` が Vercel AI SDK の `Tool` オブジェクトとして全 MCP ツールを返す |
| 出力 | **HTML のダウンロード URL とスクリーンショットの URL** |

⚠️ **SDK と製品機能の境界に注意**。`DESIGN.md` は **Stitch 製品側の機能**であり、`stitch-sdk` リポジトリ内には該当ファイルも該当 API も存在しない。同様に、**SDK 側に Figma 書き出しの API は見当たらない**。SDK からできるのは画面生成と HTML / 画像の取得である。

> **確認できなかった事項**: Stitch の料金体系・生成回数の上限は、2026-03-18 の Google Labs ブログに記載がない。
> 二次情報では月あたりの生成上限が語られているが、**一次情報で裏が取れないため本稿では数値を掲載しない**。

### 5.3 Claude Design の連携先として位置づけられるサービス

Lovable / Replit / Base44 / Gamma / Wix / Adobe / Canva / Miro / Vercel は、いずれも Claude Design の**連携先**として公式に挙げられている。単独の AI デザインツールとして比較検討するより、**Claude Design を起点にした出口として扱うほうが実態に合う**（§2.4）。

### 5.4 比較 — 「どの口からデザインシステムが入るか」

| 投入経路 | Claude Design | Figma Make | v0 | Stitch |
|---|---|---|---|---|
| GitHub リポジトリ | ⭕ | ❌ | ⭕（最大 3 件） | ❌ |
| ローカルコードベース | ⭕（`/design-sync`） | ❌ | ❌ | ❌ |
| npm パッケージ | ❌ | ⭕ | ⭕（`.tgz` 添付 / private npm） | ❌ |
| デザインツールのライブラリ | ⭕（デザインファイル） | ⭕（Figma ライブラリの変数・スタイル） | ⭕（Figma ノード） | ❌ |
| 自然言語のガイドライン | ⭕ | ⭕（guidelines） | ⭕（notes） | ⭕（`DESIGN.md`） |
| URL / Web ページ | ⭕（Web キャプチャ） | ❌ | ⭕（docs / Storybook リンク） | ⭕（URL から抽出） |

> **読み取れること**: 「**自然言語のガイドライン**」だけが 4 ツール共通の入口である。
> コードや変数を渡しても「使ってよい / いけない」の判断は渡らないため、
> どのツールでも最終的に Markdown の規約文書が要る。
> **guidelines / notes / `DESIGN.md` を書く作業は、ツールを乗り換えても無駄にならない**。

---

## 6. 採否の考え方

新しい AI デザインツールを導入するかどうかの基準は [デザインワークフロー](design-workflow.md) の
「大原則」と「外部デザインツールの採否基準」を SSOT とする。ここでは再掲しない。

本ドキュメントの調査から補足できる点だけ記す。

- **§1 の 5 つは、いずれも一次提供元が明確な公式プロダクト**である。採否基準 #1〜#5（ソース公開・ライセンス・メンテナ体制・更新頻度・送信データ）は問題にならない
- したがって判断は**採否基準 #6（既存スタックとの重複）に集約される**。個人開発で Claude Design がサブスクに含まれ、業務で Figma を契約済みという構成であれば、**v0 と Stitch は「同じ成果が既存で得られる」に該当する可能性が高い**
- 例外は「**そのツールにしかない入口**」があるとき。§5.4 の表で、自分の正本の形式（[デザイントークン §4](design-tokens.md#4-正本source-of-truthをどこに置くか--3-系統)）に対応する ⭕ が既存ツールに無い場合のみ、追加を検討する価値がある

---

## 7. 既存ドキュメントとの関係

| ドキュメント | 何の SSOT か |
|---|---|
| 本ドキュメント | 各 AI デザインツールの**仕様と現在地** |
| [デザイントークン](design-tokens.md) | トークンの**概念と規格**、正本の置き場所の設計 |
| [デザインワークフロー](design-workflow.md) | 「どのツールをいつ使うか」の**選択指針**と外部ツールの採否基準 |
| [使用ツールスタック](tool-stack.md) | 「何を導入済みか」の棚卸し |
| [スラッシュコマンド](slash-commands.md) | `/design` / `/design-sync` / `/design-login` の**コマンド定義** |

---

## 8. 出典

### 一次情報

| 出典 | URL |
|---|---|
| Introducing Claude Design by Anthropic Labs（2026-04-17） | https://www.anthropic.com/news/claude-design-anthropic-labs （2026-09-13 確認） |
| Get started with Claude Design — Claude Help Center | https://support.claude.com/en/articles/14604416-get-started-with-claude-design （2026-09-13 確認） |
| Claude Design 製品ページ | https://claude.com/product/design （2026-09-13 確認） |
| Claude Design admin guide for Team and Enterprise plans | https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans （2026-09-13 確認） |
| `DesignSync` ツール仕様 | ClaudeCode 同梱ツールのスキーマ本体（2026-09-13 実測） |
| `list_design_systems` の実行結果 | `claude_design` MCP（2026-09-13 実測、0 件） |
| Anthropic 公式 `figma` plugin のスキル一覧 | `~/.claude/plugins/cache/claude-plugins-official/figma/2.2.108/skills/`（2026-09-13 実測、15 スキル） |
| Guide to the Figma MCP server — Figma Help Center | https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server （2026-09-13 確認） |
| Rate limits & access — Figma Developers | https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/ （2026-09-13 確認） |
| Figma MCP server — Figma Developers | https://developers.figma.com/docs/figma-mcp-server/ （2026-09-13 確認） |
| Get started with Make kits — Figma Help Center | https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits （2026-09-13 確認） |
| Figma Make Is Now Available to All Users（2025-07-24） | https://www.figma.com/blog/figma-make-general-availability/ （2026-09-13 確認） |
| How AI credits work — Figma Help Center | https://help.figma.com/hc/en-us/articles/33459875669015-How-AI-credits-work （2026-09-13 確認） |
| Design systems（Design Systems 2.0）— v0 Docs | https://v0.app/docs/design-systems-2 （2026-09-13 確認） |
| Design systems (legacy) — v0 Docs | https://v0.app/docs/design-systems-legacy （2026-09-13 確認） |
| Design UI using AI with Stitch from Google Labs（2026-03-18） | https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/ （2026-09-13 確認） |
| `google-labs-code/stitch-sdk` | DeepWiki 経由で確認（2026-09-13） |
| `figma/mcp-server-guide` | DeepWiki 経由で確認（2026-09-13） |

### 確認できなかった事項

以下は一次情報で裏が取れなかったため、本文に数値・断定を書いていない。

- **Figma Make を駆動するモデル**。一般提供時の公式ブログはモデル名を明示していない。Figma の公式 SNS アカウントによるモデル追加の告知は存在するが、ヘルプセンター / ブログの一次情報として確認できていない
- **Google Stitch の料金・生成上限**。Google Labs のブログに記載がない
- **Figma MCP の Code Connect に固有のプラン要件**。Rate limits & access には Code Connect 固有のプラン条件の記載がない（`add_code_connect_map` がレート制限の対象外である旨のみ）
- **Make kits の全有料プラン展開日**。公式ヘルプはプラン条件（有料プランの Full シート）のみを記載している
- **Figma MCP のプラン別レート制限の完全な表**。Rate limits & access の表を複数回読み取ったが、**どの数値がどのプラン列に属するかが読み取りごとに食い違った**（特に Organization / Enterprise の Dev / Full 行）。再構成した表を載せるのは避け、§4.4 では複数回の読み取りで一致した値のみを記載している。正確な全数値は原典を参照する

- 関連: `docs/design-tokens.md` / `docs/design-workflow.md` / `docs/slash-commands.md`
