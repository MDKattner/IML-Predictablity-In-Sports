import csv
from collections import defaultdict

DATA_DIR = "Data"
MEMBERSHIP_PATH = f"{DATA_DIR}/mlb_division_membership.csv"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/mlb_division_series_results.csv"

def load_division_lookup():
    """Returns dict: (season, team_code) -> division name."""
    lookup = {}
    with open(MEMBERSHIP_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            season = int(row["season"])
            division = row["division"]
            for i in range(1, 6):
                team = row[f"team{i}"]
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


def verify(rows):
    expected = 12 * 6 * 10
    assert len(rows) == expected, f"expected {expected} rows, got {len(rows)}"

    for r in rows:
        assert r["wins1"] + r["wins2"] + r["ties"] == r["games_played"], (
            f"win/tie counts don't add up for {r}"
        )

    print("Basic structural checks passed (row count, wins+ties=games_played).")


def print_discrepancy_report(rows):
    print("\n=== DISCREPANCY REPORT (for team meeting) ===\n")

    games_by_season = defaultdict(set)
    for r in rows:
        games_by_season[r["season"]].add(r["games_played"])
    print("Distinct games-played-per-pair counts, by season:")
    for season in sorted(games_by_season):
        counts = sorted(games_by_season[season])
        print(f"  {season}: {counts}")

    tied_series = [r for r in rows if r["result"] == "TIE"]
    print(f"\nTrue tied division series (wins1 == wins2): {len(tied_series)}")
    for r in tied_series:
        print(f"  {r['season']} {r['division']}: {r['team1']} vs {r['team2']} "
              f"({r['wins1']}-{r['wins2']}, {r['ties']} tie game(s))")

    rows_with_tie_games = [r for r in rows if r["ties"] > 0]
    print(f"\nPairs whose season series included at least one 0-0/tied individual game: "
          f"{len(rows_with_tie_games)}")
    for r in rows_with_tie_games:
        print(f"  {r['season']} {r['division']}: {r['team1']} vs {r['team2']} "
              f"-> {r['ties']} tie game(s) out of {r['games_played']}")

    print("\n=== END REPORT ===\n")


if __name__ == "__main__":
    division_lookup = load_division_lookup()
    pair_games = load_in_division_games(division_lookup)
    rows = summarize(pair_games)
    write_csv(rows)
    verify(rows)
    print_discrepancy_report(rows)
