"""
World Cup System - Manages 9 World Cup tournaments across all formats
"""

import random
from cricket_manager.core.match_simulator import MatchSimulator


def _qualified_u21_parent_teams(teams, match_format, max_teams):
    """National teams with at least 11 U21 players; prefer Tier 1 by format points."""
    nationals = [t for t in teams if not getattr(t, "is_domestic", False)]
    tier1 = [t for t in nationals if t.format_tiers.get(match_format) == 1]
    tier1.sort(key=lambda t: t.format_stats[match_format]["points"], reverse=True)
    out = []
    for t in tier1:
        if len(getattr(t, "u21_squad", None) or []) >= 11:
            out.append(t)
        if len(out) >= max_teams:
            return out[:max_teams]
    rest = [t for t in nationals if t not in out and t.format_tiers.get(match_format) in (2, 3, 4)]
    rest.sort(key=lambda t: t.format_stats[match_format]["points"], reverse=True)
    for t in rest:
        if len(getattr(t, "u21_squad", None) or []) >= 11:
            out.append(t)
        if len(out) >= max_teams:
            break
    return out[:max_teams]


class WorldCupSystem:
    """Manage all World Cup tournaments across formats"""
    
    def __init__(self):
        # World Cups run every 2 years
        self.world_cup_frequency = 2
        
        # Tournament configurations
        self.tournaments = {
            'T20': {
                'main': {'name': 'T20 World Cup', 'teams': 12, 'groups': 2},
                'u21': {'name': 'T20 U21 World Cup', 'teams': 12, 'groups': 2},
                'associate': {'name': 'T20 Associate World Cup', 'teams': 32, 'groups': 8}
            },
            'ODI': {
                'main': {'name': 'ODI World Cup', 'teams': 12, 'groups': 2},
                'u21': {'name': 'ODI U21 World Cup', 'teams': 12, 'groups': 2},
                'associate': {'name': 'ODI Associate World Cup', 'teams': 32, 'groups': 8}
            },
            'Test': {
                'main': {'name': 'Test Championship', 'teams': 8, 'groups': 0},  # Knockout only
                'u21': {'name': 'Test U21 Championship', 'teams': 8, 'groups': 0},
                'associate': {'name': 'Test Associate Championship', 'teams': 16, 'groups': 4}
            }
        }
    
    def should_run_world_cups(self, current_year):
        """Check if World Cups should run this year"""
        return current_year % self.world_cup_frequency == 0
    
    def run_all_world_cups(self, teams, current_year):
        """
        Run all 9 World Cup tournaments
        
        Args:
            teams: List of all teams
            current_year: Current game year
            
        Returns:
            Dictionary with results for all tournaments
        """
        print("\n" + "="*60)
        print(f"WORLD CUP YEAR {current_year}")
        print("="*60)
        
        results = {
            'T20': {},
            'ODI': {},
            'Test': {}
        }
        
        # T20 World Cups
        print("\n[T20] Running T20 World Cups...")
        results['T20']['main'] = self.run_t20_world_cup(teams)
        results['T20']['u21'] = self.run_t20_u21_world_cup(teams)
        results['T20']['associate'] = self.run_t20_associate_world_cup(teams)
        
        # ODI World Cups
        print("\n[ODI] Running ODI World Cups...")
        results['ODI']['main'] = self.run_odi_world_cup(teams)
        results['ODI']['u21'] = self.run_odi_u21_world_cup(teams)
        results['ODI']['associate'] = self.run_odi_associate_world_cup(teams)
        
        # Test Championships
        print("\n[Test] Running Test Championships...")
        results['Test']['main'] = self.run_test_championship(teams)
        results['Test']['u21'] = self.run_test_u21_championship(teams)
        results['Test']['associate'] = self.run_test_associate_championship(teams)
        
        print("\n" + "="*60)
        print("ALL WORLD CUPS COMPLETE")
        print("="*60)
        
        return results
    
    def run_t20_world_cup(self, teams):
        """Run main T20 World Cup (12 teams from Tier 1)"""
        tier1_teams = [t for t in teams if t.format_tiers.get('T20') == 1]
        tier1_teams.sort(key=lambda t: t.format_stats['T20']['points'], reverse=True)
        qualified_teams = tier1_teams[:12]
        
        tournament = WorldCupTournament(
            name="T20 World Cup",
            teams=qualified_teams,
            match_format='T20',
            tournament_type='main',
            num_groups=2
        )
        
        return tournament.run_tournament()
    
    def run_t20_u21_world_cup(self, teams):
        """Run T20 U21 World Cup (12 U21 teams)"""
        qualified_teams = _qualified_u21_parent_teams(teams, "T20", 12)
        if not qualified_teams:
            print("[WorldCup] T20 U21 World Cup: no nations with 11+ U21 players.")
            return None
        
        tournament = WorldCupTournament(
            name="T20 U21 World Cup",
            teams=qualified_teams,
            match_format='T20',
            tournament_type='u21',
            num_groups=2
        )
        
        return tournament.run_tournament()
    
    def run_t20_associate_world_cup(self, teams):
        """Run T20 Associate World Cup (32 teams from Tiers 2-4)"""
        associate_teams = [t for t in teams if t.format_tiers.get('T20') in [2, 3, 4]]
        associate_teams.sort(key=lambda t: t.format_stats['T20']['points'], reverse=True)
        qualified_teams = associate_teams[:32]
        
        tournament = WorldCupTournament(
            name="T20 Associate World Cup",
            teams=qualified_teams,
            match_format='T20',
            tournament_type='associate',
            num_groups=8
        )
        
        return tournament.run_tournament()
    
    def run_odi_world_cup(self, teams):
        """Run main ODI World Cup (12 teams from Tier 1)"""
        tier1_teams = [t for t in teams if t.format_tiers.get('ODI') == 1]
        tier1_teams.sort(key=lambda t: t.format_stats['ODI']['points'], reverse=True)
        qualified_teams = tier1_teams[:12]
        
        tournament = WorldCupTournament(
            name="ODI World Cup",
            teams=qualified_teams,
            match_format='ODI',
            tournament_type='main',
            num_groups=2
        )
        
        return tournament.run_tournament()
    
    def run_odi_u21_world_cup(self, teams):
        """Run ODI U21 World Cup"""
        qualified_teams = _qualified_u21_parent_teams(teams, "ODI", 12)
        if not qualified_teams:
            print("[WorldCup] ODI U21 World Cup: no nations with 11+ U21 players.")
            return None
        
        tournament = WorldCupTournament(
            name="ODI U21 World Cup",
            teams=qualified_teams,
            match_format='ODI',
            tournament_type='u21',
            num_groups=2
        )
        
        return tournament.run_tournament()
    
    def run_odi_associate_world_cup(self, teams):
        """Run ODI Associate World Cup"""
        associate_teams = [t for t in teams if t.format_tiers.get('ODI') in [2, 3, 4]]
        associate_teams.sort(key=lambda t: t.format_stats['ODI']['points'], reverse=True)
        qualified_teams = associate_teams[:32]
        
        tournament = WorldCupTournament(
            name="ODI Associate World Cup",
            teams=qualified_teams,
            match_format='ODI',
            tournament_type='associate',
            num_groups=8
        )
        
        return tournament.run_tournament()
    
    def run_test_championship(self, teams):
        """Run Test Championship (8 teams, knockout only)"""
        tier1_teams = [t for t in teams if t.format_tiers.get('Test') == 1]
        tier1_teams.sort(key=lambda t: t.format_stats['Test']['points'], reverse=True)
        qualified_teams = tier1_teams[:8]
        
        tournament = WorldCupTournament(
            name="Test Championship",
            teams=qualified_teams,
            match_format='Test',
            tournament_type='main',
            num_groups=0  # Direct knockout
        )
        
        return tournament.run_tournament()
    
    def run_test_u21_championship(self, teams):
        """Run Test U21 Championship"""
        qualified_teams = _qualified_u21_parent_teams(teams, "Test", 8)
        if not qualified_teams:
            print("[WorldCup] Test U21 Championship: no nations with 11+ U21 players.")
            return None
        
        tournament = WorldCupTournament(
            name="Test U21 Championship",
            teams=qualified_teams,
            match_format='Test',
            tournament_type='u21',
            num_groups=0
        )
        
        return tournament.run_tournament()
    
    def run_test_associate_championship(self, teams):
        """Run Test Associate Championship"""
        associate_teams = [t for t in teams if t.format_tiers.get('Test') in [2, 3, 4]]
        associate_teams.sort(key=lambda t: t.format_stats['Test']['points'], reverse=True)
        qualified_teams = associate_teams[:16]
        
        tournament = WorldCupTournament(
            name="Test Associate Championship",
            teams=qualified_teams,
            match_format='Test',
            tournament_type='associate',
            num_groups=4
        )
        
        return tournament.run_tournament()



