# GitHub Actions で Claude Code レビュー BOT を設定する

> 出典: [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) / [usage docs](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md) / [GitHub Docs: Automatic token authentication](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication) / 実機検証 3 repo（jarvis・revolution・one-more-time PR #9/#10） (2026-06-07時点)

GitHub Actions に `anthropics/claude-code-action` を設定すると、PR の作成・更新時に `claude[bot]` が自動でコードレビューし、全体所感（PR コメント）と個別指摘（inline コメント）を GitHub 上に投稿する。本ドキュメントは、その**正しい設定手順**と、jarvis / one-more-time で紆余曲折した**教訓**（同じミスを繰り返さないため）をまとめる。

最重要の教訓は **「コメント投稿には 2 つの独立した許可レイヤーが必要で、片方を忘れると workflow は SUCCESS のまま無言で終わる」** ことである。one-more-time では「権限（`permissions`）は付与したのにコメントが出ない」状態が続き、原因は **`claude_args` の `--allowedTools` 未設定**だった。

> **「サクッと設定したい」場合**: グローバルスキル `/setup-github-claude-code-review` が、本ドキュメントを正本として workflow 配置・secret 設定案内・検証手順までを一括で実行する（後述 §6）。本ドキュメントはその根拠であり、手動設定時の手順書でもある。

---

## 1. 最重要教訓 — コメント投稿に必要な「2 層の許可」

claude[bot] が PR にコメントを投稿するには、**別レイヤーの 2 つの許可が両方**必要である。どちらか一方でも欠けるとコメントは投稿されない。

| レイヤー | 設定場所（同じ workflow ファイル内の別ブロック） | 役割 | 欠けると |
|---|---|---|---|
| **① GitHub API 権限** | `permissions: pull-requests: write` | GitHub 側でコメント書き込みを許可 | `gh pr comment` 等が 403 |
| **② Action 内ツール許可** | `with: claude_args: --allowedTools "..."` | claude-code-action のサンドボックスで投稿ツールを許可 | ツールが **permission denied**、無言で SUCCESS 終了 |

> **盲点**: ①だけ直しても②が空だと直らない。one-more-time はこのパターンで、実機ログに `permission_denials_count: 13` / `No buffered inline comments` が出てコメントゼロだった。①は「ドアの鍵」、②は「Claude の手」。両方そろって初めて投稿できる。

---

## 2. 正本 workflow（コピペ用・全文）

以下を `.github/workflows/claude-code-review.yml` として配置する。jarvis / revolution / one-more-time の 3 repo で実機検証済みの構成である。

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

# push 連打時に古いレビュー実行をキャンセルし、重複コメント・コスト増を防ぐ
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

jobs:
  claude-review:
    # fork からの PR は secret が渡らないためスキップ（public repo 対策・private でも将来安全策）
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    permissions:
      contents: read          # PR diff の読み取り
      pull-requests: write     # ← ① レビューコメント投稿に必須（GitHub API 権限）
      id-token: write          # OIDC で App token を取得するため

    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1

      - name: Run Claude Code Review
        uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          prompt: |
            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number }}

            この Pull Request を日本語でレビューしてください。観点:
            - コード品質・ベストプラクティス
            - 潜在的なバグ・問題
            - セキュリティ上の懸念
            - パフォーマンス
            - ドキュメント / 設定の場合は正確性・公式仕様や一次情報との整合

            PR ブランチは作業ディレクトリにチェックアウト済みです。
            全体的な所感は `gh pr comment`、特定箇所の指摘は
            `mcp__github_inline_comment__create_inline_comment` (confirmed: true) を使用。
            問題がなければその旨を `gh pr comment` で明示すること。
            レビューは GitHub 上にのみ投稿すること。
          # ← ② コメント投稿ツールの明示許可（これが無いと permission denied でコメントが出ない）
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*)"
```

### 各設定の意図

| 設定 | 意図 |
|---|---|
| `on: pull_request` types | PR の作成・更新・再オープン・draft 解除でレビューを起動 |
| `concurrency` + `cancel-in-progress` | push 連打時に古い run をキャンセルし、重複レビューと API コストを抑える |
| `if: head.repo.full_name == github.repository` | fork PR をスキップ（fork には secret が渡らず必ず失敗するため） |
| `permissions`（最小権限） | `contents:read` / `pull-requests:write` / `id-token:write` のみ。未使用権限（`issues` 等）は付けない |
| `claude_code_oauth_token` | `CLAUDE_CODE_OAUTH_TOKEN` secret を参照（§3 で設定） |
| `prompt` | 自由文でレビュー観点と「**GitHub 上に投稿せよ**」を明示指示。`/code-review` プラグイン方式は投稿指示が無くコメントが出ないため使わない |
| `claude_args --allowedTools` | **本設定の核心**。投稿ツール（inline comment + `gh pr comment`）を明示許可 |

> **補足（サプライチェーン強化）**: 本テンプレートは anthropics 公式 quickstart に合わせ `anthropics/claude-code-action@v1`（タグ参照）を使う。タグは後から移動・削除され得るため、より強いサプライチェーン耐性が必要なら **full-length commit SHA で固定**する選択肢がある（`uses: anthropics/claude-code-action@<full-sha>`）。ただし SHA 固定はアップデートを自動受信できなくなるトレードオフがあるため、本リポジトリでは公式 quickstart 準拠の `@v1` を既定とする。
> 出典: [GitHub — Secure use reference](https://docs.github.com/en/actions/reference/secure-use-reference)（"Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release."）/ anthropics/claude-code-action 公式 docs は全例で `@v1` を使用。

---

## 3. セットアップ手順

### 3.1 OAuth token の取得

ローカルの ClaudeCode で以下を実行し、GitHub Actions 用の長期 OAuth token を発行する。

```bash
claude setup-token
```

> 表示された token を控える。これを repo の secret `CLAUDE_CODE_OAUTH_TOKEN` に登録する。

### 3.2 secret の登録（`gh` CLI）

対象 repo のルートで:

```bash
gh secret set CLAUDE_CODE_OAUTH_TOKEN
# プロンプトに token を貼り付ける（履歴に残さないため引数で渡さない）

