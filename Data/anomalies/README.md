# Scripts

Scripts that generate the processed MLB data files in `Data/` from the raw game log. All paths
are relative to the **repo root**, so run each script from the repo root (not from inside
`scripts/`):

```
python3 scripts/build_division_membership.py
python3 scripts/build_division_series_results.py
python3 scripts/find_ties.py
```

All three read from `Data/game_data_us_leagues.csv` and write their output into `Data/`. They
have no third-party dependencies (standard library only). Run them in the order listed above:
`build_division_series_results.py` depends on the membership file produced by
`build_division_membership.py`.

---

## build_division_membership.py

**Produces:** `Data/mlb_division_membership.csv` (one row per season per division, 1985–2024).

Encodes MLB division membership for all 5 realignment eras as hardcoded domain knowledge
(`ERAS`), because the game log has no league/division column — which teams were in which division
is external historical knowledge, not something derivable from the data. On top of the era
tables, `CODE_CHANGES` applies the three franchise abbreviation changes (CAL→ANA in 1997,
MON→WAS in 2005, FLO→MIA in 2012); these changed only the code used in the data, not the team's
division.

Builds the data in a "long" format internally (one row per season/division/team) for easy
verification, then collapses it to the final tuple format (one row per season/division, teams as
an alphabetically-sorted parenthesized string like `(BAL,BOS,NYA,TBA,TOR)`).

**Verification** (`verify`): asserts all 40 seasons 1985–2024 are present, asserts the team count
per season matches documented history (26 teams 1985–92, 28 for 1993–97, 30 from 1998 on), and
cross-checks that every team code in the membership file actually appears in the game log for
that season. Prints a confirmation line if all checks pass; raises `AssertionError` otherwise.

**Input:** `Data/game_data_us_leagues.csv` (for the cross-check only).

---

## build_division_series_results.py

**Produces:** `Data/mlb_division_series_results.csv` (one row per intra-division team pair per
season) plus three anomaly evidence files in `Data/anomalies/` (see `Data/anomalies/README.md`).

For each MLB game in the log, looks up both teams' divisions for that season (via the membership
file). If both teams are in the *same* division, the game is counted toward that pair's
head-to-head series. Aggregates each pair's games into a single row: total wins for each team,
number of tied individual games, total games played, and the series winner (`result` = the
winning team's code, or `TIE` if the two teams have equal wins).

**Verification** (`verify`): asserts the row count equals the expected number of intra-division
pairs (sum of "n choose 2" over every season/division in the membership file — handles the
variable division sizes across eras via `math.comb`), and asserts `wins1 + wins2 + ties ==
games_played` for every row.

**Discrepancy report** (`print_discrepancy_report`): prints and writes evidence for three data
irregularities — the distinct games-played-per-pair counts per season, the tied division series
(wins1 == wins2), and the pairs whose series included at least one individual tie game. Creates
`Data/anomalies/` if it doesn't exist.

**Inputs:** `Data/mlb_division_membership.csv`, `Data/game_data_us_leagues.csv`.

---

## find_ties.py

**Produces:** `Data/mlb_ties_1985_2024.csv`.

Scans the game log for every MLB game in 1985–2024 with `result == 0` (a tie — a game that was
suspended/rain-shortened and never completed), and writes those raw game rows out sorted by
season and date. Prints the total count found (21). Standalone — does not depend on the other
two scripts.

**Input:** `Data/game_data_us_leagues.csv`.
