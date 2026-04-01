"""
Simple Match Launcher - Launches original simulators directly
"""

import sys
import os
import subprocess
import pickle

def launch_t20_match(team1, team2, match_format='T20', pitch_conditions=None):
    """Launch T20/ODI match simulator in a separate process.
    Returns (process, result_file_path) tuple so caller can wait for result."""
    try:
        # Convert teams to expected format
        team1_data = {
            'name': team1.name,
            'players': [
                {
                    'name': player.name,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling,
                    'fielding': player.fielding,
                    'age': player.age
                }
                for player in team1.players
            ]
        }
        
        team2_data = {
            'name': team2.name,
            'players': [
                {
                    'name': player.name,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling,
                    'fielding': player.fielding,
                    'age': player.age
                }
                for player in team2.players
            ]
        }
        
        temp_dir = os.path.dirname(__file__)
        result_file = os.path.join(temp_dir, 'temp_match_result.pkl')
        
        # Remove old result file if it exists
        if os.path.exists(result_file):
            try:
                os.remove(result_file)
            except:
                pass
        
        # Create a simple script to launch the match
        script_content = f'''
import sys
import os
import pickle

# Add DATA directory to path
sys.path.insert(0, r"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")

from t20oversimulation import T20Match

# Load team data and pitch conditions from pickle files
temp_dir = r"{os.path.dirname(__file__)}"
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
match = T20Match(None, team1_data, team2_data, "{match_format}", headless=False, pitch_conditions=pitch_cond)
match.setup_match()

# Start Tkinter main loop directly on match window
match.match_window.mainloop()

# After match window closes, save the match result to a file
result_file = os.path.join(temp_dir, 'temp_match_result.pkl')
try:
    match_result = {{
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
    }}
    with open(result_file, 'wb') as f:
        pickle.dump(match_result, f)
    print(f"Match result saved to {{result_file}}")
except Exception as e:
    print(f"Error saving match result: {{e}}")
'''
        
        # Save team data and pitch conditions to temporary pickle files
        with open(os.path.join(temp_dir, 'temp_team1.pkl'), 'wb') as f:
            pickle.dump(team1_data, f)
        with open(os.path.join(temp_dir, 'temp_team2.pkl'), 'wb') as f:
            pickle.dump(team2_data, f)
        with open(os.path.join(temp_dir, 'temp_pitch.pkl'), 'wb') as f:
            pickle.dump(pitch_conditions, f)
        
        # Write script to temporary file
        temp_file = os.path.join(temp_dir, 'temp_t20_match.py')
        with open(temp_file, 'w') as f:
            f.write(script_content)
        
        # Launch in separate process and return handle
        process = subprocess.Popen([sys.executable, temp_file])
        
        return (process, result_file)
        
    except Exception as e:
        print(f"Error launching T20 match: {e}")
        return None

def launch_test_match(team1, team2, pitch_conditions=None):
    """Launch Test match simulator in a separate process.
    Returns (process, result_file_path) tuple so caller can wait for result and update stats."""
    try:
        # Convert teams to expected format
        team1_data = {
            'name': team1.name,
            'players': [
                {
                    'name': player.name,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling,
                    'fielding': player.fielding,
                    'age': player.age
                }
                for player in team1.players
            ]
        }
        
        team2_data = {
            'name': team2.name,
            'players': [
                {
                    'name': player.name,
                    'role': player.role,
                    'batting': player.batting,
                    'bowling': player.bowling,
                    'fielding': player.fielding,
                    'age': player.age
                }
                for player in team2.players
            ]
        }
        
        temp_dir = os.path.dirname(__file__)
        result_file = os.path.join(temp_dir, 'temp_match_result.pkl')
        
        # Remove old result file if it exists
        if os.path.exists(result_file):
            try:
                os.remove(result_file)
            except:
                pass
        
        # Create script to launch the match and save result (like T20)
        script_content = f'''
import sys
import os
import pickle

# Add DATA directory to path
sys.path.insert(0, r"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")

from test_match_enhanced import TestMatchSimulator

# Load team data and pitch conditions from pickle files
temp_dir = r"{os.path.dirname(__file__)}"
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
    inn1 = test_match.innings_data[0] if test_match.innings_data else {{'score': 0, 'wickets': 0}}
    inn2 = test_match.innings_data[1] if len(test_match.innings_data) > 1 else {{'score': 0, 'wickets': 0}}
    inn3 = test_match.innings_data[2] if len(test_match.innings_data) > 2 else {{'score': 0, 'wickets': 0}}
    inn4 = test_match.innings_data[3] if len(test_match.innings_data) > 3 else {{'score': 0, 'wickets': 0}}
    team1_score = inn1['score'] + inn3['score'] if len(test_match.innings_data) >= 3 else inn1['score']
    team1_wickets = inn1['wickets'] + inn3['wickets'] if len(test_match.innings_data) >= 3 else inn1['wickets']
    team2_score = inn2['score'] + inn4['score'] if len(test_match.innings_data) >= 4 else inn2['score']
    team2_wickets = inn2['wickets'] + inn4['wickets'] if len(test_match.innings_data) >= 4 else inn2['wickets']
    match_result = {{
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
    }}
    with open(result_file, 'wb') as f:
        pickle.dump(match_result, f)
    print(f"Test match result saved to {{result_file}}")
except Exception as e:
    print(f"Error saving test match result: {{e}}")
'''
        
        # Save team data and pitch conditions to temporary pickle files
        with open(os.path.join(temp_dir, 'temp_team1.pkl'), 'wb') as f:
            pickle.dump(team1_data, f)
        with open(os.path.join(temp_dir, 'temp_team2.pkl'), 'wb') as f:
            pickle.dump(team2_data, f)
        with open(os.path.join(temp_dir, 'temp_pitch.pkl'), 'wb') as f:
            pickle.dump(pitch_conditions, f)
        
        # Write script to temporary file
        temp_file = os.path.join(temp_dir, 'temp_test_match.py')
        with open(temp_file, 'w') as f:
            f.write(script_content)
        
        # Launch in separate process and return handle (like T20)
        process = subprocess.Popen([sys.executable, temp_file])
        
        return (process, result_file)
        
    except Exception as e:
        print(f"Error launching Test match: {e}")
        return None

if __name__ == "__main__":
    # Test function
    print("Match Launcher - Test")
    print("Use launch_t20_match() or launch_test_match() from your main application")
