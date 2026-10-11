# ハーネス設計ガイド（Anthropic 提唱の Agentic Harness）

> 出典:
> - [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（Anthropic Engineering Blog、本ガイドのメイン出典）
> - [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（Anthropic Engineering Blog、先行する 2-agent 構成の解説）
> - [Claude Code Glossary - Agentic harness](https://code.claude.com/docs/en/glossary)（公式用語定義）
> - [Running auto mode in production](https://claude.com/blog/auto-mode-in-production)（2026-08-07、auto mode を前提とした長時間ループの設計指針）
> - [Claude Security](https://code.claude.com/docs/en/claude-security)（多エージェント検証の公式実装例）
> - [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)（2026-05-28、dynamic workflows / ultracode）
> - [A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（2026-06-02、failure mode / compositional パターン）
> - [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)（Opus 5 の委任・検証・冗長性の指針。4.6 節の一次出典）
> - [Building verification loops in Claude Code with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)（2026-07-22、verification loop の 4 配置モデル）
> - [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration)（2026-07-16、大規模移行の orchestration パターン）
> - [How Datadog built a "universal machine tool" for Claude Code](https://claude.com/blog/how-datadog-built-a-universal-machine-tool-for-claude-code)（2026-07-21、検証優先の設計論）
> - [Workflows](https://code.claude.com/docs/en/workflows)（dynamic workflows の runtime 制約・size guideline）
> - [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle)（2026-07-21、Evaluator を複数の狭いレビュアーに分割する根拠。4.11 節の一次出典）
> - [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude)（2026-07-28、MCP 仕様の新版。4.12 節の一次出典）
> - [Model configuration](https://code.claude.com/docs/en/model-config)（alias の解決先・automatic model fallback・effort 解決順・ultracode）
> - [Permission modes](https://code.claude.com/docs/en/permission-modes)（auto mode の既定化・既定ブロック規則）
> - [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5)（2026-09-22）/ [Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5)（2026-09-28）/ [Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)（2026-10-07）
> - [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)（無人ループの途中停止・multiagent harness の時間シグナル。4.6 節の Opus 5.5 補足の一次出典）
> - [Configure your agent](https://code.claude.com/docs/en/agent-sdk/configuration)（Agent SDK の設定ハブ。`-p` / SDK でループを組む際の参照先）
> - [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview)（Opus 5 の仕様カード。旧 `whats-new-opus-5` ページの移転先）
> - [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)（モデル別の thinking の既定と無効化可否）
> - [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)（Host containment エントリ）/ [Environment variables](https://code.claude.com/docs/en/env-vars)（workflow 関連の環境変数）
> - [How to prepare for AI-driven code modernization projects](https://claude.com/resources/articles/how-to-prepare-for-ai-driven-code-modernization-projects)（2026-09-23、4.9 節の事例）
> - [How Block orchestrates Claude Fable across thousands of pull requests](https://claude.com/resources/articles/how-block-orchestrates-claude-fable-across-thousands-of-pull-requests)（2026-10-08、4.9 節の事例）
> - [How Cresta turned CX expertise into an agent builder on the Claude Agent SDK](https://claude.com/resources/articles/how-cresta-turned-cx-expertise-into-an-agent-builder-on-the-claude-agent-sdk)（2026-10-05、4.11 節の事例）
> - [Let Claude coordinate ongoing work with Projects](https://code.claude.com/docs/en/claude-projects) / [Projects redesigned: from folder to conversation](https://claude.com/resources/articles/projects-redesigned)（2026-09-17、4.16 節）
> - 参考二次情報: ShinCode「Claude Code マルチエージェント設計｜AI の出力品質を劇的に上げるハーネスパターン」
> 最終更新: 2026-10-11（ClaudeCode v2.1.296 / Opus 5.5・Sonnet 5.5・Haiku 5.5 時点）

ClaudeCode を使った AI エージェント開発において、Anthropic Engineering Team が提唱する **「ハーネス（agentic harness）」** という設計概念がある。本ガイドは「ハーネスを一切把握していない読者が体系的に学べる」ことを目的に、要約 → 結論 → 理由 → 具体の順で整理する。

---

## 1. 要約（TL;DR）

- **ハーネスとは「言語モデルを自律的なコーディングエージェントへ変換するための足場」全体を指す公式用語である**。ClaudeCode 自体がそのハーネスの一例である。
- 単一エージェント（一人の Claude）に長時間タスクを任せると **コンテキスト不安** と **自己評価の甘さ** という 2 つの構造的問題が出る。
- Anthropic は GAN（敵対的生成ネットワーク）に着想を得て、**生成器（Generator）** と **評価器（Evaluator）** を分離する設計を提案した。フルスタック開発ではここに **プランナー（Planner）** を加えた 3 エージェント構成に発展している。
- **ハーネスの各コンポーネントは「モデル単独ではできないこと」の仮定をエンコードしている**。モデルが進化すると不要になる部分があり、定期的に削る判断が必要である。
- ハーネスの「面白い組み合わせ」はモデルが賢くなっても消えるのではなく **境界が移動する**。新しいモデルでは「より難しい問題」に対して同じハーネスが有効になる。

---

## 2. 結論

### 2.1 ハーネスの公式定義

ClaudeCode 公式 Glossary は以下のように定義する（2026-10-11 時点の現行文面。2026-05-30 の確認時から変わっていない）。

> The tools, context management, and execution environment that turn a language model into a capable coding agent. Claude Code is the harness; Claude is the model inside it. The harness supplies file access, shell execution, permission gating, memory loading, and the loop that chains actions together.
> — [Claude Code Glossary - Agentic harness](https://code.claude.com/docs/en/glossary)（詳細は [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) を参照）

つまり以下を含む **足場全体** がハーネスである。

- ツール群（ファイル読み書き・シェル実行・MCP・Web 取得 等）
- コンテキスト管理（読み込み・要約・リセット）
- 実行環境（パーミッション制御・アクション連鎖ループ）
- メモリの読み込み（CLAUDE.md・Skills・SubAgents）

**「Planner + Generator + Evaluator のセット = ハーネス」ではない**。それはハーネスの「一形態」である。ClaudeCode 単体もハーネスであり、SubAgents や Hooks・Skills を組み合わせた構成もハーネスである。

### 2.2 設計上の最重要テーゼ

Anthropic Engineering Blog から抜粋する。

> Every component in a harness encodes an assumption about what the model can't do on its own, and those assumptions are worth stress testing, both because they may be incorrect, and because they can quickly go stale as models improve. Find the simplest solution possible, and only increase complexity when needed.
> — [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

要点は 3 つ。

1. **足場（スキャフォールド）はモデルの限界に対する仮定の塊である**
2. **その仮定はモデルが進化すると陳腐化する**。定期的に検証・削減する必要がある
3. **最もシンプルな解から始めて、必要になった時だけ複雑さを増やす**

### 2.3 採用判断の基準

| 状況 | ハーネスの推奨度 | 理由 |
|------|----------------|------|
| 短時間・単純なタスク | 不要 | ハーネスは純粋なオーバーヘッド |
| 長時間（数時間以上）の自律実行 | 強く推奨 | 単一エージェントが破綻するライン |
| 主観的評価が必要なタスク（UI/UX、文章） | 強く推奨 | 自己評価が機能しない領域 |
| タスクの難易度がモデルの能力境界を超える | 推奨 | 評価器による「最後の 1 マイル」検出が効く |
| タスクがモデルの能力に対して余裕がある | 不要 | 評価器はオーバーヘッドにしかならない |

---

## 3. 理由・課題: なぜ単一エージェントでは不十分か

Anthropic は単一エージェントの長時間タスク失敗パターンを **構造的な 2 つの問題** として整理している。

### 3.1 コンテキスト不安（Context Anxiety）

#### 定義

モデルがコンテキストウィンドウの上限に近づくと「もうすぐ限界だ」と感じ取り、まだ実装すべき機能が残っているのに早めに切り上げてしまう現象。Anthropic は以下のように定義している。

> agents begin wrapping up work prematurely as they believe is their context limit
> — Harness design for long-running application development

#### 観察される兆候

- 仕様に書かれた機能の一部を省略し始める
- エラーハンドリングが急に雑になる
- テストを書かず「テストは後で追加してください」と報告する
- CSS が急にインライン化される（ファイルを増やしたくない心理）
- 「完了しました」と報告するが実際には未完成

#### モデル世代との関係

| モデル | コンテキスト不安の程度 |
|-------|---------------------|
| Sonnet 4.5 | 強い。コンパクションだけでは不十分で、コンテキストリセットが必須 |
| Opus 4.5 | 大幅に改善。連続セッション運用が可能になった |
| Opus 4.6 / 4.7 | ほぼ解消。スプリント分割なしでも 2 時間以上一貫して動作 |

Anthropic は Opus 4.5 について次のように記述している。

> Opus 4.5 largely removed that behavior on its own, allowing context resets to be dropped entirely

つまり **ハーネスのコンポーネント（コンテキストリセット）はモデルの進化と共に不要になり得る**。

### 3.2 自己評価の甘さ（Self-Evaluation Bias）

#### 問題の本質

AI に「自分のコードをレビューして」と頼むと、ほぼ常に「よくできています」と返ってくる。明らかにバグがあっても、である。これはコーディングタスクでも起きるが、特に **デザインのような主観的タスク** で深刻になる。

UI を生成した直後に「このデザインを自己レビューして」と頼むと、テンプレ的な紫グラデーション×白カードのデザインに対しても「洗練されており改善点はありません」と返答する傾向がある。

#### なぜ起きるか

- 生成器に「自分に厳しくなれ」と指示しても効果が薄い
- **作る側と評価する側が同じエージェントである限り、品質の天井を突破できない**
- 検証可能なテスト（pass/fail）があるコーディングタスクでも、AI は自分のコードに対して甘い判断をしがち

#### GAN との発想的類似

Anthropic はこの問題に対し、Generative Adversarial Networks（GAN）の構造を応用した。

> Taking inspiration from Generative Adversarial Networks (GANs), I designed a multi-agent structure with a generator and evaluator agent
> — Harness design for long-running application development

GAN では「生成器」と「判別器」が対立しながら互いを高め合う。同じ考え方で、**コードを書くエージェント** と **品質を評価するエージェント** を分離する。

分離が効く理由は 3 点。

1. **評価器を懐疑的にチューニングしやすい**: 生成器の自己否定ではなく外部からのフィードバックなので、「少しでも問題があれば不合格にして」という指示が効く
2. **評価結果が具体的な改善指示になる**: 「ここがダメ、こう直せ」が外部から来るため、生成器は具体的な修正に集中できる
3. **イテレーションが回る**: 生成 → 評価 → 修正 → 再評価のループが自動で回る

---

## 4. 具体: ハーネスの構成要素

ここからは Anthropic が実験で組み立てた **ハーネスの具体的なパーツ** を見ていく。

### 4.1 評価基準の言語化（フロントエンドデザイン実験）

Anthropic は「デザインの美しさ」という主観的なものを具体的に採点できる **4 つの基準** を定義した。

| 基準 | 内容 | 重み |
|------|------|------|
| Design Quality | 色・タイポグラフィ・レイアウトが一貫した世界観を作っているか | **高** |
| Originality | テンプレート的でない独自の判断があるか。AI スロップの兆候がないか | **高** |
| Craft | スペーシング・色の調和・コントラスト比などの技術的品質 | 低 |
| Functionality | ユーザーが迷わず操作できるか | 低 |

Anthropic は次のように述べている。

> I emphasized design quality and originality over craft and functionality

**Craft と Functionality は Claude が元々得意な領域** であり、AI の弱点である Design Quality と Originality に高い重みを置くことで、「無難だがつまらない」UI からの脱却を狙った。

#### 評価基準そのものがガイドになる効果

興味深いのは、**評価基準を読ませるだけで、評価ループを回す前から生成器の方向性が変わる** ことである。Anthropic は以下のように観察している。

> The wording of the criteria steered the generator in ways I didn't fully anticipate.

具体的には、評価基準に「最高のデザインは美術館品質である（the best designs are museum quality）」と書くだけで、生成されるデザインが特定の視覚的な方向へ収束していった。**評価器が動く前から、基準の文言自体がプロンプトとして機能している**。

#### 「AI スロップ」のペナルティ化

Originality 基準では、生成 AI が量産しがちなパターンを明示的にペナルティ対象にした。

> telltale signs of AI generation like purple gradients over white cards—fail here

つまり「紫グラデーション × 白カード」のような典型的な AI 生成パターンを **明示的に不合格条件として書く** ことで、生成器をそこから遠ざける効果があった。

### 4.2 構成パターン A: Generator + Evaluator（2-agent）

最もシンプルなハーネス構成。フロントエンドデザイン実験で使われた。

```
[ Generator ] ──HTML/CSS/JS生成──> [ 動作確認 (Playwright MCP) ]
      ↑                                       │
      │                                       │
      └──── 4 基準で採点 + 改善指示 ←─── [ Evaluator ]
```

ループは 5〜15 回。1 回のイテレーションで改善が見られない場合は **方向性を完全に変える（ピボット）指示** も含む。微調整とピボットの両方を選べるようにした点が重要。

> **Opus 5 世代での注意（4.6 参照）**: この構成の Evaluator が「**Generator 自身の作業を verify する**」役割になっている場合、Opus 5 では over-verification になる（Opus 5 は自発的に自己検証する）。**fresh context の別視点レビュー**や**決定論的な referee（動作確認・テスト）としての Evaluator は依然有効**なので、「自己検証の代行」か「独立した第三者検証」かで判断する。上図の Playwright MCP による動作確認は後者にあたり、Opus 5 でも有効である。

### 4.3 構成パターン B: Planner + Generator + Evaluator（3-agent）

フルスタック開発に拡張した版。

```
[ Planner ]
   │ 1〜4 行のプロンプト → 詳細な製品仕様書に展開
   ↓
[ Generator ]
   │ 仕様書のタスクをスプリント方式で 1 つずつ実装
   │ 各スプリント終了時に自己評価
   ↓
[ Evaluator ]
   │ Playwright MCP で実際にアプリ操作
   │ UI クリック・API 呼び出し・DB 状態確認
   ↓
合格 → 次のスプリントへ / 不合格 → Generator にフィードバック
```

#### Planner の責務

- 1〜4 文のプロンプトを **詳細な製品仕様書** に展開する
- 「何を作るか」に集中し、「どう作るか」には踏み込まない

> focused on product context and high level technical design rather than detailed technical implementation

技術的実装詳細（例: SQLite のテーブル構成）まで Planner が決めてしまうと、その判断ミスが下流の Generator・Evaluator にそのまま伝播する。**仕様策定と実装判断の分離** が設計のポイント。

#### Generator の責務

- 仕様書のタスクを 1 つずつ実装
- スプリント方式（1 回 1 機能）
- 各スプリント終了時に自己評価してから Evaluator へ引き渡す

実験では React + Vite + FastAPI + SQLite（後に PostgreSQL）のスタックが使われた。

#### Evaluator の責務

- **実際にアプリケーションを操作してテスト** する（Playwright MCP を介して）
- UI クリック、API 呼び出し、DB 状態確認
- 各基準には「ハード閾値」があり、1 つでも下回ればスプリント不合格
- 発見したバグと改善点を具体的にフィードバック

### 4.4 スプリント契約（Sprint Contract）

3-agent 構成の中でも特に重要なメカニズム。

#### 仕組み

各スプリント開始前に、生成器と評価器が **「何を作るか」と「どうやって成功を検証するか」を交渉** する。Anthropic は以下のように記述している。

> sprint contract: agreeing on what 'done' looked like for that chunk of work before any code was written

例えばレベルエディタのスプリントでは **27 項目のテスト基準** が事前に設定された。

```
スプリント 3 の契約例:
- 矩形フィルツールでドラッグして選択タイルを敷き詰められること
- エンティティのスポーンポイントを選択・削除できること
- アニメーションフレームの並べ替えが API で動作すること
```

#### スプリント契約が解決する問題

「曖昧な仕様 → なんとなく実装 → なんとなく OK 判定」という連鎖を防ぐ。評価器は契約に沿って機械的にテストするため、見落としが減る。

#### 実際のバグレポート

| 契約基準 | 評価器の発見 |
|---------|------------|
| 矩形フィルツールでドラッグして選択タイルを敷き詰められる | **不合格** — ドラッグの開始点と終了点にしかタイルが置かれない。fillRectangle 関数は存在するが mouseUp で正しくトリガーされていない |
| エンティティのスポーンポイントを選択・削除できる | **不合格** — Delete キーのハンドラーが selection と selectedEntityId の両方を要求するが、クリック時に selectedEntityId しかセットされない |
| アニメーションフレームの並べ替えが API で動作する | **不合格** — PUT /frames/reorder が /{frame_id} より後に定義されている。FastAPI が 'reorder' を整数としてパースしようとして 422 エラー |

ここまで具体的なバグレポートが出てくるのは、評価器が Playwright で **実際にアプリを操作している** からである。

#### 評価器のチューニングコスト

Anthropic も認めている通り、評価器のチューニングは大変だった。初期段階では「問題を見つけても大した問題ではないと自分を納得させて合格にする」ケースが多発した。**評価器を「適切に懐疑的」に保つこと自体が継続的なエンジニアリング課題** である。

### 4.5 コンテキスト管理: Reset vs Compaction

長時間タスクではコンテキストウィンドウの管理が品質に直結する。Anthropic は 2 つのアプローチを区別している。

| アプローチ | 仕組み | コンテキスト不安への効果 |
|-----------|------|------------------------|
| Compaction（コンパクション） | 会話の古い部分を要約し、同じエージェントが続行。ClaudeCode のデフォルト挙動 | **不十分**。会話連続性は保たれるが「もうすぐ限界」感は残る |
| Context Reset（コンテキストリセット） | コンテキストを完全クリアし、新しいエージェントを起動。前のエージェントの状態を **構造化されたハンドオフ文書** として引き継ぐ | **有効**。クリーンな状態から再開できる |

Anthropic はリセットを次のように説明している。

> Context resets—clearing the context window entirely and starting a fresh agent, combined with a structured handoff—addresses both these issues.

#### モデル世代との関係

- **Sonnet 4.5 時代**: コンテキスト不安が強く、リセットが必須だった
- **Opus 4.5 以降**: 不安が大幅に解消され、**リセットなしで連続セッション運用が可能** に
- **Opus 4.6 / 4.7**: スプリント分割すら不要なケースが増えた

これは「ハーネスのコンポーネントはモデル進化で陳腐化する」の代表例である。

### 4.6 モデル世代によるハーネス進化のまとめ

| モデル世代 | 必要なハーネスコンポーネント | 不要になったもの |
|----------|------------------------|----------------|
| Sonnet 4.5 | Planner / Generator / Evaluator / **Sprint** / **Context Reset** | — |
| Opus 4.5 | Planner / Generator / Evaluator / Sprint | Context Reset |
| Opus 4.6 | Planner / Generator / Evaluator | Sprint |
| Opus 4.7 | Planner / Generator / Evaluator（タスクが境界を超える場合のみ） | 余裕のあるタスクではすべて |
| Opus 4.8 | Planner / Generator / Evaluator（タスクが境界を超える場合のみ） | 余裕のあるタスクではすべて。compaction 回復・long-context 改善で Context Reset / Sprint の不要化が一層進む |
| Fable 5 / Mythos 5 | Planner / Generator / Evaluator（境界を超える長時間タスク・安全分類器 fallback 検証時のみ） | Opus 系列の直線的後継ではない **Mythos-class** の独立系列。長時間自律性がさらに向上し、Opus 4.8 で必要だった Evaluator 介入が一層減る |
| Sonnet 5 | Planner / Generator / Evaluator(通常のコーディング範囲では単発生成で十分) | 2026-06-30 リリース。Adaptive thinking always on、1M context 常時、**$2/$10(2026-08-10 に恒久価格化。9/1 の $3/$15 への値上げは中止)**。Anthropic API の `sonnet` エイリアスの解決先だった（v2.1.197〜v2.1.283。v2.1.284 以降は Sonnet 5.5）。Sonnet 5.5 が出るまでは、Generator を安価に長時間動かす第一候補だった |
| **Fable 5.1 / Mythos 5.1** | Planner / Generator（**Evaluator は「独立した第三者レビュー」または決定論的 referee としてのみ**） | **要 v2.1.257（2026-10-11 訂正: 以前は v2.1.255 と書いていたが、model-config と CHANGELOG はともに v2.1.257 とする）。`fable` エイリアスの解決先。self-verify 代行型 Evaluator は over-verification になる**（後述の補足を参照） |
| **Opus 5** | Planner / Generator（**Evaluator は "独立した第三者レビュー" としてのみ**） | **2026-07-24 リリース。「検証ステップをハーネスから外す」方向の世代**。公式が「**legacy harness scaffolding が追加する別 verification step を削除せよ**」と明示した最初のモデル。自己検証を自発的に行うため、Generator に self-verify させる Evaluator は over-verification になる |
| **Opus 5.5** | Planner / Generator（**Evaluator は独立した第三者レビューか決定論的 referee に限る**。Opus 5 と同じ）。加えて、無人ループでは**テキストだけで終わったターンを完了とみなさない継続判定**が要る | **2026-09-22 リリース。`opus` / `default` の解決先（v2.1.280 以降。Microsoft Foundry を除く）**。公式は、parallel subagents を使う数時間規模の監査・移行を少ない監督で最後まで回す力が Opus 5 より高いとする。**既定 effort は `medium`** で、公式テストでは Opus 5 の `high` と同等以上。Opus 5 で使っていた effort をそのまま持ち込まない（後述の補足を参照） |
| **Sonnet 5.5** | Generator / ワーカー（Opus 5.5 を低い effort で補う位置） | **2026-09-28 リリース。Anthropic API の `sonnet` の解決先（v2.1.284 以降）**。公式は Opus 5.5 の「faster, lower-cost complement」と位置づけ、低い effort で使うときに最もよく補えるとする。Sonnet として初めて cyber の safeguard と fallback を持つ（下の fallback 表）。既定 effort は Claude Code が `medium`、Claude Platform（API）が `high` |
| **Haiku 5.5** | subagent（狭く切ったワーカー・要約・compaction） | **2026-10-07 リリース。Anthropic API の `haiku` の解決先（v2.1.293 以降）**。Haiku として初めて effort に対応した（既定 `medium`）。公式は coding で Opus 5.5 / Sonnet 5.5 の subagent に向くとし、複雑な agentic coding には Sonnet 5.5 / Opus 5.5 を勧める。4.9 の Model stratification で下の層に置く候補 |

> **Opus 4.8 での補足**: 能力境界がさらに上がり、長セッションでの自律性が向上した。加えて **Dynamic Workflows（ultracode）** が登場し、1 セッションで数百の並列 subagent をオーケストレーションして数十万行規模の migration を回せるようになった。これは「面白い組み合わせは消えず、より難しい問題へ移動する」というテーゼ（下記）の具体例であり、ハーネス的構成が**より大規模な問題に対して有効になった**ことを示す。出典: [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) / [Model configuration](https://code.claude.com/docs/en/model-config)。

> **Fable 5 / Mythos 5 での補足（2026-06-09 リリース）**: Anthropic が **Mythos-class** と呼ぶ新系列で、`opus` エイリアスの解決先は **Fable 5 リリース当時は Anthropic API で** Opus 4.8 のまま据え置かれ（当時は Claude Platform on AWS が Opus 4.7、Bedrock / Google Cloud / Foundry が Opus 4.6 と**プロバイダ依存**だった。**v2.1.219〜v2.1.279 は Microsoft Foundry を除く全プロバイダで Opus 5 に統一され、v2.1.280 以降は同じ範囲で Opus 5.5 になった**。現行表は `docs/best-practices.md` の「model alias のプロバイダ別解決」を参照）、Fable 5 は `/model fable` で明示選択する。「any previous Claude models より長く自律動作可能」と公式が強調しており、Generator 単体での長時間実行をさらに伸ばす方向で能力境界が拡張された。Fable 5 には安全分類器が内蔵され、サイバー/生物関連のタスクは自動で別モデルに fallback する設計のため、ハーネス側で Evaluator を組む場合は「現在どのモデルが実装中か」を意識する必要がある（fallback 先の Opus にスイッチした際、Evaluator が想定する能力前提とズレる可能性）。料金は Opus 4.8 の約 2 倍（`$10 / $50 per MTok`）のため、ハーネスを Fable 5 で回す場合はコスト見積もりを再設定する。出典: [Introducing Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) / [Model configuration](https://code.claude.com/docs/en/model-config)。
>
> **fallback マトリクスは v2.1.219 でカテゴリ別に変更された**（それ以前は「一律で provider 既定の Opus に再実行」）。ハーネスの能力前提を考える際はこの表を使う。
>
> | 元のモデル | フラグのカテゴリ | fallback 先 |
> |---|---|---|
> | **Fable 5.1 / Fable 5** | biology | **Opus 5** |
> | **Fable 5.1 / Fable 5** | cybersecurity | **Opus 4.8** |
> | Opus 5 | cybersecurity | **Opus 4.8** |
> | Opus 5 | biology | **fallback なし。refusal で確定終了** |
> | **Opus 5.5** | biology | **Opus 5** |
> | **Opus 5.5** | cybersecurity | **Opus 4.8** |
> | **Sonnet 5.5** | cybersecurity | **Sonnet 5** |
> | Sonnet 5.5 | biology | **fallback なし。refusal で確定終了** |
>
> Opus 5.5 と Sonnet 5.5 の行は 2026-10-11 に追記した（出典: [Model configuration](https://code.claude.com/docs/en/model-config#automatic-model-fallback)）。Opus 5.5 は Fable と同じ振り分けになる。Sonnet 5.5 は biology の fallback 先を持たない。
>
> **fallback に関する追加の注意（2026-09-03 追記、2026-10-11 更新）**:
>
> - **fallback 先が `availableModels` でブロックされていると、fallback は起こらず通常のエラーになる**
> - Bedrock / Agent Platform / Foundry では deployment 経由で解決される。`ANTHROPIC_DEFAULT_OPUS_MODEL` を設定すると pin 先で再実行される。Sonnet 5.5 の cyber fallback には、これに加えて `ANTHROPIC_DEFAULT_SONNET_MODEL` か provider 側の Sonnet 5 エントリが要る
> - ⚠️ **セッション最初のリクエストで fallback が起きうる**（CLAUDE.md の内容や git status が workspace context として送られるため）。**ハーネス起動時の事故要因になる**ので、切り分けには `claude --safe-mode` を使う
> - **fallback 後も、flag されたリクエストの effort をそのまま引き継ぐ**（2026-10-11 追記）。公式の例では、既定 `medium` の Opus 5.5 から Opus 4.8 に落ちたセッションは、Opus 4.8 の既定が `high` でも `medium` のまま動く。fallback 先で Evaluator を回すなら、effort も前提に含めて見積もる
>
> **ハーネス設計上の含意（2026-10-11 更新）**: ① fallback 先は **Opus 5 / Opus 4.8 / Sonnet 5 の 3 通り**になったため、「Evaluator が想定する能力前提」もモデルとカテゴリの組ごとに用意する ② **Opus 5 と Sonnet 5.5 で biology 系タスクを回すと fallback による救済がなく長時間ジョブが停止する**。該当領域では最初から Opus 4.8 か Mythos 5（適格者のみ）を明示指定する。カテゴリ別 fallback は v2.1.219 以上が必須。
>
> （2026-09-03 時点の記述・履歴）当時の含意は「fallback 先が Opus 5 と Opus 4.8 の 2 通り」「biology の救済が無いのは Opus 5 のみ」だった。Sonnet 5.5 の追加で、どちらも上のとおり変わった。

> **Fable 5.1 / Mythos 5.1 での補足（要 v2.1.257、2026-09-03 追記。2026-10-11 訂正: 要求版を v2.1.255 と書いていたが、model-config と CHANGELOG は v2.1.257）**: Fable 5.1 は Opus 5 と同じ「**検証ステップをハーネスから引く**」方向の世代である。公式は Fable の使い方として「**Skip the verification reminders**: it verifies its own work with less prompting, so reminders to test or check are usually unnecessary」と明記しており、**self-verify を代行する Evaluator は over-verification になる**。Evaluator は「独立した第三者レビュー」または決定論的 referee に限る。
>
> プロンプト設計も変わる。公式推奨は「**Describe the outcome, not the steps**」「**Hand it ambiguous problems**」「**Size up larger tasks**（1 セッションを超える規模を分割せず渡す）」であり、**Planner の粒度を細かく切る旧設計は逆効果**になる。成果を維持させる手段として公式は **`/goal`** を案内している（§4.8 の verification loop との接続点）。
>
> ハーネス設計上の注意点:
>
> - **`fable` alias = Fable 5.1**（v2.1.257 以降。それ以前は Fable 5。Claude apps gateway のセッションでは現在も Fable 5）。Fable 5 は `claude-fable-5` の ID 明示指定が必要。**どちらも既定モデルではない**
> - effort は `low`〜`max` の全レベル対応で、モデル既定は `high`。**2026-10-11 時点の model-config の解決順には model-default hold の段が無い**（下の Opus 5 補足の「2026-10-11 更新」を参照）。v2.1.258 時点の docs では hold を持つのは Fable 5 / Opus 4.8 / Opus 4.7 だけで、Fable 5.1 と Opus 5 は持たなかった（履歴）
> - **thinking は無効化できない**（session toggle / `alwaysThinkingEnabled` / `MAX_THINKING_TOKENS=0` すべて無効）。ネイティブ 1M context
> - fallback は **biology → Opus 5 / cybersecurity → Opus 4.8**（Fable 5 と同じ）
> - ⚠️ **無人長時間ループで Fable を既定にしない**: プラン・シート次第で usage credits 課金になり、interactive では同意プロンプトが出る。**Remote Control / background session / agent team では `dialogExpiry`（既定 5 分）でターンが打ち切られる**ため、サイレントな停止要因になる
>
> 出典: [Model configuration](https://code.claude.com/docs/en/model-config) / [model-comparison.md](model-comparison.md)

> **Opus 5 での補足（2026-07-24 リリース、最重要）**: Opus 5 はハーネス設計の前提を 2 つの意味で変えた。
>
> **1. 検証ステップを「足す」から「引く」へ**。公式 [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) は、Opus 5 が指示なしで自己検証するため「最後に verification step を入れる」「subagent に verify させる」「double-check せよ」といった**旧世代由来の指示を削除せよ**と明示している。名指しで「legacy harness scaffolding が追加する別 verification step」も対象に挙げられており、**4.2 / 4.3 の Evaluator をそのまま Opus 5 に持ち込むと over-verification でコストと時間を無駄にする**。
>
> **2. ただし「独立した第三者レビュー」は依然有効**。公式が否定しているのは「**自分の作業を自分で verify させる**」構成であり、fresh context の adversarial reviewer（`/code-review` のような別視点のレビュー）は否定されていない。切り分けは以下の通り。
>
> | Evaluator の型 | Opus 5 での扱い |
> |---|---|
> | Generator 自身に self-verify させる subagent | **不要**（自発的にやるため二重になる） |
> | 独立した adversarial reviewer（fresh context・別視点） | **有効**（自己評価バイアス（3.2）は依然として残る） |
> | 決定論的な referee（compiler / test / behavioral diff） | **最も有効**（4.4 参照） |
>
> **3. 委任が過剰になる**。Opus 4.7 は「subagent spawn が控えめ」だったが、Opus 5 は逆に**委任しすぎる**。公式推奨は「大規模かつ真に独立・並列化可能な作業のみ委任。数回の tool call で終わる作業は委任しない。**自分の作業の verify / double-check に subagent を使わない**。1 体で足りるなら 1 体」。ハーネス側では **明示的な委任基準か決定論的な spawn 上限**（`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 等、[sub-agents.md](sub-agents.md) 参照）を置いて抑える。
>
> **4. 応答と成果物が長くなる**。effort を下げても可視応答は短くならないため、**長さは明示プロンプトで制御**する。ディスクに書く成果物も冗長になりやすいので「filler / redundant summary / boilerplate で埋めない」旨を指示に含める。進捗 narration も増えるため cadence を明示指定する。
>
> **5. effort の起点が変わった**。Opus 4.7 / 4.8 は `xhigh` 起点が公式推奨だったが、**Opus 5 は `high` 起点 + `low`/`medium` を主制御**。
>
> ⚠️ **2026-10-11 更新: effort の解決順は 3 段になった。** 現行 model-config の解決順は ①明示指定（`CLAUDE_CODE_EFFORT_LEVEL` / `--effort` / `/effort`）→ ②設定（モデル別の保存値か `effortLevel` キー。両者の優先は `modelSettings` の定義に従う）→ ③モデル既定、であり、**model-default hold の段は無い**。③は **`high` が基本で、Opus 5.5 / Sonnet 5.5 / Haiku 5.5 は `medium`、Opus 4.7 は `xhigh`**。組織が organization default model に既定 effort を設定している場合は、そのモデルではその値が既定になる。
>
> 加えて、**user settings の top-level `effortLevel` は Opus 5.5 には効かない**。これは per-model 保存より前に `/effort` が書いていた旧形式で、Opus 5 / Fable 5.1 以前のモデルには従来どおり効く。Opus 5.5 以降のモデルは、`/effort` か `/model` picker で選ぶまで自身の既定で始まる（project / local / managed settings と `--settings` の top-level `effortLevel` は全モデルに効く）。ハーネスを Opus 5.5 に移すときは Opus 5 の値を持ち込まず、`medium` から effort sweep をやり直す。
>
> （2026-09-03 時点の記述・履歴。解決順と既定値は上の 2026-10-11 更新が正）⚠️ **2026-09-03 訂正: 「旧モデルの effort が黙って持ち越される」という記述は現行仕様と合わない。** v2.1.251 以降、effort は **モデルごとに `modelSettings.<model>.effortLevel` に保存**されるため、モデルを切り替えても旧モデルの値は引き継がれない。解決順は ①明示指定（`CLAUDE_CODE_EFFORT_LEVEL` / `--effort` / `/effort`）→ ②**model-default hold（Fable 5 / Opus 4.8 / Opus 4.7 のみ。Opus 5 と Fable 5.1 は持たない）** → ③設定（モデル別の保存値 or `effortLevel` キー）→ ④モデル既定（一律 `high`、**Opus 4.7 のみ `xhigh`**）である。「持ち越される」のは **`effortLevel` キーを使っている場合に限られる**。
>
> （旧記述・履歴）加えて **Opus 5 には model-default hold が無く、旧モデルで設定した effort（例 `xhigh`）が黙って持ち越される**。ハーネスを移行する際は effort sweep をやり直す（[model-comparison.md](model-comparison.md) §6.3）。
>
> 出典: [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5) / [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) / [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) / [Model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)

> **ClaudeCode 側の逆方向の変化（必ず併せて読む）**: 上記 1 は「**プロンプトで verify を指示するな**」という話だが、ClaudeCode 本体では逆に「**検証は自分で組まないと走らない**」方向に変わっている。**v2.1.215 で `/verify` と `/code-review` の自発起動が停止**し、**v2.1.218 で `/deep-research` も手動起動のみ**になった（2026-10-11 更新: 現行の [Code Review](https://code.claude.com/docs/en/code-review) では `/code-review` は再び Claude が自ら起動できる。明示起動だけなのは `/verify` と `/deep-research`）。つまり:
>
> - **Claude への指示**: verify の念押しは削る（over-verification を避ける）
> - **ハーネスの構造**: 検証ステップは明示的にチェーン / 埋め込みで組む（自動では走らない）
>
> この 2 つは矛盾ではなく、「**モデルの自己検証に任せる範囲**」と「**決定論的に保証する範囲**」を分ける設計要求である。配置の 4 モデルは 4.8 節を参照。

> **Opus 5.5 / Sonnet 5.5 / Haiku 5.5 での補足（2026-09-22〜10-07 リリース、2026-10-11 追記）**: Opus 5 で始まった「検証ステップをハーネスから引く」方向は変わらない。そのうえで、ハーネス側に効く変化が 4 つある。
>
> **1. 無人ループが「テキストだけのターン」で止まる（Opus 5.5）**。公式 [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) によると、Opus 5.5 は長いタスクの途中で進捗を報告し、その一部はツール呼び出しではなくテキストでターンを終える（`stop_reason: "end_turn"`）。これをタスクの終わりとみなすループは、そこで止まってしまう。公式の対処は次のとおり。
>
> - テキストだけで終わったターンは「報告」として扱い、完了の証拠にしない
> - タスクの部品を to-do ツールやファイルのチェックリストに持たせる。未完了の項目が残り、blocker も述べられていなければ、残りを名指しする短い user message を返す
> - 完了条件を最初に示しておき、ターンが終わるたびに別の小さいモデルに会話を照合させる方法もある。満たしていなければ、その理由を次の user message として返す
> - どちらの方法でも、同じタスクの自動継続は 2〜3 回で打ち切り、本当に詰まった run は止めてレビューに回す
> - background command や subagent がまだ動いているなら、終わるのを待ち、その出力を次の user message として返す
>
> 完了を Generator の自己申告ではなく外から判定する構成であり、§4.13 の「測定可能な成功 / 失敗シグナル」をループの継続判定にも置く、という話でもある。
>
> **2. multiagent harness では経過時間を渡すと並列化が進む（Opus 5.5）**。lead agent が subagent に委任する構成で、ハーネスが各メッセージの末尾に `elapsed 340s / 1200s` のような経過時間と予算を付けると、Opus 5.5 は予算内に収まるようにペースを調整する。公式によると、effort を下げると作業そのものが減るのに対し、予算は主に並列で働く agent の数を増やす方向に効く。ただし予算は助言で、上限で止まるわけではない。ハードストップが要るなら timeout はハーネス側で持つ。時間の圧力で検索・検証が少し減る可能性もあるため、品質は自分のタスクで確かめる。
>
> **3. effort は `medium` 起点になった**。上の「2026-10-11 更新」のとおり、Claude Code の既定は 3 モデルとも `medium` である。公式は Opus 5.5 の `xhigh` / `max` を「品質向上を測定できた作業」に限るよう勧めている。Sonnet 5.5 の発表には、`max` effort では Claude Code の code-review skill（レビューを多数の subagent に分ける）を走らせる頻度が上がり、検証した 2 件で timeout やタスク範囲外の編集につながった、という注記がある。高い effort が委任の過剰につながりうる点は、Opus 5 補足 3 と同じ方向の注意である。
>
> **4. 同じ世代の中でモデルの層を組めるようになった**。公式は Sonnet 5.5 を Opus 5.5 の「faster, lower-cost complement」、Haiku 5.5 を coding で Opus 5.5 / Sonnet 5.5 の subagent に向くモデルと位置づけている。4.9 の Model stratification（実装は小さいモデル、review と rule 作成は大きいモデル）を 5.5 世代だけで組める。
>
> 出典: [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) / [Model configuration](https://code.claude.com/docs/en/model-config) / [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5) / [Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5) / [Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)

Anthropic の総括。

> Interesting harness combinations don't shrink as models improve—they move.

**ハーネスの「面白い組み合わせ」はモデル進化と共に消えるのではなく、より難しい問題に対して同じ組み合わせが有効になる方向へ移動する**。

### 4.7 Dynamic Workflows（Opus 4.8〜、公式体系化）

> 出典: [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)（2026-05-28）/ [A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（2026-06-02）

Opus 4.8 と同時に登場した **dynamic workflows（ultracode）** について、Anthropic はブログ 2 本で設計思想を公式に体系化した。本ガイドの「固定の 2-agent / 3-agent 構成」を一段抽象化した位置づけである。

#### 中核アイデア: ハーネスを「その場で書く」

従来は人間が Planner / Generator / Evaluator のような **固定ハーネス**を組んでいた。dynamic workflows では **Claude がタスクごとに専用のオーケストレーションスクリプトをその場で書き**、多数の並列 subagent を 1 セッションで指揮する。「あらゆるタスクに専用ハーネスを」という発想で、固定ハーネスの硬直性を超える。

> **⚠️ 「数百の並列 subagent」は既定挙動ではなくなった（v2.1.219）**: dynamic workflows の既定が **medium size guideline** に変更された（v2.1.219 当時は agent 15 体未満が目標。**v2.1.271 以降は 10 体未満**で、同じ版から **Pro プランの既定は `small`（5 体未満）**）。大規模ファンアウトを回すには **`workflowSizeGuideline` を `unrestricted` にする**か、`/config` の「Dynamic workflow size」を変更する必要がある。詳細は下記「v2.1.219 での既定変更」。

#### 公式が定義した 3 つの failure mode

本ガイド 3 章の「単一エージェントの 2 問題」を補強・拡張する形で、公式は長時間タスクの失敗を 3 つに整理した。

| failure mode | 内容 | 本ガイドの対応概念 |
|-------------|------|------------------|
| Agentic laziness | やるべき作業を残して早期にタスクを切り上げる | Context Anxiety（3.1） |
| Self-preferential bias | 自分の出力を甘く評価する | Self-Evaluation Bias（3.2） |
| **Goal drift** | **ターンを跨ぐうちに当初の制約・目標を見失う** | （新軸。コンテキスト圧縮で制約が失効する問題と対応） |

**Goal drift** は新しい軸であり、long-running タスクで「最初に与えた受け入れ基準が後半で忘れられる」現象を指す。

#### compositional パターン 6 種

dynamic workflows が組み合わせる基本パターン。本ガイドの 2-agent / 3-agent を超える設計カタログとして公式が提示した。

| パターン | 用途 |
|---------|------|
| Classify-and-act | 入力を分類して分岐処理 |
| Fan-out-and-synthesize | 並列に分散処理し結果を統合 |
| Adversarial verification | 別エージェントが敵対的に検証 |
| Generate-and-filter | 大量生成してから絞り込み |
| Tournament | 候補を勝ち抜き方式で選別 |
| Loop until done | 完了条件を満たすまで反復 |

#### 運用ガイダンス（best-practices.md の auto mode 章と接続）

- **多数の並列 subagent を 1 セッションで起動**するため、typical session より大幅にトークンを消費する。**scoped なタスクから始めて消費量を把握**し、**auto mode の併用**で確認疲れを避けるのが推奨。※ **v2.1.219 以降は既定が medium**（v2.1.271 以降は agent 10 体未満。Pro は `small`）なので、初期のトークン消費は当時より抑えられる。大規模ファンアウトを意図する場合のみ `workflowSizeGuideline` を上げる。
- 起動方法は 3 つ: ① Claude に直接依頼する、② `ultracode` 設定で自動起動する（`--settings` の `"ultracode": true` でも可）、③ **`claude --effort ultracode` で起動時から有効にする**（**v2.1.203 以降**。Agent SDK では `applyFlagSettings()` に `effortLevel: "ultracode"`。どちらも effort level を `xhigh` にする）。セッションの途中なら `/effort ultracode` で有効にできる。
- ⚠️ **ultracode は v2.1.284 で effort level から独立したトグルになった**（2026-10-11 更新。出典: [Model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)）。`/effort ultracode` / `/effort ultracode off`、または `/effort` スライダーで Tab を押して切り替え、**切り替えても effort level は変わらない**。`CLAUDE_CODE_EFFORT_LEVEL` や effort cap が level を決めていても、ultracode はその level のまま有効になる。使えないのは、workflows がオフのときと、モデルが `xhigh` に対応していないときだけである。永続 `effortLevel` 設定と同環境変数は引き続き `ultracode` 値を受け付けない（永続化は専用の `ultracode` キーで行う）。
- 提供対象は dynamic workflows と同じで、**全有料プラン・Anthropic API・Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry**。**Pro は `/config` の Dynamic workflows 行で有効化**する（出典: [Workflows](https://code.claude.com/docs/en/workflows)）。
- （v2.1.284 未満の挙動）ultracode をオンにすると session は `xhigh` になり、別の level を選ぶとオフになり、`xhigh` 未満の effort cap があると使えなかった。以前の記述「`CLAUDE_CODE_EFFORT_LEVEL` が `xhigh` 以外だと非活性化される」「対象は Max / Team / Enterprise（research preview）」はこの時期のもので、現行 docs とは合わない。

> **ファンアウトは意図的に「ずらして」起動されている（v2.1.229〜、2026-08-16 追記）**: 環境変数 **`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`（既定 `5000`）** が効いている。公式の定義は「**Upper bound in milliseconds on how long a workflow agent waits for a same-prefix sibling's first response to begin before sending its own first request**」であり、**固定の待機時間ではなく「待つ上限」**である点に注意する。
>
> **公式の現行記述（2026-09-03 更新）**: 「Claude Code **holds all but the first until the first agent's response begins, then releases the held agents together**... caps the hold at `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` milliseconds, `5000` by default. **Set it to `0` to disable the hold**.」— **`0` で保留を無効化できる**点が旧記述に無かった。なお以前引用していた "Upper bound in milliseconds on how long a workflow agent waits..." という英文は workflows ページには無いが、**env-vars ページの `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` の行には現在も載っている**（2026-10-11 訂正: 以前は「現行ページに存在しない」と書いていたが、env-vars ページで確認できる。「上限である」という解釈は変わらない）。
>
> 同一の prompt-cache prefix を共有するファンアウトでは、**Claude Code が先頭の 1 体を除く全エージェントをこの上限まで保留し、後続が prefix をキャッシュから読む**ようにする（先頭が未処理のまま全員が走ると、全員が prefix を uncached で処理して二重三重に課金される）。
>
> したがって「大量ファンアウトの立ち上がりが少し遅い」のは仕様であり、**レイテンシとトークンコストのトレードオフ**として調整できる。**`0` で待機を無効化**でき、また **`DISABLE_PROMPT_CACHING` が設定されている場合は一切待たない**（キャッシュしないので待つ意味がないため）。**v2.1.229 以降が必要**。出典: [Environment variables](https://code.claude.com/docs/en/env-vars) / [CHANGELOG v2.1.229](https://code.claude.com/docs/en/changelog)

#### v2.1.202 での運用改善

- **`Dynamic workflow size` 設定追加**: 1 セッションで spawn される agent 数の目安を制御できる。**正式なキー名は `workflowSizeGuideline`**（v2.1.219 で判明）。暴走を防ぐ安全弁として利用可
- **OpenTelemetry 属性の追加**: `workflow.run_id` / `workflow.name` が全 workflow イベントに付与される。同一 workflow 内の複数 subagent 実行を **run_id で相関**して分析できる (`prompt_id` (hooks) と組み合わせるとプロンプト単位・workflow 単位の両軸で追跡可能)

#### v2.1.219 での既定変更（重要）

**dynamic workflows の既定が `medium` size guideline（当時は agent 15 体未満が目標。v2.1.271 以降は 10 体未満）になった**。これは「まず大きく回す」から「まず控えめに回す」への方針転換であり、既存の大規模ファンアウト前提のハーネスは**明示的に上限を上げないと縮小される**。

| 項目 | 内容 |
|---|---|
| **設定キー** | **`workflowSizeGuideline`**。任意の settings ファイルから設定可。設定されている間は `/config` の該当行が非表示になる |
| **UI** | `/config` の「Dynamic workflow size」で変更するか、`/config workflowSizeGuideline=small` のように実行する。値を選ぶまでは `/config` の行が既定値に印を付け、workflow の `Running in background` 行に適用中の size が表示される |
| **選択肢** | **4 値**: `unrestricted`（目安なし）/ `small`（5 体未満。v2.1.271 以降の Pro の既定）/ **`medium`（既定、10 体未満。v2.1.271 未満は 15 体未満）** / `large`（50 体未満） |
| **性質** | **cap ではなく「助言」**。公式は「sends the guideline to Claude as **advice, not a cap**」と明記。プロンプト側が別スケールを要求すれば上書きされる |
| **バージョン要件** | size guideline 機能自体は **v2.1.202 以降**。**既定が `medium` になったのは v2.1.219 以降**（それ以前は `unrestricted` が既定）。`workflowSizeGuideline` を settings で指定できるのも v2.1.219 以降。**Pro の既定が `small` になり、`medium` が 15 体未満から 10 体未満に下がったのは v2.1.271**（CHANGELOG による。docs は Pro の既定 `small` に v2.1.271 を明記し、10 体未満への変更版は書いていない） |
| **`Large workflow` 警告との関係** | 既定では 25 体超（または投影トークン 150 万超）で警告が出る。**自分で guideline を選ぶと閾値がその agent 数に置き換わる**。ultracode 有効時は警告が出ない |

✅ **公式 docs の現行文面（2026-10-11 確認）**: 公式 [workflows](https://code.claude.com/docs/en/workflows) は「**The default is `medium`, or `small` when you're signed in on a Pro plan with Claude Code v2.1.271 or later.** Until you choose a value, the `/config` row marks the value as the default, and the workflow's `Running in background` line names the size in force」と書いている。

（2026-08-04 確認時の記述・履歴）**公式 docs も追従済み**: 公式 [workflows](https://code.claude.com/docs/en/workflows) は当時「**The default is `medium`.** Until you choose a value, the `/config` row shows `medium (default)` … **Requires Claude Code v2.1.219 or later; earlier versions default to `unrestricted`**」と明記している。2026-07-26 時点で本ドキュメントが実機確認（v2.1.220）を根拠に CHANGELOG を正とした判断は、公式側の追従によって裏付けられた（当時存在した不整合は解消済み）。

#### runtime の制約値（ハーネス設計時の上限）

dynamic workflows と subagent には以下のハード制約がある。設計時にこの範囲を超えないよう分割する。

| 制約 | 値 |
|---|---|
| workflow 内の同時実行 agent | **既定は最大 16。ClaudeCode が使える CPU が少なければそれより少なくなる**（CPU 制限付きコンテナ内を含む）。**`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` に 1〜256 を設定すると変更できる（v2.1.269 以降、2026-10-11 追記）**。走っている agent の transcript はメモリに載るため、値を上げるとメモリ使用が増える。⚠️ **2026-09-03 訂正: 旧記述の `min(16, CPU コア数 - 2)` という具体式は現行公式に存在しない**（超過分はキューに入り、枠が空き次第実行） |
| 1 run の総 agent 数 | 1,000（暴走ループのバックストップ） |
| 1 回の `parallel()` / `pipeline()` に渡せる item 数 | 4,096（超過は明示エラー。サイレント切り捨てではない） |
| large workflow 警告 | 25 agent または 150 万トークン超（v2.1.219 以降は size guideline 設定値で置換） |
| subagent の concurrent / depth | **20 / 3**（**per-session の 200 上限は v2.1.224 で撤廃された**。[sub-agents.md](sub-agents.md) 参照。**`ultracode` セッションは concurrent 20 の制約を免除される**） |
| workflow subagent の permission mode | ⚠️ **2026-09-03 訂正: 「常に `acceptEdits`」ではない。** workflow が spawn する subagent は**あなたの permission rules を使い、permission mode は subagent の通常ルールで決まる**（未指定なら親会話のモードを継承）。親が auto mode なら frontmatter の `permissionMode` は無視され classifier が評価する。親が `bypassPermissions` / `acceptEdits` ならそれが優先し、上書きできない |
| 保存先 | `.claude/workflows/` と `~/.claude/workflows/`（plugin 配布は `workflows/`） |

- **`ultracode` は人間入力起点でのみ発火する**（v2.1.210）。`-p` / SDK の非 human 入力・scheduled task・webhook・PR コメントからは起動しない。CI から大規模 workflow を回そうとしても効かない点に注意する。
- 出典: [Workflows](https://code.claude.com/docs/en/workflows) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) v2.1.202 / v2.1.210 / v2.1.219 / v2.1.269 / v2.1.271

### 4.8 verification loop の 4 つの配置モデル（2026-07-22 公式）

> 出典: [Building verification loops in Claude Code with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)（2026-07-22）

4.2 / 4.3 の Evaluator を「どこに置くか」について、公式が **4 つの配置モデル**を提示した。**`/verify` は自発起動しない**（v2.1.215 以降。`/code-review` も同版で止まったが、現行の [Code Review](https://code.claude.com/docs/en/code-review) では Claude が自ら起動できる。2026-10-11 更新）ため、検証を確実に走らせるにはこのいずれかを自分で構成する必要がある。

| 配置モデル | 仕組み | 向くケース |
|---|---|---|
| **Standalone** | 横断的なチェックを独立スキルとして明示起動する | 手動レビューの代替。まずここから始める |
| **Embedded** | 生成スキルの内部に検証手順を埋め込む | 生成と検証が不可分な場合。**token 効率が最も良い** |
| **Chained** | スキルが完了時に別スキルを呼ぶ | 複数観点を順に通したい場合。**Anthropic 社内は `/code-review` → `/simplify` → `/verify` → 独自デザインチェック** |
| **PR-wide** | 全 PR で自動実行する | 検証内容が安定してから最後に到達する段階 |

**公式の実務指針**:

- **「毎週手で検証していること」を起点にスキル化する**。抽象的な品質基準から始めない。
- 作り方は `skill-creator` plugin を使うか、`.claude/skills/` に Markdown を直接書く。
- **chain は token 消費が増えるため、まず embedded で効果を検証してから chain 化する**。
- **PR gate（PR-wide）は検証内容が安定してから**。過度な早期自動化を避ける。

> **Opus 5 との接続**: 4.6 節の通り、Opus 5 では「Claude 自身に verify を指示する」必要性は下がった。一方で **ここで扱う「ハーネス構造としての検証」は Opus 5 でも有効**である。両者の切り分けは「モデルの自己検証に任せる範囲（プロンプトから削る）」と「決定論的に保証する範囲（構造として組む）」の区別に対応する。

### 4.9 大規模移行の orchestration パターン（2026-07-16 公式）

> 出典: [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration)（2026-07-16）

Anthropic が Bun の Zig → Rust 移行（**100 万行を 2 週間未満・API コスト $165,000・merge 後の regression 19 件**）で用いた手法。dynamic workflows を実務規模で回す際の具体的な型として、本ガイドの 4.4 スプリント契約を補強する。

**中核原則**: 「**You fix the process (loop) that produced the code**」— 個別のファイルを直すのではなく、そのコードを生み出したループを直す。

**6 段の流れ**:

1. Rulebook（変換規則集）と依存マップを作る
2. サンプルで **mini-migration を回して stress test** する（規則の穴を先に洗い出す）
3. **並列 translation**（確信が持てない箇所には TODO マーカーを残させる）
4. **compile を orchestrated loop で回し、fixer agent がエラーを解消**する
5. smoke test
6. behavior matching（元コードとの挙動一致確認）

**4 つの orchestration パターン**:

| パターン | 内容 |
|---|---|
| **Mechanical work queue** | 次に何をするかを**ディスク上のファイルの存在で決定**する。プロセスが落ちても再開可能（resumable）になる |
| **Adversarial review + arbitration** | 別エージェントが敵対的にレビューし、**判定が不一致な場合は arbitration（裁定）へ escalate** する |
| **Build daemon** | **高価な compile を直列化し、安価な fix を並列化**する。ボトルネックを 1 本に束ねる |
| **Model stratification** | **実装は小さいモデル、review と rule 作成は大きいモデル**に割り当てる |

**検証は「built-in referee」を使う**: compiler / test suite / 元コードとの behavioral diff といった**既に存在する決定論的な判定器**を評価軸にする。LLM に品質を主観評価させるより信頼できる（4.4 スプリント契約の評価軸として一次情報化された）。

#### 事例: code modernization の準備と Block の運用（2026-09〜10、仕様変更ではない）

以下は Anthropic の記事と顧客インタビューで語られた実務の型であり、ClaudeCode の仕様変更ではない。上の 4 パターンを大規模移行に当てはめるときの参考として置く。

**code modernization の 6 段（Anthropic 記事、2026-09-23）**: [How to prepare for AI-driven code modernization projects](https://claude.com/resources/articles/how-to-prepare-for-ai-driven-code-modernization-projects) は、移行を始める前に組織が決めることを 6 段に分けている。

1. **Target**: 移行後の技術スタックと振る舞いを決める（uplift / transform / reimagine の 3 種から選ぶ）
2. **Certificate**: 変更が target に照らして正しいとみなす条件。**各条件は人を介さずに確認できるものにする**。そうすれば agentic workflow は certificate を満たすまで変更を繰り返し、満たせなければ人のレビューに回せる。条件は、fresh context で動く Claude の独立した adversarial review で blocking な指摘が無いこと、新旧で同じ入力から同じ出力が出ること、永続化した状態と wire format が新旧の間で往復できること、ビルドと型チェックが通ることなどから組む
3. **Promotion policy**: certify された変更を本番へ入れる経路。人のレビューの深さを段階に分けて事前に合意し、重要な経路には人のフルレビューを残す
4. **Prerequisites**: 環境・CI/CD・レビューの体制・承認をそろえる。agentic workflow の権限は移行用ブランチへの書き込みだけに絞って本番の credential を渡さず、各変更と PR を agent の transcript と certificate の証拠にひも付ける
5. **Agentic workflow の構築**: Claude Code の dynamic workflow として作り、移行作業を多数の小さな並列 subagent に分ける。記事は code modernization plugin から始めることを勧めている
6. **実行**: まずコードベースの小さな部分で、promotion policy を通して変更を取り込むところまで end to end に回し、それから規模を広げる

問題が出たら個々の変更ではなく workflow を直す、という記事の原則は、上の「You fix the process (loop) that produced the code」と同じである。certificate は、4.4 のスプリント契約を移行全体の合格条件に広げたものと読める。モデルの割り当ても、certificate で完全に検査できる大量の機械的作業には Sonnet のようにコストと能力の釣り合うモデルを、難しい変換と正しさを確かめる adversarial review にはより賢いモデルを充てるよう勧めており、Model stratification と一致する。

**Block のモデル × effort の格子（顧客インタビュー、2026-10-08）**: [How Block orchestrates Claude Fable across thousands of pull requests](https://claude.com/resources/articles/how-block-orchestrates-claude-fable-across-thousands-of-pull-requests) によると、Block は数千 PR 規模の移行で **Fable をオーケストレーターに、Opus / Sonnet をワーカー**に置いている。オーケストレーターは最初の複雑な計画に frontier モデルの token を使い、その後は token の多くを小さいワーカーモデルに回しても品質は落ちなかったという。effort については「同じモデルでも `xhigh` と `medium` は別のモデルのようだ」として、**モデルと effort の組み合わせを 1 つの格子とみなし、ベンチマークするユースケースごとに全モデルの全 effort を測る**運用を語っている。安全面では、main へのマージと本番デプロイは人が行い、agent の変更はセキュリティチェックを通ったうえで、**デプロイに人間 2 名の承認**を要する。Model stratification と、4.6 の補足にある「effort をモデルごとに測り直す」を実運用で組み合わせた例である。

### 4.10 検証優先の設計論（2026-07-21 公式）

> 出典: [How Datadog built a "universal machine tool" for Claude Code](https://claude.com/blog/how-datadog-built-a-universal-machine-tool-for-claude-code)（2026-07-21）

- **ボトルネックは生成ではなく検証にある**: 「Agents already produce code faster than any team can review; the gap between what's generated and what's proven is where failure modes pile up」
- **agent には任意コードではなく「仕様（specification）」を出させ、決定論的な kernel が検証・実行する**。生成物の自由度を絞ることで検証可能性を確保する。
- **state machine をコードではなくデータとして持つ**（検査・差分比較が可能になる）。
- **各 artifact は「頭に収まるサイズ」に保つ**。

> 4.9 の「built-in referee」と同じ方向の主張である。**ハーネス投資の配分は「生成を賢くする」より「検証を厳密にする」側に寄せる**のが 2026-07 時点の公式・実務双方の結論と言える。

### 4.11 Evaluator を「複数の狭いレビュアー」に分割する（2026-07-21 公式）

> 出典: [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle)（2026-07-21）

Anthropic 自社の SDLC セキュリティ運用の記事だが、**Evaluator の構成方針として直接効く主張**が含まれている。

- **万能レビュアー 1 体ではなく、焦点を絞った複数のエージェントを置く**。理由は「**they do not share biases and blindspots**」— 単一の広範なレビュアーは**盲点も 1 つに集約される**ため、独立した狭いレビュアーを並べた方が検出漏れが減る。
- **Principle of Least Agency**: 各エージェントに職務上必要な最小権限のみを与える。記事の例では、インシデント対応エージェントは**ドキュメント作成 / Slack 投稿 / ログ参照はできるが、修正のデプロイはできない**。Evaluator に「不合格なら自分で直す」権限を持たせない設計と対応する。
- **新しい Evaluator は shadow mode から始める**: 人間の承認を前提にコメントを投稿させ、信頼を獲得してから昇格させる。チームは**意図的に悪性の変更を挿入して信頼性を試験**している。「Evaluator の合否判定をいつから信じるか」に対する運用手順として使える。
- **egress allowlist 付きのリモート VM で動かす**: prompt-injection ペイロードに遭遇しても **exfiltration path が存在しない**状態を作る（「騙されない」ではなく「騙されても外に出せない」）。長時間の自律実行では特に有効。

> **4.1 節の「評価基準の言語化」との関係**: 評価基準を 1 本の長いルーブリックに詰め込むより、**観点ごとに Evaluator を分けて別々のルーブリックを持たせる**方が、この節の主張と整合する。ただし [4.8 節](#48-verification-loop-の-4-つの配置モデル2026-07-22-公式)が指摘するように **chain 構成はトークン消費が増える**ため、まず embedded で試してから分割する順序が妥当である。

#### 事例: Cresta の評価 4 観点（顧客事例、2026-10-05、仕様変更ではない）

[How Cresta turned CX expertise into an agent builder on the Claude Agent SDK](https://claude.com/resources/articles/how-cresta-turned-cx-expertise-into-an-agent-builder-on-the-claude-agent-sdk) によると、Cresta は Claude Agent SDK を汎用の実行ハーネスとして agent builder「Conductor」を作り、Conductor が agent をどれだけうまく作れるかを次の 4 観点で評価している。

| 観点 | 問い |
|---|---|
| Outcome | 依頼された、使える成果物を作ったか |
| Execution path | 適切なツールと必要なコンテキストを使ったか |
| Quality | 用意した参照解と比べてどうか |
| Resource use | 時間とモデル使用量はどれだけかかったか |

さらに、**新しい Claude モデルが出たときと Conductor のフレームワークを更新したときに、評価をやり直す**。成果物だけでなく実行経路とコストも採点する点は、Evaluator を観点ごとに分けるこの節の考え方と合う。新モデルごとの再評価は、2.2 の「ハーネスの仮定はモデルの進化で陳腐化する」と、7 章のアンチパターン「ハーネスの陳腐化放置」への具体的な対処になる。

### 4.12 MCP 仕様 2026-07-28 版（ツール層の前提変化）

> 出典: [Bringing MCP 2026-07-28 to Claude](https://claude.com/blog/bringing-mcp-2026-07-28-to-claude)（2026-07-28） / [Connect Claude Code to tools via MCP — MCP client runtimes](https://code.claude.com/docs/en/mcp)（2026-10-11時点） / [Add an interactive UI to your MCP server](https://claude.com/docs/connectors/building/mcp-apps/quickstart)（2026-10-11時点）

ハーネスの「ツール層」の前提が変わる可能性のある動きである。仕様レベルの主な変更は 3 点。

| 変更 | ハーネス設計への含意 |
|---|---|
| コアが **stateful → ステートレスな request/response** へ | セッション状態を MCP サーバー側に持たせる設計は見直しが必要になり得る。状態は呼び出し側（ハーネス）が持つ形が素直になる |
| **MCP Apps / Tasks が「バージョン付き extensions」に分離** | 機能ごとにバージョンを固定できるため、ハーネスが依存する機能の互換性管理がしやすくなる |
| 認可が **OAuth 2.0 / OIDC 準拠** へ | Microsoft Entra / Okta 等の既存 IdP と組み合わせやすくなる。長時間実行での再認証運用に影響する |

> **ClaudeCode 側の対応（2026-10-11 更新）**: MCP ページの「MCP client runtimes」節に対応状況が載った。ClaudeCode は v1 runtime（MCP TypeScript SDK 1.x）と v2 runtime（MCP TypeScript SDK 2.0。protocol revision 2026-07-28 に対応）のどちらかで接続する。v2 が既定になるのは、feature flag を取得するセッションでは v2.1.232 以降、取得しないセッション（Bedrock / Claude Platform on AWS / Agent Platform / Foundry、Claude apps gateway、telemetry off など）では v2.1.274 以降である。v2 は各サーバーに新しい revision に対応しているかを問い合わせ、対応していないサーバーには v1 と同じ方法で接続する。新しい revision で接続した channel サーバーは登録しない。**MCP Apps の UI は ClaudeCode では描画されず、ツールはテキストとして呼ばれる**（mcp-apps quickstart に明記）。詳細は [mcp-setup.md](mcp-setup.md) を参照。
>
> 2026-10-11 訂正: 以前は「ClaudeCode 側の対応状況は未確認。公式ブログは rolling out soon と述べるのみ」と書いていた。

---

### 4.13 auto mode 前提の長時間ループ設計（2026-08）

**auto mode が既定の permission mode になった**。2026-08-14 に Pro / Max / Team プランで既定になり（v2.1.283 未満では、feature flag を取得するセッションのこの 3 プランだけが対象）、**v2.1.283 以降は interactive terminal と VS Code 拡張のセッションで、全プラン・全プロバイダが既定 auto** になった（2026-10-11 更新）。版数は [Permission modes](https://code.claude.com/docs/en/permission-modes) の記載に従う。CHANGELOG はこの変更を 2.1.284 の項に載せており 1 版ずれるが、本ガイドは docs の v2.1.283 を採る。`permissions.defaultMode` を設定していればそちらが優先し、HIPAA 構成を適用した組織の対象セッションは Manual（`default`）で始まる（v2.1.285 以降。auto へは切り替えられる）。[best-practices.md](best-practices.md) / [config-files.md](config-files.md) も参照。長時間ループを回す前提条件が変わったため、ハーネス設計の観点で押さえるべき点を整理する。

> ⚠️ **`claude -p` と Agent SDK の既定は、feature flag を取得するかどうかで分かれる（2026-08-16 追記、2026-10-11 更新。ハーネス設計上の最重要点）**: `claude -p`（print mode）と Agent SDK の built-in default は、**feature flag を取得するセッションでは `default`（Manual）のまま**である。一方、**third-party provider の利用時や telemetry オフ時のように feature flag を取得しないセッションでは、v2.1.285 以降 `auto`** で始まる（それより前は `default`）。組織のポリシーが auto 既定を差し止めている場合は `default` になる。したがって、Manual 既定の `-p` ループで auto を使うなら `--permission-mode auto` を明示し、third-party provider で回す `-p` ループを Manual で動かしたいなら逆にモードを明示する。
>
> （2026-08-16 時点の記述・履歴）当時は「built-in default が `auto` になる条件から `-p` と Agent SDK は明示的に除外され、既定は従来どおり Manual」と書いていた。feature flag を取得しないセッションについては、v2.1.285 でこれが変わった。
>
> あわせて **built-in default にはバージョン要件がある**（macOS / Linux / WSL は v2.1.228 以降、native Windows は v2.1.233 以降）。古い環境で回しているループは既定が変わっていない。
>
> `-p` / Agent SDK でハーネスループを組むときの設定は、Agent SDK の設定ハブ [Configure your agent](https://code.claude.com/docs/en/agent-sdk/configuration) にまとまっている。読み込む settings の範囲（`settingSources`）、`model` / `fallbackModel`、ターン数と費用の上限（`maxTurns` / `maxBudgetUsd`）、実行中の `setModel()` / `setPermissionMode()` を 1 ページで確認できる。
>
> 出典: [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Configure your agent](https://code.claude.com/docs/en/agent-sdk/configuration) / [CHANGELOG](https://code.claude.com/docs/en/changelog) 2.1.283〜2.1.285

### 「測定可能な成功 / 失敗シグナル」がループの前提条件

公式は auto mode の本番運用について、**「長時間の自律ループは、成功 / 失敗のシグナルが測定可能な場合にのみ回す」**という前提を明文化した。

- Evaluator が「なんとなく良さそう」しか返せないループを auto mode で長時間回すのは、公式の推奨から外れる。
- §4.8 の verification loop、§4.11 の狭いレビュアー分割は、**この前提を満たすための具体手段**として位置づけられる。

### 分類器を「唯一の防壁」にしない（defense in depth）

| 層 | 手段 |
|---|---|
| 1 | **skills / permission rule で危険コマンドを deny**（再帰的削除など） |
| 2 | **MCP は tool guard 付きの proxy 経由**にする |
| 3 | auto mode の classifier（最後の砦ではなく 1 層目と考える） |

### 対人コミュニケーション系は自動承認しない

Slack 投稿・メール送信など **外部の人間に届くアクション**は deny する。ユーザーの主体性（agency）を保つためであり、ループの安全性というより**信頼の設計**の問題である。

### 作業内容によって明示的にモードを戻す

Terraform / AWS の直接操作・API の直接変更・クロスリポジトリ変更・機微な IP を扱う作業では、**interactive や `acceptEdits` へ戻す**。

> 実測値として Gusto では **約 10% のセッションで denial が発生**し、auto mode 下では **中断の間隔が従来比 9 倍**になったと報告されている。「10% は止まる」前提でループを設計する（= 完全無人を仮定しない）。
>
> ⚠️ **`-p` でハーネスループを回す場合の重要な差分（2026-09-03 追記）**: **`--permission-prompt-tool` なしの `-p` 実行にはフォールバック先の prompt が存在しない**ため、閾値に到達しても **run は停止せず、当該アクションが実行されないまま Claude は作業を続行する**。つまり `-p` 構成では「止まる」ではなく「**黙って抜け落ちる**」挙動になる。無人ループの失敗が検知されにくい最大の要因なので、Evaluator 側で「実行されたはずの操作が反映されているか」を必ず確認する。
>
> 補足: ① **許可されたアクションが 1 つあると連続カウンタはリセットされる**（累計カウンタはセッション中持続し、自身の上限発火時のみリセット）② classifier 自身のリクエストが別の安全チェックで拒否された場合は**どちらのカウンタにも加算されない** ③ check 保留中にモードを切り替えると verdict は破棄される。
>
> **auto mode の一時停止条件も設計に効く**: classifier のブロックが **3 回連続**、またはセッション累計 **20 回**に達すると auto mode を抜けて通常の prompt に戻る（閾値は設定不可）。**長時間ループが「途中から止まる」のはバグではなく仕様**である。
>
> 出典: [Running auto mode in production](https://claude.com/blog/auto-mode-in-production) / [Permission modes](https://code.claude.com/docs/en/permission-modes)

### 4.14 多エージェント検証の公式実装例: Claude Security plugin

`/plugin install claude-security@claude-plugins-official` で入る公式プラグインは、**脅威モデルの作成 → 脆弱性の探索 → 独立したエージェントによる検証**という多段構成を採る。

- **検証を別エージェントに分離している**点が §4.8 / §4.11 の設計と同じ思想である。
- **patch は必ず人間が `git apply` する**設計で、自動適用しない。「エージェントは提案まで、適用は人間」という境界の引き方の実例として参考になる。
- 出力は `CLAUDE-SECURITY-<timestamp>/` に書き出される。前提は、`PATH` 上の `python3` が 3.9 以降であること（標準ライブラリのみ使う）、dynamic workflows が使えること（v2.1.154+。有料プラン・Anthropic API・third-party provider が対象で、Pro は `/config` で有効化）、change scan と patch 生成には Git が要ること（2026-10-11 訂正: 以前は「python3 3.9.6+」と書いていたが、現行 docs は 3.9 以降とし、Git も前提に挙げる）。
- 詳細は [plugins.md](plugins.md) を参照。

---

### 4.15 v2.1.234〜v2.1.258 の追記（2026-09-03）

**`/workflow-authoring` bundled skill（v2.1.248〜）**: 保存済み workflow の `.js` を編集する前に、このスキルを実行して**スクリプト作成リファレンスをロードすることが公式推奨**である。本リポジトリで workflow を書く際は先に呼ぶ。

**`defaultMode` のスコープ制約**: `.claude/settings.json` / `.claude/settings.local.json` に `"auto"` を書いても無効で、**その場合 `~/.claude/settings.json` の `defaultMode` も使われず built-in default になる**。**`"bypassPermissions"` も同 2 ファイルでは無効**で、セッションは Manual で開始する。組織側で auto mode を選択させないキーは **`permissions.disableAutoMode: "disable"`**。詳細は [config-files.md](config-files.md)。

**auto mode の既定許可 / ブロック規則の更新（ハーネス関連のみ）**:

- **作業中リポジトリの任意ブランチへの push は既定許可**（v2.1.211 で拡大。ただし `production` / `gh-pages` 等の deploy 相当ブランチは個別判断）
- ⚠️ **`--dangerously-skip-permissions` / `--no-sandbox` / `--yes-always` で無人エージェントループを起動する行為自体が既定ブロック**される。**入れ子ハーネスの自動起動は止まる**
- **`~/.claude/projects/` 配下の `.jsonl` transcript への書き込みは既定ブロック**（v2.1.205〜）
- **自分の tmux pane へのキー送信は「自身の権限・監督の変更」としてブロック**される
- **v2.1.257 以降の既定ブロック 4 項目**（2026-10-11 追記。[Permission modes](https://code.claude.com/docs/en/permission-modes) に掲載）: ① cloud の instance-metadata endpoint（`169.254.169.254` など）からの credential 取得や、マシン自身の service account / node identity による明示的な認証 ② tunnel・reverse shell・外向きに書き換えた resolver / proxy 設定など、直接リクエスト以外の経路での public host への到達 ③ タスクではなくホストに属する credential（node の証明書、node の container registry 認証など）の読み取り ④ Claude が起動していない sibling の container / pod / VM や、container の下にある node への接続・スキャン。これらを許すべき環境で動かすなら、`autoMode.environment` の **Host containment** エントリにその構成を書く
- ⚠️ **会話中で述べた境界（「push しないで」等）は block signal として扱われるが、compaction で該当メッセージが消えると失われる**。恒久的に保証したいなら **deny rule** にする
- sandbox のネットワーク verdict はホスト + ポート単位でキャッシュされ、permission mode / rule の変更で全破棄される
- `claude auto-mode defaults` で全ルールを JSON 出力できる

> **2026-10-11 訂正: containment 関連の既定ブロックは公式 docs に載った**。2026-09-03 時点の確認では、`permission-modes` を含む取得済み 33 ページで `containment` が 0 ヒットだったため、CHANGELOG v2.1.257 の「Containment Escape rule」を唯一の一次情報としていた。現行の `permission-modes` には上記の 4 項目が v2.1.257 の既定ブロックとして載り、例外の書き方として `autoMode.environment` の **Host containment entry**（[auto mode の設定](https://code.claude.com/docs/en/auto-mode-config#define-trusted-infrastructure)）が案内されている。ただし「Containment Escape」という**ルール名**は現在も CHANGELOG にしか無いため、本ドキュメントは引き続き名称ではなく実体で記述する。
>
> （2026-09-03 時点の記述・履歴）当時は、概念的に近いものとして「無人エージェントループ起動のブロック」と「自身の tmux pane 操作のブロック」を挙げていた。

出典: [Workflows](https://code.claude.com/docs/en/workflows) / [Permission modes](https://code.claude.com/docs/en/permission-modes) / [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)

### 4.16 Claude Projects: coordinator が並列 thread を回す（2026-09、public beta）

2026-09-17 に Claude Code の Projects が作り直され、**ハーネスの「指揮者 + ワーカー」構成を製品機能として使える**ようになった。goal とリポジトリ（または文書）を渡すと、project の会話で coordinator 役の Claude が依頼をタスクに分けて **thread** を並列に起動し、結果をレビューしてまとめる。thread は通常 1 つの Claude Code cloud session で、専用のブランチで作業し、必要なら PR を開く（手元のマシンが要るタスクは Remote Control 経由でローカルでも動かせる）。cloud の thread はリポジトリの `CLAUDE.md` と skills を読み、リポジトリが 1 つなら permission rules と hooks も適用され、モデルが対応していれば auto mode で動く。thread の中でさらに subagent や workflow に分けることもできる。新しい project の既定は Opus で、thread は effort `high`、coordinator は `low` であり、プランの利用枠をほかのセッションより早く使う。Pro / Max の public beta（段階展開。Team / Enterprise は未提供）で、新しい thread は全 project 合わせて 1 日 200 本までである。固定ハーネス（4.2 / 4.3）や dynamic workflows（4.7）との使い分けは [claude-projects.md](claude-projects.md) にまとめる。出典: [Let Claude coordinate ongoing work with Projects](https://code.claude.com/docs/en/claude-projects) / [Projects redesigned: from folder to conversation](https://claude.com/resources/articles/projects-redesigned)

## 5. 実例: 公式実験の結果

### 5.1 オランダ美術館サイト（フロントエンド実験）

- 構成: Generator + Evaluator の 2-agent
- 結果: 9 回目までは「洗練されたダークテーマのランディングページ」だったが、**10 回目で CSS パースペクティブを使った 3D ギャラリー空間に完全切り替わり**
- 引用: 「壁に絵画が掛かり、ドアから別の部屋に移動するナビゲーション」

> it scrapped the approach entirely and reimagined the site as a spatial experience: a 3D room with a checkered floor rendered in CSS perspective

**単発の生成では絶対に出てこない創造的な飛躍が、評価フィードバックループから生まれた**。スコアの推移は直線的ではなく、最終版より中間のイテレーションのほうが好ましい場合もあった。

### 5.2 2D レトロゲームメーカー（フルスタック実験）

| 方式 | 所要時間 | コスト |
|------|---------|--------|
| Solo（単一エージェント） | 20 分 | $9 |
| Full Harness（3-agent） | 6 時間 | $200 |

コストは 20 倍以上だが、品質差は歴然。

**Solo の問題:**
- レイアウトがスペースを無駄に使う
- ワークフローが不親切（操作順序がわからない）
- **ゲームのプレイモードが動かない**（エンティティ定義とランタイムの配線が壊れている）

**Harness の成果:**
- フルビューポートを活用した洗練された UI
- スプライトエディタ、レベルエディタが充実
- AI 統合でプロンプトからゲーム要素を生成可能
- **ゲームが実際にプレイできる**

### 5.3 DAW（Web Audio API、Opus 4.6 改良版ハーネス）

プロンプトはたった一文。「ブラウザで動くフル機能の DAW を Web Audio API で作って」。

| エージェント | 所要時間 | コスト |
|-----------|---------|--------|
| プランナー | 4.7 分 | $0.46 |
| ビルド（1 回目） | 2 時間 7 分 | $71.08 |
| QA（1 回目） | 8.8 分 | $3.24 |
| ビルド（2 回目） | 1 時間 2 分 | $36.89 |
| QA（2 回目） | 6.8 分 | $3.09 |
| ビルド（3 回目） | 10.9 分 | $5.88 |
| QA（3 回目） | 9.6 分 | $4.06 |
| **合計** | **3 時間 50 分** | **$124.70** |

特筆すべき点。

- **ビルドエージェントが 2 時間以上連続で一貫して動作** した（Sonnet 4.5 では必須だったスプリント分割なしで）
- 完成物はアレンジメントビュー・ミキサー・トランスポートを備えたブラウザ上の音楽制作環境
- 内蔵 AI エージェントがプロンプトからテンポ設定・メロディ作成・ドラムトラック構築・ミキサーレベル調整・リバーブ追加まで自律的に実行
- それでも QA 評価器は「クリップのタイムライン上でのドラッグ移動ができない」「シンセのノブやドラムパッドの UI がない」など **見た目は良くても操作として成立しない問題** を検出した

このように、**モデルの能力が上がっても「最後の 1 マイル」を埋めるのに評価器は有効** である。

---

## 6. Claude Code ユーザーへの実践応用

Anthropic Engineering の実験は大規模だが、個人開発の ClaudeCode ユーザーが今日から活かせる要素を整理する。

### 6.1 SubAgents で「生成×評価」を再現する

最小限のハーネスは ClaudeCode の SubAgents 機能で再現できる。

```
まず feature-a を実装して。
次に別のサブエージェントを起動して、その実装をレビュー・テストさせて。
見つかった問題があれば修正して。
```

完全な 3-agent 構成ではないが、自己評価バイアスを軽減する効果がある。

カスタム SubAgent として永続化することで、毎回同じ評価基準で厳格にチェックさせられる。

```yaml
# .claude/agents/qa-reviewer.md
---
name: qa-reviewer
description: 実装されたコードの品質を厳しくレビューする
tools: Read, Grep, Glob, Bash
model: opus
---

あなたは厳格な QA レビュアーです。以下の基準で実装を評価してください。

## 評価基準
1. 仕様通りに動作するか（スタブやモックで誤魔化していないか）
2. エッジケースが処理されているか
3. UI が直感的に操作できるか
4. エラー時にユーザーにフィードバックがあるか

少しでも問題があれば「不合格」とし、具体的な修正箇所を指摘してください。
「概ね良い」「小さな問題だから大丈夫」という判断は禁止です。
```

詳細は @docs/sub-agents.md を参照。

### 6.2 CLAUDE.md / Skill に評価基準を書く

評価基準そのものがプロンプトとして機能する効果（4.1）を利用し、CLAUDE.md や Skill に **明文化された品質基準** を書く。

```markdown
# 品質基準

- UI は一貫した世界観を持つこと（色・タイポグラフィ・レイアウトの統一）
- テンプレート的な AI デザインを避けること（紫グラデーション・白カードの並びは NG）
- 各機能は実際に動作すること（スタブやモックで誤魔化さない）
- エッジケースのハンドリングを忘れないこと
```

これだけで、評価器を回さなくても「AI スロップ」からの脱却が始まる。

詳細は @docs/skills.md を参照。

### 6.3 Hooks で簡易フィードバックループを自動化

`PostToolUse` Hook でテスト・lint・型チェックを自動実行すれば、簡易的な評価ループが回る。生成器が書いたコードに対してテストという形で即座にフィードバックが返るため、評価器エージェントを立ち上げなくても品質が大きく変わる。

詳細は @docs/best-practices.md の「Hooks（確実な自動実行）」を参照。

### 6.4 採用判断のためのチェックリスト

新しいタスクに対して「ハーネスを導入すべきか」を判断する目安。

- [ ] そのタスクは 30 分以内に終わるか？ → Yes ならハーネス不要
- [ ] 検証可能な明確な完了基準があるか？ → Yes なら Hooks/テスト自動実行で十分なことが多い
- [ ] 主観的評価が必要か（UI/UX、コンテンツ、デザイン）？ → Yes なら Generator + Evaluator を検討
- [ ] 数時間以上の自律実行が必要か？ → Yes なら 3-agent + Sprint Contract を検討
- [ ] モデルの能力境界を超える難しさか？ → Yes なら評価器が「最後の 1 マイル」で効く

---

## 7. アンチパターン

公式記事と Shin さんの記事から抽出したアンチパターン。

| パターン | 症状 | 対処 |
|---------|------|------|
| 過剰なハーネス | モデルが余裕でこなせるタスクに評価器を回し、コストとレイテンシが膨らむ | タスク難易度に応じてハーネスを縮小。最もシンプルな解から始める |
| 評価器の「優しさ」 | 評価器が「大した問題ではない」と自分を納得させて合格にする | 評価器のシステムプロンプトで「少しでも問題があれば不合格」を明示。Opus などより能力の高いモデルを評価器に充てる |
| プランナーの実装詳細介入 | Planner が「SQLite のこのテーブル構成で」と決めてしまい、判断ミスが下流に伝播 | Planner は「何を作るか」のみ。「どう作るか」は Generator に委ねる |
| ハーネスの陳腐化放置 | 新モデルが出ても古いハーネスを使い続け、不要な複雑さを抱える | モデル世代ごとに「このコンポーネントはまだ必要か」を検証する |
| 自己評価への依存 | 同じエージェントに「自分のコードをレビューして」と頼む | 別の SubAgent または別セッションに評価を委ねる |

> **`import()` は runtime のハード制約である（2026-09-03 訂正）**: 現行公式の制約表は「**No module loading: a script that contains `import()` fails before the run starts**」と記載しており、**実行前に失敗する仕様**になっている（「脱出を塞いだ修正」ではなく、そもそも書けない）。**ライブラリが必要な処理は agent のタスク側に置く。**
>
> （旧記述・履歴）**workflow スクリプトの sandbox 脱出を修正（v2.1.223）**: dynamic workflow のスクリプトが**動的 `import()` を使って workflow sandbox 外のコードを実行できる**問題が塞がれた。外部から受け取った workflow スクリプトをそのまま回す運用がある場合は、v2.1.223 以上を使う。

---

## 8. JARVIS との関係（このリポジトリ固有）

本リポジトリ（JARVIS）の組織構造（ユーザー / JARVIS / 各部署 / SubAgents）は、ハーネス設計の考え方と整合している。

- **JARVIS Plugin のメインエージェント** = ハーネス全体の指揮者
- **各部署 / SubAgents** = 専門化された生成器・評価器
- **`.jarvis/[department]/CLAUDE.md`** = 部署固有の評価基準・行動規範
- **`docs/best-practices.md`** = プロジェクト全体の品質基準（評価基準としても機能）

つまり JARVIS Plugin の設計は **Anthropic 提唱のハーネスパターンを、個人開発の組織アナロジーで具現化したもの** と捉えることができる。

### 8.1 並列 SubAgent パターン vs `/harness-loop` の使い分け (v0.6.0〜)

JARVIS Plugin v0.6.0 で「**並列 SubAgent spawn プロトコル**」が SKILL.md に追加された。これによりユーザーの `/jarvis {内容}` 入力に応じて、部署 SubAgent を 1 メッセージ内で並列起動できるようになった。

`/harness-loop` (Planner / Generator / Evaluator の反復ループ) との使い分けは以下:

| 用途 | 並列 SubAgent spawn (v0.6.0〜) | `/harness-loop` |
|---|---|---|
| 時間スケール | ~30 分、1 往復 | 数時間〜、反復改善 |
| 目的 | 部署観点レビュー (横断的所見の収集) | 主観評価ドメインでの Generator/Evaluator 反証 |
| 起動方法 | `/jarvis` から自動分類 + 1 メッセージ内に複数 Task | `/jarvis` の 4 評価軸判定 → 起動 |

短時間の fan-out には並列 SubAgent、長時間の反復には `/harness-loop` を使う。前者はメイン Claude が classify-and-act でディスパッチし、結果を統合する Anthropic 公式の SubAgent パターンに準拠している (Agent Teams や Dynamic Workflows には踏み込まない)。詳細は `docs/jarvis/jarvis-harness-integration.md` 参照。

---

## 9. 関連ドキュメント

- [ClaudeCode のベストプラクティス](best-practices.md) — 第 4 章「環境を整備する」、第 7 章「自動化・スケールアップ」が本ガイドと密接に関連
- [ClaudeCode SubAgents ガイド](sub-agents.md) — 生成×評価の分離を SubAgents で実現する詳細
- [ClaudeCode Skills ガイド](skills.md) — 評価基準の Skill 化、`disable-model-invocation` の活用
- [ClaudeCode Plugins ガイド](plugins.md) — ハーネス構成のバンドル・配布

---

## 10. 出典・参考リンク

### 一次出典（Anthropic 公式）

- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) — 本ガイドのメイン出典。3-agent harness、Sprint Contract、Context Anxiety、DAW 事例
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 先行する 2-agent（initializer + coding agent）構成の解説
- [Claude Code Glossary - Agentic harness](https://code.claude.com/docs/en/glossary) — ハーネスの公式用語定義
- [Workflows](https://code.claude.com/docs/en/workflows) — dynamic workflows の公式リファレンス（runtime 制約・size guideline・保存先）
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) — **「legacy harness scaffolding の verification step を削除せよ」の一次出典**（4.6）
- [Building verification loops in Claude Code with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)（2026-07-22）— verification loop の 4 配置モデル（4.8）
- [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration)（2026-07-16）— 大規模移行の orchestration パターン（4.9）
- [How Datadog built a "universal machine tool" for Claude Code](https://claude.com/blog/how-datadog-built-a-universal-machine-tool-for-claude-code)（2026-07-21）— 検証優先の設計論（4.10）
- [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)（2026-07-24）— Claude 5 世代のコンテキスト設計 6 転換

### 参考二次情報

- ShinCode 「Claude Code マルチエージェント設計｜AI の出力品質を劇的に上げるハーネスパターン」 — 日本語での体系的解説。本ガイド作成時に整合性検証済み

### 関連する Anthropic モデル発表

- [Introducing Claude Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5) — Context Anxiety がほぼ解消された世代
- [Introducing Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6) — DAW 実験で使用された世代
- [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7) — Opus 4.8 の前世代
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) — Opus 5 の前世代（2026-07-24 まで既定の Opus）
- [Introducing Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) — 2026-06-09 リリースの Mythos-class 新系列。Fable 5 が GA、Mythos 5 は Project Glasswing 限定
- [Redeploying Fable 5 and Mythos 5](https://www.anthropic.com/news/redeploying-fable-5) — 2026-06-12 停止 → 06-30 再開の経緯
- [Introducing Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5) — 2026-06-30 リリース。Adaptive-only、1M context 常時、Anthropic API の `sonnet` エイリアスの解決先だった（v2.1.284 で Sonnet 5.5 に交代）
- [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5) — **2026-07-24 リリース。ハーネスから検証ステップを外す方向の世代**。v2.1.219〜v2.1.279 は `opus` / `default` の解決先だった（v2.1.280 で Opus 5.5 に交代。現在は Legacy 扱い）
- [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) — Opus 5 の仕様カード（Legacy 表示。model ID・料金・既定 effort `high` など）。**2026-10-11 張り替え**: 以前は「What's new in Claude Opus 5」（`whats-new-opus-5`）を「thinking 既定 ON 等の破壊的変更の一次出典」として挙げていたが、同ページはこの仕様カードに移り、破壊的変更の一覧は載っていない。Opus 5 の thinking の挙動（既定 ON、`high` 以下なら `thinking: {type: "disabled"}` 可、`xhigh` / `max` では 400）は [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) を参照
- [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5) — **2026-09-22 リリース。現行の Opus（`opus` / `default` の解決先、v2.1.280 以降）**。既定 effort `medium`。無人ループの途中停止への対処は [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)
- [Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5) — 2026-09-28 リリース。Anthropic API の `sonnet` の解決先（v2.1.284 以降）。Opus 5.5 を低い effort で補う位置づけ
- [Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5) — 2026-10-07 リリース。Anthropic API の `haiku` の解決先（v2.1.293 以降）。Haiku 初の effort 対応、subagent 向け
