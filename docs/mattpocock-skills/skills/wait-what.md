# wait-what — 分からなかった説明を、文脈を足して平易に言い直させる

> 出典（一次情報）:
> - [wait-what/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/wait-what/SKILL.md) — skill 本体
> - [docs/productivity/wait-what.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/wait-what.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- エージェントの直前の説明が分からなかったときに打つ（`SKILL.md:3`）。
- エージェントは、足りなかった文脈を加えて言い直す（re-pitch）（`SKILL.md:7`）。解説ページは「plain English で書く」と説明する（`docs/productivity/wait-what.md:3`）。
- 文体は ASD-STE100 Simplified Technical English、名詞は `GLOSSARY.md` の用語（ubiquitous language）を使う（`SKILL.md:7`）。
- 本文は 1 文だけで、短いこと自体が設計である（`docs/productivity/wait-what.md:5`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーのみ（`/mattpocock-skills:wait-what` で起動。`SKILL.md:4` が `disable-model-invocation: true`） |
| 呼び出し方 | `/mattpocock-skills:wait-what` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

使う場面（`docs/productivity/wait-what.md:11`）:

- 説明を読み飛ばし始めたと気付いたとき。
- エージェントが自作の専門用語を使い始めた、1 文に略語を詰め込んだ、知らない前提で判断を説明した、といったとき。
- 会話中ならいつでも、他の skill の実行中でも使える（ask-matt `SKILL.md:91`）。

使わない場面:

- そもそも専門用語が出ないようにしたい → 先に [grill-with-docs](grill-with-docs.md) で共通の用語を決める（ask-matt `SKILL.md:91`）。

## 4. 流れ

SKILL.md は、利用者の発言としてエージェントに次を伝える 1 文である（`SKILL.md:7`）。

1. **止める**: 「ここまでの話が分からない」と伝える。
2. **言い直させる（re-pitch）**: 少し文脈を足して説明し直させる。どこまで遡るかはエージェントが決める（`docs/productivity/wait-what.md:19`）。
3. **文体を指定する**: ASD-STE100 Simplified Technical English で書かせる。
4. **用語を指定する**: `GLOSSARY.md` の用語を使わせる。repo に複数の文脈があれば、`GLOSSARY-MAP.md` をたどって該当する `GLOSSARY.md` を使わせる。

`GLOSSARY.md` が無くても動く。その場合はドメイン用語の部分だけが効かない（`docs/productivity/wait-what.md:25`）。

## 5. 書き込むもの・副作用

なし。`GLOSSARY.md` / `GLOSSARY-MAP.md` を読むだけである（`SKILL.md:7`）。

## 6. 前後の skill

- main flow の外の standalone で、会話のどこでも使う修正手段である（ask-matt `SKILL.md:91`）。
- 根本的な対策は [grill-with-docs](grill-with-docs.md)（その中の [domain-modeling](domain-modeling.md)）で、共通の用語を `GLOSSARY.md` に先に決めておくことである（`docs/productivity/wait-what.md:36`）。

## 7. 注意点

- **言い直しは英語になる（推測）**: SKILL.md が指定する ASD-STE100 は英語の規格で、解説ページも「plain English」と書く（`docs/productivity/wait-what.md:3`）。日本語で会話している場合に出力言語がどうなるかは SKILL.md に記述が無い。日本語がほしいときは、起動時に一言添える（推測）。
- **「簡潔に」とは違う**: 出力を短くする指示ではなく、聞き手が分からなくなったことを伝える skill である。短くて分かりやすい説明が返るのが正常で、短くてそっけないだけなら機能していない（`docs/productivity/wait-what.md:15`, `docs/productivity/wait-what.md:29`）。
- **エージェントは自分では起動しない**: 分からなくなったのは利用者にしか分からないためである（`docs/productivity/wait-what.md:9`）。
- git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| wait-what/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/wait-what/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/productivity/wait-what.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/wait-what.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grill-with-docs](grill-with-docs.md) / [domain-modeling](domain-modeling.md) / [ask-matt](ask-matt.md)
