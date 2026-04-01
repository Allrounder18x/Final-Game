"""
Configuration package for Cricket Manager
Phase 12: Constants and color schemes
"""

from cricket_manager.config.constants import (
    FORMAT_CONFIG,
    TIER_CONFIG,
    PLAYER_CONFIG,
    ECONOMY_CONFIG,
    TRAINING_CONFIG,
    WORLD_CUP_CONFIG,
    YOUTH_CONFIG,
    TRAIT_CONFIG,
    UI_CONFIG,
    SIMULATION_CONFIG,
    STATS_CONFIG
)

from cricket_manager.config.colors import (
    COLORS,
    get_tier_color,
    get_trait_level_color,
    get_format_color,
    get_change_type_color,
    get_status_color,
    hex_to_rgb,
    rgb_to_hex,
    lighten_color,
    darken_color
)

__all__ = [
    # Constants
    'FORMAT_CONFIG',
    'TIER_CONFIG',
    'PLAYER_CONFIG',
    'ECONOMY_CONFIG',
    'TRAINING_CONFIG',
    'WORLD_CUP_CONFIG',
    'YOUTH_CONFIG',
    'TRAIT_CONFIG',
    'UI_CONFIG',
    'SIMULATION_CONFIG',
    'STATS_CONFIG',
    
    # Colors
    'COLORS',
    'get_tier_color',
    'get_trait_level_color',
    'get_format_color',
    'get_change_type_color',
    'get_status_color',
    'hex_to_rgb',
    'rgb_to_hex',
    'lighten_color',
    'darken_color',
]
