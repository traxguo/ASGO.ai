# atr_filtered — ATR "piyasa uygun mu?" filtreli versiyonlar

Kod: [`strategies/candidates/atr_filtered.py`](../strategies/candidates/atr_filtered.py)

| Sınıf | Temel strateji |
|---|---|
| `DonchianATR_B` / `_A` | [donchian_breakout](donchian_breakout.md) |
| `RSIReversionATR_B` / `_A` | [rsi_reversion](rsi_reversion.md) |
| `TrendMAATR_B` / `_A` | [trend_ma](trend_ma.md) (emekli; sadece filtre testi için) |

## Hipotez
Fiyat durgunken gelen sinyaller çoğu zaman gürültüdür ve stop olur. Piyasa normalden daha hareketliyken (oynaklık yüksekken) gelen sinyallerin hedefe ulaşma şansı daha yüksek olabilir. Filtre işlem sayısını azaltır; amaç kötü işlemleri ayıklayıp drawdown'u düşürmek.

## Yön
Temel stratejiyle aynı (long ve short).

## Giriş koşulları
Temel stratejinin bütün koşulları + şu koşul (long ve short için aynı):
- [vol_ok] Teknik: `ATR(14) / close` > son 200 mumdaki değerlerinin medyanı | Açıklama: "Piyasa normalden hareketli (ATR fiyatın %{atr_pct}'i, 200 mumluk ortanca %{atr_pct_median})."

## İşlem yönetimi
Ortak modülden, temel stratejilerle aynı.

## Zaman dilimi ve parametreler
Test öncesi sabitlendi; üç strateji için tek kural.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 4h | temel stratejiyle aynı |
| ATR periyodu | 14 | sabit |
| Medyan penceresi | 200 mum | 100-300 |

## Durum
- `DonchianATR`: **en iyi aday, ama aşama 4 (doğrulama) eşiklerini geçemedi** — karar proje sahibinde
- `RSIReversionATR`, `TrendMAATR`: elendi (aşama 2)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-08 | Lookahead (4h, üç strateji) | Bias yok. | — |
| 2026-10-08 | İlk backtest, A vs B (geliştirme 2020-06 → 2024-12) | DonchianATR_B: +0.16R, PF 1.22, DD %17.1, 254 işlem, 6 coinin 5'i pozitif. RSIReversionATR_B -0.32R, TrendMAATR_B -0.24R. | [results/2026-10-08_atr_filtered_ilk_backtest](../results/2026-10-08_atr_filtered_ilk_backtest/rapor.md) |
| 2026-10-08 | DonchianATR TP ızgarası (geliştirme) | 12 modelin hepsi pozitif; en iyisi varsayılan Model B (+0.152R). | [results/2026-10-08_donchian_atr_tp_izgara](../results/2026-10-08_donchian_atr_tp_izgara/izgara.md) |
| 2026-10-08 | DonchianATR_B dayanıklılık (geliştirme) | Parametre ±%20: 4 komşunun hepsi pozitif (+0.04 ile +0.20R; en zayıfı vol_window=240). Maliyet x2: +0.12R, PF 1.15. | [results/2026-10-08_donchian_atr_dayaniklilik](../results/2026-10-08_donchian_atr_dayaniklilik/parametre_komsulari.md) |
| 2026-10-08 | DonchianATR_B doğrulama (2025-01 → 2026-03) | +0.06R, PF 1.04, DD %13.5, 88 işlem, net +%2.2 (al-tut -%40). Long -9.0R, short +14.0R. 6 coinin 2'si pozitif. **Eşikleri geçemedi.** | [results/2026-10-08_donchian_atr_dogrulama](../results/2026-10-08_donchian_atr_dogrulama/rapor.md) |

## Notlar / öğrenilenler
- Filtre kırılım stratejisinde işe yaradı (yanlış kırılımları azalttı, DD %38 → %17), ama dönüş ve kesişim stratejilerinde zarar büyüttü.
- DonchianATR'de kârlı taraf dönemden döneme değişti (geliştirmede long, doğrulamada short): tutarlı bir üstünlük henüz görünmüyor.
- **Dürüstlük notu:** donchian_breakout doğrulama verisinde (2025-01 → 2026-03) bir kez test edildi ve kaybetti. Filtreli versiyonun doğrulama sonucu bu yüzden tam "görülmemiş veri" sayılmaz; bu filtre doğrulama sonucuna bakılarak seçilmedi (kural test öncesi sabitlendi), ama bunu bilerek değerlendirilmeli.

## Emeklilik gerekçesi (varsa)
- `RSIReversionATR`, `TrendMAATR` (2026-10-08): ilk backtest'te belirgin negatif beklenti (-0.32R, -0.24R).
