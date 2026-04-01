import random

"""Player traits and their effects on ODI match simulation"""

POSITIVE_TRAITS = {
    'POWER_OPENER': {
        'name': 'Power Opener',
        'description': 'Increases scoring rate in first 10 overs against new ball',
        'type': 'batting',
        'phase': 'powerplay'
    },
    'CONSOLIDATOR': {
        'name': 'Consolidator',
        'description': 'Plays defensively after wickets fall, effective in middle overs (11-40)',
        'type': 'batting',
        'phase': 'middle'
    },
    'SPIN_BASHER': {
        'name': 'Spin Basher',
        'description': 'High strike rate against spin bowling in middle overs',
        'type': 'batting',
        'phase': 'all'
    },
    'DEMOLISHER_OF_PACE': {
        'name': 'Demolisher of Pace',
        'description': 'High strike rate against pace after powerplay, especially in death overs',
        'type': 'batting',
        'phase': 'middle_death'
    },
    'FINISHER': {
        'name': 'Finisher',
        'description': 'Higher chance of remaining not out and finishing games in last 10 overs',
        'type': 'batting',
        'phase': 'death'
    },
    'MR_WALL': {
        'name': 'Mr.Wall',
        'description': 'Consistent scorer across matches, ideal for ODI format',
        'type': 'batting',
        'phase': 'all'
    },
    'CHEEKY_BAT': {
        'name': 'Cheeky Bat',
        'description': 'Reduces dot balls, increases singles/doubles - crucial in middle overs',
        'type': 'batting',
        'phase': 'all'
    },
    'MENTOR': {
        'name': 'Mentor',
        'description': 'Boosts skills of entire playing XI throughout 50 overs',
        'type': 'both',
        'phase': 'all'
    },
    'NEW_BALL_LOVER': {
        'name': 'New Ball Lover',
        'description': 'Bowling boost in first 10 overs with new ball',
        'type': 'bowling',
        'phase': 'powerplay'
    },
    'MISER': {
        'name': 'Miser',
        'description': 'Economical spells in middle overs (11-40), hard to score boundaries',
        'type': 'bowling',
        'phase': 'all'
    },
    'GOLDEN_ARM': {
        'name': 'Golden Arm',
        'description': 'More likely to break big partnerships in middle overs',
        'type': 'bowling',
        'phase': 'all'
    },
    'DEATH_BOWLER': {
        'name': 'Death Bowler',
        'description': 'Effective in last 10 overs of ODI innings',
        'type': 'bowling',
        'phase': 'death'
    },
    'BIG_TURN': {
        'name': 'Big Turn',
        'description': 'Effective spin bowling between overs 15-35',
        'type': 'bowling',
        'phase': 'middle'
    },
    'ALPHA_WOLF': {
        'name': 'Alpha Wolf',
        'description': 'Boosts next bowler\'s skills',
        'type': 'bowling',
        'phase': 'all'
    },
    'PACE_DEMON': {
        'name': 'Pace Demon',
        'description': 'One super-fast over, reduces batter skills',
        'type': 'bowling',
        'phase': 'all'
    },
    'INTIMIDATOR': {
        'name': 'Intimidator',
        'description': 'Reduces skills of opposing players',
        'type': 'both',
        'phase': 'all'
    },
    'GREAT_TECHNIQUE': {
        'name': 'Great Technique',
        'description': 'Batting bonus against pace bowling on pace-friendly pitches',
        'type': 'batting',
        'phase': 'all'
    },
    'PRESENCE_OF_MIND': {
        'name': 'Presence of Mind',
        'description': 'Batting bonus against spin bowling on spin-friendly pitches',
        'type': 'batting',
        'phase': 'all'
    },
    'NO_TECHNIQUE_BASHER': {
        'name': 'No Technique Basher',
        'description': 'Batting boost on batting wickets but struggles on bowling pitches',
        'type': 'batting',
        'phase': 'all'
    },
    'HAIRY_MONSTER': {
        'name': 'Hairy Monster',
        'description': 'Significant batting boost on bowling-friendly wickets',
        'type': 'batting',
        'phase': 'all'
    },
    'PITCH_READER': {
        'name': 'Pitch Reader',
        'description': 'Adapts batting style based on pitch conditions for better performance',
        'type': 'batting',
        'phase': 'all'
    },
    'GREEN_TRACK_BULLY': {
        'name': 'Green Track Bully',
        'description': 'Bowling boost on pace-friendly wickets',
        'type': 'bowling',
        'phase': 'all'
    },
    'DUSTY_MAN': {
        'name': 'Dusty Man',
        'description': 'Spin bowling boost on spin-friendly pitches',
        'type': 'bowling',
        'phase': 'all'
    },
    'PITCH_OUT_OF_EQUATION': {
        'name': 'Pitch Out of Equation',
        'description': 'Significant bowling boost on batting-friendly wickets',
        'type': 'bowling',
        'phase': 'all'
    },
    'REVERSE_SWING_EXPERT': {
        'name': 'Reverse Swing Expert',
        'description': 'Increased effectiveness with old ball on abrasive pitches',
        'type': 'bowling',
        'phase': 'middle_death'
    },
    'PITCH_SPECIALISTS': {
        'name': 'Pitch Specialists',
        'description': 'Team has increased performance on specific pitch types',
        'type': 'both',
        'phase': 'all'
    },
    'COMEBACK_KINGS': {
        'name': 'Comeback Kings',
        'description': 'Team performs better when behind or under pressure',
        'type': 'both',
        'phase': 'all'
    },
    'GOOD_AGAINST_MOVEMENT': {
        'name': 'Good Against Movement',
        'description': 'Up to 15% batting skill boost vs pacers/fast bowlers on >7 pace assistance pitch',
        'type': 'batting',
        'phase': 'all'
    },
    'GOOD_AGAINST_EXTREME_PACE': {
        'name': 'Good Against Extreme Pace',
        'description': 'Up to 15% batting skill boost vs 140k+ pace bowlers',
        'type': 'batting',
        'phase': 'all'
    },
    'GOOD_AGAINST_SPIN': {
        'name': 'Good Against Spin',
        'description': 'Up to 15% batting skill boost vs spin bowlers on >7 spin assistance pitch',
        'type': 'batting',
        'phase': 'all'
    },
    'GOOD_AGAINST_BOUNCE': {
        'name': 'Good Against Bounce',
        'description': 'Up to 15% batting skill boost on >7 bounce pitch',
        'type': 'batting',
        'phase': 'all'
    },
}

