# code-review — 固定点からの差分を Standards と Spec の 2 軸で並列レビューする skill

> 出典（一次情報）:
> - [code-review/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/code-review/SKILL.md) — skill 本体
> - [docs/engineering/code-review.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/code-review.md) — 同じ作者による解説ページ（補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- ユーザーが指定した固定点（commit / branch / tag / `main` / `HEAD~5` など）から `HEAD` までの差分をレビューする。
- 観点は 2 軸。**Standards**（リポジトリの文書化されたコーディング規約に従っているか）と **Spec**（元の issue / spec の要求どおりか）。
- 2 軸は別々のサブエージェントで並列に走り、結果は統合も順位付けもせず、`## Standards` と `## Spec` の見出しで並べて返す。
- Standards 軸には、リポジトリに規約が無くても効く Fowler のコードスメル 12 種（smell baseline）が常に付く。
- Claude Code 組み込みの `/code-review`（バグ検出）とは別物である。本 skill は `/mattpocock-skills:code-review` と完全修飾で呼ぶ。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方 |
| 呼び出し方 | `/mattpocock-skills:code-review` |
| 内部で呼ぶ skill | なし（サブエージェントを 2 体起動する） |
| 外部への書き込み | なし（git は読み取りのみ。issue tracker からは spec を取得するだけ） |

## 3. いつ使うか・使わないか

使う場面:

- branch・PR・作業中の変更を、「規約どおりに書けているか」と「求められたものを作ったか」の両面から確認したいとき。
- 「X 以降をレビューして（review since X）」と言える固定点があるとき。

使わない場面:

- 差分の中の null 経路・競合状態・off-by-one などのバグを探したいとき。これは Claude Code 組み込みの `/code-review` の役割である（解説ページ）。
- 1 つの差分ではなく、コードベース全体の構造が崩れているとき。[improve-codebase-architecture](improve-codebase-architecture.md) を使う（解説ページ）。
- 未コミットの変更をレビューしたいとき。差分は `<fixed-point>...HEAD` で取るため、ステージ済み・作業ツリーの変更は対象外である（`SKILL.md:21`、解説ページ）。先にコミットする。

## 4. 流れ

1. **固定点を決める（Pin the fixed point）**。ユーザーの指定を固定点とする。指定が無ければ尋ねる。差分は `git diff <fixed-point>...HEAD`（三点リーダーで merge-base と比較）、コミット一覧は `git log <fixed-point>..HEAD --oneline` で取る。先に `git rev-parse <fixed-point>` で ref が解決できること、差分が空でないことを確かめる。不正な ref や空の差分は、サブエージェント起動前のここで失敗させる（`SKILL.md:17-23`）。
2. **spec の出どころを探す（Identify the spec source）**。次の順で探す（`SKILL.md:27-32`）。
   1. コミットメッセージ内の issue 参照（`#123`、`Closes #45`、GitLab の `!67` など）。tracker doc の手順で取得する。
   2. 引数で渡されたパス。
   3. `docs/`・`specs/`・`.scratch/` 配下で branch 名や機能名に合う spec ファイル。
   4. 見つからなければユーザーに尋ねる。「無い」と言われたら Spec 軸は「no spec available」と報告してスキップする。
3. **規約の出どころを探す（Identify the standards sources）**。コードの書き方を定めたファイルをリポジトリ全体から集める。`CODING_STANDARDS.md` か `CONTRIBUTING.md` があれば必ず含める。これに smell baseline を加える（`SKILL.md:36-56`）。
   - リポジトリの規約が優先する。規約が認めていればそのスメルは出さない。
   - スメルは常に判断材料（「possible Feature Envy」のような表記）であり、確定した違反として扱わない。ツールが既に強制しているものは飛ばす。
   - 12 種: Mysterious Name / Duplicated Code / Feature Envy / Data Clumps / Primitive Obsession / Repeated Switches / Shotgun Surgery / Divergent Change / Speculative Generality / Message Chains / Middle Man / Refused Bequest。各スメルに「何か」と「どう直すか」が書かれている。
