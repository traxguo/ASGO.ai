// Run: node --test telegram_worker/
import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { answer, HELP, dueBots, startBots, servePanel, nasdaqStatus, nasdaqHistory } from "./worker.js";

const env = { TELEGRAM_CHAT_ID: "42", TELEGRAM_GROUP_ID: "-100", WEBHOOK_SECRET: "w", GH_DISPATCH_TOKEN: "t" };

function fakeGitHub(calls = [], status = 204) {
  return async (url, opts = {}) => {
    calls.push({ url, opts });
    return { status, text: async () => (status === 204 ? "" : "Bad credentials") };
  };
}

test("account commands start the GitHub job with who asked and where", async () => {
  const calls = [];
  assert.match(await answer(env, 42, "/fiyat btc", fakeGitHub(calls)), /Bakıyorum/);
  assert.equal(calls[0].url, "https://api.github.com/repos/traxguo/ASGO.ai/actions/workflows/telegram_command.yml/dispatches");
  assert.equal(calls[0].opts.headers.Authorization, "Bearer t");
  assert.deepEqual(JSON.parse(calls[0].opts.body),
    { ref: "main", inputs: { cmd: "/fiyat", arg: "btc", chat: "42", sender: "42" } });
});

test("strangers learn only their own id in private and nothing in groups", async () => {
  const calls = [];
  assert.equal(await answer(env, 7, "/durum", fakeGitHub(calls)), "Bu bot özel. Senin numaran: 7");
  assert.equal(await answer(env, -7, "/durum", fakeGitHub(calls), 7, "supergroup"), null);
  assert.equal(calls.length, 0);
});

test("only the owner can close, also in the group", async () => {
  const calls = [];
  assert.match(await answer(env, -100, "/kapat near", fakeGitHub(calls), 7, "group"), /sadece hesap sahibi/);
  assert.equal(calls.length, 0);
  await answer(env, -100, "/kapat near", fakeGitHub(calls), 42, "group");
  assert.deepEqual(JSON.parse(calls[0].opts.body).inputs, { cmd: "/kapat", arg: "near", chat: "-100", sender: "42" });
});

test("owner can ask an unknown group for its id; others cannot", async () => {
  assert.match(await answer(env, -555, "/grupid", fakeGitHub(), 42, "group"), /-555/);
  assert.equal(await answer(env, -555, "/grupid", fakeGitHub(), 7, "group"), null);
  assert.equal(await answer(env, -555, "/durum", fakeGitHub(), 42, "group"), null);
});

test("problems are reported, not thrown", async () => {
  assert.match(await answer(env, 42, "/fiyat btc", fakeGitHub([], 401)), /Bir sorun oldu: GitHub 401 Bad credentials/);
  assert.match(await answer({ ...env, GH_DISPATCH_TOKEN: "none" }, 42, "/fiyat btc", fakeGitHub()), /GH_DISPATCH_TOKEN/);
  const down = async () => ({ ok: false, status: 404 });
  assert.match(await answer(env, 42, "/durum", down), /Nasdaq kaydı okunamadı/);
});

test("help, missing coin and the group stays quiet on unknown text", async () => {
  assert.equal(await answer(env, 42, "/yardim@asgo_bot", fakeGitHub()), HELP);
  assert.match(await answer(env, 42, "/fiyat", fakeGitHub()), /Hangi coin/);
  assert.equal(await answer(env, -100, "selam", fakeGitHub(), 7, "group"), null);
});

test("webhook refuses calls without Telegram's secret token", async () => {
  const req = new Request("https://x", { method: "POST", body: "{}", headers: { "X-Telegram-Bot-Api-Secret-Token": "no" } });
  assert.equal((await worker.fetch(req, env)).status, 403);
});

test("the clock starts the demo jobs that are due", async () => {
  assert.deepEqual(dueBots(new Date("2026-10-12T04:02:00Z")), ["bitget_demo_fitil.yml", "paper_aslan_nas.yml"]);
  assert.deepEqual(dueBots(new Date("2026-10-12T05:17:00Z")), []);
  const calls = [];
  await startBots(env, new Date("2026-10-12T05:02:00Z"), fakeGitHub(calls));
  assert.equal(calls.length, 2);
  assert.equal(calls[1].url, "https://api.github.com/repos/traxguo/ASGO.ai/actions/workflows/paper_aslan_nas.yml/dispatches");
  assert.deepEqual(JSON.parse(calls[0].opts.body), { ref: "main" });
  assert.deepEqual(await startBots({ ...env, GH_DISPATCH_TOKEN: "none" }, new Date(), fakeGitHub(calls)), []);
});

