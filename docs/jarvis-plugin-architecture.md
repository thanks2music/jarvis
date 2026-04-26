# JARVIS Plugin アーキテクチャ

> 最終更新: 2026-04-26

JARVIS Plugin の内部設計、cc-company 由来の経緯、ライセンス、改変点を整理する。利用方法の概要は @docs/jarvis-plugin-guide.md を参照。

## 出典・派生関係

JARVIS Plugin は [Shin-sibainu/cc-company](https://github.com/Shin-sibainu/cc-company)（v2.1.0、MIT License）の派生物である。

| 項目 | cc-company（原作） | JARVIS Plugin |
|---|---|---|
| 形式 | Plugin + Skill | 同左（cc-company と同じ marketplace + plugin 構造） |
| 起動コマンド | `/company` | `/jarvis` |
| 状態フォルダ | `.company/` | `.jarvis/` |
| 配布 | `Shin-sibainu/cc-company` リモート marketplace | BOSS のローカル marketplace（`~/.claude/plugins/jarvis/`） |
| 窓口の人格 | 親しみやすい秘書（「〜ですね！」） | JARVIS（丁寧語 + 謙譲語、一人称「私」、BOSS-COO 階層） |
| 部署テンプレート | 9 部署 + 汎用 | 同左（口調を JARVIS 仕様に変更） |
| サブ職能（専門分化） | 未実装 | 実装済み（v0.2.0、`references/sub-roles.md`） |
| マイグレーション | v1（CEO 部門あり） → v2 | + cc-company `.company/` → JARVIS `.jarvis/` |

## ライセンス

MIT License。原作者 Shin-sibainu のクレジットを `LICENSE` ファイル内に保持している。

```
~/.claude/plugins/jarvis/plugins/jarvis/LICENSE
```

## ディレクトリ構造

```
~/.claude/plugins/jarvis/                     ← マーケットプレースルート
├── .claude-plugin/
│   └── marketplace.json                       ← マーケットプレースカタログ
└── plugins/
    └── jarvis/                                ← Plugin
        ├── .claude-plugin/
        │   └── plugin.json                    ← Plugin マニフェスト
        ├── skills/
        │   └── jarvis/
        │       ├── SKILL.md                   ← 本体ロジック（trigger: /jarvis）
        │       └── references/
        │           ├── departments.md         ← 部署別テンプレート集
        │           ├── sub-roles.md           ← サブ職能テンプレート集（Phase 2、v0.2.0）
        │           └── claude-md-template.md  ← 組織ルート CLAUDE.md 雛形
        ├── LICENSE                            ← MIT（cc-company クレジット保持）
        └── README.md                          ← Plugin 内 README
```

ClaudeCode のローカル marketplace パターンを採用。`~/.claude/plugins/jarvis/.claude-plugin/marketplace.json` をエントリポイントとして `/plugin marketplace add` で登録できる構造。

## 主要ファイルの責務

### `SKILL.md`（trigger: `/jarvis`）

JARVIS スキルの本体。以下のフローを定義:

1. **検出とモード判定** — `.jarvis/` / `.company/` の有無を確認
2. **オンボーディング** — `AskUserQuestion` で 2 問（事業内容・目標）+ 完了時にダッシュボード通知
3. **組織を自動構築** — `.jarvis/CLAUDE.md` と `.jarvis/secretary/` を生成
4. **マイグレーション処理** — cc-company v1/v2 → JARVIS への移行
5. **運営モード** — JARVIS が窓口として機能、必要に応じて部署に振り分け
6. **部署の自然な追加** — 同領域 2 回検出で部署作成を提案
7. **MCP 連携の提案** — Notion / Google Calendar / GitHub / Slack 等
8. **運用ルール** — 自動記録、同日 1 ファイル、日付チェック等

### `references/departments.md`

9 部署 + 汎用テンプレートの定義。各部署について以下を含む:

- 部署トップ（`_template.md`）
- サブフォルダのテンプレート（`docs/_template.md` 等）
- 部署別 `CLAUDE.md`（部署固有のルールと振る舞い）

cc-company の同名ファイルから派生し、口調を JARVIS 仕様に変更している。

### `references/claude-md-template.md`

組織ルート（`.jarvis/CLAUDE.md`）の雛形。`{{BUSINESS_TYPE}}`、`{{GOALS_AND_CHALLENGES}}` 等の変数をオンボーディング回答で置換する。

cc-company のテンプレートに「BOSS / JARVIS（COO 兼秘書）/ 各部署」の階層説明を追加し、Git 管理に関する注意事項（`.jarvis/` を `.gitignore` 推奨）を含めている。

### `marketplace.json`

ローカル marketplace のカタログ。`/plugin marketplace add ~/.claude/plugins/jarvis` で登録される。

### `plugin.json`

Plugin マニフェスト。`name: jarvis`、最新バージョンは「バージョン履歴」セクションを参照。

## JARVIS 人格の実装

CLAUDE.md の現行階層（BOSS / COO（JARVIS） / SubAgents）は維持しつつ、cc-company の「秘書」役割を JARVIS が引き継ぐ:

> **JARVIS = BOSS の窓口（秘書機能）兼執行責任者（COO 機能）**

口調ルールは `SKILL.md` 冒頭の「JARVIS の人格・口調」セクションと `secretary/CLAUDE.md`（自動生成）の「口調・キャラクター」セクションの両方に明示している。スキル起動中は通常の Claude Code 人格より JARVIS 人格が優先される。

## マイグレーション設計

### cc-company v1 → JARVIS（`.company/ceo/` 検出時）

1. `.company/CLAUDE.md` から既存オーナー情報を抽出
2. `.company/` を `.jarvis/` に rename
3. `.jarvis/ceo/` と `.jarvis/reviews/` を削除
4. 空部署を削除
5. `.jarvis/CLAUDE.md` を JARVIS 版テンプレートで再生成
6. `.jarvis/secretary/CLAUDE.md` を JARVIS 版に更新

### cc-company v2 → JARVIS（`.company/` のみ検出時）

1. `.company/` を `.jarvis/` に rename
2. `.jarvis/CLAUDE.md` を JARVIS 版テンプレートで再生成
3. `.jarvis/secretary/CLAUDE.md` を JARVIS 版に更新
4. その他の部署 CLAUDE.md は変更なし

### 拒否時

何も変更せず `.company/` のまま運営モードに入る。ただし JARVIS の口調・人格は維持する。

## バージョン履歴

| バージョン | リリース日 | 変更点 |
|---|---|---|
| 0.1.0 | 2026-04-26 | Phase 1（ベース移植）完了。cc-company v2.1.0 から派生 |
| 0.2.0 | 2026-04-26 | Phase 2（全部署横断のサブ職能対応）+ Phase 3.5（第 1 回稼働振り返り反映）完了 |

## Phase ロードマップ

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 0 | 準備（cc-company の解析、ライセンス確認） | 完了 |
| Phase 1 | ベース移植（`/jarvis` コマンド、`.jarvis/`、JARVIS 人格） | 完了（v0.1.0） |
| Phase 2 | 全部署横断のサブ職能（専門分化）対応 | 完了（v0.2.0） |
| Phase 3 | JARVIS リポジトリへのドキュメント統合 | 完了 |
| Phase 3.5 | 第 1 回稼働の振り返り反映（TODO 形式・曜日日本語化・運営モード挨拶 等） | 完了（v0.2.0） |
| Phase 4 | ダッシュボード（B 案: テキスト → 必要に応じて A/C） | 未着手（Phase 5 着手前に試行） |
| Phase 5 | メモリーシステムとの統合整理 | 採用、Phase 4 完了後に詳細化 |
| Phase 6 | SubAgents 連携（部署作成時に SubAgent 自動生成） | 採用、Phase 4 完了後に詳細化 |
| Phase 7 | ナレッジリンク自動メンテナンス（部署横断の相互参照） | 採用、Phase 4 完了後に詳細化 |

> Phase 5 / 6 / 7 の優先順位は Phase 2〜4 の運用結果を踏まえて別途決定する。

## Phase 2 の設計（v0.2.0 実装済み）

`references/sub-roles.md` が各部署のサブ職能テンプレート集を 1 ファイルに集約。

### 設計原則

- 部署作成時のデフォルトは **サブ職能なし**（cc-company オリジナルと同じフラット構造）
- BOSS が必要を感じた時点で 1 つだけサブ職能を追加
- 運用中の自動提案: 部署内のタスクが特定領域に偏った場合、JARVIS が「直近のタスク 3 件」を根拠に提案
- 開発部署専用の機能ではなく、すべての部署に共通する横断的な仕組み

### 検出方式: D ハイブリッド

部署フォルダの内容と会話履歴を JARVIS が総合判断する。明示的なカウンタファイル（`.jarvis/[department]/_counters.json` 等）は持たず、設計を軽量に保つ。

### 標準サブ職能カタログ

カタログは `references/sub-roles.md` を Single Source of Truth とする。本ファイルでは設計意図のみ記載し、サブ職能の追加・改名は `references/sub-roles.md` のみで管理する。

カタログ外のサブ職能は同ファイルの共通フォールバックテンプレートで生成可能。

## Phase 3.5 の改善（v0.2.0 実装済み）

第 1 回稼働の振り返りに基づく改善。

| ID | 内容 | 状態 |
|---|---|---|
| B-1 | SKILL.md に「`.jarvis/CLAUDE.md` は JARVIS スキル経由でのみ読み込まれる」を明記 | 完了 |
| B-2 | TODO テンプレートの曜日表記を日本語短縮形（日／月／火／水／木／金／土）に変更 | 完了 |
| B-3 | TODO 形式に「プロジェクト: name」フィールドを正式追加（複数プロジェクト管理対応） | 完了 |
| B-4 | Q3 ダッシュボードを「質問」から「通知」に変更 | 完了 |
| B-5 | 「秘書」呼びかけの柔軟性は維持（変更なし） | 維持 |
| B-6 | Migration ロジックの動作確認 | Phase 2 検証時に実施 |
| B-7 | 運営モード入室時の挨拶を SKILL.md に追加 | 完了 |

## 関連ドキュメント

- @docs/jarvis-plugin-guide.md — JARVIS Plugin の利用ガイド
- @docs/skills-guide.md — ClaudeCode Skills の全容
- @docs/plugins-guide.md — ClaudeCode Plugins の全容
- [Shin-sibainu/cc-company](https://github.com/Shin-sibainu/cc-company) — 原作
