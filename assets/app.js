// Static China A-Share index tracker — vanilla JS, reads the JSON the fetcher produces.
const enc = encodeURIComponent, dec = decodeURIComponent;
const BOARD_ORDER = ["Cross", "SSE", "SZSE", "ChiNext", "STAR"];
const CAT_ORDER = ["Broad market", "Sector", "Thematic", "Strategy"];

let DIR = [], META = null, CHANGES = [], STOCKS = [], BY_INDEX = {}, DIR_BY_ID = {};

function h(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === "class") e.className = attrs[k];
    else if (k === "html") e.innerHTML = attrs[k];
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), attrs[k]);
    else e.setAttribute(k, attrs[k]);
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    e.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return e;
}
const boardBadge = b => h("span", { class: "badge " + b.toLowerCase() }, b);
async function getJSON(u) { const r = await fetch(u); if (!r.ok) throw new Error(u + " " + r.status); return r.json(); }

async function boot() {
  try {
    [DIR, META, STOCKS] = await Promise.all([
      getJSON("assets/directory.json"), getJSON("meta.json"), getJSON("assets/stocks.json")]);
    const txt = await (await fetch("changes.jsonl")).text();
    CHANGES = txt.split("\n").filter(Boolean).map(JSON.parse);
  } catch (e) {
    document.querySelector("main").append(h("div", { class: "empty" },
      "Could not load data files. Serve this folder over HTTP (e.g. python -m http.server) and reload."));
    return;
  }
  DIR.forEach(d => DIR_BY_ID[d.id] = d);
  CHANGES.forEach(c => (BY_INDEX[c.index] = BY_INDEX[c.index] || []).push(c));
  renderStats(); setupSearch();
  addEventListener("hashchange", route); route();
}

function renderStats() {
  const s = META.summary || {};
  const when = (META.last_run || "").replace("T", " ").slice(0, 16);
  const parts = [
    h("span", {}, h("b", {}, String(DIR.length)), " indices"),
    h("span", {}, h("b", {}, String(STOCKS.length)), " stocks"),
    h("span", {}, "updated ", h("b", {}, when || "—")),
    (s.failed ? h("span", { class: "muted" }, `${s.failed} failed this run`) : null)];
  document.querySelector(".stats").replaceChildren(...parts.filter(Boolean));
}

function tabs(active) {
  return h("nav", { class: "tabs" },
    h("a", { href: "#/", class: active === "dir" ? "active" : "" }, "Directory"),
    h("a", { href: "#changes", class: active === "changes" ? "active" : "" }, "Recent changes"));
}

function route() {
  const m = document.querySelector("main"); m.replaceChildren();
  const hash = location.hash;
  if (hash.startsWith("#i/")) return renderIndex(dec(hash.slice(3)), m);
  if (hash.startsWith("#s/")) return renderStock(dec(hash.slice(3)), m);
  if (hash === "#changes") return renderChanges(m);
  return renderDirectory(m);
}

function displayName(d) {
  if (d.name_en) return d.name + " / " + d.name_en;
  return d.name;
}

// ---- directory ----
function renderDirectory(m) {
  m.append(tabs("dir"));
  for (const board of BOARD_ORDER) {
    for (const cat of CAT_ORDER) {
      const items = DIR.filter(d => d.board === board && d.category === cat);
      if (!items.length) continue;
      const cards = h("div", { class: "cards" });
      for (const d of items) {
        const changed = d.last_change_type === "change";
        cards.append(h("a", { class: "card", href: "#i/" + enc(d.id) },
          h("div", { class: "nm" }, d.name),
          d.name_en ? h("div", { class: "nm-en" }, d.name_en) : null,
          h("div", { class: "meta" },
            h("span", { class: "count" }, (d.count ?? "?") + " stocks"),
            h("span", {}, (changed ? "changed " : "since ") + (d.last_changed || "—")))));
      }
      m.append(h("section", { class: "group" },
        h("h2", {}, boardBadge(board), cat, " ", h("span", { class: "muted" }, "· " + items.length)), cards));
    }
  }
}

