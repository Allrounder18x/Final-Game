"""
Helper functions for cricket manager game
"""

from cricket_manager.utils.constants import (
    BATTING_ROLES, ALLROUNDER_ROLES, BOWLING_ROLES,
    PACE_BOWLING_ROLES, SPIN_BOWLING_ROLES
)


def is_batter(role):
    """Check if role is a batting role"""
    return role in BATTING_ROLES or 'Batter' in role


def is_allrounder(role):
    """Check if role is an allrounder role"""
    return role in ALLROUNDER_ROLES or 'Allrounder' in role


def is_bowler(role):
    """Check if role is a bowling role"""
    return role in BOWLING_ROLES or any(x in role for x in ['Spinner', 'Pacer', 'Bowler'])


def is_pace_bowler(role):
    """Check if role is a pace bowling role"""
    return role in PACE_BOWLING_ROLES or any(x in role for x in ['Fast', 'Medium', 'Pace'])


def is_spin_bowler(role):
    """Check if role is a spin bowling role"""
    return role in SPIN_BOWLING_ROLES or any(x in role for x in ['Spin', 'Finger', 'Wrist'])


def is_keeper(role):
    """Check if role is a wicketkeeper role"""
    return 'Keeper' in role


def get_role_category(role):
    """
    Get the primary category of a role
    
    Returns: 'batter', 'allrounder', 'bowler', or 'keeper'
    """
    if is_keeper(role):
        return 'keeper'
    elif is_allrounder(role):
        return 'allrounder'
    elif is_batter(role):
        return 'batter'
    elif is_bowler(role):
        return 'bowler'
    else:
        return 'unknown'


def get_bowling_type(role):
    """
    Get the bowling type from role
    
    Returns: 'pace', 'spin', or None
    """
    if is_pace_bowler(role):
        return 'pace'
    elif is_spin_bowler(role):
        return 'spin'
    else:
        return None


def determine_allrounder_role(batting_skill, bowling_skill, current_role):
    """
    Determine appropriate all-rounder role based on skills
    
    Args:
        batting_skill: Batting skill (0-100)
        bowling_skill: Bowling skill (0-100)
        current_role: Current player role
    
    Returns:
        New allrounder role or None if not applicable
    """
    skill_diff = abs(batting_skill - bowling_skill)
    
    # Only convert if skills are within 20 points
    if skill_diff > 20:
        return None
    
    # Determine bowling type from current role
    bowling_type = "Fast Medium"  # Default
    
    role_lower = current_role.lower()
    if any(spin_type in role_lower for spin_type in ['finger spin', 'finger', 'off break']):
        bowling_type = "Finger Spin"
    elif any(spin_type in role_lower for spin_type in ['wrist spin', 'wrist', 'leg break', 'googly']):
        bowling_type = "Wrist Spin"
    elif any(pace_type in role_lower for pace_type in ['fast', 'quick']):
        bowling_type = "Fast"
    elif any(pace_type in role_lower for pace_type in ['medium pace', 'medium']):
        bowling_type = "Medium Pace"
    
    # Determine all-rounder type based on skill balance
    if batting_skill > bowling_skill:
        if skill_diff <= 10:
            return f"Genuine Allrounder ({bowling_type})"
        else:
            return f"Batting Allrounder ({bowling_type})"
    elif bowling_skill > batting_skill:
        if skill_diff <= 10:
            return f"Genuine Allrounder ({bowling_type})"
        else:
            return f"Bowling Allrounder ({bowling_type})"
    else:  # Equal skills
        return f"Genuine Allrounder ({bowling_type})"


def format_player_stats(player, match_format):
    """
    Format player statistics for display
    
    Args:
        player: Player object
        match_format: 'T20', 'ODI', or 'Test'
    
    Returns:
        Dictionary with formatted stats
    """
    stats = player.stats[match_format]
    
    return {
        'matches': stats['matches'],
        'runs': stats['runs'],
        'average': f"{stats['batting_average']:.2f}",
        'strike_rate': f"{stats['strike_rate']:.2f}",
        'wickets': stats['wickets'],
        'bowling_avg': f"{stats['bowling_average']:.2f}",
        'economy': f"{stats['economy_rate']:.2f}",
        'centuries': stats['centuries'],
        'fifties': stats['fifties'],
        'five_wickets': stats['five_wickets']
    }


def calculate_player_rating(player, match_format):
    """
    Calculate overall player rating for a specific format
    
    Args:
        player: Player object
        match_format: 'T20', 'ODI', or 'Test'
    
    Returns:
        Rating (0-100)
    """
    role_category = get_role_category(player.role)
    
    if role_category == 'batter' or role_category == 'keeper':
        # Batting-focused rating
        rating = player.batting * 0.7 + player.fielding * 0.2 + player.bowling * 0.1
    elif role_category == 'bowler':
        # Bowling-focused rating
        rating = player.bowling * 0.7 + player.fielding * 0.2 + player.batting * 0.1
    else:  # allrounder
        # Balanced rating
        rating = (player.batting + player.bowling) * 0.4 + player.fielding * 0.2
    
    # Adjust based on format-specific stats
    stats = player.stats[match_format]
    if stats['matches'] >= 10:
        # Bonus for good performance
        if stats['batting_average'] > 40:
            rating += 5
        if stats['bowling_average'] > 0 and stats['bowling_average'] < 25:
            rating += 5
    
    return min(100, max(0, rating))


