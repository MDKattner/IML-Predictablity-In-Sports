# Scripts

Code that generates the processed data in `Data/` (the `.py` scripts) and the analysis outputs in
`Analysis/` (the `.ipynb` notebooks, see the last section). All `.py` paths are relative to the
**repo root**, so run each script from the repo root (not from inside `scripts/`). The `.py`
scripts use the standard library only. Within a league, run membership before the series-results
script — the latter reads the membership file the former produces.

```
# MLB
python3 scripts/build_mlb_division_membership.py
python3 scripts/build_mlb_division_series_results.py
python3 scripts/find_mlb_ties.py

# NBA
python3 scripts/build_nba_division_membership.py
python3 scripts/build_nba_division_series_results.py

# NFL
python3 scripts/build_nfl_division_membership.py
python3 scripts/build_nfl_division_series_results.py
```

All three leagues cover 1985–2024.

---

## Membership scripts

Each `build_<league>_division_membership.py` writes `Data/<league>_division_membership.csv`
(one row per season per division). Division membership is not in the game log, so each script
holds it as hardcoded era tables (`ERAS`) compiled from documented league history. They build a
"long" format internally (one row per season/division/team) for verification, then collapse to
the final tuple format. Each `verify()` asserts that every season is present, that team counts
match history, and that the membership's team codes match the game log exactly (both directions)
for every season. The scripts differ in how much *division placement* they can check:

### build_mlb_division_membership.py
5 realignment eras (1985–92, 1993, 1994–97, 1998–2012, 2013–24). `CODE_CHANGES` applies the three
franchise abbreviation changes (CAL→ANA 1997, MON→WAS 2005, FLO→MIA 2012). Verification confirms
team *codes* only — the log has no division column, so a team placed in the wrong division would
still pass.

### build_nba_division_membership.py
9 eras (1985–87, 1988, 1989, 1990, 1991–94, 1995–2000, 2001, 2002–03, 2004–24).
`resolve_code()` translates a franchise's canonical code to the code used in the game log each
season (NJN→BKN 2012, SEA→OKC 2008, and the non-monotonic New Orleans NOH→NOK→NOH→NOP).
Extra verification beyond codes:
- the East/West split of every season 1985–2003 must match the schedule (cross-conference pairs
  play far fewer games than same-conference pairs);
- West 1985–94 and East 1988–94: the divisions are recovered from the schedule (division rivals
  play more games) and must equal the declared ones; the placement of the 1988–90 expansion
  teams comes from this;
- East 1995–2003: pairs that played only 3 games are never in the same division (a necessary
  condition only).
Not verifiable from the schedule: East 1985–87, West 1995–2003, and division placement in
2004–24; those come from documented history and should be spot-checked against
Basketball-Reference.

### build_nfl_division_membership.py
5 eras (1985–94, 1995, 1996–98, 1999–2001, 2002–24). The game log already uses present-day
franchise codes in every season (Oilers→TEN, Colts→IND, Cardinals→ARI, Rams→LAR, Chargers→LAC,
Raiders→LV), so no code resolution is needed. Extra verification: every pair of teams in a
division must have played **exactly two games** that season (division rivals play twice), which
confirms the division placements. 1987 (players' strike) is the one exception: the log has only
12 games per team, so each pair must have played at least once.

**Input (all three):** `Data/game_data_us_leagues.csv`.

---

## Series-results scripts

Each `build_<league>_division_series_results.py` writes `Data/<league>_division_series_results.csv`
plus the league's evidence files in `Data/anomalies/`.

For each game of the league, it looks up both teams' divisions for that season; if they match, the
game counts toward that pair's head-to-head series. One output row per pair per season with wins,
ties, games played, and the series winner (`result` = winner's code, or `TIE` on equal wins).

**Verification** (`verify`): the row count equals the expected intra-division pair count (sum of
n-choose-2 over every season/division, via `math.comb`), and `wins1 + wins2 + ties ==
games_played` for every row.

**Discrepancy report:** writes the games-per-pair variation and the tied series; the MLB and NFL
scripts also write the pairs whose series included a tied individual game (NBA games always have
a winner).

**Inputs:** `Data/<league>_division_membership.csv`, `Data/game_data_us_leagues.csv`.

## find_mlb_ties.py

Writes `Data/anomalies/mlb_ties.csv`: every MLB game 1985–2024 with `result == 0`
(suspended/rain-shortened games). Standalone. **Input:** `Data/game_data_us_leagues.csv`.

---

## Analysis notebooks (`mlb_datascripts.ipynb`, `nba_datascripts.ipynb`, `nfl_datascripts.ipynb`)

**Produce:** `Analysis/<league>_scoring_sequence.csv` and `Analysis/<league>_upset_counts.csv`.

Run these after the `.py` scripts above. Each notebook reads
`Data/<league>_division_series_results.csv`, converts each series winner to 1 / -1 / 0, computes
each team's division score (series wins) per season, and counts the upsets per season and
division. Run them with Jupyter from this folder (they use `../Data/` and `../Analysis/` paths);
they need `pandas`.
