# ask-matt — 状況に合う skill と flow を教えるルーター

> 出典（一次情報）:
> - [ask-matt/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/SKILL.md) — skill 本体
> - [ask-matt/PHASE-BOUNDARIES.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/PHASE-BOUNDARIES.md) — phase の境目での 5 択の判断木
> - [docs/engineering/ask-matt.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/ask-matt.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 「いまの状況ならどの skill をどの順で使うか」を答える、plugin 内 skill の道案内である（`SKILL.md:9-13`）。
- 推薦して止まる。grilling もファイル作成も、推薦した skill の起動もしない（`docs/engineering/ask-matt.md:5`）。
- 中心は main flow（idea → ship）で、on-ramp・codebase health・vocabulary・standalone がその周りにある（`SKILL.md:13`）。
- phase の境目でのコンテキスト操作（Continue / `/clear` / `/handoff` / Subagent / `/compact`）の判断木も持つ（`PHASE-BOUNDARIES.md`）。
- 要約は道案内用にすぎない。skill の挙動を述べる前に、その skill の SKILL.md を読む決まりになっている（`SKILL.md:11`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:ask-matt` で起動。`SKILL.md:4` が `disable-model-invocation: true`） |
| 呼び出し方 | `/mattpocock-skills:ask-matt` |
| 内部で呼ぶ skill | なし（推薦先の SKILL.md を読むだけで、起動はしない） |
| 外部への書き込み | なし |

## 3. いつ使うか・使わないか

使う場面（`docs/engineering/ask-matt.md:11-17`）:

- アイデアはあるが、どこから始めればよいか分からない。
- 他人から来たバグ報告や要望が溜まっている。
- 似た 2 つの skill（例: grill-me と grill-with-docs）のどちらを使うか迷う。
- セッションが長くなり、コンテキストをどう扱うか決めたい。

使わない場面:

- 使う skill がもう決まっている。その skill を直接起動すればよい（`docs/engineering/ask-matt.md:17`）。
- 自作 skill や他作者の skill を含めた案内がほしい。ask-matt はこの plugin の skill だけを手書きでまとめた地図である（`docs/engineering/ask-matt.md:69`）。

## 4. 流れ

ask-matt は手順を実行する skill ではない。利用者の状況を、次の地図の上の位置に当てはめて返す。

1. **main flow（idea → ship）**（`SKILL.md:15-34`）
   1. [grill-with-docs](grill-with-docs.md) で interview してアイデアを固める。作業ディレクトリが無ければ [grill-me](grill-me.md) を使う。
   2. 会話だけで決められない問い（状態、業務ロジック、見て判断する UI）があれば、`/handoff` で外に出し、[prototype](prototype.md) で確かめ、`/handoff` で結果を戻す。
   3. 複数セッションにわたる開発なら [to-spec](to-spec.md) → [to-tickets](to-tickets.md) → チケットごとに [implement](implement.md)（間で `/clear`）か、[implement-spec](implement-spec.md) で一括。1 セッションで済むなら、その場で [implement](implement.md)。
   4. 実装は [tdd](tdd.md) で進め、[code-review](code-review.md) で締める。PR を出すときは [pr](pr.md) が本文を整える。
   5. [retro](retro.md) で振り返り、エージェントの環境（チェック、規約、steering ファイル）を改善する。
2. **コンテキストの扱い（context hygiene）**: 手順 1〜3 は 1 つのコンテキストで続ける。`/to-tickets` が終わるまで compact も clear もしない。smart zone（約 150k tokens）に近づいたら、最寄りの phase の境目で `/compact` する（`SKILL.md:36-40`）。
3. **on-ramp**: 溜まった issue → [triage](triage.md)、難しいバグ → [diagnosing-bugs](diagnosing-bugs.md)、1 セッションに収まらない大きな取り組み → [wayfinder](wayfinder.md)（`SKILL.md:42-54`）。
4. **codebase health**: [improve-codebase-architecture](improve-codebase-architecture.md)（`SKILL.md:56-60`）。
5. **vocabulary underneath（語彙の層）**: [domain-modeling](domain-modeling.md) と [codebase-design](codebase-design.md)（`SKILL.md:62-67`）。
6. **phase の境目（phase boundary）**: 上から順に問い、最初に yes になったものを選ぶ（`PHASE-BOUNDARIES.md:17-40`）。
   1. このセッションで続けられるか（次の phase が今の内容を一次情報として要るか、smart zone に余裕があるか）→ **Continue**
   2. 今のコンテキストは次に無関係か → **`/clear`**
   3. 持ち運ぶ必要があるか（別ハーネス、別ディレクトリ、同僚、phase 途中の脇道）→ **`/handoff`**
   4. 離席中に任せられるほど範囲が狭いか → **Subagent**
   5. どれでもない → **`/compact`**（指示を添える。例: `/compact we're going to QA this area`）
7. **standalone**: [grill-me](grill-me.md)、[grilling](grilling.md)、[prototype](prototype.md)、[research](research.md)、[to-questionnaire](to-questionnaire.md)、[wizard](wizard.md)、[wait-what](wait-what.md)、[teach](teach.md)、[writing-for-agents](writing-for-agents.md)（`SKILL.md:81-93`）。
8. **前提**: 最初の engineering flow の前に [setup-matt-pocock-skills](setup-matt-pocock-skills.md) を実行する（`SKILL.md:95-97`）。

## 5. 書き込むもの・副作用

なし。ask-matt は推薦して止まる（`docs/engineering/ask-matt.md:5`）。読むのは推薦先の SKILL.md だけである（`SKILL.md:11`）。

## 6. 前後の skill

- main flow の外にあり、どの flow にも入口を示す standalone のルーターである（`docs/engineering/ask-matt.md:89`）。
- 案内先として最も多いのは、main flow の先頭の [grill-with-docs](grill-with-docs.md) と、on-ramp の [triage](triage.md) である（同上）。

## 7. 注意点

- **名前の衝突**: ask-matt は `/code-review`・`/research`・`/handoff` を短い名前で案内する（`SKILL.md:20-21`, `SKILL.md:30`, `SKILL.md:88`）。Claude Code には組み込みの `/code-review` があり、環境によってはユーザーレベルの `research`・`handoff` skill もある。plugin 版を使うときは `/mattpocock-skills:code-review`・`/mattpocock-skills:research`・`/mattpocock-skills:handoff` と完全修飾名で呼ぶ。
- **「skill が入っていない」と誤って言う既知の不具合**: `disable-model-invocation: true` の skill は、ハーネスがエージェントに渡す skill 一覧に載らない。エージェントがこれを全件と思い込み、未インストールと報告することがある。実際には入っている。slash command を直接打つか、`.claude-plugin/plugin.json` を確認する（`docs/engineering/ask-matt.md:57`）。
- **要約だけで答える既知の不具合**: 他の skill の挙動を、その SKILL.md を読まずに一行要約から答えることがある。行動に移す前に「その SKILL.md を開いてから答えて」と頼む（`docs/engineering/ask-matt.md:61`）。食い違ったら SKILL.md が正しい（`docs/engineering/ask-matt.md:91`）。
- **Zed では `/clear` が使えない**: ask-matt の案内には `/clear`・`/compact` が出てくる（`SKILL.md:26`, `SKILL.md:74`, `SKILL.md:77`）。Zed の外部エージェント（ACP）経由では `/clear` が使えないため、新しいスレッドを開いて代える（推測: 新規スレッドで同じ効果を得られる）。
- **SKILL.md を直接編集しない**: plugin のインストール先は読み取り専用で、更新で上書きされる。恒常的な挙動は自分の `CLAUDE.md` / `AGENTS.md` に書く（`docs/engineering/ask-matt.md:73`）。
- git 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| ask-matt/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| ask-matt/PHASE-BOUNDARIES.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/PHASE-BOUNDARIES.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/ask-matt.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/ask-matt.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grill-with-docs](grill-with-docs.md) / [grill-me](grill-me.md) / [triage](triage.md)
