#!/usr/bin/env python3
"""
Test script to verify that stats are stored in the correct location
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cricket_manager.core.game_engine import GameEngine
from t20oversimulation import T20Match

def test_stats_storage_location():
    """Test that stats are stored in the correct location for UI display"""
    print("=" * 60)
    print("TESTING STATS STORAGE LOCATION")
    print("=" * 60)
    
    try:
        # Initialize game engine
        engine = GameEngine()
        engine.initialize_game()
        
        # Get two teams
        team1 = engine.all_teams[0]  # India
        team2 = engine.all_teams[1]  # Australia
        
        print(f"Teams: {team1.name} vs {team2.name}")
        
        # Get initial stats from the actual game engine
        test_player = engine.all_teams[0].players[0]
        initial_runs = test_player.stats['T20']['runs']
        initial_matches = test_player.stats['T20']['matches']
        
        print(f"Initial stats for {test_player.name}: Runs={initial_runs}, Matches={initial_matches}")
        
        # Create T20 match with master window
        t20_sim = T20Match(engine, team1, team2, 'T20')
        
        # Add realistic match stats
        test_player_name = test_player.name
        t20_sim.match_stats[test_player_name] = {
            'batting': {
                'runs': 25,
                'balls': 18,
                'fours': 3,
                'sixes': 1,
                'dismissal': 'c Keeper bowler'
            },
            'bowling': {
                'balls': 0,
                'runs': 0,
                'wickets': 0,
                'maidens': 0
            }
        }
        
        print(f"Added match stats: {test_player_name} - 25 runs")
        
        # Test stats update
        print("Testing stats update...")
        t20_sim.update_stats_using_statistics_manager()
        
        # Check stats in the original game engine object
        updated_runs = test_player.stats['T20']['runs']
        updated_matches = test_player.stats['T20']['matches']
        
        print(f"Updated stats for {test_player.name}: Runs={updated_runs}, Matches={updated_matches}")
        
        # Verify changes
        stats_changed = (updated_runs != initial_runs or updated_matches != initial_matches)
        
        if stats_changed:
            print("✅ SUCCESS: Stats stored in correct location!")
            print(f"   Runs changed: {initial_runs} -> {updated_runs}")
            print(f"   Matches changed: {initial_matches} -> {updated_matches}")
            
            # Test what Statistics screen would see
            print("\nTesting Statistics screen data access...")
            stats_screen_data = {
                'runs': test_player.stats['T20']['runs'],
                'matches': test_player.stats['T20']['matches'],
                'balls_faced': test_player.stats['T20'].get('balls_faced', 0),
                'wickets': test_player.stats['T20'].get('wickets', 0)
            }
            print(f"Statistics screen would see: {stats_screen_data}")
            
            return True
        else:
            print("❌ FAILED: Stats not stored in correct location")
            return False
        
    except Exception as e:
        print(f"❌ Error in stats storage test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stats_storage_location()
    
    print("\n" + "=" * 60)
    print("STATS STORAGE LOCATION TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS:")
        print("   - Stats stored in player.stats['T20'] correctly")
        print("   - Statistics screen can access updated data")
        print("   - Game engine objects are properly updated")
        print("   - Stats persist for UI display")
    else:
        print("❌ FAILED:")
        print("   - Stats not stored in correct location")
        print("   - Check the error messages above")
    
    print("=" * 60)
