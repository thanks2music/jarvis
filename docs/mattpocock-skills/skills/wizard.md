# wizard — 人間にしかできない手作業を案内する対話型 bash スクリプトを生成する skill

> 出典（一次情報）:
> - [wizard/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard/SKILL.md) — skill 本体
> - [wizard/template.sh](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard/template.sh) — 生成するスクリプトの雛形（ライブラリ部分は固定）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 人間が手でやるしかない手順（外部サービスの設定、認証情報や CI secret の準備、一度きりの移行）を、1 段ずつ案内する bash スクリプト（wizard）を作る（`SKILL.md:3`, `SKILL.md:8`）。
- UX は `template.sh` に組み込み済み。skill の仕事は手順の範囲決めと各段階（stage）の記述だけである（`SKILL.md:10`）。
- agent はスクリプトを生成するが、最後まで実行はしない。静的に検証して渡す（`SKILL.md:43`）。
- 生成したスクリプトは、実行時に `.env` への書き込みや `gh secret set` / `gh variable set` を行う（`template.sh:140-179`）。
- 既定では使い捨て。繰り返し使う手順のときだけ commit する（`SKILL.md:12`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:wizard` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（生成スクリプト）。スクリプトを実行すると `.env`、GitHub Actions の secret / variable |

## 3. いつ使うか・使わないか

- **使う**: インフラの準備、認証情報や CI secret の設定、慣れない外部ダッシュボードの操作、一度きりの移行や切り替え（`SKILL.md:3`）。
- **使わない**: agent 自身が実行できる手順（`SKILL.md:3`）。
- モデル起動が可能なため、作業中に agent が「人間しかできない手順」に当たったとき、自分からこの skill を使うことがある（説明文 `SKILL.md:3` が起動条件を書いている）。

## 4. 流れ

1. **手順の範囲を決める（Scope the procedure）**（`SKILL.md:16-25`）
   - 先にリポジトリを読む。セットアップなら `.env`、`.env.example`、`.env.*`、`README`、`docker-compose*`、フレームワーク設定、`.github/workflows/*`。workflow 中の `secrets.*` / `vars.*` の参照はすべて、wizard が用意すべき値である。
   - 移行なら、現状・目標状態・その間の取り消せない操作を把握する。
   - 段階の順序付きリストと、各段階で得る値をユーザーに見せて確認を取る。
   - 完了条件: 各値について (a) 人間がどこで入手するか、(b) どこに書くか（`.env`、GitHub secret、両方、どこにも書かない）、(c) 秘密か公開か、が分かっている。
2. **各段階の道筋を書き出す（Map each stage's journey）**（`SKILL.md:27-31`）
   - 開く URL、そこでの操作、値が表示される場所、埋める変数を具体的に書く。
   - 今の UI や正確なコマンドを知らないときは、ユーザーに聞くか docs を確認する。手順を作り話しない。
3. **wizard を書く（Author the wizard）**（`SKILL.md:33-37`）
   - `template.sh` を目的のパスにコピーし、例の stage を実際の段階に置き換える。`TOTAL_STAGES` を段階数に合わせる。
   - 使う helper: `stage`、`say` / `step`、`open_url`、`ask` / `ask_secret`、`write_env`、`set_secret` / `set_var`、`pause` / `confirm`。
   - 守る水準: 値を聞く前に URL を開く。秘密は `ask_secret`。保存する値は `write_env`。`set_secret` は CI が本当に必要な値だけ。取り消せない操作の前は `confirm`。1 段階は 1 つの作業に絞る。
   - `STAGES` マーカーより上のライブラリ部分は編集しない。
4. **検証して渡す（Verify and hand off）**（`SKILL.md:39-44`）
   - `bash -n <script>`。あれば `shellcheck`。`chmod +x <script>`。
   - 最後まで実行しない（ブラウザを開き、人間の入力を待つため）。代わりに静的に追う。手順 1 の値がすべて取得され、決めた場所に書かれるか。`set_secret` の名前が CI の `secrets.*` 参照と一致するか。
   - 実行方法をユーザーに伝える。繰り返し使う手順なら commit し、README からリンクする。

## 5. 書き込むもの・副作用

**skill 実行時（agent が行う）**

| 副作用 | 根拠 |
|---|---|
| `template.sh` を目的のパス（scratch か `scripts/`）にコピーしてスクリプトを作る | `SKILL.md:12`, `SKILL.md:35` |
| `chmod +x` で実行権限を付ける | `SKILL.md:42` |
| 繰り返し使う手順の場合に限り commit し、README からリンクする | `SKILL.md:12`, `SKILL.md:44` |

**生成スクリプトの実行時（ユーザーが行う）**

| 副作用 | 根拠 |
|---|---|
| `.env`（`ENV_FILE` で変更可）に `KEY='VALUE'` を upsert する。新規作成時はパーミッション 0600 | `template.sh:26`, `template.sh:137-151` |
| `gh secret set` で GitHub Actions の repo secret を設定する（`gh` が無いか未認証なら警告して手作業リストに回す） | `template.sh:153-166`（実行行は `template.sh:158`） |
| `gh variable set` で GitHub Actions の repo variable を設定する | `template.sh:168-179`（実行行は `template.sh:172`） |
| URL をブラウザで開く（`wslview` / `explorer.exe` / `xdg-open` / `open`） | `template.sh:66-76` |

- skill 自身は git branch・push・GitHub issue・ラベルには触れない（SKILL.md に記述なし）。

## 6. 前後の skill

- 決まった流れの中の 1 段ではなく、必要になったときにいつでも使う単独の skill である（公式解説ページ「Where it fits」）。
- 近い skill: [setup-matt-pocock-skills](setup-matt-pocock-skills.md)（この skill 群の設定）。wizard はそれ以外のセットアップ手順を担う。
- [implement](implement.md) で実装した機能に認証情報や手動の切り替えが要るとき、その部分を wizard で案内する（公式解説ページ）。
- 何を作るか決める段階では [grill-with-docs](grill-with-docs.md) や [to-spec](to-spec.md) を使う（公式解説ページ）。

## 7. 注意点

- **secret の扱い**: 値は、ユーザーが実行するスクリプトが端末の非表示入力で受け取り、`.env` や `gh secret` に直接書く（`template.sh:121-135`）。ただし、範囲決めの会話でチャットに貼った値はコンテキストに入る（公式解説ページ）。
- **途中で戻れない**: 入力を誤ったら Ctrl-C で中断して再実行する。`.env` に保存済みの値は既定値として再提示される（`template.sh:106-119`、公式解説ページ）。
- **リポジトリ全体の secret を書き換える**: `gh secret set` は既存の同名 secret を上書きする（推測。`gh` の一般的な挙動）。名前は CI の参照と照合してから実行する。
- 生成スクリプトは `set -euo pipefail` で動き、`run_wizard` 関数に全段階を入れて最後に呼ぶ構造である（`template.sh:9`, `template.sh:197-223`）。この構造は変えない。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| template.sh | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard/template.sh （同上） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/wizard.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [setup-matt-pocock-skills](setup-matt-pocock-skills.md) / [implement](implement.md)
