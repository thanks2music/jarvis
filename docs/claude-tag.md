# Claude Tag（Slack 上で動く組織共有の `@Claude`）

> 出典: [Introducing Claude Tag](https://www.anthropic.com/news/introducing-claude-tag) / [Work with Claude Tag](https://claude.com/docs/claude-tag/overview) / [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) / [Claude Tag for Claude Code users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users) / [Configure GitHub access](https://claude.com/docs/claude-tag/admins/configure-github) / [Customize Claude Tag](https://claude.com/docs/claude-tag/admins/customize) / [Per-service connection guides](https://claude.com/docs/claude-tag/admins/connections/overview) / [Set up a skills repository](https://claude.com/docs/claude-tag/admins/skills-repo) / [Troubleshoot Claude Tag setup](https://claude.com/docs/claude-tag/admins/troubleshooting) / [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) / [Claude Code in Slack](https://code.claude.com/docs/en/slack) / [Cloud environments](https://code.claude.com/docs/en/cloud-environments) / [Data lifecycle](https://claude.com/docs/claude-tag/concepts/data-lifecycle) / [Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data) / [When Claude responds](https://claude.com/docs/claude-tag/users/when-claude-responds) / [Set a spend limit](https://claude.com/docs/claude-tag/admins/set-spend-limit) / [Setup overview](https://claude.com/docs/claude-tag/admins/setup-overview) / [Restrict where Claude Tag operates](https://claude.com/docs/claude-tag/admins/restrict-access) / [How agent identity works](https://claude.com/docs/claude-tag/concepts/agent-identity) / [Personal connectors in channels](https://claude.com/docs/claude-tag/concepts/personal-connectors) / [Use Claude Tag in a group DM](https://claude.com/docs/claude-tag/users/group-dms) / [Manage a channel's instructions from another channel](https://claude.com/docs/claude-tag/admins/managed-by) / [Set up Claude Tag for on-call](https://claude.com/docs/claude-tag/admins/setup-oncall) / [Federated agent access](https://claude.com/docs/claude-tag/admins/federated-access/overview) / [Use Claude Tag at a healthcare organization](https://claude.com/docs/claude-tag/admins/healthcare) / [Attribute costs to users](https://claude.com/docs/claude-tag/admins/attribute-costs) / [Manage workspaces and versions](https://claude.com/docs/claude-tag/admins/workspaces) / [Give Claude access to your tools](https://claude.com/docs/claude-tag/admins/add-connections) / [What Claude Tag remembers](https://claude.com/docs/claude-tag/users/memory) / [Commands Claude Tag understands](https://claude.com/docs/claude-tag/users/commands) / [Federated agent access limits](https://claude.com/docs/claude-tag/admins/federated-access/limits) / [Connect Amplitude](https://claude.com/docs/claude-tag/admins/connections/amplitude) / [Claude Tag now supports personal connectors in channels](https://claude.com/resources/articles/claude-tag-now-supports-personal-connectors-in-channels) / [How healthcare organizations use Claude Tag](https://claude.com/resources/articles/how-healthcare-organizations-use-claude-tag) (2026-10-11 確認)

**Claude Tag** は、Slack のチャンネル内で `@Claude` を **組織の共有 ID** として動かす製品である。2026-06-23 に発表され、2026-10-11 時点でも public beta（公式 docs の各ページに "Claude Tag is in public beta" の表記がある）。

本 doc が ClaudeCode ドキュメント群に含まれる理由は、Claude Tag が **Claude Code と同じエンジンで動き、リポジトリにコミットした ClaudeCode 設定の一部（`CLAUDE.md`・`.claude/rules/`・`.claude/skills/`）を読み込む**ためである。`CLAUDE.md` や `.claude/skills/` の書き方が、そのまま Slack 上の挙動を決める。一方で `.mcp.json` は読まれず、`.claude/settings.json` の hooks は動かず、effort は設定できず、権限は auto mode 固定という**運用差**がある。この「効くもの / 効かないもの」の境界を把握することが、本 doc の主目的である。

> **本 doc のスコープ**: ClaudeCode ユーザーの視点（設定の継承・セッションモデル・権限・課金）を主軸に置く。管理者向けの接続先ごとのセットアップ手順（Jira・Datadog・Snowflake・Amplitude など 17 サービス分。前回確認の 2026-09-03 以降に Amplitude が加わった）と、Federated agent access の接続先ごとの手順（AWS / Google Cloud / gateway / 認可サーバー）は、公式の [Per-service connection guides](https://claude.com/docs/claude-tag/admins/connections/overview) と [Federated agent access](https://claude.com/docs/claude-tag/admins/federated-access/overview) に譲る。

---

## 1. Claude Tag とは

チャンネルにいる誰もが `@Claude` に仕事を渡せる。**加えて Claude は、自分が参加するチャンネルの top-level メッセージとスレッド内の返信を @-mention の有無にかかわらず全て読み、返信すべきと判断したものには @-mention なしで返信する**（チャンネル単位の **Respond automatically** 設定。**既定は ON**）。ただし公式は、タグの無いメッセージへの反応は**「何もしない」が通常**で、具体的な依頼が書かれたメッセージにだけ一度スレッドで申し出ることがある、と説明している。また Claude は、最後に自分が投稿してから top-level メッセージが**約 100 件**たまるか、**10 日超** @-mention も自分の投稿も無いと、そのチャンネルを読むのをやめる（`@Claude` のメンションで再開。数値は既定値で変わりうる）。バグの再現から PR 作成、議論スレッドのドキュメント化、プロジェクト状況の集約などを、スレッド内にチェックリストを出しながら進め、やり取り全体がチャンネルに残る。

### 1.1 提供プランと前提

| 項目 | 内容 |
|---|---|
| 提供プラン | **Team / Enterprise のみ**。Free / Pro / Max では利用できない |
| デプロイ形態 | Anthropic のファーストパーティサービスのみ。**Bedrock / Vertex / Microsoft Foundry などサードパーティデプロイは対象外** |
| 使えない組織 | **Zero Data Retention（ZDR）・customer-managed encryption（CMEK）・Claude Code / Cowork（local mode）の HIPAA 構成**のいずれかを持つ組織。Claude Tag は channel memory と transcript を保持するため |
| 組織側の前提 | **Routines** が組織で有効（Admin settings > Capabilities > Remote sessions > Routines）。無効のままだと、全メンションと DM に「使えない」と返すだけで作業しない |
| セットアップ | 組織の Slack workspace と Claude organization を[ペアリングする](https://claude.com/docs/claude-tag/admins/setup-overview#pair-your-slack-workspace)。実行には Claude 組織の **Owner** 権限が必要。`@Claude connect` の実行（とアプリのインストール）には **Slack workspace admin** が要り、pairing code は発行から **15 分**で失効する。[動作確認手順](https://claude.com/docs/claude-tag/admins/setup-overview#verify-your-setup)も同ページ |
| ユーザー側の準備 | **既定では不要**。接続済み workspace の誰でも、Claude アカウントが無くても使える。Owner は利用者を絞れる（Team は **Restrict to your organization**＝組織の Claude アカウント保持者のみ、Enterprise は **Restrict to roles with Claude Tag access**＝ロールで許可した人のみ）。この制限はチャンネルと DM の両方に効く |
| 医療機関 | Claude Tag は Anthropic の **BAA（Business Associate Agreement）の対象外**。PHI を扱わない作業に限り、承認チャンネルへの限定・DM の無効化・PHI を持たないツールだけの接続で使う（[Use Claude Tag at a healthcare organization](https://claude.com/docs/claude-tag/admins/healthcare)） |
| 設定場所 | [`claude.ai/admin-settings/claude-tag`](https://claude.ai/admin-settings/claude-tag) |

セットアップ画面は **Pair your Slack workspace → Connect GitHub → Buy usage credits → Launch Claude Tag** の順に進む。Connect GitHub は組織が Claude GitHub App を未導入のときだけ現れ（スキップ可）、Buy usage credits は米ドルのカード払いでクレジットが無い組織にだけ現れる。Launch で Claude を入れるチャンネルを選び、Claude Tag を on にする。

Claude Tag は外部システムへのアクセスを一切持たない状態から始まる。launch 後に、Claude が作業するサービスを connectors として接続し、リポジトリを Claude GitHub App に付与する。

> ⚠️ **2026-10-11 訂正**: 以前は「セットアップとは ID のプロビジョニング（Access bundle を決めて適用すること）を指す」と書いていたが、現行の [Setup overview](https://claude.com/docs/claude-tag/admins/setup-overview) はセットアップを上の 4 ステップ（pairing から launch まで）とし、ツールへのアクセス付与はセットアップ後の作業として扱う。

### 1.2 Claude Code / Cowork との使い分け

|  | Claude Tag | Cowork | Claude Code |
|---|---|---|---|
| 動く場所 | Slack チャンネル | claude.ai のチャット | ターミナル / IDE |
| 誰のアクセスで動くか | **チームの**: 管理者がチャンネル単位で設定する service account の資格情報 | **自分の**: 個人の OAuth コネクタ | **自分の**: ローカルの資格情報とファイルシステム |
| 誰が作業を見えるか | チャンネル全員 | 自分だけ | 自分だけ |
| 向く用途 | チームで見て操舵する共有作業 | 個人のリサーチ・下書き | 自分のチェックアウトでのハンズオンなコーディング |

要約すると **チーム作業 → Claude Tag、個人作業 → Cowork か Claude Code**。Claude Tag の接続は「人」ではなく「エージェント自身」を service account で認証する点が本質的な違いである。

なお **1:1 DM は例外**で、自分の claude.ai アカウントと個人コネクタで動く（Cowork に近い）。一方 **group DM**（数人の Slack DM に Claude を加えたもの）はチャンネルと同じく Claude 自身の service account で動き、組織に課金される（§6・§7）。また 2026-09-24 の告知以降、チャンネルでも**依頼者本人が許可した場合に限り、本人の依頼にその人の個人コネクタを使える**（§6「個人コネクタ」）。

---

## 2. セッションモデル

### 2.1 スレッド = 1 セッション = 1 sandbox

`@Claude` にタスクを渡すとその**スレッド専用のセッション**が始まり、専用の sandbox が立つ。同じスレッドへの返信は同じセッションの継続なので、`--continue` や `/resume` に相当する操作は存在しない。

**同一チャンネルの 2 スレッドは 2 つの別セッション**であり、状態を共有しない。ターミナルのタブを分けるのと同じ感覚で、並行タスクはスレッドを分ける。

これとは別に、Claude が top-level で働くチャンネルには**チャンネル自身のセッション**が 1 つある。top-level のメッセージと top-level の @-mention はこのセッションが受け、別々の top-level の依頼の間でもコンテキストが引き継がれる。調査・ツール・長いやり取りが要るタスクだと、このセッションがメッセージの下にスレッドを立て、そのスレッド専用の working session を始める。top-level で `!restart` を送るとチャンネルのセッションが置き換わる。

sandbox は ephemeral な環境で、**ローカルマシンでは動かない**。既定は Anthropic ホストの環境で、実体は Claude Code on the web と同じエンジンである。スコープに self-hosted environment を選んだ場合は、社内ネットワークの runner で動く（§6「Cloud environments の注意」）。

> ⚠️ **2026-10-11 訂正**: 以前は「ローカルマシンや社内ネットワークでは動かない」と書いていたが、現行の [Cloud environments](https://code.claude.com/docs/en/cloud-environments) と [Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data) は、チャンネルのセッションが self-hosted environment（社内ネットワークの runner）でも動くと書いている。

### 2.2 リクエストのライフサイクル（5 ステップ）

1. **セッション開始** — 誰かが `@Claude` にタスクを渡す、または routine（スケジュール実行）が発火する。top-level ではチャンネル自身のセッションがメッセージを受け、スレッドのセッションを始める
2. **sandbox 構築** — そのスレッド用の隔離環境が作られる
3. **作業ループ** — チャンネルのアクセス権でタスクを進め、チェックリストをその場で編集していく
4. **結果がスレッドに届く** — 回答・ドキュメント・チャート・PR のいずれか
5. **待機期間** — ターンを終えて数分後に sandbox は解放されるがスレッドは残る。新しい返信で sandbox が再構築され、ループが再開する

> **スレッドが静かでも止まっているとは限らない**。Slack はメッセージ編集を通知しないため、チェックリストが進んでいてもタイムラインは動かない。スレッドを開いてチェック済み項目が増えていれば作業は進行中である。

### 2.3 待機期間を越えて残るもの

| | 待機期間を越えて残るか |
|---|---|
| 会話とそのコンテキスト | 残る |
| channel memory | 残る |
| push / 投稿 / PR 化した成果物 | 残る（外部システム側に） |
| **sandbox 内だけに存在するファイル** | **残らない**（依頼すれば作り直す） |

長時間タスクでは「進めながらブランチを push し、途中経過を投稿してほしい」と伝え、成果物を耐久性のある場所へ逃がしておく。

### 2.4 読み取るコンテキストの範囲

進行中のスレッドの途中で `@Claude` を呼ぶと、**スレッド全体ではなく「スレッドのメッセージの窓」**が渡される（他 bot の返信は除外）。長いスレッドでは重要な前提を言い直す。

> ⚠️ **2026-09-03 訂正**: 以前「**スレッド先頭から最大 50 メッセージ**」と書いていたが、**現行公式には件数も「先頭から」という方向も明示がない**（"gives it a window of the thread's messages, not the whole thread"）。件数を断定できないため窓の存在のみを記述する。

チャンネル履歴とピン留めも読む。加えて、参加していない public チャンネルのメッセージも **workspace 検索**で見つけられる（Slack ユーザーと同じ検索範囲。private チャンネルは検索しない）。workspace 検索を無効にする設定は無いが、Owner は **Channels Claude can search** で検索対象を Claude が参加しているチャンネルに絞れる。

**ゲストを含むチャンネルでは workspace 検索は使えない**（"Workspace search is unavailable in channels that include guests"）。ゲストを含むチャンネルでの挙動は **How should Claude work in channels with guests**（各スコープの Advanced タブ、Access グループ）で決まる。

| 値 | ゲストを含むチャンネルでの挙動 |
|---|---|
| **Restrict**（既定） | 返信しない。メンションされると、ゲストを含むチャンネルでは応答しない旨の短い通知を出す |
| **Channel only** | 返信するが、ゲストがいる間は channel-only access で動く。workspace / 組織から継承した bundle・connectors・リポジトリ・instructions は外れ（チャンネルに直接付けたものは残る）、memory と skills も使わず、スコープの environment ではなく標準の environment で動く |
| **Full access** | スコープが与える全アクセスで返信する |

Restrict と Channel only は Owner か Claude Tag admin（Enterprise の委任権限）が選べるが、Full access と Inherit への戻しは Owner だけが行える。**Full access でも、ゲストを含むチャンネルでは workspace 検索・人やチャンネルの検索・他チャンネルの読み取りをしない**（ゲストが見られない内容が混ざるため）。どの値でもゲストは Claude の投稿を読める。Restrict / Channel only では返信前にゲストの有無を確認し、この確認には Slack の `users:read` 権限が必要になる。

> ⚠️ **2026-10-11 再訂正**: 2026-09-03 の訂正で「ゲストを含むチャンネルでは workspace 検索が無効になる、は誤り」と書いたが、その訂正を差し戻す。現行の [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) は "Workspace search is unavailable in channels that include guests" と明記し、[Restrict where Claude Tag operates](https://claude.com/docs/claude-tag/admins/restrict-access) も Full access でも検索しないと書く。設定名と値も、以前本 doc に書いていた Allow Claude to work in channels with guests（Restrict / Allow）から、上の名称と 3 値に変わっている。

**他チャンネルへの投稿と follow**: セッションは、Claude が参加している同じ workspace の他の public チャンネルを読める（依頼元がゲストを含む場合を除く）。そこへ top-level で投稿できるのは依頼元が public チャンネルの場合で（例: 「このスレッドの要約を #announcements に投稿して」）、1:1 DM からは投稿ごとの **Approve and post** の承認が要り、private チャンネルと group DM からは投稿できない。`@Claude follow #incidents and tell me here if anything mentions billing` のように、他チャンネルやスレッドを見張らせて依頼元で報告させることもできる（スレッドから設定した follow は、そのスレッドが 7 日間無発言で終わる）。依頼元がゲストを含む会話や他社と共有した会話だと、返信や follow の通知は届かない。

---

### 2.5 データライフサイクル（Anthropic 側に何が残り、どう消すか）

§2.3 は **sandbox の揮発性**（残らないもの）を扱ったが、その裏側として **Anthropic 側に何が保持されるか**も押さえておく必要がある。削除要求やコンプライアンス対応で直接効く。

**beta 中は自動 retention が存在しない。** 下記はすべて、明示的な削除操作が行われるまで保持される。**組織の custom data retention 設定は Claude Tag の transcript と memory には適用されない**（適用されるのは published artifacts のみ）。

保持されるものは 8 種である。

| 保持対象 | 補足 |
|---|---|
| session transcripts | Claude が見たメッセージ、添付ファイル、編集前の旧版、**Slack 検索結果や connected tools から取得したデータ**を含む |
| memory | チャンネルごとの notes、public チャンネルから保存した workspace notes、1:1 DM の会話ごとの notes（§5） |
| routines | チャンネルや DM で設定した定期・単発タスクと実行履歴 |
| scopes とその設定 | |
| bundles と connectors | 資格情報を含む。workspace ではなく組織に属する |
| account links | |
| published artifacts | ここだけ組織の data retention 設定が効く |
| アプリの installation credential | |

運用上の要点は 4 つである。

1. **Slack でメッセージやファイルを消しても、既に transcript に入った内容は消えない。** Slack 側のメッセージは Slack の retention 設定に従う別コピーであり、Claude 側の削除では消えない（§2.4 の読み取り範囲と対で理解する）。
2. **「使わなくなる」では消えない。** プラン失効・Claude Tag の off（**Enable Claude Tag** 系スイッチや **Respond in all channels** / **Respond in channels** の off、DM の無効化）は、いずれもデータを削除しない。消すには **workspace の disconnect**（`claude.ai/admin-settings/claude-tag`）または **Slack からのアプリ uninstall** が必要である。pairing 後に ZDR や制限付き compliance 設定を採用しても同じで、Claude は応答を止め新規 pairing も拒否されるが、既存データは残る。
3. **削除操作の粒度は 4 段階しかない** — workspace / Grid の disconnect → channel scope の **Remove this scope** → scope memory の削除 → routine の削除。**単一スレッドの transcript だけを消す手段は存在しない。** beta 中は組織の data export に含まれず、**Compliance API からも列挙・削除できない**。個別対応は account team か privacy@anthropic.com に依頼する。
4. **セッションは削除ではなく archive される。** `@Claude !restart` 後の旧セッション、先頭メッセージが消されて閉じたスレッドのセッション（返信の有無を問わない）、約 1 時間の沈黙または約 1 日経過で置き換わる channel-level セッションは、いずれも **full transcript を保持したまま archive** され、channel / workspace のデータ削除まで残る。§2.1 の「スレッド = 1 セッション」を補正する事実である。

### 2.6 スレッドでの操作（コマンドと Stop ボタン）

Claude Code の割り込みや再プロンプトに当たる操作は、スレッドへの返信で行う（修正や追加の制約を書けば、実行中のタスクに取り込まれる）。ほかに `@Claude !<command>` 形式のコマンドがある。

| コマンド | 働き |
|---|---|
| `!help` | その workspace で使えるコマンドを一覧する（workspace ごとに異なりうる） |
| `!status` | Claude がまだ作業中かを、本人にだけ見える短いメモで返す。作業を中断せず、新しい依頼にも数えない |
| `!restart` | 詰まった・文脈を誤ったセッションを archive し、スレッドを読み直す新しいセッションで始め直す。top-level ではチャンネル自身のセッションを置き換える |
| `!mute` / `!unmute` | そのスレッドでの返信を止める / 戻す。スレッド単位で、チャンネル全体の mute は無い |
| `!fast` / `!fast off` | そのスレッドの fast mode を切り替える（Owner が fast mode を許可している場合。§3.3） |
| `!configure` | チャンネルの Configure ページへのリンクを返す |
| `!fork <prompt>` | 会話を新しいスレッドで続ける。`!fork #channel <prompt>` で別チャンネルに移せる |

working session が始まると、スレッドの下部に **Stop** ボタン付きの作業中表示が出る。

## 3. ClaudeCode 設定の継承（本 doc の中核）

セッションは sandbox で動くため、**ローカルマシンの設定は一切届かない**。代わりに「リポジトリにコミットした設定」と「管理者がチャンネルに設定したもの」の 2 経路で構成される。

### 3.1 リポジトリから読み込まれるもの

セッションは**リポジトリを持たない状態で始まる**。メッセージが（管理者がチャンネルに付与した）対象リポジトリを名指しし、Claude がそれを clone した**次のターン**から、以下が読み込まれる。

- `CLAUDE.md` / `.claude/CLAUDE.md` / `.claude/rules/*.md` — プロジェクトコンテキストとして
- `.claude/skills/` 配下の Skills — セッション内で使えるようになる

**`.claude/settings.json` の hooks は動かない**（"Hooks in a repository's `.claude/settings.json` don't run in the session"）。詳細と公式間の食い違いは §3.5 を参照。

> **リポジトリの Skills は、そのリポジトリを clone したセッションにしか効かない。** スコープ配下の全チャンネルに Skill を配りたい場合は、[skills repository](https://claude.com/docs/claude-tag/admins/skills-repo)（Claude が自分で PR を出して更新できる git リポジトリ）を使う。

**コード作業ではリポジトリ名を最初のメッセージに書く**のが実務上重要になる。名指しがなければ clone が起きず、`CLAUDE.md` も Skills も読み込まれないまま作業が始まる。

### 3.2 読み込まれないもの

| 対象 | 扱い |
|---|---|
| ローカルの `~/.claude` ディレクトリ | 届かない |
| 個人の `settings.json` | 届かない |
| シェルの環境変数 | 届かない |
| ローカル登録の MCP サーバー | 届かない |
| **リポジトリの `.mcp.json`** | **コミットされていても読み込まれない**（"A repository's `.mcp.json` is never loaded"） |
| **リポジトリの `.claude/settings.json` の hooks** | **動かない**（§3.5） |
| 組織の server-managed settings | **届かない**（"Claude Tag sessions don't receive server-managed settings"）。そこに定義した hooks も動かない。モデルの `availableModels` allowlist は Team では Claude Tag に適用されず、Enterprise でも一部の組織でしか適用されない |

`.mcp.json` の扱いは特に注意を要する。ローカルの ClaudeCode では `.mcp.json` がプロジェクトスコープの MCP 設定として機能するが、Claude Tag では**完全に無視される**。チャンネルから外部サービスへ届く経路は次の 2 つである。

- **管理者が設定した Claude Tag connectors**（bundle 経由でスコープに付く。custom connector・custom MCP server も含む）。依頼者が誰でも同じアクセスになる
- **依頼者本人の個人コネクタ**（claude.ai に登録したもの）。本人が許可したときに、本人の依頼にだけ使える（§6「個人コネクタ」）

> ⚠️ **2026-10-11 訂正**: 以前は「個人の claude.ai に登録したコネクタもチャンネルでは使えない」と書いていたが、2026-09-24 に個人コネクタのチャンネル利用が告知され、現行の [Personal connectors in channels](https://claude.com/docs/claude-tag/concepts/personal-connectors) が手順を定めている。

### 3.3 管理者設定に置き換わるもの

| ローカル ClaudeCode の設定 | Claude Tag での対応物 |
|---|---|
| `/model` | 管理者がスコープ単位で **Model** を設定（チャンネルの Configure ページでは **Default model**。モデル family を選ぶと、組織が許可する同 family の最新モデルで始まり、新モデルが来ると自動で移る）。スレッド内での切替も可能で、メンバーが Claude に頼んでチャンネルの既定を変えることもできる（スコープの **Channel member edits** が **Block** なら不可） |
| `/fast` | Owner が **Admin settings > Claude Code** の **Fast mode** を on にすると（Claude Code と共通の設定。Team / Enterprise では既定 off）、スレッド単位で `@Claude !fast` で on にできる。Opus 以外のスレッドは組織が許可する最新の Opus に移り、`!fast off` 後もそのモデルのまま。fast mode の料金で組織に課金される |
| 環境変数・API キー等のシークレット | 管理者が connectors としてプロビジョニング。**生の鍵は sandbox に入らず**、Agent Proxy がネットワーク層でリクエストに注入する |
| 権限プロンプト | セッションは **auto mode 固定**。Claude の permission checker が各操作をレビューし、止めることがある。管理者が **auto mode allow rules** で定型作業を事前承認する |

**auto mode allow rules** は 1 文の平文でスコープに追加する（スコープのページの Advanced タブ > Sessions。例:「このチャンネルのセッションからステージングクラスタへデプロイすることは通常の承認済みワークフローである」）。1 スコープあたり **最大 50 ルール・各 1,024 文字**。上位スコープのルールは下位へ継承され、チャンネル独自のルールは**上書きではなく加算**される。

permission checker は **Claude Sonnet 5** で動く。Enterprise で Sonnet 5 を組織の Models ページで off にすると、checker は allow rule に書かれていない操作（API 呼び出しなど）をブロックするようになる。

> ⚠️ allow rule を追加すると、そのスコープが覆う**全チャンネル**で当該アクションが都度承認なしに実行される。ルールは「ツール・アクション・環境」を名指しして狭く書き、機微なシステムを開けるものは必要な最小スコープに置く。

### 3.4 代替が存在しないもの

| ローカル ClaudeCode の設定 | Claude Tag |
|---|---|
| **effort レベル** | **設定不可**。セッションはモデルの既定 effort で動く |
| 環境変数 | **environment 側に対応物がある。** admin が「チャンネルのセッションが動く environment」に環境変数を設定し、**そのチャンネルの全セッションが読む**。個人ごとに作り分ける手段は無い。値は全セッションで読めるので、シークレットは環境変数ではなく connector にする |
| 個人 `settings.json` | 対応物なし。セッションは auto mode で動き、admin が **auto mode allow rules** でルーチン操作を事前承認する |
| workspace のセットアップスクリプト | **environment 側に対応物がある。** admin が environment に setup script を設定すると、**そのチャンネルの各セッション開始時にインストール済みの状態になる**。1 リポジトリだけが必要とするコマンドは、そのリポジトリの `CLAUDE.md` の install 手順を使う |

effort が固定される点は、`docs/best-practices.md` の「effort はセッション冒頭で確定させる」という運用指針が **Claude Tag には適用できない**ことを意味する。深い思考を要するタスクは、effort ではなく**モデル選択**とプロンプトの明示性で制御することになる。

### 3.5 hooks は動かない（依存ツールの入れ方）

**リポジトリの `.claude/settings.json` に書いた hooks は、Claude Tag のセッションでは動かない**（[Claude Tag for Claude Code users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users) と [Configure GitHub access](https://claude.com/docs/claude-tag/admins/configure-github) が明記）。組織の server-managed settings もセッションに届かないため、そこに定義した hooks も動かない。ローカルや Claude Code on the web で SessionStart hook に依存インストールを書いていても、Claude Tag では走らない前提で設計する。

> ⚠️ **2026-10-11 訂正**: 以前は「`.claude/settings.json` の hooks は Claude Code と同様に動く」「hooks は sandbox 内で動くが標準イメージで走る」と書いていたが、現行の Claude Tag 固有ページはいずれも repo の hooks が動かないと明記している。
>
> **公式ソース間の食い違い**: [Cloud environments](https://code.claude.com/docs/en/cloud-environments) は一般論として「Anthropic ホスト環境では Claude Code が repo と server-managed settings の hooks を実行する（Claude Tag では server-managed settings の hooks だけが動かない）」と書く。本 doc は製品固有で明記している Claude Tag 側を採る。

セッションの sandbox は標準のツール群が入った状態で始まる。足りないものを入れる場所は 2 つある。

- **チャンネルの全セッション向け**: admin がチャンネルのセッションが動く environment の **setup script** に install コマンドを書く（§3.4・§6「Cloud environments の注意」）
- **1 リポジトリ向け**: そのリポジトリの `CLAUDE.md` に install 手順を書く。ただし Claude は `CLAUDE.md` を**無条件のセットアップ手順ではなくガイダンスとして扱う**ため、「テストをビルド・実行する前に SDK をインストールする」のように**その作業の前提条件として**書く。sandbox はセッションごとに新品なので、インストールは毎回繰り返される

パッケージマネージャ（`apt` / `pip` / `npm` / `dotnet` 等）は既定レジストリに到達できるが、**それ以外のホストからのダウンロードは sandbox の egress 境界でブロックされうる**。ベンダー製 install スクリプトやサードパーティのパッケージソースより、標準のパッケージマネージャと既定レジストリを優先する。追加ホストは、Owner か Claude Tag admin が bundle の **What's in it > Add > Domain** で許可する（資格情報なしのドメインエントリ）。広い web アクセスが要る場合は、Owner が environment の network access level で与える。

---

## 4. 振る舞いを決める 4 層

Claude Tag の挙動は、設定場所の異なる 4 層で決まる。**ユーザー単位ではなくスコープ（チャンネル / workspace / 組織）単位**である点が Claude Code との最大の違いである。

| 層 | 内容 | 設定者 |
|---|---|---|
| **Connectors** | Claude が到達できるシステムの資格情報（GitHub / Drive / Datadog / 自社 API 等）。bundle にまとめてスコープに付ける | Owner / Claude Tag admin。channel manager は担当チャンネル用 bundle の資格情報のみ |
| **Plugins と Skills** | ツールの使い方やプロセスを教える指示。Plugin は 1 つ以上の Skill を束ねたもの | Owner / Claude Tag admin。チャンネルの Configure ページからメンバーも plugin を追加できる（admin が編集を制限していなければ） |
| **Custom instructions** | スコープの全セッションで読まれる常設ガイダンス。**channel memory より優先される** | 組織は Owner、workspace は Owner / Claude Tag admin。チャンネルの **Channel instructions** はチャンネルメンバーも可（**Channel member edits** が **Block** なら不可。channel manager は Block でも可） |
| **Channel memory** | チャンネルで作業しながら Claude が保存した事実 | チャンネルの誰でも |

**Claude Tag admin** は Enterprise の custom role に付ける **Claude Tag Admin** 権限で、Owner でなくても bundle・スコープ設定・Enable スイッチなどを管理できる（pairing・DM の可否・利用者制限などは Owner のみ）。**channel manager** は Enterprise で Owner がチャンネル単位に指名する人で、担当チャンネルの既定モデル・リポジトリ・bundle の資格情報と plugin・channel instructions を扱う。

Connectors と Plugins が「**何ができるか**」を決め、instructions と memory が「**どうやるか**」を形づくる。

常設の instructions は **組織 → workspace → Managed by の core instructions → チャンネル自身の Channel instructions** の順に読まれ、いずれも channel memory より優先される。

**スレッドは開始時点の Skills・Plugins・custom instructions を固定する**。実行中のスレッドはその内容を保持し続ける。一方 connectors とドメイン規則はリクエストごとに評価されるため、管理者が途中で追加した connector は実行中スレッドでも効く（ただし Claude は新しい connector を自分から告知しないので、サービス名を挙げて依頼する）。**設定変更後は新しいトップレベルスレッドを立てる**のが確実である。

### 4.1 Managed by（別チャンネルから instructions を管理する）

**Managed by** はチャンネル設定で、指定した別の Slack チャンネル（managing channel）のメンバーが、Claude に頼んでそのチャンネルの常設 instructions を書けるようにする。ヘルプデスクや on-call のように、中央のチームが admin 権限なしに複数チャンネルのルールを管理する用途を想定している。

- **設定**: Enterprise で Owner か Claude Tag admin が、対象チャンネルの Configure ページの **Admin** タブで設定する（Team には Admin タブが無い）
- **制約**: managing channel は 1 チャンネルあたり**最大 5 つ**。全チャンネルが同じ workspace の通常チャンネルで、Claude が参加していること（DM・group DM・Slack Connect・Grid 間共有チャンネルは不可）
- **変更の流れ**: managing channel で `@Claude set the instructions for #it-help to: ...` のように頼むと、差分を示すカードが出て、managing channel の正規メンバーが **Confirm** するまで反映されない。反映後に始まる会話から効き、実行中のスレッドは開始時の内容のまま
- **上限**: core instructions は 1 チャンネル 1 つで **16 KiB**、reference files は **最大 20 個・各 100 KiB**（core から名前で参照されたときに読まれる）
- **アクセス制御ではない**: managed text は対象チャンネルの memory と一緒に保存されるため、対象チャンネルのメンバーが Claude に頼めば変えられる。メンバーに変えさせたくないルールは組織・workspace の custom instructions に置く

### 4.2 on-call セットアップ

[`claude.ai/oncall`](https://claude.ai/oncall)（claude.ai の **Code** サイドバーの **On-call**）で、インシデント対応用の Claude を組織に 1 つ設定できる。実体は**監視・アラートツールの connectors・リポジトリ・skills を束ねた Access bundle** で、setup で選んだチャンネルに付く。Claude はアラートを見張って指定チャンネルに投稿するか、インシデントチャンネルに参加してタグ無しで調査に加わる（どちらか一方でも両方でもよい）。

- **チャンネル名 prefix**（例 `incident-`）を設定すると、一致する名前で作成・改名された**新しい public チャンネル**に Claude が自動で参加する（private チャンネルと他社共有チャンネルには入らない。ワイルドカード不可）
- setup を開けるのは、Team では組織の誰でも（組織全体に効く変更は権限がある場合のみ保存される）、Enterprise では Owner か Claude Tag admin
- on-call の作業は組織の usage として課金され、月次の spend limit で上限を設けられる

---

## 5. memory モデル

memory は「人」ではなく「場所」に紐づき、個人ではなくチームに蓄積される。保存先は 3 種類ある。

| 種類 | 中身と読まれる範囲 |
|---|---|
| **channel notes** | public / private を問わずチャンネルごとに持つ notes。そのチャンネルで作業するときに読む |
| **workspace notes** | **public チャンネルから**保存する、組織全体の規約などの notes。workspace の全チャンネルで読まれる。private チャンネルは読むだけで追加できず、private チャンネルで保存したものはそのチャンネルの notes に入る |
| **DM notes** | 1:1 DM の会話ごとの notes。Claude アカウントではなく workspace 側に保存され、workspace の disconnect で消える |

- `@Claude what do you remember about this channel?` で内容を確認でき、チャンネルの誰でも訂正・削除できる
- チャンネル固有の規約を覚えさせるには `@Claude remember for this channel: reports go out as tables` のように伝える
- **group DM** は自分専用の notes を持ち、それだけを読む。workspace notes は読みも追加もしない

> ⚠️ **2026-10-11 訂正**: 以前は「public チャンネルの memory は workspace 全体で共有される」と書いていたが、現行の [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) では、各チャンネルの notes はそのチャンネルのもので、workspace 全体で読まれるのは public チャンネルから保存した workspace notes だけである。

リポジトリの規約は `CLAUDE.md` に、チャンネルの規約は memory に置く、という住み分けになる。ただし前述のとおり **custom instructions は memory より優先される**ため、確実に守らせたい規約は Configure ページの Channel instructions に置く。

---

## 6. アクセスと権限（agent identity）

**何にアクセスできるかは「誰が依頼したか」ではなく「どのチャンネルか」で決まる**（例外は、依頼者本人が許可した個人コネクタだけ）。自分の権限から推測できないため、確認するには本人に訊く。

```
@Claude what can you access from this channel?
```

| 場所 | 資格情報 | 成果物の帰属 |
|---|---|---|
| チャンネル | 管理者がプロビジョニングした service account（加えて、依頼者本人が許可した場合はその人の個人コネクタ） | エージェント自身のアカウント（PR は Claude GitHub App 名義）。個人コネクタでの作業は依頼者の名義 |
| group DM | 管理者が workspace と組織に設定した service account（チャンネル単位の connection は効かない） | エージェント自身のアカウント |
| 1:1 DM（Claude アカウント接続済み） | 自分の claude.ai アカウントと個人コネクタ（追加した MCP サーバーを含む） | 自分（ただし PR は DM でも Claude GitHub App 名義） |
| 1:1 DM（Claude アカウント未接続） | Claude 自身の ID（そのメンバーが workspace に作ったチャンネルと同じ bundle）。個人コネクタは無い | エージェント自身のアカウント |

Owner は組織全体で DM を無効化できる（**Allow direct messages**。1:1 DM と group DM の両方が止まる）。group DM は scope を持たないため、1 つの group DM だけに bundle を付けたり止めたりはできない。Slack Connect で他社の人がいる group DM と、Enterprise Grid で共通の workspace を持たない人同士の group DM では Claude は答えない。

### 個人コネクタ（チャンネルでの本人依頼）

チャンネル（と group DM）で、依頼者本人の claude.ai コネクタ（カレンダーやメールなど）を、**その人自身の依頼に限り**使える。Team では全組織で on（admin の設定は不要）、Enterprise では admin が **Personal connectors** の設定で管理する。

- **最初に承認を求める**: 本人にだけ見えるプロンプトで **Allow**（auto mode で進め、機微に見える結果だけ投稿前に確認）/ **Allow with review**（全結果を投稿前に確認）/ **Don't allow** を選ぶ。**Use this choice for future requests** で保存でき、Slack の Claude アプリの **Home** タブで変更できる
- **他人の依頼には使われない**: 同じスレッドで他の人が出した指示はタスクの情報として扱われ、個人コネクタを使えない。routine など Claude が自発的に始める作業もチャンネル自身のアクセスで動く
- **投稿前チェック**: 資格情報・個人識別子・人事・顧客情報・法務・医療情報などを含む結果は保留され、本人が確認してから投稿される。公式は「screen であって保証ではない」としている
- **Enterprise の制御**: **Require human review of every message** で全結果の確認を強制できる。**組織として個人コネクタのチャンネル利用を off にする設定は無い**（特定サービスを締め出すにはコネクタ自体を組織の connector 設定で制限する）。また個人コネクタを使うタスクのチェックは **Claude Opus 5** で動くため、Enterprise で Opus 5 を off にすると、そのタスクは断られる
- 作業は本人の権限で動き、本人の名義で記録される。スレッドに投稿された結果はチャンネルの全員が読める

### Federated agent access

保存した資格情報の代わりに、**Anthropic が署名した短命の ID トークン（JWT、有効期間 10 分）**で Claude Tag のエージェント ID を自社システムに証明する仕組み。トークンは Agent Proxy がリクエストに付け、**モデルと sandbox には渡らない**。Anthropic 側に長期の資格情報を保存しないので、ローテーションや漏えいの対象になる鍵が無い。

| 接続方式 | トークンを受け取る側 |
|---|---|
| **Gateway** | 自社で運用するサービス。トークンを検証し、権限に対応づけて社内システムへ転送する（[サンプル実装](https://github.com/anthropics/claude-tag-wif-gateway-sample)あり） |
| **AWS role** | IAM OIDC identity provider 経由。trust policy に Anthropic の issuer と自組織を書いた role の一時資格情報を発行する |
| **Google Cloud identity** | workload identity pool 経由でアクセストークンを発行する |
| **Authorization server** | 自社の OAuth 2.0 認可サーバーが JWT bearer grant（RFC 7523）として受け取り、アクセストークンを返す |

受け取る側は署名・issuer・audience・有効期限・**subject** の 5 点を検証する。全 Claude Tag 組織のトークンは同じ issuer から出るため、subject（`wimse://identity.anthropic.com/org/<組織 ID>/agent/<agent ID>`）で自組織のものかを確かめる検証が必須である。接続は admin settings の **Federated agent access** ページで Owner（または Claude Tag の全管理権限を持つ admin）が行い、bundle に入れて適用先を選ぶ。**1:1 DM と self-hosted environment では使えない**（チャンネルでエージェント ID として動くときのもので、Anthropic ホスト環境が必要）。

### GitHub Actions に対してできること・できないこと

チャンネルでの Claude は **Claude GitHub App** として振る舞い、その ID には固定の Actions 権限が付く。**管理者設定で変更できず**、`api.github.com` を独自トークンでカスタム接続しても変わらない。

**できること**（公式の「Claude can」リスト）:

- workflow run / job / ログ / artifact の読み取り
- run や失敗 job の再実行、実行中 run のキャンセル
- **`workflow_dispatch` workflow の dispatch**
- **run / ログ / artifact の削除**
- **workflow の有効化・無効化**
- ブランチ push・PR 作成による `push` / `pull_request` トリガの発火
- `.github/workflows/` 配下の編集と PR 作成

**できないこと**（この 2 つのみ）:

- **`repository_dispatch` イベントの送信**
- 承認待ち run・保留デプロイの承認

できない操作は `403` で拒否される。`repository_dispatch` の要求は "repository_dispatch is not permitted for this session type." を返す。承認待ち run と保留デプロイの承認は、GitHub が人間のために挿入したチェックポイントを解除する行為であるため、リポジトリの **Actions** タブから人間が行う。

> ⚠️ **2026-09-03 訂正**: 本節は以前「`workflow_dispatch` の dispatch」「run / ログ / artifact の削除」「workflow の有効化・無効化」を**できない側に記載していたが、いずれも誤りだった**。公式の「Claude can」リストに 3 件とも明記されている。あわせて「`workflow_dispatch` ではなく `push` / `pull_request` トリガに載せ替える」という回避策も記載していたが、**dispatch が可能なため前提ごと不要**である。

### Cloud environments の注意

ここでいう environment は、ClaudeCode の [Cloud environments](https://code.claude.com/docs/en/cloud-environments) 機能を指し、**スコープ単位でどの環境を使うかを選べる**。environment は **setup script・環境変数・network access level** を持つ。個人ごとに作り分ける手段は無い（§3.4）が、チャンネル・workspace 単位では作り分けられる。

> ⚠️ **2026-09-03 訂正**: 以前 §3.4 で「全セッションが同一の**標準 sandbox イメージ**で動く」と書いていたが、**scope 単位 environment の存在により不成立**である。

セッション開始時、Claude は次の順で最初に見つかった environment を使う。

1. チャンネルの **Environment** 設定
2. workspace の **Environment** 設定
3. **Slack** ページ（組織全体）の **Environment** 設定
4. 組織の default environment（Owner が [`claude.ai/admin-settings/claude-code`](https://claude.ai/admin-settings/claude-code) の **Cloud sessions** で選ぶ）

environment の作成（admin settings の **Cloud environments** ページ）とスコープへの設定（スコープのページの Advanced タブ > Sessions）は、どちらも **Owner** の操作で、channel manager は変更できない。設定後は新しいスレッドで確かめる（実行中のスレッドは開始時の environment のまま）。ゲストがいて channel-only access で動くチャンネルでは、これらの設定にかかわらず標準の environment で動く。

チャンネルセッションが使えるのは **organization-level の environment だけ**で、**organization-shared environment** か **self-hosted environment** のどちらかである。**個人アカウントに紐づく environment は選べない**（チャンネルセッションはユーザーアカウントを持たずに動くため）。`claude.ai/code` で作った environment は個人アカウントに属し、picker に現れない。必要なら Owner が admin settings の Cloud environments ページから organization-shared として作り、スコープに pin する。

> **個人の environment がチャンネルに割り当たっている場合**（2026-10-11 確認）: チャンネルの cloud environment が `claude.ai/code` で作った個人アカウントのものだと、**ClaudeCode はセッションを即座に失敗させ、リトライしても直らない**（[Claude Code in Slack](https://code.claude.com/docs/en/slack) の原文 "Claude Code fails the session immediately, and retrying doesn't help"）。Owner で自分の environment なら、environment selector から organization に共有すれば解消する。[Troubleshoot Claude Tag setup](https://claude.com/docs/claude-tag/admins/troubleshooting) が書く「picker に現れない」は新しく選ぶときの話で、この記述と矛盾しない。

**self-hosted environment** を選んだスコープのセッションは、社内ネットワークの runner で動く。この場合、**admin が追加した connectors はそのセッションで使えない**（"Claude can't use the connectors an admin adds in those sessions"）。Federated agent access も Anthropic ホスト環境が必要で、self-hosted では使えない。runner がセッションを claim するまで、セッションは environment のキューで待つ。

> **self-hosted environment をめぐる公式間の不整合は 2026-10-11 に解消**: 以前は [Cloud environments](https://code.claude.com/docs/en/cloud-environments) が "can't run in self-hosted environments yet" と書き、Customize 側は picker に runner pool が並ぶと書いて食い違っていた。現行の Cloud environments は "Claude Tag channel sessions use organization-level environments only, either shared environments or self-hosted environments" と書き、[Troubleshoot Claude Tag setup](https://claude.com/docs/claude-tag/admins/troubleshooting) も "the environment or runner pool set on the nearest scope" と self-hosted でのキュー待ちを説明しており、公式間の食い違いは無くなった。
>
> ⚠️ **2026-10-11 訂正**: 2026-09-03 の時点では [Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data) の原文が「self-hosted のセッションでは Access bundles をまだ使えない（yet）」だったため、本 doc は「使えないのは Access bundles だけ」と書いていた。現行の原文は上の通り「admin が追加した connectors を使えない」で、"yet" は消えている。

---

## 7. 課金

**Slack に Claude を入れても seat 課金は増えない。** チャンネルと group DM での作業は、組織の usage balance から引かれる従量課金である。ただし **課金対象外の区分がある** — 「チャンネルを読むこと」「返信すべきか判断すること」「既知の知識だけで返す短い返信」は **usage balance に一切計上されず、どの limit にもカウントされない**。チャンネルから Claude が起動する working session（Claude が自発的に始めたものを含む）は従量課金の対象である。

| 作業 | 課金先 | 上限 |
|---|---|---|
| チャンネルの作業 | 組織の usage balance | spend limit と、チャンネル個別の limit |
| group DM の作業 | 組織の usage balance | spend limit と、各 group DM に適用される **Default spend limit** |
| 読む・返信を判断する・既知の知識での短い返信 | なし | どの limit にも数えない |
| 1:1 DM（Claude アカウント接続済みのメンバー） | 送信者自身の seat | seat の通常の利用上限（組織の spend limit の対象外） |
| 1:1 DM（Claude アカウント未接続のメンバー） | 組織の usage balance | メンバーごとに **7 日間・$50（Default spend limit がそれより低ければその額）・50 セッション**のいずれかまで。組織の spend limit にも数える |

- 組織の **usage balance**（Owner が資金を入れる、請求通貨建ての残高）から引かれる
- **spend limit** は**毎月初にリセット**され、pairing した全 workspace に適用される。チャンネル個別の limit と、自前の limit を持たないチャンネルと各 group DM に効く **Default spend limit** も設定できる。spend limit は定価（list price）で数え、個別の割引は請求時に適用される
- 組織の使用量が月の spend limit の **75%** と **90%** を超えると、Claude が作業中のチャンネルの top-level に警告を投稿する（1:1 DM では投稿しない）。上限に達すると Claude は作業を止め、スレッドで依頼者に伝える
- **spend limit とは別に throughput（rate）limit がある**。残高に余裕があってもスレッド起動速度・メッセージ配信速度で制限がかかり、その旨と待ち時間（通常は数秒）がスレッドで告知される。**spend limit を上げても rate limit は解消せず、rate limit された要求は課金されない**
- ⚠️ **Team プランは入金するまで一切動かない**。「**Required, before anything runs.** A Team plan has no usage balance until it's funded, and Claude won't respond in channels until it is」。**Enterprise（請求書払い）**は、spend limit を設定するまで上限なく請求書に載るため、設定が推奨されている
- **未接続メンバーの DM を組織課金にしない**には、利用者制限トグル（§1.1）の on・**Allow direct messages** の off・workspace の Enable スイッチ（または **Respond in all channels** / **Respond in channels**）の off のいずれかを行う。どれも DM 以外にも影響する
- fast mode のチャンネルスレッドは、fast mode の料金で組織に課金される
- チャンネル別の内訳は [admin settings の usage ページ](https://claude.ai/admin-settings/usage/claude-tag)で確認できる（定価ベース）。promotional credit で賄われた分はここでは $0.00 と表示されるため、その場合は [`claude.ai/analytics/claude-tag`](https://claude.ai/analytics/claude-tag) の **Spend by channel** 表の **List price** 列を見る。analytics ページは支出を **Engaged / Proactive / Scheduled / Monitoring**（Monitoring＝チャンネルを読むことで、課金されない）に分けて示す。Claude が自発的に始める作業（Proactive）を止めるには、チャンネルの **Respond automatically** を off にする
- **Enterprise** では、Claude Enterprise Analytics API の cost report を `claude_tag_user_id` で group_by すると、**Slack ユーザー別**の支出が取れる（[Attribute costs to users](https://claude.com/docs/claude-tag/admins/attribute-costs)。`read:analytics` scope の API キーが必要で、作成できるのは組織の primary owner のみ）。依頼された作業は依頼者に、Claude が自発的に始めた作業はスレッド内の該当メンバーに、routine は設定した人に計上される

> ⚠️ **2026-10-11 訂正**: 以前は「**DM は usage balance から引かれない**」と書いていたが、これは Claude アカウント接続済みメンバーの 1:1 DM に限った話だった。現行の [Set a spend limit](https://claude.com/docs/claude-tag/admins/set-spend-limit) では、group DM と未接続メンバーの 1:1 DM は組織の usage balance に課金される。

コスト感を掴むには、spend limit を設定した状態でパイロットを回し、チャンネル別内訳を観察する（タスクあたりのコスト目安は公開されていない）。

> **launch usage credit（2026-10-01 失効、歴史記述）**: 以前は「組織によっては launch usage credit が付いている」「launch usage credit は funded balance として数えられる」と書いていた。公式記事 [How healthcare organizations use Claude Tag](https://claude.com/resources/articles/how-healthcare-organizations-use-claude-tag)（2026-09-14）によれば、Claude Tag を有効化して GitHub を連携した Enterprise 組織に $25,000、10 seat 以上の Team 組織に $2,500 のクレジットが付与されていたが、**2026-10-01 に失効した**。現行 docs はクレジットを "promotional credit" と呼ぶ。

---

## 8. 旧「Claude Code in Slack」との関係

Claude Tag 以前から、Slack で `@Claude` にコーディングタスクを渡す **Claude Code in Slack** が存在した。両者は同じ `@Claude` Slack アプリの 2 つの版（Legacy と New）だが、動き方は別物である。

| | Claude Code in Slack（旧） | Claude Tag |
|---|---|---|
| セッションの実行主体 | **各ユーザー個人**の Claude アカウント | **組織の共有 ID**（service account） |
| 利用上限 | 個人のプラン上限を消費 | 組織の usage balance を消費 |
| リポジトリアクセス | 各自が個人で接続したリポジトリのみ | 管理者が bundle に付与したリポジトリ |
| アクセス制御 | チャンネルへの招待による | 管理者がスコープ単位で設定 |
| 対象プラン | **Pro / Max のみ**、かつ Claude Tag に接続されていない workspace に限る | **Team / Enterprise のみ** |

- **2026-10-05 に retire 済み**: Claude 組織と pairing した workspace では、旧版（admin settings 上の **Legacy**）はチャンネルで応答しない。Legacy のまま残ったチャンネルでは、応答の代わりに retire 通知が出る。スコープを Legacy に切り替えることもできない。DM は影響を受けない。既存の Slack アプリと `@Claude` ハンドルはそのまま残り、データは移行しない
- **移行手順**: pairing すると全 workspace / チャンネルが既定で **New** になる。`Claude's access` → `Channels` で **Changes from defaults** 列に **legacy Claude in Slack** と出るスコープを開き、Advanced タブの **Claude Tag version** を **New** にする。**Slack** 行にはこの表示が出ないため、Slack ページの Advanced タブも確認する。version で選べる値は **New / Inherit** で、Legacy は表示されるだけである。各スコープの Enable スイッチを off にすると両版とも止まる
- **Team プラン**: **Respond in channels** の単一スイッチを持つ組織には **Claude Tag version** の設定自体が無く、移行対象が無い（スコープを Legacy にしていた等の条件を満たす Team 組織には、Enterprise と同じスコープ単位の制御が出る）
- どちらの版が応答したかは「誰が成果物の author か」で判別でき、New 版は Claude GitHub App として author になる。詳細は [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) を参照
- **Pro / Max**: Claude Tag が使えないため、**Claude Tag に接続されていない workspace に限り**、旧版が引き続き唯一のセットアップ経路である。接続済みの workspace では、プランに関係なく retire 通知が返る

> ⚠️ **2026-10-11 訂正**: 以前は「Team / Enterprise では retire が予定されている（切替日は account team が案内）」「version の値は Off / Legacy / New / Inherit の 4 つで両版を並走できる」「Team は「Enable Claude Tag」の単一スイッチ」「旧版の対象プランは Pro / Max / Team / Enterprise」と書いていた。現行の [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) と [Claude Code in Slack](https://code.claude.com/docs/en/slack) は、2026-10-05 の retire、選べる値が New / Inherit であること、Team の単一スイッチ名が Respond in channels であること、旧版がチャンネルで応答するのは未接続 workspace の Pro / Max アカウントだけであることを明記している。

> 個人開発で Pro / Max プランを使う場合、Claude Tag は選択肢に入らない。Slack 連携が必要なら、Claude Tag に接続されていない workspace で [Claude Code in Slack](https://code.claude.com/docs/en/slack) を使うことになる。

---

## 関連ドキュメント

- [メモリ（CLAUDE.md）ガイド](memory.md) — Claude Tag が clone 後に読み込む `CLAUDE.md` / `.claude/rules/` の仕様
- [ClaudeCode Skills ガイド](skills.md) — `.claude/skills/` の書き方（Claude Tag でもそのまま効く）
- [ClaudeCode Hooks ガイド](hooks.md) — `.claude/settings.json` の hooks（Claude Tag のセッションでは repo の hooks は動かない。§3.5）
- [ClaudeCode の設定ファイル一覧と役割](config-files.md) — `.mcp.json` を含む設定ファイルの全体像（Claude Tag では `.mcp.json` は読まれず、`.claude/settings.json` の hooks も動かない）
- [ClaudeCode Plugins ガイド](plugins.md) — Plugin は Owner / Claude Tag admin が bundle の What's in it > Add > Plugin で付与する（チャンネルの Configure ページからメンバーも追加できる）
- [Claude モデル比較とプラン消費](model-comparison.md) — スコープ既定モデルを選ぶ際の判断材料
- [ClaudeCode ベストプラクティス](best-practices.md) — effort 運用（Claude Tag では effort 設定不可のため適用外）

## 出典

- [Introducing Claude Tag — anthropic.com/news](https://www.anthropic.com/news/introducing-claude-tag)（2026-06-23 発表）
- [Work with Claude Tag — claude.com/docs/claude-tag/overview](https://claude.com/docs/claude-tag/overview)
- [How Claude Tag works — concepts/how-it-works](https://claude.com/docs/claude-tag/concepts/how-it-works)
- [Claude Tag for Claude Code users — concepts/for-claude-code-users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users)
- [Configure GitHub access — admins/configure-github](https://claude.com/docs/claude-tag/admins/configure-github)
- [Customize Claude Tag — admins/customize](https://claude.com/docs/claude-tag/admins/customize)
- [Claude Code in Slack — code.claude.com/docs/en/slack](https://code.claude.com/docs/en/slack)
- [Per-service connection guides — admins/connections/overview](https://claude.com/docs/claude-tag/admins/connections/overview)
- [Set up a skills repository — admins/skills-repo](https://claude.com/docs/claude-tag/admins/skills-repo)
- [Troubleshoot Claude Tag setup — admins/troubleshooting](https://claude.com/docs/claude-tag/admins/troubleshooting)
- [Migrate from the earlier Claude in Slack — admins/migrate-from-earlier](https://claude.com/docs/claude-tag/admins/migrate-from-earlier)
- [Cloud environments — code.claude.com/docs/en/cloud-environments](https://code.claude.com/docs/en/cloud-environments)
- [Data lifecycle — concepts/data-lifecycle](https://claude.com/docs/claude-tag/concepts/data-lifecycle)
- [Security and data — concepts/security-and-data](https://claude.com/docs/claude-tag/concepts/security-and-data)
- [When Claude responds — users/when-claude-responds](https://claude.com/docs/claude-tag/users/when-claude-responds)
- [Set a spend limit — admins/set-spend-limit](https://claude.com/docs/claude-tag/admins/set-spend-limit)
- [Setup overview — admins/setup-overview](https://claude.com/docs/claude-tag/admins/setup-overview)
- [Restrict where Claude Tag operates — admins/restrict-access](https://claude.com/docs/claude-tag/admins/restrict-access)
- [Manage workspaces and versions — admins/workspaces](https://claude.com/docs/claude-tag/admins/workspaces)
- [Give Claude access to your tools — admins/add-connections](https://claude.com/docs/claude-tag/admins/add-connections)
- [How agent identity works — concepts/agent-identity](https://claude.com/docs/claude-tag/concepts/agent-identity)
- [Personal connectors in channels — concepts/personal-connectors](https://claude.com/docs/claude-tag/concepts/personal-connectors)
- [Use Claude Tag in a group DM — users/group-dms](https://claude.com/docs/claude-tag/users/group-dms)
- [What Claude Tag remembers — users/memory](https://claude.com/docs/claude-tag/users/memory)
- [Commands Claude Tag understands — users/commands](https://claude.com/docs/claude-tag/users/commands)
- [Manage a channel's instructions from another channel — admins/managed-by](https://claude.com/docs/claude-tag/admins/managed-by)
- [Set up Claude Tag for on-call — admins/setup-oncall](https://claude.com/docs/claude-tag/admins/setup-oncall)
- [Federated agent access — admins/federated-access/overview](https://claude.com/docs/claude-tag/admins/federated-access/overview)（AWS / Google Cloud / gateway / 認可サーバーの各接続手順・token reference・limits・troubleshooting は同節配下の 7 ページ）
- [Federated agent access limits — admins/federated-access/limits](https://claude.com/docs/claude-tag/admins/federated-access/limits)
- [Use Claude Tag at a healthcare organization — admins/healthcare](https://claude.com/docs/claude-tag/admins/healthcare)
- [Attribute costs to users — admins/attribute-costs](https://claude.com/docs/claude-tag/admins/attribute-costs)
- [Connect Amplitude — admins/connections/amplitude](https://claude.com/docs/claude-tag/admins/connections/amplitude)
- [Claude Tag now supports personal connectors in channels（article, 2026-09-24）](https://claude.com/resources/articles/claude-tag-now-supports-personal-connectors-in-channels)
- [How healthcare organizations use Claude Tag（article, 2026-09-14）](https://claude.com/resources/articles/how-healthcare-organizations-use-claude-tag) — BAA 対象外の前提と、launch credit の失効日（2026-10-01）の出典
- [How Anthropic employees use Claude Tag（blog, 2026-08-28）](https://claude.com/blog/how-anthropic-employees-use-claude-tag) — 3 部門の利用パターン。仕様の新情報は含まない
