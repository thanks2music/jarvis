# Claude Projects（coordinator が並列 thread を回す Projects）

> 出典:
> - [Let Claude coordinate ongoing work with Projects](https://code.claude.com/docs/en/claude-projects)（公式 docs。本 doc の主出典、2026-11-01時点）
> - [Projects redesigned: from folder to conversation](https://claude.com/resources/articles/projects-redesigned)（2026-09-17、発表記事）
> - [Run agents in parallel](https://code.claude.com/docs/en/agents)（並列実行の 5 つの手段の比較、2026-11-01時点）
> - [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows)（比較表の dynamic workflows、2026-11-01時点）
> - [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments)（cloud session がリポジトリから読むものと project thread の例外、2026-11-01時点）
> - [Automate work with scheduled tasks](https://code.claude.com/docs/en/routines)（cloud scheduled tasks。旧称 routines、2026-11-01時点）
> 最終更新: 2026-11-01

**Projects** は、関連するタスクを 1 本の会話に流し込むと、Claude が coordinator としてタスクごとに **thread** を起動して並列に進め、どれが終わり、どれが自分の返事を待っているかを一か所で見せる機能である。2026-09-17 に作り直され、Claude Code の Pro / Max / Ultra 向け public beta として提供されている（2026-10-30 に Max 20x が Ultra に改称された）。発表記事は、Claude がリクエストのスコープを決め、作業を委任し、並列の thread を調整し、出力をレビューして、完成した結果を組み立てると説明している。

thread は通常 1 つの Claude Code **cloud session** で、専用のブランチで作業し、必要なら PR を開く。手元のマシンにしか無いもの（ローカル DB・デバイスエミュレータ・VPN の奥の API など）が要るタスクだけは、[Remote Control](https://code.claude.com/docs/en/remote-control) 経由で自分のマシン上の thread として動かせる。cloud の thread はノート PC を閉じても動き続け、進捗の確認や指示はスマートフォンからもできる。手元のマシンの thread は、そのマシンが起きている間だけ動く。

> **名称について**: 公式ページの名称は「Projects」である。claude.ai の chat や Cowork にある従来の Projects（会話と参照ファイルをまとめるだけで、thread も coordinator も持たない）とは別物で、従来の Projects は新しい体験が届くまで今の動きのまま使える。本リポジトリの docs では区別のため「Claude Projects」と呼ぶ。

---

## 1. 前提知識: 並列実行の手段との比較

公式 [Run agents in parallel](https://code.claude.com/docs/en/agents) は、複数のタスクを同時に進める方法を **subagents / agent view / agent teams / dynamic workflows / projects** の 5 つに整理している。公式 [Projects](https://code.claude.com/docs/en/claude-projects#how-projects-relate-to-other-claude-code-features) によれば、並列に動くこと自体は Projects の目的ではない。違いは、**session を起こして追跡するのが自分ではなく Claude であり、どの session も同じ instructions から始まる**点にある。

| 手段 | どこで動くか | 並列の単位 | コンテキスト | 誰が調整するか | 向く用途 |
|---|---|---|---|---|---|
| Subagent | 1 つの session の中 | session 内で委任される worker | 各 subagent が自分の context window で副タスクをこなし、呼び出し元の session にサマリーを返す | 呼び出し元 session の Claude | 検索結果・ログ・ファイル内容で本会話を埋めてしまう副タスク |
| Agent teams | 1 つの session（lead）が teammate session を起こす。手元のマシンでも cloud session の中でも動く | teammate session | teammate はそれぞれ別 session。teammate 同士で直接メッセージを送り、Task tools があればタスクリストを共有する | lead の Claude が計画・割り当て・監督する | 1 つのタスクを分けて割り当て、worker 同士を同期させたいとき。team はそのタスクと共に終わる。実験的機能で既定は無効 |
| Dynamic workflows | 1 つの session の中で、Claude が書いた JavaScript スクリプトを runtime がバックグラウンドで実行する | スクリプトが起こす多数の subagent | 計画を持つのは Claude のターンごとの判断ではなくスクリプト。subagent の結果をスクリプトが突き合わせる | スクリプト | 数体の subagent では収まらない仕事や相互検証が要る仕事（コードベース全体の監査・500 ファイルの移行・相互検証した調査など） |
| Claude Projects | claude.ai/code・Desktop の Code タブ・Claude mobile アプリ。thread は cloud session で、頼めば Remote Control 経由で手元のマシンでも動く | thread（それぞれが丸ごと 1 つの session） | thread ごとに別の context window。coordinator は thread の報告を見るが、各ステップは見ない。project instructions は全 thread に届き、cloud thread は project memory も読む | project の会話にいる coordinator の Claude | 日〜週の単位で続き、タスクが増え続ける仕事。マシンを閉じても進めたく、session を 1 つずつ割り振って追うより一度説明して任せたいとき |

表の補足:

- **thread の中でさらに subagent を使える**（公式 docs）。発表記事は、thread が委任された仕事を subagents・loops・workflows でさらに分割できると書いている。
- **agent view**（`claude agents`）は手元の複数 session を 1 画面で追う画面で、各 session を起こしてタスクを渡すのは自分である。ターミナル・IDE・Desktop のローカル環境で自分が始めた session は、そのままでは project に追加できない（Remote Control で接続すれば **Continue in project** でその仕事を取り込める。5.2）。
- **Claude Tag** は Team / Enterprise 向けで、Slack チャンネルにいる誰もが仕事を渡し、全員が見て操る。project は自分 1 人のもので、自分の GitHub アクセスと connectors を使い、Pro / Max / Ultra 向けである（[claude-tag.md](claude-tag.md) 参照）。
- **scheduled task**（旧称 routine）: project の中で定期作業を頼むと、Claude が [cloud scheduled task](https://code.claude.com/docs/en/routines) を作り、その project の thread として動かす（**Scheduled tasks** タブに出る）。project の外で作った scheduled task はそのまま単独で動く。公式は 2026-11 時点で routines を「cloud scheduled tasks (formerly routines)」と改称しており、本 doc の旧記述の「routine」「**Routines** タブ」は同じものを指す。

---

## 2. 向く仕事・向かない仕事

公式は「1 session を超えて続く目標があり、タスクを生み続ける仕事」に project を勧めている。

| 状況 | 公式の推奨 |
|---|---|
| 多数のリポジトリにまたがる 1 つの目標（例: 全サービスを新しい lint 設定に揃える） | project。リポジトリごとに thread と PR ができ、**Overview** でレビュー待ちが分かる |
| 1 つの領域に仕事を流し込み続ける（1 サービスのバグ・スタックトレース・レビュー依頼） | project。一度の修正で覚えさせた落とし穴が project memory に残り、次の thread に効く |
| 1 session より大きいビルドや移行（`docs/spec.md` の実装、非推奨 ORM からの移行など） | project。仕事を thread に分け、早い段階で覚えさせた判断が後の cloud thread に届く |
| コード以外の仕事（契約書のフォルダやサポートチケットの export に繰り返し質問する） | project。リポジトリの代わりに文書をアップロードし、thread の成果物は **Library** タブにファイルとして届く |
| 1 session で収まる単発タスク（例: flaky な login テストを直す） | 自分で [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web) を始める |
| すべてのタスクが手元のマシンを要する（ローカル DB・デバイスエミュレータ・VPN の奥の API） | ローカル session か [agent view](https://code.claude.com/docs/en/agent-view)。ローカルのファイルだけが要るなら project にアップロードする |
| 会話を伴わない定期実行（例: 毎週月曜に依存関係レポートを投稿する） | [cloud scheduled task](https://code.claude.com/docs/en/routines)（旧称 routine）単体 |
| 複数人が Slack チャンネルで仕事を渡して一緒に操る | [Claude Tag](https://claude.com/docs/claude-tag/overview) |

一部のタスクだけが手元のマシンを要する場合は project のままでよく、そのタスクの thread だけを手元のマシンで動かす（[5.7](#57-自分のマシンで-thread-を動かす)）。

---

## 3. project の構成

| 要素 | 役割 |
|---|---|
| project の会話（coordinator） | 長く続く 1 つの session。送られたものから何を thread にするかを決め、起動した全 thread を追跡する。thread の報告は見るが、各ステップは見ない |
| thread（worker） | それぞれ別 session で、専用の context window を持つ。1 つの仕事をして、終わったら会話に報告する。cloud thread は自分のブランチで作業し、必要なら PR を開く |
| **Overview** ペイン | 全 thread の状態と、自分の対応が要るものを一覧する。ほかのタブは **Library**（追加したファイルと thread が作ったファイル）・**Pull requests**・**Scheduled tasks**（project から Claude が作った cloud scheduled tasks。旧称 **Routines**） |

発表記事によれば、各 thread は自分のブランチとリポジトリのコピーで動く。coordinator が作業を整理するが、複数の thread が同じコードに触れた場合の重なりは、ほかの PR と同じくマージコンフリクトとして解決する。

### 3.1 cloud thread が最初から持っているもの

- project のリポジトリとファイル、project instructions と project memory
- 各リポジトリの `CLAUDE.md`（リポジトリ直下の `CLAUDE.md`・`.claude/CLAUDE.md`・`.claude/rules/`）。リポジトリの skills・`.claude/settings.json`・`.mcp.json` は、リポジトリの数に関係なく読まない
- claude.ai アカウントの connectors
- cloud environment（ネットワークアクセス・環境変数・network secrets・インストール済みツールを決める）

**cloud thread は、手元のマシンの Claude Code 設定を何も引き継がない。** 手元にだけインストールした skills・MCP servers・plugins・ツールは、次の 3.3 の方法で届ける。

> **訂正（2026-11-01）**: 旧版の本節は「各リポジトリの `CLAUDE.md` と skills。リポジトリが 1 つの project では、そのリポジトリの permission rules と hooks も」読むとしていた。2026-11-01 の公式と食い違うため訂正した。

### 3.2 リポジトリから読むもの

cloud thread は project の全リポジトリを clone するが、リポジトリから読む設定は `CLAUDE.md` 系の instructions だけである。skills・agents・commands・`.mcp.json`・`.claude/settings.json`（plugins・permission rules・hooks・`env`）は、**リポジトリが 1 つでも複数でも読まない**（公式 [What threads pick up from your repositories](https://code.claude.com/docs/en/claude-projects#what-threads-pick-up-from-your-repositories)）。

| リポジトリ内のもの | cloud thread での扱い |
|---|---|
| リポジトリ直下の `CLAUDE.md`・`.claude/CLAUDE.md`・`.claude/rules/` | thread の開始時に全リポジトリから読む。サブディレクトリの `CLAUDE.md` と path-specific rules（`paths` 付きの rules）は読まない |
| `.claude/skills/` の skills | 読まない。claude.ai アカウントで skill を有効にする（3.3） |
| `.claude/` 配下の agents・commands | 読まない。使うなら thread を手元のマシンで動かす（5.7） |
| `.mcp.json` の MCP servers | 読まない。claude.ai アカウントの connectors を使う（3.3） |
| `.claude/settings.json` で有効にした plugins | 読まない。**Project settings > Plugins** に追加する |
| `.claude/settings.json` の permission rules | 適用しない。thread の中で承認するか、thread を手元のマシンで動かす |
| `.claude/settings.json` の hooks | 実行しない。使うなら thread を手元のマシンで動かす |
| `.claude/settings.json` の `env` | 適用しない。環境変数は cloud environment で渡す |

project の外で自分が始める通常の cloud session は、これと違ってリポジトリの skills・agents・commands を読み、リポジトリが 1 つなら `.mcp.json` と hooks・permission rules も読む（公式 [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup)）。同ページの注記は、project の cloud thread がそのうちリポジトリ直下の `CLAUDE.md`・`.claude/CLAUDE.md`・path-specific でない `.claude/rules/` だけを読むと明記している。

リポジトリをまたぐ常設のルールは project instructions に書き、環境変数は cloud environment で渡す。

> **訂正（2026-11-01）**: 旧版の本節は「全リポジトリから `CLAUDE.md` と skills を読み、リポジトリが 1 つなら permission rules・hooks・`env` も適用する（複数なら Anthropic-hosted environment では適用しない）」とし、表もリポジトリ数で列を分けていた。2026-11-01 の公式と食い違うため訂正した。旧記述は、通常の cloud session の挙動と取り違えていた可能性がある。

### 3.3 skills・plugins・MCP・ツールを cloud thread に届ける

| 種類 | 届け方 |
|---|---|
| Skills | claude.ai アカウントで有効にする。cloud thread はそこで有効にした skills を読む（self-hosted environment の一部の thread を除く）。リポジトリの `.claude/skills/` に commit した skill は cloud thread では読まれない（2026-11-01 訂正。旧版は「リポジトリに commit する」としていた） |
| Subagents・commands | cloud thread には届ける手段がない。使うなら thread を手元のマシンで動かす（5.7） |
| Plugins | **Project settings > Plugins** に追加すると、新しい cloud thread ごとに読み込まれる。リポジトリの `.claude/settings.json` で宣言した plugin は cloud thread では読まれない |
| MCP servers | claude.ai アカウントの connectors（[claude.ai/customize/connectors](https://claude.ai/customize/connectors) で一度接続する）が、project ごとの設定なしに全 cloud thread に届く。リポジトリの `.mcp.json` は、リポジトリの数に関係なく読まない（2026-11-01 訂正。旧版は「リポジトリが 1 つなら `.mcp.json` も読む」としていた）。**project の会話そのものは connectors を持たない**ので、connector が要る仕事は cloud thread のタスクとして出す |
| CLI ツール・パッケージ | cloud environment の setup script でインストールする |

Remote Control 経由で手元のマシンに立てた thread は、そのマシンにインストールされたものを使う。

---

## 4. 既定値と上限

| 項目 | 既定・上限 | 変更場所・補足 |
|---|---|---|
| Thread model / Thread effort | Opus / `high` | **Project settings > General**。1 タスクだけ変えるならタスクの中で頼み、実行中の thread はその thread の model picker で変える |
| Coordinator model / Coordinator effort | Opus / `low` | **Project settings > General** |
| thread の permission mode | thread のモデルが対応していれば auto mode | 承認プロンプトは thread の中に出て、その thread で答えるまで待つ。project の会話で「進めて」と言っても届かない |
| 新しい thread の数 | 全 project を合わせて 1 日 500 本（強制される上限。2026-10-11 時点の公式は 200 本） | 同時に動く thread の数に固定の上限はない。会話で頼む上限（「同時に 2 本まで」など）は好みであって強制ではない |
| Project instructions | 最大 16,000 文字。新しい thread と coordinator の両方に送られる | **Project settings > Memory > Project instructions**、または Claude に変更を頼む |
| Project memory | Claude が書くファイル群。cloud thread は開始時に索引の `MEMORY.md` を読み、ほかのファイルは必要なときに開く | **Project settings > Memory** に **Auto memory** として並ぶ。手元のマシンの auto memory やリポジトリの `CLAUDE.md` とは別物 |
| **Library** タブからのファイル追加 | 1 回の選択で 100 ファイル・2 GB まで、1 ファイル 480 MB まで | **Overview** の **Library** タブの **Add** |
| **New project** ダイアログからのファイル追加 | 30 MB を超えるファイルはスキップされる | 大きいファイルは作成後に **Library** タブから追加する |
| フォルダの追加 | 先頭 100 ファイル・200 MB までのコピー（30 MB 超のファイル・隠しファイル・`node_modules` は除く）。フォルダと Google Drive フォルダは合わせて 1 project に 10 個まで（単体ファイルは数えない） | アップロードはコピーなので、手元での変更は再アップロードして **Replace** を選ぶまで届かない |
| cloud environment | Anthropic-hosted の既定 environment（主要なパッケージレジストリには到達できる） | **Project settings > Environment** |
| 手元のマシンで thread を動かす要件 | そのマシンに Claude Code v2.1.280 以上（公式 docs の記載） | 古いと「Claude is out of date on your device」になる |

### 4.1 Project settings の項目

project の設定は `settings.json` ではなく、claude.ai/code か Desktop の **Project settings** で変える。**instructions・repositories・plugins・environment の変更は新しい thread にだけ届き、実行中の thread には届かない。**

| 設定 | セクション | 内容 |
|---|---|---|
| Name, icon, and goal | General | サイドバーの名前とアイコン、1 行の goal |
| Coordinator model and effort | General | project の会話にいる Claude のモデルと effort |
| Thread model and effort | General | thread のモデルと effort |
| Project instructions | Memory | 新しい thread が必ず受け取る常設ルール |
| Project repositories | Environment | 新しい cloud thread が clone するリポジトリ |
| Cloud environment | Environment | 新しい cloud thread が動く cloud environment |
| Connectors | Environment | cloud thread に届く claude.ai connectors の管理画面へのリンク |
| Plugins | Plugins | 新しい cloud thread ごとに読み込まれる plugins |
| Usage | Usage | thread 別・モデル別のトークン使用量 |
| Memory | Memory | project memory のファイル |
| Restart Claude | General | project の会話で Claude が応答しなくなったときに再起動する |
| Pause, Archive, Delete | General | project を止める・隠す・削除する（4.2） |

### 4.2 Pause / Archive / Delete

| 操作 | 効果 |
|---|---|
| **Pause** | 全部を一度に止める。実行中の thread と会話が中断され、新しい thread は始まらず、scheduled task（旧称 routine）も動かず、再開するまでメッセージを受け付けない。**Resume** で戻し、止まった thread はその後にメッセージを送ると続く |
| **Archive** | サイドバーから隠し、thread をアーカイブする（実行中や PR を監視中の thread も止まる）。アーカイブ中は scheduled task も動かない。Projects ページから **Unarchive** で戻せるが、thread は session 一覧から個別に戻す |
| **Delete** | project を thread・memory・ファイルごと完全に削除し、scheduled task を止める。元に戻せない。thread が GitHub に push したブランチや PR は消えない |

---

## 5. 使い方

### 5.1 前提条件

- **プラン**: Pro / Max / Ultra で、サイドバーに **Projects** が表示されていること（直下に無ければ **More** の下も確かめる）。**Projects** を選び、**New project** か **Get started** が出ることを確かめる。
- **GitHub（コードを扱う場合）**: コードが github.com にあること（GitHub Enterprise Server・GitLab・Bitbucket は不可）。接続した GitHub アカウントに push 権限があり、リポジトリに Claude GitHub App がインストールされていること。`/web-setup` で接続したトークンは他の cloud session には足りるが、project の cloud thread には Claude GitHub App が要る。
  - organization 所有のリポジトリは organization owner しか App のインストールを完了できない。owner でなければ owner にインストール依頼が送られ、承認されるまでその project では使えない。
  - SAML SSO を強制する organization は、GitHub を再接続してその organization に Claude app を認可するまで、private リポジトリが **New project** ダイアログや **Project settings > Environment** に出ない。
- **ネットワーク・secret・ツール**: cloud thread では project の cloud environment が決める。既定の environment で足りない domain・secret・ツールがあれば environment を変える。MCP server が要るなら claude.ai connectors で接続済みか確かめる。

### 5.2 project を作る

作成・利用できるのは claude.ai/code・Desktop の Code タブ・Claude mobile アプリ（iOS / Android）である。ブラウザと Desktop では次の 2 通りで作れる。

| 始め方 | 手順と挙動 |
|---|---|
| 新規に作る | サイドバーの **Projects** → **New project**（ブラウザなら claude.ai/code/projects/browse でもよい）。**Name** だけが必須で、**Goal**（1 行の目標）と **Context**（GitHub リポジトリ・ファイル・フォルダ・Google Drive フォルダ）は任意。goal を設定すると会話の Claude はそれに向けて動く |
| 既存の cloud session から | session のサイドバーメニューで **Continue in project** を選び、サブメニューから選ぶ。**Continue as new project** は session から新しい project を作り、Claude が session を読んで **Setup recommendations** を出す。既存の project を選ぶと、その project に session の仕事を取り込み、Claude が session を読んで続きを始める。どちらも元の session は一覧に残る（**Continue as new project** では、ターンの途中なら元の session も動き続ける）。cloud session のメッセージ欄の上に出る **Set up project** バナーを使っても結果は同じだが、その場合は project が開いた時点で session の実行中のターンが止まる |

> **旧記述**: 2026-10-11 時点の公式では、メニューは **Continue as project**（新しい project を作る）と **Move to project**（既存の project に取り込む）の 2 つだった。2026-11-01 の公式では **Continue in project** のサブメニューに統合されている。

手元のマシンの session も、[Remote Control](https://code.claude.com/docs/en/remote-control) で接続すれば claude.ai/code のサイドバーに同じメニューが出る。ただしアカウントで **Require trusted devices** が on の間に接続した session は、project から transcript を読めない。off の場合の手順は次のとおり。

1. まだ接続していなければ、その session で `/remote-control` を実行する。setting が on の間に接続していたなら、一度切断して接続し直す。
2. ブラウザで claude.ai/code のサイドバーからその session の行のメニューを開き、同じサブメニューから選ぶ。

**Require trusted devices** が on か、Remote Control を使わない場合は、project の会話で仕事を説明するか、ブランチを push してリポジトリを project に追加し、タスクでブランチ名を指定する（2026-10-11 時点の公式は「ローカル session にはこの選択肢が無い」としていた）。

最初の project では、先にメッセージを送らない限り、作成直後に Claude が自分からターンを 1 回使う。**このターンも plan を消費する。** そのターンで Claude は、読み取り専用でリポジトリを調べて次の手を提案する thread を 1 本起動したり、最近の cloud session をもとに **Setup recommendations**（追加すべきリポジトリ・作るべき scheduled task・起動できる thread）を出したりする。推奨されたリポジトリと scheduled task は全部 on の状態で出るので、不要なものを off にしてから **Update setup** を押す。

### 5.3 最初のバッチを送る前に

公式は、仕事をまとめて送る前に次の 4 段階を勧めている。

1. **project instructions を書く**: どのブランチを target にするか、thread がどう自己検証するか、何に自分の許可が要るか。
2. **実際の仕事の小さな 1 つを送る**: 終わった thread を開き、報告の仕方とブランチ上の変更を確かめる。
3. **Thread model / Thread effort を確認する**: 新しい project は全 thread を Opus・effort `high` で動かし、plan を最も早く消費する。
4. **起動前の提案と同時実行数の制限を頼む**: 「thread を起動する前に提案して」「同時に数本まで」と頼み、思いどおりに返ってくるようになったら外す。

project instructions の公式の例（p95 レイテンシを 200 ms 未満に保つ project）は、次の要素を含む。

- main からブランチを切り、thread ごとに draft PR を 1 本開く
- 完了と言う前に `make test` と `make lint` を走らせ、要約行を最後のメッセージに貼る
- 必要なもの（リポジトリ・secret・API・connector）に届かなければ、何が足りないかを最初のメッセージで正確に書いて止まる。代用・モック・推測をしない
- マージ・force-push・CI 設定の変更は、thread で聞いてからにする

### 5.4 仕事を送る・結果を読む

- 簡単な質問は会話の中で答えが返る。新しい仕事は新しい thread か、その領域を担当中の thread に回され、どちらに回したかを Claude が告げる。1 つのメッセージに無関係な複数のタスクを書くと、別々の thread になる。
- thread の結果はその thread に残り、会話のカードを開いて読む。thread が作ったファイルは **Library** タブにも入る。
- Claude が thread を起動せずに **Suggested threads** として提案することもある。

coordinator の振る舞いは会話で指示して調整する。公式の例は「起動前に提案して許可を待って」「確認せずに今すぐ始めて」「同時に 2 本まで」「同じ領域のフォローアップは既存の thread を使って」「終わったときか詰まったときだけ投稿して」「計画を見るまで PR を開かないで」「何が問題かだけ教えて、まだ直さないで」「thread を起こさずここで答えて」などである。**Claude はこうした好みを自分で project memory に保存して後の cloud thread でも守るが、強制される設定ではない。** 文言どおりに全 thread へ最初から適用したいなら project instructions に書く。

### 5.5 thread の PR

cloud thread がコードを変えるときの既定の挙動は次のとおり。

| 項目 | 既定の挙動 |
|---|---|
| ブランチ | リポジトリの既定ブランチから新しいブランチを切る |
| PR | 頼めば開く。バグ修正など具体的な変更なら自分から開くこともある |
| PR を開いた後 | ほかの cloud session の設定に関係なく [auto-fix](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests) を on にして PR を監視する。CI が落ちれば修正を push し、レビューコメントに対応し、チェックが通ってレビュー待ちになったら thread で知らせる |

会話のカードには次の手のボタンが出ることがある。**Resolve conflicts**・**Fix CI**・**Address comments**・**Merge it** は、その指示を自分からのメッセージとして thread に送る。**Review PR** は GitHub で PR を開く。**Create PR** は、ブランチを push したが PR を開いていない idle の thread に出て、thread に指示を送らずそのブランチから直接 PR を作る。PR を開くタイミングや起点のブランチを変えたいときは、タスクか project instructions に書く。

### 5.6 Overview で自分の対応が要るものを見る

**Overview** の **Threads** タブは thread を状態別にまとめる。

| グループ | 中身 |
|---|---|
| **Ready for review** | PR が開いてレビュー待ちの thread |
| **Waiting on you** | 自分の返事や承認を待つ thread、または失敗した thread |
| **Working** | 実行中の thread |
| **Landing** | PR が承認済み、またはマージキューに入った thread |
| **Idle** | 終わって何も待っていない thread |
| **Resolved** | 完了とした thread。自分が thread のメニューから付けるか、PR のマージなど最後の手順を自分が済ませた後に Claude が付けるか、1 週間動きが無いと自動で付く。同じメニューから再開できる |

Desktop では、Claude が会話に投稿したとき・thread がエラーになったとき・thread が入力を求めたときにデスクトップ通知が届く（project のサイドバーメニューの **Notifications** で、thread のターン終了ごとの通知を足したり止めたりできる）。通知は Desktop 専用で、ブラウザでは **Overview** ボタンのドットで確かめる。

thread を開けば、手順ごとの記録を読む・thread 自身のメッセージ欄で直接指示する・待っている承認プロンプトに答える・**Stop** か Esc で中断する、ができる。project の会話でのフォローアップは、Claude がその thread に結び付けたときにしか届かない。

### 5.7 自分のマシンで thread を動かす

ローカル DB・デバイスエミュレータ・VPN の奥の API など、手元のマシンにしか無いものが要るタスクは、そのタスクの thread だけを [Remote Control](https://code.claude.com/docs/en/remote-control) 経由で手元のフォルダで動かせる。ほかの thread は cloud で動き続ける。

| 項目 | cloud thread | 手元のマシンの thread |
|---|---|---|
| 使う設定 | project の cloud environment | そのマシンのファイル・ツール・MCP servers・Claude Code 設定（hooks と permission rules を含む） |
| 開始時に受け取るもの | project instructions と project memory | project instructions のみ（memory ファイルは読み込まれない） |
| 動く条件 | 手元のマシンを閉じても動く | そのマシンが起きていて Remote Control が on の間だけ |

手順:

1. **フォルダを接続する**（どちらもそのマシンに Claude Code v2.1.280 以上が要る）
   - Desktop: **Settings > Code** か **Settings > Claude Code** で **Use this computer from your phone and claude.ai** を on にし、その下の一覧にフォルダを追加する。アプリが開いている間、このマシンで thread を動かせる。
   - ターミナル: そのフォルダで `claude remote-control` を実行したままにする。git リポジトリなら `--spawn worktree` を付けると、thread ごとに専用の worktree になる。
2. **Work locally を選んで頼む**: project の会話でメッセージ欄横の **+** メニューから **Work locally** を選び（メッセージに **Local** タグが付く）、やってほしいことを書く。手元のマシンで動かすようメッセージに書いてもよい。
3. **カードで許可する**: **Allow Claude to work in a folder on your device** カードでフォルダを選び、**Allow once** を押す。2 つの thread が同時に同じフォルダで動くと互いの変更を上書きしうるので、git リポジトリならフォルダのオプションで **Worktree** を on にして専用の worktree を使わせられる。

手元のマシンの thread も auto mode で動く。そのマシンの Claude Code で auto mode が使えないか off なら auto mode なしで動き、出た承認プロンプトは thread の中で答えるまで待つ。マシンがスリープすると thread は止まり、Desktop か `claude remote-control` が終了すると停止する。Desktop の **Settings > Code** か **Settings > Claude Code** で **Keep this computer awake for Remote Control** を on にすると、スリープを防げる。アカウントで **Require trusted devices** が on の間は、手元のマシンで thread を動かせない。

---

## 6. 利用枠とコスト（注意点）

project は**ほかの Claude Code session と同じ plan の利用枠を使い、より速く消費する**。とくに Pro プランでは、project を動かす日は上限に早く届くと公式は明記している。project が自力で枠を超えて使うことはなく、超えるのは自分のアカウントで usage credits を on にしている場合だけである（thread が usage credits を on にすることはできない）。

| 枠を消費するもの | 内容 |
|---|---|
| 実行中の thread | 各 thread が丸ごと 1 つの session で、複数が同時に動く。数は Claude が仕事に応じて決め、強制される上限は全 project 合わせて 1 日 500 本の新規 thread（2026-10-11 時点の公式は 200 本） |
| project の会話 | coordinator 自身も、thread の報告を読んで次の手を決めるのにトークンを使う |
| PR を監視中の thread | idle の thread も、CI の失敗やレビューコメントで起きて再び枠を使う。止めるには、その thread で PR の監視をやめるよう頼む |

実行中の thread・監視中の PR・新しいメッセージが無い project と、アーカイブした project は、置いておくだけでは枠を使わない。

**上限に届いたとき**: thread や project の会話が 5 時間枠か週の枠に届くと、自動でリトライを続け、枠がリセットされると続きを始める（thread には **Service is busy** と「Claude is still retrying and will continue automatically.」が出る）。つまり**放置した仕事は、メッセージを送らなくても次の利用枠を使い始める**。次の枠を使わせたくなければ thread の **Stop** か、project の **Pause** で止める。scheduled task（旧称 routine）が起動した thread だけは待たず、上限エラーでターンが止まり、枠のリセット後に自分でメッセージを送る。

**使用量を減らす方法**（公式）:

- **Project settings > Usage** で thread 別・モデル別の使用量と、project の会話に使った量を確かめる。
- cache の有効期間（Pro / Max / Ultra の plan 枠内では 1 時間）より長く idle だった thread にフォローアップを回すと、その thread の会話全体を読み直してから動く。新しい仕事は、大きな古い thread を起こすより新しい thread を始めてもらう方が安く済むことがある。
- 最大のモデルが要らない仕事なら、thread・会話・その両方で小さいモデルか低い effort を選ぶ。
- 同時に動かす thread を減らすよう、また小さな質問は thread を起こさず会話で答えるよう、会話で頼む。

---

## 7. 制限事項

| 項目 | 内容 |
|---|---|
| 提供範囲 | Pro / Max / Ultra の public beta で段階展開中。まず cloud session を使ったことがあり、claude.ai chat や Cowork に既存の project を持たないアカウントから届く。Team / Enterprise では未提供。サイドバーに **Projects** が出なければまず **More** の下を確かめ、そこにも無ければ展開が未到達なので waitlist に登録できる |
| 使える場所 | claude.ai/code・Desktop の Code タブ・Claude mobile アプリ |
| 使えない場所 | terminal CLI・VS Code 拡張・JetBrains plugin。Amazon Bedrock・Google Cloud's Agent Platform・Microsoft Foundry 経由でも使えない |
| モデルプロバイダ | cloud thread も手元のマシンの thread も、モデルプロバイダは Anthropic |
| ローカル session | 自分が手元で始めた session は、そのままでは project に追加できない（Remote Control で接続すれば、その仕事を **Continue in project** で取り込める。5.2）。project が手元のマシンに届くのは、Remote Control で thread を動かす場合だけ |
| sandbox の中断 | cloud thread の sandbox はターンの合間に一時停止し、続きで再開する。再開できなければ新しい clone から続けるので、commit していない変更は失われうる。長いタスクでは途中経過を commit・push するよう頼む |
| 共有 | project は 1 人のユーザーのもの。project や thread をほかのユーザーと共有できず、thread の transcript にはほかの cloud session にある共有の選択肢も無い。beta 期間中は organization 単位の管理機能も無い |
| thread の移動 | thread は起動した project に属し、別の project への移動・コピーや単独 session への切り出しはできない。**Continue in project**（旧 **Move to project**）は cloud session の仕事を project に取り込む一方向だけ。2 つの project の統合もできない |

**発表記事（2026-09-17）と現行 docs の差**: 発表記事の時点では「thread は今は cloud で動き、手元のマシンで動かす機能は近日提供」とされていた。現行 docs（2026-11-01 確認）では、Remote Control 経由で手元のマシンに thread を立てられる（Claude Code v2.1.280 以上）。発表記事は、全 Claude での新しい projects と Team / Enterprise への提供はその後になるとしており、現行 docs でも Team / Enterprise は未提供のままである。

---

## 8. Tips

- **リポジトリ固有のルールは `CLAUDE.md`、project 全体のことは project instructions と project memory に分ける**（公式の指針）。ビルドコマンドのような 1 リポジトリのルールは、cloud thread が clone から読む `CLAUDE.md` に置く。
- **cloud thread がリポジトリから読むのは `CLAUDE.md` 系だけ**: cloud thread はリポジトリ直下の `CLAUDE.md`・`.claude/CLAUDE.md`・`.claude/rules/` を clone から読むが、リポジトリの skills・`.mcp.json`・`.claude/settings.json` は読まず、手元のマシンの Claude Code 設定も引き継がない。skills は claude.ai アカウントで有効にし、plugins は **Project settings > Plugins**、MCP servers は claude.ai connectors で届ける（3.3）。旧版の「cloud thread に届くのは commit されたものだけ（`CLAUDE.md`・skills を clone から読む）」は、2026-11-01 の公式と食い違うため訂正した。
- **thread を訂正したら、その訂正を覚えるよう Claude に頼む**。project memory に入り、後の cloud thread がそこから始まる。
- **リポジトリは「ほぼ全タスクが触るもの」だけ追加する**。多数のリポジトリにまたがる project では 1〜2 本だけ追加し、ほかは project instructions で名前を挙げておく。必要になった thread は自分にだけリポジトリを足せる（ただし途中で clone するので、その `CLAUDE.md` は開始時には無い）。project が既に使っている GitHub owner 以外のリポジトリは、Claude からは足せず、自分で **Project settings > Environment** に追加する。
- **複数の thread が誤った前提で戻ってきたら、個々のタスクではなく project の設定の穴を疑う**。公式の手順は、(1) 会話で「開いている全 thread について、頼んだこと・前提にしたこと・届かなかったもの・待っているものを挙げて」と頼む、(2) 誤った前提から始まった thread は resolved にするか指示し直す、(3) project instructions か environment の穴を一度だけ直し、1 本だけ送って確かめてから残りを新しい thread として送り直す、である。
- **project の cloud thread ではリポジトリの permission rules・hooks に頼らない**。リポジトリの数に関係なく、`.claude/settings.json` の permission rules も hooks も cloud thread には効かず、auto mode と thread 内での承認だけが頼りになる。hooks や permission rules が要るタスクは、thread を手元のマシンで動かす（5.7）。旧版は「複数リポジトリの project で」に限っていたが、2026-11-01 の公式と食い違うため訂正した。

---

## 9. トラブルシューティング

| 症状・メッセージ | 対処（公式） |
|---|---|
| thread が動いていないように見える | Claude は thread の各ステップを会話に投稿しないので、たいていはまだ動いている。新しい cloud thread は Claude が始める前に cloud environment を用意するので、最初の更新まで少しかかる。thread を開いて transcript を読み、承認プロンプトを待っていればそこで答える |
| 「Claude hasn't responded」バナー | バナーの **Restart Claude** か、**Project settings > General** の **Restart**。書きかけの返答は失われるが、thread には影響しない |
| リポジトリへのアクセスエラー（「Couldn't start the session」「Unable to access your repository」「Claude can't access」） | project の cloud thread は、ほかの cloud session が同じリポジトリを clone できていても、Claude GitHub App などの前提条件を要する。メッセージのボタン（**Install GitHub App** など）を押してから **Check again** |
| **Service is busy**（利用枠の上限） | 自動でリトライし、枠のリセット後に続く。止めたければ **Stop** か **Pause**（6 章） |
| 「Lost contact with your folder」 | 手元のマシンがスリープしたか、Desktop か `claude remote-control` が終了した。マシンを起こし、Desktop の **Use this computer from your phone and claude.ai** が on のままか確かめるか、同じフォルダで `claude remote-control` を再実行する |
| 「Claude is out of date on your device」 | thread を動かすマシンの Claude Code が v2.1.280 より古い。Claude Code（フォルダを Desktop で接続しているなら Desktop）を更新してから頼み直す |
| 「Claude ran out of context on this turn」 | thread の context window が埋まった。新しい session で続くと書かれていれば自動で続き、そうでなければ残りの仕事を新しい thread で始めるよう会話で頼む |
| 「Reached the turn limit」 | [`CLAUDE_CODE_MAX_TURNS`](https://code.claude.com/docs/en/env-vars) の上限に達した。メッセージを送って続けるか、その変数を上げるか外す |
| 「Additional usage credits are required」 | plan が usage credits でしか賄わないリクエスト（plan に含まれないモデルや context サイズ）を出したが、アカウントで usage credits が on になっていない。usage credits を使えるようにしてから、メッセージを送り直す |
| 「Unable to connect to repository」と「Claude couldn't reach GitHub to fetch your repository」 | 少し待ってからメッセージを送り直す |
| 「Unable to connect to repository」と「Claude couldn't access your repository or environment」 | GitHub アカウントにリポジトリへの push 権限が要り、environment も存在している必要がある。**Project settings > Environment** で両方を確かめてから送り直す |
| 「Couldn't show the setup proposal」 | 開いているアプリが、Claude の送った **Setup recommendations** より古い。ページを再読み込みするか Desktop を再起動するか、setup の提案をやり直すよう Claude に頼む |
| 「The project's environment was removed」 | **Project settings > Environment** で別の environment を選ぶ。変更は新しい thread に効く |
| 「Setup script failed」 | エラーの **Edit setup script** を押して environment の setup script を直し、メッセージを送り直す |
| 「Couldn't start in」+ フォルダ名 | 手元のマシンでの thread の実行を許可したが、session がそこで始まらなかった。メッセージの下に理由があればそれを直し、タスクの実行を Claude に頼み直す |

ほかのメッセージは公式の [Troubleshooting](https://code.claude.com/docs/en/claude-projects#troubleshooting) を参照。

---

## 関連ドキュメント

- [ClaudeCode SubAgents ガイド](sub-agents.md) — 「並列実行の選択肢と Claude Projects」で subagent と thread の違いを扱う
- [ハーネス設計ガイド](harness.md) — §4.16「Claude Projects: coordinator が並列 thread を回す」。固定ハーネス（§4.2 / §4.3）や dynamic workflows（§4.7）との関係
- [Claude Desktop の設定ファイル](claude-desktop.md) — 「Claude Projects（Code タブから使う並列 thread）」と、手元のフォルダを接続する Desktop の設定
- [ClaudeCode セッション履歴と `--resume`](session-history.md) — Remote Control の節（`claude remote-control` の挙動と再開）
- [Claude Tag](claude-tag.md) — Slack 上で組織が共有する `@Claude`。project との違い
- [Let Claude coordinate ongoing work with Projects](https://code.claude.com/docs/en/claude-projects) — 公式 docs
- [Projects redesigned: from folder to conversation](https://claude.com/resources/articles/projects-redesigned) — 発表記事（2026-09-17）
- [Run agents in parallel](https://code.claude.com/docs/en/agents) — subagents / agent view / agent teams / dynamic workflows / projects の比較
- [Use Claude Code in the cloud](https://code.claude.com/docs/en/claude-code-on-the-web) / [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments) / [Remote Control](https://code.claude.com/docs/en/remote-control) / [Automate work with scheduled tasks](https://code.claude.com/docs/en/routines)（旧称 Routines） — thread の土台になる機能
