"""
Youth Development System - Generate and manage U21 players
"""

import random
from cricket_manager.core.player import Player
from cricket_manager.systems.trait_assignment import assign_traits_to_player, get_trait_pool_for_player, get_trait_strength
from cricket_manager.utils.constants import MAX_SQUAD_SIZE

# Every international team keeps this many U21 players (enough for U21 XI + rotation).
U21_SQUAD_TARGET = 20

# Fixed 20-role balance: batters, keepers, allrounders, bowlers — used for new games and yearly top-ups.
U21_BALANCED_ROLES_20 = [
    'Opening Batter', 'Opening Batter',
    'Middle Order Batter', 'Middle Order Batter', 'Middle Order Batter',
    'Lower Order Batter', 'Lower Order Batter',
    'Wicketkeeper Batter', 'Wicketkeeper Batter',
    'Batting Allrounder (Medium Pace)', 'Batting Allrounder (Fast Medium)',
    'Bowling Allrounder (Finger Spin)', 'Bowling Allrounder (Fast Medium)',
    'Genuine Allrounder (Fast Medium)',
    'Fast Bowler', 'Fast Medium Pacer', 'Medium Pacer', 'Medium Pacer',
    'Finger Spinner', 'Wrist Spinner',
]

# Youth-specific negative traits - format-specific (30 total: 10 per format)
YOUTH_T20_BATTING_TRAITS = [
    'T20_POWERPLAY_WASTER', 'T20_CANT_HIT_SIXES', 'T20_DEATH_OVERS_CHOKER',
    'T20_DOT_BALL_MAGNET', 'T20_RASH_SHOT_MERCHANT'
]
YOUTH_T20_BOWLING_TRAITS = [
    'T20_DEATH_BOWLING_LIABILITY', 'T20_POWERPLAY_LEAKER', 'T20_NO_SLOWER_BALL',
    'T20_WIDE_MACHINE', 'T20_PRESSURE_CRUMBLER'
]
YOUTH_ODI_BATTING_TRAITS = [
    'ODI_MIDDLE_OVERS_STALLER', 'ODI_SLOG_MISFIRE', 'ODI_POOR_STRIKE_ROTATION',
    'ODI_COLLAPSER', 'ODI_CHASE_BOTTLER'
]
YOUTH_ODI_BOWLING_TRAITS = [
    'ODI_MIDDLE_OVERS_EXPENSIVE', 'ODI_NO_WICKET_TAKER', 'ODI_DEATH_OVERS_LEAKER',
    'ODI_FIRST_SPELL_ONLY', 'ODI_PARTNERSHIP_FEEDER'
]
YOUTH_TEST_BATTING_TRAITS = [
    'TEST_NEW_BALL_BUNNY', 'TEST_POOR_CONCENTRATION', 'TEST_DAY5_CRUMBLER',
    'TEST_SECOND_INNINGS_FLOP', 'TEST_BOUNCER_VICTIM'
]
YOUTH_TEST_BOWLING_TRAITS = [
    'TEST_NO_STAMINA', 'TEST_FLAT_PITCH_PASSENGER', 'TEST_REVERSE_SWING_HOPELESS',
    'TEST_DAY5_TOOTHLESS', 'TEST_SPELL_BREAKER'
]
# Combined pools for convenience
YOUTH_NEGATIVE_BATTING_TRAITS = YOUTH_T20_BATTING_TRAITS + YOUTH_ODI_BATTING_TRAITS + YOUTH_TEST_BATTING_TRAITS
YOUTH_NEGATIVE_BOWLING_TRAITS = YOUTH_T20_BOWLING_TRAITS + YOUTH_ODI_BOWLING_TRAITS + YOUTH_TEST_BOWLING_TRAITS


