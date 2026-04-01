"""
Domestic competitions and teams for top 10 Test nations (T20, ODI, Test).
Creates domestic Team objects with generated players and round-robin fixtures.
"""

import random
import uuid

from cricket_manager.config.domestic_data import TOP_10_TEST_NATIONS, DOMESTIC_COMPETITIONS
from cricket_manager.core.team import Team
from cricket_manager.systems.trait_assignment import assign_traits_to_player
from cricket_manager.utils.constants import MAX_SQUAD_SIZE
from cricket_manager.utils.domestic_cricinfo_roster import make_player_for_game
from cricket_manager.utils.domestic_custom_rosters import (
    get_custom_players_payload,
    reload_domestic_custom_rosters,
)


def get_pitch_conditions(region_name):
    """Return pitch condition ranges for a region (used for domestic fixtures)."""
    subcontinent = ["India", "Pakistan", "Sri Lanka", "Bangladesh", "Afghanistan"]
    if region_name in subcontinent:
        return {'bounce': (3, 6), 'spin': (5, 9), 'pace': (3, 6), 'region': 'subcontinent'}
    if region_name in ["Australia", "South Africa"]:
        return {'bounce': (6, 9), 'spin': (3, 6), 'pace': (6, 9), 'region': 'sena'}
    if region_name in ["England", "New Zealand"]:
        return {'bounce': (5, 8), 'spin': (4, 7), 'pace': (5, 8), 'region': 'sena'}
    # West Indies
    return {'bounce': (5, 8), 'spin': (4, 7), 'pace': (5, 8), 'region': 'caribbean'}


