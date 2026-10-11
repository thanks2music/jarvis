# ClaudeCode スラッシュコマンドガイド

> 出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) / [Routines](https://code.claude.com/docs/en/routines) / [Fast mode](https://code.claude.com/docs/en/fast-mode) / [Agent view](https://code.claude.com/docs/en/agent-view) / [Workflows](https://code.claude.com/docs/en/workflows) / [Claude directory](https://code.claude.com/docs/en/claude-directory) / [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [whats-new week 32](https://code.claude.com/docs/en/whats-new/2026-w32) / [Output styles](https://code.claude.com/docs/en/output-styles) / [Interactive mode](https://code.claude.com/docs/en/interactive-mode) / [Manage costs](https://code.claude.com/docs/en/costs) / [Status line](https://code.claude.com/docs/en/statusline) / [Checkpointing](https://code.claude.com/docs/en/checkpointing) / [Artifacts](https://code.claude.com/docs/en/artifacts) / [Code Review](https://code.claude.com/docs/en/code-review) / [Model configuration](https://code.claude.com/docs/en/model-config) / [Skills](https://code.claude.com/docs/en/skills) / [Hooks](https://code.claude.com/docs/en/hooks) / [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [whats-new week 34](https://code.claude.com/docs/en/whats-new/2026-w34) / [week 35](https://code.claude.com/docs/en/whats-new/2026-w35) / [week 36](https://code.claude.com/docs/en/whats-new/2026-w36) / [week 37](https://code.claude.com/docs/en/whats-new/2026-w37) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。CHANGELOG は v2.1.296 まで反映)

> **公式説明が確認できず未収録のコマンド**（憶測での記載を避けている。2026-08-16 再確認）:
>
> | コマンド | 状況 |
> |---|---|
> | `/workshop` | 公式 commands ページ全文（185,618 bytes）・docs インデックス（`llms.txt`）・**CHANGELOG 全 5,534 行**を検索して **0 ヒット**。公式に存在の痕跡が見つからない |
> | `/tui` | ✅ **2026-09-03: 公式 commands ページに掲載された**（旧記述の「公式未掲載」は解消済み）。**導入は v2.1.110**（「Added `/tui` command and `tui` setting — run `/tui fullscreen` to switch to flicker-free rendering in the same conversation」）。v2.1.227 / v2.1.228 / v2.1.232 にも修正エントリがある |
> | `/usage-credits`（旧 `/extra-usage`） | ✅ **2026-09-03: 公式 commands ページに「Previously `/extra-usage`」の併記付きで掲載された**（旧記述の「依然未掲載」は解消済み） |
> | `claude rc` | cli-reference にサブコマンドとして存在しない。`--rc` は `--remote-control` の**フラグ**短縮形で、サブコマンド形は `claude remote-control` |

ClaudeCode のスラッシュコマンドは、セッション中に `/` に続けてコマンド名を入力することで実行できる。**組み込みコマンド（Built-in Commands）**と**バンドルスキル（Bundled Skills）**の 2 種類がある。`/` を入力すると利用可能なコマンドが一覧表示され、文字を続けて入力するとフィルタリングできる。

**入力途中の `/` 補完（v2.1.265〜、2026-10-11 追記）**: プロンプトの途中でも、空白の後に `/` と名前の先頭を打つと（例 `run the tests, then /com`）一致するコマンドを**候補一覧から選べる**。fullscreen rendering では入力中に一覧が開き（どの行もハイライトされないので `Enter` はそのまま送信）、`Tab` で先頭候補を挿入するか矢印キーと `Enter` で選ぶ。fullscreen 以外では先頭候補の残りが ghost text で出て、複数一致なら `+2` のような件数が付き、`Tab` で一覧を開く。名前の先頭一致だけを拾うため `/tmp/notes.md` のようなパスでは一覧が開かない。plugin skill は prefix なしの名前でも一致し、挿入時は `/myplugin:deploy-app` のような完全名になる。なお ClaudeCode がコマンドとして実行するのは、メッセージの**先頭**にあるコマンドだけである。出典: [Interactive mode — Complete a command mid-prompt](https://code.claude.com/docs/en/interactive-mode#complete-a-command-mid-prompt) / [whats-new week 37](https://code.claude.com/docs/en/whats-new/2026-w37) / CHANGELOG v2.1.265（以前は単一候補の提示だった）

---

## 前提知識

### 組み込みコマンドとバンドルスキルの違い

| 種別 | 説明 | 例 |
|------|------|----|
| 組み込みコマンド | ClaudeCode 本体に含まれるセッション管理・環境設定コマンド | `/clear`, `/compact`, `/context` |
| バンドルスキル | ClaudeCode に同梱されるタスク実行型スキル。Skills の仕組みで動作する | `/simplify`, `/batch`, `/debug`, `/loop` |

バンドルスキルはサブエージェントや並列処理を活用するため、組み込みコマンドより高度なタスクを実行できる。

### コンテキストウィンドウとの関係

スラッシュコマンドの多くは**コンテキスト管理**に関わる。コンテキストウィンドウが埋まるほどパフォーマンスが低下するため、適切なコマンドで管理することが重要である。

```
会話開始 ──→ コンテキスト蓄積 ──→ /context で確認 ──→ /compact で圧縮 or /clear でリセット
```

---

## 組み込みコマンド一覧

### コンテキスト管理

セッション中のコンテキストウィンドウを管理するコマンド群。**最も頻繁に使うカテゴリ**である。

#### `/clear [name]` — コンテキストリセット

コンテキストウィンドウを**完全にリセット**し、空のコンテキストで新しい会話を始める。無関係なタスク間の切り替え時に使う。**引数に名前を渡すと、直前の会話にその名前が付き、`/resume` のピッカーで見つけやすくなる**。直前の会話は `/resume` で再開でき、同じ ClaudeCode プロセス内なら rewind メニューの previous-session エントリからも戻せる。

> **2026-10-11 訂正**: 以前は「名前はリセット後の新しいセッションに付く」と書いていたが、現行公式 [commands](https://code.claude.com/docs/en/commands) は「Pass a name to label the previous conversation in the `/resume` picker」であり、名前が付くのは直前の会話である。

```
# タスク A 完了後、別のタスク B に取り掛かる前に
/clear

# 直前の会話（タスク A）に名前を付けてからリセット
/clear refactor-auth
```

**使いどころ**:
- 無関係なタスク間の切り替え
- 同じ問題で 2 回以上修正を試みて失敗した場合（コンテキストが失敗アプローチで汚染されている）
- 長時間の会話でコンテキストが膨らんだ場合

#### `/compact [指示]` — コンテキスト圧縮

コンテキストを手動で圧縮する。引数に指示を添えると、圧縮時に**保持すべき情報を制御**できる。

```
# 基本の圧縮
/compact

# 保持する情報を指定
/compact API の変更点に集中して

# 変更ファイルとテストコマンドを保持
/compact 変更ファイルの完全なリストとテストコマンドを必ず保持して
```

**使いどころ**:
- コンテキストが膨らんできたが、会話の文脈は維持したい場合
- `/clear` ほど完全にリセットしたくない場合
- `/context` でコンテキスト使用量を確認した後に実行すると効果的

> **Tips**: CLAUDE.md に `"コンパクト時は変更ファイルのリストとテストコマンドを必ず保持して"` と書いておくと、自動コンパクション時にも重要情報が保護される。

#### `/context [all]` — コンテキスト使用量の確認

コンテキスト使用量を**カテゴリ別**に表示する。**`all` を付けると、通常は省略される項目まで含めた完全な内訳**を表示する。

```
/context
/context all
```

表示されるカテゴリ:
- system prompt
- memory files
- skills
- MCP tools
- messages

**使いどころ**:
- コンテキストの消費状況を把握したい場合
- Skills やMCP ツールがどの程度コンテキストを消費しているか確認したい場合
- Skills の description がコンテキスト予算を超えている場合の警告を確認

#### `/btw <question>` — サイドバー質問

会話履歴に残さずに単発の質問をする。回答はオーバーレイで表示され、コンテキストを汚さない。実装中の細かな確認（API 引数・コマンド名など）に向く。**Claude 実行中でも投げられる**ため、長時間処理を中断せずに横から確認できる。**ツールは使用できない（ファイル読み込み・コマンド実行・検索は不可）ため、既存のコンテキスト内にある情報への質問のみ有効。新たに調べさせたい場合は subagent を使う。**

```
/btw このコマンドの正しいオプション名は？
```

> **引数なしの `/btw`（v2.1.212〜）**: 引数を付けずに `/btw` だけを打つと、**直近のやり取りの side-question パネルを再オープン**する。前の質問と回答を読み直したいときに使う。出典: CHANGELOG v2.1.212

---

### セッション管理

セッションの操作・復元に関するコマンド群。

#### `/rewind` — チェックポイントへの巻き戻し

以前のチェックポイントに巻き戻す。会話のみ・コードのみ・両方の復元と、選んだメッセージを境にした要約ができる。`Esc + Esc` でも起動できる。

```
/rewind
```

**選択肢**:
- **Restore code and conversation**: コードと会話の両方を復元
- **Restore conversation**: 会話のみ復元（コードはそのまま）
- **Restore code**: コードのみ復元（会話はそのまま）
- **Summarize from here**: 選んだメッセージ以降を要約に圧縮する
- **Summarize up to here**: 選んだメッセージより前を要約に圧縮し、以降のメッセージは残す

コード復元の 2 つは、選んだチェックポイント以降に追跡済みのファイル変更がある場合だけ表示される。要約はディスク上のファイルを変えず、元のメッセージも transcript に残る。Summarize の行を矢印キーで選んだ状態で `add context (optional)` に指示を書くと、要約の焦点を指定できる。

> **2026-10-11 訂正**: 以前は要約を「選択したメッセージからの要約」の 1 種類として書いていたが、現行公式 [Checkpointing](https://code.claude.com/docs/en/checkpointing) は **Summarize from here / Summarize up to here の 2 種類**である。

**使いどころ**:
- リスクのある実装を試して失敗した場合の復元
- Claude の回答が意図と異なった場合のやり直し
- 特定地点からの部分圧縮（`Esc + Esc` → `/rewind` → **Summarize from here** か **Summarize up to here**。冒頭の指示を残したまま、冗長なデバッグ部分だけを圧縮できる）

> **注意**: チェックポイントは Claude が行った変更のみを追跡する。外部プロセスの変更は対象外であり、git の代替ではない。
>
> **v2.1.191 での改善**: `/rewind` は **`/clear` を跨いで巻き戻せる**ようになった。`/clear` でコンテキストをリセットした後でも、`/clear` 実行前の会話状態に復帰可能。

#### `/rename [name]` — セッション名の変更

セッションに名前をつける。`claude --resume` で過去のセッションを選択する際に見つけやすくなる。

```
/rename oauth-migration
/rename debugging-memory-leak
```

**使いどころ**:
- 長期にわたる作業ストリームを識別したい場合
- 複数のセッションをブランチのように管理したい場合

#### その他のセッションコマンド

| コマンド | 用途 |
|---------|------|
| `/resume [session]`（alias `/continue`） | ID / 名前 / ピッカーで会話を再開（バックグラウンドセッションも表示）。**v2.1.212 以降、agent view 内での `/resume` は過去セッション（削除済みを含む）のピッカーを開き、選んだ会話を background セッションとして再開する** |
| `/branch [name]` | 現在の会話をこの地点で分岐。元会話は `/resume` で戻れる。分岐したセッションは**独自の session ID を持ち、ピッカーに別行で出る**。「複製へ自分が移る」場合はこちらを使う |
| `/fork [prompt]` | **現在の会話を新しいバックグラウンドセッションへ複製し、自分はこの会話に留まる**（v2.1.212 で再定義）。複製は現時点までの全内容を引き継ぎ、**agent view で独自の行として動く**。以降 2 つのセッションは独立する。プロンプトを渡せば複製が即座に着手し、渡さなければ agent view で最初のプロンプトを待つ。**v2.1.221 以降、複製セッションには「（その場で編集するケースを除き）独自の worktree を作れ」と指示される**（無条件に worktree が作られるわけではない） |
| `/subtask <instruction>` | **会話内 forked subagent** に脇タスクを渡し、**結果をこの会話へ戻す**（v2.1.212）。会話全体のコンテキストを継承する。**実行中は同時実行スロットを 1 つ占有する**（v2.1.224 で per-session の総数上限は撤廃されたため、消費するのは concurrency 枠のみ）。agent view が無効な環境では `/subtask` が使えず、`/fork` が旧挙動（in-session fork）に戻る |
| `/cd <path>` | セッションを新しい作業ディレクトリへ移動（v2.1.169〜、**v2.1.206 で `/add-dir` と同様の directory 入力補完対応**）。新 dir の `CLAUDE.md` は system prompt 置換ではなく**メッセージ追記**されるため prompt cache を壊さない。session storage も新 dir 配下へ移り、`--resume` / `--continue` が新 dir から会話を見つける。`/add-dir`（移動せずアクセスを追加）とは別物。`Cd` permission rule で対象を制限・無効化できる |
| `/add-dir <path>` | 現在のセッションに作業ディレクトリを**追加**してファイルアクセスを許可する（セッション自体は移動しない。移動は `/cd`）。部分パスを打つと候補が出て `Tab` で確定する。追加したディレクトリの `.claude/` 設定は大半が読み込まれず、`\\server\share` のような大半のネットワークパスは追加できない。追加に成功すると `DirectoryAdded` hook が走る。Claude の応答中に実行すると即座に確認が出て、承認すれば同じターンの次のツール呼び出しから使える（v2.1.234 より前はターン終了まで待たされた） |
| `/recap` | セッションの 1 行要約をオンデマンド生成 |
| `/plan [description]` | プロンプトから直接 plan mode に入る（任意のタスクを即指定可） |

> **⚠️ `/fork` はバージョンで意味が変わる（重要）**: 公式が明記するバージョン別挙動は以下の通りで、**v2.1.212 で役割が入れ替わっている**。本ドキュメントの旧版は v2.1.161〜211 の挙動（forked subagent）を記載していた。
>
> | バージョン | `/fork` の挙動 |
> |---|---|
> | 〜 v2.1.160 | `/branch` の alias（forked subagent が有効化されている場合を除く） |
> | v2.1.161 〜 v2.1.211 | **forked subagent** を spawn し、結果が会話へ戻る（現在の `/subtask` に相当） |
> | **v2.1.212 〜 v2.1.220** | **会話を新しい background セッションへ複製**（元セッションの checkout 内で作業する）。脇タスクを subagent に渡すのは `/subtask`、複製へ自分が移るのは `/branch` |
> | **v2.1.221 〜** | 上記に加えて、**ClaudeCode が複製に「コードを変更する前に独自の worktree を作れ」と指示する**（複製が edits in place になる場合を除く） |
>
> **v2.1.221 の worktree 化の意味**: CHANGELOG の記載は「Changed sessions forked with `/fork` to create a new worktree of their own instead of working in the original session's checkout」。ただし現行公式 [commands](https://code.claude.com/docs/en/commands) と [Agent view](https://code.claude.com/docs/en/agent-view#how-file-edits-are-isolated) が説明する仕組みは**指示**であり、複製が edits in place になる場合は worktree を作らない。Agent view が挙げる worktree を作らない条件は、セッションが既に linked worktree の中にいる、編集対象のファイルが linked worktree の中にある、git リポジトリ外で `WorktreeCreate` hook が無い、working directory の外への書き込み、などである（git 外では hook が作った worktree から移った複製だけが指示を受ける）。したがって**元セッションと fork 先が同じファイルを同時に触る事故は大きく減るが、条件によっては起こりうる**。worktree を作った場合は「fork したのに変更が元の checkout に見えない」挙動になり、**fork 先の成果物は worktree 側にある**（ディスク上の対応は [session-history.md](session-history.md) 参照）。
>
> **2026-10-11 訂正**: 以前は「複製先が独自の worktree を作成するため、同じファイルを壊す事故が構造的に起きなくなった」と書いていたが、現行公式は worktree 作成を「指示」と位置付け、例外条件を明記している。
>
> 出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Agent view](https://code.claude.com/docs/en/agent-view#from-inside-a-session) / CHANGELOG v2.1.221

---

### モデル・推論制御

モデル選択と思考量（effort）を制御するコマンド群。

| コマンド | 用途 |
|---------|------|
| **`/artifacts`** | Artifacts の管理（v2.1.208〜） |
| **`/workflow-authoring`** | workflow スクリプト作成のリファレンスをロード（v2.1.248〜。**保存済み workflow の `.js` を編集する前に実行することが公式推奨**） |
| **`/design [brief]`** | **バンドルスキル**。UI モックアップ・画面遷移・LP・ポスターを 1 つの canvas 上の artboard として下書きし、Claude Design の artifact として公開する（Claude Design の artboard ワークフローを CLI / Desktop に持ち込むもの）。artboard はデスクトップのブラウザで編集でき、PNG / PDF に書き出せる。**現行の要件は v2.1.265+**（commands ページ）・artifacts が使えるセッション・Design テンプレートが有効なアカウントで、組織がテンプレートを OFF にしていると下書きしない。Anthropic API のみで、Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS では使えない。**導入は v2.1.234**（W34 ダイジェスト。当時は research preview として告知）。**2026-10-11 訂正**: 以前は要件を「v2.1.234+」と書いていたが、それは導入版であり、現行の要件は v2.1.265+ である |
| **`/auto-mode-setup`** | auto mode のセットアップウィザード（v2.1.228〜） |
| **`/rate-limit-options`** | レート制限に達した際の選択肢を表示する |
| `/model [model]` | モデル切替。新セッションの既定として保存（ピッカーで `s` を押すと当該セッションのみ。左右キーで effort 調整）。`-p` ではモデル引数付きで使え、当該セッションだけに適用される（v2.1.205+）。エイリアス: `opus` / `sonnet` / `haiku` のほか、Fable 用に **`fable`（v2.1.257 以降は Fable 5.1 に解決。それ以前は Fable 5）**・**`best`（`fable` の解決先、Fable を使えなければ `opus` と同じモデル）**。⚠️ **Fable はどのプラン・プロバイダでもアカウント種別の既定モデルではない**。Claude apps gateway 経由では `fable` は Fable 5 に解決され続ける（Fable 5 の利用自体は v2.1.170+、Fable 5.1 は v2.1.257+）。**5.5 世代（2026-10-11 更新）**: `opus` は **v2.1.280 以降 Opus 5.5**（Anthropic API・Claude Platform on AWS・Bedrock・Google Cloud's Agent Platform。Microsoft Foundry は Opus 4.6 のまま）、Anthropic API の `sonnet` は **v2.1.284 以降 Sonnet 5.5**、`haiku` は **v2.1.293 以降 Haiku 5.5** に解決される（各モデルの利用要件も同じ版）。`default` も Microsoft Foundry 以外は Opus 5.5 になった。v2.1.219〜v2.1.279 の `opus` は Opus 5 だった（Opus 5 の利用には v2.1.219 以上が必須）。プロバイダ別の解決表は [best-practices.md](best-practices.md) §8 と [model-comparison.md](model-comparison.md) §2.1。**2026-10-11 訂正**: 以前は「v2.1.219 以降 `opus` は全プロバイダで Opus 5 に解決」「`fable` は v2.1.255 以降 Fable 5.1」と書いていた。前者は v2.1.280 で Opus 5.5 に交代し、しかも Foundry は対象外だった。後者は公式 [model-config](https://code.claude.com/docs/en/model-config) が v2.1.257 とする |
| `/effort [level\|auto\|status\|ultracode [on\|off]]` | effort 設定。`low` / `medium` / `high` / `xhigh` / `max` / `auto`（**session-only は `max` だけ**、`auto` で当該モデルの保存値をクリア、**`status` で現在の解決結果を表示**）。**ultracode は v2.1.284 以降 effort レベルではなく独立したトグル**で、`/effort ultracode`（または `ultracode on`）で現在の effort のまま当該セッションで ON、`/effort ultracode off` で OFF にする（スライダーでは `Tab`）。常時 ON にするなら設定キー `ultracode: true`。v2.1.284 未満は `/effort ultracode` がセッションを `xhigh` にし、`/effort ultracode off` は `Invalid argument` で失敗した。**画面内で `s` キーを押すとそのセッション限りの変更になる**（v2.1.257〜、`/model` と同挙動）。**既定 effort（2026-10-11 更新）**: **Opus 5.5 / Sonnet 5.5 / Haiku 5.5 は `medium`**、Opus 4.7 は `xhigh`、それ以外の effort 対応モデル（Fable 5.1 / Fable 5 / Opus 5 / Sonnet 5 / Opus 4.8 など）は `high`。⚠️ **effort は v2.1.251 以降モデルごとに保存される**（`modelSettings.<model>.effortLevel`。2026-09-03 訂正）。**モデルを切り替えても旧モデルの値は引き継がれない**。user settings 直下の旧形式 `effortLevel` は Opus 5 / Fable 5.1 以前のモデルには効き続けるが、Opus 5.5 以降のモデルには効かない。model-default hold は **v2.1.280 未満の挙動**（持っていたのは Fable 5 / Opus 4.8 / Opus 4.7）で、現行の解決順は「明示指定 → 設定 → モデル既定」の 3 段である。詳細は [best-practices.md](best-practices.md) §8。Opus 5 では公式が「`high` 起点 + `low`/`medium` を主制御」を推奨し、Opus 5 から Opus 5.5 に移るときは Opus 5 の値を持ち越さず `medium` から始めるよう推奨する。**2026-10-11 訂正**: 以前は「`max`・`ultracode` は session-only」と書き、既定 `high` のモデルとして 5.5 世代以前の 4 モデルだけを挙げていた。現行公式 [commands](https://code.claude.com/docs/en/commands) / [model-config](https://code.claude.com/docs/en/model-config) は ultracode を独立トグル（`ultracode` キーで永続化可）とし、5.5 世代の既定を `medium` とする |
| `/goal [condition\|clear]` | 完了条件を設定し、達成までターンを跨いで継続する **first-class システム**。裏で別の evaluator を spawn し、毎ターン後に完了条件を再チェックする(`docs/best-practices.md` からも参照される key workflow tool)。`clear`/`stop`/`off` 等で解除 |
| `/advisor [model\|off]` | 第 2 モデル相談ツール（advisor tool）の有効化/無効化。タスク中の要所で別モデルに助言を求める。`opus`/`sonnet`/フル model ID を指定、引数なしでピッカー（v2.1.98〜）。設定は `advisorModel`。**v2.1.232 で Fable 5 が再び受理されるようになった**（2026-08-16 更新。従来「`/advisor fable` は拒否される」と記載していたが、現在は **Fable へのアクセスを持つ組織であれば選択可能**。`/model fable` と同様に usage credits の同意が必要） |

> `/fast`（fast mode のトグル）は「その他」節に詳細がある。**v2.1.219 で対象モデルが変わり、v2.1.280 で既定が Opus 5.5 になった**ため併せて参照する。

---

### 環境確認・診断

セッションの状態やロードされているコンポーネントを確認するコマンド群。

#### `/memory` — メモリファイルの確認

メモリファイルの状態を確認する。

```
/memory
```

#### `/agents` — サブエージェント管理のリマインダ

```
/agents
```

**v2.1.198 で対話ウィザード（一覧・作成 UI）は廃止された**。現在の `/agents` は「サブエージェントの作成・管理は Claude に依頼するか、`.claude/agents/` を直接編集せよ」というリマインダを印字するだけのコマンドである。一覧を見たい場合は `.claude/agents/` を直接確認する。

#### `/hooks` — Hooks の閲覧

設定済み Hooks の**読み取り専用ブラウザ**を開く。一覧の各 hook には出所（user / project / local settings・plugin・現在のセッション）が付き、選ぶと実行内容の全文と定義場所（settings ファイルのパスや plugin 名）が見られる。一覧末尾の `All events` で、hook が未設定のイベントも含めて全イベントを閲覧できる。hook の追加・削除は settings ファイルを直接編集するか、`/update-config` で Claude に頼む。

```
/hooks
```

> **2026-10-11 訂正**: 以前は「対話的設定 UI で、既存 Hooks の確認と新規作成ができる」と書いていたが、現行公式 [Hooks — The /hooks menu](https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu) は「a read-only browser for your configured hooks」である。

#### `/mcp` — MCP サーバーステータス

接続中の MCP サーバーのステータスを確認する。

```
/mcp
```

#### `/skills` — Skills 一覧

ロードされている Skills の一覧を確認する。一覧画面の操作は **`t` = token count でのソート、`Space` / `Enter` = 可視性の切替、`Esc` = 保存**である（**2026-09-03 訂正**。旧記述の「`t` で表示のトグル、`Space` で選択」は誤りだった）。

```
/skills
```

#### `/permissions` — パーミッション設定

ツール権限の allow / ask / deny ルールを管理する。安全なコマンドを事前に許可しておくと、承認確認の回数を減らせる。ダイアログではスコープ別のルール閲覧・追加・削除、working directory の管理、**最近の auto mode 拒否の確認**ができる。alias は `/allowed-tools`。

- **Auto mode タブ**（CHANGELOG v2.1.246。W35 ダイジェストで告知）: auto mode classifier のルールを、settings ファイルを開かずに閲覧・編集できる
- **応答中でも開ける**（v2.1.234〜）: Claude の応答中に実行すると即座に開き、変更は同じターンの次のツール呼び出しから適用される。それ以前はターン終了まで待たされた

```
/permissions
```

出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [whats-new week 35](https://code.claude.com/docs/en/whats-new/2026-w35)

#### `/doctor` — 環境診断 + 自動修復 (v2.1.205 で進化)

環境のトラブルシューティングを行う。設定やツールの問題を診断する。**v2.1.205 で単なる読み取り専用レポートから full setup checkup + 自動修復対応の対話型コマンドへ進化**した。診断項目には以下が含まれる:

- インストール健全性
- **新しいバージョンが出ていないかの確認**
- 未使用の Skill / MCP / Plugin と context cost
- checked-in の CLAUDE.md との重複
- **CLAUDE.md の trim と、内容の skills / ネストした CLAUDE.md への移行提案**（v2.1.206+。公式は context ファイルの right-size 手段として `/doctor` を第一に挙げる）
- **auto mode を既定にする提案**
- 遅い hook

問題を検出した場合、**確認後に自動修復**まで実行できるようになった。エイリアス `/checkup` も新設 (v2.1.205)。

**`/doctor prompt-audit [path]`（v2.1.283〜、2026-10-11 追記）**: checkup の代わりに、CLAUDE.md・skills などの指示を「古い指示・矛盾する指示」の観点で監査する。アプリのプロンプトやツール説明を監査する `/claude-api prompt-audit` とは対象が異なる。

```
/doctor
/checkup
/doctor prompt-audit
```

> **`/doctor` は組み込みコマンドではなく[Skill]である**（v2.1.205 で built-in からバンドルスキルへ移された）。`disableBundledSkills` で全バンドルスキルを無効化した場合も、**`/doctor` だけは例外的に残る**（[skills.md](skills.md) 参照）。
>
> シェルから `claude doctor` として実行することもできる。こちらは**読み取り専用**で、自動修復は行わない。

出典: [whats-new week 28](https://code.claude.com/docs/en/whats-new/2026-w28) / [Built-in commands](https://code.claude.com/docs/en/commands) / [Skills — Check your setup with /doctor](https://code.claude.com/docs/en/skills#check-your-setup-with-/doctor)

#### その他の環境確認・診断コマンド

| コマンド | 用途 |
|---------|------|
| `/config`（alias `/settings`） | 設定 UI（テーマ・モデル・出力スタイル・エディタモード等）。**v2.1.181/183 で `/config key=value` シンタックス追加**: 任意設定をプロンプトから直接変更可能(`-p` モード・Remote Control でも動作)、`/config --help` で shorthand キー一覧。⚠️ **`key=value` シンタックスは CLI 前提であり、Claude Desktop の `/config` は `key=value` を無視する**（[claude-desktop.md](claude-desktop.md) 参照） |
| `/status` | 設定 Status タブ（バージョン・モデル・アカウント・接続状況）。**応答中でも割り込まずに即時実行される**。**v2.1.221 以降はセッション種別も表示**（`interactive` / background の `attached` / `unattended`） |
| `/usage`（alias `/cost`, `/stats`） | セッションコスト・プラン使用量・activity stats（`/stats` は Stats タブで開く）。**Pro / Max / Team / Enterprise ではプラン枠の内訳**を表示する: Attribution（skills・subagents・plugins・MCP サーバー別の割合）/ Behavior flags / **Loops**（`/loop` など scheduled task のうちトークン消費が多いものの実行回数・総トークン・run あたりトークン・最終実行）。`d` / `w` で直近 24 時間と 7 日を切り替える。**Session ブロックの `Prompt cache (main)` 行**（v2.1.251+）はメイン会話の request 数・cache から読んだ input の割合・miss 数・warm / cold を示し、v2.1.260 以降は直近 miss の推定原因（例 `likely cause: tool definitions changed`）も出す。statusline スクリプトは同じ値を `prompt_cache` オブジェクトで受け取れる（v2.1.251+）。**v2.1.221 で Stats パネルが cache トークンを合計に含める**ようになり、input / output / cache read / cache write の内訳が表示される |
| **`/usage-credits`** | limit 到達時に usage credits を設定する、または管理者に申請する。ブラウザで [usage-credits の billing 設定](https://code.claude.com/docs/en/costs#add-usage-credits-to-your-subscription)を開く。**Team / Enterprise で billing 権限のないメンバーは、CLI から管理者へ申請を送る**（v2.1.211 以降は「管理者に通知される」旨の確認ダイアログあり）。SSH 等でブラウザを開けない場合は URL を出力する（要 v2.1.205+）。**旧名 `/extra-usage`**。環境変数 `DISABLE_EXTRA_USAGE_COMMAND` で無効化できる |
| **`/upgrade`** | プランのアップグレード（Enterprise プランでは非表示） |
| **`/copy [N]`** | 直近のアシスタント応答をクリップボードへコピー。`N` を渡すと N 番目に新しい応答をコピーする（`/copy 2` で最後から 2 番目）。応答にコードブロックか引用ブロックがあるとピッカーが開き、個別のブロックか応答全体を選べる。**ピッカーで `w` を押すと、選んだものをクリップボードではなくファイルに書き出す**（SSH 越しで便利）。**2026-10-11 訂正**: 以前は `w` を「対象の切替」と書いていた |
| **`/export [filename]`** | 会話をプレーンテキストで出力。ファイル名を渡すと直接書き出し、省略するとクリップボード / ファイル保存を選ぶダイアログを開く |
| **`/desktop`**（alias `/app`） | 現在のセッションを Claude Code Desktop アプリで継続する。macOS または x64 Windows と Claude サブスクリプションが必要 |
| **`/mobile`**（alias `/ios`, `/android`） | モバイルアプリをダウンロードするための QR コードを表示 |
| **`/chrome`** | Claude in Chrome の設定 |
| `/statusline` | ステータスライン設定（自然言語指定 or shell プロンプトから自動構成） |
| `/keybindings` | キーバインド設定ファイルの作成・編集 |
| `/diff` | working tree の変更（Claude の編集とそれ以外の未コミット変更）とターン別の編集を確認する。**fullscreen rendering では会話の横に live の diff panel が開く**（v2.1.260 導入）。classic renderer では差分ダイアログが開く。実体は組み込み mod（表の直後の注記） |
| `/insights` | このマシン上の最近のセッションを分析した HTML レポート（作業しているプロジェクト・使い方・つまずき箇所・試すべき機能）を生成する。**ローカル分析でありクラウド機能ではない**。cloud セッションでは使えない。**2026-10-11 訂正**: 以前は「クラウド連携」の表に置き「セッション分析レポート」とだけ書いていた |
| `/skill-doctor` | 各 skill のコンテキストコストと使用頻度を表示し、OFF にする候補を探す（`/plugin` manager の Stats タブで開く）。要 **v2.1.252+**（commands ページ・W36 ダイジェスト。CHANGELOG の追加記載は v2.1.261）と feature-flag fetching。詳細は [skills.md](skills.md) |

> **`/diff` の live panel（v2.1.260〜、2026-10-11 追記）**: fullscreen rendering で `/diff` を実行すると、会話の横に変更ファイルの一覧（追加・削除行数付き）と各ファイルの diff を示す panel が開き、Claude がファイルを編集するかシェルコマンドを実行するたびに更新される。閉じるにはもう一度 `/diff` を実行するか header の `✕` を押す。幅 144 桁以上の端末では Claude が編集を始めると自動で開き、一度自分で開くと以後のセッションでも自動で開く（閉じれば次に `/diff` するまで閉じたまま）。panel では次の操作ができる。
>
> - ファイル名右の `ask` で、そのファイルの diff を次のプロンプトに添付する
> - header の `source` picker でターン単位（`T1`, `T2`, …）の編集を表示する。ターン表示は git ではなく Claude のファイル編集から作るため、シェル経由の変更は `Current`（working tree）にだけ出る
> - `Ctrl+X B` で比較対象を「このセッションの変更 → 未コミットの変更全体 → default branch からの分岐以降」と切り替える（リポジトリごとに記憶）
> - テストファイル・生成ファイルと、セッション開始前からの変更は折り畳まれ、件数行のクリックで展開する
>
> 導入は CHANGELOG v2.1.260 / [whats-new week 36](https://code.claude.com/docs/en/whats-new/2026-w36)。現行の [Interactive mode — Diff panel](https://code.claude.com/docs/en/interactive-mode#diff-panel) が示す panel の要件は **v2.1.287 以上・fullscreen rendering・git リポジトリ・幅 110 桁以上**である。classic renderer のダイアログは `HEAD`（または panel で最後に選んだ比較対象）と比べる。
>
> **`/diff` は組み込み mod である**: panel もダイアログも、ClaudeCode に組み込まれた mod `cc-plugin-diff` が描画している。`/plugin` でこの mod を無効にしても `/diff` は残り、ClaudeCode 本体の以前の panel と diff viewer が応答する。mod（関数 hook を持つ plugin）の仕組みは [mods.md](mods.md) を参照。出典: [Mods overview — Mods built into Claude Code](https://code.claude.com/docs/en/plugins/mods/overview#mods-built-into-claude-code)

---

### 初期設定・プロジェクト設定

#### `/init` — CLAUDE.md の自動生成

プロジェクトのビルドシステム・テストフレームワーク・コードパターンを検出し、CLAUDE.md のスターターを**自動生成**する。

```
/init
```

**使いどころ**:
- 新しいプロジェクトで ClaudeCode を使い始める時
- CLAUDE.md がまだ存在しないプロジェクトで実行

> **Tips**: `/init` で生成した CLAUDE.md は出発点であり、時間をかけて育てていく。Claudeが同じミスを繰り返す場合はルールを追加し、Claudeが指示なしで正しく動作するルールは削除する。

#### `/sandbox` — サンドボックスモード

OS レベルのサンドボックスモードを有効化する。ファイルシステム・ネットワークアクセスを制限し、その範囲内で Claude が自由に作業できる。

```
/sandbox
```

---

### Plugin 管理

#### `/plugin` — Plugin の管理 UI

Plugin の対話的管理 UI を開く。Discover タブからマーケットプレイスの Plugin を閲覧・インストールできる。

```
# 対話的 UI を開く
/plugin

# インストール
/plugin install formatter@my-marketplace

# アンインストール
/plugin uninstall formatter@my-marketplace
```

#### `/reload-plugins [--force]` — Plugin のリロード

Plugin の変更を即時反映する。ClaudeCode の再起動は不要。

```
/reload-plugins
```

#### `/plugin-authoring` — mod 作成リファレンスのロード (v2.1.287〜)

Claude が mod（ClaudeCode のイベントに関数 hook で割り込む plugin）を書くときに使うリファレンスをロードする。mod を頼めば Claude が自分でロードすることもある。バンドルスキルではなく**組み込み plugin が提供する skill** で、`/plugin` から OFF にできる。mod の仕組みは [mods.md](mods.md) を参照。

```
/plugin-authoring
```

出典: [Built-in commands](https://code.claude.com/docs/en/commands)

---

### その他

#### Artifacts (v2.1.198〜)

セッション出力を **claude.ai 上のプライベート live URL として公開** する機能。編集中もその URL がリアルタイム更新される。ダッシュボード・レポート・データ可視化を Claude Code 内から共有したいときに使う。

- **対応**（2026-10-11 時点の公式 Availability）: プランは **Pro / Max / Team / Enterprise**。セッションが **claude.ai アカウントで `/login` していること**が必要で、API キー・gateway token・クラウドプロバイダの資格情報で動くセッションからは公開できない。モデルプロバイダは Anthropic API のみ（**Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry 非対応**）。組織で **CMEK / HIPAA / ZDR** が有効だと使えない。Pro / Max では共有するまで自分専用で admin 管理は無く、Team / Enterprise では既定 ON で Owner が claude.ai admin settings から組織単位で OFF にできる
- **ショートカット**: `Ctrl+]` で最新 artifact を再度開く
- **無効化**: `/config` の Artifacts 行を OFF（user settings に `enableArtifact: false` が書かれる）/ 設定 `"enableArtifact": false`（deprecated の `"disableArtifact": true` も引き続き効く）/ 環境変数 `CLAUDE_CODE_DISABLE_ARTIFACT=1` / `permissions.deny` に `Artifact`。project / local settings の `enableArtifact: false` は v2.1.242 以降で有効になり、そこに `true` を書いても再有効化はできない
- **OFF の固定**: `--settings`・`CLAUDE_CODE_DISABLE_ARTIFACT`・管理者の managed settings のいずれかで OFF にすると、どの設定ファイルからも ON に戻せない（組織単位の OFF は前述の claude.ai admin settings）
- **2026-10-11 訂正**: 以前は見出しを「Team / Enterprise beta」、対応を「Team / Enterprise の Anthropic API 認証のみ」、無効化キーを `disableArtifact` と書いていた。現行公式は Pro / Max も対象とし、claude.ai ログインを必須とし、無効化キーを `enableArtifact: false`（`disableArtifact` は deprecated）としている。また「managed setting `enableArtifact` は v2.1.196 から」と書いていたが、この版数は現行の公式 docs と CHANGELOG で確認できないため外した
- 出典: [Artifacts — code.claude.com](https://code.claude.com/docs/en/artifacts)

**2026 week 29 の拡張**:

- **閲覧者自身の MCP connector を呼べる**ようになった。公開済み artifact が閲覧のたびにライブデータを取得し、アクションを実行できる(閲覧者の権限で動く点に注意)
- **public sharing links** に対応
- **editor role**(Team / Enterprise)を追加。閲覧のみでなく編集権限を付与できる
- **[Claude Tag](claude-tag.md) セッションからの artifact 作成**に対応。公開した artifact は
  **owner 単位の共有設定ではなくチャンネル単位のアクセス制御**になる
  (出典: [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) —
  "the same artifacts Claude Code publishes, with channel-based access in place of owner-controlled sharing")
- 出典: [What's new — week 29](https://code.claude.com/docs/en/whats-new/2026-w29)

#### Shell mode `!` の自動応答 (v2.1.186〜)

シェルモード `!` でコマンドを実行した際、**Claude が実行結果を解釈して自動的に応答する**動作がデフォルトに。例: `! npm test` を打つとテスト結果を読んで次のステップを提案する。

- 従来の「context に結果を追加するだけで応答は返さない」挙動に戻すには、設定 `respondToBashCommands: false`
- 出典: CHANGELOG v2.1.186

#### `/dataviz` — チャート/ダッシュボード設計スキル (v2.1.198〜)

チャート・ダッシュボードの設計ガイドを提供するバンドルスキル。**カラーパレット validator** を内蔵し、アクセシビリティ・コントラスト比の観点で警告を出す。

- 出典: CHANGELOG v2.1.198

#### `/fast` — Fast モードのトグル

Fast モード（高速出力）を切り替える（`/fast [on|off]`）。**モデルは変わらず**、出力速度のみ向上する。特定モデル固定の機能ではなく、対応する Opus 世代で使えるトグルである。

```
/fast
```

**対象モデルの変遷**（対象は世代ごとに入れ替わっている）:

| バージョン | fast mode の既定 | 対象モデル |
|---|---|---|
| v2.1.142 〜 v2.1.153 | **Opus 4.7** | Opus 4.6 / 4.7 |
| v2.1.154 〜 v2.1.218 | **Opus 4.8** | Opus 4.7 / 4.8（**Opus 4.6 は deprecated**） |
| v2.1.219 〜 v2.1.279 | **Opus 5** | Opus 5 / Opus 4.8（**Opus 4.7 を削除**） |
| **v2.1.280 〜** | **Opus 5.5** | **Opus 5.5 / Opus 5 / Opus 4.8** |

> **2026-10-11 訂正**: 以前は 1 行目を「〜 v2.1.153 の既定は Opus 4.6」と書いていたが、現行公式 [Fast mode](https://code.claude.com/docs/en/fast-mode) は v2.1.142〜v2.1.153 の既定を Opus 4.7 とする。v2.1.141 以前の既定は公式に記載が無い。

- 料金は **Opus 5.5 が $8 / $40 per MTok、Opus 5 / Opus 4.8 が $10 / $50 per MTok**（いずれも標準の 2 倍の価格・約 2.5 倍速）で、1M context の全域にフラット適用される。
- **fast mode は Anthropic API（Console）とサブスクリプションのみ**（Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS では利用不可、research preview）。
- **`-p`（非対話モード）では、`claude -p --settings '{"fastMode": true}'` のように `--settings` で fast mode を指定して起動したセッションでのみ `/fast` が効き**、その切替はそのセッション限りで既定として保存されない（v2.1.205+）。それ以外の `-p` セッションでは使えない旨が返る（cloud セッションは別扱い）。
- ⚠️ **サブスクリプションでは「プラン枠を消費せず usage credits から引かれる」**（重要）: 公式は「fast mode is available **via usage credits only and not included in the subscription rate limits**」「Fast mode usage **draws directly from usage credits, even if you have remaining usage on your plan** … charged at the fast mode rate **from the first token**」と明記している。プランに使用量が残っていても fast mode は credits 側から課金される。詳細と初回有効化コストは [model-comparison.md](model-comparison.md) §6.5 を参照。
- **v2.1.221 以降、セッション途中で usage credits が尽きた場合はストリーム上に報告される**（それ以前は silent failure だった）。
- **Opus 4.7 の扱いは v2.1.221 で正常化された（2026-08-12 更新）**。現行の公式 [Fast mode](https://code.claude.com/docs/en/fast-mode) は「Claude Code treats Opus 4.7 **like any other model without fast mode support: switching to it turns fast mode off**」と記載し、「**before v2.1.221**, fast mode stayed on … and the API rejected the requests」と原因も明示している。**Opus 4.7 に切り替えると fast mode は自動 OFF** になる。以前ここに書いていた「公式内で表現が揺れている」という警告は解消済みのため削除した。
- 出典: [Fast mode](https://code.claude.com/docs/en/fast-mode#understand-the-cost-tradeoff) / CHANGELOG v2.1.219 / `docs/model-comparison.md` §6.5

> 旧版の本ドキュメントは「同じ Opus 4.6 モデルのまま」と記載していたが、Fast モードは特定モデルに紐づくものではなく、対応する Opus 世代で利用できるトグルである（公式 `commands` リファレンスでは「Toggle fast mode on or off」とのみ記載）。

#### `/help` — ヘルプ表示

ClaudeCode の使い方・ヘルプを表示する。

```
/help
```

#### `/login` / `/logout` — 認証管理

ClaudeCode の認証ログイン・ログアウトを行う。

```
/login
/logout
```

#### UI・表示の切替

| コマンド | 用途 |
|---------|------|
| `/theme` | カラーテーマ変更（`auto`・colorblind 対応・light/dark 等） |
| `/focus` | フォーカスビュー切替（旧 `Ctrl+O`。直近プロンプト・edit diffstat 付きの 1 行ツール要約・最終応答だけを表示）。**fullscreen rendering 専用**。選択はセッションを跨いで保持され、設定 `viewMode` で上書きできる。Remote Control クライアントからは `/focus [on\|off]` で、保存値を変えずに当該セッションだけ切り替えられる（v2.1.281+） |
| `/tui [default\|fullscreen]` | TUI レンダラ切替。`fullscreen` でちらつきのない alt-screen レンダラ |
| `/color [color\|default]` | 当該セッションのプロンプトバーの色を設定する（`red` / `blue` / `green` / `yellow` / `purple` / `orange` / `pink` / `cyan`）。`default` で戻し、引数なしならランダム。Remote Control 接続中は claude.ai/code に同期する。`-p` でも使える（v2.1.205+） |
| `/output-style [style]` | output style の一覧表示・切替（例 `/output-style concise`）。引数なしで選べる style を一覧し、現在の style に印を付ける。`-p`・Agent SDK・Remote Control からも使える（Remote Control では組み込み style のみ）。要 v2.1.269+。詳細は本書末尾の「組み込み "Concise" output style」 |

> **廃止済みコマンド**: `/vim`（v2.1.92 廃止 → `/config` の Editor mode へ）、`/pr-comments`（v2.1.91 廃止 → Claude に直接 PR コメント参照を依頼）。
>
> **v2.1.205 で non-interactive mode 対応**: `/color` / `/effort` / `/fast` / `/mcp` / `/rename` に加え、**`/model` / `/config key=value` / `/import`** も `-p` フラグでの非対話実行に対応する。CI・スクリプト・バッチワークフローからこれらのコマンドを呼び出せる（従来は対話セッション限定）。ただし **`/fast` は `--settings` で `fastMode` を指定して起動した `-p` セッションでのみ効く**（2026-10-11 追記。「その他」節の `/fast` 参照）。出典: [Commands — code.claude.com](https://code.claude.com/docs/en/commands) / [Fast mode](https://code.claude.com/docs/en/fast-mode#toggle-fast-mode)。
>
> **v2.1.206 での挙動改善**: プラグインコマンド `/commit-push-pr`（commit-commands プラグイン）は、`origin` に加えて **configured push remote への push を auto-allow** するようになった。auto mode 下でも自然に走る。
>
> **v2.1.229 での引き締め（2026-08-16 追記）**: 上記の auto-allow は **危険フラグ付きの git 操作には適用されなくなった**。`--force` / `--amend` / `--no-verify` などを伴う場合は**通常どおり承認が求められる**。グローバルルール（force push 禁止・`--no-verify` 禁止）とも整合する変更である。出典: CHANGELOG v2.1.229

#### その他のコマンド

公式 commands リファレンスに掲載のあるその他の組み込みコマンド。

| コマンド | 用途 |
|---------|------|
| `/release-notes` | リリースノートの表示 |
| `/team-onboarding` | チーム導入オンボーディングの開始 |
| `/install-github-app` | GitHub App のインストール |
| `/install-slack-app` | Slack App のインストール |
| `/setup-bedrock` / `/setup-vertex` | Amazon Bedrock / Google Cloud's Agent Platform の認証・リージョン・model pin を設定する対話ウィザード。コマンドメニューにはそれぞれ `CLAUDE_CODE_USE_BEDROCK=1` / `CLAUDE_CODE_USE_VERTEX=1` を設定するまで表示されないので、フルネームで入力する。初めて使う場合はログイン画面からも開ける（2026-10-11 更新: 旧記述は「Google Vertex AI」だったが、公式の呼称は Google Cloud's Agent Platform） |
| `/privacy-settings` | プライバシー設定の確認・変更 |
| `/heapdump` | ヒープダンプの取得（診断用） |
| `/autocompact [auto\|<tokens>]` | auto-compact の発動閾値を設定する（v2.1.221+）。`auto` で自動判定に戻す |
| `/import [codex\|gemini\|cursor] [--dry-run] [--yes]` | OpenAI Codex / Google Gemini CLI / Cursor の設定（指示ファイル・MCP サーバー・commands・subagents・skills）を ClaudeCode へ取り込む（v2.1.213+。**Cursor は v2.1.265+**）。`--dry-run` で書き込まずにプレビュー、`--yes` で対話ピッカーを省略する。`-p` では見つけた内容と確定用コマンドを表示する。Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS・Claude apps gateway 経由・feature-flag fetching 無効時は使えない |
| `/ide` | IDE 拡張との接続状態を確認・接続する |
| `/voice [hold\|tap\|off]` | 音声入力モードの切替 |
| `/terminal-setup` | ターミナルのキーバインド等をセットアップする |
| `/exit`（alias `/quit`） | セッションを終了する |
| `/powerup`・`/passes`・`/radio`・`/stickers`・`/scroll-speed` | 補助・遊び系コマンド（ニッチ） |

#### 主なエイリアス

| 正式コマンド | エイリアス |
|-------------|-----------|
| `/clear` | `/reset`, `/new` |
| `/bug` | `/share` |
| `/rewind` | `/checkpoint`, `/undo` |
| `/loop` | `/proactive` |
| `/resume` | `/continue` |
| `/config` | `/settings` |
| `/usage` | `/cost`, `/stats` |
| `/tasks` | `/bashes` |
| `/teleport` | `/tp` |
| `/remote-control` | `/rc` |
| `/background` | `/bg` |
| `/permissions` | `/allowed-tools` |
| `/schedule` | `/routines` |
| `/exit` | `/quit` |
| `/list-agents` | `/peers` |
| `/review` | （`/code-review` の **alias 側**。v2.1.223〜） |

> **`/bug` と `/feedback` は別コマンドで、`/share` は `/bug` の alias である（v2.1.212〜）**。v2.1.212 より前は `/bug` と `/share` がともに `/feedback` の alias だった。`/feedback` に alias は無い。2 つは同じダイアログ・同意画面を使うが、Claude が下書きした feedback があるセッションでは、引数なしの `/feedback` は下書きキューを開く（`/bug` は常にダイアログを直接開く）。**2026-10-11 訂正**: 以前ここでは「`/feedback` の alias は `/share`」と書き、alias 表にもそう載せていたが、現行公式 [commands](https://code.claude.com/docs/en/commands) では `/share` は `/bug` の alias である。

> **バンドルスキル alias の不具合修正（v2.1.233、2026-08-16 追記）**: `/checkup` / `/review` のようなバンドルスキルの alias が、**`-p`（print mode）や plugin / MCP をロードした状態で "Unknown command" になる**不具合が修正された。以前この現象に遭遇していた場合、原因はコマンド名ではなくこのバグである。
>
> **`/feedback` / `/bug` の応答性改善（v2.1.232〜）**: Claude が応答生成中でも**即座に開く**ようになった（従来はターンの終了を待たされた）。**2026-10-11 訂正**: 以前は v2.1.228〜 と書いていたが、commands ページと CHANGELOG はともに v2.1.232 としている。

> **print mode のモデル指定ミスの診断（v2.1.233）**: `-p` 実行で未知の model ID を指定した場合、**stderr に `[claude-code:unrecognized_model]` という診断が出る**ようになった。`modelOverrides` で正しいマッピングを与えれば解消する。サイレントに別モデルへフォールバックして気付けなかった問題への対処である。

---

### 並列・バックグラウンド

セッションやタスクを並行実行・管理するコマンド群。

| コマンド | 用途 |
|---------|------|
| `/background [prompt]` | セッションをバックグラウンドエージェント化してターミナルを解放 |
| `/tasks`（alias `/bashes`） | セッション内バックグラウンドタスクの一覧・管理 |
| `/workflows` | ワークフロー進捗ビュー（実行中/完了の監視・一時停止・保存）。**実行中の workflow では、効いている size guideline が workflow の `Running in background` 行に表示される**（v2.1.219〜。2026-10-11 訂正: 以前は「status line に表示される」と書いていた） |
| `/subtask <instruction>` | 会話内 forked subagent に脇タスクを渡す（v2.1.212。旧 `/fork`。「セッション管理」節も参照） |
| `/list-agents`（alias `/peers`） | **メッセージを送れる到達可能なセッションの一覧**（v2.1.224）。cross-session messaging 用。`/status` にも `Peer address` 行が追加される。詳細は [sub-agents.md](sub-agents.md) の cross-session messaging 節を参照 |
| `/stop` | **アタッチ中の background セッション**（または peek reply の送り先のセッション）を停止する。transcript と worktree は残る。停止せずに離れるなら `/exit` か `←`。**2026-10-11 訂正**: 以前は「その他のコマンド」の表で「実行中の処理を停止する」と書いていた |

> **dynamic workflow の既定サイズが変わった（v2.1.219）**: dynamic workflows（ultracode が ON のときに Claude が計画するもの）の既定が **medium size guideline（agent 10 体未満を目標）** になった。**v2.1.271 以降、Pro プランでサインインしている場合の既定は `small`（5 体未満）**である。`/config` の「Dynamic workflow size」または設定キー **`workflowSizeGuideline`** で変更でき、受理値は **`unrestricted`（目安なし）/ `small`（5 体未満）/ `medium`（10 体未満、既定）/ `large`（50 体未満）** の 4 種である。**「1 セッションで数百の並列 subagent」は既定挙動ではなくなった**点に注意（詳細は `docs/harness.md` §4.7）。dynamic workflows は全有料プラン・Anthropic API・Bedrock / Google Cloud's Agent Platform / Microsoft Foundry で使え、**Pro では `/config` の Dynamic workflows 行で有効化が必要**である。**2026-10-11 訂正**: 以前は medium を「agent 15 体未満」と書いていたが、公式 [Workflows](https://code.claude.com/docs/en/workflows) は 10 体未満である。
>
> これは **cap ではなく「助言」** で、公式は「sends the guideline to Claude as **advice, not a cap**」と明記している。プロンプト側が別スケールを要求すれば上書きされる。また **自分で guideline を選ぶと `Large workflow` 警告の閾値 25 体がその agent 数に置き換わる**（ultracode 有効時は警告自体が出ない）。
>
> ✅ 2026-07-26 時点で本ドキュメントが注記していた「公式 docs が CHANGELOG に追従していない」不整合は、**公式側の追従により解消済み**（公式 [workflows](https://code.claude.com/docs/en/workflows) が「The default is `medium` … Requires Claude Code v2.1.219 or later; earlier versions default to `unrestricted`」と明記）。出典: [Workflows](https://code.claude.com/docs/en/workflows) / CHANGELOG v2.1.219

> **workflow の保存・配布・上限・無効化（2026-10-11 追記）**:
>
> - **保存**: `/workflows` で run を選んで `s` を押すと、その script を command として保存できる。保存先は project の `.claude/workflows/`（clone した全員と共有）か `~/.claude/workflows/`（自分だけ）で、以後 `/<name>` で実行できる。同名なら project 側が優先する。保存先の symlink は拒否される（project 側は `.claude` / `.claude/workflows` / 対象ファイル、personal 側は対象ファイルのみ検査）
> - **配布**: plugin の root に `workflows/` を置くと、`/<plugin名>:<meta.name>` として配布できる
> - **編集後の反映**: 保存済み script を編集したら `/reload-skills` で workflow ディレクトリを再読込してから `/<name>` を実行する
> - **runtime の上限**: 同時 agent 16（CPU が少ないと減る。`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` で 1〜256、v2.1.269+）・1 run あたり 1,000 agent・`parallel()` / `pipeline()` 1 回あたり 4,096 item。agent 25 体超か予測トークン 1.5M 超で `Large workflow` 警告が出る（助言のみで止めない）
> - **無効化**: `/config` の Dynamic workflows 行・設定 `disableWorkflows: true`・`CLAUDE_CODE_DISABLE_WORKFLOWS=1`。組織全体なら managed settings の `disableWorkflows` か Claude Code admin settings
>
> 出典: [Workflows](https://code.claude.com/docs/en/workflows)

---

### クラウド連携（Claude Code on the web）

クラウド実行・リモート連携系のコマンド群。各機能の詳細解説は別途整備予定（クラウド機能ガイド）。

| コマンド | 用途 |
|---------|------|
| `/ultrareview [PR or branch]` | クラウドサンドボックスで多エージェントの深いレビュー（推奨呼び出しは `/code-review ultra`、`/ultrareview` は alias として存続）。PR 参照を渡すとその PR をレビュー、ブランチ名を渡すと比較基準を変更する。**Pro / Max は 3 回まで無料、以降は usage credits が必要**。**v2.1.221 でエラーメッセージが改善**され、base と履歴を共有しない repo・ブランチのない checkout は事前に拒否して案内を出すようになった（既に完全な clone に対して `git fetch --unshallow` を勧める誤案内も修正） |
| `/schedule [description]` | routines（Anthropic 管理クラウドで定期実行）の作成・更新・一覧・実行 |
| `/teleport`（alias `/tp`） | クラウドの web セッションをこのターミナルに引き込む（ブランチ + 会話を取得） |
| `/remote-control`（alias `/rc`） | このセッションを claude.ai からのリモート操作に開放 |
| `/autofix-pr [prompt]` | 現ブランチの PR を監視し、CI 失敗・レビュー時にクラウドセッションが修正を push |
| `/web-setup` | ローカル `gh` CLI の認証情報で GitHub アカウントを Claude Code on the web に接続（`/schedule` 実行時に未接続なら自動で促される） |
| `/remote-env` | `--remote` で起動する web セッションの既定リモート環境を設定 |
| `/design-sync [name]` | **バンドルスキル**。リポジトリの React デザインシステムを [Claude Design](https://claude.ai/design) にアップロードし、Claude Design が生成する成果物に**実在のコンポーネント**を使わせる。名前の指定も可（例: `/design-sync Acme DS`）。初回同期は全コンポーネントを検証するため、大規模リポでは数時間かかる。**Anthropic API のみ**（claude.ai への接続が必要で、CLI が claude.ai に接続しない Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude Platform on AWS と、**Claude apps gateway 経由**では利用不可。gateway は 2026-10-11 追記） |
| `/design-login` | `/design-sync` 用に、claude.ai アカウントでデザインシステムアクセスを認可する |

> **`/ultraplan` は v2.1.222 で削除された（2026-08-12 更新）**。公式コマンド表も「`/ultraplan <prompt>` | **Removed. Use plan mode instead.**」と記載し、CHANGELOG v2.1.222 も「Removed ultraplan feature」として **`ultraplan` キーワードごと削除**したと明記している。クラウド上で計画を練りたい場合は **plan mode** か **Claude Code on the web** を使う。
>
> シェルから `claude --teleport <session id>` でクラウドセッションをローカルに引き込めるようになった（v2.1.223）。クラウドセッション側でも `/teleport` のヒントが表示される。

> **`/schedule` と scheduled-tasks ページの再編**: 公式 [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks) ページは現在 **`/loop`（ローカル定期実行）中心**に再編された。`/loop` 側が `CronCreate` / `CronList` / `CronDelete` ツール・7 日 expiry・jitter・`loop.md` カスタマイズ・`CLAUDE_CODE_DISABLE_CRON` を伴う。一方 `/schedule`（routines = クラウド定期実行）の詳細は別ページ [routines](https://code.claude.com/docs/en/routines) に分離され、クラウド / API / GitHub トリガー・最小 1 時間間隔で動作する。`/schedule` の役割（routines の作成・更新・一覧・実行）自体は変わらない。

---

## バンドルスキル

ClaudeCode に同梱されているタスク実行型のスキル。組み込みコマンドと異なり、サブエージェントや並列処理を活用して高度なタスクを実行する。

### `/simplify [target]` — コード品質クリーンアップ

変更されたコードを **4 つの並列サブエージェント**で自動レビューし、修正を適用する。

```
# 最近の変更全体をレビュー
/simplify

# 特定のパス / PR を対象にする
/simplify エラーハンドリング
```

**4 つのレビュー観点**:
- 既存ヘルパーの再利用
- 簡素化（simplification）
- 効率性（efficiency）
- 適切な抽象度（altitude）に収まっているか

**使いどころ**:
- 実装完了後のセルフレビューの代替として
- PR 作成前の品質チェック
- リファクタリング後の検証

> **仕様変遷（エイリアス的統合 → 再分離）**: `/simplify` と `/code-review` の関係は **v2.1.154 を境に変わった**。
> - **v2.1.153 以前**: `/simplify` は `/code-review --fix` と **equivalent（同等）**で、バグ検出も含む統合機能だった（実質的にエイリアスのように振る舞っていた）。
> - **v2.1.154 以降**: `/simplify` は **クリーンアップ専用**として再分離され、**correctness bug（正しさの不具合）を探さない**。バグ検出は `/code-review` の担当に明確化された。
>
> 公式 verbatim（commands リファレンス、`min-version: 2.1.154` マーカー付き）:
> > From v2.1.154, the review does not look for correctness bugs. Use `/code-review` to find bugs. On earlier versions `/simplify` is equivalent to `/code-review --fix`.
>
> **実行順序の推奨: `/code-review` を先に → `/simplify` を後に。** 理由は 2 点。
> 1. **バグ修正はコード構造を変える行為**であり、先に `/simplify` で整形しても後続のバグ修正で手戻りが発生する。正しさを先に担保するのが合理的。
> 2. 公式ベストプラクティスは、完了前の "adversarial review step" として `/code-review`（fresh subagent での diff 検証）を**名指しで推奨**している（`/simplify` ではない）。
>
> 具体的な流れ: `/code-review`（検出のみ）→ 内容を確認して適用 → 仕上げに `/simplify`（再利用・簡素化・効率・抽象度まで深掘り）。`--fix` での即適用は差分が膨らむため、初回は検出のみが無難。
>
> 出典: [Commands](https://code.claude.com/docs/en/commands) / [Best practices](https://code.claude.com/docs/en/best-practices)（2026-06-18 確認）

### `/batch <instruction>` — 大規模並列変更

大規模な変更を**並列で処理**する。コードベースを調査して作業を 5〜30 の独立ユニットに分解し、**計画を提示する**。**承認すると**、ユニットごとに隔離した worktree で background subagent を 1 体ずつ起動し、各 subagent が実装・テスト・変更の publish を行う。git リポジトリか、worktree を作る `WorktreeCreate` hook が必要で、git リポジトリ外での実行は v2.1.281 以降に限られる。**2026-10-11 訂正**: 以前は「指示を自動分解して各 worktree で作業・PR 作成まで行う」と書き、計画の提示と承認の段階を落としていた（出典: [Built-in commands](https://code.claude.com/docs/en/commands)）。

```
# 大規模なリファクタリング
/batch すべてのコンポーネントで PropTypes を TypeScript の型定義に移行して

# コードベース全体の一括変更
/batch すべての console.log を logger.info に置き換えて
```

**使いどころ**:
- 大規模なマイグレーション（フレームワーク移行、API バージョンアップ）
- コードベース全体に及ぶ一括変更
- 複数ファイルへの同じパターンの適用

> **Tips**: 最初の 2〜3 ファイルで結果を検証してからフルスケールで実行するのが安全。

### `/debug [description]` — セッションデバッグ

セッションのデバッグログを解析してトラブルシューティングする。**デバッグログの記録は既定で OFF** であり、`/debug` は「解析コマンド」であると同時に**記録を有効化するコマンド**でもある。

```
# 基本
/debug

# 問題の説明を添える
/debug MCP サーバーが接続できない
```

**使いどころ**:
- ClaudeCode 自体の動作に問題がある場合
- MCP サーバーの接続トラブル
- セッションの異常動作の原因調査

### `/loop [interval] [prompt]` — 定期実行

プロンプトまたはスキルを**指定した間隔で定期実行**する。interval を省略すると Claude が self-pace（自己ペース）で実行する。

```
# 5 分間隔でデプロイ状況を確認
/loop 5m デプロイ完了したか確認して

# 20 分間隔で PR レビューを実行
/loop 20m /review-pr 1234

# interval 省略で self-pace 監視
/loop テストスイートの実行結果を確認して
```

**使いどころ**:
- デプロイやビルドの完了待ち
- 定期的なステータス確認
- 長時間実行プロセスの監視

> **止め方（2026-10-11 追記）**: `Esc` で止まるのは、interval を省略した **self-paced loop が次の実行を待っている間**だけである（self-paced loop は Claude がタスク完了時に自分で終えることもある）。**固定間隔の loop は `Esc` では止まらず**、Claude に頼んで cancel する（`CronDelete`）か、作成から 7 日経って最終実行後に自動削除されるまで動き続ける。出典: [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

### `/claude-api` — Claude API リファレンス

[Claude API](https://platform.claude.com/docs/en/api/overview) と [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) のリファレンスを、プロジェクトの言語に合わせてロードする。コードが `anthropic` か `@anthropic-ai/sdk` を import している場合は**自動発火**する。

```
/claude-api
/claude-api prompt-audit
```

**サブコマンド**:

| サブコマンド | 内容 | 版 |
|---|---|---|
| `migrate` | 既存の Claude API コードを新しいモデルへ更新する | v2.1.221 より前から |
| **`upgrade`** | Anthropic SDK 依存のメジャーバージョン移行。現状は **Python `anthropic` 0.x → 1.x**。timeout は `httpx.Timeout` ではなく `anthropic.Timeout` を使う点などを含む | v2.1.236〜 |
| `managed-agents-onboard` | 新しい Managed Agent の作成を案内する | v2.1.221 より前から |
| **`managed-agents-onboard <url>`** / **`<quickstart-name>`** | URL のページが説明する Managed Agent、または Console の quickstart テンプレート（例 `deep-researcher`）を構築する。テンプレート名でない 1 語を渡すと有効な名前を一覧する | v2.1.290〜 |
| **`prompt-audit`** | プロンプト・skills・ツール説明から**旧世代モデル向けに書かれた指示**を洗い出し、修正案を diff で出す | v2.1.221〜 |
| **`cost-optimize`** | プロジェクトの API 支出の内訳をプロファイリングし、prompt caching・不要な入出力トークンの削減・batch・effort・モデル選択などの節約策を 1 つずつ提案する | v2.1.247〜 |
| **`build-eval`** | Claude を使うアプリの eval セットを作る | v2.1.259〜 |
| **`hillclimb`** | 既存の eval に対してアプリを反復改善する | v2.1.259〜 |
| **`preserved-thinking-migration`** | 以前のターン・system prompt・ツール一覧への編集で preserved thinking ブロックを無効化している箇所を探し、失われる推論量を測りながら 1 件ずつ修正案を出す | v2.1.282〜 |

> **2026-10-11 訂正**: 以前は `prompt-audit` について「公式 docs のコマンド一覧は未更新で、出典は CHANGELOG v2.1.221」と書いていたが、現行の commands ページと skills ページは上表の 8 種すべてを掲載している。版は公式 [Skills — Work on Claude API projects](https://code.claude.com/docs/en/skills#work-on-claude-api-projects) の表による。CLAUDE.md・skills 側の指示の監査は `/doctor prompt-audit`（v2.1.283+）が担う。

**使いどころ**:
- Claude API を使ったアプリケーション開発時
- Anthropic SDK の使い方を確認したい場合
- **旧モデル向けに書いたプロンプト資産を Opus 5 以降の世代（Opus 5.5 を含む）へ移す時**（`prompt-audit`）。Opus 5 では「検証を促す指示」「委任の推奨」が過剰動作を招くため、既存プロンプトの棚卸しに使える（[best-practices.md](best-practices.md) §8.5 参照）
- **自分のアプリの品質を eval で測って改善したい時**（`build-eval` → `hillclimb`）

### その他のバンドルスキル

| スキル | 用途 |
|--------|------|
| `/code-review [low\|medium\|high\|xhigh\|max\|ultra] [--fix] [--comment] [--max-findings n\|all\|default] [--post\|--no-post] [target]` | diff（または渡した PR 番号・ブランチ・パス）の correctness bug を検出する。**モデルと effort によっては再利用・簡素化・効率のクリーンアップも扱う**。`--fix` で修正適用、`--comment` で GitHub PR へのインラインコメント、または **GitLab MR への 1 件の note**（`glab` 経由、v2.1.257+）、`ultra` でクラウド多エージェントレビュー。**`--max-findings <n>` / `all` で指摘数の上限を変え、以後のレビューも同じ値を使う**（`default` で戻す。v2.1.288+）。**level を省略すると、前回自分で打った `low`〜`max` の level を（別セッションでも）再利用する**（v2.1.223+。一度も打っていなければ現在の effort。`-p` で渡した level は記憶されない。`ultra` は記憶の対象外）。**`ultra` かつ github.com の PR を対象にした場合、`--post` で「レビュー結果をユーザーの GitHub アカウントから 1 件のコメントとして PR に投稿する」選択肢が launch dialog に preselect される**（`--post` は v2.1.227+。`--no-post` でその選択肢を隠す。対話セッションでは dialog で確認、非対話では flag だけで投稿される）。**v2.1.218 以降は background subagent として実行**されるため、レビュー作業が会話コンテキストを埋めない（stacked slash commands もレビュー対象として保持される）。**v2.1.232 で `high` / `xhigh` / `max` も background 実行に統一**された（それまでは高 effort 時だけフォアグラウンド実行だった） |
| `/run` | プロジェクトのアプリを起動して変更を実機確認（テストだけに頼らない） |
| `/verify` | 変更がアプリ上で意図通り動くかをビルド・実行して検証 |
| `/deep-research <question>` | Web 横断調査 + 出典クロスチェック + 出典付きレポート（Workflow） |
| `/security-review` | ブランチ差分のセキュリティ脆弱性分析（injection・auth 等）。**種別は組み込みコマンド**（2026-08-12 訂正） |
| `/review [PR]` | **v2.1.223 以降は `/code-review` の alias**。effort レベルとフラグも `/code-review` と全く同じものを受け付ける。深いクラウドレビューは `/code-review ultra`。**v2.1.223 より前**は「1 パスの read-only レビュー」を行う独立コマンドだった（v2.1.186 で `/code-review medium` に統合 → v2.1.202 で単独 fast pass へ revert → **v2.1.223 で再び統合され alias に確定**という経緯） |
| `/fewer-permission-prompts` | transcript を走査し read-only Bash/MCP の allowlist を提案 |
| `/reload-skills` | スキル/コマンドディレクトリを再スキャン（再起動不要、v2.1.152〜）。**種別は組み込みコマンド**（2026-08-12 訂正）。**v2.1.216 以降、セッション中に変更した skills / commands は再起動なしでスラッシュメニューに反映される** |
| `/update-config [request]` | 設定変更（コマンドの許可・環境変数の設定・hook の追加など）を自然言語で頼むと、該当する `settings.json` を Claude が編集する。テーマやモデルのような項目は `/config` を使う |
| `/run-skill-generator` | `/run` と `/verify` に、クリーンな環境からプロジェクトのアプリをビルド・起動・操作する手順を教える project 用 skill を書く |
| `/claude-in-chrome [task]` | Claude in Chrome 経由で、ブラウザ上のタスク（ページのテスト・フォーム入力・console log の読み取りなど）を実行する。`claude --chrome` などで Chrome 連携が有効なセッションか、拡張のインストールを提案できる場合に使える |
| `/slides [brief]` | brief から Claude Slides の artifact としてプレゼンを作る（例 `/slides a quarterly review of the platform team`）。v2.1.265+・artifacts が使えるセッション・Slides テンプレートが有効なアカウントが必要で、満たさないとコマンド自体が出ない。Anthropic API のみ |
| `/artifact-capabilities` | 公開 artifact が使える実行時機能（connector 呼び出し・ファイルダウンロードなど）と、自分のアカウントで使えるものをまとめたリファレンスをロードする。通常は Claude がそうしたページを作る前に自動でロードする。artifacts が使える環境のみ |
| `/artifact-diagramming` | artifact 内で図を描くためのガイド（図が役立つ場面・描く内容・light / dark 両テーマで読める inline SVG の書き方）をロードする。v2.1.221+ |

> **⚠️ 検証系スキルの自発起動の変遷（v2.1.215 / v2.1.218）**: 従来は Claude が必要と判断して自動的に走らせることがあったが、**`/verify` と `/deep-research` は現在も明示的に呼び出さないと動かない**。`/code-review` は一度止まったが、現行公式では Claude が自ら起動できる。
>
> | スキル | 変更 |
> |---|---|
> | `/verify` | **v2.1.215**: Claude が自発的に起動しなくなった（現行の commands ページも「invoke したときだけ実行」と明記） |
> | `/code-review` | **v2.1.215** で自発起動が止まったが、**現行公式 [Code Review](https://code.claude.com/docs/en/code-review) は「Claude can start `/code-review` on its own」とし、`/code-review` を prompt にした scheduled task でも走る**と記載する。v2.1.246 で Bedrock / Vertex AI / Foundry・Claude apps gateway・telemetry 無効時にも広がった（下記「v2.1.234〜v2.1.258」表）。第一者接続で再開した版は CHANGELOG に明記が無い。自発起動を止めたい場合は `skillOverrides` に `"code-review": "user-invocable-only"` を書く |
> | `/deep-research` | **v2.1.218**: ユーザーが呼び出した時のみ実行。それ以前は Claude 自身も起動できた |
>
> **2026-10-11 訂正**: 以前は `/verify` と `/code-review` を同じ行にまとめ、どちらも現在は明示起動のみと書いていたが、同じ文書の v2.1.246 の行と矛盾していた。
>
> **ハーネス設計上の意味**: 検証を確実に走らせたいなら、**自分でチェーン（スキルの完了時に次のスキルを呼ぶ）か埋め込み（生成スキル内に検証を組み込む）を構成する必要がある**。Opus 5 は自己検証を自発的に行うため「プロンプトで verify を指示する」必要性は下がったが、**ハーネス側の明示ステップはむしろ自分で組む必要が上がった**という二方向の変化になっている。verification loop の 4 つの配置モデルは `docs/harness.md` を参照。出典: CHANGELOG v2.1.215 / v2.1.218

---

## 実践的なワークフロー

### ワークフロー 1: 探索 → 計画 → 実装 → レビュー

```
1. Plan Mode で探索・計画   ← /plan（Shift+Tab で切り替え）
2. 実装                     ← Normal Mode に戻して実装
3. /code-review             ← バグ検出（先に実行し、正しさを担保）
4. /simplify                ← クリーンアップ（後に実行。再利用・簡素化・効率・抽象度）
5. /clear                   ← 次のタスクに向けてリセット
```

### ワークフロー 2: コンテキスト管理の日常運用

```
1. /context                 ← 使用量を確認
2. 使用量が 60% を超えたら  ← /compact で圧縮
3. タスクが完全に切り替わる  ← /clear でリセット
4. 失敗アプローチが蓄積     ← /clear + より具体的なプロンプトで再開
```

### ワークフロー 3: 大規模変更の安全な実行

```
1. Plan Mode で影響範囲を調査
2. /batch <指示>            ← 並列で自動実行
3. 最初の 2〜3 ファイルを確認
4. /code-review             ← バグ検出（先に実行）
5. /simplify                ← クリーンアップ（後に実行）
```

### ワークフロー 4: デプロイ監視

```
1. デプロイを実行
2. /loop 5m デプロイの状況を確認して    ← 固定間隔の loop（作成から 7 日で自動失効）
3. 完了を確認したら「デプロイ確認の loop を止めて」と Claude に頼んで cancel する
   （Esc で止まるのは interval を省略した self-paced loop の待機中だけ）
```

> **2026-10-11 訂正**: 以前は手順 3 を「完了を確認したら会話を中断（Esc）」と書いていたが、固定間隔の loop は `Esc` では止まらない（`/loop` 節の「止め方」参照）。

---

## コマンド対応表（まとめ）

| コマンド | 種別 | カテゴリ | 用途 |
|---------|------|---------|------|
| `/clear` | 組み込み | コンテキスト管理 | コンテキストの完全リセット |
| `/compact [指示]` | 組み込み | コンテキスト管理 | コンテキストの手動圧縮 |
| `/context` | 組み込み | コンテキスト管理 | コンテキスト使用量の確認 |
| `/rewind` | 組み込み | セッション管理 | チェックポイントへの巻き戻し |
| `/rename [name]` | 組み込み | セッション管理 | セッション名の変更 |
| `/memory` | 組み込み | 環境確認 | メモリファイルの確認 |
| `/agents` | 組み込み | 環境確認 | サブエージェント管理のリマインダ表示（v2.1.198 でウィザード廃止） |
| `/hooks` | 組み込み | 環境確認 | 設定済み Hooks の閲覧（read-only） |
| `/mcp [reconnect (<server>\|all)\|enable\|disable [<server>\|all]]` | 組み込み | 環境確認 | MCP サーバーの接続と OAuth 認証の管理。**サブコマンドで再接続・有効化・無効化ができ、`reconnect all` で失敗・要認証のサーバーを一括再試行する** |
| `/skills` | 組み込み | 環境確認 | Skills 一覧 |
| `/permissions` | 組み込み | 環境確認 | パーミッション設定 |
| `/doctor [prompt-audit [path]]`（alias `/checkup`） | **バンドルスキル** | 環境確認 | 環境診断 + 自動修復（v2.1.205 で built-in からスキル化）。`prompt-audit` で指示ファイルの監査（v2.1.283+）。`disableBundledSkills` の唯一の例外 |
| `/skill-doctor` | 組み込み | 環境確認 | skill ごとのコンテキストコストと使用頻度（v2.1.252+） |
| `/insights` | 組み込み | 環境確認 | ローカルのセッション分析レポート（cloud セッションでは不可） |
| `/init` | 組み込み | 初期設定 | CLAUDE.md の自動生成 |
| `/sandbox` | 組み込み | 初期設定 | サンドボックスモード |
| `/plugin` | 組み込み | Plugin 管理 | Plugin の管理 UI |
| `/reload-plugins` | 組み込み | Plugin 管理 | Plugin のリロード |
| `/plugin-authoring` | 組み込み plugin の skill | Plugin 管理 | mod 作成リファレンスのロード（v2.1.287+） |
| `/fast` | 組み込み | その他 | Fast モードのトグル |
| `/help` | 組み込み | その他 | ヘルプ表示 |
| `/login` | 組み込み | その他 | 認証ログイン |
| `/logout` | 組み込み | その他 | 認証ログアウト |
| `/simplify [target]` | バンドルスキル | コード品質 | 4 並列サブエージェントでクリーンアップ（バグ検出はしない。v2.1.154〜） |
| `/batch <instruction>` | バンドルスキル | 大規模変更 | 大規模変更の並列処理（計画を提示し、承認後に起動） |
| `/debug [description]` | バンドルスキル | デバッグ | セッションデバッグログの解析 |
| `/loop [interval] [prompt]` | バンドルスキル | 定期実行 | プロンプトの定期実行（**プロンプト省略時は組み込みの maintenance prompt、または `loop.md` を使う**） |
| `/claude-api [subcommand]` | バンドルスキル | リファレンス | Claude API / Managed Agents リファレンスのロード（サブコマンド 8 種） |
| `/btw <question>` | 組み込み | コンテキスト管理 | コンテキストを汚さないサイドバー質問 |
| `/resume [session]` | 組み込み | セッション管理 | 会話を ID/名前/ピッカーで再開（alias `/continue`） |
| `/branch [name]` | 組み込み | セッション管理 | 会話を分岐（複製へ自分が移る） |
| `/fork [prompt]` | 組み込み | セッション管理 | 会話を新しい background セッションへ複製（v2.1.212 で再定義。**v2.1.221 から複製に独自の worktree を作るよう指示する**。edits in place などの例外あり） |
| `/subtask <instruction>` | 組み込み | セッション管理 | 脇タスクを会話内 subagent に渡し結果を戻す（v2.1.212。旧 `/fork`） |
| `/add-dir <path>` | 組み込み | セッション管理 | 作業ディレクトリを追加（移動はしない） |
| `/recap` | 組み込み | セッション管理 | セッションの 1 行要約 |
| `/plan [description]` | 組み込み | セッション管理 | プロンプトから plan mode 起動 |
| `/model [model]` | 組み込み | モデル・推論制御 | モデル切替（既定として保存） |
| `/effort [level\|auto\|status\|ultracode [on\|off]]` | 組み込み | モデル・推論制御 | effort 設定（`auto` で保存値クリア、`status` で解決結果表示。session-only は `max` のみ。ultracode は v2.1.284 以降 effort から独立したトグル） |
| `/goal [condition\|clear]` | 組み込み | モデル・推論制御 | 完了条件達成までターンを跨いで継続（`clear` で解除） |
| `/config` | 組み込み | 環境確認 | 設定 UI（alias `/settings`） |
| `/status` | 組み込み | 環境確認 | 設定 Status タブ（バージョン・接続状況・**セッション種別**、応答中も実行可） |
| `/usage` | 組み込み | 環境確認 | コスト・使用量・内訳（alias `/cost`,`/stats`） |
| `/usage-credits` | 組み込み | 環境確認 | usage credits の設定 / 管理者への申請（旧名 `/extra-usage`） |
| `/upgrade` | 組み込み | 環境確認 | プランのアップグレード（Enterprise では非表示） |
| `/copy [N]` | 組み込み | その他 | 直近（または N 番目）の応答をクリップボードへ |
| `/export [filename]` | 組み込み | その他 | 会話をプレーンテキストで出力 |
| `/desktop` | 組み込み | その他 | 現セッションを Desktop アプリで継続（alias `/app`） |
| `/mobile` | 組み込み | その他 | モバイルアプリ DL の QR 表示（alias `/ios`,`/android`） |
| `/chrome` | 組み込み | その他 | Claude in Chrome の設定 |
| `/statusline` | 組み込み | 環境確認 | ステータスライン設定 |
| `/keybindings` | 組み込み | 環境確認 | キーバインド設定ファイル |
| `/diff` | 組み込み | 環境確認 | 差分ビューア（fullscreen では live panel。実体は組み込み mod `cc-plugin-diff`） |
| `/theme` | 組み込み | UI・表示 | カラーテーマ変更 |
| `/focus` | 組み込み | UI・表示 | フォーカスビュー切替（fullscreen 専用） |
| `/tui [default\|fullscreen]` | 組み込み | UI・表示 | TUI レンダラ切替 |
| `/color [color\|default]` | 組み込み | UI・表示 | プロンプトバーの色を設定 |
| `/output-style [style]` | 組み込み | UI・表示 | output style の一覧・切替（v2.1.269+） |
| `/background [prompt]` | 組み込み | 並列・バックグラウンド | セッションをバックグラウンド化 |
| `/stop` | 組み込み | 並列・バックグラウンド | アタッチ中の background セッションを停止 |
| `/tasks` | 組み込み | 並列・バックグラウンド | バックグラウンドタスク一覧（alias `/bashes`） |
| `/workflows` | 組み込み | 並列・バックグラウンド | ワークフロー進捗ビュー |
| ~~`/ultraplan <prompt>`~~ | — | — | **v2.1.222 で削除**。plan mode か Claude Code on the web を使う |
| `/ultrareview [PR]` | 組み込み | クラウド連携 | クラウド多エージェントレビュー |
| `/schedule [description]` | 組み込み | クラウド連携 | routines（クラウド定期実行）の管理 |
| `/teleport` | 組み込み | クラウド連携 | web セッションをターミナルに引き込む（alias `/tp`） |
| `/remote-control` | 組み込み | クラウド連携 | claude.ai からのリモート操作に開放（alias `/rc`） |
| `/autofix-pr [prompt]` | 組み込み | クラウド連携 | PR を監視しクラウドで自動修正 push |
| `/design-sync [name]` | バンドルスキル | クラウド連携 | リポの React デザインシステムを Claude Design へ同期 |
| `/design-login` | 組み込み | クラウド連携 | `/design-sync` 用のデザインシステムアクセス認可 |
| `/web-setup` | 組み込み | クラウド連携 | gh CLI 認証で GitHub を web に接続 |
| `/remote-env` | 組み込み | クラウド連携 | `--remote` web セッションの既定環境設定 |
| `/code-review [...]` | バンドルスキル | コード品質 | diff のバグ検出（モデル・effort によりクリーンアップも。`ultra` でクラウド、`--max-findings` で指摘数を変更） |
| `/run` | バンドルスキル | 検証 | アプリを起動して変更を実機確認 |
| `/verify` | バンドルスキル | 検証 | 変更がアプリ上で動くか検証 |
| `/deep-research <question>` | **Workflow** | 調査 | Web 横断調査 + 出典付きレポート |
| `/security-review` | **組み込み** | セキュリティ | ブランチ差分の脆弱性分析 |
| `/review [PR]` | バンドルスキル | レビュー | **`/code-review` の alias**（v2.1.223〜） |
| `/fewer-permission-prompts` | バンドルスキル | パーミッション | read-only allowlist の自動提案 |
| `/reload-skills` | **組み込み** | 環境確認 | スキル/コマンドの再スキャン |
| `/update-config [request]` | バンドルスキル | 設定 | 自然言語の依頼で `settings.json` を編集 |
| `/run-skill-generator` | バンドルスキル | 検証 | `/run` `/verify` 用の project skill を生成 |
| `/claude-in-chrome [task]` | バンドルスキル | ブラウザ | Claude in Chrome でブラウザ上のタスクを実行 |
| `/slides [brief]` | バンドルスキル | Artifacts | Claude Slides の artifact を作成（v2.1.265+） |
| `/artifact-capabilities` | バンドルスキル | Artifacts | artifact の実行時機能リファレンスのロード |
| `/artifact-diagramming` | バンドルスキル | Artifacts | artifact 内の図解ガイドのロード（v2.1.221+） |

> **種別の訂正（2026-08-12）**: 公式 [Built-in commands](https://code.claude.com/docs/en/commands) と照合し、4 件の分類を修正した。`/doctor` は組み込み → **バンドルスキル**、`/deep-research` はバンドルスキル → **Workflow**、`/security-review` と `/reload-skills` はバンドルスキル → **組み込み**である。

---

## v2.1.234〜v2.1.258 のコマンド・表示の変更

| コマンド | 変更 | 版 |
|---|---|---|
| `/usage` | **Loops breakdown**（`/loop` など scheduled task ごとの実行回数・総トークン・run あたりトークン・最終実行）を追加。Pro / Max / Team / Enterprise のプラン内訳に出る（W35 ダイジェストで告知） | v2.1.243（CHANGELOG）。docs（Manage costs）の要件記載は v2.1.242 |
| `/usage` | **Spend limit バー**を追加（statusline の `rate_limits.spend_limit` フィールドと対） | v2.1.251 |
| `/cost` | **per-session の prompt-cache 行** `Prompt cache (main)` を追加（hit ratio / misses / re-cached tokens / warm・cold）。statusline スクリプト向けに同じ値の **`prompt_cache` オブジェクト**も追加（W36 ダイジェストで告知） | v2.1.251 |
| `/status` | `Skipped sources` 行（高優先の managed source により未適用の managed settings を列挙）/ GitHub 接続状態行 | v2.1.243 |
| `/status` | server-managed settings のロード失敗を説明する行 | v2.1.248 |
| `/doctor` | server-managed settings の診断を追加 | v2.1.248 |
| `/doctor` | **kill されたセッションが残した stale sandbox mask file の警告** | v2.1.257 |
| `/tasks`・agent detail | 各 subagent が動いた**モデルと effort level** を表示 | v2.1.243 |
| `/goal` | background task 待ちが **30 分でチェックイン**し、以降アイドル時は間隔を延ばしつつ継続。`CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0` でオプトアウト | v2.1.234〜239 |
| `/btw` | 履歴ブラウズが `←`/`→` → **`Shift+←`/`Shift+→`（または `[`/`]`）** へ変更 | v2.1.257 |
| `/loop` | self-paced dynamic mode と no-prompt autonomous default が **Bedrock / Vertex / Foundry を含め常時利用可**に | v2.1.248 |
| `/code-review` | Bedrock / Vertex / Foundry・gateway 経由・telemetry 無効時でも **Claude の自発起動が可能**に | v2.1.246 |
| `/permissions` | **auto mode classifier ルールを閲覧・編集する Auto mode タブ**を追加 | v2.1.246 |
| `/permissions` | Claude が作業中でも開けるようになり、`/add-dir <path>` も実行可。**権限ルールの変更は現在のターンの残りに即適用**される | v2.1.234〜239 |
| `/login` | **Anthropic Console のキーレスサインイン**「Sign in with your Console account」を追加（API キー禁止組織向け・推奨） | v2.1.243 |
| `/usage-credits` | AWS Marketplace 課金 Enterprise / self-serve Enterprise / Enterprise トライアルでも利用可（管理者への上限引き上げ依頼） | v2.1.248 |
| `/radio` | Bedrock / Vertex AI / Foundry / Claude Platform on AWS、telemetry 無効時にも提供 | v2.1.251 |
| `/mcp`・`/plugins` | 組織が認証を管理する claude.ai connector に **`managed` マーカー**を表示 | v2.1.243 |
| `/config` | **「Continue automatically at usage limit」行**を追加（既定 ON） | Week 34 |
| `/config` | **Time format 行**（`timeFormat` 設定と対） | v2.1.257 |

### 組み込み "Concise" output style（v2.1.237〜）

新しい組み込み output style で、**結果を先に述べ、前置きと実況ナレーションを省く**。ただし**作業の徹底度は Default と同等**で、説明を求めれば完全に答える。**エラー報告・セキュリティ警告・破壊的操作の確認は完全な内容を維持する**。

`/output-style concise`（v2.1.269+）を実行するか、`/config` の Output style から選ぶか、`settings.json` に `{"outputStyle": "Concise"}` を書く（設定値は大文字小文字を区別する。`/output-style` は区別しない）。**v2.1.251 以降、セッション途中で切り替えると次のメッセージから新しい style が効く**。v2.1.251 より前は `/clear` か新セッションが必要だった。**2026-10-11 訂正**: 以前は「適用には `/clear` か新セッションが必要」と書いていたが、これは v2.1.251 未満の挙動である。

組み込み style には **Proactive** もある。ルーチンの判断で止まって質問せず妥当な仮定で作業を進め、頼まれない限り plan mode に入らない。データを消す操作や共有・本番システムを変える操作の前には会話で確認するよう指示されているが、これは permission prompt とは別物で、permission mode も変えない。

出典: [Output styles — Built-in output styles](https://code.claude.com/docs/en/output-styles#built-in-output-styles) / CHANGELOG v2.1.234〜v2.1.258 / CHANGELOG v2.1.269

---

## v2.1.259〜v2.1.296 のコマンド・表示の変更

2026-10-11 追記。版は commands・skills・interactive-mode などの公式 docs の要件記載による。CHANGELOG を根拠にした行は版の欄に明記する。

| コマンド | 変更 | 版 |
|---|---|---|
| `/claude-api` | `build-eval` / `hillclimb` サブコマンドを追加 | v2.1.259 |
| `/diff` | fullscreen rendering で会話の横に **live diff panel** を開くようになった（「環境確認・診断」節の注記） | v2.1.260（CHANGELOG・W36）。現行 docs の panel 要件は v2.1.287+ |
| `/cost`（`/usage`） | `Prompt cache (main)` 行に直近 miss の推定原因を表示。statusline の `prompt_cache` にも `last_miss_cause` / `miss_causes` を追加 | v2.1.260 |
| 入力途中の `/` | 一致するコマンドを候補一覧から選べるようになった。plugin skill は prefix なしの名前でも一致する（冒頭の注記） | v2.1.265（CHANGELOG・W37） |
| `/design` / `/slides` | artifacts の Design / Slides テンプレートに基づく現行要件 | v2.1.265 |
| `/import` | Cursor からの取り込みに対応 | v2.1.265 |
| `/output-style [style]` | output style の一覧・切替コマンドを追加 | v2.1.269 |
| `/batch` | git リポジトリ外でも `WorktreeCreate` hook があれば実行できる | v2.1.281 |
| `/focus` | Remote Control から `/focus [on\|off]` で当該セッションだけ切り替えられる | v2.1.281 |
| `/claude-api` | `preserved-thinking-migration` サブコマンドを追加 | v2.1.282 |
| `/doctor` | `prompt-audit [path]` サブコマンドを追加 | v2.1.283 |
| `/effort` | ultracode を effort から独立したトグルに変更（`ultracode on` / `off`） | v2.1.284 |
| `/plugin-authoring` | mod 作成リファレンスをロードする組み込み plugin の skill | v2.1.287 |
| `/code-review` | `--max-findings n\|all\|default` を追加 | v2.1.288 |
| `/claude-api` | `managed-agents-onboard <url>` / `<quickstart-name>` を追加 | v2.1.290 |

出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Skills](https://code.claude.com/docs/en/skills) / [Interactive mode](https://code.claude.com/docs/en/interactive-mode) / [Manage costs](https://code.claude.com/docs/en/costs) / [Status line](https://code.claude.com/docs/en/statusline) / [Code Review](https://code.claude.com/docs/en/code-review) / [Model configuration](https://code.claude.com/docs/en/model-config) / CHANGELOG v2.1.259〜v2.1.296


## 関連ドキュメント

- [Built-in commands](https://code.claude.com/docs/en/commands) — 公式コマンドドキュメント
- [Best Practices](https://code.claude.com/docs/en/best-practices) — 公式ベストプラクティス
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) — `/loop` を含む定期実行タスク
- [Claude directory](https://code.claude.com/docs/en/claude-directory) — CLAUDE.md・settings.json・hooks・skills・workflows・auto memory などを置く `.claude` ディレクトリの解説
- [Interactive mode](https://code.claude.com/docs/en/interactive-mode) — 入力途中の `/` 補完と `/diff` の panel / ダイアログ
- [ClaudeCode Skills ガイド](skills.md) — Skills の詳細（バンドルスキルの仕組み）
- [Mods](mods.md) — `/diff` を実装する組み込み mod と、mod（関数 hook を持つ plugin）の仕組み
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
