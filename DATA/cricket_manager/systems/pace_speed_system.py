"""
Pace Speed System for Cricket Manager
Handles bowling speed calculations based on player age, role, and skill
"""

import random
import math

# Age-based speed ranges for different bowler types (in kph)
# Fast bowlers max pace is 157k at peak age (25-30) - reduced by 5k
MAX_SPEEDS_BY_AGE = {
    # Fast Bowlers - max 157kph at peak (reduced by 5k)
    'fast': {
        13: 125, 14: 130, 15: 135, 16: 140, 17: 143, 18: 145,
        19: 147, 20: 149, 21: 151, 22: 153, 23: 155, 24: 156,
        25: 157, 26: 157, 27: 157, 28: 157, 29: 157, 30: 157,
        31: 156, 32: 155, 33: 154, 34: 153, 35: 151, 36: 149,
        37: 147, 38: 145, 39: 143, 40: 140, 41: 137, 42: 134,
        43: 131, 44: 128, 45: 125, 46: 122, 47: 119, 48: 116,
        49: 113, 50: 110, 51: 107, 52: 104, 53: 101, 54: 98,
        55: 95, 56: 92, 57: 89, 58: 86, 59: 83, 60: 80
    },
    # Fast Medium Bowlers - max 145kph at peak (reduced by 5k)
    'fast_medium': {
        13: 115, 14: 120, 15: 123, 16: 126, 17: 129, 18: 131,
        19: 133, 20: 135, 21: 137, 22: 139, 23: 141, 24: 143,
        25: 145, 26: 145, 27: 145, 28: 145, 29: 145, 30: 145,
        31: 144, 32: 143, 33: 142, 34: 141, 35: 139, 36: 137,
        37: 135, 38: 133, 39: 131, 40: 129, 41: 127, 42: 125,
        43: 123, 44: 121, 45: 119, 46: 117, 47: 115, 48: 113,
        49: 111, 50: 109, 51: 107, 52: 105, 53: 103, 54: 101,
        55: 99, 56: 97, 57: 95, 58: 93, 59: 91, 60: 89
    },
    # Medium pace: pro "medium" is ~110–130 kph — avoid 90s–low 100s as typical output
    'medium': {
        13: 100, 14: 104, 15: 108, 16: 112, 17: 115, 18: 118,
        19: 120, 20: 122, 21: 124, 22: 125, 23: 126, 24: 127,
        25: 128, 26: 128, 27: 127, 28: 126, 29: 125, 30: 123,
        31: 121, 32: 118, 33: 116, 34: 114, 35: 111, 36: 108,
        37: 105, 38: 102, 39: 99, 40: 96, 41: 93, 42: 90,
        43: 87, 44: 84, 45: 81, 46: 78, 47: 75, 48: 72,
        49: 69, 50: 66, 51: 63, 52: 60, 53: 57, 54: 54,
        55: 51, 56: 48, 57: 45, 58: 42, 59: 39, 60: 36
    },
    # Spin Bowlers - max 90kph at peak (reduced by 5k)
    'spin': {
        13: 65, 14: 67, 15: 69, 16: 71, 17: 73, 18: 75,
        19: 77, 20: 79, 21: 81, 22: 83, 23: 85, 24: 87,
        25: 90, 26: 90, 27: 90, 28: 90, 29: 89, 30: 88,
        31: 86, 32: 84, 33: 82, 34: 80, 35: 77, 36: 74,
        37: 71, 38: 68, 39: 65, 40: 62, 41: 59, 42: 56,
        43: 53, 44: 50, 45: 47, 46: 44, 47: 41, 48: 38,
        49: 35, 50: 32, 51: 29, 52: 26, 53: 23, 54: 20,
        55: 17, 56: 14, 57: 11, 58: 8, 59: 5, 60: 2
    }
}

# Minimum speeds for each bowler type (reduced by 5k)
MIN_SPEEDS = {
    'fast': 120,
    'fast_medium': 110,
    'medium': 100,
    'spin': 60
}

