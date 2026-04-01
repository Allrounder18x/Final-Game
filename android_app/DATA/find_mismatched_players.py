"""
Find players with mismatched roles and pace attributes
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def find_mismatched_players():
    """Find players who have spinner roles but pace bowler speeds"""
    
    print("=" * 60)
    print("FINDING MISMATCHED PLAYERS")
    print("=" * 60)
    
    try:
        from cricket_manager.core.game_engine import GameEngine
        
        game_engine = GameEngine()
        
        print("\n1. Checking for players with mismatched roles and speeds...")
        
        mismatched_players = []
        
        for team in game_engine.all_teams:
            print(f"\n   Team: {team.name}")
            
            for player in team.players:
                role = player.role.lower()
                avg_pace = getattr(player, 'avg_pace', 0)
                top_pace = getattr(player, 'top_pace', 0)
                
                # Check for spinners with high speeds
                if 'spin' in role and avg_pace > 100:
                    print(f"      ❌ MISMATCHED: {player.name}")
                    print(f"         Role: {player.role}")
                    print(f"         Bowling: {player.bowling}")
                    print(f"         Avg Pace: {avg_pace:.1f} kph (should be 75-95)")
                    print(f"         Top Pace: {top_pace:.1f} kph (should be ≤95)")
                    mismatched_players.append(player)
                
                # Check for pace bowlers with low speeds
                elif ('fast' in role or 'medium' in role) and avg_pace > 0 and avg_pace < 110:
                    print(f"      ⚠️  SLOW PACE: {player.name}")
                    print(f"         Role: {player.role}")
                    print(f"         Bowling: {player.bowling}")
                    print(f"         Avg Pace: {avg_pace:.1f} kph (should be 130+)")
                    print(f"         Top Pace: {top_pace:.1f} kph (should be 130+)")
                
                # Check for batsmen with pace attributes
                elif player.bowling < 40 and avg_pace > 0:
                    print(f"      ⚠️  BATSMAN WITH PACE: {player.name}")
                    print(f"         Role: {player.role}")
                    print(f"         Bowling: {player.bowling}")
                    print(f"         Avg Pace: {avg_pace:.1f} kph (should be 0)")
                    print(f"         Top Pace: {top_pace:.1f} kph (should be 0)")
        
        print(f"\n2. Summary...")
        print(f"   Found {len(mismatched_players)} mismatched players")
        
        if mismatched_players:
            print(f"\n3. Fixing mismatched players...")
            
            for player in mismatched_players:
                print(f"   Fixing {player.name}...")
                
                # Reset pace attributes for spinners
                player.avg_pace = 0.0
                player.top_pace = 0.0
                player.speed_potential = 0.0
                
                # Recalculate proper spinner speeds
                from cricket_manager.systems.pace_speed_system import initialize_pace_speeds
                initialize_pace_speeds(player)
                
                print(f"      New Avg Pace: {player.avg_pace:.1f}")
                print(f"      New Top Pace: {player.top_pace:.1f}")
                
                if player.avg_pace <= 95:
                    print(f"      ✅ Fixed successfully")
                else:
                    print(f"      ❌ Still too high")
        
        print("\n" + "=" * 60)
        print("MISMATCHED PLAYERS - SUMMARY")
        print("=" * 60)
        
        if mismatched_players:
            print(f"✅ FIXED {len(mismatched_players)} PLAYERS:")
            for player in mismatched_players:
                print(f"   - {player.name}: {player.avg_pace:.1f} kph avg, {player.top_pace:.1f} kph top")
        else:
            print("✅ NO MISMATCHED PLAYERS FOUND")
        
        print("\n✅ EXPECTED BEHAVIOR:")
        print("   - Spinners: 75-95 kph")
        print("   - Pace bowlers: 130-162 kph")
        print("   - Batsmen: 0 kph (no pace attributes)")
        
        return len(mismatched_players)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    find_mismatched_players()
