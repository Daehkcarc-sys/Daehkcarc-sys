"""Shared palette, config, dates and SVG helpers for the build scripts. Standard library only."""
import json
import os
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from glyphs import text_path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

INK, CREAM, CRIMSON, GOLD = "#0B0A0C", "#EDE4D0", "#B3202E", "#B89B5E"
GLOW = "#F4CE97"  # warm light: sun, rim light, painted numerals
PETAL_REDS = ["#B3202E", "#C8323F", "#8E1823"]
PETAL = "M0-9C6-7 8 2 0 10C-7 3-6-6 0-9Z"
BODY_FONT = "Georgia,'Times New Roman',serif"  # the only live text: small body copy


def config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def today(cfg=None):
    """Current date in the configured UTC offset. Override with PROFILE_TODAY=YYYY-MM-DD to preview a day."""
    forced = os.environ.get("PROFILE_TODAY")
    if forced:
        return date.fromisoformat(forced)
    offset = (cfg or config())["countdown"].get("utc_offset_hours", 0)
    return (datetime.now(timezone.utc) + timedelta(hours=offset)).date()


def days_left(cfg=None):
    cfg = cfg or config()
    return (date.fromisoformat(cfg["countdown"]["date"]) - today(cfg)).days


def roman(n):
    out = ""
    for value, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                       (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= value:
            out += sym
            n -= value
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def tpath(text, face, size, x, y, fill, anchor="start", tracking=0.0, extra=""):
    """Text converted to a filled path (headings, labels, numerals)."""
    d, _ = text_path(text, face, size, x, y, anchor, tracking)
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def grain(r=0.93, g=0.89, b=0.82):
    """Paper grain: fine noise turned into speckles of one colour. Use on a full-size rect at low opacity."""
    return (
        '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7"/>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  1.5 0 0 0 -0.55"/></filter>'
    )


def petal_css(height):
    """Falling petals. Under prefers-reduced-motion they freeze mid-fall instead of moving."""
    return (
        ".fall{animation:fall linear infinite}"
        ".sway{animation:sway ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}"
        f"@keyframes fall{{0%{{transform:translate(0,-30px);opacity:0}}8%{{opacity:1}}88%{{opacity:1}}100%{{transform:translate(var(--dx),{height + 30}px);opacity:0}}}}"
        "@keyframes sway{from{transform:rotate(-40deg)}to{transform:rotate(70deg)}}"
        "@media (prefers-reduced-motion:reduce){.fall,.sway{animation-play-state:paused}}"
    )


def petals(n, seed, width, colors=PETAL_REDS, margin=20, scale=(0.8, 1.5), opacity=(0.75, 1.0)):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = margin + (width - 2 * margin) * (i + rnd.random() * 0.8) / n
        dur = rnd.uniform(15, 26)
        sway = rnd.uniform(3.2, 5.5)
        out.append(
            f'<g transform="translate({x:.0f} 0)"><g class="fall" style="--dx:{rnd.uniform(-70, 70):.0f}px;animation-duration:{dur:.1f}s;animation-delay:{-rnd.uniform(0, dur):.1f}s">'
            f'<path class="sway" style="animation-duration:{sway:.1f}s;animation-delay:{-rnd.uniform(0, sway):.1f}s" d="{PETAL}" '
            f'transform="scale({rnd.uniform(*scale):.2f})" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/></g></g>'
        )
    return "".join(out)


def svg_doc(width, height, body, defs="", style="", title="", desc="", comment="", radius=14):
    """Wrap a drawing: accessible title/desc, rounded panel clip. No scripts, no external references."""
    note = f"<!-- {comment} -->" if comment else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
        f'{note}<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        + (f"<style>{style}</style>" if style else "")
        + f'<defs><clipPath id="panel"><rect width="{width}" height="{height}" rx="{radius}"/></clipPath>{defs}</defs>'
        f'<g clip-path="url(#panel)">{body}</g></svg>'
    )


def write(name, content):
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"{name}: {path.stat().st_size / 1024:.1f} KB")
    return path
