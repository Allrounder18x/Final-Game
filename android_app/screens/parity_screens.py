from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner


class ParityBaseScreen(Screen):
    screen_title = "Parity Screen"
    screen_name = "parity"

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        root = BoxLayout(orientation="vertical", spacing=8, padding=10)
        self.root = root
        root.add_widget(Label(text=self.screen_title, size_hint_y=None, height=40))
        self.content = Label(text="", halign="left", valign="top")
        root.add_widget(self.content)
        nav = BoxLayout(size_hint_y=None, height=44, spacing=6)
        for dest in ("dashboard", "fixtures", "standings", "players"):
            nav.add_widget(Button(text=dest, on_press=lambda _btn, d=dest: self._go(d)))
        root.add_widget(nav)
        self.add_widget(root)

    def _go(self, dest: str):
        if self.manager and dest in self.manager.screen_names:
            self.manager.current = dest

    def on_pre_enter(self, *args):
        self.refresh()
        return super().on_pre_enter(*args)

    def refresh(self):
        self.content.text = "No data available."


class LeaguesViewScreen(ParityBaseScreen):
    screen_title = "Leagues View"
    screen_name = "leagues_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        ctl = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.current_format = "T20"
        self.current_tier = 1
        for fmt in ("T20", "ODI", "Test"):
            ctl.add_widget(Button(text=fmt, on_press=lambda _b, f=fmt: self._set_format(f)))
        for tier in (1, 2, 3, 4):
            ctl.add_widget(Button(text=f"T{tier}", on_press=lambda _b, t=tier: self._set_tier(t)))
        self.root.add_widget(ctl, index=1)

    def _set_format(self, match_format: str):
        self.current_format = match_format
        self.refresh()

    def _set_tier(self, tier: int):
        self.current_tier = tier
        self.refresh()

    def refresh(self):
        rows = self.service.get_league_table_rows(self.current_format, self.current_tier)
        lines = [f"{self.current_format} Tier {self.current_tier} League Table"]
        for i, row in enumerate(rows, start=1):
            lines.append(
                f"{i}. {row.get('team_name', '-')}: "
                f"Pts {row.get('points', 0)} W {row.get('wins', 0)} L {row.get('losses', 0)} D {row.get('draws', 0)}"
            )
        self.content.text = "\n".join(lines) if lines else "No league table rows."


class StatisticsScreen(ParityBaseScreen):
    screen_title = "Statistics View"
    screen_name = "statistics_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        ctl = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.current_format = "T20"
        for fmt in ("T20", "ODI", "Test"):
            ctl.add_widget(Button(text=fmt, on_press=lambda _b, f=fmt: self._set_format(f)))
        self.root.add_widget(ctl, index=1)

    def _set_format(self, match_format: str):
        self.current_format = match_format
        self.refresh()

    def refresh(self):
        snap = self.service.get_statistics_snapshot(self.current_format)
        self.content.text = (
            f"Format: {snap['format']}\n"
            f"Season: {snap['season']}  Year: {snap['year']}\n"
            f"Fixtures: {snap['fixtures_completed']}/{snap['fixtures_total']} completed\n"
        )


class RankingsScreen(ParityBaseScreen):
    screen_title = "Rankings View"
    screen_name = "rankings_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        ctl = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.current_format = "T20"
        for fmt in ("T20", "ODI", "Test"):
            ctl.add_widget(Button(text=fmt, on_press=lambda _b, f=fmt: self._set_format(f)))
        self.root.add_widget(ctl, index=1)

    def _set_format(self, match_format: str):
        self.current_format = match_format
        self.refresh()

    def refresh(self):
        data = self.service.get_rankings(self.current_format, limit=8)
        lines = [f"{self.current_format} Rankings"]
        lines.append("Top Batting:")
        for row in data["batting"][:5]:
            lines.append(f"- {row['name']} ({row['team']}) {row['rating']}")
        lines.append("Top Bowling:")
        for row in data["bowling"][:5]:
            lines.append(f"- {row['name']} ({row['team']}) {row['rating']}")
        self.content.text = "\n".join(lines)


class WorldCupScreen(ParityBaseScreen):
    screen_title = "World Cup View"
    screen_name = "world_cup_view"

    def refresh(self):
        history = self.service.get_world_cup_history()
        if not history:
            self.content.text = "No world cup history yet."
            return
        lines = ["World Cup History"]
        for item in history[-10:]:
            lines.append(str(item))
        self.content.text = "\n".join(lines)


