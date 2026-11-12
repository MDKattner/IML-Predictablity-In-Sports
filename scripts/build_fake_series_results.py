import argparse
import csv 
import os 
import random
from pathlib import Path

DATA_DIR = "Data"
FAKE_DIR = f"{DATA_DIR}/fake"
SEEDS = (1, 2, 3, 4, 5)

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
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
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

def generate_results(league, seed, output=None, reuse=False):
    label, p_draw = LEAGUES[league]
    rng = random.Random(seed)
    real_rows = load_real_series(league)
    assert all(r["league"] == label for r in real_rows), f"league label in the real file is not {label}"
    fake_rows = make_fake_rows(real_rows, p_draw, rng)
    out_path = Path(output or f"{FAKE_DIR}/fake{seed:02d}_{league}_division_series_results.csv")
    legacy_path = Path(f"{FAKE_DIR}/{league}_fake{seed:02d}_division_series_results.csv")
    existing = out_path if out_path.exists() else legacy_path
    if reuse and existing.exists():
        with existing.open(newline="") as f:
            actual = list(csv.DictReader(f))
        expected = [{k: str(v) for k, v in row.items()} for row in fake_rows]
        if actual != expected:
            raise ValueError(f"{existing}: does not match seed {seed} and current inputs")
        if existing != out_path:
            existing.rename(out_path)
        print(f"Reused verified seed {seed}: {out_path}")
    else:
        write_csv(fake_rows, out_path)
        print(f"Written seed {seed} to {out_path}")
    verify(real_rows, fake_rows, p_draw)
    return out_path


def run_batch():
    """Reuse verified mirrors and execute only the notebook's function cell."""
    import ast
    import json

    notebook = Path(__file__).with_name("generic_datascripts.ipynb")
    cells = json.loads(notebook.read_text())["cells"]
    function_cells = []
    for cell in cells:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if any(isinstance(node, ast.FunctionDef) and node.name == "generate_analysis"
                   for node in ast.parse(source).body):
                function_cells.append(source)
    if len(function_cells) != 1:
        raise ValueError(f"{notebook}: expected one generate_analysis function cell")
    namespace = {}
    exec(compile(function_cells[0], str(notebook), "exec"), namespace)
    generate_analysis = namespace["generate_analysis"]

    analyses = {
        "mlb": ("mlb", 0), "nba": ("nba", 0), "nfl": ("nfl", 0),
        "prem": ("premier_league", 0.5), "bund": ("bundesliga", 0.5),
    }
    for league, (name, tie_score) in analyses.items():
        for seed in SEEDS:
            series_file = generate_results(league, seed, reuse=True)
            generate_analysis(
                series_file=series_file,
                output_file=f"Analysis/fake{seed:02d}_{name}_analysis.csv",
                membership_file=f"{DATA_DIR}/{league}_division_membership.csv",
                tie_score=tie_score,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("league", choices=sorted(LEAGUES), nargs="?")
    parser.add_argument("--run", type=int, help="random seed (default: 1)")
    parser.add_argument("-o", "--output", help="results CSV path for a single run")
    parser.add_argument("--batch", action="store_true",
                        help="generate/reuse seeds 1-5 for all leagues and analyze them")
    args = parser.parse_args()
    if args.batch:
        if args.league is not None or args.run is not None or args.output is not None:
            parser.error("--batch cannot be combined with league, --run, or --output")
        run_batch()
    else:
        if args.league is None:
            parser.error("provide a league or --batch")
        generate_results(args.league, args.run if args.run is not None else 1, args.output)
