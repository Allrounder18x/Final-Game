"""
Cricinfo-style career narrative for the player profile Career history tab.
Regenerated from live save data: season_history, yearly_stats, traits, World Cup history, etc.
"""

from __future__ import annotations

import html
from typing import Any, Dict, List, Optional, Tuple

from cricket_manager.systems.trait_assignment import (
    get_trait_display_name,
    is_negative_trait,
    is_positive_trait,
)
from cricket_manager.ui.rankings_view import player_season_rank_for_filters


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def _strip_reason(text: Any, max_len: int = 280) -> str:
    t = (str(text) if text is not None else "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _surname(full_name: str) -> str:
    parts = (full_name or "Player").strip().split()
    return parts[-1] if parts else "Player"


def _season_to_calendar_year(game_engine, season_num: Optional[int]) -> Optional[int]:
    if season_num is None or not game_engine:
        return None
    for e in getattr(game_engine, "league_standings_history", None) or []:
        if e.get("season") == season_num:
            return e.get("year")
    cs = getattr(game_engine, "current_season", None)
    cy = getattr(game_engine, "current_year", None)
    if cs is not None and cy is not None:
        return cy - (cs - int(season_num))
    return None


def _trait_buckets(player) -> Tuple[List[str], List[str]]:
    pos, neg = [], []
    for t in getattr(player, "traits", None) or []:
        if not isinstance(t, dict):
            continue
        key = t.get("name") or ""
        label = get_trait_display_name(key) if key else "Trait"
        if is_positive_trait(key):
            pos.append(label)
        elif is_negative_trait(key):
            neg.append(label)
        else:
            pos.append(label)
    return pos, neg


def _fmt_list(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _collect_season_rows(player) -> List[Tuple[str, Dict[str, Any]]]:
    """(format, season_dict) for all season_history entries with matches."""
    rows = []
    for fmt in ("T20", "ODI", "Test"):
        for block in player.season_history.get(fmt, []) or []:
            m = int(block.get("matches", 0) or 0)
            if m > 0:
                rows.append((fmt, block))
    rows.sort(key=lambda x: (x[1].get("season", 0), x[0]))
    return rows


def _debut_season_number(player) -> Optional[int]:
    seasons = []
    for fmt in ("T20", "ODI", "Test"):
        for block in player.season_history.get(fmt, []) or []:
            if int(block.get("matches", 0) or 0) > 0:
                seasons.append(int(block.get("season", 0) or 0))
    return min(seasons) if seasons else None


def _first_season_age(player, game_engine) -> Optional[int]:
    """Age during the player's first season with recorded matches (not current age)."""
    debut = _debut_season_number(player)
    if debut is not None:
        for fmt in ("T20", "ODI", "Test"):
            for block in player.season_history.get(fmt, []) or []:
                if int(block.get("season", -1) or -1) != debut:
                    continue
                if int(block.get("matches", 0) or 0) <= 0:
                    continue
                a = block.get("age")
                if a is not None:
                    return int(a)
    sh = getattr(player, "skill_history", None) or []
    if sh:
        if debut is not None:
            for snap in sh:
                if int(snap.get("season", -1) or -1) == debut:
                    a = snap.get("age")
                    if a is not None:
                        return int(a)
        a0 = sh[0].get("age")
        if a0 is not None:
            return int(a0)
    if debut is not None and game_engine:
        cs = getattr(game_engine, "current_season", None)
        cur_age = int(getattr(player, "age", 0) or 0)
        if cs is not None and cur_age > 0:
            return max(1, cur_age - (int(cs) - int(debut)))
    return None


def _debut_year_text(game_engine, player) -> Tuple[Optional[int], Optional[int]]:
    """(season_num, calendar_year) for first competitive season."""
    ds = _debut_season_number(player)
    if ds is None:
        ys = sorted((getattr(player, "yearly_stats", None) or {}).keys())
        if ys:
            return None, int(ys[0])
        return None, None
    return ds, _season_to_calendar_year(game_engine, ds)


def _yearly_block_totals(yblock: dict, fmt: str) -> Tuple[int, int, int]:
    """runs, wickets, matches for one format in a yearly block dict."""
    d = (yblock or {}).get(fmt) or {}
    return (
        int(d.get("runs", 0) or 0),
        int(d.get("wickets", 0) or 0),
        int(d.get("matches", 0) or 0),
    )


def _calendar_years_for_rank_scan(player, game_engine) -> List[int]:
    """Calendar years to scan for T20 leaderboard ranks (same pools as Rankings tab)."""
    years = set()
    for attr in (
        "yearly_stats",
        "international_yearly_stats",
        "domestic_yearly_stats",
        "u21_international_yearly_stats",
    ):
        root = getattr(player, attr, None) or {}
        years.update(y for y in root.keys() if isinstance(y, int) and y >= 2000)
    for e in getattr(game_engine, "league_standings_history", None) or []:
        y = e.get("year")
        if isinstance(y, int) and y >= 2000:
            years.add(y)
    cy = getattr(game_engine, "current_year", None)
    if isinstance(cy, int) and cy >= 2000:
        years.add(cy)
        if cy > 2000:
            years.add(cy - 1)
    return sorted(years)


def _best_t20_rank_over_years(
    game_engine,
    player,
    category: str,
    stats_source: str,
    tier_label: str,
    u21_only: bool,
) -> Optional[Tuple[int, int]]:
    """
    Best (numerically lowest) T20 rank for category ('Batting' / 'Bowling') in a scope.
    Returns (rank, calendar_year) or None if never ranked.
    """
    if not game_engine or not player:
        return None
    years = _calendar_years_for_rank_scan(player, game_engine)
    best_r: Optional[int] = None
    best_y: Optional[int] = None
    for y in years:
        r = player_season_rank_for_filters(
            game_engine,
            player,
            category,
            "T20",
            tier_label,
            y,
            stats_source=stats_source,
            u21_only=u21_only,
        )
        if r is None:
            continue
        if best_r is None or r < best_r:
            best_r = r
            best_y = y
        elif r == best_r and best_y is not None and y < best_y:
            best_y = y
    if best_r is None or best_y is None:
        return None
    return (best_r, best_y)


def _worst_t20_rank_over_years(
    game_engine,
    player,
    category: str,
    stats_source: str,
    tier_label: str,
    u21_only: bool,
) -> Optional[Tuple[int, int]]:
    """
    Worst (numerically highest) T20 rank among years where the player was ranked.
    Returns (rank, calendar_year) or None if never ranked.
    """
    if not game_engine or not player:
        return None
    years = _calendar_years_for_rank_scan(player, game_engine)
    worst_r: Optional[int] = None
    worst_y: Optional[int] = None
    for y in years:
        r = player_season_rank_for_filters(
            game_engine,
            player,
            category,
            "T20",
            tier_label,
            y,
            stats_source=stats_source,
            u21_only=u21_only,
        )
        if r is None:
            continue
        if worst_r is None or r > worst_r:
            worst_r = r
            worst_y = y
        elif r == worst_r and worst_y is not None and y > worst_y:
            worst_y = y
    if worst_r is None or worst_y is None:
        return None
    return (worst_r, worst_y)


def _peak_valley_yearly(
    player, stats_attr: str, fmt: str, min_m: int = 1
) -> Tuple[Optional[Tuple[int, int, int]], Optional[Tuple[int, int, int]]]:
    """
    Best/worst calendar year by total runs in that format (min matches threshold).
    Returns ((year, runs, wk), (year, runs, wk)).
    """
    root = getattr(player, stats_attr, None) or {}
    years = sorted(root.keys())
    best_r = (None, -1, -1)
    worst_r = (None, 10**9, -1)
    for y in years:
        block = root.get(y) or {}
        r, w, m = _yearly_block_totals(block, fmt)
        if m < min_m:
            continue
        if r > best_r[1]:
            best_r = (y, r, w)
        if r < worst_r[1]:
            worst_r = (y, r, w)
    peak = best_r if best_r[0] is not None else None
    worst = worst_r if worst_r[0] is not None and worst_r[1] < 10**8 else None
    return peak, worst


def _peak_valley_wickets_yearly(
    player, stats_attr: str, fmt: str, min_m: int = 1
) -> Tuple[Optional[Tuple[int, int, int]], Optional[Tuple[int, int, int]]]:
    """
    Best/worst calendar year by wickets in that format (min matches threshold).
    Returns ((year, wickets, runs), (year, wickets, runs)).
    """
    root = getattr(player, stats_attr, None) or {}
    years = sorted(root.keys())
    best_w = (None, -1, -1)
    worst_w = (None, 10**9, -1)
    for y in years:
        block = root.get(y) or {}
        r, w, m = _yearly_block_totals(block, fmt)
        if m < min_m:
            continue
        if w > best_w[1]:
            best_w = (y, w, r)
        if w < worst_w[1]:
            worst_w = (y, w, r)
    peak = best_w if best_w[0] is not None else None
    worst = worst_w if worst_w[0] is not None and worst_w[1] < 10**8 else None
    return peak, worst


def _trait_change_sentence(game_engine, ch: dict) -> str:
    """One professional sentence for a single trait_history entry (HTML fragment)."""
    ds = ch.get("season")
    cy = _season_to_calendar_year(game_engine, ds)
    yl = str(cy) if cy else f"season {ds}"
    action = (ch.get("action") or "").lower().strip()
    tr = ch.get("trait") or ""
    tname = _esc(get_trait_display_name(tr) if tr else "trait")
    pos = is_positive_trait(tr)
    neg = is_negative_trait(tr)
    lv = ch.get("level")
    lv_s = f", now at level {lv}" if lv is not None else ""

    if action in ("gained", "new", "acquired"):
        if pos or (not pos and not neg):
            return (
                f"In <strong>{_esc(yl)}</strong>, he added strength to his game by "
                f"<strong>gaining</strong> <em>{tname}</em>{_esc(lv_s)}."
            )
        return (
            f"In <strong>{_esc(yl)}</strong>, <em>{tname}</em> appeared on his profile as "
            f"a trait to manage — a weakness that surfaced in his development."
        )
    if action == "lost":
        if neg or (not pos and not neg):
            return (
                f"In <strong>{_esc(yl)}</strong>, he overcame a weakness by "
                f"<strong>removing</strong> <em>{tname}</em> from his game."
            )
        return (
            f"In <strong>{_esc(yl)}</strong>, he no longer carried <em>{tname}</em> — "
            f"a positive marker that dropped away from his identity."
        )
    if action == "level_up":
        if pos or (not pos and not neg):
            return (
                f"In <strong>{_esc(yl)}</strong>, he pushed a strength further: "
                f"<em>{tname}</em> <strong>levelled up</strong>{_esc(lv_s)}."
            )
        return (
            f"In <strong>{_esc(yl)}</strong>, <em>{tname}</em> <strong>levelled up</strong> — "
            f"a negative pattern that tightened its grip."
        )
    if action == "level_down":
        if neg or (not pos and not neg):
            return (
                f"In <strong>{_esc(yl)}</strong>, he <strong>lowered</strong> the impact of "
                f"<em>{tname}</em>{_esc(lv_s)}, easing a former weakness."
            )
        return (
            f"In <strong>{_esc(yl)}</strong>, <em>{tname}</em> <strong>levelled down</strong> — "
            f"a strength that softened slightly."
        )
    act_disp = _esc((ch.get("action") or "change").replace("_", " "))
    return (
        f"In <strong>{_esc(yl)}</strong>, his profile recorded <em>{act_disp}</em> for "
        f"<em>{tname}</em>{_esc(lv_s)}."
    )


def _scorebook_article_paragraphs(_game_engine, player) -> List[str]:
    """
    Article-style copy for calendar-year ledgers: format, runs, wickets, and year,
    plus best (peak) and worst (lean) years where data exists.
    """
    paras: List[str] = []
    scope_specs = (
        ("international_yearly_stats", "International"),
        ("domestic_yearly_stats", "Domestic"),
    )
    for stats_attr, scope_name in scope_specs:
        sentences: List[str] = []
        for fmt in ("T20", "ODI", "Test"):
            peak_r, valley_r = _peak_valley_yearly(player, stats_attr, fmt)
            peak_w, valley_w = _peak_valley_wickets_yearly(player, stats_attr, fmt)
            if peak_r is None and peak_w is None:
                continue
            parts: List[str] = []
            if peak_r is not None:
                yp, r, w = peak_r
                parts.append(
                    f"his heaviest scoring year was <strong>{yp}</strong> "
                    f"(<strong>{r}</strong> runs and <strong>{w}</strong> wickets in {fmt})"
                )
            if valley_r is not None and peak_r is not None and valley_r != peak_r:
                yv, rv, wv = valley_r
                parts.append(
                    f"his leanest year with the bat was <strong>{yv}</strong> "
                    f"({rv} runs, {wv} wickets)"
                )
            if peak_w is not None and peak_w[1] > 0:
                ywk, wk, rw = peak_w
                if peak_r is None or ywk != peak_r[0]:
                    parts.append(
                        f"with the ball, his best calendar year brought <strong>{wk}</strong> wickets "
                        f"({rw} runs) in <strong>{ywk}</strong>"
                    )
            if (
                valley_w is not None
                and peak_w is not None
                and valley_w[0] != peak_w[0]
                and peak_w[1] > 0
            ):
                yvw, wvk, rwv = valley_w
                parts.append(
                    f"his quietest year for wickets was <strong>{yvw}</strong> "
                    f"({wvk} wickets, {rwv} runs)"
                )
            if parts:
                sentences.append(
                    f"In <strong>{scope_name}</strong> {fmt}, "
                    + "; ".join(parts)
                    + "."
                )
        if sentences:
            paras.append(
                "<p><strong>Scorebook years:</strong> "
                + " ".join(sentences)
                + "</p>"
            )
    return paras


def _peak_valley_season_history(player, fmt: str) -> Tuple[Optional[dict], Optional[dict]]:
    """Best/worst season row by runs; min runs for valley among seasons with matches."""
    hist = player.season_history.get(fmt, []) or []
    cand = [h for h in hist if int(h.get("matches", 0) or 0) >= 1]
    if not cand:
        return None, None
    best = max(cand, key=lambda h: int(h.get("runs", 0) or 0))
    worst = min(cand, key=lambda h: int(h.get("runs", 0) or 0))
    return best, worst if best != worst else None


def build_career_history_article(game_engine, player, team) -> str:
    """
    Returns HTML body (multiple <p> paragraphs) for QLabel RichText.
    """
    try:
        parts: List[str] = []

        name = getattr(player, "name", "Player")
        sn = _surname(name)
        role = _esc(getattr(player, "role", "cricketer"))
        nat = _esc(getattr(player, "nationality", ""))
        age = int(getattr(player, "age", 0) or 0)
        first_season_age = _first_season_age(player, game_engine)
        if first_season_age is None:
            first_season_age = age

        pos_traits, neg_traits = _trait_buckets(player)
        pos_s = _fmt_list(pos_traits) or "well-rounded fundamentals"
        neg_s = _fmt_list(neg_traits) or "areas still being refined"

        # --- Opening: where he started ---
        started_u21 = bool(getattr(player, "is_youth_player", False)) or bool(getattr(player, "u21_career_stats", None))
        domestic_t20 = (getattr(player, "domestic_t20_club_name", "") or "").strip()
        domestic_odi = (getattr(player, "domestic_odi_fc_club_name", "") or "").strip()
        foreign_t20 = (getattr(player, "foreign_t20_club_name", "") or "").strip()

        team_label = ""
        if team:
            if getattr(team, "is_domestic", False):
                team_label = _esc(getattr(team, "name", ""))
            elif started_u21 or (getattr(player, "u21_career_stats", None) and not domestic_t20):
                team_label = f"{nat} U21 pathway" if nat else "the national youth system"
            else:
                team_label = _esc(getattr(team, "name", nat))

        opener = (
            f"<p><strong>{_esc(name)}</strong> began his career with <strong>{team_label or 'senior cricket'}</strong> "
            f"as a <strong>{role}</strong>, aged <strong>{first_season_age}</strong>. "
            f"Scouts marked his strengths in <em>{_esc(pos_s)}</em>, while noting <em>{_esc(neg_s)}</em> as facets of his game.</p>"
        )
        parts.append(opener)

        # --- Debut season (all formats from season_history) ---
        debut_sn, debut_cy = _debut_year_text(game_engine, player)
        debut_bits = []
        if debut_sn is not None:
            for fmt in ("T20", "ODI", "Test"):
                for block in player.season_history.get(fmt, []) or []:
                    if int(block.get("season", -1) or -1) != debut_sn:
                        continue
                    m = int(block.get("matches", 0) or 0)
                    if m <= 0:
                        continue
                    runs = int(block.get("runs", 0) or 0)
                    wk = int(block.get("wickets", 0) or 0)
                    debut_bits.append(f"{fmt}: {runs} runs and {wk} wickets in {m} matches")
        year_note = ""
        if debut_cy:
            year_note = f" ({debut_cy})"
        elif debut_sn is not None:
            y2 = _season_to_calendar_year(game_engine, debut_sn)
            if y2:
                year_note = f" (calendar {y2})"

        if debut_bits:
            parts.append(
                "<p>His first season on the circuit"
                f"{_esc(year_note)} brought "
                + _esc("; ".join(debut_bits))
                + " — a snapshot of a career still finding its range across formats.</p>"
            )
        else:
            parts.append(
                "<p>Match-by-match season logs are still thin; as fixtures stack up, "
                "this space will fill with debut-year numbers across T20, ODI, and Test.</p>"
            )

        # --- Progression: promotions & pathways (inferred from data) ---
        prog_bits = []
        if domestic_t20 or domestic_odi:
            clubs = []
            if domestic_t20:
                clubs.append(f"T20 ({_esc(domestic_t20)})")
            if domestic_odi:
                clubs.append(f"ODI/FC ({_esc(domestic_odi)})")
            prog_bits.append(
                "Domestic commitments have anchored his schedule: "
                + " and ".join(clubs)
                + "."
            )
        if foreign_t20:
            prog_bits.append(
                f"An overseas T20 franchise chapter opened with <strong>{_esc(foreign_t20)}</strong>, "
                "adding a second currency to his white-ball game."
            )
        intl_years = sorted((getattr(player, "international_yearly_stats", None) or {}).keys())
        dom_years = sorted((getattr(player, "domestic_yearly_stats", None) or {}).keys())
        if intl_years and dom_years:
            first_intl = intl_years[0]
            first_dom = dom_years[0]
            if first_dom < first_intl:
                prog_bits.append(
                    f"Domestic scorebooks show activity from <strong>{first_dom}</strong> before "
                    f"international ledgers ramp up (<strong>{first_intl}</strong> onward), "
                    "charting a classical pathway from county-style workload to national duty."
                )
            elif first_intl <= first_dom:
                prog_bits.append(
                    f"The international ledger begins in <strong>{first_intl}</strong>, "
                    "with domestic numbers layering in as workloads split across competitions."
                )
        if prog_bits:
            parts.append("<p>" + " ".join(prog_bits) + "</p>")

        # --- Skill evolution (skill_history) ---
        sh = list(getattr(player, "skill_history", None) or [])
        if len(sh) >= 2:
            evo = []
            for i in range(1, len(sh)):
                prev, cur = sh[i - 1], sh[i]
                ds = cur.get("season")
                cy = _season_to_calendar_year(game_engine, ds)
                ylabel = str(cy) if cy else f"season {ds}"
                db = int(cur.get("batting", 0) or 0) - int(prev.get("batting", 0) or 0)
                dl = int(cur.get("bowling", 0) or 0) - int(prev.get("bowling", 0) or 0)
                df = int(cur.get("fielding", 0) or 0) - int(prev.get("fielding", 0) or 0)
                if max(abs(db), abs(dl), abs(df)) >= 3:
                    bits = []
                    if db >= 3:
                        bits.append(f"batting +{db}")
                    elif db <= -3:
                        bits.append(f"batting {db}")
                    if dl >= 3:
                        bits.append(f"bowling +{dl}")
                    elif dl <= -3:
                        bits.append(f"bowling {dl}")
                    if df >= 3:
                        bits.append(f"fielding +{df}")
                    elif df <= -3:
                        bits.append(f"fielding {df}")
                    if bits:
                        evo.append(f"In <strong>{_esc(ylabel)}</strong>, he " + ", ".join(bits) + ".")
            if evo:
                parts.append(
                    "<p><strong>Development arcs:</strong> "
                    + " ".join(evo[:6])
                    + (" …" if len(evo) > 6 else "")
                    + "</p>"
                )

        # --- Traits timeline (professional narrative) ---
        th = sorted(
            getattr(player, "trait_history", None) or [],
            key=lambda x: (x.get("season", 0), x.get("trait", "")),
        )
        if th:
            trait_sents = [_trait_change_sentence(game_engine, ch) for ch in th[:24]]
            parts.append(
                "<p><strong>Traits and identity:</strong> "
                + " ".join(trait_sents)
                + (" …" if len(th) > 24 else "")
                + "</p>"
            )

        # --- Calendar-year scorebook (article style; peaks and lean years) ---
        for sbp in _scorebook_article_paragraphs(game_engine, player):
            parts.append(sbp)

        # --- World Cup history (nationality match) ---
        wc_lines = []
        for wc in getattr(game_engine, "world_cup_history", None) or []:
            wn = wc.get("winner") or ""
            ru = wc.get("runner_up") or ""
            yr = wc.get("year")
            tname = wc.get("tournament") or ""
            fmt = wc.get("format") or ""
            nat = getattr(player, "nationality", "") or ""
            if not nat:
                continue
            is_u21 = "U21" in str(tname).upper()
            if is_u21 and not getattr(player, "is_youth_player", False) and not getattr(player, "u21_career_stats", None):
                continue
            if wn == nat:
                wc_lines.append(
                    f"<strong>{yr}</strong> — <strong>{_esc(str(tname))}</strong> ({_esc(fmt)}): "
                    f"<em>{_esc(nat)} lifted the trophy.</em>"
                )
            elif ru == nat:
                wc_lines.append(
                    f"<strong>{yr}</strong> — <strong>{_esc(str(tname))}</strong> ({_esc(fmt)}): "
                    f"finished runner-up behind <strong>{_esc(str(wn))}</strong>."
                )
        if wc_lines:
            parts.append("<p><strong>World Cup snapshots:</strong> " + " ".join(f"{s}<br/>" for s in wc_lines) + "</p>")

        # --- Transfers / associate / return (persistent engine logs + current snapshot) ---
        orig = getattr(player, "original_team_name", None)
        if orig:
            parts.append(
                "<p>A chapter with an associate nation followed departure from "
                f"<strong>{_esc(orig)}</strong>'s Test setup — a storyline written in "
                "form slumps and opportunity abroad.</p>"
            )

        xfer_log = sorted(
            [r for r in (getattr(game_engine, "career_transfers_log", None) or []) if r.get("player") == name],
            key=lambda r: (r.get("year") or 0, r.get("season") or 0),
        )
        # Fallback: in-session rows before first save (same data as last completed season)
        if not xfer_log and game_engine:
            for row in getattr(game_engine, "season_transfers", None) or []:
                if row.get("player") != name:
                    continue
                xfer_log.append({
                    **dict(row),
                    "season": getattr(game_engine, "current_season", None),
                    "year": getattr(game_engine, "current_year", None),
                })
        for row in xfer_log:
            ys = row.get("year")
            ss = row.get("season")
            tag = f"Season {ss}" + (f", {ys}" if ys is not None else "")
            if row.get("return"):
                parts.append(
                    f"<p><strong>{_esc(tag)} — Return to Test cricket:</strong> "
                    f"<strong>{_esc(row.get('to_team', ''))}</strong> from "
                    f"<strong>{_esc(row.get('from_team', ''))}</strong> — "
                    f"{_esc(_strip_reason(row.get('reason', '')))}</p>"
                )
            else:
                parts.append(
                    f"<p><strong>{_esc(tag)} — Move to associate cricket:</strong> "
                    f"<strong>{_esc(row.get('to_team', ''))}</strong> from "
                    f"<strong>{_esc(row.get('from_team', ''))}</strong> — "
                    f"{_esc(_strip_reason(row.get('reason', '')))}</p>"
                )

        prom_log = sorted(
            [r for r in (getattr(game_engine, "career_promotions_log", None) or []) if r.get("player") == name],
            key=lambda r: (r.get("year") or 0, r.get("season") or 0),
        )
        if not prom_log and game_engine:
            for row in getattr(game_engine, "season_promotions", None) or []:
                if row.get("player") != name:
                    continue
                prom_log.append({
                    **dict(row),
                    "season": getattr(game_engine, "current_season", None),
                    "year": getattr(game_engine, "current_year", None),
                })
        for row in prom_log:
            ys = row.get("year")
            ss = row.get("season")
            tag = f"Season {ss}" + (f", {ys}" if ys is not None else "")
            parts.append(
                f"<p><strong>{_esc(tag)} — U21 to senior:</strong> Called up to "
                f"<strong>{_esc(row.get('team', ''))}</strong>'s senior squad as a "
                f"<strong>{_esc(row.get('role', ''))}</strong> (bat {_esc(row.get('batting', ''))}, "
                f"bowl {_esc(row.get('bowling', ''))}) at age {_esc(row.get('age', ''))}.</p>"
            )

        # --- T20 only: best & worst batting & bowling ranks (international / domestic / U21) ---
        if game_engine:

            def _fmt_t20_best_worst_line(best, worst) -> str:
                if not best and not worst:
                    return ""
                if best and worst and best[0] == worst[0] and best[1] == worst[1]:
                    return f"<strong>#{best[0]}</strong> ({best[1]}) — only ranked year on file"
                bits = []
                if best:
                    bits.append(f"best <strong>#{best[0]}</strong> ({best[1]})")
                if worst and (not best or worst[0] != best[0] or worst[1] != best[1]):
                    bits.append(f"worst <strong>#{worst[0]}</strong> ({worst[1]})")
                return ", ".join(bits)

            def _fmt_t20_scope_block(bat_b, bat_w, bwl_b, bwl_w) -> str:
                segs = []
                bline = _fmt_t20_best_worst_line(bat_b, bat_w)
                if bline:
                    segs.append(f"batting {bline}")
                bwline = _fmt_t20_best_worst_line(bwl_b, bwl_w)
                if bwline:
                    segs.append(f"bowling {bwline}")
                return "; ".join(segs)

            intl_bat_b = _best_t20_rank_over_years(
                game_engine, player, "Batting", "international", "All Tiers", False
            )
            intl_bat_w = _worst_t20_rank_over_years(
                game_engine, player, "Batting", "international", "All Tiers", False
            )
            intl_bwl_b = _best_t20_rank_over_years(
                game_engine, player, "Bowling", "international", "All Tiers", False
            )
            intl_bwl_w = _worst_t20_rank_over_years(
                game_engine, player, "Bowling", "international", "All Tiers", False
            )
            dom_bat_b = _best_t20_rank_over_years(
                game_engine, player, "Batting", "domestic", "All Tiers", False
            )
            dom_bat_w = _worst_t20_rank_over_years(
                game_engine, player, "Batting", "domestic", "All Tiers", False
            )
            dom_bwl_b = _best_t20_rank_over_years(
                game_engine, player, "Bowling", "domestic", "All Tiers", False
            )
            dom_bwl_w = _worst_t20_rank_over_years(
                game_engine, player, "Bowling", "domestic", "All Tiers", False
            )
            u21_bat_b = _best_t20_rank_over_years(
                game_engine, player, "Batting", "u21_international", "U21", True
            )
            u21_bat_w = _worst_t20_rank_over_years(
                game_engine, player, "Batting", "u21_international", "U21", True
            )
            u21_bwl_b = _best_t20_rank_over_years(
                game_engine, player, "Bowling", "u21_international", "U21", True
            )
            u21_bwl_w = _worst_t20_rank_over_years(
                game_engine, player, "Bowling", "u21_international", "U21", True
            )

            t20_rank_lines = []
            ib = _fmt_t20_scope_block(intl_bat_b, intl_bat_w, intl_bwl_b, intl_bwl_w)
            if ib:
                t20_rank_lines.append(f"<strong>International</strong> — {ib}")
            db = _fmt_t20_scope_block(dom_bat_b, dom_bat_w, dom_bwl_b, dom_bwl_w)
            if db:
                t20_rank_lines.append(f"<strong>Domestic</strong> — {db}")
            ub = _fmt_t20_scope_block(u21_bat_b, u21_bat_w, u21_bwl_b, u21_bwl_w)
            if ub:
                t20_rank_lines.append(f"<strong>U21</strong> — {ub}")
            if t20_rank_lines:
                parts.append(
                    "<p><strong>T20 rankings</strong> (season leaderboards by calendar year — "
                    "lower is better; <em>best</em> is the highest placement, "
                    "<em>worst</em> the lowest among years where he was ranked): "
                    + "; ".join(t20_rank_lines)
                    + ".</p>"
                )

        # --- Closing (current age, not debut age) ---
        parts.append(
            f"<p>At <strong>{age}</strong>, with <strong>{nat}</strong> still central to his story, "
            f"{sn}'s career profile updates each season as new scorecards, traits, and team sheets land — "
            "the narrative above reflects every completed season currently on file.</p>"
        )

        return "\n".join(parts)
    except Exception as e:
        return f"<p><em>Could not build career history: {_esc(str(e))}</em></p>"
