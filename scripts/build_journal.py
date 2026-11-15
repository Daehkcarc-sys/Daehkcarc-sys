"""Render assets/journal.svg from data/activity.json: 30 days of commits, one petal per day.

It is an ordinary column chart drawn with petals: each petal stands on the baseline and
its height is proportional to that day's commits. Days without commits get a small dot.
Standard library only.
"""
import json
import random
from datetime import date

from theme import (CREAM, GOLD, PANEL_DEFS, PETAL_REDS, ROOT, body_text, grain, panel, svg_doc, tpath, wrap, write)

W, H = 800, 340
PAD = 46
BASE = 266  # baseline y
TOP = 172  # tallest petal reaches here
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def petal(x, h, w, lean, fill):
    """A petal standing on the baseline at x: height h, widest about a third of the way up."""
    d = (f"M0 0C{w * .95:.1f} {-h * .22:.1f} {w * .62:.1f} {-h * .82:.1f} 0 {-h:.1f}"
         f"C{-w * .5:.1f} {-h * .8:.1f} {-w * .9:.1f} {-h * .3:.1f} 0 0Z")
    return f'<path d="{d}" fill="{fill}" transform="translate({x:.1f} {BASE}) rotate({lean:.1f})"/>'


def build():
    data = json.loads((ROOT / "data" / "activity.json").read_text(encoding="utf-8"))
    days = data["days"]
    n = len(days)
    counts = [d["commits"] for d in days]
    total, peak, active = sum(counts), max(counts), sum(1 for c in counts if c)
    slot = (W - 2 * PAD) / n
    rnd = random.Random(7)
    marks, ticks = [], []
    for i, day in enumerate(days):
        x = PAD + slot * (i + 0.5)
        c = day["commits"]
        dt = date.fromisoformat(day["date"])
        if c:
            h = 16 + (BASE - TOP - 16) * c / peak  # linear in commits, with a visible minimum
            w = min(slot * 0.5, 7 + h * 0.12)
            marks.append(petal(x, h, w, rnd.uniform(-5, 5), PETAL_REDS[i % 3]))
            marks.append(tpath(str(c), "caps", 19 if c == peak else 16, x, BASE - h - 9, CREAM, anchor="middle",
                               extra="" if c == peak else 'opacity=".75"'))
        else:
            marks.append(f'<circle cx="{x:.1f}" cy="{BASE}" r="1.8" fill="{GOLD}" opacity=".7"/>')
        if dt.weekday() == 0 or i == n - 1:  # label Mondays and the last day
            if i == n - 1 and ticks and i - ticks[-1][0] < 3:
                ticks.pop()
            ticks.append((i, x, f"{dt.day} {MON[dt.month - 1]}"))
    axis = [f'<path d="M{PAD} {BASE}H{W - PAD}" stroke="{GOLD}" stroke-opacity=".45"/>']
    for i, x, text in ticks:
        axis.append(f'<path d="M{x:.1f} {BASE}v7" stroke="{GOLD}" stroke-opacity=".6"/>')
        last = i == n - 1
        axis.append(tpath(text, "caps", 17, W - PAD if last else x, BASE + 30, GOLD, anchor="end" if last else "middle", tracking=0.08))

    summary = f"{total} commits on {active} of the last {n} days" if total else f"No public commits in the last {n} days"
    note, _ = body_text(wrap(f"{summary}. One petal per day; its height is that day's commits to public repositories.", 22, W - 2 * PAD),
                        PAD, 98, 22, CREAM, opacity=0.85)
    ground, border = panel(W, H)
    body = (
        ground
        + tpath(f"EXPEDITION JOURNAL  ·  LAST {n} DAYS", "caps", 19, PAD, 62, GOLD, tracking=0.16)
        + note + "".join(axis) + "".join(marks) + border
    )
    listing = ", ".join(f"{date.fromisoformat(d['date']).day} {MON[date.fromisoformat(d['date']).month - 1].title()}: {d['commits']}"
                        for d in days if d["commits"]) or "none"
    return svg_doc(W, H, body, PANEL_DEFS + grain(),
                   title=f"Commit activity, last {n} days: {summary.lower()}",
                   desc=f"Column chart drawn as petals, one per day from {data['start']} to {data['end']}; height is the number of commits to public repositories. Days with commits: {listing}.")


if __name__ == "__main__":
    write("journal.svg", build())
