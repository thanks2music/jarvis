# setup-matt-pocock-skills — リポジトリに issue tracker・triage ラベル・ドメイン文書の置き場を設定する skill

> 出典（一次情報）:
> - [setup-matt-pocock-skills/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/SKILL.md) — skill 本体
> - [issue-tracker-github.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) / [issue-tracker-gitlab.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-gitlab.md) / [issue-tracker-local.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md) — tracker 別の雛形
> - [triage-labels.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/triage-labels.md) — ラベル対応表の雛形
> - [domain.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/domain.md) — ドメイン文書の読み方の雛形
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- engineering 系 skill が前提にする設定を、リポジトリごとに 1 回だけ作る skill である（`SKILL.md:9-13`）。
- 決めるのは 3 つ。issue tracker（GitHub / GitLab / ローカル markdown / その他）、triage ラベルの語彙、ドメイン文書の配置である（`SKILL.md:38-61`）。
- 結果は `docs/agents/*.md` と、`CLAUDE.md` か `AGENTS.md` の `## Agent skills` ブロックに書く（`SKILL.md:65-114`）。
- 決定的なスクリプトではない。調べて、提示して、ユーザーの確認を取ってから書く（`SKILL.md:15`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:setup-matt-pocock-skills` で起動）。`disable-model-invocation: true`（`SKILL.md:4`） |
| 呼び出し方 | `/mattpocock-skills:setup-matt-pocock-skills` |
| 内部で呼ぶ skill | なし（`triage` skill が入っているかを確認するだけ。`SKILL.md:29`） |
| 外部への書き込み | ファイル（`docs/agents/*.md`、`CLAUDE.md` / `AGENTS.md`）、GitHub / GitLab のラベル作成 |

## 3. いつ使うか・使わないか

- **使う**: engineering 系 skill を初めて使う前に、リポジトリごとに 1 回（`SKILL.md:3`）。`to-spec`・`to-tickets`・`triage`・`wayfinder`・`code-review`・`implement-spec` は、tracker の情報が無ければ「この skill を実行せよ」とユーザーに伝える作りである（例: `to-tickets/SKILL.md:11`、`triage/SKILL.md:43`）。
- **再実行する**: tracker を切り替えるとき、または最初からやり直すとき（`SKILL.md:118`）。日常の調整は `docs/agents/*.md` を直接編集すればよい（同）。
- **使わない**: grilling の頻度や口調など、他 skill の好みを設定する用途には使わない。設定できるのは tracker・ラベル・文書配置の 3 つだけである（公式解説ページ「Common questions」）。

## 4. 流れ

1. **調査（Explore）**: 次を読む（`SKILL.md:21-30`）。
   - `git remote -v` と `.git/config`（GitHub か、どのリポジトリか）
   - ルートの `AGENTS.md` / `CLAUDE.md`、既存の `## Agent skills` セクションの有無
   - `GLOSSARY.md` / `GLOSSARY-MAP.md`、`docs/adr/`、`src/*/docs/adr/`
   - `docs/agents/`（前回の出力）、`.scratch/`（ローカル markdown 運用の形跡）
   - `triage` skill が入っているか（Section B を実行するかが決まる）
   - monorepo の兆候（`pnpm-workspace.yaml`、`package.json` の `workspaces`、`packages/*`）
2. **提示と質問**: 1 セクションにつき 1 回答で順に進める。推奨案を先頭に置き、調査で決まったセクションは飛ばす（`SKILL.md:34-36`）。
   - **Section A: issue tracker**。remote が GitHub なら GitHub、GitLab なら GitLab を提案する。選択肢は次の 4 つ（`SKILL.md:42-47`）。
     - **GitHub**: GitHub Issues。`gh` CLI を使う
     - **GitLab**: GitLab Issues。`glab` CLI を使う
     - **Local markdown**: `.scratch/<feature>/` 配下のファイル。1 人のプロジェクトや remote の無いリポジトリ向け
     - **Other**（Jira、Linear など）: ユーザーが 1 段落で運用を説明し、それを文章のまま記録する
   - GitHub / GitLab の雛形には「PR（MR）を要望の受付窓口として扱う」フラグがあり、既定は off。skill はこれを話題にしない（`SKILL.md:49`）。
   - **Section B: triage ラベル**。`triage` が入っていなければ丸ごと飛ばす。入っていれば「既定のラベルのままでよいか」を 1 問だけ聞く（`SKILL.md:51-57`）。既定は `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix` の 5 つ。
   - **Section C: ドメイン文書**。既定は single-context（ルートに `GLOSSARY.md` と `docs/adr/`）で、聞かずに書く。monorepo の兆候があるときだけ multi-context（`GLOSSARY-MAP.md`）を提案する（`SKILL.md:59-61`）。
3. **確認と編集（Confirm and edit）**: `## Agent skills` ブロックと `docs/agents/*.md` の下書きを見せ、ユーザーが編集してから書く（`SKILL.md:65-70`）。
4. **書き込み（Write）**: 書き込み先ファイルを選び、ブロックと文書を書き、必要ならラベルを作る（`SKILL.md:72-114`。詳細は §5）。
5. **完了（Done）**: どの engineering skill がこれらのファイルを読むかを伝える（`SKILL.md:118`）。

## 5. 書き込むもの・副作用

| 書き込み先 | 内容 | 根拠 |
|---|---|---|
| `CLAUDE.md` または `AGENTS.md` | `## Agent skills` ブロック（`### Issue tracker` / `### Triage labels` / `### Domain docs`）。既存のブロックがあれば置き換え、重複させない | `SKILL.md:82-100` |
| `docs/agents/issue-tracker.md` | tracker の運用手順。GitHub / GitLab / ローカルは雛形から、Other はユーザーの説明から書く | `SKILL.md:49`, `SKILL.md:106-114` |
| `docs/agents/triage-labels.md` | 5 つの役割とラベル文字列の対応表。`triage` が入っていて Section B を実行したときだけ | `SKILL.md:102`, `SKILL.md:111` |
| `docs/agents/domain.md` | `GLOSSARY.md` と ADR の読み方、配置 | `SKILL.md:112` |
| GitHub / GitLab のラベル | Section B を実行し、tracker が GitHub か GitLab のとき、足りないラベルを `gh label create` / `glab label create` で作る | `SKILL.md:104` |

- **書き込み先ファイルの選び方**（`SKILL.md:74-80`）: `CLAUDE.md` があればそれを編集する。無ければ `AGENTS.md`。どちらも無ければ、どちらを作るかユーザーに聞く。片方があるときにもう片方を新規作成することはしない。
- git commit・branch・push は行わない（SKILL.md に記述なし）。
- GitHub issue は作らない。ラベル作成のみである。

## 6. 前後の skill

- **前**: なし。engineering の流れ全体の前提となる、1 回きりの準備である。
- **後（この設定を読む skill）**: [triage](triage.md)（ラベル語彙）、[to-spec](to-spec.md) と [to-tickets](to-tickets.md)（tracker への公開）、[wayfinder](wayfinder.md)（`issue-tracker.md` の「Wayfinding operations」）、[code-review](code-review.md)、[implement-spec](implement-spec.md)。
- [domain-modeling](domain-modeling.md) が、ここで決めた配置に `GLOSSARY.md` と ADR を後から作る（`domain.md:11`）。
- 外部の手作業が要る設定は [wizard](wizard.md) が担う。

## 7. 注意点

- **公式解説ページとの食い違い**: 公式解説ページ（`docs/engineering/setup-matt-pocock-skills.md`）は「`gh label create` は実行しない」と書く。一方、v1.3.1 の `SKILL.md:104` は Section B を実行した場合に足りないラベルを作ると書く。本書は一次情報の `SKILL.md` に従う。解説ページは古い版の挙動を書いている（推測）。
- **wayfinder 用ラベルは作らない**: `issue-tracker-github.md:41-42` は `wayfinder:map` と `wayfinder:<type>` ラベルを使うが、SKILL.md が作るのは Section B の triage ラベルだけである。
- **`CLAUDE.md` 優先で書く**: 書き込み先はファイルの有無で決まり、動いているハーネスでは決まらない（`SKILL.md:76-80`）。`CLAUDE.md` を `.gitignore` で除外しているリポジトリでは、ブロックはローカルにだけ残り、他の環境には共有されない（推測）。
- **ローカル markdown と GitHub は排他**: どちらか 1 つを選ぶ（公式解説ページ）。
- **プラグインからの起動名**: プラグイン経由では `/mattpocock-skills:setup-matt-pocock-skills` と完全修飾で呼ぶ。他 skill のメッセージ中の `/setup-matt-pocock-skills` は短縮名である。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| issue-tracker-github.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md （同上） |
| issue-tracker-gitlab.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-gitlab.md （同上） |
| issue-tracker-local.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md （同上） |
| triage-labels.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/triage-labels.md （同上） |
| domain.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills/domain.md （同上） |
| 公式解説ページ（二次） | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/setup-matt-pocock-skills.md （同上） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [triage](triage.md) / [to-tickets](to-tickets.md) / [wayfinder](wayfinder.md) / [wizard](wizard.md)
