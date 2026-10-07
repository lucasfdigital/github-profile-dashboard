#!/usr/bin/env python3
"""Fetch public GitHub stats without any token (REST API, unauthenticated).

- Languages: sum bytes per language across your non-fork repos
  (most recently pushed first, capped to stay far under the 60 req/h
  unauthenticated rate limit).
- Repo activity: scan your recent public events (~90 days) and count
  commits / PRs / issues per repository.

Writes data/github_stats.json. If the API rate-limits us, the previous
file is kept untouched and we exit 0 (never break the dashboard).

Usage:
    python scripts/fetch_github_stats.py [username]
"""
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config, resolve_username

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "github_stats.json"

_CFG = load_config()
USERNAME = resolve_username(
    _CFG, sys.argv[1] if len(sys.argv) > 1 else None)
API = "https://api.github.com"
HEADERS = {"User-Agent": "github-profile-dashboard/1.0",
           "Accept": "application/vnd.github+json"}

MAX_REPOS_LANG = 30
MAX_EVENT_PAGES = 3

# repos that never count toward languages (docs, playground, profile, ...)
# full "owner/name" entries, configurable in dashboard.json
EXCLUDE_REPOS = set(_CFG.get("exclude_repos", []))


def get(url: str):
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 403 and "rate limit" in r.text.lower():
        raise RuntimeError("rate-limited")
    r.raise_for_status()
    # be gentle with the unauthenticated quota
    time.sleep(0.4)
    return r.json()


def main() -> None:
    try:
        repos, page = [], 1
        while True:
            batch = get(f"{API}/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        own = [r for r in repos
               if not r.get("fork") and r.get("full_name") not in EXCLUDE_REPOS]
        own.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
        stars = sum(int(r.get("stargazers_count") or 0) for r in own)

        try:
            prs = get(f"{API}/search/issues?q=author:{USERNAME}+type:pr&per_page=1").get("total_count")
        except Exception as e:
            print(f"warn: pr search: {e}")
            prs = None

        lang_bytes: dict[str, int] = defaultdict(int)
        for r in own[:MAX_REPOS_LANG]:
            lu = r.get("languages_url")
            if not lu:
                continue
            try:
                for lang, n in get(lu).items():
                    lang_bytes[lang] += n
            except RuntimeError:
                raise
            except Exception as e:
                print(f"warn: languages for {r.get('full_name')}: {e}")
        tot = sum(lang_bytes.values()) or 1
        languages = sorted(
            ({"name": k, "bytes": v, "pct": round(v / tot * 100, 1)}
             for k, v in lang_bytes.items()),
            key=lambda d: d["bytes"], reverse=True)[:8]

        activity: dict[str, dict] = defaultdict(lambda: {"commits": 0, "prs": 0, "issues": 0})
        for page in range(1, MAX_EVENT_PAGES + 1):
            try:
                events = get(f"{API}/users/{USERNAME}/events/public?per_page=100&page={page}")
            except Exception as e:
                print(f"warn: events page {page}: {e}")
                break
            if not events:
                break
            for ev in events:
                repo = (ev.get("repo") or {}).get("name", "?")
                t = ev.get("type", "")
                if t == "PushEvent":
                    activity[repo]["commits"] += len((ev.get("payload") or {}).get("commits", []))
                elif t == "PullRequestEvent":
                    activity[repo]["prs"] += 1
                elif t == "IssuesEvent":
                    activity[repo]["issues"] += 1
        repos_top = sorted(
            ({"repo": k, **v, "total": v["commits"] + v["prs"] + v["issues"]}
             for k, v in activity.items()),
            key=lambda d: d["total"], reverse=True)
        repos_top = [r for r in repos_top if r["total"] > 0][:8]

        payload = {
            "username": USERNAME,
            "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "repo_count": len(own),
            "stars": stars,
            "prs": prs,
            "languages": languages,
            "repos": repos_top,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Wrote {OUT} — {len(own)} repos, {len(languages)} langs, {len(repos_top)} active repos")
    except RuntimeError as e:
        print(f"skip ({e}): keeping previous {OUT}")
        if not OUT.exists():
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps({"username": USERNAME, "languages": [], "repos": []}) + "\n")


if __name__ == "__main__":
    main()
