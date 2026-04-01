
import sys
import os
import pickle

# Add DATA directory to path
sys.path.insert(0, r"C:\Users\Admin\Downloads\Pro Cricket Final (3)\Pro Cricket Test\Cricket Cap Cum Coach\DATA")

from test_match_enhanced import TestMatchSimulator

# Load team data and pitch conditions from pickle files
temp_dir = r"C:\Users\Admin\Downloads\Pro Cricket Final (3)\Pro Cricket Test\Cricket Cap Cum Coach\DATA\cricket_manager\ui"
with open(os.path.join(temp_dir, 'temp_team1.pkl'), 'rb') as f:
    team1_data = pickle.load(f)
with open(os.path.join(temp_dir, 'temp_team2.pkl'), 'rb') as f:
    team2_data = pickle.load(f)
pitch_cond = None
try:
    with open(os.path.join(temp_dir, 'temp_pitch.pkl'), 'rb') as f:
        pitch_cond = pickle.load(f)
except:
    pass

# Create test match with NO parent window
test_match = TestMatchSimulator(team1_data, team2_data, parent_app=None, pitch_conditions=pitch_cond)
test_match.auto_select_xi(team1_data)
test_match.auto_select_xi(team2_data)
test_match.create_gui()

# Start Tkinter main loop directly on test match window
test_match.root.mainloop()

# After match window closes, save the match result for stats update (like T20)
result_file = os.path.join(temp_dir, 'temp_match_result.pkl')
try:
    match_stats = test_match.get_match_stats_for_result()
    inn1 = test_match.innings_data[0] if test_match.innings_data else {'score': 0, 'wickets': 0}
    inn2 = test_match.innings_data[1] if len(test_match.innings_data) > 1 else {'score': 0, 'wickets': 0}
    inn3 = test_match.innings_data[2] if len(test_match.innings_data) > 2 else {'score': 0, 'wickets': 0}
    inn4 = test_match.innings_data[3] if len(test_match.innings_data) > 3 else {'score': 0, 'wickets': 0}
    team1_score = inn1['score'] + inn3['score'] if len(test_match.innings_data) >= 3 else inn1['score']
    team1_wickets = inn1['wickets'] + inn3['wickets'] if len(test_match.innings_data) >= 3 else inn1['wickets']
    team2_score = inn2['score'] + inn4['score'] if len(test_match.innings_data) >= 4 else inn2['score']
    team2_wickets = inn2['wickets'] + inn4['wickets'] if len(test_match.innings_data) >= 4 else inn2['wickets']
    match_result = {
        'team1_name': team1_data['name'],
        'team2_name': team2_data['name'],
        'team1_score': team1_score,
        'team1_wickets': team1_wickets,
        'team2_score': team2_score,
        'team2_wickets': team2_wickets,
        'result': test_match.result or 'Match Drawn',
        'match_stats': match_stats,
        'match_format': 'Test',
        'winner': test_match.winner or 'Draw'
    }
    with open(result_file, 'wb') as f:
        pickle.dump(match_result, f)
    print(f"Test match result saved to {result_file}")
except Exception as e:
    print(f"Error saving test match result: {e}")
