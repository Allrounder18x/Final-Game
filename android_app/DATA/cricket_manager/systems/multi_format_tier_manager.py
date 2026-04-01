"""
Multi-Format Tier Manager
Manages tier systems for all three cricket formats (T20, ODI, Test)
ICC FTP-style series-based fixture generation
"""

from cricket_manager.systems.tier_system import (
    TierSystem,
    MONTH_NAMES,
    generate_season_series,
    resolve_team_day_clashes,
)


class MultiFormatTierManager:
    """Manage tier systems for all three formats"""
    
    def __init__(self):
        """Initialize tier systems for all formats"""
        self.tier_systems = {
            'T20': TierSystem('T20'),
            'ODI': TierSystem('ODI'),
            'Test': TierSystem('Test')
        }
        # Track opponent history for rotation across seasons
        self.opponent_history = {}
    
    def initialize_all_tiers(self, teams):
        """
        Initialize tier systems for all formats
        
        Args:
            teams: List of Team objects
        """
        print("\n" + "="*60)
        print("INITIALIZING MULTI-FORMAT TIER SYSTEMS")
        print("="*60)
        
        for match_format in ['T20', 'ODI', 'Test']:
            print(f"\n[{match_format}] Assigning teams to tiers...")
            self.tier_systems[match_format].assign_teams_to_tiers(teams)
        
        print("\n" + "="*60)
        print("TIER INITIALIZATION COMPLETE")
        print("="*60)
    
    def generate_all_fixtures(self, wc_month=None, current_season=1):
        """
        Generate ICC FTP-style series-based fixtures for all formats and tiers.
        Uses rotating opponents, home/away tours, randomized series lengths.
        
        Args:
            wc_month: Month index (0-11) reserved for World Cup, or None
            current_season: Current season number for rotation tracking
        
        Returns:
            Dictionary with fixtures for each format: {'T20': [...], 'ODI': [...], 'Test': [...]}
        """
        # Build tier teams dict from all three format tier systems
        # Use T20 tier system as reference for team grouping (tiers are same across formats)
        all_tier_teams = {}
        for tier_num in range(1, 5):
            # Get teams from the T20 tier system (they share the same tier assignments)
            teams = self.tier_systems['T20'].tiers[tier_num]['teams']
            if teams:
                all_tier_teams[tier_num] = teams
        
        # Generate series-based fixtures
        fixtures, self.opponent_history = generate_season_series(
            all_tier_teams=all_tier_teams,
            opponent_history=self.opponent_history,
            wc_month=wc_month,
            current_season=current_season
        )
        
        # Also generate Tier 5 (U21) fixtures for each format
        for match_format in ['T20', 'ODI', 'Test']:
            tier5_fixtures = self.tier_systems[match_format].generate_u21_fixtures()
            # Stamp month/day so U21 fixtures are distributed across the year
            # (instead of all defaulting to the same day in UI/logic).
            for i, fx in enumerate(tier5_fixtures):
                m = i % 12
                d = (i // 12) % 28 + 1
                fx['month'] = m
                fx['day'] = d
                fx['month_name'] = MONTH_NAMES[m]
            fixtures[match_format].extend(tier5_fixtures)

        # Re-run clash resolution with Tier 5 included so associate/U21 teams are
        # not scheduled for multiple matches on the same day.
        resolve_team_day_clashes(fixtures)
        
        return fixtures
    
    def process_all_promotions_relegations(self, all_teams):
        """
        Process promotion/relegation for all formats
        
        Args:
            all_teams: List of all teams in the game
        
        Returns:
            Dictionary with promoted and relegated teams for each format
        """
        results = {
            'T20': {'promoted': [], 'relegated': []},
            'ODI': {'promoted': [], 'relegated': []},
            'Test': {'promoted': [], 'relegated': []}
        }
        
        for match_format in ['T20', 'ODI', 'Test']:
            print(f"\n[{match_format}] Processing promotion/relegation...")
            promoted, relegated = self.tier_systems[match_format].process_promotion_relegation(all_teams)
            
            results[match_format]['promoted'] = promoted
            results[match_format]['relegated'] = relegated
        
        return results
    
    def get_team_tier_info(self, team):
        """
        Get tier information for a team across all formats
        
        Args:
            team: Team object
            
        Returns:
            Dictionary with tier info for all formats
        """
        info = {
            'team_name': team.name,
            'T20': {
                'tier': team.format_tiers.get('T20', 1),
                'points': team.format_stats['T20']['points'],
                'wins': team.format_stats['T20']['wins'],
                'losses': team.format_stats['T20']['losses'],
                'draws': team.format_stats['T20']['draws']
            },
            'ODI': {
                'tier': team.format_tiers.get('ODI', 1),
                'points': team.format_stats['ODI']['points'],
                'wins': team.format_stats['ODI']['wins'],
                'losses': team.format_stats['ODI']['losses'],
                'draws': team.format_stats['ODI']['draws']
            },
            'Test': {
                'tier': team.format_tiers.get('Test', 1),
                'points': team.format_stats['Test']['points'],
                'wins': team.format_stats['Test']['wins'],
                'losses': team.format_stats['Test']['losses'],
                'draws': team.format_stats['Test']['draws']
            }
        }
        
        return info
    
    def get_tier_standings(self, match_format, tier_num):
        """
        Get standings for a specific tier in a specific format
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
            tier_num: Tier number (1-5)
            
        Returns:
            List of standings dictionaries
        """
        return self.tier_systems[match_format].get_tier_standings(tier_num)
    
    def get_all_standings(self, match_format):
        """
        Get standings for all tiers in a specific format
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
            
        Returns:
            Dictionary with standings for each tier
        """
        all_standings = {}
        
        for tier_num in range(1, 5):  # Tiers 1-4
            all_standings[tier_num] = self.tier_systems[match_format].get_tier_standings(tier_num)
        
        return all_standings
    
    def reset_all_season_stats(self):
        """Reset season statistics for all formats"""
        for match_format in ['T20', 'ODI', 'Test']:
            self.tier_systems[match_format].reset_season_stats()
    
    def get_tier_info(self, match_format, tier_num):
        """
        Get information about a specific tier
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
            tier_num: Tier number (1-5)
            
        Returns:
            Dictionary with tier information
        """
        return self.tier_systems[match_format].get_tier_info(tier_num)
    
    def print_all_standings(self, match_format):
        """
        Print standings for all tiers in a format
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
        """
        for tier_num in range(1, 5):  # Tiers 1-4
            self.tier_systems[match_format].print_standings(tier_num)
    
    def get_format_fixture_count(self, match_format):
        """
        Get total fixture count for a format
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
            
        Returns:
            Total number of fixtures
        """
        total = 0
        for tier_num in range(1, 5):
            fixtures = self.tier_systems[match_format].generate_tier_fixtures(tier_num)
            total += len(fixtures)
        return total
    
    def get_total_fixture_count(self):
        """
        Get total fixture count across all formats
        
        Returns:
            Dictionary with fixture counts per format and total
        """
        counts = {}
        total = 0
        
        for match_format in ['T20', 'ODI', 'Test']:
            count = self.get_format_fixture_count(match_format)
            counts[match_format] = count
            total += count
        
        counts['total'] = total
        return counts
