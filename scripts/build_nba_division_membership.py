import csv

# working only with 2004 onwards right now, because given my current knowledge 2004 onwards 
# has a stable division structure. Season labels are start-year: "2004" = the 2004-05 season.


START_SEASON = 2004
END_SEASON = 2024

# slot codes use each franchise's EARLIEST in-window code as the cononical key
DIVISIONS = {
    "Atlantic": ["BOS", "NJN", "NYK", "PHI", "TOR"], # NJN -> BKN in 2012
    "Central": ["CHI", "CLE", "DET", "IND", "MIL"],
    "Southeast": ["ATL", "CHA", "MIA", "ORL", "WAS"],
    "Northwest": ["DEN", "MIN", "SEA", "POR", "UTA"], # SEA -> OKC in 2008
    "Pacific": ["GSW", "LAC", "LAL", "PHX", "SAC"],
    "Southwest": ["DAL", "HOU", "MEM", "NOH", "SAS"], # NOH -> NOK (2005-06) -> NOH -> NOP (2013+)
}

def resolve_code(code, season):
    """Map a canonical slot code to the code actually used in the game log that season"""
    if code == "NJN":
        return "NJN" if season <= 2011 else "BKN"
    if code == "SEA":
        return "SEA" if season <= 2007 else "OKC"
    if code == "NOH":
        if season in (2005, 2006):
            return "NOK"
        if season >= 2013:
            return "NOP"
        return "NOH"
    return code

DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/nba_division_membership.csv"

def build_rows():
    """Long format: one row per (season, division, team). Used for verification"""
    rows = []
    for season in range(START_SEASON, END_SEASON + 1):
        for division, teams in DIVISIONS.items():
            for code in teams:
                team = resolve_code(code, season)
                rows.append({"season": season, "league": "NBA", "division": division, "team": team})
    rows.sort(key=lambda r: (r["season"], r["division"], r["team"]))
    return rows

def build_tuple_rows(rows):
    """One row per (season, divison), teams written as a single alphabetically-sorted tuple-string"""
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
    with open(OUT_PATH, "w", newline ="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tuple_rows)


def verify(rows):
    by_season = {}
    for r in rows:
        by_season.setdefault(r["season"], set()).add(r["team"])

    assert set(by_season.keys()) == set(range(START_SEASON, END_SEASON + 1)), "missing or extra seasons"

    for season, teams in by_season.items():
        assert len(teams) == 30, f"{season}: expected 30 teams, got {len(teams)}"

    # cross-check against actual codes present in the game log for every season
    log_codes_by_season = {}
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

    mismatches = {}
    for season, teams in by_season.items():
        log_teams = log_codes_by_season.get(season, set())
        missing_from_log = teams - log_teams
        extra_in_log = log_teams - teams
        if missing_from_log or extra_in_log:
            mismatches[season] = {"in_membership_not_log": sorted(missing_from_log),
                                  "in_log_not_membership": sorted(extra_in_log)}

    assert not mismatches, f"team-code mismatches vs game log: {mismatches}"

    print(f"All checks passed: {len(rows)} rows, {len(by_season)} seasons "
          f"({START_SEASON}-{END_SEASON}), 30 teams each season, all codes match the game log exactly.")


if __name__ == "__main__":
    rows = build_rows()
    verify(rows)
    tuple_rows = build_tuple_rows(rows)
    write_csv(tuple_rows)