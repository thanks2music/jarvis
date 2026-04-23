# MCP サーバーの追加方法ガイド

> 出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp) (2026-03-22時点)

MCP サーバーを追加する方法は複数あるが、ClaudeCode をメインに使う場合は **`claude mcp add` コマンドが推奨**される。多くの MCP ツールの GitHub には JSON 形式の設定例しか記載されていないため、それを `claude mcp add` コマンドに変換する方法を理解しておく必要がある。

## `claude mcp add` コマンドの構文

```bash
# stdio トランスポート（ローカル実行）
claude mcp add --transport stdio [--scope <scope>] <name> [-e KEY=VALUE]... -- <command> [args...]

# HTTP トランスポート（リモートサーバー）
claude mcp add --transport http [--scope <scope>] <name> <url> [--header "Key: Value"]

# SSE トランスポート（Server-Sent Events）
claude mcp add --transport sse [--scope <scope>] <name> <url> [--header "Key: Value"]
```

## オプション解説

| オプション | 省略形 | 説明 |
|-----------|--------|------|
| `--transport <type>` | なし | 通信方式の指定。`stdio` / `http` / `sse` のいずれか（必須） |
| `--scope <scope>` | `-s` | 保存先スコープの指定。`user` / `local` / `project`（省略時は `local`） |
| `-e KEY=VALUE` | なし | 環境変数の設定。複数指定可能（`-e KEY1=VAL1 -e KEY2=VAL2`） |
| `--header "Key: Value"` | なし | HTTP/SSE で認証ヘッダーなどを追加 |
| `--` | なし | **stdio 専用**。この後ろに MCP サーバーの起動コマンドを記述する（Claude のフラグとサーバーの引数を区別するセパレータ） |

## トランスポートの種類

| トランスポート | 方式 | 用途 | 例 |
|--------------|------|------|-----|
| `stdio` | ローカルプロセスの stdin/stdout で通信 | npm パッケージや Docker で配布される MCP サーバー | `npx -y @brave/brave-search-mcp-server` |
| `http` | HTTP リクエスト/レスポンスで通信 | クラウドで公開されている MCP サーバー（**推奨**） | `https://mcp.notion.com/mcp` |
| `sse` | Server-Sent Events で通信 | SSE エンドポイントを公開しているサーバー | `https://mcp.sentry.dev/sse` |

> **使い分け**: リモート URL が提供されているなら `http`（または `sse`）を使う。npm パッケージや Docker イメージで提供されるサーバーは `stdio` を使う。

## スコープの使い分け

| スコープ | 保存先 | 用途 | Git 共有 |
|---------|--------|------|----------|
| `user` | `~/.claude/settings.json` | **全プロジェクト共通**で使いたい MCP サーバー。API キーを含む個人ツール向き | しない |
| `local` | `.claude/settings.local.json` | **現在のプロジェクトのみ**で使う個人用 MCP サーバー。デフォルト | しない |
| `project` | `.mcp.json` | **チーム全員で共有**する MCP サーバー。リポジトリにコミットされる | **する** |

> **個人利用の判断基準**: どのプロジェクトでも使うなら `user`、特定プロジェクトだけなら `local`、チームで共有するなら `project`。

## JSON 設定から `claude mcp add` への変換方法

多くの MCP ツールの GitHub には、Claude Desktop 向けの JSON 設定しか記載されていない。これを `claude mcp add` コマンドに変換する手順を解説する。

### 変換ルール

JSON の各フィールドは `claude mcp add` の以下の要素に対応する:

```
{
  "mcpServers": {
    "<name>": {                    → コマンドの <name> 引数
      "command": "<cmd>",          → -- の直後に置く
      "args": ["arg1", "arg2"],    → command の後ろに続ける
      "env": {
        "KEY": "VALUE"             → -e KEY=VALUE として指定
      }
    }
  }
}
```

**変換の公式**:
```
claude mcp add --transport stdio [-s <scope>] <name> [-e KEY=VALUE]... -- <command> <args...>
```

> **引数順序の注意**: `-e` は可変長オプションで、後続の引数を次のフラグまで環境変数として食い続ける。そのため `<name>` は `-e` より**前**に置く必要がある。逆順にすると `<name>` が env 値として解釈され、`Invalid environment variable format: <name>` というエラーになる。

### 具体例: brave-search-mcp-server

GitHub（[brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server)）に記載されている JSON:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": {
        "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

**変換手順**:

