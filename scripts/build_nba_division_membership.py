import csv
from collections import defaultdict

# NBA division membership is external domain knowledge (the game log has no league/division
# column), but for much of 1985-2003 it can be recovered or checked from the schedule itself:
#   * 1985-1994: division rivals play MORE games than other same-conference teams, so the
#     divisions are the connected groups of pairs with >= SIGNAL_THRESHOLD games
#     (West 1985-94 and East 1988-94). The eras below for those seasons come from that.
#   * Every season: cross-conference pairs play far fewer games than same-conference pairs,
#     so the East/West split of every season is checked.
#   * East 1995-2003: pairs that played only 3 games are always in different divisions
#     (necessary condition only).
#   NOT verifiable from the schedule: East 1985-87 and West 1995-2003 (all same-conference
#   pairs play the same number of games); those assignments come from documented history and
#   should be spot-checked against Basketball-Reference. 2004-2024: only codes are checked.
# Season labels are START-year ("1985" = the 1985-86 season). Unlike the NFL file, NBA codes in
# the log are period-correct (SEA, NJN, NOH/NOK, VAN/MEM ...), so a few franchises are resolved
# per season in resolve_code().

START_SEASON = 1985
END_SEASON = 2024

EAST_DIVISIONS = {"Atlantic", "Central", "Southeast"}