# Role to bowler type mapping - EVERY ROLE MUST BE DEFINED HERE
ROLE_TO_BOWLER_TYPE = {
    # Pure bowling roles
    'Fast Bowler': 'fast',
    'Fast Bowlers': 'fast',
    'fast bowler': 'fast',
    'fast bowlers': 'fast',
    'Fast': 'fast',
    'fast': 'fast',
    
    'Fast Medium Pacer': 'fast_medium',
    'Fast Medium Pacers': 'fast_medium',
    'fast medium pacer': 'fast_medium',
    'fast medium pacers': 'fast_medium',
    'Fast Medium': 'fast_medium',
    'fast medium': 'fast_medium',
    
    'Medium Pacer': 'medium',
    'Medium Pacers': 'medium',
    'medium pacer': 'medium',
    'medium pacers': 'medium',
    'Medium': 'medium',
    'medium': 'medium',
    'Pacer': 'medium',
    'pacer': 'medium',
    
    'Finger Spinner': 'spin',
    'Finger Spinners': 'spin',
    'finger spinner': 'spin',
    'finger spinners': 'spin',
    'Wrist Spinner': 'spin',
    'Wrist Spinners': 'spin',
    'wrist spinner': 'spin',
    'wrist spinners': 'spin',
    'Spinner': 'spin',
    'Spinners': 'spin',
    'spinner': 'spin',
    'spinners': 'spin',
    'Spin': 'spin',
    'spin': 'spin',
    'Leg Spinner': 'spin',
    'leg spinner': 'spin',
    'Off Spinner': 'spin',
    'off spinner': 'spin',
    
    # Generic all-rounder roles (default to spin for bowling all-rounders, medium pace for batting all-rounders)
    'Bowling All-Rounder': 'spin',
    'bowling all-rounder': 'spin',
    'Bowling Allrounder': 'spin',
    'bowling allrounder': 'spin',
    'Batting All-Rounder': 'medium',
    'batting all-rounder': 'medium',
    'Genuine All-Rounder': 'medium',
    'genuine all-rounder': 'medium',
    'All-Rounder': 'medium',
    'all-rounder': 'medium',
    
    # Allrounder roles with pace bowling
    'Batting Allrounder (Fast)': 'fast',
    'batting allrounder (fast)': 'fast',
    'Batting Allrounder (Fast Medium)': 'fast_medium',
    'batting allrounder (fast medium)': 'fast_medium',
    'Batting Allrounder (Medium Pace)': 'medium',
    'batting allrounder (medium pace)': 'medium',
    
    'Bowling Allrounder (Fast)': 'fast',
    'bowling allrounder (fast)': 'fast',
    'Bowling Allrounder (Fast Medium)': 'fast_medium',
    'bowling allrounder (fast medium)': 'fast_medium',
    'Bowling Allrounder (Medium Pace)': 'medium',
    'bowling allrounder (medium pace)': 'medium',
    
    'Genuine Allrounder (Fast)': 'fast',
    'genuine allrounder (fast)': 'fast',
    'Genuine Allrounder (Fast Medium)': 'fast_medium',
    'genuine allrounder (fast medium)': 'fast_medium',
    'Genuine Allrounder (Medium Pace)': 'medium',
    'genuine allrounder (medium pace)': 'medium',
    
    # Allrounder roles with spin bowling
    'Batting Allrounder (Wrist Spin)': 'spin',
    'batting allrounder (wrist spin)': 'spin',
    'Batting Allrounder (Finger Spin)': 'spin',
    'batting allrounder (finger spin)': 'spin',
    
    'Bowling Allrounder (Wrist Spin)': 'spin',
    'bowling allrounder (wrist spin)': 'spin',
    'Bowling Allrounder (Finger Spin)': 'spin',
    'bowling allrounder (finger spin)': 'spin',
    
    'Genuine Allrounder (Wrist Spin)': 'spin',
    'genuine allrounder (wrist spin)': 'spin',
    'Genuine Allrounder (Finger Spin)': 'spin',
    'genuine allrounder (finger spin)': 'spin',
    
    # Batting roles - no bowling
    'Opening Batter': None,
    'opening batter': None,
    'Middle Order Batter': None,
    'middle order batter': None,
    'Lower Order Batter': None,
    'lower order batter': None,
    'Keeper Batter': None,
    'keeper batter': None,
    'Batter': None,
    'batter': None,
    'Batsman': None,
    'batsman': None,
    'Wicketkeeper': None,
    'wicketkeeper': None,
    'Keeper': None,
    'keeper': None,
}


