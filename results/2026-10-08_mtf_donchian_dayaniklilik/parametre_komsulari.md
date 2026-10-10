# Parametre kararlılığı (±%20) — MTFDonchian_B — 20200101-20250101

Her seferinde tek parametre değişti. Maliyet + funding dahil.

| Varyant | İşlem | Ortalama R | Profit factor | Net getiri % | Max DD % |
|---|---|---|---|---|---|
| base | 460 | +0.100 | 1.11 | +41.4 | 36.9 |
| channel=16 | 506 | +0.085 | 1.08 | +35.1 | 39.3 |
| channel=24 | 419 | +0.094 | 1.10 | +33.8 | 34.6 |
| trend_ema=40 | 457 | +0.122 | 1.13 | +55.8 | 35.1 |
| trend_ema=60 | 459 | +0.075 | 1.07 | +26.8 | 36.7 |

**Sonuç:** Dört komşunun hepsi pozitif (+0.075 ile +0.122R), sonuç parametrelere hassas değil.

## Maliyet x2 (emir başına %0.2, geliştirme verisi)
| Strateji | İşlem | Ortalama R | Net getiri % | Max DD % | Profit factor |
|---|---|---|---|---|---|
| MTFDonchian_B | 460 | +0.059 | +17.5 | 39.8 | 1.05 |

Maliyet iki katında da pozitif, ama kâr faktörü 1.05'e iniyor.
