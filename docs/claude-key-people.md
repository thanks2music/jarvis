# Claude の開発を引っ張る人たち — フォローして学ぶためのガイド

Claude と Claude Code を使った開発で、2025〜2026 年に目立った貢献をしている人を 14 人選び、「何をした人か」「どこで発信しているか」「何を学べるか」をまとめた。Anthropic 社内で Claude・Claude Code・MCP・Agent Skills を作った人と、社外で Claude を使った開発手法やツールを広めている人の 2 群に分けている。

- **調査日**: 2026-11-14（JST）
- **調べ方**: deep-research のワークフロー（ウェブ検索と、主張ごとに 3 票で反証を試みる検証）で候補を絞った。そのうえで、所属と役職は本人の X のプロフィール（fxtwitter の公開 API `https://api.fxtwitter.com/<ハンドル>` で取得）と Anthropic の公式記事で確かめた。リポジトリの数字は GitHub API の値である（スター数は `GET /repos/{owner}/{repo}` の `stargazers_count`、コミット数は `GET /repos/{owner}/{repo}/contributors`）
- **選び方**: 一次情報（公式記事・本人のブログ・リポジトリ・本人のプロフィール）で貢献を確かめられた人だけを載せた。スター数やフォロワー数は人気の目安であり、手法の良し悪しを示すものではない
- **注意**: 役職や所属は変わりやすい。2026 年だけでも、Claude Code の中心人物 3 人が Anthropic を離れている（§3）。数字は 2026-11-14 時点の値である

---

## 1. Anthropic 社内 — Claude を作っている人

### Boris Cherny — Claude Code の作者

