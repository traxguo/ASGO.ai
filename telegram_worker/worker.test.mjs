// Run: node --test telegram_worker/
import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { answer, HELP, dueBots, startBots, servePanel } from "./worker.js";

const env = { TELEGRAM_CHAT_ID: "42", TELEGRAM_GROUP_ID: "-100", WEBHOOK_SECRET: "w", GH_DISPATCH_TOKEN: "t" };

function fakeGitHub(calls = [], status = 204) {
  return async (url, opts = {}) => {
    calls.push({ url, opts });
    return { status, text: async () => (status === 204 ? "" : "Bad credentials") };
  };
}

test("account commands start the GitHub job with who asked and where", async () => {
  const calls = [];
  assert.match(await answer(env, 42, "/durum", fakeGitHub(calls)), /Bakıyorum/);
  assert.equal(calls[0].url, "https://api.github.com/repos/traxguo/ASGO.ai/actions/workflows/telegram_command.yml/dispatches");
  assert.equal(calls[0].opts.headers.Authorization, "Bearer t");
  assert.deepEqual(JSON.parse(calls[0].opts.body),
    { ref: "main", inputs: { cmd: "/durum", arg: "", chat: "42", sender: "42" } });
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
  assert.match(await answer(env, 42, "/gecmis", fakeGitHub([], 401)), /Bir sorun oldu: GitHub 401 Bad credentials/);
  assert.match(await answer({ ...env, GH_DISPATCH_TOKEN: "none" }, 42, "/durum", fakeGitHub()), /GH_DISPATCH_TOKEN/);
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
  assert.deepEqual(dueBots(new Date("2026-10-12T04:02:00Z")),
    ["bitget_demo_fitil.yml", "bitget_demo_dalga.yml", "bitget_demo.yml"]);
  assert.deepEqual(dueBots(new Date("2026-10-12T05:02:00Z")), ["bitget_demo_fitil.yml", "bitget_demo_dalga.yml"]);
  assert.deepEqual(dueBots(new Date("2026-10-12T05:17:00Z")), ["bitget_demo_fitil.yml"]);
  const calls = [];
  await startBots(env, new Date("2026-10-12T05:02:00Z"), fakeGitHub(calls));
  assert.equal(calls.length, 2);
  assert.equal(calls[1].url, "https://api.github.com/repos/traxguo/ASGO.ai/actions/workflows/bitget_demo_dalga.yml/dispatches");
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
