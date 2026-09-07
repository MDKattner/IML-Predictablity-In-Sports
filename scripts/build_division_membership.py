import csv
# MLB format is stable for all seasons froms 2013-2024 so doing them first
# codes match game_data_us_leagues.cs
DIVISIONS_2013_2024 = {
    "AL-East": ("BAL", "BOS", "NYA", "TBA", "TOR"),
    "AL-Central": ("CHA", "CLE", "DET", "KCA", "MIN"),
    "AL-West": ("ANA", "HOU", "OAK", "SEA", "TEX"),
    "NL-East": ("ATL", "MIA", "NYN", "PHI", "WAS"),
    "NL-Central": ("CHN", "CIN", "MIL", "PIT", "SLN"),
    "NL-West": ("ARI", "COL", "LAN", "SDN", "SFN"),
}
DIVISION_ORDER = ["AL-East", "AL-Central", "AL-West", "NL-East", "NL-Central", "NL-West"]
SEASONS = range(2013,2025)

DATA_DIR = "Data"
OUT_PATH = f"{DATA_DIR}/mlb_division_membership.csv"

def build_rows():
    rows = []
    for season in SEASONS:
        for division in DIVISION_ORDER:
            teams = sorted(DIVISIONS_2013_2024[division])
            rows.append([season, "MLB", division, *teams, f"{','.join(teams)}"])
    return rows

def write_csv(rows):
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["season", "league", "division", "team1", "team2", "team3", "team4", "team5", "teams_tuple"]
        )
        writer.writerows(rows)


def verify(rows):
    assert len(rows) == 72, f"expected 72 rows, got {(len(rows))}"

    all_codes = set()
    for div_teams in DIVISIONS_2013_2024.values():
        all_codes.update(div_teams)
    assert len(all_codes) == 30, f"expected 30 unique codes, got {len(all_codes)}"

    for season in SEASONS:
        season_rows = [r for r in rows if r[0] == season]
        season_teams = []
        for r in season_rows:
            season_teams.extend(r[3:8])
        assert len(season_teams) == 30, f"{season}: expected 30 team slots, got {len(season_teams)}"
        assert len(set(season_teams)) == 30, f"{season}: duplicate team code found"
        assert set(season_teams) == all_codes, f"{season}: team set mismatch"

    with open(f"{DATA_DIR}/mlb_teams.csv") as f:
        reader = csv.DictReader(f)
        known_abbrevs = {row["Abbreviation"] for row in reader}

    unknown = all_codes - known_abbrevs
    assert unknown == {"WAS"}, f"unexpected abbreviation mismatch beyond known WAS/WSH"

    with open(f"{DATA_DIR}/game_data_us_leagues.csv") as f:
        reader = csv.DictReader(f)
        log_codes_by_season = {}
        for row in reader:
            if row["league"] != "MLB":
                continue
            s = int(row["season"])
            if s not in (2013, 2024):
                continue
            log_codes_by_season.setdefault(s, set()).add(row["team1"])
            log_codes_by_season.setdefault(s, set()).add(row["team2"])
    for s in (2013, 2024):
        assert all_codes <= log_codes_by_season[s], (
            f"{s}: division codes not all found in game log: {all_codes - log_codes_by_season[s]}"
        )

    print("All checks passed: 72 rows, 30 unique teams/season, WAS/WSH mismatch was only exception")

if __name__ == "__main__":
    rows = build_rows()
    write_csv(rows)
    verify(rows)