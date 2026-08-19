# ClaudeCode の設定ファイル一覧と役割

> 出典: [Claude Code Settings](https://code.claude.com/docs/en/settings) / [MCP Servers](https://code.claude.com/docs/en/mcp) / [Permissions](https://code.claude.com/docs/en/permissions) / [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Sandboxing](https://code.claude.com/docs/en/sandboxing) / [Accessibility](https://code.claude.com/docs/en/accessibility) / [Corporate launcher](https://code.claude.com/docs/en/corporate-launcher) / [Workflows](https://code.claude.com/docs/en/workflows) / [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-16時点)

ClaudeCode は 6 つの JSON 設定ファイルを階層的に使い分ける。それぞれスコープ（適用範囲）と優先順位が異なり、ユーザー個人の設定・プロジェクト共有の設定・ローカルオーバーライドを分離する設計になっている。さらに Claude Desktop は独自の設定ファイルを 1 つ持つ（計 7 ファイル）。

## 設定ファイル詳細

### 1. `~/.claude.json`（内部管理ファイル）

- **目的**: ClaudeCode の内部状態・認証情報の保存
- **内容**: セッション情報、認証トークンなど ClaudeCode が内部的に管理するデータ
- **保存場所**: ユーザーのホームディレクトリ（`~/.claude.json`）
- **スコープ**: ユーザーレベル（内部管理用）
- **Git 管理**: しない（個人の認証情報を含む）
- **備考**: かつては `allowedTools` や `ignorePatterns` もここに保存されていたが、現在は `settings.json` に移行済み。
- ⚠️ **「直接編集しないファイル」ではなくなった（2026-08-12 訂正）**: 公式 settings ページに **`Global config settings`** 節が新設され、次のキーは **`~/.claude.json` にしか書けない**（`settings.json` に書いても silent に無視される）。

  | キー | 内容 |
  |---|---|
  | `autoConnectIde` | 起動時に IDE へ自動接続する |
  | `autoInstallIdeExtension` | IDE 拡張を自動インストールする |
  | `diffTool` | 差分表示に使う外部ツール |
  | `externalEditorContext` | 外部エディタのコンテキスト連携 |
  | `permissionExplainerEnabled` | パーミッション要求の説明表示 |
  | `teammateDefaultModel` | Agent teams の teammate 既定モデル |

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
- **Git 管理**: **しない**。⚠️ 除外先は**リポジトリの `.gitignore` ではなく、global git excludes file**（`core.excludesFile`）に `**/.claude/settings.local.json` が追記される（2026-08-12 訂正）。リポジトリ側の `.gitignore` を見ても記載がないのはこのためである
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

> **配列型の設定はスコープ横断で「マージ」される（2026-08-12 更新）**: 公式は現在「**Array settings merge across scopes**」と記載しており、マージ対象は permission ルールに限らない。**すべての配列設定が連結 + 重複排除**される。
>
> - **例外は 2 つだけ**: `fallbackModel` と `availableModels` は優先順位に従って上書きされる。
> - `permissions.allow` / `ask` / `deny` は上位スコープが下位を置き換えるのではなく**全スコープのルールが合算**される（その上で deny が allow より強い）。「project の allow を local で消す」ことはできず、消したいなら deny を書く必要がある。
> - **`additionalDirectories` や `allowedHttpHookUrls` のような配列も同様に合算**されるため、「上位スコープで絞ったつもりが下位で足されている」状態になりうる点に注意する。
>
> 2026-08-04 時点では「permission ルールだけがマージされる」と記載していたが、公式の表現が `Permission rules merge across scopes` から `Array settings merge across scopes` に変わり、対象が広がった。出典: [Settings](https://code.claude.com/docs/en/settings)

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

> **`Shift+Tab` のサイクル順（2026-08-16 更新）**: auto mode が既定になったことに伴い、公式は起点別の挙動を明示している。**`auto` から始めた場合、最初の押下で `default` に移り、以降は `default` → `acceptEdits` → `plan` を巡回する**（`auto` はサイクルに戻らない）。

| モード | 確認なしで実行される範囲 | 主な用途 |
|--------|------------------------|----------|
| `default`（**v2.1.200 以降 UI/CLI 表記は「Manual」**、`manual` エイリアスも受理: `claude --permission-mode manual` / `"defaultMode": "manual"`。v2.1.203+ でステータスバーに `⏸ manual mode on` バッジ表示） | 読み取りのみ | 通常作業・センシティブな作業 |
| `acceptEdits` | 読み取り + ファイル編集 + 一般的な filesystem コマンド（`mkdir`/`touch`/`rm`/`rmdir`/`mv`/`cp`/`sed` 等） | レビュー前提でコードを回す |
| `plan` | 読み取り + **auto mode が使える環境では classifier が承認したコマンド**（2026-08-12 訂正。「読み取りのみ」ではない） | 変更前のコードベース調査 |
| `auto` | すべて（バックグラウンドの分類器が安全性を審査） | 長時間タスク・確認疲れの軽減 |
| `dontAsk` | 事前承認済みツールのみ（それ以外は自動拒否） | CI / 制限環境 |
| `bypassPermissions` | すべて（チェックを全バイパス） | ネット遮断したコンテナ / VM 限定 |

- `acceptEdits` が自動承認する filesystem コマンドは `mkdir` / `touch` / `rm` / `rmdir` / `mv` / `cp` / `sed`。`LANG=C` / `NO_COLOR=1` 等の安全な環境変数 prefix 付き、`timeout` / `nice` / `nohup` ラッパー付きも自動承認の対象になる。PowerShell tool 有効時は `Set-Content` 等も含む。
- `bypassPermissions` 以外のすべてのモードで、**保護パス**（`.git`、`.claude`（一部除く）、`.mcp.json`、`.bashrc` 等）への書き込みは自動承認されない。一方 **`bypassPermissions` は v2.1.126 以降、保護パスへの書き込みも prompt せず実行する**（チェックを全バイパスする設計のため。`rm -rf /` / `rm -rf ~` のみ circuit breaker として依然 prompt される）。
- `defaultMode: "auto"` は **user settings (`~/.claude/settings.json`) でのみ有効**。project / local settings に書いても無視される（リポジトリが自身に auto を付与できないようにするため）。**このとき user settings の `defaultMode` にフォールバックすることもなく、後述の built-in default が使われる**（2026-08-16 追記）。
- 管理者は managed settings で `permissions.disableAutoMode` / `permissions.disableBypassPermissionsMode` を `"disable"` にして特定モードを禁止できる。`permissions.disableAutoMode` を `"disable"` にすると、**`Shift+Tab` のサイクルから `auto` が消え、`--permission-mode auto` も起動時に拒否される**。

### 🔔 auto mode が既定の permission mode になった（2026-08-14 施行済み）

公式 [Permission modes](https://code.claude.com/docs/en/permission-modes) は現在、断定形で「**On Pro, Max, and Team plans, the built-in starting mode is auto mode.**」と記述している（2026-08-16 確認）。2026-08-12 時点までの「Starting August 14, 2026, auto mode becomes the default...」という**予告表現は既に置き換えられている**。

#### バージョン要件（見落としやすい）

**built-in default が `auto` になるには ClaudeCode 自体のバージョンが条件を満たす必要がある。**

| プラットフォーム | 必要バージョン |
|---|---|
| macOS / Linux / WSL | **v2.1.228 以降** |
| native Windows | **v2.1.233 以降** |

これより古いバージョンでは **built-in default は Manual のまま**である。「2026-08-14 を過ぎたから自動的に auto になる」わけではない。

#### セッションがどのモードで開始するかの決定順序

公式は 3 段階の優先順序を明示している。**先に決まったものが勝つ**。

1. CLI フラグ（`--permission-mode`）
2. `permissions.defaultMode`（設定ファイル）
3. built-in default（プラン・環境から決まる既定）

#### built-in default が `auto` にならない除外条件

以下のいずれかに該当すると、Pro / Max / Team であっても built-in default は `default`（Manual）になる。**表の上から順に評価され、最初に一致した行が適用される**。

| # | 条件 |
|---|---|
| 1 | `disableAutoMode: "disable"` が設定されている |
| 2 | feature-flag の取得が無効、または**インストール / アップグレード直後の最初のセッション** |
| 3 | **`claude -p`（print mode）/ Agent SDK** |
| 4 | Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS / apps gateway |
| 5 | Enterprise プラン、または Claude Console の API キー利用 |

| 論点 | 内容 |
|---|---|
| **対象** | **Pro / Max / Team プラン**。Enterprise / Claude API / Claude Platform on AWS / Google Cloud / Microsoft Foundry は引き続き opt-in |
| **既に既定を設定している場合** | **その設定が維持される**（上記の決定順序で 2 が 3 に優先するため）。一度だけ切替を促すプロンプトが出るが、受諾しない限り変わらない |
| **組織が pin している場合** | managed settings による既定は**変化しない** |
| **usage limit への影響** | **auto mode の classifier 呼び出しは usage limit に計上されなくなった**（適用済み）。「auto mode を使うと枠が減る」という懸念は解消した |
| **auto mode の一時停止** | classifier のブロックが **3 回連続**、またはセッション累計 **20 回**に達すると auto mode を抜けて通常の prompt に戻る。**この閾値は設定できない** |
| **初回通知の文言** | v2.1.228 で「auto mode は少し割高」という初回通知の注記が削除された |

> **BOSS への実務インパクト**: BOSS は Max プラン + v2.1.233 のため**バージョン要件を満たしており、対話セッションは既に auto mode が既定**である。一方、**`claude -p` を使うバッチ実行は除外条件 3 に該当し、従来どおり Manual 既定のまま**である点に注意する（`-p` で auto を使いたい場合は `--permission-mode auto` を明示する）。`~/.claude/settings.json` で `defaultMode` を明示している場合はその設定が優先されるため、意図した挙動を固定したいなら明示設定を入れておくのが確実である。
>
> 運用設計のベストプラクティス（deny すべき対象、interactive へ戻すべき作業）は [best-practices.md](best-practices.md) を参照。ハーネス（長時間ループ）設計への影響は [harness.md](harness.md) §4.13 を参照。

出典: [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Auto mode is now the default in Claude Code](https://claude.com/blog/auto-mode-default-in-claude-code)
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
| `permissions.allow` / `ask` / `deny` | ツール実行の許可・確認・拒否ルール。tool 名に **glob** 可（`"*"` で全拒否、未知 tool 名は起動時に警告）。`Tool(param:value)` でツール入力パラメータをワイルドカードマッチ（例 `Agent(model:opus)` で Opus サブエージェントをブロック、v2.1.178〜）。**v2.1.178 詳細**: matches 対象は top-level parameters(`model` / `isolation` / `run_in_background` 等)、**1 param per rule**、`*` wildcard 対応。`command` / `file_path` / `path` / `url` などの **canonical-input fields は除外**(startup 警告)、tool の specifier(`Bash(git *)` 等)を使う。tool-name の glob(`mcp__*` 等)は deny / ask で有効。**allow でも `mcp__<server>__` というリテラル接頭辞の後ろに限り glob を使える**が、`"mcp__*"` のようにアンカーのない glob は**警告付きでスキップ**される（2026-08-12 追記）。**`Cd` permission rule**(v2.1.169〜、`/cd` の移動先を制御。bare `Cd` deny で `/cd` 全体無効化、`Cd(path)` で allowlist モード、`//` / `~/` / `/` アンカー + `*` / `**` glob 対応)。**Symlink 挙動明示**: allow rules は symlink path と target の両方一致必要 (fall back to prompt)、deny rules はどちらか一致でブロック |
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
| `env` | 環境変数。Fable 5 関連の新変数として `ANTHROPIC_DEFAULT_FABLE_MODEL`（Fable 5 のデフォルト model id 上書き）・`DISABLE_PROMPT_CACHING_FABLE`（Fable 5 のプロンプトキャッシュ無効化）が追加。**追加された環境変数(2026-07 時点)**: `CLAUDE_CLIENT_PRESENCE_FILE`(v2.1.181、指定ファイル存在中は mobile push 抑制)、`CLAUDE_CODE_DISABLE_MOUSE_CLICKS`(v2.1.195、フルスクリーンのクリック/ドラッグ/ホバー無効化、ホイールは維持)、`CLAUDE_ENABLE_STREAM_WATCHDOG`(v2.1.197、5 分無音で中断・再試行、デフォルト有効。`=0` で無効化)、`CLAUDE_CODE_DISABLE_ARTIFACT`(Artifacts の無効化)、`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`(v2.1.187、remote MCP tool call の 5 分 idle timeout 調整)、`OTEL_LOG_ASSISTANT_RESPONSES`(v2.1.193、**セキュリティ注意**: 未設定時は `OTEL_LOG_USER_PROMPTS` を継承するため、既にプロンプトログを取っている環境は upgrade 時にアシスタント応答も自動で流れ始める。抑止するには明示的に `=0` を設定)、**`CLAUDE_AFK_TIMEOUT_MS`**(v2.1.198、idle 時に `AskUserQuestion` を自動継続。settings の `askUserQuestionTimeout` と対応)、**`CLAUDE_AFK_COUNTDOWN_MS`**(v2.1.198、自動継続前のカウントダウン開始、既定 20000ms)、**`CLAUDE_CODE_BRIDGE_SESSION_ID`**(v2.1.199、Remote Control 接続中に自動設定)、**`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS`**(v2.1.198、組み込み Explore / Plan subagent のみ無効化)、**`CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`**(v2.1.196、supervisor 停止時のバックグラウンド handoff 停止)、**`API_FORCE_IDLE_TIMEOUT`**(v2.1.169、5 分 idle timeout の上書き)、**`ANTHROPIC_FOUNDRY_AUTH_TOKEN`**(v2.1.203、Microsoft Foundry Bearer token 認証)。**追加された環境変数(v2.1.208〜v2.1.219)**: **`CLAUDE_CODE_PROCESS_WRAPPER`**(v2.1.208、企業ランチャー経由で自己 spawn プロセスを起動。Windows では無視。agent teams の tmux / iTerm2 ペインと Remote Control worker は v2.1.210 以降でカバー)、~~`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`~~(v2.1.212 追加 → **v2.1.224 で撤廃され no-op**。per-session の spawn 数上限は現在存在しない)、**`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`**(v2.1.217、既定 20、ultracode は免除)、**`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`**(v2.1.217、nested subagent の階層数)、**`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`**(v2.1.212、既定 200)、**`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`**(v2.1.212、2 分超の MCP tool call を自動バックグラウンド化する閾値。`0` で無効化)、**`CLAUDE_CODE_FORWARD_SUBAGENT_TEXT`**(v2.1.211、stream-json に subagent の text / thinking を含める。CLI は `--forward-subagent-text`)、**`CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`**(v2.1.214、OTel content 属性の切り詰め上限。既定 60KB)、**`CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD`**(v2.1.208、Bedrock streaming の content-type チェックをスキップ)、**`CLAUDE_AX_SCREEN_READER`**(screen reader mode。CLI は `--ax-screen-reader`)、**`CLAUDE_CODE_RESUME_INTERRUPTED_TURN`**(v2.1.211、中断ターンの自動再開。**v2.1.221 で `=0` による無効化が効かない不具合が修正**され、falsy 値が尊重されるようになった。関連: `CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS`)、**`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`**(Bash / hooks / MCP stdio の子プロセスから Anthropic・クラウド認証情報を除去。Linux では PID namespace 分離も伴い `ps` / `pgrep` / `kill` が host プロセスを見られなくなる。関連: `CLAUDE_CODE_SCRIPT_CAPS`)、**`DISABLE_EXTRA_USAGE_COMMAND`**(`/usage-credits` の無効化)。**廃止**: `CLAUDE_CODE_CONNECT_TIMEOUT_MS`(v2.1.186 で削除) |
| `askUserQuestionTimeout` | **v2.1.200〜**。`AskUserQuestion` の無応答時に自動継続するタイムアウト。値は `"60s"` / `"5m"` / **`"10m"`** / `"never"` (既定 `"never"`)。**project / local からは読まれず user-level のみ**。環境変数 `CLAUDE_AFK_TIMEOUT_MS` / `CLAUDE_AFK_COUNTDOWN_MS` と併用 |
| `cleanupPeriodDays` | **v2.1.203〜**。セッションファイル (transcript) の保持日数。**既定 30 日・最小 1**。削除は**起動時**に実行される。※ 2026-08-04 時点で書いていた「orphaned worktree の自動削除間隔」「parse 失敗時に pause」は現行公式に記載がないため削除した ([session-history.md](session-history.md) 参照) |
| `axScreenReader` | 設定キー自体は **v2.1.181〜**、**screen reader mode という機能そのものは v2.1.208 で追加**された（視覚的 TUI をラベル付きの線形テキストに置換し、VoiceOver / NVDA で読める形にする）。`tui` 設定は無効化される。CLI `--ax-screen-reader` と環境変数 `CLAUDE_AX_SCREEN_READER` が優先。v2.1.210 / 214 / 217 / 218 で読み上げ改善（permission mode 変更のアナウンス、削除テキストのアナウンス等）。出典: [Accessibility](https://code.claude.com/docs/en/accessibility) |
| `autoMemoryEnabled` / `autoMemoryDirectory` | Auto Memory の有効化 / 保存先（[memory.md](memory.md) 参照） |
| `skillOverrides` / `skillListingMaxDescChars` / `skillListingBudgetFraction` | Skills の可視性・description キャップ（既定 1536 文字）・予算（[skills.md](skills.md) 参照）。⚠️ **2026-08-12 訂正: 正しいキー名は `skillListingMaxDescChars` であり `maxSkillDescriptionChars` は存在しない**（公式全文で 0 ヒット） |
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
| `enableArtifact` | v2.1.196〜: Artifacts の利用を制御する**ユーザー設定キー**（2026-08-12 訂正。managed 専用ではない）。admin 側のマスタースイッチは別キーの **`disableArtifact`** である |
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
| `crossSessionInbound` | **v2.1.224〜**。cross-session messaging の受信ポリシー（`accept` / `hold` / `refuse`）。**既定は送受信双方の permission mode クラスから自動決定**され、bypass 側が受け手になる場合は `hold`。**v2.1.232〜 `/config` に「Messages from your other sessions」行として表示**され（user settings に書き込む）、managed / `--settings` がキーを設定中は非表示。⚠️ **`/config crossSessionInbound=value` のショートハンドはこのキーに限り拒否される**。[sub-agents.md](sub-agents.md) 参照 |
| `dialogExpiry` | **v2.1.224〜**。保留中ダイアログの有効期限。**既定 `"5m"`**（2026-08-16 訂正。従来 `"10m"` と記載していたが誤り）。受理値は `"60s"` / `"5m"` / `"10m"` / `"never"`。**`-p`（print mode）セッションにも適用**される。**user / managed / `--settings` からのみ読まれる**。環境変数 `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS` で上書き可。**v2.1.232〜 `/config` に「Dialog expiry」行として表示**され（user settings に書き込む）、managed / `--settings` がキーを設定中は非表示 |
| `isolatePeerMachines` | **v2.1.224〜**。`true` でマシンをまたぐ `SendMessage` に毎回承認を要求する。**`bypassPermissions` 下でも承認を求め、どのスコープの `true` も有効**（安全側に倒す設計） |
| `worktree.baseRef` / `symlinkDirectories` / `sparsePaths` / `bgIsolation` | worktree 生成時の基点 ref・symlink するディレクトリ・sparse checkout 対象・background セッションの隔離可否 |
| `disableAutoMode` | `"disable"` で auto mode を封鎖する（Shift+Tab のサイクルから除去し、`--permission-mode auto` も拒否）。managed settings 向け。Bedrock / Google Cloud / Microsoft Foundry 環境で管理者が auto mode を止める手段として公式に案内されている |

> 上表は運用上よく使うキーに絞っている。公式 [Settings](https://code.claude.com/docs/en/settings) にはこの他に `apiKeyHelper` / `fileSuggestion` / `deniedMcpServers` / `allowAllClaudeAiMcps` / `strictKnownMarketplaces` / `editorMode` / `agentPushNotifEnabled` / `autoScrollEnabled` 等が掲載されている。全キーの網羅は公式に委ね、本ドキュメントは判断に効くキーの解説に集中する。

> **v2.1.222〜v2.1.233 の設定・挙動変更（2026-08-12 初出 / 2026-08-16 に v2.1.233 まで延長）**
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
> | **`CLAUDE_CODE_ENABLE_TODO_TOOLS`** | 新世代モデルで既定無効化された Task / Todo ツール群を**再有効化**する（`=1`）。詳細は [sub-agents.md](sub-agents.md) の「Task / Todo ツールのモデル別提供状況」を参照 | v2.1.233 |
> | **`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`** | fan-out 時に**同一 prefix の兄弟エージェントを待たせて prompt cache を再利用**させる。**固定の待機時間ではなく「待つ上限」**（先頭 1 体の first response が始まるのを待つ上限、既定 **`5000`** ミリ秒）。`0` で無効化、`DISABLE_PROMPT_CACHING` 設定時は待たない（[harness.md](harness.md) 参照） | v2.1.229 |
> | **`CLAUDE_CODE_TOOL_MEMORY_LIMIT`** ※docs 未掲載 | Linux の memory cgroup で **Bash tool のメモリ使用量を制限**する opt-in。暴走ビルドによるセッション停止を防ぐ | v2.1.233 |
> | **`CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS`** ※docs 未掲載 | WebFetch のセッション内 URL キャッシュ TTL。**既定 15 分** | v2.1.233 |
> | **`additionalMarketplaces` / `allowedMarketplaces`** ※docs 未掲載 | `extraKnownMarketplaces` / `strictKnownMarketplaces` の **friendlier alias** として受理されるようになった（既存キー名も有効） | v2.1.232 |
> | **Windows のパス検証バイパス修正** | NT の `\??\` device prefix が UNC path 検証を回避できた問題を修正（**NTLM credential leak の経路**だった） | v2.1.233 |
> | **権限バイパス 3 件の修正** | PowerShell の `$PSDefaultParameterValues` 上書き / Linux filesystem sandbox の protected-path 回避 / cross-session messaging の socket ディレクトリ（`/tmp`）に事前配置された symlink を拒否 | v2.1.232 |
>
> ⚠️ **v2.1.233 で revert された 2 件**: v2.1.232 で入った「Bash 入力リダイレクト `< file` の権限チェック」と「Git Bash の Cygwin 形式 symlink 追跡」は、**v2.1.233 で取り消された**（後日より狭い形で再投入予定）。v2.1.232 だけを見て挙動を前提にしないこと。
>
> ※ 上表の「docs 未掲載」4 件は、公式 [Settings](https://code.claude.com/docs/en/settings) / [Environment variables](https://code.claude.com/docs/en/env-vars) ページに 2026-08-16 時点で記載がなく、**CHANGELOG のみが一次情報**である（公式 docs 側の追従待ち）。

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

> **`sandbox.network.strictAllowlist` の 4 つの制約（2026-08-04 に公式掲載を確認）**: ① allowlist の実体は **`allowedDomains` + `WebFetch(domain:...)` allow ルール**（`allowManagedDomainsOnly` 設定時は managed のエントリのみ）② **sandbox 化されたコマンドのみが対象**で、`WebFetch` のような in-process ツールはこの設定でゲートされない ③ **user / managed / CLI `--settings` からのみ有効**で、`.claude/settings.json` / `.claude/settings.local.json` に書いても**無効**（プロジェクト側から egress 制限を緩められないようにするため）④ 既定は `false`。要 v2.1.219+。出典: [Settings](https://code.claude.com/docs/en/settings) / [Sandboxing](https://code.claude.com/docs/en/sandboxing)

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
