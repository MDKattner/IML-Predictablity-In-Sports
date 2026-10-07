# Notes — division data (MLB, NBA, NFL, 1985–2024)

Findings, decisions, and data caveats from building the division-level datasets. This is the
narrative companion to the CSVs in `Data/` and the evidence files in `Data/anomalies/`. Written
to be read before using the data for upset analysis. Sections: what the data covers, how division
membership was built and checked, one section per league, the irregular seasons and how they are
handled, then the upset definition and open caveats (which apply to all leagues).

---

## What the dataset covers

All three leagues cover **1985–2024** (40 seasons), reduced to **division-level tournaments**:
within each division each season, every pair of teams plays a fixed set of games, so a division is
a small, clean testbed for the upset question before tackling full leagues. A **tournament** here
means one division in one season, and its teams' season-long head-to-head records.

| League | Tournaments (division-seasons) | Teams per tournament | Series (team pairs) | Team-seasons |
|---|---|---|---|---|
| MLB | 222 | 4–7 | 2,503 | 1,158 |
| NBA | 202 | 5–8 | 2,778 | 1,147 |
| NFL | 286 | 4–6 | 2,059 | 1,229 |

Per league, two processed files (see `Data/README.md` for columns):
`<league>_division_membership.csv` (who was in which division each season) and
`<league>_division_series_results.csv` (head-to-head record for every intra-division pair), plus
evidence files in `Data/anomalies/` (see `Data/anomalies/README.md`).

## Division membership is external knowledge

The game log (`game_data_us_leagues.csv`) has **no league or division column** — only the two
teams and the result. Which teams belonged to which division is historical domain knowledge, not
derivable from the data, so each `build_<league>_division_membership.py` encodes it as era
tables. How much of it can be checked against the data differs by league:

| League | Team codes checked vs game log | Division placement checked against the schedule |
|---|---|---|
| MLB | Yes, every season | No |
| NBA | Yes, every season | Partly (see the NBA section) |
| NFL | Yes, every season | Yes, every season: division rivals play exactly twice |

Placements that are not checked against the schedule come from documented history and should be
spot-checked against a reference (Basketball-Reference, Baseball-Reference).

---

## MLB

### MLB realigned 4 times since 1985 — there are 5 eras

Division count and size are **not** constant across the dataset. Anyone comparing seasons needs
to know this:

| Era | Seasons | Structure | Teams |
|---|---|---|---|
| 1 | 1985–1992 | 2 divisions/league (East, West), no Central | 26 |
| 2 | 1993 | 2 divisions/league, post-expansion | 28 |
| 3 | 1994–1997 | 3 divisions/league (East/Central/West) introduced | 28 |
| 4 | 1998–2012 | 3 divisions/league, 30 teams (AL 14 / NL 16) | 30 |
| 5 | 2013–2024 | 3 divisions/league, current alignment (AL 15 / NL 15) | 30 |

Division sizes range from **4 to 7 teams** (23 tournaments of 4, 148 of 5, 31 of 6, 20 of 7), so
the number of pairs per division is not fixed either. The membership file and all downstream code
handle this via `math.comb` rather than assuming a fixed division size.

### Franchise code changes (same team, different abbreviation)

Three franchises appear under two different codes in the data. These are **not** division changes
— only the abbreviation changed, at the exact season noted (verified against the game log, no
overlap year):

| Franchise | Before | After | Season |
|---|---|---|---|
| Angels | CAL | ANA | 1997 |
| Expos → Nationals | MON | WAS | 2005 |
| Marlins | FLO | MIA | 2012 |

Two rebrands that people assume changed the code but **did not**: Devil Rays → Rays stayed `TBA`
(2008), Indians → Guardians stayed `CLE` (2022). Don't "fix" these.

Note on the team lookup: the game log uses Retrosheet-style codes, so the Nationals are `WAS`.
`mlb_teams.csv` was corrected to use `WAS` (not `WSH`) to stay consistent with the data.

### Two teams actually changed divisions

| Team | From | To | Season |
|---|---|---|---|
| Milwaukee Brewers | AL Central | NL Central | 1998 |
| Houston Astros | NL Central | AL West | 2013 |

No other team changed divisions in 1985–2024; every other change is an era-wide realignment.

### MLB data anomalies

1. **Games per pair is highly variable (5 to 20).** Not a constant 13: it ranges from **5**
   (1994 strike) to **20** and is frequently even. Only **2023–2024** have the clean "exactly 13"
   property (odd, so always a decisive series). Evidence: `anomalies/mlb_games_played_variation.csv`.
2. **Tied division series — 154.** Pairs that finished a season with equal head-to-head wins.
   Common because so many seasons had an even number of games per pair. Evidence:
   `anomalies/mlb_tied_division_series.csv`.
