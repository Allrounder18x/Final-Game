"""
Trait Assignment System - Assigns traits to players based on skills and roles
Uses ONLY traits from player_traits.py (the authoritative trait source)
"""

import random
import sys
import os

# Import from player_traits.py (in DATA/ folder)
_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '')
if _data_dir not in sys.path:
    sys.path.insert(0, _data_dir)

from player_traits import POSITIVE_TRAITS, NEGATIVE_TRAITS

from cricket_manager.utils.helpers import is_batter, is_bowler, is_allrounder, is_keeper, is_pace_bowler, is_spin_bowler

# Build lookup dicts by type for trait pool selection
_BATTING_POSITIVE = {k: v for k, v in POSITIVE_TRAITS.items() if v.get('type') in ('batting', 'both')}
_BOWLING_POSITIVE = {k: v for k, v in POSITIVE_TRAITS.items() if v.get('type') in ('bowling', 'both')}
_BATTING_NEGATIVE = {k: v for k, v in NEGATIVE_TRAITS.items() if v.get('type') in ('batting', 'both')}
_BOWLING_NEGATIVE = {k: v for k, v in NEGATIVE_TRAITS.items() if v.get('type') in ('bowling', 'both')}

# Pace-only bowling traits (should NOT be assigned to spinners)
_PACE_ONLY_TRAITS = {
    'NEW_BALL_LOVER', 'DEATH_BOWLER', 'PACE_DEMON', 'GREEN_TRACK_BULLY',
    'REVERSE_SWING_EXPERT', 'REVERSE_SWING',
}

# Spin-only bowling traits (should NOT be assigned to pacers)
_SPIN_ONLY_TRAITS = {
    'BIG_TURN', 'DUSTY_MAN', 'SPIN_WIZARD',
}

# Combined lookup for display
ALL_PLAYER_TRAITS = {**POSITIVE_TRAITS, **NEGATIVE_TRAITS}


def assign_traits_to_player(player, tier=3):
    """
    Assign traits to a player based on their skills, role, and tier
    
    Args:
        player: Player object
        tier: Player tier (1-5, where 1 is best)
    
    Returns:
        List of trait dictionaries with name and strength
    """
    
    traits = []
    
    # Tier-based trait distribution
    # Tier 1: More positive traits, fewer negative
    # Tier 5: Fewer positive traits, more negative
    tier_modifiers = {
        1: {'positive_bonus': 2, 'negative_penalty': -2},
        2: {'positive_bonus': 1, 'negative_penalty': -1},
        3: {'positive_bonus': 0, 'negative_penalty': 0},
        4: {'positive_bonus': -1, 'negative_penalty': 1},
        5: {'positive_bonus': -2, 'negative_penalty': 2}
    }
    
    modifier = tier_modifiers.get(tier, tier_modifiers[3])
    
    # Determine number of traits based on skill level and tier
    avg_skill = (player.batting + player.bowling + player.fielding) / 3
    
    if avg_skill >= 85:
        num_positive = random.randint(3 + modifier['positive_bonus'], 4 + modifier['positive_bonus'])
        num_negative = random.randint(0 + modifier['negative_penalty'], 1 + modifier['negative_penalty'])
    elif avg_skill >= 70:
        num_positive = random.randint(2 + modifier['positive_bonus'], 3 + modifier['positive_bonus'])
        num_negative = random.randint(0 + modifier['negative_penalty'], 2 + modifier['negative_penalty'])
    elif avg_skill >= 50:
        num_positive = random.randint(1 + modifier['positive_bonus'], 2 + modifier['positive_bonus'])
        num_negative = random.randint(1 + modifier['negative_penalty'], 2 + modifier['negative_penalty'])
    else:
        num_positive = random.randint(0 + modifier['positive_bonus'], 1 + modifier['positive_bonus'])
        num_negative = random.randint(2 + modifier['negative_penalty'], 3 + modifier['negative_penalty'])
    
    # Ensure minimum/maximum limits
    num_positive = max(0, min(5, num_positive))
    num_negative = max(0, min(4, num_negative))
    
    # Assign positive traits
    positive_pool = get_trait_pool_for_player(player, positive=True, tier=tier)
    for _ in range(num_positive):
        if positive_pool:
            trait_key = random.choice(positive_pool)
            strength = get_trait_strength(player, trait_key, tier)
            traits.append({'name': trait_key, 'strength': strength})
            positive_pool.remove(trait_key)  # Don't assign same trait twice
    
    # Assign negative traits
    negative_pool = get_trait_pool_for_player(player, positive=False, tier=tier)
    for _ in range(num_negative):
        if negative_pool:
            trait_key = random.choice(negative_pool)
            strength = get_trait_strength(player, trait_key, tier)
            traits.append({'name': trait_key, 'strength': strength})
            negative_pool.remove(trait_key)
    
    # Store traits in player
    player.traits = traits
    
    return traits


