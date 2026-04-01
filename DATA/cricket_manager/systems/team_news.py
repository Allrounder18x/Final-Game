"""
Team News System - Generate team news and headlines
"""

import random


class TeamNewsSystem:
    """
    Generate team news and headlines
    
    News Types:
    - Player milestones (100 matches, 1000 runs, 100 wickets)
    - Form updates (hot streak, cold streak)
    - Role conversions
    - Retirements
    - Youth promotions
    """
    
    def __init__(self):
        self.news_items = []
    
    def generate_season_news(self, teams, format_type='T20'):
        """
        Generate news for the season
        
        Args:
            teams: List of Team objects
            format_type: 'T20', 'ODI', or 'Test'
        
        Returns:
            List of news items
        """
        self.news_items = []
        
        for team in teams:
            # Check for milestones
            self.check_milestones(team, format_type)
            
            # Check for form
            self.check_form(team, format_type)
        
        return self.news_items
    
    def check_milestones(self, team, format_type):
        """Check for player milestones"""
        
        for player in team.players:
            # Check if player has career stats
            if not hasattr(player, 'career_stats'):
                continue
            
            career_stats = player.career_stats.get(format_type, {})
            
            # 100 matches milestone
            matches = career_stats.get('matches', 0)
            if matches == 100:
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'high',
                    'headline': f"🎉 {player.name} Reaches 100 {format_type} Matches!",
                    'body': f"{player.name} of {team.name} has played 100 {format_type} matches. "
                           f"A remarkable achievement in their career.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{matches} matches"
                })
            
            # 50 matches milestone
            elif matches == 50:
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'medium',
                    'headline': f"🎊 {player.name} Completes 50 {format_type} Matches",
                    'body': f"{player.name} has reached the 50-match mark in {format_type} cricket.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{matches} matches"
                })
            
            # 1000 runs milestone
            runs = career_stats.get('runs', 0)
            if runs >= 1000 and runs % 1000 < 100:  # Just crossed milestone
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'high',
                    'headline': f"🏏 {player.name} Scores {runs} Career Runs!",
                    'body': f"{player.name} has reached {runs} runs in {format_type} cricket. "
                           f"An outstanding batting achievement.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{runs} runs"
                })
            
            # 500 runs milestone
            elif runs >= 500 and runs < 600:
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'medium',
                    'headline': f"🏏 {player.name} Reaches 500 Career Runs",
                    'body': f"{player.name} has scored 500+ runs in {format_type} cricket.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{runs} runs"
                })
            
            # 100 wickets milestone
            wickets = career_stats.get('wickets', 0)
            if wickets >= 100 and wickets % 100 < 10:  # Just crossed milestone
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'high',
                    'headline': f"🎯 {player.name} Takes {wickets} Career Wickets!",
                    'body': f"{player.name} has taken {wickets} wickets in {format_type} cricket. "
                           f"A phenomenal bowling record.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{wickets} wickets"
                })
            
            # 50 wickets milestone
            elif wickets >= 50 and wickets < 60:
                self.news_items.append({
                    'type': 'milestone',
                    'priority': 'medium',
                    'headline': f"🎯 {player.name} Reaches 50 Career Wickets",
                    'body': f"{player.name} has taken 50+ wickets in {format_type} cricket.",
                    'player': player.name,
                    'team': team.name,
                    'stat': f"{wickets} wickets"
                })
    
    def check_form(self, team, format_type):
        """Check player form"""
        
        for player in team.players:
            # Check if player has season stats
            if not hasattr(player, 'season_stats'):
                continue
            
            season_stats = player.season_stats.get(format_type, {})
            matches = season_stats.get('matches', 0)
            
            if matches < 5:
                continue
            
            # Hot batting form
            if any(x in player.role for x in ['Batter', 'All-Rounder', 'Wicketkeeper']):
                runs = season_stats.get('runs', 0)
                avg = runs / max(1, matches)
                
                if avg >= 50:
                    self.news_items.append({
                        'type': 'form',
                        'priority': 'high',
                        'headline': f"🔥 {player.name} in Sensational Form!",
                        'body': f"{player.name} is averaging {avg:.1f} this season with {runs} runs "
                               f"in {matches} matches. Absolutely unstoppable!",
                        'player': player.name,
                        'team': team.name,
                        'stat': f"Avg: {avg:.1f}"
                    })
                elif avg >= 35:
                    self.news_items.append({
                        'type': 'form',
                        'priority': 'medium',
                        'headline': f"📈 {player.name} in Good Form",
                        'body': f"{player.name} is averaging {avg:.1f} this season.",
                        'player': player.name,
                        'team': team.name,
                        'stat': f"Avg: {avg:.1f}"
                    })
            
            # Hot bowling form
            if any(x in player.role for x in ['Bowler', 'All-Rounder', 'Spinner', 'Pacer']):
                wickets = season_stats.get('wickets', 0)
                wpm = wickets / max(1, matches)
                
                if wpm >= 3.0:
                    self.news_items.append({
                        'type': 'form',
                        'priority': 'high',
                        'headline': f"🔥 {player.name} on Fire with the Ball!",
                        'body': f"{player.name} is taking {wpm:.1f} wickets per match this season "
                               f"with {wickets} wickets in {matches} matches. Devastating!",
                        'player': player.name,
                        'team': team.name,
                        'stat': f"WPM: {wpm:.1f}"
                    })
                elif wpm >= 2.0:
                    self.news_items.append({
                        'type': 'form',
                        'priority': 'medium',
                        'headline': f"📈 {player.name} Bowling Well",
                        'body': f"{player.name} is taking {wpm:.1f} wickets per match this season.",
                        'player': player.name,
                        'team': team.name,
                        'stat': f"WPM: {wpm:.1f}"
                    })
    
    def add_role_conversion_news(self, conversions_dict):
        """
        Add news items for role conversions
        
        Args:
            conversions_dict: Dict from RoleConversionSystem.check_all_teams()
        """
        for team_name, conversions in conversions_dict.items():
            for conv in conversions:
                player = conv['player']
                old_role = conv['old_role']
                new_role = conv['new_role']
                
                self.news_items.append({
                    'type': 'role_change',
                    'priority': 'medium',
                    'headline': f"🔄 {player.name} Role Change: {old_role} → {new_role}",
                    'body': f"{player.name} of {team_name} has been reclassified as a {new_role} "
                           f"based on recent performances (Batting: {conv['batting']}, "
                           f"Bowling: {conv['bowling']}).",
                    'player': player.name,
                    'team': team_name,
                    'stat': f"{old_role} → {new_role}"
                })
    
    def add_milestone_news(self, player_name, team_name, description):
        """Add a single milestone news item (e.g. 100 Tests, 5000 runs)."""
        self.news_items.append({
            'type': 'milestone',
            'priority': 'high',
            'headline': f"🎉 {player_name} – {description}",
            'body': f"{player_name} of {team_name} has achieved {description}. Congratulations!",
            'player': player_name,
            'team': team_name,
            'stat': description
        })
    
    def add_record_news(self, team_name, record_type, description):
        """Add a team record broken notification."""
        labels = {'highest_total': 'Highest team total', 'lowest_total': 'Lowest total (all out)', 'biggest_win_runs': 'Biggest win (runs)', 'biggest_win_wickets': 'Biggest win (wickets)'}
        label = labels.get(record_type, record_type)
        self.news_items.append({
            'type': 'record',
            'priority': 'medium',
            'headline': f"📊 {team_name} – New record: {label}",
            'body': f"{team_name} have set a new record: {description}.",
            'team': team_name,
            'stat': description
        })
    
    def add_retirement_news(self, retirements):
        """
        Add news items for retirements
        
        Args:
            retirements: List of retirement dicts from game engine
        """
        for retirement in retirements:
            player_name = retirement['player']
            team_name = retirement['team']
            age = retirement['age']
            
            self.news_items.append({
                'type': 'retirement',
                'priority': 'high',
                'headline': f"👋 {player_name} Announces Retirement",
                'body': f"{player_name} of {team_name} has retired from cricket at age {age}. "
                       f"Thank you for the memories!",
                'player': player_name,
                'team': team_name,
                'stat': f"Age: {age}"
            })
    
    def add_youth_promotion_news(self, promotions):
        """
        Add news items for youth promotions
        
        Args:
            promotions: List of promotion dicts from game engine
        """
        for promotion in promotions:
            player_name = promotion['player']
            team_name = promotion['team']
            
            self.news_items.append({
                'type': 'youth_promotion',
                'priority': 'medium',
                'headline': f"⭐ {player_name} Promoted to Senior Squad",
                'body': f"Young talent {player_name} has been promoted to {team_name}'s senior squad. "
                       f"Exciting times ahead!",
                'player': player_name,
                'team': team_name,
                'stat': "Youth → Senior"
            })
    
    def get_random_news(self, count=5):
        """
        Get random news items
        
        Args:
            count: Number of items to return
        
        Returns:
            List of news items
        """
        if len(self.news_items) <= count:
            return self.news_items
        return random.sample(self.news_items, count)
    
    def get_top_news(self, count=5):
        """
        Get top priority news items
        
        Args:
            count: Number of items to return
        
        Returns:
            List of news items sorted by priority
        """
        # Sort by priority (high > medium > low)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_news = sorted(
            self.news_items,
            key=lambda x: priority_order.get(x.get('priority', 'low'), 0),
            reverse=True
        )
        
        return sorted_news[:count]
    
    def get_team_news(self, team_name, count=5):
        """
        Get news for specific team
        
        Args:
            team_name: Name of team
            count: Number of items to return
        
        Returns:
            List of news items for that team
        """
        team_news = [item for item in self.news_items if item.get('team') == team_name]
        return team_news[:count]
    
    def clear_news(self):
        """Clear all news items"""
        self.news_items = []