3. **Individual tied games — 21 total, 13 in-division.** Suspended or rain-shortened games never
   completed. Evidence: `anomalies/mlb_ties.csv` (all 21) and
   `anomalies/mlb_individual_tie_games_in_division.csv` (the 13). They count toward `games_played`
   but toward neither team's wins, which is why the results file has a separate `ties` column.

---

## NBA

### Eras

Division structure changed often in the NBA, so there are 9 eras. Until 2003 there were 4
divisions (Atlantic, Central in the East; Midwest, Pacific in the West), of 5–8 teams; from 2004
there are 6 divisions of 5.

| Seasons | Teams | Changes |
|---|---|---|
| 1985–87 | 23 | 4 divisions of 5–6 teams; Sacramento in the Midwest |
| 1988 | 25 | Charlotte and Miami join; Sacramento moves to the Pacific |
| 1989 | 27 | Minnesota and Orlando join |
| 1990 | 27 | Placements of the expansion teams shift (see below) |
| 1991–94 | 27 | Orlando in the Atlantic |
| 1995–2000 | 29 | Toronto (Central) and Vancouver (Midwest) join |
| 2001 | 29 | Vancouver becomes Memphis |
| 2002–03 | 29 | Charlotte franchise relocates to New Orleans (NOH) but stays in the East |
| 2004–24 | 30 | 6 divisions of 5 (Atlantic, Central, Southeast, Northwest, Pacific, Southwest) |

The 1988–90 expansion placements come from the schedule (see below) and look unusual: in 1988
Miami is in the West's Midwest and Charlotte in the East's Atlantic; in 1989 Charlotte is in the
Midwest and Orlando in the East's Central; in 1990 Orlando is in the Midwest. These should be
confirmed against Basketball-Reference.

### How the divisions were derived and checked

Before 1995 division rivals played more games than other same-conference teams, so the divisions
were recovered from the schedule (West 1985–94, East 1988–94) and the script asserts they equal
the declared ones. For every season 1985–2003 the East/West split is also checked (cross-conference
pairs play far fewer games). East 1995–2003 has only a necessary-condition check (pairs that played
3 games are never division rivals). **Not verifiable from the schedule:** East 1985–87 (all
same-conference pairs play the same number of games), West 1995–2003 (all pairs play 4 games),
and division placement in 2004–24. Those come from documented history; spot-check them.

### Franchise code changes

The log uses period-correct codes, so the membership script resolves a few per season:

| Franchise | Codes (by season) |
|---|---|
| New Jersey → Brooklyn Nets | `NJN` (to 2011) → `BKN` (2012+) |
| Seattle → Oklahoma City | `SEA` (to 2007) → `OKC` (2008+) |
| Charlotte Hornets → New Orleans | `CHA` (1988–2001) → `NOH` (2002–04, 2007–12) → `NOK` (2005–06, post-Katrina) → `NOP` (2013+) |
| Vancouver → Memphis | `VAN` (to 2000) → `MEM` (2001+) |

`CHA` also appears from 2004 for the Charlotte Bobcats, a **different (new) franchise** that reuses
the code.

### Ties are expected; irregular seasons

NBA division pairs play 4–6 games (6 in the 1980s, mostly 5 in 1989–94, mostly 4 since 1995), so
level series (2–2, 3–3) are common whenever the count is even — **602** across 1985–2024 (22% of
series). The NBA has no tied games. See the irregular-seasons section below for the 1998, 2011,
2018, 2019, 2020 and 2023 disruptions.

### Design notes flagged for the group
- **Naming inconsistency:** NBA divisions are named bare (`Atlantic`, `Pacific`); MLB uses
  `AL-East` / `NL-West` and NFL `AFC-East` / `NFC-Central`. Unresolved.
- Old and new NBA divisions share names (`Atlantic`, `Central`, `Pacific`) but not members, e.g.
  the 2004 Central is not the 2003 Central.

---

## NFL

### Eras

Until 2001 the NFL had 6 divisions (AFC and NFC × East, Central, West) of uneven size; from 2002
it has 8 divisions of 4.

| Seasons | Teams | Structure |
|---|---|---|
| 1985–94 | 28 | AFC-Central and NFC-West have 4 teams; the other four have 5 |
| 1995 | 30 | Carolina and Jacksonville join; both 5-team divisions complete |
| 1996–98 | 30 | Browns inactive; Ravens (BAL) begin in the AFC-Central |
| 1999–2001 | 31 | Browns return; AFC-Central has 6 teams |
| 2002–24 | 32 | Texans join; realignment into 8 divisions of 4 (Seattle moves to the NFC-West, Arizona to the NFC-West) |

### Codes and verification

