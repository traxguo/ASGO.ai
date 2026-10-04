#!/usr/bin/env bash
# Level 1 data: OHLCV (1h, 4h) + funding rate + mark price for the Level 1 pairs,
# from the earliest available futures data, then validation.
#   ./scripts/download_data.sh            (Docker)
#   FT_LOCAL=1 ./scripts/download_data.sh (local freqtrade)
#   FT_LOCAL=1 FT_OFFLINE=1 ./scripts/download_data.sh
#       -> Binance API blocked (HTTP 451): monthly archives from data.binance.vision instead
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${FT_LOCAL:-0}" == "1" && "${FT_OFFLINE:-0}" == "1" ]]; then
  python3 scripts/safety_check.py
  python3 research/data/fetch_binance_vision.py \
    --pairs $(python3 -c "import json;print(' '.join(json.load(open('config/pairs_level1.json'))['exchange']['pair_whitelist']))") \
    --timeframes 1h 4h --start 2020-01
  python3 research/data/validate.py
  exit 0
fi

./scripts/ft.sh download-data \
  --trading-mode futures \
  --timeframes 1h 4h \
  --candle-types futures funding_rate mark \
  --timerange 20190901- \
  --data-format-ohlcv feather

if [[ "${FT_LOCAL:-0}" == "1" ]]; then
  python3 research/data/validate.py
else
  docker compose run --rm --entrypoint python3 freqtrade research/data/validate.py
fi
