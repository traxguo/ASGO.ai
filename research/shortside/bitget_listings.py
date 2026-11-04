# Bitget USDT-futures listing dates (runs on a GitHub runner; Bitget is blocked in the research container).
# Prints CSV lines "LISTING,<symbol>,<YYYY-MM-DD>,<source>,<status>" for the comparison with Binance listing dates.
import json, time, urllib.request
from datetime import datetime, timezone

BASE = "https://api.bitget.com/api/v2/mix/market/"


def get(path):
    for i in range(5):
        try:
            req = urllib.request.Request(BASE + path, headers={"User-Agent": "asgo-research"})
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            err = e
            time.sleep(1 + 2 * i)
    print("ERROR", path, err)
    return None


def first_candle(sym):
    """Earliest daily candle in 2025-07..now, scanning 90-day windows forward."""
    start = int(datetime(2025, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
    now = int(time.time() * 1000)
    step = 89 * 86400000
    t = start
    while t < now:
        r = get(f"history-candles?symbol={sym}&productType=USDT-FUTURES&granularity=1D&startTime={t}&endTime={min(t + step, now)}&limit=200")
        rows = (r or {}).get("data") or []
        if rows:
            return min(int(x[0]) for x in rows)
        t += step
        time.sleep(0.15)
    return None


r = get("contracts?productType=USDT-FUTURES")
data = (r or {}).get("data") or []
print("contracts", len(data))
if data:
    print("fields", sorted(data[0].keys()))
for c in data:
    sym, st = c.get("symbol"), c.get("symbolStatus")
    lt = c.get("launchTime")
    src = "launchTime"
    try:
        lt = int(lt) if lt not in (None, "", "0") else None
    except ValueError:
        lt = None
    if lt is None:
        lt, src = first_candle(sym), "first_candle"
    d = datetime.fromtimestamp(lt / 1000, timezone.utc).strftime("%Y-%m-%d") if lt else ""
    print(f"LISTING,{sym},{d},{src},{st}", flush=True)
