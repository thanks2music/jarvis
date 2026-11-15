# handoff — 今の会話を、別の agent が引き継げる文書に圧縮する skill

> 出典（一次情報）:
> - [handoff/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/handoff/SKILL.md) — skill 本体
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 現在の会話を要約し、新しい agent が作業を続けられる引き継ぎ文書（handoff document）を書く（`SKILL.md:8`）。
- 保存先は OS の一時ディレクトリ（`$TMPDIR`、無ければ `/tmp`、Windows は `%TEMP%`）。ワークスペースには書かない（`SKILL.md:8`）。
- 次の agent が呼ぶべき skill を「suggested skills」セクションに書く（`SKILL.md:10`）。
- spec・計画・ADR・issue・commit・diff など、既に別の成果物にある内容は複製せず、パスか URL で参照する（`SKILL.md:12`）。
- 引数で「次のセッションの用途」を渡すと、その用途に合わせて書く（`SKILL.md:4`, `SKILL.md:16`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーのみ（`/mattpocock-skills:handoff` で起動）。`disable-model-invocation: true`（`SKILL.md:5`） |
| 呼び出し方 | `/mattpocock-skills:handoff [次のセッションの用途]` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（OS の一時ディレクトリに markdown を 1 つ） |

## 3. いつ使うか・使わないか

SKILL.md は用途を限定していない。公式解説ページと [ask-matt](ask-matt.md) は、次の 4 つの場面に限るとしている（`ask-matt/SKILL.md:75`、`ask-matt/PHASE-BOUNDARIES.md:27-34`）。

| 場面 | ファイルが要る理由 |
|---|---|
| ハーネスを替える（例: Claude Code → Codex） | 新しいハーネスは前のコンテキストを見られない |
| 別のディレクトリやリポジトリに移る | prototype 用ディレクトリが典型 |
| 同僚に作業を渡す | 相手が読めるものが要る |
| フェーズの途中で見つけた脇道を分岐させる | 自分は作業を続け、別の agent が脇道を担う |

- **使わない**: 同じハーネス・同じディレクトリで続けるなら、`/compact` で足りる（公式解説ページ）。

## 4. 流れ

SKILL.md は手順を番号付きで書いていない。指示を順に並べると次のとおりである。

1. 引数があれば、次のセッションが何に集中するかの説明として扱い、内容をそれに合わせる（`SKILL.md:16`）。
2. 新しい agent が作業を続けられるよう、現在の会話を要約した引き継ぎ文書を書く（`SKILL.md:8`）。
3. 次の agent が Skill ツールで呼ぶべき skill を「suggested skills」セクションに挙げる（`SKILL.md:10`）。
4. 既存の成果物（spec、計画、ADR、issue、commit、diff）は複製せず、パスか URL で参照する（`SKILL.md:12`）。
5. API キー、パスワード、個人を特定できる情報などの機微情報を伏せる（`SKILL.md:14`）。
6. OS の一時ディレクトリに保存する（`SKILL.md:8`）。

## 5. 書き込むもの・副作用

| 書き込み先 | 内容 | 根拠 |
|---|---|---|
| `$TMPDIR`（無ければ `/tmp`、Windows は `%TEMP%`） | 引き継ぎ文書（markdown 1 ファイル） | `SKILL.md:8` |

- 現在のワークスペース（リポジトリ）には書かない（`SKILL.md:8`）。
- git commit・branch・push、GitHub issue・ラベルへの操作はない（SKILL.md に記述なし）。
- ファイル名の規則は SKILL.md に無い。

## 6. 前後の skill

- 決まった流れの中の 1 段ではなく、セッションとセッションの間で使う単独の skill である（公式解説ページ）。
- [prototype](prototype.md): 設計の会話中に「動かさないと決まらない問い」が出たら、`/handoff` で prototype 用セッションに渡し、結果を `/handoff` で元の会話に戻す（`ask-matt/SKILL.md:20-23`）。
- [teach](teach.md): grilling 中に理解できない話題が出たら、`/handoff` で学習用ワークスペースに移り、そこで `/teach` で学ぶ（公式解説ページ）。
- 引き継ぎ先の agent には、文書の「suggested skills」に挙げた skill を使わせる。

## 7. 注意点

- **名前の衝突**: ユーザー側に `handoff` という名前の skill があると、短い名前の `/handoff` はそちらを指すことがある。このプラグインの skill は必ず `/mattpocock-skills:handoff` と完全修飾で呼ぶ。他 skill の本文（例: `ask-matt/SKILL.md:20-23`）にある `/handoff` は、このプラグインの handoff を指す。
- **保存先の確認**: 一時ディレクトリのパスは長い。書き終えたらパスを聞いて控える（公式解説ページ）。
- **一時ディレクトリは消える**: 環境によってはセッション間で一時ディレクトリが消える。再起動でも消える。すぐ使わないなら、書いた直後に別の場所へコピーする（公式解説ページ）。
- **渡し方**: 新しいセッションには、文書の中身をシェル引数に埋め込まず、ファイルのパスを示して読ませる。バッククォートや `$(...)` が壊れて、内容が黙って切れることがある（公式解説ページ）。
- **確認していない断定に注意**: 「X は未実装」「Y は完了」のような、セッションで確かめていない主張が文書に入ると、次の agent はそれを前提にする。渡す前に読み、推測は推測と書き直す（公式解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/handoff/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| ask-matt/SKILL.md（handoff の用途） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/SKILL.md （同上） |
| ask-matt/PHASE-BOUNDARIES.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/PHASE-BOUNDARIES.md （同上） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/handoff.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [prototype](prototype.md) / [teach](teach.md) / [ask-matt](ask-matt.md)
