# MCP サーバーの追加方法ガイド

> 出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp) / [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-04時点)

MCP サーバーを追加する方法は複数あるが、ClaudeCode をメインに使う場合は **`claude mcp add` コマンドが推奨**される。多くの MCP ツールの GitHub には JSON 形式の設定例しか記載されていないため、それを `claude mcp add` コマンドに変換する方法を理解しておく必要がある。

## 予約済み MCP サーバー名 (v2.1.205〜)

公式が **Claude Desktop の In-app browser 関連機能で以下の MCP サーバー名を予約**した (v2.1.205)。ユーザー MCP でこれらの名称を使うと衝突するため、別名で登録する。

- `Claude Browser`
- `Claude Preview`

**公式 MCP ページに掲載されている予約名の現行リスト**（`claude mcp add` は予約名をエラーで拒否する）:

| 予約名 | 用途 |
|---|---|
| `workspace` | ワークスペース系の組み込み機能 |
| `claude-in-chrome` | Claude in Chrome 連携 |
| `computer-use` | computer use 系ツール |
| `Claude Preview` | Claude Desktop In-app browser (v2.1.205) |
| `Claude Browser` | Claude Desktop In-app browser (v2.1.205) |

出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)。関連: [claude-desktop.md § In-app browser](claude-desktop.md#2026-w27w28-の新機能)

## `claude mcp add` コマンドの構文

```bash
# stdio トランスポート（ローカル実行）
claude mcp add --transport stdio [--scope <scope>] <name> [-e KEY=VALUE]... -- <command> [args...]

# HTTP トランスポート（リモートサーバー、推奨）
claude mcp add --transport http [--scope <scope>] <name> <url> [--header "Key: Value"]

# SSE トランスポート（非推奨。HTTP を使えるなら HTTP を使う）
claude mcp add --transport sse [--scope <scope>] <name> <url> [--header "Key: Value"]
```

> **WebSocket (`ws`) トランスポート**は `--transport` フラグでは指定できず、`.mcp.json` または `claude mcp add-json` で設定する（後述）。

## オプション解説

| オプション | 省略形 | 説明 |
|-----------|--------|------|
| `--transport <type>` | なし | 通信方式の指定。`stdio` / `http` / `sse` のいずれか（必須）。`ws` は `--transport` では指定不可（`add-json` を使う） |
| `--scope <scope>` | `-s` | 保存先スコープの指定。`user` / `local` / `project`（省略時は `local`） |
| `-e KEY=VALUE` | なし | 環境変数の設定。複数指定可能（`-e KEY1=VAL1 -e KEY2=VAL2`） |
| `--header "Key: Value"` | なし | HTTP/SSE で認証ヘッダーなどを追加 |
| `--` | なし | **stdio 専用**。この後ろに MCP サーバーの起動コマンドを記述する（Claude のフラグとサーバーの引数を区別するセパレータ） |

## トランスポートの種類

| トランスポート | 方式 | 用途 | 例 |
|--------------|------|------|-----|
| `stdio` | ローカルプロセスの stdin/stdout で通信 | npm パッケージや Docker で配布される MCP サーバー | `npx -y @brave/brave-search-mcp-server` |
| `http` | HTTP リクエスト/レスポンスで通信 | クラウドで公開されている MCP サーバー（**推奨**） | `https://mcp.notion.com/mcp` |
| `sse` | Server-Sent Events で通信（**非推奨 / deprecated**） | 旧 SSE エンドポイント。HTTP が使えるなら HTTP に移行する | `https://mcp.sentry.dev/sse` |
| `ws` | WebSocket による双方向接続 | サーバーが能動的にイベントを push するリモート MCP。`.mcp.json` / `add-json` で設定 | `wss://mcp.example.com/socket` |

> **使い分け**: リモート URL が提供されているなら `http` を使う（公式が SSE を deprecated とし「HTTP を使えるなら HTTP を使う」と明記している）。サーバーが能動的に push する用途のみ `ws`。npm パッケージや Docker イメージで提供されるサーバーは `stdio` を使う。
>
> **`streamable-http` エイリアス**: `.mcp.json` / `~/.claude.json` / `claude mcp add-json` で `type` を指定する際、`http` のエイリアスとして `streamable-http` が使える（MCP 仕様の正式名）。サーバー側ドキュメントの設定をそのままコピーしても動作する。

## スコープの使い分け

| スコープ | 保存先 | 用途 | Git 共有 |
|---------|--------|------|----------|
| `user` | `~/.claude.json` | **全プロジェクト共通**で使いたい MCP サーバー。API キーを含む個人ツール向き | しない |
| `local`（デフォルト） | `~/.claude.json`（プロジェクトパス配下のエントリ） | **現在のプロジェクトのみ**で使う個人用 MCP サーバー | しない |
| `project` | `.mcp.json`（プロジェクトルート） | **チーム全員で共有**する MCP サーバー。リポジトリにコミットされる | **する** |

> **重要（よくある誤解）**: MCP サーバーの `local` / `user` スコープはいずれも **`~/.claude.json`** に保存される。これは一般的な local settings (`.claude/settings.local.json`) や user settings (`~/.claude/settings.json`) とは**別物**である。公式も明示的に注意喚起している。`local` スコープは `~/.claude.json` 内の「現在のプロジェクトパス配下のエントリ」に書き込まれるため、他プロジェクトには現れない。
>
> **スコープの旧称**: `local` は旧バージョンでは `project`、`user` は旧バージョンでは `global` と呼ばれていた。
>
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
> **API キーの扱い**: `-s user` で追加すると `~/.claude.json`（MCP サーバーの保存先。settings.json ではない）に平文保存される。キーのローテーションや共有端末での利用時は、事前に `export OPENAI_API_KEY=...` しておき `-e OPENAI_API_KEY=$OPENAI_API_KEY` で渡す運用も検討する（ただし毎回 export が必要）。

### 変換時の注意点

1. **トランスポートの判定**: JSON に `"command"` があれば `stdio`、URL だけなら `http`（`sse` は非推奨のため新規は `http`、双方向 push が必要なら `ws`）
2. **`--` セパレータは stdio のみ**: `http` / `sse` / `ws` では不要（URL を直接指定する）
3. **環境変数に API キーを含む場合**: `-e` で渡すか、事前に `export` しておく。`-s user` / `local` で保存すると `~/.claude.json` にキーが平文で保存される点に注意
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
claude mcp login <name>              # OAuth 認証を開始（v2.1.186〜、対話 /mcp を開かず shell から実行）
claude mcp login <name> --no-browser # SSH 越しの paste-URL フロー（v2.1.191〜）
claude mcp logout <name>             # OAuth トークンを破棄（v2.1.186〜）
/mcp                                 # ClaudeCode 内でステータス確認（対話中）
```

## 信頼性・接続性の改善(v2.1.187〜)

- **MCP OAuth 401/403 自動再実行**(v2.1.193): ツール呼び出しが 401/403 を返した際に `headersHelper` を自動再実行して再接続する。手動 `/mcp` 再認証が減った。
- **MCP スタートアップ通知**(v2.1.193): 認証が必要な MCP サーバーがある場合、起動時に `/mcp` へ誘導する通知を表示する。
- **MCP capability discovery 自動リトライ**(v2.1.191): `tools/list`, `prompts/list`, `resources/list` が短い backoff で自動再試行する。auth / 4xx は再試行しない。
- **MCP tool call の idle timeout**(v2.1.187〜): 応答も progress notification も返らない時間が idle window を超えると、wall-clock 上限を待たずにエラーで中断する。**idle window の既定値はサーバー種別で異なる** — **HTTP / SSE / WebSocket / claude.ai connector = 5 分、stdio = 30 分**(stdio は v2.1.203 で対象化。それ以前は免除されていた)。IDE サーバーと SDK in-process サーバーは対象外。`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(ミリ秒)で変更でき、`0` で無効化できる。**ただしこれは「call が走れる長さ」の上限であり、「セッションがブロックされる長さ」とは別**である(下記)。
  - **per-server の `timeout`(1000 以上)は idle timeout の下限として機能する**(v2.1.203〜): ClaudeCode はそのサーバーの tool call を per-server `timeout` より早く idle 判定で中断しない。
  - **wall-clock 上限は `MCP_TOOL_TIMEOUT`**(未設定時は約 28 時間)。1000 未満の per-server `timeout` は無視され `MCP_TOOL_TIMEOUT` にフォールスルーする。HTTP / SSE / connector には別途 **first-response-byte 60 秒タイマー**があり、per-server `timeout` を 60 秒以上にすると引き上がる(下げることはできない)。
- **`-p`(print mode)の MCP 接続バグ修正**(v2.1.221): `--mcp-config` で渡した MCP サーバーが**初回ターン前に接続されず、モデルが tool call をリテラルテキストとして出力してしまう**不具合を修正。非対話実行で MCP を使うスクリプトはこの版以降を使う。
- **スリープ復帰時の token refresh race 修正**(v2.1.221): 2 つの ClaudeCode プロセスが**同一 MCP connector / WIF OAuth token を同時に refresh** して再認証を強制される稀な race を修正した。複数プロジェクトを並行で開き、Mac をスリープさせる運用では効く修正である。
- **接続エラーの可視化**(v2.1.219): `claude mcp list` / `/mcp` が接続失敗時に **HTTP status と error text を表示**する。MCP 設定値の**先頭 / 末尾に不可視の空白**が含まれる場合も警告が出る。headless の stream-json では init event に **`mcp_server_errors`**(config validation でスキップされた `--mcp-config` エントリ)が入り、ターミナル実行では起動時警告として出る。
- **再認証の資格情報バグ修正**(v2.1.216): MCP 再認証が**新しいサインインの成功前に既存の有効な資格情報を revoke してしまう**不具合を修正。background セッションの needs-auth メッセージが使えないコマンドを案内していた問題も併せて修正された。
- **メモリリーク修正**(v2.1.217): 切り詰められた MCP tool output が、**未切り詰めの全文をセッション中メモリに保持し続ける**リークを修正。大きな出力を返す MCP を長時間使うセッションで効く。

### 長時間 MCP tool call の自動バックグラウンド化(v2.1.212〜)

**メイン会話の MCP tool call が 2 分を超えると、自動的に background task へ移行する**。Claude は即座に task ID を受け取って作業を継続し、結果は task notification として後から届く。「MCP の応答待ちで会話全体が止まる」状態が既定で解消された。

| 制御 | 内容 |
|---|---|
| `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` | 移行の閾値(ミリ秒)。**`0` で無効化** |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` | background task 自体を無効化するため、この機能も止まる |
| 非対話モード | **既定では対象外**。`CLAUDE_AUTO_BACKGROUND_TASKS=1` で有効化する |

> `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(idle timeout)と混同しないこと。前者は「**セッションを待たせる時間**」の制御、後者は「**call を打ち切るまでの時間**」の制御である。

## MCP tool search — 既定で MCP ツールは deferred ロードされる

**MCP を何本繋いでもコンテキスト消費がほぼ増えないのは、tool search が既定で有効だからである**。公式は「Tool search is enabled by default. MCP tools are **deferred** rather than loaded into context upfront」と明記しており、セッション開始時にコンテキストへ載るのは **ツール名と server instructions のみ**である。実際のツールスキーマは Claude が `ToolSearch` を呼んだ時点で初めて読み込まれる。

> **運用上の含意**: 「MCP を繋ぎ過ぎるとコンテキストが逼迫する」というのは tool search 以前の前提である。現在は**繋いでいるだけならほぼ無害**で、コンテキスト逼迫の主因は常時ロードされる CLAUDE.md / `@import` 側にある（[memory.md](memory.md) 参照）。

### `ENABLE_TOOL_SEARCH` の 4 状態

| 値 | 挙動 |
|---|---|
| (未設定) | 全ツールを defer する（既定） |
| `true` | 強制的に defer する |
| **`auto`** | **コンテキストの 10% に収まれば upfront ロードし、超過分のみ defer する** |
| `false` | tool search を無効化し、全ツールを upfront ロードする |

### tool search が使えない環境

- **Google Cloud's Agent Platform**
- `ANTHROPIC_BASE_URL` が non-first-party（自前 LLM gateway 等）
- **Microsoft Foundry の Azure ホスト deployment**（サーバー側で reject されるため、ClaudeCode が検知して upfront ロードに切り替える。`ENABLE_TOOL_SEARCH` でも上書きできない）
- **Google Vertex AI** は一度無効化されていたが、**v2.1.221 で Claude 4.5 世代以降のモデルに限り再有効化**された
- 対応モデル（`tool_reference` ブロック対応）は **Sonnet 4.5 / Haiku 4.5 / Opus 4.5 以降**

tool search が無効な構成では、接続待ちのサーバーに対して `ToolSearch` の代わりに `WaitForMcpServers` ツールが使われる。

### 関連する per-server / 出力の設定

| 設定 | 内容 |
|---|---|
| **`alwaysLoad: true`** | `.mcp.json` の per-server キー。該当サーバーのみ upfront ロードする。**接続完了まで起動をブロックする**（5 秒の connect timeout でキャップ）ため、常用ツールが少数のサーバーに限って使う |
| **`MAX_MCP_OUTPUT_TOKENS`** | MCP ツール出力が **10,000 トークンを超えると警告**、**既定 25,000 トークンで制限**。警告閾値は固定で変更できない。`anthropic/maxResultSizeChars` を宣言したツールは text content でそちらの値が優先される（画像データは常に `MAX_MCP_OUTPUT_TOKENS` の対象） |
| `enabledMcpServers` | 既定 off の組み込みサーバー（`computer-use` 等）を opt-in するリスト |

出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp) / CHANGELOG v2.1.221

