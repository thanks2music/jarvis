# ClaudeCode Plugins ガイド

> 出典: [Create plugins](https://code.claude.com/docs/en/plugins) / [Plugins reference](https://code.claude.com/docs/en/plugins-reference) / [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) / [Create and distribute marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [Security guidance](https://code.claude.com/docs/en/security-guidance) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-08-04時点。公式 plugins ページの再取得は 2026-08-04、CHANGELOG は v2.1.221 まで反映)

Plugins は ClaudeCode の拡張機能をパッケージングし、配布するための仕組みである。Skills・Hooks・Subagents・MCP サーバーを**一つのインストール可能なユニット**にまとめ、リポジトリ間やチーム間で再利用できる。v2.0.12 で導入された。

---

## 前提知識

### Plugins と他の拡張機能の関係

Plugins は「パッケージングレイヤー」であり、個々の拡張機能を束ねるコンテナである。

| 拡張機能 | 単体での役割 | Plugin 内での役割 |
|---------|-------------|-----------------|
| Skills | ドメイン知識・ワークフロー | Plugin にバンドルして配布 |
| Hooks | イベント駆動の自動化 | Plugin 固有のフック定義 |
| Subagents | 隔離されたタスク実行 | Plugin 専用のエージェント定義 |
| MCP サーバー | 外部サービス接続 | Plugin と一緒にインストール |

**Plugin なしでもこれらは個別に使える**。Plugin が必要になるのは、複数のリポジトリで同じセットアップを再利用したい場合や、チーム・コミュニティに配布したい場合である。

### Skills との違い

| 比較軸 | Skill | Plugin |
|--------|-------|--------|
| 粒度 | 単一の指示・ワークフロー | Skills + Hooks + Agents + MCP のバンドル |
| 配置 | `~/.claude/skills/` or `.claude/skills/` | マーケットプレイス経由 or ローカルディレクトリ |
| 名前空間 | なし（同名は優先順位で解決） | `plugin-name:skill-name` で名前空間が分離 |
| インストール | ファイル配置のみ | `/plugin install` コマンド |
| 配布 | Git リポジトリに含める | マーケットプレイスで配布 |

---

## Plugin のディレクトリ構造

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # メタデータ（必須）
├── commands/                 # スラッシュコマンド（*.md）
├── agents/                   # 専用エージェント（*.md）
├── skills/                   # Skills（SKILL.md を含むディレクトリ）
│   └── my-skill/
│       └── SKILL.md
├── hooks/                    # イベントハンドラ
│   └── hooks.json
├── .mcp.json                 # MCP サーバー設定
├── .lsp.json                 # LSP サーバー設定（コードインテリジェンス）
├── monitors/                 # バックグラウンド監視（monitors.json、experimental）
├── bin/                      # PATH に追加される実行ファイル
├── settings.json             # plugin 設定（`agent` / `subagentStatusLine` のみ対応）
└── README.md                 # ドキュメント
```

> **配布・ロードの追加手段**: プラグインは `.zip` でも配布できる（`--plugin-dir <zip>`、v2.1.128〜）。URL からの直接ロードは `--plugin-url`。Anthropic 公式の community marketplace の名称は `anthropics/claude-plugins-community`（公式 marketplace は `claude-plugins-official`）。

`.claude-plugin/plugin.json` のみ必須で、他のコンポーネントはすべてオプション。必要な機能だけを含めればよい。

---

## plugin.json リファレンス

`plugin.json` は Plugin のマニフェストファイルであり、メタデータとコンポーネントの場所を定義する。

### 基本構成

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "プラグインの説明",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  }
}
```

### フィールド一覧

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | Yes | Plugin 名。マーケットプレイス内で一意。名前空間・ルックアップに使う |
| `displayName` | string | No | `/plugin` ピッカー等の UI に表示する人間向け名称（スペース・大文字可）。省略時は `name`。**v2.1.143 以降** |
| `version` | string | No | セマンティックバージョニング（例: `1.2.0`） |
| `description` | string | No | Plugin の概要説明 |
| `author` | object | No | `name`、`email`、`url` を含む作者情報 |
| `homepage` | string | No | ドキュメントの URL |
| `repository` | string | No | ソースコードリポジトリの URL |
| `license` | string | No | ライセンス（例: `MIT`） |
| `keywords` | string[] | No | 検索用キーワード |
| `commands` | string/string[] | No | コマンドファイル or ディレクトリのパス |
| `agents` | string/string[] | No | エージェントファイル or ディレクトリのパス |
| `skills` | string | No | Skills ディレクトリのパス |
| `hooks` | string/object | No | Hooks 設定ファイルのパス or インライン定義 |
| `mcpServers` | string/object | No | MCP 設定ファイルのパス or インライン定義 |
| `outputStyles` | string | No | 出力スタイルのディレクトリパス |
| `lspServers` | string/array/object | No | LSP サーバー（コードインテリジェンス）設定 |
| `experimental.monitors` | string/array | No | バックグラウンド監視（Monitor）設定。プラグイン有効時に自動起動。**v2.1.105 以降**（experimental） |
| `dependencies` | array | No | このプラグインが要求する他プラグイン（semver 制約付き可）。例: `[{ "name": "secrets-vault", "version": "~2.1.0" }]` |
| `defaultEnabled` | boolean | No | ユーザー未設定時に有効状態で開始するか。既定 `true`。`false` で「インストール時は無効」配布が可能。**v2.1.154 以降**（旧版は無視して有効化） |
| `strict` | boolean | No | strict モードの有効化 |

> **永続データディレクトリ `${CLAUDE_PLUGIN_DATA}`**: プラグイン更新を跨いで残る永続ディレクトリ。`~/.claude/plugins/data/{id}/`（`{id}` はプラグイン識別子、英数 `_-` 以外は `-` に置換）に解決される。`node_modules` や生成物・キャッシュの保存に使う。初回参照時に自動生成される。

### 高度な構成例

```json
{
  "name": "enterprise-tools",
  "version": "2.1.0",
  "description": "Enterprise workflow automation tools",
  "author": {
    "name": "Enterprise Team",
    "email": "enterprise@example.com"
  },
  "homepage": "https://docs.example.com/plugins/enterprise-tools",
  "repository": "https://github.com/company/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "workflow", "automation"],
  "commands": [
    "./commands/core/",
    "./commands/enterprise/",
    "./commands/experimental/preview.md"
  ],
  "agents": [
    "./agents/security-reviewer.md",
    "./agents/compliance-checker.md"
  ],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
          }
        ]
      }
    ]
  },
  "mcpServers": {
    "enterprise-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  }
}
```

### `${CLAUDE_PLUGIN_ROOT}` 変数

Plugin 内のスクリプトやファイルを参照する際は `${CLAUDE_PLUGIN_ROOT}` を使用する。これは Plugin のルートディレクトリに展開される。絶対パスをハードコードせず、ポータブルな参照が可能になる。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

---

## Plugin のコンポーネント

### Skills の追加

Plugin 内の Skills は `plugin-name:skill-name` の名前空間を持つ。他の Plugin や個人 Skills と競合しない。

```
my-plugin/
└── skills/
    └── review/
        └── SKILL.md
```

呼び出し: `/my-plugin:review`

Skills の書き方は [Skills ガイド](skills.md) を参照。

### Hooks の追加

Plugin 固有の Hooks を `hooks` フィールドで定義する。すべてのレベルの Hooks はマージされ、対応するイベントで発火する。

**外部ファイル参照**:
```json
{
  "hooks": "./hooks/hooks.json"
}
```

**インライン定義**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh"
          }
        ]
      }
    ]
  }
}
```

### Agents の追加

Plugin 専用のサブエージェントをマークダウンファイルで定義する。

```
my-plugin/
└── agents/
    ├── security-reviewer.md
    └── compliance-checker.md
