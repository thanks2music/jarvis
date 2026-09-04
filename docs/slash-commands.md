# ClaudeCode スラッシュコマンドガイド

> 出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) / [Routines](https://code.claude.com/docs/en/routines) / [Fast mode](https://code.claude.com/docs/en/fast-mode) / [Agent view](https://code.claude.com/docs/en/agent-view) / [Workflows](https://code.claude.com/docs/en/workflows) / [Claude directory](https://code.claude.com/docs/en/claude-directory) / [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) / [whats-new week 32](https://code.claude.com/docs/en/whats-new/2026-w32) / [Output styles](https://code.claude.com/docs/en/output-styles) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-09-03時点。CHANGELOG は v2.1.258 まで反映)

> **公式説明が確認できず未収録のコマンド**（憶測での記載を避けている。2026-08-16 再確認）:
>
> | コマンド | 状況 |
> |---|---|
> | `/workshop` | 公式 commands ページ全文（185,618 bytes）・docs インデックス（`llms.txt`）・**CHANGELOG 全 5,534 行**を検索して **0 ヒット**。公式に存在の痕跡が見つからない |
> | `/tui` | ✅ **2026-09-03: 公式 commands ページに掲載された**（旧記述の「公式未掲載」は解消済み）。**導入は v2.1.110**（「Added `/tui` command and `tui` setting — run `/tui fullscreen` to switch to flicker-free rendering in the same conversation」）。v2.1.227 / v2.1.228 / v2.1.232 にも修正エントリがあり現役だが、**公式 commands ページには依然未掲載**で CHANGELOG のみが一次情報 |
> | `/usage-credits`（旧 `/extra-usage`） | ✅ **2026-09-03: 公式 commands ページに「Previously `/extra-usage`」の併記付きで掲載された**（旧記述の「依然未掲載」は解消済み） |
> | `claude rc` | cli-reference にサブコマンドとして存在しない。`--rc` は `--remote-control` の**フラグ**短縮形で、サブコマンド形は `claude remote-control` |

ClaudeCode のスラッシュコマンドは、セッション中に `/` に続けてコマンド名を入力することで実行できる。**組み込みコマンド（Built-in Commands）**と**バンドルスキル（Bundled Skills）**の 2 種類がある。`/` を入力すると利用可能なコマンドが一覧表示され、文字を続けて入力するとフィルタリングできる。

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

コンテキストウィンドウを**完全にリセット**する。無関係なタスク間の切り替え時に使う。**引数に名前を渡すと、リセット後の新しいセッションにその名前が付く**。

```
# タスク A 完了後、別のタスク B に取り掛かる前に
/clear

# 名前を付けてリセット
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

以前のチェックポイントに巻き戻す。会話のみ・コードのみ・両方の復元が可能。`Esc + Esc` でも起動できる。

```
/rewind
```

**選択肢**:
- 会話のみ復元（コードはそのまま）
- コードのみ復元（会話はそのまま）
- 両方復元
- 選択したメッセージからの要約

**使いどころ**:
- リスクのある実装を試して失敗した場合の復元
- Claude の回答が意図と異なった場合のやり直し
- 特定地点からの部分圧縮（`Esc + Esc` → `/rewind` → 「ここから要約」）

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
| `/recap` | セッションの 1 行要約をオンデマンド生成 |
| `/plan [description]` | プロンプトから直接 plan mode に入る（任意のタスクを即指定可） |

> **⚠️ `/fork` はバージョンで意味が変わる（重要）**: 公式が明記するバージョン別挙動は以下の通りで、**v2.1.212 で役割が入れ替わっている**。本ドキュメントの旧版は v2.1.161〜211 の挙動（forked subagent）を記載していた。
>
> | バージョン | `/fork` の挙動 |
> |---|---|
> | 〜 v2.1.160 | `/branch` の alias（forked subagent が有効化されている場合を除く） |
> | v2.1.161 〜 v2.1.211 | **forked subagent** を spawn し、結果が会話へ戻る（現在の `/subtask` に相当） |
> | **v2.1.212 〜 v2.1.220** | **会話を新しい background セッションへ複製**（元セッションの checkout 内で作業する）。脇タスクを subagent に渡すのは `/subtask`、複製へ自分が移るのは `/branch` |
> | **v2.1.221 〜** | 上記に加えて、**複製先セッションが独自の worktree を作成する**（元セッションの checkout を共有しない） |
>
> **v2.1.221 の worktree 化の意味**: 「Changed sessions forked with `/fork` to create a new worktree of their own instead of working in the original session's checkout」。fork 先が別の作業ツリーを持つため、**元セッションと fork 先が同じファイルを同時に触って壊す事故が構造的に起きなくなった**。一方で「fork したのに変更が元の checkout に見えない」挙動になるため、**fork 先の成果物は worktree 側にある**点を意識する必要がある（ディスク上の対応は [session-history.md](session-history.md) 参照）。
>
> 出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Agent view](https://code.claude.com/docs/en/agent-view#from-inside-a-session) / CHANGELOG v2.1.221

---

### モデル・推論制御

モデル選択と思考量（effort）を制御するコマンド群。

| コマンド | 用途 |
|---------|------|
| **`/artifacts`** | Artifacts の管理（v2.1.208〜） |
| **`/workflow-authoring`** | workflow スクリプト作成のリファレンスをロード（v2.1.248〜。**保存済み workflow の `.js` を編集する前に実行することが公式推奨**） |
| **`/design [brief]`** | Claude Design の artboard ワークフローを CLI / Desktop に持ち込む（research preview、要 v2.1.234+） |
| **`/auto-mode-setup`** | auto mode のセットアップウィザード（v2.1.228〜） |
| **`/rate-limit-options`** | レート制限に達した際の選択肢を表示する |
| `/model [model]` | モデル切替。新セッションの既定として保存（`s` で当該セッションのみ。左右キーで effort 調整）。エイリアス: `opus` / `sonnet` / `haiku` のほか、Fable 用に **`fable`（v2.1.255 以降は Fable 5.1 に解決。それ以前は Fable 5）**・**`best`（利用可能な最新の Fable、無ければ `opus` と同じモデル）**。⚠️ **Fable はどのプラン・プロバイダでもアカウント種別の既定モデルではない**。Claude apps gateway 経由では当面 Fable 5 に解決され続けるが追加（要 v2.1.170+）。**v2.1.219 以降 `opus` は全プロバイダで Opus 5 に解決**され、merged Opus 行は「Opus (1M context)」と表示される（**Opus 5 の利用には v2.1.219 以上が必須**）。`default` の解決先はアカウント種別で分岐（`docs/model-comparison.md` §2.1） |
| `/effort [level\|auto\|status]` | effort 設定。`low`/`medium`/`high`/`xhigh`/`max`/`ultracode`（`max`・`ultracode` は session-only、`auto` で当該モデルの保存値をクリア、**`status` で現在の解決結果を表示**）。**画面内で `s` キーを押すとそのセッション限りの変更になる**（v2.1.257〜、`/model` と同挙動）。**Opus 5 / Fable 5 / Opus 4.8 / Sonnet 5 のデフォルトは `high`、Opus 4.7 のみ `xhigh`**。⚠️ **2026-09-03 訂正: effort は v2.1.251 以降モデルごとに保存される**（`modelSettings.<model>.effortLevel`）。**モデルを切り替えても旧モデルの値は引き継がれない**。model-default hold を持たないのは **Opus 5 と Fable 5.1**（hold を持つのは Fable 5 / Opus 4.8 / Opus 4.7）で、hold の有無と「引き継ぐか」は別問題である。詳細は [best-practices.md](best-practices.md) §8。Opus 5 では公式が「`high` 起点 + `low`/`medium` を主制御」を推奨する |
| `/goal [condition\|clear]` | 完了条件を設定し、達成までターンを跨いで継続する **first-class システム**。裏で別の evaluator を spawn し、毎ターン後に完了条件を再チェックする(`docs/best-practices.md` からも参照される key workflow tool)。`clear`/`stop`/`off` 等で解除 |
| `/advisor [model\|off]` | 第 2 モデル相談ツール（advisor tool）の有効化/無効化。タスク中の要所で別モデルに助言を求める。`opus`/`sonnet`/フル model ID を指定、引数なしでピッカー（v2.1.98〜）。設定は `advisorModel`。**v2.1.232 で Fable 5 が再び受理されるようになった**（2026-08-16 更新。従来「`/advisor fable` は拒否される」と記載していたが、現在は **Fable へのアクセスを持つ組織であれば選択可能**。`/model fable` と同様に usage credits の同意が必要） |

> `/fast`（fast mode のトグル）は「その他」節に詳細がある。**v2.1.219 で対象モデルが変わった**ため併せて参照する。

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

#### `/hooks` — Hooks の設定

Hooks の対話的設定 UI を開く。既存の Hooks の確認・新規作成が可能。

```
/hooks
```

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

パーミッションの allowlist / denylist を管理する。安全なコマンドを事前に許可しておくと、承認確認の回数を減らせる。

```
/permissions
```

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

```
/doctor
/checkup
```

> **`/doctor` は組み込みコマンドではなく[Skill]である**（v2.1.205 で built-in からバンドルスキルへ移された）。`disableBundledSkills` で全バンドルスキルを無効化した場合も、**`/doctor` だけは例外的に残る**（[skills.md](skills.md) 参照）。
>
> シェルから `claude doctor` として実行することもできる。こちらは**読み取り専用**で、自動修復は行わない。

出典: [whats-new week 28](https://code.claude.com/docs/en/whats-new/2026-w28) / [Built-in commands](https://code.claude.com/docs/en/commands)

#### その他の環境確認・診断コマンド

| コマンド | 用途 |
|---------|------|
| `/config`（alias `/settings`） | 設定 UI（テーマ・モデル・出力スタイル・エディタモード等）。**v2.1.181/183 で `/config key=value` シンタックス追加**: 任意設定をプロンプトから直接変更可能(`-p` モード・Remote Control でも動作)、`/config --help` で shorthand キー一覧。⚠️ **`key=value` シンタックスは CLI 前提であり、Claude Desktop の `/config` は `key=value` を無視する**（[claude-desktop.md](claude-desktop.md) 参照） |
| `/status` | 設定 Status タブ（バージョン・モデル・アカウント・接続状況）。**応答中でも割り込まずに即時実行される**。**v2.1.221 以降はセッション種別も表示**（`interactive` / background の `attached` / `unattended`） |
| `/usage`（alias `/cost`, `/stats`） | コスト・プラン使用量・スキル/subagent 別の内訳。**v2.1.221 で Stats パネルが cache トークンを合計に含める**ようになり、input / output / cache read / cache write の内訳が表示される |
| **`/usage-credits`** | limit 到達時に usage credits を設定する、または管理者に申請する。ブラウザで [usage-credits の billing 設定](https://code.claude.com/docs/en/costs#add-usage-credits-to-your-subscription)を開く。**Team / Enterprise で billing 権限のないメンバーは、CLI から管理者へ申請を送る**（v2.1.211 以降は「管理者に通知される」旨の確認ダイアログあり）。SSH 等でブラウザを開けない場合は URL を出力する（要 v2.1.205+）。**旧名 `/extra-usage`**。環境変数 `DISABLE_EXTRA_USAGE_COMMAND` で無効化できる |
| **`/upgrade`** | プランのアップグレード（Enterprise プランでは非表示） |
| **`/copy [N]`** | 直近のアシスタント応答をクリップボードへコピー。`N` を渡すと N 番目に新しい応答をコピーする（`/copy 2` で最後から 2 番目）。引数なしでピッカーが開き、**`w` で対象の切替**ができる |
| **`/export [filename]`** | 会話をプレーンテキストで出力。ファイル名を渡すと直接書き出し、省略するとクリップボード / ファイル保存を選ぶダイアログを開く |
| **`/desktop`**（alias `/app`） | 現在のセッションを Claude Code Desktop アプリで継続する。macOS または x64 Windows と Claude サブスクリプションが必要 |
| **`/mobile`**（alias `/ios`, `/android`） | モバイルアプリをダウンロードするための QR コードを表示 |
| **`/chrome`** | Claude in Chrome の設定 |
| `/statusline` | ステータスライン設定（自然言語指定 or shell プロンプトから自動構成） |
| `/keybindings` | キーバインド設定ファイルの作成・編集 |
| `/diff` | 未コミット差分とターン別差分のインタラクティブビューア |

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

---

### その他

#### Artifacts (v2.1.198〜、Team / Enterprise beta)

セッション出力を **claude.ai 上のプライベート live URL として公開** する新機能。編集中もその URL がリアルタイム更新される。ダッシュボード・レポート・データ可視化を Claude Code 内から共有したいときに使う。

- **対応**: Team / Enterprise の Anthropic API 認証のみ。**Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry 非対応**、**ZDR / HIPAA / CMEK 非対応**
- **ショートカット**: `Ctrl+]` で最新 artifact を再度開く
- **無効化**: 設定 `disableArtifact` / 環境変数 `CLAUDE_CODE_DISABLE_ARTIFACT=1` / `Artifact` の deny rule
- **管理 admin 用**: managed setting `enableArtifact`(v2.1.196)
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
| 〜 v2.1.153 | Opus 4.6 | Opus 4.6 / 4.7 |
| v2.1.154 〜 v2.1.218 | **Opus 4.8** | Opus 4.7 / 4.8（**Opus 4.6 は deprecated**） |
| **v2.1.219 〜** | **Opus 5** | **Opus 5 / Opus 4.8**（**Opus 4.7 を削除**） |

- 料金は **$10 / $50 per MTok**（標準の約 2 倍レート・約 2.5 倍速）で、1M context の全域にフラット適用される。
- **Opus 5 の fast mode は Claude API のみ**（Bedrock / Google Cloud / Microsoft Foundry では利用不可、research preview）。
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
| `/focus` | フォーカスビュー切替（旧 `Ctrl+O`。直近プロンプト + 要約のみ表示） |
| `/tui [default\|fullscreen]` | TUI レンダラ切替。`fullscreen` でちらつきのない alt-screen レンダラ |

> **廃止済みコマンド**: `/vim`（v2.1.92 廃止 → `/config` の Editor mode へ）、`/pr-comments`（v2.1.91 廃止 → Claude に直接 PR コメント参照を依頼）。
>
> **v2.1.205 で non-interactive mode 対応**: `/color` / `/effort` / `/fast` / `/mcp` / `/rename` に加え、**`/model` / `/config key=value` / `/import`** も `-p` フラグでの非対話実行に対応する。CI・スクリプト・バッチワークフローからこれらのコマンドを呼び出せる（従来は対話セッション限定）。出典: [Commands — code.claude.com](https://code.claude.com/docs/en/commands)。
>
> **v2.1.206 での挙動改善**: プラグインコマンド `/commit-push-pr`（commit-commands プラグイン）は、`origin` に加えて **configured push remote への push を auto-allow** するようになった。auto mode 下でも自然に走る。
>
> **v2.1.229 での引き締め（2026-08-16 追記）**: 上記の auto-allow は **危険フラグ付きの git 操作には適用されなくなった**。`--force` / `--amend` / `--no-verify` などを伴う場合は**通常どおり承認が求められる**。BOSS のグローバルルール（force push 禁止・`--no-verify` 禁止）とも整合する変更である。出典: CHANGELOG v2.1.229

#### その他のコマンド

公式 commands リファレンスに掲載のあるその他の組み込みコマンド。

| コマンド | 用途 |
|---------|------|
| `/release-notes` | リリースノートの表示 |
| `/team-onboarding` | チーム導入オンボーディングの開始 |
| `/install-github-app` | GitHub App のインストール |
| `/install-slack-app` | Slack App のインストール |
| `/setup-bedrock` / `/setup-vertex` | Amazon Bedrock / Google Vertex AI 接続のセットアップ |
| `/privacy-settings` | プライバシー設定の確認・変更 |
| `/heapdump` | ヒープダンプの取得（診断用） |
| `/autocompact [auto\|<tokens>]` | auto-compact の発動閾値を設定する（v2.1.221+）。`auto` で自動判定に戻す |
| `/import [codex\|gemini]` | 他エージェント CLI（Codex / Gemini）の設定を ClaudeCode 形式へ取り込む（v2.1.213+） |
| `/ide` | IDE 拡張との接続状態を確認・接続する |
| `/voice [hold\|tap\|off]` | 音声入力モードの切替 |
| `/stop` | 実行中の処理を停止する |
| `/terminal-setup` | ターミナルのキーバインド等をセットアップする |
| `/exit`（alias `/quit`） | セッションを終了する |
| `/powerup`・`/passes`・`/radio`・`/stickers`・`/scroll-speed` | 補助・遊び系コマンド（ニッチ） |

#### 主なエイリアス

| 正式コマンド | エイリアス |
|-------------|-----------|
| `/clear` | `/reset`, `/new` |
| `/feedback` | `/share` |
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

> **`/bug` は `/feedback` の alias ではない（v2.1.212〜）**。両者は別コマンドで、`/feedback` の alias は `/share` のみである。以前ここに `/bug` を alias として列挙していたのは誤りだった。

> **バンドルスキル alias の不具合修正（v2.1.233、2026-08-16 追記）**: `/checkup` / `/review` のようなバンドルスキルの alias が、**`-p`（print mode）や plugin / MCP をロードした状態で "Unknown command" になる**不具合が修正された。以前この現象に遭遇していた場合、原因はコマンド名ではなくこのバグである。
>
> **`/feedback` / `/bug` の応答性改善（v2.1.228〜）**: Claude が応答生成中でも**即座に開く**ようになった（従来はターンの終了を待たされた）。

> **print mode のモデル指定ミスの診断（v2.1.233）**: `-p` 実行で未知の model ID を指定した場合、**stderr に `[claude-code:unrecognized_model]` という診断が出る**ようになった。`modelOverrides` で正しいマッピングを与えれば解消する。サイレントに別モデルへフォールバックして気付けなかった問題への対処である。

---

### 並列・バックグラウンド

セッションやタスクを並行実行・管理するコマンド群。

| コマンド | 用途 |
|---------|------|
| `/background [prompt]` | セッションをバックグラウンドエージェント化してターミナルを解放 |
| `/tasks`（alias `/bashes`） | セッション内バックグラウンドタスクの一覧・管理 |
| `/workflows` | ワークフロー進捗ビュー（実行中/完了の監視・一時停止・保存）。**実行中の workflow には現在の size guideline が status line に表示される**（v2.1.219〜） |
| `/subtask <instruction>` | 会話内 forked subagent に脇タスクを渡す（v2.1.212。旧 `/fork`。「セッション管理」節も参照） |
| `/list-agents`（alias `/peers`） | **メッセージを送れる到達可能なセッションの一覧**（v2.1.224）。cross-session messaging 用。`/status` にも `Peer address` 行が追加される。詳細は [sub-agents.md](sub-agents.md) の cross-session messaging 節を参照 |

> **dynamic workflow の既定サイズが変わった（v2.1.219）**: dynamic workflows（`ultracode`）の既定が **medium size guideline（agent 15 体未満を目標）** になった。`/config` の「Dynamic workflow size」または設定キー **`workflowSizeGuideline`** で変更でき、受理値は **`unrestricted`（目安なし）/ `small`（5 体未満）/ `medium`（15 体未満、既定）/ `large`（50 体未満）** の 4 種である。**「1 セッションで数百の並列 subagent」は既定挙動ではなくなった**点に注意（詳細は `docs/harness.md` §4.7）。
>
> これは **cap ではなく「助言」** で、公式は「sends the guideline to Claude as **advice, not a cap**」と明記している。プロンプト側が別スケールを要求すれば上書きされる。また **自分で guideline を選ぶと `Large workflow` 警告の閾値 25 体がその agent 数に置き換わる**（ultracode 有効時は警告自体が出ない）。
>
> ✅ 2026-07-26 時点で本ドキュメントが注記していた「公式 docs が CHANGELOG に追従していない」不整合は、**公式側の追従により解消済み**（公式 [workflows](https://code.claude.com/docs/en/workflows) が「The default is `medium`. … Requires Claude Code v2.1.219 or later; earlier versions default to `unrestricted`」と明記）。出典: [Workflows](https://code.claude.com/docs/en/workflows) / CHANGELOG v2.1.219

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
| `/insights` | セッション分析レポート（プロジェクト領域・操作パターン・摩擦点） |
| `/web-setup` | ローカル `gh` CLI の認証情報で GitHub アカウントを Claude Code on the web に接続（`/schedule` 実行時に未接続なら自動で促される） |
| `/remote-env` | `--remote` で起動する web セッションの既定リモート環境を設定 |
| `/design-sync [name]` | **バンドルスキル**。リポジトリの React デザインシステムを [Claude Design](https://claude.ai/design) にアップロードし、Claude Design が生成する成果物に**実在のコンポーネント**を使わせる。名前の指定も可（例: `/design-sync Acme DS`）。初回同期は全コンポーネントを検証するため、大規模リポでは数時間かかる。**Anthropic API のみ**（Bedrock / Google Cloud Agent Platform / Microsoft Foundry / Claude Platform on AWS では基盤ツールが claude.ai に到達できず利用不可） |
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

大規模な変更を**並列で自動処理**する。指示を 5〜30 の独立ユニットに自動分解し、各 worktree でサブエージェントが作業・テスト・PR 作成を行う。

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

### `/claude-api` — Claude API リファレンス

Claude API / Anthropic SDK / Agent SDK のリファレンスをロードする。コード内で `anthropic` をインポートしている場合は**自動発火**する。

```
/claude-api
/claude-api prompt-audit
```

**サブコマンド**:

| サブコマンド | 内容 |
|---|---|
| `migrate` / `managed-agents-onboard` | 公式 docs 掲載のサブコマンド |
| **`upgrade`**（v2.1.236〜） | **Python `anthropic` 0.x → 1.x の移行**。timeout は `httpx.Timeout` ではなく `anthropic.Timeout` を使う点などを含む |
| **`cost-optimize`**（v2.1.247〜） | **既存プロジェクトの API 支出をプロファイリングし、コストレバーを適用する** |
| **`prompt-audit`**（v2.1.221〜） | **プロンプトとツール説明を「旧世代モデル向けに書かれたパターン」の観点で監査する**。Opus 5 世代への移行支援。公式 docs のコマンド一覧は未更新で、出典は CHANGELOG v2.1.221 |

**使いどころ**:
- Claude API を使ったアプリケーション開発時
- Anthropic SDK の使い方を確認したい場合
- **旧モデル向けに書いたプロンプト資産を Opus 5 世代へ移す時**（`prompt-audit`）。Opus 5 では「検証を促す指示」「委任の推奨」が過剰動作を招くため、既存プロンプトの棚卸しに使える（[best-practices.md](best-practices.md) §8.5 参照）

### その他のバンドルスキル

| スキル | 用途 |
|--------|------|
| `/code-review [low\|medium\|high\|xhigh\|max\|ultra] [--fix] [--comment] [--post\|--no-post] [target]` | diff のバグ検出 + 再利用/簡素化/効率のクリーンアップ。`--fix` で修正適用、`--comment` で GitHub PR のインラインコメント投稿、`ultra` でクラウド多エージェントレビュー。**`ultra` かつ github.com の PR を対象にした場合、`--post` で「レビュー結果をユーザーの GitHub アカウントから 1 件のコメントとして PR に投稿する」選択肢が launch dialog に preselect される**（`--no-post` でその選択肢を隠す。対話セッションでは dialog で確認、非対話では flag だけで投稿される）。**v2.1.218 以降は background subagent として実行**されるため、レビュー作業が会話コンテキストを埋めない（stacked slash commands もレビュー対象として保持される）。**v2.1.232 で `high` / `xhigh` / `max` も background 実行に統一**された（それまでは高 effort 時だけフォアグラウンド実行だった） |
| `/run` | プロジェクトのアプリを起動して変更を実機確認（テストだけに頼らない） |
| `/verify` | 変更がアプリ上で意図通り動くかをビルド・実行して検証 |
| `/deep-research <question>` | Web 横断調査 + 出典クロスチェック + 出典付きレポート（Workflow） |
| `/security-review` | ブランチ差分のセキュリティ脆弱性分析（injection・auth 等）。**種別は組み込みコマンド**（2026-08-12 訂正） |
| `/review [PR]` | **v2.1.223 以降は `/code-review` の alias**。effort レベルとフラグも `/code-review` と全く同じものを受け付ける。深いクラウドレビューは `/code-review ultra`。**v2.1.223 より前**は「1 パスの read-only レビュー」を行う独立コマンドだった（v2.1.186 で `/code-review medium` に統合 → v2.1.202 で単独 fast pass へ revert → **v2.1.223 で再び統合され alias に確定**という経緯） |
| `/fewer-permission-prompts` | transcript を走査し read-only Bash/MCP の allowlist を提案 |
| `/reload-skills` | スキル/コマンドディレクトリを再スキャン（再起動不要、v2.1.152〜）。**種別は組み込みコマンド**（2026-08-12 訂正）。**v2.1.216 以降、セッション中に変更した skills / commands は再起動なしでスラッシュメニューに反映される** |

> **⚠️ 検証系スキルの自発起動が停止した（v2.1.215 / v2.1.218）**: 従来は Claude が必要と判断して自動的に走らせることがあったが、**現在は明示的に呼び出さないと動かない**。
>
> | スキル | 変更 |
> |---|---|
> | `/verify` / `/code-review` | **v2.1.215**: Claude が自発的に起動しなくなった |
> | `/deep-research` | **v2.1.218**: ユーザーが呼び出した時のみ実行。それ以前は Claude 自身も起動できた |
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
2. /loop 5m デプロイの状況を確認して
3. 完了を確認したら会話を中断（Esc）
```

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
| `/hooks` | 組み込み | 環境確認 | Hooks の設定 UI |
| `/mcp [reconnect <server>\|enable\|disable [<server>\|all]]` | 組み込み | 環境確認 | MCP サーバーステータス。**サブコマンドで再接続・有効化・無効化ができる** |
| `/skills` | 組み込み | 環境確認 | Skills 一覧 |
| `/permissions` | 組み込み | 環境確認 | パーミッション設定 |
| `/doctor`（alias `/checkup`） | **バンドルスキル** | 環境確認 | 環境診断 + 自動修復（v2.1.205 で built-in からスキル化）。`disableBundledSkills` の唯一の例外 |
| `/init` | 組み込み | 初期設定 | CLAUDE.md の自動生成 |
| `/sandbox` | 組み込み | 初期設定 | サンドボックスモード |
| `/plugin` | 組み込み | Plugin 管理 | Plugin の管理 UI |
| `/reload-plugins` | 組み込み | Plugin 管理 | Plugin のリロード |
| `/fast` | 組み込み | その他 | Fast モードのトグル |
| `/help` | 組み込み | その他 | ヘルプ表示 |
| `/login` | 組み込み | その他 | 認証ログイン |
| `/logout` | 組み込み | その他 | 認証ログアウト |
| `/simplify [target]` | バンドルスキル | コード品質 | 4 並列サブエージェントでクリーンアップ（バグ検出はしない。v2.1.154〜） |
| `/batch <instruction>` | バンドルスキル | 大規模変更 | 大規模変更の並列自動処理 |
| `/debug [description]` | バンドルスキル | デバッグ | セッションデバッグログの解析 |
| `/loop [interval] [prompt]` | バンドルスキル | 定期実行 | プロンプトの定期実行（**プロンプト省略時は組み込みの maintenance prompt、または `loop.md` を使う**） |
| `/claude-api` | バンドルスキル | リファレンス | Claude API / SDK リファレンスのロード |
| `/btw <question>` | 組み込み | コンテキスト管理 | コンテキストを汚さないサイドバー質問 |
| `/resume [session]` | 組み込み | セッション管理 | 会話を ID/名前/ピッカーで再開（alias `/continue`） |
| `/branch [name]` | 組み込み | セッション管理 | 会話を分岐（複製へ自分が移る） |
| `/fork [prompt]` | 組み込み | セッション管理 | 会話を新しい background セッションへ複製（v2.1.212 で再定義。**v2.1.221 で独自 worktree を作成**） |
| `/subtask <instruction>` | 組み込み | セッション管理 | 脇タスクを会話内 subagent に渡し結果を戻す（v2.1.212。旧 `/fork`） |
| `/recap` | 組み込み | セッション管理 | セッションの 1 行要約 |
| `/plan [description]` | 組み込み | セッション管理 | プロンプトから plan mode 起動 |
| `/model [model]` | 組み込み | モデル・推論制御 | モデル切替（既定として保存） |
| `/effort [level\|auto\|status]` | 組み込み | モデル・推論制御 | effort 設定（`auto` で保存値クリア、`status` で解決結果表示。`max`/`ultracode` は session-only） |
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
| `/diff` | 組み込み | 環境確認 | 差分インタラクティブビューア |
| `/theme` | 組み込み | UI・表示 | カラーテーマ変更 |
| `/focus` | 組み込み | UI・表示 | フォーカスビュー切替 |
| `/tui [default\|fullscreen]` | 組み込み | UI・表示 | TUI レンダラ切替 |
| `/background [prompt]` | 組み込み | 並列・バックグラウンド | セッションをバックグラウンド化 |
| `/tasks` | 組み込み | 並列・バックグラウンド | バックグラウンドタスク一覧（alias `/bashes`） |
| `/workflows` | 組み込み | 並列・バックグラウンド | ワークフロー進捗ビュー |
| ~~`/ultraplan <prompt>`~~ | — | — | **v2.1.222 で削除**。plan mode か Claude Code on the web を使う |
| `/ultrareview [PR]` | 組み込み | クラウド連携 | クラウド多エージェントレビュー |
| `/schedule [description]` | 組み込み | クラウド連携 | routines（クラウド定期実行）の管理 |
| `/teleport` | 組み込み | クラウド連携 | web セッションをターミナルに引き込む（alias `/tp`） |
| `/remote-control` | 組み込み | クラウド連携 | claude.ai からのリモート操作に開放（alias `/rc`） |
| `/autofix-pr [prompt]` | 組み込み | クラウド連携 | PR を監視しクラウドで自動修正 push |
| `/insights` | 組み込み | クラウド連携 | セッション分析レポート |
| `/design-sync [name]` | バンドルスキル | クラウド連携 | リポの React デザインシステムを Claude Design へ同期 |
| `/design-login` | 組み込み | クラウド連携 | `/design-sync` 用のデザインシステムアクセス認可 |
| `/web-setup` | 組み込み | クラウド連携 | gh CLI 認証で GitHub を web に接続 |
| `/remote-env` | 組み込み | クラウド連携 | `--remote` web セッションの既定環境設定 |
| `/code-review [...]` | バンドルスキル | コード品質 | diff のバグ検出 + クリーンアップ（`ultra` でクラウド） |
| `/run` | バンドルスキル | 検証 | アプリを起動して変更を実機確認 |
| `/verify` | バンドルスキル | 検証 | 変更がアプリ上で動くか検証 |
| `/deep-research <question>` | **Workflow** | 調査 | Web 横断調査 + 出典付きレポート |
| `/security-review` | **組み込み** | セキュリティ | ブランチ差分の脆弱性分析 |
| `/review [PR]` | バンドルスキル | レビュー | **`/code-review` の alias**（v2.1.223〜） |
| `/fewer-permission-prompts` | バンドルスキル | パーミッション | read-only allowlist の自動提案 |
| `/reload-skills` | **組み込み** | 環境確認 | スキル/コマンドの再スキャン |

