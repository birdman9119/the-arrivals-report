import json
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BASE_URL, OUTPUT_DIR, SITE_JSON

TPL = Path(__file__).resolve().parent.parent / "site" / "templates"
STATIC = Path(__file__).resolve().parent.parent / "site" / "static"

GOOD = 80
MID = 70


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
    return (
        f'<svg class="spark" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'aria-hidden="true"><polyline points="{points}"/>{dot}</svg>'
    )


def trend_months(months):
    return [m[-2:] for m in months]


def build():
    data = json.loads(SITE_JSON.read_text())
    env = Environment(loader=FileSystemLoader(str(TPL)))
    env.filters["cls"] = cls
    env.filters["sparkline"] = sparkline
    env.filters["monthshort"] = lambda k: k[-5:]

    month = data["latest_month"]
    routes = data["routes"]
    airports = data["airports"]
    trend = trend_months(data.get("month_keys", []))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    OUTPUT_DIR.mkdir(parents=True)
    shutil.copytree(STATIC, OUTPUT_DIR / "static")

    popular = sorted(routes.values(), key=lambda r: -r["flights"])[:40]
    ctx = {"month": month, "month_count": data["month_count"]}
    (OUTPUT_DIR / "index.html").write_text(
        env.get_template("index.html").render(
            airports=airports, month=month, popular=popular, route_count=len(routes)
        )
    )

    route_index = []
    for key, r in routes.items():
        page = env.get_template("route.html").render(r=r, **ctx)
        (OUTPUT_DIR / f"{r['orig'].lower()}-{r['dest'].lower()}.html").write_text(page)
        route_index.append(
            {
                "orig": r["orig"],
                "dest": r["dest"],
                "label": r["label"],
                "pct": r["on_time_pct"],
                "flights": r["flights"],
            }
        )
    (OUTPUT_DIR / "routes.json").write_text(json.dumps(route_index))

    for code, info in airports.items():
        out = [r for r in routes.values() if r["orig"] == code]
        inbound = [r for r in routes.values() if r["dest"] == code]
        page = env.get_template("airport.html").render(
            a=info, code=code, outbound=out, inbound=inbound, month=month, month_count=data["month_count"]
        )
        (OUTPUT_DIR / f"{code.lower()}.html").write_text(page)

    (OUTPUT_DIR / "methodology.html").write_text(
        env.get_template("methodology.html").render(month=month)
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