NEGATIVE_TRAITS = {
    'NERVOUS_BATTER': {
        'name': 'Nervous Batter',
        'description': 'Likely to get out early but scores well if survives first 10 overs',
        'type': 'batting',
        'phase': 'start'
    },
    'CONCENTRATION_LOSER': {
        'name': 'Concentration Loser',
        'description': 'Likely to get out after scoring 50 in ODIs',
        'type': 'batting',
        'phase': 'all'
    },
    'NERVOUS_BOWLER': {
        'name': 'Nervous Bowler',
        'description': 'Performance drops after expensive over, critical in middle overs',
        'type': 'bowling',
        'phase': 'all'
    },
    'REBEL': {
        'name': 'Rebel',
        'description': 'Skills vary by ±15% each match (reduced variance for ODIs)',
        'type': 'both',
        'phase': 'all'
    },
    'FLAT_TRACK_BULLY': {
        'name': 'Flat Track Bully',
        'description': 'Batting skills drop significantly on bowling-friendly pitches, exposed in longer format',
        'type': 'batting',
        'phase': 'all'
    },
    'PITCH_DEPENDENT': {
        'name': 'Pitch Dependent',
        'description': 'Bowling effectiveness drops on unfavorable pitch conditions, more impactful in 50 overs',
        'type': 'bowling',
        'phase': 'all'
    },
    'PRESSURE_COOKER': {
        'name': 'Pressure Cooker',
        'description': 'Skills decrease in high-pressure situations like close matches or when chasing big totals',
        'type': 'both',
        'phase': 'all'
    },
    'STAMINA_ISSUES': {
        'name': 'Stamina Issues',
        'description': 'Performance deteriorates after bowling 5 overs or batting for 20 overs',
        'type': 'both',
        'phase': 'all'
    },
    'BAD_AGAINST_BOUNCE': {
        'name': 'Bad Against Bounce',
        'description': 'Up to 15% batting skill reduction on >7 bounce pitch',
        'type': 'batting',
        'phase': 'all'
    },
    'BAD_AGAINST_SPIN': {
        'name': 'Bad Against Spin',
        'description': 'Up to 15% batting skill reduction vs spin bowlers on >7 spin pitch',
        'type': 'batting',
        'phase': 'all'
    },
    'BAD_AGAINST_MOVEMENT': {
        'name': 'Bad Against Movement',
        'description': 'Up to 15% batting skill reduction on >7 pace assistance pitch',
        'type': 'batting',
        'phase': 'all'
    },
    'BAD_AGAINST_EXTREME_PACE': {
        'name': 'Bad Against Extreme Pace',
        'description': 'Up to 20% batting skill reduction vs 140k+ pace bowlers',
        'type': 'batting',
        'phase': 'all'
    },
    # ============================================================
    # T20-SPECIFIC NEGATIVE TRAITS (10)
    # ============================================================
    # T20 Batting (5)
    'T20_POWERPLAY_WASTER': {
        'name': 'Powerplay Waster',
        'description': 'Cannot capitalise on fielding restrictions in overs 1-6, plays too defensively when field is up',
        'type': 'batting', 'phase': 'powerplay', 'format': 'T20'
    },
    'T20_CANT_HIT_SIXES': {
        'name': "Can't Clear the Rope",
        'description': 'Lacks the power or timing to clear the boundary, mistimes lofted shots regularly',
        'type': 'batting', 'phase': 'all', 'format': 'T20'
    },
    'T20_DEATH_OVERS_CHOKER': {
        'name': 'Death Overs Choker',
        'description': 'Freezes in overs 16-20, cannot find boundaries when the team needs acceleration',
        'type': 'batting', 'phase': 'death', 'format': 'T20'
    },
    'T20_DOT_BALL_MAGNET': {
        'name': 'Dot Ball Magnet',
        'description': 'Plays too many dot balls, builds pressure on partner and self, kills momentum',
        'type': 'batting', 'phase': 'all', 'format': 'T20'
    },
    'T20_RASH_SHOT_MERCHANT': {
        'name': 'Rash Shot Merchant',
        'description': 'Plays high-risk shots from ball one, often throws wicket away trying to hit every ball',
        'type': 'batting', 'phase': 'all', 'format': 'T20'
    },
    # T20 Bowling (5)
    'T20_DEATH_BOWLING_LIABILITY': {
        'name': 'Death Bowling Liability',
        'description': 'Cannot execute yorkers or slower balls in overs 16-20, gets smashed at the death',
        'type': 'bowling', 'phase': 'death', 'format': 'T20'
    },
    'T20_POWERPLAY_LEAKER': {
        'name': 'Powerplay Leaker',
        'description': 'Bowls too full or too short with the new ball, gives easy boundaries in fielding restrictions',
        'type': 'bowling', 'phase': 'powerplay', 'format': 'T20'
    },
    'T20_NO_SLOWER_BALL': {
        'name': 'No Slower Ball',
        'description': 'Has no change of pace, batters pick up the same speed every ball and time their shots',
        'type': 'bowling', 'phase': 'all', 'format': 'T20'
    },
    'T20_WIDE_MACHINE': {
        'name': 'Wide Machine',
        'description': 'Bowls too many wides trying to bowl wide yorkers, gives away free runs consistently',
        'type': 'bowling', 'phase': 'all', 'format': 'T20'
    },
    'T20_PRESSURE_CRUMBLER': {
        'name': 'Pressure Crumbler',
        'description': 'After being hit for a six, loses composure and bowls loose deliveries for the rest of the over',
        'type': 'bowling', 'phase': 'all', 'format': 'T20'
    },
    # ============================================================
    # ODI-SPECIFIC NEGATIVE TRAITS (10)
    # ============================================================
    # ODI Batting (5)
    'ODI_MIDDLE_OVERS_STALLER': {
        'name': 'Middle Overs Staller',
        'description': 'Cannot rotate strike in overs 11-40, gets bogged down against spin in the middle phase',
        'type': 'batting', 'phase': 'middle', 'format': 'ODI'
    },
    'ODI_SLOG_MISFIRE': {
        'name': 'Slog Misfire',
        'description': 'Mistimes big shots in overs 40-50, gets out trying to accelerate instead of building',
        'type': 'batting', 'phase': 'death', 'format': 'ODI'
    },
    'ODI_POOR_STRIKE_ROTATION': {
        'name': 'Poor Strike Rotation',
        'description': 'Cannot find gaps for singles and doubles, puts pressure on batting partner',
        'type': 'batting', 'phase': 'all', 'format': 'ODI'
    },
    'ODI_COLLAPSER': {
        'name': 'Collapser',
        'description': 'Gets out in clusters during batting collapses, cannot steady the ship when wickets fall',
        'type': 'batting', 'phase': 'all', 'format': 'ODI'
    },
    'ODI_CHASE_BOTTLER': {
        'name': 'Chase Bottler',
        'description': 'Underperforms significantly when chasing, cannot handle required rate pressure',
        'type': 'batting', 'phase': 'all', 'format': 'ODI'
    },
    # ODI Bowling (5)
    'ODI_MIDDLE_OVERS_EXPENSIVE': {
        'name': 'Middle Overs Expensive',
        'description': 'Cannot contain in overs 11-40, gives away easy boundaries when field is spread',
        'type': 'bowling', 'phase': 'middle', 'format': 'ODI'
    },
    'ODI_NO_WICKET_TAKER': {
        'name': 'No Wicket Taker',
        'description': 'Bowls tidy but never threatens the stumps, cannot break partnerships',
        'type': 'bowling', 'phase': 'all', 'format': 'ODI'
    },
    'ODI_DEATH_OVERS_LEAKER': {
        'name': 'Death Overs Leaker',
        'description': 'Concedes heavily in overs 40-50, poor at bowling under slog pressure',
        'type': 'bowling', 'phase': 'death', 'format': 'ODI'
    },
    'ODI_FIRST_SPELL_ONLY': {
        'name': 'First Spell Only',
        'description': 'Effective in first spell but falls apart in second and third spells, loses accuracy',
        'type': 'bowling', 'phase': 'all', 'format': 'ODI'
    },
    'ODI_PARTNERSHIP_FEEDER': {
        'name': 'Partnership Feeder',
        'description': 'Bowls to the strengths of set batters, feeds partnerships instead of breaking them',
        'type': 'bowling', 'phase': 'all', 'format': 'ODI'
    },
    # ============================================================
    # TEST-SPECIFIC NEGATIVE TRAITS (10)
    # ============================================================
    # Test Batting (5)
    'TEST_NEW_BALL_BUNNY': {
        'name': 'New Ball Bunny',
        'description': 'Cannot survive the new ball, edges or plays across the line in the first 20 overs',
        'type': 'batting', 'phase': 'start', 'format': 'Test'
    },
    'TEST_POOR_CONCENTRATION': {
        'name': 'Poor Concentration',
        'description': 'Loses focus after batting for long periods, throws wicket away between 30-70 runs',
        'type': 'batting', 'phase': 'all', 'format': 'Test'
    },
    'TEST_DAY5_CRUMBLER': {
        'name': 'Day 5 Crumbler',
        'description': 'Cannot bat on deteriorating pitches, struggles against turn and variable bounce on days 4-5',
        'type': 'batting', 'phase': 'all', 'format': 'Test'
    },
    'TEST_SECOND_INNINGS_FLOP': {
        'name': 'Second Innings Flop',
        'description': 'Consistently fails in the second innings, cannot handle pressure of chasing or setting targets',
        'type': 'batting', 'phase': 'all', 'format': 'Test'
    },
    'TEST_BOUNCER_VICTIM': {
        'name': 'Bouncer Victim',
        'description': 'Flinches and misplays short-pitched deliveries, easy target for sustained bouncer attack',
        'type': 'batting', 'phase': 'all', 'format': 'Test'
    },
    # Test Bowling (5)
    'TEST_NO_STAMINA': {
        'name': 'No Stamina',
        'description': 'Cannot bowl long spells, pace and accuracy drop sharply after 5 overs in a spell',
        'type': 'bowling', 'phase': 'all', 'format': 'Test'
    },
    'TEST_FLAT_PITCH_PASSENGER': {
        'name': 'Flat Pitch Passenger',
        'description': 'Completely ineffective on flat batting wickets, cannot create chances without pitch assistance',
        'type': 'bowling', 'phase': 'all', 'format': 'Test'
    },
    'TEST_REVERSE_SWING_HOPELESS': {
        'name': 'Reverse Swing Hopeless',
        'description': 'Cannot reverse the old ball, becomes toothless after ball loses its shine (30+ overs)',
        'type': 'bowling', 'phase': 'all', 'format': 'Test'
    },
    'TEST_DAY5_TOOTHLESS': {
        'name': 'Day 5 Toothless',
        'description': 'Cannot exploit deteriorating pitches on days 4-5, misses the rough and bowls too short',
        'type': 'bowling', 'phase': 'all', 'format': 'Test'
    },
    'TEST_SPELL_BREAKER': {
        'name': 'Spell Breaker',
        'description': 'Loses effectiveness between spells, cannot maintain pressure when brought back for second spell',
        'type': 'bowling', 'phase': 'all', 'format': 'Test'
    },
}

