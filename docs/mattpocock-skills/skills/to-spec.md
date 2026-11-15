# to-spec — 会話で決めた内容を spec にまとめ、issue tracker に公開する skill

> 出典（一次情報）:
> - [to-spec/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-spec/SKILL.md) — skill 本体
> - [setup-matt-pocock-skills/issue-tracker-github.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) — GitHub での「tracker に公開」の意味
> - [setup-matt-pocock-skills/issue-tracker-local.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md) — ローカル Markdown での「tracker に公開」の意味
> - [docs/engineering/to-spec.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/to-spec.md) — 同じ作者による解説ページ（二次的に参照）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 現在の会話とコードベースの理解から spec（仕様書）を書き、issue tracker に公開する（`SKILL.md:7`, `SKILL.md:19`）
- ユーザーへのインタビューはしない。すでに分かっていることをまとめるだけである（`SKILL.md:7`）
- 書く前に、テストを置く seam（継ぎ目）を描いてユーザーに確認する。seam は少ないほど良く、理想は 1 つ（`SKILL.md:15-17`）
- 公開した spec には `ready-for-agent` ラベルを付ける（`SKILL.md:19`）
- 解説ページによると、複数セッションにまたがる大きな作業のときに使う。1 セッションで終わる作業なら spec を省いて [implement](implement.md) へ進む

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:to-spec` で起動。`disable-model-invocation: true`、`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:to-spec` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | GitHub（issue 作成・ラベル付与）またはファイル（`.scratch/` 配下）。設定された tracker による |

## 3. いつ使うか・使わないか

解説ページ（docs/engineering/to-spec.md）の整理は次のとおりである。

| 状況 | 使う skill |
|---|---|
| まだ何も決まっていない | 先に [grill-with-docs](grill-with-docs.md) |
| 決まっていて、1 つの context window に収まる | [implement](implement.md)（spec は省く） |
| 決まっていて、複数セッションにまたがる | `to-spec`、続けて [to-tickets](to-tickets.md) |
| [wayfinder](wayfinder.md) の map が片付いた | `/to-spec #<map_issue>` |

- spec は「決めたことの記録」である。新しく決める場所ではない（解説ページ）
- 前提として、[setup-matt-pocock-skills](setup-matt-pocock-skills.md) で issue tracker とトリアージラベルの語彙が設定済みである必要がある。未設定なら skill はユーザーに `/setup-matt-pocock-skills` の実行を促す（`SKILL.md:9`）

## 4. 流れ

1. **コードベースを調べる**: まだなら repo を探索し、現状を把握する。プロジェクトの用語集（domain glossary）の語彙を使い、触る領域の ADR に従う（`SKILL.md:13`）
2. **seam を描く**: 機能をテストする seam を描く。既存の seam を優先し、できるだけ上位の seam を選ぶ。新しい seam が必要なら、できるだけ上位に提案する。seam の数は少ないほど良く、理想は 1 つ（`SKILL.md:15`）
3. **seam をユーザーに確認する**: 描いた seam が期待と合っているかを確認する（`SKILL.md:17`）
4. **spec を書いて公開する**: 下記のテンプレートで spec を書き、issue tracker に公開して `ready-for-agent` ラベルを付ける。追加のトリアージは不要（`SKILL.md:19`）

spec テンプレートの節（`SKILL.md:21-75`）:

- Problem Statement（ユーザー視点の問題）
- Solution（ユーザー視点の解決策）
- User Stories（`As an <actor>, I want a <feature>, so that <benefit>` 形式の、長く網羅的な番号付きリスト）
- Implementation Decisions（作る・変えるモジュール、インターフェース、アーキテクチャ判断、スキーマ変更、API 契約など）
- Testing Decisions（良いテストの条件、テスト対象モジュール、既存テストの参考例）
- Out of Scope
- Further Notes

ファイルパスやコード片は書かない。すぐ古くなるからである（`SKILL.md:55`）。例外として、prototype で作ったコード片が文章より正確に判断を表す場合（状態機械、reducer、スキーマ、型の形）は、判断に関わる部分だけを載せ、prototype 由来であることを添える（`SKILL.md:57`）。

## 5. 書き込むもの・副作用

| 書き込み | 内容 | 根拠 |
|---|---|---|
| issue tracker への公開 | spec を 1 件公開する | `SKILL.md:19` |
| GitHub の場合 | `gh issue create` で issue を作る | `issue-tracker-github.md:7`, `issue-tracker-github.md:31` |
| ローカル Markdown の場合 | `.scratch/<feature-slug>/` 配下にファイルを作る（spec は `spec.md`）。ディレクトリが無ければ作る | `issue-tracker-local.md:8`, `issue-tracker-local.md:15` |
| ラベル | `ready-for-agent` を付ける。GitHub では `gh issue edit --add-label`、ローカルでは `Status:` 行 | `SKILL.md:19`, `issue-tracker-github.md:12`, `issue-tracker-local.md:10` |

- git の commit・branch・push は行わない（SKILL.md に記述なし）

## 6. 前後の skill

解説ページが示す主な流れ（複数セッションの分岐）:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

- 前: [grill-with-docs](grill-with-docs.md)（判断を固める）、[wayfinder](wayfinder.md)（map が片付いた場合）
- 後: [to-tickets](to-tickets.md)（spec を tracer-bullet の ticket に分ける）、その後 [implement](implement.md) または [implement-spec](implement-spec.md)
- ここで合意した seam は、後で [tdd](tdd.md) がテストを書く場所になり、[code-review](code-review.md) が照合する（解説ページ）

## 7. 注意点

- **`ready-for-agent` の意味**: 解説ページによると「これ以上のトリアージは不要」という意味で、作業指示ではない。ただし `ready-for-agent` を拾う AFK エージェントは区別できず、spec 全体を 1 回で作ろうとする。AFK エージェントのプロンプトで親 spec を明示的に除外するか、`/to-tickets` の後でラベルを外す
- **`/to-tickets` との間で文脈を消さない**: 大きな spec は tracker から全文を読み戻せないことがある。解説ページは `/to-spec` と `/to-tickets` を同じ context window で続けて実行し、間で clear や compact をしないよう勧めている
- **重複チェックはしない**: tracker の既存 issue と重複していないかは調べない。ADR に従うがリンクはしない（解説ページ）
- **リファクタリングには向きにくい**: テンプレートが user story 中心のため。Implementation Decisions と Testing Decisions の節を使う（解説ページ）
- **旧名 `/to-prd`**: v1.1 で `to-spec` に改名された。旧名は動かない（解説ページ）
- 権限の扱いは [手順書](../playbook.md) を参照

## 出典

| 情報源 | URL |
|---|---|
| to-spec/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-spec/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-local.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/to-spec.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/to-spec.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [to-tickets](to-tickets.md) / [implement](implement.md) / [implement-spec](implement-spec.md) / [tdd](tdd.md)
