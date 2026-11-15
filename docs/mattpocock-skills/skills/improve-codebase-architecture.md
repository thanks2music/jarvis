# improve-codebase-architecture — コードベースから deep にする候補を探し、HTML レポートにして選んだ 1 件を詰める skill

> 出典（一次情報）:
> - [improve-codebase-architecture/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/improve-codebase-architecture/SKILL.md) — skill 本体
> - [improve-codebase-architecture/HTML-REPORT.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/improve-codebase-architecture/HTML-REPORT.md) — HTML レポートの雛形・図のパターン・文体
> - [docs/engineering/improve-codebase-architecture.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/improve-codebase-architecture.md) — 同じ作者による解説ページ（補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- shallow module を deep module に変えるリファクタ候補（deepening opportunities）を探す。狙いはテストしやすさと AI の辿りやすさ。
- 範囲を絞ってから走査する（YAGNI）。指定が無ければ commit 履歴から変更の多い場所を優先する。
- 候補は自己完結の HTML レポートとして OS の一時ディレクトリに書き出し、ブラウザで開く。リポジトリには置かない。
- レポートの後は止まって「どれを掘り下げるか」を尋ね、選ばれた 1 件を [grilling](grilling.md) で詰める。
- コードは変更しない。ただし詰める途中で `GLOSSARY.md` を更新し、ADR の記録を提案する。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーのみ（`/mattpocock-skills:improve-codebase-architecture` で起動） |
| 呼び出し方 | `/mattpocock-skills:improve-codebase-architecture` |
| 内部で呼ぶ skill | [codebase-design](codebase-design.md) / [grilling](grilling.md) / [domain-modeling](domain-modeling.md) |
| 外部への書き込み | ファイル（`$TMPDIR` の HTML レポート、`GLOSSARY.md`、提案が受け入れられた場合の ADR） |

## 3. いつ使うか・使わないか

使う場面（解説ページ）:

- 定期的な手入れ。数日おきに回して、機能追加の合間に構造が崩れないようにする。
- 大きな実装の前。spec を示して「この変更を楽にするには？」と聞くのが最も効く使い方とされる。
- 構造の無い既存リポジトリの健康診断。
- テストの無いレガシーコードに、テストを書く前に足りない seam を探す。

使わない場面（解説ページ）:

- 直す module が既に決まっている → [codebase-design](codebase-design.md) で設計する。
- 1 セッションに収まらない大きな取り組み → [wayfinder](wayfinder.md)。
- 特定の不具合の原因調査 → [diagnosing-bugs](diagnosing-bugs.md)。

## 4. 流れ

前提として、Skill tool で `codebase-design` を呼び、語彙（module / interface / depth / seam / adapter / leverage / locality）と原則を使う。「component」「service」「API」「boundary」には言い換えない。`GLOSSARY.md` のドメイン言語と `docs/adr/` の ADR も参照し、ADR で決まったことは蒸し返さない（`SKILL.md:11-14`）。

1. **探索（Explore）**（`SKILL.md:18-35`）
   - 走査の前に範囲を決める（YAGNI）。ユーザーが方向（module・サブシステム・困りごと）を示したらそれに従う。無ければ `git log --oneline` で履歴を遡り、何度も出てくるファイルや領域（ホットスポット）を優先する。散らばっていれば範囲を広げる。
   - 触る領域の `GLOSSARY.md` と ADR を先に読む。
   - サブエージェントを起動してコードベースを歩かせる。固定の手順に従わず、引っかかった箇所を記録する。観点は「1 つの概念を理解するのに多数の小さな module を行き来するか」「interface が implementation と同じくらい複雑な shallow module はどこか」「テストのためだけに純粋関数を切り出し、バグは呼び出し方に潜んでいないか（locality が無い）」「密結合な module が seam を越えて漏れていないか」「テストが無い、または今の interface では試しにくい場所はどこか」。
   - shallow と疑うものには削除テスト（deletion test）をかける。消すと複雑さが集約されるなら良い兆候である。
2. **候補を HTML レポートで示す**（`SKILL.md:37-60`）
   - 自己完結の HTML を OS の一時ディレクトリに書く。`$TMPDIR`、無ければ `/tmp`（Windows は `%TEMP%`）を使い、`<tmpdir>/architecture-review-<timestamp>.html` に保存する。`open`（macOS）/ `xdg-open`（Linux）/ `start`（Windows）で開き、絶対パスを伝える。
   - Tailwind と Mermaid を CDN から読み込む。グラフ状の関係は Mermaid、編集的な図は手組みの div / SVG を使う。各候補に before / after の図を付ける。
   - 候補ごとのカードには Files / Problem / Solution / Benefits（locality と leverage、テストがどう良くなるか）/ Before・After 図 / 推奨度（`Strong` / `Worth exploring` / `Speculative` のバッジ）を載せる。最後に **Top recommendation**（最初に取り組む候補とその理由）を置く。
   - 既存の ADR と矛盾する候補は、ADR を見直す価値があるほど痛みが大きい場合だけ出し、カードに警告として明記する。
   - この段階では interface を提案しない。ファイルを書いたら「Which of these would you like to explore?」と尋ねる。
   - 雛形・図のパターン（Mermaid グラフ、手組みの箱と矢印、断面図、質量図、呼び出しグラフの畳み込み）・配色・文体は HTML-REPORT.md に従う（`HTML-REPORT.md:5-123`）。