test("/sor hands the whole question to the GitHub job, also in the group", async () => {
  const calls = [];
  assert.match(await answer(env, -100, "/sor@asgo_bot  bugün piyasa nasıl?", fakeGitHub(calls), 7, "group"), /Bakıyorum/);
  assert.deepEqual(JSON.parse(calls[0].opts.body).inputs,
    { cmd: "/sor", arg: "bugün piyasa nasıl?", chat: "-100", sender: "7" });
  assert.match(await answer(env, -100, "/sor", fakeGitHub(calls), 7, "group"), /Ne sormak/);
  assert.equal(calls.length, 1);
});

test("/panel answers with the live page address, only to the owner chat and group", async () => {
  const e = { ...env, PANEL_URL: "https://w.example/panel" };
  assert.equal(await answer(e, 42, "/panel", fakeGitHub()), "Canlı sonuç paneli: https://w.example/panel");
  assert.equal(await answer(e, -100, "/panel", fakeGitHub(), 7, "supergroup"), "Canlı sonuç paneli: https://w.example/panel");
  assert.equal(await answer(e, 7, "/panel", fakeGitHub()), "Bu bot özel. Senin numaran: 7");
});

test("GET /panel serves the panel page from the repo; other paths stay closed", async () => {
  const asked = [];
  const fake = async (u) => { asked.push(u); return { ok: true, status: 200, text: async () => '<title>x</title><script src="normalize.js"></script>' }; };
  const page = await servePanel("/panel", fake);
  assert.equal(page.headers.get("Content-Type"), "text/html; charset=utf-8");
  const body = await page.text();
  assert.ok(body.startsWith("<!doctype html>"));
  assert.match(body, /src="\/panel\/normalize\.js"/);
  assert.equal(asked[0], "https://raw.githubusercontent.com/traxguo/asgo.ai/main/dashboard/canli/panel.html");
  const js = await servePanel("/panel/normalize.js", fake);
  assert.equal(js.headers.get("Content-Type"), "text/javascript; charset=utf-8");
  assert.equal((await servePanel("/panel/../secrets", fake)).status, 404);
  assert.equal(asked.length, 2);
});

test("a plain GET still answers ok (deploy health check)", async () => {
  const res = await worker.fetch(new Request("https://w.example/"), env);
  assert.equal(await res.text(), "ok");
});

test("the panel's data layer reads the ASGO Portföy headline line", async () => {
  const { createRequire } = await import("node:module");
  const P = createRequire(import.meta.url)("../dashboard/canli/normalize.js");
  assert.equal(P.FILES.portfoy, "forward/paper_portfoy/state.json");
  const state = { name: "ASGO Portföy", base_usdt: 10000, risk_per_trade: 0.0025, equity: 9975, return_pct: -0.25,
    max_dd_pct: 0.25, trades_closed: 1, trades_open: 0, wins: 0, by_strategy: { PusulaV2: { closed: 1, pnl_usdt: -25 } },
    curve: [{ t: "2026-10-01T00:00:00+00:00", eq: 10000 }, { t: "2026-10-07T13:00:00+00:00", eq: 9975 }] };
  const data = P.build({ portfoy: JSON.stringify(state) });
  assert.equal(data.portfolio.equity, 9975);
  assert.equal(data.portfolio.risk, 0.0025);
  assert.deepEqual(data.portfolio.curve, [{ t: "2026-10-07T13:00:00.000Z", eq: 9975 }]);
  assert.equal(P.build({}).portfolio, null);
});

test("the panel's data layer reads the BTC/ETH Trend paper line", async () => {
  const { createRequire } = await import("node:module");
  const P = createRequire(import.meta.url)("../dashboard/canli/normalize.js");
  assert.equal(P.FILES.trend, "forward/paper_btc_eth_trend/state.json");
  const state = { name: "BTC/ETH Trend", base_usdt: 10000, equity: 10050, return_pct: 0.5, max_dd_pct: 0, days: 1,
    target: { BTC: 0.31, ETH: -0.2 }, target_for: "2026-11-08", source: "bitget",
    curve: [{ t: "2026-11-07T00:00:00+00:00", eq: 10000 }, { t: "2026-11-08T00:00:00+00:00", eq: 10050 }] };
  const data = P.build({ trend: JSON.stringify(state) });
  assert.equal(data.trend.equity, 10050);
  assert.equal(data.trend.target.ETH, -0.2);
  assert.equal(data.trend.curve.length, 2);
  assert.equal(P.build({}).trend, null);
});

