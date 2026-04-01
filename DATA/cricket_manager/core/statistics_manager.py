"""
Statistics Manager - Universal statistics tracking for all match types and formats
Handles stats updates from Manual Play, Quick Sim, and Season Sim
"""


def _maybe_clear_intl_rank_flag(player, teams, count_as_senior_international):
    """Clear post–associate-return flag when the player earns a senior international cap for their nationality."""
    if not count_as_senior_international or not getattr(player, "clear_intl_rank_until_next_match", False):
        return
    nat = (getattr(player, "nationality", None) or "").strip()
    if not nat or not teams:
        return
    names = {getattr(t, "name", "") for t in teams if t}
    if nat in names:
        player.clear_intl_rank_until_next_match = False


class StatisticsManager:
    """Centralized statistics management for all match types and formats"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def _team_for_player_in_match(player, teams):
        for team in teams or []:
            for p in getattr(team, "players", []) or []:
                if p is player:
                    return team
            if hasattr(team, "u21_squad"):
                for p in team.u21_squad or []:
                    if p is player:
                        return team
        return None
    
    @staticmethod
    def _is_associate_national_team(team):
        if not team or getattr(team, "is_domestic", False):
            return False
        return getattr(team, "format_tiers", {}).get("Test", 1) != 1
    
    def update_player_stats_from_match(self, match, match_format, teams, current_year=None):
        """
        Universal statistics update function
        Called by ALL match simulation methods (Manual, Quick Sim, Season Sim)
        
        Args:
            match: Match object with match_stats dictionary
            match_format: 'T20', 'ODI', or 'Test'
            teams: List of teams in the match (usually [team1, team2])
            current_year: Current game year for yearly_stats tracking
        """
        
        print(f"[Stats] Updating player statistics from {match_format} match")
        
        # Prevent duplicate updates
        if hasattr(match, 'stats_updated') and match.stats_updated:
            print("[Stats] Statistics already updated for this match, skipping")
            return
        
        # Try to get current_year from match's parent_app if not provided
        if current_year is None:
            if hasattr(match, 'parent_app') and hasattr(match.parent_app, 'current_year'):
                current_year = match.parent_app.current_year
        
        # Split: domestic club | U21 youth international (… U21 vs … U21) | senior international.
        count_as_domestic = False
        try:
            count_as_domestic = any(getattr(t, 'is_domestic', False) for t in (teams or []))
        except Exception:
            count_as_domestic = False
        is_u21_intl = (not count_as_domestic) and any(
            (getattr(t, 'name', '') or '').endswith(' U21') for t in (teams or [])
        )
        count_as_senior_international = (not count_as_domestic) and (not is_u21_intl)
        
        # Extract match statistics
        match_stats = match.match_stats  # Dictionary of player stats
        
        for player_name, stats in match_stats.items():
            # Find player in teams
            player = self.find_player_in_teams(player_name, teams)
            
            if not player:
                print(f"[Stats] Warning: Player {player_name} not found in teams")
                continue
            
            # Extract batting and bowling stats
            batting_stats = stats.get('batting', {})
            bowling_stats = stats.get('bowling', {})
            
            ge = getattr(match, 'parent_app', None)
            u21_only = False
            if is_u21_intl and ge is not None:
                fn = getattr(ge, 'player_in_u21_only_pipeline', None)
                if callable(fn):
                    u21_only = bool(fn(player))
            
            player_team = self._team_for_player_in_match(player, teams)
            count_full_intl = False
            count_assoc_intl = False
            if count_as_senior_international:
                if player_team is None:
                    count_full_intl = True
                elif self._is_associate_national_team(player_team):
                    count_assoc_intl = True
                else:
                    count_full_intl = True
            
            # Update format-specific career statistics (domestic total always; senior intl / U21 intl optional)
            player.update_stats_from_match(
                match_format,
                batting_stats,
                bowling_stats,
                count_as_international=count_full_intl,
                count_as_u21_international=is_u21_intl,
                u21_only_pipeline=u21_only,
                count_as_associate_international=count_assoc_intl,
            )
            if count_as_senior_international:
                _maybe_clear_intl_rank_flag(player, teams, count_as_senior_international)
            
            if u21_only:
                if current_year is not None and hasattr(player, 'u21_international_yearly_stats'):
                    if current_year not in player.u21_international_yearly_stats:
                        player.u21_international_yearly_stats[current_year] = {}
                    if match_format not in player.u21_international_yearly_stats[current_year]:
                        player.u21_international_yearly_stats[current_year][match_format] = {
                            'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                            'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                            'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                        }
                    runs = batting_stats.get('runs', 0)
                    balls_faced = batting_stats.get('balls', 0)
                    wickets = bowling_stats.get('wickets', 0)
                    balls_bowled = bowling_stats.get('balls', 0)
                    runs_conceded = bowling_stats.get('runs', 0)
                    uys = player.u21_international_yearly_stats[current_year][match_format]
                    uys['runs'] += runs
                    uys['balls_faced'] += balls_faced
                    uys['wickets'] += wickets
                    uys['balls_bowled'] += balls_bowled
                    uys['runs_conceded'] += runs_conceded
                    uys['matches'] += 1
                    extra_d = batting_stats.get('dismissals', 0) or 0
                    if match_format == 'Test' and extra_d:
                        uys['dismissals'] = uys.get('dismissals', 0) + int(extra_d)
                    if runs > uys['highest_score']:
                        uys['highest_score'] = runs
                    if runs >= 100:
                        uys['centuries'] += 1
                    elif runs >= 50:
                        uys['fifties'] += 1
                    if wickets >= 5:
                        uys['five_wickets'] += 1
                print(f"[Stats] Updated {player_name} (U21-only): {batting_stats.get('runs', 0)} runs, {bowling_stats.get('wickets', 0)} wickets")
                continue
            
            # Update season statistics - all fields
            runs = batting_stats.get('runs', 0)
            balls_faced = batting_stats.get('balls', 0)
            wickets = bowling_stats.get('wickets', 0)
            balls_bowled = bowling_stats.get('balls', 0)
            runs_conceded = bowling_stats.get('runs', 0)
            
            season_stats = player.season_stats[match_format]
            season_stats['runs'] += runs
            season_stats['balls_faced'] += balls_faced
            season_stats['wickets'] += wickets
            season_stats['balls_bowled'] += balls_bowled
            season_stats['runs_conceded'] += runs_conceded
            season_stats['matches'] += 1
            
            # Update highest score for season
            if runs > season_stats.get('highest_score', 0):
                season_stats['highest_score'] = runs
            
            # Update centuries and fifties for season
            if runs >= 100:
                season_stats['centuries'] = season_stats.get('centuries', 0) + 1
            elif runs >= 50:
                season_stats['fifties'] = season_stats.get('fifties', 0) + 1
            
            # Update five wickets for season
            if wickets >= 5:
                season_stats['five_wickets'] = season_stats.get('five_wickets', 0) + 1
            
            # Update yearly_stats keyed by year (like gamer 2024.py season_stats)
            if current_year is not None and hasattr(player, 'yearly_stats'):
                if current_year not in player.yearly_stats:
                    player.yearly_stats[current_year] = {}
                if match_format not in player.yearly_stats[current_year]:
                    player.yearly_stats[current_year][match_format] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0
                    }
                ys = player.yearly_stats[current_year][match_format]
                ys['runs'] += runs
                ys['balls_faced'] += balls_faced
                ys['wickets'] += wickets
                ys['balls_bowled'] += balls_bowled
                ys['runs_conceded'] += runs_conceded
                ys['matches'] += 1
                if runs > ys['highest_score']:
                    ys['highest_score'] = runs
                if runs >= 100:
                    ys['centuries'] += 1
                elif runs >= 50:
                    ys['fifties'] += 1
                if wickets >= 5:
                    ys['five_wickets'] += 1
            
            # Update international_yearly_stats (full-member senior international only)
            if count_full_intl and current_year is not None and hasattr(player, 'international_yearly_stats'):
                if current_year not in player.international_yearly_stats:
                    player.international_yearly_stats[current_year] = {}
                if match_format not in player.international_yearly_stats[current_year]:
                    player.international_yearly_stats[current_year][match_format] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                iys = player.international_yearly_stats[current_year][match_format]
                iys['runs'] += runs
                iys['balls_faced'] += balls_faced
                iys['wickets'] += wickets
                iys['balls_bowled'] += balls_bowled
                iys['runs_conceded'] += runs_conceded
                iys['matches'] += 1
                extra_d = batting_stats.get('dismissals', 0) or 0
                if match_format == 'Test' and extra_d:
                    iys['dismissals'] = iys.get('dismissals', 0) + int(extra_d)
                if runs > iys['highest_score']:
                    iys['highest_score'] = runs
                if runs >= 100:
                    iys['centuries'] += 1
                elif runs >= 50:
                    iys['fifties'] += 1
                if wickets >= 5:
                    iys['five_wickets'] += 1
            if count_assoc_intl and current_year is not None and hasattr(player, 'associate_international_yearly_stats'):
                if current_year not in player.associate_international_yearly_stats:
                    player.associate_international_yearly_stats[current_year] = {}
                if match_format not in player.associate_international_yearly_stats[current_year]:
                    player.associate_international_yearly_stats[current_year][match_format] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                ays = player.associate_international_yearly_stats[current_year][match_format]
                ays['runs'] += runs
                ays['balls_faced'] += balls_faced
                ays['wickets'] += wickets
                ays['balls_bowled'] += balls_bowled
                ays['runs_conceded'] += runs_conceded
                ays['matches'] += 1
                extra_d = batting_stats.get('dismissals', 0) or 0
                if match_format == 'Test' and extra_d:
                    ays['dismissals'] = ays.get('dismissals', 0) + int(extra_d)
                if runs > ays['highest_score']:
                    ays['highest_score'] = runs
                if runs >= 100:
                    ays['centuries'] += 1
                elif runs >= 50:
                    ays['fifties'] += 1
                if wickets >= 5:
                    ays['five_wickets'] += 1
            
            # U21 youth international yearly (not senior caps)
            if is_u21_intl and current_year is not None and hasattr(player, 'u21_international_yearly_stats'):
                if current_year not in player.u21_international_yearly_stats:
                    player.u21_international_yearly_stats[current_year] = {}
                if match_format not in player.u21_international_yearly_stats[current_year]:
                    player.u21_international_yearly_stats[current_year][match_format] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                uys = player.u21_international_yearly_stats[current_year][match_format]
                uys['runs'] += runs
                uys['balls_faced'] += balls_faced
                uys['wickets'] += wickets
                uys['balls_bowled'] += balls_bowled
                uys['runs_conceded'] += runs_conceded
                uys['matches'] += 1
                extra_d = batting_stats.get('dismissals', 0) or 0
                if match_format == 'Test' and extra_d:
                    uys['dismissals'] = uys.get('dismissals', 0) + int(extra_d)
                if runs > uys['highest_score']:
                    uys['highest_score'] = runs
                if runs >= 100:
                    uys['centuries'] += 1
                elif runs >= 50:
                    uys['fifties'] += 1
                if wickets >= 5:
                    uys['five_wickets'] += 1
            
            if count_as_domestic and current_year is not None and hasattr(player, 'domestic_yearly_stats'):
                if current_year not in player.domestic_yearly_stats:
                    player.domestic_yearly_stats[current_year] = {}
                if match_format not in player.domestic_yearly_stats[current_year]:
                    player.domestic_yearly_stats[current_year][match_format] = {
                        'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0,
                        'balls_bowled': 0, 'runs_conceded': 0, 'centuries': 0,
                        'fifties': 0, 'five_wickets': 0, 'highest_score': 0, 'dismissals': 0
                    }
                dys = player.domestic_yearly_stats[current_year][match_format]
                dys['runs'] += runs
                dys['balls_faced'] += balls_faced
                dys['wickets'] += wickets
                dys['balls_bowled'] += balls_bowled
                dys['runs_conceded'] += runs_conceded
                dys['matches'] += 1
                extra_d = batting_stats.get('dismissals', 0) or 0
                if match_format == 'Test' and extra_d:
                    dys['dismissals'] = dys.get('dismissals', 0) + int(extra_d)
                if runs > dys['highest_score']:
                    dys['highest_score'] = runs
                if runs >= 100:
                    dys['centuries'] += 1
                elif runs >= 50:
                    dys['fifties'] += 1
                if wickets >= 5:
                    dys['five_wickets'] += 1
            
            print(f"[Stats] Updated {player_name}: {runs} runs, {wickets} wickets")
        
        # Mark match as stats updated
        match.stats_updated = True
        
        print(f"[Stats] Statistics update complete for {match_format} match")
    
    def find_player_in_teams(self, player_name, teams):
        """Find player by name in team list"""
        
        for team in teams:
            # Check main squad
            for player in team.players:
                if player.name == player_name:
                    return player
            
            # Check U21 squad
            if hasattr(team, 'u21_squad'):
                for player in team.u21_squad:
                    if player.name == player_name:
                        return player
        
        return None
    
    def get_top_batsmen(self, teams, match_format, limit=100):
        """Get top batsmen for specific format"""
        
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        # Filter players with minimum matches
        qualified = [p for p in all_players if p.stats[match_format]['matches'] >= 5]
        
        # Sort by runs
        qualified.sort(key=lambda p: p.stats[match_format]['runs'], reverse=True)
        
        return qualified[:limit]
    
    def get_top_bowlers(self, teams, match_format, limit=100):
        """Get top bowlers for specific format"""
        
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        # Filter players with minimum matches
        qualified = [p for p in all_players if p.stats[match_format]['matches'] >= 5]
        
        # Sort by wickets
        qualified.sort(key=lambda p: p.stats[match_format]['wickets'], reverse=True)
        
        return qualified[:limit]
    
    def get_rankings(self, teams, match_format, category='batting', limit=2000):
        """
        Get player rankings for specific format and category
        
        Args:
            teams: List of all teams
            match_format: 'T20', 'ODI', or 'Test'
            category: 'batting', 'bowling', or 'allrounder'
            limit: Maximum number of players to return (default 2000)
        """
        
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        # Filter by minimum matches
        qualified = [p for p in all_players if p.stats[match_format]['matches'] >= 5]
        
        if category == 'batting':
            # Sort by runs, then average
            qualified.sort(
                key=lambda p: (p.stats[match_format]['runs'], p.stats[match_format]['batting_average']),
                reverse=True
            )
        
        elif category == 'bowling':
            # Sort by wickets, then average (lower is better)
            qualified.sort(
                key=lambda p: (p.stats[match_format]['wickets'], -p.stats[match_format]['bowling_average']),
                reverse=True
            )
        
        elif category == 'allrounder':
            # Combined score: runs + (wickets * 20)
            from cricket_manager.utils.helpers import is_allrounder
            qualified = [p for p in qualified if is_allrounder(p.role)]
            qualified.sort(
                key=lambda p: p.stats[match_format]['runs'] + (p.stats[match_format]['wickets'] * 20),
                reverse=True
            )
        
        return qualified[:limit]
    
    def get_format_leaders(self, teams, match_format):
        """
        Get format leaders (top scorer, top wicket-taker, etc.)
        
        Args:
            teams: List of all teams
            match_format: 'T20', 'ODI', or 'Test'
        
        Returns:
            Dictionary with leaders
        """
        
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        # Filter players with minimum matches
        qualified = [p for p in all_players if p.stats[match_format]['matches'] >= 5]
        
        if not qualified:
            return None
        
        leaders = {}
        
        # Top scorer
        top_scorer = max(qualified, key=lambda p: p.stats[match_format]['runs'])
        leaders['top_scorer'] = {
            'player': top_scorer,
            'runs': top_scorer.stats[match_format]['runs'],
            'average': top_scorer.stats[match_format]['batting_average']
        }
        
        # Top wicket-taker
        top_bowler = max(qualified, key=lambda p: p.stats[match_format]['wickets'])
        leaders['top_bowler'] = {
            'player': top_bowler,
            'wickets': top_bowler.stats[match_format]['wickets'],
            'average': top_bowler.stats[match_format]['bowling_average']
        }
        
        # Best batting average (min 10 matches)
        avg_qualified = [p for p in qualified if p.stats[match_format]['matches'] >= 10]
        if avg_qualified:
            best_avg = max(avg_qualified, key=lambda p: p.stats[match_format]['batting_average'])
            leaders['best_batting_average'] = {
                'player': best_avg,
                'average': best_avg.stats[match_format]['batting_average'],
                'runs': best_avg.stats[match_format]['runs']
            }
        
        # Best bowling average (min 10 wickets)
        bowl_qualified = [p for p in qualified if p.stats[match_format]['wickets'] >= 10]
        if bowl_qualified:
            best_bowl_avg = min(bowl_qualified, key=lambda p: p.stats[match_format]['bowling_average'])
            leaders['best_bowling_average'] = {
                'player': best_bowl_avg,
                'average': best_bowl_avg.stats[match_format]['bowling_average'],
                'wickets': best_bowl_avg.stats[match_format]['wickets']
            }
        
        # Most centuries
        most_centuries = max(qualified, key=lambda p: p.stats[match_format]['centuries'])
        if most_centuries.stats[match_format]['centuries'] > 0:
            leaders['most_centuries'] = {
                'player': most_centuries,
                'centuries': most_centuries.stats[match_format]['centuries']
            }
        
        # Most five-wicket hauls
        most_fifers = max(qualified, key=lambda p: p.stats[match_format]['five_wickets'])
        if most_fifers.stats[match_format]['five_wickets'] > 0:
            leaders['most_five_wickets'] = {
                'player': most_fifers,
                'five_wickets': most_fifers.stats[match_format]['five_wickets']
            }
        
        return leaders
    
    def get_team_statistics(self, team, match_format):
        """
        Get comprehensive team statistics for a format
        
        Args:
            team: Team object
            match_format: 'T20', 'ODI', or 'Test'
        
        Returns:
            Dictionary with team stats
        """
        
        stats = team.format_stats[match_format]
        
        # Calculate win percentage
        if stats['matches_played'] > 0:
            win_percentage = (stats['wins'] / stats['matches_played']) * 100
        else:
            win_percentage = 0.0
        
        # Get top performers
        if team.players:
            top_scorer = max(team.players, key=lambda p: p.stats[match_format]['runs'])
            top_bowler = max(team.players, key=lambda p: p.stats[match_format]['wickets'])
        else:
            top_scorer = None
            top_bowler = None
        
        return {
            'matches_played': stats['matches_played'],
            'wins': stats['wins'],
            'losses': stats['losses'],
            'draws': stats['draws'],
            'points': stats['points'],
            'nrr': stats['nrr'],
            'win_percentage': round(win_percentage, 2),
            'tier': team.format_tiers[match_format],
            'top_scorer': top_scorer,
            'top_bowler': top_bowler
        }
    
    def reset_season_stats(self, teams, match_format):
        """
        Reset season statistics for all teams and players
        
        Args:
            teams: List of all teams
            match_format: 'T20', 'ODI', or 'Test'
        """
        
        for team in teams:
            # Reset team season stats
            team.reset_season_stats(match_format)
            
            # Reset player season stats with all fields
            for player in team.players:
                player.season_stats[match_format] = {
                    'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0, 'balls_bowled': 0,
                    'runs_conceded': 0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0
                }
        
        print(f"[Stats] Season statistics reset for {match_format}")
    
    def get_player_comparison(self, player1, player2, match_format):
        """
        Compare two players in a specific format
        
        Args:
            player1: First player
            player2: Second player
            match_format: 'T20', 'ODI', or 'Test'
        
        Returns:
            Dictionary with comparison data
        """
        
        p1_stats = player1.stats[match_format]
        p2_stats = player2.stats[match_format]
        
        comparison = {
            'player1': {
                'name': player1.name,
                'matches': p1_stats['matches'],
                'runs': p1_stats['runs'],
                'batting_avg': p1_stats['batting_average'],
                'strike_rate': p1_stats['strike_rate'],
                'wickets': p1_stats['wickets'],
                'bowling_avg': p1_stats['bowling_average'],
                'economy': p1_stats['economy_rate']
            },
            'player2': {
                'name': player2.name,
                'matches': p2_stats['matches'],
                'runs': p2_stats['runs'],
                'batting_avg': p2_stats['batting_average'],
                'strike_rate': p2_stats['strike_rate'],
                'wickets': p2_stats['wickets'],
                'bowling_avg': p2_stats['bowling_average'],
                'economy': p2_stats['economy_rate']
            }
        }
        
        return comparison
