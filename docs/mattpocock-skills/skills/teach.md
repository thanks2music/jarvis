# teach — 今のディレクトリを学習用ワークスペースにして、1 つの話題を複数セッションで教える skill

> 出典（一次情報）:
> - [teach/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/SKILL.md) — skill 本体
> - [MISSION-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/MISSION-FORMAT.md) — `MISSION.md` の書式
> - [RESOURCES-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/RESOURCES-FORMAT.md) — `RESOURCES.md` の書式
> - [LEARNING-RECORD-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/LEARNING-RECORD-FORMAT.md) — 学習記録の書式
> - [GLOSSARY-FORMAT.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/GLOSSARY-FORMAT.md) — 用語集の書式
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 複数セッションにわたって 1 つの話題を学ぶための skill である。学習の状態はファイルとして現在のディレクトリに残る（`SKILL.md:8`, `SKILL.md:12`）。
- 主な成果物は、1 つの事柄だけを教える短い HTML の lesson である（`SKILL.md:18`, `SKILL.md:49-53`）。
- 教える前に信頼できる資料を探して `RESOURCES.md` に記録する。モデル自身の知識は信用しない（`SKILL.md:30`）。
- すべての lesson を、学ぶ理由を書いた `MISSION.md` に結び付ける。mission が不明なら、まずユーザーに理由を聞く（`SKILL.md:73-77`）。
- 目標は一時的な想起（fluency）ではなく長期の定着（storage strength）である（`SKILL.md:36-45`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | productivity |
| 起動 | ユーザーのみ（`/mattpocock-skills:teach` で起動）。`disable-model-invocation: true`（`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:teach [学びたいこと]` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（現在のディレクトリ配下） |

## 3. いつ使うか・使わないか

- **使う**: 言語、フレームワーク、参加したばかりのコードベース、ヨガなど、学ぶこと自体が目的の話題を、何回かに分けて学ぶとき（`SKILL.md:8`、公式解説ページ）。
- **使わない**: 今のセッション中に 1 つの概念を説明してほしいだけなら、そのセッションで聞けばよい（公式解説ページ）。
- **実行場所**: 1 ワークスペースに mission は 1 つである（`MISSION-FORMAT.md:27`）。作業中のプロジェクトではなく、その話題専用のディレクトリで実行する（公式解説ページ）。

## 4. 流れ

SKILL.md は番号付きの手順ではなく、原則と成果物の定義を並べている。1 回の起動での動きをまとめると次のとおりである。

1. **mission を確かめる**: `MISSION.md` が無いか中身が無ければ、なぜ学びたいのかをユーザーに聞く（`SKILL.md:75`）。具体的な目標になるまで聞き返す（`MISSION-FORMAT.md:28-29`）。
2. **資料を集める**: `RESOURCES.md` が充実するまでは、質の高い資料を探すことを優先する（`SKILL.md:30`）。資料は Knowledge と Wisdom（コミュニティ）に分け、各項目に 1 行の注釈を付ける（`RESOURCES-FORMAT.md:27-29`）。
3. **次に教えることを決める**: ユーザーの指定が無ければ、`learning-records` と mission から、近接発達領域（zone of proximal development）に入る最も関連の深い事柄を選ぶ（`SKILL.md:85-89`）。
4. **lesson を作る**（`SKILL.md:49-61`）
   - 作る前に `./assets/` を読み、既存の部品（components）を再利用する（`SKILL.md:67`）。
   - 1 つの自己完結した HTML を `./lessons/0001-<dash-case-name>.html` の形で保存する（連番）。
   - 短く、すぐ終わり、具体的な成果が 1 つ得られる内容にする。
   - 他の lesson や参照資料にリンクし、主な一次資料を 1 つ薦め、不明点を agent に質問するよう促す。
   - 主張には外部資料へのリンクを付ける（`SKILL.md:95`）。
   - 可能なら CLI コマンドで lesson を開く（`SKILL.md:55`）。
