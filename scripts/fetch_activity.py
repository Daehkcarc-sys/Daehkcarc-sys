"""Fetch the last 30 days of commit counts into data/activity.json. Standard library only.

Source: GitHub commit search (GET /search/commits), which only covers PUBLIC repositories'
default branches. Results from private repositories are dropped as a second guard, so a
personal token used locally cannot leak private activity into the chart. Only per-day
counts are stored: no repository names, no commit messages.

Uses GITHUB_TOKEN if set (higher rate limit); works without one.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from theme import ROOT, config, today

DAYS = 30


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-readme-build",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch():
    cfg = config()
    tz = timezone(timedelta(hours=cfg["countdown"].get("utc_offset_hours", 0)))
    end = today(cfg)
    start = end - timedelta(days=DAYS - 1)
    counts = {(start + timedelta(days=i)).isoformat(): 0 for i in range(DAYS)}
    # one day of slack on the query; exact bucketing happens below in the configured offset
    query = f'author:{cfg["github_user"]} author-date:>={(start - timedelta(days=1)).isoformat()}'
    page = 1
    while page <= 10:  # the search API serves at most 1000 results
        url = "https://api.github.com/search/commits?" + urllib.parse.urlencode(
            {"q": query, "sort": "author-date", "order": "desc", "per_page": 100, "page": page})
        data = api(url)
        items = data.get("items", [])
        for item in items:
            if item.get("repository", {}).get("private"):
                continue
            when = datetime.fromisoformat(item["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(tz)
            key = when.date().isoformat()
            if key in counts:
                counts[key] += 1
        if len(items) < 100:
            break
        page += 1
    return {"user": cfg["github_user"], "start": start.isoformat(), "end": end.isoformat(),
            "days": [{"date": d, "commits": n} for d, n in counts.items()]}


if __name__ == "__main__":
    out = ROOT / "data" / "activity.json"
    out.parent.mkdir(exist_ok=True)
    data = fetch()
    out.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"activity.json: {sum(d['commits'] for d in data['days'])} commits, {data['start']} to {data['end']}")
