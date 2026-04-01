"""
Debug the age-based pace calculation to find the issue
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_age_calculation():
    """Debug the age-based pace calculation"""
    
    print("=" * 60)
    print("DEBUGGING AGE-BASED PACE CALCULATION")
    print("=" * 60)
    
    try:
        from cricket_manager.systems.pace_speed_system import calculate_speed_potential
        
        print("\n1. Testing age 13 fast bowler step by step...")
        
        # Test age 13 fast bowler
        age = 13
        bowling_skill = 80
        role = "Fast Bowler"
        
        print(f"   Input: Age {age}, Bowling {bowling_skill}, Role {role}")
        
        # Manually calculate what should happen
        role_lower = role.lower()
        is_spinner = "spin" in role_lower or "spinner" in role_lower
        print(f"   Is spinner: {is_spinner}")
        
        # Age-based table
        max_speeds_by_age = {
            13: (90, 65), 14: (100, 75), 15: (113, 80), 16: (123, 87), 17: (129, 93),
            18: (135, 95), 19: (139, 97), 20: (141, 99), 27: (151, 102), 32: (138, 102),
            36: (128, 90), 40: (120, 85)
        }
        
        # Get age-based speeds
        if age <= 13:
            pace_max, spin_max = max_speeds_by_age[13]
            print(f"   Age <= 13: Using age 13 values")
        elif age >= 40:
            pace_max, spin_max = max_speeds_by_age[40]
            print(f"   Age >= 40: Using age 40 values")
        elif age in max_speeds_by_age:
            pace_max, spin_max = max_speeds_by_age[age]
            print(f"   Age in table: Using age {age} values")
        else:
            print(f"   Age not in table: Would interpolate")
        
        print(f"   Pace max: {pace_max}, Spin max: {spin_max}")
        
        # Use appropriate max
        if is_spinner:
            speed_potential = spin_max
            print(f"   Using spin max: {speed_potential}")
        else:
            speed_potential = pace_max
            print(f"   Using pace max: {speed_potential}")
        
        # Add skill bonus
        if bowling_skill > 80:
            skill_bonus = (bowling_skill - 80) * (0.1 if not is_spinner else 0.05)
            speed_potential += skill_bonus
            print(f"   Skill bonus: {skill_bonus}, New potential: {speed_potential}")
        else:
            print(f"   No skill bonus (bowling skill: {bowling_skill})")
        
        # Exceptional bonus
        if not is_spinner and bowling_skill > 85:
            import random
            if random.random() < 0.02:
                exceptional_bonus = random.uniform(2, 4)
                speed_potential += exceptional_bonus
                print(f"   Exceptional bonus: {exceptional_bonus}, New potential: {speed_potential}")
            else:
                print(f"   No exceptional bonus")
        else:
            print(f"   No exceptional bonus (spinner or low skill)")
        
        print(f"   Final speed potential: {speed_potential}")
        
        # Now call the actual function
        actual_result = calculate_speed_potential(age, bowling_skill, role)
        print(f"   Actual function result: {actual_result}")
        
        print(f"\n2. Testing multiple ages...")
        
        for test_age in [13, 14, 15, 16, 17, 18, 19, 20]:
            result = calculate_speed_potential(test_age, 80, "Fast Bowler")
            expected = max_speeds_by_age[test_age][0]  # Expected pace max
            print(f"   Age {test_age}: Expected {expected}, Got {result}, Diff {result - expected:+.1f}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_age_calculation()
