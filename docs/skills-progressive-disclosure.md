# Skills の Progressive Disclosure（段階的開示）パターン

> 出典: [anthropics/claude-code plugin-dev スキル](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md) / [Extend Claude with skills](https://code.claude.com/docs/en/skills) (2026-04-09時点)

Progressive Disclosure（段階的開示）は、Anthropic が公式に推奨するスキル設計パターンである。SKILL.md を**手順の核心だけに絞り**、詳細なリファレンス・テンプレート・出力例を別ファイルに分離することで、コンテキスト効率と保守性を両立する。

本ドキュメントは [Skills ガイド](skills-guide.md) の補足であり、SKILL.md が肥大化しやすいタスク型・ビジュアル出力型スキルの設計に特化した実践ガイドである。

---

## なぜ Progressive Disclosure が必要か

### 問題: SKILL.md の肥大化

スキルにテンプレート・詳細仕様・出力例をすべて含めると、以下の問題が発生する:

1. **コンテキストウィンドウの圧迫**: スキル本文は呼び出し時にコンテキストにロードされる。巨大な SKILL.md は呼び出しただけでコンテキストを大量消費する
2. **保守性の低下**: 1 ファイルに手順・テンプレート・例が混在すると、変更時の影響範囲が読みにくい
3. **再利用性の低下**: テンプレートだけ差し替えたい場合でも、SKILL.md 全体を編集する必要がある

### 解決: 段階的開示

Claude は SKILL.md をまず読み、必要に応じて `references/` や `examples/` のファイルを相対パスで読み込む。つまり、**常にすべてを読むわけではない**。この仕組みを活かし、情報を必要な粒度で段階的に提供する。

```
呼び出し時 → SKILL.md（手順の核心）をロード
  └→ 必要に応じて references/template.md を Read
  └→ 必要に応じて examples/sample.md を Read
```

---

## SKILL.md の推奨サイズ

### 公式の推奨値

| 指標 | 推奨値 | 出典 |
|------|--------|------|
| **英語テキスト** | 1,500〜2,000 words | anthropics/claude-code plugin-dev スキル |
| **行数上限** | 500 行以下 | [Extend Claude with skills](https://code.claude.com/docs/en/skills) |

参考実装として、Anthropic の command-development スキルは約 2,470 words であり、推奨範囲をやや超えている。

### 日本語での目安

英語の 1,500〜2,000 words は日本語に換算すると概ね **150〜250 行**程度に相当する（日本語はスペース区切りでないため、行数で管理する方が実用的である）。Progressive Disclosure パターンを適用する場合は **200 行以下** を目安とする。

| パターン | SKILL.md の目安 |
|---------|----------------|
| 単一ファイル（小規模スキル） | 500 行以下 |
| Progressive Disclosure 適用 | **200 行以下** |

---

## ディレクトリ構造

### 基本構造

```
skill-name/
├── SKILL.md              ← 手続き・ワークフローの核心のみ（200 行以下）
├── references/
│   ├── template.md       ← 出力テンプレート
│   ├── patterns.md       ← 詳細パターン・ガイド
│   └── advanced.md       ← 応用テクニック・補足情報
├── examples/
│   └── sample.md         ← 期待する出力例
└── scripts/
    └── validate.sh       ← Claude が実行するスクリプト
```

`references/` と `examples/` 内のファイル数に制限はない。スキルの複雑さに応じて必要な分だけ作成する。

### 各ディレクトリの役割

| ディレクトリ | 役割 | SKILL.md からの参照方法 |
|------------|------|----------------------|
| `references/` | 詳細リファレンス・テンプレート・仕様書 | `[references/template.md](references/template.md) を参照` |
| `examples/` | 期待する出力例・サンプル | `[examples/sample.md](examples/sample.md) を参考に` |
| `scripts/` | Claude が実行するスクリプト | `` python ${CLAUDE_SKILL_DIR}/scripts/run.py `` |

---

## 分離の 4 原則

Anthropic の公式ドキュメントから抽出した原則:

### 原則 1: SKILL.md には手続きの核心だけを置く

SKILL.md に書くべきもの:
- frontmatter（name, description, 各種設定）
- 絶対ルール（Absolute Rules）
- ステップバイステップの手順
- エラーハンドリング方針

SKILL.md に書かないもの:
- 出力テンプレートの全文
- 詳細な API リファレンス
- コード例集
- マイグレーションガイド

### 原則 2: 詳細なリファレンスは references/ に分離する

`references/` に移すべきコンテンツ:

| コンテンツ種別 | 例 |
|--------------|-----|
| 出力テンプレート | レポート・PR 本文・ドキュメントの雛形 |
| 詳細パターン集 | コーディングパターン、アーキテクチャパターン |
| 応用テクニック | 高度な設定、エッジケースの対処法 |
| API リファレンス | エンドポイント一覧、スキーマ定義 |
| マイグレーションガイド | バージョン移行の詳細手順 |

### 原則 3: 情報を重複させない

SKILL.md と references/ の間で同じ情報を書かない。**1 箇所にだけ置く**。

```
# 悪い例: SKILL.md にテンプレートの要約、references/ に全文 → 同期ずれが発生する

# 良い例: SKILL.md は参照だけ、references/ に全文
```

迷った場合は references/ に置く。SKILL.md には「〜は references/xxx.md を参照」の一文だけを書く。

### 原則 4: 出力例を examples/ に置く

Claude はテンプレートだけでは出力の質にばらつきが出やすい。**具体的な出力例**を 1 件以上用意すると、テンプレートの意図を正確に理解し、出力品質が安定する。

出力例に含めるべきもの:
- テンプレートの全セクションを埋めた具体的なサンプル
- 条件付きセクション（省略可能なセクション）の省略例・記載例
- ダミーデータで構わないが、リアルな構造であること

---

## SKILL.md での参照パターン

### 相対パスリンク

最もシンプルな方法。Claude が必要に応じて Read ツールで読み込む。

```markdown
レポートの構造は [references/report-template.md](references/report-template.md) のテンプレートに従って記述する。
出力例は [examples/sample-report.md](examples/sample-report.md) を参考にする。
```

### `${CLAUDE_SKILL_DIR}` を使ったスクリプト参照

スクリプト実行時はこの変数を使うことで、スキルの配置場所に依存しないポータブルな参照が可能になる。

```markdown
以下のスクリプトでバリデーションを実行する:
\`\`\`bash
python ${CLAUDE_SKILL_DIR}/scripts/validate.py $ARGUMENTS
\`\`\`
```

### 指示文の書き方

Claude に「このファイルを読め」と明示的に伝える表現が効果的である。

```markdown
# 良い例（明示的な指示）
references/report-template.md を読み込み、そのテンプレートに従ってレポートを生成する。

# 悪い例（曖昧な参照）
詳細はリファレンスを参照。
```

---

## 適用判断フローチャート

すべてのスキルに Progressive Disclosure を適用する必要はない。

```
SKILL.md の行数が 200 行を超えそうか？
├─ No → 単一ファイルで十分
└─ Yes → 以下を確認
    ├─ テンプレート・出力形式の定義が含まれるか？
    │   └─ Yes → references/template.md に分離
    ├─ 詳細なリファレンス・仕様書が含まれるか？
    │   └─ Yes → references/ に分離
    ├─ 出力品質を安定させたいか？
    │   └─ Yes → examples/ に出力例を追加
    └─ 上記すべて No → SKILL.md を簡潔に書き直せないか検討
```

### Progressive Disclosure が有効なスキルの種別

| スキル種別 | Progressive Disclosure | 理由 |
|-----------|:---:|------|
| リファレンス型（小規模） | 不要 | SKILL.md 自体が短い |
| リファレンス型（大規模） | **有効** | API 仕様・パターン集を references/ に分離 |
| タスク型（出力テンプレートあり） | **有効** | テンプレートを references/ に分離 |
| タスク型（シンプル） | 不要 | 手順だけなら SKILL.md で完結 |
| ガードレール型 | 不要 | 判定ルールは SKILL.md に直接書く方が明確 |
| ビジュアル出力型 | **有効** | スクリプト・テンプレートを scripts/ と references/ に分離 |

---

## 実践例: report-session スキル

本リポジトリの `report-session` スキルを例に、単一ファイルから Progressive Disclosure への変換を示す。

### Before（単一ファイル）

```
report-session/
└── SKILL.md    ← 284 行（手順 + テンプレート + エラーハンドリングが混在）
```

テンプレート部分（約 130 行）が SKILL.md の半分近くを占め、手順の見通しが悪い。

### After（Progressive Disclosure 適用）

```
report-session/
├── SKILL.md                  ← 約 150 行（手順の核心のみ）
│   ├── frontmatter
│   ├── Absolute Rules
│   ├── 引数の解釈
│   ├── Phase 1: 情報収集（git コマンド手順）
│   ├── Phase 2: 差分分析
│   ├── Phase 3: レポート生成（ファイル命名 + template への参照）
│   └── エラーハンドリング
├── references/
│   └── report-template.md    ← 出力テンプレート全文（セクション 0〜9）
└── examples/
    └── sample-report.md      ← ダミーデータによるレポート出力例
```

SKILL.md 内のテンプレート参照箇所:

```markdown
## Phase 3: レポート生成

[references/report-template.md](references/report-template.md) のテンプレートに従ってレポートを生成する。
出力例は [examples/sample-report.md](examples/sample-report.md) を参考にする。
```

---

## 注意事項

### context: fork との関係

`context: fork`（サブエージェント実行）を使用するスキルでは、サブエージェントが `references/` のファイルを Read ツールで読み込む。`allowed-tools` に `Read` を含めておく必要がある。

```yaml
---
context: fork
allowed-tools: Read, Bash, Write, Glob, Grep
---
```

### コンテキストコストの考慮

Progressive Disclosure はコンテキストの**初期ロード**を軽くする。ただし、Claude が references/ を読み込んだ時点でそのコンテキストは消費される。分離の主な利点は:

- **不要な情報を読まずに済む場合がある**（例: `--brief` モードではテンプレートの一部セクションだけ参照）
- **SKILL.md の見通しが良くなる**ことで Claude の手順理解が正確になる
- **ファイル単位での保守**が可能になる

### references/ のファイルサイズ

references/ 内の個々のファイルにも上限の意識は必要である。1 ファイルあたり **500 行以下** を目安にする。それを超える場合はさらにファイルを分割する。

---

## 関連ドキュメント

- [ClaudeCode Skills ガイド](skills-guide.md) — Skills の基本・frontmatter・設計パターン
- [ClaudeCode Plugins ガイド](plugins-guide.md) — Skills のパッケージング・配布
- [ClaudeCode SubAgents ガイド](sub-agents-guide.md) — context: fork との連携
- [ClaudeCode のベストプラクティス](best-practices.md) — 公式ベストプラクティス
- [Extend Claude with skills](https://code.claude.com/docs/en/skills) — 公式 Skills ドキュメント
- [anthropics/claude-code plugin-dev スキル](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md) — Progressive Disclosure の公式実装例
