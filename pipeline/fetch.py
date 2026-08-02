import argparse
import datetime
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAW_DIR, zip_url

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
CHUNK = 4 * 1024 * 1024


def month_ago(months):
    d = datetime.date.today().replace(day=1)
    for _ in range(months):
        d = d.replace(day=1) - datetime.timedelta(days=1)
    return d.year, d.month


def fetch(url, dest, timeout=120):
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = dest.stat().st_size if dest.exists() else 0
    for attempt in range(20):
        headers = dict(UA)
        if size:
            headers["Range"] = f"bytes={size}-"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                total = int(r.headers.get("Content-Length") or 0) + size
                with open(dest, "ab") as f:
                    while True:
                        block = r.read(CHUNK)
                        if not block:
                            break
                        f.write(block)
                        size += len(block)
        except Exception as e:
            print(f"attempt {attempt + 1}: {e}")
            continue
        if total and size < total:
            print(f"truncated {size}/{total}, resuming")
            continue
        if total == 0 and size == 0:
            print("empty response, retrying")
            continue
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int)
    ap.add_argument("--month", type=int)
    ap.add_argument("--auto", action="store_true", help="download the most recent available month")
    args = ap.parse_args()

    if args.auto:
        for lag in range(1, 7):
            year, month = month_ago(lag)
            dest = RAW_DIR / f"{year}_{month}.zip"
            if dest.exists():
                print(f"already have {dest}")
                return 0
            print(f"trying {year}-{month}...")
            if fetch(zip_url(year, month), dest):
                print(f"saved {dest} ({dest.stat().st_size} bytes)")
                return 0
        print("no data available for last 6 months")
        return 1

    if not args.year or not args.month:
        ap.error("pass --year/--month or --auto")
    dest = RAW_DIR / f"{args.year}_{args.month}.zip"
    ok = fetch(zip_url(args.year, args.month), dest)
    print(f"{'saved' if ok else 'FAILED'} {dest} ({dest.stat().st_size if dest.exists() else 0} bytes)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