# 確認（値は表示されない、存在のみ）
gh secret list | grep CLAUDE_CODE_OAUTH_TOKEN
```

### 3.3 workflow の配置

§2 の YAML を `.github/workflows/claude-code-review.yml` として配置し、`main`（default branch）にマージする。

> **理由は §5 の罠を参照**。workflow は **default branch に存在して初めて有効**になるため、最初の配置は「workflow だけの PR をマージ」または「直接 default branch に置く」必要がある。

### 3.4 検証

workflow を **変更しない**通常 PR を 1 本立て、claude[bot] が「レビュー所感」コメントを投稿することを確認する（§5 の罠により、workflow 変更 PR では検証できない）。

---

## 4. トラブルシュート

| 症状 | 原因 | 対処 |
|---|---|---|
| **run は SUCCESS だがコメントが出ない**（無言） | ② `claude_args --allowedTools` が未設定 → 投稿ツールが permission denied | `claude_args` に投稿ツールを追加（§2） |
| ログに `permission_denials_count: N` / `No buffered inline comments` | 同上（②欠落の典型ログ） | 同上 |
| `gh pr comment` が 403 / 権限エラー | ① `permissions: pull-requests` が `read` のまま | `permissions: pull-requests: write` に変更 |
| **App token exchange failed: 401 — Workflow validation failed** | workflow ファイルが default branch と不一致（= workflow 変更 PR）| **正常**。§5 参照。default branch にマージ後、別 PR で検証 |
| fork PR で必ず失敗する | fork に secret が渡らない | `if: head.repo.full_name == github.repository` でスキップ（§2 既定） |
| `/code-review` プラグイン方式でコメントが出ない | プラグイン方式は投稿指示が無く、レビュー結果を計算するだけ | 自由文プロンプト方式（§2）に切替 |

### permission_denials を読む

claude-code-action のログ（`gh run view <run-id> --log`）で以下を確認する。

```text
PullRequests: write          ← ① は OK
permission_denials_count: 13 ← ② が欠落（投稿ツールが denied）
No buffered inline comments  ← 結果、コメント投稿ゼロ
```

`PullRequests: write` なのに `permission_denials_count` が出ていれば、原因は②（`claude_args`）でほぼ確定する。

---

## 5. ⚠️ 罠 — workflow を変更する PR ではレビューが走らない

claude-code-action は App token 発行時に、**「PR ブランチの workflow ファイルが repository の default branch と同一内容か」を検証**する。異なると以下で失敗する。

```text
App token exchange failed: 401 Unauthorized - Workflow validation failed.
The workflow file must exist and have identical content to the version on the
repository's default branch. If you're seeing this on a PR when you first add a
code review workflow file to your repository, this is normal and you should ignore this error.
```

これは **PR で workflow を改竄して secret を盗む攻撃を防ぐためのセキュリティ設計**であり、エラー文自身が「workflow を初めて追加する PR では正常」と明記している。

### 帰結（必ず守る）

- **workflow ファイルを変更・新規追加する PR では claude review は必ず失敗する。これは異常ではない。**
- 修正の効果検証は「**一度 default branch にマージ → workflow 以外を変える別の通常 PR で確認**」の順で行う。
- branch protection で `claude-review` を必須チェックにしている場合、workflow 変更 PR がこの失敗でブロックされる。必須から外すか、マージ運用で許容する。

> one-more-time の実例: PR #9（workflow 修正）は token validation で fail したが、これは仕様。マージ後の PR #10（README 変更）で claude[bot] のコメント投稿を確認できた。

---

## 6. サクッと設定する — `/setup-github-claude-code-review` スキル

新しい repo で上記を毎回手作業するのを避けるため、グローバルスキル（`~/.claude/skills/setup-github-claude-code-review/`）を用意している。新 repo の ClaudeCode セッションで以下を実行する。

```text
/setup-github-claude-code-review
```

スキルは本ドキュメントを正本として、以下を一括で行う。

1. `.github/workflows/claude-code-review.yml` を正本テンプレートから生成
2. `CLAUDE_CODE_OAUTH_TOKEN` secret の有無を `gh secret list` で確認し、未設定なら登録手順を案内
3. ① / ② の 2 層権限と §5 の罠を説明
4. default branch マージ → 別 PR での検証手順を案内

---

## 7. 実績（3 repo で稼働中の正本）

| repo | 公開範囲 | 備考 |
|---|---|---|
| [jarvis](https://github.com/thanks2music/jarvis) | public | 本方式の最新形（concurrency / fork スキップ / inline 対応） |
| [revolution](https://github.com/thanks2music/revolution) | public | 自由文プロンプト + `gh pr comment` 明示方式 |
| [one-more-time](https://github.com/thanks2music/one-more-time) | private | PR #9 で②を付与し解決、PR #10 で実機検証成功 |

---

## 関連ドキュメント

- [ClaudeCode Skills ガイド](skills.md) — スキルの frontmatter・発火条件
- [ClaudeCode の設定ファイル一覧と役割](config-files.md) — `settings.json` 等の権限設定
- [ClaudeCode Hooks ガイド](hooks.md) — 決定論的な自動実行（CLAUDE.md との違い）
