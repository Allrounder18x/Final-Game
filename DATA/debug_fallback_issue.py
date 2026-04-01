"""
Debug why T20 simulator is using fallback logic
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_fallback_issue():
    """Debug why T20 simulator is using fallback logic instead of pace attributes"""
    
    print("=" * 60)
    print("DEBUGGING FALLBACK LOGIC ISSUE")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from cricket_manager.core.game_engine import GameEngine
        from t20oversimulation import T20Match
        
        game_engine = GameEngine()
        
        print("\n1. Checking original player pace attributes...")
        
        # Check a few bowlers from the first team
        team = game_engine.all_teams[0]
        bowlers_with_pace = 0
        bowlers_without_pace = 0
        
        for player in team.players:
            if player.bowling >= 40:  # Only check actual bowlers
                has_avg_pace = hasattr(player, 'avg_pace') and player.avg_pace > 0
                has_top_pace = hasattr(player, 'top_pace') and player.top_pace > 0
                
                print(f"   {player.name} ({player.role}):")
                print(f"      Bowling: {player.bowling}")
                print(f"      Has avg_pace: {has_avg_pace} ({getattr(player, 'avg_pace', 0):.1f})")
                print(f"      Has top_pace: {has_top_pace} ({getattr(player, 'top_pace', 0):.1f})")
                
                if has_avg_pace and has_top_pace:
                    bowlers_with_pace += 1
                    print(f"      ✅ Has pace attributes")
                else:
                    bowlers_without_pace += 1
                    print(f"      ❌ Missing pace attributes - will use fallback")
                
                if bowlers_with_pace + bowlers_without_pace >= 5:  # Check first 5 bowlers
                    break
        
        print(f"\n2. Summary of original players:")
        print(f"   Bowlers with pace attributes: {bowlers_with_pace}")
        print(f"   Bowlers without pace attributes: {bowlers_without_pace}")
        
        print(f"\n3. Checking converted team dictionaries...")
        
        root = tk.Tk()
        root.withdraw()
        
        # Create T20 simulator
        t20_sim = T20Match(root, team, game_engine.all_teams[1], 'T20', headless=True)
        
        converted_bowlers_with_pace = 0
        converted_bowlers_without_pace = 0
        
        for player_dict in t20_sim.team1['players']:
            if player_dict['bowling'] >= 40:  # Only check actual bowlers
                has_avg_pace = player_dict.get('avg_pace', 0) > 0
                has_top_pace = player_dict.get('top_pace', 0) > 0
                
                print(f"   {player_dict['name']} ({player_dict['role']}):")
                print(f"      Bowling: {player_dict['bowling']}")
                print(f"      Has avg_pace: {has_avg_pace} ({player_dict.get('avg_pace', 0):.1f})")
                print(f"      Has top_pace: {has_top_pace} ({player_dict.get('top_pace', 0):.1f})")
                
                if has_avg_pace and has_top_pace:
                    converted_bowlers_with_pace += 1
                    print(f"      ✅ Has pace attributes")
                else:
                    converted_bowlers_without_pace += 1
                    print(f"      ❌ Missing pace attributes - will use fallback")
                
                if converted_bowlers_with_pace + converted_bowlers_without_pace >= 5:
                    break
        
        print(f"\n4. Summary of converted players:")
        print(f"   Bowlers with pace attributes: {converted_bowlers_with_pace}")
        print(f"   Bowlers without pace attributes: {converted_bowlers_without_pace}")
        
        print(f"\n5. Testing speed calculation logic...")
        
        # Test the actual speed calculation for a few bowlers
        for player_dict in t20_sim.team1['players'][:3]:
            if player_dict['bowling'] >= 40:
                print(f"   Testing {player_dict['name']}:")
                
                # Check the condition that determines if pace attributes are used
                avg_pace = player_dict.get('avg_pace', 0)
                print(f"      avg_pace value: {avg_pace}")
                print(f"      Condition (avg_pace > 0): {avg_pace > 0}")
                
                if avg_pace > 0:
                    print(f"      ✅ Will use pace attributes")
                else:
                    print(f"      ❌ Will use fallback logic")
                
                # Calculate speed
                speed = t20_sim.calculate_ball_speed(player_dict)
                print(f"      Calculated speed: {speed:.1f} kph")
        
        root.destroy()
        
        print("\n" + "=" * 60)
        print("FALLBACK LOGIC - ANALYSIS")
        print("=" * 60)
        
        if bowlers_without_pace > 0 or converted_bowlers_without_pace > 0:
            print("❌ ISSUE FOUND:")
            print("   - Some bowlers are missing pace attributes")
            print("   - This causes fallback logic to be used")
            print("   - User wants NO fallback logic")
            
            print("\n🔧 SOLUTION:")
            print("   - Ensure ALL bowlers have pace attributes")
            print("   - Remove fallback logic completely")
            print("   - Force pace attributes for all bowlers")
        else:
            print("✅ NO ISSUE:")
            print("   - All bowlers have pace attributes")
            print("   - Fallback logic should not be used")
        
        return bowlers_without_pace + converted_bowlers_without_pace
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    debug_fallback_issue()
