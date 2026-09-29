# Notes — MLB division data (1985–2024)

Findings, decisions, and data caveats from building the MLB division-level dataset. This is the
narrative companion to the CSVs in `Data/` and the evidence files in `Data/anomalies/`. Written
to be read before using the data for upset analysis.

---

## What the dataset covers

MLB seasons **1985–2024** (40 seasons), reduced to **division-level tournaments**: within each
division each season, every pair of teams plays a fixed set of games, so a division is a small,
clean testbed for the upset question before tackling full leagues.

Three processed files (see `Data/README.md` for columns):
- `mlb_division_membership.csv` — who was in which division each season.
- `mlb_division_series_results.csv` — head-to-head record for every intra-division pair.
- `mlb_ties_1985_2024.csv` — individual games that ended tied.

Plus evidence files in `Data/anomalies/` (see `Data/anomalies/README.md`).

## Division membership is external knowledge

The game log (`game_data_us_leagues.csv`) has **no league or division column** — only the two
teams and the result. Which teams belonged to which division is historical domain knowledge, not
derivable from the data. `build_division_membership.py` encodes it directly, then cross-checks
every team code against the codes that actually appear in the game log for that season. So the
membership assignments are historical facts we supplied; the team codes and season boundaries are
verified against the real data.

## MLB realigned 4 times since 1985 — there are 5 eras

Division count and size are **not** constant across the dataset. Anyone comparing seasons needs
to know this:

| Era | Seasons | Structure | Teams |
|---|---|---|---|
| 1 | 1985–1992 | 2 divisions/league (East, West), no Central | 26 |
| 2 | 1993 | 2 divisions/league, post-expansion | 28 |
| 3 | 1994–1997 | 3 divisions/league (East/Central/West) introduced | 28 |
| 4 | 1998–2012 | 3 divisions/league, 30 teams (AL 14 / NL 16) | 30 |
| 5 | 2013–2024 | 3 divisions/league, current alignment (AL 15 / NL 15) | 30 |

Division sizes range from **4 to 7 teams** depending on era, so the number of pairs per division
(and hence the size of each tournament) is not fixed either. The membership file and all
downstream code handle this via `math.comb` rather than assuming a fixed division size.

## Franchise code changes (same team, different abbreviation)

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

## Two teams actually changed divisions

Distinct from code changes — these franchises moved divisions:

| Team | From | To | Season |
|---|---|---|---|
| Milwaukee Brewers | AL Central | NL Central | 1998 |
| Houston Astros | NL Central | AL West | 2013 |

No other team changed divisions in 1985–2024; every other change is an era-wide realignment.

---

## The three data anomalies (and why each matters)

### 1. Games per pair is highly variable (5 to 20)

The number of games two division rivals play each other is **not** a constant 13. It ranges from
**5** (1994 strike) to **20**, and is frequently even. Evidence:
`anomalies/games_played_variation_1985_2024.csv`.

Only **2023–2024** have the clean "exactly 13 games/pair" property (odd → always a decisive
series winner). Implication: cross-season upset-frequency comparisons rest on very different
sample sizes per series, and even game counts make ties possible.

Special seasons: **1994** (strike, as few as 5 games/pair), **2020** (COVID, exactly 10).

### 2. Tied division series — 154 of them

154 pairs finished a season with **equal head-to-head wins** (no decisive series winner).
Evidence: `anomalies/tied_division_series_1985_2024.csv`. Common because so many seasons had an
even number of games per pair. This is the single biggest reason the upset definition needs an
explicit tie rule (below).

### 3. Individual tied games — 21 total, 13 in-division

21 MLB games in 1985–2024 ended in a tie (`result == 0`) — suspended/rain-shortened games never
completed. 13 were between division rivals. Evidence: `mlb_ties_1985_2024.csv` (all 21) and
`anomalies/individual_tie_games_in_division_1985_2024.csv` (the 13). These games count toward
`games_played` but toward neither team's wins, which is why `mlb_division_series_results.csv` has
a separate `ties` column and why win totals don't always sum to games played.

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

- **2020** (COVID, 10 games/pair) and **1994** (strike, as few as 5): keep or drop? Membership is
  unaffected, but their tiny sample sizes make their upset numbers noisier — flag or exclude when
  comparing across seasons.
- **Even game counts** (most pre-2023 seasons) mean tied series are common, so the 1/2-upset rule
  is load-bearing, not a rare edge case.
- **Variable division sizes** (4–7 teams) mean upset *counts* aren't comparable across eras
  directly — use upset *frequency* (upsets / pairs) for cross-era comparison.
