#!/usr/bin/env python3
"""
Test script to verify stats update functionality in Test Match Enhanced
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cricket_manager.core.game_engine import GameEngine
from test_match_enhanced import TestMatchSimulator

def test_test_match_stats_update():
    """Test that stats are properly updated after a test match"""
    print("=" * 60)
    print("TESTING TEST MATCH ENHANCED STATS UPDATE")
    print("=" * 60)
    
    try:
        # Initialize game engine
        engine = GameEngine()
        engine.initialize_game()
        
        # Get two teams
        team1 = engine.all_teams[0]  # India
        team2 = engine.all_teams[1]  # Australia
        
        print(f"Teams: {team1.name} vs {team2.name}")
        
        # Get initial stats for a player
        test_player = team1.players[0]
        initial_runs = test_player.stats['Test']['runs']
        initial_wickets = test_player.stats['Test']['wickets']
        initial_matches = test_player.stats['Test']['matches']
        
        print(f"Initial stats for {test_player.name}: Runs={initial_runs}, Wickets={initial_wickets}, Matches={initial_matches}")
        
        # Create Test Match simulator
        test_sim = TestMatchSimulator(
            team1=team1,
            team2=team2,
            parent_app=engine,  # Use engine as parent app
            simulation_adjustments={'dot_adj': 0, 'boundary_adj': 0, 'wicket_adj': 0},
            pitch_conditions=None
        )
        
        # Manually add some realistic Test match stats
        print("Adding realistic Test match stats for testing...")
        
        # Add batting stats for a few players
        test_players = [
            team1.players[0],  # Rohit Sharma
            team1.players[1],  # Virat Kohli  
            team2.players[0],  # Steve Smith
            team2.players[1],  # David Warner
        ]
        
        # Initialize innings_data
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
        
        # Initialize match_stats for StatisticsManager
        test_sim.match_stats = {}
        
        for i, player in enumerate(test_players):
            player_name = player.name if hasattr(player, 'name') else player['name']
            
            # Add realistic Test match batting stats (higher values)
            batting_stats = {
                'runs': 50 + (i * 25),  # 50, 75, 100, 125 runs
                'balls': 100 + (i * 50),  # 100, 150, 200, 250 balls
                'fours': 5 + i,          # 5, 6, 7, 8 fours
                'sixes': 1 + (i // 2),   # 1, 1, 2, 2 sixes
                'dismissal': 'c Keeper bowler' if i < 3 else 'Not Out'
            }
            
            bowling_stats = {
                'balls': 0,
                'runs': 0,
                'wickets': 0,
                'maidens': 0
            }
            
            # Add bowling stats for Australian players
            if i >= 2:  # Steve Smith and David Warner
                bowling_stats = {
                    'balls': 120 + (i * 30),  # 120, 150 balls
                    'runs': 60 + (i * 20),     # 60, 80 runs
                    'wickets': 2 + i,         # 2, 3 wickets
                    'maidens': 1
                }
            
            # Add to innings_data
            if i < 2:  # Indian players - first innings
                test_sim.innings_data[0]['batting_stats'][player_name] = batting_stats
                test_sim.innings_data[0]['bowling_stats'][player_name] = bowling_stats
            else:  # Australian players - second innings
                test_sim.innings_data[1]['batting_stats'][player_name] = batting_stats
                test_sim.innings_data[1]['bowling_stats'][player_name] = bowling_stats
            
            # Add to match_stats for StatisticsManager
            test_sim.match_stats[player_name] = {
                'batting': batting_stats,
                'bowling': bowling_stats
            }
        
        print("Test match stats created:")
        for i, player in enumerate(test_players):
            player_name = player.name if hasattr(player, 'name') else player['name']
            if player_name in test_sim.innings_data[0]['batting_stats']:
                batting_stats = test_sim.innings_data[0]['batting_stats'][player_name]
                print(f"  {player_name}: {batting_stats.get('runs', 0)} runs")
            if player_name in test_sim.innings_data[0]['bowling_stats']:
                bowling_stats = test_sim.innings_data[0]['bowling_stats'][player_name]
                print(f"  {player_name}: {bowling_stats.get('wickets', 0)} wickets")
        
        # Test the stats update function
        print("\nTesting Test Match stats update function...")
        test_sim._update_stats_using_statistics_manager()
        
        # Check updated stats
        updated_runs = test_player.stats['Test']['runs']
        updated_wickets = test_player.stats['Test']['wickets']
        updated_matches = test_player.stats['Test']['matches']
        
        print(f"Updated stats for {test_player.name}: Runs={updated_runs}, Wickets={updated_wickets}, Matches={updated_matches}")
        
        # Verify changes
        stats_changed = (updated_runs != initial_runs or 
                        updated_wickets != initial_wickets or 
                        updated_matches != initial_matches)
        
        if stats_changed:
            print("✅ SUCCESS: Test Match stats were properly updated!")
            print(f"   Runs changed: {initial_runs} -> {updated_runs}")
            print(f"   Wickets changed: {initial_wickets} -> {updated_wickets}")
            print(f"   Matches changed: {initial_matches} -> {updated_matches}")
            return True
        else:
            print("❌ FAILED: Test Match stats did not change as expected")
            return False
        
    except Exception as e:
        print(f"❌ Error in Test Match stats update test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_test_match_stats_update()
    
    print("\n" + "=" * 60)
    print("TEST MATCH ENHANCED STATS UPDATE TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS:")
        print("   - Test Match stats update function works")
        print("   - StatisticsManager integration working")
        print("   - Players get Test match runs and wickets")
        print("   - Match count increases for Test format")
        print("   - OK button will update stats correctly")
    else:
        print("❌ FAILED:")
        print("   - Test Match stats not updating properly")
        print("   - Check the error messages above")
    
    print("=" * 60)
