# 2026-11-09 — Endeks + forex fikir paketi
## Yapılanlar
- 8 bilinen endeks/forex fikri ön kayıtla test edildi (`results/2026-11-09_endeks_forex_batch/README.md`, ön kayıt 01af554, çıta eki 289113a).
- HistData verisi GitHub sunucusunda (`research/endeks_forex/fetch.py`), test `research/endeks_forex/batch.py`, sonuç CSV'leri iş akışıyla repoya commit'lendi.
- Kart `cards/endeks_forex_paketi.md`; karar `docs/decisions.md`.
## Bulgular (rakamlarla)
- 0/15 yön satırı geçti. I3 RSI(2) long: gel. +0.45% PF 1.94 (71), doğ. +0.23% PF 1.35 (34), 2x artı, ama rastgele kontrol p 0.16.
- I5 3 düşüş günü long: gel. +0.25% PF 1.44 (147), doğ. +0.85% PF 6.4 (51), p 0.10.
- Gece kayması long gel. −0.005% (2317 işlem); gün içi short −0.048%. Londra kırılımı iki yönde eksi.
## Başarısız olan / elenen
- Tüm 8 fikir. Short tarafı hiçbir fikirde iki dönemde tutmadı.
- İlk çalıştırma veri hatası verdi (DAX gün eksikliği, +%278 sahte işlem); kurallar değişmeden veri okuma düzeltildi, iki kez yeniden çalıştırıldı.
## Açık sorular
- HistData DAX (grxeur) 2020-06 → 2023-11 arası başka bir endeks (Euro Stoxx 50 seviyesi). Aslan GER40 sonucu yeniden değerlendirilmeli mi?
## Sıradaki adım
- Proje sahibi isterse I3 RSI(2) long için başka bir piyasa rejiminde (ör. 2000-2019 verisi, Yahoo) bağımsız bir test; kasa kullanılmadan.
