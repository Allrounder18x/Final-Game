"""
Rankings Screen - View top player rankings across formats
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QGridLayout, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from cricket_manager.ui.styles import COLORS, get_skill_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


def _rankings_yearly_block(player, calendar_year):
    return (getattr(player, "yearly_stats", None) or {}).get(calendar_year) or {}


def _yearly_block_for_source(player, calendar_year, stats_source):
    """stats_source: 'combined' (yearly_stats), 'international', 'associate_international', 'domestic', or 'u21_international'."""
    if stats_source == "international":
        return (getattr(player, "international_yearly_stats", None) or {}).get(calendar_year) or {}
    if stats_source == "associate_international":
        return (getattr(player, "associate_international_yearly_stats", None) or {}).get(calendar_year) or {}
    if stats_source == "domestic":
        return (getattr(player, "domestic_yearly_stats", None) or {}).get(calendar_year) or {}
    if stats_source == "u21_international":
        return (getattr(player, "u21_international_yearly_stats", None) or {}).get(calendar_year) or {}
    return _rankings_yearly_block(player, calendar_year)


def _rankings_batting_yearly_block(block, fmt):
    """Returns (runs, matches, avg, sr) from a single year's format block dict."""
    if fmt == "Overall":
        runs = matches = bf = dis = 0
        for f in ("T20", "ODI", "Test"):
            d = block.get(f) or {}
            runs += int(d.get("runs", 0) or 0)
            matches += int(d.get("matches", 0) or 0)
            bf += int(d.get("balls_faced", 0) or 0)
            dis += int(d.get("dismissals", 0) or 0)
        if dis > 0:
            avg = round(runs / dis, 2)
        else:
            avg = round(runs / matches, 2) if matches else 0.0
        sr = round((runs / bf * 100), 2) if bf else 0.0
        return runs, matches, avg, sr
    d = block.get(fmt) or {}
    runs = int(d.get("runs", 0) or 0)
    matches = int(d.get("matches", 0) or 0)
    bf = int(d.get("balls_faced", 0) or 0)
    dis = int(d.get("dismissals", 0) or 0)
    if fmt == "Test" and dis > 0:
        avg = round(runs / dis, 2)
    else:
        avg = round(runs / matches, 2) if matches else 0.0
    sr = round((runs / bf * 100), 2) if bf else 0.0
    return runs, matches, avg, sr


def _rankings_bowling_yearly_block(block, fmt):
    """Returns (wickets, matches, avg, econ) from a single year's format block dict."""
    if fmt == "Overall":
        wk = m = bb = rc = 0
        for f in ("T20", "ODI", "Test"):
            d = block.get(f) or {}
            wk += int(d.get("wickets", 0) or 0)
            m += int(d.get("matches", 0) or 0)
            bb += int(d.get("balls_bowled", 0) or 0)
            rc += int(d.get("runs_conceded", 0) or 0)
        avg = round(rc / wk, 2) if wk else 0.0
        econ = round(rc / (bb / 6.0), 2) if bb else 0.0
        return wk, m, avg, econ
    d = block.get(fmt) or {}
    wk = int(d.get("wickets", 0) or 0)
    m = int(d.get("matches", 0) or 0)
    bb = int(d.get("balls_bowled", 0) or 0)
    rc = int(d.get("runs_conceded", 0) or 0)
    avg = round(rc / wk, 2) if wk else 0.0
    econ = round(rc / (bb / 6.0), 2) if bb else 0.0
    return wk, m, avg, econ


def _rankings_batting_yearly(player, calendar_year, fmt):
    """Returns (runs, matches, avg, sr) from yearly_stats for one calendar year."""
    block = _rankings_yearly_block(player, calendar_year)
    return _rankings_batting_yearly_block(block, fmt)


def _rankings_bowling_yearly(player, calendar_year, fmt):
    """Returns (wickets, matches, avg, econ) from yearly_stats."""
    block = _rankings_yearly_block(player, calendar_year)
    return _rankings_bowling_yearly_block(block, fmt)


def _rankings_team_matches_tier(game_engine, team, tier_label, match_format, league_year_for_snapshot):
    if tier_label == "All Tiers":
        return True
    if tier_label == "U21":
        tier_num = 5
    else:
        tier_num = int(tier_label.split()[-1])
    fmt_for_tier = match_format if match_format in ("T20", "ODI", "Test") else "T20"
    if league_year_for_snapshot is None:
        team_tier = team.format_tiers.get(fmt_for_tier, getattr(team, "tier", 1))
    else:
        team_tier = game_engine.get_team_tier_at_league_year(
            team, fmt_for_tier, league_year_for_snapshot
        )
    return team_tier == tier_num


