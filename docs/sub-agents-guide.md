# ClaudeCode SubAgents ガイド

> 出典: [Subagents](https://code.claude.com/docs/en/sub-agents) / [Extend Claude Code](https://code.claude.com/docs/en/features-overview) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [anthropics/claude-code](https://github.com/anthropics/claude-code) (2026-03-26時点)

SubAgents は ClaudeCode のメインセッションから**隔離されたコンテキスト**でタスクを実行する自律的なワーカーである。大量のファイル読み込みや並列調査をサブエージェントに委任することで、メインの会話コンテキストをクリーンに保ちながら、専門的なタスクを効率的に処理できる。

---

## 前提知識

### SubAgents の基本概念

SubAgents はメインセッションとは**別のコンテキストウィンドウ**で動作する。メインセッションの会話履歴にはアクセスできず、作業結果のサマリーだけがメインに返される。

```
メインセッション ─── タスク委任 ──→ SubAgent（隔離コンテキスト）
      ↑                                    │
      └──── サマリーを受け取る ←────────────┘
```

この「コンテキスト隔離」が SubAgents の最大の利点である。サブエージェントが数十ファイルを読み込んでも、メインセッションのコンテキストは消費されない。

### コンテキストウィンドウとの関係

| 項目 | ロードタイミング | メインへの影響 |
|------|----------------|---------------|
| CLAUDE.md | セッション開始時 | 毎リクエスト消費 |
| Skills（description） | セッション開始時 | 毎リクエスト消費（低コスト） |
| Skills（本文） | 呼び出し時 | 呼び出し後に消費 |
| **SubAgent** | **起動時** | **隔離 — メインを消費しない** |
| MCP サーバー | セッション開始時 | 毎リクエスト消費 |
| Hooks | トリガー時 | ゼロ（外部実行） |

SubAgent 起動時にロードされるもの:
- システムプロンプト（親と共有、キャッシュ効率のため）
- `skills:` フィールドで指定された Skills の全文
- CLAUDE.md と git status（親から継承）
- リードエージェントがプロンプトで渡したコンテキスト

**メインの会話履歴や、メインで呼び出された Skills は継承しない。**

### Skills / SubAgents / Agent Teams の使い分け

| 比較軸 | Skill | SubAgent | Agent Teams |
|--------|-------|----------|-------------|
| 何であるか | 再利用可能な指示・知識 | 隔離されたワーカー | 独立した複数セッション |
| コンテキスト | メインと共有 | メインから隔離 | 各セッションが完全独立 |
| コミュニケーション | — | 結果をメインに返す | チームメイト同士で直接通信 |
| 最適な用途 | リファレンス、ワークフロー | 調査、レビュー、並列作業 | 複雑な協調作業、競合仮説の検証 |
| トークンコスト | メインコンテキストを消費 | 低い（サマリーのみ返却） | 高い（各セッションが独立インスタンス） |

**判断基準**:
- 「知識を共有したい」→ Skill
- 「作業を委任して結果だけ欲しい」→ SubAgent
- 「複数のワーカーが互いに議論・協調する必要がある」→ Agent Teams

**移行ポイント**: 並列サブエージェントでコンテキスト上限に達する場合や、サブエージェント同士の通信が必要な場合は Agent Teams への移行を検討する。

### Skills と SubAgents の組み合わせ

Skills と SubAgents は双方向で連携できる:

| アプローチ | システムプロンプト | タスク | 追加ロード |
|-----------|-------------------|--------|-----------|
| Skill に `context: fork` | エージェントタイプ（Explore 等）のプロンプト | SKILL.md の本文 | CLAUDE.md |
| SubAgent に `skills` フィールド | サブエージェントのマークダウン本文 | Claude の委任メッセージ | プリロードされた Skills + CLAUDE.md |

---

## 組み込みサブエージェント

ClaudeCode には 3 つの組み込みサブエージェントがある。タスクの性質に応じて自動的に選択される。

| エージェント | モデル | 用途 | 特徴 |
|-------------|--------|------|------|
| **Explore** | Haiku | コードベースの探索・発見・分析 | 読み取り専用、高速。Glob・Grep・Read に最適化 |
| **Plan** | — | Plan Mode でのリサーチ・コンテキスト収集 | コードを変更しない。設計・計画フェーズ向け |
| **general-purpose** | — | 複雑なマルチステップ操作 | 探索とコード変更の両方が可能。デフォルト |

**Explore の活用例**: 「認証システムのトークンリフレッシュの仕組みを調査して」のような読み取り専用の調査タスクに最適。大量のファイルを読み込んでもメインコンテキストを汚さない。

---

## カスタムサブエージェントの作成

### ファイル形式

サブエージェントは YAML frontmatter + マークダウン本文のファイルで定義する。

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

frontmatter がサブエージェントの設定（使えるツール、モデル等）を定義し、マークダウン本文がサブエージェントの**システムプロンプト**となる。

### 配置場所とスコープ

| スコープ | パス | 適用範囲 | Git 管理 |
|---------|------|---------|----------|
| Managed | 企業管理設定で配布 | 組織内の全ユーザー | — |
| CLI | `--agent` フラグ or `--agents` JSON | 当該セッションのみ | しない |
| Project | `.claude/agents/<name>.md` | 当該プロジェクト | **する** |
| User | `~/.claude/agents/<name>.md` | 全プロジェクト共通 | しない |
| Plugin | `<plugin>/agents/<name>.md` | Plugin が有効な場所 | — |

**同名サブエージェントの優先順位**: **Managed > CLI フラグ > Project > User > Plugin**

**使い分え**:
- **Project**: チームで共有したいレビュアーや専門エージェント → `.claude/agents/` に配置して Git 管理
- **User**: 個人で全プロジェクトに使いたいエージェント → `~/.claude/agents/` に配置
- **CLI**: 一時的な実験用エージェント → `--agents` フラグで JSON 定義

### frontmatter リファレンス

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | 推奨 | エージェント識別子。小文字・数字・ハイフン |
| `description` | string | 推奨 | Claude がエージェントを自動選択する判断基準。`<example>` ブロックでトリガー条件を具体的に示すと効果的 |
| `tools` | string/string[] | No | 使用可能なツール。例: `Read, Grep, Glob, Bash` |
| `model` | string | No | 使用モデル。`sonnet`, `opus`, `haiku`, `inherit`（親と同じ） |
| `color` | string | No | ステータスラインの表示色。`blue`, `green`, `red` 等 |
| `effort` | string | No | エフォートレベル。`low` / `medium` / `high` / `max` |
| `skills` | string[] | No | 起動時にプリロードする Skills のリスト |
| `hooks` | object | No | エージェントのライフサイクルにスコープされた Hooks |
| `allowed-tools` | string/string[] | No | 許可なしで使えるツール |

### description の書き方（トリガー設計）

`description` はClaudeがサブエージェントを自動選択するかどうかの判断基準である。`<example>` ブロックを含めることで、トリガー精度を大幅に向上させる。

**効果的な description の例**:

```yaml
description: |
  Use this agent when reviewing code for security vulnerabilities. Examples:

  <example>
  Context: User has just implemented authentication logic
  user: "Review this code for security issues"
  assistant: "I'll use the security-reviewer agent to analyze your code"
  <commentary>
  Security review is the agent's core expertise
  </commentary>
  </example>
```

**ポイント**:
- 「いつ使うか」を明確にする
- `<example>` ブロックで具体的なトリガーシーンを示す
- ユーザーが自然に使う言葉を含める

### システムプロンプトの設計パターン

frontmatter の下のマークダウン本文がサブエージェントのシステムプロンプトとなる。

**分析型**（コードレビュー、セキュリティ監査）:

```markdown
You are a senior code reviewer ensuring high standards of code quality.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- No duplicated code
- Proper error handling
- No exposed secrets or API keys

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

**調査型**（リサーチ、探索）:

```markdown
You are a codebase researcher. When given a topic:

1. Search for relevant files using Glob and Grep
2. Read and analyze the code thoroughly
3. Trace dependencies and call chains
4. Summarize findings with specific file:line references
```

**生成型**（コード生成、ドキュメント作成）:

```markdown
You are an API endpoint developer. Follow team conventions:

1. Read existing endpoints for patterns
2. Implement the new endpoint
3. Add validation and error handling
4. Write tests
5. Update API documentation
```

---

## SubAgents の使い方

### Claude に委任を指示する

自然言語でサブエージェントの使用を指示する:

```
サブエージェントを使って、認証システムのトークンリフレッシュの仕組みを調査して。
```

```
サブエージェントを使ってこのコードのセキュリティレビューをして。
```

```
サブエージェントを使って、再利用できる既存の OAuth ユーティリティがないか調査して。
```

カスタムサブエージェントが定義されていれば、Claude は description を基に最適なエージェントを自動選択する。

### CLI からの起動

```bash
# セッション全体を特定のサブエージェントとして起動
claude --agent code-reviewer

# 一時的なサブエージェントを JSON で定義
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on quality and security.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors and provide fixes."
  }
}'
```

### デフォルトエージェントの設定

`.claude/settings.json` にデフォルトのサブエージェントを設定できる:

```json
{
  "agent": "code-reviewer"
}
```

この設定により、セッション開始時に `code-reviewer` のシステムプロンプトとツール制限が適用される。CLI フラグ（`--agent`）で上書き可能。

### Skills のプリロード

`skills` フィールドでサブエージェント起動時に Skills を自動ロードする:

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns
from the preloaded skills.
```

