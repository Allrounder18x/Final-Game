"""
Validation utilities for data integrity
Phase 12: Data validation functions
"""

from cricket_manager.config.constants import PLAYER_CONFIG, FORMAT_CONFIG


def validate_player(player):
    """
    Validate player object
    
    Args:
        player: Player object to validate
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Name validation
    if not player.name or len(player.name.strip()) == 0:
        errors.append("Player name cannot be empty")
    
    # Age validation
    if player.age < 16 or player.age > 45:
        errors.append(f"Invalid age: {player.age} (must be 16-45)")
    
    # Batting skill validation
    if player.batting < PLAYER_CONFIG['min_skill'] or player.batting > PLAYER_CONFIG['max_skill']:
        errors.append(f"Invalid batting skill: {player.batting} (must be {PLAYER_CONFIG['min_skill']}-{PLAYER_CONFIG['max_skill']})")
    
    # Bowling skill validation
    if player.bowling < PLAYER_CONFIG['min_skill'] or player.bowling > PLAYER_CONFIG['max_skill']:
        errors.append(f"Invalid bowling skill: {player.bowling} (must be {PLAYER_CONFIG['min_skill']}-{PLAYER_CONFIG['max_skill']})")
    
    # Fielding skill validation
    if player.fielding < PLAYER_CONFIG['min_skill'] or player.fielding > PLAYER_CONFIG['max_skill']:
        errors.append(f"Invalid fielding skill: {player.fielding} (must be {PLAYER_CONFIG['min_skill']}-{PLAYER_CONFIG['max_skill']})")
    
    # Role validation
    valid_roles = [
        'Opening Batter', 'Top Order Batter', 'Middle Order Batter', 'Lower Order Batter',
        'Wicketkeeper Batter', 'Batting All-Rounder', 'Bowling All-Rounder', 'Genuine All-Rounder',
        'Fast Bowler', 'Medium Pacer', 'Leg Spinner', 'Off Spinner', 'Left Arm Spinner'
    ]
    
    # Check if role contains any valid role substring
    role_valid = any(valid_role in player.role for valid_role in valid_roles)
    if not role_valid:
        errors.append(f"Invalid role: {player.role}")
    
    return len(errors) == 0, errors


def validate_team(team):
    """
    Validate team object
    
    Args:
        team: Team object to validate
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Name validation
    if not team.name or len(team.name.strip()) == 0:
        errors.append("Team name cannot be empty")
    
    # Squad size validation
    if len(team.players) < PLAYER_CONFIG['playing_xi_size']:
        errors.append(f"Team must have at least {PLAYER_CONFIG['playing_xi_size']} players (has {len(team.players)})")
    
    # Playing XI validation
    if hasattr(team, 'playing_xi') and team.playing_xi:
        if len(team.playing_xi) != PLAYER_CONFIG['playing_xi_size']:
            errors.append(f"Playing XI must have exactly {PLAYER_CONFIG['playing_xi_size']} players (has {len(team.playing_xi)})")
        
        # Check for keeper
        keepers = [p for p in team.playing_xi if 'Wicketkeeper' in p.role or 'Keeper' in p.role]
        if len(keepers) == 0:
            errors.append("Playing XI must have at least one wicketkeeper")
        
        # Check for bowlers
        bowlers = [p for p in team.playing_xi if any(x in p.role for x in ['Bowler', 'Spinner', 'Pacer', 'All-Rounder'])]
        if len(bowlers) < 4:
            errors.append(f"Playing XI must have at least 4 bowlers (has {len(bowlers)})")
    
    return len(errors) == 0, errors


def validate_format_type(format_type):
    """
    Validate format type
    
    Args:
        format_type: Format string to validate
    
    Returns:
        Boolean indicating if format is valid
    """
    valid_formats = list(FORMAT_CONFIG.keys())
    return format_type in valid_formats


def validate_tier(tier):
    """
    Validate tier number
    
    Args:
        tier: Tier number to validate
    
    Returns:
        Boolean indicating if tier is valid
    """
    return 1 <= tier <= 5


def validate_match_result(result):
    """
    Validate match result dictionary
    
    Args:
        result: Match result dictionary
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Required fields
    required_fields = ['winner', 'team1', 'team2', 'format']
    for field in required_fields:
        if field not in result:
            errors.append(f"Missing required field: {field}")
    
    # Format validation
    if 'format' in result and not validate_format_type(result['format']):
        errors.append(f"Invalid format: {result['format']}")
    
    # Winner validation
    if 'winner' in result and 'team1' in result and 'team2' in result:
        if result['winner'] not in [result['team1'], result['team2'], 'Draw', 'Tie']:
            errors.append(f"Invalid winner: {result['winner']}")
    
    return len(errors) == 0, errors


def validate_scorecard(scorecard):
    """
    Validate scorecard dictionary
    
    Args:
        scorecard: Scorecard dictionary
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Required fields
    if 'innings' not in scorecard:
        errors.append("Missing innings data")
        return False, errors
    
    # Validate each innings
    for idx, innings in enumerate(scorecard['innings']):
        if 'batting_team' not in innings:
            errors.append(f"Innings {idx+1}: Missing batting team")
        
        if 'bowling_team' not in innings:
            errors.append(f"Innings {idx+1}: Missing bowling team")
        
        if 'total_runs' not in innings:
            errors.append(f"Innings {idx+1}: Missing total runs")
        
        if 'wickets' not in innings:
            errors.append(f"Innings {idx+1}: Missing wickets")
        
        if 'overs' not in innings:
            errors.append(f"Innings {idx+1}: Missing overs")
    
    return len(errors) == 0, errors


def validate_fixture(fixture):
    """
    Validate fixture dictionary
    
    Args:
        fixture: Fixture dictionary
    
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Required fields
    required_fields = ['team1', 'team2', 'format']
    for field in required_fields:
        if field not in fixture:
            errors.append(f"Missing required field: {field}")
    
    # Format validation
    if 'format' in fixture and not validate_format_type(fixture['format']):
        errors.append(f"Invalid format: {fixture['format']}")
    
    # Teams must be different
    if 'team1' in fixture and 'team2' in fixture:
        if fixture['team1'] == fixture['team2']:
            errors.append("Team1 and Team2 must be different")
    
    return len(errors) == 0, errors


def validate_skill_value(skill_value, skill_name="skill"):
    """
    Validate a skill value
    
    Args:
        skill_value: Skill value to validate
        skill_name: Name of the skill (for error messages)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(skill_value, (int, float)):
        return False, f"{skill_name} must be a number"
    
    if skill_value < PLAYER_CONFIG['min_skill'] or skill_value > PLAYER_CONFIG['max_skill']:
        return False, f"{skill_name} must be between {PLAYER_CONFIG['min_skill']} and {PLAYER_CONFIG['max_skill']}"
    
    return True, None


def validate_age(age):
    """
    Validate player age
    
    Args:
        age: Age to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(age, int):
        return False, "Age must be an integer"
    
    if age < 16 or age > 45:
        return False, "Age must be between 16 and 45"
    
    return True, None


def validate_credits(credits):
    """
    Validate credits amount
    
    Args:
        credits: Credits amount to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(credits, (int, float)):
        return False, "Credits must be a number"
    
    if credits < 0:
        return False, "Credits cannot be negative"
    
    return True, None