def _rankings_fielding_matches_yearly_block(block, fmt):
    """Total matches in that calendar year block (fielding rankings proxy)."""
    if fmt == "Overall":
        return sum(int((block.get(f) or {}).get("matches", 0) or 0) for f in ("T20", "ODI", "Test"))
    return int((block.get(fmt) or {}).get("matches", 0) or 0)


def _rankings_fielding_matches_yearly(player, calendar_year, fmt):
    """Total international matches in that calendar year (proxy for season activity in fielding rankings)."""
    block = _rankings_yearly_block(player, calendar_year)
    return _rankings_fielding_matches_yearly_block(block, fmt)


def national_team_for_profile_rank_chips(game_engine, profile_team, player=None):
    """
    Resolve the international side used for tier-scoped profile header ranks.
    Prefer the player's current nationality (e.g. associate side after a move) so tiers match
    where they play international cricket, not an outdated profile context.
    Domestic clubs map to parent_nation; national teams use that team when nationality does not resolve.
    """
    if not game_engine:
        return None
    if player is not None:
        nat = (getattr(player, "nationality", None) or "").strip()
        if nat:
            by_nat = game_engine.get_team_by_name(nat)
            if by_nat is not None and not getattr(by_nat, "is_domestic", False):
                return by_nat
    if not profile_team:
        return None
    if getattr(profile_team, "is_domestic", False):
        nation = getattr(profile_team, "parent_nation", None)
        if nation:
            return game_engine.get_team_by_name(nation)
        return None
    return profile_team


def tier_label_for_profile_format(national_team, fmt_key):
    """
    Leaderboard tier label for one format ('Tier 1'…'Tier 4' or 'All Tiers').
    Senior international header chips must not use 'U21' here — that label switches the pool to
    u21_international stats in the rankings builder.
    """
    if not national_team:
        return "All Tiers"
    ft = getattr(national_team, "format_tiers", None) or {}
    tnum = ft.get(fmt_key, getattr(national_team, "tier", 1))
    try:
        tnum = int(tnum)
    except (TypeError, ValueError):
        tnum = 1
    if tnum in (1, 2, 3, 4):
        return f"Tier {tnum}"
    return "All Tiers"


def _international_matches_in_year(player, calendar_year, fmt_key):
    block = (getattr(player, "international_yearly_stats", None) or {}).get(calendar_year) or {}
    d = block.get(fmt_key) or {}
    return int(d.get("matches", 0) or 0)


def _build_season_rankings_list(
    game_engine,
    category,
    match_format,
    tier_label,
    calendar_year,
    league_snap_year,
    stats_source="combined",
    u21_only=False,
):
    """
    Rank players using yearly_stats for `calendar_year` only (season totals).
    Returns sorted list of row tuples (format depends on category).
    league_snap_year: tier filter snapshot year (None = current tiers).
    stats_source: 'combined' (yearly_stats), 'international', 'associate_international', 'domestic', or 'u21_international'.
    u21_only: if True, only national U21 squad members; stats use u21_international_yearly_stats (youth intl only).
    """
    u21_pool = u21_only or (tier_label == "U21")
    if u21_pool:
        stats_source = "u21_international"
    # U21 leaderboard is all national U21 squads; do not filter nations by senior Tier 5.
    tier_for_filter = "All Tiers" if tier_label == "U21" else tier_label

    teams = game_engine.all_teams
    all_players = []
    if u21_pool:
        for team in teams:
            if getattr(team, "is_domestic", False):
                continue
            if not _rankings_team_matches_tier(game_engine, team, tier_for_filter, match_format, league_snap_year):
                continue
            for player in getattr(team, "u21_squad", None) or []:
                all_players.append((player, team))
    else:
        for team in teams:
            if not _rankings_team_matches_tier(game_engine, team, tier_for_filter, match_format, league_snap_year):
                continue
            for player in team.players:
                all_players.append((player, team))

    ranked = []

    if category == "Batting":
        for player, team in all_players:
            if any(role in player.role for role in ("Batter", "Wicketkeeper", "All-Rounder", "Allrounder")):
                block = _yearly_block_for_source(player, calendar_year, stats_source)
                runs, matches, avg, sr = _rankings_batting_yearly_block(block, match_format)
                ranked.append((player, team, player.batting, runs, matches, avg, sr))
        ranked.sort(key=lambda x: (x[3] == 0, -x[3]))
    elif category == "Bowling":
        for player, team in all_players:
            if any(role in player.role for role in ("Bowler", "Spinner", "Pacer", "All-Rounder", "Allrounder")):
                block = _yearly_block_for_source(player, calendar_year, stats_source)
                wk, matches, avg, econ = _rankings_bowling_yearly_block(block, match_format)
                ranked.append((player, team, player.bowling, wk, matches, avg, econ))
        ranked.sort(key=lambda x: (x[3] == 0, -x[3]))
    elif category == "All-Rounder":
        for player, team in all_players:
            if "All-Rounder" in player.role or "Allrounder" in player.role:
                block = _yearly_block_for_source(player, calendar_year, stats_source)
                runs, _, _, _ = _rankings_batting_yearly_block(block, match_format)
                wk, _, _, _ = _rankings_bowling_yearly_block(block, match_format)
                performance = (runs / 10.0) + (wk * 20)
                if performance > 0:
                    ranked.append((player, team, player.batting, player.bowling, performance))
        ranked.sort(key=lambda x: x[4], reverse=True)
    else:
        for player, team in all_players:
            block = _yearly_block_for_source(player, calendar_year, stats_source)
            mplay = _rankings_fielding_matches_yearly_block(block, match_format)
            ranked.append((player, team, player.fielding, mplay))
        ranked.sort(key=lambda x: (x[3] == 0, -x[3], -x[2]))

    return ranked


