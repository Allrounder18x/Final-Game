
import sys
import os
import pickle

# Add DATA directory to path
sys.path.insert(0, r"C:\Users\Admin\Downloads\Pro Cricket Final (3)\Pro Cricket Test\Cricket Cap Cum Coach\DATA")

from t20oversimulation import T20Match

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

# Create match with NO master window
match = T20Match(None, team1_data, team2_data, "T20", headless=False, pitch_conditions=pitch_cond)
match.setup_match()

# Start Tkinter main loop directly on match window
match.match_window.mainloop()

# After match window closes, save the match result to a file
result_file = os.path.join(temp_dir, 'temp_match_result.pkl')
try:
    match_result = {
        'team1_name': match.team1['name'],
        'team2_name': match.team2['name'],
        'team1_score': match.first_innings_score,
        'team1_wickets': match.first_innings_wickets,
        'team2_score': match.total_runs,
        'team2_wickets': match.total_wickets,
        'result': match.result,
        'match_stats': match.match_stats,
        'match_format': match.match_format,
        'winner': match.result if match.result else 'Unknown'
    }
    with open(result_file, 'wb') as f:
        pickle.dump(match_result, f)
    print(f"Match result saved to {result_file}")
except Exception as e:
    print(f"Error saving match result: {e}")
