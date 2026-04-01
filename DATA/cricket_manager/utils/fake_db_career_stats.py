"""
Synthesize plausible T20 / ODI / Test career totals for fake-database players.

Core batting/bowling *per-appearance* shapes are calibrated from FastMatchSimulator
samples (see DATA/scripts/calibrate_fast_sim_stats.py): anchor profiles vs mean runs,
balls faced, wickets, and balls bowled when the player bats or bowls in a match.

Scaled by age (fewer caps when young), role weights (bat_w / bwl_w), and trait noise,
then recalculated with Player.recalculate_averages like real match aggregation.
"""
from __future__ import annotations

import copy
import random
from typing import Literal, Optional

from cricket_manager.core.player import _fresh_career_stats

# International FTP-style caps per team per season (tier_system.generate_season_series)
_MAX_T20_INTL_PER_SEASON = 22
_MAX_ODI_INTL_PER_SEASON = 22
_MAX_TEST_INTL_PER_SEASON = 12
# Typical domestic double round-robin: 6 teams -> 2*(6-1)=10; 10 teams -> 18 (use mid-range base)
_DOM_TYPICAL_MATCHES_PER_SEASON = 12


def _trait_noise_factor(player) -> float:
    traits = getattr(player, "traits", None) or []
    if not traits:
        return 1.0
    pos = neg = 0
    for t in traits:
        if isinstance(t, dict):
            name = (t.get("name") or "").upper()
            if "NEG" in name or "LIABILITY" in name or "CHOKER" in name or "WASTER" in name:
                neg += 1
            else:
                pos += 1
        else:
            pos += 1
    adj = 0.012 * (pos - neg)
    return max(0.88, min(1.12, 1.0 + adj))


def _role_bat_bowl_weights(role: str, batting: int, bowling: int) -> tuple[float, float]:
    rl = (role or "").lower()
    bw, bwl = 0.5, 0.5
    if any(
        x in rl
        for x in (
            "wicketkeeper",
            "opening batter",
            "middle order",
            "lower order",
            "batter",
        )
    ):
        bw, bwl = 0.9, 0.32
    elif any(
        x in rl
        for x in (
            "bowler",
            "spinner",
            "pace",
            "fast medium",
            "fast bowler",
            "medium pacer",
            "finger spin",
            "wrist spin",
            "leg spinner",
            "off spinner",
        )
    ):
        bw, bwl = 0.22, 0.92
    elif "allrounder" in rl:
        bw, bwl = 0.74, 0.76

    if batting > bowling + 12:
        bw = min(0.96, bw + 0.08)
        bwl = max(0.12, bwl - 0.12)
    if bowling > batting + 12:
        bwl = min(0.96, bwl + 0.08)
        bw = max(0.12, bw - 0.12)
    return bw, bwl


def _career_length_years(age: int, is_youth: bool) -> float:
    if is_youth or age < 19:
        return max(0.15, min(3.0, (age - 15) * 0.45))
    return float(max(0.8, min(age - 19, 18)))


def _format_match_splits_intl_domestic(
    age: int, is_youth: bool, rng: random.Random, intl_weight: float
) -> tuple[dict[str, int], dict[str, int]]:
    """
    International + domestic career match counts from season structure:
    intl caps (22/22/12 per year) plus ~12 domestic games per format per year (double RR).
    intl_weight ~1.0 for full internationals, ~0.06–0.15 for domestic-club-only players.
    """
    yrs = _career_length_years(age, is_youth)
    scale = 0.35 if is_youth else 1.0
    iw = max(0.0, min(1.0, float(intl_weight)))
    dom_boost = rng.uniform(1.02, 1.22) if iw < 0.2 else 1.0

    def one_format(intl_cap: int, dom_base: int, cap_total: int) -> tuple[int, int]:
        intl_per_yr = intl_cap * rng.uniform(0.28, 0.72) * iw
        dom_per_yr = dom_base * rng.uniform(0.52, 0.94) * dom_boost
        mi = int(scale * yrs * intl_per_yr * rng.uniform(0.9, 1.08))
        md = int(scale * yrs * dom_per_yr * rng.uniform(0.9, 1.08))
        mi = max(0, min(mi, cap_total))
        md = max(0, min(md, cap_total))
        return mi, md

    t20_i, t20_d = one_format(_MAX_T20_INTL_PER_SEASON, _DOM_TYPICAL_MATCHES_PER_SEASON + 2, 320)
    odi_i, odi_d = one_format(_MAX_ODI_INTL_PER_SEASON, _DOM_TYPICAL_MATCHES_PER_SEASON, 280)
    tst_i, tst_d = one_format(_MAX_TEST_INTL_PER_SEASON, _DOM_TYPICAL_MATCHES_PER_SEASON, 220)

    intl = {"T20": t20_i, "ODI": odi_i, "Test": tst_i}
    dom = {"T20": t20_d, "ODI": odi_d, "Test": tst_d}
    return intl, dom


