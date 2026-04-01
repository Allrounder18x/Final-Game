"""
Enhanced Match Simulator Thread - Integration with t20oversimulation.py and test_match_enhanced.py
Step 6: Backend Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QThread, pyqtSignal


class EnhancedMatchSimulatorThread(QThread):
    """Thread for running match simulation using actual backends"""
    update_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, match_type, team1, team2, match_format, batting_aggression=50, bowling_aggression=50, 
                 pace_rating=5, spin_rating=5, bounce_rating=5, bowling_line='Good Length', 
                 field_setting='Balanced'):
        super().__init__()
        self.match_type = match_type
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.batting_aggression = batting_aggression
        self.bowling_aggression = bowling_aggression
        self.pace_rating = pace_rating
        self.spin_rating = spin_rating
        self.bounce_rating = bounce_rating
        self.bowling_line = bowling_line
        self.field_setting = field_setting
        self.result = None
        self.match_instance = None
        
    def run(self):
        """Run the match simulation using actual backends"""
        try:
            if self.match_type in ['T20', 'ODI']:
                # Use t20oversimulation.py - run in main thread
                from t20oversimulation import T20Match
                
                # Convert teams to expected format
                team1_data = self._convert_team_to_format(self.team1)
                team2_data = self._convert_team_to_format(self.team2)
                
                print(f"[Thread] Starting {self.match_format} match: {team1_data['name']} vs {team2_data['name']}")
                
                # Signal that we're ready to create the match
                self.update_signal.emit({
                    'status': 'creating_match',
                    'team1_data': team1_data,
                    'team2_data': team2_data,
                    'match_format': self.match_format,
                    'batting_aggression': self.batting_aggression,
                    'bowling_aggression': self.bowling_aggression,
                    'pace_rating': self.pace_rating,
                    'spin_rating': self.spin_rating,
                    'bounce_rating': self.bounce_rating,
                    'bowling_line': self.bowling_line,
                    'field_setting': self.field_setting
                })
                
                # Wait for match to complete (will be handled by main thread)
                while not hasattr(self, 'match_ended') or not self.match_ended:
                    self.msleep(100)
                
                # Get result
                self.result = {
                    'winner': getattr(self, 'result', 'Unknown'),
                    'team1_score': f"{getattr(self, 'first_innings_score', 0)}/{getattr(self, 'first_innings_wickets', 0)}",
                    'team2_score': f"{getattr(self, 'total_runs', 0)}/{getattr(self, 'total_wickets', 0)}",
                    'match_stats': getattr(self, 'match_stats', {}),
                    'pitch_conditions': {
                        'pace': getattr(self, 'pitch_pace_rating', self.pace_rating),
                        'spin': getattr(self, 'pitch_spin_rating', self.spin_rating),
                        'bounce': getattr(self, 'pitch_bounce_rating', self.bounce_rating)
                    },
                    'final_scorecard': self._get_scorecard()
                }
                
            else:  # Test match
                # Use test_match_enhanced.py
                from test_match_enhanced import TestMatchSimulator
                
                # Convert teams to expected format
                team1_data = self._convert_team_to_format(self.team1)
                team2_data = self._convert_team_to_format(self.team2)
                
                print(f"[Thread] Starting Test match: {team1_data['name']} vs {team2_data['name']}")
                
                # Create test match with all parameters
                self.match_instance = TestMatchSimulator(team1_data, team2_data)
                
                # Set up the match
                self.match_instance.auto_select_xi(team1_data)
                self.match_instance.auto_select_xi(team2_data)
                
                print("[Thread] Test match setup complete")
                
                # Simulate the full match
                self.match_instance.simulate_full_match()
                print("[Thread] Test match simulation complete")
                
                # Get result
                self.result = {
                    'winner': getattr(self.match_instance, 'winner', 'Unknown'),
                    'result': getattr(self.match_instance, 'result', 'Unknown'),
                    'innings_data': getattr(self.match_instance, 'innings_data', []),
                    'pitch_type': getattr(self.match_instance, 'pitch_type', 'Unknown'),
                    'pitch_conditions': {
                        'pace': getattr(self.match_instance, 'pitch_pace', self.pace_rating),
                        'spin': getattr(self.match_instance, 'pitch_spin', self.spin_rating),
                        'bounce': getattr(self.match_instance, 'pitch_bounce', self.bounce_rating)
                    },
                    'final_scorecard': {}
                }
            
            print(f"[Thread] Result: {self.result}")
            self.finished_signal.emit(self.result)
            
        except Exception as e:
            print(f"[Thread] Match simulation error: {e}")
            import traceback
            traceback.print_exc()
            self.result = {'error': str(e)}
            self.finished_signal.emit(self.result)
    
    def _convert_team_to_format(self, team):
        """Convert team object to expected format for simulators"""
        players = []
        for player in team.players:
            players.append({
                'name': player.name,
                'role': player.role,
                'batting': player.batting,
                'bowling': player.bowling,
                'fielding': player.fielding,
                'age': player.age
            })
        
        return {
            'name': team.name,
            'players': players
        }
    
    def _get_scorecard(self):
        """Get scorecard from match instance"""
        try:
            if hasattr(self.match_instance, 'get_scorecard'):
                return self.match_instance.get_scorecard()
            else:
                return {}
        except Exception as e:
            print(f"[Thread] Error getting scorecard: {e}")
            return {}
    
    def msleep(self, milliseconds):
        """Sleep for specified milliseconds"""
        import time
        time.sleep(milliseconds / 1000.0)
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.match_instance:
            try:
                self.match_instance.match_ended = True
            except:
                pass
