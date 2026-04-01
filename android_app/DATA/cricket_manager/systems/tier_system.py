"""
Tier System - 5-tier league structure for a single format
Manages fixtures, standings, promotion, and relegation
ICC FTP-style series-based fixture generation with rotating opponents
"""

import random
import uuid
from cricket_manager.utils.constants import TIER_SIZES, TIER_NAMES

# Calendar months for scheduling
MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Match caps per team per season
MAX_T20_MATCHES = 22
MAX_ODI_MATCHES = 22
MAX_TEST_MATCHES = 12

# Series length options
SERIES_LENGTHS = {
    'T20': [3, 5],
    'ODI': [3, 5],
    'Test': [2, 3, 5],
}

# Tour format combinations (what formats a tour can include)
# Each tour between two teams picks 2-3 of these
TOUR_FORMAT_COMBOS = [
    ['T20', 'ODI'],           # White-ball tour
    ['ODI', 'Test'],          # Traditional tour
    ['T20', 'ODI', 'Test'],   # Full tour
    ['T20', 'Test'],          # Mixed tour
]

# ---- Country classifications for pitch conditions ----
SUBCONTINENT_COUNTRIES = {
    'India', 'Pakistan', 'Sri Lanka', 'Bangladesh', 'Afghanistan', 'Nepal',
    'UAE', 'Oman',
}
SENA_COUNTRIES = {
    'Australia', 'England', 'South Africa', 'New Zealand', 'West Indies',
    'Ireland', 'Zimbabwe', 'Scotland', 'Netherlands', 'Kenya', 'Namibia',
    'USA', 'Canada', 'PNG', 'Hong Kong', 'Singapore',
}

def get_pitch_conditions(host_name):
    """Return (bounce, spin, pace) ranges based on host country region.
    Subcontinent: bounce 2-5, spin 6-9, pace 2-6
    SENA:         bounce 6-10, spin 2-6, pace 6-10
    Default (neutral): balanced ranges
    """
    if host_name in SUBCONTINENT_COUNTRIES:
        return {
            'bounce': (2, 5),
            'spin': (6, 9),
            'pace': (2, 6),
            'region': 'subcontinent',
        }
    elif host_name in SENA_COUNTRIES:
        return {
            'bounce': (6, 10),
            'spin': (2, 6),
            'pace': (6, 10),
            'region': 'sena',
        }
    else:
        # Neutral / unknown
        return {
            'bounce': (4, 7),
            'spin': (4, 7),
            'pace': (4, 7),
            'region': 'neutral',
        }


