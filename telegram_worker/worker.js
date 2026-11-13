// Telegram commands for the Bitget DEMO account (play money), running on Cloudflare Workers.
// Telegram calls this worker (webhook) for every message; the worker checks the sender, answers
// help itself and hands account questions to a GitHub job (see "GitHub hand-off" below).
// Secrets live in Cloudflare (set by .github/workflows/telegram_worker.yml), never in the repo.
// Owner guide (Turkish): docs/telegram_cloudflare_kurulum.md

export const HELP = [
  "ASGO botu. Nasdaq (US100) kâğıt takibi: gerçek para yok.",
  "",
  "/durum: Nasdaq botunun açık işlemleri ve toplam sonucu",
  "/gecmis: Nasdaq botunun son kapanan işlemleri",
  "/grafik: Nasdaq grafiği (long/short, giriş, stop, hedef)",
  "/panel: canlı sonuç paneli (tüm işlemler, kazanma oranı, açık işlemler)",
  "/fiyat BTC: güncel fiyat",
  "/yorum ETH: canlı veriyle piyasa yorumu (sinyal değildir)",
  "/kapat NEAR: o coindeki demo işlemini hemen kapat",
  "/sor ...: yapay zekâya serbest soru (sohbet; sinyal veya seviye vermez)",
  "/yardim: bu mesaj",
  "",
  "Not: seviyeler sadece test edilmiş kuraldan gelir; bot kendi kafasına göre seviye söylemez.",
].join("\n");

// ------------------------------------------------------------------ GitHub hand-off
// Bitget blocks requests from Cloudflare's servers, so the worker only checks who is asking and
// starts .github/workflows/telegram_command.yml; that job asks Bitget (demo header always on)
// from a GitHub runner and sends the answer to Telegram itself.

const REPO = "traxguo/ASGO.ai";
const WORKFLOW = "telegram_command.yml";
const REMOTE = new Set(["/fiyat", "/yorum", "/kapat", "/sor"]);

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
      inputs: { cmd, arg: (arg || "").slice(0, cmd === "/sor" ? 400 : 30), chat: String(chatId), sender: String(fromId) } }),
  });
  if (res.status !== 204) return `Bir sorun oldu: GitHub ${res.status} ${(await res.text()).slice(0, 150)}`;
  return "⏳ Bakıyorum, cevap yaklaşık 30 saniye içinde gelecek.";
}

export async function answer(env, chatId, text, fetchFn = fetch, fromId = chatId, chatType = "private") {
  const ownerChat = String(chatId) === String(env.TELEGRAM_CHAT_ID);
  const ownerSpeaking = String(fromId) === String(env.TELEGRAM_CHAT_ID);
  const group = env.TELEGRAM_GROUP_ID && String(chatId) === String(env.TELEGRAM_GROUP_ID);
  const [cmdRaw, firstWord] = (text || "").trim().split(/\s+/);
  const cmd = (cmdRaw || "").toLowerCase().split("@")[0];
  // /sor takes the whole question; the other commands take one word
  const arg = cmd === "/sor" ? (text || "").trim().slice((cmdRaw || "").length).trim() : firstWord;
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
  if (cmd === "/panel") return env.PANEL_URL ? `Canlı sonuç paneli: ${env.PANEL_URL}` : "Panel adresi henüz yok.";
  if (cmd === "/grafik") return env.PANEL_URL ? `Nasdaq grafiği (giriş, stop, hedef): ${env.PANEL_URL}/nasdaq` : "Grafik adresi henüz yok.";
  if (cmd === "/durum" || cmd === "/gecmis") {
    try {
      const data = await loadNasdaq(fetchFn);
      return cmd === "/durum" ? nasdaqStatus(data, env.PANEL_URL) : nasdaqHistory(data);
    } catch (e) {
      return `Nasdaq kaydı okunamadı: ${String(e.message || e).slice(0, 150)}`;
    }
  }
  if (cmd === "/kapat" && !ownerSpeaking) return "İşlem kapatmayı sadece hesap sahibi yapabilir.";
  if (cmd === "/fiyat" && !arg) return "Hangi coin? Örnek: /fiyat BTC";
  if (cmd === "/yorum" && !arg) return "Hangi coin? Örnek: /yorum ETH";
  if (cmd === "/kapat" && !arg) return "Hangi coin? Örnek: /kapat NEAR";
  if (cmd === "/sor" && !arg) return "Ne sormak istersin? Örnek: /sor merhaba";
  if (REMOTE.has(cmd)) {
    try {
      return await startCommand(env, cmd, arg, chatId, fromId, fetchFn);
    } catch (e) {
      return `Bir sorun oldu: ${String(e.message || e).slice(0, 200)}`;
    }
  }
  return ownerChat ? "Bu komutu tanımıyorum. /yardim yaz." : null;
}

