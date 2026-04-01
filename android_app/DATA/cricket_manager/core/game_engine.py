"""
Game Engine - Core orchestration of all game systems
Phase 9 Step 9A: Core & Initialization
"""

import random
import copy
from datetime import datetime

# Import real players database
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
try:
    from real_players_database import REAL_PLAYERS  # type: ignore[import-not-found]
except ImportError:
    print("[GameEngine] Warning: real_players_database not found, using generated players only")
    REAL_PLAYERS = {}


from cricket_manager.core.team import Team
from cricket_manager.core.player import Player
from cricket_manager.core.match_simulator import MatchSimulator
from cricket_manager.core.fast_match_simulator import FastMatchSimulator
from cricket_manager.core.statistics_manager import StatisticsManager
from cricket_manager.systems.multi_format_tier_manager import MultiFormatTierManager
from cricket_manager.systems.trait_assignment import assign_traits_to_player
from cricket_manager.systems.loot_pack_system import LootPackSystem
from cricket_manager.systems.world_cup_system import WorldCupSystem
from cricket_manager.systems.youth_system import YouthSystem
from cricket_manager.systems.training_system import TrainingSystem
from cricket_manager.systems.domestic_system import DomesticSystem
from cricket_manager.systems.bowling_movements import generate_bowling_movements, update_bowling_movements
from cricket_manager.utils.name_generator import generate_player_name
from cricket_manager.utils.constants import MAX_SQUAD_SIZE
from cricket_manager.utils.domestic_affiliations import (
    assign_foreign_t20_elite_national_squads,
    pick_affiliations_for_domestic_squad_player,
    pick_affiliations_for_nation,
)