```

### MCP サーバーの追加

Plugin に MCP サーバーをバンドルする。

**外部ファイル参照**（`.mcp.json`）:
```json
{
  "mcpServers": {
    "plugin-api": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/api-server.js"]
    }
  }
}
```

**plugin.json にインライン定義**:
```json
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

---

## Plugin のインストールと管理

### インストール

```bash
# マーケットプレイスからインストール（user スコープ、デフォルト）
/plugin install formatter@my-marketplace

# project スコープ（チーム共有、.claude/settings.json に追加）
/plugin install formatter@my-marketplace --scope project

# local スコープ（個人のみ、.claude/settings.local.json に追加）
/plugin install formatter@my-marketplace --scope local
```

| スコープ | 保存先 | 用途 | Git 共有 |
|---------|--------|------|----------|
| `user`（デフォルト） | `~/.claude/settings.json` | 全プロジェクト共通 | しない |
| `project` | `.claude/settings.json` | チーム全員で共有 | **する** |
| `local` | `.claude/settings.local.json` | 現在のプロジェクトのみ | しない |

### 対話的インストール

`/plugin` コマンドで対話的な UI を開き、**Discover** タブからマーケットプレイスのプラグインを閲覧・インストールできる。スコープの選択も UI 上で行える。**v2.1.186 で Installed タブに "Skills" セクションが追加**され、プラグインが提供する Skill を UI から個別確認できるようになった。