class DomesticSystem:
    """
    Creates domestic teams and fixtures for top 10 Test nations across T20, ODI, Test.
    List-A / FC sides get generated squads. T20 league teams keep their real names (PSL, IPL, etc.);
    those squads are filled by randomly assigning players already on ODI/FC domestic teams (same
    player can appear on a province and a franchise — no extra generated players for T20-only names).
    """

    def __init__(self, game_engine=None):
        self.game_engine = game_engine
        # All domestic teams: list of Team objects (is_domestic=True, parent_nation set)
        self.domestic_teams = []
        # Fixtures per format: {'T20': [...], 'ODI': [...], 'Test': [...]}
        # Each fixture has: team1, team2, home_team, away_team, format, competition_name, nation, tier=0 (domestic), month, day, etc.
        self.domestic_fixtures = {'T20': [], 'ODI': [], 'Test': []}
        # Lookup: nation -> format -> (competition_name, [Team, ...])
        self.competitions_by_nation = {}

    def build_domestic_teams_and_fixtures(
        self, international_team_names, *, force_generated_squads: bool = False
    ):
        """
        Create domestic teams and fixtures for every nation in TOP_10_TEST_NATIONS
        that exists in the game (international_team_names).

        One canonical Team per name: if the same short name appears in T20 and ODI/Test (e.g. Surrey),
        one Team plays all formats. T20-only names (e.g. Peshawar Zalmi) get a separate Team whose
        squad is built only from players drawn at random from the nation's ODI/FC domestic squads
        (shared Player references — no new generated players for those franchises).

        Args:
            international_team_names: set or list of international team names (e.g. from game_engine.all_teams)
            force_generated_squads: If True, ignore domestic_custom_rosters.json and use only
                procedurally generated players (used after "Generate Fake Database").
        """
        names_set = set(international_team_names)
        self.domestic_teams = []
        self.domestic_fixtures = {'T20': [], 'ODI': [], 'Test': []}
        self.competitions_by_nation = {}
        reload_domestic_custom_rosters()

        for nation in TOP_10_TEST_NATIONS:
            if nation not in names_set:
                continue
            if nation not in DOMESTIC_COMPETITIONS:
                continue

            comps = DOMESTIC_COMPETITIONS[nation]
            self.competitions_by_nation[nation] = {}

            # List-A / FC roster sources only (generated players live here)
            roster_names_ordered = []
            seen_roster = set()
            for roster_fmt in ('ODI', 'Test'):
                if roster_fmt not in comps:
                    continue
                _, team_names = comps[roster_fmt]
                for short_name in team_names:
                    if short_name not in seen_roster:
                        seen_roster.add(short_name)
                        roster_names_ordered.append(short_name)
            if not roster_names_ordered and 'T20' in comps:
                _, team_names = comps['T20']
                roster_names_ordered = list(team_names)

            t20_names_in_config = list(comps['T20'][1]) if 'T20' in comps else []
            t20_name_set = set(t20_names_in_config)

            team_registry = {}
            for short_name in roster_names_ordered:
                formats_here = []
                if 'ODI' in comps and short_name in comps['ODI'][1]:
                    formats_here.append('ODI')
                if 'Test' in comps and short_name in comps['Test'][1]:
                    formats_here.append('Test')
                if short_name in t20_name_set:
                    formats_here.append('T20')
                if not formats_here:
                    formats_here = ['ODI']
                primary_fmt = formats_here[0]
                primary_comp = comps[primary_fmt][0]
                team = Team(name=short_name, tier=0)
                team.is_domestic = True
                team.parent_nation = nation
                team.domestic_competition = primary_comp
                team.domestic_format = "Multi" if len(formats_here) > 1 else primary_fmt
                team.format_tiers['T20'] = 0
                team.format_tiers['ODI'] = 0
                team.format_tiers['Test'] = 0
                self._populate_domestic_squad(team, nation, force_generated=force_generated_squads)
                team_registry[short_name] = team
                self.domestic_teams.append(team)

            # Pool of all ODI/FC domestic players for this nation (for T20-only franchise squads)
            national_pool = []
            for short_name in roster_names_ordered:
                national_pool.extend(team_registry[short_name].players[:])
            random.shuffle(national_pool)
            pool_idx = 0

            if 'T20' in comps:
                t20_comp_name = comps['T20'][0]
                for t20_name in t20_names_in_config:
                    if t20_name in team_registry:
                        continue
                    t20_team = Team(name=t20_name, tier=0)
                    t20_team.is_domestic = True
                    t20_team.parent_nation = nation
                    t20_team.domestic_competition = t20_comp_name
                    t20_team.domestic_format = 'T20'
                    t20_team.format_tiers['T20'] = 0
                    t20_team.format_tiers['ODI'] = 0
                    t20_team.format_tiers['Test'] = 0
                    # Same nominal squad size as ODI/FC clubs (_populate_domestic_squad)
                    custom_t20 = (
                        None
                        if force_generated_squads
                        else get_custom_players_payload(nation, t20_name)
                    )
                    if custom_t20:
                        records, tier = custom_t20
                        cap = min(15, MAX_SQUAD_SIZE)
                        for rec in records[:cap]:
                            try:
                                p = make_player_for_game(rec, nationality=nation, tier=tier)
                                if not t20_team.add_player(p):
                                    break
                            except Exception as e:
                                print(f"[DomesticSystem] Skip {rec.get('name')}: {e}")
                    else:
                        for _ in range(15):
                            if pool_idx >= len(national_pool):
                                break
                            p = national_pool[pool_idx]
                            pool_idx += 1
                            if not t20_team.add_player(p):
                                break
                    team_registry[t20_name] = t20_team
                    self.domestic_teams.append(t20_team)

            for fmt in ['T20', 'ODI', 'Test']:
                if fmt not in comps:
                    continue
                comp_name, team_names = comps[fmt]
                teams = [team_registry[n] for n in team_names if n in team_registry]
                if not teams:
                    continue
                self.competitions_by_nation[nation][fmt] = (comp_name, teams)
                fixtures = self._generate_round_robin_fixtures(teams, fmt, comp_name, nation)
                self.domestic_fixtures[fmt].extend(fixtures)

        print(f"[DomesticSystem] Created {len(self.domestic_teams)} domestic teams and "
              f"{sum(len(f) for f in self.domestic_fixtures.values())} domestic fixtures")
        return self.domestic_teams, self.domestic_fixtures

    def _populate_domestic_squad(self, team, nation, *, force_generated: bool = False):
        """Fill a domestic club with generated players (one shared squad per team)."""
        cap = min(15, MAX_SQUAD_SIZE)
        payload = None if force_generated else get_custom_players_payload(nation, team.name)
        if payload:
            records, tier = payload
            records = records[:cap]
            if len(records) < 11:
                print(
                    f"[DomesticSystem] Custom roster {team.name}: only {len(records)} players "
                    f"(11+ recommended for a full side)"
                )
            for rec in records:
                try:
                    p = make_player_for_game(rec, nationality=nation, tier=tier)
                    team.add_player(p)
                except Exception as e:
                    print(f"[DomesticSystem] Skip player {rec.get('name')}: {e}")
            if team.players:
                return
            print(f"[DomesticSystem] Custom roster produced no players for {team.name}; using generated squad.")

        for _ in range(15):
            player = self.game_engine.generate_player(nation, tier=2)
            player.nationality = nation
            assign_traits_to_player(player)
            if hasattr(self.game_engine, 'training_system') and self.game_engine.training_system:
                from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                if player.bowling > 40:
                    from cricket_manager.systems.bowling_movements import generate_bowling_movements
                    player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
                initialize_pace_speeds(player)
            team.add_player(player)

    def _create_domestic_teams_for_competition(self, nation, comp_name, fmt, team_names):
        """Create Team objects for each domestic team name; assign generated players."""
        teams = []
        for short_name in team_names:
            # Display name can include nation for clarity in UI
            display_name = f"{short_name}"  # e.g. "Mumbai Indians"
            team = Team(name=display_name, tier=0)
            team.is_domestic = True
            team.parent_nation = nation
            team.domestic_competition = comp_name
            team.domestic_format = fmt
            # Format tiers: 0 = domestic (excluded from international tiers)
            team.format_tiers['T20'] = 0
            team.format_tiers['ODI'] = 0
            team.format_tiers['Test'] = 0

            self._populate_domestic_squad(team, nation)

            teams.append(team)
        return teams

    def _generate_round_robin_fixtures(self, teams, fmt, comp_name, nation):
        """Generate double round-robin (home and away) for the list of teams. Assign month/day spread across season."""
        fixtures = []
        n = len(teams)
        if n < 2:
            return fixtures
        pc = get_pitch_conditions(nation)
        pairs = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    pairs.append((i, j))
        random.shuffle(pairs)
        months_used = list(range(12))
        random.shuffle(months_used)
        for match_idx, (i, j) in enumerate(pairs):
            home_team = teams[i]
            away_team = teams[j]
            month_idx = months_used[match_idx % 12]
            day = (match_idx % 28) + 1
            pitch = {
                'pitch_bounce': random.randint(pc['bounce'][0], pc['bounce'][1]),
                'pitch_spin': random.randint(pc['spin'][0], pc['spin'][1]),
                'pitch_pace': random.randint(pc['pace'][0], pc['pace'][1]),
                'pitch_region': pc['region'],
            }
            fixture = {
                'team1': home_team,
                'team2': away_team,
                'home_team': home_team,
                'away_team': away_team,
                'home': home_team.name,
                'away': away_team.name,
                'tier': 0,
                'format': fmt,
                'month': month_idx,
                'day': day,
                'competition_name': comp_name,
                'nation': nation,
                'match_type': 'domestic',
                'series_id': f"dom_{nation}_{comp_name.replace(' ', '_')}_{uuid.uuid4().hex[:6]}",
                'series_name': f"{comp_name} ({nation})",
                'pitch_conditions': pitch,
                'completed': False,
            }
            fixtures.append(fixture)
        return fixtures

    def get_domestic_teams_for_nation_format(self, nation, format_type):
        """Return list of domestic Team objects for a nation and format."""
        if nation not in self.competitions_by_nation:
            return []
        if format_type not in self.competitions_by_nation[nation]:
            return []
        _, teams = self.competitions_by_nation[nation][format_type]
        return teams

    def get_all_domestic_teams_flat(self):
        """Return flat list of all domestic teams (for save/load and UI)."""
        return list(self.domestic_teams)
