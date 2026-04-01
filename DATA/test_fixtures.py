"""Quick test for the new series-based fixture generation"""
from cricket_manager.core.team import Team
from cricket_manager.systems.tier_system import generate_season_series, get_pitch_conditions
from collections import Counter

# Create mock teams for tier 1
teams = []
names = ['India', 'Australia', 'England', 'Pakistan', 'South Africa', 'New Zealand',
         'West Indies', 'Sri Lanka', 'Bangladesh', 'Afghanistan', 'Ireland', 'Zimbabwe']
for n in names:
    t = Team(name=n, tier=1)
    teams.append(t)

# Create mock teams for tier 2
t2_names = ['Scotland', 'Netherlands', 'UAE', 'Oman', 'Nepal', 'PNG',
            'Namibia', 'USA', 'Canada', 'Kenya', 'Hong Kong', 'Singapore']
t2_teams = []
for n in t2_names:
    t = Team(name=n, tier=2)
    t2_teams.append(t)

all_tier_teams = {1: teams, 2: t2_teams}
fixtures, history = generate_season_series(all_tier_teams, wc_month=5, current_season=1)

print("=" * 60)
print("FIXTURE GENERATION TEST")
print("=" * 60)

print(f"\nT20: {len(fixtures['T20'])} matches")
print(f"ODI: {len(fixtures['ODI'])} matches")
print(f"Test: {len(fixtures['Test'])} matches")
print(f"Total: {sum(len(v) for v in fixtures.values())} matches")

# Check match caps per team
print("\n--- Match Caps ---")
for fmt in ['T20', 'ODI', 'Test']:
    counts = Counter()
    for f in fixtures[fmt]:
        counts[f['home']] += 1
        counts[f['away']] += 1
    if counts:
        max_team = max(counts, key=counts.get)
        print(f"  {fmt} max per team: {counts[max_team]} ({max_team})")

# Check tier isolation (no cross-tier matches)
print("\n--- Tier Isolation Check ---")
cross_tier = 0
for fmt in fixtures:
    for f in fixtures[fmt]:
        t1 = f.get('team1')
        t2 = f.get('team2')
        if t1 and t2:
            t1_tier = None
            t2_tier = None
            for tier, tlist in all_tier_teams.items():
                if t1 in tlist: t1_tier = tier
                if t2 in tlist: t2_tier = tier
            if t1_tier and t2_tier and t1_tier != t2_tier:
                cross_tier += 1
print(f"  Cross-tier matches: {cross_tier} (should be 0)")
assert cross_tier == 0, "FAIL: Cross-tier matches found!"

# Check Tri/Quad-Nations
print("\n--- Tri/Quad-Nations Check ---")
tri_count = 0
quad_count = 0
for fmt in fixtures:
    for f in fixtures[fmt]:
        mt = f.get('match_type', '')
        if mt == 'tri_nations':
            tri_count += 1
        elif mt == 'quad_nations':
            quad_count += 1
print(f"  Tri-Nations matches: {tri_count}")
print(f"  Quad-Nations matches: {quad_count}")
assert tri_count + quad_count > 0, "FAIL: No multi-team tournaments generated!"

# Check pitch conditions
print("\n--- Pitch Conditions Check ---")
sub_count = 0
sena_count = 0
for fmt in fixtures:
    for f in fixtures[fmt]:
        region = f.get('pitch_region', '')
        if region == 'subcontinent':
            sub_count += 1
            assert 2 <= f['pitch_bounce'] <= 5, f"FAIL: Subcontinent bounce {f['pitch_bounce']}"
            assert 6 <= f['pitch_spin'] <= 9, f"FAIL: Subcontinent spin {f['pitch_spin']}"
            assert 2 <= f['pitch_pace'] <= 6, f"FAIL: Subcontinent pace {f['pitch_pace']}"
        elif region == 'sena':
            sena_count += 1
            assert 6 <= f['pitch_bounce'] <= 10, f"FAIL: SENA bounce {f['pitch_bounce']}"
            assert 2 <= f['pitch_spin'] <= 6, f"FAIL: SENA spin {f['pitch_spin']}"
            assert 6 <= f['pitch_pace'] <= 10, f"FAIL: SENA pace {f['pitch_pace']}"
print(f"  Subcontinent-hosted matches: {sub_count}")
print(f"  SENA-hosted matches: {sena_count}")
assert sub_count > 0 and sena_count > 0, "FAIL: Missing pitch regions!"

# Check WC month exclusion
print("\n--- WC Month Check ---")
months_used = set()
for fmt in fixtures:
    for f in fixtures[fmt]:
        months_used.add(f.get('month', -1))
print(f"  Months used: {sorted(months_used)}")
print(f"  WC month (5/June) excluded: {5 not in months_used}")
assert 5 not in months_used, "FAIL: WC month has bilateral matches!"

# Show sample series
print("\n--- Sample Series ---")
shown = set()
for fmt in ['T20', 'ODI', 'Test']:
    for f in fixtures[fmt]:
        sname = f.get('series_name', '')
        if sname and sname not in shown and len(shown) < 8:
            shown.add(sname)
            mnum = f.get('match_number', '?')
            total = f.get('total_matches', '?')
            month = f.get('month_name', '?')
            region = f.get('pitch_region', '?')
            print(f"  {sname} | Match {mnum}/{total} | {month} | pitch: {region}")

# Test pitch condition function directly
print("\n--- Pitch Function Test ---")
pc = get_pitch_conditions('India')
assert pc['region'] == 'subcontinent'
pc = get_pitch_conditions('Australia')
assert pc['region'] == 'sena'
pc = get_pitch_conditions('UnknownCountry')
assert pc['region'] == 'neutral'
print("  get_pitch_conditions: OK")

# Test imports
print("\n--- Import Checks ---")
from cricket_manager.core.fast_match_simulator import FastMatchSimulator
print("  FastMatchSimulator: OK")
from cricket_manager.ui.fixtures_view import FixturesScreen
print("  FixturesScreen: OK")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
