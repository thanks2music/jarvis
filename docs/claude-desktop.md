# Claude Desktop の設定ファイル

> 出典: [MCP Quickstart](https://modelcontextprotocol.io/quickstart) / [DeepWiki - modelcontextprotocol/docs](https://deepwiki.com/modelcontextprotocol/docs) / [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop) / [Test iOS apps in the simulator](https://code.claude.com/docs/en/desktop-ios-simulator) / [Self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments) / [Self-hosted environments quickstart](https://code.claude.com/docs/en/self-hosted-environments-quickstart) / [Self-hosted environments reference](https://code.claude.com/docs/en/self-hosted-environments-reference) / [Self-hosted environments configuration](https://code.claude.com/docs/en/self-hosted-environments-configuration) / [whats-new week 30](https://code.claude.com/docs/en/whats-new/2026-w30) / [whats-new week 33](https://code.claude.com/docs/en/whats-new/2026-w33) / [whats-new week 35](https://code.claude.com/docs/en/whats-new/2026-w35) / [whats-new week 36](https://code.claude.com/docs/en/whats-new/2026-w36) / [whats-new week 37](https://code.claude.com/docs/en/whats-new/2026-w37) / [Network configuration](https://code.claude.com/docs/en/network-config) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) / [Projects](https://code.claude.com/docs/en/claude-projects) / [Claude Cowork and chat are now one Claude](https://claude.com/resources/articles/cowork-is-now-claude) / [Set up Cowork (local mode) for a HIPAA-ready organization](https://claude.com/docs/cowork/hipaa-setup) / Claude Desktop on 3P の各ページ（[Unified Claude](https://claude.com/docs/third-party/claude-desktop/unified-claude) / [Enterprise Admin Console](https://claude.com/docs/third-party/claude-desktop/admin-console) / [Built-in browser and Claude in Chrome](https://claude.com/docs/third-party/claude-desktop/browser) / [Managed MCP sign-in](https://claude.com/docs/third-party/claude-desktop/mcp-sign-in) / [Box](https://claude.com/docs/third-party/claude-desktop/connectors-box) / [Google Cloud](https://claude.com/docs/third-party/claude-desktop/connectors-google-cloud) / [Salesforce](https://claude.com/docs/third-party/claude-desktop/connectors-salesforce) / [Models and effort levels](https://claude.com/docs/third-party/claude-desktop/models)） / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。CHANGELOG 由来の記述は v2.1.258 までを反映)

Claude Desktop は ClaudeCode とは別のデスクトップアプリケーションであり、独自の設定ファイルを持つ。MCP サーバーの設定方法が ClaudeCode とは異なるため、混同しないよう整理する。

## アプリの構成と提供プラットフォーム

公式 Desktop ページ（2026-10-11 時点）は、Claude Desktop を **Chat / Cowork / Code の 3 タブ**構成として説明している。このうち **Code タブが Claude Code 相当**の機能を提供する（本ドキュメントで「Claude Desktop 上のセッション」と書いているのは Code タブのセッションを指す）。

- **macOS / Windows** に加えて **Linux beta**（apt / `.deb`）が提供されている
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop)

### Cowork と chat の統合（2026-09-16 発表）

**2026-10-11 更新**: 以前は「Chat / Cowork / Code の 3 タブ構成である」とだけ書いていた。2026-09-16 の公式記事で、**Cowork と chat を 1 つの Claude に統合する**ことが発表された。

| 論点 | 公式記事の記載 |
|---|---|
| 内容 | 短い質問も大きなタスクも同じ会話で受け、Cowork と Claude Design でできることをどの会話からでも使えるようにする |
| 展開 | **Pro / Max プランから**、web・desktop・mobile の Claude app で数週間かけて段階展開する。有効化の操作は不要 |
| 他プラン | Team / Free は「soon」で追随。Enterprise は組織に変更が入る **30 日以上前に管理者へ連絡**する |
| 既存データ | Cowork を使っていた場合も、chats / projects / artifacts / connectors / skills はそのまま残る |
| 同時発表 | Claude Docs と Claude Slides（有料プランの beta。Enterprise は管理者が有効化の時期を選ぶ） |