// ------------------------------------------------------------------ Nasdaq paper status
// 2026-11-13: the project trades only Nasdaq on paper (docs/decisions.md 2026-11-10) and the Bitget demo
// account is empty, so /durum and /gecmis read the Aslan Nasdaq paper logs (forward/paper_aslan_nas*)
// from the repo's main branch. Read-only. Levels are shown as US100 (cash): futures price minus basis.json.

const FWD = "https://raw.githubusercontent.com/traxguo/asgo.ai/main/forward/";
export const NAS_LINES = [["paper_aslan_nas", "Ana bot"], ["paper_aslan_nas_nobias", "Gevşek 1"], ["paper_aslan_nas_maxopen2", "Gevşek 2"]];

export async function loadNasdaq(fetchFn = fetch) {
  const get = async (path) => {
    const res = await fetchFn(FWD + path, { cf: { cacheTtl: 60 } });
    if (!res.ok) throw new Error(`${path} ${res.status}`);
    return res.json();
  };
  const lines = [];
  for (const [dir, name] of NAS_LINES) lines.push({ name, state: await get(`${dir}/state.json`) });
  let basis = null;
  try { basis = (await get("paper_aslan_nas/basis.json")).basis; } catch (e) { basis = null; }
  return { lines, basis: Number.isFinite(basis) ? basis : null };
}

const px = (v, basis) => Math.round(v - (basis || 0)).toLocaleString("tr-TR");
const trTime = (iso) => new Date(new Date(iso).getTime() + 3 * 3600e3).toISOString().slice(5, 16).replace("T", " ");
const openList = (state) => (Array.isArray(state.open) ? state.open : state.open ? [state.open] : []);
const sumR = (trades) => trades.reduce((a, t) => a + (t.net_r || 0), 0);
const fmtR = (r) => `${r >= 0 ? "+" : ""}${r.toFixed(2)}R`;

export function nasdaqStatus(data, panelUrl) {
  const unit = data.basis === null ? "vadeli fiyat" : "US100, yaklaşık";
  const out = ["Nasdaq botu (kâğıt takip, gerçek para yok)", ""];
  for (const { name, state } of data.lines) {
    const trades = state.trades || [];
    out.push(`${name}: ${trades.length} kapanan işlem, toplam ${fmtR(sumR(trades))}`);
    const open = openList(state);
    if (!open.length) out.push("  Açık işlem yok.");
    for (const o of open) {
      const kind = o.status === "pozisyon" ? "AÇIK" : "BEKLEYEN EMİR";
      out.push(`  ${kind} ${o.side === "long" ? "LONG" : "SHORT"}: giriş ${px(o.entry, data.basis)}, stop ${px(o.stop, data.basis)}, hedef ${px(o.target, data.basis)}`);
    }
  }
  out.push("", `Fiyatlar: ${unit}. Son bakılan mum: ${trTime(data.lines[0].state.last_bar)} (TR).`);
  out.push("Ana bot asıl kuraldır; Gevşek 1 ve 2 sadece karşılaştırma içindir.");
  if (panelUrl) out.push(`Grafik: ${panelUrl}/nasdaq`);
  return out.join("\n");
}

