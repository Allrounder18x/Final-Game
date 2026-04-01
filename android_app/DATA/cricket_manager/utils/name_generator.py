"""
Player Name Generator
Comprehensive name generation using regional name databases
Phase 11: Enhanced with authentic regional names
"""

import random
from cricket_manager.data.name_database import get_name_lists


# Track used names to avoid duplicates
_used_names = set()


def generate_player_name(team_name=None, ensure_unique=True):
    """
    Generate a random player name based on team nationality
    
    Args:
        team_name: Team name to determine regional names
        ensure_unique: If True, ensure name hasn't been used before
    
    Returns:
        Full player name (e.g., "Virat Kohli", "James Anderson")
    """
    # Get appropriate name lists for the team
    first_names, last_names = get_name_lists(team_name)
    
    # Generate unique name
    max_attempts = 100
    for attempt in range(max_attempts):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Check uniqueness
        if not ensure_unique or full_name not in _used_names:
            if ensure_unique:
                _used_names.add(full_name)
            return full_name
    
    # If we couldn't find a unique name after max_attempts, add a suffix
    base_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    suffix = 1
    while f"{base_name} {suffix}" in _used_names:
        suffix += 1
    
    full_name = f"{base_name} {suffix}"
    _used_names.add(full_name)
    return full_name


def generate_batch_names(team_name, count=15, ensure_unique=True):
    """
    Generate multiple player names for a team
    
    Args:
        team_name: Team name to determine regional names
        count: Number of names to generate
        ensure_unique: If True, ensure all names are unique
    
    Returns:
        List of player names
    """
    names = []
    for _ in range(count):
        name = generate_player_name(team_name, ensure_unique)
        names.append(name)
    return names


def reset_name_tracking():
    """Reset the used names tracker (useful for testing or new game)"""
    global _used_names
    _used_names.clear()


def get_used_names_count():
    """Get count of unique names generated"""
    return len(_used_names)