class YouthSystem:
    """Manage youth player development and promotion"""
    
    def __init__(self):
        # Promotion thresholds (17+ only for senior national or domestic moves from U21 pipeline)
        self.min_age_for_promotion = 17
        self.min_skill_for_promotion = 50  # Lowered from 60 to allow more promotions
        self.max_age_for_u21 = 22  # Players stay until they turn 22
    
    def generate_u21_squad(self, team, count=None):
        """
        Generate U21 squad for a team with TIER-BASED skill caps
        
        Gamer 2024 Style - Youth skills depend on parent team tier:
        - Tier 1 parent: Youth primary 25-50, secondary 12-30
        - Tier 2 parent: Youth primary 22-45, secondary 10-28
        - Tier 3 parent: Youth primary 20-40, secondary 8-25
        - Tier 4 parent: Youth primary 18-35, secondary 6-22
        
        Args:
            team: Parent team
            count: Number of youth players (default U21_SQUAD_TARGET)
        
        Returns:
            List of youth players
        """
        u21_players = []
        if count is None:
            count = U21_SQUAD_TARGET
        
        # Get parent team tier
        parent_tier = getattr(team, 'tier', 3)
        
        # Tier-based skill ranges for youth
        youth_skill_ranges = {
            1: {'primary': (50, 67), 'secondary': (15, 30), 'fielding': (40, 60)},  # Test nations U21
            2: {'primary': (40, 58), 'secondary': (12, 28), 'fielding': (35, 52)},
            3: {'primary': (35, 50), 'secondary': (10, 25), 'fielding': (30, 45)},
            4: {'primary': (30, 45), 'secondary': (8, 22), 'fielding': (25, 40)},
            5: {'primary': (25, 40), 'secondary': (6, 20), 'fielding': (20, 35)}
        }
        
        ranges = youth_skill_ranges.get(parent_tier, youth_skill_ranges[3])
        primary_min, primary_max = ranges['primary']
        secondary_min, secondary_max = ranges['secondary']
        fielding_min, fielding_max = ranges['fielding']
        
        # Role distribution: repeat balanced template if count > 20
        roles_this_squad = []
        template = list(U21_BALANCED_ROLES_20)
        while len(roles_this_squad) < count:
            random.shuffle(template)
            roles_this_squad.extend(template)
        roles_this_squad = roles_this_squad[:count]
        
        for i in range(count):
            role = roles_this_squad[i]
            name = self.generate_youth_name(team.name)
            age = random.randint(16, 21)
            
            player = Player(name, age, role, team.name)
            player.is_youth_player = True
            
            # Age-based skill adjustment for youth
            age_bonus = (age - 16) * 2  # 0-10 bonus based on age
            
            # Calculate skill caps with age bonus
            adj_primary_max = min(primary_max + age_bonus, primary_max + 10)
            adj_fielding_max = min(fielding_max + age_bonus // 2, fielding_max + 5)
            
            # Assign skills based on role type (same rules as main generation)
            if role in ['Opening Batter', 'Middle Order Batter', 'Lower Order Batter', 'Wicketkeeper Batter']:
                # Pure batsmen: bowling max 25
                player.batting = random.randint(primary_min, adj_primary_max)
                player.bowling = random.randint(5, 25)
                
            elif role in ['Finger Spinner', 'Wrist Spinner', 'Medium Pacer', 'Fast Medium Pacer', 'Fast Bowler']:
                # Pure bowlers: batting max 30
                player.batting = random.randint(8, 30)
                player.bowling = random.randint(primary_min, adj_primary_max)
                
            elif 'Batting Allrounder' in role:
                # Batting allrounder: batting 20 points higher than bowling
                player.batting = random.randint(primary_min, adj_primary_max)
                player.bowling = max(10, player.batting - 20 + random.randint(-3, 3))
                
            elif 'Bowling Allrounder' in role:
                # Bowling allrounder: bowling 20 points higher than batting
                player.bowling = random.randint(primary_min, adj_primary_max)
                player.batting = max(10, player.bowling - 20 + random.randint(-3, 3))
                
            elif 'Genuine Allrounder' in role:
                # Genuine allrounder: both skills within 10 points of each other
                base_skill = random.randint(primary_min, max(primary_min, adj_primary_max - 5))
                player.batting = base_skill + random.randint(-5, 5)
                player.bowling = base_skill + random.randint(-5, 5)
            
            player.fielding = random.randint(fielding_min, adj_fielding_max)
            
            # Potential based on parent tier (higher tier = higher potential ceiling)
            potential_ranges = {
                1: (70, 95), 2: (65, 90), 3: (60, 85), 4: (55, 80), 5: (50, 75)
            }
            pot_min, pot_max = potential_ranges.get(parent_tier, (60, 85))
            player.potential = random.randint(pot_min, pot_max)
            
            # Form for youth
            player.form = random.randint(45, 75)
            
            # Generate bowling movements for bowlers
            if player.bowling > 40:
                from cricket_manager.systems.bowling_movements import generate_bowling_movements
                player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
            
            # Initialize pace speeds for bowlers (age-based)
            if player.bowling > 40:
                from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                initialize_pace_speeds(player)
            
                        
            # Assign 2-5 traits: at least 1 positive + 1 negative, rest random
            self._assign_youth_traits(player)
            
            u21_players.append(player)
        
        print(f"[Youth] Generated {len(u21_players)} youth players for {team.name} (Tier {parent_tier})")
        return u21_players
    
    def generate_youth_name(self, team_name):
        """Generate a youth player name using regional name database from gamer 2024"""
        from cricket_manager.utils.name_generator import generate_player_name
        return generate_player_name(team_name, ensure_unique=True)
    
    def calculate_performance_score(self, player, match_format='T20'):
        """
        Calculate youth player performance score for promotion consideration
        
        Higher score = better performance
        """
        season_stats = player.season_stats.get(match_format, {})
        career_stats = player.stats.get(match_format, {})
        
        # Get stats
        runs = season_stats.get('runs', 0)
        wickets = season_stats.get('wickets', 0)
        matches = season_stats.get('matches', 0)
        
        if matches == 0:
            return 0  # No matches played
        
        # Calculate batting score
        batting_average = career_stats.get('batting_average', 0)
        batting_score = runs + (batting_average * 10)
        
        # Calculate bowling score
        bowling_average = career_stats.get('bowling_average', 0)
        bowling_score = (wickets * 20)
        if bowling_average > 0:
            bowling_score += max(0, 50 - bowling_average)
        
        # Role-based weighting
        if 'Batter' in player.role or 'Wicketkeeper' in player.role:
            total_score = (batting_score * 0.8) + (bowling_score * 0.2)
        elif 'Bowler' in player.role or 'Pacer' in player.role or 'Spinner' in player.role:
            total_score = (batting_score * 0.2) + (bowling_score * 0.8)
        else:  # All-rounder
            total_score = (batting_score * 0.5) + (bowling_score * 0.5)
        
        # Age bonus (younger players get bonus for same performance)
        age_bonus = max(0, (23 - player.age) * 5)
        
        # Potential bonus
        potential_bonus = (player.potential - 70) * 2
        
        return total_score + age_bonus + potential_bonus
    
    def is_eligible_for_promotion(self, player, match_format='T20'):
        """
        Check if youth player is eligible for promotion to senior team
        
        Criteria:
        - Age >= 17 (younger players stay in U21 until they turn 17)
        - Batting or bowling skill above min_skill_for_promotion
        
        Returns:
            (bool, str): (is_eligible, reason)
        """
        # Age check
        if player.age < self.min_age_for_promotion:
            return False, f"Too young (minimum age {self.min_age_for_promotion})"
        
        # Skill check - either batting or bowling must be > 50
        if player.batting > self.min_skill_for_promotion:
            return True, f"Eligible (Batting: {player.batting})"
        
        if player.bowling > self.min_skill_for_promotion:
            return True, f"Eligible (Bowling: {player.bowling})"
        
        return False, f"Skills too low (BAT: {player.batting}, BOWL: {player.bowling}, need >{self.min_skill_for_promotion})"
    
    def promote_youth_players(self, team, match_format='T20', max_promotions=3):
        """
        Promote best youth players to senior team
        
        Args:
            team: Team object
            match_format: Format to evaluate performance in
            max_promotions: Maximum number of promotions (default 3)
        
        Returns:
            List of promoted players
        """
        if not hasattr(team, 'u21_squad') or not team.u21_squad:
            return []
        
        # Get eligible players
        eligible_players = []
        for player in team.u21_squad:
            is_eligible, reason = self.is_eligible_for_promotion(player, match_format)
            if is_eligible:
                score = self.calculate_performance_score(player, match_format)
                eligible_players.append((player, score))
                print(f"[Youth] {team.name}: {player.name} eligible - BAT:{player.batting} BOWL:{player.bowling} Score:{score:.1f}")
        
        if not eligible_players:
            print(f"[Youth] {team.name}: No eligible youth players for promotion")
            return []
        
        # Sort by performance score (highest first)
        eligible_players.sort(key=lambda x: x[1], reverse=True)
        
        # Promote top players (up to max_promotions); must be 17+ (is_eligible enforces this)
        num_promotions = min(max_promotions, len(eligible_players))
        promoted = []
        
        for i in range(num_promotions):
            player, score = eligible_players[i]
            
            # Check if senior squad has space
            if len(team.players) >= MAX_SQUAD_SIZE:
                print(f"[Youth] Cannot promote {player.name} - senior squad full ({len(team.players)}/{MAX_SQUAD_SIZE})")
                break
            
            # Remove from U21 squad
            team.u21_squad.remove(player)
            
            # Snapshot U21 stats (frozen for profile) and reset senior career stats
            player.snapshot_u21_and_reset_senior_career()
            # Add to senior team
            player.is_youth_player = False
            team.add_player(player)
            
            promoted.append(player)
            
            print(f"[Youth] Promoted {player.name} ({player.role}, Age {player.age}, BAT:{player.batting}, BOWL:{player.bowling}) to {team.name} senior team")
        
        return promoted
    
    def age_youth_players(self, team, game_engine=None, associate_teams=None):
        """
        Age youth players and handle those who reach age 22
        
        Players who turn 22:
        - Top 1-3 players (by performance score) are promoted to senior team
        - Remaining players are placed on a domestic club in their country first; if none fit,
          they transfer to an international associate nation as before.
        
        Args:
            team: Team with U21 squad
            game_engine: GameEngine (used to find domestic_teams by parent_nation)
            associate_teams: List of associate teams (Tier 2-4) for fallback transfers
        
        Returns:
            Tuple of (promoted_to_senior, transferred) — each transfer dict may include 'to_domestic': True
        """
        if not hasattr(team, 'u21_squad'):
            return [], []
        
        promoted = []
        transferred = []
        aged_out_players = []
        
        # Note: Players are already aged once for the year by GameEngine.age_all_players() before this runs
        # This function only handles players who have reached age 22
        for player in team.u21_squad[:]:  # Copy list to modify during iteration
            # Collect players who have reached age 22
            if player.age >= self.max_age_for_u21:
                aged_out_players.append(player)
        
        if not aged_out_players:
            return [], []
        
        # Calculate performance scores for aged-out players
        scored_players = []
        for player in aged_out_players:
            score = self.calculate_performance_score(player)
            # Also factor in skills directly
            skill_score = max(player.batting, player.bowling) + (player.fielding * 0.3)
            total_score = score + skill_score
            scored_players.append((player, total_score))
        
        # Sort by score (highest first)
        scored_players.sort(key=lambda x: x[1], reverse=True)
        
        # Determine how many to promote (1-3 based on available senior squad space)
        senior_space = max(0, MAX_SQUAD_SIZE - len(team.players))
        num_to_promote = max(
            0,
            min(random.randint(1, 3), len(scored_players), senior_space),
        )
        
        # Promote top 1-3 aged-out players to senior team (they are already max_age_for_u21+)
        for player, score in scored_players[:num_to_promote]:
            
            # Remove from U21 squad (defensive check in case squad changed elsewhere)
            if player in team.u21_squad:
                team.u21_squad.remove(player)
            
            # Snapshot U21 stats and reset senior career
            player.snapshot_u21_and_reset_senior_career()
            # Promote to senior team
            player.is_youth_player = False
            team.add_player(player)
            promoted.append(player)
            
            print(f"[Youth] PROMOTED: {player.name} ({player.role}, Age {player.age}, BAT:{player.batting}, BOWL:{player.bowling}) to {team.name} senior team")
        
        # Transfer remaining aged-out players: domestic club first, then associate nation
        for player, score in scored_players[num_to_promote:]:
            
            # Remove from U21 squad (defensive check as above)
            if player in team.u21_squad:
                team.u21_squad.remove(player)
            
            placed = False
            if game_engine is not None:
                domestic_candidates = [
                    t for t in (getattr(game_engine, 'domestic_teams', None) or [])
                    if getattr(t, 'parent_nation', None) == team.name
                ]
                random.shuffle(domestic_candidates)
                for dt in domestic_candidates:
                    if len(dt.players) < MAX_SQUAD_SIZE:
                        player.snapshot_u21_and_reset_senior_career()
                        player.is_youth_player = False
                        player.nationality = team.name
                        dt.add_player(player)
                        transferred.append({
                            'player': player,
                            'from_team': team.name,
                            'to_team': dt.name,
                            'to_domestic': True,
                        })
                        print(f"[Youth] TRANSFERRED (domestic): {player.name} from {team.name} U21 to {dt.name} at age {player.age}")
                        placed = True
                        break
            
            if placed:
                continue
            
            if associate_teams and len(associate_teams) > 0:
                available_teams = [t for t in associate_teams if len(t.players) < MAX_SQUAD_SIZE]
                
                if available_teams:
                    target_team = random.choice(available_teams)
                    
                    player.snapshot_u21_and_reset_senior_career()
                    player.is_youth_player = False
                    player.nationality = target_team.name
                    
                    target_team.add_player(player)
                    transferred.append({
                        'player': player,
                        'from_team': team.name,
                        'to_team': target_team.name,
                        'to_domestic': False,
                    })
                    print(f"[Youth] TRANSFERRED (associate): {player.name} from {team.name} U21 to {target_team.name} at age {player.age}")
                else:
                    print(f"[Youth] {player.name} aged out - no domestic or associate squad space, player retired")
            else:
                print(f"[Youth] {player.name} aged out - no domestic placement and no associate teams, player retired")
        
        return promoted, transferred
    
    def ensure_u21_squad_strength(self, team, target=None):
        """
        Top up U21 to `target` players after exits/promotions so squads never sit at 0.
        Uses the same balanced role template as generate_u21_squad.
        """
        if target is None:
            target = U21_SQUAD_TARGET
        if not hasattr(team, 'u21_squad') or team.u21_squad is None:
            team.u21_squad = []
        need = target - len(team.u21_squad)
        if need <= 0:
            return []
        added = self.replace_aged_out_players(team, need)
        print(f"[Youth] {team.name}: U21 squad {len(team.u21_squad)}/{target} after top-up (+{len(added)})")
        return added
    
    def replace_aged_out_players(self, team, num_to_replace):
        """
        Generate new youth players to replace those who aged out
        Ensures proper role balance by checking what roles are missing
        
        Args:
            team: Team object
            num_to_replace: Number of players to generate
        
        Returns:
            List of new players
        """
        if num_to_replace <= 0:
            return []
        
        new_players = []
        
        # Get parent team tier
        parent_tier = getattr(team, 'tier', 1)
        
        # Tier-based skill ranges for youth
        youth_skill_ranges = {
            1: {'primary': (50, 67), 'secondary': (15, 30), 'fielding': (40, 60)},
            2: {'primary': (40, 58), 'secondary': (12, 28), 'fielding': (35, 52)},
            3: {'primary': (35, 50), 'secondary': (10, 25), 'fielding': (30, 45)},
            4: {'primary': (30, 45), 'secondary': (8, 22), 'fielding': (25, 40)},
            5: {'primary': (25, 40), 'secondary': (6, 20), 'fielding': (20, 35)}
        }
        
        ranges = youth_skill_ranges.get(parent_tier, youth_skill_ranges[1])
        primary_min, primary_max = ranges['primary']
        fielding_min, fielding_max = ranges['fielding']
        
        # Same balanced template as new-game U21 (shuffled chunks) for playable XIs
        template = list(U21_BALANCED_ROLES_20)
        roles_to_add = []
        while len(roles_to_add) < num_to_replace:
            random.shuffle(template)
            roles_to_add.extend(template)
        roles_to_add = roles_to_add[:num_to_replace]
        
        for role in roles_to_add:
            name = self.generate_youth_name(team.name)
            # Academy intakes: stay under 17 until annual aging; promotion to senior/domestic only at 17+
            age = random.randint(15, 16)
            
            player = Player(name, age, role, team.name)
            player.is_youth_player = True
            
            # Age-based skill adjustment
            age_bonus = max(0, (age - 15) * 2)
            adj_primary_max = min(primary_max + age_bonus, primary_max + 8)
            
            # Generate skills based on role
            if role in ['Opening Batter', 'Middle Order Batter', 'Lower Order Batter', 'Wicketkeeper Batter']:
                player.batting = random.randint(primary_min, adj_primary_max)
                player.bowling = random.randint(5, 25)
            elif role in ['Finger Spinner', 'Wrist Spinner', 'Medium Pacer', 'Fast Medium Pacer', 'Fast Bowler']:
                player.batting = random.randint(8, 30)
                player.bowling = random.randint(primary_min, adj_primary_max)
            elif 'Batting Allrounder' in role:
                player.batting = random.randint(primary_min, adj_primary_max)
                player.bowling = max(10, player.batting - 20 + random.randint(-3, 3))
            elif 'Bowling Allrounder' in role:
                player.bowling = random.randint(primary_min, adj_primary_max)
                player.batting = max(10, player.bowling - 20 + random.randint(-3, 3))
            elif 'Genuine Allrounder' in role:
                base_skill = random.randint(primary_min, max(primary_min, adj_primary_max - 5))
                player.batting = base_skill + random.randint(-5, 5)
                player.bowling = base_skill + random.randint(-5, 5)
            else:
                player.batting = random.randint(primary_min, adj_primary_max)
                player.bowling = random.randint(primary_min, adj_primary_max)
            
            player.fielding = random.randint(fielding_min, fielding_max)
            player.potential = random.randint(70, 95)
            player.form = random.randint(50, 80)
            
            # Generate bowling movements for bowlers
            if player.bowling > 40:
                from cricket_manager.systems.bowling_movements import generate_bowling_movements
                player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
            
            # Initialize pace speeds for bowlers (age-based)
            if player.bowling > 40:
                from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                initialize_pace_speeds(player)
            
                        
            # Assign 2-5 traits: at least 1 positive + 1 negative, rest random
            self._assign_youth_traits(player)
            
            team.u21_squad.append(player)
            new_players.append(player)
        
        print(f"[Youth] Generated {len(new_players)} new youth players for {team.name}")
        return new_players
    
    def _assign_youth_traits(self, player):
        """
        Assign 2-5 total traits to a youth/U21 player.
        Guarantees at least 1 positive trait and 1 negative trait.
        Remaining slots filled randomly from either pool.
        Negative traits are drawn from the format-specific youth pools.
        """
        from cricket_manager.utils.helpers import is_batter, is_bowler, is_allrounder, is_keeper
        
        # Start fresh
        player.traits = []
        
        total_traits = random.randint(2, 5)
        
        # --- Build negative pool (format-specific youth traits) ---
        neg_pool = []
        if is_batter(player.role) or is_keeper(player.role) or is_allrounder(player.role):
            neg_pool.extend(YOUTH_NEGATIVE_BATTING_TRAITS)
        if is_bowler(player.role) or is_allrounder(player.role):
            neg_pool.extend(YOUTH_NEGATIVE_BOWLING_TRAITS)
        if not neg_pool:
            neg_pool = YOUTH_NEGATIVE_BATTING_TRAITS + YOUTH_NEGATIVE_BOWLING_TRAITS
        random.shuffle(neg_pool)
        
        # --- Build positive pool (role-appropriate from trait_assignment) ---
        pos_pool = get_trait_pool_for_player(player, positive=True, tier=5)
        random.shuffle(pos_pool)
        
        assigned = set()
        
        # Step 1: Guarantee at least 1 negative trait
        for t in neg_pool:
            if t not in assigned:
                strength = random.randint(1, 3)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
                break
        
        # Step 2: Guarantee at least 1 positive trait
        for t in pos_pool:
            if t not in assigned:
                strength = get_trait_strength(player, t, tier=5)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
                break
        
        # Step 3: Fill remaining slots randomly from both pools
        remaining = total_traits - len(player.traits)
        combined_pool = [t for t in (neg_pool + pos_pool) if t not in assigned]
        random.shuffle(combined_pool)
        
        for t in combined_pool:
            if remaining <= 0:
                break
            if t not in assigned:
                # Determine if positive or negative for strength calc
                if t in YOUTH_NEGATIVE_BATTING_TRAITS or t in YOUTH_NEGATIVE_BOWLING_TRAITS:
                    strength = random.randint(1, 3)
                else:
                    strength = get_trait_strength(player, t, tier=5)
                player.traits.append({'name': t, 'strength': strength})
                assigned.add(t)
                remaining -= 1
    
    def develop_youth_players(self, team, current_season=None):
        """
        Develop youth players based on potential
        
        Youth players with high potential improve faster
        """
        if not hasattr(team, 'u21_squad'):
            return
        
        for player in team.u21_squad:
            if current_season is not None:
                if getattr(player, '_annual_skill_development_season', None) == current_season:
                    continue
            # Improvement chance based on potential
            improvement_chance = player.potential / 100.0
            
            if random.random() < improvement_chance:
                # Improve skills
                if 'Batter' in player.role or 'Wicketkeeper' in player.role or 'All-rounder' in player.role:
                    player.batting = min(95, player.batting + random.randint(1, 3))
                
                if 'Bowler' in player.role or 'All-rounder' in player.role or 'Pacer' in player.role or 'Spinner' in player.role:
                    player.bowling = min(95, player.bowling + random.randint(1, 3))
                
                player.fielding = min(95, player.fielding + random.randint(1, 2))
            if current_season is not None:
                player._annual_skill_development_season = current_season
