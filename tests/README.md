# Testler

Kodun doğru çalıştığını kontrol eder: `python -m pytest -q tests`

- `test_trade_management.py` — İşlem yönetimi kuralları: brief'teki sonuç tablosu (Model B: −1R / +1R / +3R, Model A: −1R / 0R / +4R), TP1 ≥ 1R, likidasyon kuralı, iptal kuralları.
- `test_schema.py` — Sinyal veri yapısı; uydurma seviyeli sinyali reddetmesi.
- `test_safety_check.py` — Güvenlik kontrolünün token'ları yakalaması.
- `test_binance_vision_parse.py` — Yedek veri indiricinin dosya okuma kısmı.

`smoke/` — Binance'e erişilemeyen ortamda **sentetik veriyle** uçtan uca boru hattı testi:
```bash
python tests/smoke/make_synthetic_data.py /tmp/synth/binance
python scripts/offline_freqtrade.py backtesting -c config/base.json -c tests/smoke/pairs_smoke.json \
  --datadir /tmp/synth/binance --strategy-path strategies/candidates \
  --strategy-list TrendMA_A TrendMA_B --timeframe 4h --userdir /tmp/ud
```
`smoke/ornek_rapor_SENTETIK/` bu testin rapor örneğidir; **rakamları anlamsızdır**, sadece rapor formatını gösterir.
