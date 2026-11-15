"""Dev-time tool: extract glyph outlines + kerning from font files into scripts/glyphs.json.

Only needed if you want to change the typefaces. Day-to-day text edits do NOT
need this: the build scripts in scripts/ compose paths from glyphs.json using
the standard library only.

Requires: pip install fonttools
Usage:    python tools/extract_glyphs.py <dir-with-ttf-files>

Fonts (SIL Open Font License 1.1, from https://github.com/google/fonts/tree/main/ofl):
  cormorantgaramond/CormorantGaramond[wght].ttf
  cormorantgaramond/CormorantGaramond-Italic[wght].ttf
  cinzel/Cinzel[wght].ttf
"""
import json
import sys
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# name in glyphs.json -> (file name suffix, weight)
FACES = {
    "display": ("CormorantGaramond[wght].ttf", 600),
    "displayBold": ("CormorantGaramond[wght].ttf", 700),
    "italic": ("CormorantGaramond-Italic[wght].ttf", 500),
    "caps": ("Cinzel[wght].ttf", 500),
}

CHARS = (
    "".join(chr(c) for c in range(32, 127))
    + "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜàâäçéèêëîïôöùûüñÑ"
    + "–—·•’‘“”…×→"
)


class ListPen(BasePen):
    """Records an outline as [op, numbers...] lists (M, L, Q, C, Z)."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.cmds = []

    def _moveTo(self, pt):
        self.cmds.append(["M", *pt])

    def _lineTo(self, pt):
        self.cmds.append(["L", *pt])

    def _curveToOne(self, p1, p2, p3):
        self.cmds.append(["C", *p1, *p2, *p3])

    def _qCurveToOne(self, p1, p2):
        self.cmds.append(["Q", *p1, *p2])

    def _closePath(self):
        self.cmds.append(["Z"])

    def _endPath(self):
        self.cmds.append(["Z"])


def kerning_pairs(font, cmap, chars):
    """Flatten GPOS 'kern' pair positioning to {left+right: xAdvance delta}."""
    if "GPOS" not in font:
        return {}
    gpos = font["GPOS"].table
    if not gpos.FeatureList or not gpos.LookupList:
        return {}
    name_to_chars = {}
    for ch in chars:
        g = cmap.get(ord(ch))
        if g:
            name_to_chars.setdefault(g, []).append(ch)
    wanted = set(name_to_chars)
    lookups = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            lookups.update(fr.Feature.LookupListIndex)
    pairs = {}

    def put(left, right, value):
        if not value:
            return
        for a in name_to_chars[left]:
            for b in name_to_chars[right]:
                pairs.setdefault(a + b, value)  # first matching subtable wins

    for idx in sorted(lookups):
        lookup = gpos.LookupList.Lookup[idx]
        seen = set()  # pairs already decided by an earlier subtable of this lookup
        for st in lookup.SubTable:
            if st.LookupType == 9:
                st = st.ExtSubTable
            if st.LookupType != 2:
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for left, ps in zip(cov, st.PairSet):
                    if left not in wanted:
                        continue
                    for rec in ps.PairValueRecord:
                        right = rec.SecondGlyph
                        if right in wanted and (left, right) not in seen:
                            seen.add((left, right))
                            v = rec.Value1.XAdvance if rec.Value1 else 0
                            put(left, right, v or 0)
            elif st.Format == 2:
                c1 = st.ClassDef1.classDefs if st.ClassDef1 else {}
                c2 = st.ClassDef2.classDefs if st.ClassDef2 else {}
                for left in cov:
                    if left not in wanted:
                        continue
                    row = st.Class1Record[c1.get(left, 0)]
                    for right in wanted:
                        if (left, right) in seen:
                            continue
                        rec = row.Class2Record[c2.get(right, 0)]
                        v = rec.Value1.XAdvance if rec.Value1 else 0
                        seen.add((left, right))
                        put(left, right, v or 0)
    return pairs


def extract(path, weight):
    font = TTFont(path)
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": weight})
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"]
    glyphs = {}
    for ch in CHARS:
        name = cmap.get(ord(ch))
        if not name:
            continue
        pen = ListPen(glyph_set)
        glyph_set[name].draw(pen)
        cmds = [[c[0], *[round(v) for v in c[1:]]] for c in pen.cmds]
        glyphs[ch] = {"w": hmtx[name][0], "d": cmds}
    os2 = font["OS/2"]
    return {
        "unitsPerEm": font["head"].unitsPerEm,
        "capHeight": getattr(os2, "sCapHeight", 0),
        "xHeight": getattr(os2, "sxHeight", 0),
        "glyphs": glyphs,
        "kern": kerning_pairs(font, cmap, CHARS),
    }


def main():
    src = Path(sys.argv[1])
    out = {}
    for face, (suffix, weight) in FACES.items():
        matches = [p for p in src.iterdir() if p.name.endswith(suffix)]
        # "CormorantGaramond[wght].ttf" must not match the Italic file
        matches = [p for p in matches if ("Italic" in p.name) == ("Italic" in suffix)]
        if not matches:
            sys.exit(f"font not found for {face}: *{suffix} in {src}")
        out[face] = extract(matches[0], weight)
        print(face, matches[0].name, len(out[face]["glyphs"]), "glyphs,", len(out[face]["kern"]), "kern pairs")
    dest = Path(__file__).resolve().parent.parent / "scripts" / "glyphs.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print("wrote", dest, dest.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