# Slot codes use each franchise's EARLIEST code in the window as the canonical key.
ERAS = [
    # (start_season, end_season, {division: [slot codes]})
    (1985, 1987, {  # 23 teams. East split not verifiable from the schedule.
        "Atlantic": ["BOS", "NJN", "NYK", "PHI", "WAS"],
        "Central": ["ATL", "CHI", "CLE", "DET", "IND", "MIL"],
        "Midwest": ["DAL", "DEN", "HOU", "SAC", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SEA"],
    }),
    (1988, 1988, {  # 25 teams: CHA and MIA join (placement taken from the schedule)
        "Atlantic": ["BOS", "CHA", "NJN", "NYK", "PHI", "WAS"],
        "Central": ["ATL", "CHI", "CLE", "DET", "IND", "MIL"],
        "Midwest": ["DAL", "DEN", "HOU", "MIA", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (1989, 1989, {  # 27 teams: MIN and ORL join (placement taken from the schedule)
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "PHI", "WAS"],
        "Central": ["ATL", "CHI", "CLE", "DET", "IND", "MIL", "ORL"],
        "Midwest": ["CHA", "DAL", "DEN", "HOU", "MIN", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (1990, 1990, {
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "PHI", "WAS"],
        "Central": ["ATL", "CHA", "CHI", "CLE", "DET", "IND", "MIL"],
        "Midwest": ["DAL", "DEN", "HOU", "MIN", "ORL", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (1991, 1994, {
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "ORL", "PHI", "WAS"],
        "Central": ["ATL", "CHA", "CHI", "CLE", "DET", "IND", "MIL"],
        "Midwest": ["DAL", "DEN", "HOU", "MIN", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (1995, 2000, {  # 29 teams: TOR and VAN join. Schedule gives no division signal here
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "ORL", "PHI", "WAS"],
        "Central": ["ATL", "CHA", "CHI", "CLE", "DET", "IND", "MIL", "TOR"],
        "Midwest": ["DAL", "DEN", "HOU", "MIN", "SAS", "UTA", "VAN"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (2001, 2001, {  # VAN -> MEM
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "ORL", "PHI", "WAS"],
        "Central": ["ATL", "CHA", "CHI", "CLE", "DET", "IND", "MIL", "TOR"],
        "Midwest": ["DAL", "DEN", "HOU", "MEM", "MIN", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (2002, 2003, {  # CHA franchise relocates to New Orleans (NOH) but stays in the East
        "Atlantic": ["BOS", "MIA", "NJN", "NYK", "ORL", "PHI", "WAS"],
        "Central": ["ATL", "CHI", "CLE", "DET", "IND", "MIL", "NOH", "TOR"],
        "Midwest": ["DAL", "DEN", "HOU", "MEM", "MIN", "SAS", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "POR", "SAC", "SEA"],
    }),
    (2004, 2024, {  # current 6-division alignment (Charlotte Bobcats expansion team = CHA)
        "Atlantic": ["BOS", "NJN", "NYK", "PHI", "TOR"],
        "Central": ["CHI", "CLE", "DET", "IND", "MIL"],
        "Southeast": ["ATL", "CHA", "MIA", "ORL", "WAS"],
        "Northwest": ["DEN", "MIN", "SEA", "POR", "UTA"],
        "Pacific": ["GSW", "LAC", "LAL", "PHX", "SAC"],
        "Southwest": ["DAL", "HOU", "MEM", "NOH", "SAS"],
    }),
]

EXPECTED_TEAM_COUNT = {
    **{s: 23 for s in range(1985, 1988)},
    1988: 25,
    **{s: 27 for s in range(1989, 1995)},
    **{s: 29 for s in range(1995, 2004)},
    **{s: 30 for s in range(2004, 2025)},
}

# (season, conference) -> minimum games that mark same-division pairs; divisions are then the
# connected components of those pairs (seasons where the schedule reveals the divisions).
SIGNAL_THRESHOLD = {}
for _s in range(1985, 1988):
    SIGNAL_THRESHOLD[(_s, "West")] = 6
SIGNAL_THRESHOLD[(1988, "West")] = 6
SIGNAL_THRESHOLD[(1988, "East")] = 6
for _s in range(1989, 1995):
    SIGNAL_THRESHOLD[(_s, "West")] = 5
    SIGNAL_THRESHOLD[(_s, "East")] = 5

# East seasons where 3-game pairs must never be division rivals (1998 lockout season skipped)
THREE_GAME_RULE_SEASONS = [s for s in range(1995, 2004) if s != 1998]


def resolve_code(code, season):
    """Map a canonical slot code to the code actually used in the game log that season."""
    if code == "NJN":
        return "NJN" if season <= 2011 else "BKN"
    if code == "SEA":
        return "SEA" if season <= 2007 else "OKC"
    if code == "NOH":
        if season in (2005, 2006):
            return "NOK"  # New Orleans/Oklahoma City Hornets (post-Katrina)
        if season >= 2013:
            return "NOP"  # renamed Pelicans
        return "NOH"
    return code


DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/nba_division_membership.csv"


def build_rows():
    """Long format: one row per (season, division, team). Used for verification."""
    rows = []
    for start, end, divisions in ERAS:
        for season in range(start, end + 1):
            for division, teams in divisions.items():
                for code in teams:
                    team = resolve_code(code, season)
                    rows.append({"season": season, "league": "NBA", "division": division, "team": team})
    rows.sort(key=lambda r: (r["season"], r["division"], r["team"]))
    return rows


def build_tuple_rows(rows):
    """One row per (season, division), teams collapsed into a single alphabetically-sorted
    tuple-string column, e.g. "(BOS,BKN,NYK,PHI,TOR)"."""
    grouped = {}
    for r in rows:
        key = (r["season"], r["division"])
        grouped.setdefault(key, []).append(r["team"])

    tuple_rows = []
    for (season, division), teams in grouped.items():
        teams = sorted(teams)
        teams_tuple = "(" + ",".join(teams) + ")"
        tuple_rows.append({"season": season, "league": "NBA", "division": division, "teams": teams_tuple})

    tuple_rows.sort(key=lambda r: (r["season"], r["division"]))
    return tuple_rows


def write_csv(tuple_rows):
    fieldnames = ["season", "league", "division", "teams"]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tuple_rows)


def components(nodes, edges):
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, out = set(), []
    for t in sorted(nodes):
        if t in seen:
            continue
        comp, stack = set(), [t]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        out.append(frozenset(comp))
    return set(out)


def verify(rows):
    by_season = {}
    divs = defaultdict(dict)  # season -> {division: set(teams)}
    for r in rows:
        by_season.setdefault(r["season"], set()).add(r["team"])
        divs[r["season"]].setdefault(r["division"], set()).add(r["team"])

    assert set(by_season.keys()) == set(range(START_SEASON, END_SEASON + 1)), "missing or extra seasons"

    for season, teams in by_season.items():
        expected = EXPECTED_TEAM_COUNT[season]
        assert len(teams) == expected, f"{season}: expected {expected} teams, got {len(teams)}"

    log_codes_by_season = {}
    pair_games = defaultdict(int)  # (season, team_a, team_b) -> games that season
    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["league"] != "NBA":
                continue
            s = int(row["season"])
            if s < START_SEASON or s > END_SEASON:
                continue
            log_codes_by_season.setdefault(s, set()).add(row["team1"])
            log_codes_by_season.setdefault(s, set()).add(row["team2"])
            a, b = sorted([row["team1"], row["team2"]])
            pair_games[(s, a, b)] += 1

    mismatches = {}
    for season, teams in by_season.items():
        log_teams = log_codes_by_season.get(season, set())
        missing_from_log = teams - log_teams
        extra_in_log = log_teams - teams
        if missing_from_log or extra_in_log:
            mismatches[season] = {"in_membership_not_log": sorted(missing_from_log),
                                  "in_log_not_membership": sorted(extra_in_log)}

    assert not mismatches, f"team-code mismatches vs game log: {mismatches}"

    def games(season, a, b):
        x, y = sorted([a, b])
        return pair_games.get((season, x, y), 0)

    problems = []
    for season in range(START_SEASON, 2004):
        east = set().union(*[t for d, t in divs[season].items() if d in EAST_DIVISIONS])
        west = by_season[season] - east

        # 1. conference check: every cross-conference pair played fewer games than every
        #    same-conference pair
        cross = [games(season, a, b) for a in east for b in west]
        within = [games(season, a, b) for grp in (east, west) for a in grp for b in grp if a < b]
        if max(cross) >= min(within):
            problems.append(f"{season}: East/West split not supported by schedule "
                            f"(cross max {max(cross)}, same-conference min {min(within)})")

        # 2. divisions recovered from the schedule must equal the declared divisions
        for conf, grp in (("East", east), ("West", west)):
            t = SIGNAL_THRESHOLD.get((season, conf))
            if t is None:
                continue
            edges = [(a, b) for a in grp for b in grp if a < b and games(season, a, b) >= t]
            found = components(grp, edges)
            declared = {frozenset(ts) for d, ts in divs[season].items()
                        if (d in EAST_DIVISIONS) == (conf == "East")}
            if found != declared:
                problems.append(f"{season} {conf}: schedule-derived divisions differ from declared ones")

        # 3. 3-game pairs are never division rivals (East 1995-2003)
        if season in THREE_GAME_RULE_SEASONS:
            for d, ts in divs[season].items():
                if d not in EAST_DIVISIONS:
                    continue
                for a in ts:
                    for b in ts:
                        if a < b and games(season, a, b) < 4:
                            problems.append(f"{season} {d}: {a}-{b} played {games(season, a, b)} games")

    assert not problems, "division checks failed: " + "; ".join(problems[:10])

    print(f"All checks passed: {len(rows)} rows, {len(by_season)} seasons "
          f"({START_SEASON}-{END_SEASON}), team counts match history, all codes match the game log, "
          f"East/West split confirmed 1985-2003, divisions confirmed from the schedule for "
          f"West 1985-94 and East 1988-94.")
    print("NOT verifiable from the schedule (documented history only): East 1985-87, "
          "West 1995-2003, and division placement in 2004-2024. Spot-check against "
          "Basketball-Reference.")


if __name__ == "__main__":
    rows = build_rows()
    verify(rows)
    tuple_rows = build_tuple_rows(rows)
    write_csv(tuple_rows)