class TierSystem:
    """Manage 5-tier league system for a specific format"""
    
    def __init__(self, match_format):
        self.match_format = match_format  # 'T20', 'ODI', or 'Test'
        
        # 5 tiers with different team counts
        self.tiers = {
            1: {'name': TIER_NAMES[1], 'teams': [], 'size': TIER_SIZES[1]},
            2: {'name': TIER_NAMES[2], 'teams': [], 'size': TIER_SIZES[2]},
            3: {'name': TIER_NAMES[3], 'teams': [], 'size': TIER_SIZES[3]},
            4: {'name': TIER_NAMES[4], 'teams': [], 'size': TIER_SIZES[4]},
            5: {'name': TIER_NAMES[5], 'teams': [], 'size': TIER_SIZES[5]}  # U21 teams
        }
        
        # Promotion/relegation rules
        self.promotion_slots = 2  # Top 2 teams promoted
        self.relegation_slots = 2  # Bottom 2 teams relegated
    
    def assign_teams_to_tiers(self, teams):
        """
        Assign teams to tiers based on format-specific strength
        For ALL formats, Tier 1 consists of exactly 12 teams
        Tier 5 is U21 teams for test playing nations
        
        Args:
            teams: List of Team objects
        """
        
        # Clear existing tier assignments
        for tier_num in range(1, 6):
            self.tiers[tier_num]['teams'] = []
        
        # Test nations for Tier 1 (12 teams) - same for all formats
        test_nations = [
            "India", "Australia", "England", "Pakistan", "South Africa",
            "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan",
            "Ireland", "Zimbabwe"
        ]
        
        # For ALL formats, assign Test nations to Tier 1
        tier1_teams = [t for t in teams if t.name in test_nations]
        for team in tier1_teams:
            team.format_tiers[self.match_format] = 1
            self.tiers[1]['teams'].append(team)
        
        # Remaining teams go to other tiers based on strength
        remaining_teams = [t for t in teams if t.name not in test_nations]
        team_strengths = []
        for team in remaining_teams:
            strength = self.calculate_format_strength(team)
            team_strengths.append((team, strength))
        
        # Sort by strength
        team_strengths.sort(key=lambda x: x[1], reverse=True)
        
        # Assign to tiers 2-4 (12 teams each)
        index = 0
        for tier_num in range(2, 5):
            tier_size = self.tiers[tier_num]['size']
            for i in range(tier_size):
                if index < len(team_strengths):
                    team, strength = team_strengths[index]
                    team.format_tiers[self.match_format] = tier_num
                    self.tiers[tier_num]['teams'].append(team)
                    index += 1
        
        # Tier 5: U21 teams for test playing nations
        # These are youth teams that play in their own competitive league
        for team in tier1_teams:
            # Ensure team has U21 squad
            if not hasattr(team, 'u21_squad') or not team.u21_squad:
                from cricket_manager.systems.youth_system import YouthSystem, U21_SQUAD_TARGET
                youth_system = YouthSystem()
                team.u21_squad = youth_system.generate_u21_squad(team, count=U21_SQUAD_TARGET)
            # Create a U21 team representation for Tier 5
            # The U21 team uses the same format_tiers but we track stats separately
            team.format_tiers[self.match_format] = 1  # Senior team stays in Tier 1
            # Add to Tier 5 for U21 competition
            self.tiers[5]['teams'].append(team)
        
        print(f"[Tier System] Assigned {len(tier1_teams)} teams to {self.match_format} Tier 1")
        print(f"[Tier System] Assigned {index} teams to {self.match_format} Tiers 2-4")
        print(f"[Tier System] Tier 5 (U21): {len(tier1_teams)} youth teams")
    
    def calculate_format_strength(self, team):
        """
        Calculate team strength for specific format
        
        Args:
            team: Team object
        
        Returns:
            Strength score (float)
        """
        
        if not team.players:
            return 0
        
        total_strength = 0
        
        for player in team.players:
            # Get format-specific stats
            format_stats = player.stats.get(self.match_format, {})
            
            # Weight by format
            if self.match_format == 'T20':
                # T20: Strike rate and economy matter more
                batting_strength = player.batting * 0.7
                if format_stats.get('strike_rate', 0) > 0:
                    batting_strength += format_stats['strike_rate'] * 0.3
                
                bowling_strength = player.bowling * 0.7
                if format_stats.get('economy_rate', 0) > 0:
                    bowling_strength += (10 - format_stats['economy_rate']) * 3
            
            elif self.match_format == 'ODI':
                # ODI: Balance of average and strike rate
                batting_strength = player.batting * 0.8
                if format_stats.get('batting_average', 0) > 0:
                    batting_strength += format_stats['batting_average'] * 0.2
                
                bowling_strength = player.bowling * 0.8
                if format_stats.get('wickets', 0) > 0:
                    bowling_strength += format_stats['wickets'] * 0.2
            
            else:  # Test
                # Test: Averages and consistency matter most
                batting_strength = player.batting
                if format_stats.get('batting_average', 0) > 0:
                    batting_strength += format_stats['batting_average'] * 0.5
                
                bowling_strength = player.bowling
                if format_stats.get('wickets', 0) > 0:
                    bowling_strength += format_stats['wickets'] * 0.3
            
            total_strength += batting_strength + bowling_strength + player.fielding
        
        # Average strength per player
        return total_strength / len(team.players) if team.players else 0
    
    def generate_tier_fixtures(self, tier_num):
        """
        Legacy method - generates simple round-robin fixtures.
        Now only used as fallback. Main generation uses generate_season_series().
        """
        teams = self.tiers[tier_num]['teams']
        fixtures = []
        for i, team1 in enumerate(teams):
            for j, team2 in enumerate(teams):
                if i < j:
                    fixtures.append({
                        'team1': team1,
                        'team2': team2,
                        'tier': tier_num,
                        'format': self.match_format,
                        'home_team': team1,
                        'match_type': 'league'
                    })
        return fixtures
    
    def generate_u21_fixtures(self):
        """
        Generate fixtures for Tier 5 (U21 teams)
        U21 teams play single round-robin in all formats
        
        Returns:
            List of U21 fixture dictionaries
        """
        teams = self.tiers[5]['teams']  # These are parent teams with U21 squads
        fixtures = []
        
        if not teams:
            print(f"[Fixtures] No U21 teams found for {self.match_format}")
            return fixtures
        
        # Single round-robin for U21 teams
        for i, team1 in enumerate(teams):
            for j, team2 in enumerate(teams):
                if i < j:
                    # U21 fixtures use team names with " U21" suffix
                    fixtures.append({
                        'team1': None,  # Will be resolved at match time
                        'team2': None,  # Will be resolved at match time
                        'home': f"{team1.name} U21",
                        'away': f"{team2.name} U21",
                        'home_parent': team1,
                        'away_parent': team2,
                        'tier': 5,
                        'format': self.match_format,
                        'home_team': team1,
                        'match_type': 'u21_league',
                        'is_u21': True
                    })
        
        print(f"[Fixtures] Generated {len(fixtures)} {self.match_format} U21 fixtures for Tier 5")
        return fixtures
    
    def generate_all_fixtures(self):
        """
        Legacy method - use generate_season_series() for ICC FTP-style fixtures.
        """
        all_fixtures = []
        for tier_num in range(1, 5):
            tier_fixtures = self.generate_tier_fixtures(tier_num)
            all_fixtures.extend(tier_fixtures)
        return all_fixtures
    
    def get_tier_standings(self, tier_num):
        """
        Get standings for a tier (sorted by points, then NRR)
        
        Args:
            tier_num: Tier number (1-5)
        
        Returns:
            List of teams sorted by standings
        """
        
        teams = self.tiers[tier_num]['teams']
        
        # Sort by points (descending), then NRR (descending)
        standings = sorted(
            teams,
            key=lambda t: (
                t.format_stats[self.match_format]['points'],
                t.format_stats[self.match_format]['nrr']
            ),
            reverse=True
        )
        
        # Update tier positions
        for position, team in enumerate(standings, 1):
            team.format_stats[self.match_format]['tier_position'] = position
        
        return standings
    
    def get_all_standings(self):
        """
        Get standings for all tiers
        
        Returns:
            Dictionary with tier numbers as keys and standings as values
        """
        
        all_standings = {}
        
        for tier_num in range(1, 5):  # Tiers 1-4
            all_standings[tier_num] = self.get_tier_standings(tier_num)
        
        return all_standings
    
    def process_promotion_relegation(self, all_teams):
        """
        Process promotion and relegation at season end
        
        Args:
            all_teams: List of all teams in the game
        
        Rules:
        - Tier 1: NO promotion or relegation in ANY format (closed group)
        - Tier 2: Can only RELEGATE to Tier 3, NEVER promote to Tier 1
        - Tier 3: Can promote to Tier 2, can relegate to Tier 4
        - Tier 4: Can promote to Tier 3, cannot relegate further
        
        Returns:
            Tuple of (promoted_teams, relegated_teams)
        """
        
        promoted_teams = []
        relegated_teams = []
        
        for tier_num in range(1, 5):  # Tiers 1-4
            # TIER 1: Completely locked - no promotion or relegation
            if tier_num == 1:
                print(f"[Tier System] Tier 1 {self.match_format} is locked - no promotion/relegation")
                continue
            
            # Get standings for this tier
            standings = self.get_tier_standings(tier_num)
            
            # PROMOTION: Tier 2 CANNOT promote to Tier 1 (blocked).
            # Tier 3 can promote to Tier 2, Tier 4 can promote to Tier 3.
            if tier_num >= 3 and len(standings) >= 2:
                top_2 = standings[:2]
                for team in top_2:
                    old_tier = team.format_tiers[self.match_format]
                    new_tier = tier_num - 1
                    team.format_tiers[self.match_format] = new_tier
                    team.format_stats[self.match_format]['is_promoted'] = True
                    promoted_teams.append((team, old_tier, new_tier))
                    print(f"[Promotion] {team.name} promoted from {self.match_format} Tier {old_tier} to Tier {new_tier}")
            elif tier_num == 2:
                print(f"[Tier System] Tier 2 {self.match_format} cannot promote to Tier 1 (locked)")
            
            # RELEGATION: Tier 2 can relegate to Tier 3, Tier 3 can relegate to Tier 4.
            # Tier 4 cannot relegate further.
            if tier_num < 4 and len(standings) >= 2:
                bottom_2 = standings[-2:]
                for team in bottom_2:
                    old_tier = team.format_tiers[self.match_format]
                    new_tier = tier_num + 1
                    team.format_tiers[self.match_format] = new_tier
                    team.format_stats[self.match_format]['is_relegated'] = True
                    relegated_teams.append((team, old_tier, new_tier))
                    print(f"[Relegation] {team.name} relegated from {self.match_format} Tier {old_tier} to Tier {new_tier}")
        
        # Apply skill bonuses/penalties
        self.apply_tier_changes(promoted_teams, relegated_teams)
        
        # Rebuild tier lists
        self.rebuild_tier_lists(all_teams)
        
        return promoted_teams, relegated_teams
    
    def apply_tier_changes(self, promoted_teams, relegated_teams):
        """
        Apply skill bonuses/penalties for promotion/relegation
        
        Args:
            promoted_teams: List of (team, old_tier, new_tier) tuples
            relegated_teams: List of (team, old_tier, new_tier) tuples
        """
        
        # Promoted teams get skill boost
        for team, old_tier, new_tier in promoted_teams:
            for player in team.players:
                # +5 to all skills (capped at 95)
                from cricket_manager.utils.helpers import is_batter, is_bowler, is_allrounder, is_keeper
                
                if is_batter(player.role) or is_allrounder(player.role) or is_keeper(player.role):
                    player.batting = min(95, player.batting + 5)
                if is_bowler(player.role) or is_allrounder(player.role):
                    player.bowling = min(95, player.bowling + 5)
                player.fielding = min(95, player.fielding + 2)
        
        # Relegated teams get slight penalty
        for team, old_tier, new_tier in relegated_teams:
            for player in team.players:
                # -2 to all skills (minimum 30)
                from cricket_manager.utils.helpers import is_batter, is_bowler, is_allrounder, is_keeper
                
                if is_batter(player.role) or is_allrounder(player.role) or is_keeper(player.role):
                    player.batting = max(30, player.batting - 2)
                if is_bowler(player.role) or is_allrounder(player.role):
                    player.bowling = max(30, player.bowling - 2)
                player.fielding = max(30, player.fielding - 1)
    
    def rebuild_tier_lists(self, all_teams):
        """
        Rebuild tier lists after promotion/relegation
        
        Args:
            all_teams: List of all teams in the game
        """
        
        # Clear all tier lists
        for tier_num in range(1, 5):
            self.tiers[tier_num]['teams'] = []
        
        # Rebuild based on current tier assignments
        for team in all_teams:
            tier = team.format_tiers.get(self.match_format)
            if tier and 1 <= tier <= 4:
                self.tiers[tier]['teams'].append(team)
        
        print(f"[Tier System] Rebuilt {self.match_format} tier lists")
    
    def reset_season_stats(self):
        """Reset season statistics for all teams in this format"""
        
        for tier_num in range(1, 6):
            for team in self.tiers[tier_num]['teams']:
                team.reset_season_stats(self.match_format)
    
    def get_tier_info(self, tier_num):
        """
        Get information about a tier
        
        Args:
            tier_num: Tier number (1-5)
        
        Returns:
            Dictionary with tier information
        """
        
        tier = self.tiers[tier_num]
        standings = self.get_tier_standings(tier_num)
        
        return {
            'tier_num': tier_num,
            'name': tier['name'],
            'size': tier['size'],
            'teams': tier['teams'],
            'standings': standings,
            'matches_per_team': 22 if tier_num == 1 else 11
        }
    
    def get_team_tier(self, team):
        """
        Get the tier number for a team
        
        Args:
            team: Team object
        
        Returns:
            Tier number (1-5)
        """
        
        return team.format_tiers.get(self.match_format, 1)
    
    def print_standings(self, tier_num):
        """
        Print standings for a tier (for debugging)
        
        Args:
            tier_num: Tier number (1-5)
        """
        
        standings = self.get_tier_standings(tier_num)
        
        print(f"\n{self.match_format} Tier {tier_num} - {self.tiers[tier_num]['name']}")
        print("="*70)
        print(f"{'Pos':<4} {'Team':<20} {'P':<4} {'W':<4} {'L':<4} {'D':<4} {'Pts':<5} {'NRR':<8}")
        print("-"*70)
        
        for pos, team in enumerate(standings, 1):
            stats = team.format_stats[self.match_format]
            print(f"{pos:<4} {team.name:<20} {stats['matches_played']:<4} "
                  f"{stats['wins']:<4} {stats['losses']:<4} {stats['draws']:<4} "
                  f"{stats['points']:<5} {stats['nrr']:<8.3f}")
        
        print("="*70)


