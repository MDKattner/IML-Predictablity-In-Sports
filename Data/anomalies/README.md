# Anomalies

Evidence files for irregularities in the data, and for features that are expected but matter for
the upset analysis (tied series, schedule variation). Nothing was removed from the
data, this is more for documentation. The files are written by the `build_<league>_division_series_results.py` scripts, except
`mlb_ties.csv`, which comes from `scripts/find_mlb_ties.py`.

MLB, NBA and NFL each have a games-played variation file and a tied series file. MLB and NFL also
have a file of tied games, because their games can end tied; NBA games always have a winner. The
Premier League only has a tied series file: every pair plays exactly 2 games, and its drawn games
are in the `ties` column of the results file.

## MLB

- `mlb_games_played_variation.csv`: for each season, the distinct numbers of games played per pair
  (separated by `;`). Columns: `season, distinct_games_played_counts`. The count ranges from 5 to 20
  and is often even; only 2023-2024 have exactly 13. 1994 (strike, as few as 5), 1995 and 2020
  (COVID, 10) stand out.
- `mlb_tied_division_series.csv`: pairs whose series ended with equal wins, 154 in 1985-2024.
  Columns: `season, division, team1, team2, wins1, wins2, ties, games_played`. They are common
  because many seasons had an even number of games per pair. Each counts 0 as a strict upset and
  1/2 as a weak upset.
- `mlb_ties.csv`: every MLB game from 1985 to 2024 that ended tied (`result == 0`), 21 games, 13
  between division teams and 8 between others. These are suspended or rain-shortened games that
  were never finished. Columns: `season, date, league, team1, team2, result, score1, score2`.
- `mlb_individual_tie_games_in_division.csv`: division pairs whose series had at least one tied
  game, 13 in 1985-2024. Columns: `season, division, team1, team2, ties, games_played`. For these
  pairs `wins1 + wins2` is less than `games_played`, which is why the results file has `ties`.

## NBA

- `nba_games_played_variation.csv`: games per pair by season. 5-6 in 1985-88, 4-6 in 1989-94, 4-5 in
  1995-2003 (3-4 in the 1998 lockout season), and 4 in 2004-2024 except the disrupted seasons (2011
  lockout, 2018, 2019-20 COVID, 2023).
- `nba_tied_division_series.csv`: pairs whose series ended level (2-2, or 3-3 in 6-game series),
  602 in 1985-2024. This is expected with an even number of games per pair. Same columns as the
  MLB file.

## NFL

- `nfl_games_played_variation.csv`: games per pair by season. It is 2 in every season except 1987
  (players' strike), when the log has only 12 games per team and pairs played 1 or 2 games.
- `nfl_tied_division_series.csv`: pairs whose two games were split 1-1 (or tied), 853 in 1985-2024.
  Expected with only two games per pair. Same columns as the MLB file.
- `nfl_individual_tie_games_in_division.csv`: division pairs with a tied game (after overtime), 10
  pairs in 1985-2024. There are 21 tied games in all, 11 of them between teams in different
  divisions. Columns: `season, division, team1, team2, ties, games_played`.

## Premier League

- `prem_tied_division_series.csv`: pairs whose two games ended level, either a win and a loss or
  two draws, 1,215 in 2001-2024 (950 a win and a loss, 265 two draws ~29%). Expected with two games per
  pair. Same columns as the MLB file, where `ties` is the number of drawn games.

The Premier League game log also has no 2003 and 2004 seasons (see `Notes.md`).

## Irregular seasons

These seasons have different game counts from the standard schedule. All are kept in the data.

| League | Season | What the log shows |
|---|---|---|
| NFL | 1987 | strike, 12 games per team, many division pairs played once |
| NBA | 1998 | lockout, 50 games per team |
| NBA | 2011 | lockout, 66 games per team |
| NBA | 2019 | COVID suspension, 64-75 games per team |
| NBA | 2020 | 72 games per team |
| NBA | 2018 | 1,228 games instead of 1,230, BOS-PHI have 3 games (cause unknown) |
| NBA | 2023 | four division pairs have 5 games (BOS-NYK, IND-MIL, LAL-PHX, PHX-SAC), cause unknown |
| NBA | 2012 | BOS and IND have 81 games, not division rivals, no effect |
| NFL | 2022 | BUF and CIN have 16 games (cancelled game), not division rivals, no effect |
| MLB | 1994, 1995, 2020 | strike (1994-95) and COVID (2020) seasons |

`Notes.md` explains how these are handled.
