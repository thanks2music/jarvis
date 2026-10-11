# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) / [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Sandboxing](https://code.claude.com/docs/en/sandboxing) / [Accessibility](https://code.claude.com/docs/en/accessibility) / [Corporate launcher](https://code.claude.com/docs/en/corporate-launcher) / [Workflows](https://code.claude.com/docs/en/workflows) / [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / [Example settings files](https://code.claude.com/docs/en/settings-example) / [Deploy managed settings](https://code.claude.com/docs/en/managed-settings) / [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Fast mode](https://code.claude.com/docs/en/fast-mode) / [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config) / [Auto mode classifier request charges](https://code.claude.com/docs/en/auto-mode-classifier-billing) / [Model configuration](https://code.claude.com/docs/en/model-config) / [Tools reference](https://code.claude.com/docs/en/tools-reference) / [Set up Claude Code (local mode) for a HIPAA-ready organization](https://code.claude.com/docs/en/hipaa-setup) / [Connect Claude Code to Claude for Government](https://claude.com/docs/government/deploy-claude-code/configure) / What's new [2026-w35](https://code.claude.com/docs/en/whats-new/2026-w35)・[2026-w36](https://code.claude.com/docs/en/whats-new/2026-w36)・[2026-w37](https://code.claude.com/docs/en/whats-new/2026-w37) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。CHANGELOG は v2.1.296 まで反映)

ClaudeCode は 6 つの JSON 設定ファイルを階層的に使い分ける。それぞれスコープ（適用範囲）と優先順位が異なり、ユーザー個人の設定・プロジェクト共有の設定・ローカルオーバーライドを分離する設計になっている。さらに Claude Desktop は独自の設定ファイルを 1 つ持つ（計 7 ファイル）。

## 設定ファイル詳細

### 1. `~/.claude.json`（内部管理ファイル）

