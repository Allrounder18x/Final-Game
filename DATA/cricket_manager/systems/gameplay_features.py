"""
Gameplay features: injuries, morale, H2H, records, POTM, season awards, difficulty.
Called from game_engine after matches and season end.
"""
import random


def _h2h_key(team1_name, team2_name):
    return tuple(sorted([team1_name, team2_name]))


def update_head_to_head(game_engine, team1_name, team2_name, result):
    """Update head-to-head after a match. result: 'win' for team1, 'loss' for team1, 'draw'."""
    key = _h2h_key(team1_name, team2_name)
    if key not in game_engine.head_to_head:
        game_engine.head_to_head[key] = {'wins_1': 0, 'wins_2': 0, 'draws': 0, 'last_5': []}
    h = game_engine.head_to_head[key]
    t1, t2 = key[0], key[1]
    if team1_name == t1 and team2_name == t2:
        first_won = result == 'win'
        second_won = result == 'loss'
    else:
        first_won = result == 'loss'
        second_won = result == 'win'
    if result == 'draw':
        h['draws'] += 1
        h['last_5'].append('D')
    elif first_won:
        h['wins_1'] += 1
        h['last_5'].append('1')
    else:
        h['wins_2'] += 1
        h['last_5'].append('2')
    h['last_5'] = h['last_5'][-5:]


def get_head_to_head(game_engine, team1_name, team2_name):
    """Return {wins_1, wins_2, draws, last_5} for team1 vs team2 (order by key)."""
    key = _h2h_key(team1_name, team2_name)
    if key not in game_engine.head_to_head:
        return {'wins_1': 0, 'wins_2': 0, 'draws': 0, 'last_5': []}
    h = game_engine.head_to_head[key].copy()
    if team1_name != key[0]:
        h['wins_1'], h['wins_2'] = h['wins_2'], h['wins_1']
        h['last_5'] = ['2' if x == '1' else ('1' if x == '2' else 'D') for x in h['last_5']]
    return h


def roll_injuries_after_match(team, match_format, difficulty='Normal'):
    """Roll for injury for each player who played. difficulty: Hard = more injuries."""
    injury_chance = 0.02  # 2% per player per match
    if difficulty == 'Hard':
        injury_chance = 0.035
    elif difficulty == 'Easy':
        injury_chance = 0.01
    for player in team.players:
        if getattr(player, 'is_injured', False):
            player.injury_duration = max(0, getattr(player, 'injury_duration', 0) - 1)
            if player.injury_duration <= 0:
                player.is_injured = False
            continue
        if random.random() < injury_chance:
            player.is_injured = True
            player.injury_duration = random.randint(1, 3)  # 1-3 matches out


def update_morale_after_match(team, result, is_home=True, opposition_name=None):
    """Update team and player morale. result: 'win'|'loss'|'draw'."""
    delta = {'win': 5, 'loss': -4, 'draw': 0}
    team.morale = max(0, min(100, team.morale + delta.get(result, 0)))
    if not is_home and result == 'win':
        team.morale = min(100, team.morale + 2)
    for player in team.players:
        if not hasattr(player, 'morale'):
            player.morale = 50
        player.morale = max(0, min(100, player.morale + delta.get(result, 0) + random.randint(-1, 1)))


def update_last_5(player, runs_batted=None, wickets_bowled=None):
    """Append to last_5_batting / last_5_bowling (keep max 5)."""
    if not hasattr(player, 'last_5_batting'):
        player.last_5_batting = []
    if not hasattr(player, 'last_5_bowling'):
        player.last_5_bowling = []
    if runs_batted is not None:
        player.last_5_batting = (player.last_5_batting + [runs_batted])[-5:]
    if wickets_bowled is not None:
        player.last_5_bowling = (player.last_5_bowling + [wickets_bowled])[-5:]


def calculate_potm(scorecard, team1_name, team2_name):
    """Return player name of Player of the Match from match_stats. Simple: runs + wickets*25."""
    match_stats = scorecard.get('match_stats', {})
    best_name, best_score = None, -1
    for name, data in match_stats.items():
        bat = data.get('batting', {})
        bowl = data.get('bowling', {})
        runs = bat.get('runs', 0)
        wickets = bowl.get('wickets', 0)
        score = runs + wickets * 25
        if score > best_score:
            best_score = score
            best_name = name
    return best_name


