const input = document.getElementById("route-search");
const results = document.getElementById("results");
let routes = [];

fetch("routes.json")
  .then((r) => r.json())
  .then((d) => { routes = d; });

input.addEventListener("input", () => {
  const q = input.value.trim().toLowerCase();
  if (q.length < 2) { results.hidden = true; results.innerHTML = ""; return; }
  const terms = q.split(/[^a-z0-9]+/).filter(Boolean);
  const hits = routes
    .filter((r) => terms.every((t) => (r.orig + r.dest + r.label).toLowerCase().includes(t)))
    .slice(0, 12);
  if (!hits.length) { results.hidden = false; results.innerHTML = "<p class=\"empty\">No routes match.</p>"; return; }
  results.hidden = false;
  results.innerHTML = hits.map((r) => `
    <a class="result" href="${r.orig.toLowerCase()}-${r.dest.toLowerCase()}.html">
      <span class="result-code">${r.orig} → ${r.dest}</span>
      <span class="result-label">${r.label}</span>
      <span class="result-pct">${r.pct}% on-time</span>
    </a>`).join("");
});
