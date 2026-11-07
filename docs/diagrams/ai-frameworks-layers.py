"""AI フレームワーク学習ガイドのレイヤー図を生成する。

前提: diagram-maker plugin の diagramlib（リポジトリの外）。場所は環境変数 DIAGRAM_MAKER_LIB で指定できる。
使い方: python3 ai-frameworks-layers.py ai-frameworks-layers.drawio
"""
import os
import sys

# diagram-maker plugin の lib（DIAGRAM_MAKER_LIB で上書きできる）
sys.path.insert(0, os.environ.get("DIAGRAM_MAKER_LIB", os.path.expanduser(
    "~/.claude/plugins/avengers/plugins/diagram-maker/skills/diagram-builder/lib")))
from diagramlib import Diagram  # noqa: E402

# -- データ ---------------------------------------------------------------
LAYERS = [  # 上から順（④ → ①）
    ("l4", "④ エージェント /\nLLM アプリ", "primary",
     [["LangGraph", "Pydantic AI", "OpenAI Agents SDK"], ["Vercel AI SDK", "Mastra", "Claude Agent SDK"]]),
    ("l3", "③ 推論・配信", "warning", [["MLX-LM", "vLLM", "SGLang"]]),
    ("l2", "② モデルと学習", "success", [["Transformers", "TRL + PEFT"]]),
    ("l1", "① 深層学習の基盤", "neutral", [["PyTorch", "JAX", "Keras 3", "TensorFlow\n（保守中心）"]]),
]
HANDOFFS = {  # 下の層 → 上の層
    ("l1", "l2"): "モデルの重み（safetensors）",
    ("l2", "l3"): "重み・LoRA アダプタ",
    ("l3", "l4"): "OpenAI 互換 API（/v1/chat/completions）",
}

# -- 寸法 -----------------------------------------------------------------
X, W = 40, 700            # 層の枠
HEAD_W = 170              # 層の見出しの幅
CHIP_H, ROW_GAP = 44, 12
PAD = 18
GAP = 64                  # 層と層の間（矢印とラベル）
NOTE_X, NOTE_W = 770, 170

d = Diagram("AI frameworks layers", theme="cloud-modern", width=980, height=760)
d.text("title", "AI フレームワークの 4 つの層と受け渡し", X, 14, 600, 30, size=18, bold=True)

y = 64
geo = {}
for lid, title, role, rows in LAYERS:
    h = PAD * 2 + len(rows) * CHIP_H + (len(rows) - 1) * ROW_GAP
    d.node(lid, "", d.box_style("neutral", fillColor=d.t["surface"], arcSize=6), X, y, W, h)
    d.text(f"{lid}-t", title, X + 16, y, HEAD_W - 16, h, size=14, bold=True)
    inner_x, inner_w = X + HEAD_W, W - HEAD_W - PAD
    for r, row in enumerate(rows):
        cw = (inner_w - (len(row) - 1) * 12) / len(row)
        for c, name in enumerate(row):
            cid = f"{lid}-{r}-{c}"
            d.node(cid, name, d.box_style(role, fontStyle=1),
                   inner_x + c * (cw + 12), y + PAD + r * (CHIP_H + ROW_GAP), cw, CHIP_H)
    geo[lid] = (y, h)
    y += h + GAP

# 層の間の上向き矢印（下の層の上辺 → 上の層の下辺）
for (lo, hi), label in HANDOFFS.items():
    y_hi = geo[hi][0] + geo[hi][1]
    y_lo = geo[lo][0]
    ax = X + W / 2
    a, b = d.anchor(f"{lo}-{hi}-s", ax, y_lo), d.anchor(f"{lo}-{hi}-d", ax, y_hi)
    d.edge(f"e-{lo}-{hi}", a, b, "", d.edge_style(strokeWidth=2))
    d.text(f"e-{lo}-{hi}-t", label, ax + 14, y_hi + 8, 330, GAP - 16, size=12, color=d.t["muted"])

# 右側の注記
y4, h4 = geo["l4"]
d.node("n-tools", "層の中のつなぎ目:\nツール呼び出しと\nJSON Schema の取り決め",
       d.box_style("neutral", dashed=1, align="left", spacingLeft=10, fontSize=12), NOTE_X, y4, NOTE_W, 70)
y3, h3 = geo["l3"]
d.node("api", "Anthropic API", d.box_style("dark"), NOTE_X, y3 + (h3 - CHIP_H) / 2, NOTE_W, CHIP_H)
d.edge("e-claude", "l4-1-2", "api", "", d.edge_style(dashed=True, exitX=1, exitY=0.5, entryX=0.5, entryY=0),
       waypoints=[(NOTE_X + NOTE_W / 2, d.abs("l4-1-2")[1] + CHIP_H / 2)])
d.text("n-claude", "Claude Agent SDK は\n③ を通らず直接つなぐ", NOTE_X, y3 + (h3 + CHIP_H) / 2 + 4, NOTE_W, 40,
       size=11, color=d.t["muted"])

d.save(sys.argv[1] if len(sys.argv) > 1 else "ai-frameworks-layers.drawio")
