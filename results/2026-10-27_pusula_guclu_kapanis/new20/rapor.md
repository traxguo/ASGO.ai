# PusulaV2NoBe vs PusulaV2NoBeStrongClose — guclu_kapanis — 2026-10-27

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeStrongClose**: 180 işlem, işlem başına ortalama **0.30R** (maliyet ve funding dahil), net getiri 41.7%, en büyük düşüş 20.1%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeStrongClose | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 41.7% | 194.7% |
| Max drawdown | 22.6% | 20.1% | 97.6% |
| Profit factor | 1.53 | 1.26 | — |
| Ortalama R | 0.61 | 0.30 | — |
| İşlem sayısı | 193 | 180 | — |
| Winrate | 23.3% | 22.8% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeStrongClose | long | 180 | 0.30 | 54.16 | 1.26 |
| PusulaV2NoBeStrongClose | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeStrongClose | 52.8% | 0.6% | 0.0% | 0.0% | 46.7% | 6.7% | -2684.60 |

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
| PusulaV2NoBeStrongClose | FIL/USDT:USDT | 5 | 1.38 | 6.91 | -97.9% |
| PusulaV2NoBeStrongClose | UNI/USDT:USDT | 18 | 1.25 | 22.57 | 62.4% |
| PusulaV2NoBeStrongClose | AAVE/USDT:USDT | 16 | -0.76 | -12.20 | 286.5% |
| PusulaV2NoBeStrongClose | NEAR/USDT:USDT | 9 | -0.48 | -4.31 | 373.4% |
| PusulaV2NoBeStrongClose | ALGO/USDT:USDT | 10 | 3.77 | 37.71 | -47.9% |
| PusulaV2NoBeStrongClose | XTZ/USDT:USDT | 15 | 0.31 | 4.58 | -84.3% |
| PusulaV2NoBeStrongClose | THETA/USDT:USDT | 8 | -0.64 | -5.15 | -48.0% |
| PusulaV2NoBeStrongClose | VET/USDT:USDT | 11 | 1.37 | 15.03 | 139.2% |
| PusulaV2NoBeStrongClose | ICP/USDT:USDT | 6 | -0.66 | -3.94 | -99.3% |
| PusulaV2NoBeStrongClose | SAND/USDT:USDT | 2 | -0.81 | -1.62 | -54.0% |
| PusulaV2NoBeStrongClose | MANA/USDT:USDT | 7 | -0.54 | -3.79 | -91.4% |
| PusulaV2NoBeStrongClose | AXS/USDT:USDT | 2 | -0.68 | -1.36 | 136.4% |
| PusulaV2NoBeStrongClose | EGLD/USDT:USDT | 8 | -0.38 | -3.08 | -65.7% |
| PusulaV2NoBeStrongClose | HBAR/USDT:USDT | 6 | -0.65 | -3.88 | -68.6% |
| PusulaV2NoBeStrongClose | CHZ/USDT:USDT | 6 | -0.69 | -4.12 | -26.0% |
| PusulaV2NoBeStrongClose | ENJ/USDT:USDT | 2 | 1.97 | 3.94 | -83.5% |
| PusulaV2NoBeStrongClose | ZEC/USDT:USDT | 13 | -0.12 | -1.62 | 3815.4% |
| PusulaV2NoBeStrongClose | DASH/USDT:USDT | 13 | -0.42 | -5.48 | -19.1% |
| PusulaV2NoBeStrongClose | NEO/USDT:USDT | 14 | 1.09 | 15.33 | -65.8% |
| PusulaV2NoBeStrongClose | IOTA/USDT:USDT | 9 | -0.15 | -1.36 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeStrongClose_sermaye.png](PusulaV2NoBeStrongClose_sermaye.png)
![PusulaV2NoBeStrongClose_R_dagilimi.png](PusulaV2NoBeStrongClose_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
