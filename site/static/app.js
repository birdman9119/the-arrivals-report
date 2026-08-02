const input = document.getElementById("airport-search");
const rows = Array.from(document.querySelectorAll(".airport-row"));
const empty = document.getElementById("no-results");

input.addEventListener("input", () => {
  const q = input.value.trim().toLowerCase();
  let visible = 0;
  for (const row of rows) {
    const match = row.dataset.search.toLowerCase().includes(q);
    row.hidden = !match;
    if (match) visible++;
  }
  if (empty) empty.hidden = visible > 0 || q === "";
});
