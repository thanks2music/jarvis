# implement — spec や ticket に書かれた作業を実装し、現在のブランチに commit する skill

> 出典（一次情報）:
> - [implement/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement/SKILL.md) — skill 本体
> - [setup-matt-pocock-skills/issue-tracker-github.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) / [issue-tracker-local.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md) — ticket の取得方法
> - [docs/engineering/implement.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement.md) — 同じ作者による解説ページ（二次的に参照）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 利用者が指定した spec や ticket の作業を実装する（`SKILL.md:7`）
- ticket を渡すと tracker から取得し、着手前にタイトルを述べる。参照が曖昧なら尋ねる（`SKILL.md:9`）
- 合意済みの seam で [tdd](tdd.md) を呼び、型チェックと単体テストファイルをこまめに回し、最後に全テストを 1 回回す（`SKILL.md:11-13`）
- 終わったら [code-review](code-review.md) を呼び、**現在のブランチに commit する**（`SKILL.md:15-17`）
- 1 回の起動で 1 ticket。計画を見直したり、別案を出したりはしない（解説ページ）

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:implement` で起動。`disable-model-invocation: true`、`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:implement`（ticket 番号・URL・spec などを添える） |
| 内部で呼ぶ skill | `tdd`（`SKILL.md:11`）、`code-review`（`SKILL.md:15`） |
| 外部への書き込み | git（現在のブランチへの commit） |

## 3. いつ使うか・使わないか

解説ページ（docs/engineering/implement.md）の整理は次のとおりである。

| 作業の状態 | 使う skill |
|---|---|
| tracker に ticket がある | `/implement #42`。1 セッション 1 ticket、ticket ごとに文脈を消す |
| spec があり、未分割で複数セッションにまたがる | 先に [to-tickets](to-tickets.md)、その後 ticket ごとに `/implement` |
| spec があり、小さい | spec に対して直接 `/implement` |
| 直前の会話にしかなく、小さい | 同じウィンドウで `/implement`（計画が会話にしかないと明言する） |
| どこにも書かれていない | [grill-with-docs](grill-with-docs.md)、コードベースが無ければ [grill-me](grill-me.md) |
| spec なしで 1 つの振る舞いを test-first で作りたい | [tdd](tdd.md) を直接 |
| 作り終えていて確認したい | [code-review](code-review.md) を直接 |

- 複数 ticket を 1 回でまとめて並列に作るなら [implement-spec](implement-spec.md) を使う

## 4. 流れ

1. **作業を把握する**: 利用者が示した spec や ticket の作業を実装対象にする（`SKILL.md:7`）
2. **ticket を取得する**: ticket の参照を渡された場合は issue tracker から取得し、着手前にタイトルを述べる。参照が曖昧なら尋ねる（`SKILL.md:9`）。GitHub では `gh issue view`、ローカルではファイルを読む（`issue-tracker-github.md:8`, `issue-tracker-local.md:19`）
3. **tdd で作る**: 可能な範囲で、事前に合意した seam（pre-agreed seams）で Skill tool に `"tdd"` を渡して呼ぶ（`SKILL.md:11`）
4. **こまめに確認する**: 型チェックと単体のテストファイルを定期的に実行し、全テストは最後に 1 回だけ実行する（`SKILL.md:13`）
5. **レビューする**: 終わったら Skill tool に `"code-review"` を渡して呼ぶ（`SKILL.md:15`）
6. **commit する**: 作業を現在のブランチに commit する（`SKILL.md:17`）

## 5. 書き込むもの・副作用

| 書き込み | 内容 | 根拠 |
|---|---|---|
| repo 内ファイル | 実装コードとテストを書く | `SKILL.md:7`, `SKILL.md:11` |
| git commit | **現在のブランチ**に commit する。ブランチは作らない（ブランチ作成の記述が無い） | `SKILL.md:17` |
| tracker | 読むだけ。ticket を閉じる・チェックを付ける手順は無い | `SKILL.md:9` |

- push・PR 作成の手順は無い（SKILL.md に記述なし）
- 解説ページも、ticket は開いたまま残り、受け入れ基準のチェックも付かないので利用者が閉じる、と書いている

## 6. 前後の skill

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

- 前: [to-tickets](to-tickets.md)（ticket を作る）、[to-spec](to-spec.md)（小さい作業なら spec から直接）
- 中で呼ぶ: [tdd](tdd.md)、[code-review](code-review.md)
- 後: [retro](retro.md)
- 並列版: [implement-spec](implement-spec.md)

## 7. 注意点

- **main ブランチ上で実行しない**: 現在のブランチにそのまま commit するため、着手前に作業用ブランチへ切り替えておく
- **`code-review` の名前の衝突**: この skill は Skill tool に `"code-review"` を渡す（`SKILL.md:15`）。Claude Code には同名の組み込み `/code-review` もあり、どちらが解決されるかは未検証である。出力が mattpocock 版の 2 軸レビュー（Standards と Spec）になっているかを確認する
- **`code-review` が変更を見られないことがある**: 解説ページによると、`code-review` は `git diff <fixed-point>...HEAD` を見るので、commit 前の変更は含まれない。この skill は commit 前に review を呼ぶため、途中の commit が無いと review 対象が空になる。未修正の既知の問題である
- **同じ checkout で並行実行しない**: 解説ページは、複数の `/implement` セッションを 1 つの作業ディレクトリで並べると、別セッションの commit への amend や stash の消失が起きた報告を挙げている
- **ticket は 1 つずつ、文脈を消してから**: Zed では `/clear` が使えないため、ticket ごとに新しいスレッドを開いて代える
- **seam の合意が無いと tdd が効かない**: この skill 自体は seam を合意しない。spec で seam を決めておくか、起動直後のやり取りで合意する（解説ページ）
- 権限の扱いは [手順書](../playbook.md) を参照

## 出典

| 情報源 | URL |
|---|---|
| implement/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-local.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/implement.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [tdd](tdd.md) / [code-review](code-review.md) / [implement-spec](implement-spec.md) / [to-tickets](to-tickets.md)
