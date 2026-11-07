# デザインワークフロー — ツールの使い分け

> 最終更新: 2026-11-07（用途別の表にロゴ・画像生成の行を追加し、「[ロゴ・ブランドアセット](#ロゴブランドアセット)」節を新設）
>
> 出典（一次情報）: [How the product designer who built Claude Design uses it](https://claude.com/resources/articles/how-the-product-designer-who-built-claude-design-uses-it-to-explore-ideas-before-building-them)（2026-07-24 公開。Claude Design はロゴ制作に不向きと明言）/ [WCAG 2.2 SC 1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum)（ロゴの文字はコントラスト要件の対象外）/ [HTML Standard: link type "icon"](https://html.spec.whatwg.org/multipage/links.html#rel-icon)（favicon の選ばれ方）/ [Claude Design (Anthropic Labs)](https://www.anthropic.com/news/claude-design-anthropic-labs)（2026-04-17 公開。Claude Code への実装ハンドオフに言及）/ [whats-new week 34](https://code.claude.com/docs/en/whats-new/2026-w34)（スキル `/design` の追加。**導入は v2.1.234**、当時は research preview）/ [Built-in commands](https://code.claude.com/docs/en/commands)（**`/design` の現行要件は v2.1.265+**）/ [Build live dashboards and animate explainers with Claude](https://claude.com/resources/articles/dashboards-and-motion)（2026-10-08 公開。Claude Design の beta 終了・全プラン提供・`claude.ai/design` の 2026-12-14 閉鎖予定）/ [Migrate from standalone Claude Design to Claude](https://support.claude.com/en/articles/17440474)（デザインシステムの移行手順）

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
| **ロゴ・アイコン・ブランドアセットの制作** | `figma` MCP の `use_figma`（Figma 上にベクターで直接組む） | Figma 公式 |
| **写真・イラスト・アイキャッチの画像生成（ラスタ）** | `figma` MCP の `generate_image` / Gemini の画像生成（`nano-banana` skill 等） | Figma 公式 / 自作（Gemini CLI を呼ぶ） |
| **実装後の目視確認・表示崩れチェック** | `browse-playwright` → `browse-chrome` | 自作スキル |

### 補足

- **`claude_design` と `design` skill の関係**: どちらも Claude Design 基盤。
  MCP はプロジェクト管理・ファイル書き込み・プレビュー描画・共有/コメントまで扱う。
  `design` skill（`/design`）は Claude Code から Claude Design の artifact（canvas 上の artboard）を下書きするバンドルスキルで、
  **視覚的に手で直したい**場合に向く。要件は v2.1.265+・artifacts が使えるセッション・Design テンプレートが有効なアカウント（commands ページ）。
  **2026-10-11 訂正**: 以前は「早期プレビュー版」と書いていた。Claude Design 自体は 2026-10-08 に beta を終えたが、
  Claude Code の Artifacts ページは 2026-10-11 時点でも Templates を beta と書いており、docs が未追従である
  （[AI デザイン制作ツール §2.5](ai-design-tools.md#25-スタンドアロン版の閉鎖と移行)）。
- **`browse-playwright` を先に試す**: ブラウザ確認のフォールバックチェーンは
  `~/.claude/work-style.md` の「ブラウザ確認の自走原則」に従う。
- **ロゴの最終成果物に Claude Design と画像生成を使わない**: Claude Design は画像モデルを持たず、公式に「ロゴ制作には不向き」とされている（2026-07-24 時点）。
  今回試した画像生成（Gemini・ChatGPT Images・Figma の `generate_image`）はラスタしか出力しない。画像生成は発想段階までにとどめ、ロゴは Figma 上でベクターとして作る（次節）。

---

## ロゴ・ブランドアセット

> 2026-11-07、個人開発のサービス（アニメイベントのレビューサイト）のロゴ制作で実証した。
> それ以前に、画像生成モデル（Gemini・ChatGPT Images）と Claude が手で書いた SVG で 300 案を超える PoC を行い、採用案が出なかった。
> 同じ題材を本節のやり方に切り替えたところ、2 ラウンドで確定した。

### 結論

1. **Claude Design はロゴに使わない。** 公式ブログ（2026-07-24）が、画像モデルを持たずロゴ制作に不向きで、既存のロゴを持ち込むのが良いと明言している（原文の引用は [AI デザイン制作ツール §2.1](ai-design-tools.md#21-何ができるか)）。ロゴが決まってから、デザインシステムに登録して展開する用途で使う
2. **画像生成モデルの出番は発想段階まで。** 今回試したモデルの出力はラスタだけで、比率・余白・時刻のような数値の指定や、「〜に見えないように」という否定形の指示が効かない（PoC で実測）。最終成果物はベクターで作る
3. **Claude の強みは、構造を持ったベクターの組み立てと、体系的な比較。** 実在の書体を `use_figma` で配置してアウトライン化し、幾何学的な部品と組み合わせれば、字形は崩れない。手描きの曲線は Claude の弱点なので避ける。Figma 上に直接組めば、人が手で微調整できる
4. **白い紙の上ではなく、使う場所に置いて評価する。** 実際のヘッダー（モバイルは等倍）・下層ページのブランドバー・PC ヘッダー・暗い背景・単色・favicon（16/32/48px）に並べた比較シートで判断する。白い紙の上で見栄えのする案は、ヘッダーの高さ 32px 前後では重すぎたり、小さい文字が読めなかったりする
5. **多めに出してから選び、混ぜる。** 公式ブログの「Ask for ten options, then remix」と同じ考え方。1 回目は 3 つの表記それぞれに方向を変えた 5 案ずつ、計 15 案を広く出し、選ばれた案の要素を 2 回目で組み合わせ直す
6. **作り手による自己評価には偏りが出る。** 採否は、置き場所に即したチェックリストと、人の判断で決める。批評役の SubAgent を立てる方法もあるが、この案件では使わなかった
7. **公式 skill にロゴ専用のものは無い。** 原則は公式 plugin の `frontend-design:frontend-design`（題材に根ざした書体選択・AI の既定値を避ける・計画→制作→批評。`~/.claude/skills/` 側の古い複製には無い。下の「[既知の重複](#既知の重複要整理)」）と `canvas-design`（先に哲学を決める）から借りる。`use_figma` の前には `/figma-use` の読み込みが必須。見た目を変える書き込みでは `/figma-generate-design` も読む。再利用するコンポーネントやトークンが主な成果物なら、代わりに `/figma-generate-library` を読む（構成済みのビューも作るなら両方）。読み取りだけならどちらも要らない

### 進め方（実証済み）

1. **置き場所と制約を先にブリーフへ書く。** 既存のデザイントークン（色・書体・角丸）と、ロゴが置かれる場所の寸法を入れる。「発想を縛らないため制約を入れない」ブリーフは、UI に合わない案を量産する
2. **`use_figma` で文字を組み、`figma.flatten` でアウトライン化する。** 書体は、ロゴ・商標への利用を許すライセンス（例: SIL Open Font License）のものに限る。 パスのデータを部品ごとに分けて扱えるので、濁点・i の点だけを別の図形に差し替える、といった加工ができる。組み上げた図形は `figma.createNodeFromSvg` で戻し、`figma.createComponentFromNode` でコンポーネントにする
3. **比較シートを作る。** 各案のインスタンスを、上の「使う場所」に並べたフレームを Figma 上に作り、`get_screenshot` で確認する（`get_screenshot` は読み取り系でレート制限の対象。View / Collab シートは月 20 コールで、この進め方には Full / Dev シートが要る。キャンバスへの書き込みも、ベータ後は有料になる。[AI デザイン制作ツール §4.4](ai-design-tools.md#44-figma-mcp-サーバー)）。1 回目の結果は Figma 上に注記として残す（外した案も消さない）
4. **確定版をコンポーネントにする。** 横組み・小さい場所用・シンボル・favicon 16px 専用・単色・暗い背景用を分け、余白のルールと最小サイズを注記する
5. **SVG を書き出し、実ブラウザで確認する。** ヘッダーの模型を載せたプレビュー HTML を Playwright で開き、表示とコンソールエラーを確かめる

### 落とし穴

- **Plugin API では OpenType の `palt` を設定できない。** `openTypeFeatures` は読み取り専用で、日本語の詰め組みを書体の機能で行えない。代わりに、文字ごとに TextNode を分けてからアウトライン化し、字面の間隔をそろえて並べる（`setRangeLetterSpacing` で文字ごとに字間を変える方法もある）。今回は 1 つの TextNode をアウトライン化した後、x 方向に重なるサブパスを 1 字とみなして並べ直したが、この見分け方は「い」「ハ」「ル」のように離れた画を持つ字を 2 字に割り、詰めた字どうしを 1 字にまとめてしまう
- **`download_assets` の SVG 書き出しは、親フレームの背景まで含める。** 親の無い一時インスタンスをページの最上位に置いてから書き出し、ページ背景の矩形 1 行を取り除く。`exportAsync({ format: 'SVG_STRING' })` ならノード単体を書き出せるが、長いパスを手で書き写すと数値の写し間違いが起きうる
- **`figma.subtract` の結果には既定の灰色の塗りが付く。** 結果の `fills` を明示的に設定する
- **書体の有無は `figma.listAvailableFontsAsync()` で確かめる。** Google Fonts にあっても Figma に無い書体がある
- **ロゴの文字は、WCAG のコントラスト要件の対象外である**（SC 1.4.3「Text that is part of a logo or brand name has no contrast requirement.」）。ただし読めるかどうかは別の問題で、薄い色を文字の本体に使わない
- **16px だけ別デザインの favicon は作れるが、実ブラウザで確かめる。** HTML 仕様は「type・media・sizes 属性に照らして最も適切なアイコンを選ぶ」「同等に適切なものが複数あれば、最後に宣言したものを使う」と定めるが、何が最も適切かの判定は実装に委ねられている。`sizes="any"` を宣言した SVG や ICO を置くと、全サイズでそれが選ばれる可能性がある（Next.js の metadata files では、`.svg` の icon と `app/favicon.ico` に `sizes="any"` が自動で付く）

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

### スタンドアロン版の閉鎖（2026-12-14 まで）

Claude Design は 2026-10-08 に beta を終え、Free を含む全プランで Claude 本体（通常の会話・Artifacts）から使える。
スタンドアロン版 `claude.ai/design` は **2026-12-14 までに閉鎖**され（公式の表現は「closes by December 14, 2026」）、Claude 本体に統合される。

- standalone で作ったデザインシステムは、Claude の Artifacts ページの **「Migrate team design systems」** で組織分をまとめて移行する
- **Claude とのチャットと、プロジェクト・デザインシステムへのコメントは移行されない**。閉鎖後に削除されるため、要るものは閉鎖前に保存する
- 閉鎖後に `/design-sync` と `claude_design` MCP がどこへ同期・接続するかは、公式に記載が無く**未確認**（2026-11-01 確認）

詳細は [AI デザイン制作ツール §2.5](ai-design-tools.md#25-スタンドアロン版の閉鎖と移行) を参照。

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
- [AI デザイン制作ツール](ai-design-tools.md) — Claude Design / Figma Make / v0 / Google Stitch の仕様と現在地
- [デザイントークン](design-tokens.md) — トークンの概念・DTCG 2025.10・正本の置き場所
- [MCP サーバーの追加方法](mcp-setup.md)
- [Skills ガイド](skills.md)
- [ベストプラクティス](best-practices.md)
