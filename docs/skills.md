# ClaudeCode Skills ガイド

> 出典: [Extend Claude with skills](https://code.claude.com/docs/en/skills) / [Extend Claude Code](https://code.claude.com/docs/en/features-overview) / [anthropics/claude-code](https://github.com/anthropics/claude-code) (2026-03-25時点)

Skills は ClaudeCode の拡張機能であり、`SKILL.md` ファイルにマークダウンで記述した「ドメイン知識」や「再利用可能なワークフロー」を Claude に与える仕組みである。CLAUDE.md が毎セッション常時読み込まれるのに対し、Skills は**必要な時だけオンデマンドでロード**される。

Skills は [Agent Skills](https://agentskills.io) オープンスタンダードに準拠しており、ClaudeCode 独自の拡張（呼び出し制御・サブエージェント実行・動的コンテキスト注入）も備える。

---

## 前提知識

Skills を効果的に使うために理解しておくべき概念を整理する。

### コンテキストウィンドウとの関係

| 項目 | ロードタイミング | コンテキストコスト |
|------|----------------|-------------------|
| CLAUDE.md | セッション開始時 | 毎リクエスト（全文） |
| Skills（description） | セッション開始時 | 毎リクエスト（低コスト） |
| Skills（本文） | 呼び出し時のみ | 呼び出し後のリクエスト |
| MCP サーバー | セッション開始時 | 毎リクエスト（ツール定義） |
| Subagent | 起動時 | メインセッションから隔離 |
| Hooks | トリガー時 | ゼロ（外部実行） |

**重要**: Skills の description はコンテキストの 2%（フォールバック: 16,000文字）を上限としてロードされる。スキル数が多い場合はこの上限を超え、一部が除外される。`/context` で警告を確認できる。上限の変更は環境変数 `SLASH_COMMAND_TOOL_CHAR_BUDGET` で可能。

### CLAUDE.md / Rules / Skills の使い分け

| 機能 | ロードタイミング | スコープ | 最適な用途 |
|------|----------------|---------|-----------|
| CLAUDE.md | 毎セッション | プロジェクト全体 | コーディング規約、ビルドコマンド |
| `.claude/rules/` | 毎セッション or ファイルパス一致時 | ファイルパス単位で限定可能 | 言語別・ディレクトリ別ガイドライン |
| Skills | オンデマンド | タスク単位 | リファレンス資料、再利用ワークフロー |

**判断基準**: 「毎セッション必要か？」→ Yes なら CLAUDE.md。「特定ファイル操作時だけ？」→ Rules。「必要な時だけ？」→ Skills。CLAUDE.md は 200行以下を目安に保ち、肥大化したらリファレンス内容を Skills に移す。

### Skills と類似機能の比較

| 比較軸 | Skill | Subagent | MCP |
|--------|-------|----------|-----|
| 何であるか | 再利用可能な指示・知識 | 隔離されたワーカー | 外部サービスとの接続 |
| 主な利点 | コンテキスト間で共有可能 | コンテキスト隔離 | 外部データ・アクション |
| 最適な用途 | リファレンス、ワークフロー | 大量ファイル読み込み、並列作業 | DB クエリ、Slack 投稿 |

**組み合わせ**: MCP がサービスへの接続を提供し、Skill がその使い方を教える。例えば、MCP でデータベースに接続し、Skill でスキーマやクエリパターンを Claude に教える。

---

## Skills の基本

### ディレクトリ構造

各 Skill は独立したディレクトリで、`SKILL.md` がエントリポイントとなる。

```
my-skill/
├── SKILL.md           # メインの指示（必須）
├── template.md        # Claude が埋めるテンプレート（任意）
├── examples/
│   └── sample.md      # 期待する出力例（任意）
├── references/
│   └── api-spec.md    # 詳細リファレンス（任意）
└── scripts/
    └── validate.sh    # Claude が実行するスクリプト（任意）
```

`SKILL.md` は 500行以下に保ち、詳細なリファレンスは別ファイルに分離する。`SKILL.md` から相対パスでリンクし、Claude が必要に応じて読み込めるようにする。

### 配置場所とスコープ

| スコープ | パス | 適用範囲 |
|---------|------|---------|
| Enterprise | マネージド設定で配布 | 組織内の全ユーザー |
| Personal（個人） | `~/.claude/skills/<skill-name>/SKILL.md` | 全プロジェクト共通 |
| Project（プロジェクト） | `.claude/skills/<skill-name>/SKILL.md` | 当該プロジェクトのみ |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Plugin が有効な場所 |

同名スキルの優先順位: **Enterprise > Personal > Project**。Plugin スキルは `plugin-name:skill-name` の名前空間を持つため競合しない。

**サブディレクトリの自動検出**: `packages/frontend/` 内のファイルを操作すると、`packages/frontend/.claude/skills/` のスキルも自動検出される（モノレポ対応）。

### SKILL.md の書き方

```yaml
---
name: my-skill
description: このスキルが何をするか、いつ使うかの説明
---

スキルの本文（マークダウン形式の指示）
```

---

## frontmatter リファレンス

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | No | スキル名。省略時はディレクトリ名を使用。小文字・数字・ハイフンのみ（最大64文字） |
| `description` | 推奨 | スキルの説明。Claude が自動ロードの判断に使用する。省略時は本文の最初の段落を使用 |
| `argument-hint` | No | オートコンプリートで表示される引数のヒント。例: `[issue-number]` |
| `disable-model-invocation` | No | `true` にすると Claude の自動ロードを禁止。手動呼び出し専用にする。デフォルト: `false` |
| `user-invocable` | No | `false` にすると `/` メニューに非表示。ユーザーが直接呼び出す必要のない背景知識向き。デフォルト: `true` |
| `allowed-tools` | No | スキル実行中に許可なしで使えるツール。例: `Read, Grep, Glob` |
| `model` | No | スキル実行時のモデル指定 |
| `effort` | No | エフォートレベル。`low` / `medium` / `high` / `max`（Opus 4.6 のみ） |
| `context` | No | `fork` でサブエージェント内での隔離実行を有効化 |
| `agent` | No | `context: fork` 時に使用するサブエージェントの種類 |
| `hooks` | No | スキルのライフサイクルにスコープされた Hooks |

### 呼び出し制御の組み合わせ

| frontmatter 設定 | ユーザーが呼べる | Claude が呼べる | コンテキストへのロード |
|-----------------|---------------|---------------|---------------------|
| （デフォルト） | Yes | Yes | description は常時、本文は呼び出し時 |
| `disable-model-invocation: true` | Yes | No | コンテキストに一切ロードされない |
| `user-invocable: false` | No | Yes | description は常時、本文は呼び出し時 |

**使い分け**:
- `disable-model-invocation: true` → デプロイ、コミット、Slack 投稿など**副作用のあるアクション**。Claude が勝手に実行するのを防ぐ
- `user-invocable: false` → レガシーシステムの背景知識など、Claude が必要に応じて参照するが、ユーザーが `/` で呼ぶ必要がない情報

---

## 文字列置換（変数）

スキル本文で使える動的変数:

| 変数 | 説明 |
|------|------|
| `$ARGUMENTS` | `/skill-name` に続けて渡されたすべての引数 |
| `$ARGUMENTS[N]` / `$N` | 0ベースインデックスで個別の引数にアクセス（例: `$0` = 最初の引数） |
| `${CLAUDE_SESSION_ID}` | 現在のセッション ID |
| `${CLAUDE_SKILL_DIR}` | スキルの `SKILL.md` が存在するディレクトリパス |

**引数の例**:

```yaml
---
name: migrate-component
description: コンポーネントをフレームワーク間で移行する
---

$0 コンポーネントを $1 から $2 に移行する。
既存の動作とテストを維持すること。
```

```
/migrate-component SearchBar React Vue
```

→ `$0` = `SearchBar`、`$1` = `React`、`$2` = `Vue`

---

## 動的コンテキスト注入

`` !`<command>` `` 構文でシェルコマンドをスキル本文に埋め込む。コマンドは**スキルが Claude に送信される前に実行**され、出力がプレースホルダーを置換する。

```yaml
---
name: pr-summary
description: PR の変更内容を要約する
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR コンテキスト
- PR diff: !`gh pr diff`
- PR コメント: !`gh pr view --comments`
- 変更ファイル: !`gh pr diff --name-only`

## タスク
この PR を要約して...
```

**実行順序**: 各 `` !`<command>` `` が即座に実行 → 出力がプレースホルダーを置換 → Claude は展開済みのプロンプトのみを受け取る。これは前処理であり、Claude が実行するものではない。

---

## サブエージェント実行（context: fork）

`context: fork` を設定すると、スキルは隔離されたサブエージェント内で実行される。スキル本文がサブエージェントのプロンプトとなり、会話履歴にはアクセスできない。

```yaml
---
name: deep-research
description: トピックを徹底的に調査する
context: fork
agent: Explore
---

$ARGUMENTS を徹底的に調査する:

1. Glob と Grep でファイルを検索
2. コードを読み込んで分析
3. 具体的なファイル参照付きで所見を要約
```

| `context: fork` の場合 | 通常の場合 |
|----------------------|-----------|
| サブエージェントのシステムプロンプト + SKILL.md 本文 | メイン会話のコンテキスト + SKILL.md 本文 |
| 会話履歴にアクセス不可 | 会話履歴にアクセス可能 |
| メインコンテキストを消費しない | メインコンテキストを消費する |

**`agent` フィールド**: `Explore`（読み取り専用探索）、`Plan`（設計・計画）、`general-purpose`（汎用）、またはカスタムサブエージェント（`.claude/agents/`）を指定可能。省略時は `general-purpose`。

> **注意**: `context: fork` は明確なタスク指示があるスキルでのみ意味がある。「この API 規約に従え」のようなガイドラインだけのスキルでは、サブエージェントがガイドラインを受け取るだけで実行すべきタスクがなく、意味のある出力を返さない。

---

## スキルの種類と設計パターン

### リファレンス型（知識・規約）

Claude の作業に適用される知識を提供する。会話内でインラインで実行される。

```yaml
---
name: api-conventions
description: REST API の設計規約。API エンドポイント作成時に使用
---

# API 規約

- URL パスは kebab-case
- JSON プロパティは camelCase
- リストエンドポイントには必ずページネーション
- URL パスでバージョニング（/v1/, /v2/）
```

### タスク型（ワークフロー）

特定のアクションをステップバイステップで実行する。`disable-model-invocation: true` で手動トリガーにするのが一般的。

```yaml
---
name: deploy
description: アプリケーションを本番環境にデプロイする
context: fork
disable-model-invocation: true
---

$ARGUMENTS をデプロイする:

1. テストスイートを実行
2. アプリケーションをビルド
3. デプロイターゲットにプッシュ
4. デプロイが成功したことを検証
```

### ガードレール型（品質・安全性）

特定の条件で自動発火し、品質や安全性を担保する。

```yaml
---
name: infra-decompose
description: |
  インフラとアプリケーションが同一フィーチャーに混在している場合に発火し、
  スコープの分割を提案する。
---

## 発火条件
以下が同一フィーチャーに混在している場合:
- インフラ層: Terraform、S3、ECS...
- アプリケーション層: UI、コンポーネント...

## 分解の原則
...
```

### ビジュアル出力型（HTML生成）

スクリプトをバンドルし、ブラウザで開けるインタラクティブな HTML を生成する。

```yaml
---
name: codebase-visualizer
description: コードベースの対話的ツリービューを生成する
allowed-tools: Bash(python *)
---

# Codebase Visualizer

プロジェクトルートから可視化スクリプトを実行:

\`\`\`bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
\`\`\`
```

---

## バンドルスキル（組み込み）

ClaudeCode に同梱されており、全セッションで使用可能:

| スキル | 用途 |
|--------|------|
| `/batch <instruction>` | 大規模な変更を並列で実行。5〜30の独立ユニットに分解し、各 worktree でエージェントが作業・テスト・PR 作成 |
| `/claude-api` | Claude API / Agent SDK のリファレンスをロード。`anthropic` インポート時に自動発火 |
| `/debug [description]` | セッションのデバッグログを解析してトラブルシューティング |
| `/loop [interval] <prompt>` | プロンプトを定期実行（例: `/loop 5m デプロイ完了したか確認`） |
| `/simplify [focus]` | 最近変更したファイルのコード品質を 3 並列エージェントでレビュー・修正 |

---

## パーミッション制御

### スキルへのアクセス制限

```
# Skill ツール自体を無効化（全スキルへのアクセスを拒否）
Skill

# 特定スキルのみ許可
Skill(commit)
Skill(review-pr *)

# 特定スキルを拒否
Skill(deploy *)
```

構文: `Skill(name)` = 完全一致、`Skill(name *)` = プレフィックスマッチ。

### スキル内のツール制限

`allowed-tools` でスキル実行中に使えるツールを制限する:

```yaml
---
name: safe-reader
description: ファイルを変更せずに読み取り専用で探索する
allowed-tools: Read, Grep, Glob
---
```

---

## ベストプラクティス

### description の書き方

description は Claude がスキルを自動ロードするかどうかの判断基準である。

**悪い例**:
```yaml
description: API 関連の処理
```

**良い例**:
```yaml
description: |
  REST API の設計規約。API エンドポイント作成、レスポンス形式の設計、
  バリデーション実装時に使用。「API」「エンドポイント」「REST」に関する実装時に自動ロード。
```

- **具体的なトリガーフレーズ**を含める（ユーザーが使いそうなキーワード）
- 「いつ使うか」を明示する
- 曖昧な説明は Claude の誤ロードや見逃しの原因になる

### SKILL.md のサイズ管理

- **SKILL.md は 500行以下**に保つ
- 詳細な API ドキュメント、コード例集、仕様書は別ファイルに分離する
- `SKILL.md` から相対パスで参照し、Claude が必要に応じて読み込めるようにする

```markdown
## 追加リソース

- 完全な API 詳細は [reference.md](reference.md) を参照
- 使用例は [examples.md](examples.md) を参照
```

### 副作用のあるスキルの保護

デプロイ、コミット、メッセージ送信など副作用のあるワークフローは必ず手動トリガーにする:

```yaml
disable-model-invocation: true
```

これにより:
- Claude が勝手に実行することを防ぐ
- description がコンテキストにロードされないため、コンテキストコストもゼロになる
- ユーザーが `/skill-name` で明示的に呼び出す必要がある

### スキル数の管理

- description のコンテキスト予算はウィンドウの 2%（フォールバック: 16,000文字）
- スキルが多すぎると一部が除外される。`/context` で確認
- 使用頻度の低いスキルは `disable-model-invocation: true` にしてコンテキストから除外するか、削除を検討する

### ホットリロード

`~/.claude/skills/` や `.claude/skills/` のスキルは**セッション再起動なしで自動反映**される。作成・編集後すぐにテスト可能。

---

## Tips

### extended thinking の有効化

スキル本文に `ultrathink` という単語を含めると extended thinking が有効化される。

### 既存 `.claude/commands/` との互換性

`.claude/commands/deploy.md` と `.claude/skills/deploy/SKILL.md` は同じ `/deploy` コマンドを作成する。既存の commands ファイルはそのまま動作するが、同名の場合は Skills が優先される。Skills はサポートファイル（テンプレート、スクリプト）を含められる点で commands より強力である。

### `--add-dir` からのスキル検出

`--add-dir` で追加したディレクトリ内の `.claude/skills/` も自動検出される。ライブ変更検出にも対応しており、セッション中の編集が即時反映される。

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| スキルが発火しない | description にユーザーが使うキーワードを含めているか確認。`What skills are available?` で Claude に認識されているか確認。`/skill-name` で直接呼び出してテスト |
| スキルが頻繁に誤発火する | description をより具体的にする。`disable-model-invocation: true` で手動呼び出し専用にする |
| Claude がスキルを認識しない | スキル数が多くてコンテキスト予算を超えている可能性。`/context` で警告を確認 |

---

## 現在の個人スキル一覧

`~/.claude/skills/` に配置されている Personal スコープのスキル:

| スキル | 種別 | 用途 |
|--------|------|------|
| `aws-ecs-fargate` | リファレンス | ECS Fargate + RDS + ElastiCache の Terraform パターン |
| `aws-static-hosting` | リファレンス | S3 + CloudFront 静的サイトホスティングの Terraform パターン |
| `ecs-deploy-troubleshooting` | リファレンス | ECS デプロイ障害の調査手順と過去事例 |
| `github-actions-aws-oidc` | リファレンス | GitHub Actions OIDC → AWS デプロイパターン |
| `infra-decompose` | ガードレール | インフラ+アプリ混在フィーチャーのスコープ分割提案 |

すべて Personal スコープ（全プロジェクト共通）で、`disable-model-invocation` なし（Claude が自動ロード可能）。実務パターンに基づくリファレンス型スキル群。

---

## 関連ドキュメント

- [Extend Claude with skills](https://code.claude.com/docs/en/skills) — 公式 Skills ドキュメント
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — 拡張機能の全体像
- [Subagents](https://code.claude.com/docs/en/sub-agents) — サブエージェントとの連携
- [Hooks](https://code.claude.com/docs/en/hooks) — イベント駆動の自動化
- [Plugins](https://code.claude.com/docs/en/plugins) — Skills のパッケージング・配布
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
