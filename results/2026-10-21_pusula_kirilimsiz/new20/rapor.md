# PusulaV2NoBe vs PusulaV2NoBeNoBreakout — kirilimsiz — 2026-10-21

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeNoBreakout**: 737 işlem, işlem başına ortalama **-0.23R** (maliyet ve funding dahil), net getiri -8.7%, en büyük düşüş 82.9%.
- Aynı dönemde coinleri al-tut (eşit ağırlık): getiri 194.7%, ortalama en büyük düşüş 97.6%.

## Ayarlar
- Dönem: 2020-04-11 00:00:00 → 2026-09-30 20:00:00
- Coinler: FIL/USDT:USDT, UNI/USDT:USDT, AAVE/USDT:USDT, NEAR/USDT:USDT, ALGO/USDT:USDT, XTZ/USDT:USDT, THETA/USDT:USDT, VET/USDT:USDT, ICP/USDT:USDT, SAND/USDT:USDT, MANA/USDT:USDT, AXS/USDT:USDT, EGLD/USDT:USDT, HBAR/USDT:USDT, CHZ/USDT:USDT, ENJ/USDT:USDT, ZEC/USDT:USDT, DASH/USDT:USDT, NEO/USDT:USDT, IOTA/USDT:USDT
- Zaman dilimi: 4h
- Yön: long + short
- Mod: futures / isolated
- Kaldıraç: en fazla 3x, likidasyon stop mesafesinin en az 2 katı uzakta (bölüm 7.6)
- Risk: işlem başına sermayenin %1'i (pozisyon büyüklüğü stop mesafesine göre)
- Maliyet: her emir için %0.05 komisyon + %0.05 kayma (= %0.1), funding geçmiş veriden
- Başlangıç sermayesi: 10000 USDT

