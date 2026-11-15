# to-tickets — 計画や spec を tracer-bullet の ticket に分け、依存関係付きで tracker に公開する skill

> 出典（一次情報）:
> - [to-tickets/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-tickets/SKILL.md) — skill 本体
> - [setup-matt-pocock-skills/issue-tracker-github.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) — GitHub での issue 作成・sub-issue・blocking の操作
> - [setup-matt-pocock-skills/issue-tracker-local.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md) — ローカル Markdown での ticket ファイルの置き方
> - [docs/engineering/to-tickets.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/to-tickets.md) — 同じ作者による解説ページ（二次的に参照）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 計画・spec・現在の会話を、tracer bullet（縦切り）の ticket の集まりに分ける（`SKILL.md:9`）
- 各 ticket は、先に終わるべき ticket（blocking edge）を宣言する（`SKILL.md:38`）
- 公開する前に分け方を番号付きリストで示し、ユーザーが承認するまで繰り返す（`SKILL.md:42-56`）
- 公開先は設定された tracker による。ローカルなら 1 ticket 1 ファイル、GitHub などなら 1 ticket 1 issue（`SKILL.md:60-63`）
- 親 issue は閉じず、変更もしない（`SKILL.md:67`）

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:to-tickets` で起動。`disable-model-invocation: true`、`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:to-tickets`（spec のパス、issue 番号、URL を引数に渡せる。`SKILL.md:17`） |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | GitHub（issue 作成・sub-issue・blocking・ラベル）またはファイル（`.scratch/` 配下）。設定された tracker による |

## 3. いつ使うか・使わないか

解説ページ（docs/engineering/to-tickets.md）の整理は次のとおりである。

| 状況 | 使う skill |
|---|---|
| spec の issue があり、作業が複数セッションにまたがる | `/to-tickets` または `/to-tickets #<spec_issue>` |
| 計画が会話の中にしかない | `/to-tickets`（会話を直接読む。spec は不要） |
| 変更全体が 1 つの context window に収まる | [implement](implement.md)（ticket は作らない） |
| まだ何も決まっていない | [grill-with-docs](grill-with-docs.md)、続けて [to-spec](to-spec.md) |

- 前提として、[setup-matt-pocock-skills](setup-matt-pocock-skills.md) で tracker とトリアージラベルの語彙が設定済みである必要がある。未設定なら `/setup-matt-pocock-skills` の実行を促す（`SKILL.md:11`）
- 解説ページによると、この skill が作った ticket に [triage](triage.md) をかける必要はない

## 4. 流れ

1. **文脈を集める**: 会話にある情報から始める。引数で参照（spec のパス、issue 番号や URL）を渡された場合は取得し、本文とコメントを全部読む（`SKILL.md:17`）
2. **コードベースを調べる（任意）**: 未探索なら現状を調べる。ticket のタイトルと説明には用語集の語彙を使い、ADR に従う。実装を楽にする事前リファクタリング（prefactor）の機会を探す（`SKILL.md:21-23`）
3. **縦切りの slice を下書きする**（`SKILL.md:27-36`）:
   - 各 slice は schema・API・UI・テストの全層を細く完全に通す。1 層だけの横切りにしない
   - 完了した slice は単独でデモまたは検証できる
   - 各 slice は新しい context window 1 つに収まる大きさにする
   - 事前リファクタリングは先に置く
   - 各 ticket に blocking edge を付ける。blocker の無い ticket はすぐ着手できる（`SKILL.md:38`）
4. **広範なリファクタリングの例外**: 列名の変更のように、1 つの機械的な変更が codebase 全体に波及するもの（wide refactor）は縦切りにしない。expand–contract で並べる（`SKILL.md:40`）
   - expand: 新しい形を古い形の横に足す
   - migrate: 呼び出し箇所をパッケージやディレクトリ単位のバッチで移す。各バッチを 1 ticket にし、expand に block させる
   - contract: 呼び出し元が無くなったら古い形を消す。全 migrate バッチに block させる
5. **ユーザーに確認する（Quiz the user）**: 各 ticket の Title・Blocked by・What it delivers を番号付きリストで示し、粒度、blocking edge の正しさ、統合や分割の要否を尋ねる。承認されるまで繰り返す（`SKILL.md:42-56`）
6. **tracker に公開する**: 承認された ticket を公開する（`SKILL.md:58-67`）。詳細は次節

## 5. 書き込むもの・副作用

| 書き込み | 内容 | 根拠 |
|---|---|---|
| ローカル tracker の場合 | `.scratch/<feature-slug>/issues/<NN>-<slug>.md` に 1 ticket 1 ファイルで書く。`01` から依存順（blocker が先）に番号を振る。1 ファイルにまとめない | `SKILL.md:62`, `issue-tracker-local.md:9` |
| ローカルの状態 | 各ファイルに `**Status:** ready-for-agent` を書く | `SKILL.md:77` |
| 実 tracker（GitHub, Linear など）の場合 | 1 ticket 1 issue を依存順（blocker が先）に作る | `SKILL.md:63` |
| blocking | tracker に native の blocking 関係があればそれを使う。無ければ本文の「Blocked by」に書く | `SKILL.md:63`, `SKILL.md:101` |
| GitHub の blocking 操作 | `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` | `issue-tracker-github.md:43` |
| sub-issue | 元が既存 issue なら、各 ticket をその sub-issue にする。GitHub では `gh issue create --parent <parent>`（`gh` 2.94+） | `SKILL.md:63`, `issue-tracker-github.md:10` |
| ラベル | 指示が無い限り `ready-for-agent` を付ける | `SKILL.md:63` |
| 親 issue | 閉じない・変更しない | `SKILL.md:67` |

- git の commit・branch・push は行わない（SKILL.md に記述なし）
- 本文にはファイルパスやコード片を書かない。prototype 由来の判断を表すコード片だけは例外（`SKILL.md:105`）

## 6. 前後の skill

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

- 前: [to-spec](to-spec.md)（解説ページは同じ context window で続けて実行するよう勧めている）
- 後: [implement](implement.md)（1 セッション 1 ticket）、または [implement-spec](implement-spec.md)（blocking edge を task graph として読み、並列に実装する）

## 7. 注意点

- **細かく分けすぎる**: 解説ページによると最も多い報告である。確認（Quiz）の段階で統合を頼む。変更全体が 1 つの context window に収まるなら、この skill 自体が不要
- **層ごとに分かれてしまう**: 確認の段階で「この ticket が終わったら何をデモできるか」を ticket ごとに尋ねる。答えが無ければ横切りである（解説ページ）
- **ticket の実行は利用者の仕事**: この skill は ticket を作って止まる。自動で配る仕組みは無い。[implement](implement.md) は完了時に ticket を確実には閉じないので、状態は利用者が更新する（解説ページ）
- **`/to-spec` との間で文脈を消さない**: 大きな spec は tracker から全文を読み戻せないことがある（解説ページ）。Zed では `/clear` が使えないため、新しいスレッドで代える場面でも、この 2 つは同じスレッドで続ける
- 権限の扱いは [手順書](../playbook.md) を参照

## 出典

| 情報源 | URL |
|---|---|
| to-tickets/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-tickets/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-local.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/to-tickets.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/to-tickets.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [to-spec](to-spec.md) / [implement](implement.md) / [implement-spec](implement-spec.md)
