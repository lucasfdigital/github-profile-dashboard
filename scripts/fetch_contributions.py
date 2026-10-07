#!/usr/bin/env python3
"""Fetch real contribution data — no token.

GitHub serves your contribution calendar as public HTML at
https://github.com/users/<username>/contributions — the same fragment
the profile page itself uses. Parse the day cells and write
data/contributions.json with raw days plus derived stats.

Usage:
    python scripts/fetch_contributions.py [username]
    GITHUB_USERNAME=lucasfdigital python scripts/fetch_contributions.py
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config, resolve_username

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = DATA_DIR / "contributions.json"

_CFG = load_config()
USERNAME = resolve_username(
    _CFG, sys.argv[1] if len(sys.argv) > 1 else None)
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(tooltip_text: str) -> int:
    t = (tooltip_text or "").strip()
    if t.lower().startswith("no contributions"):
        return 0
    m = re.match(r"(\d+)\s+contribution", t)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)", t)
    return int(m.group(1)) if m else 0


def scrape(url: str, headers: dict) -> tuple[list[dict], object]:
    """Scrape one contributions fragment (trailing year or ?from=&to=)."""
    rr = requests.get(url, headers=headers, timeout=30)
    rr.raise_for_status()
    ss = BeautifulSoup(rr.text, "html.parser")
    cells = ss.select("td.ContributionCalendar-day")
    if not cells:
        # Fallback: older markup used rect / other selectors
        cells = ss.select("[data-date][data-level]")
    if not cells:
        raise SystemExit("No contribution day cells found — GitHub markup changed?")
    days = []
    for td in cells:
        tip = td.find_next_sibling("tool-tip")
        days.append({"date": td.get("data-date"),
                     "count": parse_count(tip.get_text() if tip else ""),
                     "level": int(td.get("data-level", 0))})
    return days, ss


def main() -> None:
    headers = {"User-Agent": "github-profile-dashboard/1.0"}
    days, soup = scrape(URL, headers)

    # full previous calendar years (the trailing scrape only covers ~12 months,
    # so e.g. 2025 would show just Oct-Dec). Merge by date, trailing wins.
    merged = {}
    cur_year = date.today().year
    for y in (cur_year - 1, cur_year - 2):
        try:
            for d in scrape(f"{URL}?from={y}-01-01&to={y}-12-31", headers)[0]:
                merged[d["date"]] = d
        except Exception as e:
            print(f"warn: full-year {y}: {e}")
    for d in days:
        merged[d["date"]] = d
    days = sorted(merged.values(), key=lambda x: x["date"])

    # Total from the <h2> ("3,174 contributions in the last year"), fallback to sum
    total = sum(d["count"] for d in days)
    h2 = soup.select_one("h2")
    if h2:
        m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", h2.get_text())
        if m:
            total = int(m.group(1).replace(",", ""))

    # Derived stats
    counts_by_date = {d["date"]: d["count"] for d in days}
    best = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}

    # Streaks (consecutive days with count > 0, ending today)
    sorted_dates = sorted(counts_by_date.keys())
    longest = 0
    run = 0
    prev = None
    for ds in sorted_dates:
        cur = date.fromisoformat(ds)
        if counts_by_date[ds] > 0:
            if prev and (cur - prev).days == 1 and run > 0:
                run += 1
            else:
                # start new run — but only continues if previous day existed
                # check continuity: if gap, reset
                if prev and (cur - prev).days != 1:
                    run = 1
                else:
                    run = run + 1 if prev else 1
            longest = max(longest, run)
        else:
            run = 0
        prev = cur

    # current streak: walk backwards from last day
    current_streak = 0
    for ds in reversed(sorted_dates):
        if counts_by_date[ds] > 0:
            current_streak += 1
        else:
            # allow today to be empty without breaking streak
            if ds == sorted_dates[-1]:
                continue
            break

    monthly = defaultdict(int)
    yearly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
        yearly[d["date"][:4]] += d["count"]

    payload = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_last_year": total,
        "days": days,
        "stats": {
            "current_streak": current_streak,
            "longest_streak": longest,
            "best_day": best["date"],
            "best_day_count": best["count"],
            "monthly_totals": dict(sorted(monthly.items())),
            "yearly_totals": dict(sorted(yearly.items())),
        },
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {OUT} — {len(days)} days, total={total}, best={best}")


if __name__ == "__main__":
    main()