**通常の Skills との違い**: メインセッションでは Skills はオンデマンドロードされるが、サブエージェントでは `skills:` フィールドで指定された Skills が**起動時に全文プリロード**される。サブエージェントはメインセッションの Skills を継承しないため、明示的に指定する必要がある。

### Skill からの SubAgent 実行（context: fork）

Skill の frontmatter に `context: fork` を設定すると、その Skill がサブエージェント内で実行される:

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

`agent` フィールドで使用するサブエージェントを指定する。組み込み（`Explore`, `Plan`, `general-purpose`）またはカスタムサブエージェント名を指定可能。

---

## 実践パターン

### パターン 1: Writer/Reviewer 分離

一方のセッションでコードを書き、別のサブエージェントでレビューする。新しいコンテキストでレビューすることで品質が向上する。

```
# セッション A（Writer）
APIエンドポイントにレートリミッターを実装して

# セッション B（Reviewer — サブエージェント）
サブエージェントを使って src/middleware/rateLimiter.ts をレビューして。
エッジケース・競合状態・既存ミドルウェアパターンとの一貫性を確認して
```

### パターン 2: 並列調査

独立した調査を複数のサブエージェントに同時実行させる:

```
以下を並列でサブエージェントに調査させて:
1. 認証システムのトークンリフレッシュの仕組み
2. 再利用できる既存の OAuth ユーティリティ
3. 現在のセッション管理の実装
```