def _prior_season_rank_map(
    game_engine,
    category,
    match_format,
    tier_label,
    prior_calendar_year,
    stats_source="combined",
    u21_only=False,
):
    """
    Map id(player) -> rank (1-based) in the same filters for the previous calendar year.
    Returns empty dict if prior year is invalid or no pool.
    """
    if prior_calendar_year is None:
        return {}
    snap = prior_calendar_year
    rows = _build_season_rankings_list(
        game_engine,
        category,
        match_format,
        tier_label,
        prior_calendar_year,
        snap,
        stats_source=stats_source,
        u21_only=u21_only,
    )
    out = {}
    pos = 1
    for row in rows:
        player = row[0]
        out[id(player)] = pos
        pos += 1
    return out


def _format_last_season_bracket(rank_map, player):
    r = rank_map.get(id(player))
    if r is None:
        return " (Last: —)"
    return f" (Last: #{r})"


def player_season_rank_for_filters(
    game_engine,
    player,
    category,
    match_format,
    tier_label,
    calendar_year,
    stats_source="combined",
    u21_only=False,
):
    """1-based rank for one season with same filters as the rankings table, or None if unranked."""
    if game_engine is None or player is None or calendar_year is None or calendar_year < 2000:
        return None
    m = _prior_season_rank_map(
        game_engine,
        category,
        match_format,
        tier_label,
        calendar_year,
        stats_source=stats_source,
        u21_only=u21_only,
    )
    return m.get(id(player))


def format_three_year_rank_suffix(
    game_engine, player, category, match_format, tier_label, display_year,
    stats_source="combined",
):
    """
    Bracket after player name: ranks for the three seasons before display_year (most recent first),
    numbers only; same filters as the current table.
    """
    if display_year is None or display_year < 2001:
        return ""
    parts = []
    for offset in (1, 2, 3):
        y = display_year - offset
        if y < 2000:
            continue
        r = player_season_rank_for_filters(
            game_engine, player, category, match_format, tier_label, y,
            stats_source=stats_source,
            u21_only=(tier_label == "U21"),
        )
        parts.append(f"#{r}" if r is not None else "—")
    if not parts:
        return ""
    return " (" + " · ".join(parts) + ")"


def player_profile_career_ranking_chips(game_engine, player, display_year=None, profile_team=None):
    """
    Six segment strings (T20/ODI/Test Bat, then T20/ODI/Test Bowl) for a horizontal header row.
    International season ranks for the national side's tier per format, last completed calendar year
    (display_year - 1). No rank until senior international activity in that format that season, or
    while clear_intl_rank_until_next_match is set (e.g. after returning from an associate nation).
    """
    if not game_engine or not player:
        return []
    cy = display_year if display_year is not None else getattr(game_engine, "current_year", None)
    if not cy or cy < 2001:
        return []
    y = cy - 1
    if y < 2000:
        return []

    national = national_team_for_profile_rank_chips(game_engine, profile_team, player)

    def segment_for(cat, fmt_key):
        if getattr(player, "clear_intl_rank_until_next_match", False):
            rank_s = "—"
        elif _international_matches_in_year(player, y, fmt_key) <= 0:
            rank_s = "—"
        else:
            tier_label = tier_label_for_profile_format(national, fmt_key)
            r = player_season_rank_for_filters(
                game_engine, player, cat, fmt_key, tier_label, y,
                stats_source="international",
                u21_only=False,
            )
            rank_s = f"#{r}" if r is not None else "—"
        role = "Bat" if cat == "Batting" else "Bowl"
        return f"{fmt_key} {role}: {rank_s}"

    formats = ("T20", "ODI", "Test")
    bat_lines = [segment_for("Batting", f) for f in formats]
    bowl_lines = [segment_for("Bowling", f) for f in formats]
    return bat_lines + bowl_lines


