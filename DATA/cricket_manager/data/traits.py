"""
Player Traits System - RPG-style traits that affect match performance
Traits provide variety and make each player unique beyond just skill numbers
"""

# Positive Batting Traits
POSITIVE_BATTING_TRAITS = {
    'POWER_HITTER': {
        'name': 'Power Hitter',
        'description': 'Increased boundary scoring',
        'effects': {
            'six_bonus': 0.10,      # +10% chance for sixes
            'four_bonus': 0.05,     # +5% chance for fours
            'dot_penalty': -0.05    # -5% dot balls
        }
    },
    'ACCUMULATOR': {
        'name': 'Accumulator',
        'description': 'Consistent run scoring',
        'effects': {
            'single_bonus': 0.15,   # +15% singles
            'two_bonus': 0.10,      # +10% twos
            'six_penalty': -0.10    # -10% sixes (plays safe)
        }
    },
    'ANCHOR': {
        'name': 'Anchor',
        'description': 'Defensive batting, hard to dismiss',
        'effects': {
            'dot_bonus': 0.10,           # +10% dot balls
            'wicket_resistance': 0.20    # -20% wicket chance
        }
    },
    'FINISHER': {
        'name': 'Finisher',
        'description': 'Better in death overs (16-20)',
        'effects': {
            'death_overs_bonus': 0.25,   # +25% scoring in death
            'pressure_bonus': 0.15       # +15% under pressure
        }
    },
    'BIG_MATCH_PLAYER': {
        'name': 'Big Match Player',
        'description': 'Performs in important matches',
        'effects': {
            'world_cup_bonus': 0.30,     # +30% in World Cups
            'final_bonus': 0.40          # +40% in finals
        }
    },
    'AGGRESSIVE': {
        'name': 'Aggressive',
        'description': 'High risk, high reward',
        'effects': {
            'boundary_bonus': 0.15,      # +15% boundaries
            'wicket_penalty': 0.10       # +10% wicket chance
        }
    },
    'TECHNICALLY_SOUND': {
        'name': 'Technically Sound',
        'description': 'Solid technique',
        'effects': {
            'wicket_resistance': 0.15,   # -15% wicket chance
            'consistency_bonus': 0.10    # More consistent scores
        }
    },
    'SPIN_BASHER': {
        'name': 'Spin Basher',
        'description': 'Dominates spin bowling',
        'effects': {
            'vs_spin_bonus': 0.25,       # +25% vs spin
            'boundary_vs_spin': 0.15     # +15% boundaries vs spin
        }
    },
    'DEMOLISHER_OF_PACE': {
        'name': 'Demolisher of Pace',
        'description': 'Excels against pace bowling',
        'effects': {
            'vs_pace_bonus': 0.25,       # +25% vs pace
            'boundary_vs_pace': 0.15     # +15% boundaries vs pace
        }
    },
    'POWER_OPENER': {
        'name': 'Power Opener',
        'description': 'Aggressive in powerplay',
        'effects': {
            'powerplay_bonus': 0.30,     # +30% in powerplay
            'boundary_powerplay': 0.20   # +20% boundaries in powerplay
        }
    },
    'CONSOLIDATOR': {
        'name': 'Consolidator',
        'description': 'Rebuilds after wickets',
        'effects': {
            'after_wicket_bonus': 0.20,  # +20% after wicket falls
            'partnership_bonus': 0.15    # +15% in partnerships
        }
    },
    'GREAT_TECHNIQUE': {
        'name': 'Great Technique',
        'description': 'Excellent batting technique',
        'effects': {
            'wicket_resistance': 0.20,   # -20% wicket chance
            'vs_swing_bonus': 0.15       # +15% vs swing
        }
    },
    'PRESENCE_OF_MIND': {
        'name': 'Presence of Mind',
        'description': 'Smart decision making',
        'effects': {
            'run_out_resistance': 0.30,  # -30% run out chance
            'pressure_bonus': 0.15       # +15% under pressure
        }
    },
    'PITCH_READER': {
        'name': 'Pitch Reader',
        'description': 'Adapts to pitch conditions',
        'effects': {
            'difficult_pitch_bonus': 0.25,  # +25% on difficult pitches
            'consistency_bonus': 0.15       # +15% consistency
        }
    },
    'MR_WALL': {
        'name': 'Mr. Wall',
        'description': 'Extremely hard to dismiss',
        'effects': {
            'wicket_resistance': 0.30,   # -30% wicket chance
            'dot_bonus': 0.15            # +15% dot balls
        }
    }
}

