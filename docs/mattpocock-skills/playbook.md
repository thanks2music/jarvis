# mattpocock-skills 手順書 — 個人開発とチーム開発で使う

> 出典（一次情報）:
> - [ask-matt/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/SKILL.md) — skill の地図（main flow・on-ramp・phase boundary）
> - [ask-matt/PHASE-BOUNDARIES.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt/PHASE-BOUNDARIES.md) — フェーズの区切りで `/clear`・`/compact`・`/handoff` のどれを選ぶか
> - [setup-matt-pocock-skills/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/SKILL.md) — 最初に 1 回だけ行う設定
> - [Skills (code.claude.com)](https://code.claude.com/docs/en/skills) — `disable-model-invocation`・plugin の skill の名前空間
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

[mattpocock-skills](https://github.com/mattpocock/skills) を、実際の開発で使うための手順書である。各 skill の詳しい説明は [skill の一覧](README.md) から辿れる。本書は「どの順番で、どの skill を打つか」と、git・GitHub への書き込みをどう扱うかに絞る。

---

## 1. TL;DR

- 迷ったら `/mattpocock-skills:ask-matt` に状況を書く。どの skill を使うかを案内してくれる（`ask-matt` 自身は何も作らない）
- 基本の流れは **grill → spec → tickets → implement → retro**。考えを固めるのが先で、いきなり作らせない
- 1 セッションに収まらない、先の見えない大仕事は `/wayfinder` で「決めることの地図」を作ってから、spec に合流する
- skill は手順の中で commit・push・Issue 起票をする。どこまで許すかを、リポジトリの種類（個人開発 / チーム開発）ごとに先に決めておく（[§6](#6-git-と-github-への書き込み)）
- Claude Code の組み込みや自作の skill と名前が重なる `code-review`・`research`・`handoff` は、`/mattpocock-skills:<name>` と完全修飾で呼ぶ

## 2. 前提: 導入と最初の設定

| 手順 | コマンド | 何が起きるか |
|---|---|---|
| 1. plugin を入れる | `claude plugin install mattpocock-skills@claude-plugins-official` | 27 の skill が `mattpocock-skills:` の名前空間で使えるようになる |
| 2. リポジトリごとに設定する | `/mattpocock-skills:setup-matt-pocock-skills` | issue tracker（GitHub / GitLab / ローカルの Markdown）、triage のラベル、用語集と ADR の置き場所を決め、`docs/agents/` に書き出す。CLAUDE.md か AGENTS.md に `## Agent skills` の節を足す。tracker に無いラベルを作る |
| 3. wayfinder を使うならラベルを足す | `gh label create wayfinder:map` など | `wayfinder:map` と `wayfinder:{research,prototype,grilling,task}` が無いと、Issue の作成が失敗する |

- 設定はリポジトリ単位である。新しいリポジトリで使うときは、最初に 2 を実行する
- CLAUDE.md を git 管理外にしているリポジトリでは、2 で足される `## Agent skills` の節もローカルにだけ残る

## 3. 起動の区分

skill は 2 種類ある（[Skills の公式 docs](https://code.claude.com/docs/en/skills) の `disable-model-invocation`）。

| 区分 | skill | 意味 |
|---|---|---|
| **ユーザーだけが起動できる** | ask-matt・grill-with-docs・grill-me・to-spec・to-tickets・implement・implement-spec・triage・wayfinder・improve-codebase-architecture・retro・handoff・teach・to-questionnaire・wait-what・setup-matt-pocock-skills | 利用者がスラッシュコマンドで打つ。Claude は自分から起動しない |
| **モデルも起動できる** | tdd・diagnosing-bugs・prototype・research・domain-modeling・codebase-design・code-review・pr・wizard・grilling・writing-for-agents | 会話の内容に応じて Claude が起動することがある。他の skill の中から呼ばれることも多い |

この区分は、§6 の「どこまでを利用者の指示とみなすか」の線引きにも使う。

## 4. 典型的な流れ

### 4.1 1 セッションで終わる機能

```text
/mattpocock-skills:grill-with-docs <作りたいこと>   … 質問に答えて固める
/mattpocock-skills:implement                       … 同じコンテキストのまま実装（tdd → code-review → commit）
/mattpocock-skills:retro                           … 同じセッションの中で振り返る
```

### 4.2 複数セッションにまたがる機能

```text
(セッション A)
/mattpocock-skills:grill-with-docs <作りたいこと>
/mattpocock-skills:to-spec        … 会話を spec にまとめて Issue に起票（ready-for-agent）
/mattpocock-skills:to-tickets     … 縦切りの ticket に分け、ブロック関係を付けて起票（起票の前に一覧を確認される）

(セッション B: 新しいコンテキスト)  /mattpocock-skills:implement <ticket>
(セッション C: 新しいコンテキスト)  /mattpocock-skills:implement <ticket>
…
または /mattpocock-skills:implement-spec <spec>  … ブロックの解けた ticket を subagent に並列で実装させ、1 本の統合ブランチにまとめる
```

- grill から `to-tickets` までは、同じコンテキストのまま続ける。途中で `/clear` や `/compact` をしない（grilling の議論が spec と ticket の材料になるため）
- ticket は単体で話が完結するように書かれるので、`implement` は ticket ごとに新しいコンテキストで回してよい
- 会話で決めきれない問い（状態の持ち方、画面の見た目）は、`/mattpocock-skills:prototype` で捨てるつもりのコードを作って確かめる

### 4.3 先の見えない大仕事（`/wayfinder`）

既存サイトの基盤を丸ごと移す、新規のプロダクトを立ち上げる、といった 1 セッションでは決めきれない判断が連鎖する仕事に使う。

```text
(セッション A) /mattpocock-skills:wayfinder <ぼんやりした目的>
               … 目的地（destination）を決め、決めることの地図（map）を Issue に作る。
                 research の ticket は subagent が並列で調べ、research/<name> ブランチに残す（push する。PR は作らない）
(セッション B〜) /mattpocock-skills:wayfinder <map>
               … 1 セッションで判断の ticket を 1 件だけ解く。解けた分だけ霧が晴れ、次の ticket が増える
(晴れたら)     /mattpocock-skills:to-spec → to-tickets → implement   … ここで初めて作る
```

- wayfinder が出すのは判断だけで、成果物は作らない
- 範囲がはっきりした機能には使わない（SKILL.md の言葉で "never a well-scoped feature"）。迷ったら `ask-matt` に聞く
- 人間にしかできない手順（DNS の切り替え、管理画面の操作、認証情報の発行）は、`wizard` が対話式の bash スクリプトにする

### 4.4 不具合

```text
/mattpocock-skills:diagnosing-bugs <症状>   … まず、必ず赤くなる再現コマンドを作ってから直す
/mattpocock-skills:retro                    … 同じセッションの中で「何があれば防げたか」を振り返る
```

### 4.5 その他の入口

| 状況 | skill |
|---|---|
| 他人が起票した Issue やバグ報告が溜まっている | `/mattpocock-skills:triage`（自分で `to-tickets` した ticket は triage しない） |
| コードベースを agent が扱いやすく保ちたい | `/mattpocock-skills:improve-codebase-architecture` |
| 自分では答えられない判断を、他人に聞きたい | `/mattpocock-skills:to-questionnaire` |
| 直前の説明が分からなかった | `/mattpocock-skills:wait-what` |
| 出典つきで調べものを任せたい | `/mattpocock-skills:research` |

## 5. セッションの区切り方

フェーズ（grilling・実装・QA）の境目では、次の 5 つから選ぶ（`PHASE-BOUNDARIES.md`）。

| 選択肢 | いつ |
|---|---|
| 続ける | まず検討する。何も失わない |
| `/clear` | 今のコンテキストが次の作業に要らないとき |
| `/mattpocock-skills:handoff` | 別のハーネス・別のディレクトリ・他人へ渡すとき、または作業の途中で横道を分けるとき |
| subagent | 範囲の狭い作業を別のコンテキストに任せ、報告だけ受け取るとき |
| `/compact` | 既定の選択肢。上のどれにも当たらないとき |

- コンテキストが ~150k トークン（SKILL.md の言う smart zone）に近づいたら、近いフェーズの境目で `/compact` する
- エディタの外部エージェント（ACP）経由で Claude Code を使う場合、`/clear` が使えないことがある。その場合は新しいスレッド（新しいセッション）を開いて代える

## 6. git と GitHub への書き込み

### 6.1 skill ごとの書き込み

| skill | 書き込むもの |
|---|---|
| setup-matt-pocock-skills | `docs/agents/*`、CLAUDE.md / AGENTS.md、tracker のラベル |
| to-spec・to-tickets | Issue の起票・ラベル（ローカル tracker なら `.scratch/` のファイル） |
| triage | Issue / PR へのコメント・ラベル・close、`.out-of-scope/` |
| wayfinder | Issue（地図と ticket）・ラベル・assign・close、`research/<name>` ブランチの push |
| implement | 今のブランチへの commit |
| implement-spec | 統合ブランチと ticket ごとのブランチ・worktree、マージ、条件付きで draft PR |
| prototype・wizard | 捨てるブランチへの commit（wizard は利用者が望んだときだけ） |
| domain-modeling・grill-with-docs | `GLOSSARY.md`・`docs/adr/` |

根拠の行番号は各 skill のページにある。

### 6.2 権限の決め方（推奨）

`settings.json` の permission rule は「どの skill の中で実行しているか」を条件にできない。skill の frontmatter の `allowed-tools` は skill 単位で事前承認できるが、その skill を起動したターンだけで切れ、plugin の skill は利用者が編集するものでもない（[Skills の公式 docs](https://code.claude.com/docs/en/skills)）。そこで次のように運用する。

1. **意図を CLAUDE.md に書く。** 「利用者がユーザー起動専用の skill を起動したら、その流れの成果物について、決めた範囲の git / GitHub 操作を指示したものとみなす」と宣言する
2. **実行時の判定は permission と auto mode に任せる。** auto mode を使うなら、方針に沿った操作を `autoMode.allow`（既定の soft_deny への例外）に散文で書く。`environment` には信頼するリポジトリと org（`Source control`）を書く。人の指示でも越えてはいけない線（チーム開発のマージ、デプロイ用ブランチへの push）は `autoMode.hard_deny` に書く。分類器は skill の起動そのものを、commit や push の明示的な意図とは見なさない（[auto mode の設定](https://code.claude.com/docs/en/auto-mode-config): "General requests don't count as explicit intent."）
3. **モデルが自分の判断で起動した skill は、指示とみなさない。** `prototype` や `wizard` は、利用者が起動した流れの途中で呼ばれた場合だけ範囲に含める

リポジトリの種類ごとの線引きの例:

| 操作 | 個人開発 | チーム開発（業務委託など） |
|---|---|---|
| commit・作業ブランチへの push・PR 作成 | 可 | 可 |
| GitHub Issues（起票・ラベル・assign・close） | 可 | 可（チームが読む前提で書く） |
| マージ | 可（CI 通過と AI レビュー対応の後） | 不可。「マージ可能」と報告して人間に渡す |

変えないもの:

- main やデプロイ用ブランチへ直接 push しない。`implement` は今のブランチに commit するので、先に作業ブランチを切る
- force push・squash / rebase merge・branch protection の回避はしない
- PR 本文の言語、署名、AI であることの明記は、各リポジトリの規約に従う。`triage` は投稿の冒頭に `> *This was generated by AI during triage.*` を付ける規定があるので、AI を名乗らない規約のリポジトリではこの行を外す
- リポジトリ側の規約（`.claude/rules/`、project の settings）がさらに厳しい場合は、そちらに従う

### 6.3 チーム開発で使うときの追加の注意

- setup は tracker にラベルを作る。チームのリポジトリにラベルが増えることを、事前に伝えておく
- Issue をすでに別のツールで管理しているチームでは、正本を二重にしない。GitHub Issues に起票するのは、これらの skill で spec と ticket を作るときだけに絞る
- push でデプロイが走るブランチを、最初に洗い出しておく（`.github/workflows/*.yml` の `on.push.branches`。Git 連携のホスティングは workflow に現れないので別に確かめる）

## 7. ルールの優先順位

1. リポジトリの規約（CLAUDE.md・AGENTS.md・`.claude/rules/`・project の settings）
2. 利用者のグローバルの規約（`~/.claude/CLAUDE.md` など）
3. skill の SKILL.md の手順

- 1 と 2 が食い違ったら、厳しい方に従う
- 1・2 と 3 が食い違ったら、1・2 に従う（skill の手順より、利用者とリポジトリの規約が優先する）

## 8. 名前が重なる skill

| 名前 | 重なる相手 | 使い分け |
|---|---|---|
| `code-review` | Claude Code 組み込みの `/code-review`（バグの検出） | plugin 版は、基準点からの差分を Standards（規約）と Spec（spec どおりか）の 2 軸で見る。見ている物が違うので、両方を使ってよい |
| `research` | 利用者が自分で置いた同名の skill（ある場合） | plugin 版は background agent が一次情報を調べ、出典つきの Markdown をリポジトリに残す |
| `handoff` | 利用者が自分で置いた同名の skill（ある場合） | plugin 版は会話を圧縮した引き継ぎ文書を書く |

`implement` と `implement-spec` は内部で Skill tool に `"code-review"` と `"tdd"` を渡す。同名の skill があるとき、どれが呼ばれるかは確かめていない。実行後に、2 軸のレビューが走ったかを出力で確かめる。

## 出典

| 情報源 | URL |
|---|---|
| mattpocock/skills（v1.3.1） | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336 （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| ask-matt/SKILL.md・PHASE-BOUNDARIES.md | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/ask-matt （2026-11-15 確認） |
| wayfinder/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wayfinder/SKILL.md （2026-11-15 確認） |
| Skills（Claude Code docs） | https://code.claude.com/docs/en/skills （2026-11-15 確認） |

### 確認できなかった事項

- 同名の skill があるとき、`implement` が内部で呼ぶ `code-review` がどれに解決されるか
- エディタの外部エージェント経由で `/clear` が使えるかどうかは、クライアントの実装と版で変わる

- 関連: [skill の一覧](README.md) / [Matt Pocock の AI コーディング環境](../matt-pocock-dev-environment.md) / [Skills ガイド](../skills.md)
