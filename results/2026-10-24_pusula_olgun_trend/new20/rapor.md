# PusulaV2NoBe vs PusulaV2NoBeMature — olgun_trend — 2026-10-24

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeMature**: 130 işlem, işlem başına ortalama **0.62R** (maliyet ve funding dahil), net getiri 89.5%, en büyük düşüş 23.2%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeMature | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 89.5% | 194.7% |
| Max drawdown | 22.6% | 23.2% | 97.6% |
| Profit factor | 1.53 | 1.54 | — |
| Ortalama R | 0.61 | 0.62 | — |
| İşlem sayısı | 193 | 130 | — |
| Winrate | 23.3% | 24.6% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeMature | long | 130 | 0.62 | 80.32 | 1.54 |
| PusulaV2NoBeMature | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeMature | 53.1% | 0.0% | 0.0% | 0.0% | 46.9% | 5.1% | -3525.58 |

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
| PusulaV2NoBeMature | FIL/USDT:USDT | 2 | 16.20 | 32.41 | -97.9% |
| PusulaV2NoBeMature | UNI/USDT:USDT | 12 | -0.23 | -2.71 | 62.4% |
| PusulaV2NoBeMature | AAVE/USDT:USDT | 11 | -0.79 | -8.72 | 286.5% |
| PusulaV2NoBeMature | NEAR/USDT:USDT | 6 | -0.45 | -2.69 | 373.4% |
| PusulaV2NoBeMature | ALGO/USDT:USDT | 9 | 0.10 | 0.94 | -47.9% |
| PusulaV2NoBeMature | XTZ/USDT:USDT | 12 | 0.11 | 1.28 | -84.3% |
| PusulaV2NoBeMature | THETA/USDT:USDT | 9 | 2.00 | 18.01 | -48.0% |
| PusulaV2NoBeMature | VET/USDT:USDT | 6 | 4.08 | 24.51 | 139.2% |
| PusulaV2NoBeMature | ICP/USDT:USDT | 4 | 0.10 | 0.39 | -99.3% |
| PusulaV2NoBeMature | SAND/USDT:USDT | 4 | -0.81 | -3.25 | -54.0% |
| PusulaV2NoBeMature | MANA/USDT:USDT | 4 | -0.30 | -1.19 | -91.4% |
| PusulaV2NoBeMature | AXS/USDT:USDT | 2 | -1.01 | -2.02 | 136.4% |
| PusulaV2NoBeMature | EGLD/USDT:USDT | 5 | -0.16 | -0.80 | -65.7% |
| PusulaV2NoBeMature | HBAR/USDT:USDT | 4 | -0.55 | -2.19 | -68.6% |
| PusulaV2NoBeMature | CHZ/USDT:USDT | 5 | 0.16 | 0.82 | -26.0% |
| PusulaV2NoBeMature | ENJ/USDT:USDT | 1 | 5.69 | 5.69 | -83.5% |
| PusulaV2NoBeMature | ZEC/USDT:USDT | 8 | -0.26 | -2.09 | 3815.4% |
| PusulaV2NoBeMature | DASH/USDT:USDT | 10 | 0.19 | 1.87 | -19.1% |
| PusulaV2NoBeMature | NEO/USDT:USDT | 10 | 1.47 | 14.68 | -65.8% |
| PusulaV2NoBeMature | IOTA/USDT:USDT | 6 | 0.90 | 5.39 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeMature_sermaye.png](PusulaV2NoBeMature_sermaye.png)
![PusulaV2NoBeMature_R_dagilimi.png](PusulaV2NoBeMature_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
