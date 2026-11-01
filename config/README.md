# Ayarlar

- `base.json` — Freqtrade ana ayarları. **`dry_run: true` her zaman** (güvenlik kontrolü bunu denetler). Futures, izole marjin, başlangıç sermayesi 10.000 USDT, emir başına %0.1 maliyet. API key alanları boş kalır.
- `pairs_level1.json` — Seviye 1 sabit coin listesi (seçim gerekçesi `docs/decisions.md`).
- `pairs_level2/` — Seviye 2'de dönemsel (tarihli) coin listeleri buraya gelecek.
- `entry_market.json` — piyasa emriyle giren stratejiler için ek ayar (Freqtrade, piyasa giriş emrinde `entry_pricing.price_side = "other"` istiyor). Backtest sonucunu değiştirmez (backtest fiyatı mumdan alır). İlk kullanım: `PusulaV2NoBeMarketEntry` (kuyruk 23, 2026-11-01).
