# codebase-design — deep module を設計するための共通語彙を定める skill

> 出典（一次情報）:
> - [codebase-design/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/SKILL.md) — skill 本体
> - [codebase-design/DEEPENING.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/DEEPENING.md) — 依存の分類と、テストの置き換え方
> - [codebase-design/DESIGN-IT-TWICE.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/DESIGN-IT-TWICE.md) — 並列サブエージェントで interface を複数案出す手順
> - [docs/engineering/codebase-design.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/codebase-design.md) — 同じ作者による解説ページ（補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 手順ではなく語彙のリファレンスである。**module / interface / implementation / depth / seam / adapter / leverage / locality** を厳密に定義し、「component」「service」「API」「boundary」への言い換えを禁じる。
- 目標は **deep module**（小さな interface の裏に多くの振る舞い）を、きれいな seam に置き、interface 越しにテストできるようにすること。
- 原則は 4 つ。depth は interface の性質、削除テスト、interface がテスト面、adapter 1 つは仮の seam・2 つで本物の seam。
- 補助ファイルとして、依存の 4 分類（DEEPENING.md）と、3 案以上の interface を並列に出す「Design It Twice」（DESIGN-IT-TWICE.md）を持つ。
- 他の設計系 skill（[improve-codebase-architecture](improve-codebase-architecture.md) など）がこの語彙を使う。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方 |
| 呼び出し方 | `/mattpocock-skills:codebase-design` |
| 内部で呼ぶ skill | なし（DESIGN-IT-TWICE.md でサブエージェントを 3 体以上起動する） |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

使う場面（`SKILL.md:3`）:

- module の interface を設計・改善したいとき。
- deep にする機会（deepening opportunity）を探すとき、seam をどこに置くか決めるとき。
- コードをテストしやすく、AI が辿りやすくしたいとき。
- 他の skill が deep module の語彙を必要とするとき。

使わない場面（解説ページ）:

- ドメインの言葉（「account」が 3 つの意味を持つ等）を揃えたい → [domain-modeling](domain-modeling.md)。
- どの module を直すべきかまだ分からない → [improve-codebase-architecture](improve-codebase-architecture.md)。
- 設計に反論してほしい → [grilling](grilling.md)。
- 単体で「進めて」と渡すこと。手順も停止条件も無いため、エージェントが独自の手順を作って長時間走る既知の問題がある（後述）。

## 4. 流れ

本体は語彙と原則であり、番号付きの手順は持たない。中身は次のとおり。

**用語（Glossary）**（`SKILL.md:12-28`）

| 用語 | 意味 | 避ける言葉 |
|---|---|---|
| Module | interface と implementation を持つもの全般。関数・クラス・パッケージ・層をまたぐ縦切りまで規模を問わない | unit, component, service |
| Interface | 正しく使うために呼び出し側が知るべきことの全部。型シグネチャに加え、不変条件・呼び出し順の制約・エラーの出方・必要な設定・性能特性 | API, signature |
| Implementation | module の中身。Adapter とは別概念 | — |
| Depth | interface での leverage。覚える interface あたりに使える振る舞いの量。deep / shallow | — |
| Seam | Michael Feathers の用語。その場所を編集せずに振る舞いを変えられる場所。interface が置かれる位置 | boundary |
| Adapter | seam で interface を満たす具体物。中身ではなく役割を指す | — |
| Leverage | depth から呼び出し側が得るもの | — |
| Locality | depth から保守する側が得るもの。変更・バグ・検証が 1 か所に集まる | — |

interface を設計するときは「メソッド数を減らせるか」「引数を単純にできるか」「もっと複雑さを中に隠せるか」を問う（`SKILL.md:54-58`）。

**原則**（`SKILL.md:62-65`）

1. depth は implementation ではなく interface の性質である。内部に seam を持ってよいが、interface に出さない。
2. 削除テスト（deletion test）。module を消したら複雑さが消えるなら素通し、N か所の呼び出し側に再出現するなら役に立っていた。
3. interface がテスト面である。interface の向こう側をテストしたくなるなら形が違う。
4. adapter が 1 つなら仮の seam、2 つなら本物の seam。変わるものが無ければ seam を作らない。

