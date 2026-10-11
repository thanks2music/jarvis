# ClaudeCode Plugins ガイド

> 出典: [Plugins overview](https://code.claude.com/docs/en/plugins/overview) / [Create a plugin](https://code.claude.com/docs/en/plugins/create) / [Add components to a plugin](https://code.claude.com/docs/en/plugins/components) / [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference) / [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) / [Install and manage plugins](https://code.claude.com/docs/en/plugins/install) / [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading) / [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) / [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference) / [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace) / [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces) / [Publish and distribute a plugin](https://code.claude.com/docs/en/plugins/publish) / [Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org) / [Plugin security and trust](https://code.claude.com/docs/en/plugins/security) / [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure) / [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) / [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [Environment variables](https://code.claude.com/docs/en/env-vars) / [Security guidance](https://code.claude.com/docs/en/security-guidance) / [Claude Security](https://code.claude.com/docs/en/claude-security) / [Week 37 · September 7–11, 2026](https://code.claude.com/docs/en/whats-new/2026-w37) / [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support) / [Manage plugins for your organization (claude.ai)](https://claude.com/docs/plugins/admin) / [Publish to the directory](https://claude.com/docs/directory/publish) / [Build plugins for Claude](https://claude.com/resources/articles/build-plugins-for-claude) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2026-10-11時点。CHANGELOG 由来の記述は 2026-09-03 に v2.1.258 まで反映済みで、それ以降の版数は各公式ページの「Requires Claude Code」記載による)
>
> **2026-10-11 出典張替え**: 公式の旧 7 ページ（Create plugins / Plugins reference / Create and distribute marketplaces / Discover and install plugins / Plugin dependencies / Plugin hints / Plugin relevance）は `docs/en/plugins/` 配下へ改名・分割された。旧 URL は今も新ページの本文を返すが公式の索引 (llms.txt) から消えたため、本ドキュメントの出典とアンカーは新ページに張り替えた。

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
│   └── plugin.json          # メタデータ（**任意**。省略時は標準レイアウトから自動検出）
├── commands/                 # スラッシュコマンド（*.md）※ 新規プラグインは skills/ の使用が推奨
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
├── workflows/                # Workflow スクリプト
├── themes/                   # テーマ
├── output-styles/            # 出力スタイル
└── README.md                 # ドキュメント
```

> **plugin ルートの `CLAUDE.md` は project context としてロードされない**（公式明記）。プラグイン利用者のセッションに常時ルールを注入する用途には使えない。

> **配布・ロードの追加手段**: プラグインは `.zip` でも配布できる（`--plugin-dir <zip>`、v2.1.128〜）。URL からの直接ロードは `--plugin-url`。community marketplace の**名称は `claude-community`** で、`anthropics/claude-plugins-community` は `claude plugin marketplace add` に渡す **repo 名**である（2026-08-12 訂正: 両者を混同していた）。公式 marketplace は `claude-plugins-official`。

> **`archive` plugin source（v2.1.224〜）**: git / npm を使わず、**HTTPS 経由の zip アーカイブから plugin を配布・インストール**できるようになった。**認証が必要な配布元には `headers`（object）または `headersHelper`（短命の HTTP ヘッダを生成するコマンド。`"strict": false` が必要）を使う**（v2.1.238〜）。`claude plugin install` / `update` は helper を実行する前に `[y/N]` の確認を出す。`sha256` でのピン留めに対応する。**`http://`・loopback・link-local・cloud-metadata ホストは拒否**される。
>
> **marketplace の owner ワイルドカード（v2.1.223〜）**: `strictKnownMarketplaces` / `blockedMarketplaces` が `"owner/*"` 形式を受理し、**GitHub org 単位で一括許可 / 遮断**できる。
>
> **設定キーの別名（v2.1.232〜）**: `extraKnownMarketplaces` / `strictKnownMarketplaces` は、それぞれ **`additionalMarketplaces` / `allowedMarketplaces`** という「読みやすい別名」でも受理されるようになった。**既存のキー名も引き続き有効**なので書き換えは不要である。旧版のクライアントは別名を無視するため、版が混在する環境では正式名を使う。同じファイルに両方を書いた場合は正式名の値が使われる。**2026-10-11 更新**: 以前は「公式ページへの掲載が無く CHANGELOG が一次情報」としていたが、現行公式 [Manage Claude Code plugins for your organization — Aliases for the marketplace keys](https://code.claude.com/docs/en/plugins/org#aliases-for-the-marketplace-keys) に掲載された。

⚠️ **`plugin.json`（manifest）は任意である**（2026-08-12 訂正、2026-10-11 再確認）。公式 [Plugin manifest reference — Manifest file](https://code.claude.com/docs/en/plugins/manifest-reference#manifest-file) は「The manifest is optional」と明記している。省略した場合は**標準レイアウトに置いたコンポーネントが自動検出**され、plugin 名は **marketplace エントリの名前**、`--plugin-dir` で読み込んだ場合は**ディレクトリ名**になる。manifest を置く場合に必須なのは `name` だけである。メタデータ・既定外の場所に置くコンポーネント・`userConfig`・インライン定義が要るときに書く。

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
| `name` | string | Yes | Plugin 名（kebab-case）。空白・`@`・`:`・パス区切り・制御文字は使えない。全コンポーネントがこの名前空間に入る（予約名の規則は表の後） |
| `displayName` | string | No | `/plugin` ピッカー等の UI に表示する人間向け名称（スペース・大文字可）。名前空間・ルックアップには使われない。marketplace エントリ側の `displayName` が優先。**v2.1.143 以降** |
| `version` | string | No | バージョン文字列（semver の検査はしない）。設定すると、変更するまで利用者はその版に留まる（後述「バージョン解決とキャッシュキー」） |
| `description` | string | No | Plugin の概要説明 |
| `author` | object | No | 作者情報。`name` は**必須**、`email`・`url` は任意 |
| `homepage` | string | No | ドキュメントの URL。**URL として解釈できないと plugin のロードに失敗する** |
| `repository` | string | No | ソースコードリポジトリの URL（検証されない） |
| `license` | string | No | SPDX 識別子（例: `MIT`、`Apache-2.0`） |
| `keywords` | string[] | No | 検索用キーワード |
| `icon` / `documentationUrl` / `supportUrl` / `privacyPolicyUrl` / `termsOfServiceUrl` | string | No | Anthropic の directory 掲載用（`icon` は plugin 内の画像パス、他は `https://` URL）。**Claude Code はロード時に読まない**。`plugin.json` にだけ書く（marketplace エントリに書くと validate が unknown field と報告）。v2.1.281 以降の validate は警告しない |
| `commands` | string/string[]/object | No | フラットな `.md` コマンドファイル、そのディレクトリ、またはコマンド名 → `source` / `content` の object map。**既定の `commands/` 走査を置き換える** |
| `agents` | string/string[] | No | エージェントの `.md` ファイル。**ディレクトリは受け付けない**。既定の `agents/` 走査を置き換える |
| `skills` | string/string[] | No | Skills を探すディレクトリ（`<name>/SKILL.md` を並べたディレクトリ、または `SKILL.md` を直接持つフォルダ）。`"."` は plugin ルート。**既定の `skills/` 走査に追加される** |
| `hooks` | string/object/array | No | `.json` のフック設定ファイル or インライン定義（配列で複数可）。`hooks/hooks.json` と併せて読み込まれる |
| `mcpServers` | string/object/array | No | `.json` の MCP 設定ファイル、`.mcpb` / `.dxt` バンドル、`https://` のバンドル URL、またはサーバー名をキーにしたインライン定義。`.mcp.json` と併せて読み込まれ、後から宣言した同名サーバーが前のものを置き換える |
| `outputStyles` | string/string[] | No | 出力スタイルのファイル or ディレクトリ。既定の `output-styles/` 走査を置き換える |
| `lspServers` | string/object/array | No | LSP サーバー（コードインテリジェンス）の `.json` 設定 or インライン定義。`.lsp.json` と併せて読み込まれる |
| `experimental.monitors` | string/array | No | バックグラウンド監視（Monitor）。`.json` のパス or インライン配列で、既定は `monitors/monitors.json`。各エントリの `when` が `"always"`（既定。セッション開始時と plugin の reload 時に起動）か `"on-skill-invoke:<skill>"`（その skill の初回実行時に起動）。**対話セッションでのみ動き、Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry では動かない**。**v2.1.105 以降**（experimental） |
| `dependencies` | string[]/object[] | No | このプラグインが要求する他プラグイン。`"name"`・`"name@marketplace"`・`{ "name", "marketplace", "version" }` のいずれか（semver 制約付き可）。例: `[{ "name": "secrets-vault", "version": "~2.1.0" }]` |
| `defaultEnabled` | boolean | No | ユーザー未設定時に有効状態で開始するか。既定 `true`。`false` で「インストール時は無効」配布が可能。**v2.1.154 以降**（旧版は無視して有効化） |
| `settings` | object | No | plugin 有効時に適用する設定。**効くのは `agent` と `subagentStatusLine` だけ**で、他のキーはロード時に捨てられる。plugin ルートの `settings.json` が優先 |
| `types` | string | No | [mod](#modshooks-module) の `$.state` の値と `$` の名詞を宣言する `.d.ts` ファイルのパス |
| `$schema` | string | No | JSON Schema の URL（エディタ補完用。ロード時は無視） |
| `metadata` | object | No | 任意のメタデータ。Claude Code は読まない（v2.1.222〜） |
| `workflows` | string/string[] | No | Workflow の `.js` ファイル or ディレクトリ。既定の `workflows/` 走査を置き換える |
| `userConfig` | object | No | ユーザーが設定できる項目の定義 |
| `channels` | **array** | No | Channels（外部イベント push）の定義。各エントリは plugin の MCP サーバーの 1 つに紐づく。[mcp-setup.md](mcp-setup.md) 参照（2026-09-03 訂正: 旧記述の `string/object` は誤り。現行公式 manifest-reference の Fields 表でも `Array of objects`） |
| `experimental.themes` | string/string[] | No | テーマのファイル or ディレクトリ。既定の `themes/` 走査を置き換える。トップレベルの `themes` キーも validate の警告付きで読まれる |
| `experimental.evals` | string/string[] | No | eval ケースのディレクトリ（既定 `evals/` 以外に置く場合）。配列は先頭だけが使われる。`claude plugin eval --eval-dir` が優先 |

> **`name` の予約規則**: 大文字小文字を区別せず、区切り記号の連続を 1 つとみなして判定する。`claude-` / `anthropic-` / `anthropics-` / `cc-plugin-` で始まる名前、`claude` / `anthropic` / `anthropics` / `claude-code` / `claude-mods` そのもの、`official` を `claude` / `anthropic` と並べた名前（例 `official-claude-tools`）は `claude plugin validate` がエラーにし、`claude plugin init` / `tag` も拒否する（ただしインストールとロードはできる）。それ以外の位置で `claude` 等を単語として含む名前（例 `mcp-for-claude`）は警告になる。出典: [Plugin manifest reference — name](https://code.claude.com/docs/en/plugins/manifest-reference#name)

> ⚠️ **`strict` は `plugin.json` のフィールドではない**（2026-08-12 訂正）。`claude plugin validate --strict` という **CLI オプション**（警告も失敗として扱う。CI 向け）である。
>
> **ただし「`strict` というキーが存在しない」わけではない**（**2026-09-03 補足**）。`strict`（boolean、既定 `true`）は **`marketplace.json` の plugin entry の正式フィールド**で、取得した plugin に `plugin.json` があり、**かつ entry 側も `commands` / `agents` / `skills` / `hooks` / `outputStyles` / `themes` を宣言したとき**の扱いを決める。
>
> | `strict` | `plugin.json` | entry のコンポーネント宣言 | 結果 |
> |---|---|---|---|
> | どちらでも | 無い | どちらでも | entry が manifest になる |
> | `true`（既定） | ある | どちらでも | `plugin.json` が権威。entry のコンポーネントは**追記**される（`hooks` だけはイベント単位で entry の matcher が置き換える） |
> | `false` | ある | 無い | `plugin.json` が manifest（`true` と同じ） |
> | `false` | ある | 1 つ以上 | **衝突**。`Plugin <name> has conflicting manifests` でロードに失敗する |
>
> `archive` source の `headersHelper` を entry に書く場合は `"strict": false` が必須である。**2026-10-11 訂正**: 以前は「`strict` を偽にすると marketplace 側の定義が勝つ」と書いていたが誤りで、現行公式では `false` かつ entry がコンポーネントを宣言すると衝突エラーになる。出典: [Marketplace reference — Strict mode](https://code.claude.com/docs/en/plugins/marketplace-reference#strict-mode) / [Plugin manifest reference — Marketplace entries and the manifest](https://code.claude.com/docs/en/plugins/manifest-reference#marketplace-entries-and-the-manifest)
>
> **未知のフィールドの扱い**（公式 "Unrecognized fields"）: トップレベルの未知フィールドは除去されて plugin はロードされる（validate は警告）。`userConfig` の各オプション・`channels` エントリ・`lspServers` 設定・`monitors` エントリの中の未知キーは**エラーで、plugin はロードされない**。

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

**利用できるパス変数は 3 種**（2026-08-12 更新。`${CLAUDE_PROJECT_DIR}` を追記）:

| 変数 | 解決先 |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin のインストールディレクトリ |
| `${CLAUDE_PLUGIN_DATA}` | Plugin の永続データディレクトリ（更新を跨いで残る） |
| `${CLAUDE_PROJECT_DIR}` | 現在のプロジェクトルート |

> ⚠️ **`${CLAUDE_PLUGIN_ROOT}` は plugin の更新でパスが変わる**。**旧ディレクトリは約 2 週間残存**した後に削除されるため、絶対パスをどこかに控えておく運用は壊れる。永続化したいデータは `${CLAUDE_PLUGIN_DATA}` に置く。

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

## Mods（hooks module）

> 出典: [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference) / [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) (2026-10-11時点)

**mod は plugin の一種**で、`hooks/hooks.json` の `modules`（例 `"modules": ["./register.js"]`）に指定した JavaScript / TypeScript のファイル（**hooks module**）を Claude Code の**プロセス内**で実行する。ツール呼び出し・プロンプト送信・UI の描画などのイベントで呼ばれる関数を登録し、イベントを観察・書き換え・肩代わりできる。transcript 横の pane や prompt 上の band、Claude のターンを介さずに即実行される `/command` も足せる。

- **既定で ON**: CLI は v2.1.287 以降、Desktop の Code タブは v2.1.286 以降
- **sandbox の外で本人の権限で動く**: ファイル・プロセス・ネットワーク・環境変数に触れ、`ask` ルールで確認されるはずのツール呼び出しや、自分の `PreToolUse` フックが止めた呼び出しも承認しうる。信頼できる作者・marketplace のものだけを入れる
- **組込み mod もある**: `/diff` パネル（`cc-plugin-diff`）や `AGENTS.md` の読み込み（`cc-plugin-agents-md`）、ユーザーの mod から組織の管理設定を守る `cc-plugin-sec-default` など
- **止め方**: 個別は `/plugin` で plugin を無効化、1 セッションだけなら `--safe-mode`、全部なら `"disableAllHooks": true`。組織は `allowManagedModsOnly` 等で制御する
- **テスト**: `claude plugin test` で `*.test.ts` / `*.test.tsx` を実行する（セッション・サインイン・ネットワーク不要）

> 公式の mods ページは、mod のハンドラを「hook」、settings ファイルに書く従来のフック（[Hooks ガイド](hooks.md)）を「**settings hook**」と呼び分けている。仕組み・API・管理キーの詳細は [Mods ガイド](mods.md) を参照。

---

## Plugin のインストールと管理

### インストール

> 出典: [Install and manage plugins](https://code.claude.com/docs/en/plugins/install) / [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) (2026-10-11時点)

```bash
# セッション内: Discover タブで plugin の詳細を開き、そこでスコープを選んでインストールする
/plugin install formatter@my-marketplace

# シェルから（スクリプト向け）。スコープの既定は user
claude plugin install formatter@my-marketplace
claude plugin install formatter@my-marketplace --scope project   # .claude/settings.json に記録
claude plugin install formatter@my-marketplace --scope local     # .claude/settings.local.json に記録
```

> **2026-10-11 訂正**: 以前は `/plugin install` に `--scope` を付ける例を載せていたが、**セッション内の `/plugin install` はすぐにはインストールせず、`/plugin` パネルの詳細画面でスコープを選ばせる**。`--scope` はシェル側 `claude plugin install` のフラグである。

| スコープ | 保存先 | 用途 | Git 共有 |
|---------|--------|------|----------|
| `user`（デフォルト） | `~/.claude/settings.json` | 全プロジェクト共通 | しない |
| `project` | `.claude/settings.json` | チーム全員で共有 | **する** |
| `local` | `.claude/settings.local.json` | 現在のプロジェクトのみ | しない |

- **project スコープは「有効化」の共有であり、ダウンロードの共有ではない**。`.claude/settings.json` を commit しても共同作業者のマシンには入らないため、各自が一度 `claude plugin install <name>@<marketplace> --scope project` を実行する
- **marketplace の追加とインストールを 1 コマンドで**: `--marketplace <source>` を付けると、未追加の marketplace を（確認のうえ）追加してから plugin を入れる。セッション内の `/plugin install <plugin> --marketplace <source>` は v2.1.275 以降、シェルの `claude plugin install <plugin> --marketplace <source>` は v2.1.292 以降（公式 cli-reference の記載）
- **同じ plugin を複数スコープで設定した場合**は local > project > user の順に優先される

### 対話的インストール

`/plugin` コマンドで対話的な UI を開き、**Discover** タブからマーケットプレイスのプラグインを閲覧・インストールできる。スコープの選択も UI 上で行える。**v2.1.186 で Installed タブに "Skills" セクションが追加**され、プラグインが提供する Skill を UI から個別確認できるようになった。

### ローカル開発用の読み込み

開発中の Plugin はディレクトリ指定で直接読み込める（そのセッション限りで、設定には何も書かれない）:

```bash
claude --plugin-dir /path/to/my-plugin                 # ディレクトリ or .zip。複数指定可
claude --plugin-dir ./plugins                          # plugin を並べたフォルダ（v2.1.265〜）
claude --plugin-url https://example.com/my-plugin.zip  # URL の .zip を取得して読み込む
```

- **フォルダを渡すと配下を一括ロード**（v2.1.265〜、公式 create ページの記載）: トップレベルに `.claude-plugin/` もコンポーネントも無いフォルダは「plugin の入ったフォルダ」とみなされ、`.claude-plugin/plugin.json` を持つ**直下のサブフォルダ**がそれぞれ plugin として読まれる（manifest の無いサブフォルダは黙って飛ばされる）。対話セッション中にサブフォルダを足す・消すと plugin のロード・アンロードも追従する
- **marketplace ルートを渡した場合**: `.claude-plugin/` に `plugin.json` が無く `marketplace.json` だけがある構成なら、v2.1.281 以降は横に並ぶ plugin フォルダが読まれる。`marketplace.json` 自体は読まれない（何もインストール・有効化されない）
- **フラグを付けられない環境**では、絶対パスを `CLAUDE_CODE_PLUGIN_DIRS`（Unix は `:`、Windows は `;` 区切り）に並べる（v2.1.280〜）。project / local settings の `env` からは設定できない
- 読み込んだ plugin は `<name>@inline` として扱われる。managed 設定の `disableSideloadFlags` で、管理者は `--plugin-dir` / `--plugin-url` / `CLAUDE_CODE_PLUGIN_DIRS` をまとめて拒否できる

出典: [Create a plugin — Develop without a marketplace](https://code.claude.com/docs/en/plugins/create#develop-without-a-marketplace) / [Plugin commands reference — Flags that load a plugin for one session](https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session)

### 管理コマンド

セッション内の `/plugin` は対話的な UI を開くのが基本で、多くのサブコマンドは該当タブを開いてそこで操作する。

```bash
/plugin                                    # 対話的 UI を開く（Discover タブ）
/plugin install <name>@<marketplace>       # Discover タブで plugin の詳細を開く（スコープを選んでインストール）
/plugin uninstall <name>@<marketplace>     # Installed タブを開いてアンインストール
/plugin disable <name>@<marketplace>       # 一時的に無効化
/plugin enable <name>@<marketplace>        # 再有効化
/plugin configure <name>@<marketplace>     # userConfig のダイアログを開く
/plugin list                               # marketplace 由来のインストール済み一覧（--enabled / --disabled フィルタ可、v2.1.163〜）
/reload-plugins                            # 変更を即時反映（再起動不要。--force は後述）
```

CLI（シェル）からの操作も用意されている。`claude plugins` は `claude plugin` の別名である。

```bash
claude plugin init <name>                  # 新規 Plugin の雛形を ~/.claude/skills/ に生成（v2.1.157〜）
claude plugin install <plugin>             # インストール（--scope / --config / --yes / --json / --marketplace）
claude plugin uninstall <plugin>           # アンインストール（--scope / --keep-data / --prune / --json）
claude plugin enable <plugin>              # 有効化
claude plugin disable <plugin>             # 無効化
claude plugin update <plugin>              # 最新版へ更新（--scope 省略時は自動判定）
claude plugin list                         # インストール済み Plugin の一覧（--json あり）
claude plugin details <name>               # コンポーネント一覧と**トークンコストの見積もり**
claude plugin configure <plugin>           # userConfig の確認・保存（v2.1.285〜）
claude plugin prune                        # 自動インストールされた依存のうち、もう要らないものを削除（別名 autoremove）
claude plugin eval [target]                # eval ケースを実行して採点（v2.1.269〜）
claude plugin eval init                    # eval スイートを対話的に作る
claude plugin tag [path]                   # リリース用の annotated git tag `<name>--v<version>` を作る
claude plugin test [directory]             # mod のテスト（*.test.ts / *.test.tsx）を実行
claude plugin validate <path>              # manifest / 構成の検証（`--strict` で警告も失敗扱い）
claude plugin marketplace add <source>     # marketplace を追加
claude plugin marketplace list             # marketplace の一覧（--json あり）
claude plugin marketplace remove <name>    # marketplace を削除（そこから入れた plugin もアンインストール）
claude plugin marketplace update [name]    # marketplace のカタログを refresh
```

> **公式のサブコマンドは 15 個 + marketplace 系 4 個である**（2026-10-11 更新。2026-08-12 時点の本ドキュメントは「11 個」としていた）。シェル側の `init` / `update` / `details` / `prune` / `eval` / `eval init` / `test` には**セッション内の形が無い**。特に **`claude plugin details` はトークンコストの見積もりを表示する**ため、「どの plugin がコンテキストを食っているか」を調べる用途に使える。全一覧は [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) を参照。
>
> **`--json`（v2.1.268〜）**: `install` / `uninstall` / `update` / `enable` / `disable` に `--json` を付けると、結果を**標準出力の最終行に JSON オブジェクト 1 つ**で出す（スクリプト向け）。`list` と `marketplace` 系にも `--json` がある。出典: [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) / [Week 37](https://code.claude.com/docs/en/whats-new/2026-w37)

> **`/plugin list`（セッション内）は marketplace 由来の plugin のみを表示する**。`@skills-dir` 経由で自動ロードされた plugin は出てこない点に注意する。

**`.claude/skills` 自動ロード（v2.1.157〜）**: `.claude/skills/` ディレクトリ配下に置いた Plugin は、marketplace を経由せずに**自動ロード**される。手元で素早く Plugin を試す場合に便利である（`--plugin-dir` 起動と並ぶ開発手段）。**単一 skill のみを持つ Plugin なら `SKILL.md` を root に置くだけで自動検出される**(v2.1.142+、`"skills": ["./"]` の明示指定不要。frontmatter の `name` が invocation 名になる)。

#### `@skills-dir` — marketplace も install も不要な開発フロー

> ⚠️ **`@skills-dir` は personal スコープと project スコープで挙動が異なる**（2026-08-12 追記）。
>
> | 観点 | personal（`~/.claude/skills/`） | project（`<repo>/.claude/skills/`） |
> |---|---|---|
> | ロード条件 | 即座にロードされる | **workspace trust を承認するまでロードされない** |
> | background monitors | ロードされる | **ロードされない** |
> | ディレクトリ探索 | — | **リポジトリルートへ walk up しない**（起動した cwd 直下の `.claude/skills/` のみ） |
>
> 最後の点は重要で、**サブディレクトリから `claude` を起動すると、リポジトリルートの `.claude/skills/` は読まれない**。本リポジトリの `claude-docs-sync`（project スコープ + symlink 運用）も、必ずリポジトリルートで起動する前提である。

**`claude plugin init my-tool`** は `~/.claude/skills/my-tool/` に `.claude-plugin/plugin.json` と starter `SKILL.md` を生成する。この plugin は次のセッションから **`my-tool@skills-dir`** として**自動ロード**され、**marketplace 登録も `/plugin install` も不要**である。

```bash
claude plugin init my-tool     # ~/.claude/skills/my-tool/ に雛形を生成
# → 次セッションで my-tool@skills-dir として自動ロードされる
```

- `--plugin-dir` を毎回渡す必要がなくなるため、**自作 skill / plugin を日常的に育てる運用に向く**
- **`claude-plugins-official` は初回の対話起動時に自動登録される**（managed policy か `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL` で止められる）。非対話起動が先だった場合や marketplace policy でブロックされた場合は、`claude plugin marketplace add anthropics/claude-plugins-official` を手動実行する
- plugin ルートの `settings.json` は **`plugin.json` 内の `settings` より優先**され、未知のキーは silent ignore される
- **組織が `strictKnownMarketplaces`（許可リスト）を設定すると、`{ "source": "skills-dir" }` エントリが無い限り `@skills-dir` の plugin は読み込まれなくなる**（manifest を持たない素の Skill は読まれ続ける）

> **本リポジトリの運用との関係**: 本環境の skills / plugins は avengers リポジトリで実体管理し `~/.claude/skills/` へ symlink する方式を採っている。`@skills-dir` は**この配置とそのまま噛み合う**（`~/.claude/skills/<name>/` に `.claude-plugin/plugin.json` があれば plugin として認識される）ため、marketplace を用意せずに plugin 化する選択肢になる。

出典: [Create a plugin — Make a plugin load in every session](https://code.claude.com/docs/en/plugins/create#scaffold-a-plugin-that-loads-every-session) / [Plugin loading reference — Plugins shared through a repository](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository) / [Manage Claude Code plugins for your organization — Keep skills-directory plugins loading](https://code.claude.com/docs/en/plugins/org#keep-skills-directory-plugins-loading)

**Marketplace の rename 自動追従**(v2.1.193): `marketplace.json` に `renames` map を設定すると、プラグインをリネームしても既存インストールが自動で settings 更新される。配布側の破壊的変更を利用者に手作業させずに済む。

**`claude plugin validate` の対象拡張**(v2.1.196): `.` を source とするローカルプラグインも validate 対象になった。CI での事前チェックに使いやすい。**v2.1.221 では名前の検証警告が追加**され、marketplace 名 / plugin 名が **Claude Desktop の managed marketplace sync で拒否される形式**である場合に警告が出るようになった（配布前に気付ける）。**v2.1.233 ではさらに、plugin 構造の外にある bare な `.claude/skills` ディレクトリも検査対象**になり、frontmatter のパースに失敗した `SKILL.md` を報告するようになった（本リポジトリのように `.claude/skills/` へ symlink を置く運用でも事前チェックが効く）。

**org 配布 skill の名前衝突バグ修正**(v2.1.221): plugin / 組織配布の skill が**ターミナル専用組込コマンドと同名**の場合に**非対話セッションで起動できない**不具合が修正された。現行の [Skills](https://code.claude.com/docs/en/skills) によれば、非対話セッションで予約が外れるのは **`help` と `feedback` の 2 つだけ**で、`/login` など他のターミナル専用コマンド名は予約されたまま（2026-10-11 訂正: 以前は「`/help` `/feedback` 等」と書いていた）。

**project で有効化された plugin のアンインストール**: リポジトリの `.claude/settings.json` が有効化している plugin を、`/plugin` の Installed タブや `/plugin uninstall` で Uninstall すると、どちらにするかを尋ねられる。

| キー | 選択肢 | 動作 |
|---|---|---|
| **y** | Disable for me | 自分の `.claude/settings.local.json` に `false` を書く。プロジェクトにはインストールされたまま（チームメイトに影響しない） |
| **u** | Uninstall for everyone | 共有の `.claude/settings.json` から plugin を外す |

> **2026-10-11 訂正**: 以前は「project スコープのアンインストールは常に `settings.local.json` での無効化になる」と書いていたが、現行公式では上の 2 択のプロンプトが出る。出典: [Install and manage plugins — Uninstall a plugin the project enables](https://code.claude.com/docs/en/plugins/install#uninstall-a-plugin-the-project-enables)

**最後のスコープからアンインストールすると、plugin の永続データディレクトリ（`~/.claude/plugins/data/<id>/`）と保存済みの `userConfig` の値・secret も削除される**。データを残したい場合はシェル側の `claude plugin uninstall` に `--keep-data` を付ける:

```bash
claude plugin uninstall formatter@my-marketplace --scope project --keep-data
```

出典: [Plugin commands reference — plugin uninstall](https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall)

### コストと利用状況を確かめる

| 手段 | 分かること |
|---|---|
| `claude plugin details <name>` | **Always-on**（skill / agent / command の名前と description が全セッションに足すトークン）と、コンポーネントごとの always-on / on-invoke の内訳 |
| `/plugin` で marketplace の plugin を選ぶ | 公式 marketplace の plugin だけ、詳細ペインに **Context cost**（`Every turn:` と `When invoked:`）が出る。自前の marketplace の plugin には出ない |
| `/plugin` の Installed タブ | 自分で入れた plugin のうち **14 日以上かつ 10 セッション以上使われていないもの**が **Not used recently** の見出しの下に移る。詳細には `Last used:` 行が出る |

使っていない plugin も起動時間とコンテキストを消費し続けるため、これらで見つけて無効化・アンインストールする。出典: [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure) / [Install and manage plugins — Find plugins you no longer use](https://code.claude.com/docs/en/plugins/install#find-plugins-you-no-longer-use)

---

## アップデートの仕組み

> 出典: [Plugin loading reference — Versions and updates](https://code.claude.com/docs/en/plugins/loading#versions-and-updates) / [Install and manage plugins — Keep plugins updated](https://code.claude.com/docs/en/plugins/install#keep-plugins-updated) / [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace) / [Environment variables](https://code.claude.com/docs/en/env-vars) (2026-10-11 時点)

ClaudeCode の Plugin の更新は **marketplace 単位の自動アップデート + 手動更新** の組み合わせである。**自動アップデートが既定で ON なのは、Anthropic の公式 marketplace（`claude-plugins-official` など。`knowledge-work-plugins` と `first-party-plugins` は除く）と claude.ai から追加した marketplace だけ**で、community・サードパーティ・ローカル開発用の marketplace は既定 OFF である。

> **2026-10-11 訂正**: 以前は「既定で自動アップデートされ、放置していても最新版に追従する」と書いていたが、自作・社内・サードパーティの marketplace は、ユーザーか管理者が ON にしない限り追従しない。`marketplace.json` 側に自動更新を ON にするフィールドは無い。

### 自動アップデート

対話セッションで**最初のメッセージを送った後、最大 10 分のランダムな遅延**を置いて実行される。auto-update が ON の marketplace を refresh し、そこから入れた plugin をディスク上で更新する。実行中のセッションは読み込み済みの版を使い続け、`Plugin updated: <name> · Run /reload-plugins to apply` が表示される。次回起動時は新しい版が読まれる。

marketplace の auto-update が ON かどうかは、次のうち最初に設定されているもので決まる。

1. settings ファイルの `extraKnownMarketplaces` エントリの `autoUpdate`
2. `known_marketplaces.json` エントリの `autoUpdate`（`/plugin` の Marketplaces タブの **Enable auto-update** トグルが書く）
3. 既定値（上記）

`headersHelper` を宣言した entry の plugin は自動更新の対象外である。`command` source の plugin はこのパスを待たず、セッションごとにコマンドを再実行する（後述）。Seed-managed marketplace（企業配布の read-only マーケットプレース）も対象外。

#### 自動更新を制御する設定・環境変数

| 設定・環境変数 | 効果 |
|---------|------|
| `extraKnownMarketplaces` エントリの `autoUpdate`（`true` / `false`） | その marketplace の自動更新を決める（最優先）。managed 設定で指定すると、ユーザーの `/plugin` トグルは拒否される |
| `/plugin` の Marketplaces タブ → **Enable / Disable auto-update** | ユーザーが marketplace ごとに切り替える |
| `DISABLE_AUTOUPDATER=1` / `DISABLE_UPDATES=1` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | いずれかを設定すると **plugin の自動更新パス全体が止まり**、トグルも非表示になる（各変数は Claude Code 本体の更新にも効く） |
| `FORCE_AUTOUPDATE_PLUGINS=1` | 上の 3 変数があっても plugin の自動更新だけは動かす（本体の更新は止めたまま） |
| `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` | refresh がリモートに届かない・認証できないとき、再 clone を試みずに既存の checkout を使い続ける（オフライン・airgapped 環境向け） |

> **2026-10-11 再訂正**: 2026-05-30 には「env-vars に `DISABLE_UPDATES` / `FORCE_AUTOUPDATE_PLUGINS` の独立した項目が無い」として 3 変数を表から外したが、現行の [Environment variables](https://code.claude.com/docs/en/env-vars) には 3 変数とも独立して掲載され、[Plugin loading reference — When auto-update runs](https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs) も plugin の自動更新を止める変数として明記している。表を現行公式に合わせて戻した。なお `DISABLE_AUTOUPDATER` は `command` source の plugin の毎セッション再実行は止めない。

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

`source` が `directory`（ローカルディレクトリ）のマーケットプレースは remote から pull する概念がないため `autoUpdate` 設定は適用外となる。ファイル変更はそのまま即時反映される。

**プライベート marketplace のバックグラウンド更新**は、ユーザーの git の資格情報で認証し、**プロンプトは一切出さない**。

- **SSH のリモート**: `ssh-agent` に読み込んだ鍵で認証される
- **HTTPS のリモート**: 資格情報を保存済みで、プロンプトなしで返せる credential helper（Git Credential Manager、macOS Keychain、`git-credential-store` など）なら認証される。GitHub なら `gh auth login` → `gh auth setup-git` で保存する
- **プロンプトが必要な helper**: バックグラウンドでは答えられず、更新は静かに失敗して既存の checkout のまま動く
- **`GITHUB_TOKEN` などを環境変数に置くだけでは認証されない**。`gh` の credential helper のように、その変数を読む helper を経由したときだけ効く

> **2026-10-11 訂正**: 以前は「プライベート marketplace の自動更新には `GITHUB_TOKEN` / `GH_TOKEN` / `GITLAB_TOKEN` / `GL_TOKEN` 等を環境変数に設定する必要がある」と書いていたが、現行公式では環境変数のトークン単体では足りず、credential helper か `ssh-agent` が必要である。出典: [Host and maintain a marketplace — What background auto-update does with credentials](https://code.claude.com/docs/en/plugins/host-marketplace#what-background-auto-update-does-with-credentials)

### 手動アップデート

| 操作 | 役割 |
|---------|------|
| `/plugin` の Installed タブで plugin を選び **Update now** | その plugin を最新版へ更新（セッション内） |
| `claude plugin update <plugin>@<marketplace>` | シェルから特定 plugin を更新。`--scope` を省くと local → project → user → managed の順で、インストールされている最も具体的なスコープを自動で選ぶ（v2.1.281〜。それ未満は user 固定） |
| `/plugin` の Marketplaces タブで marketplace を選び **Update marketplace**（`/plugin marketplace update <name>` でも同じ画面を開く） | カタログを refresh し、**その marketplace から入れた plugin も更新する**。`command` source の plugin と `headersHelper` 付き entry の plugin は対象外 |
| `claude plugin marketplace update`（名前なし） | 全 marketplace のカタログだけを refresh。**インストール済み plugin の版は変えない** |
| `/reload-plugins` | セッション再起動なしで変更を反映（不足依存も auto-install） |

**全 plugin を一括で更新するコマンドは無い**。また**セッション内に `/plugin update` は無く**、更新はシェル側の `claude plugin update` か `/plugin` の UI で行う。

> **2026-10-11 訂正**: 以前は `/plugin update`（個別・全体）を載せ、「marketplace update だけでは plugin の版は上がらない」と一律に書いていた。現行公式 [Install and manage plugins — Update plugins now](https://code.claude.com/docs/en/plugins/install#update-plugins-now) では、`update` サブコマンドはシェル専用（セッション内は Installed タブの Update now）で一括更新は無く、版を上げないのは**シェルの** `claude plugin marketplace update`（名前なし）である。

> **v2.1.232 での緩和（2026-08-16 追記）**: **`/plugin install <plugin>@<marketplace>` は、インストール前に対象 marketplace を自動で refresh する**ようになった。そのため「marketplace に新しく公開されたばかりのプラグイン」を入れる場合、**事前の marketplace update は不要**である。シェルの `claude plugin install <plugin>@<marketplace>` も同様に refresh する。一方、**marketplace 名を付けない `claude plugin install <plugin>` は refresh せずキャッシュ済みのカタログを読む**。既にインストール済みプラグインの更新には、上表の Update now か `claude plugin update` が要る。出典: CHANGELOG v2.1.232 / [Plugin loading reference — When Claude Code refreshes a marketplace before an install](https://code.claude.com/docs/en/plugins/loading#when-claude-code-refreshes-a-marketplace-before-an-install)

### バージョン解決とキャッシュキー

ClaudeCode はプラグインごとにバージョンを計算して cache key（キャッシュディレクトリ名）として扱い、**`installed_plugins.json` に記録した版と一致すれば更新をスキップ** する。`command` 以外の source では、バージョンは次の順で決まる。

1. `plugin.json` の `version` フィールド
2. marketplace エントリの `version` フィールド
3. どちらも無い場合は source 型から導く

| source 型 | `version` が無いときの版 |
|---|---|
| `github` / `url` / `git-subdir` | source の commit SHA の先頭 12 文字（`git-subdir` はサブディレクトリパスのハッシュも含む） |
| `archive` | SHA-256 ダイジェストの先頭 12 文字（entry の `sha256` ピン。無ければダウンロードしたファイルのダイジェスト） |
| Git ホストの marketplace 内の相対パス | インストールしたディレクトリの commit SHA |
| plugin も marketplace も git 管理外のローカルディレクトリ | `unknown` |
| `npm` | `unknown` |

- **`command` source** は常にコマンドの出力から版を導く（12 文字のハッシュ。manifest に `version` があれば `<version>-<hash>`）。entry の `version` は無視される
- **claude.ai でホストされた marketplace** の plugin は claude.ai が記録した版が使われ、manifest の `version` は読まれない
- **ローカルパスから追加した marketplace の in-place plugin** は、版の文字列に関係なく毎セッション現在のファイルを読む
- `~/.claude` を git 管理しているような「インストール先を囲むリポジトリ」から版は取らない

出典: [Plugin loading reference — How Claude Code computes the version](https://code.claude.com/docs/en/plugins/loading#how-claude-code-computes-the-version)

#### よくある落とし穴

> Because the manifest comes first, a manifest that pins `"version": "1.0.0"` keeps every user on the cached copy until its author changes the string, however many commits they push.
> — [Plugin loading reference — How Claude Code computes the version](https://code.claude.com/docs/en/plugins/loading#how-claude-code-computes-the-version)

**自動更新が有効でも、プラグイン作者が `plugin.json` の `version` を bump していない場合、新しい commit を push しても更新は走らない**。`claude plugin update` を実行して `<name> is already at the latest version (<version>).` が返るのに作者リポジトリの commit log に変更がある場合は、このケースに該当する可能性が高い。commit ごとに追従させたい場合は、manifest と marketplace エントリの両方から `version` を外す。

> **2026-10-11 更新**: 以前の引用元（旧 Plugins reference の "you must bump it every time..." の一文）は現行公式から消えたため、同じ趣旨の現行の一文に差し替えた。

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

- `extraKnownMarketplaces[*].autoUpdate` が `true` になっているか（未設定なら `/plugin` のトグルか既定値で決まる）
- `env` に `DISABLE_AUTOUPDATER` / `DISABLE_UPDATES` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` が含まれていないか（含まれていても `FORCE_AUTOUPDATE_PLUGINS=1` があれば plugin は更新される）
- シェル環境変数にも同じフラグが無いか（`env | grep -E "DISABLE_AUTOUPDATER|DISABLE_UPDATES|NONESSENTIAL|FORCE_AUTOUPDATE_PLUGINS"`）

#### 方法 C: 環境診断

```
/doctor
```

設定の異常を検出する。`DISABLE_*` 系が意図せず有効になっていれば警告が出る。

### 長期間ぶりに最新化する場合の推奨手順

一括更新のコマンドは無いため、marketplace 単位で更新する。

```
/plugin                             # Marketplaces タブで各 marketplace を選び「Update marketplace」
                                    # （カタログ更新 + その marketplace から入れた plugin を更新）
/reload-plugins                     # 反映（/plugin を閉じたときにも自動実行される）
```

シェルから行う場合は、カタログを refresh してから plugin ごとに更新する。

```bash
claude plugin marketplace update                  # 全 marketplace のカタログを refresh（plugin の版は変えない）
claude plugin update <plugin>@<marketplace>       # plugin ごとに更新
```

その後 `/plugin` で各プラグインのバージョンを確認すると、長期間更新されていないプラグインを特定できる。`command` source と `headersHelper` 付きの plugin は Update marketplace では更新されないため、Installed タブの個別画面か `claude plugin update` で更新する。

---

## マーケットプレイス

> 出典: [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) / [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference) / [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace) (2026-10-11時点)

マーケットプレイスは Plugin のカタログであり、Git リポジトリ（GitHub 以外の git ホストも可）、ホストした `marketplace.json` の URL、共有ファイルシステム上のディレクトリのいずれかでホストする。

> **「Claude Marketplace」とは別物**: claude.com/marketplace の **Claude Marketplace** は、plugin・コネクタ・パートナー製品・サービスパートナーを閲覧する Web サイトであり、`/plugin marketplace add` で追加する plugin marketplace ではない（公式 [Plugins overview — Get plugins from a marketplace](https://code.claude.com/docs/en/plugins/overview#get-plugins-from-a-marketplace) の明記）。

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
- **`url`**: `{"source": "url", ...}` — **汎用 git リポジトリ**（GitHub 以外のホスティングを含む）
- **`archive`**: `{"source": "archive", ...}` — **HTTPS 経由の zip アーカイブ**（後述）
- **`command`**（**v2.1.229〜**）: `{"source": "command", "command": "<cmd>", "timeout": <sec?>, "mode": "<copy|link?>"}` — ローカルコマンドを実行し、**その stdout が指すディレクトリ**をプラグイン本体として使う

> **source 型は計 7 種である**（2026-09-03 更新。以前は `url` と `archive` が抜けていた）: ローカルパス / `github` / `url` / `git-subdir` / `npm` / `archive` / `command`。

> **`command` source の性質（2026-08-16 追記）**
>
> | 項目 | 内容 |
> |---|---|
> | 解決タイミング | **セッションごとにバックグラウンドで 1 回再実行**される。したがって**内容を差し替えても再起動が不要** |
> | `command` | ASCII 500 文字以内 |
> | `timeout` | 秒数。**既定 60・最大 600** |
> | `mode` | `"link"` を指定するとコピーせず **in-place で利用**する |
> | ⚠️ バージョン固定 | 版は**常にコマンド出力のハッシュから導かれる**（manifest に `version` があれば `<version>-<hash>`、entry の `version` は無視）ため、`version` でピン留めできない |
> | 互換性 | v2.1.120〜228 では install に失敗し、それ以前では **marketplace 全体のロードに失敗**する。チームで配る場合は最低バージョンを揃える必要がある |
>
> **2026-10-11 訂正**: 以前は command を「`version` でピン留めできない唯一の source」と書いていたが、現行の manifest-reference によれば `version` でピン留めされないのは **command source・claude.ai でホストされた marketplace の plugin・ローカルパスから追加した marketplace の in-place plugin の 3 種**である。
>
> 出典: [Marketplace reference — command plugin source](https://code.claude.com/docs/en/plugins/marketplace-reference#command-plugin-source) / [Plugin manifest reference — version](https://code.claude.com/docs/en/plugins/manifest-reference#version) / [Plugin loading reference — When a command source re-runs](https://code.claude.com/docs/en/plugins/loading#when-a-command-source-re-runs) / CHANGELOG v2.1.229

> **GitLab の一級サポート（v2.1.232 / v2.1.233、2026-08-16 追記）**
>
> - marketplace が **`.git` の付かない `https://gitlab.com/...` のリポジトリ URL（ネストした subgroup を含む）を `github.com` と同様に clone** するようになった。`https://` を付けない `gitlab.example.com/team/plugins` のような書き方は `owner/repo` の短縮形として解釈されて失敗する。**2026-10-11 更新**: 以前は「公式ページに未反映で CHANGELOG が一次情報」としていたが、現行公式 [Plugin commands reference — plugin marketplace add](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-add) に掲載された
> - GitLab トークンの secret redaction を追加（`glrt-` / `gloas-` / `glptt-` / `glagent-` / `glimt-` / `glsoat-` / `glcbt-` / `glft-` / `glffct-`。`glpat-` / `gldt-` は全体を redaction）。`glab` CLI の設定ストアも `gh` と同等に保護される
> - **GitLab の Merge Request URL が `--worktree` と `claude agents` view に対応**（MR は `!N` 形式で表示、v2.1.233）
>
> 出典: CHANGELOG v2.1.232 / v2.1.233

`category` は任意で指定可能（例: `development`, `productivity`, `learning`, `security`）。

> **`metadata.pluginRoot`**（v2.1.239〜）: marketplace 全体で、素の名前で書いた相対 `source` を解決するベースディレクトリを指定できる。
>
> **`defaultEnabled` の優先順位**: marketplace エントリ側の `defaultEnabled` が、plugin.json 側の `defaultEnabled` より**優先**される。配布側（marketplace）で「インストール時は無効」を強制できる。
>
> **フォルダ衝突の警告**: manifest のキーと既定フォルダ（`commands/` 等）が衝突する場合、v2.1.140 以降は `claude plugin list` と `/plugin` の UI が `Default <folder>/ folder is ignored because the manifest sets "<key>"` と警告する。**2026-10-11 訂正**: 以前は `/doctor` でも警告されると書いていたが、現行公式 [Plugin manifest reference — How each key combines with its default location](https://code.claude.com/docs/en/plugins/manifest-reference#how-each-key-combines-with-its-default-location) が挙げるのは `claude plugin list` と `/plugin` だけである。
>
> **marketplace の予約名**: 公式・community・directory の名前（`claude-plugins-official`・`claude-community` など）は `github.com/anthropics/` 由来でない限り使えない。公式を装う名前、`inline` / `builtin` / `skills-dir` / `synced`、`claudeai-` で始まる名前なども予約されている。一覧は [Marketplace reference — Reserved names](https://code.claude.com/docs/en/plugins/marketplace-reference#reserved-names) を参照。

### マーケットプレイスの管理

```bash
/plugin marketplace add <source>           # マーケットプレイスを追加（owner/repo・git URL・marketplace.json の URL・ローカルパス）
/plugin marketplace update [name]          # Marketplaces タブを開く。名前を渡すとその marketplace を refresh（plugin も更新）
/plugin marketplace list                   # マーケットプレイス名の一覧
/plugin marketplace remove [name]          # 削除（そこから入れた plugin もアンインストールされる）
```

- **`/plugin marketplace` を引数なしで実行しても何も起きない**（`add` / `list` / `update` / `remove` のいずれかを付ける）。**2026-10-11 訂正**: 以前は引数なしで一覧が出ると書いていた
- **marketplace を削除すると、そこから入れた plugin がすべてアンインストール**され、`enabledPlugins` の記載・保存済みの `userConfig` とデータも消える。plugin を残したまま最新化したい場合は `update` を使う
- シェルでは `claude plugin marketplace add` / `list` / `update` / `remove` が同じ操作である

出典: [Install and manage plugins — Manage marketplaces](https://code.claude.com/docs/en/plugins/install#manage-marketplaces) / [Plugin commands reference — /plugin in a session](https://code.claude.com/docs/en/plugins/cli-reference#plugin-in-a-session)

### チームへの共有（extraKnownMarketplaces）

リポジトリの `.claude/settings.json` に `extraKnownMarketplaces`（**marketplace 名をキーにしたオブジェクト**）と `enabledPlugins` を設定すると、チームメンバーがそのフォルダを **trust した後に** marketplace が登録され、plugin が有効化される。シェルで一度 `claude plugin marketplace add your-org/your-marketplace --scope project` を実行し、書き込まれた `.claude/settings.json` を commit しても同じ状態になる。

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": { "source": "github", "repo": "company/claude-plugins-marketplace" }
    }
  },
  "enabledPlugins": {
    "code-formatter@company-tools": true
  }
}
```

- キーは marketplace 自身の `marketplace.json` の `name` である（リポジトリ名ではない）
- **未信頼のフォルダでは何のメッセージも無く無視される**。`-p` の非対話実行では、対話で trust 済みのフォルダ（または `~/.claude.json` の `hasTrustDialogAccepted`）でのみ適用される。trust ダイアログを出さない cloud session では登録されない
- marketplace 内の**相対パス**で載っている plugin はそのまま読まれるが、**外部 source**（plugin 自身の GitHub リポジトリ等）を指す entry は、各自が `claude plugin install <name>@<marketplace> --scope project` を実行するまで入らない（`Plugin "<name>" is enabled in project settings but isn't installed` が出る）

> **2026-10-11 訂正**: 以前の例は `extraKnownMarketplaces` を配列で書いていたが誤りで、公式はオブジェクト形式である。出典: [Manage Claude Code plugins for your organization — Require plugins per repository](https://code.claude.com/docs/en/plugins/org#require-plugins-per-repository) / [Host and maintain a marketplace — Register the marketplace for everyone in a repository](https://code.claude.com/docs/en/plugins/host-marketplace#register-the-marketplace-for-everyone-in-a-repository) / [Plugin loading reference — Plugins shared through a repository](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository)

### マーケットプレイスの作成から配布までの流れ

1. **Plugin を作成**: Skills・Hooks・Agents・MCP サーバーを含む Plugin を構築
2. **marketplace.json を作成**: Plugin のカタログを定義し、`claude plugin validate` で検証
3. **ホスティング**: GitHub・GitLab 等の Git ホストにプッシュ
4. **共有**: ユーザーが `/plugin marketplace add` でマーケットプレイスを追加し、`/plugin install` で個別の Plugin をインストール
5. **更新**: リポジトリに変更をプッシュ（`version` を pin しているなら上げる）。自前の marketplace は auto-update が既定 OFF のため、ユーザーが Marketplaces タブで auto-update を ON にするか管理者が managed 設定で `autoUpdate: true` にしない限り、ユーザーが `/plugin marketplace update <name>` か `claude plugin update <plugin>@<name>` を実行したときに届く
6. **リネーム・削除**: plugin の `name` を変えると既存のインストールが壊れる。表示名だけなら `displayName` を変え、`name` を変える・entry を消す場合は `marketplace.json` のトップレベル `renames`（旧名 → 新名、削除なら `null`）で既存ユーザーを移行させる（出典: [Host and maintain a marketplace — Rename or remove a plugin](https://code.claude.com/docs/en/plugins/host-marketplace#rename-or-remove-a-plugin)）

---

## claude.ai・Cowork と共通の Plugin

> 出典: [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support) / [Plugin loading reference — Plugins synced from claude.ai](https://code.claude.com/docs/en/plugins/loading#synced-plugins) / [Publish and distribute a plugin](https://code.claude.com/docs/en/plugins/publish) / [Publish to the directory](https://claude.com/docs/directory/publish) / [Build plugins for Claude](https://claude.com/resources/articles/build-plugins-for-claude) (2026-10-11時点)

同じ plugin フォルダを claude.ai の chat・Cowork・Claude Code のどこにでも入れられる。ただし **surface ごとに読み込むコンポーネントが違い**、読まないものは黙って飛ばされる（「インストール不可」のものは plugin 全体が拒否される）。

| コンポーネント | Chat | Cowork | Claude Code |
|---|---|---|---|
| Skills | 読む | 読む | 読む |
| Commands（`commands/*.md`） | skill として読み、合う場面で Claude が使う | 読む（`/plugin-name:command` で実行） | 読む |
| Agents・Hooks | 無視 | 読む | 読む |
| リモート MCP（`http` / `sse`） | plugin の Connectors タブで接続すれば使える | 読む | 読む |
| ローカル MCP（`.mcpb` を含む） | 無視 | Cowork セッションが手元の PC で動く場合に読む | 読む |
| トップレベルの `bin/` | **インストール不可** | **インストール不可** | 読む |
| LSP・output styles・themes・`settings` | 無視 | 無視 | 読む |

### claude.ai から同期される plugin（`<name>@synced`）

- **v2.1.273 以降**、claude.ai アカウントで有効にした plugin（組織がメンバー向けに有効にしたものを含む）は Claude Code にも **`<name>@synced`** として読み込まれる。marketplace もインストール記録も持たない
- ターミナルでは**起動ごとにバックグラウンドで 1 回同期**し、セッション中に変化があれば `Plugins changed. Run /reload-plugins to activate.` が出る
- **claude.ai アカウントでサインインしたセッションだけ**が同期する。`ANTHROPIC_AUTH_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` / `apiKeyHelper` で認証したセッション、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` を設定したセッション、bare mode・`--safe-mode`、`user` を含まない `--setting-sources` では同期しない
- **止め方**: 個別は `claude plugin disable <name>@synced` か `/plugin` の Installed タブ（ユーザー設定の `enabledPlugins` に `false` が書かれる）。マシン全体なら `syncClaudeAiPlugins: false`（ユーザー設定か managed 設定）。**組織が Required にした plugin は無効化できない**
- **逆方向には同期しない**: `/plugin` や `claude plugin install` で入れた plugin は claude.ai アカウントには追加されない

### Anthropic の directory への提出

- 提出は developer portal（[claude.ai/directory/manage](https://claude.ai/directory/manage)）で行い、**Pro / Max / Team / Enterprise の有料プランなら誰でも提出できる**（Free は不可）。Anthropic の審査を経て掲載される。旧 Claude Console のフォームは終了した
- **directory への desktop extension（MCPB）の掲載は deprecated** で、ローカル MCP サーバーを配るなら plugin bundle に含める
- directory から claude.ai で入れた plugin は、Claude Code には `<name>@synced` として届く。掲載用の `icon` 等のフィールドは前述の manifest 表を参照
- claude.com の対応表は、Claude Code 側の directory 閲覧を `/plugin directory`（v2.1.287〜）としている（code.claude.com の cli-reference のセッション内コマンド表には 2026-10-11 時点で載っていない）
- Anthropic は 2026-09-25 の記事で「**今後数週間で Claude と Claude Code の plugin の探索体験を 1 つに統合する**」と告知している。directory に掲載済みの skill・コネクタ・plugin は変更不要

---

## 組織での Plugin 管理

> 出典: [Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org) / [Manage plugins for your organization (claude.ai)](https://claude.com/docs/plugins/admin) / [Plugin security and trust](https://code.claude.com/docs/en/plugins/security) (2026-10-11時点)

組織が plugin を配る経路は 2 つある。

| 経路 | 対象 | 何ができるか |
|---|---|---|
| claude.ai の **Organization settings > Plugins & skills**（Team / Enterprise の Owner） | chat・Cowork（Claude Code にも `@synced` で同期） | plugin ごとに **Not available / Available to install / Installed by default / Required** を設定。Required は Claude Code でも外せない |
| Claude Code の **managed 設定**（server-managed / MDM / `managed-settings.json`） | Claude Code | `extraKnownMarketplaces` + `enabledPlugins` で marketplace 登録と plugin の事前インストール・強制有効化。managed は他スコープより優先され、ユーザーは無効化・削除できない |

- **コンテナ・CI**: ビルド時に `CLAUDE_CODE_PLUGIN_CACHE_DIR` を seed パスに向けて marketplace と plugin を入れ、実行時は `CLAUDE_CODE_PLUGIN_SEED_DIR` で指す。seed は read-only で clone せずに読まれ、`autoUpdate` は強制 OFF。seed の plugin も `enabledPlugins` で有効化が要る
- **許可・遮断**: `strictKnownMarketplaces`（許可リスト）と `blockedMarketplaces`（遮断リスト）は marketplace の **source** で照合する。エントリは `github`（`"owner/*"` の owner ワイルドカードは v2.1.223〜）・`git`・`url`・`file`・`directory` のほか、正規表現の **`hostPattern`**（`github` / `git` / `url` のホスト名に照合。`^...$` でアンカーする。GHES や GitLab 向け）と **`pathPattern`**（`file` / `directory` のパスに照合）、`@skills-dir` を残す `{ "source": "skills-dir" }` を使える
- **抜け道を塞ぐ**: managed の `disableSideloadFlags` で `--plugin-dir` / `--plugin-url` / `CLAUDE_CODE_PLUGIN_DIRS` を拒否し、`disableCommandPluginSources` で `command` source を止められる
- **更新ポリシー**: managed の `extraKnownMarketplaces` エントリに `autoUpdate` を書けば全員に強制される。`env` に `DISABLE_AUTOUPDATER` を置くと plugin の自動更新も止まり、`FORCE_AUTOUPDATE_PLUGINS` を足すと plugin だけ動かせる
- **名前による信頼区分**: marketplace は名前で official / community / third-party の 3 区分に分かれ、official と community の名前は `github.com/anthropics/` 由来のときだけ受理される。official 区分の名前は `claude-plugins-official`・`claude-code-marketplace`・`claude-code-plugins`・`anthropic-marketplace`・`anthropic-plugins`・`agent-skills`・`anthropic-agent-skills`・`life-sciences`・`knowledge-work-plugins`・`claude-for-legal`・`claude-for-financial-services`・`financial-services-plugins`・`first-party-plugins`・`claude-tag-plugins` の 14 個、community は `claude-community`・`claude-plugins-community`・`healthcare`

---

## Plugin の作成

### 手動作成

1. ディレクトリ構造を作成:

```bash
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/skills/my-skill
```

2. `plugin.json` を作成（manifest は任意だが、メタデータを付けるなら置く）:

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

公式 marketplace `claude-plugins-official` からインストールできる `plugin-dev` Plugin を使うと、対話的に Plugin を作成できる。skills・hooks・MCP サーバーなどのコンポーネントを書くための skill と agent、完成した plugin の検証機能が入っている。

> **2026-10-11 訂正**: 以前は `plugin-dev` を「本体に同梱」と書いていたが、公式 [Create a plugin](https://code.claude.com/docs/en/plugins/create) は `claude-plugins-official` からインストールするものとしている。

```bash
/plugin install plugin-dev@claude-plugins-official

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

### `claude plugin eval` で効果を測る（v2.1.269〜）

`claude plugin eval` は、plugin の **eval ケース（利用者が打ちそうなプロンプト + 1 つ以上の grader）** を実行して採点するシェルコマンドである。grader は返答への正規表現、特定ツールの呼び出し有無、別モデルが rubric で判定する judge などの合否チェックである。

```bash
claude plugin eval init        # plugin について質問し、ケースと grader を提案・試走して evals/ に書き出す
claude plugin eval .           # 全ケースを実行して採点（結果は evals/results/ の report.html にも出る）
```

- **plugin なし（baseline）と比較する**: 各ケースは対象 plugin だけを読み込んだ隔離された非対話セッションで実行され、既定で plugin なしでも同じ回数実行される。`WITH` と `W/OUT` のスコア差 `Δ` が plugin の寄与である。両方 1.0 なら plugin は効いていない
- **既定は 1 ケース 3 回**（`--runs`）。同時実行は `-j, --concurrency`（1〜8、既定 1）
- **対象**: plugin ディレクトリ、単一の `prompt.md` / `case.yaml`、インストール済みの `name` / `name@marketplace`、`name@skills-dir`。eval ケースの置き場所は既定 `evals/` で、manifest の `experimental.evals` か `--eval-dir` で変えられる
- **前提**: manifest（`plugin.json` か `.claude-plugin/plugin.json`）を持つ plugin ディレクトリか skills-directory plugin。git が入っているなら 2.31 以降
- ⚠️ **実行ごとに課金される**: eval の各実行・judge grader・`eval init` はすべて実際のモデル呼び出しで、プランの利用枠か API 料金に計上される。ケース数 × 回数の実行が plugin あり・なしの 2 系統で走る
- skill-creator の eval（`evals/evals.json`）とは別形式で、互いのケースファイルは読まない

出典: [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) / [Plugin commands reference — plugin eval](https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval) / [Week 37](https://code.claude.com/docs/en/whats-new/2026-w37)

---

## ベストプラクティス

### Plugin 構造

- **標準のディレクトリ構造に従う**: manifest は任意だが、置くなら `.claude-plugin/plugin.json` に置き、`skills/` などのコンポーネントは `.claude-plugin/` の中ではなく plugin ルートに置く（**2026-10-11 訂正**: 以前は manifest を必須のように書いていたが、冒頭の注記どおり任意である。ただし `claude plugin eval` の対象にするには manifest が要る）
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

- **`/plugin` パネルを閉じると、パネル内で行った変更に対して `/reload-plugins` が自動で実行される**。別のターミナルで `claude plugin` を実行した場合など、パネル外の変更は自分で `/reload-plugins` を打つ
- **prompt cache を壊す reload は保留される**: plugin の MCP サーバーや `LSP` ツールが増減する reload は、次のメッセージで会話全体を読み直すことになるため適用されず、警告が出る。承知のうえで適用するなら **`/reload-plugins --force`**
- **非対話の環境でも動く**（v2.1.260〜）: Desktop・Agent SDK・`-p` でも、自分で打った場合に限り実行される（Remote Control や Slack 経由では拒否）。この場合 plugin の MCP サーバーの接続・切断は次のセッションまで反映されない

出典: [Plugin commands reference — /reload-plugins](https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins)

**v2.1.221 以降は `/reload-plugins` 自体が不要になる場面が増えた**:

- `/plugin` からインストールした plugin は、**安全と判断できる場合に即時有効化**される（従来は常に `/reload-plugins` が必要だった）
- `/plugin install` は「plugin not found」を返す前に、**stale な marketplace カタログを更新して再試行**するようになった
- plugin が `skills` パスに **`"."` を受理**するようになり、root-level `SKILL.md` の検証エラーも plugin root を使うよう案内する

> ✅ **この不具合は v2.1.246 で修正済み**（2026-09-03 更新）。CHANGELOG は「Fixed `/reload-plugins` reporting 0 skills for plugins that define skills under `skills/*/SKILL.md`」と記載しており、**現在は skills 件数を信用してよい**。
>
> （旧記述: 「`/reload-plugins` のサマリに出る skills 件数は `commands/` ディレクトリのみを数えている。`skills/` を編集しても `0 skills` と表示され得るため、この数字でスキルの読み込みを判断しない」。**v2.1.246 未満を使っている場合のみ当てはまる**）

出典: CHANGELOG v2.1.221 / CHANGELOG v2.1.246

### Managed スコープ

組織の管理者がマネージド設定で Plugin をインストールした場合、`managed` スコープとなる。ユーザーは変更・削除できない（`/plugin` の Installed タブに Managed として表示される）。配り方・制限のかけ方は [組織での Plugin 管理](#組織での-plugin-管理) を参照。

### 公式 Plugin

Anthropic は汎用の plugin marketplace を 3 つ公開している。

| 区分 | marketplace 名（`@` の後ろに書く名前） | リポジトリ | 入手方法 |
|---|---|---|---|
| 公式 | `claude-plugins-official` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 初回の対話起動時に自動で追加される |
| community | `claude-community` | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | `/plugin marketplace add anthropics/claude-plugins-community` |
| demo | `claude-code-plugins` | [anthropics/claude-code](https://github.com/anthropics/claude-code) の `plugins/` | `/plugin marketplace add anthropics/claude-code` |

`plugin-dev` は Plugin 開発を支援する公式ツールキットで、公式 marketplace から入れる。公式 marketplace の中身は `/plugin` の Discover タブか、Web の [Claude Marketplace](https://claude.com/marketplace/plugins) で閲覧できる。

> **2026-10-11 訂正**: 以前は「anthropics/claude-code の `plugins/` に公式 Plugin が含まれている」と書いていたが、そこは **demo marketplace**（`claude-code-plugins`）であり公式 marketplace ではない（ただし名前による信頼区分では `claude-code-plugins` も official tier に入る。[Plugin security](https://code.claude.com/docs/en/plugins/security) の official marketplace names。区分が official でも、用途は例示用の demo である）。出典: [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces)

**security-guidance plugin（公式）**: Claude のコード変更を脆弱性観点でレビューし、その場で修正する公式 Plugin。3 段構成で動作する — 編集ごとの高速パターンチェック → ターンごとのモデルレビュー → commit/push 時の深いエージェントレビュー。プロジェクト固有のルールは `.claude/claude-security-guidance.md` に置く。

```bash
/plugin install security-guidance@claude-plugins-official
```

> 出典: [Security guidance](https://code.claude.com/docs/en/security-guidance)

**Claude Security plugin（公式・別物）**: `security-guidance` とは**別のプラグイン**で、こちらは**多エージェントによる本格的な脆弱性スキャン**を行う。

```bash
/plugin install claude-security@claude-plugins-official
# 実行
/claude-security
```

| 論点 | 内容 |
|---|---|
| 動作 | **脅威モデルの作成 → 脆弱性の探索 → 独立したエージェントによる検証**という多段構成 |
| 対象範囲 | リポジトリ全体、ブランチの差分（base に無い commit）、open な PR、単一の commit。大きなリポジトリは領域を絞って走らせる |
| 出力 | `CLAUDE-SECURITY-<timestamp>/` ディレクトリに、レポート（`.md`）・機械可読の `.jsonl`・**SARIF 2.1.0 の `.sarif`**（GitHub code scanning 等向け）・対象 commit を記録した revision stamp を書き出す |
| **patch の適用** | **自動では適用されない**。シェルで `git apply` するか、Claude に適用と PR 作成を頼む（1 patch 1 PR を推奨） |
| 前提 | 有料プラン・Anthropic API・サードパーティプロバイダ（Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry）のいずれか（scan が dynamic workflows を使うため。Pro は `/config` の Dynamic workflows で有効化）、**Python 3.9 以降**（`python3`。標準ライブラリのみ使用）、差分スキャンと patch 作成には Git |

> **2026-10-11 訂正**: 以前は前提を「Python 3.9.6 以上と dynamic workflows（v2.1.154+）」、patch を「必ず人間が適用する」と書いていた。現行公式は Python 3.9 以降、利用経路（有料プラン / API / サードパーティ）を前提とし、Claude に適用を頼むこともできるとしている。

> `security-guidance` が「編集のたびに軽くチェックする常駐型」であるのに対し、`claude-security` は「腰を据えて監査する多エージェント型」である。**検証を独立エージェントに分離している**点は [harness.md](harness.md) の検証ループ設計と同じ思想である。
>
> 出典: [Claude Security](https://code.claude.com/docs/en/claude-security)

### Themes（プラグインコンポーネント）

プラグインは **themes/**（`experimental.themes` で宣言）でターミナルのテーマを配布できる。2026-08-12 時点で本ドキュメントは詳細を扱わない。仕様は [Add components to a plugin — Themes and output styles](https://code.claude.com/docs/en/plugins/components#themes-and-output-styles) を参照。

---

## 関連ドキュメント

- [Plugins overview](https://code.claude.com/docs/en/plugins/overview) — Plugin の概要・marketplace・インストールスコープ
- [Create a plugin](https://code.claude.com/docs/en/plugins/create) / [Add components to a plugin](https://code.claude.com/docs/en/plugins/components) — 公式 Plugin 作成ガイド
- [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference) — `plugin.json` の全フィールド
- [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) — CLI コマンドリファレンス（`claude plugin` / `/plugin` / `/reload-plugins`）
- [Install and manage plugins](https://code.claude.com/docs/en/plugins/install) — Plugin のインストール・管理
- [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading) — ロード元・スコープ・バージョンと更新の規則
- [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) / [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference) / [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace) — マーケットプレイスの作成・配布
- [Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org) — 組織での配布・制限
- [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) — `claude plugin eval`
- [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support) — claude.ai・Cowork・Claude Code の対応表
- [Mods ガイド](mods.md) — plugin の hooks module（mods）
- [ClaudeCode Hooks ガイド](hooks.md) — settings ファイルに書くフック
- [ClaudeCode Skills ガイド](skills.md) — Skills の詳細（Plugin 内 Skills にも適用）
- [ClaudeCode のベストプラクティス](best-practices.md) — ClaudeCode 全般のベストプラクティス
