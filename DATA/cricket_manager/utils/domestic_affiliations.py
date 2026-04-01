"""
Domestic club names for player profiles (T20 vs ODI/FC sides).
Uses DomesticSystem.competitions_by_nation when available; synthetic labels otherwise.

National senior squads: home T20 + home ODI/FC always. The top 7–8 players by skill
per nation may also get an extra overseas T20 franchise (display only).
"""

import hashlib
import random


def _club_label(obj):
    """Competition lists may be Team instances or plain names."""
    if obj is None:
        return ""
    if hasattr(obj, "name"):
        return obj.name
    return str(obj)


# When no multi-nation T20 data exists, use generic overseas labels (deterministic pick per player).
_FALLBACK_FOREIGN_T20_LABELS = (
    "Overseas T20 franchise (CPL)",
    "Overseas T20 franchise (BBL)",
    "Overseas T20 franchise (The Hundred)",
    "Overseas T20 franchise (ILT20)",
    "Overseas T20 franchise (SA20)",
    "Overseas T20 franchise (Global League)",
)


def pick_affiliations_for_nation(nation, player_name, competitions_by_nation):
    """
    Return (t20_club_name, odi_fc_club_name) for an international-list player.
    Deterministic per (nation, player_name) so saves stay stable.
    """
    seed = hash((nation or "", player_name or "")) & 0xFFFFFFFF
    rng = random.Random(seed)
    data = competitions_by_nation.get(nation) if competitions_by_nation else None
    if not data:
        return (
            f"{nation} (T20 domestic)",
            f"{nation} (ODI / First-Class)",
        )
    t20_names = []
    if "T20" in data:
        _, teams = data["T20"]
        t20_names = [_club_label(x) for x in teams]
    odi_names = []
    if "ODI" in data:
        _, teams = data["ODI"]
        odi_names = [_club_label(x) for x in teams]
    if not odi_names and "Test" in data:
        _, teams = data["Test"]
        odi_names = [_club_label(x) for x in teams]
    if not t20_names:
        t20_names = [f"{nation} T20"]
    if not odi_names:
        odi_names = [f"{nation} FC / List A"]
    t20_pick = rng.choice(t20_names)
    odi_pick = rng.choice(odi_names)
    if t20_pick == odi_pick:
        alts = [x for x in t20_names if x != odi_pick]
        if alts:
            t20_pick = rng.choice(alts)
    return (t20_pick, odi_pick)


def pick_affiliations_for_domestic_squad_player(player, domestic_team, competitions_by_nation):
    """
    Player plays for a domestic club Team: set the matching-format club to that team,
    and pick the other format's club from the same nation's competitions.
    """
    nation = getattr(domestic_team, "parent_nation", None) or getattr(player, "nationality", None)
    fmt = getattr(domestic_team, "domestic_format", "T20")
    label = _club_label(getattr(domestic_team, "name", domestic_team))
    # One squad for T20 + ODI + FC: same club name for both profile slots
    if fmt == "Multi":
        return (label, label)
    player_nat = (getattr(player, "nationality", None) or "").strip()
    host_nat = (nation or "").strip()
    # Overseas player on a franchise (e.g. IPL): home T20 + home ODI/FC from their real country
    if player_nat and host_nat and player_nat != host_nat:
        return pick_affiliations_for_nation(
            player_nat,
            getattr(player, "name", "player") or "player",
            competitions_by_nation or {},
        )
    t20_pick, odi_pick = pick_affiliations_for_nation(
        nation,
        getattr(player, "name", "player") or "player",
        competitions_by_nation or {},
    )
    if fmt == "T20":
        return (label, odi_pick)
    if fmt in ("ODI", "Test"):
        return (t20_pick, label)
    return (t20_pick, odi_pick)


def set_franchise_squad_player_domestic_labels(
    player, franchise_club_name: str, host_nation: str, competitions_by_nation: dict
) -> None:
    """
    After creating a player for a T20 franchise squad (save patch or tools):
    local players get franchise as home T20 side; overseas get both slots from their nationality.
    """
    hn = (host_nation or "").strip()
    pnat = (getattr(player, "nationality", None) or "").strip()
    comps = competitions_by_nation or {}
    if pnat and hn and pnat != hn:
        t20, odi = pick_affiliations_for_nation(pnat, getattr(player, "name", "") or "player", comps)
        player.domestic_t20_club_name = t20
        player.domestic_odi_fc_club_name = odi
    else:
        _, odi_pick = pick_affiliations_for_nation(hn, getattr(player, "name", "") or "player", comps)
        player.domestic_t20_club_name = franchise_club_name
        player.domestic_odi_fc_club_name = odi_pick


def _t20_side_labels_from_comp_data(data):
    """Extract display names from competitions_by_nation T20 entry (Team objects or strings)."""
    if not data or "T20" not in data:
        return []
    _, teams = data["T20"]
    return [_club_label(x) for x in teams]


def foreign_t20_options_excluding_nation(competitions_by_nation, host_nation):
    """All T20 club names from nations other than host_nation (for overseas franchise display)."""
    labels = []
    if competitions_by_nation:
        for nat, fmts in competitions_by_nation.items():
            if nat == host_nation:
                continue
            labels.extend(_t20_side_labels_from_comp_data(fmts))
    if not labels:
        labels = list(_FALLBACK_FOREIGN_T20_LABELS)
    return labels


def pick_foreign_t20_franchise(host_nation, player_name, competitions_by_nation):
    """Stable overseas T20 franchise label for elite national-team players."""
    options = foreign_t20_options_excluding_nation(competitions_by_nation or {}, host_nation)
    seed = hash((host_nation or "", player_name or "", "foreign_t20_v1")) & 0xFFFFFFFF
    rng = random.Random(seed)
    return rng.choice(options)


def _national_elite_skill_score(player):
    return max(getattr(player, "batting", 0), getattr(player, "bowling", 0)) + getattr(
        player, "fielding", 0
    ) * 0.3


def elite_foreign_t20_slots_for_team(team_name):
    """7 or 8 slots per nation, stable for that team name (not PYTHONHASHSEED-dependent)."""
    h = hashlib.md5((team_name or "").encode("utf-8")).hexdigest()
    return 7 + (int(h[-1], 16) % 2)


def assign_foreign_t20_elite_national_squads(all_teams, domestic_teams, competitions_by_nation):
    """
    National senior squads: top 7–8 by skill get foreign_t20_club_name; everyone else cleared.
    Domestic-club and U21 players never get an overseas T20 row.
    """
    domestic_teams = domestic_teams or []
    for dt in domestic_teams:
        for p in getattr(dt, "players", None) or []:
            if hasattr(p, "foreign_t20_club_name"):
                p.foreign_t20_club_name = ""
    for team in all_teams or []:
        for p in getattr(team, "u21_squad", None) or []:
            if hasattr(p, "foreign_t20_club_name"):
                p.foreign_t20_club_name = ""
        seniors = list(getattr(team, "players", None) or [])
        for p in seniors:
            if hasattr(p, "foreign_t20_club_name"):
                p.foreign_t20_club_name = ""
        if not seniors:
            continue
        nation = getattr(team, "name", None) or ""
        slots = elite_foreign_t20_slots_for_team(nation)
        slots = min(slots, len(seniors))
        ranked = sorted(seniors, key=_national_elite_skill_score, reverse=True)
        elite = set(ranked[:slots])
        for p in elite:
            p.foreign_t20_club_name = pick_foreign_t20_franchise(nation, getattr(p, "name", ""), competitions_by_nation)