### ローカル開発用の読み込み

開発中の Plugin はディレクトリ指定で直接読み込める:

```bash
claude --plugin-dir /path/to/my-plugin
```

### 管理コマンド

```bash
/plugin                                    # 対話的 UI を開く
/plugin install <name>@<marketplace>       # インストール
/plugin uninstall <name>@<marketplace>     # アンインストール
/plugin disable <name>@<marketplace>       # 一時的に無効化
/plugin enable <name>@<marketplace>        # 再有効化
/plugin list                               # インストール済み一覧（--enabled / --disabled フィルタ可、v2.1.163〜）
/reload-plugins                            # 変更を即時反映（再起動不要）
```

CLI からの操作も用意されている。

```bash
claude plugin init <name>                  # 新規 Plugin の雛形を生成（v2.1.157〜）
claude plugin list                         # インストール済み Plugin の一覧
```

**`.claude/skills` 自動ロード（v2.1.157〜）**: `.claude/skills/` ディレクトリ配下に置いた Plugin は、marketplace を経由せずに**自動ロード**される。手元で素早く Plugin を試す場合に便利である（`--plugin-dir` 起動と並ぶ開発手段）。**単一 skill のみを持つ Plugin なら `SKILL.md` を root に置くだけで自動検出される**(v2.1.142+、`"skills": ["./"]` の明示指定不要。frontmatter の `name` が invocation 名になる)。

#### `@skills-dir` — marketplace も install も不要な開発フロー

**`claude plugin init my-tool`** は `~/.claude/skills/my-tool/` に `.claude-plugin/plugin.json` と starter `SKILL.md` を生成する。この plugin は次のセッションから **`my-tool@skills-dir`** として**自動ロード**され、**marketplace 登録も `/plugin install` も不要**である。

```bash
claude plugin init my-tool     # ~/.claude/skills/my-tool/ に雛形を生成
# → 次セッションで my-tool@skills-dir として自動ロードされる
```

- `--plugin-dir` を毎回渡す必要がなくなるため、**自作 skill / plugin を日常的に育てる運用に向く**
- **`claude-plugins-official` は初回の対話起動時に自動登録される**。非対話起動が先だった場合や marketplace policy でブロックされた場合は、`claude plugin marketplace add anthropics/claude-plugins-official` を手動実行する
- plugin ルートの `settings.json` は **`plugin.json` 内の `settings` より優先**され、未知のキーは silent ignore される

> **本リポジトリの運用との関係**: BOSS の skills / plugins は avengers リポジトリで実体管理し `~/.claude/skills/` へ symlink する方式を採っている。`@skills-dir` は**この配置とそのまま噛み合う**（`~/.claude/skills/<name>/` に `.claude-plugin/plugin.json` があれば plugin として認識される）ため、marketplace を用意せずに plugin 化する選択肢になる。

