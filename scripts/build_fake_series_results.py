import argparse
import csv 
import os 
import random

DATA_DIR = "Data"
FAKE_DIR = f"{DATA_DIR}/fake"

# prob of draw for each league
LEAGUES = {
    "mlb": ("MLB", 0.0),
    "nba": ("NBA", 0.0),
    "nfl": ("NFL", 0.0),
    "prem": ("PL", 0.25),
    "bund": ("BL", 0.25),
}

FIELDNAMES = ["season", "league", "division", "team1", "team2", "result", 
              "wins1", "wins2", "ties", "games_played"]

def load_real_series(league):
    path = f"{DATA_DIR}/{league}_division_series_results.csv"
    with open(path) as f:
        return list(csv.DictReader(f))

def play_games(n_games, p_draw, rng):
    """Returns (wins1, wins2, ties) for n_games independent games"""
    wins1 = wins2 = ties = 0
    p_win = (1 - p_draw) / 2
    for _ in range(n_games):
        x = rng.random()
        if x < p_win:
            wins1 += 1
        elif x < 2 * p_win:
            wins2 += 1
        else:
            ties += 1
    return wins1, wins2, ties

def make_fake_rows(real_rows, p_draw, rng):
    rows = []
    for r in real_rows:
        if p_draw == 0:
            n_games = int(r["wins1"]) + int(r["wins2"])
        else:
            n_games = int(r["games_played"])
        wins1, wins2, ties = play_games(n_games, p_draw, rng)
        if wins1 > wins2:
            result = r["team1"]
        elif wins2 > wins1:
            result = r["team2"]
        else:
            result = "TIE"
        rows.append({
            "season": r["season"],
            "league": r["league"],
            "division": r["division"],
            "team1": r["team1"],
            "team2": r["team2"],
            "result": result,
            "wins1": wins1,
            "wins2": wins2,
            "ties": ties, 
            "games_played": n_games,
        })
    return rows

def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

def verify(real_rows, fake_rows, p_draw):
    assert len(fake_rows) == len(real_rows), f"expected {len(real_rows)} rows, got {len(fake_rows)}"
    for real, fake in zip(real_rows, fake_rows):
        for col in ["season", "league", "division", "team1", "team2"]:
            assert real[col] == fake[col], f"{col} differs for {real}"
        assert fake["wins1"] + fake["wins2"] + fake["ties"] == fake["games_played"], f"counts don't add up for {fake}"
        if p_draw == 0:
            assert fake["ties"] == 0, f"unexpected draw in {fake}"
            assert fake["games_played"] == int(real["wins1"]) + int(real["wins2"]), f"games differ for {real}"
        else:
            assert fake["games_played"] == int(real["games_played"]), f"games differ for {real}"

    games = sum(r["games_played"] for r in fake_rows)
    ties = sum(r["ties"] for r in fake_rows)
    tied_series = sum(1 for r in fake_rows if r["result"] == "TIE")
    print(f"Checks passed: {len(fake_rows)} rows, same teams and pairs as the real file.")
    print(f"Fake games: {games}, drawn: {ties} ({ties / games:.1%}), "
          f"tied series: {tied_series} ({tied_series / len(fake_rows):.1%}).")
    real_tied = sum(1 for r in real_rows if r["result"] == "TIE")
    print(f"Real tied series: {real_tied} ({real_tied / len(real_rows):.1%}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("league", choices=sorted(LEAGUES))
    parser.add_argument("--run", type = int, default = 1, help = "default run number for the random seed")
    args = parser.parse_args()

    label, p_draw = LEAGUES[args.league]
    rng = random.Random(args.run)
    real_rows = load_real_series(args.league)
    assert all(r["league"] == label for r in real_rows), f"league label in the real file is not {label}"
    fake_rows = make_fake_rows(real_rows, p_draw, rng)
    suffix = f"_{args.run:02d}"
    out_path = f"{FAKE_DIR}/{args.league}_fake_division_series_results{suffix}.csv"
    write_csv(fake_rows, out_path)
    verify(real_rows, fake_rows, p_draw)
    print(f"Written to {out_path}")