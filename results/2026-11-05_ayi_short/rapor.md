# Ayı Short ailesi — düşüş piyasası için coin short araştırması (2026-11-05)

## GUO'ya not
- Düşen piyasada coin short'layan 8 yeni kural denedik; **hiçbiri geçmedi**.
- Kurallar testten önce yazılıp kaydedildi; sonradan ayar oynamadık.
- Silinen coinler dahil 680 coinle test ettik; yani sonuç gerçekçi.
- Bulgu: düşüşte "rastgele short" bile kazanıyor; bizim tetiklerimiz bunu belirgin şekilde geçemedi ya da masrafı karşılamadı.
- Kasa (son 6 ay) kullanılmadı.

## Kurulum
- Veri: Binance USDT vadeli, silinenler dahil 680 coin günlük + funding; evrene bir gün bile giren 260 coinin 1 saatlik mumları.
- Evren U: ≥180 gün geçmiş, 30 günlük hacimde ilk 50. Ayı rejimi: BTC < EMA50 ve EMA50 düşüyor.
- Masraf: %0.20 gidiş-dönüş + stop kayması (günlük %0.30, saatlik %0.10) + gerçek funding. 2x masraf: %0.40.
- Geçme şartı: ana kural iki dönemde artı (≥30 işlem), rastgele giriş kontrolünün %95'ini geçer, 2x masrafta artı.
- Ön kayıt: `cards/ayi_short.md` (commit d434d10 ve 22d7a70, testlerden önce).

## Sonuçlar (ana kurallar)
| Kural | Dev 2020-24 | Val 2025-01..2026-03 | 2x masraf | Rastgele kontrol |
|---|---|---|---|---|
| H1 Kırılım Short (20g dip, 10g çıkış) | −0.037R (353) | +0.007R (127) | eksi | geçmedi |
| H2 BTC Kırılım Sepeti | −0.193R | −0.194R | eksi | geçmedi |
| H3 Zombi Coin | −0.157R | +0.021R | dev eksi | geçmedi |
| H4 Funding Tuzağı | −0.015R (53) | +0.42R (3) | — | geçmedi |
| H5 Hacimli Çöküş Devamı | −0.119R (35) | +0.118R (11) | — | geçmedi |
| H6 Gün Dibi Kırılımı (1s) | −0.084R (3568) | +0.009R (1534) | eksi | **geçti** (p<0.01) ama net eksi |
| H7 Saat Penceresi (1s) | −%0.02/pencere | −%0.17 | eksi | geçmedi |
| H8 BTC Şoku Gecikmesi (1s) | −0.174R | −0.130R | eksi | rastgeleden kötü |

Komşu ızgaralar ve yıllık kırılım: `research/bear_short/out_grid.csv`, `out_yearly.csv`, `out_1h_grid.csv`; kontroller `out_controls.csv`, `out_1h_controls.csv`.

## Al-tut kıyası
BTC short-tut: dev −%1214 (BTC 13 kat arttı), val +%27.8. Ayı rejimi günleri: dev %38, val %55.

## Sonradan görülen ipuçları (KABUL EDİLMEDİ, sadece not)
- H4 komşusu (funding eşiği %0.03, 7 gün): dev +0.12R (267 işlem), val +0.27R ama sadece 25 işlem.
- H1 uzun çıkışlı komşular (X20) doğrulamada artı (+0.15..0.30R) ama geliştirmede eksi.
- H6 tetiği rastgeleden ~0.1R iyi ama brüt kazanç masrafın dörtte biri.

## Ders
Silinen coinler dahil evrende, düşüş piyasasında short kazancı neredeyse tamamen rejimden geliyor; fiyat tetikleri (kırılım, şok, hacim, saat) masraf sonrası ek değer üretmiyor. Daha önceki 16+ kısa vadeli fikirle aynı sonuç.