def player_profile_career_ranking_lines(game_engine, player, display_year=None, profile_team=None):
    """
    Two multi-line strings for the player profile header: batting block and bowling block.
    International season ranks for the national tier per format, last completed calendar year only
    (default display_year: engine current_year).
    """
    chips = player_profile_career_ranking_chips(
        game_engine, player, display_year, profile_team=profile_team
    )
    if not chips or len(chips) < 6:
        return ("", "")
    bat_text = "\n".join(chips[:3])
    bowl_text = "\n".join(chips[3:])
    return (bat_text, bowl_text)


def _three_year_rank_line_for_scope(
    game_engine, player, category, fmt, display_year, stats_source, u21_only,
):
    """Single line: last three seasons' ranks for All Tiers (e.g. '#3 · #12 · —', most recent first)."""
    if display_year is None or display_year < 2001:
        return ""
    parts = []
    for offset in (1, 2, 3):
        y = display_year - offset
        if y < 2000:
            continue
        m = _prior_season_rank_map(
            game_engine, category, fmt, "All Tiers", y, stats_source, u21_only,
        )
        r = m.get(id(player))
        parts.append(f"#{r}" if r is not None else "—")
    return " · ".join(parts)


def player_profile_rankings_tab_sections(game_engine, player, display_year=None):
    """
    Legacy flat lines (unused if UI uses player_profile_rankings_tab_tables).
    """
    data = player_profile_rankings_tab_tables(game_engine, player, display_year)
    out = []
    for sec in data:
        lines = [sec["subtitle"]]
        for row in sec["rows"]:
            bat_s = " · ".join(row["bat_display"])
            bowl_s = " · ".join(row["bowl_display"])
            lines.append(f"{row['format']} Bat — {bat_s}")
            lines.append(f"{row['format']} Bowl — {bowl_s}")
        out.append((sec["title"], lines))
    return out


def _rank_triplet_for_scope(
    game_engine, player, category, fmt, display_year, stats_source, u21_only,
):
    """Three seasons (most recent first): list of (year, rank or None)."""
    triple = []
    for offset in (1, 2, 3):
        y = display_year - offset
        if y < 2000:
            triple.append((y, None))
            continue
        m = _prior_season_rank_map(
            game_engine, category, fmt, "All Tiers", y, stats_source, u21_only,
        )
        r = m.get(id(player))
        triple.append((y, r))
    return triple


def player_profile_rankings_tab_tables(game_engine, player, display_year=None):
    """
    Structured data for the Rankings tab: list of section dicts with title, subtitle,
    season_years (3 ints, most recent first), and rows per format with bat/bowl rank triplets.
    """
    if not game_engine or not player:
        return []
    cy = display_year if display_year is not None else getattr(game_engine, "current_year", None)
    if not cy or cy < 2001:
        return []

    sections_meta = (
        (
            "Senior international",
            "Leaderboard ranks from full-member international matches only (All Tiers).",
            "international",
            False,
        ),
        (
            "Associate international",
            "Leaderboard ranks from associate-nation international matches only (All Tiers).",
            "associate_international",
            False,
        ),
        (
            "Domestic",
            "Leaderboard ranks from domestic club and league matches only.",
            "domestic",
            False,
        ),
        (
            "U21",
            "Among national U21 squads; youth international (U21 vs U21) calendar-year totals only.",
            "u21_international",
            True,
        ),
    )
    formats = ("T20", "ODI", "Test")
    out = []
    for title, subtitle, src, u21 in sections_meta:
        years = [cy - 1, cy - 2, cy - 3]
        years = [y for y in years if y >= 2000][:3]
        rows = []
        for fmt in formats:
            bat_triple = _rank_triplet_for_scope(
                game_engine, player, "Batting", fmt, cy, src, u21,
            )
            bowl_triple = _rank_triplet_for_scope(
                game_engine, player, "Bowling", fmt, cy, src, u21,
            )
            bat_display = [f"#{t[1]}" if t[1] is not None else "—" for t in bat_triple]
            bowl_display = [f"#{t[1]}" if t[1] is not None else "—" for t in bowl_triple]
            rows.append({
                "format": fmt,
                "bat_triple": bat_triple,
                "bowl_triple": bowl_triple,
                "bat_display": bat_display,
                "bowl_display": bowl_display,
            })
        out.append({
            "title": title,
            "subtitle": subtitle,
            "season_years": years,
            "rows": rows,
        })
    return out


