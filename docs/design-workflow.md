# デザインワークフロー — ツールの使い分け

> 最終更新: 2026-09-03
>
> 出典（一次情報）: [Claude Design (Anthropic Labs)](https://www.anthropic.com/news/claude-design-anthropic-labs)（2026-04-17 公開。Claude Code への実装ハンドオフに言及）/ [whats-new week 34](https://code.claude.com/docs/en/whats-new/2026-w34)（**組み込みスキル `/design` の追加。要 v2.1.234+**）

デザイン作業で使うツールが増えたため、「どれをいつ使うか」の判断基準をまとめる。
「何を持っているか」の棚卸しは [使用ツールスタック](tool-stack.md) を SSOT とし、本ドキュメントは
**選択の指針**に絞る。

## 大原則

**Anthropic 一次提供 → 各サービスの公式提供 → サードパーティ、の順で検討する。**

デザイン系は「AI でデザインが良くなる」を謳うサードパーティ製 MCP / Skill が乱立しており、
安易に増やすと以下のコストを負う。

- **データ境界の増加**: リポジトリ構造・依存構成・絶対パスが新しいベンダーへ渡る
- **業務委託案件での説明責任**: 新規サブプロセッサの追加は委託元への確認が必要になる
- **課金の重複**: 既存プランで賄える機能に別途サブスクリプションを払う

採否基準は本ドキュメント末尾の「[外部デザインツールの採否基準](#外部デザインツールの採否基準)」を参照。

---

## 用途別の使い分け

| やりたいこと | 使うもの | 提供元 |
|---|---|---|
| **0→1 のデザイン生成・案出し** | `claude_design` MCP | Anthropic |
| **手で微調整したいビジュアル（モックアップ・LP・ポスター等）** | `design` skill（Claude Design canvas） | Anthropic（組み込み） |
| **既存 Figma からの実装 / コードとの双方向連携** | `figma` MCP | Figma 公式 |
| **コードを直接書く時の品質担保** | `frontend-design` skill | Anthropic 公式 plugin |
| **スタイル・配色・フォント選定** | `ui-ux-pro-max` skill | サードパーティ（導入済） |
| **Artifact として公開するページの設計** | `artifact-design` skill | Anthropic（組み込み） |
| **図・ダイアグラム** | `artifact-diagramming` skill / `diagram-maker` | Anthropic（組み込み）/ 自作 |
| **グラフ・ダッシュボード・チャート** | `dataviz` skill | Anthropic（組み込み） |
| **実装後の目視確認・表示崩れチェック** | `browse-playwright` → `browse-chrome` | 自作スキル |

### 補足

- **`claude_design` と `design` skill の関係**: どちらも Claude Design 基盤。
  MCP はプロジェクト管理・ファイル書き込み・プレビュー描画・共有/コメントまで扱う。
  `design` skill は Claude Code 内で canvas エディタ付き Artifact を作る早期プレビュー版で、
  **BOSS が視覚的に手で直したい**場合に向く。
- **`browse-playwright` を先に試す**: ブラウザ確認のフォールバックチェーンは
  `~/.claude/work-style.md` の「ブラウザ確認の自走原則」に従う。

---

## Claude Design のデザインシステム登録

Claude Design は **デザインシステムを登録すると、以降の生成がそのトークン**
（配色・タイポグラフィ・コンポーネント規約）**に従う**設計になっている。

未登録のままだと生成のたびにテイストが変わるため、**継続案件では最初に登録する**。

```
list_design_systems  → 登録済みデザインシステムの確認（is_default=true が既定）
get_claude_design_prompt --design_system_id <uuid>
                     → write_files の前に必ず呼ぶ
```

> **2026-08-19 時点の状態**: 登録済みデザインシステムは **0 件**。
> 継続的にデザインを生成する案件では、着手時に登録しておく。

---

## 外部デザインツールの採否基準

新しいデザイン系 MCP / Skill の導入を検討する際は、以下を**導入前に**確認する。

| # | 確認項目 | 却下ライン |
|---|---|---|
| 1 | ソースコードは公開されているか | `package.json` の repository が 404 / 非公開 |
| 2 | ライセンス | `UNLICENSED` 等、監査・改変が不可 |
| 3 | メンテナ体制 | 個人 1 名かつ法人実体が確認できない |
| 4 | 更新頻度 | pre-1.0 かつ数ヶ月更新なし |
| 5 | 送信データ | コード本体・絶対パス・リポジトリ構造がどこへ行くか |
| 6 | **既存スタックとの重複** | Anthropic / 各公式提供で同じ成果が得られる |
| 7 | 設定ファイルの汚染 | `~/.claude/` に symlink 管理外の実ファイルを書き込む |

**6 が最重要**。機能が既存と重複するなら、他が問題なくても導入しない。

### 評価記録: AIDesigner MCP（2026-08-19・不採用）

`npx -y @aidesigner/agent-skills init` で導入する、デザイン生成 MCP + Skill のバンドル。
「リポジトリを自動解析して既存デザインパターンに合わせる」を売りとする。

**不採用と判断した。** 調査結果は以下。

| 項目 | 実測結果 |
|---|---|
| ソース公開 | ❌ `AI-Diffusion-Organization/growthpedia` は GitHub API で **404**。全体検索も 0 件 |
| ライセンス | ❌ `UNLICENSED` |
| メンテナ | 個人 1 名（npm: `tyleryin`）。法人は公式サイト footer の "AIDesigner Inc." のみ |
| バージョン | v0.1.4（2026-04-11）。以降更新なし |
| 採用実績 | npm 月 427 DL / 週 73 DL |
| 実体 | `https://api.aidesigner.ai` への SaaS クライアント。OAuth 必須・**$25/月**（100 クレジット） |
| 送信データ | 絶対パス・依存一覧・ルート候補・コンポーネントディレクトリ・CSS 変数（コード本体は送らない） |
| コード品質 | ⭕ tarball 全 13 ファイルを実読。postinstall なし・難読化なし・テレメトリなし・依存 1 個。ユーザースコープでは `claude mcp add` を spawn する行儀の良い実装 |

**決め手は採否基準 #6。** 同等の機能を Anthropic 一次提供の `claude_design` MCP
（`https://api.anthropic.com/v1/design/mcp`）が既にカバーしており、
**新規ベンダーもデータ境界も増やさずに同じ成果が得られる**。
リポジトリ解析の中身も `package.json` の依存判定・ルート候補・CSS 変数の収集にとどまり、
Claude Code が Read / Grep で直接読める情報の劣化版だった。

> **記事情報の注意点**: 各所で紹介されている `init claude-code` という引数は**誤り**。
> ソース上の `SUPPORTED_HOSTS` は `claude | codex | cursor | vscode | windsurf` で、
> `claude-code` は `Unsupported host` 例外になる。ベンダー公式 docs も引数なしの
> `npx -y @aidesigner/agent-skills init` と記載している。二次情報（SNS 投稿）を
> 一次情報で検証せずに実行すると失敗する典型例として記録しておく。

---

## 既知の重複（要整理）

`frontend-design` が **2 系統**存在する。

| 実体 | 経路 |
|---|---|
| `~/.agents/skills/frontend-design` ← `~/.claude/skills/frontend-design` | skills CLI（vercel-labs）で導入 |
| `frontend-design:frontend-design` | Anthropic 公式 plugin marketplace |

description が競合するとスキル選択の精度が落ちるため、**どちらかへの一本化を検討する**。
公式 plugin 側を残す方針が妥当。

---

## 関連ドキュメント

- [使用ツールスタック](tool-stack.md) — 導入済みツールの棚卸し
- [MCP サーバーの追加方法](mcp-setup.md)
- [Skills ガイド](skills.md)
- [ベストプラクティス](best-practices.md)
