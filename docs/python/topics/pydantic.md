# Pydantic — Zod にあたる、型ヒントから作る検証

> 出典（一次情報）:
> - [Pydantic — Concepts (docs.pydantic.dev)](https://docs.pydantic.dev/latest/concepts/models/) — Models / Fields / Validators / Unions / JSON Schema / Serialization / Alias / Strict Mode / Performance
> - [Pydantic — Configuration API (docs.pydantic.dev)](https://docs.pydantic.dev/latest/api/config/) — `extra`・`regex_engine`・`validate_by_name`・`serialize_by_alias`
> - [Settings Management (docs.pydantic.dev)](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — `pydantic-settings` の `BaseSettings`
> - [Zod — Defining schemas / JSON Schema (zod.dev)](https://zod.dev/api) — 対応表の Zod 側
>
> 最終更新: 2026-11-08（pydantic 2.14.3・pydantic-core 2.50.4・pydantic-settings 2.16.2・Python 3.15.2・uv 0.13.7 で検証）

Pydantic は、**型ヒントを書いたクラスを、そのまま実行時の検証スキーマにする**ライブラリである。Zod は「スキーマから型を取り出す」（`z.infer`）が、Pydantic は「型を書いたクラスがスキーマになる」。向きが逆なだけで、役割は同じである。
通し課題での使い方は [Step 04: 型](../steps/04-typing.md)（`Faq` をモデルにする）、mypy との組み合わせは [Step 05: 品質ツール](../steps/05-quality.md) の §3.6 を参照。Step 04 の短い対応表を、ここで全体に広げる。

---

## 1. TL;DR

- **`BaseModel` を継承したクラスが `z.object` と `z.infer` を兼ねる**。外から来た JSON は `Model.model_validate_json(s)` で、解析と検証を 1 回で行う（§3.1）。
- **`safeParse` にあたる、例外を投げない API は無い**。`ValidationError` を `try` / `except` で受ける。`BaseModel` と `TypeAdapter` の検証メソッドはすべて例外を投げる版だけだった（検証済み、§3.1）。
- **既定は lax モードで、`"3"` を `3` に変換する**。Zod では `z.coerce` と書いたときだけの変換が、何も書かなくても効く。止めるなら `strict=True`。未知のキーは既定で捨てる（`extra="ignore"`。`"forbid"` が `z.strictObject`、`"allow"` が `z.looseObject`。§3.3）。
- camelCase の JSON は `alias_generator=to_camel` で受ける。**書き出しは既定で Python 側の名前（snake_case）に戻る**ので、`by_alias=True` を付ける（§3.4・§6）。
- 環境変数と `.env` は `pydantic-settings` の `BaseSettings` で読む（zod + dotenv にあたる、§3.5）。

---

## 2. Node.js / Bun との対応

| Zod（v4） | Pydantic（v2） | 補足 |
|---|---|---|
| `z.object({...})` | `class M(BaseModel): ...` | |
| `z.infer<typeof M>` | 不要（クラスがそのまま型） | |
| `M.parse(data)` | `M.model_validate(data)` | `M(**data)` でも検証は走るが、型チェッカーとの相性は `model_validate` が良い（[型チェッカーの比較](type-checkers.md) §4.1） |
| `M.parse(JSON.parse(s))` | `M.model_validate_json(s)` | 解析と検証を Rust 側でまとめて行う |
| `M.safeParse(data)` | 無い。`try` / `except ValidationError` | `e.errors()` が `loc`・`type`・`msg` の dict の list を返す |
| `.optional()` / `.nullable()` | `x: str \| None = None` | `= None` を書かないと、`None` を許しても必須のまま（キーが無いと `missing`） |
| `.default([])` | `Field(default_factory=list)` | |
| `z.enum([...])` / `z.nativeEnum(E)` | `Literal["a", "b"]` / `enum.Enum` | `Enum` は検証後に `Status.OPEN` のような列挙子になる |
| `.min()` / `.max()` / `.regex()` | `Field(min_length=, max_length=, pattern=)` | 数値は `ge` / `le` / `gt` / `lt`。`pattern` の正規表現は既定で Rust の regex crate（§6） |
| `z.email()` | `EmailStr` | `pydantic[email]`（email-validator）が要る（§6） |
| `.refine()` | `@field_validator("x")` | `ValueError` を投げると検証エラーになる |
| `.superRefine()`（フィールドをまたぐ） | `@model_validator(mode="after")` | |
| `.transform()` / `z.preprocess()` | `AfterValidator` / `BeforeValidator`（`Annotated` に付ける） | `field_validator(mode="before")` でも書ける |
| `z.coerce.number()` | 既定の lax モード | `ConfigDict(strict=True)` か `Field(strict=True)` で止める |
| `z.strictObject` / `z.looseObject` | `extra="forbid"` / `extra="allow"` | Zod 3 の `.strict()` / `.passthrough()` にあたる |
| `z.discriminatedUnion("kind", [...])` | `A \| B = Field(discriminator="kind")` | |
| `z.array(Item)` を単独で検証 | `TypeAdapter(list[Item])` | モデルでない型（list・dict・`TypedDict`）の検証の入口 |
| `z.toJSONSchema()`（旧 zod-to-json-schema） | `M.model_json_schema()` | |
| （出力用の整形） | `model_dump()` / `model_dump_json()` | `by_alias`・`exclude`・`mode="json"` |
| dotenv + `z.object` で `process.env` を検証 | `pydantic-settings` の `BaseSettings` | python-dotenv は依存として一緒に入る |

---

## 3. 早見表

### 3.1 モデル・検証・`safeParse` の代わり

制約と既定値を書き、`safeParse` のように結果を返す関数を自分で包む（抜粋・単体では動かない。全体は `ex/basics.py`。出力の 1 行目は `model_validate`、2 行目は `model_validate_json` で読んだ `id`、3 行目は `safe_parse` の結果）。

```python
class Faq(BaseModel):
    id: str = Field(pattern=r"^faq-\d{2}$")
    category: Literal["経費", "勤怠", "IT"]
    question: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)  # .default([]) にあたる
    owner: str | None = None  # .nullable().optional() にあたる


def safe_parse(data: object) -> Faq | list[str]:
    """Zod の safeParse にあたる関数は無いので、自分で包む。"""
    try:
        return Faq.model_validate(data)
    except ValidationError as e:
        return [f"{'.'.join(map(str, err['loc']))}: {err['type']}" for err in e.errors()]
```

`ex/basics.py` を動かす（検証済み）。

実行結果:

```text
$ uv run python ex/basics.py
id='faq-01' category='IT' question='VPN は?' tags=[] owner=None
faq-02
['id: string_pattern_mismatch', 'category: literal_error', 'question: string_too_short']
```

誤りは最初の 1 つで止まらず、全フィールド分がまとめて返る（Zod の `issues` と同じ）。テストでは安定した名前の `err["type"]` を比べる（[Step 06](../steps/06-testing.md)）。

### 3.2 バリデータと変換

`.transform()` と `.refine()` にあたる部分（抜粋・単体では動かない。全体は `ex/validators.py`）。

```python
Trimmed = Annotated[str, BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v)]
Upper = Annotated[str, AfterValidator(str.upper)]  # 検証の後で値を加工する


class Range(BaseModel):
    label: Trimmed  # 型を検証する前に空白を落とす
    code: Upper
    start: int
    end: int

    @model_validator(mode="after")  # フィールドをまたぐ検査
    def check_order(self) -> Self:
        if self.start > self.end:
            raise ValueError("start must be <= end")
        return self
```

`Range(label="  Q1  ", code="abc", start=1, end=3)` は `label='Q1' code='ABC'` になり、`start` が `end` より大きい dict は `Value error, start must be <= end [type=value_error, ...]` で弾かれた（検証済み）。
`BeforeValidator` は生の入力（`str` とは限らない）を受けるので、`isinstance` で確かめてから触る。1 つのフィールドだけの `.refine()` は `@field_validator("label")` と `@classmethod` で書く。

### 3.3 lax / strict・未知のキー・判別共用体

`count: int` と `active: bool` のモデルに `{"count": "3", "active": "yes"}` を渡し、既定・`strict=True`・`extra` の設定で比べた `ex/modes.py`（検証済み）。

実行結果:

```text
$ uv run python ex/modes.py
lax: count=3 active=True
strict: ['int_type', 'bool_type']
strict json: count=3 active=True
ignore: count=1 active=False
forbid: extra_forbidden
allow: name='a' x=1 {'x': 1}
```

公式 docs は strict を "no data conversion is performed" と説明する。`extra="allow"` のキーは `model_extra` に入る。

`kind: Literal["text"]` の `Text` と `kind: Literal["link"]` の `Link` を `block: Text | Link = Field(discriminator="kind")` で判別し、続けて `TypeAdapter(list[Text]).validate_json(...)`、`Post.model_json_schema()` の `block` の部分、存在しないタグ `"video"` の順に試した `ex/unions.py`（検証済み）。

実行結果:

```text
$ uv run python ex/unions.py
Link
[Text(kind='text', body='a')]
{"discriminator": {"mapping": {"link": "#/$defs/Link", "text": "#/$defs/Text"}, "propertyName": "kind"}, "oneOf": [{"$ref": "#/$defs/Text"}, {"$ref": "#/$defs/Link"}], "title": "Block"}
…（中略: 15 行）…
  Input tag 'video' found using 'kind' does not match any of the expected tags: 'text', 'link' [type=union_tag_invalid, input_value={'kind': 'video'}, input_type=dict]
```

### 3.4 書き出しと別名（camelCase の JSON）

JSON は camelCase、Python は snake_case で扱う（抜粋・単体では動かない。全体は `ex/alias.py`）。

```python
class User(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)

    user_id: int
    display_name: str
    signup_date: date
    password_hash: str = Field(exclude=True)  # 書き出しに含めない
```

`{"userId": 1, "displayName": "Ann", "signupDate": "2026-11-08", "passwordHash": "x"}` を `model_validate_json` で読み、`model_dump()`・`model_dump(mode="json", by_alias=True)`・`model_dump_json(by_alias=True, exclude={"signup_date"})` の順に書き出した（検証済み）。

実行結果:

```text
$ uv run python ex/alias.py
user_id=1 display_name='Ann' signup_date=datetime.date(2026, 11, 8) password_hash='x'
{'user_id': 1, 'display_name': 'Ann', 'signup_date': datetime.date(2026, 11, 8)}
{'userId': 1, 'displayName': 'Ann', 'signupDate': '2026-11-08'}
{"userId":1,"displayName":"Ann"}
…（中略: 1 行）…
[('displayName',), ('signupDate',), ('passwordHash',)]
```

最後の行は `{"user_id": 3}` を渡したときのエラーの `loc` で、別名で出るので API の利用者にそのまま返せる。

### 3.5 pydantic-settings（環境変数と `.env`）

`.env` を置き、環境変数で一部を上書きする。`Db` は `host: str = "localhost"` と `port: int = 5432` を持つ `BaseModel` で、最後に `Settings()` を作り、`print(s)` と、`api_key` の先頭 3 文字・`db.port + 1` を表示する（抜粋・単体では動かない。全体は `settings_demo/settings.py`）。

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FAQ_", env_nested_delimiter="__", env_file=".env"
    )

    debug: bool = False
    api_key: SecretStr
    db: Db = Db()
```

`.env` は `FAQ_API_KEY=from-dotenv-123`・`FAQ_DEBUG=true`・`FAQ_DB__HOST=db.local` の 3 行（検証済み）。

実行結果:

```text
$ FAQ_DB__PORT=6543 FAQ_DEBUG=false uv run python settings.py
debug=False api_key=SecretStr('**********') db=Db(host='db.local', port=6543)
fro... 6544
```

- `env_prefix` は `.env` の中の名前にも効く。入れ子は `env_nested_delimiter="__"` で `FAQ_DB__HOST` と書く
- 優先順位は公式 docs で、高い順に CLI 引数（`cli_parse_args` のとき）→ `Settings(...)` の引数 → 環境変数 → `.env` → secrets ディレクトリ → 既定値。上でも `FAQ_DEBUG=false` が `.env` に勝った
- `SecretStr` は `print` やログで `**********` になる。中身は `get_secret_value()` で取り出す

---

## 4. 推奨の使い方（2026-11）

| 推奨 | 理由 |
|---|---|
| JSON の文字列は `model_validate_json` / `validate_json` に渡す | Performance のページの最初の項目が "use `model_validate_json()` not `model_validate(json.loads(...))`"。1,000 件の list で 0.062 秒と 0.086 秒だった（参考値） |
| `TypeAdapter` はモジュールの先頭などで 1 回だけ作り、使い回す | 公式 docs: "Each time a TypeAdapter is instantiated, it will construct a new validator and serializer." 小さい入力では、毎回作ると 0.001 秒が 0.039 秒になった（参考値） |
| 共用体には判別用のフィールドを置き、`discriminator` を指定する | Performance のページ: "Use tagged union, not union"。エラーも「どのタグが不正か」の 1 件になる（§3.3） |
| mypy を使うなら `plugins = ["pydantic.mypy"]`、dict からは `M.model_validate(d)` で作る | プラグインが無いと `frozen=True` への代入などを見逃す。`init_typed` では `M(**d)` が型の誤りになる（[Step 05](../steps/05-quality.md) §3.6、[型チェッカーの比較](type-checkers.md) §4.1） |

---

## 5. 選び方・代替との比較

| 道具 | 一次情報の説明 | 向いている場面 |
|---|---|---|
| 標準の `dataclasses` | Python docs: "nothing in `@dataclass` examines the type specified in the variable annotation."（2 つの例外を除く） | 検証の要らない内部のデータ。依存を増やさない |
| `pydantic.dataclasses` | Pydantic docs: "Pydantic dataclasses are not a replacement for Pydantic models." | 既存の dataclass に検証だけを足したい |
| attrs（26.1.0） | README: "*without* writing dull boilerplate code again and again and *without* runtime performance penalties." `dataclasses` は attrs の子孫とも書かれている | 標準の `dataclasses` より多くの設定が要る内部のクラス（機能の一覧は attrs の docs） |
| msgspec（0.22.0） | README: "a *fast* serialization and validation library"。"Zero-cost schema validation using familiar Python type annotations." | 速さが最優先の JSON / MessagePack の入出力 |
| Pydantic（2.14.3） | 本ページ | 外部の入力の検証。FastAPI（公式: "Pydantic for the data parts."、[Step 09](../README.md#4-学習ロードマップ)）・pydantic-settings・JSON Schema と組み合わせる |

---

## 6. つまずきポイント

| 症状 | 原因 | 対処 |
|---|---|---|
| 実験用に `email.py` を作ると、`from pydantic import EmailStr` が `ImportError: cannot import name 'EmailStr' from 'pydantic'` で落ちる（検証中に発生） | スクリプトのあるディレクトリが `sys.path` の先頭に入り、標準ライブラリの `email` より自分の `email.py` が先に見つかる。Pydantic が中で `importlib.metadata` を読み、それが `import email` する | 標準ライブラリと同じ名前のファイルを作らない（[import の仕組み](imports.md)） |
| `EmailStr` を使ったモデルの定義で `ImportError: email-validator is not installed, run \`pip install 'pydantic[email]'\``（検証で再現） | email-validator は任意の依存である（公式 docs: "you need to install the optional email-validator package"） | `uv add "pydantic[email]"`。email-validator 2.3.0・dnspython・idna が入った |
| alias を付けたモデルに `Plain(user_id=1)` と Python 側の名前で渡すと `missing ('userId',)`（検証で再現） | 公式 docs: `validate_by_alias` は "True by default"、`validate_by_name` は "False by default" | `ConfigDict(validate_by_name=True)`（§3.4） |
| camelCase で受けたのに、`model_dump()` が snake_case で返る（検証で再現） | 別名での書き出しは既定で無効（"serialization by alias, which is disabled by default"） | 呼ぶたびに `by_alias=True` を付けるか、`ConfigDict(serialize_by_alias=True)` |
| 別のディレクトリから起動すると `.env` の値が読まれず `api_key Field required`（検証で再現） | `env_file=".env"` は起動したときのカレントディレクトリから探す | 起動するディレクトリを決めるか、`Path(__file__)` から絶対パスを組み立てて渡す |
| `pattern` に先読み・後読みを書くと、クラス定義の時点で `SchemaError` | 既定の `regex_engine` は `'rust-regex'`。公式 docs: "non-backtracking and therefore more DDoS resistant, but does not support all regex features." | 書き方を変えるか `ConfigDict(regex_engine="python-re")`（先読みを含む `pattern` が通ることを確かめた。詳細は [Step 04](../steps/04-typing.md) §5） |
| `"3"` や `"yes"` が黙って `3` や `True` になる | 既定の lax モード（§3.3） | 型の厳密さが要るモデル・フィールドに `strict=True` |

---

## 出典

| 情報源 | URL（確認日） |
|---|---|
| Pydantic — Models / Fields / Validators / Unions / JSON Schema / Serialization | https://docs.pydantic.dev/latest/concepts/models/ ・ https://docs.pydantic.dev/latest/concepts/fields/ ・ https://docs.pydantic.dev/latest/concepts/validators/ ・ https://docs.pydantic.dev/latest/concepts/unions/ ・ https://docs.pydantic.dev/latest/concepts/json_schema/ ・ https://docs.pydantic.dev/latest/concepts/serialization/ （2026-11-08 確認、Context7 `/pydantic/pydantic/v2.14.1` 経由） |
| Pydantic — Alias / Strict Mode / Performance / Dataclasses | https://docs.pydantic.dev/latest/concepts/alias/ ・ https://docs.pydantic.dev/latest/concepts/strict_mode/ ・ https://docs.pydantic.dev/latest/concepts/performance/ ・ https://docs.pydantic.dev/latest/concepts/dataclasses/ （2026-11-08 確認。引用はページの実物から） |
| Pydantic — Configuration API / Network Types | https://docs.pydantic.dev/latest/api/config/ ・ https://docs.pydantic.dev/latest/api/networks/ （2026-11-08 確認。`regex_engine`・`EmailStr`） |
| FastAPI | https://fastapi.tiangolo.com/ （2026-11-08 確認。依存の説明） |
| Settings Management（pydantic-settings） | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ （2026-11-08 確認、Context7 `/pydantic/pydantic-settings` 経由。優先順位・`env_prefix`・`env_nested_delimiter`） |
| Zod — Defining schemas / JSON Schema | https://zod.dev/api ・ https://zod.dev/json-schema （2026-11-08 確認、Context7 `/colinhacks/zod/v4.6.7` 経由。`z.strictObject`・`z.looseObject`・`z.toJSONSchema()`） |
| dataclasses（Python docs） | https://docs.python.org/3/library/dataclasses.html （2026-11-08 確認） |
| attrs / msgspec の README | https://github.com/python-attrs/attrs ・ https://github.com/jcrist/msgspec （2026-11-08 確認） |

### 確認できなかった事項

- **公開 API としての、例外を投げない検証**。`BaseModel`・`TypeAdapter` の検証メソッドはすべて例外を投げる。pydantic-core の `SchemaValidator` には `isinstance_python` があるが、内部寄りの API で公式の案内は見つからなかったので、本文では扱わない

- 関連: [Python 学習ガイド](../README.md) / [Step 04: 型](../steps/04-typing.md) / [Step 05: 品質ツール](../steps/05-quality.md) / [Step 06: テスト](../steps/06-testing.md) / [型チェッカーの比較](type-checkers.md) / [import の仕組み](imports.md)
