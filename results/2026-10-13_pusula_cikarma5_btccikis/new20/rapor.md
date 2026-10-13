# PusulaV2NoBe vs PusulaV2NoBeNoBtcExit — cikarma5_new20 — 2026-10-13

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeNoBtcExit**: 220 işlem, işlem başına ortalama **1.31R** (maliyet ve funding dahil), net getiri 483.9%, en büyük düşüş 38.6%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeNoBtcExit | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 483.9% | 194.7% |
| Max drawdown | 22.6% | 38.6% | 97.6% |
| Profit factor | 1.53 | 2.59 | — |
| Ortalama R | 0.61 | 1.31 | — |
| İşlem sayısı | 193 | 220 | — |
| Winrate | 23.3% | 21.8% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeNoBtcExit | long | 220 | 1.31 | 287.71 | 2.59 |
| PusulaV2NoBeNoBtcExit | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeNoBtcExit | 55.0% | 0.5% | 0.0% | 0.0% | 44.5% | 7.2% | -1792.29 |

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
| PusulaV2NoBeNoBtcExit | FIL/USDT:USDT | 7 | 5.55 | 38.87 | -97.9% |
| PusulaV2NoBeNoBtcExit | UNI/USDT:USDT | 20 | 1.08 | 21.70 | 62.4% |
| PusulaV2NoBeNoBtcExit | AAVE/USDT:USDT | 23 | -0.86 | -19.88 | 286.5% |
| PusulaV2NoBeNoBtcExit | NEAR/USDT:USDT | 13 | -0.46 | -5.93 | 373.4% |
| PusulaV2NoBeNoBtcExit | ALGO/USDT:USDT | 13 | 2.61 | 33.97 | -47.9% |
| PusulaV2NoBeNoBtcExit | XTZ/USDT:USDT | 17 | 0.18 | 2.99 | -84.3% |
| PusulaV2NoBeNoBtcExit | THETA/USDT:USDT | 8 | 2.45 | 19.59 | -48.0% |
| PusulaV2NoBeNoBtcExit | VET/USDT:USDT | 13 | 1.47 | 19.12 | 139.2% |
| PusulaV2NoBeNoBtcExit | ICP/USDT:USDT | 4 | 0.36 | 1.43 | -99.3% |
| PusulaV2NoBeNoBtcExit | SAND/USDT:USDT | 5 | -0.66 | -3.32 | -54.0% |
| PusulaV2NoBeNoBtcExit | MANA/USDT:USDT | 9 | -0.48 | -4.32 | -91.4% |
| PusulaV2NoBeNoBtcExit | AXS/USDT:USDT | 2 | -0.68 | -1.36 | 136.4% |
| PusulaV2NoBeNoBtcExit | EGLD/USDT:USDT | 9 | -0.47 | -4.25 | -65.7% |
| PusulaV2NoBeNoBtcExit | HBAR/USDT:USDT | 5 | -0.64 | -3.22 | -68.6% |
| PusulaV2NoBeNoBtcExit | CHZ/USDT:USDT | 8 | 0.03 | 0.25 | -26.0% |
| PusulaV2NoBeNoBtcExit | ENJ/USDT:USDT | 5 | 0.26 | 1.31 | -83.5% |
| PusulaV2NoBeNoBtcExit | ZEC/USDT:USDT | 17 | 10.73 | 182.40 | 3815.4% |
| PusulaV2NoBeNoBtcExit | DASH/USDT:USDT | 22 | -0.13 | -2.84 | -19.1% |
| PusulaV2NoBeNoBtcExit | NEO/USDT:USDT | 12 | 0.66 | 7.88 | -65.8% |
| PusulaV2NoBeNoBtcExit | IOTA/USDT:USDT | 8 | 0.41 | 3.30 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeNoBtcExit_sermaye.png](PusulaV2NoBeNoBtcExit_sermaye.png)
![PusulaV2NoBeNoBtcExit_R_dagilimi.png](PusulaV2NoBeNoBtcExit_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