各サブエージェントが独立して探索し、Claude が結果を統合する。**調査パスが互いに依存しない場合**に最も効果的。

### パターン 3: 実装後の検証

コード変更後にサブエージェントで検証する:

```
サブエージェントを使ってこのコードのエッジケースをレビューして。
```

### パターン 4: セキュリティレビュー

カスタムサブエージェント `security-reviewer` を定義して専門的なレビューを実施:

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

使用時: `このコードのセキュリティレビューにサブエージェントを使って`

### パターン 5: 大規模コードベース探索

新しいプロジェクトへのオンボーディング時、サブエージェントに構造調査を委任する:

```
サブエージェントを使って以下を調査して:
- プロジェクトのディレクトリ構造と各モジュールの責務
- 主要なエントリポイントとデータフロー
- テストの構成とカバレッジ
```

---

## コンテキスト管理のベストプラクティス

### いつ SubAgent を使うべきか

| シナリオ | SubAgent を使う | メインで直接やる |
|---------|:---:|:---:|
| 大量のファイル読み込みが必要な調査 | **○** | |
| 数行のコード修正 | | **○** |
| コードレビュー（変更後の検証） | **○** | |
| 単純なファイル編集 | | **○** |
| 並列で独立した調査 | **○** | |
| 会話の文脈が必要なタスク | | **○** |
| 新しいコードベースの全体把握 | **○** | |
| 特定ファイルの小さな質問 | | **○** |

### コンテキスト消費の注意

