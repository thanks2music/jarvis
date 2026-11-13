# Matt Pocock の AI コーディング環境（2025〜2026）

TypeScript の教育者で、`mattpocock/skills`（Claude Code などのエージェント向けスキル集）の作者でもある Matt Pocock が、AI コーディングをどんな環境で行っているかを、本人の発言から確かめた記録である。

- **調査日**: 2026-11-14
- **調べ方**: X（@mattpocockuk）はログインしたブラウザで `from:mattpocockuk` を検索し、各投稿の原文と日時を取得した（X の画面は自動翻訳されるため、原文は公開 API の fxtwitter で取り直した）。あわせて、aihero.dev の記事、GitHub の `mattpocock/skills`・`mattpocock/sandcastle`、deep-research のワークフロー（ウェブ検索と主張ごとの反証チェック）の結果を照合した
- **注意**: 本人が「自分の開発環境」をまとめて公開したページは無い。以下は散らばった投稿をつなぎ合わせたものである。X の検索は網羅的ではないため、拾えていない投稿がありうる

---

## 1. 結論

| 時期 | 環境 |
|---|---|
| 〜2025 年 | Windows + WSL 上の Cursor が中心 |
| 2025-10 / 2026-01 | **Cursor をやめて VS Code + Claude Code（ターミナル）へ移った**。理由は WSL での Cursor の遅さと不安定さ |
| 2026-01〜07 | VS Code（エディタ・diff の確認・Markdown の閲覧）＋ ターミナルの Claude Code。席を外している間のエージェント（AFK）は bash ループの「Ralph」で回し、作業の 8 割が AFK になった |
| 2026-06〜 | 自作の LLM wiki を司令塔にし、そこから全リポジトリを操作。タスク管理は Todoist |
| **2026-08〜（最新）** | **ローカルの開発環境をやめ、月 £20 の Hetzner の VM に移った。操作は Discord から行う**（「My IDE is Discord」）。複数リポジトリの作業は Home Repo（スキル・steering ファイル・wiki を置く 1 つのリポジトリ）から指示する |

- **Zed・Ghostty・tmux を自分で使っているという発言は見つからなかった**。tmux は、エージェントが別のエージェントを起動する手段の例として挙げているだけである（2026-08-05）
- エージェントは一貫して **Claude Code**。2026 年には Codex 向けの対応（スキルの修正など）もしているが、Codex へ乗り換えたという発言は無い

---

## 2. 時系列の一次情報

### 2.1 Cursor から VS Code へ（WSL）

