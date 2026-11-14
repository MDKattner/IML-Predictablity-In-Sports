"""Summarize each analysis CSV independently; no generation or analysis is run."""

import argparse
import csv
import math
from pathlib import Path
from statistics import mean, stdev

METRICS = ("upset_strict_frequency", "upset_weak_frequency")
FIELDNAMES = ("source_file", "strict_mean", "strict_std", "weak_mean", "weak_std")


def parse_num_teams(rules):
    """Turns ["mlb=5", "nfl=4"] into {"mlb": 5, "nfl": 4}."""
    parsed = {}
    for rule in rules:
        league, _, count = rule.partition("=")
        if not league or not count.isdigit():
            raise ValueError(f"--num-teams expects league=number, got {rule!r}")
        parsed[league] = int(count)
    return parsed


def num_teams_for(source_file, num_teams):
    """The team count to keep for this file, or None to keep every row.
    A rule for mlb applies to mlb_analysis.csv and to every fakeNN_mlb_analysis.csv."""
    name = Path(source_file).name
    for league, count in num_teams.items():
        if name == f"{league}_analysis.csv" or name.endswith(f"_{league}_analysis.csv"):
            return count
    return None


def summarize(source_file, keep_num_teams=None):
    values = {column: [] for column in METRICS}
    with open(source_file, newline="") as f:
        reader = csv.DictReader(f)
        for column in METRICS:
            if column not in (reader.fieldnames or []):
                raise ValueError(f"{source_file}: missing required column {column}")
        if keep_num_teams is not None and "num_teams" not in (reader.fieldnames or []):
            raise ValueError(f"{source_file}: missing required column num_teams")
        for row_number, row in enumerate(reader, start=2):
            if keep_num_teams is not None and int(row["num_teams"]) != keep_num_teams:
                continue
            for column in METRICS:
                raw = (row[column] or "").strip()
                if not raw:
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    raise ValueError(
                        f"{source_file}: column {column}, row {row_number}: invalid value {raw!r}"
                    ) from None
                if math.isnan(value):
                    continue
                if not math.isfinite(value):
                    raise ValueError(
                        f"{source_file}: column {column}, row {row_number}: nonfinite value {raw!r}"
                    )
                values[column].append(value)

    result = {"source_file": source_file}
    for prefix, column in zip(("strict", "weak"), METRICS):
        observations = values[column]
        result[f"{prefix}_mean"] = mean(observations) if observations else ""
        result[f"{prefix}_std"] = stdev(observations) if len(observations) > 1 else ""
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_files", nargs="+", help="real or fake analysis CSV paths")
    parser.add_argument("-o", "--output", required=True, help="summary CSV path")
    parser.add_argument("--num-teams", nargs="+", default=[], metavar="LEAGUE=N",
                        help="keep only divisions with N teams for that league, e.g. mlb=5 nba=5 nfl=4")
    args = parser.parse_args()
    try:
        num_teams = parse_num_teams(args.num_teams)
        for league in num_teams:
            if not any(num_teams_for(path, {league: 0}) is not None for path in args.analysis_files):
                raise ValueError(f"--num-teams {league}: no analysis file matches this league")
        rows = [summarize(path, num_teams_for(path, num_teams)) for path in args.analysis_files]
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
