# 使用ツールスタック

> 最終更新: 2026-03-22

AI を活用した開発で使用しているツール群。試行錯誤中のため、今後追加・変更される可能性がある。

## 現在のスタック

| 役割 | ツール | 備考 |
|------|--------|------|
| メイン AI エージェント | ClaudeCode | Anthropic 製。ターミナルベースのエージェント型コーディング環境 |
| サブ AI エージェント | Codex | OpenAI 製 |
| 仕様駆動開発 | SpecKit (SDD) | Spec-Driven Development |

## MCP サーバー

| MCP サーバー | 用途 |
|-------------|------|
| [Context7](https://github.com/upstash/context7) | ライブラリの最新ドキュメント参照 |
| [DeepWiki](https://github.com/AsyncFuncAI/deepwiki-open) | GitHub リポジトリの AI ドキュメント |
| [GitHub MCP Server](https://github.com/github/github-mcp-server) | GitHub の Issue・PR・リポジトリ操作 |
| [Playwright MCP](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-playwright) | ブラウザ自動操作・E2E テスト |
| [Sentry MCP](https://github.com/getsentry/sentry-mcp) | エラー監視・Issue トラッキング |
| [Figma MCP](https://github.com/nichochar/open-figma-mcp) | Figma デザインデータの参照・連携 |
| [Backlog MCP](https://github.com/nulab/backlog-mcp-server) | Backlog の課題・プロジェクト管理 |
| [Firebase MCP](https://github.com/nichochar/firebase-mcp) | Firebase プロジェクトの管理・操作 |
| [AWS Documentation MCP](https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server) | AWS 公式ドキュメントの検索・参照 |
| [gcloud MCP](https://github.com/googleapis/gcloud-mcp) | Google Cloud リソースの操作 |
| [observability-mcp](https://github.com/googleapis/gcloud-mcp) | Google Cloud のオブザーバビリティ（gcloud MCP 内） |
| [vercel-awesome-ai MCP](https://github.com/vercel/awesome-ai) | Vercel AI 関連ツール・リソース |
| chrome-devtools | Chrome DevTools との連携 |
| browsermcp | ブラウザ操作 |
| [Drawio](https://github.com/xvnpw/mcp-drawio) | ダイアグラム作成 |
| [Todoist](https://github.com/abhiz123/todoist-mcp-server) | タスク管理 |

> MCP サーバーの追加方法については [MCP サーバーの追加方法ガイド](mcp-setup-guide.md) を参照。
