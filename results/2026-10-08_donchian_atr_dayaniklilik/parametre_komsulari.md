# Parametre kararlılığı (±%20) — DonchianATR_B — 20200101-20250101

Her seferinde tek parametre değişti. Maliyet + funding dahil.

| Varyant | İşlem | Ortalama R | Profit factor | Net getiri % | Max DD % |
|---|---|---|---|---|---|
| base | 261 | +0.152 | 1.20 | +38.6 | 17.2 |
| channel=16 | 298 | +0.071 | 1.07 | +15.8 | 17.9 |
| channel=24 | 235 | +0.200 | 1.29 | +49.5 | 12.8 |
| vol_window=160 | 254 | +0.191 | 1.25 | +50.2 | 18.9 |
| vol_window=240 | 279 | +0.035 | 1.02 | +4.0 | 24.7 |

Not: buradaki "base" satırı tek başına çalıştırıldığı için 2020-03'ten başlar (500 mum ısınma); ilk backtest raporundaki rakamlardan biraz farklıdır.

**Sonuç:** Dört komşunun hepsi pozitif, ama `channel=16` (+0.07R) ve `vol_window=240` (+0.04R, PF 1.02, DD %24.7) zayıf. Eşik ("komşularında da pozitif") sağlanıyor, sınırda.

## Maliyet x2 (emir başına %0.2, geliştirme verisi)
| Strateji | İşlem | Ortalama R | Net getiri % | Max DD % | Profit factor |
|---|---|---|---|---|---|
| DonchianATR_B | 261 | +0.118 | +27.7 | 17.9 | 1.15 |

Maliyet iki katına çıkınca da pozitif → "kırılgan" değil.
