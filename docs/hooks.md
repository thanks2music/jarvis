# ClaudeCode Hooks ガイド

> 出典: [Hooks](https://code.claude.com/docs/en/hooks) / [Get started with hooks](https://code.claude.com/docs/en/hooks-guide) / [Settings](https://code.claude.com/docs/en/settings) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-12時点)

Hooks は ClaudeCode のライフサイクルイベント（ツール実行前後・プロンプト送信時・セッション開始/終了・コンパクション前後など）で**決定論的に外部コマンド等を実行**する仕組みである。CLAUDE.md の指示が「Claude へのアドバイス（守られないことがある）」であるのに対し、Hooks は**必ず実行される**点が最大の違いである。「例外なく毎回実行したい処理」（lint・型チェック・通知・書き込みブロック等）に使う。

---

## 前提知識

### Hooks と他の拡張機能の違い

| 機能 | 実行主体 | 確実性 | コンテキストコスト |
|------|---------|--------|-------------------|
| CLAUDE.md | Claude（解釈して従う） | アドバイス（無視され得る） | 毎リクエスト（全文） |
| Skills | Claude（オンデマンド） | Claude の判断次第 | 呼び出し時 |
| **Hooks** | **ハーネス（外部プロセス）** | **決定論的（必ず実行）** | **ゼロ（外部実行）** |

Hooks はモデルのコンテキストを消費せず、モデルの「気まぐれ」に左右されない。例: 「全ファイル編集後に必ず eslint を実行」は CLAUDE.md に書くより Hooks にする方が確実である。

### Hooks が向くケース / 向かないケース

| 向く（Hooks にすべき） | 向かない（別機能が適切） |
|----------------------|----------------------|
| 編集後の lint / format / 型チェックの強制実行 | ドメイン知識の提供（→ Skills） |
| 特定パスへの書き込みブロック（例: `migrations/`） | 再利用ワークフロー（→ Skills） |
| タスク完了時の通知音・デスクトップ通知 | 外部サービス接続そのもの（→ MCP） |
| セッション開始時の環境変数注入・コンテキスト投入 | 一度きりの確認 |

---

## Hooks の定義場所とスコープ

Hooks は複数のレベルで定義でき、すべてマージされて対応イベントで発火する。

| 定義場所 | スコープ | Git 管理 |
|---------|---------|----------|
| `~/.claude/settings.json` | 全プロジェクト（ユーザー） | しない |
| `.claude/settings.json` | プロジェクト共有 | **する** |
| `.claude/settings.local.json` | プロジェクト（ローカルのみ） | しない |
| Managed policy settings | 組織管理（管理者制御） | — |
| Plugin の `hooks/hooks.json` | Plugin 有効時 | — |
| Skill / Subagent の frontmatter | コンポーネントのライフサイクル | コンポーネントに準ずる |

> Skill / Subagent の frontmatter で定義した Hooks は、そのコンポーネントが動作している間だけ有効で、終了時にクリーンアップされる（[Skills ガイド](skills.md) / [SubAgents ガイド](sub-agents.md) 参照）。
>
> **v2.1.218 の trust ゲート**: **agent frontmatter の hooks は、その agent ファイル自身が置かれているフォルダの workspace trust が承認済みであることを要求する**ようになった。untrusted なフォルダから持ち込まれた agent 定義が hook を勝手に実行するのを防ぐための変更である。外部リポジトリの `.claude/agents/` をそのまま流用している場合、trust 承認まで hook が発火しない。出典: CHANGELOG v2.1.218

---

## 設定構造

`hooks` フィールドは「イベント名 → マッチャー付きハンドラ配列」の構造を持つ。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/lint.sh",
            "timeout": 600,
            "statusMessage": "Linting"
          }
        ]
      }
    ]
  }
}
```

| フィールド | 説明 |
|-----------|------|
| `matcher` | フィルタ。完全一致 / `\|` 区切り / **カンマ区切り**(v2.1.191〜、空白許容) / 正規表現（例: `Bash`、`Edit\|Write`、`Edit,Write`、`mcp__memory__.*`、`*` で全マッチ）。**v2.1.195 でハイフンを含む matcher は exact-match に変更**(以前は unanchored regex で部分一致していた)。⚠️ **ただし一律ではない**（2026-08-12 追記）: **`FileChanged` と `StopFailure` だけはこの exact-match 化の対象外**で、従来どおり正規表現として評価される。一部イベントは matcher 非対応 |
| `type` | ハンドラ種別。`command` / `http` / `mcp_tool` / `prompt` / `agent` |
| `if` | 任意。パーミッションルールでさらに絞る（例: `Bash(git *)`）。⚠️ **ツール系 5 イベント（`PreToolUse` / `PostToolUse` / `PermissionRequest` / `SubagentStart` / `SubagentStop`）でのみ有効**（2026-08-12 追記）。**それ以外のイベントに `if` を付けると、その hook は一切発火しなくなる** |
| `timeout` | 秒。既定は **`command` / `http` / `mcp_tool` = 600、`prompt` = 30、`agent` = 60**。イベント別の例外は下表を参照 |
| `statusMessage` | 実行中のスピナーに出すメッセージ |
| `once` | `true` でセッション中 1 回だけ実行して除去。⚠️ **skill frontmatter でのみ有効**（2026-08-12 訂正）。`settings.json` や agent frontmatter に書いても**無視される** |

**`timeout` 既定値のイベント別例外**:

| イベント | 既定 timeout |
|---|---|
| `UserPromptSubmit` | `command` / `http` / `mcp_tool` を **30 秒**へ引き下げ |
| `MessageDisplay` | **10 秒**へ引き下げ |
| `SessionEnd` | 全 hook で**共有予算 1.5 秒**。settings でより長い per-hook `timeout` を指定した場合、ClaudeCode が予算をそれに合わせて引き上げる（**最大 60 秒**） |

> **hook 出力は 10,000 文字でキャップされる**: `additionalContext` / `systemMessage` / プレーンな stdout の文字列は **10,000 文字**が上限で、超過分は大きなツール結果と同じ扱いでファイルに退避され、プレビューとファイルパスに置き換えられる。長い出力を Claude に渡したい場合は、hook 側でファイルに書いてパスだけ返す設計にする。

> **同一ハンドラは自動で重複排除される**: 並列実行時、同じハンドラは自動的に dedup される（`command` は command 文字列 + args、`http` は URL で同一判定）。複数の matcher が同じ hook にヒットしても多重実行されない。

### ハンドラタイプ

| type | 用途 | 主なフィールド |
|------|------|--------------|
| `command` | 実行ファイル / スクリプトを起動 | `command`, `args`（exec 形式・シェル不使用）, `async`, **`asyncRewake`**, `shell`（`bash`/`powershell`） |
| `http` | HTTP エンドポイントに POST | `url`, `headers`, `allowedEnvVars`（env 補間に必須） |
| `mcp_tool` | 接続済み MCP ツールを呼ぶ | `server`, `tool`, `input`（`${tool_input.file_path}` 等で置換） |
| `prompt` | 軽量モデルで判定 | `prompt`（`$ARGUMENTS` = hook 入力 JSON）, `model` |
| `agent` | サブエージェントで検証 | `prompt`, `model` |

> **`args` と `shell` は排他**: `command` hook は `args`（配列）を指定すると **exec 形式**（シェル不使用）で実行され、このとき `shell` は無視される。`args` を省略すると **shell 形式**になり `shell`（`bash`/`powershell`）が効く。両方を同時に効かせることはできない。

> **`async` と `asyncRewake` の違い**: `async: true` は hook をバックグラウンド実行して結果を待たない。**`asyncRewake: true` はバックグラウンド実行に加えて「exit code 2 で Claude を rewake する」**（`async` を含意する）。rewake 時は hook の stderr（空なら stdout）が system reminder として Claude に渡るため、**長時間走るバックグラウンド処理の失敗に Claude 自身が反応できる**。「ビルドを裏で回して、失敗したら Claude に知らせる」用途に向く。

### パスプレースホルダと hook が読める環境変数

| プレースホルダ | 解決先 |
|--------------|--------|
| `${CLAUDE_PROJECT_DIR}` | プロジェクトルート |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin のインストールディレクトリ |
| `${CLAUDE_PLUGIN_DATA}` | Plugin の永続データディレクトリ |

hook の subprocess からは上記に加えて以下の環境変数が読める。

| 環境変数 | 内容 |
|---|---|
| `$CLAUDE_CODE_REMOTE` | リモート実行（Claude Code on the web 等）かどうか |
| `$CLAUDE_CODE_BRIDGE_SESSION_ID` | bridge セッション ID（v2.1.199〜） |
| `$CLAUDE_EFFORT` | 現在の reasoning effort |
| `$CLAUDE_PLUGIN_OPTION_<KEY>` | Plugin のオプション値 |

> **`OTEL_*` exporter 変数は全 hook subprocess から除去される**。hook 内で OpenTelemetry を使う場合は、hook 側で明示的に設定し直す必要がある。

---

## Hook イベント一覧

ClaudeCode は多数のライフサイクルイベントで Hooks を発火する。「Can Block」列は exit code 2 等でアクションを阻止できるかを示す。

| イベント | トリガー | ブロック可否 |
|---------|---------|------------|
| `SessionStart` | 新規セッション・resume・**fork**・`/clear`・コンパクション | 不可 |
| `Setup` | `--init-only` / `--init` / `--maintenance` フラグ | 不可 |
| `UserPromptSubmit` | ユーザーがプロンプト送信 | **可** |
| `UserPromptExpansion` | ユーザー入力のコマンド展開 | **可** |
| `PreToolUse` | ツール呼び出しの実行前 | **可** |
| `PermissionRequest` | パーミッションダイアログ表示時 | **可** |
| `PermissionDenied` | auto mode 分類器がツールを拒否 | 不可（retry 要求は可） |
| `PostToolUse` | ツール呼び出し成功後 | 不可 |
| `PostToolUseFailure` | ツール呼び出し失敗後 | 不可 |
| `PostToolBatch` | 並列ツール呼び出しの解決後 | **可** |
| `Stop` | Claude が応答を終える時 | **可**（停止を阻止し継続、ただし 8 連続 override で強制終了） |
| `StopFailure` | API エラーでターン終了 | 不可 |
| `SubagentStart` | サブエージェント起動時 | 不可 |
| `SubagentStop` | サブエージェント終了時 | **可** |
| `TeammateIdle` | Agent team のメンバーが idle になる直前 | **可** |
| `TaskCreated` | `TaskCreate` でタスク作成時 | **可** |
| `TaskCompleted` | タスク完了時 | **可** |
| `Notification` | ClaudeCode が通知を送る時 | 不可 |
| `MessageDisplay` | アシスタントのメッセージ表示時 | 不可（表示専用） |
| `InstructionsLoaded` | CLAUDE.md / `.claude/rules/*.md` ロード時 | 不可 |
| `ConfigChange` | セッション中の設定ファイル変更 | **可** |
| `CwdChanged` | 作業ディレクトリ変更 | 不可 |
| `DirectoryAdded` | `/add-dir` または SDK の `register_repo_root` で作業ディレクトリが追加された後 | 不可 |
| `FileChanged` | 監視対象ファイルの変更 | 不可 |
| `PreCompact` | コンテキストコンパクション前 | **可** |
| `PostCompact` | コンパクション完了後 | 不可 |
| `Elicitation` | MCP サーバーがユーザー入力を要求 | **可** |
| `ElicitationResult` | MCP elicitation へのユーザー応答 | **可** |
| `WorktreeCreate` | worktree 作成時 | **可**（**非ゼロ exit code すべて**が作成を中止する。exit 2 限定ではない） |
| `WorktreeRemove` | worktree 削除時 | 不可 |
| `SessionEnd` | セッション終了 | 不可 |

> **新しいイベント（要点）**:
> - **`MessageDisplay`**: アシスタントメッセージが画面に出る瞬間にテキストを変換・隠蔽できる（後述の `displayContent`）。
> - **`InstructionsLoaded`**: CLAUDE.md / rules がロードされた時に発火。`file_path` / `load_reason` / `memory_type` を受け取る。
> - **`StopFailure`**: API エラーでターンが落ちた時に発火。通知 hook を仕込んでおくと失敗に気付ける。
> - **`DirectoryAdded`**（v2.1.219〜）: `/add-dir` または SDK の `register_repo_root` control request で**セッション中に新しい作業ディレクトリが登録された後**に発火。`CwdChanged`（作業ディレクトリの移動）とは別で、こちらは「アクセス範囲の追加」に対応する。マルチルートで lint 対象や環境変数を切り替える用途に使える。
>   ✅ **公式 docs も追従済み（2026-08-04 確認）**: 公式 [hooks](https://code.claude.com/docs/en/hooks) のイベント表に掲載され、matcher（`slash_command` / `register_repo_root`）まで明記された。**blocking 非対応で decision control も持たない**（失敗は debug ログにのみ残る）ため、「ディレクトリ追加を拒否する」用途には使えない。

> **`PostToolUse` と `PostToolBatch` のブロック可否が異なる理由**: `PostToolUse` は単一ツールが**既に実行された後**に発火するためブロックできない（show stderr のみ）。一方 `PostToolBatch` は並列ツール呼び出しの解決後・**次のモデル呼び出し前**に発火するため、エージェンティックループを停止できる。

### イベント別のマッチャー対象

| イベント | マッチ対象 | 例 |
|---------|-----------|-----|
| `PreToolUse` / `PostToolUse` 等 | ツール名 | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | セッションソース | `startup`, `resume`, `clear`, `compact`, **`fork`** |
| `SessionEnd` | 終了理由 | `logout`, `clear`, `resume`, `prompt_input_exit`, **`bypass_permissions_disabled`**(auto mode 分類器が bypass 挙動を無効化した時), **`other`** の 6 値 |
| `Setup` | 起動フラグ | **`init`, `maintenance`**(`--init-only` / `--init` / `--maintenance` フラグを判別) |
| `InstructionsLoaded` | ロード分類 | **`session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`** の 5 値 |
| `DirectoryAdded` | 追加経路 | **`slash_command`**(`/add-dir` 経由), **`register_repo_root`**(SDK control request 経由) |
| `StopFailure` | API エラー種別 | **`rate_limit`, `overloaded`, `authentication_failed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, **`oauth_org_not_allowed`**, `unknown`** の 10 値 |
| `ConfigChange` | 変更された設定ソース | **`user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`** |
| `Notification` | 通知種別 | `permission_prompt`, `auth_success`, `elicitation_dialog`, **`idle_prompt`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`** の 9 値（2026-08-12 追記: 3 値と書いていたのは不足） |
| `SubagentStart` / `SubagentStop` | エージェント種別 | `general-purpose`, `Explore`, `Plan` に加え、**カスタム agent 名**および **plugin スコープ名**（`^my-plugin:reviewer$` のように正規表現で書ける） |
| `PreCompact` / `PostCompact` | トリガー | `manual`, `auto` |
| `FileChanged` | 監視ファイル名 | `.envrc\|.env`（リテラル） |
| `Stop` / `UserPromptSubmit` / `MessageDisplay` 等 | matcher 非対応 | 常時発火 |

> **`SessionStart` の `fork` source（v2.1.214〜）**: fork 起点のセッション開始は、従来 `resume` に含まれていたが **`fork` として独立**した。`fork` が渡るのは ① `--fork-session` + `--resume` / `--continue`、② `/fork` による background コピー、③ `/branch` の 3 経路。「resume 時だけ環境を復元する」hook を書いている場合、**fork 時に発火しなくなる**ため matcher の見直しが必要である。出典: [Hooks](https://code.claude.com/docs/en/hooks) / CHANGELOG v2.1.214

> **`if:` 条件での single-segment glob の扱い（v2.1.214〜）**: hook の `if:` 条件では **`"Edit(src/**)"` が `<cwd>/src` のみにマッチ**する。任意の深さに効かせたい場合は `"Edit(**/src/**)"` と書く。**permission ルールの deny / ask は任意深さのまま**なので、同じ記法でも hook 側と挙動が異なる点に注意する（`docs/config-files.md`「permission ルールの重要な変更」参照）。

---

## 入力と出力

### 共通入力フィールド

Hooks は stdin で JSON を受け取る。共通フィールドの主なもの:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "effort": { "level": "medium" },
  "agent_id": "agent-uuid",
  "agent_type": "Explore",
  "prompt_id": "01H..."
}
```

イベント固有の入力（例: `PreToolUse` は `tool_name` / `tool_input`、`PostToolUse` は加えて `tool_result`、`UserPromptSubmit` は `prompt`）が付与される。

> **`prompt_id`（v2.1.196〜）**: すべての hook イベントが `prompt_id`(UUID) を受信する。OpenTelemetry 相関用に、同一プロンプトに紐づく複数 hook 呼び出しを紐づけたい場合に使う。**初回 user input が発生するまでは `prompt_id` は absent (session-only hook 等では null になり得る)**。出典: [Hooks — code.claude.com](https://code.claude.com/docs/en/hooks)。

### exit code の挙動

| exit code | 意味 | 効果 |
|-----------|------|------|
| `0` | 成功 | stdout の JSON 出力を処理する |
| `2` | ブロッキングエラー | アクションをブロックし、stderr を Claude に渡す |
| `1` / その他 | 非ブロッキングエラー | hook エラー通知を出して実行は継続 |

exit code 2 の効果はイベント依存（`PreToolUse`=ツール呼び出しをブロック、`UserPromptSubmit`=プロンプトをブロックしコンテキストから消去、`Stop`=停止を阻止し会話継続、`PreCompact`=コンパクションをブロック など）。

> **v2.1.214 の修正**: exit code 2 を返した hook が、**stdout の JSON が schema validation に失敗した場合にブロックしなかった**不具合が修正された。現在はドキュメント通り、JSON が不正でも exit code 2 は確実にブロックする。exit code 2 をガードレールとして使っている hook は、この version 以前では**すり抜けていた可能性がある**点に注意する。出典: CHANGELOG v2.1.214

### JSON 出力（hookSpecificOutput）

exit code 0 のとき、stdout に JSON を返して構造化制御できる。

```json
{
  "continue": true,
  "stopReason": "Build failed",
  "suppressOutput": false,
  "systemMessage": "Warning text",
  "decision": "block",
  "reason": "Policy violation",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "Current branch: main",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Why",
    "updatedInput": {},
    "displayContent": "New text",
    "reloadSkills": true
  }
}
```

主なフィールド:

| フィールド | 対象 | 役割 |
|-----------|------|------|
| `continue` | 全般 | `false` で Claude を完全停止（`stopReason` で理由提示） |
| `suppressOutput` | 全般 | stdout をトランスクリプトから隠す |
| `systemMessage` | 全般 | ユーザー向け警告を表示 |
| `additionalContext` | 多くのイベント | Claude に追加コンテキストを注入 |
| `permissionDecision` | `PreToolUse` | `allow` / `deny` / `ask` / `defer` |
| **`decision`（オブジェクト）** | **`PermissionRequest`** | `{ "behavior": "allow" \| "deny", "updatedInput": {...} }` の形で返す。**`PreToolUse` の `permissionDecision` とはフィールド名・形が異なる**点に注意（`PermissionRequest` で `permissionDecision` を返しても効かない） |
| `updatedInput` | `PreToolUse` | ツール入力（引数）を書き換える。※旧称ではなく現行公式のフィールド名 |
| `updatedToolOutput` | `PostToolUse` | ツールの実行結果（出力）を差し替える |
| `displayContent` | `MessageDisplay` | 画面表示テキストを差し替える |
| `decision` | `Stop` 等 | `block` で停止を阻止し会話継続 |
| `retry` | `PermissionDenied` | `true` で、拒否されたツール呼び出しの再試行をモデルに許可する（`PermissionDenied` は exit code / stderr が無視されるため、retry は JSON のこのフィールドで要求する） |
| `reloadSkills` | `SessionStart` | hook 実行後にスキルを再スキャン（スキルをインストールする hook が同セッションで有効化される） |
| `sessionTitle` / `watchPaths` / `initialUserMessage` | `SessionStart` | セッション名変更 / `FileChanged` 監視パス / `-p` モードの初回メッセージ |
| `terminalSequence` | 多くのイベント | 端末エスケープシーケンス（OSC）を発行。デスクトップ通知（OSC 9 / 99 / 777）・ウィンドウ/アイコンタイトル（OSC 0 / 1 / 2）・タスクバー進捗（OSC 9;4）・ベル（BEL）に使う。許可された OSC と BEL に制限（カーソル移動・色破壊を防ぐ、v2.1.141〜） |

> **`SessionStart` の `additionalContext`** は、セッション開始時に「現在のブランチ・未解決 issue 数・直近のデプロイ状況」などを Claude に自動投入する用途で有用。**`reloadSkills: true`** と組み合わせれば、スキルを動的に取得・有効化する hook を 1 セッション内で完結できる。

### Stop / SubagentStop の additionalContext

`Stop`・`SubagentStop` は `hookSpecificOutput.additionalContext` を返せる。`decision` を省略すれば、ターンを完了させつつフィードバックだけ追加できる（例: 「テスト完了。次はセキュリティ監査を検討」）。

### Stop hook の 8 連続 override(セーフティネット)

Stop hook は `decision: "block"` でターン継続を強制できるが、**ClaudeCode は 8 連続で override が続いた場合、その override を打ち切ってターンを終了する**。無限ループで Claude を停止不能にしないためのセーフティネット。「Hooks は決定論的で必ず実行される」原則は Stop hook に関して条件付きになる点に注意。決定論性を厳密に担保したい制御は `PreToolUse` の `permissionDecision: "deny"` を使う。出典: [Best practices — Verification loops](https://code.claude.com/docs/en/best-practices)。

---

## PreToolUse のパーミッション制御

`PreToolUse` hook はツール実行の可否を制御できる。

| `permissionDecision` | 挙動 |
|---------------------|------|
| `allow` | プロンプトなしで承認 |
| `deny` | ツール呼び出しをブロック |
| `ask` | ユーザーのパーミッションプロンプトにエスカレート |
| `defer` | 通常のパーミッションフローに委ねる |

`migrations/` への書き込みをブロックする例（自然言語で Claude に依頼すれば hook を構成してくれる）:

> migrations フォルダへの Write/Edit をブロックする PreToolUse hook を書いて。

> **`ask` が auto mode に上書きされなくなった（v2.1.211）**: 従来は auto mode 配下で hook の `ask` 判定が分類器の自動承認に飲まれることがあったが、**hook の `ask` が最低保証としてプロンプトを出す**ようになった。auto mode で運用しつつ「特定操作だけは必ず人間に確認させる」ガードレールが hook で確実に組める。
>
> 併せて **v2.1.212** で、`continue: false` による halt が **ツール失敗時や mid-stream 完了時に効かなくなる**不具合が修正されている。出典: CHANGELOG v2.1.211 / v2.1.212

---

## 環境変数の永続化（CLAUDE_ENV_FILE）

`SessionStart`（および `Setup` / `CwdChanged` / `FileChanged`）hook は `CLAUDE_ENV_FILE` に書き込むことで、以降の Bash コマンドに環境変数を永続化できる。

```bash
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

---

## 管理・確認

- **`/hooks`**: 設定済み Hooks の読み取り専用ブラウザを開く。イベントごとの件数・matcher・ハンドラ・ソース（User / Project / Local / Plugin / Session / Built-in）・詳細を確認できる。
- **`disableAllHooks: true`**: settings に追加すると全 Hooks を無効化（managed policy hooks は対象外。これを無効化できるのは managed settings の `disableAllHooks` のみ）。

---

## 実践パターン

### パターン 1: 編集後の自動 lint（PostToolUse）

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/lint.sh" }]
      }
    ]
  }
}
```

CLAUDE.md に「編集後 lint」と書くより確実に走る（[best-practices.md](best-practices.md) の「Hooks（確実な自動実行）」参照）。

### パターン 2: 完了通知（Stop / StopFailure）

タスク完了やターン失敗で音やデスクトップ通知を出す。長時間タスクの完了・失敗に気付ける。`StopFailure` を仕込むと、API エラーで落ちたターンも検知できる。

### パターン 3: 簡易フィードバックループ（PostToolUse + テスト）

`PostToolUse` でテスト・型チェックを自動実行すれば、評価器エージェントを立てなくても簡易的な生成×検証ループが回る（[harness.md](harness.md) 参照）。

### パターン 4: ガードレール（PreToolUse でブロック）

保護したいパスや危険コマンドを `PreToolUse` の `permissionDecision: "deny"` でブロックする。auto mode の安全網に加えて、プロジェクト固有の禁止事項を決定論的に強制できる。

---

## セキュリティ関連の修正（v2.1.222）

**PreToolUse の auto-allow hook が background agent の内部タスクでツール制限をバイパスしていた問題**が修正された。

- 対象は background agent が内部的に実行する**要約・compaction・rename** といったタスク。
- これらのタスクでは、`PreToolUse` hook が `allow` を返すとツール制限が効かない状態になっていた。
- 「hook で自動承認しているが、内部タスクは対象外のはず」と考えて設計していた場合、**想定より広い範囲が承認されていた**可能性がある。

`CLAUDE_CODE_MESSAGING_SOCKET`（v2.1.224）は、cross-session messaging のセッション固有 inbox socket のパスを持つ環境変数で、**`SessionStart` より前**から hook / Bash に export される。hook 側からセッション間通信の宛先を知りたい場合に使える（[sub-agents.md](sub-agents.md) 参照）。

出典: CHANGELOG v2.1.222 / v2.1.224

---

## 関連ドキュメント

- [Hooks](https://code.claude.com/docs/en/hooks) — 公式 Hooks ドキュメント
- [Get started with hooks](https://code.claude.com/docs/en/hooks-guide) — 公式入門ガイド
- [ClaudeCode のベストプラクティス](best-practices.md) — 「環境を整備する」内の Hooks 活用
- [ClaudeCode Skills ガイド](skills.md) — Skill frontmatter の hooks
- [ClaudeCode SubAgents ガイド](sub-agents.md) — Subagent frontmatter の hooks
- [ClaudeCode Plugins ガイド](plugins.md) — Plugin の hooks バンドル
- [ハーネス設計ガイド](harness.md) — Hooks による簡易フィードバックループ
