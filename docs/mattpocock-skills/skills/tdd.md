# tdd — 合意した seam で red → green を 1 つずつ回す、テスト駆動開発の参照 skill

> 出典（一次情報）:
> - [tdd/SKILL.md (github.com/mattpocock/skills)](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/SKILL.md) — skill 本体
> - [tdd/tests.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/tests.md) — 良いテストと悪いテストの例
> - [tdd/mocking.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/mocking.md) — mock を使う場所
> - [docs/engineering/tdd.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/tdd.md) — 同じ作者による解説ページ（二次的に参照）
>
> 最終更新: 2026-11-15（mattpocock-skills v1.3.1、commit 49dd158 で確認）

## 1. TL;DR

- TDD を red → green のループとして扱い、残す価値のあるテストを書くための参照である（`SKILL.md:8`）
- テストは公開インターフェース越しに振る舞いを確かめる。実装の詳細は見ない（`SKILL.md:14`）
- テストを書く前に seam を書き出し、ユーザーに確認する。確認していない seam にはテストを書かない（`SKILL.md:22`）
- 1 サイクルは 1 seam・1 テスト・最小の実装。リファクタリングはループに含めず、[code-review](code-review.md) の段階に回す（`SKILL.md:36-38`）
- mock はシステム境界（外部 API、時刻、乱数など）だけで使う（`mocking.md:3-14`）

## 2. 基本情報

| 項目 | 内容 |
|---|---|
| カテゴリ | engineering |
| 起動 | ユーザーとモデルの両方（`disable-model-invocation` の指定なし） |
| 呼び出し方 | `/mattpocock-skills:tdd`。test-first で作りたい、"red-green-refactor" と言った、integration test を求めた場合にモデルも使う（`SKILL.md:3`） |
| 内部で呼ぶ skill | `codebase-design`（インターフェースの形自体が問題のときだけ、語彙の参照として。`SKILL.md:26`） |
| 外部への書き込み | なし（テストと実装は repo 内に書く） |

## 3. いつ使うか・使わないか

解説ページ（docs/engineering/tdd.md）の整理は次のとおりである。

| 状況 | 使う skill |
|---|---|
| 入力と出力が決まった振る舞い（業務ロジック、リクエスト/レスポンス契約、変換、検証） | `tdd` |
| 振る舞いがまだ決まっていない | [to-spec](to-spec.md)（seam も先に合意する） |
| 問題がテストではなくインターフェースの形 | [codebase-design](codebase-design.md) |
| spec や ticket があり、実装全体を任せたい | [implement](implement.md)（ticket ごとに `tdd` を呼ぶ） |
| 設定、配線、型注釈、単純な CRUD | 合うものが無い（解説ページは未解決の課題として挙げている） |

- 解説ページによると、`tdd` は「進め方の参照」であり、ループを回すのは利用者か [implement](implement.md) である

## 4. 流れ

1. **用語を合わせる**: コードベースを調べるときは `GLOSSARY.md` があれば読み、テスト名とインターフェースの語彙をドメインの言葉に合わせる。触る領域の ADR に従う（`SKILL.md:10`）
2. **seam を合意する**: 「公開インターフェースは何か、どの seam をテストするか」を尋ねる。提案する各 seam に、何を捕まえ何を見逃すかを 1 行で添える（`SKILL.md:22-24`）
   - インターフェースの形そのもの（モジュールの深さ、seam の位置、公開範囲）が問題なら、Skill tool で `"codebase-design"` を呼んで語彙を参照する。セッションとして回すものではない（`SKILL.md:26`）
3. **red**: 失敗するテストを先に書く（`SKILL.md:36`）
4. **green**: そのテストを通すだけの実装を書く。先のテストを見越した実装や推測の機能は足さない（`SKILL.md:36`）
5. **繰り返す**: 1 seam・1 テスト・最小の実装を 1 サイクルとし、縦切り（vertical slice）で進める。各テストは前のサイクルで分かったことに応じる tracer bullet である（`SKILL.md:32`, `SKILL.md:37`）
6. **リファクタリングはしない**: ループの外であり、`code-review` の段階で行う（`SKILL.md:38`）

