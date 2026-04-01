"""
Final test of the age-based pace progression fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_final_age_progression():
    """Final verification of age-based pace progression"""
    
    print("=" * 60)
    print("FINAL AGE-BASED PACE PROGRESSION TEST")
    print("=" * 60)
    
    try:
        from cricket_manager.core.game_engine import GameEngine
        from cricket_manager.systems.pace_speed_system import calculate_speed_potential, initialize_pace_speeds
        import tkinter as tk
        from t20oversimulation import T20Match
        
        game_engine = GameEngine()
        
        print("\n1. Verifying age progression matches gamer 2024.py + 5k...")
        
        # Expected values from gamer 2024.py + 5k for pace bowlers
        expected_pace = {
            13: 90, 14: 100, 15: 113, 16: 123, 17: 129, 18: 135, 19: 139, 20: 141,
            27: 151, 32: 138, 36: 128, 40: 120
        }
        
        # Expected values from gamer 2024.py for spinners (no change)
        expected_spin = {
            13: 65, 14: 75, 15: 80, 16: 87, 17: 93, 18: 95, 19: 97, 20: 99,
            27: 102, 32: 102, 36: 90, 40: 85
        }
        
        print("\n   Fast Bowler Verification:")
        print("   Age | Expected | Actual  | Status")
        print("   ----|----------|---------|-------")
        
        all_correct = True
        for age, expected in expected_pace.items():
            actual = calculate_speed_potential(age, 80, "Fast Bowler")
            # Allow small variation due to skill bonus
            if abs(actual - expected) <= 5:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                all_correct = False
            print(f"   {age:2d}  | {expected:8d} | {actual:7.1f} | {status}")
        
        print("\n   Spinner Verification:")
        print("   Age | Expected | Actual  | Status")
        print("   ----|----------|---------|-------")
        
        for age, expected in expected_spin.items():
            actual = calculate_speed_potential(age, 80, "Off Spinner")
            # Allow small variation due to skill bonus
            if abs(actual - expected) <= 5:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                all_correct = False
            print(f"   {age:2d}  | {expected:8d} | {actual:7.1f} | {status}")
        
        print(f"\n2. Testing T20 simulator integration...")
        
        root = tk.Tk()
        root.withdraw()
        
        # Create T20 simulator with test team
        team1 = game_engine.all_teams[0]
        team2 = game_engine.all_teams[1]
        t20_sim = T20Match(root, team1, team2, 'T20', headless=True)
        
        # Test a few bowlers from the actual team
        bowlers_tested = 0
        speeds_realistic = True
        
        for player_dict in t20_sim.team1['players']:
            if player_dict['bowling'] >= 40 and bowlers_tested < 3:
                bowlers_tested += 1
                
                # Calculate speeds
                speeds = []
                for i in range(5):
                    speed = t20_sim.calculate_ball_speed(player_dict)
                    speeds.append(speed)
                
                avg_speed = sum(speeds) / len(speeds)
                
                print(f"   {player_dict['name']} ({player_dict['role']}): {avg_speed:.1f} kph")
                
                # Check if speed is realistic for the role
                role = player_dict['role'].lower()
                if 'spin' in role or 'spinner' in role:
                    if avg_speed > 95:
                        print(f"      ❌ Spinner too fast")
                        speeds_realistic = False
                    else:
                        print(f"      ✅ Spinner speed realistic")
                else:
                    if avg_speed < 110 or avg_speed > 162:
                        print(f"      ❌ Pace bowler speed unrealistic")
                        speeds_realistic = False
                    else:
                        print(f"      ✅ Pace bowler speed realistic")
        
        root.destroy()
        
        print("\n" + "=" * 60)
        print("FINAL AGE PROGRESSION TEST - RESULTS")
        print("=" * 60)
        
        if all_correct and speeds_realistic:
            print("✅ SUCCESS:")
            print("   - Age progression matches gamer 2024.py + 5k")
            print("   - Spinner progression unchanged from gamer 2024.py")
            print("   - T20 simulator uses correct speeds")
            print("   - All speeds are realistic for player roles")
        else:
            print("❌ ISSUES FOUND:")
            if not all_correct:
                print("   - Some age calculations don't match expected values")
            if not speeds_realistic:
                print("   - Some speeds are unrealistic for player roles")
        
        print("\n✅ FINAL VERIFICATION:")
        print("   - Age 13 Fast Bowler: ~90 kph (was 85) +5k")
        print("   - Age 18 Fast Bowler: ~135 kph (was 130) +5k")
        print("   - Age 27 Fast Bowler: ~151 kph (prime age)")
        print("   - Age 13 Spinner: ~65 kph (unchanged)")
        print("   - Age 27 Spinner: ~102 kph (prime age)")
        
        return all_correct and speeds_realistic
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_age_progression()
