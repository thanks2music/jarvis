"""「Claude で書いたコードを、なぜ Claude にレビューさせるのか」の図を生成する。

上段は PR を出してからマージまでの流れ、下段は書いた Claude とレビューする Claude が持っている情報の比較。
前提: diagram-maker plugin の diagramlib（リポジトリの外）。場所は環境変数 DIAGRAM_MAKER_LIB で指定できる。
正本は生成済みの why-ai-review-context.drawio と ../images/why-ai-review/context.png で、図を使うだけならこのスクリプトは要らない。
使い方: python3 why-ai-review-context.py why-ai-review-context.drawio
"""
import os
import sys

sys.path.insert(0, os.environ.get("DIAGRAM_MAKER_LIB", os.path.expanduser(
    "~/.claude/plugins/avengers/plugins/diagram-maker/skills/diagram-builder/lib")))
from diagramlib import Diagram, text_width  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "why-ai-review-context.drawio"

# -- データ ---------------------------------------------------------------
TITLE = "同じ Claude でも、書く側とレビューする側では渡される情報が違う"
FLOW_HEAD = "PR を出してからマージまで"
FLOW = [  # (ラベル, 強調するか)
    ("① ローカルで\nClaude と開発", False),
    ("② push して\nPR を作る", False),
    ("③ GitHub Actions\nが起動", False),
    ("④ claude[bot] が\nPR にコメント", True),
    ("⑤ 開発者が確かめて\n対応する", False),
    ("⑥ 人がマージを\n判断する", False),
]
CMP_HEAD = "2 つの Claude が持っている情報（①と④の比較）"
LEFT = "書いた Claude（ローカルのセッション）"
RIGHT = "レビューする Claude（CI の claude[bot]）"
# (観点, 書いた Claude, レビューする Claude, レビューする側の役割色)。
# ../why-ai-review-ai-code.md §2 の表の要約。表を変えたらここも直して再生成する。
# 見えていない情報の行だけ danger にする
ROWS = [
    ("受けた指示", "「この機能を作って」", "「この PR をレビューして」（workflow の prompt）", "primary"),
    ("会話と経緯", "依頼・試行錯誤・自分で決めた前提", "見えない（書いた理由を知らない）", "danger"),
    ("読むコード", "作業中のファイル", "push された PR の差分とリポジトリのファイル", "primary"),
    ("リポジトリのルール", "CLAUDE.md と個人・ローカル専用の設定", "コミットされた CLAUDE.md だけ", "primary"),
    ("結果の行き先", "自分の会話の中", "PR のコメント（チームが読める）", "primary"),
]
FOOTER = "同じモデルでも、渡される情報と役割が違うので、書いた本人とは別のレビュアーとして働く"

# -- 寸法 -----------------------------------------------------------------
d = Diagram("Why AI review", theme="cloud-modern")
T = d.t
FS = T["font_node"]
X0 = 40
CHEV_W = max(text_width(label, FS) for label, _ in FLOW) + 40   # 山形の先端と左右の余白
CHEV_H, CHEV_GAP = 56, 6
FLOW_W = len(FLOW) * CHEV_W + (len(FLOW) - 1) * CHEV_GAP

PAD, HEAD, ROW_H, PITCH = 16, 40, 44, 56
KEY_W = max(text_width(k, FS) for k, *_ in ROWS) + 24
ITEM_W = max(text_width(v, FS) for _, a, b, _ in ROWS for v in (a, b)) + 32
COL_W = ITEM_W + PAD * 2
GUTTER = 24
CMP_W = KEY_W + COL_W * 2 + GUTTER

d.width = int(max(FLOW_W, CMP_W, text_width(TITLE, T["font_title"]), text_width(FOOTER, FS + 1)) + X0 * 2)
TITLE_Y = 24
FLOW_HEAD_Y = 76
FLOW_Y = FLOW_HEAD_Y + 30
CMP_HEAD_Y = FLOW_Y + CHEV_H + 44
CMP_Y = CMP_HEAD_Y + 30
BODY_H = PAD * 2 + (len(ROWS) - 1) * PITCH + ROW_H
FOOTER_Y, FOOTER_H = CMP_Y + HEAD + BODY_H + 24, 28
d.height = FOOTER_Y + FOOTER_H + 32

# -- 描く -----------------------------------------------------------------
d.text("title", TITLE, X0, TITLE_Y, d.width - X0 * 2, 32, size=T["font_title"], bold=True)

fx = X0 + (d.width - X0 * 2 - FLOW_W) / 2
d.text("flow-head", FLOW_HEAD, fx, FLOW_HEAD_Y, FLOW_W, 22, size=T["font_zone"], bold=True, color=T["muted"])
for i, (label, strong) in enumerate(FLOW):
    d.node(f"f{i}", label, d.chevron_style(role="primary" if strong else None),
           fx + i * (CHEV_W + CHEV_GAP), FLOW_Y, CHEV_W, CHEV_H)

cx = X0 + (d.width - X0 * 2 - CMP_W) / 2
d.text("cmp-head", CMP_HEAD, cx, CMP_HEAD_Y, CMP_W, 22, size=T["font_zone"], bold=True, color=T["muted"])
LX = cx + KEY_W
RX = LX + COL_W + GUTTER
for cid, title, x, role in (("left", LEFT, LX, None), ("right", RIGHT, RX, "primary")):
    d.node(cid + "-head", title, d.cell_style(header=True, role=role), x, CMP_Y, COL_W, HEAD)
    d.node(cid + "-body", "", d.cell_style(), x, CMP_Y + HEAD, COL_W, BODY_H)

for i, (key, mine, theirs, role) in enumerate(ROWS):
    y = CMP_Y + HEAD + PAD + i * PITCH
    d.text(f"k{i}", key, cx, y, KEY_W - 12, ROW_H, bold=True, align="right", color=T["muted"])
    d.node(f"a{i}", mine, d.box_style("neutral", align="left", spacingLeft=12), LX + PAD, y, ITEM_W, ROW_H)
    d.node(f"b{i}", theirs, d.box_style(role, align="left", spacingLeft=12), RX + PAD, y, ITEM_W, ROW_H)

d.text("footer", FOOTER, X0, FOOTER_Y, d.width - X0 * 2, FOOTER_H, size=FS + 1, bold=True, align="center")

print(d.save(OUT))
