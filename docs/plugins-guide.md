# ClaudeCode Plugins ガイド

> 出典: [Create plugins](https://code.claude.com/docs/en/plugins) / [Plugins reference](https://code.claude.com/docs/en/plugins-reference) / [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) / [Create and distribute marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) / [anthropics/claude-code](https://github.com/anthropics/claude-code) (2026-03-25時点)

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
└── README.md                 # ドキュメント
```

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
| `name` | string | Yes | Plugin 名。マーケットプレイス内で一意 |
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
| `lspServers` | string | No | LSP サーバー設定ファイルのパス |
| `strict` | boolean | No | strict モードの有効化 |

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

Skills の書き方は [Skills ガイド](skills-guide.md) を参照。

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

`/plugin` コマンドで対話的な UI を開き、**Discover** タブからマーケットプレイスのプラグインを閲覧・インストールできる。スコープの選択も UI 上で行える。

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
/reload-plugins                            # 変更を即時反映（再起動不要）
```

**アンインストールの挙動**: `/plugin uninstall` は project スコープの場合、`.claude/settings.json` を直接変更せず `.claude/settings.local.json` で無効化する。チームメイトに影響しない。

`--keep-data` オプションで Plugin の永続データを保持したままアンインストールできる:

```bash
/plugin uninstall formatter@my-marketplace --scope project --keep-data
```

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

`source` は以下の 2 種類:
- **ローカルパス**: `"./plugins/formatter"` — 同一リポジトリ内のディレクトリ
- **GitHub リポジトリ**: `{"source": "github", "repo": "owner/repo"}` — 外部リポジトリ

`category` は任意で指定可能（例: `development`, `productivity`, `learning`, `security`）。

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

### Managed スコープ

組織の管理者がマネージド設定で Plugin をインストールした場合、`managed` スコープとなる。ユーザーは変更・削除できない。

### 公式 Plugin

ClaudeCode リポジトリ（[anthropics/claude-code](https://github.com/anthropics/claude-code)）の `plugins/` ディレクトリに公式 Plugin が含まれている。`plugin-dev` は Plugin 開発を支援する公式ツールキットである。

---

## 関連ドキュメント

- [Create plugins](https://code.claude.com/docs/en/plugins) — 公式 Plugin 作成ガイド
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — CLI コマンドリファレンス
- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) — Plugin のインストール・管理
- [Create and distribute marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — マーケットプレイスの作成・配布
- [ClaudeCode Skills ガイド](skills-guide.md) — Skills の詳細（Plugin 内 Skills にも適用）
- [ClaudeCode のベストプラクティス](best-practices.md) — ClaudeCode 全般のベストプラクティス