出典: [Create plugins](https://code.claude.com/docs/en/plugins)

**Marketplace の rename 自動追従**(v2.1.193): `marketplace.json` に `renames` map を設定すると、プラグインをリネームしても既存インストールが自動で settings 更新される。配布側の破壊的変更を利用者に手作業させずに済む。

**`claude plugin validate` の対象拡張**(v2.1.196): `.` を source とするローカルプラグインも validate 対象になった。CI での事前チェックに使いやすい。**v2.1.221 では名前の検証警告が追加**され、marketplace 名 / plugin 名が **Claude Desktop の managed marketplace sync で拒否される形式**である場合に警告が出るようになった（配布前に気付ける）。

**org 配布 skill の名前衝突バグ修正**(v2.1.221): plugin / 組織配布の skill が `/help` `/feedback` 等の**ターミナル専用組込コマンドと同名**の場合、**非対話セッションで起動できない**不具合が修正された。

**アンインストールの挙動**: `/plugin uninstall` は project スコープの場合、`.claude/settings.json` を直接変更せず `.claude/settings.local.json` で無効化する。チームメイトに影響しない。

`--keep-data` オプションで Plugin の永続データを保持したままアンインストールできる:

```bash
/plugin uninstall formatter@my-marketplace --scope project --keep-data
```

---

## アップデートの仕組み

> 出典: [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) / [Plugins reference](https://code.claude.com/docs/en/plugins-reference) (2026-04-30 時点)

ClaudeCode の Plugin は **デフォルトで自動アップデート + 手動コマンド併用** の設計である。インストール後に放置していても、無効化フラグを設定していなければ起動時のバックグラウンド処理で最新版に追従する。

### 自動アップデート

ClaudeCode 起動時にバックグラウンドで実行される。各 marketplace の `autoUpdate: true` 設定が有効化のトリガーになる。Seed-managed marketplace（企業配布の read-only マーケットプレース）は対象外。

#### 自動更新を制御する設定・環境変数

自動更新の制御は **marketplace 単位の `autoUpdate` 設定**（後述）が基本である。環境変数では以下が現行公式で確認できる。

| 設定・環境変数 | 効果 |
|---------|------|
| marketplace の `autoUpdate: false` | その marketplace の自動更新を無効化（後述の `extraKnownMarketplaces`） |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | 非必須トラフィックを一括停止。`DISABLE_AUTOUPDATER` 等を同時に有効化する束ねフラグ |
| seed-managed marketplace | read-only のため auto-update 対象外（git pull できない） |
| プライベート marketplace の `GITHUB_TOKEN` / `GH_TOKEN`（GitLab は `GITLAB_TOKEN` / `GL_TOKEN`） | 認証が必要なプライベート marketplace を起動時バックグラウンドで自動更新するために設定 |

> **訂正（2026-05-30 確認）**: 旧版の本表は `DISABLE_AUTOUPDATER` / `DISABLE_UPDATES` / `FORCE_AUTOUPDATE_PLUGINS` の 3 変数を単独で記載していたが、現行公式（[env-vars](https://code.claude.com/docs/en/env-vars) / [plugins-reference](https://code.claude.com/docs/en/plugins-reference) / [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)）では **`DISABLE_UPDATES` と `FORCE_AUTOUPDATE_PLUGINS` の単独エントリは確認できない**。`DISABLE_AUTOUPDATER` も独立エントリではなく `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` バンドルの構成要素としてのみ言及されている。憶測を避けるため、現行で裏が取れる事実に置き換えた。

#### Marketplace 単位の autoUpdate 設定

`~/.claude/settings.json` の `extraKnownMarketplaces` で marketplace ごとに切り替える。

```json
{
  "extraKnownMarketplaces": {
    "anthropic-agent-skills": {
      "source": { "source": "github", "repo": "anthropics/skills" },
      "autoUpdate": true
    }
  }
}
```

`source` が `directory`（ローカルディレクトリ）のマーケットプレースは remote から pull する概念がないため `autoUpdate` 設定は適用外となる。ファイル変更はそのまま即時反映される。プライベートリポジトリの marketplace を自動更新したい場合は、認証トークン（`GITHUB_TOKEN` / `GH_TOKEN` / `GITLAB_TOKEN` / `GL_TOKEN` 等）を環境変数として設定する必要がある。

### 手動アップデート

| コマンド | 役割 |
|---------|------|
| `/plugin marketplace update [name]` | マーケットプレースのカタログ（プラグイン一覧・バージョン情報）を refresh |
| `/plugin update <plugin>` | 特定プラグインを最新版へ更新 |
| `/plugin update` | 全プラグインを更新 |
| `/reload-plugins` | セッション再起動なしで変更を反映（不足依存も auto-install） |

「カタログの更新（marketplace update）」と「プラグイン本体の更新（plugin update）」は **別操作** である。`/plugin marketplace update` だけでは個別プラグインのバージョンは上がらない点に注意する。

### バージョン解決とキャッシュキー

ClaudeCode はプラグインのバージョンを cache key として扱い、**現在のバージョンと一致すれば更新をスキップ** する。バージョンの解決順は以下の通り。

1. `plugin.json` の `version` フィールド
2. marketplace エントリの `version` フィールド
3. プラグインの git commit SHA（`github` / `url` / `git-subdir` / 相対パス）
4. `unknown`（npm source、または git 管理外のローカルディレクトリ）

#### よくある落とし穴

> If you set `version` in `plugin.json`, you must bump it every time you want users to receive changes. Pushing new commits alone is not enough, because Claude Code sees the same version string and keeps the cached copy.
> — [Plugins reference](https://code.claude.com/docs/en/plugins-reference)

**自動更新が有効でも、プラグイン作者が `plugin.json` の `version` を bump していない場合、新しい commit を push しても更新は走らない**。`/plugin update` を実行して `"already at the latest version"` が返るのに作者リポジトリの commit log に変更がある場合は、このケースに該当する可能性が高い。

### 自動更新が有効か確認する方法

#### 方法 A: `/plugin` 対話 UI

```
/plugin
```

各 marketplace の auto-update トグル状態と、各プラグインのバージョンを UI で確認できる。

#### 方法 B: 設定ファイルを直接確認

```bash
cat ~/.claude/settings.json | jq '.extraKnownMarketplaces, .env'
```

確認ポイント:

- `extraKnownMarketplaces[*].autoUpdate` が `true` になっているか
- `env` に `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`（`DISABLE_AUTOUPDATER` を束ねるフラグ）が含まれていないか
- シェル環境変数にも同じフラグが無いか（`env | grep -E "DISABLE_AUTOUPDATER|NONESSENTIAL"`）

#### 方法 C: 環境診断

```
/doctor
```

設定の異常を検出する。`DISABLE_*` 系が意図せず有効になっていれば警告が出る。

### 長期間ぶりに最新化する場合の推奨手順

```
/plugin marketplace update          # 全 marketplace のカタログ更新
/plugin update                      # 全プラグインを最新版へ
/reload-plugins                     # 反映（再起動不要）
```

その後 `/plugin` で各プラグインのバージョンを確認すると、長期間更新されていないプラグインを特定できる。

---

## マーケットプレイス

マーケットプレイスは Plugin のカタログであり、Git リポジトリとしてホストする。

### マーケットプレイスの構造

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # マーケットプレイスのカタログ
└── plugins/
    ├── plugin-a/
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── skills/
    │   └── README.md
    └── plugin-b/
        ├── .claude-plugin/
        │   └── plugin.json
        └── ...
```

### marketplace.json

```json
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "Automatic code formatting on save",
      "version": "2.1.0",
      "author": {
        "name": "DevTools Team"
      },
      "category": "development"
    },
    {
      "name": "deployment-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin"
      },
      "description": "Deployment automation tools"
    }
  ]
}
```

`source` は以下のタイプが指定できる:
- **ローカルパス**: `"./plugins/formatter"` — 同一リポジトリ内のディレクトリ
- **GitHub リポジトリ**: `{"source": "github", "repo": "owner/repo"}` — 外部リポジトリ
- **`git-subdir`**: `{"source": "git-subdir", ...}` — Git リポジトリの一部だけを sparse clone する
- **`npm`**: `{"source": "npm", "package": "<pkg>", "version": "<ver?>", "registry": "<url?>"}` — npm レジストリから取得

`category` は任意で指定可能（例: `development`, `productivity`, `learning`, `security`）。

> **`metadata.pluginRoot`**: marketplace 全体で相対 `source` パスのベースディレクトリを指定できる。
>
> **`defaultEnabled` の優先順位**: marketplace エントリ側の `defaultEnabled` が、plugin.json 側の `defaultEnabled` より**優先**される。配布側（marketplace）で「インストール時は無効」を強制できる。
>
> **フォルダ衝突の警告**: manifest のキーと既定フォルダ（`commands/` 等）が衝突する場合、v2.1.140 以降は `/doctor` と `claude plugin list` が「無視したフォルダ」を警告する。

### マーケットプレイスの管理

```bash
/plugin marketplace add <url>              # マーケットプレイスを追加
/plugin marketplace update                 # ローカルコピーを更新
/plugin marketplace                        # マーケットプレイス一覧
```

### チームへの共有（extraKnownMarketplaces）

リポジトリの `.claude/settings.json` に `extraKnownMarketplaces` を設定すると、チームメンバーがフォルダを信頼した際にマーケットプレイスと Plugin のインストールを促される。

```json
{
  "extraKnownMarketplaces": [
    {
      "source": "github",
      "repo": "company/claude-plugins-marketplace"
    }
  ]
}
```

ユーザーの信頼境界を尊重し、明示的な同意が必要。不要なマーケットプレイスや Plugin はスキップできる。

### マーケットプレイスの作成から配布までの流れ

1. **Plugin を作成**: Skills・Hooks・Agents・MCP サーバーを含む Plugin を構築
2. **marketplace.json を作成**: Plugin のカタログを定義
3. **ホスティング**: GitHub・GitLab 等の Git ホストにプッシュ
4. **共有**: ユーザーが `/plugin marketplace add` でマーケットプレイスを追加し、`/plugin install` で個別の Plugin をインストール
5. **更新**: リポジトリに変更をプッシュ。ユーザーは `/plugin marketplace update` でローカルコピーを更新

---

## Plugin の作成

### 手動作成

1. ディレクトリ構造を作成:

```bash
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/skills/my-skill
```

2. `plugin.json` を作成:

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "プラグインの説明",
  "author": {
    "name": "Your Name"
  }
}
```

