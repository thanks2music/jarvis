# Claude Tag（Slack 上で動く組織共有の `@Claude`）

> 出典: [Introducing Claude Tag](https://www.anthropic.com/news/introducing-claude-tag) / [Work with Claude Tag](https://claude.com/docs/claude-tag/overview) / [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) / [Claude Tag for Claude Code users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users) / [Configure GitHub access](https://claude.com/docs/claude-tag/admins/configure-github) / [Customize Claude Tag](https://claude.com/docs/claude-tag/admins/customize) / [Per-service connection guides](https://claude.com/docs/claude-tag/admins/connections/overview) / [Set up a skills repository](https://claude.com/docs/claude-tag/admins/skills-repo) / [Troubleshoot Claude Tag setup](https://claude.com/docs/claude-tag/admins/troubleshooting) / [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) / [Claude Tag（ClaudeCode docs）](https://code.claude.com/docs/en/claude-tag) / [Claude Code in Slack](https://code.claude.com/docs/en/slack) / [Cloud environments](https://code.claude.com/docs/en/cloud-environments) / [Data lifecycle](https://claude.com/docs/claude-tag/concepts/data-lifecycle) / [Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data) / [When Claude responds](https://claude.com/docs/claude-tag/users/when-claude-responds) / [Set a spend limit](https://claude.com/docs/claude-tag/admins/set-spend-limit) / [Setup overview](https://claude.com/docs/claude-tag/admins/setup-overview) (2026-09-03 確認)

**Claude Tag** は、Slack のチャンネル内で `@Claude` を **組織の共有 ID** として動かす製品である。2026-06-23 に発表され、2026-08-19 時点で public beta。

本 doc が ClaudeCode ドキュメント群に含まれる理由は、Claude Tag が **Claude Code と同じエンジンで動き、リポジトリにコミットした ClaudeCode 設定をそのまま読み込む**ためである。`CLAUDE.md` や `.claude/skills/` の書き方が、そのまま Slack 上の挙動を決める。一方で `.mcp.json` は読まれず、effort は設定できず、権限は auto mode 固定という**運用差**がある。この「効くもの / 効かないもの」の境界を把握することが、本 doc の主目的である。

> **本 doc のスコープ**: ClaudeCode ユーザーの視点（設定の継承・セッションモデル・権限・課金）を主軸に置く。管理者向けの接続先ごとのセットアップ手順（Jira・Datadog・Snowflake など 16 サービス分）は公式の [Per-service connection guides](https://claude.com/docs/claude-tag/admins/connections/overview) に譲る。

---

## 1. Claude Tag とは

チャンネルにいる誰もが `@Claude` に仕事を渡せる。**加えて Claude は、自分が参加するチャンネルの top-level メッセージとスレッド内の返信を @-mention の有無にかかわらず全て読み、返信すべきと判断したものには @-mention なしで返信する**（チャンネル単位の **Respond automatically** 設定。**既定は ON**）。バグの再現から PR 作成、議論スレッドのドキュメント化、プロジェクト状況の集約などを、スレッド内にチェックリストを出しながら進め、やり取り全体がチャンネルに残る。

### 1.1 提供プランと前提

| 項目 | 内容 |
|---|---|
| 提供プラン | **Team / Enterprise のみ**。Free / Pro / Max では利用できない |
| デプロイ形態 | Anthropic のファーストパーティサービスのみ。**Bedrock / Vertex / Microsoft Foundry などサードパーティデプロイは対象外** |
| セットアップ | 組織の Slack workspace と Claude organization を[ペアリングする](https://claude.com/docs/claude-tag/admins/setup-overview#pair-your-slack-workspace)。実行には Claude 組織の **Owner** 権限が必要。[動作確認手順](https://claude.com/docs/claude-tag/admins/setup-overview#verify-your-setup)も同ページ |
| ユーザー側の準備 | **不要**。チャンネルに入っていれば全員がそのまま使える |
| 設定場所 | [`claude.ai/admin-settings/claude-tag`](https://claude.ai/admin-settings/claude-tag) |

Slack アプリのインストールは前提条件であって、セットアップそのものではない。セットアップとは **ID のプロビジョニング**（Claude が名乗る資格情報＝ Access bundle を決め、どの workspace / チャンネルに適用するかを決めること）を指す。Claude Tag は外部システムへのアクセスを一切持たない状態から始まる。

### 1.2 Claude Code / Cowork との使い分け

|  | Claude Tag | Cowork | Claude Code |
|---|---|---|---|
| 動く場所 | Slack チャンネル | claude.ai のチャット | ターミナル / IDE |
| 誰のアクセスで動くか | **チームの**: 管理者がチャンネル単位で設定する service account の資格情報 | **自分の**: 個人の OAuth コネクタ | **自分の**: ローカルの資格情報とファイルシステム |
| 誰が作業を見えるか | チャンネル全員 | 自分だけ | 自分だけ |
| 向く用途 | チームで見て操舵する共有作業 | 個人のリサーチ・下書き | 自分のチェックアウトでのハンズオンなコーディング |

要約すると **チーム作業 → Claude Tag、個人作業 → Cowork か Claude Code**。Claude Tag の接続は「人」ではなく「エージェント自身」を service account で認証する点が本質的な違いである。

なお **DM は例外**で、自分の claude.ai アカウントと個人コネクタで動く（Cowork に近い）。

---

## 2. セッションモデル

### 2.1 スレッド = 1 セッション = 1 sandbox

`@Claude` にタスクを渡すとその**スレッド専用のセッション**が始まり、専用の sandbox が立つ。同じスレッドへの返信は同じセッションの継続なので、`--continue` や `/resume` に相当する操作は存在しない。

**同一チャンネルの 2 スレッドは 2 つの別セッション**であり、状態を共有しない。ターミナルのタブを分けるのと同じ感覚で、並行タスクはスレッドを分ける。

sandbox は Anthropic がホストする ephemeral な環境で、**ローカルマシンや社内ネットワークでは動かない**。実体は Claude Code on the web と同じマネージド compute である。

### 2.2 リクエストのライフサイクル（5 ステップ）

1. **セッション開始** — 誰かが `@Claude` にタスクを渡す、または routine（スケジュール実行）が発火する
2. **sandbox 構築** — そのスレッド用の隔離環境が作られる
3. **作業ループ** — チャンネルのアクセス権でタスクを進め、チェックリストをその場で編集していく
4. **結果がスレッドに届く** — 回答・ドキュメント・チャート・PR のいずれか
5. **待機期間** — sandbox は解放されるがスレッドは残る。新しい返信で sandbox が再構築され、ループが再開する

> **スレッドが静かでも止まっているとは限らない**。Slack はメッセージ編集を通知しないため、チェックリストが進んでいてもタイムラインは動かない。スレッドを開いてチェック済み項目が増えていれば作業は進行中である。

### 2.3 待機期間を越えて残るもの

| | 待機期間を越えて残るか |
|---|---|
| 会話とそのコンテキスト | 残る |
| channel memory | 残る |
| push / 投稿 / PR 化した成果物 | 残る（外部システム側に） |
| **sandbox 内だけに存在するファイル** | **残らない**（依頼すれば作り直す） |

長時間タスクでは「進めながらブランチを push し、途中経過を投稿してほしい」と伝え、成果物を耐久性のある場所へ逃がしておく。

### 2.5 データライフサイクル（Anthropic 側に何が残り、どう消すか）

§2.3 は **sandbox の揮発性**（残らないもの）を扱ったが、その裏側として **Anthropic 側に何が保持されるか**も押さえておく必要がある。削除要求やコンプライアンス対応で直接効く。

**beta 中は自動 retention が存在しない。** 下記はすべて、明示的な削除操作が行われるまで保持される。**組織の custom data retention 設定は Claude Tag の transcript と memory には適用されない**（適用されるのは published artifacts のみ）。

保持されるものは 8 種である。

| 保持対象 | 補足 |
|---|---|
| session transcripts | Claude が見たメッセージ、添付ファイル、編集前の旧版、**Slack 検索結果や connected tools から取得したデータ**を含む |
| memory | scope 単位 |
| routines | |
| scopes とその設定 | |
| Access bundles | |
| account links | |
| published artifacts | ここだけ組織の data retention 設定が効く |
| アプリの installation credential | |

運用上の要点は 4 つである。

1. **Slack でメッセージやファイルを消しても、既に transcript に入った内容は消えない。** Slack 側のメッセージは Slack の retention 設定に従う別コピーであり、Claude 側の削除では消えない（§2.4 の読み取り範囲と対で理解する）。
2. **「使わなくなる」では消えない。** プラン失効・Claude Tag の off・スコープの **Off** 設定は、いずれもデータを削除しない。消すには **workspace の disconnect**（`claude.ai/admin-settings/claude-tag`）または **Slack からのアプリ uninstall** が必要である。pairing 後に ZDR や制限付き compliance 設定を採用しても同じで、Claude は応答を止め新規 pairing も拒否されるが、既存データは残る。
3. **削除操作の粒度は 4 段階しかない** — workspace / Grid の disconnect → channel scope の **Remove this scope** → scope memory の削除 → routine の削除。**単一スレッドの transcript だけを消す手段は存在しない。** beta 中は組織の data export に含まれず、**Compliance API からも列挙・削除できない**。個別対応は account team か privacy@anthropic.com に依頼する。
4. **セッションは削除ではなく archive される。** `@Claude !restart` 後の旧セッション、返信前に先頭メッセージが消されたスレッド、約 1 時間の沈黙または 1 日経過で置き換わる channel-level セッションは、いずれも **full transcript を保持したまま archive** され、channel / workspace のデータ削除まで残る。§2.1 の「スレッド = 1 セッション」を補正する事実である。

### 2.4 読み取るコンテキストの範囲

進行中のスレッドの途中で `@Claude` を呼ぶと、**スレッド全体ではなく「スレッドのメッセージの窓」**が渡される（他 bot の返信は除外）。長いスレッドでは重要な前提を言い直す。

> ⚠️ **2026-09-03 訂正**: 以前「**スレッド先頭から最大 50 メッセージ**」と書いていたが、**現行公式には件数も「先頭から」という方向も明示がない**（"gives it a window of the thread's messages, not the whole thread"）。件数を断定できないため窓の存在のみを記述する。

チャンネル履歴とピン留めも読む。加えて、参加していない public チャンネルのメッセージも **workspace 検索**で見つけられる（Slack ユーザーと同じ検索範囲）。

> ⚠️ **2026-09-03 訂正**: 以前「ゲストを含むチャンネルでは workspace 検索は無効になる」と書いていたが誤り。正しくは **Allow Claude to work in channels with guests** の既定が **Restrict** で、**ゲストがいるチャンネルでは Claude はそもそも返信しない**（返信前にゲストの有無を確認する。この確認には Slack の `users:read` 権限が必要）。**Allow に変えても workspace 検索が復活するわけではない**。Allow はそのスコープが覆う全ゲストチャンネルに適用され、ゲストは Claude の返信を見て操作できるようになる。

---

## 3. ClaudeCode 設定の継承（本 doc の中核）

セッションは sandbox で動くため、**ローカルマシンの設定は一切届かない**。代わりに「リポジトリにコミットした設定」と「管理者がチャンネルに設定したもの」の 2 経路で構成される。

### 3.1 リポジトリから読み込まれるもの

セッションは**リポジトリを持たない状態で始まる**。メッセージが対象リポジトリを名指しし、Claude がそれを clone した**次のターン**から、以下が読み込まれる。

- `CLAUDE.md` / `.claude/CLAUDE.md` / `.claude/rules/*.md` — プロジェクトコンテキストとして
- `.claude/skills/` 配下の Skills — セッション内で使えるようになる
- `.claude/settings.json` のプロジェクト設定 — ここで定義した **hooks は Claude Code と同様に動く**

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

`.mcp.json` の扱いは特に注意を要する。ローカルの ClaudeCode では `.mcp.json` がプロジェクトスコープの MCP 設定として機能するが、Claude Tag では**完全に無視される**。外部サービスへの到達手段は Access bundle の connections のみで、個人の claude.ai に登録したコネクタもチャンネルでは使えない。

### 3.3 管理者設定に置き換わるもの

| ローカル ClaudeCode の設定 | Claude Tag での対応物 |
|---|---|
| `/model` | 管理者がスコープ単位で **Default model** を設定。スレッド内での切替も可能 |
| 環境変数・API キー等のシークレット | 管理者が connections としてプロビジョニング。**生の鍵は sandbox に入らず**、Agent Proxy がネットワーク層でリクエストに注入する |
| 権限プロンプト | セッションは **auto mode 固定**。管理者が **auto mode allow rules** で定型作業を事前承認する |

**auto mode allow rules** は 1 文の平文でスコープに追加する（例:「このチャンネルのセッションからステージングクラスタへデプロイすることは通常の承認済みワークフローである」）。1 スコープあたり **最大 50 ルール・各 1,024 文字**。上位スコープのルールは下位へ継承され、チャンネル独自のルールは**上書きではなく加算**される。

> ⚠️ allow rule を追加すると、そのスコープが覆う**全チャンネル**で当該アクションが都度承認なしに実行される。ルールは「ツール・アクション・環境」を名指しして狭く書き、機微なシステムを開けるものは必要な最小スコープに置く。

### 3.4 代替が存在しないもの

| ローカル ClaudeCode の設定 | Claude Tag |
|---|---|
| **effort レベル** | **設定不可**。セッションはモデルの既定 effort で動く |
| 環境変数 | **environment 側に対応物がある。** admin が「チャンネルのセッションが動く environment」に環境変数を設定し、**そのチャンネルの全セッションが読む**。個人ごとに作り分ける手段は無い |
| 個人 `settings.json` | 対応物なし。セッションは auto mode で動き、admin が **auto mode allow rules** でルーチン操作を事前承認する |
| workspace のセットアップスクリプト | **environment 側に対応物がある。** admin が environment に setup script を設定すると、**そのチャンネルの各セッション開始時にインストール済みの状態になる**。1 リポジトリだけが必要とするコマンドは、そのリポジトリの `CLAUDE.md` の install 手順を使う |

effort が固定される点は、`docs/best-practices.md` の「effort はセッション冒頭で確定させる」という運用指針が **Claude Tag には適用できない**ことを意味する。深い思考を要するタスクは、effort ではなく**モデル選択**とプロンプトの明示性で制御することになる。

### 3.5 hooks と sandbox イメージ

hooks は sandbox 内で動くが、**どのリポジトリを clone しても同じ標準イメージ**で走る。イメージに含まれないコマンドを呼ぶ hook は、そのままでは失敗する。

対処はリポジトリの `CLAUDE.md` に install 手順を書くこと。ただし Claude は `CLAUDE.md` を**無条件のセットアップ手順ではなくガイダンスとして扱う**ため、「テストをビルド・実行する前に SDK をインストールする」のように**その作業の前提条件として**書く。sandbox はセッションごとに新品なので、インストールは毎回繰り返される。

パッケージマネージャ（`apt` / `pip` / `npm` / `dotnet` 等）は既定レジストリに到達できるが、**それ以外のホストからのダウンロードは sandbox の egress 境界でブロックされうる**。ベンダー製 install スクリプトやサードパーティのパッケージソースより、標準のパッケージマネージャと既定レジストリを優先する。追加ホストの許可は Owner が bundle の Domains タブで行う。

---

## 4. 振る舞いを決める 4 層

Claude Tag の挙動は、設定場所の異なる 4 層で決まる。**ユーザー単位ではなくスコープ（チャンネル / workspace / 組織）単位**である点が Claude Code との最大の違いである。

| 層 | 内容 | 設定者 |
|---|---|---|
| **Connections** | Claude が到達できるシステムの資格情報（GitHub / Drive / Datadog / 自社 API 等） | Owner |
| **Plugins と Skills** | ツールの使い方やプロセスを教える指示。Plugin は 1 つ以上の Skill を束ねたもの | Owner |
| **Custom instructions** | スコープの全セッションで読まれる常設ガイダンス。**channel memory より優先される** | Owner（チャンネルスコープはチャンネルメンバーも可） |
| **Channel memory** | チャンネルで作業しながら Claude が保存した事実 | チャンネルの誰でも |

Connections と Plugins が「**何ができるか**」を決め、instructions と memory が「**どうやるか**」を形づくる。

**スレッドは開始時点の Skills・Plugins・custom instructions を固定する**。実行中のスレッドはその内容を保持し続ける。一方 connections とドメイン規則はリクエストごとに評価されるため、管理者が途中で追加した接続は実行中スレッドでも効く（ただし Claude は新しい接続を自分から告知しないので、サービス名を挙げて依頼する）。**設定変更後は新しいトップレベルスレッドを立てる**のが確実である。

---

## 5. memory モデル

memory は「人」ではなく「場所」に紐づき、個人ではなくチームに蓄積される。

- **public チャンネルの memory は workspace 全体で共有される**。`#launch-week` で記録した決定は `#gtm-west` での質問時にも参照される
- **private チャンネル**は workspace memory を読むが、保存先はそのチャンネル専用のストアになる
- `@Claude what do you remember about this channel?` で内容を確認でき、チャンネルの誰でも訂正・削除できる
- チャンネル固有の規約を覚えさせるには `@Claude remember for this channel: reports go out as tables` のように伝える

リポジトリの規約は `CLAUDE.md` に、チャンネルの規約は memory に置く、という住み分けになる。ただし前述のとおり **custom instructions は memory より優先される**ため、確実に守らせたい規約は Configure ページの Channel instructions に置く。

---

## 6. アクセスと権限（agent identity）

**何にアクセスできるかは「誰が依頼したか」ではなく「どのチャンネルか」で決まる。** 自分の権限から推測できないため、確認するには本人に訊く。

```
@Claude what can you access from this channel?
```

| 場所 | 資格情報 | 成果物の帰属 |
|---|---|---|
| チャンネル | 管理者がプロビジョニングした service account | エージェント自身のアカウント（PR は Claude GitHub App 名義） |
| DM | 自分の claude.ai アカウントと個人コネクタ | 自分（ただし PR は DM でも Claude GitHub App 名義） |

Owner は組織全体で DM を無効化できる。

### GitHub Actions に対してできること・できないこと

チャンネルでの Claude は **Claude GitHub App** として振る舞い、その ID には固定の Actions 権限が付く。**管理者設定で変更できず**、`api.github.com` を独自トークンでカスタム接続しても変わらない。

| できる | できない |
|---|---|
| workflow run / job / ログ / artifact の読み取り | **`repository_dispatch` イベントの送信** |
| run や失敗 job の再実行、実行中 run のキャンセル | 承認待ち run・保留デプロイの承認 |
| **`workflow_dispatch` workflow の dispatch** | |
| **run / ログ / artifact の削除** | |
| **workflow の有効化・無効化** | |
| ブランチ push・PR 作成による `push` / `pull_request` トリガの発火 | |
| `.github/workflows/` 配下の編集と PR 作成 | |

できない操作は `403` で拒否される。`repository_dispatch` の要求は "repository_dispatch is not permitted for this session type." を返す。承認待ち run と保留デプロイの承認は、GitHub が人間のために挿入したチェックポイントを解除する行為であるため、リポジトリの **Actions** タブから人間が行う。

> ⚠️ **2026-09-03 訂正**: 本節は以前「`workflow_dispatch` の dispatch」「run / ログ / artifact の削除」「workflow の有効化・無効化」を**できない側に記載していたが、いずれも誤りだった**。公式の「Claude can」リストに 3 件とも明記されている。あわせて「`workflow_dispatch` ではなく `push` / `pull_request` トリガに載せ替える」という回避策も記載していたが、**dispatch が可能なため前提ごと不要**である。

### Cloud environments の注意

ここでいう environment は、ClaudeCode の [Cloud environments](https://code.claude.com/docs/en/cloud-environments) 機能を指し、**スコープ単位でどの環境を使うかを選べる**。environment は **setup script・環境変数・network access level** を持つため、§3.4 の「個人ごとに環境を作り分ける手段が無い」はスコープ単位では成立しない。

> ⚠️ **2026-09-03 訂正**: 以前 §3.4 で「全セッションが同一の**標準 sandbox イメージ**で動く」と書いていたが、**scope 単位 environment の存在により不成立**である。

チャンネルセッションが動くのは **organization-shared な Anthropic ホスト環境のみ**である。**個人アカウントに紐づく environment は選べない**（チャンネルセッションはユーザーアカウントを持たずに動くため）。

個人アカウントで作った environment をチャンネルに割り当てようとすると、セッションは即座に失敗しリトライも効かない。Owner が admin settings の Cloud environments ページから organization-shared として作り直す必要がある。`claude.ai/code` で作った environment は個人アカウントに属するため picker に現れない。

> **self-hosted environment の扱い（2026-09-03 に解決）**: 公式 [Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data) が「Sessions in a **self-hosted environment run on runners inside your network**, and Claude **can't use Access bundles** in those sessions yet」と明記し、矛盾は解消された。
>
> **実行はできる。使えないのは Access bundles だけである。**
>
> ⚠️ **2026-09-03 訂正**: 本 doc は以前、公式ドキュメント間の食い違いに対して「**使えない**」側（[Configure cloud environments](https://code.claude.com/docs/en/cloud-environments) の "can't run in self-hosted environments yet"）を採用していたが、**その判断は公式に否定された**。picker に runner pool が並ぶという [Customize Claude Tag](https://claude.com/docs/claude-tag/admins/customize) 側の記述が正しかったことになる。

---

## 7. 課金

**Slack に Claude を入れても seat 課金は増えない。** チャンネルとスレッドでの作業は従量課金である。ただし **課金対象外の区分がある** — 「チャンネルを読むこと」「返信すべきか判断すること」「既知の知識だけで返す短い返信」は **usage balance に一切計上されず、どの limit にもカウントされない**。チャンネルから Claude が起動する working session は従量課金の対象である。

- 組織の **usage balance**（Owner が資金を入れる、請求通貨建ての残高）から引かれる
- **spend limit** が請求期間ごとの上限を決める。組織全体とチャンネル個別の両方に設定できる
- **spend limit とは別に throughput（rate）limit がある**。残高に余裕があってもスレッド起動速度・メッセージ配信速度で制限がかかり、その旨と待ち時間（通常は数秒）がスレッドで告知される。**spend limit を上げても rate limit は解消せず、rate limit された要求は課金されない**
- ⚠️ **Team プランは入金するまで一切動かない**。「**Required, before anything runs.** A Team plan has no usage balance until it's funded, and Claude won't respond in channels until it is」。launch usage credit は funded balance として数えられるため、クレジット購入前に付与の有無を確認する
- **DM は usage balance から引かれない**。送信者自身の claude.ai アカウントで動き、その seat の通常の利用上限に従う。組織の spend limit の対象外
- チャンネル別の内訳は [admin settings の usage ページ](https://claude.ai/admin-settings/usage/claude-tag)で確認できる

コスト感を掴むには、spend limit を設定した状態でパイロットを回し、チャンネル別内訳を観察する。組織によっては launch usage credit が付いている場合がある。

---

## 8. 旧「Claude Code in Slack」との関係

Claude Tag 以前から、Slack で `@Claude` にコーディングタスクを渡す **Claude Code in Slack** が存在した。両者は別物である。

| | Claude Code in Slack（旧） | Claude Tag |
|---|---|---|
| セッションの実行主体 | **各ユーザー個人**の Claude アカウント | **組織の共有 ID**（service account） |
| 利用上限 | 個人のプラン上限を消費 | 組織の usage balance を消費 |
| リポジトリアクセス | 各自が個人で接続したリポジトリのみ | 管理者が bundle に付与したリポジトリ |
| アクセス制御 | チャンネルへの招待による | 管理者がスコープ単位で設定 |
| 対象プラン | Pro / Max / Team / Enterprise | **Team / Enterprise のみ** |

- **Team / Enterprise**: Anthropic は旧版を Claude Tag に一本化する方針で、**retire が予定されている**。既存の Slack アプリと `@Claude` ハンドルはそのまま残る。切替日は Anthropic の account team が案内する（公式も "check with your account team for the cutover date" のまま）。**移行手順**: pairing すると各スコープの **Claude Tag version** が既定で **New** になるため、`Claude Tag's access` → `Slack` で各スコープの **Advanced** を開き、**Legacy** が残るものを **New** に切り替える。version の値は **Off / Legacy / New / Inherit** の 4 つで、1 つの workspace で両版を並走させた段階移行ができる。**Team プランは「Enable Claude Tag」の単一スイッチがこの version 設定を置き換えるため、移行対象そのものが無い**。どちらの版が応答したかは「誰が成果物の author か」で判別でき、New 版は Claude GitHub App として author になる。詳細は [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) を参照
- **Pro / Max**: Claude Tag が使えないため、**旧版が引き続き唯一のセットアップ経路**である

> 個人開発で Pro / Max プランを使う場合、Claude Tag は選択肢に入らない。Slack 連携が必要なら [Claude Code in Slack](https://code.claude.com/docs/en/slack) を使うことになる。

---

## 関連ドキュメント

- [メモリ（CLAUDE.md）ガイド](memory.md) — Claude Tag が clone 後に読み込む `CLAUDE.md` / `.claude/rules/` の仕様
- [ClaudeCode Skills ガイド](skills.md) — `.claude/skills/` の書き方（Claude Tag でもそのまま効く）
- [ClaudeCode Hooks ガイド](hooks.md) — `.claude/settings.json` の hooks（sandbox 内で動く。標準イメージの制約に注意）
- [ClaudeCode の設定ファイル一覧と役割](config-files.md) — `.mcp.json` を含む設定ファイルの全体像（Claude Tag では `.mcp.json` のみ無効）
- [ClaudeCode Plugins ガイド](plugins.md) — Plugin は Owner が bundle の Plugins タブで付与する
- [Claude モデル比較とプラン消費](model-comparison.md) — スコープ既定モデルを選ぶ際の判断材料
- [ClaudeCode ベストプラクティス](best-practices.md) — effort 運用（Claude Tag では effort 設定不可のため適用外）

## 出典

- [Introducing Claude Tag — anthropic.com/news](https://www.anthropic.com/news/introducing-claude-tag)（2026-06-23 発表）
- [Work with Claude Tag — claude.com/docs/claude-tag/overview](https://claude.com/docs/claude-tag/overview)
- [How Claude Tag works — concepts/how-it-works](https://claude.com/docs/claude-tag/concepts/how-it-works)
- [Claude Tag for Claude Code users — concepts/for-claude-code-users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users)
- [Configure GitHub access — admins/configure-github](https://claude.com/docs/claude-tag/admins/configure-github)
- [Customize Claude Tag — admins/customize](https://claude.com/docs/claude-tag/admins/customize)
- [Claude Tag — code.claude.com/docs/en/claude-tag](https://code.claude.com/docs/en/claude-tag)
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
- [How Anthropic employees use Claude Tag（blog, 2026-08-28）](https://claude.com/blog/how-anthropic-employees-use-claude-tag) — 3 部門の利用パターン。仕様の新情報は含まない
