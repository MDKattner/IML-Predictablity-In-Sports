import csv 
import os
from collections import defaultdict
from math import comb

DATA_DIR = "Data"
MEMBERSHIP_PATH = f"{DATA_DIR}/bund_division_membership.csv"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_bundesliga.csv"
OUT_PATH = f"{DATA_DIR}/bund_division_series_results.csv"

ANOMALIES_DIR = f"{DATA_DIR}/anomalies"
TIED_SERIES_PATH = f"{ANOMALIES_DIR}/bund_tied_division_series.csv"

GAMES_PER_PAIR = 2

def load_division_lookup():
    """Returns dict: (season, team_code) -> division name"""
    lookup = {}
    with open(MEMBERSHIP_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            season = int(row["season"])
            division = row["division"]
            teams_str = row["teams"].strip("()")
            teams = teams_str.split(",")
            for team in teams:
                lookup[(season, team)] = division
    return lookup

def load_in_division_games(division_lookup):
    """Returns dict: (season, division, pair) -> list of (winner_code, is_draw) tuples"""
    pair_games = defaultdict(list)
    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            season = int(row["season"])
            home = row["home_team"]
            away = row["away_team"]
            div1 = division_lookup.get((season, home))
            div2 = division_lookup.get((season, away))
            if div1 is None or div2 is None or div1 != div2:
                continue
            result = int(row["hometeamresult"])
            pair = tuple(sorted([home, away]))
            if result == 1:
                winner = home
                is_draw = False
            elif result == -1:
                winner = away
                is_draw = False
            else:
                winner = None
                is_draw = True
            pair_games[(season, div1, pair)].append((winner, is_draw))
    return pair_games

def summarize(pair_games):
    rows = []
    for (season, division, pair), games in pair_games.items():
        team1, team2 = pair
        wins1 = sum(1 for winner, is_draw in games if winner == team1)
        wins2 = sum(1 for winner, is_draw in games if winner == team2)
        ties = sum(1 for winner, is_draw in games if is_draw)
        games_played = len(games)
        if wins1 > wins2: 
            result = team1
        elif wins2 > wins1:
            result = team2
        else:
            result = "TIE"

        rows.append({
            "season": season,
            "league": "BL",
            "division": division, 
            "team1": team1,
            "team2": team2,
            "result": result, 
            "wins1": wins1,
            "wins2": wins2,
            "ties": ties,
            "games_played": games_played
        })
    rows.sort(key=lambda r: (r["season"], r["division"], r["team1"], r["team2"]))
    return rows

def write_csv(rows):
    fieldnames = ["season", "league", "division", "team1", "team2", "result",
                  "wins1", "wins2", "ties", "games_played"]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def verify(rows, division_lookup):
    teams_by_season_division = defaultdict(set)
    for (season, team), division in division_lookup.items():
        teams_by_season_division[(season, division)].add(team)

    expected = sum(comb(len(teams), 2) for teams in teams_by_season_division.values())
    assert len(rows) == expected, f"expected {expected} rows, got {len(rows)}"

    for r in rows:
        assert r["wins1"] + r["wins2"] + r["ties"] == r["games_played"], f"win/draw counts don't add up for {r}"
        assert r["games_played"] == GAMES_PER_PAIR, f"expected {GAMES_PER_PAIR} games per pair, got {r}"

    print(f"Basic structural checks passed: {len(rows)} rows (matches expected pair count "
          f"from membership file), wins+draws=games_played and games_played={GAMES_PER_PAIR} for all rows.")


def print_discrepancy_report(rows):
    os.makedirs(ANOMALIES_DIR, exist_ok=True)

    print("\n=== BUNDESLIGA REPORT (for team meeting) ===\n")

    # Every pair plays exactly 2 games (even), so tied series (1-1, or two draws) are expected
    # and common - not a data anomaly, but recorded because the upset definition treats a
    # tied series separately (strict: not an upset, weak: 1/2 upset).
    tied_series = [r for r in rows if r["result"] == "TIE"]
    two_draws = [r for r in tied_series if r["ties"] == 2]
    print(f"Tied division series (wins1 == wins2): {len(tied_series)} "
          f"({len(tied_series) - len(two_draws)} are a win plus a loss, {len(two_draws)} are two draws)")
    with open(TIED_SERIES_PATH, "w", newline="") as f:
        fieldnames = ["season", "division", "team1", "team2", "wins1", "wins2", "ties", "games_played"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in tied_series:
            writer.writerow({k: r[k] for k in fieldnames})

    print("\n=== END REPORT ===\n")
    print(f"Written to {ANOMALIES_DIR}/: bund_tied_division_series")


if __name__ == "__main__":
    division_lookup = load_division_lookup()
    pair_games = load_in_division_games(division_lookup)
    rows = summarize(pair_games)
    write_csv(rows)
    verify(rows, division_lookup)
    print_discrepancy_report(rows)