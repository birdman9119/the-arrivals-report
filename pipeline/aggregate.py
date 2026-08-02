import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import AIRPORTS, MIN_FLIGHTS, RAW_DIR, SITE_JSON, month_label

USECOLS = [
    "Reporting_Airline",
    "FlightDate",
    "Dest",
    "ArrDel15",
    "ArrDelay",
    "ArrDelayMinutes",
    "TaxiIn",
    "Cancelled",
    "Diverted",
]

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
    csv_name = None
    with zipfile.ZipFile(zpath) as z:
        csv_name = z.namelist()[0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f, usecols=USECOLS, low_memory=False)
    return df


def aggregate(df):
    rows = []
    for code, name, city in AIRPORTS:
        apt = df[df["Dest"] == code].copy()
        if apt.empty:
            continue
        apt["ArrDelay"] = pd.to_numeric(apt["ArrDelay"], errors="coerce")
        apt["ArrDelayMinutes"] = pd.to_numeric(apt["ArrDelayMinutes"], errors="coerce")
        apt["TaxiIn"] = pd.to_numeric(apt["TaxiIn"], errors="coerce")
        apt["ArrDel15"] = pd.to_numeric(apt["ArrDel15"], errors="coerce")
        apt["Cancelled"] = pd.to_numeric(apt["Cancelled"], errors="coerce").fillna(0)
        apt["Diverted"] = pd.to_numeric(apt["Diverted"], errors="coerce").fillna(0)

        scheduled = apt[apt["Cancelled"] == 0]
        g = scheduled.groupby("Reporting_Airline")
        airlines = []
        for carrier, sub in g:
            if len(sub) < MIN_FLIGHTS:
                continue
            ontime = int((sub["ArrDel15"] == 0).sum())
            airlines.append(
                {
                    "code": carrier,
                    "name": AIRLINE_NAMES.get(carrier, carrier),
                    "flights": int(len(sub)),
                    "on_time_pct": round(ontime / len(sub) * 100, 1),
                    "avg_delay_min": round(float(sub["ArrDelay"].mean()), 1),
                    "avg_taxi_in_min": round(float(sub["TaxiIn"].mean()), 1),
                }
            )
        airlines.sort(key=lambda a: -a["on_time_pct"])

        flown = int(len(scheduled))
        rows.append(
            {
                "code": code,
                "name": name,
                "city": city,
                "flights": flown,
                "on_time_pct": round(int((scheduled["ArrDel15"] == 0).sum()) / flown * 100, 1) if flown else 0,
                "cancelled": int(apt["Cancelled"].sum()),
                "airlines": airlines,
            }
        )
    rows.sort(key=lambda a: -a["on_time_pct"])
    return rows


def latest_raw():
    zips = sorted(RAW_DIR.glob("*.zip"), reverse=True)
    if not zips:
        sys.exit(f"no data in {RAW_DIR} — run fetch.py first")
    name = zips[0].stem
    year, month = map(int, name.split("_"))
    return zips[0], year, month


def main():
    zpath, year, month = latest_raw()
    df = load_month(year, month)
    airports = aggregate(df)
    data = {
        "month": month_label(year, month),
        "year": year,
        "month_num": month,
        "airports": airports,
    }
    SITE_JSON.write_text(json.dumps(data, indent=2))
    print(f"wrote {SITE_JSON}: {len(airports)} airports")
    for a in airports:
        print(f"  {a['code']} {a['on_time_pct']}% on-time, {len(a['airlines'])} airlines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