- **目的**: ClaudeCode の内部状態・認証情報の保存
- **内容**: セッション情報、認証トークンなど ClaudeCode が内部的に管理するデータ
- **保存場所**: ユーザーのホームディレクトリ（`~/.claude.json`）
- **スコープ**: ユーザーレベル（内部管理用）
- **Git 管理**: しない（個人の認証情報を含む）
- **備考**: かつては `allowedTools` や `ignorePatterns` もここに保存されていたが、現在は `settings.json` に移行済み。
- ⚠️ **「直接編集しないファイル」ではなくなった（2026-08-12 訂正）**: 公式 settings ページに **`Global config settings`** 節が新設され、次のキーは **`~/.claude.json` にしか書けない**（`settings.json` に書いても silent に無視される）。公式は「ClaudeCode と `/config` がほとんどを書き込むが、**手で編集してもよい**」と明記している。2026-10-11 時点の [Settings reference](https://code.claude.com/docs/en/settings-reference#global-config-settings) は Global config キーを 12 個載せている（うち 2 個は削除済み）。

  | キー | 内容 |
  |---|---|
  | `autoConnectIde` | 外部ターミナルから起動したとき、実行中の VS Code / JetBrains に自動接続する（既定 `false`） |
  | `autoInstallIdeExtension` | VS Code のターミナルから起動したときの IDE 拡張の自動インストール（`false` で止める） |
  | `claudeInChromeDefaultEnabled` | 対話 CLI と VS Code 拡張でセッション開始時に Chrome 連携を ON にする |
  | `copyFullResponse` | `/copy` が picker を出さずに応答全体をコピーする |
  | `copyOnSelect` | fullscreen 描画と agent view でマウス選択したテキストの自動コピー（`false` で止める） |
  | `defaultToAgentsView` | 引数なしの `claude` で新しい会話ではなく agent view を開く |
  | `diffTool` | 提案された変更を VS Code / JetBrains の diff viewer で開くか、ターミナルに留めるか |
  | `externalEditorContext` | `Ctrl+G` で外部エディタを開いたとき、Claude の直前の応答をコメントとして表示する |
  | `leftArrowOpensAgents` | セッションを background に回して agent view を開く `←` ショートカット（`false` で止める） |
  | `prStatusFooterEnabled` | プロンプトフッターの PR review status バッジと、その裏の PR チェック（`false` で止める） |
  | ~~`permissionExplainerEnabled`~~ | **v2.1.257 で削除**（shell の permission prompt の `Ctrl+E` コマンド説明と一緒に廃止） |
  | ~~`teammateDefaultModel`~~ | **v2.1.234 で削除**（teammate のモデルの決まり方は公式 [Agent teams](https://code.claude.com/docs/en/agent-teams) を参照） |

  なお `disabledMcpServers`（`/mcp` パネルでのトグル結果）も**プロジェクト単位でこのファイルに記録される**（[mcp-setup.md](mcp-setup.md) 参照）。

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
- **Git 管理**: **しない**。⚠️ 除外先は**リポジトリの `.gitignore` ではなく、global git excludes file**（`core.excludesFile`）に `**/.claude/settings.local.json` が追記される（2026-08-12 訂正）。リポジトリ側の `.gitignore` を見ても記載がないのはこのためである。追記は **ClaudeCode がそのリポジトリで初めてこのファイルを書いたとき**（リポジトリがまだ ignore していない場合）だけ行われる。`core.excludesFile` が未設定なら `$XDG_CONFIG_HOME/git/ignore`（未設定時は `~/.config/git/ignore`）が使われる。**手でファイルを作った場合は追記されない**ので、自分で `.gitignore` に足す（2026-10-11 追記。出典: [Settings](https://code.claude.com/docs/en/settings)）
- **備考**: `.claude/settings.json` より優先される
- **workspace trust の挙動 (要注意。2026-10-11 更新)**: 現行の [Permissions](https://code.claude.com/docs/en/permissions#when-your-local-settings-file-needs-trust) によると、ClaudeCode はこのファイルが git 管理外かどうかを git で確かめてから allow rules と `additionalDirectories` を適用する。git の確認はフォルダを trust した後（trust ダイアログを受諾したとき、trust が及ぶ親フォルダを trust 済みのとき、または `-p` / SDK セッション）にしか行わないため、それまでは次のように扱われる。
  - **configuration home**（ホームディレクトリ、または `CLAUDE_CONFIG_DIR` に指定した `.claude` の親）では git を使わずにすぐ適用する
  - **それ以外の場所**では project settings と同じく trust まで保留する。ファイルが git 管理下にある場合や `.claude` が symlink の場合は、リポジトリ由来の設定として trust 後に適用する
  - v2.1.207 より前は、git 管理外のファイルのルールを trust ダイアログの受諾前から適用していた
  - **経緯（v2.1.207 未満の挙動）**: **v2.1.196〜199** では workspace trust が rejected の下で local 設定が **ignored** になり、**v2.1.200 で pre-v2.1.196 挙動に復帰**した（ホームディレクトリや `CLAUDE_CONFIG_DIR` セット時は allow rules 適用）。以前ここに書いていた「現行 (v2.1.200+) では以前通り効く」は、上記の v2.1.207 の変更より前の記述である

### 5. `.mcp.json`（MCP サーバー設定）

- **目的**: プロジェクトで使う MCP サーバーの共有設定
- **内容**: MCP サーバーの定義（コマンド、引数、環境変数）
- **保存場所**: プロジェクトルート `.mcp.json`
- **スコープ**: プロジェクトレベル（`project` スコープの MCP サーバー）
- **Git 管理**: **する**（チームメンバーが同じ MCP ツールを利用できるようにする）
- **備考**: セキュリティ上、プロジェクトスコープの MCP サーバーは**対話セッションでは**使用前に承認プロンプトが表示される（選択のリセットは `claude mcp reset-project-choices`）。**`claude -p`・Agent SDK・cloud セッションではプロンプトを出せないため、確認なしでロードされる**（2026-10-11 訂正: 以前は「初回使用時に承認プロンプトが表示される」とだけ書いていた）。読み込ませたくない場合は `disabledMcpjsonServers` で拒否するか、`--strict-mcp-config` で `--mcp-config` に渡したサーバーだけを使う。リポジトリにコミットされた `enableAllProjectMcpServers` / `enabledMcpjsonServers` は trust していないフォルダでは無視される。出典: [MCP](https://code.claude.com/docs/en/mcp)
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

> **配列型の設定はスコープ横断で「マージ」される（2026-09-03 更新）**: 公式の現在の見出しは「**Lists merge instead of overriding**」であり、マージ対象は permission ルールに限らない。**すべての配列設定が連結 + 重複排除**される。
>
> - **例外は 4 キー**（2026-09-03 更新。以前は「2 つだけ」と記載していたが増えた）:
>   - `fallbackModel` — 優先順位に従って上書き
>   - **`modelPicker`** — managed / `--settings` / user のうち**最上位が全体を供給し、2 ソースを混ぜない**。project / local では無視される
>   - `availableModels` — **managed が定義していればそれを as-is 適用**、非 managed スコープ間では通常どおりマージ
>   - **`modelSettings`** — モデル 1 件ずつ `effortLevel` と併せて解決される
> - `permissions.allow` / `ask` / `deny` は上位スコープが下位を置き換えるのではなく**全スコープのルールが合算**される（その上で deny が allow より強い）。「project の allow を local で消す」ことはできず、消したいなら deny を書く必要がある。
> - **`additionalDirectories` や `allowedHttpHookUrls` のような配列も同様に合算**されるため、「上位スコープで絞ったつもりが下位で足されている」状態になりうる点に注意する。
>
> 2026-08-04 時点では「permission ルールだけがマージされる」と記載していたが、公式の表現が `Permission rules merge across scopes` → `Array settings merge across scopes` → **`Lists merge instead of overriding`**（現行）と 2 度変わり、対象が広がった。出典: [Settings — Lists merge instead of overriding](https://code.claude.com/docs/en/settings#lists-merge-instead-of-overriding)

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

> **`Shift+Tab` のサイクル順（2026-10-11 訂正）**: **`auto` から始めた場合、最初の押下で `default` に移り、以降は `default` → `acceptEdits` → `plan` →（有効なら `bypassPermissions`）→（使えるなら `auto`）の順に巡回する**。任意モードは `plan` の後に入り、**`bypassPermissions` が先、`auto` が最後**である。したがって auto mode が使えるセッションでは `auto` → Manual → accept edits → plan → `auto` と一周する（公式の動画もこの順で戻る）。`dontAsk` はサイクルに入らず、`--permission-mode dontAsk` でのみ設定する。以前は「`auto` はサイクルに戻らない」と書いていたが、現行の [Permission modes](https://code.claude.com/docs/en/permission-modes#switch-permission-modes) とは合わない。

| モード | 確認なしで実行される範囲 | 主な用途 |
|--------|------------------------|----------|
| `default`（**v2.1.200 以降 UI/CLI 表記は「Manual」**、`manual` エイリアスも受理: `claude --permission-mode manual` / `"defaultMode": "manual"`。v2.1.203+ でステータスバーに `⏸ manual mode on` バッジ表示） | 読み取りのみ | 通常作業・センシティブな作業 |
| `acceptEdits` | 読み取り + ファイル編集 + 一般的な filesystem コマンド（`mkdir`/`touch`/`rm`/`rmdir`/`mv`/`cp`/`sed` 等） | レビュー前提でコードを回す |
| `plan` | 読み取り + **auto mode が使える環境では classifier が承認したコマンド**（2026-08-12 訂正。「読み取りのみ」ではない） | 変更前のコードベース調査 |
| `auto` | すべて（バックグラウンドの分類器が安全性を審査） | 長時間タスク・確認疲れの軽減 |
| `dontAsk` | working directories 内のファイル読み取り + 事前承認済みツール（プロンプトが必要なものはすべて自動拒否。2026-10-11 訂正: 以前は「事前承認済みツールのみ」と書いていた） | CI / 制限環境 |
| `bypassPermissions` | すべて（チェックを全バイパス） | ネット遮断したコンテナ / VM 限定 |

- `acceptEdits` が自動承認する filesystem コマンドは `mkdir` / `touch` / `rm` / `rmdir` / `mv` / `cp` / `sed`。`LANG=C` / `NO_COLOR=1` 等の安全な環境変数 prefix 付き、`timeout` / `nice` / `nohup` ラッパー付きも自動承認の対象になる。PowerShell tool 有効時は `Set-Content` 等も含む。
- `bypassPermissions` 以外のすべてのモードで、**保護パス**（`.git`、`.claude`（一部除く）、`.mcp.json`、`.bashrc` 等）への書き込みは自動承認されない。一方 **`bypassPermissions` は v2.1.126 以降、保護パスへの書き込みも prompt せず実行する**（チェックを全バイパスする設計のため）。bypass permissions が使える対話ターミナルの plan mode も同じ扱いになる。
- **critical path の circuit breaker（2026-10-11 訂正）**: `rm` / `rmdir` が critical path を対象にする場合、allow ルールや `PreToolUse` hook の `"allow"` では承認されない（一致する deny ルールはそのまま拒否する）。以前は「`rm -rf /` / `rm -rf ~` のみ」と書いていたが、現行の [Permission modes — Critical paths](https://code.claude.com/docs/en/permission-modes#critical-paths) の範囲はもっと広い。
  - **critical path に当たるもの**: ファイルシステムのルート、ルート直下のディレクトリ（`/usr`・`/etc`・`/data` 等）、ホームディレクトリ、Windows のドライブルートとその直下、working directory とその親。additional working directories とその親は、その下を glob で消す場合（`rm -rf <dir>/*`）だけが対象になる
  - **展開結果が読めない形も対象**: 空になりうるシェル変数の直下の glob（`rm -rf "$DIR"/*`）、`$(pwd)` 等の展開結果だけを対象にした再帰削除なども critical path として扱う
  - **モード別の扱い**: `default` / `acceptEdits` / `plan` は承認を求める。`auto` はターミナルでは制限時間付きで承認を求め、それ以外では拒否する。`dontAsk` は拒否する。`bypassPermissions` も承認を求める（ターミナルでは制限時間付き）。`auto` と `bypassPermissions` の制限時間は 2 分で、応答がなければ拒否される
- `defaultMode` の **`"auto"` と `"bypassPermissions"` は、project / local settings に書いても無視される**（リポジトリが自身に強い権限を付与できないようにするため）。**このとき user settings の `defaultMode` にフォールバックすることもなく、後述の built-in default が使われる**。`"bypassPermissions"` を書いた場合、セッションは **Manual で開始**する。それ以外の値は任意の settings ファイルから有効。
  - ⚠️ **2026-09-03 更新**: 以前は「`"auto"` のみが user scope 限定」と記載していたが、**`"bypassPermissions"` も同じ扱いになった**。公式は「`auto` and `bypassPermissions` don't take effect from project or local settings」「**Before v2.1.257, `bypassPermissions` took effect from any file**」と明記している。
  - VS Code 拡張が開始した会話では、`defaultMode` は **user / managed / `--settings` のみ**から読まれる。
  - 組織側で auto mode を選択させない設定キーは **`permissions.disableAutoMode: "disable"`**（後述）。
- 管理者は managed settings で `permissions.disableAutoMode` / `permissions.disableBypassPermissionsMode` を `"disable"` にして特定モードを禁止できる。`permissions.disableAutoMode` を `"disable"` にすると、**`Shift+Tab` のサイクルから `auto` が消え、`--permission-mode auto`・settings ファイル・built-in default のどれで auto を選んでも、セッションは拒否されずに `default`（Manual）で始まる**。管理者が配信するソースからこの設定が届くと、実行中の auto mode セッションも auto を抜けて `auto mode disabled by settings` を表示する（v2.1.251 以降。それより前は終了まで auto のままだった）。**2026-10-11 訂正**: 以前は「`--permission-mode auto` も起動時に拒否される」と書いていたが、現行 docs は拒否ではなく Manual で起動すると記述している。

### 🔔 auto mode が既定の permission mode になった（2026-08-14 施行、v2.1.283 で全プラン・全プロバイダへ拡大）

**v2.1.283 以降、対話ターミナルと VS Code 拡張の built-in starting mode は、全プラン・全プロバイダで auto mode である**（2026-10-11 更新）。公式 [Permission modes](https://code.claude.com/docs/en/permission-modes) は「With Claude Code v2.1.283 or later, auto mode is the built-in starting permission mode for interactive terminal and VS Code sessions」と記述している。CHANGELOG はこの変更を **2.1.284** の項に載せており 1 版ずれるが、本書は docs の v2.1.283 を採る。

> **経緯（v2.1.283 未満の記述）**: 2026-08-16 の確認時点では、公式は断定形で「**On Pro, Max, and Team plans, the built-in starting mode is auto mode.**」と書いており、auto が既定になるのは Pro / Max / Team（feature flags を取得するセッション）だけだった。2026-08-12 時点までの「Starting August 14, 2026, auto mode becomes the default...」という予告表現は、その時点で既に置き換えられていた。

#### バージョン要件（見落としやすい）

**built-in default が `auto` になるには ClaudeCode 自体のバージョンが条件を満たす必要がある。**

| プラットフォーム | 必要バージョン |
|---|---|
| macOS / Linux / WSL | **v2.1.228 以降** |
| native Windows | **v2.1.233 以降** |

これより古いバージョンでは **built-in default は Manual のまま**である。「2026-08-14 を過ぎたから自動的に auto になる」わけではない。さらに、Pro / Max / Team 以外のプランやプロバイダで auto が既定になるのは **v2.1.283 以降**である。

#### セッションがどのモードで開始するかの決定順序

公式は 3 段階の優先順序を明示している。**先に決まったものが勝つ**。

1. CLI フラグ（`--permission-mode`）
2. `permissions.defaultMode`（設定ファイル）
3. built-in default（プラン・環境から決まる既定）

#### built-in default の決まり方（2026-10-11 更新）

ターミナルまたは VS Code 拡張で始めたセッションは、次の表を**上から順に評価し、最初に一致した行**の開始モードになる（Desktop と claude.ai は別の規則）。

| # | 実行のしかた | built-in の開始モード |
|---|---|---|
| 1 | いずれかの settings ファイルが `disableAutoMode: "disable"` を設定している | `default` |
| 2 | **`claude -p`（print mode）/ Agent SDK** | feature flags を取得するセッションは `default`。取得しないセッション（サードパーティ provider、telemetry off など）は **v2.1.285 以上で `auto`**（それ未満は `default`）。auto 既定を差し控えるポリシーの組織では `default` |
| 3 | HIPAA 構成が適用された組織で、その対象になるセッション（後述「[HIPAA 構成](#hipaa-構成claude-code-local-mode)」） | **v2.1.285 以上で `default`**。auto mode への切替は可能 |
| 4 | ターミナル / VS Code 拡張 | **v2.1.283 以上で `auto`**。それ未満は Pro / Max / Team で feature flags を取得するセッションだけ `auto`、それ以外は `default` |

- インストール / アップグレード直後の最初のセッションは、feature flags が届く前に開始モードを決めることがあり、表と違うモードで始まりうる。
- flag・settings・built-in default が `auto` を選んでも、そのセッションで auto mode が使えない場合（対応外のモデル、settings での無効化、Anthropic がサーバー側で一時的に止めている場合など）は Manual で始まる。
- VS Code 拡張が始める会話は、`claudeCode.initialPermissionMode` → mode indicator で最後に選んだモード → managed settings / `~/.claude/settings.json` の `permissions.defaultMode` → built-in default の順で決まる。project / local settings は読まない。

> **v2.1.283 未満の除外条件（履歴）**: 以前は本節に「built-in default が `auto` にならない除外条件」として 5 行の表を載せていた（① `disableAutoMode: "disable"` ② feature-flag の取得が無効、またはインストール / アップグレード直後の最初のセッション ③ `claude -p` / Agent SDK ④ Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS / apps gateway ⑤ Enterprise プラン、または Claude Console の API キー利用）。これは auto が既定になるのが Pro / Max / Team だけだった v2.1.283 未満の条件であり、現行は上の 4 行に置き換わった。

| 論点 | 内容 |
|---|---|
| **対象** | v2.1.283 以降は**全プラン・全プロバイダ**の対話ターミナルと VS Code 拡張。v2.1.283 未満は **Pro / Max / Team プラン**だけで、Enterprise / Claude API / Claude Platform on AWS / Google Cloud / Microsoft Foundry は opt-in だった（2026-08-16 時点の記述。履歴） |
| **既に既定を設定している場合** | **その設定が維持される**（上記の決定順序で 2 が 3 に優先するため）。Pro / Max / Team と、feature flags を取得しないセッションでは、`~/.claude/settings.json` の `defaultMode` を auto に変えるかを一度だけ尋ねる（後者は CHANGELOG 2.1.285 で追加）。受諾しない限り変わらない |
| **組織が pin している場合** | managed settings の `permissions.defaultMode` で開始モードを固定できる。ターミナルのセッションはそのモードで始まり、利用者は auto に切り替えられる。auto を選べなくするには `permissions.disableAutoMode: "disable"` を使う |
| **classifier の課金** | **classifier の呼び出しが無課金になるのは server-side classifier review が効くセッションだけ**である。server-side review ではサーバーがセッションのモデルリクエストの一部として判定するため、別の classifier 呼び出しが発生しない。gateway / proxy がリクエストや結果を落とす場合や、platform・region・credential が未対応の場合は ClaudeCode 自身の classifier リクエストに戻り、Enterprise / Claude API / Claude Platform on AWS / Bedrock / Google Cloud's Agent Platform / Microsoft Foundry では token 使用量に計上される（その旨の通知が出る。Pro / Max / Team では通知は出ない）。`/status` の **Auto mode server** 行で確認でき、`CLAUDE_CODE_AUTO_MODE_SERVER=0` で ClaudeCode 自身の classifier に固定できる。**2026-10-11 訂正**: 以前は「auto mode の classifier 呼び出しは usage limit に計上されなくなった（適用済み）」と一律に書いていた |
| **auto mode の一時停止** | classifier のブロックが **3 回連続**、またはセッション累計 **20 回**に達すると auto mode を抜けて通常の prompt に戻る。**この閾値は設定できない**。server-side classifier review で verdict が返らない action は実行せず拒否し、10 回連続で返らないとターンを止める |
| **初回通知の文言** | v2.1.228 で「auto mode は少し割高」という初回通知の注記が削除された |

> **実務インパクト（2026-10-11 更新）**: v2.1.283 以降は、プランやプロバイダを問わず対話セッションの既定が auto mode である。**`claude -p` のバッチ実行は環境で分かれる**: feature flags を取得するセッション（Anthropic API に直接つなぎ telemetry を切っていない場合など）は Manual で始まり、取得しないセッション（サードパーティ provider や telemetry off）は v2.1.285 以降 auto で始まる。どの環境でも同じ挙動にしたいなら `--permission-mode` を明示する。`~/.claude/settings.json` で `defaultMode` を明示している場合はその設定が優先されるため、意図した挙動を固定したいなら明示設定を入れておくのが確実である。
>
> 運用設計のベストプラクティス（deny すべき対象、interactive へ戻すべき作業）は [best-practices.md](best-practices.md) を参照。ハーネス（長時間ループ）設計への影響は [harness.md](harness.md) §4.13 を参照。

出典: [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Auto mode classifier request charges](https://code.claude.com/docs/en/auto-mode-classifier-billing) / [Auto mode is now the default in Claude Code](https://claude.com/blog/auto-mode-default-in-claude-code) / CHANGELOG v2.1.284・v2.1.285
- **auto mode の分類器モデルは v2.1.210 以降 Sonnet 5 が既定**（allowlist が Sonnet 5 を許さない場合はセッションモデルまたは Opus にフォールバック）。**Anthropic がサーバー側で設定した classifier モデルがあれば、そちらがこの既定より優先される**（2026-10-11 追記）。セッションの初回リクエストで検証し、以降は pin される。v2.1.216 では OAuth token 期限切れ時に分類器が「HTTP 401」エラーで **deny してしまう不具合**が修正された。
- **server-side classifier review（2026-10-11 追記）**: auto mode の判定を、ClaudeCode 自身の classifier リクエストの代わりにサーバーがセッションのモデルリクエストの一部として行う。Anthropic API 直結の対話ターミナルは Pro / Max / Team で v2.1.271 以上、Enterprise / Claude API で v2.1.278 以上、`-p` / Agent SDK / VS Code / Desktop は v2.1.281 以上。クラウド provider と gateway / proxy 経由は v2.1.278 以上、サインイン済みの Claude apps gateway は v2.1.280 以上。サーバーが review しないセッションは ClaudeCode 自身の classifier に戻り、課金は上表「classifier の課金」のとおり。出典: [Permission modes — Server-side classifier review](https://code.claude.com/docs/en/permission-modes#server-side-classifier-review)
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

#### 1-2. `Read` の deny は `Edit` と `Write` も塞ぐ（Edit は v2.1.208〜、Write は v2.1.228〜）

公式は「A **`Read` deny rule also blocks the Edit and Write tools** on the same path, including creating a new file there」と明記している。つまり `Read(secrets/**)` を deny すると、同じパスへの `Edit` と `Write`（新規ファイル作成を含む）も塞がれる。この確認は Edit には v2.1.208 以上、Write には v2.1.228 以上が必要である。

ただし **`NotebookEdit` はカバーされない**。「どのツールからも変更させたくないパス」には、`Read` deny に加えて **`Edit` deny も明示的に書く**必要がある（`Edit` ルールは全てのファイル編集系ツールをカバーするため）。**2026-10-11 訂正**: 以前は「`Write` と `NotebookEdit` はカバーされない」と書いていたが、現行の [Permissions](https://code.claude.com/docs/en/permissions) で対象外なのは NotebookEdit だけである。

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

**`EndConversation`** は **Claude 側からセッションを終了できる**ツールである。Claude が使うのは、**警告と方向修正を試みた後も続く継続的な abusive input への最終手段**と、**ユーザーがこのツールの実演を明示的に求めて終了を確認した場合**の 2 つだけで、苛立ち・暴言・作業の不調や有害なリクエストは対象にならない（2026-10-11 訂正: 以前は「極端に敵対的な振る舞いや jailbreak の試行に対して」と書いていた）。**他のツールが 1 つでも残っている限り、deny / ask ルールや `disallowedTools` では取り除けない**設計になっている（「全ツール禁止」でなければ常に残る）。通常の開発利用で問題になることはないが、「ツール一覧を完全に固定したい」設計では前提として押さえておく。出典: [Tools reference](https://code.claude.com/docs/en/tools-reference) / CHANGELOG v2.1.214

出典: [Permissions](https://code.claude.com/docs/en/permissions) / CHANGELOG v2.1.210 / v2.1.211 / v2.1.214

## settings.json の主な設定項目

`settings.json`（user / project / local）で指定できる代表的なフィールド。網羅的な一覧は公式 [Settings reference](https://code.claude.com/docs/en/settings-reference) を参照する（2026-10-11 時点で **244 キー**を `Key` / `Description` / `Topic` / `Scope` の 4 列表で網羅している。2026-09-03 時点は 222 キーだった）。

> **2026-09-03: 公式 `settings` ページが全面再編された。** 個別キーの一覧表は `settings` ページから消え、以下 3 本に分割された。本ドキュメントの出典もこれに合わせて張り替えてある。
>
> | ページ | 役割 |
> |---|---|
> | [Settings](https://code.claude.com/docs/en/settings) | 設定ファイルの選び方・変更手順・**precedence**（キー一覧は無い） |
> | [Settings reference](https://code.claude.com/docs/en/settings-reference) | **全キーの網羅リファレンス**（2026-10-11 時点で 244 キー。`~/.claude.json` の global config キーを含む） |
> | [Example settings files](https://code.claude.com/docs/en/settings-example) | 個人 / チーム / 組織 `managed-settings.json` の実例 3 本 |
> | [Deploy managed settings](https://code.claude.com/docs/en/managed-settings) | managed settings の OS 別配信方式・managed source の合成規則 |
>
> あわせて公式は **`Scope` の語彙**を導入した。2026-10-11 時点では `Any file` / `User, local, or managed` / `User or managed` / `User` / `Managed` / `Global config` の **6 種**である（2026-09-03 時点の 5 種に `User` が加わった）。`Any file` は user / project / local / managed の 4 つすべてを指す。本ドキュメントでスコープを書く際はこの語彙に揃える。

| フィールド | 役割 |
|-----------|------|
| `permissions.allow` / `ask` / `deny` | ツール実行の許可・確認・拒否ルール。tool 名に **glob** 可（`"*"` で全拒否、未知 tool 名は起動時に警告）。**`Tool(param:value)`** で組み込みツールの入力のトップレベル・パラメータに一致させられるのは **deny / ask ルールだけ**である（例 `Agent(model:opus)` で Opus サブエージェントをブロック、v2.1.178〜。allow ルールは各ツールの specifier を使う）。対象は `model` / `isolation` / `run_in_background` 等、**1 ルールにつき 1 パラメータ**、`*` wildcard 対応、モデルが省略したパラメータには一致しない。`command` / `file_path` / `path` / `notebook_path` / `url` の**主要入力フィールドは対象外**(無視して startup 警告。`Bash(git *)` 等の specifier を使う)。**MCP ツールのパラメータに一致させるには `--disallowedTools` の deny ルールを使う**。settings ファイルに書いた括弧付きの `mcp__` ルールは読み飛ばされ、対話セッション開始時の invalid-settings ダイアログと `claude doctor` に表示される（2026-10-11 訂正: 以前は param 指定を allow / deny / ask 共通のように書いており、`notebook_path` と MCP の扱いが抜けていた）。tool-name の glob(`mcp__*` 等)は deny / ask で有効。**allow でも `mcp__<server>__` というリテラル接頭辞の後ろに限り glob を使える**が、`"mcp__*"` のようにアンカーのない glob は**警告付きでスキップ**される（2026-08-12 追記）。**`Cd` permission rule**(v2.1.169〜、`/cd` の移動先を制御。bare `Cd` deny で `/cd` 全体無効化、`Cd(path)` で allowlist モード、`//` / `~/` / `/` アンカー + `*` / `**` glob 対応)。**Symlink 挙動明示**: allow rules は symlink path と target の両方一致必要 (fall back to prompt)、deny rules はどちらか一致でブロック |
| `permissions.defaultMode` | 既定のパーミッションモード（前掲の 6 モード） |
| `permissions.disableAutoMode` / `disableBypassPermissionsMode` | `"disable"` で特定モードを禁止（managed 向け） |
| `model` / `availableModels` / `enforceAvailableModels` | 既定モデル / 選択可能モデルの allowlist / allowlist を `/model` の Default にも強制（v2.1.175〜）。**スコープは 3 キーとも `Any file`** で、managed に置いた `availableModels` は `/model`・`--model`・各自のファイルの `model` を制限する。ただし `enforceAvailableModels` は、組織が何らかの managed settings を配布していると managed ソースからだけ読まれる（2026-10-11 訂正: 以前は「managed・policy のみ有効」と書いていた）。**`availableModels` のモデル ID は既定で前方一致**し、`"claude-opus-5"` は Opus 5.5 も許可する。版ごとに絞るには managed 専用の **`availableModelsMatch: "exact"`** と **`deniedModels`**（どちらも v2.1.283〜）を使う（下記「v2.1.259〜v2.1.296 で追加された設定キー」参照）。フル model ID 例: `claude-opus-5-5`・`claude-sonnet-5-5`・`claude-haiku-5-5`・`claude-opus-5`・`claude-opus-4-8`・`claude-fable-5-1`・`claude-sonnet-5`（**Opus 5.5 は要 v2.1.280+、Sonnet 5.5 は要 v2.1.284+、Haiku 5.5 は v2.1.293+ で使う**、Opus 5 は要 v2.1.219+、Fable 5 は要 v2.1.170+、Sonnet 5 は要 v2.1.197+）。**v2.1.187 / v2.1.196 で強化**: managed で `/model` ピッカー・`--model`・`ANTHROPIC_MODEL` 環境変数の 3 経路すべてを制限可能。`/model` UI に "Org default" / "Role default" ラベル表示 |
| `fallbackModel` | プライマリが過負荷・不在のとき順次試す代替モデル（最大 3 つ、CLI は `--fallback-model`、v2.1.168〜） |
| `modelOverrides` | Anthropic のモデル ID を**プロバイダ固有の ID**（Bedrock の inference profile ARN、Google Cloud's Agent Platform の version 名、Microsoft Foundry の deployment など）に対応付ける。model picker の各項目はプロバイダ API の呼び出しにこの値を使う。スコープ `Any file`。**2026-10-11 訂正**: 以前は「サブエージェント種別ごとのモデル上書き」と書いていたが誤りだった。出典: [Model configuration — Override model IDs per version](https://code.claude.com/docs/en/model-config#override-model-ids-per-version) |
| **`modelSettings`** | **v2.1.251〜。`/effort` や `/model` の effort スライダーを操作すると、`effortLevel` ではなくこのキーの `modelSettings.<model>.effortLevel` に保存される**（「Before v2.1.251, `/effort` wrote this key」）。**effort はモデルごとに保存され、モデルを切り替えても旧モデルの値は引き継がれない**。同一ファイル内では `modelSettings` が `effortLevel` に勝ち、ファイル横断では「そのモデルのエントリか `effortLevel` を設定した最上位ファイル」が決める。`/effort auto` で当該モデルの保存値をクリアできる。**各モデルのエントリには `effortLevel` のほか、`maxEffortLevel`（そのモデルだけの effort 上限、v2.1.267〜）と `autoCompactWindow`（`100000`〜`1000000` トークンまたは `"auto"`。`/autocompact` が保存し、同じファイルのトップレベル `autoCompactWindow` より優先、v2.1.288〜）も置ける**（2026-10-11 追記） |
| `effortLevel` | レベルを保存していないモデルの既定 effort（`low`/`medium`/`high`/`xhigh`。`max` は session-only のため不可。`ultracode` は v2.1.284 以降 effort レベルではなく独立したトグルで、常時 ON にするには `ultracode: true` を使う）。**v2.1.251 以降、`/effort` はこのキーを書き換えず `modelSettings` に保存する**。effort の解決順は ①明示指定（`CLAUDE_CODE_EFFORT_LEVEL` / `--effort` / `/effort`）→ ②設定（モデル別の保存値 or 本キー）→ ③モデル既定（effort 対応モデルは `high`。**ただし Opus 5.5 / Sonnet 5.5 / Haiku 5.5 は `medium`**、Opus 4.7 は `xhigh`、組織が organization default model に既定 effort を設定していればその値）の 3 段である。**user settings（`~/.claude/settings.json`）直下の本キーは旧形式で、Opus 5・Fable 5.1 とそれ以前のモデルにだけ効き、Opus 5.5 以降のモデルには効かない**（project / local / managed / `--settings` の本キーは全モデルに効く）。`-p` / Agent SDK / remote worker 接続セッションでは `/effort` はそのセッション限り。**2026-10-11 訂正**: 以前は解決順を「明示 → model-default hold（Fable 5 / Opus 4.8 / Opus 4.7 のみ）→ 設定 → モデル既定（effort 対応モデルは一律 `high`、例外は Opus 4.7 の `xhigh`）」の 4 段で書いていた。hold は現行 docs の解決順に無い（v2.1.280 未満の挙動。[best-practices.md](best-practices.md) §8 参照） |
| `maxEffortLevel` | **v2.1.267〜**（2026-10-11 追記）。セッションが使える effort の**上限**を設定する（`"low"`〜`"max"`。`"max"` は上限なし、既定は未設定）。`/effort`・`/model` picker・`--effort`・`CLAUDE_CODE_EFFORT_LEVEL`・skill / subagent の `effort` frontmatter・モデル既定のどれで上限を超えても上限で動く。ClaudeCode がリクエスト前に自分で適用するため、Bedrock / Google Cloud's Agent Platform / Microsoft Foundry を含む全プロバイダで効く。スコープ `Any file`。複数スコープが設定すると**最も低い値**が効き、別スコープから引き上げられない。モデル別の上限は `modelSettings.<model>.maxEffortLevel`（同じ settings ソース内では本キーより優先し、`"max"` でそのソースの上限から外せる）。組織の effort limit とも併用され、低い方が効く |
| `alwaysThinkingEnabled` | **`false` にして全セッションの extended thinking を切る**ためのキー（thinking は既定で ON なので `true` は何も変えない）。Opus 5.5 / Sonnet 5.5 / Haiku 5.5 / Fable 系のように常に思考するモデルでは `false` も効かない。サードパーティ provider では `thinking` パラメータを省くだけなので、adaptive reasoning のモデルは思考しうる。`MAX_THINKING_TOKENS` がセッション単位で本キーより優先する。**2026-10-11 訂正**: 以前は「extended thinking を既定で有効化」と書いていた |
| `outputStyle` / `statusLine` | 出力スタイル / カスタムステータスライン |
| `agent` | メインスレッドを名前付き subagent として起動 |
| `hooks` | ライフサイクルイベントの Hooks 定義 |
| `env` | 環境変数。⚠️ **project / local settings の `env` は一部の変数を落として警告する**（下記「`env` で設定できない変数」参照）。Fable 関連の変数として `ANTHROPIC_DEFAULT_FABLE_MODEL`（`fable` エイリアスの解決先 model id。未設定なら Fable 5.1）・`DISABLE_PROMPT_CACHING_FABLE`（Fable 系モデル全般のプロンプトキャッシュ無効化）がある（2026-10-11 更新: 以前は「Fable 5 のデフォルト model id 上書き」「Fable 5 のプロンプトキャッシュ無効化」と書いていた。[best-practices.md](best-practices.md) 参照）。**追加された環境変数(2026-07 時点)**: `CLAUDE_CLIENT_PRESENCE_FILE`(v2.1.181、指定ファイル存在中は mobile push 抑制)、`CLAUDE_CODE_DISABLE_MOUSE_CLICKS`(v2.1.195、フルスクリーンのクリック/ドラッグ/ホバー無効化、ホイールは維持)、`CLAUDE_ENABLE_STREAM_WATCHDOG`(v2.1.197、5 分無音で中断・再試行、デフォルト有効。`=0` で無効化)、`CLAUDE_CODE_DISABLE_ARTIFACT`(Artifacts の無効化)、`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(v2.1.187、remote MCP tool call の 5 分 idle timeout 調整)、`OTEL_LOG_ASSISTANT_RESPONSES`(v2.1.193、**セキュリティ注意**: 未設定時は `OTEL_LOG_USER_PROMPTS` を継承するため、既にプロンプトログを取っている環境は upgrade 時にアシスタント応答も自動で流れ始める。抑止するには明示的に `=0` を設定)、**`CLAUDE_AFK_TIMEOUT_MS`**(v2.1.198、idle 時に `AskUserQuestion` を自動継続。settings の `askUserQuestionTimeout` と対応)、**`CLAUDE_AFK_COUNTDOWN_MS`**(v2.1.198、自動継続前のカウントダウン開始、既定 20000ms)、**`CLAUDE_CODE_BRIDGE_SESSION_ID`**(v2.1.199、Remote Control 接続中に自動設定)、**`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS`**(v2.1.198、組み込み Explore / Plan subagent のみ無効化)、**`CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`**(v2.1.196、supervisor 停止時のバックグラウンド handoff 停止)、**`API_FORCE_IDLE_TIMEOUT`**(v2.1.169、5 分 idle timeout の上書き)、**`ANTHROPIC_FOUNDRY_AUTH_TOKEN`**(v2.1.203、Microsoft Foundry Bearer token 認証)。**追加された環境変数(v2.1.208〜v2.1.219)**: **`CLAUDE_CODE_PROCESS_WRAPPER`**(v2.1.208、企業ランチャー経由で自己 spawn プロセスを起動。Windows では無視。agent teams の tmux / iTerm2 ペインと Remote Control worker は v2.1.210 以降でカバー)、~~`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`~~(v2.1.212 追加 → **v2.1.224 で撤廃され no-op**。per-session の spawn 数上限は現在存在しない)、**`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`**(v2.1.217、既定 20、ultracode は免除)、**`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`**(v2.1.217、nested subagent の階層数)、**`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`**(v2.1.212、既定 200)、**`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`**(v2.1.212、2 分超の MCP tool call を自動バックグラウンド化する閾値。`0` で無効化)、**`CLAUDE_CODE_FORWARD_SUBAGENT_TEXT`**(v2.1.211、stream-json に subagent の text / thinking を含める。CLI は `--forward-subagent-text`)、**`CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`**(v2.1.214、OTel content 属性の切り詰め上限。既定 60KB)、**`CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD`**(v2.1.208、Bedrock streaming の content-type チェックをスキップ)、**`CLAUDE_AX_SCREEN_READER`**(screen reader mode。CLI は `--ax-screen-reader`)、**`CLAUDE_CODE_RESUME_INTERRUPTED_TURN`**(v2.1.211、中断ターンの自動再開。**v2.1.221 で `=0` による無効化が効かない不具合が修正**され、falsy 値が尊重されるようになった。関連: `CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS`)、**`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`**(Bash / hooks / MCP stdio の子プロセスから Anthropic・クラウド認証情報を除去。Linux では PID namespace 分離も伴い `ps` / `pgrep` / `kill` が host プロセスを見られなくなる。関連: `CLAUDE_CODE_SCRIPT_CAPS`)、**`DISABLE_EXTRA_USAGE_COMMAND`**(`/usage-credits` の無効化)。**廃止**: `CLAUDE_CODE_CONNECT_TIMEOUT_MS`(v2.1.186 で削除) |
| `askUserQuestionTimeout` | **v2.1.200〜**。`AskUserQuestion` の無応答時に自動継続するタイムアウト。値は `"60s"` / `"5m"` / **`"10m"`** / `"never"` (既定 `"never"`)。**project / local からは読まれず user-level のみ**。環境変数 `CLAUDE_AFK_TIMEOUT_MS` / `CLAUDE_AFK_COUNTDOWN_MS` と併用 |
| `cleanupPeriodDays` | **v2.1.203〜**。セッションファイル (transcript) の保持日数。**既定 30 日・最小 1**。削除は**起動時**に実行される。※ 2026-08-04 時点で書いていた「orphaned worktree の自動削除間隔」「parse 失敗時に pause」は現行公式に記載がないため削除した ([session-history.md](session-history.md) 参照) |
| `axScreenReader` | screen reader mode（視覚的 TUI を装飾なしの線形テキストに置換し、VoiceOver / NVDA で読める形にする）を有効にする。classic renderer を使うため `tui` 設定は無効化される。CLI `--ax-screen-reader` と環境変数 `CLAUDE_AX_SCREEN_READER` が優先。**版数は公式ソース間で食い違う**: [CLI reference](https://code.claude.com/docs/en/cli-reference) は `--ax-screen-reader` の要件を **v2.1.181 以上**とし、CHANGELOG は screen reader mode の追加を **2.1.208** の項に載せている（2026-10-11 訂正: 以前は「設定キー自体は v2.1.181〜、機能そのものは v2.1.208 で追加」と断定していた）。v2.1.210 / 214 / 217 / 218 で読み上げ改善（permission mode 変更のアナウンス、削除テキストのアナウンス等）。出典: [Accessibility](https://code.claude.com/docs/en/accessibility) |
| `autoMemoryEnabled` / `autoMemoryDirectory` | Auto Memory の有効化 / 保存先（[memory.md](memory.md) 参照） |
| `skillOverrides` / `skillListingMaxDescChars` / `skillListingBudgetFraction` | Skills の可視性・description キャップ（既定 1536 文字）・予算（[skills.md](skills.md) 参照）。⚠️ **2026-08-12 訂正: 正しいキー名は `skillListingMaxDescChars` であり `maxSkillDescriptionChars` は存在しない**（公式全文で 0 ヒット） |
| `sandbox` | Bash サンドボックスの設定。主要サブフィールドは下表を参照 |
| `extraKnownMarketplaces` | 追加 Plugin marketplace（[plugins.md](plugins.md) 参照） |
| `claudeMd` / `claudeMdExcludes` | managed CLAUDE.md 本文 / 読み込み除外パターン |
| `autoMode` / `useAutoModeDuringPlan` | auto mode の挙動カスタマイズ / plan mode 中の auto 利用。主要サブフィールドは下表を参照。**v2.1.218 の挙動変更**: `useAutoModeDuringPlan` 有効時、plan mode でも**静的解析で read-only と証明できない Bash はプロンプトを出さず分類器が裁定する**ようになった。同 version で dangerous-`rm` / background-`&` / suspicious-Windows-path の各チェックも permission dialog を開かず分類器裁定に変わっている |
| `permissions.additionalDirectories` | セッション開始時から作業対象に含める追加ディレクトリ。⚠️ **`/add-dir` の「設定版」ではない。** 公式は「grant **file access only** and don't load any of the configuration」と明記しており、**ファイルアクセスのみを与え、設定を一切読み込まない**。`.claude/skills/` / `.claude/commands/` / `.claude/agents/` / `enabledPlugins` + `extraKnownMarketplaces` の読み込みは **`--add-dir` / `/add-dir`（および Agent SDK の該当オプション）限定の例外**である。`CLAUDE.md` の読み込みには別途 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` が必要 |
| `allowedHttpHookUrls` | `type: "http"` の Hooks が POST できる URL の allowlist |
| `disableAgentView` / `disableSkillShellExecution` | agent view の無効化 / skill からのシェル実行の禁止 |
| `fileCheckpointingEnabled` | ファイル変更のチェックポイント（`/rewind` の巻き戻し対象）の有効化 |
| `showClearContextOnPlanAccept` | plan 承認時に「コンテキストをクリアするか」の選択を表示する |
| `includeGitInstructions` | システムプロンプトへの git 操作指示の同梱を制御 |
| `respondToBashCommands` | Shell mode `!` の自動応答トグル(v2.1.186〜)。デフォルト `true`(コマンド出力を Claude が読んで応答)。`false` で従来の「context 追加のみ」に戻す |
| `disableSideloadFlags` | managed 専用(v2.1.193): `--plugin-dir` / `--plugin-url` / `--agents` / `--mcp-config` などの sideload 系フラグをブロック |
| `disableClaudeAiConnectors` | ClaudeCode が自分で取得する claude.ai connectors を、取得も接続もしない。スコープは **`Any file`** で、**どのファイルの `true` も効く**（リポジトリの `.claude/settings.json` でそのリポジトリだけ opt out できるが、project の `false` で user / managed の `true` は覆せない）。`ENABLE_CLAUDEAI_MCP_SERVERS=false` でもセッション単位で切れる。`--mcp-config` で明示したサーバーは対象外。**2026-10-11 訂正**: 以前は「managed 専用(v2.1.182)」と書いていたが、現行 docs のスコープは `Any file` で、版数の記載も無い |
| `enableArtifact` | Artifacts の利用を制御するキー（導入版は現行の公式 docs と CHANGELOG で確認できないため記載しない。2026-10-11 更新: 以前は「v2.1.196〜」と書いていた）。スコープは **`Any file`**。**「どのファイルからも OFF にでき、どのファイルからも ON に戻せない」ロック型**である（v2.1.242 より前は上位スコープが下位の `true` を上書きできた）。`/config` の Artifacts 行を OFF にすると本キーが user settings に書かれ、`disableArtifact` はクリアされる |
| ~~`disableArtifact`~~ | **deprecated**（`enableArtifact` を使う）。`disableArtifact: true` は `enableArtifact: false` と等価として今も尊重されるが、**`disableArtifact: false` は無視される**。スコープは `Any file` |
| `disableAllHooks` | 全 Hooks の無効化（managed hooks は managed 側でのみ無効化可、[hooks.md](hooks.md) 参照） |
| `workflowKeywordTriggerEnabled` / `disableWorkflows` / `enableWorkflows` / `ultracode` | dynamic workflows のキーワードトリガ（`false` で `ultracode` と打っても起動しない）/ 設定が届く全員向けの無効化（managed なら組織全体。`CLAUDE_CODE_DISABLE_WORKFLOWS=1` も同等）/ **自分だけの ON・OFF**（2026-10-11 追記。`/config` の **Dynamic workflows** 行が user settings に書く。未設定時は ON で、Pro プランだけ OFF）/ ultracode の既定 ON（v2.1.157〜）。`enableWorkflows: true` は `disableWorkflows` や組織のポリシーが止めている間は効かない。**`ultracode: true` は v2.1.284 以降 effort を変えず**、セッションの effort のまま ultracode が動く（v2.1.284 未満は `xhigh` で動き、`xhigh` 未満の effort 上限があると OFF のままだった）。ClaudeCode はこのキーを読むだけで書かない（`/effort ultracode` はセッション限り） |
| `parentSettingsBehavior` | **埋め込みホスト（Agent SDK・IDE 拡張・Claude Desktop など）が渡す managed settings（parent settings）を、管理者配信の managed tier があるときに適用するか**（v2.1.133〜）。`"first-wins"`（既定）はホストの設定を捨て、`"merge"` は restrictive な値だけを admin tier の下に適用する。スコープは **`Managed`**（最上位の admin ソースから読む）。admin tier が無いときは、ホストの設定が restrictive な値に絞られたうえで唯一の managed tier になる。**2026-10-11 訂正**: 以前は「上位スコープ設定の継承挙動」と書いていた |
| `policyHelper` | **起動時に managed settings を算出する実行ファイル**を指定する（`path` / `timeoutMs` / `refreshIntervalMs`）。端末の状態・ID・リモートサービスから policy を導くための仕組みで、helper が出力する `managedSettings` がそのセッションの唯一の managed ソースになる。スコープは **`Managed`**（macOS plist / Windows HKLM / managed settings ファイルから読み、server-managed・HKCU・parent settings では無視）。起動時の実行が失敗すると ClaudeCode は起動を拒否する。server-managed settings が起動時に policy を届けた場合は helper は動かない。**2026-10-11 訂正**: 以前は「パーミッション判定を委譲する外部ヘルパー」と書いていた |
| `defaultShell` | **入力欄で `!` を付けて打つシェルコマンド**を Bash と PowerShell のどちらで実行するか（`"bash"` / `"powershell"`。既定 `"bash"`、Bash が無い Windows では `"powershell"`）。`"powershell"` は PowerShell tool が有効なときだけ効き、指定したシェルが無いともう一方を使う。**2026-10-11 訂正**: 以前は「Bash ツールが使う既定シェル」と書いていた |
| `autoUpdatesChannel` | 自動更新チャンネルの選択 |
| `teammateMode` | Agent teams の動作モード。`"iterm2"`(v2.1.186)を指定すると iTerm2 統合を有効化(`it2` CLI が無いと警告) |
| `plansDirectory` | plan mode の計画ファイル保存先 |
| `requiredMinimumVersion` / `requiredMaximumVersion` | 許可する ClaudeCode バージョン範囲（managed 向け、v2.1.163〜） |
| `disableRemoteControl` | `/remote-control` の無効化 |
| `strictPluginOnlyCustomization` | カスタマイズを Plugin 経由に限定する（v2.1.202 以降は array 指定対応で、対象カテゴリを細かく列挙できる） |
| `advisorModel` | `/advisor`（第 2 モデル相談ツール）が使うモデル（v2.1.98〜） |
| `attribution` | commit / PR の署名（Co-Authored-By 等）のカスタマイズ。スコープは **`Any file`**、型は object、既定は unset。**サブキーは 3 つ**: `commit`（string、git trailer）/ `pr`（string、PR 本文のプレーンテキスト）/ `sessionUrl`（Boolean、v2.1.183。web / Remote Control セッションが commit / PR に添える claude.ai セッションリンクを省略できる）。**署名を全部消すには `commit` と `pr` を空文字列にし、`sessionUrl: false` を設定する**（本リポジトリ `CLAUDE.md` の「AI 署名を付けない」運用を settings で担保する場合はこの形）。**`attribution.commit` か `attribution.pr` のいずれかを設定した時点で `includeCoAuthoredBy` は無視される** |
| ~~`includeCoAuthoredBy`~~ | **v2.0.62 で deprecated**（`attribution` を使う）。スコープ `Any file`、型 Boolean、**既定 `true`**。上記のとおり `attribution.commit` / `attribution.pr` のどちらかが設定されると無視される |
| `subagentStatusLine` | サブエージェント用のステータスライン。**v2.1.214 以降、payload に reasoning effort が含まれる**（subagent ごとの effort を表示できる） |
| `footerLinksRegexes` | フッター行に正規表現マッチのリンクバッジを追加（v2.1.176〜） |
| `language` | **Claude の応答言語**を既定で英語以外にする（v2.1.176〜。値はそのまま「常にその言語で応答せよ」という指示として渡り、検証されない。例 `"japanese"`）。同じ値が音声入力の言語と自動生成のセッションタイトルの言語にも使われる（未設定時のタイトルは会話の言語）。スコープ `Any file`。**2026-10-11 訂正**: 以前は「セッションタイトルの言語を固定」と書いていた |
| `disableBundledSkills` | バンドルスキル・workflows・組込コマンドをモデルから隠す（env `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` でも可） |
| `workflowSizeGuideline` | dynamic workflows (ultracode) が 1 セッションで spawn する agent 数の目安を制御する。**既定は `medium`、Pro プランでサインインしている場合は v2.1.271 以降 `small`**。受理値は 4 種（下表）。任意の settings ファイルから設定可で、**設定されている間は `/config` の該当行が非表示**になる（settings の値が `/config` より優先）。実行中の workflow の `Running in background` 行に、効いている size が表示される（2026-10-11 訂正: 以前は「status line に表示」と書いていた）。関連 OpenTelemetry 属性: `workflow.run_id` / `workflow.name`（v2.1.202〜）。詳細は下記の注記を参照 |
| `emojiCompletionEnabled` | **v2.1.217〜**。`:shortcode:` 形式での絵文字補完（既定 `true`）。**v2.1.221 以降は `:thumbsup:` / `:thumbsdown:` / `:love:` 等の別名 shortcode も受理**する |
| `vimInsertModeRemaps` | **v2.1.208〜**。vim editor mode の INSERT モードで、2 文字の入力列を **Escape** に割り当てる（例: `jj` → `"<Esc>"`）。割り当て先は **`"<Esc>"` だけ**で、それ以外のエントリは無視される。`editorMode` が `"vim"` でないと効かない。スコープは **`User or managed`**（リポジトリからは変えられない）。**2026-10-11 訂正**: 以前は「2 キー列を別キーにリマップする」と書いていた |
| `processWrapper` | **v2.1.210〜**（環境変数版 `CLAUDE_CODE_PROCESS_WRAPPER` は v2.1.208）。企業ランチャー経由で ClaudeCode の自己 spawn プロセスを起動する。**project / local からは設定不可**。詳細は [Corporate launcher](https://code.claude.com/docs/en/corporate-launcher) |
| `crossSessionInbound` | **v2.1.224〜**。cross-session messaging の受信ポリシー（`accept` / `hold` / `refuse`）。**既定は送受信双方の permission mode クラスから自動決定**され、bypass 側が受け手になる場合は `hold`。**v2.1.232〜 `/config` に「Messages from your other sessions」行として表示**され（user settings に書き込む）、managed / `--settings` がキーを設定中は非表示。⚠️ **`/config crossSessionInbound=value` のショートハンドはこのキーに限り拒否される**。[sub-agents.md](sub-agents.md) 参照 |
| `dialogExpiry` | **v2.1.224〜**。保留中ダイアログの有効期限。**既定 `"5m"`**（2026-08-16 訂正。従来 `"10m"` と記載していたが誤り）。受理値は `"60s"` / `"5m"` / `"10m"` / `"never"`。**`-p`（print mode）セッションにも適用**される。**user / managed / `--settings` からのみ読まれる**。環境変数 `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS` で上書き可。**v2.1.232〜 `/config` に「Dialog expiry」行として表示**され（user settings に書き込む）、managed / `--settings` がキーを設定中は非表示 |
| `isolatePeerMachines` | **v2.1.224〜**。`true` でマシンをまたぐ `SendMessage` に毎回承認を要求する。**`bypassPermissions` 下でも承認を求め、どのスコープの `true` も有効**（安全側に倒す設計） |
| `worktree.baseRef` / `symlinkDirectories` / `sparsePaths` / `bgIsolation` | worktree 生成時の基点 ref・symlink するディレクトリ・sparse checkout 対象・background セッションの隔離可否 |
| `disableAutoMode` | `"disable"` で auto mode を封鎖する（`Shift+Tab` のサイクルから除去し、`--permission-mode auto`・settings・built-in default のどれで auto を選んでも `default` で開始させる）。スコープは `Any file` で、`permissions.disableAutoMode` としても受理される。利用者が覆せない managed settings で使うのが主な用途。Bedrock / Google Cloud / Microsoft Foundry 環境で管理者が auto mode を止める手段として公式に案内されている。**2026-10-11 訂正**: 以前は「`--permission-mode auto` も拒否」と書いていた |

> 上表は運用上よく使うキーに絞っている。公式 [Settings reference](https://code.claude.com/docs/en/settings-reference) にはこの他に `apiKeyHelper` / `fileSuggestion` / `deniedMcpServers` / `allowAllClaudeAiMcps` / `strictKnownMarketplaces` / `editorMode` / `agentPushNotifEnabled` / `autoScrollEnabled` / `switchModelsOnFlag` / `showThinkingSummaries` / `autoCompactEnabled` / `autoCompactWindow` / `respectGitignore` / `prUrlTemplate` / `syncClaudeAiSkills` / `allowedMcpServers` / `channelsEnabled` / `voice` / `policyHelper` / `managedSourcesBehavior` / `processWrapper` / `otelHeadersHelper` 等、2026-10-11 時点で計 **244 キー**が掲載されている（2026-09-03 時点は 222 キー）。全キーの網羅は公式に委ね、本ドキュメントは判断に効くキーの解説に集中する。

> **v2.1.222〜v2.1.233 の設定・挙動変更（2026-08-12 初出 / 2026-08-16 に v2.1.233 まで延長。履歴として保存）**
>
> ⚠️ **v2.1.234〜v2.1.258 の変更は上記「v2.1.234〜v2.1.258 で追加された設定キー」「`env` で設定できない変数」「新しい環境変数」「制限モード」の各節にある**（2026-09-03 追記）。本表は当時の記録として残している。
>
> | 変更 | 内容 | 版 |
> |---|---|---|
> | **Remote Control 自動接続の制限** | `remoteControlAtStartup` は **user / managed でのみ有効化できる**。project / local からは **OFF 方向にしか設定できない**（リポジトリ同梱の設定で勝手にリモート接続を開かせないため） | v2.1.222 |
> | **`CLAUDE_CODE_DISABLE_1M_CONTEXT` の意味変更** | 固定のモデルリストではなく、**ネイティブ 1M context を持つ全モデル**を 200K へ抑制する。抑制できていない場合は起動時に警告 | v2.1.223 |
> | **未知 model の auto-compact** | 未知の model ID のセッションも想定コンテキスト内に auto-compact される。旧挙動へ戻すには `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` | v2.1.223 |
> | **marketplace の owner ワイルドカード** | `strictKnownMarketplaces` / `blockedMarketplaces` が `"owner/*"` 形式を受理し、**GitHub org 単位で一括許可 / 遮断**できる | v2.1.223 |
> | **`ANTHROPIC_BEDROCK_REGION_PREFIX`** | Bedrock の cross-region inference profile を明示指定する環境変数 | v2.1.224 |
> | **`CLAUDE_CODE_MESSAGING_SOCKET`** | cross-session messaging のセッション固有 inbox socket のパス。**SessionStart より前**から hook / Bash に export される | v2.1.224 |
> | **gateway の spend limit** | 独立表示だった gateway の spend limit が **usage warning に統合**された | v2.1.225 |
> | **auto mode の `SendMessage` 審査** | 他セッション／teammate への `SendMessage` の**送信内容を送信前に permission classifier が評価**するようになった | v2.1.222 |
> | **auto mode の連続ブロック計上** | safety-filter による拒否が「連続ブロック上限」に計上されてしまうバグを修正（auto mode が不当に早く解除されていた） | v2.1.225 |
> | **Write tool のルール緩和** | **新世代モデルは未 Read のファイルを `Write` で上書きできる**ようになった（`Edit` と同ルール）。旧世代モデルは従来どおり Read 必須 | v2.1.228 |
> | **ネスト git リポジトリの trust 継承廃止** | **子リポジトリが親リポジトリの trust を継承しなくなった**。各リポジトリで個別に trust 確認が要る（セキュリティ修正） | v2.1.232 |
> | **`sandbox.ripgrep` のスコープ制限** | **user / managed / `--settings` からのみ読まれる**ようになり、project から上書きできなくなった。`bwrapPath` / `socatPath` / `ripgrep` の server-managed 上書きは managed の承認が必須 | v2.1.232 |
> | **`CLAUDE_CODE_FORK_SUBAGENT`** | subagent の fork mode を上書きする環境変数。**対話セッションでは既定 ON になったため、この変数は「常時 ON (`1`)／常時 OFF (`0`)」の上書き専用**（[sub-agents.md](sub-agents.md) 参照） | v2.1.232 |
> | **`CLAUDE_CODE_ENABLE_TODO_TOOLS`** | 新世代モデルで既定除外された task-tracking ツール群を**入れる**（`=1`、起動前に export）。**現役の変数である**。別軸の **`CLAUDE_CODE_ENABLE_TASKS`**（ツールがあるセッション内で Task 4 種と旧 `TodoWrite` のどちらを使うかを選ぶ。既定 Task 4 種、`=0` で `TodoWrite`）と共存する。詳細は [sub-agents.md](sub-agents.md) の「Task / Todo ツールのモデル別提供状況」を参照 | v2.1.233 |
> | **`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`** | fan-out 時に**同一 prefix の兄弟エージェントを待たせて prompt cache を再利用**させる。**固定の待機時間ではなく「待つ上限」**（先頭 1 体の first response が始まるのを待つ上限、既定 **`5000`** ミリ秒）。`0` で無効化、`DISABLE_PROMPT_CACHING` 設定時は待たない（[harness.md](harness.md) 参照） | v2.1.229 |
> | **`CLAUDE_CODE_TOOL_MEMORY_LIMIT`** | Linux の memory cgroup で **Bash tool のメモリ使用量を制限**する opt-in。暴走ビルドによるセッション停止を防ぐ | v2.1.233 |
> | **`CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS`** | WebFetch のセッション内 URL キャッシュ TTL。**既定 15 分** | v2.1.233 |
> | **`additionalMarketplaces` / `allowedMarketplaces`** | `extraKnownMarketplaces` / `strictKnownMarketplaces` の **friendlier alias** として受理されるようになった（既存キー名も有効） | v2.1.232 |
> | **Windows のパス検証バイパス修正** | NT の `\??\` device prefix が UNC path 検証を回避できた問題を修正（**NTLM credential leak の経路**だった） | v2.1.233 |
> | **権限バイパス 3 件の修正** | PowerShell の `$PSDefaultParameterValues` 上書き / Linux filesystem sandbox の protected-path 回避 / cross-session messaging の socket ディレクトリ（`/tmp`）に事前配置された symlink を拒否 | v2.1.232 |
>
> ⚠️ **v2.1.233 で revert された 2 件**: v2.1.232 で入った「Bash 入力リダイレクト `< file` の権限チェック」と「Git Bash の Cygwin 形式 symlink 追跡」は、**v2.1.233 で取り消された**（後日より狭い形で再投入予定）。v2.1.232 だけを見て挙動を前提にしないこと。
>
> ※ **2026-09-03 更新**: 上表は 2026-08-16 時点で「docs 未掲載・CHANGELOG のみが一次情報」としていたが、**4 件すべて公式 docs に掲載された**ため注記を外した。`CLAUDE_CODE_TOOL_MEMORY_LIMIT` と `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` は [Environment variables](https://code.claude.com/docs/en/env-vars) に、`additionalMarketplaces` / `allowedMarketplaces` は [Settings reference の Marketplace key aliases](https://code.claude.com/docs/en/settings-reference#marketplace-key-aliases) に「v2.1.232 以降 `extraKnownMarketplaces` / `strictKnownMarketplaces` の別名として受理され、ファイル更新時に正式名へ書き換えられることがある」と明記されている。

> **LLM gateway 利用者向けの破壊的変更（v2.1.221）**: Gateway の `model` フィールド検証が厳格化され、**非文字列値は転送されず 400 で拒否**されるようになった。gateway クライアントを自作している場合は、`model` に必ず文字列を渡すよう確認する。出典: CHANGELOG v2.1.221

#### `sandbox` の主要サブフィールド

| サブフィールド | 役割 |
|---|---|
| `sandbox.enabled` | サンドボックスの有効化 |
| `sandbox.allowAppleEvents` | v2.1.181〜。macOS で sandbox コマンドが Apple Events を送信可（opt-in） |
| `sandbox.network.allowedDomains` / `deniedDomains` / `allowUnixSockets` | ネットワーク隔離のドメイン allowlist / denylist / Unix ソケット許可（2026-08-12 訂正: 正しいキー名は `allowedDomains` / `deniedDomains` であり、`allowDomains` / `denyDomains` ではない） |
| **`sandbox.network.strictAllowlist`** | v2.1.219〜。allowlist 外のホストへの接続を**プロンプトなしで拒否**する。既定 `false`。詳細は下記注記 |
| `sandbox.credentials.files` / `envVars` | v2.1.187〜。sandbox 化コマンドが credential file / secret env を読むことをブロック。**v2.1.221 でファイルに `mode: "mask"` が追加**（下記注記） |
| `sandbox.filesystem.disabled` | v2.1.216〜。**filesystem 隔離のみ無効化してネットワーク隔離は維持**する。user / managed / `--settings` のみ設定可で **project / local からは設定不可**。さらに **managed が `sandbox.filesystem` または `credentials.files` を設定している場合は managed のみ**が設定できる。`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` が設定されている場合は全ソース無視 |
| `sandbox.filesystem.allowRead` / `denyRead` | 読み取り許可 / 拒否パス。**両方にマッチする場合はより狭い方が勝つ** |
| `sandbox.autoAllowBashIfSandboxed` | sandbox 化された Bash を自動承認する |
| `sandbox.network.tlsTerminate` | v2.1.199〜（experimental）。credential マスキングの前提となる TLS 終端 |

> ⚠️ **2026-09-03 訂正**: 以前は「admin 側のマスタースイッチは別キーの `disableArtifact` である」と記載していたが**誤り**だった。`disableArtifact` は **deprecated** で、admin 専用のマスタースイッチではない（両キーともスコープは `Any file`）。
>
> **`sandbox.network.strictAllowlist` の 4 つの制約（2026-08-04 に公式掲載を確認）**: ① allowlist の実体は **`allowedDomains` + `WebFetch(domain:...)` allow ルール**（`allowManagedDomainsOnly` 設定時は managed のエントリのみ）② **sandbox 化されたコマンドのみが対象**で、`WebFetch` のような in-process ツールはこの設定でゲートされない ③ **user / managed / CLI `--settings` からのみ有効**で、`.claude/settings.json` / `.claude/settings.local.json` に書いても**無効**（プロジェクト側から egress 制限を緩められないようにするため）④ 既定は `false`。要 v2.1.219+。出典: [Settings reference — sandbox.network.strictAllowlist](https://code.claude.com/docs/en/settings-reference#sandbox-network-strictallowlist) / [Sandboxing](https://code.claude.com/docs/en/sandboxing)

> **`sandbox.credentials.files` の `mode: "mask"`（v2.1.221〜）**: 従来 credential ファイルは `deny`（読ませない）しかなかったが、**Linux / WSL では `mask` が選べる**ようになった。sandbox 化コマンドは**センチネル値のコピー**（ファイル全体、または `extract` 正規表現が捕捉したスパンのみ）を読み、**egress 時に sandbox proxy が実値へ置換する**。「トークンの形をしたダミーを読ませて、実際の通信時だけ本物に差し替える」方式である。**macOS ではファイルマスキングは `deny` にフォールバック**する。出典: CHANGELOG v2.1.221
>
> **v2.1.224 でマスキングが大幅に拡張された**:
>
> | 追加項目 | 内容 |
> |---|---|
> | `onExtractNoMatch` | `extract` 正規表現がマッチしなかった場合の挙動を指定する |
> | `decode: "jwt"` + `maskClaims` | JWT をデコードし、**指定した claim だけをマスクする** |
> | `awsPairs` | AWS のアクセスキー ID / シークレットのペアを対応付けてマスクする |
> | `sigv4` | egress 時に **SigV4 で再署名**する（マスク値のまま署名すると壊れるため） |
>
> いずれも **`sandbox.network.tlsTerminate` が必須**で、**user / managed / `--settings` からのみ設定できる**（project / local からは設定不可）。出典: CHANGELOG v2.1.224
>
> **セキュリティ修正（v2.1.224）**: `sandbox.filesystem.denyRead` 等の deny エントリを **末尾スラッシュ付き**（例 `denyRead: "~/.aws/"`）で書くと、Linux / macOS で**その deny が無効化される**問題が修正された。過去に末尾スラッシュで書いていた場合、**実際には保護されていなかった**可能性があるため設定を確認する。

#### `autoMode` の主要サブフィールド

| サブフィールド | 役割 |
|---|---|
| `autoMode.classifyAllShell` | v2.1.193〜。Bash / PowerShell の**全**コマンドを分類器に通す。既定は "arbitrary code execution" パターンのみ。denial reason が transcript / toast / `/permissions` に表示される |
| `autoMode.environment` | 環境の宣言（信頼するリポジトリ・バケット・ドメインなど）。**`"$defaults"` を含めると組み込みの既定セットを継承**した上で自分の項目を足せる |
| `autoMode.allow` | 分類器が `soft_deny` の**例外として許可する**ルール（分類器を素通りさせるものではない） |
| `autoMode.soft_deny` | 分類器がブロックするルール。`allow` の例外と、ユーザーのメッセージが当該操作を直接・具体的に指示している場合は上書きされる |
| `autoMode.hard_deny` | 分類器が無条件でブロックするルール（ユーザーの意図も `allow` の例外も効かない） |

> **2026-10-11 訂正**: `environment` / `allow` / `soft_deny` / `hard_deny` は**分類器に渡す自然言語（prose）のルールの配列**であり、正規表現やツールパターンではない。分類器は `hard_deny` → `soft_deny` → `allow`（`soft_deny` の例外）→ ユーザーの明示的な意図の順に評価する。以前は `allow` を「分類器に通さず許可するパターン」、`soft_deny` を「Claude が理由を添えて再試行を要求できるパターン」と書いていたが、どちらも誤りだった。分類器より前に効くツールパターンの拒否は `permissions.deny` で書く。`"$defaults"` を含めずに配列を設定するとその節の組み込みルールは全部置き換わり、配列はスコープ横断で連結される。スコープは `User or managed`。v2.1.246 以降は `/permissions` の **Auto mode** タブからも編集できる。出典: [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config) / [Settings reference — autoMode](https://code.claude.com/docs/en/settings-reference#automode)

#### `workflowSizeGuideline` の受理値

| 値 | Claude が目標にする agent 数 |
|---|---|
| `unrestricted` | 目安なし（Claude がタスクに応じて決める） |
| `small` | 5 体未満（**Pro プランでサインインしている場合は v2.1.271 以降これが既定**） |
| **`medium`（既定）** | **10 体未満** |
| `large` | 50 体未満 |

> **2026-10-11 更新**: v2.1.219 の導入時は `medium` が「15 体未満」だったが、v2.1.271 で 10 体未満に引き下げられた（[CHANGELOG](https://code.claude.com/docs/en/changelog) 2.1.271）。現行の [Workflows](https://code.claude.com/docs/en/workflows#set-a-size-guideline) と [Settings reference](https://code.claude.com/docs/en/settings-reference#workflowsizeguideline) はどちらも「fewer than 10 agents」としている。
>
> **これは cap ではなく「助言」である**: 公式は「Claude Code sends the guideline to Claude as **advice, not a cap**, so a prompt that calls for a different scale still overrides it」と明記している。上限を強制したい場合は runtime 側の agent cap に依存する（2026-10-11 更新）。
>
> | runtime の上限 | 内容 |
> |---|---|
> | agent 総数 | 1 run あたり 1,000 体 |
> | 同時実行数 | 既定 16 体。CPU が少ない環境（CPU 制限付きコンテナを含む）ではそれより少ない。`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`（`1`〜`256`、v2.1.269〜）で変更できる |
> | 1 回の `parallel()` / `pipeline()` | 4,096 items まで（超えるとエラーで拒否） |
>
> **既定が `medium` になったのは v2.1.219 から**で、それ以前は `unrestricted` が既定だった（size guideline 機能自体は v2.1.202 以降）。また、**自分で guideline を選ぶと `Large workflow` 警告の閾値 25 体がその agent 数に置き換わる**。ultracode 有効時はこの警告が出ない（大規模実行に opt-in 済みとみなされるため）。`Large workflow` 警告は、agent 数が 25 体を超えたときのほか、**予測トークン総数が 150 万を超えたとき**にも出る（2026-10-11 追記。警告は助言で、run を止めない）。
>
> **その他の workflow の挙動（2026-10-11 追記）**:
>
> - **usage limit で一時停止**: agent が claude.ai の usage limit に達すると、run は失敗せず一時停止し、リセット後に自動で再開する（v2.1.271〜。`autoContinueAtUsageLimit` が ON であることなどが条件。それより前は該当 agent が失敗した）
> - **無効化の手段**: `/config` の **Dynamic workflows** 行を OFF、`"disableWorkflows": true`、`CLAUDE_CODE_DISABLE_WORKFLOWS=1` のいずれか。無効化中は `/workflows`・workflow コマンド・`/workflow-authoring` skill が使えず、`ultracode` キーワードも起動しない
> - **`/workflow-authoring`**: 保存した workflow の `.js` を編集する前に読み込む、スクリプト記述リファレンスの bundled skill（v2.1.248〜）
>
> ✅ **2026-07-26 時点で本ドキュメントが「公式 docs が CHANGELOG に追従していない」と注記していた不整合は、公式側の追従により解消済み**（公式 [workflows](https://code.claude.com/docs/en/workflows) が「The default is `medium`」と明記）。

### Managed 専用の追加設定 (2026-07 時点、2026-10-11 追記)

「managed 側で個人環境の自由度を絞る」ための強化設定。個人開発では通常不要だが、Team/Enterprise 環境で覚えておく。公式 [Deploy managed settings — Keys only a managed source can set](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) は、ここに無いキーが managed 専用かどうかは Settings reference の `Scope` 列（`Managed`）で確かめるよう案内している。

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
| **`managedMcpServers`** | **v2.1.259〜**（2026-10-11 追記）。remote（`http` / `sse`、`https://` 必須）の MCP サーバーを全利用者に**提供**する。利用者が自分で追加したサーバーはそのまま残り、提供されたサーバーは利用者が編集・削除できない。何かを封鎖するキーではない。サードパーティ構成の Claude Desktop の Code タブと Cowork では読まれない |
| **`managedSourcesBehavior`** | 複数の managed ソースがあるとき、最上位の 1 つだけを使う `"first-wins"`（既定）か、全 admin ソースを合成する `"merge"`（v2.1.242〜）か（下記「Managed（企業管理）設定の配置場所」参照） |
| **`disableCommandPluginSources`** | `true` で marketplace が宣言したコマンドを実行してインストールする `command` 形式の plugin source を全面的に封鎖する |
| **`pluginSuggestionMarketplaces`** | `/plugin` で plugin のインストール提案を出してよい marketplace を選ぶ |
| **`channelsEnabled`** | 組織で channels を許可する |
| **`allowedChannelPlugins`** | メッセージを push できる channel plugin の allowlist（設定すると Anthropic の既定 allowlist を置き換える。`channelsEnabled: true` が前提） |

> mods（関数 hook を持つ plugin）向けの managed キー（`allowManagedModsOnly` など）は [mods.md](mods.md) を参照。モデル制限の `deniedModels` / `availableModelsMatch`、プロバイダ制限の `allowedProviders` も `Managed` スコープで、下記「v2.1.259〜v2.1.296 で追加された設定キー」にまとめた。

**managed 設定の細目（v2.1.214〜v2.1.219）**

- **`${VAR}` の解決元**（v2.1.219）: managed の MCP allowlist / denylist に書いた `${VAR}` は、**settings ファイル内の env ではなく「起動時の環境変数 + managed-settings の env」から解決される**。settings 側の `env` で定義した変数は使えない。
- **settings-approval prompt の緩和**（v2.1.218）: 無害な feature / cost 系のトグルでは settings 承認プロンプトを出さなくなった。
- **`--settings` のサイズ上限**（v2.1.214）: `--settings` で渡す設定が **2 MiB を超えると起動時エラー**になる。

出典: [Permissions — code.claude.com](https://code.claude.com/docs/en/permissions) / [Settings reference — code.claude.com](https://code.claude.com/docs/en/settings-reference) / [Corporate launcher — code.claude.com](https://code.claude.com/docs/en/corporate-launcher) / CHANGELOG v2.1.208〜v2.1.219

> 上記は代表例であり、`settings.json` のフィールドは高頻度で増えている。網羅的な一覧は必ず公式 [Settings reference](https://code.claude.com/docs/en/settings-reference) を参照する。

### v2.1.234〜v2.1.258 で追加された設定キー

| キー | 内容 | 版 / スコープ |
|---|---|---|
| **`modelSettings`** | モデル別の effort 保存先（上表参照） | v2.1.251 / `Any file` |
| **`modelPicker`** | `/model` picker を順序付き・ラベル付きリストでキュレートする。`options[]` + `replaceBuiltInOptions`。任意の ID 表記（Vertex / Bedrock 形式を含む）を指定でき、組み込みラインナップへの追加または置換ができる | v2.1.242 / **`User or managed`**（project / local では無視） |
| **`promptCacheTtl`** / **`subagentPromptCacheTtl`** | prompt cache の TTL。受理値は `"5m"` / `"1h"`。「本会話は 1 時間キャッシュ、subagent は 5 分」といった分離ができる。優先順位は `FORCE_PROMPT_CACHING_5M` > `CLAUDE_CODE_PROMPT_CACHE_TTL` > 本キー > `ENABLE_PROMPT_CACHING_1H` | v2.1.242 / `Any file` |
| **`modelPricing`** | 組織の契約単価・割引率を、list price の代わりにコスト表示へ反映する。反映先は `/usage`（`/cost` はその alias）・statusline・Agent SDK の `total_cost_usd`・`--max-budget-usd` の上限判定・OpenTelemetry のコスト metric / event（2026-10-11 更新）。`multiplier` + `overrides`。`multiplier` を 1 超（最大 10）にする値上げは v2.1.271 以降 | v2.1.242 / **`Managed` のみ**（`--settings` でも HKCU でも設定不可） |
| ~~**`keybindingFlavor`**~~ | **v2.1.261 で deprecated になり、効果は無い**（2026-10-11 訂正）。v2.1.238〜v2.1.260 では `"readline"` にすると `Ctrl+W` が直前の空白まで削除になった。現行はプロンプトの単語編集キーが常に readline 準拠で、`Ctrl+W` は直前の空白まで、`Alt+B` / `Alt+F` / `Alt+D` は `/` や `.` も単語の区切りとして扱う。キー自体は受理されるので、設定ファイルに残っていてもエラーにはならない。以前は「既定 `"classic"` は不変」と書いていた | v2.1.238（v2.1.261 で deprecated）/ `Any file` |
| **`timeFormat`** | ターン終了時刻・transcript タイムスタンプの表示形式。受理値は `"auto"` / `"12-hour"` / `"24-hour"` / `"24-hour-utc"`。`/config` の **Time format** 行 | v2.1.257 |
| **`timeZone`** | IANA タイムゾーン名。`timeFormat` が `"24-hour-utc"` のときは無視される。`/config` に行は無い | v2.1.257 |
| **`spellcheck`** | プロンプト入力のスペルミスに下線を引く。インストール済みの `aspell` / `hunspell` / `ispell` を使う | v2.1.235 |
| **`feedbackDrafts`** | Claude が下書きするフィードバック（`SendFeedback` ツール。`/feedback` でレビュー・送信する）の扱い。`"notify"`（既定。下書きをキューに入れるとカードを表示）/ `"quiet"`（カードを出さずフッターに件数だけ表示）/ `"off"`（`SendFeedback` ツールを外す）の 3 値。`/config` の **Claude-drafted feedback** 行が user settings に書き、project / local では無視される。`CLAUDE_CODE_SEND_FEEDBACK=0` でセッション単位で切れる。**2026-10-11 訂正**: 以前は「`SendFeedback` ツールの無効化」とだけ書いていた | v2.1.247 / **`User or managed`** |
| **`fastMode`** / **`fastModePerSessionOptIn`** | fast mode（research preview）の制御。**Opus を最大 2.5x 高速化するが、トークン単価は上昇する**。**対応は Opus 5.5 / Opus 5 / Opus 4.8**（Sonnet / Haiku は非対応。他のモデルで ON にすると Opus に切り替わる）。単価は Opus 5.5 が $8 / $40、Opus 5 と Opus 4.8 が $10 / $50（per MTok）。fast mode の既定モデルは v2.1.280 以降 Opus 5.5。`/fast` でトグル。Opus 4.7 向けは 2026-06-25 deprecated → 2026-07-24 削除。**2026-10-11 訂正**: 以前は「対応は Opus 5 / Opus 4.8 のみ」と書いていた。詳細は公式 [Fast mode](https://code.claude.com/docs/en/fast-mode) | — |
| **`switchModelsOnFlag`** | safety classifier が flag したとき fallback へ自動切替するか。`true` は自動切替、`false` は対話セッションでは一時停止して選ばせ、`-p` ではエラー終了する。**既定は未設定**で、自動切替するが対話セッションでは先に確認することがある。`/config` の **Switch models when a message is flagged** 行。**2026-10-11 訂正**: 以前は「既定 `true`」と書いていた | — / `Any file` |
| **`desktopSessionCleanupPeriodDays`** | Desktop / Cowork transcript 専用の保持期間。**キーが無ければ Desktop / Cowork の transcript は年齢に関係なく保持される**（v2.1.248 未満は `cleanupPeriodDays` で削除）。設定すると **`cleanupPeriodDays` との AND 判定**になるため、既定 30 日環境で `7` を入れても 30 日保持になる。本キーが無視され `cleanupPeriodDays` で削除されるのは、managed settings が `cleanupPeriodDays` を設定している場合と、HIPAA 構成がセッションに適用されている場合の 2 つ。`--settings` で渡したファイルからも読む（2026-10-11 更新） | v2.1.248 / **`User or managed`** |
| **`experimental.cacheTtl`**（agent frontmatter） | `"5m"` / `"1h"`。subagent の TTL 設定が無いときに使う per-agent prompt cache TTL。**トップレベルではなく `experimental` マップ配下に置く必要がある** | v2.1.248 |
| sandbox 系サブキー | `sandbox.failIfUnavailable` / `excludedCommands` / `allowUnsandboxedCommands` / `filesystem.allowWrite` / `denyWrite` / `allowManagedReadPathsOnly` / `ignoreViolations` / `enableWeakerNestedSandbox` / `enableWeakerNetworkIsolation` / `network.allowAllUnixSockets` / `allowLocalBinding` / `allowMachLookup` / `httpProxyPort` / `socksProxyPort` / `credentials.sigv4` / `allowPlaintextInject` | — |

> ⚠️ **版数の注意**: `modelPicker` / `promptCacheTtl` / `subagentPromptCacheTtl` / `modelPricing` は CHANGELOG では v2.1.243 として告知されたが、**公式 `settings-reference` は 4 件すべて一貫して `Requires Claude Code v2.1.242 or later` と記載している**。CHANGELOG は掲載バージョンに欠番があり網羅的でないため、**版数は公式 docs を優先する**。
>
> **`permissions.blockReadsOutsideWorkingDirectories`**（v2.1.257〜）は、現行の [Settings reference](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories) と [Permission modes](https://code.claude.com/docs/en/permission-modes) に掲載された。ON の間は working directories 外の読み取りをファイルツールが拒否し、認識できる読み取り系 Bash コマンドは auto mode と `bypassPermissions` mode でもプロンプトを出す。OFF の間は、auto mode で Read / Grep / Glob が working directories 外を初めて読むときに 1 回だけ確認が出て、「今後はブロックする」を選ぶと user settings に `true` が書かれる。**2026-10-11 更新**: 以前は「CHANGELOG v2.1.257 だけが一次情報で、docs の追従待ち」と書いていた。

### v2.1.259〜v2.1.296 で追加された設定キー

2026-10-11 追記。版数は [Settings reference](https://code.claude.com/docs/en/settings-reference) の `Requires Claude Code vX or later` に従う。

| キー | 内容 | 版 / スコープ |
|---|---|---|
| **`maxEffortLevel`** | effort の上限（前掲の表を参照） | v2.1.267 / `Any file` |
| **`modelSettings.<model>.maxEffortLevel`** / **`autoCompactWindow`** | モデル別の effort 上限 / auto-compact window（前掲 `modelSettings` 行を参照） | v2.1.267 / v2.1.288、`Any file` |
| **`availableModelsMatch`** | `availableModels` のモデル ID の一致方式。`"prefix"`（既定。`"claude-opus-5"` が Opus 5.5 も許可する）/ `"exact"`（記載した版だけを許可。dated ID は含む。`"opus"` のような family alias は family 全体を許可し、`best` / `opusplan` / `default` は無視）。`"exact"` では Default の選択肢も一覧のモデルに限られる | v2.1.283 / `Managed`（他のスコープと `--settings` では警告付きで無視） |
| **`deniedModels`** | 特定のモデルを、`availableModels` が許可していても封鎖する（`/model` picker から隠し、Default でも走らせない）。`"opus"` は family 全体、`"claude-opus-5-5"` はその版のあらゆる表記（dated・provider 固有 ID を含む）、マイナー版なしの `"claude-opus-5"` は Opus 5.5 も封鎖する（Opus 5 だけを封鎖するなら `"claude-opus-5-0"`） | v2.1.283 / `Managed`（同上） |
| **`enableWorkflows`** | dynamic workflows の自分用 ON / OFF（前掲の表を参照） | — / `Any file` |
| **`bashOutputMaxChars`** | 成功した Bash / PowerShell コマンドの出力を Claude がインラインで受け取る上限文字数。超えた出力はファイルに保存され、Claude はプレビューとパスを受け取る。`4000`〜`128000` に丸められ、未設定時は 30,000 文字。設定すると `BASH_MAX_OUTPUT_LENGTH` は無視される | v2.1.261 / `Any file` |
| ~~**`taskOutputMaxChars`**~~ | background task の出力を `TaskOutput` ツールで読むときのインライン上限。v2.1.261 で `bashOutputMaxChars` と同時に追加された（What's new 2026-w36 も両方を紹介している）が、**v2.1.277 で `TaskOutput` ツールとともに削除**され、現行では効果が無い（Claude は background task の出力ファイルを `Read` で読む） | v2.1.261〜v2.1.276 / `Any file` |
| **`managedMcpServers`** | 全利用者に remote MCP サーバーを提供する（前掲「Managed 専用の追加設定」を参照） | v2.1.259 / `Managed` |
| **`allowedProviders`** | その端末が使ってよい API provider の一覧（`"anthropic"` / `"bedrock"` / `"vertex"` / `"foundry"` / `"anthropicAws"` / `"mantle"` / `"customEndpoint"` / `"gateway"`）。一覧に無い provider のセッションは、起動時・ログイン時・次の API 呼び出し時に拒否される。端末側の admin ソースが設定した一覧は server-managed settings の一覧と両方が効き、server-managed 側は絞ることはできても広げられない。HIPAA 構成の推奨 managed settings にも含まれる（後述） | v2.1.285 / `Managed` |

**W35〜W37 の設定まわりの変更（v2.1.243〜v2.1.268 を含む。2026-10-11 追記）**

- **`/login` の Console account サインイン**: `/login` の **Anthropic Console account** に **Sign in with your Console account** が加わった。API キーを作らずにサインインする方式で、API キーを許可しない Console 組織のメンバーもサインインできる（CHANGELOG 2.1.243。What's new 2026-w35）。`forceLoginMethod` を `"claudeai"` / `"console"` にすると、その設定が効くセッションではこの keyless サインインは提示されない。
- **サードパーティ provider での機能解禁**: Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry と telemetry off のセッションでも、同じマシン上のセッション同士の cross-session messaging（v2.1.248）と、`/loop` が自分で間隔を選ぶモード（v2.1.248）が使えるようになった。`/model` と `/effort`（CHANGELOG では `/fast` も）は、ターンの終了を待たずに即時反映されるようになった（v2.1.243）。出典: What's new 2026-w35 / [Cross-session messaging — Availability](https://code.claude.com/docs/en/cross-session-messaging#availability) / CHANGELOG 2.1.243・2.1.248
- **WebFetch の 5 分 deadline**: WebFetch は、redirect を含めてページのダウンロードが 5 分以内に終わらないと deadline エラーで失敗する（以前は応答を開いたまま終わらないサーバーで無期限に止まっていた）。`CLAUDE_CODE_WEBFETCH_DEADLINE_MS`（既定 `300000`、`0` で無制限、v2.1.268〜）で変更できる。出典: [Tools reference — WebFetch tool behavior](https://code.claude.com/docs/en/tools-reference#webfetch-tool-behavior) / What's new 2026-w37

### `env` で設定できない変数（project / local settings）

**project / local settings の `env` は「チェックアウトしたリポジトリが制御すべきでない変数」を落として警告する**（`claude --debug` で確認できる）。2026-10-11 時点の [Settings reference — Variables Claude Code ignores in env](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env) は対象を 7 分類に広げ、一部に版数を付けている（2026-09-03 時点の記述は「版数を明示せず 3 分類」だった）。

| 分類 | 変数 |
|---|---|
| 自身のファイル出力先を変える系 | `CLAUDE_CONFIG_DIR` / `CLAUDE_CODE_TMPDIR` / `HOME` / `TMPDIR` / `TMP` / `TEMP` / `XDG_*` |
| セッション内容を外部送出する系 | `OTEL_LOG_RAW_API_BODIES` / `ENABLE_BETA_TRACING_DETAILED` / `BETA_TRACING_ENDPOINT` |
| 起動・同期を変える系 | `CLAUDE_CODE_PROCESS_WRAPPER` / `CLAUDE_CODE_SYNC_SKILLS` / `CLAUDE_CODE_SYNC_PLUGINS` / `CLAUDE_CODE_PLUGIN_CACHE_DIR` / `CLAUDE_CODE_PLUGIN_SEED_DIR` |
| Windows のプログラム・マシン全体の設定を選ぶ系 | `SystemRoot` / `ComSpec` / `ProgramData` / `LOCALAPPDATA` / `PATHEXT` / `PSModulePath` / `ProgramFiles` 系 |
| telemetry を ON にする・送り先や取得内容を決める OpenTelemetry 系（v2.1.282〜） | `CLAUDE_CODE_ENABLE_TELEMETRY` / enhanced telemetry beta の 2 変数 / `OTEL_LOGS_EXPORTER`・`OTEL_METRICS_EXPORTER`・`OTEL_TRACES_EXPORTER` / `OTEL_LOG_USER_PROMPTS`・`OTEL_LOG_ASSISTANT_RESPONSES`・`OTEL_LOG_TOOL_CONTENT`・`OTEL_LOG_TOOL_DETAILS` / `OTEL_EXPORTER_OTLP_*` の endpoint・headers・protocol・証明書系 / `OTEL_EXPORTER_PROMETHEUS_HOST`・`_PORT`。ただし 3 つの exporter selector の `none` と、`OTEL_LOG_USER_PROMPTS`・`OTEL_LOG_TOOL_CONTENT`・`OTEL_LOG_TOOL_DETAILS` の `0` などの off 値という、**telemetry を切る値だけは適用される** |
| 未応答ダイアログのタイマー系・添付処理（v2.1.290〜） | `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS` / `CLAUDE_AFK_TIMEOUT_MS` / `CLAUDE_AFK_COUNTDOWN_MS` / `CLAUDE_CODE_DISABLE_ATTACHMENTS` |

ファイル出力先を変える系とセッション内容を外部送出する系は、v2.1.251 より前は project / local からも設定できた（`HOME` と `XDG_CONFIG_HOME` を除く）。また `CLAUDE_CODE_PROJECT_DIR_NAME` / `CLAUDE_CODE_RESTRICTED` / `CLAUDE_CODE_MESSAGING_SOCKET`・`_TOKEN` などの起動環境専用の変数は、どの settings ファイルからも無視される。

これらは shell / user / managed settings で設定する。`env` の適用タイミングもソース別に規定されている — user / `--settings` / managed は**起動時と保存時**、project / local は **workspace trust 後または `-p` 起動時**、`/cd` 後（v2.1.246〜）は移動先の値を上乗せする。

### 新しい環境変数（v2.1.234〜v2.1.258）

| 変数 | 内容 | 版 |
|---|---|---|
| **`ANTHROPIC_DEFAULT_MODEL`** | 新規セッションの開始モデルを指定する。**`--model`・`ANTHROPIC_MODEL`・いずれかの settings ファイルの `model`（`/model` で保存した選択を含む）・organization default model のどれもモデルを決めていないときだけ使われる**。`/model` で保存した選択は以後の起動でもこの変数に勝つ（`ANTHROPIC_MODEL` は起動のたびにその値へ戻る点が異なる）。`default` / `inherit` / `opusplan` / `haiku` を指定した場合や `enforceAvailableModels` が ON の場合などは無視される。**2026-10-11 訂正**: 以前は「`/model` の選択を上書きし、再起動後も保持される」と書いていたが、現行の [Model configuration](https://code.claude.com/docs/en/model-config#set-a-default-model-for-new-sessions) の記述とは逆だった | v2.1.236 |
| **`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`** | `=1` で agent 定義の `model:` と per-spawn の明示指定を**すべて無視**し、全 subagent（組み込みの Explore / Plan を含む）に強制適用する | v2.1.257 |
| **`CLAUDE_CODE_PROJECT_DIR_NAME`** | `CLAUDE_CONFIG_DIR` と併用して per-project transcript ディレクトリ名を固定する（1〜64 文字の英数字・ハイフン・アンダースコア）。**`CLAUDE_CONFIG_DIR` 未設定時は無視され、起動シェルの環境からのみ読まれる**（settings の `env` ブロックは不可） | v2.1.234 |
| **`CLAUDE_CODE_GOAL_CHECKIN_MINUTES`** | `/goal` の background task チェックイン間隔。`0` でオプトアウト | v2.1.234〜239 |
| **`CLAUDE_CODE_RESTRICTED`** | `=1` で制限モード（下記） | v2.1.248 |
| **`SELF_HOSTED_RUNNER_CLIENT_LABEL`** | self-hosted runner の登録ラベル上書き（既定は hostname） | v2.1.248 |
| **`CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY`** | `=1` で、`ANTHROPIC_BASE_URL` が Anthropic 互換の gateway（LiteLLM・Kong・社内 proxy など）を指すとき、**gateway の `/v1/models` から `/model` picker の項目を取得する**。共有 API キーの gateway で全員に全モデルが見えるのを避けるため既定は OFF（CHANGELOG によると 2.1.126〜2.1.128 は自動で、2.1.129 から opt-in）。取得したモデルにも `availableModels` が効く。v2.1.257 で gateway が返す `description` を picker に表示できるようになり（無い項目は "From gateway"）、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 設定時も動作するよう変更された。**2026-10-11 訂正**: 以前は変数の役割を「`description` を出せるようにする」と書いていたが、それは v2.1.257 の追加分である | v2.1.129（v2.1.257 で拡張） |
| **`CLAUDE_CODE_ENABLE_TASKS`** | `=0` で `TaskCreate` / `TaskGet` / `TaskList` / `TaskUpdate` の代わりに旧 `TodoWrite` を使う。**現行は Task 4 種が既定で、`TodoWrite` は既定で無効** | — |

### 制限モード（`--restricted` / `CLAUDE_CODE_RESTRICTED=1`）

**v2.1.248〜。** 信頼できないリポジトリを触るときや、CI で権限を絞りたいときに使う。

1. コマンド・コードを実行する組み込みツールと `WebFetch` を**削除**する（`--tools` で個別に明示した場合のみ復活。`default` プリセット経由では復活しない）
2. 組み込みファイルツールを **working directories 内に限定**する
3. **managed settings と `--settings` のみ読み、user / project / local settings を無視**する
4. `bypassPermissions` を拒否する
5. cloud session の作成を拒否する

⚠️ 環境変数版は **settings ファイルの `env` ブロックからは無視され、launch 環境からのみ読まれる**。

出典: [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [Settings reference](https://code.claude.com/docs/en/settings-reference)

## Managed（企業管理）設定の配置場所

組織が配布する managed settings は `~/.claude` の外の OS レベルパスに置かれ、ユーザーは上書き・除外できない。

| プラットフォーム | パス | ドロップイン |
|----------------|------|------------|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` | `…/managed-settings.d/` |
| Linux / WSL | `/etc/claude-code/managed-settings.json` | `/etc/claude-code/managed-settings.d/` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` | `…\managed-settings.d\` |

- `managed-settings.d/` 配下の `*.json` は `managed-settings.json` の後にアルファベット順でマージされる（数値プレフィックスでマージ順を制御。単一値は後のファイルが勝ち、配列は連結・重複排除、オブジェクトは deep-merge）。**例外**: `fallbackModel` と `modelPicker` は後のファイルが全体を置き換え、`extraKnownMarketplaces` と `managedMcpServers` は同名エントリを後のファイルが丸ごと置き換える（2026-10-11 追記）。
- **旧 Windows パス** `C:\ProgramData\ClaudeCode\managed-settings.json` は **v2.1.75 で廃止**。`C:\Program Files\ClaudeCode\` へ移行する。
- **Windows の Group Policy / レジストリ配置**: managed 設定は `HKLM\SOFTWARE\Policies\ClaudeCode`（マシン全体の Group Policy）と `HKCU\SOFTWARE\Policies\ClaudeCode`（ユーザー単位）にも置ける。ただし HKCU は利用者が書き込めるため admin ソースに数えられず、**上位の admin ソース（remote / MDM・HKLM / managed settings ファイル）が存在しない場合にだけ**読まれる（2026-10-11 訂正: 以前は「HKLM と HKCU の両方から読み込まれる」とだけ書いていた）。
- **複数の managed ソースの合成（`managedSourcesBehavior`。2026-10-11 追記）**: 優先順位は ① remote（claude.ai の server-managed settings または Claude apps gateway）→ ② MDM / OS レベル（macOS plist・HKLM）→ ③ managed settings ファイル（`managed-settings.d/*.json` と `managed-settings.json`）→ ④ HKCU。既定の `"first-wins"` は、policy key を 1 つでも含む最上位のソースだけを使い、残りは（一部の cross-source キーを除いて）マージせずに無視する。`"merge"`（v2.1.242〜）は全 admin ソースを合成し、多くのキーは上位の値、配列は和集合、ロックは最も厳しい値になる。どのソースを使い、どれを飛ばしたかは `/status` で確認できる。出典: [Deploy managed settings — How Claude Code combines managed sources](https://code.claude.com/docs/en/managed-settings#how-claude-code-combines-managed-sources)
- **Claude for Government への接続（2026-10-11 追記）**: Claude for Government では Claude Code（CLI）が early access で、端末のシステムレベルの managed settings に `forceLoginMethod: "gateway"` と `forceLoginGatewayUrl`（政府向け gateway のアドレス）を必須で置き、Claude Desktop と併用する端末では `parentSettingsBehavior: "merge"` も推奨される（要 Claude Code 2.1.267 以上）。出典: [Connect Claude Code to Claude for Government](https://claude.com/docs/government/deploy-claude-code/configure)

### HIPAA 構成（Claude Code local mode）

2026-10-11 追記。HIPAA 構成は、PHI を扱い Anthropic と BAA を結んだ **Claude Enterprise** 組織の organization setting で、Claude Code（local mode）と Cowork（local mode）の機能を制限する。適用は組織の Primary Owner が行い、端末の準備は IT / セキュリティ管理者が行う。出典: [Set up Claude Code (local mode) for a HIPAA-ready organization](https://code.claude.com/docs/en/hipaa-setup)

- **対象になるセッション**: Claude Enterprise アカウントでサインインし、Claude API に直接つなぐセッションだけ。Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS / Claude apps gateway、LLM gateway などのカスタム `ANTHROPIC_BASE_URL`、Claude Console の API キーや federation credentials のセッションには適用されない。VS Code / JetBrains 拡張は local mode に含まれない（構成の適用後も動くが BAA の対象外）
- **必要バージョン**: Claude Code **v2.1.285 以上**、Claude Desktop v2.19675.0 以上。フッターに `HIPAA configured` タグが出る（v2.1.286 未満は `HIPAA`）
- **推奨 managed settings**: `forceLoginMethod: "claudeai"`・`forceLoginOrgUUID`（自組織の ID）・`allowedProviders: ["anthropic"]`。`forceLoginMethod` か `forceLoginOrgUUID` があると、`ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` / `apiKeyHelper` で認証するセッションも拒否される。v2.1.285 未満は `allowedProviders` を無視するため、`requiredMinimumVersion: "2.1.285"` を併記して古い版の起動を止められる
- **off になる機能**: WebFetch（Web search は使える）、cloud セッション（`--cloud`・`/teleport` は拒否される）と Remote Control、`/feedback`・`/bug`、artifact の公開。ClaudeCode が起動するシェルコマンド・hooks・MCP サーバーの環境からは Anthropic の認証情報（`ANTHROPIC_API_KEY` 等）が除かれる（クラウドや GitHub の認証情報は除かれない）
- **permission mode**: built-in default の `auto` は適用されず、対象セッションは Manual（`default`）で始まる（auto mode への切替は可能。前掲「built-in default の決まり方」参照）
- **セッションデータ**: local mode のセッションデータは各端末に保存され、その保護と削除は組織の責任になる。`cleanupPeriodDays` による削除は ClaudeCode の起動時にしか走らない。即時削除は v2.1.288 以降 `claude purge`（v2.1.126〜v2.1.287 は `claude project purge`）

## 対応表（まとめ）

| ファイル | 保存場所 | スコープ | 主な用途 | Git 管理 | 優先順位 | ユーザー編集 |
|----------|----------|----------|----------|----------|----------|-------------|
| `~/.claude.json` | `~/` | ユーザー（内部） | 内部状態・認証情報・Global config キー | しない | — | Global config キーは可（通常は `/config` 経由） |
| `~/.claude/settings.json` | `~/.claude/` | ユーザー | 全プロジェクト共通の個人設定 | しない | 5（最低） | **する** |
| `~/.claude/keybindings.json` | `~/.claude/` | ユーザー | キーボードショートカット | しない | — | **する** |
| `.claude/settings.json` | プロジェクトルート | プロジェクト | チーム共有のプロジェクト設定 | **する** | 4 | **する** |
| `.claude/settings.local.json` | プロジェクトルート | ローカル | プロジェクト設定の個人オーバーライド | しない | 3 | **する** |
| `.mcp.json` | プロジェクトルート | プロジェクト | MCP サーバーのチーム共有設定 | **する** | — | **する** |

> **補足（2026-10-11 訂正）**: `~/.claude.json` は ClaudeCode が内部状態を保存するファイルだが、公式は Global config キーについて「手で編集してもよい」としている（§1 参照）。ほとんどのキーは ClaudeCode と `/config` が書くため、通常の設定のカスタマイズには `settings.json` 系のファイルを使う。以前ここに書いていた「ユーザーが直接編集するものではなく」は、§1 の 2026-08-12 訂正と食い違っていた。Managed（企業管理）設定は組織が配布するもので、個人環境では通常意識する必要はない。