def get_trait_pool_for_player(player, positive=True, tier=3):
    """
    Get appropriate trait pool for player based on role and tier.
    Uses ONLY traits from player_traits.py.
    
    Args:
        player: Player object
        positive: True for positive traits, False for negative
        tier: Player tier (1-5, where 1 is best)
    
    Returns:
        List of trait keys
    """
    
    pool = []
    
    # Determine if this player's bowling type is pace or spin
    role = player.role
    player_is_pacer = is_pace_bowler(role)
    player_is_spinner = is_spin_bowler(role)
    
    if positive:
        # Batting traits for batters/allrounders/keepers
        if is_batter(role) or is_allrounder(role) or is_keeper(role):
            pool.extend(list(_BATTING_POSITIVE.keys()))
        
        # Bowling traits for bowlers/allrounders
        if is_bowler(role) or is_allrounder(role):
            bowling_pool = list(_BOWLING_POSITIVE.keys())
            # Filter out incompatible bowling traits
            if player_is_pacer:
                bowling_pool = [t for t in bowling_pool if t not in _SPIN_ONLY_TRAITS]
            elif player_is_spinner:
                bowling_pool = [t for t in bowling_pool if t not in _PACE_ONLY_TRAITS]
            pool.extend(bowling_pool)
        
        # If pool is empty (edge case), give all positive traits
        if not pool:
            pool.extend(list(POSITIVE_TRAITS.keys()))
    else:
        # Negative batting traits
        if is_batter(role) or is_allrounder(role) or is_keeper(role):
            pool.extend(list(_BATTING_NEGATIVE.keys()))
        
        # Negative bowling traits
        if is_bowler(role) or is_allrounder(role):
            bowling_pool = list(_BOWLING_NEGATIVE.keys())
            # Filter out incompatible bowling traits
            if player_is_pacer:
                bowling_pool = [t for t in bowling_pool if t not in _SPIN_ONLY_TRAITS]
            elif player_is_spinner:
                bowling_pool = [t for t in bowling_pool if t not in _PACE_ONLY_TRAITS]
            pool.extend(bowling_pool)
        
        # If pool is empty, give all negative traits
        if not pool:
            pool.extend(list(NEGATIVE_TRAITS.keys()))
    
    # Remove duplicates
    pool = list(set(pool))
    
    return pool


def get_trait_strength(player, trait_key, tier=3):
    """
    Determine trait strength (1-3) based on player skill and tier
    
    Args:
        player: Player object
        trait_key: Trait key
        tier: Player tier (1-5, where 1 is best)
    
    Returns:
        Strength level (1-3)
    """
    
    # Determine relevant skill based on trait type from player_traits.py
    trait_info = ALL_PLAYER_TRAITS.get(trait_key, {})
    trait_type = trait_info.get('type', 'both')
    
    if trait_type == 'batting':
        skill = player.batting
    elif trait_type == 'bowling':
        skill = player.bowling
    else:  # 'both' or unknown
        skill = max(player.batting, player.bowling)
    
    # Tier-based strength bonus
    tier_bonus = {
        1: 1,  # Tier 1 gets +1 strength
        2: 0,  # Tier 2 gets normal
        3: 0,  # Tier 3 gets normal
        4: 0,  # Tier 4 gets normal
        5: -1  # Tier 5 gets -1 strength
    }
    
    bonus = tier_bonus.get(tier, 0)
    
    # Determine strength based on skill and tier
    if skill >= 85:
        base_strength = random.randint(2, 3)
    elif skill >= 70:
        base_strength = random.randint(1, 2)
    else:
        base_strength = 1
    
    # Apply tier bonus
    final_strength = max(1, min(3, base_strength + bonus))
    
    return final_strength