// ---- index detail ----
async function renderIndex(id, m) {
  const d = DIR_BY_ID[id];
  m.append(h("a", { class: "back", href: "#/" }, "← Directory"));
  if (!d) return m.append(h("div", { class: "empty" }, "Unknown index."));
  const panel = h("div", { class: "panel" },
    h("div", { class: "detail-head" }, boardBadge(d.board), h("h2", {}, displayName(d))),
    h("div", { class: "sub" }, `${d.category} · ${d.count} constituents · `
      + (d.last_change_type === "change" ? "last changed " : "baselined ") + (d.last_changed || "—")),
    h("div", {}, "Loading constituents…"));
  m.append(panel);
  let doc;
  try { doc = await getJSON("current/" + d.file); }
  catch (e) { panel.lastChild.replaceWith(h("div", { class: "empty" }, "Could not load constituents.")); return; }

  const rows = doc.members.map((mm, i) => h("tr", {},
    h("td", { class: "muted" }, String(i + 1)),
    h("td", {}, h("a", { class: "sym", href: "#s/" + enc(mm.symbol) }, mm.symbol)),
    h("td", {}, mm.name || ""),
    h("td", { class: "muted" }, mm.name_en || "")));
  const table = h("table", {}, h("thead", {}, h("tr", {},
    h("th", {}, "#"), h("th", {}, "Code"), h("th", {}, "Name"), h("th", {}, "English"))),
    h("tbody", {}, rows));

  const hist = (BY_INDEX[id] || []).slice().sort((a, b) => b.date.localeCompare(a.date));
  panel.lastChild.replaceWith(h("div", {},
    h("div", { class: "section-title" }, `Constituents (${doc.members.length})`), table,
    h("div", { class: "section-title" }, "Change history"),
    hist.length ? h("div", { class: "changes-list" }, hist.map(changeCard))
      : h("div", { class: "muted" }, "No history yet.")));
}

// ---- changes feed ----
function changeCard(c) {
  const d = DIR_BY_ID[c.index];
  const board = d ? d.board : (c.index.split(":")[0] || "Cross");
  const top = h("div", { class: "top" },
    h("span", {}, boardBadge(board),
      " ", h("a", { href: "#i/" + enc(c.index) }, d ? displayName(d) : c.index)),
    h("span", {}, h("span", { class: "pill " + c.type }, c.type), " ",
      h("span", { class: "date" }, c.date)));
  let body;
  if (c.type === "initial") {
    body = h("div", { class: "muted" }, `Added to tracking — ${c.added.length} constituents`);
  } else {
    body = h("div", {},
      c.added.map(a => h("span", { class: "chip add" }, "+ " + a.symbol)),
      c.removed.map(r => h("span", { class: "chip rem" }, "− " + r.symbol)));
  }
  return h("div", { class: "ch" }, top, body);
}

function renderChanges(m) {
  m.append(tabs("changes"));
  const real = CHANGES.filter(c => c.type === "change").sort((a, b) => b.date.localeCompare(a.date));
  const initials = CHANGES.filter(c => c.type === "initial");
  m.append(h("div", { class: "section-title" }, "Membership changes (add / remove)"));
  m.append(real.length ? h("div", { class: "changes-list" }, real.map(changeCard))
    : h("div", { class: "empty" }, "No membership changes recorded yet — the baseline was just established. "
      + "Changes appear here automatically when constituents are added or removed (~2×/year)."));
  if (initials.length) {
    const dates = [...new Set(initials.map(c => c.date))].join(", ");
    m.append(h("div", { class: "section-title" }, "Baseline"),
      h("div", { class: "ch" }, h("div", { class: "muted" },
        `${initials.length} indices added to tracking on ${dates}.`)));
  }
}

// ---- stock lookup ----
function setupSearch() {
  const input = document.querySelector(".search input");
  const box = document.querySelector(".results");
  const close = () => box.classList.remove("open");
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (q.length < 2) return close();
    const hits = STOCKS.filter(s => s.name.toLowerCase().includes(q)
      || s.symbol.toLowerCase().includes(q)
      || (s.name_en || "").toLowerCase().includes(q)).slice(0, 12);
    box.replaceChildren(...(hits.length ? hits.map(s => h("a", {
      class: "row", href: "#s/" + enc(s.symbol),
      onclick: () => { close(); input.value = ""; }
    }, h("span", {}, `${s.symbol} ${s.name}`),
       h("small", {}, `${s.indices.length} indices`)))
      : [h("div", { class: "row muted" }, "No matches")]));
    box.classList.add("open");
  });
  document.addEventListener("click", e => { if (!e.target.closest(".search")) close(); });
}

function renderStock(key, m) {
  m.append(h("a", { class: "back", href: "#/" }, "← Directory"));
  const s = STOCKS.find(x => x.symbol === key);
  if (!s) return m.append(h("div", { class: "empty" }, "Stock not found."));
  const blocks = [];
  blocks.push(h("div", { class: "section-title" }, `Member of ${s.indices.length} tracked indices`));
  blocks.push(h("div", { class: "cards" }, s.indices.sort().map(id => {
    const d = DIR_BY_ID[id];
    return h("a", { class: "card", href: "#i/" + enc(id) },
      h("div", { class: "nm" }, d ? displayName(d) : id),
      h("div", { class: "meta" }, h("span", { class: "muted" }, d ? d.category : "")));
  })));
  m.append(h("div", { class: "panel" },
    h("div", { class: "detail-head" }, h("h2", {}, `${s.symbol} ${s.name}`)),
    h("div", { class: "sub" }, s.name_en || ""),
    ...blocks));
}

boot();
