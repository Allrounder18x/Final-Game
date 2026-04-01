"""
Combined test script for batting and bowling averages
Tests 3 categories of batters vs 3 categories of bowlers in Test matches
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricket_manager'))

from cricket_manager.core.fast_match_simulator import FastMatchSimulator
from cricket_manager.core.player import Player
from cricket_manager.core.team import Team

def create_test_team(name, is_team1=True):
    """Create a test team with 3 categories of batters and 3 categories of bowlers"""
    team = Team(name=name, tier=1)
    
    if is_team1:
        # Team 1: Elite batters (85-90), Good batters (65-75), Avg batters (45-55)
        #         Elite bowlers (85-90), Good bowlers (65-75), Avg bowlers (45-55)
        players_config = [
            # Elite Batters (3)
            ('Elite_Bat_1', 'Opening Batter', 90, 15),
            ('Elite_Bat_2', 'Opening Batter', 85, 15),
            ('Elite_Bat_3', 'Middle Order Batter', 82, 15),
            # Good Batters (3)
            ('Good_Bat_1', 'Middle Order Batter', 72, 15),
            ('Good_Bat_2', 'Middle Order Batter', 68, 15),
            ('Good_Bat_3', 'Wicketkeeper Batter', 65, 15),
            # Average Batters (2) - also bowl as allrounders
            ('Avg_Bat_AR_1', 'Bowling Allrounder', 52, 55),
            ('Avg_Bat_AR_2', 'Bowling Allrounder', 48, 52),
            # Elite Bowlers (2)
            ('Elite_Bowl_1', 'Fast Bowler', 20, 88),
            ('Elite_Bowl_2', 'Fast Bowler', 18, 85),
            # Good Bowler (1)
            ('Good_Bowl_1', 'Finger Spinner', 15, 70),
        ]
    else:
        # Team 2: Similar structure with slight variations
        players_config = [
            ('Elite_Bat_A', 'Opening Batter', 88, 15),
            ('Elite_Bat_B', 'Opening Batter', 84, 15),
            ('Elite_Bat_C', 'Middle Order Batter', 80, 15),
            ('Good_Bat_A', 'Middle Order Batter', 70, 15),
            ('Good_Bat_B', 'Middle Order Batter', 66, 15),
            ('Good_Bat_C', 'Wicketkeeper Batter', 62, 15),
            ('Avg_Bat_AR_A', 'Bowling Allrounder', 50, 52),
            ('Avg_Bat_AR_B', 'Bowling Allrounder', 45, 48),
            ('Elite_Bowl_A', 'Fast Bowler', 18, 86),
            ('Elite_Bowl_B', 'Fast Bowler', 16, 82),
            ('Good_Bowl_A', 'Finger Spinner', 14, 68),
        ]
    
    for pname, role, bat, bowl in players_config:
        player = Player(f"{pname}_{name}", 25, role, name)
        player.batting = bat
        player.bowling = bowl
        player.fielding = 60
        team.players.append(player)
    
    return team

def categorize_batting(skill):
    if skill >= 80: return 'Elite (80+)'
    elif skill >= 60: return 'Good (60-79)'
    elif skill >= 40: return 'Average (40-59)'
    else: return 'Weak (<40)'

def categorize_bowling(skill):
    if skill >= 80: return 'Elite (80+)'
    elif skill >= 60: return 'Good (60-79)'
    elif skill >= 40: return 'Average (40-59)'
    else: return 'Weak (<40)'

def run_test_matches(num_matches=10):
    team1 = create_test_team("Team1", is_team1=True)
    team2 = create_test_team("Team2", is_team1=False)
    
    # Track stats
    batting_stats = {}  # by batting skill category
    bowling_stats = {}  # by bowling skill category
    
    print(f"\n{'='*80}")
    print(f"COMBINED BATTING & BOWLING AVERAGES TEST - {num_matches} TEST MATCHES")
    print(f"{'='*80}\n")
    
    for match_num in range(num_matches):
        print(f"Simulating Test Match {match_num + 1}...")
        
        simulator = FastMatchSimulator(team1=team1, team2=team2, match_format='Test')
        result = simulator.simulate()
        
        # Collect stats
        for player_name, stats in simulator.match_stats.items():
            # Find player
            player_obj = None
            for p in team1.players + team2.players:
                if p.name == player_name:
                    player_obj = p
                    break
            
            if not player_obj:
                continue
            
            bat_skill = player_obj.batting
            bowl_skill = player_obj.bowling
            bat_cat = categorize_batting(bat_skill)
            bowl_cat = categorize_bowling(bowl_skill)
            
            # Batting stats
            if bat_cat not in batting_stats:
                batting_stats[bat_cat] = {'runs': 0, 'dismissals': 0, 'balls': 0, 'players': set()}
            batting = stats.get('batting', {})
            batting_stats[bat_cat]['runs'] += batting.get('runs', 0)
            batting_stats[bat_cat]['dismissals'] += batting.get('dismissals', 0)
            batting_stats[bat_cat]['balls'] += batting.get('balls', 0)
            batting_stats[bat_cat]['players'].add(player_name)
            
            # Bowling stats (only for players who bowl)
            bowling = stats.get('bowling', {})
            if bowling.get('balls', 0) > 0:
                if bowl_cat not in bowling_stats:
                    bowling_stats[bowl_cat] = {'runs': 0, 'wickets': 0, 'balls': 0, 'players': set()}
                bowling_stats[bowl_cat]['runs'] += bowling.get('runs', 0)
                bowling_stats[bowl_cat]['wickets'] += bowling.get('wickets', 0)
                bowling_stats[bowl_cat]['balls'] += bowling.get('balls', 0)
                bowling_stats[bowl_cat]['players'].add(player_name)
    
    # Display BATTING results
    print(f"\n{'='*80}")
    print(f"BATTING AVERAGES BY SKILL CATEGORY")
    print(f"{'='*80}")
    print(f"{'Category':<20} {'Players':>8} {'Runs':>10} {'Dismissals':>12} {'Average':>10}")
    print(f"{'-'*60}")
    
    bat_order = ['Elite (80+)', 'Good (60-79)', 'Average (40-59)', 'Weak (<40)']
    for cat in bat_order:
        if cat in batting_stats:
            data = batting_stats[cat]
            avg = data['runs'] / max(1, data['dismissals'])
            print(f"{cat:<20} {len(data['players']):>8} {data['runs']:>10} {data['dismissals']:>12} {avg:>10.2f}")
    
    print(f"\nTARGET: Elite ~50, Good ~40, Average ~25")
    
    # Display BOWLING results
    print(f"\n{'='*80}")
    print(f"BOWLING AVERAGES BY SKILL CATEGORY")
    print(f"{'='*80}")
    print(f"{'Category':<20} {'Players':>8} {'Wickets':>10} {'Runs':>10} {'Average':>10} {'Econ':>8}")
    print(f"{'-'*70}")
    
    bowl_order = ['Elite (80+)', 'Good (60-79)', 'Average (40-59)', 'Weak (<40)']
    for cat in bowl_order:
        if cat in bowling_stats:
            data = bowling_stats[cat]
            avg = data['runs'] / max(1, data['wickets'])
            econ = (data['runs'] * 6) / max(1, data['balls'])
            print(f"{cat:<20} {len(data['players']):>8} {data['wickets']:>10} {data['runs']:>10} {avg:>10.2f} {econ:>8.2f}")
    
    print(f"\nTARGET: Elite ~22, Good ~30, Average ~40+")
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    num_matches = 15
    if len(sys.argv) > 1:
        try:
            num_matches = int(sys.argv[1])
        except:
            pass
    
    run_test_matches(num_matches)
