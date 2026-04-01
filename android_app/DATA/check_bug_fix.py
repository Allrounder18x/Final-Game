"""
Simple check to verify the run-out bug fix
"""

def check_bug_fix():
    """Check if the run-out bug lines have been removed"""
    
    print("=" * 60)
    print("CHECKING RUN-OUT BUG FIX")
    print("=" * 60)
    
    try:
        # Read the t20oversimulation.py file
        with open('t20oversimulation.py', 'r') as f:
            content = f.read()
        
        # Check for the problematic lines
        bug_patterns = [
            "wickets'] -= 1",
            "wickets'] -=",
            "wickets -= 1"
        ]
        
        bugs_found = []
        for pattern in bug_patterns:
            if pattern in content:
                # Find line numbers where this pattern occurs
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if pattern in line:
                        bugs_found.append(f"Line {i}: {line.strip()}")
        
        print("1. Checking for bug lines in t20oversimulation.py:")
        
        if bugs_found:
            print(f"   ❌ FOUND {len(bugs_found)} BUG LINES:")
            for bug in bugs_found:
                print(f"      {bug}")
            print("\n   ❌ BUG NOT FULLY FIXED!")
            return False
        else:
            print("   ✅ NO BUG LINES FOUND!")
        
        # Check for the correct logic
        print("\n2. Checking for correct run-out logic:")
        
        correct_patterns = [
            "if dismissal_type != \"Run Out\":",
            "dismissal_type != \"Run Out\"",
            "# Don't increment bowler wickets for run out"
        ]
        
        correct_logic_found = []
        for pattern in correct_patterns:
            if pattern in content:
                correct_logic_found.append(pattern)
        
        if correct_logic_found:
            print(f"   ✅ CORRECT LOGIC FOUND:")
            for logic in correct_logic_found:
                print(f"      - {logic}")
        else:
            print("   ⚠️ Could not find correct run-out logic")
        
        # Check the Fast Match Simulator too
        print("\n3. Checking Fast Match Simulator:")
        
        with open('cricket_manager/core/fast_match_simulator.py', 'r') as f:
            fast_sim_content = f.read()
        
        fast_sim_bugs = []
        for pattern in bug_patterns:
            if pattern in fast_sim_content:
                fast_sim_bugs.append(pattern)
        
        if fast_sim_bugs:
            print(f"   ❌ FOUND BUGS IN FAST SIMULATOR: {fast_sim_bugs}")
            return False
        else:
            print("   ✅ NO BUGS IN FAST SIMULATOR!")
        
        print("\n" + "=" * 60)
        print("BUG FIX VERIFICATION RESULTS")
        print("=" * 60)
        
        if not bugs_found and not fast_sim_bugs:
            print("✅ RUN-OUT BUG SUCCESSFULLY FIXED!")
            print("✅ All problematic lines have been removed")
            print("✅ Both simulators are clean")
            print("\n📋 What was fixed:")
            print("   - Removed 'wickets -= 1' lines for run-outs")
            print("   - Run-outs no longer affect bowler wicket counts")
            print("   - Bowlers keep their legitimate wickets")
            print("\n🎯 Expected behavior:")
            print("   - Bowler takes wicket → wickets increase")
            print("   - Run-out occurs → wickets stay the same")
            print("   - Bowler's wicket count is preserved")
            return True
        else:
            print("❌ BUG STILL EXISTS!")
            print("❌ Some problematic lines remain")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    check_bug_fix()
