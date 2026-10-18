# Scripts

The `.py` scripts build the processed data in `Data/`. The notebooks build the files in `Analysis/`.
Run each script from the repo root, not from inside `scripts/`. They only use the standard library.
Run a league's membership script before its series results script, because the second reads the
output of the first.

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

# Premier League
python3 scripts/build_prem_division_membership.py
python3 scripts/build_prem_division_series_results.py
```

MLB, NBA and NFL cover 1985-2024. The Premier League covers 2001-2024 without 2003 and 2004,
which are missing from the source data.

## Membership scripts

Each `build_<league>_division_membership.py` writes `Data/<league>_division_membership.csv`, one
row per division per season. The game log has no division column, so MLB, NBA and NFL keep the
divisions in era tables in the script. Each script checks that every season is present, that the
team counts are right, and that the team codes match the game log. Beyond that:

- MLB (5 eras): applies the three code changes (CAL to ANA 1997, MON to WAS 2005, FLO to MIA 2012).
  Division placement cannot be checked, since the log only has team codes.
- NBA (9 eras): translates each franchise to the code the log uses that season (NJN to BKN in 2012,
  SEA to OKC in 2008, the New Orleans codes, VAN to MEM). It also checks the East/West split for
  1985-2003 and recovers the West 1985-94 and East 1988-94 divisions from the schedule. East
  1985-87, West 1995-2003 and 2004-2024 cannot be checked this way.
- NFL (5 eras): the log already uses present-day codes. Every pair in a division must have played
  exactly twice, which confirms the placements. 1987 (strike) only needs at least one game.
- Premier League: no divisions, so no era tables. The teams of each season are read from the log,
  and the script checks the season list, 20 teams and 380 games per season, and that every
  home/away pairing happens exactly once.

The placements that could not be checked in the scripts were compared with the Wikipedia season
pages (see `Data/Notes.md`).

## Series results scripts

Each `build_<league>_division_series_results.py` writes `Data/<league>_division_series_results.csv`
and the league's evidence files in `Data/anomalies/`. For every game it looks up both teams'
divisions for that season. If they match, the game counts toward that pair's series. The output has
one row per pair per season, with wins, ties, games played and the winner (`result` is the winner's
code, or `TIE` on equal wins).

`verify` checks that the row count equals the number of pairs (the sum of n-choose-2 over the
divisions) and that `wins1 + wins2 + ties` equals `games_played` on every row. The Premier League
script also checks that `games_played` is 2.

The Premier League log is laid out differently: it has `home_team`, `away_team` and
`hometeamresult` (1 home win, -1 away win, 0 draw) and no `league` column. A draw goes in `ties`.

Each script writes its tied series to `Data/anomalies/`. MLB and NFL also write the pairs with a
tied individual game, and MLB, NBA and NFL write a games-per-pair variation file. The Premier League
has neither, since every pair plays exactly 2 games.

## find_mlb_ties.py

Writes `Data/anomalies/mlb_ties.csv`, every MLB game from 1985 to 2024 with `result == 0`
(suspended or rain-shortened games). Input: `Data/game_data_us_leagues.csv`.

## Analysis notebooks

`mlb_datascripts.ipynb`, `nba_datascripts.ipynb` and `nfl_datascripts.ipynb` write
`Analysis/<league>_analysis.csv`, one row per division-season. Run them after the scripts above.

Each notebook reads `Data/<league>_division_series_results.csv`, turns the series winner into
1, -1 or 0, and adds up each team's series wins as its score. It then counts upsets in two ways:

- `upset_strict`: a tied series between teams with different scores is not an upset
- `upset_weak`: such a tied series counts as 1/2 upset

Finally it collapses each division-season into one row: `season, division, num_teams,
games_per_pair, teams, scoring_sequence, upset_strict, upset_weak`. `teams` and `scoring_sequence`
are tuples ranked by score, and `games_per_pair` comes from the first pair in the division.

Run them in Jupyter from this folder (they use `../Data/` and `../Analysis/`). They need `pandas`,
and are saved with their outputs cleared. There is no Premier League notebook yet.
