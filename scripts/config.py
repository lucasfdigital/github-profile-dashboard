#!/usr/bin/env python3
"""Shared dashboard.json config loader (template-friendly).

Resolution order for the username:
  1. CLI argument, 2. GITHUB_USERNAME env (the workflow exports
     github.repository_owner), 3. dashboard.json -> github_username.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = {
    "github_username": None,
    "exclude_repos": [],
    "sections": {
        "kpis": True,
        "extras": True,
        "chart": True,
        "languages": True,
        "heatmap": True,
    },
}

sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    try:
        raw = json.loads((ROOT / "dashboard.json").read_text())
        cfg.update(raw)
    except (OSError, ValueError):
        pass
    secs = dict(DEFAULTS["sections"])
    secs.update(cfg.get("sections") or {})
    cfg["sections"] = secs
    cfg["exclude_repos"] = cfg.get("exclude_repos") or []
    return cfg


def resolve_username(cfg: dict, cli_arg: str | None = None) -> str:
    if cli_arg:
        return cli_arg
    name = os.environ.get("GITHUB_USERNAME") or cfg.get("github_username")
    if not name:
        raise SystemExit(
            "No username: pass it as argv, set GITHUB_USERNAME, or set "
            "github_username in dashboard.json")
    return name
