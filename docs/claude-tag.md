# Claude Tag（Slack 上で動く組織共有の `@Claude`）

> 出典: [Introducing Claude Tag](https://www.anthropic.com/news/introducing-claude-tag) / [Work with Claude Tag](https://claude.com/docs/claude-tag/overview) / [How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works) / [Claude Tag for Claude Code users](https://claude.com/docs/claude-tag/concepts/for-claude-code-users) / [Configure GitHub access](https://claude.com/docs/claude-tag/admins/configure-github) / [Customize Claude Tag](https://claude.com/docs/claude-tag/admins/customize) / [Claude Tag（ClaudeCode docs）](https://code.claude.com/docs/en/claude-tag) / [Claude Code in Slack](https://code.claude.com/docs/en/slack) (2026-08-19 確認)

**Claude Tag** は、Slack のチャンネル内で `@Claude` を **組織の共有 ID** として動かす製品である。2026-06-23 に発表され、2026-08-19 時点で public beta。

本 doc が ClaudeCode ドキュメント群に含まれる理由は、Claude Tag が **Claude Code と同じエンジンで動き、リポジトリにコミットした ClaudeCode 設定をそのまま読み込む**ためである。`CLAUDE.md` や `.claude/skills/` の書き方が、そのまま Slack 上の挙動を決める。一方で `.mcp.json` は読まれず、effort は設定できず、権限は auto mode 固定という**運用差**がある。この「効くもの / 効かないもの」の境界を把握することが、本 doc の主目的である。

> **本 doc のスコープ**: ClaudeCode ユーザーの視点（設定の継承・セッションモデル・権限・課金）を主軸に置く。管理者向けの接続先ごとのセットアップ手順（Jira・Datadog・Snowflake など 16 サービス分）は公式の [Per-service connection guides](https://claude.com/docs/claude-tag/admins/connections/overview) に譲る。

---

## 1. Claude Tag とは

チャンネルにいる誰もが `@Claude` に仕事を渡せる。バグの再現から PR 作成、議論スレッドのドキュメント化、プロジェクト状況の集約などを、スレッド内にチェックリストを出しながら進め、やり取り全体がチャンネルに残る。

### 1.1 提供プランと前提

| 項目 | 内容 |
|---|---|
| 提供プラン | **Team / Enterprise のみ**。Free / Pro / Max では利用できない |
| デプロイ形態 | Anthropic のファーストパーティサービスのみ。**Bedrock / Vertex / Microsoft Foundry などサードパーティデプロイは対象外** |
| セットアップ | 組織の Slack workspace と Claude organization をペアリングする。実行には Claude 組織の **Owner** 権限が必要 |
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

### 2.4 読み取るコンテキストの範囲

進行中のスレッドの途中で `@Claude` を呼ぶと、**スレッド先頭から最大 50 メッセージ**（ルート + 古い側の返信。他 bot の返信は除外）が渡される。長いスレッドでは**メンション直前の最新メッセージが窓から外れうる**ため、重要な前提は言い直す。

チャンネル履歴とピン留めも読む。加えて、参加していない public チャンネルのメッセージも **workspace 検索**で見つけられる（Slack ユーザーと同じ検索範囲）。ただしゲストを含むチャンネルでは workspace 検索は無効になる。

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
| 環境変数 / 個人 `settings.json` | 対応物なし。全セッションが同一の**標準 sandbox イメージ**で動くため、個人ごとに実行環境を作り分ける手段が無い（スコープ単位で選ぶ **Cloud environments** は別の機能。§6 を参照） |
| workspace のセットアップスクリプト | 対応物なし。`CLAUDE.md` の install 手順で代替する |

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
| workflow run / job / ログ / artifact の読み取り | workflow の dispatch（`workflow_dispatch` / `repository_dispatch`） |
| run や失敗 job の再実行、実行中 run のキャンセル | 承認待ち run・保留デプロイの承認 |
| ブランチ push・PR 作成による `push` / `pull_request` トリガの発火 | run / ログ / artifact の削除 |
| `.github/workflows/` 配下の編集と PR 作成 | workflow の有効化・無効化 |

できない操作は `403` で拒否される。**Claude に自動化をオンデマンドで起動させたい場合は、`workflow_dispatch` ではなく `push` / `pull_request` トリガに載せ替える**。

### Cloud environments の注意

ここでいう environment は、§3.4 の「標準 sandbox イメージ」とは別の概念である。ClaudeCode の [Cloud environments](https://code.claude.com/docs/en/cloud-environments) 機能を指し、**スコープ単位でどの環境を使うかを選べる**。

スコープの **Environment** 設定に現れるのは、**organization-shared cloud environment** と self-hosted の runner pool のみである。**個人アカウントに紐づく environment は一切現れない**（チャンネルセッションはユーザーアカウントを持たずに動くため）。

個人アカウントで作った environment をチャンネルに割り当てようとすると、セッションは即座に失敗しリトライも効かない。Owner が admin settings の Cloud environments ページから organization-shared として作り直す必要がある。

---

## 7. 課金

**Slack に Claude を入れても seat 課金は増えない。** チャンネルとスレッドでの作業は従量課金である。

- 組織の **usage balance**（Owner が資金を入れる、請求通貨建ての残高）から引かれる
- **spend limit** が請求期間ごとの上限を決める。組織全体とチャンネル個別の両方に設定できる
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

- **Team / Enterprise**: Anthropic は旧版を Claude Tag に一本化する方針で、**retire が予定されている**。既存の Slack アプリと `@Claude` ハンドルはそのまま残る。切替日は Anthropic の account team が案内する。既存 workspace の移行手順は [Migrate from the earlier Claude in Slack](https://claude.com/docs/claude-tag/admins/migrate-from-earlier) を参照
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