# Negative Batting Traits
NEGATIVE_BATTING_TRAITS = {
    'INCONSISTENT': {
        'name': 'Inconsistent',
        'description': 'Variable performance',
        'effects': {
            'skill_variance': 0.30       # ±30% skill variation
        }
    },
    'NERVOUS_STARTER': {
        'name': 'Nervous Starter',
        'description': 'Struggles in first 10 balls',
        'effects': {
            'first_10_balls_penalty': -0.20  # -20% performance
        }
    },
    'PRESSURE_PRONE': {
        'name': 'Pressure Prone',
        'description': 'Struggles under pressure',
        'effects': {
            'high_pressure_penalty': -0.25   # -25% when chasing
        }
    },
    'SOFT_DISMISSAL': {
        'name': 'Soft Dismissal',
        'description': 'Gets out to poor shots',
        'effects': {
            'wicket_penalty': 0.15           # +15% wicket chance
        }
    },
    'NO_TECHNIQUE_BASHER': {
        'name': 'No Technique Basher',
        'description': 'All power, no technique',
        'effects': {
            'boundary_bonus': 0.20,          # +20% boundaries
            'wicket_penalty': 0.25           # +25% wicket chance
        }
    },
    'WEAK_AGAINST_SPIN': {
        'name': 'Weak Against Spin',
        'description': 'Struggles vs spin',
        'effects': {
            'vs_spin_penalty': -0.25         # -25% vs spin
        }
    },
    'WEAK_AGAINST_PACE': {
        'name': 'Weak Against Pace',
        'description': 'Struggles vs pace',
        'effects': {
            'vs_pace_penalty': -0.25         # -25% vs pace
        }
    },
    # --- T20 Batting Negative Traits ---
    'T20_POWERPLAY_WASTER': {
        'name': 'Powerplay Waster',
        'description': 'Cannot capitalise on fielding restrictions in overs 1-6',
        'effects': {'powerplay_penalty': -0.25, 'dot_penalty': 0.20}
    },
    'T20_CANT_HIT_SIXES': {
        'name': "Can't Clear the Rope",
        'description': 'Lacks power to clear the boundary, mistimes lofted shots',
        'effects': {'six_penalty': -0.30, 'four_penalty': -0.10}
    },
    'T20_DEATH_OVERS_CHOKER': {
        'name': 'Death Overs Choker',
        'description': 'Freezes in overs 16-20, cannot find boundaries',
        'effects': {'death_batting_penalty': -0.25, 'wicket_penalty': 0.15}
    },
    'T20_DOT_BALL_MAGNET': {
        'name': 'Dot Ball Magnet',
        'description': 'Plays too many dot balls, kills momentum',
        'effects': {'dot_penalty': 0.25, 'strike_rate_penalty': -0.20}
    },
    'T20_RASH_SHOT_MERCHANT': {
        'name': 'Rash Shot Merchant',
        'description': 'Plays high-risk shots from ball one, throws wicket away',
        'effects': {'wicket_penalty': 0.25, 'boundary_bonus': 0.05}
    },
    # --- ODI Batting Negative Traits ---
    'ODI_MIDDLE_OVERS_STALLER': {
        'name': 'Middle Overs Staller',
        'description': 'Cannot rotate strike in overs 11-40, bogged down vs spin',
        'effects': {'middle_overs_penalty': -0.20, 'dot_penalty': 0.15}
    },
    'ODI_SLOG_MISFIRE': {
        'name': 'Slog Misfire',
        'description': 'Mistimes big shots in overs 40-50, gets out trying to accelerate',
        'effects': {'death_batting_penalty': -0.20, 'wicket_penalty': 0.15}
    },
    'ODI_POOR_STRIKE_ROTATION': {
        'name': 'Poor Strike Rotation',
        'description': 'Cannot find gaps for singles and doubles',
        'effects': {'single_penalty': -0.20, 'dot_penalty': 0.15}
    },
    'ODI_COLLAPSER': {
        'name': 'Collapser',
        'description': 'Gets out in clusters during batting collapses',
        'effects': {'wicket_penalty': 0.20, 'pressure_penalty': -0.20}
    },
    'ODI_CHASE_BOTTLER': {
        'name': 'Chase Bottler',
        'description': 'Underperforms when chasing, cannot handle required rate',
        'effects': {'chase_penalty': -0.25, 'wicket_penalty': 0.15}
    },
    # --- Test Batting Negative Traits ---
    'TEST_NEW_BALL_BUNNY': {
        'name': 'New Ball Bunny',
        'description': 'Cannot survive the new ball, edges in first 20 overs',
        'effects': {'new_ball_penalty': -0.30, 'wicket_penalty': 0.25}
    },
    'TEST_POOR_CONCENTRATION': {
        'name': 'Poor Concentration',
        'description': 'Loses focus, throws wicket away between 30-70 runs',
        'effects': {'concentration_penalty': -0.20, 'wicket_penalty': 0.15}
    },
    'TEST_DAY5_CRUMBLER': {
        'name': 'Day 5 Crumbler',
        'description': 'Cannot bat on deteriorating pitches on days 4-5',
        'effects': {'day45_penalty': -0.25, 'spin_penalty': -0.20}
    },
    'TEST_SECOND_INNINGS_FLOP': {
        'name': 'Second Innings Flop',
        'description': 'Consistently fails in the second innings',
        'effects': {'second_innings_penalty': -0.25, 'wicket_penalty': 0.15}
    },
    'TEST_BOUNCER_VICTIM': {
        'name': 'Bouncer Victim',
        'description': 'Flinches at short-pitched deliveries, easy bouncer target',
        'effects': {'short_ball_penalty': -0.30, 'wicket_penalty': 0.20}
    }
}

