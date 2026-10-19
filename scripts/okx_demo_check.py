"""One-off check: which of our 81 coins does the OKX demo (x-simulated-trading) list as USDT perpetuals?"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ours = [p.split("/")[0] for p in json.loads((ROOT / "config" / "pairs_wide81.json").read_text())["exchange"]["pair_whitelist"]]
HOSTS = ("www.okx.com", "my.okx.com", "app.okx.com", "eea.okx.com", "aws.okx.com")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
for host in HOSTS:
    for label, extra in (("demo", {"x-simulated-trading": "1"}), ("live", {})):
        req = urllib.request.Request(f"https://{host}/api/v5/public/instruments?instType=SWAP",
                                     headers={"User-Agent": UA, "Accept": "application/json", **extra})
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        except urllib.error.HTTPError as e:
            print(f"{host} {label}: HTTP {e.code} {e.read()[:200]!r}")
            continue
        except Exception as e:  # noqa: BLE001 - report every host, never stop
            print(f"{host} {label}: {type(e).__name__} {e}")
            continue
        ids = {d["instId"] for d in data.get("data", []) if d.get("settleCcy") == "USDT" and d.get("state") == "live"}
        have = [c for c in ours if f"{c}-USDT-SWAP" in ids]
        print(f"{host} {label}: code {data.get('code')} {len(ids)} USDT perps; of our {len(ours)} coins listed: {len(have)}")
        print("  missing:", " ".join(c for c in ours if c not in have))
