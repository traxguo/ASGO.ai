# mtf_trend — Önce günlük trend, sonra 4 saatlik giriş

Kod: [`strategies/candidates/mtf_trend.py`](../strategies/candidates/mtf_trend.py)

## Hipotez
Proje sahibinin fikri: önce büyük resme (günlük grafik) bakıp trend yönünü belirle, sadece o yönde işlem aç. Günlük trend yukarıyken sadece long, aşağıyken sadece short. Giriş anını 4 saatlik grafikte popüler bir tetikle yakala. Ters yöndeki sinyaller elenir.

## Ortak trend filtresi (hepsinde)
- [trend_1d_up] Teknik: son **kapanmış** günlük mumun kapanışı > günlük EMA(50) | Açıklama: "Günlük trend yukarı (günlük kapanış {close_1d}, EMA50 {ema_trend_1d} üzerinde)."
- [trend_1d_down] Teknik: son kapanmış günlük mumun kapanışı < günlük EMA(50) | Açıklama: "Günlük trend aşağı (günlük kapanış {close_1d}, EMA50 {ema_trend_1d} altında)."

## Giriş tetikleri (4h) — her biri ayrı strateji
| Sınıf | Fikir | Long koşulu | Short koşulu |
|---|---|---|---|
| `MTFDonchian` | Kanal kırılımı (turtle) | [breakout_up] kapanış önceki 20 mumun tepesini ilk kez geçti: "Fiyat ({close}) son 20 mumun tepesini ({dc_upper}) kırdı." | [breakout_down] kapanış önceki 20 mumun dibinin altına ilk kez indi |
| `MTFPullback` | Trend içinde geri çekilme sonu | [rsi_pullback_end_up] RSI(14) 40'ın üstüne döndü: "RSI ({rsi}) geri çekilmeden yukarı döndü." | [rsi_pullback_end_down] RSI(14) 60'ın altına döndü |
| `MTFSupertrend` | Supertrend (popüler ATR tabanlı trend göstergesi) | [supertrend_flip_up] Supertrend(10, 3) yukarı döndü | [supertrend_flip_down] Supertrend(10, 3) aşağı döndü |
| `MTFSqueeze` | Sıkışma sonrası patlama (TTM squeeze) | [squeeze_break_up] önceki mumda Bollinger(20,2) Keltner(20,1.5 ATR) içindeydi, kapanış üst Bollinger'ı geçti | [squeeze_break_down] aynısı alt bantta |
| `MTFDonchianATR` | En iyi aday (DonchianATR) + günlük trend | breakout_up + [vol_ok] ATR% 200 mumluk medyanın üstünde | breakout_down + vol_ok |

## İşlem yönetimi
Ortak modülden, diğer stratejilerle aynı (giriş bölgesi, 1.5 ATR / yapısal stop, Model A ve B, 3 mum geçerlilik, en fazla 3x).

## Zaman dilimi ve parametreler
Test öncesi sabitlendi.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 4h | 1h, 4h |
| Trend zaman dilimi | 1d | sabit |
| Günlük EMA | 50 | 40-60 |
| Donchian kanalı | 20 mum | 15-55 |
| RSI / eşikler | 14 / 40-60 | 7-21 / 35-45 |
| Supertrend | 10, 3 | 7-14, 2-4 |
| Bollinger / Keltner | 20, 2 / 20, 1.5 | sabit |
| Isınma (startup) | 400 mum | günlük EMA50 için de 400 gün |

## Durum
- `MTFDonchian`: **en tutarlı aday** (iki dönemde de +0.10R), ama eşikleri geçemedi (doğrulamada PF 1.09 < 1.2; geliştirmede DD %37 > %25)
- `MTFPullback`, `MTFSupertrend`, `MTFSqueeze`, `MTFDonchianATR`: elendi (aşama 2)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-08 | Lookahead (5 strateji) + recursive (Supertrend) | Bias yok; 400 mum ısınmada sapma yok. | — |
| 2026-10-08 | İlk backtest, A vs B (geliştirme 2020-03 → 2024-12) | MTFDonchian_B +0.10R, PF 1.11, DD %36.9, 460 işlem. Pullback_B 0.00R, Supertrend_B -0.03R, Squeeze_B -0.08R. | [results/2026-10-08_mtf_trend_ilk_backtest](../results/2026-10-08_mtf_trend_ilk_backtest/rapor.md) |
| 2026-10-08 | MTFDonchianATR ilk backtest (geliştirme) | B +0.08R, PF 1.09, DD %28.2; filtresiz DonchianATR_B'den kötü (+0.15R, DD %17). Günlük filtre short'ları bozdu (-18.5R). | [results/2026-10-08_mtf_donchian_atr_ilk_backtest](../results/2026-10-08_mtf_donchian_atr_ilk_backtest/rapor.md) |
| 2026-10-08 | MTFDonchian TP ızgarası (geliştirme) | 12 modelin hepsi +0.06 ile +0.10R; en iyisi Model B. | [results/2026-10-08_mtf_donchian_tp_izgara](../results/2026-10-08_mtf_donchian_tp_izgara/izgara.md) |
| 2026-10-08 | MTFDonchian_B dayanıklılık (geliştirme) | ±%20: 4 komşu +0.075 ile +0.122R. Maliyet x2: +0.06R, PF 1.05, DD %39.8. | [results/2026-10-08_mtf_donchian_dayaniklilik](../results/2026-10-08_mtf_donchian_dayaniklilik/parametre_komsulari.md) |
| 2026-10-08 | MTFDonchian_B doğrulama (2025-01 → 2026-03) | +0.10R, PF 1.09, DD %16.1, 140 işlem, net +%9.5 (al-tut -%40). Long +4.1R, short +9.7R. 6 coinin 4'ü pozitif. | [results/2026-10-08_mtf_donchian_dogrulama](../results/2026-10-08_mtf_donchian_dogrulama/rapor.md) |

## Notlar / öğrenilenler
- Günlük trend filtresi, Donchian'da long tarafını korudu ama short'ları kötüleştirdi (günlük düşüş trendindeki aşağı kırılımlar sık sık geri döndü).
- Geri çekilme, Supertrend ve sıkışma tetikleri bu coinlerde ve 4h'de kâr üretmedi.
- MTFDonchian_B'nin artısı: iki dönemde de aynı beklenti (+0.10R) ve iki yön de doğrulamada pozitif. Eksisi: geliştirmede drawdown %37 ve kâr faktörü 1.1 civarı.
- **Çoklu deneme uyarısı:** Bugüne kadar ~15 varyant denendi. Çok şey denenince biri şansla iyi görünebilir; kasa testi bu yüzden önemli.

## Emeklilik gerekçesi (varsa)
- `MTFPullback`, `MTFSupertrend`, `MTFSqueeze` (2026-10-08): ilk backtest'te beklenti ≤ 0R.
- `MTFDonchianATR` (2026-10-08): pozitif (+0.08R) ama her ölçüde temel DonchianATR'den kötü; doğrulamaya alınmadı.