def get_bowler_type_from_role(role):
    """Get bowler type from role string - handles all variations"""
    if not role:
        return None
    
    role_str = str(role).strip()
    
    # Direct lookup
    if role_str in ROLE_TO_BOWLER_TYPE:
        return ROLE_TO_BOWLER_TYPE[role_str]
    
    # Case-insensitive lookup
    role_lower = role_str.lower()
    if role_lower in ROLE_TO_BOWLER_TYPE:
        return ROLE_TO_BOWLER_TYPE[role_lower]
    
    # Keyword-based detection for any role variations
    # Check for spin first (so spinner allrounders get spin, not pace)
    if any(spin_keyword in role_lower for spin_keyword in ['wrist spin', 'finger spin', 'leg spin', 'off spin', 'spinner', 'spin']):
        return 'spin'
    
    # Check for fast
    if 'fast' in role_lower and 'fast medium' not in role_lower and 'medium' not in role_lower:
        return 'fast'
    
    # Check for fast medium
    if 'fast medium' in role_lower or ('fast' in role_lower and 'medium' in role_lower):
        return 'fast_medium'
    
    # Check for medium pace
    if 'medium' in role_lower or 'pacer' in role_lower:
        return 'medium'
    
    # Check for allrounder with bowling type
    if 'allrounder' in role_lower or 'all-rounder' in role_lower:
        # Check for specific bowling types first
        if any(spin_keyword in role_lower for spin_keyword in ['wrist', 'finger', 'leg', 'off', 'spin']):
            return 'spin'
        elif 'fast' in role_lower:
            return 'fast'
        elif 'medium' in role_lower:
            return 'medium'
        # Generic all-rounder roles - use bowling skill to determine type
        elif 'bowling' in role_lower:
            # Bowling all-rounders default to spin (most common)
            return 'spin'
        else:
            # Batting all-rounders and genuine all-rounders default to medium pace
            return 'medium'
    
    # No bowling type found - this is a batter/keeper
    return None


