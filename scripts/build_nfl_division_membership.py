import csv
from collections import defaultdict

# I gathered the NFL Division membership form external domain knowledge has the game log isn't too descriptive for it
# NFL teams play each division rival twice a season
# Season labels are start-year, this dataset already uses present-day franchise codes in every season
# (Oilers -> TEN, Colts -> IND, Cardinals -> ARI, Rams -> LAR, Chargers -> LAC,
# Raiders -> LV), so no per-season code resolution is needed. The Browns are absent 1996-1998
# (franchise inactive) and BAL (Ravens) first appears in 1996, exactly as in the game log.
START_SEASON = 1985
END_SEASON = 2024

# 1987 players' strike: only 12 games per team, so many division pairs played once not twice
STRIKE_SEASON = 1987

AFC_EAST_OLD = ["BUF", "IND", "MIA", "NE", "NYJ"]
AFC_WEST_OLD = ["DEN", "KC", "LAC", "LV", "SEA"]
NFC_EAST_OLD = ["ARI", "DAL", "NYG", "PHI", "WAS"]
NFC_CENTRAL_OLD = ["CHI", "DET", "GB", "MIN", "TB"]

ERAS = [
    # (start_season, end_season, {division: [team codes]})
    (1985, 1994, {  # 28 teams, AFC-Central and NFC-West have 4 teams
        "AFC-East": AFC_EAST_OLD,
        "AFC-Central": ["CIN", "CLE", "PIT", "TEN"],
        "AFC-West": AFC_WEST_OLD,
        "NFC-East": NFC_EAST_OLD,
        "NFC-Central": NFC_CENTRAL_OLD,
        "NFC-West": ["ATL", "LAR", "NO", "SF"],
    }),
    (1995, 1995, {  # expansion: CAR, JAX (30 teams)
        "AFC-East": AFC_EAST_OLD,
        "AFC-Central": ["CIN", "CLE", "JAX", "PIT", "TEN"],
        "AFC-West": AFC_WEST_OLD,
        "NFC-East": NFC_EAST_OLD,
        "NFC-Central": NFC_CENTRAL_OLD,
        "NFC-West": ["ATL", "CAR", "LAR", "NO", "SF"],
    }),
    (1996, 1998, {  # Browns inactive, Ravens (BAL) start; 30 teams
        "AFC-East": AFC_EAST_OLD,
        "AFC-Central": ["BAL", "CIN", "JAX", "PIT", "TEN"],
        "AFC-West": AFC_WEST_OLD,
        "NFC-East": NFC_EAST_OLD,
        "NFC-Central": NFC_CENTRAL_OLD,
        "NFC-West": ["ATL", "CAR", "LAR", "NO", "SF"],
    }),
    (1999, 2001, {  # Browns return; AFC-Central has 6 teams; 31 teams
        "AFC-East": AFC_EAST_OLD,
        "AFC-Central": ["BAL", "CIN", "CLE", "JAX", "PIT", "TEN"],
        "AFC-West": AFC_WEST_OLD,
        "NFC-East": NFC_EAST_OLD,
        "NFC-Central": NFC_CENTRAL_OLD,
        "NFC-West": ["ATL", "CAR", "LAR", "NO", "SF"],
    }),
    (2002, 2024, {  # Texans join (32 teams); realignment into 8 divisions of 4
        "AFC-East": ["BUF", "MIA", "NE", "NYJ"],
        "AFC-North": ["BAL", "CIN", "CLE", "PIT"],
        "AFC-South": ["HOU", "IND", "JAX", "TEN"],
        "AFC-West": ["DEN", "KC", "LAC", "LV"],
        "NFC-East": ["DAL", "NYG", "PHI", "WAS"],
        "NFC-North": ["CHI", "DET", "GB", "MIN"],
        "NFC-South": ["ATL", "CAR", "NO", "TB"],
        "NFC-West": ["ARI", "LAR", "SEA", "SF"],
    }),
]

EXPECTED_TEAM_COUNT = {
    **{s: 28 for s in range(1985, 1995)},
    **{s: 30 for s in range(1995, 1999)},
    **{s: 31 for s in range(1999, 2002)},
    **{s: 32 for s in range(2002, 2025)},
}

DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/nfl_division_membership.csv"

def build_rows():
    """Long format: one row per (season, division, team)"""
    rows = []
    for start, end, divisions in ERAS:
        for season in range(start, end + 1):
            for division, teams in divisions.items():
                for team in teams:
                    rows.append({"season": season, "league": "NFL", "division": division, "team": team})
    rows.sort(key=lambda r: (r["season"], r["division"], r["team"]))
    return rows

def build_tuple_rows(rows):
    """One row per (season, diviosn), teams collapsed into a single alphabetically-sorted
    tuple-string column"""
    grouped = {}
    for r in rows:
        key = (r["season"], r["division"])
        grouped.setdefault(key, []).append(r["team"])

    tuple_rows = []
    for (season, division), teams in grouped.items():
        teams = sorted(teams)
        teams_tuple = "(" + ",".join(teams) + ")"
        tuple_rows.append({"season": season, "league": "NFL", "division": division, "teams": teams_tuple})

    tuple_rows.sort(key=lambda r: (r["season"], r["division"]))
    return tuple_rows

def write_csv(tuple_rows):
    fieldnames = ["season", "league", "division", "teams"]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tuple_rows)


def verify(rows):
    by_season = {}
    by_season_division = defaultdict(set)
    for r in rows:
        by_season.setdefault(r["season"], set()).add(r["team"])
        by_season_division[(r["season"], r["division"])].add(r["team"])

    assert set(by_season.keys()) == set(range(START_SEASON, END_SEASON + 1)), "missing or extra seasons"

    for season, teams in by_season.items():
        expected = EXPECTED_TEAM_COUNT[season]
        assert len(teams) == expected, f"{season}: expected {expected} teams, got {len(teams)}"

    log_codes_by_season = {}
    pair_games = defaultdict(int)  # (season, team_a, team_b) -> games played that season
    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["league"] != "NFL":
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

    # Division placement check: division rivals play exactly twice a season.
    bad_pairs = []
    for (season, division), teams in by_season_division.items():
        ordered = sorted(teams)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                games = pair_games.get((season, a, b), 0)
                ok = games >= 1 if season == STRIKE_SEASON else games == 2
                if not ok:
                    bad_pairs.append((season, division, a, b, games))

    assert not bad_pairs, f"division rivals that did not play exactly twice: {bad_pairs[:10]}"

    print(f"All checks passed: {len(rows)} rows, {len(by_season)} seasons "
          f"({START_SEASON}-{END_SEASON}), team counts match history, all codes match the game log, "
          f"and every division pair played exactly twice (1987 strike season: at least once).")


if __name__ == "__main__":
    rows = build_rows()
    verify(rows)
    tuple_rows = build_tuple_rows(rows)
    write_csv(tuple_rows)
