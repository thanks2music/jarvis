# Claude Desktop の設定ファイル

> 出典: [MCP Quickstart](https://modelcontextprotocol.io/quickstart) / [DeepWiki - modelcontextprotocol/docs](https://deepwiki.com/modelcontextprotocol/docs) (2026-03-22時点)

Claude Desktop は ClaudeCode とは別のデスクトップアプリケーションであり、独自の設定ファイルを持つ。MCP サーバーの設定方法が ClaudeCode とは異なるため、混同しないよう整理する。

## `claude_desktop_config.json`

- **目的**: Claude Desktop が接続する MCP サーバーの定義
- **内容**: MCP サーバーの起動コマンド、引数、環境変数
- **保存場所**（OS 別）:
  - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
  - **Linux**: 現時点では Claude Desktop 未対応
- **スコープ**: ユーザーレベル（Claude Desktop 全体に適用）
- **Git 管理**: しない（個人環境固有のパス情報を含む）
- **備考**: 編集後は Claude Desktop の再起動が必要。パスは絶対パスで指定する
- **設定例**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    },
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

## ClaudeCode と Claude Desktop の MCP 設定の違い

| 項目 | ClaudeCode | Claude Desktop |
|------|-----------|----------------|
| MCP 設定ファイル | `.mcp.json`（project）/ `settings.json`（user/local） | `claude_desktop_config.json` |
| 設定方法 | `claude mcp add` コマンド or 手動編集 | 手動で JSON ファイルを編集 |
| スコープ | user / local / project の3段階 | ユーザーレベルのみ |
| Git 共有 | `.mcp.json` は共有可能 | 共有しない |
| 反映タイミング | 即座に反映 | アプリ再起動が必要 |

## 全設定ファイル対応表（ClaudeCode + Claude Desktop）

| ファイル | 対象アプリ | 保存場所 | 主な用途 | Git 管理 | ユーザー編集 |
|----------|-----------|----------|----------|----------|-------------|
| `~/.claude.json` | ClaudeCode | `~/` | 内部状態・認証情報 | しない | しない |
| `~/.claude/settings.json` | ClaudeCode | `~/.claude/` | 全プロジェクト共通の個人設定 | しない | **する** |
| `~/.claude/keybindings.json` | ClaudeCode | `~/.claude/` | キーボードショートカット | しない | **する** |
| `.claude/settings.json` | ClaudeCode | プロジェクトルート | チーム共有のプロジェクト設定 | **する** | **する** |
| `.claude/settings.local.json` | ClaudeCode | プロジェクトルート | プロジェクト設定の個人オーバーライド | しない | **する** |
| `.mcp.json` | ClaudeCode | プロジェクトルート | MCP サーバーのチーム共有設定 | **する** | **する** |
| `claude_desktop_config.json` | Claude Desktop | OS 固有パス※ | MCP サーバー設定 | しない | **する** |

> ※ macOS: `~/Library/Application Support/Claude/`、Windows: `%APPDATA%\Claude\`
