"""Render assets/divider.svg and assets/petal.svg. Standard library only."""
from theme import ASSETS, CRIMSON, GOLD, PETAL, config, today

W, H = 800, 44


def divider():
    """Ornamental rule on a transparent ground: gold and crimson read on both light and dark pages."""
    c, y = W / 2, H / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">'
        '<title id="t">Divider</title><desc id="d">Ornamental rule with a central lozenge.</desc>'
        f'<g fill="none" stroke="{GOLD}" stroke-width="1.2" stroke-linecap="round">'
        f'<path d="M150 {y}H{c - 64}C{c - 48} {y} {c - 44} {y - 12} {c - 30} {y - 12}M{W - 150} {y}H{c + 64}C{c + 48} {y} {c + 44} {y - 12} {c + 30} {y - 12}"/>'
        f'<path d="M{c} {y - 15}l15 15-15 15-15-15Z"/></g>'
        f'<path d="M{c} {y - 7}l7 7-7 7-7-7Z" fill="{CRIMSON}"/>'
        f'<circle cx="150" cy="{y}" r="2" fill="{GOLD}"/><circle cx="{W - 150}" cy="{y}" r="2" fill="{GOLD}"/>'
        "</svg>"
    )


def petal():
    cfg = config()
    accent = today(cfg).strftime("%m-%d") == cfg.get("ornament", {}).get("accent_day")
    fill = GOLD if accent else CRIMSON
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -11 20 23" role="img" aria-labelledby="t">'
        '<!-- "Continuer à t\'aimer" -->'
        f'<title id="t">petal</title><path d="{PETAL}" fill="{fill}" transform="rotate(18)"/></svg>'
    )


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for name, content in (("divider.svg", divider()), ("petal.svg", petal())):
        (ASSETS / name).write_text(content, encoding="utf-8", newline="\n")
        print(name, len(content), "bytes")
