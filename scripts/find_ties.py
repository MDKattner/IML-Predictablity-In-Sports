import csv

DATA_DIR = "Data"
GAME_LOG_PATH = f"{DATA_DIR}/game_data_us_leagues.csv"
OUT_PATH = f"{DATA_DIR}/mlb_ties_1985_2024.csv"

START_SEASON = 1985
END_SEASON = 2024


def find_ties():
    ties = []
    with open(GAME_LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["league"] != "MLB":
                continue
            season = int(row["season"])
            if season < START_SEASON or season > END_SEASON:
                continue
            if int(row["result"]) == 0:
                ties.append(row)
    ties.sort(key=lambda r: (int(r["season"]), r["date"]))
    return ties


def write_csv(ties):
    fieldnames = ["season", "date", "league", "team1", "team2", "result", "score1", "score2"]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ties)


def print_report(ties):
    print(f"Found {len(ties)} tie games (result=0) in MLB, {START_SEASON}-{END_SEASON}.")
    print(f"Written to {OUT_PATH}")


if __name__ == "__main__":
    ties = find_ties()
    write_csv(ties)
    print_report(ties)