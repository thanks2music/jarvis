# diagnosing-bugs — 難しいバグや性能劣化を、まず「赤くなる再現ループ」を作ってから 6 段階で診断する skill

> 出典（一次情報）:
> - [diagnosing-bugs/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs/SKILL.md) — skill 本体
> - [diagnosing-bugs/scripts/hitl-loop.template.sh (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh) — 人が操作する再現ループのテンプレート
> - [docs/engineering/diagnosing-bugs.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/diagnosing-bugs.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- 難しいバグと性能劣化のための診断手順。段階を飛ばすのは、明確な理由がある場合だけ（`SKILL.md:8`）。
- 中心は Phase 1 の **フィードバックループ** 作り。このバグで赤くなる、速くて決定的なコマンドができるまで、仮説を立てない（`SKILL.md:20`, `SKILL.md:59-66`）。
- 仮説は 3〜5 個を順位付きで出し、検証前にユーザーに見せる（`SKILL.md:90-98`）。
- 修正は、正しい継ぎ目（seam）があれば回帰テストを先に書いてから行う。最後にデバッグログと使い捨てコードを片付ける（`SKILL.md:116-138`）。
- 出力に含まれる秘密情報は `<REDACTED>` に置き換えてから見せる（`SKILL.md:14`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:diagnosing-bugs`。「diagnose」「debug this」や、何かが壊れている・例外が出る・失敗する・遅いという報告でモデルも起動する（`SKILL.md:3`） |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（テスト、再現スクリプト、一時的なデバッグログ、修正コード）。git の commit / PR メッセージへの記載は Phase 6 のチェック項目にある |

## 3. いつ使うか・使わないか

使う場面:

- 一目では解けないバグ、たまにしか起きない不具合、2 つの既知の状態の間で入った回帰（`docs/engineering/diagnosing-bugs.md:11`）。
- 前後が分かっている性能劣化。性能用の分岐（ベースラインを測ってから二分探索）がある（`SKILL.md:112`）。

使わない場面:

- 「このコードベースのボトルネックはどこか」のような、具体的な症状のない監査。この skill は既知の 1 つの不具合を診断するもので、監査はしない（`docs/engineering/diagnosing-bugs.md:17`）。
- 1 つの返答で済ませたい軽い質問。解説ページは、軽い質問でこの skill が起動して返答が遅れる報告を挙げている。「診断せずに答えだけ」と伝えるのが回避策である（`docs/engineering/diagnosing-bugs.md:60`）。

## 4. 流れ

調査中は `GLOSSARY.md` があれば読み、触る領域の ADR を確認する（`SKILL.md:10`）。

1. **Phase 1: フィードバックループを作る（Build a feedback loop）**。この skill の本体である（`SKILL.md:20`）。作り方はおおむね次の優先順（`SKILL.md:26-35`）。
   1. 失敗するテスト（unit / integration / e2e）
   2. 起動中の dev サーバーへの curl / HTTP スクリプト
   3. fixture 入力での CLI 実行と、正常時の出力との diff
   4. headless ブラウザのスクリプト（Playwright / Puppeteer）
   5. 記録したトレース（リクエスト、ペイロード、イベントログ）の再生
   6. 使い捨てのハーネス（システムの最小部分）
   7. プロパティ / ファズのループ
   8. `git bisect run` で回せる二分探索ハーネス
   9. 旧版と新版の出力を比べる差分ループ
   10. 最後の手段として、人が操作する HITL bash スクリプト（`scripts/hitl-loop.template.sh`）

   ループができたら、速く・鋭く・決定的にする（`SKILL.md:41-47`）。たまにしか起きないバグでは、きれいな再現ではなく **再現率を上げる** ことを目標にする（`SKILL.md:51`）。どうしてもループが作れなければ、止まって試したことを列挙し、再現環境へのアクセス、秘密情報を伏せた記録（HAR、ログ、コアダンプ、録画）、本番への一時的な計測の追加許可のどれかをユーザーに求める。ループなしで仮説に進んではならない（`SKILL.md:55`）。

   **完了条件**: すでに 1 回実行した 1 つのコマンドを示せること。そのコマンドは、ユーザーの症状そのものを検査して赤くなれる（red-capable）、毎回同じ結果になる（deterministic）、数秒で終わる（fast）、エージェントが単独で回せる（agent-runnable）、の 4 つを満たす（`SKILL.md:59-66`）。
2. **Phase 2: 再現して最小化する（Reproduce + minimise）**。ループを回して赤くなるのを確認する。ユーザーが述べた症状であること、複数回再現すること、正確な症状を記録したことを確かめる（`SKILL.md:70-76`）。次に、入力・呼び出し元・設定・データ・手順を 1 つずつ削り、毎回ループを回して、残った要素がすべて必要な状態まで縮める（`SKILL.md:80-86`）。
3. **Phase 3: 仮説を立てる（Hypothesise）**。検証前に 3〜5 個の仮説を順位付きで出す。各仮説は「X が原因なら、Y を変えるとバグが消える / Z を変えると悪化する」の形で反証可能にする。順位付きの一覧をユーザーに見せる。ユーザーが不在なら自分の順位で進める（`SKILL.md:90-98`）。
4. **Phase 4: 計測する（Instrument）**。各プローブは Phase 3 の予測 1 つに対応させ、変数は 1 度に 1 つだけ変える。デバッガ / REPL を優先し、次に仮説を区別する境界での的を絞ったログを使う。デバッグログには `[DEBUG-a4f2]` のような固有の接頭辞を付ける（`SKILL.md:102-110`）。性能劣化ではログより、ベースラインを測ってから二分探索する（`SKILL.md:112`）。
5. **Phase 5: 修正と回帰テスト（Fix + regression test）**。実際のバグの形を呼び出し箇所で再現できる「正しい継ぎ目」があれば、修正前に回帰テストを書く。なければ、その事実を発見として記録する（`SKILL.md:116-120`）。継ぎ目がある場合は、最小化した再現を失敗するテストにする → 失敗を確認する → 修正する → 成功を確認する → 最小化前の元のシナリオで Phase 1 のループを再実行する（`SKILL.md:124-128`）。
6. **Phase 6: 片付け（Cleanup）**。元の再現が起きないこと、回帰テストが通ること（または継ぎ目がないことの記録）、`[DEBUG-...]` の計測をすべて消したこと、使い捨てのプロトタイプを消したこと（または明示したデバッグ用の場所に移したこと）、正しかった仮説を commit / PR メッセージに書いたことを確認する（`SKILL.md:132-138`）。

## 5. 書き込むもの・副作用

| 対象 | 内容 | 根拠 |
|---|---|---|
| repo 内ファイル（テスト・スクリプト） | 再現ループ用の失敗するテスト、curl / CLI / ブラウザのスクリプト、使い捨てハーネスを作る | `SKILL.md:26-35` |
| repo 内ファイル（一時的なデバッグログ） | `[DEBUG-...]` 付きのログを入れ、Phase 6 で消す | `SKILL.md:110`, `SKILL.md:136` |
| repo 内ファイル（修正・回帰テスト） | 回帰テストを書き、修正を適用する | `SKILL.md:124-127` |
| HITL スクリプト | テンプレートをコピーして手順を書き換え、実行する。ユーザーの入力は `KEY=VALUE` で出力される | `SKILL.md:35`, `hitl-loop.template.sh:3`, `hitl-loop.template.sh:13` |
| git（bisect） | 回帰の範囲が分かっていれば `git bisect run` を使う | `SKILL.md:33` |
| git commit / PR メッセージ | 正しかった仮説を commit / PR メッセージに書く（Phase 6 のチェック項目）。commit や PR を作る手順そのものは書かれていない | `SKILL.md:138` |
| 外部サービス | 本番への一時的な計測の追加は、ユーザーの許可を得てから行う | `SKILL.md:55` |

## 6. 前後の skill

- 前: 他の人から届いた未確認のバグ報告は、先に [triage](triage.md) を通す。triage は Phase 1〜2 の浅い版を行う（`docs/engineering/diagnosing-bugs.md:19`, `docs/engineering/diagnosing-bugs.md:94`）。
- 後: 修正後、同じセッションで [retro](retro.md) を実行し、何があればこのバグを防げたかを振り返る。この skill は retro を自動では呼ばない（`docs/engineering/diagnosing-bugs.md:94`）。
- 正しい継ぎ目がない場合は [improve-codebase-architecture](improve-codebase-architecture.md) を自分で起動する（`docs/engineering/diagnosing-bugs.md:22`）。
- 設計上の問いに答えるだけなら [prototype](prototype.md)、計画した振る舞いをテスト先行で作るなら [tdd](tdd.md)（`docs/engineering/diagnosing-bugs.md:20-21`）。

## 7. 注意点

- **モデルが自動で起動する**。軽い質問でも起動し、再現シナリオ作りから始めることがある（`docs/engineering/diagnosing-bugs.md:60`）。
- **修正前の確認ゲートはない**。人の確認があるのは Phase 3 の仮説一覧だけで、計測から修正までの間に止まらない。修正前に止まってほしければ、起動時にそう伝える（`docs/engineering/diagnosing-bugs.md:66`）。
- **秘密情報**。コマンド・出力・記録を見せる前に秘密情報を `<REDACTED>` に置き換え、認証情報は環境変数に置く。伏せた出力で診断できなければ、そう伝えてユーザーに尋ねる（`SKILL.md:14-16`）。HITL スクリプトの `capture` は入力値を端末に表示するので、サインインは `step` としてユーザーに任せる（`hitl-loop.template.sh:15-16`）。
- **旧名**。v1.0.0 で `/diagnose` から改名された（`docs/engineering/diagnosing-bugs.md:78`）。
- **git 権限**。権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| diagnosing-bugs/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| diagnosing-bugs/scripts/hitl-loop.template.sh | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/diagnosing-bugs.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/diagnosing-bugs.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [triage](triage.md) / [retro](retro.md) / [tdd](tdd.md) / [prototype](prototype.md)
