"""Summarize each analysis CSV independently; no generation or analysis is run."""

import argparse
import csv
import math
from pathlib import Path
from statistics import mean, stdev

METRICS = ("upset_strict_frequency", "upset_weak_frequency")
FIELDNAMES = ("source_file", "strict_mean", "strict_std", "weak_mean", "weak_std")


def summarize(source_file):
    values = {column: [] for column in METRICS}
    with open(source_file, newline="") as f:
        reader = csv.DictReader(f)
        for column in METRICS:
            if column not in (reader.fieldnames or []):
                raise ValueError(f"{source_file}: missing required column {column}")
        for row_number, row in enumerate(reader, start=2):
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
    args = parser.parse_args()
    try:
        rows = [summarize(path) for path in args.analysis_files]
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
