# Zed エディタ活用ガイド（ClaudeCode を ACP で動かす）

> 出典:
> - [Zed Docs — Getting Started](https://zed.dev/docs/getting-started)
> - [Zed Docs — Key Bindings](https://zed.dev/docs/key-bindings)
> - [Zed Docs — Agent Panel](https://zed.dev/docs/ai/agent-panel)（ソース: [`docs/src/ai/agent-panel.md`](https://github.com/zed-industries/zed/blob/main/docs/src/ai/agent-panel.md)）
> - [Zed Docs — External Agents (ACP)](https://zed.dev/docs/ai/external-agents)
> - [Zed Docs — Parallel Agents](https://github.com/zed-industries/zed/blob/main/docs/src/ai/parallel-agents.md)
> - 公式キーマップ: [`default-macos.json`](https://github.com/zed-industries/zed/blob/main/assets/keymaps/default-macos.json)（DeepWiki でクロスチェック）
> - 最終更新: 2026-06-08（macOS 基準）

[Zed](https://zed.dev) は Atom / Tree-sitter の開発者が作る高速なマルチプレイヤー型コードエディタである。本リポジトリの文脈では、**ClaudeCode を [ACP（Agent Client Protocol）](https://zed.dev/docs/ai/external-agents) 経由の External Agent として動かすホスト環境**として利用する。iTerm2 / Tabby のようなターミナルから `claude` を起動する代わりに、Zed の **Agent Panel** にスレッドとして JARVIS（ClaudeCode）を常駐させ、エディタの編集・差分レビュー・Git worktree 機能と統合された状態で開発できる。

> **本ガイドの裏取りについて**: 記載のショートカット・仕様はすべて Zed 公式ドキュメントと公式キーマップ（`default-macos.json`）を一次情報として確認済みである。確認できなかった操作は本ガイドに含めていない。網羅的なキーバインドは必ず公式キーマップを参照すること。
>
> **プラットフォーム注記**: 本ガイドは **macOS** のキーバインドを基準とする。Linux / Windows では概ね `cmd` → `ctrl` に読み替える（一部例外あり）。

---

## 1. Zed の主要な使い方

Zed を使い始めるうえで理解すべき中核 UI 概念を整理する。

### 1.1 Command Palette（すべての入口）

`Cmd+Shift+P` で開く Command Palette が「Zed のあらゆるアクションへのゲートウェイ」である。アクション名（例: `agent: new thread`、`editor: rename`）を検索して実行できる。ショートカットを忘れても、まず Command Palette を開けばよい。

### 1.2 プロジェクトを開く

| 方法 | コマンド |
|------|---------|
| CLI から起動 | `zed ~/projects/my-app` |
| 別ウィンドウで開く | `zed -n ~/projects/my-app`（`-n` フラグ） |
| エディタ内から開く | `Cmd+O` |

新しいプロジェクトはデフォルトで**現在のウィンドウ**に開く。別ウィンドウにしたい場合は `-n` を使う。

### 1.3 パネルとドック

Zed の UI は中央のエディタと、それを囲む**ドック**（左・右・下）で構成される。

| ドック / パネル | 役割 | トグル |
|----------------|------|--------|
| 左ドック（Project Panel 等） | ファイルツリー | `Cmd+B` |
| 右ドック | Agent Panel 等 | `Cmd+R`（または `Cmd+Alt+B`） |
| 下ドック | Terminal 等 | `Cmd+J` |
| Project Panel にフォーカス | ファイルツリー操作 | `Cmd+Shift+E` |
| 統合ターミナル | CLI 作業 | `Ctrl+`` ` |

### 1.4 タブ・ペイン・分割

複数ファイルを同時に編集するため、Zed はタブとペイン分割をサポートする。

| 操作 | ショートカット |
|------|--------------|
| ペインを右に分割 | `Cmd+\` |
| ペインを下に分割 | `Cmd+K` → `Down` |
| 隣のペインへ移動 | `Cmd+K` → `Cmd+←/→/↑/↓` |
| 番号でペインをアクティブ化 | `Cmd+1` 〜 `Cmd+9` |

### 1.5 Multibuffer（Zed 特有の概念）

**Multibuffer** は複数ファイルの断片を 1 つの編集可能なバッファに集約する Zed 独自の機能である。プロジェクト全体検索の結果や、AI エージェントの編集差分レビューは、この Multibuffer 上で「複数ファイルをまたいで一括編集・承認」できる。後述の Agent Panel の差分レビュー（§3）もこの仕組みを使う。

### 1.6 ナビゲーションと検索

| 操作 | ショートカット | アクション名 |
|------|--------------|------------|
| ファイルを開く（File Finder） | `Cmd+P` | — |
| プロジェクト全体検索 | `Cmd+Shift+F` | — |
| バッファ内のシンボル一覧（Outline） | `Cmd+Shift+O` | `outline::Toggle` |
| 行番号へジャンプ | `Ctrl+G` | `go_to_line::Toggle` |
| 定義へジャンプ | `F12` | `editor::GoToDefinition` |
| 戻る / 進む（履歴） | `Ctrl+-` / `Ctrl+_` | `pane::GoBack` / `pane::GoForward` |

### 1.7 レイアウトモード（Agentic / Classic）

Zed は 2 つのパネルレイアウトを選べる。

- **Agentic**: Agent Panel と Threads Sidebar を並べて表示。AI 駆動開発向け（本リポジトリの主用途）
- **Classic**: エディタ中心の従来レイアウト

### 1.8 設定

`Cmd+,` で設定（`settings.json`）を開く。テーマ・フォント・format-on-save などを調整する。

---

## 2. 覚えるのを推奨するショートカット

すべてを暗記する必要はない。以下は**実務で使用頻度が高く、覚える投資対効果が高いもの**を厳選した。すべて macOS の公式デフォルト（`default-macos.json`）で確認済み。

### 2.1 最優先（これだけは覚える）

| 操作 | ショートカット |
|------|--------------|
| Command Palette | `Cmd+Shift+P` |
| ファイルを開く | `Cmd+P` |
| プロジェクト全体検索 | `Cmd+Shift+F` |
| 統合ターミナル | `Ctrl+`` ` |
| 設定 | `Cmd+,` |

### 2.2 ナビゲーション

| 操作 | ショートカット | アクション名 |
|------|--------------|------------|
| 定義へジャンプ | `F12` | `editor::GoToDefinition` |
| 戻る / 進む | `Ctrl+-` / `Ctrl+_` | `pane::GoBack` / `pane::GoForward` |
| 行番号へジャンプ | `Ctrl+G` | `go_to_line::Toggle` |
| バッファ内シンボル | `Cmd+Shift+O` | `outline::Toggle` |
| Project Panel フォーカス | `Cmd+Shift+E` | `project_panel::ToggleFocus` |

### 2.3 編集

| 操作 | ショートカット | アクション名 |
|------|--------------|------------|
| 次の同一語を選択（マルチ選択） | `Cmd+D` | `editor::SelectNext` |
| カーソルを上 / 下に追加 | `Cmd+Alt+↑` / `Cmd+Alt+↓` | `editor::AddSelectionAbove/Below` |
| コメントのトグル | `Cmd+/` | `editor::ToggleComments` |
| バッファをフォーマット | `Cmd+Shift+I` | `editor::Format` |
| シンボルのリネーム | `F2` | `editor::Rename` |
| コードアクション | `Cmd+.` | `editor::ToggleCodeActions` |

### 2.4 ペイン・ドック

| 操作 | ショートカット | アクション名 |
|------|--------------|------------|
| 左ドック（ファイルツリー） | `Cmd+B` | `workspace::ToggleLeftDock` |
| 右ドック（Agent Panel） | `Cmd+R` / `Cmd+Alt+B` | `workspace::ToggleRightDock` |
| 下ドック（ターミナル等） | `Cmd+J` | `workspace::ToggleBottomDock` |
| ペインを右に分割 | `Cmd+\` | `pane::SplitRight` |
| 番号でペイン移動 | `Cmd+1`〜`Cmd+9` | `workspace::ActivatePane` |

### 2.5 AI / Agent（ClaudeCode 運用の要）

| 操作 | ショートカット | アクション名 |
|------|--------------|------------|
| Agent Panel のトグル | `Cmd+Shift+A` | — |
| 新規スレッド | `Cmd+N`（Agent Panel フォーカス時） | `agent::NewThread` |
| 新規スレッドメニュー | `Cmd+Alt+Shift+N` | — |
| スレッドスイッチャー（巡回） | `Ctrl+Tab` / `Ctrl+Shift+Tab` | `agents_sidebar::ToggleThreadSwitcher` |
| Threads Sidebar のトグル | `Cmd+Alt+J` | `multi_workspace::ToggleWorkspaceSidebar` |
| サイドバーにフォーカス | `Cmd+Alt+;` | — |
| 選択範囲をコンテキストに追加 | `Cmd+>` | — |
| エージェントの変更をレビュー | `Shift+Ctrl+R` | — |
| 使用モデルの変更 | `Cmd+Alt+/` | — |
| インラインアシスト | `Cmd+Enter` | — |

> **コンテキスト依存の衝突に注意**: 一部のキーは「どのパネルにフォーカスしているか」で意味が変わる。例として `Ctrl+G` はエディタでは「行ジャンプ」だが、Agent Panel フォーカス時は **Thread History** を開く（`agents_sidebar::ToggleThreadHistory`）。`Cmd+N` も Agent Panel フォーカス時は新規スレッド作成になる。

---

## 3. 実際の開発業務のワークフロー（Zed × ClaudeCode）

本リポジトリの [ベストプラクティス](best-practices.md) が掲げる「**探索 → 計画 → 実装 → コミット**」の流れを、Zed の機能にマッピングする。Zed の利点は、この各フェーズが**エディタ内で完結し、差分レビューと Git 操作がネイティブ統合**される点にある。

### Step 0: 準備（LLM プロバイダ / エージェント選択）

1. Agent Panel を開く（`Cmd+Shift+A`）
2. 新規スレッドメニュー（`Cmd+Alt+Shift+N`）で **External Agent（Claude Code）** を選択する
   - 内蔵の **Zed Agent** と、ACP 経由の **External Agent** から選べる
   - JARVIS（ClaudeCode）を使う場合は External Agent を選ぶ
3. 必要に応じて使用モデルを切り替える（`Cmd+Alt+/`）

### Step 1: 探索（コンテキストを与える）

ClaudeCode 公式の「具体的なコンテキストを与える」原則（[best-practices.md §3](best-practices.md)）を、Zed では `@`-mention で行う。

- メッセージ欄で `@` を入力 → ファイル・ディレクトリ・シンボル・過去スレッド・skill・diagnostics を参照として添付できる
- エディタで範囲選択 → `Cmd+>` でその選択をコンテキストに追加
- 画像はエディタに直接ドラッグして添付（vision 対応モデル向け）

### Step 2: 計画

- プロンプトで「まず計画を立てて」と依頼し、実装方針を固める（ClaudeCode の Plan Mode 相当）
- 長い会話がコンテキスト上限に近づいたら、新規スレッドメニューの **「New From Summary」** で会話を圧縮して引き継ぐ（ClaudeCode の `/compact` 相当）

### Step 3: 実装と追従

- プロンプト送信時に `Cmd`（または `Ctrl`）を押しながら送ると、エージェントの作業を**自動追従（follow）**する（左下のクロスヘアアイコンでも切替可能）
- ツール使用インジケータを見ながら、エージェントがファイルを読み・編集する様子を確認する

### Step 4: 差分レビュー（Zed の強み）

エージェントが編集を行うと、Agent Panel が「どのファイルを・何ファイル・何行編集したか」を提示する。

- `Shift+Ctrl+R` で **Multibuffer のレビューペイン**を開く
- 変更を**ハンク単位で個別に accept / reject**、または一括で承認できる
- エディタネイティブの差分表示なので、ターミナルで `git diff` を読むより精度高くレビューできる

### Step 5: チェックポイントと巻き戻し

- エージェントが軌道を外れたら、**checkpoint** から変更を巻き戻せる（ClaudeCode の `/rewind` 相当）
- 応答に thumbs up/down で評価を返すこともできる

### Step 6: コミット

- レビュー承認後は、Zed の Git 機能、または JARVIS に commit → push → PR を依頼する（本リポジトリは [CLAUDE.md の Git/GitHub Workflow](../CLAUDE.md) に従い自走可能）

> **ハーネスとの接続**: 主観評価が必要な UI/UX や長時間タスクでは、§4 の Parallel Agents で「実装スレッド」と「レビュー（評価器）スレッド」を分離すると、[harness.md](harness.md) の Generator / Evaluator 分離を Zed 上で再現できる。

---

## 4. 複数プロジェクトを Zed で起動する（Parallel Agents）

> 本セクションは 3 ソース（zed.dev / DeepWiki `zed-industries/zed` / Context7 の docs ソース）で裏取り済みである。

### 4.1 結論: プロジェクトを分けなくても複数セッションは並行できる

Zed には **Parallel Agents** という専用機能があり、「複数のエージェントスレッドとターミナルスレッドを同時並行で実行でき、**各スレッドが独立した agent・コンテキストウィンドウ・会話履歴を持つ**」。

したがって「複数プロジェクトを別々に立ち上げてセッションを分ける」必要はなく、**同一プロジェクト内でも複数スレッドを並行**できる。プロジェクトを分けるのは「別リポジトリを扱う場合」に限られる。

### 4.2 用語の整理（混同しやすい 2 つのビュー）

| ビュー | 仕様 | 開き方 |
|--------|------|--------|
| **Threads Sidebar** | スレッドを**プロジェクト別にグループ化**して表示（各プロジェクトにセクションヘッダー）。時系列ソートではない | `Cmd+Alt+J`（`ToggleWorkspaceSidebar`） |
| **Thread History** | アーカイブ含む**全スレッドを保持**するビュー | 時計アイコン（`agents_sidebar::ToggleThreadHistory`） |

Threads Sidebar には、エージェントスレッド・External Agent スレッド・ターミナルスレッドが**アイコンで区別されて共存**する。

### 4.3 スレッドの操作

| 操作 | 方法 |
|------|------|
| 新規スレッド | `Cmd+N`（Agent Panel フォーカス時） |
| 切り替え | サイドバーでクリック、または `Ctrl+Tab` / `Ctrl+Shift+Tab` で巡回 |
| サイドバーにフォーカス | `Cmd+Alt+;` |
| サイドバー内でスレッド検索 | サイドバーフォーカス時に `Cmd+F` |
| アーカイブ | スレッドにホバー → アーカイブアイコン、または `Shift+Backspace`（実行中はアーカイブ不可） |
| 復元 | Thread History で対象をクリック（削除された Git worktree も自動復元される） |
| 完全削除 | Thread History でゴミ箱アイコン（会話履歴と worktree データも削除） |

### 4.4 複数プロジェクトを 1 つのサイドバーで扱う

- サイドバー下部の**フォルダアイコン**でプロジェクトを追加する
- 最近のプロジェクトがポップオーバーに表示される（ローカル / リモート両対応）
- **マルチルートプロジェクト**: プロジェクト作成時に複数フォルダを選ぶと、1 スレッドで横断作業できる

### 4.5 ⚠️ Git worktree 分離（並行編集の競合回避）

複数スレッドが**同じファイルを並行編集すると競合する**。Zed はこれを worktree 分離でネイティブに解決する（本リポジトリ [sub-agents.md](sub-agents.md) の `isolation: worktree` と同じ思想）。

- タイトルバーの**プロジェクトピッカー右隣の worktree ピッカー**で、worktree の切替・新規作成（detached HEAD）ができる
- worktree とリンクしたスレッドは、その main worktree のプロジェクト配下にグループ表示される
- `create_worktree` トリガーの **Task hook** で、worktree 作成時の初期化処理を自動化できる（環境変数 `ZED_WORKTREE_ROOT` / `ZED_MAIN_GIT_WORKTREE` が利用可能）
- スレッドをアーカイブすると Git 状態は保持しつつディスク上の worktree を削除し、復元時に再構築する

> **JARVIS 運用との噛み合わせ**: 本リポジトリは JARVIS が git/PR を自走する。実装スレッドを 2 本以上並行させ、同一ファイルに触れる可能性がある場合は worktree 分離を推奨する。Zed 側がスレッドのライフサイクルと worktree を連動管理するため、手動の `git worktree` 管理より安全である。

### 4.6 推奨される並行ワークフロー（公式）

1. **プロジェクト準備**: サイドバーの Add Project で対象プロジェクトを開く
2. **分離戦略**: 同一ファイルを編集しうるスレッドには個別の Git worktree を作る
3. **エージェント割り当て**: スレッドごとに異なるエージェントを割り当てる（1 本は Zed Agent、別は External Agent 等）
4. **並行実行**: 1 本目にプロンプトを送り、完了を待たずに 2 本目で別タスクを開始する
5. **進捗監視**: `Ctrl+Tab` のスレッドスイッチャーで並行作業の進捗を確認する
6. **履歴管理**: 完了したスレッドをアーカイブし、変更は通常の Git ワークフローでレビュー・マージする

### 4.7 既存 ClaudeCode セッションのインポート

External Agent（Claude Code 等）がインストール済みなら、Zed は既存スレッドを検出する。Thread History ツールバーの**インポートアイコン**で、既存の ClaudeCode スレッドを Zed の Thread History に取り込める（※全 External Agent がインポート対応とは限らない）。

---

## 5. BOSS 向けの推奨運用（まとめ）

本リポジトリ・JARVIS の運用文脈での推奨スタイル。

- **タブ（ワークスペース）= リポジトリ単位**で開く（スクショの「1 Revo-index … 6 設定」がこれ）
- **同一リポジトリ内は `Cmd+N` で用途別スレッドを並行**（実装・調査・レビューを分ける）
- **切替は `Cmd+Alt+J`（サイドバー）と `Ctrl+Tab`（巡回）**
- **同一ファイルを並行編集する実装は worktree 分離**
- **差分レビューは `Shift+Ctrl+R` の Multibuffer** でハンク単位に承認

---

## 関連ドキュメント

- [使用ツールスタック](tool-stack.md) — Zed を含む開発環境
- [ClaudeCode のベストプラクティス](best-practices.md) — 探索→計画→実装の原則（本ガイド §3 の土台）
- [ハーネス設計ガイド](harness.md) — Generator / Evaluator 分離（Parallel Agents で再現）
- [SubAgents ガイド](sub-agents.md) — `isolation: worktree`（Zed の worktree 分離と同思想）
- [Zed Docs — Agent Panel](https://zed.dev/docs/ai/agent-panel)（公式一次情報）
- [Zed Docs — External Agents (ACP)](https://zed.dev/docs/ai/external-agents)（公式一次情報）
- [Zed Docs — Parallel Agents](https://github.com/zed-industries/zed/blob/main/docs/src/ai/parallel-agents.md)（公式一次情報）