def _merge_intl_dom_career(intl_stats: dict, dom_stats: dict) -> dict:
    """Sum international + domestic buckets into combined career (player.stats)."""
    out = _fresh_career_stats()
    for fmt in ("T20", "ODI", "Test"):
        a = intl_stats[fmt]
        b = dom_stats[fmt]
        out[fmt]["matches"] = int(a.get("matches", 0) + b.get("matches", 0))
        out[fmt]["runs"] = int(a.get("runs", 0) + b.get("runs", 0))
        out[fmt]["balls_faced"] = int(a.get("balls_faced", 0) + b.get("balls_faced", 0))
        out[fmt]["wickets"] = int(a.get("wickets", 0) + b.get("wickets", 0))
        out[fmt]["balls_bowled"] = int(a.get("balls_bowled", 0) + b.get("balls_bowled", 0))
        out[fmt]["runs_conceded"] = int(a.get("runs_conceded", 0) + b.get("runs_conceded", 0))
        out[fmt]["centuries"] = int(a.get("centuries", 0) + b.get("centuries", 0))
        out[fmt]["fifties"] = int(a.get("fifties", 0) + b.get("fifties", 0))
        out[fmt]["five_wickets"] = int(a.get("five_wickets", 0) + b.get("five_wickets", 0))
        out[fmt]["highest_score"] = max(a.get("highest_score", 0), b.get("highest_score", 0))
        if fmt == "Test":
            out[fmt]["innings"] = int(a.get("innings", 0) + b.get("innings", 0))
            out[fmt]["dismissals"] = int(a.get("dismissals", 0) + b.get("dismissals", 0))
            out[fmt]["ten_wickets"] = int(a.get("ten_wickets", 0) + b.get("ten_wickets", 0))
    return out


def _format_matches(age: int, is_youth: bool, rng: random.Random) -> dict[str, int]:
    yrs = _career_length_years(age, is_youth)
    scale = 0.35 if is_youth else 1.0
    t20 = int(scale * (rng.uniform(2, 8) + yrs * rng.uniform(4, 10)))
    odi = int(scale * (rng.uniform(1, 5) + yrs * rng.uniform(2, 6)))
    tst = int(scale * (rng.uniform(0, 2) + yrs * rng.uniform(0.8, 2.4)))
    return {
        "T20": max(0, min(t20, 220)),
        "ODI": max(0, min(odi, 180)),
        "Test": max(0, min(tst, 110)),
    }


def _strike_rate_t20(batting: int, rng: random.Random) -> float:
    base = 108.0 + (max(20, min(100, batting)) - 50) * 0.55
    return max(95.0, min(175.0, base + rng.uniform(-6, 6)))


def _strike_rate_odi(batting: int, rng: random.Random) -> float:
    base = 78.0 + (max(20, min(100, batting)) - 50) * 0.28
    return max(65.0, min(115.0, base + rng.uniform(-4, 4)))


def _strike_rate_test(batting: int, rng: random.Random) -> float:
    base = 42.0 + (max(20, min(100, batting)) - 50) * 0.18
    return max(28.0, min(62.0, base + rng.uniform(-3, 3)))


def _expected_batting_avg_test(batting: int, rng: random.Random) -> float:
    base = 22.0 + (max(25, min(98, batting)) - 50) * 0.42
    return max(14.0, min(58.0, base + rng.uniform(-2.5, 2.5)))


