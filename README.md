# JARVIS

@thanks2music (Yoshiyuki Ito) が AI を活用した開発における試行錯誤・実験・検証の記録と、現時点のベストプラクティスをまとめるリポジトリ。

## Why?

爆発的なスピードで進化する LLM/AI 業界のすべてに追従することは、現実的に難しい。

しかし、ClaudeCode や MCP を軸に「AI を使って開発するためのグランドデザイン」の輪郭が見え始めてきた。その試行錯誤の過程と現時点のベストプラクティスを GitHub 上に記録・可視化することで、環境が変わった際の再構築を容易にすることを目的としている。

## 活用原則

- **完成よりも継続**: 完璧なグランドデザインを目指すのではなく、試行錯誤しながらステップ・バイ・ステップで改善していく
- **AI は手段、人間が主体**: ClaudeCode を最大限に活用しながらも、設計・判断・責任は常に人間が担う
- **再現性を意識した記録**: 環境が変わっても同じ状態を再構築できるよう、具体的なツール・設定・コマンドを残す
- **鮮度を保つ更新**: 古くなった情報は積極的に更新または削除し、記録の正確さを維持する

## thanks2music's AI grand design

- Main: ClaudeCode
- Sub: Codex
- Essential:
  - SDD (Spec-Driven Development = 仕様駆動開発)
  - SpecKit
- MCP:
  - chrome-devtools
  - playwright
  - Context7
  - DeepWiki
  - Drawio
  - Todoist
  - browsermcp

## ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [ClaudeCode の設定ファイル一覧と役割](docs/config-files.md) | 6 つの JSON 設定ファイルの目的・スコープ・優先順位・対応表 |
| [Claude Desktop の設定ファイル](docs/claude-desktop.md) | `claude_desktop_config.json` の詳細と ClaudeCode との違い |
| [MCP サーバーの追加方法ガイド](docs/mcp-setup-guide.md) | `claude mcp add` の構文・JSON からの変換方法・スコープの使い分け |
| [ClaudeCode のベストプラクティス](docs/best-practices.md) | 公式ドキュメントに基づく 7 つのベストプラクティス（編集対象外） |

## リポジトリ名の意味

**AIdentity** = AI + Identity の「I」を統合したモノグラム造語。AI と自分自身のアイデンティティを掛け合わせた名前である。
