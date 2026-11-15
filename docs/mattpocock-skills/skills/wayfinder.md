# wayfinder — 1 セッションに収まらない大きな作業を、issue tracker 上の「地図」と判断チケットで計画する skill

> 出典（一次情報）:
> - [wayfinder/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wayfinder/SKILL.md) — skill 本体
> - [setup-matt-pocock-skills/issue-tracker-github.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) — GitHub での Wayfinding operations（`gh` コマンド）
> - [docs/engineering/wayfinder.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/wayfinder.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 1 つのエージェントセッションに収まらず、目的地までの道筋もまだ見えない作業を、issue tracker 上の **地図（map）** と **判断チケット（decision tickets）** で計画する（`SKILL.md:7`）。
- 既定は「計画するだけで、作らない（Plan, don't do）」。各チケットは判断を 1 つ決める。道筋がはっきりしたら地図は完了で、実装は別の流れに渡す（`SKILL.md:11-13`）。
- 起動は 2 モード。**地図を描く（Chart the map）** と **地図を進める（Work through the map）**。どちらも 1 セッションで解決するチケットは 1 枚だけ。例外は research チケット（`SKILL.md:105`）。
- GitHub では地図とチケットを issue（sub-issue）、ブロック関係を native issue dependencies で表す。issue 作成・assign・コメント・close を行う（`issue-tracker-github.md:39-46`）。
- 地図を描くときは research チケットごとにサブエージェントを起動し、結果を `research/<name>` ブランチに置いて push する。PR は作らない（`SKILL.md:115`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:wayfinder` で起動）。`disable-model-invocation: true`（`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:wayfinder`（地図を描く: 漠然としたアイデアを渡す / 地図を進める: 地図の URL か番号を渡す） |
| 内部で呼ぶ skill | grilling、domain-modeling、prototype、research（`SKILL.md:77-79`, `SKILL.md:111`, `SKILL.md:115`, `SKILL.md:124`） |
| 外部への書き込み | GitHub（issue 作成・sub-issue 化・依存関係・assign・コメント・close・本文編集）、git（`research/<name>` ブランチの push） |

## 3. いつ使うか・使わないか

使う場面:

- 作業が 1 セッション（約 100K トークン）に収まらず、目的地までの道筋が霧に包まれているとき（`SKILL.md:7`, `SKILL.md:57`）。
- 解説ページによると、判断の境目は「プロジェクトの大きさ」ではなく「セッション数」である。1 セッションで計画できるなら grill-with-docs、複数セッションなら wayfinder（`docs/engineering/wayfinder.md:11`）。

使わない場面:

- 地図を描く途中の幅優先の grilling で霧が見つからなかったとき。道筋がすでに明確で、1 セッションで終わる大きさなら地図は不要である。skill はそこで止まり、どう進めるかをユーザーに尋ねる（`SKILL.md:112`）。
- 判断がもう済んでいて、仕様書にまとめるだけのとき。解説ページは to-spec へ直接進むよう案内している（`docs/engineering/wayfinder.md:17`）。

## 4. 流れ

### 4.1 地図の構成

**目的地（destination）**: この作業が向かう先。仕様書、計画前に固める判断、データ構造の移行のようなその場での変更などがある。最初に名前を付け、これがスコープを決める（`SKILL.md:9`）。

**地図（map）**: `wayfinder:map` ラベルを付けた 1 つの issue で、正本（canonical artifact）となる。チケットはその子 issue である（`SKILL.md:21`）。地図は索引（index）であって保管場所（store）ではない。判断の中身はチケットにだけ置き、地図には要旨とリンクだけを書く（`SKILL.md:23`）。未解決のチケットは本文に並べず、クエリで探す（`SKILL.md:29`）。本文は次の 5 セクションで構成する（`SKILL.md:31-53`）。

| セクション | 中身 |
|---|---|
| Destination | 目的地。1〜2 行 |
| Notes | 領域、毎セッションで参照する skill、この作業での方針 |
| Decisions so far | close したチケットを 1 行ずつ: `[チケット名](link): 答えの要旨` |
| Not yet specified | 霧（fog of war）。まだチケットにできないスコープ内の論点 |
| Out of scope | 目的地の先にあると判断した作業 |

**チケット（ticket）**: 地図の子 issue。本文は `## Question` だけで、1 セッション（100K トークン）で扱える大きさにする（`SKILL.md:57-63`）。答えは本文に書かず、解決時にコメントで残す（`SKILL.md:71`）。

- ラベルは `wayfinder:<type>` だけを付ける。`ready-for-agent` のような triage ラベルは付けない。実装作業ではなく判断だからである（`SKILL.md:65`）。
- **claim**: 作業を始める前に、地図を進めている開発者へチケットを assign する。assign されていること自体が claim である（`SKILL.md:67`）。
- **ブロック**: tracker の native な依存関係を使う。tracker の UI で frontier が見えるからである。native 機能がない tracker だけ本文の記法で代替する（`SKILL.md:69`）。
- **frontier**: open で、ブロックされておらず、claim されていない子チケットの集合（`SKILL.md:69`）。

**名前で呼ぶ**: 人が読む文章では、チケットを番号ではなくタイトルで呼ぶ。リンクはタイトルの中に入れる（`SKILL.md:17`）。

### 4.2 チケットの 4 種類

各チケットは HITL（human in the loop。人とのやり取りで解決する）か AFK（エージェント単独で解決する）のどちらかである。HITL チケットでエージェントが人の側を代弁してはならない（`SKILL.md:75`）。

| 種類（ラベル） | モード | 使う場面 | 解決方法 |
|---|---|---|---|
| `wayfinder:research` | AFK | 作業ディレクトリの外の知識（ドキュメント、外部 API、ナレッジベース）が判断に必要なとき | research skill を呼ぶサブエージェント（`SKILL.md:77`） |
| `wayfinder:prototype` | HITL | 「どう見えるべきか」「どう振る舞うべきか」が論点のとき | prototype skill で安価で粗い成果物を作り、資産としてリンクする（`SKILL.md:78`） |
| `wayfinder:grilling` | HITL | 会話で決められるとき。既定の種類 | grilling と domain-modeling の 2 つを呼ぶ（`SKILL.md:79`） |
| `wayfinder:task` | HITL または AFK | 判断の前に必要な手作業（サービス登録、権限付与、データ移動など） | エージェントだけでできれば AFK、できなければ人にチェックリストを渡す。結果として得た事実（認証情報の場所、URL、件数など）を答えに残す（`SKILL.md:80`） |

task は唯一「決める」のではなく「やる」種類である。判断を解き放つためにだけ存在し、目的地の一部を作るためのものではない（`SKILL.md:80`）。

### 4.3 霧（fog of war）と対象外（out of scope）

- 地図は意図的に不完全にする。まだ見えないものはチケットにしない（`SKILL.md:84`）。
- 霧かチケットかの判定基準は「今その問いを正確に書けるか」である。「今答えられるか」ではない。正確に書けるならブロック中でもチケットにする。書けないなら **Not yet specified** に置き、チケット大に事前分割しない（`SKILL.md:88-91`）。
- 霧は目的地の方向にだけ生じる。目的地の先の作業は霧ではなく **Out of scope** に置く。対象外の作業は昇格しない（`SKILL.md:97-99`）。
- 既存チケットが目的地の先にあると分かったら、そのチケットを close し、Out of scope に要旨・理由・リンクを 1 行書く。Decisions so far には書かない（`SKILL.md:101`）。

### 4.4 モード 1: 地図を描く（Chart the map）

漠然としたアイデアを渡して起動する（`SKILL.md:109`）。

1. **目的地を決める**。grilling と domain-modeling を呼び、何に向かうかを固める（`SKILL.md:111`）。
2. **frontier を洗い出す**。今度は幅優先（breadth-first）で grilling し、未決の判断と今すぐ着手できる最初の一歩を広く洗い出す。霧がなければ地図は不要なので、止まってユーザーに進め方を尋ねる（`SKILL.md:112`）。
3. **地図を作る**。`wayfinder:map` ラベルで作成し、Destination と Notes を埋める。Decisions so far は空にし、霧を Not yet specified に書く（`SKILL.md:113`）。
4. **今書けるチケットを作る**。まず子 issue として作成し、その後の **2 回目のパス** でブロック関係を張る。issue は ID ができるまで互いを参照できないからである。相互参照もこのパスで実 ID を使って書く。`#<n>` のような仮の番号は無関係な issue へ自動リンクされてしまう（`SKILL.md:114`）。
5. **research サブエージェントを起動する**。作成した research チケットごとに、research skill を呼ぶサブエージェントを並列で起動する。結果は使い捨ての `research/<name>` ブランチに置き、チケットからそのブランチへの参照（context pointer）を付ける。ブランチは push するが、PR は作らない。マージもしない（`SKILL.md:115`）。
6. **止まる**。地図を描くのが 1 セッション分の仕事で、チケットを自分で解決はしない（`SKILL.md:116`）。

### 4.5 モード 2: 地図を進める（Work through the map）

地図の URL か番号を渡して起動する。チケットの指定は任意で、指定がなければ skill が次のチケットを選ぶ（`SKILL.md:120`）。

1. 地図を読み込む。全チケットの本文ではなく、地図の概観だけを読む（`SKILL.md:122`）。
2. チケットを選ぶ。指定があればそれを、なければ frontier の先頭を使う。作業前に自分へ assign して claim する（`SKILL.md:123`）。
3. `wayfinder:<type>` ラベルが示す種類として解決する。種類は本文に書かれていないので、ラベルを読む。必要に応じて関連チケットや close 済みチケットの本文を取得し、Notes が指定する skill を呼ぶ。迷ったら grilling と domain-modeling を呼ぶ（`SKILL.md:124`）。
4. 解決を記録する。答えを **resolution comment** として投稿し、issue を close し、地図の Decisions so far に参照を 1 行追記する（`SKILL.md:125`）。
5. 新しく見つかったチケットを追加し（作成してから依存関係を張る）、明確になった霧をチケットに昇格して Not yet specified から消す。目的地の先と分かったチケットは対象外として扱う。判断が地図の他の部分を無効にした場合は、該当チケットを更新または削除する（`SKILL.md:126`）。

ユーザーがブロックされていないチケットを並行で進めることがあるため、他のセッションが同時に tracker を編集している前提で動く（`SKILL.md:128`）。

## 5. 書き込むもの・副作用

GitHub での具体的な操作は `issue-tracker-github.md` の Wayfinding operations に定義されている。

| 対象 | 内容 | 根拠 |
|---|---|---|
| GitHub issue（地図） | `gh issue create --label wayfinder:map` で地図を作成する | `SKILL.md:113`, `issue-tracker-github.md:41` |
| GitHub issue（チケット） | 子 issue を作成し、sub-issue として地図に紐付ける（`gh issue create --parent` など）。sub-issue が使えなければ地図本文のタスクリストと子本文の `Part of #<map>` で代替する | `SKILL.md:114`, `issue-tracker-github.md:10`, `issue-tracker-github.md:42` |
| GitHub ラベル | 地図に `wayfinder:map`、チケットに `wayfinder:{research,prototype,grilling,task}` を付ける | `SKILL.md:21`, `SKILL.md:65` |
| GitHub 依存関係 | `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` でブロック関係を張る。使えなければ本文先頭に `Blocked by: #<n>` を書く | `SKILL.md:114`, `issue-tracker-github.md:43` |
| GitHub assign | `gh issue edit <n> --add-assignee @me` で claim する。セッションの最初の書き込み | `SKILL.md:123`, `issue-tracker-github.md:45` |
| GitHub コメント・close | `gh issue comment` で答えを投稿し、`gh issue close` で閉じる。対象外と判断したチケットも close する | `SKILL.md:101`, `SKILL.md:125`, `issue-tracker-github.md:46` |
| 地図本文の編集 | Decisions so far への追記、Not yet specified・Out of scope の更新 | `SKILL.md:101`, `SKILL.md:125-126` |
| チケットの更新・削除 | 判断で無効になったチケットを更新または削除する | `SKILL.md:126` |
| git ブランチ・push | research チケットごとに `research/<name>` ブランチを作って push する。PR は作らず、マージもしない | `SKILL.md:115` |
| repo 内ファイル | research サブエージェントが Markdown を書く（research skill の動作）。prototype チケットでは prototype skill がコードを書き、使い捨てブランチに commit する | `SKILL.md:77-78`, [research](research.md) / [prototype](prototype.md) |

## 6. 前後の skill

- 前: 漠然としたアイデアから直接始める。setup-matt-pocock-skills で tracker を設定しておく必要がある（`SKILL.md:25`）。
- 中で呼ぶ: [grilling](grilling.md)、[domain-modeling](domain-modeling.md)、[prototype](prototype.md)、[research](research.md)。
- 後: 解説ページによると、地図が片付いたら [to-spec](to-spec.md) で判断を 1 つの仕様書にまとめ、[to-tickets](to-tickets.md) で実装チケットに分け、[implement](implement.md) へ進む（`docs/engineering/wayfinder.md:18`, `docs/engineering/wayfinder.md:66`）。
- 1 セッションで済む計画は [grill-with-docs](grill-with-docs.md) を使う（`docs/engineering/wayfinder.md:11`）。

## 7. 注意点

- **ラベルを事前に作る**。`wayfinder:map` と `wayfinder:research` / `wayfinder:prototype` / `wayfinder:grilling` / `wayfinder:task` の 5 つを、GitHub リポジトリに先に作っておく。skill 本体はラベルの作成手順を書いていない（`SKILL.md:21`, `SKILL.md:65`）。
- **tracker の設定が前提**。tracker が設定されていなければ `/setup-matt-pocock-skills` を実行するよう促す。設定がない場合はローカル Markdown の tracker を既定にする（`SKILL.md:25`）。
- **1 セッション 1 チケット**。research チケットだけが例外である（`SKILL.md:105`）。チケットごとに新しいセッションを始める。Zed では `/clear` が使えないため、新しいスレッドを開いて代える。
- **既定は計画だけ**。Notes に書けば実行まで含められる（`SKILL.md:13`）。解説ページは、エージェント自身が Notes に「この地図は実行を含む」と書き、後のセッションがそれを許可と読んで実装を始めた事例を挙げている。自分で描いていない地図は Notes を確認するとよい（`docs/engineering/wayfinder.md:69`）。
- **research ブランチ**。`research/<name>` ブランチは push されるが PR にならず、マージもされない（`SKILL.md:115`）。research の解説ページによると、後でブランチを消すとチケットからの参照（context pointer）が壊れる（`docs/engineering/research.md:61`）。
- **research の入れ子**。research skill 自体がバックグラウンドエージェントを起動するため、サブエージェントの中でさらにエージェントが起動しうる（[research](research.md) の注意点を参照）。
- **並行作業**。frontier が並行作業を可能にするが、解説ページは 1 チケットずつ進めるのを安全な既定としている。grilling を 2 セッションで同時に進めると、片方で答えた質問をもう片方で再度聞かれる（`docs/engineering/wayfinder.md:75`）。
- **git 権限**。権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| wayfinder/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wayfinder/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| setup-matt-pocock-skills/issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/wayfinder.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/wayfinder.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [grilling](grilling.md) / [domain-modeling](domain-modeling.md) / [prototype](prototype.md) / [research](research.md) / [to-spec](to-spec.md)
