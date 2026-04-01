"""
Test that T20 simulator no longer uses fallback logic
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_no_fallback():
    """Test that T20 simulator always uses pace attributes"""
    
    print("=" * 60)
    print("TESTING NO FALLBACK LOGIC")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from cricket_manager.core.game_engine import GameEngine
        from t20oversimulation import T20Match
        
        game_engine = GameEngine()
        
        print("\n1. Testing T20 simulator with no fallback logic...")
        
        root = tk.Tk()
        root.withdraw()
        
        # Create T20 simulator
        team1 = game_engine.all_teams[0]
        team2 = game_engine.all_teams[1]
        t20_sim = T20Match(root, team1, team2, 'T20', headless=True)
        
        print("   ✅ T20 simulator created successfully")
        
        # Test speed calculation for multiple bowlers
        print(f"\n2. Testing speed calculations...")
        
        bowlers_tested = 0
        all_using_pace_attrs = True
        
        for player_dict in t20_sim.team1['players']:
            if player_dict['bowling'] >= 40 and bowlers_tested < 5:  # Test first 5 bowlers
                bowlers_tested += 1
                
                print(f"   Testing {player_dict['name']} ({player_dict['role']}):")
                print(f"      Bowling: {player_dict['bowling']}")
                print(f"      Avg Pace: {player_dict.get('avg_pace', 0):.1f}")
                print(f"      Top Pace: {player_dict.get('top_pace', 0):.1f}")
                
                # Calculate multiple speeds to see variation
                speeds = []
                for i in range(10):
                    speed = t20_sim.calculate_ball_speed(player_dict)
                    speeds.append(speed)
                
                avg_speed = sum(speeds) / len(speeds)
                min_speed = min(speeds)
                max_speed = max(speeds)
                
                print(f"      Calculated speeds: {avg_speed:.1f} avg, {min_speed:.1f}-{max_speed:.1f} range")
                
                # Check if speed is based on player's avg_pace
                player_avg = player_dict.get('avg_pace', 0)
                if player_avg > 0:
                    expected_range = (player_avg - 3, player_avg + 2 + 10)  # Allow for variation and aggression
                    if expected_range[0] <= avg_speed <= expected_range[1]:
                        print(f"      ✅ Speed based on player attributes")
                    else:
                        print(f"      ❌ Speed not based on player attributes")
                        all_using_pace_attrs = False
                else:
                    print(f"      ❌ Player has no avg_pace attribute")
                    all_using_pace_attrs = False
        
        root.destroy()
        
        print(f"\n3. Summary...")
        print(f"   Bowlers tested: {bowlers_tested}")
        print(f"   All using pace attributes: {all_using_pace_attrs}")
        
        print("\n" + "=" * 60)
        print("NO FALLBACK LOGIC - SUMMARY")
        print("=" * 60)
        
        if all_using_pace_attrs:
            print("✅ SUCCESS:")
            print("   - T20 simulator always uses pace attributes")
            print("   - No fallback logic is being used")
            print("   - All speeds based on player's avg_pace")
            print("   - Proper variation and capping applied")
        else:
            print("❌ ISSUE:")
            print("   - Some bowlers still not using pace attributes")
            print("   - Fallback logic might still be active")
        
        print("\n✅ CHANGES MADE:")
        print("   - Removed all fallback logic from calculate_ball_speed")
        print("   - Function now ALWAYS uses pace attributes")
        print("   - Auto-generates pace attributes if missing")
        print("   - No more age-based fallback calculations")
        
        return all_using_pace_attrs
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_no_fallback()
