# TP model ızgarası — DonchianBreakout_B — 20200101-20250101

Sadece geliştirme verisi. Maliyet + funding dahil. Ortalama R'ye göre sıralı.

| Varyant | TP1 (R) | TP2 (R) | TP1'de kapat % | BE tetiği | İşlem | Ortalama R | Long R | Short R | Profit factor | Net getiri % | Max DD % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tp1=2.0_tp2=4.0_pct=50_be=TP1 | 2.0 | 4.0 | 50 | TP1 | 567 | +0.092 | +46.7 | +5.4 | 1.10 | +47.0 | 38.4 |
| tp1=1.5_tp2=4.0_pct=50_be=TP1 | 1.5 | 4.0 | 50 | TP1 | 620 | +0.084 | +52.0 | +0.4 | 1.12 | +51.0 | 35.2 |
| tp1=2.0_tp2=3.0_pct=50_be=TP1 | 2.0 | 3.0 | 50 | TP1 | 636 | +0.084 | +34.9 | +18.6 | 1.09 | +47.8 | 43.3 |
| tp1=1.5_tp2=3.0_pct=50_be=TP1 | 1.5 | 3.0 | 50 | TP1 | 700 | +0.084 | +41.5 | +17.2 | 1.12 | +60.2 | 37.2 |
| tp1=2.0_tp2=3.0_pct=0_be=TP1 | 2.0 | 3.0 | 0 | TP1 | 636 | +0.078 | +33.4 | +16.0 | 1.07 | +37.0 | 48.0 |
| tp1=1.5_tp2=3.0_pct=0_be=2R | 1.5 | 3.0 | 0 | 2R | 636 | +0.078 | +33.4 | +16.0 | 1.07 | +37.0 | 48.0 |
| tp1=1.5_tp2=3.0_pct=0_be=TP1 | 1.5 | 3.0 | 0 | TP1 | 703 | +0.071 | +41.2 | +9.0 | 1.08 | +40.0 | 52.1 |
| tp1=1.5_tp2=3.0_pct=50_be=2R | 1.5 | 3.0 | 50 | 2R | 636 | +0.067 | +30.9 | +11.9 | 1.09 | +37.5 | 41.1 |
| tp1=2.0_tp2=4.0_pct=0_be=TP1 | 2.0 | 4.0 | 0 | TP1 | 570 | +0.064 | +40.5 | -3.7 | 1.04 | +18.9 | 41.6 |
| tp1=1.5_tp2=4.0_pct=0_be=2R | 1.5 | 4.0 | 0 | 2R | 570 | +0.064 | +40.5 | -3.7 | 1.04 | +18.9 | 41.6 |
| tp1=1.5_tp2=4.0_pct=50_be=2R | 1.5 | 4.0 | 50 | 2R | 569 | +0.058 | +37.6 | -4.6 | 1.07 | +24.8 | 35.4 |
| tp1=2.0_tp2=3.0_pct=50_be=2R | 2.0 | 3.0 | 50 | 2R | 635 | +0.057 | +25.8 | +10.5 | 1.05 | +24.1 | 47.7 |
| tp1=2.0_tp2=4.0_pct=50_be=2R | 2.0 | 4.0 | 50 | 2R | 568 | +0.054 | +32.6 | -1.8 | 1.04 | +18.5 | 40.4 |
| tp1=1.5_tp2=4.0_pct=0_be=TP1 | 1.5 | 4.0 | 0 | TP1 | 628 | +0.046 | +45.7 | -16.7 | 1.03 | +11.4 | 49.8 |

Not: Bu tablo ızgara tekilleştirmesi düzeltilmeden önce üretildi; `tp1=2.0_tp2=3.0_pct=0_be=TP1` ile `tp1=1.5_tp2=3.0_pct=0_be=2R` (ve 4R'lı eşi) aynı modeldir (kısmi çıkış yoksa TP1 sadece BE seviyesini belirler, ikisi de 2R).

**Seçim:** Ortalama R'ye göre en iyi varyant zaten varsayılan Model B (2R'de %50, BE, 4R). Komşu varyantlar +0.05 ile +0.09R arası; sonuç TP seçimine hassas değil.
