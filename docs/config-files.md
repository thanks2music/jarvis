# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) / [Permission modes](https://code.claude.com/docs/en/permission-modes) (2026-07-11時点)

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

> auto mode の詳細（分類器のブロック対象・利用条件・フォールバック挙動）は [`docs/best-practices.md`](best-practices.md) を参照。

## settings.json の主な設定項目

`settings.json`（user / project / local）で指定できる代表的なフィールド。網羅的な一覧は公式 [Settings](https://code.claude.com/docs/en/settings) を参照する。

| フィールド | 役割 |
|-----------|------|
| `permissions.allow` / `ask` / `deny` | ツール実行の許可・確認・拒否ルール。tool 名に **glob** 可（`"*"` で全拒否、未知 tool 名は起動時に警告）。`Tool(param:value)` でツール入力パラメータをワイルドカードマッチ（例 `Agent(model:opus)` で Opus サブエージェントをブロック、v2.1.178〜）。**v2.1.178 詳細**: matches 対象は top-level parameters(`model` / `isolation` / `run_in_background` 等)、**1 param per rule**、`*` wildcard 対応。`command` / `file_path` / `path` / `url` などの **canonical-input fields は除外**(startup 警告)、tool の specifier(`Bash(git *)` 等)を使う。tool-name の glob(`mcp__*` 等)は deny / ask で有効。**`Cd` permission rule**(v2.1.169〜、`/cd` の移動先を制御。bare `Cd` deny で `/cd` 全体無効化、`Cd(path)` で allowlist モード、`//` / `~/` / `/` アンカー + `*` / `**` glob 対応)。**Symlink 挙動明示**: allow rules は symlink path と target の両方一致必要 (fall back to prompt)、deny rules はどちらか一致でブロック |
| `permissions.defaultMode` | 既定のパーミッションモード（前掲の 6 モード） |
| `permissions.disableAutoMode` / `disableBypassPermissionsMode` | `"disable"` で特定モードを禁止（managed 向け） |
| `model` / `availableModels` / `enforceAvailableModels` | 既定モデル / 選択可能モデルの allowlist / allowlist を Default モデルにも強制（managed・policy のみ有効、v2.1.175〜）。フル model ID 例: `claude-opus-4-8`・`claude-fable-5`・`claude-sonnet-5`（Fable 5 は要 v2.1.170+、Sonnet 5 は要 v2.1.197+）。**v2.1.187 / v2.1.196 で強化**: managed で `/model` ピッカー・`--model`・`ANTHROPIC_MODEL` 環境変数の 3 経路すべてを制限可能。`/model` UI に "Org default" / "Role default" ラベル表示 |
| `fallbackModel` | プライマリが過負荷・不在のとき順次試す代替モデル（最大 3 つ、CLI は `--fallback-model`、v2.1.168〜） |
| `modelOverrides` | サブエージェント種別ごとのモデル上書き |
| `effortLevel` | 既定 effort（`low`/`medium`/`high`/`xhigh`。`max`/`ultracode` は session-only で不可） |
| `alwaysThinkingEnabled` | extended thinking を既定で有効化 |
| `outputStyle` / `statusLine` | 出力スタイル / カスタムステータスライン |
| `agent` | メインスレッドを名前付き subagent として起動 |
| `hooks` | ライフサイクルイベントの Hooks 定義 |
| `env` | 環境変数。Fable 5 関連の新変数として `ANTHROPIC_DEFAULT_FABLE_MODEL`（Fable 5 のデフォルト model id 上書き）・`DISABLE_PROMPT_CACHING_FABLE`（Fable 5 のプロンプトキャッシュ無効化）が追加。**追加された環境変数(2026-07 時点)**: `CLAUDE_CLIENT_PRESENCE_FILE`(v2.1.181、指定ファイル存在中は mobile push 抑制)、`CLAUDE_CODE_DISABLE_MOUSE_CLICKS`(v2.1.195、フルスクリーンのクリック/ドラッグ/ホバー無効化、ホイールは維持)、`CLAUDE_ENABLE_STREAM_WATCHDOG`(v2.1.197、5 分無音で中断・再試行、デフォルト有効。`=0` で無効化)、`CLAUDE_CODE_DISABLE_ARTIFACT`(Artifacts の無効化)、`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(v2.1.187、remote MCP tool call の 5 分 idle timeout 調整)、`OTEL_LOG_ASSISTANT_RESPONSES`(v2.1.193、**セキュリティ注意**: 未設定時は `OTEL_LOG_USER_PROMPTS` を継承するため、既にプロンプトログを取っている環境は upgrade 時にアシスタント応答も自動で流れ始める。抑止するには明示的に `=0` を設定)、**`CLAUDE_AFK_TIMEOUT_MS`**(v2.1.198、idle 時に `AskUserQuestion` を自動継続。settings の `askUserQuestionTimeout` と対応)、**`CLAUDE_AFK_COUNTDOWN_MS`**(v2.1.198、自動継続前のカウントダウン開始、既定 20000ms)、**`CLAUDE_CODE_BRIDGE_SESSION_ID`**(v2.1.199、Remote Control 接続中に自動設定)、**`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS`**(v2.1.198、組み込み Explore / Plan subagent のみ無効化)、**`CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`**(v2.1.196、supervisor 停止時のバックグラウンド handoff 停止)、**`API_FORCE_IDLE_TIMEOUT`**(v2.1.169、5 分 idle timeout の上書き)、**`ANTHROPIC_FOUNDRY_AUTH_TOKEN`**(v2.1.203、Microsoft Foundry Bearer token 認証)。**廃止**: `CLAUDE_CODE_CONNECT_TIMEOUT_MS`(v2.1.186 で削除) |
| `askUserQuestionTimeout` | **v2.1.200〜**。`AskUserQuestion` の無応答時に自動継続するタイムアウト。値は `"60s"` / `"5m"` / `"never"` (既定 `"never"`)。**project / local からは読まれず user-level のみ**。環境変数 `CLAUDE_AFK_TIMEOUT_MS` / `CLAUDE_AFK_COUNTDOWN_MS` と併用 |
| `cleanupPeriodDays` | **v2.1.203〜**。セッションファイル・orphaned worktree の自動削除間隔 (日数)。設定ファイルが読めない/parse 失敗時は**クリーンアップが pause し `/status` に警告** (managed 設定のみ挙動継続) |
| `axScreenReader` | **v2.1.181〜**。screen-reader 向けフラットテキストレンダリングの有効化。`tui` 設定は無効化される。CLI `--ax-screen-reader` と環境変数 `CLAUDE_AX_SCREEN_READER` が優先 |
| `autoMemoryEnabled` / `autoMemoryDirectory` | Auto Memory の有効化 / 保存先（[memory.md](memory.md) 参照） |
| `skillOverrides` / `maxSkillDescriptionChars` / `skillListingBudgetFraction` | Skills の可視性・description キャップ・予算（[skills.md](skills.md) 参照） |
| `sandbox` | Bash サンドボックスの設定。**サブフィールド**: `sandbox.allowAppleEvents`(v2.1.181、macOS で sandbox コマンドが Apple Events 送信可、opt-in)、`sandbox.credentials`(v2.1.187、sandbox 化コマンドが credential file / secret env を読むことをブロック) |
| `extraKnownMarketplaces` | 追加 Plugin marketplace（[plugins.md](plugins.md) 参照） |
| `claudeMd` / `claudeMdExcludes` | managed CLAUDE.md 本文 / 読み込み除外パターン |
| `autoMode` / `useAutoModeDuringPlan` | auto mode の挙動カスタマイズ / plan mode 中の auto 利用。**サブフィールド**: `autoMode.classifyAllShell`(v2.1.193、Bash / PowerShell の**全**コマンドを分類器に通す。既定は "arbitrary code execution" パターンのみ。denial reason が transcript / toast / `/permissions` に表示) |
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
| `strictPluginOnlyCustomization` | カスタマイズを Plugin 経由に限定する |
| `advisorModel` | `/advisor`（第 2 モデル相談ツール）が使うモデル（v2.1.98〜） |
| `attribution` | commit / PR の署名（Co-Authored-By 等）のカスタマイズ。**サブフィールド**: `attribution.sessionUrl`(v2.1.183、web / Remote Control セッションが commit / PR に添える claude.ai セッションリンクを省略できる) |
| `subagentStatusLine` | サブエージェント用のステータスライン |
| `footerLinksRegexes` | フッター行に正規表現マッチのリンクバッジを追加（v2.1.176〜） |
| `language` | セッションタイトルの言語を固定（既定は会話言語で自動生成、v2.1.176〜） |
| `disableBundledSkills` | バンドルスキル・workflows・組込コマンドをモデルから隠す（env `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` でも可） |
| `dynamicWorkflowSize` (仮称) | **v2.1.202〜**。dynamic workflows (ultracode) で 1 セッションが spawn する agent 数の上限を制御。暴走を防ぐ安全弁 (公式 CHANGELOG では設定名が略称。詳細キー名は公式 [Settings](https://code.claude.com/docs/en/settings) で要確認)。関連 OpenTelemetry 属性: `workflow.run_id` / `workflow.name` |

### Managed 専用の追加設定 (2026-07 時点)

「managed 側で個人環境の自由度を絞る」ための強化設定。個人開発では通常不要だが、Team/Enterprise 環境で覚えておく。

| フィールド | 役割 |
|-----------|------|
| `allowManagedHooksOnly` | Hooks は managed 定義のみ許可 (ユーザー/プロジェクト定義を無効化) |
| `allowManagedMcpServersOnly` | MCP サーバーは managed 定義のみ許可 |
| `allowManagedPermissionRulesOnly` | permission ルールは managed 定義のみ許可 |
| `strictPluginOnlyCustomization` | array 指定対応 (カスタマイズを Plugin 経由に限定) |
| `sandbox.filesystem.allowManagedReadPathsOnly` | filesystem 読み取り path は managed 定義のみ |
| `sandbox.network.allowManagedDomainsOnly` | ネットワーク接続先は managed 定義のみ |
| `forceRemoteSettingsRefresh` | remote settings の再取得を強制 |
| `blockedMarketplaces` | Plugin marketplace の deny list |
| `pluginTrustMessage` | Plugin 信頼確認時のカスタムメッセージ |
| `wslInheritsWindowsSettings` | WSL 側が Windows 側の managed settings を継承 |

出典: [Permissions — code.claude.com](https://code.claude.com/docs/en/permissions) / [Settings — code.claude.com](https://code.claude.com/docs/en/settings)

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
