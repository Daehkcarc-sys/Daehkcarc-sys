"""Compose text into SVG path data from scripts/glyphs.json. Standard library only.

    from glyphs import text_path
    d, width = text_path("Expedition Log", face="display", size=48, x=40, y=80)

Faces: "display" (Cormorant Garamond SemiBold), "displayBold", "italic"
(Cormorant Garamond Medium Italic), "caps" (Cinzel Medium).
"""
import json
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent / "glyphs.json"


@lru_cache(maxsize=1)
def _fonts():
    return json.loads(_PATH.read_text(encoding="utf-8"))


def _num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def text_width(text, face="display", size=32, tracking=0.0):
    """Advance width in px. `tracking` is extra space per letter, in em."""
    font = _fonts()[face]
    scale = size / font["unitsPerEm"]
    glyphs, kern = font["glyphs"], font["kern"]
    w = 0.0
    prev = None
    for ch in text:
        g = glyphs.get(ch) or glyphs["?"]
        if prev is not None:
            w += kern.get(prev + ch, 0) * scale + tracking * size
        w += g["w"] * scale
        prev = ch
    return w


def text_path(text, face="display", size=32, x=0.0, y=0.0, anchor="start", tracking=0.0):
    """Return (path_d, width). (x, y) is the baseline origin; anchor = start|middle|end."""
    font = _fonts()[face]
    scale = size / font["unitsPerEm"]
    glyphs, kern = font["glyphs"], font["kern"]
    width = text_width(text, face, size, tracking)
    pen_x = x - {"start": 0.0, "middle": width / 2, "end": width}[anchor]
    out = []
    prev = None
    for ch in text:
        g = glyphs.get(ch) or glyphs["?"]
        if prev is not None:
            pen_x += kern.get(prev + ch, 0) * scale + tracking * size
        for cmd in g["d"]:
            op, nums = cmd[0], cmd[1:]
            if op == "Z":
                out.append("Z")
                continue
            pts = []
            for i in range(0, len(nums), 2):
                pts.append(_num(pen_x + nums[i] * scale))
                pts.append(_num(y - nums[i + 1] * scale))
            out.append(op + " ".join(pts))
        pen_x += g["w"] * scale
        prev = ch
    return "".join(out), width


def cap_height(face="display", size=32):
    font = _fonts()[face]
    return font["capHeight"] * size / font["unitsPerEm"]


def fit_size(text, face, size, max_width, tracking=0.0, min_size=8):
    """Largest size <= `size` at which `text` fits in `max_width`."""
    w = text_width(text, face, size, tracking)
    if w <= max_width:
        return size
    return max(min_size, size * max_width / w)
