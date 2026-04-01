"""
Team class with multi-format support
Manages players, tiers, and statistics for T20, ODI, and Test formats
"""

class Team:
    """Represents a cricket team with multi-format support"""
    
    def __init__(self, name, tier=1):
        self.name = name
        
        # Players
        self.players = []  # Senior squad (up to MAX_SQUAD_SIZE, default 40)
        self.u21_squad = []  # Youth team (15 players)
        
        # FORMAT-SPECIFIC TIER INFORMATION (separate tiers for each format)
        self.format_tiers = {
            'T20': tier,
            'ODI': tier,
            'Test': tier
        }
        
        # FORMAT-SPECIFIC LEAGUE STATISTICS
        self.format_stats = {
            'T20': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,  # Net run rate
                'tier_position': 0,
                'is_promoted': False,
                'is_relegated': False
            },
            'ODI': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,
                'tier_position': 0,
                'is_promoted': False,
                'is_relegated': False
            },
            'Test': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,
                'tier_position': 0,
                'is_promoted': False,
                'is_relegated': False
            }
        }
        
        # U21/YOUTH LEAGUE STATISTICS (Tier 5)
        self.u21_stats = {
            'T20': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,
                'tier_position': 0,
            },
            'ODI': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,
                'tier_position': 0,
            },
            'Test': {
                'matches_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'points': 0,
                'nrr': 0.0,
                'tier_position': 0,
            }
        }
        
        # Loot Pack System
        self.credits = 0
        self.inventory = []
        
        # Team Attributes
        self.morale = 50
        self.form = 50
        # Captain and vice-captain (player names; None = use auto selection)
        self.captain_name = None
        self.vice_captain_name = None
        # Manual selection: list of 11 player names for next match (None = use get_playing_xi)
        self.selected_xi_names = None
        self.batting_order_names = None  # Order for next match (same 11 names in bat order)
        # Team records (updated when broken)
        self.team_records = {
            'highest_total': None,      # {'runs': int, 'vs': str, 'format': str, 'season': int}
            'lowest_total': None,       # {'runs': int, 'vs': str, 'format': str, 'season': int}
            'biggest_win_runs': None,   # {'margin': int, 'vs': str, 'format': str, 'season': int}
            'biggest_win_wickets': None # {'margin': int, 'vs': str, 'format': str, 'season': int}
        }
    
    def add_player(self, player):
        """Add player to squad"""
        from cricket_manager.utils.constants import MAX_SQUAD_SIZE
        if player in self.players:
            return True
        if len(self.players) < MAX_SQUAD_SIZE:
            self.players.append(player)
            return True
        return False
    
    def get_playing_xi(self, match_format='T20'):
        """
        Get best 11 players for match using 5-2-4 structure
        
        Target composition:
        - 5 Batters (positions 1-5)
        - 2 Allrounders (positions 6-7)
        - 4 Bowlers (positions 8-11, sorted by batting skill)
        """
        # Exclude injured players
        available = [p for p in self.players if not getattr(p, 'is_injured', False)]
        # Manual selection
        if self.selected_xi_names and len(self.selected_xi_names) >= 11:
            name_to_player = {p.name: p for p in available}
            xi = [name_to_player[n] for n in self.selected_xi_names[:11] if n in name_to_player]
            if len(xi) >= 11:
                return xi[:11]
        
        # Categorize players by role
        batters = [p for p in available if 'Batter' in p.role and 'Allrounder' not in p.role]
        allrounders = [p for p in available if 'Allrounder' in p.role]
        bowlers = [p for p in available if p not in batters and p not in allrounders]
        
        # Select best players by skill
        xi = []
        
        # 1. Top 5 batters by batting skill
        top_batters = sorted(batters, key=lambda p: p.batting, reverse=True)[:5]
        xi.extend(top_batters)
        
        # 2. Top 2 allrounders by combined skill
        top_allrounders = sorted(allrounders, 
                                key=lambda p: (p.batting + p.bowling) / 2, 
                                reverse=True)[:2]
        xi.extend(top_allrounders)
        
        # 3. Top 4 bowlers by bowling skill, then sorted by batting for positions 8-11
        top_bowlers = sorted(bowlers, key=lambda p: p.bowling, reverse=True)[:4]
        top_bowlers = sorted(top_bowlers, key=lambda p: p.batting, reverse=True)
        xi.extend(top_bowlers)
        
        # Handle shortages
        if len(xi) < 11:
            # Fill remaining spots with best available players
            remaining = [p for p in available if p not in xi]
            remaining = sorted(remaining, 
                             key=lambda p: (p.batting + p.bowling + p.fielding) / 3, 
                             reverse=True)
            xi.extend(remaining[:11 - len(xi)])
        
        return xi[:11]
    
    def get_batting_order(self, match_format='T20'):
        """Return playing XI in batting order. Uses batting_order_names if set."""
        xi = self.get_playing_xi(match_format)
        if self.batting_order_names and len(self.batting_order_names) >= 11:
            name_to_player = {p.name: p for p in xi}
            ordered = [name_to_player[n] for n in self.batting_order_names[:11] if n in name_to_player]
            if len(ordered) >= 11:
                return ordered
        return xi
    
    def get_bowling_squad(self):
        """Get top 7 bowlers for bowling rotation"""
        
        # Get all players who can bowl (bowlers + allrounders)
        bowlers = [p for p in self.players if p.bowling >= 40]
        
        # Sort by bowling skill
        bowlers = sorted(bowlers, key=lambda p: p.bowling, reverse=True)
        
        return bowlers[:7]
    
    def update_points(self, match_format, result):
        """Update team points after match for specific format"""
        stats = self.format_stats[match_format]
        
        if result == 'win':
            stats['wins'] += 1
            stats['points'] += 2
        elif result == 'loss':
            stats['losses'] += 1
        else:  # draw
            stats['draws'] += 1
            stats['points'] += 1
        
        stats['matches_played'] += 1
    
    def update_nrr(self, match_format, runs_scored, overs_batted, runs_conceded, overs_bowled):
        """Update net run rate for specific format"""
        stats = self.format_stats[match_format]
        
        if overs_batted > 0 and overs_bowled > 0:
            run_rate_for = runs_scored / overs_batted
            run_rate_against = runs_conceded / overs_bowled
            stats['nrr'] = round(run_rate_for - run_rate_against, 3)
    
    def reset_season_stats(self, match_format):
        """Reset season statistics for specific format"""
        stats = self.format_stats[match_format]
        stats['matches_played'] = 0
        stats['wins'] = 0
        stats['losses'] = 0
        stats['draws'] = 0
        stats['points'] = 0
        stats['nrr'] = 0.0
        stats['is_promoted'] = False
        stats['is_relegated'] = False
        
        # Reset player season stats with all fields
        for player in self.players:
            player.season_stats[match_format] = {
                'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0, 'balls_bowled': 0,
                'runs_conceded': 0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0
            }
    
    def __repr__(self):
        return f"Team({self.name}, T20 Tier {self.format_tiers['T20']}, {len(self.players)} players)"
