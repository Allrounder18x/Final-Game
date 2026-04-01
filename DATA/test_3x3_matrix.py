"""
3x3 Matrix Test: 9 combinations of batter skill vs bowler skill
- Elite Batter vs Elite Bowler
- Elite Batter vs Good Bowler
- Elite Batter vs Avg Bowler
- Good Batter vs Elite Bowler
- Good Batter vs Good Bowler
- Good Batter vs Avg Bowler
- Avg Batter vs Elite Bowler
- Avg Batter vs Good Bowler
- Avg Batter vs Avg Bowler
"""
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricket_manager'))

from cricket_manager.core.fast_match_simulator import FastMatchSimulator

def simulate_balls(batting_skill, bowling_skill, num_balls=10000):
    """Simulate many balls between a batter and bowler skill level"""
    
    # Create mock player objects
    class MockPlayer:
        def __init__(self, role='Fast Bowler', traits=None):
            self.role = role
            self.traits = traits or []
    
    # Borrow the probability calculation from FastMatchSimulator
    from cricket_manager.core.fast_match_simulator import FastMatchSimulator
    real_sim = FastMatchSimulator.__new__(FastMatchSimulator)
    real_sim.match_format = 'Test'
    real_sim.current_bowler = MockPlayer('Fast Bowler')
    real_sim.striker = MockPlayer('Opening Batter')
    real_sim.ball_age = 30  # Mid-age ball
    real_sim.weather = 'Sunny'
    real_sim.current_day = 2
    real_sim.pitch_pace = 6
    real_sim.pitch_spin = 5
    real_sim.pitch_bounce = 6
    real_sim.simulation_adjustments = {}
    real_sim.total_overs = 50
    real_sim.total_wickets = 3
    real_sim.target = None
    real_sim.total_runs = 150
    real_sim.settings = {'max_overs': 90}
    
    total_runs = 0
    total_wickets = 0
    total_balls = 0
    
    for _ in range(num_balls):
        probs = real_sim._calculate_ball_probabilities(batting_skill, bowling_skill, is_test=True, innings_num=2)
        
        outcomes = list(probs.keys())
        weights = [probs[o] for o in outcomes]
        outcome = random.choices(outcomes, weights=weights, k=1)[0]
        
        if outcome == 'wicket':
            total_wickets += 1
        elif outcome == 'single':
            total_runs += 1
        elif outcome == 'double':
            total_runs += 2
        elif outcome == 'triple':
            total_runs += 3
        elif outcome == 'four':
            total_runs += 4
        elif outcome == 'six':
            total_runs += 6
        
        total_balls += 1
    
    batting_avg = total_runs / max(1, total_wickets)
    bowling_avg = total_runs / max(1, total_wickets)  # Same calculation
    strike_rate = (total_runs / total_balls) * 100
    
    return {
        'runs': total_runs,
        'wickets': total_wickets,
        'balls': total_balls,
        'batting_avg': batting_avg,
        'bowling_avg': bowling_avg,
        'strike_rate': strike_rate
    }

def run_3x3_test(num_balls=10000):
    """Run 3x3 matrix test"""
    
    # Define skill levels
    batter_categories = [
        ('Elite (85)', 85),
        ('Good (70)', 70),
        ('Average (50)', 50)
    ]
    
    bowler_categories = [
        ('Elite (85)', 85),
        ('Good (70)', 70),
        ('Average (50)', 50)
    ]
    
    print(f"\n{'='*90}")
    print(f"3x3 MATRIX TEST: BATTING & BOWLING AVERAGES ({num_balls} balls per combination)")
    print(f"{'='*90}\n")
    
    # Results matrix
    results = {}
    
    for bat_name, bat_skill in batter_categories:
        results[bat_name] = {}
        for bowl_name, bowl_skill in bowler_categories:
            result = simulate_balls(bat_skill, bowl_skill, num_balls)
            results[bat_name][bowl_name] = result
    
    # Display BATTING AVERAGE matrix
    print(f"BATTING AVERAGES (Runs per Dismissal)")
    print(f"Target: Elite ~50, Good ~40, Average ~25")
    print(f"{'-'*70}")
    print("{:<20}".format("Batter \\ Bowler"), end='')
    for bowl_name, _ in bowler_categories:
        print(f"{bowl_name:>16}", end='')
    print()
    print(f"{'-'*70}")
    
    for bat_name, _ in batter_categories:
        print(f"{bat_name:<20}", end='')
        for bowl_name, _ in bowler_categories:
            avg = results[bat_name][bowl_name]['batting_avg']
            print(f"{avg:>16.2f}", end='')
        print()
    
    # Display BOWLING AVERAGE matrix (same numbers, different perspective)
    print(f"\n{'='*70}")
    print(f"BOWLING AVERAGES (Runs Conceded per Wicket)")
    print(f"Target: Elite ~22, Good ~30, Average ~40+")
    print(f"{'-'*70}")
    print("{:<20}".format("Bowler \\ Batter"), end='')
    for bat_name, _ in batter_categories:
        print(f"{bat_name:>16}", end='')
    print()
    print(f"{'-'*70}")
    
    for bowl_name, _ in bowler_categories:
        print(f"{bowl_name:<20}", end='')
        for bat_name, _ in batter_categories:
            avg = results[bat_name][bowl_name]['bowling_avg']
            print(f"{avg:>16.2f}", end='')
        print()
    
    # Display Strike Rates
    print(f"\n{'='*70}")
    print(f"STRIKE RATES (Runs per 100 balls)")
    print(f"{'-'*70}")
    print("{:<20}".format("Batter \\ Bowler"), end='')
    for bowl_name, _ in bowler_categories:
        print(f"{bowl_name:>16}", end='')
    print()
    print(f"{'-'*70}")
    
    for bat_name, _ in batter_categories:
        print(f"{bat_name:<20}", end='')
        for bowl_name, _ in bowler_categories:
            sr = results[bat_name][bowl_name]['strike_rate']
            print(f"{sr:>16.2f}", end='')
        print()
    
    print(f"\n{'='*90}\n")

if __name__ == "__main__":
    num_balls = 10000
    if len(sys.argv) > 1:
        try:
            num_balls = int(sys.argv[1])
        except:
            pass
    
    run_3x3_test(num_balls)
