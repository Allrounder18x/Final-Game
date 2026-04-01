"""
Application service facade for Kivy/Android UI.
"""

from __future__ import annotations

import os
import threading
import uuid
import io
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, List, Optional

from cricket_manager.android.save_store import AndroidSaveStore
from cricket_manager.core.game_engine import GameEngine


class _ValueControl:
    """
    Service facade over GameEngine.
    Keeps UI logic out of the core simulation layer.
    """

    def __init__(self, value: Any) -> None:
        self._value = value

    def get(self) -> Any:
        return self._value

    def set(self, value: Any) -> None:
        self._value = value


class CricketAppService:
    """
    Service facade over GameEngine.
    Keeps UI logic out of the core simulation layer.
    """

    def __init__(self, app_storage_dir: Optional[str] = None) -> None:
        base_dir = app_storage_dir or os.path.join(os.getcwd(), "android_data")
        os.makedirs(base_dir, exist_ok=True)
        self.app_storage_dir = base_dir
        self.save_store = AndroidSaveStore(base_dir)
        self.engine: Optional[GameEngine] = None
        self.interactive_sessions: Dict[str, Dict[str, Any]] = {}
        self.last_season_outputs: Dict[str, Any] = {}
        self.season_jobs: Dict[str, Dict[str, Any]] = {}

    def init_new_game(self) -> GameEngine:
        self.engine = GameEngine()
        return self.engine

    def get_engine(self) -> GameEngine:
        if self.engine is None:
            self.engine = GameEngine()
        return self.engine

    def save_game(self, slot_name: str = "autosave") -> str:
        engine = self.get_engine()
        return self.save_store.save_engine(engine, slot_name)

    def load_game(self, slot_name_or_path: str = "autosave") -> str:
        engine = self.get_engine()
        return self.save_store.load_engine(engine, slot_name_or_path)

    def list_saves(self) -> List[Dict[str, Optional[str]]]:
        return self.save_store.list_saves()

    def get_fixtures(self, match_format: str) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        return engine.get_fixtures(match_format)

    def get_fixtures_filtered(
        self,
        match_format: str = "All",
        status: str = "All",
        team_filter: Optional[str] = None,
        tier_filter: int = 0,
        limit: int = 300,
    ) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        formats = ["T20", "ODI", "Test"] if match_format == "All" else [match_format]
        rows: List[Dict[str, Any]] = []
        for fmt in formats:
            for f in engine.get_fixtures(fmt):
                if status == "Pending" and f.get("completed"):
                    continue
                if status == "Completed" and not f.get("completed"):
                    continue
                if tier_filter > 0 and int(f.get("tier", 0) or 0) != tier_filter:
                    continue
                t1 = f.get("team1").name if f.get("team1") else f.get("home", "")
                t2 = f.get("team2").name if f.get("team2") else f.get("away", "")
                if team_filter and team_filter != "All Teams" and team_filter not in (t1, t2):
                    continue
                rows.append(f)
        return rows[:limit]

    def get_standings(self, match_format: str, tier_num: Optional[int] = None) -> Dict[str, Any]:
        engine = self.get_engine()
        if tier_num:
            return {
                "format": match_format,
                "tier": tier_num,
                "rows": engine.tier_manager.get_tier_standings(match_format, tier_num),
            }
        return {
            "format": match_format,
            "tiers": engine.tier_manager.get_all_standings(match_format),
        }

    def get_players(self, team_name: Optional[str] = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        players: List[Dict[str, Any]] = []
        for player, team in engine.get_all_players():
            if team_name and team.name != team_name:
                continue
            players.append(
                {
                    "team": team.name,
                    "name": getattr(player, "name", "Unknown"),
                    "role": getattr(player, "role", "Unknown"),
                    "age": getattr(player, "age", None),
                    "batting": getattr(player, "batting", None),
                    "bowling": getattr(player, "bowling", None),
                    "fielding": getattr(player, "fielding", None),
                }
            )
        return players

    def get_players_filtered(
        self,
        team_name: Optional[str] = None,
        search_text: str = "",
        role_filter: str = "All Roles",
        sort_key: str = "Name",
        limit: int = 600,
    ) -> List[Dict[str, Any]]:
        rows = self.get_players(team_name if team_name and team_name != "All Teams" else None)
        s = search_text.strip().lower()
        if s:
            rows = [r for r in rows if s in str(r.get("name", "")).lower()]
        if role_filter != "All Roles":
            rf = role_filter.lower()
            rows = [r for r in rows if rf in str(r.get("role", "")).lower()]
        if sort_key == "Batting":
            rows.sort(key=lambda x: int(x.get("batting") or 0), reverse=True)
        elif sort_key == "Bowling":
            rows.sort(key=lambda x: int(x.get("bowling") or 0), reverse=True)
        elif sort_key == "Age":
            rows.sort(key=lambda x: int(x.get("age") or 0))
        elif sort_key == "Team":
            rows.sort(key=lambda x: str(x.get("team", "")))
        else:
            rows.sort(key=lambda x: str(x.get("name", "")))
        return rows[:limit]

    def list_teams(self) -> List[str]:
        engine = self.get_engine()
        return [getattr(t, "name", "Unknown") for t in getattr(engine, "all_teams", [])]

    def get_player_profile(self, player_name: str) -> Optional[Dict[str, Any]]:
        for row in self.get_players():
            if row["name"] == player_name:
                return row
        return None

    def set_user_team(self, team_name: str) -> bool:
        engine = self.get_engine()
        team = engine.get_team_by_name(team_name)
        if team is None:
            return False
        engine.user_team = team
        return True

    def simulate_match(self, fixture: Dict[str, Any], match_format: str) -> Dict[str, Any]:
        # Android path uses legacy desktop simulators for match-accuracy parity.
        # Falls back to core engine fast simulator if anything fails.
        if match_format == "Test":
            result = self._simulate_match_with_legacy_test(fixture)
            if result:
                return result
        elif match_format in {"T20", "ODI"}:
            result = self._simulate_match_with_legacy_limited_overs(fixture, match_format)
            if result:
                return result

        engine = self.get_engine()
        result = engine.simulate_match(fixture, match_format, headless=True)
        return result or {}

    def simulate_season_chunk(self, match_format: str) -> Dict[str, Any]:
        engine = self.get_engine()
        result = engine.simulate_season(match_format, headless=True)
        self.last_season_outputs = {match_format: result}
        return result

    def get_league_table_rows(self, match_format: str, tier_num: int, season_year: Optional[int] = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        year = season_year if season_year is not None else engine.current_year
        return engine.get_league_season_table_rows(match_format, tier_num, year)

    def get_rankings(self, match_format: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "batting": self.get_top_players(match_format, "Batting", limit),
            "bowling": self.get_top_players(match_format, "Bowling", limit),
            "all_rounder": self.get_top_players(match_format, "All-Rounder", limit),
        }

    def get_top_players(self, match_format: str, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        rows = []
        for player, team, rating in engine.get_top_players(match_format, category, limit):
            rows.append(
                {
                    "name": getattr(player, "name", "Unknown"),
                    "team": getattr(team, "name", "Unknown"),
                    "rating": rating,
                    "role": getattr(player, "role", "Unknown"),
                }
            )
        return rows

    def get_statistics_snapshot(self, match_format: str) -> Dict[str, Any]:
        engine = self.get_engine()
        fixtures = engine.get_fixtures(match_format)
        completed = [f for f in fixtures if f.get("completed", False)]
        return {
            "format": match_format,
            "fixtures_total": len(fixtures),
            "fixtures_completed": len(completed),
            "season": engine.current_season,
            "year": engine.current_year,
        }

    def get_world_cup_history(self) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        return list(getattr(engine, "world_cup_history", []))

    def get_training_overview(self) -> Dict[str, Any]:
        engine = self.get_engine()
        user_team = getattr(engine, "user_team", None)
        training_system = getattr(engine, "training_system", None)
        points = None
        if user_team and training_system and hasattr(training_system, "team_training_points"):
            points = training_system.team_training_points.get(user_team.name)
        return {
            "user_team": getattr(user_team, "name", None),
            "training_points": points,
            "points_per_season": getattr(training_system, "training_points_per_season", None),
        }

    def get_settings(self) -> Dict[str, Any]:
        engine = self.get_engine()
        return {
            "difficulty": getattr(engine, "difficulty", "Normal"),
            "hide_batting_bowling_ratings": getattr(engine, "hide_batting_bowling_ratings", False),
            "simulation_settings": dict(getattr(engine, "simulation_settings", {})),
        }

    def update_settings(self, difficulty: Optional[str] = None, hide_ratings: Optional[bool] = None) -> Dict[str, Any]:
        engine = self.get_engine()
        if difficulty in {"Easy", "Normal", "Hard"}:
            engine.difficulty = difficulty
        if hide_ratings is not None:
            engine.hide_batting_bowling_ratings = bool(hide_ratings)
        return self.get_settings()

    def get_recent_season_summary(self, limit: int = 20) -> Dict[str, Any]:
        engine = self.get_engine()
        matches = list(getattr(engine, "season_matches", []))[-limit:]
        return {
            "season": getattr(engine, "current_season", None),
            "year": getattr(engine, "current_year", None),
            "recent_matches": matches,
            "season_awards": getattr(engine, "season_awards", {}),
        }

    def get_recent_season_summary_filtered(
        self,
        match_format: str = "All",
        team_filter: str = "All Teams",
        tier_filter: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        base = self.get_recent_season_summary(limit=2000)
        rows = list(base.get("recent_matches", []))
        if match_format != "All":
            rows = [m for m in rows if m.get("format") == match_format]
        if team_filter != "All Teams":
            rows = [m for m in rows if team_filter in (m.get("home", ""), m.get("away", ""))]
        if tier_filter > 0:
            rows = [m for m in rows if int(m.get("tier", 0) or 0) == tier_filter]
        base["recent_matches"] = rows[-limit:]
        return base

    def simulate_season_all_formats(self) -> Dict[str, Any]:
        outputs = {}
        for fmt in ("T20", "ODI", "Test"):
            outputs[fmt] = self.simulate_season_chunk(fmt)
        self.last_season_outputs = outputs
        return outputs

    def start_season_simulation_job(self, mode: str = "all", match_format: str = "T20") -> str:
        """
        Start asynchronous season simulation.
        mode: 'single' or 'all'
        """
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "mode": mode,
            "format": match_format,
            "running": True,
            "cancel_requested": False,
            "progress": 0.0,
            "message": "Queued",
            "error": None,
            "result": None,
        }
        self.season_jobs[job_id] = job

        def _worker():
            try:
                if mode == "single":
                    result = self._simulate_with_progress(job, match_format)
                else:
                    result = {}
                    for idx, fmt in enumerate(("T20", "ODI", "Test"), start=1):
                        if job["cancel_requested"]:
                            raise RuntimeError("Simulation cancelled")
                        job["message"] = f"Starting {fmt} season simulation ({idx}/3)"
                        partial = self._simulate_with_progress(job, fmt, phase=idx, total_phases=3)
                        result[fmt] = partial
                job["result"] = result
                self.last_season_outputs = result if isinstance(result, dict) else {}
                job["progress"] = 100.0
                job["message"] = "Completed"
            except Exception as exc:
                if str(exc) == "Simulation cancelled":
                    job["message"] = "Cancelled"
                else:
                    job["error"] = str(exc)
                    job["message"] = f"Failed: {exc}"
            finally:
                job["running"] = False

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return job_id

    def _simulate_with_progress(
        self,
        job: Dict[str, Any],
        match_format: str,
        phase: int = 1,
        total_phases: int = 1,
    ) -> Dict[str, Any]:
        engine = self.get_engine()

        def _progress_callback(message: str, progress_percent: float) -> None:
            if job["cancel_requested"]:
                raise RuntimeError("Simulation cancelled")
            bounded = max(0.0, min(100.0, float(progress_percent)))
            if total_phases <= 1:
                job["progress"] = bounded
            else:
                phase_start = (phase - 1) * (100.0 / total_phases)
                phase_span = 100.0 / total_phases
                job["progress"] = phase_start + (bounded / 100.0) * phase_span
            job["message"] = f"{match_format}: {message}"

        # Capture verbose engine prints to avoid terminal encoding issues on some
        # Windows environments during long season simulations.
        sink = io.StringIO()
        with redirect_stdout(sink), redirect_stderr(sink):
            return engine.simulate_season(match_format, headless=True, progress_callback=_progress_callback)

    def get_season_simulation_job_status(self, job_id: str) -> Dict[str, Any]:
        job = self.season_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        return {
            "id": job["id"],
            "mode": job["mode"],
            "format": job["format"],
            "running": job["running"],
            "progress": job["progress"],
            "message": job["message"],
            "error": job["error"],
            "has_result": job["result"] is not None,
        }

    def cancel_season_simulation_job(self, job_id: str) -> Dict[str, Any]:
        job = self.season_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        job["cancel_requested"] = True
        return {"ok": True, "id": job_id}

    def get_last_simulation_report(self) -> Dict[str, Any]:
        outputs = self.last_season_outputs or {}
        report: Dict[str, Any] = {"formats": {}, "combined": {"matches": 0, "retirements": 0, "promotions": 0}}
        for fmt, data in outputs.items():
            if not isinstance(data, dict):
                continue
            matches = list(data.get("matches", []) or [])
            retirements = list(data.get("retirements", []) or [])
            promotions = list(data.get("promotions", []) or [])
            awards = data.get("season_awards", {}) or {}
            report["formats"][fmt] = {
                "season": data.get("season"),
                "year": data.get("year"),
                "total_matches": data.get("total_matches"),
                "matches_sample": matches[-20:],
                "retirements": retirements[:20],
                "promotions": promotions[:20],
                "world_cup": data.get("world_cup"),
                "awards": awards,
            }
            report["combined"]["matches"] += int(data.get("total_matches") or 0)
            report["combined"]["retirements"] += len(retirements)
            report["combined"]["promotions"] += len(promotions)
        return report

    def get_recent_scorecards(self, limit: int = 20) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        items = []
        for key, scorecard in list(getattr(engine, "match_scorecards", {}).items())[-limit:]:
            team1, team2, season, match_format = key
            items.append(
                {
                    "team1": team1,
                    "team2": team2,
                    "season": season,
                    "format": match_format,
                    "man_of_the_match": scorecard.get("man_of_the_match"),
                    "innings": scorecard.get("innings", []),
                }
            )
        return items

    def get_select_xi(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        engine = self.get_engine()
        team = engine.get_team_by_name(team_name) if team_name else getattr(engine, "user_team", None)
        if team is None:
            return {"team": None, "xi": []}
        players = list(getattr(team, "players", []))
        ranked = sorted(
            players,
            key=lambda p: (getattr(p, "batting", 0) + getattr(p, "bowling", 0) + getattr(p, "fielding", 0)),
            reverse=True,
        )
        xi = []
        for p in ranked[:11]:
            xi.append(
                {
                    "name": getattr(p, "name", "Unknown"),
                    "role": getattr(p, "role", "Unknown"),
                    "batting": getattr(p, "batting", 0),
                    "bowling": getattr(p, "bowling", 0),
                    "fielding": getattr(p, "fielding", 0),
                }
            )
        return {"team": getattr(team, "name", None), "xi": xi}

    def _team_to_legacy_dict(self, team: Any) -> Dict[str, Any]:
        players = []
        for p in getattr(team, "players", []) or []:
            players.append(
                {
                    "name": getattr(p, "name", "Unknown"),
                    "role": getattr(p, "role", ""),
                    "batting": getattr(p, "batting", 0),
                    "bowling": getattr(p, "bowling", 0),
                    "fielding": getattr(p, "fielding", 0),
                    "age": getattr(p, "age", 0),
                    "bowling_movements": getattr(p, "bowling_movements", {}),
                    "playing_xi": bool(getattr(p, "playing_xi", False)),
                    "batting_position": getattr(p, "batting_position", None),
                }
            )
        return {"name": getattr(team, "name", "Unknown"), "players": players}

    def set_manual_xi(self, team_name: str, player_names: List[str]) -> Dict[str, Any]:
        engine = self.get_engine()
        team = engine.get_team_by_name(team_name)
        if team is None:
            return {"ok": False, "reason": "Team not found"}
        wanted = set(player_names[:11])
        position = 1
        for p in getattr(team, "players", []) or []:
            is_in = getattr(p, "name", None) in wanted
            setattr(p, "playing_xi", is_in)
            if is_in:
                setattr(p, "batting_position", position)
                position += 1
            else:
                setattr(p, "batting_position", None)
        return {"ok": True, "team": team_name, "selected_count": len(wanted)}

    def auto_select_xi_for_team(self, team_name: str) -> Dict[str, Any]:
        info = self.get_select_xi(team_name)
        team = info.get("team")
        xi = info.get("xi", [])
        if not team or not xi:
            return {"ok": False, "reason": "No team/xi available"}
        names = [p.get("name") for p in xi if p.get("name")]
        return self.set_manual_xi(team, names)

    def _simulate_match_with_legacy_limited_overs(self, fixture: Dict[str, Any], match_format: str) -> Dict[str, Any]:
        try:
            from t20oversimulation import T20Match  # type: ignore[import-not-found]

            team1_obj = fixture.get("team1")
            team2_obj = fixture.get("team2")
            if team1_obj is None or team2_obj is None:
                return {}

            pitch_conditions = fixture.get("pitch_conditions")
            if not pitch_conditions and fixture.get("pitch_bounce") is not None:
                pitch_conditions = {
                    "pitch_bounce": fixture.get("pitch_bounce", 5),
                    "pitch_spin": fixture.get("pitch_spin", 5),
                    "pitch_pace": fixture.get("pitch_pace", 5),
                }

            sim_adj_full = dict(getattr(self.get_engine(), "simulation_settings", {}))
            sim_adj = {
                "dot_adj": sim_adj_full.get(f"{match_format.lower()}_dot_adj", 0),
                "boundary_adj": sim_adj_full.get(f"{match_format.lower()}_boundary_adj", 0),
                "wicket_adj": sim_adj_full.get(f"{match_format.lower()}_wicket_adj", 0),
            }

            match = T20Match(
                None,
                self._team_to_legacy_dict(team1_obj),
                self._team_to_legacy_dict(team2_obj),
                match_format=match_format,
                headless=True,
                simulation_adjustments=sim_adj,
                pitch_conditions=pitch_conditions,
            )
            match.setup_match()
            # Headless fallback controls expected by simulate_ball()/quick_simulate_match()
            if not hasattr(match, "batting_slider"):
                match.batting_slider = _ValueControl(50)
            if not hasattr(match, "bowling_slider"):
                match.bowling_slider = _ValueControl(50)
            if not hasattr(match, "bowling_line_var"):
                match.bowling_line_var = _ValueControl("Good Length")
            if not hasattr(match, "field_setting_var"):
                match.field_setting_var = _ValueControl("Balanced")
            match.quick_simulate_match()
        except Exception:
            # Legacy Tk simulator can fail in some environments due GUI-grab constraints.
            # Caller can safely fall back to core simulator.
            return {}

        result_text = getattr(match, "result", None) or "Match Complete"
        fixture["completed"] = True
        fixture["winner"] = result_text
        fixture["margin"] = result_text
        return {
            "winner": result_text,
            "team1": getattr(team1_obj, "name", "Team 1"),
            "team2": getattr(team2_obj, "name", "Team 2"),
            "format": match_format,
            "margin": result_text,
            "scorecard": {
                "man_of_the_match": None,
                "innings": getattr(match, "innings_history", []),
                "legacy_engine": "t20oversimulation.py",
            },
        }

    def _simulate_match_with_legacy_test(self, fixture: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from test_match_enhanced import TestMatchSimulator  # type: ignore[import-not-found]
        except Exception:
            return {}

        team1_obj = fixture.get("team1")
        team2_obj = fixture.get("team2")
        if team1_obj is None or team2_obj is None:
            return {}

        pitch_conditions = fixture.get("pitch_conditions")
        if not pitch_conditions and fixture.get("pitch_bounce") is not None:
            pitch_conditions = {
                "pitch_bounce": fixture.get("pitch_bounce", 5),
                "pitch_spin": fixture.get("pitch_spin", 5),
                "pitch_pace": fixture.get("pitch_pace", 5),
            }

        sim_adj_full = dict(getattr(self.get_engine(), "simulation_settings", {}))
        sim_adj = {
            "dot_adj": sim_adj_full.get("test_dot_adj", 0),
            "boundary_adj": sim_adj_full.get("test_boundary_adj", 0),
            "wicket_adj": sim_adj_full.get("test_wicket_adj", 0),
        }

        team1 = self._team_to_legacy_dict(team1_obj)
        team2 = self._team_to_legacy_dict(team2_obj)
        simulator = TestMatchSimulator(
            team1,
            team2,
            parent_app=None,
            simulation_adjustments=sim_adj,
            pitch_conditions=pitch_conditions,
        )
        result_payload = simulator.quick_simulate()
        result_text = result_payload.get("result") or "Match Drawn"

        fixture["completed"] = True
        fixture["winner"] = result_payload.get("winner") or result_text
        fixture["margin"] = result_text
        return {
            "winner": result_payload.get("winner") or result_text,
            "team1": getattr(team1_obj, "name", "Team 1"),
            "team2": getattr(team2_obj, "name", "Team 2"),
            "format": "Test",
            "margin": result_text,
            "scorecard": {
                "man_of_the_match": None,
                "innings": result_payload.get("innings_data", []),
                "legacy_engine": "test_match_enhanced.py",
            },
        }

    def start_interactive_match(self, fixture: Dict[str, Any], match_format: str) -> Dict[str, Any]:
        team1_obj = fixture.get("team1")
        team2_obj = fixture.get("team2")
        if team1_obj is None or team2_obj is None:
            return {"error": "Invalid fixture teams"}

        session_id = str(uuid.uuid4())
        pitch_conditions = fixture.get("pitch_conditions")
        if not pitch_conditions and fixture.get("pitch_bounce") is not None:
            pitch_conditions = {
                "pitch_bounce": fixture.get("pitch_bounce", 5),
                "pitch_spin": fixture.get("pitch_spin", 5),
                "pitch_pace": fixture.get("pitch_pace", 5),
            }

        if match_format in {"T20", "ODI"}:
            from t20oversimulation import T20Match  # type: ignore[import-not-found]

            sim_adj_full = dict(getattr(self.get_engine(), "simulation_settings", {}))
            sim_adj = {
                "dot_adj": sim_adj_full.get(f"{match_format.lower()}_dot_adj", 0),
                "boundary_adj": sim_adj_full.get(f"{match_format.lower()}_boundary_adj", 0),
                "wicket_adj": sim_adj_full.get(f"{match_format.lower()}_wicket_adj", 0),
            }
            simulator = T20Match(
                None,
                self._team_to_legacy_dict(team1_obj),
                self._team_to_legacy_dict(team2_obj),
                match_format=match_format,
                headless=True,
                simulation_adjustments=sim_adj,
                pitch_conditions=pitch_conditions,
            )
            simulator.setup_match()
            # Headless fallback controls expected by simulate_ball()
            if not hasattr(simulator, "batting_slider"):
                simulator.batting_slider = _ValueControl(50)
            if not hasattr(simulator, "bowling_slider"):
                simulator.bowling_slider = _ValueControl(50)
            if not hasattr(simulator, "bowling_line_var"):
                simulator.bowling_line_var = _ValueControl("Good Length")
            if not hasattr(simulator, "field_setting_var"):
                simulator.field_setting_var = _ValueControl("Balanced")
            self.interactive_sessions[session_id] = {
                "format": match_format,
                "fixture": fixture,
                "simulator": simulator,
            }
            return {"session_id": session_id, "state": self._snapshot_t20(simulator)}

        if match_format == "Test":
            from test_match_enhanced import TestMatchSimulator  # type: ignore[import-not-found]

            sim_adj_full = dict(getattr(self.get_engine(), "simulation_settings", {}))
            sim_adj = {
                "dot_adj": sim_adj_full.get("test_dot_adj", 0),
                "boundary_adj": sim_adj_full.get("test_boundary_adj", 0),
                "wicket_adj": sim_adj_full.get("test_wicket_adj", 0),
            }
            simulator = TestMatchSimulator(
                self._team_to_legacy_dict(team1_obj),
                self._team_to_legacy_dict(team2_obj),
                parent_app=None,
                simulation_adjustments=sim_adj,
                pitch_conditions=pitch_conditions,
            )
            simulator.initialize_match()
            self.interactive_sessions[session_id] = {
                "format": "Test",
                "fixture": fixture,
                "simulator": simulator,
            }
            return {"session_id": session_id, "state": self._snapshot_test(simulator)}
        return {"error": f"Unsupported format: {match_format}"}

    def step_interactive_match(self, session_id: str, action: str) -> Dict[str, Any]:
        session = self.interactive_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        match_format = session["format"]
        simulator = session["simulator"]
        fixture = session["fixture"]

        if match_format in {"T20", "ODI"}:
            self._step_t20(simulator, action)
            if getattr(simulator, "match_ended", False):
                fixture["completed"] = True
                fixture["winner"] = getattr(simulator, "result", "Match Complete")
                fixture["margin"] = getattr(simulator, "result", "Match Complete")
            return {"session_id": session_id, "state": self._snapshot_t20(simulator)}

        self._step_test(simulator, action)
        if getattr(simulator, "match_ended", False):
            fixture["completed"] = True
            fixture["winner"] = getattr(simulator, "winner", None) or getattr(simulator, "result", "Match Drawn")
            fixture["margin"] = getattr(simulator, "result", "Match Drawn")
        return {"session_id": session_id, "state": self._snapshot_test(simulator)}

    def get_interactive_state(self, session_id: str) -> Dict[str, Any]:
        session = self.interactive_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        match_format = session["format"]
        simulator = session["simulator"]
        if match_format in {"T20", "ODI"}:
            return {"session_id": session_id, "state": self._snapshot_t20(simulator)}
        return {"session_id": session_id, "state": self._snapshot_test(simulator)}

    def set_limited_overs_tactics(
        self,
        session_id: str,
        batting_aggression: Optional[int] = None,
        bowling_aggression: Optional[int] = None,
        bowling_line: Optional[str] = None,
        field_setting: Optional[str] = None,
        bowler_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = self.interactive_sessions.get(session_id)
        if not session or session.get("format") not in {"T20", "ODI"}:
            return {"error": "Limited overs session not found"}
        sim = session["simulator"]
        if batting_aggression is not None:
            sim.batting_slider.set(max(0, min(100, int(batting_aggression))))
        if bowling_aggression is not None:
            sim.bowling_slider.set(max(0, min(100, int(bowling_aggression))))
        if bowling_line in {"Short", "Good Length", "Full"}:
            sim.bowling_line_var.set(bowling_line)
        if field_setting in {"Aggressive", "Balanced", "Defensive"}:
            sim.field_setting_var.set(field_setting)
        if bowler_name:
            for b in getattr(sim, "bowling_xi", []) or []:
                name = getattr(b, "name", b.get("name") if isinstance(b, dict) else None)
                if name == bowler_name:
                    sim.current_bowler = b
                    break
        return {"session_id": session_id, "state": self._snapshot_t20(sim)}

    def cycle_limited_overs_bowler(self, session_id: str) -> Dict[str, Any]:
        session = self.interactive_sessions.get(session_id)
        if not session or session.get("format") not in {"T20", "ODI"}:
            return {"error": "Limited overs session not found"}
        sim = session["simulator"]
        bowlers = list(getattr(sim, "bowling_xi", []) or [])
        if not bowlers:
            return {"session_id": session_id, "state": self._snapshot_t20(sim)}
        current_name = self._name_of(getattr(sim, "current_bowler", None))
        idx = 0
        for i, b in enumerate(bowlers):
            if self._name_of(b) == current_name:
                idx = i
                break
        sim.current_bowler = bowlers[(idx + 1) % len(bowlers)]
        return {"session_id": session_id, "state": self._snapshot_t20(sim)}

    def cycle_test_bowler(self, session_id: str) -> Dict[str, Any]:
        session = self.interactive_sessions.get(session_id)
        if not session or session.get("format") != "Test":
            return {"error": "Test session not found"}
        sim = session["simulator"]
        bowling_team = getattr(sim, "bowling_team", None)
        if not bowling_team:
            return {"session_id": session_id, "state": self._snapshot_test(sim)}
        bowlers = list(sim.get_playing_xi(bowling_team))
        if not bowlers:
            return {"session_id": session_id, "state": self._snapshot_test(sim)}
        current_name = self._name_of(getattr(sim, "current_bowler", None))
        idx = 0
        for i, b in enumerate(bowlers):
            if self._name_of(b) == current_name:
                idx = i
                break
        sim.current_bowler = bowlers[(idx + 1) % len(bowlers)]
        return {"session_id": session_id, "state": self._snapshot_test(sim)}

    def _step_t20(self, simulator: Any, action: str) -> None:
        if getattr(simulator, "match_ended", False):
            return
        if action == "ball":
            simulator.bowl_delivery()
            return
        if action == "over":
            simulator.bowl_over()
            return
        if action == "end":
            guard = 0
            while not getattr(simulator, "match_ended", False) and guard < 1000:
                simulator.bowl_over()
                guard += 1
            return
        simulator.bowl_delivery()

    def _step_test(self, simulator: Any, action: str) -> None:
        if getattr(simulator, "match_ended", False):
            return
        if action == "ball":
            simulator.simulate_ball()
            return
        if action == "over":
            # Bowl at least one over; no-balls can extend past 6 deliveries.
            start_overs = getattr(simulator, "current_overs", 0)
            guard = 0
            while not getattr(simulator, "match_ended", False) and getattr(simulator, "current_overs", 0) == start_overs and guard < 24:
                simulator.simulate_ball()
                guard += 1
            return
        if action == "session":
            start_session = getattr(simulator, "current_session", 1)
            guard = 0
            while not getattr(simulator, "match_ended", False) and getattr(simulator, "current_session", 1) == start_session and guard < 2200:
                simulator.simulate_ball()
                guard += 1
            return
        if action == "day":
            start_day = getattr(simulator, "current_day", 1)
            guard = 0
            while not getattr(simulator, "match_ended", False) and getattr(simulator, "current_day", 1) == start_day and guard < 7000:
                simulator.simulate_ball()
                guard += 1
            return
        if action == "end":
            guard = 0
            while not getattr(simulator, "match_ended", False) and guard < 30000:
                simulator.simulate_ball()
                guard += 1
            return
        simulator.simulate_ball()

    def _snapshot_t20(self, simulator: Any) -> Dict[str, Any]:
        batting_table = []
        bowling_table = []
        for name, stats in (getattr(simulator, "match_stats", {}) or {}).items():
            bat = stats.get("batting", {})
            bowl = stats.get("bowling", {})
            batting_table.append(
                {
                    "name": name,
                    "runs": bat.get("runs", 0),
                    "balls": bat.get("balls", 0),
                    "fours": bat.get("fours", 0),
                    "sixes": bat.get("sixes", 0),
                    "dismissal": bat.get("dismissal"),
                }
            )
            bowling_table.append(
                {
                    "name": name,
                    "balls": bowl.get("balls", 0),
                    "runs": bowl.get("runs", 0),
                    "wickets": bowl.get("wickets", 0),
                    "maidens": bowl.get("maidens", 0),
                }
            )
        batting_table.sort(key=lambda r: (r["runs"], -r["balls"]), reverse=True)
        bowling_table.sort(key=lambda r: (r["wickets"], -r["runs"]), reverse=True)
        return {
            "engine": "t20oversimulation.py",
            "format": getattr(simulator, "match_format", "T20"),
            "innings": getattr(simulator, "current_innings", 1),
            "runs": getattr(simulator, "total_runs", 0),
            "wickets": getattr(simulator, "total_wickets", 0),
            "overs": getattr(simulator, "total_overs", 0),
            "balls": getattr(simulator, "total_balls", 0),
            "target": getattr(simulator, "target", None),
            "striker": self._name_of(getattr(simulator, "striker", None)),
            "non_striker": self._name_of(getattr(simulator, "non_striker", None)),
            "current_bowler": self._name_of(getattr(simulator, "current_bowler", None)),
            "batting_aggression": int(getattr(simulator, "batting_slider", _ValueControl(50)).get()),
            "bowling_aggression": int(getattr(simulator, "bowling_slider", _ValueControl(50)).get()),
            "bowling_line": getattr(simulator, "bowling_line_var", _ValueControl("Good Length")).get(),
            "field_setting": getattr(simulator, "field_setting_var", _ValueControl("Balanced")).get(),
            "result": getattr(simulator, "result", None),
            "match_ended": bool(getattr(simulator, "match_ended", False)),
            "commentary_tail": list(getattr(simulator, "commentary_log", [])[-8:]),
            "batting_table_top": batting_table[:8],
            "bowling_table_top": bowling_table[:8],
        }

    def _snapshot_test(self, simulator: Any) -> Dict[str, Any]:
        score_lines = []
        for idx, inn in enumerate(getattr(simulator, "innings_data", [])[-4:], start=1):
            score_lines.append(
                f"Inn{idx}: {inn.get('batting_team', '?')} "
                f"{inn.get('score', 0)}/{inn.get('wickets', 0)}"
            )
        bat_stats = getattr(simulator, "batting_stats", {}) or {}
        bowl_stats = getattr(simulator, "bowling_stats", {}) or {}
        batting_table = []
        for name, s in bat_stats.items():
            batting_table.append(
                {
                    "name": name,
                    "runs": s.get("runs", 0),
                    "balls": s.get("balls", 0),
                    "fours": s.get("fours", 0),
                    "sixes": s.get("sixes", 0),
                    "dismissal": s.get("dismissal"),
                }
            )
        bowling_table = []
        for name, s in bowl_stats.items():
            bowling_table.append(
                {
                    "name": name,
                    "overs": s.get("overs", 0),
                    "runs": s.get("runs", 0),
                    "wickets": s.get("wickets", 0),
                    "maidens": s.get("maidens", 0),
                }
            )
        batting_table.sort(key=lambda r: (r["runs"], -r["balls"]), reverse=True)
        bowling_table.sort(key=lambda r: (r["wickets"], -r["runs"]), reverse=True)
        return {
            "engine": "test_match_enhanced.py",
            "format": "Test",
            "innings": getattr(simulator, "current_innings", 1),
            "day": getattr(simulator, "current_day", 1),
            "session": getattr(simulator, "current_session", 1),
            "runs": getattr(simulator, "current_score", 0),
            "wickets": getattr(simulator, "current_wickets", 0),
            "overs": getattr(simulator, "current_overs", 0),
            "balls": getattr(simulator, "current_balls", 0),
            "striker": self._name_of(getattr(simulator, "striker", None)),
            "non_striker": self._name_of(getattr(simulator, "non_striker", None)),
            "current_bowler": self._name_of(getattr(simulator, "current_bowler", None)),
            "result": getattr(simulator, "result", None),
            "winner": getattr(simulator, "winner", None),
            "match_ended": bool(getattr(simulator, "match_ended", False)),
            "innings_summary": score_lines,
            "commentary_tail": list(getattr(simulator, "commentary", [])[-8:]),
            "batting_table_top": batting_table[:8],
            "bowling_table_top": bowling_table[:8],
            "fow_tail": list(getattr(simulator, "fow", [])[-6:]),
        }

    def _name_of(self, player: Any) -> str:
        if player is None:
            return "Unknown"
        if hasattr(player, "name"):
            return str(getattr(player, "name"))
        if isinstance(player, dict):
            return str(player.get("name", "Unknown"))
        return str(player)