def generate_season_series(all_tier_teams, opponent_history=None, wc_month=None, current_season=1):
    """
    Generate ICC FTP-style series-based fixtures for ALL tiers and ALL formats.
    
    Each team plays a rotating subset of same-tier opponents each season.
    Tours pair 2-3 formats together. Series lengths are randomized.
    Includes Tri-Nations and Quad-Nations tournaments for T20/ODI.
    Respects match caps: 22 T20, 22 ODI, 12 Test per team per season.
    World Cup month is kept free of bilateral matches.
    Pitch conditions are set based on host country (Subcontinent vs SENA).
    
    Args:
        all_tier_teams: dict {tier_num: [team_list]} for tiers 1-4
        opponent_history: dict tracking which teams played each other recently
        wc_month: int (0-11) month index reserved for World Cup, or None
        current_season: current season number for rotation tracking
    
    Returns:
        (fixtures_dict, updated_opponent_history)
        fixtures_dict = {'T20': [...], 'ODI': [...], 'Test': [...]}
    """
    if opponent_history is None:
        opponent_history = {}
    
    fixtures = {'T20': [], 'ODI': [], 'Test': []}
    
    # Track match counts per team per format
    match_counts = {}  # {team_name: {'T20': n, 'ODI': n, 'Test': n}}
    
    def get_count(team_name, fmt):
        return match_counts.get(team_name, {}).get(fmt, 0)
    
    def add_count(team_name, fmt, n):
        if team_name not in match_counts:
            match_counts[team_name] = {'T20': 0, 'ODI': 0, 'Test': 0}
        match_counts[team_name][fmt] += n
    
    def get_cap(fmt):
        if fmt == 'T20': return MAX_T20_MATCHES
        if fmt == 'ODI': return MAX_ODI_MATCHES
        if fmt == 'Test': return MAX_TEST_MATCHES
        return 22
    
    def can_add_series(team_names, fmt, length):
        """Check if ALL teams in list have room for this series under the cap."""
        cap = get_cap(fmt)
        return all(get_count(tn, fmt) + length <= cap for tn in team_names)
    
    def _make_pitch(host_name):
        """Generate concrete pitch values from host country ranges."""
        pc = get_pitch_conditions(host_name)
        return {
            'pitch_bounce': random.randint(*pc['bounce']),
            'pitch_spin': random.randint(*pc['spin']),
            'pitch_pace': random.randint(*pc['pace']),
            'pitch_region': pc['region'],
        }
    
    # Available months for bilateral series (exclude WC month)
    available_months = list(range(12))
    if wc_month is not None and 0 <= wc_month <= 11:
        available_months.remove(wc_month)
    
    # ================================================================
    # PHASE 1: Bilateral tours (same as before, strictly within tier)
    # ================================================================
    for tier_num in sorted(all_tier_teams.keys()):
        teams = all_tier_teams[tier_num]
        if len(teams) < 2:
            continue
        
        # Build all possible pairings WITHIN this tier only
        all_pairs = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                all_pairs.append((teams[i], teams[j]))
        
        # Sort pairs by how long ago they last played (prioritize stale matchups)
        def pair_priority(pair):
            key = tuple(sorted([pair[0].name, pair[1].name]))
            return opponent_history.get(key, 0)
        
        all_pairs.sort(key=pair_priority)
        
        target_opponents = min(6, len(teams) - 1)
        team_opponent_count = {t.name: 0 for t in teams}
        month_idx = 0
        selected_tours = []
        
        for team_a, team_b in all_pairs:
            if (team_opponent_count[team_a.name] >= target_opponents and
                team_opponent_count[team_b.name] >= target_opponents):
                continue
            
            combo = random.choice(TOUR_FORMAT_COMBOS)
            
            # Determine home team (alternate based on history)
            key = tuple(sorted([team_a.name, team_b.name]))
            last_host = opponent_history.get(key + ('host',), None)
            if last_host == team_a.name:
                home_team, away_team = team_b, team_a
            elif last_host == team_b.name:
                home_team, away_team = team_a, team_b
            else:
                home_team, away_team = random.choice([(team_a, team_b), (team_b, team_a)])
            
            tour_series = []
            for fmt in combo:
                length = random.choice(SERIES_LENGTHS[fmt])
                if not can_add_series([home_team.name, away_team.name], fmt, length):
                    smaller = [l for l in SERIES_LENGTHS[fmt] if l < length]
                    if smaller:
                        length = min(smaller)
                        if not can_add_series([home_team.name, away_team.name], fmt, length):
                            continue
                    else:
                        continue
                tour_series.append((fmt, length))
            
            if not tour_series:
                continue
            
            selected_tours.append((home_team, away_team, tour_series, tier_num))
            team_opponent_count[home_team.name] += 1
            team_opponent_count[away_team.name] += 1
            
            for fmt, length in tour_series:
                add_count(home_team.name, fmt, length)
                add_count(away_team.name, fmt, length)
        
        # Assign months and generate match fixtures for bilateral tours
        random.shuffle(selected_tours)
        
        for tour_idx, (home_team, away_team, tour_series, t_num) in enumerate(selected_tours):
            tour_month = available_months[month_idx % len(available_months)]
            month_idx += 1
            tour_id = str(uuid.uuid4())[:8]
            tour_name = f"{away_team.name} Tour of {home_team.name}"
            pitch = _make_pitch(home_team.name)
            day_counter = 1
            
            for fmt, length in tour_series:
                series_id = f"{tour_id}_{fmt}"
                series_name = f"{away_team.name} vs {home_team.name} - {length}-match {fmt} Series"
                
                for match_num in range(1, length + 1):
                    if fmt == 'Test':
                        match_day = min(day_counter, 28)
                        day_counter += 7
                    else:
                        match_day = min(day_counter, 28)
                        day_counter += 3
                    
                    fixture = {
                        'team1': home_team,
                        'team2': away_team,
                        'home': home_team.name,
                        'away': away_team.name,
                        'tier': t_num,
                        'format': fmt,
                        'home_team': home_team,
                        'match_type': 'series',
                        'series_id': series_id,
                        'series_name': series_name,
                        'tour_id': tour_id,
                        'tour_name': tour_name,
                        'match_number': match_num,
                        'total_matches': length,
                        'month': tour_month,
                        'month_name': MONTH_NAMES[tour_month],
                        'day': match_day,
                        'completed': False,
                        'status': 'Scheduled',
                        'winner': None,
                        'margin': '',
                        'scorecard': {},
                        'is_world_cup': False,
                        # Pitch conditions based on host country
                        'pitch_bounce': pitch['pitch_bounce'],
                        'pitch_spin': pitch['pitch_spin'],
                        'pitch_pace': pitch['pitch_pace'],
                        'pitch_region': pitch['pitch_region'],
                    }
                    fixtures[fmt].append(fixture)
                
                if day_counter > 28:
                    idx_in_tour = [s[0] for s in tour_series].index(fmt)
                    if idx_in_tour < len(tour_series) - 1:
                        month_idx += 1
                        tour_month = available_months[month_idx % len(available_months)]
                        day_counter = 1
            
            key = tuple(sorted([home_team.name, away_team.name]))
            opponent_history[key] = current_season
            opponent_history[key + ('host',)] = home_team.name
    
    # ================================================================
    # PHASE 2: Tri-Nations & Quad-Nations (T20 and ODI only)
    # ================================================================
    # Real-life format:
    #   Tri-Nations:  3 pairs x 2 matches each = 6 group + 1 Final = 7 total
    #                 Each team plays 4 group matches (+ possibly final)
    #   Quad-Nations: 6 pairs x 1 match each = 6 group + 2 Semis + 1 Final = 9 total
    #                 Each team plays 3 group matches (+ possibly semi/final)
    for tier_num in sorted(all_tier_teams.keys()):
        teams = list(all_tier_teams[tier_num])
        if len(teams) < 3:
            continue
        
        random.shuffle(teams)
        
        multi_events_scheduled = 0
        max_multi_events = 2 if len(teams) >= 6 else 1
        team_pool = list(teams)
        
        while multi_events_scheduled < max_multi_events and len(team_pool) >= 3:
            if len(team_pool) >= 4 and random.random() < 0.4:
                n_teams = 4
                event_type = 'Quad-Nations'
                matches_per_team = 3   # 3 group matches per team
            else:
                n_teams = 3
                event_type = 'Tri-Nations'
                matches_per_team = 4   # 4 group matches per team (play each opponent twice)
            
            fmt = random.choice(['T20', 'ODI'])
            
            eligible = [t for t in team_pool
                        if get_count(t.name, fmt) + matches_per_team <= get_cap(fmt)]
            
            if len(eligible) < n_teams:
                break
            
            selected = eligible[:n_teams]
            for t in selected:
                if t in team_pool:
                    team_pool.remove(t)
            
            host = selected[0]
            pitch = _make_pitch(host.name)
            
            tour_month = available_months[random.randint(0, len(available_months) - 1)]
            tour_id = str(uuid.uuid4())[:8]
            series_id = f"{tour_id}_{fmt}"
            team_names_str = ' / '.join(t.name for t in selected)
            series_name = f"{event_type} {fmt} Series ({team_names_str})"
            tour_name = f"{event_type} in {host.name}"
            
            day_counter = 1
            match_num = 0
            
            match_type_tag = event_type.lower().replace('-', '_')
            
            def _add_fixture(t1, t2, mnum, total, rnd='Group'):
                nonlocal day_counter
                match_day = min(day_counter, 28)
                day_counter += 3
                fixture = {
                    'team1': t1,
                    'team2': t2,
                    'home': t1.name,
                    'away': t2.name,
                    'tier': tier_num,
                    'format': fmt,
                    'home_team': host,
                    'match_type': match_type_tag,
                    'series_id': series_id,
                    'series_name': series_name,
                    'tour_id': tour_id,
                    'tour_name': tour_name,
                    'match_number': mnum,
                    'total_matches': total,
                    'round': rnd,
                    'month': tour_month,
                    'month_name': MONTH_NAMES[tour_month],
                    'day': match_day,
                    'completed': False,
                    'status': 'Scheduled',
                    'winner': None,
                    'margin': '',
                    'scorecard': {},
                    'is_world_cup': False,
                    'pitch_bounce': pitch['pitch_bounce'],
                    'pitch_spin': pitch['pitch_spin'],
                    'pitch_pace': pitch['pitch_pace'],
                    'pitch_region': pitch['pitch_region'],
                }
                fixtures[fmt].append(fixture)
            
            if event_type == 'Tri-Nations':
                # 3 pairs x 2 = 6 group matches + 1 Final = 7 total
                total_matches = 7
                for leg in range(2):
                    for i in range(len(selected)):
                        for j in range(i + 1, len(selected)):
                            match_num += 1
                            _add_fixture(selected[i], selected[j], match_num, total_matches, 'Group')
                # Final (TBD teams — top 2 from group stage)
                match_num += 1
                _add_fixture(selected[0], selected[1], match_num, total_matches, 'Final')
                # Mark final as needing team update from group standings
                fixtures[fmt][-1]['needs_team_update'] = True
                fixtures[fmt][-1]['multi_nation_type'] = 'tri_nations'
                fixtures[fmt][-1]['multi_nation_teams'] = [t.name for t in selected]
                # Each team plays 4 group matches
                for t in selected:
                    add_count(t.name, fmt, matches_per_team)
            
            else:  # Quad-Nations
                # 6 pairs x 1 = 6 group matches + 1 Final = 7 total
                total_matches = 7
                for i in range(len(selected)):
                    for j in range(i + 1, len(selected)):
                        match_num += 1
                        _add_fixture(selected[i], selected[j], match_num, total_matches, 'Group')
                # Final (top 2 from group stage)
                match_num += 1
                _add_fixture(selected[0], selected[1], match_num, total_matches, 'Final')
                # Mark final as needing team update from group standings
                fixtures[fmt][-1]['needs_team_update'] = True
                fixtures[fmt][-1]['multi_nation_type'] = 'quad_nations'
                fixtures[fmt][-1]['multi_nation_teams'] = [t.name for t in selected]
                # Each team plays 3 group matches
                for t in selected:
                    add_count(t.name, fmt, matches_per_team)
            
            multi_events_scheduled += 1
    
    # ================================================================
    # Sort fixtures within each format by month then day
    # ================================================================
    for fmt in fixtures:
        fixtures[fmt].sort(key=lambda f: (f.get('month', 0), f.get('day', 1)))
    
    # ================================================================
    # Ensure no team has 2 matches on the same date (spread clashes)
    # ================================================================
    resolve_team_day_clashes(fixtures)
    
    # Print summary
    for fmt in ['T20', 'ODI', 'Test']:
        print(f"[Series Fixtures] Generated {len(fixtures[fmt])} {fmt} matches")
    
    return fixtures, opponent_history


