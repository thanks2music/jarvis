# Zed ショートカット・チートシート（BOSS カスタム版）

> **目的**: BOSS が自身の `keymap.json` に追加したカスタムショートカットを忘れないための学習用ドキュメント。
> **対象**: macOS。他 OS では `cmd` → `ctrl` に読み替える。
> **前提**: 網羅的な Zed の使い方は [Zed エディタ活用ガイド](zed.md) を参照する。本ドキュメントは「複数プロジェクト運用のショートカット」に特化した速習用チートシートである。
>
> **カスタム設定の実体**: `~/.config/zed/keymap.json`（symlink ではなく実体ファイル。リポジトリ管理外のためリンクは張らない）。
> **出典**: [Zed Docs — Key Bindings](https://zed.dev/docs/key-bindings) / [`default-macos.json`](https://github.com/zed-industries/zed/blob/main/assets/keymaps/default-macos.json)

---

## 1. 覚えるべきコアフロー（3 ステップ）

BOSS の主要ユースケース = **「別プロジェクトへ切り替えて、そのプロジェクト用の新規 Agent スレッドを開始する」**。以下 3 ステップで完結する。

```
① ⌘ + Shift + O    プロジェクト切替（Open Recent Project）
② ⌘ + Shift + ;    Threads Sidebar にフォーカス
③ ⌘ + Shift + N    そのプロジェクトに新規 Agent Thread 作成
```

**覚え方**: 「`Shift + O / ; / N`」の 3 連コンボ。**Shift 系列で統一**しているので指の動きが小さい。

---

## 2. カスタムショートカット一覧

BOSS の `keymap.json` に手動追加したショートカットの全量。デフォルト挙動を打ち消したり、指の癖に合わせた予備キーを追加している。

### 2.1 プロジェクト操作

| ショートカット | 動作 | 用途 |
|---|---|---|
| `⌘⇧O` | Open Recent Project | **メイン**。プロジェクト切替の主軸 |
| `⌘⌥O` | Open Recent Project | 誤タイプ救済 + Zed の `dev::ToggleInspector` エラー抑止 |
| `⌘⌥⇧O` | Open Recent Project（別ウィンドウ） | プロジェクトを新ウィンドウで開きたい時 |

### 2.2 パネル・フォーカス操作

| ショートカット | 動作 | 用途 |
|---|---|---|
| `⌘⇧A` | Agent Panel トグル | 右ドックの Agent Panel 開閉 |
| `⌘⇧;` | Threads Sidebar にフォーカス | `⌘⇧N` を発火可能な状態にする |
| `⌘⇧I` | Agent チャット入力にフォーカス | **ターミナル ⇄ チャット行き来**の主軸 |

### 2.3 新規作成系

| ショートカット | 動作 | 用途 |
|---|---|---|
| `⌘⇧N` | 新規 Agent Thread（選択中グループに） | `ThreadsSidebar` フォーカス時のみ発火 |
| `⌘⇧⌃N` | 新規ウィンドウ | Zed デフォルトの `⌘⇧N`（新規ウィンドウ）を移設したもの |

### 2.4 デフォルト無効化

| キー | 状態 |
|---|---|
| `⌘⇧N`（Workspace context） | `null`（デフォルトの新規ウィンドウを解除。`⌘⇧⌃N` に移設） |

---

## 3. Zed デフォルトで既に便利なショートカット（併用推奨）

カスタムしていないが、多プロジェクト運用で頻用するもの。

| ショートカット | 動作 | 備考 |
|---|---|---|
| `⌘⇧P` | Command Palette | **万能。ショートカットを忘れたらこれ** |
| `⌘O` | ファイル/フォルダを開く | OS ネイティブダイアログ |
| `⌘B` | 左ドック（Project Panel）トグル | ファイルツリー |
| `⌘R` | 右ドック（Agent Panel が入る）トグル | `⌘⌥B` と等価 |
| `⌘J` | 下ドック（Terminal）トグル | |
| `⌘P` | File Finder | プロジェクト内ファイル検索 |
| `⌘⇧F` | プロジェクト全体検索 | |
| `⌘⌥;` | Threads Sidebar フォーカス（デフォルト） | カスタム `⌘⇧;` と同等 |
| `⌘?`（= `⌘⇧/`） | Agent チャットにフォーカス（デフォルト） | カスタム `⌘⇧I` と同等 |
| `⌘K` → `⌘S` | keymap.json を開く（`zed::OpenKeymap`） | 設定を素早く編集したい時 |

---

## 4. 覚え方（記憶の補助）

### 4.1 「Shift + 一文字」で機能を分類

BOSS のカスタムキーは **`⌘⇧` プレフィックス** に統一している。一文字を意味と紐付けて覚える。

| キー | 意味 | 動作 |
|---|---|---|
| `⌘⇧O` | **O**pen recent | プロジェクト切替 |
| `⌘⇧;` | **セミコロン** = 隣（コード内でも意味の区切り） | Threads Sidebar にフォーカス（隣のパネルへ） |
| `⌘⇧N` | **N**ew thread | 新規 Agent Thread |
| `⌘⇧A` | **A**gent panel | Agent Panel トグル |
| `⌘⇧I` | **I**nput / **I**nteract | Agent チャット入力にフォーカス |

### 4.2 修飾キーの意味

| 修飾キー | 意味 |
|---|---|
| `⌘⇧` プレフィックス | 「主要動作」= プロジェクト切替まわり |
| `⌘⌥` 追加 | 「変形版」= 新ウィンドウで開く、など |
| `⌘⇧⌃` | 「予備退避先」= 元のデフォルトを移設したキー |

---

## 5. トラブルシュート

### 5.1 `⌘⇧N` を押しても新規 Agent Thread が作られない

**原因**: `Threads Sidebar` にフォーカスがない可能性が高い。`agents_sidebar::NewThreadInGroup` は **`ThreadsSidebar` context 限定**のアクションで、フォーカスが sidebar 外にある場合は発火しない。

**解決**: `⌘⇧;` を先に押して Threads Sidebar にフォーカスを合わせる。

### 5.2 `⌘⌥O` で `dev::ToggleInspector` エラーが出る

**原因**: Zed の debug 用アクションが誤発火している。

**解決**: すでに `⌘⌥O` を `projects::OpenRecent` に明示的に再割当済み（本 keymap にて）。もし再発したら keymap.json の当該 binding を確認する。

### 5.3 `⌘⇧N` で新規ウィンドウが開いてしまう

**原因**: `ThreadsSidebar` context にフォーカスがない状態で押した場合、Zed が fall-through して次にマッチする binding（Zed デフォルトの新規ウィンドウ）を探しにいく。

**対策**: keymap.json では `Workspace` context で `⌘⇧N: null` としてデフォルトを無効化済み。新規ウィンドウを開きたい時は `⌘⇧⌃N` を使う。

### 5.4 ショートカットが効かなくなった

1. `⌘⇧P` → `zed: reload keymap` を実行
2. それでも駄目なら keymap.json の構文エラーを疑う（`node -e "JSON.parse(require('fs').readFileSync('~/.config/zed/keymap.json','utf8').replace(/\\/\\/.*$/gm,'').replace(/,(\\s*[}\\]])/g,'$1'))"` 相当）
3. `⌘⇧P` → `zed: open default keymap` でデフォルトを参照して照合

---

## 6. さらに追加したくなった時

### 6.1 まず Command Palette でアクション名を調べる

`⌘⇧P` を開き、実行したい動作を英語で検索する。表示される項目の右端に **Action 名**（例: `agent::ToggleFocus`）と **現在のバインド**が出る。

### 6.2 keymap.json の書き方

```json
[
  {
    "context": "任意（省略時はグローバル）",
    "bindings": {
      "cmd-shift-キー": "action::Name",
      "cmd-shift-キー2": ["action::Name", { "オプション": true }],
      "cmd-shift-キー3": null
    }
  }
]
```

- 後方のエントリが前方より**優先される**
- `context` を指定するとその文脈でのみ発火する（例: `"ThreadsSidebar"`, `"Editor"`, `"Terminal"`, `"Workspace"`）
- `null` で既存のデフォルトを無効化できる

### 6.3 全アクション一覧の参照先

[Zed Docs — All Actions](https://zed.dev/docs/all-actions) にアクション名の完全なカタログがある。カテゴリ別に整理されているので、追加したい機能はまずここで探す。

---

## 7. まとめ（30 秒で復習）

```
プロジェクト切替:     ⌘⇧O
別ウィンドウで:       ⌘⌥⇧O
Threads Sidebar へ:  ⌘⇧;
新規 Agent Thread:   ⌘⇧N（Sidebar フォーカス必須）
Agent Panel トグル:  ⌘⇧A
Agent チャット入力:  ⌘⇧I
新規ウィンドウ:       ⌘⇧⌃N
何でも呼べる:         ⌘⇧P（Command Palette）
```

**迷ったら `⌘⇧P` → 動作を英語で検索する**。これが最強の逃げ道である。
