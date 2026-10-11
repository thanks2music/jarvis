# ClaudeCode Skills ガイド

> 出典: [Extend Claude with skills](https://code.claude.com/docs/en/skills) / [Extend Claude Code](https://code.claude.com/docs/en/features-overview) / [Commands](https://code.claude.com/docs/en/commands) / [Model configuration](https://code.claude.com/docs/en/model-config) / [What's new — Week 34](https://code.claude.com/docs/en/whats-new/2026-w34) / [What's new — Week 36](https://code.claude.com/docs/en/whats-new/2026-w36) / [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。公式 skills / commands ページを再照合し、配置スコープ (Nested / Additional directory / claude.ai account)・frontmatter の命名規則・置換変数の置換範囲・バンドルスキル 20 件・`/skill-doctor`・commit 前の `verify` / `simplify` 実行を反映済み)

Skills は ClaudeCode の拡張機能であり、`SKILL.md` ファイルにマークダウンで記述した「ドメイン知識」や「再利用可能なワークフロー」を Claude に与える仕組みである。CLAUDE.md が毎セッション常時読み込まれるのに対し、Skills は**必要な時だけオンデマンドでロード**される。

Skills は [Agent Skills](https://agentskills.io) オープンスタンダードに準拠しており、ClaudeCode 独自の拡張（呼び出し制御・サブエージェント実行・動的コンテキスト注入）も備える。

---

## 前提知識

Skills を効果的に使うために理解しておくべき概念を整理する。

### コンテキストウィンドウとの関係

| 項目 | ロードタイミング | コンテキストコスト |
|------|----------------|-------------------|
| CLAUDE.md | セッション開始時 | 毎リクエスト（全文） |
| Skills（description） | セッション開始時 | 毎リクエスト（低コスト） |
| Skills（本文） | 呼び出し時のみ | 呼び出し後のリクエスト |
| MCP サーバー | セッション開始時 | ツール名のみ（完全な schema は使う時に取得）。tool search が既定 ON のため、ツールを使うまでは低コスト |
| Subagent | 起動時 | メインセッションから隔離 |
| Hooks | トリガー時 | ゼロ（外部実行） |

> **2026-10-11 訂正**: MCP の行は以前「毎リクエスト（ツール定義）」としていたが、現行公式 [Extend Claude Code](https://code.claude.com/docs/en/features-overview) は「Tool names; full schemas on demand」「Low until a tool is used」とする。Skills の description は `disable-model-invocation: true`（自作スキル）か `skillOverrides`（他人のスキル）でコンテキストから外せる。

**重要**: Skills の description リスト全体は **モデルコンテキストの 1%** を予算としてロードされる（`skillListingBudgetFraction` 既定 `0.01`、`SLASH_COMMAND_TOOL_CHAR_BUDGET` で固定文字数指定も可）。個別の description（+ `when_to_use`）は **1,536 文字でキャップ**される（**`skillListingMaxDescChars`** で変更可。⚠️ 2026-08-12 訂正: 旧記載の `maxSkillDescriptionChars` は存在しないキー名だった）。スキル数が多く予算を超えると、使用頻度の低いスキルの description から削られる（スキル名はすべて残る）。overflow の確認は **`/doctor`** で行う（旧記述の `/context` ではない。予算超過時は `--debug` のデバッグログにも警告が出る）。OFF にする候補を探すには **`/skill-doctor`**（後述「[スキル数の管理](#スキル数の管理)」）を使う。**v2.1.196 で `/context` の Skills 行が post-budget size(モデルが実際に見るサイズ)を表示するようになった**ため、以前より正確に把握できる(旧版は overcount していた)。

> **auto-compaction 時のスキル引き継ぎ**: コンテキスト自動圧縮（compaction）が走ると、各スキルの最新 invocation が要約後に再添付される。引き継ぎ量には上限があり、**各スキル先頭 5,000 トークン / 合算 25,000 トークン**まで（長時間セッションで多数のスキルを呼んでいると、この上限で一部が落ちる点に留意する）。

### CLAUDE.md / Rules / Skills の使い分け

| 機能 | ロードタイミング | スコープ | 最適な用途 |
|------|----------------|---------|-----------|
| CLAUDE.md | 毎セッション | プロジェクト全体 | コーディング規約、ビルドコマンド |
| `.claude/rules/` | 毎セッション or ファイルパス一致時 | ファイルパス単位で限定可能 | 言語別・ディレクトリ別ガイドライン |
| Skills | オンデマンド | タスク単位 | リファレンス資料、再利用ワークフロー |

**判断基準**: 「毎セッション必要か？」→ Yes なら CLAUDE.md。「特定ファイル操作時だけ？」→ Rules。「必要な時だけ？」→ Skills。CLAUDE.md は 200行以下を目安に保ち、肥大化したらリファレンス内容を Skills に移す。

### Skills と類似機能の比較

| 比較軸 | Skill | Subagent | MCP |
|--------|-------|----------|-----|
| 何であるか | 再利用可能な指示・知識 | 隔離されたワーカー | 外部サービスとの接続 |
| 主な利点 | コンテキスト間で共有可能 | コンテキスト隔離 | 外部データ・アクション |
| 最適な用途 | リファレンス、ワークフロー | 大量ファイル読み込み、並列作業 | DB クエリ、Slack 投稿 |

**組み合わせ**: MCP がサービスへの接続を提供し、Skill がその使い方を教える。例えば、MCP でデータベースに接続し、Skill でスキーマやクエリパターンを Claude に教える。

---

## Skills の基本

### ディレクトリ構造

各 Skill は独立したディレクトリで、`SKILL.md` がエントリポイントとなる。

```
my-skill/
├── SKILL.md           # メインの指示（必須）
├── template.md        # Claude が埋めるテンプレート（任意）
├── examples/
│   └── sample.md      # 期待する出力例（任意）
├── references/
│   └── api-spec.md    # 詳細リファレンス（任意）
└── scripts/
    └── validate.sh    # Claude が実行するスクリプト（任意）
```

`SKILL.md` は 500行以下に保ち、詳細なリファレンスは別ファイルに分離する。`SKILL.md` から相対パスでリンクし、Claude が必要に応じて読み込めるようにする。

### 配置場所とスコープ

| スコープ | パス | 適用範囲 |
|---------|------|---------|
| Enterprise | [managed settings ディレクトリ](https://code.claude.com/docs/en/managed-settings#delivery-mechanisms)内の `.claude/skills/<skill-name>/SKILL.md` | 組織が配布したマシンの全ユーザー |
| Personal（個人） | `~/.claude/skills/<skill-name>/SKILL.md` | このマシンの全プロジェクト。**Cowork / cloud セッションでは読まれない** |
| Project（プロジェクト） | `.claude/skills/<skill-name>/SKILL.md` | 当該リポジトリのセッション。commit すればチームにも届く |
| Nested | `<subdir>/.claude/skills/<skill-name>/SKILL.md` | `<subdir>` 以下で開始したセッション。より上で開始したセッションでは、Claude がそこのファイルを触った時点でロードされる |
| Additional directory | `--add-dir` で渡したディレクトリの `.claude/skills/<skill-name>/SKILL.md` | そのセッション |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Plugin が有効な場所（`/plugin-name:skill-name`） |
| claude.ai account | claude.ai アカウントで有効にしたスキル | Cowork / cloud セッションと、そのアカウントでログインしたターミナルセッション（v2.1.273〜。後述） |

> **2026-10-11 更新**: Nested / Additional directory / claude.ai account の 3 行を追加し、Enterprise のパスを公式表記に合わせた。出典: [Extend Claude with skills — Choose where skills load](https://code.claude.com/docs/en/skills#where-skills-live)

同名スキルの優先順位: **Enterprise > Personal > Project**。Plugin スキルは `plugin-name:skill-name` の名前空間を持つため競合しない。バンドルスキル・組込コマンドと同名の自作スキルはそのコマンドを置き換えるが、エイリアスは置き換えない（例: project の `code-review` スキルは `/code-review` を置き換えるが、`/review` は引き続きバンドル側を呼ぶ）。claude.ai から同期したスキルは、他と名前が衝突すると短縮名を譲る（後述）。

**モノレポ・サブディレクトリ**: Project スキルは、起動したディレクトリから**リポジトリルートまでの親ディレクトリ**の `.claude/skills/` からロードされる（`packages/frontend/` で起動してもルートのスキルが読まれる）。起動位置より**下**の `.claude/skills/` は起動時には読まれず、Claude がそのサブディレクトリのファイルを初めて読むか編集した時点でロードされ、以後セッション中は使える。それまでは `/` メニューに出ず名前でも呼べない。先にロードしたい場合は `/add-dir <サブディレクトリ>`（v2.1.257〜）を使う。

**Additional directory の注意**: スキルを読むのは `--add-dir` / `/add-dir`（Agent SDK の `additionalDirectories` / `add_dirs` を含む）だけで、`settings.json` の `permissions.additionalDirectories` はファイルアクセスを与えるだけでスキルは読まない。

### claude.ai から同期されるスキル（v2.1.273〜）

claude.ai アカウントでログインしたターミナルセッションでは、アカウントで有効なスキル（自作・組織提供・`pdf` / `xlsx` など Anthropic 組込）が `~/.claude/skills/synced/` にバックグラウンドで同期される。手元の Personal スキルと扱いが異なる点を押さえておく。

| 項目 | 挙動 |
|---|---|
| 呼び出し名 | `/<name>` か完全名 `/anthropic-skills:<name>`。他のコマンドが短縮名を使っていれば、同期スキルは完全名でしか呼べない |
| 予約名 | Enterprise / Personal / Project のスキルフォルダ名に `synced`（大文字小文字を問わない）を使うとスキップされる。plugin 外で `anthropic-skills`（および `anthropic-skills:` で始まる名前）を使ったスキル・コマンドもロードされない |
| 本文の扱い（手元のターミナルセッション） | `!` コマンドを実行せず、`@` 参照のファイルも添付せず、`${CLAUDE_PROJECT_DIR}` / `${CLAUDE_SESSION_ID}` も置換しない。いずれも文字列のまま Claude に届く（v2.1.228〜） |
| 編集 | ダウンロード専用。`~/.claude/skills/synced/` を手で直しても claude.ai には反映されず、次の同期で上書き・削除されうる。変更は claude.ai 側で行う |
| 同期しない条件 | API キー・`ANTHROPIC_AUTH_TOKEN`・`CLAUDE_CODE_OAUTH_TOKEN`・`apiKeyHelper` による認証、Amazon Bedrock、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`、bare mode / `--safe-mode` など |
| 止め方 | user settings で `syncClaudeAiSkills: false`。同期済みスキルは次回起動時に `~/.claude/skills/.trash/` へ移される |

出典: [Extend Claude with skills — Skills synced from claude.ai](https://code.claude.com/docs/en/skills#how-synced-skills-behave)

### SKILL.md の書き方

```yaml
---
name: my-skill
description: このスキルが何をするか、いつ使うかの説明
---

スキルの本文（マークダウン形式の指示）
```

---

## frontmatter リファレンス

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | No | `/` メニューに出る**コマンド名**。省略時はディレクトリ名を使用。⚠️ **2026-10-11 訂正**: personal / project skill でも `name` がコマンド名を決める（2026-09-03 版は「personal / project では決めない」としていたが、現行公式は逆）。<br>・personal / project skill: `name` が `/` メニューに出て入力するコマンド名になる（他のコマンドがその名前を使っていなければ）。**ディレクトリ名でも呼べる**（例: `.claude/skills/deploy-staging/` に `name: deploy` → `/deploy`、`/deploy-staging` も可）<br>・**plugin skill: `name` がコマンドの末尾セグメントを決める**（例: `my-plugin/skills/review/` に `name: fancy` を書くと `/my-plugin:fancy` になる）<br>「小文字・数字・ハイフンのみ（最大 64 文字）」という制約は現行公式に記載がないため削除した |
| `description` | 推奨 | スキルの説明。Claude が自動ロードの判断に使用する。省略時は本文の**最初の空でない行**を使用（**2026-10-11 訂正**: 旧記述は「最初の段落」）。`when_to_use` と合わせて 1,536 文字でキャップ |
| `when_to_use` | No | Claude がいつスキルを呼ぶべきかの補足（トリガーフレーズ・例示リクエスト等）。description に追記され、1,536 文字キャップに合算される |
| `argument-hint` | No | オートコンプリートで表示される引数のヒント。例: `[issue-number]` |
| `arguments` | No | `$name` 置換用の名前付き位置引数。スペース区切り文字列か YAML リストで指定 |
| `disable-model-invocation` | No | `true` にすると Claude の自動ロードを禁止。手動呼び出し専用にする。デフォルト: `false` |
| `user-invocable` | No | `false` にすると `/` メニューに非表示。ユーザーが直接呼び出す必要のない背景知識向き。デフォルト: `true` |
| `allowed-tools` | No | スキル実行中に**許可プロンプトなしで使えるようにするツール**（= 事前承認）。⚠️ **制限ではない**（2026-08-12 訂正）。公式は「It **does not restrict** which tools are available」と明記する。効力は**そのスキルを呼び出したターンの間のみ**。使えるツールを絞りたい場合は `disallowed-tools` を使う。**workspace trust では止まらない**（後述「[スキル内のツール制限](#スキル内のツール制限)」） |
| `disallowed-tools` | No | スキル有効中に使用プールから除外するツール（例: 自律ループで `AskUserQuestion` を禁止）。次のメッセージで解除される |
| `model` | No | スキル実行時のモデル指定。**そのターンの間のみ適用**され設定には保存されない（次プロンプトでセッションモデルに戻る）。`/model` と同じ値、または `inherit`。組織の `availableModels` で除外されたモデルや、auto mode（および classifier が審査中の plan mode）で auto mode 非対応のモデルは使われず、セッションのモデルのままになる。**`context: fork` では forked subagent のモデルを決める** |
| `effort` | No | エフォートレベル。`low` / `medium` / `high` / `xhigh` / `max`（使える値はモデルに依存）。セッションの effort を上書きする |
| `paths` | No | スキルの自動発火を限定する glob パターン。指定すると、マッチするファイルを操作している時だけ自動ロードされる |
| `shell` | No | `` !`command` `` と ` ```! ` ブロックに使うシェル。`bash`（既定）/ `powershell`。`powershell` は PowerShell tool が有効な時に効く。PowerShell tool は **Windows で Git Bash が無い環境と、Git Bash があっても claude.ai / Console アカウントでは既定 ON**。Amazon Bedrock・Google Cloud Agent Platform・Microsoft Foundry のセッションと macOS / Linux / WSL では `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` が必要（**2026-10-11 訂正**: 2026-08-12 版は「Git Bash が無い Windows 以外はすべて要設定」としていた） |
| `context` | No | `fork` でサブエージェント内での隔離実行を有効化 |
| `agent` | No | `context: fork` 時に使用するサブエージェントの種類 |
| `background` | No | **v2.1.218〜**。`context: fork` 時のみ有効。**既定 `true`** で forked subagent は**バックグラウンド実行**され、結果は後から会話に届く。`false` にすると呼び出したターン内で完了を待つ |
| `hooks` | No | スキル呼び出し時に登録される Hooks。⚠️ **「スキルのライフサイクルにスコープ」ではない**（**2026-09-03 訂正**）。公式は「Hooks that Claude Code registers when the skill is invoked and **keeps running for the rest of the session**」と明記しており、**スキルが終わっても解除されず、セッションが終わるまで生き続ける**。初回の成功後に除去したい場合は `once: true` を使う（失敗・exit 2・timeout の後は残る。`once` は skill frontmatter でのみ有効。2026-10-11 訂正: 以前は「1 回だけ実行して除去」と書いていた。[hooks.md](hooks.md) 参照） |
| `metadata` | No | 任意のメタデータ（公式 frontmatter に追加） |
| `license` | No | スキルのライセンス表記 |
| `compatibility` | No | 互換性の宣言 |

> **フィールド数は 18 → 20 に増えた（2026-08-12 更新）**。`metadata` / `license` / `compatibility` が追加された。

> **frontmatter の boolean 値（v2.1.218〜）**: skill / plugin の frontmatter では、`true` / `false` 以外に **`yes` / `no` / `on` / `off` / `1` / `0`（大文字小文字を問わない）** も受理される。

### 呼び出し制御の組み合わせ

| frontmatter 設定 | ユーザーが呼べる | Claude が呼べる | コンテキストへのロード |
|-----------------|---------------|---------------|---------------------|
| （デフォルト） | Yes | Yes | description は常時、本文は呼び出し時 |
| `disable-model-invocation: true` | Yes | 単独では不可 | description は載らない。本文は呼び出し時にロード |
| `user-invocable: false` | No | Yes | description は常時、本文は呼び出し時 |

> **2026-10-11 訂正**: `disable-model-invocation: true` の行は以前「コンテキストに一切ロードされない」としていたが、現行公式の表は「Description not in context, full skill loads when invoked」であり、ユーザーが呼び出せば本文はロードされる。また Claude の可否は「No」ではなく「Not on its own」である。メッセージの**先頭**に `/deploy staging` と書けば直接実行され、**文中**に別の語として `/deploy` と書くと（直接は実行されず）そのメッセージに限り Claude が実行してよいという許可になる。スキルに言及するだけで実行を許したくない場合はスラッシュを付けない。出典: [Extend Claude with skills — Where you write the skill's name](https://code.claude.com/docs/en/skills#where-you-write-the-skills-name)

**使い分け**:
- `disable-model-invocation: true` → デプロイ、コミット、Slack 投稿など**副作用のあるアクション**。Claude が勝手に実行するのを防ぐ
- `user-invocable: false` → レガシーシステムの背景知識など、Claude が必要に応じて参照するが、ユーザーが `/` で呼ぶ必要がない情報

> **注意**: `disable-model-invocation: true` は、SubAgent の `skills:` フィールドによる**プリロードも阻止する**。手動呼び出し専用スキルを SubAgent にプリロードさせたい場合は、この設定と両立しない点に留意する（[SubAgents ガイド](sub-agents.md) 参照）。**v2.1.196 以降は scheduled task(cron 起動)の発火もブロック**するようになった(auto-load + subagent preload に加えて 3 経路すべてを止められる)。

> **frontmatter の命名（2026-10-11 訂正）**: 現行公式は「フィールド名は `when_to_use` を除き**ハイフン区切りの小文字**」「表の綴りと（ハイフンを含め）完全一致しないフィールドは、エラーを出さずに無視する」と明記する。`disable_model_invocation` や `allowedTools` のように書くと黙って効かないため、上表の綴りどおりに書く。
>
> 旧記述は「v2.1.186〜 多語 frontmatter は kebab-case / snake_case / camelCase のどれでも受理され、書き換え不要」としていた。CHANGELOG 2.1.186 の該当項目が対象とするのは `display-name` / `default-enabled` / `fallback` / `metadata.*` だけである。前 3 つは現行 skills ページの frontmatter 表に無いキー、`metadata.*` は自由記述の `metadata` map の中のキーであり、表にあるフィールドへの一般化は誤りだった。
>
> frontmatter が読まれるのは、開きの `---` がファイルの 1 行目にある時だけである。YAML が壊れているとフィールド無しでロードされる（`/skill-name` では呼べるが description で自動発火しない）。

---

## 文字列置換（変数）

スキル本文で使える動的変数:

| 変数 | 説明 |
|------|------|
| `$ARGUMENTS` | `/skill-name` に続けて渡されたすべての引数 |
| `$ARGUMENTS[N]` / `$N` | 0ベースインデックスで個別の引数にアクセス（例: `$0` = 最初の引数） |
| `$name` | frontmatter の `arguments` で宣言した名前付き引数。宣言順に位置へ対応する（`arguments: [issue, branch]` なら `$issue` = 1 番目、`$branch` = 2 番目） |
| `${CLAUDE_SESSION_ID}` | 現在のセッション ID |
| `${CLAUDE_SKILL_DIR}` | スキルの `SKILL.md` が存在するディレクトリパス。**plugin skill の場合は「plugin ルート」ではなく「plugin 内のそのスキルのサブディレクトリ」**に解決される（`${CLAUDE_PLUGIN_ROOT}` と混同しない） |
| **`${CLAUDE_PLUGIN_ROOT}`** | **plugin のルートディレクトリ**。plugin 内の複数スキルが共有するスクリプト・アセットを参照する場合に使う。plugin skill でのみ置換される |
| **`${CLAUDE_PLUGIN_DATA}`** | **plugin の永続データディレクトリ**（plugin の更新後も残る）。plugin が状態を書き出す先。plugin skill でのみ置換される |
| `${CLAUDE_PROJECT_DIR}` | 現在のプロジェクトルート(v2.1.196〜)。**スキル本文だけでなく `allowed-tools` frontmatter 内でも置換される**ため、`allowed-tools: Bash(${CLAUDE_PROJECT_DIR}/scripts/*)` のようなプロジェクトルート依存の allowlist が書けるようになった |
| `${CLAUDE_EFFORT}` | 現在の effort レベル（`low` / `medium` / `high` / `xhigh` / `max`）。effort に応じてスキル指示を切り替えるのに使う。**ultracode は effort レベルではなく独立したトグル**なので、ultracode の ON / OFF にかかわらず実際の effort レベルが入る（**2026-10-11 訂正**: 旧記述は「ultracode は `xhigh` として報告」。v2.1.284 より前は ultracode を ON にするとセッションが `xhigh` になっていたため、その時期の挙動を一般化していた。出典: [Model configuration](https://code.claude.com/docs/en/model-config)） |

> **置換される場所（2026-10-11 訂正）**: **`SKILL.md` の本文と `allowed-tools` の Bash ルールの双方**で置換されると公式が明記しているのは **`${CLAUDE_SKILL_DIR}` と `${CLAUDE_PROJECT_DIR}`**、plugin skill ではさらに `${CLAUDE_PLUGIN_ROOT}` と `${CLAUDE_PLUGIN_DATA}` である。2026-09-03 版はこれを全置換変数に一般化していた。本文と `allowed-tools` で同じ変数を使えば、同梱スクリプトを許可プロンプトなしで実行できる（例: `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)`）。
>
> claude.ai から同期したスキルは、手元のセッションでは `${CLAUDE_PROJECT_DIR}` と `${CLAUDE_SESSION_ID}` が置換されず、文字列のまま Claude に届く（v2.1.228〜）。

**引数の例**:

```yaml
---
name: migrate-component
description: コンポーネントをフレームワーク間で移行する
---

$0 コンポーネントを $1 から $2 に移行する。
既存の動作とテストを維持すること。
```

```
/migrate-component SearchBar React Vue
```

→ `$0` = `SearchBar`、`$1` = `React`、`$2` = `Vue`

---

## 動的コンテキスト注入

`` !`<command>` `` 構文でシェルコマンドをスキル本文に埋め込む。コマンドは**スキルが Claude に送信される前に実行**され、出力がプレースホルダーを置換する。

```yaml
---
name: pr-summary
description: PR の変更内容を要約する
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR コンテキスト
- PR diff: !`gh pr diff`
- PR コメント: !`gh pr view --comments`
- 変更ファイル: !`gh pr diff --name-only`

## タスク
この PR を要約して...
```

**実行順序**: 各 `` !`<command>` `` が即座に実行 → 出力がプレースホルダーを置換 → Claude は展開済みのプロンプトのみを受け取る。これは前処理であり、Claude が実行するものではない。

**複数行のコマンド**は、インライン形式の代わりに ` ```! ` で開くフェンスブロックに書く。

````markdown
## Environment
```!
node --version
git status --short
```
````

注入コマンドについて、2026-10-11 時点の公式仕様で押さえておく点:

| 項目 | 挙動 |
|---|---|
| 失敗時 | **1 つでも失敗するとスキル呼び出し全体が中断**され、Claude は本文を受け取らない（`Shell command failed for pattern "..."`）。既定の `bash` では非 0 終了がすべて失敗扱い（検索・比較系コマンドの exit 1 は例外）。非 0 で終わるのが正常なコマンドには `\|\| true` を付ける |
| 権限 | レンダリング中に許可プロンプトは出ない。deny ルールに一致すると中断する。auto mode 以外では allow にならないコマンドも中断するため、`allowed-tools` で事前承認しておく |
| 無効化 | settings の `"disableSkillShellExecution": true` で user / project / plugin / additional-directory 由来のスキルのコマンドを `[shell command execution disabled by policy]` に置き換える。バンドル・managed スキルは対象外 |
| 同期スキル | claude.ai から同期したスキルの `!` コマンドは、この設定にかかわらず手元のマシンでは実行されない（v2.1.228〜） |

出典: [Extend Claude with skills — Inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context)

---

## サブエージェント実行（context: fork）

`context: fork` を設定すると、スキルは隔離されたサブエージェント内で実行される。スキル本文がサブエージェントのプロンプトとなり、会話履歴にはアクセスできない。

```yaml
---
name: deep-research
description: トピックを徹底的に調査する
context: fork
agent: Explore
---

$ARGUMENTS を徹底的に調査する:

1. Glob と Grep でファイルを検索
2. コードを読み込んで分析
3. 具体的なファイル参照付きで所見を要約
```

| `context: fork` の場合 | 通常の場合 |
|----------------------|-----------|
| サブエージェントのシステムプロンプト + SKILL.md 本文 | メイン会話のコンテキスト + SKILL.md 本文 |
| 会話履歴にアクセス不可 | 会話履歴にアクセス可能 |
| メインコンテキストを消費しない | メインコンテキストを消費する |

**`agent` フィールド**: `Explore`（読み取り専用探索）、`Plan`（設計・計画）、`general-purpose`（汎用）、またはカスタムサブエージェント（`.claude/agents/`）を指定可能。省略時は `general-purpose`。

### `background` フィールドと既定のバックグラウンド実行（v2.1.218〜）

**`context: fork` のスキルは、既定でバックグラウンド実行される**（`background: true` が既定）。呼び出したターンはブロックされず、結果は後から会話に届く。**v2.1.218 より前は forked skill が常にターンをブロックしていた**ため、この変更で体感が大きく変わっている。

バックグラウンド実行に伴う副作用が 3 点あり、いずれも `background: false` の判断材料になる。

| 副作用 | 内容 | 対処 |
|---|---|---|
| **ツールセットが狭くなる** | background subagent 用の限定されたツールセットが適用される | 広いツールが必要なら `background: false` |
| **`/rewind` で戻せない** | background fork が行った編集は**セッションの checkpoint 外**にあるため巻き戻せない | git で revert する |
| **場面によっては待ち動作になる** | `background: false` でなくても結果を待つ場面がある: `-p` / Agent SDK の非対話実行、`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`、同じスキルの前回呼び出しが実行中の再呼び出し、scheduled task の発火、dynamic workflow 内の agent からの呼び出し（v2.1.295〜。それ以前は待たず、結果がメイン会話に届いていた） | 挙動を固定したいなら明示指定する |

> **注意**: `context: fork` は明確なタスク指示があるスキルでのみ意味がある。「この API 規約に従え」のようなガイドラインだけのスキルでは、サブエージェントがガイドラインを受け取るだけで実行すべきタスクがなく、意味のある出力を返さない。

> **`disallowed-tools` で除去できないツール**: `EndConversation`（v2.1.214、敵対的な振る舞いに対して Claude 側からセッションを終了するツール）は、**他のツールが残っている限り `disallowed-tools` でも取り除けない**。出典: [Extend Claude with skills](https://code.claude.com/docs/en/skills) / CHANGELOG v2.1.214

---

## スキルの種類と設計パターン

### リファレンス型（知識・規約）

Claude の作業に適用される知識を提供する。会話内でインラインで実行される。

```yaml
---
name: api-conventions
description: REST API の設計規約。API エンドポイント作成時に使用
---

# API 規約

- URL パスは kebab-case
- JSON プロパティは camelCase
- リストエンドポイントには必ずページネーション
- URL パスでバージョニング（/v1/, /v2/）
```

### タスク型（ワークフロー）

特定のアクションをステップバイステップで実行する。`disable-model-invocation: true` で手動トリガーにするのが一般的。

```yaml
---
name: deploy
description: アプリケーションを本番環境にデプロイする
context: fork
disable-model-invocation: true
---

$ARGUMENTS をデプロイする:

1. テストスイートを実行
2. アプリケーションをビルド
3. デプロイターゲットにプッシュ
4. デプロイが成功したことを検証
```

### ガードレール型（品質・安全性）

特定の条件で自動発火し、品質や安全性を担保する。

```yaml
---
name: infra-decompose
description: |
  インフラとアプリケーションが同一フィーチャーに混在している場合に発火し、
  スコープの分割を提案する。
---

## 発火条件
以下が同一フィーチャーに混在している場合:
- インフラ層: Terraform、S3、ECS...
- アプリケーション層: UI、コンポーネント...

## 分解の原則
...
```

### ビジュアル出力型（HTML生成）

スクリプトをバンドルし、ブラウザで開けるインタラクティブな HTML を生成する。

```yaml
---
name: codebase-visualizer
description: コードベースの対話的ツリービューを生成する
allowed-tools: Bash(python *)
---

# Codebase Visualizer

プロジェクトルートから可視化スクリプトを実行:

\`\`\`bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
\`\`\`
```

---

## バンドルスキル（組み込み）

ClaudeCode に同梱されており、全セッションで使用可能:

| スキル | 用途 |
|--------|------|
| **`/artifact-capabilities`** | 公開 artifact が使えるランタイム機能（connector 呼び出し・ファイルダウンロード等）のリファレンスをロード。artifacts が使える環境のみ |
| **`/artifact-diagramming`** | artifact 内の図（インライン SVG）の描き方ガイドをロード（要 v2.1.221+） |
| `/batch <instruction>` | 大規模な変更を並列で実行。5〜30の独立ユニットに分解し、各 worktree でエージェントが作業・テスト・PR 作成 |
| `/claude-api [subcommand]` | **Claude API と Managed Agents** のリファレンスを、プロジェクトの言語に合わせてロード。コードが `anthropic` か `@anthropic-ai/sdk` を import していると自動発火。サブコマンドは 8 種（`migrate` / `upgrade` / `managed-agents-onboard` / `prompt-audit` / `cost-optimize` / `build-eval` / `hillclimb` / `preserved-thinking-migration`。各版は [slash-commands.md](slash-commands.md) の `/claude-api` 節） |
| **`/claude-in-chrome [task]`** | Claude in Chrome 経由でブラウザ上の作業（ページのテスト・フォーム入力・コンソール確認等）を行う。Chrome 連携が有効なセッションのみ |
| `/code-review [level] [options] [target]` | 現在の差分、または PR 番号・ブランチ・パスを正しさのバグの観点でレビューする。`--fix` で適用、`--comment` で PR に投稿、`ultra` でクラウドの深いレビュー |
| **`/dataviz [request]`** | チャート・グラフ・ダッシュボードのデザインガイド（色の割り当て・配色検証・アクセシビリティ） |
| `/debug [description]` | セッションのデバッグログを解析してトラブルシューティング |
| **`/design [brief]`** | **Claude Design の artboard ワークフローを CLI / Desktop に持ち込む**。現行の要件は **v2.1.265+**（commands ページ）と、artifacts が使えるセッション・Design テンプレートが有効なアカウント。導入は **v2.1.234**（whats-new W34。当時は research preview と表示） |
| **`/design-sync [hint]`** | リポジトリの React デザインシステムを変換して Claude Design にアップロードする |
| `/doctor [prompt-audit [path]]`（alias `/checkup`） | 環境診断 + 自動修復。**v2.1.205 で組み込みコマンドからバンドルスキルへ移された**。`/doctor prompt-audit`（v2.1.283+）は checkup の代わりに CLAUDE.md・skills などの指示を監査する |
| **`/fewer-permission-prompts`** | transcript を走査して read-only な Bash / MCP 呼び出しの allowlist を提案する |
| `/loop [interval] [prompt]` | プロンプトを定期実行（例: `/loop 5m デプロイ完了したか確認`）。interval を省くと Claude が間隔を決め、prompt を省くと組込のメンテナンス用プロンプトか `loop.md` を実行する |
| `/run` | プロジェクトのアプリを起動して変更が実際に動くことを確認する |
| `/run-skill-generator` | **`/run` と `/verify` にプロジェクトのビルド・起動手順を教える**。クリーンな環境からアプリを動かし、成功した手順を per-project スキル `.claude/skills/run-<name>/` として記録する |
| `/simplify [target]` | 変更されたコードを 4 並列エージェントでクリーンアップ（バグ検出はしない。v2.1.154〜） |
| **`/slides [brief]`** | brief から Claude Slides の artifact としてプレゼンテーションを作る（要 v2.1.265+） |
| **`/update-config [request]`** | 設定変更を言葉で伝えると、該当する `settings.json` を Claude が編集する |
| `/verify` | アプリをビルド・実行して、コード変更が意図どおり動くかを確かめる（テストや型チェックで代用しない） |
| **`/workflow-authoring`** | **workflow スクリプト作成のリファレンスをロードする（要 v2.1.248+）。保存済み workflow の `.js` を編集する前に実行することが公式推奨**。dynamic workflows が有効な時のみ |

> **2026-10-11 更新: 公式のバンドルスキルは 20 件である**（commands ページで種別が「Skill」の行を数えた）。2026-09-03 版の 15 件に `/artifact-capabilities` `/artifact-diagramming` `/claude-in-chrome` `/slides` `/update-config` の 5 件を加えた。`/skill-doctor` と `/reload-skills` は組み込みコマンド、`/plugin-authoring` は built-in plugin のスキルであり、いずれもバンドルスキルではない。
>
> **2026-10-11 訂正**: `/claude-api` は以前「Claude API / Agent SDK のリファレンスをロード」、`/run-skill-generator` は「スキル生成ワークフローを起動する」としていたが、いずれも現行公式の説明と異なっていたため上表のとおり直した。
>
> バンドルスキル `/simplify`・`/code-review` は **v2.1.145 以降**が必要（`/security-review` は組み込みコマンド側に分類される）。

> **Managed Agents とは（2026-10-11 追記。2026-09-03 からの持ち越し調査を解消）**: [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) は、Claude Platform 上で提供される「Anthropic 管理のインフラで動く、設定可能な既製の agent harness」である（beta。全エンドポイントに `managed-agents-2026-04-01` beta header が必要）。公式は Messages API と並ぶ「Claude で作る 2 つの方法」の一方として位置付けており、自前の agent loop・ツール実行・ランタイムを組む代わりに使う。**Agent SDK の新概念ではなく、別のハーネス**である。`/claude-api managed-agents-onboard` は、この Managed Agent の作成を案内するサブコマンドである。

### バンドルスキルの無効化と `skillOverrides`

| 設定 | 内容 |
|---|---|
| **`disableBundledSkills`** | バンドルスキル・workflows・組込コマンドをモデルから隠す。⚠️ **`/doctor` だけは例外的に入力可能なまま残る**（v2.1.205〜。環境が壊れた時の復旧手段のため）。`/doctor` も隠すには環境変数 `DISABLE_DOCTOR_COMMAND` か `skillOverrides` の `"doctor": "off"` を使う。環境変数 `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` でも指定可 |
| **`skillOverrides`** | スキル単位で可視性を制御する。**4 つの状態**を取る（下表） |

`skillOverrides` の 4 状態:

| 値 | 挙動 |
|---|---|
| `on` | 通常どおり有効（既定） |
| **`name-only`** | **名前だけをリストに載せ、description をロードしない**。コンテキスト予算を節約しつつ存在は知らせたい場合に使う |
| **`user-invocable-only`** | **ユーザーが `/` で呼んだ時のみ有効**。Claude の自動起動を禁じる（frontmatter の `disable-model-invocation` を設定側から強制するのに相当） |
| `off` | 完全に無効化する |

> **本環境の運用との関係**: 自作スキルが 29 個ある環境では、`skillListingBudgetFraction`（既定 1%）を圧迫しがちである。**使用頻度の低いスキルを `name-only` にする**と、description 分の予算を空けつつ「存在は忘れない」状態を保てる。

> **⚠️ 検証系バンドルスキルの自発起動（v2.1.215 / v2.1.218、2026-10-11 更新）**: v2.1.215 / v2.1.218 で Claude が自動的に走らせる挙動が止まった。現行で**明示的に呼び出さないと動かないのは `/verify` と `/deep-research`** である。`/code-review` は現行の [Code Review](https://code.claude.com/docs/en/code-review) が「Claude can start `/code-review` on its own」としており、Claude が自ら起動できる（[slash-commands.md](slash-commands.md) の変遷表を参照）。
>
> | スキル | 変更 |
> |---|---|
> | `/verify` | **v2.1.215**: Claude が自発起動しない（現行も同じ） |
> | `/code-review` | **v2.1.215** で自発起動が止まったが、現行公式では Claude が自ら起動できる |
> | `/deep-research` | **v2.1.218**: ユーザーが呼び出した時のみ実行（それ以前は Claude 自身も起動できた） |
> | `/code-review` | **v2.1.218**: **background subagent として実行**され、会話コンテキストを埋めない。stacked slash commands もレビュー対象として保持される |
>
> 検証を確実に走らせたい場合は、**スキルのチェーン（完了時に次のスキルを呼ぶ）か埋め込み（生成スキル内に検証を組み込む）を自分で構成する**必要がある。配置の 4 モデルは `docs/harness.md` の verification loop 節を参照。出典: CHANGELOG v2.1.215 / v2.1.218

> **commit の直前に `verify` / `simplify` スキルを走らせる（v2.1.286〜、2026-10-11 追記）**: セッション開始時に `verify` か `simplify` という名前のスキルがあると、Claude Code の commit 指示に「各 commit の直前にそれを実行する」が加わる（docs / テストだけの変更は除く）。条件は次の 3 つである。
>
> | 条件 | 内容 |
> |---|---|
> | 置き場所 | Enterprise / Personal / Project / Additional directory のスキル、または同名の `.claude/commands/` ファイル。`/verify` がリポジトリルートに記録するレシピ（`.claude/skills/verify/SKILL.md`）は Project スキルなので数に入る。**バンドルの `/verify` / `/simplify`・plugin スキル・claude.ai 同期スキルは数に入らない** |
> | 呼び出し可否 | Claude が呼べること。`disable-model-invocation: true` だと指示は加わらない |
> | git 指示 | `includeGitInstructions` を OFF にしていないこと（OFF にすると組込の commit / PR 指示ごと消える） |
>
> 出典: [Extend Claude with skills — Run your checks before each commit](https://code.claude.com/docs/en/skills#run-your-checks-before-each-commit)

> **セッション中の変更が即反映される（v2.1.216〜）**: セッション中に追加・変更した skills / commands は、**再起動なしでスラッシュメニューに反映**される（CHANGELOG v2.1.216 で修正された不具合）。**2026-10-11 追記**: ただし `/reload-skills`（v2.1.152〜の組み込みコマンド）が今も要る場面がある。セッション開始時に存在しなかった**トップレベルの skills ディレクトリ**を新しく作った場合は監視対象外のため、`/reload-skills` を実行する（以後そこを変更するたびに再実行が要る）。また、plugin を兼ねるスキルフォルダの `hooks/`・`.mcp.json`・`agents/`・`output-styles/` の変更は `/reload-plugins` が必要である。出典: CHANGELOG v2.1.216 / [Extend Claude with skills — Edit a skill during a session](https://code.claude.com/docs/en/skills#live-change-detection)

> **`disable-model-invocation` の skill を Claude が呼ぼうとした時の挙動（v2.1.222〜）**: 従来は Claude が「呼べないので自分でワークフローを再現する」方向に流れがちだったが、現在は **「ユーザーに実行を依頼せよ」と明示的に指示される**ようになった。`/ok-ship-it` のように「明示発火のみ」を意図したスキルが、Claude の自己流の再現で骨抜きになる問題が解消している。出典: CHANGELOG v2.1.222

> **組込コマンドと同名の skill が非対話で起動できない不具合（v2.1.221 で修正）**: plugin / 組織配布の skill が **`/help` / `/feedback` と同名**の場合、非対話セッション（`-p` / SDK）で起動できなかった。**2026-10-11 訂正**: 修正後も、非対話セッションで予約が外れるのは `help` と `feedback` の **2 つだけ**である。`/login` など他のターミナル専用組込コマンドの名前は、非対話でコマンド自体が動かなくても予約されたままなので、その名前の plugin skill は素の名前では呼べない。旧記述の「`/help` `/feedback` 等」は CHANGELOG の「e.g.」をそのまま訳したもので、他の組込名にも及ぶと読める点が誤りだった。組込名との衝突は避ける。出典: CHANGELOG v2.1.221 / [Extend Claude with skills — How a skill gets its command name](https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name)

---

## パーミッション制御

### スキルへのアクセス制限

```
# Skill ツール自体を無効化（全スキルへのアクセスを拒否）
Skill

# 特定スキルのみ許可
Skill(commit)
Skill(review-pr *)

# 特定スキルを拒否
Skill(deploy *)
```

構文: `Skill(name)` = 完全一致、`Skill(name *)` = プレフィックスマッチ。

**deny ルールが及ぶ範囲（2026-10-11 追記）**: deny ルールは書いた名前以外にも次をブロックする。

| deny ルールに書く名前 | 例 | 併せてブロックされるもの |
|---|---|---|
| エイリアス | `Skill(review)` | エイリアス `/review` 経由のバンドル `/code-review` |
| 修飾なしの名前 | `Skill(deploy)` | `apps/web:deploy` として列挙される Nested スキル（v2.1.260〜。それ以前はブロックされなかった） |
| claude.ai 同期スキル | `Skill(anthropic-skills:deploy)` | Claude Desktop が plugin としてセッションに渡す同じスキル |
| 同期スキルの plugin 形 | `Skill(deploy:deploy)` | 同期スキル本体 |
| パラメータ形 | `Skill(skill:deploy)` | Claude がどの名前（エイリアス・表示名を含む）で呼んでもそのスキル |

allow ルールはスキル自身の名前と Claude が呼んだ名前にしか一致しない。同期スキルを許可なしで通すには予約名前空間の中で書く（`Skill(anthropic-skills:pdf)` / `Skill(anthropic-skills *)`。`Skill(anthropic *)` は一致しない）。出典: [Extend Claude with skills — Restrict Claude's skill access](https://code.claude.com/docs/en/skills#restrict-claudes-skill-access)

> **ネストしたスキルの名前**（v2.1.203〜、2026-08-12 追記。**2026-10-11 訂正**）: サブディレクトリの `.claude/skills/` に置いたスキルは、**ディレクトリ名が他のスキルと衝突する場合に** `/apps/web:deploy` のような**ディレクトリ修飾名**を持つ（衝突しなければディレクトリ名のまま）。ルートと `apps/web/` の両方に `deploy` がある場合、`/deploy` はルート側を実行し、Claude には修飾名の候補も列挙されて作業中のファイルがあるディレクトリの方を使うよう指示される。また、起動位置より下のスキルは**そのサブディレクトリ配下のファイルを触った時点で初めて利用可能になる**（常時ロードされない）。モノレポで各パッケージにスキルを置く場合、この挙動が前提になる。

### スキル内のツール制限

⚠️ **`allowed-tools` は「制限」ではなく「事前承認」である**（2026-08-12 訂正）。公式は「It **does not restrict** which tools are available」と明記している。書いたツールが**許可プロンプトなしで使えるようになる**だけで、書いていないツールが使えなくなるわけではない。効力は**そのスキルを呼び出したターンの間のみ**である。

**2026-10-11 追記**:

- **workspace trust では止まらない**: 一度も信頼していないフォルダでの `-p` 実行でも、project スキルの `allowed-tools` は適用される。リポジトリに commit されたスキルの `allowed-tools` は、そのリポジトリで ClaudeCode を動かす前に確認する
- **`allowManagedPermissionRulesOnly` 下では無視される**（v2.1.282〜）: 組織が managed settings でこれを設定すると、project / personal スキルの `allowed-tools` は無視され、列挙したツールは managed ルールと通常の許可プロンプトを通る。無視されたスキルは `/status` で確認できる

```yaml
---
name: gh-helper
description: gh CLI で PR 情報を取得する
# gh コマンドを都度承認なしで使えるようにする（他のツールも依然として使える）
allowed-tools: Bash(gh *), Read, Grep, Glob
---
```

**本当に制限したい場合は `disallowed-tools` を使う**:

```yaml
---
name: safe-reader
description: ファイルを変更せずに読み取り専用で探索する
disallowed-tools: Edit, Write, NotebookEdit
---
```

---

## ベストプラクティス

### description の書き方

description は Claude がスキルを自動ロードするかどうかの判断基準である。

**悪い例**:
```yaml
description: API 関連の処理
```

**良い例**:
```yaml
description: |
  REST API の設計規約。API エンドポイント作成、レスポンス形式の設計、
  バリデーション実装時に使用。「API」「エンドポイント」「REST」に関する実装時に自動ロード。
```

- **具体的なトリガーフレーズ**を含める（ユーザーが使いそうなキーワード）
- 「いつ使うか」を明示する
- 曖昧な説明は Claude の誤ロードや見逃しの原因になる

### SKILL.md のサイズ管理

- **SKILL.md は 500行以下**に保つ
- 詳細な API ドキュメント、コード例集、仕様書は別ファイルに分離する
- `SKILL.md` から相対パスで参照し、Claude が必要に応じて読み込めるようにする

```markdown
## 追加リソース

- 完全な API 詳細は [reference.md](reference.md) を参照
- 使用例は [examples.md](examples.md) を参照
```

### 副作用のあるスキルの保護

デプロイ、コミット、メッセージ送信など副作用のあるワークフローは必ず手動トリガーにする:

```yaml
disable-model-invocation: true
```

これにより:
- Claude が勝手に実行することを防ぐ
- description がコンテキストにロードされないため、呼び出すまではコンテキストコストがかからない（本文は呼び出し時にロードされる）
- ユーザーが `/skill-name` で明示的に呼び出す必要がある

### スキル数の管理

- description リストのコンテキスト予算はモデルウィンドウの 1%（個別 description は 1,536 文字キャップ）
- スキルが多すぎると一部の description が除外される。`/doctor` で overflow を確認
- **`/skill-doctor`**（組み込みコマンド、2026-10-11 追記）で、スキルごとのコンテキストコストと使用頻度を確認する。対話セッションでは `/plugin` manager の **Stats** タブに、`-p` では文字列で出る。バンドルスキルと Enterprise スキルは対象外で、一度も呼ばれていないスキルと OFF にする場所を示す。コストの大きいものから OFF を検討する。要 **v2.1.252+**（skills / commands ページと whats-new W36 の記載。CHANGELOG では 2.1.261 の項に追加と記載）で、feature flag を取得しないセッション（Bedrock 等）や Remote Control 経由では使えない
- 使用頻度の低いスキルは `disable-model-invocation: true` にしてコンテキストから除外するか、`skillOverrides` で `name-only` にするか、削除を検討する

### ホットリロード

`~/.claude/skills/`・`.claude/skills/`・`--add-dir` で渡したディレクトリの `.claude/skills/` のスキルは**セッション再起動なしで自動反映**される（bare mode を除く）。作成・編集後すぐにテスト可能。

> **2026-10-11 追記**: 自動反映の対象は `SKILL.md` のテキストだけである。セッション開始後に新設したトップレベルの skills ディレクトリは `/reload-skills`、plugin を兼ねるスキルフォルダの `hooks/` などは `/reload-plugins` が必要（上記「セッション中の変更が即反映される」の注記を参照）。

---

## Tips

### extended thinking の有効化

スキル本文に `ultrathink` という単語を含めると、その turn だけより深い推論を要求できる（公式キーワード。API に送る effort レベルは変わらない。[model-config](https://code.claude.com/docs/en/model-config) 参照）。

### 既存 `.claude/commands/` との互換性

`.claude/commands/deploy.md` と `.claude/skills/deploy/SKILL.md` は同じ `/deploy` コマンドを作成する。既存の commands ファイルはそのまま動作するが、同名の場合は Skills が優先される。Skills はサポートファイル（テンプレート、スクリプト）を含められる点で commands より強力である。

### `--add-dir` からのスキル検出

`--add-dir` で追加したディレクトリ内の `.claude/skills/` も自動検出される。ライブ変更検出にも対応しており、セッション中の編集が即時反映される。

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| スキルが発火しない | description にユーザーが使うキーワードを含めているか確認。`What skills are available?` で Claude に認識されているか確認。`/skill-name` で直接呼び出してテスト。frontmatter の YAML が壊れていると description が効かないため、`claude plugin validate .claude/skills`（personal なら `~/.claude/skills`。v2.1.233+）か `--debug` で parse エラーを探す |
| スキルが頻繁に誤発火する | description をより具体的にする。`disable-model-invocation: true` で手動呼び出し専用にする |
| Claude がスキルを認識しない | スキル数が多くてコンテキスト予算を超えている可能性。`/doctor` で overflow を確認し、`/skill-doctor`（v2.1.252+）で OFF にする候補を探す |

---

## 現在の個人スキル一覧

`~/.claude/skills/` に配置されている Personal スコープのスキル:

| スキル | 種別 | 用途 |
|--------|------|------|
| `aws-ecs-fargate` | リファレンス | ECS Fargate + RDS + ElastiCache の Terraform パターン |
| `aws-static-hosting` | リファレンス | S3 + CloudFront 静的サイトホスティングの Terraform パターン |
| `ecs-deploy-troubleshooting` | リファレンス | ECS デプロイ障害の調査手順と過去事例 |
| `github-actions-aws-oidc` | リファレンス | GitHub Actions OIDC → AWS デプロイパターン |
| `infra-decompose` | ガードレール | インフラ+アプリ混在フィーチャーのスコープ分割提案 |

すべて Personal スコープ（全プロジェクト共通）で、`disable-model-invocation` なし（Claude が自動ロード可能）。実務パターンに基づくリファレンス型スキル群。

---

## 関連ドキュメント

- [Extend Claude with skills](https://code.claude.com/docs/en/skills) — 公式 Skills ドキュメント
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — 拡張機能の全体像
- [Subagents](https://code.claude.com/docs/en/sub-agents) — サブエージェントとの連携
- [Hooks](https://code.claude.com/docs/en/hooks) — イベント駆動の自動化
- [Plugins overview](https://code.claude.com/docs/en/plugins/overview) — Skills のパッケージング・配布（2026-10-11 張替え: 旧 `docs/en/plugins` は `plugins/overview` へ改名された）
- [Commands](https://code.claude.com/docs/en/commands) — 組み込みコマンドとバンドルスキルの一覧
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
