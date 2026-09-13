# Claude Desktop の設定ファイル

> 出典: [MCP Quickstart](https://modelcontextprotocol.io/quickstart) / [DeepWiki - modelcontextprotocol/docs](https://deepwiki.com/modelcontextprotocol/docs) / [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop) / [Self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments) / [whats-new week 30](https://code.claude.com/docs/en/whats-new/2026-w30) / [Network configuration](https://code.claude.com/docs/en/network-config) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-09-03時点。CHANGELOG は v2.1.258 まで反映)

Claude Desktop は ClaudeCode とは別のデスクトップアプリケーションであり、独自の設定ファイルを持つ。MCP サーバーの設定方法が ClaudeCode とは異なるため、混同しないよう整理する。

## アプリの構成（3 タブ）と提供プラットフォーム

Claude Desktop は **Chat / Cowork / Code の 3 タブ**構成である。このうち **Code タブが Claude Code 相当**の機能を提供する（本ドキュメントで「Claude Desktop 上のセッション」と書いているのは Code タブのセッションを指す）。

- **macOS / Windows** に加えて **Linux beta**（apt / `.deb`）が提供されている
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop)

## ClaudeCode と挙動が異なる点（重要）

Desktop は CLI と同じ設定ファイルを読むが、**一部の挙動が異なる**。CLI の前提で書いた手順がそのまま通らない箇所を先に押さえる。

| 項目 | Desktop での挙動 |
|---|---|
| **`/config key=value`** | ⚠️ **Desktop の `/config` は `key=value` を無視する**（`/config theme=dark` が効かない）。この構文は **CLI 前提**である（[slash-commands.md](slash-commands.md) 参照） |
| **`desktopSessionCleanupPeriodDays`** | **Desktop / Cowork transcript 専用の保持期間**（v2.1.248〜、user または managed settings、`--settings` 可）。⚠️ **`cleanupPeriodDays` との AND 判定**なので、既定 30 日環境で `7` を入れても 30 日保持になる。managed settings が `cleanupPeriodDays` を設定している場合は本キーは無視される |
| **`sshHostAllowlist`** | managed settings のみで読まれ、**Desktop アプリだけが honor する**（CLI / IDE 拡張は読まない）。**Bash 経由の `ssh` は制限しない**点に注意 |
| **`disableBrowserExternalNavigation`** | **JSON boolean の `true` のみ有効**。文字列 `"true"` は無視される |
| **`MAX_THINKING_TOKENS=0`** | モデル世代で挙動が分岐する。Fable 5 では無効、adaptive reasoning モデルは 0 以外の値を無視、Opus 4.6 / Sonnet 4.6 は `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` で固定 budget 化できる |
| **`.worktreeinclude`** | gitignore されたファイル（`.env` 等）を worktree にコピーする指定ができる |

出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop)

## 2026-w27〜w28 の新機能

### In-app browser (Week 28)

