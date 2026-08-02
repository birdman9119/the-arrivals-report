# The Arrivals Report

Which airline is most reliable on your route? Per-route, per-airline on-time performance with 12-month trends, from U.S. DOT data.

Static site in `output/` (built by CI), deployed to GitHub Pages.

## Pipeline

```
pipeline/fetch.py      --year Y --month M   download one month (resume-safe)
pipeline/fetch.py      --backfill N         download the last N months (one-time)
pipeline/fetch.py      --since YYYY-M       download every month from YYYY-M up to the latest
pipeline/fetch.py      --auto               download the most recent available month
pipeline/aggregate.py                       append latest month to data/history/, build data/site.json
pipeline/build.py                           render output/ static site
```

`data/history/YYYY_M.json` holds per-month route stats (committed to git, ~500KB each). CI only needs to download the single newest month — history comes from the repo.

## Data

Source: [BTS On-Time Performance](https://www.transtats.bts.gov/), reporting carriers, US domestic flights between tracked airports (see `pipeline/config.py`).

- On-time: arrived within 15 minutes of schedule (DOT definition); cancelled/diverted excluded.
- Year-to-date: the headline number on each page is the running total for the calendar year (Jan through the latest month), weighted by flight volume.
- Avg. delay: mean arrival delay, early arrivals counted as zero (DOT "ArrDelayMinutes").
- Trend: monthly on-time percentage per airline across the rolling window (last 12 months).
- Morning/evening: scheduled departures before noon vs after 5pm.
- Historical month averages (pick a date in the wizard): the weighted average of that calendar month across all years on file (since 2020).

## Design constraints

- No runtime server. Build once, host as static files anywhere.
- One accent color, tabular numerals, no images, no frameworks. Sparklines are hand-rolled inline SVG.
- Affiliate slots: the two links under each route table (`site/templates/route.html`); swap the `href="#"` placeholders.
- `BASE_URL` in `pipeline/config.py` for sitemap/robots.

## Monthly update

GitHub Action `.github/workflows/deploy.yml` runs on the 15th: fetch newest month → aggregate → commit history → build → deploy. Manual: "Run workflow" in the Actions tab.

## Roadmap

- Airline baggage-loss rate column (DOT ATCR, national per-airline) — needs PDF parsing, not yet automated.
- More airports (config-only change).
- Historical month archive pages.