サブエージェントの結果はメインに返却されるため、**多数のサブエージェントが詳細な結果を返すとメインのコンテキストを消費する**。

対策:
- サブエージェントに「要約して返却」を指示する
- 不要な詳細を省くよう指示する
- 持続的な並列作業が必要な場合は Agent Teams を検討する

### セッション管理

- サブエージェントはセッション開始時にロードされる
- セッション中にファイルを作成・変更した場合は、再起動または `/agents` コマンドでリロードが必要
- `/agents` でロードされているサブエージェント一覧を確認できる

---

## 活用シナリオ別ガイド

### 日常の開発作業での活用

| タスク | 推奨アプローチ | 理由 |
|--------|--------------|------|
| PR のコードレビュー | カスタム `code-reviewer` エージェント | レビュー観点を統一でき、メインコンテキストを汚さない |
| バグの原因調査 | 「サブエージェントを使って調査して」 | 大量のコード読み込みが発生するため隔離が有効 |
| リファクタリング前の影響調査 | Explore エージェント | 読み取り専用で高速に依存関係を調査 |
| テスト追加前のカバレッジ確認 | サブエージェントで既存テストを分析 | テスト構造の全体像を把握してからテストを書ける |
| 新規参画時のオンボーディング | 並列サブエージェントで各モジュールを調査 | 短時間でプロジェクトの全体像を把握 |
| セキュリティチェック | カスタム `security-reviewer` エージェント | 専門的な観点で漏れなくチェック |
| ドキュメント生成 | カスタムエージェント + Skills プリロード | API 規約等の知識をプリロードして一貫性のあるドキュメントを生成 |

### カスタムサブエージェントを作るべき場面

- **同じ種類のタスクを繰り返す**: コードレビュー、セキュリティチェック等
- **専門的な観点が必要**: 特定のチェックリストやレビュー基準がある
- **チームで共有したい**: `.claude/agents/` に配置して Git 管理

### カスタムサブエージェントが不要な場面

- **一回限りの調査**: 「サブエージェントを使って X を調査して」で十分
- **単純なタスク**: メインセッションで直接実行した方が早い
- **会話の文脈が必要**: サブエージェントは会話履歴にアクセスできない

---

## Tips

### proactive な description

`description` に「Use proactively」を含めると、Claude がコード変更後に自動的にサブエージェントを起動する:

```yaml
description: |
  Expert code reviewer. Use proactively after code changes.
```

### model の選択

| モデル | コスト | 最適な用途 |
|--------|--------|-----------|
| `haiku` | 低 | 高速な探索、簡単なチェック |
| `sonnet` | 中 | コードレビュー、一般的なタスク |
| `opus` | 高 | セキュリティ監査、複雑な分析 |
| `inherit` | 親と同じ | 特にこだわりがない場合 |

### ツール制限による安全性

読み取り専用のサブエージェントを作る場合、`tools` フィールドでツールを制限する:

```yaml
tools: Read, Glob, Grep
```

これにより、サブエージェントがファイルを変更したりコマンドを実行したりすることを防ぐ。

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| サブエージェントが起動しない | `/agents` でロード状況を確認。ファイル作成後はセッション再起動が必要 |
| 期待と異なるエージェントが選ばれる | `description` をより具体的にする。`<example>` ブロックを追加する |
| 結果が詳細すぎてコンテキストを圧迫する | 「要約して」を指示に含める。Agent Teams への移行を検討 |
| サブエージェントが会話の文脈を理解しない | 仕様上、会話履歴にアクセスできない。必要な情報はプロンプトで明示的に渡す |

---

## 関連ドキュメント

- [Subagents](https://code.claude.com/docs/en/sub-agents) — 公式 SubAgents ドキュメント
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — 拡張機能の全体像
- [Agent teams](https://code.claude.com/docs/en/agent-teams) — マルチエージェント協調（実験的機能）
- [Skills](https://code.claude.com/docs/en/skills) — Skills との連携（context: fork、skills プリロード）
- [Hooks](https://code.claude.com/docs/en/hooks) — イベント駆動の自動化
- [ClaudeCode Skills ガイド](skills-guide.md) — 本リポジトリの Skills ガイド
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
