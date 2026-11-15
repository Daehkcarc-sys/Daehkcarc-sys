"""Dev-time tool: render SVGs to PNG the way GitHub shows them.

Each SVG is loaded through an <img> tag (same sandbox GitHub uses: no scripts,
no external resources) inside a page that imitates the README column, at a
desktop width and a phone width, on GitHub's light and dark backgrounds.

Usage: python tools/render.py <out-dir> <svg> [<svg> ...] [--t=SECONDS] [--widths=846,350]
Needs Microsoft Edge (or set EDGE=path to any Chromium browser). Standard library only.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EDGE = os.environ.get("EDGE", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
THEMES = {"dark": "#0d1117", "light": "#ffffff"}


def render(svg: Path, out_dir: Path, width: int, theme: str, seconds: float):
    vb = None
    head = svg.read_text(encoding="utf-8")[:600]
    if 'viewBox="' in head:
        vb = [float(v) for v in head.split('viewBox="')[1].split('"')[0].split()]
    ratio = (vb[3] / vb[2]) if vb else 0.5
    pad = 16
    height = int(width * ratio) + 2 * pad + 2
    html = (
        f"<!doctype html><meta charset=utf-8><style>html,body{{margin:0;background:{THEMES[theme]}}}"
        f"body{{padding:{pad}px}}img{{display:block;width:{width}px}}</style>"
        f'<img src="{svg.resolve().as_uri()}">'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
        page = Path(fh.name)
    out = out_dir.resolve() / f"{svg.stem}-{width}-{theme}.png"
    out.unlink(missing_ok=True)
    cmd = [
        EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
        # Chromium clamps windows to ~500px min, so the window is wider than a phone; the <img> has the real width
        f"--window-size={max(width + 2 * pad, 520)},{height}", f"--screenshot={out}",
        f"--virtual-time-budget={int(seconds * 1000)}", page.as_uri(),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    page.unlink(missing_ok=True)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--"))
    seconds = float(opts.get("t", 6))
    widths = [int(w) for w in opts.get("widths", "846,350").split(",")]
    themes = opts.get("themes", "dark,light").split(",")
    out_dir = Path(args[0])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in args[1:]:
        for w in widths:
            for theme in themes:
                print(render(Path(name), out_dir, w, theme, seconds))


if __name__ == "__main__":
    main()