export function nasdaqHistory(data) {
  const out = ["Nasdaq botu: son kapanan işlemler (kâğıt takip)", ""];
  for (const { name, state } of data.lines) {
    const trades = (state.trades || []).slice(-5);
    out.push(`${name}:`);
    if (!trades.length) out.push("  Henüz kapanan işlem yok.");
    for (const t of trades) {
      out.push(`  ${trTime(t.t_in)} ${t.side === "long" ? "LONG" : "SHORT"} ${px(t.entry, data.basis)} → ${px(t.exit, data.basis)} (${t.why}) ${fmtR(t.net_r || 0)}`);
    }
  }
  out.push("", data.basis === null ? "Fiyatlar: vadeli fiyat. Saatler Türkiye saati." : "Fiyatlar: US100, yaklaşık. Saatler Türkiye saati.");
  return out.join("\n");
}

// ------------------------------------------------------------------ demo bot clock
// GitHub's own cron drops or delays many runs (2026-10-11: the hourly Dalga job did not start for
// 3 hours, the 15-minute Kivilcim job never). Cloudflare's cron is punctual, so every 15 minutes
// the worker starts the demo jobs that are due (owner approved 2026-10-12); GitHub's schedules stay
// as a backup and the jobs' concurrency groups keep runs from overlapping.

// 2026-11-10: the Bitget demo bots were stopped (docs/decisions.md). The clock now starts only the paper
// trackers that need a punctual hourly run: Fitil paper tracking (its workflow also winds the demo account
// down) and the Aslan Nasdaq paper tracker.

export function dueBots(when) {
  if (when.getUTCMinutes() >= 15) return [];            // first tick after each closed hour
  return ["bitget_demo_fitil.yml", "paper_aslan_nas.yml"];
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

// ------------------------------------------------------------------ live results page
// GET /panel serves dashboard/canli/panel.html from the repo's main branch; the page then reads the bots'
// log files from GitHub in the browser. Read-only: nothing here can place or close a trade.

const RAW = "https://raw.githubusercontent.com/traxguo/asgo.ai/main/dashboard/canli/";
const PANEL_FILES = { "": ["panel.html", "text/html; charset=utf-8"], "normalize.js": ["normalize.js", "text/javascript; charset=utf-8"],
  "nasdaq": ["nasdaq.html", "text/html; charset=utf-8"] };  // /panel/nasdaq: Nasdaq chart with entry, stop and target

export async function servePanel(path, fetchFn = fetch) {
  const sub = path.replace(/^\/panel\/?/, "");
  const file = PANEL_FILES[sub];
  if (!file) return new Response("not found", { status: 404 });
  const res = await fetchFn(RAW + file[0], { cf: { cacheTtl: 60 } });
  if (!res.ok) return new Response(`panel not available (${res.status})`, { status: 502 });
  let body = await res.text();
  if (sub === "nasdaq") body = "<!doctype html>\n" + body;
  if (sub === "") body = "<!doctype html>\n" + body.replace('<script src="normalize.js">', '<script src="/panel/normalize.js">');
  return new Response(body, { headers: { "Content-Type": file[1], "Cache-Control": "max-age=60" } });
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(startBots(env, new Date(event.scheduledTime)));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && (url.pathname === "/panel" || url.pathname.startsWith("/panel/"))) {
      return servePanel(url.pathname);
    }
    if (request.method !== "POST") return new Response("ok");
    if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET) {
      return new Response("forbidden", { status: 403 });
    }
    const update = await request.json();
    const msg = update.message;
    if (!msg?.text) return new Response("ok");
    const reply = await answer({ ...env, PANEL_URL: `${url.origin}/panel` }, msg.chat.id, msg.text, fetch, msg.from?.id, msg.chat.type);
    if (!reply) return new Response("ok");
    // answering inside the webhook response saves a separate call to Telegram
    return new Response(JSON.stringify({ method: "sendMessage", chat_id: msg.chat.id, text: reply }),
      { headers: { "Content-Type": "application/json" } });
  },
};
