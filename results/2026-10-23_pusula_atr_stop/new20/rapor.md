# PusulaV2NoBe vs PusulaV2NoBeAtrStop — atr_stop — 2026-10-23

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeAtrStop**: 412 işlem, işlem başına ortalama **0.72R** (maliyet ve funding dahil), net getiri 423.4%, en büyük düşüş 68.3%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeAtrStop | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 423.4% | 194.7% |
| Max drawdown | 22.6% | 68.3% | 97.6% |
| Profit factor | 1.53 | 1.53 | — |
| Ortalama R | 0.61 | 0.72 | — |
| İşlem sayısı | 193 | 412 | — |
| Winrate | 23.3% | 15.8% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeAtrStop | long | 412 | 0.72 | 296.25 | 1.53 |
| PusulaV2NoBeAtrStop | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeAtrStop | 79.1% | 0.5% | 0.0% | 0.0% | 20.4% | 5.9% | -12790.20 |

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
| PusulaV2NoBeAtrStop | FIL/USDT:USDT | 13 | 2.18 | 28.28 | -97.9% |
| PusulaV2NoBeAtrStop | UNI/USDT:USDT | 36 | 1.94 | 69.73 | 62.4% |
| PusulaV2NoBeAtrStop | AAVE/USDT:USDT | 30 | -0.25 | -7.46 | 286.5% |
| PusulaV2NoBeAtrStop | NEAR/USDT:USDT | 26 | 1.66 | 43.16 | 373.4% |
| PusulaV2NoBeAtrStop | ALGO/USDT:USDT | 25 | 0.23 | 5.70 | -47.9% |
| PusulaV2NoBeAtrStop | XTZ/USDT:USDT | 23 | -0.49 | -11.23 | -84.3% |
| PusulaV2NoBeAtrStop | THETA/USDT:USDT | 32 | 1.21 | 38.64 | -48.0% |
| PusulaV2NoBeAtrStop | VET/USDT:USDT | 24 | 2.84 | 68.25 | 139.2% |
| PusulaV2NoBeAtrStop | ICP/USDT:USDT | 11 | -0.77 | -8.48 | -99.3% |
| PusulaV2NoBeAtrStop | SAND/USDT:USDT | 7 | -1.05 | -7.33 | -54.0% |
| PusulaV2NoBeAtrStop | MANA/USDT:USDT | 11 | 1.60 | 17.57 | -91.4% |
| PusulaV2NoBeAtrStop | AXS/USDT:USDT | 8 | 0.05 | 0.44 | 136.4% |
| PusulaV2NoBeAtrStop | EGLD/USDT:USDT | 21 | 3.00 | 62.91 | -65.7% |
| PusulaV2NoBeAtrStop | HBAR/USDT:USDT | 23 | -0.17 | -4.01 | -68.6% |
| PusulaV2NoBeAtrStop | CHZ/USDT:USDT | 26 | -0.86 | -22.33 | -26.0% |
| PusulaV2NoBeAtrStop | ENJ/USDT:USDT | 4 | -1.04 | -4.16 | -83.5% |
| PusulaV2NoBeAtrStop | ZEC/USDT:USDT | 33 | 1.79 | 59.20 | 3815.4% |
| PusulaV2NoBeAtrStop | DASH/USDT:USDT | 17 | -0.57 | -9.74 | -19.1% |
| PusulaV2NoBeAtrStop | NEO/USDT:USDT | 25 | -1.02 | -25.39 | -65.8% |
| PusulaV2NoBeAtrStop | IOTA/USDT:USDT | 17 | 0.15 | 2.52 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeAtrStop_sermaye.png](PusulaV2NoBeAtrStop_sermaye.png)
![PusulaV2NoBeAtrStop_R_dagilimi.png](PusulaV2NoBeAtrStop_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