class WorldCupTournament:
    """Represents a single World Cup tournament"""
    
    def __init__(self, name, teams, match_format, tournament_type, num_groups):
        self.name = name
        self.teams = teams
        self.match_format = match_format
        self.tournament_type = tournament_type
        self.num_groups = num_groups
        
        self.groups = {}
        self.knockout_teams = []
        self.winner = None
        self.runner_up = None
        self.top_scorer = None
        self.top_wicket_taker = None
        
        # Match results
        self.group_results = []
        self.knockout_results = []
    
    def _u21_xi_team(self, parent):
        import copy
        from cricket_manager.core.team import Team
        t = Team(name=f"{parent.name} U21", tier=5)
        sq = getattr(parent, "u21_squad", None) or []
        if len(sq) >= 11:
            t.players = copy.deepcopy(sq[:11])
        elif sq:
            t.players = copy.deepcopy(sq)
        else:
            t.players = []
        t.wc_parent_team = parent
        return t
    
    def _pair_for_sim(self, parent1, parent2):
        if self.tournament_type != "u21":
            return parent1, parent2
        return self._u21_xi_team(parent1), self._u21_xi_team(parent2)
    
    def _winner_parent(self, winner_side, s1, s2, parent1, parent2):
        if winner_side is None:
            return parent1
        wp = getattr(winner_side, "wc_parent_team", None)
        if wp is not None:
            return wp
        return parent1 if winner_side is s1 or getattr(winner_side, "name", None) == s1.name else parent2
    
    def run_tournament(self):
        """Run complete tournament"""
        print(f"\n{'='*60}")
        print(f"{self.name}")
        print(f"{'='*60}")
        
        if self.num_groups > 0:
            # Group stage
            self.create_groups()
            self.run_group_stage()
        else:
            # Direct knockout (Test Championship)
            self.knockout_teams = self.teams
        
        # Knockout stage
        self.run_knockout_stage()
        
        # Find top performers
        self.find_top_performers()
        
        print(f"\n🏆 WINNER: {self.winner.name}")
        print(f"🥈 RUNNER-UP: {self.runner_up.name}")
        
        return {
            'winner': self.winner,
            'runner_up': self.runner_up,
            'top_scorer': self.top_scorer,
            'top_wicket_taker': self.top_wicket_taker,
            'groups': self.groups,
            'group_results': self.group_results,
            'knockout_results': self.knockout_results
        }
    
    def create_groups(self):
        """Create groups for tournament"""
        shuffled_teams = self.teams.copy()
        random.shuffle(shuffled_teams)
        
        teams_per_group = len(shuffled_teams) // self.num_groups
        group_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        for i in range(self.num_groups):
            group_name = group_names[i]
            start_idx = i * teams_per_group
            end_idx = start_idx + teams_per_group
            
            self.groups[group_name] = {
                'teams': shuffled_teams[start_idx:end_idx],
                'standings': []
            }
            
            # Initialize group points
            for team in self.groups[group_name]['teams']:
                team.wc_points = 0
                team.wc_nrr = 0.0
        
        print(f"Created {self.num_groups} groups with {teams_per_group} teams each")
    
    def run_group_stage(self):
        """Run group stage matches"""
        print("\n[Group Stage] Starting...")
        
        for group_name, group_data in self.groups.items():
            teams = group_data['teams']
            print(f"\nGroup {group_name}:")
            
            # Round-robin within group
            for i, team1 in enumerate(teams):
                for j, team2 in enumerate(teams):
                    if i < j:
                        # Simulate match (U21 tournaments use youth XIs)
                        s1, s2 = self._pair_for_sim(team1, team2)
                        match = MatchSimulator(s1, s2, self.match_format, headless=True)
                        winner_side = match.simulate()
                        winner = self._winner_parent(winner_side, s1, s2, team1, team2)
                        
                        # Update points
                        if winner == team1:
                            team1.wc_points += 2
                        elif winner == team2:
                            team2.wc_points += 2
                        else:
                            team1.wc_points += 1
                            team2.wc_points += 1
                        
                        # Store result
                        self.group_results.append({
                            'group': group_name,
                            'team1': team1.name,
                            'team2': team2.name,
                            'winner': winner.name if winner else 'Tie'
                        })
            
            # Get standings
            standings = sorted(teams, key=lambda t: t.wc_points, reverse=True)
            group_data['standings'] = standings
            
            # Top 2 qualify for knockout
            self.knockout_teams.extend(standings[:2])
            
            print(f"  Qualified: {standings[0].name}, {standings[1].name}")
        
        print(f"\n[Group Stage] Complete. {len(self.knockout_teams)} teams qualified")
    
    def run_knockout_stage(self):
        """Run knockout stage"""
        print("\n[Knockout Stage] Starting...")
        
        num_teams = len(self.knockout_teams)
        
        if num_teams == 8:
            # Quarter-finals
            qf_winners = self.run_knockout_round(self.knockout_teams, "Quarter-Final")
            # Semi-finals
            sf_winners = self.run_knockout_round(qf_winners, "Semi-Final")
            # Final
            self.run_final(sf_winners)
        
        elif num_teams == 4:
            # Semi-finals only
            sf_winners = self.run_knockout_round(self.knockout_teams, "Semi-Final")
            # Final
            self.run_final(sf_winners)
        
        elif num_teams == 16:
            # Round of 16
            r16_winners = self.run_knockout_round(self.knockout_teams, "Round of 16")
            # Quarter-finals
            qf_winners = self.run_knockout_round(r16_winners, "Quarter-Final")
            # Semi-finals
            sf_winners = self.run_knockout_round(qf_winners, "Semi-Final")
            # Final
            self.run_final(sf_winners)
    
    def run_knockout_round(self, teams, round_name):
        """Run a knockout round"""
        print(f"\n[{round_name}]")
        winners = []
        
        # Pair teams
        for i in range(0, len(teams), 2):
            team1 = teams[i]
            team2 = teams[i + 1]
            
            s1, s2 = self._pair_for_sim(team1, team2)
            match = MatchSimulator(s1, s2, self.match_format, headless=True)
            winner_side = match.simulate()
            winner = self._winner_parent(winner_side, s1, s2, team1, team2)
            winners.append(winner)
            
            # Store result
            self.knockout_results.append({
                'round': round_name,
                'team1': team1.name,
                'team2': team2.name,
                'winner': winner.name
            })
            
            print(f"  {team1.name} vs {team2.name} -> {winner.name} wins")
        
        return winners
    
    def run_final(self, finalists):
        """Run the final"""
        print(f"\n[FINAL]")
        
        team1 = finalists[0]
        team2 = finalists[1]
        
        s1, s2 = self._pair_for_sim(team1, team2)
        match = MatchSimulator(s1, s2, self.match_format, headless=True)
        winner_side = match.simulate()
        self.winner = self._winner_parent(winner_side, s1, s2, team1, team2)
        self.runner_up = team2 if self.winner == team1 else team1
        
        # Store result
        self.knockout_results.append({
            'round': 'Final',
            'team1': team1.name,
            'team2': team2.name,
            'winner': self.winner.name
        })
        
        print(f"  {team1.name} vs {team2.name}")
        print(f"  🏆 CHAMPION: {self.winner.name}")
    
    def find_top_performers(self):
        """Find top run scorer and wicket taker"""
        # Collect all players from participating teams
        all_players = []
        for team in self.teams:
            if self.tournament_type == "u21":
                all_players.extend(getattr(team, "u21_squad", None) or [])
            else:
                all_players.extend(team.players)
        
        # Find top scorer (most runs in this format)
        if all_players:
            self.top_scorer = max(
                all_players,
                key=lambda p: p.stats.get(self.match_format, {}).get('runs', 0)
            )
            
            # Find top wicket taker
            self.top_wicket_taker = max(
                all_players,
                key=lambda p: p.stats.get(self.match_format, {}).get('wickets', 0)
            )
