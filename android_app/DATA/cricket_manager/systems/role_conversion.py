"""
Role Conversion System - Automatically converts player roles based on skills
"""


class RoleConversionSystem:
    """
    Automatically converts player roles based on skills
    
    Conversion Rules:
    - Batter → All-rounder: If bowling >= 60
    - Bowler → All-rounder: If batting >= 60
    - All-rounder → Batter: If bowling < 50 and batting >= 70
    - All-rounder → Bowler: If batting < 50 and bowling >= 70
    """
    
    def __init__(self):
        self.conversion_thresholds = {
            'batter_to_allrounder': {'bowling': 60},
            'bowler_to_allrounder': {'batting': 60},
            'allrounder_to_batter': {'batting': 70, 'bowling_max': 50},
            'allrounder_to_bowler': {'bowling': 70, 'batting_max': 50}
        }
    
    def check_conversions(self, team):
        """
        Check all players for role conversions
        
        Args:
            team: Team object
        
        Returns:
            List of conversion events
        """
        conversions = []
        
        for player in team.players:
            old_role = player.role
            new_role = self.determine_role(player)
            
            if new_role != old_role:
                player.role = new_role
                conversions.append({
                    'player': player,
                    'old_role': old_role,
                    'new_role': new_role,
                    'batting': player.batting,
                    'bowling': player.bowling
                })
                
                print(f"[Role Conversion] {player.name}: {old_role} → {new_role}")
        
        return conversions
    
    def check_all_teams(self, teams):
        """
        Check all teams for role conversions
        
        Args:
            teams: List of Team objects
        
        Returns:
            Dict mapping team names to conversion lists
        """
        all_conversions = {}
        
        for team in teams:
            conversions = self.check_conversions(team)
            if conversions:
                all_conversions[team.name] = conversions
        
        return all_conversions
    
    def determine_role(self, player):
        """
        Determine appropriate role based on skills
        
        Args:
            player: Player object
        
        Returns:
            String role name
        """
        
        current_role = player.role
        batting = player.batting
        bowling = player.bowling
        
        # Wicketkeeper stays wicketkeeper (but can become wicketkeeper-batter)
        if 'Wicketkeeper' in current_role:
            if bowling >= 60:
                return 'Wicketkeeper All-Rounder'
            return current_role
        
        # Check for specific role types
        is_batter = any(x in current_role for x in ['Batter', 'Batsman'])
        is_bowler = any(x in current_role for x in ['Bowler', 'Spinner', 'Pacer'])
        is_allrounder = 'All-Rounder' in current_role or 'All-rounder' in current_role
        
        # Batter conversions
        if is_batter and not is_allrounder:
            if bowling >= 60:
                return 'Batting All-Rounder'
            return current_role
        
        # Bowler conversions
        if is_bowler and not is_allrounder:
            if batting >= 60:
                return 'Bowling All-Rounder'
            return current_role
        
        # All-rounder conversions
        if is_allrounder:
            if bowling < 50 and batting >= 70:
                return 'Top Order Batter'
            elif batting < 50 and bowling >= 70:
                # Determine bowling type
                if 'Spin' in current_role or bowling < 75:
                    return 'Off Spinner'
                else:
                    return 'Fast Bowler'
            return current_role
        
        return current_role
    
    def get_conversion_summary(self, conversions_dict):
        """
        Get summary of conversions
        
        Args:
            conversions_dict: Dict from check_all_teams()
        
        Returns:
            String summary
        """
        total = sum(len(convs) for convs in conversions_dict.values())
        
        if total == 0:
            return "No role conversions this season."
        
        summary = f"Role Conversions: {total} player(s)\n"
        summary += "=" * 50 + "\n"
        
        for team_name, conversions in conversions_dict.items():
            if conversions:
                summary += f"\n{team_name}:\n"
                for conv in conversions:
                    player = conv['player']
                    summary += f"  • {player.name}: {conv['old_role']} → {conv['new_role']}\n"
                    summary += f"    (Batting: {conv['batting']}, Bowling: {conv['bowling']})\n"
        
        return summary
