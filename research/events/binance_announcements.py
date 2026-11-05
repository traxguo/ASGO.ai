# Binance announcement titles (delisting, monitoring tag, futures delisting) for the event-driven short research.
# Runs on a GitHub runner (binance.com is blocked in the research container). Writes one row per article to
# research/events/binance_announcements.csv: catalog,release_ms,code,title (the workflow commits it to the PR branch).
# Catalogs: 161 = Delisting, 49 = Latest Binance News, 48 = New Cryptocurrency Listing, 51 = API updates (unused).
import csv, json, re, sys, time, urllib.request

HOSTS = ["https://www.binance.com", "https://www.binance.info", "https://www.binance.me"]
PATH = "/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId={c}&pageNo={p}&pageSize=50"
HDR = {"User-Agent": "Mozilla/5.0 (asgo-research)", "Accept": "application/json", "lang": "en", "clienttype": "web"}


def get(path):
    err = None
    for h in HOSTS:
        for i in range(3):
            try:
                req = urllib.request.Request(h + path, headers=HDR)
                return json.loads(urllib.request.urlopen(req, timeout=30).read())
            except Exception as e:
                err = f"{h}: {e}"
                time.sleep(1 + 2 * i)
    print("ERROR", path, err, flush=True)
    return None


rows = []
for cat in [int(x) for x in (sys.argv[1:] or ["161", "49", "48"])]:
    n = 0
    for page in range(1, 400):
        r = get(PATH.format(c=cat, p=page))
        cats = ((r or {}).get("data") or {}).get("catalogs") or []
        arts = cats[0].get("articles", []) if cats else []
        if not arts:
            break
        for a in arts:
            t = (a.get("title") or "").replace("\n", " ").strip()
            rows.append((cat, a.get("releaseDate"), a.get("code"), t))
            n += 1
        time.sleep(0.3)
    print(f"DONE catalog {cat}: {n} articles", flush=True)

with open("research/events/binance_announcements.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["catalog", "release_ms", "code", "title"]); w.writerows(rows)
print("rows", len(rows))

# Bodies of the event-relevant articles (delisting / monitoring tag), plain text, for coin names and settlement times.
DET = "/bapi/composite/v1/public/cms/article/detail/query?articleCode={code}"


def texts(x, out):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "text" and isinstance(v, str):
                out.append(v)
            else:
                texts(v, out)
    elif isinstance(x, list):
        for v in x:
            texts(v, out)
    return out


rel = [r for r in rows if re.search(r"delist|monitoring tag", r[3], re.I)]
brows = []
for cat, ms, code, title in rel:
    r = get(DET.format(code=code))
    body = ((r or {}).get("data") or {}).get("body") or ""
    try:
        txt = " ".join(texts(json.loads(body), []))
    except Exception:
        txt = re.sub(r"<[^>]+>", " ", body)
    brows.append((code, re.sub(r"\s+", " ", txt)[:20000]))
    time.sleep(0.2)
with open("research/events/binance_announcement_bodies.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["code", "body"]); w.writerows(brows)
print("bodies", len(brows), "non-empty", sum(1 for b in brows if b[1]))