3. **詰める（Grilling loop）**（`SKILL.md:62-71`）
   - ユーザーが候補を選んだら、Skill tool で `grilling` を呼び、制約・依存・deep にした module の形・seam の裏に置くもの・残るテストを一緒に詰める。
   - 決定が固まるたびに、Skill tool で `domain-modeling` を呼んでドメインモデルを更新する。
     - deep にした module に `GLOSSARY.md` に無い概念名を付けたら、その用語を `GLOSSARY.md` に足す。ファイルが無ければその時点で作る。
     - あいまいな用語を明確にしたら、その場で `GLOSSARY.md` を更新する。
     - ユーザーが重い理由で候補を却下したら、「今後のレビューで再提案されないよう ADR に記録しますか？」と提案する。一時的な理由や自明な理由では提案しない。
     - interface の別案を探りたい場合は `codebase-design` の Design It Twice（並列サブエージェント）を使う。

## 5. 書き込むもの・副作用

| 種類 | 内容 | 根拠 |
|---|---|---|
| git | `git log --oneline` の読み取りのみ。commit・branch・push は無い | `SKILL.md:23` |
| サブエージェント | コードベース探索用に起動する。Design It Twice を使えばさらに並列起動する | `SKILL.md:27`, `SKILL.md:71` |
| $TMPDIR | `<tmpdir>/architecture-review-<timestamp>.html` を書き出し、OS のコマンドで開く | `SKILL.md:39` |
| ネットワーク | レポートが Tailwind と Mermaid を CDN から読み込む | `SKILL.md:41`, `HTML-REPORT.md:13-17` |
| repo 内ファイル | `GLOSSARY.md` に用語を追加・更新する（無ければ作成） | `SKILL.md:68-69` |
| repo 内ファイル | 却下理由を ADR に記録するか提案する（作成はユーザーの了承後） | `SKILL.md:70` |
| skill 呼び出し | `codebase-design` / `grilling` / `domain-modeling` | `SKILL.md:13`, `SKILL.md:64`, `SKILL.md:66` |

コード自体は変更しない（SKILL.md に該当する指示が無い。解説ページも「It never changes the code」と明言）。

## 6. 前後の skill

本流の 1 段ではなく、定期的な手入れとして本流の外で回す（解説ページ）。

- 内部: [codebase-design](codebase-design.md) が語彙を、[grilling](grilling.md) が決定木の詰めを、[domain-modeling](domain-modeling.md) が `GLOSSARY.md` と ADR の更新を担う。
- 前: 共通の語彙が無いコードベースでは、先に [grill-with-docs](grill-with-docs.md) で語彙を作ると結果が良くなる（解説ページ）。
- 後: 出てきた決定は本流に戻し、[to-spec](to-spec.md) → [to-tickets](to-tickets.md) → [implement](implement.md) で実装する。リファクタは別セッションで行う（解説ページ）。
- 対: [retro](retro.md) はエージェントの環境を、本 skill はコードを改善する（解説ページ）。

## 7. 注意点

- 起動はユーザーのみ（`disable-model-invocation: true`、`SKILL.md:4`）。
- **質問攻めになることがある**。設計意図はレポートが先で、詰めは選んだ候補だけだが、モデルによっては最初の案についてすぐ延々と質問を始める。起動時に「詰めずにレポートだけ見せて」と伝えると避けられる。専用の no-grill モードは無い（解説ページ）。
- **レポートがスタイル無しで表示される**。CDN を読めない環境（オフライン、SRI ハッシュを強制するセキュリティ hook など）では図も崩れる。エージェントはページを描画しないので気付かない。インライン CSS と手組み SVG を頼むと回避できる（解説ページ）。
- **1 セッション 1 候補**。複数を同じ会話で進めるとコンテキストが溢れる。残りは ticket にして後で拾う（解説ページ）。
- **「問題なし」とはまず言わない**。候補を出すための skill なので、全候補が `Speculative` なら実質的に何も見つからなかったと読む（解説ページ）。
- `GLOSSARY.md` は gitignore されていなければ作業ツリーに差分として残る（推測）。コミットするかどうかは利用者が決める。
- 権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| improve-codebase-architecture/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/improve-codebase-architecture/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| improve-codebase-architecture/HTML-REPORT.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/improve-codebase-architecture/HTML-REPORT.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/improve-codebase-architecture.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/improve-codebase-architecture.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [codebase-design](codebase-design.md) / [grilling](grilling.md) / [domain-modeling](domain-modeling.md) / [retro](retro.md)
