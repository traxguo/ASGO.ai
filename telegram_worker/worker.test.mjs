// Run: node --test telegram_worker/
import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { answer, HELP, dueBots, startBots } from "./worker.js";

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