def get_trait_effect(trait_name, strength_level):
    """Calculate the effect multiplier based on trait strength (1-5) for ODI format"""
    base_effects = {
        'POWER_OPENER': lambda x: 1 + (x * 0.08),  # Up to 40% boost (reduced from T20)
        'CONSOLIDATOR': lambda x: 1 + (x * 0.12),  # Up to 60% defensive boost
        'SPIN_BASHER': lambda x: 1 + (x * 0.1),  # Up to 50% boost vs spin
        'DEMOLISHER_OF_PACE': lambda x: 1 + (x * 0.1),  # Up to 50% boost vs pace
        'FINISHER': lambda x: 1 + (x * 0.12),  # Up to 60% boost in death overs
        'MR_WALL': lambda x: 1 + (x * 0.1),  # Up to 50% consistency boost (increased for ODI)
        'CHEEKY_BAT': lambda x: 1 + (x * 0.12),  # Up to 60% reduction in dots (increased for ODI)
        'MENTOR': lambda x: 1 + (x * 0.05),  # Up to 25% team boost (increased for longer format)
        'NEW_BALL_LOVER': lambda x: 1 + (x * 0.1),  # Up to 50% new ball boost
        'MISER': lambda x: 1 + (x * 0.12),  # Up to 60% economy boost (increased for ODI)
        'GOLDEN_ARM': lambda x: 1 + (x * 0.12),  # Up to 60% partnership breaker
        'DEATH_BOWLER': lambda x: 1 + (x * 0.1),  # Up to 50% death over boost
        'BIG_TURN': lambda x: 1 + (x * 0.14),  # Up to 70% spin boost (increased for ODI middle overs)
        'ALPHA_WOLF': lambda x: 1 + (x * 0.1),  # Up to 50% next bowler boost (increased for ODI)
        'PACE_DEMON': lambda x: 1 + (x * 0.16),  # Up to 80% pace boost for one over (reduced for ODI)
        'INTIMIDATOR': lambda x: 1 + (x * 0.08),  # Up to 40% opponent debuff (increased for longer format)
        
        # Batting traits adjusted for ODI
        'GREAT_TECHNIQUE': lambda x: 1 + (x * 0.16),  # Up to 80% boost vs pace on pace-friendly pitches
        'PRESENCE_OF_MIND': lambda x: 1 + (x * 0.16),  # Up to 80% boost vs spin on spin-friendly pitches
        'NO_TECHNIQUE_BASHER': lambda x: 1 + (x * 0.14),  # Up to 70% boost on batting wickets
        'HAIRY_MONSTER': lambda x: 1 + (x * 0.16),  # Up to 80% batting boost on bowling-friendly wickets
        'PITCH_READER': lambda x: 1 + (x * 0.12),  # Up to 60% boost based on pitch adaptation
        
        # Bowling traits adjusted for ODI
        'GREEN_TRACK_BULLY': lambda x: 1 + (x * 0.14),  # Up to 70% bowling boost on pace-friendly wickets
        'DUSTY_MAN': lambda x: 1 + (x * 0.14),  # Up to 70% spin bowling boost on spin-friendly pitches
        'PITCH_OUT_OF_EQUATION': lambda x: 1 + (x * 0.16),  # Up to 80% bowling boost on batting-friendly wickets
        'REVERSE_SWING_EXPERT': lambda x: 1 + (x * 0.16),  # Up to 80% boost with old ball (increased for ODI)
        
        # Team traits adjusted for ODI
        'PITCH_SPECIALISTS': lambda x: 1 + (x * 0.12),  # Up to 60% boost on specific pitch types
        'COMEBACK_KINGS': lambda x: 1 + (x * 0.14),  # Up to 70% boost when behind (increased for longer format)
        
        # New traits
        'GOOD_AGAINST_MOVEMENT': lambda x: 1 + (x * 0.15),
        'GOOD_AGAINST_EXTREME_PACE': lambda x: 1 + (x * 0.15),
        'GOOD_AGAINST_SPIN': lambda x: 1 + (x * 0.15),
        'GOOD_AGAINST_BOUNCE': lambda x: 1 + (x * 0.15),
        'BAD_AGAINST_BOUNCE': lambda x: 1 - (x * 0.15),
        'BAD_AGAINST_SPIN': lambda x: 1 - (x * 0.15),
        'BAD_AGAINST_MOVEMENT': lambda x: 1 - (x * 0.15),
        'BAD_AGAINST_EXTREME_PACE': lambda x: 1 - (x * 0.20),
        # T20-specific negative traits
        'T20_POWERPLAY_WASTER': lambda x: 1 - (x * 0.14),
        'T20_CANT_HIT_SIXES': lambda x: 1 - (x * 0.16),
        'T20_DEATH_OVERS_CHOKER': lambda x: 1 - (x * 0.14),
        'T20_DOT_BALL_MAGNET': lambda x: 1 - (x * 0.12),
        'T20_RASH_SHOT_MERCHANT': lambda x: 1 - (x * 0.14),
        'T20_DEATH_BOWLING_LIABILITY': lambda x: 1 - (x * 0.18),
        'T20_POWERPLAY_LEAKER': lambda x: 1 - (x * 0.14),
        'T20_NO_SLOWER_BALL': lambda x: 1 - (x * 0.14),
        'T20_WIDE_MACHINE': lambda x: 1 - (x * 0.12),
        'T20_PRESSURE_CRUMBLER': lambda x: 1 - (x * 0.16),
        # ODI-specific negative traits
        'ODI_MIDDLE_OVERS_STALLER': lambda x: 1 - (x * 0.12),
        'ODI_SLOG_MISFIRE': lambda x: 1 - (x * 0.12),
        'ODI_POOR_STRIKE_ROTATION': lambda x: 1 - (x * 0.10),
        'ODI_COLLAPSER': lambda x: 1 - (x * 0.12),
        'ODI_CHASE_BOTTLER': lambda x: 1 - (x * 0.12),
        'ODI_MIDDLE_OVERS_EXPENSIVE': lambda x: 1 - (x * 0.12),
        'ODI_NO_WICKET_TAKER': lambda x: 1 - (x * 0.10),
        'ODI_DEATH_OVERS_LEAKER': lambda x: 1 - (x * 0.14),
        'ODI_FIRST_SPELL_ONLY': lambda x: 1 - (x * 0.10),
        'ODI_PARTNERSHIP_FEEDER': lambda x: 1 - (x * 0.10),
        # Test-specific negative traits
        'TEST_NEW_BALL_BUNNY': lambda x: 1 - (x * 0.16),
        'TEST_POOR_CONCENTRATION': lambda x: 1 - (x * 0.12),
        'TEST_DAY5_CRUMBLER': lambda x: 1 - (x * 0.14),
        'TEST_SECOND_INNINGS_FLOP': lambda x: 1 - (x * 0.12),
        'TEST_BOUNCER_VICTIM': lambda x: 1 - (x * 0.16),
        'TEST_NO_STAMINA': lambda x: 1 - (x * 0.14),
        'TEST_FLAT_PITCH_PASSENGER': lambda x: 1 - (x * 0.14),
        'TEST_REVERSE_SWING_HOPELESS': lambda x: 1 - (x * 0.12),
        'TEST_DAY5_TOOTHLESS': lambda x: 1 - (x * 0.14),
        'TEST_SPELL_BREAKER': lambda x: 1 - (x * 0.10),
    }
    
    if trait_name in base_effects:
        return base_effects[trait_name](strength_level/5.0)
    return 1.0  # No effect if trait not found

