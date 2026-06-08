# JARVIS

> *"Just a Really Very Intelligent System"*

[日本語版はこちら](#jarvis-1)

A personal repository documenting experiments, best practices, and ongoing learnings in AI-powered development.

## Why JARVIS?

"JARVIS" is an homage to Tony Stark's J.A.R.V.I.S. — a personal attempt to build a "Just a Really Very Intelligent System" in the age of AI and LLMs.

Keeping up with every advancement in the rapidly evolving LLM/AI landscape isn't realistic. However, the outlines of a "grand design for AI-powered development" are starting to take shape. This repository captures that journey — recording and visualizing the process on GitHub, with a focus on reproducibility, version control, and continuously improving the development workflow.

### Principles

- **Progress over perfection** — Improve step by step rather than chasing the ideal
- **AI as a tool, humans at the helm** — Design, decisions, and accountability always rest with the human
- **Document for reproducibility** — Record specifics so the same setup can be rebuilt in any environment
- **Keep it fresh** — Actively update or remove outdated information

## Documentation

| Document | Description |
|----------|-------------|
| [Tool Stack](docs/tool-stack.md) | AI agents, MCP servers, and other tools in use |
| [ClaudeCode Configuration Files](docs/config-files.md) | 6 JSON config files — purpose, scope, precedence, and reference table |
| [Claude Desktop Configuration](docs/claude-desktop.md) | `claude_desktop_config.json` details and differences from ClaudeCode |
| [MCP Server Setup Guide](docs/mcp-setup.md) | `claude mcp add` syntax, JSON-to-CLI conversion, and scope usage |
| [ClaudeCode Slash Commands Guide](docs/slash-commands.md) | Built-in commands and bundled skills — context management, session control, and productivity workflows |
| [ClaudeCode Skills Guide](docs/skills.md) | Skills overview — prerequisites, usage, frontmatter, patterns, and tips |
| [Skills Progressive Disclosure](docs/skills-progressive-disclosure.md) | How skills load context on demand — progressive disclosure design and reference splitting |
| [ClaudeCode Plugins Guide](docs/plugins.md) | Plugins overview — structure, plugin.json, marketplace, installation, updates, and tips |
| [ClaudeCode SubAgents Guide](docs/sub-agents.md) | SubAgents overview — built-in agents, custom creation, practical patterns, and tips |
| [ClaudeCode Hooks Guide](docs/hooks.md) | Hooks overview — lifecycle events, configuration structure, hookSpecificOutput, and deterministic automation |
| [Harness Design Guide](docs/harness.md) | Anthropic's "agentic harness" design — multi-agent generator/evaluator pattern, sprint contracts, and Claude Code applications |
| [ClaudeCode Best Practices](docs/best-practices.md) | Best practices based on official documentation (kept fresh via the claude-docs-sync skill) |
| [Memory (CLAUDE.md) Guide](docs/memory.md) | Memory system — CLAUDE.md hierarchy, auto-memory, imports, and context management |
| [Session History & `--resume`](docs/session-history.md) | The session JSONL store, how `--resume` matches sessions by `cwd`, the safe project-directory rename procedure, and Zed/ACP session visibility |
| [GitHub Actions Claude Code Review](docs/github-actions-claude-code-review.md) | Setting up the claude[bot] PR review action — the two-layer permission model, copy-paste workflow, troubleshooting, and the `/setup-github-claude-code-review` skill |
| [Zed Editor Guide](docs/zed.md) | Using Zed as the ACP host for Claude Code — core usage, recommended shortcuts, dev workflow, and parallel agents across projects |

---

<a id="jarvis-1"></a>

# ジャーヴィス

[English version is above](#jarvis)

AI を活用した開発における試行錯誤・実験・検証の記録と、現時点のベストプラクティスをまとめる個人リポジトリ。

## Why JARVIS?

"JARVIS" は Tony Stark の J.A.R.V.I.S. へのオマージュである。AI・LLM 時代に、自分だけの "Just a Really Very Intelligent System" を構築する試みとして名付けた。

LLM/AI の進化すべてに追従するのは現実的に難しい。しかし「AI を使って開発するためのグランドデザイン」の輪郭が見え始めてきた。このリポジトリは、その試行錯誤の過程を GitHub 上に記録・可視化し、再現性・バージョン管理を重視しながら、開発プロセスを継続的に改善していくことを目的としている。

### 方針

- **完成よりも継続** — 完璧を目指さず、ステップ・バイ・ステップで改善する
- **AI は手段、人間が主体** — 設計・判断・責任は常に人間が担う
- **再現性を意識した記録** — 環境が変わっても再構築できるよう具体的に残す
- **鮮度を保つ更新** — 古い情報は積極的に更新または削除する

## ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [使用ツールスタック](docs/tool-stack.md) | AI エージェント・MCP サーバーなど使用ツール一覧 |
| [ClaudeCode の設定ファイル一覧と役割](docs/config-files.md) | 6 つの JSON 設定ファイルの目的・スコープ・優先順位・対応表 |
| [Claude Desktop の設定ファイル](docs/claude-desktop.md) | `claude_desktop_config.json` の詳細と ClaudeCode との違い |
| [MCP サーバーの追加方法ガイド](docs/mcp-setup.md) | `claude mcp add` の構文・JSON からの変換方法・スコープの使い分け |
| [ClaudeCode スラッシュコマンドガイド](docs/slash-commands.md) | 組み込みコマンド・バンドルスキル — コンテキスト管理・セッション制御・生産性ワークフロー |
| [ClaudeCode Skills ガイド](docs/skills.md) | Skills の全容 — 前提知識・使い方・frontmatter・設計パターン・Tips |
| [Skills の段階的開示](docs/skills-progressive-disclosure.md) | Skills が必要な時だけコンテキストを読み込む仕組み — progressive disclosure 設計とリファレンス分割 |
| [ClaudeCode Plugins ガイド](docs/plugins.md) | Plugins の全容 — 構造・plugin.json・マーケットプレイス・インストール・アップデート・Tips |
| [ClaudeCode SubAgents ガイド](docs/sub-agents.md) | SubAgents の全容 — 組み込みエージェント・カスタム作成・実践パターン・Tips |
| [ClaudeCode Hooks ガイド](docs/hooks.md) | Hooks の全容 — ライフサイクルイベント・設定構造・hookSpecificOutput・決定論的な自動実行 |
| [ハーネス設計ガイド](docs/harness.md) | Anthropic 提唱の「agentic harness」— マルチエージェントの生成器/評価器パターン・スプリント契約・ClaudeCode への応用 |
| [ClaudeCode のベストプラクティス](docs/best-practices.md) | 公式ドキュメントに基づくベストプラクティス（claude-docs-sync スキルで鮮度を維持） |
| [メモリ（CLAUDE.md）ガイド](docs/memory.md) | メモリシステム — CLAUDE.md の階層・auto-memory・インポート・コンテキスト管理 |
| [セッション履歴と `--resume`](docs/session-history.md) | セッション JSONL ストア・`--resume` が `cwd` で突合する仕組み・プロジェクトディレクトリの安全なリネーム手順・Zed/ACP セッションの可視性 |
| [GitHub Actions Claude Code レビュー設定](docs/github-actions-claude-code-review.md) | claude[bot] による PR 自動レビューの設定 — 2 層の権限モデル・コピペ用 workflow・トラブルシュート・`/setup-github-claude-code-review` スキル |
| [Zed エディタ活用ガイド](docs/zed.md) | Claude Code の ACP ホストとしての Zed — 主要な使い方・推奨ショートカット・開発ワークフロー・複数プロジェクトの Parallel Agents |
