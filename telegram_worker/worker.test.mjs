// Run: node --test telegram_worker/
import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { answer, bitgetRequest, symbolOf, HELP } from "./worker.js";

const env = {
  BITGET_DEMO_API_KEY: "k", BITGET_DEMO_API_SECRET: "s", BITGET_DEMO_API_PASSPHRASE: "p",
  TELEGRAM_CHAT_ID: "42", TELEGRAM_GROUP_ID: "-100", WEBHOOK_SECRET: "w",
};

function fakeFetch(routes, calls = []) {
  return async (url, opts = {}) => {
    calls.push({ url, opts });
    const path = new URL(url).pathname;
    const data = routes[path];
    return { json: async () => (data instanceof Error ? { code: "40001", msg: data.message } : { code: "00000", data }) };
  };
}

test("every signed request carries the demo header and a valid signature", async () => {
  const calls = [];
  await bitgetRequest(env, "GET", "/api/v2/mix/account/accounts", { productType: "USDT-FUTURES" }, null,
    fakeFetch({ "/api/v2/mix/account/accounts": [] }, calls));
  const h = calls[0].opts.headers;
  assert.equal(h.paptrading, "1");
  assert.equal(h["ACCESS-KEY"], "k");
  const { createHmac } = await import("node:crypto");
  const expected = createHmac("sha256", "s")
    .update(h["ACCESS-TIMESTAMP"] + "GET/api/v2/mix/account/accounts?productType=USDT-FUTURES").digest("base64");
  assert.equal(h["ACCESS-SIGN"], expected);
});

test("strangers get no answer", async () => {
  assert.equal(await answer(env, 7, "/durum", fakeFetch({})), null);
});

test("status lists balance and open positions", async () => {
  const f = fakeFetch({
    "/api/v2/mix/account/accounts": [{ marginCoin: "USDT", accountEquity: "9999.5", available: "9950", unrealizedPL: "-0.5" }],
    "/api/v2/mix/position/all-position": [{ symbol: "NEARUSDT", holdSide: "long", total: "9", openPriceAvg: "5.471",
      markPrice: "5.46", unrealizedPL: "-0.1" }],
  });
  const text = await answer(env, 42, "/durum", f);
  assert.match(text, /9\.999,50 USDT/);
  assert.match(text, /NEAR long: 9 adet, giriş 5\.471/);
});

test("close only from the owner chat and only when a position exists", async () => {
  const calls = [];
  const f = fakeFetch({ "/api/v2/mix/position/all-position": [{ symbol: "NEARUSDT" }],
    "/api/v2/mix/order/close-positions": {} }, calls);
  assert.match(await answer(env, -100, "/kapat near", f), /sadece sahibin/);
  assert.match(await answer(env, 42, "/kapat btc", f), /açık demo işlemi yok/);
  assert.match(await answer(env, 42, "/kapat near", f), /kapatıldı/);
  const post = calls.find((c) => c.url.endsWith("/close-positions"));
  assert.deepEqual(JSON.parse(post.opts.body), { symbol: "NEARUSDT", productType: "USDT-FUTURES" });
  assert.equal(post.opts.headers.paptrading, "1");
});

test("errors are reported, not thrown", async () => {
  const f = fakeFetch({ "/api/v2/mix/position/history-position": new Error("bad key") });
  assert.match(await answer(env, 42, "/gecmis", f), /Bir sorun oldu: Bitget 40001: bad key/);
});

test("help, symbol names and the group stays quiet on unknown text", async () => {
  assert.equal(await answer(env, 42, "/yardim@asgo_bot", fakeFetch({})), HELP);
  assert.equal(symbolOf("near"), "NEARUSDT");
  assert.equal(symbolOf("BTCUSDT"), "BTCUSDT");
  assert.equal(await answer(env, -100, "selam", fakeFetch({})), null);
});

test("webhook refuses calls without Telegram's secret token", async () => {
  const req = new Request("https://x", { method: "POST", body: "{}", headers: { "X-Telegram-Bot-Api-Secret-Token": "no" } });
  assert.equal((await worker.fetch(req, env)).status, 403);
});
