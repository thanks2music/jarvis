# Slack の MCP で複数のワークスペースを使い分ける

仕事用と個人用など、2 つの Slack ワークスペースを ClaudeCode から使う手順をまとめる。結論は次のとおりである。

- **1 つのセッションの中で、2 つのワークスペースを同時には使えない**
- **プロジェクト（起動したディレクトリ）ごとに、どちらのワークスペースを使うかを分けられる**。Slack の plugin を片方のワークスペースに、claude.ai の Slack connector をもう片方のワークスペースにつなぎ、plugin を使わないプロジェクトでだけ plugin のサーバーを無効にする

> 2026-11-22 に ClaudeCode v2.1.330 で実測した。公式 docs に複数ワークスペースについての記載は無い（下の「公式 docs で確かめたこと」）。plugin と connector の重複の扱いは版によって変わってきた（下の「2 つを同時に有効にするとどうなるか」）ため、ClaudeCode を更新したら、手順 5 でワークスペースを確かめ直す。

## Slack の MCP につなぐ経路は 2 つある

| | Slack の plugin（`plugin:slack:slack`） | claude.ai の Slack connector（`claude.ai Slack`） |
|---|---|---|
| 入れ方 | ClaudeCode で `/plugin install slack` | [claude.ai/customize/connectors](https://claude.ai/customize/connectors) で Slack を追加する |
| 接続先 | `https://mcp.slack.com`（`/mcp` の画面の表示） | `https://mcp.slack.com/mcp`（claude.ai の connector の画面の表示） |
| 使える場所 | その Mac の ClaudeCode | claude.ai の Web・デスクトップアプリ・ClaudeCode |
| 付いてくるもの | Slack 公式の skill（検索・チャンネルの要約・standup など）と MCP のツール | MCP のツールだけ |
| サインイン | `/mcp` でサーバーを選び、OAuth でワークスペースを選ぶ | claude.ai の connector の画面で「連携させる」を押し、OAuth でワークスペースを選ぶ |

どちらも、1 つのサインインにつき 1 つのワークスペースである。OAuth の画面の「Claude をどこで使用しますか？」で選んだワークスペースにつながる。

## 2 つを同時に有効にするとどうなるか

plugin と connector を両方とも有効にすると、`/mcp` で connector が次のように表示され、使えない。

```
claude.ai Slack · ○ hidden — same URL as your server 'plugin:slack:slack'
  To use this connector instead, disable the plugin server in /plugin
```

- 接続先の URL は末尾の `/mcp` の有無だけ違うが、同じサーバーとして扱われた。[mcp-setup.md](mcp-setup.md#同じサーバーが複数の場所にあるとき) にまとめた docs の説明では、パスが違えば別のサーバーになるはずであり、食い違っている
- このとき plugin のツール（`mcp__plugin_slack_slack__*`）は使え、plugin がつないだワークスペースのユーザー情報を読めた。mcp-setup.md の「[plugin と connector が同じ URL だと両方とも使えなくなる](mcp-setup.md#plugin-と-connector-が同じ-url-だと両方とも使えなくなる)」（2026-11-07、Figma と Notion で実測）とは違い、docs どおり plugin が優先された
- 同じ connector に別の名前を付けて 2 つ目として足しても、同じ URL なので重複として外れる見込みである（docs: "It matches plugins and connectors by endpoint"）。試していない

## 手順: プロジェクトごとにワークスペースを分ける

例として、ワークスペース A（仕事）を plugin で、ワークスペース B（個人）を connector で使う。B を使いたいプロジェクトでだけ plugin を無効にする。

1. **plugin をワークスペース A でつなぐ**: `/plugin install slack` の後、`/mcp` で `plugin:slack:slack` を選んでサインインし、OAuth の画面で A を選ぶ
2. **connector をワークスペース B でつなぐ**: [claude.ai/customize/connectors](https://claude.ai/customize/connectors) で Slack を追加し、「連携させる」から OAuth の画面で B を選ぶ。「接続済み」と出れば済み
3. **ClaudeCode に読み込ませる**: 起動中のセッションでは `/reload-plugins` を実行する。connector が `/mcp` に現れる（この時点では上の hidden の表示になる）
4. **B を使うプロジェクトで plugin を無効にする**: そのプロジェクトのディレクトリで起動したセッションで、`/mcp` → `plugin:slack:slack` →「Disable」を選び、`/reload-plugins` を実行する。hidden の表示は「disable the plugin server in /plugin」と案内するが、`/plugin` で plugin を無効にすると全プロジェクトに効く。プロジェクトごとに分けるには `/mcp` の「Disable」を使う。`claude.ai Slack` が ✔ になり、ツール（`mcp__claude_ai_Slack__*`）が使えるようになる
5. **どのワークスペースにつながったかを確かめる**: Claude に `slack_read_user_profile` を引数なしで（自分のプロフィールを）読ませる。表示名・組織名・メールアドレスで、どちらのワークスペースかが分かる。読み取りだけのツールなので、何も書き込まない
6. **A を使うプロジェクトでは何もしない**: plugin は有効のままなので、A が使われる

### 無効にした設定はどこに残るか

`/mcp` の「Disable」は、`~/.claude.json` の `projects` の中の、**そのディレクトリのエントリ**の `disabledMcpServers` に記録される。次のコマンドで、どのディレクトリで無効にしたかを確かめられる（サーバー名だけを読み、値は表示しない）。

```bash
jq -r '.projects | to_entries[] | select((.value.disabledMcpServers // []) | index("plugin:slack:slack")) | .key' ~/.claude.json
```

- 他のディレクトリには効かない。同じリポジトリでも、**サブディレクトリや git worktree で起動すると、別のエントリになる**。そこで B を使いたければ、そのディレクトリでも同じ操作をする
- 全体で plugin を止めたいなら `/plugin` で plugin ごと無効にする。この場合は、どのプロジェクトでも connector（B）だけになる

## 使うときの注意

- **どちらのワークスペースかを、作業を始める前に確かめる**（手順 5）。サインインしたまま忘れていると、仕事のワークスペースの内容を個人の作業に持ち込むことになる
- メッセージの投稿・リアクション・canvas の作成などの**書き込みのツールは、実行する前に人が確認する**。Slack の MCP には書き込みのツールも含まれる（connector の画面では「書き込み/削除ツール」として分けて表示される）
- claude.ai の Web・デスクトップアプリでは、plugin は関係なく、connector のワークスペース（B）が使われる

## 公式 docs で確かめたこと

- connector の追加とサインイン: ClaudeCode に claude.ai のサブスクリプションでログインしていれば、claude.ai で追加した connector が自動で現れる。サインインは claude.ai で行うか、ClaudeCode の `/mcp` でつなぎ直す（[Claude Code MCP](https://code.claude.com/docs/en/mcp)、[Remote Control](https://code.claude.com/docs/en/remote-control)）
- plugin と connector の重複: "It matches plugins and connectors by endpoint, so one that points at the same URL or command as an enabled server above counts as a duplicate."（[Claude Code MCP](https://code.claude.com/docs/en/mcp) の Scope hierarchy and precedence）
- サインインの保存: "Claude Code stores OAuth sign-ins per endpoint"（同上）
- Slack の plugin: "You'll be prompted to authenticate into your Slack workspace via OAuth."（[Slack MCP and Skills Plugin](https://docs.slack.dev/ai/slack-skills-plugin/)）
- **複数のワークスペース・複数のアカウントへの対応、connector がどのワークスペースにつながっているかを表示する方法は、どの docs にも記載が無い**（2026-11-22 確認）。上の手順は実測に基づく
