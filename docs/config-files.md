# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) / [Permission modes](https://code.claude.com/docs/en/permission-modes) (2026-06-10時点)

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
| `default` | 読み取りのみ | 通常作業・センシティブな作業 |
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
| `permissions.allow` / `ask` / `deny` | ツール実行の許可・確認・拒否ルール |
| `permissions.defaultMode` | 既定のパーミッションモード（前掲の 6 モード） |
| `permissions.disableAutoMode` / `disableBypassPermissionsMode` | `"disable"` で特定モードを禁止（managed 向け） |
| `model` / `availableModels` | 既定モデル / 選択可能モデルの制限。フル model ID 例: `claude-opus-4-8`・`claude-fable-5`（Fable 5 は要 v2.1.170+） |
| `fallbackModel` | プライマリが過負荷・不在のとき順次試す代替モデル（最大 3 つ、CLI は `--fallback-model`、v2.1.168〜） |
| `modelOverrides` | サブエージェント種別ごとのモデル上書き |
| `effortLevel` | 既定 effort（`low`/`medium`/`high`/`xhigh`。`max`/`ultracode` は session-only で不可） |
| `alwaysThinkingEnabled` | extended thinking を既定で有効化 |
| `outputStyle` / `statusLine` | 出力スタイル / カスタムステータスライン |
| `agent` | メインスレッドを名前付き subagent として起動 |
| `hooks` | ライフサイクルイベントの Hooks 定義 |
| `env` | 環境変数。Fable 5 関連の新変数として `ANTHROPIC_DEFAULT_FABLE_MODEL`（Fable 5 のデフォルト model id 上書き）・`DISABLE_PROMPT_CACHING_FABLE`（Fable 5 のプロンプトキャッシュ無効化）が追加 |
| `autoMemoryEnabled` / `autoMemoryDirectory` | Auto Memory の有効化 / 保存先（[memory.md](memory.md) 参照） |
| `skillOverrides` / `maxSkillDescriptionChars` / `skillListingBudgetFraction` | Skills の可視性・description キャップ・予算（[skills.md](skills.md) 参照） |
| `sandbox` | Bash サンドボックスの設定 |
| `extraKnownMarketplaces` | 追加 Plugin marketplace（[plugins.md](plugins.md) 参照） |
| `claudeMd` / `claudeMdExcludes` | managed CLAUDE.md 本文 / 読み込み除外パターン |
| `autoMode` / `useAutoModeDuringPlan` | auto mode の挙動カスタマイズ / plan mode 中の auto 利用 |
| `disableAllHooks` | 全 Hooks の無効化（managed hooks は managed 側でのみ無効化可、[hooks.md](hooks.md) 参照） |
| `workflowKeywordTriggerEnabled` / `disableWorkflows` / `ultracode` | dynamic workflows（ultracode）のキーワードトリガ / 無効化 / 既定起動（v2.1.157〜） |
| `parentSettingsBehavior` | 上位スコープ設定の継承挙動（v2.1.133〜） |
| `policyHelper` | パーミッション判定を委譲する外部ヘルパー |
| `defaultShell` | Bash ツールが使う既定シェル |
| `autoUpdatesChannel` | 自動更新チャンネルの選択 |
| `teammateMode` | Agent teams の動作モード |
| `plansDirectory` | plan mode の計画ファイル保存先 |
| `requiredMinimumVersion` / `requiredMaximumVersion` | 許可する ClaudeCode バージョン範囲（managed 向け、v2.1.163〜） |
| `disableRemoteControl` | `/remote-control` の無効化 |
| `strictPluginOnlyCustomization` | カスタマイズを Plugin 経由に限定する |

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
