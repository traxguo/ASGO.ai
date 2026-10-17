# PusulaV2NoBe vs PusulaV2NoBeNoReentry — yeniden_giris — 2026-10-17

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeNoReentry**: 164 işlem, işlem başına ortalama **0.55R** (maliyet ve funding dahil), net getiri 86.5%, en büyük düşüş 23.4%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeNoReentry | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 86.5% | 194.7% |
| Max drawdown | 22.6% | 23.4% | 97.6% |
| Profit factor | 1.53 | 1.47 | — |
| Ortalama R | 0.61 | 0.55 | — |
| İşlem sayısı | 193 | 164 | — |
| Winrate | 23.3% | 20.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeNoReentry | long | 164 | 0.55 | 89.56 | 1.47 |
| PusulaV2NoBeNoReentry | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeNoReentry | 58.5% | 0.0% | 0.0% | 0.0% | 41.5% | 6.3% | -2739.83 |

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
| PusulaV2NoBeNoReentry | FIL/USDT:USDT | 8 | 5.96 | 47.71 | -97.9% |
| PusulaV2NoBeNoReentry | UNI/USDT:USDT | 14 | 1.26 | 17.65 | 62.4% |
| PusulaV2NoBeNoReentry | AAVE/USDT:USDT | 10 | -0.77 | -7.66 | 286.5% |
| PusulaV2NoBeNoReentry | NEAR/USDT:USDT | 9 | 1.69 | 15.25 | 373.4% |
| PusulaV2NoBeNoReentry | ALGO/USDT:USDT | 13 | 2.63 | 34.23 | -47.9% |
| PusulaV2NoBeNoReentry | XTZ/USDT:USDT | 11 | 0.31 | 3.43 | -84.3% |
| PusulaV2NoBeNoReentry | THETA/USDT:USDT | 6 | -0.57 | -3.44 | -48.0% |
| PusulaV2NoBeNoReentry | VET/USDT:USDT | 12 | 0.95 | 11.44 | 139.2% |
| PusulaV2NoBeNoReentry | ICP/USDT:USDT | 4 | -0.53 | -2.13 | -99.3% |
| PusulaV2NoBeNoReentry | SAND/USDT:USDT | 4 | -0.69 | -2.76 | -54.0% |
| PusulaV2NoBeNoReentry | MANA/USDT:USDT | 6 | -0.93 | -5.58 | -91.4% |
| PusulaV2NoBeNoReentry | AXS/USDT:USDT | 2 | -0.68 | -1.36 | 136.4% |
| PusulaV2NoBeNoReentry | EGLD/USDT:USDT | 8 | -0.48 | -3.86 | -65.7% |
| PusulaV2NoBeNoReentry | HBAR/USDT:USDT | 6 | -0.33 | -1.95 | -68.6% |
| PusulaV2NoBeNoReentry | CHZ/USDT:USDT | 7 | -0.88 | -6.17 | -26.0% |
| PusulaV2NoBeNoReentry | ENJ/USDT:USDT | 4 | 0.59 | 2.36 | -83.5% |
| PusulaV2NoBeNoReentry | ZEC/USDT:USDT | 11 | -0.39 | -4.34 | 3815.4% |
| PusulaV2NoBeNoReentry | DASH/USDT:USDT | 13 | 0.24 | 3.18 | -19.1% |
| PusulaV2NoBeNoReentry | NEO/USDT:USDT | 11 | -0.21 | -2.34 | -65.8% |
| PusulaV2NoBeNoReentry | IOTA/USDT:USDT | 5 | -0.82 | -4.11 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeNoReentry_sermaye.png](PusulaV2NoBeNoReentry_sermaye.png)
![PusulaV2NoBeNoReentry_R_dagilimi.png](PusulaV2NoBeNoReentry_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