3. コンポーネント（Skills、Hooks、Agents 等）を追加
4. `README.md` を作成

> **frontmatter の boolean 値（v2.1.218〜）**: plugin / skill の frontmatter では `true` / `false` 以外に **`yes` / `no` / `on` / `off` / `1` / `0`（大文字小文字を問わない）** も受理される。既存の設定を書き換える必要はないが、他ツールから移植した定義がそのまま通るようになった。

### plugin-dev による AI アシスト作成

ClaudeCode に同梱されている `plugin-dev` Plugin を使うと、対話的に Plugin を作成できる:

```bash
/plugin-dev:create-plugin [optional description]

# 例
/plugin-dev:create-plugin A plugin for managing database migrations
```

8 つのフェーズ（発見・コンポーネント計画・詳細設計・構造作成・実装・検証・テスト・ドキュメント）を自動で進行する。

### ローカルテスト

```bash
# Plugin ディレクトリを指定して ClaudeCode を起動
claude --plugin-dir /path/to/my-plugin

# Skills が正しくロードされるか確認
# Hooks が正しく発火するか確認
# コマンドが表示されるか確認
```

---

## ベストプラクティス

### Plugin 構造

- **標準のディレクトリ構造に従う**: `.claude-plugin/plugin.json` を必ず配置する
- **README.md を充実させる**: すべてのコマンド・エージェント・Skills を文書化し、使用例を含める
- **コンポーネントを適切に分離**: Skills は `skills/`、Hooks は `hooks/`、Agents は `agents/` にそれぞれ配置する