def _days_in_month(month_idx):
    """Return number of days in month (0-11)."""
    if month_idx in (0, 2, 4, 6, 7, 9, 11):
        return 31
    if month_idx in (3, 5, 8, 10):
        return 30
    return 28  # February (no leap-year logic for simplicity)


# ICC FTP: allow 2–4 matches per day across the calendar (1395 matches / 365 days)
MAX_MATCHES_PER_DAY = 4
# Test matches span 5 consecutive days; both teams are unavailable for any other match on those days
TEST_MATCH_DAYS = 5


def _team_names_for_fixture(f):
    """Return (home_name, away_name) for a fixture; normalised and stripped."""
    home = f.get('home') or (f.get('team1').name if hasattr(f.get('team1'), 'name') else '')
    away = f.get('away') or (f.get('team2').name if hasattr(f.get('team2'), 'name') else '')
    if not home and f.get('team1'):
        home = getattr(f['team1'], 'name', '')
    if not away and f.get('team2'):
        away = getattr(f['team2'], 'name', '')
    return (str(home).strip() if home else '', str(away).strip() if away else '')


def _test_match_block(m, start_d):
    """Return list of (month, day) covered by a Test starting on (m, start_d) over TEST_MATCH_DAYS days."""
    block = []
    mm, dd = m, start_d
    for _ in range(TEST_MATCH_DAYS):
        max_d = _days_in_month(mm)
        if dd <= max_d:
            block.append((mm, dd))
        dd += 1
        if dd > max_d:
            dd = 1
            mm = (mm + 1) % 12
    return block


