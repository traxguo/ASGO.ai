// Telegram commands for the Bitget DEMO account (play money), running on Cloudflare Workers.
// Telegram calls this worker (webhook) for every message; the worker answers in the same request.
// Secrets live in Cloudflare (set by .github/workflows/telegram_worker.yml), never in the repo.
// Owner guide (Turkish): docs/telegram_cloudflare_kurulum.md

const BITGET = "https://api.bitget.com";
const PRODUCT = "USDT-FUTURES";

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

// ------------------------------------------------------------------ Bitget (demo only)

async function hmacBase64(secret, text) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(text));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

export async function bitgetRequest(env, method, path, query = {}, body = null, fetchFn = fetch) {
  const qs = new URLSearchParams(query).toString();
  const requestPath = path + (qs ? `?${qs}` : "");
  const bodyText = body ? JSON.stringify(body) : "";
  const ts = Date.now().toString();
  const headers = {
    "ACCESS-KEY": env.BITGET_DEMO_API_KEY,
    "ACCESS-SIGN": await hmacBase64(env.BITGET_DEMO_API_SECRET, ts + method + requestPath + bodyText),
    "ACCESS-TIMESTAMP": ts,
    "ACCESS-PASSPHRASE": env.BITGET_DEMO_API_PASSPHRASE,
    "Content-Type": "application/json",
    "locale": "en-US",
    "paptrading": "1",  // demo account only; never removed
  };
  if (headers.paptrading !== "1") throw new Error("STOP: request without the demo header");
  const res = await fetchFn(BITGET + requestPath, { method, headers, body: bodyText || undefined });
  const data = await res.json();
  if (data.code !== "00000") throw new Error(`Bitget ${data.code}: ${data.msg}`);
  return data.data;
}

async function publicTicker(symbol, fetchFn = fetch) {
  const res = await fetchFn(`${BITGET}/api/v2/mix/market/ticker?symbol=${symbol}&productType=${PRODUCT}`);
  const data = await res.json();
  if (data.code !== "00000" || !data.data?.length) return null;
  return data.data[0];
}

// ------------------------------------------------------------------ commands

const num = (x, d = 2) => Number(x || 0).toLocaleString("tr-TR", { minimumFractionDigits: d, maximumFractionDigits: d });
const coin = (symbol) => symbol.replace(/USDT$/, "");
export const symbolOf = (word) => (word || "").toUpperCase().replace(/[^A-Z0-9]/g, "").replace(/USDT$/, "") + "USDT";

async function status(env, fetchFn) {
  const accounts = await bitgetRequest(env, "GET", "/api/v2/mix/account/accounts", { productType: PRODUCT }, null, fetchFn);
  const usdt = accounts.find((a) => a.marginCoin === "USDT") || {};
  const positions = await bitgetRequest(env, "GET", "/api/v2/mix/position/all-position",
    { productType: PRODUCT, marginCoin: "USDT" }, null, fetchFn);
  const lines = [
    `Bakiye: ${num(usdt.accountEquity)} USDT (kullanılabilir ${num(usdt.available)})`,
    `Açık kâr/zarar: ${num(usdt.unrealizedPL)} USDT`,
    "",
  ];
  if (!positions.length) lines.push("Açık işlem yok.");
  for (const p of positions) {
    lines.push(`• ${coin(p.symbol)} ${p.holdSide === "long" ? "long" : "short"}: ${p.total} adet, giriş ${p.openPriceAvg}, ` +
      `şimdi ${p.markPrice}, kâr/zarar ${num(p.unrealizedPL)} USDT`);
  }
  return lines.join("\n");
}

async function history(env, fetchFn) {
  const data = await bitgetRequest(env, "GET", "/api/v2/mix/position/history-position",
    { productType: PRODUCT, limit: "10" }, null, fetchFn);
  const list = data?.list || [];
  if (!list.length) return "Henüz kapanmış işlem yok.";
  return ["Son kapanan işlemler:", ...list.map((p) => {
    const day = new Date(Number(p.utime || p.uTime || p.ctime || 0)).toISOString().slice(0, 10);
    return `• ${day} ${coin(p.symbol)} ${p.holdSide}: giriş ${p.openAvgPrice}, çıkış ${p.closeAvgPrice}, ` +
      `net ${num(p.netProfit ?? p.pnl)} USDT`;
  })].join("\n");
}

async function price(word, fetchFn) {
  if (!word) return "Hangi coin? Örnek: /fiyat BTC";
  const t = await publicTicker(symbolOf(word), fetchFn);
  if (!t) return `${word.toUpperCase()} bulunamadı.`;
  const change = Number(t.change24h || 0) * 100;
  return `${coin(t.symbol)}: ${t.lastPr} USDT (24 saat ${change >= 0 ? "+" : ""}${change.toFixed(2)}%). Bilgi amaçlıdır, sinyal değildir.`;
}

async function closePosition(env, word, fetchFn) {
  if (!word) return "Hangi coin? Örnek: /kapat NEAR";
  const symbol = symbolOf(word);
  const positions = await bitgetRequest(env, "GET", "/api/v2/mix/position/all-position",
    { productType: PRODUCT, marginCoin: "USDT" }, null, fetchFn);
  if (!positions.some((p) => p.symbol === symbol)) return `${coin(symbol)} için açık demo işlemi yok.`;
  await bitgetRequest(env, "POST", "/api/v2/mix/order/close-positions", null,
    { symbol, productType: PRODUCT }, fetchFn);
  return `${coin(symbol)} demo işlemi piyasa fiyatından kapatıldı. /durum ile kontrol edebilirsin.`;
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
  try {
    switch (cmd) {
      case "/start": case "/yardim": case "/help": return HELP;
      case "/durum": return await status(env, fetchFn);
      case "/gecmis": return await history(env, fetchFn);
      case "/fiyat": return await price(arg, fetchFn);
      case "/kapat":
        if (!ownerSpeaking) return "İşlem kapatmayı sadece hesap sahibi yapabilir.";
        return await closePosition(env, arg, fetchFn);
      default:
        return ownerChat ? "Bu komutu tanımıyorum. /yardim yaz." : null;
    }
  } catch (e) {
    return `Bir sorun oldu: ${String(e.message || e).slice(0, 200)}`;
  }
}

export default {
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