def update_team_records(game_engine, team, opposition_name, total_runs, wickets_lost, format_type, result, margin_runs=None, margin_wickets=None):
    """Update team.team_records if new record set. Optionally add record notifications to news."""
    if not hasattr(team, 'team_records') or team.team_records is None:
        return
    rec = team.team_records
    season = getattr(game_engine, 'current_season', 1)
    # Highest total
    if total_runs is not None:
        if rec.get('highest_total') is None or total_runs > rec['highest_total'].get('runs', 0):
            rec['highest_total'] = {'runs': total_runs, 'vs': opposition_name, 'format': format_type, 'season': season}
            if hasattr(game_engine, 'news_system') and game_engine.news_system:
                game_engine.news_system.add_record_news(team.name, 'highest_total', f"{total_runs} vs {opposition_name}")
    # Lowest total (all out)
    if total_runs is not None and wickets_lost >= 10:
        if rec.get('lowest_total') is None or total_runs < rec['lowest_total'].get('runs', 99999):
            rec['lowest_total'] = {'runs': total_runs, 'vs': opposition_name, 'format': format_type, 'season': season}
            if hasattr(game_engine, 'news_system') and game_engine.news_system:
                game_engine.news_system.add_record_news(team.name, 'lowest_total', f"{total_runs} all out vs {opposition_name}")
    if result == 'win' and margin_runs is not None and margin_runs > 0:
        if rec.get('biggest_win_runs') is None or margin_runs > rec['biggest_win_runs'].get('margin', 0):
            rec['biggest_win_runs'] = {'margin': margin_runs, 'vs': opposition_name, 'format': format_type, 'season': season}
            if hasattr(game_engine, 'news_system') and game_engine.news_system:
                game_engine.news_system.add_record_news(team.name, 'biggest_win_runs', f"by {margin_runs} runs vs {opposition_name}")
    if result == 'win' and margin_wickets is not None and margin_wickets > 0:
        if rec.get('biggest_win_wickets') is None or margin_wickets > rec['biggest_win_wickets'].get('margin', 0):
            rec['biggest_win_wickets'] = {'margin': margin_wickets, 'vs': opposition_name, 'format': format_type, 'season': season}
            if hasattr(game_engine, 'news_system') and game_engine.news_system:
                game_engine.news_system.add_record_news(team.name, 'biggest_win_wickets', f"by {margin_wickets} wickets vs {opposition_name}")


def check_and_add_player_milestones(game_engine, player, team_name):
    """Check career milestones (e.g. 100 Tests, 5000 runs) and add to milestones + news."""
    if not hasattr(player, 'milestones'):
        player.milestones = []
    season = getattr(game_engine, 'current_season', 1)
    added = []
    for fmt in ['T20', 'ODI', 'Test']:
        m = player.stats.get(fmt, {}).get('matches', 0)
        r = player.stats.get(fmt, {}).get('runs', 0)
        w = player.stats.get(fmt, {}).get('wickets', 0)
        for threshold, label in [(100, f'100 {fmt} matches'), (50, f'50 {fmt} matches'), (5000, f'5000 {fmt} runs'), (1000, f'1000 {fmt} runs'), (200, f'200 {fmt} wickets'), (100, f'100 {fmt} wickets')]:
            if threshold in (100, 50) and 'matches' in label and m >= threshold:
                key = f'{fmt}_matches_{threshold}'
                if not any(x.get('key') == key for x in player.milestones):
                    player.milestones.append({'season': season, 'description': label, 'key': key})
                    added.append(label)
            if 'runs' in label and r >= threshold:
                key = f'{fmt}_runs_{threshold}'
                if not any(x.get('key') == key for x in player.milestones):
                    player.milestones.append({'season': season, 'description': label, 'key': key})
                    added.append(label)
            if 'wickets' in label and w >= threshold:
                key = f'{fmt}_wickets_{threshold}'
                if not any(x.get('key') == key for x in player.milestones):
                    player.milestones.append({'season': season, 'description': label, 'key': key})
                    added.append(label)
    for desc in added:
        if hasattr(game_engine, 'news_system') and game_engine.news_system:
            game_engine.news_system.add_milestone_news(player.name, team_name, desc)


def compute_season_awards(game_engine):
    """Set game_engine.season_awards: batter, bowler, young_player of the season."""
    best_batter_name, best_bowler_name, best_young_name = None, None, None
    best_batter_runs, best_bowler_wickets, best_young_score = -1, -1, -1
    for team in game_engine.all_teams:
        for p in team.players:
            runs = sum(p.stats.get(fmt, {}).get('runs', 0) for fmt in ['T20', 'ODI', 'Test'])
            wkts = sum(p.stats.get(fmt, {}).get('wickets', 0) for fmt in ['T20', 'ODI', 'Test'])
            if runs > best_batter_runs:
                best_batter_runs = runs
                best_batter_name = p.name
            if wkts > best_bowler_wickets:
                best_bowler_wickets = wkts
                best_bowler_name = p.name
            if getattr(p, 'age', 99) <= 23 and (runs + wkts * 20) > best_young_score:
                best_young_score = runs + wkts * 20
                best_young_name = p.name
    game_engine.season_awards = {
        'batter': best_batter_name,
        'bowler': best_bowler_name,
        'young_player': best_young_name
    }


def get_difficulty_modifier_batting(game_engine):
    """Return multiplier for batting (e.g. Hard = harder for user). Used in sim."""
    d = getattr(game_engine, 'difficulty', 'Normal')
    if d in ('Hard', 'Expert'):
        return 0.95
    if d == 'Easy':
        return 1.05
    return 1.0


def get_difficulty_modifier_bowling(game_engine):
    """Return multiplier for opposition bowling strength (Hard = more wickets)."""
    d = getattr(game_engine, 'difficulty', 'Normal')
    if d in ('Hard', 'Expert'):
        return 1.05
    if d == 'Easy':
        return 0.95
    return 1.0


def get_pitch_report_text(pitch_conditions):
    """One-line pitch report from pitch_pace, pitch_bounce, pitch_spin."""
    if not pitch_conditions:
        return "Pitch: Good for batting."
    pace = pitch_conditions.get('pitch_pace', 5)
    bounce = pitch_conditions.get('pitch_bounce', 5)
    spin = pitch_conditions.get('pitch_spin', 5)
    if pace >= 7 and bounce >= 7:
        return "Pitch: Green and bouncy - seamers will enjoy."
    if spin >= 7:
        return "Pitch: Dry and turning - spinners will enjoy."
    if pace <= 3 and spin <= 3:
        return "Pitch: Flat and true - good for batting."
    return "Pitch: Good for batting with something for everyone."
