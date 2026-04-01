"""
Android parity smoke test for service wiring.

This test validates that major Android service integrations are callable and
produce sane outputs. It is intentionally lightweight but touches critical
paths, including legacy match engines and season simulation jobs.
"""

from __future__ import annotations

import os
import sys
import time


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "DATA")
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)

from cricket_manager.android.service_facade import CricketAppService


def _assert(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def run() -> None:
    service = CricketAppService(app_storage_dir=os.path.join(PROJECT_ROOT, "android_runtime_test"))
    engine = service.init_new_game()
    _assert(engine is not None, "Engine not initialized")
    _assert(len(service.list_teams()) > 0, "No teams loaded")

    # Team selection + player filters
    team_name = service.list_teams()[0]
    _assert(service.set_user_team(team_name), "Failed to set user team")
    players = service.get_players_filtered(team_name=team_name, search_text="", role_filter="All Roles", sort_key="Name", limit=50)
    _assert(len(players) > 0, "No players returned for user team")

    # XI flow
    xi = service.get_select_xi(team_name)
    _assert(len(xi.get("xi", [])) == 11, "XI selection did not return 11")
    apply_res = service.auto_select_xi_for_team(team_name)
    _assert(bool(apply_res.get("ok")), "Failed to apply XI")

    # Fixture filtering
    pending_t20 = service.get_fixtures_filtered(match_format="T20", status="Pending", team_filter="All Teams", tier_filter=0, limit=20)
    _assert(len(pending_t20) > 0, "No pending T20 fixtures found")

    # Interactive limited-overs session + tactics
    lo_fixture = pending_t20[0]
    lo_start = service.start_interactive_match(lo_fixture, "T20")
    sid = lo_start.get("session_id")
    _assert(bool(sid), "Failed to start T20 interactive session")
    service.set_limited_overs_tactics(sid, batting_aggression=70, bowling_aggression=40, bowling_line="Full", field_setting="Aggressive")
    lo_step = service.step_interactive_match(sid, "ball")
    _assert("state" in lo_step, "No state after T20 ball step")
    service.cycle_limited_overs_bowler(sid)

    # Interactive test session
    pending_test = service.get_fixtures_filtered(match_format="Test", status="Pending", team_filter="All Teams", tier_filter=0, limit=120)
    pending_test = [f for f in pending_test if f.get("team1") is not None and f.get("team2") is not None]
    _assert(len(pending_test) > 0, "No pending Test fixtures with valid teams found")
    test_start = service.start_interactive_match(pending_test[0], "Test")
    test_sid = test_start.get("session_id")
    _assert(bool(test_sid), "Failed to start Test interactive session")
    service.step_interactive_match(test_sid, "ball")
    service.cycle_test_bowler(test_sid)

    # Direct legacy-backed quick match sim
    odi_candidates = service.get_fixtures_filtered("ODI", "Pending", "All Teams", 0, 120)
    odi_candidates = [f for f in odi_candidates if f.get("team1") is not None and f.get("team2") is not None]
    _assert(len(odi_candidates) > 0, "No valid ODI fixtures for legacy path test")
    quick_result = service.simulate_match(odi_candidates[0], "ODI")
    _assert(bool(quick_result), "ODI quick simulation returned empty result")

    # Save/load path
    save_path = service.save_game("smoke_autosave")
    _assert(os.path.exists(save_path), "Save file not created")
    fmt = service.load_game("smoke_autosave")
    _assert(fmt in {"json", "pickle"}, "Unexpected load format")

    # Background season job (single format for runtime)
    job_id = service.start_season_simulation_job(mode="single", match_format="T20")
    _assert(bool(job_id), "Failed to start background season job")
    deadline = time.time() + 120
    status = {}
    while time.time() < deadline:
        status = service.get_season_simulation_job_status(job_id)
        if not status.get("running"):
            break
        time.sleep(0.5)
    _assert(not status.get("running"), "Season simulation job timed out")
    _assert(not status.get("error"), f"Season simulation job failed: {status.get('error')}")

    # Summary/report filters
    summary = service.get_recent_season_summary_filtered(match_format="T20", team_filter="All Teams", tier_filter=0, limit=30)
    _assert("recent_matches" in summary, "Filtered summary missing recent_matches")
    report = service.get_last_simulation_report()
    _assert("formats" in report, "Missing simulation report")

    print("ANDROID_PARITY_SMOKE_TEST: PASS")


if __name__ == "__main__":
    run()
