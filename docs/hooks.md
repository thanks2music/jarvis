# ClaudeCode Hooks ガイド

> 出典: [Hooks](https://code.claude.com/docs/en/hooks) / [Get started with hooks](https://code.claude.com/docs/en/hooks-guide) / [Settings](https://code.claude.com/docs/en/settings) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / [Configure permissions](https://code.claude.com/docs/en/permissions) / [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [Mods: React to events](https://code.claude.com/docs/en/plugins/mods/events) / [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-11-01時点。CHANGELOG は v2.1.316 まで反映)

Hooks は ClaudeCode のライフサイクルイベント（ツール実行前後・プロンプト送信時・セッション開始/終了・コンパクション前後など）で**決定論的に外部コマンド等を実行**する仕組みである。CLAUDE.md の指示が「Claude へのアドバイス（守られないことがある）」であるのに対し、Hooks は**必ず実行される**点が最大の違いである。「例外なく毎回実行したい処理」（lint・型チェック・通知・書き込みブロック等）に使う。

---

## 前提知識

### Hooks と他の拡張機能の違い

| 機能 | 実行主体 | 確実性 | コンテキストコスト |
|------|---------|--------|-------------------|
| CLAUDE.md | Claude（解釈して従う） | アドバイス（無視され得る） | 毎リクエスト（全文） |
| Skills | Claude（オンデマンド） | Claude の判断次第 | 呼び出し時 |
| **Hooks** | **ハーネス（外部プロセス）** | **決定論的（必ず実行）** | **ゼロ（外部実行）** |
| Mods（関数 hook を持つ plugin） | ハーネス（ClaudeCode 本体のプロセス内で JS / TS の関数を実行） | 決定論的（イベントで必ず呼ばれる）。ツール呼び出し・プロンプトの書き換え、UI の描画、権限判定の上書きまでできる | 原則ゼロ（プロンプトを書き換え・投入した分は会話に入る） |

Hooks はモデルのコンテキストを消費せず、モデルの「気まぐれ」に左右されない。例: 「全ファイル編集後に必ず eslint を実行」は CLAUDE.md に書くより Hooks にする方が確実である。

### Hooks と Mods の関係

**Mods** は、ClaudeCode のイベント（ツール呼び出し・プロンプト送信・UI の描画など）で呼ばれる **JavaScript / TypeScript の関数（hook）を持つ plugin** である（CLI v2.1.287〜 / Desktop v2.1.286〜で既定 ON、公式 docs の記載）。公式は両者をどちらも「hook」と呼ぶため、mods のページでは本ページの hook を **settings hook** と呼び分けている。settings hook は mods と併存して従来どおり動く。

| 観点 | settings hook（本ページ） | mod |
|---|---|---|
| 実体 | settings ファイル等に書くシェルコマンド・HTTP リクエスト・prompt など | plugin 内の関数。ClaudeCode 本体と同じプロセスで動く |
| 変えられるもの | ツール呼び出し / プロンプトを通すか、ツールの引数と結果、Claude への追加コンテキスト | ツール呼び出し・プロンプト・コマンド・ターン、UI の描画（pane / band / 既存行の差し替え） |
| 権限判定 | 締めることはできても、パーミッションルールより緩めることはできない | `tool.check` で `allow` / `ask` / `deny` を返す。**組込みのガードが働く環境（managed settings がある、または Team / Enterprise の `/login`）では、deny / ask ルールと、どの settings ファイルの `PreToolUse` hook のブロックも覆せない**。ガードの無い環境（managed settings の無いマシンの API キーのセッションや、`CLAUDE_CODE_OAUTH_TOKEN` のセッションを含む）では、deny ルールや `PreToolUse` hook がブロックした呼び出しも承認しうる（auto mode では分類器も通らない）。2026-10-11 時点の記載は「ask ルールや managed 以外の `PreToolUse` hook がブロックした呼び出しも承認しうる」だった |
| 実行環境 | 外部プロセス | **sandbox の外で、ユーザーの権限のまま**（本体と同じ）動く。ファイル読み書き・プロセス起動・ネットワーク・秘密情報の参照・モデル呼び出し（利用量を消費）が可能 |

mod は sandbox を有効にしていても隔離されない（sandbox が隔離するのは Claude が実行する Bash コマンドで、mod が起動したプロセスは対象外）。導入前に `claude plugin validate <dir>` で、その mod が扱うイベントと呼び出す API を一覧できる。managed settings があるマシン、またはセッションの資格情報が Team / Enterprise プランの `/login` である場合は、ClaudeCode 組込みのガード（`sec-default@builtin`）がユーザーの mod より先に読み込まれる。ガードが働くと、ユーザーの mod は **deny ルールで拒否された呼び出し**（組織は `allowModsToOverrideDenyRules` で変更可）も、**ask ルールでプロンプトが出る呼び出し**も、**どの settings ファイルの `PreToolUse` hook がブロックした呼び出し**も承認できない。API キー・Amazon Bedrock・Google Cloud's Agent Platform・Microsoft Foundry で認証するユーザーは、managed settings のあるマシンでだけガードが働く。`CLAUDE_CODE_OAUTH_TOKEN` で動くセッションは、Team / Enterprise の `/login` が保存されていても該当しない（**2026-11-01 更新**: 2026-10-11 時点は「Team / Enterprise プランでサインインしている場合」「deny ルールで拒否された呼び出しをユーザーの mod が承認できないようにする」とだけ書いていた）。managed settings の `PreToolUse` hook はどの mod の `tool.call` よりも先に動き、そのブロックはどの mod も覆せない。mod が呼び出しを書き換えた場合は、書き換え後の呼び出しに対して managed hook がもう一度動く。`tool.check` と `PreToolUse` hook の評価順は「[PreToolUse のパーミッション制御](#pretooluse-のパーミッション制御)」の注記を参照。

詳細（作り方・イベント・API・組織での管理）は [Mods ガイド](mods.md) にまとめる。出典: [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [Mods — React to events](https://code.claude.com/docs/en/plugins/mods/events) / [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) / [Hooks](https://code.claude.com/docs/en/hooks)

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
| Skill の frontmatter | **skill の呼び出し後、セッションの残り全体** | コンポーネントに準ずる |
| Subagent の frontmatter | その subagent の実行中のみ | コンポーネントに準ずる |

> **Skill と Subagent で hook の寿命が異なる**（**2026-10-11 訂正**）: Subagent の frontmatter で定義した Hooks は、その subagent が動作している間だけ有効で、終了時に除去される（`Stop` hook は `SubagentStop` に変換される）。一方 **Skill の frontmatter で定義した Hooks は、skill が呼び出された時点で登録され、skill 自身のターンが終わった後もセッションの残り全体で発火し続ける**。初回の成功後に外したい場合は `once: true` を付ける（[Skills ガイド](skills.md) / [SubAgents ガイド](sub-agents.md) 参照）。以前は「Skill / Subagent とも、そのコンポーネントが動作している間だけ有効で、終了時にクリーンアップされる」と書いていたが、現行公式では Skill 側は該当しない。出典: [Hooks — Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)
>
> **v2.1.218 の trust ゲート**: **agent frontmatter の hooks は、その agent ファイル自身が置かれているフォルダの workspace trust が承認済みであることを要求する**ようになった。untrusted なフォルダから持ち込まれた agent 定義が hook を勝手に実行するのを防ぐための変更である。外部リポジトリの `.claude/agents/` をそのまま流用している場合、trust 承認まで hook が発火しない。現行公式では、**agent frontmatter の hook に限っては `-p` による暗黙の trust を承認とみなさない**（project の subagent の frontmatter hook は `-p` では動かない。settings ファイルの hook の扱いは次の注記のとおり逆である）。出典: CHANGELOG v2.1.218 / [Hooks — Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)
>
> **settings ファイルの hook と workspace trust**（2026-11-01 追記）: ClaudeCode は settings ファイルの hook を動かす前に workspace trust を確かめる。対話セッションでは、自分の `~/.claude/settings.json` を含む**すべての settings ファイルの hook**を、そのフォルダ（または trust が及ぶ親ディレクトリ）の trust ダイアログを承認するまで止めておく。一方 **`-p` / SDK のセッションはダイアログを出さずにフォルダを trusted とみなす**ため、リポジトリに commit された `.claude/settings.json` の hook が、一度も trust していないフォルダでも動く。他人のリポジトリに `claude -p` を流す前に `.claude/` の settings を確認するか、`--bare` で起動するか、`--settings '{"disableAllHooks": true}'` でその回だけ hook を止める。project の skill の frontmatter hook は settings ファイルと同じ規則に従い、trust していないフォルダの `-p` でも skill の呼び出し時に登録される。出典: [Hooks — Workspace trust](https://code.claude.com/docs/en/hooks#workspace-trust) / [Hooks — Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)
>
> **skill hook の上限**（v2.1.304〜）: skill の出どころ（project・個人の skills フォルダ・plugin ごと）ごとに、1 セッションで登録できる hook は **1,024 個**、その matcher の合計は **16,384 文字**までである（1 つの matcher の下に複数の hook があれば hook ごとに数える）。上限を超えた skill は frontmatter の hook を 1 つも登録せずに動き、debug ログに `registers none of its hooks` が出る。また managed の `strictPluginOnlyCustomization` で hook が plugin と managed settings に限られている場合、plugin の skill・bundled skill・managed settings ディレクトリの skill 以外は frontmatter の hook を失う（v2.1.304 からは、main の会話で使う skill の hook が外されると、その skill の `allowed-tools` も効かなくなった）。出典: [Hooks — Limits on skill hooks](https://code.claude.com/docs/en/hooks#limits-on-skill-hooks) / CHANGELOG v2.1.304
>
> **cloud セッションと subagent**（2026-11-01 追記）: cloud セッションはローカルの `~/.claude/settings.json` を読まないため、そこに書いた hook は動かない。settings ファイル・managed policy settings・plugin の hook は subagent の中でも動き、subagent のツール呼び出しで `PreToolUse` / `PostToolUse` などが main の会話と同じく発火する（入力の `agent_id` / `agent_type` で subagent を見分ける）。managed settings の `allowManagedHooksOnly` は user / project / local / plugin の hook を止める（managed の `enabledPlugins` で強制有効化された plugin の hook は除く）。出典: [Hooks — Hook locations](https://code.claude.com/docs/en/hooks#hook-locations)
>
> **plugin hook の失敗時の扱い（v2.1.299）**: CHANGELOG v2.1.299 は「plugin hook がブロックしうるアクションは、hook に渡せない・hook から答えを受け取れない場合に、通さずに拒否する。実行済みのツールは結果を伏せる」「plugin hook が返す値の入れ子が 28,000 段を超えると、上限を示すエラーで拒否する」と書く。値の受け渡しの記述からは mod（関数 hook）を指すとみられるが、CHANGELOG は対象を明記していない。出典: CHANGELOG v2.1.299

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
| `matcher` | フィルタ。完全一致 / `\|` 区切り / **カンマ区切り**(v2.1.191〜、空白許容) / 正規表現（例: `Bash`、`Edit\|Write`、`Edit,Write`、`mcp__memory__.*`、`*` で全マッチ）。**v2.1.195 でハイフンを含む matcher は exact-match に変更**(以前は unanchored regex で部分一致していた)。⚠️ **ただし一律ではない**（**2026-09-03 訂正**）: **`FileChanged` と `StopFailure` は「対象外」ではなく、より狭い exact-match 集合を使う** — **英数字・`_`・`\|` のみ**が exact-match として扱われ、**ハイフン / 空白 / カンマが入ると正規表現の経路に戻る**。またこの 2 イベントでは**区切りは `\|` だけ**である（カンマ区切りは効かない）。<br>⚠️ 旧記述は「この exact-match 化の対象外で、従来どおり正規表現として評価される」としていたが誤り。<br>一部イベントは matcher 非対応（`UserPromptSubmit` / `PostToolBatch` / `Stop` / `TeammateIdle` / `TaskCreated` / `TaskCompleted` / `WorktreeCreate` / `WorktreeRemove` / `MessageDisplay` / `CwdChanged`） |
| `type` | ハンドラ種別。`command` / `http` / `mcp_tool` / `prompt` / `agent`（`agent` は **experimental** で、挙動・設定が今後変わりうる） |
| `if` | 任意。パーミッションルールでさらに絞る（例: `Bash(git *)`、`Edit(*.ts)`）。⚠️ **ツール系 5 イベント（`PreToolUse` / `PostToolUse` / **`PostToolUseFailure`** / `PermissionRequest` / **`PermissionDenied`**）でのみ有効**（**2026-09-03 訂正**）。**それ以外のイベントに `if` を付けると、その hook は一切発火しなくなる**。<br>⚠️ **旧記述の訂正**: 以前は有効イベントに `SubagentStart` / `SubagentStop` を挙げていたが**誤り**で、この 2 つは対象外である（`if` 付きの hook を書くと永久に発火しない）。逆に `PostToolUseFailure` / `PermissionDenied` が漏れていた。公式原文は「Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied`. On other events, a hook with `if` set never runs.」 |
| `timeout` | 秒。既定は **`command` / `http` / `mcp_tool` = 600、`prompt` = 30、`agent` = 60**。**イベント別の例外**: `UserPromptSubmit` / **`PreModelSwitch`** / **`PostModelSwitch`** では `command` / `http` / `mcp_tool` の既定が **30** に、`MessageDisplay` では **10** に下がる。`SessionEnd` は **1.5 秒の共有バジェット**（設定側でより長い `timeout` を書くとバジェットが最大 60 秒まで引き上げられる。plugin 由来の hook の timeout は引き上げに寄与しない。`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` で明示上書き可）。`async: true` の command hook には timeout が適用されない。v2.1.312 以降、`prompt` / `agent` hook では **1 秒未満の `timeout` は 1 秒として扱われる**（CHANGELOG v2.1.312） |
| `statusMessage` | 実行中のスピナーに出すメッセージ |
| `once` | `true` で、**初回の成功後に** hook を除去する。失敗・exit code 2 でのブロック・timeout に終わった実行では除去されず、次の該当イベントで再び実行される（**2026-10-11 訂正**: 以前は「セッション中 1 回だけ実行して除去」と書いていたが、除去の条件は「成功した実行」である）。⚠️ **skill frontmatter でのみ有効**（2026-08-12 訂正）。`settings.json` や agent frontmatter に書いても**無視される** |
| `onFailure` | **`command` / `http` hook のみ**（v2.1.295〜、公式 docs の記載）。hook が失敗したときにアクションをどうするか。`"continue"`（既定）か `"block"`。詳細は後述の「hook の失敗でアクションを止める（`onFailure`）」 |

**`timeout` 既定値のイベント別例外**:

| イベント | 既定 timeout |
|---|---|
| `UserPromptSubmit` | `command` / `http` / `mcp_tool` を **30 秒**へ引き下げ |
| `MessageDisplay` | **10 秒**へ引き下げ |
| `SessionEnd` | 全 hook で**共有予算 1.5 秒**。settings でより長い per-hook `timeout` を指定した場合、ClaudeCode が予算をそれに合わせて引き上げる（**最大 60 秒**） |

> **hook 出力は 10,000 文字でキャップされる**: `additionalContext` / `systemMessage` / **`initialUserMessage`** / プレーンな stdout の文字列は **10,000 文字**が上限で、超過分は大きなツール結果と同じ扱いでファイルに退避され、**先頭最大 2,000 文字のプレビュー**とファイルパスに置き換えられる。文字列は 1 つずつ測る（同じイベントで複数の hook が動いても合算しない。JSON はフィールドごと、プレーンな stdout は全体で測る）。この上限を引き上げる設定・環境変数は無く、ClaudeCode は退避先ファイルを読むよう Claude に促さない。長い出力を Claude に渡したい場合は、hook 側でファイルに書いてパスだけ返す設計にする（**2026-11-01 更新**: `initialUserMessage` も対象であること・プレビューの長さ・測り方を追記。v2.1.314 では、出力が非常に大きい `PreCompact` hook で compaction が失敗・反復する不具合が直り、hook ごとの出力が 10,000 文字で切られるようになった）。出典: [Hooks — JSON output](https://code.claude.com/docs/en/hooks#json-output) / CHANGELOG v2.1.314
>
> **prompt / agent hook の同時実行数**: マッチした hook は並列に動くが、1 つのイベントで `prompt` / `agent` hook が 12 個を超える場合は、**同時に動くのは 12 個まで**で、残りは空きができ次第始まる（v2.1.302〜）。待っている hook の `timeout` は、その hook が始まった時点から数える。さらに v2.1.312 で、**セッション全体（subagent を含む）で同時に 24 個まで、加えて自分のイベントの timeout より長く待った 12 個まで**に変わった。出典: [Hooks — Hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields) / CHANGELOG v2.1.302 / v2.1.312

> **同一ハンドラの重複排除は settings ファイル間だけ**（**2026-10-11 訂正**）: マッチした hook はすべて並列に実行される。**同じハンドラを複数の settings ファイルに定義した場合は 1 回だけ実行される**が、**plugin や skill が持つ同じハンドラのコピーは別扱い**で、それぞれ実行される。以前は「並列実行時、同じハンドラは自動的に dedup される（`command` は command 文字列 + args、`http` は URL で同一判定）。複数の matcher が同じ hook にヒットしても多重実行されない」と書いていたが、現行公式が述べている重複排除は settings ファイル間のものだけで、同一判定の基準も記載されていない。出典: [Hooks — Hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields)

### ハンドラタイプ

| type | 用途 | 主なフィールド |
|------|------|--------------|
| `command` | 実行ファイル / スクリプトを起動 | `command`, `args`（exec 形式・シェル不使用）, `async`, **`asyncRewake`**, `shell`（`bash`/`powershell`）, **`onFailure`**（v2.1.295〜） |
| `http` | HTTP エンドポイントに POST | `url`, `headers`, `allowedEnvVars`（env 補間に必須）, **`onFailure`**（v2.1.295〜） |
| `mcp_tool` | 接続済み MCP ツールを呼ぶ | `server`, `tool`, `input`（`${tool_input.file_path}` 等で置換） |
| `prompt` | 軽量モデルで判定 | `prompt`（`$ARGUMENTS` = hook 入力 JSON）, `model` |
| `agent` | サブエージェントで検証（**experimental**） | `prompt`, `model` |

> **`agent` hook は experimental で、`PermissionRequest` では動かない**: 公式は agent hook を「experimental で今後変わりうる。本番のワークフローでは command hook を推奨」としている。対応イベントは `prompt` hook と同じだが **`PermissionRequest` だけは除外**で、ここに agent hook を設定してもスキップされ、パーミッションフローは変わらない（v2.1.280 で、agent hook の応答は許可・拒否に使えないため実行しないよう変更され、command / http hook を使うよう促すエラーが出るようになった。出典: CHANGELOG v2.1.280）。`PermissionRequest` で許可・拒否したい場合は command / http hook から `decision` オブジェクトを返す。出典: [Hooks — Agent-based hooks](https://code.claude.com/docs/en/hooks#agent-based-hooks)

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
| `UserPromptSubmit` | プロンプトの送信時（Claude が処理する前）。ユーザーの入力に加え、**scheduled task の発火（`/loop` の各回を含む）・background subagent が起動元セッションへ報告を返す時・他セッションから main の会話へメッセージが届いた時**にも発火する。v2.1.299 以降は **skill / カスタムスラッシュコマンドの展開より前**に走るため、プロンプトをブロックすると、その skill 等に埋め込まれたシェルコマンドも止まる。skill 自身の frontmatter の `UserPromptSubmit` hook は、skill を呼び出したプロンプトの次のプロンプトから動く（CHANGELOG v2.1.299） | **可** |
| `UserPromptExpansion` | ユーザー入力のコマンド展開 | **可** |
| `PreToolUse` | ツール呼び出しの実行前 | **可** |
| `PermissionRequest` | パーミッションダイアログ表示時 | **可**（JSON の `decision` オブジェクトで `behavior: "deny"` を返した場合のみ。**exit code 2 は無視**され、パーミッションフローはそのまま進む） |
| `PermissionDenied` | auto mode がツール呼び出しを拒否（分類器の verdict が出なかった拒否を含む） | 不可（retry 要求は可。ただし**分類器が verdict を出せなかった拒否では `retry: true` は無視**される） |
| `PostToolUse` | ツール呼び出し成功後 | 不可 |
| `PostToolUseFailure` | ツール呼び出し失敗後 | 不可 |
| `PostToolBatch` | 並列ツール呼び出しの解決後 | **可** |
| `Stop` | Claude が応答を終える時 | **可**（停止を阻止し継続。ただし 8 回連続で継続させると次の block は上書きされてターンが終わる。Claude がツールを呼ぶとカウントはリセット） |
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
| **`PreModelSwitch`** | **モデル切替の適用前**（v2.1.251〜）。対象は `/model <name>` と `/model` picker、`Option+P` / `Alt+P` の model picker、`/config` の Model 設定、セッションのモデルが変わる fast mode の有効化、Agent SDK ホストや Remote Control からの `set_model` / `apply_flag_settings` のモデル変更（**2026-11-01 更新**: 2026-10-11 時点は「`/model <name>` と `/model` picker からの切替が対象」と書いていた）。automatic model fallback やセッション再開時のモデル復元など ClaudeCode 自身による切替では動かず、`PostModelSwitch` だけが発火する。**timeout を過ぎて応答しないと切替はブロックされる**（`PreToolUse` と違い、timeout はツール続行にならない） | **可**（切替をブロックできる） |
| **`PostModelSwitch`** | **セッションのモデルが変わった後**（v2.1.251〜） | 不可（async） |
| `Elicitation` | MCP サーバーがユーザー入力を要求 | **可** |
| `ElicitationResult` | MCP elicitation へのユーザー応答 | **可** |
| `WorktreeCreate` | worktree 作成時 | **可**（**非ゼロ exit code すべて**が作成を中止する。exit 2 限定ではない） |
| `WorktreeRemove` | `WorktreeCreate` hook が作った worktree の削除時 | **可**（非ゼロ exit code で、hook 終了後もディレクトリが残っていれば削除は失敗する。**2026-10-11 訂正**: 以前は「不可」と書いていた） |
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
| `SessionEnd` | 終了理由 | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` の **5 値**（**2026-09-03 訂正**）。⚠️ **`bypass_permissions_disabled` は v2.1.234 で削除済み**。公式は「Removed in v2.1.234; Claude Code doesn't send it. **Drop it from your `SessionEnd` matchers**」と明記している。既存の設定に残っていたら外すこと |
| `Setup` | 起動フラグ | **`init`, `maintenance`**(`--init-only` / `--init` / `--maintenance` フラグを判別) |
| `InstructionsLoaded` | ロード分類 | **`session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`** の 5 値 |
| `DirectoryAdded` | 追加経路 | **`slash_command`**(`/add-dir` 経由), **`register_repo_root`**(SDK control request 経由) |
| `StopFailure` | API エラー種別 | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, **`cloud_credential_error`**, `unknown` の **12 値**（**2026-10-11 更新**: `cloud_credential_error` を追加。2026-09-03 時点は 11 値。`cloud_credential_error` での matcher は **v2.1.267〜**（公式 docs の記載）で、それより前はクレデンシャルの読み込み失敗が `server_error` か `unknown` として報告される） |
| `ConfigChange` | 変更された設定ソース | **`user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`** |
| `Notification` | 通知種別 | `permission_prompt`, `auth_success`, `elicitation_dialog`, **`idle_prompt`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`**, さらに **`quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled`**（v2.1.234〜）と、mod が `$.ui.notify` で出す通知の **`plugin_notification`** を加えた **13 値**（**2026-11-01 更新**: `plugin_notification` を追加。2026-09-03〜2026-10-11 時点は 12 値、2026-08-12 時点は 9 値、それ以前は 3 値と書いていた）。⚠️ **v2.1.232 以前は、Claude Desktop / VS Code 配下で動かした場合に `permission_prompt` で発火しない不具合があった**（v2.1.233 で修正。2026-08-16 追記） |
| `SubagentStart` / `SubagentStop` | エージェント種別 | `general-purpose`, `Explore`, `Plan` に加え、**カスタム agent 名**および **plugin スコープ名**（`^my-plugin:reviewer$` のように正規表現で書ける） |
| `PreCompact` / `PostCompact` | トリガー | `manual`, `auto` |
| **`PreModelSwitch` / `PostModelSwitch`** | **切替先モデルの正規名**（`[1m]` の接尾辞は無視。alias・日付付き ID・Bedrock 等の provider 固有 ID も解決先の正規名で照合される） | `claude-opus-5`、`claude-opus-4-6\|claude-opus-5`、`.*opus.*` のように指定する（v2.1.251〜。**2026-11-01 更新**: 例を公式の `claude-opus-4-6\|claude-opus-5` に合わせた。2026-10-11 時点は `claude-opus-4-6\|claude-opus-4-8` と書いていた）。正規名が決まらない切替先（LLM gateway だけが知る custom model ID 等）では matcher に関係なく全 hook が動くため、ブロックする hook は入力の `to_model` も確かめる |
| `FileChanged` | 監視ファイル名 | `.envrc\|.env`（リテラル） |
| `Stop` / `UserPromptSubmit` / `MessageDisplay` 等 | matcher 非対応 | 常時発火 |

> **`SessionStart` の `fork` source（v2.1.214〜）**: fork 起点のセッション開始は、従来 `resume` に含まれていたが **`fork` として独立**した。`fork` が渡るのは ① `--fork-session` + `--resume` / `--continue`、② `/fork` による background コピー、③ `/branch` の 3 経路。「resume 時だけ環境を復元する」hook を書いている場合、**fork 時に発火しなくなる**ため matcher の見直しが必要である。出典: [Hooks](https://code.claude.com/docs/en/hooks) / CHANGELOG v2.1.214

> **`if:` 条件での single-segment glob の扱い（v2.1.214〜）**: hook の `if:` 条件では **`"Edit(src/**)"` が `<cwd>/src` のみにマッチ**する。任意の深さに効かせたい場合は `"Edit(**/src/**)"` と書く。**permission ルールの deny / ask は任意深さのまま**なので、同じ記法でも hook 側と挙動が異なる点に注意する（`docs/config-files.md`「permission ルールの重要な変更」参照）。

> **Monitor ツールと Bash の hook（v2.1.314）**: Monitor ツールが起動するシェルコマンドに、`Bash` に matcher を合わせた hook が動かなかった不具合が直った。ただしこれらの hook は Monitor のコマンドを**ブロック・`ask` にはできても、承認・書き換えはできない**。併せて、`Monitor(tail *)` のような `if:` 条件が、`Bash(tail *)` が Bash に対して合うのと同じく Monitor のシェルコマンドに合うようになった。出典: CHANGELOG v2.1.314

---

## 入力と出力

### 共通入力フィールド

Hooks は stdin で JSON を受け取る。共通フィールドの主なもの:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "scratchpad_dir": "/tmp/claude-1000/-home-user-my-project/abc123/scratchpad",
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

> **`scratchpad_dir`（v2.1.257〜、公式 docs の記載）**: セッションの scratchpad ディレクトリ（Claude が一時的な作業ファイルを置く場所）のパス。セッションに scratchpad が無い場合や temp ディレクトリが使えない場合は含まれない。hook から Claude の一時ファイルを参照・掃除したい場合に使う。
>
> **`permission_mode` の `"default"`**: UI で **Manual** と表示されるモードは `"default"` として届き、`"manual"` にはならない（`"default"` を判定している既存スクリプトはそのまま動く）。また、この field を受け取らないイベントもある。出典: [Hooks — Common input fields](https://code.claude.com/docs/en/hooks#common-input-fields)

### exit code の挙動

| exit code | 意味 | 効果 |
|-----------|------|------|
| `0` | 成功 | stdout の JSON 出力を処理する |
| `2` | ブロッキングエラー | アクションをブロックし、stderr を Claude に渡す。stdout の JSON が schema validation を通っても、その fields でブロックを覆すことはできない |
| `1` / その他 | 非ブロッキングエラー | hook エラー通知を出して実行は継続。**ただし stdout の JSON が schema validation を通った場合は「成功」扱いになり、exit code は無視されて JSON の fields だけで結果が決まる**（`onFailure: "block"` を設定した hook では失敗として数える） |

exit code 2 の効果はイベント依存（`PreToolUse`=ツール呼び出しをブロック、`UserPromptSubmit`=プロンプトをブロックしコンテキストから消去、`Stop`=停止を阻止し会話継続、`PreCompact`=コンパクションをブロック など）。**`PermissionRequest` では exit code 2 は無視され**（stderr も捨てられる）、拒否するには `decision` オブジェクトを返す必要がある。

> **2026-10-11 追記**: 「exit 1 でも stdout の JSON が有効なら成功扱い」になる点は、exit code だけで成否を判定するつもりのスクリプトで見落としやすい。たとえば `PreToolUse` hook が exit 1 で終了しても、`permissionDecision` を含む有効な JSON を出していれば、その JSON の判定が適用される。出典: [Hooks — Exit code output](https://code.claude.com/docs/en/hooks#exit-code-output)

> **v2.1.214 の修正**: exit code 2 を返した hook が、**stdout の JSON が schema validation に失敗した場合にブロックしなかった**不具合が修正された。現在はドキュメント通り、JSON が不正でも exit code 2 は確実にブロックする。exit code 2 をガードレールとして使っている hook は、この version 以前では**すり抜けていた可能性がある**点に注意する。出典: CHANGELOG v2.1.214

#### hook の失敗でアクションを止める（`onFailure`）

多くのイベントでは、hook が失敗・timeout しても ClaudeCode はアクションを続行する。そのため、パスを書き間違えたポリシー hook やクラッシュするスクリプトは**すべてを素通しにする**。これを防ぐには、`command` / `http` hook に **`"onFailure": "block"`** を設定する（既定は `"continue"`。v2.1.295〜、公式 docs と CHANGELOG v2.1.295 の記載）。

```json
{
  "type": "command",
  "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.js",
  "onFailure": "block"
}
```

失敗として数えるのは次の 5 つ:

| 失敗の種類 | 内容 |
|---|---|
| 起動できない | スクリプトや実行ファイルが存在しない等で command hook が起動しない |
| 0 / 2 以外の exit code | command hook では、`permissionDecision: "allow"` のような許可の JSON を出していても失敗扱い（JSON で判定を返すなら exit 0 にする） |
| HTTP エラー | http hook の接続失敗、または 2xx 以外のステータス |
| timeout | hook が `timeout` に達した |
| 不正な出力 | JSON が parse できない、または schema validation に失敗した（command hook のプレーンテキスト stdout は失敗ではない） |

`"block"` のときの失敗は、**そのイベントで exit code 2 が起こすのと同じ効果**を持つ（`PreToolUse` ならツール呼び出しをブロック、`UserPromptSubmit` ならプロンプトをブロック）。例外として `PermissionRequest` では要求を拒否する。一方、**`Stop` / `SubagentStop` / `TaskCompleted` / `TeammateIdle` の hook と、`async` / `asyncRewake` を付けた background command hook には効果がない**（前者は exit 2 が「作業を続けさせる」意味になり、動かない hook を Claude が直せないため）。出典: [Hooks — Block the action when a hook fails](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)

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
| `suppressOutput` | 全般 | **効果なし**。ClaudeCode は field を受け付けるが何もしない。成功した hook の stdout はもともとトランスクリプトに表示されず、debug ログに記録される（**2026-10-11 訂正**: 以前は「stdout をトランスクリプトから隠す」と書いていた） |
| `systemMessage` | 全般 | ユーザー向け警告を表示 |
| `additionalContext` | 多くのイベント | Claude に追加コンテキストを注入 |
| `permissionDecision` | `PreToolUse` | `allow` / `deny` / `ask` / `defer` |
| **`decision`（オブジェクト）** | **`PermissionRequest`** | `{ "behavior": "allow" \| "deny", "updatedInput": {...} }` の形で返す。**`PreToolUse` の `permissionDecision` とはフィールド名・形が異なる**点に注意（`PermissionRequest` で `permissionDecision` を返しても効かない）。Cowork の cloud セッションでは、allow に含めた `setMode` の更新は無視される（v2.1.300）。また Cowork の cloud セッションの auto mode では、`PermissionRequest` hook はシェルコマンドと subagent を承認できない（v2.1.299）。出典: CHANGELOG v2.1.299 / v2.1.300 |
| `updatedInput` | `PreToolUse` | ツール入力（引数）を書き換える。※旧称ではなく現行公式のフィールド名。入力オブジェクト全体を置き換えるため、変えないフィールドも含めて返す。パーミッションルールは hook が返した入力に対して評価される。v2.1.300 以降、`PreToolUse` / `PermissionRequest` の `updatedInput` は **Claude 自身の入力と同様に検証される**（未知のキーは捨てられ、ツールが受け付けない入力なら呼び出しは拒否される。CHANGELOG v2.1.300） |
| `updatedToolOutput` | `PostToolUse` | ツールの実行結果（出力）を差し替える |
| `displayContent` | `MessageDisplay` | 画面表示テキストを差し替える |
| `decision` | `Stop` 等 | `block` で停止を阻止し会話継続 |
| `retry` | `PermissionDenied` | `true` で、拒否されたツール呼び出しの再試行をモデルに許可する（`PermissionDenied` は exit code / stderr が無視されるため、retry は JSON のこのフィールドで要求する）。拒否そのものは覆らず、「再試行してよい」というメッセージが会話に足されるだけ。**分類器が verdict を出せなかった拒否（応答が parse できない等）では無視される** |
| `reloadSkills` | `SessionStart` | hook 実行後にスキルを再スキャン（スキルをインストールする hook が同セッションで有効化される） |
| `sessionTitle` / `watchPaths` / `initialUserMessage` | `SessionStart` | セッション名変更 / `FileChanged` 監視パス / `-p` モードの初回メッセージ |
| `terminalSequence` | 多くのイベント | 端末エスケープシーケンス（OSC）を発行。デスクトップ通知（OSC 9 / 99 / 777）・ウィンドウ/アイコンタイトル（OSC 0 / 1 / 2）・タスクバー進捗（OSC 9;4）・ベル（BEL）に使う。許可された OSC と BEL に制限（カーソル移動・色破壊を防ぐ、v2.1.141〜） |

> **`SessionStart` の `additionalContext`** は、セッション開始時に「現在のブランチ・未解決 issue 数・直近のデプロイ状況」などを Claude に自動投入する用途で有用。**`reloadSkills: true`** と組み合わせれば、スキルを動的に取得・有効化する hook を 1 セッション内で完結できる。

### Stop / SubagentStop の additionalContext

`Stop`・`SubagentStop` は `hookSpecificOutput.additionalContext` を返せる。これは**エラーではないフィードバック**で、**会話は継続し**、Claude がその内容に対応する（例: 「終了前にテストスイートを実行して」）。`decision: "block"` と同じループ保護（`stop_hook_active` 入力と後述の 8 連続上限）を通るが、トランスクリプトには hook エラーではなく `Stop hook feedback` として表示され、hook エラー通知も出ない。hook が想定どおり動いていて Claude に指示を与えたい場合は `additionalContext`、条件未達で止めたい場合は `decision: "block"` を使い分ける。

**2026-10-11 訂正**: 以前は「`decision` を省略すれば、ターンを完了させつつフィードバックだけ追加できる」と書いていたが誤りで、`additionalContext` を返すとターンは終わらず継続する。出典: [Hooks — Stop decision control](https://code.claude.com/docs/en/hooks#stop-decision-control)

### Stop hook の 8 連続上限(セーフティネット)

Stop hook は `decision: "block"`（または `additionalContext`）でターン継続を強制できるが、**stop hook が 8 回連続でターンを継続させると、ClaudeCode は次の block を上書きしてターンを終了する**。**連続回数のカウントは Claude がツールを呼ぶたびにリセットされる**ため、ツールを使いながら作業が進んでいる限り上限には達しない。上限は環境変数 **`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`** で引き上げられる。無限ループで Claude を停止不能にしないためのセーフティネットである。「Hooks は決定論的で必ず実行される」原則は Stop hook に関して条件付きになる点に注意。決定論性を厳密に担保したい制御は `PreToolUse` の `permissionDecision: "deny"` を使う（ただし後述のとおり、組込みのガードが働かない環境では、`PreToolUse` hook のブロックを mod の `tool.check` が覆しうる）。出典: [Hooks — Stop input](https://code.claude.com/docs/en/hooks#stop-input)（**2026-10-11 張替え**: 以前の出典は Best practices の Verification loops 節だった）。

---

## PreToolUse のパーミッション制御

`PreToolUse` hook はツール実行の可否を制御できる。

| `permissionDecision` | 挙動 |
|---------------------|------|
| `allow` | プロンプトなしで承認（ただし settings の deny / ask ルールは引き続き評価される。どのモードでも自動承認されない操作・ネットワークパスの読み取り・`AskUserQuestion` / `ExitPlanMode` もプロンプトを省略できない。`AskUserQuestion` / `ExitPlanMode` は `"allow"` と `updatedInput` を組にすれば通る）。**2026-11-01 追記**: ほかに `requiresUserInteraction` を付けた MCP ツール、組織が `ask` に設定した connector ツール（その設定が届くセッション）、Agent SDK アプリが `always_ask` にしたツール（permission mode が承認する場合を除く）も `allow` でプロンプトを省略できない。**plan mode では、`ExitPlanMode` 以外の読み取り専用でない呼び出し（ファイル編集など）への `allow` は効かず**、hook が無い場合と同じプロンプト・ブロック・承認になる（`updatedInput` は適用される）。v2.1.299 で、plan mode で hook や mod の allow が書き込みを通してしまう不具合が直った。また Cowork の cloud セッションの auto mode では、MCP ツール呼び出しへの hook の allow は「答え無し」として扱われ、分類器かプロンプトが決める（v2.1.314） |
| `deny` | ツール呼び出しをブロック |
| `ask` | ユーザーのパーミッションプロンプトにエスカレート |
| `defer` | **`-p`（非対話モード）専用**。ツールを実行せずにプロセスを `stop_reason: "tool_deferred"` で終了し、保留中のツール呼び出しをトランスクリプトに残す。`claude -p` を subprocess として動かす Agent SDK アプリや独自 UI が、自前の UI で入力を集めてから resume するための値。**対話セッションでは警告をログに出して無視される**。1 ターンに複数のツール呼び出しがある場合も無視され、通常のパーミッションフローに進む |

> **`defer` の訂正**（**2026-10-11**）: 以前は `defer` を「通常のパーミッションフローに委ねる」と書いていたが、現行公式では上記のとおり `-p` 専用の「一時停止して後で resume する」値である。複数の `PreToolUse` hook が異なる判定を返した場合の優先順位は `deny` > `defer` > `ask` > `allow`。出典: [Hooks — Defer a tool call for later](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later)

`migrations/` への書き込みをブロックする例（自然言語で Claude に依頼すれば hook を構成してくれる）:

> migrations フォルダへの Write/Edit をブロックする PreToolUse hook を書いて。

> **`ask` が auto mode に上書きされなくなった（v2.1.211）**: 従来は auto mode 配下で hook の `ask` 判定が分類器の自動承認に飲まれることがあったが、**hook の `ask` が最低保証としてプロンプトを出す**ようになった。auto mode で運用しつつ「特定操作だけは必ず人間に確認させる」ガードレールが hook で確実に組める。
>
> **2026-11-01 追記（例外）**: 現行公式では、auto mode の `ask` は通常プロンプトへ回り分類器は判定しないが、次の 2 つは別の経路を通る。① **ClaudeCode 自身のチェックにも掛かる呼び出し**（protected paths への書き込み、sandbox の外での実行を求めるコマンドなど）は、プロンプトが出る前に分類器が deny しうる（分類器が承認すれば通常どおりプロンプトへ回る）。② **`SubagentHandback`**（subagent が報告を返すツール）はプロンプトが出ず、分類器が反対しても実行される。止めたい場合は `"deny"` を返す（ClaudeCode が subagent に最大 3 回再呼び出しを促し、それでも拒否が続けば報告は届かず、待っている会話にその旨の注記が入る）。したがって上の「最低保証」は無条件ではない。出典: [Hooks — PreToolUse ask decisions in auto mode](https://code.claude.com/docs/en/hooks#pretooluse-ask-decisions-in-auto-mode)
>
> 併せて **v2.1.212** で、`continue: false` による halt が **ツール失敗時や mid-stream 完了時に効かなくなる**不具合が修正されている。出典: CHANGELOG v2.1.211 / v2.1.212

> **⚠️ mod の `tool.check` は、ガードの無い環境では `PreToolUse` hook のブロックを覆しうる**（2026-10-11 追記、**2026-11-01 更新**）: settings ファイルと plugin の `hooks/hooks.json` の hook は、パーミッションを**締めることはできても緩めることはできない**。ところが mod（前述「Hooks と Mods の関係」）が `tool.check` イベントを扱うと、その判定は**パーミッションルールと settings の `PreToolUse` hook が判定した後**に出される。覆せる範囲は、組込みのガード（`sec-default@builtin`）が働くかどうかで変わる。
>
> - **ガードが働く環境**（managed settings があるマシン、またはセッションの資格情報が Team / Enterprise の `/login`）: 既定では、deny ルールで拒否された呼び出しは拒否のまま（組織は変更可）、ask ルール・`PreToolUse` hook・`permissions.blockReadsOutsideWorkingDirectories` でプロンプトが出る呼び出しはプロンプトが出たまま、**どの settings ファイルの `PreToolUse` hook がブロックした呼び出しもブロックのまま**、`--permission-prompt-tool` / Agent SDK の `canUseTool` に問い合わせる呼び出しは問い合わせたままになる
> - **ガードが無い環境**（managed settings が無く、Team / Enterprise の `/login` でもない。API キーや `CLAUDE_CODE_OAUTH_TOKEN` のセッションは、その login が保存されていても該当する）: ユーザーが入れた mod は、deny ルールで拒否された呼び出しも、`PreToolUse` hook がブロックした呼び出しも承認でき、ask ルール等のプロンプトも省略させられる
> - **どの環境でも**: auto mode では mod が承認した呼び出しは分類器のチェックを通らない（ガードが働き、`--permission-prompt-tool` か `canUseTool` を使うセッションでは分類器が先に審査する）。plan mode では、mod は読み取り専用でない呼び出しを承認できない（ブロックはできる）。`AskUserQuestion` や `requiresUserInteraction` の MCP ツールなど、ユーザーの操作を要するツールのプロンプトは mod の承認では省略できない（v2.1.292〜）
> - **managed settings の `PreToolUse` hook** は最初の mod の `tool.call` より前に実行され、そのブロックは最終で、どの mod も覆せない。mod が呼び出しを書き換えた場合は、書き換え後の呼び出しに対して managed hook がもう一度動く
> - managed 以外の `PreToolUse` hook は最後の mod の後に動く。`tool.call` を `next` を呼ばずに処理した（自分で答えた）mod があると、ツールは実行されず、managed 以外の `PreToolUse` hook も実行されない
>
> 2026-10-11 時点は環境による違いを書かず、「managed settings 以外（user / project / local / plugin）の `PreToolUse` hook がブロックした呼び出しを、ユーザーが入れた mod は承認できる。ask ルールで確認が出るはずの呼び出しも承認できる」としていた。現行公式では、これはガードの無い環境だけに当てはまる。
>
> 「hook で必ず止める」前提のガードレールを組織で強制したい場合は managed settings を配る（ガードが働く）か managed settings に hook を置くか、mods 側を `allowManagedModsOnly` 等で制限する。出典: [Configure permissions — Precedence among rules, hooks, and mods](https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods) / [Configure permissions — Hook approvals in plan mode](https://code.claude.com/docs/en/permissions#hook-approvals-in-plan-mode) / [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) / [Mods — React to events](https://code.claude.com/docs/en/plugins/mods/events) / [Get started with hooks](https://code.claude.com/docs/en/hooks-guide)

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

- **`/hooks`**: 設定済み Hooks の読み取り専用ブラウザを開く。**v2.1.286 以降は、設定済みの hook をイベントごとにまとめた 1 つのリストで開き**、1 回の Enter で hook の詳細に入れる（以前は 3 段階の操作が必要だった。出典: CHANGELOG v2.1.286）。各 hook には出どころ（user settings / project settings / local settings / plugin / 現在のセッション）のラベルが付き、選ぶと実行内容の全文と定義場所（settings ファイルのパスや plugin 名）が見られる。hook が無いイベントも含めて全イベントを見たい場合は、リスト末尾の `All events` を選ぶ。**2026-10-11 訂正**: 以前は「イベントごとの件数・matcher・ハンドラ・ソース（User / Project / Local / Plugin / Session / Built-in）」を確認できると書いていたが、v2.1.286 で画面構成が変わり、現行公式のラベルに Built-in は無い。
- **`disableAllHooks: true`**: hook・カスタム status line・カスタム file suggestion コマンドをまとめて止める。効く範囲は**どの settings ファイルに書いたか**で変わる。

| `disableAllHooks` を書いた場所 | 止まるもの | 動き続けるもの |
|---|---|---|
| managed settings | managed を含む全 settings hook、全 plugin の mods（組織の mod を含む） | Agent SDK がプロセス内で登録した hook（v2.1.242〜、公式 docs の記載）、ClaudeCode 組込みの mod |
| Agent SDK の `managedSettings` オプション（v2.1.309〜） | user / project / local / plugin の hook、SDK の `settings` オプションの hook。管理者が managed settings を配っているマシンでは、管理者が埋め込みホストによる policy の追加を許可していない限り、このキーは無視される | 管理者の managed hook、強制有効化された plugin の hook、SDK の hook callback（mods への効果は公式に記載なし） |
| それ以外（user / project / local） | user / project / local / plugin の hook、ユーザーが入れた mods | managed hook、Agent SDK の hook、managed の `enabledPlugins` で強制有効化された plugin の hook、組織の mods、組込みの mod |

> hooks が無効な間は **`/goal` が使えず**、`/hooks` は hook の代わりに通知を表示する。settings の優先順位が適用されるため、project の `.claude/settings.json` に `"disableAllHooks": false` があると user settings の `true` を上書きする。プロジェクト設定に関係なく 1 回の実行だけ止めたい場合は `--settings '{"disableAllHooks": true}'` を渡す。個々の hook を設定に残したまま無効化する手段は無い。**2026-10-11 訂正**: 以前は「全 Hooks を無効化（managed policy hooks は対象外）」とだけ書いていたが、status line・file suggestion・mods にも及ぶことと、managed 以外に動き続けるものがあることが漏れていた。**2026-11-01 追記**: Agent SDK の `managedSettings` オプションに書いた場合の行を足した（v2.1.309）。出典: [Hooks — Disable or remove hooks](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks) / [Settings reference — `disableAllHooks`](https://code.claude.com/docs/en/settings-reference#disableallhooks)

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

保護したいパスや危険コマンドを `PreToolUse` の `permissionDecision: "deny"` でブロックする。auto mode の安全網に加えて、プロジェクト固有の禁止事項を決定論的に強制できる。ただし組込みのガードが働かない環境（managed settings が無く、Team / Enterprise の `/login` でもない）で mods を入れている場合は、`PreToolUse` hook のブロックを mod の `tool.check` が承認で覆しうる（「PreToolUse のパーミッション制御」の注記参照）。スクリプトのパス誤りやクラッシュで素通しにしないよう、ガードレール用の hook には `"onFailure": "block"` を付けておく。

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
- [Mods ガイド](mods.md) — 関数 hook を持つ plugin（mods）。`tool.check` と settings hook の関係
- [ハーネス設計ガイド](harness.md) — Hooks による簡易フィードバックループ
