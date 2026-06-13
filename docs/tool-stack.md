# 使用ツールスタック

> 最終更新: 2026-05-25

AI を活用した開発で使用しているツール群。試行錯誤中のため、今後追加・変更される可能性がある。

## 現在のスタック

| 役割 | ツール | 備考 |
|------|--------|------|
| メイン AI エージェント | ClaudeCode | Anthropic 製。ターミナルベースのエージェント型コーディング環境 |
| エディタ / ACP ホスト | Zed | ClaudeCode を ACP 経由で動かすエディタ環境（詳細は [Zed ガイド](zed.md)） |
| サブ AI エージェント | Codex | OpenAI 製 |
| 仕様駆動開発 | SpecKit (SDD) | Spec-Driven Development |

## MCPs

| MCP サーバー | 用途 |
|-------------|------|
| [Context7](https://github.com/upstash/context7) | ライブラリの最新ドキュメント参照 |
| [DeepWiki](https://github.com/AsyncFuncAI/deepwiki-open) | GitHub リポジトリの AI ドキュメント |
| [GitHub MCP Server](https://github.com/github/github-mcp-server) | GitHub の Issue・PR・リポジトリ操作 |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | ブラウザ操作のメイン MCP。navigate / クリック / スクリーンショット / コンソール確認。トークン消費が最少で、スナップショットのファイル退避がデフォルト（2026-06-13 検証で第 1 推奨） |
| [Sentry MCP](https://github.com/getsentry/sentry-mcp) | エラー監視・Issue トラッキング |
| [Figma MCP](https://github.com/nichochar/open-figma-mcp) | Figma デザインデータの参照・連携 |
| [Backlog MCP](https://github.com/nulab/backlog-mcp-server) | Backlog の課題・プロジェクト管理 |
| [Firebase MCP](https://github.com/nichochar/firebase-mcp) | Firebase プロジェクトの管理・操作 |
| [AWS Documentation MCP](https://github.com/awslabs/mcp) | AWS 公式ドキュメントの検索・参照 |
| [gcloud MCP](https://github.com/googleapis/gcloud-mcp) | Google Cloud リソースの操作 |
| [observability-mcp](https://github.com/googleapis/gcloud-mcp) | Google Cloud のオブザーバビリティ（gcloud MCP 内） |
| [vercel-awesome-ai MCP](https://github.com/vercel/awesome-ai) | Vercel AI 関連ツール・リソース |
| [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | LCP 計測・パフォーマンス分析・Lighthouse 監査・network 詳細・コンソール 20 種フィルタなどデバッグ用途で唯一無二の機能を持つ（2026-06-13 検証で第 2 推奨） |
| [browser-use MCP](https://github.com/browser-use/browser-use) | AI エージェント自律操作（フォーム自動入力・複数ページ調査の自動化等）の特化用途。通常のブラウザ確認では非推奨（コンソール検証不可、スクリーンショット強制インライン）。`uvx --python 3.14 --from 'browser-use[cli]' browser-use --mcp` で起動（`--python 3.14` は 2026-06-13 時点で動作確認したバージョン。Python 3.15 以降がリリースされた場合は要再検証） |
| [Drawio](https://github.com/xvnpw/mcp-drawio) | ダイアグラム作成 |
| [Todoist](https://github.com/abhiz123/todoist-mcp-server) | タスク管理 |

> MCP サーバーの追加方法については [MCP サーバーの追加方法ガイド](mcp-setup.md) を参照。

## Skills

主要な常用スキル。個人スキルの最新・完全な一覧は [Skills ガイド](skills.md#現在の個人スキル一覧) を SSOT とする。

| スキル | スコープ | 用途 |
|--------|---------|------|
| `claude-docs-sync` | Project | 公式 ClaudeCode docs の鮮度同期（本リポジトリ専用） |
| `aws-ecs-fargate` | Personal | ECS Fargate + RDS + ElastiCache の Terraform パターン |
| `aws-static-hosting` | Personal | S3 + CloudFront 静的サイトホスティングの Terraform パターン |
| `ecs-deploy-troubleshooting` | Personal | ECS デプロイ障害の調査手順と過去事例 |
| `github-actions-aws-oidc` | Personal | GitHub Actions OIDC → AWS デプロイパターン |
| `infra-decompose` | Personal | インフラ + アプリ混在フィーチャーのスコープ分割提案 |
