# ClaudeCode セッション履歴と `--resume`（ディレクトリリネーム手順含む）

> 出典: [Manage sessions](https://code.claude.com/docs/en/sessions) / [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Built-in commands](https://code.claude.com/docs/en/commands) / [External agents (ACP)](https://zed.dev/docs/ai/external-agents) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) / [Claude directory](https://code.claude.com/docs/en/claude-directory) / [Settings reference](https://code.claude.com/docs/en/settings-reference) / DeepWiki [anthropics/claude-code](https://deepwiki.com/anthropics/claude-code) (2026-09-03 確認)

ClaudeCode の会話履歴（セッション）は `~/.claude/projects/` 配下に JSONL ファイルとして永続化される。この doc は **セッション履歴ストアの仕組み**・**`claude --resume` がどのセッションを一覧表示するかのロジック**・**プロジェクトディレクトリを安全にリネームする手順**を扱う。`config-files.md`（設定ファイルという成果物の解説）と対をなす「セッション履歴という成果物とその保全」の SSOT である。

> **`slash-commands.md` の「セッション管理」との違い**: `slash-commands.md` は `/resume` `/rewind` `/rename` `/branch` といった **UX レベルのセッション操作**を扱う。本 doc は **ディスク上の JSONL ストアとその突合・保全**という別レイヤーを扱う。
>
> **公式仕様と実証知見の区別**: 本 doc には公式 docs に明記がない**実機検証ベースの事実**が含まれる。各表で「公式 / 実証」を明示し、実証部分は再現条件を併記する。

---

## 1. セッション履歴ストアの仕組み

### 保存場所と命名

セッションの会話履歴（transcript）は、作業ディレクトリ単位でグループ化された JSONL として保存される。

```
~/.claude/projects/<encoded-cwd>/<session-id>.jsonl
```

- `<encoded-cwd>`: 作業ディレクトリの絶対パスの **非英数字を `-` に置換**した文字列。⚠️ **変換後の名前が 200 文字を超える場合、200 文字に切り詰めたうえでフルパスのハッシュが付加される**（2026-09-03 追記。設計仕様として公式に明記されている）。**深いパスでは後述の `tr -c '[:alnum:]' '-'` による導出が一致しない**ため、その場合は実ディレクトリを直接探す。
  例: `/Users/yoshi/work/dev/my-projects/jarvis` → `-Users-yoshi-work-dev-my-projects-jarvis`
  > ⚠️ **`/` だけの置換ではない**（2026-08-12 訂正）。`.` や `_` などの記号も `-` になるため、**ドットやアンダースコアを含むディレクトリ名では `tr '/' '-'` による導出が一致しない**。§3 の runbook もこの前提で読むこと。
- `<session-id>`: セッションごとの UUID。`claude --resume <session-id>` で直接指定できる。
- サブディレクトリ:
  - `<session-id>/subagents/agent-*.jsonl` … サブエージェントの transcript
  - `<session-id>/tool-results/*.txt` … 大きなツール出力の退避先

> 公式 docs（[Manage sessions](https://code.claude.com/docs/en/sessions)）でも、transcript が `~/.claude/projects/<project>/<session-id>.jsonl` に保存され、`<project>` が作業ディレクトリパスから導出されると明記されている。

> **`/cd` による移動（v2.1.169〜）**: セッション中に `/cd <path>` で作業ディレクトリを変えると、**セッションストレージが新 dir の project ストア配下へ移動**し、`--resume` / `--continue` は新 dir から会話を見つける（=`<encoded-cwd>` グループが変わる）。この挙動は §3 のディレクトリリネーム手順とは別の正規ルートである。なお `/add-dir` はアクセス追加のみでストアは移動しない。出典: [Commands](https://code.claude.com/docs/en/commands)。
>
> **v2.1.196 での挙動改善**:
> - 移動したセッションは **crash / 強制終了後も旧 dir の picker に出ない**(以前は復帰時に旧位置に再登場する場合があった)
> - `claude --resume <name>` / `/resume <name>` は **exact match なら直接 resume** する。⚠️ **曖昧な場合の挙動は両者で異なる**（2026-09-03 訂正）: **`claude --resume <name>` は名前を検索語としてプリフィルした picker を開き、`/resume <name>` はエラーを返す**
> - **セッション名の重複時は自分側が自動リネームされる**（v2.1.232〜）: 既存の live セッションと同名を使うと `auth-refactor-graceful-unicorn` 形式の 2 語サフィックス付きに改名される（AI 生成タイトル・default 表示名・background / `-p` の `--name`・旧バージョンのセッションは対象外）
> - 名前なしセッションに **default 表示名 auto-generation**(例 `my-app-3f`、agent-view / `claude agents --json` に表示。resume の handle にはならない)
> - **`--from-pr <number>`** サポート: GitHub PR 番号を渡してセッションを開始できる (PR 差分と PR 本文がコンテキストに入る)
> - **`claude --resume <session-id>` が SDK / headless セッションでも動作**(以前は対話セッション限定)
>
> **v2.1.198 以降の追加**:
> - **post-compaction session naming が最初の prompt を参照**するようになった。auto-compaction 後もセッション名が意味的に維持される
> - **`--no-session-persistence`** CLI フラグ (**単発 non-interactive run で transcript write を抑止**する。scratch な `-p` 実行で `~/.claude/projects/` が汚れなくなる)
> - **`Ctrl+B`** session picker で **current git branch フィルタ** (worktree 別に piv したセッションを見つけやすくなった)

> **Background sessions のプロセス跨ぎ永続化(v2.1.197〜)**: `claude` プロセスの停止・再起動・アップデートを跨いで、長時間コマンド・ワークフローが survive するようになった。Windows でも background shell を kill せず handoff する。長時間タスク進行中の `claude` アップデート適用が安全になった。出典: CHANGELOG v2.1.197。

### transcript の保持期間と保存先の制御

**transcript は無期限には残らない**。本 doc は「履歴の保全」を主題にするため、消える条件を先に押さえる。

| 項目 | 内容 |
|---|---|
| **自動削除** | **既定 30 日**で削除される（設定キーは **`cleanupPeriodDays`**、最小 1）。⚠️ **2026-09-03 訂正**: 削除は「起動時」ではなく **セッション開始後のバックグラウンド sweep** で実行される（保持期間を安全に判定できる場合に限る）。**`0` は validation エラー**なので、長期保持したい場合は `3650` 等を指定する。あわせて **`desktopSessionCleanupPeriodDays`**（v2.1.248〜、user / managed のみ）で Desktop / Cowork transcript に別の年齢上限を掛けられるが、**`cleanupPeriodDays` との AND 判定**なので既定 30 日環境で `7` を入れても 30 日保持になる |
| **`<project>` ディレクトリ名の固定** | **`CLAUDE_CODE_PROJECT_DIR_NAME`**（v2.1.234〜）を `CLAUDE_CONFIG_DIR` と併用すると、起動リポジトリに関係なく `<config dir>/projects/<その名前>/` を使う。**1〜64 文字の英数字・ハイフン・アンダースコア**。⚠️ **`CLAUDE_CONFIG_DIR` 未設定時は無視され、起動シェルの環境からのみ読まれる**（settings の `env` ブロックからは設定できない）。**§3 のディレクトリリネーム runbook の代替手段**になる。auto memory も同ディレクトリ配下に置かれる |
| **保存先の変更** | `CLAUDE_CONFIG_DIR` で `~/.claude` 自体の位置を変えられる。ストアごと別ボリュームへ逃がす場合に使う |
| **transcript 書き込みの抑止** | ⚠️ **2026-09-03 訂正**: `CLAUDE_CODE_SKIP_PROMPT_HISTORY` は `~/.claude/history.jsonl` 限定ではなく、**全モードで transcript の書き込み自体を抑止する**。公式表の行は "Suppress transcript writes in all modes" であり、`--no-session-persistence`（print mode 限定）の「any mode」版にあたる |
| **単発実行での抑止** | `--no-session-persistence`（v2.1.198〜）で transcript 自体を書かない |

> **長期保全したい記録は 30 日以内に別の場所へ退避する必要がある**。本リポジトリの `/report-session` `/handoff` のように「セッションの内容を成果物として残す」運用は、この保持期間があるからこそ意味を持つ。

### v2.1.222〜v2.1.224 の重要な変更

- **【最重要】`claude --resume <session-id>` がマシン全体スコープに拡大**(v2.1.223): 公式は「**from any directory** … then in **every other project on this machine**」と記載する。**セッション ID さえ分かれば、どのディレクトリからでも再開できる**。§3 のディレクトリリネーム手順は「ピッカーに出す」ための整合作業であり、**ID 直指定での復元自体はリネーム前後を問わず可能**である点が、より明確になった。
- **worktree isolation が Bash と git redirect にも適用**(v2.1.222): 従来はファイル編集ツールのみの隔離で、**Bash 経由やリダイレクトでメイン checkout を破壊できた**。全セッション種別とその subagent に適用される。
- **長いプロジェクトパスの越境バグを修正**(v2.1.224): **200 文字を超える絶対パス**のプロジェクトで、`<encoded-cwd>` が**別プロジェクトのセッションディレクトリに解決される**問題があった。list / rename / fork / delete / `/resume` がプロジェクト境界を越えて別プロジェクトのセッションを操作しうる状態だった。深い階層で作業する場合は v2.1.224 以上を使う。
- **`claude --teleport <session id>`**(v2.1.223): クラウド（Claude Code on the web）のセッションをローカルターミナルに引き込む。クラウドセッション側にも `/teleport` のヒントが表示される。
- 出典: [Manage sessions](https://code.claude.com/docs/en/sessions) / CHANGELOG v2.1.222 / v2.1.223 / v2.1.224

### JSONL の中身（絶対パスを持つフィールド）

各 JSONL は 1 行 = 1 イベントの JSON（`type` 別に `user` / `assistant` / `system` / `summary` 等）。リネーム時に問題になる「絶対パスを保持するフィールド」は次のとおり。

| フィールド | 内容 | リネーム時の影響 |
|---|---|---|
| `cwd` | そのイベント時点の作業ディレクトリ（絶対パス） | **`--resume` の突合キー。置換漏れすると履歴がピッカーから消える** |
| `timestamp` | イベントの ISO8601 時刻 | パスを含まない。`X ago` 表示の復元に使える（後述） |
| `gitBranch` | git ブランチ名 | パスを含まない |
| `head_at_capture` / `baseline_sha` 等 | git 状態（SHA・ファイル名のみ） | **絶対パスは保持しない** |

> **重要（実証）**: 絶対パスを保持しているのは事実上 `cwd` のみ。`head_at_capture` 等の git 系フィールドは SHA・ファイル名だけで絶対パスを持たない。したがってリネーム時に整合を取るべき本質的なフィールドは `cwd` である（2026-06-08 実機確認 + DeepWiki `anthropics/claude-code`）。

**transcript の記録内容・サイズに関する変更（v2.1.208〜v2.1.219）**:

| 変更 | 内容 |
|---|---|
| **effort level の記録**（v2.1.212〜） | **各 assistant メッセージに reasoning effort level が記録される**。セッション後から「どのターンをどの effort で回したか」を追える |
| **サイズの大幅削減**（v2.1.208〜） | superseded な file-history backup を剪定するようになり、transcript サイズが**最大 79 倍**削減された |
| **保存失敗時の警告**（v2.1.217〜） | transcript の書き込み失敗（ディスクフル等）や、環境変数の継承でセッション保存が off になっている場合に**警告を出す**（以前は無言でセッションを失っていた） |
| **subagent の text 転送**（v2.1.211〜） | `--forward-subagent-text` / `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` で **stream-json に subagent の text / thinking を含められる**。v2.1.219 では **depth-2 以上の nested subagent も転送対象**になり、**spawn 元 Agent の `tool_use` id をキーに紐づく**（JSONL 解析側で親子関係を復元できる） |

> JSONL を解析するスキル（`/report-session` 等）を書く場合、**effort level フィールドの追加**と **nested subagent の `tool_use` id 紐付け**は解析対象として有用である。

> ### ⚠️ 公式は JSONL の直接パースを非推奨としている（2026-08-12 追記）
>
> 公式 [Manage sessions](https://code.claude.com/docs/en/sessions) は、transcript の JSONL 形式について「**internal to Claude Code and changes between versions**」と明記し、内容を機械処理する場合は **`/export`** やスクリプトインターフェース経由を使うよう推奨している。
>
> **本リポジトリはこれを承知の上で直接パースを採用している**。`/report-session` `/handoff` `copy-session-path` は、`/export` では取れない粒度（subagent の transcript、tool_use id の親子関係、effort level、tool-results への退避ファイル）を扱うため、現時点で代替手段がない。
>
> **その代わり、次のリスクを受け入れている**:
>
> - ClaudeCode のアップデートで**予告なくスキーマが変わりうる**（実際、v2.1.208 の backup 剪定・v2.1.212 の effort 記録・v2.1.219 の nested subagent キー付けでフィールドは変化してきた）
> - 解析スクリプトは**壊れる前提**で書く（未知フィールドを無視し、`errors=replace` でデコードし、dict / str の型ガードを入れる）
>
> **公式仕様に依拠したい場合は `/export` を使う**。「壊れても自分で直せる範囲か」で選択する。

### `~/.claude/history.jsonl` は別物

混同しやすいが、`~/.claude/history.jsonl` は **`--resume` とは無関係**である。

| ファイル | 役割 | `--resume` が参照するか |
|---|---|---|
| `~/.claude/projects/<encoded>/<id>.jsonl` | セッション会話履歴（transcript） | **する**（これが実体） |
| `~/.claude/history.jsonl` | `Ctrl+R` で呼ぶ**プロンプト入力履歴**専用・全プロジェクト共通の単一ファイル | **しない** |

> 出典: DeepWiki `anthropics/claude-code` — 「The resume picker for sessions (`claude --resume`) operates on the session `.jsonl` files, not `history.jsonl`.」

---

## 2. `claude --resume` の表示ロジック

ピッカーに出る／出ないは、以下のルールの組み合わせで決まる。

| ルール | 種別 | 内容 |
|---|---|---|
| **他 worktree / 無関係プロジェクトを選んだ時** | 公式 | 同一リポの**別 worktree のセッションはその場で resume** される（worktree が消えていれば現ディレクトリで resume）。**無関係プロジェクトのセッションは resume せず、`cd` + resume コマンドをクリップボードにコピーする**（ディレクトリが消えていれば現ディレクトリで resume）。§5 のディレクトリリネーム後のトラブルシュートで直接効く（2026-09-03 追記） |
| **`cwd` 突合** | 公式 | ピッカーは「**現在の worktree**、および `/add-dir` で追加したディレクトリ」のセッションを絞り込む。**`Ctrl+W` で全 worktree、`Ctrl+A` で全プロジェクトへスコープを広げられる**。出典: [Manage sessions](https://code.claude.com/docs/en/sessions) |
| **`--continue` の除外条件** | 公式 | `claude --continue` は **background セッション・`-p` / SDK セッション・最初のプロンプトが `/loop` のセッションをスキップ**する。⚠️ ただし **`claude -p --continue` は `-p` / SDK / `/loop` を含め、background だけは依然スキップ**するという非対称性がある（2026-09-03 追記） |
| **`-p` / Agent SDK セッション** | 公式 | **ピッカーには出ない**。ただし `--resume <session-id>` の直指定では再開できる |
| **アクティブセッション除外** | 実証 | 現在稼働中（書き込み中）のセッションはピッカーから除外される。複数の Zed タブ等を同時に開いていると、それら全てが候補から外れる。**2026-08-12 時点の公式 docs にこの記述は見当たらず**（background セッションはむしろ `bg` マーク付きで表示される）、種別を「公式/実証」から**実証**へ格下げした |
| **`X ago` の表示順** | 実証 | 表示の新しさ順は**ファイルの mtime 起源**。一括書き換えで mtime が揃うと全件が同じ `X ago` になる（2026-06-08 実機確認） |
| **`--resume <id>` 直指定** | 公式 | セッション ID を直接渡す場合は `cwd` フィルタを**迂回**する。`cwd` が旧パスのままでも特定セッションへの復元自体は可能。**v2.1.223 以降はマシン全体がスコープ**になり、「any directory から、このマシン上の every other project のセッションを」再開できると公式が明記した（それ以前は project dir スコープ） |
| **resume 時に復元されないもの** | 公式 | permission mode の **`plan` / `bypassPermissions` は復元されない**。CLI 側の `--mcp-config` / `--settings` / `--plugin-dir` / `--fallback-model` / `--add-dir` も**復元されない**ため、再開時に渡し直す必要がある。**10 万トークンを超えるセッションの再開時は 3 択ダイアログ**（そのまま / compact / 新規）が出る |
| **`/loop` 起点セッションの除外** | 公式 | **最初のプロンプトが `/loop` だったセッションはピッカーに出ない**（v2.1.211〜）。会話の途中で `/loop` を使った場合は隠れない。**v2.1.211 より前は、会話初期に `/loop` を使うとそのセッションが恒久的にピッカーから隠れていた**。出典: [Manage sessions](https://code.claude.com/docs/en/sessions) |
| **agent view 内の `/resume`** | 公式 | v2.1.212 以降、agent view 内で `/resume` を実行すると**削除済みを含む過去セッションのピッカー**が開き、選んだ会話は **background セッションとして再開**される（フォアグラウンドの復元とは別経路）。出典: CHANGELOG v2.1.212 |

### セッションを増やす 3 経路の違い（`/branch` / `/fork` / `/subtask`）

`docs/slash-commands.md` の UX レベルの説明と対応させると、**ディスク上のセッション同一性**は次のように分かれる。**v2.1.212 で `/fork` の意味が変わった**ため、旧来の理解のままだと JSONL の対応付けを誤る。

| コマンド | 新しいセッションができるか | ピッカーでの見え方 |
|---|---|---|
| `/branch [name]` | **できる**（独自の session ID を持つ） | **別行として出る**。自分がその複製へ移る |
| **`/fork [prompt]`**（v2.1.212〜） | **できる**（独立した background セッション） | agent view に独自の行を持つ。元の会話には自分が留まる |
| **`/subtask <instruction>`**（v2.1.212〜） | できない（会話内 subagent） | セッションとしては現れない。結果が元の会話に戻る |

> ⚠️ **v2.1.221 で `/fork` は独自の worktree を作るようになった（作業ツリーの同一性も分かれる）**: 公式 CHANGELOG は「Changed sessions forked with `/fork` to create a **new worktree of their own** instead of working in the original session's checkout」と記述している。v2.1.220 以前は「セッションは別だが**作業ツリーは元セッションと同じ checkout**」だったため、fork 先の編集が元の作業ツリーに直接現れていた。
>
> **v2.1.221 以降の調査時の注意**: fork 先セッションの成果物は**元のリポジトリ作業ツリーではなく worktree 側にある**。「fork したのに変更が見えない」場合は `git worktree list` で fork 先の作業ツリーを確認する。JSONL 側は従来どおり独立した session ID を持つ。出典: CHANGELOG v2.1.221

- `--fork-session` + `--resume` / `--continue` でも独自 session ID のセッションができる。
- **`SessionStart` hook の `source`**: 上記の fork 系（`--fork-session`、`/fork` の background コピー、`/branch`）は **v2.1.214 以降 `"fork"`** が渡る（それ以前は `"resume"` に含まれていた）。hook で resume 時だけ処理していると fork 時に発火しなくなる（[hooks.md](hooks.md) 参照）。
- **v2.1.218 の修正**: headless / SDK で **compaction 後に fork-session の系譜（lineage）が失われる**不具合が修正された。

### 「ファイルはあるのに履歴が出ない」の典型原因

`~/.claude/projects/<encoded>/` に JSONL が物理的に存在するのにピッカーが空 → **JSONL 内の `cwd` が現在の cwd と一致していない**ことをまず疑う。ディレクトリリネーム後に最も起きやすい（§3 / §5）。

---

## 3. プロジェクトディレクトリを安全にリネームする手順（runbook）

ディレクトリ名を変えるときは、以下の **5 ステップを必ずセットで実施する**。1 つでも欠けると `--resume` ピッカーが壊れる。`$OLD` / `$NEW` は環境に合わせて置き換える。

```bash
OLD="/abs/path/to/old-name"
NEW="/abs/path/to/new-name"
# ClaudeCode は「非英数字」を '-' に置換する。'/' だけでなく '.' '_' 等も対象になる
# printf を使う（echo だと末尾改行まで '-' に変換されてしまう）
OLD_ENC="$(printf '%s' "$OLD" | tr -c '[:alnum:]' '-')"   # 例: -abs-path-to-old-name
NEW_ENC="$(printf '%s' "$NEW" | tr -c '[:alnum:]' '-')"
# 導出結果が実在するか必ず確認する（一致しない場合は ls で実物を探して手で指定する）
ls -d "$HOME/.claude/projects/$OLD_ENC" || echo "encoded 名が一致しない。ls ~/.claude/projects/ で実物を確認せよ"

# 0. 該当プロジェクトの ClaudeCode セッションを全て終了する
#    （pgrep -x claude では他プロジェクトの claude も拾うため、lsof で cwd を確認して個別判定する。§4 参照）

# 1. バックアップ（mtime 保持のため -p を必ず付ける。再実行・複数プロジェクトでの上書きを防ぐためサブディレクトリを明示）
mkdir -p ~/claude-migrate-backup-projects
cp -Rp ~/.claude/projects/"$OLD_ENC" ~/claude-migrate-backup-projects/"$OLD_ENC"

# 2. プロジェクトフォルダ自体をリネーム
mv "$OLD" "$NEW"

# 3. エンコード済み履歴ディレクトリをリネーム
mv ~/.claude/projects/"$OLD_ENC" ~/.claude/projects/"$NEW_ENC"

# 4. JSONL 内部の絶対パス + エンコード形を再帰置換（perl で GNU/BSD 非依存）
find ~/.claude/projects/"$NEW_ENC" -type f \( -name '*.jsonl' -o -name '*.txt' -o -name '*.md' \) -exec \
  perl -pi -e "s|\Q$OLD\E|$NEW|g; s|\Q$OLD_ENC\E|$NEW_ENC|g" {} +

# 5. 検証: 旧パス（絶対パス + エンコード形）を含むファイルが 0 件であること
#    basename だけで grep すると会話本文中の旧ディレクトリ名に誤マッチするため、フルパス + エンコード形で検証する
#    -F（固定文字列）でパス中の '.' 等が正規表現メタ文字として誤マッチするのを防ぐ
grep -rlF -e "$OLD" -e "$OLD_ENC" ~/.claude/projects/"$NEW_ENC"
```

### 各ステップの根拠

| ステップ | 根拠 |
|---|---|
| step 1 で `-p` 必須 | バックアップを「ロールバック元」として機能させるため。macOS デフォルトの `cp -R` は mtime を保持しないため、`-p` なしだと後述の mtime 復元にバックアップが使えなくなる |
| step 3（ディレクトリ rename） | エンコード形ディレクトリはプロジェクトのグループ化（並列読み込みの単位）に使われる。ここを揃えないとそもそも新パス配下に履歴が現れない |
| step 4 で `perl` を使う | BSD sed（`sed -i ''`）と GNU sed（`sed -i'<suffix>'`）で `-i` 構文が**非互換**。`perl -pi -e` は macOS / Linux どちらでも同一挙動。`\Q...\E` でパスを正規表現リテラルとして扱い、`.`（任意 1 文字）などのメタ文字を自動クオートして誤マッチを防ぐ（区切り文字に `\|` を使うため `/` のエスケープは不要） |
| step 4 でエンコード形も置換 | JSONL 内には絶対パスだけでなく `-Users-...` 形式の encoded path 文字列も含まれることがあるため |
| step 5 の grep 検証 | フルパス（`$OLD`）+ エンコード形（`$OLD_ENC`）で検証する。`basename "$OLD"` 単体だと会話本文中の旧ディレクトリ名（過去の grep コマンドやテキスト引用）に誤マッチして偽陽性が出るため。0 件にならない場合は `cwd` フィールドだけを Python / jq で抜き、実際の置換漏れか会話本文の引用かを切り分ける |

### `X ago` 表示の修復（mtime 復元）

step 4 の置換後、ピッカーで全セッションが「2 minutes ago」に揃う現象が起きる。`perl -pi` の atomic rename でファイル mtime が書き換え時刻に統一されるためである。各 JSONL の最終 `timestamp` フィールドから mtime を戻す。

```python
import os, json, glob, calendar
from datetime import datetime

DIR = os.path.expanduser('~/.claude/projects/-abs-path-to-new-name')  # ← この文字列を上の bash の $NEW_ENC の値（フルパス）に置き換える。例: ~/.claude/projects/-Users-yoshi-work-dev-my-projects-jarvis
for f in glob.glob(os.path.join(DIR, '*.jsonl')):
    last_ts = None
    with open(f, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            try:
                t = json.loads(line).get('timestamp')
                if t:
                    last_ts = t
            except Exception:
                pass
    if not last_ts:
        continue
    # Python 3.9+ 前提。Z サフィックスのみ除去して naive な UTC datetime を得る（rstrip は複数文字を誤除去しうる）
    dt = datetime.fromisoformat(last_ts.removesuffix('Z'))
    epoch = calendar.timegm(dt.timetuple()) + dt.microsecond / 1e6
    os.utime(f, (epoch, epoch))
```

これは mtime のみの操作で内容には触れないため、不可逆な書き換えではなく安心して実行できる。

### 推奨：修正は別プロジェクトのセッションから実行する

リネーム対象ディレクトリに常駐するセッションは、自身の JSONL を書き込み続けるため置換対象と競合する。**修正は別ディレクトリのセッションから実行する**のが最も安全（実証で競合なく完了）。

---

## 4. やってはいけないこと（アンチパターン）

| アンチパターン | 理由 | 対処 |
|---|---|---|
| `~/.claude/history.jsonl` を書き換える | (1) resume ピッカーは参照しない（Ctrl+R プロンプト履歴専用）。(2) **全プロジェクト共通の単一ファイル**で、他プロジェクトの稼働 claude が追記中の可能性が常にある。`perl -pi` の atomic rename と書き込み中 fd の競合で、他プロジェクトの履歴末尾が欠ける原理リスクがある | 置換対象に含めない。旧パスは Ctrl+R 検索に残るが resume には無関係。気になるなら全 claude 停止時に別タスクとして実施 |
| `sed -i ''` ワンライナーをそのままコピペ | BSD / GNU で `-i` 構文が非互換でハマる | `perl -pi -e` を使う |
| `pgrep -x claude` だけで安全装置を組む | プロセス名は全プロジェクト共通なので、無関係な claude を「稼働中」と誤検知して永遠に通らない | `lsof -p <PID>` で実 cwd を取って判定する（下記） |

```bash
# 安全装置: 対象プロジェクト配下で稼働中の claude だけを検出する
# step 0（リネーム前）に実行するため、稼働中セッションの cwd は $OLD。リネーム後に実行する場合に備え $NEW も併せて判定する
for pid in $(pgrep -x claude 2>/dev/null); do
  cwd=$(lsof -p "$pid" 2>/dev/null | awk '$4=="cwd"{print $NF}' | head -1)
  case "$cwd" in
    "$OLD"|"$OLD"/*|"$NEW"|"$NEW"/*) echo "ERROR: 対象プロジェクト配下に claude (PID=$pid, cwd=$cwd) が稼働中"; exit 1 ;;
  esac
done
```

---

## 5. トラブルシュート

| 症状 | 原因 | 対処 |
|---|---|---|
| リネーム後、`claude --resume` の一覧が空（ファイルは存在する） | JSONL 内の `cwd` が旧パスのまま | §3 step 4 の `perl -pi` で `cwd` を再置換。`cwd` だけ抜いて確認: `grep '"cwd"' <id>.jsonl \| head` |
| `--resume <id>` 直指定は通るのにピッカーに出ない | 同上（直指定は `cwd` フィルタを迂回するため成功する） | 同上 |
| 置換後にピッカー全件が同じ `X ago` になる | 一括書き換えで mtime が統一された | §3 の mtime 復元スクリプトを実行 |
| 修正スクリプトの安全装置が永遠に通らない | `pgrep -x claude` が他プロジェクトの claude を誤検知 | §4 の `lsof` ベース判定に置き換える |
| **Zed（ACP）で開いたセッションが `--resume` に出ない** | **主因は「アクティブセッション除外」**。Zed/ACP セッションも同じストアに通常の JSONL として保存され resume 適格。ACP であること自体は無関係 | 当該 Zed スレッドを終了してから `claude --resume`、または `claude --resume <id>` で直指定。詳細は下記 |

### Zed（ACP）セッションが `--resume` に出ない件の補足

Zed は `claude` CLI を直接起動せず、ACP アダプタ（`@zed-industries/claude-agent-acp`）経由で Claude Code を動かす。ただし**実機検証では、ACP セッションも CLI セッションと同一形式の JSONL を同じ project dir に書き込んでおり、resume 適格**だった（`version` / `userType` / トップレベルキー / `cwd` が CLI セッションと一致）。

したがって「ACP だから出ない」は誤りで、出ない主因は **そのセッションが現在アクティブ（書き込み中）でピッカーから除外されている**こと。Zed の複数タブを同時に開いている場合、それら全てが候補から外れる。

> なお Zed 公式が「resuming threads from history は not yet available」と記すのは [Zed の Agent Panel（スレッド履歴 UI）](https://zed.dev/docs/ai/external-agents)の話であり、**CLI の `claude --resume` とは別レイヤー**。CLI 側のストアには正常に残る。

---

## 6. 公式仕様 vs 実証知見の対応表

本 doc の主張のうち、どこまでが公式 docs 由来で、どこからが実機検証由来かを明示する。

| 主張 | 区分 | 根拠 |
|---|---|---|
| transcript は `~/.claude/projects/<encoded>/<id>.jsonl` に保存 | 公式 | [Manage sessions](https://code.claude.com/docs/en/sessions) |
| ピッカーは現在の作業ディレクトリで絞り込む | 公式 | [Manage sessions](https://code.claude.com/docs/en/sessions) |
| 絞り込みは JSONL 内の `cwd` フィールドで行う | 公式（DeepWiki 経由で明文化） | DeepWiki `anthropics/claude-code` |
| `history.jsonl` は resume に参照されない（Ctrl+R 専用） | 公式（DeepWiki 経由） | DeepWiki `anthropics/claude-code` |
| `cwd` 以外に絶対パスを持つフィールドは無い | 実証 | 2026-06-08 実機確認（60 本の JSONL 走査） |
| `X ago` 表示は mtime 起源 | 実証 | 一括書き換えで全件 "few minutes ago" に統一されたことから |
| ACP（Zed）セッションも CLI と同形式で resume 適格 | 実証 | 本セッションの JSONL を CLI セッションと構造比較（`version` 2.1.165 / `userType` external 等が一致） |
| BSD/GNU sed の `-i` 非互換で置換漏れが起きる | 実証 | 当初の `rename_jarvis_dir.sh` が GNU sed 環境で step 4 以降を実行できなかった |

---

## 7. Remote Control セッションの再開（v2.1.228〜v2.1.232）

ローカルの `--continue` / `--resume` とは別に、**Remote Control 経由のセッションにも再開手段がある**（2026-08-16 追記）。

| 操作・挙動 | 内容 | 版 |
|---|---|---|
| **`claude remote-control --continue`** | 直近の Remote Control セッションを再開する。公式 [Remote Control](https://code.claude.com/docs/en/remote-control) ページに明記された | v2.1.229 |
| **archive 済みセッションの復帰** | `--continue` / `--session-id` で archive 済みセッションを指定すると、**自動で unarchive して再開**する（従来は archive されていると再開できなかった） | v2.1.228 |
| **再接続の維持** | 接続が切れても**約 30 分は再接続を待つ**ようになった。一時的なネットワーク断でセッションを失わない | v2.1.232 |
| **切断理由の区別表示** | 「他デバイスに引き継がれた」「他アプリで終了された」「削除された」を区別して表示する（従来は一律の切断表示だった） | v2.1.232 |
| **cloud セッションの継承バグ修正** | bridge が cloud セッションの transcript と認証情報を誤って継承する不具合を修正 | v2.1.232 |

出典: [Remote Control](https://code.claude.com/docs/en/remote-control) / CHANGELOG v2.1.228 / v2.1.229 / v2.1.232

---

## background セッションのシェル操作（v2.1.251〜）

background セッションは `~/.claude/jobs/<short-id>` がディレクトリ名になる（transcript は §1 の `projects/` 側に置かれる）。シェルから直接操作できる。

| コマンド | 内容 |
|---|---|
| `claude attach <id>` | 実行中の background セッションに接続する |
| `claude logs <id>` | 出力を確認する |
| `claude stop <id>`（`claude kill` も可） | 停止する |
| `claude respawn <id>` | **元の prompt を再実行**する（`--all` で全 running を再起動） |
| `claude rm <id>` | 一覧から削除する。⚠️ **transcript はローカルに残り `claude --resume` で到達できる** |
| `claude daemon status` | daemon の状態を見る |
| `claude daemon stop --any [--keep-workers]` | daemon を止める |

⚠️ **`cleanupPeriodDays` で transcript が消えた stopped session は行を開けない**（`respawn` は元 prompt を再実行するため動く）。

### `claude project purge` — ローカル状態の一括削除

`claude project purge [path]` は、プロジェクトの **transcripts / task lists / debug logs / file-edit history / prompt history 行 / `~/.claude.json` のプロジェクトエントリ**を一括削除する。`--dry-run` / `-y` / `-i` / `--all` を取る。

**§3 の手動 runbook を使う前に、まずこの公式コマンドを検討する。** auto memory も削除対象に含まれる点に注意する（[memory.md](memory.md) 参照）。

出典: [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Manage sessions from the shell](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell) / [Claude directory — Clear local data](https://code.claude.com/docs/en/claude-directory#clear-local-data)

> ⚠️ **`claude --resume <id> --bg` の挙動変更（CHANGELOG v2.1.257 のみが一次情報）**: 「何も動かしていなければそのセッションを同一 ID のまま継続し、コピー起動になる場合は明示告知する」という変更が CHANGELOG に記載されているが、**`cli-reference` / `sessions` / `agent-view` のいずれにも該当記述がない**（2026-09-03 確認）。公式 docs 側の追従待ちとして扱う。

## Remote Control（v2.1.234〜 research preview を卒業）

`claude remote-control` を実行中の全マシンが、Claude アプリの Code タブ上部に **デバイスカード**として表示され、そこから directory を選んでセッションを開始できる。

- スマホ / `claude.ai/code` から **effort level を変更するとマシン上のセッションに適用**される
- Desktop / VS Code がホストする Remote Control セッションは、接続デバイスに**現在の permission mode** も表示する
- **VS Code 拡張がセッション一覧をグループ化**するようになった（Week 33）。右クリックで作成 / リネーム / 削除、Cmd/Ctrl・Shift クリックで複数移動

出典: [whats-new week 33](https://code.claude.com/docs/en/whats-new/2026-w33) / [whats-new week 34](https://code.claude.com/docs/en/whats-new/2026-w34)

## 関連ドキュメント

- [ClaudeCode の設定ファイル一覧と役割](config-files.md) — `~/.claude.json` 等の設定ファイル成果物（本 doc と対をなす）
- [ClaudeCode スラッシュコマンドガイド](slash-commands.md) — `/resume` `/rewind` `/rename` 等の UX レベルのセッション操作
- [メモリ（CLAUDE.md）ガイド](memory.md) — `~/.claude/projects/<encoded>/memory/` の Auto Memory ストア
- [Zed エディタ活用ガイド](zed.md) — ACP ホストとしての Zed・スレッド履歴

## 出典

- [Manage sessions — code.claude.com/docs/en/sessions](https://code.claude.com/docs/en/sessions)
- [CLI reference — code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)
- [External agents (ACP) — zed.dev/docs/ai/external-agents](https://zed.dev/docs/ai/external-agents)
- DeepWiki [anthropics/claude-code](https://deepwiki.com/anthropics/claude-code) — resume picker / `cwd` filtering / `history.jsonl` の役割
- 実機検証: 2026-06-08、`JARVIS-aka-AIdentity` → `jarvis` ディレクトリリネーム事例（インシデント記録は `docs/report/` 配下・gitignore）
