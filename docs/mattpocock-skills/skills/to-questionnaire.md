# to-questionnaire — 自分だけでは決められない事柄を、他の人に答えてもらう質問票にする skill

> 出典（一次情報）:
> - [to-questionnaire/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/to-questionnaire/SKILL.md) — skill 本体
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- ユーザーだけでは答えられない事柄を、答えを知る 1 人に渡す Markdown の質問票（questionnaire）にする。非同期で記入してもらうか、会議で一緒に埋める（`SKILL.md:7`）。
- ユーザーに聞くのは「送り先（the send）」のことだけで、話題そのものは聞かない（`SKILL.md:9`）。
- 聞くのは 2 点。誰に送るか、何を返してほしいか（`SKILL.md:12-14`）。
- 質問票は現在のディレクトリの `to-questionnaire-<slug>.md` に書き、パスを伝える（`SKILL.md:16`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーのみ（`/mattpocock-skills:to-questionnaire` で起動）。`disable-model-invocation: true`（`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:to-questionnaire` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（現在のディレクトリに markdown を 1 つ） |

## 3. いつ使うか・使わないか

- **使う**: 判断が、他の 1 人の頭の中にある知識を待って止まっているとき（`SKILL.md:7`）。典型は、grilling の途中で自分には答えられない質問が出た場面である（公式解説ページ）。
- 答えがどこにあるかで、使う skill が変わる（公式解説ページ）。

| 答えがある場所 | 使う skill |
|---|---|
| 自分の頭の中（まだ整理されていない） | [grill-me](grill-me.md) |
| コードベース | [grill-with-docs](grill-with-docs.md) |
| 他の人の頭の中 | `to-questionnaire` |
| まだ誰も持っていない（触れるものが要る） | [prototype](prototype.md) |

- **使わない**: 複数の相手に分けて聞きたいとき、1 回の実行では対応しない。1 人につき 1 回実行する（`SKILL.md:12`、公式解説ページ）。

## 4. 流れ

1. **誰に送るか（Who is it going to?）**: 受け手の役割、専門性、ユーザーとの関係を 1 回のやり取りで聞く。これで文書の口調と、どれだけ背景説明を載せるかが決まる。完了条件は、受け手が誰で、ユーザーが知らない何を知っているかが分かったこと（`SKILL.md:12`）。
2. **何を返してほしいか（What do you need back?）**: ユーザーが 1 人では決められず、この相手から得たい判断や事実を 1 回のやり取りで聞く。完了条件は、ユーザーが最終的にできるようになるべきこと・決めるべきことの具体的なリストができたこと（`SKILL.md:14`）。
3. **質問票を書く（Write the questionnaire）**: 1・2 の差（gap）を狙った質問を、下記の文書構造で書く。`to-questionnaire-<slug>.md`（slug は話題から作る）に保存し、パスを伝える。完了条件は、ファイルが存在し、2 で挙がった項目がすべて質問でカバーされていること（`SKILL.md:16`）。

### 文書構造（`SKILL.md:18-54`）

- 「発見のための質問票（discovery questionnaire）」として書く。ユーザーは背景を持たず、受け手が持っている。
- 重要な質問から順に並べる。非同期では 1 回しか答えてもらえないかもしれないためである。質問が数個を超えたら、テーマごとに `##` 見出しでまとめる。
- 冒頭に目的（Purpose）、差出人・宛先・回答の使い道、1 段落の背景（Context）、回答方法（期限、手間の目安、「分からない」も有用であること）を書く。
- 各質問は 1 つのことだけを聞く（複合質問にしない）。直下に回答欄を置く。誤読されそうな質問にだけ、1 行の「なぜ重要か（why this matters）」を添える。
- 最後に「他に知っておくべきことは？（Anything else?）」を置く。

## 5. 書き込むもの・副作用

| 書き込み先 | 内容 | 根拠 |
|---|---|---|
| 現在のディレクトリの `to-questionnaire-<slug>.md` | 質問票 | `SKILL.md:16` |

- 送付はしない。Slack・issue tracker・メールなどへの送信は利用者が行う（SKILL.md に送信の記述なし。公式解説ページ）。
- git commit・branch・push、GitHub への操作はない（SKILL.md に記述なし）。

## 6. 前後の skill

- 決まった流れの中の 1 段ではなく、必要になったときに使う単独の skill である（公式解説ページ）。
- **前**: [grill-me](grill-me.md) や [grilling](grilling.md) のセッションで、自分には答えられない質問が出たとき。同じ会話の中で実行すると、その内容を質問の下書きに使える（公式解説ページ）。
- **後**: 返ってきた回答を、次の grilling、[grill-with-docs](grill-with-docs.md)、[to-spec](to-spec.md) に渡す（公式解説ページ）。

## 7. 注意点

- **話題について質問されたら逸脱**: この skill がユーザーに聞くのは送り先と必要な回答だけである（`SKILL.md:9`）。
- **新しいセッションで実行した場合**: 取り込み（ingest）の段階は無い。前の grilling の内容は自動では入らないため、「何を返してほしいか」で話題を改めて伝える（公式解説ページ）。
- **分岐しない**: 回答に応じて質問を飛ばす構造にはならない。テーマ別に並んだ一覧である（公式解説ページ）。
- 現在のディレクトリにファイルを置くため、リポジトリ内で実行すると未追跡ファイルが増える（推測）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/to-questionnaire/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/to-questionnaire.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grill-me](grill-me.md) / [grilling](grilling.md) / [prototype](prototype.md)
