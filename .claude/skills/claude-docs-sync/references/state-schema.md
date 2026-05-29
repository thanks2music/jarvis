# state-schema.md — docs/.docs-sync-state.json のスキーマ

前回の調査時点を記録し、差分検出の基準とする状態ファイル。本リポで git 管理する
(マシン間・clean clone でも「どこまで把握済みか」を共有するため)。

## スキーマ

```json
{
  "schema_version": 1,
  "last_scan": "2026-05-29",
  "claude_code_version_seen": "2.1.x",
  "known_models": ["Opus 4.5", "Opus 4.6", "Opus 4.7"],
  "known_features": [
    "Agent teams",
    "/btw side questions",
    "auto mode",
    "Ultraplan"
  ],
  "known_whats_new_entries": [
    "2026-04-xx: <whats-new に出ていたエントリ見出し>"
  ],
  "doc_sources": {
    "docs/skills.md": [
      "https://code.claude.com/docs/en/skills",
      "https://code.claude.com/docs/en/features-overview"
    ],
    "docs/best-practices.md": [
      "https://code.claude.com/docs/en/best-practices",
      "https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code"
    ]
  }
}
```

## 各フィールドの意味

| フィールド | 役割 |
|---|---|
| `schema_version` | スキーマ変更時の互換性管理 (現状 1) |
| `last_scan` | 前回スキャン日 (YYYY-MM-DD) |
| `claude_code_version_seen` | 前回把握した ClaudeCode バージョン |
| `known_models` | 把握済み Claude モデル世代。新モデル検出の基準 |
| `known_features` | 把握済み機能名。SubAgent 1 の「新規」判定に使う |
| `known_whats_new_entries` | whats-new で既読のエントリ見出し。重複検出回避 |
| `doc_sources` | `doc パス → 依拠する公式 URL[]`。SubAgent 2 の照合対象 |

## 運用ルール

- `doc_sources` は各 doc 冒頭の `> 出典:` 行から自動抽出して同期する。doc が増減したら追従する。
- フェーズ2 完了時に `last_scan`・`known_*` を更新する。
- 差分ゼロの回でも `last_scan` は更新する (「いつ確認したか」を残すため)。
- 初回 (ファイル不在) は全項目を新規構築する。