def get_player_trait_effects(player):
    """
    Get combined trait effects for a player (using player_traits.py)
    
    Args:
        player: Player object
    
    Returns:
        Dictionary with combined effects
    """
    
    combined_effects = {
        'batting': {},
        'bowling': {},
        'both': {}
    }
    
    if not hasattr(player, 'traits') or not player.traits:
        return combined_effects
    
    for trait_dict in player.traits:
        trait_key = trait_dict['name']
        strength = trait_dict.get('strength', 1)
        
        # Get trait info from player_traits.py
        trait_info = ALL_PLAYER_TRAITS.get(trait_key, {})
        if not trait_info:
            continue
        
        # Determine category from type field
        category = trait_info.get('type', 'both')
        if category not in combined_effects:
            category = 'both'
        
        # Store trait key and strength for downstream use
        if 'traits' not in combined_effects[category]:
            combined_effects[category]['traits'] = []
        combined_effects[category]['traits'].append({'name': trait_key, 'strength': strength})
    
    return combined_effects


def apply_trait_to_probabilities(player, base_probs, situation=None):
    """
    Apply player traits to base probabilities
    
    Args:
        player: Player object
        base_probs: Dictionary of base probabilities
        situation: Optional situation context (powerplay, death_overs, etc.)
    
    Returns:
        Modified probabilities dictionary
    """
    
    if not hasattr(player, 'traits') or not player.traits:
        return base_probs
    
    modified_probs = base_probs.copy()
    trait_effects = get_player_trait_effects(player)
    batting_effects = trait_effects['batting']
    
    # Apply batting effects
    if 'dot_bonus' in batting_effects:
        modified_probs['dot'] = modified_probs.get('dot', 0) + batting_effects['dot_bonus']
    
    if 'single_bonus' in batting_effects:
        modified_probs['single'] = modified_probs.get('single', 0) + batting_effects['single_bonus']
    
    if 'two_bonus' in batting_effects:
        modified_probs['two'] = modified_probs.get('two', 0) + batting_effects['two_bonus']
    
    if 'four_bonus' in batting_effects:
        modified_probs['four'] = modified_probs.get('four', 0) + batting_effects['four_bonus']
    
    if 'six_bonus' in batting_effects:
        modified_probs['six'] = modified_probs.get('six', 0) + batting_effects['six_bonus']
    
    if 'boundary_bonus' in batting_effects:
        bonus = batting_effects['boundary_bonus']
        modified_probs['four'] = modified_probs.get('four', 0) + bonus / 2
        modified_probs['six'] = modified_probs.get('six', 0) + bonus / 2
    
    # Apply situation-specific bonuses
    if situation:
        if situation == 'powerplay' and 'powerplay_bonus' in batting_effects:
            bonus = batting_effects['powerplay_bonus']
            for key in modified_probs:
                if key != 'dot':
                    modified_probs[key] *= (1 + bonus)
        
        elif situation == 'death_overs' and 'death_overs_bonus' in batting_effects:
            bonus = batting_effects['death_overs_bonus']
            for key in modified_probs:
                if key != 'dot':
                    modified_probs[key] *= (1 + bonus)
    
    # Normalize probabilities to sum to 1.0
    total = sum(modified_probs.values())
    if total > 0:
        for key in modified_probs:
            modified_probs[key] /= total
    
    return modified_probs


def calculate_wicket_chance_with_traits(batsman, bowler, base_wicket_chance, situation=None):
    """
    Calculate wicket chance with trait effects
    
    Args:
        batsman: Batsman player object
        bowler: Bowler player object
        base_wicket_chance: Base wicket probability
        situation: Optional situation context
    
    Returns:
        Modified wicket chance
    """
    
    wicket_chance = base_wicket_chance
    
    # Batsman traits
    if hasattr(batsman, 'traits') and batsman.traits:
        batsman_effects = get_player_trait_effects(batsman)
        batting_effects = batsman_effects['batting']
        
        if 'wicket_resistance' in batting_effects:
            wicket_chance *= (1 - batting_effects['wicket_resistance'])
        
        if 'wicket_penalty' in batting_effects:
            wicket_chance *= (1 + batting_effects['wicket_penalty'])
    
    # Bowler traits
    if hasattr(bowler, 'traits') and bowler.traits:
        bowler_effects = get_player_trait_effects(bowler)
        bowling_effects = bowler_effects['bowling']
        
        if 'wicket_bonus' in bowling_effects:
            wicket_chance *= (1 + bowling_effects['wicket_bonus'])
        
        if 'wicket_chance_bonus' in bowling_effects:
            wicket_chance *= (1 + bowling_effects['wicket_chance_bonus'])
        
        # Situation-specific bonuses
        if situation:
            if situation == 'powerplay' and 'powerplay_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['powerplay_bonus'])
            
            elif situation == 'death_overs' and 'death_overs_bonus' in bowling_effects:
                wicket_chance *= (1 + bowling_effects['death_overs_bonus'])
    
    # Clamp between reasonable bounds
    wicket_chance = max(0.01, min(0.30, wicket_chance))
    
    return wicket_chance


