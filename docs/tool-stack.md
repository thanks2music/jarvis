# 使用ツールスタック

> 最終更新: 2026-10-30

AI を活用した開発で使用しているツール群。試行錯誤中のため、今後追加・変更される可能性がある。

## 現在のスタック

| 役割 | ツール | 備考 |
|------|--------|------|
| メイン AI エージェント | ClaudeCode | Anthropic 製。ターミナルベースのエージェント型コーディング環境 |
| エディタ / ACP ホスト | Zed | ClaudeCode を ACP 経由で動かすエディタ環境（詳細は [Zed ガイド](zed.md)） |
| サブ AI エージェント | Codex | OpenAI 製 |

## 駆動開発 (Driven Development)

AI エージェントとの開発で採用している駆動開発の手法。**上から順に優先して採用する**。

| 優先 | 手法 | 略称 | 正式名称 | 開発の起点にするもの | この環境での主な手段 |
|------|------|------|----------|----------------------|----------------------|
| 1 | テスト駆動開発 | TDD | Test-Driven Development | 先に書いた失敗するテスト（期待する振る舞い） | Vitest / Jest |
| 2 | スキーマ駆動開発 | SDD | Schema-Driven Development | スキーマ（API・DB・データ構造の定義）。型とバリデーションをスキーマから導出する | [Zod](https://zod.dev) |
| 3 | 仕様駆動開発 | SDD | Spec-Driven Development | 仕様書（要件・受け入れ基準）。計画とタスクを仕様から起こす | [GitHub Spec Kit](https://github.com/github/spec-kit)（`specify` CLI） |

- **略称の衝突**: スキーマ駆動と仕様駆動はどちらも SDD と略される。GitHub Spec Kit は SDD を Spec-Driven Development の意味で使っている。SDD とだけ書くとどちらか分からないため、本リポジトリの文中では日本語名で区別する
- **TDD を最優先にすることと公式の推奨**: ClaudeCode の公式ベストプラクティスは「Claude が自分の作業を検証できる手段を与える」ことを最重要に挙げ、その手段の筆頭にテストを置いている（[ベストプラクティス §1](best-practices.md#1-作業を検証できる手段を提供する最重要)）。テストを先に書くと、この検証手段が実装より先に揃う

出典: [Canon TDD（Kent Beck）](https://tidyfirst.substack.com/p/canon-tdd) / [GitHub Spec Kit](https://github.com/github/spec-kit) / [Zod](https://zod.dev)

## 2026-09-03 時点で評価対象に入った公式機能

いずれも既存スタックの代替候補であり、**採否は未決**である。

| 機能 | 内容 | 既存スタックとの関係 |
|---|---|---|
| **Claude in Chrome（GA）** | 全有料プランで一般提供。**各操作の承認なしに自律でクリック・入力・フォーム記入**し、安全性分類器が実行前に検証する。prompt injection 対策も強化された | `~/.claude/work-style.md` のブラウザ確認フォールバックチェーン（Playwright MCP → chrome-devtools MCP → browser-use MCP）の**代替候補**。ただし現行チェーンはコンソールエラー検証・トークン消費で選定した経緯があるため、置き換えるなら同じ観点での比較が必要 |
| **GitLab MR バッジ**（v2.1.234〜） | GitLab remote があり `glab` CLI が `glab auth login` 済みのリポジトリで、**footer と statusline に draft / open / mergeable で色分けした `MR !N` を表示**する | 既存の「GitLab の一級サポート（v2.1.232 / 233、`--worktree` と `claude agents` view）」に続く追加。GitLab を使うリポジトリでのみ効く |
| **Desktop の Computer use**（research preview） | Claude が実際のデスクトップでアプリを開き画面を操作する。**Pro / Max 限定・既定 off**。詳細は [claude-desktop.md](claude-desktop.md) | ブラウザ以外の GUI 操作が必要な場面の選択肢。**sandboxed Bash とは信頼境界が異なる**点に注意 |
| **`/design`**（導入は v2.1.234 で当時は research preview。現行の要件は v2.1.265+・artifacts が使えるセッション・Design テンプレートが有効なアカウント。2026-10-11 更新） | Claude Design の artboard ワークフローを CLI / Desktop に持ち込むバンドルスキル。詳細は [design-workflow.md](design-workflow.md) | 既存の `claude_design` MCP / `design` skill と同一基盤 |

出典: [Claude in Chrome is generally available](https://claude.com/blog/claude-in-chrome-generally-available) / [whats-new week 34](https://code.claude.com/docs/en/whats-new/2026-w34) / [Claude Desktop](https://code.claude.com/docs/en/desktop)

## MCPs

2026-10-30 時点で実際に登録している MCP サーバー。登録の経路ごとに分けて載せる。

### 手動登録（user scope。全プロジェクト共通）

| MCP サーバー | 用途 |
|-------------|------|
| [Context7](https://github.com/upstash/context7) | ライブラリの最新ドキュメント参照 |
| [DeepWiki](https://docs.devin.ai/work-with-devin/deepwiki-mcp) | 公開 GitHub リポジトリの AI ドキュメント（`mcp.deepwiki.com`） |
| [Devin MCP](https://docs.devin.ai/work-with-devin/devin-mcp) | DeepWiki の認証付き版（プライベートリポジトリに対応）と Devin の操作（`mcp.devin.ai`） |
| [AWS Documentation MCP](https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server) | AWS 公式ドキュメントの検索・参照 |
| [AWS IaC MCP](https://github.com/awslabs/mcp/tree/main/src/aws-iac-mcp-server) | CloudFormation テンプレートの検証、CDK ドキュメントの検索 |
| [Backlog MCP](https://github.com/nulab/backlog-mcp-server) | Backlog の課題・プロジェクト管理。1 インスタンスで 1 ワークスペースしか扱えないため、ワークスペースごとに別名で登録する |
| [Notion MCP](https://github.com/makenotion/notion-mcp-server) | Notion のページ・データベース操作（API トークン版）。claude.ai コネクタ経由のリモート版も併用する |
| [Todoist MCP](https://github.com/Doist/todoist-mcp) | タスク管理（Doist 公式。API トークンの stdio 版） |
| [Memory MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) | ナレッジグラフ形式の永続メモリ |
| [Google Workspace MCP](https://github.com/taylorwilsdon/google_workspace_mcp) | Google ドキュメント・ドライブの参照 |
| [Google Sheets MCP](https://github.com/xing5/mcp-google-sheets) | Google スプレッドシートの作成・編集 |
| [Gemini API Docs MCP](https://ai.google.dev/gemini-api/docs/coding-agents) | Gemini API の公式ドキュメント・SDK リファレンスの検索 |
| Claude Design MCP | Claude Design の artboard との連携（詳細は [design-workflow.md](design-workflow.md)） |
| [browser-use MCP](https://github.com/browser-use/browser-use) | AI エージェント自律操作（フォーム自動入力・複数ページ調査の自動化等）の特化用途。通常のブラウザ確認では非推奨（コンソール検証不可、スクリーンショット強制インライン）。`uvx --managed-python --python 3.14 --from 'browser-use[cli]' browser-use --mcp` で起動（`--python 3.14` は 2026-06-13 時点で動作確認したバージョン。3.15 系での動作は未検証）。`--managed-python` は uv 管理の Python（python-build-standalone。アプリバンドルを持たない）に固定するために付ける。Homebrew の `python@3.14` のようなフレームワークビルドで動かすと、browser-use が MCP 初期化時に `AppKit.NSScreen` で画面サイズを取った時点で `Python.app` が通常アプリとして登録され、セッションの数だけ Dock に Python のアイコンが並ぶ（2026-10-30 実測。asdf の global を 3.15.1 に上げたことで `--python 3.14` の解決先が Homebrew 版に変わったのが発端） |
| [Supabase MCP](https://github.com/supabase/mcp) | Supabase プロジェクトの DB / Edge Functions / migration 操作 (30 ツール)。**stdio + PAT 推奨** — hosted OAuth 版 (`mcp.supabase.com`) は約 1 週間ごとの再認証 UX 問題と `Unrecognized client_id` 不具合があるため。user scope は `--read-only` 既定、書込が必要な特定プロジェクト dir でのみ local scope で `--read-only` なしを上書き登録する運用 (2026-06-13/14 Revolution 案件で実証)。`npx -y @supabase/mcp-server-supabase@latest` で起動 |

### プラグイン経由（`~/.claude/settings.json` の `enabledPlugins`）

| MCP サーバー | 用途 |
|-------------|------|
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | ブラウザ操作のメイン MCP。navigate / クリック / スクリーンショット / コンソール確認。トークン消費が最少で、スナップショットのファイル退避がデフォルト（2026-06-13 検証で第 1 推奨） |
| [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | LCP 計測・パフォーマンス分析・Lighthouse 監査・network 詳細・コンソール 20 種フィルタなどデバッグ用途で唯一無二の機能を持つ（2026-06-13 検証で第 2 推奨） |
| [Figma MCP](https://developers.figma.com/docs/figma-mcp-server/) | Figma 公式のリモート版（`mcp.figma.com`）。デザインの参照・コードとの連携・Figma への書き込み |
| [Firebase MCP](https://firebase.google.com/docs/ai-assistance/mcp-server) | Firebase プロジェクトの管理・操作（`firebase-tools` に同梱） |
| [Sentry MCP](https://github.com/getsentry/sentry-mcp) | エラー監視・Issue トラッキング（OAuth 認証が必要） |
| [Slack MCP](https://docs.slack.dev/ai/mcp-server) | Slack の検索・閲覧・投稿 |
| [Stripe MCP](https://docs.stripe.com/mcp) | Stripe の API 操作・ドキュメント検索（OAuth 認証が必要） |
| [Cloudflare MCP](https://github.com/cloudflare/mcp-server-cloudflare) | Cloudflare のドキュメント検索ほか |
| [Microsoft Learn MCP](https://learn.microsoft.com/en-us/training/support/mcp) | Microsoft / Azure の公式ドキュメント検索 |
| [Google Developer Knowledge MCP](https://developers.google.com/knowledge/mcp) | Google Cloud・Firebase など Google の公式ドキュメント検索 |
| [Terraform MCP](https://github.com/hashicorp/terraform-mcp-server) | Terraform Registry の provider / module 情報の参照 |
| [Prisma MCP](https://www.prisma.io/docs/postgres/integrations/mcp-server) | Prisma のローカル操作と Prisma Postgres の管理 |
| [Laravel Boost](https://github.com/laravel/boost) | Laravel プロジェクトの中でだけ動く MCP（`php artisan boost:mcp`） |
| [GitHub MCP Server](https://github.com/github/github-mcp-server) | プラグインは有効だが、Personal Access Token を設定していないため接続していない。GitHub の操作は `gh` CLI で行う |

### claude.ai コネクタ

claude.ai で接続したコネクタは ClaudeCode にも自動で現れる（[MCP サーバーの追加方法ガイド](mcp-setup.md#claudeai-の-connectors-と-custom-connector)）。Gmail / Google Calendar / Google Drive / Notion / [Vercel](https://vercel.com/docs/mcp/vercel-mcp) / Claude Docs を接続している。

### プロジェクト単位（local scope）

一部のプロジェクトでだけ local scope に登録しているもの: [gcloud MCP / observability MCP](https://github.com/googleapis/gcloud-mcp)、[Framelink Figma MCP](https://github.com/GLips/Figma-Context-MCP)、GitHub MCP（stdio 版）、AWS MCP（`mcp-proxy-for-aws` 経由）、書き込みを許可した Supabase MCP（Revolution）など。

以前に載せていた Drawio MCP は登録していない。図は `diagram-maker` プラグインと `draw-io` スキルで作る。

> MCP サーバーの追加方法については [MCP サーバーの追加方法ガイド](mcp-setup.md) を参照。

## Skills

常用しているスキル。直近 60 日のセッション履歴で利用回数が多かったものから、業務固有のものを除いて載せる（2026-10-30 集計）。個人スキル（Personal）の実体は avengers リポジトリ（private）で管理し、`~/.claude/skills/` へ symlink している。スキルの仕組みは [Skills ガイド](skills.md) を参照。

| スキル | スコープ | 用途 |
|--------|---------|------|
| `handoff` | Personal | 次のセッションへの引き継ぎ文書を生成し、並列レビューで直す |
| `spec-driven-review` | Personal | 完了報告の直前に、観点の異なる 4 体のサブエージェントが公式仕様を根拠に並列レビューする |
| `report-session` | Personal | 完了した作業のセッション作業報告書を残す |
| `review-all-ai` | Personal | 複数の AI レビュアー（Copilot / claude[bot] など）の PR レビューを横断取得し、妥当性を検証して対応する |
| `ok-ship-it` | Personal | commit → push → PR 作成 → BOT レビュー対応までを自走する（明示起動のみ） |
| `briefing` | Personal | 会話履歴と git の事実から、いまの作業状況を構造化して示す |
| `browse-playwright` | Personal | Playwright MCP でブラウザを開き、表示・動作を確認する |
| `best-practice-auditor` | Personal | 技術選定・設計判断を公式仕様と一次情報で監査する |
| `todoist-ops` | Personal | Todoist のタスク追加・ラベル・フィルターの運用 |
| `git-commit` | Personal | emoji + 種別付きのメッセージでコミットする（明示起動のみ） |
| `revolution` | Plugin | Revolution プロジェクトのタスク管理と情報収集 |
| `diagram-maker` | Plugin | draw.io の図を生成し、自己検証まで行う |
| `claude-docs-sync` | Project | 公式 ClaudeCode docs の鮮度同期（本リポジトリ専用） |
