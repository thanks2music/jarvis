# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) (2026-03-22時点)

ClaudeCode は 6 つの JSON 設定ファイルを階層的に使い分ける。それぞれスコープ（適用範囲）と優先順位が異なり、ユーザー個人の設定・プロジェクト共有の設定・ローカルオーバーライドを分離する設計になっている。さらに Claude Desktop は独自の設定ファイルを 1 つ持つ（計 7 ファイル）。

## 設定ファイル詳細

### 1. `~/.claude.json`（内部管理ファイル）

- **目的**: ClaudeCode の内部状態・認証情報の保存
- **内容**: セッション情報、認証トークンなど ClaudeCode が内部的に管理するデータ
- **保存場所**: ユーザーのホームディレクトリ（`~/.claude.json`）
- **スコープ**: ユーザーレベル（内部管理用）
- **Git 管理**: しない（個人の認証情報を含む）
- **備考**: かつては `allowedTools` や `ignorePatterns` もここに保存されていたが、現在は `settings.json` に移行済み。ユーザーが直接編集するファイルではない

### 2. `~/.claude/settings.json`（ユーザー設定）

- **目的**: 全プロジェクト共通のユーザー個人設定
- **内容**: パーミッション（allow/deny）、環境変数、MCP サーバー（user スコープ）、UI 設定（`showTurnDuration`、`language` など）
- **保存場所**: `~/.claude/settings.json`
- **スコープ**: ユーザーレベル（すべてのプロジェクトに適用）
- **Git 管理**: しない（個人設定）
- **設定例**:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Bash(curl *)", "Read(./.env)"]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1"
  }
}
```

### 3. `.claude/settings.json`（プロジェクト設定）

- **目的**: プロジェクト固有の共有設定
- **内容**: プロジェクト共通のパーミッションルール、プラグイン設定、モデル設定など
- **保存場所**: プロジェクトルート `.claude/settings.json`
- **スコープ**: プロジェクトレベル（チーム全員に適用）
- **Git 管理**: **する**（チームで共有する前提）
- **備考**: ユーザー設定（`~/.claude/settings.json`）より優先される

### 4. `.claude/settings.local.json`（ローカル設定）

- **目的**: プロジェクト設定のローカルオーバーライド
- **内容**: 個人的な実験やプラグインの無効化など、チームに共有しない設定
- **保存場所**: プロジェクトルート `.claude/settings.local.json`
- **スコープ**: プロジェクトレベル（ローカルのみ）
- **Git 管理**: **しない**（作成時に ClaudeCode が自動で `.gitignore` に追加）
- **備考**: `.claude/settings.json` より優先される

### 5. `.mcp.json`（MCP サーバー設定）

- **目的**: プロジェクトで使う MCP サーバーの共有設定
- **内容**: MCP サーバーの定義（コマンド、引数、環境変数）
- **保存場所**: プロジェクトルート `.mcp.json`
- **スコープ**: プロジェクトレベル（`project` スコープの MCP サーバー）
- **Git 管理**: **する**（チームメンバーが同じ MCP ツールを利用できるようにする）
- **備考**: セキュリティ上、プロジェクトスコープの MCP サーバーは初回使用時に承認プロンプトが表示される
- **設定例**:
```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

### 6. `~/.claude/keybindings.json`（キーバインド設定）

- **目的**: ClaudeCode のキーボードショートカットのカスタマイズ
- **内容**: 各コンテキスト（Chat など）ごとのキーバインド定義。アクションへのキー割り当て変更や無効化（`null`）が可能
- **保存場所**: `~/.claude/keybindings.json`
- **スコープ**: ユーザーレベル（全セッションに適用）
- **Git 管理**: しない（個人のキーバインド設定）
- **備考**: `/keybindings` コマンドでファイルを作成・編集できる。変更は即座に反映され、再起動不要（v2.1.18 以降）
- **設定例**:
```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+u": null
      }
    }
  ]
}
```

## 設定の優先順位（上が最優先）

ClaudeCode は同じ設定が複数の場所で定義されている場合、**より具体的なスコープを優先**する。deny は常に allow より強い。

```
1. Managed（企業管理設定）     ← 最優先。他のどのレベルでも上書き不可
2. コマンドライン引数           ← セッション単位の一時的なオーバーライド
3. .claude/settings.local.json ← プロジェクトのローカルオーバーライド
4. .claude/settings.json       ← プロジェクト共有設定
5. ~/.claude/settings.json     ← ユーザー個人設定（最低優先）
```

## MCP サーバーのスコープ

`claude mcp add` コマンドで MCP サーバーを追加する際、`--scope` オプションでスコープを指定する。

| スコープ | 保存先 | 用途 | Git 管理 |
|----------|--------|------|----------|
| `user` | `~/.claude/settings.json` | 全プロジェクトで使う個人用 MCP サーバー | しない |
| `local`（デフォルト） | `.claude/settings.local.json` | 現在のプロジェクトでのみ使うローカル MCP サーバー | しない |
| `project` | `.mcp.json` | チーム全員で共有する MCP サーバー | **する** |

```bash
# user スコープ（全プロジェクト共通）
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic

# local スコープ（デフォルト、個人のプロジェクト設定）
claude mcp add --transport http stripe --scope local https://mcp.stripe.com

# project スコープ（チーム共有、.mcp.json に保存）
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

## 対応表（まとめ）

| ファイル | 保存場所 | スコープ | 主な用途 | Git 管理 | 優先順位 | ユーザー編集 |
|----------|----------|----------|----------|----------|----------|-------------|
| `~/.claude.json` | `~/` | ユーザー（内部） | 内部状態・認証情報 | しない | — | しない |
| `~/.claude/settings.json` | `~/.claude/` | ユーザー | 全プロジェクト共通の個人設定 | しない | 5（最低） | **する** |
| `~/.claude/keybindings.json` | `~/.claude/` | ユーザー | キーボードショートカット | しない | — | **する** |
| `.claude/settings.json` | プロジェクトルート | プロジェクト | チーム共有のプロジェクト設定 | **する** | 4 | **する** |
| `.claude/settings.local.json` | プロジェクトルート | ローカル | プロジェクト設定の個人オーバーライド | しない | 3 | **する** |
| `.mcp.json` | プロジェクトルート | プロジェクト | MCP サーバーのチーム共有設定 | **する** | — | **する** |

> **補足**: `~/.claude.json` はユーザーが直接編集するものではなく、ClaudeCode が内部的に管理するファイルである。設定のカスタマイズには `settings.json` 系のファイルを使う。Managed（企業管理）設定は組織が配布するもので、個人環境では通常意識する必要はない。
