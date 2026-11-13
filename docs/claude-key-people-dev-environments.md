# Claude の主要人物の開発環境（2025〜2026）

[claude-key-people.md](claude-key-people.md) で選んだ 14 人のうち、Matt Pocock（[matt-pocock-dev-environment.md](matt-pocock-dev-environment.md)）を除く 13 人が、AI コーディングをどんな環境で行っているかを、本人の発言から確かめた記録である。

- **調査日**: 2026-11-14（JST）
- **調べ方**:
  - X は、ログインしたブラウザで `from:<ハンドル>` に環境の語（`ghostty OR tmux OR vscode OR worktree OR terminal OR macbook OR "I use"` など）を組み合わせて検索し、出てきた本人の投稿の原文と返信先を、fxtwitter の公開 API（`https://api.fxtwitter.com/<ハンドル>/status/<ID>`）で取り直した
  - ブログ・講演・ポッドキャストは、deep-research のワークフロー（ウェブ検索と、主張ごとに 3 票で反証を試みる検証）で集めた。Boris Cherny のスレッドの続きは Thread Reader のミラーで読み、スレッドの先頭の投稿は fxtwitter で原文を確かめた
- **注意**:
  - 本人の発言を日付付きで載せている。「2026-11 時点でもそうしている」とは限らない
  - OS・エディタ・ターミナルを本人が明言していることは少ない。分かるのは主に、どのエージェントをどう使っているか、ローカルかクラウドか、である
  - X の検索は網羅的ではない。拾えていない投稿がありうる

---

## 1. 一覧

| 人物 | エージェント・モデル | 動かす場所 | エディタ・ターミナル | OS・マシン |
|---|---|---|---|---|
| Boris Cherny | Claude Code。普段は Opus 5.5 を effort medium で | ターミナルで並列、Web、iOS アプリ、Slack の Claude Tag | IDE はアンインストール（2025-11 頃）。ターミナル名は不明 | 不明 |
| David Soria Parra | Claude Code と Claude Tag（Tag の方が多い） | ターミナルと Slack | Zed が好き（2025-05）。Ghostty を推す返信あり | MacBook（2026-04 に Framework から移行）、nix devenv |
| Simon Willison | Claude Code（主に on the web）と Codex（Desktop・Remote） | クラウドのコンテナ中心。スマホからも操作 | 不明 | M5 Max のノート PC |
| Kieran Klaassen | Claude Code CLI・Codex CLI・Cursor | Mac mini の tmux に ssh。Cursor のホストされたエージェント | Cursor（音声入力の Monologue と組み合わせる） | Mac mini |
| Geoffrey Huntley | 自作のハーネス、opencode、Codex。確認役に Opus | 不明（実験には勤務先 Antithesis の機材を使う） | ターミナル中心（herdr）。VS Code は非常口 | NixOS / Nix |
| Dex Horthy | コーディングは Codex（5.5）に移行し、Fable に Codex のサブエージェントを管理させる。以前は Claude Code | tmux の worktree、GitHub Actions のループ | 以前は JetBrains・Cursor。tmux | 不明（macOS の `say` を使う） |
| Jesse Vincent ほか 7 人 | 不明 | 不明 | 不明 | 不明 |

---

## 2. 人物ごとの詳細

### Boris Cherny（Claude Code の作者）

