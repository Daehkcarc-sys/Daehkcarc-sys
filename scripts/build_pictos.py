"""Render assets/pictos.svg from skills.json: three ornamental columns. Standard library only."""
import json

from glyphs import fit_size
from theme import (CREAM, CRIMSON, GOLD, PANEL_DEFS, ROOT, body_text, body_width, grain, panel, svg_doc, tpath, write)

W = 800
PAD = 46
ITEM = 22  # live text, about 9.6px when the image is 350px wide
ROW = 36


def build():
    groups = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    n = len(groups)
    gap = 26
    col = (W - 2 * PAD - gap * (n - 1)) / n
    rows = max(len(g["items"]) for g in groups)
    top = 104
    H = int(top + 74 + rows * ROW + PAD - 14)
    fs = ITEM  # one size for every item, reduced only if the longest label needs it
    longest = max((item for g in groups for item in g["items"]), key=lambda t: body_width(t, ITEM))
    while body_width(longest, fs) * 1.05 > col - 20 and fs > 16:
        fs -= 1
    parts = [tpath("PICTOS  &  LUMINA", "caps", 19, PAD, 62, GOLD, tracking=0.16)]
    for i, g in enumerate(groups):
        x = PAD + i * (col + gap)
        # picto: a hairline lozenge holding a crimson one
        cx, cy = x + 17, top + 16
        parts.append(f'<path d="M{cx} {cy - 17}l17 17-17 17-17-17Z" fill="none" stroke="{GOLD}" stroke-width="1.2"/>')
        parts.append(f'<path d="M{cx} {cy - 8}l8 8-8 8-8-8Z" fill="{CRIMSON}"/>')
        size = fit_size(g["title"], "display", 34, col - 46)
        parts.append(tpath(g["title"], "display", size, x + 46, top + 27, CREAM))
        parts.append(f'<path d="M{x} {top + 50}h{col:.0f}" stroke="{GOLD}" stroke-opacity=".35"/>')
        for j, item in enumerate(g["items"]):
            y = top + 88 + j * ROW
            parts.append(f'<path d="M{x + 5} {y - 12}l4 4-4 4-4-4Z" fill="{GOLD}"/>')
            text, _ = body_text([item], x + 20, y, fs, CREAM, opacity=0.9)
            parts.append(text)
    ground, border = panel(W, H)
    desc = " ".join(f'{g["title"]}: {", ".join(g["items"])}.' for g in groups)
    return svg_doc(W, H, ground + "".join(parts) + border, PANEL_DEFS + grain(), title="Skills: " + ", ".join(g["title"] for g in groups), desc=desc)


if __name__ == "__main__":
    write("pictos.svg", build())