| JSON フィールド | 値 | 変換先 |
|----------------|-----|--------|
| キー名 `"brave-search"` | — | `<name>` → `brave-search` |
| `"command"` | `"npx"` | `--` の直後 → `npx` |
| `"args"` | `["-y", "@brave/brave-search-mcp-server"]` | command の後 → `-y @brave/brave-search-mcp-server` |
| `"env"` | `{"BRAVE_API_KEY": "..."}` | `-e` オプション → `-e BRAVE_API_KEY=YOUR_API_KEY_HERE` |

**結果**:
```bash
# user スコープ（全プロジェクトで使いたい場合）
claude mcp add --transport stdio -s user brave-search -e BRAVE_API_KEY=YOUR_API_KEY_HERE -- npx -y @brave/brave-search-mcp-server

# local スコープ（デフォルト、現在のプロジェクトのみ）
claude mcp add --transport stdio brave-search -e BRAVE_API_KEY=YOUR_API_KEY_HERE -- npx -y @brave/brave-search-mcp-server
```

> **注意**: `npx -y` の `-y` は npm パッケージの自動インストール確認をスキップするフラグである。MCP サーバーの引数ではなく npx 自体のオプション。

### 具体例: codex (OpenAI)

Claude Desktop の `claude_desktop_config.json` に記載されている JSON:

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"],
      "env": {
        "OPENAI_API_KEY": "sk-YOUR_OPENAI_API_KEY"
      }
    }
  }
}
```

**変換手順**:

| JSON フィールド | 値 | 変換先 |
|----------------|-----|--------|
| キー名 `"codex"` | — | `<name>` → `codex` |
| `"command"` | `"codex"` | `--` の直後 → `codex`（`codex` CLI がインストール済みである前提） |
| `"args"` | `["mcp-server"]` | command の後 → `mcp-server` |
| `"env"` | `{"OPENAI_API_KEY": "..."}` | `-e` オプション → `-e OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY` |

**結果**:
```bash
# user スコープ（全プロジェクトで使いたい場合。サブ AI エージェントとしての一般的な使い方）
claude mcp add --transport stdio -s user codex -e OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY -- codex mcp-server
```

> **前提**: `codex` コマンドが PATH に存在する必要がある（`npm install -g @openai/codex` 等でインストール済みであること）。`command` に `codex` を直接指定するのは、JSON 側の `"command": "codex"` と同じく「PATH 上の実行ファイルを起動する」という意味。
>
> **API キーの扱い**: `-s user` で追加すると `~/.claude/settings.json` に平文保存される。キーのローテーションや共有端末での利用時は、事前に `export OPENAI_API_KEY=...` しておき `-e OPENAI_API_KEY=$OPENAI_API_KEY` で渡す運用も検討する（ただし毎回 export が必要）。

### 変換時の注意点

1. **トランスポートの判定**: JSON に `"command"` があれば `stdio`、URL だけなら `http` または `sse`
2. **`--` セパレータは stdio のみ**: `http` / `sse` では不要（URL を直接指定する）
3. **環境変数に API キーを含む場合**: `-e` で渡すか、事前に `export` しておく。`-s user` で保存すると設定ファイルにキーが平文で保存される点に注意
4. **`--transport http` が args に含まれる場合**: これは MCP サーバー自体の内部オプション（サーバーが HTTP モードで起動する指示）であり、`claude mcp add` の `--transport` とは別物である。ClaudeCode と MCP サーバー間の通信は `stdio`（stdin/stdout 経由）のまま

## その他の追加方法

### `claude mcp add-json`（JSON 直接指定）

JSON をコマンドラインで直接渡す方法。複雑な設定やスクリプトからの追加に便利。

```bash
claude mcp add-json brave-search '{"command":"npx","args":["-y","@brave/brave-search-mcp-server"],"env":{"BRAVE_API_KEY":"YOUR_API_KEY_HERE"}}'
```

### `claude mcp add-from-claude-desktop`（Claude Desktop からインポート）

Claude Desktop に既に設定済みの MCP サーバーを ClaudeCode にインポートする。macOS と WSL でのみ利用可能。

```bash
# 対話的に選択してインポート
claude mcp add-from-claude-desktop

# user スコープでインポート（全プロジェクトで使えるようにする）
claude mcp add-from-claude-desktop --scope user
```

> **運用の流れ**: まず Claude Desktop の `claude_desktop_config.json` に JSON を手動追加 → 動作確認 → `claude mcp add-from-claude-desktop` で ClaudeCode にインポート、という使い方もできる。

### MCP 管理コマンド一覧

```bash
claude mcp list                      # 登録済み MCP サーバーの一覧表示
claude mcp remove <name>             # MCP サーバーの削除
claude mcp reset-project-choices     # プロジェクトスコープの承認選択をリセット
/mcp                                 # ClaudeCode 内でステータス確認（対話中）
```
