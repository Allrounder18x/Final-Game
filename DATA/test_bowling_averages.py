"""
Test script to verify bowling averages for different skill levels in Test matches
"""
import sys
import os

# Add the cricket_manager path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricket_manager'))

from cricket_manager.core.fast_match_simulator import FastMatchSimulator
from cricket_manager.core.player import Player
from cricket_manager.core.team import Team

def create_test_team(name, bowling_skills):
    """Create a test team with specified bowling skills"""
    team = Team(name=name, tier=1)
    
    roles = [
        'Opening Batter', 'Opening Batter', 'Middle Order Batter', 
        'Middle Order Batter', 'Wicketkeeper Batter',
        'Bowling Allrounder', 'Bowling Allrounder',
        'Fast Bowler', 'Fast Bowler', 'Finger Spinner', 'Fast Medium Pacer'
    ]
    
    for i, (bowl_skill, role) in enumerate(zip(bowling_skills, roles)):
        player = Player(f"Player_{name}_{i+1}", 25, role, name)
        # Batters have low bowling, bowlers have specified bowling skill
        if 'Bowler' in role or 'Allrounder' in role or 'Spinner' in role:
            player.bowling = bowl_skill
            player.batting = 30 if 'Allrounder' in role else 15
        else:
            player.batting = 70
            player.bowling = 10
        player.fielding = 60
        team.players.append(player)
    
    return team

def run_test_matches(num_matches=10):
    """Run test matches and analyze bowling averages by skill level"""
    
    # Create teams with varied bowling skills for bowlers (positions 6-11)
    # Positions 1-5 are batters with low bowling
    team1_skills = [10, 10, 10, 10, 10, 75, 70, 90, 85, 80, 65]  # Last 6 are bowlers
    team1 = create_test_team("TestTeam1", team1_skills)
    
    team2_skills = [10, 10, 10, 10, 10, 72, 68, 88, 82, 78, 62]  # Last 6 are bowlers
    team2 = create_test_team("TestTeam2", team2_skills)
    
    # Track cumulative stats
    player_stats = {}
    
    print(f"\n{'='*70}")
    print(f"TESTING BOWLING AVERAGES - {num_matches} TEST MATCHES")
    print(f"{'='*70}\n")
    
    for match_num in range(num_matches):
        print(f"Simulating Test Match {match_num + 1}...")
        
        simulator = FastMatchSimulator(
            team1=team1,
            team2=team2,
            match_format='Test'
        )
        
        result = simulator.simulate()
        
        # Collect stats from match
        for player_name, stats in simulator.match_stats.items():
            if player_name not in player_stats:
                # Find the player to get their bowling skill
                player_obj = None
                for p in team1.players:
                    if p.name == player_name:
                        player_obj = p
                        break
                if not player_obj:
                    for p in team2.players:
                        if p.name == player_name:
                            player_obj = p
                            break
                
                bowl_skill = player_obj.bowling if player_obj else 0
                role = player_obj.role if player_obj else ''
                
                player_stats[player_name] = {
                    'bowling_skill': bowl_skill,
                    'role': role,
                    'total_runs_conceded': 0,
                    'total_wickets': 0,
                    'total_balls': 0,
                    'matches': 0
                }
            
            bowling = stats.get('bowling', {})
            player_stats[player_name]['total_runs_conceded'] += bowling.get('runs', 0)
            player_stats[player_name]['total_wickets'] += bowling.get('wickets', 0)
            player_stats[player_name]['total_balls'] += bowling.get('balls', 0)
            player_stats[player_name]['matches'] += 1
    
    # Calculate and display BOWLING averages
    print(f"\n{'='*80}")
    print(f"BOWLING AVERAGES BY SKILL LEVEL (Only players who bowled)")
    print(f"{'='*80}")
    print(f"{'Player':<25} {'BowlSkill':>9} {'Wkts':>6} {'Runs':>8} {'Balls':>8} {'Avg':>8} {'Econ':>6}")
    print(f"{'-'*80}")
    
    # Sort by bowling skill (highest first), only show players who bowled
    bowlers = [(name, stats) for name, stats in player_stats.items() 
               if stats['total_balls'] > 0 and stats['bowling_skill'] > 20]
    sorted_bowlers = sorted(bowlers, key=lambda x: x[1]['bowling_skill'], reverse=True)
    
    skill_groups = {
        'Elite (80+)': {'runs': 0, 'wickets': 0, 'balls': 0, 'players': 0},
        'Good (60-79)': {'runs': 0, 'wickets': 0, 'balls': 0, 'players': 0},
        'Average (40-59)': {'runs': 0, 'wickets': 0, 'balls': 0, 'players': 0},
        'Weak (<40)': {'runs': 0, 'wickets': 0, 'balls': 0, 'players': 0}
    }
    
    for player_name, stats in sorted_bowlers:
        runs = stats['total_runs_conceded']
        wickets = stats['total_wickets']
        balls = stats['total_balls']
        skill = stats['bowling_skill']
        
        avg = runs / max(1, wickets)
        econ = (runs * 6) / max(1, balls)
        
        print(f"{player_name:<25} {skill:>9} {wickets:>6} {runs:>8} {balls:>8} {avg:>8.2f} {econ:>6.2f}")
        
        # Group by skill level
        if skill >= 80:
            group = 'Elite (80+)'
        elif skill >= 60:
            group = 'Good (60-79)'
        elif skill >= 40:
            group = 'Average (40-59)'
        else:
            group = 'Weak (<40)'
        
        skill_groups[group]['runs'] += runs
        skill_groups[group]['wickets'] += wickets
        skill_groups[group]['balls'] += balls
        skill_groups[group]['players'] += 1
    
    # Display group averages
    print(f"\n{'='*80}")
    print(f"BOWLING AVERAGES BY SKILL GROUP")
    print(f"{'='*80}")
    print(f"{'Group':<20} {'Players':>8} {'Wickets':>10} {'Runs':>10} {'Group Avg':>12} {'Econ':>8}")
    print(f"{'-'*80}")
    
    for group, data in skill_groups.items():
        if data['players'] > 0 and data['wickets'] > 0:
            group_avg = data['runs'] / max(1, data['wickets'])
            group_econ = (data['runs'] * 6) / max(1, data['balls'])
            print(f"{group:<20} {data['players']:>8} {data['wickets']:>10} {data['runs']:>10} {group_avg:>12.2f} {group_econ:>8.2f}")
    
    print(f"\n{'='*80}")
    print("TARGET: Elite ~22, Good ~30, Average ~40+")
    print("EXPECTED: Elite < Good < Average < Weak")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    num_matches = 10
    if len(sys.argv) > 1:
        try:
            num_matches = int(sys.argv[1])
        except:
            pass
    
    run_test_matches(num_matches)