def initialize_pace_speeds(player):
    """Initialize pace speed attributes for a player"""
    age = player.age
    role = player.role
    bowling_skill = player.bowling
    
    # Determine bowler type from role
    bowler_type = get_bowler_type_from_role(role)
    
    # If not a bowler or bowling skill too low, no pace attributes
    if bowler_type is None or bowling_skill < 40:
        player.avg_pace = 0.0
        player.top_pace = 0.0
        player.speed_potential = 0.0
        return
    
    # Get age-appropriate max speed
    age_speeds = MAX_SPEEDS_BY_AGE[bowler_type]
    if age in age_speeds:
        max_speed = age_speeds[age]
    else:
        # Find closest age
        available_ages = sorted(age_speeds.keys())
        if age < min(available_ages):
            max_speed = age_speeds[min(available_ages)]
        elif age > max(available_ages):
            max_speed = age_speeds[max(available_ages)]
        else:
            # Find nearest age
            closest_age = min(available_ages, key=lambda x: abs(x - age))
            max_speed = age_speeds[closest_age]
    
    min_speed = MIN_SPEEDS[bowler_type]
    
    # Calculate speed based on bowling skill (40-99 skill range)
    skill_factor = (bowling_skill - 40) / 59  # Normalize to 0-1
    
    # Add some randomness for natural variation
    random_factor = random.uniform(0.85, 1.0)
    
    # Calculate average speed
    avg_speed = min_speed + (max_speed - min_speed) * skill_factor * random_factor
    # Adult medium pacers should not sit in high-90s / low-100s when peak allows (realistic ~110–130 kph)
    if bowler_type == 'medium' and age >= 18 and max_speed >= 112:
        avg_speed = max(avg_speed, min(108, max_speed - 4))
    
    # Calculate top speed (usually 3-8 kph faster than average, depending on bowler type)
    if bowler_type == 'spin':
        speed_variation = random.uniform(2, 5)  # Spinners have less variation
    elif bowler_type == 'medium':
        speed_variation = random.uniform(3, 6)
    elif bowler_type == 'fast_medium':
        speed_variation = random.uniform(4, 7)
    else:  # fast
        speed_variation = random.uniform(5, 8)
    
    top_speed = avg_speed + speed_variation
    
    # Cap top speed at age-appropriate maximum
    top_speed = min(top_speed, max_speed)
    
    # Calculate speed potential for future development
    if age <= 20:
        player.speed_potential = random.uniform(0.8, 1.0)  # Very high potential
    elif age <= 25:
        player.speed_potential = random.uniform(0.7, 1.0)  # High potential
    elif age <= 30:
        player.speed_potential = random.uniform(0.3, 0.7)  # Medium potential
    else:
        player.speed_potential = random.uniform(0.0, 0.3)  # Low potential
    
    # Set the attributes
    player.avg_pace = round(avg_speed, 1)
    player.top_pace = round(top_speed, 1)


def update_pace_speeds_for_season(player, season_increment=True):
    """Update pace speeds based on age progression/regression with new formulas"""
    age = player.age
    role = player.role
    
    # Determine bowler type from role
    bowler_type = get_bowler_type_from_role(role)
    
    # Only update for bowlers with existing pace attributes
    if bowler_type is None:
        return
    
    if not hasattr(player, 'avg_pace') or player.avg_pace == 0:
        # Initialize if not already set
        initialize_pace_speeds(player)
        return
    
    # NEW PROGRESSION FORMULAS:
    # Young bowlers (13-20): -1 to +5
    # After 21: -2 to +3
    # After 28: -2 to +2
    # After 31: -2 to +1
    # After 34: -5 to -1
    # After 37: -6 to -5
    
    if season_increment:
        # Player is getting older
        if age <= 20:
            # Young bowlers (13-20): -1 to +5
            speed_change = random.uniform(-1.0, 5.0)
        elif age <= 27:
            # After 21: -2 to +3
            speed_change = random.uniform(-2.0, 3.0)
        elif age <= 30:
            # After 28: -2 to +2
            speed_change = random.uniform(-2.0, 2.0)
        elif age <= 33:
            # After 31: -2 to +1
            speed_change = random.uniform(-2.0, 1.0)
        elif age <= 36:
            # After 34: -5 to -1
            speed_change = random.uniform(-5.0, -1.0)
        else:
            # After 37: -6 to -5
            speed_change = random.uniform(-6.0, -5.0)
        
        player.avg_pace += speed_change
        player.top_pace += speed_change * 0.8
    else:
        # Season regression (for testing or special cases)
        if age <= 20:
            # Young players might regress slightly
            regression = random.uniform(-0.5, 0.2)
        elif age <= 27:
            # Prime age - minimal regression
            regression = random.uniform(-0.2, 0.1)
        elif age <= 30:
            # Still good - minimal regression
            regression = random.uniform(-0.3, 0.0)
        elif age <= 33:
            # Starting to decline
            regression = random.uniform(-0.8, -0.2)
        elif age <= 36:
            # Declining faster
            regression = random.uniform(-2.0, -0.5)
        else:
            # Rapid decline
            regression = random.uniform(-3.0, -1.5)
        
        player.avg_pace += regression
        player.top_pace += regression * 0.8
    
    # Ensure speeds don't go below minimum
    min_speed = MIN_SPEEDS[bowler_type]
    player.avg_pace = max(player.avg_pace, min_speed)
    player.top_pace = max(player.top_pace, min_speed + 2)
    
    # Also ensure speeds don't exceed max for age
    age_speeds = MAX_SPEEDS_BY_AGE[bowler_type]
    if age in age_speeds:
        max_speed = age_speeds[age]
    else:
        available_ages = sorted(age_speeds.keys())
        if age < min(available_ages):
            max_speed = age_speeds[min(available_ages)]
        elif age > max(available_ages):
            max_speed = age_speeds[max(available_ages)]
        else:
            closest_age = min(available_ages, key=lambda x: abs(x - age))
            max_speed = age_speeds[closest_age]
    
    player.avg_pace = min(player.avg_pace, max_speed)
    player.top_pace = min(player.top_pace, max_speed)
    if bowler_type == 'medium' and age >= 18 and max_speed >= 112:
        player.avg_pace = max(player.avg_pace, min(108, max_speed - 4))
        player.avg_pace = min(player.avg_pace, max_speed)
        player.top_pace = max(player.top_pace, min(max_speed, player.avg_pace + 2))
        player.top_pace = min(player.top_pace, max_speed)
    
    # Round to 1 decimal place
    player.avg_pace = round(player.avg_pace, 1)
    player.top_pace = round(player.top_pace, 1)