### 名前空間の活用

Plugin 内の Skills は自動的に `plugin-name:skill-name` の名前空間を持つ。これにより:
- 複数の Plugin が同名の Skill を持てる
- 個人 Skills やプロジェクト Skills との競合を回避できる
- 呼び出し時は `/plugin-name:skill-name` で明示的に指定

> **`:` は名前空間の区切りとして予約された（v2.1.218）**: **subagent の `name` frontmatter に `:` を含められなくなった**。plugin の名前空間区切りとの衝突を避けるための変更である。既存の agent 定義に `:` を使っている場合はリネームが必要（[sub-agents.md](sub-agents.md) 参照）。
>
> **関連する修正**: **v2.1.216** — `name` frontmatter を持つ plugin skill が、スラッシュコマンド補完で **plugin prefix を失う**不具合を修正。**v2.1.214** — `--settings` 経由で有効化した plugin がロードされない不具合を修正（v2.1.181 からの regression）。出典: CHANGELOG v2.1.214 / v2.1.216 / v2.1.218

### ポータブルなパス参照

Plugin 内でファイルやスクリプトを参照する際は、常に `${CLAUDE_PLUGIN_ROOT}` を使用する:

```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

絶対パスやユーザー固有のパスをハードコードしない。

### スコープの選択

| 状況 | 推奨スコープ |
|------|------------|
| 個人で全プロジェクトに使いたい | `user` |
| チーム全員で共有したい | `project` |
| 特定プロジェクトで個人的に試したい | `local` |

### Plugin を作るべき場面

- **同じ Skills・Hooks のセットを複数リポジトリで使う**: 毎回コピーするより Plugin にまとめる
- **チームやコミュニティに配布したい**: マーケットプレイス経由でインストール可能にする
- **Skills + Hooks + MCP を組み合わせた統合機能**: 個別管理より Plugin として一括管理

### Plugin が不要な場面

- **単一プロジェクトでしか使わない Skills**: `.claude/skills/` に直接配置すれば十分
- **個人用の Hooks**: `~/.claude/settings.json` に直接定義すれば十分
- **試行錯誤の段階**: まず個別の Skills・Hooks として動作検証し、安定したら Plugin にまとめる

---

## Tips

### コードインテリジェンス Plugin

型付き言語（TypeScript、Go、Rust 等）を使う場合は、コードインテリジェンス Plugin のインストールを推奨する。正確なシンボルナビゲーションと、編集後の自動エラー検出を提供する。

### ホットリロード

Plugin のインストール・有効化・無効化後は `/reload-plugins` で即時反映できる。ClaudeCode の再起動は不要。

**v2.1.221 以降は `/reload-plugins` 自体が不要になる場面が増えた**:

- `/plugin` からインストールした plugin は、**安全と判断できる場合に即時有効化**される（従来は常に `/reload-plugins` が必要だった）
- `/plugin install` は「plugin not found」を返す前に、**stale な marketplace カタログを更新して再試行**するようになった
- plugin が `skills` パスに **`"."` を受理**するようになり、root-level `SKILL.md` の検証エラーも plugin root を使うよう案内する

> ⚠️ **`/reload-plugins` のサマリに出る skills 件数は `commands/` ディレクトリのみを数えている**。`skills/` を編集しても `0 skills` と表示され得るため、この数字でスキルの読み込みを判断しない（既知の紛らわしい挙動）。

出典: CHANGELOG v2.1.221 / [Create plugins](https://code.claude.com/docs/en/plugins)

### Managed スコープ

組織の管理者がマネージド設定で Plugin をインストールした場合、`managed` スコープとなる。ユーザーは変更・削除できない。

### 公式 Plugin

ClaudeCode リポジトリ（[anthropics/claude-code](https://github.com/anthropics/claude-code)）の `plugins/` ディレクトリに公式 Plugin が含まれている。`plugin-dev` は Plugin 開発を支援する公式ツールキットである。

**security-guidance plugin（公式）**: Claude のコード変更を脆弱性観点でレビューし、その場で修正する公式 Plugin。3 段構成で動作する — 編集ごとの高速パターンチェック → ターンごとのモデルレビュー → commit/push 時の深いエージェントレビュー。プロジェクト固有のルールは `.claude/claude-security-guidance.md` に置く。

```bash
/plugin install security-guidance@claude-plugins-official
```

> 出典: [Security guidance](https://code.claude.com/docs/en/security-guidance)

---

## 関連ドキュメント

- [Create plugins](https://code.claude.com/docs/en/plugins) — 公式 Plugin 作成ガイド
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — CLI コマンドリファレンス
- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) — Plugin のインストール・管理
- [Create and distribute marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — マーケットプレイスの作成・配布
- [ClaudeCode Skills ガイド](skills.md) — Skills の詳細（Plugin 内 Skills にも適用）
- [ClaudeCode のベストプラクティス](best-practices.md) — ClaudeCode 全般のベストプラクティス
