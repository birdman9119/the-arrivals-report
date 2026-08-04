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
    ("FLL", "Fort Lauderdale-Hollywood International", "Fort Lauderdale"),
    ("BNA", "Nashville International", "Nashville"),
    ("RDU", "Raleigh-Durham International", "Raleigh"),
    ("SJC", "Norman Y. Mineta San Jose International", "San Jose"),
    ("DAL", "Dallas Love Field", "Dallas"),
    ("STL", "St. Louis Lambert International", "St. Louis"),
    ("MSY", "Louis Armstrong New Orleans International", "New Orleans"),
    ("SMF", "Sacramento International", "Sacramento"),
    ("OAK", "Oakland International", "Oakland"),
    ("SAT", "San Antonio International", "San Antonio"),
    ("PIT", "Pittsburgh International", "Pittsburgh"),
    ("CMH", "John Glenn Columbus International", "Columbus"),
    ("IND", "Indianapolis International", "Indianapolis"),
    ("CLE", "Cleveland Hopkins International", "Cleveland"),
    ("MCI", "Kansas City International", "Kansas City"),
    ("RSW", "Southwest Florida International", "Fort Myers"),
    ("MKE", "Milwaukee Mitchell International", "Milwaukee"),
    ("OGG", "Kahului Airport", "Kahului"),
    ("PBI", "Palm Beach International", "West Palm Beach"),
    ("ABQ", "Albuquerque International Sunport", "Albuquerque"),
    ("ONT", "Ontario International", "Ontario"),
    ("JAX", "Jacksonville International", "Jacksonville"),
    ("BDL", "Bradley International", "Hartford"),
    ("CHS", "Charleston International", "Charleston"),
    ("TUS", "Tucson International", "Tucson"),
    ("GEG", "Spokane International", "Spokane"),
    ("BOI", "Boise Airport", "Boise"),
    ("OKC", "Will Rogers World Airport", "Oklahoma City"),
    ("TUL", "Tulsa International", "Tulsa"),
    ("MEM", "Memphis International", "Memphis"),
    ("RNO", "Reno-Tahoe International", "Reno"),
    ("BUR", "Hollywood Burbank Airport", "Burbank"),
    ("SNA", "John Wayne Airport", "Orange County"),
    ("HOU", "William P. Hobby Airport", "Houston"),
    ("ANC", "Ted Stevens Anchorage International", "Anchorage"),
    ("KOA", "Kona International Airport", "Kona"),
    ("LIH", "Lihue Airport", "Lihue"),
    ("ELP", "El Paso International", "El Paso"),
    ("BUF", "Buffalo Niagara International", "Buffalo"),
    ("PVD", "Rhode Island T.F. Green International", "Providence"),
    ("SDF", "Louisville Muhammad Ali International", "Louisville"),
    ("GRR", "Gerald R. Ford International", "Grand Rapids"),
    ("ORF", "Norfolk International", "Norfolk"),
    ("SRQ", "Sarasota Bradenton International", "Sarasota"),
    ("BZN", "Bozeman Yellowstone International", "Bozeman"),
    ("BHM", "Birmingham-Shuttlesworth International", "Birmingham"),
    ("TYS", "McGhee Tyson Airport", "Knoxville"),
    ("GSP", "Greenville-Spartanburg International", "Greenville"),
    ("SAV", "Savannah/Hilton Head International", "Savannah"),
    ("PSP", "Palm Springs International", "Palm Springs"),
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
    "FLL": (26.0742, -80.1506),
    "BNA": (36.1263, -86.6774),
    "RDU": (35.8776, -78.7875),
    "SJC": (37.3626, -121.9290),
    "DAL": (32.8471, -96.8518),
    "STL": (38.7487, -90.3700),
    "MSY": (29.9934, -90.2580),
    "SMF": (38.6954, -121.5908),
    "OAK": (37.7213, -122.2207),
    "SAT": (29.5337, -98.4698),
    "PIT": (40.4915, -80.2329),
    "CMH": (39.9980, -82.8919),
    "IND": (39.7173, -86.2944),
    "CLE": (41.4117, -81.8498),
    "MCI": (39.2976, -94.7139),
    "RSW": (26.5362, -81.7552),
    "MKE": (42.9472, -87.8966),
    "OGG": (20.8987, -156.4305),
    "PBI": (26.6832, -80.0956),
    "ABQ": (35.0402, -106.6092),
    "ONT": (34.0560, -117.6012),
    "JAX": (30.4941, -81.6879),
    "BDL": (41.9389, -72.6832),
    "CHS": (32.8986, -80.0405),
    "TUS": (32.1161, -110.9410),
    "GEG": (47.6199, -117.5338),
    "BOI": (43.5644, -116.2228),
    "OKC": (35.3931, -97.6007),
    "TUL": (36.1984, -95.8881),
    "MEM": (35.0424, -89.9767),
    "RNO": (39.4991, -119.7681),
    "BUR": (34.2007, -118.3590),
    "SNA": (33.6757, -117.8682),
    "HOU": (29.6454, -95.2789),
    "ANC": (61.1743, -149.9963),
    "KOA": (19.7388, -156.0456),
    "LIH": (21.9760, -159.3389),
    "ELP": (31.8072, -106.3776),
    "BUF": (42.9405, -78.7322),
    "PVD": (41.7240, -71.4282),
    "SDF": (38.1744, -85.7360),
    "GRR": (42.8808, -85.5228),
    "ORF": (36.8946, -76.2012),
    "SRQ": (27.3954, -82.5544),
    "BZN": (45.7777, -111.1517),
    "BHM": (33.5629, -86.7535),
    "TYS": (35.8111, -83.9940),
    "GSP": (34.8957, -82.2189),
    "SAV": (32.1276, -81.2021),
    "PSP": (33.8292, -116.5066),
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
