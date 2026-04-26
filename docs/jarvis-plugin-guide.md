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

## 初回セットアップ（3 ステップ）

任意のプロジェクトディレクトリで `/jarvis` を実行すると、JARVIS が `AskUserQuestion` で 3 問を伺う。

```
/jarvis

JARVIS: はじめまして、BOSS。私は JARVIS でございます。
        まず、BOSS の事業や活動について教えていただけますでしょうか。

BOSS: 個人開発で AI 関連のプロジェクト

JARVIS: ありがとうございます。
        続いて、現在の目標や日々お困りのことがあれば教えていただけますでしょうか。

BOSS: SaaS を作って月 10 万を目指している。タスクが散らかるのが悩み

JARVIS: ブラウザで組織状況を確認できるダッシュボードがございます。
        セットアップなさいますか？（補足: 現バージョンでは未実装）

BOSS: いいえ

→ .jarvis/ が自動生成される（完了）
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

## サブ職能・マイグレーション・Phase ロードマップ

サブ職能（部署内の専門分化）の設計、cc-company からの自動マイグレーション、Phase ロードマップの詳細は @docs/jarvis-plugin-architecture.md を参照。

要点だけ:

- サブ職能は Phase 2 で全部署横断の仕組みとして実装予定
- 既存 `.company/` を持つプロジェクトで `/jarvis` を実行すると、JARVIS が `.jarvis/` への自動マイグレーションを提案する

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
