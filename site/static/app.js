let airports = [];
fetch("airports.json")
  .then((r) => r.json())
  .then((d) => { airports = d; });

const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function setupCombo(inputId, hiddenId, suggestId) {
  const input = document.getElementById(inputId);
  const hidden = document.getElementById(hiddenId);
  const suggest = document.getElementById(suggestId);
  let active = -1;

  function close() { suggest.hidden = true; active = -1; }

  function render(q) {
    const terms = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let hits;
    if (!terms.length) {
      hits = airports.slice().sort((a, b) => b.flights - a.flights).slice(0, 12);
    } else {
      const scored = [];
      airports.forEach((a) => {
        const hay = (a.code + " " + a.city + " " + a.name).toLowerCase();
        if (!terms.every((t) => hay.includes(t))) return;
        const joined = terms.join(" ");
        let score;
        if (a.code.toLowerCase() === joined) score = 0;
        else if (a.code.toLowerCase().startsWith(terms[0])) score = 1;
        else if (a.city.toLowerCase().startsWith(terms[0])) score = 2;
        else score = 3;
        scored.push([a, score]);
      });
      scored.sort((x, y) => x[1] - y[1] || y[0].flights - x[0].flights);
      hits = scored.slice(0, 12).map((x) => x[0]);
    }
    if (!hits.length) { suggest.innerHTML = "<p class=\"suggest-empty\">No airports match.</p>"; suggest.hidden = false; return; }
    suggest.innerHTML = hits.map((a, i) =>
      `<button type="button" class="suggest-item" data-index="${i}" data-code="${a.code}" data-label="${a.code} — ${a.city}">${a.code} — ${a.city} <span class="muted">${a.name}</span></button>`
    ).join("");
    suggest.hidden = false;
  }

  input.addEventListener("input", () => { hidden.value = ""; render(input.value); tryMapHighlight(); });
  input.addEventListener("focus", () => render(input.value));
  input.addEventListener("blur", () => setTimeout(close, 150));
  input.addEventListener("keydown", (e) => {
    const items = suggest.querySelectorAll(".suggest-item");
    if (e.key === "ArrowDown" && suggest.hidden === false) { e.preventDefault(); active = (active + 1) % items.length; items[active] && items[active].focus(); }
    else if (e.key === "ArrowUp" && suggest.hidden === false) { e.preventDefault(); active = (active - 1 + items.length) % items.length; items[active] && items[active].focus(); }
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); }
  });
  suggest.addEventListener("click", (e) => {
    const item = e.target.closest(".suggest-item");
    if (!item) return;
    input.value = item.dataset.label.split(" — ")[0] + " — " + item.dataset.label.split(" — ")[1];
    hidden.value = item.dataset.code;
    close();
    tryMapHighlight();
  });
}

function tryMapHighlight() {
  if (!MAP) return;
  const from = document.getElementById("from-code").value;
  const to = document.getElementById("to-code").value;
  if (!from || !to) {
    const fromIn = document.getElementById("from").value.trim().toUpperCase();
    const toIn = document.getElementById("to").value.trim().toUpperCase();
    const f = airports.find((a) => a.code === fromIn);
    const t = airports.find((a) => a.code === toIn);
    if (f && t) { MAP.highlight(f.code, t.code); return; }
    MAP.highlight(from || f?.code, to || t?.code);
    return;
  }
  MAP.highlight(from, to);
}

function routePage(from, to, date) {
  const d = new Date(date + "T00:00:00");
  const url = `${from.toLowerCase()}-${to.toLowerCase()}.html`;
  const q = isNaN(d) ? "" : "?date=" + date;
  location.href = url + q;
}