- ⚠️ 記事は **Code タブの扱いに触れていない**。first-party で Code タブが統合後も別のまま残るかは、記事からは読み取れない（下記の 3P 版は「Code は別のまま」と明記している）。
- 出典: [Claude Cowork and chat are now one Claude](https://claude.com/resources/articles/cowork-is-now-claude)

### 3P 版の Unified Claude（beta）

Amazon Bedrock などのサードパーティ基盤で動く Claude Desktop（Desktop 3P）には、同じ統合が **Unified Claude** という名前で入っている。

- **beta**。**11 月 10 日まで opt-in で、それ以降は全 Desktop 3P デプロイで強制**される（公式ページに年の記載は無い）。新しく作る Enterprise Admin Console の組織は最初から on
- 有効にすると、ホーム画面の入力欄から Chat / Cowork を選ばずに送れる。Cowork を起動できる端末では Cowork セッション、VM を起動できない端末では Chat の会話になる
- **Code は別のまま**（`isClaudeCodeForDesktopEnabled` が引き続き制御する）
- 有効化と設定キーは後述「[サードパーティ基盤 (3P) での管理](#サードパーティ基盤-3p-での管理)」を参照
- 出典: [Unified Claude in Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/unified-claude)

## ClaudeCode と挙動が異なる点（重要）

Desktop は CLI と同じ設定ファイルを読むが、**一部の挙動が異なる**。CLI の前提で書いた手順がそのまま通らない箇所を先に押さえる。

| 項目 | Desktop での挙動 |
|---|---|
| **`/config key=value`** | ⚠️ **Desktop の `/config` は `key=value` を無視する**（`/config theme=dark` が効かない）。この構文は **CLI 前提**である（[slash-commands.md](slash-commands.md) 参照） |
| **`desktopSessionCleanupPeriodDays`** | **Desktop / Cowork transcript 専用の保持期間**（v2.1.248〜、user または managed settings、`--settings` 可。project / local settings では無視）。**既定は `0` で年齢上限なし**（キーが無ければ Desktop / Cowork の transcript は何日経っても残る）。⚠️ **`cleanupPeriodDays` との AND 判定**なので、既定 30 日環境で `7` を入れても 30 日保持になる。managed settings が `cleanupPeriodDays` を設定している場合と、**HIPAA 構成が適用されたセッション**では `cleanupPeriodDays` で削除され、本キーは無視される（2026-10-11 追記: 既定値と HIPAA の条件） |
| **`sshHostAllowlist`** | managed settings のみで読まれ、**Desktop アプリだけが honor する**（CLI / IDE 拡張は読まない）。**Bash 経由の `ssh` は制限しない**点に注意 |
| **`disableBrowserExternalNavigation`** | **JSON boolean の `true` のみ有効**。文字列 `"true"` は無視される |
| **`MAX_THINKING_TOKENS=0`** | Anthropic API では local environment editor で `0` にすると thinking を OFF にできるが、**Opus 5.5 / Sonnet 5.5 / Haiku 5.5 / Fable 系は常に extended thinking を使うため効かない**。thinking OFF のとき、Opus 5 のように「thinking OFF と高い effort の組み合わせ」を受け付けないモデルには effort `high` を送る。adaptive reasoning モデルは正の値の数値部分を無視する。Opus 4.6 / Sonnet 4.6 は `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` で固定 budget 化できるが、Fable 系・Sonnet 5 以降・Haiku 5.5・Opus 4.7 以降には固定 budget モードが無い（**2026-10-11 訂正**: 以前は「Fable 5 では無効」とだけ書いていたが、現行公式で `0` が効かないのは 5.5 世代と Fable 系である） |
| **`.worktreeinclude`** | gitignore されたファイル（`.env` 等）を worktree にコピーする指定ができる |

出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop) / [Settings reference — desktopSessionCleanupPeriodDays](https://code.claude.com/docs/en/settings-reference#desktopsessioncleanupperioddays) / [Explore the .claude directory — Cleaned up automatically](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)

## 2026-w27〜w28 の新機能

### In-app browser (Week 28)

- Claude Desktop に**組み込みブラウザ**が搭載され、Claude が外部サイトを直接読み・クリック・操作できるようになった
- ブラウザは **sandboxed** で動作し、安全分類器レビューを経由する
- セッション永続化 (persist) は選択可能 (履歴・cookie を残すかどうかを個別に指定)
- 併せて公式が **MCP server 名として "Claude Browser" / "Claude Preview" を予約** (v2.1.205、[mcp-setup.md](mcp-setup.md) 参照)
- Desktop 3P では built-in browser は既定 off で、`builtinBrowserEnabled` などの管理キーで有効化・サイト制限する（後述「[サードパーティ基盤 (3P) での管理](#サードパーティ基盤-3p-での管理)」、2026-10-11 追記）
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop#browse-external-sites) / [whats-new week 28](https://code.claude.com/docs/en/whats-new/2026-w28)

### Claude Desktop on Linux beta (Week 27)

- **Ubuntu / Debian 向け beta 提供**開始。当初「Linux 未対応」だったが状況変化した (下記「保存場所」表の Linux 行を「beta 提供中」に読み替える)
- 出典: [whats-new — code.claude.com](https://code.claude.com/docs/en/whats-new)

## 2026-w30 の新機能

### iOS Simulator ペイン (macOS のみ)

- **macOS 版 Claude Code Desktop に iOS シミュレータのペイン**が追加された。iOS アプリを開発しながら、同じウィンドウ内でシミュレータ上の挙動を確認できる（操作できるのはシミュレータのデバイスだけで、実機の iPhone / iPad は操作できない）
- **Pro / Max / Team / Enterprise の public beta**。ただし **HIPAA 構成を有効にした Enterprise 組織では使えない**
- **local セッション専用**。cloud / SSH セッションでは Claude が動くマシンから手元の Mac のシミュレータに届かないため使えない
- 前提: **Xcode と iOS platform** がインストール済みであること（Xcode 26.x または 27 を推奨）、**Claude Desktop v1.24012.0 以上**
- managed setting の `disableMobileSimulatorTools` で Claude のシミュレータ操作ツールを止められる（ペイン自体はユーザーが操作できるまま残り、アプリ内から上書きできない）
- **2026-10-11 訂正**: 以前は W30 の発表どおり「Pro / Max / Team の public beta」と書いていたが、現行の公式ページは Enterprise も対象に含めている（HIPAA 構成の組織を除く）
- 出典: [whats-new week 30](https://code.claude.com/docs/en/whats-new/2026-w30) / [Test iOS apps in the simulator](https://code.claude.com/docs/en/desktop-ios-simulator)

## 2026-w33〜w37 の新機能

2026-10-11 追記。

| 機能 | 内容 | 週 |
|---|---|---|
| **Auto-continue when limits reset** | Code タブで session limit に達したときの上限カードに **Auto-continue when limits reset** のチェックボックスが出る。チェックしてセッションを開いたままにすると、リセット後に中断したターンを Desktop アプリが再試行する。カードには `Auto-resuming at` に続けてリセット時刻が出る。**weekly limit のカードには出ない** | W33 |
| **`/resume` で CLI セッションを取り込む** | Desktop の入力欄で `/resume` と打つと、この PC の CLI で始めたセッションを一覧でき、タイトル・フォルダ・ブランチで検索し、続きをプレビューしてから再開できる。コピーではなく同じセッションを続けるので、後から terminal の `claude --resume` でも見つかる。先に terminal 側のセッションを閉じておく。**local セッションのみ**で、SSH / WSL / cloud セッションでは使えない | W35 |
| **background computer use** | macOS では computer use がバックグラウンドで動き、ユーザーが作業を続ける間に Claude が承認済みのアプリを操作する。**Pro / Max の beta**（下記「[Computer use](#computer-use画面操作research-preview)」） | W36 |
| **pane を別ウィンドウに分離** | diff や terminal などの pane を独立したウィンドウに pop out し、終わったら元のウィンドウに dock し直せる。別画面に pane を置いたまま、Claude はメインウィンドウで作業を続ける | W37 |

出典: [whats-new week 33](https://code.claude.com/docs/en/whats-new/2026-w33) / [whats-new week 35](https://code.claude.com/docs/en/whats-new/2026-w35) / [whats-new week 36](https://code.claude.com/docs/en/whats-new/2026-w36) / [whats-new week 37](https://code.claude.com/docs/en/whats-new/2026-w37) / [Claude Desktop — Coming from the CLI](https://code.claude.com/docs/en/desktop#coming-from-the-cli) / [Claude Desktop — Arrange your workspace](https://code.claude.com/docs/en/desktop#arrange-your-workspace)

## 自社インフラでセッションを走らせる (Self-hosted environments)

> **Team / Enterprise 限定の public beta**。個人プラン (Pro / Max) では利用できないため、**本リポジトリの運用における優先度は低い**。概要のみ記録する。

`claude self-hosted-runner` (v2.1.224〜) で、**自社のマシン・コンテナを Claude Code の cloud session の実行先**にできる。cloud session は開発者のマシン以外で動くセッションの総称で、既定では Anthropic のインフラで動く（**2026-10-11 訂正**: 以前は「web / mobile / desktop セッションの実行先」と書いていたが、現行公式は対象を下表「対象 surface」の範囲に広げている）。

| 論点 | 内容 |
|---|---|
| 構成（現行の用語） | **Environment / Runner / Session の 3 部構成**として整理された（2026-09-03 更新）。公式 docs も 6 ページに分割（quickstart / deploy / configuration / testing / reference / identity） |
| モード | **自分で runner を常駐させる**（旧「fixed」）/ **autoscaling orchestrator を別プロセスで立てる**（旧「on-demand」） |
| 隔離 | ⚠️ **2026-09-03 訂正: 「セッションごとに独立した checkout」ではなく、runner が最初のセッションで 1 owner にロックされるモデル**である（`--drain-grace-sec` 既定 0 で、完了後は即 exit する） |
| **有効化ゲート** | **Owner が Cloud environments 管理画面で「Allow self-hosted environments」を有効化する必要があり、前提として Claude Code on the web が組織で有効**でなければならない |
| 対象 surface | claude.ai/code・mobile / desktop アプリ・scheduled routines・terminal の `claude --cloud` と `--environment` dispatch から始めたセッション。**Claude Security と Code Review のセッションはまだ回せない**（2026-10-11 追記） |
| Claude Tag との関係 | **Claude Tag セッションも実行できる。ただし admin が追加した connectors と Federated agent access はそのセッションで使えない**（2026-10-11 更新。以前は「Access bundles は使えない」と書いていた。[claude-tag.md](claude-tag.md) §6 参照） |
| 課金 | **Anthropic-hosted と同じく組織の Claude Code usage を消費する** |
| リポジトリ | **GitHub のみ** |
| 追加オプション | `--client-label` / `SELF_HOSTED_RUNNER_CLIENT_LABEL`（登録ラベル上書き。既定は hostname、v2.1.248）/ `--defer-shutdown-max-min <minutes>`（SIGTERM 後も指定分だけ attached session を配信し、残りを park して終了、v2.1.238）/ `--proxy-authorization-command` / `--proxy-authorization-file`（接続ごとに新規発行の `Proxy-Authorization` ヘッダを要求する egress proxy 向け、v2.1.238） |
| 目的 | **ソースとビルド成果物を自社インフラ内に留める** |
| 制約 | **ZDR 組織と HIPAA 構成を適用した組織は対象外** |
| 推論の送り先 | 既定は Anthropic API。**runner ごとに Amazon Bedrock / Google Cloud's Agent Platform へ送るよう設定できる**。その場合もセッション内容は Anthropic に送られ、その runner のセッションには server-managed settings と claude.ai の組織ポリシーが届かない（**2026-10-11 訂正**: 以前は「推論自体は Anthropic API 固定」と書いていたが、現行公式は Bedrock / Agent Platform への送信を設定できるとしている） |
| runner host の OS | **Linux / macOS**。**Windows は runner host としてサポート外**で、Linux コンテナで動かすよう案内されている（開発者の端末はブラウザから使うので影響しない、2026-10-11 追記） |
| Remote Control との違い | Remote Control は「個人マシンで継続する」もの。こちらは**組織が管理する共有基盤** |

v2.1.225 で `--base-dir` の作成に失敗した場合、起動時エラーとして扱われるようになった。

**v2.1.229 / v2.1.233 での変更**（2026-08-16 追記）:

| 変更 | 内容 | 版 |
|---|---|---|
| **server 供給 hook のサポート** | orchestrator 側が配布する hook を runner が受け取って実行できる | v2.1.229 |
| **Windows は `--base-dir` が必須** | Windows では既定の checkout ディレクトリを持たなくなり、明示指定が要る（CHANGELOG v2.1.233 時点の記述。**2026-10-11 追記**: 現行の公式 reference は Windows を「サポート外の runner host」と位置付けたうえで、既定値が無く flag か `SELF_HOSTED_RUNNER_BASE_DIR` が無ければ起動時に exit すると書いている。Windows で運用する前提にはしない） | v2.1.233 |
| **セッション開始の高速化** | branch 作成時に working tree を書き換えないよう変更された | v2.1.233 |
| **`managed-mcp.json` の起動失敗を緩和** | 配備された `managed-mcp.json` が原因で起動に失敗していたのを、**warning を出してスキップ**する挙動に変更 | v2.1.233 |

出典: [Self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments) / [Self-hosted environments quickstart](https://code.claude.com/docs/en/self-hosted-environments-quickstart) / [Self-hosted environments reference](https://code.claude.com/docs/en/self-hosted-environments-reference) / [Send model requests to Bedrock or Agent Platform](https://code.claude.com/docs/en/self-hosted-environments-configuration#send-model-requests-to-bedrock-or-agent-platform) / [Run Claude Code sessions on your own compute](https://claude.com/blog/run-claude-code-sessions-on-your-own-compute) / CHANGELOG v2.1.224 / v2.1.225 / v2.1.229 / v2.1.233

## 企業ネットワーク設定の扱い (v2.1.212 / v2.1.217)

Claude Desktop 上のセッションでは、**ClaudeCode で有効な企業ネットワーク設定の一部が適用されない**ケースがある。社内プロキシや mTLS を前提とした環境では注意する。

| バージョン | 内容 |
|---|---|
| **v2.1.212**（**2026-09-03 訂正済み。下記注記を参照**） | **hosted（host-managed）セッションでは、mTLS 証明書・追加 CA バンドル・OAuth scope の設定を「警告付きで無視する」**仕様が明示された。設定は書けるが効かない点に注意 |
| **v2.1.217** | **corporate mTLS / TLS-verify / OAuth scope / proxy の設定が Claude Desktop セッションで無視されていた不具合を修正**。v2.1.217 以降は（hosted セッションを除き）意図通り適用される |

- 出典: [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) v2.1.212 / v2.1.217
- ✅ **2026-09-03 訂正: 公式 `network-config` が正確な条件を明文化したため、CHANGELOG 依存は解消した。**
  - 正しくは「一律で警告付きに無視」ではなく **「読み取り scope の制限」**である。
  - **アプリが provider 接続を管理するセッション**（third-party provider 上の Code タブ、Cowork セッション）では、`CLAUDE_CODE_CLIENT_CERT` / `_KEY` / `_KEY_PASSPHRASE` / `NODE_EXTRA_CA_CERTS` / `NODE_TLS_REJECT_UNAUTHORIZED` / `CLAUDE_CODE_OAUTH_SCOPES` および `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` を **managed settings と `~/.claude/settings.json` からのみ読み、リポジトリ側の settings は無視する**。理由は「checkout したリポジトリが TLS / proxy 経路を書き換えられないようにするため」。
  - **claude.ai サインインの local / SSH / WSL Code タブは、アプリが接続を管理しないため全 scope から読む。**
  - cloud session では settings の `env` ブロック由来の上記変数を無視し、**無視した各キーを debug log に記録する**。
  - 出典: [Network configuration — mTLS authentication](https://code.claude.com/docs/en/network-config#mtls-authentication)
- （旧記述・履歴）⚠️ **出典の注意（2026-08-04 確認）**: 上表 v2.1.212 の「hosted セッションでは mTLS / CA バンドル / OAuth scope を警告付きで無視する」は **CHANGELOG v2.1.212 のみを根拠**としている。現行の公式 [Claude Desktop](https://code.claude.com/docs/en/desktop) ページ本文では同記述を確認できず、同ページは mTLS / 独自 CA / proxy を [Network configuration](https://code.claude.com/docs/en/network-config) へのリンクで扱う形に変わっている。**誤りとは断定できないが、企業ネットワーク前提の構築時は network-config ページ側で現行仕様を確認する**のが安全である。

## `claude_desktop_config.json`

- **目的**: Claude Desktop が接続する MCP サーバーの定義
- **内容**: MCP サーバーの起動コマンド、引数、環境変数
- **保存場所**（OS 別）:
  - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
  - **Linux**: **beta 提供中**（apt / `.deb`）。設定パスは `~/.config/Claude/claude_desktop_config.json` 相当（環境により異なるためアプリ内の設定画面から確認する）
- **スコープ**: ユーザーレベル（Claude Desktop 全体に適用）
- **Git 管理**: しない（個人環境固有のパス情報を含む）
- **備考**: 編集後は Claude Desktop の再起動が必要。パスは絶対パスで指定する
- **設定例**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    },
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

## ClaudeCode と Claude Desktop の MCP 設定の違い

| 項目 | ClaudeCode | Claude Desktop |
|------|-----------|----------------|
| MCP 設定ファイル | `.mcp.json`（project）/ `settings.json`（user/local） | `claude_desktop_config.json` |
| 設定方法 | `claude mcp add` コマンド or 手動編集 | 手動で JSON ファイルを編集、**または GUI の Connectors**（MCP サーバーの graphical setup。セッション中の追加も可） |
| スコープ | user / local / project の3段階 | **Chat タブは `claude_desktop_config.json` のみ。ただし Code タブ（local session）は `claude_desktop_config.json` に加えて `~/.claude.json` と `.mcp.json` も読む** |
| Git 共有 | `.mcp.json` は共有可能 | **Code タブでは `.mcp.json` が効くため共有可能** |
| 反映タイミング | 即座に反映 | アプリ再起動が必要 |

> ⚠️ **2026-09-03 訂正**: 上表のスコープ欄は以前「ユーザーレベルのみ」、Git 共有欄は「共有しない」と記載していたが、**Code タブについては誤り**だった。
>
> **Code タブの precedence は CLI と異なる 2 段仕様である**（ここが最も間違いやすい）:
>
> 1. 同名サーバーが `claude_desktop_config.json` と `~/.claude.json` / `.mcp.json` の両方にある場合 → **`claude_desktop_config.json` の定義を採用**する
> 2. `~/.claude.json`（user scope）と `.mcp.json` に同名の stdio サーバーがある場合 → **`~/.claude.json` を採用**する。**これは CLI の scope hierarchy から逸脱している**
>
> 逆方向として、**CLI は `claude_desktop_config.json` を読まない**。macOS / WSL では `claude mcp add-from-claude-desktop` で取り込む。
>
> 出典: [Claude Desktop — MCP servers from the Claude Desktop chat app](https://code.claude.com/docs/en/desktop#mcp-servers-from-the-claude-desktop-chat-app)

## Computer use（画面操作・research preview）

Claude が**実際のデスクトップでアプリを開き、画面を操作する**機能。

| 項目 | 内容 |
|---|---|
| 提供 | **macOS / Windows の research preview** |
| プラン | **Pro / Max 限定。Team / Enterprise は不可** |
| 既定 | **off** |
| macOS の前提 | **Accessibility + Screen Recording の付与**が必要 |
| ツール選択の優先順 | connector → Bash → Claude in Chrome → iOS Simulator → **computer use**（最後の手段） |
| per-app access tier | **ブラウザは view-only、ターミナル / IDE は click-only** に上限が掛かる |
| 承認 | セッション単位（Dispatch 由来のセッションは 30 分） |
| バックグラウンド実行 | **macOS ではバックグラウンドで動かせる**。ユーザーが作業を続ける間に、Claude が承認済みのアプリを操作する。**Pro / Max の beta**（W36、2026-10-11 追記）。バックグラウンドでないときは、承認したアプリだけを操作するために他のウィンドウを隠し、終了時に戻す（**Unhide apps when Claude finishes** 設定で切り替え） |
| Linux | **Linux beta の Desktop アプリでは computer use はまだ使えない**（2026-10-11 追記） |

⚠️ 公式は **sandboxed Bash とは信頼境界が異なる**旨を明示的に警告している。画面操作は sandbox の外でホスト UI を触るため、Bash の sandbox 設定では守れない。

出典: [Claude Desktop — Let Claude use your computer](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer) / [whats-new week 36](https://code.claude.com/docs/en/whats-new/2026-w36)

## Claude Projects（Code タブから使う並列 thread）

2026-10-11 追記。**Projects** は、1 つの会話に関連タスクを流し込むと coordinator 役の Claude がタスクごとに thread を立てて並列に進める機能である。thread は通常 1 つの cloud session で、手元のマシンにしか無いもの（ローカル DB や VPN の奥の API など）が要るときは Remote Control 経由で自分のマシン上の thread として動かせる。claude.ai/code・**Desktop の Code タブ**・Claude mobile アプリで作成・利用でき、Desktop では thread のエラーや入力待ちをデスクトップ通知で受け取れる。ローカル thread 用のフォルダは Desktop の **Settings > Claude Code** で **Use this computer from your phone and claude.ai** を on にして登録する（terminal で `claude remote-control` を動かしてもよい。どちらもそのマシンに Claude Code v2.1.280 以上が要る）。**Pro / Max の public beta で段階展開中**、Team / Enterprise では未提供。terminal CLI・VS Code 拡張・JetBrains plugin や Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry 経由では使えない。thread の既定モデル・effort、subagent / agent teams との違いなどは [claude-projects.md](claude-projects.md) にまとめる。

出典: [Projects](https://code.claude.com/docs/en/claude-projects)

## サードパーティ基盤 (3P) での管理

2026-10-11 追記。**Claude Desktop on 3P**（Desktop 3P）は、Code タブなどを Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry / self-hosted LLM gateway などの推論 provider 上で動かす形態である。設定は MDM・bootstrap server・アプリ内の configuration window などで配るか、Anthropic がホストする Enterprise Admin Console で一元管理する。

> 組織向けの管理機能であり、個人プラン (Pro / Max) で claude.ai にサインインして使う本リポジトリの運用では**優先度は低い**。新設された公式ページのキー名と出典だけを記録する。

| 論点 | キー / 設定場所 | 内容 | 出典 |
|---|---|---|---|
| **Enterprise Admin Console**（beta） | claude.ai の **Organization settings** の **Desktop 3P** 各ページ。Admin API（`read:desktop_config` / `write:desktop_config` scope）でも読み書きできる | Anthropic 担当者経由でプロビジョニングする。MDM / bootstrap と同じ設定キーを console で管理し、ユーザーは work account で一度サインインすれば設定をダウンロードして 3P モードで再起動する。prompts・responses は自社の推論 provider に送られ、Anthropic が持つのはユーザー一覧と保存した設定（usage analytics を on にすると token / session 数も）。provider の credentials は持たない。推論 provider に Claude API は選べない | [Enterprise Admin Console](https://claude.com/docs/third-party/claude-desktop/admin-console) |
| **Unified Claude**（beta） | MDM / bootstrap では `desktopHome` を `standard` にする（認識できない値は `off` 扱い、キーを消すと無効）。Admin Console では **Capabilities** の **Opt into the new Chat and Cowork unified view** | Chat と Cowork を統合する。11 月 10 日に全 Desktop 3P デプロイで強制（年は公式ページに記載なし）。有効時は `chatTabEnabled` / `chatAdvancedFileAnalysisEnabled` / `coworkTabEnabled` を無視し、新しい会話は Cowork の保持期間に従う。Code は `isClaudeCodeForDesktopEnabled` で別に制御する | [Unified Claude](https://claude.com/docs/third-party/claude-desktop/unified-claude) |
| **Built-in browser** | `builtinBrowserEnabled`（既定 off、変更は再起動後に反映）/ `builtinBrowserDefaultDomainPolicy`（未設定か `allow` なら `builtinBrowserBlockedDomains` 以外を開ける、`block` なら `builtinBrowserAllowedDomains` だけ）/ `coworkEgressAllowedHosts` | Cowork / Code セッションの Browser pane。サイト制限がかかるのは Claude で、ユーザーはブロック対象のサイトも開ける（Claude のツールはそのページで止まる）。`coworkEgressAllowedHosts` に host を並べると、ブラウザ側の許可より狭くなる。Anthropic の site safety check がブロックしたサイトは allow list に入れても開けない。**Claude in Chrome は Admin Console で管理する組織だけ**が使える | [Built-in browser and Claude in Chrome](https://claude.com/docs/third-party/claude-desktop/browser) |
| **managed MCP のサインイン** | `managedMcpServers` の各エントリの `oauth` キー（Admin Console では **Connectors** ページ） | **OAuth** 設定は **None** / **Auto-register (dynamic client registration)** / **Bring your own client** / **Anthropic-hosted client identity**（claude.ai サインインが要る）の 4 択。Bring your own client の redirect URI は `http://127.0.0.1:53280/callback`。client secret を console に保存できるのは Google の Desktop-app 型 client（`GOCSPX-` で始まる）だけで、それ以外は各端末の同じ絶対パスに置いた **client secret helper script** が `{"clientSecret": "…"}` を出力し、30 秒以内に終了コード 0 で終わる必要がある | [Set up sign-in for managed MCP servers](https://claude.com/docs/third-party/claude-desktop/mcp-sign-in) |
| **Box / Google Cloud / Salesforce の接続例** | `managedMcpServers`（Salesforce は加えて `allowedPluginMarketplaces`） | Box は Box 管理者が作る OAuth client を使い、Admin Console では secret を各端末の helper script で渡す（MDM / bootstrap ではエントリに secret を直接書ける）。Google Cloud の remote MCP は dynamic client registration 非対応で、Desktop-app 型 OAuth client の client ID と `GOCSPX-` secret を使う（BigQuery の例では各ユーザーに `roles/mcp.toolUser`）。Salesforce は partner marketplace の plugin と hosted MCP を組み合わせ、PKCE 必須の client なので secret は不要 | [Box](https://claude.com/docs/third-party/claude-desktop/connectors-box) / [Google Cloud](https://claude.com/docs/third-party/claude-desktop/connectors-google-cloud) / [Salesforce](https://claude.com/docs/third-party/claude-desktop/connectors-salesforce) |
| **モデルと effort** | `inferenceModels`（先頭が既定モデル）と各エントリの `maxEffort` / `defaultModelEffort` / `alwaysStartWithDefaultModel` | `maxEffort`（`low` / `medium` / `high` / `xhigh` / `max`）は Chat / Cowork / Code で選べる effort の上限で、**Code セッションでは `CLAUDE_CODE_EFFORT_LEVEL` や `/effort` も上限で抑える**。認識できない値は `low` に cap される。`inferenceModels` を省くと、対応 provider では model discovery が picker を埋める | [Models and effort levels](https://claude.com/docs/third-party/claude-desktop/models) |

## Cowork の HIPAA 設定（Enterprise）

2026-10-11 追記。HIPAA 構成は、PHI を扱い Anthropic と BAA を結んだ **Claude Enterprise** 組織の organization setting で、Claude Code（local mode）と Cowork（local mode）に適用される。Claude Desktop の Code タブも local mode に含まれる。**Desktop 3P には適用されない**。Claude Code 側の設定は [config-files.md の HIPAA 構成](config-files.md#hipaa-構成claude-code-local-mode) を参照する。

| 項目 | 内容 |
|---|---|
| 必要バージョン | **Claude Desktop v2.19675.0 以上**。最低版は随時引き上げられ、古い版では **Update required** ダイアログが出てリクエストが拒否される |
| 適用直後 | Cowork は Owner が再び on にするまで off になる |
| `forceLoginOrgUUID` | 組織 ID を入れる。他組織のアカウントはサインインできない。ID として読めない値を入れると、その端末では誰もアプリを使えなくなる |
| `isLocalDevMcpEnabled: false` | chat / Cowork にローカル MCP サーバーを追加できなくなる。plugin が持ち込むローカル MCP サーバーも読み込まれない |
| `isDesktopExtensionEnabled: false` | desktop extension の読み込みと新規インストールを止める |
| `otlpContentCapture: []` | Cowork の monitoring イベントを metadata のみにする。**空文字は未設定扱い**になり、prompt や応答が載りうる |
| `requireCoworkFullVmSandbox` | `true` にすると Claude Code は Cowork の VM 内で動き、`cleanupPeriodDays` 以外の Claude Code managed settings が Cowork に効かなくなる。managed settings に頼るなら設定しない |
| `disabledBuiltinTools` | `["WebSearch"]` で Cowork と Code タブの web search を止める。リストとして読めない値だと **全 built-in tool が止まる** |
| ネットワーク | Cowork の shell は VM で動く。到達先を絞るには Owner が **Organization settings > Capabilities** の **Allow network egress** を off にする |
| 確認 | タイトルバー（Mac はサイドバー）とアカウントメニューに **HIPAA configured** ラベルが出る |

HIPAA 構成の組織では iOS Simulator ペインと self-hosted environments が使えず、`desktopSessionCleanupPeriodDays` も無視される（各節を参照）。

出典: [Set up Cowork (local mode) for a HIPAA-ready organization](https://claude.com/docs/cowork/hipaa-setup)

## 全設定ファイル対応表（ClaudeCode + Claude Desktop）

| ファイル | 対象アプリ | 保存場所 | 主な用途 | Git 管理 | ユーザー編集 |
|----------|-----------|----------|----------|----------|-------------|
| `~/.claude.json` | ClaudeCode | `~/` | 内部状態・認証情報 | しない | しない |
| `~/.claude/settings.json` | ClaudeCode | `~/.claude/` | 全プロジェクト共通の個人設定 | しない | **する** |
| `~/.claude/keybindings.json` | ClaudeCode | `~/.claude/` | キーボードショートカット | しない | **する** |
| `.claude/settings.json` | ClaudeCode | プロジェクトルート | チーム共有のプロジェクト設定 | **する** | **する** |
| `.claude/settings.local.json` | ClaudeCode | プロジェクトルート | プロジェクト設定の個人オーバーライド | しない | **する** |
| `.mcp.json` | ClaudeCode | プロジェクトルート | MCP サーバーのチーム共有設定 | **する** | **する** |
| `claude_desktop_config.json` | Claude Desktop | OS 固有パス※ | MCP サーバー設定 | しない | **する** |

> ※ macOS: `~/Library/Application Support/Claude/`、Windows: `%APPDATA%\Claude\`
