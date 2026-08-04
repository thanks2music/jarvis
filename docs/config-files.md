# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) / [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Sandboxing](https://code.claude.com/docs/en/sandboxing) / [Accessibility](https://code.claude.com/docs/en/accessibility) / [Corporate launcher](https://code.claude.com/docs/en/corporate-launcher) / [Workflows](https://code.claude.com/docs/en/workflows) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-04時点)

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
- **内容**: パーミッション（allow/deny）、環境変数、UI 設定（`showTurnDuration`、`language` など）。※ MCP サーバーの user / local スコープは settings.json ではなく `~/.claude.json` に保存される（後述の「MCP サーバーのスコープ」を参照）
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
- **workspace trust の挙動 (要注意)**: **v2.1.196〜199** で workspace trust が rejected の下では local 設定が **ignored** になっていたが、**v2.1.200 で pre-v2.1.196 挙動に復帰**した (ホームディレクトリや `CLAUDE_CONFIG_DIR` セット時は allow rules 適用)。この短期的な挙動変化は、v2.1.199 以下で運用していたリポで「local 設定が突然効かなくなった」経験があった場合の原因になり得る。現行 (v2.1.200+) では以前通り効く。出典: [Permissions — code.claude.com](https://code.claude.com/docs/en/permissions)

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

> **permission ルールだけはスコープ横断で「マージ」される**: 公式は「**Permission rules merge across scopes; other settings follow priority order**」と明記している。つまり上の優先順位は **permission 以外の設定** に適用される規則であり、`permissions.allow` / `ask` / `deny` は上位スコープが下位を置き換えるのではなく**全スコープのルールが合算**される（その上で deny が allow より強い）。「project の allow を local で消す」ことはできず、消したいなら deny を書く必要がある。出典: [Settings](https://code.claude.com/docs/en/settings)

## MCP サーバーのスコープ

`claude mcp add` コマンドで MCP サーバーを追加する際、`--scope` オプションでスコープを指定する。

| スコープ | 保存先 | 用途 | Git 管理 |
|----------|--------|------|----------|
| `user` | `~/.claude.json` | 全プロジェクトで使う個人用 MCP サーバー | しない |
| `local`（デフォルト） | `~/.claude.json`（プロジェクトパス配下のエントリ） | 現在のプロジェクトでのみ使うローカル MCP サーバー | しない |
| `project` | `.mcp.json` | チーム全員で共有する MCP サーバー | **する** |

> **重要**: MCP サーバーの `local` / `user` スコープはいずれも **`~/.claude.json`** に保存される。これは settings ファイル（`.claude/settings.local.json` / `~/.claude/settings.json`）とは**別物**であり、公式も明示的に注意喚起している。本表の「設定ファイル」の話とは保存先が異なる点に注意する。

```bash
# user スコープ（全プロジェクト共通）
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic

# local スコープ（デフォルト、個人のプロジェクト設定）
claude mcp add --transport http stripe --scope local https://mcp.stripe.com

# project スコープ（チーム共有、.mcp.json に保存）
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

## パーミッションモード（permission modes）

ClaudeCode は「ツール実行前にどの程度確認するか」を **6 つのパーミッションモード**で制御する。`settings.json` の `permissions.defaultMode` で既定値を設定でき、セッション中は `Shift+Tab` でサイクル切替する。

| モード | 確認なしで実行される範囲 | 主な用途 |
|--------|------------------------|----------|
| `default`（**v2.1.200 以降 UI/CLI 表記は「Manual」**、`manual` エイリアスも受理: `claude --permission-mode manual` / `"defaultMode": "manual"`。v2.1.203+ でステータスバーに `⏸ manual mode on` バッジ表示） | 読み取りのみ | 通常作業・センシティブな作業 |
| `acceptEdits` | 読み取り + ファイル編集 + 一般的な filesystem コマンド（`mkdir`/`touch`/`rm`/`rmdir`/`mv`/`cp`/`sed` 等） | レビュー前提でコードを回す |
| `plan` | 読み取りのみ（変更しない） | 変更前のコードベース調査 |
| `auto` | すべて（バックグラウンドの分類器が安全性を審査） | 長時間タスク・確認疲れの軽減 |
| `dontAsk` | 事前承認済みツールのみ（それ以外は自動拒否） | CI / 制限環境 |
| `bypassPermissions` | すべて（チェックを全バイパス） | ネット遮断したコンテナ / VM 限定 |

- `acceptEdits` が自動承認する filesystem コマンドは `mkdir` / `touch` / `rm` / `rmdir` / `mv` / `cp` / `sed`。`LANG=C` / `NO_COLOR=1` 等の安全な環境変数 prefix 付き、`timeout` / `nice` / `nohup` ラッパー付きも自動承認の対象になる。PowerShell tool 有効時は `Set-Content` 等も含む。
- `bypassPermissions` 以外のすべてのモードで、**保護パス**（`.git`、`.claude`（一部除く）、`.mcp.json`、`.bashrc` 等）への書き込みは自動承認されない。一方 **`bypassPermissions` は v2.1.126 以降、保護パスへの書き込みも prompt せず実行する**（チェックを全バイパスする設計のため。`rm -rf /` / `rm -rf ~` のみ circuit breaker として依然 prompt される）。
- `defaultMode: "auto"` は **user settings (`~/.claude/settings.json`) でのみ有効**。project / local settings に書いても無視される（リポジトリが自身に auto を付与できないようにするため）。
- 管理者は managed settings で `permissions.disableAutoMode` / `permissions.disableBypassPermissionsMode` を `"disable"` にして特定モードを禁止できる。
- **auto mode の分類器モデルは v2.1.210 以降 Sonnet 5 が既定**（allowlist が Sonnet 5 を許さない場合はセッションモデルまたは Opus にフォールバック）。セッションの初回リクエストで検証し、以降は pin される。v2.1.216 では OAuth token 期限切れ時に分類器が「HTTP 401」エラーで **deny してしまう不具合**が修正された。
- **`claude auto-mode reset`**（v2.1.212〜）で auto mode 設定を既定へ復元できる。`--yes` を付けると確認をスキップする。
- **v2.1.221 の分類器まわりの改善**: 並列ツール呼び出しの権限チェックが cache 効率化され、**判定保留中にモードを切り替えた場合は stale な結果を適用せず確実にプロンプトを出す**ようになった。会話 prefix の cache 再利用により prompt-cache コストも削減されている。同 version で「Permission mode changed while the auto-mode classifier call was queued」の反復通知は承認プロンプトから削除された。出典: CHANGELOG v2.1.221

> auto mode の詳細（分類器のブロック対象・利用条件・フォールバック挙動）は [`docs/best-practices.md`](best-practices.md) を参照。

### permission ルールの重要な変更（v2.1.210 / v2.1.211 / v2.1.214）

既存の permission ルールが **黙って無効化される / 意図より広く効く** 変更が入っている。設定済みのルールは一度見直す価値がある。

#### 1. path 付きルールは `Edit` / `Read` のみ有効になった（v2.1.210）

file permission のチェックは **`Edit(path)` と `Read(path)` にのみマッチする**。他ツールに path を付けたルールは **accept されるが決してマッチしない（never matched）** 状態になり、allow / deny / ask の各ルールごとに**起動時警告**が出る。

| 非推奨の書き方 | 置き換え |
|---|---|
| `Write(docs/**)` | **`Edit(docs/**)`** |
| `NotebookEdit(notebooks/**)` | **`Edit(notebooks/**)`** |
| `Glob(docs/**)` | **`Read(docs/**)`** |
| `MultiEdit(...)`（legacy） | **`Edit(...)`** |

- **path を付けない tool 名だけのルール**（`Write` 単体の deny 等）は影響を受けない。
- ⚠️ **実害**: 既存の `Write(...)` / `Glob(...)` ルールは「書いてあるのに効かない」状態になる。deny を意図していた場合、**防いでいるつもりで防げていない**ことになるため、起動時警告を確認する。
- **例外**: `--allowedTools` で渡した `Glob` ルールだけは起動時警告が出ない。CLI 経由の設定は自分で気付く必要がある。
- 起動時警告の実際の文面は次の形である。

  ```text
  Permission deny rule (.claude/settings.json): Write(docs/**) is not matched by file
  permission checks — only Edit(path) rules are. Use Edit(docs/**) instead
  (Edit rules cover all file-editing tools).
  ```

#### 1-2. `Read` の deny は `Edit` も塞ぐ（v2.1.208〜）

公式は「A **`Read` deny rule also blocks the Edit tool** on the same path, including creating a new file there」と明記している。つまり `Read(secrets/**)` を deny すると、同じパスへの `Edit`（新規ファイル作成を含む）も塞がれる。

ただし **`Write` と `NotebookEdit` はカバーされない**。「どのツールからも変更させたくないパス」には、`Read` deny に加えて **`Edit` deny も明示的に書く**必要がある（`Edit` ルールは全てのファイル編集系ツールをカバーするため）。

#### 1-3. ルールと hook matcher は canonical tool 名のみにマッチする

transcript やパーミッションダイアログに表示される**ラベル**と、ルール記述に使う **canonical 名**は異なる場合がある。公式が挙げる例は「the tool labeled **`Stop Task`** in the transcript has the canonical name **`TaskStop`**」で、`Stop Task` と書いたルールは何にもマッチしない。canonical 名は [Tools reference](https://code.claude.com/docs/en/tools-reference) を参照する（deny / ask ルールについては上記の起動時警告がミスマッチを検出してくれる）。

#### 2. single-segment パターンの深さ挙動が allow / deny で非対称になった（v2.1.214）

同じ `dir/**` という書き方でも、ルール種別で解釈が変わる。

| ルール種別 | `Edit(src/**)` / `Read(secrets/**)` の解釈 |
|---|---|
| **allow** | **`<cwd>/src` のみ**にマッチ（任意の深さに効かせたいなら `Edit(**/src/**)`） |
| **deny / ask** | **任意の深さ**の `secrets` にマッチ（従来どおり広く効く） |

これは **v2.1.214 のセキュリティ修正**に伴う変更である。それ以前は単一セグメントの `dir/**` allow ルールが**ツリー内の任意の `dir/` への書き込みを自動承認していた**（例: `Edit(src/**)` が `vendor/foo/src/` への書き込みまで許可していた）。同 version では他に、PowerShell 5.1 での permission チェック回避、file descriptor リダイレクト形式の fail-closed 化、`file -m` / `file -f` の権限要求化も修正されている。

**v2.1.221 でも権限チェックのバイパスが 2 件修正された**（いずれも「チェックをすり抜けて実行できていた」類のため、古いバージョンを使い続ける場合はリスクとして認識しておく）。

| 修正内容 | 影響 |
|---|---|
| **zsh の `[[ ]]` 正規表現条件式**に隠したコマンドが Bash tool の権限チェックを回避して実行できた | 該当コマンドは権限プロンプトの対象になった |
| **Windows の PowerShell 権限チェックが引用符を含むパスを誤処理**していた | 該当パスは承認プロンプトの対象になった |

出典: CHANGELOG v2.1.221

#### 3. 「always allow」の保存先がリポジトリルートになった（v2.1.211）

プロンプトで「always allow」を選んだ際のルールは **リポジトリルートに保存される**。これにより **git worktree で与えた承認がセッション・worktree を跨いで永続化**する。worktree ごとに承認をやり直す必要がなくなった反面、**一時的な worktree で与えた許可がリポジトリ全体に残る**点は意識しておく。

#### 4. `EndConversation` tool は permission ルールで除去できない（v2.1.214）

**`EndConversation`** は、極端に敵対的な振る舞いや jailbreak の試行に対して **Claude 側からセッションを終了できる**ツールである。**他のツールが 1 つでも残っている限り、deny / ask ルールや `disallowedTools` では取り除けない**設計になっている（「全ツール禁止」でなければ常に残る）。通常の開発利用で問題になることはないが、「ツール一覧を完全に固定したい」設計では前提として押さえておく。出典: [Tools reference](https://code.claude.com/docs/en/tools-reference) / CHANGELOG v2.1.214

出典: [Permissions](https://code.claude.com/docs/en/permissions) / CHANGELOG v2.1.210 / v2.1.211 / v2.1.214

## settings.json の主な設定項目

`settings.json`（user / project / local）で指定できる代表的なフィールド。網羅的な一覧は公式 [Settings](https://code.claude.com/docs/en/settings) を参照する。

| フィールド | 役割 |
|-----------|------|
| `permissions.allow` / `ask` / `deny` | ツール実行の許可・確認・拒否ルール。tool 名に **glob** 可（`"*"` で全拒否、未知 tool 名は起動時に警告）。`Tool(param:value)` でツール入力パラメータをワイルドカードマッチ（例 `Agent(model:opus)` で Opus サブエージェントをブロック、v2.1.178〜）。**v2.1.178 詳細**: matches 対象は top-level parameters(`model` / `isolation` / `run_in_background` 等)、**1 param per rule**、`*` wildcard 対応。`command` / `file_path` / `path` / `url` などの **canonical-input fields は除外**(startup 警告)、tool の specifier(`Bash(git *)` 等)を使う。tool-name の glob(`mcp__*` 等)は deny / ask で有効。**`Cd` permission rule**(v2.1.169〜、`/cd` の移動先を制御。bare `Cd` deny で `/cd` 全体無効化、`Cd(path)` で allowlist モード、`//` / `~/` / `/` アンカー + `*` / `**` glob 対応)。**Symlink 挙動明示**: allow rules は symlink path と target の両方一致必要 (fall back to prompt)、deny rules はどちらか一致でブロック |
| `permissions.defaultMode` | 既定のパーミッションモード（前掲の 6 モード） |
| `permissions.disableAutoMode` / `disableBypassPermissionsMode` | `"disable"` で特定モードを禁止（managed 向け） |
| `model` / `availableModels` / `enforceAvailableModels` | 既定モデル / 選択可能モデルの allowlist / allowlist を Default モデルにも強制（managed・policy のみ有効、v2.1.175〜）。フル model ID 例: `claude-opus-5`・`claude-opus-4-8`・`claude-fable-5`・`claude-sonnet-5`（**Opus 5 は要 v2.1.219+**、Fable 5 は要 v2.1.170+、Sonnet 5 は要 v2.1.197+）。**v2.1.187 / v2.1.196 で強化**: managed で `/model` ピッカー・`--model`・`ANTHROPIC_MODEL` 環境変数の 3 経路すべてを制限可能。`/model` UI に "Org default" / "Role default" ラベル表示 |
| `fallbackModel` | プライマリが過負荷・不在のとき順次試す代替モデル（最大 3 つ、CLI は `--fallback-model`、v2.1.168〜） |
| `modelOverrides` | サブエージェント種別ごとのモデル上書き |
| `effortLevel` | 既定 effort（`low`/`medium`/`high`/`xhigh`。`max`/`ultracode` は session-only で不可）。⚠️ **Opus 5 には model-default hold が無い**ため、旧モデル向けに設定した値（例 `xhigh`）が Opus 5 でもそのまま使われる。他モデル（Fable 5 / Opus 4.8 / 4.7）は初回起動時にモデル既定で上書きされる。Opus 5 の公式推奨は `high` 起点（[model-comparison.md](model-comparison.md) §6.3） |
| `alwaysThinkingEnabled` | extended thinking を既定で有効化 |
| `outputStyle` / `statusLine` | 出力スタイル / カスタムステータスライン |
| `agent` | メインスレッドを名前付き subagent として起動 |
| `hooks` | ライフサイクルイベントの Hooks 定義 |
| `env` | 環境変数。Fable 5 関連の新変数として `ANTHROPIC_DEFAULT_FABLE_MODEL`（Fable 5 のデフォルト model id 上書き）・`DISABLE_PROMPT_CACHING_FABLE`（Fable 5 のプロンプトキャッシュ無効化）が追加。**追加された環境変数(2026-07 時点)**: `CLAUDE_CLIENT_PRESENCE_FILE`(v2.1.181、指定ファイル存在中は mobile push 抑制)、`CLAUDE_CODE_DISABLE_MOUSE_CLICKS`(v2.1.195、フルスクリーンのクリック/ドラッグ/ホバー無効化、ホイールは維持)、`CLAUDE_ENABLE_STREAM_WATCHDOG`(v2.1.197、5 分無音で中断・再試行、デフォルト有効。`=0` で無効化)、`CLAUDE_CODE_DISABLE_ARTIFACT`(Artifacts の無効化)、`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(v2.1.187、remote MCP tool call の 5 分 idle timeout 調整)、`OTEL_LOG_ASSISTANT_RESPONSES`(v2.1.193、**セキュリティ注意**: 未設定時は `OTEL_LOG_USER_PROMPTS` を継承するため、既にプロンプトログを取っている環境は upgrade 時にアシスタント応答も自動で流れ始める。抑止するには明示的に `=0` を設定)、**`CLAUDE_AFK_TIMEOUT_MS`**(v2.1.198、idle 時に `AskUserQuestion` を自動継続。settings の `askUserQuestionTimeout` と対応)、**`CLAUDE_AFK_COUNTDOWN_MS`**(v2.1.198、自動継続前のカウントダウン開始、既定 20000ms)、**`CLAUDE_CODE_BRIDGE_SESSION_ID`**(v2.1.199、Remote Control 接続中に自動設定)、**`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS`**(v2.1.198、組み込み Explore / Plan subagent のみ無効化)、**`CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`**(v2.1.196、supervisor 停止時のバックグラウンド handoff 停止)、**`API_FORCE_IDLE_TIMEOUT`**(v2.1.169、5 分 idle timeout の上書き)、**`ANTHROPIC_FOUNDRY_AUTH_TOKEN`**(v2.1.203、Microsoft Foundry Bearer token 認証)。**追加された環境変数(v2.1.208〜v2.1.219)**: **`CLAUDE_CODE_PROCESS_WRAPPER`**(v2.1.208、企業ランチャー経由で自己 spawn プロセスを起動。Windows では無視。agent teams の tmux / iTerm2 ペインと Remote Control worker は v2.1.210 以降でカバー)、**`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`**(v2.1.212、既定 200、無効化不可)、**`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`**(v2.1.217、既定 20、ultracode は免除)、**`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`**(v2.1.217、nested subagent の階層数)、**`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`**(v2.1.212、既定 200)、**`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`**(v2.1.212、2 分超の MCP tool call を自動バックグラウンド化する閾値。`0` で無効化)、**`CLAUDE_CODE_FORWARD_SUBAGENT_TEXT`**(v2.1.211、stream-json に subagent の text / thinking を含める。CLI は `--forward-subagent-text`)、**`CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`**(v2.1.214、OTel content 属性の切り詰め上限。既定 60KB)、**`CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD`**(v2.1.208、Bedrock streaming の content-type チェックをスキップ)、**`CLAUDE_AX_SCREEN_READER`**(screen reader mode。CLI は `--ax-screen-reader`)、**`CLAUDE_CODE_RESUME_INTERRUPTED_TURN`**(v2.1.211、中断ターンの自動再開。**v2.1.221 で `=0` による無効化が効かない不具合が修正**され、falsy 値が尊重されるようになった。関連: `CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS`)、**`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`**(Bash / hooks / MCP stdio の子プロセスから Anthropic・クラウド認証情報を除去。Linux では PID namespace 分離も伴い `ps` / `pgrep` / `kill` が host プロセスを見られなくなる。関連: `CLAUDE_CODE_SCRIPT_CAPS`)、**`DISABLE_EXTRA_USAGE_COMMAND`**(`/usage-credits` の無効化)。**廃止**: `CLAUDE_CODE_CONNECT_TIMEOUT_MS`(v2.1.186 で削除) |
| `askUserQuestionTimeout` | **v2.1.200〜**。`AskUserQuestion` の無応答時に自動継続するタイムアウト。値は `"60s"` / `"5m"` / `"never"` (既定 `"never"`)。**project / local からは読まれず user-level のみ**。環境変数 `CLAUDE_AFK_TIMEOUT_MS` / `CLAUDE_AFK_COUNTDOWN_MS` と併用 |
| `cleanupPeriodDays` | **v2.1.203〜**。セッションファイル・orphaned worktree の自動削除間隔 (日数)。設定ファイルが読めない/parse 失敗時は**クリーンアップが pause し `/status` に警告** (managed 設定のみ挙動継続) |
| `axScreenReader` | 設定キー自体は **v2.1.181〜**、**screen reader mode という機能そのものは v2.1.208 で追加**された（視覚的 TUI をラベル付きの線形テキストに置換し、VoiceOver / NVDA で読める形にする）。`tui` 設定は無効化される。CLI `--ax-screen-reader` と環境変数 `CLAUDE_AX_SCREEN_READER` が優先。v2.1.210 / 214 / 217 / 218 で読み上げ改善（permission mode 変更のアナウンス、削除テキストのアナウンス等）。出典: [Accessibility](https://code.claude.com/docs/en/accessibility) |
| `autoMemoryEnabled` / `autoMemoryDirectory` | Auto Memory の有効化 / 保存先（[memory.md](memory.md) 参照） |
| `skillOverrides` / `maxSkillDescriptionChars` / `skillListingBudgetFraction` | Skills の可視性・description キャップ・予算（[skills.md](skills.md) 参照） |
| `sandbox` | Bash サンドボックスの設定。主要サブフィールドは下表を参照 |
| `extraKnownMarketplaces` | 追加 Plugin marketplace（[plugins.md](plugins.md) 参照） |
| `claudeMd` / `claudeMdExcludes` | managed CLAUDE.md 本文 / 読み込み除外パターン |
| `autoMode` / `useAutoModeDuringPlan` | auto mode の挙動カスタマイズ / plan mode 中の auto 利用。主要サブフィールドは下表を参照。**v2.1.218 の挙動変更**: `useAutoModeDuringPlan` 有効時、plan mode でも**静的解析で read-only と証明できない Bash はプロンプトを出さず分類器が裁定する**ようになった。同 version で dangerous-`rm` / background-`&` / suspicious-Windows-path の各チェックも permission dialog を開かず分類器裁定に変わっている |
| `permissions.additionalDirectories` | セッション開始時から作業対象に含める追加ディレクトリ（`/add-dir` の設定版） |
| `allowedHttpHookUrls` | `type: "http"` の Hooks が POST できる URL の allowlist |
| `disableAgentView` / `disableSkillShellExecution` | agent view の無効化 / skill からのシェル実行の禁止 |
| `fileCheckpointingEnabled` | ファイル変更のチェックポイント（`/rewind` の巻き戻し対象）の有効化 |
| `showClearContextOnPlanAccept` | plan 承認時に「コンテキストをクリアするか」の選択を表示する |
| `includeGitInstructions` | システムプロンプトへの git 操作指示の同梱を制御 |
| `respondToBashCommands` | Shell mode `!` の自動応答トグル(v2.1.186〜)。デフォルト `true`(コマンド出力を Claude が読んで応答)。`false` で従来の「context 追加のみ」に戻す |
| `disableSideloadFlags` | managed 専用(v2.1.193): `--plugin-dir` / `--plugin-url` / `--agents` / `--mcp-config` などの sideload 系フラグをブロック |
| `disableClaudeAiConnectors` | managed 専用(v2.1.182): claude.ai connectors の利用を禁止 |
| `enableArtifact` | managed 専用(v2.1.196): Artifacts の利用を制御(admin 側のマスタースイッチ) |
| `disableAllHooks` | 全 Hooks の無効化（managed hooks は managed 側でのみ無効化可、[hooks.md](hooks.md) 参照） |
| `workflowKeywordTriggerEnabled` / `disableWorkflows` / `ultracode` | dynamic workflows（ultracode）のキーワードトリガ / 無効化 / 既定起動（v2.1.157〜） |
| `parentSettingsBehavior` | 上位スコープ設定の継承挙動（v2.1.133〜） |
| `policyHelper` | パーミッション判定を委譲する外部ヘルパー |
| `defaultShell` | Bash ツールが使う既定シェル |
| `autoUpdatesChannel` | 自動更新チャンネルの選択 |
| `teammateMode` | Agent teams の動作モード。`"iterm2"`(v2.1.186)を指定すると iTerm2 統合を有効化(`it2` CLI が無いと警告) |
| `plansDirectory` | plan mode の計画ファイル保存先 |
| `requiredMinimumVersion` / `requiredMaximumVersion` | 許可する ClaudeCode バージョン範囲（managed 向け、v2.1.163〜） |
| `disableRemoteControl` | `/remote-control` の無効化 |
| `strictPluginOnlyCustomization` | カスタマイズを Plugin 経由に限定する（v2.1.202 以降は array 指定対応で、対象カテゴリを細かく列挙できる） |
| `advisorModel` | `/advisor`（第 2 モデル相談ツール）が使うモデル（v2.1.98〜） |
| `attribution` | commit / PR の署名（Co-Authored-By 等）のカスタマイズ。**サブフィールド**: `attribution.sessionUrl`(v2.1.183、web / Remote Control セッションが commit / PR に添える claude.ai セッションリンクを省略できる) |
| `subagentStatusLine` | サブエージェント用のステータスライン。**v2.1.214 以降、payload に reasoning effort が含まれる**（subagent ごとの effort を表示できる） |
| `footerLinksRegexes` | フッター行に正規表現マッチのリンクバッジを追加（v2.1.176〜） |
| `language` | セッションタイトルの言語を固定（既定は会話言語で自動生成、v2.1.176〜） |
| `disableBundledSkills` | バンドルスキル・workflows・組込コマンドをモデルから隠す（env `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` でも可） |
| `workflowSizeGuideline` | dynamic workflows (ultracode) が 1 セッションで spawn する agent 数の目安を制御する。**既定は `medium`**。受理値は 4 種（下表）。任意の settings ファイルから設定可で、**設定されている間は `/config` の該当行が非表示**になる（settings の値が `/config` より優先）。実行中の workflow には現在の size が status line に表示される。関連 OpenTelemetry 属性: `workflow.run_id` / `workflow.name`（v2.1.202〜）。詳細は下記の注記を参照 |
| `emojiCompletionEnabled` | **v2.1.217〜**。`:shortcode:` 形式での絵文字補完（既定 `true`）。**v2.1.221 以降は `:thumbsup:` / `:thumbsdown:` / `:love:` 等の別名 shortcode も受理**する |
| `vimInsertModeRemaps` | **v2.1.208〜**。vim insert mode で 2 キー列を別キーにリマップする（例: `jj` → Escape） |
| `processWrapper` | **v2.1.210〜**（環境変数版 `CLAUDE_CODE_PROCESS_WRAPPER` は v2.1.208）。企業ランチャー経由で ClaudeCode の自己 spawn プロセスを起動する。**project / local からは設定不可**。詳細は [Corporate launcher](https://code.claude.com/docs/en/corporate-launcher) |
| `disableAutoMode` | `"disable"` で auto mode を封鎖する（Shift+Tab のサイクルから除去し、`--permission-mode auto` も拒否）。managed settings 向け。Bedrock / Google Cloud / Microsoft Foundry 環境で管理者が auto mode を止める手段として公式に案内されている |

> 上表は運用上よく使うキーに絞っている。公式 [Settings](https://code.claude.com/docs/en/settings) にはこの他に `apiKeyHelper` / `fileSuggestion` / `deniedMcpServers` / `allowAllClaudeAiMcps` / `strictKnownMarketplaces` / `editorMode` / `agentPushNotifEnabled` / `autoScrollEnabled` 等が掲載されている。全キーの網羅は公式に委ね、本ドキュメントは判断に効くキーの解説に集中する。

> **LLM gateway 利用者向けの破壊的変更（v2.1.221）**: Gateway の `model` フィールド検証が厳格化され、**非文字列値は転送されず 400 で拒否**されるようになった。gateway クライアントを自作している場合は、`model` に必ず文字列を渡すよう確認する。出典: CHANGELOG v2.1.221

#### `sandbox` の主要サブフィールド

| サブフィールド | 役割 |
|---|---|
| `sandbox.enabled` | サンドボックスの有効化 |
| `sandbox.allowAppleEvents` | v2.1.181〜。macOS で sandbox コマンドが Apple Events を送信可（opt-in） |
| `sandbox.network.allowDomains` / `denyDomains` / `allowUnixSockets` | ネットワーク隔離のドメイン allowlist / denylist / Unix ソケット許可 |
| **`sandbox.network.strictAllowlist`** | v2.1.219〜。allowlist 外のホストへの接続を**プロンプトなしで拒否**する。既定 `false`。詳細は下記注記 |
| `sandbox.credentials.files` / `envVars` | v2.1.187〜。sandbox 化コマンドが credential file / secret env を読むことをブロック。**v2.1.221 でファイルに `mode: "mask"` が追加**（下記注記） |
| `sandbox.filesystem.disabled` | v2.1.216〜。**filesystem 隔離のみ無効化してネットワーク隔離は維持**する。user / managed / `--settings` のみ設定可で **project / local からは設定不可**。さらに **managed が `sandbox.filesystem` または `credentials.files` を設定している場合は managed のみ**が設定できる。`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` が設定されている場合は全ソース無視 |
| `sandbox.filesystem.allowRead` / `denyRead` | 読み取り許可 / 拒否パス。**両方にマッチする場合はより狭い方が勝つ** |
| `sandbox.autoAllowBashIfSandboxed` | sandbox 化された Bash を自動承認する |
| `sandbox.network.tlsTerminate` | v2.1.199〜（experimental）。credential マスキングの前提となる TLS 終端 |

> **`sandbox.network.strictAllowlist` の 4 つの制約（2026-08-04 に公式掲載を確認）**: ① allowlist の実体は **`allowedDomains` + `WebFetch(domain:...)` allow ルール**（`allowManagedDomainsOnly` 設定時は managed のエントリのみ）② **sandbox 化されたコマンドのみが対象**で、`WebFetch` のような in-process ツールはこの設定でゲートされない ③ **user / managed / CLI `--settings` からのみ有効**で、`.claude/settings.json` / `.claude/settings.local.json` に書いても**無効**（プロジェクト側から egress 制限を緩められないようにするため）④ 既定は `false`。要 v2.1.219+。出典: [Settings](https://code.claude.com/docs/en/settings) / [Sandboxing](https://code.claude.com/docs/en/sandboxing)

> **`sandbox.credentials.files` の `mode: "mask"`（v2.1.221〜）**: 従来 credential ファイルは `deny`（読ませない）しかなかったが、**Linux / WSL では `mask` が選べる**ようになった。sandbox 化コマンドは**センチネル値のコピー**（ファイル全体、または `extract` 正規表現が捕捉したスパンのみ）を読み、**egress 時に sandbox proxy が実値へ置換する**。「トークンの形をしたダミーを読ませて、実際の通信時だけ本物に差し替える」方式である。**macOS ではファイルマスキングは `deny` にフォールバック**する。出典: CHANGELOG v2.1.221

#### `autoMode` の主要サブフィールド

| サブフィールド | 役割 |
|---|---|
| `autoMode.classifyAllShell` | v2.1.193〜。Bash / PowerShell の**全**コマンドを分類器に通す。既定は "arbitrary code execution" パターンのみ。denial reason が transcript / toast / `/permissions` に表示される |
| `autoMode.environment` | 環境の宣言。**`"$defaults"` を含めると組み込みの既定セットを継承**した上で自分の項目を足せる |
| `autoMode.allow` | 分類器に通さず許可するパターン |
| `autoMode.soft_deny` | 拒否するが、Claude が理由を添えて再試行を要求できるパターン |
| `autoMode.hard_deny` | 無条件で拒否するパターン |

#### `workflowSizeGuideline` の受理値

| 値 | Claude が目標にする agent 数 |
|---|---|
| `unrestricted` | 目安なし（Claude がタスクに応じて決める） |
| `small` | 5 体未満 |
| **`medium`（既定）** | 15 体未満 |
| `large` | 50 体未満 |

> **これは cap ではなく「助言」である**: 公式は「Claude Code sends the guideline to Claude as **advice, not a cap**, so a prompt that calls for a different scale still overrides it」と明記している。上限を強制したい場合は runtime 側の agent cap（1 run あたり 1,000 体・同時 16 体）に依存する。
>
> **既定が `medium` になったのは v2.1.219 から**で、それ以前は `unrestricted` が既定だった（size guideline 機能自体は v2.1.202 以降）。また、**自分で guideline を選ぶと `Large workflow` 警告の閾値 25 体がその agent 数に置き換わる**。ultracode 有効時はこの警告が出ない（大規模実行に opt-in 済みとみなされるため）。
>
> ✅ **2026-07-26 時点で本ドキュメントが「公式 docs が CHANGELOG に追従していない」と注記していた不整合は、公式側の追従により解消済み**（公式 [workflows](https://code.claude.com/docs/en/workflows) が「The default is `medium`」と明記）。

### Managed 専用の追加設定 (2026-07 時点)

「managed 側で個人環境の自由度を絞る」ための強化設定。個人開発では通常不要だが、Team/Enterprise 環境で覚えておく。

| フィールド | 役割 |
|-----------|------|
| `allowManagedHooksOnly` | Hooks は managed 定義のみ許可 (ユーザー/プロジェクト定義を無効化) |
| `allowManagedMcpServersOnly` | MCP サーバーは managed 定義のみ許可 |
| `allowManagedPermissionRulesOnly` | permission ルールは managed 定義のみ許可 |
| `sandbox.filesystem.allowManagedReadPathsOnly` | filesystem 読み取り path は managed 定義のみ |
| `sandbox.network.allowManagedDomainsOnly` | ネットワーク接続先は managed 定義のみ |
| `forceRemoteSettingsRefresh` | remote settings の再取得を強制 |
| `blockedMarketplaces` | Plugin marketplace の deny list |
| `pluginTrustMessage` | Plugin 信頼確認時のカスタムメッセージ |
| `wslInheritsWindowsSettings` | WSL 側が Windows 側の managed settings を継承 |

**managed 設定の細目（v2.1.214〜v2.1.219）**

- **`${VAR}` の解決元**（v2.1.219）: managed の MCP allowlist / denylist に書いた `${VAR}` は、**settings ファイル内の env ではなく「起動時の環境変数 + managed-settings の env」から解決される**。settings 側の `env` で定義した変数は使えない。
- **settings-approval prompt の緩和**（v2.1.218）: 無害な feature / cost 系のトグルでは settings 承認プロンプトを出さなくなった。
- **`--settings` のサイズ上限**（v2.1.214）: `--settings` で渡す設定が **2 MiB を超えると起動時エラー**になる。

出典: [Permissions — code.claude.com](https://code.claude.com/docs/en/permissions) / [Settings — code.claude.com](https://code.claude.com/docs/en/settings) / [Corporate launcher — code.claude.com](https://code.claude.com/docs/en/corporate-launcher) / CHANGELOG v2.1.208〜v2.1.219

> 上記は代表例であり、`settings.json` のフィールドは高頻度で増えている。網羅的な一覧は必ず公式 [Settings](https://code.claude.com/docs/en/settings) を参照する。

## Managed（企業管理）設定の配置場所

組織が配布する managed settings は `~/.claude` の外の OS レベルパスに置かれ、ユーザーは上書き・除外できない。

| プラットフォーム | パス | ドロップイン |
|----------------|------|------------|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` | `…/managed-settings.d/` |
| Linux / WSL | `/etc/claude-code/managed-settings.json` | `/etc/claude-code/managed-settings.d/` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` | `…\managed-settings.d\` |

- `managed-settings.d/` 配下の `*.json` はアルファベット順にマージされる（数値プレフィックスでマージ順を制御。配列は連結・重複排除、オブジェクトは deep-merge）。
- **旧 Windows パス** `C:\ProgramData\ClaudeCode\managed-settings.json` は **v2.1.75 で廃止**。`C:\Program Files\ClaudeCode\` へ移行する。
- **Windows の Group Policy / レジストリ配置**: managed 設定は `HKLM\SOFTWARE\Policies\ClaudeCode`（マシン全体の Group Policy）および `HKCU\SOFTWARE\Policies\ClaudeCode`（ユーザー単位）からも読み込まれる。

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
