"""Python 学習ガイドの全体図（uv を中心にしたプロジェクトの構成）を生成する。

前提: diagram-maker plugin の diagramlib（リポジトリの外）。場所は環境変数 DIAGRAM_MAKER_LIB で指定できる。
正本は生成済みの python-toolchain.drawio と ../images/python/toolchain.png で、図を使うだけならこのスクリプトは要らない。
使い方: python3 python-toolchain.py python-toolchain.drawio
"""
import os
import sys

sys.path.insert(0, os.environ.get("DIAGRAM_MAKER_LIB", os.path.expanduser(
    "~/.claude/plugins/avengers/plugins/diagram-maker/skills/diagram-builder/lib")))
from diagramlib import Diagram  # noqa: E402

# -- データ ---------------------------------------------------------------
LEFT = [  # 開発者が書くもの: (id, 名前, 説明, Node での相当)
    ("pyproject", "pyproject.toml", "依存の宣言", "Node: package.json"),
    ("pyver", ".python-version", "Python の版の固定", "Node: .nvmrc"),
]
RIGHT = [  # uv が作るもの
    ("lock", "uv.lock", "解決した版の記録\nコミットする", "Node: package-lock.json"),
    ("venv", ".venv（仮想環境）", "本体へのリンク + site-packages\nコミットしない", "Node: node_modules"),
]
BOTTOM = [  # uv のコマンド
    ("run", "uv run", ".venv の中でコマンドを実行", "Node: npm exec / bun run"),
    ("uvx", "uvx", "プロジェクトと切り離した\n使い捨ての環境でツールを実行", "Node: npx / bunx"),
]

# -- 寸法 -----------------------------------------------------------------
ZONE_Y, ZONE_HEAD = 200, 40
ITEM_W, ITEM_H, NOTE_H, ITEM_GAP = 230, 62, 22, 20
LEFT_X, RIGHT_X = 40, 690
ZONE_W = ITEM_W + 32
UV_X, UV_W, UV_H = 400, 180, 72
PY_Y = 70
BOTTOM_Y = 520

d = Diagram("Python toolchain", theme="cloud-modern", width=1010, height=680)
d.text("title", "uv を中心にした Python プロジェクトの全体像", LEFT_X, 14, 700, 30, size=18, bold=True)


def item(cid, name, desc, note, x, y, role, w=ITEM_W, h=ITEM_H, note_side="below"):
    d.node(cid, f"<b>{name}</b><br><font style=\"font-size:11px\">{desc.replace(chr(10), '<br>')}</font>",
           d.box_style(role), x, y, w, h)
    if note_side == "left":
        d.text(f"{cid}-node", note, x - 212, y + (h - NOTE_H) / 2, 200, NOTE_H, size=12, color=d.t["muted"], align="right")
    else:
        d.text(f"{cid}-node", note, x, y + h + 2, w, NOTE_H, size=12, color=d.t["muted"], align="center")


def zone(cid, title, x, items, role):
    h = ZONE_HEAD + len(items) * (ITEM_H + NOTE_H + ITEM_GAP) + 4
    d.node(cid, "", d.box_style("neutral", fillColor=d.t["surface"], arcSize=6), x, ZONE_Y, ZONE_W, h)
    d.text(f"{cid}-t", title, x + 16, ZONE_Y + 8, ZONE_W - 32, 24, size=13, bold=True)
    for i, (iid, name, desc, note) in enumerate(items):
        item(iid, name, desc, note, x + 16, ZONE_Y + ZONE_HEAD + i * (ITEM_H + NOTE_H + ITEM_GAP), role)


zone("z-left", "開発者が書く（コミットする）", LEFT_X, LEFT, "neutral")
zone("z-right", "uv が作る", RIGHT_X, RIGHT, "success")

# 中央の uv（左右の 2 つの項目の中間の高さ）
uv_y = ZONE_Y + ZONE_HEAD + (2 * ITEM_H + NOTE_H + ITEM_GAP) / 2 - UV_H / 2
d.node("uv", "<b>uv</b>", d.box_style("primary", fontSize=20), UV_X, uv_y, UV_W, UV_H)

# 上の Python 本体
item("python", "Python 本体", "~/.local/share/uv/python", "Node: nvm が入れる node 本体", UV_X - 25, PY_Y, "success", w=UV_W + 50, note_side="left")

# 下の uv のコマンド
for i, (cid, name, desc, note) in enumerate(BOTTOM):
    item(cid, name, desc, note, UV_X - 140 + i * 290, BOTTOM_Y, "primary", w=ITEM_W + 20, h=64)

# -- 線 -------------------------------------------------------------------
e = d.edge_style
d.edge("e-pyproject", "pyproject", "uv", "読む", e(exitX=1, exitY=0.5, entryX=0, entryY=0.3))
d.edge("e-pyver", "pyver", "uv", "", e(exitX=1, exitY=0.5, entryX=0, entryY=0.7))
d.edge("e-lock", "uv", "lock", "解決して記録", e(exitX=1, exitY=0.3, entryX=0, entryY=0.5))
d.edge("e-venv", "uv", "venv", "lockfile\nどおりに入れる", e(exitX=1, exitY=0.7, entryX=0, entryY=0.5))
d.edge("e-python", "uv", "python", "uv python install", e(exitX=0.5, exitY=0, entryX=0.5, entryY=1))
d.edge("e-run", "uv", "run", "", e(exitX=0.3, exitY=1, entryX=0.5, entryY=0))
d.edge("e-uvx", "uv", "uvx", "", e(exitX=0.7, exitY=1, entryX=0.5, entryY=0))
# .venv → Python 本体（参照）: 右のゾーンの外側を回る
_, vy, _, vh = d.abs("venv")
_, py, _, ph = d.abs("python")
ch_x = RIGHT_X + ZONE_W + 24
d.edge("e-link", "venv", "python", "本体へのリンク",
       e(dashed=True, exitX=1, exitY=0.5, entryX=1, entryY=0.5),
       waypoints=[(ch_x, vy + vh / 2), (ch_x, py + ph / 2)], label_pos=0.6)

# -- 凡例 -----------------------------------------------------------------
LX, LY = LEFT_X, BOTTOM_Y + 4
a1, b1 = d.anchor("lg-a1", LX, LY + 10), d.anchor("lg-b1", LX + 40, LY + 10)
d.edge("lg-e1", a1, b1, "", e())
d.text("lg-t1", "uv の操作", LX + 48, LY, 120, 20, size=12, color=d.t["muted"])
a2, b2 = d.anchor("lg-a2", LX, LY + 36), d.anchor("lg-b2", LX + 40, LY + 36)
d.edge("lg-e2", a2, b2, "", e(dashed=True))
d.text("lg-t2", "参照（リンク）", LX + 48, LY + 26, 120, 20, size=12, color=d.t["muted"])

d.save(sys.argv[1] if len(sys.argv) > 1 else "python-toolchain.drawio")
