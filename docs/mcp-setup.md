# MCP サーバーの追加方法ガイド

> 出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp) / [Control MCP server access for your organization](https://code.claude.com/docs/en/managed-mcp) / [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude) / [Build plugins for Claude](https://claude.com/resources/articles/build-plugins-for-claude) / [Add an interactive UI to your MCP server](https://claude.com/docs/connectors/building/mcp-apps/quickstart) / [Add a connector that isn't in the directory](https://claude.com/docs/connectors/custom/add-unlisted) / [Claude now works with Google Docs, Sheets, and Slides](https://claude.com/resources/articles/claude-now-works-in-google-docs-sheets-and-slides) / [Channels](https://code.claude.com/docs/en/channels) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。版数は MCP ページなど docs の記載を優先し、docs に無いものは CHANGELOG による)

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

# SSE トランスポート（非推奨。v2.1.265 未満の版か、SSE で直接繋ぎたい場合だけ使う）
claude mcp add --transport sse [--scope <scope>] <name> <url> [--header "Key: Value"]
```

> **SSE だけのサーバーも `--transport http` で追加できる（v2.1.265〜、2026-10-11 追記）**: ClaudeCode はまず HTTP で接続し、サーバーが受け付けなければ SSE に自動で切り替える。この自動切り替えは v2.1.265 以降で、それより前の版では `--transport sse` を指定する（版数は MCP ページの記載による）。

> **WebSocket (`ws`) トランスポート**は `--transport` フラグでは指定できず、`.mcp.json` または `claude mcp add-json` で設定する（後述）。

## オプション解説

| オプション | 省略形 | 説明 |
|-----------|--------|------|
| `--transport <type>` | **stdio** | 通信方式の指定。`stdio` / `http` / `sse` のいずれか。⚠️ **必須ではない**（**2026-09-03 訂正**）。正規構文は `claude mcp add [options] <name> -- <command> [args...]` で、公式例（`claude mcp add example --env API_KEY=your-key -- npx -y @example/mcp-server`）は `--transport` を省略している。**`type` を書かない場合は stdio と解釈される**。`ws` は `--transport` では指定不可（`add-json` を使う） |
| `--scope <scope>` | `-s` | 保存先スコープの指定。`user` / `local` / `project`（省略時は `local`） |
| `-e KEY=VALUE` | なし | 環境変数の設定。複数指定可能（`-e KEY1=VAL1 -e KEY2=VAL2`） |
| `--header "Key: Value"` | なし | HTTP/SSE で認証ヘッダーなどを追加 |
| `--` | なし | **stdio 専用**。この後ろに MCP サーバーの起動コマンドを記述する（Claude のフラグとサーバーの引数を区別するセパレータ） |

## トランスポートの種類

| トランスポート | 方式 | 用途 | 例 |
|--------------|------|------|-----|
| `stdio` | ローカルプロセスの stdin/stdout で通信 | npm パッケージや Docker で配布される MCP サーバー | `npx -y @brave/brave-search-mcp-server` |
| `http` | HTTP リクエスト/レスポンスで通信 | クラウドで公開されている MCP サーバー（**推奨**） | `https://mcp.notion.com/mcp` |
| `sse` | Server-Sent Events で通信（**非推奨 / deprecated**） | 旧 SSE エンドポイント。HTTP が使えるなら HTTP に移行する。SSE しか提供しないサーバーも v2.1.265 以降は `--transport http` で追加すれば自動で SSE に切り替わる | `https://mcp.sentry.dev/sse` |
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

> **引数順序の注意**: `-e`（`--env`）は複数の `KEY=VALUE` を受け付けるため、**`--env` の直後にサーバー名を置くと、CLI はサーバー名も env ペアとして読んで拒否する**（`Invalid environment variable format: <name>` というエラーになる）。回避策は 2 つある。上の「変換の公式」のように `<name>` を `-e` より前に置くか、MCP ページの例 `claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable -- npx -y airtable-mcp-server` のように `--env` とサーバー名の間に `--transport stdio` など別のオプションを 1 つ以上挟む。
>
> **2026-10-11 訂正**: 以前は「`<name>` は `-e` より前に置かなければならない」と書いていたが、MCP ページは「`--env` とサーバー名の間に別のオプションを 1 つ以上挟めばよい」としている。

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
                                     #   v2.1.238〜: 無効化済みサーバーには接続せず
                                     #   `⊘ Disabled for this project (re-enable via /mcp)` と表示する
claude mcp serve                     # ClaudeCode 自体を MCP サーバーとして起動する
claude mcp remove <name>             # MCP サーバーの削除
                                     #   remote サーバーなら、保存済みの OAuth トークンと
                                     #   client registration も一緒に削除される
claude mcp reset-project-choices     # プロジェクトスコープの承認選択をリセット
claude mcp login <name>              # OAuth 認証を開始（v2.1.186〜、対話 /mcp を開かず shell から実行）
claude mcp login <name> --no-browser # SSH 越しの paste-URL フロー（v2.1.191〜）
claude mcp logout <name>             # OAuth トークンを破棄（v2.1.186〜）
/mcp                                 # ClaudeCode 内でステータス確認（対話中）
/mcp reconnect all                   # 接続失敗・要認証のサーバーをまとめて再試行
                                     #   対話ターミナルでは v2.1.284〜。それより前の版は
                                     #   `MCP server "all" not found` と表示する
```

出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（Managing your servers / Retry failed servers yourself。2026-10-11 追記）

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
- **OAuth コールバックの redirect URI は v2.1.229 だけ `127.0.0.1` になった（退行。v2.1.231 で `localhost` に戻った）**: v2.1.229 は strict な認可サーバー向けの修正として、redirect URI を `http://127.0.0.1:PORT/callback` で送るように変えた。その結果、登録済みの redirect URI と完全一致で照合するサーバーが redirect URI mismatch でサインインを拒否するようになった。v2.1.231 で `localhost` 形式に戻している。v2.1.229 のまま復旧するには、ClaudeCode を更新するか、サーバー側の登録 redirect URI に `http://127.0.0.1:PORT/callback` を一時的に追加する。固定ポートで登録する場合は `--callback-port` を使い、`http://localhost:PORT/callback` の形で事前登録する。
  - **2026-10-11 訂正**: 以前は「v2.1.229 で bind 先を `127.0.0.1` に変更し、IPv6 / hosts ファイルの設定差で OAuth が完了しなかった環境で効く」と書いていた。現行の MCP ページは、v2.1.229 のこの挙動を redirect URI mismatch を起こした版として扱い、v2.1.231 で `localhost` 形式に戻したと明記している。
- **pre-registered client の redirect URI 不一致修正**(v2.1.231): Slack のように**事前登録済みの OAuth クライアント**を使う MCP サーバーで、redirect URI が一致せず認証に失敗する不具合を修正。上の v2.1.229 の退行に対する修正である。
- **MCP v2 接続の stream 再オープン暴走を修正**(v2.1.232): v2 runtime が `list_changed` 通知を受けるために開いておく stream が、繰り返し再オープンされる不具合。v2 runtime の仕組みと現行の再オープン上限は [MCP client runtimes（v1 / v2）](#mcp-client-runtimesv1--v2) を参照。
  - **2026-10-11 訂正**: 以前は「"MCP v2" という接続方式の存在が CHANGELOG 上で示唆されているが、公式 docs に解説が無い（2026-08-16 時点）」と書いていた。現在は MCP ページの「MCP client runtimes」節に解説がある。

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

### `ENABLE_TOOL_SEARCH` の 5 状態

| 値 | 挙動 |
|---|---|
| (未設定) | 全ツールを defer する（既定） |
| `true` | 強制的に defer する |
| **`auto`** | **defer 対象のツール定義の合計がコンテキストの 10% 未満なら全部 upfront ロードし、10% に達したら全部 defer する**（一部だけ defer する動作ではない） |
| **`auto:N`** | **閾値のパーセントを任意に指定する**（例 `auto:5` で 5%）。2026-08-12 追記 |
| `false` | tool search を無効化し、全ツールを upfront ロードする |

> **2026-10-11 訂正**: 以前は `auto` を「10% に収まれば upfront ロードし、超過分のみ defer する」と書いていたが、現行の MCP ページは「10% に達した時点で全部 defer する」と書いている。

> **`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` は tool search を強制的に off にする**。この場合 `ENABLE_TOOL_SEARCH` では上書きできない。ただし組織は managed settings で tool search を ON に保てる（v2.1.227 以降。2026-10-11 追記）。

### tool search が使えない環境

- ~~**Google Cloud's Agent Platform**~~ → **2026-08-12 更新: 制限は解消した**。**Opus 4.5 / Sonnet 4.5 / Haiku 4.5 以降のモデルでは既定 ON** である（v2.1.221 で Claude 4.5 世代以降に限り再有効化された経緯を経て、公式本文からも "Vertex" 呼称ごと記述が消えた）
- `ANTHROPIC_BASE_URL` が non-first-party（自前 LLM gateway 等）
- **Microsoft Foundry の Azure ホスト deployment**（サーバー側で reject されるため、ClaudeCode が検知して upfront ロードに切り替える。`ENABLE_TOOL_SEARCH` でも上書きできない）
- 対応モデル（`tool_reference` ブロック対応）は **Sonnet 4.5 / Haiku 4.5 / Opus 4.5 以降**

tool search が無効な構成では、接続待ちのサーバーに対して `ToolSearch` の代わりに `WaitForMcpServers` ツールが使われる。

### 関連する per-server / 出力の設定

| 設定 | 内容 |
|---|---|
| **`alwaysLoad: true`** | `.mcp.json` の per-server キー。該当サーバーのみ upfront ロードする。**ツール単位でも指定できる**（ツールの `_meta` に `"anthropic/alwaysLoad": true`、2026-08-12 追記）。**接続完了まで起動をブロックする**（5 秒の connect timeout でキャップ）ため、常用ツールが少数のサーバーに限って使う |
| **`alwaysLoad: false`**（v2.1.287〜） | 該当サーバーの全ツールを tool search の後ろに置く。サーバー作者がツールの `_meta` で upfront 指定したツールも defer される（`alwaysLoad` を書かなければ、作者が指定したツールは upfront ロードされる）。逆にツール側の `_meta` に `"anthropic/alwaysLoad": false` があると、`--mcp-config` / Agent SDK / plugin から渡されたサーバーでは、設定側の `alwaysLoad: true` でもそのツールだけ defer に留まる（それ以外のサーバーでは upfront ロードされる。v2.1.285〜）。2026-10-11 追記 |
| **`CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH`**（v2.1.280〜） | ツールの説明文とサーバーの instructions は、それぞれ**既定 2,048 文字で切り詰められる**。この変数で全サーバー共通の上限文字数を変える。サーバー作者は重要な情報を先頭に置く。2026-10-11 追記 |
| **`MAX_MCP_OUTPUT_TOKENS`** | MCP ツール出力が **10,000 トークンを超えると警告**し（警告閾値は固定で変更できない）、**既定の上限は 25,000 トークン**。上限を超えた成功結果（画像を含まないもの）は切り捨てではなく、**セッションの `tool-results` ディレクトリにファイル保存され、会話にはそのパスを示すメッセージが入る**（Claude は必要な時にファイルを読む）。前景で完了した呼び出しでは、テキスト結果が 50,000 文字を超えるとトークン数に関係なくファイル保存される（この変数では変わらない）。`anthropic/maxResultSizeChars` を宣言したツールは text content でそちらの値が優先される（上限 500,000 文字。画像データは常に `MAX_MCP_OUTPUT_TOKENS` の対象）。**2026-10-11 訂正**: 以前は「既定 25,000 トークンで制限」とだけ書き、超過時にファイル保存される点を書いていなかった |
| `enabledMcpServers` | 既定 off の組み込みサーバー（`computer-use` 等）を opt-in するリスト |
| **`disabledMcpServers`** | `/mcp` パネルのトグルで無効化したサーバーが、**プロジェクト単位で `~/.claude.json` に記録される**（2026-08-12 追記）。`enabledMcpServers` とは互いに素の集合として扱われる |

出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（MCP output limits and warnings / Scale with MCP tool search）/ CHANGELOG v2.1.221

### discovery cache — 有効時は remote サーバーが「初回ツール呼び出しまで接続しない」（v2.1.221〜、v2.1.238 以降は既定 OFF）

v2.1.221 で導入された当初は既定 ON だったが、**v2.1.238 以降は既定 OFF** である（段階的な rollout で有効化されたアカウントを除く）。有効なときは `/mcp` パネルの表示の読み方が変わる。

- 以前に使ったことのある remote の HTTP / SSE サーバーは、**前のセッションで保存したツール一覧をキャッシュから読み込む**。ツールは最初のメッセージから使える。
- `/mcp`（と `/plugin` マネージャー）には `cached 2h ago · connects on first use · 5 tools` のように表示される。
- **実際の接続は、Claude がそのサーバーのツールを初めて呼ぶまで行われない**。
- 有効にするには **`MCP_DISCOVERY_CACHE=1`**。`0` にすると、rollout で有効化されていても OFF に保てる。
- `/mcp` のサーバーメニューで **Disable** / **Clear authentication** を選ぶとキャッシュも破棄される。**Reconnect** は接続済み・失敗中のサーバーではキャッシュを破棄し、`cached` 状態のサーバーではキャッシュを残したまま今すぐ接続する。
- 関連して **`MCP_CONNECTION_NONBLOCKING=0`** で接続の非ブロッキング化も止められる。cached エントリを持つ remote サーバーは `alwaysLoad` を付けても起動をブロックしない。

> キャッシュが有効な環境では「接続済みに見えないが実は正常」という状態になるため、**接続エラーだと早合点しない**こと。
>
> **2026-10-11 訂正**: 以前は「既定挙動の変更」として既定 ON と書き、無効化に `MCP_DISCOVERY_CACHE=0` を挙げていた。現行の MCP ページは「v2.1.238 より前は既定 ON、現在は既定 OFF で `MCP_DISCOVERY_CACHE=1` で有効化」としている。対象も「HTTP / SSE / ws / connector」と書いていたが、MCP ページが挙げるのは remote の HTTP / SSE サーバーである。

### MCP 関連のバグ修正（v2.1.222 / v2.1.224）

| 修正 | 内容 | 版 |
|---|---|---|
| `/usage` の MCP 過大計上 | MCP のトークンが実際より多く計上されていた。**ツール結果を実際に消費したリクエストにのみ按分**されるよう修正 | v2.1.222 |
| deferred 化されたツール名が通知されない | セッション途中で接続した MCP のツールが tool search で deferred になる際、**ツール名がモデルに通知されず呼び出せない**バグを修正 | v2.1.224 |

### 管理コマンドの補足

- **`claude mcp get <name>`** — 個別サーバーの詳細を表示する。**WebSocket (`ws`) サーバーは `claude mcp list` に出ない**ため、確認にはこちらが必要になる。
- `claude mcp add` の `--transport` / `--header` には短縮形 **`-t` / `-H`** がある。`-e` は `--env` と同義。

## Channels（research preview）— 外部イベントをセッションに push する

> ✅ **導入バージョンが判明した（2026-08-16 更新）**: 2026-08-12 時点では「CHANGELOG に記載が無く特定不能」としていたが、再調査で以下を確認した。
>
> | 版 | 内容 |
> |---|---|
> | **v2.1.80** | `--channels`（research preview）を追加。「allow MCP servers to push messages into your session」 |
> | v2.1.81 | permission relay を追加 |
> | v2.1.84 | `allowedChannelPlugins` を追加 |
> | v2.1.128 | console（API キー）認証に対応し、`channelsEnabled` が必須化された |
>
> 公式 [Channels](https://code.claude.com/docs/en/channels) ページ側にはバージョン記載がないため、**版数については CHANGELOG が一次情報**である。

MCP サーバー経由で**外部イベントをセッションへ push** する仕組み。セッション側から取りに行く通常の MCP tool call とは向きが逆である。

| 項目 | 内容 |
|---|---|
| 起動 | `--channels plugin:<name>@<marketplace>` |
| 開発中の channel を読む | `--dangerously-load-development-channels` に `plugin:<name>@<marketplace>` か `server:<name>` の形式で渡す（2026-10-11 追記） |
| managed settings | `channelsEnabled` / `allowedChannelPlugins` |
| 公式提供の channel plugin | **`telegram` / `discord` / `imessage` の 3 種**（2026-09-03 訂正。`fakechat` は quickstart のデモであり research preview の提供物ではない） |
| 利用できない環境 | **Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry** |
| v2 runtime での制約（2026-10-11 追記） | v2 runtime で protocol revision 2026-07-28 をネゴシエートした channel サーバーは、**channel として登録されない**（この revision は channel メッセージを運べない）。stdio サーバーには既定で新しい revision を問い合わせるため、stdio の channel サーバーを従来のハンドシェイクに留めるには `MCP_PROTOCOL_NEGOTIATION=legacy` を設定する（全サーバーが従来のハンドシェイクになる）。[MCP client runtimes（v1 / v2）](#mcp-client-runtimesv1--v2) も参照 |

出典: [Channels](https://code.claude.com/docs/en/channels) / [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（Push messages with channels）

## MCP 仕様 2026-07-28 版と ClaudeCode の対応

2026-07-28 に MCP 仕様の新版が公開され、Anthropic が Claude 製品への対応を進めていることを公式ブログで表明した。仕様レベルの主な変更は次の 3 点である。

| 変更 | 内容 |
|---|---|
| コアの単純化 | **stateful なプロトコルから、ステートレスな request/response モデルへ** |
| 機能の分離 | **MCP Apps / Tasks が「バージョン付き extensions」として分離**された |
| 認可 | **OAuth 2.0 / OIDC 準拠**へ（Microsoft Entra / Okta 等の既存 IdP と組み合わせやすくなる） |

2026-09-25 の公式記事 [Build plugins for Claude](https://claude.com/resources/articles/build-plugins-for-claude) は、Claude がこの最新仕様（通称 **MCP 2.0**。ステートレスなコアを含む）に対応したと述べている。plugin 作者向けには、対応済みの extension として **MCP Apps**（チャット内のインタラクティブ UI）と **Enterprise Managed Auth**（企業ユーザー向けの、ユーザー操作なしで済む OAuth）の 2 つを挙げ、ほかの機能と extension は今後対応するとしている。

> **ClaudeCode 側の対応（2026-10-11 更新）**: MCP ページの「MCP client runtimes」節に対応状況が載った。ClaudeCode は v1 runtime（MCP TypeScript SDK 1.x）と v2 runtime（MCP TypeScript SDK 2.0。protocol revision 2026-07-28 に対応）のどちらかで接続する。v2 が既定になるのは、feature flag を取得するセッションでは v2.1.232 以降、取得しないセッション（Bedrock / Claude Platform on AWS / Agent Platform / Foundry、Claude apps gateway、telemetry off など）では v2.1.274 以降である。v2 は各サーバーに新しい revision に対応しているかを問い合わせ、対応していないサーバーには v1 と同じ方法で接続する。新しい revision で接続した channel サーバーは登録しない。**MCP Apps の UI は ClaudeCode では描画されず、ツールはテキストとして呼ばれる**（mcp-apps quickstart に明記）。詳細は次の 2 節。
>
> **2026-10-11 訂正**: 以前は「ClaudeCode 側の対応状況は未確認。公式ブログは Claude 製品への展開を rolling out soon と述べるのみで、ClaudeCode の対応バージョンには言及していない」と書いていた。

出典: [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude) / [Build plugins for Claude](https://claude.com/resources/articles/build-plugins-for-claude) / [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（MCP client runtimes）

### MCP client runtimes（v1 / v2）

ClaudeCode は**起動のたびに runtime を 1 つ選び、終了するまで使い続ける**。v2 runtime は v1 と同じコードを MCP TypeScript SDK 2.0 に載せたもので、MCP protocol revision 2026-07-28 が加わる。MCP ページの他の節は、v2 runtime と名指ししている箇所を除いて両方の runtime に当てはまる。

| 項目 | 内容 |
|---|---|
| v1 runtime | MCP TypeScript SDK 1.x ベース |
| v2 runtime | MCP TypeScript SDK 2.0 ベース。protocol revision 2026-07-28 に対応 |
| v2 が既定になる版 | feature flag を取得するセッション: **v2.1.232 以降**。取得しないセッション: **v2.1.274 以降**（Bedrock / Claude Platform on AWS / Google Cloud's Agent Platform / Microsoft Foundry のセッション（埋め込みホストが `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` を設定する場合を除く）、Claude apps gateway 経由のサインイン、`DISABLE_TELEMETRY` などで telemetry や feature flag の取得を止めたセッション） |
| revision の問い合わせ | v2 は HTTP / stdio / claude.ai connector の各サーバーに新しい revision に対応しているかを問い合わせ、対応するサーバーとだけ新しい revision で接続する。それ以外のサーバーには v1 と同じ方法で接続する |
| `list_changed` 通知 | 新しい revision のサーバーからは、ClaudeCode が開いておく stream で受け取る。stream が 10 秒以内に閉じたら再オープンは 3 回まで（それで止める）。10 秒以上開いてから閉じた場合（serverless ホストでよくある）は、1 時間に 5 回再オープンしたあと約 6 時間待つ。再オープンまでは最後に取得したツール一覧を使うので、早く反映したいときは `/mcp` から reconnect する |
| channel | 新しい revision で接続した channel サーバーは登録しない（[Channels](#channelsresearch-preview-外部イベントをセッションに-push-する) 参照） |
| OAuth | 認可レスポンスの issuer が想定と違うサインインは失敗させる。資格情報は HTTPS か `localhost` / `127.0.0.1` / `::1` の token endpoint にしか送らない。ローカルネットワーク上の機器など、それ以外の plain `http://` の token endpoint を持つサーバーはサインインに失敗する（[Refusing to send credentials to non-https token endpoint](https://code.claude.com/docs/en/errors#refusing-to-send-credentials-to-non-https-token-endpoint)） |
| Anthropic 側の制御 | Anthropic は、ClaudeCode が取得する feature flag で特定のサーバーを古い protocol や stream なしに留めることがある |
| 自分で選ぶ | runtime は **`MCP_SDK_GENERATION`** に `v1` / `v2` を設定する。新しい revision を問い合わせるかどうかは **`MCP_PROTOCOL_NEGOTIATION`** に `auto` / `legacy` を設定する |

出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（MCP client runtimes / Notification streams on the v2 runtime）

### MCP Apps — ClaudeCode では UI を描画しない

MCP Apps は、MCP サーバーが Claude の会話の中に描画するインタラクティブな UI（グラフや地図など）である。サーバー側では、`ui://` URI の resource（中身は描画する HTML）と、ツールの `_meta.ui.resourceUri` でその resource を指す形で実装する。

- **UI を描画するのは MCP Apps に対応したホスト**（Claude の desktop app など）である。**ClaudeCode はツールをテキストとして呼び、UI は描画しない**。同じサーバーを ClaudeCode からテキスト専用クライアントとして使うことはできる。
- ツールが `structuredContent` を返すようにすると、ClaudeCode の `stream-json` 出力で Claude が受け取る `tool_result` は、`content` のテキストではなく `structuredContent` の JSON 文字列になる（quickstart の例）。
- claude.ai や desktop app に URL で追加したサーバーへは Anthropic のインフラからインターネット経由で接続するため、`localhost` のサーバーには届かない。UI の描画を確かめるには、サーバーを公開ホストに置くか、desktop app の設定ファイルから SDK のサンプルサーバーを繋ぐ。
- MCP サーバー自体の作り方は [Build your first MCP server for Claude](https://claude.com/docs/connectors/building/quickstart) から始める。

> **2026-10-11 更新**: 以前は MCP Apps を ClaudeCode が描画するかを確認できていなかった。mcp-apps quickstart に「Claude Code calls the tool as text and doesn't render the UI」と明記されたため、未確認事項は解消した。

出典: [Add an interactive UI to your MCP server](https://claude.com/docs/connectors/building/mcp-apps/quickstart)

## claude.ai の connectors と custom connector

**claude.ai の connectors は ClaudeCode に自動で現れる**。ClaudeCode に claude.ai アカウントでログインしていれば、[claude.ai/customize/connectors](https://claude.ai/customize/connectors) で追加した MCP サーバー（connectors）が `/mcp` に claude.ai 由来の表示付きで並ぶ。Team / Enterprise プランでは admin しか追加できない。

- **読み込まれるのは、有効な認証方式が claude.ai サブスクリプションのログインのときだけ**である。`ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` / `apiKeyHelper` が有効な場合、Bedrock や Agent Platform など third-party provider を使う場合、`claude setup-token` のトークンを `CLAUDE_CODE_OAUTH_TOKEN` に入れている場合などは読み込まれない。`/mcp` に出ないときは `/status` で認証方式を確認する。
- ClaudeCode 側で同じ URL のサーバーを追加していると、そちらが優先され、connector は `/mcp` で hidden と表示される。
- 個別に止めるなら `deniedMcpServers`（例: `serverName` に `"claude.ai Slack"`）か `/mcp` のトグル、全部止めるなら `disableClaudeAiConnectors: true` か `ENABLE_CLAUDEAI_MCP_SERVERS=false`。

### custom connector — ディレクトリに無い remote MCP を URL で追加する

Connectors Directory に無い remote MCP サーバーは、URL を指定して custom connector として追加する。Free / Pro / Max プランは自分のアカウントに **Customize > Connectors > Add custom connector** で追加する（Free プランは 1 個まで）。Team / Enterprise プランは Owner が **Organization settings > Connectors** から組織に追加し、各メンバーが自分のアカウントで接続する（Enterprise では組織のライブラリを管理する custom role を持つメンバーも追加できる）。旧ページ `connectors/custom/remote-mcp` と `connectors/custom/desktop-extensions` は、現在このページ（add-unlisted）にリダイレクトされる。

| 設定 | 選択肢 |
|---|---|
| **Authentication** | **Sign in now**（使う前に各ユーザーが OAuth でサインイン）/ **Sign in when needed**（資格情報なしで接続し、サーバーが求めたらサインインを促す）/ **No sign-in**（URL にアクセスできる人は誰でも使える。API キーで認証するサーバーはこれを選び、Request headers にキーを入れる） |
| **OAuth client**（No sign-in 以外） | **Use Claude's published identity**（推奨。Anthropic がホストする Client ID Metadata Document をサーバーが読む。サーバー側の対応が必要）/ **Register automatically**（Dynamic Client Registration。多くのサーバーで動くが、client registration が増えていく）/ **Use your own OAuth client**（サーバーに登録済みの client ID を入れる） |
| **Request headers**（beta） | API キーや bearer token などの固定の資格情報を毎リクエストで送る。一部の組織にだけ提供されており、ダイアログに項目が無ければ未提供。OAuth と併用でき、OAuth の bearer token と一緒に送られるが、OAuth 接続では `Authorization` ヘッダーは設定できない。組織で 1 つの資格情報を共有するサービス向けで、各自のアカウントでサインインさせたいなら OAuth を使う |
| **Advanced > Transport** | サーバーのドキュメントに指示がある場合だけ変える。URL が `/sse` で終わると旧 SSE transport になる |

出典: [Add a connector that isn't in the directory](https://claude.com/docs/connectors/custom/add-unlisted)

### Google Docs / Sheets / Slides connectors（beta、2026-10-06）

Claude から Google のファイルを作成・編集する connectors が beta で追加された。Google ファイルのリンクを貼るか、doc / sheet / deck を作るよう頼むと、対応する構成では会話の横のペインで開く。Claude のアクセス範囲は、既存の Google の共有権限と同じになる。Team / Enterprise プランでは、owner か primary owner が先に connectors を有効にする必要がある。同時に発表された Claude for Google Workspace（Google Docs / Sheets / Slides のサイドバーで動く add-on。全有料プランで public beta）とは別物である。

> ⚠️ **ClaudeCode の `/mcp` に出るかは未確認**: 上記のとおり claude.ai の connectors が ClaudeCode に自動で現れる仕組みはある（MCP ページ）。ただし、今回の Google Docs / Sheets / Slides connectors がそれに該当して `/mcp` に並ぶかは確認できていない。

出典: [Claude now works with Google Docs, Sheets, and Slides](https://claude.com/resources/articles/claude-now-works-in-google-docs-sheets-and-slides) / [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)（Use MCP servers from claude.ai）

## 組織が MCP サーバーを配布する — `managedMcpServers`（v2.1.259〜）

**managed settings の `managedMcpServers` に HTTP / SSE の MCP サーバーを並べると、組織の全ユーザーに配布できる**（2026-10-11 追記）。ユーザーが自分で追加したサーバーはそのまま残り、配布分が加わる。サーバー一式を排他的に固定する `managed-mcp.json` や、`allowedMcpServers` / `deniedMcpServers` による制限とは別の仕組みである。v2.1.259 以降で有効で、それより前の版はこのキーを無視する（版数は managed-mcp ページと CHANGELOG 2.1.259 で一致）。

```json
{
  "managedMcpServers": {
    "search": {
      "type": "http",
      "url": "https://search.example.com/mcp"
    }
  }
}
```

| 項目 | 内容 |
|---|---|
| 置ける場所 | server-managed settings / Claude apps gateway の policy / MDM プロファイルやレジストリ policy / `managed-settings.json`。user・project・local の settings ファイルに書くと警告付きで捨てられる。ユーザーが書き込める HKCU レジストリや、埋め込みホストが渡す parent settings からも読まない |
| エントリの形 | project の `.mcp.json` の HTTP / SSE サーバーと同じ（`headers` / `oauth` も可） |
| 読み込まれる条件 | `type` が `http` か `sse`（`streamable-http` も可）。`url` が `https://`（`localhost` でも plain `http://` は拒否）。`command` / `args` / `env` / `headersHelper` を持たない。`${VAR}` を含まない（展開されない）。条件を満たさないエントリは捨てられ、`/status` で通知を確認できる |
| 優先順位 | 同名の local / project / user スコープのサーバー、同じ URL の plugin サーバーや claude.ai connector より優先する。`managed-mcp.json` と同名なら `managed-mcp.json` 側が優先する |
| ユーザーにできること | 編集・削除はできない（`claude mcp remove` は組織提供のサーバーだと報告する）。`/mcp` の **Managed MCPs** で自分の分だけ OFF にはできる。`deniedMcpServers` も効く |
| 注意 | `headers` の値は、その端末の managed settings を読める人（ユーザー本人を含む）なら誰でも読める。対象者全員向けに発行した資格情報を使うか、`headers` を省いて各ユーザーに OAuth でサインインさせる。Claude Desktop にも同名の managed setting があるが、値は形の違う配列なので、そのままコピーしない |

出典: [Control MCP server access for your organization](https://code.claude.com/docs/en/managed-mcp)（Provide servers through managed settings）/ [What's new 2026-w36](https://code.claude.com/docs/en/whats-new/2026-w36) / CHANGELOG 2.1.259

## `.mcp.json` project-scope の workspace-trust ゲート(v2.1.196〜)

**破壊的変更**: v2.1.196 以降、`claude mcp list` / `claude mcp get` は `.mcp.json` の approvals を **workspace-trust ダイアログを承認するまで読まない**(non-checked-in settings のみ利用)。

- project の `.claude/settings.json` に書いた `enableAllProjectMcpServers` / `enabledMcpjsonServers` は **untrusted folder では無視される**
- チームでリポジトリを共有していて、pull 直後に MCP が動かない場合はまず workspace-trust の承認状態を確認する
- 出典: [Claude Code MCP Servers](https://code.claude.com/docs/en/mcp)
