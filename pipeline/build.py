import datetime
import json
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BASE_URL, COORDS, HISTORY_DIR, OUTPUT_DIR, SITE_JSON

TPLEXE = Path(__file__).resolve().parent.parent / "site" / "templates"
STATIC = Path(__file__).resolve().parent.parent / "site" / "static"
GOOD = 80
MID = 70

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def ytd_label(month_keys, latest_month):
    latest_year = int(month_keys[-1][:4])
    keys = [k for k in month_keys if k.startswith(str(latest_year))]
    if len(keys) == 1:
        return latest_month
    return f"{MONTH_NAMES[int(keys[0][5:7]) - 1]}–{latest_month}"


def cls(pct):
    if pct is None:
        return ""
    if pct >= GOOD:
        return "good"
    if pct >= MID:
        return "mid"
    return "bad"


def sparkline(values, width=150, height=34):
    pts = [(i, v) for i, v in enumerate(values) if v is not None]
    if len(pts) < 2:
        return ""
    lo = min(v for _, v in pts)
    hi = max(v for _, v in pts)
    span = max(hi - lo, 1)
    pad = 4
    x = lambda i: pad + i * (width - 2 * pad) / (len(values) - 1)
    y = lambda v: height - pad - (v - lo) * (height - 2 * pad) / span
    points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in pts)
    last_i, last_v = pts[-1]
    dot = f'<circle cx="{x(last_i):.1f}" cy="{y(last_v):.1f}" r="2.4"/>'
    label = ", ".join(str(v) for v in values if v is not None) + "%"
    return (
        f'<svg class="spark" role="img" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'aria-label="Monthly on-time percentage: {label}"><title>Monthly on-time percentage: {label}</title>'
        f'<polyline points="{points}"/>{dot}</svg>'
    )


def months_behind(latest_key):
    today = datetime.date.today()
    ly, lm = map(int, latest_key.split("-"))
    return (today.year - ly) * 12 + (today.month - lm)


def stale_note(month, latest_key):
    behind = months_behind(latest_key)
    if behind < 2:
        return None
    return (
        f"Data is from {month} — {behind} months behind. New months are added shortly "
        f"after each DOT release (usually by mid-month)."
    )


def render_og_image(label, sub, path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (17, 17, 17))
    d = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 72)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
    except OSError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    d.text((80, 120), "The Arrivals Report", fill=(255, 255, 255), font=font_small)
    d.rectangle((80, 190, 400, 194), fill=(15, 123, 61))
    d.text((80, 260), label, fill=(255, 255, 255), font=font_big)
    d.text((80, 380), sub, fill=(155, 155, 155), font=font_small)
    img.save(path, "PNG", optimize=True)
    return True


def month_of_year_stats(routes):
    stats = {}
    for hp in sorted(HISTORY_DIR.glob("*.json")):
        hist = json.loads(hp.read_text())
        month_num = int(hist["month"][-2:])
        for key, route in hist["routes"].items():
            s = stats.setdefault(key, {}).setdefault(month_num, {"pct": 0.0, "flights": 0})
            s["pct"] += route["on_time_pct"] * route["flights"]
            s["flights"] += route["flights"]
    out = {}
    for key, months in stats.items():
        out[key] = {
            m: round(s["pct"] / s["flights"], 1)
            for m, s in months.items()
            if s["flights"]
        }
    return out


