"""
Build Player instances from Cricinfo-style roster dicts for domestic squads.

Delegates to tools/cricinfo_domestic_roster/build_game_player.py so CLI and game
stay in sync (same skills / traits logic).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Optional

_make_player_fn: Optional[Callable[..., Any]] = None


def _resolve_tool_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "tools" / "cricinfo_domestic_roster"


def _load_make_player() -> Callable[..., Any]:
    global _make_player_fn
    if _make_player_fn is not None:
        return _make_player_fn
    tool_dir = _resolve_tool_dir()
    if not tool_dir.is_dir():
        raise ImportError(
            f"Cricinfo roster tools not found at {tool_dir}. "
            "Restore the tools/cricinfo_domestic_roster folder."
        )
    td = str(tool_dir)
    if td not in sys.path:
        sys.path.insert(0, td)
    from build_game_player import make_player_for_game as fn

    _make_player_fn = fn
    return fn


def make_player_for_game(rec, nationality, tier=2, rng=None):
    """Same contract as tools/cricinfo_domestic_roster/build_game_player.make_player_for_game."""
    fn = _load_make_player()
    return fn(rec, nationality, tier=tier, rng=rng)


def filter_custom_roster_records(records: list) -> list:
    """Drop rows whose name is a bowling/style fragment (not a person)."""
    tool_dir = _resolve_tool_dir()
    td = str(tool_dir)
    if td not in sys.path:
        sys.path.insert(0, td)
    from roster_validation import is_valid_roster_player_name

    out = []
    for r in records:
        if not isinstance(r, dict):
            continue
        if is_valid_roster_player_name(str(r.get("name") or "")):
            out.append(r)
    return out
