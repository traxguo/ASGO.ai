# Binance announcement titles (delisting, monitoring tag, futures delisting) for the event-driven short research.
# Runs on a GitHub runner (binance.com is blocked in the research container). Prints one line per article:
#   ANN|<catalogId>|<release ms>|<code>|<title>
# Catalogs: 161 = Delisting, 49 = Latest Binance News, 48 = New Cryptocurrency Listing, 51 = API updates (unused).
import json, sys, time, urllib.request

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


for cat in [int(x) for x in (sys.argv[1:] or ["161", "49", "48"])]:
    n = 0
    for page in range(1, 400):
        r = get(PATH.format(c=cat, p=page))
        cats = ((r or {}).get("data") or {}).get("catalogs") or []
        arts = cats[0].get("articles", []) if cats else []
        if not arts:
            break
        for a in arts:
            t = (a.get("title") or "").replace("|", "/").replace("\n", " ")
            print(f"ANN|{cat}|{a.get('releaseDate')}|{a.get('code')}|{t}", flush=True)
            n += 1
        time.sleep(0.3)
    print(f"DONE catalog {cat}: {n} articles", flush=True)