5. **練習させる**: 知識を教えたあと、即時のフィードバックがある練習（クイズ、ブラウザ内の課題、実際の手順の案内）で技能を身に付けさせる（`SKILL.md:93`, `SKILL.md:103-108`）。クイズの選択肢は語数をそろえ、正解の位置を問題ごとに変える（`SKILL.md:110`）。
6. **参照資料を作る**: lesson の要点を `./reference/*.html` にまとめる（`SKILL.md:124-136`）。
7. **学習記録を残す**: 理解を示した、既有知識を申告した、誤解を正した、mission が変わった、のいずれかで `./learning-records/0001-<slug>.md` を書く（`LEARNING-RECORD-FORMAT.md:31-36`）。
8. **wisdom が要る質問**: 答えを試みたうえで、評判の良いコミュニティを案内する。ユーザーが望まなければ案内しない（`SKILL.md:116-120`）。

## 5. 書き込むもの・副作用

すべて `/teach` を実行したディレクトリからの相対パスに書く（`SKILL.md:12`）。

| 書き込み先 | 内容 | 根拠 |
|---|---|---|
| `MISSION.md` | 学ぶ理由、成功の姿、制約、対象外。変更はユーザーの確認を取ってから | `SKILL.md:14`, `SKILL.md:79` |
| `RESOURCES.md` | 信頼できる資料とコミュニティの一覧 | `SKILL.md:16` |
| `./lessons/NNNN-<name>.html` | lesson 本体 | `SKILL.md:18`, `SKILL.md:49` |
| `./reference/*.html` | 早見表、手順、用語集などの参照資料 | `SKILL.md:15` |
| `./learning-records/NNNN-<slug>.md` | 学習記録。ディレクトリは最初の記録を書くときに作る | `SKILL.md:17`, `LEARNING-RECORD-FORMAT.md:3` |
| `./assets/*` | 共有スタイルシートなど、再利用する部品 | `SKILL.md:19`, `SKILL.md:65-69` |
| `NOTES.md` | ユーザーの好みや作業メモ | `SKILL.md:20`, `SKILL.md:140` |

- lesson をブラウザ等で開く CLI コマンドを実行することがある（`SKILL.md:55`）。
- git commit・branch・push、GitHub への操作はない（SKILL.md に記述なし）。

## 6. 前後の skill

- 決まった流れの中の 1 段ではなく、engineering の流れと成果物を共有しない単独の skill である（公式解説ページ）。
- [handoff](handoff.md): grilling 中に分からない話題が出たら、`/handoff` で学習用ワークスペースへ移り、そこで `/teach` を使う（公式解説ページ）。
- 一次資料を読んで出典付きの文書にまとめたいだけなら [research](research.md)、自分の考えを鍛えたいなら [grill-me](grill-me.md) が向く（公式解説ページ）。

## 7. 注意点

- **書き込み先は実行ディレクトリ**: lesson やファイルは `/teach` を実行したディレクトリに溜まる。作業中のリポジトリで実行すると、そのリポジトリにファイルが増える（`SKILL.md:12`）。
- **用語集**: `GLOSSARY-FORMAT.md` は同梱されているが、`SKILL.md` からはリンクされていない。`LEARNING-RECORD-FORMAT.md:41` が `GLOSSARY.md` に触れるのみである。用語集が欲しければ明示的に頼む（公式解説ページ）。
- **内容の正しさ**: 引用と一次資料で確認しやすくはなるが、確認そのものは利用者が行う（公式解説ページ）。
- **復習の予定管理はしない**: 間隔反復を意識して lesson を設計するが、復習を予定に入れる仕組みは無い（公式解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| MISSION-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/MISSION-FORMAT.md （同上） |
| RESOURCES-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/RESOURCES-FORMAT.md （同上） |
| LEARNING-RECORD-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/LEARNING-RECORD-FORMAT.md （同上） |
| GLOSSARY-FORMAT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/GLOSSARY-FORMAT.md （同上） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/productivity/teach.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [handoff](handoff.md) / [research](research.md)