# Positive Bowling Traits
POSITIVE_BOWLING_TRAITS = {
    'SWING_BOWLER': {
        'name': 'Swing Bowler',
        'description': 'Ball swings in air',
        'effects': {
            'wicket_bonus': 0.15,        # +15% wicket chance
            'powerplay_bonus': 0.20      # +20% in powerplay
        }
    },
    'YORKER_SPECIALIST': {
        'name': 'Yorker Specialist',
        'description': 'Excellent yorkers',
        'effects': {
            'death_overs_bonus': 0.25,   # +25% in death overs
            'economy_bonus': 0.15        # -15% runs conceded
        }
    },
    'DEATH_BOWLER': {
        'name': 'Death Bowler',
        'description': 'Excels in overs 17-20',
        'effects': {
            'overs_17_20_bonus': 0.30,   # +30% in death
            'pressure_bonus': 0.20       # +20% under pressure
        }
    },
    'ECONOMICAL': {
        'name': 'Economical',
        'description': 'Concedes fewer runs',
        'effects': {
            'runs_conceded_reduction': 0.20  # -20% runs
        }
    },
    'WICKET_TAKER': {
        'name': 'Wicket Taker',
        'description': 'Takes more wickets',
        'effects': {
            'wicket_chance_bonus': 0.25      # +25% wickets
        }
    },
    'REVERSE_SWING': {
        'name': 'Reverse Swing',
        'description': 'Ball reverses after 30 overs',
        'effects': {
            'old_ball_bonus': 0.30,          # +30% with old ball
            'odi_test_bonus': 0.20           # Better in longer formats
        }
    },
    'SPIN_WIZARD': {
        'name': 'Spin Wizard',
        'description': 'Exceptional spin bowling',
        'effects': {
            'spin_bonus': 0.25,              # +25% on spin-friendly pitches
            'middle_overs_bonus': 0.20       # +20% in middle overs
        }
    },
    'NEW_BALL_LOVER': {
        'name': 'New Ball Lover',
        'description': 'Excels with new ball',
        'effects': {
            'new_ball_bonus': 0.30,          # +30% with new ball
            'powerplay_bonus': 0.25          # +25% in powerplay
        }
    },
    'GOLDEN_ARM': {
        'name': 'Golden Arm',
        'description': 'Takes wickets at crucial times',
        'effects': {
            'wicket_bonus': 0.20,            # +20% wicket chance
            'partnership_breaker': 0.25      # +25% vs set batsmen
        }
    },
    'PACE_DEMON': {
        'name': 'Pace Demon',
        'description': 'Express pace intimidates batsmen',
        'effects': {
            'speed_bonus': 5,                # +5 km/h speed
            'wicket_bonus': 0.15             # +15% wicket chance
        }
    },
    'GREEN_TRACK_BULLY': {
        'name': 'Green Track Bully',
        'description': 'Dominates on green pitches',
        'effects': {
            'green_pitch_bonus': 0.35,       # +35% on green pitches
            'seam_bonus': 0.20               # +20% seam movement
        }
    },
    'PITCH_OUT_OF_EQUATION': {
        'name': 'Pitch Out of Equation',
        'description': 'Performs on any pitch',
        'effects': {
            'all_pitch_bonus': 0.15,         # +15% on all pitches
            'consistency_bonus': 0.20        # +20% consistency
        }
    },
    'REVERSE_SWING_EXPERT': {
        'name': 'Reverse Swing Expert',
        'description': 'Masters reverse swing',
        'effects': {
            'old_ball_bonus': 0.35,          # +35% with old ball
            'wicket_bonus': 0.20             # +20% wicket chance
        }
    },
    'MISER': {
        'name': 'Miser',
        'description': 'Extremely economical',
        'effects': {
            'economy_bonus': 0.25,           # -25% runs conceded
            'dot_ball_bonus': 0.20           # +20% dot balls
        }
    },
    'BIG_TURN': {
        'name': 'Big Turn',
        'description': 'Massive spin on ball',
        'effects': {
            'spin_bonus': 0.30,              # +30% spin
            'wicket_bonus': 0.20             # +20% wicket chance
        }
    },
    'DUSTY_MAN': {
        'name': 'Dusty Man',
        'description': 'Excels on dusty pitches',
        'effects': {
            'dusty_pitch_bonus': 0.35,       # +35% on dusty pitches
            'spin_bonus': 0.25               # +25% spin
        }
    },
    'ALPHA_WOLF': {
        'name': 'Alpha Wolf',
        'description': 'Leader of bowling attack',
        'effects': {
            'wicket_bonus': 0.20,            # +20% wicket chance
            'pressure_bonus': 0.25           # +25% under pressure
        }
    }
}

