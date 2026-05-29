# report-template.md — 差分レポートの構成テンプレート

`docs/sync-reports/YYYY-MM-DD-docs-sync.md` に出力する。各項目に**通し番号**を振り、BOSS が番号で
承認・却下を指定できるようにする。

## テンプレート

```markdown
# ClaudeCode ドキュメント同期レポート

> 調査日: YYYY-MM-DD
> 前回調査: YYYY-MM-DD (初回の場合は「初回」)
> 正ソース: 英語版 (en)

## サマリ

- 新機能: N 件 (新規ファイル M 件 / 既存追記 K 件)
- 更新必要: P 件
- ドリフト是正: Q 件
- 合計: R 項目

---

## 新機能

### 1. [新規ファイル] Agent Teams
- 配置案: `docs/agent-teams.md`
- 要点: 複数セッションを共有タスクリストで自動連携させる実験的機能。subagent との違いは…
- 出典: https://code.claude.com/docs/en/agent-teams
- 連動更新: README.md (英/日 目次), CLAUDE.md (構造ツリー + 参照リスト)

### 2. [既存追記] /btw サイドバー質問
- 追記先: `docs/slash-commands.md` のバンドルスキル節
- 要点: コンテキストを汚さず単発質問できるコマンド。1 文で説明可のため追記が妥当。
- 出典: https://code.claude.com/docs/en/interactive-mode#...

---

## 更新必要 (既存ドキュメントの陳腐化)

### 3. best-practices.md — Opus 4.8 のベストプラクティス
- 該当箇所: 第 8 章「Opus 4.7 を活用する」
- 現状: Opus 4.7 までの記述
- 公式最新: Opus 4.8 が発表され、effort デフォルト/thinking 挙動が変化
- 対応案: 4.7 記述を残しつつ 4.8 を追記 (履歴併存)
- 出典: https://www.anthropic.com/news/claude-opus-4-8
- ★連動: CLAUDE.md の「編集してはいけないドキュメント」記述を「本スキル経由+承認時のみ編集可」に改訂
- 注意: best-practices.md は聖域指定のため、特に慎重な確認をお願いします

### 4. config-files.md — 設定項目の追加
- 該当箇所: 設定ファイル詳細
- 現状: … / 公式最新: … / 出典: …

---

## ドリフト是正 (公式変化とは別: ドキュメント整合性)

### 5. CLAUDE.md 目次のドリフト
- docs/memory.md と docs/skills-progressive-disclosure.md が実在するが CLAUDE.md の
  「ドキュメント構造」「ドキュメント参照」に未記載
- 対応案: CLAUDE.md の該当箇所に 2 ファイルを追記

---

## 承認のお願い

上記のうち、反映してよい項目を番号でお知らせください。
(例: 「全部」「1・2・5 のみ」「3 は却下、他はOK」など)
```

## 書き方の注意

- 各項目は **独立して採否判断できる** 粒度にする。
- best-practices.md 関連は「聖域」である旨を必ず明示し、慎重な確認を促す。
- 出典は必ず英語版の公式 URL を載せる。
- before/after は「要約」で良い (レポートを読みやすく保つ)。実際の全文差分はフェーズ2 で行う。