## MCP 仕様 2026-07-28 版（Claude 製品への展開は rolling out）

2026-07-28 に MCP 仕様の新版が公開され、Anthropic が Claude 製品への対応を進めていることを公式ブログで表明した。仕様レベルの主な変更は次の 3 点である。

| 変更 | 内容 |
|---|---|
| コアの単純化 | **stateful なプロトコルから、ステートレスな request/response モデルへ** |
| 機能の分離 | **MCP Apps / Tasks が「バージョン付き extensions」として分離**された |
| 認可 | **OAuth 2.0 / OIDC 準拠**へ（Microsoft Entra / Okta 等の既存 IdP と組み合わせやすくなる） |

> ⚠️ **ClaudeCode 側の対応状況は未確認**である。公式ブログは Claude 製品への展開を「rolling out soon」と述べるのみで、ClaudeCode の対応バージョンには言及していない。**自作 MCP サーバーを運用している場合は、仕様本体と SDK の更新状況を個別に確認する**必要がある。出典: [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude)

## `.mcp.json` project-scope の workspace-trust ゲート(v2.1.196〜)

**破壊的変更**: v2.1.196 以降、`claude mcp list` / `claude mcp get` は `.mcp.json` の approvals を **workspace-trust ダイアログを承認するまで読まない**(non-checked-in settings のみ利用)。

- project の `.claude/settings.json` に書いた `enableAllProjectMcpServers` / `enabledMcpjsonServers` は **untrusted folder では無視される**
- チームでリポジトリを共有していて、pull 直後に MCP が動かない場合はまず workspace-trust の承認状態を確認する
- 出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)
