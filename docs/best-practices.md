# ClaudeCodeのベストプラクティスに準拠する

> 出典:
> - [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) (2026-07-11 確認、公式版は Opus 4.7 章削除により**一般化**へ構造刷新)
> - [Best practices for using Claude Opus 4.7 with Claude Code](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code) (Anthropic 公式ブログ、Opus 4.7 専用ガイダンス、2026-04-29 時点。本リポでは第 8 章の履歴として保全)
> - [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) / [Model configuration](https://code.claude.com/docs/en/model-config) / [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) (Opus 4.8 の能力・effort デフォルト・ultracode・thinking 分類、2026-06-07 確認)
> - [Introducing Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) / [Introducing Claude Fable 5 and Claude Mythos 5 (platform docs)](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) (Mythos-class モデルの GA・料金・必須 v2.1.170・fallback 挙動、2026-06-10 確認)
> - [Introducing Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5) / [Redeploying Fable 5 and Mythos 5](https://www.anthropic.com/news/redeploying-fable-5) / [Claude Fable 5 promotional access](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access) (Sonnet 5 GA・Fable 5 stop&redeploy・プロモは 07-01〜**2026-07-19 23:59:59 PT で終了**、2026-07-26 確認)
> - [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) (2026-07-07、モデル選択と effort レベル選択の公式ガイダンス)
> - [A field guide to Claude Fable 5: Finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns) (2026-07-06、Fable 5 プロンプト戦略の 4 象限フレーム)
> - [Cookbook: Classifier fallback and billing for Claude Fable 5](https://platform.claude.com/cookbook/fable-5-fallback-billing-guide) (Fable 5 classifier fallback 課金ルール確定、2026-07-11 確認)
> - [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5) / [What's new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5) / [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) / [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) (**Opus 5 の GA・破壊的変更・プロンプト作法・effort 推奨の反転**、2026-07-26 確認)
> - [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) (2026-07-24、Claude 5 世代のコンテキスト設計 6 転換。system prompt 80% 削減の実例)
> - [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration) (2026-07-16、大規模移行の orchestration パターン)
> - [Building verification loops in Claude Code with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills) (2026-07-22、verification loop の 4 配置モデル)
> - [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle) (2026-07-21、AI ネイティブ開発のセキュリティ実践 6 点。第 9 章の出典)
> - [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) / [Permission modes](https://code.claude.com/docs/en/permission-modes) (**Opus 5 の tokenizer 世代確定・auto mode 対応の開区間表現**、2026-08-04 確認)

ClaudeCodeはチャットボットではなく、**エージェント型のコーディング環境**である。ファイルを読み、コマンドを実行し、変更を加え、問題を自律的に解決する。「自分でコードを書いてレビューを頼む」スタイルから「何を作りたいかを説明し、ClaudeCodeが実現方法を考える」スタイルへの転換が必要になる。

## 読み始める前に: Opus 4.7 以降のメンタルモデル

Opus 4.7 以降の最新モデルでは、ClaudeCode を **「行ごとに導くペアプログラマー」** ではなく **「能力ある同僚エンジニアへの委任」** として扱うスタイルが圧倒的に効果的になった。**Opus 5（2026-07-24 GA）ではこの傾向がさらに強まり**、公式は「完全なタスク仕様を初手で渡して放置する」ことを最良の使い方として挙げている。本書全体を読む前に、以下の 2 点を頭に置いておくと、各章の内容が一貫した文脈で理解できる。

- **第 1 ターンに完全な仕様を渡す**: intent / 制約 / 受け入れ基準 / 関連ファイル位置を初手で揃える。曖昧なプロンプトを多ターンで補完していくスタイルはトークン効率も品質も悪化させる。**Opus 5 でもこの原則は強化される方向**で、公式は「完全なタスク仕様を初手で渡して放置するのが最良」と明記している
- **subagent / ツール呼び出しは「明示的に指示」する**: Opus 4.7 はデフォルトでこれらを控えめにする傾向。並列調査やファンアウトを期待するなら、いつ・なぜ使うかを文章で示す。⚠️ **Opus 5 では逆に委任が過剰になる**ため、抑制する方向の指示が必要（§8「Opus 5 への更新」参照）

> **effort のデフォルトはモデルで異なる**: 公式は「effort をサポートする**全モデルで既定は `high`**、**例外は Opus 4.7 のみ `xhigh`**」と定義している。既定モデルが Opus 5 になった現在、実効デフォルトは `high` である。**Opus 5 には model-default hold が無く、旧モデルで設定した effort をそのまま引き継ぐ**点にも注意する。モデル別の一覧と選び方は §8「effort 設定の選び方」、adaptive thinking の使い方は第 8 章で扱う。

## 大前提: コンテキストウィンドウを管理する

**すべてのベストプラクティスはこの一点に集約される。コンテキストウィンドウはすぐに埋まり、埋まるほどパフォーマンスが低下する。**

会話全体・Claudeが読んだファイル・コマンド出力がすべてコンテキストを消費する。デバッグセッション1回だけで数万トークンを使うこともある。コンテキストが満杯に近づくと、Claude は以前の指示を「忘れたり」ミスが増え始める。

- カスタムステータスラインでコンテキスト使用量を常時モニタリングする
- 無関係なタスクの間は `/clear` でコンテキストを完全リセットする
- 部分的な要約は `/compact <指示>` を使う（例: `/compact APIの変更点に集中して`）
- `Esc + Esc` → `/rewind` → 「ここから要約」で特定地点からの部分圧縮も可能
- CLAUDE.md に `"コンパクト時は変更ファイルのリストとテストコマンドを必ず保持して"` と書くと、要約時に重要情報を保護できる

---

## 1. 作業を検証できる手段を提供する（最重要）

> **ポイント**: テスト・スクリーンショット・期待する出力結果を事前に提示すること。これが単一で最もレバレッジが高い行動。

Claudeが自分で検証できる環境を作ることで、パフォーマンスが劇的に向上する。検証手段がなければ「動いているように見えるが実際には壊れている」コードを生成しがちで、すべてのミスにあなたの確認が必要になる。

| 戦略 | 悪い例 | 良い例 |
|------|--------|--------|
| 検証基準を提示する | `"メールアドレス検証関数を実装して"` | `"validateEmail関数を書いて。テストケース: user@example.comはtrue、invalidはfalse、user@.comはfalse。実装後にテストを実行して"` |
| UIの変更を視覚的に検証する | `"ダッシュボードをきれいにして"` | `"[スクリーンショット貼付] このデザインを実装して。結果のスクリーンショットを撮って元と比較し、差異を列挙して修正して"` |
| 症状でなく根本原因を対処する | `"ビルドが失敗している"` | `"ビルドがこのエラーで失敗: [貼り付け]。ビルドが成功するまで修正して。エラーを隠蔽せず根本原因に対処して"` |

検証手段はテストスイート・リンター・出力を確認するBashコマンドでもよい。検証を堅牢にすることへの投資は常に価値がある。

UIの変更を Claude 自身に動作確認させたい場合は **[Claude in Chrome](https://code.claude.com/docs/en/chrome) 拡張**（現在 beta、Chrome / Edge 対応・WSL 非対応）が有効。新しいタブを開き UI を実際にテストし、コードが期待通り動くまでイテレーションさせられる。

**`/goal` — Verification loop の常駐システム**: 公式版 best-practices は 2026-07 更新で `/goal` を **verification loop の first-class システム**として正式紹介した。`/goal <完了条件>` で完了条件を宣言すると、裏で別の evaluator が spawn され、**毎ターン後に完了条件を再チェック**する。ターンを跨ぐ Goal drift (当初の受け入れ基準が長時間タスクで忘れられる問題、[harness.md §4.7](harness.md#47-dynamic-workflowsopus-48公式体系化) 参照) の対策として設計されている。解除は `/goal clear`。長時間の自律実行 (auto mode + Fable 5 + `/goal`) で威力を発揮する。詳細な UI は [slash-commands.md](slash-commands.md) 参照。

> **⚠️ Opus 5 世代での「検証」の扱い（2026-07-24 以降）**: 本章の原則（**検証できる環境を与える**）は Opus 5 でも変わらず最重要である。変わったのは「**誰に検証させるか**」の 2 点である。
>
> 1. **プロンプトでの verify 指示は削る**。Opus 5 は指示なしで自己検証するため、「最後に verification step を入れて」「double-check して」「subagent に verify させて」といった旧世代向けの念押しは **over-verification** を招く。公式は「legacy harness scaffolding が追加する別 verification step」も削除対象に名指ししている（§8「Opus 5 への更新」参照）。
> 2. **一方でハーネス側の検証は自分で組む必要が増えた**。**v2.1.215 で `/verify` と `/code-review` の自発起動が停止**、**v2.1.218 で `/deep-research` も手動起動のみ**になった。「Claude が気付いてレビューしてくれる」前提は成立しない。
>
> つまり本章で言う「検証手段を与える」は、**テスト・リンター・ビルド・スクリーンショットといった決定論的な判定器を用意すること**に一層寄せるのが正しい。公式の大規模移行事例でも、評価軸は LLM の主観ではなく **compiler / test suite / 元コードとの behavioral diff といった "built-in referee"** に置かれている（[harness.md](harness.md) §4.9）。

---

## 2. 探索 → 計画 → 実装 → コミットの順番で進める

> **ポイント**: コーディング前にリサーチと計画を分離する。Plan Modeを活用して間違った問題を解くことを防ぐ。

**Phase 1: 探索** (Plan Mode)
```
read /src/auth でセッションとログインの仕組みを理解して。
また環境変数でシークレットをどう管理しているか確認して。
```

**Phase 2: 計画** (Plan Mode)
```
Google OAuthを追加したい。変更が必要なファイルは？セッションフローは？計画を作って。
```
`Ctrl+G` でプランをテキストエディタに展開し、実装前に直接編集できる。

**Phase 3: 実装** (Normal Mode)

Plan Mode で計画を承認する際、ClaudeCode は以下の **5 つの選択肢** を提示する:

- **Approve and start in auto mode**: auto mode で実装に進む
- **Approve and accept edits**: `acceptEdits` モードで実装に進む
- **Approve and review each edit manually**: 1 編集ずつ手動レビュー
- **Keep planning with feedback**: フィードバックを返してさらに計画を磨く
- **Refine with Ultraplan**: Ultraplan（Claude Code on the web 上の plan mode）でブラウザベースのレビューを使って計画を磨く

各 approve オプションは「計画コンテキストを先にクリアするか」も選べる。auto mode を組み合わせると、長時間タスクの cycle time を大きく短縮できる。

```
計画に従ってOAuthフローを実装して。コールバックハンドラのテストを書き、
テストスイートを実行して失敗を修正して。
```

**Phase 4: コミット**
```
説明的なメッセージでコミットしてPRを作って。
```

> **注意**: Plan Modeにも追加コストがある。タイポ修正・ログ追加・変数名変更のような小さな変更は計画不要。計画が最も有効なのは「変更が複数ファイルに及ぶ」「アプローチが不明確」「修正対象コードに不慣れ」な場合。
>
> **Tips**: **diff を 1 文で説明できるなら計画はスキップしてよい**。逆に 1 文で説明できないなら計画した方がよい。

---

## 3. プロンプトに具体的なコンテキストを提供する

> **ポイント**: 指示が具体的なほど、修正回数は減る。

Claudeは意図を推測できるが、心は読めない。特定のファイルを参照し、制約を明示し、既存パターンを示す。

Opus 4.7 以降では特に **「第 1 ターンに完全な仕様（intent / 制約 / 受け入れ基準 / 関連ファイル位置）を渡す」** ことが効率を大きく左右する。曖昧なプロンプトを多ターンに分けて補完していくスタイルは、トークン効率も品質も悪化しがちなため避ける。詳細は第 8 章「Opus 4.7 を活用する」を参照。**Opus 5 ではこの原則がさらに強まり**、公式は「完全なタスク仕様を初手で渡して放置するのが最良」と明記している（§8「Opus 5 への更新」）。

> **「Simple Specs → Rich References」（2026-07-24 公式）**: 公式ブログ [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) は、Claude 5 世代では **仕様を簡素な文章で説明するより「濃い参照物」を渡す方が効く**と整理している。具体的には **実際のコード・テストスイート・HTML artifact・rubric（評価基準）** を渡す。
>
> 同記事はさらに **「Examples → Interface Design」**（大量の出力例を並べるより、tool / スキルのパラメータ設計で意図を伝える）と **「Rules → Judgment」**（細則の列挙より判断を委ねる。例: 「Write code that reads like the surrounding code」）も挙げている。**本章の「具体的に指示する」は「細かく縛る」ことではなく「濃い参照物と明確な受け入れ基準を渡す」ことだと理解する**のが Claude 5 世代の正しい読み方である。

| 戦略 | 悪い例 | 良い例 |
|------|--------|--------|
| タスクのスコープを絞る | `"foo.pyのテストを追加して"` | `"foo.pyのログアウト状態のエッジケースをカバーするテストを書いて。モック不使用で"` |
| ソースを直接指定する | `"ExecutionFactoryのAPIがなぜこんなに変なの？"` | `"ExecutionFactoryのgit履歴を調べて、APIがこうなった経緯をまとめて"` |
| 既存パターンを参照させる | `"カレンダーウィジェットを追加して"` | `"HotDogWidget.phpを参考にパターンを理解して、同じパターンで月選択と年ページネーション付きカレンダーウィジェットを実装して。既存ライブラリのみ使用"` |
| 症状・場所・完了状態を説明する | `"ログインのバグを修正して"` | `"セッションタイムアウト後にログインが失敗するとユーザーから報告。src/auth/の認証フロー（特にトークンリフレッシュ）を確認。問題を再現する失敗テストを書いてから修正して"` |

> **注意**: 「このファイルで改善できる点は？」のような曖昧なプロンプトが有効な場面もある。探索中や、自分では気づかないことを発見したい時に使う。

**リッチなコンテキストの渡し方:**
- **`@ファイル名`** でファイルを参照（Claudeが自動で読み込む）
- **画像を直接ペースト** またはドラッグ&ドロップ
- **URLを提示** してドキュメントやAPIリファレンスを参照させる（`/permissions` で頻繁に使うドメインをallowlistに追加可能）
- **パイプ入力**: `cat error.log | claude` でファイル内容を直接渡す
- **Claudeに取得させる**: BashコマンドやMCPツール・ファイル読み込みで自律的にコンテキストを収集させる
- **`/btw` でサイドバー質問**: 一時的な確認に使う。回答はオーバーレイで表示され、**会話履歴に残らない**。コンテキストを汚染せずに細かい仕様や数値を確認したい時に有効（[Side questions with /btw](https://code.claude.com/docs/en/interactive-mode#side-questions-with-%2Fbtw)）

---

## 4. 環境を整備する

### CLAUDE.md（全セッション共通のコンテキスト）

> **ポイント**: `/init` でスターターCLAUDE.mdを自動生成し、時間をかけて育てる。

CLAUDE.md はすべての会話の開始時にClaudeが読み込む特別なファイル。Bashコマンド・コードスタイル・ワークフロールールを記載する。`/init` がビルドシステム・テストフレームワーク・コードパターンを検出し、ベースを自動生成する。

```markdown
# Code style
- ES modulesを使う (import/export)、CommonJS (require) は不使用
- 可能な場合はdestructure importを使う

# Workflow
- 一連の変更後は必ずtypecheckを実行
- テストはスイート全体でなく単体テストを優先（パフォーマンス）
```

**CLAUDE.mdに書くべきもの / 書かないもの:**

| 書く | 書かない |
|---------|------------|
| Claudeが推測できないBashコマンド | コードを読めば分かること |
| デフォルトと異なるコードスタイルルール | 標準的な言語の慣習 |
| テスト手順と優先するテストランナー | 詳細なAPIドキュメント（リンクのみ） |
| ブランチ名/PRの規約（リポジトリエチケット） | 頻繁に変わる情報 |
| プロジェクト固有のアーキテクチャ決定 | 長い説明やチュートリアル |
| 開発環境の特殊事情（必要な環境変数など） | ファイルごとのコードベース説明 |
| よくある落とし穴や非自明な動作 | 「クリーンなコードを書く」のような自明なプラクティス |

**運用ルール:**
- **「この行を削除するとClaudeが間違いを犯すか？」** → NOならカット。肥大化したCLAUDE.mdはClaudeに無視される
- 強調表現（`IMPORTANT`、`YOU MUST`）でルールへの遵守率を上げられる
- **チームでgitにcommit**することで、ファイルは時間とともに価値が複利で増える
- Claudeが同じ問題を繰り返す → ファイルが長すぎる。Claudeが書いてある質問をしてくる → 表現が曖昧。コードと同様にレビュー・剪定・動作確認を継続する

**他ファイルのインポート構文:**
```markdown
# CLAUDE.md
プロジェクト概要は @README.md、利用可能なnpmコマンドは @package.json を参照。

# 追加指示
- Gitワークフロー: @docs/git-instructions.md
- 個人オーバーライド: @~/.claude/my-project-instructions.md
```

**配置場所:**
| 場所 | 用途 |
|------|------|
| `~/.claude/CLAUDE.md` | 全Claudeセッションに適用 |
| `./CLAUDE.md` | gitにcommitしてチームで共有（または`CLAUDE.local.md`で`.gitignore`） |
| 親ディレクトリ | モノレポで`root/CLAUDE.md`と`root/foo/CLAUDE.md`が自動的に読み込まれる |
| 子ディレクトリ | そのディレクトリのファイルを操作する際にオンデマンドで読み込まれる |

> **Tips**: CLAUDE.mdは常時読み込まれるため**全セッション共通の情報のみ**を書く。特定ドメインの知識や限定的なワークフローはSkillsを使う（必要な時だけロードされる）。

#### CLAUDE.md の軽量化が公式方針になった（2026-07-24）

公式ブログ [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) は、Claude 5 世代のコンテキスト設計を **「制約する」から「判断を信頼する」へ**の転換として整理した。**Anthropic 自身が ClaudeCode の system prompt を 80% 以上削除して性能低下がなかった**と報告しており、「情報を足すほど良くなる」という前提は成立しない。

Then → Now の 6 転換:

| # | 転換 | 内容 |
|---|---|---|
| ① | **Rules → Judgment** | 細則の列挙より判断を委ねる（例: 「Write code that reads like the surrounding code」） |
| ② | **Examples → Interface Design** | 出力例を並べるより、tool パラメータの表現力で意図を示す |
| ③ | **Upfront Info → Progressive Disclosure** | 「使うかもしれない情報」を先に全部渡さず、**skills に逃がす** |
| ④ | **Repetition → Concision** | system prompt と tool description の**重複を排除** |
| ⑤ | **Manual Memory → Auto-memory** | 手動の CLAUDE.md 更新より auto-memory を使う |
| ⑥ | **Simple Specs → Rich References** | 実コード・テストスイート・HTML artifact・rubric を渡す |

**ClaudeCode 運用への具体的な含意**:

- **CLAUDE.md は「gotcha（落とし穴）とリポジトリ固有の癖」に絞る**。汎用的に良い作法や一般的なコーディング規約は書かない（モデルが既に持っている判断を上書きするだけになる）。上記の「書くべきもの / 書かないもの」表の方針が公式に裏付けられた形である。
- **skills は progressive disclosure 前提でモジュール分割する**（[skills-progressive-disclosure.md](skills-progressive-disclosure.md) 参照）。
- **spec や mockup は `@mention` で参照させる**（本文に転記しない）。
- **`/doctor` で skills と context ファイルを right-size する**（公式が明示的に挙げる運用手段。`/context` でも予算内訳を確認できる）。
- 動的に学ぶ知見は **Auto Memory** 側へ流す（[memory.md](memory.md) 参照）。

> **本リポジトリでの適用実績**: JARVIS リポジトリは 2026-07-14 に CLAUDE.md の `docs/` 群への `@import` をリンク参照へ切り替え、常時ロード量を大幅に削減した（コミット `deed983`）。上記公式方針と整合する変更である。

### CLIツール

> **ポイント**: GitHubには `gh`、AWSには `aws`、GCPには `gcloud` など、外部サービスとのやり取りにはCLIツールを使うよう指示する。

CLIツールはコンテキスト効率の高い外部サービス連携手段。`gh` CLIがあればClaudeはissue作成・PR作成・コメント確認ができる（なければGitHub APIを使うが未認証でレート制限に当たりやすい）。Claudeは未知のCLIツールも学習できる:

```
'foo-cli-tool --help' でfooツールの使い方を学んで、A・B・Cを実現するために使って。
```

### MCPサーバー

> **ポイント**: `claude mcp add` で Notion・Figma・データベースなど外部ツールを接続する。

MCPサーバーにより、issueトラッカーからの機能実装・データベースのクエリ・モニタリングデータの分析・Figmaからのデザイン統合・ワークフローの自動化が可能になる。

### パーミッション設定

> **ポイント**: 承認確認を減らしつつ制御を保つ手段は 3 つ: auto mode、allowlist（`/permissions`）、サンドボックス（`/sandbox`）。新規導入時は auto mode が第一選択。

デフォルトでは、ファイル書き込み・Bashコマンド・MCPツールなどに都度承認が必要。10回承認すると実質的にレビューせず通過させてしまう。

- **Auto mode（推奨）**: 別の分類器モデルがコマンドを審査し、**スコープ逸脱・未知のインフラ操作・敵対的コンテンツ起因の動作**をブロックする。ルーチンワークは確認なしで通過する。`claude --permission-mode auto -p "..."` または対話セッション中の **Shift+Tab** で切替可能。research preview 段階（[Auto mode 解説](https://claude.com/blog/auto-mode)）
- **パーミッション allowlist**: `npm run lint` や `git commit` など安全なツールを事前に許可。`/permissions` で管理。拒否されたアクションは `/permissions` の **Recently denied** タブに表示され、`r` キーで手動承認付きリトライが可能
- **サンドボックス** (`/sandbox`): ファイルシステム・ネットワークアクセスを制限し、その範囲内でClaudeが自由に作業できるOSレベルの分離
- **`--dangerously-skip-permissions`**: 公式 [permission-modes](https://code.claude.com/docs/en/permission-modes) ページで **`--permission-mode bypassPermissions` と equivalent（同等）** と明記されている。現行の公式ベストプラクティスでは言及されておらず、自律実行用途では auto mode が第一選択として案内されている。利用するならインターネット接続なしのサンドボックス環境に限定すること

#### Auto mode 詳細

> 初学者は `Auto mode（推奨）` の概要だけ把握して先に進んでよい。実際に運用を始める段階で本節を再読すると効率的。

**利用条件（[公式の前提](https://code.claude.com/docs/en/permission-modes)）**:

- **プラン**: **All plans**（全プラン。以前は Pro 不可だったが現在は Pro でも利用可能に拡大）
- **モデル**: **Claude Opus 4.6 以降、Sonnet 4.6 以降**（Opus 4.8 / **Opus 5** / **Sonnet 5** を含む）。Sonnet 4.5 / Opus 4.5 / Haiku / claude-3 系は非対応
  - 公式は **モデル名としての明示列挙をせず「Opus 4.6 **or later**」という開区間表現**を使っている（2026-08-04 確認）。したがって **Opus 5 は構造的にこの条件を満たし、対応している**。2026-07-26 版で「明示列挙がないため未確認」としていた扱いは、開区間表現の解釈で解消した
- **分類器モデル**: **v2.1.210 以降は Sonnet 5 が既定**（allowlist が Sonnet 5 を許さない場合はセッションモデルまたは Opus にフォールバック）。セッション初回リクエストで検証し以降は pin される。分類器はセッションのモデルとは独立して動く
- **プロバイダ**: Anthropic API と Claude Platform on AWS は **Opus 4.6 以降 / Sonnet 4.6 以降 / Fable 5** で標準対応。**Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / Claude apps gateway** は **Sonnet 5・Opus 4.7 以降（= Opus 4.7 / 4.8 / Opus 5）・Fable 5** が対象。v2.1.158〜v2.1.206 は `CLAUDE_CODE_ENABLE_AUTO_MODE=1` の opt-in が必要だったが、**v2.1.207 以降は opt-in 不要**で標準有効になった。旧環境変数の設定は残っていても無害だが、新規セットアップでは不要
- **バージョン**: ClaudeCode v2.1.83 以上
- **管理者**: Team / Enterprise では管理者の有効化操作が必要（`permissions.disableAutoMode: "disable"` でロックオフ可能）

> **更新履歴**: 旧版の本ドキュメントは「Pro では利用不可」「Max は Opus 4.7 のみ」と記載していたが、公式 [permission-modes](https://code.claude.com/docs/en/permission-modes) の現行記述では **プランは All plans、モデルは Opus 4.6 以降 / Sonnet 4.6** に更新されている（2026-05-30 確認）。

**ブロック対象の具体例**: `curl | bash` のようなダウンロード&実行、本番デプロイやマイグレーション、IAM / リポジトリ権限付与、強制 push、`main` への直 push、機密データの外部送信、共有インフラへの変更、セッション開始時から存在したファイルの不可逆削除など。これらが安全網として機能するため、ローカル作業中は事実上ほぼ通過する設計になっている。

**v2.1.183 で追加されたブロック対象（破壊的 git / IaC）**: `git reset --hard`・`git checkout -- .`・`git restore .`・`git clean -fd`・`git stash drop`・`git stash clear` は「明示要求なし」ならブロック。`git commit --amend` は「セッション開始前のコミット」に対してのみブロック（エージェント自身が作ったコミットへの amend は許可）。`terraform destroy` / `pulumi destroy` / `cdk destroy` / `terragrunt destroy` は **stack 名を specific に指定した場合のみ** 許可（全体 destroy はブロック）。

**v2.1.195 で追加された 13 カテゴリ**: secret manager writes、DNS / TLS 変更、self-approving PRs、CI checks 無効化、bot コマンドコメント経由の権限昇格、feature-flag 削除、protected IaC scopes、cluster-wide K8s DaemonSets / webhooks、sensitive interactive shells（`bash -i` 等の tunneling）、tunneling ツール、live credential の標準出力印字、PII アクセス、package registry ルーティング変更、`--insecure` フラグ、Claude in Chrome の off-origin 動作。逆に **allowed-by-default に追加** されたのは、セッション内で作られた job の削除、security 系コード書き込み、agent-team 内メッセージ、trusted infra 間のデータフロー。

**v2.1.198〜v2.1.205 で追加されたブロック対象 (2026-07 時点)**:

- **v2.1.198**: pushed commit への `git commit --amend` (message-only の amend は例外) / sandbox network verdict の cache 化 / **PR/issue body 経由の sensitive detail 送信** / external agent runner の `--yes-always` isolation 無効化 / sensitive data location 間の外送
- **v2.1.199**: MCP tool の `_meta["anthropic/requiresUserInteraction"]` は**分類器をバイパスして常にユーザーへ prompt** される (`dontAsk` / `bypassPermissions` でも尊重される。ユーザー確認が本質的に必要なツールの契約が保証される)
- **v2.1.200**: セキュリティ関連テストの削除・force-pass ブロック / セッションで作らなかった **stateful リソースの teardown** ブロック / **API base URL / proxy / webhook / registry mirror の third-party host repointing** (`.env.example` 含む) / `git remote set-url` / `add` の unnamed 変更 / 公開レポへの secret / 個人データ push / 外部レポ / 別 org への PR / third-party フォーク・push / **mid-session の `git remote add` は untrusted** 扱い (トラスト継承変更)
- **v2.1.202**: Remote Control セッションのモード同期改善
- **v2.1.203**: **default branch への push** で sensitive / misdescribed / rerouted 内容ブロック (branch protection と併用可能) / API 応答から個人データを PR body へ持ち込みブロック / 独自 dotfiles repo の personal data 一部例外 / **private repo → public surface のブロック** / sensitive local store からのコミット / PR / gist / package publish
- **v2.1.205**: **セッション JSONL transcript への write** (`~/.claude/projects/`) ブロック / **未定義シェル変数へ向いた `rm -rf "$VAR"`** ブロック (context から解決できない変数を含む場合、事前確認を要求)

これらは特に **long-running な自律実行 + auto mode 併用時に効いてくる**。BOSS の運用で該当するケース (branch protection まわり、mid-session の git remote 変更、secret がらみの push) は事前に承知しておく。

**subagent の事前分類（v2.1.178〜）**: auto mode 分類器は **subagent spawn の直前** にタスク記述を評価するようになった。以前は step 2（実行中の各ツール呼び出し）と step 3（戻り値検査）のみが分類器を通過していたため、subagent 経由でブロック対象アクションを実行する抜け穴が存在した。v2.1.178 でこの穴が塞がれている。

**会話で宣言した境界も尊重される**: ユーザーがチャット内で「push しないで」「レビューしてからデプロイして」と伝えると、デフォルトで許可される操作でも分類器がブロックする。ただし境界はトランスクリプト上のメッセージから毎回読み直されるため、**コンテキストコンパクションでメッセージが削られると失効する**。確実にブロックしたい場合は `/permissions` の deny ルールを使うこと。

**フォールバック挙動**: 分類器が **3 連続でブロック、または累計 20 ブロック** で auto mode は pause し、通常の承認プロンプトに戻る。`-p` フラグでの非インタラクティブ実行中は、フォールバック先のユーザーがいないためそのまま abort する。

> **警告**: 任意コマンドの実行許可はデータ損失・システム破損・プロンプトインジェクションによるデータ流出のリスクがある。**auto mode は事前に境界（分類器の判定基準）が定義されているため、`--dangerously-skip-permissions` よりも安全に同等の自律性が得られる**。

### Hooks（確実な自動実行）

> **ポイント**: 例外なく毎回実行しなければならない処理にはHooksを使う。CLAUDE.mdの指示は「アドバイス」だが、Hooksは「決定論的」で必ず実行される。

- `"全ファイル編集後にeslintを実行するhookを書いて"` などとClaudeに依頼可能
- `"migrationsフォルダへの書き込みをブロックするhookを書いて"` のような制御も可能
- `"タスク完了時に音を鳴らせ"` と頼むと、Claude が hook ベースの完了通知を自分で構成する（Opus 4.7 ブログで紹介された具体例）
- `/hooks` でインタラクティブ設定、または `.claude/settings.json` を直接編集

> **例外: Stop hook の 8 連続 override**: 「Hooks は決定論的で必ず実行される」原則は Stop hook に関して条件付きになる。ClaudeCode は **Stop hook が 8 連続でターン継続を強制した場合、その override を打ち切ってターンを終了する** 挙動を持つ。無限ループで Claude を停止できないケースへのセーフティネット。決定論性を厳密に担保したい制御には `PreToolUse` の `permissionDecision: "deny"` を使う。出典: [Best practices - Verification loops](https://code.claude.com/docs/en/best-practices)

### Skills（ドメイン知識・再利用ワークフロー）

> **ポイント**: `.claude/skills/` に `SKILL.md` を作成してClaudeにドメイン知識と再利用可能なワークフローを与える。必要な時だけロードされるため、CLAUDE.mdを肥大化させずに専門知識を持たせられる。

> **公式方針としての位置づけ（2026-07-24）**: skills は「**Upfront Info → Progressive Disclosure**」（前掲の 6 転換の③）を実現する主要手段として公式に位置づけられた。「使うかもしれない情報」を CLAUDE.md に前倒しで置くのではなく、**skills に逃がして必要時に読ませる**のが Claude 5 世代の標準設計である。設計の具体は [skills-progressive-disclosure.md](skills-progressive-disclosure.md) を参照。
>
> 検証系スキルの構成については、**v2.1.215 以降 `/verify` と `/code-review` が自発起動しなくなった**点に注意する（[skills.md](skills.md) 参照）。検証を確実に走らせるには **Standalone / Embedded / Chained / PR-wide の 4 配置モデル**のいずれかを自分で組む（[harness.md](harness.md) §4.8）。Anthropic 社内では `/code-review` → `/simplify` → `/verify` → 独自デザインチェックのチェーンが使われている。

**ドメイン知識の例**（関連タスク時に自動適用）:
```markdown
---
name: api-conventions
description: REST API設計規約
---
# API規約
- URLパスはkebab-case
- JSONプロパティはcamelCase
- リストエンドポイントには必ずページネーションを含める
- URLパスでAPIをバージョニング (/v1/, /v2/)
```

**ワークフローの例**（手動呼び出し）:
```markdown
---
name: fix-issue
description: GitHubのissueを修正する
disable-model-invocation: true
---
GitHub issue: $ARGUMENTS を分析して修正する。

1. `gh issue view` でissueの詳細を取得
2. 問題を理解する
3. 関連ファイルをコードベースから検索
4. 修正を実装
5. テストを書いて実行して検証
6. lint・型チェックをパス
7. 説明的なコミットメッセージを作成
8. Pushしてプルリクエストを作成
```

`/fix-issue 1234` で呼び出し。`disable-model-invocation: true` は副作用のあるワークフローを手動トリガーに限定する。

### カスタムSubagents

> **ポイント**: `.claude/agents/` に専用アシスタントを定義し、独立したコンテキストで動作する孤立タスクをClaudeに委任させる。

多数のファイルを読む必要があるタスクや、特定の専門知識が必要なタスクに有効。メインの会話コンテキストを汚染しない。

```markdown
---
name: security-reviewer
description: セキュリティ脆弱性のコードレビュー
tools: Read, Grep, Glob, Bash
model: opus
---
シニアセキュリティエンジニアとして以下をレビュー:
- インジェクション脆弱性（SQL・XSS・コマンドインジェクション）
- 認証・認可の欠陥
- コード内のシークレット・認証情報
- 安全でないデータ処理

具体的な行番号と修正案を提示すること。
```

明示的に指示: `"このコードのセキュリティレビューにサブエージェントを使って"`

> **注意（Opus 4.7）**: Opus 4.7 は subagent spawn が控えめになる傾向。詳細と推奨プロンプト例は第 8 章「サブエージェント delegation の指示」を参照。

### Plugins（スキル・ツール・インテグレーションのバンドル）

> **ポイント**: `/plugin` でマーケットプレイスを閲覧。設定なしでSkills・Tools・インテグレーションを追加できる。

PluginsはSkills・Hooks・Subagents・MCPサーバーを一つのインストール可能なユニットにまとめたもの。型付き言語を使う場合は**コードインテリジェンスプラグイン**のインストールを推奨（正確なシンボルナビゲーションと編集後の自動エラー検出を提供）。

> **Tips**: 機能の選び方 — Skills（ドメイン知識・ワークフロー）/ Hooks（確実な自動実行）/ Subagents（独立コンテキストで動作）/ MCP（外部ツール統合）/ Plugins（上記のバンドル）

---

## 5. 効果的にコミュニケーションする

### コードベースへの質問

> **ポイント**: シニアエンジニアに聞くような質問をClaudeにする。特別なプロンプトは不要。直接質問するだけでよい。

新しいコードベースへのオンボーディングにClaudeCodeを積極的に活用する。他のエンジニアに聞くような質問をそのまま投げかけられる:

- ログはどう動作している？
- 新しいAPIエンドポイントはどう作る？
- `foo.rs` の134行目の `async move { ... }` は何をしている？
- `CustomerOnboardingFlowImpl` はどんなエッジケースを処理している？
- 333行目でなぜ `bar()` でなく `foo()` を呼んでいる？

この使い方はオンボーディングを大幅に効率化し、他のエンジニアへの負荷も減らす。

### 大きな機能はClaudeにインタビューさせる

> **ポイント**: 大きな機能は先にClaudeにインタビューさせる。最小限のプロンプトで始め、`AskUserQuestion` ツールを使ったインタビューを依頼する。

```
[簡単な説明]を作りたい。AskUserQuestionツールを使って詳細にインタビューして。
技術実装・UI/UX・エッジケース・懸念事項・トレードオフについて聞いて。
明らかな質問は避け、私が考慮していない難しい部分を掘り下げて。
全部カバーできたら、完全な仕様をSPEC.mdに書いて。
```

仕様が完成したら、**新しいセッション**で実装を開始する。クリーンなコンテキストで実装に集中でき、仕様書も参照できる。

### コンテキストを汚さないサイドバー質問（`/btw`）

> **ポイント**: 「ついでに聞きたいこと」は `/btw` で投げる。回答はオーバーレイ表示で、**会話履歴に残らない**。

実装中に「この API の引数って何だっけ」「このコマンドの正しいオプション名は」のような細かな確認をしたくなった時、通常のターンで聞くと回答がそのままコンテキストに積まれる。`/btw` を使えば、回答は閉じれば消えるオーバーレイで返ってくるため、長セッションの後半でもコンテキストを節約できる。

**`/btw` の重要な制約**:

- **ツール不可**: ファイル読み込み・コマンド実行・検索ができない。**既存のコンテキスト内にある情報のみ** から回答する（ただし Claude が既に読んだファイル・既に下した判断はすべて参照可能）
- **単発回答**: フォローアップターンが存在しない。深掘りしたい時は通常プロンプトに切り替える
- **Claude 実行中も投げられる**: 長時間処理を中断せずに横から聞ける
- **`Space` / `Enter` / `Escape`** で回答オーバーレイを閉じる
- **subagent の inverse**: subagent は「ツールフル + 空のコンテキスト」、`/btw` は「ツールなし + フル会話可視」。**今のセッションで Claude が既に知っていることを聞く時に使う**。新たに調べさせたい時は subagent を使う

> **Tips（Opus 4.7）**: ポジティブ例優位（「こうしないで」より「こういう声で書いて」）、ユーザーターン削減（質問は batch）が特に効く。詳細は第 8 章「プロンプト戦略」を参照。

---

## 6. セッションを管理する

会話は永続的かつ可逆的。これを最大限に活用する。

### 早めに・頻繁に修正する

> **ポイント**: 軌道がずれたと気づいたらすぐに修正する。タイトなフィードバックループが最良の結果を生む。

| 操作 | 方法 | 効果 |
|------|------|------|
| 中断 | `Esc` | コンテキストを保持しながら停止・リダイレクト |
| 巻き戻し | `Esc + Esc` または `/rewind` | 以前の会話・コード状態に復元 |
| 元に戻す | `"Undo that"` と指示 | Claudeが変更を差し戻す |
| コンテキストリセット | `/clear` | 無関係なタスク間でコンテキスト全消去 |

**重要**: 同じ問題で2回以上修正を試みたら、コンテキストが失敗したアプローチで汚染されている。`/clear` してより具体的なプロンプトで新しいセッションを始める。学んだことを反映した新しいセッションは、長い修正セッションよりほぼ常に良い結果を出す。

### コンテキストを積極的に管理する

> **ポイント**: 無関係なタスクの間は `/clear` でコンテキストをリセットする。

- `/clear`: コンテキストウィンドウを完全リセット
- 自動コンパクション: 上限に近づくと自動的に重要情報（コードパターン・ファイル状態・主要決定）を保持して圧縮
- `/compact <指示>`: 手動でコンパクション。例: `/compact APIの変更点に集中して`
- `Esc + Esc` または `/rewind` → メッセージチェックポイントを選び **「Summarize from here」** を選択: その地点以降のメッセージのみを要約し、それ以前のコンテキストはそのまま残す
- CLAUDE.md に圧縮動作の指示を追加: `"コンパクト時は変更ファイルの完全なリストとテストコマンドを必ず保持して"`
- 一度きりの確認で会話履歴に残したくない質問は `/btw` を使う（第 5 章参照）

### 調査はサブエージェントに委任する

> **ポイント**: `"サブエージェントを使ってXを調査して"` と指示。独立したコンテキストで探索するので、メインの会話を実装のためにクリーンに保てる。

```
サブエージェントを使って、認証システムのトークンリフレッシュの仕組みと、
再利用できる既存のOAuthユーティリティがないかを調査して。
```

実装後の検証にも使える:
```
サブエージェントを使ってこのコードのエッジケースをレビューして。
```

### チェックポイントで巻き戻す

> **ポイント**: Claudeがアクションを取るたびにチェックポイントが作られる。会話・コード、またはその両方を以前の状態に復元できる。

`Esc + Esc` または `/rewind` でリワインドメニューを開く。会話のみ・コードのみ・両方の復元、または選択したメッセージからの要約が可能。リスクのある実装を試して失敗したら巻き戻して別のアプローチを試せる。**チェックポイントはセッションをまたいで永続**するため、ターミナルを閉じた後でも巻き戻せる。

> **注意**: チェックポイントはClaudeが行った変更のみを追跡する。外部プロセスの変更は対象外。gitの代替ではない。

### セッションを再開する

> **ポイント**: `claude --continue` で最後のセッションを再開、`--resume` で最近のセッションから選択。

```bash
claude --continue    # 直前の会話を再開
claude --resume      # 最近の会話から選択して再開
```

`/rename` でセッションに `"oauth-migration"` や `"debugging-memory-leak"` のような分かりやすい名前をつけて管理する。セッションをブランチのように扱う: 異なる作業ストリームに別々の永続コンテキストを持たせられる。

複数セッションをチームとして自動連携させたい場合は **Agent teams**（第 7 章「並列セッション」を参照）が利用できる。

---

## 7. 自動化・スケールアップ

1人・1Claude・1会話という前提を超えて、並列セッション・非インタラクティブモード・ファンアウトパターンでアウトプットを拡大する。

### 非インタラクティブモード（CI/スクリプト統合）

> **ポイント**: `claude -p "プロンプト"` でCI・pre-commitフック・スクリプトから実行。`--output-format stream-json` でストリーミングJSON出力。

```bash
# 1回限りのクエリ
claude -p "このプロジェクトの説明をして"

# スクリプト用の構造化出力
claude -p "APIエンドポイントを列挙して" --output-format json

# リアルタイム処理用ストリーミング
claude -p "このログファイルを分析して" --output-format stream-json

# 既存パイプラインへの統合
claude -p "<プロンプト>" --output-format json | your_command
```

開発時は `--verbose` でデバッグ、本番では無効化。

### 並列セッション

> **ポイント**: 並列でClaudeセッションを実行して開発を加速し、実験を分離し、複雑なワークフローを開始する。

並列セッションの 3 つの方法:

- **ClaudeCode デスクトップアプリ**: ローカルセッションを視覚的に管理。各セッションが独自の分離されたworktreeを持つ
- **Claude Code on the web**: Anthropicのセキュアなクラウドインフラ上で分離されたVMで実行
- **[Agent teams](https://code.claude.com/docs/en/agent-teams)（experimental）**: 共有タスク・メッセージング・チームリードを持つ複数セッションの自動連携。**`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`** で有効化（ClaudeCode v2.1.32 以上）。subagent との違い: subagent は結果のみメインに返すが、agent teams のメンバーは **共有タスクリストを持ち、互いに直接コミュニケーション** する。Writer / Reviewer / Tester のような役割分担を 1 つの「チーム」として走らせたい場合に有効

**Writer/Reviewerパターン**（新しいコンテキストはコードレビューの品質を向上させる）:

| Session A (Writer) | Session B (Reviewer) |
|--------------------|----------------------|
| `APIエンドポイントにレートリミッターを実装して` | |
| | `@src/middleware/rateLimiter.ts をレビューして。エッジケース・競合状態・既存ミドルウェアパターンとの一貫性を確認して` |
| `[Session Bのレビュー結果]。これらの問題に対処して` | |

テストとコードでも同様: 一方のClaudeがテストを書き、もう一方がそのテストを通すコードを書く。

### ファンアウトパターン（大規模マイグレーション）

> **ポイント**: `claude -p` を呼び出すループでタスクを分散。バッチ操作のパーミッションスコープには `--allowedTools` を使う。

```bash
for file in $(cat files.txt); do
  claude -p "$file をReactからVueに移行して。OKかFAILで返して" \
    --allowedTools "Edit,Bash(git commit *)"
done
```

最初の2〜3ファイルで検証してプロンプトを調整し、その後フルスケールで実行。`--allowedTools` で許可する操作を限定することが無人実行時には特に重要。

許可スコープの代替として **`--permission-mode auto`** を使うと、auto mode の分類器が各コマンドを審査するため、`--allowedTools` を逐一列挙せずに安全に走らせやすい:

```bash
claude --permission-mode auto -p "lint エラーを全部修正して"
```

`-p` フラグでの非インタラクティブ実行中に分類器が連続でブロックするとフォールバック先のユーザーがいないため、auto mode は abort する。バッチ実行前に手元で挙動を確認しておくこと。

> **注意: `ultracode` は `-p` から起動しない**（v2.1.210〜）。`ultracode` キーワードは**人間入力起点でのみ発火**する設計になり、`-p` / SDK の非 human 入力・scheduled task・webhook・PR コメントからは起動しない。CI で大規模 workflow を回そうとしても効かないため、バッチ側は上記のような素朴なループか、`--max-budget-usd` 付きの通常実行で組む。

#### Anthropic 自身の大規模移行手法（2026-07-16 公式）

上記の素朴なループより一段進んだ型として、Anthropic は自社の大規模移行（**Bun の Zig → Rust、100 万行を 2 週間未満・API コスト $165,000・merge 後の regression 19 件**）で用いた手法を公開した。数千ファイル規模を扱う場合はこちらを土台にする。

**中核原則**: 「**You fix the process (loop) that produced the code**」— 個別ファイルを直すのではなく、そのコードを生んだループを直す。

| パターン | 内容 |
|---|---|
| **Mechanical work queue** | 次に何をするかを**ディスク上のファイルの存在で決定**する。途中で落ちても再開可能（resumable）になる |
| **Adversarial review + arbitration** | 別エージェントが敵対的にレビューし、**判定が不一致なら arbitration へ escalate** する |
| **Build daemon** | **高価な compile を直列化し、安価な fix を並列化**する |
| **Model stratification** | **実装は小さいモデル、review と rule 作成は大きいモデル**に割り当てる（コスト最適化） |

流れは ①Rulebook + 依存マップ作成 → ②サンプルで mini-migration による stress test → ③並列 translation（不確実箇所には TODO マーカー）→ ④compile を orchestrated loop で回し fixer agent が解消 → ⑤smoke test → ⑥behavior matching。**評価は compiler / test suite / behavioral diff といった "built-in referee" に任せる**。詳細は [harness.md](harness.md) §4.9。

### 安全な自律モード（auto mode 推奨）

> **ポイント**: 中断なしで Claude を動作させたい時の **第一選択は auto mode**。`--dangerously-skip-permissions` は事実上の旧来オプション。

```bash
claude --permission-mode auto -p "fix all lint errors"
```

auto mode は別の分類器モデルがコマンドを審査し、スコープ逸脱・未知のインフラ操作・敵対的コンテンツ起因の動作のみブロックする。lint 修正・ボイラープレート生成・大規模マイグレーションのような信頼できるタスクで cycle time を短縮できる。

`--dangerously-skip-permissions` は全チェックをバイパスする旧来のフラグで、機能としては残存するが、**インターネット接続を切ったサンドボックス環境** などで限定的に使うべきオプションである。auto mode が利用できる環境では auto mode を優先する。

> **警告**: 任意コマンドの実行はデータ損失・システム破損・プロンプトインジェクション攻撃によるデータ流出のリスクがある。`/sandbox` を有効化するとチェックをバイパスする代わりに事前に境界を定義するため、`--dangerously-skip-permissions` 単体より高いセキュリティで自律性が得られる。auto mode と組み合わせるとさらに安全度が上がる。

---

## 8. Opus 4.7 を活用する

> 出典: [Best practices for using Claude Opus 4.7 with Claude Code](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code)（Anthropic 公式ブログ）/ [Opus 4.7 launch announcement](https://www.anthropic.com/news/claude-opus-4-7)

> **本章の位置づけ (2026-07-26 更新)**: 公式版 [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) は 2026-07-02 以降の更新で **Opus 4.7 専用章を削除し、一般化された原則へ再編**された。しかし本リポでは **Opus 4.7 → 4.8 → Fable 5 → Sonnet 5 → Opus 5 の世代進化を追える履歴保全ドキュメント**として本章を残す。以下に続く各節 (§8.1 概要 = Opus 4.7 時代の観察、§8.2 Opus 4.8 更新、§8.3 Fable 5 / Mythos 5 更新、§8.4 Sonnet 5 更新、**§8.5 Opus 5 更新**) は「その世代でどう挙動が変わったか」の差分ドキュメントとして機能する。
>
> **現行モデルで新規に運用を組む場合は、まず §8.5 (Opus 5 節) を読む**。Opus 5 は `opus` / `default` エイリアスの現在の解決先であり、**検証指示とサブエージェント委任について旧世代とは逆方向の調整を要求する**（旧世代向けの指示をそのまま持ち込むと逆効果になる）。そのうえで必要に応じて §8.2〜§8.4 を参照する。

本章は Anthropic 公式ブログを基に、Opus 4.7 を ClaudeCode で使う際のチューニングポイントをまとめる。モデルの世代交代でデフォルト動作が変わったため、4.6 までの感覚で使うと無駄なトークン消費や品質低下が起こりうる。新しい挙動を理解した上で、効果が大きい設定だけを取り込みたい。

### 概要

Opus 4.7 は **「コーディング・エンタープライズワークフロー・長時間エージェンティックタスク」向けに、リリース当時（2026-04）で最も強力な Opus 系列の一般提供モデル** である（その後 Opus 4.8・Fable 5 が後継としてリリース。本節は Opus 4.7 の特性として履歴的に残す）。Opus 4.6 と比較して以下が改善された:

- 曖昧性への対処が向上（少ない指示で意図を汲める）
- バグ発見・コードレビューが大幅に強化
- セッション横断のコンテキスト保持が信頼できる水準に
- 曖昧なタスクでも自力で推論を進められる

一方、トークン消費に影響する 2 つの変更がある:

1. **トークナイザーの更新**
2. **エフォートレベルが高いほど思考量が増える性質**（特に長セッションの後半ほど顕著）

そのため Opus 4.6 から差し替えた直後は、プロンプトとハーネスを少しチューニングするだけで体感が大きく変わる。本書の他章のテクニックと組み合わせると効果が出やすい。

長時間タスク適性: 「複数ファイルにまたがる複雑な変更」「曖昧なバグのデバッグ」「サービス全体のコードレビュー」「複数ステップのエージェンティック作業」のような **これまで人間の監視がボトルネックだった用途** に向く。BOSS のように複数プロジェクトを並行運用する状況では、長セッションでの自律性が直接アウトプット量に効く。

### Opus 4.8 への更新（2026-05-28 リリース）

> 出典: [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) / [Model configuration](https://code.claude.com/docs/en/model-config)

2026-05-28 に **Opus 4.8**（model id `claude-opus-4-8`、要 ClaudeCode **v2.1.154 以上**）がリリースされ、Opus 4.7 の後継となった。Anthropic API では `opus` エイリアスが Opus 4.8 に解決される。本節は Opus 4.7 の記述を**履歴として残したまま**、4.7 → 4.8 の差分を追記する（世代の進化を追えるようにするため）。

**4.7 → 4.8 の主な差分:**

| 観点 | Opus 4.7 | Opus 4.8 | 補足 |
|------|---------|---------|------|
| **デフォルト effort** | `xhigh` | **`high`** | 全 surface 共通。Opus 4.8 を初回起動した時、過去に別モデルで設定した effort があっても `high` が適用される。`/effort` で再調整可 |
| コード品質 | 基準 | **欠陥見逃しが約 1/4** | コードの欠陥を見逃す確率が 4.7 比で大幅低下 |
| ツール呼び出し | 「必要な呼び出しをスキップする」報告あり | **改善**。より少ないステップで完了 | 4.7 で控えめすぎた tool triggering が是正 |
| 長時間タスク | — | **compaction 回数減・回復改善**、long-context 改善 | 長セッションでスタイル方向性を保持 |
| judgment | — | 質問を返す・自分のミスを捕捉・不健全な計画に push back する傾向が強化 | |

> **tokenizer（2026-08-04 更新）**: Opus 4.8 **固有**の tokenizer 変更は公式に記述がなく、「4.8 で tokenizer がさらに変わった」とは断定しない。ただし公式 [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) が「**Claude Opus 4.7 introduced a new tokenizer, which later Opus models, including Claude Opus 5, also use**」と明記したため、**Opus 4.7 / 4.8 / Opus 5 は同一 tokenizer 世代**であることが確定した（4.7 以前のモデル比で 1x〜1.35x、最大 ~35% 増）。詳細は [model-comparison.md](model-comparison.md) §3.2 を参照。また、Opus 4.7 のような **専用ベストプラクティスブログ記事は 2026-05-30 時点で未確認**。Opus 4.8 のチューニング指針は [model-config](https://code.claude.com/docs/en/model-config) / [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) に分散して掲載されている。

**Dynamic Workflows / ultracode（Opus 4.8 の新機能、research preview）:**

`/effort` メニューに **`ultracode`** が追加された。これは effort レベルではなく **ClaudeCode の設定**で、モデルには `xhigh` を送りつつ、substantive なタスクに対して **dynamic workflows**（多数の並列 subagent をオーケストレーション）を起動する。数十万行規模の codebase migration を kickoff → merge まで自律実行する用途を想定（Enterprise / Team / Max 対象、session-only）。`--settings` で `"ultracode": true` でも起動できる。本章「サブエージェント delegation の指示」（4.7 では spawn 控えめ）と接続する新トピックである。

> **v2.1.210 / v2.1.219 での変更**: ① **`ultracode` キーワードは人間入力起点でのみ発火する**（`-p` / SDK の非 human 入力・scheduled task・webhook・PR コメントからは起動しない）② **dynamic workflows の既定が medium size guideline（agent 15 体未満を目標）に変更**され、「1 セッションで数百の並列 subagent」は既定挙動ではなくなった。大規模ファンアウトには `workflowSizeGuideline` を `unrestricted` にする（[harness.md](harness.md) §4.7 / [config-files.md](config-files.md) 参照）。

### Claude Fable 5 / Claude Mythos 5 への更新（2026-06-09 リリース）

> 出典: [Introducing Claude Fable 5 and Claude Mythos 5 (news)](https://www.anthropic.com/news/claude-fable-5-mythos-5) / [Introducing Claude Fable 5 and Claude Mythos 5 (platform docs)](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) / [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) / [Model configuration](https://code.claude.com/docs/en/model-config)

2026-06-09 に **Claude Fable 5**（model id `claude-fable-5`、要 ClaudeCode **v2.1.170 以上**）と **Claude Mythos 5**（model id `claude-mythos-5`）が同時リリースされた。両モデルは Anthropic が **Mythos-class** と呼ぶ次世代モデルで、**Opus 4.8 の直線的後継ではなく独立した系列**として位置づけられている（Fable 5 リリース時点では `opus` / `sonnet` / `haiku` エイリアスの解決先は**変更なし**で、Anthropic API では `opus`→Opus 4.8、`sonnet`→Sonnet 4.6 のままだった。**その後 2026-06-30 の Sonnet 5 リリースで `sonnet` は Sonnet 5 に更新された**。詳細は本章「Claude Sonnet 5 への更新」節を参照）。本節は Opus 4.7 / 4.8 の記述を**履歴として残したまま**、Fable 5 / Mythos 5 を追記する。

**Fable 5 と Mythos 5 の関係**:

- **同一の基盤モデル**である。違いは安全分類器（safeguards）の有無のみ
- **Fable 5**: 一般提供版（GA）。サイバーセキュリティ・生物/化学・蒸留クエリ等は安全分類器がフラグし、**自動的に別モデルへ fallback** される。**リリース当初は「一律で provider 既定の Opus」**（Anthropic API / gateway は Opus 4.8、Claude Platform on AWS は Opus 4.7）だったが、**v2.1.219 以降はフラグのカテゴリごとに fallback 先が分岐する**（§8.5「classifier fallback の変更」参照）
- **Mythos 5**: 一般提供なし。**Project Glasswing** 経由の招待制（防御的サイバーセキュリティの研究者・インフラ提供者など）。同能力で safeguards が一部解除される。セルフサインアップ不可

**Opus 4.8 → Fable 5 の主な差分:**

| 観点 | Opus 4.8 | Fable 5 | 補足 |
|------|---------|---------|------|
| 位置づけ | フラッグシップ Opus 系列 | **Mythos-class（独立系列）** | `opus` エイリアスの解決先は依然 Opus 4.8。明示選択（`/model fable` / `best`）で利用 |
| デフォルト effort | `high` | **`high`** | Opus 4.8 と同じ。新モデル初回起動時にデフォルトが自動適用される |
| 必須 ClaudeCode | v2.1.154 以上 | **v2.1.170 以上** | 旧版は model picker に Fable 5 を出さない。`claude update` で更新 |
| 料金（per MTok） | $5 / $25 | **$10 / $50** | Opus 4.8 の約 2 倍レート。Mythos 5 も同額（Mythos Preview の半額以下） |
| context window | 1M（API） | **1M（常時）** | Fable 5 は API で常に 1M window |
| max output | — | **128k tokens**（Batch API は 300k beta header あり） | |
| 安全分類器 | — | **あり**（Fable 5 のみ。Mythos 5 は同能力で解除） | フラグ時は自動 fallback。**v2.1.219 以降はカテゴリ別**（biology → Opus 5 / cybersecurity → Opus 4.8）。それ以前は一律 provider 既定 Opus |
| ベンチマーク | — | **「state-of-the-art on nearly all tested benchmarks」**、software engineering / vision / scientific research で卓越 | Stripe の 5000 万行 Ruby migration、Hebbia Finance Benchmark の最高スコア等が公式言及 |
| 長時間自律タスク | 改善 | **「any previous Claude models より長く自律動作可能」** | Mythos-class の中核能力 |
| データ保持 | — | **30 日保持・ZDR 非対応**（Covered Models） | Mythos 5 も同じ |
| tokenizer | Opus 4.7 と同じ | **Opus 4.7 と同じ**（4.7 より前のモデル比で同テキストが約 30% 多くトークン化） | 単純な乗算でコスト試算する際は注意 |

**effort と thinking（Fable 5）**:

- **effort レベル**: `low / medium / high / xhigh / max`（Opus 4.8 / 4.7 と同じ）。デフォルト `high`
- **Extended thinking: No / Adaptive thinking: Yes**（always on）。Fable 5 では **thinking を OFF にできない**: `MAX_THINKING_TOKENS=0` / `alwaysThinkingEnabled` / セッショントグル / `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` のいずれも Fable 5 には無効
- `ultrathink` キーワード・`ultracode` 設定は従来通り（モデル横断、Fable 5 固有の変更なし）

**model alias のプロバイダ別解決（重要）**:

`opus` / `sonnet` の解決先は **プロバイダによって異なる**。本表は **2026-08-04 に公式 [Model configuration](https://code.claude.com/docs/en/model-config) を再取得して更新した現行版**である（本書の他箇所に残る「`opus`→Opus 4.8」等の記述は、その世代の当時の状態を述べた履歴記述であり、現行の解決先は本表を優先する）。

**現行（v2.1.219 以降）**:

| プロバイダ | `opus` | `sonnet` |
|---|---|---|
| Anthropic API | **Opus 5** | Sonnet 5 |
| Claude Platform on AWS | **Opus 5** | Sonnet 4.6 |
| Amazon Bedrock / **Google Cloud's Agent Platform** | **Opus 5** | Sonnet 4.5 |
| **Microsoft Foundry** | **Opus 4.6** | Sonnet 4.5 |

`default`（アカウント種別で分岐）:

| アカウント種別 / プロバイダ | `default` の解決先 |
|---|---|
| Max / Team Premium / Enterprise PAYG / Anthropic API | **Opus 5** |
| Claude Platform on AWS / Amazon Bedrock / Google Cloud's Agent Platform | **Opus 5** |
| Pro / Team Standard / Enterprise seat | **Sonnet 5** |
| **Microsoft Foundry** | **Sonnet 4.5** |

> **上表が適用されない 2 つの例外**: ① 管理者が **organization default model** を設定している場合、`default` は上表のアカウント種別既定ではなく**その組織既定に解決される**（要 v2.1.196+）② managed settings が Default モデルの allowlist 強制を有効にしており、アカウント種別既定が `availableModels` に含まれない場合、`default` は**強制された Default に解決される**。両方が効く場合は「組織既定でアカウント種別既定を置換 → その結果に allowlist 強制を適用」の順で処理される。
>
> なお **Fable 5 はどのアカウント種別でも既定モデルにならない**（`/model fable` / `model` 設定 / `best` エイリアスで明示選択した場合のみ使われる）。また公式が言う **Enterprise PAYG** は「subscription seat 課金ではなく従量課金の Enterprise 組織」を指す。

> **表を読む際の 3 つの注意**:
> 1. **Microsoft Foundry だけが Opus 5 に上がっていない**（`opus` は Opus 4.6 のまま）。公式は Bedrock / Google Cloud と Foundry を**別行**で扱っており、「Bedrock / Vertex / Foundry」とまとめると誤りになる。
> 2. 公式の呼称は **Google Cloud's Agent Platform**（Vertex ではない）。
> 3. **エイリアスが古いモデルに解決されるプロバイダで最新モデルを使う**には、フル model name を明示するか `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` を設定する。

**履歴（世代の変遷を追うため保全）**:

| 期間 | Anthropic API の `opus` | Claude Platform on AWS | Bedrock / Google Cloud |
|---|---|---|---|
| v2.1.219 〜（現行） | **Opus 5** | **Opus 5** | **Opus 5** |
| v2.1.207 〜 v2.1.218 | Opus 4.8 | Opus 4.8 | Opus 4.8 |
| v2.1.154 〜 v2.1.206 | Opus 4.8 | Opus 4.7 | Opus 4.6 |

- `best` エイリアスは「組織にアクセスがあれば Fable 5、無ければ最新 Opus」。
- **Fable 5 の安全分類器 fallback 先もプロバイダ依存**（**v2.1.219 未満**）: Anthropic API / LLM gateway は **Opus 4.8**、Claude Platform on AWS は **Opus 4.7**。Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry では `ANTHROPIC_DEFAULT_FABLE_MODEL` と `ANTHROPIC_DEFAULT_OPUS_MODEL` の両方を設定しないと自動 fallback が働かない。**v2.1.219 以降はプロバイダ依存ではなくカテゴリ別の分岐に変わった**（§8.5「classifier fallback の変更」参照）。
- Bedrock / Google Cloud's Agent Platform / Microsoft Foundry で新しいモデルを使うには full model name か `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` 等で明示指定する。
- 出典: [Model configuration](https://code.claude.com/docs/en/model-config)（**2026-08-04 再確認**）

**プラン同梱とコスト**（2026-06-12 停止・06-30 再開の経緯を含む時系列で管理する）:

| 日付 | 事象 |
|---|---|
| 2026-06-09 | Fable 5 / Mythos 5 GA。当初アナウンスでは Pro / Max / Team / seat-based Enterprise に **06-22 まで** 追加費用なしで含まれる予定 |
| **2026-06-12** | 米国 export controls の発令により、Anthropic が **Fable 5 のグローバル提供を全面停止**（全ユーザー影響） |
| 2026-06-22 | 当初の同梱終了予定日。ただし 06-12 の停止措置が継続中で、同梱終了は事実上凍結 |
| **2026-06-30** | export controls 解除 + Amazon researchers 発見の jailbreak 対策 safety classifier 導入（該当技術を 99% 以上ブロック）で **redeploy 発表**。翌日から新プロモを開始 |
| **2026-07-01 00:00 PT 〜 07-19 23:59:59 PT** | **Fable 5 プロモーショナルアクセス**（復帰記念、**当初 07-07 終了 → 07-12 → 最終的に 07-19 まで 2 回延長**）: Pro / Max / Team / seat-based Enterprise の Premium seat で weekly usage limit の **最大 50%** まで Fable 5 使用可（追加課金なし）。Claude Code は **v2.1.170 以上**必須。API 経由は対象外（常に標準レート課金） |
| **2026-07-19 23:59:59 PT 以降（確定）** | **プロモ終了。以降の扱いはプラン別に分岐する**（当初想定の「全プラン一律で usage credits 必須」ではなくなった）: **Max / Team premium seat は 50% 枠が標準機能として継続（追加費用なし）**、**Pro / Team standard seat は weekly limit の対象外となり usage credits が必要**（対象 seat には one-time credit が付与される） |

- **BOSS 環境への影響**: Max プランであればプロモ終了後も 50% 枠が無償で継続するため、実務上の変化はない。Pro / Team standard seat を併用している場合のみ usage credits の有効化を検討する
- Fable 5 の 50% 上限は「独立割当」ではなく **weekly limit 全体の残りに対する天井**。他モデルで既に消費した分は Fable 5 側の上限にも影響する（詳細は `docs/model-comparison.md` §4.3 参照）
- 出典: [Redeploying Fable 5 and Mythos 5](https://www.anthropic.com/news/redeploying-fable-5) / [Claude Fable 5 promotional access](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access) / [usage credits の管理](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)（**2026-07-26 確認**）

**Fable 5 を選ぶ判断基準**:

| 状況 | 推奨 |
|------|------|
| 長時間の自律エージェンティックタスク（数時間〜の subagent オーケストレーション、大規模 migration） | **Fable 5**（Mythos-class の中核能力） |
| 大規模 monorepo を 1 セッションで把握させたい（1M context が必須） | **Fable 5** |
| 通常のコーディング・コードレビュー・小規模 PR | **Opus 4.8 で十分**（Fable 5 は約 2 倍コスト） |
| サイバーセキュリティ関連の専門ワークロード | Fable 5 / Opus 5 いずれも Opus 4.8 に fallback されるため、**Opus 4.8 を直接指定**するか、適格者は Mythos 5 |
| 生物 / 化学関連の専門ワークロード | Fable 5 は Opus 5 に fallback される。**Opus 5 自体は fallback されず refusal で終了する**ため、Opus 5 を選ばない。適格者は Mythos 5（§8.5 参照） |
| ZDR（zero data retention）下で運用 | **Fable 5 は非提供**。Opus 4.8 等を使う |

**fast mode 対応**: 公式の news / model-config / models overview いずれにも Fable 5 の fast mode 言及は**ない**（記載なし）。fast mode の対象は引き続き Opus 4.8（[Fast mode](https://code.claude.com/docs/en/fast-mode)）。

**auto mode 対応モデル**: [permission-modes](https://code.claude.com/docs/en/permission-modes) は本書執筆時点（2026-07-11）で Fable 5 / Mythos 5 を auto mode 対応モデルとして**明示列挙していない**。Fable 5 で auto mode を運用する場合は事前に短いセッションで挙動を確認すること。**Sonnet 5 は 2026-06-30 GA と同時に auto mode 対応が明示列挙された**（Anthropic API 標準対応、Bedrock/Vertex/Foundry では **v2.1.207 で opt-in が不要**になり標準有効）。

**新環境変数**:

| 変数 | 役割 |
|------|------|
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | Fable 5 のデフォルト model id を上書き |
| `DISABLE_PROMPT_CACHING_FABLE` | Fable 5 のプロンプトキャッシュを無効化 |

**Fable 5 の安全分類器を切り分ける**:

セッション開始直後から想定外に Opus 4.8 で応答していると感じた場合、CLAUDE.md や git status のみで安全分類器がフラグしている可能性がある。`claude --safe-mode` でカスタマイズを無効化して起動し、fallback の挙動を切り分けられる。

**Fable 5 のプロンプト / ハーネス調整（公式プロンプトガイド準拠）**:

Fable 5 は Opus 4.8 から挙動が変わっており、旧モデル向けのプロンプト・skill・ハーネスはそのままだと過剰指示になりやすい。移行時は以下を見直す。

- **effort は `high` 既定で、`low` / `medium` も実用的**: Fable 5 の低 effort は旧モデルの `xhigh` を上回ることがある。タスクが完了するのに時間がかかりすぎる時や、対話的に回したい時は effort を下げる。
- **長ターン化が最大の変化**: 1 リクエストが数分〜、自律実行は数時間に及ぶ。**クライアント timeout / streaming / 進捗表示の調整と、ハーネスの「非同期チェック化」（ブロックせず scheduled job 等で確認）を移行前に**行う。
- **指示追従が強化**: 各挙動を列挙せず短い指示で制御できる。冗長性・不要な refactor / tidy・checkpoint 挙動は 1〜2 文の指示で足りる（例: 「成果を先頭に。簡潔さより読みやすさ」「破壊的・不可逆・スコープ変更・ユーザーにしか出せない入力の時だけ止まれ」）。
- **進捗の幻覚対策**: 「報告前に各主張をこのセッションの tool result と突合せよ。検証できた作業だけ報告し、未検証は明示せよ」を入れると、長時間自律実行での fabricated status がほぼ消える。
- **境界の明示**: 「問題の説明・質問・思考中の発話には assessment を返して止まる。修正は依頼があるまで適用しない」を明示すると、頼んでいない変更（勝手なメール下書き・防御的 git ブランチ作成等）を抑制できる。
- **並列 subagent を積極ディスパッチ**: Fable 5 は subagent 起動が得意。orchestrator ↔ subagent は **非同期通信を推奨**（各 subagent の完了をブロックして待たない）。long-lived subagent は cache 活用で時間・コストを節約。
- **メモリシステムの構築**: 「1 ファイル 1 lesson、先頭に 1 行サマリ」の Markdown ノートを与えると、過去の学びを参照して品質が上がる。
- **`reasoning_extraction` の落とし穴**: 「内部推論を応答に再現／転記／説明せよ」系の指示は Fable 5 で **refusal を誘発し Opus 4.8 への fallback が増える**。show-your-thinking 系の skill / system prompt は移行時に監査する。推論可視化が必要なら adaptive thinking の構造化 `thinking` ブロックを読む。
- **send-to-user tool パターン**: 長時間非同期エージェントで、ユーザーに verbatim で届けたい内容（成果物・進捗の具体数値・途中質問への直接回答）は client-side tool で渡す（tool input は要約されない仕様を利用）。
- 出典: [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)（2026-06-18 確認）

**Fable 5 プロンプトの実務フレーム — Finding Your Unknowns (2026-07-06 公式ブログ)**:

Anthropic は 2026-07-06 に [A field guide to Claude Fable 5: Finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns) を公開し、Fable 5 で unknowns (不明点) を扱う 4 象限フレームと実務ワークフローを示した。Fable 5 は「unknowns の clarify 能力がボトルネックになる初のモデル」と位置づけられている。

- **4 象限**:
  - **Known knowns**: 既知の既知 (仕様通り実装)
  - **Known unknowns**: 既知の不明 (質問して埋める)
  - **Unknown knowns**: 気づいていない既知 (blind spot として認識させる)
  - **Unknown unknowns**: 気づいていない不明 (探索的に炙り出す)
- **Pre-implementation フェーズ**:
  - **Blind Spot Pass**: 仕様に対する見落としを Fable 5 に列挙させる
  - **Brainstorms**: 実装案の複数バリエーションを出させる
  - **Interviews (one question at a time)**: 一度に 1 問ずつ質問させる (`AskUserQuestion` を使わず対話ベースで進める)
  - **References**: source code を優先的に読ませる (公式 docs より実コードから真実を得る)
  - **Implementation Plans**: 実装前に詳細なプランを書かせる
- **Implementation 中**:
  - **Implementation Notes**: 一時的な md ファイルに deviation (計画からの逸脱) を記録させる。長時間タスクの途中経過を BOSS が追える
- **Post-implementation**:
  - **Pitches**: 変更内容を売り込み形式でまとめる
  - **Explainers**: 変更内容を初見の人向けに説明する
  - **Quizzes**: HTML レポート + comprehension quiz (理解度チェック) を生成させる

出典: [A field guide to Claude Fable 5: Finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns) (2026-07-06)

**Fable 5 classifier fallback の課金ルール (2026-07-11 公式 cookbook 化)**:

Fable 5 の安全分類器がタスクをフラグして別モデルに fallback する挙動については、公式 cookbook [Classifier fallback and billing for Claude Fable 5](https://platform.claude.com/cookbook/fable-5-fallback-billing-guide) が詳細を明文化した。ハーネス側の実装コスト設計に必要な情報が揃った。**課金ルール自体は fallback 先のモデルが変わっても同じ**である（v2.1.219 で fallback 先がカテゴリ別に分岐したが、下記の課金ロジックは維持される。§8.5 参照）。

- **Classifier ブロック時 (`stop_reason: "refusal"`)**: **input tokens は課金されない** (無償)
- **fallback 先での input tokens 課金**: **cache-read 相当の 10% レート**で課金 (通常の cache-write $1.25-2x ではない。fallback のコスト負担が大幅軽減)。cookbook 執筆時点の記述は「Fable 5 → Opus 4.8」だが、**v2.1.219 以降は biology フラグ時の fallback 先が Opus 5 になる**（課金レートの扱いは同じ）
- **`server-side-fallback-2026-06-01` beta header**: SDK 側の fallback 実装コストが激減 (Anthropic 側で自動 fallback + 課金調整)
- **`fallback-credit-2026-06-01` beta header**: client-side fallback を実装する場合でも、上記課金ルールが適用される (自前で refusal 検知 → Opus 4.8 リトライしても割高にならない)

出典: [Classifier fallback and billing for Claude Fable 5](https://platform.claude.com/cookbook/fable-5-fallback-billing-guide) (2026-07-11 確認)

### Claude Sonnet 5 への更新（2026-06-30 リリース）

> 出典: [Introducing Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5) / [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) / [Model configuration](https://code.claude.com/docs/en/model-config)

2026-06-30 に **Claude Sonnet 5**（model id `claude-sonnet-5`、要 ClaudeCode **v2.1.197 以上**）がリリースされ、Sonnet 4.6 の後継として Anthropic API の `sonnet` エイリアスに割り当てられた。Anthropic は Sonnet 5 を「最も agentic な Sonnet」と位置づけ、reasoning / tool use / coding / knowledge work で Sonnet 4.6 から大幅な向上を実現している。本節は Sonnet 4.6 の記述を **履歴として残したまま**、Sonnet 5 の差分を追記する。

**Sonnet 4.6 → Sonnet 5 の主な差分**:

| 観点 | Sonnet 4.6 | Sonnet 5 | 補足 |
|---|---|---|---|
| デフォルト effort | `high` | **`high`** | ただし Sonnet 5 は **Claude API と Claude Code のみ**（Opus 4.8 のような全 surface ではない）。claude.ai は既定 effort が別途設定される |
| effort レベル | `low/medium/high/max`（`xhigh` は `high` にフォールバック） | **`low/medium/high/xhigh/max`**（Fable 5 / Opus 4.8 と同じ 5 段） | `xhigh` を素で使えるようになった |
| Extended thinking | Yes | **No** | 固定 budget 非対応。adaptive-only モデルとして再設計 |
| Adaptive thinking | Yes | **Yes（always on）** | Fable 5 と同じく **thinking を OFF にできない**: `MAX_THINKING_TOKENS=0` / `alwaysThinkingEnabled` / `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` は Sonnet 5 に不適用 |
| Context window | 1M（usage credits 要） | **1M 常時**（Anthropic API、`[1m]` suffix / usage credits 不要、auto-compact 閾値 ~967K は `CLAUDE_CODE_AUTO_COMPACT_WINDOW` で調整可） | Sonnet 5 のフラッグシップ機能 |
| Max output（Messages API） | 128K | 128K | Batch API では `output-300k-2026-03-24` header で 300K |
| 料金（per MTok） | $3 / $15 | **$2 / $10（Introductory、2026-08-31 まで）→ 以降 $3 / $15** | 導入価格は Sonnet 4.6 より 33% 安 |
| 必須 ClaudeCode | v2.1.83 以上（auto mode 前提） | **v2.1.197 以上** | 旧版は model picker に Sonnet 5 を出さない |
| auto mode | 対応 | **対応**（明示列挙） | Bedrock/Vertex/Foundry では **v2.1.207 で opt-in 不要**（旧: `CLAUDE_CODE_ENABLE_AUTO_MODE=1` 必須） |
| `sonnet` エイリアスの解決先 | 該当（Anthropic API） | **Sonnet 5**（Anthropic API） / Sonnet 4.6（Claude Platform on AWS） / Sonnet 4.5（Bedrock/Vertex/Foundry） | プロバイダ別解決表を参照 |
| fast mode | 未対応 | **明示なし**（公式 news / model-config / models overview / Fast mode ページで Sonnet 5 の fast mode 言及なし） | fast mode の主対象は Opus 4.8 のまま |

**default エイリアスの tier 別変更**:

Sonnet 5 GA と同時に **Pro / Team Standard / Enterprise seat の default が Sonnet 5 に変更**された（Max / Team Premium / Enterprise PAYG / Anthropic API は当時 Opus 4.8 のまま。**v2.1.219 以降はこれらが Opus 5 に更新**されている）。BOSS が Max プランなら日常挙動に影響はないが、他プランと共用しているアカウントで default の差分が出る点に注意。

**Sonnet 5 を選ぶ判断基準**:

| 状況 | 推奨 |
|---|---|
| 通常のコーディング / コードレビュー / 小規模 PR | **Sonnet 5**（Introductory 価格の 2026-08-31 まで特に有利） |
| 高速レスポンスが必要なドラフト・スニペット拡張 | Sonnet 5（Fast latency + adaptive thinking の組み合わせで軽快） |
| 1M context を通常価格で使いたい | **Sonnet 5**（Anthropic API は常時 1M、追加課金不要） |
| 複雑 agentic / long-running タスク | Opus 4.8 or Fable 5（Sonnet 5 は Adaptive のみで固定 budget 思考が組めない） |
| Extended thinking を活用したデバッグ | Opus 4.7（`xhigh` + extended thinking）または Haiku 4.5 |

**Sonnet 5 のプロンプト調整（既存 docs との差分）**:

- 旧世代 Sonnet 用のプロンプトはそのまま動く。Adaptive thinking always on になった影響で、簡単なタスクでも一定の思考トークンが出る点だけ意識する（コストへの影響は Introductory 価格中は限定的）。
- 「Extended thinking を on / off」する既存の skill / setting は Sonnet 5 では機能しない。同機能を必要とするワークフローは Opus 4.7 / Haiku 4.5 に切り替える。
- Sonnet 5 専用プロンプトガイド（`prompting-claude-sonnet-5` 相当）は 2026-07-02 時点で platform docs 上に確認できていない。追加されたら追記する。

### Claude Opus 5 への更新（2026-07-24 リリース）

**`claude-opus-5` が GA し、`opus` / `default` エイリアスの解決先になった**（要 **ClaudeCode v2.1.219 以上**）。本節は**置き換えではなく追記**であり、上記の Opus 4.7 / 4.8 / Fable 5 / Sonnet 5 の記述は履歴として保全する。

**基本スペック**（詳細は [model-comparison.md](model-comparison.md)）:

| 項目 | 内容 |
|---|---|
| モデル ID | `claude-opus-5`（Bedrock `anthropic.claude-opus-5` / Google Cloud `claude-opus-5`） |
| 料金 | **$5 / $25 per MTok（Opus 4.8 と同額）**。fast mode は $10 / $50（Claude API のみ） |
| Context | **1M が既定かつ最大**（小さい variant なし）。max output 128k |
| Reliable knowledge cutoff | **May 2026**（Opus 4.8 は Jan 2026） |
| effort | 既定 **`high`**、`low`〜`max` の 5 段。**model-default hold なし**（旧設定を引き継ぐ） |
| thinking | **既定 ON**（破壊的変更）。`xhigh` / `max` では無効化不可（400 エラー） |

**能力変化（Opus 4.8 比、公式表現）**:

- **agentic coding / long-horizon が最大の伸び**。stub や placeholder を残さず multi-file feature や大規模 refactor を完遂する。公式は「**完全なタスク仕様を初手で渡して放置するのが最良**」と明記
- **test-time compute scaling の効率が歴代 Opus で最良**（effort を性能に変換する効率が高い）。`max` が最上段
- **`low` / `medium` の効率が良い**。少ないトークン・低レイテンシで高品質を出す
- **code review / bug-finding が強化**。1 パスあたりの実バグ検出率が高く false positive が少ない。**低 effort でも精度が落ちにくい**
- **multi-agent coordination** が機能する（writer-verifier パターンでエージェント同士の上書き事故が少ない）
- vision（chart / diagram 理解・UI 再現）と 1M 全域の instruction following が安定
- ベンチマーク: Frontier-Bench v0.1 で Opus 4.8 の 2 倍超、ARC-AGI 3 で次点の 3 倍、OSWorld 2.0 で Fable 5 を 1/3 のコストで上回る、CursorBench 3.2 で Fable 5 と 0.5% 差。**ただし cybersecurity exploitation では Mythos 5 に劣る**

#### classifier fallback の変更（カテゴリ別分岐へ）

**v2.1.219 で安全分類器の fallback 先が「一律 provider 既定 Opus」から「フラグのカテゴリ別」に変わった**。本節が fallback マトリクスの参照元であり、§8.3（Fable 5 節）の記述もこの表に従う。

| 元のモデル | フラグのカテゴリ | fallback 先 |
|---|---|---|
| **Fable 5** | biology | **Opus 5** で再実行 |
| **Fable 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | cybersecurity | **Opus 4.8** で再実行 |
| **Opus 5** | biology | **fallback なし。refusal で確定終了** |

- **v2.1.219 未満**は「フラグされた Fable 5 リクエストを一律で provider 既定の Opus に再実行」する挙動で、**Opus 5 は fallback 先ではなかった**。
- ⚠️ **実務上の注意**: Opus 5 は自身が biology classifier を持つため、**生物・化学系のワークロードでは fallback による救済がなく作業が停止する**。該当領域では最初から Opus 4.8（または適格者は Mythos 5）を明示指定する。
- 課金ルール（refusal 時の input 非課金 / fallback 先の cache-read 10% レート）は fallback 先が変わっても同じ（§8.3 の課金ルール参照）。
- 出典: [Model configuration](https://code.claude.com/docs/en/model-config) / CHANGELOG v2.1.219

#### プロンプト作法の変更（旧世代の指示を「削る」）

Opus 5 で最も重要な変化は、**旧世代向けに書いたプロンプトの一部が有害になる**点である。公式 [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) が明示的に「削除せよ」と指示している項目を挙げる。

| 削除すべき指示 | 理由 |
|---|---|
| 「最後に verification step を入れる」「subagent で verify させる」 | **Opus 5 は指示なしで自己検証する**ため over-verification になる。公式は「**legacy harness scaffolding が追加する別 verification step**」も名指しで対象にしている |
| 「double-check your answer」「re-verify before responding」 | 同上。思考の積み増しにしかならない |

一方、**新しく追加すべき指示**もある。

| 追加すべき指示 | 理由 |
|---|---|
| **委任の抑制** | Opus 5 は subagent 委任が過剰になりがち。公式推奨文言は「大規模かつ真に独立・並列化可能な作業のみ委任。数回の tool call で終わる作業は委任しない。**自分の作業の verify / double-check に subagent を使わない**。1 体で足りるなら 1 体」。決定論的な spawn 上限（[sub-agents.md](sub-agents.md) の 3 種の cap）と併用する |
| **応答の長さ指定** | 既定の応答が長くなった。**effort を下げても可視応答は短くならない**ため、長さは明示プロンプトで制御する |
| **成果物の冗長性抑制** | ディスクに書くドキュメント・コードも長くなる。「filler / redundant summary / boilerplate で埋めない」旨を指示する |
| **narration の cadence 指定** | agentic セッション中の進捗報告が増える。報告頻度を明示指定して調整する |
| **スコープの固定** | 勝手にスコープを広げる傾向がある。狭いタスクには「Deliver what was asked, at the scope intended.」型の制約を置く |

> **thinking を切る場合の既知アーティファクト**: thinking 無効時、tool call が構造化された `tool_use` ではなくテキストとして漏れる / `<thinking>` 等の内部 XML タグが可視出力に混入する事象が公式に報告されている。**回避策は thinking を有効に保ったまま effort を下げること**で、公式は「thinking ON + `low` effort は thinking OFF と同コストでより高性能」と明言している。

#### ClaudeCode 側の逆方向の変化（併せて読む）

上記は「**Claude への verify 指示を削る**」話だが、ClaudeCode 本体は逆に「**検証は自分で組まないと走らない**」方向に変わった。

- **v2.1.215**: Claude は `/verify` と `/code-review` を**自発起動しない**
- **v2.1.218**: `/deep-research` も**手動起動のみ**。`/code-review` は background subagent として実行

したがって整理は次の 2 軸になる。

| 層 | 方針 |
|---|---|
| **プロンプト（モデルへの指示）** | verify の念押しを**削る**（over-verification 回避） |
| **ハーネス（構造）** | 検証ステップを**明示的にチェーン / 埋め込みで組む**（自動では走らない） |

verification loop の 4 配置モデル（Standalone / Embedded / Chained / PR-wide）は [harness.md](harness.md) §4.8 を参照。

#### auto mode との関係

auto mode 対応モデルは公式に「Opus 4.6 以降 / Sonnet 4.6 以降」と定義されており、**Opus 5 についての明示的な記載は 2026-07-26 時点で確認できていない**（未確認）。世代条件から対応していると推測されるが、断定はしない。なお auto mode の**分類器モデルは v2.1.210 以降 Sonnet 5 が既定**である（[config-files.md](config-files.md) 参照）。

### effort 設定の選び方

公式の定義は「**effort をサポートする全モデルで既定は `high`、例外は Opus 4.7 のみ `xhigh`**」である。したがって **Opus 5 / Fable 5 / Opus 4.8 / Sonnet 5 / Opus 4.6 / Sonnet 4.6 = `high`、Opus 4.7 = `xhigh`**（auto mode の利用可否とは独立）。effort レベル一覧もモデルに依存する: **Opus 5 / Fable 5 / Opus 4.8 / 4.7 / Sonnet 5 は `low/medium/high/xhigh/max`**、Opus 4.6 / Sonnet 4.6 は `low/medium/high/max`（`xhigh` は Opus 4.6 / Sonnet 4.6 では `high` にフォールバック）。**Sonnet 5 のデフォルト `high` は Claude API と Claude Code のみで適用**され、Opus 4.8 のような全 surface 適用ではない点に注意。

**⚠️ Opus 5 は「初回起動時にモデル既定を適用する」挙動（model-default hold）を持たない**。Fable 5 / Opus 4.8 / Opus 4.7 は初回起動時にモデル既定の effort を強制適用して保持するが、**Opus 5 は以前設定したレベルをそのまま引き継ぐ**。旧世代で `xhigh` を選んでいた場合、Opus 5 に切り替えても黙って `xhigh` のまま動くため、`/effort` で明示的に確認・再設定する。

**Opus 5 では effort の推奨が反転した**（Opus 4.7 / 4.8 世代の「`xhigh` から始める」とは逆）。

| モデル | 公式の出発点 |
|---|---|
| Opus 4.7 / 4.8 | **`xhigh` から始める**（coding / agentic） |
| **Opus 5** | **`high`（既定）から始める。`low` / `medium` をコスト・レイテンシの主制御として積極的に使う。demanding な coding / agentic で `xhigh`、正当化できる場合のみ `max`** |

公式は「**旧モデルから effort 設定を引き継いだ場合は、自分の eval で effort sweep をやり直せ**」と明記している。また `xhigh` / `max` を使う場合は `max_tokens` を大きく取る（**64k 起点**を推奨）。Opus 5 は thinking が既定 ON で `max_tokens` が「thinking + response」の合計上限になるため、旧世代の値を流用すると出力が切れる。

| effort | 推奨用途 | 補足 |
|--------|---------|------|
| `low` / `medium` | コスト・レイテンシ重視。スコープが狭く決定的なタスク | 同じ effort なら旧世代より高性能で、トークン消費が減ることもある |
| **`high`（Opus 5 / Fable 5 / Opus 4.8 / 4.6・Sonnet 5 / 4.6 のデフォルト）** | ほとんどのコーディング・エージェンティック用途 | トークン消費と知性のバランス点。**Opus 5 では公式の推奨出発点**でもある |
| **`xhigh`（Opus 4.7 のデフォルト）** | より深い推論が欲しい時 | 推論とレイテンシのトレードオフを制御しやすい。**Opus 5 / Fable 5 / Opus 4.8 では既定ではない**（Opus 5 では「demanding な coding / agentic タスク」に限って選ぶ） |
| `max` | 真に難しい問題への限定使用、評価ベンチマーク | diminishing returns（収穫逓減）の領域。overthinking しやすいため、`high`/`xhigh` で十分でないと判断できた時のみ使う。session-only |
| `ultracode` | 数十万行規模の migration 等、dynamic workflows を回したい時 | ClaudeCode 設定（`xhigh` + dynamic workflows）。session-only、research preview |

> **Tips**: 同一タスク内で effort をトグルできる。仕様検討は `xhigh`、ボイラープレート生成は `medium` のように **ステップごとに切り替える** のが効果的。新モデルへ移行する時は古い effort 設定をそのまま継承せず、そのモデルのデフォルト（**Opus 5** / Fable 5 / Opus 4.8 なら `high`、Opus 4.7 なら `xhigh`）を起点に再調整する。**Opus 5 は旧設定を自動で上書きしてくれない**ため、この再調整は手動で行う必要がある。

**モデル選択と effort レベルの公式ガイダンス (2026-07-07 公式ブログ)**:

Anthropic の [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) (2026-07-07) が、モデル選択と effort 選択の実務的な判別軸を明文化した。BOSS の運用に直接使える指標として要点を追記する。

- **モデル選択**: **Sonnet = routine な作業** (ボイラープレート、既定通りの実装)、**Opus / Fable = 複雑な・曖昧なタスク** (仕様が確定していない、複数ファイル横断のロジック、非自明な設計判断が必要)
- **格上げの判別軸**:
  - **モデル格上げ (Sonnet → Opus → Fable)**: Claude が full context を持っていて (ファイルを全部読ませても) それでも失敗した場合。「情報不足」ではなく「思考深度不足」が原因のとき
  - **effort 格上げ (`medium` → `high` → `xhigh` → `max`)**: file skip / test 未実行 / refactor 途中放棄など「やるべきことを飛ばす」パターンが出たとき。effort は **「思考時間」ではなく「読むファイル数・検証量・multi-step の推し込み度合い」を制御する**概念
- **コスト影響**: higher effort で **~7x token 増**することもある (公式実測値)。「デフォルト effort を task-by-task ではなく general preference で調整する」姿勢が推奨される (毎回タスクごとに切り替えるのではなく、自分の運用パターンに合った既定を選ぶ)
- 出典: [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) (2026-07-07)

### プロンプト戦略

Opus 4.7 は「ペアプログラマー」より **「能力ある同僚エンジニアへの委任」** として扱った方が結果が良くなる。インタラクティブセッションではユーザーターンのたびに推論が走り、追加トークンを使うため、最初の 1 ターンで十分な情報を渡し切るのが鉄則。

- **第 1 ターンに完全な仕様を提示する**: intent / 制約 / 受け入れ基準 / 関連ファイルの位置 を全部まとめて渡す。曖昧なプロンプトを多ターンに小分けして補完するスタイルはトークン効率も品質も悪化させる
- **ユーザーターン数を減らす**: 質問は batch して投げ、モデルが進めるための文脈を最初に揃える
- **正例で示す（ポジティブ例 > ネガティブ指示）**: 出力長や声色にこだわる時は「こうしないで」より「こういうトーンで書いて」と例示する方が効く
- **思考の方向性を直接プロンプトする**: 「慎重に段階的に考えて、見た目より難しい問題」/「素早く返答することを優先、迷ったら直接答えて」のような言い方で思考量を制御できる（詳細は本章「adaptive thinking と `ultrathink` キーワード」を参照）

### サブエージェント delegation の指示

Opus 4.7 はデフォルトで subagent の spawn を控える方向に振った。並列調査やファンアウトを期待する場合は **明示的に指示** する必要がある。Opus 4.7 ブログでは以下のような逐語のガイドラインをプロンプトに含めることが推奨されている:

```
Do not spawn a subagent for work you can complete directly in a single response
(e.g., refactoring a function you can already see).
Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.
```

ツール使用についても同様で、より積極的な検索やファイル読み込みを期待するなら **「いつ・なぜ使うか」を明示** する。「気を利かせて使ってくれるはず」を前提にすると、4.6 比でツール呼び出しが減って情報不足のまま回答してしまうことがある。

#### ⚠️ Opus 5 では方針が反転する（委任過剰を抑える）

**Opus 5 は逆に subagent へ委任しすぎる傾向がある**。上記の「明示的に spawn を促す」指示を Opus 5 にそのまま持ち込むと、不要なファンアウトでコストとレイテンシを浪費する。公式 [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) が推奨する抑制方針は以下の通り。

- **大規模かつ真に独立・並列化可能な作業のみ委任する**
- **数回の tool call で終わる作業は委任しない**
- **自分の作業の verify / double-check に subagent を使わない**（Opus 5 は自己検証するため二重になる）
- **1 体で足りるなら 1 体にする**

加えて、**明示的な委任基準か決定論的な spawn 上限を置く**ことが推奨される。ClaudeCode 側にも v2.1.212 / v2.1.217 で **3 種のハード上限**（per-session 200 / concurrent 20 / depth）が入り、ランタイム側でも暴走ファンアウトは抑止されている（[sub-agents.md](sub-agents.md) 参照）。`--max-budget-usd` は **background subagent も停止させる**（v2.1.217 修正）。

| モデル世代 | 委任に関する既定の傾向 | プロンプトでの対処 |
|---|---|---|
| Opus 4.6 | 標準的 | — |
| **Opus 4.7 / 4.8** | **控えめ**（spawn を渋る） | **明示的に spawn を促す**（上記の逐語ガイドライン） |
| **Opus 5** | **過剰**（委任しすぎる） | **委任基準を明示して抑える** + spawn 上限を設定 |

### 4.6 → 4.7 の振る舞い変化早見表

旧モデル向けにチューニング済みのプロンプト・ハーネスを引き継ぐ時に効くのが、デフォルト挙動の差分把握。

| 観点 | Opus 4.6 | Opus 4.7 | 対処の指針 |
|------|---------|---------|-----------|
| 応答長 | デフォルトで冗長 | タスク複雑度に応じて calibrated。単純な lookup は短く、開放的な分析は長く | 出力長にこだわるなら **長さ・スタイルを正例で明示** |
| ツール使用頻度 | 多め | より少なく、推論を増やす方向 | 検索・読み込みを増やしたいなら **タイミングと理由を明示** |
| サブエージェント spawn | 多めに spawn | judicious に判断、デフォルトでは少なめ | ファンアウトや並列調査を期待するなら **同一ターン内で複数 spawn を指示** |

### adaptive thinking と `ultrathink` キーワード

**Opus 4.7 以降では固定 thinking budget の Extended Thinking はサポートされない。** 代わりに **adaptive thinking（adaptive reasoning）** が標準で動作する。これは「各ステップで思考の有無を選ぶ」仕組みで、単純な質問では即座に答え、利益のないステップでは思考をスキップし、必要な時にだけ thinking トークンを投入する。長いエージェンティック実行では、トータルで応答が速くなり体験が改善する。Opus 4.7 で **overthinking の傾向が抑えられ**、Opus 4.8 では同一 effort でも bimodal ワークロードで無駄な thinking トークンがさらに減少した。なお公式モデル overview の分類では **Opus 4.8 は「Extended thinking: No / Adaptive thinking: Yes」**（= 固定 budget の extended thinking は非対応で adaptive reasoning のみ）、Sonnet 4.6 は「Extended thinking: Yes」、Haiku 4.5 は「Adaptive thinking: No」と整理されている（出典: [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)）。

思考量を直接プロンプトで制御する例:

- **思考を増やしたい**: `Think carefully and step-by-step before responding; this problem is harder than it looks.`
- **思考を減らしたい**: `Prioritize responding quickly rather than thinking deeply. When in doubt, respond directly.`（精度は若干下がる可能性あり、トークン節約優先のとき）

**`ultrathink` キーワードは公式にサポートされている**（[model-config](https://code.claude.com/docs/en/model-config) で明記）。プロンプトのどこかに `ultrathink` を含めると、そのターンだけ in-context の指示が追加され、より深い推論を要求できる（API に送られる effort レベル自体は変わらない）。一方、`think` / `think hard` / `think more` 等の語句は通常のプロンプトテキストとして扱われ、キーワードとしては認識されない。extended thinking のトグル自体は `Option+T` / `Alt+T` で引き続き存在する。

> **補足（旧版からの訂正）**: 旧版の本ドキュメントは「`ultrathink` は公式に明示的言及がない」と記載していたが、現行の [model-config](https://code.claude.com/docs/en/model-config) では `ultrathink` が公式キーワードとして明記されている（2026-05-30 確認）。ただし adaptive thinking が標準で機能するため、複雑タスクではキーワード無しでもモデルが思考量を増やす。`max` effort + 強制的な思考促進の併用は overthinking を呼びやすいため、評価用途以外では控えるのが安全。

> **Tips**: effort をモデルのデフォルト（Opus 4.8 なら `high`、Opus 4.7 なら `xhigh`）のままにして、まずは「第 1 ターンで完全仕様」を試してみる。旧世代比で必要なターン数が減り、長時間タスクへの適性が体感できれば、ハーネス側の調整をさらに進められる。

---

## 9. AI ネイティブ開発のセキュリティ（Anthropic 自社の実践）

> 出典: [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle)（2026-07-21）

Anthropic が自社の SDLC で実践しているセキュリティ運用を公開した記事である。**「エージェントに何をさせないか」ではなく「エージェントが失敗しても被害が出ない構造をどう作るか」**という設計思想で、個人開発でもそのまま使える要素が多い。

### 6 つの実践

| 実践 | 内容 |
|---|---|
| **セキュア指針を CLAUDE.md に埋める** | セキュアコーディングのガイドラインを CLAUDE.md に書き、「**コードが生成された瞬間から**ベストプラクティスに従う」状態を作る。脆弱性が見つかったら該当ファイルを更新して**再発を防ぐ閉ループ**にする（レビューで毎回指摘するのではなく、生成時点で防ぐ） |
| **`/security-review` を生成フローに組み込む** | 「攻撃者が制御可能な入力の侵入点を探し、疑わしいリンクをスキャンし、**検出結果を検証する**」。セキュリティ指針の plugin が生成中の会話をリアルタイムでレビューする運用も併用している |
| **egress allowlist 付きのリモート VM** | 開発はリモート VM 上で行い、egress を allowlist で絞る。エージェントが untrusted な入力に含まれる **prompt-injection ペイロードに遭遇しても exfiltration path が存在しない**状態を作る（「騙されない」ではなく「騙されても外に出せない」） |
| **Principle of Least Agency** | 各エージェントに**職務上必要な最小権限のみ**を与える。例として挙げられているインシデント対応エージェントは、**ドキュメント作成 / Slack 投稿 / ログ参照はできるが、修正のデプロイはできない** |
| **狭いスコープのレビュアーを複数置く** | 広範な単一レビュアーではなく、**焦点を絞った複数のエージェント**を使う。理由は「**they do not share biases and blindspots**」— 万能レビュアー 1 体は盲点も 1 つに集約されるため、独立した狭いレビュアーを並べる方が検出漏れが減る |
| **新レビュアーは shadow mode から** | 新しい自動レビュアーは、**人間の承認を前提にコメントを投稿させて信頼を獲得してから**昇格させる。チームは**意図的に悪性の変更を挿入して信頼性を試験**している |

### 本リポジトリのハーネス設計への影響

「**狭いスコープのレビュアーを複数置く**」は、[harness.md](harness.md) の Planner / Generator / Evaluator 構成に対する公式側の補強材料である。**Evaluator を 1 体の万能レビュアーとして設計しない**根拠になる（詳細は harness.md の該当節を参照）。

本リポジトリの既存運用との対応:

- `best-practice-auditor` / `spec-driven-review` を**別 SubAgent として分離**しているのは、上記「盲点を共有しない複数レビュアー」と同じ発想である
- `/review-all-ai` で claude[bot] / Copilot の**複数 AI レビューを横断**させているのも同型のパターンにあたる

---

## よくある失敗パターン（アンチパターン）

| パターン | 症状 | 対処法 |
|---------|------|--------|
| **キッチンシンクセッション** | 一つのセッションで無関係なタスクを混在させ、コンテキストが無関係な情報で溢れる | `/clear` で無関係なタスク間を分離 |
| **繰り返し修正** | 同じ問題を何度修正しても直らず、コンテキストが失敗したアプローチで汚染される | 2回失敗したら `/clear` して、学んだことを反映したより良いプロンプトで再開 |
| **肥大化したCLAUDE.md** | 長すぎるためClaudeがルールの半分を無視する | 容赦なく剪定。Claudeが指示なしで正しく動作するなら削除、またはHookに変換 |
| **検証なしの信頼** | 動いているように見えるがエッジケースを処理していない実装を出荷する | 常に検証手段（テスト・スクリプト・スクリーンショット）を提供する。検証できなければ出荷しない |
| **無限探索** | スコープなしで「調査して」と頼むと数百ファイルを読みコンテキストを消費する | 調査のスコープを絞るか、サブエージェントに委任してメインコンテキストを消費させない |
| **過度な subagent spawn** | 単一応答で完結する作業まで毎回 subagent に委任し、レイテンシとトークンを浪費する | プロンプトで delegation 方針を明示する（逐語例は下記、または第 8 章「サブエージェント delegation の指示」を参照） |

> **過度な subagent spawn の対処プロンプト例**（Opus 4.7 ブログより）:
> ```
> Do not spawn a subagent for work you can complete directly in a single response
> (e.g., refactoring a function you can already see).
> Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.
> ```

---

## 直感を磨く

このガイドのパターンは出発点であり、すべての状況に最適ではない。

- **コンテキストを蓄積すべき時もある**: 一つの複雑な問題に深く入り込んでいて、履歴が価値を持つ場合
- **計画をスキップすべき時もある**: 探索的なタスクでClaudeが自分で考えた方が良い場合
- **曖昧なプロンプトが最適な時もある**: 制約を加える前にClaudeが問題をどう解釈するかを見たい場合

**うまくいった時に注目する**: プロンプト構造・提供したコンテキスト・使っていたモードを意識する。**Claudeが苦戦した時に原因を考える**: コンテキストがノイジーすぎた？プロンプトが曖昧すぎた？タスクが一回で処理するには大きすぎた？

時間とともに、どのガイドも捉えられない直感が身につく。いつ具体的にすべきか、いつオープンエンドにすべきか、いつ計画すべきか、いつ探索すべきか、いつコンテキストをクリアすべきか、いつ蓄積すべきかを感覚的に理解できるようになる。

そしてモデルが更新されるたびに、最適な直感も少しずつ変わる。次のモデル世代が来たら、本書の各章ごと「まだ通用するか / 何が変わったか」を再点検することを習慣にしたい。

---

## 関連リソース

本書の出典と、本文中で参照した公式ドキュメント・ブログを 3 つのカテゴリで分類する。

### 一次出典

| リソース | URL |
|---------|-----|
| [公式ベストプラクティス](https://code.claude.com/docs/en/best-practices) | 本書全体の一次出典 |
| [Opus 4.7 ベストプラクティス（ブログ）](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code) | 第 8 章の主たる出典 |
| [Opus 4.7 launch announcement](https://www.anthropic.com/news/claude-opus-4-7) | モデル概要・能力比較 |

### 本書で参照した機能ドキュメント

| リソース | 用途 |
|---------|------|
| [Permission modes](https://code.claude.com/docs/en/permission-modes) | auto mode・bypassPermissions など全モードの仕様 |
| [Permissions（allow / ask / deny ルール）](https://code.claude.com/docs/en/permissions) | deny ルール構文・managed policies |
| [Sandboxing](https://code.claude.com/docs/en/sandboxing) | OS レベル分離の詳細 |
| [Checkpointing](https://code.claude.com/docs/en/checkpointing) | チェックポイント仕様 |
| [Agent teams](https://code.claude.com/docs/en/agent-teams) | 複数セッション自動連携（experimental） |
| [Side questions with /btw](https://code.claude.com/docs/en/interactive-mode#side-questions-with-%2Fbtw) | コンテキストを汚さないサイドバー質問 |
| [Claude in Chrome](https://code.claude.com/docs/en/chrome) | UI 検証用ブラウザ拡張（beta） |

### 発展リソース

| リソース | 用途 |
|---------|------|
| [Auto mode 解説（ブログ）](https://claude.com/blog/auto-mode) | auto mode の設計思想と内部の安全層 |
| [セッション管理と 1M context（ブログ）](https://claude.com/blog/using-claude-code-session-management-and-1m-context) | 長セッション運用の補足 |
| [Prompt engineering best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | プロンプト設計の体系ガイド |
| [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) | エージェンティックループの内部仕様 |
| [Extend Claude Code](https://code.claude.com/docs/en/features-overview) | Skills / Hooks / MCP / Subagents / Plugins の選び分け |
| [Common workflows](https://code.claude.com/docs/en/common-workflows) | デバッグ・テスト・PR 作成などの典型レシピ |
| [Memory（CLAUDE.md 詳細）](https://code.claude.com/docs/en/memory) | CLAUDE.md と memory システムの体系 |

---

Harder Better AI Stronger
