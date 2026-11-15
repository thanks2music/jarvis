# grill-me — 何も保存しない interview で計画やアイデアを固める

> 出典（一次情報）:
> - [grill-me/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grill-me/SKILL.md) — skill 本体
> - [docs/productivity/grill-me.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/grill-me.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 本体は 1 行で、[grilling](grilling.md) を呼ぶだけである（`SKILL.md:7`）。
- stateless で、ファイルを何も書かない。結果は利用者の頭の中にだけ残る（`docs/productivity/grill-me.md:5`）。
- repo が無い場面（計画、設計、文章、事業判断など）で使う。repo があるなら [grill-with-docs](grill-with-docs.md) の方が良い（ask-matt `SKILL.md:85`）。
- grilling はモデルも自動で使えるが、grill-me はユーザーが打ったときだけ動く入口である。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーのみ（`/mattpocock-skills:grill-me` で起動。`SKILL.md:4` が `disable-model-invocation: true`） |
| 呼び出し方 | `/mattpocock-skills:grill-me` |
| 内部で呼ぶ skill | [grilling](grilling.md)（`SKILL.md:7`） |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

使う場面:

- 作業ディレクトリ（repo）が無いところで、計画・設計・文章などを詰めたい（ask-matt `SKILL.md:85`）。
- 真剣に考える価値のあるアイデアが出た直後。曖昧なままでよく、曖昧さを取り除くのがこの skill の役目である（`docs/productivity/grill-me.md:11`）。
- 対象はコードでなくてもよい（`docs/productivity/grill-me.md:15`）。

使わない場面:

- repo の中にいる → [grill-with-docs](grill-with-docs.md)（ask-matt `SKILL.md:85`）。
- 1 セッションに収まらない → [wayfinder](wayfinder.md)（`docs/productivity/grill-me.md:17`）。
- すでに正確に仕様を書ける → grilling は不要（`docs/productivity/grill-me.md:11`）。

## 4. 流れ

grill-me は grilling を起動するだけなので、流れは grilling と同じである（`SKILL.md:7`）。

1. 対象を設計の木（design tree）として捉える（grilling `SKILL.md:6`）。
2. 前提が決まった問い（frontier）をまとめて 1 ラウンドで聞く。各問いに番号と推奨回答を付ける。「yes」で推奨回答を受け入れられる聞き方にする（grilling `SKILL.md:8-24`）。
3. 回答を受けて frontier を計算し直し、次のラウンドを聞く（grilling `SKILL.md:26`）。
4. 事実は自分で調べ、決定は利用者に聞く（grilling `SKILL.md:28`）。
5. frontier が空になったら終わる。利用者が確認するまで、決めた内容に基づいて動かない（grilling `SKILL.md:30`）。

解説ページの補足（`docs/productivity/grill-me.md:9`, `docs/productivity/grill-me.md:19`）:

- 新しい会話で始める。エージェントにすでに書かせた計画の上で始めない。
- plan mode は切っておく。plan mode だとエージェントが計画作成を急ぐ。

## 5. 書き込むもの・副作用

なし。grill-me 本体は grilling を呼ぶだけで（`SKILL.md:7`）、grilling も書き込みの指示を持たない。事実を調べるためにサブエージェントを起動することはある（grilling `SKILL.md:28`）。

## 6. 前後の skill

- main flow の外にある standalone である（ask-matt `SKILL.md:81-85`）。
- 対象がソフトウェアだった場合は、同じ会話を [to-spec](to-spec.md) に渡して main flow に合流できる（`docs/productivity/grill-me.md:65`, `docs/productivity/grill-me.md:76`）。
- 会話で決まらない問い（見て判断する UI など）は [prototype](prototype.md) に回す（`docs/productivity/grill-me.md:35`）。
- 他人の知識が必要なら [to-questionnaire](to-questionnaire.md)（ask-matt `SKILL.md:89`）。

## 7. 注意点

- **grilling が必要**: grill-me だけ入れても動かない（`docs/productivity/grilling.md:70`）。
- **受け身で答えない**: 「agreed」を繰り返すと、エージェントが書いた計画にうなずいただけになる。範囲がずれたら指摘し、分からなければ「分からない」と答える（`docs/productivity/grill-me.md:25-27`）。
- **1 問ずつに戻したい場合**: グローバルの `CLAUDE.md` に `When grilling, ask one question at a time.` と書く（`docs/productivity/grill-me.md:55-59`）。
- **質問が多すぎる場合**: 範囲が広すぎることが多い。先に小さく分けてから grill する（`docs/productivity/grill-me.md:52`）。
- **モデルの質が効く**: 最良のモデルを使う（`docs/productivity/grill-me.md:68`）。
- git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| grill-me/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grill-me/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| grilling/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/productivity/grill-me.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/grill-me.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grilling](grilling.md) / [grill-with-docs](grill-with-docs.md) / [ask-matt](ask-matt.md)
