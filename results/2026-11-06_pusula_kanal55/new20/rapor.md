# PusulaV2NoBe vs PusulaV2NoBeChannel55 — kanal55 — 2026-11-06

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeChannel55**: 127 işlem, işlem başına ortalama **0.55R** (maliyet ve funding dahil), net getiri 60.5%, en büyük düşüş 27.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeChannel55 | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 60.5% | 194.7% |
| Max drawdown | 22.6% | 27.9% | 97.6% |
| Profit factor | 1.53 | 1.59 | — |
| Ortalama R | 0.61 | 0.55 | — |
| İşlem sayısı | 193 | 127 | — |
| Winrate | 23.3% | 22.0% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeChannel55 | long | 127 | 0.55 | 69.81 | 1.59 |
| PusulaV2NoBeChannel55 | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeChannel55 | 60.6% | 0.8% | 0.0% | 0.0% | 38.6% | 4.5% | -1271.02 |

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
| PusulaV2NoBeChannel55 | FIL/USDT:USDT | 4 | 4.34 | 17.37 | -97.9% |
| PusulaV2NoBeChannel55 | UNI/USDT:USDT | 11 | 1.59 | 17.48 | 62.4% |
| PusulaV2NoBeChannel55 | AAVE/USDT:USDT | 13 | -0.26 | -3.41 | 286.5% |
| PusulaV2NoBeChannel55 | NEAR/USDT:USDT | 7 | 5.51 | 38.58 | 373.4% |
| PusulaV2NoBeChannel55 | ALGO/USDT:USDT | 8 | 4.23 | 33.82 | -47.9% |
| PusulaV2NoBeChannel55 | XTZ/USDT:USDT | 7 | 0.33 | 2.33 | -84.3% |
| PusulaV2NoBeChannel55 | THETA/USDT:USDT | 6 | -0.93 | -5.56 | -48.0% |
| PusulaV2NoBeChannel55 | VET/USDT:USDT | 3 | -0.54 | -1.61 | 139.2% |
| PusulaV2NoBeChannel55 | ICP/USDT:USDT | 3 | 0.15 | 0.45 | -99.3% |
| PusulaV2NoBeChannel55 | SAND/USDT:USDT | 5 | -1.00 | -5.00 | -54.0% |
| PusulaV2NoBeChannel55 | MANA/USDT:USDT | 4 | -0.68 | -2.71 | -91.4% |
| PusulaV2NoBeChannel55 | AXS/USDT:USDT | 1 | -0.38 | -0.38 | 136.4% |
| PusulaV2NoBeChannel55 | EGLD/USDT:USDT | 6 | -1.06 | -6.35 | -65.7% |
| PusulaV2NoBeChannel55 | HBAR/USDT:USDT | 5 | -0.57 | -2.84 | -68.6% |
| PusulaV2NoBeChannel55 | CHZ/USDT:USDT | 6 | -0.50 | -2.99 | -26.0% |
| PusulaV2NoBeChannel55 | ENJ/USDT:USDT | 4 | -0.80 | -3.19 | -83.5% |
| PusulaV2NoBeChannel55 | ZEC/USDT:USDT | 9 | 0.36 | 3.22 | 3815.4% |
| PusulaV2NoBeChannel55 | DASH/USDT:USDT | 7 | -0.21 | -1.44 | -19.1% |
| PusulaV2NoBeChannel55 | NEO/USDT:USDT | 10 | -0.60 | -5.99 | -65.8% |
| PusulaV2NoBeChannel55 | IOTA/USDT:USDT | 8 | -0.24 | -1.96 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeChannel55_sermaye.png](PusulaV2NoBeChannel55_sermaye.png)
![PusulaV2NoBeChannel55_R_dagilimi.png](PusulaV2NoBeChannel55_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
