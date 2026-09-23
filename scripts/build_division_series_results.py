import csv
import os
from collections import defaultdict
from math import comb

DATA_DIR = "Data"
ANOMALIES_DIR = f"{DATA_DIR}/anomalies"
GAMES_PLAYED_VARIATION_PATH = f"{ANOMALIES_DIR}/games_played_variation_1985_2024.csv"
TIED_SERIES_PATH = f"{ANOMALIES_DIR}/tied_division_series_1985_2024.csv"
TIE_GAMES_IN_DIVISION_PATH = f"{ANOMALIES_DIR}/individual_tie_games_in_division_1985_2024.csv"

def load_division_lookup():
    """Returns dict: (season, team_code) -> division name."""
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
    """
    Scans the full game log, keeps only MLB games where both teams
    are in the same division that season. Returns a dict:
    (season, division, pair) -> list of (winner_code, is_tie) tuples,
    where pair is a sorted tuple of the two team codes (so BAL/BOS
    and BOS/BAL collapse to the same key).
    """
    pair_games = defaultdict(list)

    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["league"] != "MLB":
                continue

            season = int(row["season"])
            team1 = row["team1"]
            team2 = row["team2"]

            div1 = division_lookup.get((season, team1))
            div2 = division_lookup.get((season, team2))

            if div1 is None or div2 is None or div1 != div2:
                continue

            result = int(row["result"])
            pair = tuple(sorted([team1, team2]))

            if result == 1:
                winner = team1
                is_tie = False
            elif result == -1:
                winner = team2
                is_tie = False
            else:
                winner = None
                is_tie = True

            pair_games[(season, div1, pair)].append((winner, is_tie))

        return pair_games

def summarize(pair_games):
    """
    Turns each (season, division, pair) -> list of game outcomes into one summary row:
    season, league, division, team1, team2, result, wins1, wins2, ties, games_played
    """
    rows = []
    for (season, division, pair), games in pair_games.items():
        team1, team2 = pair
        wins1 = sum(1 for winner, is_tie in games if winner == team1)
        wins2 = sum(1 for winner, is_tie in games if winner == team2)
        ties = sum(1 for winner, is_tie in games if is_tie)
        games_played = len(games)

        if wins1 > wins2:
            result = team1
        elif wins2 > wins1:
            result = team2
        else:
            result = "TIE"

        rows.append(
            {
                "season": season,
                "league": "MLB",
                "division": division,
                "team1": team1,
                "team2": team2,
                "result": result,
                "wins1": wins1,
                "wins2": wins2,
                "ties": ties,
                "games_played": games_played,
            }
        )
    rows.sort(key=lambda r: (r["season"], r["division"], r["team1"], r["team2"]))
    return rows

def write_csv(rows):
    fieldnames = [
        "season", "league", "division", "team1", "team2",
        "result", "wins1", "wins2", "ties", "games_played",
    ]
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
        assert r["wins1"] + r["wins2"] + r["ties"] == r["games_played"], f"win/tie counts don't add up for {r}"

    print(f"Basic structural checks passed: {len(rows)} rows (matches expected pair count "
          f"from membership file), wins+ties=games_played for all rows.")


def print_discrepancy_report(rows):
    os.makedirs(ANOMALIES_DIR, exist_ok=True)

    print("\n=== DISCREPANCY REPORT (for team meeting) ===\n")

    games_by_season = defaultdict(set)
    for r in rows:
        games_by_season[r["season"]].add(r["games_played"])
    print("Distinct games-played-per-pair counts, by season:")
    with open(GAMES_PLAYED_VARIATION_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["season", "distinct_games_played_counts"])
        writer.writeheader()
        for season in sorted(games_by_season):
            counts = sorted(games_by_season[season])
            print(f"  {season}: {counts}")
            writer.writerow({"season": season, "distinct_games_played_counts": ";".join(str(c) for c in counts)})

    tied_series = [r for r in rows if r["result"] == "TIE"]
    print(f"\nTrue tied division series (wins1 == wins2): {len(tied_series)}")
    with open(TIED_SERIES_PATH, "w", newline="") as f:
        fieldnames = ["season", "division", "team1", "team2", "wins1", "wins2", "ties", "games_played"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in tied_series:
            print(f"  {r['season']} {r['division']}: {r['team1']} vs {r['team2']} "
                  f"({r['wins1']}-{r['wins2']}, {r['ties']} tie game(s))")
            writer.writerow({k: r[k] for k in fieldnames})

    rows_with_tie_games = [r for r in rows if r["ties"] > 0]
    print(f"\nPairs whose season series included at least one 0-0/tied individual game: "
          f"{len(rows_with_tie_games)}")
    with open(TIE_GAMES_IN_DIVISION_PATH, "w", newline="") as f:
        fieldnames = ["season", "division", "team1", "team2", "ties", "games_played"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows_with_tie_games:
            print(f"  {r['season']} {r['division']}: {r['team1']} vs {r['team2']} "
                  f"-> {r['ties']} tie game(s) out of {r['games_played']}")
            writer.writerow({k: r[k] for k in fieldnames})

    print("\n=== END REPORT ===\n")
    print(f"Written to {ANOMALIES_DIR}/: games_played_variation, tied_division_series, "
          f"individual_tie_games_in_division")

if __name__ == "__main__":
    division_lookup = load_division_lookup()
    pair_games = load_in_division_games(division_lookup)
    rows = summarize(pair_games)
    write_csv(rows)
    verify(rows, division_lookup)
    print_discrepancy_report(rows)
