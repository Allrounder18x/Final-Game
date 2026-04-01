"""One-off: sample FastMatchSimulator outputs by skill profile (not imported by game)."""
from __future__ import annotations

import os
import random
import statistics
import sys

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)

from cricket_manager.core.fast_match_simulator import FastMatchSimulator
from cricket_manager.core.player import Player
from cricket_manager.core.team import Team


def _adj():
    return {
        "dot_adj": 0,
        "boundary_adj": 0,
        "wicket_adj": 0,
        "difficulty_bat": 1.0,
        "difficulty_bowl": 1.0,
    }


def make_player(name: str, bat: int, bowl: int, role: str) -> Player:
    p = Player(name, 26, role, "Calib")
    p.batting = bat
    p.bowling = bowl
    p.fielding = 55
    return p


def random_filler(prefix: str, i: int) -> Player:
    p = Player(f"{prefix}{i}", 24 + (i % 9), "Middle Order Batter", "Calib")
    p.batting = random.randint(38, 72)
    p.bowling = random.randint(38, 72)
    p.fielding = 50
    return p


def run_block(fmt: str, anchor: Player, n: int) -> list[dict]:
    rows = []
    pname = anchor.name
    for k in range(n):
        t1 = Team(name="SideA", tier=2)
        t2 = Team(name="SideB", tier=2)
        if k % 2 == 0:
            t1.players = [anchor] + [random_filler("A", i) for i in range(10)]
            t2.players = [random_filler("B", i) for i in range(11)]
        else:
            t2.players = [anchor] + [random_filler("B", i) for i in range(10)]
            t1.players = [random_filler("A", i) for i in range(11)]
        sim = FastMatchSimulator(t1, t2, fmt, simulation_adjustments=_adj())
        sim.simulate()
        sc = sim.get_scorecard()
        ms = sc.get("match_stats", {}).get(pname)
        if not ms:
            continue
        b = ms.get("batting") or {}
        bw = ms.get("bowling") or {}
        rows.append(
            {
                "runs": int(b.get("runs") or 0),
                "balls": int(b.get("balls") or 0),
                "dismissals": int(b.get("dismissals") or 0),
                "wkts": int(bw.get("wickets") or 0),
                "bballs": int(bw.get("balls") or 0),
                "bruns": int(bw.get("runs") or 0),
            }
        )
    return rows


def summarize(label: str, rows: list[dict]) -> None:
    if not rows:
        print(f"  {label}: no rows")
        return

    def mean(xs):
        return statistics.mean(xs) if xs else 0.0

    runs = [r["runs"] for r in rows]
    balls = [r["balls"] for r in rows]
    wkts = [r["wkts"] for r in rows]
    bballs = [r["bballs"] for r in rows]
    bruns = [r["bruns"] for r in rows]
    dismissed = sum(1 for r in rows if r["dismissals"] > 0)
    batted = sum(1 for r in rows if r["balls"] > 0)
    bowled = sum(1 for r in rows if r["bballs"] > 0)

    sr = [100.0 * r["runs"] / r["balls"] for r in rows if r["balls"] > 0]
    econ = [(6 * r["bruns"] / r["bballs"]) for r in rows if r["bballs"] > 0]
    bavg = [(r["bruns"] / r["wkts"]) for r in rows if r["wkts"] > 0]

    bat_rows = [r for r in rows if r["balls"] > 0]
    bowl_rows = [r for r in rows if r["bballs"] > 0]
    rb = [r["runs"] for r in bat_rows]
    bb = [r["balls"] for r in bat_rows]
    sr2 = [100.0 * r["runs"] / r["balls"] for r in bat_rows]
    wk = [r["wkts"] for r in bowl_rows]
    bbl = [r["bballs"] for r in bowl_rows]
    br = [r["bruns"] for r in bowl_rows]

    print(
        f"  {label}: n={len(rows)} batted={batted} bowled={bowled} | "
        f"when bat: runs mean={mean(rb) if rb else 0:.1f} balls mean={mean(bb) if bb else 0:.1f} "
        f"SR mean={mean(sr2) if sr2 else 0:.1f} | "
        f"when bowl: wkts mean={mean(wk) if wk else 0:.2f} bballs mean={mean(bbl) if bbl else 0:.1f} "
        f"econ mean={mean([(6*bruns/bb_) for bruns, bb_ in zip(br, bbl) if bb_>0]) if bbl else 0:.2f} | "
        f"all-innings runs mean={mean(runs):.1f} wkts mean={mean(wkts):.2f}"
    )


def main():
    random.seed(42)
    profiles = [
        ("elite_bat", 88, 28, "Opening Batter"),
        ("avg_bat", 55, 40, "Middle Order Batter"),
        ("avg_ar", 52, 55, "Genuine Allrounder (Fast Medium)"),
        ("avg_bowl", 32, 82, "Fast Bowler"),
    ]
    formats = ["T20", "ODI", "Test"]
    n = 120
    for fmt in formats:
        print(f"\n=== {fmt} ({n} sims per profile, swap home/away) ===")
        for key, bat, bowl, role in profiles:
            anchor = make_player(f"Z_{key}", bat, bowl, role)
            rows = run_block(fmt, anchor, n)
            summarize(key, rows)


if __name__ == "__main__":
    main()
