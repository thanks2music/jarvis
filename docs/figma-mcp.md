# Figma MCP の認証とアカウント切り替え

> 出典: [Rate limits & access — Figma Developers](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/) / [Set up the remote server — Figma Developers](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/) / [Set up the desktop server — Figma Developers](https://developers.figma.com/docs/figma-mcp-server/local-server-installation/) / [figma/mcp-server-guide](https://github.com/figma/mcp-server-guide) / [MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp) / [CLI reference — Claude Code Docs](https://code.claude.com/docs/en/cli-reference)（2026-11-07 確認。Claude Code v2.1.318 と公式 `figma` plugin v2.2.157 で実測）

公式 `figma` plugin の MCP サーバー（remote server）について、次の 3 点をまとめる。

- どの Figma アカウントで、どのファイルを読めるか
- Figma アカウントを切り替える手順
- 「`claude mcp list` では Connected なのに、セッションで Figma のツールが使えない」ときの直し方

Figma MCP の機能、プラン条件、他の AI デザインツールとの比較は [ai-design-tools.md](ai-design-tools.md) の §4 で扱う。

## 要点

- 公式 plugin の Figma MCP は **OAuth** で Figma アカウントにサインインする。API キーは使わない
- 読めるのは、**サインイン中のアカウントがアクセスできるファイルだけ**である
- **同時に使える Figma アカウントは 1 つ**。切り替えは `claude mcp logout` → `claude mcp login`（手順は §3、理由は §2）
- 今どのアカウントでサインインしているかは、`whoami` で確かめる（§1.3）
- claude.ai 側に Figma のコネクタがあると、未接続でもセッションから Figma のツールが消える。`deniedMcpServers` で直す（§4）

## 1. 認証の仕組み

### 1.1 API キーではなく OAuth

plugin に同梱されている `.mcp.json` は、URL とヘッダーしか持たない。認証情報を書く欄は無い。

```json
"figma": {
  "type": "http",
  "url": "https://mcp.figma.com/mcp",
  "headers": { "X-Figma-Plugin-Bundle": "figma_prod@2_2_157" }
}
```

初めて接続するときにブラウザが開く。そこで Figma にサインインし、**Allow access** を押して許可する（Figma の remote server のセットアップ手順による）。Figma が公開している Gemini CLI 向けの設定にも `"oauth": { "enabled": true }` とある。トークンは Claude Code が保存し、期限が来ると自動で更新する（"Authentication tokens are stored securely and refreshed automatically"）。

### 1.2 読めるファイルと呼び出し回数の上限

Figma 公式の記述は次のとおり。

> "You can only use the MCP server with Figma files you already have access to."
> "Check your access. Make sure that account belongs to the plan that owns the file."

呼び出し回数の上限は、seat とプランの種類の組み合わせで決まる。プラン × seat の全表は [ai-design-tools.md §4.4](ai-design-tools.md#44-figma-mcp-サーバー) にある。

### 1.3 今のアカウントを確かめる — `whoami`

Figma は `whoami` を次のように説明している。"It shows the email you're signed in with, your plans, and your seat on each plan." `whoami` は呼び出し回数の上限に数えられない。

セッションの中なら、「Figma の whoami を実行して」と頼めばよい。シェルからは、次の 1 回の実行で、今のアカウントと §4 の問題の有無をまとめて確かめられる。

```bash
cd /tmp && claude -p "Call the mcp__plugin_figma_figma__whoami tool once and print its raw result." \
  --allowedTools "mcp__plugin_figma_figma__whoami" \
  --model haiku --debug-file /tmp/figma-mcp-debug.log
grep -E 'Lazy dedup|Suppressing claude.ai connector' /tmp/figma-mcp-debug.log
```

- `cd /tmp` は、プロジェクトの CLAUDE.md を読み込ませないためである。plugin が user scope で有効なら、どのディレクトリからでも使える
- `--model haiku` でも MCP ツールを呼べた（実測）。確認だけなら小さいモデルで足りる
- `grep` で Figma を含む行が出たら、§4 の問題が起きている
- ⚠️ **プロンプトは `--allowedTools` より前に書く**。`--allowedTools` は値を複数受け取る。そのため後ろに置いたプロンプトまでツール名として読まれ、`Error: Input must be provided either through stdin or as a prompt argument when using --print` で止まる（実測）

返り値の形は次のとおり（値は伏せている）。上限は `plans[].seat` と `plans[].tier` の組み合わせで決まる。`tier` が `starter` なら、seat に関係なく月 20 回までになる。`tier` は実測で `starter` / `pro` / `org` / `student` が返った。Education プランは `student` になる。

```json
{"whoami":{"email":"<サインイン中のメールアドレス>","plans":[{"name":"<チーム名>","seat":"Full","tier":"pro","key":"team::<id>","role":"admin"}]}}
```

### 1.4 API キーで動く Figma MCP と混同しない

API キー（Personal Access Token、PAT）で動く Figma MCP は、公式 plugin とは別のサーバーである。たとえばサードパーティ製の Framelink（`figma-developer-mcp`）は、PAT を `--figma-api-key` か環境変数 `FIGMA_API_KEY` で受け取る。本リポジトリの環境では、一部のプロジェクトにだけ local scope で登録している（[tool-stack.md](tool-stack.md)）。

local scope の登録は、`claude mcp list` では今いるディレクトリの分しか表示されない（[mcp-setup.md のスコープの使い分け](mcp-setup.md#スコープの使い分け)）。登録しているプロジェクトをすべて探すには、次のように実行する。

```bash
jq -r '.projects | to_entries[] | select((.value.mcpServers // {}) | tostring | test("figma-developer-mcp")) | .key' ~/.claude.json
```

`--figma-api-key=...` のように引数で渡すと、PAT が `~/.claude.json` に平文で残り、プロセス一覧（`ps`）にも表示される。環境変数で渡す方がよい。Framelink の SECURITY.md も "Use environment variables for secrets" としている。

## 2. 同時に使える Figma アカウントは 1 つ

同じサーバーが複数の場所で定義されたときの優先順位と、重複の判定方法は [mcp-setup.md](mcp-setup.md#同じサーバーが複数の場所にあるとき) にまとめた。Figma に当てはめると、次のようになる。

- サインインはサーバーの定義ごとに 1 つで、`claude mcp login <name>` も名前で指定する。`plugin:figma:figma` が持てるのは 1 アカウント分である
- plugin と同じ URL のサーバーを local / project / user scope に足すと、plugin の方が重複として外れる。plugin と並べて 2 本目を持つことはできない
- 同じ URL を local / project / user scope に別名で 2 つ登録すると、両方が残る可能性はある。ただし、2 つのサインインが別々に保存されるかは未確認である（末尾参照）。この構成には頼らない

Figma 側も "Usually, each person signs in to Figma separately to use the MCP server." としており、1 人が複数のアカウントを同時に使う構成は想定されていない。

## 3. アカウントを切り替える手順

切り替える前に、§4 の問題が起きていないことを確かめる。起きていると、切り替えてもセッションで Figma のツールが使えない。

```bash
# 1. ブラウザで figma.com に、切り替え先のアカウントでログインしておく
# 2. 今のサインインを消す
claude mcp logout plugin:figma:figma
# 3. サインインし直す（ブラウザが開く）
claude mcp login plugin:figma:figma
# 4. 承認画面に表示されたアカウントが切り替え先であることを確かめてから "Allow access" を押す
# 5. §1.3 のコマンドで whoami を実行し、メールアドレスと seat を確かめる
```

- サーバー名は、plugin の scoped name である `plugin:figma:figma` を使う。docs には "The server itself registers under the scoped name `plugin:<plugin-name>:<server-name>`" とある
- セッションの中からなら、`/mcp` で `plugin:figma:figma` を選び、**Clear authentication** の後に **Authenticate** を選んでも同じ操作になる
- `logout` / `login` の詳しい挙動と、ブラウザが開かない環境で使う `--no-browser` は、[mcp-setup.md の MCP 管理コマンド一覧](mcp-setup.md#mcp-管理コマンド一覧) を参照
- 切り替えると、元のアカウントでしか開けないファイルは読めなくなる。戻すときは、同じ手順を元のアカウントで行う

> **実測（2026-11-07）**: 業務用のアカウントから個人用のアカウント（Education プラン）に切り替えた。新しいセッションで `whoami` が個人用のアカウントを返し、個人用チームのデザインファイルの node を `get_metadata` で取得できた。

## 4. トラブル: Connected なのにセッションで Figma のツールが使えない

`claude mcp list` は `plugin:figma:figma: https://mcp.figma.com/mcp (HTTP) - ✔ Connected` と表示する。ところがセッションの中には、`mcp__plugin_figma_figma__*` が 1 つも無い。§1.3 の `grep` で次の行が出れば、claude.ai の Figma コネクタとの重複が原因である。

```
[MCP] Lazy dedup: suppressing ... plugin server(s) that duplicate claude.ai connectors: plugin:figma:figma
Suppressing claude.ai connector "claude.ai Figma": duplicates manually-configured "plugin:figma:figma"
```

`~/.claude/settings.json` の `deniedMcpServers` に、コネクタを名前で追加すれば直る（実測）。

```json
{
  "deniedMcpServers": [
    { "serverName": "claude.ai Figma" }
  ]
}
```

原因の詳細、`serverUrl` で指定してはいけない理由、他の止め方、claude.ai 側でコネクタを削除してはいけない理由は、[mcp-setup.md](mcp-setup.md#plugin-と-connector-が同じ-url-だと両方とも使えなくなる) にまとめた。Notion など、Figma 以外の plugin でも同じことが起きる。

## 5. 業務用と個人用を両方使いたいとき

| 方法 | やり方 | 注意点 |
|---|---|---|
| **A. 切り替える**（推奨） | §3 の手順 | 2 つのアカウントを同時には使えない |
| **B. desktop server を併用する** | `claude mcp add --transport http --scope user figma-desktop http://127.0.0.1:3845/mcp`。URL が違うため、remote と重複扱いにならない | 要件は [ai-design-tools.md §4.4](ai-design-tools.md#44-figma-mcp-サーバー) を参照。キャンバスへの書き込みはできない。どのアカウントで動くかは未確認（末尾参照） |
| **C. 一方のアカウントを、もう一方のチームに招待する** | 1 つのアカウントで、両方のファイルを開けるようにする | 招待先での seat が View / Collab なら、上限は月 20 回になると考えられる（未確認。末尾参照） |

## 出典

| 情報源 | URL / 取得元 |
|---|---|
| Rate limits & access — Figma Developers | https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/ （2026-11-07 確認。全表は ai-design-tools.md §4.4） |
| Set up the remote server — Figma Developers | https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/ （2026-11-07 確認） |
| Set up the desktop server — Figma Developers | https://developers.figma.com/docs/figma-mcp-server/local-server-installation/ （2026-11-07 確認） |
| `figma/mcp-server-guide` | Context7 経由で確認（2026-11-07。`.mcp.json` と `gemini-extension.json`） |
| MCP — Claude Code Docs | https://code.claude.com/docs/en/mcp （2026-11-07 確認。優先順位・重複判定・OAuth の保存・claude.ai コネクタ） |
| CLI reference — Claude Code Docs | https://code.claude.com/docs/en/cli-reference （2026-11-07 確認。`claude mcp login` / `logout`） |
| `GLips/Figma-Context-MCP`（Framelink） | Context7 経由で確認（2026-11-07。`FIGMA_API_KEY` と SECURITY.md） |
| 公式 `figma` plugin の同梱ファイル | `~/.claude/plugins/cache/claude-plugins-official/figma/2.2.157/`（2026-11-07 実測。`.mcp.json` と README） |
| 重複抑止のログ | `claude -p ... --debug-file` の出力（2026-11-07 実測、v2.1.318） |

### 確認できなかった事項

- 複数のプランに属するアカウントで、どのプランの seat が上限に使われるか。Figma は「ファイルを持つプランにアカウントが属していること」としか書いていない
- 同じ URL を local / project / user scope に別名で 2 つ登録したときに、2 つのサインインが別々に保存されるか（§2）
- desktop server がどのアカウントで動くか
- §4 の重複抑止が既知の不具合かどうか。changelog と issue は確認していない
