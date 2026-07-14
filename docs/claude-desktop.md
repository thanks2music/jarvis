# Claude Desktop の設定ファイル

> 出典: [MCP Quickstart](https://modelcontextprotocol.io/quickstart) / [DeepWiki - modelcontextprotocol/docs](https://deepwiki.com/modelcontextprotocol/docs) / [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop) (2026-07-11時点)

Claude Desktop は ClaudeCode とは別のデスクトップアプリケーションであり、独自の設定ファイルを持つ。MCP サーバーの設定方法が ClaudeCode とは異なるため、混同しないよう整理する。

## 2026-w27〜w28 の新機能

### In-app browser (Week 28)

- Claude Desktop に**組み込みブラウザ**が搭載され、Claude が外部サイトを直接読み・クリック・操作できるようになった
- ブラウザは **sandboxed** で動作し、安全分類器レビューを経由する
- セッション永続化 (persist) は選択可能 (履歴・cookie を残すかどうかを個別に指定)
- 併せて公式が **MCP server 名として "Claude Browser" / "Claude Preview" を予約** (v2.1.205、[mcp-setup.md](mcp-setup.md) 参照)
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop#browse-external-sites) / [whats-new week 28](https://code.claude.com/docs/en/whats-new/2026-w28)

### Claude Desktop on Linux beta (Week 27)

- **Ubuntu / Debian 向け beta 提供**開始。当初「Linux 未対応」だったが状況変化した (下記「保存場所」表の Linux 行を「beta 提供中」に読み替える)
- 出典: [whats-new — code.claude.com](https://code.claude.com/docs/en/whats-new)

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
