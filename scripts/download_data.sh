#!/usr/bin/env bash
# Level 1 data: OHLCV (1h, 4h) + funding rate + mark price for the Level 1 pairs,
# from the earliest available futures data, then validation.
#   ./scripts/download_data.sh            (Docker)
#   FT_LOCAL=1 ./scripts/download_data.sh (local freqtrade)
set -euo pipefail
cd "$(dirname "$0")/.."

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
