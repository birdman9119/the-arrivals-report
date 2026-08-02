# The Arrivals Report

On-time performance for US airlines, per airport. One table per airport, no filler.

Static site generated from U.S. DOT BTS On-Time Performance data. See `output/` for the rendered site.

## Pipeline

```
pipeline/fetch.py      --year Y --month M   downloads the monthly BTS zip (resume-safe)
pipeline/aggregate.py                       builds data/site.json (airport × airline stats)
pipeline/build.py                           renders output/ static site
```

Monthly update:

```
python3 pipeline/fetch.py --year 2026 --month 6
python3 pipeline/aggregate.py
python3 pipeline/build.py
```

`pipeline/config.py` holds the airport list, current month, and affiliate/domain constants.

## Data

Source: [BTS On-Time Performance](https://www.transtats.bts.gov/), monthly release, reporting carriers, US domestic arrivals.

- On-time: arrived within 15 minutes of schedule (DOT definition); cancelled/diverted excluded.
- Avg. delay: mean arrival delay, early arrivals counted as zero (DOT "ArrDelayMinutes").
- Avg. taxi-in: wheels-on to gate, minutes.

## Design constraints

- No runtime server. Build once, host as static files anywhere.
- One accent color, tabular numerals, no images, no JS frameworks (one 10-line filter on the index).
- Affiliate slots are the two links under each airport table (`site/templates/airport.html`); swap the `href="#"` placeholders.

## Roadmap

- Airline baggage-loss rate column (DOT ATCR, national per-airline) — needs PDF parsing, not yet automated.
- More airports (config-only change).
- Historical month archive pages.
