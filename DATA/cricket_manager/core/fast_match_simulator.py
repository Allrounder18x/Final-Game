"""
FastMatchSimulator - 10-Over Chunk Simulation for T20, ODI, and Test Matches
Combines logic from t20oversimulation.py and test_match_enhanced.py
Simulates matches in 10-over chunks for speed while maintaining realistic statistics.
"""

import random
import copy
from typing import Dict, List, Optional, Tuple, Any


class FastMatchSimulator:
    """
    Fast cricket match simulator using 10-over chunk simulation.
    """
    
    FORMAT_SETTINGS = {
        'T20': {
            'avg_score': 160, 'avg_wickets': 7, 'score_variance': 40,
            'wicket_variance': 3, 'max_overs': 20, 'extras_pct': 0.06,
            'min_score': 50, 'max_score': 270, 'run_rate_base': 8.0
        },
        'ODI': {
            'avg_score': 250, 'avg_wickets': 8, 'score_variance': 60,
            'wicket_variance': 3, 'max_overs': 50, 'extras_pct': 0.06,
            'min_score': 60, 'max_score': 450, 'run_rate_base': 5.0
        },
        'Test': {
            'innings_1': {'avg_score': 350, 'avg_wickets': 8, 'score_variance': 80, 'wicket_variance': 3},
            'innings_2': {'avg_score': 350, 'avg_wickets': 8, 'score_variance': 80, 'wicket_variance': 3},
            'innings_3': {'avg_score': 240, 'avg_wickets': 8, 'score_variance': 70, 'wicket_variance': 3},
            'innings_4': {'avg_score': 240, 'avg_wickets': 8, 'score_variance': 70, 'wicket_variance': 3},
            'max_overs': 90, 'extras_pct': 0.08, 'min_score': 80, 'max_score': 550
        }
    }
    
    def __init__(self, team1, team2, match_format='T20', simulation_adjustments=None, pitch_conditions=None):
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.settings = self.FORMAT_SETTINGS.get(match_format, self.FORMAT_SETTINGS['T20'])
        
        # User simulation adjustments from settings (-100 to +100) + difficulty multipliers
        self.simulation_adjustments = simulation_adjustments or {
            'dot_adj': 0,
            'boundary_adj': 0,
            'wicket_adj': 0
        }
        self.difficulty_bat = self.simulation_adjustments.get('difficulty_bat', 1.0)
        self.difficulty_bowl = self.simulation_adjustments.get('difficulty_bowl', 1.0)
        
        self.current_innings = 1
        self.total_runs = 0
        self.total_wickets = 0
        self.total_overs = 0
        self.match_ended = False
        self.target = None
        self.winner = None
        self.result = None
        
        self.batting_team = team1
        self.bowling_team = team2
        self.batting_xi = []
        self.bowling_xi = []
        
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.next_batsman_index = 2
        
        self.match_stats = {}
        self.innings_data = []
        self.fow = []
        
        self.bowler_overs = {}
        self.bowlers_used = []
        self.innings_bowler_balls = {}  # Track balls bowled per bowler in current innings
        
        # Use fixture-provided pitch conditions if available, otherwise generate random
        if pitch_conditions:
            self.pitch_bounce = pitch_conditions.get('pitch_bounce', random.randint(4, 7))
            self.pitch_spin = pitch_conditions.get('pitch_spin', random.randint(4, 7))
            self.pitch_pace = pitch_conditions.get('pitch_pace', random.randint(4, 7))
        else:
            self._generate_pitch_conditions()
        self.weather_options = ['Sunny', 'Cloudy', 'Overcast', 'Humid']
        self.weather = random.choice(self.weather_options)
        
        self.current_day = 1
        self.current_session = 1
        self.ball_age = 0
        self.follow_on_enforced = False
        
    def _generate_pitch_conditions(self):
        """Generate pitch conditions similar to test_match_enhanced.py"""
        pitch_type = random.choice(['green_seamer', 'green_top', 'dustbowl', 'flat_road', 'bouncy', 'balanced'])
        
        if pitch_type == 'green_seamer':
            self.pitch_pace = random.randint(7, 10)
            self.pitch_spin = random.randint(2, 5)
            self.pitch_bounce = random.randint(6, 9)
        elif pitch_type == 'green_top':
            self.pitch_pace = random.randint(8, 10)
            self.pitch_spin = random.randint(1, 3)
            self.pitch_bounce = random.randint(7, 9)
        elif pitch_type == 'dustbowl':
            self.pitch_pace = random.randint(2, 5)
            self.pitch_spin = random.randint(7, 10)
            self.pitch_bounce = random.randint(3, 6)
        elif pitch_type == 'flat_road':
            self.pitch_pace = random.randint(2, 4)
            self.pitch_spin = random.randint(2, 4)
            self.pitch_bounce = random.randint(2, 4)
        elif pitch_type == 'bouncy':
            self.pitch_pace = random.randint(5, 7)
            self.pitch_spin = random.randint(4, 6)
            self.pitch_bounce = random.randint(8, 10)
        else:
            self.pitch_pace = random.randint(5, 7)
            self.pitch_spin = random.randint(5, 7)
            self.pitch_bounce = random.randint(5, 7)
    
    def auto_select_xi(self, team):
        """Auto-select XI with proper balance and rotation - ensures at least 6 bowlers/allrounders for bowling rotation"""
        import random
        
        # Handle both Team objects and dictionary format
        if hasattr(team, 'players'):
            # Team object from game engine
            players = list(team.players)
        elif isinstance(team, dict):
            # Dictionary format
            players = team.get('players', [])[:]
        else:
            players = []
        
        if not players:
            return []
        
        batters = []
        allrounders = []
        bowlers = []
        keepers = []
        
        for p in players:
            # Handle both Player objects and dicts
            if hasattr(p, 'role'):
                role = p.role.lower()
            elif isinstance(p, dict):
                role = p.get('role', '').lower()
            else:
                continue
            
            if 'allrounder' in role or 'all-rounder' in role:
                allrounders.append(p)
            elif 'keeper' in role or 'wicketkeeper' in role:
                keepers.append(p)
            elif 'batter' in role or 'batsman' in role:
                batters.append(p)
            elif any(x in role for x in ['bowler', 'pacer', 'spinner', 'fast', 'medium']):
                bowlers.append(p)
            else:
                # Default to batter if role unclear
                batters.append(p)
        
        # Sort by skills - handle both objects and dicts
        def get_batting(p):
            return p.batting if hasattr(p, 'batting') else p.get('batting', 0)
        
        def get_bowling(p):
            return p.bowling if hasattr(p, 'bowling') else p.get('bowling', 0)
        
        def get_allround_skill(p):
            return (get_batting(p) + get_bowling(p)) / 2
        
        batters_by_skill = sorted(batters, key=get_batting, reverse=True)
        keepers_by_skill = sorted(keepers, key=get_batting, reverse=True)
        allrounders_by_skill = sorted(allrounders, key=get_allround_skill, reverse=True)
        bowlers_by_skill = sorted(bowlers, key=get_bowling, reverse=True)
        
        xi = []
        
        # 1. Select 1 keeper (required) - from top 2 keepers
        if keepers_by_skill:
            top_keepers = keepers_by_skill[:min(2, len(keepers_by_skill))]
            xi.append(random.choice(top_keepers))
        
        # Format-specific rotation pools - T20/ODI need larger pools for better rotation across season
        is_limited_overs = self.match_format in ['T20', 'ODI']
        
        # 2. Select batters with rotation - pick 4 from top 8 (Test) or top 12 (T20/ODI) available
        num_batters_needed = 4
        batter_pool_size = 12 if is_limited_overs else 8  # Larger pool for T20/ODI rotation
        top_batters_pool = batters_by_skill[:min(batter_pool_size, len(batters_by_skill))]
        if len(top_batters_pool) >= num_batters_needed:
            selected_batters = random.sample(top_batters_pool, num_batters_needed)
        else:
            selected_batters = top_batters_pool
        xi.extend(selected_batters)
        
        # 3. Select allrounders with rotation - pick 2 from top 4 (Test) or top 6 (T20/ODI) available
        num_allrounders_needed = 2
        allrounder_pool_size = 6 if is_limited_overs else 4  # Larger pool for T20/ODI rotation
        top_allrounders_pool = allrounders_by_skill[:min(allrounder_pool_size, len(allrounders_by_skill))]
        if len(top_allrounders_pool) >= num_allrounders_needed:
            selected_allrounders = random.sample(top_allrounders_pool, num_allrounders_needed)
        else:
            selected_allrounders = top_allrounders_pool
        xi.extend(selected_allrounders)
        
        # 4. Select bowlers with rotation - pick 4 from top 8 (Test) or top 10 (T20/ODI) available
        num_bowlers_needed = 4
        bowler_pool_size = 10 if is_limited_overs else 8  # Larger pool for T20/ODI rotation
        top_bowlers_pool = bowlers_by_skill[:min(bowler_pool_size, len(bowlers_by_skill))]
        if len(top_bowlers_pool) >= num_bowlers_needed:
            selected_bowlers = random.sample(top_bowlers_pool, num_bowlers_needed)
        else:
            selected_bowlers = top_bowlers_pool
        xi.extend(selected_bowlers)
        
        # 5. Ensure we have at least 6 players who can bowl (bowlers + allrounders)
        bowling_options = len(selected_bowlers) + len(selected_allrounders)
        if bowling_options < 6:
            # Add more bowlers or allrounders
            remaining_bowlers = [b for b in bowlers_by_skill if b not in xi]
            remaining_allrounders = [a for a in allrounders_by_skill if a not in xi]
            
            while bowling_options < 6 and (remaining_bowlers or remaining_allrounders):
                if remaining_bowlers:
                    xi.append(remaining_bowlers.pop(0))
                elif remaining_allrounders:
                    xi.append(remaining_allrounders.pop(0))
                bowling_options += 1
        
        # 6. Fill remaining slots to reach 11
        if len(xi) < 11:
            shortage = 11 - len(xi)
            remaining_players = [p for p in players if p not in xi]
            
            def get_overall(p):
                bat = get_batting(p)
                bowl = get_bowling(p)
                field = p.fielding if hasattr(p, 'fielding') else p.get('fielding', 0)
                return (bat + bowl + field) / 3
            
            remaining_by_overall = sorted(remaining_players, key=get_overall, reverse=True)
            for i in range(min(shortage, len(remaining_by_overall))):
                xi.append(remaining_by_overall[i])
        
        # Trim to 11 if over
        xi = xi[:11]
        
        # Sort by batting skill for batting order
        xi.sort(key=get_batting, reverse=True)
        
        # Mark playing XI - handle both objects and dicts
        for i, player in enumerate(xi):
            if hasattr(player, 'playing_xi'):
                player.playing_xi = True
                player.batting_position = i + 1
            elif isinstance(player, dict):
                player['playing_xi'] = True
                player['batting_position'] = i + 1
        
        return xi
    
    def _init_match_stats(self):
        """Initialize match statistics for all players - handles both Team objects and dicts"""
        # Get players from both teams
        def get_players(team):
            if hasattr(team, 'players'):
                return list(team.players)
            elif isinstance(team, dict):
                return team.get('players', [])
            return []
        
        def get_name(p):
            return p.name if hasattr(p, 'name') else p.get('name', 'Unknown')
        
        all_players = get_players(self.team1) + get_players(self.team2)
        
        for player in all_players:
            name = get_name(player)
            self.match_stats[name] = {
                'batting': {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dismissal': None, 'dismissals': 0, 'innings_batted': 0},
                'bowling': {'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0}
            }
    
    def _calculate_ball_probabilities(self, batting_skill, bowling_skill, 
                                       is_test=False, innings_num=1):
        """Calculate ball outcome probabilities - matches t20oversimulation.py and test_match_enhanced.py"""
        # Base probabilities from baser.py - very realistic Test cricket
        if is_test:
            if innings_num <= 2:
                # Realistic Test probabilities - BATTING FRIENDLY (+18% total on runs, -18% on dots/wickets)
                base_probs = {
                    'dot': 0.533,     # Reduced from 65% to ~53.3% (-18%)
                    'single': 0.238,  # Increased from 20% to 23.8%
                    'double': 0.0714, # Increased from 6% to 7.14%
                    'triple': 0.00595,# Increased from 0.5% to 0.595%
                    'four': 0.0476,   # Increased from 4% to 4.76%
                    'six': 0.00238,   # Increased from 0.2% to 0.238%
                    'wicket': 0.01435,# Reduced from 1.75% to ~1.435%
                    'wide': 0.0022,   # Slightly increased
                    'noball': 0.0011  # Slightly increased
                }
            else:
                # Slightly higher wickets for innings 3-4 as pitch deteriorates
                base_probs = {
                    'dot': 0.509,
                    'single': 0.238,
                    'double': 0.0714,
                    'triple': 0.00595,
                    'four': 0.0452,
                    'six': 0.00238,
                    'wicket': 0.0155,  # Slightly higher for deteriorated pitch
                    'wide': 0.0022,
                    'noball': 0.0011
                }
        elif self.match_format == 'T20':
            # T20 base probabilities - match t20oversimulation.py
            base_probs = {'dot': 0.32, 'single': 0.28, 'double': 0.132, 'triple': 0.0165,
                   'four': 0.132, 'six': 0.088, 'wicket': 0.04554}
        else:
            # ODI base probabilities - match t20oversimulation.py (decreased wickets by 3%)
            base_probs = {'dot': 0.43, 'single': 0.303, 'double': 0.12, 'triple': 0.02,
                   'four': 0.06, 'six': 0.04, 'wicket': 0.024}
        
        # Get bowler role for pitch effects
        bowler_role = self._get_attr(self.current_bowler, 'role', '').lower()
        is_pace_bowler = any(term in bowler_role for term in ['fast', 'medium', 'seam'])
        is_spin_bowler = not is_pace_bowler
        
        # Pitch effects - matching t20oversimulation.py (end version)
        if is_pace_bowler:
            if self.pitch_pace >= 7:
                base_probs['dot'] *= 1.2
                base_probs['wicket'] *= 1.2
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.7
            elif self.pitch_pace <= 3:
                base_probs['dot'] *= 0.9
                base_probs['wicket'] *= 0.9
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
            # Bounce effect for pace bowlers (stronger)
            if self.pitch_bounce >= 7:
                base_probs['dot'] *= 1.15
                base_probs['wicket'] *= 1.25
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.75
            elif self.pitch_bounce <= 3:
                base_probs['dot'] *= 0.95
                base_probs['wicket'] *= 0.9
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
        else:
            # Spin bowler
            if self.pitch_spin >= 7:
                base_probs['dot'] *= 1.2
                base_probs['wicket'] *= 1.2
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.7
            elif self.pitch_spin <= 3:
                base_probs['dot'] *= 0.9
                base_probs['wicket'] *= 0.75
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
            # Bounce effect for spin bowlers (milder)
            if self.pitch_bounce >= 7:
                base_probs['dot'] *= 1.05
                base_probs['wicket'] *= 1.05
                base_probs['four'] *= 0.9
                base_probs['six'] *= 0.85
            elif self.pitch_bounce <= 3:
                base_probs['dot'] *= 0.98
                base_probs['wicket'] *= 0.95
                base_probs['four'] *= 1.05
                base_probs['six'] *= 1.05
        
        # Player traits - batter traits (matching t20oversimulation.py)
        batter_traits = self._get_attr(self.striker, 'traits', [])
        current_over = self.total_overs
        
        # Format-specific phase definitions
        if self.match_format == 'T20':
            is_powerplay = current_over <= 6
            is_middle_overs = 6 < current_over < 16
            is_death_overs = current_over >= 16
        elif self.match_format == 'ODI':
            is_powerplay = current_over <= 10
            is_middle_overs = 10 < current_over < 40
            is_death_overs = current_over >= 40
        else:  # Test
            is_powerplay = False
            is_middle_overs = False
            is_death_overs = False
        
        if batter_traits:
            for trait in batter_traits:
                trait_name = trait.get('name', '') if isinstance(trait, dict) else ''
                trait_strength = trait.get('strength', 3) if isinstance(trait, dict) else 3
                # Calculate trait effect (1.0 + strength * 0.1 for strength 1-5)
                trait_effect = 1.0 + (trait_strength * 0.1)
                
                if trait_name == 'POWER_OPENER' and is_powerplay:
                    base_probs['four'] *= trait_effect
                    base_probs['six'] *= trait_effect
                    base_probs['dot'] /= trait_effect
                elif trait_name == 'CONSOLIDATOR' and is_middle_overs:
                    base_probs['single'] *= trait_effect
                    base_probs['double'] *= trait_effect
                    base_probs['wicket'] /= trait_effect
                elif trait_name == 'SPIN_BASHER' and is_spin_bowler:
                    base_probs['four'] *= trait_effect
                    base_probs['six'] *= trait_effect
                elif trait_name == 'DEMOLISHER_OF_PACE' and is_pace_bowler and not is_powerplay:
                    base_probs['four'] *= trait_effect
                    base_probs['six'] *= trait_effect
                elif trait_name == 'FINISHER' and is_death_overs:
                    base_probs['four'] *= trait_effect
                    base_probs['six'] *= trait_effect
                    base_probs['wicket'] /= trait_effect
                # --- Format-specific youth negative batting traits ---
                # T20 batting traits
                elif trait_name == 'T20_POWERPLAY_WASTER' and is_powerplay:
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['dot'] *= (2.0 - neg_effect)
                    base_probs['single'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['four'] *= neg_effect
                    base_probs['six'] *= neg_effect
                elif trait_name == 'T20_CANT_HIT_SIXES':
                    neg_effect = 1.0 - (trait_strength * 0.16)
                    base_probs['six'] *= neg_effect
                    base_probs['four'] *= neg_effect * 0.5 + 0.5
                elif trait_name == 'T20_DEATH_OVERS_CHOKER' and is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= neg_effect
                    base_probs['six'] *= neg_effect
                    base_probs['dot'] *= (2.0 - neg_effect)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                elif trait_name == 'T20_DOT_BALL_MAGNET':
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['dot'] *= (2.0 - neg_effect)
                    base_probs['single'] *= neg_effect
                    base_probs['four'] *= neg_effect * 0.5 + 0.5
                elif trait_name == 'T20_RASH_SHOT_MERCHANT':
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['four'] *= 1.05
                    base_probs['six'] *= 1.05
                # ODI batting traits
                elif trait_name == 'ODI_MIDDLE_OVERS_STALLER' and not is_powerplay and not is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['dot'] *= (2.0 - neg_effect)
                    base_probs['single'] *= neg_effect
                    base_probs['four'] *= neg_effect
                elif trait_name == 'ODI_SLOG_MISFIRE' and is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['four'] *= neg_effect
                    base_probs['six'] *= neg_effect
                elif trait_name == 'ODI_POOR_STRIKE_ROTATION':
                    neg_effect = 1.0 - (trait_strength * 0.10)
                    base_probs['single'] *= neg_effect
                    base_probs['dot'] *= (2.0 - neg_effect)
                elif trait_name == 'ODI_COLLAPSER' and self.total_wickets >= 3:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
                elif trait_name == 'ODI_CHASE_BOTTLER' and self.current_innings == 2:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['four'] *= neg_effect
                # Test batting traits
                elif trait_name == 'TEST_NEW_BALL_BUNNY' and self.total_overs < 20:
                    neg_effect = 1.0 - (trait_strength * 0.16)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
                elif trait_name == 'TEST_POOR_CONCENTRATION':
                    batter_name = self._get_attr(self.striker, 'name', '')
                    b_runs = self.match_stats.get(batter_name, {}).get('batting', {}).get('runs', 0)
                    if 30 <= b_runs <= 70:
                        neg_effect = 1.0 - (trait_strength * 0.12)
                        base_probs['wicket'] *= (2.0 - neg_effect)
                elif trait_name == 'TEST_DAY5_CRUMBLER':
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
                elif trait_name == 'TEST_SECOND_INNINGS_FLOP' and hasattr(self, 'current_innings') and self.current_innings in (2, 4):
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['four'] *= neg_effect
                elif trait_name == 'TEST_BOUNCER_VICTIM' and is_pace_bowler:
                    neg_effect = 1.0 - (trait_strength * 0.16)
                    base_probs['wicket'] *= (2.0 - neg_effect)
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
        
        # Apply bowler's format-specific youth negative traits
        bowler_traits = self._get_attr(self.current_bowler, 'traits', [])
        if bowler_traits:
            for trait in bowler_traits:
                trait_name = trait.get('name', '') if isinstance(trait, dict) else ''
                trait_strength = trait.get('strength', 3) if isinstance(trait, dict) else 3
                
                # T20 bowling traits
                if trait_name == 'T20_DEATH_BOWLING_LIABILITY' and is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.18)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['six'] *= (2.0 - neg_effect)
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'T20_POWERPLAY_LEAKER' and is_powerplay:
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['six'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'T20_NO_SLOWER_BALL':
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['six'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'T20_WIDE_MACHINE':
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['dot'] *= neg_effect
                    base_probs['four'] *= (2.0 - neg_effect) * 0.5 + 0.5
                elif trait_name == 'T20_PRESSURE_CRUMBLER':
                    bowler_name = self._get_attr(self.current_bowler, 'name', '')
                    b_runs = self.match_stats.get(bowler_name, {}).get('bowling', {}).get('runs', 0)
                    b_balls = self.match_stats.get(bowler_name, {}).get('bowling', {}).get('balls', 0)
                    if b_balls > 0 and b_runs / max(1, b_balls) > 1.5:
                        neg_effect = 1.0 - (trait_strength * 0.16)
                        base_probs['four'] *= (2.0 - neg_effect)
                        base_probs['six'] *= (2.0 - neg_effect)
                        base_probs['wicket'] *= neg_effect
                # ODI bowling traits
                elif trait_name == 'ODI_MIDDLE_OVERS_EXPENSIVE' and not is_powerplay and not is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['single'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'ODI_NO_WICKET_TAKER':
                    neg_effect = 1.0 - (trait_strength * 0.10)
                    base_probs['wicket'] *= neg_effect
                    base_probs['dot'] *= (2.0 - neg_effect) * 0.3 + 0.7
                elif trait_name == 'ODI_DEATH_OVERS_LEAKER' and is_death_overs:
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['six'] *= (2.0 - neg_effect)
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'ODI_FIRST_SPELL_ONLY':
                    bowler_name = self._get_attr(self.current_bowler, 'name', '')
                    b_balls = self.match_stats.get(bowler_name, {}).get('bowling', {}).get('balls', 0)
                    if b_balls > 30:
                        neg_effect = 1.0 - (trait_strength * 0.10)
                        base_probs['four'] *= (2.0 - neg_effect)
                        base_probs['wicket'] *= neg_effect
                elif trait_name == 'ODI_PARTNERSHIP_FEEDER':
                    batter_name = self._get_attr(self.striker, 'name', '')
                    b_runs = self.match_stats.get(batter_name, {}).get('batting', {}).get('runs', 0)
                    if b_runs >= 30:
                        neg_effect = 1.0 - (trait_strength * 0.10)
                        base_probs['four'] *= (2.0 - neg_effect)
                        base_probs['six'] *= (2.0 - neg_effect) * 0.5 + 0.5
                        base_probs['wicket'] *= neg_effect
                # Test bowling traits
                elif trait_name == 'TEST_NO_STAMINA':
                    bowler_name = self._get_attr(self.current_bowler, 'name', '')
                    b_balls = self.match_stats.get(bowler_name, {}).get('bowling', {}).get('balls', 0)
                    if b_balls > 30:
                        neg_effect = 1.0 - (trait_strength * 0.14)
                        base_probs['four'] *= (2.0 - neg_effect)
                        base_probs['wicket'] *= neg_effect
                elif trait_name == 'TEST_FLAT_PITCH_PASSENGER':
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['six'] *= (2.0 - neg_effect) * 0.5 + 0.5
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'TEST_REVERSE_SWING_HOPELESS' and self.total_overs >= 30:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'TEST_DAY5_TOOTHLESS':
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    base_probs['four'] *= (2.0 - neg_effect)
                    base_probs['wicket'] *= neg_effect
                elif trait_name == 'TEST_SPELL_BREAKER':
                    bowler_name = self._get_attr(self.current_bowler, 'name', '')
                    b_balls = self.match_stats.get(bowler_name, {}).get('bowling', {}).get('balls', 0)
                    if b_balls > 18:
                        neg_effect = 1.0 - (trait_strength * 0.10)
                        base_probs['four'] *= (2.0 - neg_effect)
                        base_probs['wicket'] *= neg_effect
        
        # Skill differential - additive approach from baser.py (more realistic for Tests)
        skill_diff = (batting_skill - bowling_skill) / 100.0
        if is_test:
            # Additive adjustments for Test cricket (from baser.py)
            base_probs['dot'] += -skill_diff * 0.12
            base_probs['single'] += skill_diff * 0.06
            base_probs['four'] += skill_diff * 0.04
            base_probs['six'] += skill_diff * 0.01
            base_probs['wicket'] += -skill_diff * 0.015
        else:
            # Multiplicative for limited overs (original behavior)
            for outcome in base_probs:
                if outcome in ['four', 'six']:
                    base_probs[outcome] *= (1 + skill_diff)
                elif outcome == 'wicket':
                    base_probs[outcome] *= (1 - skill_diff)
            # T20 only: elite batters harder to dismiss, average batters easier to dismiss
            if self.match_format == 'T20':
                if batting_skill >= 75:
                    base_probs['wicket'] *= 0.72   # elite: reduce wicket chance
                elif batting_skill <= 50:
                    base_probs['wicket'] *= 1.28   # average: increase wicket chance
            # Revert T20 wicket changes while keeping code, and reduce 4s/6s for elite batters
            if self.match_format == 'T20':
                if batting_skill >= 75:
                    # Cancel previous wicket tweak for elite batters
                    base_probs['wicket'] /= 0.72
                    # New: slightly reduce 4s and 6s probability (3%) for elite batters
                    base_probs['four'] *= 0.97 * 0.97   # 3% + further 3% reduction for elite
                    base_probs['six'] *= 0.97 * 0.97
                elif batting_skill <= 50:
                    # Cancel previous wicket tweak for average batters
                    base_probs['wicket'] /= 1.28
            # T20/ODI: slightly higher wicket chance for elite batters, lower for very low-skill
            if not is_test:
                if batting_skill >= 75:
                    base_probs['wicket'] *= 1.06   # elite: +10% wicket probability
                elif batting_skill < 40:
                    base_probs['wicket'] *= 0.90   # low skill: -10% wicket probability
                # Global tuning: increase wicket probability in ODIs and T20s by 13%
                # Applied only for batters with skill >= 40 to avoid over-punishing weak batters
                if self.match_format in ('T20', 'ODI') and batting_skill >= 40:
                    base_probs['wicket'] *= 1.13
        
        # Bowling skill adjustments for realistic bowling averages in Test matches
        # Balanced: Elite bowlers should have better averages, but all bowlers need to take wickets
        # Target: Elite ~28 avg, Good ~35 avg, Average ~45 avg, Weak ~60+ avg
        # IMPORTANT: Even weak bowlers need to take ~6+ wickets per innings to allow all batters to bat
        if is_test:
            if bowling_skill >= 80:
                # Elite bowlers - better average (~28)
                elite_bonus = (bowling_skill - 80) / 100  # 0.0 to 0.20
                base_probs['wicket'] *= (0.90 + elite_bonus * 0.10)  # 90-110% of base
            elif bowling_skill >= 60:
                # Good bowlers - decent average (~35)
                good_bonus = (bowling_skill - 60) / 100  # 0.0 to 0.20 for 60-79
                base_probs['wicket'] *= (0.75 + good_bonus * 0.10)  # 75-85% of base
            elif bowling_skill >= 40:
                # Average bowlers - average performance (~45)
                base_probs['wicket'] *= 0.60  # 60% of base - still takes wickets
            else:
                # Weak bowlers - poor average but still takes wickets (~60+)
                # INCREASED from 20% to 50% to ensure enough wickets for all batters to bat
                base_probs['wicket'] *= 0.50  # 50% of base - ensures ~6-7 wickets per innings
        
        # Test match specific adjustments
        if is_test:
            # Ball age effects
            if self.ball_age < 20:
                base_probs['wicket'] *= 1.4
                base_probs['dot'] *= 1.2
            elif self.ball_age > 60:
                base_probs['single'] *= 1.3
                base_probs['wicket'] *= 0.7
            
            # Day effects
            if hasattr(self, 'current_day') and self.current_day >= 4:
                base_probs['wicket'] *= 1.25
            
            # Weather effects
            if self.weather == 'Overcast' and is_pace_bowler and self.ball_age < 25:
                base_probs['wicket'] *= 1.5
                base_probs['dot'] *= 1.3
            elif self.weather == 'Sunny' and is_spin_bowler and hasattr(self, 'current_day') and self.current_day >= 3:
                base_probs['wicket'] *= 1.4
                base_probs['dot'] *= 1.2
            
            # Penalty for low-skilled batsmen (< 45 batting) - DOUBLED PENALTY
            if batting_skill < 45:
                skill_penalty = (45 - batting_skill) / 100  # 0.01 to 0.45 penalty
                base_probs['wicket'] *= (1.0 + skill_penalty * 4.0)  # DOUBLED: Up to 180% more wickets
                base_probs['dot'] *= (1.0 + skill_penalty * 1.0)     # DOUBLED: Up to 45% more dots
                base_probs['four'] *= (1.0 - skill_penalty * 1.0 + skill_penalty * 0.067)  # DOUBLED + 3% boundary bonus
                base_probs['six'] *= (1.0 - skill_penalty * 1.0 + skill_penalty * 0.067)   # DOUBLED + 3% boundary bonus
            # Penalty for average batsmen (45-60) - DOUBLED PENALTY for < 61 skill
            elif batting_skill < 61:
                avg_penalty = (61 - batting_skill) / 100  # 0.0 to 0.16 for 45-60 skill
                base_probs['wicket'] *= (3.0 + avg_penalty * 6.0)  # DOUBLED: +200% base + scaling (up to 296% total)
                base_probs['dot'] *= (1.0 + avg_penalty * 2.0)     # DOUBLED
                base_probs['four'] *= (1.0 - avg_penalty * 1.6)    # DOUBLED
            
            # Format-specific wicket increase for skilled batters
            # Test +4%, T20/ODI +3% — makes dismissals more realistic
            wkt_boost = 1.04 if is_test else 1.03
            
            # Global curb on Test boundaries so 4s and 6s are slightly rarer across all skill levels
            base_probs['four'] *= 0.90
            base_probs['six'] *= 0.90
            
            # Elite batsmen (80+) - target avg ~50, but increase wickets to reduce centuries/fifties
            if batting_skill >= 80:
                elite_bonus = (batting_skill - 80) / 100  # 0.0 to 0.20 for 80-100 skill
                base_probs['wicket'] *= (1.08 - elite_bonus * 0.78)  # +8% base, reduced by skill (down to -8% at 100 skill)
                base_probs['wicket'] *= wkt_boost
                base_probs['four'] *= (1.0 + elite_bonus * 1.5)
                base_probs['six'] *= (1.0 + elite_bonus * 1.0)
                # ADDITIONAL 6% for elite batters on ALL scoring shots
                base_probs['single'] *= 1.06
                base_probs['double'] *= 1.06
                base_probs['four'] *= 1.06
                base_probs['six'] *= 1.06
                base_probs['dot'] *= 0.94
                
                # Super elite batsmen (89+) - additional 4% boost
                if batting_skill >= 89:
                    base_probs['single'] *= 1.04
                    base_probs['double'] *= 1.04
                    base_probs['four'] *= 1.04
                    base_probs['six'] *= 1.04
                    base_probs['wicket'] *= 0.96
                    base_probs['dot'] *= 0.96
            # Good batters (60-79) - target avg ~40, increase wickets to reduce big scores
            elif batting_skill >= 60:
                good_penalty = (80 - batting_skill) / 100  # 0.0 to 0.20 for 60-79 skill
                base_probs['wicket'] *= (1.40 + good_penalty * 1.2)  # +40% base + scaling (up to 64% total)
                base_probs['wicket'] *= wkt_boost
                # ADDITIONAL 4% for good batters
                base_probs['single'] *= 1.04
                base_probs['double'] *= 1.04
                base_probs['dot'] *= 0.96
        
        # Apply user simulation adjustments from settings (-100 to +100)
        dot_adj = self.simulation_adjustments.get('dot_adj', 0) / 100.0
        boundary_adj = self.simulation_adjustments.get('boundary_adj', 0) / 100.0
        wicket_adj = self.simulation_adjustments.get('wicket_adj', 0) / 100.0
        
        # Apply adjustments (positive = increase, negative = decrease)
        base_probs['dot'] *= (1.0 + dot_adj)
        base_probs['four'] *= (1.0 + boundary_adj)
        base_probs['six'] *= (1.0 + boundary_adj)
        base_probs['wicket'] *= (1.0 + wicket_adj)
        
        # Ensure no negative probabilities
        for key in base_probs:
            base_probs[key] = max(0.001, base_probs[key])
        
        # Normalize probabilities
        total = sum(base_probs.values())
        for outcome in base_probs:
            base_probs[outcome] /= total
        
        # Cap wicket probability for Test matches (prevents unrealistic collapses)
        # BUT only for skilled batters (60+) - weak batters should get out more often.
        # Slightly relaxed caps to increase total dismissals in long Test careers.
        if is_test:
            if batting_skill >= 60:
                # Skilled batters get protection from unrealistic collapses
                if base_probs['wicket'] > 0.028:   # was 0.022
                    excess = base_probs['wicket'] - 0.028
                    base_probs['wicket'] = 0.028
                    base_probs['dot'] += excess
                elif base_probs['wicket'] < 0.016:  # was 0.012
                    deficit = 0.016 - base_probs['wicket']
                    base_probs['wicket'] = 0.016
                    base_probs['dot'] = max(0.001, base_probs['dot'] - deficit)
            else:
                # Weak batters (< 60 skill) - previously had an extra wicket cap here.
                # To avoid a double penalty, this block is now disabled so they only
                # receive the standard skill-based adjustments above.
                if False:
                    # Cap at 0.06 (6%) to prevent completely unrealistic dismissals (was 5%)
                    if base_probs['wicket'] > 0.06:
                        excess = base_probs['wicket'] - 0.06
                        base_probs['wicket'] = 0.06
                        base_probs['dot'] += excess
        
        return base_probs
    
    def _get_attr(self, obj, attr, default=0):
        """Get attribute from object or dict"""
        if hasattr(obj, attr):
            return getattr(obj, attr)
        elif isinstance(obj, dict):
            return obj.get(attr, default)
        return default
    
    def _set_attr(self, obj, attr, value):
        """Set attribute on object or dict"""
        if hasattr(obj, attr):
            setattr(obj, attr, value)
        elif isinstance(obj, dict):
            obj[attr] = value
    
    def _get_name(self, obj):
        """Get name from object or dict"""
        return self._get_attr(obj, 'name', 'Unknown')
    
    def _simulate_10_over_chunk(self, overs_to_simulate=10):
        """
        Simulate a chunk of overs by processing balls individually (like original simulators)
        but without GUI overhead for speed.
        """
        chunk_runs = 0
        chunk_wickets = 0
        is_test = self.match_format == 'Test'
        innings_num = self.current_innings if is_test else 1
        
        # Process each over
        for over in range(overs_to_simulate):
            if self.total_wickets >= 10:
                break
            
            # Check for innings end conditions
            max_overs = self.settings.get('max_overs', 20) if not is_test else 90
            if max_overs and self.total_overs >= max_overs:
                break
            if self.target and self.total_runs >= self.target:
                break
            
            # Process 6 balls in this over
            for ball in range(6):
                if self.total_wickets >= 10:
                    break
                
                # Get probabilities based on current state (form and difficulty modifiers)
                batting_skill = self._get_attr(self.striker, 'batting', 50) if self.striker else 50
                bowling_skill = self._get_attr(self.current_bowler, 'bowling', 50) if self.current_bowler else 50
                striker_form = self._get_attr(self.striker, 'form', 50) if self.striker else 50
                bowler_form = self._get_attr(self.current_bowler, 'form', 50) if self.current_bowler else 50
                form_bat = 0.96 + (striker_form / 50.0) * 0.16
                form_bowl = 0.96 + (bowler_form / 50.0) * 0.16
                batting_skill = min(99, max(1, batting_skill * form_bat * getattr(self, 'difficulty_bat', 1.0)))
                bowling_skill = min(99, max(1, bowling_skill * form_bowl * getattr(self, 'difficulty_bowl', 1.0)))
                probs = self._calculate_ball_probabilities(batting_skill, bowling_skill, is_test, innings_num)
                
                # Determine outcome
                outcomes = list(probs.keys())
                weights = [probs[o] for o in outcomes]
                outcome = random.choices(outcomes, weights=weights, k=1)[0]
                
                # Process outcome
                if outcome == 'wicket':
                    chunk_wickets += 1
                    self.total_wickets += 1
                    
                    # Record wicket
                    if self.striker and self.current_bowler:
                        striker_name = self._get_name(self.striker)
                        bowler_name = self._get_name(self.current_bowler)
                        self.match_stats[striker_name]['batting']['dismissal'] = f"b {bowler_name}"
                        self.match_stats[striker_name]['batting']['dismissals'] += 1  # Track total dismissals for avg
                        self.match_stats[striker_name]['batting']['balls'] += 1
                        self.match_stats[bowler_name]['bowling']['wickets'] += 1
                        self.match_stats[bowler_name]['bowling']['balls'] += 1
                        # Track innings-specific balls for over limit enforcement
                        self.innings_bowler_balls[bowler_name] = self.innings_bowler_balls.get(bowler_name, 0) + 1
                    
                    # Record FOW
                    self.fow.append({
                        'wicket': self.total_wickets,
                        'score': self.total_runs,
                        'batsman': self._get_name(self.striker) if self.striker else 'Unknown',
                        'overs': f"{self.total_overs}.{ball+1}"
                    })
                    
                    # Get next batsman
                    if self.next_batsman_index < len(self.batting_xi):
                        self.striker = self.batting_xi[self.next_batsman_index]
                        self.next_batsman_index += 1
                    else:
                        break
                        
                elif outcome in ['wide', 'noball']:
                    # Wide or no-ball = 1 run + extra ball
                    chunk_runs += 1
                    self.total_runs += 1
                    if self.current_bowler:
                        bowler_name = self._get_name(self.current_bowler)
                        self.match_stats[bowler_name]['bowling']['runs'] += 1
                    # Ball is not counted, don't increment ball count
                    
                else:
                    # Runs scored
                    runs = {'dot': 0, 'single': 1, 'double': 2, 'triple': 3, 'four': 4, 'six': 6}[outcome]
                    chunk_runs += runs
                    self.total_runs += runs
                    
                    # Update batsman stats
                    if self.striker:
                        striker_name = self._get_name(self.striker)
                        self.match_stats[striker_name]['batting']['runs'] += runs
                        self.match_stats[striker_name]['batting']['balls'] += 1
                        if runs == 4:
                            self.match_stats[striker_name]['batting']['fours'] += 1
                        elif runs == 6:
                            self.match_stats[striker_name]['batting']['sixes'] += 1
                    
                    # Update bowler stats
                    if self.current_bowler:
                        bowler_name = self._get_name(self.current_bowler)
                        self.match_stats[bowler_name]['bowling']['runs'] += runs
                        self.match_stats[bowler_name]['bowling']['balls'] += 1
                        # Track innings-specific balls for over limit enforcement
                        self.innings_bowler_balls[bowler_name] = self.innings_bowler_balls.get(bowler_name, 0) + 1
                    
                    # Swap strikers on odd runs
                    if runs % 2 == 1:
                        self.striker, self.non_striker = self.non_striker, self.striker
            
            # Over complete - rotate bowler
            self.total_overs += 1
            self.ball_age += 1
            if self.total_overs % 80 == 0:
                self.ball_age = 0  # New ball in Test
            self.current_bowler = self._get_next_bowler()
            
            # Swap strikers at end of over
            self.striker, self.non_striker = self.non_striker, self.striker
        
        return chunk_runs, chunk_wickets, overs_to_simulate * 6
    
    def _get_bowler_overs_this_innings(self, bowler_name):
        """Get overs bowled by a bowler in the current innings"""
        # Use the innings_bowler_balls tracker which is reset each innings
        balls = self.innings_bowler_balls.get(bowler_name, 0)
        return balls // 6
    
    def _get_next_bowler(self):
        """Get next bowler based on rotation - lowest overs bowled among available bowlers"""
        # Ensure bowling_xi is populated
        if not self.bowling_xi or len(self.bowling_xi) == 0:
            # Try to get players from bowling team
            if hasattr(self.bowling_team, 'players') and self.bowling_team.players:
                self.bowling_xi = list(self.bowling_team.players)[:11]
            elif isinstance(self.bowling_team, dict) and self.bowling_team.get('players'):
                self.bowling_xi = list(self.bowling_team.get('players', []))[:11]
            
            # If still empty, this is a critical error
            if not self.bowling_xi:
                # Return current bowler if we have one
                if self.current_bowler:
                    return self.current_bowler
                raise ValueError("No players available to bowl - bowling XI is empty")
        
        # Get players with bowling skill > 0
        bowling_xi = [p for p in self.bowling_xi if self._get_attr(p, 'bowling', 0) > 0]
        
        # If no dedicated bowlers, use all players sorted by bowling skill (even if low)
        if not bowling_xi:
            bowling_xi = sorted(self.bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
        
        # Get top 6 bowlers (or all if less than 6)
        bowlers = sorted(bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)[:6]
        
        # If still no bowlers, use any player from the XI
        if not bowlers:
            bowlers = list(self.bowling_xi)[:6] if self.bowling_xi else []
        
        # Final fallback - use any available player
        if not bowlers:
            if self.bowling_xi:
                return self.bowling_xi[0]
            if self.current_bowler:
                return self.current_bowler
            raise ValueError("No players available to bowl - bowling XI is empty")
        
        # Determine max overs per bowler based on format
        if self.match_format == 'T20':
            max_overs_per_bowler = 4
        elif self.match_format == 'ODI':
            max_overs_per_bowler = 10
        else:  # Test
            max_overs_per_bowler = 999  # No limit in Test matches
        
        current_bowler_name = self._get_name(self.current_bowler) if self.current_bowler else None
        
        # Filter out bowlers who have reached their max overs AND the current bowler (can't bowl consecutive overs)
        available = [b for b in bowlers 
                     if self._get_name(b) != current_bowler_name 
                     and self._get_bowler_overs_this_innings(self._get_name(b)) < max_overs_per_bowler]
        
        # If no bowlers available (all maxed out except current), allow current bowler
        if not available:
            available = [b for b in bowlers if self._get_bowler_overs_this_innings(self._get_name(b)) < max_overs_per_bowler]
        
        # If still no bowlers available (all maxed out), use any bowler
        if not available:
            available = bowlers
        
        # Select bowler with fewest overs bowled this innings
        next_bowler = min(available, key=lambda x: self._get_bowler_overs_this_innings(self._get_name(x)))
        return next_bowler

    
    def simulate_innings(self):
        """
        Simulate a complete innings using 10-over chunks.
        Each chunk processes balls individually like the original simulators.
        """
        is_test = self.match_format == 'Test'
        max_overs = self.settings.get('max_overs', 20) if not is_test else None
        
        # Continue until innings end
        while self.total_wickets < 10:
            # Check for innings end conditions
            if max_overs and self.total_overs >= max_overs:
                break
            if is_test and self.total_overs >= 90:
                break
            
            # Check for target (2nd innings)
            if self.target and self.total_runs >= self.target:
                break
            
            # Calculate remaining overs in this chunk
            if max_overs:
                remaining_overs = max_overs - self.total_overs
            else:
                remaining_overs = 90 - self.total_overs if is_test else 20
            
            chunk_size = min(10, remaining_overs)
            
            # Simulate 10-over chunk (ball-by-ball internally)
            self._simulate_10_over_chunk(chunk_size)
            
            # Test match specific: check for declaration
            if is_test and self.current_innings in [1, 3]:
                if self.total_runs >= 520:
                    break
                if self.current_innings == 3 and len(self.innings_data) >= 2:
                    team1_total = self.innings_data[0]['runs']
                    team2_total = self.innings_data[1]['runs']
                    current_lead = (team1_total - team2_total) + self.total_runs
                    if current_lead >= 380:
                        break
            
            # Check if all out
            if self.total_wickets >= 10:
                break
    
    def _save_innings_data(self):
        """Save current innings data"""
        # Save batting XI names for complete scorecard
        batting_xi_names = [self._get_name(p) for p in self.batting_xi]
        
        innings_data = {
            'innings_num': self.current_innings,
            'batting_team': self._get_name(self.batting_team),
            'bowling_team': self._get_name(self.bowling_team),
            'runs': self.total_runs,
            'wickets': self.total_wickets,
            'overs': self.total_overs,
            'match_stats': copy.deepcopy(self.match_stats),
            'fow': copy.deepcopy(self.fow),
            'batting_xi': batting_xi_names
        }
        self.innings_data.append(innings_data)
    
    def _check_follow_on(self):
        """Check if follow-on should be enforced in Test matches"""
        if self.match_format != 'Test' or len(self.innings_data) < 2:
            return False
        
        team1_score = self.innings_data[0]['runs']
        team2_score = self.innings_data[1]['runs']
        deficit = team1_score - team2_score
        
        if deficit >= 200:
            enforce_chance = 0.55
            if deficit >= 300:
                enforce_chance += 0.2
            if deficit >= 400:
                enforce_chance += 0.15
            if self.current_day <= 2:
                enforce_chance += 0.15
            if self.pitch_pace >= 7 or self.pitch_spin >= 7:
                enforce_chance += 0.1
            
            enforce_chance = min(0.95, enforce_chance)
            
            if random.random() < enforce_chance:
                self.follow_on_enforced = True
                return True
        
        return False
    
    def _start_next_innings(self):
        """Setup for next innings"""
        self._save_innings_data()
        self.current_innings += 1
        
        # Swap teams
        if not self.follow_on_enforced or self.current_innings > 3:
            self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        
        self.follow_on_enforced = False
        
        # Reset innings state
        self.total_runs = 0
        self.total_wickets = 0
        self.total_overs = 0
        self.fow = []
        self.ball_age = 0
        self.innings_bowler_balls = {}  # Reset innings-specific bowler balls
        
        # Select new XIs
        self.batting_xi = self.auto_select_xi(self.batting_team)
        self.bowling_xi = self.auto_select_xi(self.bowling_team)
        
        # Reset batsmen
        if len(self.batting_xi) >= 2:
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
            self.next_batsman_index = 2
        
        # Select opening bowler
        bowling_xi = [p for p in self.bowling_xi if self._get_attr(p, 'bowling', 0) > 0]
        bowlers = sorted(bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
        if bowlers:
            self.current_bowler = bowlers[0]
        
        self.bowler_overs = {}
    
    def simulate_t20_match(self):
        """Simulate a T20 match"""
        # Select XIs
        self.batting_xi = self.auto_select_xi(self.team1)
        self.bowling_xi = self.auto_select_xi(self.team2)
        
        # Initialize match stats
        self._init_match_stats()
        
        # Set initial players
        if len(self.batting_xi) >= 2:
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
        
        bowling_xi = [p for p in self.bowling_xi if self._get_attr(p, 'bowling', 0) > 0]
        if bowling_xi:
            bowlers = sorted(bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
            self.current_bowler = bowlers[0]
        elif self.bowling_xi:
            # Fallback: use any player from bowling XI sorted by bowling skill
            bowlers = sorted(self.bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
            self.current_bowler = bowlers[0]
        
        # First innings
        self.simulate_innings()
        first_innings_runs = self.total_runs
        first_innings_wickets = self.total_wickets
        self._save_innings_data()
        
        # Setup second innings
        self.target = first_innings_runs + 1
        self.batting_team, self.bowling_team = self.team2, self.team1
        self.current_innings = 2
        self.total_runs = 0
        self.total_wickets = 0
        self.total_overs = 0
        self.fow = []
        self.bowler_overs = {}  # Reset bowler overs for new innings
        self.innings_bowler_balls = {}  # Reset innings-specific bowler balls
        
        self.batting_xi = self.auto_select_xi(self.batting_team)
        self.bowling_xi = self.auto_select_xi(self.bowling_team)
        
        if len(self.batting_xi) >= 2:
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
            self.next_batsman_index = 2
        
        bowling_xi = [p for p in self.bowling_xi if self._get_attr(p, 'bowling', 0) > 0]
        if bowling_xi:
            bowlers = sorted(bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
            self.current_bowler = bowlers[0]
        elif self.bowling_xi:
            # Fallback: use any player from bowling XI sorted by bowling skill
            bowlers = sorted(self.bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
            self.current_bowler = bowlers[0]
        
        self.bowler_overs = {}
        
        # Second innings
        self.simulate_innings()
        self._save_innings_data()  # Save second innings data
        
        # Determine result
        if self.total_runs >= self.target:
            self.winner = self._get_name(self.team2)
            self.result = f"{self._get_name(self.team2)} won by {10 - self.total_wickets} wickets"
        elif self.total_runs < first_innings_runs:
            self.winner = self._get_name(self.team1)
            self.result = f"{self._get_name(self.team1)} won by {first_innings_runs - self.total_runs} runs"
        else:
            self.result = "Match Tied"
        
        self.match_ended = True
        return self._get_match_result()
    
    def simulate_odi_match(self):
        """Simulate an ODI match"""
        return self.simulate_t20_match()  # Same structure, different settings
    
    def simulate_test_match(self):
        """Simulate a Test match with 4 innings"""
        # Select XIs for first innings
        self.batting_xi = self.auto_select_xi(self.team1)
        self.bowling_xi = self.auto_select_xi(self.team2)
        self._init_match_stats()
        
        if len(self.batting_xi) >= 2:
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
        
        bowling_xi = [p for p in self.bowling_xi if self._get_attr(p, 'bowling', 0) > 0]
        bowlers = sorted(bowling_xi, key=lambda x: self._get_attr(x, 'bowling', 0), reverse=True)
        if bowlers:
            self.current_bowler = bowlers[0]
        
        # Innings 1
        self.simulate_innings()
        self._start_next_innings()
        
        # Innings 2
        self.simulate_innings()
        
        # Check for follow-on
        if self._check_follow_on():
            # Team 2 bats again
            self._start_next_innings()
            self.simulate_innings()
            
            # Innings 4 if needed
            if self.current_innings == 3:
                self._start_next_innings()
                # Check if there's a target
                if len(self.innings_data) >= 3:
                    team1_total = self.innings_data[0]['runs'] + self.innings_data[2]['runs']
                    team2_total = self.innings_data[1]['runs']
                    target = team1_total - team2_total
                    if target > 0:
                        self.target = target
                self.simulate_innings()
        else:
            # Normal sequence: Innings 3 and 4
            self._start_next_innings()
            self.simulate_innings()
            
            if self.current_innings < 4:
                self._start_next_innings()
                if len(self.innings_data) >= 3:
                    team1_total = self.innings_data[0]['runs'] + self.innings_data[2]['runs']
                    team2_total = self.innings_data[1]['runs']
                    target = team1_total - team2_total
                    if target > 0:
                        self.target = target
                self.simulate_innings()
        
        # Save final innings data
        self._save_innings_data()
        
        # Calculate result
        return self._calculate_test_result()
    
    def _calculate_test_result(self):
        """Calculate Test match result"""
        if len(self.innings_data) < 4:
            self.result = "Match Drawn"
            return self._get_match_result()
        
        team1_total = self.innings_data[0]['runs'] + self.innings_data[2]['runs']
        team2_total = self.innings_data[1]['runs'] + self.innings_data[3]['runs']
        
        if team1_total > team2_total:
            margin = team1_total - team2_total
            self.winner = self._get_name(self.team1)
            self.result = f"{self._get_name(self.team1)} won by {margin} runs"
        elif team2_total > team1_total:
            wickets_lost = self.innings_data[3]['wickets']
            wickets_left = max(1, 10 - wickets_lost)
            self.winner = self._get_name(self.team2)
            self.result = f"{self._get_name(self.team2)} won by {wickets_left} wickets"
        else:
            self.result = "Match Drawn"
        
        self.match_ended = True
        return self._get_match_result()
    
    def _get_match_result(self):
        """Get match result dictionary"""
        return {
            'result': self.result,
            'winner': self.winner,
            'innings_data': self.innings_data,
            'match_stats': self.match_stats
        }
    
    def simulate_match(self):
        """Main entry point to simulate match - dispatches to format-specific method"""
        if self.match_format == 'Test':
            return self.simulate_test_match()
        elif self.match_format == 'ODI':
            return self.simulate_odi_match()
        else:
            return self.simulate_t20_match()
    
    def simulate(self):
        """
        Simulate match and return winner team (for game engine compatibility).
        Also sets self.margin for access after simulation.
        """
        result = self.simulate_match()
        
        # Determine winner team object
        winner_name = result.get('winner')
        if winner_name == self._get_name(self.team1):
            winner = self.team1
        elif winner_name == self._get_name(self.team2):
            winner = self.team2
        else:
            winner = None  # Draw
        
        # Set margin for game engine access
        if winner:
            result_str = result.get('result', '')
            if 'runs' in result_str.lower():
                # Extract run margin from result string
                try:
                    parts = result_str.split('by ')
                    if len(parts) > 1:
                        margin_part = parts[1].split(' ')[0]
                        self.margin = f"{margin_part} runs"
                    else:
                        self.margin = "won"
                except:
                    self.margin = "won"
            else:
                # Wicket margin
                try:
                    parts = result_str.split('by ')
                    if len(parts) > 1:
                        margin_part = parts[1].split(' ')[0]
                        self.margin = f"{margin_part} wickets"
                    else:
                        self.margin = "won"
                except:
                    self.margin = "won"
        else:
            self.margin = "Match Tied"
        
        return winner
    
    def get_scorecard(self):
        """Get scorecard in format expected by game engine and UI"""
        # Always return at least 2 innings for game engine compatibility
        if not self.innings_data or len(self.innings_data) < 2:
            # Return default innings if simulation didn't complete properly
            pitch_conditions = {'pitch_pace': getattr(self, 'pitch_pace', 5), 'pitch_bounce': getattr(self, 'pitch_bounce', 5), 'pitch_spin': getattr(self, 'pitch_spin', 5)}
            try:
                from cricket_manager.systems.gameplay_features import get_pitch_report_text
                pitch_report = get_pitch_report_text(pitch_conditions)
            except Exception:
                pitch_report = "Pitch: Good for batting."
            return {
                'team1': self._get_name(self.team1),
                'team2': self._get_name(self.team2),
                'format': self.match_format,
                'winner': self.winner if hasattr(self, 'winner') else None,
                'margin': getattr(self, 'margin', ''),
                'pitch_report': pitch_report,
                'innings': [
                    {
                        'batting_team': self._get_name(self.team1),
                        'bowling_team': self._get_name(self.team2),
                        'total_runs': getattr(self, 'total_runs', 0),
                        'wickets_fallen': getattr(self, 'total_wickets', 0),
                        'overs': getattr(self, 'total_overs', 0),
                        'batting_card': [],
                        'bowling_card': []
                    },
                    {
                        'batting_team': self._get_name(self.team2),
                        'bowling_team': self._get_name(self.team1),
                        'total_runs': 0,
                        'wickets_fallen': 0,
                        'overs': 0,
                        'batting_card': [],
                        'bowling_card': []
                    }
                ],
                'match_stats': self.match_stats
            }
        
        # Convert to game engine expected format
        # Note: match_stats in innings_data is CUMULATIVE, so we need to calculate per-innings stats
        innings_list = []
        prev_stats = {}  # Track previous innings cumulative stats
        
        for idx, inn in enumerate(self.innings_data):
            # Get cumulative match_stats at end of this innings
            curr_stats = inn.get('match_stats', {})
            batting_team = inn['batting_team']
            bowling_team = inn['bowling_team']
            batting_xi = inn.get('batting_xi', [])
            
            # Build batting_card and bowling_card from per-innings stats
            batting_card = []
            bowling_card = []
            batters_who_batted = set()
            
            for player_name, stats in curr_stats.items():
                # Get previous cumulative stats for this player
                prev_player_stats = prev_stats.get(player_name, {
                    'batting': {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dismissal': None},
                    'bowling': {'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0}
                })
                
                # Calculate per-innings stats by subtracting previous cumulative
                batting_stats = stats.get('batting', {})
                bowling_stats = stats.get('bowling', {})
                prev_batting = prev_player_stats.get('batting', {})
                prev_bowling = prev_player_stats.get('bowling', {})
                
                # Per-innings batting stats
                inn_runs = batting_stats.get('runs', 0) - prev_batting.get('runs', 0)
                inn_balls = batting_stats.get('balls', 0) - prev_batting.get('balls', 0)
                inn_fours = batting_stats.get('fours', 0) - prev_batting.get('fours', 0)
                inn_sixes = batting_stats.get('sixes', 0) - prev_batting.get('sixes', 0)
                
                # Check if player was dismissed in THIS innings (dismissal changed from None to something)
                curr_dismissal = batting_stats.get('dismissal')
                prev_dismissal = prev_batting.get('dismissal')
                inn_dismissal = curr_dismissal if curr_dismissal != prev_dismissal else None
                
                # Add to batting card if player batted in this innings
                if inn_balls > 0 or inn_runs > 0 or inn_dismissal:
                    batters_who_batted.add(player_name)
                    batting_card.append({
                        'name': player_name,
                        'runs': inn_runs,
                        'balls': inn_balls,
                        'fours': inn_fours,
                        'sixes': inn_sixes,
                        'dismissal': inn_dismissal if inn_dismissal else 'not out',
                        'strike_rate': round((inn_runs / max(1, inn_balls)) * 100, 2)
                    })
                
                # Per-innings bowling stats
                inn_bowl_balls = bowling_stats.get('balls', 0) - prev_bowling.get('balls', 0)
                inn_bowl_runs = bowling_stats.get('runs', 0) - prev_bowling.get('runs', 0)
                inn_wickets = bowling_stats.get('wickets', 0) - prev_bowling.get('wickets', 0)
                inn_maidens = bowling_stats.get('maidens', 0) - prev_bowling.get('maidens', 0)
                
                # Add to bowling card if player bowled in this innings
                if inn_bowl_balls > 0:
                    overs = int(inn_bowl_balls / 6) + (inn_bowl_balls % 6) / 10
                    bowling_card.append({
                        'name': player_name,
                        'overs': round(overs, 1),
                        'balls': inn_bowl_balls,
                        'maidens': inn_maidens,
                        'runs': inn_bowl_runs,
                        'wickets': inn_wickets,
                        'economy': round((inn_bowl_runs * 6) / max(1, inn_bowl_balls), 2)
                    })
            
            # Sort batting card by runs (highest first)
            batting_card.sort(key=lambda x: -x['runs'])
            
            # Add "did not bat" entries for players in batting XI who didn't bat
            for player_name in batting_xi:
                if player_name not in batters_who_batted:
                    batting_card.append({
                        'name': player_name,
                        'runs': 0,
                        'balls': 0,
                        'fours': 0,
                        'sixes': 0,
                        'dismissal': 'did not bat',
                        'strike_rate': 0
                    })
            
            # Sort bowling card by wickets taken, then by runs conceded
            bowling_card.sort(key=lambda x: (-x['wickets'], x['runs']))
            
            innings_list.append({
                'batting_team': batting_team,
                'bowling_team': bowling_team,
                'total_runs': inn['runs'],
                'wickets_fallen': inn['wickets'],
                'overs': inn['overs'],
                'batting_card': batting_card,
                'bowling_card': bowling_card,
                'match_stats': curr_stats,
                'fow': inn.get('fow', [])
            })
            
            # Update prev_stats for next innings calculation
            prev_stats = copy.deepcopy(curr_stats)
        
        pitch_conditions = {'pitch_pace': getattr(self, 'pitch_pace', 5), 'pitch_bounce': getattr(self, 'pitch_bounce', 5), 'pitch_spin': getattr(self, 'pitch_spin', 5)}
        try:
            from cricket_manager.systems.gameplay_features import get_pitch_report_text
            pitch_report = get_pitch_report_text(pitch_conditions)
        except Exception:
            pitch_report = "Pitch: Good for batting."
        return {
            'team1': self._get_name(self.team1),
            'team2': self._get_name(self.team2),
            'format': self.match_format,
            'winner': self.winner if hasattr(self, 'winner') else None,
            'margin': getattr(self, 'margin', ''),
            'innings': innings_list,
            'match_stats': self.match_stats,
            'pitch_report': pitch_report
        }

