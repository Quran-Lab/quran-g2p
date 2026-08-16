/* Live status of the expert (ijazah) review of the quran-g2p rulings
 * register. Reads the review sheet (id supplied as the SHEET_ID secret),
 * aggregates verdict counts only — no row content leaves the sheet — and
 * serves:  /progress.svg  /badge.json  /status.json
 */

const VERDICT_COL = "صحيح/خطأ";

export function parseCsv(text) {
  const rows = [];
  let row = [], field = "", inQuotes = false, sawAny = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += c;
    } else if (c === '"') {
      inQuotes = true; sawAny = true;
    } else if (c === ",") {
      row.push(field); field = ""; sawAny = true;
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      if (sawAny || field !== "") { row.push(field); rows.push(row); }
      row = []; field = ""; sawAny = false;
    } else { field += c; sawAny = true; }
  }
  if (sawAny || field !== "") { row.push(field); rows.push(row); }
  return rows;
}

export function computeStats(rows) {
  const idx = rows[0].indexOf(VERDICT_COL);
  const s = { total: 0, reviewed: 0, sahih: 0, khata: 0, wajhan: 0 };
  for (const row of rows.slice(1)) {
    s.total++;
    const v = idx >= 0 && idx < row.length ? row[idx].trim() : "";
    if (!v) continue;
    s.reviewed++;
    if (v === "صحيح") s.sahih++;
    else if (v === "خطأ") s.khata++;
    else if (v === "فيه وجهان") s.wajhan++;
  }
  return s;
}

export function renderBadge(s) {
  const color =
    s.total > 0 && s.reviewed === s.total
      ? (s.khata === 0 ? "brightgreen" : "yellow")
      : s.reviewed === 0 ? "lightgrey" : "blue";
  return JSON.stringify({
    schemaVersion: 1,
    label: "expert review",
    message: `${s.reviewed}/${s.total} rulings`,
    color,
  });
}

export function renderSvg(s, asOf) {
  const W = 680, BAR_W = 632, pct = s.total ? s.reviewed / s.total : 0;
  const pctTxt = (pct * 100).toFixed(1).replace(/\.0$/, "");
  const fill = Math.max(pct * BAR_W, s.reviewed > 0 ? 6 : 0);
  return `<svg width="${W}" height="150" viewBox="0 0 ${W} 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Expert review: ${s.reviewed} of ${s.total} rulings reviewed">
  <rect width="${W}" height="150" rx="12" fill="#0f172a"/>
  <text x="24" y="34" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" letter-spacing="2.5" fill="#94a3b8">IJAZAH EXPERT REVIEW · LIVE</text>
  <text x="24" y="72" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="30" font-weight="600" fill="#f8fafc">${s.reviewed} / ${s.total}<tspan font-size="15" font-weight="400" fill="#94a3b8" dx="10">rulings reviewed · ${pctTxt}%</tspan></text>
  <rect x="24" y="88" width="${BAR_W}" height="10" rx="5" fill="#1e293b"/>
  <rect x="24" y="88" width="${fill.toFixed(1)}" height="10" rx="5" fill="#10b981"/>
  <circle cx="30" cy="122" r="5" fill="#10b981"/>
  <text x="42" y="127" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#e2e8f0">${s.sahih} confirmed</text>
  <circle cx="188" cy="122" r="5" fill="#f59e0b"/>
  <text x="200" y="127" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#e2e8f0">${s.khata} in adjudication</text>
  <circle cx="368" cy="122" r="5" fill="#38bdf8"/>
  <text x="380" y="127" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#e2e8f0">${s.wajhan} two-wajh</text>
  <text x="${W - 24}" y="127" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#64748b">as of ${asOf} UTC · auto-updating</text>
</svg>`;
}

async function loadStats(env) {
  const url = `https://docs.google.com/spreadsheets/d/${env.SHEET_ID}/export?format=csv`;
  const res = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 (quran-g2p review status)" },
    cf: { cacheTtl: 60, cacheEverything: true },
  });
  if (!res.ok) throw new Error(`sheet fetch ${res.status}`);
  return computeStats(parseCsv(await res.text()));
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    const headers = {
      "Cache-Control": "public, max-age=60",
      "Access-Control-Allow-Origin": "*",
    };
    let stats;
    try {
      stats = await loadStats(env);
    } catch (e) {
      return new Response(`status unavailable: ${e.message}`, {
        status: 503,
        headers: { "Cache-Control": "no-store" },
      });
    }
    const asOf = new Date().toISOString().slice(0, 16).replace("T", " ");
    if (path === "/progress.svg")
      return new Response(renderSvg(stats, asOf), {
        headers: { ...headers, "Content-Type": "image/svg+xml" },
      });
    if (path === "/badge.json")
      return new Response(renderBadge(stats), {
        headers: { ...headers, "Content-Type": "application/json" },
      });
    if (path === "/status.json" || path === "/")
      return new Response(
        JSON.stringify({ ...stats, as_of_utc: asOf }, null, 2),
        { headers: { ...headers, "Content-Type": "application/json" } },
      );
    return new Response("not found", { status: 404 });
  },
};