const MAP = (function () {
  const wrap = document.getElementById("map-wrap");
  if (!wrap) return null;
  const tip = document.getElementById("map-tip");

  const projection = d3.geoAlbersUsa().scale(1300).translate([487.5, 305]);
  const TOP_ROUTES = 30;

  let ports = {}, routeLines = {}, hotLine = null;

  function distMiles(a, b) {
    const R = 3958.8;
    const dLat = ((b.lat - a.lat) * Math.PI) / 180;
    const dLon = ((b.lon - a.lon) * Math.PI) / 180;
    const s = Math.sin(dLat / 2) ** 2 +
      Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(s));
  }

  function linePath(a, b, bow) {
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
    const len = Math.hypot(dx, dy) || 1;
    const nx = -dy / len, ny = dx / len;
    const cx = mx + nx * bow, cy = my + ny * bow;
    return `M${a[0].toFixed(1)},${a[1].toFixed(1)} Q${cx.toFixed(1)},${cy.toFixed(1)} ${b[0].toFixed(1)},${b[1].toFixed(1)}`;
  }

  function routeTooltip(r, miles) {
    return (
      `<strong>${r.orig} → ${r.dest}</strong> ${r.label}<br>` +
      `<b>${r.pct}%</b> on-time year to date (${r.ytd_label})${r.cancel_rate ? ` · ${r.cancel_rate}% cancelled` : ""}<br>` +
      `Best: ${r.best} (${r.best_pct}%) · ${r.flights.toLocaleString()} flights · ~${Math.round(miles).toLocaleString()} mi`
    );
  }

  function tipShow(html, x, y) {
    tip.innerHTML = html;
    tip.hidden = false;
    const rect = wrap.getBoundingClientRect();
    const tipRect = tip.getBoundingClientRect();
    let tx = x - rect.left, ty = y - rect.top - tipRect.height - 10;
    if (tx + tipRect.width > rect.width - 8) tx = rect.width - tipRect.width - 8;
    if (tx < 8) tx = 8;
    if (ty < 8) ty = y - rect.top + 14;
    tip.style.left = tx + "px";
    tip.style.top = ty + "px";
  }
  function tipHide() { tip.hidden = true; }

  function render(atlas, airports, routes) {
    airports.forEach((a) => { ports[a.code] = a; });

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 975 610");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Map of U.S. airports and flight routes");

    const statesG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    statesG.setAttribute("class", "states");
    const statePath = d3.geoPath();
    topojson.feature(atlas, atlas.objects.states).features.forEach((f) => {
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", statePath(f));
      statesG.appendChild(p);
    });
    svg.appendChild(statesG);

    const topKeys = new Set(
      routes.slice().sort((a, b) => b.flights - a.flights).slice(0, TOP_ROUTES).map((r) => `${r.orig}_${r.dest}`)
    );

    const maxFlights = Math.max(...routes.map((r) => r.flights));
    const lineWidth = (f) => (f >= maxFlights * 0.1 ? 1.2 + Math.pow(f / maxFlights, 0.4) * 4 : 1.2);

    const routesG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    routesG.setAttribute("class", "map-routes");
    const halosG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    halosG.setAttribute("class", "map-halos");
    routes.forEach((r) => {
      const a = ports[r.orig], b = ports[r.dest];
      if (!a || !b) return;
      const miles = distMiles(a, b);
      const xyA = projection([a.lon, a.lat]);
      const xyB = projection([b.lon, b.lat]);
      if (!xyA || !xyB) return;
      const bow = Math.min(5 + miles * 0.028, 110);
      const d = linePath(xyA, xyB, bow);
      const isTop = topKeys.has(`${r.orig}_${r.dest}`);
      const tooltip = () => routeTooltip(r, miles);
      const wire = (el, onEnter, onLeave) => {
        el.addEventListener("mousemove", (e) => tipShow(tooltip(), e.clientX, e.clientY));
        el.addEventListener("mouseleave", onLeave);
        el.addEventListener("click", () => routePage(r.orig, r.dest, ""));
        if (onEnter) el.addEventListener("mouseenter", onEnter);
      };

      const halo = document.createElementNS("http://www.w3.org/2000/svg", "path");
      halo.setAttribute("d", d);
      halo.setAttribute("class", "route-hit");
      wire(halo);
      halosG.appendChild(halo);

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("class", "route-line" + (isTop ? " top" : ""));
      if (isTop) path.setAttribute("stroke-width", lineWidth(r.flights));
      path.setAttribute("data-orig", r.orig);
      path.setAttribute("data-dest", r.dest);
      wire(path, () => {
        path.classList.add("reveal");
        routesG.appendChild(path);
      }, () => path.classList.remove("reveal"));
      routesG.appendChild(path);
      routeLines[`${r.orig}_${r.dest}`] = path;
    });
    svg.appendChild(halosG);
    svg.appendChild(routesG);

    const portsG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    portsG.setAttribute("class", "map-ports");
    Object.values(ports).forEach((a) => {
      const xy = projection([a.lon, a.lat]);
      if (!xy) return;
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", xy[0]);
      c.setAttribute("cy", xy[1]);
      c.setAttribute("r", 4);
      c.setAttribute("class", "port-dot");
      c.setAttribute("data-code", a.code);
      const mine = routes.filter((r) => r.orig === a.code || r.dest === a.code);
      c.addEventListener("mousemove", (e) => {
        tipShow(`<strong>${a.code}</strong> ${a.city}<br>${mine.length} routes from here`, e.clientX, e.clientY);
      });
      c.addEventListener("mouseleave", () => {
        tipHide();
        mine.forEach((r) => routeLines[`${r.orig}_${r.dest}`].classList.remove("reveal"));
      });
      c.addEventListener("mouseenter", () => {
        mine.forEach((r) => routeLines[`${r.orig}_${r.dest}`].classList.add("reveal"));
      });
      c.addEventListener("click", () => (location.href = a.code.toLowerCase() + ".html"));
      portsG.appendChild(c);
    });
    svg.appendChild(portsG);

    wrap.insertBefore(svg, tip);
  }

  function highlight(from, to) {
    if (hotLine) { hotLine.classList.remove("hot"); hotLine = null; }
    if (!from || !to || from === to) return;
    const key = `${from}_${to}`;
    const line = routeLines[key] || routeLines[`${to}_${from}`];
    if (!line) {
      const rect = wrap.getBoundingClientRect();
      tipShow(
        `<strong>${from} → ${to}</strong><br>We don't track this route (yet).`,
        rect.left + rect.width / 2, rect.top + rect.height / 2
      );
      return;
    }
    line.classList.add("hot");
    hotLine = line;
  }

  return { render, highlight };
})();