def get_negative_trait_effect(trait_name, strength_level, match_format='ODI'):
    """Calculate the negative effect multiplier for format-specific youth negative traits.
    
    30 unique traits: 10 T20-specific, 10 ODI-specific, 10 Test-specific.
    Each trait only activates in its own format's simulation.
    strength_level: 1-5 star rating.
    Returns multiplier < 1.0 (worse = lower).
    """
    # Legacy negative traits (format-independent)
    legacy_effects = {
        'NERVOUS_BATTER': lambda x: 1 - (x * 0.12),
        'CONCENTRATION_LOSER': lambda x: 1 - (x * 0.1),
        'NERVOUS_BOWLER': lambda x: 1 - (x * 0.1),
        'REBEL': lambda x: 1 - (x * 0.03 * random.choice([-1, 1])),
        'FLAT_TRACK_BULLY': lambda x: 1 - (x * 0.14),
        'PITCH_DEPENDENT': lambda x: 1 - (x * 0.12),
        'PRESSURE_COOKER': lambda x: 1 - (x * 0.1),
        'STAMINA_ISSUES': lambda x: 1 - (x * 0.08),
    }
    if trait_name in legacy_effects:
        return legacy_effects[trait_name](strength_level)
    
    # T20-specific traits (only active in T20 matches)
    t20_effects = {
        'T20_POWERPLAY_WASTER': lambda x: 1 - (x * 0.14),       # Defensive in PP = wasted overs
        'T20_CANT_HIT_SIXES': lambda x: 1 - (x * 0.16),         # No clearing ability
        'T20_DEATH_OVERS_CHOKER': lambda x: 1 - (x * 0.14),     # Freezes overs 16-20
        'T20_DOT_BALL_MAGNET': lambda x: 1 - (x * 0.12),        # Kills momentum
        'T20_RASH_SHOT_MERCHANT': lambda x: 1 - (x * 0.14),     # Throws wicket away
        'T20_DEATH_BOWLING_LIABILITY': lambda x: 1 - (x * 0.18), # Gets smashed at death
        'T20_POWERPLAY_LEAKER': lambda x: 1 - (x * 0.14),       # Leaks in PP
        'T20_NO_SLOWER_BALL': lambda x: 1 - (x * 0.14),         # No change of pace
        'T20_WIDE_MACHINE': lambda x: 1 - (x * 0.12),           # Free runs from wides
        'T20_PRESSURE_CRUMBLER': lambda x: 1 - (x * 0.16),      # Spirals after being hit
    }
    
    # ODI-specific traits (only active in ODI matches)
    odi_effects = {
        'ODI_MIDDLE_OVERS_STALLER': lambda x: 1 - (x * 0.12),   # Bogged down overs 11-40
        'ODI_SLOG_MISFIRE': lambda x: 1 - (x * 0.12),           # Mistimes in overs 40-50
        'ODI_POOR_STRIKE_ROTATION': lambda x: 1 - (x * 0.10),   # Can't find gaps
        'ODI_COLLAPSER': lambda x: 1 - (x * 0.12),              # Falls in clusters
        'ODI_CHASE_BOTTLER': lambda x: 1 - (x * 0.12),          # Fails chasing
        'ODI_MIDDLE_OVERS_EXPENSIVE': lambda x: 1 - (x * 0.12), # Leaks overs 11-40
        'ODI_NO_WICKET_TAKER': lambda x: 1 - (x * 0.10),        # Tidy but no threat
        'ODI_DEATH_OVERS_LEAKER': lambda x: 1 - (x * 0.14),     # Leaks overs 40-50
        'ODI_FIRST_SPELL_ONLY': lambda x: 1 - (x * 0.10),       # Falls apart in later spells
        'ODI_PARTNERSHIP_FEEDER': lambda x: 1 - (x * 0.10),      # Feeds set batters
    }
    
    # Test-specific traits (only active in Test matches)
    test_effects = {
        'TEST_NEW_BALL_BUNNY': lambda x: 1 - (x * 0.16),        # Edges in first 20 overs
        'TEST_POOR_CONCENTRATION': lambda x: 1 - (x * 0.12),    # Throws away 30-70
        'TEST_DAY5_CRUMBLER': lambda x: 1 - (x * 0.14),         # Fails on worn pitches
        'TEST_SECOND_INNINGS_FLOP': lambda x: 1 - (x * 0.12),   # Fails 2nd innings
        'TEST_BOUNCER_VICTIM': lambda x: 1 - (x * 0.16),        # Flinches at short ball
        'TEST_NO_STAMINA': lambda x: 1 - (x * 0.14),            # Drops after 5 overs
        'TEST_FLAT_PITCH_PASSENGER': lambda x: 1 - (x * 0.14),  # Useless on flat decks
        'TEST_REVERSE_SWING_HOPELESS': lambda x: 1 - (x * 0.12),# No reverse with old ball
        'TEST_DAY5_TOOTHLESS': lambda x: 1 - (x * 0.14),        # Can't exploit worn pitch
        'TEST_SPELL_BREAKER': lambda x: 1 - (x * 0.10),         # Loses it between spells
    }
    
    # All 30 traits in one lookup (each trait only fires in its format's simulator)
    all_effects = {**t20_effects, **odi_effects, **test_effects}
    
    if trait_name in all_effects:
        return all_effects[trait_name](strength_level)
    return 1.0
