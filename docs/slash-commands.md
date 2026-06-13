# ClaudeCode スラッシュコマンドガイド

> 出典: [Built-in commands](https://code.claude.com/docs/en/commands) / [Best Practices](https://code.claude.com/docs/en/best-practices) / [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) / [Routines](https://code.claude.com/docs/en/routines) / [Fast mode](https://code.claude.com/docs/en/fast-mode) / [Claude directory](https://code.claude.com/docs/en/claude-directory) (2026-06-10時点)

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

#### `/clear` — コンテキストリセット

コンテキストウィンドウを**完全にリセット**する。無関係なタスク間の切り替え時に使う。

```
# タスク A 完了後、別のタスク B に取り掛かる前に
/clear
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

#### `/context` — コンテキスト使用量の確認

コンテキスト使用量を**カテゴリ別**に表示する。

```
/context
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

会話履歴に残さずに単発の質問をする。回答はオーバーレイで表示され、コンテキストを汚さない。実装中の細かな確認（API 引数・コマンド名など）に向く。**ツールは使用できない（ファイル読み込み・コマンド実行・検索は不可）ため、既存のコンテキスト内にある情報への質問のみ有効。新たに調べさせたい場合は subagent を使う。**
会話履歴に残さずに単発の質問をする。回答はオーバーレイで表示され、コンテキストを汚さない。実装中の細かな確認（API 引数・コマンド名など）に向く。**Claude 実行中でも投げられる**ため、長時間処理を中断せずに横から確認できる。**ツールは使用できない（ファイル読み込み・コマンド実行・検索は不可）ため、既存のコンテキスト内にある情報への質問のみ有効。新たに調べさせたい場合は subagent を使う。**
```
/btw このコマンドの正しいオプション名は？
```

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
| `/resume [session]`（alias `/continue`） | ID / 名前 / ピッカーで会話を再開（バックグラウンドセッションも表示） |
| `/branch [name]`（alias `/fork`） | 現在の会話をこの地点で分岐。元会話は `/resume` で戻れる |
| `/recap` | セッションの 1 行要約をオンデマンド生成 |
| `/plan [description]` | プロンプトから直接 plan mode に入る（任意のタスクを即指定可） |

---

### モデル・推論制御

モデル選択と思考量（effort）を制御するコマンド群。

| コマンド | 用途 |
|---------|------|
| `/model [model]` | モデル切替。新セッションの既定として保存（`s` で当該セッションのみ。左右キーで effort 調整）。エイリアス: `opus` / `sonnet` / `haiku` のほか、Fable 5 用に `fable`・`best`（access があれば Fable 5、無ければ最新 Opus）が追加（要 v2.1.170+） |
| `/effort [level\|auto]` | effort 設定。`low`/`medium`/`high`/`xhigh`/`max`/`ultracode`（`max`・`ultracode` は session-only、`auto` で既定へ戻す）。Fable 5 / Opus 4.8 のデフォルトは `high`、Opus 4.7 は `xhigh`（モデル初回起動時に自動適用） |
| `/goal [condition\|clear]` | 完了条件を設定し、達成までターンを跨いで継続。`clear`/`stop`/`off` 等で解除 |

---

### 環境確認・診断

セッションの状態やロードされているコンポーネントを確認するコマンド群。

#### `/memory` — メモリファイルの確認

メモリファイルの状態を確認する。

```
/memory
```

#### `/agents` — サブエージェント一覧

ロードされているサブエージェントの一覧を確認する。

```
/agents
```

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

ロードされている Skills の一覧を確認する。

```
/skills
```

#### `/permissions` — パーミッション設定

パーミッションの allowlist / denylist を管理する。安全なコマンドを事前に許可しておくと、承認確認の回数を減らせる。

```
/permissions
```

#### `/doctor` — 環境診断

環境のトラブルシューティングを行う。設定やツールの問題を診断する。

```
/doctor
```

#### その他の環境確認・診断コマンド

| コマンド | 用途 |
|---------|------|
| `/config`（alias `/settings`） | 設定 UI（テーマ・モデル・出力スタイル・エディタモード等） |
| `/status` | 設定 Status タブ（バージョン・モデル・アカウント・接続状況） |
| `/usage`（alias `/cost`, `/stats`） | コスト・プラン使用量・スキル/subagent 別の内訳 |
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

#### `/reload-plugins` — Plugin のリロード

Plugin の変更を即時反映する。ClaudeCode の再起動は不要。

```
/reload-plugins
```

---

### その他

#### `/fast` — Fast モードのトグル

Fast モード（高速出力）を切り替える（`/fast [on|off]`）。**モデルは変わらず**、出力速度のみ向上する。Fast モードは Opus 4.6 / 4.7 / 4.8 で利用できる（特定モデル固定の機能ではない）。

```
/fast
```

> 旧版の本ドキュメントは「同じ Opus 4.6 モデルのまま」と記載していたが、Fast モードは特定モデルに紐づくものではなく、現行の Opus 各世代で利用できるトグルである（公式 `commands` リファレンスでは「Toggle fast mode on or off」とのみ記載）。
>
> **Opus 4.8 既定化（v2.1.154〜）**: fast モードは **Opus 4.8 を既定**とし、$10/$50 per MTok（標準の約 2 倍レート・約 2.5 倍速）で動作する。**Opus 4.6 の fast モードは deprecated**。出典: [Fast mode](https://code.claude.com/docs/en/fast-mode#understand-the-cost-tradeoff)。

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
| `/powerup`・`/passes`・`/radio`・`/stickers`・`/scroll-speed` | 補助・遊び系コマンド（ニッチ） |

#### 主なエイリアス

| 正式コマンド | エイリアス |
|-------------|-----------|
| `/clear` | `/reset`, `/new` |
| `/feedback` | `/bug`, `/share` |
| `/rewind` | `/checkpoint`, `/undo` |
| `/loop` | `/proactive` |
| `/resume` | `/continue` |
| `/branch` | `/fork` |
| `/config` | `/settings` |
| `/usage` | `/cost`, `/stats` |
| `/tasks` | `/bashes` |
| `/teleport` | `/tp` |
| `/remote-control` | `/rc` |

---

### 並列・バックグラウンド

セッションやタスクを並行実行・管理するコマンド群。

| コマンド | 用途 |
|---------|------|
| `/background [prompt]` | セッションをバックグラウンドエージェント化してターミナルを解放 |
| `/tasks`（alias `/bashes`） | セッション内バックグラウンドタスクの一覧・管理 |
| `/workflows` | ワークフロー進捗ビュー（実行中/完了の監視・一時停止・保存） |

---

### クラウド連携（Claude Code on the web）

クラウド実行・リモート連携系のコマンド群。各機能の詳細解説は別途整備予定（クラウド機能ガイド）。

| コマンド | 用途 |
|---------|------|
| `/ultraplan <prompt>` | クラウドの ultraplan セッションで計画を作成 → ブラウザでレビュー → リモート実行 or CLI 引き戻し |
| `/ultrareview [PR]` | クラウドサンドボックスで多エージェントの深いレビュー（推奨呼び出しは `/code-review ultra`） |
| `/schedule [description]` | routines（Anthropic 管理クラウドで定期実行）の作成・更新・一覧・実行 |
| `/teleport`（alias `/tp`） | クラウドの web セッションをこのターミナルに引き込む（ブランチ + 会話を取得） |
| `/remote-control`（alias `/rc`） | このセッションを claude.ai からのリモート操作に開放 |
| `/autofix-pr [prompt]` | 現ブランチの PR を監視し、CI 失敗・レビュー時にクラウドセッションが修正を push |
| `/insights` | セッション分析レポート（プロジェクト領域・操作パターン・摩擦点） |
| `/web-setup` | ローカル `gh` CLI の認証情報で GitHub アカウントを Claude Code on the web に接続（`/schedule` 実行時に未接続なら自動で促される） |
| `/remote-env` | `--remote` で起動する web セッションの既定リモート環境を設定 |

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

> **重要な仕様変更（v2.1.154〜）**: `/simplify` は **correctness bug（正しさの不具合）を探さない、クリーンアップ専用**のレビューになった。バグを検出したい場合は `/code-review` を使う。旧版（v2.1.153 以前）の `/simplify` は `/code-review --fix` と同等だった。
>
> **推奨**: コード変更後にすぐ `/simplify`（クリーンアップ）と `/code-review`（バグ検出）を併用すると、品質を維持しやすい。

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

セッションのデバッグログを解析してトラブルシューティングする。

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

### `/loop [interval] <prompt>` — 定期実行

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
```

**使いどころ**:
- Claude API を使ったアプリケーション開発時
- Anthropic SDK の使い方を確認したい場合

### その他のバンドルスキル

| スキル | 用途 |
|--------|------|
| `/code-review [low\|medium\|high\|xhigh\|max\|ultra] [--fix] [--comment] [target]` | diff のバグ検出 + 再利用/簡素化/効率のクリーンアップ。`ultra` でクラウド多エージェントレビュー |
| `/run` | プロジェクトのアプリを起動して変更を実機確認（テストだけに頼らない） |
| `/verify` | 変更がアプリ上で意図通り動くかをビルド・実行して検証 |
| `/deep-research <question>` | Web 横断調査 + 出典クロスチェック + 出典付きレポート（Workflow） |
| `/security-review` | ブランチ差分のセキュリティ脆弱性分析（injection・auth 等） |
| `/review [PR]` | PR をローカルでレビュー（深いクラウドレビューは `/code-review ultra`） |
| `/fewer-permission-prompts` | transcript を走査し read-only Bash/MCP の allowlist を提案 |
| `/reload-skills` | スキル/コマンドディレクトリを再スキャン（再起動不要、v2.1.152〜） |

---

## 実践的なワークフロー

### ワークフロー 1: 探索 → 計画 → 実装 → レビュー

```
1. Plan Mode で探索・計画   ← /plan（Shift+Tab で切り替え）
2. 実装                     ← Normal Mode に戻して実装
3. /simplify                ← 品質レビュー
4. /clear                   ← 次のタスクに向けてリセット
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
4. /simplify                ← 変更後の品質レビュー
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
| `/agents` | 組み込み | 環境確認 | サブエージェント一覧 |
| `/hooks` | 組み込み | 環境確認 | Hooks の設定 UI |
| `/mcp` | 組み込み | 環境確認 | MCP サーバーステータス |
| `/skills` | 組み込み | 環境確認 | Skills 一覧 |
| `/permissions` | 組み込み | 環境確認 | パーミッション設定 |
| `/doctor` | 組み込み | 環境確認 | 環境診断 |
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
| `/loop [interval] <prompt>` | バンドルスキル | 定期実行 | プロンプトの定期実行 |
| `/claude-api` | バンドルスキル | リファレンス | Claude API / SDK リファレンスのロード |
| `/btw <question>` | 組み込み | コンテキスト管理 | コンテキストを汚さないサイドバー質問 |
| `/resume [session]` | 組み込み | セッション管理 | 会話を ID/名前/ピッカーで再開（alias `/continue`） |
| `/branch [name]` | 組み込み | セッション管理 | 会話を分岐（alias `/fork`） |
| `/recap` | 組み込み | セッション管理 | セッションの 1 行要約 |
| `/plan [description]` | 組み込み | セッション管理 | プロンプトから plan mode 起動 |
| `/model [model]` | 組み込み | モデル・推論制御 | モデル切替（既定として保存） |
| `/effort [level\|auto]` | 組み込み | モデル・推論制御 | effort 設定（`auto` で既定へ。`max`/`ultracode` は session-only） |
| `/goal [condition\|clear]` | 組み込み | モデル・推論制御 | 完了条件達成までターンを跨いで継続（`clear` で解除） |
| `/config` | 組み込み | 環境確認 | 設定 UI（alias `/settings`） |
| `/status` | 組み込み | 環境確認 | 設定 Status タブ（バージョン・接続状況） |
| `/usage` | 組み込み | 環境確認 | コスト・使用量・内訳（alias `/cost`,`/stats`） |
| `/statusline` | 組み込み | 環境確認 | ステータスライン設定 |
| `/keybindings` | 組み込み | 環境確認 | キーバインド設定ファイル |
| `/diff` | 組み込み | 環境確認 | 差分インタラクティブビューア |
| `/theme` | 組み込み | UI・表示 | カラーテーマ変更 |
| `/focus` | 組み込み | UI・表示 | フォーカスビュー切替 |
| `/tui [default\|fullscreen]` | 組み込み | UI・表示 | TUI レンダラ切替 |
| `/background [prompt]` | 組み込み | 並列・バックグラウンド | セッションをバックグラウンド化 |
| `/tasks` | 組み込み | 並列・バックグラウンド | バックグラウンドタスク一覧（alias `/bashes`） |
| `/workflows` | 組み込み | 並列・バックグラウンド | ワークフロー進捗ビュー |
| `/ultraplan <prompt>` | 組み込み | クラウド連携 | クラウドで計画作成 → ブラウザレビュー |
| `/ultrareview [PR]` | 組み込み | クラウド連携 | クラウド多エージェントレビュー |
| `/schedule [description]` | 組み込み | クラウド連携 | routines（クラウド定期実行）の管理 |
| `/teleport` | 組み込み | クラウド連携 | web セッションをターミナルに引き込む（alias `/tp`） |
| `/remote-control` | 組み込み | クラウド連携 | claude.ai からのリモート操作に開放（alias `/rc`） |
| `/autofix-pr [prompt]` | 組み込み | クラウド連携 | PR を監視しクラウドで自動修正 push |
| `/insights` | 組み込み | クラウド連携 | セッション分析レポート |
| `/web-setup` | 組み込み | クラウド連携 | gh CLI 認証で GitHub を web に接続 |
| `/remote-env` | 組み込み | クラウド連携 | `--remote` web セッションの既定環境設定 |
| `/code-review [...]` | バンドルスキル | コード品質 | diff のバグ検出 + クリーンアップ（`ultra` でクラウド） |
| `/run` | バンドルスキル | 検証 | アプリを起動して変更を実機確認 |
| `/verify` | バンドルスキル | 検証 | 変更がアプリ上で動くか検証 |
| `/deep-research <question>` | バンドルスキル | 調査 | Web 横断調査 + 出典付きレポート |
| `/security-review` | バンドルスキル | セキュリティ | ブランチ差分の脆弱性分析 |
| `/review [PR]` | バンドルスキル | レビュー | PR をローカルでレビュー |
| `/fewer-permission-prompts` | バンドルスキル | パーミッション | read-only allowlist の自動提案 |
| `/reload-skills` | バンドルスキル | 環境確認 | スキル/コマンドの再スキャン |

---

## 関連ドキュメント

- [Built-in commands](https://code.claude.com/docs/en/commands) — 公式コマンドドキュメント
- [Best Practices](https://code.claude.com/docs/en/best-practices) — 公式ベストプラクティス
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) — `/loop` を含む定期実行タスク
- [Claude directory](https://code.claude.com/docs/en/claude-directory) — `/context` を含む .claude ディレクトリの確認
- [ClaudeCode Skills ガイド](skills.md) — Skills の詳細（バンドルスキルの仕組み）
- [ClaudeCode のベストプラクティス](best-practices.md) — 本リポジトリの ClaudeCode ベストプラクティス