The log already uses present-day franchise codes in every season (Oilers → `TEN`, Colts → `IND`,
Cardinals → `ARI`, Rams → `LAR`, Chargers → `LAC`, Raiders → `LV`), so there is no code resolution
for the NFL. Because division rivals play exactly twice a season, the script asserts that every
pair in every declared division played exactly 2 games, which confirms the division placements
in every season except 1987 (see below).

### Ties and irregular seasons

NFL pairs play only 2 games, so 1–1 splits are common — **853** tied series (41% of series). NFL
games can also end tied after overtime: **21** in 1985–2024, 10 of them between division rivals.
A tied game counts for neither team. **1987** (players' strike) has only 12 games per team in the
log, so many division pairs played once.

---

## Irregular seasons and how they are handled

Seasons whose game counts differ from the standard schedule:

| League | Season | What the log shows | Tournaments affected |
|---|---|---|---|
| NFL | 1987 | Strike: 12 games per team; many division pairs played once | 6 of 286 |
| NBA | 1998 | Lockout: 50 games per team | 4 of 202 |
| NBA | 2011 | Lockout: 66 games per team | 6 |
| NBA | 2019 | COVID suspension: 64–75 games per team, uneven | 6 |
| NBA | 2020 | 72 games per team | 6 |
| NBA | 2018 | 1,228 games instead of 1,230; BOS–PHI has 3 games (cause not established) | 1 series |
| NBA | 2023 | Four division pairs have 5 games (cause not established); the log also has one extra game in 2023 and in 2024 | 4 series |
| NBA | 2012 | BOS and IND have 81 games; not division rivals | none |
| NFL | 2022 | BUF and CIN have 16 games (cancelled game); not division rivals | none |
| MLB | 1994, 1995, 2020 | Strike-shortened (1994–95) and COVID (2020) seasons | 12 of 222 (1994, 2020) |

For the NBA the four short seasons (1998, 2011, 2019, 2020) cover 22 of 202 tournaments (11%).

**Handling:** all of these seasons are **included**; no season or game is removed. Tied games count
for neither team. Tied series follow the upset definition below. NFL 1987 is included with the
1986 alignment (the strike did not change it), and its division check is relaxed to "played at
least once". The games-per-pair variation files flag the irregular seasons. Whether to exclude or
flag them in cross-season comparisons is **open** (see the caveats below).

---

## The settled definition of "upset"

Decided in the 2026-09-16 and 2026-09-23 coding-subgroup meetings. Given two teams with total
season scores s1, s2 (score = number of division-series wins, a tied series counting as 1/2):

- **s1 == s2 → skip.** Don't classify the pair as an upset or a non-upset; exclude it from both
  numerator and denominator. (We can't say which team ranked higher, so "did the lower-ranked
  team win?" is undefined.)
- **s1 ≠ s2** (say s1 > s2; the other case is symmetric):
  - higher-scoring team won the head-to-head series → **not an upset**.
  - lower-scoring team won the head-to-head series → **1 upset**.
  - head-to-head series tied → **1/2 upset**.

This deliberately differs from the graph-theory literature (Fulkerson 1965; Brualdi & Li 1983),
which breaks score ties by arbitrary team-labeling (e.g. alphabetical) order. We rejected that
because it makes the upset count depend on an arbitrary labeling and corresponds to no real-world
meaning for actual sports results. Consequence: the classic "upsets = above-diagonal entries in a
score-sorted adjacency matrix" identity from the literature no longer holds under our definition.

## Two models per division/season

- **Model 1 — Binary:** only the series winner matters (one directed edge per pair). This is the
  standard tournament graph, directly comparable to the theory subgroup's work.
- **Model 2 — Win/Loss:** keep actual game-win tallies; a team's score is its total in-division
  game wins. Captures margin of dominance, not just who won each series.

Both produce standings, scoring sequences, and upset counts — possibly different, since a team
can win many series narrowly (strong in Model 1) or few series by large margins (strong in
Model 2).

## Open caveats for downstream analysis

- **Shortened seasons** (see the table above): keep, flag, or drop them when comparing across
  seasons? Their small samples make upset counts noisier.
- **Tied series are common** in all three leagues (MLB 6%, NBA 22%, NFL 41% of series), so the
  1/2-upset rule is load-bearing, not a rare edge case.
- **Variable division sizes** (4–8 teams) mean upset *counts* aren't comparable across eras
  directly — use upset *frequency* (upsets / pairs) for cross-era comparison.
- **Division placements not checked against the schedule** (MLB all seasons, NBA East 1985–87 and
  West 1995–2003 and 2004–24, plus the 1988–90 NBA expansion placements) need a spot-check
  against a reference.
- **Division naming** is inconsistent across leagues (see the NBA section).
