// Telegram commands for the Bitget DEMO account (play money), running on Cloudflare Workers.
// Telegram calls this worker (webhook) for every message; the worker checks the sender, answers
// help itself and hands account questions to a GitHub job (see "GitHub hand-off" below).
// Secrets live in Cloudflare (set by .github/workflows/telegram_worker.yml), never in the repo.
// Owner guide (Turkish): docs/telegram_cloudflare_kurulum.md

export const HELP = [
  "ASGO demo botu (Bitget demo hesabı, oyun parası).",
  "",
  "/durum: bakiye ve açık işlemler",
  "/gecmis: son kapanan işlemler",
  "/fiyat BTC: güncel fiyat",
  "/kapat NEAR: o coindeki demo işlemini hemen kapat",
  "/yardim: bu mesaj",
  "",
  "Not: Bot kendi kafasına göre alım/stop seviyesi söylemez; işlemleri sadece Pusula açar.",
].join("\n");

// ------------------------------------------------------------------ GitHub hand-off
// Bitget blocks requests from Cloudflare's servers, so the worker only checks who is asking and
// starts .github/workflows/telegram_command.yml; that job asks Bitget (demo header always on)
// from a GitHub runner and sends the answer to Telegram itself.

const REPO = "traxguo/ASGO.ai";
const WORKFLOW = "telegram_command.yml";
const REMOTE = new Set(["/durum", "/gecmis", "/fiyat", "/kapat"]);

export async function startCommand(env, cmd, arg, chatId, fromId, fetchFn = fetch) {
  if (!env.GH_DISPATCH_TOKEN || env.GH_DISPATCH_TOKEN === "none") return "Kurulum eksik: GH_DISPATCH_TOKEN secret'ı yok (docs/telegram_cloudflare_kurulum.md).";
  const res = await fetchFn(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GH_DISPATCH_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "asgo-telegram",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ref: "main",
      inputs: { cmd, arg: (arg || "").slice(0, 30), chat: String(chatId), sender: String(fromId) } }),
  });
  if (res.status !== 204) return `Bir sorun oldu: GitHub ${res.status} ${(await res.text()).slice(0, 150)}`;
  return "⏳ Bakıyorum, cevap yaklaşık 30 saniye içinde gelecek.";
}

export async function answer(env, chatId, text, fetchFn = fetch, fromId = chatId, chatType = "private") {
  const ownerChat = String(chatId) === String(env.TELEGRAM_CHAT_ID);
  const ownerSpeaking = String(fromId) === String(env.TELEGRAM_CHAT_ID);
  const group = env.TELEGRAM_GROUP_ID && String(chatId) === String(env.TELEGRAM_GROUP_ID);
  const [cmdRaw, arg] = (text || "").trim().split(/\s+/);
  const cmd = (cmdRaw || "").toLowerCase().split("@")[0];
  // the owner can ask any group for its id once, to add it as the TELEGRAM_GROUP_ID secret
  if (cmd === "/grupid" && ownerSpeaking && !ownerChat) {
    return `Bu grubun numarası: ${chatId}\nBunu GitHub Secrets'a TELEGRAM_GROUP_ID adıyla ekle, sonra kurulumu tekrar çalıştır.`;
  }
  if (!ownerChat && !group) {
    // a private chat that is not the owner's: say only the sender's own id, so the owner can
    // spot a wrong TELEGRAM_CHAT_ID secret; nothing about the account is shared; groups stay silent
    return chatType === "private" ? `Bu bot özel. Senin numaran: ${chatId}` : null;
  }
  if (cmd === "/start" || cmd === "/yardim" || cmd === "/help") return HELP;
  if (cmd === "/kapat" && !ownerSpeaking) return "İşlem kapatmayı sadece hesap sahibi yapabilir.";
  if (cmd === "/fiyat" && !arg) return "Hangi coin? Örnek: /fiyat BTC";
  if (cmd === "/kapat" && !arg) return "Hangi coin? Örnek: /kapat NEAR";
  if (REMOTE.has(cmd)) {
    try {
      return await startCommand(env, cmd, arg, chatId, fromId, fetchFn);
    } catch (e) {
      return `Bir sorun oldu: ${String(e.message || e).slice(0, 200)}`;
    }
  }
  return ownerChat ? "Bu komutu tanımıyorum. /yardim yaz." : null;
}

// ------------------------------------------------------------------ demo bot clock
// GitHub's own cron drops or delays many runs (2026-10-11: the hourly Dalga job did not start for
// 3 hours, the 15-minute Kivilcim job never). Cloudflare's cron is punctual, so every 15 minutes
// the worker starts the demo jobs that are due (owner approved 2026-10-12); GitHub's schedules stay
// as a backup and the jobs' concurrency groups keep runs from overlapping.

export function dueBots(when) {
  const minute = when.getUTCMinutes(), hour = when.getUTCHours();
  const due = ["bitget_demo_fitil.yml"];                // Fitil Avcisi: every tick (15 min), limits live one hour
  if (minute < 15) {
    due.push("bitget_demo_dalga.yml");                  // first tick after each 1h candle
    if (hour % 4 === 0) due.push("bitget_demo.yml");    // first tick after each 4h candle (Pusula)
  }
  return due;
}

export async function startBots(env, when, fetchFn = fetch) {
  if (!env.GH_DISPATCH_TOKEN || env.GH_DISPATCH_TOKEN === "none") return [];
  const started = [];
  for (const wf of dueBots(when)) {
    const res = await fetchFn(`https://api.github.com/repos/${REPO}/actions/workflows/${wf}/dispatches`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GH_DISPATCH_TOKEN}`,
        "Accept": "application/vnd.github+json",
        "User-Agent": "asgo-telegram",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: "main" }),
    });
    started.push(`${wf} ${res.status}`);
  }
  console.log(started.join(", "));
  return started;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(startBots(env, new Date(event.scheduledTime)));
  },

  async fetch(request, env) {
    if (request.method !== "POST") return new Response("ok");
    if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET) {
      return new Response("forbidden", { status: 403 });
    }
    const update = await request.json();
    const msg = update.message;
    if (!msg?.text) return new Response("ok");
    const reply = await answer(env, msg.chat.id, msg.text, fetch, msg.from?.id, msg.chat.type);
    if (!reply) return new Response("ok");
    // answering inside the webhook response saves a separate call to Telegram
    return new Response(JSON.stringify({ method: "sendMessage", chat_id: msg.chat.id, text: reply }),
      { headers: { "Content-Type": "application/json" } });
  },
};
