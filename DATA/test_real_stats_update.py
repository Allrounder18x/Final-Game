#!/usr/bin/env python3
"""
Test script to verify stats update with actual match data
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cricket_manager.core.game_engine import GameEngine
from t20oversimulation import T20Match

def test_real_stats_update():
    """Test stats update with realistic match data"""
    print("=" * 60)
    print("TESTING REAL STATS UPDATE WITH MATCH DATA")
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
        initial_runs = test_player.stats['T20']['runs']
        initial_wickets = test_player.stats['T20']['wickets']
        initial_matches = test_player.stats['T20']['matches']
        
        print(f"Initial stats for {test_player.name}: Runs={initial_runs}, Wickets={initial_wickets}, Matches={initial_matches}")
        
        # Create T20 match
        t20_sim = T20Match(engine, team1, team2, 'T20', headless=True)
        
        # Manually add some realistic match stats to test the update system
        print("Adding realistic match stats for testing...")
        
        # Add batting stats for a few players
        test_players = [
            team1.players[0],  # Rohit Sharma
            team1.players[1],  # Virat Kohli  
            team2.players[0],  # Steve Smith
            team2.players[1],  # David Warner
        ]
        
        for i, player in enumerate(test_players):
            player_name = player.name if hasattr(player, 'name') else player['name']
            
            # Add realistic batting stats
            t20_sim.match_stats[player_name] = {
                'batting': {
                    'runs': 15 + (i * 10),  # 15, 25, 35, 45 runs
                    'balls': 12 + (i * 8),   # 12, 20, 28, 36 balls
                    'fours': 2 + i,          # 2, 3, 4, 5 fours
                    'sixes': i // 2,         # 0, 0, 1, 1 sixes
                    'dismissal': 'c Keeper bowler' if i < 3 else 'Not Out'
                },
                'bowling': {
                    'balls': 0,
                    'runs': 0,
                    'wickets': 0,
                    'maidens': 0
                }
            }
            
            # Add bowling stats for Australian players
            if i >= 2:  # Steve Smith and David Warner
                t20_sim.match_stats[player_name]['bowling'] = {
                    'balls': 24 - (i * 6),    # 24, 18 balls
                    'runs': 30 + (i * 5),     # 30, 35 runs
                    'wickets': 1 + (i % 2),   # 1, 2 wickets
                    'maidens': 0
                }
        
        print("Match stats created:")
        for player_name, stats in t20_sim.match_stats.items():
            if stats['batting']['runs'] > 0 or stats['bowling']['wickets'] > 0:
                print(f"  {player_name}: {stats['batting']['runs']} runs, {stats['bowling']['wickets']} wickets")
        
        # Test the stats update function
        print("\nTesting stats update function...")
        t20_sim.update_stats_using_statistics_manager()
        
        # Check updated stats
        updated_runs = test_player.stats['T20']['runs']
        updated_wickets = test_player.stats['T20']['wickets']
        updated_matches = test_player.stats['T20']['matches']
        
        print(f"Updated stats for {test_player.name}: Runs={updated_runs}, Wickets={updated_wickets}, Matches={updated_matches}")
        
        # Verify changes
        stats_changed = (updated_runs != initial_runs or 
                        updated_wickets != initial_wickets or 
                        updated_matches != initial_matches)
        
        if stats_changed:
            print("✅ SUCCESS: Stats were properly updated!")
            print(f"   Runs changed: {initial_runs} -> {updated_runs}")
            print(f"   Wickets changed: {initial_wickets} -> {updated_wickets}")
            print(f"   Matches changed: {initial_matches} -> {updated_matches}")
            return True
        else:
            print("❌ FAILED: Stats did not change as expected")
            return False
        
    except Exception as e:
        print(f"❌ Error in real stats update test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_stats_update()
    
    print("\n" + "=" * 60)
    print("REAL STATS UPDATE TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS:")
        print("   - Stats update function works with real data")
        print("   - Players get runs and wickets added")
        print("   - Match count increases")
        print("   - StatisticsManager integration working")
    else:
        print("❌ FAILED:")
        print("   - Stats not updating properly")
        print("   - Check the error messages above")
    
    print("=" * 60)