class GameEngine:
    """
    Main game engine that orchestrates all game systems
    
    Responsibilities:
    - Season simulation for all formats
    - Match execution and scorecard storage
    - World Cup tournaments (every 2 years)
    - Player retirements and aging
    - Youth promotions
    - Tier promotions/relegations
    - End-of-season summary
    - Save/load game state
    """
    
    def __init__(self):
        print("[GameEngine] Initializing...")
        
        # Game state
        self.current_season = 1
        self.current_year = 2025
        
        # Simulation settings (can be updated from Settings screen)
        self.simulation_settings = {
            't20_dot_adj': 0,
            't20_boundary_adj': 0,
            't20_wicket_adj': 0,
            'odi_dot_adj': 0,
            'odi_boundary_adj': 0,
            'odi_wicket_adj': 0,
            'test_dot_adj': 0,
            'test_boundary_adj': 0,
            'test_wicket_adj': 0,
        }
        
        # Initialize all systems
        self.statistics_manager = StatisticsManager()
        self.tier_manager = MultiFormatTierManager()
        self.loot_system = LootPackSystem()
        self.world_cup_system = WorldCupSystem()
        self.youth_system = YouthSystem()
        self.training_system = TrainingSystem()
        
        # Phase 10 systems
        from cricket_manager.systems.role_conversion import RoleConversionSystem
        from cricket_manager.systems.team_news import TeamNewsSystem
        from cricket_manager.systems.commentary import CommentarySystem
        
        self.role_conversion = RoleConversionSystem()
        self.news_system = TeamNewsSystem()
        self.commentary_system = CommentarySystem()
        
        # Game data
        self.all_teams = []
        self.user_team = None
        self.fixtures = {
            'T20': [],
            'ODI': [],
            'Test': []
        }
        self.match_scorecards = {}  # Store detailed scorecards
        self.world_cup_history = []
        self.opponent_history = {}  # Track opponent rotation across seasons
        self.domestic_system = DomesticSystem(self)
        self.domestic_teams = []
        self.domestic_fixtures = {'T20': [], 'ODI': [], 'Test': []}
        self.user_domestic_team = None  # When user picks a domestic side at start, this is set
        
        # Season tracking
        self.season_retirements = []
        self.season_promotions = []
        self.season_changes = []
        
        # Head-to-head: (team_a, team_b) sorted -> {wins_a, wins_b, draws, last_5_results}
        self.head_to_head = {}
        # Difficulty: 'Easy' | 'Normal' | 'Hard' (affects AI strength / sim variance)
        self.difficulty = 'Normal'
        # Season awards (filled at end of season)
        self.season_awards = {}  # {'batter': name, 'bowler': name, 'young_player': name}
        # Last match POTM (for display)
        self.last_match_potm = None
        # Hide batting/bowling ratings in all GUIs when True
        self.hide_batting_bowling_ratings = False
        self.season_matches = []
        self.season_transfers = []  # Test nation -> associate transfers (poor performers)
        # Persistent career logs (append-only; not cleared each simulate_season)
        self.career_promotions_log = []  # U21 -> senior promotions; dicts include season, year
        self.career_transfers_log = []  # associate / return moves; dicts include season, year
        # End-of-season snapshots for league tab year-by-year views (see _snapshot_league_standings_for_history)
        self.league_standings_history = []
        
        # Initialize game
        self.initialize_game()
        
        print(f"[GameEngine] Initialized - Season {self.current_season}, Year {self.current_year}")
    
    def initialize_game(self):
        """Initialize new game with teams and players"""
        print("[GameEngine] Generating teams and players...")
        
        # Test nations (Tier 1) - 12 teams
        test_nations = [
            "India", "Australia", "England", "Pakistan", "South Africa",
            "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan",
            "Ireland", "Zimbabwe"
        ]
        
        # Tier 2 associates - 12 teams (strong associates)
        tier2_teams = [
            "Scotland", "Netherlands", "UAE", "Oman", "Nepal", "PNG",
            "Namibia", "USA", "Canada", "Kenya", "Hong Kong", "Singapore"
        ]
        
        # Tier 3-4 teams - 24 teams
        other_teams = [
            "Malaysia", "Thailand", "Kuwait", "Bahrain",
            "Qatar", "Saudi Arabia", "Maldives", "Bermuda", "Denmark", "Germany",
            "Italy", "Jersey", "Norway", "Spain", "Austria", "Belgium",
            "France", "Greece", "Portugal", "Sweden", "Switzerland", "Turkey",
            "Argentina", "Brazil"
        ]
        
        # Generate Test nations (Tier 1) with REAL players
        for name in test_nations:
            team = Team(name=name, tier=1)
            
            # Use real players if available
            if name in REAL_PLAYERS:
                for player_data in REAL_PLAYERS[name]:
                    player = Player(
                        name=player_data['name'],
                        age=player_data['age'],
                        role=player_data['role'],
                        nationality=name
                    )
                    player.batting = player_data['batting']
                    player.bowling = player_data['bowling']
                    player.fielding = player_data['fielding']
                    player.form = random.randint(70, 95)
                    
                    # Generate bowling movements based on skill and role
                    if player.bowling > 40:
                        player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
                    
                    # Initialize pace speeds for bowlers
                    from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                    initialize_pace_speeds(player)
                    
                                        
                    # Assign traits
                    assign_traits_to_player(player)
                    team.add_player(player)
                
                print(f"[GameEngine] Loaded {len(REAL_PLAYERS[name])} real players for {name}")
            else:
                # Fallback to generated players
                for i in range(15):
                    player = self.generate_player(team.name, tier=1)
                    team.add_player(player)
            
            self.all_teams.append(team)
        
        # Generate Tier 2 teams (strong associates) with REAL players where available
        for name in tier2_teams:
            team = Team(name=name, tier=2)
            
            # Use real players if available, otherwise generate
            if name in REAL_PLAYERS:
                for player_data in REAL_PLAYERS[name]:
                    player = Player(
                        name=player_data['name'],
                        age=player_data['age'],
                        role=player_data['role'],
                        nationality=name
                    )
                    player.batting = player_data['batting']
                    player.bowling = player_data['bowling']
                    player.fielding = player_data['fielding']
                    player.form = random.randint(65, 90)
                    
                    # Generate bowling movements based on skill and role
                    if player.bowling > 40:
                        player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
                    
                    # Initialize pace speeds for bowlers
                    from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                    initialize_pace_speeds(player)
                    
                                        
                    # Assign traits
                    assign_traits_to_player(player)
                    team.add_player(player)
                
                print(f"[GameEngine] Loaded {len(REAL_PLAYERS[name])} real players for {name}")
            else:
                # Generate players for teams without real data
                for i in range(15):
                    player = self.generate_player(team.name, tier=2)
                    team.add_player(player)
            
            self.all_teams.append(team)
        
        # Generate Tier 3-4 teams with generated players
        for name in other_teams:
            team = Team(name=name, tier=3)
            
            # Generate 15 players per team
            for i in range(15):
                player = self.generate_player(team.name, tier=3)
                team.add_player(player)
            
            # Assign traits to all players
            for player in team.players:
                assign_traits_to_player(player)
            
            self.all_teams.append(team)
        
        total_teams = len(self.all_teams)
        total_players = sum(len(t.players) for t in self.all_teams)
        print(f"[GameEngine] Generated {total_teams} teams with {total_players} players")
        print(f"  - Tier 1 (Test nations): {len(test_nations)} teams with real players")
        print(f"  - Tier 2 (Associates): {len(tier2_teams)} teams")
        print(f"  - Tier 3-4: {len(other_teams)} teams")
        
        # Assign teams to tiers for all formats
        print("[GameEngine] Assigning teams to tiers...")
        self.tier_manager.initialize_all_tiers(self.all_teams)
        
        # Generate U21 squads
        print("[GameEngine] Generating U21 squads...")
        for team in self.all_teams:
            team.u21_squad = self.youth_system.generate_u21_squad(team)
        
        # Generate youth fixtures for all formats (Tier 5)
        print("[GameEngine] Generating youth fixtures...")
        self.generate_youth_fixtures()
        
        # Set user team (India by default)
        self.user_team = next((t for t in self.all_teams if t.name == "India"), self.all_teams[0])
        print(f"[GameEngine] User team: {self.user_team.name}")
        
        # Generate fixtures for all formats (ICC FTP-style series)
        print("[GameEngine] Generating fixtures...")
        wc_month = self._get_wc_month(self.current_season)
        self.fixtures = self.tier_manager.generate_all_fixtures(
            wc_month=wc_month, current_season=self.current_season
        )
        
        # Pre-generate World Cup group stage fixtures (playable in fixtures tab)
        self.generate_world_cup_fixtures()
        
        total_fixtures = sum(len(f) for f in self.fixtures.values())
        print(f"[GameEngine] Generated {total_fixtures} fixtures across all formats")
        
        # Domestic competitions (top 10 Test nations, all 3 formats)
        print("[GameEngine] Building domestic teams and fixtures...")
        international_names = [t.name for t in self.all_teams]
        self.domestic_system.build_domestic_teams_and_fixtures(international_names)
        self.domestic_teams = self.domestic_system.domestic_teams
        self.domestic_fixtures = self.domestic_system.domestic_fixtures
        domestic_total = sum(len(f) for f in self.domestic_fixtures.values())
        print(f"[GameEngine] Domestic: {len(self.domestic_teams)} teams, {domestic_total} fixtures")
        
        self.assign_domestic_affiliations_all_players()
        
        # Give all teams starting training points so any team selected in Training tab has points
        for team in self.all_teams:
            self.training_system.reset_training_points(team)
        print(f"[GameEngine] All teams given {self.training_system.training_points_per_season} training points")
        
        print("[GameEngine] Initialization complete!")
    
    def _append_career_promotion_log(self, row):
        """Persist U21→senior promotion for career history / saves (season/year = completed campaign)."""
        self.career_promotions_log.append({
            **dict(row),
            'season': self.current_season,
            'year': self.current_year,
        })
    
    def _append_career_transfer_log(self, row):
        """Persist associate transfer or return-to-Test for career history / saves."""
        self.career_transfers_log.append({
            **dict(row),
            'season': self.current_season,
            'year': self.current_year,
        })
    
    def generate_player(self, team_name, tier=3, max_age=None, min_age=None):
        """Generate a random player for a team with STRICT tier-based skills
        
        Optional max_age/min_age force a band (e.g. max_age=21 for domestic/U21-only recruits).
        
        Role Distribution (exact percentages):
        - Opening Batter: 15%
        - Middle Order Batter: 17%
        - Lower Order Batter: 12%
        - Wicketkeeper Batter: 10%
        - Batting Allrounder variants: 4% total
        - Bowling Allrounder variants: 5% total
        - Genuine Allrounder variants: 2% total
        - Finger Spinner: 9%
        - Wrist Spinner: 7%
        - Medium Pacer: 10%
        - Fast Medium Pacer: 7%
        - Fast Bowler: 2%
        
        Skill Rules:
        - Pure batsmen: bowling max 25
        - Pure bowlers: batting max 30
        - Batting allrounder: batting 20 points higher than bowling
        - Bowling allrounder: bowling 20 points higher than batting
        """
        name = generate_player_name(team_name)
        
        # Age distribution based on tier (or forced U21 band for domestic pipeline)
        if max_age is not None:
            lo = 17 if min_age is None else min_age
            hi = max_age
            if hi < lo:
                lo, hi = hi, lo
            age = random.randint(lo, hi)
        elif tier == 1:
            age = random.choices(range(18, 36), weights=[1,2,3,4,5,6,7,8,8,7,6,5,4,3,2,1,1,1])[0]
        elif tier == 2:
            age = random.choices(range(17, 34), weights=[2,3,4,5,6,7,7,6,5,4,3,2,2,1,1,1,1])[0]
        elif tier == 3:
            age = random.choices(range(17, 32), weights=[3,4,5,6,6,5,5,4,3,3,2,2,1,1,1])[0]
        else:  # Tier 4-5
            age = random.choices(range(17, 30), weights=[4,5,6,6,5,4,4,3,3,2,2,1,1])[0]
        
        # EXACT percentage-based role distribution (totals 100%)
        roles_with_weights = [
            # Pure Batsmen (54%)
            ('Opening Batter', 15.0),
            ('Middle Order Batter', 17.0),
            ('Lower Order Batter', 12.0),
            ('Wicketkeeper Batter', 10.0),
            # Batting Allrounders (4%)
            ('Batting Allrounder (Medium Pace)', 1.0),
            ('Batting Allrounder (Wrist Spin)', 1.0),
            ('Batting Allrounder (Finger Spin)', 1.0),
            ('Batting Allrounder (Fast Medium)', 1.0),
            # Bowling Allrounders (5%)
            ('Bowling Allrounder (Medium Pace)', 1.5),
            ('Bowling Allrounder (Wrist Spin)', 1.0),
            ('Bowling Allrounder (Finger Spin)', 1.0),
            ('Bowling Allrounder (Fast Medium)', 1.0),
            ('Bowling Allrounder (Fast)', 0.5),
            # Genuine Allrounders (2%)
            ('Genuine Allrounder (Medium Pace)', 0.25),
            ('Genuine Allrounder (Wrist Spin)', 0.50),
            ('Genuine Allrounder (Finger Spin)', 0.50),
            ('Genuine Allrounder (Fast Medium)', 0.50),
            ('Genuine Allrounder (Fast)', 0.25),
            # Pure Bowlers (35%)
            ('Finger Spinner', 9.0),
            ('Wrist Spinner', 7.0),
            ('Medium Pacer', 10.0),
            ('Fast Medium Pacer', 7.0),
            ('Fast Bowler', 2.0),
        ]
        
        roles = [r[0] for r in roles_with_weights]
        weights = [r[1] for r in roles_with_weights]
        role = random.choices(roles, weights=weights)[0]
        
        player = Player(name=name, age=age, role=role, nationality=team_name)
        
        # STRICT Tier-based skill ranges
        tier_skill_ranges = {
            1: {'primary': (70, 95), 'fielding': (55, 80)},
            2: {'primary': (58, 82), 'fielding': (45, 70)},
            3: {'primary': (45, 68), 'fielding': (38, 60)},
            4: {'primary': (35, 55), 'fielding': (30, 52)},
            5: {'primary': (25, 45), 'fielding': (22, 42)}
        }
        
        ranges = tier_skill_ranges.get(tier, tier_skill_ranges[3])
        primary_min, primary_max = ranges['primary']
        fielding_min, fielding_max = ranges['fielding']
        
        # Age-based skill adjustment
        if age <= 19:
            age_penalty = 10
        elif age <= 23:
            age_penalty = 5
        elif age <= 28:
            age_penalty = 0
        elif age <= 32:
            age_penalty = 3
        else:
            age_penalty = 8
        
        primary_max = max(primary_min, primary_max - age_penalty)
        fielding_max = max(fielding_min, fielding_max - age_penalty // 2)
        
        # Generate skills based on role type
        if role in ['Opening Batter', 'Middle Order Batter', 'Lower Order Batter', 'Wicketkeeper Batter']:
            # Pure batsmen: bowling max 25
            player.batting = random.randint(primary_min, primary_max)
            player.bowling = random.randint(5, 25)
            
        elif role in ['Finger Spinner', 'Wrist Spinner', 'Medium Pacer', 'Fast Medium Pacer', 'Fast Bowler']:
            # Pure bowlers: batting max 30
            player.batting = random.randint(8, 30)
            player.bowling = random.randint(primary_min, primary_max)
            
        elif 'Batting Allrounder' in role:
            # Batting allrounder: batting 20 points higher than bowling
            player.batting = random.randint(primary_min, primary_max)
            player.bowling = max(10, player.batting - 20 + random.randint(-3, 3))
            
        elif 'Bowling Allrounder' in role:
            # Bowling allrounder: bowling 20 points higher than batting
            player.bowling = random.randint(primary_min, primary_max)
            player.batting = max(10, player.bowling - 20 + random.randint(-3, 3))
            
        elif 'Genuine Allrounder' in role:
            # Genuine allrounder: both skills within 10 points of each other
            base_skill = random.randint(primary_min, max(primary_min, primary_max - 5))
            player.batting = base_skill + random.randint(-5, 5)
            player.bowling = base_skill + random.randint(-5, 5)
        
        player.fielding = random.randint(fielding_min, fielding_max)
        
        # Generate bowling movements based on skill and role
        if player.bowling > 40:
            player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
        
        # Initialize pace speeds for bowlers (only if bowling skill > 40)
        if player.bowling > 40:
            from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
            initialize_pace_speeds(player)
        
                
        # Form based on tier
        form_ranges = {1: (65, 95), 2: (60, 90), 3: (55, 85), 4: (50, 80), 5: (45, 75)}
        form_min, form_max = form_ranges.get(tier, (55, 85))
        player.form = random.randint(form_min, form_max)
        
        # Potential based on age and tier
        if age <= 23:
            player.potential = random.randint(60, 95 - (tier * 5))
        else:
            player.potential = random.randint(40, 70 - (tier * 3))
        
        # Assign traits: min 3, max 5 — guaranteed 2 positive + 1 negative, rest random
        from cricket_manager.systems.trait_assignment import get_trait_pool_for_player, get_trait_strength
        player.traits = []
        
        total_traits = random.randint(3, 5)
        
        pos_pool = get_trait_pool_for_player(player, positive=True, tier=tier)
        neg_pool = get_trait_pool_for_player(player, positive=False, tier=tier)
        random.shuffle(pos_pool)
        random.shuffle(neg_pool)
        
        assigned = set()
        
        # Guarantee 2 positive traits
        for t in pos_pool:
            if len([x for x in player.traits if x['name'] in set(pos_pool)]) >= 2:
                break
            if t not in assigned:
                strength = get_trait_strength(player, t, tier=tier)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
        
        # Guarantee 1 negative trait
        for t in neg_pool:
            if t not in assigned:
                strength = get_trait_strength(player, t, tier=tier)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
                break
        
        # Fill remaining slots randomly from both pools
        remaining = total_traits - len(player.traits)
        combined = [t for t in (pos_pool + neg_pool) if t not in assigned]
        random.shuffle(combined)
        for t in combined:
            if remaining <= 0:
                break
            if t not in assigned:
                strength = get_trait_strength(player, t, tier=tier)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
                remaining -= 1
        
        comps = getattr(getattr(self, 'domestic_system', None), 'competitions_by_nation', None) or {}
        if comps:
            t20, odi = pick_affiliations_for_nation(team_name, player.name, comps)
            player.domestic_t20_club_name = t20
            player.domestic_odi_fc_club_name = odi
        
        return player

    @staticmethod
    def _role_can_bowl(role):
        r = (role or "").lower()
        return (
            ("bowler" in r)
            or ("pacer" in r)
            or ("spinner" in r)
            or ("allrounder" in r)
            or ("all-rounder" in r)
        )

    def _ensure_playable_team_squad(
        self,
        team,
        nation_name,
        *,
        tier=2,
        min_players=11,
        min_bowling_options=6,
        target_size=15,
    ):
        """
        Ensure a team has enough players and bowling options for a stable auto-XI.
        Used after fake DB generation to prevent empty/non-playable bowling XIs.
        """
        if team is None:
            return
        players = getattr(team, "players", None)
        if players is None:
            team.players = []
            players = team.players

        # 1) Basic headcount floor
        guard = 0
        while len(players) < min_players and guard < 200:
            guard += 1
            p = self.generate_player(nation_name, tier=tier)
            team.add_player(p)
            players = getattr(team, "players", []) or []

        # 2) Prefer normal squad size for domestic depth (if room)
        guard = 0
        while len(players) < target_size and guard < 300:
            guard += 1
            p = self.generate_player(nation_name, tier=tier)
            team.add_player(p)
            players = getattr(team, "players", []) or []
            if len(players) >= target_size:
                break

        # 3) Bowling option floor
        def bowl_opts(pool):
            c = 0
            for pl in pool:
                if self._role_can_bowl(getattr(pl, "role", "")) or int(getattr(pl, "bowling", 0) or 0) >= 40:
                    c += 1
            return c

        guard = 0
        while bowl_opts(players) < min_bowling_options and guard < 400:
            guard += 1
            # Try until we get a bowling-capable profile
            inner = 0
            while inner < 40:
                inner += 1
                p = self.generate_player(nation_name, tier=tier)
                if self._role_can_bowl(getattr(p, "role", "")) or int(getattr(p, "bowling", 0) or 0) >= 40:
                    team.add_player(p)
                    break
            players = getattr(team, "players", []) or []
            # Stop if add_player refused due cap
            if guard > 10 and len(players) >= MAX_SQUAD_SIZE:
                break
    
    def assign_domestic_affiliations_all_players(self):
        """Set domestic T20 and ODI/FC club names on every international and domestic-list player."""
        comps = getattr(self.domestic_system, 'competitions_by_nation', None) or {}
        for team in self.all_teams:
            for p in team.players:
                t20, odi = pick_affiliations_for_nation(team.name, p.name, comps)
                p.domestic_t20_club_name = t20
                p.domestic_odi_fc_club_name = odi
            for p in getattr(team, 'u21_squad', []) or []:
                t20, odi = pick_affiliations_for_nation(team.name, p.name, comps)
                p.domestic_t20_club_name = t20
                p.domestic_odi_fc_club_name = odi
        for dt in getattr(self, 'domestic_teams', None) or []:
            for p in dt.players:
                t20, odi = pick_affiliations_for_domestic_squad_player(p, dt, comps)
                p.domestic_t20_club_name = t20
                p.domestic_odi_fc_club_name = odi
        assign_foreign_t20_elite_national_squads(
            self.all_teams, getattr(self, 'domestic_teams', None) or [], comps
        )
        self.sync_national_players_into_domestic_club_squads()
    
    def fill_missing_domestic_club_names(self):
        """For loaded saves: only assign club names when missing."""
        comps = getattr(self.domestic_system, 'competitions_by_nation', None) or {}
        for team in self.all_teams:
            for p in team.players:
                if not getattr(p, 'domestic_t20_club_name', '') or not getattr(p, 'domestic_odi_fc_club_name', ''):
                    t20, odi = pick_affiliations_for_nation(team.name, p.name, comps)
                    p.domestic_t20_club_name = t20
                    p.domestic_odi_fc_club_name = odi
            for p in getattr(team, 'u21_squad', []) or []:
                if not getattr(p, 'domestic_t20_club_name', '') or not getattr(p, 'domestic_odi_fc_club_name', ''):
                    t20, odi = pick_affiliations_for_nation(team.name, p.name, comps)
                    p.domestic_t20_club_name = t20
                    p.domestic_odi_fc_club_name = odi
        for dt in getattr(self, 'domestic_teams', None) or []:
            for p in dt.players:
                if not getattr(p, 'domestic_t20_club_name', '') or not getattr(p, 'domestic_odi_fc_club_name', ''):
                    t20, odi = pick_affiliations_for_domestic_squad_player(p, dt, comps)
                    p.domestic_t20_club_name = t20
                    p.domestic_odi_fc_club_name = odi
        assign_foreign_t20_elite_national_squads(
            self.all_teams, getattr(self, 'domestic_teams', None) or [], comps
        )
        self.sync_national_players_into_domestic_club_squads()
    
    def _player_on_any_international_roster(self, player):
        """True if player is on a senior or U21 list for a non-domestic country team."""
        for t in self.all_teams:
            if getattr(t, "is_domestic", False):
                continue
            if player in getattr(t, "players", []):
                return True
            if player in (getattr(t, "u21_squad", None) or []):
                return True
        return False
    
    def _domestic_team_for_nation_and_club(self, nation, club_name):
        """Resolve a domestic Team by parent nation and display name."""
        name = (club_name or "").strip()
        if not name or not nation:
            return None
        for dt in getattr(self, "domestic_teams", None) or []:
            if getattr(dt, "parent_nation", None) == nation and dt.name == name:
                return dt
        return None
    
    def _domestic_club_memberships_count(self, player):
        n = 0
        for dt in getattr(self, "domestic_teams", None) or []:
            if player in getattr(dt, "players", []):
                n += 1
        return n
    
    def _make_room_on_domestic_squad_for_international(self, dteam):
        """
        Free one slot on dteam by removing a generated domestic player.
        Prefer someone who still appears on another domestic club; else drop weakest exclusive.
        """
        def _is_generated_domestic_only(p):
            if self._player_on_any_international_roster(p):
                return False
            return True
        
        shared = [
            p for p in dteam.players
            if _is_generated_domestic_only(p) and self._domestic_club_memberships_count(p) > 1
        ]
        if shared:
            dteam.players.remove(random.choice(shared))
            return True
        exclusive = [
            p for p in dteam.players
            if _is_generated_domestic_only(p) and self._domestic_club_memberships_count(p) == 1
        ]
        if exclusive:
            exclusive.sort(key=lambda x: max(getattr(x, "batting", 0), getattr(x, "bowling", 0)))
            dteam.players.remove(exclusive[0])
            return True
        return False
    
    def player_in_u21_only_pipeline(self, player):
        """
        True if the player is only on a national U21 squad: not on senior international,
        not on any domestic club. Those players may only play U21 youth internationals until promoted.
        """
        if player is None:
            return False
        for dt in getattr(self, "domestic_teams", None) or []:
            if player in getattr(dt, "players", []):
                return False
        for team in self.all_teams:
            if getattr(team, "is_domestic", False):
                continue
            if player in getattr(team, "players", []):
                return False
        for team in self.all_teams:
            if getattr(team, "is_domestic", False):
                continue
            u21 = getattr(team, "u21_squad", None) or []
            if player in u21:
                return True
        return False
    
    def sync_national_players_into_domestic_club_squads(self):
        """
        Domestic sims use team.players only. Add each senior international list player to distinct
        domestic sides for their nation (FC/ODI and T20 when set). U21-only players are excluded
        until promoted to senior or assigned to a domestic club after season rules.
        """
        domestic_teams = getattr(self, "domestic_teams", None) or []
        if not domestic_teams:
            return

        def _remove_player_from_nation_domestic_squads(player, nation_name: str) -> None:
            for dt in domestic_teams:
                if getattr(dt, "parent_nation", None) != nation_name:
                    continue
                if player in getattr(dt, "players", []):
                    dt.players.remove(player)

        def _distinct_domestic_club_names(player):
            odi = (getattr(player, "domestic_odi_fc_club_name", None) or "").strip()
            t20 = (getattr(player, "domestic_t20_club_name", None) or "").strip()
            out = []
            seen = set()
            for cname in (odi, t20):
                if cname and cname not in seen:
                    seen.add(cname)
                    out.append(cname)
            return out

        for team in self.all_teams:
            if getattr(team, "is_domestic", False):
                continue
            nation = team.name
            to_visit = list(getattr(team, "players", []) or [])
            for player in to_visit:
                club_names = _distinct_domestic_club_names(player)
                if not club_names:
                    continue
                _remove_player_from_nation_domestic_squads(player, nation)
                for cname in club_names:
                    dt = self._domestic_team_for_nation_and_club(nation, cname)
                    if dt is None:
                        continue
                    if player in dt.players:
                        continue
                    if not dt.add_player(player):
                        if self._make_room_on_domestic_squad_for_international(dt):
                            dt.add_player(player)
    
    def get_fixtures(self, format_type):
        """Get fixtures for a specific format"""
        return self.fixtures.get(format_type, [])
    
    def get_team_by_name(self, team_name):
        """Get team by name"""
        return next((t for t in self.all_teams if t.name == team_name), None)
    
    def get_all_players(self):
        """Get all players from all teams"""
        all_players = []
        for team in self.all_teams:
            for player in team.players:
                all_players.append((player, team))
        return all_players
    
    def get_top_players(self, format_type='T20', category='Batting', limit=100):
        """
        Get top players by category
        
        Args:
            format_type: 'T20', 'ODI', 'Test', or 'Overall'
            category: 'Batting', 'Bowling', 'All-Rounder', 'Fielding'
            limit: Number of players to return
        
        Returns:
            List of (player, team, rating) tuples
        """
        all_players = self.get_all_players()
        rated_players = []
        
        for player, team in all_players:
            # Filter by category
            if category == 'Batting':
                if 'Batter' not in player.role and 'Wicketkeeper' not in player.role:
                    continue
                rating = player.batting
            elif category == 'Bowling':
                if 'Bowler' not in player.role and 'Spinner' not in player.role and 'Pacer' not in player.role:
                    continue
                rating = player.bowling
            elif category == 'All-Rounder':
                if 'All-Rounder' not in player.role:
                    continue
                rating = (player.batting + player.bowling) / 2
            else:  # Fielding
                rating = player.fielding
            
            rated_players.append((player, team, rating))
        
        # Sort by rating
        rated_players.sort(key=lambda x: x[2], reverse=True)
        
        return rated_players[:limit]
    
    def generate_fake_database(self, with_stats=True):
        """Replace all players in every international team with randomly generated players,
        then rebuild domestic leagues with generated squads only (no domestic_custom_rosters.json).

        Uses the same role distribution, age generation, skill ranges, and trait assignment
        as generate_player(). Generates exactly 20 players per international team (fake DB only).

        with_stats: When True (default), the top 20 senior players per nation (by bat+bowl+fielding)
        get synthetic international + domestic career stats; other seniors, all U21, and domestic
        club-only players get domestic_stats only (international_stats remain zero). When False,
        no synthetic career totals are filled—career stats stay at zero for all generated players.
        """
        from cricket_manager.systems.trait_assignment import assign_traits_to_player
        from cricket_manager.utils.name_generator import reset_name_tracking
        
        FAKE_DB_PLAYERS_PER_TEAM = 20
        FAKE_DB_INTL_STATS_PLAYERS = 20

        def _fake_db_overall_rating(pl):
            return (
                int(getattr(pl, "batting", 0) or 0)
                + int(getattr(pl, "bowling", 0) or 0)
                + int(getattr(pl, "fielding", 0) or 0)
            )

        # Reset name tracking to avoid stale entries from previous generations
        reset_name_tracking()
        self.career_promotions_log = []
        self.career_transfers_log = []
        
        total_generated = 0
        for team in self.all_teams:
            # Determine tier for this team (use T20 tier as reference)
            tier = team.format_tiers.get('T20', 3)
            
            # Clear existing players
            team.players = []
            
            # Generate squad with unique names within the team (20 players per team for fake DB)
            team_names = set()
            for _ in range(FAKE_DB_PLAYERS_PER_TEAM):
                player = self.generate_player(team.name, tier=tier)
                # Ensure no duplicate names within the same team
                attempts = 0
                while player.name in team_names and attempts < 50:
                    player = self.generate_player(team.name, tier=tier)
                    attempts += 1
                team_names.add(player.name)
                team.add_player(player)
                total_generated += 1

            # Fake DB safety: ensure enough players + bowling options for a playable XI.
            self._ensure_playable_team_squad(
                team,
                team.name,
                tier=max(1, min(4, int(tier or 3))),
                min_players=11,
                min_bowling_options=6,
                target_size=20,
            )
            
            # Enforce super elite cap for Tier 1 teams: max 0-4 players with 89+ bat or bowl
            if tier == 1:
                max_super_elite = random.randint(0, 4)
                super_elite_players = [p for p in team.players
                                       if p.batting >= 89 or p.bowling >= 89]
                random.shuffle(super_elite_players)
                # Keep only max_super_elite, clamp the rest below 89
                for p in super_elite_players[max_super_elite:]:
                    if p.batting >= 89:
                        p.batting = random.randint(84, 88)
                    if p.bowling >= 89:
                        p.bowling = random.randint(84, 88)
            
            # Regenerate U21 squad if youth system exists
            if hasattr(self, 'youth_system'):
                team.u21_squad = self.youth_system.generate_u21_squad(team)
        
        if with_stats:
            from cricket_manager.utils.fake_db_career_stats import (
                clear_fake_db_career_history,
                synthesize_fake_career_stats,
            )
            # Synthetic career totals: international_stats only for top N senior players per team
            for team in self.all_teams:
                senior = list(team.players)
                senior.sort(
                    key=lambda p: (_fake_db_overall_rating(p), getattr(p, "name", "")),
                    reverse=True,
                )
                intl_eligible_ids = {id(p) for p in senior[:FAKE_DB_INTL_STATS_PLAYERS]}
                for player in team.players:
                    synthesize_fake_career_stats(
                        player,
                        career_scope="international",
                        include_international_stats=(id(player) in intl_eligible_ids),
                    )
                    clear_fake_db_career_history(player)
                for player in getattr(team, "u21_squad", None) or []:
                    synthesize_fake_career_stats(
                        player,
                        career_scope="domestic",
                        include_international_stats=False,
                    )
                    clear_fake_db_career_history(player)
        
        # Rebuild domestic clubs (one team per club name) and fixtures; ignore custom roster JSON
        # so every domestic side gets the same generated treatment as international teams.
        international_names = [t.name for t in self.all_teams]
        self.domestic_system.build_domestic_teams_and_fixtures(
            international_names, force_generated_squads=True
        )
        self.domestic_teams = self.domestic_system.domestic_teams
        self.domestic_fixtures = self.domestic_system.domestic_fixtures

        # Domestic fake DB safety: ensure no domestic side is left non-playable.
        for dt in self.domestic_teams:
            nation = getattr(dt, "parent_nation", None) or getattr(dt, "name", "")
            self._ensure_playable_team_squad(
                dt,
                nation,
                tier=2,
                min_players=11,
                min_bowling_options=6,
                target_size=15,
            )

        intl_player_ids = set()
        for team in self.all_teams:
            for player in team.players:
                intl_player_ids.add(id(player))
            for player in getattr(team, "u21_squad", None) or []:
                intl_player_ids.add(id(player))
        if with_stats:
            from cricket_manager.utils.fake_db_career_stats import (
                clear_fake_db_career_history,
                synthesize_fake_career_stats,
            )
            for dt in self.domestic_teams:
                for player in getattr(dt, "players", None) or []:
                    if id(player) in intl_player_ids:
                        continue
                    synthesize_fake_career_stats(
                        player,
                        career_scope="domestic",
                        include_international_stats=False,
                    )
                    clear_fake_db_career_history(player)
        
        self.assign_domestic_affiliations_all_players()
        
        # Regenerate fixtures for new teams
        wc_month = self._get_wc_month(self.current_season)
        self.fixtures = self.tier_manager.generate_all_fixtures(
            wc_month=wc_month, current_season=self.current_season
        )
        self.generate_world_cup_fixtures()
        
        domestic_players = sum(len(getattr(t, "players", []) or []) for t in self.domestic_teams)
        stats_note = "with synthetic career stats" if with_stats else "without synthetic career stats"
        print(
            f"[GameEngine] Fake database generated ({stats_note}): {total_generated} international players "
            f"({len(self.all_teams)} teams), {domestic_players} domestic club players "
            f"({len(self.domestic_teams)} clubs)"
        )
        return total_generated
    
    def save_game(self, filename):
        """Save game state to file"""
        import pickle
        
        _udom = getattr(self, 'user_domestic_team', None)
        game_state = {
            'current_season': self.current_season,
            'current_year': self.current_year,
            'all_teams': self.all_teams,
            'user_team_name': self.user_team.name if self.user_team else None,
            'fixtures': self.fixtures,
            'match_scorecards': self.match_scorecards,
            'world_cup_history': self.world_cup_history,
            'tier_manager': self.tier_manager,
            'simulation_settings': getattr(self, 'simulation_settings', {}),
            'head_to_head': getattr(self, 'head_to_head', {}),
            'difficulty': getattr(self, 'difficulty', 'Normal'),
            'season_awards': getattr(self, 'season_awards', {}),
            'hide_batting_bowling_ratings': getattr(self, 'hide_batting_bowling_ratings', False),
            'domestic_teams': getattr(self, 'domestic_teams', []),
            'domestic_fixtures': getattr(self, 'domestic_fixtures', {'T20': [], 'ODI': [], 'Test': []}),
            'user_domestic_team_name': _udom.name if _udom is not None else None,
            'league_standings_history': getattr(self, 'league_standings_history', []),
            'career_promotions_log': getattr(self, 'career_promotions_log', []),
            'career_transfers_log': getattr(self, 'career_transfers_log', []),
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(game_state, f)
        
        print(f"[GameEngine] Game saved to {filename}")
    
    def load_game(self, filename):
        """Load game state from file"""
        import pickle
        
        with open(filename, 'rb') as f:
            game_state = pickle.load(f)
        
        self.current_season = game_state['current_season']
        self.current_year = game_state['current_year']
        self.all_teams = game_state['all_teams']
        self.fixtures = game_state['fixtures']
        self.match_scorecards = game_state['match_scorecards']
        self.world_cup_history = game_state['world_cup_history']
        self.tier_manager = game_state['tier_manager']
        
        # Restore simulation settings (slider values)
        self.simulation_settings = game_state.get('simulation_settings', {})
        self.head_to_head = game_state.get('head_to_head', {})
        self.difficulty = game_state.get('difficulty', 'Normal')
        self.season_awards = game_state.get('season_awards', {})
        self.hide_batting_bowling_ratings = game_state.get('hide_batting_bowling_ratings', False)
        self.domestic_teams = game_state.get('domestic_teams', [])
        self.domestic_fixtures = game_state.get('domestic_fixtures', {'T20': [], 'ODI': [], 'Test': []})
        self.domestic_system.domestic_teams = self.domestic_teams
        self.domestic_system.domestic_fixtures = self.domestic_fixtures
        self.domestic_system.game_engine = self
        self.league_standings_history = game_state.get('league_standings_history', [])
        self.career_promotions_log = game_state.get('career_promotions_log', [])
        self.career_transfers_log = game_state.get('career_transfers_log', [])
        
        # Restore user team
        user_team_name = game_state.get('user_team_name')
        if user_team_name:
            self.user_team = self.get_team_by_name(user_team_name)
        user_domestic_name = game_state.get('user_domestic_team_name')
        self.user_domestic_team = None
        if user_domestic_name and self.domestic_teams:
            for t in self.domestic_teams:
                if t.name == user_domestic_name:
                    self.user_domestic_team = t
                    break
        
        def _migrate_player_save_fields(player):
            from cricket_manager.core.player import _fresh_career_stats
            if not hasattr(player, 'yearly_stats'):
                player.yearly_stats = {}
            if not hasattr(player, 'morale'):
                player.morale = 50
            if not hasattr(player, 'last_5_batting'):
                player.last_5_batting = []
            if not hasattr(player, 'last_5_bowling'):
                player.last_5_bowling = []
            if not hasattr(player, 'squad_role'):
                player.squad_role = None
            if not hasattr(player, 'milestones'):
                player.milestones = []
            if not hasattr(player, 'u21_career_stats'):
                player.u21_career_stats = None
            if not hasattr(player, 'u21_yearly_stats'):
                player.u21_yearly_stats = None
            if not hasattr(player, 'international_stats') or player.international_stats is None:
                player.international_stats = copy.deepcopy(player.stats)
            if not hasattr(player, 'international_yearly_stats') or player.international_yearly_stats is None:
                ys = getattr(player, 'yearly_stats', None) or {}
                player.international_yearly_stats = copy.deepcopy(ys) if ys else {}
            if not hasattr(player, 'domestic_stats') or player.domestic_stats is None:
                player.domestic_stats = _fresh_career_stats()
            if not hasattr(player, 'domestic_yearly_stats') or player.domestic_yearly_stats is None:
                player.domestic_yearly_stats = {}
            if not hasattr(player, 'domestic_t20_club_name'):
                player.domestic_t20_club_name = ''
            if not hasattr(player, 'domestic_odi_fc_club_name'):
                player.domestic_odi_fc_club_name = ''
            if not hasattr(player, 'foreign_t20_club_name'):
                player.foreign_t20_club_name = ''
            if not hasattr(player, '_annual_skill_development_season'):
                player._annual_skill_development_season = None
            if not hasattr(player, 'u21_international_stats') or player.u21_international_stats is None:
                player.u21_international_stats = _fresh_career_stats()
            if not hasattr(player, 'u21_international_yearly_stats') or player.u21_international_yearly_stats is None:
                player.u21_international_yearly_stats = {}
            if not hasattr(player, 'clear_intl_rank_until_next_match'):
                player.clear_intl_rank_until_next_match = False
            if not hasattr(player, 'associate_international_stats') or player.associate_international_stats is None:
                player.associate_international_stats = _fresh_career_stats()
            if not hasattr(player, 'associate_international_yearly_stats') or player.associate_international_yearly_stats is None:
                player.associate_international_yearly_stats = {}
        
        # Ensure all players have yearly_stats (for saves from before this feature)
        for team in self.all_teams:
            for player in team.players:
                _migrate_player_save_fields(player)
            if hasattr(team, 'u21_squad') and team.u21_squad:
                for player in team.u21_squad:
                    _migrate_player_save_fields(player)
        for team in getattr(self, 'domestic_teams', None) or []:
            for player in getattr(team, 'players', None) or []:
                _migrate_player_save_fields(player)
            if hasattr(team, 'u21_squad') and team.u21_squad:
                for player in team.u21_squad:
                    _migrate_player_save_fields(player)
            if not hasattr(team, 'team_records') or team.team_records is None:
                team.team_records = {'highest_total': None, 'lowest_total': None, 'biggest_win_runs': None, 'biggest_win_wickets': None}
            if not hasattr(team, 'selected_xi_names'):
                team.selected_xi_names = None
            if not hasattr(team, 'batting_order_names'):
                team.batting_order_names = None
            if not hasattr(team, 'captain_name'):
                team.captain_name = None
            if not hasattr(team, 'vice_captain_name'):
                team.vice_captain_name = None
        
        self.fill_missing_domestic_club_names()
        self.remove_duplicate_players()
        
        print(f"[GameEngine] Game loaded from {filename}")
        print(f"[GameEngine] Season {self.current_season}, Year {self.current_year}")
        print(f"[GameEngine] Simulation settings: {self.simulation_settings}")

    def _reset_domestic_fixtures_for_new_season(self):
        """
        Mark all domestic league fixtures unplayed for the upcoming season.
        International fixtures are replaced wholesale in generate_all_fixtures; domestic lists
        persist, so we must clear completion state or domestic matches never run again and
        domestic_stats / domestic_yearly_stats stop accumulating.
        """
        df = getattr(self, "domestic_fixtures", None) or {}
        n = 0
        for fmt in ("T20", "ODI", "Test"):
            for f in df.get(fmt) or []:
                if not isinstance(f, dict):
                    continue
                if f.get("completed"):
                    n += 1
                f["completed"] = False
                f.pop("winner", None)
                f.pop("margin", None)
                f.pop("scorecard", None)
        if n:
            print(f"[Season] Reset {n} domestic fixtures for the new season (completion flags cleared)")

    def _maybe_reopen_domestic_leagues(self):
        """
        If international play still has unplayed fixtures but every domestic match in every format
        is marked completed, domestic flags were never cleared (e.g. partial save or code path
        skipped complete_season). Re-open domestic leagues so simulate_season runs them again.
        """
        intl_remaining = sum(
            1
            for ft in ("T20", "ODI", "Test")
            for f in (self.fixtures.get(ft) or [])
            if not f.get("completed", False)
        )
        if intl_remaining == 0:
            return
        for ft in ("T20", "ODI", "Test"):
            dlist = self.domestic_fixtures.get(ft) or []
            if not dlist:
                continue
            if any(not f.get("completed", False) for f in dlist):
                return
        self._reset_domestic_fixtures_for_new_season()
        print(
            "[Season] Domestic leagues were all marked complete while international fixtures "
            "remain — cleared domestic completion flags so club seasons run again."
        )

    # ========================================================================
    # SEASON SIMULATION - STEP 9B
    # ========================================================================
    
    def simulate_season(self, format_type='T20', headless=True, progress_callback=None, skip_aging=False):
        """
        Simulate all matches for a season in the specified format
        
        Args:
            format_type: 'T20', 'ODI', or 'Test'
            headless: If True, run without UI updates
            progress_callback: Optional callback function(message, progress_percent)
            skip_aging: If True, skip aging players (used when simulating multiple formats in one season)
        
        Returns:
            Season summary dictionary
        """
        
        print(f"\n{'='*60}")
        print(f"SIMULATING SEASON {self.current_season} - {format_type}")
        print(f"{'='*60}\n")
        
        # Remove duplicate players from all teams
        self.remove_duplicate_players()

        self._maybe_reopen_domestic_leagues()
        
        # Reset season tracking
        self.season_retirements = []
        self.season_promotions = []
        self.season_changes = []
        self.season_matches = []
        self.season_transfers = []
        
        # Step 1: Simulate tier matches (skip already completed)
        print(f"[Season] Step 1: Simulating {format_type} tier matches...")
        fixtures = self.fixtures[format_type]
        total_matches = len(fixtures)
        remaining_matches = sum(1 for f in fixtures if not f.get('completed', False))
        
        print(f"[Season] Total fixtures: {total_matches}, Remaining: {remaining_matches}")
        
        domestic_fixtures = self.domestic_fixtures.get(format_type) or []
        remaining_domestic = sum(1 for f in domestic_fixtures if not f.get('completed', False))
        total_this_format = remaining_matches + remaining_domestic
        simulated_count = 0
        
        for idx, fixture in enumerate(fixtures):
            # Skip already completed matches
            if fixture.get('completed', False):
                continue
            
            if progress_callback:
                progress = (simulated_count / max(1, total_this_format)) * 100
                progress_callback(
                    f"Simulating match {simulated_count + 1}/{total_this_format} ({format_type})",
                    progress,
                )
            
            # Simulate match
            result = self.simulate_match(fixture, format_type, headless)
            
            # Skip if simulation failed (e.g., missing teams)
            if result is None:
                continue
            
            # Check if this is a U21 fixture
            is_u21 = fixture.get('is_u21', False) or (fixture.get('team1') is None and fixture.get('team2') is None)
            
            if is_u21:
                # U21 fixtures - use tier from fixture directly
                tier = fixture.get('tier', 5)
                home_name = fixture.get('home', 'Unknown U21')
                away_name = fixture.get('away', 'Unknown U21')
            else:
                # Regular fixtures - get tier from home team's format tier
                home_team = fixture['team1']
                tier = home_team.format_tiers.get(format_type, 1) if home_team else fixture.get('tier', 1)
                home_name = fixture['team1'].name
                away_name = fixture['team2'].name
            
            # Track for summary with FULL scorecard
            scorecard = result.get('scorecard', {})
            self.season_matches.append({
                'home': home_name,
                'away': away_name,
                'format': format_type,
                'tier': tier,  # <-- ADDED: Store tier info for filtering
                'winner': result.get('winner', 'Draw'),
                'margin': result.get('margin', ''),
                'man_of_the_match': scorecard.get('man_of_the_match', ''),
                'result': result  # Full result including scorecard
            })
            
            simulated_count += 1
            
            if not headless and simulated_count % 50 == 0:
                print(f"  Completed {simulated_count}/{total_this_format} matches")
        
        print(f"[Season] Completed {simulated_count} international tier matches "
              f"({total_matches - remaining_matches} were already played before this run)")
        
        # Step 1b: Domestic league fixtures (same format — club teams with is_domestic)
        if domestic_fixtures and remaining_domestic > 0:
            print(f"[Season] Step 1b: Simulating {remaining_domestic} domestic {format_type} matches...")
        dom_simulated = 0
        for fixture in domestic_fixtures:
            if fixture.get('completed', False):
                continue
            
            if progress_callback:
                progress = (simulated_count / max(1, total_this_format)) * 100
                progress_callback(
                    f"Domestic {format_type}: {dom_simulated + 1}/{remaining_domestic}",
                    progress,
                )
            
            result = self.simulate_match(fixture, format_type, headless)
            if result is None:
                continue
            
            home_team = fixture['team1']
            away_team = fixture['team2']
            home_name = home_team.name
            away_name = away_team.name
            scorecard = result.get('scorecard', {})
            self.season_matches.append({
                'home': home_name,
                'away': away_name,
                'format': format_type,
                'tier': 0,
                'winner': result.get('winner', 'Draw'),
                'margin': result.get('margin', ''),
                'man_of_the_match': scorecard.get('man_of_the_match', ''),
                'result': result,
                'match_type': 'domestic',
                'nation': fixture.get('nation'),
                'competition_name': fixture.get('competition_name'),
            })
            
            simulated_count += 1
            dom_simulated += 1
        
        if domestic_fixtures and dom_simulated > 0:
            print(f"[Season] Completed {dom_simulated} domestic {format_type} matches this run")
        
        # Step 2: Simulate youth matches
        print(f"[Season] Step 2: Simulating youth matches...")
        youth_matches = self.simulate_youth_matches(format_type)
        print(f"[Season] Completed {youth_matches} youth matches")
        
        # Step 3: Execute World Cup (4-year cycle)
        # Year 1: T20 World Cup
        # Year 2: ODI World Cup  
        # Year 3: U19 World Cup
        # Year 4: Associate World Cup
        world_cup_results = None
        wc_cycle = (self.current_season - 1) % 4  # 0, 1, 2, 3
        
        wc_types = ['T20', 'ODI', 'U19', 'Associate']
        wc_names = ['T20 World Cup', 'ODI World Cup', 'U19 World Cup', 'Associate World Cup']
        
        should_run_wc = False
        wc_format = None
        wc_name = None
        
        if wc_cycle == 0 and format_type == 'T20':  # T20 WC runs in T20 format
            should_run_wc = True
            wc_format = 'T20'
            wc_name = 'T20 World Cup'
        elif wc_cycle == 1 and format_type == 'ODI':  # ODI WC runs in ODI format
            should_run_wc = True
            wc_format = 'ODI'
            wc_name = 'ODI World Cup'
        elif wc_cycle == 2 and format_type == 'ODI':  # U19 WC runs in ODI format
            should_run_wc = True
            wc_format = 'ODI'
            wc_name = 'U19 World Cup'
        elif wc_cycle == 3 and format_type == 'ODI':  # Associate WC runs in ODI format
            should_run_wc = True
            wc_format = 'ODI'
            wc_name = 'Associate World Cup'
        
        if should_run_wc:
            print(f"[Season] Step 3: Executing {wc_name}...")
            world_cup_results = self.execute_world_cup(wc_format, wc_name)
            
            # Add World Cup matches to season matches (for stats tracking)
            if 'matches' in world_cup_results:
                self.season_matches.extend(world_cup_results['matches'])
                # Note: fixtures are already updated in-place by execute_world_cup
                # (group matches updated in-place, semi/final appended directly)
            
            # Collect final scorecard and all WC scorecards for stats
            _wc_fmt = wc_format if wc_format else 'T20'
            wc_all = [f for f in self.fixtures.get(_wc_fmt, []) if f.get('is_world_cup')]
            final_fixture = next((f for f in wc_all if f.get('round') == 'Final' and f.get('completed')), None)
            final_scorecard = final_fixture.get('scorecard', {}) if final_fixture else {}
            final_score = ''
            if final_scorecard and 'innings' in final_scorecard:
                inns = final_scorecard['innings']
                if len(inns) >= 2:
                    t1 = f"{inns[0].get('batting_team', '')} {inns[0].get('total_runs', 0)}/{inns[0].get('wickets_fallen', 0)}"
                    t2 = f"{inns[1].get('batting_team', '')} {inns[1].get('total_runs', 0)}/{inns[1].get('wickets_fallen', 0)}"
                    final_score = f"{t1}  vs  {t2}"
            
            # Collect all completed WC scorecards for top batters/bowlers
            wc_scorecards = [f.get('scorecard', {}) for f in wc_all if f.get('completed') and f.get('scorecard')]
            
            # Store in history
            self.world_cup_history.append({
                'season': self.current_season,
                'year': self.current_year,
                'format': _wc_fmt,
                'tournament': wc_name,
                'winner': world_cup_results['winner'],
                'runner_up': world_cup_results['runner_up'],
                'host': getattr(self, 'wc_host', 'Various'),
                'final_score': final_score,
                'final_scorecard': final_scorecard,
                'wc_scorecards': wc_scorecards,
            })
            
            print(f"[Season] World Cup Winner: {world_cup_results['winner']}")
        else:
            print(f"[Season] Step 3: No World Cup this season ({format_type})")
        
        # Step 4: Process retirements — only once per year (final format) to avoid
        # cascading depletion across T20/ODI/Test simulate_season calls.
        if not skip_aging:
            print(f"[Season] Step 4: Processing retirements...")
            for team in self.all_teams:
                retirements = self.process_retirements(team)
                self.season_retirements.extend(retirements)
            for team in getattr(self, "domestic_teams", None) or []:
                retirements = self.process_retirements(team)
                self.season_retirements.extend(retirements)
            print(f"[Season] {len(self.season_retirements)} players retired")
            
            # Immediately refill depleted squads so no team sits below 11 players
            for team in self.all_teams:
                if getattr(team, "is_domestic", False):
                    continue
                if len(team.players) < 15:
                    before = len(team.players)
                    self.fill_national_squad_from_domestic_and_u21(team, 20)
                    after = len(team.players)
                    if after > before:
                        print(f"[Season] Refilled {team.name}: {before} → {after} players after retirements")
            
            # Top up U21 squads that may have been drained by national call-ups
            for team in self.all_teams:
                self.youth_system.ensure_u21_squad_strength(team)
        else:
            print(f"[Season] Step 4: Skipping retirements (will run on final format)")
        
        # Step 6: Check role conversions (Phase 10)
        print(f"[Season] Step 6: Checking role conversions...")
        role_conversions = self.role_conversion.check_all_teams(self.all_teams)
        total_conversions = sum(len(convs) for convs in role_conversions.values())
        print(f"[Season] {total_conversions} role conversions")
        
        # Step 7: Generate team news (Phase 10)
        print(f"[Season] Step 7: Generating team news...")
        self.news_system.clear_news()
        self.news_system.generate_season_news(self.all_teams, format_type)
        self.news_system.add_role_conversion_news(role_conversions)
        self.news_system.add_retirement_news(self.season_retirements)
        print(f"[Season] Generated {len(self.news_system.news_items)} news items")
        
        # Season awards (Batter, Bowler, Young Player of the season)
        try:
            from cricket_manager.systems.gameplay_features import compute_season_awards
            compute_season_awards(self)
        except Exception as e:
            print(f"[Season] compute_season_awards error: {e}")
        
        # Prepare season summary
        summary = {
            'season': self.current_season,
            'year': self.current_year,
            'format': format_type,
            'total_matches': total_matches,
            'youth_matches': youth_matches,
            'retirements': self.season_retirements,
            'role_conversions': role_conversions,
            'news_items': self.news_system.get_top_news(10),
            'world_cup': world_cup_results,
            'matches': self.season_matches,
            'season_awards': getattr(self, 'season_awards', {})
        }
        
        print(f"\n{'='*60}")
        print(f"SEASON {self.current_season} SIMULATION COMPLETE")
        print(f"{'='*60}\n")
        
        return summary
    
    def simulate_match(self, fixture, format_type, headless=True):
        """
        Simulate a single match using fast simulator
        
        Args:
            fixture: Fixture dictionary with team1, team2, home_team
            format_type: 'T20', 'ODI', or 'Test'
            headless: If True, use fast simulator (always True for season sim)
        
        Returns:
            Match result dictionary
        """
        # Check if this is a U21 fixture
        is_u21 = fixture.get('is_u21', False) or (fixture.get('team1') is None and fixture.get('team2') is None)
        home_parent = None
        away_parent = None
        
        if is_u21:
            # U21 fixtures use parent teams' U21 squads
            home_parent = fixture.get('home_parent') or fixture.get('home_team')
            away_parent = fixture.get('away_parent')
            
            if not home_parent or not away_parent:
                print(f"[simulate_match] ERROR: U21 fixture missing parent teams")
                return None
            
            # Create temporary U21 team objects - use deep copy of players
            from cricket_manager.core.team import Team
            
            home_name = fixture.get('home', f"{home_parent.name} U21")
            away_name = fixture.get('away', f"{away_parent.name} U21")
            
            team1 = Team(name=home_name, tier=5)
            # Create new player objects to avoid reference issues
            if hasattr(home_parent, 'u21_squad') and home_parent.u21_squad:
                import copy
                team1.players = copy.deepcopy(home_parent.u21_squad[:11])
            else:
                team1.players = []
            
            team2 = Team(name=away_name, tier=5)
            if hasattr(away_parent, 'u21_squad') and away_parent.u21_squad:
                import copy
                team2.players = copy.deepcopy(away_parent.u21_squad[:11])
            else:
                team2.players = []
            
            # Validate U21 squads have enough players
            if len(team1.players) < 11:
                print(f"[simulate_match] WARNING: {home_name} has only {len(team1.players)} players")
            if len(team2.players) < 11:
                print(f"[simulate_match] WARNING: {away_name} has only {len(team2.players)} players")
        else:
            # Regular fixture - extract teams directly
            team1 = fixture['team1']
            team2 = fixture['team2']
        
        # Get format-specific simulation adjustments
        sim_adj = self._get_simulation_adjustments(format_type)
        
        # Extract pitch conditions from fixture (set by host country region)
        pitch_conditions = None
        if fixture.get('pitch_bounce') is not None:
            pitch_conditions = {
                'pitch_bounce': fixture['pitch_bounce'],
                'pitch_spin': fixture.get('pitch_spin', 5),
                'pitch_pace': fixture.get('pitch_pace', 5),
            }
        elif fixture.get('pitch_conditions'):
            pc = fixture['pitch_conditions']
            pitch_conditions = {
                'pitch_bounce': pc.get('pitch_bounce', 5),
                'pitch_spin': pc.get('pitch_spin', 5),
                'pitch_pace': pc.get('pitch_pace', 5),
            }
        
        # Use fast simulator for season simulation
        simulator = FastMatchSimulator(
            team1=team1,
            team2=team2,
            match_format=format_type,
            simulation_adjustments=sim_adj,
            pitch_conditions=pitch_conditions
        )
        
        # Simulate match (returns winner Team object)
        winner_team = simulator.simulate()
        
        # Get full scorecard
        scorecard = simulator.get_scorecard()
        
        # Create result dictionary
        result = {
            'winner': winner_team.name if winner_team else 'Draw',
            'team1': team1.name,
            'team2': team2.name,
            'format': format_type,
            'margin': simulator.margin,
            'scorecard': scorecard
        }
        
        # Store scorecard
        scorecard_key = (
            team1.name,
            team2.name,
            self.current_season,
            format_type
        )
        self.match_scorecards[scorecard_key] = scorecard
        
        # Mark fixture as completed
        fixture['completed'] = True
        fixture['winner'] = result['winner']
        fixture['margin'] = result['margin']
        
        # Update team stats
        self.update_team_stats(team1, team2, result, format_type)
        
        # Update player career stats from match
        self._update_player_career_stats(scorecard, team1, team2, format_type)
        
        # U21: sync updated stats from temporary copy players back to parent teams' u21_squad
        if is_u21 and home_parent and away_parent:
            self._sync_u21_match_stats_to_parent_squads(team1, team2, home_parent, away_parent)
            self._update_u21_team_stats_from_match(home_parent, away_parent, team1.name, team2.name, scorecard, result, format_type)
        
        # Post-match gameplay features: injuries, morale, last_5, records, POTM, H2H, milestones
        try:
            from cricket_manager.systems.gameplay_features import (
                roll_injuries_after_match,
                update_morale_after_match,
                update_last_5,
                update_team_records,
                calculate_potm,
                update_head_to_head,
                check_and_add_player_milestones,
            )
            winner_name = result['winner']
            team1_name, team2_name = team1.name, team2.name
            innings_list = scorecard.get('innings', [])
            t1_total = sum(inn['total_runs'] for inn in innings_list if inn.get('batting_team') == team1_name)
            t2_total = sum(inn['total_runs'] for inn in innings_list if inn.get('batting_team') == team2_name)
            t1_wickets = sum(inn['wickets_fallen'] for inn in innings_list if inn.get('batting_team') == team1_name)
            t2_wickets = sum(inn['wickets_fallen'] for inn in innings_list if inn.get('batting_team') == team2_name)
            home_team_name = fixture.get('home_team') or fixture.get('home') or team1_name
            if hasattr(home_team_name, 'name'):
                home_team_name = home_team_name.name
            is_team1_home = (home_team_name == team1_name)
            res1 = 'win' if winner_name == team1_name else ('loss' if winner_name == team2_name else 'draw')
            res2 = 'win' if winner_name == team2_name else ('loss' if winner_name == team1_name else 'draw')
            roll_injuries_after_match(team1, format_type, self.difficulty)
            roll_injuries_after_match(team2, format_type, self.difficulty)
            update_morale_after_match(team1, res1, is_home=is_team1_home)
            update_morale_after_match(team2, res2, is_home=not is_team1_home)
            match_stats = scorecard.get('match_stats', {})
            t1_players = {p.name: p for p in team1.players}
            t2_players = {p.name: p for p in team2.players}
            for pname, data in match_stats.items():
                p = t1_players.get(pname) or t2_players.get(pname)
                if p:
                    bat = data.get('batting', {})
                    bowl = data.get('bowling', {})
                    update_last_5(p, bat.get('runs'), bowl.get('wickets'))
            margin_runs = margin_wickets = None
            if 'runs' in str(result.get('margin', '')):
                try:
                    margin_runs = int(str(result['margin']).split()[0])
                except (ValueError, IndexError):
                    pass
            if 'wicket' in str(result.get('margin', '')).lower():
                try:
                    margin_wickets = int(str(result['margin']).split()[0])
                except (ValueError, IndexError):
                    pass
            if hasattr(team1, 'team_records') and team1.team_records is not None:
                update_team_records(self, team1, team2_name, t1_total, t1_wickets, format_type, res1, margin_runs if res1 == 'win' else None, margin_wickets if res1 == 'win' else None)
            if hasattr(team2, 'team_records') and team2.team_records is not None:
                update_team_records(self, team2, team1_name, t2_total, t2_wickets, format_type, res2, margin_runs if res2 == 'win' else None, margin_wickets if res2 == 'win' else None)
            self.last_match_potm = calculate_potm(scorecard, team1_name, team2_name)
            if self.last_match_potm:
                scorecard['potm'] = self.last_match_potm
            update_head_to_head(self, team1_name, team2_name, res1)
            for pname in match_stats:
                p = t1_players.get(pname) or t2_players.get(pname)
                if p:
                    check_and_add_player_milestones(self, p, team1_name if p in team1.players else team2_name)
        except Exception as e:
            print(f"[simulate_match] gameplay_features error: {e}")
        
        return result
    
    def _get_simulation_adjustments(self, format_type):
        """Get format-specific simulation adjustments from settings"""
        prefix = format_type.lower()
        try:
            from cricket_manager.systems.gameplay_features import get_difficulty_modifier_batting, get_difficulty_modifier_bowling
            diff_bat = get_difficulty_modifier_batting(self)
            diff_bowl = get_difficulty_modifier_bowling(self)
        except Exception:
            diff_bat = diff_bowl = 1.0
        return {
            'dot_adj': self.simulation_settings.get(f'{prefix}_dot_adj', 0),
            'boundary_adj': self.simulation_settings.get(f'{prefix}_boundary_adj', 0),
            'wicket_adj': self.simulation_settings.get(f'{prefix}_wicket_adj', 0),
            'difficulty_bat': diff_bat,
            'difficulty_bowl': diff_bowl,
        }
    
    def _accumulate_u21_only_career_from_scorecard_line(
        self,
        player,
        format_type,
        player_name,
        batting,
        bowling,
        dismissals_per_player,
        innings_per_player,
    ):
        """U21-only pipeline: update u21_international_* only (no combined/senior/domestic)."""
        u21stats = None
        if getattr(player, 'u21_international_stats', None) is not None:
            if format_type in player.u21_international_stats:
                u21stats = player.u21_international_stats[format_type]
        if u21stats is None:
            return
        runs_scored = batting.get('runs', 0)
        balls_faced = batting.get('balls', 0)
        wickets_taken = bowling.get('wickets', 0)
        balls_bowled = bowling.get('balls', 0)
        runs_conceded = bowling.get('runs', 0)
        player_participated = False
        if runs_scored > 0 or balls_faced > 0:
            u21stats['runs'] += runs_scored
            u21stats['balls_faced'] += balls_faced
            player_participated = True
            if runs_scored >= 50:
                u21stats['fifties'] += 1
            if runs_scored >= 100:
                u21stats['centuries'] += 1
            if runs_scored > u21stats.get('highest_score', 0):
                u21stats['highest_score'] = runs_scored
        if format_type == 'Test' and player_name in dismissals_per_player:
            d_add = dismissals_per_player[player_name]
            u21stats['dismissals'] = u21stats.get('dismissals', 0) + d_add
        if wickets_taken > 0 or balls_bowled > 0:
            u21stats['wickets'] += wickets_taken
            u21stats['balls_bowled'] += balls_bowled
            u21stats['runs_conceded'] += runs_conceded
            player_participated = True
            if wickets_taken >= 5:
                u21stats['five_wickets'] += 1
        if player_participated:
            u21stats['matches'] += 1
            if format_type == 'Test':
                player_innings = innings_per_player.get(player_name, 0)
                inn_add = max(1, player_innings)
                u21stats['innings'] = u21stats.get('innings', 0) + inn_add
        if hasattr(player, 'u21_international_yearly_stats') and player_participated:
            year = self.current_year
            if year not in player.u21_international_yearly_stats:
                player.u21_international_yearly_stats[year] = {}
            if format_type not in player.u21_international_yearly_stats[year]:
                player.u21_international_yearly_stats[year][format_type] = {
                    'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                    'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                    'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                }
            uys = player.u21_international_yearly_stats[year][format_type]
            uys['matches'] += 1
            uys['runs'] += runs_scored
            uys['balls_faced'] += balls_faced
            uys['wickets'] += wickets_taken
            uys['balls_bowled'] += balls_bowled
            uys['runs_conceded'] += runs_conceded
            if format_type == 'Test' and player_name in dismissals_per_player:
                uys['dismissals'] = uys.get('dismissals', 0) + dismissals_per_player[player_name]
            if runs_scored > uys['highest_score']:
                uys['highest_score'] = runs_scored
            if runs_scored >= 100:
                uys['centuries'] += 1
            if runs_scored >= 50:
                uys['fifties'] += 1
            if wickets_taken >= 5:
                uys['five_wickets'] += 1
        self._recalculate_player_averages(player, format_type)
    
    def _clear_intl_rank_flag_if_national_squad(self, player, team1, team2):
        """Clear clear_intl_rank_until_next_match after a senior international cap for the player's nationality."""
        if not getattr(player, "clear_intl_rank_until_next_match", False):
            return
        nat = (getattr(player, "nationality", None) or "").strip()
        if not nat:
            return
        n1 = getattr(team1, "name", "") or ""
        n2 = getattr(team2, "name", "") or ""
        if nat == n1 or nat == n2:
            player.clear_intl_rank_until_next_match = False
    
    def _player_team_in_senior_match(self, player, team1, team2):
        if player in getattr(team1, "players", []) or []:
            return team1
        if player in getattr(team2, "players", []) or []:
            return team2
        return None

    @staticmethod
    def _is_associate_national_team(team):
        if not team or getattr(team, "is_domestic", False):
            return False
        return getattr(team, "format_tiers", {}).get("Test", 1) != 1

    def _senior_international_split(self, player, team1, team2, count_as_senior_international):
        """Which senior buckets apply: full-member international vs associate international."""
        if not count_as_senior_international:
            return False, False
        mt = self._player_team_in_senior_match(player, team1, team2)
        if mt is None:
            return True, False
        if self._is_associate_national_team(mt):
            return False, True
        return True, False

    def _update_player_career_stats(self, scorecard, team1, team2, format_type):
        """Update player career statistics after a match"""
        print(f"[_update_player_career_stats] Updating stats for {format_type} match")
        
        # Get player name to player object mappings
        team1_players = {p.name: p for p in team1.players}
        team2_players = {p.name: p for p in team2.players}
        all_players = {**team1_players, **team2_players}
        
        # International-only stats mirror: domestic fixtures do not count toward international_* totals.
        # U21 youth internationals (Pakistan U21 vs …) use u21_international_* only, not senior caps.
        count_as_domestic = (
            getattr(team1, 'is_domestic', False) or getattr(team2, 'is_domestic', False)
        )
        is_u21_match = (not count_as_domestic) and (
            (getattr(team1, "name", "") or "").endswith(" U21")
            or (getattr(team2, "name", "") or "").endswith(" U21")
        )
        count_as_senior_international = (not count_as_domestic) and (not is_u21_match)
        
        print(f"[_update_player_career_stats] Team1: {len(team1_players)} players, Team2: {len(team2_players)} players")
        
        # For Test matches, we need to count dismissals and innings from each innings
        dismissals_per_player = {}
        innings_per_player = {}  # Track how many innings each player batted in
        
        if format_type == 'Test':
            # Get per-innings stats to count dismissals and innings properly
            innings_stats_list = scorecard.get('innings', [])
            
            for innings in innings_stats_list:
                batting_card = innings.get('batting_card', [])
                for batter in batting_card:
                    player_name = batter.get('name', '')
                    if not player_name:
                        continue
                    
                    # Count this as an innings if player batted (faced balls or scored runs)
                    balls = batter.get('balls', 0)
                    runs = batter.get('runs', 0)
                    if balls > 0 or runs > 0:
                        innings_per_player[player_name] = innings_per_player.get(player_name, 0) + 1
                    
                    # Count dismissal (case-insensitive: not out / did not bat = not dismissed)
                    dismissal = (batter.get('dismissal') or '').strip().lower()
                    if dismissal and dismissal not in ('not out', 'did not bat'):
                        dismissals_per_player[player_name] = dismissals_per_player.get(player_name, 0) + 1
            
            print(f"[_update_player_career_stats] Test match innings: {innings_per_player}")
            print(f"[_update_player_career_stats] Test match dismissals: {dismissals_per_player}")
        
        # Get match stats from scorecard (cumulative for all innings)
        match_stats = scorecard.get('match_stats', {})
        print(f"[_update_player_career_stats] Match stats entries: {len(match_stats)}")
        
        # Get all players who were in the playing XI (from all innings)
        playing_xi_players = set()
        for innings in scorecard.get('innings', []):
            batting_xi = innings.get('batting_xi', [])
            for player_name in batting_xi:
                playing_xi_players.add(player_name)
        
        print(f"[_update_player_career_stats] Playing XI members: {len(playing_xi_players)}")
        
        updated_count = 0
        match_count_only = 0
        
        # First, update players who batted or bowled (have match_stats)
        for player_name, stats in match_stats.items():
            if player_name not in all_players:
                print(f"[_update_player_career_stats] Player {player_name} not found in teams")
                continue
                
            player = all_players[player_name]
            batting = stats.get('batting', {})
            bowling = stats.get('bowling', {})
            
            print(f"[_update_player_career_stats] Updating {player_name}: runs={batting.get('runs', 0)}, wickets={bowling.get('wickets', 0)}")
            
            # Get format-specific stats from player.stats
            if format_type not in player.stats:
                print(f"[_update_player_career_stats] Format {format_type} not in player.stats")
                continue
                
            pstats = player.stats[format_type]
            senior_full, senior_assoc = self._senior_international_split(player, team1, team2, count_as_senior_international)
            senior_stat_dicts = []
            if senior_full and getattr(player, 'international_stats', None) and format_type in player.international_stats:
                senior_stat_dicts.append(player.international_stats[format_type])
            if senior_assoc and getattr(player, 'associate_international_stats', None) and format_type in player.associate_international_stats:
                senior_stat_dicts.append(player.associate_international_stats[format_type])
            u21stats = None
            dstats = None
            if is_u21_match and getattr(player, 'u21_international_stats', None) is not None:
                if format_type in player.u21_international_stats:
                    u21stats = player.u21_international_stats[format_type]
            if count_as_domestic and getattr(player, 'domestic_stats', None) is not None:
                if format_type in player.domestic_stats:
                    dstats = player.domestic_stats[format_type]
            
            # Update batting stats
            runs_scored = batting.get('runs', 0)
            balls_faced = batting.get('balls', 0)
            
            # Track if player actually participated (batted or bowled)
            player_participated = False
            
            skip_agg = is_u21_match and self.player_in_u21_only_pipeline(player)
            if skip_agg:
                self._accumulate_u21_only_career_from_scorecard_line(
                    player, format_type, player_name, batting, bowling,
                    dismissals_per_player, innings_per_player,
                )
                updated_count += 1
                playing_xi_players.discard(player_name)
                continue
            
            if runs_scored > 0 or balls_faced > 0:
                pstats['runs'] += runs_scored
                pstats['balls_faced'] += balls_faced
                player_participated = True
                for sd in senior_stat_dicts:
                    sd['runs'] += runs_scored
                    sd['balls_faced'] += balls_faced
                if u21stats is not None:
                    u21stats['runs'] += runs_scored
                    u21stats['balls_faced'] += balls_faced
                if dstats is not None:
                    dstats['runs'] += runs_scored
                    dstats['balls_faced'] += balls_faced
                
                # Update fifties and centuries
                if runs_scored >= 50:
                    pstats['fifties'] += 1
                    for sd in senior_stat_dicts:
                        sd['fifties'] += 1
                    if u21stats is not None:
                        u21stats['fifties'] += 1
                    if dstats is not None:
                        dstats['fifties'] += 1
                if runs_scored >= 100:
                    pstats['centuries'] += 1
                    for sd in senior_stat_dicts:
                        sd['centuries'] += 1
                    if u21stats is not None:
                        u21stats['centuries'] += 1
                    if dstats is not None:
                        dstats['centuries'] += 1
                
                # Update highest score
                if runs_scored > pstats['highest_score']:
                    pstats['highest_score'] = runs_scored
                for sd in senior_stat_dicts:
                    if runs_scored > sd.get('highest_score', 0):
                        sd['highest_score'] = runs_scored
                if u21stats is not None and runs_scored > u21stats.get('highest_score', 0):
                    u21stats['highest_score'] = runs_scored
                if dstats is not None and runs_scored > dstats.get('highest_score', 0):
                    dstats['highest_score'] = runs_scored
            
            # For Test matches, use the dismissals we counted from each innings
            if format_type == 'Test' and player_name in dismissals_per_player:
                # Add the dismissals from this match to the career total
                d_add = dismissals_per_player[player_name]
                pstats['dismissals'] = pstats.get('dismissals', 0) + d_add
                for sd in senior_stat_dicts:
                    sd['dismissals'] = sd.get('dismissals', 0) + d_add
                if u21stats is not None:
                    u21stats['dismissals'] = u21stats.get('dismissals', 0) + d_add
                if dstats is not None:
                    dstats['dismissals'] = dstats.get('dismissals', 0) + d_add
            
            # Update bowling stats
            wickets_taken = bowling.get('wickets', 0)
            balls_bowled = bowling.get('balls', 0)
            runs_conceded = bowling.get('runs', 0)
            
            if wickets_taken > 0 or balls_bowled > 0:
                pstats['wickets'] += wickets_taken
                pstats['balls_bowled'] += balls_bowled
                pstats['runs_conceded'] += runs_conceded
                player_participated = True
                for sd in senior_stat_dicts:
                    sd['wickets'] += wickets_taken
                    sd['balls_bowled'] += balls_bowled
                    sd['runs_conceded'] += runs_conceded
                if u21stats is not None:
                    u21stats['wickets'] += wickets_taken
                    u21stats['balls_bowled'] += balls_bowled
                    u21stats['runs_conceded'] += runs_conceded
                if dstats is not None:
                    dstats['wickets'] += wickets_taken
                    dstats['balls_bowled'] += balls_bowled
                    dstats['runs_conceded'] += runs_conceded
                
                if wickets_taken >= 5:
                    pstats['five_wickets'] += 1
                    for sd in senior_stat_dicts:
                        sd['five_wickets'] += 1
                    if u21stats is not None:
                        u21stats['five_wickets'] += 1
                    if dstats is not None:
                        dstats['five_wickets'] += 1
            
            # Increment match count if player participated
            if player_participated:
                pstats['matches'] += 1
                for sd in senior_stat_dicts:
                    sd['matches'] += 1
                if u21stats is not None:
                    u21stats['matches'] += 1
                if dstats is not None:
                    dstats['matches'] += 1
                if format_type == 'Test':
                    # Use actual innings count from scorecard (can be 1 or 2 per match)
                    player_innings = innings_per_player.get(player_name, 0)
                    inn_add = max(1, player_innings)
                    pstats['innings'] = pstats.get('innings', 0) + inn_add
                    for sd in senior_stat_dicts:
                        sd['innings'] = sd.get('innings', 0) + inn_add
                    if u21stats is not None:
                        u21stats['innings'] = u21stats.get('innings', 0) + inn_add
                    if dstats is not None:
                        dstats['innings'] = dstats.get('innings', 0) + inn_add
            
            # Update yearly_stats keyed by year (like gamer 2024.py season_stats)
            if hasattr(player, 'yearly_stats') and player_participated:
                year = self.current_year
                if year not in player.yearly_stats:
                    player.yearly_stats[year] = {}
                if format_type not in player.yearly_stats[year]:
                    player.yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                ys = player.yearly_stats[year][format_type]
                ys['matches'] += 1
                ys['runs'] += runs_scored
                ys['balls_faced'] += balls_faced
                ys['wickets'] += wickets_taken
                ys['balls_bowled'] += balls_bowled
                ys['runs_conceded'] += runs_conceded
                if format_type == 'Test' and player_name in dismissals_per_player:
                    ys['dismissals'] = ys.get('dismissals', 0) + dismissals_per_player[player_name]
                if runs_scored > ys['highest_score']:
                    ys['highest_score'] = runs_scored
                if runs_scored >= 100:
                    ys['centuries'] += 1
                if runs_scored >= 50:
                    ys['fifties'] += 1
                if wickets_taken >= 5:
                    ys['five_wickets'] += 1
            
            if senior_full and hasattr(player, 'international_yearly_stats') and player_participated:
                year = self.current_year
                if year not in player.international_yearly_stats:
                    player.international_yearly_stats[year] = {}
                if format_type not in player.international_yearly_stats[year]:
                    player.international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                iys = player.international_yearly_stats[year][format_type]
                iys['matches'] += 1
                iys['runs'] += runs_scored
                iys['balls_faced'] += balls_faced
                iys['wickets'] += wickets_taken
                iys['balls_bowled'] += balls_bowled
                iys['runs_conceded'] += runs_conceded
                if format_type == 'Test' and player_name in dismissals_per_player:
                    iys['dismissals'] = iys.get('dismissals', 0) + dismissals_per_player[player_name]
                if runs_scored > iys['highest_score']:
                    iys['highest_score'] = runs_scored
                if runs_scored >= 100:
                    iys['centuries'] += 1
                if runs_scored >= 50:
                    iys['fifties'] += 1
                if wickets_taken >= 5:
                    iys['five_wickets'] += 1
            if senior_assoc and hasattr(player, 'associate_international_yearly_stats') and player_participated:
                year = self.current_year
                if year not in player.associate_international_yearly_stats:
                    player.associate_international_yearly_stats[year] = {}
                if format_type not in player.associate_international_yearly_stats[year]:
                    player.associate_international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                ays = player.associate_international_yearly_stats[year][format_type]
                ays['matches'] += 1
                ays['runs'] += runs_scored
                ays['balls_faced'] += balls_faced
                ays['wickets'] += wickets_taken
                ays['balls_bowled'] += balls_bowled
                ays['runs_conceded'] += runs_conceded
                if format_type == 'Test' and player_name in dismissals_per_player:
                    ays['dismissals'] = ays.get('dismissals', 0) + dismissals_per_player[player_name]
                if runs_scored > ays['highest_score']:
                    ays['highest_score'] = runs_scored
                if runs_scored >= 100:
                    ays['centuries'] += 1
                if runs_scored >= 50:
                    ays['fifties'] += 1
                if wickets_taken >= 5:
                    ays['five_wickets'] += 1
            
            if is_u21_match and hasattr(player, 'u21_international_yearly_stats') and player_participated:
                year = self.current_year
                if year not in player.u21_international_yearly_stats:
                    player.u21_international_yearly_stats[year] = {}
                if format_type not in player.u21_international_yearly_stats[year]:
                    player.u21_international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                uys = player.u21_international_yearly_stats[year][format_type]
                uys['matches'] += 1
                uys['runs'] += runs_scored
                uys['balls_faced'] += balls_faced
                uys['wickets'] += wickets_taken
                uys['balls_bowled'] += balls_bowled
                uys['runs_conceded'] += runs_conceded
                if format_type == 'Test' and player_name in dismissals_per_player:
                    uys['dismissals'] = uys.get('dismissals', 0) + dismissals_per_player[player_name]
                if runs_scored > uys['highest_score']:
                    uys['highest_score'] = runs_scored
                if runs_scored >= 100:
                    uys['centuries'] += 1
                if runs_scored >= 50:
                    uys['fifties'] += 1
                if wickets_taken >= 5:
                    uys['five_wickets'] += 1
            
            if count_as_domestic and hasattr(player, 'domestic_yearly_stats') and player_participated:
                year = self.current_year
                if year not in player.domestic_yearly_stats:
                    player.domestic_yearly_stats[year] = {}
                if format_type not in player.domestic_yearly_stats[year]:
                    player.domestic_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                dys = player.domestic_yearly_stats[year][format_type]
                dys['matches'] += 1
                dys['runs'] += runs_scored
                dys['balls_faced'] += balls_faced
                dys['wickets'] += wickets_taken
                dys['balls_bowled'] += balls_bowled
                dys['runs_conceded'] += runs_conceded
                if format_type == 'Test' and player_name in dismissals_per_player:
                    dys['dismissals'] = dys.get('dismissals', 0) + dismissals_per_player[player_name]
                if runs_scored > dys['highest_score']:
                    dys['highest_score'] = runs_scored
                if runs_scored >= 100:
                    dys['centuries'] += 1
                if runs_scored >= 50:
                    dys['fifties'] += 1
                if wickets_taken >= 5:
                    dys['five_wickets'] += 1
            
            # Recalculate averages
            self._recalculate_player_averages(player, format_type)
            updated_count += 1
            if count_as_senior_international:
                self._clear_intl_rank_flag_if_national_squad(player, team1, team2)
            playing_xi_players.discard(player_name)  # Remove from set since we've processed them
        
        # Now, for players in playing XI who didn't bat or bowl (remaining in set),
        # just increment their match count
        for player_name in playing_xi_players:
            if player_name not in all_players:
                continue
            
            player = all_players[player_name]
            if format_type not in player.stats:
                continue
            
            pstats = player.stats[format_type]
            senior_full, senior_assoc = self._senior_international_split(player, team1, team2, count_as_senior_international)
            senior_stat_dicts = []
            if senior_full and getattr(player, 'international_stats', None) and format_type in player.international_stats:
                senior_stat_dicts.append(player.international_stats[format_type])
            if senior_assoc and getattr(player, 'associate_international_stats', None) and format_type in player.associate_international_stats:
                senior_stat_dicts.append(player.associate_international_stats[format_type])
            u21stats = None
            dstats = None
            if is_u21_match and getattr(player, 'u21_international_stats', None) is not None:
                if format_type in player.u21_international_stats:
                    u21stats = player.u21_international_stats[format_type]
            if count_as_domestic and getattr(player, 'domestic_stats', None) is not None:
                if format_type in player.domestic_stats:
                    dstats = player.domestic_stats[format_type]
            skip_agg2 = is_u21_match and self.player_in_u21_only_pipeline(player)
            if skip_agg2:
                if u21stats is not None:
                    u21stats['matches'] += 1
                if format_type == 'Test':
                    player_innings = innings_per_player.get(player_name, 0)
                    if player_innings > 0 and u21stats is not None:
                        u21stats['innings'] = u21stats.get('innings', 0) + player_innings
                if is_u21_match and hasattr(player, 'u21_international_yearly_stats'):
                    year = self.current_year
                    if year not in player.u21_international_yearly_stats:
                        player.u21_international_yearly_stats[year] = {}
                    if format_type not in player.u21_international_yearly_stats[year]:
                        player.u21_international_yearly_stats[year][format_type] = {
                            'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                            'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                            'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                        }
                    player.u21_international_yearly_stats[year][format_type]['matches'] += 1
                self._recalculate_player_averages(player, format_type)
                match_count_only += 1
                continue
            pstats['matches'] += 1
            for sd in senior_stat_dicts:
                sd['matches'] += 1
            if u21stats is not None:
                u21stats['matches'] += 1
            if dstats is not None:
                dstats['matches'] += 1
            
            if format_type == 'Test':
                # Even if they didn't bat, they were in the playing XI
                player_innings = innings_per_player.get(player_name, 0)
                if player_innings > 0:
                    pstats['innings'] = pstats.get('innings', 0) + player_innings
                    for sd in senior_stat_dicts:
                        sd['innings'] = sd.get('innings', 0) + player_innings
                    if u21stats is not None:
                        u21stats['innings'] = u21stats.get('innings', 0) + player_innings
                    if dstats is not None:
                        dstats['innings'] = dstats.get('innings', 0) + player_innings
            
            # Update yearly_stats for match-count-only players too
            if hasattr(player, 'yearly_stats'):
                year = self.current_year
                if year not in player.yearly_stats:
                    player.yearly_stats[year] = {}
                if format_type not in player.yearly_stats[year]:
                    player.yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                player.yearly_stats[year][format_type]['matches'] += 1
            
            if senior_full and hasattr(player, 'international_yearly_stats'):
                year = self.current_year
                if year not in player.international_yearly_stats:
                    player.international_yearly_stats[year] = {}
                if format_type not in player.international_yearly_stats[year]:
                    player.international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                player.international_yearly_stats[year][format_type]['matches'] += 1
            if senior_assoc and hasattr(player, 'associate_international_yearly_stats'):
                year = self.current_year
                if year not in player.associate_international_yearly_stats:
                    player.associate_international_yearly_stats[year] = {}
                if format_type not in player.associate_international_yearly_stats[year]:
                    player.associate_international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                player.associate_international_yearly_stats[year][format_type]['matches'] += 1
            
            if is_u21_match and hasattr(player, 'u21_international_yearly_stats'):
                year = self.current_year
                if year not in player.u21_international_yearly_stats:
                    player.u21_international_yearly_stats[year] = {}
                if format_type not in player.u21_international_yearly_stats[year]:
                    player.u21_international_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                player.u21_international_yearly_stats[year][format_type]['matches'] += 1
            
            if count_as_domestic and hasattr(player, 'domestic_yearly_stats'):
                year = self.current_year
                if year not in player.domestic_yearly_stats:
                    player.domestic_yearly_stats[year] = {}
                if format_type not in player.domestic_yearly_stats[year]:
                    player.domestic_yearly_stats[year][format_type] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                player.domestic_yearly_stats[year][format_type]['matches'] += 1
            
            if count_as_senior_international:
                self._clear_intl_rank_flag_if_national_squad(player, team1, team2)
            match_count_only += 1
        
        print(f"[_update_player_career_stats] Updated {updated_count} players with stats, {match_count_only} players match count only")
    
    def _sync_u21_match_stats_to_parent_squads(self, team1, team2, home_parent, away_parent):
        """Copy updated stats from temporary U21 match players (team1, team2) back to parent teams' u21_squad."""
        import copy
        def sync_squad(copy_players, parent_team):
            if not getattr(parent_team, 'u21_squad', None):
                return
            name_to_real = {p.name: p for p in parent_team.u21_squad}
            for copy_p in copy_players:
                real = name_to_real.get(copy_p.name)
                if not real:
                    continue
                real.stats = copy.deepcopy(getattr(copy_p, 'stats', real.stats))
                if hasattr(copy_p, 'yearly_stats'):
                    real.yearly_stats = copy.deepcopy(copy_p.yearly_stats)
                if hasattr(copy_p, 'international_stats'):
                    real.international_stats = copy.deepcopy(copy_p.international_stats)
                if hasattr(copy_p, 'international_yearly_stats'):
                    real.international_yearly_stats = copy.deepcopy(copy_p.international_yearly_stats)
                if hasattr(copy_p, 'associate_international_stats'):
                    real.associate_international_stats = copy.deepcopy(copy_p.associate_international_stats)
                if hasattr(copy_p, 'associate_international_yearly_stats'):
                    real.associate_international_yearly_stats = copy.deepcopy(copy_p.associate_international_yearly_stats)
                if hasattr(copy_p, 'domestic_stats'):
                    real.domestic_stats = copy.deepcopy(copy_p.domestic_stats)
                if hasattr(copy_p, 'domestic_yearly_stats'):
                    real.domestic_yearly_stats = copy.deepcopy(copy_p.domestic_yearly_stats)
                if hasattr(copy_p, 'u21_international_stats'):
                    real.u21_international_stats = copy.deepcopy(copy_p.u21_international_stats)
                if hasattr(copy_p, 'u21_international_yearly_stats'):
                    real.u21_international_yearly_stats = copy.deepcopy(copy_p.u21_international_yearly_stats)
        sync_squad(team1.players, home_parent)
        sync_squad(team2.players, away_parent)
    
    def _update_u21_team_stats_from_match(self, home_parent, away_parent, team1_name, team2_name, scorecard, result, format_type):
        """Update parent teams' u21_stats (wins, runs for/against, etc.) after a U21 match."""
        _u21_default = {'matches_played': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0}
        def _ensure_u21_format(team, fmt):
            if not hasattr(team, 'u21_stats'):
                team.u21_stats = {}
            if fmt not in team.u21_stats:
                team.u21_stats[fmt] = dict(_u21_default)
            else:
                for k, v in _u21_default.items():
                    if k not in team.u21_stats[fmt]:
                        team.u21_stats[fmt][k] = v
        _ensure_u21_format(home_parent, format_type)
        _ensure_u21_format(away_parent, format_type)
        innings_list = scorecard.get('innings', [])
        h_runs = sum(inn['total_runs'] for inn in innings_list if inn.get('batting_team') == team1_name)
        a_runs = sum(inn['total_runs'] for inn in innings_list if inn.get('batting_team') == team2_name)
        h_overs = sum(inn.get('overs', 0) for inn in innings_list if inn.get('batting_team') == team1_name)
        a_overs = sum(inn.get('overs', 0) for inn in innings_list if inn.get('batting_team') == team2_name)
        home_parent.u21_stats[format_type]['matches_played'] += 1
        away_parent.u21_stats[format_type]['matches_played'] += 1
        home_parent.u21_stats[format_type]['runs_for'] += h_runs
        home_parent.u21_stats[format_type]['runs_against'] += a_runs
        home_parent.u21_stats[format_type]['overs_batted'] += h_overs
        home_parent.u21_stats[format_type]['overs_bowled'] += a_overs
        away_parent.u21_stats[format_type]['runs_for'] += a_runs
        away_parent.u21_stats[format_type]['runs_against'] += h_runs
        away_parent.u21_stats[format_type]['overs_batted'] += a_overs
        away_parent.u21_stats[format_type]['overs_bowled'] += h_overs
        winner = result.get('winner', 'Draw')
        if winner == team1_name:
            home_parent.u21_stats[format_type]['wins'] += 1
            home_parent.u21_stats[format_type]['points'] += 2
            away_parent.u21_stats[format_type]['losses'] += 1
        elif winner == team2_name:
            away_parent.u21_stats[format_type]['wins'] += 1
            away_parent.u21_stats[format_type]['points'] += 2
            home_parent.u21_stats[format_type]['losses'] += 1
        else:
            home_parent.u21_stats[format_type]['draws'] += 1
            away_parent.u21_stats[format_type]['draws'] += 1
            home_parent.u21_stats[format_type]['points'] += 1
            away_parent.u21_stats[format_type]['points'] += 1
    
    def _recalculate_player_averages(self, player, format_type):
        """Recalculate player averages after stats update"""
        stats = player.stats[format_type]
        
        # Batting average - runs per dismissal (not per match)
        if format_type == 'Test':
            # For Test: batting average = runs / dismissals (per dismissed innings, not per match)
            dismissals = stats.get('dismissals', 0)
            if dismissals > 0:
                stats['batting_average'] = round(stats['runs'] / dismissals, 2)
            else:
                stats['batting_average'] = 0.0
        else:
            # For T20/ODI: runs per match
            if stats['matches'] > 0:
                stats['batting_average'] = round(stats['runs'] / stats['matches'], 2)
            else:
                stats['batting_average'] = 0.0
        
        # Debug output for Test matches
        if format_type == 'Test' and stats['runs'] > 100:
            print(f"[TestAvg] {player.name}: {stats['runs']} runs, {stats.get('dismissals', 0)} dismissals, avg={stats['batting_average']}")
        
        # Bowling average (runs per wicket)
        if stats['wickets'] > 0:
            stats['bowling_average'] = round(stats['runs_conceded'] / stats['wickets'], 2)
        else:
            stats['bowling_average'] = 0.0
        
        # Strike rate (runs per 100 balls)
        if stats['balls_faced'] > 0:
            stats['strike_rate'] = round((stats['runs'] / stats['balls_faced']) * 100, 2)
        else:
            stats['strike_rate'] = 0.0
        
        # Economy rate (runs per over)
        if stats['balls_bowled'] > 0:
            overs = stats['balls_bowled'] / 6
            stats['economy_rate'] = round(stats['runs_conceded'] / overs, 2)
        else:
            stats['economy_rate'] = 0.0
        
        if getattr(player, 'international_stats', None) and format_type in player.international_stats:
            player._recalculate_averages_for_stats_dict(player.international_stats[format_type], format_type)
        if getattr(player, 'associate_international_stats', None) and format_type in player.associate_international_stats:
            player._recalculate_averages_for_stats_dict(player.associate_international_stats[format_type], format_type)
        if getattr(player, 'domestic_stats', None) and format_type in player.domestic_stats:
            player._recalculate_averages_for_stats_dict(player.domestic_stats[format_type], format_type)
        if getattr(player, 'u21_international_stats', None) and format_type in player.u21_international_stats:
            player._recalculate_averages_for_stats_dict(player.u21_international_stats[format_type], format_type)
    
    def update_team_stats(self, home_team, away_team, result, format_type):
        """Update team statistics after a match"""
        # Get format stats
        home_stats = home_team.format_stats[format_type]
        away_stats = away_team.format_stats[format_type]
        
        # Update matches played
        home_stats['matches_played'] += 1
        away_stats['matches_played'] += 1
        
        # Update wins/losses/draws
        winner = result.get('winner', 'Draw')
        if winner == home_team.name:
            home_stats['wins'] += 1
            away_stats['losses'] += 1
            home_stats['points'] += 2
        elif winner == away_team.name:
            away_stats['wins'] += 1
            home_stats['losses'] += 1
            away_stats['points'] += 2
        else:  # Draw
            home_stats['draws'] += 1
            away_stats['draws'] += 1
            home_stats['points'] += 1
            away_stats['points'] += 1
    
    def simulate_youth_matches(self, format_type):
        """
        Simulate youth matches for Tier 5 and track stats
        Only Tier 1 (Test playing nations) have U21 teams that play matches
        
        Args:
            format_type: 'T20', 'ODI', or 'Test'
        
        Returns:
            List of match dictionaries for U21 tier
        """
        youth_matches = []
        
        # Get Tier 1 teams ONLY (Test playing nations) with U21 squads
        # Tier 5 U21 teams should only exist for Test nations
        teams_with_youth = [t for t in self.all_teams 
                           if t.format_tiers.get(format_type) == 1  # Only Tier 1 teams
                           and hasattr(t, 'u21_squad') 
                           and len(t.u21_squad) >= 11]
        
        if len(teams_with_youth) < 2:
            return []
        
        # Reset U21 stats for this format
        for team in teams_with_youth:
            if not hasattr(team, 'u21_stats'):
                team.u21_stats = {
                    'T20': {'matches_played': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0},
                    'ODI': {'matches_played': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0},
                    'Test': {'matches_played': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0}
                }
            # Reset current format stats
            team.u21_stats[format_type] = {'matches_played': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0}
        
        # Round-robin: each U21 team plays every other team once
        for i, team1 in enumerate(teams_with_youth):
            for j, team2 in enumerate(teams_with_youth):
                if i < j:  # Only play once per pair
                    # Create temporary teams with youth players - use deep copy
                    from cricket_manager.core.team import Team
                    import copy
                    
                    youth_team1 = Team(name=f"{team1.name} U21", tier=5)
                    youth_team1.players = copy.deepcopy(team1.u21_squad[:11])
                    
                    youth_team2 = Team(name=f"{team2.name} U21", tier=5)
                    youth_team2.players = copy.deepcopy(team2.u21_squad[:11])
                    
                    # Simulate match using fast simulator
                    from cricket_manager.core.fast_match_simulator import FastMatchSimulator
                    simulator = FastMatchSimulator(
                        team1=youth_team1,
                        team2=youth_team2,
                        match_format=format_type
                    )
                    
                    winner = simulator.simulate()
                    scorecard = simulator.get_scorecard()
                    
                    # Get innings data
                    innings1 = scorecard['innings'][0]
                    innings2 = scorecard['innings'][1]
                    
                    # Update U21 stats for both parent teams
                    # Team 1
                    team1.u21_stats[format_type]['matches_played'] += 1
                    team1.u21_stats[format_type]['runs_for'] += innings1['total_runs']
                    team1.u21_stats[format_type]['runs_against'] += innings2['total_runs']
                    team1.u21_stats[format_type]['overs_batted'] += innings1['overs']
                    team1.u21_stats[format_type]['overs_bowled'] += innings2['overs']
                    
                    # Team 2
                    team2.u21_stats[format_type]['matches_played'] += 1
                    team2.u21_stats[format_type]['runs_for'] += innings2['total_runs']
                    team2.u21_stats[format_type]['runs_against'] += innings1['total_runs']
                    team2.u21_stats[format_type]['overs_batted'] += innings2['overs']
                    team2.u21_stats[format_type]['overs_bowled'] += innings1['overs']
                    
                    # Update wins/losses/points
                    if winner == youth_team1:
                        team1.u21_stats[format_type]['wins'] += 1
                        team1.u21_stats[format_type]['points'] += 2
                        team2.u21_stats[format_type]['losses'] += 1
                    elif winner == youth_team2:
                        team2.u21_stats[format_type]['wins'] += 1
                        team2.u21_stats[format_type]['points'] += 2
                        team1.u21_stats[format_type]['losses'] += 1
                    else:  # Tie
                        team1.u21_stats[format_type]['draws'] += 1
                        team1.u21_stats[format_type]['points'] += 1
                        team2.u21_stats[format_type]['draws'] += 1
                        team2.u21_stats[format_type]['points'] += 1
                    
                    # Add to match list with FULL scorecard
                    match_info = {
                        'home': f"{team1.name} U21",
                        'away': f"{team2.name} U21",
                        'format': format_type,
                        'tier': 5,
                        'completed': True,
                        'status': 'Completed',
                        'winner': winner.name if winner else 'Tie',
                        'margin': simulator.margin,
                        'scorecard': scorecard,  # <-- ADDED: Full scorecard for viewing
                        'result': {
                            'team1_score': f"{innings1['total_runs']}/{innings1['wickets_fallen']}",
                            'team2_score': f"{innings2['total_runs']}/{innings2['wickets_fallen']}",
                            'winner': winner.name if winner else 'Tie'
                        }
                    }
                    youth_matches.append(match_info)
        
        # Calculate NRR for all teams
        for team in teams_with_youth:
            stats = team.u21_stats[format_type]
            if stats['overs_batted'] > 0 and stats['overs_bowled'] > 0:
                run_rate_for = stats['runs_for'] / stats['overs_batted']
                run_rate_against = stats['runs_against'] / stats['overs_bowled']
                stats['nrr'] = round(run_rate_for - run_rate_against, 3)
        
        print(f"[Youth] Simulated {len(youth_matches)} U21 {format_type} matches for {len(teams_with_youth)} Tier 1 teams")
        
        # Add youth matches to main fixtures list for Tier 5 viewing
        if format_type in self.fixtures:
            # Convert youth matches to fixture format and add to fixtures
            for match in youth_matches:
                fixture = {
                    'home': match['home'],
                    'away': match['away'],
                    'format': match['format'],
                    'tier': 5,
                    'completed': match['completed'],
                    'status': match['status'],
                    'winner': match['winner'],
                    'margin': match.get('margin', ''),
                    'result': match.get('result', {}),
                    'scorecard': match.get('scorecard', {}),
                    # Add team objects for compatibility
                    'team1': None,  # U21 teams don't have Team objects in main list
                    'team2': None
                }
                self.fixtures[format_type].append(fixture)
            print(f"[Youth] Added {len(youth_matches)} U21 matches to {format_type} fixtures for Tier 5 viewing")
        
        return youth_matches
    
    def generate_youth_fixtures(self):
        """Generate youth fixtures for all formats (Tier 5) - scheduled but not played"""
        for format_type in ['T20', 'ODI', 'Test']:
            print(f"[GameEngine] Generating {format_type} youth fixtures...")
            
            # Get Tier 1 teams with U21 squads
            teams_with_youth = [t for t in self.all_teams 
                               if t.format_tiers.get(format_type) == 1  # Only Tier 1 teams
                               and hasattr(t, 'u21_squad') 
                               and len(t.u21_squad) >= 11]
            
            if len(teams_with_youth) < 2:
                continue
            
            # Round-robin: each U21 team plays every other team once
            for i, team1 in enumerate(teams_with_youth):
                for j, team2 in enumerate(teams_with_youth):
                    if i < j:  # Only play once per pair
                        fixture = {
                            'home': f"{team1.name} U21",
                            'away': f"{team2.name} U21",
                            'format': format_type,
                            'tier': 5,
                            'completed': False,
                            'status': 'Scheduled',
                            'winner': None,
                            'margin': '',
                            'result': {},
                            'scorecard': {},
                            # Add team objects for compatibility
                            'team1': None,  # U21 teams don't have Team objects in main list
                            'team2': None
                        }
                        self.fixtures[format_type].append(fixture)
            
            print(f"[GameEngine] Generated {len([f for f in self.fixtures[format_type] if f.get('tier') == 5])} {format_type} youth fixtures")
    
    def _get_wc_month(self, season):
        """Get the month index (0-11) reserved for the World Cup in a given season.
        World Cups rotate on a 4-year cycle. Returns None if no WC that season.
        WC month is June (index 5) for T20 WC, October (index 9) for ODI/U19/Associate WC.
        """
        wc_cycle = (season - 1) % 4
        if wc_cycle == 0:
            return 5   # June - T20 World Cup
        elif wc_cycle == 1:
            return 9   # October - ODI World Cup
        elif wc_cycle == 2:
            return 9   # October - U19 World Cup
        elif wc_cycle == 3:
            return 9   # October - Associate World Cup
        return None
    
    def generate_world_cup_fixtures(self, for_season=None):
        """Pre-generate World Cup group stage fixtures so they appear in the fixtures tab
        and can be played/quick-simmed individually before season simulation.
        
        Args:
            for_season: Season number to generate WC for. If None, uses current_season.
        """
        import random as _rng
        from cricket_manager.systems.tier_system import resolve_team_day_clashes
        
        season = for_season if for_season is not None else self.current_season
        wc_cycle = (season - 1) % 4
        
        wc_configs = {
            0: ('T20', 'T20 World Cup'),
            1: ('ODI', 'ODI World Cup'),
            2: ('ODI', 'U19 World Cup'),
            3: ('ODI', 'Associate World Cup'),
        }
        
        wc_format, wc_name = wc_configs[wc_cycle]
        
        # Ensure format key exists in fixtures
        if wc_format not in self.fixtures:
            self.fixtures[wc_format] = []
        
        # Remove any old WC fixtures from all formats before generating new ones
        for fmt in ['T20', 'ODI', 'Test']:
            if fmt in self.fixtures:
                self.fixtures[fmt] = [f for f in self.fixtures[fmt] if not f.get('is_world_cup', False)]
        
        wc_month = self._get_wc_month(season)
        wc_month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Store WC info
        self.wc_format = wc_format
        self.wc_name = wc_name
        
        # ---- Pick a host nation and derive pitch conditions ----
        from cricket_manager.systems.tier_system import get_pitch_conditions, SUBCONTINENT_COUNTRIES, SENA_COUNTRIES
        
        if wc_name == 'Associate World Cup':
            # Host = random associate nation (Tier 2/3/4)
            assoc_candidates = [t for t in self.all_teams if t.format_tiers.get('ODI', 99) in (2, 3, 4)]
            wc_host = _rng.choice(assoc_candidates) if assoc_candidates else None
        else:
            # Host = random Test-playing (Tier 1) nation
            tier1 = [t for t in self.all_teams if t.format_tiers.get(wc_format, 99) == 1]
            wc_host = _rng.choice(tier1) if tier1 else None
        
        wc_host_name = wc_host.name if wc_host else 'England'
        self.wc_host = wc_host_name
        
        # Pitch conditions based on host
        pitch_ranges = get_pitch_conditions(wc_host_name)
        wc_pitch = {
            'pitch_bounce': _rng.randint(*pitch_ranges['bounce']),
            'pitch_spin': _rng.randint(*pitch_ranges['spin']),
            'pitch_pace': _rng.randint(*pitch_ranges['pace']),
            'pitch_region': pitch_ranges['region'],
        }
        
        print(f"[World Cup] {wc_name} hosted by {wc_host_name} ({pitch_ranges['region']})")
        
        # ---- ASSOCIATE WORLD CUP: 32-team knockout from Tier 2/3/4 ----
        if wc_name == 'Associate World Cup':
            assoc_pool = [t for t in self.all_teams
                          if t.format_tiers.get('ODI', 99) in (2, 3, 4)]
            _rng.shuffle(assoc_pool)
            qualified_teams = assoc_pool[:32]
            
            if len(qualified_teams) < 4:
                print(f"[World Cup] Not enough associate teams for {wc_name} ({len(qualified_teams)})")
                return
            
            # Pad to nearest power of 2 if needed (shouldn't be needed for 32)
            self.wc_group_a = None
            self.wc_group_b = None
            self.wc_associate_teams = qualified_teams
            self.wc_is_knockout = True
            
            # Generate Round of 32 knockout fixtures
            wc_fixture_count = 0
            day_counter = 1
            _rng.shuffle(qualified_teams)
            
            for i in range(0, len(qualified_teams) - 1, 2):
                t1 = qualified_teams[i]
                t2 = qualified_teams[i + 1]
                fixture = {
                    'team1': t1,
                    'team2': t2,
                    'home': t1.name,
                    'away': t2.name,
                    'format': wc_format,
                    'tier': 0,
                    'is_world_cup': True,
                    'round': 'Round of 32',
                    'wc_tournament': wc_name,
                    'wc_host': wc_host_name,
                    'completed': False,
                    'status': 'Scheduled',
                    'winner': None,
                    'margin': '',
                    'scorecard': {},
                    'month': wc_month if wc_month is not None else 9,
                    'month_name': wc_month_names[wc_month] if wc_month is not None else 'October',
                    'day': min(day_counter, 28),
                    'pitch_bounce': wc_pitch['pitch_bounce'],
                    'pitch_spin': wc_pitch['pitch_spin'],
                    'pitch_pace': wc_pitch['pitch_pace'],
                    'pitch_region': wc_pitch['pitch_region'],
                }
                day_counter += 1
                self.fixtures[wc_format].append(fixture)
                wc_fixture_count += 1
            
            print(f"[World Cup] Pre-generated {wc_fixture_count} {wc_name} Round of 32 fixtures ({wc_format})")
            print(f"[World Cup] {len(qualified_teams)} teams from Tier 2/3/4")
            # Re-resolve full calendar after WC fixtures insertion so no team has same-day doubles.
            resolve_team_day_clashes(self.fixtures)
            return
        
        # ---- STANDARD WORLD CUP (T20, ODI, U19): Group stage with Tier 1 teams ----
        tier1_teams = [t for t in self.all_teams if t.format_tiers.get(wc_format) == 1]
        tier1_teams.sort(key=lambda t: t.format_stats[wc_format].get('points', 0), reverse=True)
        qualified_teams = tier1_teams[:min(12, len(tier1_teams))]
        
        if len(qualified_teams) < 4:
            print(f"[World Cup] Not enough teams for {wc_name} ({len(qualified_teams)})")
            return
        
        # Shuffle and divide into 2 groups
        _rng.shuffle(qualified_teams)
        group_a = qualified_teams[:6]
        group_b = qualified_teams[6:12]
        
        self.wc_group_a = group_a
        self.wc_group_b = group_b
        self.wc_is_knockout = False
        
        wc_fixture_count = 0
        
        # Generate Group A round-robin fixtures
        day_counter = 1
        for i in range(len(group_a)):
            for j in range(i + 1, len(group_a)):
                fixture = {
                    'team1': group_a[i],
                    'team2': group_a[j],
                    'home': group_a[i].name,
                    'away': group_a[j].name,
                    'format': wc_format,
                    'tier': 0,
                    'is_world_cup': True,
                    'round': 'Group A',
                    'wc_tournament': wc_name,
                    'wc_host': wc_host_name,
                    'completed': False,
                    'status': 'Scheduled',
                    'winner': None,
                    'margin': '',
                    'scorecard': {},
                    'month': wc_month if wc_month is not None else 5,
                    'month_name': wc_month_names[wc_month] if wc_month is not None else 'June',
                    'day': min(day_counter, 28),
                    'pitch_bounce': wc_pitch['pitch_bounce'],
                    'pitch_spin': wc_pitch['pitch_spin'],
                    'pitch_pace': wc_pitch['pitch_pace'],
                    'pitch_region': wc_pitch['pitch_region'],
                }
                day_counter += 2
                self.fixtures[wc_format].append(fixture)
                wc_fixture_count += 1
        
        # Generate Group B round-robin fixtures
        for i in range(len(group_b)):
            for j in range(i + 1, len(group_b)):
                fixture = {
                    'team1': group_b[i],
                    'team2': group_b[j],
                    'home': group_b[i].name,
                    'away': group_b[j].name,
                    'format': wc_format,
                    'tier': 0,
                    'is_world_cup': True,
                    'round': 'Group B',
                    'wc_tournament': wc_name,
                    'wc_host': wc_host_name,
                    'completed': False,
                    'status': 'Scheduled',
                    'winner': None,
                    'margin': '',
                    'scorecard': {},
                    'month': wc_month if wc_month is not None else 5,
                    'month_name': wc_month_names[wc_month] if wc_month is not None else 'June',
                    'day': min(day_counter, 28),
                    'pitch_bounce': wc_pitch['pitch_bounce'],
                    'pitch_spin': wc_pitch['pitch_spin'],
                    'pitch_pace': wc_pitch['pitch_pace'],
                    'pitch_region': wc_pitch['pitch_region'],
                }
                day_counter += 2
                self.fixtures[wc_format].append(fixture)
                wc_fixture_count += 1
        
        print(f"[World Cup] Pre-generated {wc_fixture_count} {wc_name} group stage fixtures ({wc_format})")
        print(f"[World Cup] Group A: {', '.join([t.name for t in group_a])}")
        print(f"[World Cup] Group B: {', '.join([t.name for t in group_b])}")
        # Re-resolve full calendar after WC fixtures insertion so no team has same-day doubles.
        resolve_team_day_clashes(self.fixtures)
    
    def _world_cup_uses_u21_squads(self, tournament_name):
        """Youth World Cups must be simulated with national U21 XIs, not senior squads."""
        if not tournament_name:
            return False
        tn = str(tournament_name)
        return ("U21" in tn) or ("U19" in tn) or ("youth" in tn.lower())

    def _wc_u21_xi_team(self, parent_team, format_type=None):
        """Temporary match team using up to 11 players from parent u21_squad (deep copy)."""
        import copy
        from cricket_manager.core.team import Team
        t = Team(name=f"{parent_team.name} U21", tier=5)
        sq = getattr(parent_team, "u21_squad", None) or []
        if len(sq) >= 11:
            t.players = copy.deepcopy(sq[:11])
        elif sq:
            t.players = copy.deepcopy(sq)
        else:
            t.players = []
        setattr(t, "_wc_parent_team", parent_team)
        return t

    def _wc_resolve_winner_parent(self, winner_side, sim1, sim2, parent1, parent2):
        if winner_side is None:
            return parent1
        wp = getattr(winner_side, "_wc_parent_team", None)
        if wp is not None:
            return wp
        if winner_side is sim1 or getattr(winner_side, "name", None) == sim1.name:
            return parent1
        return parent2

    def execute_world_cup(self, format_type, tournament_name=None):
        """
        Execute World Cup tournament.
        - Standard WCs (T20, ODI, U19): group stage + semis + final with Tier 1 teams.
        - Associate WC: 32-team pure knockout from Tier 2/3/4.
        
        Pre-generated fixtures that were already played/quick-simmed are respected.
        
        Returns:
            World Cup results dictionary with full details
        """
        wc_format = getattr(self, 'wc_format', format_type)
        wc_name = getattr(self, 'wc_name', tournament_name)
        is_knockout = getattr(self, 'wc_is_knockout', False)
        
        if not tournament_name:
            tournament_name = wc_name or ('T20 World Cup' if format_type == 'T20' else 'ODI World Cup')
        
        print(f"\n{'='*60}")
        print(f"{tournament_name.upper()}")
        print(f"{'='*60}")
        
        # ================================================================
        # ASSOCIATE WORLD CUP: Pure knockout tournament (32 teams)
        # ================================================================
        if is_knockout or tournament_name == 'Associate World Cup':
            return self._execute_associate_wc_knockout(format_type, tournament_name)
        
        # ================================================================
        # STANDARD WORLD CUP: Group stage + knockouts
        # ================================================================
        group_a = getattr(self, 'wc_group_a', None)
        group_b = getattr(self, 'wc_group_b', None)
        
        # If groups weren't pre-generated, generate them now (fallback)
        if not group_a or not group_b:
            tier1_teams = [t for t in self.all_teams if t.format_tiers.get(format_type) == 1]
            tier1_teams.sort(key=lambda t: t.format_stats[format_type].get('points', 0), reverse=True)
            qualified_teams = tier1_teams[:min(12, len(tier1_teams))]
            
            if len(qualified_teams) < 4:
                print(f"[World Cup] Not enough teams qualified ({len(qualified_teams)})")
                return {
                    'winner': 'N/A', 'runner_up': 'N/A',
                    'tournament': tournament_name, 'qualified_teams': [], 'matches': []
                }
            
            random.shuffle(qualified_teams)
            group_a = qualified_teams[:6]
            group_b = qualified_teams[6:12]
        
        qualified_teams = group_a + group_b
        print(f"[World Cup] {len(qualified_teams)} teams qualified")
        
        use_u21_lineups = self._world_cup_uses_u21_squads(tournament_name)
        if use_u21_lineups:
            print("[World Cup] Simulating youth World Cup with U21 squads (not senior XIs).")
        
        # Collect all WC fixtures from the fixtures list
        all_wc_fixtures = [f for f in self.fixtures.get(format_type, [])
                          if f.get('is_world_cup', False) and f.get('tier') == 0]
        
        wc_matches = []
        wc_player_stats = {}
        group_a_standings: list = []
        group_b_standings: list = []
        
        # --- GROUP STAGE ---
        print(f"\n[World Cup] GROUP STAGE")
        print("-" * 60)
        
        for group_name, group_teams in [("A", group_a), ("B", group_b)]:
            print(f"\nGroup {group_name}: {', '.join([t.name for t in group_teams])}")
            
            # Initialize standings
            standings = {}
            for team in group_teams:
                standings[team.name] = {
                    'played': 0, 'won': 0, 'lost': 0, 'points': 0, 'nrr': 0.0,
                    'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0
                }
            
            # Process each group match pair
            for i in range(len(group_teams)):
                for j in range(i + 1, len(group_teams)):
                    team1 = group_teams[i]
                    team2 = group_teams[j]
                    
                    # Check if this match was already played (find in fixtures)
                    existing = None
                    for f in all_wc_fixtures:
                        if f.get('completed') and f.get('round') == f'Group {group_name}':
                            f_t1 = f.get('team1')
                            f_t2 = f.get('team2')
                            f_home = f.get('home', '')
                            f_away = f.get('away', '')
                            # Match by team object or name
                            t1_match = (f_t1 == team1 or f_home == team1.name)
                            t2_match = (f_t2 == team2 or f_away == team2.name)
                            t1_match_rev = (f_t1 == team2 or f_home == team2.name)
                            t2_match_rev = (f_t2 == team1 or f_away == team1.name)
                            if (t1_match and t2_match) or (t1_match_rev and t2_match_rev):
                                existing = f
                                break
                    
                    if existing and existing.get('scorecard'):
                        # Use already-played result
                        scorecard = existing['scorecard']
                        winner_name = existing.get('winner', '')
                        winner = self.get_team_by_name(winner_name) if winner_name and winner_name != 'Tie' else None
                        print(f"  {team1.name} vs {team2.name} - Already played (Won: {winner_name})")
                    else:
                        # Simulate this match (youth WC uses U21 XIs)
                        if use_u21_lineups:
                            sim1 = self._wc_u21_xi_team(team1, format_type)
                            sim2 = self._wc_u21_xi_team(team2, format_type)
                            simulator = FastMatchSimulator(sim1, sim2, format_type)
                            winner_side = simulator.simulate()
                            winner = self._wc_resolve_winner_parent(winner_side, sim1, sim2, team1, team2)
                        else:
                            simulator = FastMatchSimulator(team1, team2, format_type)
                            winner = simulator.simulate()
                        scorecard = simulator.get_scorecard()
                        winner_name = winner.name if winner else 'Tie'
                        
                        # Update the fixture in-place if it exists
                        if existing:
                            existing['completed'] = True
                            existing['status'] = 'Completed'
                            existing['winner'] = winner_name
                            existing['margin'] = simulator.margin
                            existing['scorecard'] = scorecard
                            existing['man_of_the_match'] = scorecard.get('man_of_the_match', '')
                        else:
                            # Find the scheduled fixture and update it
                            for f in all_wc_fixtures:
                                if not f.get('completed') and f.get('round') == f'Group {group_name}':
                                    f_t1 = f.get('team1')
                                    f_t2 = f.get('team2')
                                    f_home = f.get('home', '')
                                    f_away = f.get('away', '')
                                    t1_match = (f_t1 == team1 or f_home == team1.name)
                                    t2_match = (f_t2 == team2 or f_away == team2.name)
                                    t1_match_rev = (f_t1 == team2 or f_home == team2.name)
                                    t2_match_rev = (f_t2 == team1 or f_away == team1.name)
                                    if (t1_match and t2_match) or (t1_match_rev and t2_match_rev):
                                        f['completed'] = True
                                        f['status'] = 'Completed'
                                        f['winner'] = winner_name
                                        f['margin'] = simulator.margin
                                        f['scorecard'] = scorecard
                                        f['man_of_the_match'] = scorecard.get('man_of_the_match', '')
                                        break
                        
                        if use_u21_lineups:
                            print(f"  {team1.name} U21 vs {team2.name} U21 - Simulated (Won: {winner_name})")
                        else:
                            print(f"  {team1.name} vs {team2.name} - Simulated (Won: {winner_name})")
                    
                    # Store match result
                    match_data = {
                        'home': team1.name, 'away': team2.name,
                        'format': format_type, 'tier': 0,
                        'is_world_cup': True, 'round': f'Group {group_name}',
                        'completed': True, 'status': 'Completed',
                        'winner': winner_name,
                        'scorecard': scorecard
                    }
                    wc_matches.append(match_data)
                    
                    # Extract player stats
                    ext_home = f"{team1.name} U21" if use_u21_lineups else team1.name
                    ext_away = f"{team2.name} U21" if use_u21_lineups else team2.name
                    self._extract_player_stats_from_scorecard(scorecard, wc_player_stats, ext_home, ext_away)
                    
                    # Update standings from scorecard
                    if scorecard and 'innings' in scorecard and len(scorecard['innings']) >= 2:
                        innings1 = scorecard['innings'][0]
                        innings2 = scorecard['innings'][1]
                        
                        standings[team1.name]['played'] += 1
                        standings[team1.name]['runs_for'] += innings1.get('total_runs', 0)
                        standings[team1.name]['runs_against'] += innings2.get('total_runs', 0)
                        standings[team1.name]['overs_batted'] += innings1.get('overs', 0)
                        standings[team1.name]['overs_bowled'] += innings2.get('overs', 0)
                        
                        standings[team2.name]['played'] += 1
                        standings[team2.name]['runs_for'] += innings2.get('total_runs', 0)
                        standings[team2.name]['runs_against'] += innings1.get('total_runs', 0)
                        standings[team2.name]['overs_batted'] += innings2.get('overs', 0)
                        standings[team2.name]['overs_bowled'] += innings1.get('overs', 0)
                        
                        if winner == team1:
                            standings[team1.name]['won'] += 1
                            standings[team1.name]['points'] += 2
                            standings[team2.name]['lost'] += 1
                        elif winner == team2:
                            standings[team2.name]['won'] += 1
                            standings[team2.name]['points'] += 2
                            standings[team1.name]['lost'] += 1
                        else:
                            standings[team1.name]['points'] += 1
                            standings[team2.name]['points'] += 1
            
            # Calculate NRR
            for team_name, stats in standings.items():
                if stats['overs_batted'] > 0 and stats['overs_bowled'] > 0:
                    rr_for = stats['runs_for'] / stats['overs_batted']
                    rr_against = stats['runs_against'] / stats['overs_bowled']
                    stats['nrr'] = round(rr_for - rr_against, 3)
            
            # Print standings
            sorted_standings = sorted(standings.items(), key=lambda x: (x[1]['points'], x[1]['nrr']), reverse=True)
            print(f"\nGroup {group_name} Standings:")
            print(f"{'Team':<20} {'P':<4} {'W':<4} {'L':<4} {'Pts':<5} {'NRR':<8}")
            print("-" * 50)
            for tn, st in sorted_standings:
                print(f"{tn:<20} {st['played']:<4} {st['won']:<4} {st['lost']:<4} {st['points']:<5} {st['nrr']:<8.3f}")
            
            # Store standings for this group
            if group_name == "A":
                group_a_standings = sorted_standings
            else:
                group_b_standings = sorted_standings
        
        # --- SEMI-FINALS ---
        if len(group_a_standings) < 2 or len(group_b_standings) < 2:
            print("[World Cup] ERROR: Group standings incomplete — cannot run knockouts.")
            return {
                'winner': 'N/A',
                'runner_up': 'N/A',
                'tournament': tournament_name,
                'qualified_teams': [t.name for t in qualified_teams],
                'matches': wc_matches,
            }
        a1_team = self.get_team_by_name(group_a_standings[0][0])
        a2_team = self.get_team_by_name(group_a_standings[1][0])
        b1_team = self.get_team_by_name(group_b_standings[0][0])
        b2_team = self.get_team_by_name(group_b_standings[1][0])
        if not all((a1_team, a2_team, b1_team, b2_team)):
            print("[World Cup] ERROR: Could not resolve team objects for knockout.")
            return {
                'winner': 'N/A',
                'runner_up': 'N/A',
                'tournament': tournament_name,
                'qualified_teams': [t.name for t in qualified_teams],
                'matches': wc_matches,
            }
        
        assert a1_team is not None and a2_team is not None and b1_team is not None and b2_team is not None
        print(f"\n[World Cup] Group A Qualifiers: {a1_team.name}, {a2_team.name}")
        print(f"[World Cup] Group B Qualifiers: {b1_team.name}, {b2_team.name}")
        
        print(f"\n[World Cup] SEMI-FINALS")
        print("-" * 60)
        
        def _play_knockout(t1, t2, round_name):
            """Simulate a knockout match and add to fixtures + wc_matches"""
            # Check if already played in fixtures
            for f in all_wc_fixtures:
                if f.get('completed') and f.get('round') == round_name:
                    f_home = f.get('home', '')
                    f_away = f.get('away', '')
                    if (f_home == t1.name and f_away == t2.name) or (f_home == t2.name and f_away == t1.name):
                        w_name = f.get('winner', '')
                        w = self.get_team_by_name(w_name) if w_name and w_name != 'Tie' else t1
                        print(f"  {t1.name} vs {t2.name} - Already played (Won: {w_name})")
                        if f.get('scorecard'):
                            eh = f"{t1.name} U21" if use_u21_lineups else t1.name
                            ea = f"{t2.name} U21" if use_u21_lineups else t2.name
                            self._extract_player_stats_from_scorecard(f['scorecard'], wc_player_stats, eh, ea)
                        wc_matches.append(f)
                        return w
            
            if use_u21_lineups:
                st1 = self._wc_u21_xi_team(t1, format_type)
                st2 = self._wc_u21_xi_team(t2, format_type)
                sim = FastMatchSimulator(st1, st2, format_type)
                w_side = sim.simulate()
                w = self._wc_resolve_winner_parent(w_side, st1, st2, t1, t2)
            else:
                sim = FastMatchSimulator(t1, t2, format_type)
                w = sim.simulate()
            if w is None:
                w = t1
            sc = sim.get_scorecard()
            if use_u21_lineups:
                print(f"  {t1.name} U21 vs {t2.name} U21 - {w.name} wins ({sim.margin})")
            else:
                print(f"  {t1.name} vs {t2.name} - {w.name} wins ({sim.margin})")
            
            match_data = {
                'team1': t1, 'team2': t2,
                'home': t1.name, 'away': t2.name,
                'format': format_type, 'tier': 0,
                'is_world_cup': True, 'round': round_name,
                'completed': True, 'status': 'Completed',
                'winner': w.name, 'margin': sim.margin,
                'man_of_the_match': sc.get('man_of_the_match', ''),
                'scorecard': sc
            }
            self.fixtures[format_type].append(match_data)
            wc_matches.append(match_data)
            eh = f"{t1.name} U21" if use_u21_lineups else t1.name
            ea = f"{t2.name} U21" if use_u21_lineups else t2.name
            self._extract_player_stats_from_scorecard(sc, wc_player_stats, eh, ea)
            return w
        
        semi1_winner = _play_knockout(a1_team, b2_team, 'Semi-Final')
        semi1_loser = b2_team if semi1_winner == a1_team else a1_team
        
        semi2_winner = _play_knockout(b1_team, a2_team, 'Semi-Final')
        semi2_loser = a2_team if semi2_winner == b1_team else b1_team
        assert semi1_winner is not None and semi2_winner is not None
        
        # --- FINAL ---
        print(f"\n[World Cup] FINAL")
        print("=" * 60)
        print(f"{semi1_winner.name} vs {semi2_winner.name}")
        
        champion = _play_knockout(semi1_winner, semi2_winner, 'Final')
        if champion is None:
            champion = semi1_winner
            runner_up = semi2_winner
        else:
            runner_up = semi2_winner if champion == semi1_winner else semi1_winner
        assert champion is not None and runner_up is not None
        
        print(f"\nCHAMPION: {champion.name}")
        print(f"   Runner-up: {runner_up.name}")
        print("=" * 60)
        
        # Award credits (knockout sides are always resolved to Team objects here)
        assert semi1_loser is not None and semi2_loser is not None
        champion.credits += 5000
        runner_up.credits += 2500
        semi1_loser.credits += 1000
        semi2_loser.credits += 1000
        
        top_batters = self._calculate_top_batters(wc_player_stats)
        top_bowlers = self._calculate_top_bowlers(wc_player_stats)
        
        results = {
            'winner': champion.name,
            'runner_up': runner_up.name,
            'semi_finalists': [semi1_loser.name, semi2_loser.name],
            'tournament': tournament_name,
            'qualified_teams': [t.name for t in qualified_teams],
            'group_a_standings': [(name, stats['points'], stats['nrr']) for name, stats in group_a_standings],
            'group_b_standings': [(name, stats['points'], stats['nrr']) for name, stats in group_b_standings],
            'matches': wc_matches,
            'top_batters': top_batters,
            'top_bowlers': top_bowlers
        }
        
        return results
    
    def _execute_associate_wc_knockout(self, format_type, tournament_name):
        """Execute Associate World Cup as a pure knockout tournament (R32→R16→QF→SF→F)."""
        wc_player_stats = {}
        wc_matches = []
        
        # Collect all WC fixtures
        all_wc = [f for f in self.fixtures.get(format_type, [])
                   if f.get('is_world_cup', False) and f.get('wc_tournament') == tournament_name]
        
        # Get teams from pre-generated fixtures or fallback
        assoc_teams = getattr(self, 'wc_associate_teams', None)
        if not assoc_teams:
            assoc_teams = list(set(
                [f.get('team1') for f in all_wc if f.get('team1')] +
                [f.get('team2') for f in all_wc if f.get('team2')]
            ))
        
        if len(assoc_teams) < 2:
            print(f"[Associate WC] Not enough teams ({len(assoc_teams)})")
            return {
                'winner': 'N/A', 'runner_up': 'N/A',
                'tournament': tournament_name, 'qualified_teams': [], 'matches': []
            }
        
        print(f"[Associate WC] {len(assoc_teams)} teams in knockout")
        
        # Knockout round names in order
        round_names = {32: 'Round of 32', 16: 'Round of 16', 8: 'Quarter-Final',
                       4: 'Semi-Final', 2: 'Final'}
        
        def _sim_knockout_match(t1, t2, round_name):
            """Simulate or retrieve a knockout match."""
            # Check if already played
            for f in all_wc:
                if f.get('completed') and f.get('round') == round_name:
                    f_home = f.get('home', '')
                    f_away = f.get('away', '')
                    if (f_home == t1.name and f_away == t2.name) or (f_home == t2.name and f_away == t1.name):
                        w_name = f.get('winner', '')
                        w = self.get_team_by_name(w_name) if w_name and w_name != 'Tie' else t1
                        if f.get('scorecard'):
                            self._extract_player_stats_from_scorecard(f['scorecard'], wc_player_stats, t1.name, t2.name)
                        wc_matches.append(f)
                        return w
            
            sim = FastMatchSimulator(t1, t2, format_type)
            w = sim.simulate()
            if w is None:
                w = t1
            sc = sim.get_scorecard()
            
            # Find and update existing scheduled fixture, or create new one
            updated = False
            for f in all_wc:
                if not f.get('completed') and f.get('round') == round_name:
                    f_home = f.get('home', '')
                    f_away = f.get('away', '')
                    if (f_home == t1.name and f_away == t2.name) or (f_home == t2.name and f_away == t1.name):
                        f['completed'] = True
                        f['status'] = 'Completed'
                        f['winner'] = w.name
                        f['margin'] = sim.margin
                        f['scorecard'] = sc
                        f['man_of_the_match'] = sc.get('man_of_the_match', '')
                        wc_matches.append(f)
                        updated = True
                        break
            
            if not updated:
                match_data = {
                    'team1': t1, 'team2': t2,
                    'home': t1.name, 'away': t2.name,
                    'format': format_type, 'tier': 0,
                    'is_world_cup': True, 'round': round_name,
                    'wc_tournament': tournament_name,
                    'completed': True, 'status': 'Completed',
                    'winner': w.name, 'margin': sim.margin,
                    'man_of_the_match': sc.get('man_of_the_match', ''),
                    'scorecard': sc
                }
                self.fixtures[format_type].append(match_data)
                wc_matches.append(match_data)
            
            self._extract_player_stats_from_scorecard(sc, wc_player_stats, t1.name, t2.name)
            print(f"  {t1.name} vs {t2.name} - {w.name} wins ({sim.margin})")
            return w
        
        # Run knockout rounds
        current_round_teams = list(assoc_teams)
        random.shuffle(current_round_teams)
        
        runner_up = None
        while len(current_round_teams) >= 2:
            n = len(current_round_teams)
            rname = round_names.get(n, f'Round of {n}')
            print(f"\n[Associate WC] {rname} ({n} teams)")
            print("-" * 50)
            
            next_round = []
            for i in range(0, n - 1, 2):
                t1 = current_round_teams[i]
                t2 = current_round_teams[i + 1]
                winner = _sim_knockout_match(t1, t2, rname)
                next_round.append(winner)
                if n == 2:
                    runner_up = t2 if winner == t1 else t1
            
            if n % 2 == 1:
                bye_team = current_round_teams[-1]
                print(f"  {bye_team.name} gets a bye")
                next_round.append(bye_team)
            
            current_round_teams = next_round
        
        champion = current_round_teams[0] if current_round_teams else None
        if not runner_up and len(assoc_teams) >= 2:
            runner_up = assoc_teams[1]
        
        if champion:
            print(f"\nCHAMPION: {champion.name}")
            print(f"   Runner-up: {runner_up.name if runner_up else 'N/A'}")
            print("=" * 60)
            champion.credits += 3000
            if runner_up:
                runner_up.credits += 1500
        
        top_batters = self._calculate_top_batters(wc_player_stats)
        top_bowlers = self._calculate_top_bowlers(wc_player_stats)
        
        return {
            'winner': champion.name if champion else 'N/A',
            'runner_up': runner_up.name if runner_up else 'N/A',
            'tournament': tournament_name,
            'qualified_teams': [t.name for t in assoc_teams],
            'matches': wc_matches,
            'top_batters': top_batters,
            'top_bowlers': top_bowlers,
        }
    
    def simulate_world_cup_group_with_matches(self, teams, format_type, group_name):
        """
        Simulate round-robin group stage and return both standings and match data
        
        Args:
            teams: List of teams in the group
            format_type: Match format
            group_name: Group identifier (A or B)
        
        Returns:
            Tuple of (standings dict, matches list, player_stats dict)
        """
        # Initialize standings
        standings = {}
        for team in teams:
            standings[team.name] = {
                'played': 0,
                'won': 0,
                'lost': 0,
                'points': 0,
                'nrr': 0.0,
                'runs_for': 0,
                'runs_against': 0,
                'overs_batted': 0,
                'overs_bowled': 0
            }
        
        matches = []
        player_stats = {}  # Track player stats: {player_name: {'runs': 0, 'balls': 0, 'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0, 'team': ''}}
        
        # Round-robin: each team plays every other team once
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team1 = teams[i]
                team2 = teams[j]
                
                # Simulate match
                simulator = FastMatchSimulator(team1, team2, format_type)
                winner = simulator.simulate()
                scorecard = simulator.get_scorecard()
                
                # Store match data
                matches.append({
                    'home': team1.name,
                    'away': team2.name,
                    'format': format_type,
                    'tier': 0,
                    'is_world_cup': True,
                    'round': f'Group {group_name}',
                    'winner': winner.name if winner else 'Tie',
                    'margin': simulator.margin,
                    'man_of_the_match': scorecard.get('man_of_the_match', ''),
                    'scorecard': scorecard
                })
                
                # Extract player stats from scorecard
                self._extract_player_stats_from_scorecard(scorecard, player_stats, team1.name, team2.name)
                
                # Update standings
                innings1 = scorecard['innings'][0]
                innings2 = scorecard['innings'][1]
                
                # Team 1 stats
                standings[team1.name]['played'] += 1
                standings[team1.name]['runs_for'] += innings1['total_runs']
                standings[team1.name]['runs_against'] += innings2['total_runs']
                standings[team1.name]['overs_batted'] += innings1['overs']
                standings[team1.name]['overs_bowled'] += innings2['overs']
                
                # Team 2 stats
                standings[team2.name]['played'] += 1
                standings[team2.name]['runs_for'] += innings2['total_runs']
                standings[team2.name]['runs_against'] += innings1['total_runs']
                standings[team2.name]['overs_batted'] += innings2['overs']
                standings[team2.name]['overs_bowled'] += innings1['overs']
                
                # Update wins/losses and points
                if winner == team1:
                    standings[team1.name]['won'] += 1
                    standings[team1.name]['points'] += 2
                    standings[team2.name]['lost'] += 1
                elif winner == team2:
                    standings[team2.name]['won'] += 1
                    standings[team2.name]['points'] += 2
                    standings[team1.name]['lost'] += 1
                else:  # Tie
                    standings[team1.name]['points'] += 1
                    standings[team2.name]['points'] += 1
        
        # Calculate Net Run Rate for each team
        for team_name, stats in standings.items():
            if stats['overs_batted'] > 0 and stats['overs_bowled'] > 0:
                run_rate_for = stats['runs_for'] / stats['overs_batted']
                run_rate_against = stats['runs_against'] / stats['overs_bowled']
                stats['nrr'] = round(run_rate_for - run_rate_against, 3)
        
        # Print group standings
        print(f"\nGroup {group_name} Standings:")
        print(f"{'Team':<20} {'P':<4} {'W':<4} {'L':<4} {'Pts':<5} {'NRR':<8}")
        print("-" * 60)
        
        sorted_standings = sorted(standings.items(), key=lambda x: (x[1]['points'], x[1]['nrr']), reverse=True)
        for team_name, stats in sorted_standings:
            print(f"{team_name:<20} {stats['played']:<4} {stats['won']:<4} {stats['lost']:<4} {stats['points']:<5} {stats['nrr']:<8.3f}")
        
        return standings, matches, player_stats
    
    def _extract_player_stats_from_scorecard(self, scorecard, player_stats, team1_name, team2_name):
        """Extract batting and bowling stats from scorecard"""
        for innings in scorecard.get('innings', []):
            batting_team = innings.get('team', '')
            
            # Extract batting stats
            for batter in innings.get('batting', []):
                name = batter.get('name', '')
                if not name:
                    continue
                
                if name not in player_stats:
                    player_stats[name] = {
                        'runs': 0, 'balls': 0, 'wickets': 0, 
                        'runs_conceded': 0, 'balls_bowled': 0,
                        'team': batting_team, 'matches': 0,
                        'highest_score': 0, 'fifties': 0, 'hundreds': 0,
                        'four_wickets': 0, 'five_wickets': 0
                    }
                
                runs = batter.get('runs', 0)
                balls = batter.get('balls', 0)
                
                player_stats[name]['runs'] += runs
                player_stats[name]['balls'] += balls
                player_stats[name]['matches'] += 1
                
                # Track milestones
                if runs > player_stats[name]['highest_score']:
                    player_stats[name]['highest_score'] = runs
                if runs >= 50 and runs < 100:
                    player_stats[name]['fifties'] += 1
                if runs >= 100:
                    player_stats[name]['hundreds'] += 1
            
            # Extract bowling stats
            for bowler in innings.get('bowling', []):
                name = bowler.get('name', '')
                if not name:
                    continue
                
                if name not in player_stats:
                    player_stats[name] = {
                        'runs': 0, 'balls': 0, 'wickets': 0, 
                        'runs_conceded': 0, 'balls_bowled': 0,
                        'team': team1_name if batting_team == team2_name else team2_name,
                        'matches': 0, 'highest_score': 0, 'fifties': 0, 'hundreds': 0,
                        'four_wickets': 0, 'five_wickets': 0
                    }
                
                wickets = bowler.get('wickets', 0)
                runs_conceded = bowler.get('runs', 0)
                overs = bowler.get('overs', 0)
                balls_bowled = int(overs) * 6 + int((overs % 1) * 10)
                
                player_stats[name]['wickets'] += wickets
                player_stats[name]['runs_conceded'] += runs_conceded
                player_stats[name]['balls_bowled'] += balls_bowled
                
                # Track milestones
                if wickets >= 4 and wickets < 5:
                    player_stats[name]['four_wickets'] += 1
                if wickets >= 5:
                    player_stats[name]['five_wickets'] += 1
    
    def _calculate_top_batters(self, player_stats):
        """Calculate top 20 batters from World Cup player stats"""
        batters = []
        
        for name, stats in player_stats.items():
            if stats.get('runs', 0) > 0:
                runs = stats.get('runs', 0)
                balls = stats.get('balls', 0)
                matches = stats.get('matches', 1)
                
                # Calculate average and strike rate
                avg = round(runs / max(1, matches), 2)
                sr = round((runs / max(1, balls)) * 100, 2) if balls > 0 else 0
                
                batters.append({
                    'name': name,
                    'team': stats.get('team', 'Unknown'),
                    'runs': runs,
                    'avg': avg,
                    'sr': sr,
                    'matches': matches,
                    'highest_score': stats.get('highest_score', 0),
                    'fifties': stats.get('fifties', 0),
                    'hundreds': stats.get('hundreds', 0)
                })
        
        # Sort by runs (descending), then by average
        batters.sort(key=lambda x: (x['runs'], x['avg']), reverse=True)
        
        return batters[:20]  # Return top 20
    
    def _calculate_top_bowlers(self, player_stats):
        """Calculate top 20 bowlers from World Cup player stats"""
        bowlers = []
        
        for name, stats in player_stats.items():
            if stats.get('wickets', 0) > 0:
                wickets = stats.get('wickets', 0)
                runs_conceded = stats.get('runs_conceded', 0)
                balls_bowled = stats.get('balls_bowled', 0)
                matches = stats.get('matches', 1)
                
                # Calculate average and economy
                avg = round(runs_conceded / max(1, wickets), 2)
                econ = round((runs_conceded / max(1, balls_bowled)) * 6, 2) if balls_bowled > 0 else 0
                
                bowlers.append({
                    'name': name,
                    'team': stats.get('team', 'Unknown'),
                    'wickets': wickets,
                    'avg': avg,
                    'econ': econ,
                    'matches': matches,
                    'runs_conceded': runs_conceded,
                    'four_wickets': stats.get('four_wickets', 0),
                    'five_wickets': stats.get('five_wickets', 0)
                })
        
        # Sort by wickets (descending), then by average (ascending)
        bowlers.sort(key=lambda x: (x['wickets'], -x['avg']), reverse=True)
        
        return bowlers[:20]  # Return top 20
    
    def simulate_world_cup_group(self, teams, format_type, group_name):
        """
        Simulate round-robin group stage
        
        Args:
            teams: List of teams in the group
            format_type: Match format
            group_name: Group identifier (A or B)
        
        Returns:
            Dictionary with team standings
        """
        # Initialize standings
        standings = {}
        for team in teams:
            standings[team.name] = {
                'played': 0,
                'won': 0,
                'lost': 0,
                'points': 0,
                'nrr': 0.0,
                'runs_for': 0,
                'runs_against': 0,
                'overs_batted': 0,
                'overs_bowled': 0
            }
        
        # Round-robin: each team plays every other team once
        matches_played = 0
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team1 = teams[i]
                team2 = teams[j]
                
                # Simulate match
                simulator = FastMatchSimulator(team1, team2, format_type)
                winner = simulator.simulate()
                scorecard = simulator.get_scorecard()
                
                # Update standings
                innings1 = scorecard['innings'][0]
                innings2 = scorecard['innings'][1]
                
                # Team 1 stats
                standings[team1.name]['played'] += 1
                standings[team1.name]['runs_for'] += innings1['total_runs']
                standings[team1.name]['runs_against'] += innings2['total_runs']
                standings[team1.name]['overs_batted'] += innings1['overs']
                standings[team1.name]['overs_bowled'] += innings2['overs']
                
                # Team 2 stats
                standings[team2.name]['played'] += 1
                standings[team2.name]['runs_for'] += innings2['total_runs']
                standings[team2.name]['runs_against'] += innings1['total_runs']
                standings[team2.name]['overs_batted'] += innings2['overs']
                standings[team2.name]['overs_bowled'] += innings1['overs']
                
                # Update wins/losses and points
                if winner == team1:
                    standings[team1.name]['won'] += 1
                    standings[team1.name]['points'] += 2
                    standings[team2.name]['lost'] += 1
                elif winner == team2:
                    standings[team2.name]['won'] += 1
                    standings[team2.name]['points'] += 2
                    standings[team1.name]['lost'] += 1
                else:  # Tie
                    standings[team1.name]['points'] += 1
                    standings[team2.name]['points'] += 1
                
                matches_played += 1
        
        # Calculate Net Run Rate for each team
        for team_name, stats in standings.items():
            if stats['overs_batted'] > 0 and stats['overs_bowled'] > 0:
                run_rate_for = stats['runs_for'] / stats['overs_batted']
                run_rate_against = stats['runs_against'] / stats['overs_bowled']
                stats['nrr'] = round(run_rate_for - run_rate_against, 3)
        
        # Print group standings
        print(f"\nGroup {group_name} Standings:")
        print(f"{'Team':<20} {'P':<4} {'W':<4} {'L':<4} {'Pts':<5} {'NRR':<8}")
        print("-" * 60)
        
        sorted_standings = sorted(standings.items(), key=lambda x: (x[1]['points'], x[1]['nrr']), reverse=True)
        for team_name, stats in sorted_standings:
            print(f"{team_name:<20} {stats['played']:<4} {stats['won']:<4} {stats['lost']:<4} {stats['points']:<5} {stats['nrr']:<8.3f}")
        
        return standings
    
    def _purge_retired_player_from_all_rosters(self, player):
        """Remove a retired player from every international, U21, and domestic squad."""
        for t in self.all_teams:
            if player in t.players:
                t.players.remove(player)
            u21 = getattr(t, "u21_squad", None) or []
            if player in u21:
                u21.remove(player)
        for t in getattr(self, "domestic_teams", None) or []:
            pl = getattr(t, "players", None) or []
            if player in pl:
                pl.remove(player)
    
    def _nation_has_domestic_teams(self, nation_name):
        return any(
            getattr(dt, "parent_nation", None) == nation_name
            for dt in (getattr(self, "domestic_teams", None) or [])
        )
    
    def _domestic_form_score_last_two_years(self, player):
        """Sum domestic runs + weighted wickets from current and previous calendar year."""
        cy = getattr(self, "current_year", 2025)
        years = (cy, cy - 1)
        tot_runs = 0
        tot_wkts = 0
        dys = getattr(player, "domestic_yearly_stats", None) or {}
        for y in years:
            yd = dys.get(y) or {}
            for fmt in ("T20", "ODI", "Test"):
                s = yd.get(fmt) or {}
                tot_runs += int(s.get("runs", 0) or 0)
                tot_wkts += int(s.get("wickets", 0) or 0)
        if tot_runs == 0 and tot_wkts == 0:
            dst = getattr(player, "domestic_stats", None) or {}
            for fmt in ("T20", "ODI", "Test"):
                s = dst.get(fmt) or {}
                tot_runs += int(s.get("runs", 0) or 0)
                tot_wkts += int(s.get("wickets", 0) or 0)
            tot_runs = int(tot_runs * 0.35)
            tot_wkts = int(tot_wkts * 0.35)
        skill = getattr(player, "batting", 0) + getattr(player, "bowling", 0)
        return float(tot_runs + tot_wkts * 18 + skill * 0.4)
    
    def _u21_recruit_score_for_national(self, player):
        """How attractive this U21 player is for a senior national call-up when filling gaps."""
        ys = getattr(player, "yearly_stats", None) or {}
        cy = getattr(self, "current_year", 2025)
        runs = wkts = 0
        for y in (cy, cy - 1):
            yd = ys.get(y) or {}
            for fmt in ("T20", "ODI", "Test"):
                s = yd.get(fmt) or {}
                runs += int(s.get("runs", 0) or 0)
                wkts += int(s.get("wickets", 0) or 0)
        if runs == 0 and wkts == 0:
            for fmt in ("T20", "ODI", "Test"):
                s = (getattr(player, "stats", None) or {}).get(fmt) or {}
                runs += int(s.get("runs", 0) or 0)
                wkts += int(s.get("wickets", 0) or 0)
            runs = int(runs * 0.2)
            wkts = int(wkts * 0.2)
        skill = getattr(player, "batting", 0) + getattr(player, "bowling", 0)
        return float(runs + wkts * 20 + skill * 0.5)
    
    def _promote_u21_to_national_senior(self, national_team, player):
        """Move one player from national U21 to senior list (same as youth promotion path)."""
        u21 = getattr(national_team, "u21_squad", None) or []
        if player not in u21:
            return False
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            return False
        u21.remove(player)
        player.snapshot_u21_and_reset_senior_career()
        player.is_youth_player = False
        player.nationality = national_team.name
        national_team.add_player(player)
        comps = getattr(self.domestic_system, "competitions_by_nation", None) or {}
        if comps:
            t20, odi = pick_affiliations_for_nation(national_team.name, player.name, comps)
            player.domestic_t20_club_name = t20
            player.domestic_odi_fc_club_name = odi
        return True
    
    def _recruit_best_from_domestic_for_national(self, national_team):
        """Pull the best domestic performer (last 2 years) not already on the senior national squad."""
        nation = national_team.name
        best = None
        best_score = -1.0
        best_dt = None
        for dt in getattr(self, "domestic_teams", None) or []:
            if getattr(dt, "parent_nation", None) != nation:
                continue
            for p in list(getattr(dt, "players", None) or []):
                if p in national_team.players:
                    continue
                sc = self._domestic_form_score_last_two_years(p)
                if sc > best_score:
                    best_score = sc
                    best = p
                    best_dt = dt
        if best is None or best_dt is None:
            return False
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            return False
        if best not in best_dt.players:
            return False
        best_dt.players.remove(best)
        self._remove_player_from_national_lineups(best_dt, best)
        best.nationality = nation
        if hasattr(best, "is_youth_player"):
            best.is_youth_player = False
        national_team.add_player(best)
        comps = getattr(self.domestic_system, "competitions_by_nation", None) or {}
        if comps:
            t20, odi = pick_affiliations_for_nation(nation, best.name, comps)
            best.domestic_t20_club_name = t20
            best.domestic_odi_fc_club_name = odi
        print(f"[NationalRecruit] {best.name} called up from {best_dt.name} to {nation} (domestic form score {best_score:.1f})")
        return True
    
    def fill_national_squad_from_domestic_and_u21(self, national_team, target_size=20):
        """
        Never generate random seniors for internationals: fill from domestic (form, last 2 years)
        and U21; associates without domestic may add U21-only then generated U21-age players.
        """
        if getattr(national_team, "is_domestic", False):
            return
        has_domestic = self._nation_has_domestic_teams(national_team.name)
        safety = 0
        tier = max(1, min(5, getattr(national_team, "tier", 3)))
        while len(national_team.players) < target_size and safety < 200:
            safety += 1
            progressed = False
            if has_domestic and self._recruit_best_from_domestic_for_national(national_team):
                progressed = True
            if not progressed:
                u21 = getattr(national_team, "u21_squad", None) or []
                if u21:
                    ranked = sorted(u21, key=lambda p: self._u21_recruit_score_for_national(p), reverse=True)
                    if self._promote_u21_to_national_senior(national_team, ranked[0]):
                        progressed = True
            if not progressed:
                if has_domestic:
                    break
                p = self.generate_player(national_team.name, tier=tier, max_age=21, min_age=17)
                assign_traits_to_player(p)
                national_team.add_player(p)
                print(f"[NationalRecruit] {national_team.name}: added generated U21-age player {p.name} (no domestic league)")
                progressed = True
            if not progressed:
                break
    
    def _process_national_veteran_send_to_domestic(self):
        """50% per season for each national player aged 35+ with a domestic league to move to club cricket."""
        for nt in self.all_teams:
            if getattr(nt, "is_domestic", False):
                continue
            if not self._nation_has_domestic_teams(nt.name):
                continue
            for p in list(nt.players):
                if getattr(p, "age", 0) < 35:
                    continue
                if random.random() >= 0.5:
                    continue
                ok, detail = self.send_national_player_to_domestic(p, nt)
                if ok:
                    print(f"[VeteranDomestic] {p.name} ({p.age}) sent from {nt.name} to domestic club {detail}")
    
    def process_retirements(self, team):
        """
        Process player retirements based on age
        
        Args:
            team: Team object
        
        Returns:
            List of retirement dictionaries
        """
        retirements = []
        
        for player in team.players[:]:  # Copy list to modify during iteration
            # Stronger curve so fewer players linger past 38
            if player.age >= 40:
                retirement_chance = 0.92
            elif player.age >= 39:
                retirement_chance = 0.88
            elif player.age >= 38:
                retirement_chance = 0.82
            elif player.age >= 37:
                retirement_chance = 0.55
            elif player.age >= 36:
                retirement_chance = 0.38
            elif player.age >= 35:
                retirement_chance = 0.18
            elif player.age >= 34:
                retirement_chance = 0.08
            else:
                retirement_chance = 0.0
            
            if random.random() < retirement_chance:
                self._purge_retired_player_from_all_rosters(player)
                retirements.append({
                    'player': player.name,
                    'team': team.name,
                    'age': player.age,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling
                })
                
                print(f"  {player.name} ({player.age}) retired from {team.name}")
        
        return retirements
    
    def age_all_players(self):
        """
        Age every player exactly once for the year (national seniors, U21, domestic squads).
        Uses Player.age_player() for skills/pace; shared Player objects are deduped by id.
        """
        seen: set[int] = set()

        def _age_once(player, team_tier: int) -> None:
            pid = id(player)
            if pid in seen:
                return
            seen.add(pid)
            player.age_player(team_tier)

        for team in self.all_teams:
            team_tier = getattr(team, "tier", 3)
            for player in team.players:
                _age_once(player, team_tier)
            if hasattr(team, "u21_squad") and team.u21_squad:
                for player in team.u21_squad:
                    _age_once(player, team_tier)
        for team in getattr(self, "domestic_teams", None) or []:
            dt = getattr(team, "tier", 3)
            for player in getattr(team, "players", None) or []:
                _age_once(player, dt)

    # ========================================================================
    # LEAGUE STANDINGS HISTORY (Leagues tab — season / year filter)
    # ========================================================================

    _LEAGUE_TAB_U21_NATION_NAMES = (
        "India", "Australia", "England", "Pakistan", "South Africa",
        "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan",
        "Ireland", "Zimbabwe",
    )

    def _compress_team_league_stats(self, team, match_format):
        st = team.format_stats.get(match_format, {})
        return {
            'tier': team.format_tiers.get(match_format, 1),
            'matches_played': int(st.get('matches_played', 0) or 0),
            'wins': int(st.get('wins', 0) or 0),
            'losses': int(st.get('losses', 0) or 0),
            'draws': int(st.get('draws', 0) or 0),
            'points': int(st.get('points', 0) or 0),
            'nrr': float(st.get('nrr', 0.0) or 0.0),
        }

    def _compress_u21_league_stats(self, team, match_format):
        st = (getattr(team, 'u21_stats', None) or {}).get(match_format, {})
        return {
            'matches_played': int(st.get('matches_played', 0) or 0),
            'wins': int(st.get('wins', 0) or 0),
            'losses': int(st.get('losses', 0) or 0),
            'draws': int(st.get('draws', 0) or 0),
            'points': int(st.get('points', 0) or 0),
            'nrr': float(st.get('nrr', 0.0) or 0.0),
        }

    def _snapshot_league_standings_for_history(self):
        """Record international + U21 league totals before season/year increments (cumulative intl stats)."""
        by_format = {}
        u21_by_format = {}
        for fmt in ('T20', 'ODI', 'Test'):
            by_format[fmt] = {}
            for t in self.all_teams:
                if getattr(t, 'is_domestic', False):
                    continue
                by_format[fmt][t.name] = self._compress_team_league_stats(t, fmt)
            u21_by_format[fmt] = {}
            for t in self.all_teams:
                if t.name not in self._LEAGUE_TAB_U21_NATION_NAMES:
                    continue
                if not hasattr(t, 'u21_stats') or fmt not in (t.u21_stats or {}):
                    continue
                u21_by_format[fmt][t.name] = self._compress_u21_league_stats(t, fmt)
        self.league_standings_history.append({
            'season': self.current_season,
            'year': self.current_year,
            'by_format': by_format,
            'u21_by_format': u21_by_format,
        })

    @staticmethod
    def _league_stats_diff(cur, prev):
        """Per-season style row from cumulative snapshots (cur − prev)."""
        if not cur:
            cur = {}
        if not prev:
            prev = {}
        return {
            'matches_played': cur.get('matches_played', 0) - prev.get('matches_played', 0),
            'wins': cur.get('wins', 0) - prev.get('wins', 0),
            'losses': cur.get('losses', 0) - prev.get('losses', 0),
            'draws': cur.get('draws', 0) - prev.get('draws', 0),
            'points': cur.get('points', 0) - prev.get('points', 0),
        }

    def _league_history_entry_for_year(self, calendar_year):
        for e in self.league_standings_history:
            if e.get('year') == calendar_year:
                return e
        return None

    def get_league_season_table_rows(self, match_format, tier_num, season_view_year):
        """
        Rows for Leagues tab table.
        season_view_year: None = current in-progress campaign (delta since last snapshot).
        Otherwise calendar year (int) matching a completed entry in league_standings_history.
        Returns list of dicts: team_name, stats (matches_played, wins, losses, draws, points, nrr or None), nrr_mode.
        nrr_mode: 'live_cumulative' | 'season_unknown' | 'u21_season'
        """
        history = getattr(self, 'league_standings_history', None) or []
        if tier_num == 5:
            return self._get_league_u21_season_rows(match_format, season_view_year, history)
        return self._get_league_intl_season_rows(match_format, tier_num, season_view_year, history)

    def _get_league_intl_season_rows(self, match_format, tier_num, season_view_year, history):
        if season_view_year is None:
            prev_map = history[-1]['by_format'].get(match_format, {}) if history else {}
            rows = []
            for team in self.all_teams:
                if getattr(team, 'is_domestic', False):
                    continue
                if team.format_tiers.get(match_format) != tier_num:
                    continue
                live = self._compress_team_league_stats(team, match_format)
                prev = prev_map.get(team.name, {})
                diff = self._league_stats_diff(live, prev)
                st = team.format_stats.get(match_format, {})
                diff['nrr'] = float(st.get('nrr', 0.0) or 0.0)
                rows.append({
                    'team_name': team.name,
                    'stats': diff,
                    'nrr_mode': 'live_cumulative',
                })
            rows.sort(key=lambda r: (-r['stats']['points'], -r['stats']['wins'], -r['stats']['matches_played']))
            return rows
        entry = self._league_history_entry_for_year(season_view_year)
        if not entry:
            return []
        idx = next((i for i, e in enumerate(history) if e.get('year') == season_view_year), -1)
        prev_entry = history[idx - 1] if idx > 0 else None
        cur_map = entry['by_format'].get(match_format, {})
        prev_map = (prev_entry['by_format'].get(match_format, {}) if prev_entry else {})
        rows = []
        for name, cur in cur_map.items():
            if cur.get('tier') != tier_num:
                continue
            prev = prev_map.get(name, {})
            diff = self._league_stats_diff(cur, prev)
            diff['nrr'] = None
            rows.append({'team_name': name, 'stats': diff, 'nrr_mode': 'season_unknown'})
        rows.sort(key=lambda r: (-r['stats']['points'], -r['stats']['wins'], -r['stats']['matches_played']))
        return rows

    def _get_league_u21_season_rows(self, match_format, season_view_year, history):
        if season_view_year is None:
            teams = [t for t in self.all_teams if t.name in self._LEAGUE_TAB_U21_NATION_NAMES
                     and hasattr(t, 'u21_stats') and match_format in (t.u21_stats or {})]
            rows = []
            for team in teams:
                st = team.u21_stats.get(match_format, {})
                rows.append({
                    'team_name': team.name,
                    'stats': {
                        'matches_played': int(st.get('matches_played', 0) or 0),
                        'wins': int(st.get('wins', 0) or 0),
                        'losses': int(st.get('losses', 0) or 0),
                        'draws': int(st.get('draws', 0) or 0),
                        'points': int(st.get('points', 0) or 0),
                        'nrr': float(st.get('nrr', 0.0) or 0.0),
                    },
                    'nrr_mode': 'u21_season',
                })
            rows.sort(key=lambda r: (-r['stats']['points'], -r['stats']['nrr']))
            return rows
        entry = self._league_history_entry_for_year(season_view_year)
        if not entry:
            return []
        # U21 snapshots are already stored as season totals (not cumulative lifetime totals).
        # So for year-filtered league view we must use the snapshot directly and NOT subtract
        # previous season again (that would double-difference and break Played/Won/Lost).
        cur_map_direct = entry.get('u21_by_format', {}).get(match_format, {})
        direct_rows = []
        for name, cur in cur_map_direct.items():
            direct_rows.append({
                'team_name': name,
                'stats': {
                    'matches_played': int(cur.get('matches_played', 0) or 0),
                    'wins': int(cur.get('wins', 0) or 0),
                    'losses': int(cur.get('losses', 0) or 0),
                    'draws': int(cur.get('draws', 0) or 0),
                    'points': int(cur.get('points', 0) or 0),
                    'nrr': None,
                },
                'nrr_mode': 'season_unknown',
            })
        if direct_rows:
            direct_rows.sort(key=lambda r: (-r['stats']['points'], -r['stats']['wins'], -r['stats']['matches_played']))
            return direct_rows
        idx = next((i for i, e in enumerate(history) if e.get('year') == season_view_year), -1)
        prev_entry = history[idx - 1] if idx > 0 else None
        cur_map = entry.get('u21_by_format', {}).get(match_format, {})
        prev_map = (prev_entry.get('u21_by_format', {}).get(match_format, {}) if prev_entry else {})
        rows = []
        for name, cur in cur_map.items():
            prev = prev_map.get(name, {})
            diff = self._league_stats_diff(cur, prev)
            diff['nrr'] = None
            rows.append({'team_name': name, 'stats': diff, 'nrr_mode': 'season_unknown'})
        rows.sort(key=lambda r: (-r['stats']['points'], -r['stats']['wins'], -r['stats']['matches_played']))
        return rows

    def get_team_tier_at_league_year(self, team, match_format, calendar_year):
        """International team's tier at end of a completed year (for Rankings tier filter)."""
        entry = self._league_history_entry_for_year(calendar_year)
        if not entry:
            return team.format_tiers.get(match_format, getattr(team, "tier", 1))
        row = entry.get("by_format", {}).get(match_format, {}).get(team.name)
        if row and "tier" in row:
            return int(row.get("tier") or 1)
        return team.format_tiers.get(match_format, getattr(team, "tier", 1))

    # ========================================================================
    # PLAYER DEVELOPMENT - STEP 9C
    # ========================================================================
    
    def complete_season(self, format_type='T20', increment_season=True, skip_development=False):
        """
        Complete season with player development and tier updates
        
        Args:
            format_type: 'T20', 'ODI', or 'Test'
            increment_season: If True, increment season/year (set to False when called multiple times for same season)
            skip_development: If True, skip player development steps (used when completing multiple formats in one year)
        
        Returns:
            Updated season summary
        """
        
        print(f"\n{'='*60}")
        print(f"COMPLETING SEASON {self.current_season} - {format_type}")
        print(f"{'='*60}\n")
        
        # PHASE 14: Save season statistics for all players
        # Only save skill snapshots once per year (when skip_development=False, i.e., final format)
        if not skip_development:
            print(f"[Season] Saving season statistics to player history...")
            for team in self.all_teams:
                for player in team.players:
                    # Save season stats for all formats
                    for fmt in ['T20', 'ODI', 'Test']:
                        player.save_season_stats(self.current_season, fmt)
                    
                    # Save skill snapshot (only once per year)
                    player.save_skill_snapshot(self.current_season)
            print(f"[Season] Season statistics saved for all players")
        else:
            print(f"[Season] Skipping skill snapshot save (will be done on final format)")
        
        if not skip_development:
            # These steps only run once per year (on the final format completion)
            
            # Step 6: Promote eligible youth players
            print(f"[Season] Step 6: Promoting youth players...")
            # Defer season_promotions rows until after Step 7 age_all_players(), so summary Age matches
            # player profile (was: snapshot pre-aging age, profile showed +1 year).
            promotions_pending = []
            for team in self.all_teams:
                promoted = self.youth_system.promote_youth_players(team, format_type, max_promotions=2)
                for player in promoted:
                    promotions_pending.append((team, player))
            print(f"[Season] {len(promotions_pending)} youth players promoted (summary recorded after year-end aging)")
            
            # Step 6b: Fill national squads from domestic form + U21 (no random senior generation for internationals)
            print(f"[Season] Step 6b: Filling national squads from domestic / U21...")
            for team in self.all_teams:
                if getattr(team, "is_domestic", False):
                    continue
                target_size = 20
                if len(team.players) < target_size:
                    before = len(team.players)
                    self.fill_national_squad_from_domestic_and_u21(team, target_size)
                    added = len(team.players) - before
                    if added:
                        print(f"[Season] {team.name}: filled {added} senior spot(s) via domestic/U21 pipeline")
            
            self.fill_missing_domestic_club_names()
            
            # Step 7: Age all players (senior + U21) by 1 year before handling aged-out youth
            print(f"[Season] Step 7: Aging all players by 1 year...")
            self.age_all_players()
            
            for team, player in promotions_pending:
                prom = {
                    'player': player.name,
                    'team': team.name,
                    'age': player.age,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling
                }
                self.season_promotions.append(prom)
                self._append_career_promotion_log(prom)
            
            # Step 8: Age youth players and replace aged-out
            print(f"[Season] Step 8: Aging youth players and handling promotions/transfers...")
            transferred_to_domestic_total = 0
            transferred_to_associate_total = 0
            promoted_from_u21 = 0
            
            # Get associate teams (Tier 4 and Tier 5) for aged-out player transfers
            associate_teams = [t for t in self.all_teams 
                              if t.format_tiers.get(format_type, 5) >= 4]
            print(f"[Season] Found {len(associate_teams)} associate teams for fallback transfers")
            
            for team in self.all_teams:
                promoted_to_senior, transferred = self.youth_system.age_youth_players(team, self, associate_teams)
                transferred_to_domestic_total += sum(1 for t in transferred if t.get('to_domestic'))
                transferred_to_associate_total += sum(1 for t in transferred if not t.get('to_domestic'))
                promoted_from_u21 += len(promoted_to_senior)
                n_new = len(transferred) + len(promoted_to_senior)
                new_youth = self.youth_system.replace_aged_out_players(team, n_new)
                comps = getattr(self.domestic_system, 'competitions_by_nation', None) or {}
                if comps:
                    for np in new_youth:
                        t20, odi = pick_affiliations_for_nation(team.name, np.name, comps)
                        np.domestic_t20_club_name = t20
                        np.domestic_odi_fc_club_name = odi
            for team in self.all_teams:
                fill_youth = self.youth_system.ensure_u21_squad_strength(team)
                comps = getattr(self.domestic_system, 'competitions_by_nation', None) or {}
                if comps and fill_youth:
                    for np in fill_youth:
                        t20, odi = pick_affiliations_for_nation(team.name, np.name, comps)
                        np.domestic_t20_club_name = t20
                        np.domestic_odi_fc_club_name = odi
            print(f"[Season] Youth exits: {transferred_to_domestic_total} to domestic clubs, "
                  f"{transferred_to_associate_total} to associate nations; {promoted_from_u21} promoted to senior")
            
            self.fill_missing_domestic_club_names()
            
            # Step 8: Develop youth players
            print(f"[Season] Step 8: Developing youth players...")
            for team in self.all_teams:
                self.youth_system.develop_youth_players(team, current_season=self.current_season)
            print(f"[Season] Youth players developed")
            
            # Step 9: Player skill progression/regression
            print(f"[Season] Step 9: Processing player skill changes...")
            for team in self.all_teams:
                skill_changes = self.process_player_progression(team)
                self.season_changes.extend(skill_changes)
            for team in getattr(self, 'domestic_teams', None) or []:
                skill_changes = self.process_player_progression(team)
                self.season_changes.extend(skill_changes)
            print(f"[Season] {len(self.season_changes)} significant skill changes")
            
            # Step 10: Trait evolution
            print(f"[Season] Step 10: Processing trait evolution...")
            trait_changes = 0
            for team in self.all_teams:
                changes = self.process_trait_evolution(team, format_type)
                trait_changes += len(changes)
                self.season_changes.extend(changes)
            print(f"[Season] {trait_changes} trait changes")
            
            # Step 10b: Transfer poor Test performers from top 12 Test nations to associate nations
            self._process_test_transfers_to_associates()
            # Step 10c1: Veterans 35+ — 50% chance per year to return to domestic cricket (nations with a league)
            self._process_national_veteran_send_to_domestic()
            # Step 10c2: Domestic to national call-ups (top performers with skills can join national squad)
            self._process_domestic_call_ups()
            for team in self.all_teams:
                if getattr(team, "is_domestic", False):
                    continue
                if len(team.players) < 20:
                    self.fill_national_squad_from_domestic_and_u21(team, 20)
            assign_foreign_t20_elite_national_squads(
                self.all_teams,
                getattr(self, 'domestic_teams', None) or [],
                getattr(self.domestic_system, 'competitions_by_nation', None) or {},
            )
            self.sync_national_players_into_domestic_club_squads()
        else:
            print(f"[Season] Skipping development steps (will be done on final format)")
        
        # Step 11: Update tier standings and process promotion/relegation
        # Only process for the CURRENT format to avoid running 3x per year
        print(f"[Season] Step 11: Updating {format_type} tier standings...")
        promoted, relegated = self.tier_manager.tier_systems[format_type].process_promotion_relegation(self.all_teams)
        promoted_teams = promoted
        relegated_teams = relegated
        print(f"[Season] {format_type} Promotions: {len(promoted_teams)}, Relegations: {len(relegated_teams)}")
        
        # Step 12: Award season-end credits
        print(f"[Season] Step 12: Awarding credits...")
        self.award_season_credits(format_type)
        print(f"[Season] Credits awarded")
        
        # Step 13: Generate new fixtures for next season
        # Only regenerate ALL fixtures once (on final format) to avoid stale/duplicate fixtures
        if not skip_development:
            print(f"[Season] Step 13: Generating fixtures for next season...")
            next_season = self.current_season + 1
            wc_month = self._get_wc_month(next_season)
            self.fixtures = self.tier_manager.generate_all_fixtures(
                wc_month=wc_month, current_season=next_season
            )
            # Pre-generate World Cup group stage fixtures for next season
            self.generate_world_cup_fixtures(for_season=next_season)
            # Domestic fixtures are reused each year; without resetting completed flags,
            # simulate_season would skip all domestic games so domestic_stats never grow.
            self._reset_domestic_fixtures_for_new_season()
            print(f"[Season] New fixtures generated")
        else:
            print(f"[Season] Step 13: Skipping fixture generation (will be done on final format)")
        
        # Step 14: Increment season (aging runs once in Step 7 via age_all_players when development runs)
        if increment_season:
            print(f"[Season] Step 14: Advancing season and year...")
            self._snapshot_league_standings_for_history()
            self.current_season += 1
            self.current_year += 1
            print(f"[Season] Advanced to Season {self.current_season}, Year {self.current_year}")
            
            # Step 15: Reset training points for ALL teams so any team selected in Training tab has points
            print(f"[Season] Step 15: Resetting training points for all teams...")
            for team in self.all_teams:
                self.training_system.reset_training_points(team)
            print(f"[Season] All teams received {self.training_system.training_points_per_season} training points")
        else:
            print(f"[Season] Skipping season increment and player aging (will be done by caller)")
        
        print(f"\n{'='*60}")
        print(f"SEASON COMPLETE - Now Season {self.current_season}")
        print(f"{'='*60}\n")
        
        return {
            'promotions': self.season_promotions,
            'skill_changes': self.season_changes,
            'tier_promoted': promoted_teams,
            'tier_relegated': relegated_teams
        }
    
    def process_player_progression(self, team):
        """
        Process player skill progression/regression based on age.
        Runs ONCE per year per player (guarded by _annual_skill_development_season; shared with U21 develop).
        
        Age-based skill changes:
        - Under 23: Improve (young, developing)
        - 23-28: Peak (slight improvement)
        - 29-32: Stable (no change)
        - 33-35: Decline (slight regression)
        - 36+: Significant decline
        
        Returns:
            List of significant skill changes
        """
        skill_changes = []
        
        for player in team.players:
            # Guard: one automatic skill-development pass per season (also set by develop_youth_players).
            # Same player object can sit on national + domestic squads; domestic loop must not double-apply.
            if getattr(player, '_annual_skill_development_season', None) == self.current_season:
                continue
            
            old_batting = player.batting
            old_bowling = player.bowling
            old_fielding = player.fielding
            
            # Determine age category and change parameters
            if player.age < 23:
                # Young players improve
                change_range = (-1, 2)
            elif player.age <= 28:
                # Peak years - slight improvement
                change_range = (-1, 2)
            elif player.age <= 32:
                # Stable years - minimal change
                change_range = (-1, 1)
            elif player.age <= 35:
                # Decline begins
                change_range = (-2, 0)
            else:
                # Significant decline
                change_range = (-3, 0)
            
            # Apply skill changes (once per year, capped at 4 total points)
            total_applied = 0
            max_total_change = 4
            
            # Batting change
            if 'Batter' in player.role or 'Wicketkeeper' in player.role or 'All-Rounder' in player.role:
                change = random.randint(*change_range)
                change = max(-max_total_change, min(max_total_change - total_applied, change))
                player.batting = max(20, min(99, player.batting + change))
                total_applied += abs(change)
            
            # Bowling change
            if 'Bowler' in player.role or 'Spinner' in player.role or 'Pacer' in player.role or 'All-Rounder' in player.role:
                remaining = max_total_change - total_applied
                if remaining > 0:
                    change = random.randint(*change_range)
                    change = max(-remaining, min(remaining, change))
                    player.bowling = max(20, min(99, player.bowling + change))
                    total_applied += abs(change)
            
            # Fielding change (all players)
            remaining = max_total_change - total_applied
            if remaining > 0:
                change = random.randint(*change_range)
                change = max(-remaining, min(remaining, change))
                player.fielding = max(20, min(99, player.fielding + change))
            
            # Update bowling movements if bowling skill changed and player has movements
            if old_bowling != player.bowling and hasattr(player, 'bowling_movements') and player.bowling_movements:
                player.bowling_movements['movements'] = update_bowling_movements(
                    player.bowling_movements['movements'],
                    old_bowling,
                    player.bowling
                )
            
                        
            # Track significant changes (3+ points in any skill)
            total_change = abs(player.batting - old_batting) + \
                          abs(player.bowling - old_bowling) + \
                          abs(player.fielding - old_fielding)
            
            if total_change >= 3:
                skill_changes.append({
                    'type': 'skill_change',
                    'player': player.name,
                    'team': team.name,
                    'age': player.age,
                    'old_batting': old_batting,
                    'new_batting': player.batting,
                    'old_bowling': old_bowling,
                    'new_bowling': player.bowling,
                    'old_fielding': old_fielding,
                    'new_fielding': player.fielding,
                    'total_change': total_change
                })
            
            player._annual_skill_development_season = self.current_season
        
        return skill_changes
    
    def _role_is_primary_batter(self, role):
        """True if role is a batting-only role (Opening Batter, Middle Order, Wicketkeeper, etc.)."""
        if not role:
            return False
        return role in (
            'Opening Batter', 'Middle Order Batter', 'Lower Order Batter', 'Wicketkeeper Batter'
        )

    def _role_is_primary_bowler(self, role):
        """True if role is a bowling-only role (Finger Spinner, Fast Bowler, etc.)."""
        if not role:
            return False
        return role in (
            'Finger Spinner', 'Wrist Spinner', 'Medium Pacer', 'Fast Medium Pacer', 'Fast Bowler'
        )

    def _role_is_allrounder(self, role):
        """True if role is any allrounder (Batting/Bowling/Genuine Allrounder)."""
        if not role:
            return False
        return 'Allrounder' in role or 'All-Rounder' in role

    def _player_has_batting_role(self, player):
        """True if player is judged on batting for transfer (primary batter or batting/genuine allrounder)."""
        r = player.role or ''
        return self._role_is_primary_batter(r) or 'Batting Allrounder' in r or 'Genuine Allrounder' in r

    def _player_has_bowling_role(self, player):
        """True if player is judged on bowling for transfer (primary bowler or bowling/genuine allrounder)."""
        r = player.role or ''
        return self._role_is_primary_bowler(r) or 'Bowling Allrounder' in r or 'Genuine Allrounder' in r

    def _get_last_n_seasons_stats(self, player, n=3):
        """
        Aggregate batting/bowling stats over the last n seasons from yearly_stats.
        Returns dict with 'Test' and 'T20' keys; each value is a dict with matches, runs,
        dismissals (Test only), wickets, runs_conceded, batting_average, bowling_average.
        """
        result = {'Test': {'matches': 0, 'runs': 0, 'dismissals': 0, 'wickets': 0, 'runs_conceded': 0,
                          'batting_average': 0.0, 'bowling_average': 999.0},
                  'T20': {'matches': 0, 'runs': 0, 'dismissals': 0, 'wickets': 0, 'runs_conceded': 0,
                         'batting_average': 0.0, 'bowling_average': 999.0}}
        if not getattr(player, 'yearly_stats', None):
            return result
        years = sorted(player.yearly_stats.keys(), reverse=True)[:n]
        for year in years:
            for fmt in ('Test', 'T20'):
                if fmt not in player.yearly_stats[year]:
                    continue
                ys = player.yearly_stats[year][fmt]
                result[fmt]['matches'] += ys.get('matches', 0)
                result[fmt]['runs'] += ys.get('runs', 0)
                result[fmt]['dismissals'] += ys.get('dismissals', 0)
                result[fmt]['wickets'] += ys.get('wickets', 0)
                result[fmt]['runs_conceded'] += ys.get('runs_conceded', 0)
        for fmt in ('Test', 'T20'):
            r = result[fmt]
            if fmt == 'Test' and r['dismissals'] > 0:
                r['batting_average'] = round(r['runs'] / r['dismissals'], 2)
            elif r['matches'] > 0:
                r['batting_average'] = round(r['runs'] / r['matches'], 2)
            if r['wickets'] > 0:
                r['bowling_average'] = round(r['runs_conceded'] / r['wickets'], 2)
        return result

    @staticmethod
    def _eligible_for_domestic_national_swap(player):
        """Batsmen, allrounders, bowlers, and keepers are all eligible."""
        from cricket_manager.utils.helpers import is_batter, is_bowler, is_allrounder, is_keeper
        role = getattr(player, 'role', '') or ''
        return is_batter(role) or is_bowler(role) or is_allrounder(role) or is_keeper(role)

    def _t20_season_performance_score(self, player):
        """
        Single number for ranking T20 season form (uses current season_stats['T20'],
        still populated when this runs after save_season_stats copies to history).
        Higher = better season.
        """
        s = getattr(player, 'season_stats', {}).get('T20') or {}
        runs = int(s.get('runs', 0) or 0)
        wkts = int(s.get('wickets', 0) or 0)
        m = int(s.get('matches', 0) or 0)
        bf = int(s.get('balls_faced', 0) or 0)
        bb = int(s.get('balls_bowled', 0) or 0)
        rc = int(s.get('runs_conceded', 0) or 0)
        # Batting: volume + strike rate shape
        sr = (runs / bf * 100.0) if bf > 0 else 0.0
        bat_pts = runs * 1.15 + sr * 0.35 + (runs / max(1, m)) * 2.5
        # Bowling: wickets + economy shape
        bowl_pts = wkts * 26.0
        if bb > 0:
            econ = (rc / bb) * 6.0
            bowl_pts += max(0.0, 36.0 - econ) * 1.8
        if m == 0 and runs == 0 and wkts == 0:
            # No T20 data this season — small skill-based prior so lists still rank
            return (
                getattr(player, 'batting', 0) * 0.12
                + getattr(player, 'bowling', 0) * 0.12
                + getattr(player, 'form', 50) * 0.05
            )
        return bat_pts + bowl_pts

    def _process_domestic_call_ups(self):
        """
        Each season, for every international team that has a domestic league:
        demote the 2 worst T20 performers on the senior national squad and promote the 2 best
        T20 performers from domestic clubs (batters / allrounders / bowlers / keepers).
        """
        domestic_teams = getattr(self, 'domestic_teams', []) or []
        if not domestic_teams:
            return
        max_pairs = 2
        any_swap = False
        comps = getattr(self.domestic_system, 'competitions_by_nation', None) or {}

        for nation_team in self.all_teams:
            if getattr(nation_team, 'is_domestic', False):
                continue
            nation = nation_team.name
            if not self._nation_has_domestic_teams(nation):
                continue
            nation_domestic = [t for t in domestic_teams if getattr(t, 'parent_nation', None) == nation]
            if not nation_domestic:
                continue

            nationals_eligible = [
                p for p in getattr(nation_team, 'players', []) or []
                if self._eligible_for_domestic_national_swap(p)
            ]
            if len(nationals_eligible) < 1:
                continue
            # Worst 2: lowest T20 season score
            worst_two = sorted(
                nationals_eligible,
                key=lambda p: self._t20_season_performance_score(p),
            )[:max_pairs]

            # Best domestic: not already on national senior list, same role filter
            domestic_pool = []
            seen_pid = set()
            for dt in nation_domestic:
                for p in list(getattr(dt, 'players', None) or []):
                    if p in nation_team.players:
                        continue
                    if not self._eligible_for_domestic_national_swap(p):
                        continue
                    pid = id(p)
                    if pid in seen_pid:
                        continue
                    seen_pid.add(pid)
                    sc = self._t20_season_performance_score(p)
                    domestic_pool.append((sc, p, dt))
            domestic_pool.sort(key=lambda x: -x[0])
            best_two = domestic_pool[:max_pairs]

            n_pairs = min(len(worst_two), len(best_two))
            if n_pairs < 1:
                continue

            for i in range(n_pairs):
                wplay = worst_two[i]
                sc_dom, bplay, from_dt = best_two[i]
                if wplay is bplay:
                    continue
                ok, detail = self.send_national_player_to_domestic(wplay, nation_team)
                if not ok:
                    print(f"[DomesticCallUp] {nation}: could not demote {getattr(wplay, 'name', '?')} — {detail}")
                    continue
                if bplay not in from_dt.players:
                    continue
                from_dt.players.remove(bplay)
                self._remove_player_from_national_lineups(from_dt, bplay)
                bplay.nationality = nation
                if hasattr(bplay, 'is_youth_player'):
                    bplay.is_youth_player = False
                if not nation_team.add_player(bplay):
                    # Restore wplay from domestic club back to national; put bplay back on club
                    from_dt.players.append(bplay)
                    for dt in nation_domestic:
                        if wplay in getattr(dt, 'players', []):
                            dt.players.remove(wplay)
                            self._remove_player_from_national_lineups(dt, wplay)
                            break
                    nation_team.add_player(wplay)
                    print(f"[DomesticCallUp] {nation}: reverted swap (national full) for {getattr(bplay, 'name', '?')}")
                    continue
                if comps:
                    t20, odi = pick_affiliations_for_nation(nation, bplay.name, comps)
                    bplay.domestic_t20_club_name = t20
                    bplay.domestic_odi_fc_club_name = odi
                any_swap = True
                xfer = {
                    'player': bplay.name,
                    'from_team': from_dt.name,
                    'to_team': nation,
                    'reason': (
                        f"T20 season swap: promoted (score {sc_dom:.1f}); "
                        f"{getattr(wplay, 'name', '?')} demoted to domestic ({detail})"
                    ),
                    'format': 'T20',
                    'matches': None,
                    'bat_avg': None,
                    'ball_avg': None,
                    'role': bplay.role or '',
                    'return': False,
                }
                self.season_transfers.append(xfer)
                self._append_career_transfer_log(xfer)
                print(
                    f"[DomesticCallUp] {bplay.name} → {nation} (T20 score {sc_dom:.1f}); "
                    f"{wplay.name} → domestic ({detail})"
                )

        if any_swap and comps:
            assign_foreign_t20_elite_national_squads(self.all_teams, domestic_teams, comps)

    def _remove_player_from_national_lineups(self, national_team, player):
        """Clear selected XI / batting order / captaincy entries for this player."""
        name = getattr(player, "name", None)
        if not name:
            return
        xi = getattr(national_team, "selected_xi_names", None)
        if xi:
            national_team.selected_xi_names = [n for n in xi if n != name]
            if not national_team.selected_xi_names:
                national_team.selected_xi_names = None
        bo = getattr(national_team, "batting_order_names", None)
        if bo:
            national_team.batting_order_names = [n for n in bo if n != name]
            if not national_team.batting_order_names:
                national_team.batting_order_names = None
        if getattr(national_team, "captain_name", None) == name:
            national_team.captain_name = None
        if getattr(national_team, "vice_captain_name", None) == name:
            national_team.vice_captain_name = None

    def promote_domestic_player_to_national(self, player, domestic_team):
        """
        Move a player from a domestic club squad to their parent nation's senior international squad.
        Does not swap another player down (unlike end-of-season call-ups).

        Returns:
            (True, national_team_name) on success, or (False, error_message).
        """
        if player not in getattr(domestic_team, "players", []):
            return False, "Player is not on this domestic squad."
        if not getattr(domestic_team, "is_domestic", False):
            return False, "This is not a domestic club."
        nation = getattr(domestic_team, "parent_nation", None)
        if not nation:
            return False, "Domestic team has no parent nation set."
        national_team = self.get_team_by_name(nation)
        if not national_team:
            return False, f"No international team named \"{nation}\"."
        if getattr(national_team, "is_domestic", False):
            return False, "Parent nation team is not a national side."
        if player in national_team.players:
            return False, "Player is already on the national senior squad."
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            return False, (
                f"{nation} senior squad is full (maximum {MAX_SQUAD_SIZE} players). "
                "Release or move a player first."
            )

        domestic_team.players.remove(player)
        self._remove_player_from_national_lineups(domestic_team, player)
        if not national_team.add_player(player):
            domestic_team.players.append(player)
            return False, "Could not add player to national squad (full)."

        if hasattr(player, "is_youth_player"):
            player.is_youth_player = False
        player.nationality = nation

        comps = getattr(self.domestic_system, "competitions_by_nation", None) or {}
        t20, odi = pick_affiliations_for_nation(nation, getattr(player, "name", ""), comps)
        player.domestic_t20_club_name = t20
        player.domestic_odi_fc_club_name = odi
        if hasattr(player, "foreign_t20_club_name"):
            player.foreign_t20_club_name = ""
        assign_foreign_t20_elite_national_squads(
            self.all_teams,
            getattr(self, "domestic_teams", None) or [],
            comps,
        )
        self.sync_national_players_into_domestic_club_squads()
        print(
            f"[DomesticPromote] {player.name} promoted from {domestic_team.name} "
            f"to {nation} national senior squad"
        )
        return True, national_team.name

    def send_national_player_to_domestic(self, player, national_team):
        """
        Remove a senior player from the national squad and place them on a domestic club
        for the same country. Prefers a club matching existing domestic_t20_club_name or
        domestic_odi_fc_club_name when that team exists and has space; otherwise picks a
        random domestic side with room.

        Returns:
            (True, domestic_team_name) on success, or (False, error_message).
        """
        if player not in getattr(national_team, "players", []):
            return False, "Player is not on this national squad."
        if getattr(national_team, "is_domestic", False):
            return False, "This is not a national team."
        domestic_teams = getattr(self, "domestic_teams", None) or []
        nation = national_team.name
        candidates = [
            dt for dt in domestic_teams if getattr(dt, "parent_nation", None) == nation
        ]
        if not candidates:
            return False, f"No domestic clubs exist for {nation}."

        def _with_space(pool):
            return [dt for dt in pool if len(dt.players) < MAX_SQUAD_SIZE]

        t20n = (getattr(player, "domestic_t20_club_name", None) or "").strip()
        odi_fc = (getattr(player, "domestic_odi_fc_club_name", None) or "").strip()
        preferred = [dt for dt in candidates if dt.name == t20n or dt.name == odi_fc]
        target_pool = _with_space(preferred) if preferred else []
        if not target_pool:
            target_pool = _with_space(candidates)
        if not target_pool:
            return False, (
                "All domestic squads are full for this nation. "
                "Release a domestic player first."
            )
        target = random.choice(target_pool)

        national_team.players.remove(player)
        self._remove_player_from_national_lineups(national_team, player)
        if not target.add_player(player):
            national_team.players.append(player)
            return False, "Could not add player to domestic squad (full)."

        comps = getattr(self.domestic_system, "competitions_by_nation", None) or {}

        t20, odi = pick_affiliations_for_domestic_squad_player(player, target, comps)
        player.domestic_t20_club_name = t20
        player.domestic_odi_fc_club_name = odi
        if hasattr(player, "foreign_t20_club_name"):
            player.foreign_t20_club_name = ""
        assign_foreign_t20_elite_national_squads(self.all_teams, domestic_teams, comps)
        if getattr(player, "nationality", None) != nation:
            player.nationality = nation
        return True, target.name

    def send_u21_player_to_domestic(self, player, national_team):
        """
        Remove a player from the national U21 squad and place them on a domestic club
        for the same country. Uses the same placement rules as send_national_player_to_domestic.
        """
        u21 = getattr(national_team, "u21_squad", None) or []
        if player not in u21:
            return False, "Player is not on this national U21 squad."
        if getattr(national_team, "is_domestic", False):
            return False, "This is not a national team."
        domestic_teams = getattr(self, "domestic_teams", None) or []
        nation = national_team.name
        candidates = [
            dt for dt in domestic_teams if getattr(dt, "parent_nation", None) == nation
        ]
        if not candidates:
            return False, f"No domestic clubs exist for {nation}."

        def _with_space(pool):
            return [dt for dt in pool if len(dt.players) < MAX_SQUAD_SIZE]

        t20n = (getattr(player, "domestic_t20_club_name", None) or "").strip()
        odi_fc = (getattr(player, "domestic_odi_fc_club_name", None) or "").strip()
        preferred = [dt for dt in candidates if dt.name == t20n or dt.name == odi_fc]
        target_pool = _with_space(preferred) if preferred else []
        if not target_pool:
            target_pool = _with_space(candidates)
        if not target_pool:
            return False, (
                "All domestic squads are full for this nation. "
                "Release a domestic player first."
            )
        target = random.choice(target_pool)

        if hasattr(player, "snapshot_u21_and_reset_senior_career"):
            player.snapshot_u21_and_reset_senior_career()
        national_team.u21_squad.remove(player)
        if not target.add_player(player):
            national_team.u21_squad.append(player)
            return False, "Could not add player to domestic squad (full)."

        comps = getattr(self.domestic_system, "competitions_by_nation", None) or {}

        t20, odi = pick_affiliations_for_domestic_squad_player(player, target, comps)
        player.domestic_t20_club_name = t20
        player.domestic_odi_fc_club_name = odi
        if hasattr(player, "foreign_t20_club_name"):
            player.foreign_t20_club_name = ""
        assign_foreign_t20_elite_national_squads(self.all_teams, domestic_teams, comps)
        if getattr(player, "nationality", None) != nation:
            player.nationality = nation
        if hasattr(player, "is_youth_player"):
            player.is_youth_player = False
        self.sync_national_players_into_domestic_club_squads()
        print(
            f"[U21Domestic] {player.name} moved from {nation} U21 to domestic {target.name}"
        )
        return True, target.name

    def _process_test_transfers_to_associates(self):
        """
        Transfer players from top 12 Test nations to random associate nations if they have
        poor stats in the LAST 3 SEASONS (Test: 20+ matches, bat avg < 20 or ball avg > 50;
        T20: 40+ matches, bat avg < 15 or ball avg > 40). Associates have no squad limit.
        Players can return to their original Test nation if LAST 3 SEASONS Test bat avg > 42
        and T20 bat avg > 32 (batters), or Test ball avg < 28 and T20 ball avg < 24 (bowlers).
        """
        # Top 12 Test nations = Test tier 1
        test_nations = [t for t in self.all_teams if t.format_tiers.get('Test', 5) == 1]
        associate_teams = [t for t in self.all_teams if t.format_tiers.get('Test', 1) != 1]
        if not associate_teams:
            return

        # --- Step 1: Process returns (associate -> original Test nation) ---
        for team in list(associate_teams):
            for player in list(team.players):
                original_name = getattr(player, 'original_team_name', None)
                if not original_name:
                    continue
                original_team = self.get_team_by_name(original_name)
                if not original_team or original_team not in test_nations:
                    continue
                last3 = self._get_last_n_seasons_stats(player, n=3)
                t = last3['Test']
                t20 = last3['T20']
                test_m = t['matches']
                test_dismissals = t['dismissals']
                test_wickets = t['wickets']
                test_bat_avg = t['batting_average']
                test_ball_avg = t['bowling_average']
                t20_m = t20['matches']
                t20_bat_avg = t20['batting_average']
                t20_wickets = t20['wickets']
                t20_ball_avg = t20['bowling_average']
                qualifies_bat = (
                    test_m >= 20 and test_dismissals >= 5 and test_bat_avg > 42
                    and t20_m >= 40 and t20_bat_avg > 32
                )
                qualifies_ball = (
                    test_wickets >= 10 and test_ball_avg < 28
                    and t20_wickets >= 5 and t20_ball_avg < 24
                )
                return_now = False
                reason_parts = []
                if self._player_has_batting_role(player) and not self._player_has_bowling_role(player):
                    return_now = qualifies_bat
                    if return_now:
                        reason_parts.append(f"Test bat avg (L3) {test_bat_avg} > 42, T20 bat avg (L3) {t20_bat_avg} > 32")
                elif self._player_has_bowling_role(player) and not self._player_has_batting_role(player):
                    return_now = qualifies_ball
                    if return_now:
                        reason_parts.append(f"Test ball avg (L3) {test_ball_avg} < 28, T20 ball avg (L3) {t20_ball_avg} < 24")
                else:
                    return_now = qualifies_bat or qualifies_ball
                    if qualifies_bat:
                        reason_parts.append(f"Bat: Test {test_bat_avg} > 42, T20 {t20_bat_avg} > 32 (L3)")
                    if qualifies_ball:
                        reason_parts.append(f"Ball: Test {test_ball_avg} < 28, T20 {t20_ball_avg} < 24 (L3)")
                if not return_now or not reason_parts:
                    continue
                try:
                    team.players.remove(player)
                except ValueError:
                    continue
                original_team.players.append(player)
                player.nationality = original_team.name
                if hasattr(player, 'original_team_name'):
                    delattr(player, 'original_team_name')
                reason = "Return: " + "; ".join(reason_parts)
                xfer = {
                    'player': player.name,
                    'from_team': team.name,
                    'to_team': original_team.name,
                    'reason': reason,
                    'format': 'Return',
                    'matches': None,
                    'bat_avg': test_bat_avg if qualifies_bat else None,
                    'ball_avg': test_ball_avg if qualifies_ball else None,
                    'role': player.role or '',
                    'return': True,
                }
                self.season_transfers.append(xfer)
                self._append_career_transfer_log(xfer)
                print(f"[Transfers] {player.name} RETURNED ({team.name} -> {original_team.name}): {reason}")

        # --- Step 2: Process transfers out (Test nation -> associate) ---
        for team in test_nations:
            for player in list(team.players):
                reason_parts = []
                bat_avg_display = None
                ball_avg_display = None
                matches_display = None
                fmt_used = []

                last3 = self._get_last_n_seasons_stats(player, n=3)
                t = last3['Test']
                t20 = last3['T20']

                # --- Test (last 3 seasons): 20+ matches, role-based thresholds ---
                test_matches = t['matches']
                test_dismissals = t['dismissals']
                test_wickets = t['wickets']
                test_bat_avg = t['batting_average']
                test_ball_avg = t['bowling_average']
                if test_matches >= 20:
                    if self._player_has_batting_role(player) and test_dismissals >= 5 and test_bat_avg < 20:
                        reason_parts.append(f"Test bat avg (L3) {test_bat_avg} < 20 ({test_matches} Tests)")
                        fmt_used.append("Test")
                        bat_avg_display = test_bat_avg
                        matches_display = test_matches
                    if self._player_has_bowling_role(player) and test_wickets >= 10 and test_ball_avg > 50:
                        reason_parts.append(f"Test ball avg (L3) {test_ball_avg} > 50 ({test_matches} Tests)")
                        if "Test" not in fmt_used:
                            fmt_used.append("Test")
                        ball_avg_display = test_ball_avg
                        if matches_display is None:
                            matches_display = test_matches

                # --- T20 (last 3 seasons): 40+ matches, non-bowler bat avg < 15 / non-batter ball avg > 40 ---
                t20_matches = t20['matches']
                t20_bat_avg = t20['batting_average']
                t20_wickets = t20['wickets']
                t20_ball_avg = t20['bowling_average']
                if t20_matches >= 40:
                    # Not a bowler = has batting role → check bat avg < 15
                    if self._player_has_batting_role(player) and t20_matches >= 5 and t20_bat_avg < 15:
                        reason_parts.append(f"T20 bat avg {t20_bat_avg} < 15 ({t20_matches} T20s)")
                        if "T20" not in fmt_used:
                            fmt_used.append("T20")
                        if bat_avg_display is None:
                            bat_avg_display = t20_bat_avg
                        if matches_display is None:
                            matches_display = t20_matches
                    # Not a batter = has bowling role → check ball avg > 40
                    if self._player_has_bowling_role(player) and t20_wickets >= 5 and t20_ball_avg > 40:
                        reason_parts.append(f"T20 ball avg {t20_ball_avg} > 40 ({t20_matches} T20s)")
                        if "T20" not in fmt_used:
                            fmt_used.append("T20")
                        if ball_avg_display is None:
                            ball_avg_display = t20_ball_avg
                        if matches_display is None:
                            matches_display = t20_matches

                if not reason_parts:
                    continue
                # No squad limit for associates
                to_team = random.choice(associate_teams)
                try:
                    team.players.remove(player)
                except ValueError:
                    continue
                to_team.players.append(player)
                player.nationality = to_team.name
                player.original_team_name = team.name  # for possible return later
                reason = "; ".join(reason_parts)
                xfer = {
                    'player': player.name,
                    'from_team': team.name,
                    'to_team': to_team.name,
                    'reason': reason,
                    'format': ", ".join(fmt_used) if fmt_used else "Test/T20",
                    'matches': matches_display,
                    'bat_avg': bat_avg_display,
                    'ball_avg': ball_avg_display,
                    'role': player.role or '',
                    'return': False,
                }
                self.season_transfers.append(xfer)
                self._append_career_transfer_log(xfer)
                print(f"[Transfers] {player.name} ({team.name} -> {to_team.name}): {reason}")
        print(f"[Transfers] {len(self.season_transfers)} players transferred/returned this season")
    
    def process_trait_evolution(self, team, format_type):
        """
        Process trait evolution based on performance and age
        
        Trait changes:
        - Level up: Good performance + young age
        - Level down: Poor performance + old age
        - New trait: Exceptional performance
        - Remove trait: Very poor performance or age-related
        
        Returns:
            List of trait changes
        """
        from cricket_manager.systems.trait_assignment import assign_random_trait, remove_trait
        
        trait_changes = []
        players_lost_trait = set()  # Track players who already lost a trait this season
        
        for player in team.players:
            # Get player's season performance
            season_stats = player.season_stats.get(format_type, {})
            matches = season_stats.get('matches', 0)
            
            if matches < 1:
                continue  # Need minimum 1 match for trait evolution
            
            # Flat probability trait evolution per season:
            # 0% nothing, 30% level up, 30% level down, 20% remove, 20% new trait
            roll = random.random()
            
            if roll < 0.30:
                # 30% - Level up a random trait
                if player.traits:
                    upgradeable = [t for t in player.traits if isinstance(t, dict) and t.get('strength', 1) < 5]
                    if upgradeable:
                        trait = random.choice(upgradeable)
                        old_level = trait.get('strength', 1)
                        trait['strength'] = old_level + 1
                        player.add_trait_change(self.current_season, 'level_up', trait['name'], trait['strength'])
                        trait_changes.append({
                            'type': 'trait_level_up',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait['name'],
                            'old_level': old_level,
                            'new_level': trait['strength']
                        })
            
            elif roll < 0.60:
                # 30% - Level down a random trait
                if player.traits:
                    downgradeable = [t for t in player.traits if isinstance(t, dict) and t.get('strength', 1) > 1]
                    if downgradeable:
                        trait = random.choice(downgradeable)
                        old_level = trait.get('strength', 1)
                        trait['strength'] = old_level - 1
                        player.add_trait_change(self.current_season, 'level_down', trait['name'], trait['strength'])
                        trait_changes.append({
                            'type': 'trait_level_down',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait['name'],
                            'old_level': old_level,
                            'new_level': trait['strength']
                        })
            
            elif roll < 0.80:
                # 20% - Remove a random trait (only if strength is 1, max 1 loss per season)
                if player.traits and id(player) not in players_lost_trait:
                    removable = [t for t in player.traits if isinstance(t, dict) and t.get('strength', 1) <= 1]
                    if removable:
                        trait = random.choice(removable)
                        player.traits.remove(trait)
                        trait_name = trait['name'] if isinstance(trait, dict) else str(trait)
                        player.add_trait_change(self.current_season, 'lost', trait_name)
                        players_lost_trait.add(id(player))
                        trait_changes.append({
                            'type': 'trait_lost',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait_name,
                            'reason': 'season evolution'
                        })
            
            else:
                # 20% - Gain a new trait (role-appropriate from player_traits.py)
                new_trait = assign_random_trait(player)
                if new_trait:
                    player.add_trait_change(self.current_season, 'gained', new_trait['name'], new_trait['strength'])
                    trait_changes.append({
                        'type': 'trait_gained',
                        'player': player.name,
                        'team': team.name,
                        'trait': new_trait['name'],
                        'strength': new_trait['strength']
                    })
        
        # Youth negative trait evolution (separate rules)
        # These apply to ALL players who have youth negative traits (senior + U21)
        YOUTH_NEGATIVE_TRAITS = {
            # T20
            'T20_POWERPLAY_WASTER', 'T20_CANT_HIT_SIXES', 'T20_DEATH_OVERS_CHOKER',
            'T20_DOT_BALL_MAGNET', 'T20_RASH_SHOT_MERCHANT',
            'T20_DEATH_BOWLING_LIABILITY', 'T20_POWERPLAY_LEAKER', 'T20_NO_SLOWER_BALL',
            'T20_WIDE_MACHINE', 'T20_PRESSURE_CRUMBLER',
            # ODI
            'ODI_MIDDLE_OVERS_STALLER', 'ODI_SLOG_MISFIRE', 'ODI_POOR_STRIKE_ROTATION',
            'ODI_COLLAPSER', 'ODI_CHASE_BOTTLER',
            'ODI_MIDDLE_OVERS_EXPENSIVE', 'ODI_NO_WICKET_TAKER', 'ODI_DEATH_OVERS_LEAKER',
            'ODI_FIRST_SPELL_ONLY', 'ODI_PARTNERSHIP_FEEDER',
            # Test
            'TEST_NEW_BALL_BUNNY', 'TEST_POOR_CONCENTRATION', 'TEST_DAY5_CRUMBLER',
            'TEST_SECOND_INNINGS_FLOP', 'TEST_BOUNCER_VICTIM',
            'TEST_NO_STAMINA', 'TEST_FLAT_PITCH_PASSENGER', 'TEST_REVERSE_SWING_HOPELESS',
            'TEST_DAY5_TOOTHLESS', 'TEST_SPELL_BREAKER'
        }
        
        all_players = list(team.players)
        if hasattr(team, 'u21_squad'):
            all_players.extend(team.u21_squad)
        
        for player in all_players:
            if not player.traits:
                continue
            youth_neg = [t for t in player.traits if isinstance(t, dict) and t.get('name') in YOUTH_NEGATIVE_TRAITS]
            for trait in youth_neg:
                roll = random.random()
                old_level = trait.get('strength', 1)
                
                if roll < 0.50:
                    # 50% - Level down; if already at 1 and no trait lost yet, remove it
                    if old_level <= 1:
                        if id(player) not in players_lost_trait:
                            player.traits.remove(trait)
                            player.add_trait_change(self.current_season, 'lost', trait['name'])
                            players_lost_trait.add(id(player))
                            trait_changes.append({
                                'type': 'trait_lost',
                                'player': player.name,
                                'team': team.name,
                                'trait': trait['name'],
                                'reason': 'youth trait outgrown'
                            })
                    else:
                        trait['strength'] = old_level - 1
                        player.add_trait_change(self.current_season, 'level_down', trait['name'], trait['strength'])
                        trait_changes.append({
                            'type': 'trait_level_down',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait['name'],
                            'old_level': old_level,
                            'new_level': trait['strength']
                        })
                elif roll < 0.70:
                    # 20% - Level up (max 5)
                    if old_level < 5:
                        trait['strength'] = old_level + 1
                        player.add_trait_change(self.current_season, 'level_up', trait['name'], trait['strength'])
                        trait_changes.append({
                            'type': 'trait_level_up',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait['name'],
                            'old_level': old_level,
                            'new_level': trait['strength']
                        })
                else:
                    # 30% - Remove the trait only if strength is 1 and no trait lost yet
                    if old_level <= 1 and id(player) not in players_lost_trait:
                        player.traits.remove(trait)
                        player.add_trait_change(self.current_season, 'lost', trait['name'])
                        players_lost_trait.add(id(player))
                        trait_changes.append({
                            'type': 'trait_lost',
                            'player': player.name,
                            'team': team.name,
                            'trait': trait['name'],
                            'reason': 'youth trait outgrown'
                        })
        
        return trait_changes
    
    def award_season_credits(self, format_type):
        """Award credits to teams based on performance"""
        for team in self.all_teams:
            # Base credits
            team.credits += 1000
            
            # Get format stats
            stats = team.format_stats.get(format_type, {})
            wins = stats.get('wins', 0)
            
            # Bonus for wins
            team.credits += wins * 100
            
            # Tier bonus (higher tiers get more)
            tier = team.format_tiers.get(format_type, 5)
            tier_bonus = (6 - tier) * 500
            team.credits += tier_bonus
    
    def remove_duplicate_players(self):
        """Remove duplicate players from all teams - prevents training/save bugs"""
        def _dedupe_team_players(team):
            seen_names = {}
            unique_players = []
            
            for player in team.players:
                # Use player name as key (assumes names are unique identifiers)
                if player.name not in seen_names:
                    seen_names[player.name] = player
                    unique_players.append(player)
                else:
                    # Duplicate found - keep the one with more traits or higher skills
                    existing = seen_names[player.name]
                    
                    # Count traits
                    existing_traits = len(existing.traits) if hasattr(existing, 'traits') else 0
                    current_traits = len(player.traits) if hasattr(player, 'traits') else 0
                    
                    # Keep player with more traits, or higher total skill
                    if current_traits > existing_traits:
                        # Replace existing with current
                        for i, p in enumerate(unique_players):
                            if p is existing:
                                unique_players[i] = player
                                seen_names[player.name] = player
                                break
                    elif current_traits == existing_traits:
                        # Compare total skills
                        existing_total = existing.batting + existing.bowling + existing.fielding
                        current_total = player.batting + player.bowling + player.fielding
                        if current_total > existing_total:
                            for i, p in enumerate(unique_players):
                                if p is existing:
                                    unique_players[i] = player
                                    seen_names[player.name] = player
                                    break
            
            # Update team players list
            removed_count = len(team.players) - len(unique_players)
            if removed_count > 0:
                print(f"[GameEngine] Removed {removed_count} duplicate players from {team.name}")
            team.players = unique_players
        
        for team in self.all_teams:
            _dedupe_team_players(team)
        for team in getattr(self, 'domestic_teams', None) or []:
            _dedupe_team_players(team)
    
    
