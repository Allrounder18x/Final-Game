from __future__ import annotations

from typing import Any, Dict, List

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


class BaseCricketScreen(Screen):
    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.root_layout = BoxLayout(orientation="vertical", spacing=8, padding=10)
        self.add_widget(self.root_layout)

    def nav_row(self, *destinations: str) -> BoxLayout:
        row = BoxLayout(size_hint_y=None, height=44, spacing=6)
        for dest in destinations:
            row.add_widget(Button(text=dest, on_press=lambda _btn, d=dest: self._go(d)))
        return row

    def _go(self, dest: str) -> None:
        sm = self.manager
        if sm and dest in sm.screen_names:
            sm.current = dest


class TeamSelectionScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.root_layout.add_widget(Label(text="Team Selection", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("dashboard", "fixtures", "standings", "players"))
        self.team_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        self.team_list.bind(minimum_height=self.team_list.setter("height"))
        sv = ScrollView()
        sv.add_widget(self.team_list)
        self.root_layout.add_widget(sv)
        self.refresh()

    def refresh(self):
        self.team_list.clear_widgets()
        engine = self.service.get_engine()
        for team in engine.all_teams:
            self.team_list.add_widget(
                Button(
                    text=team.name,
                    size_hint_y=None,
                    height=40,
                    on_press=lambda _btn, name=team.name: self._select_team(name),
                )
            )

    def _select_team(self, team_name: str):
        self.service.set_user_team(team_name)
        self._go("dashboard")


class DashboardScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.root_layout.add_widget(Label(text="Dashboard", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("team_selection", "fixtures", "standings", "players"))
        parity_row_1 = BoxLayout(size_hint_y=None, height=40, spacing=4)
        for dest in ("leagues_view", "statistics_view", "rankings_view", "world_cup_view"):
            parity_row_1.add_widget(Button(text=dest, on_press=lambda _btn, d=dest: self._go(d)))
        self.root_layout.add_widget(parity_row_1)
        parity_row_2 = BoxLayout(size_hint_y=None, height=40, spacing=4)
        for dest in ("training_view", "settings_view", "season_summary_view", "select_xi_view"):
            parity_row_2.add_widget(Button(text=dest, on_press=lambda _btn, d=dest: self._go(d)))
        self.root_layout.add_widget(parity_row_2)
        parity_row_3 = BoxLayout(size_hint_y=None, height=40, spacing=4)
        for dest in ("t20_interactive_view", "test_interactive_view", "match_scorecard_view"):
            parity_row_3.add_widget(Button(text=dest, on_press=lambda _btn, d=dest: self._go(d)))
        self.root_layout.add_widget(parity_row_3)
        self.info = Label(text="", halign="left", valign="top")
        self.root_layout.add_widget(self.info)
        self.refresh()

    def on_pre_enter(self, *args):
        self.refresh()
        return super().on_pre_enter(*args)

    def refresh(self):
        engine = self.service.get_engine()
        team_name = engine.user_team.name if engine.user_team else "Not selected"
        total_fixtures = len(engine.get_fixtures("T20")) + len(engine.get_fixtures("ODI")) + len(engine.get_fixtures("Test"))
        self.info.text = (
            f"User Team: {team_name}\n"
            f"Season: {engine.current_season}\n"
            f"Year: {engine.current_year}\n"
            f"Total Fixtures: {total_fixtures}\n"
        )


class FixturesScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.current_format = "T20"
        self.current_status = "All"
        self.current_tier = 0
        self.root_layout.add_widget(Label(text="Fixtures (tap to simulate)", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("dashboard", "standings", "players", "match_simulation"))
        format_row = BoxLayout(size_hint_y=None, height=40, spacing=4)
        for fmt in ("T20", "ODI", "Test"):
            format_row.add_widget(Button(text=fmt, on_press=lambda _btn, f=fmt: self._set_format(f)))
        self.root_layout.add_widget(format_row)
        filter_row = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.status_spinner = Spinner(text="All", values=("All", "Pending", "Completed"))
        self.status_spinner.bind(text=lambda _s, v: self._set_status(v))
        filter_row.add_widget(self.status_spinner)
        self.tier_spinner = Spinner(text="Tier 0", values=("Tier 0", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"))
        self.tier_spinner.bind(text=lambda _s, v: self._set_tier(v))
        filter_row.add_widget(self.tier_spinner)
        self.team_spinner = Spinner(text="All Teams", values=("All Teams",))
        self.team_spinner.bind(text=lambda _s, _v: self.refresh())
        filter_row.add_widget(self.team_spinner)
        self.root_layout.add_widget(filter_row)
        sim_row = BoxLayout(size_hint_y=None, height=40, spacing=4)
        sim_row.add_widget(Button(text="Sim Format Season", on_press=lambda _b: self._sim_format_season()))
        sim_row.add_widget(Button(text="Sim All Formats", on_press=lambda _b: self._sim_all_formats()))
        self.root_layout.add_widget(sim_row)
        self.fixtures_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        self.fixtures_list.bind(minimum_height=self.fixtures_list.setter("height"))
        sv = ScrollView()
        sv.add_widget(self.fixtures_list)
        self.root_layout.add_widget(sv)
        self.refresh()

    def _set_format(self, fmt: str):
        self.current_format = fmt
        self._refresh_team_options()
        self.refresh()

    def _set_status(self, status: str):
        self.current_status = status
        self.refresh()

    def _set_tier(self, tier_text: str):
        self.current_tier = int(tier_text.split()[-1])
        self.refresh()

    def _refresh_team_options(self):
        teams = ["All Teams"] + self.service.list_teams()
        self.team_spinner.values = tuple(teams)
        if self.team_spinner.text not in teams:
            self.team_spinner.text = "All Teams"

    def refresh(self):
        self.fixtures_list.clear_widgets()
        self._refresh_team_options()
        fixtures = self.service.get_fixtures_filtered(
            match_format=self.current_format,
            status=self.current_status,
            team_filter=self.team_spinner.text,
            tier_filter=self.current_tier,
            limit=300,
        )
        for fixture in fixtures[:200]:
            t1 = fixture.get("team1").name if fixture.get("team1") else fixture.get("home", "TBD")
            t2 = fixture.get("team2").name if fixture.get("team2") else fixture.get("away", "TBD")
            done = " [Done]" if fixture.get("completed") else ""
            label = f"{self.current_format}: {t1} vs {t2}{done}"
            self.fixtures_list.add_widget(
                Button(
                    text=label,
                    size_hint_y=None,
                    height=42,
                    on_press=lambda _btn, fx=fixture: self._simulate(fx),
                )
            )

    def _sim_format_season(self):
        self.service.simulate_season_chunk(self.current_format)
        self.refresh()

    def _sim_all_formats(self):
        self.service.simulate_season_all_formats()
        self.refresh()

    def _simulate(self, fixture: Dict[str, Any]):
        result = self.service.simulate_match(fixture, self.current_format)
        sim_screen = self.manager.get_screen("match_simulation")
        sim_screen.set_result(result)
        self.manager.current = "match_simulation"


class MatchSimulationScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.root_layout.add_widget(Label(text="In-App Match Simulation", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("fixtures", "dashboard", "standings", "players"))
        self.result_label = Label(text="No match simulated yet.", halign="left", valign="top")
        self.root_layout.add_widget(self.result_label)

    def set_result(self, result: Dict[str, Any]):
        if not result:
            self.result_label.text = "Simulation failed."
            return
        scorecard = result.get("scorecard", {})
        motm = scorecard.get("man_of_the_match", "N/A")
        self.result_label.text = (
            f"{result.get('team1')} vs {result.get('team2')}\n"
            f"Winner: {result.get('winner')}\n"
            f"Margin: {result.get('margin')}\n"
            f"Player of Match: {motm}"
        )


class StandingsScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.current_format = "T20"
        self.current_tier = 1
        self.root_layout.add_widget(Label(text="Standings", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("dashboard", "fixtures", "players"))
        controls = BoxLayout(size_hint_y=None, height=40, spacing=4)
        for fmt in ("T20", "ODI", "Test"):
            controls.add_widget(Button(text=fmt, on_press=lambda _btn, f=fmt: self._set_format(f)))
        for tier in (1, 2, 3, 4):
            controls.add_widget(Button(text=f"T{tier}", on_press=lambda _btn, t=tier: self._set_tier(t)))
        self.root_layout.add_widget(controls)
        self.table = Label(text="", halign="left", valign="top")
        self.root_layout.add_widget(self.table)
        self.refresh()

    def _set_format(self, fmt: str):
        self.current_format = fmt
        self.refresh()

    def _set_tier(self, tier: int):
        self.current_tier = tier
        self.refresh()

    def refresh(self):
        standings = self.service.get_standings(self.current_format, self.current_tier).get("rows", [])
        lines = [f"{self.current_format} Tier {self.current_tier}"]
        for i, row in enumerate(standings, start=1):
            lines.append(
                f"{i}. {row.get('team_name')} | Pts {row.get('points', 0)} "
                f"W {row.get('wins', 0)} L {row.get('losses', 0)} D {row.get('draws', 0)}"
            )
        self.table.text = "\n".join(lines)


class PlayerListScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.root_layout.add_widget(Label(text="Players (lite)", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("dashboard", "fixtures", "standings"))
        filter_row = BoxLayout(size_hint_y=None, height=40, spacing=4)
        self.team_spinner = Spinner(text="All Teams", values=("All Teams",))
        self.team_spinner.bind(text=lambda _s, _v: self.refresh())
        filter_row.add_widget(self.team_spinner)
        self.role_spinner = Spinner(text="All Roles", values=("All Roles", "Batter", "Bowler", "All-Rounder", "Wicket-Keeper"))
        self.role_spinner.bind(text=lambda _s, _v: self.refresh())
        filter_row.add_widget(self.role_spinner)
        self.sort_spinner = Spinner(text="Name", values=("Name", "Team", "Age", "Batting", "Bowling"))
        self.sort_spinner.bind(text=lambda _s, _v: self.refresh())
        filter_row.add_widget(self.sort_spinner)
        self.search_input = TextInput(text="", multiline=False, hint_text="Search player...")
        self.search_input.bind(text=lambda _s, _v: self.refresh())
        filter_row.add_widget(self.search_input)
        self.root_layout.add_widget(filter_row)
        self.players_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        self.players_list.bind(minimum_height=self.players_list.setter("height"))
        sv = ScrollView()
        sv.add_widget(self.players_list)
        self.root_layout.add_widget(sv)
        self.refresh()

    def on_pre_enter(self, *args):
        self.refresh()
        return super().on_pre_enter(*args)

    def refresh(self):
        self.players_list.clear_widgets()
        teams = ["All Teams"] + self.service.list_teams()
        self.team_spinner.values = tuple(teams)
        if self.team_spinner.text not in teams:
            self.team_spinner.text = "All Teams"
        rows = self.service.get_players_filtered(
            team_name=self.team_spinner.text,
            search_text=self.search_input.text,
            role_filter=self.role_spinner.text,
            sort_key=self.sort_spinner.text,
            limit=500,
        )
        for row in rows:
            text = f"{row['name']} ({row['team']}) - {row['role']}"
            self.players_list.add_widget(
                Button(text=text, size_hint_y=None, height=40, on_press=lambda _btn, n=row["name"]: self._open_player(n))
            )

    def _open_player(self, player_name: str):
        profile_screen = self.manager.get_screen("player_profile_lite")
        profile_screen.set_player(player_name)
        self.manager.current = "player_profile_lite"


class PlayerProfileLiteScreen(BaseCricketScreen):
    def __init__(self, service, **kwargs):
        super().__init__(service=service, **kwargs)
        self.root_layout.add_widget(Label(text="Player Profile Lite", size_hint_y=None, height=40))
        self.root_layout.add_widget(self.nav_row("players", "dashboard", "fixtures", "standings"))
        self.profile = Label(text="Select a player", halign="left", valign="top")
        self.root_layout.add_widget(self.profile)

    def set_player(self, player_name: str):
        player = self.service.get_player_profile(player_name)
        if not player:
            self.profile.text = "Player not found."
            return
        self.profile.text = (
            f"Name: {player['name']}\n"
            f"Team: {player['team']}\n"
            f"Role: {player['role']}\n"
            f"Age: {player['age']}\n"
            f"Batting: {player['batting']}\n"
            f"Bowling: {player['bowling']}\n"
            f"Fielding: {player['fielding']}"
        )
