# retro — コーディングセッションを振り返り、エージェントの環境の改善案を出す skill

> 出典（一次情報）:
> - [retro/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro/SKILL.md) — skill 本体
> - [docs/engineering/retro.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/retro.md) — 同じ作者による解説ページ（補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- セッションの記録を読み、次回の実行が良くなるよう、コードではなくエージェントの **環境（environment）** の改善候補を挙げる。
- 候補は 7 分類（Navigation / Automated checks / Coding standards / Global AGENTS.md / Tool economy / No-ops / Information access）で探し、深刻な順に提示する。
- 機械的な違反には決定論的なチェック（lint ルール・pre-commit hook・CI ジョブ）を作り、`CODING_STANDARDS.md` は本当の判断事項に限る。
- 規約を課すのは実装エージェントではなくレビューエージェントの役目、という考え方が土台にある。
- 提案するだけで、ファイルは変更しない。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:retro` で起動） |
| 呼び出し方 | `/mattpocock-skills:retro` |
| 内部で呼ぶ skill | [writing-for-agents](writing-for-agents.md) |
| 外部への書き込み | なし（候補を提示するだけ） |

## 3. いつ使うか・使わないか

使う場面:

- 本来より手こずったセッションの終わり。探し物に時間がかかった、ツールで防げた誤りをした、必要な情報に届かなかった、など（解説ページ）。

使わない場面:

- 順調だったセッション。学ぶことが少ない（解説ページ）。
- セッションが作ったコードの良し悪しを判定したいとき。[code-review](code-review.md) を使う（解説ページ）。
- 同じ誤りを防ぐために `CLAUDE.md` に 1 行足したいとき。本 skill はそれに反対する立場で、チェックかレビュアー向け規約に回す（解説ページ）。

## 4. 流れ

1. Skill tool で `writing-for-agents` を呼び、文体ガイドを読み込む（`SKILL.md:11`）。
2. ユーザーが指定したセッションの一次資料を読む。このマシンのセッションログを検索することもある。指定が無ければ現在のセッションを対象にする（`SKILL.md:13`）。
3. 次の分類で改善候補を探す（`SKILL.md:15-23`）。
   - **Navigation**: 正しいファイルに辿り着きやすかったか。ファイル間に隠れた依存はないか。**ナビゲーションポインタ（navigation pointer）** で楽にならないか。情報探しに時間がかかったときに使う。
   - **Automated checks**: lint・型・テスト・ファイルシステム linter などで誤りを捕まえられないか。まずリポジトリ既存のチェックコマンド（`package.json` やビルドツールの `lint` / `check`、CI ワークフロー）を読み、既存だが未接続・壊れているチェックがあればそれを指摘する（作り直さない）。pre-commit hook も CI ジョブも無い、つまり **guardrail** が無いこと自体を指摘事項とする。
   - **Coding standards**: **レビューエージェント（reviewer agent）** に新しいルールを課すべきか、既存ルールを削る・明確にすべきか。まず違反を分類する。**機械的（mechanical）** な違反（固定の構文パターン、禁止 API、import の形、ファイル配置）には、リポジトリの linter のカスタムルール・pre-commit hook・CI ジョブのうち最も安いものでチェックを作る。ルールを書くよりチェックを作るのが既定である。`CODING_STANDARDS.md` は本当の **判断事項（judgement call）** に限る。レビューエージェントが誤りを見逃したときに使う。
   - **Global AGENTS.md**: コーディング規約や自動チェックに移すべき指示がないか。リポジトリかユーザーのグローバルの AGENTS.md が大きいときに使う。
   - **Tool economy**: 高くつくツール呼び出しを減らせないか。トークン効率の悪い自作ツール（CLI・MCP）はないか。
   - **No-ops**: 指示ファイルにある、エージェントの挙動を変えていない指示を探す。
   - **Information access**: エージェントが得られる情報を増やせないか（dev サーバーのログを tee で残す、外部サービスの読み取り専用アクセスなど）。
4. 候補を深刻な順にユーザーへ提示する（`SKILL.md:25`）。

参照情報として、SKILL.md は次の前提を置く（`SKILL.md:29-44`）。

- 作業は実装とレビューの 2 段階を通る。実装エージェントは探索・コーディング・デバッグを担い **コンテキスト圧力（context pressure）** が最も高い。レビューエージェントは差分を受け取るだけで圧力が最も低い。だから規約を課すのはレビュー側の責任である。
- `CLAUDE.md` / `AGENTS.md` は全エージェントのコンテキストに入るので、ごく控えめに使い、主に他ファイルへのナビゲーションポインタに限る。
- `CODING_STANDARDS.md` は実装時ではなくレビュー時に読まれる。1,000 行を超えたら docs フォルダへのポインタを足す。
- docs は他ファイルから指される参照資料とする。新しく書く前に既存を探す。
- skill は、description がコンテキストに入るので docs の代わりに、またはユーザー起動のコマンドとして使う。

## 5. 書き込むもの・副作用

| 種類 | 内容 | 根拠 |
|---|---|---|
| skill 呼び出し | `writing-for-agents` を読み込む | `SKILL.md:11` |
| 読み取り | 指定セッション（既定は現在のセッション）の一次資料。マシン上のセッションログを検索することがある | `SKILL.md:13` |
| 読み取り | リポジトリのチェックコマンド（`package.json`、ビルドツール、CI ワークフロー） | `SKILL.md:18` |
| 書き込み | なし。候補をユーザーに提示して終わる | `SKILL.md:25` |

git 操作・GitHub 操作・ファイル書き込みの指示は SKILL.md に無い。解説ページも「提案するだけで、候補を選ぶまで何も変わらない」と明言している。

## 6. 前後の skill

解説ページが示す本流は `grill-with-docs → to-spec → to-tickets → implement → code-review → retro` で、本 skill は最後の段である（PR を出す場合は `pr` の後）。

- 前: [code-review](code-review.md) は本 skill が最もよく調整する対象のレビュアーである。新しい規約は Standards 軸が読む場所に置かれる。
- 前: [pr](pr.md) で PR 本文を書いた後に振り返る。
- 内部: [writing-for-agents](writing-for-agents.md) が、本 skill が提案する指示ファイルや skill の文体を定める。
- 対: [improve-codebase-architecture](improve-codebase-architecture.md) はコードを改善し、本 skill は環境を改善する（解説ページ）。

## 7. 注意点

- 起動はユーザーのみ（`disable-model-invocation: true`、`SKILL.md:4`）。モデルは自動で呼ばない。
- **一般論を作り上げる傾向**。分類を埋めるために汎用的な助言をでっち上げることがある。セッションの特定の場面に辿れない候補は捨てる（解説ページ）。
- **チェックの棚卸しはしない**。散文の no-op は削除候補に挙げるが、過去に提案した lint ルールや hook・CI ジョブは監査しない。チェックの削除は自分で判断する（解説ページ）。
- **長いセッション**。既定は現在のセッションで、苦労がコンテキストに残っているのが最善である。コンテキストが溢れていたらクリアし、新しい `/mattpocock-skills:retro` で前のセッションのログを指す（解説ページ）。
- `CODING_STANDARDS.md` を同梱する skill は無い。判断事項のルールが初めて見つかったときに、本 skill が作成を提案する（解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| retro/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/retro.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/retro.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [code-review](code-review.md) / [writing-for-agents](writing-for-agents.md) / [improve-codebase-architecture](improve-codebase-architecture.md)
