import csv
from collections import defaultdict
from math import comb

#The premier league (prem) has no divisions: the whole league is one tournament per season
# (20 teams, every pair plays twice - once home once away). So no era tables needed.
# Season labels are start-year (2024 = 2024-25).
# The game log has no 2003 and 2004 seasons. So they are not filled in here (for now)

LEAGUE = "PL"
DIVISION = "Premier-League"
EXPECTED_SEASONS = [2001, 2002] + list(range(2005, 2025))
TEAMS_PER_SEASON = 20
GAMES_PER_SEASON = 380

DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_premier_league.csv"
OUT_PATH = f"{DATA_DIR}/prem_division_membership.csv"

def read_games():
    """One (season, home_team, away_team) tuple per game"""
    games = []
    with open(GAME_LOG_PATH) as f:
        for row in csv.DictReader(f):
            games.append((int(row["season"]), row["home_team"], row["away_team"]))
    return games

def build_rows(games):
    """Long format: one row per (season, division, team)"""
    teams_by_season = defaultdict(set)
    for season, home, away in games:
        teams_by_season[season].add(home)
        teams_by_season[season].add(away)

    rows = []
    for season, teams in teams_by_season.items():
        for team in teams:
            rows.append({"season": season, "league": LEAGUE, "division": DIVISION, "team": team})
    rows.sort(key=lambda r: (r["season"], r["team"]))
    return rows

def build_tuple_rows(rows):
    """One row per (season, division), teams collapsed into a single alphabetically-sorted tuple-string column"""
    grouped = {}
    for r in rows:
        key = (r["season"], r["division"])
        grouped.setdefault(key, []).append(r["team"])

    tuple_rows = []
    for (season, division), teams in grouped.items():
        teams = sorted(teams)
        teams_tuple = "("+ ",".join(teams) + ")"
        tuple_rows.append({"season": season, "league": LEAGUE, "division": division, "teams": teams_tuple})

    tuple_rows.sort(key=lambda r: (r["season"], r["division"]))
    return tuple_rows

def write_csv(tuple_rows):
    fieldnames = ["season", "league", "division", "teams"]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tuple_rows)

def verify(rows, games):
    by_season = defaultdict(set)
    for r in rows:
        by_season[r["season"]].add(r["team"])

    assert sorted(by_season) == EXPECTED_SEASONS, "missing or extra seasons"

    for season, teams in by_season.items():
        assert len(teams) == TEAMS_PER_SEASON, f"{season}: expected {TEAMS_PER_SEASON} teams, got {len(teams)}"

    games_per_season = defaultdict(int)
    ordered_pairs = defaultdict(int)  # (season, home, away) -> games
    for season, home, away in games:
        games_per_season[season] += 1
        ordered_pairs[(season, home, away)] += 1

    for season in EXPECTED_SEASONS:
        assert games_per_season[season] == GAMES_PER_SEASON, \
            f"{season}: expected {GAMES_PER_SEASON} games, got {games_per_season[season]}"

    # Every pair of teams plays exactly twice, once with each team at home
    bad = [k for k, n in ordered_pairs.items() if n != 1]
    assert not bad, f"home/away pairs that did not occur exactly once: {bad[:10]}"
    for season in EXPECTED_SEASONS:
        n_pairs = sum(1 for (s, _, _) in ordered_pairs if s == season)
        assert n_pairs == 2 * comb(TEAMS_PER_SEASON, 2), f"{season}: wrong number of home/away pairs"

    print(f"All checks passed: {len(rows)} rows, {len(by_season)} seasons "
          f"({EXPECTED_SEASONS[0]}-{EXPECTED_SEASONS[-1]}, no 2003 or 2004), {TEAMS_PER_SEASON} teams "
          f"and {GAMES_PER_SEASON} games per season, every pair played exactly twice (home and away).")

if __name__ == "__main__":
    games = read_games()
    rows = build_rows(games)
    verify(rows, games)
    tuple_rows = build_tuple_rows(rows)
    write_csv(tuple_rows)