- **2026-01-02**: 自分のセットアップを公開した。「My setup might be surprisingly vanilla!」（[status/2007179832300581177](https://x.com/bcherny/status/2007179832300581177)）。スレッドの続き（[Thread Reader](https://threadreaderapp.com/thread/2007179832300581177.html)）の内容:
  - ターミナルで Claude Code を 5 セッション並列に動かす。タブに 1〜5 の番号を振り、入力待ちはシステム通知で知る
  - 同時に claude.ai/code（Claude Code on the web）でも 5〜10 セッション
  - ローカルのセッションを `&` で Web に渡し、`--teleport` で行き来する。毎朝 iOS アプリからもセッションを始める
- **2026-03-30**: よく使う機能のスレッド（[status/2038454336355999749](https://x.com/bcherny/status/2038454336355999749)、[Thread Reader](https://threadreaderapp.com/thread/2038454336355999749.html)）の内容:
  - `claude -w` で worktree を作り、「I have dozens of Claudes running at all times」
  - 「I write a lot of my code from the iOS app」
  - `/config` で Remote Control を全セッションで有効にしている
- **2026-05-24**: 一番のコツは auto mode。権限の確認が無くなり、複数のセッションを並列に回す（multi-clauding）土台になる（[status/2058519809214607704](https://x.com/bcherny/status/2058519809214607704)）。Opus 4.7 以降は、多くの作業で Plan Mode を使わない（[status/2058523623665627193](https://x.com/bcherny/status/2058523623665627193)）
- **2026-06-09**: 「After 4.5 came out I uninstalled my IDE when I realized that I'd been doing 100% of my coding in a terminal for a few weeks.」（Opus 4.5 は 2025-11 公開。[status/2064431111154053187](https://x.com/bcherny/status/2064431111154053187)）
- **2026-07-17**: 複数のエージェントを管理するインターフェイスとして、CLI の Agent view・Desktop・iOS / Android・Tag を挙げ、上の段階では `/loop`・`/batch`・dynamic workflows を使う（[status/2077929390806073807](https://x.com/bcherny/status/2077929390806073807)）
- **2026-08-11**: たまった worktree はループで掃除している（[status/2087024157196489117](https://x.com/bcherny/status/2087024157196489117)）
- **2026-09〜10**: Opus 5.5 が日常のモデル（[status/2102439069053747549](https://x.com/bcherny/status/2102439069053747549)）。「95% of the time I stick to medium」、複雑な見た目の作業だけ xhigh / max（[status/2108007305463869649](https://x.com/bcherny/status/2108007305463869649)）
- **2026-09-25**: 「Tag writes >50% of my PRs every day.」データ分析はほぼ 100% を Tag が担う（[status/2103538666597691552](https://x.com/bcherny/status/2103538666597691552)）
- **補足**: Anthropic の社員が自社製品について話しているので、宣伝の要素を含みうる。ターミナルのアプリ名は明言していない（2026-01 のスレッドが、Claude Code のドキュメントの iTerm2 の通知設定にリンクしている程度）

### David Soria Parra（MCP の作者）

- **2025-05-02**: a16z のポッドキャストで、気に入っているエディタとして Zed を挙げた（「for me, there was the Zed code editor, which I really like」、[a16z](https://a16z.com/podcast/mcp-co-creator-on-the-next-wave-of-llm-innovation/)）。メインのエディタだとは言っていない
- **2026-04-28 / 30**: Framework のノート PC（第 2 世代）が壊れ、MacBook にすると決めた（[status/2048938895794962789](https://x.com/dsp_/status/2048938895794962789)、[status/2049877147439800408](https://x.com/dsp_/status/2049877147439800408)）
- **2026-06-12**: 「I use nix devenv」（[status/2065481088147849411](https://x.com/dsp_/status/2065481088147849411)）
- **2026-06-23**: 「I do probably more engineering work with Claude Tag these days than in my terminal, because it's a collaborative space where my team can jump in.」（[status/2069486245990789340](https://x.com/dsp_/status/2069486245990789340)）
- **2026-08-13**: Tabby というターミナルを使い始めた人に「Ghostty ??!!??」と返信した（[status/2087952453119483979](https://x.com/dsp_/status/2087952453119483979)）。Ghostty を使っているとは明言していない

### Simon Willison

- **2025-10-05**: 「My daily drivers are currently Claude Code (on Sonnet 4.5), Codex CLI (on GPT-5-Codex), and Codex Cloud (for asynchronous tasks, frequently launched from my phone.)」。複数のターミナルで、ディレクトリごとにエージェントを YOLO モード（承認なし）で並列に動かす。git worktree はまだ使わず、`/tmp` に checkout し直す（[parallel-coding-agents](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/)）
- **2025-11-06**: 非同期のクラウドエージェントでコードの調査を 1 日 2〜3 件走らせる。手元のマシンを壊したり、非公開のデータを漏らしたりする心配が無いので便利だと書いている（[async-code-research](https://simonwillison.net/2025/Nov/6/async-code-research/)）
- **2026-08-14**: M5 Max のノート PC で、LM Studio を使ってローカルのモデルも動かす（[status/2088361426662637714](https://x.com/simonw/status/2088361426662637714)）
- **2026-08-21**: 「The only thing I trust is an environment that controls what they can do - that's why I use Claude Code for web so much, but I've been experimenting with Apple Containers too」（[status/2090727511751639185](https://x.com/simonw/status/2090727511751639185)）
- **2026-09-20**: 「I've started using Codex Remote to run coding agents on various machines while controlling them from my phone.」（[llm-keys-ui](https://simonwillison.net/2026/Sep/20/llm-keys-ui/)）
- **2026-09-24**: Claude Code on the web を「about a year」使っている（[status/2102929804685390095](https://x.com/simonw/status/2102929804685390095)）
- **2026-08〜10**: Codex Desktop も併用している。料理をしながら、音声だけでブログの機能を作った（[status/2108547065634844839](https://x.com/simonw/status/2108547065634844839)）

### Kieran Klaassen（Compound Engineering）

- **時期不明（Every のガイド）**: 「I always run with skip permissions: alias cc='claude --dangerously-skip-permissions'」。前提は、自分のノート PC で、main から切り離したブランチで、テストがあり、いつでも戻せること（[every.to/guides/compound-engineering](https://every.to/guides/compound-engineering)）。ガイドには日付が無く、共同メンテナーがいるため、この一人称の発話者が Kieran 本人かは署名欄からの推定である
  - 権限確認を省くこの設定は、本人が上の前提条件を付けて使っているものである。真似をする場合は、サンドボックスや使い捨ての環境に限るのが安全である
- **2026-05-11**: やり方は 2 つ。1 つは Cursor で音声入力の Monologue を使い、ループの中で話しながら進める。もう 1 つは背後で夜通し回す方式で、tmux で Claude Code CLI と Codex CLI を動かす（[status/2053895877987807633](https://x.com/kieranklaassen/status/2053895877987807633)）
- **2026-05-21**: 使っている構成を聞かれて「tmux on a mac mini with ssh / cursor hosted agents」（[status/2057505969052209178](https://x.com/kieranklaassen/status/2057505969052209178)）
- **2026-08-18**: 「I love Cursor, still using Claude + codex all the time. But the ios app and agents of cursor are the best」（[status/2089797659544506384](https://x.com/kieranklaassen/status/2089797659544506384)）

### Geoffrey Huntley（Ralph）

- **2026-06-19**: 「harnesses are fungible. use whatever wherever you can get tokens the cheapest」。GLM には opencode を使う（[status/2067975656772718996](https://x.com/GeoffreyHuntley/status/2067975656772718996)）
- **2026-09-20**: herdr（エージェントに対応した tmux）と opencode（複数のモデルを 1 つのハーネスで切り替えられる）を推している（[status/2101524492975796548](https://x.com/GeoffreyHuntley/status/2101524492975796548)）
- **2026-09-27**: スキルは事前に入れない。腹が立つ失敗があったときだけスキルを作らせて手で削り、新しいモデルが出たら消す（[status/2104159902826664199](https://x.com/GeoffreyHuntley/status/2104159902826664199)、[status/2104163643936145547](https://x.com/GeoffreyHuntley/status/2104163643936145547)）
- **2026-10-02 / 07**: 個人のプロジェクトでは Nix と Buck2 を使い、NixOS のマシンテストを回している（[status/2106005786933780795](https://x.com/GeoffreyHuntley/status/2106005786933780795)、[ghuntley.com/nix](https://ghuntley.com/nix/)）
- **2026-10-07**: 「i use my own harness these days」（[status/2107772134219288660](https://x.com/GeoffreyHuntley/status/2107772134219288660)）。立ち上げには Codex のハーネスと自作の underclass を使い、その後は自作の kittens に移る（[status/2107798332655763663](https://x.com/GeoffreyHuntley/status/2107798332655763663)、[status/2107799522566889508](https://x.com/GeoffreyHuntley/status/2107799522566889508)）
- **2026-10-10**: VS Code は「really just a debug escape hatch」（[status/2108956218240958579](https://x.com/GeoffreyHuntley/status/2108956218240958579)）
- **2026-10-19**: 大量の作業は OpenAI で回し、漏れの確認を Opus に任せる（[status/2112246468492869936](https://x.com/GeoffreyHuntley/status/2112246468492869936)）。Claude の $200 のサブスクを複数持ち、デザインの作業に使う（[status/2112010656186818636](https://x.com/GeoffreyHuntley/status/2112010656186818636)）
- **2026-09-01**: 勤務先の Antithesis が、実験用に「racks of hardware」を提供してくれていると書いている（[status/2094651317981794449](https://x.com/GeoffreyHuntley/status/2094651317981794449)）

### Dex Horthy（context engineering）

- **2026-08-01**: 自分の遍歴をまとめた（[status/2083582284658245837](https://x.com/dexhorthy/status/2083582284658245837)）
  1. ChatGPT からのコピペ → JetBrains、Cursor の補完
  2. Codebuff CLI + JetBrains（読む）+ Cursor（仕上げ）
  3. ターミナルの Claude Code + JetBrains（デバッグ）
  4. tmux の worktree で Claude を 4 つ、5 つ目が全コミットを main にマージ
  5. Claude Code で research → plan → implement、CodeLayer の RPI、HumanLayer の QRSPI、夜間の GitHub Actions のループ
  6. 「Took the codex pill, 5.5 for all coding」。Fable が Codex のサブエージェントを管理する
- **2026-07-20**: worktree は「new worktrees off the latest remote main」を既定にしている（[status/2079016387876692098](https://x.com/dexhorthy/status/2079016387876692098)）。同じ日に、前の週に worktree を 10 個片付けたら node_modules の削除だけで 1 分以上かかったと書いている（[status/2079022799520411798](https://x.com/dexhorthy/status/2079022799520411798)）
- **2026-09-09**: 同僚が Codex に 4 時間かけて worktree と node_modules を削除させた、と書いている（[status/2097783909539021134](https://x.com/dexhorthy/status/2097783909539021134)）
- **2026-09-12**: macOS の `say` コマンドをよく使う（[status/2098828959161184723](https://x.com/dexhorthy/status/2098828959161184723)）
- **補足**: 2026-11 時点の X のプロフィールは「MTS @factory」。Factory に移ってからの環境は分からない

### 環境が分からなかった人

Justin Spahr-Summers・Barry Zhang・Erik Schluntz・Mahesh Murag・Keith Lazuka・Lance Martin・Jesse Vincent の 7 人は、今回の範囲では本人が環境を語った情報が見つからなかった。

- Jesse Vincent は X にほとんど投稿しておらず、発信はブログ（[blog.fsck.com](https://blog.fsck.com)）が中心である
- Anthropic の社員の多くは、環境について個人で発信していない

---

## 3. 共通して見えること

- **IDE から離れている**: Boris はアンインストールし、Geoffrey は VS Code をデバッグ用に限っている。Dex も JetBrains や Cursor からターミナルへ移った。Kieran は Cursor を使うが、音声入力でエージェントと話すループと、Cursor のホストされたエージェント・iOS アプリとして使っている
- **並列化と worktree**: Boris（数十のセッション）、Dex（tmux の worktree）、Simon（ディレクトリを分けて並列に）。たまった worktree の掃除は、Boris と Dex がともに課題として挙げている
- **ローカルの外へ**: Simon（Claude Code on the web、Codex Remote）、Kieran（Mac mini に ssh）、Boris（Web・iOS・Tag）。Matt Pocock の VM と Discord への移行（[matt-pocock-dev-environment.md](matt-pocock-dev-environment.md)）と同じ方向である
- **チャットツールの中のエージェント**: Boris と David はともに、Slack の Claude Tag での作業の比重が大きいと書いている
- **Claude 一本ではない**: Simon・Kieran・Geoffrey・Dex は Codex なども併用する。Dex は主力を Codex に移した

---

## 4. 確かめられなかったこと

- Boris Cherny のスレッドの続きは、Thread Reader のミラーで読んだ（先頭の投稿は原文で確認済み）
- Kieran Klaassen のガイドには日付が無い。共同メンテナーがいるため、一人称の発話者は署名欄からの推定である
- 誤りとして除いた主張がある。deep-research の反証チェックで否決された次の 2 件は、この文書に載せていない
  - Boris が「全タスクで Opus 4.5 と extended thinking を使う」
  - David が「MCP 最初のクライアントを Zed に実装した」
