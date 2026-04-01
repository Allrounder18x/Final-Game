"""
Game constants and configuration values
Phase 12: Comprehensive game configuration
"""

# Format configurations
FORMAT_CONFIG = {
    'T20': {
        'overs': 20,
        'max_overs_per_bowler': 4,
        'powerplay_overs': 6,
        'death_overs_start': 16,
        'innings': 2
    },
    'ODI': {
        'overs': 50,
        'max_overs_per_bowler': 10,
        'powerplay_overs': 10,
        'death_overs_start': 40,
        'innings': 2
    },
    'Test': {
        'overs': 450,  # Maximum per innings
        'max_overs_per_bowler': 999,  # No limit
        'powerplay_overs': 0,
        'death_overs_start': 999,
        'innings': 4
    }
}

# Tier system
TIER_CONFIG = {
    'tiers_per_format': 5,
    'teams_per_tier': {
        1: 16,  # Tier 1
        2: 15,  # Tier 2
        3: 15,  # Tier 3
        4: 15,  # Tier 4
        5: 15   # Tier 5
    },
    'promotion_slots': 2,
    'relegation_slots': 2,
    'points_for_win': 2,
    'points_for_tie': 1,
    'points_for_loss': 0
}

# Player generation
PLAYER_CONFIG = {
    'min_age': 18,
    'max_age': 35,
    'retirement_age': 38,
    'peak_age_start': 23,
    'peak_age_end': 28,
    'decline_age': 33,
    'min_skill': 20,
    'max_skill': 99,
    'squad_size': 15,
    'playing_xi_size': 11,
    'u21_squad_size': 15,
    'u21_max_age': 21
}

# Economy
ECONOMY_CONFIG = {
    'starting_credits': 10000,
    'season_base_credits': 1000,
    'win_bonus': 100,
    'tier_1_bonus': 2500,
    'tier_2_bonus': 2000,
    'tier_3_bonus': 1500,
    'tier_4_bonus': 1000,
    'tier_5_bonus': 500,
    'world_cup_winner_bonus': 5000,
    'world_cup_runner_up_bonus': 2500,
    'world_cup_semifinal_bonus': 1000,
    'loot_pack_bronze_cost': 500,
    'loot_pack_silver_cost': 1000,
    'loot_pack_gold_cost': 2000,
    'loot_pack_platinum_cost': 5000
}

# Training
TRAINING_CONFIG = {
    'points_per_season': 5,
    'base_success_rate': 0.6,
    'young_age_modifier': 1.2,
    'prime_age_modifier': 1.0,
    'veteran_age_modifier': 0.7,
    'old_age_modifier': 0.4,
    'low_skill_modifier': 0.8,
    'medium_skill_modifier': 0.6,
    'high_skill_modifier': 0.4,
    'elite_skill_modifier': 0.2,
    'min_improvement': 1,
    'max_improvement': 3
}

# World Cups
WORLD_CUP_CONFIG = {
    'frequency': 2,  # Every 2 years
    'group_size': 6,
    'knockout_teams': 4,
    'qualification_threshold': 2,  # Top 2 from each group
    'total_teams': 12
}

# Youth development
YOUTH_CONFIG = {
    'promotion_min_age': 18,
    'promotion_min_matches': 3,
    'batter_min_runs': 50,
    'batter_min_avg': 15,
    'bowler_min_wickets': 5,
    'bowler_max_avg': 35,
    'allrounder_min_runs': 30,
    'allrounder_min_avg': 12,
    'allrounder_min_wickets': 3,
    'allrounder_max_avg': 40,
    'development_rate': 0.7,
    'max_promotions_per_season': 2
}

# Trait system
TRAIT_CONFIG = {
    'max_traits_per_player': 5,
    'min_trait_level': 1,
    'max_trait_level': 3,
    'level_up_chance': 0.3,
    'level_down_chance': 0.2,
    'new_trait_chance': 0.15,
    'remove_trait_chance': 0.1,
    'good_performance_threshold': 3.0,
    'poor_performance_threshold': 1.5,
    'exceptional_performance_threshold': 4.0
}

# UI
UI_CONFIG = {
    'window_width': 1400,
    'window_height': 900,
    'default_font': ('Arial', 10),
    'header_font': ('Arial', 14, 'bold'),
    'title_font': ('Arial', 18, 'bold'),
    'treeview_height': 20,
    'max_rankings_display': 2000
}

# Simulation
SIMULATION_CONFIG = {
    'fast_mode': True,
    'show_ball_by_ball': False,
    'auto_save_frequency': 5,  # Save every 5 seasons
    'max_concurrent_matches': 10
}

# Statistics
STATS_CONFIG = {
    'min_matches_for_ranking': 5,
    'top_players_count': 100,
    'career_stats_retention': True,
    'season_stats_retention': True
}
