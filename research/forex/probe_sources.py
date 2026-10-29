"""Check which free forex data sources answer from a GitHub runner (one small request each)."""
import subprocess
import time
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
URLS = {
    "dukascopy candles": "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/02/05/BID_candles_min_1.bi5",
    "dukascopy ticks": "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/02/05/10h_ticks.bi5",
    "yahoo 1h": "https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval=1h&range=5d",
    "histdata page": "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/eurusd/2023",
}
for name, url in URLS.items():
    t0 = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30)
        body = r.read()
        print(f"{name}: HTTP {r.status} {len(body)} bytes in {time.time() - t0:.1f}s", flush=True)
    except Exception as e:  # noqa: BLE001 - report every source
        print(f"{name}: {type(e).__name__} {e} after {time.time() - t0:.1f}s", flush=True)
out = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download} %{time_total}s",
                      "--max-time", "40", URLS["dukascopy candles"]], capture_output=True, text=True)
print("curl dukascopy candles:", out.stdout, out.stderr.strip(), flush=True)
try:
    from histdata import download_hist_data as dl
    from histdata.api import Platform as P, TimeFrame as TF
    t0 = time.time()
    f = dl(year="2023", month=None, pair="eurusd", platform=P.GENERIC_ASCII, time_frame=TF.ONE_MINUTE)
    print(f"histdata package: {f} in {time.time() - t0:.1f}s", flush=True)
except Exception as e:  # noqa: BLE001
    print(f"histdata package: {type(e).__name__} {e}", flush=True)
