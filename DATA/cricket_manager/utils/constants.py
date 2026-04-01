"""
Game constants including player roles, colors, and game settings
"""

# Detailed Player Roles (from gamer 2024.py)
PLAYER_ROLES = {
    "Opening Batter": 15,
    "Middle Order Batter": 17,
    "Lower Order Batter": 12,
    "Keeper Batter": 10,
    "Batting Allrounder (Medium Pace)": 1,
    "Batting Allrounder (Wrist Spin)": 1,
    "Batting Allrounder (Finger Spin)": 1,
    "Batting Allrounder (Fast Medium)": 1,
    "Batting Allrounder (Fast)": 0,
    "Bowling Allrounder (Medium Pace)": 1.5,
    "Bowling Allrounder (Wrist Spin)": 1,
    "Bowling Allrounder (Finger Spin)": 1,
    "Bowling Allrounder (Fast Medium)": 1,
    "Bowling Allrounder (Fast)": 0.5,
    "Genuine Allrounder (Medium Pace)": 0.25,
    "Genuine Allrounder (Wrist Spin)": 0.50,
    "Genuine Allrounder (Finger Spin)": 0.50,
    "Genuine Allrounder (Fast Medium)": 0.50,
    "Genuine Allrounder (Fast)": 0.25,
    "Finger Spinner": 9,
    "Wrist Spinner": 7,
    "Medium Pacer": 10,
    "Fast Medium Pacer": 7,
    "Fast Bowler": 2
}

# Role categories for easier filtering
BATTING_ROLES = [
    "Opening Batter",
    "Middle Order Batter",
    "Lower Order Batter",
    "Keeper Batter"
]

ALLROUNDER_ROLES = [
    "Batting Allrounder (Medium Pace)",
    "Batting Allrounder (Wrist Spin)",
    "Batting Allrounder (Finger Spin)",
    "Batting Allrounder (Fast Medium)",
    "Batting Allrounder (Fast)",
    "Bowling Allrounder (Medium Pace)",
    "Bowling Allrounder (Wrist Spin)",
    "Bowling Allrounder (Finger Spin)",
    "Bowling Allrounder (Fast Medium)",
    "Bowling Allrounder (Fast)",
    "Genuine Allrounder (Medium Pace)",
    "Genuine Allrounder (Wrist Spin)",
    "Genuine Allrounder (Finger Spin)",
    "Genuine Allrounder (Fast Medium)",
    "Genuine Allrounder (Fast)"
]

BOWLING_ROLES = [
    "Finger Spinner",
    "Wrist Spinner",
    "Medium Pacer",
    "Fast Medium Pacer",
    "Fast Bowler"
]

# Pace bowler roles
PACE_BOWLING_ROLES = [
    "Medium Pacer",
    "Fast Medium Pacer",
    "Fast Bowler"
]

# Spin bowler roles
SPIN_BOWLING_ROLES = [
    "Finger Spinner",
    "Wrist Spinner"
]

# Color scheme
COLORS = {
    'primary': '#2E7D32',      # Green
    'secondary': '#1976D2',    # Blue
    'success': '#4CAF50',      # Light Green
    'warning': '#FF9800',      # Orange
    'danger': '#F44336',       # Red
    'background': '#FFFFFF',   # White
    'text': '#212121'          # Dark Gray
}

# Match formats
MATCH_FORMATS = ['T20', 'ODI', 'Test']

# Format-specific settings
FORMAT_SETTINGS = {
    'T20': {
        'max_overs': 20,
        'powerplay_overs': 6,
        'max_bowler_overs': 4,
        'innings_count': 2
    },
    'ODI': {
        'max_overs': 50,
        'powerplay_overs': 10,
        'max_bowler_overs': 10,
        'innings_count': 2
    },
    'Test': {
        'max_overs': None,  # Unlimited
        'powerplay_overs': 0,
        'max_bowler_overs': None,  # Unlimited
        'innings_count': 4,
        'max_overs_per_day': 90,
        'follow_on_threshold': 200
    }
}

# Tier system
TIER_SIZES = {
    1: 12,  # Elite
    2: 12,  # Professional
    3: 12,  # Competitive
    4: 12,  # Developing
    5: 28   # Grassroots (U21)
}

TIER_NAMES = {
    1: 'Elite',
    2: 'Professional',
    3: 'Competitive',
    4: 'Developing',
    5: 'Grassroots'
}

# Promotion/Relegation
PROMOTION_SLOTS = 2
RELEGATION_SLOTS = 2

# Loot pack system
LOOT_PACK_COST = 80

# Credit rewards
CREDIT_REWARDS = {
    'match_win': 100,
    'match_loss': 25,
    'tournament_win': 500,
    'promotion': 300,
    'century': 50,
    'five_wickets': 50,
    'hat_trick': 100,
    'world_cup_win': 1000,
    'world_cup_runner_up': 500
}

# Skill ranges
MIN_SKILL = 1
MAX_SKILL = 100

# Age ranges
MIN_AGE = 16
MAX_AGE = 45
RETIREMENT_AGE = 40

# Squad sizes
MIN_SQUAD_SIZE = 15
MAX_SQUAD_SIZE = 25
PLAYING_XI_SIZE = 11
BOWLING_SQUAD_SIZE = 7

# Youth system
U21_AGE_LIMIT = 21
U21_SQUAD_SIZE = 15
