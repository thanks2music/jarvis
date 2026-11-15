# domain-modeling — 用語を詰めて GLOSSARY.md と ADR に書き込む

> 出典（一次情報）:
> - [domain-modeling/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/SKILL.md) — skill 本体
> - [domain-modeling/GLOSSARY-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/GLOSSARY-FORMAT.md) — `GLOSSARY.md` / `GLOSSARY-MAP.md` の書式
> - [domain-modeling/ADR-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/ADR-FORMAT.md) — ADR の書式と書く基準
> - [docs/engineering/domain-modeling.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/domain-modeling.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 設計しながら、プロジェクトのドメインモデル（用語）を積極的に作り、鋭くする skill である（`SKILL.md:8`）。
- 用語の食い違いを指摘し、曖昧な言葉に正式名を提案し、シナリオとコードで境界を確かめる（`SKILL.md:44-58`）。
- 用語が決まった瞬間に `GLOSSARY.md` に書く。まとめ書きはしない（`SKILL.md:62`）。
- ADR は「戻しにくい」「文脈なしでは意外」「本当のトレードオフ」の 3 条件がそろったときだけ提案する（`SKILL.md:68-74`）。
- `GLOSSARY.md` を読むだけならこの skill は不要。モデルを変えるときに使う（`SKILL.md:8`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし。`SKILL.md:1-4`） |
| 呼び出し方 | `/mattpocock-skills:domain-modeling` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（`GLOSSARY.md`、`docs/adr/NNNN-slug.md`） |

## 3. いつ使うか・使わないか

使う場面（`SKILL.md:3`、`docs/engineering/domain-modeling.md:13-20`）:

- コードベースの用語を議論するとき。
- `GLOSSARY.md` を書く・直すとき。ADR を記録する・直すとき。
- 同じ言葉（例: 「cancellation」）を人によって違う意味で使っている。
- 1 つの言葉（例: 「account」）が複数の役割を担っている。

使わない場面:

- 用語を調べたいだけ → `GLOSSARY.md` を読めばよい（`SKILL.md:8`）。
- モジュールの形（seam の位置、interface の深さ）が問題 → [codebase-design](codebase-design.md)（`docs/engineering/domain-modeling.md:18`）。
- 計画全体を問い詰めたい → [grill-with-docs](grill-with-docs.md)（この skill を内部で使う）。

## 4. 流れ

1. **構成を判断する**（`SKILL.md:12-38`、`GLOSSARY-FORMAT.md:54-60`）
   - ルートに `GLOSSARY-MAP.md` があれば複数文脈（multi-context）。map を読み、話題に合う文脈の `GLOSSARY.md` を使う。分からなければ利用者に聞く。
   - ルートに `GLOSSARY.md` だけがあれば単一文脈。
   - どちらも無ければ、最初の用語が決まったときにルートの `GLOSSARY.md` を作る。
2. **用語集と照らし合わせる（challenge against the glossary）**: 既存の定義と違う意味で使われたら、すぐ指摘する（`SKILL.md:44-46`）。
3. **曖昧な言葉を鋭くする（sharpen fuzzy language）**: 正確な正式名を提案する。例: 「account」は Customer か User か（`SKILL.md:48-50`）。
4. **具体的なシナリオで試す**: 端のケースを作り、概念の境界をはっきりさせる（`SKILL.md:52-54`）。
5. **コードと照らし合わせる**: 発言とコードが食い違えば指摘する（`SKILL.md:56-58`）。
6. **`GLOSSARY.md` をその場で更新する**: 書式は `GLOSSARY-FORMAT.md` に従う（`SKILL.md:60-62`）。
   - 1 つの概念に複数の言葉があれば 1 つを選び、残りを `_Avoid_` に並べる（`GLOSSARY-FORMAT.md:27`）。
   - 定義は 1〜2 文。何をするかでなく、何であるかを書く（`GLOSSARY-FORMAT.md:28`）。
   - 一般的なプログラミング概念は入れない（`GLOSSARY-FORMAT.md:29`）。
   - 実装の詳細は書かない。仕様書・メモ帳・実装判断の置き場にしない（`SKILL.md:64`）。
7. **ADR は控えめに提案する**: 3 条件がそろったときだけ（`SKILL.md:66-74`）。
   - 置き場所は `docs/adr/`、名前は `0001-slug.md` の連番。既存の最大番号に 1 を足す（`ADR-FORMAT.md:3`, `ADR-FORMAT.md:25-27`）。
   - 本文は題と 1〜3 文（文脈・決定・理由）で足りる。Status・Considered Options・Consequences は価値があるときだけ付ける（`ADR-FORMAT.md:7-23`）。
   - 対象の例: アーキテクチャの形、文脈間の連携方式、乗り換えの重い技術選定、境界と範囲、意図的な定石外し、コードに現れない制約、理由が自明でない却下案（`ADR-FORMAT.md:39-47`）。

## 5. 書き込むもの・副作用

| 書き込み先 | タイミング | 根拠 |
|---|---|---|
| `GLOSSARY.md`（ルート、または `GLOSSARY-MAP.md` が指す文脈ごとのファイル） | 用語が決まった瞬間。無ければその時に新規作成 | `SKILL.md:40`, `SKILL.md:62`、`GLOSSARY-FORMAT.md:54-58` |
| `docs/adr/` ディレクトリ | 最初の ADR が必要になったとき | `SKILL.md:40`、`ADR-FORMAT.md:5` |
| `docs/adr/NNNN-slug.md` | 3 条件を満たす決定について ADR を提案したとき | `SKILL.md:66-74`、`ADR-FORMAT.md:3`, `ADR-FORMAT.md:27` |

- ファイルは中身ができたときだけ作る（lazily）。前もって作らない（`SKILL.md:40`）。
- `GLOSSARY-MAP.md` を作る・直す手順は SKILL.md に無い。既存の map を読むだけである（`GLOSSARY-FORMAT.md:56`）。
- git commit / push / GitHub への書き込みはしない（SKILL.md・参照ファイルに記述なし）。

## 6. 前後の skill

- 他の skill の下で動く語彙の層（vocabulary underneath）である（ask-matt `SKILL.md:62-66`）。
- 呼び出し元: [grill-with-docs](grill-with-docs.md)（`grill-with-docs/SKILL.md:7`）。解説ページでは [wayfinder](wayfinder.md)、[triage](triage.md)、[improve-codebase-architecture](improve-codebase-architecture.md) も使うとされる（`docs/engineering/domain-modeling.md:86`）。
- 兄弟: [codebase-design](codebase-design.md)（モジュールの形の語彙）。
- 書いた `GLOSSARY.md` は [wait-what](wait-what.md) が言い直しで使う（`wait-what/SKILL.md:7`）。

## 7. 注意点

- **自動起動されにくい**: grill-with-docs などが読み込みを指示しても、モデルが grilling だけ読み込み、この skill を飛ばすことが多い。セッション後に `GLOSSARY.md` が変わっていなければこれが原因である。他の skill と一緒に名前で起動する（`docs/engineering/domain-modeling.md:9`）。
- **`GLOSSARY.md` が肥大化しやすい**: モデルが回答をすべて書き込み、仕様書のようになる。`/mattpocock-skills:grill-with-docs make my GLOSSARY.md more concise and remove any implementation details from it` のように直接指示して削る（`docs/engineering/domain-modeling.md:44`, `docs/engineering/domain-modeling.md:55`）。
- **issue tracker は見ない**: 照合するのはコード・`GLOSSARY.md`・ADR だけである。過去の issue で決着済みの命名を、新しい問題として蒸し返すことがある（`docs/engineering/domain-modeling.md:50`）。
- **独自の ADR 書式とは衝突する**: 既存の書式・置き場所があるチームは、repo のエージェント向け文書で上書きする（`docs/engineering/domain-modeling.md:67`）。
- git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| domain-modeling/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| domain-modeling/GLOSSARY-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/GLOSSARY-FORMAT.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| domain-modeling/ADR-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/ADR-FORMAT.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/domain-modeling.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/domain-modeling.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grill-with-docs](grill-with-docs.md) / [codebase-design](codebase-design.md) / [wait-what](wait-what.md)