> **種別の訂正（2026-08-12）**: 公式 [Built-in commands](https://code.claude.com/docs/en/commands) と照合し、4 件の分類を修正した。`/doctor` は組み込み → **バンドルスキル**、`/deep-research` はバンドルスキル → **Workflow**、`/security-review` と `/reload-skills` はバンドルスキル → **組み込み**である。

---

## v2.1.234〜v2.1.258 のコマンド・表示の変更

| コマンド | 変更 | 版 |
|---|---|---|
| `/usage` | **Loops breakdown**（loop ごとの実行回数・総トークン・run あたりトークン・最終実行）を追加 | v2.1.243 |
| `/usage` | **Spend limit バー**を追加（statusline の `rate_limits.spend_limit` フィールドと対） | v2.1.251 |
| `/cost` | **per-session の prompt-cache 行**を追加（hit ratio / misses / re-cached tokens / warm・cold） | v2.1.251 |
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

`/config` の Output style から選ぶか、`settings.json` に `{"outputStyle": "Concise"}` を書く。**適用には `/clear` か新セッションが必要**である。

出典: [Output styles — Built-in output styles](https://code.claude.com/docs/en/output-styles#built-in-output-styles) / CHANGELOG v2.1.234〜v2.1.258


## 関連ドキュメント

- [Built-in commands](https://code.claude.com/docs/en/commands) — 公式コマンドドキュメント
- [Best Practices](https://code.claude.com/docs/en/best-practices) — 公式ベストプラクティス
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) — `/loop` を含む定期実行タスク
- [Claude directory](https://code.claude.com/docs/en/claude-directory) — `/context` を含む .claude ディレクトリの確認
- [ClaudeCode Skills ガイド](skills.md) — Skills の詳細（バンドルスキルの仕組み）
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