def _expected_batting_avg_limited(batting: int, fmt: str, rng: random.Random) -> float:
    if fmt == "T20":
        base = 18.0 + (max(25, min(98, batting)) - 50) * 0.35
        return max(10.0, min(48.0, base + rng.uniform(-2, 2)))
    base = 26.0 + (max(25, min(98, batting)) - 50) * 0.38
    return max(15.0, min(52.0, base + rng.uniform(-2.5, 2.5)))


def _expected_bowling_avg(bowling: int, rng: random.Random) -> float:
    base = 38.0 - (max(15, min(98, bowling)) - 50) * 0.32
    return max(16.0, min(52.0, base + rng.uniform(-3, 3)))


def _expected_economy_t20(bowling: int, rng: random.Random) -> float:
    base = 8.4 - (max(15, min(98, bowling)) - 50) * 0.038
    return max(5.8, min(11.5, base + rng.uniform(-0.35, 0.35)))


def _expected_economy_odi(bowling: int, rng: random.Random) -> float:
    base = 5.5 - (max(15, min(98, bowling)) - 50) * 0.022
    return max(3.8, min(7.2, base + rng.uniform(-0.25, 0.25)))


def _expected_economy_test(bowling: int, rng: random.Random) -> float:
    base = 3.25 - (max(15, min(98, bowling)) - 50) * 0.018
    return max(2.2, min(4.8, base + rng.uniform(-0.2, 0.2)))


def _clamp_skill(v: int) -> int:
    return max(20, min(100, int(v)))


def _cal_t20_runs_balls_when_batting(bat: int) -> tuple[float, float]:
    """Piecewise linear fit to fast sim (when player faces balls in a T20)."""
    b = _clamp_skill(bat)
    runs = max(0.0, 0.682 * b - 18.7)
    if b <= 55:
        balls = 0.435 * b - 10.925
    else:
        balls = 0.339 * b - 5.645
    balls = max(1.0, balls) if runs > 0 else max(0.0, balls)
    return runs, balls


def _cal_odi_runs_balls_when_batting(bat: int) -> tuple[float, float]:
    b = _clamp_skill(bat)
    if b <= 55:
        runs = max(0.0, 1.11 * (b - 35) + 9.7)
        balls = max(1.0, 0.905 * (b - 35) + 12.1) if runs > 0 else max(0.0, 0.905 * (b - 35) + 12.1)
    else:
        runs = max(0.0, 0.594 * (b - 55) + 31.9)
        balls = max(1.0, 0.382 * (b - 55) + 30.2) if runs > 0 else max(0.0, 0.382 * (b - 55) + 30.2)
    return runs, balls


def _cal_test_runs_balls_per_match_when_batting(bat: int) -> tuple[float, float]:
    """One Test match aggregate when player batted (fast sim match_stats totals)."""
    b = _clamp_skill(bat)
    if b <= 55:
        runs = max(0.0, 0.265 * (b - 35) + 18.9)
        balls = max(1.0, 0.14 * (b - 35) + 39.6) if runs > 0 else max(0.0, 0.14 * (b - 35) + 39.6)
    else:
        runs = max(0.0, 1.936 * (b - 55) + 24.2)
        balls = max(1.0, (114.4 - 42.4) / (88 - 55) * (b - 55) + 42.4) if runs > 0 else max(
            0.0, (114.4 - 42.4) / (88 - 55) * (b - 55) + 42.4
        )
    return runs, balls


def _cal_t20_wkts_bballs_when_bowling(bowl: int) -> tuple[float, float]:
    b = _clamp_skill(bowl)
    wkts = max(0.0, min(5.0, 0.0268 * b - 0.65))
    bballs = max(0.0, 0.186 * (b - 55) + 17.4)
    return wkts, bballs


def _cal_odi_wkts_bballs_when_bowling(bowl: int) -> tuple[float, float]:
    b = _clamp_skill(bowl)
    wkts = max(0.0, min(6.0, 0.0115 * b + 0.747))
    bballs = max(0.0, 0.15 * (b - 55) + 42.1)
    return wkts, bballs


def _cal_test_wkts_bballs_when_bowling(bowl: int) -> tuple[float, float]:
    b = _clamp_skill(bowl)
    wkts = max(0.0, min(9.0, 0.076 * b - 1.81))
    bballs = max(0.0, min(140.0, 0.037 * (b - 55) + 117.0))
    return wkts, bballs


