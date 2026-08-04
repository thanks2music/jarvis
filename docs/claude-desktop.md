# Claude Desktop の設定ファイル

> 出典: [MCP Quickstart](https://modelcontextprotocol.io/quickstart) / [DeepWiki - modelcontextprotocol/docs](https://deepwiki.com/modelcontextprotocol/docs) / [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-04時点)

Claude Desktop は ClaudeCode とは別のデスクトップアプリケーションであり、独自の設定ファイルを持つ。MCP サーバーの設定方法が ClaudeCode とは異なるため、混同しないよう整理する。

## アプリの構成（3 タブ）と提供プラットフォーム

Claude Desktop は **Chat / Cowork / Code の 3 タブ**構成である。このうち **Code タブが Claude Code 相当**の機能を提供する（本ドキュメントで「Claude Desktop 上のセッション」と書いているのは Code タブのセッションを指す）。

- **macOS / Windows** に加えて **Linux beta**（apt / `.deb`）が提供されている
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop)

## ClaudeCode と挙動が異なる点（重要）

Desktop は CLI と同じ設定ファイルを読むが、**一部の挙動が異なる**。CLI の前提で書いた手順がそのまま通らない箇所を先に押さえる。

| 項目 | Desktop での挙動 |
|---|---|
| **`/config key=value`** | ⚠️ **Desktop の `/config` は `key=value` を無視する**（`/config theme=dark` が効かない）。この構文は **CLI 前提**である（[slash-commands.md](slash-commands.md) 参照） |
| **`sshHostAllowlist`** | managed settings のみで読まれ、**Desktop アプリだけが honor する**（CLI / IDE 拡張は読まない）。**Bash 経由の `ssh` は制限しない**点に注意 |
| **`disableBrowserExternalNavigation`** | **JSON boolean の `true` のみ有効**。文字列 `"true"` は無視される |
| **`MAX_THINKING_TOKENS=0`** | モデル世代で挙動が分岐する。Fable 5 では無効、adaptive reasoning モデルは 0 以外の値を無視、Opus 4.6 / Sonnet 4.6 は `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` で固定 budget 化できる |
| **`.worktreeinclude`** | gitignore されたファイル（`.env` 等）を worktree にコピーする指定ができる |

出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop)

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

## 企業ネットワーク設定の扱い (v2.1.212 / v2.1.217)

Claude Desktop 上のセッションでは、**ClaudeCode で有効な企業ネットワーク設定の一部が適用されない**ケースがある。社内プロキシや mTLS を前提とした環境では注意する。

| バージョン | 内容 |
|---|---|
| **v2.1.212** | **hosted（host-managed）セッションでは、mTLS 証明書・追加 CA バンドル・OAuth scope の設定を「警告付きで無視する」**仕様が明示された。設定は書けるが効かない点に注意 |
| **v2.1.217** | **corporate mTLS / TLS-verify / OAuth scope / proxy の設定が Claude Desktop セッションで無視されていた不具合を修正**。v2.1.217 以降は（hosted セッションを除き）意図通り適用される |

- 出典: [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) v2.1.212 / v2.1.217
- ⚠️ **出典の注意（2026-08-04 確認）**: 上表 v2.1.212 の「hosted セッションでは mTLS / CA バンドル / OAuth scope を警告付きで無視する」は **CHANGELOG v2.1.212 のみを根拠**としている。現行の公式 [Claude Desktop](https://code.claude.com/docs/en/desktop) ページ本文では同記述を確認できず、同ページは mTLS / 独自 CA / proxy を [Network configuration](https://code.claude.com/docs/en/network-config) へのリンクで扱う形に変わっている。**誤りとは断定できないが、企業ネットワーク前提の構築時は network-config ページ側で現行仕様を確認する**のが安全である。

## `claude_desktop_config.json`

- **目的**: Claude Desktop が接続する MCP サーバーの定義
- **内容**: MCP サーバーの起動コマンド、引数、環境変数
- **保存場所**（OS 別）:
  - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
  - **Linux**: **beta 提供中**（apt / `.deb`）。設定パスは `~/.config/Claude/claude_desktop_config.json` 相当（環境により異なるためアプリ内の設定画面から確認する）
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
