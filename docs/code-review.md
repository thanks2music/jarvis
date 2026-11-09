# マネージド Code Review（Team / Enterprise）

> 出典:
> - [Code Review](https://code.claude.com/docs/en/code-review)（概要・提供条件・レビューの仕組み・選択肢の比較）
> - [Set up Code Review](https://code.claude.com/docs/en/code-review-setup)（有効化・review level・Review runs・リポジトリ管理）
> - [Customize Code Review](https://code.claude.com/docs/en/code-review-customize)（`CLAUDE.md` / `REVIEW.md` / include / skill の取り込み / 読むブランチ）
> - [Read and request reviews on a pull request](https://code.claude.com/docs/en/code-review-pull-requests)（重大度・check run・コメントコマンド・Action との併用）
> - [Code Review costs and usage](https://code.claude.com/docs/en/code-review-costs)（課金・使用量上限・analytics）
> - [Troubleshoot Code Review](https://code.claude.com/docs/en/code-review-troubleshooting)（check run のタイトル別の対処）
> - [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local)（ローカルの `/code-review`）
> - [Code Review is now generally available](https://claude.com/resources/articles/code-review-is-now-generally-available)（GA 告知、2026-10-15）
> 最終更新: 2026-11-01

**Code Review** は、GitHub の Pull Request を **Anthropic のインフラ上で** Claude がレビューするマネージドサービスである。複数のエージェントが差分と周辺コードを並列に読み、検証ステップで誤検知を落としたうえで、指摘を該当行への inline コメント・review body の要約・check run として PR に投稿する。2026-10-15 に research preview を終えて **GA** となり、**Team / Enterprise プラン**の組織で使える。

レビューは PR を approve も block もしない。マージの判断は人間に残る。公式は「指摘ゼロは、コードにバグや脆弱性が無いことを意味しない」と注記している。

本リポジトリには、PR レビューの手段として **GitHub Actions の claude-code-action**（[github-actions-claude-code-review.md](github-actions-claude-code-review.md)）と、**ローカルの `/code-review`**（[slash-commands.md](slash-commands.md)）がすでにある。本 doc はマネージド版の仕様をまとめ、3 つの違いを §9 の比較表で示す。

---

## 1. 提供条件

| 項目 | 内容 |
|---|---|
| プラン | **Team / Enterprise**。Free / Pro / Max / Ultra では使えない |
| コードホスト | GitHub（GitHub Enterprise Server、data residency 付きの GitHub Enterprise Cloud を含む） |
| 使えない組織 | **Zero Data Retention（ZDR）** を有効にした組織、**HIPAA 構成**を適用した組織。Anthropic の BAA の対象外でもある。**customer-managed encryption keys（CMEK）** を使う組織も現時点では使えない |
| 実行場所 | Anthropic のインフラ上のマネージド環境。**self-hosted 環境では動かない** |
| クラウドプロバイダ経由の組織 | 開発者が Amazon Bedrock / Google Cloud's Agent Platform / Microsoft Foundry 経由で Claude Code を使っていても、上記プランの Claude organization が必要 |

> GA 告知によると、対象の Enterprise 組織は 2027-01-15 までに少なくとも $10,000 分の Code Review credits を申請できる（申請から 30 日で失効、規約あり）。

---

## 2. レビューの仕組み

既定では **correctness**（本番を壊すバグ）に絞り、フォーマットの好みやテスト不足は指摘しない。レビューは 4 段階で進む。

| 段階 | 内容 |
|---|---|
| 1. Find | 複数のエージェントが差分と周辺コードを並列に調べる |
| 2. Verify | 検証ステップが候補をコードと照合し、誤検知を除く |
| 3. Rank | 残った指摘を重複排除し、重大度で並べる |
| 4. Post | PR に結果を投稿する |

PR に残るもの:

- **Findings**: 該当行への inline コメントと、review body の要約
- **check run**: 名前は **Claude Code Review**。Details に指摘の一覧が出る。結論は neutral（または一部の push 後は skipped）で、**failure にはならない**
- **指摘ゼロのときの note**: check run のタイトルは **Code review found no issues**

レビューに使うモデルは Code Review が選び、admin 設定にモデルの選択肢は無い。徹底度は review level（§3.2）で変える。

### 2.1 レビューがアクセスできる範囲

| 観点 | 内容 |
|---|---|
| 経路 | Owner がセットアップで入れる **Claude GitHub App** |
| リポジトリへのアクセス | レビュー中は **read-only**。commit は push しない |
| PR への書き込み | コメント・check run の投稿、自分の過去スレッドの resolve、コメントコマンドへの 👀 リアクション |
| コードの扱い | 差分と周辺コードを読むだけで、**build も実行もしない** |
| App の権限 | App 自体は他の Claude 機能（GitHub Actions など）と共有する、より広い権限セットを持つ |

---

## 3. 有効化と組織の既定値（Owner 向け）

Owner が claude.ai の **Admin settings > Claude Code** の **Code review** 節で有効化する。レビューは Anthropic のインフラで動くため、**リポジトリに workflow ファイルを置く必要は無い**。

### 3.1 有効化の手順

| 必要な権限 | 用途 |
|---|---|
| Claude organization の **Owner** | admin ページの全操作 |
| GitHub organization の owner | Claude GitHub App のインストールと Claude organization への link |
| 追加する各リポジトリへの write 権限（Claude に接続した GitHub アカウントで） | リポジトリの追加 |

1. **Allow code review** スイッチを on にする
2. **Connect GitHub** で GitHub アカウントを接続する（GHES はここでインスタンスを選ぶ）
3. 必要なら **Install GitHub App** から Claude GitHub App を入れ、対象リポジトリへのアクセスを与える
4. レビュー対象のリポジトリを選び **Continue**
5. **Code review is set up** ダイアログで **Finish** を押す（他の方法で閉じるとリポジトリは追加されるが Allow code review は off のまま）
6. draft でないテスト PR を開き、数分以内に **Claude Code Review** の check run が出ることを確認する

追加直後のリポジトリは **After every push**（最もレビュー回数が多い設定）で始まる。

### 3.2 review level

| level | 内容 |
|---|---|
| Quick | 軽いパス。最速・最安 |
| Standard | 深さ・速度・コストのバランス。**既定** |
| Deep | 最も徹底したパス。最も時間とコストがかかる |

組織の既定を 1 つ選び、リポジトリごとに上書きできる（例: 定型的なコードベースは Quick、重要なものは Deep）。変更は、変更後に始まるレビューから効く。

### 3.3 Review runs（いつレビューするか）

リポジトリごとの設定である。

| 選択肢 | 動き |
|---|---|
| **Once after PR creation** | PR の open / reopen / ready for review でレビュー |
| **After every push** | PR ブランチへの push ごとにレビュー。修正された指摘のスレッドを自動で resolve する |
| **Manual (@claude review)** | open や push ではレビューしない。`@claude review` で 1 回、`@claude review always` で以降の push も対象にする |

- どの選択肢でも、**draft と fork からの PR は自動レビューの対象外**（コメントコマンドなら draft・fork でも動く）
- GitHub organization の行で Review runs を設定すると、App がアクセスできる全リポジトリ（後から追加されたものを含む）を一括でカバーする。github.com の organization のみで、月額の使用量上限の設定が前提
- **Show tips on pull requests**（既定 on）は、レビューが始まらない理由（Manual 設定・fork・権限の無いコメント・未 link）を PR に短いコメントで知らせる

開発者が Owner 権限なしでできるのは、`@claude review` によるレビュー依頼、`@claude review always` による push ごとのレビュー購読、`REVIEW.md` / `CLAUDE.md` のコミットによる指摘内容の調整である。

---

## 4. リポジトリ内の設定ファイルの読み方

指摘の内容は、リポジトリにコミットした 2 種類のファイルで調整する。

| ファイル | 役割 | 読まれる範囲 |
|---|---|---|
| `CLAUDE.md` | Claude Code 全般のプロジェクト指示。Code Review もプロジェクト context として読み、違反を指摘にする | **root** と、**変更ファイルの親ディレクトリ**にある `CLAUDE.md` |
| `REVIEW.md` | レビュー専用の指示（何をどの重大度で指摘し、何を飛ばすか） | root。サブディレクトリの `REVIEW.md` は、その配下の変更に root のものに追加して効く（ブランチ保護の条件あり、§4.3） |

`REVIEW.md` は自由形式の Markdown で、レビューの「形式」ではなく「何を見つけて報告するか」を変える。公式が挙げる使い方は、Important の定義の再調整、Nit の上限、生成ファイル・lockfile・CI が既に見ている項目の除外、チーム独自ルールの追加、指摘に `file:line` の根拠を求めること、である。全般的な context は `CLAUDE.md` に置き、`REVIEW.md` はレビュー挙動を変える指示に限る。

### 4.1 `@` で他のファイルを取り込む

root の `REVIEW.md` に、`@` とファイル名だけの行を書くと、その行がファイルの中身に置き換わる。

| 制約 | 内容 |
|---|---|
| 置き場所 | `REVIEW.md` と同じ **リポジトリ root**（skill を除き、`@docs/review-rules.md` のようなサブディレクトリは取り込まない） |
| 階層 | 1 段だけ。取り込んだファイルやサブディレクトリの `REVIEW.md` 内の `@` 行はプレーンテキストのまま |
| ファイル数 | 異なるファイルは **最大 8 個** |
| サイズ | `REVIEW.md` と取り込むファイルの合計で **150,000 bytes 未満**。上限に達するファイルは途中で切らず丸ごと飛ばす |
| Markdown リンク | 合計 **64 個以下**（`http` / `https` / `mailto` / `#` アンカーは数えない）。超えると root の `REVIEW.md` 全体が飛ばされる |
| 前提 | 保護されたブランチから `REVIEW.md` を読むときだけ取り込む。保護されていない default branch では `@` 行がプレーンテキストのまま残る |

### 4.2 skill を取り込む（実行はしない）

`@.claude/skills/<folder>/SKILL.md` の行で、skill の本文をレビュー指示として取り込める。ただし **Code Review は skill を実行しない**。

- `SKILL.md` は **30,000 bytes 以下**（frontmatter 込み）。8 ファイル・150,000 bytes の上限にも数える
- symlink はたどらない（ファイル自体でもパス途中のフォルダでも）。通常のテキストファイルとしてコミットする
- 取り込むのは `SKILL.md` の本文だけ。frontmatter の内容・`!` コマンドの出力・`$ARGUMENTS` などの置換・補助ファイル・`@file` 参照は届かない
- 除外ルールと Nit の上限は skill ではなく `REVIEW.md` 側に書く（skill の文面は根拠として受け付けない）
- bundled / personal / plugin の skill や `.claude/` 配下の他のファイルは直接取り込めない。`REVIEW.md` の隣にコピーして取り込む

### 4.3 どのブランチの版を読むか

`REVIEW.md` は **PR の base branch か default branch の版**を読み、**PR 自身の変更からは決して読まない**。`REVIEW.md` を変えたいときは、先にその変更をマージする。読む版はブランチ保護の状態で決まる。

| ブランチ保護 | 読む版 | 読むファイル |
|---|---|---|
| default branch が保護され、PR がそこ（または ruleset の無いブランチ）を向く | default branch | root・取り込み・サブディレクトリ |
| PR が ruleset で保護された別ブランチを向く | その base branch | root・取り込み・サブディレクトリ |
| default branch が無保護で、base branch にも保護ルールが無い | default branch | root のみ |
| 保護設定を確認できない | なし | なし |

「重大度を下げる」「パス・ファイル・種類の除外」「Nit の上限」の指示は、保護された default branch の root `REVIEW.md` から読んだときに守られる。公式は default branch に `REVIEW.md` を置き、そのブランチを保護することを勧めている。

---

## 5. PR での読み方とコメントコマンド

### 5.1 重大度

| マーカー | 重大度 | 意味 |
|---|---|---|
| 🔴 | Important | マージ前に直すべきバグ |
| 🟡 | Nit | 直す価値はあるがブロックしない軽微な問題 |
| 🟣 | Pre-existing | この PR が持ち込んだのではない、既存のバグ |

推論が記録されていれば、指摘に折りたたみの **Why this was flagged** が付く。

### 5.2 指摘への対応

- **コードを変えずに却下**: GitHub でスレッドを自分で resolve する。返信だけでは却下にならない
- **修正**: コードを直して push する。次のレビューが修正済みと判断すればスレッドを resolve する
- **反論・説明**: コメントに返信する。Claude はすぐには応答せず、返信でレビューは始まらない。次のレビューが返信を読み、resolve するか 1 回だけ返信する

push 後に check run が **Code review skipped — no new changes** / **Code review not repeated — earlier findings still open** になったら、新しいレビューを走らせずに前回の結果を残している（空 commit・base のクリーンな merge / rebase で差分の行が同じ場合など）。自動で始まった後続レビューは、前回からの変更に絞り Nit と Pre-existing を減らす。PR 全体をもう一度見るには `@claude review` を使う。

check run の Details の最終行には `<!-- bughunter-severity: {...} -->` の形で重大度ごとの件数が JSON で入る。自前の CI でマージを止めたいときは `gh api` と jq でこの行を読む（`normal` が Important の件数）。

### 5.3 コメントコマンド

| コマンド | 動き |
|---|---|
| `@claude review` | 1 回だけレビューする。以降の push は購読しない |
| `@claude review always` | レビューし、以降の push でもレビューするよう PR を購読する |
| `@claude review once` | `@claude review` と同じ |
| `@claude review stop` | push ごとのレビューの購読をやめる。レビューは始めず、実行中のものも止めない |
| `@claude review off` / `@claude review pause` | `@claude review stop` と同じ |

コマンドが効く条件:

- **新しい top-level の PR コメント**として投稿する（inline コメント・review body・既存コメントの編集は不可）
- コマンド全体をコメント冒頭の 1 行に書く（後ろに文章を続けてよい。大文字小文字は問わない）
- 投稿者がリポジトリに **write / maintain / admin** 権限を持つ（fork の PR では base リポジトリの権限）。bot のコメントではレビューは始まらない
- PR が open である

受け付けられると check run が **Code review queued...** → **Code review in progress...** と変わる。👀 リアクションはレビューが始まらない場合にも付くため、check run で確認する。**After every push** のリポジトリでは push で必ずレビューが走るので、コメントでは止められない（止めたい PR は draft にする）。

> **2026-07 の更新より前の挙動**: `@claude review` は PR を push ごとのレビューに購読させていた。その挙動に依存していた場合は `@claude review always` を使う。

### 5.4 GitHub Actions の claude-code-action と併用する場合

公式は、同じリポジトリで **Claude Code GitHub Action を interactive mode・既定の trigger phrase `@claude` のまま**動かしていると、`@claude review` のコメントで **Action も起動する**と注意している。両者を分けるには、Action の `trigger_phrase` 入力を別の文字列にする。

本リポジトリの正本 workflow（[github-actions-claude-code-review.md §2](github-actions-claude-code-review.md#2-正本-workflowコピペ用全文)）は `on: pull_request` だけで起動し、`issue_comment` などのコメントトリガーを持たないため、現状は `@claude review` で起動しない。コメントで反応する `@claude` 応答用の workflow を別途追加し、かつマネージド Code Review も有効にする場合は、`trigger_phrase` を変える。

---

## 6. 料金と使用量

| 項目 | 内容 |
|---|---|
| 課金方式 | トークン使用量に応じて **usage credits** から課金。プランに含まれる使用量とは別。1 レビューあたりの定額は無い |
| 請求先 | **組織**（PR の作成者やレビューの依頼者ではない）。Bedrock / Agent Platform / Foundry を他機能で使っていても Anthropic の請求に載る |
| 1 回のコストを決める要素 | review level、変更の大きさ、周辺コードの複雑さ、検証が必要な候補の数 |
| 回数を決める要素 | Review runs の設定。After every push は push 数に比例して増える。`@claude review always` は Once / Manual のリポジトリで push ごとのコストを追加する |
| 専用の上限 | [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) で **Claude Code Review サービス専用の月額上限**を設定できる（組織全体に効く） |
| 上限に達したとき | Code Review 専用上限・組織全体の月額上限・usage credits 残高のいずれかが尽きると、**レビューを skip する**。残りが 1 回分の見込みコストを下回っても skip する。PR には「⚠️ Code review skipped」で始まるコメントが付く |
| 使用状況 | [claude.ai/analytics/code-review](https://claude.ai/analytics/code-review) で、レビュー済み PR 数・当月コスト・自動 resolve された指摘数・重大度別の件数・リポジトリ別の内訳を見る。analytics の金額は定価ベースの推定で、請求額とは異なりうる |

公式は、全面展開の前に月額上限を設けて少数のリポジトリで Once / Manual で試し、admin ページの **Average cost** 列から月額を見積もる手順を勧めている。

---

## 7. トラブルシューティングの要点

まず PR の **Claude Code Review** check run のタイトルを見る。

| check run のタイトル | 意味 | 対処 |
|---|---|---|
| Code review queued... / in progress... | 未完了 | 待つ |
| Code review found no issues | 完了・指摘なし | 2 回目以降なら review body で「投稿しなかった件数」を確認 |
| 指摘ありのタイトル | 完了・指摘あり | inline に見えなければ check run の Details、Files changed の annotation、review body の **Additional findings** を見る |
| Code review skipped — no new changes / not repeated — earlier findings still open | push で前回の結果を残した | `@claude review` でレビューを強制する。後者は Important の修正 push でも可 |
| Code review failed / timed out | 未完了 | `@claude review` か、fork でなければ check run の **Re-run** |
| Code review declined | 実行されなかった | summary を読む。予算・上限なら §6 |
| check run なし | 始まっていない | `@claude review` を投稿。それでも出なければ、リポジトリが追加されているか・コメント条件・write 権限・予算を確認 |

- セッションが中断したレビューは 1 回だけ自動で再試行され、check run の summary にその旨が出る
- check run が `REVIEW.md` に触れるメッセージを出したら、§4.1 / §4.3 の条件（ブランチ保護・リンク数・取り込みの制約）を確認する
- テスト PR に check run が出ないときは、Allow code review が on か、リポジトリが一覧にあるか、App がアクセスできるか、draft でないか、Manual 設定でないかを確認する

---

## 8. ローカルの `/code-review` との関係

ローカルの `/code-review` は、Claude Code のセッション内で動く **bundled skill** であり、マネージド Code Review とは別物である。

- **どのプランでも使え**、セッションのプラン使用量または API 課金に数える
- バックグラウンドの subagent として動き、結果は会話に届く（`--fix` で作業ツリーに適用、`--comment` で PR に inline コメント投稿）
- `CLAUDE.md` は読むが、**`REVIEW.md` は読まない**。公式は「両方に効かせたい指示は `CLAUDE.md` に、PR レビュー専用のルールは `REVIEW.md` に」と勧めている
- **Claude が自分から起動できる**（平易な言葉でレビューを頼んだとき、または session-scoped の scheduled task から）。**v2.1.246 より前**は、Anthropic から取得する feature flag が有効な場合だけ自発起動していた。自発起動を止めて手打ちだけにするには `skillOverrides` で `"code-review": "user-invocable-only"` を設定する（[Let Claude start the review](https://code.claude.com/docs/en/code-review-local#let-claude-start-the-review)）
- `/code-review ultra` はクラウドの ultrareview に昇格する（claude.ai アカウントが必要、ZDR / HIPAA / CMEK・Bedrock 等では不可）

詳細は [slash-commands.md](slash-commands.md) の `/code-review` の項を参照する。

---

## 9. 3 つのレビュー手段の比較

| 観点 | マネージド Code Review | ローカルの `/code-review` | GitHub Actions の claude-code-action |
|---|---|---|---|
| 本リポジトリの doc | 本 doc | [slash-commands.md](slash-commands.md) | [github-actions-claude-code-review.md](github-actions-claude-code-review.md) |
| 起動 | リポジトリごとの Review runs 設定に従う PR の活動、または `@claude review` | ユーザーがコマンドを打つ。Claude の自発起動・scheduled task も可 | workflow のトリガー（本リポジトリは `pull_request`） |
| 実行場所 | Anthropic のインフラ | 自分の Claude Code セッション | 自分の GitHub Actions runner |
| 使える人 | Team / Enterprise の組織（Owner が有効化）。ZDR / HIPAA / CMEK は不可 | 全プラン | Claude API キーまたはクラウドプロバイダの認証情報（本リポジトリは `CLAUDE_CODE_OAUTH_TOKEN`）を持つ人 |
| 設定 | Admin settings + Claude GitHub App。**workflow 不要** | 不要 | workflow ファイル・secret・`permissions`・`--allowedTools` |
| 課金 | usage credits から組織へ。専用の月額上限あり | セッションのプラン使用量 / API 課金 | 使う認証情報の課金先（本リポジトリはサブスクリプションの OAuth token） |
| 読む指示 | `CLAUDE.md`（root + 変更ファイルの親）と `REVIEW.md`（base / default branch の版） | `CLAUDE.md`（`REVIEW.md` は読まない） | workflow の `prompt` に書いた指示 |
| 出力 | inline コメント + review body + check run（failure にならない） | 会話内の報告（`--comment` で PR に投稿、`--fix` で適用） | prompt の指示どおり（本リポジトリは `gh pr comment` + inline コメント） |
| レビュー観点の調整 | review level（Quick / Standard / Deep）と `REVIEW.md` | effort level と `--max-findings` | prompt を自由に書く |

公式の比較表には、ほかに **Ultrareview**（クラウドサンドボックス、claude.ai アカウントが必要）と、**自作の reviewer subagent / skill** も並んでいる。

---

## 関連ドキュメント

- [Claude で書いたコードを、なぜ Claude にレビューさせるのか](why-ai-review-ai-code.md) — 書いた Claude とは別の Claude にレビューさせる理由と限界
- [GitHub Actions で Claude Code レビュー BOT を設定する](github-actions-claude-code-review.md) — 自前の runner で動かす claude-code-action の正本 workflow
- [ClaudeCode スラッシュコマンドガイド](slash-commands.md) — ローカルの `/code-review` / `/review` / `/simplify`
- [ClaudeCode Skills ガイド](skills.md) — `REVIEW.md` から取り込む `SKILL.md` の書き方、bundled skill
- [ClaudeCode メモリガイド](memory.md) — Code Review も読む `CLAUDE.md` の階層
- 公式:
  - [Code Review](https://code.claude.com/docs/en/code-review)
  - [Set up Code Review](https://code.claude.com/docs/en/code-review-setup)
  - [Customize Code Review](https://code.claude.com/docs/en/code-review-customize)
  - [Read and request reviews on a pull request](https://code.claude.com/docs/en/code-review-pull-requests)
  - [Code Review costs and usage](https://code.claude.com/docs/en/code-review-costs)
  - [Troubleshoot Code Review](https://code.claude.com/docs/en/code-review-troubleshooting)
  - [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local)
  - [Code Review is now generally available（article, 2026-10-15）](https://claude.com/resources/articles/code-review-is-now-generally-available)
