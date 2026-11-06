// Builds the clean trade table (dashboard/canli/islemler.csv) from the bots' log files, and optionally a
// single-file snapshot of the panel with the data inside (for places that cannot fetch from GitHub).
//   node dashboard/canli/build_snapshot.mjs                 # table + summary
//   node dashboard/canli/build_snapshot.mjs out.html        # also the self-contained snapshot page
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");
const P = createRequire(import.meta.url)("./normalize.js");

const raw = {};
for (const [k, f] of Object.entries(P.FILES)) raw[k] = existsSync(join(repo, f)) ? readFileSync(join(repo, f), "utf8") : null;
const data = P.build(raw);
const names = Object.fromEntries(P.STRATEGIES.map((s) => [s.id, s]));

const TR_STATUS = { closed: "kapandı", open: "açık" };
const REAL = { yes: "gerçek piyasada da dolardı", no: "gerçek piyasada DOLMAZDI", pending: "kontrol bekliyor" };
const cols = ["strateji", "ortam", "yon", "coin", "giris_zamani_utc", "giris_fiyati", "cikis_zamani_utc", "cikis_fiyati",
  "net_sonuc", "birim", "kar_usdt_10k_kasada", "durum", "cikis_sebebi", "gercek_fiyat_kontrolu", "gercek_fiyatla_net_yuzde", "not"];
const esc = (v) => (v === null || v === undefined ? "" : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
const r = (v, d) => (v === null || v === undefined ? "" : Number(v).toFixed(d));
const lines = [cols.join(",")];
for (const t of data.trades) {
  lines.push([
    names[t.strategy].name, t.track === "demo" ? "Bitget demo hesap" : "kâğıt (gerçek fiyat)", t.side, t.symbol,
    (t.entry_time || "").slice(0, 16).replace("T", " "), t.entry_price, (t.exit_time || "").slice(0, 16).replace("T", " "),
    t.exit_price === null ? "" : +Number(t.exit_price).toPrecision(8), r(t.net_pct, 2), t.unit,
    r(t.pnl_usdt, 2) + (t.estimated ? " (tahmin)" : ""), TR_STATUS[t.status] || t.status, t.reason,
    t.real ? REAL[t.real.state] : "", t.real && t.real.state === "yes" ? r(t.real.ret, 2) : t.real && t.real.state === "no" ? "0 (işlem olmazdı)" : "",
    t.note,
  ].map(esc).join(","));
}
writeFileSync(join(here, "islemler.csv"), lines.join("\n") + "\n");

for (const s of data.strategies) {
  const st = s.stats;
  console.log(`${s.name.padEnd(24)} ${s.track.padEnd(5)} closed ${st.closed} open ${st.open} win ${st.winRate === null ? "-" : (st.winRate * 100).toFixed(0) + "%"} pnl ${st.pnl.toFixed(1)} (${st.pnlPct.toFixed(2)}%) dd ${st.maxDd.toFixed(2)}%`);
}
const demoReal = P.stats(data.trades.filter((t) => t.track === "demo"), true);
console.log(`demo at real prices: counted ${demoReal.counted}, pnl ${demoReal.pnl.toFixed(1)}`);
console.log(`pending orders: ${data.pending.length}`);

const out = process.argv[2];
if (out) {
  // keep only what the panel uses: drop cancelled demo limits and the new-coin archive lists
  const slim = { ...raw };
  const fd = P.parseJson(raw.fitilDemo);
  if (fd) slim.fitilDemo = JSON.stringify({ trades: Object.fromEntries(Object.entries(fd.trades).filter(([, t]) => t.status !== "cancelled")) });
  for (const k of ["yeniCoin", "yeniCoinHedge"]) {
    const s = P.parseJson(raw[k]);
    if (s) { delete s.known; slim[k] = JSON.stringify(s); }
  }
  let html = readFileSync(join(here, "panel.html"), "utf8");
  const stamp = new Date().toISOString();
  html = html.replace('<script src="normalize.js"></script>',
    () => `<script>${readFileSync(join(here, "normalize.js"), "utf8")}</script>\n<script>window.PANEL_RAW=${JSON.stringify(slim).replace(/</g, "\\u003c")};window.PANEL_STAMP="${stamp}";</script>`);
  writeFileSync(out, html);
  console.log(`snapshot: ${out}`);
}
