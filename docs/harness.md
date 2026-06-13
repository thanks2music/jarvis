# ハーネス設計ガイド（Anthropic 提唱の Agentic Harness）

> 出典:
> - [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（Anthropic Engineering Blog、本ガイドのメイン出典）
> - [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（Anthropic Engineering Blog、先行する 2-agent 構成の解説）
> - [Claude Code Glossary - Agentic harness](https://code.claude.com/docs/en/glossary)（公式用語定義）
> - [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)（2026-05-28、dynamic workflows / ultracode）
> - [A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（2026-06-02、failure mode / compositional パターン）
> - 参考二次情報: ShinCode「Claude Code マルチエージェント設計｜AI の出力品質を劇的に上げるハーネスパターン」
> 最終更新: 2026-06-10

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

ClaudeCode 公式 Glossary は以下のように定義する（2026-05-30 時点の現行文面）。

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

> **Opus 4.8 での補足**: 能力境界がさらに上がり、長セッションでの自律性が向上した。加えて **Dynamic Workflows（ultracode）** が登場し、1 セッションで数百の並列 subagent をオーケストレーションして数十万行規模の migration を回せるようになった。これは「面白い組み合わせは消えず、より難しい問題へ移動する」というテーゼ（下記）の具体例であり、ハーネス的構成が**より大規模な問題に対して有効になった**ことを示す。出典: [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) / [Model configuration](https://code.claude.com/docs/en/model-config)。

> **Fable 5 / Mythos 5 での補足（2026-06-09 リリース）**: Anthropic が **Mythos-class** と呼ぶ新系列で、`opus` エイリアスの解決先は Opus 4.8 のまま据え置かれ、Fable 5 は `/model fable` で明示選択する。「any previous Claude models より長く自律動作可能」と公式が強調しており、Generator 単体での長時間実行をさらに伸ばす方向で能力境界が拡張された。Fable 5 には安全分類器が内蔵され、サイバー/生物関連のタスクは自動で default Opus に fallback する設計のため、ハーネス側で Evaluator を組む場合は「現在どのモデルが実装中か」を意識する必要がある（fallback で Opus 4.8 にスイッチした際、Evaluator が想定する能力前提とズレる可能性）。料金は Opus 4.8 の約 2 倍（`$10 / $50 per MTok`）のため、ハーネスを Fable 5 で回す場合はコスト見積もりを再設定する。出典: [Introducing Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) / [Model configuration](https://code.claude.com/docs/en/model-config)。

Anthropic の総括。

> Interesting harness combinations don't shrink as models improve—they move.

**ハーネスの「面白い組み合わせ」はモデル進化と共に消えるのではなく、より難しい問題に対して同じ組み合わせが有効になる方向へ移動する**。

### 4.7 Dynamic Workflows（Opus 4.8〜、公式体系化）

> 出典: [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)（2026-05-28）/ [A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（2026-06-02）

Opus 4.8 と同時に登場した **dynamic workflows（ultracode）** について、Anthropic はブログ 2 本で設計思想を公式に体系化した。本ガイドの「固定の 2-agent / 3-agent 構成」を一段抽象化した位置づけである。

#### 中核アイデア: ハーネスを「その場で書く」

従来は人間が Planner / Generator / Evaluator のような **固定ハーネス**を組んでいた。dynamic workflows では **Claude がタスクごとに専用のオーケストレーションスクリプトをその場で書き**、数百の並列 subagent を 1 セッションで指揮する。「あらゆるタスクに専用ハーネスを」という発想で、固定ハーネスの硬直性を超える。

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

- **数百の並列 subagent を 1 セッションで起動**するため、typical session より大幅にトークンを消費する。**scoped なタスクから始めて消費量を把握**し、**auto mode の併用**で確認疲れを避けるのが推奨。
- 起動方法は 2 つ: ① Claude に直接依頼する、② `ultracode` 設定で自動起動する（`--settings` の `"ultracode": true` でも可）。対象は Max / Team / Enterprise（research preview）。

---

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

---

## 8. JARVIS との関係（このリポジトリ固有）

本リポジトリ（JARVIS）の組織構造（BOSS / JARVIS / 各部署 / SubAgents）は、ハーネス設計の考え方と整合している。

- **JARVIS（COO 兼秘書）** = ハーネス全体の指揮者
- **各部署 / SubAgents** = 専門化された生成器・評価器
- **`.jarvis/[department]/CLAUDE.md`** = 部署固有の評価基準・行動規範
- **`docs/best-practices.md`** = プロジェクト全体の品質基準（評価基準としても機能）

つまり JARVIS Plugin の設計は **Anthropic 提唱のハーネスパターンを、個人開発の組織アナロジーで具現化したもの** と捉えることができる。

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

### 参考二次情報

- ShinCode 「Claude Code マルチエージェント設計｜AI の出力品質を劇的に上げるハーネスパターン」 — 日本語での体系的解説。本ガイド作成時に整合性検証済み

### 関連する Anthropic モデル発表

- [Introducing Claude Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5) — Context Anxiety がほぼ解消された世代
- [Introducing Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6) — DAW 実験で使用された世代
- [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7) — Opus 4.8 の前世代
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) — Opus 系列の現行最新
- [Introducing Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) — 2026-06-09 リリースの Mythos-class 新系列。Fable 5 が GA、Mythos 5 は Project Glasswing 限定
