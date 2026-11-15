"""Render assets/header.svg: the banner. Standard library only.

Text and the countdown date come from config.json. The numeral on the monolith is the
number of days left to countdown.date, so this is rebuilt daily together with the counter.
"""
import random

from glyphs import fit_size, text_width
from theme import (CREAM, CRIMSON, GLOW, GOLD, INK, config, days_left, grain, petal_css, petals, roman,
                   svg_doc, today, tpath, write)

W, H = 1000, 400
HZ = 282  # horizon line
MX, LEAN, SUN_DX = 822, 4, -78  # monolith foot, lean in degrees, sun offset from the foot


def paris(seed, base, hmin, hmax, wmin, wmax, dome_x=None, x0=-12, x1=W + 12):
    """Haussmann roofline as one path: cornice, steep mansard, chimney walls with pots, optional dome."""
    rnd = random.Random(seed)
    d = []
    x = x0
    while x < x1:
        w = rnd.uniform(wmin, wmax)
        top = base - rnd.uniform(hmin, hmax)  # cornice line
        r = rnd.uniform(15, 22)  # mansard height
        inset = rnd.uniform(4, 7)  # steep lower slope
        d.append(f"M{x:.0f} {H + 5}V{top:.0f}h-2v-2.5h{w + 4:.0f}v2.5h-2V{H + 5}Z")
        d.append(f"M{x:.0f} {top:.0f}L{x + inset:.0f} {top - r:.0f}L{x + inset + 7:.0f} {top - r - 3:.0f}H{x + w - inset - 7:.0f}L{x + w - inset:.0f} {top - r:.0f}L{x + w:.0f} {top:.0f}Z")
        for side in rnd.sample([0, 1], rnd.randint(1, 2)):  # chimney wall with a row of pots
            cw = rnd.uniform(12, 24)
            ch = rnd.uniform(9, 15)
            cx = x + inset + 3 if side == 0 else x + w - inset - 3 - cw
            cy = top - r - 2
            d.append(f"M{cx:.0f} {cy:.0f}v{-ch:.0f}h{cw:.0f}v{ch:.0f}Z")
            for k in range(int(cw // 4.5)):
                d.append(f"M{cx + 1.2 + k * 4.5:.1f} {cy - ch:.0f}v-{rnd.uniform(3, 5.5):.1f}h2v5.5Z")
        if dome_x is not None and x <= dome_x < x + w + 4:
            c, y = x + w / 2, top - r - 2
            d.append(f"M{c - 38:.0f} {y + 3:.0f}v-20h76v20Z")  # drum
            d.append(f"M{c - 33:.0f} {y - 17:.0f}C{c - 33:.0f} {y - 66:.0f} {c + 33:.0f} {y - 66:.0f} {c + 33:.0f} {y - 17:.0f}Z")  # dome
            d.append(f"M{c - 5:.0f} {y - 50:.0f}v-15h10v15ZM{c - 1.5:.0f} {y - 65:.0f}l1.5-20l1.5 20Z")  # lantern, spire
        x += w + rnd.uniform(1, 4)
    return "".join(d)


def poly(points, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="M{" ".join(f"{x} {y}" for x, y in points)}Z" {a}/>'


def stroke(points, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="M{" ".join(f"{x} {y}" for x, y in points)}" fill="none" stroke-linecap="round" stroke-linejoin="round" {a}/>'


def numeral(days):
    """Painted day count. Bare once the date has passed; crimson on the day it reads 33."""
    if days <= 0:
        return ""
    text = str(days)
    size = fit_size(text, "displayBold", 62, 72)
    color = "#E0303E" if days == 33 else GLOW
    return (
        tpath(text, "displayBold", size, -6, -158, color, anchor="middle", extra='opacity=".5" filter="url(#soft)"')
        + tpath(text, "displayBold", size, -6, -158, color, anchor="middle", extra='opacity=".78" filter="url(#paint)"')
    )


def monolith(days):
    """Colossus: leaves the frame, two faces, rim light on both edges, cracks, mist at the foot."""
    front = [(-58, 8), (-44, -360), (40, -360), (46, 8)]
    side = [(46, 8), (40, -360), (62, -360), (70, 8)]
    cracks = [[(-30, 6), (-24, -40), (-32, -78), (-22, -120)], [(20, -360), (14, -300), (24, -262), (18, -230)], [(30, 6), (34, -50), (26, -84)]]
    return (
        '<g filter="url(#rough)">'
        + poly(front, fill="url(#face)") + poly(side, fill="url(#lit)")
        + stroke([(40, -360), (46, 6)], stroke=GLOW, stroke_width=2, opacity=".9")
        + stroke([(-44, -360), (-58, 6)], stroke=GLOW, stroke_width=1.6, opacity=".75")
        + "".join(stroke(c, stroke=GLOW, stroke_width=1, opacity=".4") for c in cracks)
        + "</g>" + numeral(days)
        + f'<ellipse cx="0" cy="2" rx="150" ry="13" fill="{GLOW}" opacity=".3" filter="url(#mist)"/>'
    )


def build():
    cfg = config()
    days = days_left(cfg)
    handle, name = cfg["handle"], cfg["name"]
    label = f'{cfg["banner"]["label"]}  ·  {roman(today(cfg).year)}'
    tagline = cfg["banner"]["tagline"]
    sx = MX + SUN_DX
    defs = grain() + f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="{HZ}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#08070a"/><stop offset=".5" stop-color="#160d12"/><stop offset=".84" stop-color="#4a161c"/><stop offset="1" stop-color="#96292a"/></linearGradient>
<linearGradient id="sea" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#34131a"/><stop offset=".35" stop-color="#160b0f"/><stop offset="1" stop-color="#0a080a"/></linearGradient>
<radialGradient id="halo" cx="{sx}" cy="{HZ}" r="360" gradientUnits="userSpaceOnUse" gradientTransform="translate(0 {HZ * 0.42:.0f}) scale(1 .58)"><stop offset="0" stop-color="#FFE9BE"/><stop offset=".14" stop-color="#F3AE6A" stop-opacity=".82"/><stop offset=".38" stop-color="#C5333A" stop-opacity=".45"/><stop offset="1" stop-color="#B3202E" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF0CF"/><stop offset=".7" stop-color="#F8CB8C"/><stop offset="1" stop-color="#EE9C5A"/></radialGradient>
<linearGradient id="face" x1="0" y1="-220" x2="0" y2="6" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#050406"/><stop offset=".75" stop-color="#0a0608"/><stop offset="1" stop-color="#2a0f13"/></linearGradient>
<linearGradient id="lit" x1="0" y1="-220" x2="0" y2="6" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2c171b"/><stop offset=".6" stop-color="#55211f"/><stop offset="1" stop-color="#a2452f"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{INK}" stop-opacity=".8"/><stop offset=".5" stop-color="{INK}" stop-opacity=".4"/><stop offset=".7" stop-color="{INK}" stop-opacity="0"/></linearGradient>
<clipPath id="above"><rect width="{W}" height="{HZ}"/></clipPath>
<filter id="brush" x="-5%" y="-40%" width="110%" height="180%"><feTurbulence type="fractalNoise" baseFrequency="0.009 0.11" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="34" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="rough" x="-20%" y="-5%" width="140%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="11"/><feDisplacementMap in="SourceGraphic" scale="3" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="paint" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="6"/><feDisplacementMap in="SourceGraphic" scale="2.4" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="scrim" x="-10%" y="-80%" width="120%" height="260%"><feGaussianBlur stdDeviation="11"/></filter>
<filter id="mist" x="-30%" y="-200%" width="160%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
"""
    rnd = random.Random(5)
    bands = []
    for _ in range(10):  # painterly cloud bands, smeared by the brush filter
        y = rnd.uniform(70, HZ - 22)
        col = rnd.choice(["#B3202E", "#7a1c22", "#D0905A", "#5a1a22"])
        bands.append(f'<ellipse cx="{rnd.uniform(360, 1000):.0f}" cy="{y:.0f}" rx="{rnd.uniform(140, 330):.0f}" ry="{rnd.uniform(3, 9):.0f}" fill="{col}" opacity="{0.10 + 0.34 * (y / HZ) ** 2:.2f}"/>')
    refl = []
    for i in range(8):  # sun on the water
        half = (64 - i * 6) * rnd.uniform(.5, 1.1)
        refl.append(f'<rect x="{sx - half + rnd.uniform(-10, 10):.0f}" y="{HZ + 5 + i * 5.5:.1f}" width="{2 * half:.0f}" height="1.5" fill="{GLOW}" opacity="{0.6 - i * 0.065:.2f}"/>')
    wr = random.Random(2)
    windows = "".join(
        f'<rect x="{wr.uniform(20, 980):.0f}" y="{wr.uniform(376, 394):.0f}" width="2.2" height="3.6" fill="{GLOW}" opacity="{wr.uniform(.5, .95):.2f}"/>' for _ in range(12))

    text_w = 668  # room left of the monolith
    name_size = fit_size(handle, "display", 116, text_w)
    tag_size = fit_size(tagline, "display", 37, text_w)
    tag_w = text_width(tagline, "display", tag_size)
    body = f"""
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{HZ}" fill="url(#halo)"/>
<g filter="url(#brush)">{''.join(bands)}</g>
<circle cx="{sx}" cy="{HZ - 4}" r="50" fill="url(#sun)" clip-path="url(#above)"/>
<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#sea)"/>
<rect y="{HZ}" width="{W}" height="1" fill="{GLOW}" opacity=".4"/>
{''.join(refl)}
<g transform="translate({MX} {HZ}) rotate({LEAN})">{monolith(days)}</g>
<path d="{paris(21, 372, 2, 20, 46, 92, dome_x=700)}" fill="#2a151e"/>
<path d="{paris(8, 406, 6, 30, 60, 128)}" fill="#050405"/>
{windows}
<rect width="{W}" height="{HZ - 30}" fill="url(#fade)"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".2"/>
{petals(10, 3, W)}
<rect x="34" y="229" width="{tag_w + 58:.0f}" height="46" rx="23" fill="{INK}" opacity=".62" filter="url(#scrim)"/>
{tpath(label, "caps", 25, 64, 84, GOLD, tracking=0.14)}
{tpath(handle, "display", name_size, 58, 186, CREAM)}
<path d="M64 216h250" stroke="{GOLD}" stroke-width="1.2"/><path d="M324 216l7-7 7 7-7 7Z" fill="{CRIMSON}"/>
{tpath(tagline, "display", tag_size, 63, 261, CREAM)}
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.5" fill="none" stroke="{CREAM}" stroke-opacity=".16" stroke-width="1.5"/>
"""
    scene = "a dark leaning monolith against the setting sun on a crimson horizon, beyond Paris rooftops, with crimson petals drifting down"
    count = f" The monolith is painted with the number {days}." if days > 0 else ""
    return svg_doc(W, H, body, defs, petal_css(H),
                   title=f"{handle} — {tagline}",
                   desc=f"Banner for {name} ({handle}): {scene}.{count}",
                   comment="The number goes down. The work goes up.")


if __name__ == "__main__":
    write("header.svg", build())