## Metrikler
| Metrik | PusulaV2NoBe | PusulaV2NoBeNoBreakout | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | -8.7% | 194.7% |
| Max drawdown | 22.6% | 82.9% | 97.6% |
| Profit factor | 1.53 | 0.99 | — |
| Ortalama R | 0.61 | -0.23 | — |
| İşlem sayısı | 193 | 737 | — |
| Winrate | 23.3% | 17.9% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeNoBreakout | long | 737 | -0.23 | -171.23 | 0.99 |
| PusulaV2NoBeNoBreakout | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeNoBreakout | 54.0% | 0.1% | 0.0% | 0.0% | 45.9% | 5.4% | -8154.32 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
| PusulaV2NoBe | FIL/USDT:USDT | 7 | 5.55 | 38.87 | -97.9% |
| PusulaV2NoBe | UNI/USDT:USDT | 20 | 1.06 | 21.22 | 62.4% |
| PusulaV2NoBe | AAVE/USDT:USDT | 17 | -0.75 | -12.83 | 286.5% |
| PusulaV2NoBe | NEAR/USDT:USDT | 9 | -0.19 | -1.72 | 373.4% |
| PusulaV2NoBe | ALGO/USDT:USDT | 12 | 2.92 | 35.04 | -47.9% |
| PusulaV2NoBe | XTZ/USDT:USDT | 16 | 0.25 | 4.04 | -84.3% |
| PusulaV2NoBe | THETA/USDT:USDT | 8 | 2.45 | 19.59 | -48.0% |
| PusulaV2NoBe | VET/USDT:USDT | 13 | 1.47 | 19.17 | 139.2% |
| PusulaV2NoBe | ICP/USDT:USDT | 4 | 0.36 | 1.43 | -99.3% |
| PusulaV2NoBe | SAND/USDT:USDT | 4 | -0.69 | -2.76 | -54.0% |
| PusulaV2NoBe | MANA/USDT:USDT | 7 | -0.55 | -3.84 | -91.4% |
| PusulaV2NoBe | AXS/USDT:USDT | 2 | -0.68 | -1.36 | 136.4% |
| PusulaV2NoBe | EGLD/USDT:USDT | 8 | -0.48 | -3.86 | -65.7% |
| PusulaV2NoBe | HBAR/USDT:USDT | 6 | -0.66 | -3.94 | -68.6% |
| PusulaV2NoBe | CHZ/USDT:USDT | 6 | -0.68 | -4.10 | -26.0% |
| PusulaV2NoBe | ENJ/USDT:USDT | 4 | 0.59 | 2.36 | -83.5% |
| PusulaV2NoBe | ZEC/USDT:USDT | 13 | -0.17 | -2.15 | 3815.4% |
| PusulaV2NoBe | DASH/USDT:USDT | 17 | 0.08 | 1.35 | -19.1% |
| PusulaV2NoBe | NEO/USDT:USDT | 12 | 0.66 | 7.88 | -65.8% |
| PusulaV2NoBe | IOTA/USDT:USDT | 8 | 0.41 | 3.31 | -66.9% |
| PusulaV2NoBeNoBreakout | FIL/USDT:USDT | 52 | 0.21 | 11.00 | -97.9% |
| PusulaV2NoBeNoBreakout | UNI/USDT:USDT | 74 | 0.72 | 53.16 | 62.4% |
| PusulaV2NoBeNoBreakout | AAVE/USDT:USDT | 68 | -0.40 | -27.19 | 286.5% |
| PusulaV2NoBeNoBreakout | NEAR/USDT:USDT | 43 | -1.54 | -66.35 | 373.4% |
| PusulaV2NoBeNoBreakout | ALGO/USDT:USDT | 42 | -0.02 | -0.91 | -47.9% |
| PusulaV2NoBeNoBreakout | XTZ/USDT:USDT | 45 | -0.65 | -29.11 | -84.3% |
| PusulaV2NoBeNoBreakout | THETA/USDT:USDT | 53 | -0.14 | -7.55 | -48.0% |
| PusulaV2NoBeNoBreakout | VET/USDT:USDT | 36 | 0.72 | 25.74 | 139.2% |
| PusulaV2NoBeNoBreakout | ICP/USDT:USDT | 26 | -0.23 | -5.91 | -99.3% |
| PusulaV2NoBeNoBreakout | SAND/USDT:USDT | 15 | -0.82 | -12.27 | -54.0% |
| PusulaV2NoBeNoBreakout | MANA/USDT:USDT | 30 | -0.64 | -19.11 | -91.4% |
| PusulaV2NoBeNoBreakout | AXS/USDT:USDT | 15 | -0.05 | -0.81 | 136.4% |
| PusulaV2NoBeNoBreakout | EGLD/USDT:USDT | 23 | 0.37 | 8.52 | -65.7% |
| PusulaV2NoBeNoBreakout | HBAR/USDT:USDT | 29 | -0.60 | -17.39 | -68.6% |
| PusulaV2NoBeNoBreakout | CHZ/USDT:USDT | 24 | -1.47 | -35.36 | -26.0% |
| PusulaV2NoBeNoBreakout | ENJ/USDT:USDT | 10 | -0.66 | -6.60 | -83.5% |
| PusulaV2NoBeNoBreakout | ZEC/USDT:USDT | 56 | -0.25 | -14.20 | 3815.4% |
| PusulaV2NoBeNoBreakout | DASH/USDT:USDT | 30 | -0.07 | -2.23 | -19.1% |
| PusulaV2NoBeNoBreakout | NEO/USDT:USDT | 33 | -0.28 | -9.12 | -65.8% |
| PusulaV2NoBeNoBreakout | IOTA/USDT:USDT | 33 | -0.47 | -15.55 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeNoBreakout_sermaye.png](PusulaV2NoBeNoBreakout_sermaye.png)
![PusulaV2NoBeNoBreakout_R_dagilimi.png](PusulaV2NoBeNoBreakout_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
