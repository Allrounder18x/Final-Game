"""
Universal Match Simulator for T20, ODI, and Test formats
Supports ball-by-ball simulation with automatic bowler rotation
"""

import random
from cricket_manager.utils.constants import FORMAT_SETTINGS


class MatchSimulator:
    """Universal match simulator for T20, ODI, and Test formats"""
    
    def __init__(self, team1, team2, match_format='T20', headless=False, parent_app=None):
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.headless = headless  # True = no GUI, fast simulation
        self.parent_app = parent_app  # Reference to game engine
        
        # FORMAT-SPECIFIC SETTINGS
        settings = FORMAT_SETTINGS[match_format]
        self.max_overs = settings['max_overs']
        self.innings_count = settings['innings_count']
        self.powerplay_overs = settings['powerplay_overs']
        self.max_bowler_overs = settings['max_bowler_overs']
        
        if match_format == 'Test':
            self.max_overs_per_day = settings['max_overs_per_day']
            self.follow_on_threshold = settings['follow_on_threshold']
            self.current_day = 1
        
        # Match state
        self.current_innings = 1
        self.total_runs = 0
        self.total_wickets = 0
        self.total_overs = 0
        self.total_balls = 0
        self.current_over = 0
        self.current_ball = 0
        self.match_ended = False
        
        # Batting/Bowling
        self.batting_team = None
        self.bowling_team = None
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        
        # Bowling management
        self.bowling_squad = []  # Top 7 bowlers
        self.bowler_stats = {}  # Track overs bowled per bowler
        self.last_bowler = None  # Prevent consecutive overs
        
        # Match statistics (accumulated during match)
        self.match_stats = {}
        self.stats_updated = False  # Prevent duplicate updates
        
        # Scorecards
        self.innings_scores = []  # List of innings scores
        
        # Pitch conditions (vary by format)
        self.initialize_pitch_conditions()
        
        # Ball-by-ball commentary
        self.commentary = []
        
        # Winner
        self.winner = None
        self.result = ""
    
    def initialize_pitch_conditions(self):
        """Initialize pitch conditions based on format"""
        
        if self.match_format == 'Test':
            # Test pitches have more variety and deteriorate over 5 days
            pitch_types = ['green_seamer', 'green_top', 'dustbowl', 
                          'flat_road', 'bouncy', 'balanced']
            self.pitch_type = random.choice(pitch_types)
            
            if self.pitch_type == 'green_seamer':
                self.pitch_pace = random.randint(7, 10)
                self.pitch_spin = random.randint(2, 5)
                self.pitch_bounce = random.randint(6, 9)
            elif self.pitch_type == 'dustbowl':
                self.pitch_pace = random.randint(2, 5)
                self.pitch_spin = random.randint(7, 10)
                self.pitch_bounce = random.randint(3, 6)
            elif self.pitch_type == 'flat_road':
                self.pitch_pace = random.randint(2, 4)
                self.pitch_spin = random.randint(2, 4)
                self.pitch_bounce = random.randint(2, 4)
            else:  # balanced
                self.pitch_pace = random.randint(5, 7)
                self.pitch_spin = random.randint(5, 7)
                self.pitch_bounce = random.randint(5, 7)
        
        else:
            # T20/ODI pitches are more balanced
            self.pitch_pace = random.randint(5, 8)
            self.pitch_spin = random.randint(4, 7)
            self.pitch_bounce = random.randint(5, 8)
    
    def update_pitch_conditions(self):
        """Update pitch conditions (Test matches deteriorate)"""
        
        if self.match_format == 'Test':
            # Pitch deteriorates over days
            if self.current_day >= 3:
                # Day 3+: More spin, less pace
                self.pitch_spin = min(10, self.pitch_spin + 1)
                self.pitch_pace = max(1, self.pitch_pace - 1)
            
            if self.current_day >= 4:
                # Day 4+: Even more spin
                self.pitch_spin = min(10, self.pitch_spin + 1)
                self.pitch_bounce = max(1, self.pitch_bounce - 1)
    
    def simulate(self):
        """Simulate complete match"""
        
        # Initialize match stats for all players
        self.initialize_match_stats()
        
        # Toss
        self.toss()
        
        if self.match_format == 'Test':
            # Test match: Up to 4 innings
            for innings_num in range(1, 5):
                if not self.match_ended:
                    self.current_innings = innings_num
                    self.simulate_innings()
                    
                    # Check for follow-on after 2nd innings
                    if innings_num == 2:
                        self.check_follow_on()
        else:
            # T20/ODI: 2 innings
            self.current_innings = 1
            self.simulate_innings()
            
            # Store first innings score
            self.innings_scores.append({
                'runs': self.total_runs,
                'wickets': self.total_wickets,
                'overs': self.total_overs
            })
            
            self.current_innings = 2
            self.swap_teams()
            self.simulate_innings()
            
            # Store second innings score
            self.innings_scores.append({
                'runs': self.total_runs,
                'wickets': self.total_wickets,
                'overs': self.total_overs
            })
        
        # Determine winner
        self.determine_winner()
        
        # Update statistics
        self.end_match()
        
        return self.winner
    
    def initialize_match_stats(self):
        """Initialize match statistics for all players"""
        
        all_players = self.team1.players + self.team2.players
        
        for player in all_players:
            self.match_stats[player.name] = {
                'batting': {
                    'runs': 0,
                    'balls': 0,
                    'fours': 0,
                    'sixes': 0,
                    'dismissal': None
                },
                'bowling': {
                    'balls': 0,
                    'runs': 0,
                    'wickets': 0,
                    'maidens': 0,
                    'speeds': []  # List of bowling speeds
                }
            }
    
    def toss(self):
        """Conduct toss"""
        
        toss_winner = random.choice([self.team1, self.team2])
        decision = random.choice(['bat', 'bowl'])
        
        if decision == 'bat':
            self.batting_team = toss_winner
            self.bowling_team = self.team2 if toss_winner == self.team1 else self.team1
        else:
            self.bowling_team = toss_winner
            self.batting_team = self.team2 if toss_winner == self.team1 else self.team1
        
        # Get bowling squad
        self.bowling_squad = self.bowling_team.get_bowling_squad()
        
        # Initialize bowler stats
        for bowler in self.bowling_squad:
            self.bowler_stats[bowler.name] = {
                'overs': 0,
                'balls': 0,
                'current_spell': 0
            }
    
    def simulate_innings(self):
        """Simulate one innings"""
        
        self.current_over = 0
        self.total_runs = 0
        self.total_wickets = 0
        self.total_balls = 0
        
        # Get playing XI
        batting_xi = self.batting_team.get_playing_xi(self.match_format)
        
        # Set opening batsmen
        self.striker = batting_xi[0]
        self.non_striker = batting_xi[1]
        self.next_batsman_index = 2
        
        # Simulate overs
        max_overs = self.max_overs if self.max_overs else 90  # Default for Test
        
        while self.current_over < max_overs and self.total_wickets < 10:
            self.simulate_over()
            
            # Test match: Check for day end
            if self.match_format == 'Test' and self.current_over % 90 == 0:
                self.current_day += 1
                self.update_pitch_conditions()
            
            # Check target (for 2nd innings)
            if self.current_innings == 2 and self.match_format != 'Test':
                if len(self.innings_scores) > 0:
                    target = self.innings_scores[0]['runs']
                    if self.total_runs > target:
                        break  # Target achieved
    
    def simulate_over(self):
        """Simulate one over (6 balls)"""
        
        # Select bowler (automatic rotation)
        self.current_bowler = self.select_bowler_automatic()
        
        if not self.current_bowler:
            return  # No bowler available (shouldn't happen)
        
        # Simulate 6 balls
        for ball in range(6):
            if self.total_wickets >= 10:
                break
            
            self.current_ball = ball + 1
            self.simulate_ball()
        
        self.current_over += 1
        
        # Update bowler stats
        if self.current_bowler:
            self.bowler_stats[self.current_bowler.name]['overs'] += 1
        
        # Swap striker and non-striker at end of over
        self.striker, self.non_striker = self.non_striker, self.striker
        
        # Update last bowler
        self.last_bowler = self.current_bowler
    
    def select_bowler_automatic(self):
        """
        Automatic bowler selection with phase-based rotation
        
        Phases:
        - Opening (overs 1-10): Best 2 pace bowlers
        - First change (overs 11-20): Next 2 bowlers
        - Middle overs (overs 21-40): Spinners + economical bowlers
        - Death overs (overs 41-50): Best death bowlers
        """
        
        # Get eligible bowlers (not last bowler, under max overs)
        eligible = []
        
        for bowler in self.bowling_squad:
            # Skip if bowled last over
            if self.last_bowler and bowler.name == self.last_bowler.name:
                continue
            
            # Check max overs constraint
            if self.max_bowler_overs:
                overs_bowled = self.bowler_stats[bowler.name]['overs']
                if overs_bowled >= self.max_bowler_overs:
                    continue
            
            eligible.append(bowler)
        
        if not eligible:
            # Emergency: allow last bowler if no one else available
            return self.last_bowler
        
        # Phase-based selection
        if self.match_format == 'T20':
            if self.current_over < 6:  # Powerplay
                # Prefer pace bowlers
                from cricket_manager.utils.helpers import is_pace_bowler
                pace_bowlers = [b for b in eligible if is_pace_bowler(b.role)]
                if pace_bowlers:
                    return max(pace_bowlers, key=lambda b: b.bowling)
            elif self.current_over >= 16:  # Death overs
                # Best bowlers
                return max(eligible, key=lambda b: b.bowling)
            else:  # Middle overs
                # Rotate all bowlers
                return min(eligible, key=lambda b: self.bowler_stats[b.name]['overs'])
        
        elif self.match_format == 'ODI':
            if self.current_over < 10:  # Powerplay
                from cricket_manager.utils.helpers import is_pace_bowler
                pace_bowlers = [b for b in eligible if is_pace_bowler(b.role)]
                if pace_bowlers:
                    return max(pace_bowlers, key=lambda b: b.bowling)
            elif self.current_over >= 40:  # Death overs
                return max(eligible, key=lambda b: b.bowling)
            else:  # Middle overs
                return min(eligible, key=lambda b: self.bowler_stats[b.name]['overs'])
        
        else:  # Test
            # Rotate based on least overs bowled
            return min(eligible, key=lambda b: self.bowler_stats[b.name]['overs'])
    
    def simulate_ball(self):
        """Simulate one ball"""
        
        # Calculate outcome probabilities based on skills
        batting_skill = self.striker.batting
        bowling_skill = self.current_bowler.bowling
        
        # Skill difference affects probabilities
        skill_diff = batting_skill - bowling_skill
        
        # Base probabilities (vary by format)
        if self.match_format == 'T20':
            dot_prob = 0.35
            single_prob = 0.25
            four_prob = 0.12
            six_prob = 0.08
        elif self.match_format == 'ODI':
            dot_prob = 0.40
            single_prob = 0.28
            four_prob = 0.10
            six_prob = 0.05
        else:  # Test
            dot_prob = 0.50
            single_prob = 0.30
            four_prob = 0.08
            six_prob = 0.02
        
        two_prob = 0.15
        three_prob = 0.05
        
        # Adjust based on skill difference
        if skill_diff > 20:
            dot_prob -= 0.10
            four_prob += 0.05
            six_prob += 0.05
        elif skill_diff < -20:
            dot_prob += 0.10
            four_prob -= 0.05
            six_prob -= 0.05
        
        # Create base probabilities dictionary
        base_probs = {
            'dot': dot_prob,
            'single': single_prob,
            'two': two_prob,
            'three': three_prob,
            'four': four_prob,
            'six': six_prob
        }
        
        # APPLY TRAIT EFFECTS TO PROBABILITIES
        situation = self.get_current_situation()
        modified_probs = self.apply_traits_to_probabilities(base_probs, situation)
        
        # Roll for outcome
        roll = random.random()
        cumulative = 0
        
        # Wicket chance (separate roll) WITH TRAIT EFFECTS
        base_wicket_chance = 0.05 + (bowling_skill - batting_skill) * 0.001
        base_wicket_chance = max(0.02, min(0.15, base_wicket_chance))
        
        wicket_chance = self.calculate_wicket_chance_with_traits(base_wicket_chance, situation)
        
        if random.random() < wicket_chance:
            self.handle_wicket()
            return
        
        # Determine runs using modified probabilities
        for outcome, prob in modified_probs.items():
            cumulative += prob
            if roll < cumulative:
                if outcome == 'dot':
                    runs = 0
                elif outcome == 'single':
                    runs = 1
                elif outcome == 'two':
                    runs = 2
                elif outcome == 'three':
                    runs = 3
                elif outcome == 'four':
                    runs = 4
                elif outcome == 'six':
                    runs = 6
                break
        else:
            # Fallback if probabilities don't sum to 1
            runs = 0
        
        # Update scores
        self.total_runs += runs
        self.total_balls += 1
        
        # Update player stats in match_stats dictionary
        self.match_stats[self.striker.name]['batting']['runs'] += runs
        self.match_stats[self.striker.name]['batting']['balls'] += 1
        if runs == 4:
            self.match_stats[self.striker.name]['batting']['fours'] += 1
        elif runs == 6:
            self.match_stats[self.striker.name]['batting']['sixes'] += 1
        
        self.match_stats[self.current_bowler.name]['bowling']['runs'] += runs
        self.match_stats[self.current_bowler.name]['bowling']['balls'] += 1
        
        # Generate bowling speed
        from cricket_manager.utils.helpers import is_pace_bowler
        if is_pace_bowler(self.current_bowler.role):
            if 'Fast Bowler' in self.current_bowler.role:
                base_speed = 130
            elif 'Fast Medium' in self.current_bowler.role:
                base_speed = 125
            else:
                base_speed = 115
            
            speed = base_speed + random.randint(-10, 15)
            self.match_stats[self.current_bowler.name]['bowling']['speeds'].append(speed)
        
        # Swap batsmen on odd runs
        if runs % 2 == 1:
            self.striker, self.non_striker = self.non_striker, self.striker
        
        # Add commentary (if not headless)
        if not self.headless:
            self.add_commentary(runs, False)
    
    def handle_wicket(self):
        """Handle a wicket"""
        self.total_wickets += 1
        self.total_balls += 1
        
        # Update bowler stats
        self.match_stats[self.current_bowler.name]['bowling']['wickets'] += 1
        self.match_stats[self.current_bowler.name]['bowling']['balls'] += 1
        
        # Generate realistic dismissal method
        dismissal_roll = random.random() * 100
        
        # Select fielder for caught dismissals
        fielders = [p for p in self.bowling_team.players if p.name != self.current_bowler.name]
        fielder = random.choice(fielders) if fielders else self.bowling_team.players[0]
        
        # Check if spin or pace bowler
        is_spin = 'Spin' in self.current_bowler.role or 'Leg' in self.current_bowler.role or 'Off' in self.current_bowler.role
        
        if is_spin:
            # Spin bowler dismissals
            if dismissal_roll < 30:  # 30% Caught
                dismissal = f"c {fielder.name} b {self.current_bowler.name}"
            elif dismissal_roll < 45:  # 15% Bowled
                dismissal = f"b {self.current_bowler.name}"
            elif dismissal_roll < 68:  # 23% LBW
                dismissal = f"lbw b {self.current_bowler.name}"
            elif dismissal_roll < 77:  # 9% Stumped
                dismissal = f"st {fielder.name} b {self.current_bowler.name}"
            elif dismissal_roll < 78:  # 1% Hit Wicket
                dismissal = f"hit wicket b {self.current_bowler.name}"
            elif dismissal_roll < 96:  # 18% Edge Caught
                dismissal = f"c {fielder.name} b {self.current_bowler.name}"
            else:  # 4% Run Out
                dismissal = "run out"
                # Don't count as bowler's wicket
                self.match_stats[self.current_bowler.name]['bowling']['wickets'] -= 1
        else:
            # Pace bowler dismissals (no stumped)
            if dismissal_roll < 30:  # 30% Caught
                dismissal = f"c {fielder.name} b {self.current_bowler.name}"
            elif dismissal_roll < 45:  # 15% Bowled
                dismissal = f"b {self.current_bowler.name}"
            elif dismissal_roll < 68:  # 23% LBW
                dismissal = f"lbw b {self.current_bowler.name}"
            elif dismissal_roll < 69:  # 1% Hit Wicket
                dismissal = f"hit wicket b {self.current_bowler.name}"
            elif dismissal_roll < 87:  # 18% Edge Caught
                dismissal = f"c {fielder.name} b {self.current_bowler.name}"
            else:  # 13% Run Out
                dismissal = "run out"
                # Don't count as bowler's wicket
                self.match_stats[self.current_bowler.name]['bowling']['wickets'] -= 1
        
        # Update batsman dismissal
        self.match_stats[self.striker.name]['batting']['dismissal'] = dismissal
        
        # Add commentary (if not headless)
        if not self.headless:
            self.add_commentary(0, True)
        
        # New batsman
        batting_xi = self.batting_team.get_playing_xi(self.match_format)
        if self.next_batsman_index < len(batting_xi):
            self.striker = batting_xi[self.next_batsman_index]
            self.next_batsman_index += 1
    
    def add_commentary(self, runs, is_wicket):
        """Add ball commentary"""
        over_ball = f"{self.current_over}.{self.current_ball}"
        
        if is_wicket:
            comment = f"{over_ball}: WICKET! {self.striker.name} out! {self.current_bowler.name} strikes!"
        elif runs == 0:
            comment = f"{over_ball}: Dot ball"
        elif runs == 4:
            comment = f"{over_ball}: FOUR! {self.striker.name} finds the boundary!"
        elif runs == 6:
            comment = f"{over_ball}: SIX! {self.striker.name} sends it out of the park!"
        else:
            comment = f"{over_ball}: {runs} run(s)"
        
        self.commentary.append(comment)
    
    def swap_teams(self):
        """Swap batting and bowling teams"""
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        
        # Reset bowling squad
        self.bowling_squad = self.bowling_team.get_bowling_squad()
        self.bowler_stats = {}
        for bowler in self.bowling_squad:
            self.bowler_stats[bowler.name] = {
                'overs': 0,
                'balls': 0,
                'current_spell': 0
            }
        self.last_bowler = None
    
    def check_follow_on(self):
        """Check for follow-on in Test match"""
        if self.match_format != 'Test':
            return
        
        # Simplified: No follow-on implementation for now
        pass
    
    def determine_winner(self):
        """Determine match winner"""
        
        if self.match_format == 'Test':
            # Test match winner logic (simplified)
            if len(self.innings_scores) >= 2:
                # Compare total runs
                team1_total = sum(s['runs'] for i, s in enumerate(self.innings_scores) if i % 2 == 0)
                team2_total = sum(s['runs'] for i, s in enumerate(self.innings_scores) if i % 2 == 1)
                
                if team1_total > team2_total:
                    self.winner = self.team1
                    self.result = f"{self.winner.name} won by {team1_total - team2_total} runs"
                elif team2_total > team1_total:
                    self.winner = self.team2
                    self.result = f"{self.winner.name} won by {team2_total - team1_total} runs"
                else:
                    self.winner = None
                    self.result = "Match drawn"
            else:
                self.winner = None
                self.result = "Match drawn"
        else:
            # T20/ODI
            if len(self.innings_scores) >= 2:
                first_innings = self.innings_scores[0]
                second_innings = self.innings_scores[1]
                
                if second_innings['runs'] > first_innings['runs']:
                    self.winner = self.bowling_team  # Team batting second
                    wickets_left = 10 - second_innings['wickets']
                    self.result = f"{self.winner.name} won by {wickets_left} wickets"
                elif first_innings['runs'] > second_innings['runs']:
                    self.winner = self.batting_team  # Team batting first
                    runs_diff = first_innings['runs'] - second_innings['runs']
                    self.result = f"{self.winner.name} won by {runs_diff} runs"
                else:
                    self.winner = None
                    self.result = "Match tied"
    
    def end_match(self):
        """End match and update statistics"""
        
        self.match_ended = True
        
        # CRITICAL: Update player statistics for this format
        if self.parent_app and hasattr(self.parent_app, 'statistics_manager'):
            self.parent_app.statistics_manager.update_player_stats_from_match(
                match=self,
                match_format=self.match_format,
                teams=[self.team1, self.team2]
            )
        
        # Update team points
        if self.winner == self.team1:
            self.team1.update_points(self.match_format, 'win')
            self.team2.update_points(self.match_format, 'loss')
        elif self.winner == self.team2:
            self.team2.update_points(self.match_format, 'win')
            self.team1.update_points(self.match_format, 'loss')
        else:
            self.team1.update_points(self.match_format, 'draw')
            self.team2.update_points(self.match_format, 'draw')
    
    def quick_simulate_match(self):
        """Quick simulation for headless mode"""
        return self.simulate()

    
    def get_current_situation(self):
        """
        Determine current match situation for trait effects
        
        Returns:
            String describing situation (powerplay, death_overs, pressure, etc.)
        """
        
        # Powerplay
        if self.current_over < self.powerplay_overs:
            return 'powerplay'
        
        # Death overs (format-specific)
        if self.match_format == 'T20':
            if self.current_over >= 16:
                return 'death_overs'
        elif self.match_format == 'ODI':
            if self.current_over >= 40:
                return 'death_overs'
        
        # Pressure situation (chasing in 2nd innings)
        if self.current_innings == 2:
            if len(self.innings_scores) > 0:
                target = self.innings_scores[0]['runs']
                runs_needed = target - self.total_runs + 1
                overs_left = self.max_overs - self.current_over if self.max_overs else 90
                
                if overs_left > 0:
                    required_rate = runs_needed / overs_left
                    current_rate = self.total_runs / max(1, self.current_over)
                    
                    # High pressure if required rate is much higher than current rate
                    if required_rate > current_rate * 1.5:
                        return 'pressure'
        
        # Middle overs (default)
        return 'middle_overs'
    
    def apply_traits_to_probabilities(self, base_probs, situation):
        """
        Apply trait effects from both batsman and bowler to probabilities
        
        Args:
            base_probs: Dictionary of base probabilities
            situation: Current match situation
        
        Returns:
            Modified probabilities dictionary
        """
        
        from cricket_manager.systems.trait_assignment import (
            get_player_trait_effects, apply_trait_to_probabilities
        )
        from cricket_manager.utils.helpers import is_spin_bowler, is_pace_bowler
        
        # Start with base probabilities
        modified_probs = base_probs.copy()
        
        # Apply batsman traits
        if hasattr(self.striker, 'traits') and self.striker.traits:
            batsman_effects = get_player_trait_effects(self.striker)
            batting_effects = batsman_effects['batting']
            
            # Apply basic effects
            if 'dot_bonus' in batting_effects:
                modified_probs['dot'] += batting_effects['dot_bonus']
            if 'dot_penalty' in batting_effects:
                modified_probs['dot'] += batting_effects['dot_penalty']
            
            if 'single_bonus' in batting_effects:
                modified_probs['single'] += batting_effects['single_bonus']
            
            if 'two_bonus' in batting_effects:
                modified_probs['two'] += batting_effects['two_bonus']
            
            if 'four_bonus' in batting_effects:
                modified_probs['four'] += batting_effects['four_bonus']
            
            if 'six_bonus' in batting_effects:
                modified_probs['six'] += batting_effects['six_bonus']
            if 'six_penalty' in batting_effects:
                modified_probs['six'] += batting_effects['six_penalty']
            
            if 'boundary_bonus' in batting_effects:
                bonus = batting_effects['boundary_bonus']
                modified_probs['four'] += bonus / 2
                modified_probs['six'] += bonus / 2
            
            # Apply situation-specific bonuses
            if situation == 'powerplay' and 'powerplay_bonus' in batting_effects:
                bonus = batting_effects['powerplay_bonus']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 + bonus)
            
            elif situation == 'death_overs' and 'death_overs_bonus' in batting_effects:
                bonus = batting_effects['death_overs_bonus']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 + bonus)
            
            elif situation == 'pressure' and 'pressure_bonus' in batting_effects:
                bonus = batting_effects['pressure_bonus']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 + bonus)
            
            # Apply vs spin/pace bonuses
            if is_spin_bowler(self.current_bowler.role):
                if 'vs_spin_bonus' in batting_effects:
                    bonus = batting_effects['vs_spin_bonus']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 + bonus)
                if 'vs_spin_penalty' in batting_effects:
                    penalty = batting_effects['vs_spin_penalty']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 + penalty)
            
            elif is_pace_bowler(self.current_bowler.role):
                if 'vs_pace_bonus' in batting_effects:
                    bonus = batting_effects['vs_pace_bonus']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 + bonus)
                if 'vs_pace_penalty' in batting_effects:
                    penalty = batting_effects['vs_pace_penalty']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 + penalty)
        
        # Apply bowler traits (reduce scoring)
        if hasattr(self.current_bowler, 'traits') and self.current_bowler.traits:
            bowler_effects = get_player_trait_effects(self.current_bowler)
            bowling_effects = bowler_effects['bowling']
            
            # Economy bonus reduces runs
            if 'economy_bonus' in bowling_effects:
                reduction = bowling_effects['economy_bonus']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 - reduction)
                modified_probs['dot'] *= (1 + reduction)
            
            # Runs conceded reduction
            if 'runs_conceded_reduction' in bowling_effects:
                reduction = bowling_effects['runs_conceded_reduction']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 - reduction)
                modified_probs['dot'] *= (1 + reduction)
            
            # Runs conceded increase (negative trait)
            if 'runs_conceded_increase' in bowling_effects:
                increase = bowling_effects['runs_conceded_increase']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 + increase)
                modified_probs['dot'] *= (1 - increase)
            
            # Situation-specific bonuses
            if situation == 'powerplay' and 'powerplay_bonus' in bowling_effects:
                bonus = bowling_effects['powerplay_bonus']
                for key in ['single', 'two', 'three', 'four', 'six']:
                    modified_probs[key] *= (1 - bonus)
                modified_probs['dot'] *= (1 + bonus)
            
            elif situation == 'death_overs':
                if 'death_overs_bonus' in bowling_effects:
                    bonus = bowling_effects['death_overs_bonus']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 - bonus)
                    modified_probs['dot'] *= (1 + bonus)
                
                if 'death_overs_penalty' in bowling_effects:
                    penalty = bowling_effects['death_overs_penalty']
                    for key in ['single', 'two', 'three', 'four', 'six']:
                        modified_probs[key] *= (1 - penalty)
        
        # Normalize probabilities to sum to 1.0
        total = sum(modified_probs.values())
        if total > 0:
            for key in modified_probs:
                modified_probs[key] /= total
        
        # Ensure no negative probabilities
        for key in modified_probs:
            modified_probs[key] = max(0, modified_probs[key])
        
        return modified_probs
    
    def calculate_wicket_chance_with_traits(self, base_wicket_chance, situation):
        """
        Calculate wicket chance with trait effects from both batsman and bowler
        
        Args:
            base_wicket_chance: Base wicket probability
            situation: Current match situation
        
        Returns:
            Modified wicket chance
        """
        
        from cricket_manager.systems.trait_assignment import get_player_trait_effects
        
        wicket_chance = base_wicket_chance
        
        # Batsman traits
        if hasattr(self.striker, 'traits') and self.striker.traits:
            batsman_effects = get_player_trait_effects(self.striker)
            batting_effects = batsman_effects['batting']
            
            if 'wicket_resistance' in batting_effects:
                wicket_chance *= (1 - batting_effects['wicket_resistance'])
            
            if 'wicket_penalty' in batting_effects:
                wicket_chance *= (1 + batting_effects['wicket_penalty'])
        
        # Bowler traits
        if hasattr(self.current_bowler, 'traits') and self.current_bowler.traits:
            bowler_effects = get_player_trait_effects(self.current_bowler)
            bowling_effects = bowler_effects['bowling']
            
            if 'wicket_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['wicket_bonus'])
            
            if 'wicket_chance_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['wicket_chance_bonus'])
            
            if 'wicket_penalty' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['wicket_penalty'])
            
            # Situation-specific bonuses
            if situation == 'powerplay' and 'powerplay_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['powerplay_bonus'] * 0.5)
            
            elif situation == 'death_overs' and 'death_overs_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['death_overs_bonus'] * 0.5)
        
        # Clamp between reasonable bounds
        wicket_chance = max(0.01, min(0.30, wicket_chance))
        
        return wicket_chance

    # ========================================================================
    # INTERACTIVE MATCH PLAY - Ball-by-ball with controls
    # ========================================================================
    
    def start_match(self):
        """Initialize match for interactive play"""
        self.batting_team = self.team1
        self.bowling_team = self.team2
        self.current_innings = 1
        self.match_ended = False
        self.innings_complete = False
        self.current_ball = 0
        self.current_over = 0
        self.target = None
        self.last_bowler = None
        
        # Initialize match_stats for ALL players in both teams
        self.match_stats = {}
        for player in self.team1.players + self.team2.players:
            self.match_stats[player.name] = {
                'batting': {
                    'runs': 0,
                    'balls': 0,
                    'fours': 0,
                    'sixes': 0,
                    'dismissal': None
                },
                'bowling': {
                    'balls': 0,
                    'runs': 0,
                    'wickets': 0,
                    'maidens': 0,
                    'speeds': []
                }
            }
        
        # Initialize batsmen
        self.striker = self.batting_team.players[0]
        self.non_striker = self.batting_team.players[1]
        self.striker_runs = 0
        self.striker_balls = 0
        self.non_striker_runs = 0
        self.non_striker_balls = 0
        
        # Initialize bowling squad (top 7 bowlers by bowling skill)
        sorted_bowlers = sorted(self.bowling_team.players, key=lambda x: x.bowling, reverse=True)
        self.bowling_squad = sorted_bowlers[:7]
        
        # Initialize bowler data
        self.bowler_data = {}
        for bowler in self.bowling_squad:
            self.bowler_data[bowler.name] = {
                'overs_bowled': 0,
                'current_spell': 0,
                'spell_length': None,
                'can_bowl_after': None,
                'spells': 0
            }
        
        # Select opening bowlers (best 2 from bowling squad)
        self.opening_bowlers = self.bowling_squad[:2]
        self.current_bowler = self.opening_bowlers[0]
        self.bowler_runs = 0
        self.bowler_wickets = 0
        self.bowler_overs = 0
        
        # Initialize innings data
        self.current_innings_data = {
            'batting_team': self.batting_team.name,
            'bowling_team': self.bowling_team.name,
            'runs': 0,
            'wickets': 0,
            'overs': 0.0,
            'balls': 0
        }
        
        # Initialize innings tracking
        self.innings1_data = None
        self.innings2_data = None
        
        self.current_over_balls = []
        self.match_complete = False
    
    def simulate_ball_interactive(self, aggression=0.5, shot_type=None):
        """
        Simulate one ball with user controls (interactive mode)
        
        Args:
            aggression: 0.0 to 1.0 (defensive to aggressive)
            shot_type: Optional shot selection
        
        Returns:
            dict with ball result
        """
        if self.match_complete or self.innings_complete:
            return {}
        
        # Calculate outcome based on aggression and shot type
        runs, wicket, extras = self.calculate_ball_outcome(aggression, shot_type)
        
        # Update scores
        self.current_innings_data['runs'] += runs
        self.current_innings_data['balls'] += 1
        
        # Update match_stats for batsman
        if self.striker.name in self.match_stats:
            self.match_stats[self.striker.name]['batting']['runs'] += runs
            self.match_stats[self.striker.name]['batting']['balls'] += 1
            if runs == 4:
                self.match_stats[self.striker.name]['batting']['fours'] += 1
            elif runs == 6:
                self.match_stats[self.striker.name]['batting']['sixes'] += 1
        
        # Update match_stats for bowler
        if self.current_bowler.name in self.match_stats:
            self.match_stats[self.current_bowler.name]['bowling']['runs'] += runs
            self.match_stats[self.current_bowler.name]['bowling']['balls'] += 1
            
            # Generate bowling speed
            from cricket_manager.utils.helpers import is_pace_bowler
            if is_pace_bowler(self.current_bowler.role):
                if 'Fast Bowler' in self.current_bowler.role:
                    base_speed = 140
                elif 'Fast Medium' in self.current_bowler.role:
                    base_speed = 130
                else:
                    base_speed = 120
                speed = base_speed + random.randint(-10, 15)
                self.match_stats[self.current_bowler.name]['bowling']['speeds'].append(speed)
            elif 'Spin' in self.current_bowler.role or 'Leg' in self.current_bowler.role or 'Off' in self.current_bowler.role:
                base_speed = 85
                speed = base_speed + random.randint(-5, 5)
                self.match_stats[self.current_bowler.name]['bowling']['speeds'].append(speed)
        
        # Update batsman
        if not extras:
            self.striker_runs += runs
            self.striker_balls += 1
        
        # Update bowler
        self.bowler_runs += runs
        
        # Track ball in over
        if wicket:
            self.current_over_balls.append('W')
            self.current_innings_data['wickets'] += 1
            self.bowler_wickets += 1
            
            # Update match_stats for wicket
            if self.current_bowler.name in self.match_stats:
                self.match_stats[self.current_bowler.name]['bowling']['wickets'] += 1
            
            # Generate realistic dismissal method
            dismissal_roll = random.random() * 100
            
            # Select fielder for caught dismissals
            fielders = [p for p in self.bowling_team.players if p.name != self.current_bowler.name]
            fielder = random.choice(fielders) if fielders else self.bowling_team.players[0]
            
            # Check if spin or pace bowler
            is_spin = 'Spin' in self.current_bowler.role or 'Leg' in self.current_bowler.role or 'Off' in self.current_bowler.role
            
            if is_spin:
                # Spin bowler dismissals
                if dismissal_roll < 30:  # 30% Caught
                    dismissal = f"c {fielder.name} b {self.current_bowler.name}"
                elif dismissal_roll < 45:  # 15% Bowled
                    dismissal = f"b {self.current_bowler.name}"
                elif dismissal_roll < 68:  # 23% LBW
                    dismissal = f"lbw b {self.current_bowler.name}"
                elif dismissal_roll < 77:  # 9% Stumped
                    dismissal = f"st {fielder.name} b {self.current_bowler.name}"
                elif dismissal_roll < 78:  # 1% Hit Wicket
                    dismissal = f"hit wicket b {self.current_bowler.name}"
                elif dismissal_roll < 96:  # 18% Edge Caught
                    dismissal = f"c {fielder.name} b {self.current_bowler.name}"
                else:  # 4% Run Out
                    dismissal = "run out"
                    # Don't count as bowler's wicket
                    if self.current_bowler.name in self.match_stats:
                        self.match_stats[self.current_bowler.name]['bowling']['wickets'] -= 1
            else:
                # Pace bowler dismissals (no stumped)
                if dismissal_roll < 30:  # 30% Caught
                    dismissal = f"c {fielder.name} b {self.current_bowler.name}"
                elif dismissal_roll < 45:  # 15% Bowled
                    dismissal = f"b {self.current_bowler.name}"
                elif dismissal_roll < 68:  # 23% LBW
                    dismissal = f"lbw b {self.current_bowler.name}"
                elif dismissal_roll < 69:  # 1% Hit Wicket
                    dismissal = f"hit wicket b {self.current_bowler.name}"
                elif dismissal_roll < 87:  # 18% Edge Caught
                    dismissal = f"c {fielder.name} b {self.current_bowler.name}"
                else:  # 13% Run Out
                    dismissal = "run out"
                    # Don't count as bowler's wicket
                    if self.current_bowler.name in self.match_stats:
                        self.match_stats[self.current_bowler.name]['bowling']['wickets'] -= 1
            
            # Update batsman dismissal in match_stats
            if self.striker.name in self.match_stats:
                self.match_stats[self.striker.name]['batting']['dismissal'] = dismissal
            
            # New batsman
            if self.current_innings_data['wickets'] < 10:
                self.striker = self.batting_team.players[self.current_innings_data['wickets'] + 1]
                self.striker_runs = 0
                self.striker_balls = 0
            else:
                self.innings_complete = True
        else:
            if runs == 0:
                self.current_over_balls.append('•')
            else:
                self.current_over_balls.append(str(runs))
            
            # Rotate strike on odd runs
            if runs % 2 == 1:
                self.striker, self.non_striker = self.non_striker, self.striker
                self.striker_runs, self.non_striker_runs = self.non_striker_runs, self.striker_runs
                self.striker_balls, self.non_striker_balls = self.non_striker_balls, self.striker_balls
        
        # Check if over complete
        self.current_ball += 1
        if self.current_ball >= 6:
            self.complete_over()
        
        # Update overs - IMPORTANT: Show max overs when all out
        balls = self.current_innings_data['balls']
        calculated_overs = balls // 6 + (balls % 6) / 10
        
        # If all out, show max overs instead of actual overs
        if self.current_innings_data['wickets'] >= 10 and self.max_overs:
            self.current_innings_data['overs'] = float(self.max_overs)
        else:
            self.current_innings_data['overs'] = calculated_overs
        
        # Check innings complete
        if calculated_overs >= self.max_overs:
            self.innings_complete = True
        
        # Check if chasing team won
        if self.current_innings == 2 and self.target:
            if self.current_innings_data['runs'] >= self.target:
                self.innings_complete = True
                self.match_complete = True
        
        # Handle innings transition
        if self.innings_complete and self.current_innings == 1:
            # Store first innings data
            self.innings1_data = self.current_innings_data.copy()
            self.target = self.innings1_data['runs'] + 1
            
            # Start second innings
            self.current_innings = 2
            self.innings_complete = False
            self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
            
            # Reset match_stats for second innings (keep first innings stats)
            # Only reset the stats for the new batting team
            for player in self.batting_team.players:
                if player.name in self.match_stats:
                    # Reset batting stats for new batting team
                    self.match_stats[player.name]['batting'] = {
                        'runs': 0,
                        'balls': 0,
                        'fours': 0,
                        'sixes': 0,
                        'dismissal': None
                    }
            
            for player in self.bowling_team.players:
                if player.name in self.match_stats:
                    # Reset bowling stats for new bowling team
                    self.match_stats[player.name]['bowling'] = {
                        'balls': 0,
                        'runs': 0,
                        'wickets': 0,
                        'maidens': 0,
                        'speeds': []
                    }
            
            # Initialize new bowling squad for second innings
            sorted_bowlers = sorted(self.bowling_team.players, key=lambda x: x.bowling, reverse=True)
            self.bowling_squad = sorted_bowlers[:7]
            
            # Reset bowler data
            self.bowler_data = {}
            for bowler in self.bowling_squad:
                self.bowler_data[bowler.name] = {
                    'overs_bowled': 0,
                    'current_spell': 0,
                    'spell_length': None,
                    'can_bowl_after': None,
                    'spells': 0
                }
            
            # Select new opening bowlers
            self.opening_bowlers = self.bowling_squad[:2]
            
            # Reset for second innings
            self.striker = self.batting_team.players[0]
            self.non_striker = self.batting_team.players[1]
            self.striker_runs = 0
            self.striker_balls = 0
            self.non_striker_runs = 0
            self.non_striker_balls = 0
            
            self.last_bowler = None
            self.current_bowler = self.opening_bowlers[0]
            self.bowler_runs = 0
            self.bowler_wickets = 0
            self.bowler_overs = 0
            self.current_ball = 0
            self.current_over = 0
            
            self.current_innings_data = {
                'batting_team': self.batting_team.name,
                'bowling_team': self.bowling_team.name,
                'runs': 0,
                'wickets': 0,
                'overs': 0.0,
                'balls': 0
            }
            self.current_over_balls = []
        
        elif self.innings_complete and self.current_innings == 2:
            # Store second innings data
            self.innings2_data = self.current_innings_data.copy()
            self.match_complete = True
        
        # Prepare result
        result = {
            'over': int(self.current_innings_data['overs']),
            'ball': self.current_ball,
            'runs': runs,
            'wicket': wicket,
            'extras': extras,
            'batsman': self.striker.name,
            'bowler': self.current_bowler.name,
            'description': self.generate_ball_description(runs, wicket, shot_type)
        }
        
        return result
    
    def calculate_ball_outcome(self, aggression, shot_type):
        """Calculate ball outcome based on aggression and shot"""
        # Base probabilities
        dot_prob = 0.4 - (aggression * 0.3)
        single_prob = 0.3
        boundary_prob = 0.1 + (aggression * 0.2)
        wicket_prob = 0.05 + (aggression * 0.1)
        
        # Adjust for shot type
        if shot_type == 'Defend':
            dot_prob += 0.3
            wicket_prob -= 0.03
            boundary_prob -= 0.1
        elif shot_type == 'Slog' or shot_type == 'Loft':
            boundary_prob += 0.2
            wicket_prob += 0.15
            dot_prob -= 0.2
        elif shot_type == 'Drive' or shot_type == 'Cut':
            boundary_prob += 0.1
            wicket_prob += 0.05
        
        # Adjust for player skills
        skill_diff = (self.striker.batting - self.current_bowler.bowling) / 100
        wicket_prob -= skill_diff * 0.05
        boundary_prob += skill_diff * 0.1
        
        # Roll dice
        roll = random.random()
        
        # Determine outcome
        if roll < wicket_prob:
            return 0, True, False
        elif roll < wicket_prob + dot_prob:
            return 0, False, False
        elif roll < wicket_prob + dot_prob + boundary_prob:
            # Boundary (4 or 6)
            if random.random() < 0.3:
                return 6, False, False
            else:
                return 4, False, False
        else:
            # Singles/twos/threes
            return random.choice([1, 1, 1, 2, 2, 3]), False, False
    
    def complete_over(self):
        """Complete current over"""
        self.current_over += 1
        self.current_ball = 0
        
        # Update bowler data
        if self.current_bowler and self.current_bowler.name in self.bowler_data:
            self.bowler_data[self.current_bowler.name]['overs_bowled'] += 1
            self.bowler_data[self.current_bowler.name]['current_spell'] += 1
        
        # Rotate strike
        self.striker, self.non_striker = self.non_striker, self.striker
        self.striker_runs, self.non_striker_runs = self.non_striker_runs, self.striker_runs
        self.striker_balls, self.non_striker_balls = self.non_striker_balls, self.striker_balls
        
        # Change bowler
        self.last_bowler = self.current_bowler
        self.current_bowler = self.select_bowler()
        self.bowler_runs = 0
        self.bowler_wickets = 0
        self.bowler_overs = 0
        
        # Clear over balls
        self.current_over_balls = []
    
    def select_bowler(self):
        """
        Select next bowler with proper rotation (like t20oversimulation.py)
        
        Bowling phases:
        - T20: Overs 1-6 (powerplay): Opening bowlers alternate
               Overs 7-16 (middle): 3rd-6th bowlers rotate
               Overs 17-20 (death): Best bowlers return
        - ODI: Overs 1-10: Opening bowlers alternate
               Overs 11-20: 3rd & 4th bowlers
               Overs 21-30: 5th & 6th bowlers
               Overs 31-40: 3rd & 4th return
               Overs 41-50: Opening bowlers return
        """
        current_over = self.current_over + 1
        
        # T20 bowling rotation
        if self.match_format == 'T20':
            # Phase 1: Powerplay (overs 1-6) - Opening bowlers alternate
            if current_over <= 6:
                if current_over % 2 == 1:  # Odd overs
                    selected = self.opening_bowlers[0]
                else:  # Even overs
                    selected = self.opening_bowlers[1]
                
                # Ensure not same as last bowler
                if selected == self.last_bowler and len(self.opening_bowlers) > 1:
                    selected = [b for b in self.opening_bowlers if b != self.last_bowler][0]
                
                return selected
            
            # Phase 2: Middle overs (7-16) - Rotate 3rd-6th bowlers
            elif 6 < current_over <= 16:
                eligible = [b for b in self.bowling_squad[2:6] if b != self.last_bowler]
                if eligible:
                    # Rotate to bowler who has bowled least
                    return min(eligible, key=lambda b: self.bowler_data.get(b.name, {}).get('overs_bowled', 0))
            
            # Phase 3: Death overs (17-20) - Best bowlers return
            else:
                eligible = [b for b in self.bowling_squad[:4] if b != self.last_bowler]
                if eligible:
                    return max(eligible, key=lambda b: b.bowling)
        
        # ODI bowling rotation
        elif self.match_format == 'ODI':
            # Phase 1: Opening bowlers (overs 1-10)
            if current_over <= 10:
                if current_over % 2 == 1:
                    selected = self.opening_bowlers[0]
                else:
                    selected = self.opening_bowlers[1]
                
                if selected == self.last_bowler and len(self.opening_bowlers) > 1:
                    selected = [b for b in self.opening_bowlers if b != self.last_bowler][0]
                
                return selected
            
            # Phase 2: 3rd & 4th bowlers (overs 11-20)
            elif 10 < current_over <= 20:
                eligible = [b for b in self.bowling_squad[2:4] if b != self.last_bowler]
                if eligible:
                    return eligible[0]
            
            # Phase 3: 5th & 6th bowlers (overs 21-30)
            elif 20 < current_over <= 30:
                eligible = [b for b in self.bowling_squad[4:6] if b != self.last_bowler]
                if eligible:
                    return eligible[0]
            
            # Phase 4: 3rd & 4th return (overs 31-40)
            elif 30 < current_over <= 40:
                eligible = [b for b in self.bowling_squad[2:4] if b != self.last_bowler]
                if eligible:
                    return eligible[0]
            
            # Phase 5: Opening bowlers return (overs 41-50)
            else:
                eligible = [b for b in self.opening_bowlers if b != self.last_bowler]
                if eligible:
                    return eligible[0]
        
        # Test match - rotate all bowlers
        else:
            eligible = [b for b in self.bowling_squad if b != self.last_bowler]
            if eligible:
                return min(eligible, key=lambda b: self.bowler_data.get(b.name, {}).get('overs_bowled', 0))
        
        # Fallback: any bowler except last
        eligible = [b for b in self.bowling_squad if b != self.last_bowler]
        if eligible:
            return eligible[0]
        
        # Emergency: return first bowler
        return self.bowling_squad[0] if self.bowling_squad else self.bowling_team.players[0]
    
    def generate_ball_description(self, runs, wicket, shot_type):
        """Generate ball description"""
        if wicket:
            dismissals = ['bowled', 'caught', 'lbw', 'caught behind']
            return f"{self.striker.name} {random.choice(dismissals)}!"
        elif runs == 6:
            return f"Massive six! {self.striker.name} sends it sailing!"
        elif runs == 4:
            return f"Beautiful shot for four by {self.striker.name}!"
        elif runs == 0:
            return f"Dot ball. Good bowling by {self.current_bowler.name}."
        else:
            return f"{runs} run{'s' if runs > 1 else ''}."
    
    def get_winner(self):
        """Get match winner"""
        if not self.match_complete:
            return None
        
        if self.innings1_data and self.innings2_data:
            if self.innings1_data['runs'] > self.innings2_data['runs']:
                return self.team1
            elif self.innings2_data['runs'] > self.innings1_data['runs']:
                return self.team2
        
        return None
    
    def get_margin(self):
        """Get winning margin"""
        winner = self.get_winner()
        if not winner:
            return "Match Tied"
        
        if winner == self.team1:
            run_diff = self.innings1_data['runs'] - self.innings2_data['runs']
            return f"{run_diff} runs"
        else:
            wickets_left = 10 - self.innings2_data['wickets']
            return f"{wickets_left} wickets"
