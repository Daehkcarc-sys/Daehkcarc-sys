"""Rebuild every SVG in assets/ from config.json, projects.json, skills.json and data/activity.json.

    python scripts/build_all.py            # offline: uses the data already in the repo
    python scripts/build_all.py --fetch    # first refresh stars, languages and commit activity from the GitHub API

Standard library only.
"""
import sys

import build_banner
import build_cards
import build_footer
import build_gommage
import build_journal
import build_pictos
from theme import ASSETS, write


def main():
    if "--fetch" in sys.argv:
        import json

        import fetch_activity
        import refresh_projects
        from theme import ROOT

        refresh_projects.refresh()
        try:
            data = fetch_activity.fetch()
            (ROOT / "data").mkdir(exist_ok=True)
            (ROOT / "data" / "activity.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
        except Exception as exc:  # keep yesterday's data rather than fail the whole build
            print(f"activity not refreshed ({exc})")
    write("header.svg", build_banner.build())
    write("gommage.svg", build_gommage.build())
    build_cards.build()
    write("pictos.svg", build_pictos.build())
    write("journal.svg", build_journal.build())
    for name, content in (("divider.svg", build_footer.divider()), ("petal.svg", build_footer.petal())):
        (ASSETS / name).write_text(content, encoding="utf-8", newline="\n")
    total = sum(p.stat().st_size for p in ASSETS.glob("*.svg"))
    print(f"total: {total / 1024:.0f} KB in {len(list(ASSETS.glob('*.svg')))} files")


if __name__ == "__main__":
    main()
