# ClaudeCode セッション履歴と `--resume`（ディレクトリリネーム手順含む）

> 出典: [Manage sessions](https://code.claude.com/docs/en/sessions) / [CLI reference](https://code.claude.com/docs/en/cli-reference) / [Built-in commands](https://code.claude.com/docs/en/commands) / [External agents (ACP)](https://zed.dev/docs/ai/external-agents) / [anthropics/claude-code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) / DeepWiki [anthropics/claude-code](https://deepwiki.com/anthropics/claude-code) (2026-07-26 確認)

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

- `<encoded-cwd>`: 作業ディレクトリの絶対パスの `/` を `-` に置換した文字列。
  例: `/Users/yoshi/work/dev/my-projects/jarvis` → `-Users-yoshi-work-dev-my-projects-jarvis`
- `<session-id>`: セッションごとの UUID。`claude --resume <session-id>` で直接指定できる。
- サブディレクトリ:
  - `<session-id>/subagents/agent-*.jsonl` … サブエージェントの transcript
  - `<session-id>/tool-results/*.txt` … 大きなツール出力の退避先

> 公式 docs（[Manage sessions](https://code.claude.com/docs/en/sessions)）でも、transcript が `~/.claude/projects/<project>/<session-id>.jsonl` に保存され、`<project>` が作業ディレクトリパスから導出されると明記されている。

> **`/cd` による移動（v2.1.169〜）**: セッション中に `/cd <path>` で作業ディレクトリを変えると、**セッションストレージが新 dir の project ストア配下へ移動**し、`--resume` / `--continue` は新 dir から会話を見つける（=`<encoded-cwd>` グループが変わる）。この挙動は §3 のディレクトリリネーム手順とは別の正規ルートである。なお `/add-dir` はアクセス追加のみでストアは移動しない。出典: [Commands](https://code.claude.com/docs/en/commands)。
>
> **v2.1.196 での挙動改善**:
> - 移動したセッションは **crash / 強制終了後も旧 dir の picker に出ない**(以前は復帰時に旧位置に再登場する場合があった)
> - `claude --resume <name>` / `/resume <name>` が **worktree 横断で fuzzy resolution**(名前が曖昧なら picker を開く)
> - 名前なしセッションに **default 表示名 auto-generation**(例 `my-app-3f`、agent-view / `claude agents --json` に表示。resume の handle にはならない)
> - **`--from-pr <number>`** サポート: GitHub PR 番号を渡してセッションを開始できる (PR 差分と PR 本文がコンテキストに入る)
> - **`claude --resume <session-id>` が SDK / headless セッションでも動作**(以前は対話セッション限定。現在は project dir スコープで再開可能)
>
> **v2.1.198 以降の追加**:
> - **post-compaction session naming が最初の prompt を参照**するようになった。auto-compaction 後もセッション名が意味的に維持される
> - **`--no-session-persistence`** CLI フラグ (**単発 non-interactive run で transcript write を抑止**する。scratch な `-p` 実行で `~/.claude/projects/` が汚れなくなる)
> - **`Ctrl+B`** session picker で **current git branch フィルタ** (worktree 別に piv したセッションを見つけやすくなった)

> **Background sessions のプロセス跨ぎ永続化(v2.1.197〜)**: `claude` プロセスの停止・再起動・アップデートを跨いで、長時間コマンド・ワークフローが survive するようになった。Windows でも background shell を kill せず handoff する。長時間タスク進行中の `claude` アップデート適用が安全になった。出典: CHANGELOG v2.1.197。

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
| **`cwd` 突合** | 公式 | ピッカーは「JSONL の `cwd` が現在の作業ディレクトリと一致するセッション」を絞り込む（`/add-dir` で追加した worktree も含む）。出典: [Manage sessions](https://code.claude.com/docs/en/sessions) / DeepWiki |
| **アクティブセッション除外** | 公式/実証 | 現在稼働中（書き込み中）のセッションはピッカーから除外される。複数の Zed タブ等を同時に開いていると、それら全てが候補から外れる |
| **`X ago` の表示順** | 実証 | 表示の新しさ順は**ファイルの mtime 起源**。一括書き換えで mtime が揃うと全件が同じ `X ago` になる（2026-06-08 実機確認） |
| **`--resume <id>` 直指定** | 実証 | セッション ID を直接渡す場合は `cwd` フィルタを**迂回**する。`cwd` が旧パスのままでも特定セッションへの復元自体は可能 |
| **`/loop` 起点セッションの除外** | 公式 | **最初のプロンプトが `/loop` だったセッションはピッカーに出ない**（v2.1.211〜）。会話の途中で `/loop` を使った場合は隠れない。**v2.1.211 より前は、会話初期に `/loop` を使うとそのセッションが恒久的にピッカーから隠れていた**。出典: [Manage sessions](https://code.claude.com/docs/en/sessions) |
| **agent view 内の `/resume`** | 公式 | v2.1.212 以降、agent view 内で `/resume` を実行すると**削除済みを含む過去セッションのピッカー**が開き、選んだ会話は **background セッションとして再開**される（フォアグラウンドの復元とは別経路）。出典: CHANGELOG v2.1.212 |

### セッションを増やす 3 経路の違い（`/branch` / `/fork` / `/subtask`）

`docs/slash-commands.md` の UX レベルの説明と対応させると、**ディスク上のセッション同一性**は次のように分かれる。**v2.1.212 で `/fork` の意味が変わった**ため、旧来の理解のままだと JSONL の対応付けを誤る。

| コマンド | 新しいセッションができるか | ピッカーでの見え方 |
|---|---|---|
| `/branch [name]` | **できる**（独自の session ID を持つ） | **別行として出る**。自分がその複製へ移る |
| **`/fork [prompt]`**（v2.1.212〜） | **できる**（独立した background セッション） | agent view に独自の行を持つ。元の会話には自分が留まる |
| **`/subtask <instruction>`**（v2.1.212〜） | できない（会話内 subagent） | セッションとしては現れない。結果が元の会話に戻る |

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
OLD_ENC="$(echo "$OLD" | tr '/' '-')"   # 例: -abs-path-to-old-name
NEW_ENC="$(echo "$NEW" | tr '/' '-')"

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
