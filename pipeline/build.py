import json
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BASE_URL, OUTPUT_DIR, SITE_JSON

TPL = Path(__file__).resolve().parent.parent / "site" / "templates"
STATIC = Path(__file__).resolve().parent.parent / "site" / "static"


def build():
    data = json.loads(SITE_JSON.read_text())
    env = Environment(loader=FileSystemLoader(str(TPL)))
    month = data["month"]
    airports = data["airports"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    OUTPUT_DIR.mkdir(parents=True)
    shutil.copytree(STATIC, OUTPUT_DIR / "static")

    (OUTPUT_DIR / "index.html").write_text(
        env.get_template("index.html").render(airports=airports, month=month)
    )
    for a in airports:
        page = env.get_template("airport.html").render(a=a, month=month)
        (OUTPUT_DIR / f"{a['code'].lower()}.html").write_text(page)
    (OUTPUT_DIR / "methodology.html").write_text(
        env.get_template("methodology.html").render(month=month)
    )

    sitemap = [BASE_URL, BASE_URL + "methodology.html"]
    sitemap += [f"{BASE_URL}{a['code'].lower()}.html" for a in airports]
    (OUTPUT_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap)
        + "</urlset>\n"
    )
    (OUTPUT_DIR / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + BASE_URL + "sitemap.xml\n"
    )
    print(f"built {len(airports) + 2} pages -> {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
