import datetime
from pathlib import Path

AIRPORTS = [
    ("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta"),
    ("DFW", "Dallas/Fort Worth International", "Dallas"),
    ("DEN", "Denver International", "Denver"),
    ("ORD", "O'Hare International", "Chicago"),
    ("LAX", "Los Angeles International", "Los Angeles"),
    ("CLT", "Charlotte Douglas International", "Charlotte"),
    ("MIA", "Miami International", "Miami"),
    ("JFK", "John F. Kennedy International", "New York"),
    ("LAS", "Harry Reid International", "Las Vegas"),
    ("PHX", "Phoenix Sky Harbor International", "Phoenix"),
    ("SEA", "Seattle-Tacoma International", "Seattle"),
    ("EWR", "Newark Liberty International", "Newark"),
    ("SFO", "San Francisco International", "San Francisco"),
    ("IAH", "George Bush Intercontinental", "Houston"),
    ("MCO", "Orlando International", "Orlando"),
    ("BOS", "Logan International", "Boston"),
    ("MSP", "Minneapolis-Saint Paul International", "Minneapolis"),
    ("DTW", "Detroit Metropolitan Wayne County", "Detroit"),
    ("PHL", "Philadelphia International", "Philadelphia"),
    ("LGA", "LaGuardia", "New York"),
    ("SLC", "Salt Lake City International", "Salt Lake City"),
    ("SAN", "San Diego International", "San Diego"),
    ("BWI", "Baltimore/Washington International", "Baltimore"),
    ("TPA", "Tampa International", "Tampa"),
    ("DCA", "Ronald Reagan Washington National", "Washington"),
    ("AUS", "Austin-Bergstrom International", "Austin"),
    ("PDX", "Portland International", "Portland"),
    ("IAD", "Washington Dulles International", "Washington"),
    ("HNL", "Daniel K. Inouye International", "Honolulu"),
    ("MDW", "Chicago Midway International", "Chicago"),
]
AIRPORT_NAMES = {code: name for code, name, _ in AIRPORTS}
AIRPORT_CITIES = {code: city for code, _, city in AIRPORTS}

CURRENT_MONTH = (2026, 5)

# Regional carriers shown to travelers by the brand they actually book.
BRAND_NAMES = {
    "OO": "SkyWest (United Express)",
    "MQ": "Envoy (American Eagle)",
    "OH": "PSA (American Eagle)",
    "9E": "Endeavor (Delta Connection)",
    "YX": "Republic (American/Delta/United)",
    "G7": "GoJet (United Express)",
    "QX": "Horizon (Alaska)",
    "C5": "CommutAir (United Express)",
    "PT": "Piedmont (American Eagle)",
    "YV": "Mesa (United Express)",
}

BASE_URL = "https://birdman9119.github.io/the-arrivals-report/"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
HISTORY_DIR = DATA_DIR / "history"
SITE_JSON = DATA_DIR / "site.json"
OUTPUT_DIR = ROOT / "output"

TRACKED = set(AIRPORT_NAMES)
MIN_ROUTE_FLIGHTS = 200
MIN_CARRIER_MONTHLY = 50
TREND_MONTHS = 12


def month_label(year, month):
    return datetime.date(year, month, 1).strftime("%B %Y")


def zip_url(year, month):
    return (
        "https://transtats.bts.gov/PREZIP/"
        f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
    )
