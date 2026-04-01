"""
Commentary System - Generate ball-by-ball commentary
"""

import random


class CommentarySystem:
    """
    Generate ball-by-ball commentary
    
    Commentary varies based on:
    - Runs scored
    - Dismissal type
    - Match situation
    - Player traits
    """
    
    def __init__(self):
        self.commentary_templates = {
            'dot': [
                "Defended solidly.",
                "No run.",
                "Dot ball.",
                "Good length, defended.",
                "Plays it back to the bowler.",
                "Watchful defense.",
                "Blocked safely.",
                "Solid technique on display."
            ],
            'single': [
                "Quick single taken.",
                "Pushed for one.",
                "Single to {fielder}.",
                "Easy single.",
                "Rotates the strike.",
                "Nudged away for one.",
                "Works it for a single.",
                "Good running between the wickets."
            ],
            'two': [
                "Two runs!",
                "Good running, two taken.",
                "Placed well for two.",
                "Couple of runs.",
                "They scamper back for two.",
                "Excellent placement, two runs."
            ],
            'three': [
                "Three runs!",
                "Great running, three taken!",
                "Superb running between the wickets!",
                "They push for three and make it!",
                "Excellent fitness, three runs."
            ],
            'boundary': [
                "FOUR! Beautiful shot!",
                "Cracking boundary!",
                "That's gone to the fence!",
                "FOUR runs!",
                "Superb timing!",
                "What a shot! FOUR!",
                "Glorious stroke for four!",
                "Races away to the boundary!",
                "Perfectly placed! FOUR!",
                "Exquisite timing! Boundary!"
            ],
            'six': [
                "SIX! What a shot!",
                "MAXIMUM! Out of the park!",
                "That's huge! SIX!",
                "Into the stands!",
                "Massive hit for six!",
                "BANG! That's gone all the way!",
                "Incredible power! SIX!",
                "Launched into orbit!",
                "Monstrous six!",
                "That's disappeared! MAXIMUM!"
            ],
            'wicket_bowled': [
                "BOWLED! {batsman} is gone!",
                "Timber! {bowler} strikes!",
                "Cleaned up! What a delivery!",
                "Through the gate! BOWLED!",
                "The stumps are shattered!"
            ],
            'wicket_caught': [
                "CAUGHT! {batsman} has to go!",
                "In the air... and TAKEN!",
                "Excellent catch! {batsman} is out!",
                "Straight to the fielder! OUT!",
                "What a catch! {batsman} departs!"
            ],
            'wicket_lbw': [
                "LBW! {batsman} is given out!",
                "That's plumb! LBW!",
                "Trapped in front! OUT!",
                "Dead in front! LBW!",
                "No doubt about that! LBW!"
            ],
            'wicket_stumped': [
                "STUMPED! Lightning quick work!",
                "{batsman} is stumped! Brilliant keeping!",
                "Out of the crease and STUMPED!",
                "Quick as a flash! STUMPED!",
                "The keeper whips off the bails! OUT!"
            ],
            'wicket_runout': [
                "RUN OUT! {batsman} is short!",
                "Direct hit! RUN OUT!",
                "Brilliant fielding! RUN OUT!",
                "Caught short! OUT!",
                "Disaster! RUN OUT!"
            ]
        }
        
        self.fielding_positions = [
            'mid-off', 'mid-on', 'cover', 'square leg', 'fine leg',
            'third man', 'point', 'mid-wicket', 'long-on', 'long-off'
        ]
    
    def generate_commentary(self, ball_result, batsman, bowler, match_situation=None):
        """
        Generate commentary for a ball
        
        Args:
            ball_result: Dict with runs, wicket, dismissal info
            batsman: Batsman player object or name
            bowler: Bowler player object or name
            match_situation: Dict with score, overs, required rate (optional)
        
        Returns:
            String commentary
        """
        
        runs = ball_result.get('runs', 0)
        is_wicket = ball_result.get('wicket', False)
        
        # Get player names
        batsman_name = batsman.name if hasattr(batsman, 'name') else str(batsman)
        bowler_name = bowler.name if hasattr(bowler, 'name') else str(bowler)
        
        if is_wicket:
            dismissal = ball_result.get('dismissal_type', 'out')
            commentary = self._generate_wicket_commentary(
                batsman_name, bowler_name, dismissal
            )
        elif runs == 0:
            commentary = random.choice(self.commentary_templates['dot'])
        elif runs == 1:
            template = random.choice(self.commentary_templates['single'])
            commentary = template.format(fielder=random.choice(self.fielding_positions))
        elif runs == 2:
            commentary = random.choice(self.commentary_templates['two'])
        elif runs == 3:
            commentary = random.choice(self.commentary_templates['three'])
        elif runs == 4:
            commentary = random.choice(self.commentary_templates['boundary'])
        elif runs == 6:
            commentary = random.choice(self.commentary_templates['six'])
        else:
            commentary = f"{runs} runs."
        
        # Add situation context
        if match_situation:
            commentary = self._add_situation_context(commentary, match_situation)
        
        return commentary
    
    def _generate_wicket_commentary(self, batsman_name, bowler_name, dismissal_type):
        """Generate wicket-specific commentary"""
        
        dismissal_lower = dismissal_type.lower()
        
        if 'bowl' in dismissal_lower:
            template = random.choice(self.commentary_templates['wicket_bowled'])
        elif 'caught' in dismissal_lower or 'catch' in dismissal_lower:
            template = random.choice(self.commentary_templates['wicket_caught'])
        elif 'lbw' in dismissal_lower:
            template = random.choice(self.commentary_templates['wicket_lbw'])
        elif 'stump' in dismissal_lower:
            template = random.choice(self.commentary_templates['wicket_stumped'])
        elif 'run' in dismissal_lower:
            template = random.choice(self.commentary_templates['wicket_runout'])
        else:
            # Generic wicket
            templates = [
                "OUT! {batsman} is gone!",
                "WICKET! {bowler} strikes!",
                "{batsman} has to go!",
                "Breakthrough for {bowler}!"
            ]
            template = random.choice(templates)
        
        return template.format(batsman=batsman_name, bowler=bowler_name)
    
    def _add_situation_context(self, commentary, situation):
        """Add match situation context to commentary"""
        
        # Pressure situation
        if situation.get('pressure', False):
            pressure_comments = [
                " Pressure building!",
                " Tension in the air!",
                " Crucial moment!",
                " Every run counts now!"
            ]
            commentary += random.choice(pressure_comments)
        
        # Close finish
        if situation.get('close_finish', False):
            close_comments = [
                " This is going down to the wire!",
                " What a finish this is!",
                " Nail-biting stuff!",
                " Edge of the seat cricket!"
            ]
            commentary += random.choice(close_comments)
        
        # High required rate
        if situation.get('high_required_rate', False):
            rate_comments = [
                " They need to accelerate!",
                " Run rate climbing!",
                " Time running out!",
                " Need boundaries now!"
            ]
            commentary += random.choice(rate_comments)
        
        return commentary
    
    def generate_over_summary(self, over_number, runs_in_over, wickets_in_over):
        """
        Generate end of over summary
        
        Args:
            over_number: Over number
            runs_in_over: Runs scored in the over
            wickets_in_over: Wickets fallen in the over
        
        Returns:
            String summary
        """
        
        summary = f"End of over {over_number}: "
        
        if wickets_in_over > 0:
            summary += f"{runs_in_over} runs, {wickets_in_over} wicket(s). "
            if wickets_in_over > 1:
                summary += "Double strike!"
            else:
                summary += "Breakthrough!"
        elif runs_in_over == 0:
            summary += "Maiden over! Excellent bowling!"
        elif runs_in_over >= 15:
            summary += f"{runs_in_over} runs! Expensive over!"
        elif runs_in_over >= 10:
            summary += f"{runs_in_over} runs. Good over for the batting side."
        else:
            summary += f"{runs_in_over} runs."
        
        return summary
    
    def generate_innings_summary(self, team_name, runs, wickets, overs):
        """
        Generate innings summary
        
        Args:
            team_name: Name of batting team
            runs: Total runs
            wickets: Wickets fallen
            overs: Overs bowled
        
        Returns:
            String summary
        """
        
        summary = f"{team_name} finish on {runs}/{wickets} in {overs:.1f} overs. "
        
        if wickets == 10:
            summary += "All out!"
        elif runs >= 200:
            summary += "Massive total!"
        elif runs >= 150:
            summary += "Competitive score."
        elif runs < 100:
            summary += "Below par score."
        else:
            summary += "Decent total."
        
        return summary
    
    def generate_match_result(self, winner_name, margin, match_type='runs'):
        """
        Generate match result commentary
        
        Args:
            winner_name: Name of winning team
            margin: Winning margin (runs or wickets)
            match_type: 'runs' or 'wickets'
        
        Returns:
            String result commentary
        """
        
        if match_type == 'runs':
            result = f"{winner_name} win by {margin} runs! "
            if margin >= 100:
                result += "Dominant performance!"
            elif margin >= 50:
                result += "Comprehensive victory!"
            else:
                result += "Well played!"
        else:
            result = f"{winner_name} win by {margin} wickets! "
            if margin >= 8:
                result += "Cruised to victory!"
            elif margin >= 5:
                result += "Comfortable win!"
            else:
                result += "Close finish!"
        
        return result