class TrainingScreen(ParityBaseScreen):
    screen_title = "Training View"
    screen_name = "training_view"

    def refresh(self):
        ov = self.service.get_training_overview()
        self.content.text = (
            f"Team: {ov.get('user_team') or 'Not selected'}\n"
            f"Training Points: {ov.get('training_points')}\n"
            f"Points/Season: {ov.get('points_per_season')}\n"
        )


class SettingsScreen(ParityBaseScreen):
    screen_title = "Settings View"
    screen_name = "settings_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        actions = BoxLayout(size_hint_y=None, height=40, spacing=4)
        actions.add_widget(Button(text="Easy", on_press=lambda _b: self._set_diff("Easy")))
        actions.add_widget(Button(text="Normal", on_press=lambda _b: self._set_diff("Normal")))
        actions.add_widget(Button(text="Hard", on_press=lambda _b: self._set_diff("Hard")))
        actions.add_widget(Button(text="Toggle Hide Ratings", on_press=lambda _b: self._toggle_hide()))
        actions.add_widget(Button(text="Save", on_press=lambda _b: self._save()))
        actions.add_widget(Button(text="Load", on_press=lambda _b: self._load()))
        self.root.add_widget(actions, index=1)

    def _set_diff(self, difficulty: str):
        self.service.update_settings(difficulty=difficulty)
        self.refresh()

    def _toggle_hide(self):
        s = self.service.get_settings()
        self.service.update_settings(hide_ratings=not bool(s.get("hide_batting_bowling_ratings")))
        self.refresh()

    def _save(self):
        self.service.save_game("autosave")
        self.refresh()

    def _load(self):
        try:
            self.service.load_game("autosave")
        except Exception:
            pass
        self.refresh()

    def refresh(self):
        s = self.service.get_settings()
        self.content.text = (
            f"Difficulty: {s.get('difficulty')}\n"
            f"Hide Ratings: {s.get('hide_batting_bowling_ratings')}\n"
            f"Saves: {len(self.service.list_saves())}\n"
        )