test("/grafik gives the Nasdaq chart address and the worker serves that page", async () => {
  const e = { ...env, PANEL_URL: "https://w.example/panel" };
  assert.equal(await answer(e, 42, "/grafik", fakeGitHub()), "Nasdaq grafiği (giriş, stop, hedef): https://w.example/panel/nasdaq");
  const asked = [];
  const fake = async (url) => { asked.push(url); return { ok: true, text: async () => "<html></html>" }; };
  const page = await servePanel("/panel/nasdaq", fake);
  assert.equal(page.status, 200);
  assert.match(await page.text(), /^<!doctype html>/);
  assert.equal(asked[0], "https://raw.githubusercontent.com/traxguo/asgo.ai/main/dashboard/canli/nasdaq.html");
});

// ---- /durum and /gecmis read the Nasdaq paper logs (no GitHub job, no Bitget)
const shortTrade = { side: "short", t_in: "2026-11-11T21:00:00+00:00", entry: 28484.25, stop: 28697, target: 28058.75,
  t_out: "2026-11-12T13:00:00+00:00", exit: 28058.75, net_r: 1.987, why: "hedef" };
const openLong = { status: "pozisyon", side: "long", sig_t: "2026-11-12T14:00:00+00:00", entry: 28359, stop: 28027.31, target: 29022.38 };
const nasFiles = {
  "paper_aslan_nas/state.json": { trades: [shortTrade], open: null, last_bar: "2026-11-13T06:00:00+00:00" },
  "paper_aslan_nas_nobias/state.json": { trades: [shortTrade], open: [openLong], last_bar: "2026-11-13T06:00:00+00:00" },
  "paper_aslan_nas_maxopen2/state.json": { trades: [], open: [], last_bar: "2026-11-13T06:00:00+00:00" },
  "paper_aslan_nas/basis.json": { basis: 99.06 },
};
function fakeRaw(files, calls = []) {
  return async (url) => {
    calls.push(url);
    const key = url.split("/forward/")[1];
    return key in files ? { ok: true, status: 200, json: async () => files[key] } : { ok: false, status: 404 };
  };
}

test("/durum shows the Nasdaq paper lines in US100 prices without starting a GitHub job", async () => {
  const calls = [];
  const text = await answer({ ...env, PANEL_URL: "https://x/panel" }, 42, "/durum", fakeRaw(nasFiles, calls));
  assert.ok(calls.every((u) => u.startsWith("https://raw.githubusercontent.com/traxguo/asgo.ai/main/forward/")));
  assert.match(text, /Ana bot: 1 kapanan işlem, toplam \+1\.99R\n  Açık işlem yok\./);
  assert.match(text, /Gevşek 1: 1 kapanan işlem.*\n  AÇIK LONG: giriş 28\.260, stop 27\.928, hedef 28\.923/);
  assert.match(text, /Gevşek 2: 0 kapanan işlem, toplam \+0\.00R/);
  assert.match(text, /US100, yaklaşık\. Son bakılan mum: 11-13 09:00 \(TR\)/);
  assert.match(text, /https:\/\/x\/panel\/nasdaq/);
});

test("/gecmis lists closed Nasdaq trades; without basis the futures price is shown and said", async () => {
  const text = await answer(env, -100, "/gecmis", fakeRaw(nasFiles), 7, "group");
  assert.match(text, /Ana bot:\n  11-12 00:00 SHORT 28\.385 → 27\.960 \(hedef\) \+1\.99R/);
  assert.match(text, /Gevşek 2:\n  Henüz kapanan işlem yok\./);
  const { ["paper_aslan_nas/basis.json"]: _, ...noBasis } = nasFiles;
  const data = { lines: [{ name: "Ana bot", state: noBasis["paper_aslan_nas_nobias/state.json"] }], basis: null };
  assert.match(nasdaqStatus(data), /giriş 28\.359.*\n\nFiyatlar: vadeli fiyat/);
  assert.match(nasdaqHistory(data), /Fiyatlar: vadeli fiyat/);
});