# Negative Bowling Traits
NEGATIVE_BOWLING_TRAITS = {
    'EXPENSIVE': {
        'name': 'Expensive',
        'description': 'Concedes more runs',
        'effects': {
            'runs_conceded_increase': 0.25   # +25% runs
        }
    },
    'NO_BALL_PRONE': {
        'name': 'No-Ball Prone',
        'description': 'Bowls no-balls',
        'effects': {
            'no_ball_chance': 0.05           # 5% no-ball chance
        }
    },
    'WAYWARD': {
        'name': 'Wayward',
        'description': 'Inconsistent line and length',
        'effects': {
            'boundary_penalty': 0.15,        # +15% boundaries
            'wicket_penalty': -0.10          # -10% wickets
        }
    },
    'PRESSURE_BOWLER': {
        'name': 'Pressure Bowler',
        'description': 'Struggles under pressure',
        'effects': {
            'death_overs_penalty': -0.20,    # -20% in death
            'final_overs_penalty': -0.25     # -25% in final overs
        }
    },
    'FLAT_TRACK_BULLY': {
        'name': 'Flat Track Bully',
        'description': 'Only performs on flat pitches',
        'effects': {
            'difficult_pitch_penalty': -0.30  # -30% on difficult pitches
        }
    },
    # --- T20 Bowling Negative Traits ---
    'T20_DEATH_BOWLING_LIABILITY': {
        'name': 'Death Bowling Liability',
        'description': 'Cannot execute yorkers in overs 16-20, gets smashed at death',
        'effects': {'death_overs_penalty': -0.30, 'boundary_conceded': 0.25}
    },
    'T20_POWERPLAY_LEAKER': {
        'name': 'Powerplay Leaker',
        'description': 'Gives easy boundaries with new ball in fielding restrictions',
        'effects': {'powerplay_penalty': -0.25, 'boundary_conceded': 0.20}
    },
    'T20_NO_SLOWER_BALL': {
        'name': 'No Slower Ball',
        'description': 'No change of pace, batters time shots easily',
        'effects': {'runs_conceded_increase': 0.20, 'wicket_penalty': -0.15}
    },
    'T20_WIDE_MACHINE': {
        'name': 'Wide Machine',
        'description': 'Bowls too many wides, gives away free runs',
        'effects': {'wide_chance': 0.10, 'boundary_penalty': 0.15}
    },
    'T20_PRESSURE_CRUMBLER': {
        'name': 'Pressure Crumbler',
        'description': 'Loses composure after being hit for six',
        'effects': {'after_boundary_penalty': -0.30, 'runs_conceded_increase': 0.20}
    },
    # --- ODI Bowling Negative Traits ---
    'ODI_MIDDLE_OVERS_EXPENSIVE': {
        'name': 'Middle Overs Expensive',
        'description': 'Cannot contain in overs 11-40, leaks boundaries',
        'effects': {'middle_overs_penalty': -0.20, 'boundary_conceded': 0.15}
    },
    'ODI_NO_WICKET_TAKER': {
        'name': 'No Wicket Taker',
        'description': 'Bowls tidy but never threatens stumps',
        'effects': {'wicket_penalty': -0.20, 'economy_bonus': 0.05}
    },
    'ODI_DEATH_OVERS_LEAKER': {
        'name': 'Death Overs Leaker',
        'description': 'Concedes heavily in overs 40-50 under slog pressure',
        'effects': {'death_overs_penalty': -0.25, 'boundary_conceded': 0.20}
    },
    'ODI_FIRST_SPELL_ONLY': {
        'name': 'First Spell Only',
        'description': 'Falls apart in second and third spells',
        'effects': {'later_spell_penalty': -0.20, 'runs_conceded_increase': 0.15}
    },
    'ODI_PARTNERSHIP_FEEDER': {
        'name': 'Partnership Feeder',
        'description': 'Bowls to strengths of set batters, feeds partnerships',
        'effects': {'vs_set_batter_penalty': -0.20, 'wicket_penalty': -0.15}
    },
    # --- Test Bowling Negative Traits ---
    'TEST_NO_STAMINA': {
        'name': 'No Stamina',
        'description': 'Pace and accuracy drop after 5 overs in a spell',
        'effects': {'long_spell_penalty': -0.25, 'accuracy_penalty': -0.20}
    },
    'TEST_FLAT_PITCH_PASSENGER': {
        'name': 'Flat Pitch Passenger',
        'description': 'Ineffective on flat wickets, needs pitch assistance',
        'effects': {'flat_pitch_penalty': -0.30, 'wicket_penalty': -0.20}
    },
    'TEST_REVERSE_SWING_HOPELESS': {
        'name': 'Reverse Swing Hopeless',
        'description': 'Cannot reverse old ball, toothless after 30+ overs',
        'effects': {'old_ball_penalty': -0.25, 'wicket_penalty': -0.15}
    },
    'TEST_DAY5_TOOTHLESS': {
        'name': 'Day 5 Toothless',
        'description': 'Cannot exploit deteriorating pitches on days 4-5',
        'effects': {'day45_penalty': -0.25, 'wicket_penalty': -0.20}
    },
    'TEST_SPELL_BREAKER': {
        'name': 'Spell Breaker',
        'description': 'Loses effectiveness between spells, cannot maintain pressure',
        'effects': {'between_spell_penalty': -0.20, 'accuracy_penalty': -0.15}
    }
}

