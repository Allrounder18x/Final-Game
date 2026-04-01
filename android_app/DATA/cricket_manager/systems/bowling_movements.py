"""
Bowling Movement System
Dynamic bowling movement attributes based on skill and role
Ported from gamer_2024.py with exact formulas
"""

import random


def determine_bowler_type(role):
    """Determine if a bowler is pace or spin based on their role"""
    role_lower = role.lower()
    
    # Spin bowlers
    if any(spin_type in role_lower for spin_type in ['spin', 'finger', 'wrist', 'off break', 'leg break']):
        return "spin"
    
    # Pace bowlers  
    elif any(pace_type in role_lower for pace_type in ['fast', 'medium', 'seam', 'pace']):
        return "pace"
    
    # All-rounders - determine by bowling skill level
    elif 'allrounder' in role_lower or 'all rounder' in role_lower:
        # For allrounders, we'll default to pace unless specifically mentioned as spin
        if any(spin_type in role_lower for spin_type in ['spin', 'finger', 'wrist']):
            return "spin"
        else:
            return "pace"
    
    # Default to pace for any other bowler types
    return "pace"


def generate_bowling_movements(bowling_skill, role):
    """
    Generate bowling movements for a new player based on skill and role.

    Args:
        bowling_skill (int): Bowling skill from 0-100
        role (str): Player role to determine bowler type

    Returns:
        dict: Movement types with ratings and categories
    """
    
    bowler_type = determine_bowler_type(role)

    # Define possible movement types for each bowler type
    movement_types = {
        "spin": ["off_spin", "leg_spin", "indrift", "outdrift", "straighter"],
        "pace": ["inswing", "outswing", "off_cutter", "leg_cutter", "seam", "straight"]
    }

    # Define skill brackets and corresponding major_count
    skill_brackets = [
        {"min": 0, "max": 59, "major_count": 1},
        {"min": 60, "max": 69, "major_count": (1, 2)},
        {"min": 70, "max": 79, "major_count": (1, 2)},
        {"min": 80, "max": 89, "major_count": (1, 3)},
        {"min": 90, "max": 100, "major_count": (1, 4)}
    ]

    # Find the appropriate skill bracket
    bracket = None
    for b in skill_brackets:
        if b["min"] <= bowling_skill <= b["max"]:
            bracket = b
            break

    if not bracket:
        bracket = skill_brackets[0]  # Fallback to lowest bracket

    # Determine number of major movement types
    if isinstance(bracket["major_count"], tuple):
        major_count = random.randint(bracket["major_count"][0], bracket["major_count"][1])
    else:
        major_count = bracket["major_count"]

    # Get available movement types for this bowler type
    available_movements = movement_types[bowler_type]

    # Randomly select major movement types
    major_movements = random.sample(available_movements, min(major_count, len(available_movements)))

    # Create movements dictionary
    movements = {}

    for movement in available_movements:
        if movement in major_movements:
            # Major movements: 90% to 110% of bowling skill
            min_rating = int(bowling_skill * 0.9)
            max_rating = int(bowling_skill * 1.1)
            rating = max(1, min(100, random.randint(min_rating, max_rating)))
            category = "major"
        else:
            # Minor movements: 30% to 60% of bowling skill
            min_rating = int(bowling_skill * 0.3)
            max_rating = int(bowling_skill * 0.6)
            rating = max(1, min(100, random.randint(min_rating, max_rating)))
            category = "minor"
        movements[movement] = {
            "rating": rating,
            "category": category
        }

    return {
        "bowler_type": bowler_type,
        "movements": movements
    }


def update_bowling_movements(movements, old_skill, new_skill):
    """
    Update movement ratings based on skill change.
    
    Args:
        movements (dict): Current movement data
        old_skill (int): Previous bowling skill
        new_skill (int): New bowling skill
    
    Returns:
        dict: Updated movements with new ratings
    """
    if old_skill == new_skill:
        return movements
    
    skill_delta = new_skill - old_skill
    
    # Define multipliers for major vs minor movements
    major_multiplier = 1.2
    minor_multiplier = 0.6
    
    updated_movements = {}
    
    for movement_type, movement_data in movements.items():
        category = movement_data["category"]
        current_rating = movement_data["rating"]
        
        if category == "major":
            # Major movements change more with skill
            rating_change = int(skill_delta * major_multiplier)
        else:
            # Minor movements change less with skill
            rating_change = int(skill_delta * minor_multiplier)
        
        new_rating = max(1, min(100, current_rating + rating_change))
        
        updated_movements[movement_type] = {
            "rating": new_rating,
            "category": category
        }
    
    return updated_movements


def get_movement_display_name(movement_type):
    """Get display name for movement type"""
    display_names = {
        "inswing": "Inswing",
        "outswing": "Outswing", 
        "off_cutter": "Off Cutter",
        "leg_cutter": "Leg Cutter",
        "seam": "Seam",
        "straight": "Straight",
        "off_spin": "Off Spin",
        "leg_spin": "Leg Spin",
        "indrift": "In Drift",
        "outdrift": "Out Drift",
        "straighter": "Straighter"
    }
    return display_names.get(movement_type, movement_type.title())


def format_movement_rating(rating, category):
    """Format movement rating with star for major movements"""
    if category == "major":
        return f"{rating}★"
    else:
        return str(rating)
