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

# (lat, lon) for map rendering
COORDS = {
    "ATL": (33.6407, -84.4277),
    "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737),
    "ORD": (41.9742, -87.9073),
    "LAX": (33.9416, -118.4085),
    "CLT": (35.2144, -80.9431),
    "MIA": (25.7959, -80.2870),
    "JFK": (40.6413, -73.7781),
    "LAS": (36.0840, -115.1537),
    "PHX": (33.4342, -112.0116),
    "SEA": (47.4502, -122.3088),
    "EWR": (40.6895, -74.1745),
    "SFO": (37.6213, -122.3790),
    "IAH": (29.9902, -95.3368),
    "MCO": (28.4312, -81.3081),
    "BOS": (42.3656, -71.0096),
    "MSP": (44.8848, -93.2223),
    "DTW": (42.2124, -83.3534),
    "PHL": (39.8744, -75.2424),
    "LGA": (40.7769, -73.8740),
    "SLC": (40.7899, -111.9791),
    "SAN": (32.7338, -117.1933),
    "BWI": (39.1774, -76.6684),
    "TPA": (27.9755, -82.5332),
    "DCA": (38.8521, -77.0377),
    "AUS": (30.1975, -97.6664),
    "PDX": (45.5898, -122.5951),
    "IAD": (38.9531, -77.4565),
    "HNL": (21.3245, -157.9251),
    "MDW": (41.7868, -87.7522),
}

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
