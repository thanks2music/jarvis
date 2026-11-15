# grilling — 設計の木をラウンド単位で問い詰める interview の本体

> 出典（一次情報）:
> - [grilling/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling/SKILL.md) — skill 本体
> - [docs/productivity/grilling.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/grilling.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 計画・決定・アイデアを、共通理解に達するまで問い詰める interview の本体（primitive）である（`SKILL.md:3`, `SKILL.md:6`）。
- 対象を設計の木（design tree）にし、前提が決まった問い（frontier）をまとめて 1 ラウンドで聞く（`SKILL.md:6-8`）。
- 各問いに番号と推奨回答を付ける。「yes」で推奨回答を受け入れられる聞き方にする（`SKILL.md:8-24`）。
- 事実はエージェントが調べ、決定は利用者が下す（`SKILL.md:28`）。
- frontier が空になり、利用者が確認するまで実行に移らない（`SKILL.md:30`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし。「grill」を含む言い回しでも起動する。`SKILL.md:3`） |
| 呼び出し方 | `/mattpocock-skills:grilling` |
| 内部で呼ぶ skill | なし（事実調査のためサブエージェントを起動する。`SKILL.md:28`） |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

使う場面:

- 計画・決定・アイデアを、実行前に試したい（`SKILL.md:3`）。
- 包みのない素の interview だけがほしい（ask-matt `SKILL.md:86`）。
- 自作 skill の中で interview が必要なとき。interview を書き直さず、grilling を呼ぶ（`docs/productivity/grilling.md:19`）。

ほかの入口を選ぶ場面（`docs/productivity/grilling.md:13-19`）:

- 作業ディレクトリが無い → [grill-me](grill-me.md)
- 作業ディレクトリがあり、用語集と ADR も残したい → [grill-with-docs](grill-with-docs.md)
- 1 セッションに収まらない → [wayfinder](wayfinder.md)
- 会話で決まらない（見た目や触り心地）→ [prototype](prototype.md)

## 4. 流れ

1. **設計の木を描く**: どの決定も、そこからぶら下がる決定に枝分かれする（`SKILL.md:6`）。
2. **frontier を求める**: 前提がすべて決まった決定の集まりを frontier とする。まだ聞いていない答えを推測しなくても聞ける問いだけを含む（`SKILL.md:8`）。
3. **1 ラウンドで frontier を全部聞く**: 各問いに番号を振り、推奨回答を付ける。利用者の回答を待ってから次のラウンドに進む（`SKILL.md:8`）。書式は次のとおり（`SKILL.md:10-22`）。

   ```
   ❓ **Q1** - **<問いの題>**: <本文。選択肢を含んでもよい>

   ➡️ <推奨回答>
   ```

4. **聞き方**: 「yes」と答えれば推奨回答を受け入れたことになるように問いを書く（`SKILL.md:24`）。
5. **frontier を計算し直す**: 回答で決まった決定は frontier を外へ押し広げる。同じラウンドで未決の問いに依存する問いは、後のラウンドに回す（`SKILL.md:26`）。
6. **事実と決定を分ける**: 環境（ファイルシステム、ツール）から分かる事実は、サブエージェントを出して調べる。利用者には聞かない。調査中でも待たずに、その結果に依存しない問いを先に聞く。決定は利用者に聞き、回答を待つ（`SKILL.md:28`）。
7. **終わり方**: frontier が空になったら終わる。設計の木のすべての枝を訪れ、暗黙の前提が残っていない状態である。利用者が「共通理解に達した」と確認するまで、その内容に基づいて動かない（`SKILL.md:30`）。

## 5. 書き込むもの・副作用

なし。ファイル・git・GitHub への書き込みの指示は無い。事実を調べるためにサブエージェントを起動する（`SKILL.md:28`）。実行に移るのは利用者の確認後である（`SKILL.md:30`）。

## 6. 前後の skill

- 予定に組み込む手順ではなく、interview の唯一の正本（primitive）である（`docs/productivity/grilling.md:87`）。
- ユーザー向けの入口: [grill-me](grill-me.md)（`grill-me/SKILL.md:7`）、[grill-with-docs](grill-with-docs.md)（`grill-with-docs/SKILL.md:7`）。
- 内部で使う skill: [triage](triage.md)、[wayfinder](wayfinder.md)、[improve-codebase-architecture](improve-codebase-architecture.md)（ask-matt `SKILL.md:86`）。
- grill-with-docs 経由のときは、その後 [to-spec](to-spec.md) へ進む（ask-matt `SKILL.md:25`）。

## 7. 注意点

- **1 問ずつに戻したい場合**: グローバルの `CLAUDE.md` に `When grilling, ask one question at a time.` と書く。公式に支持された設定である（`docs/productivity/grilling.md:46-52`）。
- **質問数の上限は設けられない**: 長すぎるときは「まとめて」と言うか、範囲を分けて grill し直す（`docs/productivity/grilling.md:67`）。
- **確認せずに実装を始めることがある**: 弱いモデルや低い effort で起きやすい。`AGENTS.md` / `CLAUDE.md` に「許可なく実装しない」と書くと確実である（`docs/productivity/grilling.md:61`）。
- **自分で決定を答えてしまうことがある**: 他の skill の中で動くときに起きやすい。実行上の不具合である（`docs/productivity/grilling.md:64`）。
- **推奨回答と問いの向きが逆になることがある**: 推奨に同意すると「no」になる場合は、その旨を書いて答える（`docs/productivity/grilling.md:27`）。
- git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| grilling/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/productivity/grilling.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/grilling.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grill-me](grill-me.md) / [grill-with-docs](grill-with-docs.md) / [domain-modeling](domain-modeling.md)