def get_trait_display_name(trait_key):
    """Get display name for a trait (from player_traits.py)"""
    trait_info = ALL_PLAYER_TRAITS.get(trait_key, {})
    if trait_info:
        return trait_info.get('name', trait_key.replace('_', ' ').title())
    return trait_key.replace('_', ' ').title()


def get_trait_description(trait_key):
    """Get description for a trait (from player_traits.py)"""
    trait_info = ALL_PLAYER_TRAITS.get(trait_key, {})
    if trait_info:
        return trait_info.get('description', '')
    return ""


def is_positive_trait(trait_key):
    """Check if trait is positive (from player_traits.py)"""
    return trait_key in POSITIVE_TRAITS


def is_negative_trait(trait_key):
    """Check if trait is negative (from player_traits.py)"""
    return trait_key in NEGATIVE_TRAITS


def format_player_traits(player):
    """
    Format player traits for display
    
    Args:
        player: Player object
    
    Returns:
        Formatted string of traits
    """
    
    if not hasattr(player, 'traits') or not player.traits:
        return "No traits"
    
    trait_strings = []
    for trait_dict in player.traits:
        trait_key = trait_dict['name']
        strength = trait_dict.get('strength', 1)
        display_name = get_trait_display_name(trait_key)
        
        # Add strength indicator
        strength_indicator = "★" * strength
        trait_strings.append(f"{display_name} {strength_indicator}")
    
    return " | ".join(trait_strings)


def upgrade_trait(player, trait_key):
    """
    Upgrade a trait's strength (max 3)
    
    Args:
        player: Player object
        trait_key: Trait key to upgrade
    
    Returns:
        True if upgraded, False if already max or not found
    """
    
    if not hasattr(player, 'traits') or not player.traits:
        return False
    
    for trait_dict in player.traits:
        if trait_dict['name'] == trait_key:
            if trait_dict.get('strength', 1) < 3:
                trait_dict['strength'] = trait_dict.get('strength', 1) + 1
                return True
            return False
    
    return False


def add_new_trait(player, trait_key, strength=None):
    """
    Add a new trait to player
    
    Args:
        player: Player object
        trait_key: Trait key to add
        strength: Optional strength (1-3), auto-determined if None
    
    Returns:
        True if added, False if already exists
    """
    
    if not hasattr(player, 'traits'):
        player.traits = []
    
    # Check if trait already exists
    for trait_dict in player.traits:
        if trait_dict['name'] == trait_key:
            return False
    
    # Determine strength if not provided
    if strength is None:
        strength = get_trait_strength(player, trait_key)
    
    # Add trait
    player.traits.append({'name': trait_key, 'strength': strength})
    return True


def remove_trait(player, trait_key):
    """
    Remove a trait from player
    
    Args:
        player: Player object
        trait_key: Trait key to remove
    
    Returns:
        True if removed, False if not found
    """
    
    if not hasattr(player, 'traits') or not player.traits:
        return False
    
    for i, trait_dict in enumerate(player.traits):
        if trait_dict['name'] == trait_key:
            player.traits.pop(i)
            return True
    
    return False


def assign_random_trait(player):
    """
    Assign a single random role-appropriate trait to a player.
    Will not assign a trait the player already has.
    
    Args:
        player: Player object
    
    Returns:
        Trait dictionary with name and strength, or None if no trait assigned
    """
    # Get appropriate trait pool (role-filtered from player_traits.py)
    positive_pool = get_trait_pool_for_player(player, positive=True)
    
    if not positive_pool:
        return None
    
    # Exclude traits the player already has
    existing_keys = set()
    if hasattr(player, 'traits') and player.traits:
        existing_keys = {t['name'] for t in player.traits if isinstance(t, dict)}
    
    available = [k for k in positive_pool if k not in existing_keys]
    if not available:
        return None
    
    # Select random trait
    trait_key = random.choice(available)
    strength = get_trait_strength(player, trait_key)
    
    # Add to player's traits
    new_trait = {'name': trait_key, 'strength': strength}
    if not hasattr(player, 'traits') or player.traits is None:
        player.traits = []
    player.traits.append(new_trait)
    
    return new_trait
