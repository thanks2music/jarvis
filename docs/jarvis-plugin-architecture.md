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
| サブ職能（専門分化） | 未実装 | Phase 2 で実装予定（`references/sub-roles.md`） |
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
        │           └── claude-md-template.md  ← 組織ルート CLAUDE.md 雛形
        ├── LICENSE                            ← MIT（cc-company クレジット保持）
        └── README.md                          ← Plugin 内 README
```

ClaudeCode のローカル marketplace パターンを採用。`~/.claude/plugins/jarvis/.claude-plugin/marketplace.json` をエントリポイントとして `/plugin marketplace add` で登録できる構造。

## 主要ファイルの責務

### `SKILL.md`（trigger: `/jarvis`）

JARVIS スキルの本体。以下のフローを定義:

1. **検出とモード判定** — `.jarvis/` / `.company/` の有無を確認
2. **オンボーディング** — `AskUserQuestion` で 3 問（事業内容・目標・ダッシュボード）
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

Plugin マニフェスト。`name: jarvis`、`version: 0.1.0`。

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

## Phase ロードマップ

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 0 | 準備（cc-company の解析、ライセンス確認） | 完了 |
| Phase 1 | ベース移植（`/jarvis` コマンド、`.jarvis/`、JARVIS 人格） | 完了（v0.1.0） |
| Phase 2 | 全部署横断のサブ職能（専門分化）対応 | 未着手 |
| Phase 3 | JARVIS リポジトリへのドキュメント統合 | 完了 |
| Phase 4 | ダッシュボード（任意） | 未着手 |

## Phase 2 の設計方針（参考）

Phase 2 で追加予定の `references/sub-roles.md` は、各部署のサブ職能テンプレート集を 1 ファイルに集約する。

- 部署作成時のデフォルトは **サブ職能なし**（cc-company オリジナルと同じフラット構造）
- BOSS が必要を感じた時点で 1 つだけサブ職能を追加
- 2 回目以降のタスクで JARVIS が次のサブ職能を提案
- 開発部署専用の機能ではなく、すべての部署に共通する横断的な仕組み

## 関連ドキュメント

- @docs/jarvis-plugin-guide.md — JARVIS Plugin の利用ガイド
- @docs/skills-guide.md — ClaudeCode Skills の全容
- @docs/plugins-guide.md — ClaudeCode Plugins の全容
- [Shin-sibainu/cc-company](https://github.com/Shin-sibainu/cc-company) — 原作
