# JARVIS Plugin ガイド

> 最終更新: 2026-04-26

`/jarvis` コマンドを呼び出すと、JARVIS（Just a Really Very Intelligent System）が BOSS 専用の窓口（秘書機能）兼執行責任者（COO 機能）として動作する。本ガイドはインストール手順・使い方・部署運用のフローをまとめる。

## 概要

- **コマンド**: `/jarvis`
- **配置形式**: ClaudeCode のローカル marketplace + Plugin
- **マーケットプレース配置**: `~/.claude/plugins/jarvis/`
- **状態フォルダ**: 各プロジェクトの `.jarvis/`
- **設計の元**: [Shin-sibainu/cc-company](https://github.com/Shin-sibainu/cc-company)（MIT）の派生物

詳細な内部設計は @docs/jarvis-plugin-architecture.md を参照。

## インストール（初回のみ）

ClaudeCode セッション内で以下を実行する。

```
/plugin marketplace add /Users/yoshi/.claude/plugins/jarvis
/plugin install jarvis@jarvis
```

成功すると `/plugin` で `jarvis@jarvis` が user スコープでインストールされていることを確認できる。

> ローカル marketplace のため Git push や公開は不要。BOSS のローカル環境のみで完結する。

## 初回セットアップ（2 問 + 通知）

任意のプロジェクトディレクトリで `/jarvis` を実行すると、JARVIS が `AskUserQuestion` で 2 問を伺い、完了時にダッシュボード通知を出す。

```
/jarvis

JARVIS: はじめまして、BOSS。私は JARVIS でございます。
        まず、BOSS の事業や活動について教えていただけますでしょうか。

BOSS: 個人開発で AI 関連のプロジェクト

JARVIS: ありがとうございます。
        続いて、現在の目標や日々お困りのことがあれば教えていただけますでしょうか。

BOSS: SaaS を作って月 10 万を目指している。タスクが散らかるのが悩み

→ .jarvis/ が自動生成される
→ 完了メッセージ末尾に「ダッシュボードは Phase 4 で対応予定」の通知が含まれる
```

完了後、以下のディレクトリ構造が生成される。

```
.jarvis/
├── CLAUDE.md              ← 組織ルール（オーナープロフィール含む）
└── secretary/
    ├── CLAUDE.md           ← JARVIS の振る舞い・口調ルール
    ├── inbox/              ← クイックキャプチャ
    ├── todos/
    │   └── YYYY-MM-DD.md   ← 今日の TODO
    └── notes/              ← 壁打ち・意思決定ログ
```

## 日常の運営

### TODO 管理

```
/jarvis

JARVIS: 何かご用がございましたらお申し付けください。

BOSS: 今日やることを教えて

JARVIS: 本日の TODO は以下でございます。
  - [ ] クライアント A への見積もり送付
  - [ ] LP 設計書のレビュー
```

### 壁打ち・相談

```
BOSS: 競合サービスについて整理したい

JARVIS: 承知いたしました。私からいくつか観点を提示しつつ整理いたします。
  → secretary/notes/2026-04-26-competitor-research.md に保存
```

### 部署の自然な追加

同じ領域のタスクが 2 回以上繰り返されると、JARVIS が部署作成を提案する。

```
BOSS: 海外のトレンドも調べて

JARVIS: リサーチのご依頼が増えてまいりました。
        リサーチ部門を作成いたしましょうか？
        専用フォルダで調査結果を体系的に管理できます。

BOSS: 作って

→ .jarvis/research/ が自動生成される
```

## 用意されている部署（必要に応じて追加）

| 部署 | フォルダ | 担当領域 |
|---|---|---|
| 秘書室（常設） | `secretary/` | TODO 管理、壁打ち、メモ、相談 |
| PM | `pm/` | プロジェクト進捗、チケット管理 |
| リサーチ | `research/` | 市場調査、競合分析、技術調査 |
| マーケティング | `marketing/` | コンテンツ企画、SNS、キャンペーン |
| 開発 | `engineering/` | 技術ドキュメント、設計、デバッグ |
| 経理 | `finance/` | 請求書、経費、売上管理 |
| 営業 | `sales/` | クライアント管理、提案書 |
| クリエイティブ | `creative/` | デザインブリーフ、ブランド管理 |
| 人事 | `hr/` | 採用管理、チーム管理 |

各部署のテンプレート詳細は `~/.claude/plugins/jarvis/plugins/jarvis/skills/jarvis/references/departments.md` を参照。

## サブ職能（専門分化）

v0.2.0（Phase 2）から、各部署内に専門領域ごとのサブ職能フォルダを追加できる。

### 標準サブ職能リスト

| 部署 | サブ職能 |
|---|---|
| `engineering/` | frontend, backend, fullstack, ui-ux, qa, infra, database, security, ai, data |
| `creative/` | web-designer, graphic-designer, animation, illustrator, brand-designer |
| `marketing/` | content, sns, ads, seo, pr, growth |
| `sales/` | inside, field, customer-success, partner |
| `pm/` | product, project, program |
| `research/` | market, competitor, tech, user |
| `hr/` | recruit, team-ops, culture |
| `finance/` | bookkeeping, tax, controlling |

### 追加フロー

1. **部署作成時**: JARVIS が「初期のサブ職能を追加しますか？」と確認（`AskUserQuestion` の multiSelect）
2. **運用中**: 部署内のタスクが特定領域に偏ってきた場合、JARVIS が「直近のタスク 3 件」を引用してサブ職能の追加を提案

「最初は粗く、必要に応じて細分化」の原則に従い、デフォルトはサブ職能なしのフラット構造。

### 既存フラット構造との共存

既に `[department]/docs/` `[department]/debug-log/` がある状態でサブ職能を追加する場合、既存ファイルは温存し、サブ職能フォルダを並列追加する。既存ファイルの自動移動は行わない。

詳細は `~/.claude/plugins/jarvis/plugins/jarvis/skills/jarvis/references/sub-roles.md` を参照。

## マイグレーション・Phase ロードマップ

cc-company からの自動マイグレーション、Phase ロードマップの詳細は @docs/jarvis-plugin-architecture.md を参照。

要点: 既存 `.company/` を持つプロジェクトで `/jarvis` を実行すると、JARVIS が `.jarvis/` への自動マイグレーションを提案する。

## Git 管理について

`.jarvis/` 配下は個人情報・機密情報を含む可能性があるため、デフォルトでは `.gitignore` への追加を推奨する。BOSS が個別にコミット可否を判断する。

```bash
# プロジェクトの .gitignore に追加
.jarvis/
```

## 関連ドキュメント

- @docs/jarvis-plugin-architecture.md — Plugin の内部設計、cc-company 由来の改変点
- @docs/skills-guide.md — ClaudeCode Skills の全容
- @docs/plugins-guide.md — ClaudeCode Plugins の全容
