# Çıkarma turu 2 — günlük puan eşiği +3 → +1 — 2026-10-11 (temel: PusulaV2NoBtcFilter)

## GUO'ya not
- Long girişi için "coinin günlük puanı +3 olmalı" şartını gevşettim: artık +1 de yetiyor (`PusulaV2NoBtcScore1`). Puan sadece -3/-1/+1/+3 olabildiği için "+2" pratikte "+1" demek.
- İki coin grubunda da daha iyi: eski 16'da işlem başına +1.20R → +1.30R, yeni 20'de +0.46R → +0.52R; en büyük düşüş ikisinde de azaldı. İşlem sayısı arttı: 210 → 238 ve 150 → 201.
- Karar: **kabul**. Bir uyarı: kazancın büyük kısmı birkaç coinden geliyor (eski 16'da SOL, yeni 20'de ALGO ve UNI). Coinlerin yarısından fazlası biraz kötüleşti. Kural iyi ama "her yerde daha iyi" değil.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBtcFilter (temel) | 210 | +1.20R | 252.90 | 2.07 | %26.1 | +%560.2 |
| Eski 16 | Puan ≥ +1 | **238** | **+1.30R** | 309.88 | 2.21 | %21.5 | +%824.2 |
| Yeni 20 | PusulaV2NoBtcFilter (temel) | 150 | +0.46R | 68.51 | 1.41 | %24.6 | +%67.8 |
| Yeni 20 | Puan ≥ +1 | **201** | **+0.52R** | 104.81 | 1.47 | %22.2 | +%115.3 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6).
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: kabul** (iki listede de ortalama R daha iyi, DD daha düşük). İşlem sayısı: eski 16'da +28 (%13), yeni 20'de +51 (%34).

## Ne değişti
`PusulaV2NoBtcScore1(PusulaV2NoBtcFilter)`: sadece long girişindeki `regime_up` şartı `puan >= 3` yerine `puan >= 1`. Kırılım, stop, BTC-dönüş çıkışı, EMA20 çıkışı aynı. `PusulaTrendLong`, `PusulaV2`, `PusulaV2NoBtcFilter` değişmedi.

## Ayarlar (tur 1 ile aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2NoBtcFilter) rakamları tur 1 raporuyla birebir aynı çıktı (210 / 150 işlem, 252.90R / 68.51R), yani ayarlar doğru kopyalandı.
- Not: bu dönem kasayı (2026-04 → 2026-09) da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Uyarı: kazanç birkaç coinde toplanıyor
Coin bazında toplam R farkı (yeni − temel):
- Eski 16: 7 coin daha iyi, 9 coin daha kötü. SOL tek başına +61.7R (toplam fark +57.0R). SOL hariç fark ≈ -4.7R. Daha kötüler: ETH -8.3R, ADA -5.3R, BNB -5.1R, LINK -4.3R.
- Yeni 20: 9 coin daha iyi, 11 coin daha kötü. ALGO +32.1R, UNI +25.7R (toplam fark +36.3R). Bu ikisi hariç fark ≈ -21.5R. En kötü: NEAR -12.2R.
- Yorum: gevşek eşik, trendin daha erken evresinde birkaç büyük kazananı yakalıyor; diğer coinlerde ek işlemler biraz zararda. Bu, Pusula'nın genel yapısıyla aynı (kâr birkaç büyük trendde). Kabul kuralı "ortalama R ve DD" olduğu için karar kabul, ama sonuç az sayıda işleme bağlı.
