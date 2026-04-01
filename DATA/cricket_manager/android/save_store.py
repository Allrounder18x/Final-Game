"""
Android-safe save abstraction with pickle compatibility bridge.

Canonical format:
- JSON container with schema/version metadata
- Base64 encoded pickle payload for full backwards-compatible engine state
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class AndroidSaveStore:
    """Persist and restore game state using a versioned JSON container."""

    SCHEMA_VERSION = 1

    def __init__(self, app_dir: str) -> None:
        self.app_dir = app_dir
        self.saves_dir = os.path.join(app_dir, "saves")
        os.makedirs(self.saves_dir, exist_ok=True)

    def _save_path(self, slot_name: str) -> str:
        safe_slot = "".join(ch for ch in slot_name if ch.isalnum() or ch in ("_", "-", ".")).strip(".")
        if not safe_slot:
            safe_slot = "autosave"
        if not safe_slot.endswith(".json"):
            safe_slot = f"{safe_slot}.json"
        return os.path.join(self.saves_dir, safe_slot)

    def save_engine(self, engine: Any, slot_name: str) -> str:
        """
        Save engine state in canonical JSON format.
        Returns full save file path.
        """
        save_path = self._save_path(slot_name)
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
            temp_pickle_path = tmp.name
        try:
            engine.save_game(temp_pickle_path)
            with open(temp_pickle_path, "rb") as fh:
                pickle_bytes = fh.read()

            payload = {
                "schema": "cricket_manager_android_save",
                "schema_version": self.SCHEMA_VERSION,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "engine_version_hint": "legacy_pickle_bridge",
                "summary": {
                    "season": getattr(engine, "current_season", None),
                    "year": getattr(engine, "current_year", None),
                    "user_team": getattr(getattr(engine, "user_team", None), "name", None),
                },
                "pickle_payload_b64": base64.b64encode(pickle_bytes).decode("ascii"),
            }
            with open(save_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=True, indent=2)
            return save_path
        finally:
            if os.path.exists(temp_pickle_path):
                os.remove(temp_pickle_path)

    def load_engine(self, engine: Any, path_or_slot: str) -> str:
        """
        Load from either:
        - canonical JSON save file
        - legacy .pkl save file
        Returns source format string: 'json' or 'pickle'.
        """
        candidate = path_or_slot
        if not os.path.isabs(candidate):
            candidate = self._save_path(path_or_slot)

        if not os.path.exists(candidate):
            raise FileNotFoundError(f"Save not found: {candidate}")

        lower = candidate.lower()
        if lower.endswith(".pkl") or lower.endswith(".pickle"):
            engine.load_game(candidate)
            return "pickle"

        with open(candidate, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

        schema_version = int(payload.get("schema_version", 0))
        if schema_version > self.SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported save schema version {schema_version}. "
                f"Current supported version is {self.SCHEMA_VERSION}."
            )
        pickle_b64 = payload.get("pickle_payload_b64")
        if not pickle_b64:
            raise ValueError("Invalid save file: missing pickle payload")

        pickle_bytes = base64.b64decode(pickle_b64.encode("ascii"))
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
            temp_pickle_path = tmp.name
            tmp.write(pickle_bytes)

        try:
            engine.load_game(temp_pickle_path)
        finally:
            if os.path.exists(temp_pickle_path):
                os.remove(temp_pickle_path)
        return "json"

    def list_saves(self) -> list[Dict[str, Optional[str]]]:
        out: list[Dict[str, Optional[str]]] = []
        if not os.path.exists(self.saves_dir):
            return out
        for name in sorted(os.listdir(self.saves_dir)):
            if not name.lower().endswith(".json"):
                continue
            full = os.path.join(self.saves_dir, name)
            team = None
            season = None
            year = None
            try:
                with open(full, "r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                summary = payload.get("summary", {})
                team = summary.get("user_team")
                season = str(summary.get("season")) if summary.get("season") is not None else None
                year = str(summary.get("year")) if summary.get("year") is not None else None
            except Exception:
                pass
            out.append(
                {
                    "slot": name,
                    "path": full,
                    "user_team": team,
                    "season": season,
                    "year": year,
                }
            )
        return out