### 良いテストと避けるパターン

良いテスト（`tests.md:5-23`）: 公開 API だけを使い、利用者や呼び出し側が気にする振る舞いを確かめる。内部のリファクタリングで壊れない。HOW ではなく WHAT を書く。1 テスト 1 つの論理的な assertion。

避けるパターン（`SKILL.md:30-32`）:

| パターン | 内容 |
|---|---|
| 実装結合（Implementation-coupled） | 内部の協調オブジェクトを mock する、private メソッドをテストする、DB を直接引くなど脇道で確かめる。振る舞いは同じなのにリファクタリングで壊れる |
| 恒真（Tautological） | 期待値をコードと同じ計算で作る（`expect(add(a, b)).toBe(a + b)` など）。期待値は既知のリテラル、計算例、spec など独立した情報源から取る |
| 横切り（Horizontal slicing） | テストを全部書いてから実装を全部書く。想像上の振る舞いを確かめることになる |

mock の方針（`mocking.md:3-14`）: 外部 API、DB（テスト用 DB を優先）、時刻・乱数、ファイルシステム（場合による）などのシステム境界だけ mock する。自分のクラスやモジュール、内部の協調オブジェクトは mock しない。境界では依存性注入と、汎用 fetcher ではなく操作ごとの SDK 風インターフェースを使う（`mocking.md:20-53`）。

## 5. 書き込むもの・副作用

- git の commit・branch・push、GitHub、tracker への書き込みは無い（SKILL.md に記述なし）
- ループの中で、テストと実装のコードを repo に書く（`SKILL.md:36`）
- 解説ページも「stateless で、自分のファイルは書かない」としている

## 6. 前後の skill

`tdd` は単独の段ではなく、主な流れの build 段の中で動く（解説ページ）。

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

- seam を先に合意する: [to-spec](to-spec.md)
- `tdd` を呼ぶ: [implement](implement.md)（ticket ごと）、[implement-spec](implement-spec.md)（各 implementer サブエージェント）
- 後: [code-review](code-review.md)（合意した seam だけが使われたかを確かめ、リファクタリングも受け持つ）
- 語彙の参照元: [codebase-design](codebase-design.md)

## 7. 注意点

- **description と本文のずれ**: description は "red-green-refactor" で起動すると書く（`SKILL.md:3`）が、本文はリファクタリングをループから外している（`SKILL.md:38`）。解説ページによると意図的な削除で、ずれは issue として残っている
- **seam の選び方が分からない**: 解説ページによると最も多い報告である。答える前に、各 seam が何を捕まえ何を見逃すか、どれだけ遅いかをエージェントに尋ねる
- **ブラウザテストや E2E を先に書かない**: red → green のループが遅くなりすぎる。skill は止めないので、repo の `CLAUDE.md` に書いておく（解説ページ）
- **他の ticket を知らない**: 1 ticket に対して動かすと、隣の ticket の作業を提案することがある。spec も一緒に渡すと良い（解説ページ）
- **前提**: 解説ページによると [codebase-design](codebase-design.md) が入っている必要がある（この plugin には同梱されている）
- 権限の扱いは [手順書](../playbook.md) を参照

## 出典

| 情報源 | URL |
|---|---|
| tdd/SKILL.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/SKILL.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| tdd/tests.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/tests.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| tdd/mocking.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/mocking.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |
| docs/engineering/tdd.md | https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/tdd.md （2026-11-15 確認、plugin キャッシュの v1.3.1 で照合） |

- 関連: [mattpocock-skills ガイド](../README.md) / [手順書](../playbook.md) / [implement](implement.md) / [implement-spec](implement-spec.md) / [code-review](code-review.md) / [codebase-design](codebase-design.md)