**テストしやすさ**（`SKILL.md:69-95`）: 依存は自分で作らず受け取る。副作用ではなく結果を返す。表面積を小さくする。

**退けた考え方**（`SKILL.md:107-109`）: Ousterhout の「実装行数 ÷ interface 行数」としての depth（実装の水増しを報いるため）、TypeScript の `interface` キーワードとしての interface、「boundary」という語。

**DEEPENING.md: 依存の 4 分類**（`DEEPENING.md:7-25`）

1. In-process: 純粋計算・メモリ内状態。常に deep にできる。統合して新 interface 越しにテストする。
2. Local-substitutable: ローカルの代替がある依存（Postgres に対する PGLite 等）。代替をテストで動かす。seam は内部に置く。
3. Remote but owned（Ports & Adapters）: 自前のネットワーク越しサービス。seam に port を定義し、本番は HTTP / gRPC / queue の adapter、テストはメモリ内 adapter。
4. True external（Mock）: 制御できない外部サービス。注入した port に、テストでは mock adapter を渡す。

テストは「重ねずに置き換える（replace, don't layer）」。deep にした module の interface にテストができたら、浅い module の古い単体テストは削除する（`DEEPENING.md:32-37`）。

**DESIGN-IT-TWICE.md: interface の複数案**（`DESIGN-IT-TWICE.md:9-44`）

1. 選んだ候補について、満たすべき制約・依存とその分類・制約を示すラフなコードをユーザー向けに説明し、すぐ次へ進む。
2. サブエージェントを 3 体以上並列に起動し、それぞれ根本的に違う interface を出させる。制約は「入口を 1〜3 に最小化」「柔軟性を最大化」「最も多い呼び出し側に最適化」「（該当すれば）ports & adapters 前提」。各案は interface・使用例・seam の裏に隠すもの・依存戦略・トレードオフを返す。
3. 案を順に示し、depth・locality・seam の位置で比較する。最後に自分の推奨（必要なら混成案）をはっきり述べる。

## 5. 書き込むもの・副作用

| 種類 | 内容 | 根拠 |
|---|---|---|
| サブエージェント | Design It Twice を使うとき 3 体以上を並列起動する | `DESIGN-IT-TWICE.md:21` |
| git / GitHub / ファイル | なし | `SKILL.md:1-114` に該当する指示が無い |

書き込みはなし。

## 6. 前後の skill

本 skill は本流の 1 段ではなく、設計系 skill の下にある語彙の層である（解説ページ）。

- 呼ばれる: [improve-codebase-architecture](improve-codebase-architecture.md) が語彙の取得と Design It Twice のために呼ぶ。
- 並ぶ: [domain-modeling](domain-modeling.md) はドメインの言葉、本 skill は module の形を扱う。両方を併用することが多い。
- 並ぶ: [tdd](tdd.md) は本 skill への参照を持つ（解説ページ）。

## 7. 注意点

- **単体で「進めて」と使わない**。手順も停止条件も無いため、エージェントが DESIGN-IT-TWICE.md の並列サブエージェントを手順代わりに走らせ、長時間トークンを使った報告がある（解説ページ、upstream issue #449）。[improve-codebase-architecture](improve-codebase-architecture.md)・[tdd](tdd.md) などの駆動役 skill から語彙として使う。
- **TypeScript での強制方法は示さない**。deep module の定義はあるが、interface を迂回する import を防ぐ仕組みは含まない（解説ページ）。
- **ファイル構成の規約ではない**。module は規模を問わない概念で、フォルダ構成とは独立している（解説ページ）。
- Design It Twice は Claude Code のサブエージェント機能を前提にしており、他のハーネスでは動きが変わりうる（解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| codebase-design/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| codebase-design/DEEPENING.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/DEEPENING.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| codebase-design/DESIGN-IT-TWICE.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design/DESIGN-IT-TWICE.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/codebase-design.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/codebase-design.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [improve-codebase-architecture](improve-codebase-architecture.md) / [domain-modeling](domain-modeling.md) / [tdd](tdd.md)
