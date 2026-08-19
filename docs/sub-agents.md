# ClaudeCode SubAgents ガイド

> 出典: [Subagents](https://code.claude.com/docs/en/sub-agents) / [Extend Claude Code](https://code.claude.com/docs/en/features-overview) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Agent teams](https://code.claude.com/docs/en/agent-teams) / [Agent view](https://code.claude.com/docs/en/agent-view) / [Built-in commands](https://code.claude.com/docs/en/commands) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [whats-new week 27-32](https://code.claude.com/docs/en/whats-new/2026-w32) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-16時点)

SubAgents は ClaudeCode のメインセッションから**隔離されたコンテキスト**でタスクを実行する自律的なワーカーである。大量のファイル読み込みや並列調査をサブエージェントに委任することで、メインの会話コンテキストをクリーンに保ちながら、専門的なタスクを効率的に処理できる。

---

## 前提知識

### SubAgents の基本概念

SubAgents はメインセッションとは**別のコンテキストウィンドウ**で動作する。メインセッションの会話履歴にはアクセスできず、作業結果のサマリーだけがメインに返される。

```
メインセッション ─── タスク委任 ──→ SubAgent（隔離コンテキスト）
      ↑                                    │
      └──── サマリーを受け取る ←────────────┘
```

この「コンテキスト隔離」が SubAgents の最大の利点である。サブエージェントが数十ファイルを読み込んでも、メインセッションのコンテキストは消費されない。

### コンテキストウィンドウとの関係

| 項目 | ロードタイミング | メインへの影響 |
|------|----------------|---------------|
| CLAUDE.md | セッション開始時 | 毎リクエスト消費 |
| Skills（description） | セッション開始時 | 毎リクエスト消費（低コスト） |
| Skills（本文） | 呼び出し時 | 呼び出し後に消費 |
| **SubAgent** | **起動時** | **隔離 — メインを消費しない** |
| MCP サーバー | セッション開始時 | 毎リクエスト消費 |
| Hooks | トリガー時 | ゼロ（外部実行） |

SubAgent 起動時にロードされるもの:
- システムプロンプト（親と共有、キャッシュ効率のため）
- `skills:` フィールドで指定された Skills の全文
- CLAUDE.md と git status（親から継承）
- リードエージェントがプロンプトで渡したコンテキスト

**メインの会話履歴や、メインで呼び出された Skills は継承しない。**

### Skills / SubAgents / Agent Teams の使い分け

| 比較軸 | Skill | SubAgent | Agent Teams |
|--------|-------|----------|-------------|
| 何であるか | 再利用可能な指示・知識 | 隔離されたワーカー | 独立した複数セッション |
| コンテキスト | メインと共有 | メインから隔離 | 各セッションが完全独立 |
| コミュニケーション | — | 結果をメインに返す | チームメイト同士で直接通信 |
| 最適な用途 | リファレンス、ワークフロー | 調査、レビュー、並列作業 | 複雑な協調作業、競合仮説の検証 |
| トークンコスト | メインコンテキストを消費 | 低い（サマリーのみ返却） | 高い（各セッションが独立インスタンス） |

**判断基準**:
- 「知識を共有したい」→ Skill
- 「作業を委任して結果だけ欲しい」→ SubAgent
- 「複数のワーカーが互いに議論・協調する必要がある」→ Agent Teams

**移行ポイント**: 並列サブエージェントでコンテキスト上限に達する場合や、サブエージェント同士の通信が必要な場合は Agent Teams への移行を検討する。

### Skills と SubAgents の組み合わせ

Skills と SubAgents は双方向で連携できる:

| アプローチ | システムプロンプト | タスク | 追加ロード |
|-----------|-------------------|--------|-----------|
| Skill に `context: fork` | エージェントタイプ（Explore 等）のプロンプト | SKILL.md の本文 | CLAUDE.md |
| SubAgent に `skills` フィールド | サブエージェントのマークダウン本文 | Claude の委任メッセージ | プリロードされた Skills + CLAUDE.md |

---

## 組み込みサブエージェント

ClaudeCode には組み込みサブエージェントがある。タスクの性質に応じて自動的に選択される。

| エージェント | モデル | 用途 | 特徴 |
|-------------|--------|------|------|
| **Explore** | **メインから継承（Claude API では Opus で cap）** | コードベースの探索・発見・分析 | 読み取り専用、高速。Glob・Grep・Read に最適化。CLAUDE.md / 親の git status をスキップして調査を軽量化。**v2.1.198 で Haiku 固定は撤回**（それ以前は Haiku 固定）。下記の cap 挙動を参照 |
| **Plan** | メイン会話から継承 | Plan Mode でのリサーチ・コンテキスト収集 | コードを変更しない。設計・計画フェーズ向け。CLAUDE.md / git status をスキップ |
| **general-purpose** | メイン会話から継承 | 複雑なマルチステップ操作 | 探索とコード変更の両方が可能。デフォルト |
| **statusline-setup** | Sonnet | `/statusline` でステータスライン設定時 | 設定支援 |
| **claude-code-guide** | Haiku | ClaudeCode の機能について質問した時 | 機能ガイド |

> Explore は呼び出し時に thoroughness レベル（`quick` / `medium` / `very thorough`）を指定して使われる。Explore と Plan は CLAUDE.md と親の git status を読み込まないが、その他の組み込み・カスタムサブエージェントは両方を読み込む。

**Explore の活用例**: 「認証システムのトークンリフレッシュの仕組みを調査して」のような読み取り専用の調査タスクに最適。大量のファイルを読み込んでもメインコンテキストを汚さない。

> **Explore の model cap はプロバイダで挙動が異なる（2026-08-04 更新）**: 公式は「inherits from the main conversation, **capped at Opus on the Claude API**, so Explore never runs on a more expensive model than the one you already chose」と説明する。**cap 先はバージョン固定ではなく `opus` エイリアスの解決先**であり、v2.1.219 以降は Opus 5 になる（それ以前の版で「Opus 4.8 に cap」と書いていたのは当時の解決先を書いたもので、仕様としては誤り）。メインが Sonnet / Haiku ならその同一モデルで動く。**Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS では cap がなく、メインのモデルを直接継承する**。出典: [Subagents](https://code.claude.com/docs/en/sub-agents)

### 新しいサブエージェント機能（実行形態の拡張）

frontmatter フィールド（上掲）で以下の実行形態を制御できる。

- **Forked subagents**: 会話コンテキスト全体を継承する fork 実行。通常のサブエージェントは空コンテキストから始まるのに対し、fork は現在の会話（と prompt cache）を引き継ぐ。**v2.1.232 以降、対話セッションでは fork mode が既定 ON になった**（2026-08-16 訂正。従来は「環境変数 `CLAUDE_CODE_FORK_SUBAGENT=1` で有効化」と書いていたが、現在この環境変数は**上書き専用**である）。**対話セッションから手動で起動するコマンドは v2.1.212 で `/fork` から `/subtask` に変わった**（現在の `/fork` は「会話を別 background セッションへ複製する」別機能。`docs/slash-commands.md` の「セッション管理」節を参照）。**さらに v2.1.221 で `/fork` は複製先セッション用に独自の worktree を作成する**ようになり、元セッションの checkout を共有しなくなった。

  | 実行形態 | fork mode の既定 |
  |---|---|
  | 対話セッション | **ON**（v2.1.232 以降。それ以前は OFF で、`CLAUDE_CODE_FORK_SUBAGENT=1` が必要だった） |
  | `claude -p`（print mode） | **OFF** |
  | Agent SDK | **OFF** |

  環境変数 `CLAUDE_CODE_FORK_SUBAGENT` は上記の既定を上書きする。`1` で `-p` / SDK も含め全セッションで ON、`0` で全セッション OFF。あわせて **v2.1.232 以降、teammate 以外の agent spawn も対話セッションでは既定でバックグラウンド実行**になった。
- **Background subagents** (`background: true`): バックグラウンドタスクとして常時実行。`/tasks` で稼働中を確認できる。**2026-w27 (Week 27) 以降は background 実行が subagent の既定挙動に**なった (呼び出し中もメインが作業を継続できるようになった)。従来の「フォアグラウンドでメインを止めて完了を待つ」動作を明示指示したい場合は、呼び出し側でその旨を伝える。
  - **background では保持するツール集合が狭くなる**（同じ定義がフォアグラウンドと background で違うツール集合に解決される点に注意）。`Agent` / `ExitPlanMode` を除き、background subagent が保持する組み込みツールは **`Read` / `Grep` / `Glob` / `Bash` / `PowerShell` / `Edit` / `Write` / `NotebookEdit` / `WebFetch` / `WebSearch` / `TodoWrite`（※後述のとおりモデル世代により提供されない） / `Skill` / `ToolSearch` / `EnterWorktree` / `ExitWorktree` / `Monitor` / `TaskStop` / `SendMessage` / `Artifact` のみ**である。MCP ツールは全て保持される。
- **Worktree isolation** (`isolation: worktree`): リポジトリの隔離コピー（一時 git worktree）で実行し、並列変更の競合を避ける。
- **Persistent memory** (`memory: user|project|local`): セッションを跨いだ学習を有効化。保存先パスは scope ごとに異なる（`user`=`~/.claude/agent-memory/<name>/` / `project`=`.claude/agent-memory/<name>/` / `local`=`.claude/agent-memory-local/<name>/`）。MEMORY.md は先頭 200 行または 25KB がロードされる。
- **Nested subagents（入れ子）** (v2.1.172〜): サブエージェントが自身のサブエージェントを spawn できる（`tools` に `Agent` を含めると有効）。委任タスクがさらに並列サブタスクに分かれる場合（例: レビュアーが finding ごとに検証担当を起動）に使い、中間出力をメイン会話に流さずトップレベルのサマリだけ返す。`/agents` のパネルにツリー表示される。resumed / forked subagent は spawn depth を継承・カウントする。fork は別の fork を spawn できないが、他種別は spawn 可能（深さにカウントされる）。**v2.1.193 で panel の可視化が sibling + child + path-to-main まで拡張**、**v2.1.196 の `/doctor` が same-scope 同名 agent 重複を報告**する。**既定の深さは短期間で 3 回変わっている**ため、下記の変遷表を必ず確認する。

#### nested subagent の既定深さの変遷（重要）

| バージョン | 既定の深さ | 変更可否 |
|---|---|---|
| v2.1.172 〜 v2.1.180 | depth 5（fg は self-limiting とされていた） | 不可 |
| v2.1.181 〜 v2.1.216 | **depth 5**（fg / bg 両方ともハード cap） | 不可 |
| **v2.1.217 〜 v2.1.218** | **nesting 無効（depth 1）** | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` で許可レイヤ数を指定 |
| **v2.1.219 〜** | **depth 3** | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` で nesting を無効化 |

- nesting が無効な状態では、**`Agent` ツールは fork 以外のすべての subagent から withheld される**（ツール一覧には残るが呼ぶとエラーを返す）。深さ上限に達した fork は `Agent` を継承ツールに保持するが、呼ぶと spawn せずエラーを返す。
- ✅ **公式 docs も追従済み（2026-08-04 確認）**: 公式 [Subagents](https://code.claude.com/docs/en/sub-agents) は現在「**By default, a subagent can spawn subagents of its own, up to three layers below the main conversation.**」と記載し、版履歴も「**v2.1.217 through v2.1.218**: the limit defaulted to one … v2.1.219 raised the default to three」と明記している。**2026-07-26 時点で本ドキュメントが CHANGELOG を正として記述した判断は、公式側の追従で裏付けられた**（当時存在した不整合は解消済み）。
- `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` は**正の整数のみ受理**する。`1` で nesting 無効化はできるが、**上限の撤廃はできない**。
- 出典: CHANGELOG v2.1.181 / v2.1.217 / v2.1.219 / [Subagents](https://code.claude.com/docs/en/sub-agents) / [Environment variables](https://code.claude.com/docs/en/env-vars)

#### spawn のハード上限（v2.1.224 で「per-session 200」が撤廃された）

暴走ファンアウトを防ぐ上限は、現在**同時実行数と深さの 2 方向のみ**である。

| 上限 | 既定値 | 環境変数 | 備考 |
|---|---|---|---|
| **per-session の総 spawn 数** | **上限なし** | ~~`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`~~ | **v2.1.224 で撤廃**。環境変数は残っているが **no-op** |
| **同時実行数** | **20** | `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`（v2.1.217〜） | 超過時は `Concurrent subagent limit reached`。**`ultracode` セッションは免除** |
| **nesting の深さ** | 3（v2.1.219〜） | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`（v2.1.217〜） | 上記変遷表を参照 |
| **セッション全体の WebSearch 回数** | **200** | `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`（v2.1.212〜） | **こちらは現役**。subagent の調査ファンアウトにも効く |

> **⚠️ 200 上限は撤廃された（2026-08-12 更新）**。公式 [Subagents](https://code.claude.com/docs/en/sub-agents) は現在「**There's no limit on the total number of subagents Claude can spawn over a session.**」と明記し、[Environment variables](https://code.claude.com/docs/en/env-vars) も `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` を「**Removed in v2.1.224 and now a no-op**」としている。CHANGELOG v2.1.224 の原文は「Removed the 200-subagent-per-session spawn cap; **long-running sessions no longer refuse new agents** (concurrency and depth limits still apply)」である。
>
> 2026-08-04 時点の本ドキュメントは「セッション単位・同時実行・深さの **3 方向**に上限」「per-session 200 は**無効化できない**」「200 回上限は `/clear` でリセットされる」と記載していたが、いずれも現行仕様ではない。**長時間セッションで agent が拒否される心配は無くなった**。
>
> **`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`（200）は現役**なので混同しないこと。撤廃されたのは subagent 側だけである。

- `/subtask`（会話内 forked subagent）は **実行中に同時実行スロットを 1 つ占有する**（v2.1.224 以降。それ以前は「per-session budget を消費するが cap でブロックされない」という扱いだった）。`/fork`（会話を別 background セッションへ複製）は同時実行枠にもカウントされない。
- `--max-budget-usd` は **background subagent も停止させる**（v2.1.217 で修正）。print mode 限定のフラグである。
- 出典: [Subagents](https://code.claude.com/docs/en/sub-agents) / [Environment variables](https://code.claude.com/docs/en/env-vars) / CHANGELOG v2.1.212 / v2.1.217 / **v2.1.224**

> **JARVIS Plugin の運用方針との関係**: 上記は **公式機能としての可否**である。本リポジトリの JARVIS Plugin は、コンテキスト連鎖・デバッグ容易性・コストの観点から **運用方針としてはフラット並列（nested を使わない）** を採る（後述「パターン 6」参照）。「機能として可能」と「運用方針として使う」はレイヤーが別である点に注意する。

> 同名サブエージェントの解決（ネスト時）: 複数の `.claude/agents/` が同名 `name` を定義する場合、**v2.1.178 以降は cwd に最も近い定義が採用される**。

> 多数の独立セッションを 1 画面で管理する用途は [background agents (Agent view)](https://code.claude.com/docs/en/agent-view)、セッション間で通信する用途は [agent teams](https://code.claude.com/docs/en/agent-teams) を参照。

#### Task / Todo ツールのモデル別提供状況（v2.1.233〜、破壊的変更）

**v2.1.233 以降、以下の 5 ツールは新しい世代のモデルでは既定で提供されない。**

| 項目 | 内容 |
|---|---|
| 対象ツール | `TodoWrite` / `TaskCreate` / `TaskGet` / `TaskUpdate` / `TaskList` |
| 提供されないモデル | **Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5、およびそれらのファミリの後継**（Opus 5 を含む） |
| 従来どおり提供されるモデル | 上記より前の世代（Opus 4.7 等） |
| 例外 | **background session と Claude Code on the web では全モデルで提供**される |
| 再有効化 | `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` / `--allowedTools TaskCreate` / `--tools` / Agent SDK の `allowedTools` |
| SubAgent での扱い | **親セッションが持っている場合にのみ subagent も持つ** |

公式は理由を「これらのモデルは書き出しのチェックリスト無しで多段タスクを追跡でき、ツール定義とリマインダがコンテキストを消費するため」と説明している。

> ⚠️ **公式記述と実機観測の差異（2026-08-16 確認）**: BOSS の環境（Opus 5 / v2.1.233 / `CLAUDE_CODE_ENABLE_TODO_TOOLS` 未設定）で確認したところ、**`TodoWrite` は確かに提供されていない**一方、**`TaskCreate` / `TaskGet` / `TaskUpdate` / `TaskList` の 4 つは deferred tool として提供されていた**。公式は 5 つすべてを対象と記述しているため、実装と記述が一致していない可能性がある。**判断の基準は公式記述に置きつつ、実際に使えるかはセッションのツール一覧で確認する**のが安全である。

出典: [Tools reference — Task tool availability](https://code.claude.com/docs/en/tools-reference#task-tool-availability) / CHANGELOG v2.1.233

### v2.1.183 以降の追加変更(2026-07 時点)

- **Background subagent の permission prompts がメインに浮上**(v2.1.186): 従来は auto-deny だった background subagent の permission 要求が、v2.1.186 で**メインセッションに浮上**する挙動になった。どの agent が求めているかも表示、`Esc` で当該 tool のみ拒否できる。
- **`claude agents` background agent 通知 + 自動 commit/push/PR**(v2.1.198): `Notification` hook に **`agent_needs_input` / `agent_completed`** イベントが追加。コード変更ワークを完了した worktree では**自動で commit + push + draft PR まで走らせる**(質問で止まらない)ため、長時間バックグラウンド運用の実用性が上がった。
  - ⚠️ **v2.1.221 で完了時の挙動が変わった（破壊的）**: 「Changed background sessions to **commit and push to preserve work**, open a **draft PR only when the task calls for one**, **follow your CLAUDE.md git instructions**, and always end by **reporting where the work lives**」。つまり **commit + push は作業保全のため必ず行うが、draft PR はタスクが要求する場合のみ**に後退し、代わりに **CLAUDE.md の git 指示に従う**ようになった。最後に必ず「作業物の所在」を報告する。**CLAUDE.md に git 運用ルール（push/PR の可否、AI 署名の禁止など）を書いているリポジトリでは、その指示が background session にも効く**点が重要である。出典: CHANGELOG v2.1.221
- **subagent / compaction が extended thinking 設定を継承**(v2.1.198): 委任タスクの出力品質が改善。
- **Agent teams: implicit team 化**(v2.1.178): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` で**全セッションに暗黙 team** が有効化される。**`TeamCreate` / `TeamDelete` は削除**され、Agent tool の `name` パラメータで直接 teammate を spawn する。`team_name` は accept but ignore の互換モードで残る。
- **`CLAUDE_CODE_SUBAGENT_MODEL=inherit` セマンティクス変更**(v2.1.196): **`inherit` は「leave unset」に変更**され、per-invocation param → frontmatter へフォールスルーする挙動になった。それ以前はメイン会話のモデルを**強制**して frontmatter / param を無視していたため、**破壊的変更**。既存 subagent 設定の見直しが必要。
- **auto mode の subagent 事前分類**(v2.1.178): 分類器が subagent spawn **直前** にタスク記述を評価するようになり、subagent 経由でブロック対象アクションを実行する抜け穴が塞がれた。詳細は `docs/best-practices.md` の Auto mode 節を参照。
- **`/agents` ウィザード廃止**(v2.1.198): 対話 UI は撤去。今後は Claude に依頼する(「〜な subagent を作って」)か、`.claude/agents/` を直接編集する運用に移行。`/agents` コマンド自体はロード状況の確認・リロード用途で存続する。

### 2026-w27〜w28 (2026-07) の追加変更

- **Subagent が background 実行既定**(Week 27): 上掲「実行形態」注記の通り、呼び出し中もメインが作業を継続できる既定挙動に切り替わった。
- **Agent view rows の刷新**(Week 28): raw tool call text の代替として、**colored state word + 分類器生成の headline** を表示。実行中のセッション状態が視覚的に把握しやすくなった。
- **`claude agents` の PR 自動リンク**(Week 28): セッションが編集・マージ・コメント・push した PR を、agent view から自動でリンク表示する。
- **Background agents の自動 upgrade**(Week 28): ClaudeCode 本体の更新直後に、attach 済み background agent が自動 upgrade されるようになり、stale-session の upgrade 遅延が解消された。
- **Background task 通知に「no human input has occurred」明示**(Week 28): prompt-injection 起因で fabricated な承認がバックグラウンド通知経由で紛れ込むのを防ぐため、通知本文に「これは自動イベントであり、ユーザー入力ではない」旨が明示されるようになった。**セキュリティ強化**。
- **Agent teams の細部改善**(v2.1.198 / v2.1.199):
  - v2.1.198: teammate turn が API error で終わった際に **lead へ通知**が届く / 別 teammate からのメッセージで **idle teammate が wake** する
  - v2.1.199: idle teammate row の表示挙動改善(他 teammate 稼働中は保持) / **`/model` / `/fast` を teammate viewing 中に打つと lead へ適用**の notice が表示される
  - サブエージェント定義を teammate として使う場合、frontmatter の `skills` / `mcpServers` は **teammate 実行時に適用されず**、project/user settings から読まれる
  - **SendMessage 経由の approval 主張は auto mode 分類器で untrusted 扱い**(teammate 間メッセージだけで許可を取ろうとしても分類器が独立審査する)

### v2.1.222〜v2.1.233 の追加変更 (2026-08)

- **worktree isolation が Bash と git redirect にも適用**(v2.1.222): 従来の worktree isolation は**ファイル編集ツールのみ**を隔離しており、**Bash 経由やリダイレクトでメイン checkout を破壊できた**。現在は全セッション種別とその subagent に対して適用される（[session-history.md](session-history.md) も参照）。
- **agent 定義の `bypassPermissions` が組織ポリシーを迂回できた穴を修正**(v2.1.223): 組織が bypass を無効化していても、agent 定義側で `bypassPermissions` を指定すると通ってしまう問題が塞がれた。
- **org 制限下の model alias が段階降格するようになった**(v2.1.222 / v2.1.223): 組織の allowlist で `opus` などの family alias がブロックされた場合、従来は**親セッションのモデルへフォールバック**していたが、現在は **同じファミリ内で allowlist が許す最新モデルへ段階的に降格**する。降格時には警告が表示される。
- **`claude agents` が untrusted ディレクトリで workspace trust を要求**(v2.1.225)。
- **`claude agents` view と `--worktree` が GitLab の Merge Request URL に対応**(v2.1.233): GitHub の PR と同様に MR URL を渡せるようになり、view 上では **`!N`** 形式で表示される。
- **agent panel の表示改善**(v2.1.232): 完了した subagent を即座に非表示にし、フッタに `/tasks` へのヒントを出すようになった。
- **カスタム subagent 作成を勧める起動 tip の削除**(v2.1.232): 起動時 tip と `/powerup` の該当ナッジが削除された（公式が「まず組み込みで足りるか試す」方向に寄せた変更）。
- 出典: CHANGELOG v2.1.222 / v2.1.223 / v2.1.225 / v2.1.232 / v2.1.233

---

## セッション間メッセージング (Cross-session messaging)

> **v2.1.224 で追加された新機能**。SubAgent（親子関係）とは別の、**独立したセッション同士**が直接テキストをやり取りする仕組みである。

### SubAgent との違い

| 観点 | SubAgent | Cross-session messaging |
|---|---|---|
| 関係 | 親 → 子（spawn する） | **対等な独立セッション同士** |
| 引き継がれるもの | 親から渡したプロンプト。結果は親へ戻る | **テキストのみ**。会話履歴もファイルも渡らない |
| ライフサイクル | 親セッションに従属 | 互いに独立。片方が終了しても他方は動く |
| 使うツール | `Agent` | **`ListAgents` / `SendMessage`** |

> ⚠️ **`SendMessage` というツール名は Agent teams の teammate 間通信でも使われる**。同名だが、cross-session messaging では「別セッション」が宛先になる点が異なる。

### 使い方

| 操作 | 方法 |
|---|---|
| 到達可能なセッションを探す | `ListAgents` ツール、または **`/list-agents`（alias `/peers`）** |
| メッセージを送る | `SendMessage` ツール |
| **宛先を自分で指名する** | プロンプト内で **`@` + セッション名の先頭数文字**を打ち、typeahead から選ぶ（**v2.1.232〜**。subagent の `@` メンションと同じ操作）。例: `Let @api-worker know the schema migration finished` |
| 自分のアドレスを確認する | **`/status`** に `Peer address` 行が表示される |

#### セッション名の解決（v2.1.229 / v2.1.232 で強化）

- **名前のユニーク化**: 既に live なセッションが使っている名前で起動 / `/rename` すると、**先着のセッションが名前を保持し、後発には variant 名が割り当てられる**。それでも同名が並びうる（片方が旧バージョンの場合など）ため、`/list-agents` は**各ローカルセッションの作業ディレクトリを表示**して判別できるようにしている。
- **bare name での配送**: **その名前に一致する live セッションが 1 つだけなら、`SendMessage` は名前だけで配送する**。複数一致する場合、または ClaudeCode が全ての実行場所を確認できなかった場合にのみ、一覧の各行に短い識別子が付与され、それを含めて宛先指定する。
- **`@` メンションの補完範囲**: `@` の後に 1 文字以上入力すると同一マシンの live セッションが候補に出る（bare `@` では出ない）。クラウド / Remote Control のセッションは、**一度そのセッションを列挙またはメッセージ送信した後**にのみ候補へ現れる。同名の live セッションが複数一致する場合は送信前に確認を求められる。
- **`ListAgents` のラベル（v2.1.229〜）**: クラウドセッションは **`cloud`**、Remote Control 接続が切れたセッションは **`offline`** と表示される。他マシンの Remote Control セッションは `Remote Control` ラベルが付く。

### 制約

- **macOS / Linux のみ**。Windows は非対応。
- **Bedrock / Claude Platform on AWS / Google Cloud / Microsoft Foundry では利用できない**（Claude API / サブスクリプション経由のみ）。
- **v2.1.225 以降は Remote Control 経由で他マシンのセッションにも名前で送信できる**（v2.1.224 時点は同一マシン内のみ）。

### 関連設定

| 設定キー / 環境変数 | 内容 |
|---|---|
| `crossSessionInbound` | 受信ポリシー。`accept` / `hold` / `refuse`。**既定は両セッションの permission mode クラスから自動決定**され、bypass 側が受け手になる場合は `hold` になる |
| `dialogExpiry` | 保留中ダイアログの期限。**既定 `"5m"`**（2026-08-16 訂正。従来 `"10m"` と記載していたが誤り）。受理値は `"60s"` / `"5m"` / `"10m"` / `"never"`。`-p`（print mode）セッションにも適用される |
| `isolatePeerMachines` | `true` で**マシンをまたぐ `SendMessage` に毎回承認を要求**する。`bypassPermissions` 下でも承認を求める。**どのスコープで `true` にしても有効**（安全側に倒す設計） |
| `CLAUDE_CODE_MESSAGING_SOCKET` | セッション固有の inbox socket のパス。**SessionStart より前**から hook / Bash に export される |

> **`/config` からの設定（v2.1.232〜）**: `crossSessionInbound` は **「Messages from your other sessions」**、`dialogExpiry` は **「Dialog expiry」** という行として `/config` に現れる。いずれも user settings に書き込み、managed settings または `--settings` フラグがそのキーを設定している間は行自体が非表示になる。⚠️ **`crossSessionInbound` に限り `/config crossSessionInbound=value` のショートハンド指定は拒否される**。

> **auto mode との関係**: `SendMessage` の**送信内容は送信前に permission classifier が評価する**（v2.1.222）。他セッションへメッセージを投げること自体が、auto mode の審査対象である。

出典: [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [whats-new week 32](https://code.claude.com/docs/en/whats-new/2026-w32) / CHANGELOG v2.1.224 / v2.1.225 / v2.1.229 / v2.1.232

---

## カスタムサブエージェントの作成

### ファイル形式

サブエージェントは YAML frontmatter + マークダウン本文のファイルで定義する。

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

frontmatter がサブエージェントの設定（使えるツール、モデル等）を定義し、マークダウン本文がサブエージェントの**システムプロンプト**となる。

### 配置場所とスコープ

| スコープ | パス | 適用範囲 | Git 管理 |
|---------|------|---------|----------|
| Managed | 企業管理設定で配布 | 組織内の全ユーザー | — |
| CLI | `--agent` フラグ or `--agents` JSON | 当該セッションのみ | しない |
| Project | `.claude/agents/<name>.md` | 当該プロジェクト | **する** |
| User | `~/.claude/agents/<name>.md` | 全プロジェクト共通 | しない |
| Plugin | `<plugin>/agents/<name>.md` | Plugin が有効な場所 | — |

**同名サブエージェントの優先順位**: **Managed > CLI フラグ > Project > User > Plugin**

**使い分え**:
- **Project**: チームで共有したいレビュアーや専門エージェント → `.claude/agents/` に配置して Git 管理
- **User**: 個人で全プロジェクトに使いたいエージェント → `~/.claude/agents/` に配置
- **CLI**: 一時的な実験用エージェント → `--agents` フラグで JSON 定義

### frontmatter リファレンス

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | **Yes** | エージェント識別子。小文字・数字・ハイフン。Hooks には `agent_type` として渡る。**v2.1.218 以降 `:` を含められない**（plugin の名前空間区切りとして予約） |
| `description` | string | **Yes** | Claude がエージェントを自動選択する判断基準。`<example>` ブロックでトリガー条件を具体的に示すと効果的 |
| `tools` | string/string[] | No | 使用可能なツール。例: `Read, Grep, Glob, Bash`。省略時は全ツールを継承。**`Agent(worker) Agent(researcher)` の形式で書くと spawn できる subagent 型を allowlist 制限できる**（`--agent` でメインスレッド起動した agent のみ有効。subagent 定義内では括弧内の型リストは無視される） |
| `disallowedTools` | string/string[] | No | 継承/指定リストから除外するツール（「Write/Edit 以外を全部継承」等に便利）。**`tools` と併用した場合は `disallowedTools` を先に適用し、残ったプールに対して `tools` を解決する**（両方に載ったツールは除去される）。MCP は `mcp__<server>` / `mcp__<server>__*` のサーバー単位パターンが使え、`disallowedTools` では `mcp__*` で全 MCP ツールを除去できる |
| `model` | string | No | 使用モデル。`sonnet`, `opus`, `haiku`, `fable`（Fable 5、要 v2.1.170+）, **フル model ID（例 `claude-opus-5` / `claude-fable-5`）**, `inherit`。**デフォルトは `inherit`**。`opus` は v2.1.219 以降 Opus 5 に解決される |
| `color` | string | No | タスクリスト・トランスクリプトでの表示色。`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` の 8 色 |
| `effort` | string | No | エフォートレベル。`low` / `medium` / `high` / `xhigh` / `max`（使える値はモデルに依存）。セッションの effort を上書き |
| `permissionMode` | string | No | サブエージェントのパーミッションモード。受理値は `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan` / **`manual`（`default` のエイリアス、要 v2.1.200+）**。※ auto mode 配下では無視される。**v2.1.212 以降、指定がなければ親セッションの permission mode を継承する**（同 version で `Task` / `Agent` ツールの `mode` パラメータは **deprecated** となり無視される） |
| `skills` | string[] | No | 起動時にプリロードする Skills のリスト（本文全文が注入される） |
| `mcpServers` | string[]/object | No | このサブエージェントが使う MCP サーバー（既存サーバー名参照 or インライン定義）。plugin サブエージェントでは無視 |
| `hooks` | object | No | エージェントのライフサイクルにスコープされた Hooks |
| `memory` | string | No | 永続メモリのスコープ（`user` / `project` / `local`）。セッションを跨いだ学習を有効化 |
| `background` | boolean | No | `true` で常にバックグラウンドタスクとして実行。デフォルト `false` |
| `isolation` | string | No | `worktree` で一時的な git worktree（リポジトリの隔離コピー、既定で default branch から分岐）で実行。変更がなければ自動削除 |
| `maxTurns` | number | No | 停止までの最大エージェンティックターン数 |
| `initialPrompt` | string | No | `--agent` / `agent` 設定でメインセッションエージェントとして動く時、最初の user ターンとして自動投入される。コマンド・スキルも処理され、ユーザー入力の前に prepend される |

> **`allowed-tools` は subagent の frontmatter フィールドではない（2026-08-04 修正）**: 公式の frontmatter リファレンスに `allowed-tools` は存在しない（これは [Skill](skills.md) 側のフィールドである）。subagent でツールを制限する場合は `tools`（allowlist）または `disallowedTools`（denylist）を使う。本ドキュメントの旧版は誤って `allowed-tools` 行を掲載していた。出典: [Subagents](https://code.claude.com/docs/en/sub-agents)

### description の書き方（トリガー設計）

`description` はClaudeがサブエージェントを自動選択するかどうかの判断基準である。`<example>` ブロックを含めることで、トリガー精度を大幅に向上させる。

**効果的な description の例**:

```yaml
description: |
  Use this agent when reviewing code for security vulnerabilities. Examples:

  <example>
  Context: User has just implemented authentication logic
  user: "Review this code for security issues"
  assistant: "I'll use the security-reviewer agent to analyze your code"
  <commentary>
  Security review is the agent's core expertise
  </commentary>
  </example>
```

**ポイント**:
- 「いつ使うか」を明確にする
- `<example>` ブロックで具体的なトリガーシーンを示す
- ユーザーが自然に使う言葉を含める

### システムプロンプトの設計パターン

frontmatter の下のマークダウン本文がサブエージェントのシステムプロンプトとなる。

**分析型**（コードレビュー、セキュリティ監査）:

```markdown
You are a senior code reviewer ensuring high standards of code quality.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- No duplicated code
- Proper error handling
- No exposed secrets or API keys

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

**調査型**（リサーチ、探索）:

```markdown
You are a codebase researcher. When given a topic:

1. Search for relevant files using Glob and Grep
2. Read and analyze the code thoroughly
3. Trace dependencies and call chains
4. Summarize findings with specific file:line references
```

**生成型**（コード生成、ドキュメント作成）:

```markdown
You are an API endpoint developer. Follow team conventions:

1. Read existing endpoints for patterns
2. Implement the new endpoint
3. Add validation and error handling
4. Write tests
5. Update API documentation
```

---

## SubAgents の使い方

### Claude に委任を指示する

自然言語でサブエージェントの使用を指示する:

```
サブエージェントを使って、認証システムのトークンリフレッシュの仕組みを調査して。
```

```
サブエージェントを使ってこのコードのセキュリティレビューをして。
```

```
サブエージェントを使って、再利用できる既存の OAuth ユーティリティがないか調査して。
```

カスタムサブエージェントが定義されていれば、Claude は description を基に最適なエージェントを自動選択する。

### CLI からの起動

```bash
# セッション全体を特定のサブエージェントとして起動
claude --agent code-reviewer

# 一時的なサブエージェントを JSON で定義
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on quality and security.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors and provide fixes."
  }
}'
```

### デフォルトエージェントの設定

`.claude/settings.json` にデフォルトのサブエージェントを設定できる:

```json
{
  "agent": "code-reviewer"
}
```

この設定により、セッション開始時に `code-reviewer` のシステムプロンプトとツール制限が適用される。CLI フラグ（`--agent`）で上書き可能。

### Skills のプリロード

`skills` フィールドでサブエージェント起動時に Skills を自動ロードする:

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns
from the preloaded skills.
```

**通常の Skills との違い**: メインセッションでは Skills はオンデマンドロードされるが、サブエージェントでは `skills:` フィールドで指定された Skills が**起動時に全文プリロード**される。サブエージェントはメインセッションの Skills を継承しないため、明示的に指定する必要がある。

### Skill からの SubAgent 実行（context: fork）

Skill の frontmatter に `context: fork` を設定すると、その Skill がサブエージェント内で実行される:

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

`agent` フィールドで使用するサブエージェントを指定する。組み込み（`Explore`, `Plan`, `general-purpose`）またはカスタムサブエージェント名を指定可能。

---

## 実践パターン

### パターン 1: Writer/Reviewer 分離

一方のセッションでコードを書き、別のサブエージェントでレビューする。新しいコンテキストでレビューすることで品質が向上する。

```
# セッション A（Writer）
APIエンドポイントにレートリミッターを実装して

# セッション B（Reviewer — サブエージェント）
サブエージェントを使って src/middleware/rateLimiter.ts をレビューして。
エッジケース・競合状態・既存ミドルウェアパターンとの一貫性を確認して
```

### パターン 2: 並列調査

独立した調査を複数のサブエージェントに同時実行させる:

```
以下を並列でサブエージェントに調査させて:
1. 認証システムのトークンリフレッシュの仕組み
2. 再利用できる既存の OAuth ユーティリティ
3. 現在のセッション管理の実装
```

各サブエージェントが独立して探索し、Claude が結果を統合する。**調査パスが互いに依存しない場合**に最も効果的。

### パターン 3: 実装後の検証

コード変更後にサブエージェントで検証する:

```
サブエージェントを使ってこのコードのエッジケースをレビューして。
```

### パターン 4: セキュリティレビュー

カスタムサブエージェント `security-reviewer` を定義して専門的なレビューを実施:

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

使用時: `このコードのセキュリティレビューにサブエージェントを使って`

### パターン 5: 大規模コードベース探索

新しいプロジェクトへのオンボーディング時、サブエージェントに構造調査を委任する:

```
サブエージェントを使って以下を調査して:
- プロジェクトのディレクトリ構造と各モジュールの責務
- 主要なエントリポイントとデータフロー
- テストの構成とカバレッジ
```

### パターン 6: JARVIS Plugin による並列 SubAgent ディスパッチ

`/jarvis {内容}` の単一エントリで、内容に応じて部署 SubAgent を**並列起動**する運用パターン。本リポの JARVIS Plugin v0.6.0 で実装された (`~/.claude/plugins/jarvis/plugins/jarvis/skills/jarvis/SKILL.md` の「並列 SubAgent spawn プロトコル」セクション参照)。

**仕組み**:

1. メイン JARVIS が BOSS の発話をキーワード分類 (前述「部署への振り分け」表)
2. 単一部署で完結する場合は 1 つの `Task` 呼び出し
3. **複数部署横断の場合は 1 アシスタントメッセージ内に複数の `Task` 呼び出しを配置** (並列 fan-out)
4. 各 SubAgent が部署 CLAUDE.md (`.jarvis/[部署]/CLAUDE.md`) を Read して責任範囲を厳守
5. メイン JARVIS が結果を統合し、矛盾がある場合は `AskUserQuestion` で BOSS に判断を仰ぐ

**重要な制約 (SubAgent 仕様より)**:

- SubAgent からは `AskUserQuestion` が使用不可。BOSS への問いはメイン JARVIS のみが担う
- SubAgent は「BOSS 確認が必要な事項」セクションを返却し、メイン JARVIS がそれを集約して `AskUserQuestion` で問う
- nested SubAgent は使わない (フラット並列)
- サブ職能 SubAgent は**事前生成しない** (公式 "Define a custom subagent when you keep spawning the same kind of worker" 準拠)。運用で繰り返しパターンが見えてから SKILL.md の「サブ職能の自動提案」フローで追加する

**使い分け** (`/harness-loop` との対比):

| 用途 | 並列 SubAgent spawn | `/harness-loop` |
|---|---|---|
| 時間スケール | ~30 分、1 往復 | 数時間〜、反復ループ |
| 主観評価ドメイン | 部署観点レビューが目的 | UI/UX 等の Generator/Evaluator 反証 |
| メイン⇔ワーカー通信 | 結果サマリのみ返却 | 同左 (Anthropic 公式の Agent Teams は不採用) |

詳細は本リポ `docs/jarvis/jarvis-harness-integration.md` の「並列 SubAgent spawn ワークフロー」セクションを参照。

---

## コンテキスト管理のベストプラクティス

### いつ SubAgent を使うべきか

| シナリオ | SubAgent を使う | メインで直接やる |
|---------|:---:|:---:|
| 大量のファイル読み込みが必要な調査 | **○** | |
| 数行のコード修正 | | **○** |
| コードレビュー（変更後の検証） | **○** | |
| 単純なファイル編集 | | **○** |
| 並列で独立した調査 | **○** | |
| 会話の文脈が必要なタスク | | **○** |
| 新しいコードベースの全体把握 | **○** | |
| 特定ファイルの小さな質問 | | **○** |

### コンテキスト消費の注意

サブエージェントの結果はメインに返却されるため、**多数のサブエージェントが詳細な結果を返すとメインのコンテキストを消費する**。

対策:
- サブエージェントに「要約して返却」を指示する
- 不要な詳細を省くよう指示する
- 持続的な並列作業が必要な場合は Agent Teams を検討する

### セッション管理

- **ClaudeCode は `~/.claude/agents/` と `.claude/agents/` を watch しており、ファイルの追加・編集は数秒で検出され、次の委任から新定義が使われる（再起動不要）**
- **再起動が必要なのは次の 2 例外のみ**:
  1. **そのスコープで初めて `agents` ディレクトリ自体を新規作成した場合** — watcher はセッション開始時に存在したディレクトリのみを対象にするため、新規作成したディレクトリは検出されない
  2. `--disable-slash-commands` で起動している場合
- ⚠️ **`/agents` に一覧表示 UI はもう無い**（v2.1.198 でウィザード廃止）。現在はリマインダを印字するだけなので、**ロード状況は `.claude/agents/` を直接見る**か Claude に尋ねる（[slash-commands.md](slash-commands.md) 参照）
- 出典: [Subagents](https://code.claude.com/docs/en/sub-agents)（2026-08-04 確認。旧版の「再起動または `/agents` でリロードが必要」は現在の仕様では誤り）

---

## 活用シナリオ別ガイド

### 日常の開発作業での活用

| タスク | 推奨アプローチ | 理由 |
|--------|--------------|------|
| PR のコードレビュー | カスタム `code-reviewer` エージェント | レビュー観点を統一でき、メインコンテキストを汚さない |
| バグの原因調査 | 「サブエージェントを使って調査して」 | 大量のコード読み込みが発生するため隔離が有効 |
| リファクタリング前の影響調査 | Explore エージェント | 読み取り専用で高速に依存関係を調査 |
| テスト追加前のカバレッジ確認 | サブエージェントで既存テストを分析 | テスト構造の全体像を把握してからテストを書ける |
| 新規参画時のオンボーディング | 並列サブエージェントで各モジュールを調査 | 短時間でプロジェクトの全体像を把握 |
| セキュリティチェック | カスタム `security-reviewer` エージェント | 専門的な観点で漏れなくチェック |
| ドキュメント生成 | カスタムエージェント + Skills プリロード | API 規約等の知識をプリロードして一貫性のあるドキュメントを生成 |

### カスタムサブエージェントを作るべき場面

- **同じ種類のタスクを繰り返す**: コードレビュー、セキュリティチェック等
- **専門的な観点が必要**: 特定のチェックリストやレビュー基準がある
- **チームで共有したい**: `.claude/agents/` に配置して Git 管理

### カスタムサブエージェントが不要な場面

- **一回限りの調査**: 「サブエージェントを使って X を調査して」で十分
- **単純なタスク**: メインセッションで直接実行した方が早い
- **会話の文脈が必要**: サブエージェントは会話履歴にアクセスできない

---

## Tips

### proactive な description

`description` に「Use proactively」を含めると、Claude がコード変更後に自動的にサブエージェントを起動する:

```yaml
description: |
  Expert code reviewer. Use proactively after code changes.
```

### model の選択

| モデル | コスト | 最適な用途 |
|--------|--------|-----------|
| `haiku` | 低 | 高速な探索、簡単なチェック |
| `sonnet` | 中 | コードレビュー、一般的なタスク |
| `opus`（v2.1.219 以降は **Opus 5**） | 高（$5/$25 per MTok） | セキュリティ監査、複雑な分析。**code review の実バグ検出率が高く false positive が少ない**ため、低 effort でもレビュー用途に耐える |
| `fable` | 最高（$10/$50 per MTok） | 長時間自律タスク、1M context が必要な大規模 monorepo。要 v2.1.170+ |
| フル model ID（例 `claude-opus-5` / `claude-fable-5`） | 任意 | バージョンを固定したい場合 |
| `inherit`（デフォルト） | 親と同じ | 特にこだわりがない場合 |

> **Opus 5 を subagent に使う場合の注意**: Opus 5 は **委任が過剰になりやすい**性質を持つため、`tools` から `Agent` を外すか `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` で深さを固定して、subagent がさらに subagent を呼ぶ連鎖を意図的に止める設計が有効である。公式も「**自分の作業の verify / double-check に subagent を使わない**」ことを明示的に推奨している（`docs/best-practices.md` §8 参照）。

### ツール制限による安全性

読み取り専用のサブエージェントを作る場合、`tools` フィールドでツールを制限する:

```yaml
tools: Read, Glob, Grep
```

これにより、サブエージェントがファイルを変更したりコマンドを実行したりすることを防ぐ。

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| サブエージェントが起動しない | `/agents` でロード状況を確認。ファイル編集は watch により数秒で反映される（再起動不要）。**そのスコープで `agents` ディレクトリを新規作成した直後だけは再起動が必要** |
| 期待と異なるエージェントが選ばれる | `description` をより具体的にする。`<example>` ブロックを追加する |
| 結果が詳細すぎてコンテキストを圧迫する | 「要約して」を指示に含める。Agent Teams への移行を検討 |
| サブエージェントが会話の文脈を理解しない | 仕様上、会話履歴にアクセスできない。必要な情報はプロンプトで明示的に渡す |

---

## 関連ドキュメント

- [Subagents](https://code.claude.com/docs/en/sub-agents) — 公式 SubAgents ドキュメント
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — 拡張機能の全体像
- [Agent teams](https://code.claude.com/docs/en/agent-teams) — マルチエージェント協調（実験的機能）
- [Skills](https://code.claude.com/docs/en/skills) — Skills との連携（context: fork、skills プリロード）
- [Hooks](https://code.claude.com/docs/en/hooks) — イベント駆動の自動化
- [ClaudeCode Skills ガイド](skills.md) — 本リポジトリの Skills ガイド
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
