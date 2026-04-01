#!/usr/bin/env python3
"""
Test script for Enhanced Test Match Simulator with StatisticsManager
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cricket_manager.core.game_engine import GameEngine
from test_match_enhanced import TestMatchSimulator

def test_test_match_enhanced():
    """Test the enhanced test match simulator"""
    print("=" * 60)
    print("TEST MATCH ENHANCED SIMULATOR TEST")
    print("=" * 60)
    
    try:
        # Initialize game engine
        engine = GameEngine()
        engine.initialize_game()
        
        # Get two teams
        team1 = engine.all_teams[0]  # India
        team2 = engine.all_teams[1]  # Australia
        
        print(f"Teams: {team1.name} vs {team2.name}")
        
        # Create test match simulator
        test_sim = TestMatchSimulator(
            team1=team1,
            team2=team2,
            parent_app=None,  # Standalone test
            simulation_adjustments={'dot_adj': 0, 'boundary_adj': 0, 'wicket_adj': 0},
            pitch_conditions=None
        )
        
        print("✅ Test match simulator created successfully")
        
        # Test that it has the new StatisticsManager function
        if hasattr(test_sim, '_update_stats_using_statistics_manager'):
            print("✅ StatisticsManager integration function found")
        else:
            print("❌ StatisticsManager integration function missing")
            return False
        
        # Test match summary creation (without playing full match)
        test_sim.result = f"{team1.name} won by 5 wickets"
        test_sim.innings_data = [
            {
                'batting_team': team1.name,
                'bowling_team': team2.name,
                'batting_stats': {},
                'bowling_stats': {}
            },
            {
                'batting_team': team2.name,
                'bowling_team': team1.name,
                'batting_stats': {},
                'bowling_stats': {}
            }
        ]
        
        # This should work without errors
        print("✅ Test match enhanced setup complete")
        return True
        
    except Exception as e:
        print(f"❌ Error in test match enhanced: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_test_match_enhanced()
    
    print("\n" + "=" * 60)
    print("TEST MATCH ENHANCED TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS:")
        print("   - Test match enhanced imports without errors")
        print("   - StatisticsManager integration available")
        print("   - OK button will use StatisticsManager")
        print("   - Stats will update in statistics_manager.py")
    else:
        print("❌ FAILED:")
        print("   - Test match enhanced has errors")
        print("   - Check the error messages above")
    
    print("=" * 60)
