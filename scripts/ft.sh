#!/usr/bin/env bash
# Runs a Freqtrade command, ALWAYS after the safety check.
#   ./scripts/ft.sh backtesting --strategy TrendMA_B
#   FT_LOCAL=1 ./scripts/ft.sh ...   -> use a local freqtrade install instead of Docker
#   FT_OFFLINE=1 (with FT_LOCAL=1)    -> static market list, for when the Binance API is blocked (HTTP 451)
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/safety_check.py

# Strategy folder: candidates by default; use FT_STRATEGY_DIR=strategies/active for active ones.
COMMON=(-c config/base.json -c config/pairs_level1.json --userdir user_data --strategy-path "${FT_STRATEGY_DIR:-strategies/candidates}")
cmd="$1"; shift

case "$cmd" in
  # commands that take strategy/config arguments
  backtesting|lookahead-analysis|recursive-analysis|hyperopt|trade|backtesting-analysis)
    ARGS=("$cmd" "${COMMON[@]}" "$@") ;;
  download-data|list-data|list-pairs|list-markets)
    ARGS=("$cmd" -c config/base.json -c config/pairs_level1.json --userdir user_data "$@") ;;
  *)
    ARGS=("$cmd" "$@") ;;
esac

if [[ "${FT_LOCAL:-0}" == "1" && "${FT_OFFLINE:-0}" == "1" ]]; then
  python3 scripts/offline_freqtrade.py "${ARGS[@]}"
elif [[ "${FT_LOCAL:-0}" == "1" ]]; then
  freqtrade "${ARGS[@]}"
else
  docker compose run --rm freqtrade "${ARGS[@]}"
fi
