import csv

# Division membership is external domain knowledge (not derivable from the game log,
# which has no league/division column). Compiled from documented MLB realignment
# history, then cross-checked against the team codes actually present in
# game_data_us_leagues.csv for every season 1985-2024 (season boundaries and codes
# below match the data exactly).

ERAS = [
    # (start_season, end_season, {division: [team codes as of era start]})
    (1985, 1992, {
        "AL-East": ["BAL", "BOS", "CLE", "DET", "MIL", "NYA", "TOR"],
        "AL-West": ["CAL", "CHA", "KCA", "MIN", "OAK", "SEA", "TEX"],
        "NL-East": ["CHN", "MON", "NYN", "PHI", "PIT", "SLN"],
        "NL-West": ["ATL", "CIN", "HOU", "LAN", "SDN", "SFN"],
    }),
    (1993, 1993, {
        "AL-East": ["BAL", "BOS", "CLE", "DET", "MIL", "NYA", "TOR"],
        "AL-West": ["CAL", "CHA", "KCA", "MIN", "OAK", "SEA", "TEX"],
        "NL-East": ["CHN", "FLO", "MON", "NYN", "PHI", "PIT", "SLN"],
        "NL-West": ["ATL", "CIN", "COL", "HOU", "LAN", "SDN", "SFN"],
    }),
    (1994, 1997, {
        "AL-East": ["BAL", "BOS", "DET", "NYA", "TOR"],
        "AL-Central": ["CHA", "CLE", "KCA", "MIL", "MIN"],
        "AL-West": ["CAL", "OAK", "SEA", "TEX"],
        "NL-East": ["ATL", "FLO", "MON", "NYN", "PHI"],
        "NL-Central": ["CHN", "CIN", "HOU", "PIT", "SLN"],
        "NL-West": ["COL", "LAN", "SDN", "SFN"],
    }),
    (1998, 2012, {
        "AL-East": ["BAL", "BOS", "NYA", "TBA", "TOR"],
        "AL-Central": ["CHA", "CLE", "DET", "KCA", "MIN"],
        "AL-West": ["ANA", "OAK", "SEA", "TEX"],
        "NL-East": ["ATL", "FLO", "MON", "NYN", "PHI"],
        "NL-Central": ["CHN", "CIN", "HOU", "MIL", "PIT", "SLN"],
        "NL-West": ["ARI", "COL", "LAN", "SDN", "SFN"],
    }),
    (2013, 2024, {
        "AL-East": ["BAL", "BOS", "NYA", "TBA", "TOR"],
        "AL-Central": ["CHA", "CLE", "DET", "KCA", "MIN"],
        "AL-West": ["ANA", "HOU", "OAK", "SEA", "TEX"],
        "NL-East": ["ATL", "MIA", "NYN", "PHI", "WAS"],
        "NL-Central": ["CHN", "CIN", "MIL", "PIT", "SLN"],
        "NL-West": ["ARI", "COL", "LAN", "SDN", "SFN"],
    }),
]

# (season the new code first appears, old code, new code) - division unchanged,
# only the abbreviation used in the data changed. Applied on top of ERAS above.
CODE_CHANGES = [
    (1997, "CAL", "ANA"),  # Angels: California -> Anaheim
    (2005, "MON", "WAS"),  # Expos -> Nationals (relocation)
    (2012, "FLO", "MIA"),  # Marlins: Florida -> Miami
]

EXPECTED_TEAM_COUNT = {
    **{s: 26 for s in range(1985, 1993)},
    1993: 28,
    **{s: 28 for s in range(1994, 1998)},
    **{s: 30 for s in range(1998, 2025)},
}

DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/mlb_division_membership_1985_2024.csv"


def apply_code_changes(season, teams):
    updated = list(teams)
    for change_season, old, new in CODE_CHANGES:
        if season >= change_season:
            updated = [new if t == old else t for t in updated]
    return updated


MAX_TEAMS_PER_DIVISION = 7  # largest division size across all eras (1985-1992, 1993)


def build_rows():
    """Long format: one row per (season, division, team). Used for verification."""
    rows = []
    for start, end, divisions in ERAS:
        for season in range(start, end + 1):
            for division, teams in divisions.items():
                current_teams = apply_code_changes(season, teams)
                for team in sorted(current_teams):
                    rows.append({"season": season, "league": "MLB", "division": division, "team": team})
    rows.sort(key=lambda r: (r["season"], r["division"], r["team"]))
    return rows


def build_wide_rows(rows):
    """Wide format: one row per (season, division), teams spread across team1..team7.
    Divisions with fewer than 7 teams (every era except 1985-1993) leave the extra
    team columns blank rather than padding with a fake value."""
    grouped = {}
    for r in rows:
        key = (r["season"], r["division"])
        grouped.setdefault(key, []).append(r["team"])

    wide_rows = []
    for (season, division), teams in grouped.items():
        teams = sorted(teams)
        row = {"season": season, "league": "MLB", "division": division}
        for i in range(MAX_TEAMS_PER_DIVISION):
            row[f"team{i + 1}"] = teams[i] if i < len(teams) else ""
        wide_rows.append(row)

    wide_rows.sort(key=lambda r: (r["season"], r["division"]))
    return wide_rows


def write_csv(wide_rows):
    fieldnames = ["season", "league", "division"] + [f"team{i + 1}" for i in range(MAX_TEAMS_PER_DIVISION)]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(wide_rows)


def verify(rows):
    by_season = {}
    for r in rows:
        by_season.setdefault(r["season"], set()).add(r["team"])

    assert set(by_season.keys()) == set(range(1985, 2025)), "missing or extra seasons"

    for season, teams in by_season.items():
        expected = EXPECTED_TEAM_COUNT[season]
        assert len(teams) == expected, f"{season}: expected {expected} teams, got {len(teams)}"

    # cross-check against actual codes present in the game log for every season
    log_codes_by_season = {}
    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["league"] != "MLB":
                continue
            s = int(row["season"])
            if s < 1985 or s > 2024:
                continue
            log_codes_by_season.setdefault(s, set()).add(row["team1"])
            log_codes_by_season.setdefault(s, set()).add(row["team2"])

    mismatches = {}
    for season, teams in by_season.items():
        log_teams = log_codes_by_season.get(season, set())
        missing_from_log = teams - log_teams
        # WAS/WSH is a known, already-documented mismatch versus mlb_teams.csv,
        # not versus the game log itself - our codes are built to match the log.
        if missing_from_log:
            mismatches[season] = missing_from_log

    assert not mismatches, f"teams in our membership file not found in game log: {mismatches}"

    print(f"All checks passed: {len(rows)} rows, {len(by_season)} seasons (1985-2024), "
          f"team counts match documented history, all codes confirmed present in game log.")


if __name__ == "__main__":
    rows = build_rows()
    verify(rows)  # verify against the long format - simplest to reason about
    wide_rows = build_wide_rows(rows)
    write_csv(wide_rows)
