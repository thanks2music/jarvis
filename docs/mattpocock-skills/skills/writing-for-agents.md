# writing-for-agents — agent が読む文書（skill、AGENTS.md / CLAUDE.md など）の書き方の参照資料

> 出典（一次情報）:
> - [writing-for-agents/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL.md) — skill 本体
> - [SKILL-MECHANICS.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL-MECHANICS.md) — skill 固有の事項（frontmatter、起動方式、router skill）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- agent が読む文書（skill、`AGENTS.md` / `CLAUDE.md`、ポインタから辿られる文書）を書くための参照資料である。手順ではなく、ほぼすべてが参照（reference）である（`SKILL.md:6`）。
- 目的は、agent が毎回同じ「過程」をたどるようにすること。同じ出力を出させることではない（`SKILL.md:6`）。
- 中心の考え方は 2 つの負荷。常時読み込まれる内容が agent のコンテキストに課す context load と、どの文書がいつ要るかを人間が覚える cognitive load である（`SKILL.md:20-27`）。
- 書いている文書が skill のときは、`SKILL-MECHANICS.md` も読む（`SKILL.md:8`）。
- 何も書き込まない。ファイルの作成・編集は、この skill を読んだ agent がユーザーの依頼に沿って行う。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:writing-for-agents` |
| 内部で呼ぶ skill | なし（skill を書くときは同梱の `SKILL-MECHANICS.md` を読む。`SKILL.md:8`） |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

- **自動で使われる**: skill を作る・編集するとき、`AGENTS.md` や `CLAUDE.md` を変更するとき（`SKILL.md:3`）。
- **手で呼ぶ**: それ以外で agent が読む文書。docs、spec、ticket、システムプロンプトなど（公式解説ページ）。
- **使わない**: コードベースに何があるかを調べる用途。この skill が扱うのは文書の書き方であり、中身ではない（公式解説ページ）。

## 4. 流れ

手順を持たない参照資料である。主な項目は次のとおり。

1. **context pointer**（`SKILL.md:10-18`）: 文脈内にあって、文脈外の資料を名指しし、いつ辿るかを表す参照。skill の description も、`AGENTS.md` 内で文書を名指しする行も同じものである。辿られるかどうかは、参照先ではなくポインタの文言で決まる。
   - 決め手になる語（leading word）を先頭に置く。
   - 分岐（branch）1 つにつき起動条件は 1 つ。同義語は 1 つにまとめる。
   - 本文が既に持つ説明は削る。
2. **2 つの負荷（The two loads）**（`SKILL.md:20-27`）: context load は常時読み込まれる内容のコスト。cognitive load は人間側のコストで、最小化の対象ではなく、人間の判断が要る所に使うものである。
3. **情報の階層（Information hierarchy）**（`SKILL.md:29-43`）: 文書は手順（steps）と参照（reference）でできている。置き場所は、ファイル内の手順 → ファイル内の参照 → ポインタの先の別ファイル（disclosed reference）の順に下がる。
   - **progressive disclosure**: 一部の分岐だけが使う内容を下の段へ移し、上を読みやすく保つ。
   - **co-location**: 1 つの概念の定義・規則・注意を 1 つの見出しの下にまとめる。
   - **sprawl**: 文書が長すぎる失敗。階層で直す。
4. **手順と完了条件（Steps and completion criteria）**（`SKILL.md:45-52`）: 各手順は完了条件で終える。曖昧だと早すぎる完了（premature completion）を招く。まず条件を明確にし、それでも駄目なら後続の手順を見えなくする（セッションの引き継ぎかサブエージェントへの委任が必要）。条件の要求度（demand）が、agent がどこまで調べるか（legwork）を決める。
5. **分割の判断（When to split）**（`SKILL.md:54-59`）: 後続の手順が今の手順を急がせるときは順序で分ける。起動方式で分ける場合は `SKILL-MECHANICS.md` に従う。
6. **leading word**（`SKILL.md:61-74`）: 事前学習に既にある簡潔な概念（例: _tight_、_red_、_tracer bullets_）を繰り返し使い、少ないトークンで振る舞いを固定する。禁止で導く（negation）と、禁じた振る舞いがかえって想起されやすい。してほしいことを肯定形で書く。
7. **刈り込み（Pruning）**（`SKILL.md:76-81`）: 1 つの意味は 1 か所に（single source of truth）。`package.json` や設定ファイルで分かることは書かない。古くなった行（sediment）を削る。既定の振る舞いを繰り返すだけの文（no-op）は文ごと消す。

### SKILL-MECHANICS.md（skill を書くときだけ読む）

- **model-invoked**: `disable-model-invocation` を省き、起動条件を含む description を書く。常時の context load と引き換えに、agent や他 skill から呼べる（`SKILL-MECHANICS.md:9`）。
- **user-invoked**: `disable-model-invocation: true` にする。description は人間向けの 1 行にする。context load は無いが、人間が存在を覚えておく必要がある（`SKILL-MECHANICS.md:10`）。
- 手で呼ぶだけなら user-invoked にする（`SKILL-MECHANICS.md:12`）。
- user-invoked の skill が増えすぎたら、他の skill の名前と使いどころを並べる router skill を 1 つ作る（`SKILL-MECHANICS.md:20-22`）。

## 5. 書き込むもの・副作用

- なし。`SKILL.md` と `SKILL-MECHANICS.md` は参照資料であり、ファイル書き込み・git・GitHub の操作を指示していない（`SKILL.md:6`, `SKILL-MECHANICS.md:3`）。

## 6. 前後の skill

- 単独の参照資料で、この skill 群全体に適用される（公式解説ページ）。
- [retro](retro.md) が、最初の手順でこの skill を Skill ツールで読み込む（`retro/SKILL.md:11`）。retro が skill や steering file を提案する際の書き方の基準になる（`retro/SKILL.md:44`）。
- [setup-matt-pocock-skills](setup-matt-pocock-skills.md) が `CLAUDE.md` / `AGENTS.md` に書く `## Agent skills` ブロックも、この skill の対象となる文書である（推測）。

## 7. 注意点

- **常時読み込まれる**: model-invoked のため、description（`SKILL.md:3`）は常にコンテキストに載る。これは `SKILL-MECHANICS.md:9` が説明する context load そのものである。
- **旧名**: v1.1 までは `writing-great-skills` という名前だった。別名は無い（公式解説ページ）。
- **自動評価は無い**: 文書を実際に動かし、本 skill の失敗の語彙（duplication、sediment、no-op など）で診断する（公式解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| SKILL-MECHANICS.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL-MECHANICS.md （同上） |
| retro/SKILL.md（呼び出し元） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro/SKILL.md （同上） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/writing-for-agents.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [retro](retro.md) / [setup-matt-pocock-skills](setup-matt-pocock-skills.md)
