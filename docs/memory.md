# ClaudeCode メモリガイド

> 出典: [Manage memory](https://code.claude.com/docs/en/memory) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Features overview](https://code.claude.com/docs/en/features-overview) / [Context window](https://code.claude.com/docs/en/context-window) / [Claude directory](https://code.claude.com/docs/en/claude-directory) / [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-16時点)

ClaudeCode のメモリは、セッションをまたいでプロジェクトやユーザーの知識を保持する仕組みである。会話を終えて再起動しても、前回の文脈や学んだことが次のセッションに引き継がれるため、同じ説明を繰り返す必要がなくなる。

ClaudeCode のメモリは **2 つの機構** から成る。どちらもセッション開始時にコンテキストウィンドウへ自動ロードされる。

| 機構 | 正体 | 書く主体 |
|------|------|--------|
| **CLAUDE.md ファイル** | 人が手で書くマークダウン | ユーザー（人間） |
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
| CLAUDE.md（親方向） | セッション開始時 | フル読み込み |
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

ClaudeCode は作業ディレクトリから上位に向かって CLAUDE.md を検索し、**すべてのファイルをマージ** してコンテキストに読み込む。

```
~/.claude/CLAUDE.md               ← ユーザーグローバル（全プロジェクト共通）
 └─ project/CLAUDE.md             ← プロジェクト共有（Git 管理推奨）
     └─ project/CLAUDE.local.md   ← 個人オーバーライド（.gitignore 推奨）
         └─ project/subdir/CLAUDE.md   ← サブディレクトリ（オンデマンドロード）
```

### 配置場所とスコープ

| 配置場所 | 目的 | Git 管理 |
|----------|------|----------|
| `~/.claude/CLAUDE.md` | 全 ClaudeCode セッション共通の個人ルール | しない |
| プロジェクトルートの `./CLAUDE.md` **または `./.claude/CLAUDE.md`** | チームで共有するプロジェクト規約（**2 箇所のどちらでもよい**。2026-08-12 追記） | **する** |
| プロジェクトルートの `./CLAUDE.local.md` | 個人オーバーライド（ローカル専用） | しない |
| サブディレクトリの `CLAUDE.md` | 特定ディレクトリ配下のみ適用 | する（通常） |
| Managed（Enterprise 配布） | 組織管理の強制ルール | — |

### ロード順序と優先順位

ClaudeCode は現在の作業ディレクトリから**上位に向かって探索**し、見つかった CLAUDE.md をすべてマージする。同一ディレクトリ内では以下の順序でマージされる:

1. `CLAUDE.md`（プロジェクト共有）
2. `CLAUDE.local.md`（個人オーバーライド）← 後にマージされるため優先される

**サブディレクトリの CLAUDE.md は、その配下のファイルを操作した時だけオンデマンドでロード**される。モノレポ構成で `packages/frontend/CLAUDE.md` と `packages/backend/CLAUDE.md` を分けておくと、作業対象の領域だけ限定的に読み込める。

### `@` インポート構文

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
| **作業ディレクトリ外への import** | プロジェクトスコープの memory から作業ディレクトリ外を import すると、**初回に承認ダイアログ**が出る。拒否すると以後その import は無効のままになり、**ダイアログも再表示されない**。user スコープ（`~/.claude/CLAUDE.md`、`~/.claude/rules/`）からの import はダイアログなし |

> **Cowork セッションでは user スコープの外部 import が展開されない（v2.1.232〜、2026-08-16 追記）**: **Claude Cowork のセッションは、user スコープの memory ファイル（`~/.claude/CLAUDE.md` 等）が持つ「外部ファイルへの `@`-import」をインライン展開しなくなった**。BOSS の `~/.claude/CLAUDE.md` は `@~/.claude/work-style.md` / `@~/.claude/github-workflow.md` などの外部 import で構成されているため、**Cowork 経由では ClaudeCode CLI と同じ指示が読まれない**ことになる。CLI での挙動は従来どおり変わらない。出典: CHANGELOG v2.1.232

> **4 hops 制限は実運用に効く**: ルート `CLAUDE.md` → 中間ファイル → さらに import と重ねる構成では、深さを意識せずネストすると末端が読まれない。本リポジトリのように `CLAUDE.md` が persona ファイル群を直接 import する構成（1 hop）なら問題にならないが、**import されたファイルの中の import も数える**点に注意する。

> **補足（現行で確認できる追加仕様）**:
> - **`AGENTS.md` の import 対応**: CLAUDE.md から `AGENTS.md`（他ツールと共有する agent 指示ファイル）を import できる。**公式推奨パターンは `@AGENTS.md` の import**(または非 Windows 環境なら symlink)。`/init` は既存の `AGENTS.md` / `.cursorrules` / `.devin/rules/` / `.windsurfrules` を検出して読み込む(他 AI エージェントツールとの設定共有が容易に)。
> - **`/init` が読み取る他ツールの設定ファイル（2026-08-12 更新）**: 既定で読むのは **Cursor rules と Copilot rules（`.github/copilot-instructions.md`）**、および **`.clinerules`** である。**`AGENTS.md` / `.devin/rules/` / `.windsurfrules` は `CLAUDE_CODE_NEW_INIT=1` を設定した場合のみ**読み取り対象になる（同時に `/init` が対話型・多フェーズになる）。以前ここに「`/init` が `.cursorrules` / `.devin/rules` / `.windsurfrules` も読む」と書いていたのは、既定と opt-in を混同していた。
> - **`.claude/rules/`**: symlink およびユーザーレベル（`~/.claude/rules/`）の rules に対応。
> - **`InstructionsLoaded` hook**: CLAUDE.md / `.claude/rules/*.md` がロードされた時に発火する hook がある（[hooks.md](hooks.md) 参照）。

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

> 公式は「CLAUDE.md は 200 行以内に保ち、リファレンス的な内容は skills へ移してオンデマンドでロードせよ」という趣旨を推奨している（要約。**この英語表現は現行公式ページに verbatim では存在しないため、引用形から要約形に改めた**。2026-08-12 確認）。

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

### managed settings から CLAUDE.md を制御する（2026-08-12 追記）

| 設定キー | 内容 |
|---|---|
| **`claudeMdExcludes`** | パス / glob を指定して **CLAUDE.md のロードを除外**する。**全スコープで設定でき、レイヤ間でマージ**される（配列設定のマージ規則に従う） |
| **`claudeMd`** | `managed-settings.json` に**内容そのものを直接埋め込む**。ファイルを配らずに組織ルールを配布できる |

### `/compact` 後の再注入ルール（2026-08-12 追記）

コンパクション後に **すべての CLAUDE.md が読み直されるわけではない**。

| 対象 | `/compact` 後 |
|---|---|
| プロジェクトルートの CLAUDE.md | **ディスクから再読込される**（compact 前に編集していれば新しい内容が入る） |
| **ネストした（サブディレクトリの）CLAUDE.md** | **再注入されない** |
| **`paths:` frontmatter を持つ `.claude/rules/*.md`** | **再注入されない** |

> 長時間セッションで auto-compaction が走った後、「サブディレクトリのルールが効かなくなった」ように見えるのはこの仕様による。**重要なルールはプロジェクトルートの CLAUDE.md に置く**か、compact 後に対象ファイルを触り直して再ロードさせる。

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
- **デフォルト**: ON。
- **無効化の方法**: セッション中に `/memory` でトグル OFF にする / project settings の `autoMemoryEnabled` を `false` にする / 環境変数 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` を設定する。
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

> メモリファイルは**先頭 200 行または 25KB まで**が会話コンテキストへ自動ロードされる（要約。**この英語表現は現行公式ページに verbatim では存在しないため、引用形から要約形に改めた**。2026-08-12 確認）。

Auto Memory のインデックス（`MEMORY.md`）は、**最初の 200 行または 25KB まで**がコンテキストにロードされる。それ以降はセッションに読み込まれないため、運用上の注意点は以下の通りである。

- `MEMORY.md` は 1 行 150 文字以下のインデックス形式を保つ
- 各メモリの詳細は個別ファイルに分離し、必要になった時だけ参照する
- 古くなったメモリは積極的に削除する

**上限に達した時の挙動（v2.1.210 / v2.1.211 で明確化）**:

- **超過は silent truncation ではない**。書き込み後に上限を計測し、上限に近い場合は Claude に短縮を促し、**超過した場合は書き込み自体は成功するが明示的にエラーを返す**（v2.1.210）。「気付かないうちに後半が読まれていない」状態は起きない。
- **計測対象は実際にロードされる内容のみ**（v2.1.211）。**YAML frontmatter と block-level の HTML コメントは剥がされてから計測**されるため、上限にカウントされない。frontmatter を厚めに書いても本文の予算は削られない。

### メモリファイルの構造

各メモリファイルは frontmatter 付きのマークダウンで構成される。JARVIS リポジトリでは以下 4 種類のタイプを使い分けている。

| タイプ | 用途 | 書き方のポイント |
|-------|------|----------------|
| `user` | ユーザーの役割・好み・知識 | 作業に反映すべき属性を記述 |
| `feedback` | ユーザーから受けた指導 | **Why:**（理由）と **How to apply:**（適用場面）を添える |
| `project` | 進行中プロジェクトの背景 | 意思決定の理由と、判断に影響する期限・制約を記述 |
| `reference` | 外部システムへのポインタ | 「Linear の INGEST プロジェクトに課題がある」等 |

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
> **訂正**: 旧版の本ドキュメントは「project スコープからは設定不可」と記載していたが、現行公式では信頼ゲート付きで project からも設定可能に更新されている（2026-05-30 確認、[Manage memory](https://code.claude.com/docs/en/memory)）。

### SubAgent は独自の auto memory を持つ（2026-08-12 追記）

**メイン会話の auto memory は SubAgent には読み込まれない**。SubAgent は自身の auto memory を持ち、メイン側とは分離されている。

- 例外は **fork**（`context: fork` / `/fork` 由来）で、この場合はメイン会話の記憶を引き継ぐ。
- 「メインで覚えさせた前提が SubAgent に効いていない」と感じた場合は、この分離が原因であることが多い。**SubAgent に渡したい前提はプロンプトに明示的に含める**。

### フィードバック送信時に共有される範囲が広がった（v2.1.224）

`/feedback` 等でフィードバック調査に同意した場合、transcript に加えて **system prompt（= CLAUDE.md の内容を含む）・tool 定義・model パラメータも送信**されるようになった。

> **CLAUDE.md に機微情報を書いている場合は特に注意する**。本リポジトリのように `docs/private/` を `@import` している構成では、**import された内容も system prompt の一部**として送信対象に含まれる。出典: CHANGELOG v2.1.224

---

## `/memory` コマンド

セッション中に `/memory` を実行すると、以下の操作ができる。

- **ロード済みファイルの一覧表示**: CLAUDE.md / CLAUDE.local.md / rules ファイルを確認
- **Auto Memory の ON/OFF トグル**: プライバシーを優先する場合は OFF に切り替え可能
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
- **`/doctor` で skills と context ファイルを right-size する**（公式が明示的に推奨する運用手段）。
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

### パターン 5: 個人オーバーライド

プロジェクト `CLAUDE.md` はチーム共有だが、`CLAUDE.local.md` は個人用である。例えば「自分は特定のテストランナーで実行している」「自分の環境では特定のパスを使う」といった個人固有の事情は `CLAUDE.local.md` に書き、`.gitignore` に追加する。CLAUDE.local.md は各ディレクトリ内で最後にマージされるため、共有設定を個人設定で上書きできる。

---

## ベストプラクティス

### CLAUDE.md を育てる運用

- **`/init` で自動生成した CLAUDE.md を出発点にする**: プロジェクトのビルドシステム・テストフレームワーク・コードパターンを ClaudeCode が検出して雛形を作る
- **同じミスを繰り返したらルールを追加**: Claude が同じ間違いを繰り返す場合は、ルールの言い方が曖昧か不足している
- **指示なしで正しく動作するルールは削除**: 不要なルールで肥大化させない
- **強調表現を活用**: `IMPORTANT:` `YOU MUST` 等でルールへの遵守率が上がる
- **コードと同様にレビュー・剪定する**: CLAUDE.md も定期的に見直す対象である

### CLAUDE.md に書くべきもの / 書かないもの

| 書く | 書かない |
|------|----------|
| Claude が推測できない Bash コマンド | コードを読めば分かること |
| デフォルトと異なるコードスタイル | 標準的な言語の慣習 |
| テスト手順と優先するテストランナー | 詳細な API ドキュメント |
| ブランチ名・PR の規約 | 頻繁に変わる情報 |
| プロジェクト固有のアーキテクチャ決定 | 長い説明・チュートリアル |
| 開発環境の特殊事情（必要な環境変数等） | 頻繁には変わらない一般的なコードベース解説 |
| よくある落とし穴・非自明な動作 | 自明なプラクティス |

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
| Claude が自明なことを質問してくる | CLAUDE.md の表現が曖昧 | 具体的な指示に書き換える（`IMPORTANT:` `YOU MUST` 等で強調） |
| メモリに何が保存されているか分からない | `/memory` で自動メモリフォルダを開く | プレーンマークダウンなので直接確認・編集・削除可能 |
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

Auto Memory を無効化したい場合、`/memory` コマンドから OFF に切り替えられる。機密性の高いプロジェクトでは Auto Memory を OFF にし、CLAUDE.md のみで運用する選択肢もある。

---

## 関連ドキュメント

- [Manage memory](https://code.claude.com/docs/en/memory) — 公式メモリドキュメント
- [Best Practices](https://code.claude.com/docs/en/best-practices) — 公式ベストプラクティス
- [Context window](https://code.claude.com/docs/en/context-window) — コンテキストウィンドウ管理
- [Claude directory](https://code.claude.com/docs/en/claude-directory) — `.claude/` ディレクトリの構造
- [ClaudeCode Skills ガイド](skills.md) — Skills との使い分け
- [ClaudeCode スラッシュコマンドガイド](slash-commands.md) — `/memory` を含むコマンド一覧
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリのベストプラクティス
