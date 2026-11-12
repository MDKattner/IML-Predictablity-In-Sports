# Notes on the division data

How the division data was built and what to keep in mind when using it. MLB, NBA and NFL cover
1985-2024. The Premier League and the Bundesliga cover 2001-2024.

## What the data is

Each division in each season is one tournament: its teams and every pair's head-to-head record
that season.

| League | Tournaments | Teams per tournament | Series (team pairs) | Team-seasons |
|---|---|---|---|---|
| MLB | 222 | 4-7 | 2,503 | 1,158 |
| NBA | 202 | 5-8 | 2,778 | 1,147 |
| NFL | 286 | 4-6 | 2,059 | 1,229 |
| Premier League | 24 | 20 | 4,560 | 480 |
| Bundesliga | 24 | 18 | 3,672 | 432 |

The Premier League and the Bundesliga have no divisions, so each season is one tournament of all
the teams in the league.

Every league has a membership file and a series results file in `Data/`, plus evidence files in
`Data/anomalies/`. The columns are described in `Data/README.md`.

## Where division membership comes from

The game log has no division column, so each membership script holds the divisions as era tables
taken from league history. What each script checks:

| League | Team codes vs game log | Division placement |
|---|---|---|
| MLB | every season | not checked |
| NBA | every season | partly, see the NBA section |
| NFL | every season | every season (division rivals play exactly twice) |
| Premier League | read from the log | one tournament per season; every pair plays twice, checked every season |
| Bundesliga | read from the log | same as the Premier League |

The placements the scripts cannot check were compared by hand with the Wikipedia season pages, one
season per era: MLB 1985, 1993, 1994, 1997, 1998, 2012, 2013 and NBA 1985, 1988, 1989, 1990, 1994,
1995, 1999, 2001, 2002, 2004, 2023. All matched. Other seasons rely on the era tables staying
constant within an era.

## MLB

There are five eras:

| Seasons | Structure | Teams |
|---|---|---|
| 1985-1992 | 2 divisions per league (East, West) | 26 |
| 1993 | same, after expansion | 28 |
| 1994-1997 | 3 divisions per league (East, Central, West) | 28 |
| 1998-2012 | 3 divisions per league | 30 |
| 2013-2024 | current alignment | 30 |

Divisions have 4 to 7 teams (23 of size 4, 148 of size 5, 31 of size 6, 20 of size 7).

Three franchises changed their code: CAL became ANA (1997), MON became WAS (2005) and FLO became
MIA (2012). The Rays (`TBA`) and Guardians (`CLE`) kept their codes. Only two teams changed
divisions: Milwaukee moved from the AL Central to the NL Central in 1998, and Houston from the NL
Central to the AL West in 2013.

Games per pair range from 5 to 20, and only 2023-2024 have exactly 13. There are 154 tied series.
21 individual games ended tied (13 between division teams); they count toward `games_played` but
not toward either team's wins, which is why the results file has a `ties` column.

## NBA

The NBA has nine eras. Until 2003 there were 4 divisions of 5-8 teams (Atlantic and Central in the
East, Midwest and Pacific in the West). Since 2004 there are 6 divisions of 5.

- 1985-87: 23 teams, Sacramento in the Midwest.
- 1988: Charlotte and Miami join, Sacramento moves to the Pacific.
- 1989: Minnesota and Orlando join.
- 1990: the expansion teams move around. In 1988 Miami is in the Midwest and Charlotte in the
  Atlantic, in 1989 Charlotte is in the Midwest and Orlando in the Central, and in 1990 Orlando is
  in the Midwest. This comes from the schedule and matches Wikipedia.
- 1991-94: Orlando in the Atlantic.
- 1995-2000: Toronto (Central) and Vancouver (Midwest) join.
- 2001: Vancouver becomes Memphis.
- 2002-03: the Charlotte franchise moves to New Orleans and stays in the East.
- 2004-2024: six divisions of 5.

Before 1995, division rivals played more games than other teams in the same conference, so the
script recovers the divisions from the schedule (West 1985-94, East 1988-94) and checks them against
the declared ones. It also checks the East/West split every season up to 2003, and that East
1995-2003 pairs with only 3 games are never in the same division. Not checkable from the schedule:
East 1985-87, West 1995-2003 and 2004-2024.

The log uses the code of the time, which the script resolves each season: NJN became BKN (2012), SEA
became OKC (2008), VAN became MEM (2001), and New Orleans went NOH, NOK (2005-06), NOH, NOP (2013).
`CHA` after 2004 is the Charlotte Bobcats, a new franchise that reuses the code.

Pairs play 4 to 6 games (mostly 6 in the 1980s, 5 in 1989-94, 4 since 1995), so a series is often
tied: 602 times, 22% of series. NBA games themselves never end tied.

## NFL

Until 2001 there were 6 divisions of uneven size, and since 2002 there are 8 divisions of 4:

- 1985-94: 28 teams, AFC-Central and NFC-West have 4 teams, the other four have 5.
- 1995: Carolina and Jacksonville join.
- 1996-98: the Browns are inactive and the Ravens start in the AFC-Central.
- 1999-2001: the Browns return, AFC-Central has 6 teams.
- 2002-2024: the Texans join and the league realigns into 8 divisions of 4.

The log already uses present-day codes (TEN, IND, ARI, LAR, LAC, LV), so there is no code
resolution. Division rivals play exactly twice, and the script checks this for every pair in every
division, which confirms the placements. The one exception is 1987 (players' strike), when the log
has only 12 games per team and many pairs played once, so the check there is "at least once".

Two games per pair means 853 tied series (41% of series). 21 games ended tied after overtime, 10
of them between division teams. Tied games count for neither team.

## Premier League

20 teams, and every pair plays twice per season, once at each ground (380 games). Each season is
one tournament of 20 teams. The game log has `home_team`, `away_team`, the goals and
`hometeamresult` (1 home win, -1 away win, 0 draw), with no `league` column, so it is laid out
differently from the US log. It covers 2001-2024 (24 seasons, 9,120 games) and comes from
football-data.co.uk. 2003 and 2004 were missing at first and were added from the same source; they
match a second source (engsoccerdata) exactly.

Membership is read from the log, since promotion and relegation change the 20 teams every year.
The script checks the season list, 20 teams and 380 games per season, and that every home/away
pairing happens exactly once.

A series is the two games between a pair, 4,560 in total. A drawn game goes in the `ties` column.
With a win worth 1, a draw 1/2 and a loss 0, the possible series scores are (0, 2), (1/2, 3/2),
(1, 1), (3/2, 1/2) and (2, 0). Only (1, 1) is a tied series. Comparing `wins1` and `wins2` gives
the same winner, since both teams get 1/2 per draw. 1,338 series are tied (29%): 1,035 are a win
and a loss, 303 are two draws. 2,246 games were drawn (25%).

## Bundesliga

18 teams, and every pair plays twice per season, once at each ground (306 games). Like the Premier
League, each season is one tournament, now of 18 teams. It covers 2001-2024 (24 seasons, 7,344
games), so the window matches the Premier League. Everything else about the structure is the same,
including how drawn games and tied series are handled.

**Game log.** `game_data_bundesliga.csv` is our own cleaned log, in the same layout as the Premier
League log. It was built from the football-data.co.uk season files and checked against a second
source (engsoccerdata), with no differences in any date, team or score. We kept our own cleaned log
and not the raw files because the source limits its use to private use and match prediction. The
raw files needed some care: one season is in a different text encoding, another starts with a
byte-order mark, and the date format changes in 2018-19. Club codes are our own, three letters,
38 clubs in all. They are never taken from the city alone, since Munich, Berlin and Hamburg each
had two clubs in the league.

Membership is read from the log, as for the Premier League, and the script checks the season list,
18 teams and 306 games per season, and that every home/away pairing happens exactly once. There are
3,672 series: 1,161 are tied (32%), of which 922 are a win and a loss and 239 are two draws. 1,817
games were drawn (25%). The relegation play-offs between the 16th Bundesliga team and the third
2. Bundesliga team are not league games and are not in the log. The 2019-20 season was suspended
for COVID, but all 306 games were played.

**Official results.** The log holds the official result of every game. One game differs from what
was played on the pitch: Union Berlin v Bochum on 14 December 2024 ended 1-1, but a lighter hit
Bochum's goalkeeper, and the DFB sports court awarded the game 0-2 to Bochum in January 2025 (the
appeal was rejected in February). We used the official 0-2, which makes that pair's series a Bochum
win. With the pitch result, both games would have been draws and the series would be tied. It is
one series out of 3,672, in the 2024 tournament only. Two other games were abandoned and awarded
0-2 (St. Pauli v Schalke in 2010-11 and Bochum v Gladbach in 2021-22, both after a cup hit an
assistant referee), but that was the score when play stopped, so the winner is the same. Nürnberg
v Wolfsburg in 2007-08 was abandoned at half-time because of rain and replayed in full on 20 April
2008; the log only holds the replay.

## Irregular seasons

These seasons have different game counts from the standard schedule. All of them are kept in the
data.

| League | Season | What happened | Tournaments affected |
|---|---|---|---|
| NFL | 1987 | strike, 12 games per team, many pairs played once | 6 of 286 |
| NBA | 1998 | lockout, 50 games per team | 4 of 202 |
| NBA | 2011 | lockout, 66 games per team | 6 |
| NBA | 2019 | COVID suspension, 64-75 games per team | 6 |
| NBA | 2020 | 72 games per team | 6 |
| NBA | 2018 | 1,228 games instead of 1,230, BOS-PHI have 3 games (cause unknown) | 1 series |
| NBA | 2023 | four division pairs have 5 games (cause unknown) | 4 series |
| NBA | 2012 | BOS and IND have 81 games, not division rivals | none |
| NFL | 2022 | BUF and CIN have 16 games (cancelled game), not division rivals | none |
| MLB | 1994, 1995, 2020 | strike and COVID seasons | 12 of 222 (1994, 2020) |

Whether to exclude or mark the shortened seasons in comparisons is still open.

## How we define an upset

Take two teams in a division with season scores s1 and s2. A team's score is the number of
division series it won.

- If s1 equals s2, the pair is skipped. It is neither an upset nor a non-upset.
- Otherwise, say s1 is larger. If the higher-scoring team won the series, there is no upset. If the
  lower-scoring team won, that is 1 upset. If the series was tied, it depends on the version:
  - strict upset: the tie counts 0
  - weak upset: the tie counts 1/2

The two counts are the same when a tied series is impossible (an odd number of games per pair), and
the weak count is higher by 1/2 for every tied series between teams with different scores.

This differs from the graph theory literature (Fulkerson 1965, Brualdi and Li 1983), which breaks
equal scores using an arbitrary team order. That makes the upset count depend on how the teams are
labelled and has no meaning for real results, so we skip those pairs instead. As a result, upsets
are no longer the above-diagonal entries of a score-sorted adjacency matrix.

## The analysis files

`Analysis/<league>_analysis.csv` has one row per tournament, with the columns `season, division,
num_teams, games_per_pair, teams, scoring_sequence, upset_strict, upset_weak`. `teams` lists the
teams ranked by score and `scoring_sequence` has the matching scores. `games_per_pair` is the number
for the first pair in the division, so it is not exact in the irregular seasons.

How often the two counts differ:

| League | Tournaments | Weak count higher | Tied series between teams with different scores |
|---|---|---|---|
| MLB | 222 | 60 | 100 |
| NBA | 202 | 157 | 413 |
| NFL | 286 | 240 | 486 |

All tournaments stay in the files. Filters such as "5-team divisions only" are applied when
computing results. For the NBA midterm numbers, 129 of the 202 divisions have 5 teams. Their
strict upsets (0, 1, 2) occur (93, 32, 4) times, and for 2004-2024 only it is (90, 32, 4) out of 126.

The Premier League file is `premier_league_analysis.csv`, which does not follow the `prem_` prefix
used by the other Premier League files; the name is still to be settled. It was built before 2003
and 2004 were added and has 22 rows, so it needs a rerun. Its notebook (`prem_datascripts.ipynb`)
scores a tied series as 1/2 point (a series win is 1), unlike the MLB, NBA and NFL notebooks, where
a tied series adds nothing. The Bundesliga analysis file is not built yet.

## Open questions

- Tied series in the scores. In the MLB, NBA and NFL analysis files a tied series adds nothing to
  either team's score, while the Premier League file gives it 1/2 point. Earlier meetings counted
  it as 1/2 a point. The leagues should use the same rule; switching the US leagues would change
  some scoring sequences and upset counts.
- The shortened seasons: keep, mark or drop them.
- Upset counts depend on the number of teams (4-8 in a division, 18 in the Bundesliga, 20 in the
  Premier League), so compare frequencies, not counts.
- Division names are not consistent: `AL-East` (MLB), `AFC-East` (NFL), `Atlantic` (NBA),
  `Premier-League` and `Bundesliga`.
- The analysis file names are not consistent (`premier_league_analysis.csv` against the `prem_`
  prefix).
