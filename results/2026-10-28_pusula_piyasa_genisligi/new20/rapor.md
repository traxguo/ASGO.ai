# PusulaV2NoBe vs PusulaV2NoBeBreadth — piyasa_genisligi — 2026-10-28

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeBreadth**: 146 işlem, işlem başına ortalama **1.06R** (maliyet ve funding dahil), net getiri 240.0%, en büyük düşüş 16.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeBreadth | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 240.0% | 194.7% |
| Max drawdown | 22.6% | 16.9% | 97.6% |
| Profit factor | 1.53 | 2.11 | — |
| Ortalama R | 0.61 | 1.06 | — |
| İşlem sayısı | 193 | 146 | — |
| Winrate | 23.3% | 24.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeBreadth | long | 146 | 1.06 | 155.14 | 2.11 |
| PusulaV2NoBeBreadth | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeBreadth | 52.1% | 0.7% | 0.0% | 0.0% | 47.3% | 5.2% | -3752.42 |

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
| PusulaV2NoBeBreadth | FIL/USDT:USDT | 5 | 7.84 | 39.20 | -97.9% |
| PusulaV2NoBeBreadth | UNI/USDT:USDT | 12 | 0.15 | 1.80 | 62.4% |
| PusulaV2NoBeBreadth | AAVE/USDT:USDT | 10 | -0.73 | -7.26 | 286.5% |
| PusulaV2NoBeBreadth | NEAR/USDT:USDT | 8 | 4.02 | 32.15 | 373.4% |
| PusulaV2NoBeBreadth | ALGO/USDT:USDT | 5 | -0.55 | -2.75 | -47.9% |
| PusulaV2NoBeBreadth | XTZ/USDT:USDT | 17 | 0.97 | 16.44 | -84.3% |
| PusulaV2NoBeBreadth | THETA/USDT:USDT | 5 | 3.98 | 19.91 | -48.0% |
| PusulaV2NoBeBreadth | VET/USDT:USDT | 10 | 3.02 | 30.24 | 139.2% |
| PusulaV2NoBeBreadth | ICP/USDT:USDT | 3 | 0.50 | 1.49 | -99.3% |
| PusulaV2NoBeBreadth | SAND/USDT:USDT | 4 | -0.69 | -2.76 | -54.0% |
| PusulaV2NoBeBreadth | MANA/USDT:USDT | 6 | 2.10 | 12.59 | -91.4% |
| PusulaV2NoBeBreadth | AXS/USDT:USDT | 1 | -1.07 | -1.07 | 136.4% |
| PusulaV2NoBeBreadth | EGLD/USDT:USDT | 5 | -0.14 | -0.72 | -65.7% |
| PusulaV2NoBeBreadth | HBAR/USDT:USDT | 4 | -0.47 | -1.87 | -68.6% |
| PusulaV2NoBeBreadth | CHZ/USDT:USDT | 7 | -0.69 | -4.82 | -26.0% |
| PusulaV2NoBeBreadth | ENJ/USDT:USDT | 3 | 5.01 | 15.02 | -83.5% |
| PusulaV2NoBeBreadth | ZEC/USDT:USDT | 9 | 0.22 | 1.95 | 3815.4% |
| PusulaV2NoBeBreadth | DASH/USDT:USDT | 14 | -0.60 | -8.35 | -19.1% |
| PusulaV2NoBeBreadth | NEO/USDT:USDT | 10 | 1.06 | 10.64 | -65.8% |
| PusulaV2NoBeBreadth | IOTA/USDT:USDT | 8 | 0.41 | 3.29 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeBreadth_sermaye.png](PusulaV2NoBeBreadth_sermaye.png)
![PusulaV2NoBeBreadth_R_dagilimi.png](PusulaV2NoBeBreadth_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