# Positive Fielding Traits
POSITIVE_FIELDING_TRAITS = {
    'SAFE_HANDS': {
        'name': 'Safe Hands',
        'description': 'Rarely drops catches',
        'effects': {
            'catch_success_bonus': 0.30      # +30% catch success
        }
    },
    'ATHLETIC': {
        'name': 'Athletic',
        'description': 'Saves boundaries',
        'effects': {
            'boundary_save_chance': 0.25,    # 25% chance to save 4
            'run_out_bonus': 0.20            # +20% run-out chance
        }
    },
    'LIGHTNING_REFLEXES': {
        'name': 'Lightning Reflexes',
        'description': 'Quick reactions',
        'effects': {
            'catch_bonus': 0.25,             # +25% catches
            'stumping_bonus': 0.30           # +30% stumpings (keepers)
        }
    },
    'HAIRY_MONSTER': {
        'name': 'Hairy Monster',
        'description': 'Exceptional fielder',
        'effects': {
            'catch_bonus': 0.30,             # +30% catches
            'run_out_bonus': 0.25,           # +25% run-outs
            'boundary_save_chance': 0.20     # 20% boundary saves
        }
    }
}

# Negative Fielding Traits
NEGATIVE_FIELDING_TRAITS = {
    'BUTTER_FINGERS': {
        'name': 'Butter Fingers',
        'description': 'Drops catches',
        'effects': {
            'catch_success_penalty': -0.30   # -30% catch success
        }
    },
    'SLOW': {
        'name': 'Slow',
        'description': 'Slow in the field',
        'effects': {
            'boundary_save_penalty': -0.20,  # -20% boundary saves
            'run_out_penalty': -0.15         # -15% run-outs
        }
    }
}

