"""Render assets/card-N.svg from projects.json. Standard library only.

Each project: repo, title, description, note (optional), tags, language, stars.
`language` and `stars` are refreshed by scripts/refresh_projects.py in the daily workflow
(set "language_pin": true to keep the language you wrote).
"""
import json

from glyphs import fit_size, text_width
from theme import (ASSETS, CREAM, CRIMSON, GOLD, PANEL_DEFS, ROOT, body_text, grain, panel, roman, svg_doc, tpath,
                   wrap, write)

W = 800
PAD = 46
BODY, NOTE = 25, 22  # live text sizes: about 11px and 9.6px when the card is 350px wide
STAR = "M0-7.4L1.9-2.4 7.2-2.2 3-1 1.2 4.5 6.2 0 3.1-4.5 6.2-3-1.2-7.2-2.2-1.9-2.4Z"


def tag_row(tags, x, y, max_x):
    """Caps labels in hairline lozenges, wrapped to the card width. Returns (svg, bottom y)."""
    size, track, hpad, height, gap = 18, 0.1, 15, 34, 10
    out, cx, cy = [], x, y
    for tag in tags:
        tw = text_width(tag.upper(), "caps", size, track)
        w = tw + 2 * hpad
        if cx + w > max_x and cx > x:
            cx, cy = x, cy + height + gap
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{height}" rx="{height / 2}" fill="none" stroke="{GOLD}" stroke-opacity=".55"/>')
        out.append(tpath(tag.upper(), "caps", size, cx + hpad, cy + height / 2 + 6.3, GOLD, tracking=track))
        cx += w + gap
    return "".join(out), cy + height


def card(project, index):
    inner = W - 2 * PAD
    numeral = roman(index)
    # header row: chapter label left, language (and stars, once there are any) right
    head_y = 62
    parts = [tpath(f"EXPEDITION {numeral}", "caps", 19, PAD, head_y, GOLD, tracking=0.16)]
    meta = (project.get("language") or "").upper()
    rx = W - PAD
    if project.get("stars"):
        count = str(project["stars"])
        cw = text_width(count, "caps", 19, 0.08)
        parts.append(tpath(count, "caps", 19, rx, head_y, CREAM, anchor="end", tracking=0.08))
        parts.append(f'<path d="{STAR}" fill="{GOLD}" transform="translate({rx - cw - 14:.1f} {head_y - 6.5})"/>')
        rx -= cw + 40
    if meta:
        mw = text_width(meta, "caps", 19, 0.14)
        parts.append(tpath(meta, "caps", 19, rx, head_y, CREAM, anchor="end", tracking=0.14, extra='opacity=".8"'))
        parts.append(f'<path d="M{rx - mw - 18:.1f} {head_y - 6.5}l5-5 5 5-5 5Z" fill="{CRIMSON}"/>')

    title_size = fit_size(project["title"], "display", 50, inner)
    title_y = 122
    parts.append(tpath(project["title"], "display", title_size, PAD - 2, title_y, CREAM))
    parts.append(f'<path d="M{PAD} {title_y + 24}h{inner}" stroke="{GOLD}" stroke-opacity=".35"/>')

    y = title_y + 66
    text, y = body_text(wrap(project["description"], BODY, inner), PAD, y, BODY, CREAM, line_height=36, opacity=0.9)
    parts.append(text)
    if project.get("note"):
        y += 4
        text, y = body_text(wrap(project["note"], NOTE, inner, italic=True), PAD, y, NOTE, GOLD, line_height=31, italic=True)
        parts.append(text)
    tags, bottom = tag_row(project.get("tags", []), PAD, y - 4, W - PAD)
    parts.append(tags)
    height = int(bottom + PAD - 6)

    ground, border = panel(W, height)
    # chapter numeral as a faint watermark: the one ornament on the card
    mark = tpath(numeral, "display", 250, W - 18, height - 2, CREAM, anchor="end", extra='opacity=".045"')
    body = ground + mark + "".join(parts) + border
    name = project["repo"].split("/")[-1]
    desc = project["description"] + (f' {project["note"]}.' if project.get("note") else "")
    return svg_doc(W, height, body, PANEL_DEFS + grain(), title=f'{project["title"]} ({name})', desc=desc)


def build():
    projects = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    for stale in ASSETS.glob("card-*.svg"):
        stale.unlink()
    for i, project in enumerate(projects, 1):
        write(f"card-{i}.svg", card(project, i))
    return projects


if __name__ == "__main__":
    build()