class RankingsScreen(BaseScreen):
    """Player rankings screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.all_teams = game_engine.all_teams if game_engine else []
        self.current_format = "T20"
        self.current_category = "Batting"
        self.current_tier = "Tier 1"  # Default tier filter
        self.rankings_season_view_year = None
        self.rankings_stats_source = "international"  # default: senior international; combined | associate_international | domestic
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main scroll area - SINGLE SCROLL BAR
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        # Content
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Filters
        filters = self.create_filters()
        content_layout.addWidget(filters)
        
        # Category selector
        category_selector = self.create_category_selector()
        content_layout.addWidget(category_selector)
        
        # Rankings table
        self.rankings_table = self.create_rankings_table()
        content_layout.addWidget(self.rankings_table, 1)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def create_filters(self):
        """Create filter controls"""
        container = QFrame()
        container.setObjectName("rankingsFilters")
        container.setStyleSheet(f"""
            QFrame#rankingsFilters {{
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Player Rankings")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["T20", "ODI", "Test", "Overall"])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        layout.addWidget(self.format_combo)
        
        # Tier selector
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(tier_label)
        
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["Tier 1", "Tier 2", "Tier 3", "Tier 4", "U21", "All Tiers"])
        self.tier_combo.setCurrentText(self.current_tier)
        self.tier_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.tier_combo.currentTextChanged.connect(self.on_tier_changed)
        layout.addWidget(self.tier_combo)
        
        stats_label = QLabel("Stats:")
        stats_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(stats_label)
        self.stats_scope_combo = QComboBox()
        self.stats_scope_combo.addItems(["Combined", "International", "Associate international", "Domestic"])
        self.stats_scope_combo.setCurrentText("International")
        self.stats_scope_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 130px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.stats_scope_combo.currentTextChanged.connect(self.on_stats_scope_changed)
        layout.addWidget(self.stats_scope_combo)
        
        season_label = QLabel("Season:")
        season_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(season_label)
        self.rankings_season_combo = QComboBox()
        self.rankings_season_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 160px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.rankings_season_combo.currentIndexChanged.connect(self.on_rankings_season_filter_changed)
        layout.addWidget(self.rankings_season_combo)
        
        container.setLayout(layout)
        self._populate_rankings_season_combo()
        return container
    
    def create_category_selector(self):
        """Create category selector with radio buttons"""
        container = QFrame()
        container.setObjectName("rankingsCategory")
        container.setStyleSheet(f"""
            QFrame#rankingsCategory {{
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Label
        label = QLabel("Category:")
        label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #EAF1FF;
        """)
        layout.addWidget(label)
        
        # Radio buttons
        self.category_group = QButtonGroup()
        categories = ["Batting", "Bowling", "All-Rounder", "Fielding"]
        
        for i, category in enumerate(categories):
            radio = QRadioButton(category)
            radio.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 13px;
                    color: #EAF1FF;
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QRadioButton::indicator::unchecked {{
                    border: 2px solid {COLORS['border']};
                    border-radius: 9px;
                    background-color: #111827;
                }}
                QRadioButton::indicator::checked {{
                    border: 2px solid {COLORS['primary']};
                    border-radius: 9px;
                    background-color: {COLORS['primary']};
                }}
            """)
            if category == self.current_category:
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, cat=category: self.on_category_changed(cat) if checked else None)
            self.category_group.addButton(radio, i)
            layout.addWidget(radio)
        
        layout.addStretch()
        
        # Info
        info = QLabel("Top 100 players shown")
        info.setStyleSheet("""
            font-size: 12px;
            color: #888;
        """)
        layout.addWidget(info)
        
        container.setLayout(layout)
        return container
    
    def create_rankings_table(self):
        """Create rankings table"""
        container = QFrame()
        container.setObjectName("rankingsTableContainer")
        container.setStyleSheet(f"""
            QFrame#rankingsTableContainer {{
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        self.table_title = QLabel(f"Top {self.current_category} Players - {self.current_format}")
        self.table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(self.table_title)
        
        # Info label
        info_label = QLabel("💡 Double-click on any player row to view their profile")
        info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Table
        self.table_widget = QTableWidget()
        self.ranked_players_data = []  # Store player data for click handling
        table = self.table_widget
        
        # Different columns based on category
        if self.current_category == "Batting":
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Age", "Role", "Runs", "Avg", "SR", "Form"
            ])
        elif self.current_category == "Bowling":
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Age", "Role", "Wickets", "Avg", "Econ", "Form"
            ])
        elif self.current_category == "All-Rounder":
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Age", "Role", "Batting", "Bowling", "Rating", "Form"
            ])
        else:  # Fielding
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Age", "Role", "Fielding", "Season Mat", "Form"
            ])
        
        # Style table - ensure header text is visible with WHITE text on dark green
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                alternate-background-color: {COLORS['bg_tertiary']};
                border: none;
                gridline-color: {COLORS['border']};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px;
                border: none;
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QHeaderView {{
                background-color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: #FFFFFF;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.2);
                font-weight: bold;
                font-size: 13px;
                min-height: 25px;
            }}
        """)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setVisible(True)  # Ensure header is visible
        table.horizontalHeader().setFixedHeight(40)  # Explicit header height
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setVisible(False)
        
        # DISABLE SCROLL BARS - use parent scroll
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 60)
        table.setColumnWidth(3, 60)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 70)
        table.setColumnWidth(7, 70)
        if table.columnCount() > 8:
            table.setColumnWidth(8, 70)
        
        # Populate with sample data
        self.populate_rankings_table(table)
        
        # Connect double-click to open player profile
        table.cellDoubleClicked.connect(self.on_player_clicked)
        
        # Set fixed height based on content (show top 100)
        row_count = min(100, table.rowCount())
        row_height = 35
        header_height = 40
        total_height = header_height + (row_count * row_height)
        table.setFixedHeight(total_height)
        
        layout.addWidget(table)
        container.setLayout(layout)
        return container
    
    def populate_rankings_table(self, table):
        """Populate rankings from yearly season stats; name shows last calendar year's rank for same filters."""
        if not self.game_engine:
            print("[Rankings] ERROR: No game engine available")
            return
        
        ge = self.game_engine
        display_year = ge.current_year if self.rankings_season_view_year is None else self.rankings_season_view_year
        league_snap = self.rankings_season_view_year if self.rankings_season_view_year is not None else None
        
        ranked_players = _build_season_rankings_list(
            ge,
            self.current_category,
            self.current_format,
            self.current_tier,
            display_year,
            league_snap,
            stats_source=self.rankings_stats_source,
        )
        print(
            f"[Rankings] Season stats year={display_year}, "
            f"rows={len(ranked_players)}, tier={self.current_tier}"
        )
        
        self.ranked_players_data = ranked_players[:100]
        
        display_count = min(100, len(ranked_players))
        table.setRowCount(display_count)
        
        for row in range(display_count):
            bracket = format_three_year_rank_suffix(
                ge,
                ranked_players[row][0],
                self.current_category,
                self.current_format,
                self.current_tier,
                display_year,
                stats_source=self.rankings_stats_source,
            )
            if self.current_category == "Batting":
                player, team, batting, runs, matches, avg, sr = ranked_players[row]
                rank_item = self.create_rank_item(row + 1)
                table.setItem(row, 0, rank_item)
                table.setItem(row, 1, QTableWidgetItem(f"{player.name}{bracket}"))
                table.setItem(row, 2, QTableWidgetItem(team.name))
                table.setItem(row, 3, self.create_center_item(str(player.age)))
                table.setItem(row, 4, QTableWidgetItem(player.role))
                table.setItem(row, 5, self.create_center_item(str(runs)))
                table.setItem(row, 6, self.create_center_item(f"{avg:.2f}" if avg > 0 else "0.00"))
                table.setItem(row, 7, self.create_center_item(f"{sr:.2f}" if sr > 0 else "0.00"))
                table.setItem(row, 8, self.create_center_item(str(player.form)))
            elif self.current_category == "Bowling":
                player, team, bowling, wickets, matches, avg, econ = ranked_players[row]
                rank_item = self.create_rank_item(row + 1)
                table.setItem(row, 0, rank_item)
                table.setItem(row, 1, QTableWidgetItem(f"{player.name}{bracket}"))
                table.setItem(row, 2, QTableWidgetItem(team.name))
                table.setItem(row, 3, self.create_center_item(str(player.age)))
                table.setItem(row, 4, QTableWidgetItem(player.role))
                table.setItem(row, 5, self.create_center_item(str(wickets)))
                table.setItem(row, 6, self.create_center_item(f"{avg:.2f}" if avg > 0 else "0.00"))
                table.setItem(row, 7, self.create_center_item(f"{econ:.2f}" if econ > 0 else "0.00"))
                table.setItem(row, 8, self.create_center_item(str(player.form)))
            elif self.current_category == "All-Rounder":
                player, team, batting, bowling, performance = ranked_players[row]
                rank_item = self.create_rank_item(row + 1)
                table.setItem(row, 0, rank_item)
                table.setItem(row, 1, QTableWidgetItem(f"{player.name}{bracket}"))
                table.setItem(row, 2, QTableWidgetItem(team.name))
                table.setItem(row, 3, self.create_center_item(str(player.age)))
                table.setItem(row, 4, QTableWidgetItem(player.role))
                table.setItem(row, 5, self.create_center_item(str(batting)))
                table.setItem(row, 6, self.create_center_item(str(bowling)))
                table.setItem(row, 7, self.create_center_item(f"{performance:.1f}"))
                table.setItem(row, 8, self.create_center_item(str(player.form)))
            else:
                player, team, fielding, mplay = ranked_players[row]
                rank_item = self.create_rank_item(row + 1)
                table.setItem(row, 0, rank_item)
                table.setItem(row, 1, QTableWidgetItem(f"{player.name}{bracket}"))
                table.setItem(row, 2, QTableWidgetItem(team.name))
                table.setItem(row, 3, self.create_center_item(str(player.age)))
                table.setItem(row, 4, QTableWidgetItem(player.role))
                table.setItem(row, 5, self.create_center_item(str(fielding)))
                table.setItem(row, 6, self.create_center_item(str(mplay)))
                table.setItem(row, 7, self.create_center_item(str(player.form)))
    
    def create_rank_item(self, rank):
        """Create styled rank item"""
        rank_item = QTableWidgetItem(str(rank))
        rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Color code top 3
        if rank <= 3:
            font = rank_item.font()
            font.setBold(True)
            rank_item.setFont(font)
            
            if rank == 1:
                rank_item.setForeground(QColor('#FFD700'))  # Gold
            elif rank == 2:
                rank_item.setForeground(QColor('#C0C0C0'))  # Silver
            elif rank == 3:
                rank_item.setForeground(QColor('#CD7F32'))  # Bronze
        
        return rank_item
    
    def create_center_item(self, text):
        """Create centered table item"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.refresh_rankings()
    
    def on_category_changed(self, category):
        """Handle category change"""
        self.current_category = category
        self.refresh_rankings()
    
    def on_tier_changed(self, tier):
        """Handle tier change"""
        self.current_tier = tier
        self.refresh_rankings()
    
    def on_stats_scope_changed(self, text):
        """Combined vs international-only vs domestic-only yearly stats for rankings."""
        mapping = {
            "Combined": "combined",
            "International": "international",
            "Associate international": "associate_international",
            "Domestic": "domestic",
        }
        self.rankings_stats_source = mapping.get(text, "combined")
        self.refresh_rankings()
    
    def _populate_rankings_season_combo(self):
        """Same years as Leagues tab, plus any year keys found in player yearly_stats."""
        if not hasattr(self, "rankings_season_combo"):
            return
        saved = self.rankings_season_view_year
        self.rankings_season_combo.blockSignals(True)
        self.rankings_season_combo.clear()
        self.rankings_season_combo.addItem("Current season (YTD)", None)
        years = set()
        if self.game_engine:
            for e in getattr(self.game_engine, "league_standings_history", None) or []:
                y = e.get("year")
                if y is not None:
                    years.add(y)
            for team in self.game_engine.all_teams:
                for p in getattr(team, "players", []) or []:
                    years.update((getattr(p, "yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "international_yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "associate_international_yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "domestic_yearly_stats", None) or {}).keys())
                for p in getattr(team, "u21_squad", None) or []:
                    years.update((getattr(p, "yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "international_yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "associate_international_yearly_stats", None) or {}).keys())
                    years.update((getattr(p, "domestic_yearly_stats", None) or {}).keys())
        for y in sorted(years, reverse=True):
            history = getattr(self.game_engine, "league_standings_history", None) or []
            ent = next((e for e in history if e.get("year") == y), None)
            if ent:
                self.rankings_season_combo.addItem(
                    f"{y} (Season {ent.get('season', '?')} ended)", y
                )
            else:
                self.rankings_season_combo.addItem(str(y), y)
        idx = 0
        if saved is not None:
            for i in range(self.rankings_season_combo.count()):
                if self.rankings_season_combo.itemData(i) == saved:
                    idx = i
                    break
        else:
            # Default: last completed calendar year = current in-game year minus 1
            target = None
            if self.game_engine is not None:
                cy = getattr(self.game_engine, "current_year", None)
                if cy is not None and cy > 2000:
                    target = cy - 1
            if target is not None:
                for i in range(self.rankings_season_combo.count()):
                    if self.rankings_season_combo.itemData(i) == target:
                        idx = i
                        break
                else:
                    best_i = 0
                    best_y = None
                    for i in range(1, self.rankings_season_combo.count()):
                        y = self.rankings_season_combo.itemData(i)
                        if y is not None and y <= target:
                            if best_y is None or y > best_y:
                                best_y = y
                                best_i = i
                    if best_y is not None:
                        idx = best_i
                    elif self.rankings_season_combo.count() > 1:
                        idx = 1
            elif self.rankings_season_combo.count() > 1:
                idx = 1
        self.rankings_season_combo.setCurrentIndex(idx)
        self.rankings_season_view_year = self.rankings_season_combo.currentData()
        self.rankings_season_combo.blockSignals(False)
    
    def on_rankings_season_filter_changed(self, _index=None):
        if not hasattr(self, "rankings_season_combo"):
            return
        self.rankings_season_view_year = self.rankings_season_combo.currentData()
        self.refresh_rankings()
    
    def refresh_rankings(self):
        """Refresh rankings data (called by filter changes)"""
        # Update all_teams from game engine (important after season simulation when tiers change)
        if self.game_engine:
            self.all_teams = self.game_engine.all_teams
        
        # Update table title
        if hasattr(self, 'table_title'):
            tier_text = f" ({self.current_tier})" if self.current_tier != "All Tiers" else ""
            if self.rankings_season_view_year is None and self.game_engine:
                sy = f" • year {self.game_engine.current_year} (YTD)"
            elif self.rankings_season_view_year is not None:
                sy = f" • calendar year {self.rankings_season_view_year}"
            else:
                sy = ""
            src_label = {
                "combined": "combined",
                "international": "senior international (full member) only",
                "associate_international": "associate international only",
                "domestic": "domestic only",
            }.get(self.rankings_stats_source, "combined")
            self.table_title.setText(
                f"Top {self.current_category} ({src_label} season stats) — {self.current_format}{tier_text}{sy}. "
                f"Bracket = rank previous calendar year, same filters."
            )
        
        # Clear and repopulate existing table
        if hasattr(self, 'table_widget') and self.table_widget:
            # Recreate table structure based on category
            table = self.table_widget
            # Use clearContents instead of clear to preserve headers
            table.clearContents()
            table.setRowCount(0)
            
            if self.current_category == "Batting":
                table.setColumnCount(9)
                table.setHorizontalHeaderLabels([
                    "Rank", "Player", "Team", "Age", "Role", "Runs", "Avg", "SR", "Form"
                ])
            elif self.current_category == "Bowling":
                table.setColumnCount(9)
                table.setHorizontalHeaderLabels([
                    "Rank", "Player", "Team", "Age", "Role", "Wickets", "Avg", "Econ", "Form"
                ])
            elif self.current_category == "All-Rounder":
                table.setColumnCount(9)
                table.setHorizontalHeaderLabels([
                    "Rank", "Player", "Team", "Age", "Role", "Batting", "Bowling", "Rating", "Form"
                ])
            else:  # Fielding
                table.setColumnCount(8)
                table.setHorizontalHeaderLabels([
                    "Rank", "Player", "Team", "Age", "Role", "Fielding", "Season Mat", "Form"
                ])
            
            # Reapply stylesheet to ensure headers are visible
            table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: #111827;
                    alternate-background-color: {COLORS['bg_tertiary']};
                    border: none;
                    gridline-color: {COLORS['border']};
                    font-size: 13px;
                }}
                QTableWidget::item {{
                    padding: 10px;
                    border: none;
                }}
                QTableWidget::item:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
                QTableWidget::item:selected {{
                    background-color: {COLORS['primary']};
                    color: white;
                }}
                QHeaderView {{
                    background-color: {COLORS['primary']};
                }}
                QHeaderView::section {{
                    background-color: {COLORS['primary']};
                    color: white;
                    padding: 12px 8px;
                    border: none;
                    border-right: 1px solid rgba(255, 255, 255, 0.2);
                    font-weight: bold;
                    font-size: 12px;
                    min-height: 20px;
                }}
            """)
            
            self.populate_rankings_table(table)
        
        print(f"[Rankings] Refreshed: {self.current_format} - {self.current_category}")
    
    def refresh_data(self):
        """Refresh data when tab is clicked (called by main window navigation)"""
        self._populate_rankings_season_combo()
        self.refresh_rankings()
    
    def on_player_clicked(self, row, col):
        """Open player profile when table row is double-clicked"""
        if not hasattr(self, 'ranked_players_data') or row >= len(self.ranked_players_data):
            return
        
        player_data = self.ranked_players_data[row]
        player = player_data[0]
        team = player_data[1]
        
        if player and team:
            from cricket_manager.ui.player_profile_dialog import PlayerProfileDialog
            dialog = PlayerProfileDialog(self, player, team, self.game_engine)
            dialog.exec()
