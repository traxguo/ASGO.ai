# Market-nötr long+short fikirler — 2026-11-04

## GUO'ya not
- Piyasa düşse de çıksa da kazanma fikriyle 6 "hem al hem sat" stratejisi denedik. Hepsi silinen coinler dahil, masraf ve funding ile.
- 5'i elendi: coin çiftleri, ETH/BTC oranı, kısa vadeli geri dönüş, funding toplama, sakin/oynak coin.
- 1 tanesi umut verdi: **"Yeni Coin Short"**: yeni listelenen coini 1 hafta sonra sat, karşılığında aynı tutarda BTC al, en fazla 1 ay tut. 2020-24'te +%109, 2025-26/03'te +%32 (BTC aynı dönemde -%28). Ama kötü dönemde kasa %27'ye kadar geriliyor ve 2026'nın ilk 3 ayı -%15.
- Sıradaki adım: yönetici karar verirse saklanan son 6 ayda (kasa) bir kez test. Gerçek para yok, canlı botlara dokunulmadı.

## Ortak ayarlar
- Evren: Binance USDⓈ-M'de bugüne kadar listelenmiş 680 USDT coin (silinenler dahil). Günlük veri `research/xsec/fetch_all_daily.py`, funding `research/neutral/fetch_funding_daily.py`, yeni coinlerin saatlik verisi `research/neutral/fetch_newlist_1h.py` (hepsi data.binance.vision).
- Her gün: 30 günlük ortalama hacimde ilk 50 coin, ≥180 gün geçmiş (çift / geri dönüş / funding / oynaklık testleri).
- Masraf: gidiş-dönüş %0.20 (her bacak) + funding; 2x masraf (%0.40) kontrolü.
- Geliştirme 2020-01-01..2024-12-31, doğrulama 2025-01-01..2026-03-31. Kasa (2026-04..09) kullanılmadı.
- Al-tut kıyası: BTC geliştirme +%1200 (düşüş %77), doğrulama -%28 (düşüş %50); ETH +%2454 / -%37.
- Kod: `research/neutral/`. Ham çıktılar: `cikti/`.

## Sonuç tablosu (masraf %0.20 + funding)
| Fikir | Ayar sayısı | Geliştirme | Doğrulama | Karar |
|---|---|---|---|---|
| (a) Coin çiftleri (z-skor ±2, 0'da çık, ±4 stop, 20 gün) | 18 | -%41..+%19 | **18/18 eksi** (-%7..-%17) | Elendi |
| (b1) ETH/BTC geri dönüş | 9 | 9/9 eksi | 9/9 eksi | Elendi |
| (b2) ETH/BTC trend | 6 | 2/6 artı | 5/6 artı (farklı ayarlar) | Elendi, tutarsız |
| (c) BTC'den arındırılmış 1-3 gün geri dönüş | 18 | **18/18 eksi** | karışık | Elendi (masraf) |
| (d) Funding carry | 12 | 12/12 artı | K10: 5/6 artı, K5: 1/6 | Elendi (kâr birkaç güne bağlı, doğrulamada fiyat tarafı hep eksi) |
| (f) Sakin coin al / oynak coin sat | 4 | 2/4 artı | 4/4 artı | Elendi (düşüş %50+, tutarsız) |
| **(e) Yeni Coin Short + BTC long (saatlik stop)** | 24 | **24/24 artı** | **18/24 artı** (%30 stoplu 12/12) | **Zayıf aday** |

## (e) Yeni Coin Short — kart kuralı (7 gün bekle, 30 gün tut, %30 stop)
| Dönem | Toplam | Düşüş | 2x masraf | İşlem | İşlem başı | Kazanma |
|---|---|---|---|---|---|---|
| Geliştirme | +%109 | %22 | +%97 | 307 (ayda 5.1) | +%2.71 | %54 |
| Doğrulama | +%32 | %27 | +%26 | 216 (ayda 14.4) | +%1.77 | %51 |

- Long ve short ayrı (bacağın kendi tutarına göre, işlem başı ortalama): geliştirme coin short +%1.71, BTC long +%4.12; doğrulama coin short +%5.70, BTC long -%1.77.
- Yıllar: 2020 +68, 2021 -16, 2022 +6, 2023 +16, 2024 +22, 2025 +55, 2026Q1 -15 (%).
- En kötü aylar: 2026-02 -%12, 2025-08 -%9, 2020-08 -%8, 2023-02 -%8.
- Pozisyon: işlem başına kasanın %5'i short + %5'i BTC long, izole 1x, en fazla 20 açık işlem.

### Simülasyon dersleri (aynı fikir, üç hesap)
| Hesap | Doğrulama (N7 M30 %30) | Not |
|---|---|---|
| Her gün eşit ağırlığa döndürme | +%87 | Gerçekçi değil: squeeze eden short'u her gün küçültüyor, bu işlemlerin masrafı yok |
| Gerçek pozisyon, stop günlük kapanışta | +%23, düşüş %38, 5 likidasyon | COAI 1 günde 6 katı |
| **Gerçek pozisyon, stop saatlik** | **+%32, düşüş %27, 0 likidasyon** | Kart kuralı |

## (d) Funding carry neden elendi
K=10, top 50 coin (LB = funding'e bakılan gün, H = tutma günü):

| Ayar | Gel. net | Doğ. net | Doğ. sadece fiyat (masrafsız) | Doğ. sadece funding | Doğ. 2x masraf | Doğ. en iyi 5 gün hariç |
|---|---|---|---|---|---|---|
| LB7 H1 | +%100 | +%36 | -%25 | +%107 | +%20 | -%16 |
| LB7 H7 | +%115 | +%9 | -%33 | +%72 | +%3 | -%26 |
| LB14 H1 | +%136 | +%11 | -%41 | +%104 | +%2 | -%33 |

En az 365 gün geçmişli coinlerle doğrulama -%6..+%17. Kâr funding'in kendisinden geliyor, fiyat tarafı onu yiyor ve sonuç birkaç sert güne bağlı.

## Karar
- (a), (b), (c), (d), (f): elendi, `cards/market_notr.md`.
- (e) Yeni Coin Short: zayıf aday, `cards/yeni_coin_short.md`. Kasa testi için yönetici/GUO kararı bekleniyor. Kural değiştirilmeden bir kez çalıştırılmalı.
