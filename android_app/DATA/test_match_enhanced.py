"""
Enhanced Test Match Simulator - Professional Version
Features: Auto pitch/weather, innings tabs, lead/trail display, stats update
"""

import random
import copy
import tkinter as tk
from tkinter import ttk, messagebox
from cricket_manager.core.statistics_manager import StatisticsManager

# Game theme colors - Professional Cricket Manager Theme (Dark Green)
BG_COLOR = "#1B4332"  # Dark green
FG_COLOR = "#D8F3DC"  # Light green-gray
ACCENT_COLOR = "#52B788"  # Medium green
BUTTON_COLOR = "#2D6A4F"  # Darker green
SUCCESS_COLOR = "#74C69D"  # Light green


class TestMatchSimulator:
    """Enhanced Test Match Simulator with professional features"""
    
    def __init__(self, team1, team2, parent_app=None, simulation_adjustments=None, pitch_conditions=None):
        self.team1 = team1
        self.team2 = team2
        self.parent_app = parent_app
        self._fixture_pitch_conditions = pitch_conditions  # From fixture (host country)
        
        # User simulation adjustments from settings (-100 to +100)
        self.simulation_adjustments = simulation_adjustments or {
            'dot_adj': 0,
            'boundary_adj': 0,
            'wicket_adj': 0
        }
        
        # Initialize match_stats for StatisticsManager compatibility
        self.match_stats = {}
        
        # Match state
        self.current_innings = 1
        self.current_day = 1
        self.current_session = 1
        self.ball_age = 0
        self.overs_in_session = 0
        self.follow_on_enforced = False
        
        # Current innings state
        self.batting_team = None
        self.bowling_team = None
        self.current_score = 0
        self.current_wickets = 0
        self.current_overs = 0
        self.current_balls = 0
        
        # Players
        self.striker = None
        self.non_striker = None
        self.next_batsman_index = 2
        self.current_bowler = None
        self.bowler_overs = {}
        
        # Stats
        self.batting_stats = {}
        self.bowling_stats = {}
        self.fow = []
        self.batter_balls = {}
        self.batter_runs = {}
        self.bowler_runs = {}
        self.bowler_balls = {}
        
        # All innings data
        self.innings_data = []
        
        # Result
        self.result = None
        self.winner = None
        self.match_ended = False
        
        # If fixture provides pitch conditions (host country based), use those as base
        # and infer a matching pitch_type for deterioration logic.
        if self._fixture_pitch_conditions:
            self.base_pitch_pace = self._fixture_pitch_conditions.get('pitch_pace', random.randint(5, 7))
            self.base_pitch_spin = self._fixture_pitch_conditions.get('pitch_spin', random.randint(5, 7))
            self.base_pitch_bounce = self._fixture_pitch_conditions.get('pitch_bounce', random.randint(5, 7))
            # Infer pitch type from the provided values for deterioration
            if self.base_pitch_spin >= 7:
                pitch_type = 'dustbowl'
            elif self.base_pitch_pace >= 7 and self.base_pitch_bounce >= 7:
                pitch_type = random.choice(['green_seamer', 'green_top'])
            elif self.base_pitch_bounce >= 8:
                pitch_type = 'bouncy'
            elif self.base_pitch_pace <= 4 and self.base_pitch_spin <= 4:
                pitch_type = 'flat_road'
            else:
                pitch_type = 'balanced'
        else:
            # Generate pitch type randomly
            pitch_type = random.choice(['green_seamer', 'green_top', 'dustbowl', 'flat_road', 'bouncy', 'balanced'])
            
            if pitch_type == 'green_seamer':
                self.base_pitch_pace = random.randint(7, 10)
                self.base_pitch_spin = random.randint(2, 5)
                self.base_pitch_bounce = random.randint(6, 9)
            elif pitch_type == 'green_top':
                self.base_pitch_pace = random.randint(8, 10)
                self.base_pitch_spin = random.randint(1, 3)
                self.base_pitch_bounce = random.randint(7, 9)
            elif pitch_type == 'dustbowl':
                self.base_pitch_pace = random.randint(2, 5)
                self.base_pitch_spin = random.randint(7, 10)
                self.base_pitch_bounce = random.randint(3, 6)
            elif pitch_type == 'flat_road':
                self.base_pitch_pace = random.randint(2, 4)
                self.base_pitch_spin = random.randint(2, 4)
                self.base_pitch_bounce = random.randint(2, 4)
            elif pitch_type == 'bouncy':
                self.base_pitch_pace = random.randint(5, 7)
                self.base_pitch_spin = random.randint(4, 6)
                self.base_pitch_bounce = random.randint(8, 10)
            else:  # balanced
                self.base_pitch_pace = random.randint(5, 7)
                self.base_pitch_spin = random.randint(5, 7)
                self.base_pitch_bounce = random.randint(5, 7)
        
        self.pitch_type = pitch_type  # Store for reference
        self.pitch_pace = self.base_pitch_pace
        self.pitch_spin = self.base_pitch_spin
        self.pitch_bounce = self.base_pitch_bounce
        
        # Weather (changes with session/day)
        self.weather_options = ['Sunny', 'Cloudy', 'Overcast', 'Humid']
        self.weather = random.choice(self.weather_options)
        
        # GUI
        self.root = None
        self.gui_elements = {}
    
    def get_match_stats_for_result(self):
        """
        Build match_stats dict from innings_data in StatisticsManager format.
        Aggregates batting and bowling across all innings for stats update.
        """
        match_stats = {}
        for inn in self.innings_data:
            for name, s in inn.get('batting_stats', {}).items():
                if name not in match_stats:
                    match_stats[name] = {'batting': {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dismissal': 'Not Out'}, 'bowling': {'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0, 'speeds': []}}
                match_stats[name]['batting']['runs'] += s.get('runs', 0)
                match_stats[name]['batting']['balls'] += s.get('balls', 0)
                match_stats[name]['batting']['fours'] += s.get('fours', 0)
                match_stats[name]['batting']['sixes'] += s.get('sixes', 0)
                if s.get('dismissal') and str(s.get('dismissal', '')).lower() not in ('not out', ''):
                    match_stats[name]['batting']['dismissal'] = s.get('dismissal', 'Not Out')
            for name, s in inn.get('bowling_stats', {}).items():
                if name not in match_stats:
                    match_stats[name] = {'batting': {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dismissal': 'Not Out'}, 'bowling': {'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0, 'speeds': []}}
                match_stats[name]['bowling']['balls'] += s.get('balls', 0)
                match_stats[name]['bowling']['runs'] += s.get('runs', 0)
                match_stats[name]['bowling']['wickets'] += s.get('wickets', 0)
                match_stats[name]['bowling']['maidens'] += s.get('maidens', 0)
        return match_stats
    
    def auto_select_xi(self, team):
        """Auto-select XI with rotation from best 15 players (matches T20 logic)"""
        import random
        
        players = team['players'][:]
        
        # Categorize players by role
        batters = []
        allrounders = []
        bowlers = []
        
        for p in players:
            role = p.get('role', '').lower()
            if 'allrounder' in role or 'all-rounder' in role:
                allrounders.append(p)
            elif 'batter' in role or 'batsman' in role or 'keeper' in role:
                batters.append(p)
            else:
                bowlers.append(p)
        
        print(f"[Test XI] {team['name']}: {len(batters)} batters, {len(allrounders)} allrounders, {len(bowlers)} bowlers")
        
        # Sort by skills to get the best pools
        batters_by_skill = sorted(batters, key=lambda x: x.get('batting', 0), reverse=True)
        allrounders_by_skill = sorted(allrounders, key=lambda x: (x.get('batting', 0) + x.get('bowling', 0))/2, reverse=True)
        bowlers_by_skill = sorted(bowlers, key=lambda x: x.get('bowling', 0), reverse=True)
        
        # ROTATION: Select 5 batters randomly from best 9 available
        best_9_batters = batters_by_skill[:min(9, len(batters_by_skill))]
        selected_batters = random.sample(best_9_batters, min(5, len(best_9_batters)))
        
        # ROTATION: Select 2 allrounders randomly from best 4 available
        best_4_allrounders = allrounders_by_skill[:min(4, len(allrounders_by_skill))]
        selected_allrounders = random.sample(best_4_allrounders, min(2, len(best_4_allrounders)))
        
        # ROTATION: Select 4 bowlers randomly from best 8 available
        best_8_bowlers = bowlers_by_skill[:min(8, len(bowlers_by_skill))]
        selected_bowlers = random.sample(best_8_bowlers, min(4, len(best_8_bowlers)))
        
        # Build initial XI
        xi = selected_batters + selected_allrounders + selected_bowlers
        
        print(f"[Test XI] Random selection: {len(selected_batters)} batters (from top {len(best_9_batters)}), {len(selected_allrounders)} allrounders (from top {len(best_4_allrounders)}), {len(selected_bowlers)} bowlers (from top {len(best_8_bowlers)})")
        
        # Handle shortages - SIMPLIFIED to always get 11 players
        if len(xi) < 11:
            shortage = 11 - len(xi)
            print(f"[Test XI] Shortage of {shortage} players, filling with best available...")
            remaining_players = [p for p in players if p not in xi]
            
            # Sort remaining by overall skill and take what we need
            remaining_by_overall = sorted(
                remaining_players, 
                key=lambda x: (x.get('batting', 0) + x.get('bowling', 0) + x.get('fielding', 0))/3, 
                reverse=True
            )
            
            # Add players until we have 11
            for i in range(min(shortage, len(remaining_by_overall))):
                xi.append(remaining_by_overall[i])
            
            print(f"[Test XI] Added {min(shortage, len(remaining_by_overall))} players, now have {len(xi)} total")
        
        # Ensure exactly 11 players
        xi = xi[:11]
        
        # Sort XI by batting skill for batting order (best batsmen first)
        xi.sort(key=lambda x: x.get('batting', 0), reverse=True)
        
        # Mark selected players as playing XI
        for i, player in enumerate(xi):
            player['playing_xi'] = True
            player['batting_position'] = i + 1
        
        # Mark non-selected players
        for player in players:
            if player not in xi:
                player['playing_xi'] = False
        
        xi_names = [f"{p['name']} ({p['role']})" for p in xi]
        print(f"[Test XI] Final XI for {team['name']}: {', '.join(xi_names)}")
    
    def get_playing_xi(self, team):
        """Get playing XI in batting order"""
        playing = [p for p in team['players'] if p.get('playing_xi', False)]
        # Sort by batting position if available, otherwise by batting skill
        if playing and 'batting_position' in playing[0]:
            playing.sort(key=lambda p: p.get('batting_position', 99))
        else:
            # Fallback: sort by batting skill
            playing.sort(key=lambda p: p.get('batting', 50), reverse=True)
        return playing[:11]
    
    def _update_pitch_conditions(self):
        """Auto-update pitch based on day and pitch type"""
        # Different pitch types deteriorate differently
        if self.current_day == 1:
            self.pitch_pace = self.base_pitch_pace
            self.pitch_spin = self.base_pitch_spin
            self.pitch_bounce = self.base_pitch_bounce
        elif self.current_day == 2:
            if self.pitch_type == 'green_seamer':
                # Green pitch loses pace quickly
                self.pitch_pace = max(1, self.base_pitch_pace - 2)
                self.pitch_spin = min(10, self.base_pitch_spin + 1)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 1)
            elif self.pitch_type == 'green_top':
                # Green top STAYS green, gets bouncier, spin DECREASES
                self.pitch_pace = min(10, self.base_pitch_pace + 1)  # More pace!
                self.pitch_spin = max(1, self.base_pitch_spin - 1)   # Less spin!
                self.pitch_bounce = min(10, self.base_pitch_bounce + 1)  # More bounce!
            elif self.pitch_type == 'dustbowl':
                # Dustbowl gets even more spin
                self.pitch_pace = max(1, self.base_pitch_pace - 1)
                self.pitch_spin = min(10, self.base_pitch_spin + 2)
                self.pitch_bounce = self.base_pitch_bounce
            elif self.pitch_type == 'flat_road':
                # Flat pitch stays flat longer
                self.pitch_pace = self.base_pitch_pace
                self.pitch_spin = min(10, self.base_pitch_spin + 1)
                self.pitch_bounce = self.base_pitch_bounce
            else:
                # Standard deterioration
                self.pitch_pace = max(1, self.base_pitch_pace - 1)
                self.pitch_spin = min(10, self.base_pitch_spin + 1)
                self.pitch_bounce = self.base_pitch_bounce
        elif self.current_day == 3:
            if self.pitch_type == 'green_seamer':
                self.pitch_pace = max(1, self.base_pitch_pace - 3)
                self.pitch_spin = min(10, self.base_pitch_spin + 2)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 2)
            elif self.pitch_type == 'green_top':
                # Green top continues to favor pace
                self.pitch_pace = min(10, self.base_pitch_pace + 1)
                self.pitch_spin = max(1, self.base_pitch_spin - 1)
                self.pitch_bounce = min(10, self.base_pitch_bounce + 2)
            elif self.pitch_type == 'dustbowl':
                self.pitch_pace = max(1, self.base_pitch_pace - 1)
                self.pitch_spin = min(10, self.base_pitch_spin + 3)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 1)
            elif self.pitch_type == 'flat_road':
                self.pitch_pace = max(1, self.base_pitch_pace - 1)
                self.pitch_spin = min(10, self.base_pitch_spin + 2)
                self.pitch_bounce = self.base_pitch_bounce
            else:
                self.pitch_pace = max(1, self.base_pitch_pace - 2)
                self.pitch_spin = min(10, self.base_pitch_spin + 2)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 1)
        elif self.current_day >= 4:
            if self.pitch_type == 'green_seamer':
                self.pitch_pace = max(1, self.base_pitch_pace - 4)
                self.pitch_spin = min(10, self.base_pitch_spin + 3)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 3)
            elif self.pitch_type == 'green_top':
                # Green top STAYS fast and bouncy throughout!
                self.pitch_pace = min(10, self.base_pitch_pace + 1)
                self.pitch_spin = max(1, self.base_pitch_spin - 1)
                self.pitch_bounce = min(10, self.base_pitch_bounce + 2)
            elif self.pitch_type == 'dustbowl':
                self.pitch_pace = max(1, self.base_pitch_pace - 2)
                self.pitch_spin = min(10, self.base_pitch_spin + 4)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 2)
            elif self.pitch_type == 'flat_road':
                self.pitch_pace = max(1, self.base_pitch_pace - 2)
                self.pitch_spin = min(10, self.base_pitch_spin + 3)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 1)
            else:
                self.pitch_pace = max(1, self.base_pitch_pace - 3)
                self.pitch_spin = min(10, self.base_pitch_spin + 3)
                self.pitch_bounce = max(1, self.base_pitch_bounce - 2)
    
    def _update_weather(self):
        """Auto-update weather based on session"""
        # Weather can change each session
        if random.random() < 0.3:  # 30% chance of weather change
            self.weather = random.choice(self.weather_options)
    
    def _get_match_situation(self):
        """Get current match situation (lead/trail/target)"""
        if self.current_innings == 1:
            return f"{self.batting_team['name']} batting"
        elif self.current_innings == 2:
            inn1_score = self.innings_data[0]['score']
            if self.current_score > inn1_score:
                lead = self.current_score - inn1_score
                return f"Lead by {lead} runs"
            elif self.current_score < inn1_score:
                trail = inn1_score - self.current_score
                return f"Trail by {trail} runs"
            else:
                return "Scores level"
        elif self.current_innings == 3:
            inn1_score = self.innings_data[0]['score']
            inn2_score = self.innings_data[1]['score']
            if inn1_score > inn2_score:
                lead = (inn1_score - inn2_score) + self.current_score
                return f"Lead by {lead} runs"
            else:
                trail = (inn2_score - inn1_score) - self.current_score
                if trail > 0:
                    return f"Trail by {trail} runs"
                else:
                    return f"Lead by {abs(trail)} runs"
        elif self.current_innings == 4:
            inn1_score = self.innings_data[0]['score']
            inn2_score = self.innings_data[1]['score']
            inn3_score = self.innings_data[2]['score']
            target = (inn1_score + inn3_score) - inn2_score
            needed = target - self.current_score
            if needed > 0:
                return f"Need {needed} runs to win"
            else:
                return f"Target achieved"
        return ""
    
    def initialize_match(self):
        """Initialize match"""
        # DEFENSIVE: Ensure both teams have playing_xi set
        # If no players have playing_xi=True, auto-select
        team1_xi = [p for p in self.team1['players'] if p.get('playing_xi', False)]
        team2_xi = [p for p in self.team2['players'] if p.get('playing_xi', False)]
        
        if len(team1_xi) != 11:
            print(f"[DEFENSIVE] Team1 has {len(team1_xi)} players with playing_xi=True, auto-selecting...")
            self.auto_select_xi(self.team1)
        
        if len(team2_xi) != 11:
            print(f"[DEFENSIVE] Team2 has {len(team2_xi)} players with playing_xi=True, auto-selecting...")
            self.auto_select_xi(self.team2)
        
        self.batting_team = self.team1
        self.bowling_team = self.team2
        self._init_innings_stats()
        
        batting_xi = self.get_playing_xi(self.batting_team)
        self.striker = batting_xi[0]
        self.non_striker = batting_xi[1]
        
        bowling_xi = self.get_playing_xi(self.bowling_team)
        bowlers = sorted(bowling_xi, key=lambda x: x.get('bowling', 0), reverse=True)
        self.current_bowler = bowlers[0]
        self.bowler_overs = {b['name']: 0 for b in bowling_xi}
    
    def _init_innings_stats(self):
        """Initialize stats for current innings"""
        self.batting_stats = {}
        self.bowling_stats = {}
        self.fow = []
        
        for player in self.get_playing_xi(self.batting_team):
            self.batting_stats[player['name']] = {
                'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                'dismissal': 'not out', 'bowler': '', 'sr': 0.0
            }
        
        for player in self.get_playing_xi(self.bowling_team):
            self.bowling_stats[player['name']] = {
                'overs': 0, 'balls': 0, 'maidens': 0, 'runs': 0,
                'wickets': 0, 'economy': 0.0, 'dots': 0, 'wides': 0, 'noballs': 0
            }
    
    def simulate_ball(self):
        """Simulate one ball"""
        if self.match_ended:
            return
        
        probs = self._get_ball_probabilities()
        outcomes = list(probs.keys())
        weights = list(probs.values())
        outcome = random.choices(outcomes, weights=weights, k=1)[0]
        
        if outcome == 'wicket':
            self._handle_wicket()
        elif outcome == 'wide':
            self._handle_wide()
        elif outcome == 'noball':
            self._handle_noball()
        else:
            runs = {'dot': 0, 'single': 1, 'double': 2, 'triple': 3, 'four': 4, 'six': 6}[outcome]
            self._handle_runs(runs)
        
        if outcome != 'wide':
            self.current_balls += 1
            self.ball_age += 1
            self.bowling_stats[self.current_bowler['name']]['balls'] += 1
            
            if self.current_balls == 6:
                self._complete_over()
        
        self._check_session_day()
    
    def _get_ball_probabilities(self):
        """Calculate probabilities - Innings-dependent Test cricket scoring"""
        # Determine which innings we're in
        innings_num = len(self.innings_data) + 1
        
        if innings_num <= 2:
            # First two innings: Fresh pitch, good batting (target 350+ runs)
            base = {
                'dot': 0.55,      # Fewer dots for higher scoring
                'single': 0.26,   # More singles
                'double': 0.08,   # More doubles
                'triple': 0.009,  # More triples
                'four': 0.055,    # More boundaries
                'six': 0.006,     # More sixes
                'wicket': 0.012,  # REDUCED - multipliers will increase this
                'wide': 0.002,    # Very rare
                'noball': 0.001   # Extremely rare
            }
        else:
            # Last two innings: Deteriorating pitch, harder batting (target 240 runs)
            base = {
                'dot': 0.62,      # More dots, harder to score
                'single': 0.23,   # Fewer singles
                'double': 0.07,   # Fewer doubles
                'triple': 0.007,  # Fewer triples
                'four': 0.045,    # Fewer boundaries
                'six': 0.004,     # Fewer sixes
                'wicket': 0.014,  # REDUCED - multipliers will increase this
                'wide': 0.002,    # Very rare
                'noball': 0.001   # Extremely rare
            }
        
        probs = base.copy()
        
        # Skill differential with safety checks
        bat_skill = self.striker.get('batting', 50)
        bowl_skill = self.current_bowler.get('bowling', 50)
        
        # Ensure skills are valid numbers
        if not isinstance(bat_skill, (int, float)) or bat_skill < 0 or bat_skill > 100:
            bat_skill = 50
        if not isinstance(bowl_skill, (int, float)) or bowl_skill < 0 or bowl_skill > 100:
            bowl_skill = 50
        
        skill_diff = (bat_skill - bowl_skill) / 100
        
        probs['dot'] += -skill_diff * 0.12
        probs['single'] += skill_diff * 0.06
        probs['four'] += skill_diff * 0.04
        probs['six'] += skill_diff * 0.01
        probs['wicket'] += -skill_diff * 0.015
        
        # Penalty for low-skilled batsmen (< 45 batting)
        if bat_skill < 45:
            skill_penalty = (45 - bat_skill) / 100  # 0.01 to 0.45 penalty
            probs['wicket'] *= (1.0 + skill_penalty * 2.0)  # Up to 90% more wickets
            probs['dot'] *= (1.0 + skill_penalty * 0.5)     # Up to 22.5% more dots
            probs['four'] *= (1.0 - skill_penalty * 0.5)    # Up to 22.5% fewer boundaries
        
        # Ball age
        if self.ball_age < 20:
            probs['wicket'] *= 1.4
            probs['dot'] *= 1.2
        elif self.ball_age > 60:
            probs['single'] *= 1.3
            probs['wicket'] *= 0.7
        
        # Day effects
        if self.current_day >= 4:
            probs['wicket'] *= 1.25
        
        # Bowler traits from player_traits.py (MAJOR impact)
        bowler_traits = self.current_bowler.get('traits', [])
        for trait in bowler_traits:
            trait_name = trait.get('name', '')
            trait_strength = trait.get('strength', 1)
            multiplier = 1.0 + (trait_strength * 0.12)  # 12% per strength level (1-5 stars)
            
            # Bowling traits
            if trait_name == 'NEW_BALL_LOVER' and self.ball_age < 20:
                probs['wicket'] *= multiplier * 1.8
                probs['dot'] *= multiplier * 1.3
            elif trait_name == 'MISER':
                probs['dot'] *= multiplier * 1.5
                probs['four'] *= 0.6
                probs['six'] *= 0.5
            elif trait_name == 'GOLDEN_ARM':
                probs['wicket'] *= multiplier * 1.5
            elif trait_name == 'DEATH_BOWLER':
                probs['wicket'] *= multiplier * 1.3
                probs['dot'] *= multiplier * 1.2
            elif trait_name == 'BIG_TURN' and self.pitch_spin >= 6:
                probs['wicket'] *= multiplier * 1.8
                probs['dot'] *= multiplier * 1.4
                probs['four'] *= 0.6
            elif trait_name == 'PACE_DEMON':
                probs['wicket'] *= multiplier * 1.6
                probs['four'] *= 0.7
            elif trait_name == 'GREEN_TRACK_BULLY' and self.pitch_pace >= 7:
                probs['wicket'] *= multiplier * 2.0
                probs['dot'] *= multiplier * 1.5
                probs['four'] *= 0.5
            elif trait_name == 'DUSTY_MAN' and self.pitch_spin >= 7:
                probs['wicket'] *= multiplier * 2.2
                probs['dot'] *= multiplier * 1.6
                probs['four'] *= 0.4
            elif trait_name == 'PITCH_OUT_OF_EQUATION':
                probs['wicket'] *= multiplier * 1.4
                probs['dot'] *= multiplier * 1.3
            elif trait_name == 'REVERSE_SWING_EXPERT' and self.ball_age > 60:
                probs['wicket'] *= multiplier * 1.8
                probs['dot'] *= multiplier * 1.4
        
        # Pitch conditions (MAJOR impact - both high and low values)
        bowling_trait = self.current_bowler.get('bowling_trait', '').lower()
        
        # Pace-friendly pitch (7+) - MAJOR wicket boost
        if self.pitch_pace >= 7:
            if 'fast' in bowling_trait or 'seam' in bowling_trait or 'pace' in bowling_trait:
                probs['wicket'] *= 1.8  # 80% more wickets for pace bowlers
                probs['dot'] *= 1.4     # 40% more dots
                probs['four'] *= 0.7    # Fewer boundaries
            else:
                probs['wicket'] *= 1.3  # Even non-pace bowlers benefit
        # Batting-friendly for pace (1-5) - FEWER wickets
        elif self.pitch_pace <= 5:
            if 'fast' in bowling_trait or 'seam' in bowling_trait or 'pace' in bowling_trait:
                probs['wicket'] *= 0.6  # 40% fewer wickets for pace bowlers
                probs['four'] *= 1.3    # More boundaries
                probs['six'] *= 1.4     # More sixes
        
        # Spin-friendly pitch (7+) - MAJOR wicket boost
        if self.pitch_spin >= 7:
            if 'spin' in bowling_trait or 'leg' in bowling_trait or 'off' in bowling_trait:
                probs['wicket'] *= 2.0  # Double wickets for spinners!
                probs['dot'] *= 1.5     # 50% more dots
                probs['four'] *= 0.6    # Much fewer boundaries
            else:
                probs['wicket'] *= 1.2  # Even non-spinners benefit slightly
        # Batting-friendly for spin (1-5) - FEWER wickets
        elif self.pitch_spin <= 5:
            if 'spin' in bowling_trait or 'leg' in bowling_trait or 'off' in bowling_trait:
                probs['wicket'] *= 0.6  # 40% fewer wickets for spinners
                probs['four'] *= 1.3    # More boundaries
                probs['six'] *= 1.4     # More sixes
        
        # High bounce (7+) - helps all bowlers
        if self.pitch_bounce >= 7:
            probs['wicket'] *= 1.5      # 50% more wickets
            probs['dot'] *= 1.3         # 30% more dots
            probs['four'] *= 0.8        # Fewer boundaries
        # Low bounce (1-5) - batting paradise
        elif self.pitch_bounce <= 5:
            probs['wicket'] *= 0.7      # 30% fewer wickets
            probs['four'] *= 1.2        # More boundaries
            probs['six'] *= 1.3         # More sixes
        
        # Weather effects
        if self.weather == 'Overcast' and 'swing' in bowling_trait and self.ball_age < 25:
            probs['wicket'] *= 1.5
            probs['dot'] *= 1.3
        elif self.weather == 'Sunny' and 'spin' in bowling_trait and self.current_day >= 3:
            probs['wicket'] *= 1.4
            probs['dot'] *= 1.2
        
        # Player traits from player_traits.py (MAJOR impact)
        player_traits = self.striker.get('traits', [])
        for trait in player_traits:
            trait_name = trait.get('name', '')
            trait_strength = trait.get('strength', 1)
            multiplier = 1.0 + (trait_strength * 0.12)  # 12% per strength level (1-5 stars)
            
            # Batting traits
            if trait_name == 'POWER_OPENER':
                probs['four'] *= multiplier * 1.5
                probs['six'] *= multiplier * 2.0
                probs['dot'] *= 0.7
            elif trait_name == 'SPIN_BASHER' and 'spin' in self.current_bowler.get('bowling_trait', '').lower():
                probs['four'] *= multiplier * 1.8
                probs['six'] *= multiplier * 2.5
                probs['wicket'] *= 0.7
            elif trait_name == 'DEMOLISHER_OF_PACE' and 'fast' in self.current_bowler.get('bowling_trait', '').lower():
                probs['four'] *= multiplier * 1.8
                probs['six'] *= multiplier * 2.0
            elif trait_name == 'FINISHER':
                probs['four'] *= multiplier * 1.5
                probs['six'] *= multiplier * 1.8
                probs['wicket'] *= 0.8
            elif trait_name == 'MR_WALL':
                probs['dot'] *= multiplier * 1.3
                probs['single'] *= multiplier * 1.3
                probs['wicket'] *= 0.6
            elif trait_name == 'CHEEKY_BAT':
                probs['dot'] *= 0.6
                probs['single'] *= multiplier * 1.5
                probs['double'] *= multiplier * 1.5
            elif trait_name == 'CONSOLIDATOR':
                probs['dot'] *= multiplier * 1.4
                probs['single'] *= multiplier * 1.3
                probs['wicket'] *= 0.7
            elif trait_name == 'GREAT_TECHNIQUE' and self.pitch_pace >= 7:
                probs['wicket'] *= 0.6
                probs['dot'] *= multiplier * 1.2
            elif trait_name == 'PRESENCE_OF_MIND' and self.pitch_spin >= 7:
                probs['wicket'] *= 0.6
                probs['single'] *= multiplier * 1.3
            elif trait_name == 'HAIRY_MONSTER' and (self.pitch_pace >= 7 or self.pitch_spin >= 7):
                probs['four'] *= multiplier * 1.5
                probs['wicket'] *= 0.7
            elif trait_name == 'GOOD_AGAINST_MOVEMENT' and self.pitch_pace >= 7:
                probs['wicket'] *= 0.5
                probs['four'] *= multiplier * 1.3
            elif trait_name == 'GOOD_AGAINST_SPIN' and self.pitch_spin >= 7:
                probs['wicket'] *= 0.5
                probs['four'] *= multiplier * 1.3
            elif trait_name == 'GOOD_AGAINST_BOUNCE' and self.pitch_bounce >= 7:
                probs['wicket'] *= 0.6
            elif trait_name == 'NERVOUS_BATTER' and self.current_overs < 10:
                probs['wicket'] *= 1.8
                probs['dot'] *= 1.3
            # --- Test-specific youth negative batting traits ---
            elif trait_name == 'TEST_NEW_BALL_BUNNY' and self.current_overs < 20:
                neg_effect = 1.0 - (trait_strength * 0.16)
                probs['wicket'] *= (2.0 - neg_effect)
                probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
            elif trait_name == 'TEST_POOR_CONCENTRATION':
                batter_name = self.striker.get('name', '')
                b_runs = self.batter_runs.get(batter_name, 0) if hasattr(self, 'batter_runs') else 0
                if 30 <= b_runs <= 70:
                    neg_effect = 1.0 - (trait_strength * 0.12)
                    probs['wicket'] *= (2.0 - neg_effect)
            elif trait_name == 'TEST_DAY5_CRUMBLER':
                neg_effect = 1.0 - (trait_strength * 0.14)
                probs['wicket'] *= (2.0 - neg_effect)
                probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
            elif trait_name == 'TEST_SECOND_INNINGS_FLOP' and self.current_innings in (2, 4):
                neg_effect = 1.0 - (trait_strength * 0.12)
                probs['wicket'] *= (2.0 - neg_effect)
                probs['four'] *= neg_effect
            elif trait_name == 'TEST_BOUNCER_VICTIM' and 'fast' in self.current_bowler.get('bowling_trait', '').lower():
                neg_effect = 1.0 - (trait_strength * 0.16)
                probs['wicket'] *= (2.0 - neg_effect)
                probs['dot'] *= (2.0 - neg_effect) * 0.5 + 0.5
        
        # Apply bowler's Test-specific youth negative traits
        bowler_traits = self.current_bowler.get('traits', [])
        for trait in bowler_traits:
            trait_name = trait.get('name', '')
            trait_strength = trait.get('strength', 1)
            
            if trait_name == 'TEST_NO_STAMINA':
                bowler_name = self.current_bowler.get('name', '')
                b_balls = self.bowler_balls.get(bowler_name, 0) if hasattr(self, 'bowler_balls') else 0
                if b_balls > 30:
                    neg_effect = 1.0 - (trait_strength * 0.14)
                    probs['four'] *= (2.0 - neg_effect)
                    probs['wicket'] *= neg_effect
            elif trait_name == 'TEST_FLAT_PITCH_PASSENGER':
                neg_effect = 1.0 - (trait_strength * 0.14)
                probs['four'] *= (2.0 - neg_effect)
                probs['six'] *= (2.0 - neg_effect) * 0.5 + 0.5
                probs['wicket'] *= neg_effect
            elif trait_name == 'TEST_REVERSE_SWING_HOPELESS' and self.current_overs >= 30:
                neg_effect = 1.0 - (trait_strength * 0.12)
                probs['four'] *= (2.0 - neg_effect)
                probs['wicket'] *= neg_effect
            elif trait_name == 'TEST_DAY5_TOOTHLESS':
                neg_effect = 1.0 - (trait_strength * 0.14)
                probs['four'] *= (2.0 - neg_effect)
                probs['wicket'] *= neg_effect
            elif trait_name == 'TEST_SPELL_BREAKER':
                bowler_name = self.current_bowler.get('name', '')
                b_balls = self.bowler_balls.get(bowler_name, 0) if hasattr(self, 'bowler_balls') else 0
                if b_balls > 18:
                    neg_effect = 1.0 - (trait_strength * 0.10)
                    probs['four'] *= (2.0 - neg_effect)
                    probs['wicket'] *= neg_effect
        
        # Elite batsmen (80+) - scoring boost + 4% wicket increase for Test realism
        if bat_skill >= 80:
            probs['wicket'] *= 0.90 * 1.04
            probs['single'] *= 1.06
            probs['double'] *= 1.06
            probs['four'] *= 1.06
            probs['six'] *= 1.06
            probs['dot'] *= 0.94
            
            # Super elite batsmen (89+) - additional 4% boost to scoring, -4% dismissal
            if bat_skill >= 89:
                probs['single'] *= 1.04
                probs['double'] *= 1.04
                probs['four'] *= 1.04
                probs['six'] *= 1.04
                probs['wicket'] *= 0.96
                probs['dot'] *= 0.96
        # Good batters (60-79) - minor scoring boost + 4% wicket increase for Test realism
        elif bat_skill >= 60:
            probs['wicket'] *= 0.90 * 1.04
            probs['single'] *= 1.04
            probs['double'] *= 1.04
            probs['dot'] *= 0.96
        
        # Apply user simulation adjustments from settings (-100 to +100)
        if hasattr(self, 'simulation_adjustments') and self.simulation_adjustments:
            dot_adj = self.simulation_adjustments.get('dot_adj', 0) / 100.0
            boundary_adj = self.simulation_adjustments.get('boundary_adj', 0) / 100.0
            wicket_adj = self.simulation_adjustments.get('wicket_adj', 0) / 100.0
            
            probs['dot'] *= (1.0 + dot_adj)
            probs['four'] *= (1.0 + boundary_adj)
            probs['six'] *= (1.0 + boundary_adj)
            probs['wicket'] *= (1.0 + wicket_adj)
            
            # Ensure no negative probabilities
            for key in probs:
                probs[key] = max(0.001, probs[key])
        
        # First normalize to ensure probabilities sum to 1.0
        total = sum(probs.values())
        probs = {k: max(0.001, v/total) for k, v in probs.items()}
        
        # THEN cap wicket probability AFTER normalization
        # Maximum 2.2% for realistic Test cricket (prevents collapses)
        # Minimum 1.2% to prevent runaway scores
        if probs['wicket'] > 0.022:
            excess = probs['wicket'] - 0.022
            probs['wicket'] = 0.022
            # Redistribute excess to dots
            probs['dot'] += excess
        elif probs['wicket'] < 0.012:
            deficit = 0.012 - probs['wicket']
            probs['wicket'] = 0.012
            # Take from dots
            probs['dot'] = max(0.001, probs['dot'] - deficit)
        
        return probs
    
    def _handle_runs(self, runs):
        """Handle runs"""
        self.current_score += runs
        self.batting_stats[self.striker['name']]['runs'] += runs
        self.batting_stats[self.striker['name']]['balls'] += 1
        self.batter_runs[self.striker['name']] = self.batter_runs.get(self.striker['name'], 0) + runs
        self.batter_balls[self.striker['name']] = self.batter_balls.get(self.striker['name'], 0) + 1
        
        if runs == 4:
            self.batting_stats[self.striker['name']]['fours'] += 1
        elif runs == 6:
            self.batting_stats[self.striker['name']]['sixes'] += 1
        elif runs == 0:
            self.bowling_stats[self.current_bowler['name']]['dots'] += 1
        
        self.bowling_stats[self.current_bowler['name']]['runs'] += runs
        self.bowler_runs[self.current_bowler['name']] = self.bowler_runs.get(self.current_bowler['name'], 0) + runs
        self.bowler_balls[self.current_bowler['name']] = self.bowler_balls.get(self.current_bowler['name'], 0) + 1
        
        if runs % 2 == 1:
            self.striker, self.non_striker = self.non_striker, self.striker
        
        # Check if target achieved in 4th innings
        if self.current_innings == 4:
            self._check_target_achieved()
    
    def _handle_wicket(self):
        """Handle wicket"""
        self.current_wickets += 1
        self.batting_stats[self.striker['name']]['balls'] += 1
        self.batter_balls[self.striker['name']] = self.batter_balls.get(self.striker['name'], 0) + 1
        self.batting_stats[self.striker['name']]['dismissal'] = f"b {self.current_bowler['name']}"
        self.batting_stats[self.striker['name']]['bowler'] = self.current_bowler['name']
        self.bowling_stats[self.current_bowler['name']]['wickets'] += 1
        
        self.fow.append({
            'wicket': self.current_wickets,
            'score': self.current_score,
            'batsman': self.striker['name'],
            'overs': f"{self.current_overs}.{self.current_balls}"
        })
        
        if self.current_wickets >= 10:
            self._end_innings()
            return
        
        batting_xi = self.get_playing_xi(self.batting_team)
        if self.next_batsman_index < len(batting_xi):
            self.striker = batting_xi[self.next_batsman_index]
            self.next_batsman_index += 1
    
    def _handle_wide(self):
        """Handle wide"""
        self.current_score += 1
        self.bowling_stats[self.current_bowler['name']]['runs'] += 1
        self.bowling_stats[self.current_bowler['name']]['wides'] += 1
    
    def _handle_noball(self):
        """Handle no ball"""
        runs = random.choice([0, 1, 2, 4])
        self.current_score += runs + 1
        self.batting_stats[self.striker['name']]['runs'] += runs
        self.bowling_stats[self.current_bowler['name']]['runs'] += runs + 1
        self.bowling_stats[self.current_bowler['name']]['noballs'] += 1
        
        if runs % 2 == 1:
            self.striker, self.non_striker = self.non_striker, self.striker
    
    def _complete_over(self):
        """Complete over"""
        self.current_overs += 1
        self.current_balls = 0
        self.overs_in_session += 1
        
        self.bowling_stats[self.current_bowler['name']]['overs'] += 1
        
        if self.bowling_stats[self.current_bowler['name']]['dots'] == 6:
            self.bowling_stats[self.current_bowler['name']]['maidens'] += 1
        
        self.bowling_stats[self.current_bowler['name']]['dots'] = 0
        self.striker, self.non_striker = self.non_striker, self.striker
        self._change_bowler()
        
        if self.current_overs % 80 == 0:
            self.ball_age = 0
        
        # Check for declaration after each over
        self._check_declaration()
    
    def _change_bowler(self):
        """Change bowler"""
        bowling_xi = self.get_playing_xi(self.bowling_team)
        bowlers = sorted(bowling_xi, key=lambda x: x.get('bowling', 0), reverse=True)[:6]
        available = [b for b in bowlers if b['name'] != self.current_bowler['name']]
        
        if available:
            next_bowler = min(available, key=lambda x: self.bowler_overs.get(x['name'], 0))
            self.current_bowler = next_bowler
            self.bowler_overs[next_bowler['name']] = self.bowler_overs.get(next_bowler['name'], 0) + 1
    
    def _check_declaration(self):
        """Check if team should declare"""
        # Only check in innings 1 and 3 (not when chasing)
        if self.current_innings not in [1, 3]:
            return
        
        # Declaration Rule 1: Score 520+ runs
        if self.current_score >= 520:
            print(f"[Declaration] {self.batting_team['name']} declares at {self.current_score}/{self.current_wickets}")
            self._end_innings()
            return
        
        # Declaration Rule 2: Lead by 380+ runs (only in innings 3)
        if self.current_innings == 3 and len(self.innings_data) >= 2:
            team1_total = self.innings_data[0]['score']
            team2_total = self.innings_data[1]['score']
            current_lead = (team1_total - team2_total) + self.current_score
            
            if current_lead >= 380:
                print(f"[Declaration] {self.batting_team['name']} declares with lead of {current_lead} runs")
                self._end_innings()
                return
    
    def _check_target_achieved(self):
        """Check if target is achieved in 4th innings"""
        if self.current_innings == 4 and len(self.innings_data) >= 3:
            # Calculate target
            team1_total = self.innings_data[0]['score'] + self.innings_data[2]['score']
            team2_total = self.innings_data[1]['score']
            target = team1_total - team2_total
            
            # Check if target achieved
            if self.current_score > target:
                print(f"[Target Achieved] Score: {self.current_score}, Target: {target}")
                self._end_innings()
    
    def _check_session_day(self):
        """Check session/day progression"""
        # Session ends after ~30 overs
        if self.overs_in_session >= 30:
            self.overs_in_session = 0
            old_session = self.current_session
            old_weather = self.weather
            
            self.current_session += 1
            self._update_weather()  # Weather can change between sessions
            
            # Show weather change notification
            if hasattr(self, 'gui_elements') and old_weather != self.weather:
                self._show_notification(f"Weather changed: {old_weather} → {self.weather}")
            
            if self.current_session > 3:
                self.current_session = 1
                old_day = self.current_day
                self.current_day += 1
                
                old_pitch = (self.pitch_pace, self.pitch_spin, self.pitch_bounce)
                self._update_pitch_conditions()  # Pitch deteriorates each day
                
                # Show pitch change notification
                if hasattr(self, 'gui_elements'):
                    self._show_notification(
                        f"Day {self.current_day} begins\n"
                        f"Pitch: Pace {old_pitch[0]}→{self.pitch_pace}, "
                        f"Spin {old_pitch[1]}→{self.pitch_spin}, "
                        f"Bounce {old_pitch[2]}→{self.pitch_bounce}"
                    )
        
        if self.current_day > 5:
            self._end_match_draw()
    
    def _show_notification(self, message):
        """Show a brief notification about pitch/weather changes"""
        if not hasattr(self, 'root') or not self.root:
            return
        
        # Create notification label if it doesn't exist
        if 'notification_label' not in self.gui_elements:
            self.gui_elements['notification_label'] = ttk.Label(
                self.root,
                text="",
                font=('Arial', 10, 'bold'),
                foreground='green',
                background='lightyellow',
                padding=5
            )
        
        # Show notification
        notif = self.gui_elements['notification_label']
        notif.config(text=message)
        notif.place(relx=0.5, rely=0.1, anchor='center')
        
        # Hide after 3 seconds
        self.root.after(3000, lambda: notif.place_forget())
    
    def _end_innings(self):
        """End innings"""
        for name, stats in self.batting_stats.items():
            if stats['balls'] > 0:
                stats['sr'] = (stats['runs'] * 100) / stats['balls']
        
        for name, stats in self.bowling_stats.items():
            if stats['balls'] > 0:
                stats['economy'] = (stats['runs'] * 6) / stats['balls']
        
        self.innings_data.append({
            'innings_num': self.current_innings,
            'batting_team': self.batting_team['name'],
            'bowling_team': self.bowling_team['name'],
            'score': self.current_score,
            'wickets': self.current_wickets,
            'overs': self.current_overs + (self.current_balls / 6),
            'batting_stats': copy.deepcopy(self.batting_stats),
            'bowling_stats': copy.deepcopy(self.bowling_stats),
            'fow': copy.deepcopy(self.fow)
        })
        
        if self.current_innings >= 4:
            self._calculate_result()
        elif self.current_innings == 2:
            self._check_follow_on()
        else:
            self._start_next_innings()
    
    def _check_follow_on(self):
        """Check follow-on based on real Test cricket rules"""
        team1_score = self.innings_data[0]['score']
        team2_score = self.innings_data[1]['score']
        deficit = team1_score - team2_score
        
        # Real-life follow-on rule: 200 runs deficit
        if deficit >= 200:
            # Factors affecting follow-on decision:
            # 1. Size of lead (bigger lead = more likely)
            # 2. Time remaining (more days = more likely)
            # 3. Pitch condition (bowling-friendly = more likely)
            
            enforce_chance = 0.55  # Base 55% chance (increased from 30%)
            
            # Increase chance based on lead size
            if deficit >= 300:
                enforce_chance += 0.2  # 75% total
            if deficit >= 400:
                enforce_chance += 0.15  # 90% total
            
            # Increase chance if early in match (more time)
            if self.current_day <= 2:
                enforce_chance += 0.15
            
            # Increase chance on bowling-friendly pitch
            if self.pitch_pace >= 7 or self.pitch_spin >= 7 or self.pitch_bounce >= 7:
                enforce_chance += 0.1
            
            # Decrease chance if team is tired (late in day)
            if self.current_session == 3:
                enforce_chance -= 0.05
            
            # Cap at 95%
            enforce_chance = min(0.95, enforce_chance)
            
            if random.random() < enforce_chance:
                self.follow_on_enforced = True
                self.batting_team = self.team2
                self.bowling_team = self.team1
                print(f"[Follow-On] {self.team1['name']} enforces follow-on (deficit: {deficit} runs, chance: {enforce_chance:.0%})")
        
        self._start_next_innings()
    
    def _start_next_innings(self):
        """Start next innings"""
        self.current_innings += 1
        
        if not self.follow_on_enforced or self.current_innings > 3:
            self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        
        self.follow_on_enforced = False
        self.current_score = 0
        self.current_wickets = 0
        self.current_overs = 0
        self.current_balls = 0
        self.next_batsman_index = 2
        
        self._init_innings_stats()
        
        batting_xi = self.get_playing_xi(self.batting_team)
        self.striker = batting_xi[0]
        self.non_striker = batting_xi[1]
        
        bowling_xi = self.get_playing_xi(self.bowling_team)
        bowlers = sorted(bowling_xi, key=lambda x: x.get('bowling', 0), reverse=True)
        self.current_bowler = bowlers[0]
        self.bowler_overs = {b['name']: 0 for b in bowling_xi}
        
        # Auto-switch to new innings tab
        if hasattr(self, 'gui_elements') and 'notebook' in self.gui_elements:
            self.gui_elements['notebook'].select(self.current_innings - 1)
    
    def _calculate_result(self):
        """Calculate result with improved logic"""
        team1_total = self.innings_data[0]['score'] + self.innings_data[2]['score']
        team2_total = self.innings_data[1]['score'] + self.innings_data[3]['score']
        
        if team1_total > team2_total:
            margin = team1_total - team2_total
            self.result = f"{self.team1['name']} won by {margin} runs"
            self.winner = self.team1['name']
        elif team2_total > team1_total:
            # Get actual wickets lost (not remaining)
            wickets_lost = self.innings_data[3]['wickets']
            wickets_left = 10 - wickets_lost
            
            # Ensure wickets_left is not negative or zero when they won
            if wickets_left <= 0:
                wickets_left = 1  # At least 1 wicket remaining
            
            self.result = f"{self.team2['name']} won by {wickets_left} wickets"
            self.winner = self.team2['name']
        else:
            self.result = "Match Drawn"
            self.winner = None
        
        self.match_ended = True
    
    def _end_match_draw(self):
        """End as draw"""
        self.result = "Match Drawn (Time)"
        self.winner = None
        self.match_ended = True
    
    def quick_simulate(self):
        """Quick simulate"""
        self.initialize_match()
        while not self.match_ended:
            self.simulate_ball()
        return {
            'result': self.result,
            'winner': self.winner,
            'innings_data': self.innings_data
        }
    
    # ==================== ENHANCED GUI ====================
    
    def create_gui(self):
        """Create enhanced GUI"""
        self.root = tk.Tk()
        self.root.title(f"TEST: {self.team1['name']} vs {self.team2['name']}")
        
        # Make window large but not full screen to ensure buttons are visible
        self.root.geometry("1400x900+50+50")
        
        # Make modal but don't use topmost to avoid blank window issue
        self.root.grab_set()
        self.root.focus_set()
        self.root.lift()
        
        self.root.configure(bg=BG_COLOR)
        
        # Apply comprehensive styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles using global colors
        style.configure('TLabel', 
                        font=('Arial', 10), 
                        foreground=FG_COLOR, 
                        background=BG_COLOR)
        style.configure('TButton', 
                        font=('Arial', 10, 'bold'), 
                        foreground='white', 
                        background=BUTTON_COLOR,
                        borderwidth=1,
                        relief='raised')
        style.map('TButton', 
                  background=[('active', '#1B5E3F'), ('pressed', '#0F3420')])
        style.configure('TLabelframe.Label', 
                        font=('Arial', 10, 'bold'), 
                        foreground=FG_COLOR, 
                        background=BG_COLOR)
        style.configure('TLabelframe', 
                        foreground=FG_COLOR, 
                        background=BG_COLOR,
                        borderwidth=2,
                        relief='solid')
        style.configure('TEntry', 
                        foreground=FG_COLOR, 
                        background=BUTTON_COLOR,
                        fieldbackground=BUTTON_COLOR)
        style.configure('TCombobox', 
                        foreground=FG_COLOR, 
                        background=BUTTON_COLOR,
                        fieldbackground=BUTTON_COLOR)
        style.configure('Treeview', 
                        font=('Arial', 9), 
                        foreground=FG_COLOR, 
                        background=BUTTON_COLOR,
                        fieldbackground=BUTTON_COLOR)
        style.configure('Treeview.Heading', 
                        font=('Arial', 10, 'bold'), 
                        foreground=FG_COLOR, 
                        background=BG_COLOR)
        style.configure('TNotebook', 
                        background=BG_COLOR,
                        borderwidth=2,
                        relief='solid')
        style.configure('TNotebook.Tab', 
                        background=BUTTON_COLOR,
                        foreground='white',
                        padding=[10, 5])
        style.map('TNotebook.Tab', 
                  background=[('selected', ACCENT_COLOR), ('active', '#1B5E3F')])
        
        # Apply root-level options for all widgets
        self.root.option_add('*background', BG_COLOR)
        self.root.option_add('*foreground', FG_COLOR)
        self.root.option_add('*TLabel*background', BG_COLOR)
        self.root.option_add('*TLabel*foreground', FG_COLOR)
        self.root.option_add('*TButton*background', BUTTON_COLOR)
        self.root.option_add('*TButton*foreground', 'white')
        self.root.option_add('*TFrame*background', BG_COLOR)
        self.root.option_add('*TLabelframe*background', BG_COLOR)
        self.root.option_add('*TLabelframe.Label*background', BG_COLOR)
        self.root.option_add('*TLabelframe.Label*foreground', FG_COLOR)
        self.root.option_add('*TNotebook*background', BG_COLOR)
        self.root.option_add('*TNotebook.Tab*background', BUTTON_COLOR)
        self.root.option_add('*TNotebook.Tab*foreground', 'white')
        
        # Create main frame with explicit styling
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(expand=True, fill='both')
        
        # Title with explicit styling
        title_label = ttk.Label(
            main_frame,
            text=f"TEST MATCH: {self.team1['name']} vs {self.team2['name']}",
            font=('Arial', 16, 'bold'),
            background=BG_COLOR,
            foreground=FG_COLOR
        )
        title_label.pack(pady=5)
        
        # Day/Session/Weather info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=5)
        
        self.gui_elements['day_label'] = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 11, 'bold'),
            background=BG_COLOR,
            foreground=FG_COLOR
        )
        self.gui_elements['day_label'].pack(side='left', padx=10)
        
        self.gui_elements['weather_label'] = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 11),
            background=BG_COLOR,
            foreground=FG_COLOR
        )
        self.gui_elements['weather_label'].pack(side='left', padx=10)
        
        self.gui_elements['pitch_label'] = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 11),
            background=BG_COLOR,
            foreground=FG_COLOR
        )
        self.gui_elements['pitch_label'].pack(side='left', padx=10)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill='both', pady=10)
        
        # Left panel
        self._create_left_panel(content_frame)
        
        # Right panel - Innings tabs
        self._create_innings_tabs(content_frame)
        
        # Controls
        self._create_controls(main_frame)
        
        self.initialize_match()
        self.update_gui()
    
    def _create_left_panel(self, parent):
        """Create left status panel"""
        left_frame = ttk.LabelFrame(parent, text="Match Status", padding=10)
        left_frame.pack(side='left', fill='both', padx=(0, 5))
        
        # Current score
        self.gui_elements['score_label'] = ttk.Label(
            left_frame,
            text="0/0 (0.0)",
            font=('Arial', 22, 'bold'),
            background=BG_COLOR,
            foreground=FG_COLOR
        )
        self.gui_elements['score_label'].pack(pady=10)
        
        # Match situation (lead/trail/target)
        self.gui_elements['situation_label'] = ttk.Label(
            left_frame,
            text="",
            font=('Arial', 12, 'bold'),
            background=BG_COLOR,
            foreground=ACCENT_COLOR
        )
        self.gui_elements['situation_label'].pack(pady=5)
        
        # Innings summary
        self.gui_elements['innings_summary'] = ttk.Label(
            left_frame,
            text="",
            font=('Arial', 9),
            background=BG_COLOR,
            foreground=FG_COLOR,
            justify='left'
        )
        self.gui_elements['innings_summary'].pack(pady=10, fill='x')
        
        # Batsmen
        batsmen_title = ttk.Label(left_frame, text="Batsmen:", font=('Arial', 11, 'bold'), 
                                  background=BG_COLOR, foreground=FG_COLOR)
        batsmen_title.pack(pady=(15, 5))
        self.gui_elements['striker_label'] = ttk.Label(left_frame, text="", font=('Arial', 10),
                                                        background=BG_COLOR, foreground=FG_COLOR)
        self.gui_elements['striker_label'].pack(anchor='w', padx=10)
        self.gui_elements['non_striker_label'] = ttk.Label(left_frame, text="", font=('Arial', 10),
                                                          background=BG_COLOR, foreground=FG_COLOR)
        self.gui_elements['non_striker_label'].pack(anchor='w', padx=10)
        
        # Bowler
        bowler_title = ttk.Label(left_frame, text="Bowler:", font=('Arial', 11, 'bold'),
                                background=BG_COLOR, foreground=FG_COLOR)
        bowler_title.pack(pady=(15, 5))
        self.gui_elements['bowler_label'] = ttk.Label(left_frame, text="", font=('Arial', 10),
                                                      background=BG_COLOR, foreground=FG_COLOR)
        self.gui_elements['bowler_label'].pack(anchor='w', padx=10)
    
    def _create_innings_tabs(self, parent):
        """Create separate tabs for each innings"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', expand=True, fill='both', padx=(5, 0))
        
        # Notebook for innings
        self.gui_elements['notebook'] = ttk.Notebook(right_frame)
        self.gui_elements['notebook'].pack(expand=True, fill='both')
        
        # Create 4 innings tabs
        for i in range(1, 5):
            innings_frame = ttk.Frame(self.gui_elements['notebook'])
            self.gui_elements['notebook'].add(innings_frame, text=f"Innings {i}")
            
            # Create sub-notebook for batting/bowling
            sub_notebook = ttk.Notebook(innings_frame)
            sub_notebook.pack(expand=True, fill='both')
            
            # Batting tab
            bat_frame = ttk.Frame(sub_notebook)
            sub_notebook.add(bat_frame, text="Batting")
            bat_tree = self._create_batting_tree(bat_frame)
            self.gui_elements[f'inn{i}_bat_tree'] = bat_tree
            
            # Bowling tab
            bowl_frame = ttk.Frame(sub_notebook)
            sub_notebook.add(bowl_frame, text="Bowling")
            bowl_tree = self._create_bowling_tree(bowl_frame)
            self.gui_elements[f'inn{i}_bowl_tree'] = bowl_tree
    
    def _create_batting_tree(self, parent):
        """Create batting tree"""
        columns = ('name', 'runs', 'balls', '4s', '6s', 'sr', 'dismissal')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        tree.heading('name', text='Batsman')
        tree.heading('runs', text='Runs')
        tree.heading('balls', text='Balls')
        tree.heading('4s', text='4s')
        tree.heading('6s', text='6s')
        tree.heading('sr', text='SR')
        tree.heading('dismissal', text='Dismissal')
        
        tree.column('name', width=150, anchor='w')
        tree.column('runs', width=60, anchor='center')
        tree.column('balls', width=60, anchor='center')
        tree.column('4s', width=50, anchor='center')
        tree.column('6s', width=50, anchor='center')
        tree.column('sr', width=60, anchor='center')
        tree.column('dismissal', width=200, anchor='w')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        return tree
    
    def _create_bowling_tree(self, parent):
        """Create bowling tree"""
        columns = ('name', 'overs', 'maidens', 'runs', 'wickets', 'economy')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        tree.heading('name', text='Bowler')
        tree.heading('overs', text='Overs')
        tree.heading('maidens', text='Maidens')
        tree.heading('runs', text='Runs')
        tree.heading('wickets', text='Wickets')
        tree.heading('economy', text='Economy')
        
        tree.column('name', width=150, anchor='w')
        tree.column('overs', width=80, anchor='center')
        tree.column('maidens', width=80, anchor='center')
        tree.column('runs', width=80, anchor='center')
        tree.column('wickets', width=80, anchor='center')
        tree.column('economy', width=80, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        return tree
    
    def _create_controls(self, parent):
        """Create control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=10)
        
        buttons = [
            ("Ball", self.gui_simulate_ball),
            ("Over", self.gui_simulate_over),
            ("Session", self.gui_simulate_session),
            ("Day", self.gui_simulate_day),
            ("To End", self.gui_simulate_to_end)
        ]
        
        for text, command in buttons:
            ttk.Button(
                control_frame,
                text=text,
                command=command,
                width=15
            ).pack(side='left', padx=5)
    
    def update_gui(self):
        """Update GUI"""
        if not self.root:
            return
        
        # Day/Session/Weather with color coding
        sessions = {1: "Morning", 2: "Afternoon", 3: "Evening"}
        self.gui_elements['day_label'].config(
            text=f"Day {self.current_day}, {sessions[self.current_session]} | Innings {self.current_innings}/4"
        )
        
        # Weather with color
        weather_colors = {
            'Sunny': 'orange',
            'Cloudy': 'gray',
            'Overcast': 'darkblue',
            'Humid': 'darkgreen'
        }
        self.gui_elements['weather_label'].config(
            text=f"Weather: {self.weather}",
            foreground=weather_colors.get(self.weather, 'black')
        )
        
        # Pitch with indicators
        pitch_text = f"Pitch: Pace {self.pitch_pace}"
        if self.pitch_pace >= 7:
            pitch_text += "↑"
        elif self.pitch_pace <= 3:
            pitch_text += "↓"
        
        pitch_text += f" | Spin {self.pitch_spin}"
        if self.pitch_spin >= 7:
            pitch_text += "↑"
        elif self.pitch_spin <= 3:
            pitch_text += "↓"
        
        pitch_text += f" | Bounce {self.pitch_bounce}"
        if self.pitch_bounce >= 7:
            pitch_text += "↑"
        elif self.pitch_bounce <= 3:
            pitch_text += "↓"
        
        self.gui_elements['pitch_label'].config(text=pitch_text)
        
        # Score with run rate
        overs_display = f"{self.current_overs}.{self.current_balls}"
        total_overs = self.current_overs + (self.current_balls / 6)
        
        # Calculate run rate
        if total_overs > 0:
            run_rate = self.current_score / total_overs
            score_text = f"{self.current_score}/{self.current_wickets} ({overs_display})\nRR: {run_rate:.2f}"
        else:
            score_text = f"{self.current_score}/{self.current_wickets} ({overs_display})\nRR: 0.00"
        
        self.gui_elements['score_label'].config(text=score_text)
        
        # Match situation
        situation = self._get_match_situation()
        self.gui_elements['situation_label'].config(text=situation)
        
        # Innings summary with run rates
        summary_lines = []
        for inn in self.innings_data:
            run_rate = inn['score'] / inn['overs'] if inn['overs'] > 0 else 0
            summary_lines.append(
                f"Innings {inn['innings_num']}: {inn['batting_team']} "
                f"{inn['score']}/{inn['wickets']} ({inn['overs']:.1f} ov, RR: {run_rate:.2f})"
            )
        self.gui_elements['innings_summary'].config(text="\n".join(summary_lines))
        
        # Batsmen
        if self.striker:
            s = self.batting_stats[self.striker['name']]
            self.gui_elements['striker_label'].config(
                text=f"* {self.striker['name']}: {s['runs']}({s['balls']}) [{s['fours']}x4, {s['sixes']}x6]"
            )
        
        if self.non_striker:
            ns = self.batting_stats[self.non_striker['name']]
            self.gui_elements['non_striker_label'].config(
                text=f"  {self.non_striker['name']}: {ns['runs']}({ns['balls']}) [{ns['fours']}x4, {ns['sixes']}x6]"
            )
        
        # Bowler
        if self.current_bowler:
            b = self.bowling_stats[self.current_bowler['name']]
            self.gui_elements['bowler_label'].config(
                text=f"{self.current_bowler['name']}: {b['overs']}.{b['balls']%6}-{b['maidens']}-{b['runs']}-{b['wickets']}"
            )
        
        # Update scorecards
        self._update_scorecards()
    
    def _update_scorecards(self):
        """Update all scorecard trees"""
        # Update current innings
        inn_num = self.current_innings
        bat_tree = self.gui_elements.get(f'inn{inn_num}_bat_tree')
        bowl_tree = self.gui_elements.get(f'inn{inn_num}_bowl_tree')
        
        if bat_tree:
            for item in bat_tree.get_children():
                bat_tree.delete(item)
            self._populate_batting_tree(bat_tree, self.batting_stats)
        
        if bowl_tree:
            for item in bowl_tree.get_children():
                bowl_tree.delete(item)
            self._populate_bowling_tree(bowl_tree, self.bowling_stats)
        
        # Update completed innings
        for i, inn in enumerate(self.innings_data, 1):
            bat_tree = self.gui_elements.get(f'inn{i}_bat_tree')
            bowl_tree = self.gui_elements.get(f'inn{i}_bowl_tree')
            
            if bat_tree:
                for item in bat_tree.get_children():
                    bat_tree.delete(item)
                self._populate_batting_tree(bat_tree, inn['batting_stats'])
            
            if bowl_tree:
                for item in bowl_tree.get_children():
                    bowl_tree.delete(item)
                self._populate_bowling_tree(bowl_tree, inn['bowling_stats'])
    
    def _populate_batting_tree(self, tree, stats):
        """Populate batting tree"""
        for name, s in stats.items():
            if s['balls'] > 0 or s['runs'] > 0:
                # Calculate SR on the fly
                sr = (s['runs'] * 100 / s['balls']) if s['balls'] > 0 else 0.0
                tree.insert('', 'end', values=(
                    name, s['runs'], s['balls'], s['fours'], s['sixes'],
                    f"{sr:.1f}", s['dismissal']
                ))
    
    def _populate_bowling_tree(self, tree, stats):
        """Populate bowling tree"""
        for name, s in stats.items():
            if s['balls'] > 0:
                overs_display = f"{s['overs']}.{s['balls']%6}"
                # Calculate economy on the fly
                economy = (s['runs'] * 6 / s['balls']) if s['balls'] > 0 else 0.0
                tree.insert('', 'end', values=(
                    name, overs_display, s['maidens'], s['runs'],
                    s['wickets'], f"{economy:.2f}"
                ))
    
    # GUI simulation methods
    
    def gui_simulate_ball(self):
        """Simulate one ball"""
        if not self.match_ended:
            self.simulate_ball()
            self.update_gui()
        
        if self.match_ended:
            self._show_match_summary()
    
    def gui_simulate_over(self):
        """Simulate one over"""
        for _ in range(6):
            if not self.match_ended:
                self.simulate_ball()
        
        self.update_gui()
        
        if self.match_ended:
            self._show_match_summary()
    
    def gui_simulate_session(self):
        """Simulate until end of session"""
        target_session = self.current_session
        target_day = self.current_day
        
        while not self.match_ended and self.current_session == target_session and self.current_day == target_day:
            self.simulate_ball()
        
        self.update_gui()
        
        if self.match_ended:
            self._show_match_summary()
    
    def gui_simulate_day(self):
        """Simulate until end of day"""
        target_day = self.current_day
        
        while not self.match_ended and self.current_day == target_day:
            self.simulate_ball()
        
        self.update_gui()
        
        if self.match_ended:
            self._show_match_summary()
    
    def gui_simulate_to_end(self):
        """Simulate to end"""
        while not self.match_ended:
            self.simulate_ball()
        
        self.update_gui()
        self._show_match_summary()
    
    def _show_match_summary(self):
        """Show enhanced match summary with OK button to update stats"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Match Summary")
        summary_window.geometry("800x600")
        summary_window.transient(self.root)
        
        # Make it modal
        summary_window.grab_set()
        
        # Main frame with scrollbar
        main_frame = ttk.Frame(summary_window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        ttk.Label(
            scrollable_frame,
            text="MATCH RESULT",
            font=('Arial', 18, 'bold')
        ).pack(pady=15)
        
        # Result
        ttk.Label(
            scrollable_frame,
            text=self.result,
            font=('Arial', 14, 'bold'),
            foreground='blue'
        ).pack(pady=10)
        
        # Match details
        details_frame = ttk.LabelFrame(scrollable_frame, text="Match Details", padding=10)
        details_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(
            details_frame,
            text=f"Duration: {self.current_day} days",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        ttk.Label(
            details_frame,
            text=f"Final Weather: {self.weather}",
            font=('Arial', 10)
        ).pack(anchor='w')
        
        # Innings summary
        for i, inn in enumerate(self.innings_data):
            inn_frame = ttk.LabelFrame(scrollable_frame, text=f"Innings {i+1}", padding=10)
            inn_frame.pack(fill='x', padx=20, pady=5)
            
            ttk.Label(
                inn_frame,
                text=f"{inn['batting_team']}: {inn['score']}/{inn['wickets']} ({inn['overs']:.1f} overs)",
                font=('Arial', 12, 'bold')
            ).pack(anchor='w')
            
            # Top scorers
            sorted_batsmen = sorted(
                inn['batting_stats'].items(),
                key=lambda x: x[1]['runs'],
                reverse=True
            )[:3]
            
            if sorted_batsmen and sorted_batsmen[0][1]['runs'] > 0:
                ttk.Label(inn_frame, text="Top Scorers:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5,2))
                for name, stats in sorted_batsmen:
                    if stats['runs'] > 0:
                        ttk.Label(
                            inn_frame,
                            text=f"  {name}: {stats['runs']}({stats['balls']}) - {stats['fours']}x4, {stats['sixes']}x6",
                            font=('Arial', 9)
                        ).pack(anchor='w')
            
            # Top bowlers
            sorted_bowlers = sorted(
                inn['bowling_stats'].items(),
                key=lambda x: x[1]['wickets'],
                reverse=True
            )[:3]
            
            if sorted_bowlers and sorted_bowlers[0][1]['wickets'] > 0:
                ttk.Label(inn_frame, text="Top Bowlers:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5,2))
                for name, stats in sorted_bowlers:
                    if stats['wickets'] > 0:
                        ttk.Label(
                            inn_frame,
                            text=f"  {name}: {stats['wickets']}/{stats['runs']} ({stats['overs']}.{stats['balls']%6} ov, Econ: {stats['economy']:.2f})",
                            font=('Arial', 9)
                        ).pack(anchor='w')
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # OK button to update stats and close
        button_frame = ttk.Frame(summary_window)
        button_frame.pack(fill='x', pady=10)
        
        def on_ok():
            """Update stats, fixture, and close"""
            try:
                print(f"[on_ok] Starting stats update process...")
                
                # Update player stats using StatisticsManager
                self._update_stats_using_statistics_manager()
                
                # Update fixture in parent app
                if self.parent_app:
                    try:
                        print(f"[on_ok] Updating fixture with result: {self.result}")
                        
                        # Get the format
                        match_format = self.parent_app.fixtures_format_var.get() if hasattr(self.parent_app, 'fixtures_format_var') else 'Test'
                        
                        # Update the fixture in fixtures_by_format
                        if hasattr(self.parent_app, 'fixtures_by_format') and match_format in self.parent_app.fixtures_by_format:
                            fixtures_list = self.parent_app.fixtures_by_format[match_format]
                            
                            # Find and update the fixture
                            for i, fixture in enumerate(fixtures_list):
                                if (fixture[0] == self.team1['name'] and fixture[1] == self.team2['name']) or \
                                   (fixture[0] == self.team2['name'] and fixture[1] == self.team1['name']):
                                    # Update the fixture tuple (team1, team2, result)
                                    fixtures_list[i] = (fixture[0], fixture[1], self.result)
                                    print(f"[on_ok] Updated fixture: {fixtures_list[i]}")
                                    break
                        
                        # Refresh the fixtures display
                        if hasattr(self.parent_app, 'update_fixtures_display'):
                            self.parent_app.update_fixtures_display()
                            print(f"[on_ok] Fixtures display refreshed")
                        
                    except Exception as e:
                        print(f"[on_ok] Error updating fixture: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Close windows
                summary_window.destroy()
                if self.root:
                    self.root.destroy()
                
                # Delay UI updates to ensure windows are closed (like T20 simulator)
                if self.parent_app and hasattr(self.parent_app, 'after'):
                    self.parent_app.after(500, self._complete_ui_updates)
                else:
                    self._complete_ui_updates()
                    
            except Exception as e:
                print(f"[on_ok] Error in on_ok: {e}")
                import traceback
                traceback.print_exc()
        
        ttk.Button(
            button_frame,
            text="OK - Update Stats",
            command=on_ok,
            width=20
        ).pack()
    
    def _update_player_stats(self):
        """Update player stats in parent app"""
        if not self.parent_app:
            return
        
        try:
            # Track which players have been counted for match participation
            players_in_match = set()
            
            # Update stats for all innings
            for inn in self.innings_data:
                batting_team_name = inn['batting_team']
                bowling_team_name = inn['bowling_team']
                
                # Find teams
                team1_name = self.team1.name if hasattr(self.team1, 'name') else self.team1['name']
                team2_name = self.team2.name if hasattr(self.team2, 'name') else self.team2['name']
                batting_team = self.team1 if team1_name == batting_team_name else self.team2
                bowling_team = self.team2 if team2_name == batting_team_name else self.team1
                
                # Update batting stats
                for player_name, stats in inn['batting_stats'].items():
                    # Search in parent_app.teams instead of self.team1/team2
                    if self.parent_app and hasattr(self.parent_app, 'teams'):
                        batting_team_obj = next((t for t in self.parent_app.teams if t.name == batting_team_name), None)
                        if batting_team_obj:
                            player = next((p for p in batting_team_obj.players if p.name == player_name), None)
                        else:
                            player = None
                    else:
                        player = next((p for p in batting_team.players if p.name == player_name), None)
                    
                    if player and stats['balls'] > 0:
                        # Initialize stats structure if not present (matches ODI/T20 format)
                        if isinstance(player, dict):
                            if 'stats' not in player:
                                player['stats'] = {'Test': {'matches': 0, 'innings_played': 0, 'runs': 0, 'balls_faced': 0, 'fours': 0, 'sixes': 0, 'dismissals': 0, 'not_outs': 0, 'highest_score': 0, 'wickets': 0, 'balls_bowled': 0, 'runs_conceded': 0, 'maidens': 0}}
                            stats_structure = player['stats']['Test']
                        else:
                            stats_structure = player.stats['Test']
                        
                        # Update batting stats
                        stats_structure['runs'] += stats['runs']
                        stats_structure['balls_faced'] += stats['balls']
                        stats_structure['innings_played'] += 1
                        stats_structure['matches'] += 1
                        if stats['dismissal'] != 'not out':
                            stats_structure['dismissals'] = stats_structure.get('dismissals', 0) + 1
                        
                        # Update highest score
                        if stats['runs'] > stats_structure.get('highest_score', 0):
                            stats_structure['highest_score'] = stats['runs']
                        
                        # Update fifties and centuries
                        if stats['runs'] >= 100:
                            stats_structure['centuries'] = stats_structure.get('centuries', 0) + 1
                        elif stats['runs'] >= 50:
                            stats_structure['fifties'] = stats_structure.get('fifties', 0) + 1
                
                # Update bowling stats
                print(f"[DEBUG] Processing bowling stats for innings: {bowling_team_name}")
                print(f"[DEBUG] Bowling team found: {bowling_team['name']}, has {len(bowling_team['players'])} players")
                print(f"[DEBUG] First 3 player names in bowling team: {[p['name'] for p in bowling_team['players'][:3]]}")
                
                for player_name, stats in inn['bowling_stats'].items():
                    # Search in parent_app.teams instead of self.team1/team2
                    # because self.team1/team2 might be copies, not the actual team objects
                    if self.parent_app and hasattr(self.parent_app, 'teams'):
                        bowling_team_obj = next((t for t in self.parent_app.teams if t['name'] == bowling_team_name), None)
                        if bowling_team_obj:
                            player = next((p for p in bowling_team_obj['players'] if p['name'] == player_name), None)
                        else:
                            player = None
                            print(f"[DEBUG] ⚠️ Could not find team '{bowling_team_name}' in parent_app.teams!")
                    else:
                        # Fallback to original method
                        player = next((p for p in bowling_team['players'] if p['name'] == player_name), None)
                    
                    # Check if bowler has bowled (either complete overs or partial balls)
                    if player and (stats.get('overs', 0) > 0 or stats.get('balls', 0) > 0):
                        print(f"[DEBUG] ✓ Updating bowling stats for {player_name}")
                        # Initialize test_stats if not present
                        if 'test_stats' not in player:
                            player['test_stats'] = {
                                'matches': 0,
                                'innings_played': 0,
                                'runs': 0,
                                'balls_faced': 0,
                                'fours': 0,
                                'sixes': 0,
                                'highest_score': 0,
                                'fifties': 0,
                                'centuries': 0,
                                'dismissals': 0,
                                'balls_bowled': 0,
                                'wickets': 0,
                                'runs_conceded': 0,
                                'maidens': 0,
                                'best_bowling': (0, 0),
                                'four_wicket_hauls': 0,
                                'five_wicket_hauls': 0
                            }
                        
                        test_stats = player['test_stats']
                        
                        # Only increment match count once per player
                        if player_name not in players_in_match:
                            test_stats['matches'] = test_stats.get('matches', 0) + 1
                            players_in_match.add(player_name)
                        
                        # Use balls directly (it's already the total count, not remainder)
                        total_balls = stats.get('balls', 0)
                        print(f"[DEBUG] Total balls: {total_balls} (overs={stats.get('overs', 0)})")
                        test_stats['balls_bowled'] = test_stats.get('balls_bowled', 0) + total_balls
                        test_stats['runs_conceded'] = test_stats.get('runs_conceded', 0) + stats['runs']
                        test_stats['wickets'] = test_stats.get('wickets', 0) + stats['wickets']
                        test_stats['maidens'] = test_stats.get('maidens', 0) + stats['maidens']
                        print(f"[DEBUG] Updated stats - balls_bowled={test_stats['balls_bowled']}, wickets={test_stats['wickets']}, runs={test_stats['runs_conceded']}")
                        
                        # Update best bowling
                        current_best = test_stats.get('best_bowling', (0, 0))
                        if isinstance(current_best, tuple) and len(current_best) == 2:
                            if stats['wickets'] > current_best[0] or (stats['wickets'] == current_best[0] and stats['runs'] < current_best[1]):
                                test_stats['best_bowling'] = (stats['wickets'], stats['runs'])
                        else:
                            test_stats['best_bowling'] = (stats['wickets'], stats['runs'])
                        
                        # Update wicket hauls
                        if stats['wickets'] >= 5:
                            test_stats['five_wicket_hauls'] = test_stats.get('five_wicket_hauls', 0) + 1
                        elif stats['wickets'] >= 4:
                            test_stats['four_wicket_hauls'] = test_stats.get('four_wicket_hauls', 0) + 1
            
            # Update parent app
            if hasattr(self.parent_app, 'update_all_stats'):
                self.parent_app.update_all_stats()
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_team_stats(self):
        """Update team stats (matches played, won, lost, points)"""
        if not self.parent_app or not hasattr(self.parent_app, 'teams'):
            return
        
        try:
            print(f"[DEBUG] Updating team stats for {self.team1['name']} vs {self.team2['name']}")
            print(f"[DEBUG] Result: {self.result}, Winner: {self.winner}")
            
            # Update both teams
            for team in self.parent_app.teams:
                if team['name'] == self.team1['name'] or team['name'] == self.team2['name']:
                    # Increment matches played
                    team['matches_played'] = team.get('matches_played', 0) + 1
                    print(f"[DEBUG] {team['name']} matches_played: {team['matches_played']}")
                    
                    # Update wins/losses/points
                    if self.winner and team['name'] == self.winner:
                        team['matches_won'] = team.get('matches_won', 0) + 1
                        team['points'] = team.get('points', 0) + 2
                        print(f"[DEBUG] {team['name']} WON - matches_won: {team['matches_won']}, points: {team['points']}")
                    elif self.winner and self.winner != "Draw":
                        team['matches_lost'] = team.get('matches_lost', 0) + 1
                        print(f"[DEBUG] {team['name']} LOST - matches_lost: {team['matches_lost']}")
                    elif self.winner == "Draw":
                        # Draw - both teams get 1 point
                        team['points'] = team.get('points', 0) + 1
                        print(f"[DEBUG] {team['name']} DRAW - points: {team['points']}")
            
            # Update teams tab display
            if hasattr(self.parent_app, 'update_teams_tab'):
                self.parent_app.update_teams_tab()
                print(f"[DEBUG] Teams tab updated")
                
        except Exception as e:
            print(f"Error updating team stats: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_stats_using_statistics_manager(self):
        """Update player stats using StatisticsManager instead of direct updates"""
        print("[Test Match] Updating player stats using StatisticsManager...")
        
        try:
            # Create StatisticsManager instance
            stats_manager = StatisticsManager()
            
            # Get current year from parent app if available
            current_year = None
            if self.parent_app and hasattr(self.parent_app, 'current_year'):
                current_year = self.parent_app.current_year
            
            # Create team objects for StatisticsManager
            # Convert team dictionaries to Team objects if needed
            teams = []
            for team_data in [self.team1, self.team2]:
                if hasattr(team_data, 'players'):
                    # Already a Team object
                    teams.append(team_data)
                else:
                    # Need to find the actual Team object in parent_app
                    if self.parent_app and hasattr(self.parent_app, 'teams'):
                        for team in self.parent_app.teams:
                            if team.name == team_data['name']:
                                teams.append(team)
                                break
                    else:
                        print(f"[Test Match] Warning: Could not find team object for {team_data['name']}")
            
            if len(teams) == 2:
                # Update stats using StatisticsManager
                stats_manager.update_player_stats_from_match(
                    match=self,
                    match_format='Test',
                    teams=teams,
                    current_year=current_year
                )
                print("[Test Match] StatisticsManager update completed successfully!")
            else:
                print("[Test Match] Could not find proper team objects, falling back to original method")
                self._update_player_stats()
                self._update_team_stats()
            
        except Exception as e:
            print(f"[Test Match] Error updating stats with StatisticsManager: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to original method if StatisticsManager fails
            self._update_player_stats()
            self._update_team_stats()
    
    def _complete_ui_updates(self):
        """Complete UI updates after window closure (matches T20 simulator pattern)"""
        if not self.parent_app:
            return
        
        try:
            print("[UI Update] Completing delayed UI updates...")
            
            # Update screens using the correct method names found in main_window.py
            if hasattr(self.parent_app, 'screen_manager') and self.parent_app.screen_manager:
                print("[UI Update] Updating screens through screen_manager...")
                
                # Refresh Statistics screen
                if 'Statistics' in self.parent_app.screen_manager.screens:
                    stats_screen = self.parent_app.screen_manager.screens['Statistics']
                    if hasattr(stats_screen, 'refresh_all_stats'):
                        print("[UI Update] Calling refresh_all_stats on Statistics screen...")
                        stats_screen.refresh_all_stats()
                    if hasattr(stats_screen, 'refresh_data'):
                        print("[UI Update] Calling refresh_data on Statistics screen...")
                        stats_screen.refresh_data()
                
                # Refresh Players screen (for player profiles)
                if 'Players' in self.parent_app.screen_manager.screens:
                    players_screen = self.parent_app.screen_manager.screens['Players']
                    if hasattr(players_screen, 'refresh_data'):
                        print("[UI Update] Calling refresh_data on Players screen...")
                        players_screen.refresh_data()
                
                # Refresh all screens that have refresh_data method
                print("[UI Update] Refreshing all screens with refresh_data method...")
                for screen_name, screen in self.parent_app.screen_manager.screens.items():
                    if hasattr(screen, 'refresh_data'):
                        print(f"[UI Update] Calling refresh_data on {screen_name} screen...")
                        screen.refresh_data()
            
            # Also try some common method names as fallback
            if hasattr(self.parent_app, 'update_all_stats'):
                print("[UI Update] Calling update_all_stats...")
                self.parent_app.update_all_stats()
                
            if hasattr(self.parent_app, 'update'):
                print("[UI Update] Forcing UI redraw...")
                self.parent_app.update()
            
            print("[UI Update] All UI updates completed!")
            
        except Exception as e:
            print(f"[UI Update] Error in _complete_ui_updates: {e}")
            import traceback
            traceback.print_exc()
    
    def start_match(self):
        """Start match"""
        if self.root:
            self.root.mainloop()
