# Data files

## Overview

The processed data turns each league into division-level tournaments: in a division, every pair of
teams plays a fixed number of games each season. MLB, NBA and NFL cover 1985-2024. The Premier
League covers 2001-2024 without 2003 and 2004 (missing from the source data) and has no divisions,
so each season is one tournament. Season labels are the start year (NBA 2004 is the 2004-05
season).

| League | Structure | Games per pair | Tied series |
|---|---|---|---|
| MLB | 5 eras, divisions of 4-7 teams (6 divisions of 5 since 2013) | 5-20 (13 only in 2023-24) | 154 (6%) |
| NBA | 9 eras, 4 divisions of 5-8 teams until 2003, 6 divisions of 5 since 2004 | 4-6, mostly 4 | 602 (22%) |
| NFL | 5 eras, 6 divisions of 4-6 teams until 2001, 8 divisions of 4 since 2002 | 2 | 853 (41%) |
| Premier League | one tournament of 20 teams per season | 2 (home and away) | 1,215 (29%) |

Division membership is not in the game log, so it comes from league history. `Notes.md` describes
how much of it was checked. Division names are not consistent across leagues (`AL-East`,
`AFC-East`, `Atlantic`, `Premier-League`); this is still open.

## Original data

- `game_data_us_leagues.csv` (about 181,000 rows): game results for MLB, NBA and NFL back to 1980,
  one row per game. Columns: `season, date, league, team1, team2, result, score1, score2`.
  `result` is 1 for a team1 win, -1 for a team2 win and 0 for a tie.
- `game_data_premier_league.csv` (8,360 rows): Premier League games, 2001-2024 without 2003 and
  2004. Columns: `season, date, home_team, away_team, hometeamgoals, awayteamgoals,
  hometeamresult, home_team_points, away_team_points`. `hometeamresult` is 1 for a home win, -1 for
  an away win and 0 for a draw. It has no `league` column, so it is not laid out like the US file.
- `mlb_teams.csv`, `nba_teams.csv`, `nfl_teams.csv`, `prem_teams.csv`: team names and codes for each
  league. `mlb_teams.csv` uses `WAS` for the Nationals, as the game log does, not `WSH`.

## Processed data

Each league has two files, made by the scripts in `scripts/`:

- `<league>_division_membership.csv`: one row per division per season. Columns: `season, league,
  division, teams`. `teams` is the alphabetical tuple of team codes, for example
  `(BAL,BOS,NYA,TBA,TOR)`.
- `<league>_division_series_results.csv`: one row per pair of teams in the same division per season
  (`team1` comes before `team2` alphabetically). Columns: `season, league, division, team1, team2,
  result, wins1, wins2, ties, games_played`. `result` is the code of the series winner, or `TIE` if
  `wins1` equals `wins2`. `ties` is the number of games in the series that ended tied (or drawn),
  and `games_played` is the number of games the pair played that season.

| League | Membership rows | Results rows |
|---|---|---|
| MLB | 222 | 2,503 |
| NBA | 202 | 2,778 |
| NFL | 286 | 2,059 |
| Premier League (`prem_`, league `PL`) | 22 | 4,180 |

`anomalies/` has evidence files for tied series and schedule irregularities, described in
`anomalies/README.md`.

## Analysis files

The notebooks in `scripts/` write one file per league to the top-level `Analysis/` folder:
`<league>_analysis.csv`, with one row per division-season (MLB 222, NBA 202, NFL 286). Columns:

- `season`, `division`
- `num_teams`: number of teams in the division
- `games_per_pair`: games played by the first pair in the division (not exact in irregular seasons)
- `teams`: the teams, ranked by score
- `scoring_sequence`: the matching scores (series won; a tied series adds nothing to either team)
- `upset_strict`: upsets when a tied series between teams with different scores counts 0
- `upset_weak`: the same, with such a tied series counting 1/2

Example: `2024,NL-East,5,13,"('ATL', 'PHI', 'NYN', 'WAS', 'MIA')","(3, 3, 2, 2, 0)",1,1.0`

All tournaments are kept. Filters such as "5-team divisions only" are applied when computing
results. `prem_analysis.csv` is not built yet.
