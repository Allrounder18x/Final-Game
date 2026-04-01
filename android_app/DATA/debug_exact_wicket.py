"""
Debug the exact wicket counting logic step by step
"""

def debug_exact_wicket():
    """Debug exactly what happens with wicket counting"""
    
    print("=" * 60)
    print("DEBUGGING EXACT WICKET COUNTING")
    print("=" * 60)
    
    try:
        # Read the actual process_wicket function
        with open('t20oversimulation.py', 'r') as f:
            content = f.read()
        
        # Find the process_wicket function
        lines = content.split('\n')
        in_process_wicket = False
        process_wicket_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'def process_wicket(' in line:
                in_process_wicket = True
                process_wicket_lines.append(f"Line {i}: {line}")
            elif in_process_wicket and line.strip().startswith('def ') and 'process_wicket' not in line:
                break
            elif in_process_wicket:
                process_wicket_lines.append(f"Line {i}: {line}")
        
        print("1. Current process_wicket function:")
        for line in process_wicket_lines[:20]:  # First 20 lines
            print(f"   {line}")
        
        if len(process_wicket_lines) > 20:
            print(f"   ... ({len(process_wicket_lines) - 20} more lines)")
        
        # Look for any suspicious patterns
        print("\n2. Looking for suspicious patterns:")
        
        suspicious_patterns = [
            'wickets',
            'wicket',
            '-=',
            'Run Out',
            'run out',
            'dismissal_type'
        ]
        
        found_patterns = {}
        for pattern in suspicious_patterns:
            if pattern.lower() in content.lower():
                # Find lines containing this pattern
                matching_lines = []
                for i, line in enumerate(lines, 1):
                    if pattern.lower() in line.lower():
                        matching_lines.append(f"Line {i}: {line.strip()}")
                
                if matching_lines:
                    found_patterns[pattern] = matching_lines[:5]  # First 5 matches
        
        for pattern, matches in found_patterns.items():
            print(f"\n   Pattern '{pattern}' found in {len(matches)} places:")
            for match in matches:
                print(f"      {match}")
        
        # Check specifically for the run-out logic
        print("\n3. Checking run-out logic specifically:")
        
        runout_lines = []
        for i, line in enumerate(lines, 1):
            if 'run out' in line.lower() or 'Run Out' in line:
                runout_lines.append(f"Line {i}: {line.strip()}")
        
        print(f"   Found {len(runout_lines)} lines with 'run out':")
        for line in runout_lines[:10]:  # First 10 matches
            print(f"      {line}")
        
        if len(runout_lines) > 10:
            print(f"      ... ({len(runout_lines) - 10} more lines)")
        
        # Look for the exact issue
        print("\n4. Analyzing the potential issue:")
        
        # Check if there are any other places where wickets might be modified
        wicket_modifications = []
        for i, line in enumerate(lines, 1):
            if ('wickets' in line and ('=' in line or '-=' in line or '+=' in line)) or 'wickets' in line and ('-' in line):
                wicket_modifications.append(f"Line {i}: {line.strip()}")
        
        print(f"   Found {len(wicket_modifications)} lines that modify wickets:")
        for line in wicket_modifications:
            print(f"      {line}")
        
        print("\n" + "=" * 60)
        print("DEBUG ANALYSIS")
        print("=" * 60)
        
        # Check for the specific bug pattern
        bug_indicators = [
            "wickets'] -= 1",
            "wickets -= 1",
            "wickets'] -="
        ]
        
        bug_found = False
        for indicator in bug_indicators:
            if indicator in content:
                print(f"❌ BUG INDICATOR FOUND: '{indicator}'")
                bug_found = True
        
        if not bug_found:
            print("✅ No obvious bug indicators found")
        
        # Check for correct logic
        correct_indicators = [
            'if dismissal_type != "Run Out"',
            'dismissal_type != "Run Out"'
        ]
        
        correct_found = False
        for indicator in correct_indicators:
            if indicator in content:
                print(f"✅ CORRECT LOGIC FOUND: '{indicator}'")
                correct_found = True
        
        if not correct_found:
            print("⚠️ Correct run-out logic not found")
        
        print("\n📋 NEXT STEPS:")
        print("1. The bug might be in a different part of the code")
        print("2. Check if there are multiple places where wickets are counted")
        print("3. Look for any initialization or reset logic that might affect wickets")
        print("4. Check if the issue is in the display logic rather than the counting logic")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    debug_exact_wicket()