| 項目 | 内容 |
|---|---|
| 何者か | Claude Code の作者。2026 年の報道では「Head of Claude Code」と紹介されている（[Lenny's Newsletter, 2026-02](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens)）。本人の X のプロフィールは「Claude @anthropicai」 |
| 発信場所 | X [@bcherny](https://x.com/bcherny)（フォロワー約 64 万）／ [borischerny.com](https://borischerny.com) |
| 学べること | Claude Code の設計思想と、作った本人の使い方。AI Engineer World's Fair 2025 の講演 [Claude Code: The Evolution of Agentic Coding](https://ai.engineer/talks/claude-code-the-evolution-of-agentic-coding) |
| 根拠 | 公開リポジトリ `anthropics/claude-code`（★約 15.6 万）の貢献者で、bot を除くと 2 位。ただし、このリポジトリに製品のソースコードは無く、CHANGELOG とプラグインが中心である |

### David Soria Parra / Justin Spahr-Summers — MCP の作者

| 項目 | 内容 |
|---|---|
| 何者か | MCP（Model Context Protocol）を Anthropic 社内で作った 2 人。公式発表に「MCP was created at Anthropic by David Soria Parra and Justin Spahr-Summers.」とある（[2024-11-25](https://www.anthropic.com/news/model-context-protocol)）。2 人とも、X のプロフィールでは現在も Anthropic 所属 |
| 発信場所 | David: X [@dsp_](https://x.com/dsp_)（プロフィールは「Member of Technical Staff @AnthropicAI. Co-Creator of modelcontextprotocol.io」）／ [experimentalworks.net](https://experimentalworks.net/)。Justin: X [@jspahrsummers](https://x.com/jspahrsummers)（本人いわく X はほぼ使わない）／ [jspahrsummers.com](https://jspahrsummers.com) |
| 学べること | MCP の仕様と、その設計判断の背景（[modelcontextprotocol.io](https://modelcontextprotocol.io)） |
| 補足 | MCP は 2025-12 に Linux Foundation 傘下の Agentic AI Foundation へ移管された。作者が 2 人であることは変わらない |

### Barry Zhang / Erik Schluntz — 「Building effective agents」の著者

| 項目 | 内容 |
|---|---|
| 何者か | エージェント設計の定番記事 [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（2024-12）の著者（記事の署名は「Written by Erik S. and Barry Zhang」）。Barry Zhang は Agent Skills の公式記事の共著者でもある |
| 発信場所 | Erik: X [@ErikSchluntz](https://x.com/ErikSchluntz)（Member of Technical Staff）／ [erikschluntz.com](http://erikschluntz.com)。Barry の X のハンドルは確認できなかった |
| 学べること | workflow と agent の使い分け、単純な構成から始める考え方。記事の冒頭には、2024-12 以降の道具立ての変化について、Claude Managed Agents の記事を参照するよう注記が追加されている |

### Mahesh Murag / Barry Zhang / Keith Lazuka — Agent Skills の作者

| 項目 | 内容 |
|---|---|
| 何者か | Agent Skills を発表した公式記事 [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)（2025-10-16）の著者 3 人。2025-12-18 に、Agent Skills はオープン標準として公開された（[agentskills.io](https://agentskills.io)） |
| 発信場所 | Mahesh: X [@maheshmurag](https://x.com/maheshmurag)（プロフィールは「pm @ anthropic, skills & memory」） |
| 学べること | スキルの段階的な読み込み（progressive disclosure）の設計。JARVIS の [skills-progressive-disclosure.md](skills-progressive-disclosure.md) の元になった考え方である |

### Lance Martin — Agent Skills のリポジトリの主要メンテナー

| 項目 | 内容 |
|---|---|
| 何者か | Anthropic の Member of Technical Staff（X のプロフィール「MTS @anthropicai」）。公式のスキル集 [anthropics/skills](https://github.com/anthropics/skills)（★約 19.4 万）でコミット数が最も多い（17 件。2 位は Keith Lazuka の 13 件） |
| 発信場所 | X [@RLanceMartin](https://x.com/RLanceMartin)（フォロワー約 4.3 万）／ [rlancemartin.github.io](https://rlancemartin.github.io/) |
| 学べること | 公式スキル集のスキルの書き方（リポジトリそのものが手本になる） |
| 補足 | コミット数は設計への貢献度そのものではない |

---

## 2. 社外 — Claude を使った開発手法を広めている人

### Matt Pocock — mattpocock/skills・Sandcastle

| 項目 | 内容 |
|---|---|
| 何者か | TypeScript の教育者。AI コーディングの講座「AI Hero」を運営する |
| 貢献 | [mattpocock/skills](https://github.com/mattpocock/skills)（2026-02 作成、★約 32.4 万）。Claude Code の公式プラグインマーケットプレイスに掲載されている。サンドボックスでエージェントを動かすライブラリ [Sandcastle](https://github.com/mattpocock/sandcastle) も作っている |
| 発信場所 | X [@mattpocockuk](https://x.com/mattpocockuk)／ [aihero.dev](https://www.aihero.dev)／ YouTube |
| 学べること | grilling → spec → tickets → TDD → review という一連の流れ、AFK エージェント（Ralph）、ソフトウェアファクトリー。本人の環境は [matt-pocock-dev-environment.md](matt-pocock-dev-environment.md) を参照 |

### Jesse Vincent — Superpowers

| 項目 | 内容 |
|---|---|
| 何者か | Prime Radiant 所属（README に「built by Jesse Vincent and the rest of the folks at Prime Radiant」）。GitHub は [obra](https://github.com/obra) |
| 貢献 | Claude Code 向けのスキル集 [Superpowers](https://github.com/obra/superpowers)（2025-10-09 公開、★約 31.7 万）。brainstorm → plan → implement の流れに、git worktree、サブエージェントへのタスクの分配、RED/GREEN の TDD を組み込んでいる。公式マーケットプレイスにも掲載されている（`superpowers@claude-plugins-official`） |
| 発信場所 | ブログ [blog.fsck.com](https://blog.fsck.com)／ X [@obra](https://x.com/obra) |
| 学べること | 公開時の記事 [Superpowers](https://blog.fsck.com/2025/10/09/superpowers/)。スキルで開発の流れを強制する設計 |

### Kieran Klaassen — Compound Engineering

| 項目 | 内容 |
|---|---|
| 何者か | Every の社員（X のプロフィールは「frontier team @every」。Every の記事では、メールプロダクト Cora のゼネラルマネージャーと紹介されている） |
| 貢献 | 「1 つの作業が次の作業を楽にするようにする」という開発哲学 Compound Engineering の提唱者。プラグイン [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin)（★約 2.6 万、Trevin Chow と共同でメンテナンス） |
| 発信場所 | X [@kieranklaassen](https://x.com/kieranklaassen)／ [every.to](https://every.to)／ [frontier.every.to](https://frontier.every.to) |
| 学べること | ガイド [Compound Engineering](https://every.to/p/compound-engineering)（2026-01 公開）。レビューの指摘を仕組みに戻して、次の作業を楽にするやり方 |

### Simon Willison — Claude の使い方を最も多く記録している人

| 項目 | 内容 |
|---|---|
| 何者か | Django の共同作者、Datasette の作者 |
| 貢献 | ブログで Claude と Claude Code の検証を続けている（タグ `claude-code` の記事だけで 135 本、2026-11-09 時点）。2026-07 の AI Engineer World's Fair では、Claude Code チームとの対談の司会を務めた（[記事](https://simonwillison.net/2026/jul/21/cat-and-thariq/)）。CLI ツール [llm](https://github.com/simonw/llm)（★約 1.3 万）の作者でもある |
| 発信場所 | [simonwillison.net](https://simonwillison.net/)（[claude-code タグ](https://simonwillison.net/tags/claude-code/)）／ X [@simonw](https://x.com/simonw)（フォロワー約 25 万） |
| 学べること | 新しいモデルや機能が出るたびの、具体的で再現できる検証記事 |

### Geoffrey Huntley — Ralph ループ

| 項目 | 内容 |
|---|---|
| 何者か | エンジニア・ブロガー |
| 貢献 | AI エージェントを bash のループで回し続ける手法「Ralph」を提唱した（[ghuntley.com/ralph](https://ghuntley.com/ralph/)、2025-07-14）。記事は Ralph を「In its purest form, Ralph is a Bash loop」と定義し、`while :; do cat PROMPT.md | claude-code ; done` という例を示している。この手法は Matt Pocock などに広く取り入れられた |
| 発信場所 | [ghuntley.com](https://ghuntley.com/)／ X [@GeoffreyHuntley](https://x.com/GeoffreyHuntley)（フォロワー約 9.1 万）／ [how-to-build-a-coding-agent](https://github.com/ghuntley/how-to-build-a-coding-agent)（★約 5.9k） |
| 学べること | 人がそばにいないときにエージェントを動かす手法（AFK）と、その限界 |

### Dex Horthy — context engineering・12-Factor Agents（現在は Factory 所属）

| 項目 | 内容 |
|---|---|
| 何者か | HumanLayer（YC 出身のスタートアップ）の出身。**2026-11 時点の X のプロフィールは「MTS @factory」**で、コーディングエージェントの会社 Factory に移っている（移った時期は確認できていない） |
| 貢献 | [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)（★約 2.7 万）と、Claude Code を使った開発の進め方の記事 [Advanced Context Engineering](https://humanlayer.dev/blog/advanced-context-engineering)（research → plan → implement の流れ）で、context engineering という考え方を広めた |
| 発信場所 | X [@dexhorthy](https://x.com/dexhorthy)／ ポッドキャスト「AI That Works」 |
| 学べること | コンテキストの使い方の設計。Pragmatic Engineer の対談記事 [Context engineering with Dex Horthy](https://newsletter.pragmaticengineer.com/p/context-engineering-with-dex-horthy) |
| 補足 | 現在は Claude 以外のエージェントの会社にいる。考え方は Claude Code にも当てはまるため載せた |

---

## 3. 参考 — 2026 年に Anthropic や Claude から離れた人

過去の発信は今も参考になるが、「今の Claude の中の人」ではない。

| 人物 | 元の役割 | 2026 年の変化 | 根拠 |
|---|---|---|---|
| Cat Wu（[@_catwu](https://x.com/_catwu)） | Claude Code のプロダクトを率いた | 2026-10-30 に Anthropic を離れ、OpenAI の Core Products に移った | X のプロフィール「core products @openai, prev: claude code @anthropic」。報道は [The Next Web](https://thenextweb.com/news/cat-wu-claude-code-anthropic-openai-core-products) など |
| Thariq Shihipar（[@trq212](https://x.com/trq212)） | Claude Code のエンジニア | 2026-10-24 に退社を発表。次の行き先は未公表 | X のプロフィール「formerly Claude Code @anthropicai」 |
| Peter Steinberger（[@steipete](https://x.com/steipete)） | OpenClaw（旧 Clawdbot）の作者。Clawdbot という名前には Anthropic が異議を唱え、改名した | 2026-02 に OpenAI に入社 | X のプロフィール「@OpenClaw + @OpenAI」。[The Register](https://www.theregister.com/2026/02/16/open_ai_grabs_openclaw) |

---

## 4. どこから始めるか

- **Claude Code を作った人の考え方を知りたい**: Boris Cherny の X と講演
- **スキルで開発の流れを組みたい**: Matt Pocock の `mattpocock/skills` と Jesse Vincent の Superpowers を読み比べる。公式の考え方は Agent Skills の記事（Mahesh Murag ほか）
- **エージェントを長く・自律的に動かしたい**: Geoffrey Huntley の Ralph → Matt Pocock の Sandcastle → Dex Horthy の context engineering
- **新機能の検証を追いたい**: Simon Willison のブログの `claude-code` タグ
- **MCP を深く知りたい**: David Soria Parra と modelcontextprotocol.io

---

## 5. 確かめられなかったこと

- Boris Cherny の 2026-11 時点の正式な肩書き（報道は「Head of Claude Code」、X のプロフィールは「Claude @anthropicai」）
- Cat Wu の後に Claude Code のプロダクトを率いている人
- Barry Zhang・Keith Lazuka の現在の役職と X のハンドル
- Dex Horthy が Factory に移った時期