def get_player_form(player, match_format):
    """
    Calculate player form based on recent season stats
    
    Args:
        player: Player object
        match_format: 'T20', 'ODI', or 'Test'
    
    Returns:
        Form rating (0-100)
    """
    season_stats = player.season_stats[match_format]
    
    if season_stats['matches'] == 0:
        return 50  # Neutral form
    
    # Calculate form based on season performance
    runs_per_match = season_stats['runs'] / season_stats['matches']
    wickets_per_match = season_stats['wickets'] / season_stats['matches']
    
    role_category = get_role_category(player.role)
    
    if role_category in ['batter', 'keeper']:
        # Form based on runs
        if runs_per_match > 50:
            return 90
        elif runs_per_match > 30:
            return 70
        elif runs_per_match > 15:
            return 50
        else:
            return 30
    elif role_category == 'bowler':
        # Form based on wickets
        if wickets_per_match > 2:
            return 90
        elif wickets_per_match > 1:
            return 70
        elif wickets_per_match > 0.5:
            return 50
        else:
            return 30
    else:  # allrounder
        # Combined form
        combined = (runs_per_match / 30) + (wickets_per_match / 1.5)
        return min(100, max(0, int(combined * 50)))



# ============================================================================
# PHASE 12: Additional Helper Functions
# ============================================================================

import random
from datetime import datetime


def calculate_batting_average(runs, dismissals):
    """Calculate batting average"""
    if dismissals == 0:
        return runs if runs > 0 else 0.0
    return runs / dismissals


def calculate_bowling_average(runs_conceded, wickets):
    """Calculate bowling average"""
    if wickets == 0:
        return 999.0 if runs_conceded > 0 else 0.0
    return runs_conceded / wickets


def calculate_strike_rate(runs, balls):
    """Calculate batting strike rate"""
    if balls == 0:
        return 0.0
    return (runs / balls) * 100


def calculate_economy_rate(runs_conceded, overs):
    """Calculate bowling economy rate"""
    if overs == 0:
        return 0.0
    return runs_conceded / overs


def calculate_net_run_rate(runs_scored, overs_batted, runs_conceded, overs_bowled):
    """Calculate net run rate"""
    if overs_batted == 0 or overs_bowled == 0:
        return 0.0
    
    run_rate_for = runs_scored / overs_batted
    run_rate_against = runs_conceded / overs_bowled
    
    return run_rate_for - run_rate_against


def format_overs(balls):
    """Format balls as overs (e.g., 120 balls = 20.0 overs)"""
    overs = balls // 6
    remaining_balls = balls % 6
    return f"{overs}.{remaining_balls}"


def balls_to_overs(balls):
    """Convert balls to overs as float"""
    overs = balls // 6
    remaining_balls = balls % 6
    return overs + (remaining_balls / 10)


def overs_to_balls(overs):
    """Convert overs to balls"""
    whole_overs = int(overs)
    partial_over = int((overs - whole_overs) * 10)
    return (whole_overs * 6) + partial_over


def get_match_phase(current_over, format_type):
    """Determine match phase (powerplay, middle, death)"""
    from cricket_manager.config.constants import FORMAT_CONFIG
    
    config = FORMAT_CONFIG[format_type]
    
    if current_over < config['powerplay_overs']:
        return 'powerplay'
    elif current_over >= config['death_overs_start']:
        return 'death'
    else:
        return 'middle'


def weighted_random_choice(items, weights):
    """Choose random item based on weights"""
    return random.choices(items, weights=weights, k=1)[0]


def clamp(value, min_value, max_value):
    """Clamp value between min and max"""
    return max(min_value, min(max_value, value))


def percentage(value, total):
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (value / total) * 100


def format_number(number):
    """Format number with commas"""
    return f"{number:,}"


def get_ordinal(n):
    """Get ordinal suffix for number (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def truncate_text(text, max_length, suffix='...'):
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_current_timestamp():
    """Get current timestamp string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_divide(numerator, denominator, default=0.0):
    """Safely divide, returning default if denominator is 0"""
    if denominator == 0:
        return default
    return numerator / denominator


def format_duration(seconds):
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_large_number(number):
    """Format large numbers with K, M suffixes"""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def calculate_win_percentage(wins, total_matches):
    """Calculate win percentage"""
    if total_matches == 0:
        return 0.0
    return (wins / total_matches) * 100


def get_age_category(age):
    """Get age category for player"""
    if age < 21:
        return 'youth'
    elif age < 28:
        return 'prime'
    elif age < 33:
        return 'experienced'
    else:
        return 'veteran'


def interpolate(value, min_val, max_val, target_min, target_max):
    """Interpolate value from one range to another"""
    if max_val == min_val:
        return target_min
    normalized = (value - min_val) / (max_val - min_val)
    return target_min + (normalized * (target_max - target_min))
