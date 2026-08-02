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
    const hits = terms.length
      ? airports.filter((a) => terms.every((t) => (a.code + " " + a.city + " " + a.name).toLowerCase().includes(t))).slice(0, 8)
      : airports.slice(0, 8);
    if (!hits.length) { suggest.innerHTML = "<p class=\"suggest-empty\">No airports match.</p>"; suggest.hidden = false; return; }
    suggest.innerHTML = hits.map((a, i) =>
      `<button type="button" class="suggest-item" data-index="${i}" data-code="${a.code}" data-label="${a.code} — ${a.city}">${a.code} — ${a.city} <span class="muted">${a.name}</span></button>`
    ).join("");
    suggest.hidden = false;
  }

  input.addEventListener("input", () => { hidden.value = ""; render(input.value); });
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
  });
}

function routePage(from, to, date) {
  const d = new Date(date + "T00:00:00");
  const url = `${from.toLowerCase()}-${to.toLowerCase()}.html`;
  const q = isNaN(d) ? "" : "?date=" + date;
  location.href = url + q;
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
    const from = document.getElementById("from-code").value;
    const to = document.getElementById("to-code").value;
    const date = document.getElementById("date").value;
    if (!from || !to) { msg.hidden = false; msg.textContent = "Pick an airport from the suggestions."; return; }
    if (from === to) { msg.hidden = false; msg.textContent = "Pick two different airports."; return; }
    msg.hidden = true;
    routePage(from, to, date);
  });
}
