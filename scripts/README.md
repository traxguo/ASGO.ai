# Yardımcı komutlar

| Script | Ne yapar |
|---|---|
| `safety_check.py` | `dry_run` her yerde `true` mu, repoda key/token benzeri bir şey var mı kontrol eder; sorun varsa durdurur. |
| `ft.sh` | Freqtrade komutlarını çalıştırır; **her seferinde önce** güvenlik kontrolünü çalıştırır. |
| `download_data.sh` | Seviye 1 coinleri için 1h/4h mumlar + funding + mark price indirir, sonra doğrular. |
| `make_report.py` | Bir backtest sonucundan Türkçe rapor (`results/.../rapor.md`) üretir: R cinsinden, maliyet ve funding dahil, al-tut kıyaslı. |