if (MAP) {
  Promise.all([
    fetch("static/us-atlas.json").then((r) => r.json()),
    fetch("airports.json").then((r) => r.json()),
    fetch("routes.json").then((r) => r.json()),
  ]).then(([atlas, airports, routes]) => {
    MAP.render(atlas, airports, routes);
  });
}

function resolveAirport(input, hidden) {
  if (hidden.value) return hidden.value;
  const raw = input.value.trim();
  if (!raw) return null;
  const exact = airports.find((a) => a.code === raw.toUpperCase());
  if (exact) return exact.code;
  const terms = raw.toLowerCase().split(/\s+/).filter(Boolean);
  const hits = airports.filter((a) => terms.every((t) => (a.code + " " + a.city + " " + a.name).toLowerCase().includes(t)));
  if (hits.length === 1) return hits[0].code;
  return null;
}

const form = document.getElementById("trip-form");
if (form) {
  setupCombo("from", "from-code", "from-suggest");
  setupCombo("to", "to-code", "to-suggest");
  const msg = document.getElementById("wizard-msg");
  document.getElementById("swap").addEventListener("click", () => {
    const f = document.getElementById("from");
    const t = document.getElementById("to");
    const fh = document.getElementById("from-code");
    const th = document.getElementById("to-code");
    [f.value, t.value] = [t.value, f.value];
    [fh.value, th.value] = [th.value, fh.value];
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const from = resolveAirport(document.getElementById("from"), document.getElementById("from-code"));
    const to = resolveAirport(document.getElementById("to"), document.getElementById("to-code"));
    const date = document.getElementById("date").value;
    if (!from || !to) { msg.hidden = false; msg.textContent = "Type a 3-letter airport code (e.g. JFK) or pick from the suggestions."; return; }
    if (from === to) { msg.hidden = false; msg.textContent = "Pick two different airports."; return; }
    msg.hidden = true;
    routePage(from, to, date);
  });
}