def _cal_econ_t20_from_sim(bowl: int) -> float:
    b = _clamp_skill(bowl)
    return max(5.8, min(11.5, 9.4 - 0.022 * b))


def _cal_econ_odi_from_sim(bowl: int) -> float:
    b = _clamp_skill(bowl)
    return max(3.8, min(7.2, 6.35 - 0.012 * b))


def _cal_econ_test_from_sim(bowl: int) -> float:
    b = _clamp_skill(bowl)
    return max(2.2, min(4.8, 3.85 - 0.012 * b))


def _bat_skill_role_factor(bat: int, bat_w: float) -> float:
    """0..1 from batting attribute and batting-role weight."""
    s = max(0.0, min(1.0, (bat - 28) / 68.0))
    w = max(0.18, min(1.0, bat_w)) ** 0.5
    return s * w


def _batting_milestones_limited(
    fmt: str,
    runs: int,
    bat_games: int,
    bat: int,
    bat_w: float,
    rng: random.Random,
) -> tuple[int, int]:
    """
    Centuries (100+) and fifties (50–99 only), at most one per batting innings proxy.
    Driven by innings, runs/innings, skill and role — not arbitrary run fractions.
    """
    if bat_games <= 0 or runs <= 0:
        return 0, 0
    inn = bat_games
    avg = runs / float(inn)
    f = _bat_skill_role_factor(bat, bat_w)

    if fmt == "T20":
        p100 = min(0.018, 0.00035 + 0.012 * f * (avg / 30.0) ** 1.35)
        p50_only = 0.010 + 0.095 * f * (avg / 28.0) ** 1.08
    else:
        p100 = min(0.065, 0.0055 + 0.038 * f * (avg / 34.0) ** 1.18)
        p50_only = 0.028 + 0.13 * f * (avg / 31.0) ** 1.05

    p50_only = max(0.0, min(p50_only, max(0.0, 0.97 - p100)))
    p100 = max(0.0, min(p100, 0.45))

    cent = fifties_cnt = 0
    for _ in range(inn):
        u = rng.random()
        if u < p100:
            cent += 1
        elif u < p100 + p50_only:
            fifties_cnt += 1

    cent = min(cent, inn, max(0, runs // 97))
    fifties_cnt = min(
        fifties_cnt, max(0, inn - cent), max(0, (runs - 100 * cent) // 51)
    )
    return cent, fifties_cnt


def _batting_milestones_test(
    runs: int,
    innings: int,
    bat: int,
    bat_w: float,
    rng: random.Random,
) -> tuple[int, int]:
    if innings <= 0 or runs <= 0:
        return 0, 0
    avg = runs / float(innings)
    sk = _bat_skill_role_factor(bat, bat_w)
    p100 = min(0.048, 0.0016 + 0.026 * sk * (avg / 27.0) ** 1.12)
    p50_only = 0.022 + 0.10 * sk * (avg / 25.0) ** 1.02
    p50_only = max(0.0, min(p50_only, max(0.0, 0.96 - p100)))

    cent = f50 = 0
    for _ in range(innings):
        u = rng.random()
        if u < p100:
            cent += 1
        elif u < p100 + p50_only:
            f50 += 1

    cent = min(cent, innings, max(0, runs // 97))
    f50 = min(f50, max(0, innings - cent), max(0, (runs - 100 * cent) // 51))
    return cent, f50


def _highest_score_support_milestones(
    fmt: str,
    base_hs: int,
    centuries: int,
    fifties: int,
    rng: random.Random,
) -> int:
    """Ensure HS is consistent with at least one 50+ score when milestones exist."""
    cap = 130 if fmt == "T20" else (200 if fmt == "ODI" else 334)
    hs = max(0, min(cap, base_hs))
    if centuries > 0:
        hs = max(hs, min(cap, 100 + int(rng.uniform(0, min(95, cap - 100)))))
    elif fifties > 0:
        top = min(cap, 99) if fmt != "Test" else min(cap, 190)
        hs = max(hs, min(top, 50 + int(rng.uniform(0, min(49, top - 50)))))
    return max(1, hs) if (centuries > 0 or fifties > 0 or hs > 0) else hs


def _fill_limited_format(
    player,
    fmt: str,
    m: int,
    bat_w: float,
    bwl_w: float,
    rng: random.Random,
    tf: float,
    stats_root: Optional[dict] = None,
) -> None:
    if m <= 0:
        return
    root = stats_root if stats_root is not None else player.stats
    st = root[fmt]
    bat = max(1, min(100, getattr(player, "batting", 50) or 50))
    bowl = max(1, min(100, getattr(player, "bowling", 50) or 50))

    bat_games = max(0, int(m * bat_w * rng.uniform(0.55, 1.0) * tf))
    bowl_games = max(0, int(m * bwl_w * rng.uniform(0.55, 1.0) * tf))

    if fmt == "T20":
        rpg, bpg = _cal_t20_runs_balls_when_batting(bat)
    else:
        rpg, bpg = _cal_odi_runs_balls_when_batting(bat)

    br = rng.uniform(0.88, 1.12) * tf
    bb = rng.uniform(0.88, 1.1) * tf
    runs = int(bat_games * rpg * br) if bat_games else 0
    balls_faced = int(bat_games * bpg * bb) if bat_games else 0
    if bat_games > 0 and runs < int(bat_games * rpg * 0.38):
        runs = int(bat_games * rpg * rng.uniform(0.62, 0.98) * tf)
    if balls_faced > 0 and runs > 0:
        sr_now = 100.0 * runs / balls_faced
        cap = 198.0 if fmt == "T20" else 128.0
        if sr_now > cap:
            balls_faced = max(1, int(runs * 100.0 / cap))

    st["balls_faced"] = balls_faced
    st["runs"] = runs
    st["matches"] = m

    wkts = 0
    balls_bowled = 0
    runs_conc = 0
    if bowl_games > 0 and bowl > 22:
        if fmt == "T20":
            wpg, bbpg = _cal_t20_wkts_bballs_when_bowling(bowl)
            econ = _cal_econ_t20_from_sim(bowl)
        else:
            wpg, bbpg = _cal_odi_wkts_bballs_when_bowling(bowl)
            econ = _cal_econ_odi_from_sim(bowl)
        wkts = int(bowl_games * wpg * rng.uniform(0.82, 1.12) * tf)
        wkts = max(0, min(wkts, bowl_games * 5))
        balls_bowled = int(bowl_games * bbpg * rng.uniform(0.85, 1.08))
        runs_conc_econ = int((balls_bowled / 6.0) * econ * rng.uniform(0.92, 1.08))
        runs_conc = max(int(wkts * 9 + rng.randint(0, 18)), runs_conc_econ)

    st["wickets"] = wkts
    st["balls_bowled"] = balls_bowled
    st["runs_conceded"] = runs_conc

    if runs > 0:
        hs_cap = 130 if fmt == "T20" else 200
        base_hs = min(
            hs_cap,
            max(1, int((runs / max(1, bat_games)) * rng.uniform(1.2, 2.35))),
        )
    else:
        base_hs = 0
    cent, f50 = _batting_milestones_limited(fmt, runs, bat_games, bat, bat_w, rng)
    st["centuries"] = cent
    st["fifties"] = f50
    if runs > 0:
        st["highest_score"] = _highest_score_support_milestones(
            fmt, base_hs, cent, f50, rng
        )
    if wkts >= 5:
        st["five_wickets"] = min(m, max(0, wkts // 6 + rng.randint(0, 1)))

    player._recalculate_averages_for_stats_dict(st, fmt)


def _fill_test_format(
    player,
    m: int,
    bat_w: float,
    bwl_w: float,
    rng: random.Random,
    tf: float,
    stats_root: Optional[dict] = None,
) -> None:
    if m <= 0:
        return
    root = stats_root if stats_root is not None else player.stats
    st = root["Test"]
    bat = max(1, min(100, getattr(player, "batting", 50) or 50))
    bowl = max(1, min(100, getattr(player, "bowling", 50) or 50))

    innings = max(1, int(m * rng.uniform(1.55, 2.15) * bat_w * tf))
    dismissals = max(1, int(innings * rng.uniform(0.78, 0.96)))
    rpg, bpg = _cal_test_runs_balls_per_match_when_batting(bat)
    runs = int(m * bat_w * rpg * rng.uniform(0.88, 1.1) * tf)
    sr_cal = 100.0 * rpg / bpg if bpg > 0 else 50.0
    balls_faced = int(max(runs * 100.0 / max(sr_cal, 30.0), dismissals * 22))

    st["matches"] = m
    st["innings"] = innings
    st["dismissals"] = dismissals
    st["runs"] = runs
    st["balls_faced"] = balls_faced

    bowl_inns = max(0, int(m * 1.55 * bwl_w * rng.uniform(0.65, 1.0) * tf))
    wkts = 0
    balls_bowled = 0
    runs_conc = 0
    if bowl_inns > 0 and bowl > 22:
        wpg, _bbpg_unused = _cal_test_wkts_bballs_when_bowling(bowl)
        wkts = int(m * bwl_w * wpg * rng.uniform(0.82, 1.1) * tf)
        wkts = max(0, min(wkts, bowl_inns * 8))
        if wkts > 0:
            raw_avg = _expected_bowling_avg(bowl, rng)
            tavg = max(24.0, min(36.0, raw_avg + rng.uniform(-1.5, 2.5)))
            if bowl >= 82:
                tavg = max(22.0, min(32.0, tavg - rng.uniform(0, 3)))
            runs_conc = int(wkts * tavg * rng.uniform(0.95, 1.08))
            tecon = max(2.45, min(3.75, _cal_econ_test_from_sim(bowl) * rng.uniform(0.94, 1.06)))
            balls_bowled = int(max(runs_conc / tecon * 6.0, wkts * 50.0))
            overs = balls_bowled / 6.0
            econ_now = runs_conc / overs if overs > 0 else tecon
            if econ_now > 3.85:
                balls_bowled = int(max(wkts * 50, runs_conc / 3.75 * 6.0))
            elif econ_now < 2.35:
                runs_conc = int(max(runs_conc, overs * 2.35))
        else:
            balls_bowled = 0
            runs_conc = 0
    else:
        balls_bowled = 0
        runs_conc = 0

    st["wickets"] = wkts
    st["balls_bowled"] = balls_bowled
    st["runs_conceded"] = runs_conc

    if runs > 0:
        base_hs = min(334, max(1, int((runs / max(1, dismissals)) * rng.uniform(1.05, 2.15))))
    else:
        base_hs = 0
    cent, f50 = _batting_milestones_test(runs, innings, bat, bat_w, rng)
    st["centuries"] = cent
    st["fifties"] = f50
    if runs > 0:
        st["highest_score"] = _highest_score_support_milestones(
            "Test", base_hs, cent, f50, rng
        )
    if wkts >= 5:
        st["five_wickets"] = min(m * 2, max(0, wkts // 7 + rng.randint(0, 2)))
    if wkts >= 10:
        st["ten_wickets"] = max(0, min(3, wkts // 25))

    player._recalculate_averages_for_stats_dict(st, "Test")


def _mirror_stats_to_split(player, scope: Literal["international", "domestic"]) -> None:
    snap = copy.deepcopy(
        {
            "T20": dict(player.stats["T20"]),
            "ODI": dict(player.stats["ODI"]),
            "Test": dict(player.stats["Test"]),
        }
    )
    if scope == "international" and getattr(player, "international_stats", None) is not None:
        for fmt in ("T20", "ODI", "Test"):
            player.international_stats[fmt] = copy.deepcopy(snap[fmt])
    elif scope == "domestic" and getattr(player, "domestic_stats", None) is not None:
        for fmt in ("T20", "ODI", "Test"):
            player.domestic_stats[fmt] = copy.deepcopy(snap[fmt])


def _seed_season_and_form(player, rng: random.Random) -> None:
    """Light-touch season_stats and last-5 form from career shape."""
    for fmt in ("T20", "ODI", "Test"):
        st = player.stats.get(fmt) or {}
        m = int(st.get("matches") or 0)
        r = int(st.get("runs") or 0)
        w = int(st.get("wickets") or 0)
        frac = rng.uniform(0.08, 0.22)
        ss = player.season_stats.setdefault(
            fmt,
            {
                "runs": 0,
                "wickets": 0,
                "matches": 0,
                "balls_faced": 0,
                "balls_bowled": 0,
                "runs_conceded": 0,
                "centuries": 0,
                "fifties": 0,
                "five_wickets": 0,
                "highest_score": 0,
            },
        )
        sm = max(0, int(m * frac))
        ss["matches"] = sm
        ss["runs"] = int(r * frac * rng.uniform(0.85, 1.15)) if r else 0
        ss["wickets"] = int(w * frac * rng.uniform(0.85, 1.15)) if w else 0
        ss["balls_faced"] = int((st.get("balls_faced") or 0) * frac * rng.uniform(0.85, 1.12))
        ss["balls_bowled"] = int((st.get("balls_bowled") or 0) * frac * rng.uniform(0.85, 1.12))
        ss["runs_conceded"] = int((st.get("runs_conceded") or 0) * frac * rng.uniform(0.85, 1.12))
        if ss["runs"] > 0:
            ss["highest_score"] = min(
                st.get("highest_score") or ss["runs"],
                max(ss["runs"] // max(1, sm // 2 or 1), int(ss["runs"] * 0.35)),
            )

    if rng.random() < 0.75:
        player.last_5_batting = [max(0, int(rng.gauss(28, 22))) for _ in range(5)]
    if rng.random() < 0.65:
        player.last_5_bowling = [max(0, min(6, int(rng.gauss(1.2, 1.1)))) for _ in range(5)]


def synthesize_fake_career_stats(
    player,
    rng: Optional[random.Random] = None,
    *,
    career_scope: Literal["international", "domestic"] = "international",
    intl_weight: Optional[float] = None,
    include_international_stats: bool = True,
) -> None:
    """
    Fill international_stats and domestic_stats from season-shaped match volumes, then
    merge into player.stats (combined = intl + dom), matching live play rules.

    include_international_stats: when False, international_stats stay zero and only
    domestic volumes are synthesized (player.stats equals domestic career).

    intl_weight: fraction of FTP caps played (default 1.0 for national players, ~0.08
    for domestic-only club players). career_scope selects the default when omitted;
    ignored (treated as 0) when include_international_stats is False.
    """
    if not include_international_stats:
        intl_w = 0.0
    else:
        intl_w = intl_weight if intl_weight is not None else (
            1.0 if career_scope == "international" else 0.09
        )

    intl_stats = _fresh_career_stats()
    dom_stats = _fresh_career_stats()
    player.stats = _fresh_career_stats()

    rng = rng or random.Random()
    seed = (hash(getattr(player, "name", "")) ^ id(player)) & 0xFFFFFFFF
    rng = random.Random(seed ^ rng.randint(0, 10_000_000))

    age = max(16, min(48, getattr(player, "age", 24) or 24))
    is_youth = bool(getattr(player, "is_youth_player", False)) or age < 22
    bat_w, bwl_w = _role_bat_bowl_weights(
        getattr(player, "role", "") or "",
        int(getattr(player, "batting", 50) or 50),
        int(getattr(player, "bowling", 50) or 50),
    )
    tf = _trait_noise_factor(player)

    intl_counts, dom_counts = _format_match_splits_intl_domestic(age, is_youth, rng, intl_w)
    for fmt in ("T20", "ODI"):
        _fill_limited_format(player, fmt, intl_counts[fmt], bat_w, bwl_w, rng, tf, stats_root=intl_stats)
        _fill_limited_format(player, fmt, dom_counts[fmt], bat_w, bwl_w, rng, tf, stats_root=dom_stats)
    _fill_test_format(player, intl_counts["Test"], bat_w, bwl_w, rng, tf, stats_root=intl_stats)
    _fill_test_format(player, dom_counts["Test"], bat_w, bwl_w, rng, tf, stats_root=dom_stats)

    player.international_stats = copy.deepcopy(intl_stats)
    player.domestic_stats = copy.deepcopy(dom_stats)
    player.stats = _merge_intl_dom_career(intl_stats, dom_stats)
    for fmt in ("T20", "ODI", "Test"):
        player.recalculate_averages(fmt)

    _seed_season_and_form(player, rng)


def clear_fake_db_career_history(player) -> None:
    """Clear yearly / milestone history after synthetic totals (keeps player.stats)."""
    player.yearly_stats = {}
    player.international_yearly_stats = {}
    player.domestic_yearly_stats = {}
    player.season_history = {"T20": [], "ODI": [], "Test": []}
    player.skill_history = []
    player.trait_history = []
    player.milestones = []
