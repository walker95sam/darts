# PDC Tour-Card Form Dashboard

Live form tracking for the 127 PDC tour-card holders, scraped daily from
[dartsorakel.com](https://dartsorakel.com). Built for darts betting
analysis — surfaces last-10-match averages, trend, strength of schedule,
performance vs opponent, and a head-to-head comparison view.

**Live page:** https://walker95sam.github.io/darts/

## What it shows

- Sortable table of all current PDC tour-card holders
- For each player: last 10 matches' 3-dart average, trend (last 5 vs prior 5),
  win rate, consistency (std dev), mean opponent average, and the
  performance-vs-opponent edge (your avg minus theirs)
- Season-wide checkout %, total 180s, first-9 average
- Click any row → match-by-match breakdown including opponent and their average
- "Compare players" tab — pick any two players, choose a sample window
  (5 / 10 / 20 / 30 / 50), filter by event type, see side-by-side stats with
  delta colouring, an overlaid line chart, common-opponents analysis, and any
  direct head-to-head meetings

Sample excludes World Grand Prix (different format — double-in/double-out
distorts averages). Includes Premier League, World Championship, Matchplay,
Grand Slam, European Championship, European Tour, World Series, Players
Championship Finals, Pro Tour, qualifiers, and other PDC-sanctioned events.

## How it stays fresh

A GitHub Action runs daily at 07:00 UTC (workflow file at
`.github/workflows/scrape.yml`). It:

1. Re-scrapes everything from the dartsorakel API (~5–7 minutes).
2. Rebuilds `docs/index.html` with the new data baked in.
3. Commits the refreshed `docs/` back to `main`.
4. GitHub Pages then serves it at https://walker95sam.github.io/darts/.

You can also trigger a manual refresh from the **Actions** tab → "Scrape
darts data and rebuild dashboard" → "Run workflow".

## One-time setup (you have to do this once)

After pushing this code:

1. **Enable GitHub Pages**
   - Repo Settings → Pages
   - Source: **Deploy from a branch**
   - Branch: **main** / **/docs**
   - Save. Your URL will be https://walker95sam.github.io/darts/

2. **Allow Actions to push back to main**
   - Repo Settings → Actions → General
   - Workflow permissions: **Read and write permissions**
   - Save

3. **(Optional) Run it once manually to verify**
   - Actions tab → "Scrape darts data and rebuild dashboard" → Run workflow
   - First run takes 5–7 minutes
   - When it succeeds, the dashboard will be live at the Pages URL above

## Running locally

No external dependencies — Python 3.10+ stdlib only.

```bash
python scripts/scrape_and_build.py
# Then open docs/index.html in any browser
```

## File layout

```
darts/
├── README.md                            # this file
├── .github/workflows/scrape.yml          # daily cron + manual trigger
├── scripts/
│   ├── scrape_and_build.py               # full pipeline (entrypoint)
│   └── build_html.py                     # HTML template + render()
└── docs/                                 # served by GitHub Pages
    ├── index.html                        # generated; do not edit by hand
    └── data/
        ├── tourcard_summary.csv          # 127 rows, model-friendly features
        └── tourcard_matches_long.csv     # all matches in long format
```

## Data sources

All public, no auth required:

- `GET /api/stats/player?tourCardYear=2026` — current tour-card holders
- `GET /api/player/matches/{key}?organisation=All&organStat=All` — per-player match history
- `GET /api/stats/player?tourCardYear=2026&rankKey={1053|26|1029}` — season-wide checkout%, 180s, first-9 avg

## Notes for the betting model

Things worth knowing when interpreting the numbers:

- **Premier League sub-matches**: each PL night produces 2–3 sub-matches
  (QF/SF/F). PL-qualified players' last-10 windows are dominated by PL
  during the season. That's accurate — it's their most recent form — but
  it means they're sometimes facing the same opponent multiple times.
- **Qualifier matches** (`category = "Q"`) make up ~23% of the sample. Mostly
  best-of-7 against lower-ranked players — averages run a touch higher and
  variance is high. If they distort your model you can filter them out via
  the long CSV.
- **Strength of schedule (`mean_opp_avg`)**: a player averaging 95 against
  opponents averaging 88 is showing very different form to one averaging 95
  against opponents averaging 96. The `mean_perf_vs_opp` column captures
  this directly.
- **Format mixing**: the sample mixes best-of-11 floor matches (Pro Tour,
  ET) with sets-format TV majors and Premier League nightly format. Averages
  vary systematically by format — Premier League averages run high (no
  doubles-in pressure on every leg), Worlds run lower (long sets, fatigue,
  TV nerves).