def calculate_bowler_speed(player, aggression_level=1.0):
    """Calculate bowling speed for a specific delivery"""
    # Handle both Player objects and dictionary-style players
    if hasattr(player, 'role'):
        role = player.role
        age = getattr(player, 'age', 25)
    elif isinstance(player, dict):
        role = player.get('role', '')
        age = player.get('age', 25)
    else:
        role = str(player)
        age = 25
    
    # Determine bowler type from role
    bowler_type = get_bowler_type_from_role(role)
    
    # If not a bowler, return 0
    if bowler_type is None:
        return 0.0
    
    # Check if player has pace attributes
    if hasattr(player, 'avg_pace') and player.avg_pace > 0:
        # Use player's pace attributes
        avg_speed = player.avg_pace
        top_speed = player.top_pace
        
        # Get age-appropriate max speed
        age_speeds = MAX_SPEEDS_BY_AGE[bowler_type]
        if age in age_speeds:
            age_max_speed = age_speeds[age]
        else:
            available_ages = sorted(age_speeds.keys())
            if age < min(available_ages):
                age_max_speed = age_speeds[min(available_ages)]
            elif age > max(available_ages):
                age_max_speed = age_speeds[max(available_ages)]
            else:
                closest_age = min(available_ages, key=lambda x: abs(x - age))
                age_max_speed = age_speeds[closest_age]
        
        # Cap speeds at age-appropriate maximum
        top_speed = min(top_speed, age_max_speed)
        avg_speed = min(avg_speed, age_max_speed - 5)  # avg should be below max
        
        # STRICT speed caps based on bowler type (reduced by 5k)
        if bowler_type == 'fast':
            # For fast bowlers, only 20% can bowl 145kph+
            if top_speed > 145:
                potential = getattr(player, 'potential', 70)
                bowling_skill = getattr(player, 'bowling', 70)
                # Elite if high potential OR high bowling skill (more inclusive)
                is_elite = potential >= 80 or bowling_skill >= 82
                if not is_elite:
                    top_speed = min(top_speed, 144)
                    avg_speed = min(avg_speed, 140)
        elif bowler_type == 'fast_medium':
            # Fast medium capped at 140
            top_speed = min(top_speed, 140)
            avg_speed = min(avg_speed, 135)
        elif bowler_type == 'medium':
            # Medium pace: align with age table peak ~128 kph
            top_speed = min(top_speed, 128)
            avg_speed = min(avg_speed, 123)
        elif bowler_type == 'spin':
            # Spin capped at 90
            top_speed = min(top_speed, 90)
            avg_speed = min(avg_speed, 85)
        
        # Calculate variation based on bowler type
        if bowler_type == 'spin':
            variation = random.uniform(-3, 2)  # Less variation for spinners
        elif bowler_type == 'medium':
            variation = random.uniform(-2, 4)
        elif bowler_type == 'fast_medium':
            variation = random.uniform(-6, 4)
        else:  # fast
            variation = random.uniform(-8, 5)
        
        # Aggression affects speed (more aggressive = faster)
        aggression_bonus = (aggression_level - 1.0) * 5
        
        # Calculate final speed
        speed = avg_speed + variation + aggression_bonus
        
        # Ensure speed is within reasonable bounds (medium: tighter floor so balls stay near real medium pace)
        speed = max(speed, avg_speed - (5 if bowler_type == 'medium' else 10))
        speed = min(speed, top_speed)
        
        return round(speed, 1)
    else:
        # No pace attributes - calculate based on age and role
        age_speeds = MAX_SPEEDS_BY_AGE[bowler_type]
        if age in age_speeds:
            max_speed = age_speeds[age]
        else:
            available_ages = sorted(age_speeds.keys())
            if age < min(available_ages):
                max_speed = age_speeds[min(available_ages)]
            elif age > max(available_ages):
                max_speed = age_speeds[max(available_ages)]
            else:
                closest_age = min(available_ages, key=lambda x: abs(x - age))
                max_speed = age_speeds[closest_age]
        
        min_speed = MIN_SPEEDS[bowler_type]
        
        # For fast bowlers, only 20% can bowl 145kph+
        if bowler_type == 'fast' and max_speed > 145:
            # 80% of fast bowlers capped below 145kph
            if random.random() < 0.8:
                max_speed = min(max_speed, 144)  # Cap at 144 for 80%
        
        # STRICT caps for non-fast bowlers (reduced by 5k)
        if bowler_type == 'fast_medium':
            max_speed = min(max_speed, 140)  # Fast medium capped at 140
        elif bowler_type == 'medium':
            max_speed = min(max_speed, 128)
        elif bowler_type == 'spin':
            max_speed = min(max_speed, 90)   # Spin capped at 90
        
        # Random speed within range
        speed = random.uniform(min_speed, max_speed)
        
        # Aggression affects speed
        aggression_bonus = (aggression_level - 1.0) * 5
        speed += aggression_bonus
        
        return round(speed, 1)


