"""One-off check: which of our 81 coins does the OKX demo (x-simulated-trading) list as USDT perpetuals?"""
import json
import urllib.request
from pathlib import Path

ours = [p.split("/")[0] for p in json.loads((Path(__file__).resolve().parents[1] / "config" / "pairs_wide81.json")
        .read_text())["exchange"]["pair_whitelist"]]
demo15 = [p.split("/")[0] for p in json.loads((Path(__file__).resolve().parents[1] / "config" / "pairs_demo15.json")
          .read_text())["exchange"]["pair_whitelist"]]
for label, headers in (("demo", {"x-simulated-trading": "1"}), ("live", {})):
    req = urllib.request.Request("https://www.okx.com/api/v5/public/instruments?instType=SWAP", headers=headers)
    data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
    ids = {d["instId"] for d in data.get("data", []) if d.get("settleCcy") == "USDT" and d.get("state") == "live"}
    have = [c for c in ours if f"{c}-USDT-SWAP" in ids]
    print(f"OKX {label}: code {data.get('code')} {len(ids)} USDT perps; of our {len(ours)} coins listed: {len(have)}")
    print("  missing:", " ".join(c for c in ours if c not in have))
print("bitget demo list in repo:", len(demo15))