# Mental Traits
MENTAL_TRAITS = {
    'CAPTAIN_MATERIAL': {
        'name': 'Captain Material',
        'description': 'Natural leader',
        'effects': {
            'team_morale_bonus': 5,          # +5 team morale
            'pressure_bonus': 0.15           # +15% under pressure
        }
    },
    'ICE_COOL': {
        'name': 'Ice Cool',
        'description': 'Calm under pressure',
        'effects': {
            'pressure_bonus': 0.25,          # +25% under pressure
            'final_bonus': 0.20              # +20% in finals
        }
    },
    'MATCH_WINNER': {
        'name': 'Match Winner',
        'description': 'Wins close matches',
        'effects': {
            'close_match_bonus': 0.30,       # +30% in close matches
            'pressure_bonus': 0.20           # +20% under pressure
        }
    },
    'CHOKER': {
        'name': 'Choker',
        'description': 'Fails under pressure',
        'effects': {
            'pressure_penalty': -0.30,       # -30% under pressure
            'final_penalty': -0.25           # -25% in finals
        }
    }
}

# Combine all traits
ALL_TRAITS = {
    **POSITIVE_BATTING_TRAITS,
    **NEGATIVE_BATTING_TRAITS,
    **POSITIVE_BOWLING_TRAITS,
    **NEGATIVE_BOWLING_TRAITS,
    **POSITIVE_FIELDING_TRAITS,
    **NEGATIVE_FIELDING_TRAITS,
    **MENTAL_TRAITS
}

# Trait categories for easy filtering
TRAIT_CATEGORIES = {
    'batting_positive': list(POSITIVE_BATTING_TRAITS.keys()),
    'batting_negative': list(NEGATIVE_BATTING_TRAITS.keys()),
    'bowling_positive': list(POSITIVE_BOWLING_TRAITS.keys()),
    'bowling_negative': list(NEGATIVE_BOWLING_TRAITS.keys()),
    'fielding_positive': list(POSITIVE_FIELDING_TRAITS.keys()),
    'fielding_negative': list(NEGATIVE_FIELDING_TRAITS.keys()),
    'mental': list(MENTAL_TRAITS.keys())
}


def get_trait_info(trait_key):
    """Get trait information by key"""
    return ALL_TRAITS.get(trait_key, None)


def get_trait_effect(trait_key, effect_name):
    """Get specific effect value from a trait"""
    trait = get_trait_info(trait_key)
    if trait and 'effects' in trait:
        return trait['effects'].get(effect_name, 0)
    return 0


def is_positive_trait(trait_key):
    """Check if trait is positive"""
    return (trait_key in POSITIVE_BATTING_TRAITS or 
            trait_key in POSITIVE_BOWLING_TRAITS or 
            trait_key in POSITIVE_FIELDING_TRAITS or
            trait_key in ['CAPTAIN_MATERIAL', 'ICE_COOL', 'MATCH_WINNER'])


def is_negative_trait(trait_key):
    """Check if trait is negative"""
    return (trait_key in NEGATIVE_BATTING_TRAITS or 
            trait_key in NEGATIVE_BOWLING_TRAITS or 
            trait_key in NEGATIVE_FIELDING_TRAITS or
            trait_key == 'CHOKER')


def get_traits_by_category(category):
    """Get all traits in a category"""
    return TRAIT_CATEGORIES.get(category, [])
