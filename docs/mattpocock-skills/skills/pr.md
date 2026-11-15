# pr — PR 本文を Summary / Evidence / Merge Danger の 3 節で書く skill

> 出典（一次情報）:
> - [pr/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr/SKILL.md) — skill 本体
> - [pr/CREDITS.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr/CREDITS.md) — Summary 節の出典表記
> - [docs/engineering/pr.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/pr.md) — 同じ作者による解説ページ（補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- PR 本文の「形」だけを定める書式リファレンスである。branch の push も PR の作成もしない。
- 本文は **Summary**（変更の姿を図で示す）、**Evidence**（動く証拠の before / after）、**Merge Danger**（戻せるか・影響範囲）の 3 節で書く。
- Summary は文章ではなく、要点が伝わる最小の図（疑似コード・呼び出しツリー・コンポーネントツリー・ファイルツリー・Mermaid・diff）を選ぶ。
- Merge Danger では one-way door / two-way door と blast radius を明記する。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方 |
| 呼び出し方 | `/mattpocock-skills:pr` |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | なし（本文の書式を示すだけ） |

## 3. いつ使うか・使わないか

使う場面:

- PR 本文を書くとき（description は「Use when writing a PR body.」、`SKILL.md:3`）。モデル起動が可能なので、エージェントが PR 本文を書く場面では自動で使われる（解説ページ）。

使わない場面:

- まだ誰もレビューしていないコード。先に [code-review](code-review.md) を通す（解説ページ）。
- PR に付いたレビューコメントの仕分け・対応。本 skill は本文を書いて止まる（解説ページ）。

## 4. 流れ

手順ではなくテンプレートである。次の形で本文を書く（`SKILL.md:12-33`）。

```markdown
## Summary

<diagram, diff-sketch, or tree>

## Evidence

- **Before:** <screenshot/output/failing test run>
  **After:** <screenshot/output/passing test run>

## Merge Danger

**Door:** <one-way or two-way>

<optional: description>

**Blast Radius:** <one-word description>

<optional: potential ramifications of merge>
```

全体の規則: 前置きを書かず、文章は短くする。用語は `GLOSSARY.md` にあるユーザーのドメイン言語を使う（`SKILL.md:37`）。

1. **Summary**。要点が伝わる最小の表現を選ぶ（`SKILL.md:41`）。
   - ロジックやアルゴリズム → 疑似コード（pseudocode）
   - 実行時の制御フロー → 呼び出しツリー（call tree）
   - UI 構造 → コンポーネントツリー（state やモジュールの境目も含める）
   - ファイルの責務や広範なリファクタ → 浅いファイルツリー
   - コンポーネント間の連携・データフロー → Mermaid
   - 周囲の形は既にあり、変化が要点 → `diff`。話題に合わせて diff の形（コンポーネント・ファイル配置・呼び出しツリー・状態遷移）を選ぶ
   - 大半が新規、または順序や所有関係が省略で隠れる場合 → ブロック全体（`SKILL.md:43-150`）
   - 図は、それを支える短い文の隣に置く。必要な呼び出し・ファイル・props・状態・境目だけを残す。1 つか数個を使い、全部は使わない（`SKILL.md:154-156`）。
2. **Evidence**。変更が動く具体的な証拠を before / after で示す。見た目の変更でスクリーンショットが撮れる環境なら最上（S-tier）。テスト結果やコンソール出力などの実行ベースの証拠は次点（A-tier）。失敗していたテストが通るようになったことを疑似コードで示す（`SKILL.md:160-164`）。
3. **Merge Danger**。one-way door（戻せない）か two-way door（戻せる）かを書く。破壊的な操作や戻しにくい決定を含む変更は one-way door である。blast radius は変更が及びうる範囲で、レイアウト崩れ・利用側の破損・モバイル表示などあらゆる可能性を考える（`SKILL.md:168-170`）。

## 5. 書き込むもの・副作用

なし。SKILL.md は本文のテンプレートと書き方だけを定め、git・GitHub・ファイルへの操作を指示していない（`SKILL.md:12-170`）。PR を開く操作は本 skill の範囲外である（解説ページ）。

## 6. 前後の skill

解説ページが示す本流は `to-spec → to-tickets → implement → code-review → pr → retro` である。

- 前: [implement](implement.md) が本文の対象になるコミットを作る。
- 前: [code-review](code-review.md) でレビュー済みの差分について本文を書く。
- 後: [retro](retro.md) でセッションを振り返る。

## 7. 注意点

- **PR 本文の言語や署名の扱いは各リポジトリの規約に従う。**
- **リポジトリ既存の PR テンプレートとの関係**。本 skill は `.github/pull_request_template.md` などを探さない。何もしないと同じ本文に 2 つの指示が並ぶので、リポジトリのエージェント向け文書でどちらを優先するか決めておく（解説ページ）。
- **door 判定は鵜呑みにしない**。書いたエージェント自身が判定するため、「two-way、blast radius 小」は特に疑う。diff だけでは戻せるか分からないことが多いので、spec や ticket も渡す（解説ページ）。
- **本文は書いた時点のもの**。レビュー中に大きく変わったら書き直しを頼む（解説ページ）。
- **Mermaid はターミナルでは描画されない**。GitHub / GitLab の PR 本文では描画される（解説ページ）。
- Summary 節の図の選び方は Dex Horthy の `show-me` skill からほぼそのまま取り込んだもので、依存はしていない（`CREDITS.md:3`）。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| pr/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| pr/CREDITS.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr/CREDITS.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/pr.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/pr.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [code-review](code-review.md) / [retro](retro.md)
