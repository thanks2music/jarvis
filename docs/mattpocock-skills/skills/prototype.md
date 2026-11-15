# prototype — 設計上の問いに答えるための使い捨てコードを作る skill

> 出典（一次情報）:
> - [prototype/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/SKILL.md) — skill 本体
> - [prototype/LOGIC.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/LOGIC.md) — ロジック / 状態モデルの分岐
> - [prototype/UI.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/UI.md) — UI の分岐
> - [docs/engineering/prototype.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/prototype.md) — 同じ作者による解説ページ（二次的な補足）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- プロトタイプは「問いに答える使い捨てのコード」で、問いが形を決める（`SKILL.md:8`）。
- 分岐は 2 つ。「このロジック / 状態モデルで良いか」なら単一の HTML ファイル、「どう見えるべきか」なら 1 つのルート上に作る複数の UI バリエーション（`SKILL.md:14-15`）。
- **モデルも自動で起動できる** のに、終わるとプロトタイプを main の外の **使い捨てブランチに commit** する。実装 issue にもブランチへの参照を残す（`SKILL.md:26`）。
- 検証できた判断だけを本物のコードに取り込み、main にはその判断だけを残す（`SKILL.md:26`）。
- テスト、エラー処理、抽象化、永続化は入れない（`SKILL.md:23-24`）。

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:prototype`。状態モデルやロジックの妥当性を確かめたいとき、UI の見た目を探りたいときにモデルも起動する（`SKILL.md:3`） |
| 内部で呼ぶ skill | なし |
| 外部への書き込み | ファイル（プロトタイプのコード、本物のコードへの取り込み）、git（使い捨てブランチへの commit）、GitHub（実装 issue へのコメントで参照と答えを残す） |

## 3. いつ使うか・使わないか

使う場面:

- 状態機械の境界ケースを頭の中で追いきれないとき、画面を 3 案並べて見ないと決められないときなど、話し合いでは決まらない問いがあるとき（`docs/engineering/prototype.md:11`）。
- [wayfinder](wayfinder.md) の `wayfinder:prototype` チケットを解決するとき（`docs/engineering/prototype.md:13`）。

使わない場面:

- すでに作ったものがおかしく、その原因を知りたいとき。それは [diagnosing-bugs](diagnosing-bugs.md) の役割である（`docs/engineering/prototype.md:11`）。
- 何を作るかがすでに決まっているとき。次の手順は implement である（`docs/engineering/prototype.md:41`）。
- アプリ全体のプロトタイプ。1 つの問いに絞れないため、本番コードに流れ込みやすい（`docs/engineering/prototype.md:44`）。

## 4. 流れ

1. **分岐を選ぶ（Pick a branch）**。ユーザーの依頼、周辺のコード、またはユーザーへの質問から、どちらの問いかを見極める（`SKILL.md:12-15`）。
   - 「ロジック / 状態モデルで良いか」→ [LOGIC.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/LOGIC.md)
   - 「どう見えるべきか」→ [UI.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/UI.md)

   問いが曖昧でユーザーに連絡が取れなければ、周辺コードに合う方（バックエンドのモジュールならロジック、ページやコンポーネントなら UI）を選び、その前提をプロトタイプの冒頭に書く（`SKILL.md:17`）。
2. **ロジックの分岐（LOGIC.md）**。
   1. 何の状態モデルについての、どの問いかを 1 段落で書き、デモの冒頭に表示する（`LOGIC.md:18-20`）。
   2. 問いに答えるロジックを、DOM に依存しない純粋なモジュール（reducer、状態機械、純粋関数の集合、クラスのいずれか）として 1 つの `<script>` に分ける。後で本物のコードに移せるようにするためである（`LOGIC.md:22-33`）。
   3. フレームワークもビルドもサーバーもない、ダブルクリックで開ける 1 つの HTML ファイルを作る。ラベルはドメインの言葉で書く。構成は上から、タイトルと説明、現在の状態のパネル、自由に押せるボタン、タブごとのシナリオのガイド付きウォークスルーである（`LOGIC.md:35-50`）。
   4. ファイルを渡すか開いて見せる（`LOGIC.md:52-54`）。
   5. 答えを記録し、検証済みのロジックを本物のモジュールに移す。HTML 部分は使い捨てブランチに置く（`LOGIC.md:56-58`）。
3. **UI の分岐（UI.md）**。
   1. 問いを書き、バリエーション数 N を決める。既定は 3、上限は 5（`UI.md:36-44`）。
   2. レイアウト、情報の階層、主な操作が構造的に異なるバリエーションを作る。色だけの違いは不可（`UI.md:46-54`）。
   3. 既存ページの同じルートに `?variant=` で切り替える形（sub-shape A）を強く優先する。新しいページ（sub-shape B）は最後の手段で、プロジェクトのルーティング規約に従い、名前に `prototype` を含める（`UI.md:14-32`, `UI.md:56-75`）。
   4. 画面下部に浮かぶ切り替えバーを作る。左右の矢印とキーボードの `←` `→` で切り替え、URL も更新する。本番ビルドでは隠す（`UI.md:77-92`）。
   5. URL と `?variant=` のキーを伝える（`UI.md:94-96`）。
   6. 採用案と理由を記録する。採用案を本物のコードに取り込み、不採用案と切り替えバーは main から外して使い捨てブランチに置く（`UI.md:98-105`）。
4. **共通ルール**（`SKILL.md:21-26`）。
   - 使い捨てであることが分かる名前にし、使う場所の近くに置く。
   - 1 コマンド（`pnpm <name>` など）か、HTML のダブルクリックで動くようにする。
   - 状態はメモリに置く。データベースが問いそのものなら、「PROTOTYPE, wipe me」と分かる名前の使い捨て DB かローカルファイルを使う。
   - 操作のたびに状態全体を表示する。
   - 終わったら、検証済みの判断を本物のコードに取り込み、プロトタイプを使い捨てブランチに commit する。実装 issue にそのブランチへの参照を残し、答え（結論と、それが決めた問い）を issue か commit に残す。

## 5. 書き込むもの・副作用

| 対象 | 内容 | 根拠 |
|---|---|---|
| repo 内ファイル（プロトタイプ） | 対象モジュールやページの近くにプロトタイプのコードを置く。UI では使い捨てルートや共有の切り替えコンポーネントも作る | `SKILL.md:21`, `UI.md:28`, `UI.md:92` |
| repo 内ファイル（本物のコード） | 検証できた判断（ロジックのモジュール、採用した UI）を本物のコードに取り込む | `SKILL.md:26`, `LOGIC.md:58`, `UI.md:100-103` |
| repo 内ファイル（task runner） | UI のプロトタイプを `pnpm <name>` などの 1 コマンドで起動できるようにする（推測: package.json などのスクリプト追加を伴う） | `SKILL.md:22` |
| ローカルの使い捨て DB / ファイル | データベースが問いの場合のみ | `SKILL.md:23` |
| git commit / branch | プロトタイプを main の外の使い捨てブランチに commit する。解説ページではブランチ名を `prototype/<name>` とし、マージしないとしている | `SKILL.md:26`, `docs/engineering/prototype.md:30` |
| GitHub（実装 issue） | ブランチへの参照（context pointer）と、答えを残す（答えは commit に残してもよい） | `SKILL.md:26` |

push や PR 作成については SKILL.md に記述がない。

## 6. 前後の skill

- 前: [grilling](grilling.md) / grill-with-docs で話し合っても決まらない問いがここに来る（`docs/engineering/prototype.md:67`）。[wayfinder](wayfinder.md) の prototype チケットからも呼ばれる（`docs/engineering/prototype.md:65`）。
- 後: 検証した状態モデルや UI の方向性は [to-spec](to-spec.md) の確定した入力になる（`docs/engineering/prototype.md:67`）。
- 隣: 作ったものの不具合の原因調査は [diagnosing-bugs](diagnosing-bugs.md)。

## 7. 注意点

- **モデルが起動しても commit する**。ユーザーが `/prototype` を打たなくても起動しうる skill だが、終了時には使い捨てブランチへの commit と、実装 issue への書き込みを行う（`SKILL.md:26`）。予期しない commit を避けたい場合は、起動されたときに確認するとよい（推測）。
- **プロトタイプは削除しない**。以前は答えだけ残してコードを捨てていたが、今は一次情報としてブランチに残す。main にはマージしない（`docs/engineering/prototype.md:35`）。
- **選ぶのはユーザー**。UI では「B のヘッダーと C のサイドバー」のようなユーザーの反応が本当の答えになる（`UI.md:96`）。
- **プロトタイプをそのまま本番に上げない**。テストやエラー処理なしで書いたコードなので、取り込むときは書き直す（`UI.md:112`, `LOGIC.md:67`）。
- **別セッションで動かす**。プロトタイプは多くのコンテキストを生むため、解説ページは別セッションで動かして答えだけを持ち帰ることを勧めている（`docs/engineering/prototype.md:47`）。Zed では `/clear` が使えないため、新しいスレッドを開いて代える。
- **git 権限**。権限の扱いは [手順書](../playbook.md) を参照。

## 出典

| 情報源 | URL |
|---|---|
| prototype/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| prototype/LOGIC.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/LOGIC.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| prototype/UI.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype/UI.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/prototype.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/prototype.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [wayfinder](wayfinder.md) / [diagnosing-bugs](diagnosing-bugs.md) / [to-spec](to-spec.md)
