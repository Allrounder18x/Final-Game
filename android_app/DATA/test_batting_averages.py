"""
Test script to verify batting averages for different skill levels in Test matches
"""
import sys
import os

# Add the cricket_manager path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricket_manager'))

from cricket_manager.core.fast_match_simulator import FastMatchSimulator
from cricket_manager.core.player import Player
from cricket_manager.core.team import Team

def create_test_team(name, batting_skills):
    """Create a test team with specified batting skills"""
    team = Team(name=name, tier=1)
    
    roles = [
        'Opening Batter', 'Opening Batter', 'Middle Order Batter', 
        'Middle Order Batter', 'Middle Order Batter', 'Wicketkeeper Batter',
        'Bowling Allrounder', 'Fast Bowler', 'Fast Bowler', 
        'Finger Spinner', 'Fast Medium Pacer'
    ]
    
    for i, (bat_skill, role) in enumerate(zip(batting_skills, roles)):
        player = Player(f"Player_{name}_{i+1}", 25, role, name)
        player.batting = bat_skill
        player.bowling = 70 if 'Bowler' in role or 'Allrounder' in role else 20
        player.fielding = 60
        team.players.append(player)
    
    return team

def run_test_matches(num_matches=10):
    """Run test matches and analyze batting averages by skill level"""
    
    # Create teams with varied batting skills
    # Team 1: Mix of skills (90, 85, 80, 75, 70, 65, 55, 45, 35, 25, 20)
    team1_skills = [90, 85, 80, 75, 70, 65, 55, 45, 35, 25, 20]
    team1 = create_test_team("TestTeam1", team1_skills)
    
    # Team 2: Similar mix
    team2_skills = [88, 82, 78, 72, 68, 62, 52, 42, 32, 22, 18]
    team2 = create_test_team("TestTeam2", team2_skills)
    
    # Track cumulative stats
    player_stats = {}
    
    print(f"\n{'='*70}")
    print(f"TESTING BATTING AVERAGES - {num_matches} TEST MATCHES")
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
                # Find the player to get their batting skill
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
                
                bat_skill = player_obj.batting if player_obj else 0
                
                player_stats[player_name] = {
                    'batting_skill': bat_skill,
                    'total_runs': 0,
                    'total_dismissals': 0,
                    'total_balls': 0,
                    'matches': 0
                }
            
            batting = stats.get('batting', {})
            player_stats[player_name]['total_runs'] += batting.get('runs', 0)
            player_stats[player_name]['total_dismissals'] += batting.get('dismissals', 0)
            player_stats[player_name]['total_balls'] += batting.get('balls', 0)
            player_stats[player_name]['matches'] += 1
    
    # Calculate and display BATTING averages
    print(f"\n{'='*70}")
    print(f"BATTING AVERAGES BY SKILL LEVEL")
    print(f"{'='*70}")
    print(f"{'Player':<25} {'BatSkill':>8} {'Runs':>8} {'Dismissals':>10} {'Average':>10}")
    print(f"{'-'*70}")
    
    # Sort by batting skill (highest first)
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1]['batting_skill'], reverse=True)
    
    skill_groups = {
        'Elite (80+)': {'runs': 0, 'dismissals': 0, 'players': 0},
        'Good (60-79)': {'runs': 0, 'dismissals': 0, 'players': 0},
        'Average (40-59)': {'runs': 0, 'dismissals': 0, 'players': 0},
        'Weak (<40)': {'runs': 0, 'dismissals': 0, 'players': 0}
    }
    
    for player_name, stats in sorted_players:
        runs = stats['total_runs']
        dismissals = stats['total_dismissals']
        balls = stats['total_balls']
        skill = stats['batting_skill']
        
        avg = runs / max(1, dismissals)
        
        print(f"{player_name:<25} {skill:>6} {runs:>8} {dismissals:>10} {avg:>10.2f} {balls:>8}")
        
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
        skill_groups[group]['dismissals'] += dismissals
        skill_groups[group]['players'] += 1
    
    # Display group averages
    print(f"\n{'='*70}")
    print(f"AVERAGES BY SKILL GROUP")
    print(f"{'='*70}")
    print(f"{'Group':<20} {'Players':>8} {'Total Runs':>12} {'Dismissals':>12} {'Group Avg':>12}")
    print(f"{'-'*70}")
    
    for group, data in skill_groups.items():
        if data['players'] > 0:
            group_avg = data['runs'] / max(1, data['dismissals'])
            print(f"{group:<20} {data['players']:>8} {data['runs']:>12} {data['dismissals']:>12} {group_avg:>12.2f}")
    
    print(f"\n{'='*70}")
    print("EXPECTED: Elite > Good > Average > Weak")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    num_matches = 5  # Run 5 Test matches for quick test
    if len(sys.argv) > 1:
        try:
            num_matches = int(sys.argv[1])
        except:
            pass
    
    run_test_matches(num_matches)
