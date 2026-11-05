// ASGO live results: turns the bots' own log files (forward/ in the repo) into one trade list and
// per-strategy statistics. Used by panel.html (browser, live from GitHub) and build_snapshot.mjs (node,
// writes the clean table). Nothing here changes a trade; it only reads and adds up.
(function (root) {
  "use strict";

  const BASE = 10000; // every strategy is tracked on its own 10,000 USDT (demo: the shared demo account)
  const OUTAGE = { from: "2026-10-20T13:17:00Z", to: "2026-10-28T19:00:00Z" };

  // raw files the panel needs, relative to the repo root
  const FILES = {
    fitilDemo: "forward/bitget_fitil/state.json",
    dalgaDemo: "forward/bitget_demo_dalga/state.json",
    pusulaDemo: "forward/bitget_demo/state.json",
    paperFitil: "forward/paper_fitil/state.json",
    yeniCoin: "forward/paper_yeni_coin/state.json",
    yeniCoinHedge: "forward/paper_yeni_coin_hedge/state.json",
    aslanNas: "forward/paper_aslan_nas/state.json",
    realCheck: "dashboard/canli/demo_gercek_kontrol.csv",
  };

  const STRATEGIES = [
    { id: "fitil_demo", name: "Fitil Avcısı", track: "demo", side: "long", since: "2026-10-12",
      about: "Günlük yükselişteki coine, saatin açılış fiyatının %5 altına alış emri koyar. Ani panik iğnesini yakalar, 3 saat sonra satar. Stop yok." },
    { id: "derin_demo", name: "Derin Fitil", track: "demo", side: "long", since: "2026-10-17",
      about: "Günlük düşüşteki coine, açılışın %8 altına alış emri koyar. 3 saat tutar, %4 stop (4 Kasım'dan beri)." },
    { id: "dalga_demo", name: "Dalga", track: "demo", side: "long", since: "2026-10-11",
      about: "Günlük yükseliş trendindeki coin son 24 saatin zirvesini kırınca alır, birkaç gün tutar. Piyasa 7 Ekim'den beri düşüşte, şart oluşmadı." },
    { id: "pusula_demo", name: "Pusula v2", track: "demo", side: "long", since: "2026-10-10",
      about: "4 saatlik trend takibi. BTC düşüşe geçince açık long'ları kapatır. Düşüş piyasasında işlem açmaz." },
    { id: "fitil_paper", name: "Fitil Avcısı", track: "paper", side: "long", since: "2026-10-17",
      about: "Demodaki kuralın aynısı, 81 coinde, Bitget'in gerçek piyasa fiyatlarıyla kâğıt üstünde." },
    { id: "derin_paper", name: "Derin Fitil", track: "paper", side: "long", since: "2026-10-17",
      about: "Demodaki kuralın aynısı, 81 coinde, gerçek piyasa fiyatlarıyla kâğıt üstünde." },
    { id: "pusula_paper", name: "Pusula (ilk sürüm)", track: "paper", side: "long", since: "2026-10-01",
      about: "Dondurulmuş ilk Pusula kuralı, 16 coin. Kâğıt kaydı 10 Ekim'den sonra güncellenmedi; v2 demoda devam ediyor." },
    { id: "yeni_coin", name: "Yeni Coin Short", track: "paper", side: "short", since: "2026-11-04",
      about: "Binance'e yeni listelenen coini ertesi gün short'lar, 14 gün tutar, %40 stop. Kasanın %1'i riske edilir." },
    { id: "yeni_coin_hedge", name: "Yeni Coin + BTC koruma", track: "paper", side: "short", since: "2026-11-05",
      about: "Listelemeden bir hafta sonra coini short'lar, aynı anda BTC long açar. Piyasanın yönünden bağımsız kazanmayı dener." },
    { id: "aslan_nas", name: "Aslan Nasdaq", track: "paper", side: "long/short", since: "2026-11-05",
      about: "Aslan'ın likidite ve yapı kırılımı kuralı, Nasdaq vadeli 1 saatlik grafik. Hedef 2R. Sonuçlar R cinsinden; 1R = kasanın %1'i sayılır." },
  ];

  // Pusula paper log (forward/pusula_kagit.md), frozen since 2026-10-10; R results, 1R ~ 1% of equity
  const PUSULA_PAPER = [
    { symbol: "BTC", entry_time: "2026-10-02T08:00:00Z", entry_price: 85947.4, exit_time: "2026-10-07T13:00:00Z", r: -1.06 },
    { symbol: "LTC", entry_time: "2026-10-02T08:00:00Z", entry_price: 70.02, exit_time: "2026-10-07T21:00:00Z", r: -1.03 },
    { symbol: "BNB", entry_time: "2026-10-03T20:00:00Z", entry_price: 789.24, exit_time: "2026-10-07T02:00:00Z", r: -1.05 },
  ];

  // LINK 2026-10-29: the bot sold but could not read the sell fill (nan in the log). The position did
  // close (21:03 run: 0 USDT margin locked). The account equity moved 9957.37 (10-28 23:05) -> 9922.54
  // (10-29 21:03); minus BCH +16.67 and BNB -45.85 leaves about -5.6 USDT for LINK.
  const LINK_ESTIMATE = { key: "fitlink2026102920", pnl: -5.6 };

  const num = (v) => (v === null || v === undefined || v === "" || Number.isNaN(Number(v)) ? null : Number(v));
  const coin = (pair) => String(pair || "").split("/")[0].replace(/USDT$/, "");
  const iso = (s) => (s ? new Date(s.length === 10 ? s + "T00:00:00Z" : s).toISOString() : null);

  function parseJson(text) {
    if (!text) return null;
    return JSON.parse(text.replace(/\bNaN\b/g, "null").replace(/-?\bInfinity\b/g, "null"));
  }

  function parseCsv(text) {
    if (!text) return [];
    const rows = [];
    let row = [], cell = "", q = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) {
        if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
        else if (c === '"') q = false;
        else cell += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cell); rows.push(row); row = []; cell = "";
      } else cell += c;
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    const head = rows.shift() || [];
    return rows.filter((r) => r.length > 1).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
  }

  function demoFitil(state, checks) {
    const out = [], pending = [];
    const byKey = Object.fromEntries(checks.map((c) => [c.key, c]));
    for (const [key, t] of Object.entries((state && state.trades) || {})) {
      const mode = t.mode === "derin" ? "derin" : "fitil";
      const sid = mode + "_demo";
      if (t.status === "pending") { pending.push({ strategy: sid, symbol: coin(t.pair), price: t.limit_price, hour: t.hour }); continue; }
      if (t.status !== "open" && t.status !== "closed") continue;
      const notional = num(t.fill_price) * num(t.amount);
      let pnl = num(t.pnl_usdt), est = false, note = "";
      if (t.status === "closed" && pnl === null && key === LINK_ESTIMATE.key) {
        pnl = LINK_ESTIMATE.pnl; est = true;
        note = "Bot satış fiyatını okuyamadı (logda nan). Pozisyon kapandı; hesap bakiyesinden yaklaşık -5.6 USDT.";
      }
      const c = byKey[key];
      let real = null;
      if (c) {
        real = c.status === "checked"
          ? { state: c.real_fill === "yes" ? "yes" : "no", ret: num(c.real_ret_pct), low: num(c.real_low), exit: num(c.real_exit),
              pnl: num(c.real_ret_pct) * notional / 100 }
          : { state: "pending" };
      } else if (t.status === "closed") real = { state: "pending" };
      if (key === "fitnear2026102013") note = "Kesinti: emir 20 Ekim'de iptal edilmeliydi, 24 Ekim'de doldu ve 3 saat yerine 4 gün tutuldu. Kural dışı.";
      out.push({
        id: key, strategy: sid, track: "demo", side: "long", symbol: coin(t.pair),
        entry_time: iso(t.fill_time), entry_price: num(t.fill_price),
        exit_time: t.status === "closed" ? iso(t.exit_time) : null,
        exit_price: t.status === "closed" ? num(t.exit_price) : null,
        net_pct: t.status === "closed" ? (est ? (pnl / notional) * 100 : num(t.ret_pct)) : null,
        pnl_usdt: t.status === "closed" ? pnl : null, estimated: est, unit: "%",
        status: t.status, reason: t.exit_reason || "", real, note,
      });
    }
    return { trades: out, pending };
  }

  function demoGeneric(state, sid) {
    const out = [], pending = [];
    for (const [key, t] of Object.entries((state && state.trades) || {})) {
      if (t.status === "pending") { pending.push({ strategy: sid, symbol: coin(t.pair), price: t.plan_entry, hour: t.signal_time }); continue; }
      if (t.status !== "open" && t.status !== "closed") continue;
      const notional = num(t.fill_price) * num(t.amount);
      const pnl = num(t.pnl_usdt);
      out.push({
        id: key, strategy: sid, track: "demo", side: t.side || "long", symbol: coin(t.pair),
        entry_time: iso(t.fill_time), entry_price: num(t.fill_price),
        exit_time: t.status === "closed" ? iso(t.exit_time) : null,
        exit_price: t.status === "closed" ? num(t.exit_price) : null,
        net_pct: t.status === "closed" && pnl !== null && notional ? (pnl / notional) * 100 : null,
        pnl_usdt: t.status === "closed" ? pnl : null, unit: "%", status: t.status, reason: t.exit_reason || "",
        real: t.status === "closed" ? { state: "pending" } : null, note: "",
      });
    }
    return { trades: out, pending };
  }

  function paperFitil(state) {
    return ((state && state.trades) || []).map((t, i) => ({
      id: "pf" + i, strategy: (t.mode === "derin" ? "derin" : "fitil") + "_paper", track: "paper", side: "long",
      symbol: coin(t.pair), entry_time: iso(t.fill_time), entry_price: num(t.entry),
      exit_time: iso(t.exit_time), exit_price: num(t.exit), net_pct: num(t.ret_pct), pnl_usdt: num(t.pnl_usdt),
      unit: "%", status: t.exit_time ? "closed" : "open", reason: "", note: "",
    }));
  }

  function paperYeni(state, sid) {
    return ((state && state.trades) || []).filter((t) => t.why !== "skipped").map((t, i) => ({
      id: sid + i, strategy: sid, track: "paper", side: "short", symbol: coin(t.symbol || t.pair),
      entry_time: iso(t.entry_day), entry_price: num(t.entry), exit_time: t.why === "open" ? null : iso(t.exit_day),
      exit_price: num(t.exit), net_pct: num(t.ret_pct), pnl_usdt: num(t.pnl_usdt), unit: "%",
      status: t.why === "open" ? "open" : "closed", reason: t.why || "", note: t.note || "",
    }));
  }

  function paperAslan(state) {
    const out = ((state && state.trades) || []).map((t, i) => ({
      id: "an" + i, strategy: "aslan_nas", track: "paper", side: t.side, symbol: "NASDAQ",
      entry_time: iso(t.t_in), entry_price: num(t.entry), exit_time: iso(t.t_out), exit_price: num(t.exit),
      net_pct: num(t.net_r), pnl_usdt: num(t.net_r) * BASE / 100, unit: "R", status: "closed", reason: t.why || "", note: "",
    }));
    const o = state && state.open;
    if (o && o.status === "pozisyon") {
      out.push({ id: "an-open", strategy: "aslan_nas", track: "paper", side: o.side, symbol: "NASDAQ",
        entry_time: iso(o.sig_t), entry_price: num(o.entry), exit_time: null, exit_price: null, net_pct: null,
        pnl_usdt: null, unit: "R", status: "open", reason: "", note: `stop ${o.stop}, hedef ${o.target}` });
    }
    return out;
  }

  function pusulaPaper() {
    return PUSULA_PAPER.map((t, i) => ({
      id: "pp" + i, strategy: "pusula_paper", track: "paper", side: "long", symbol: t.symbol,
      entry_time: t.entry_time, entry_price: t.entry_price, exit_time: t.exit_time, exit_price: null,
      net_pct: t.r, pnl_usdt: t.r * BASE / 100, unit: "R", status: "closed", reason: "stop", note: "",
    }));
  }

  // raw: {name: file text or null}
  function build(raw) {
    const checks = parseCsv(raw.realCheck);
    const fd = demoFitil(parseJson(raw.fitilDemo), checks);
    const dd = demoGeneric(parseJson(raw.dalgaDemo), "dalga_demo");
    const pd = demoGeneric(parseJson(raw.pusulaDemo), "pusula_demo");
    const aslan = parseJson(raw.aslanNas);
    const trades = [
      ...fd.trades, ...dd.trades, ...pd.trades,
      ...paperFitil(parseJson(raw.paperFitil)), ...pusulaPaper(),
      ...paperYeni(parseJson(raw.yeniCoin), "yeni_coin"), ...paperYeni(parseJson(raw.yeniCoinHedge), "yeni_coin_hedge"),
      ...paperAslan(aslan),
    ].sort((a, b) => String(a.entry_time).localeCompare(String(b.entry_time)));
    const pending = [...fd.pending, ...dd.pending, ...pd.pending];
    if (aslan && aslan.open && aslan.open.status !== "pozisyon") {
      pending.push({ strategy: "aslan_nas", symbol: "NASDAQ", price: aslan.open.entry, hour: aslan.open.sig_t });
    }
    return { trades, pending, strategies: STRATEGIES.map((s) => ({ ...s, stats: stats(trades.filter((t) => t.strategy === s.id)) })) };
  }

  // realized equity curve, win rate and max drawdown from closed trades; real=true uses real-price demo results
  function stats(list, real = false) {
    const closed = list.filter((t) => t.status === "closed").sort((a, b) => String(a.exit_time).localeCompare(String(b.exit_time)));
    let eq = BASE, peak = BASE, maxDd = 0, wins = 0, counted = 0;
    const curve = [];
    for (const t of closed) {
      let pnl = t.pnl_usdt, ret = t.net_pct;
      if (real && t.track === "demo") {
        if (!t.real || t.real.state === "pending") continue;
        if (t.real.state === "no") continue; // would not exist on real prices
        pnl = t.real.pnl; ret = t.real.ret;
      }
      if (pnl === null || pnl === undefined) continue;
      eq += pnl; counted++;
      if (ret > 0) wins++;
      peak = Math.max(peak, eq);
      maxDd = Math.max(maxDd, (peak - eq) / peak);
      curve.push({ t: t.exit_time, eq });
    }
    return {
      closed: closed.length, counted, open: list.filter((t) => t.status === "open").length,
      wins, winRate: counted ? wins / counted : null, pnl: eq - BASE, pnlPct: ((eq - BASE) / BASE) * 100,
      maxDd: maxDd * 100, curve,
    };
  }

  const api = { BASE, OUTAGE, FILES, STRATEGIES, build, stats, parseCsv, parseJson };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.AsgoPanel = api;
})(typeof window !== "undefined" ? window : globalThis);
