"""Render assets/gommage.svg: the countdown. Standard library only.

The numeral is the number of days from today to countdown.date in config.json (the same
value the banner uses). On the day it reads 33 it is painted crimson; from the date
onwards the monolith is bare and the heading changes.
"""
from datetime import date

from glyphs import fit_size
from theme import (CREAM, GLOW, GOLD, INK, body_text, config, days_left, grain, svg_doc, tpath, wrap, write)

W, H = 800, 300
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def build():
    cfg = config()
    c = cfg["countdown"]
    days = days_left(cfg)
    target = date.fromisoformat(c["date"])
    when = f"{target.day} {MONTHS[target.month - 1]} {target.year}"
    done = days <= 0
    label = (c["label_after"] if done else c["label"]).replace("{date}", when).upper()
    heading = c["heading_after"] if done else c["heading"]
    color = "#E0303E" if days == 33 else GLOW

    mx = 150  # monolith centre
    defs = grain() + f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#09080b"/><stop offset=".55" stop-color="#1a0e13"/><stop offset=".86" stop-color="#55181d"/><stop offset="1" stop-color="#8f2729"/></linearGradient>
<radialGradient id="halo" cx="{mx - 60}" cy="{H}" r="330" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFE9BE" stop-opacity=".9"/><stop offset=".2" stop-color="#F3AE6A" stop-opacity=".5"/><stop offset=".55" stop-color="#C5333A" stop-opacity=".22"/><stop offset="1" stop-color="#B3202E" stop-opacity="0"/></radialGradient>
<linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050406"/><stop offset=".7" stop-color="#0a0608"/><stop offset="1" stop-color="#2a0f13"/></linearGradient>
<linearGradient id="lit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c171b"/><stop offset=".6" stop-color="#55211f"/><stop offset="1" stop-color="#a2452f"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset=".3" stop-color="{INK}" stop-opacity="0"/><stop offset=".5" stop-color="{INK}" stop-opacity=".72"/><stop offset="1" stop-color="{INK}" stop-opacity=".9"/></linearGradient>
<filter id="rough" x="-20%" y="-5%" width="140%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="11"/><feDisplacementMap in="SourceGraphic" scale="3" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="paint" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" seed="6"/><feDisplacementMap in="SourceGraphic" scale="3.4" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
"""
    number = ""
    if not done:
        text = str(days)
        size = fit_size(text, "displayBold", 124, 150)
        number = (
            tpath(text, "displayBold", size, -4, 172, color, anchor="middle", extra='opacity=".5" filter="url(#soft)"')
            + tpath(text, "displayBold", size, -4, 172, color, anchor="middle", extra='opacity=".85" filter="url(#paint)"')
        )
    slab = (
        '<g filter="url(#rough)">'
        f'<path d="M-104 {H + 20}L-90 -20L84 -20L92 {H + 20}Z" fill="url(#face)"/>'
        f'<path d="M92 {H + 20}L84 -20L112 -20L124 {H + 20}Z" fill="url(#lit)"/>'
        f'<path d="M84 -20L92 {H + 20}" stroke="{GLOW}" stroke-width="2" opacity=".9" fill="none"/>'
        f'<path d="M-90 -20L-104 {H + 20}" stroke="{GLOW}" stroke-width="1.6" opacity=".7" fill="none"/>'
        f'<path d="M-60 -20L-52 30L-64 62L-56 96M40 {H + 20}L46 250L36 222" stroke="{GLOW}" stroke-width="1" opacity=".35" fill="none" stroke-linejoin="round"/>'
        "</g>" + number
    )
    tx = 318
    room = W - tx - 40
    lines, _ = body_text(wrap(c["line"], 25, room), tx, 196, 25, CREAM, line_height=36, opacity=0.9)
    body = f"""
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#halo)"/>
<g transform="translate({mx} 0) rotate(3 0 {H})">{slab}</g>
<rect width="{W}" height="{H}" fill="url(#fade)"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".2"/>
{tpath(label, "caps", fit_size(label, "caps", 19, room, tracking=0.1), tx, 78, GOLD, tracking=0.1)}
{tpath(heading, "display", fit_size(heading, "display", 50, room), tx - 2, 134, CREAM)}
<path d="M{tx} 156h150" stroke="{GOLD}" stroke-width="1.2"/><path d="M{tx + 160} 156l6-6 6 6-6 6Z" fill="#B3202E"/>
{lines}
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.5" fill="none" stroke="{CREAM}" stroke-opacity=".16" stroke-width="1.5"/>
"""
    if done:
        title = heading
        desc = f"A bare monolith. {c['line']}"
    else:
        title = f"{days} days until {when}"
        desc = f"Countdown painted on a monolith: {days} days until graduation on {when}. {heading}: {c['line']}"
    return svg_doc(W, H, body, defs, title=title, desc=desc)


if __name__ == "__main__":
    write("gommage.svg", build())