- **2025-06-18**: 「Cursor が更新されるたびに WSL 用の VSCode server をダウンロードし直すことになり、毎回約 8 分かかる」
  > Every time Cursor updates (which is a lot) / I have to download this VSCode server for WSL / Which takes around 8 minutes each time
  — [x.com/mattpocockuk/status/1935262441186934826](https://x.com/mattpocockuk/status/1935262441186934826)
- **2025-10-03**: Cursor を 1 週間やめて、Claude Code + VS Code を試す
  > Dropping Cursor for the week and trying Claude Code + VSCode. … I find Claude Code far superior to Cursor's agent. … I like being able to switch to CLI when needed. … Cursor is still a weighty beast (might be a WSL-specific thing).
  — [x.com/mattpocockuk/status/1974176232968171717](https://x.com/mattpocockuk/status/1974176232968171717)
- **2026-01-19**: もう一度 Cursor をやめて VS Code へ
  > Saying bye-bye to Cursor for a bit. / Can't abide the 90 second loading time on WSL / Multi-line edits don't work / … Good NES doesn't matter so much when Claude is doing all the work / Sup, VSCode
  — [x.com/mattpocockuk/status/2013196846357762128](https://x.com/mattpocockuk/status/2013196846357762128)
- **2026-01-21**: コードのレビューと diff は「In my IDE, or in GitHub」 — [status/2013933866961060197](https://x.com/mattpocockuk/status/2013933866961060197)
- **2026-02-21**: 「VSCode's overall reliability beats the pants off Cursor.」 — [status/2025249859154923822](https://x.com/mattpocockuk/status/2025249859154923822)
- **2026-04-24**: Markdown を何で開くかと聞かれて「VSCode」 — [status/2047708861302251773](https://x.com/mattpocockuk/status/2047708861302251773)

**OS について**: 本人が「Windows を使っている」と明言した投稿は無い。ただし WSL での問題を 2025-06・2025-10・2026-01 の 3 回書いており、ローカル環境は Windows + WSL だったと判断してよい。

### 2.2 ターミナルの Claude Code と AFK エージェント

- **2026-01-22**: 「AFK Ralph in a bash loop is SO much better than the Claude Code plugin.」 — [status/2014277127244296688](https://x.com/mattpocockuk/status/2014277127244296688)
- **2026-02-05**: Claude Code の hooks は、ターミナルを見る必要があるときに「ding」と鳴らすのに使っている — [status/2019460237237813571](https://x.com/mattpocockuk/status/2019460237237813571)
- **2026-02-25**: 「My terminal history: gh issue create / gh issue create / pnpm ralph / …」 — [status/2026669944553816275](https://x.com/mattpocockuk/status/2026669944553816275)
- **2026-03-05**: 「probably 80% is now AFK and 20% is human in the loop」 — [status/2029484601698107629](https://x.com/mattpocockuk/status/2029484601698107629)
- **2026-07-22**: 「In Claude Code in the terminal, clearing a session is the same as creating a new session.」 — [status/2079887646403280928](https://x.com/mattpocockuk/status/2079887646403280928)
- **2026-07-23**: 同じターミナルで複数のエージェントを管理する道具について、「I'm happy with Claude agents but it's not for everyone. Also keen to try herdr.」 — [status/2080228104497201628](https://x.com/mattpocockuk/status/2080228104497201628)
- **2026-08-05**: エージェントに別のエージェントを起動させる手段を募集。「`/claude-handoff` skill which I use a LOT」「/spawn would detect what tool you use (tmux/cmux etc)」 — [status/2084935574943576532](https://x.com/mattpocockuk/status/2084935574943576532)

### 2.3 wiki を司令塔にする運用

- **2026-06-30**: 「I'm now using the wiki as the ONLY place I run Claude Code / I use it as a master controller for all of my repos, kicking off cross-repo tasks and using Todoist as a task tracker」 — [status/2071901405690949874](https://x.com/mattpocockuk/status/2071901405690949874)
- **2026-10-19**: 「3 months on, and my personal wiki has become critical infrastructure for my business.」。中身は「just a Karpathy-style LLM wiki」 — [status/2112131671097020895](https://x.com/mattpocockuk/status/2112131671097020895) / [status/2112132602383802799](https://x.com/mattpocockuk/status/2112132602383802799)
- **2026-11-03**: 領域ごとに長く続くスレッドを持ち、各エージェントが wiki を育てるので、会話履歴を捨ててハーネスを切り替えられる — [status/2117571010660581804](https://x.com/mattpocockuk/status/2117571010660581804)
- **2026-11-10**: **Home Repo** の紹介。スキル・steering ファイル・wiki を 1 つのリポジトリに置き、そこでエージェントを動かす。他のリポジトリへのポインタは AGENTS.md に書く
  > I have a single repo (the home) where all of my skills, steering files, wiki etc live. / I run my agent in the home repo, and then inside AGENTS.md I have pointers to the other repos
  — [status/2120260969750540327](https://x.com/mattpocockuk/status/2120260969750540327)

### 2.4 ローカルをやめて VM と Discord へ（最新）

- **2026-08-08**: 「Getting all my agent interactions off my PC and into remote boxes, controllable via Discord」 — [status/2086104430412181587](https://x.com/mattpocockuk/status/2086104430412181587)
- **2026-08-12**: 「My IDE is Discord」 — [status/2087555290174566491](https://x.com/mattpocockuk/status/2087555290174566491)
- **2026-08-17**: 「Having a lot of fun with Sandman / Added a /handoff command for spawning new Discord threads」（Sandman が何かの説明は見つからなかった） — [status/2089291938868457688](https://x.com/mattpocockuk/status/2089291938868457688)
- **2026-08-22**: 「I'm moving away from my local dev setup / Makes zero sense to me now」 — [status/2091194428639621284](https://x.com/mattpocockuk/status/2091194428639621284)。同じスレッドへの本人の返信:
  - 移行先は「VM on cloud, connected via Discord」 — [status/2091202407166320710](https://x.com/mattpocockuk/status/2091202407166320710)
  - 「It's just a £20/month Hetzner box」（Mac mini をこのために買うのはやめておけ、とも） — [status/2091208319792771494](https://x.com/mattpocockuk/status/2091208319792771494)
  - 「I don't run local inference」（ローカル推論の話ではなく、ローカルのディスクでの開発をやめる話） — [status/2091207355450974582](https://x.com/mattpocockuk/status/2091207355450974582)
  - 今も人が操縦する「in the loop」で使っており、ファクトリー型の構成も動かせる — [status/2091202504792900019](https://x.com/mattpocockuk/status/2091202504792900019)
  - 利点は「Seamless collaboration with other humans / Never worry about a worktree again / Scale up and up / Software factory time」 — [status/2091208898392752610](https://x.com/mattpocockuk/status/2091208898392752610)
  - 画面を目で確かめる作業は「preview deploys and /prototype feel fine here」 — [status/2091207245065273608](https://x.com/mattpocockuk/status/2091207245065273608)

### 2.5 Sandcastle（ファクトリーの部品）

- `mattpocock/sandcastle` は、AI コーディングエージェントを隔離したサンドボックスで動かす本人製の TypeScript ライブラリである。README には「Great for parallelizing multiple AFK agents」とある。サンドボックスは OS 標準の仕組み（Linux と WSL2 は Bubblewrap、macOS は Seatbelt）、Docker / Podman、クラウド（Daytona・E2B・Fly.io Sprites・Modal・Vercel）に対応する — [github.com/mattpocock/sandcastle](https://github.com/mattpocock/sandcastle)
- **2026-11-01**: v1 の構想として「Sandcastle helps you build your software factory」「6 built-in harnesses (Claude Code, Codex, etc)」「Support for HITL (over Slack and Discord) as well as AFK runs」「Every skill in my repo becomes an Agent()」 — [status/2116805878187794740](https://x.com/mattpocockuk/status/2116805878187794740)
- ただし、本人が自分の日々の作業で Sandcastle を並列に回していると明言した投稿は見つからなかった。2026-01 の Ralph の記事では、Docker Desktop のサンドボックス（`docker sandbox run claude`）で隔離する方法を教えている（[aihero.dev/getting-started-with-ralph](https://aihero.dev/getting-started-with-ralph)、[aihero.dev/tips-for-ai-coding-with-ralph-wiggum](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum)）

### 2.6 計画の置き場所

- 2025-10 頃から「Instead of markdown files, I've been getting my AI to save plans in GitHub issues.」と書いている（[status/1976932157521379574](https://x.com/mattpocockuk/status/1976932157521379574)）。2026 年のワークショップでも、PRD をローカルの Markdown から GitHub Issues に移す回がある（[aihero.dev/workshops/day-5-ralph-dj2dh](https://www.aihero.dev/workshops/day-5-ralph-dj2dh)）
- 一方、Ralph の記事の例はローカルの `prd.json` で、`mattpocock/skills` の docs も「Local markdown is a full option, not a fallback」としている。**いつも GitHub Issues というわけではない**

---

## 3. 先に出していた回答の検証結果

2026-11-14 に JARVIS がいったん出した回答（ウェブ検索ベース）を、上の一次情報で検証した。

| 先の回答 | 判定 | 補足 |
|---|---|---|
| 2025-10-03 に Cursor → Claude Code + VS Code を試し、WSL に言及 | ✅ 正しい | 原文で確認 |
| OS は Windows + WSL の可能性が高い | ✅ 正しい（明言は無い） | 2025-06・2026-01 にも WSL の投稿がある |
| エディタは VS Code で、ターミナルと併用 | ✅ 正しい（2026-08 まで） | **2026-08 以降は VM + Discord が主で、情報が古かった** |
| Zed・Ghostty・tmux の発言は無い | ✅ 正しい | tmux は他人向けの例として触れただけ |
| wiki を司令塔にし、Todoist でタスク管理 | ✅ 正しい | 2026-11 には「Home Repo」として整理されている |
| AFK エージェントを Sandcastle で隔離し並列実行 | ⚠️ 言い過ぎ | Sandcastle の用途としては正しい。本人が自分で並列運用していると明言した投稿は無い |
| 計画を GitHub Issues に保存 | ⚠️ 限定が要る | よく使う選択肢の一つで、常にではない |
| 「VS Code（WSL）＋ Claude Code の CLI が基本」というまとめ | ❌ 最新ではない | 最新は「Hetzner の VM ＋ Discord ＋ Home Repo」 |

---

## 4. 確かめられなかったこと

- VM の中で使っているツール（Discord と Claude Code をつなぐ仕組み。Sandman が自作のボットかどうか）
- VM に移った後も、ローカルの VS Code を使う場面があるか（2026-08-22 の返信では、画面の確認は preview deploy と `/prototype` で足りるとしている）
- VM の OS
- 2026-07-16 の YouTube 動画で「Opus 4.8 on medium effort」と話したという情報は、文字起こしサイト経由の二次情報で、動画そのものでは確かめていない（[youtube.com/watch?v=M6mYodf0dJM](https://www.youtube.com/watch?v=M6mYodf0dJM)）