def get_speed_category(speed):
    """Get speed category for display purposes"""
    if speed >= 155:
        return "Ultra Express"
    elif speed >= 145:
        return "Express"
    elif speed >= 140:
        return "Fast"
    elif speed >= 135:
        return "Fast-Medium"
    elif speed >= 130:
        return "Medium-Fast"
    elif speed >= 120:
        return "Medium"
    elif speed >= 110:
        return "Medium-Slow"
    elif speed >= 95:
        return "Slow-Medium"
    else:
        return "Slow"


def get_bowler_pace_range(role, age):
    """Get the min and max pace for a bowler based on role and age"""
    bowler_type = get_bowler_type_from_role(role)
    
    if bowler_type is None:
        return None, None
    
    age_speeds = MAX_SPEEDS_BY_AGE[bowler_type]
    if age in age_speeds:
        max_speed = age_speeds[age]
    else:
        available_ages = sorted(age_speeds.keys())
        if age < min(available_ages):
            max_speed = age_speeds[min(available_ages)]
        elif age > max(available_ages):
            max_speed = age_speeds[max(available_ages)]
        else:
            closest_age = min(available_ages, key=lambda x: abs(x - age))
            max_speed = age_speeds[closest_age]
    
    min_speed = MIN_SPEEDS[bowler_type]
    
    return min_speed, max_speed
