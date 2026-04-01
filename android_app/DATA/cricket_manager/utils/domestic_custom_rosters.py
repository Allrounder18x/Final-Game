"""
Load optional per-club domestic rosters from config/domestic_custom_rosters.json.

Populated by tools/cricinfo_domestic_roster/apply_to_domestic_database.py from Cricinfo data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cricket_manager.utils.domestic_cricinfo_roster import filter_custom_roster_records

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "domestic_custom_rosters.json"

_cache: Optional[Dict[str, Any]] = None


def reload_domestic_custom_rosters() -> None:
    """Clear cache so the next read picks up file changes (e.g. after running the Cricinfo tool)."""
    global _cache
    _cache = None


def _normalize_tier(t: Any) -> int:
    try:
        n = int(t)
    except (TypeError, ValueError):
        return 2
    return max(1, min(5, n))


def _load() -> Dict[str, Any]:
    global _cache
    if _cache is not None:
        return _cache
    empty: Dict[str, Any] = {"defaults": {"tier": 2}, "rosters": {}}
    if not _CONFIG_PATH.is_file():
        _cache = empty
        return _cache
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        _cache = empty
        return _cache
    if not isinstance(raw, dict):
        _cache = empty
        return _cache
    rosters = raw.get("rosters")
    defaults = raw.get("_defaults") or raw.get("defaults") or {}
    if rosters is None:
        rosters = {k: v for k, v in raw.items() if k not in ("_defaults", "defaults") and isinstance(v, dict)}
    if not isinstance(rosters, dict):
        rosters = {}
    if not isinstance(defaults, dict):
        defaults = {}
    tier = _normalize_tier(defaults.get("tier", 2))
    _cache = {"defaults": {"tier": tier}, "rosters": rosters}
    return _cache


def get_custom_players_payload(nation: str, team_name: str) -> Optional[Tuple[List[dict], int]]:
    """
    If this club has a custom roster in the JSON, return (player_records, tier).
    Records match Cricinfo fetch shape: name, age, batting_styles, bowling_styles, etc.
    """
    d = _load()
    nation_map = d["rosters"].get(nation)
    if not isinstance(nation_map, dict):
        return None
    payload = nation_map.get(team_name)
    if payload is None:
        return None
    default_tier = d["defaults"]["tier"]
    if isinstance(payload, dict) and "players" in payload:
        players = payload.get("players") or []
        tier = _normalize_tier(payload.get("tier", default_tier))
    elif isinstance(payload, list):
        players = payload
        tier = default_tier
    else:
        return None
    if not isinstance(players, list):
        return None
    cleaned = [p for p in players if isinstance(p, dict) and (str(p.get("name") or "").strip())]
    cleaned = filter_custom_roster_records(cleaned)
    if not cleaned:
        return None
    return (cleaned, tier)