4. **2 体のサブエージェントを並列に起動する**。両方をフォアグラウンドで同時に呼ぶ（`SKILL.md:60`）。
   - Standards 用: 差分コマンドとコミット一覧、規約ファイルの一覧、smell baseline の全文を渡す。規約違反は規約ファイルとルールを引用し、スメルは名前と該当 hunk を引用させる。400 語以内（`SKILL.md:62-66`）。
   - Spec 用: 差分コマンドとコミット一覧、spec のパスか取得済みの本文を渡す。(a) 未実装・部分実装の要求、(b) 求められていない振る舞い（scope creep）、(c) 実装されているが誤っていそうな要求を、spec の行を引用して報告させる。400 語以内（`SKILL.md:68-72`）。
   - spec が無ければ Spec 用は起動せず、最終報告にその旨を書く（`SKILL.md:74`）。
5. **集約する（Aggregate）**。2 つの報告を `## Standards` と `## Spec` の見出しの下にそのまま、または軽く整えて並べる。統合や順位の付け直しはしない。最後に 1 行で、軸ごとの指摘件数と軸ごとの最悪の問題を書く。軸をまたいだ「一番の問題」は選ばない（`SKILL.md:78-80`）。

2 軸に分ける理由は、片方の軸が他方の失敗を隠さないためである。規約をすべて守っていても違うものを作っていれば Spec は失敗し、要求どおりでも規約を破っていれば Standards は失敗する（`SKILL.md:84-89`）。

## 5. 書き込むもの・副作用

| 種類 | 内容 | 根拠 |
|---|---|---|
| git | `git diff` / `git log` / `git rev-parse` の読み取りのみ。commit・branch・push は無い | `SKILL.md:21-23` |
| GitHub / issue tracker | コミットメッセージの issue 参照から spec を取得する（読み取り） | `SKILL.md:29` |
| サブエージェント | Standards 用・Spec 用の 2 体を並列起動する | `SKILL.md:11`, `SKILL.md:60` |
| repo 内ファイル | なし | — |

書き込みはなし。前提として issue tracker の設定が必要で、無ければ `/setup-matt-pocock-skills` の実行をユーザーに促す（`SKILL.md:13`）。

## 6. 前後の skill

解説ページが示す本流は `grill-with-docs → to-spec → to-tickets → implement → code-review → pr → retro` である。

- 前: [implement](implement.md) が自身の締めのレビューとして本 skill を呼ぶ。[implement-spec](implement-spec.md) も統合ブランチ全体に対して同様に呼ぶ（解説ページ）。
- 前: [to-spec](to-spec.md) と [to-tickets](to-tickets.md) が、Spec 軸の照合先になる文書を作る。
- 後: [pr](pr.md) でレビュー済みの変更の PR 本文を書く。
- 後: [retro](retro.md) が、レビューで見落とした種類の誤りを `CODING_STANDARDS.md` のルールやチェックとして提案し、Standards 軸を強化する。
- 対: [improve-codebase-architecture](improve-codebase-architecture.md) はコードベース全体版である。

## 7. 注意点

- **組み込み `/code-review` との名前の衝突**。Claude Code には同名の組み込み `/code-review` があり、こちらは差分の正しさ（バグ）を探す。本 skill は差分を固定点と比べ、規約（Standards）と仕様（Spec）の 2 軸で見る。目的が違うので両方に出番がある。plugin として入れると `mattpocock-skills:` 接頭辞が付くため、本 skill は `/mattpocock-skills:code-review` と完全修飾で呼ぶ（解説ページ）。
- **サブエージェントの再帰起動**。サブエージェントへの指示は委任を禁じていないため、サブエージェントが再び `/code-review` を呼んでエージェントが増え続ける既知の未修正バグがある（解説ページ）。無人で回すときはエージェント数に注意する。
- **同じセッションでのレビュー**。コードを書いたセッションでレビューすると確証バイアスがかかるため、新しいセッションからの実行を推奨している（解説ページ）。
- **指摘の検証**。集約時に各指摘をファイルと照合し直す手順は無い。指摘ごとの引用（規約・スメルと hunk・spec の行）を確認してから対応する（解説ページ）。
- **収束しない**。Standards 軸の判断材料は実行ごとに変わるため、指摘ゼロになるまで繰り返すと終わらない（解説ページ）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| code-review/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/code-review/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/code-review.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/code-review.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [pr](pr.md) / [retro](retro.md) / [improve-codebase-architecture](improve-codebase-architecture.md)