- Claude Desktop に**組み込みブラウザ**が搭載され、Claude が外部サイトを直接読み・クリック・操作できるようになった
- ブラウザは **sandboxed** で動作し、安全分類器レビューを経由する
- セッション永続化 (persist) は選択可能 (履歴・cookie を残すかどうかを個別に指定)
- 併せて公式が **MCP server 名として "Claude Browser" / "Claude Preview" を予約** (v2.1.205、[mcp-setup.md](mcp-setup.md) 参照)
- 出典: [Claude Desktop — code.claude.com](https://code.claude.com/docs/en/desktop#browse-external-sites) / [whats-new week 28](https://code.claude.com/docs/en/whats-new/2026-w28)

### Claude Desktop on Linux beta (Week 27)

- **Ubuntu / Debian 向け beta 提供**開始。当初「Linux 未対応」だったが状況変化した (下記「保存場所」表の Linux 行を「beta 提供中」に読み替える)
- 出典: [whats-new — code.claude.com](https://code.claude.com/docs/en/whats-new)

## 2026-w30 の新機能

### iOS Simulator ペイン (macOS のみ)

- **macOS 版 Claude Code Desktop に iOS シミュレータのペイン**が追加された。iOS アプリを開発しながら、同じウィンドウ内で実機挙動を確認できる
- **Pro / Max / Team の public beta**
- 前提: **Xcode** がインストール済みであること、**Claude Code Desktop v1.24012.0 以上**
- 出典: [whats-new week 30](https://code.claude.com/docs/en/whats-new/2026-w30) / [iOS Simulator — code.claude.com](https://code.claude.com/docs/en/desktop-ios-simulator)

## 自社インフラでセッションを走らせる (Self-hosted environments)

> **Team / Enterprise 限定の public beta**。個人プラン (Pro / Max) では利用できないため、**本リポジトリの運用における優先度は低い**。概要のみ記録する。

`claude self-hosted-runner` (v2.1.224〜) で、**自社のマシン・コンテナを Claude Code の web / mobile / desktop セッションの実行先**にできる。

| 論点 | 内容 |
|---|---|
| 構成（現行の用語） | **Environment / Runner / Session の 3 部構成**として整理された（2026-09-03 更新）。公式 docs も 6 ページに分割（quickstart / deploy / configuration / testing / reference / identity） |
| モード | **自分で runner を常駐させる**（旧「fixed」）/ **autoscaling orchestrator を別プロセスで立てる**（旧「on-demand」） |
| 隔離 | ⚠️ **2026-09-03 訂正: 「セッションごとに独立した checkout」ではなく、runner が最初のセッションで 1 owner にロックされるモデル**である（`--drain-grace-sec` 既定 0 で、完了後は即 exit する） |
| **有効化ゲート** | **Owner が Cloud environments 管理画面で「Allow self-hosted environments」を有効化する必要があり、前提として Claude Code on the web が組織で有効**でなければならない |
| Claude Tag との関係 | **Claude Tag セッションも実行できる。ただし Access bundles は使えない** |
| 課金 | **Anthropic-hosted と同じく組織の Claude Code usage を消費する** |
| リポジトリ | **GitHub のみ** |
| 追加オプション | `--client-label` / `SELF_HOSTED_RUNNER_CLIENT_LABEL`（登録ラベル上書き。既定は hostname、v2.1.248）/ `--defer-shutdown-max-min <minutes>`（SIGTERM 後も指定分だけ attached session を配信し、残りを park して終了、v2.1.238）/ `--proxy-authorization-command` / `--proxy-authorization-file`（接続ごとに新規発行の `Proxy-Authorization` ヘッダを要求する egress proxy 向け、v2.1.238） |
| 目的 | **ソースとビルド成果物を自社インフラ内に留める** |
| 制約 | **ZDR 組織は対象外**。推論自体は Anthropic API 固定 |
| Remote Control との違い | Remote Control は「個人マシンで継続する」もの。こちらは**組織が管理する共有基盤** |

v2.1.225 で `--base-dir` の作成に失敗した場合、起動時エラーとして扱われるようになった。

**v2.1.229 / v2.1.233 での変更**（2026-08-16 追記）:

| 変更 | 内容 | 版 |
|---|---|---|
| **server 供給 hook のサポート** | orchestrator 側が配布する hook を runner が受け取って実行できる | v2.1.229 |
| **Windows は `--base-dir` が必須** | Windows では既定の checkout ディレクトリを持たなくなり、明示指定が要る | v2.1.233 |
| **セッション開始の高速化** | branch 作成時に working tree を書き換えないよう変更された | v2.1.233 |
| **`managed-mcp.json` の起動失敗を緩和** | 配備された `managed-mcp.json` が原因で起動に失敗していたのを、**warning を出してスキップ**する挙動に変更 | v2.1.233 |

出典: [Self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments) / [Run Claude Code sessions on your own compute](https://claude.com/blog/run-claude-code-sessions-on-your-own-compute) / CHANGELOG v2.1.224 / v2.1.225 / v2.1.229 / v2.1.233

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

⚠️ 公式は **sandboxed Bash とは信頼境界が異なる**旨を明示的に警告している。画面操作は sandbox の外でホスト UI を触るため、Bash の sandbox 設定では守れない。

出典: [Claude Desktop — Let Claude use your computer](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)

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
