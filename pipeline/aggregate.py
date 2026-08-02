import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    AIRPORT_CITIES,
    AIRPORT_NAMES,
    BRAND_NAMES,
    HISTORY_DIR,
    MIN_CARRIER_MONTHLY,
    MIN_ROUTE_FLIGHTS,
    RAW_DIR,
    SITE_JSON,
    TRACKED,
    TREND_MONTHS,
    month_label,
)

USECOLS = [
    "Reporting_Airline",
    "Dest",
    "Origin",
    "CRSDepTime",
    "ArrDel15",
    "ArrDelayMinutes",
    "Cancelled",
    "Diverted",
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

AIRLINE_NAMES = {
    "AA": "American",
    "AS": "Alaska",
    "B6": "JetBlue",
    "DL": "Delta",
    "F9": "Frontier",
    "G4": "Allegiant",
    "HA": "Hawaiian",
    "NK": "Spirit",
    "UA": "United",
    "WN": "Southwest",
    "OO": "SkyWest",
    "YX": "Republic",
    "MQ": "Envoy Air",
    "OH": "PSA Airlines",
    "9E": "Endeavor Air",
    "G7": "GoJet",
    "QX": "Horizon Air",
    "C5": "CommutAir",
}


def load_month(year, month):
    zpath = RAW_DIR / f"{year}_{month}.zip"
    with zipfile.ZipFile(zpath) as z:
        csv = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(csv) as f:
            return pd.read_csv(f, usecols=USECOLS, low_memory=False)


def time_bucket(hhmm):
    try:
        t = int(float(hhmm))
    except (TypeError, ValueError):
        return None
    if t < 1200:
        return "morning"
    if t >= 1700:
        return "evening"
    return None


def route_month(df):
    apt = df[df["Origin"].isin(TRACKED) & df["Dest"].isin(TRACKED)].copy()
    apt["route"] = apt["Origin"] + "_" + apt["Dest"]
    apt["bucket"] = apt["CRSDepTime"].map(time_bucket)
    apt["ArrDel15"] = pd.to_numeric(apt["ArrDel15"], errors="coerce")
    apt["ArrDelayMinutes"] = pd.to_numeric(apt["ArrDelayMinutes"], errors="coerce")
    apt["Cancelled"] = pd.to_numeric(apt["Cancelled"], errors="coerce").fillna(0)

    flown = apt[apt["Cancelled"] == 0]
    out = {}
    for route, sub in flown.groupby("route"):
        total = len(sub)
        if total < MIN_ROUTE_FLIGHTS:
            continue
        carriers = []
        for carrier, csub in sub.groupby("Reporting_Airline"):
            if len(csub) < MIN_CARRIER_MONTHLY:
                continue
            carriers.append(
                {
                    "code": carrier,
                    "name": AIRLINE_NAMES.get(carrier, carrier),
                    "flights": int(len(csub)),
                    "on_time_pct": round(float((csub["ArrDel15"] == 0).mean() * 100), 1),
                    "avg_delay_min": round(float(csub["ArrDelayMinutes"].mean()), 1),
                }
            )
        if not carriers:
            continue
        tod = {}
        for bucket in ("morning", "evening"):
            bsub = sub[sub["bucket"] == bucket]
            if len(bsub) >= 30:
                tod[bucket] = round(float((bsub["ArrDel15"] == 0).mean() * 100), 1)
        out[route] = {
            "flights": int(total),
            "on_time_pct": round(float((sub["ArrDel15"] == 0).mean() * 100), 1),
            "avg_delay_min": round(float(sub["ArrDelayMinutes"].mean()), 1),
            "cancelled": int(apt[apt["route"] == route]["Cancelled"].sum()),
            "tod": tod,
            "carriers": carriers,
        }
    return out


def history_path(year, month):
    return HISTORY_DIR / f"{year}_{month}.json"


def latest_raw():
    zips = sorted(RAW_DIR.glob("*.zip"), reverse=True)
    if not zips:
        sys.exit(f"no data in {RAW_DIR} — run fetch.py first")
    name = zips[0].stem
    year, month = map(int, name.split("_"))
    return zips[0], year, month


def aggregate_route(route, months, latest_label=None):
    by_carrier = {}
    tot_flights = 0
    ontime_w = 0
    delay_w = 0
    cancelled = 0
    for key, m in months:
        tot_flights += m["flights"]
        ontime_w += m["flights"] * m["on_time_pct"]
        delay_w += m["flights"] * m["avg_delay_min"]
        cancelled += m.get("cancelled", 0)

    latest_key = months[-1][0]
    latest_year = int(latest_key[:4])
    ytd_months = [(k, m) for k, m in months if int(k[:4]) == latest_year]
    yf_tot = sum(m["flights"] for _, m in ytd_months)
    yc_tot = sum(m.get("cancelled", 0) for _, m in ytd_months)
    ytd_pct = round(sum(m["flights"] * m["on_time_pct"] for _, m in ytd_months) / yf_tot, 1) if yf_tot else 0.0
    ytd_delay = round(sum(m["flights"] * m["avg_delay_min"] for _, m in ytd_months) / yf_tot, 1) if yf_tot else 0.0
    ytd_cancel_rate = round(yc_tot * 100 / (yf_tot + yc_tot), 1) if (yf_tot + yc_tot) else 0.0
    if len(ytd_months) == 1:
        ytd_label = latest_label or latest_key
    else:
        ytd_label = f"{MONTH_NAMES[int(ytd_months[0][0][5:7]) - 1]}–{latest_label or latest_key}"

    carrier_codes = sorted({c["code"] for _, m in months for c in m["carriers"]})
    for code in carrier_codes:
        first = next(c for _, m in months for c in m["carriers"] if c["code"] == code)
        row = {
            "code": code,
            "name": BRAND_NAMES.get(code, first["name"]),
            "flights": 0,
            "window_flights": 0,
            "on_time_pct": 0.0,
            "avg_delay_min": 0.0,
            "trend": [],
        }
        w = []
        d = []
        yf = 0
        yw = 0
        yd = 0
        for key, m in months:
            cm = next((x for x in m["carriers"] if x["code"] == code), None)
            if cm:
                row["window_flights"] += cm["flights"]
                row["trend"].append(cm["on_time_pct"])
                w.append(cm["flights"])
                d.append(cm["flights"] * cm["avg_delay_min"])
                if int(key[:4]) == latest_year:
                    yf += cm["flights"]
                    yw += cm["flights"] * cm["on_time_pct"]
                    yd += cm["flights"] * cm["avg_delay_min"]
            else:
                row["trend"].append(None)
                w.append(0)
                d.append(0)
        if row["window_flights"] >= MIN_CARRIER_MONTHLY * len(months):
            row["flights"] = yf
            row["on_time_pct"] = round(yw / yf, 1) if yf else None
            row["avg_delay_min"] = round(yd / yf, 1) if yf else None
            by_carrier[code] = row
    tod_w = {"morning": 0, "evening": 0}
    for _, m in ytd_months:
        for k in tod_w:
            if k in m["tod"]:
                tod_w[k] += m["flights"] * m["tod"][k]
    total = yf_tot + yc_tot
    return {
        "flights": yf_tot,
        "on_time_pct": ytd_pct,
        "avg_delay_min": ytd_delay,
        "cancelled": yc_tot,
        "cancel_rate": ytd_cancel_rate,
        "ytd_label": ytd_label,
        "ytd_months": len(ytd_months),
        "window_pct": round(ontime_w / tot_flights, 1) if tot_flights else 0.0,
        "window_flights": tot_flights,
        "tod": {k: round(v / yf_tot, 1) for k, v in tod_w.items()},
        "carriers": sorted(
            by_carrier.values(),
            key=lambda c: -(c["on_time_pct"] if c["on_time_pct"] is not None else -1),
        ),
    }


def main():
    months = []
    for hp in sorted(HISTORY_DIR.glob("*.json")):
        months.append(json.loads(hp.read_text()))
    have = {m["month"] for m in months}

    for zpath in sorted(RAW_DIR.glob("*.zip")):
        year, month = map(int, zpath.stem.split("_"))
        key = f"{year}-{month:02d}"
        if key in have:
            continue
        print(f"aggregating {zpath.name}...")
        rm = route_month(load_month(year, month))
        entry = {"month": key, "label": month_label(year, month), "routes": rm}
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        history_path(year, month).write_text(json.dumps(entry))
        print(f"wrote history {history_path(year, month).name} ({len(rm)} routes)")
        months.append(entry)

    months.sort(key=lambda m: m["month"])
    months = months[-TREND_MONTHS:]

    latest = months[-1]
    routes = {}
    for route in latest["routes"]:
        present = [(m["month"], m["routes"][route]) for m in months if route in m["routes"]]
        if not present:
            continue
        codes = route.split("_")
        agg = aggregate_route(route, present, latest["label"])
        if not agg["carriers"]:
            continue
        routes[route] = agg
        routes[route]["orig"] = codes[0]
        routes[route]["dest"] = codes[1]
        routes[route]["label"] = f"{AIRPORT_CITIES[codes[0]]} to {AIRPORT_CITIES[codes[1]]}"

    site = {
        "latest_month": months[-1]["label"],
        "latest_month_key": months[-1]["month"],
        "month_count": len(months),
        "month_keys": [m["month"] for m in months],
        "routes": routes,
        "airports": {c: {"name": n, "city": AIRPORT_CITIES[c]} for c, n in AIRPORT_NAMES.items() if c in TRACKED},
    }
    SITE_JSON.write_text(json.dumps(site, indent=1))
    print(f"wrote {SITE_JSON}: {len(routes)} routes over {len(months)} months")
    return 0


if __name__ == "__main__":
    sys.exit(main())