def build():
    data = json.loads(SITE_JSON.read_text())
    env = Environment(loader=FileSystemLoader(str(TPLEXE)))
    env.filters["cls"] = cls
    env.filters["sparkline"] = sparkline
    env.filters["monthshort"] = lambda k: k[-5:]

    month = data["latest_month"]
    latest_key = data["latest_month_key"]
    month_count = data["month_count"]
    routes = data["routes"]
    airports = data["airports"]
    month_stats = month_of_year_stats(routes)

    env.globals["stale"] = stale_note(month, latest_key)
    total_flights = sum(r["flights"] for r in routes.values()) or 1
    national = round(sum(r["on_time_pct"] * r["flights"] for r in routes.values()) / total_flights, 1)
    env.globals["national"] = national

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    OUTPUT_DIR.mkdir(parents=True)
    shutil.copytree(STATIC, OUTPUT_DIR / "static")

    og_dir = OUTPUT_DIR / "og"
    og_dir.mkdir(exist_ok=True)
    render_og_image(
        "Which airline should you book?",
        "On-time performance by route and airline, from U.S. DOT data.",
        og_dir / "home.png",
    )

    popular = sorted(routes.values(), key=lambda r: -r["flights"])[:40]
    ytd = ytd_label(data["month_keys"], month)
    ctx = {"month": month, "month_count": month_count, "ytd_label": ytd}
    (OUTPUT_DIR / "index.html").write_text(
        env.get_template("index.html").render(
            airports=airports,
            month=month,
            popular=popular,
            route_count=len(routes),
            month_count=month_count,
            ytd_label=ytd,
            og_url=BASE_URL,
            og_image=BASE_URL + "og/home.png",
        )
    )

    airport_list = [
        {
            "code": c,
            "city": info["city"],
            "name": info["name"],
            "label": f"{c} — {info['city']} ({info['name']})",
            "lat": COORDS.get(c, (0, 0))[0],
            "lon": COORDS.get(c, (0, 0))[1],
        }
        for c, info in sorted(airports.items())
    ]
    (OUTPUT_DIR / "airports.json").write_text(json.dumps(airport_list))

    route_index = []
    for key, r in routes.items():
        page = env.get_template("route.html").render(
            r=r,
            monthly=month_stats.get(key, {}),
            og_url=BASE_URL + f"{r['orig'].lower()}-{r['dest'].lower()}.html",
            og_image=BASE_URL + f"og/{r['orig'].lower()}-{r['dest'].lower()}.png",
            **ctx,
        )
        (OUTPUT_DIR / f"{r['orig'].lower()}-{r['dest'].lower()}.html").write_text(page)
        render_og_image(
            f"{r['orig']} → {r['dest']}",
            f"{r['carriers'][0]['name']} leads at {r['carriers'][0]['on_time_pct']}% on-time year to date. {r['on_time_pct']}% of flights arrived on time ({r['ytd_label']}).",
            og_dir / f"{r['orig'].lower()}-{r['dest'].lower()}.png",
        )
        route_index.append(
            {
                "orig": r["orig"],
                "dest": r["dest"],
                "label": r["label"],
                "pct": r["on_time_pct"],
                "flights": r["flights"],
                "best": r["carriers"][0]["name"] if r["carriers"] else None,
                "best_pct": r["carriers"][0]["on_time_pct"] if r["carriers"] else None,
                "cancel_rate": r["cancel_rate"],
                "ytd_label": r["ytd_label"],
            }
        )
    (OUTPUT_DIR / "routes.json").write_text(json.dumps(route_index))

    for code, info in airports.items():
        out = [r for r in routes.values() if r["orig"] == code]
        inbound = [r for r in routes.values() if r["dest"] == code]
        page = env.get_template("airport.html").render(
            a=info,
            code=code,
            outbound=out,
            inbound=inbound,
            og_url=BASE_URL + f"{code.lower()}.html",
            og_image=BASE_URL + "og/home.png",
            **ctx,
        )
        (OUTPUT_DIR / f"{code.lower()}.html").write_text(page)

    (OUTPUT_DIR / "methodology.html").write_text(
        env.get_template("methodology.html").render(month=month, month_count=month_count)
    )

    (OUTPUT_DIR / "404.html").write_text(
        env.get_template("404.html").render(airports=airports, month=month)
    )

    sitemap = [BASE_URL, BASE_URL + "methodology.html"]
    sitemap += [f"{BASE_URL}{code.lower()}.html" for code in airports]
    sitemap += [f"{BASE_URL}{r['orig'].lower()}-{r['dest'].lower()}.html" for r in routes.values()]
    (OUTPUT_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap)
        + "</urlset>\n"
    )
    (OUTPUT_DIR / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + BASE_URL + "sitemap.xml\n"
    )
    print(f"built {len(routes)} route + {len(airports)} airport + home/methodology pages -> {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
