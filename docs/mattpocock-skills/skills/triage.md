# triage — 外から届いた issue と外部 PR を、triage ロールの状態遷移で仕分ける skill

> 出典（一次情報）:
> - [triage/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/SKILL.md) — skill 本体
> - [triage/AGENT-BRIEF.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/AGENT-BRIEF.md) — agent brief の書き方
> - [triage/OUT-OF-SCOPE.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/OUT-OF-SCOPE.md) — `.out-of-scope/` ナレッジベース
> - [setup-matt-pocock-skills/triage-labels.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/triage-labels.md) — ロールとラベル文字列の対応表
> - [docs/engineering/triage.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/triage.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- issue tracker の issue（設定によっては外部 PR も）を、カテゴリ 1 つと状態 1 つの triage ロールで仕分ける（`SKILL.md:9-11`, `SKILL.md:41`）。
- 推奨を示してメンテナーの指示を待つ。ラベル変更・コメント・close はその後に行う（`SKILL.md:72`）。
- `ready-for-agent` にするときは、AFK エージェントが作業の契約として読む **agent brief** をコメントで投稿する（`SKILL.md:79`, `AGENT-BRIEF.md:3`）。
- 投稿するコメントや issue の先頭には、必ず AI 生成である旨の 1 行を入れる（`SKILL.md:13-17`）。
- 機能要望を `wontfix` で却下するときは、repo の `.out-of-scope/` に理由を書いたファイルを作る（`SKILL.md:85`, `OUT-OF-SCOPE.md:84-97`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:triage` で起動）。`disable-model-invocation: true`（`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:triage` の後に、やりたいことを自然文で書く（例: 「対応が必要なものを見せて」「#42 を見よう」「#42 を ready-for-agent に移して」）（`SKILL.md:49-54`） |
| 内部で呼ぶ skill | grilling、domain-modeling（必要な場合のみ）（`SKILL.md:76`） |
| 外部への書き込み | GitHub（ラベル付け外し・コメント・close）、repo 内ファイル（`.out-of-scope/*.md`、`GLOSSARY.md`、ADR） |

## 3. いつ使うか・使わないか

使う場面:

- 他の人が起票した生のバグ報告や機能要望、予告なく届いた外部 PR を仕分けるとき（`docs/engineering/triage.md:5`）。

使わない場面:

- 自分で計画して to-tickets で作ったチケット。すでに agent-ready なので、triage にかけると作業が無駄になる（`docs/engineering/triage.md:5`）。
- 根本原因を探したいとき。triage の検証は「本当に起きるか、だいたいどこか」までの浅いもので、根本原因の調査は diagnosing-bugs で行う（`docs/engineering/triage.md:90`）。

## 4. 流れ

### 4.1 ロール

- カテゴリ（2 つ）: `bug`（壊れている）、`enhancement`（新機能・改善）（`SKILL.md:26-29`）。
- 状態（5 つ）: `needs-triage`（メンテナーの評価待ち）、`needs-info`（報告者の追加情報待ち）、`ready-for-agent`（仕様が揃い AFK エージェントが着手できる）、`ready-for-human`（人の実装が必要）、`wontfix`（対応しない）（`SKILL.md:31-37`）。
- 実際のラベル文字列は repo ごとに異なりうる。対応表は `triage-labels.md` にあり、提供されていなければ `/setup-matt-pocock-skills` の実行を促す（`SKILL.md:43`, `triage-labels.md:5-11`）。
- 状態遷移: ラベルなし → `needs-triage` → `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`。`needs-info` は報告者が返信すると `needs-triage` に戻る（`SKILL.md:45`）。
- PR の場合、`ready-for-agent` は「brief が付いており、エージェントが diff に対する次の作業をする」、`ready-for-human` は「人がマージできる」を意味する（`SKILL.md:39`）。

### 4.2 対応が必要なものを表示する

tracker を問い合わせ、古い順に 3 つのバケツで示す。(1) ラベルなし、(2) `needs-triage`、(3) 前回の triage メモ以降に報告者の動きがある `needs-info`。件数と 1 行要約を出し、メンテナーに選ばせる（`SKILL.md:58-66`）。PR が対象の場合、発見時は外部の PR だけを含め、各行に `[PR]` / `[issue]` を付ける（`SKILL.md:64`）。

### 4.3 特定の issue / PR を triage する

1. **文脈を集める（Gather context）**。本文・コメント・ラベル・作成者・日付を読み、PR なら diff も読む。前回の triage メモを解析して、解決済みの質問を繰り返さない。domain glossary と ADR を踏まえてコードを調べ、2 つの確認をする。(a) **重複（redundancy）**: 同じ振る舞いがすでに実装されていないかを、要望の文言ではなくドメインの概念で探す。(b) **過去の却下（prior rejection）**: `.out-of-scope/*.md` を読み、似たものがあれば示す（`SKILL.md:70`）。
2. **推奨する（Recommend）**。カテゴリと状態の推奨を理由付きで伝え、関連するコードの要約（既に実装済みかどうかも含む）を添える。指示を待つ（`SKILL.md:72`）。
3. **主張を検証する（Verify the claim）**。バグなら報告者の手順で再現する。PR ならチェックアウトして関連テストやコマンドを実行する。結果を「確認できた（コードパス付き）」「失敗」「情報不足」で報告する（`SKILL.md:74`）。
4. **詰める（Grill, 必要な場合）**。grilling と domain-modeling を呼び、1 ラウンドずつ質問し、決まった内容を `GLOSSARY.md` と ADR に反映する（`SKILL.md:76`）。
5. **結果を適用する（Apply the outcome）**（`SKILL.md:78-86`）。
   - `ready-for-agent`: agent brief をコメントで投稿する。
   - `ready-for-human`: 同じ構成で、委任できない理由（判断、外部アクセス、設計判断、手動テスト）を添える。
   - `needs-info`: triage メモ（Triage Notes テンプレート）を投稿する。
   - `wontfix`: issue を close する。既に実装済みならその場所を示し、`.out-of-scope/` には書かない。却下したバグは丁寧に説明して close する。却下した機能要望は `.out-of-scope/` に書き、コメントからリンクして close する。
   - `needs-triage`: ロールを付ける。途中経過があればコメントは任意。

### 4.4 その他

- **状態の即時変更（Quick state override）**: 「#42 を ready-for-agent に移して」と言われたら、メンテナーを信頼して直接適用する。適用前に何をするか（ロール変更、コメント、close）を確認し、grilling は省く。grilling なしで `ready-for-agent` にする場合は、agent brief を書くかどうかを尋ねる（`SKILL.md:90`）。
- **前回の続き**: 既存の triage メモを読み、報告者が未解決の質問に答えたかを確認して、最新の状況を示してから続ける（`SKILL.md:112`）。
- **agent brief の原則**: ファイルパスや行番号を書かず、型・シグネチャ・振る舞いの契約を書く。具体的で検証可能な受け入れ基準と、対象外の範囲を明記する（`AGENT-BRIEF.md:9-37`）。

## 5. 書き込むもの・副作用

| 対象 | 内容 | 根拠 |
|---|---|---|
| GitHub コメント | agent brief、triage メモ、wontfix の説明を投稿する。先頭に AI 生成の注記が必ず付く | `SKILL.md:13-17`, `SKILL.md:79-86` |
| GitHub ラベル | カテゴリ・状態のロールを付け外しする | `SKILL.md:41`, `SKILL.md:86`, `SKILL.md:90` |
| GitHub close | `wontfix` で issue（または PR）を close する | `SKILL.md:82-85`, `OUT-OF-SCOPE.md:97` |
| repo 内ファイル `.out-of-scope/<concept>.md` | 却下した機能要望の記録を新規作成、または既存ファイルの「Prior requests」に追記、方針転換時は削除・更新 | `SKILL.md:85`, `OUT-OF-SCOPE.md:90-105` |
| repo 内ファイル `GLOSSARY.md` / ADR | grilling 中に決まった用語や判断を反映する | `SKILL.md:76` |
| PR のチェックアウト・コマンド実行 | 検証のため PR をチェックアウトし、テストやコマンドを実行する | `SKILL.md:74` |

issue の新規作成も「issue を投稿する場合は注記を付ける」と書かれているが、新規作成する場面は SKILL.md に具体的な記述がない（`SKILL.md:13`）。

## 6. 前後の skill

- 前: なし。外から issue や PR が届いたときの入口（on-ramp）である（`docs/engineering/triage.md:109`）。
- 中で呼ぶ: [grilling](grilling.md)、[domain-modeling](domain-modeling.md)。
- 後: `ready-for-agent` になった issue は [implement](implement.md) が拾う。to-tickets の流れとは `ready-for-agent` で合流する（`docs/engineering/triage.md:109`）。根本原因を調べたいバグは [diagnosing-bugs](diagnosing-bugs.md) へ（`docs/engineering/triage.md:90`）。
- 自分の計画から始める作業は [to-spec](to-spec.md) → [to-tickets](to-tickets.md) の流れを使う。

## 7. 注意点

- **AI の注記**。triage 中に tracker へ投稿するコメントや issue は、必ず次の行で始まる（`SKILL.md:13-17`）。

  ```
  > *This was generated by AI during triage.*
  ```

  チーム開発のリポジトリで AI を名乗らない規約がある場合の扱いは [手順書](../playbook.md) を参照。
- **ラベルを事前に作る**。解説ページによると、setup-matt-pocock-skills はラベルの対応表を書くだけで、tracker にラベルを作らない。状態 5 つとカテゴリ 2 つのラベルを `gh label create` などで先に作っておく（`docs/engineering/triage.md:78`）。
- **状態ロールの衝突**。状態ロールが矛盾している issue は、何かする前にメンテナーに確認する（`SKILL.md:41`）。
- **PR の扱い**。外部 PR を対象にするかは tracker 設定のフラグで決まり、既定は「no」である（`issue-tracker-github.md:19`）。
- **一括処理**。解説ページによると、一覧表示はコメントを含まないため、多数の issue をまとめて処理すると既存コメントを見落とすことがある。一括で回すなら各 issue のコメントを読むよう明示する（`docs/engineering/triage.md:93`）。
- **git 権限**。権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| triage/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| triage/AGENT-BRIEF.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/AGENT-BRIEF.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| triage/OUT-OF-SCOPE.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage/OUT-OF-SCOPE.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| setup-matt-pocock-skills/triage-labels.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/triage-labels.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| setup-matt-pocock-skills/issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/triage.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/triage.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [diagnosing-bugs](diagnosing-bugs.md) / [grilling](grilling.md) / [domain-modeling](domain-modeling.md) / [implement](implement.md)
