# research — 一次情報で問いを調べ、出典付きの Markdown を repo に残す skill（バックグラウンドエージェントで実行）

> 出典（一次情報）:
> - [research/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/research/SKILL.md) — skill 本体
> - [docs/engineering/research.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/research.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 調査を **バックグラウンドエージェント** に任せ、呼び出した側は作業を続ける（`SKILL.md:6`）。
- 調べる先は一次情報（公式ドキュメント、ソースコード、仕様、ファーストパーティの API）に限る。各主張をその情報を持つ出典まで遡る（`SKILL.md:10`）。
- 結果は、各主張に出典を付けた Markdown ファイル 1 つにまとめる（`SKILL.md:11`）。
- 保存先は repo の既存の慣習に合わせる。慣習がなければ適当な場所に置き、その場所を伝える（`SKILL.md:12`）。
- ユーザー側に同名の `research` skill があると衝突するため、`/mattpocock-skills:research` と完全修飾で呼ぶ。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:research`。話題の調査、ドキュメントや API の事実集め、読み込み作業の委任を求められたときにモデルも起動する（`SKILL.md:3`） |
| 内部で呼ぶ skill | なし（バックグラウンドエージェントを 1 つ起動する）（`SKILL.md:6`） |
| 外部への書き込み | ファイル（repo 内の Markdown 1 つ） |

## 3. いつ使うか・使わないか

使う場面:

- 次の一歩が「作業ディレクトリの外のことを調べる」であるとき。外部 API の挙動、仕様の記述、バージョンに関する主張の真偽などで、自分のスレッドを読み込み作業で止めたくない場合（`docs/engineering/research.md:11`）。
- [wayfinder](wayfinder.md) の `wayfinder:research` チケットを解決するとき。wayfinder が地図を描く際に、チケットごとにこの skill を呼ぶサブエージェントを起動する（wayfinder の `SKILL.md:77`, `SKILL.md:115`）。

使わない場面:

- 欲しいものが「事実」ではなく「判断」のとき。それは grilling の役割である（`docs/engineering/research.md:21`）。
- 自分のコードベースでやり方が通用するかを確かめたいとき。それは [prototype](prototype.md) の役割である（`docs/engineering/research.md:18`）。

## 4. 流れ

1. 呼び出した側が **バックグラウンドエージェント** を起動し、調査を任せる。呼び出した側はその間も作業を続ける（`SKILL.md:6`）。
2. エージェントが、問いを **一次情報**（official docs、source code、specs、first-party APIs）で調べる。二次的な解説ではなく、主張を持つ出典まで遡る（`SKILL.md:10`）。
3. 結果を 1 つの Markdown ファイルに書き、各主張に出典を付ける（`SKILL.md:11`）。
4. repo がこの種のメモを置いている場所に保存する。既存の慣習に合わせ、なければ適当な場所に置いてその場所を伝える（`SKILL.md:12`）。

SKILL.md 本体はこの 4 点だけで構成されている。調査の終了条件や、信頼できる情報源の判定基準は書かれていない（`docs/engineering/research.md:45`, `docs/engineering/research.md:57`）。

## 5. 書き込むもの・副作用

| 対象 | 内容 | 根拠 |
|---|---|---|
| バックグラウンドエージェントの起動 | 調査用のエージェントを 1 つ起動する | `SKILL.md:6` |
| repo 内ファイル | 出典付きの Markdown ファイルを 1 つ書く。場所は repo の慣習に従う | `SKILL.md:11-12` |
| git / GitHub | SKILL.md 単体では commit・push・issue 操作の記述はない。wayfinder から呼ばれた場合は、wayfinder 側が結果を `research/<name>` ブランチに置いて push する（PR は作らない） | wayfinder の `SKILL.md:115` |

## 6. 前後の skill

- 前: [wayfinder](wayfinder.md) が research チケットごとに呼ぶ。この skill を直接呼ぶ skill は wayfinder だけである（`docs/engineering/research.md:73`）。
- 後: 結果のファイルを [grilling](grilling.md)、[grill-with-docs](grill-with-docs.md)、[to-spec](to-spec.md) に持ち込む。後のセッションが自動でファイルを読み込むことはないので、自分で渡す（`docs/engineering/research.md:49`, `docs/engineering/research.md:73`）。

## 7. 注意点

- **名前の衝突**。ユーザースコープなどに同名の `research` skill があると、`/research` がどちらを指すか紛らわしい。この plugin の skill は `/mattpocock-skills:research` と完全修飾で呼ぶ。
- **バックグラウンドで動く**。結果は会話の中ではなくファイルとして返る。完了通知とファイルのパスを確認する（`SKILL.md:6`, `SKILL.md:12`）。
- **エージェントの入れ子**。解説ページによると、起動されたバックグラウンドエージェントが同じ指示に従い、さらに別のエージェントを起動する未修正の不具合がある（issue #530）。起動後はバックグラウンドタスクの一覧を確認し、重複していれば止める（`docs/engineering/research.md:35`）。
- **逆の失敗**。利用者のグローバル指示が「エージェントは作業を再委任しない」と定めていると、バックグラウンドエージェントが作業を断り、何も起きないことがある（`docs/engineering/research.md:37`）。
- **範囲を絞る**。終了条件がないため、深く掘りすぎたり、広く浅く読んで肝心な点を落としたりする。1 つの API、1 つの挙動のような狭い問いにする（`docs/engineering/research.md:57`）。
- **ファイルの扱い**。解説ページは、research ファイルはその日時点の事実なので古くなると有害であり、git に入れない運用が多いとしている（`docs/engineering/research.md:41`）。
- **git 権限**。権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| research/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/research/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| wayfinder/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wayfinder/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/research.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/research.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [wayfinder](wayfinder.md) / [grilling](grilling.md) / [prototype](prototype.md)
