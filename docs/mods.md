# ClaudeCode Mods ガイド

> 出典:
> - [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)（全体像・組込み mod・動作環境。2026-10-11時点）
> - [Create a mod](https://code.claude.com/docs/en/plugins/mods/create)（`/plugin-authoring` で書かせる手順・自分で書く手順・validate）
> - [React to events with a mod](https://code.claude.com/docs/en/plugins/mods/events)（`tool.call` / `tool.check`・実行順・失敗時の扱い）
> - [Draw in the interface with a mod](https://code.claude.com/docs/en/plugins/mods/interface)（pane / band / 既存の描画の差し替え・state）
> - [Use the mods API](https://code.claude.com/docs/en/plugins/mods/api)（コマンド・ツール・モデル呼び出し・ファイル / プロセス / ネットワーク）
> - [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference)（イベント・API・render site・上限・設定キーの一覧。v2.1.290 時点の記載）
> - [Test a mod](https://code.claude.com/docs/en/plugins/mods/test)（`claude plugin test` と test kit）
> - [Troubleshoot a mod](https://code.claude.com/docs/en/plugins/mods/troubleshoot)（読み込まれない・拒否される・描画されない原因）
> - [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin)（既定の挙動・組込みガード・managed settings）
> - [Interface gallery for mods](https://code.claude.com/docs/en/plugins/mods/gallery)（描画できる要素の見本）
> - [Configure permissions — Extend permissions with hooks](https://code.claude.com/docs/en/permissions#extend-permissions-with-hooks)（mod の `tool.check` が覆せる判定・覆せない判定）
> - [Customize Claude Code with mods](https://claude.com/resources/articles/claude-code-mods)（2026-10-01、発表記事）
> - [Changelog](https://code.claude.com/docs/en/changelog)（v2.1.287 に "Added Claude Mods"）
>
> 最終更新: 2026-10-11（ClaudeCode v2.1.296 時点）

**Mods** は、plugin に同梱して配る **JavaScript / TypeScript の関数 hook** である。plugin の `hooks/hooks.json` の `modules` に指定したファイル（**hooks module**）を、ClaudeCode が**自分のプロセス内**で実行する。ClaudeCode はツール呼び出し・プロンプト送信・画面の描画などのたびにイベントを発し、mod の関数はそのイベントの**前・後・代わり**に処理を差し込める（公式記事によれば、前後を包むこともできる）。公式記事は「hooks ではイベントの書き換え・新しい UI の描画・機能の置き換えができなかったが、mods はできる」と位置づけている。mod でできることの例:

- ツール呼び出しの**書き換え・ブロック・再試行**、ツールを実行せずに結果を返す肩代わり、プロンプトの**書き換え・破棄**
- 権限判定の**上書き**（`tool.check` で `allow` / `ask` / `deny` を返す）
- transcript 横の pane や prompt 上の band など **UI の追加**、スピナーやツール呼び出し行など **ClaudeCode 自身の描画の差し替え**
- Claude のターンを介さずに即実行される `/command` の追加

**必要な版**: ターミナルの CLI は v2.1.287 以降、Desktop アプリの Code タブは v2.1.286 以降で、**既定で ON** である（公式 docs の記載。CHANGELOG も v2.1.287 に "Added Claude Mods" と記す）。`/diff` のパネルや `AGENTS.md` の読み込みなど、ClaudeCode 自身の機能の一部もすでに mod として実装されている（[3. 組込み mod](#3-組込み-mod)）。

> **用語**: 公式の mods ページは、mod の関数を「hook」、settings ファイルや plugin の `hooks/hooks.json` の `hooks` に書く従来のフック（[Hooks ガイド](hooks.md)）を「**settings hook**」と呼び分けている。本ドキュメントもこの呼び方に従う。

---

## 前提知識

### settings hook・plugin・mod の関係

mod は plugin の一種である。plugin は skill・MCP サーバー・settings hook・mod をまとめて入れられる入れ物で、`hooks/hooks.json` に `modules` キーがあることが「その plugin が mod を含む」ことの目印になる。同じ `hooks.json` に settings hook（`hooks` キー）を併記してもよい。

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json        ← plugin の manifest（mod 用の必須フィールドは無い）
├── skills/                ← 任意: skill
├── .mcp.json              ← 任意: MCP サーバー
└── hooks/
    ├── hooks.json         ← "modules": [...] で hooks module を指す。"hooks" に settings hook も書ける
    └── register.js        ← hooks module（mod の本体）
```

settings hook は mods の登場後も従来どおり動き、非推奨にはなっていない（[Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) の記載）。

### mod / settings hook / Skill / MCP サーバーの比較

公式の比較表をもとに、権限判定の行を足した。既存の settings hook・skill・MCP サーバーで足りるなら、mod を書く前にそちらを検討するよう公式は勧めている。

| 観点 | mod | settings hook | Skill | MCP サーバー |
|---|---|---|---|---|
| 実体 | plugin 内の関数。ClaudeCode が**自分のプロセス内**で呼ぶ | ライフサイクルイベントで実行されるシェルコマンド・HTTP リクエスト・prompt | Claude が読む指示（`SKILL.md`） | Claude にツールを渡す外部プロセス・サービス |
| 変えられるもの | ツール呼び出し・プロンプト・コマンド・ターン・画面の描画 | ツール呼び出しやプロンプトを通すか否か、ツールの引数と結果、Claude への追加コンテキスト | Claude が知っていること・やること | Claude が使えるツール |
| 画面に描画できるか | できる | できない | できない | できない |
| 書くもの | JavaScript / TypeScript | スクリプト + `settings.json` のエントリ | Markdown | 任意の言語のサーバー |
| 権限判定を緩められるか | `tool.check` で緩められる（[2.2](#22-権限判定への影響toolcheck)） | 緩められない。`PreToolUse` が `allow` を返しても deny ルール・ask ルールが優先する | — | — |
| 選ぶ場面 | pane・prompt 上の band・独自コマンドが欲しい、イベントを書き換えたい | 手元のスクリプトでイベントをブロック・許可・記録したい | 同じ指示を何度もチャットに貼っている | Claude が外部システムに届く必要がある |

---

## 1. 仕組み

### 1.1 ファイル構成

最小の mod は 3 ファイルである。Node.js・バンドラ・ビルド工程は要らない（ClaudeCode が `.js` / `.ts` を直接読み込む）。

| ファイル | 必須 | 内容 |
|---|---|---|
| `.claude-plugin/plugin.json` | 必須 | plugin の manifest。mod のために足す必須フィールドは無い |
| `hooks/hooks.json` | 必須 | `modules`: hooks module へのパスを 1 つ持つ配列（`hooks.json` からの相対パス）。`hooks` に settings hook も書ける |
| hooks module（例 `hooks/register.js`） | 必須 | mod の入口。`register(on, options)` を export する ES module。拡張子は `.js` / `.mjs` / `.cjs` / `.jsx` / `.ts` / `.mts` / `.cts` / `.tsx` |
| `types/index.d.ts`（manifest の `types` で指定） | `$.state` を使う、または mods API に namespace を足すとき | `PluginState` の値や追加する namespace の宣言 |
| `*.test.ts` / `*.test.tsx` | 任意 | `claude plugin test` が実行するテスト |

```json
{
  "description": "The first-mod hooks module",
  "modules": ["./register.js"]
}
```

`register` の第 2 引数 `options` には、manifest の `userConfig` で宣言した値（既定値を補完済み）が入る。

### 1.2 hook 関数とイベントの扱い

hooks module は `register(on)` の中で `on(イベント名, [matcher], hook)` を呼んで hook を登録する。hook は `async ($, e, next) => ...` の形で、3 つの引数を受け取る。

| 引数 | 内容 |
|---|---|
| `$` | **mods API**。描画・コマンド追加・モデル呼び出し・ファイル / プロセス / ネットワークへのアクセスはすべてここを通す |
| `e` | イベントの入力（深く freeze されたデータ）。変えるときはコピーを `next` に渡す |
| `next(e)` | 次のハンドラ。同じイベントの hook はミドルウェアのチェーンになっており、最後の `next` が ClaudeCode 自身の処理に届く |

hook がイベントに対してできることは 3 つである。

| 動作 | やり方 | 例 |
|---|---|---|
| 観察（Observe） | 記録だけして `next(e)` をそのまま返す | ツール呼び出しを数える |
| 書き換え（Rewrite） | 変更した `e` のコピーを `next` に渡す | スピナーの文言に件数を足す |
| 肩代わり（Answer） | `next` を呼ばずに自分で結果を返す。本来の処理は動かない | コマンドを拒否する |

公式 events ページの例を短く示す。`git push --force` を含む Bash 呼び出しを、権限プロンプトを出さずに拒否し、理由を Claude に返す。

```javascript
on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
  if (/git push .*--force/.test(e.command)) {
    // next を呼ばずに返すので、コマンドは実行されない
    return { deny: 'Force pushes are not allowed in this repository. Push to a new branch instead.' }
  }
  return next(e) // それ以外は通常どおり権限チェック → 実行へ
})
```

hook がファイル・プロセス・ネットワークに触れる手段は mods API だけである。そのため ClaudeCode は、コードを実行しなくても「その mod がどのイベントを受け、どの API を呼ぶか」を静的解析で一覧できる（[2.3](#23-導入前の確認claude-plugin-validate)）。逆に、静的解析で読めない書き方（`$` を変数に代入する、イベント名を変数で渡す、dynamic `import()` など）をした mod は読み込みを拒否される。

### 1.3 主なイベント

全イベントは [Mods reference — Events](https://code.claude.com/docs/en/plugins/mods/reference#events) にある。代表的なものだけ挙げる。

| 分類 | イベント | できること |
|---|---|---|
| ツール | `tool.call` | ツール実行の直前に呼ばれる（subagent や MCP ツールの呼び出しも含む）。拒否（`{ deny }`）、引数の変更、再試行、実行せずに結果を返す（`{ result }`）、実行後に結果を Claude から伏せる、ができる |
| ツール | `tool.check` | 権限ルール・permission mode・`PreToolUse` hook が出した判定を受け取り、`allow` / `ask` / `deny` を返し直す |
| ツール | `tool.describe` | Claude に送るツール説明の書き換え、tool search の後ろに回すかの指定 |
| プロンプト | `prompt.submit` / `prompt.section` / `prompt.context` など | 送信されたプロンプトの書き換え・破棄（`{ drop }`）、system prompt の節の差し替え |
| コマンド | `command.run` | 登録した `/command` を Claude のターン無しで即実行する（Claude が作業中でも動く） |
| ターン | `turn.start` / `turn.step` / `turn.complete` | 1 リクエストごとにモデルや effort を差し替える、など |
| セッション | `session.start` / `session.end` / `session.append` など | コマンド・ツールの登録、会話の各行を保存前に書き換える |
| subagent | `agent.spawn` / `agent.offer` | subagent・teammate の起動の拒否やモデル指定 |
| 描画 | `ui.render` / `ui.press` / `ui.input` / `ui.select` | render site に描くものを返す、ボタンや入力欄の操作に応じる |
| 他の mod | `plugin.register` | 他の mod の読み込み直前に、その mod が使うイベント・API を見て拒否する（組織のポリシー mod 向け） |
| settings hook | `classic.<Event>`（例 `classic.Stop`） | settings hook のイベントを受ける。`e` は settings hook の stdin JSON と同じ |
| mods API 呼び出し | `fs.read` / `model.complete` / `ui.open` など | 後ろで動く mod の API 呼び出しを横取りし、記録・拒否する |

### 1.4 実行順

同じイベントに複数の mod が hook していれば 1 本のチェーンになる。先頭の mod が最も外側で、イベントを最初に見て、結果を最後に見る。後ろの mod は前の mod がイベントを見るのを止められない。ClaudeCode は出どころでチェーンを並べる。

| 順 | 何が並ぶか |
|---|---|
| 1 | 組込みガード `sec-default@builtin`（読み込まれる環境のみ）、managed の `prependPlugins` に載せた mod、その他の「組織の mod」（`appendPlugins` に載せたものを除く） |
| 2 | ユーザーがインストールした mod（manifest の `dependencies` に挙げた mod より先に動く） |
| 3 | managed の `appendPlugins` に載せた mod |
| 4 | その他の組込み mod |

settings hook の `PreToolUse` は、チェーンの決まった位置で動く。

- **managed settings の `PreToolUse`**: 最初の mod の `tool.call` より前に動き、そのブロックは**最終**である（どの mod もその呼び出しを見ない）。mod が呼び出しを書き換えた場合も、書き換え後の呼び出しに対して再度動く
- **それ以外の settings ファイルと plugin の `hooks/hooks.json` の `PreToolUse`**: 最後の mod が `next` を呼んだ後に、ClaudeCode 自身の処理の一部として動く。`next` を呼ばずに肩代わりした mod があれば動かない
- **`tool.check`**: 上の hook と権限ルールが判定を出した**後**に呼ばれる。そのため、2 番目のグループの hook がブロックした呼び出しを承認できる

hook が `.catch` 無しで例外・タイムアウト（1 イベントあたり 10 秒）を起こした場合、`next` を呼ぶ前なら飛ばされて次のハンドラが動く。ブロック目的の hook は `.catch` で拒否を返すようにして fail closed にする（[React to events — Handle a hook that fails](https://code.claude.com/docs/en/plugins/mods/events#handle-a-hook-that-fails)）。

### 1.5 画面への描画

mod が描ける場所を **render site** と呼ぶ。`ui.render` hook を matcher（例 `{ component: 'Pane' }`）で絞り、描く要素の木を返す。

| 描ける場所 | 内容 |
|---|---|
| Pane | 広い fullscreen ターミナルでは transcript 横のサイドバー、それ以外では prompt 上の枠。`$.ui.open({ id })` で開く。複数あればタブになる |
| Band（`AbovePrompt`） | prompt 入力欄の直上の帯。全 mod で共有する |
| ClaudeCode 自身の描画 | ユーザー / アシスタントのメッセージ、ツール呼び出し行、`AskUserQuestion` のダイアログ、スピナーなどを装飾・差し替えできる |
| toast・status line・log 行 | `$.ui.toast` / `$.ui.status` / `$.ui.log` で表示を頼む |

要素は `Text` / `Markdown` / `Link` / `Code`（diff 表示を含む）/ `Box` / `Button` / `Input` / `Select` / `Raster` / `Svg` / `Image` / `Client` がある（見本は [Interface gallery](https://code.claude.com/docs/en/plugins/mods/gallery)）。一部の render site と要素はターミナル専用で、Desktop では描かれない（[Mods reference — Render sites](https://code.claude.com/docs/en/plugins/mods/reference#render-sites)）。

**権限プロンプトだけは mod が変えられない**。mod は画面の多くを差し替えられるが、権限プロンプトの表示内容は変えられない。

### 1.6 mods API の要点

`$` の namespace のうち、よく使うものと注意点をまとめる。全メソッドは [Mods reference — Mods API methods](https://code.claude.com/docs/en/plugins/mods/reference#mods-api-methods) と、ClaudeCode が書き出す型定義（[4.2](#42-自分で書く)）にある。

| namespace | 用途 | 注意点 |
|---|---|---|
| `$.ui` | pane を開く、再描画を頼む（`invalidate`）、toast・status・log の表示 | `invalidate` による再描画は 1 秒あたり 10 回などに間引かれる |
| `$.command` / `$.tool` | ユーザー向けの `/command`、Claude 向けのツールを登録する | `session.start` で登録すると最初のターンから使える |
| `$.model` | `complete`（単発のプロンプト）、`fork`（現在の会話の続きとして 1 回送る） | セッションの認証情報を使うので、**ユーザーのプラン・API キー・クラウドプロバイダに課金される** |
| `$.prompt` | プロンプトの投入（`submit`）や下書き | `submit({ text, asUser: true })` はユーザー本人の発言として送る |
| `$.session` | 会話の取得・別セッションへのメッセージ送信（`send`）・使用量の取得 | `send` は他のセッション・subagent・teammate の Claude が読む |
| `$.fs` / `$.process` / `$.http` | ファイル読み書き、プログラム起動、HTTP リクエスト | すべて**ユーザー本人の権限**で動く。`$.fs.write` は atomic でない |
| `$.mcp` | 接続済み MCP サーバーのツールを呼ぶ | セッションの権限ルールの下で動く |
| `$.store` / `$.state` | マシン上の全セッションで共有する KV（4 MiB まで）/ 再描画と連動する state | モジュール変数は reload のたびに初期化されるので、残す値はこちらに置く |
| `$.env` / `$.settings` | 環境変数・設定の読み取り、環境変数の設定 | API キーを読める。`$.env.set` はその後に起動するコマンド・MCP サーバーにも効く |

### 1.7 mod が動く場所

hooks は plugin を読み込む全種類のセッションで動くが、**描画が出るのはターミナルと Desktop だけ**である。

| ClaudeCode を動かす場所 | hooks が動くか | mod の描画が出るか |
|---|---|---|
| ターミナルの `claude`（エディタの統合ターミナル、JetBrains plugin を含む） | 動く | 出る |
| Desktop アプリの Code タブ（WSL セッションを除く） | 動く | 出る（ターミナル専用の要素を除く） |
| Desktop アプリの WSL セッション | 動かない（WSL セッションでは plugin が使えない） | 出ない |
| VS Code 拡張のチャットパネル | 動く | 出ない |
| `claude -p` と Agent SDK | 動く | 出ない |
| claude.ai / モバイルアプリからの Remote Control | 手元マシン上のセッションで動く | 手元のターミナルに出る |
| cloud session | cloud session に持ち込まれる plugin なら動く | 出ない |

描画する mod は `e.surface` などで動作中のアプリを確かめ、描画が出ない場所では transcript の行やコマンドの返答に切り替えられる。

> **Zed（ACP）の扱いは未確認**: 本リポジトリで主に使う Zed の外部エージェント（ACP）として ClaudeCode を動かす場合は、公式の表に行が無く、hooks が動くか・描画が出るかを公式は示していない。一方、**Zed の統合ターミナルで `claude` を起動する場合**は表の 1 行目（エディタの統合ターミナル）に当たり、hooks も描画も動く。Zed の運用は [Zed ガイド](zed.md) を参照。

---

## 2. 信頼モデルと権限

### 2.1 mod が触れられるもの

mod は **sandbox の外で、ClaudeCode 本体と同じユーザー権限**で動く。読み込まれた mod は次のことができる。

- ユーザーとして**マシン上で動く**: ユーザーアカウントが触れる範囲のファイルの読み書き、プログラムの起動、ネットワークリクエスト
- **秘密情報を読む**: 環境変数・設定ファイル（そこに置いた API キーを含む）
- **セッションを見る**: 送った全プロンプト、Claude の全ツール呼び出し
- **セッションを変える**: プロンプトやツール呼び出しの書き換え、ユーザーが打ったかのようなプロンプト投入、別セッションへのメッセージ送信
- **確認なしに動く**: 確認が出る前にツール呼び出しを承認する
- **利用量を使う**: ユーザーのプランや API キーでモデルを呼ぶ

sandboxing を有効にしても、隔離されるのは Claude が実行する Bash コマンドであり、**mod が起動したプロセスは sandbox の外**で動く。公式は「信頼できる作者・marketplace の mod だけを入れる」よう警告している。

### 2.2 権限判定への影響（`tool.check`）

settings hook（`PreToolUse`）の判定は権限ルールを越えられないが、`tool.check` を扱う mod は**権限ルールと `PreToolUse` hook の判定の後に答え、その判定を置き換えられる**。どこまで覆せるかは、組込みガード `sec-default` が読み込まれる環境かどうかで変わる。ガードが読み込まれるのは「managed settings があるマシン」または「Team / Enterprise プランでサインインしている」場合である（API キーや Amazon Bedrock・Google Cloud の Agent Platform・Microsoft Foundry 経由の利用では、managed settings があるマシンに限る）。

| 判定 | ガードが無い環境（managed settings 無し、かつ Team / Enterprise 以外。個人の Pro / Max など） | ガードが読み込まれる環境 |
|---|---|---|
| `ask` ルール | mod が承認すれば確認なしで通る | 同左 |
| managed 以外の `PreToolUse` hook のブロック | mod が承認すれば通る | 同左 |
| managed settings の `PreToolUse` hook のブロック | —（managed settings が無い） | **最終**。どの mod も覆せない |
| auto mode の classifier | mod が承認した呼び出しは classifier の審査を受けずに動く | 同左 |
| `deny` ルール | **mod が承認すれば通る** | 既定では覆せない（どの settings ファイルの deny ルールでも）。組織が `allowModsToOverrideDenyRules` を `true` にすると覆せる |
| 利用者の操作が要るツール（`AskUserQuestion`、`requiresUserInteraction` を付けた MCP ツール） | mod が承認しても確認は省略されない（v2.1.292 以降、公式 docs の記載） | 同左 |

ガードが守るのはツール呼び出しの判定だけである。**mod 自身の `$.fs` / `$.process` 呼び出しには deny ルールが効かない**。たとえば `Read(.env)` を deny していても、mod は `$.fs.read` でそのファイルを読めるし、読むプログラムを起動できる。これを防ぐには、その mod を読み込ませないか、組織のポリシー mod でその API 呼び出しを拒否する。

ガードはほかに、ユーザーの mod が「managed hooks が受け取る内容・判定」「system prompt」「managed の `CLAUDE.md` などの指示」「mod が設定として読む値」「managed MCP サーバーのツールと説明」を変えることも防ぐ。それ以外は制限しない。

### 2.3 導入前の確認（`claude plugin validate`）

mod を実行せずに、扱うイベントと呼び出す API を一覧できる。plugin のファイルを手元に取得（リポジトリを clone するなど）してから、シェルで実行する。

```bash
claude plugin validate ./some-mod
```

出力の `hooks:` 行が受け取るイベント、`calls:` 行が呼び出す mods API である（環境変数を読み書きすれば `env reads:` / `env writes:` 行も出る）。

```text
  ❯ ./register.js hooks: session.start, tool.call, ui.render{component=Pane}
  ❯ ./register.js calls: $.fs.read, $.http.fetch, $.store.set, $.ui.open
```

`calls:` 行で特に見るもの:

| 呼び出し | 意味 |
|---|---|
| `$.fs.read` / `$.fs.write` | ユーザーが触れる範囲のどこでもファイルを読み書きする |
| `$.process.run` / `$.process.spawn` | ユーザーとしてプログラムを起動する |
| `$.http.fetch` | ネットワークリクエストを送る |
| `$.env.get` / `$.settings.read` | API キーを含みうる環境変数・設定を読む |
| `$.env.set` | 以後に起動するコマンドや MCP サーバーの環境変数を変える |
| `$.mcp.call` | 接続済み MCP サーバーのツールを呼ぶ |
| `$.model.complete` | ユーザーのプラン・API キーでモデルを呼ぶ |
| `$.prompt.submit` | プロンプトを投入する。ユーザー本人の発言としても送れる |
| `$.session.send` | 他のセッション・subagent・teammate の Claude が読むメッセージを送る |

`hooks:` 行では、`tool.call` と `prompt.submit`（全ツール呼び出し・全プロンプトを見て変えられる）、`session.append`（会話の各行を保存前に書き換えられる）、`ui.render{component=AskUserQuestion}`（Claude の質問ダイアログを描き直せる）、`tool.check`（確認前に承認・拒否できる）に注意する。

---

## 3. 組込み mod

ClaudeCode 自身の機能の一部は mod である。`/plugin` の **Installed** タブで **Built-in** の下に並ぶ。組込み mod は更新・アンインストールできない。

| `/plugin` での名前 | 役割 | 有効な場所 | 止め方 |
|---|---|---|---|
| `cc-plugin-agents-md` | `AGENTS.md` をプロジェクトの指示として読み込む | `AGENTS.md` を読めないセッションを除く全セッション | `/plugin` で無効化、または読み込む指示ファイルを選ぶ設定（[メモリガイド](memory.md#agentsmd-の直接読み込みv212772026-10-11-追記)） |
| `cc-plugin-diff` | `/diff` を引き受けてパネルを描く | 対話型のターミナルセッション | `/plugin` で無効化。`/diff` は残り、ClaudeCode 本体に組み込まれた版のコマンドが応答する |
| `cc-plugin-plugin-authoring` | mod を書くための `plugin-authoring` skill を Claude に渡す（skill だけで mod のコードは持たない） | Anthropic がインストール済み mod を遠隔で止めていない限り | `/plugin` で無効化 |
| `cc-plugin-sec-default` | 組織が管理するものを、ユーザーがインストールした mod から守るガード | managed settings があるマシン、または Team / Enterprise でサインイン時（[2.2](#22-権限判定への影響toolcheck)） | 止められない。管理者が managed settings で順序を決める |
| `cc-plugin-telemetry` | ClaudeCode と組込み mod が記録する分析データを送る | ClaudeCode 自身の分析が有効な場所 | `/plugin` で無効化、または `DISABLE_TELEMETRY` などで分析を止める |
| `cc-plugin-you-should-know` | 長めのタスク中に side agent が見張り、見落としそうなことを prompt 上にメモで知らせる | **既定で無効**。組織で使える場合は `/plugin` → Installed → Show disabled に出る | `/plugin enable cc-plugin-you-should-know@builtin` で有効化、`/plugin` で無効化 |

**インストール済みの mod を止める設定・フラグ（`disableAllHooks`・`--bare`・`--safe-mode`）は、組込み mod を止めない**。組込み mod は上の表の「止め方」で個別に止める。また、`/plugin` の `mods active` 行（[5.2](#52-止め方)）は組込み mod を数えない。

`diff`・`agents-md`・`sec-default`・`telemetry` のソースは [anthropics/claude-code の `mods` ディレクトリ](https://github.com/anthropics/claude-code/tree/main/mods)で公開されており、hooks module とテストを含む完全な plugin として読める。

---

## 4. 作り方

### 4.1 Claude に書かせる（`/plugin-authoring`）

対話型セッションで欲しい mod を説明すると、Claude が組込みの `plugin-authoring` skill（書き先・使えるイベントと API・読み込み方を Claude に教える）を使って書く。skill は Claude が自分でロードすることもあり、`/plugin-authoring` で明示的にロードしてもよい（[スラッシュコマンドガイド](slash-commands.md)）。

1. **説明する**: 例「現在の git ブランチを prompt の上に表示する mod を作って」。Claude はセッション専用の mods フォルダ `~/.claude/dev-mods/<セッション ID>/<mod 名>/` に書く。`default` / `acceptEdits` モードでは `~/.claude` が protected path なので、ファイルごとに作成の承認を求められる
2. **承認する**: 最初のファイルが保存されると、このセッションで hot reload を有効にするかを聞かれる
   - **Enable for this session**: ターン終了時に読み込まれ、以後は mod を変えたターンの終わりごとに reload される（resume 後も有効）
   - **Not now**: いまは読み込まない。ファイルは残り、そのセッションの次回起動時に読み込まれる。読み込ませたくなければディレクトリを消す
3. **確認する**: `/plugin` の **Installed** タブに mod が並ぶ。そこで無効化もできる
4. **試して直す**: 直したい点を Claude に伝えると、変更したターンの終わりに reload される

Claude が書いた mod は**それを書いたセッションでしか読み込まれず**、mods フォルダは `cleanupPeriodDays` を過ぎると削除される。残すにはディレクトリを自分の場所（例 `~/mods/git-branch`）へコピーし、`claude --plugin-dir ~/mods/git-branch` で読み込むか、marketplace に載せる。

**Claude が書いて承認待ちの mod が読み込まれない条件**（この条件は Claude が書いた mod だけのもので、インストール済みの mod 全般の条件ではない）:

| 条件 | 理由 |
|---|---|
| `claude -p` の実行、`dontAsk` モード | 承認するプロンプトを出せない |
| まだ信頼していない workspace | ディレクトリの trust プロンプトに答えていない |
| `--safe-mode` / `--bare` で起動、`disableAllHooks` を設定、組織の managed settings が禁止 | mods が無効になっている |

インストール済みの mod は `claude -p` や Agent SDK でも hooks が動く（[1.7](#17-mod-が動く場所)）。

### 4.2 自分で書く

公式チュートリアル（[Create a mod — Write a mod yourself](https://code.claude.com/docs/en/plugins/mods/create#write-a-mod-yourself)）は、ツール呼び出しを数えてスピナー横に表示し、`/tally` コマンドで件数を返す `first-mod` を作る。開発の要点は次のとおり。

- **`--plugin-dir` で開発する**: `claude --plugin-dir ./first-mod` で読み込むと、保存のたびに reload される。インストール済みのコピーはバージョンごとにキャッシュされるため、編集しても反映されない
- **型定義が自動で書き出される**: 対話型セッションで `--plugin-dir` から読み込んだ mod と Claude が書いた mod には、ClaudeCode が `.claude-plugin/types/` に型定義（イベント・mods API・要素・組込みツールの入力・接続中の MCP ツール）と `tsconfig.json` を書き出す。イベントや API はリリースごとに変わりうるので、**docs と食い違えば手元の型定義を正とする**
- **`claude plugin validate` を通す**: ClaudeCode が読み込み時に行うのと同じ静的解析を、セッション無しで実行する。イベント名の綴り違いもここで見つかる（例 `"tool.calls" is not an event`）
- **静的解析のための書き方の制約**: mods API は `$.store.get(...)` のように namespace とメソッドまで省略せずに書く（`$` や `$.ui` を変数に入れない・分割代入しない）。`on` のイベント名は文字列リテラルで書く。import はファイル先頭の `import` 宣言で、plugin ディレクトリ内の相対パスと `claude-code`（型と一部ヘルパー）だけにする。ES module で書く（`require` 不可）
- **Claude に直させる**: `claude --plugin-dir ./first-mod` で起動してから変更を頼むと、Claude が hooks module を編集し、`claude plugin validate` を実行して指摘を直す。`--plugin-dir` のディレクトリも protected path なので、`default` / `acceptEdits` では編集ごとに承認を求められる

### 4.3 テスト

`claude plugin test` で、名前が `.test.ts` / `.test.tsx` で終わるファイルを実行する。**セッション・サインイン・ネットワーク無し**で動き、テストは mod の hook にイベントを流して結果を確かめる。テストファイルは test kit（`claude-code/testing` モジュール）を import する。

```typescript
import { expect, test } from 'claude-code/testing'

test('/tally reports the tool calls the mod has seen', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }))          // ClaudeCode の代わりに答える stub
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: 'README.md' })
  const answer = await $.command.run({ command: 'tally', args: '' })
  expect(answer.text).toBe('Claude has made 2 tool calls since this mod loaded')
})
```

test kit の主な決まり（[Test a mod](https://code.claude.com/docs/en/plugins/mods/test)）:

- stub（`on(...)`）は、テストが最初に `$` を呼ぶ前にすべて登録する
- `session.start` は自動では動かない。それに依存する hook があれば、テスト内で先に発火させる
- `next(e)` を返す hook には、答える stub が要る
- 1 テストの上限は既定 5 秒（`timeoutMs` で変更）。失敗があれば終了ステータス 1

### 4.4 共有

mod は plugin なので、manifest でバージョンを付け、`/plugin` の仕組みでインストール・更新する。配り方は [Plugins ガイド](plugins.md)の marketplace の節と同じで、少人数ならディレクトリや `.zip` を渡す、チームなら自前の marketplace、誰にでもなら公開 marketplace か Anthropic の directory へ提出する。

- `claude plugin validate` は Anthropic 公式に見える名前（`claude-` で始まるなど）を不合格にする
- イベントと API はリリースごとに変わりうるので、README に検証した ClaudeCode の版を書いておく

---

## 5. インストール・止め方・管理

### 5.1 インストール

mod は marketplace から plugin としてインストールする。

```bash
# セッション内
/plugin install token-chart@your-org

# シェルから
claude plugin install token-chart@your-org
```

セッションを開いたままシェルからインストール・更新した場合は、そのセッションで `/reload-plugins` を実行すると読み込まれる（実行しなければ次回起動時）。

Anthropic は見本の mod を [anthropics/claude-code-playground の `claude-code/mods`](https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods) で公開している（サポート無し）。

| 見本 | 内容 |
|---|---|
| `token-weather` | コンテキストウィンドウの「天気予報」を prompt の上に描く |
| `blast-radius` | `rm -rf` や force push など危険なシェルコマンドを止め、何が変わるかを見せて続行 / 中止のボタンを出す |
| `replay-theater` | 直前のターンで Claude が行ったファイル編集を順に再生する `/replay` を足す |

試すなら clone して `--plugin-dir` で 1 セッションだけ読み込む。見本もユーザー権限で動くので、先に `claude plugin validate` で中身を確かめる。

### 5.2 止め方

mods は既定で ON である。どの範囲を、どの期間止めるかで方法を選ぶ（戻すときは同じ変更を取り消す）。

| 範囲 | 方法 | 補足 |
|---|---|---|
| 1 つの mod | `/plugin` の **Installed** タブで plugin を無効化・アンインストール | 組込み mod もここで個別に無効化する（`sec-default` を除く） |
| インストール済みの全 mod、1 セッションだけ | `claude --safe-mode` で起動 | 他のカスタマイズも止まる。組織の mod も止まる（問題の切り分け向け） |
| インストール済みの全 mod、全セッション | `~/.claude/settings.json` に `"disableAllHooks": true` | settings hook とカスタム status line も止まる。組織が管理するものは動き続ける |
| managed 以外のインストール済み plugin の mod | `claude --bare` で起動 | `--bare` では managed 以外のインストール済み plugin が hooks module を読み込まない |

- **上の設定・フラグは組込み mod を止めない**（[3. 組込み mod](#3-組込み-mod)）
- `disableAllHooks` と組織の `allowManagedModsOnly` は **mod だけを止め、plugin の残り（skill・コマンド・agent・MCP サーバー）は読み込まれたまま**になる
- 先行公開の時期に `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` を設定していたら削除する。v2.1.287 以降はこの変数を無視するので、`0` にしても mods は止まらない

**読み込まれた mod の確認**: ターミナルで `/plugin` を開くと、タブの下に `1 mod active · first-mod` のような薄い行が出る（組込み mod は数えない）。

**mods が読み込める状態かの確認**: mod の無いディレクトリでシェルから `claude plugin test` を実行し、表示で判断する（セッション不要）。

| 表示に含まれる文言 | 意味 |
|---|---|
| `no hooks module to load` | mods は読み込める（テストする mod が無いだけ） |
| `hooks modules are turned off here` | 自分の `disableAllHooks` か組織のポリシーが止めている |
| `... the rollout switch served off` | Anthropic がインストール済み mod を遠隔で止めている |
| `... the rollout switch was saved off by an earlier session` | 以前のセッションが保存した古い値を使った。一度 `claude` を起動して更新してから再実行する |

組織の `allowManagedModsOnly` はこのコマンドでは分からない（その場合はインストールした mod が拒否され、理由のメッセージが出る）。

### 5.3 組織での管理（managed settings）

管理者は managed settings で、mods を動かすか・どれを・どの順で動かすかを決める。方針ごとの設定は次のとおり（[Manage mods for your organization — Choose how much to allow](https://code.claude.com/docs/en/plugins/mods/admin#choose-how-much-to-allow)）。

| やりたいこと | 設定 |
|---|---|
| インストール済みの mod を一切動かさず、settings hook は残す | `allowManagedModsOnly` を設定し、組織の mod は配らない |
| インストール済みの mod も hook も（managed hooks も含め）一切動かさない | `disableAllHooks` を `true` |
| 組織の mod だけを動かす | `allowManagedModsOnly` を設定し、組織の mod として数えられる形で配る |
| 承認した marketplace の mod なら何でも可 | marketplace の制限を維持し、`disableSideloadFlags` を `true` |
| どの mod も可。ただし組織の mod が他を検査する | 組織の mod を配り、`sec-default@builtin` と一緒に `prependPlugins` に載せる |

関係するキー:

| キー | 置き場所 | 内容 |
|---|---|---|
| `allowManagedModsOnly` | managed settings の `pluginConfigs."cc-plugin-sec-default@builtin".options` | 組織の mod と組込み mod だけが hooks を動かす。ユーザーの settings hook・status line・`/goal` は動き続ける |
| `allowModsToOverrideDenyRules` | 同上 | ユーザーの mod が deny ルールで拒否される呼び出しを承認できるようにする |
| `prependPlugins` / `appendPlugins` | managed settings（managed settings が無く、Team / Enterprise でサインインしていないマシンに限り user settings でも可） | plugin id のリスト。`prependPlugins` はユーザーの mod より前、`appendPlugins` は後に、記載順で動く |
| `pluginConfigs` | user / managed settings | mod の `userConfig` の値。plugin id（`--plugin-dir` なら `<名前>@inline`）をキーにする |
| `allowManagedHooksOnly` | managed settings | 組織の mod と組込み mod 以外の mod を読み込まない。ユーザーの settings ファイルの hook も止める |
| `disableAllHooks` | 任意の settings ファイル | managed では、組織の mod も含め全インストール済み plugin の mod と全 hook を止める（managed の `PreToolUse` も効かなくなる）。ユーザー側では組織が管理するものは動き続ける |
| `disableSideloadFlags` | managed settings | 起動時に `--plugin-dir` / `--plugin-url` を拒否し、Claude が書いた mod の読み込みも止める（`--agents` / `--mcp-config` も拒否する） |

```json
{
  "pluginConfigs": {
    "cc-plugin-sec-default@builtin": {
      "options": {
        "allowManagedModsOnly": true
      }
    }
  }
}
```

設定時の注意（いずれも公式 admin ページの記載）:

- **ガードの option は managed settings だけが有効**: user / project / local の settings や `--settings` のファイルに同じエントリを書いても、設定も緩和もされない。`pluginConfigs` のキーは `cc-plugin-sec-default@builtin` の形だけを受け付ける（`prependPlugins` は `sec-default@builtin` も可）
- **`prependPlugins` は既定を置き換える**: managed で `prependPlugins` を設定したら、ガードを残すために `sec-default@builtin` をリストに含める。含めないとガードが読み込まれず、option も効かない
- **ガードは fail closed**: managed settings を読めなければユーザーの mod を全部拒否し、mod が承認した呼び出しの deny ルールを確かめられなければその呼び出しを拒否する
- **「組織の mod」と数えられる条件**: managed の `enabledPlugins` で `true`、marketplace を絶対パスのローカルディレクトリとして managed settings で指定、その marketplace が plugin を相対パスで載せている（その場で読み込まれる）。GitHub・git・URL・npm から取得してキャッシュにコピーされる plugin は、managed で有効化してもユーザーの mod として扱われる
- **ネットワーク制御**: 組織のポリシーが WebFetch を許さなければ、全 mod の `$.http.fetch` も拒否される。`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` が止めるのは、組込み mod のリクエストと、セッションの Anthropic 認証情報を伴う `$.http.fetch` だけで、ユーザーや組織が入れた mod のリクエストは止めない（v2.1.288 より前は全 mod の `$.http.fetch` を止めていた。公式 docs の記載）。`$.process.run` で起動したプログラムの通信はどちらの対象でもない
- **plugin の制御はそのまま mod に効く**: `strictKnownMarketplaces` などインストールを制限する設定が、mod を入れられるかを決める（[Plugins ガイド](plugins.md)）

開発・配布で使う環境変数:

| 名前 | 内容 |
|---|---|
| `CLAUDE_CODE_PLUGIN_DIRS` | フラグを渡せないアプリ向けに、`--plugin-dir` と同じく読み込む plugin ディレクトリ（絶対パスを `:` 区切り、Windows は `;`）。環境変数か `~/.claude/settings.json` の `env` に書く |
| `CLAUDE_CODE_PLUGIN_DIR_WATCH` | `1` で、長時間動く非対話セッションでも `--plugin-dir` の mod を保存時に reload する |

---

## 6. Tips / トラブルシューティング

### Tips

- **固定の条件なら権限ルールで足りる**: 決まったコマンドやパスの許可・拒否は `Bash(npm test)` のようなパーミッションルールで書け、コードは要らない。`tool.check` は「いまの git ブランチ」のように**その時点の状態で判定が変わる**場合に使う（公式 events ページの指針）
- **mod の判定はリマインダーと考える**: コマンド文字列を照合する `tool.check` は回避されうる。`main` への push を全員に対して確実に防ぐなら、Git ホスティング側の branch protection を使う（公式の注記）
- **ブロック用の hook には `.catch` を付ける**: 付けないと、例外やタイムアウトで hook が飛ばされ、呼び出しが素通りする（[1.4](#14-実行順)）
- **個人環境ではガードが無いことを前提にする**: managed settings が無く Team / Enterprise でもない環境では、インストールした mod は deny ルールも越えて承認しうる（[2.2](#22-権限判定への影響toolcheck)）。入れる前に `claude plugin validate` で `tool.check` の有無と `calls:` を確かめる
- **残したい値は `$.state` / `$.store` に置く**: モジュール変数は reload のたびに初期化される。`$.state` は `/clear`・`/resume`・`/branch` でも既定値に戻る

### トラブルシューティング

まず `claude plugin validate <dir>` で mod の読み取り結果を見て、次に ClaudeCode が書く 1 行のメッセージを探す。`--plugin-dir` で hot reload 中のセッションなら transcript に薄い行で出る。それ以外の対話セッションでは debug log にしか出ないので、`claude --debug` または `claude --debug-file ./mod-debug.log --plugin-dir ./first-mod` で起動する。

| 症状 | 原因 | 対処 |
|---|---|---|
| `validate` は通るが `hooks` 行が出ない | `hooks/hooks.json` に `modules` が無い、または綴り違い | `"modules": ["./register.js"]` を足す |
| `/plugin` の `mods active` 行に mod が無い | hooks module が拒否された | debug log の `hooks module <名前> not loaded:` の後の理由を読む（`disableAllHooks`・`allowManagedHooksOnly`・`--bare`・同名 plugin など） |
| 初めて開いたディレクトリで mod が読み込まれない | trust プロンプトに答えていない | そのディレクトリで `claude` を起動し、trust プロンプトを承認する |
| インストール済みの plugin が全く読み込まれない | `--safe-mode` で起動した | フラグを外して起動する |
| `claude -p` で `hooks module not loaded` が stderr に出る | hooks module が拒否された | コロンの後の理由を読む |
| 編集が反映されない | インストール済みの（キャッシュされた）コピーを編集している | `claude --plugin-dir <作業ディレクトリ>` で開発する |
| Claude が書いた mod が読み込まれず、hot reload の質問も出なくなった | 質問が回答なしで 3 回終わった（`askUserQuestionTimeout` の時間切れなど） | mods フォルダからディレクトリをコピーし、`--plugin-dir` で新しいセッションを起動する |
| auto mode で `a hook changed this call's input after the model wrote it` と拒否される | mod の `tool.call` / `turn.step` か settings hook の `PreToolUse` が、server-side classifier の審査後に入力を変えた | 同じ hook が毎回変えているなら、その mod / hook を止めるか、auto mode を抜けて自分で承認する |
| `tried to lift a deny rule in your settings` | mod の `tool.check` が deny ルールで拒否される呼び出しを承認しようとし、ガードが止めた（呼び出しは拒否のまま） | 意図した挙動。組織で許すなら `allowModsToOverrideDenyRules` |
| `mods that run in the hooks worker are off for this session: it crashed 3 times` | hooks worker が 3 回落ち、原因の mod を特定できなかったため、組込み以外の全 mod を外した | `/reload-plugins` で読み込み直す |
| Desktop でだけ描画が出ない | その render site・要素が Desktop に無い | [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference#render-sites) の render site と要素の表を確かめる |

---

## 関連ドキュメント

- [ClaudeCode Plugins ガイド — Mods（hooks module）](plugins.md#modshooks-module) — plugin 側から見た mod の位置づけ、marketplace・インストール
- [ClaudeCode Hooks ガイド — Hooks と Mods の関係](hooks.md#hooks-と-mods-の関係) — settings hook との比較、`PreToolUse` と `tool.check` の評価順
- [ClaudeCode スラッシュコマンドガイド](slash-commands.md) — `/diff`（組込み mod `cc-plugin-diff`）、`/plugin`、`/plugin-authoring`
- [ClaudeCode の設定ファイル一覧と役割](config-files.md) — managed settings の配置、`disableAllHooks` などの設定キー
- [ClaudeCode メモリガイド — AGENTS.md の直接読み込み](memory.md#agentsmd-の直接読み込みv212772026-10-11-追記) — 組込み mod `cc-plugin-agents-md`
- [Zed エディタ活用ガイド](zed.md) — ACP で ClaudeCode を動かす環境（mods の描画は未確認）
- [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview) / [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference) / [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin) — 公式ドキュメント