class SeasonSummaryScreen(ParityBaseScreen):
    screen_title = "Season Summary View"
    screen_name = "season_summary_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.filter_format = "All"
        self.filter_team = "All Teams"
        self.filter_tier = 0
        self.active_job_id = None
        actions = BoxLayout(size_hint_y=None, height=40, spacing=4)
        actions.add_widget(Button(text="Sim T20 Chunk", on_press=lambda _b: self._sim("T20")))
        actions.add_widget(Button(text="Sim ODI Chunk", on_press=lambda _b: self._sim("ODI")))
        actions.add_widget(Button(text="Sim Test Chunk", on_press=lambda _b: self._sim("Test")))
        actions.add_widget(Button(text="Sim All", on_press=lambda _b: self._sim_all()))
        self.root.add_widget(actions, index=1)
        job_row = BoxLayout(size_hint_y=None, height=40, spacing=4)
        job_row.add_widget(Button(text="Start BG Sim Format", on_press=lambda _b: self._start_bg_single()))
        job_row.add_widget(Button(text="Start BG Sim All", on_press=lambda _b: self._start_bg_all()))
        job_row.add_widget(Button(text="Poll Progress", on_press=lambda _b: self._poll_job()))
        job_row.add_widget(Button(text="Cancel BG Sim", on_press=lambda _b: self._cancel_job()))
        self.root.add_widget(job_row, index=2)
        filters = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.fmt_spinner = Spinner(text="All", values=("All", "T20", "ODI", "Test"))
        self.fmt_spinner.bind(text=lambda _s, v: self._set_format(v))
        filters.add_widget(self.fmt_spinner)
        self.tier_spinner = Spinner(text="Tier 0", values=("Tier 0", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"))
        self.tier_spinner.bind(text=lambda _s, v: self._set_tier(v))
        filters.add_widget(self.tier_spinner)
        self.team_spinner = Spinner(text="All Teams", values=("All Teams",))
        self.team_spinner.bind(text=lambda _s, v: self._set_team(v))
        filters.add_widget(self.team_spinner)
        self.root.add_widget(filters, index=3)

    def _sim(self, match_format: str):
        self.service.simulate_season_chunk(match_format)
        self.refresh()

    def _sim_all(self):
        self.service.simulate_season_all_formats()
        self.refresh()

    def _start_bg_single(self):
        self.active_job_id = self.service.start_season_simulation_job(mode="single", match_format=self.filter_format if self.filter_format != "All" else "T20")
        self.refresh()

    def _start_bg_all(self):
        self.active_job_id = self.service.start_season_simulation_job(mode="all")
        self.refresh()

    def _poll_job(self):
        if not self.active_job_id:
            self.refresh()
            return
        self.refresh()

    def _cancel_job(self):
        if self.active_job_id:
            self.service.cancel_season_simulation_job(self.active_job_id)
        self.refresh()

    def _set_format(self, match_format: str):
        self.filter_format = match_format
        self.refresh()

    def _set_team(self, team: str):
        self.filter_team = team
        self.refresh()

    def _set_tier(self, tier_text: str):
        self.filter_tier = int(tier_text.split()[-1])
        self.refresh()

    def refresh(self):
        teams = ["All Teams"] + self.service.list_teams()
        self.team_spinner.values = tuple(teams)
        if self.team_spinner.text not in teams:
            self.team_spinner.text = "All Teams"
        summary = self.service.get_recent_season_summary_filtered(
            match_format=self.filter_format,
            team_filter=self.filter_team,
            tier_filter=self.filter_tier,
            limit=30,
        )
        lines = [f"Season {summary.get('season')} ({summary.get('year')}) - Recent Matches"]
        if self.active_job_id:
            st = self.service.get_season_simulation_job_status(self.active_job_id)
            if not st.get("error"):
                lines.append(
                    f"BG Job {self.active_job_id[:8]}: {st.get('message')} | "
                    f"{st.get('progress', 0):.1f}% | running={st.get('running')}"
                )
            else:
                lines.append(f"BG Job error: {st.get('error')}")
        awards = summary.get("season_awards", {}) or {}
        if awards:
            lines.append(
                f"Awards: Batter={awards.get('batter')} | Bowler={awards.get('bowler')} | Young={awards.get('young_player')}"
            )
        for row in summary.get("recent_matches", []):
            lines.append(
                f"- {row.get('home')} vs {row.get('away')} | "
                f"{row.get('winner')} {row.get('margin', '')}"
            )
        report = self.service.get_last_simulation_report()
        formats = report.get("formats", {})
        if formats:
            lines.append("")
            lines.append("Last Simulation Report:")
            for fmt, data in formats.items():
                lines.append(
                    f"[{fmt}] matches={data.get('total_matches')} "
                    f"retirements={len(data.get('retirements', []))} "
                    f"promotions={len(data.get('promotions', []))}"
                )
                wc = data.get("world_cup")
                if wc:
                    lines.append(f"  World Cup: {wc}")
        self.content.text = "\n".join(lines) if len(lines) > 1 else "No season matches tracked yet."


class MatchScorecardScreen(ParityBaseScreen):
    screen_title = "Match Scorecard View"
    screen_name = "match_scorecard_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.current_index = 0
        controls = BoxLayout(size_hint_y=None, height=40, spacing=4)
        controls.add_widget(Button(text="Prev", on_press=lambda _b: self._move(-1)))
        controls.add_widget(Button(text="Next", on_press=lambda _b: self._move(1)))
        self.root.add_widget(controls, index=1)
        # Use scroll for potentially longer scorecard preview.
        self.root.remove_widget(self.content)
        self.scroll_content = Label(text="", halign="left", valign="top", size_hint_y=None)
        self.scroll_content.bind(texture_size=self.scroll_content.setter("size"))
        sv = ScrollView()
        sv.add_widget(self.scroll_content)
        self.root.add_widget(sv, index=1)

    def _move(self, delta: int):
        rows = self.service.get_recent_scorecards(limit=30)
        if not rows:
            self.current_index = 0
            self.refresh()
            return
        self.current_index = max(0, min(len(rows) - 1, self.current_index + delta))
        self.refresh()

    def refresh(self):
        rows = self.service.get_recent_scorecards(limit=30)
        if not rows:
            self.scroll_content.text = "No scorecards available yet."
            return
        self.current_index = max(0, min(len(rows) - 1, self.current_index))
        row = rows[self.current_index]
        lines = [
            f"Scorecard {self.current_index + 1}/{len(rows)}",
            f"S{row['season']} {row['format']}: {row['team1']} vs {row['team2']}",
            f"POTM: {row.get('man_of_the_match')}",
        ]
        innings = row.get("innings", [])
        if innings:
            lines.append("Innings:")
            for idx, inn in enumerate(innings, start=1):
                total_runs = inn.get("total_runs", inn.get("score", 0))
                wkts = inn.get("wickets_lost", inn.get("wickets", 0))
                overs = inn.get("overs", "")
                lines.append(
                    f"- {idx}) {inn.get('batting_team')} {total_runs}/{wkts} {overs}"
                )
        self.scroll_content.text = "\n".join(lines)


class SelectXIScreen(ParityBaseScreen):
    screen_title = "Select XI View"
    screen_name = "select_xi_view"

    def refresh(self):
        info = self.service.get_select_xi()
        if not info.get("team"):
            self.content.text = "Select a user team first."
            return
        lines = [f"Suggested XI - {info['team']}"]
        for i, p in enumerate(info["xi"], start=1):
            lines.append(
                f"{i}. {p['name']} ({p['role']}) "
                f"B{p['batting']} Bo{p['bowling']} F{p['fielding']}"
            )
        lines.append("")
        lines.append("Tap 'Apply Suggested XI' to force this XI for legacy interactive match engines.")
        self.content.text = "\n".join(lines)

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        controls = BoxLayout(size_hint_y=None, height=40, spacing=4)
        controls.add_widget(Button(text="Apply Suggested XI", on_press=lambda _b: self._apply()))
        controls.add_widget(Button(text="Refresh", on_press=lambda _b: self.refresh()))
        self.root.add_widget(controls, index=1)

    def _apply(self):
        engine = self.service.get_engine()
        if not getattr(engine, "user_team", None):
            self.content.text = "Select a user team first."
            return
        result = self.service.auto_select_xi_for_team(engine.user_team.name)
        if result.get("ok"):
            self.refresh()
        else:
            self.content.text = f"Failed to apply XI: {result.get('reason')}"


class T20InteractiveScreen(ParityBaseScreen):
    screen_title = "T20/ODI Interactive Engine View"
    screen_name = "t20_interactive_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.session_id = None
        self.current_format = "T20"
        actions = BoxLayout(size_hint_y=None, height=40, spacing=4)
        actions.add_widget(Button(text="Start T20", on_press=lambda _b: self._start("T20")))
        actions.add_widget(Button(text="Start ODI", on_press=lambda _b: self._start("ODI")))
        actions.add_widget(Button(text="Ball", on_press=lambda _b: self._step("ball")))
        actions.add_widget(Button(text="Over", on_press=lambda _b: self._step("over")))
        actions.add_widget(Button(text="To End", on_press=lambda _b: self._step("end")))
        self.root.add_widget(actions, index=1)
        tactics_1 = BoxLayout(size_hint_y=None, height=40, spacing=4)
        tactics_1.add_widget(Button(text="Bat Agg +10", on_press=lambda _b: self._tactic("bat_up")))
        tactics_1.add_widget(Button(text="Bat Agg -10", on_press=lambda _b: self._tactic("bat_down")))
        tactics_1.add_widget(Button(text="Bowl Agg +10", on_press=lambda _b: self._tactic("bowl_up")))
        tactics_1.add_widget(Button(text="Bowl Agg -10", on_press=lambda _b: self._tactic("bowl_down")))
        self.root.add_widget(tactics_1, index=2)
        tactics_2 = BoxLayout(size_hint_y=None, height=40, spacing=4)
        tactics_2.add_widget(Button(text="Line Short", on_press=lambda _b: self._line("Short")))
        tactics_2.add_widget(Button(text="Line Good", on_press=lambda _b: self._line("Good Length")))
        tactics_2.add_widget(Button(text="Line Full", on_press=lambda _b: self._line("Full")))
        tactics_2.add_widget(Button(text="Field Agg", on_press=lambda _b: self._field("Aggressive")))
        tactics_2.add_widget(Button(text="Field Bal", on_press=lambda _b: self._field("Balanced")))
        tactics_2.add_widget(Button(text="Field Def", on_press=lambda _b: self._field("Defensive")))
        tactics_2.add_widget(Button(text="Next Bowler", on_press=lambda _b: self._next_bowler()))
        self.root.add_widget(tactics_2, index=3)

    def _start(self, match_format: str):
        self.current_format = match_format
        fixtures = self.service.get_fixtures(match_format)
        target = next(
            (
                f
                for f in fixtures
                if not f.get("completed")
                and f.get("team1") is not None
                and f.get("team2") is not None
            ),
            None,
        )
        if not target:
            self.content.text = f"No pending {match_format} fixtures with valid teams."
            return
        payload = self.service.start_interactive_match(target, match_format)
        self.session_id = payload.get("session_id")
        self._render_state(payload.get("state", {}))

    def _step(self, action: str):
        if not self.session_id:
            self.content.text = "Start a T20/ODI interactive match first."
            return
        payload = self.service.step_interactive_match(self.session_id, action)
        self._render_state(payload.get("state", {}))

    def _tactic(self, mode: str):
        if not self.session_id:
            self.content.text = "Start a T20/ODI interactive match first."
            return
        state = self.service.get_interactive_state(self.session_id).get("state", {})
        bat = int(state.get("batting_aggression", 50))
        bowl = int(state.get("bowling_aggression", 50))
        if mode == "bat_up":
            bat += 10
        elif mode == "bat_down":
            bat -= 10
        elif mode == "bowl_up":
            bowl += 10
        elif mode == "bowl_down":
            bowl -= 10
        payload = self.service.set_limited_overs_tactics(
            self.session_id,
            batting_aggression=bat,
            bowling_aggression=bowl,
        )
        self._render_state(payload.get("state", {}))

    def _line(self, bowling_line: str):
        if not self.session_id:
            self.content.text = "Start a T20/ODI interactive match first."
            return
        payload = self.service.set_limited_overs_tactics(self.session_id, bowling_line=bowling_line)
        self._render_state(payload.get("state", {}))

    def _field(self, setting: str):
        if not self.session_id:
            self.content.text = "Start a T20/ODI interactive match first."
            return
        payload = self.service.set_limited_overs_tactics(self.session_id, field_setting=setting)
        self._render_state(payload.get("state", {}))

    def _next_bowler(self):
        if not self.session_id:
            self.content.text = "Start a T20/ODI interactive match first."
            return
        payload = self.service.cycle_limited_overs_bowler(self.session_id)
        self._render_state(payload.get("state", {}))

    def _render_state(self, state):
        commentary = state.get("commentary_tail", [])
        commentary_text = "\n".join([f"- {c}" for c in commentary[-6:]]) if commentary else "-"
        batting_rows = state.get("batting_table_top", [])
        bowling_rows = state.get("bowling_table_top", [])
        batting_text = "\n".join(
            [f"- {r['name']} {r['runs']}({r['balls']}) 4s:{r['fours']} 6s:{r['sixes']}" for r in batting_rows[:5]]
        ) or "-"
        bowling_text = "\n".join(
            [f"- {r['name']} {r['wickets']}/{r['runs']} balls:{r['balls']}" for r in bowling_rows[:5]]
        ) or "-"
        self.content.text = (
            f"Engine: {state.get('engine')}\n"
            f"Format: {state.get('format')}\n"
            f"Innings: {state.get('innings')}  Score: {state.get('runs')}/{state.get('wickets')}\n"
            f"Overs: {state.get('overs')}.{state.get('balls')}  Target: {state.get('target')}\n"
            f"Batters: {state.get('striker')}* / {state.get('non_striker')}\n"
            f"Bowler: {state.get('current_bowler')}\n"
            f"Tactics: BatAgg {state.get('batting_aggression')} | BowlAgg {state.get('bowling_aggression')} | "
            f"Line {state.get('bowling_line')} | Field {state.get('field_setting')}\n"
            f"Result: {state.get('result')}\n"
            f"Ended: {state.get('match_ended')}\n"
            f"Top Batting:\n{batting_text}\n"
            f"Top Bowling:\n{bowling_text}\n"
            f"Commentary:\n{commentary_text}"
        )

    def refresh(self):
        self.content.text = (
            "This screen uses legacy limited-overs engine backend for accuracy:\n"
            "- DATA/t20oversimulation.py\n"
            "Use Start -> Ball/Over/To End for interactive control."
        )


class TestInteractiveScreen(ParityBaseScreen):
    screen_title = "Test Interactive Engine View"
    screen_name = "test_interactive_view"

    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.session_id = None
        actions = BoxLayout(size_hint_y=None, height=40, spacing=4)
        actions.add_widget(Button(text="Start Test", on_press=lambda _b: self._start()))
        actions.add_widget(Button(text="Ball", on_press=lambda _b: self._step("ball")))
        actions.add_widget(Button(text="Over", on_press=lambda _b: self._step("over")))
        actions.add_widget(Button(text="Session", on_press=lambda _b: self._step("session")))
        actions.add_widget(Button(text="Day", on_press=lambda _b: self._step("day")))
        actions.add_widget(Button(text="To End", on_press=lambda _b: self._step("end")))
        actions.add_widget(Button(text="Next Bowler", on_press=lambda _b: self._next_bowler()))
        self.root.add_widget(actions, index=1)

    def _start(self):
        fixtures = self.service.get_fixtures("Test")
        target = next(
            (
                f
                for f in fixtures
                if not f.get("completed")
                and f.get("team1") is not None
                and f.get("team2") is not None
            ),
            None,
        )
        if not target:
            self.content.text = "No pending Test fixtures with valid teams."
            return
        payload = self.service.start_interactive_match(target, "Test")
        self.session_id = payload.get("session_id")
        self._render_state(payload.get("state", {}))

    def _step(self, action: str):
        if not self.session_id:
            self.content.text = "Start a Test interactive match first."
            return
        payload = self.service.step_interactive_match(self.session_id, action)
        self._render_state(payload.get("state", {}))

    def _next_bowler(self):
        if not self.session_id:
            self.content.text = "Start a Test interactive match first."
            return
        payload = self.service.cycle_test_bowler(self.session_id)
        self._render_state(payload.get("state", {}))

    def _render_state(self, state):
        commentary = state.get("commentary_tail", [])
        commentary_text = "\n".join([f"- {c}" for c in commentary[-6:]]) if commentary else "-"
        innings_summary = "\n".join(state.get("innings_summary", [])) or "-"
        batting_rows = state.get("batting_table_top", [])
        bowling_rows = state.get("bowling_table_top", [])
        fow_rows = state.get("fow_tail", [])
        batting_text = "\n".join(
            [f"- {r['name']} {r['runs']}({r['balls']}) 4s:{r['fours']} 6s:{r['sixes']}" for r in batting_rows[:5]]
        ) or "-"
        bowling_text = "\n".join(
            [f"- {r['name']} {r['wickets']}/{r['runs']} overs:{r['overs']}" for r in bowling_rows[:5]]
        ) or "-"
        fow_text = "\n".join(
            [f"- {f.get('team', '?')} {f.get('score', '?')}/{f.get('wicket', '?')} ({f.get('batsman', '?')})" for f in fow_rows]
        ) or "-"
        self.content.text = (
            f"Engine: {state.get('engine')}\n"
            f"Day {state.get('day')} Session {state.get('session')} Innings {state.get('innings')}\n"
            f"Current: {state.get('runs')}/{state.get('wickets')} in {state.get('overs')}.{state.get('balls')}\n"
            f"Batters: {state.get('striker')}* / {state.get('non_striker')}\n"
            f"Bowler: {state.get('current_bowler')}\n"
            f"Winner: {state.get('winner')}  Result: {state.get('result')}\n"
            f"Ended: {state.get('match_ended')}\n"
            f"Innings Summary:\n{innings_summary}\n"
            f"Top Batting:\n{batting_text}\n"
            f"Top Bowling:\n{bowling_text}\n"
            f"FOW Tail:\n{fow_text}\n"
            f"Commentary:\n{commentary_text}"
        )

    def refresh(self):
        self.content.text = (
            "This screen uses legacy test-match engine backend for accuracy:\n"
            "- DATA/test_match_enhanced.py\n"
            "Use Start -> Ball/Over/Session/Day/To End for interactive control."
        )


PARITY_SCREEN_CLASSES = [
    LeaguesViewScreen,
    StatisticsScreen,
    RankingsScreen,
    WorldCupScreen,
    TrainingScreen,
    SettingsScreen,
    SeasonSummaryScreen,
    MatchScorecardScreen,
    SelectXIScreen,
    T20InteractiveScreen,
    TestInteractiveScreen,
]
