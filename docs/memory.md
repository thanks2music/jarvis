# ClaudeCode メモリガイド

> 出典: [Manage memory](https://code.claude.com/docs/en/memory) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Features overview](https://code.claude.com/docs/en/features-overview) / [Context window](https://code.claude.com/docs/en/context-window) / [Claude directory](https://code.claude.com/docs/en/claude-directory) / [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。CHANGELOG は v2.1.296 まで反映)

ClaudeCode のメモリは、セッションをまたいでプロジェクトやユーザーの知識を保持する仕組みである。会話を終えて再起動しても、前回の文脈や学んだことが次のセッションに引き継がれるため、同じ説明を繰り返す必要がなくなる。

ClaudeCode のメモリは **2 つの機構** から成る。どちらもセッション開始時にコンテキストウィンドウへ自動ロードされる。

| 機構 | 正体 | 書く主体 |
|------|------|--------|
| **CLAUDE.md ファイル** | 人が手で書くマークダウン（CLAUDE.md が無いリポジトリでは `AGENTS.md` を代わりに読む。v2.1.277〜） | ユーザー（人間） |
| **Auto Memory（自動メモリ）** | Claude が会話から自動生成するノート | ClaudeCode（AI） |

> **使い分けの原則**
> - **CLAUDE.md**: 意図的に定めたルール・規約（コーディング規約、禁止事項、プロジェクト原則）
> - **Auto Memory**: 会話の中で学んだ動的な知見（ユーザーの好み、過去の失敗、進行中の背景）

---

## 前提知識

### メモリとコンテキストウィンドウの関係

メモリはセッション開始時にフルロードされるため、**コンテキストウィンドウを消費する**。無計画に巨大化させるとパフォーマンスが低下し、Claude が以前の指示を忘れたりミスが増えたりする。メモリは容赦なく剪定し、必要なものだけを残す運用が基本である。

| 項目 | ロードタイミング | コンテキストコスト |
|------|----------------|-------------------|
| CLAUDE.md（親方向） | セッション開始時 | **4 MiB までフル読み込み**（それを超えるファイルは**スキップされる**。2026-09-03 追記） |
| CLAUDE.md（子ディレクトリ） | 子ディレクトリのファイル操作時 | オンデマンド |
| Auto Memory | セッション開始時 | 最初の 200 行または 25KB |
| Skills（description） | セッション開始時 | 低コスト（description のみ） |
| Skills（本文） | 呼び出し時 | 呼び出し時にロード |

### メモリ・CLAUDE.md・Skills の使い分け

| 機能 | 適した用途 |
|------|-----------|
| CLAUDE.md | 毎セッション必要な規約・プロジェクト全体で共通のルール |
| Auto Memory | ユーザーの好み・過去の会話で学んだ動的な知見 |
| `.claude/rules/` | ファイルパス単位で限定したいガイドライン |
| Skills | 必要な時だけロードしたいリファレンス・ワークフロー |

判断基準は「毎セッション必要か？」→ Yes なら CLAUDE.md、「会話から学ぶか？」→ Yes なら Auto Memory、「特定の場面だけ？」→ Skills または Rules となる。

---

## CLAUDE.md ファイル

### 階層構造

ClaudeCode は作業ディレクトリから上位に向かって CLAUDE.md を検索し、**見つかったすべてのファイルを連結** してコンテキストに読み込む（互いに上書きはしない。下記「ロード順序と優先順位」）。

```
~/.claude/CLAUDE.md               ← ユーザーグローバル（全プロジェクト共通）
 └─ project/CLAUDE.md             ← プロジェクト共有（Git 管理推奨）
     └─ project/CLAUDE.local.md   ← 個人用の追記（.gitignore 推奨。上書きではなく連結）
         └─ project/subdir/CLAUDE.md   ← サブディレクトリ（オンデマンドロード）
```

### 配置場所とスコープ

| 配置場所 | 目的 | Git 管理 |
|----------|------|----------|
| `~/.claude/CLAUDE.md` | 全 ClaudeCode セッション共通の個人ルール | しない |
| プロジェクトルートの `./CLAUDE.md` **または `./.claude/CLAUDE.md`** | チームで共有するプロジェクト規約（**2 箇所のどちらでもよい**。2026-08-12 追記） | **する** |
| プロジェクトルートの `./AGENTS.md`（v2.1.277〜） | 他のコーディングエージェントと共有する指示ファイル。作業ディレクトリかその上位に CLAUDE.md が**無い**時に、CLAUDE.md の代わりに読まれる（下記「AGENTS.md の直接読み込み」） | する |
| プロジェクトルートの `./CLAUDE.local.md` | 個人用の追記（ローカル専用） | しない |
| サブディレクトリの `CLAUDE.md` | 特定ディレクトリ配下のみ適用 | する（通常） |
| Managed（Enterprise 配布） | 組織管理の強制ルール | — |

### ロード順序と優先順位

ClaudeCode は現在の作業ディレクトリと**その上位のすべてのディレクトリ**から `CLAUDE.md` / `CLAUDE.local.md` を読み込む。公式は「All discovered files are **concatenated into context rather than overriding each other**」と書いており、**見つかったファイルは連結されるだけで、どれも他を上書きしない**。

- **ディレクトリ間の順序**: ファイルシステムのルートから作業ディレクトリへ向かう順に並ぶ。`foo/bar/` で起動すると `foo/CLAUDE.md` が `foo/bar/CLAUDE.md` より先に入り、起動ディレクトリに近い指示ほど後に読まれる
- **同一ディレクトリ内の順序**:
  1. `CLAUDE.md`（プロジェクト共有）
  2. `CLAUDE.local.md`（個人用）← `CLAUDE.md` の後に追記されるため、そのディレクトリで Claude が最後に読む内容になる
- **競合時**: 2 つの指示が矛盾すると Claude はどちらかを任意に選びうる。後に読まれる側が勝つ保証は無いので、矛盾は書き直して解消する

> **2026-10-11 訂正**: 以前は「`CLAUDE.local.md` は後にマージされるため優先される」と、後のファイルが前のファイルを上書きするかのように書いていた。現行公式は「連結であって上書きではない」と明記している。

**サブディレクトリの CLAUDE.md は、その配下のファイルを操作した時だけオンデマンドでロード**される。モノレポ構成で `packages/frontend/CLAUDE.md` と `packages/backend/CLAUDE.md` を分けておくと、作業対象の領域だけ限定的に読み込める。

### AGENTS.md の直接読み込み（v2.1.277〜、2026-10-11 追記）

**v2.1.277 以降、ClaudeCode は `AGENTS.md` をプロジェクト指示として直接読む**。他のコーディングエージェント向けに `AGENTS.md` を用意済みのリポジトリは、CLAUDE.md・import・設定のどれも足さずにそのまま使える（出典: [Manage memory - AGENTS.md](https://code.claude.com/docs/en/memory)）。

既定で何が読まれるかは、リポジトリにある指示ファイルの組み合わせで決まる。

| リポジトリの状態 | Claude が読むもの |
|---|---|
| `AGENTS.md` があり、作業ディレクトリかその上位に `CLAUDE.md` / `CLAUDE.local.md` が無い | `AGENTS.md` |
| `AGENTS.md` と、作業ディレクトリかその上位に `CLAUDE.md` / `CLAUDE.local.md` がある | `CLAUDE.md` 側だけ |
| `CLAUDE.md` が `@AGENTS.md` を import している | `CLAUDE.md`（`AGENTS.md` は import 経由で入る） |

- **判定に数えるファイル**: 作業ディレクトリかその上位にある `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md`。**`~/.claude/CLAUDE.md`・組織の managed CLAUDE.md・`.claude/rules/` は数えず**、`AGENTS.md` と並んで読まれる
- ⚠️ **`CLAUDE.local.md` も数える**。`AGENTS.md` に頼るプロジェクトで個人用の `CLAUDE.local.md` を足すと、その人には `AGENTS.md` が読まれなくなる。両方読ませるには下記の `claude-md-and-agents-md` にする
- **読まれる場所**: 起動時に作業ディレクトリと上位の `AGENTS.md` / `.claude/AGENTS.md`。サブディレクトリの `AGENTS.md` は、そのディレクトリに CLAUDE.md 3 種が無く、Claude が Read tool でそこのファイルを開いた時に読まれる。`AGENTS.md` 内の `@path` import は展開され、`claudeMdExcludes` も効く
- **読まれないもの**: `AGENTS.local.md`・`AGENTS.override.md`・`.agents/` 配下

**読むファイルの切り替え**: `/config` の **Project instructions** で次の 4 値から選ぶ。

| 値 | Claude が読むもの |
|---|---|
| `claude-md-or-agents-md`（既定） | CLAUDE.md。作業ディレクトリかその上位に `CLAUDE.md` / `CLAUDE.local.md` が無い時だけ `AGENTS.md` |
| `claude-md-and-agents-md` | 両方。各ディレクトリで CLAUDE.md が先、`AGENTS.md` が後。import や symlink で読み込み済みの `AGENTS.md` は二重に読まない |
| `claude-md` | CLAUDE.md だけ |
| `managed-only` | 起動時は組織の managed CLAUDE.md と auto memory だけ。project / local / user の CLAUDE.md・`.claude/rules/`・すべての `AGENTS.md` を外す（サブディレクトリの CLAUDE.md・rules と path-scoped rules はオンデマンドで読まれる） |

設定ファイルで指定する場合は、`pluginConfigs` の **`cc-plugin-agents-md@builtin`**（`AGENTS.md` を読む組込み plugin の ID）の下に書く。**読まれるのは `~/.claude/settings.json`・`--settings` のファイル・managed settings だけ**で、project / local の settings に書いても無視される。

```json
{
  "pluginConfigs": {
    "cc-plugin-agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```

> **plugin ID の変遷**: v2.1.285 より前の ID は `agents-md@builtin` で、`cc-plugin-agents-md@builtin` の項目は無視されていた。v2.1.285 以降はどちらの ID も読む。古い版でも同じ settings を読ませるなら `agents-md@builtin` で書く。
>
> **AGENTS.md の読み込みは組込み mod である**: `/plugin` の Installed タブに **Built-in** として `cc-plugin-agents-md` が並ぶ。`/plugin` で無効化できる。`disableAllHooks`・`--bare`・`--safe-mode` など、インストールした mod を止める設定やフラグでは止まらない。mod（関数 hook を持つ plugin）の仕組みは [mods.md](mods.md) を参照（出典: [Mods overview - Mods built into Claude Code](https://code.claude.com/docs/en/plugins/mods/overview)）。

**直接読めないセッション**（CLAUDE.md だけが読まれ、`/config` に Project instructions が出ない）:

- v2.1.277 より前の版
- `/plugin` で上記の組込み plugin を無効化している
- v2.1.276 以前からアップグレードした直後の最初のセッション（場合による。次のセッションから読む）
- v2.1.281 より前は、Amazon Bedrock のセッションや telemetry を無効にしたセッションなども CLAUDE.md だけを読んでいた

こうしたセッションで `AGENTS.md` を読ませるには、隣に置いた CLAUDE.md から `@AGENTS.md` を import する（下記「補足」）。

**CLAUDE.md として読む場合との違い**: Project instructions 経由で読まれた `AGENTS.md` では **`InstructionsLoaded` hook が発火しない**（CLAUDE.md から import / symlink された `AGENTS.md` では発火する）。また、`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` を設定して `--add-dir` で足したディレクトリでも、**その `AGENTS.md` はロードされない**。

**以前の回避策の扱い**:

| 回避策 | 対応 |
|---|---|
| `@AGENTS.md` を含む CLAUDE.md | 残してよい。どの Project instructions の値でも二重には読まれない。他に何も書いていなければ削除してよいが、直接読めないセッションがあるなら残す |
| 「`AGENTS.md` を読め」と文章で指示する CLAUDE.md | Claude がファイルを開くと決めた時しか読まれない。CLAUDE.md を消して直接読ませるか、文章を `@AGENTS.md` の import に置き換える |
| `AGENTS.md` への symlink にした CLAUDE.md | そのままでも、symlink を消してもよい。どちらでも内容は 1 回だけ読まれる |
| `AGENTS.md` を出力する `SessionStart` hook | **削除する**。直接読み込みと合わせて同じ内容が 2 回入る |

読まれたかどうかは `/memory` の一覧にパスが出るかで確認する（v2.1.280 より前は `/memory` / `/context` に直接読んだ `AGENTS.md` が出なかった）。

### `@` インポート構文

⚠️ **`@import` はコンテキストを節約しない**（2026-09-03 追記）。公式は「Splitting into `@path` imports **helps organization but doesn't reduce context**, since imported files load at launch」と明記している。**肥大化への対策は `paths:` 付きの path-scoped rules が正解**である。本ドキュメント末尾の「215k → 24k 削減」実績は `@import` 自体を廃止してリンク参照に切り替えた対応であり、この公式記述と矛盾しない。

CLAUDE.md 内から他のマークダウンファイルを参照できる。複数のドキュメントを組み合わせて「モジュール化された CLAUDE.md」を構築する際に便利である。

```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

`@~/` でユーザーホームディレクトリ配下のファイルも参照できる。相対パスは**そのファイル自身の位置**を基準に解決される（作業ディレクトリ基準ではない）。

#### import の上限と落とし穴

| 項目 | 仕様 |
|---|---|
| **再帰 import の深さ** | **最大 4 hops**。import されたファイルがさらに import できるが、4 段を超えた分は読まれない |
| **コードブロック内は import されない** | Markdown の code span（`` `@README` ``）と fenced code block はパース対象外。**リテラルとして書きたい場合はバッククォートで囲む** |
| **空白を含むパス**（2026-10-11 追記） | **空白の前にバックスラッシュを置く**（例: `@Design\ Docs/api-conventions.md`）。バックスラッシュが無いと、import だけの行でも最初の空白でパスが切れる。**引用符で囲んだパスはバックスラッシュの有無にかかわらず import されない** |
| **作業ディレクトリ外への import** | プロジェクトスコープの memory から作業ディレクトリ外を import すると、**初回に承認ダイアログ**が出る。拒否すると以後その import は無効のままになり、**ダイアログも再表示されない**。user スコープ（`~/.claude/CLAUDE.md`、`~/.claude/rules/`）からの import はダイアログなし |

> ⚠️ **dotfiles の symlink 運用に直撃する追加仕様（2026-09-03 追記）**: Cowork では上記に加えて ① **`~/.claude/CLAUDE.md` それ自体が symlink / hard link の場合もスキップされる** ② **作業ディレクトリ外を指す symlink された `~/.claude/rules/` ディレクトリ・rule ファイルもスキップされる**。本リポジトリのように `~/.claude/*` を `~/dotfiles` や `avengers` の実体への symlink で運用している構成では、**Cowork セッションでこれらが一切読まれない**ことになる。
>
> **Cowork セッションでは user スコープの外部 import が展開されない（v2.1.232〜、2026-08-16 追記）**: **Claude Cowork のセッションは、user スコープの memory ファイル（`~/.claude/CLAUDE.md` 等）が持つ「外部ファイルへの `@`-import」をインライン展開しなくなった**。本環境の `~/.claude/CLAUDE.md` は `@~/.claude/work-style.md` / `@~/.claude/github-workflow.md` などの外部 import で構成されているため、**Cowork 経由では ClaudeCode CLI と同じ指示が読まれない**ことになる。CLI での挙動は従来どおり変わらない。出典: CHANGELOG v2.1.232

> **4 hops 制限は実運用に効く**: ルート `CLAUDE.md` → 中間ファイル → さらに import と重ねる構成では、深さを意識せずネストすると末端が読まれない。本リポジトリのように `CLAUDE.md` が persona ファイル群を直接 import する構成（1 hop）なら問題にならないが、**import されたファイルの中の import も数える**点に注意する。

> **補足（現行で確認できる追加仕様）**:
> - **`AGENTS.md` を CLAUDE.md から import する（フォールバック、2026-10-11 訂正）**: CLAUDE.md の先頭に `@AGENTS.md` を書き、その下に Claude 固有の指示を足す。v2.1.277 以降は `AGENTS.md` が直接読まれるため（上記「AGENTS.md の直接読み込み」）、この import は **CLAUDE.md も置くプロジェクト・Project instructions を `claude-md` にした場合・直接読めないセッション**向けの手段になった。Claude 固有の内容が要らなければ `ln -s AGENTS.md CLAUDE.md` の symlink でもよいが、Edit / Write tool は symlink 越しに書かず、リンク先の `AGENTS.md` を編集するよう Claude に促す。Windows で clone する人がいるなら import を使う（symlink の作成に管理者権限か開発者モードが要り、`core.symlinks` が無効だと 1 行の CLAUDE.md として checkout される）。以前は「公式推奨パターンは `@AGENTS.md` の import」「`/init` は既存の `AGENTS.md` / `.cursorrules` / `.devin/rules/` / `.windsurfrules` を検出して読み込む」と書いていた。前者は直接読み込みの導入で、後者は次項の既定 / opt-in の区別で古くなった。
> - **`/init` が読み取る他ツールの設定ファイル（2026-09-03 訂正）**: **既定で読むのは Cursor rules（`.cursor/rules/` または `.cursorrules`）と Copilot rules（`.github/copilot-instructions.md`）のみ**である。**`CLAUDE_CODE_NEW_INIT=1` を設定した場合に追加で読むのは `AGENTS.md` / `.devin/rules/` / `.windsurf/rules/` または `.windsurfrules` / **`.clinerules`** の 4 種**。⚠️ 旧記述は `.clinerules` を既定側に置いていたが誤りで、**`.clinerules` は opt-in 側**である。
> - **`/import` コマンド（v2.1.213〜）**: 他コーディングエージェントの設定を取り込む。`AGENTS.md` 等の指示ファイルを対応する `CLAUDE.md` へ**一度だけコピー追記**し、MCP サーバー・commands・subagents・skills も引き継ぐ。`/init` と違い「移行」のためのコマンドである。
> - **`.claude/rules/`**: symlink およびユーザーレベル（`~/.claude/rules/`）の rules に対応。作業ディレクトリ外を指す symlink は external import と同じ承認の対象になる（下記「`.claude/rules/` の基本仕様」）。
> - **`InstructionsLoaded` hook**: CLAUDE.md / `.claude/rules/*.md` がロードされた時に発火する hook がある（[hooks.md](hooks.md) 参照）。

#### `.claude/rules/` の基本仕様（2026-09-03 追記）

- **`paths` を持たない rules は `.claude/CLAUDE.md` と同じ優先度で起動時にロードされる**
- **`--setting-sources` から `project` を除くと project rules はスキップされる**（v2.1.211 より前は on-demand rules だけは読まれていた）
- `.md` は**サブディレクトリまで再帰的に発見される**
- **symlink に対応**しており、循環は検知される（symlink されたチェックアウト経由の path マッチは v2.1.198 以降）
- ⚠️ **作業ディレクトリ外を指す symlink は external import 扱い**（2026-10-11 追記）。プロジェクトで external import を承認するまでリンク先の rules はロードされず、**承認後も `paths` を持たない rules だけがロードされる**。承認は対話セッション開始時のダイアログでプロジェクトごとに 1 回で、外部の `@path` import と並んで一覧される。承認なしで共有 rules を使うなら `~/.claude/rules/` に置く（全プロジェクトに効く）
- **network path を指す symlink は読まれない**: `.claude/rules/` や `CLAUDE.md` の symlink が UNC 共有（`\\server\share`）や `/net` / `/Network` 配下を指すと、リンクを辿らずロードしない（`\\wsl$` は network path に数えない）
- ⚠️ **user-level rules（`~/.claude/rules/`）は project rules より先にロードされ、project rule のほうが context の後ろに入る。ただしどちらも他方を上書きしない**。両者が矛盾すると Claude はどちらに従うか分からないため、内容を揃えておく（**2026-10-11 訂正**: 以前は「先にロードされる = project 側が優先する」と書いていたが、現行公式は「Neither set overrides the other」と明記している）

#### `.claude/rules/` の `paths` 展開の上限

rule ファイルの frontmatter に書く `paths` は brace 展開に対応するが、無制限ではない。

| 項目 | 仕様 |
|---|---|
| **展開上限** | 1 つの rule の `paths` リスト全体で **1,000 展開パターンかつ 4 MiB** の予算を共有する。brace を含まないパターンはこの予算を消費しない |
| **超過時の挙動** | 超過したパターンは**未展開のまま使われ、リテラルの `{}` として何にもマッチしない**（v2.1.217 より前は起動時に stall / crash していた） |
| **展開数の数え方** | brace グループは掛け算になる。`src/*.{ts,tsx}` は 2 パターン、`{a,b}/{c,d}/*.{ts,tsx}` は 8 パターン |
| **`[` は bracket expression** | `photos [2024/**` は不正で何にもマッチしない（v2.1.207 より前は Read tool が全ファイルで失敗していた）。リテラルの `[` は **`photos \[2024/**`** とエスケープする |

### 200 行ルール

公式のベストプラクティスとして **CLAUDE.md は 200 行以下** を推奨している。

> **公式原文（2026-09-03 に verbatim 化）**: 「**Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence.」（同旨は `claude-directory` にも "Target under 200 lines..." として掲載）。以前は「この英語表現は現行公式ページに verbatim では存在しない」と注記していたが、**現在は直接引用できる**。
>
> ⚠️ **200 行 / 25KB の上限は `MEMORY.md` にのみ適用される**点に注意する（CLAUDE.md 側の上限は 4 MiB）。
>
> （旧記述・履歴）公式は「CLAUDE.md は 200 行以内に保ち、リファレンス的な内容は skills へ移してオンデマンドでロードせよ」という趣旨を推奨している（要約。**この英語表現は現行公式ページに verbatim では存在しないため、引用形から要約形に改めた**。2026-08-12 確認）。

CLAUDE.md は全セッションでフルロードされるため、肥大化すると Claude がルールの一部を無視し始める。詳細なリファレンスは Skills に切り出し、CLAUDE.md からは `@` 参照または Skills の description で間接的に利用する運用が望ましい。

### HTML コメントで Claude から隠す（v2.1.72 以降）

ClaudeCode v2.1.72 以降、CLAUDE.md 内の HTML コメント `<!-- ... -->` は**自動注入時に Claude から隠される** 仕様になった。人間向けのメンテナンス情報・履歴・背景説明などをファイルに残しつつ、Claude のコンテキストには渡さないという使い分けが可能である。

> **精密な仕様(2026-07 時点の再確認)**: stripping は **block-level HTML コメントのみ** が対象。**inline HTML コメント**(段落中に `<!-- ... -->` を挟むケース)や **code block 内**(``` フェンス内)の HTML コメントは stripping されず、そのまま Claude に渡る。「block-level」とは行頭・行末に前後が空行または改行のみの独立行として書かれた HTML コメントを指す。

> 出典: [anthropics/claude-code CHANGELOG v2.1.72](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

```markdown
# CLAUDE.md

## Build Commands
- `npm run build` — 本番ビルド
- `npm run test` — テスト実行

<!--
メンテナー向けメモ: この CLAUDE.md は四半期ごとにレビューする。
前回レビュー: 2026-01-15
次回レビュー予定: 2026-04-15

## 削除候補ルール
- 以前あった「すべての関数に JSDoc を書く」ルールは、
  プロジェクト方針の変更により削除予定
-->

## Coding Standards
- ES modules を使用する（CommonJS 不使用）
```

**特徴:**

| 条件 | Claude の可視性 |
|------|---------------|
| セッション開始時の自動注入 | **見えない**（コンテキストに含まれない） |
| `Read` ツールで明示的に読み込まれた場合 | **見える**（ファイル内容として全体が返される） |

**主な活用シーン:**

- **メンテナンス情報**: 最終レビュー日、次回レビュー予定、改訂履歴
- **削除候補のメモ**: 「このルールは次回見直しで削除予定」等の人間向けメモ
- **背景説明**: ルールが追加された経緯・当時の議論（Claude には結論だけ伝えたい）
- **TODO / FIXME**: CLAUDE.md 自体の改善タスク
- **長文の注釈**: Claude のコンテキスト予算を圧迫したくない補足情報

**注意点:**

- `Read` ツールで明示的に読まれた場合（例: CEO が `cat CLAUDE.md` 相当の操作をした場合や、Claude にファイル全体を読ませた場合）はコメント内容もそのまま渡される
- したがって**機密情報の隠蔽には使用不可**である。あくまで「自動注入時のコンテキスト節約」の目的で使う
- v2.1.71 以前の ClaudeCode ではコメントも含めて全文が注入されるため、バージョン依存がある

### `--add-dir` からの CLAUDE.md ロード

`claude --add-dir ../shared-config` で追加したディレクトリ内の CLAUDE.md は、**デフォルトではロードされない**。以下の環境変数を設定するとロードが有効になる。

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

有効化した場合にロードされるのは次の 4 種である（2026-08-12 追記）。

- `CLAUDE.md`
- `.claude/CLAUDE.md`
- `.claude/rules/*.md`
- `CLAUDE.local.md`

- **`--setting-sources` から `local` を外すと、追加ディレクトリの `CLAUDE.local.md` はスキップされる**（2026-10-11 追記）
- **追加ディレクトリの `AGENTS.md` はロードされない**（2026-10-11 追記）。Project instructions 設定経由の `AGENTS.md` 読み込みは `--add-dir` 先に及ばない（上記「AGENTS.md の直接読み込み」の「CLAUDE.md として読む場合との違い」）

### managed settings から CLAUDE.md を制御する（2026-08-12 追記）

| 設定キー | 内容 |
|---|---|
| **`claudeMdExcludes`** | パス / glob を指定して **CLAUDE.md のロードを除外**する。**symlink 経由で到達する rules ファイルは、`.claude/rules/` 側のパスとリンク先パスのどちらに一致しても除外される**（v2.1.239〜。それより前はリンク先に一致するパターンのみが効いた）。**全スコープで設定でき、レイヤ間でマージ**される（配列設定のマージ規則に従う） |
| **`claudeMd`** | `managed-settings.json` に**内容そのものを直接埋め込む**。⚠️ **managed / policy settings でのみ有効**で、user / project / local に書いても**一切効かない**（2026-09-03 追記）。優先順位は managed な CLAUDE.md ファイルと同じ（user / project より先にロードされる）。ファイルを配らずに組織ルールを配布できる |

### `/compact` 後の再注入ルール（2026-08-12 追記）

コンパクション後に **すべての CLAUDE.md が読み直されるわけではない**。

| 対象 | `/compact` 後 |
|---|---|
| プロジェクトルートの CLAUDE.md と **unscoped rules（`paths:` を持たない `.claude/rules/*.md`）** | **ディスクから再読込される**（compact 前に編集していれば新しい内容が入る。unscoped rules は 2026-10-11 追記） |
| **git status のスナップショット**（2026-10-11 追記） | **リポジトリから取り直される** |
| **ネストした（サブディレクトリの）CLAUDE.md** | ⚠️ **2026-09-03 訂正: Claude が該当ファイルを読んだ時点で再ロードされる**（「再注入されない」は誤り） |
| **`paths:` frontmatter を持つ `.claude/rules/*.md`** | ⚠️ **2026-09-03 訂正: 同上。trigger file を読めば再ロードされる** |
| **auto memory** | **ディスクから再注入される** |
| **plan mode で書いた plan** | **再注入される** |
| **invoked skill の本文** | **再注入される**（skill 単位 5,000 トークン・合計 25,000 トークンの上限。超過分は古い順に破棄） |
| **`compact` source に一致する `SessionStart` hook の出力** | **追加される** |

> **compact 直後、ClaudeCode は直近更新の最大 5 ファイルを再読込し、それに該当する rules / nested CLAUDE.md を再ロードする**。5,000 トークンを超えるファイルは本文なしの `Referenced file` として戻るが、rules は再ロードされる。恒久的に効かせたいルールは `paths:` を外すか、ルート CLAUDE.md へ移す。
>
> （旧記述・履歴）長時間セッションで auto-compaction が走った後、「サブディレクトリのルールが効かなくなった」ように見えるのはこの仕様による。**重要なルールはプロジェクトルートの CLAUDE.md に置く**か、compact 後に対象ファイルを触り直して再ロードさせる。

---

## Auto Memory（自動メモリ）

### 機能概要

Auto Memory は、Claude がユーザーとのやり取りから**自動的に学習したノート**を保存し、次のセッションに持ち越すための仕組みである。ユーザーが明示的に「これを覚えておいて」と指示しなくても、Claude が以下のような知見を自発的に記録する:

- ビルドコマンド・テストコマンドなどの作業手順
- デバッグで得られた知見
- ユーザーの好み・嗜好
- プロジェクト固有の背景情報・意思決定

> 公式は Auto memory を「ビルドコマンド・デバッグで得た知見・ユーザーの好みを記録することで、Claude がやり取りから自律的に学習できる仕組み」と説明している（要約。**この英語表現は現行公式ページに verbatim では存在しないため、引用形から要約形に改めた**。2026-08-12 確認）。

### 有効化条件・無効化

- **必要バージョン**: Auto Memory は **ClaudeCode v2.1.59 以上**で利用できる（`claude --version` で確認）。
- **デフォルト**: **local セッションでは ON**。Claude Tag のセッションを除き、**self-hosted environment のセッションは既定 OFF** で動く（**2026-10-11 訂正**: 以前は条件を付けずに「ON」と書いていた）。
- **無効化の方法**:
  - **`/memory` のトグル**: `autoMemoryEnabled` を **user settings（`~/.claude/settings.json`）に保存する**。つまり OFF にすると、そのプロジェクトだけでなく**全プロジェクトに効く**
  - **1 プロジェクトだけ OFF にする**: そのプロジェクトの settings に `"autoMemoryEnabled": false` を書く
  - **環境変数**: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` で無効化。この変数は 1 セッション分 `autoMemoryEnabled` より優先され、逆に `=0` にすると `--bare` や `autoMemoryEnabled: false` があっても強制的に ON になる
- **キーより強いもの**: `autoMemoryEnabled: true`（未設定と同じ）でも、`--bare`・safe mode・`CLAUDE_CODE_DISABLE_AUTO_MEMORY` がセッション単位で OFF にする（出典: [Settings reference - autoMemoryEnabled](https://code.claude.com/docs/en/settings-reference) / [Environment variables](https://code.claude.com/docs/en/env-vars)）。
- **トグルで ON に戻せないセッション**: background session と、別の ClaudeCode セッションが起動したセッション（Claude が Bash tool で `claude` を実行した場合など）では、トグルは OFF にできても ON には戻せない（表示は `off · can't be turned on here; use a session started outside Claude Code`）。ON に戻すには、端末から直接 `claude` を起動したセッションで `/memory` のトグルを使う。
- **保存先の共有範囲**: マシンローカル。同一 git リポジトリの全 worktree・サブディレクトリで 1 つの memory ディレクトリを共有する（マシン間・クラウド環境では共有されない）。

### 保存場所

Auto Memory は**プロジェクトごとに別ディレクトリ** で管理される。デフォルトの保存先は以下の通りである。

```
~/.claude/projects/<リポジトリパスを変換した文字列>/memory/
```

例として、本リポジトリ (`/Users/yoshi/work/dev/my-projects/JARVIS-aka-AIdentity`) の場合:

```
~/.claude/projects/-Users-yoshi-work-dev-my-projects-JARVIS-aka-AIdentity/memory/
├── MEMORY.md                     ← インデックス（常時ロードされる）
├── user_*.md                     ← ユーザーの属性・好み
├── feedback_*.md                 ← ユーザーから受けた指導
├── project_*.md                  ← 進行中プロジェクトの背景
└── reference_*.md                ← 外部システムへのポインタ
```

プロジェクトが異なれば別ディレクトリで管理されるため、複数リポジトリで作業してもメモリが混ざらない。

### コンテキストへのロード上限

> **`/memory` の現行挙動（2026-09-03 追記）**: ① **まだ存在しない** user / project CLAUDE.md エントリも一覧に出て、選ぶと**新規作成される** ② GUI エディタ（VS Code 等）を開いてもセッションはブロックされない（**v2.1.216 より前は閉じるまで待機していた**）③ 実際にロードされたファイルの確認は **`/context` の Memory files** で行う。
>
> ⚠️ **`#` ショートカットは現行公式 docs（memory / commands）に一切記載がない**。本ドキュメントに残る `#` の記述は**公式で裏が取れていない**ものとして扱う。
>
> メモリファイルは**先頭 200 行または 25KB まで**が会話コンテキストへ自動ロードされる（要約。**この英語表現は現行公式ページに verbatim では存在しないため、引用形から要約形に改めた**。2026-08-12 確認）。

Auto Memory のインデックス（`MEMORY.md`）は、**最初の 200 行または 25KB まで**がコンテキストにロードされる。それ以降はセッションに読み込まれないため、運用上の注意点は以下の通りである。

- `MEMORY.md` は 1 行 150 文字以下のインデックス形式を保つ
- 各メモリの詳細は個別ファイルに分離し、必要になった時だけ参照する
- 古くなったメモリは積極的に削除する

**上限に達した時の挙動（v2.1.210 / v2.1.211 で明確化）**:

- **超過は silent truncation ではない**。書き込み後に上限を計測し、上限に近い場合は Claude に短縮を促し、**超過した場合は書き込み自体は成功するが明示的にエラーを返す**（v2.1.210）。「気付かないうちに後半が読まれていない」状態は起きない。
- **計測対象は実際にロードされる内容のみ**（v2.1.211）。**YAML frontmatter と block-level の HTML コメントは剥がされてから計測**されるため、上限にカウントされない。frontmatter を厚めに書いても本文の予算は削られない。

### メモリファイルの構造

各メモリファイルは frontmatter 付きのマークダウンで構成される。**Claude の auto memory は、ノートを次の 4 種類に分けて書き、その種類を frontmatter の `type` フィールドに記録する**。4 種類は auto memory の組込仕様であり、ユーザーやリポジトリが設定するものではない。

| タイプ | 用途（公式の定義） | 書き方のポイント |
|-------|------|----------------|
| `user` | ユーザーの役割・専門・作業上の好み | 作業に反映すべき属性を記述 |
| `feedback` | ユーザーからの訂正と、ユーザーが認めたやり方 | **Why:**（理由）と **How to apply:**（適用場面）を添える |
| `project` | 進行中の作業・期限・決定のうち、コードや git 履歴から導けないもの | 意思決定の理由と、判断に影響する期限・制約を記述 |
| `reference` | プロジェクト外の情報の在り処（課題トラッカー・ダッシュボードなど） | 「Linear の INGEST プロジェクトに課題がある」等 |

> **2026-10-11 訂正**: 以前は「JARVIS リポジトリでは以下 4 種類のタイプを使い分けている」と、本リポジトリ独自の運用であるかのように書いていた。現行公式は 4 種類を auto memory の仕様として定義している（[Manage memory - Auto memory](https://code.claude.com/docs/en/memory)）。「書き方のポイント」列は公式 docs には無い記述である（実際の memory ファイルの書き方から整理した補足）。
>
> 公式によれば、Claude は**コードベースから導けるもの（アーキテクチャ・ファイルパス・デバッグの修正内容）と、CLAUDE.md に既に書かれていることは保存しない**。また毎セッション何かを保存するわけではなく、将来の会話で役立つかで判断する。

frontmatter のフォーマット例:

```markdown
---
name: メモリの名前
description: 1 行の説明（関連性判定に使用される）
type: user
modified: 2026-07-26T10:32:11Z
---

本文
```

**`modified` フィールド（v2.1.214〜）**: Claude がメモリファイルへ書き込む際、**そのファイルが YAML frontmatter で始まっている場合に限り**、書き込み時刻を **ISO 8601 形式の `modified` フィールド**として記録する。旧バージョンで作られたファイルも、次回書き込み時に自動で付与される。

- **frontmatter を持たないファイルには frontmatter を追加しない**（既存の素のマークダウンを勝手に構造化しない設計）。
- メモリの鮮度判断に使える。「いつ書かれた事実か」が分かるため、古い前提を掘り起こしてしまう事故を減らせる。
- 出典: [Manage memory](https://code.claude.com/docs/en/memory) / CHANGELOG v2.1.214

### 保存場所のカスタマイズ

Auto Memory の保存場所は `autoMemoryDirectory` で変更できる。

```json
// ~/.claude/settings.json
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

**`CLAUDE_CODE_PROJECT_DIR_NAME` による固定（v2.1.234〜）**: `CLAUDE_CONFIG_DIR` と併せて設定すると、**起動リポジトリに関係なく `<config dir>/projects/<その名前>/` を使う**。git リポジトリ外では project root がキーになる。詳細は [session-history.md](session-history.md)。

**retention sweep からの除外（2026-09-03 追記）**: **auto memory ディレクトリは `cleanupPeriodDays` の削除対象から除外される**。ディレクトリ自体が消えるのは「保持期間まるごと空だった場合」のみである。⚠️ **v2.1.228 より前は、memory 配下のフォルダをセッションデータとみなして削除し得た**。

**明示的な削除**: **`claude purge [path]`** は 1 プロジェクト分の ClaudeCode の状態を削除し、`projects/` 配下の transcript と**あわせて auto memory も削除する**。ほかに per-session の `tasks/` / `debug/` / `file-history/`、`history.jsonl` の該当プロンプト行、`~/.claude.json` のプロジェクト項目も消す。削除計画を表示してから確認を取る。フラグは `--dry-run`（下見）/ `-y`・`--yes`（確認省略）/ `-i`・`--interactive`（1 項目ずつ確認）/ `--all`（全プロジェクト。`history.jsonl` は丸ごと削除）。path を省くと対話的に選ぶ。auto memory だけを残したい場合はこのコマンドを使わない（出典: [Claude directory - Clear local data](https://code.claude.com/docs/en/claude-directory) / [CLI reference](https://code.claude.com/docs/en/cli-reference)）。

> **2026-10-11 訂正**: 以前は `claude project purge <path>` と書いていた。**v2.1.288 でコマンド名が `claude purge` に変わった**（docs の「Before v2.1.288, the command was `claude project purge`」と CHANGELOG 2.1.288 による。CHANGELOG は旧名も動き、notice を出すと記載）。

`autoMemoryDirectory` は **すべての settings スコープ**（user / project / local / policy / `--settings`）から設定できる。値は絶対パスか `~/` 始まりである必要がある。

| 設定ファイル | 設定可否 |
|-------------|---------|
| `~/.claude/settings.json`（user） | **可** |
| `.claude/settings.local.json`（local） | **可** |
| `.claude/settings.json`（project / チーム共有） | **可**（ワークスペース信頼ダイアログの承認が条件） |
| Managed 設定（policy） | **可** |
| `--settings` フラグ | **可** |

> project / local スコープで設定した場合、**ワークスペース信頼ダイアログを承認した後にのみ有効**になる（Hooks と同じ信頼ゲート）。共有プロジェクトが無断で機密ディレクトリへ書き込むのを防ぐ仕組みである。
>
> **`permissions.blockReadsOutsideWorkingDirectories` が ON の間**（2026-10-11 追記）は、リポジトリが持ち込む settings ファイルが選んだディレクトリからは、場所にかかわらず auto memory を読み込まず、そこへ保存もしない。
>
> **訂正**: 旧版の本ドキュメントは「project スコープからは設定不可」と記載していたが、現行公式では信頼ゲート付きで project からも設定可能に更新されている（2026-05-30 確認、[Manage memory](https://code.claude.com/docs/en/memory)）。

### SubAgent は独自の auto memory を持つ（2026-08-12 追記）

**SubAgent の memory は `memory:` frontmatter で 3 スコープに分かれる**（2026-09-03 追記）。**`memory:` を書いた SubAgent にのみディレクトリが作られる。**

| `memory:` の値 | 保存先 |
|---|---|
| `project` | `.claude/agent-memory/<name>/` |
| `local` | `.claude/agent-memory-local/` |
| `user` | `~/.claude/agent-memory/` |

ロード量はメイン会話と同じ「`MEMORY.md` の先頭 200 行（25KB 上限）」で、**SubAgent の system prompt に入る**。

**メイン会話の auto memory は SubAgent には読み込まれない**。SubAgent は自身の auto memory を持ち、メイン側とは分離されている。

- 例外は **fork**（`context: fork` / `/fork` 由来）で、この場合はメイン会話の記憶を引き継ぐ。
- 「メインで覚えさせた前提が SubAgent に効いていない」と感じた場合は、この分離が原因であることが多い。**SubAgent に渡したい前提はプロンプトに明示的に含める**。

### フィードバック送信時に共有される範囲が広がった（v2.1.224）

`/feedback` 等でフィードバック調査に同意した場合、transcript に加えて **system prompt・tool 定義・model パラメータも送信**されるようになった。

**CLAUDE.md の内容は system prompt の一部ではなく、system prompt の後に置かれる user message として Claude に渡る**。公式 memory ページは「CLAUDE.md content is delivered as a **user message after the system prompt, not as part of the system prompt itself**」と明記しており、本ドキュメントはこの記述に揃える。

> **2026-10-11 訂正**: 2026-09-03 版はこの節で、前段に「CLAUDE.md は system prompt に含まれない」と書きながら、後段の注意書きで「import された内容も system prompt の一部として送信対象に含まれる」と書いており、自己矛盾していた。あわせて前段の「CHANGELOG v2.1.224 は system prompt の送信のみを述べていた」も誤りだった。CHANGELOG 2.1.224 の原文は「the system prompt (**which includes your `CLAUDE.md` instructions**), tool definitions, and model parameters」で、CLAUDE.md を system prompt の側に含めて書いている。**CHANGELOG と memory ページの言い方は食い違っている**が、渡り方の説明としては memory ページを正とする。

> **CLAUDE.md に機微情報を書いている場合は特に注意する**。CLAUDE.md と、そこから `@import` された内容は、上記のとおり system prompt の後の user message として会話に入る。CHANGELOG 2.1.224 も送信される request の設定に CLAUDE.md の指示が含まれると明記しているため、**どちらの書き方に従っても、フィードバック調査に同意すれば CLAUDE.md と import 先の内容は共有されうる**。本リポジトリのように `docs/private/` を `@import` している構成では、その内容も対象になる。出典: [Manage memory - Claude isn't following my CLAUDE.md](https://code.claude.com/docs/en/memory) / CHANGELOG v2.1.224

---

## `/memory` コマンド

セッション中に `/memory` を実行すると、以下の操作ができる。

- **ロード済みファイルの一覧表示**: CLAUDE.md / CLAUDE.local.md / rules ファイルを確認
- **Auto Memory の ON/OFF トグル**: プライバシーを優先する場合は OFF に切り替え可能。**設定は user settings（`~/.claude/settings.json`）に保存されるため全プロジェクトに効く**（2026-10-11 追記。1 プロジェクトだけ OFF にする方法は「有効化条件・無効化」）
- **読み込まれた `AGENTS.md` の確認**: 直接読み込まれた `AGENTS.md` もパスが一覧に出る（v2.1.280〜）
- **Auto Memory フォルダへのアクセス**: エクスプローラーでフォルダを開くリンクが提供される

```
/memory
```

Auto Memory に保存された内容はすべてプレーンマークダウンであるため、直接開いて編集・削除が可能である。

### 「覚えておいて」と指示する

会話中にユーザーが「これを覚えておいて」と指示すると、Claude は Auto Memory にファイルを保存する。CLAUDE.md に追加したい場合は、明示的に「CLAUDE.md に追加して」と指示するか、`/memory` で CLAUDE.md を直接編集する。

### `#` ショートカット（現行仕様）

以前は `#` で始めるとクイックメモリ入力ができたが、**現在は CLAUDE.md の編集を促す挙動に変更**されている。クイックな追加には会話中の「〜を覚えておいて」指示を使う方が自然である。

---

## CLAUDE.md と Auto Memory の対応表

| 観点 | CLAUDE.md | Auto Memory |
|------|-----------|-------------|
| 誰が書くか | ユーザー（人間） | ClaudeCode（AI） |
| Git 管理 | する（project スコープ） | しない（個人ディレクトリに保存） |
| チーム共有 | できる | できない |
| ファイル形式 | 単一ファイル | トピックごとの複数ファイル + インデックス |
| 最適な内容 | コーディング規約・禁止事項・プロジェクト構造 | 会話で学んだ好み・背景・失敗事例・進行状況 |
| 変更頻度 | 低い（慎重に育てる） | 高い（動的に追加・削除） |
| コンテキスト負荷 | フル読み込み | インデックスの 200 行/25KB まで |
| 推奨サイズ | 200 行以下 | インデックスは 200 行以下、個別ファイルは分離 |

### 公式方針は「Manual Memory → Auto-memory」へ（2026-07-24）

Anthropic 公式ブログ [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) は、Claude 5 世代のコンテキスト設計における 6 つの転換の 1 つとして **「Manual Memory → Auto-memory」** を挙げている。同記事では Anthropic 自身が **ClaudeCode の system prompt を 80% 以上削除して性能低下がなかった**と報告しており、設計思想が「制約する」から「判断を信頼する」へ移っている。

ClaudeCode 運用への含意は以下の通りである。

- **CLAUDE.md は軽量に保ち、「gotcha（落とし穴）とリポジトリ固有の癖」に絞る**。汎用的な良い作法や一般的なコーディング規約を書き込むのではなく、モデルの判断では気付けないリポ固有の事情だけを残す。
- **手動での CLAUDE.md 更新より auto-memory を優先する**。動的に学ぶ内容は Auto Memory 側に流し、CLAUDE.md を肥大させない。
- **`/doctor` で skills と context ファイルを right-size する**（**v2.1.206 以降**）。チェックイン済み CLAUDE.md に対して「**コードから導出できる内容（ディレクトリ構成・依存一覧・アーキテクチャ概要）を削り、落とし穴・理由・ツール既定と異なる規約を残す**」trim を提案する。これは公式が明示的に推奨する運用手段である。
- 上記は本ドキュメントの「パターン 1: プロジェクト原則は CLAUDE.md、動的知見は Auto Memory」と同じ方向であり、公式の裏付けが付いた形になる。

> **本リポジトリでの適用実績**: JARVIS リポジトリでは 2026-07-14 に CLAUDE.md の `docs/` 群への `@import` をリンク参照へ切り替え、常時ロードを 215k → 24k 相当まで削減した（コミット `deed983`）。これは上記の公式方針と整合する変更である。

---

## 実践的な活用パターン

### パターン 1: プロジェクト原則は CLAUDE.md、動的知見は Auto Memory

本 JARVIS リポジトリが典型的な例である。

| 内容 | どこに書くか |
|------|------------|
| 「ドキュメントはすべて日本語で記述」 | `CLAUDE.md` ← 不変のルール |
| 「`docs/best-practices.md` は編集禁止」 | `CLAUDE.md` ← 不変のルール |
| 「JARVIS のトンマナ（丁寧語 + 謙譲語）」 | `CLAUDE.md` ← 不変のルール |
| 「Context7/DeepWiki を WebSearch より優先」 | `feedback_*.md` ← 過去に受けた指導 |
| 「ユーザーの趣味・興味」 | `user_*.md` ← ユーザーの属性 |
| 「進行中の新規プロジェクトの背景」 | `project_*.md` ← プロジェクトの動的情報 |

### パターン 2: 失敗の再発を防ぐ

ユーザーが「それは違う、前も言ったよね」と指摘した場合、Claude は即座に feedback メモリを書く。次回以降のセッションで同じミスを回避できる。

feedback メモリには以下を含めると判断材料として役立つ:

- ルール本体（何をすべきか / すべきでないか）
- **Why:** ルールの理由（過去の失敗事例や強い選好）
- **How to apply:** ルールが適用される場面

### パターン 3: 新セッションへのスムーズな引き継ぎ

長期的なプロジェクトで、セッションをまたいで作業する場合、プロジェクトメモリを保存しておくと**背景・方針・決定事項が次のセッションに自動引き継ぎ**される。同じ説明を何度も繰り返す必要がなくなる。

### パターン 4: モノレポでのディレクトリ別 CLAUDE.md

大規模プロジェクトでは、サブディレクトリごとに CLAUDE.md を配置できる。

```
monorepo/
├── CLAUDE.md                      ← リポジトリ全体の共通ルール
├── packages/
│   ├── frontend/
│   │   └── CLAUDE.md              ← フロントエンド固有のルール
│   └── backend/
│       └── CLAUDE.md              ← バックエンド固有のルール
```

フロントエンドを作業している時のみ `packages/frontend/CLAUDE.md` がロードされるため、コンテキストの無駄遣いを防げる。

### パターン 5: 個人用の指示（CLAUDE.local.md）

プロジェクト `CLAUDE.md` はチーム共有だが、`CLAUDE.local.md` は個人用である。例えば「自分は特定のテストランナーで実行している」「自分の環境では特定のパスを使う」といった個人固有の事情は `CLAUDE.local.md` に書き、`.gitignore` に追加する。`CLAUDE.local.md` は各ディレクトリで `CLAUDE.md` の後に連結され、そのディレクトリで Claude が最後に読む内容になる。**ただし共有の `CLAUDE.md` を上書きするわけではない**。共有側と矛盾する指示を書くと Claude はどちらかを任意に選びうるので、個人用には共有側と矛盾しない追加の事情を書く。`AGENTS.md` を使うプロジェクトでは、`CLAUDE.local.md` を置くと既定設定では `AGENTS.md` が読まれなくなる点にも注意する（「AGENTS.md の直接読み込み」）。

> **2026-10-11 訂正**: 以前は「最後にマージされるため、共有設定を個人設定で上書きできる」と書いていた。現行公式は各ファイルを連結するだけで、互いに上書きしないと明記している。

---

## ベストプラクティス

### CLAUDE.md を育てる運用

- **`/init` で自動生成した CLAUDE.md を出発点にする**: プロジェクトのビルドシステム・テストフレームワーク・コードパターンを ClaudeCode が検出して雛形を作る
- **同じミスを繰り返したらルールを追加**: Claude が同じ間違いを繰り返す場合は、ルールの言い方が曖昧か不足している
- **指示なしで正しく動作するルールは削除**: 不要なルールで肥大化させない
- **強調は 1 行だけに付ける**: Claude が繰り返し無視する 1 行にだけ `IMPORTANT` などの強調を付ける。多くの行を強調するとどれも目立たなくなる（[Best Practices](https://code.claude.com/docs/en/best-practices)。**2026-10-11 訂正**: 以前は「`IMPORTANT:` `YOU MUST` 等でルールへの遵守率が上がる」と一般化して書いていた。公式に `YOU MUST` への言及は無い）
- **コードと同様にレビュー・剪定する**: CLAUDE.md も定期的に見直す対象である
- **`/doctor prompt-audit` で指示ファイルを監査する**（v2.1.283〜、2026-10-11 追記）: CLAUDE.md・CLAUDE.local.md・AGENTS.md と、`.claude/` / `~/.claude/` 配下の rules・skills・commands・subagents・output styles を対象に、**旧モデル向けに書かれた指示・存在しないファイルやコマンドへの参照・互いに矛盾するファイル**を探し、修正案付きのレポートを返す（ファイルは適用を頼むまで変わらない）。パスを渡すと 1 ファイル / 1 ディレクトリに絞れる（例: `/doctor prompt-audit .claude/skills/deploy`）。同梱の `/claude-api` skill 経由で動くため、`skillOverrides` や `disableBundledSkills` でその skill を無効化していると使えない（出典: [Manage memory - Audit your instruction files](https://code.claude.com/docs/en/memory)）

### CLAUDE.md に書くべきもの / 書かないもの

| 書く | 書かない |
|------|----------|
| Claude が推測できない Bash コマンド | コードを読めば分かること |
| デフォルトと異なるコードスタイル | 標準的な言語の慣習 |
| テスト手順と優先するテストランナー | 詳細な API ドキュメント |
| ブランチ名・PR の規約 | 頻繁に変わる情報 |
| プロジェクト固有のアーキテクチャ決定 | 長い説明・チュートリアル |
| 開発環境の特殊事情（必要な環境変数等） | ファイルごとのコードベース説明 |
| よくある落とし穴・非自明な動作 | 自明なプラクティス |

> **2026-10-11 訂正**: 「書かない」列の 6 行目は以前「頻繁には変わらない一般的なコードベース解説」としていたが、公式の該当行は「File-by-file descriptions of the codebase」（ファイルごとのコードベース説明）である（[Best Practices](https://code.claude.com/docs/en/best-practices)）。

### Auto Memory の運用ルール

- **インデックス `MEMORY.md` は 1 行 150 文字以下**: コンテキスト予算に収まるサイズを維持する
- **詳細は個別ファイルに分離**: `MEMORY.md` にはリンクと一行のフック説明のみを書く
- **古くなったメモリは削除**: メモリは時間経過で鮮度が落ちる
- **トピック別に整理**: 時系列ではなく意味で分類する（`user_*.md`, `feedback_*.md` 等）
- **重複を避ける**: 新しく書く前に既存メモリを更新できないか確認する

### 書かないもの（Auto Memory）

以下はコードや git 履歴から取得できるため、Auto Memory に保存すべきではない。

- コードパターン・アーキテクチャ・ファイル構造（コードを読めば分かる）
- git 履歴・最近の変更（`git log` / `git blame` が正）
- 一時的な作業状態（タスクやプランで管理する）
- すでに CLAUDE.md に書かれている内容

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| Claude が同じ間違いを繰り返す | CLAUDE.md が長すぎて無視されている | 200 行以下に削る。リファレンスは Skills に移す |
| Claude が自明なことを質問してくる | CLAUDE.md の表現が曖昧 | 具体的な指示に書き換える（例: 「コードを整形する」ではなく「インデントは 2 スペース」）。強調は繰り返し無視される 1 行にだけ付ける（2026-10-11 訂正: 以前は「`IMPORTANT:` `YOU MUST` 等で強調」と書いていた） |
| **指示ファイルが長すぎるという警告が出る**（2026-10-11 追記） | 推奨の長さを超えたファイルがある（起動時と `/status` で警告）。各ファイルが推奨内でも、合計が上限を超えると起動時に警告が出る。CLAUDE.md・rules ファイル・`@path` import はそれぞれ別ファイルとして数える | path-scoped rules に分ける / 毎セッション不要な内容を削る / `/doctor` の trim 提案を使う |
| **commit / PR の規約を CLAUDE.md に書いたのに従わない**（2026-10-11 追記） | ClaudeCode が自分で足す git の指示と競合している | `includeGitInstructions` で組込みの commit / PR 指示を OFF にし、帰属表記は `attribution` で設定する |
| **`AGENTS.md` が読まれない**（2026-10-11 追記） | 作業ディレクトリか上位に `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md` がある（`~/.claude/CLAUDE.md` は数えない）/ v2.1.277 未満 / Project instructions が `claude-md` か `managed-only` | 「AGENTS.md の直接読み込み」を参照。CLAUDE.md を残したいなら Project instructions を `claude-md-and-agents-md` にするか、CLAUDE.md から `@AGENTS.md` を import する |
| メモリに何が保存されているか分からない | `/memory` で自動メモリフォルダを開く | プレーンマークダウンなので直接確認・編集・削除可能 |
| **特定タイミングで必ず走らせたい指示がある** | **hook にする**（CLAUDE.md は enforcement ではない。ブロックしたいなら **PreToolUse hook**） | [hooks.md](hooks.md) |
| **system prompt レベルに載せたい** | **`--append-system-prompt`** を使う（毎回渡す必要があるためスクリプト向き） | — |
| **実際にロードされたか確認したい** | **`/context` の Memory files** を見る | — |
| Auto Memory の保存場所を変えたい | `autoMemoryDirectory` を設定 | **任意の settings スコープから読まれる**（2026-08-12 訂正。以前ここに書いていた「project 設定からは不可」は誤りで、本文の記述とも矛盾していた） |
| サブディレクトリの CLAUDE.md がロードされない | そのディレクトリ配下のファイルをまだ操作していない | 該当ディレクトリのファイルを読むか操作すると自動でロードされる |
| `--add-dir` で追加したディレクトリの CLAUDE.md がロードされない | デフォルトではロードされない仕様 | `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` を設定 |

---

## Tips

### `/memory` で即座に編集

CLAUDE.md の書き換えは `/memory` コマンドから直接行える。エディタを別途開く必要がなく、ClaudeCode 内でシームレスに編集できる。

### HTML コメントで Claude から情報を隠す

v2.1.72 以降、CLAUDE.md 内の `<!-- ... -->` は自動注入時に Claude から隠される。メンテナンス情報・履歴・削除候補メモなど、人間向けの注釈を書きつつコンテキスト予算を節約できる。詳細は本ドキュメントの「HTML コメントで Claude から隠す」セクションを参照。

### メモリは git 代替ではない

Auto Memory と CLAUDE.local.md は個人ディレクトリに保存され、Git では管理されない。チームで共有したい情報は `CLAUDE.md` または `.mcp.json` など Git 管理対象のファイルに書く必要がある。

### メモリ内容の確認

ユーザーが自身で Auto Memory の内容を確認したい場合、以下のコマンドで保存先を直接閲覧できる。

```bash
ls ~/.claude/projects/<プロジェクトパス>/memory/
```

または ClaudeCode セッション中に `/memory` を実行し、UI からアクセスする。

### プライバシー配慮

Auto Memory を無効化したい場合、`/memory` コマンドから OFF に切り替えられる。ただしこのトグルは user settings に保存され全プロジェクトに効く。機密性の高い**特定のプロジェクトだけ** Auto Memory を OFF にして CLAUDE.md のみで運用するなら、そのプロジェクトの settings に `"autoMemoryEnabled": false` を書く（2026-10-11 訂正: 以前は `/memory` のトグルでプロジェクト単位に切り替えられるかのように書いていた）。

---

## 関連ドキュメント

- [Manage memory](https://code.claude.com/docs/en/memory) — 公式メモリドキュメント
- [Best Practices](https://code.claude.com/docs/en/best-practices) — 公式ベストプラクティス
- [Context window](https://code.claude.com/docs/en/context-window) — コンテキストウィンドウ管理
- [Claude directory](https://code.claude.com/docs/en/claude-directory) — `.claude/` ディレクトリの構造
- [ClaudeCode Skills ガイド](skills.md) — Skills との使い分け
- [ClaudeCode スラッシュコマンドガイド](slash-commands.md) — `/memory` を含むコマンド一覧
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリのベストプラクティス
