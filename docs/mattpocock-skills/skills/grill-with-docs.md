# grill-with-docs — interview で計画を固め、用語集と ADR を repo に残す

> 出典（一次情報）:
> - [grill-with-docs/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/grill-with-docs/SKILL.md) — skill 本体
> - [docs/engineering/grill-with-docs.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/grill-with-docs.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 本体は 1 行で、[grilling](grilling.md) と [domain-modeling](domain-modeling.md) の 2 つの skill を呼ぶだけである（`SKILL.md:7`）。
- interview は grilling、用語集と ADR の書き込みは domain-modeling が担う。
- [grill-me](grill-me.md) と同じ interview だが、stateful で、repo に `GLOSSARY.md` と `docs/adr/` を残す（`SKILL.md:3`）。
- 作業ディレクトリ（repo）がある場合の main flow の入口である（ask-matt `SKILL.md:19`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:grill-with-docs` で起動。`SKILL.md:4` が `disable-model-invocation: true`） |
| 呼び出し方 | `/mattpocock-skills:grill-with-docs` |
| 内部で呼ぶ skill | [grilling](grilling.md)、[domain-modeling](domain-modeling.md)（`SKILL.md:7`） |
| 外部への書き込み | ファイル（`GLOSSARY.md`、`docs/adr/NNNN-slug.md`。domain-modeling 経由） |

## 3. いつ使うか・使わないか

使う場面:

- repo の中で、計画や設計がまだ曖昧で、用語も定まっていない変更の最初（`docs/engineering/grill-with-docs.md:11`）。
- ドメイン文書が何も無い既存 repo で、用語集を作りたいとき。「help me document my repo」と添えて起動する（`docs/engineering/grill-with-docs.md:58`）。

使わない場面（`docs/engineering/grill-with-docs.md:13-19`）:

- 作業ディレクトリが無い → [grill-me](grill-me.md)
- 1 セッションに収まらない大きな取り組み → [wayfinder](wayfinder.md)
- 他人の頭の中にある知識が足りない → [to-questionnaire](to-questionnaire.md)

## 4. 流れ

SKILL.md 自体は「Skill tool を 2 回呼ぶ。`grilling` と `domain-modeling`」とだけ書く（`SKILL.md:7`）。実際の流れは 2 つの skill の組み合わせになる。

1. **grilling を読み込む**: 計画を設計の木（design tree）として捉え、前提が決まった問い（frontier）を 1 ラウンドにまとめて聞く。各問いに推奨回答を付ける（grilling `SKILL.md:6-24`）。
2. **domain-modeling を読み込む**: interview 中に用語を詰める（grilling と並行して働く）。
   - 既存の `GLOSSARY.md` と食い違う用語は、すぐに指摘する（domain-modeling `SKILL.md:44-46`）。
   - 曖昧な用語には、正確な正式名（canonical term）を提案する（同 `SKILL.md:48-50`）。
   - 具体的なシナリオで境界を確かめる。コードと発言が食い違えば指摘する（同 `SKILL.md:52-58`）。
3. **用語が決まったら、その場で `GLOSSARY.md` に書く**。まとめ書きはしない（domain-modeling `SKILL.md:60-62`）。
4. **ADR は条件を満たすときだけ提案する**。条件は「戻しにくい」「文脈なしでは意外」「本当のトレードオフの結果」の 3 つ全部（domain-modeling `SKILL.md:66-74`）。
5. **事実は調べる、決定は利用者に聞く**。環境から分かる事実はサブエージェントで調べる（grilling `SKILL.md:28`）。
6. **frontier が空になったら終わる**。利用者が「理解が共有できた」と確認するまで、決めた内容に基づいて動かない（grilling `SKILL.md:30`）。

## 5. 書き込むもの・副作用

grill-with-docs 自身は何も書かない。書き込みはすべて domain-modeling による。

| 書き込み先 | タイミング | 根拠 |
|---|---|---|
| `GLOSSARY.md`（repo ルート、または `GLOSSARY-MAP.md` が指す文脈ごとのファイル） | 用語が決まった瞬間。無ければその時に作る | domain-modeling `SKILL.md:40`, `SKILL.md:62`、`GLOSSARY-FORMAT.md:54-58` |
| `docs/adr/NNNN-slug.md` | 3 条件を満たす決定があり、ADR を提案したとき。ディレクトリは最初の ADR の時に作る | domain-modeling `SKILL.md:40`, `SKILL.md:66-74`、`ADR-FORMAT.md:3-5` |
| サブエージェントの起動 | 事実の調査が必要なとき（調査のみ） | grilling `SKILL.md:28` |

git commit / push / GitHub への書き込みはしない（SKILL.md・参照ファイルに記述なし）。

## 6. 前後の skill

main flow の先頭である（`docs/engineering/grill-with-docs.md:76-80`）。

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

- 前: [research](research.md) の調査結果や [improve-codebase-architecture](improve-codebase-architecture.md) で見つけた改善候補を持ち込める（ask-matt `SKILL.md:60`, `SKILL.md:88`）。[wayfinder](wayfinder.md) が地図の一部を渡してくることもある。
- 後: 同じ会話のまま [to-spec](to-spec.md) へ進む。小さな変更なら [implement](implement.md) へ直接進む（`docs/engineering/grill-with-docs.md:61`）。
- 会話だけで決まらない問いは [prototype](prototype.md) に回す（ask-matt `SKILL.md:20-23`）。

## 7. 注意点

- **依存 skill が必要**: grilling と domain-modeling が無いと動かない（`docs/engineering/grill-with-docs.md:27`）。
- **依存 skill を読み込み損ねる既知の不具合**: 全部の問いを一度に、推奨回答なしで聞いてくる場合は、grilling を読み込めていない。interview は良いのに `GLOSSARY.md` が変わらない場合は、domain-modeling を読み込めていない。エージェントに「どの skill を読み込んだか」と直接聞くと回復することが多い（`docs/engineering/grill-with-docs.md:52`）。
- **ファイルが残らない場合もある**: 新しい用語も 3 条件を満たす決定も無ければ、何も書かれないのが正しい動作である。また、他のオーケストレーション層の中で動かすと書き込みだけ起きない不具合が報告されている（`docs/engineering/grill-with-docs.md:49`）。
- **決めた内容の大半は会話にしか残らない**: `GLOSSARY.md` は用語集で、仕様書ではない。セッションを `/clear` せず、そのまま to-spec に渡す（`docs/engineering/grill-with-docs.md:39`, `docs/engineering/grill-with-docs.md:55`）。Zed の外部エージェント（ACP）経由では `/clear` が使えないので、誤ってスレッドを閉じないよう注意する。
- **作業場所**: repo に直接書き込むので、書き込んでよいブランチ・ディレクトリで起動する（`docs/engineering/grill-with-docs.md:25`）。git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| grill-with-docs/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/grill-with-docs/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| grilling/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| domain-modeling/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/grill-with-docs.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/grill-with-docs.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grilling](grilling.md) / [domain-modeling](domain-modeling.md) / [grill-me](grill-me.md) / [to-spec](to-spec.md)
