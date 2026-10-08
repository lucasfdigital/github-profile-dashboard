#!/usr/bin/env python3
"""Bump the dashboard <picture> URLs in README.md with a fresh ?v= timestamp.

GitHub proxies README images through its camo cache; a new query string
forces a fresh fetch so the profile shows the just-generated SVGs.
Idempotent: replaces an existing ?v= instead of stacking one.
"""
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATTERN = re.compile(r"\./profile-top(-light)?\.svg(\?v=[\w-]+)?")


def main() -> None:
    v = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M")
    p = ROOT / "README.md"
    s = p.read_text()
    s, n = PATTERN.subn(lambda m: f"./profile-top{m.group(1) or ''}.svg?v={v}", s)
    if not n:
        print("warning: no profile-top image tag found in README.md, skipping")
        return
    p.write_text(s)
    print(f"cache-bust {v} ({n} tags)")


if __name__ == "__main__":
    main()
