# Scripts

Scripts that generate the processed data files in `Data/` from the raw game log. All paths are
relative to the **repo root**, so run each script from the repo root (not from inside `scripts/`).
No third-party dependencies (standard library only). Within a league, run membership before the
series-results script — the latter reads the membership file the former produces.

```
# MLB
python3 scripts/build_mlb_division_membership.py
python3 scripts/build_mlb_division_series_results.py
python3 scripts/find_ties.py

# NBA
python3 scripts/build_nba_division_membership.py
python3 scripts/build_nba_division_series_results.py
```

---

## build_mlb_division_membership.py

**Produces:** `Data/mlb_division_membership.csv` (one row per season per division, 1985–2024).

Encodes MLB division membership for all 5 realignment eras as hardcoded domain knowledge
(`ERAS`), because the game log has no league/division column. `CODE_CHANGES` applies the three
franchise abbreviation changes (CAL→ANA 1997, MON→WAS 2005, FLO→MIA 2012); these changed only the
code used in the data, not the division. Builds a "long" format internally (one row per
season/division/team) for verification, then collapses to the final tuple format.

**Verification** (`verify`): all 40 seasons present; team count per season matches documented
history (26 teams 1985–92, 28 for 1993–97, 30 from 1998 on); every team code appears in the game
log for that season. NOTE: this confirms team *codes*, not division *assignments* — the log has
no division column, so a team placed in the wrong division would still pass.

**Input:** `Data/game_data_us_leagues.csv` (cross-check only).

## build_mlb_division_series_results.py

**Produces:** `Data/mlb_division_series_results.csv` plus three MLB anomaly files in
`Data/anomalies/`.

For each MLB game, looks up both teams' divisions for that season; if they match, counts the game
toward that pair's head-to-head series. One output row per pair per season with wins, ties, games
played, and the series winner (`result` = winner's code, or `TIE` on equal wins).

**Verification** (`verify`): row count equals the expected intra-division pair count (sum of
n-choose-2 over every season/division, via `math.comb`); `wins1 + wins2 + ties == games_played`
for every row.

**Discrepancy report:** writes evidence for the games-per-pair variation, tied series, and
individual tie games.

**Inputs:** `Data/mlb_division_membership.csv`, `Data/game_data_us_leagues.csv`.

## find_ties.py

**Produces:** `Data/mlb_ties_1985_2024.csv`. Scans the log for every MLB game 1985–2024 with
`result == 0` (suspended/rain-shortened games). Standalone. **Input:**
`Data/game_data_us_leagues.csv`.

---

## build_nba_division_membership.py

**Produces:** `Data/nba_division_membership.csv` (one row per season per division, 2004–2024).

Encodes the NBA's modern 6-division-of-5 alignment, which is constant across 2004–2024 (a single
`DIVISIONS` table, no realignment eras — unlike MLB). `resolve_code()` translates a franchise's
canonical code to the code actually used in the game log each season, for the three franchises
that changed code in-window (NJN→BKN 2012, SEA→OKC 2008, and the non-monotonic New Orleans
NOH→NOK→NOH→NOP).

**Verification** (`verify`): all 21 seasons present; exactly 30 teams each season; the membership
code set matches the game-log code set exactly (both directions) per season. Same caveat as MLB:
confirms codes, not division assignments.

**Input:** `Data/game_data_us_leagues.csv` (cross-check only).

## build_nba_division_series_results.py

**Produces:** `Data/nba_division_series_results.csv` plus two NBA report files in
`Data/anomalies/` (games-per-pair variation, tied series).

Same logic as the MLB results script with the league filter set to `"NBA"`. The NBA plays an even
4 games per intra-division pair, so tied series (2–2) are common and expected — recorded because
the upset definition treats a tied series as 1/2 an upset, not because they are errors.

**Inputs:** `Data/nba_division_membership.csv`, `Data/game_data_us_leagues.csv`.
