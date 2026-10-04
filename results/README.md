# Test sonuçları

Her test kendi klasörünü alır: `YYYY-MM-DD_<strateji>_<test>/rapor.md` (+ grafikler).

Raporlar `scripts/make_report.py` ile üretilir ve şunları içerir: 3 cümlelik özet, ayarlar, strateji vs al-tut metrikleri, long/short ayrımı, stop/BE/TP oranları, funding, coin bazında sonuç, grafikler, yorum ve karar (devam / düzelt / emekli).

Kötü sonuçlar da burada kalır, silinmez. Henüz gerçek veriyle yapılmış test yok (bkz. `docs/decisions.md`). Rapor formatının örneği (sentetik veriyle): [`tests/smoke/ornek_rapor_SENTETIK/rapor.md`](../tests/smoke/ornek_rapor_SENTETIK/rapor.md).
