"""Refresh stars and primary language in projects.json from the GitHub API. Standard library only.

Only public repositories are read. A project with "language_pin": true keeps its language.
A failed request leaves that project unchanged.
"""
import json

from fetch_activity import api
from theme import ROOT


def refresh():
    path = ROOT / "projects.json"
    projects = json.loads(path.read_text(encoding="utf-8"))
    for p in projects:
        try:
            repo = api(f'https://api.github.com/repos/{p["repo"]}')
        except Exception as exc:  # network error, rate limit, renamed repo: keep the last known values
            print(f'{p["repo"]}: not refreshed ({exc})')
            continue
        if repo.get("private"):
            continue
        p["stars"] = repo.get("stargazers_count", p.get("stars", 0))
        if not p.get("language_pin") and repo.get("language"):
            p["language"] = repo["language"]
        print(f'{p["repo"]}: {p["stars"]} stars, {p.get("language")}')
    path.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    refresh()
