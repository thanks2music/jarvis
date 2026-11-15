# implement-spec — spec と ticket をサブエージェントで並列に実装し、1 本の統合ブランチにまとめる skill

> 出典（一次情報）:
> - [implement-spec/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/SKILL.md) — skill 本体
> - [setup-matt-pocock-skills/issue-tracker-github.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) / [issue-tracker-local.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md) — ticket の読み方・閉じ方
> - [docs/engineering/implement-spec.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement-spec.md) — 同じ作者による解説ページ（二次的に参照）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- [to-spec](to-spec.md) と [to-tickets](to-tickets.md) の結果を、1 回の起動でまとめて実装する（`SKILL.md:3`, `SKILL.md:7`）
- ticket を手順の列ではなく、blocking 関係を持つ task graph として読む。着手できる ticket の集まり（frontier）を並列に進める（`SKILL.md:13`）
- ticket ごとに implementer サブエージェントを、それぞれ専用の worktree とブランチで動かす（`SKILL.md:27`）
- 終わった作業は merger サブエージェントが 1 本の統合ブランチ（integration branch）にマージする（`SKILL.md:32`）
- 全 ticket の完了後に [code-review](code-review.md) をかけ、指摘を 1 つの implementer サブエージェントでまとめて直す（`SKILL.md:36`）

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:implement-spec` で起動。`disable-model-invocation: true`、`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:implement-spec`（spec の issue 番号やファイルパスを添える。解説ページ） |
| 内部で呼ぶ skill | `tdd`（各 implementer、`SKILL.md:29`）、`code-review`（統合ブランチに対して、`SKILL.md:36`） |
| 外部への書き込み | git（ブランチ・worktree・commit・merge）、条件付きで GitHub（draft PR）、tracker（ticket の解決）、repo 外のメモファイル |

## 3. いつ使うか・使わないか

解説ページ（docs/engineering/implement-spec.md）の整理は次のとおりである。

| 状況 | 使う skill |
|---|---|
| ticket に分かれ blocking edge を持つ spec を、1 回でまとめて実装したい | `/implement-spec` |
| 1 ticket ずつ自分の context window で進め、間で文脈を消したい | [implement](implement.md) |
| spec がまだ ticket に分かれていない | 先に [to-tickets](to-tickets.md) |
| graph と呼べる構造の無い小さな作業 | [implement](implement.md) を直接 |

- 前提として、tracker が設定済みである必要がある。未設定なら `/setup-matt-pocock-skills` の実行を促す（`SKILL.md:9`）
- 解説ページによると、サブエージェントをバックグラウンドで動かし、それぞれに git worktree を与えられるハーネスが必要である。1 つずつしか動かせないなら、遅い `implement` と変わらない

## 4. 流れ

前提となる方針:

- 目標は、spec 全体を 1 本の統合ブランチに実装し、各 ticket を tracker の閉じ方で解決することである（`SKILL.md:11`）
- サブエージェントとのやり取りは最小限にし、spec・ticket・調査メモ・過去の commit への参照（context pointers）で伝える。参照で得られる情報を繰り返さない（`SKILL.md:15`）
- implementer サブエージェントは、可能ならバックグラウンドで動かして並列度を上げる（`SKILL.md:17`）

手順（`SKILL.md:21-40`）:

1. **spec と ticket を読む**: task graph を把握する
2. **調査する（任意）**: exploration サブエージェントに、ticket に必要なコードベースや外部ドキュメントを調べさせる。メモは **repo の外**のディレクトリに Markdown で保存し、後のサブエージェント全員が読めるようにする
3. **統合ブランチを作る**: tracker が PR で作業を閉じる場合、または利用者が求めた場合は、手順 5 の最初のマージの後に draft PR を開き、spec と ticket を閉じる PR として印を付ける（main より先の commit が無いブランチでは PR を開けないため）
4. **implementer サブエージェントで実装する**: ticket ごとに専用の worktree とブランチで動かす。各 implementer は次を行う
   - worktree が統合ブランチを起点にしているか確かめ、違えば統合ブランチに reset する
   - Skill tool で `tdd` を呼んで ticket を作る
   - 完了報告の前に、統合ブランチの先端を自分のブランチにマージする
5. **統合ブランチにマージする**: implementer が終わったら、merger サブエージェントがその作業を統合ブランチにマージする
6. **frontier を更新する**: マージで着手できる ticket が増えたら、新しい implementer を起動する
7. **レビューする**: 全 ticket が終わったら、統合ブランチに対して Skill tool で `code-review` を呼ぶ。指摘はすべて 1 つの implementer サブエージェントで直す
8. **締める**: draft PR があれば ready for review にする。無ければ、各 ticket を tracker の閉じ方で解決し、統合ブランチを報告する
9. **片付ける**: implementer の worktree をすべて削除する

## 5. 書き込むもの・副作用

| 書き込み | 内容 | 根拠 |
|---|---|---|
| repo 外のファイル | exploration サブエージェントが調査メモを repo 外のディレクトリに保存する（場所の指定は無い。`$TMPDIR` などになるかは（推測）） | `SKILL.md:23` |
| git branch | 統合ブランチを作る | `SKILL.md:25` |
| git worktree・branch | ticket ごとに worktree とブランチを作る。最後に worktree を削除する | `SKILL.md:27`, `SKILL.md:40` |
| git reset | worktree が統合ブランチを起点にしていなければ reset する | `SKILL.md:28` |
| git commit・merge | implementer が commit し、統合ブランチの先端を取り込む。merger が統合ブランチにマージする（commit の明示は無いが、マージには commit が要る（推測）） | `SKILL.md:30`, `SKILL.md:32` |
| GitHub draft PR | tracker が PR で閉じる場合か、利用者が求めた場合のみ開き、最後に ready for review にする。PR を開くには統合ブランチの push が要る（推測） | `SKILL.md:25`, `SKILL.md:38` |
| tracker | draft PR が無い場合、各 ticket を tracker の閉じ方で解決する。GitHub なら `gh issue close`、ローカルなら `Status:` 行の更新になる（tracker 文書の対応からの（推測）） | `SKILL.md:38`, `issue-tracker-github.md:13`, `issue-tracker-local.md:10` |

## 6. 前後の skill

解説ページが示す流れ（並列版）:

```txt
grill-with-docs → to-spec → to-tickets → implement-spec → retro
```

- 前: [to-tickets](to-tickets.md)（blocking edge 付きの ticket を作る）
- 中で呼ぶ: [tdd](tdd.md)、[code-review](code-review.md)
- 後: [retro](retro.md)
- 逐次版: [implement](implement.md)

## 7. 注意点

- **main ブランチ上で起動しない**: 統合ブランチを作ってから作業する手順だが、起点のブランチは確認してから始める
- **`code-review` の名前の衝突**: Skill tool に `code-review` を渡す（`SKILL.md:36`）。Claude Code には同名の組み込み `/code-review` もあり、どちらが解決されるかは未検証である。出力が mattpocock 版の 2 軸レビュー（Standards と Spec）になっているかを確認する
- **レビューと修正のループが長引く**: 解説ページによると、review は spec 全体と照合するので全 ticket の完了後にだけ意味がある。修正後に 2 回目の広いレビューが始まったら、修正した指摘だけを確かめて止めるよう指示する
- **並列の implementer が同じファイルで衝突する**: worktree は衝突をマージ時まで遅らせるだけである。共有ファイルに触る ticket 同士には blocking edge を足すか、調査メモで名前を固定する（解説ページ）
- **GitHub で blocked な ticket が始まらない**: GitHub の blocked-by は blocker が閉じたときに減るため、実行中は古い。統合ブランチにマージ済みの ticket を orchestrator 自身に追わせる（解説ページ）
- **worktree では gitignore されたファイルが無い**: それに依存するテストが黙ってスキップされることがある（解説ページ）
- 権限の扱いは [手順書](../playbook.md) を参照

## 出典

| 情報源 | URL |
|---|---|
| implement-spec/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-local.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/implement-spec.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement-spec.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [implement](implement.md) / [to-tickets](to-tickets.md) / [tdd](tdd.md) / [code-review](code-review.md)