def resolve_team_day_clashes(fixtures):
    """
    ICC FTP: Reschedule so (1) no team plays twice on the same day,
    (2) at most MAX_MATCHES_PER_DAY matches start on any day,
    (3) Test matches reserve 5 consecutive days for both teams (no other match for them in that block).
    Does NOT remove any fixture – same number of matches per season.
    """
    total_before = sum(len(fixtures.get(fmt, [])) for fmt in ('T20', 'ODI', 'Test'))
    all_f = []
    for fmt in ('T20', 'ODI', 'Test'):
        for f in fixtures.get(fmt, []):
            m, d = f.get('month', 0), f.get('day', 1)
            if m < 0:
                continue
            all_f.append((m, d, f))
    
    all_f.sort(key=lambda x: (x[0], x[1], x[2].get('match_number', 0)))
    
    occupied = {}
    match_count = {}
    
    def get_occupied(m, d):
        if m not in occupied:
            occupied[m] = {}
        return occupied[m].setdefault(d, set())
    
    def set_occupied(m, d, team_names):
        if m not in occupied:
            occupied[m] = {}
        occupied[m][d] = set(team_names)
    
    def get_count(m, d):
        if m not in match_count:
            match_count[m] = {}
        return match_count[m].get(d, 0)
    
    def inc_count(m, d):
        if m not in match_count:
            match_count[m] = {}
        match_count[m][d] = match_count[m].get(d, 0) + 1
    
    def team_free_on_block(team_a, team_b, block):
        for m, d in block:
            occ = get_occupied(m, d)
            if team_a in occ or team_b in occ:
                return False
        return True
    
    def next_free_day(m, d, team_a, team_b, is_test, steps_left=400):
        if steps_left <= 0:
            return (m, min(d, _days_in_month(m)))
        max_d = _days_in_month(m)
        while d <= max_d:
            if is_test:
                block = _test_match_block(m, d)
                if not team_free_on_block(team_a, team_b, block):
                    d += 1
                    continue
                start_cnt = get_count(m, d)
                if start_cnt >= MAX_MATCHES_PER_DAY:
                    d += 1
                    continue
                return (m, d)
            else:
                occ = get_occupied(m, d)
                cnt = get_count(m, d)
                if (team_a not in occ and team_b not in occ and cnt < MAX_MATCHES_PER_DAY):
                    return (m, d)
            d += 1
        m2 = (m + 1) % 12
        return next_free_day(m2, 1, team_a, team_b, is_test, steps_left - 1)
    
    for m, d, f in all_f:
        home, away = _team_names_for_fixture(f)
        if not home or not away:
            continue
        is_test = (f.get('format') == 'Test')
        if is_test:
            block = _test_match_block(m, d)
            clash = not team_free_on_block(home, away, block)
        else:
            occ = get_occupied(m, d)
            clash = home in occ or away in occ
        cnt = get_count(m, d)
        over_cap = cnt >= MAX_MATCHES_PER_DAY
        if clash or over_cap:
            new_m, new_d = next_free_day(m, d, home, away, is_test)
            f['day'] = new_d
            f['month'] = new_m
            f['month_name'] = MONTH_NAMES[new_m] if 0 <= new_m <= 11 else f.get('month_name', '')
            m, d = new_m, new_d
        if is_test:
            block = _test_match_block(m, d)
            for (mm, dd) in block:
                occ = get_occupied(mm, dd)
                occ.add(home)
                occ.add(away)
                set_occupied(mm, dd, occ)
        else:
            occ = get_occupied(m, d)
            occ.add(home)
            occ.add(away)
            set_occupied(m, d, occ)
        inc_count(m, d)
    
    for fmt in fixtures:
        fixtures[fmt].sort(key=lambda f: (f.get('month', 0), f.get('day', 1)))
    
    total_after = sum(len(fixtures.get(fmt, [])) for fmt in ('T20', 'ODI', 'Test'))
    if total_before != total_after:
        raise AssertionError(
            f"[TierSystem] resolve_team_day_clashes must not change fixture count: "
            f"before={total_before} after={total_after}"
        )
