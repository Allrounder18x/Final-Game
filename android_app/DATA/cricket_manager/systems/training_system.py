"""
Training System - Manages player training and skill improvement
"""

import random


class TrainingSystem:
    """
    Manages player training and skill improvement
    
    Training Rules:
    - Players can train Batting, Bowling, or Fielding
    - Success rate depends on age and current skill
    - Younger players improve faster
    - Higher skills are harder to improve
    - Each training session costs 1 training point
    - Teams get 5 training points per season
    """
    
    def __init__(self):
        self.training_points_per_season = 5
        
        # Age-based success rate modifiers
        self.age_modifiers = {
            'young': 1.2,      # Under 25
            'prime': 1.0,      # 25-30
            'veteran': 0.7,    # 31-35
            'old': 0.4         # Over 35
        }
        
        # Skill level difficulty modifiers
        self.skill_modifiers = {
            'low': 0.8,        # Under 50
            'medium': 0.6,     # 50-70
            'high': 0.4,       # 71-85
            'elite': 0.2       # Over 85
        }
    
    def get_age_category(self, age):
        """Get age category for training modifier"""
        if age < 25:
            return 'young'
        elif age <= 30:
            return 'prime'
        elif age <= 35:
            return 'veteran'
        else:
            return 'old'
    
    def get_skill_category(self, skill_value):
        """Get skill category for training modifier"""
        if skill_value < 50:
            return 'low'
        elif skill_value <= 70:
            return 'medium'
        elif skill_value <= 85:
            return 'high'
        else:
            return 'elite'
    
    def calculate_success_rate(self, player, skill_type):
        """
        Calculate training success rate
        
        Args:
            player: Player object
            skill_type: 'batting', 'bowling', or 'fielding'
        
        Returns:
            Float between 0.0 and 1.0
        """
        
        # Get current skill value
        if skill_type == 'batting':
            current_skill = player.batting
        elif skill_type == 'bowling':
            current_skill = player.bowling
        elif skill_type == 'fielding':
            current_skill = player.fielding
        else:
            return 0.0
        
        # Base success rate
        base_rate = 0.6
        
        # Apply age modifier
        age_category = self.get_age_category(player.age)
        age_mod = self.age_modifiers[age_category]
        
        # Apply skill modifier
        skill_category = self.get_skill_category(current_skill)
        skill_mod = self.skill_modifiers[skill_category]
        
        # Calculate final rate
        success_rate = base_rate * age_mod * skill_mod
        
        # Cap between 0.1 and 0.9
        success_rate = max(0.1, min(0.9, success_rate))
        
        return success_rate
    
    def train_player(self, player, skill_type):
        """
        Train a player in a specific skill
        
        Args:
            player: Player object
            skill_type: 'batting', 'bowling', or 'fielding'
        
        Returns:
            Tuple (success: bool, old_value: int, new_value: int, message: str)
        """
        
        # Get current skill
        if skill_type == 'batting':
            current_skill = player.batting
        elif skill_type == 'bowling':
            current_skill = player.bowling
        elif skill_type == 'fielding':
            current_skill = player.fielding
        else:
            return False, 0, 0, "Invalid skill type"
        
        # Check if already at max
        if current_skill >= 99:
            return False, current_skill, current_skill, f"{skill_type.title()} already at maximum"
        
        # Calculate success rate
        success_rate = self.calculate_success_rate(player, skill_type)
        
        # Attempt training
        if random.random() < success_rate:
            # Success - improve skill
            improvement = random.randint(1, 3)
            new_skill = min(99, current_skill + improvement)
            
            # Update player
            if skill_type == 'batting':
                player.batting = new_skill
            elif skill_type == 'bowling':
                player.bowling = new_skill
            elif skill_type == 'fielding':
                player.fielding = new_skill
            
            message = f"Training successful! {skill_type.title()} improved by {improvement} points"
            return True, current_skill, new_skill, message
        else:
            # Failure - no improvement
            message = f"Training unsuccessful. {skill_type.title()} remains at {current_skill}"
            return False, current_skill, current_skill, message
    
    def get_training_info(self, player, skill_type):
        """
        Get training information for display
        
        Returns:
            Dict with success rate, current skill, potential improvement
        """
        
        if skill_type == 'batting':
            current_skill = player.batting
        elif skill_type == 'bowling':
            current_skill = player.bowling
        elif skill_type == 'fielding':
            current_skill = player.fielding
        else:
            return None
        
        success_rate = self.calculate_success_rate(player, skill_type)
        
        return {
            'skill_type': skill_type,
            'current_skill': current_skill,
            'success_rate': success_rate,
            'success_percentage': int(success_rate * 100),
            'age_category': self.get_age_category(player.age),
            'skill_category': self.get_skill_category(current_skill),
            'max_improvement': 3,
            'at_maximum': current_skill >= 99
        }
    
    def reset_training_points(self, team):
        """Reset team's training points for new season"""
        team.training_points = self.training_points_per_season
        print(f"[Training] {team.name} received {self.training_points_per_season} training points")
    
    def use_training_point(self, team):
        """
        Use one training point
        
        Returns:
            bool: True if point was used, False if no points available
        """
        if not hasattr(team, 'training_points'):
            team.training_points = 0
        
        if team.training_points > 0:
            team.training_points -= 1
            return True
        return False
    
    def get_training_points(self, team):
        """Get team's current training points"""
        if not hasattr(team, 'training_points'):
            team.training_points = self.training_points_per_season
        return team.training_points
