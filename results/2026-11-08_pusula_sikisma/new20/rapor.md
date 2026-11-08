# PusulaV2NoBe vs PusulaV2NoBeSqueeze — sikisma — 2026-11-08

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeSqueeze**: 172 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 121.9%, en büyük düşüş 28.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeSqueeze | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 121.9% | 194.7% |
| Max drawdown | 22.6% | 28.9% | 97.6% |
| Profit factor | 1.53 | 1.53 | — |
| Ortalama R | 0.61 | 0.61 | — |
| İşlem sayısı | 193 | 172 | — |
| Winrate | 23.3% | 22.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeSqueeze | long | 172 | 0.61 | 104.53 | 1.53 |
| PusulaV2NoBeSqueeze | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeSqueeze | 53.5% | 0.6% | 0.0% | 0.0% | 45.9% | 6.5% | -3766.10 |

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
| PusulaV2NoBeSqueeze | FIL/USDT:USDT | 5 | 5.86 | 29.31 | -97.9% |
| PusulaV2NoBeSqueeze | UNI/USDT:USDT | 16 | 1.48 | 23.68 | 62.4% |
| PusulaV2NoBeSqueeze | AAVE/USDT:USDT | 15 | -0.72 | -10.74 | 286.5% |
| PusulaV2NoBeSqueeze | NEAR/USDT:USDT | 8 | -0.15 | -1.17 | 373.4% |
| PusulaV2NoBeSqueeze | ALGO/USDT:USDT | 8 | 0.36 | 2.86 | -47.9% |
| PusulaV2NoBeSqueeze | XTZ/USDT:USDT | 14 | 0.38 | 5.34 | -84.3% |
| PusulaV2NoBeSqueeze | THETA/USDT:USDT | 12 | 1.28 | 15.35 | -48.0% |
| PusulaV2NoBeSqueeze | VET/USDT:USDT | 12 | 1.09 | 13.07 | 139.2% |
| PusulaV2NoBeSqueeze | ICP/USDT:USDT | 3 | 0.82 | 2.47 | -99.3% |
| PusulaV2NoBeSqueeze | SAND/USDT:USDT | 5 | -0.76 | -3.79 | -54.0% |
| PusulaV2NoBeSqueeze | MANA/USDT:USDT | 7 | 2.48 | 17.35 | -91.4% |
| PusulaV2NoBeSqueeze | AXS/USDT:USDT | 1 | -0.98 | -0.98 | 136.4% |
| PusulaV2NoBeSqueeze | EGLD/USDT:USDT | 8 | -0.49 | -3.90 | -65.7% |
| PusulaV2NoBeSqueeze | HBAR/USDT:USDT | 5 | -0.98 | -4.92 | -68.6% |
| PusulaV2NoBeSqueeze | CHZ/USDT:USDT | 8 | -0.68 | -5.48 | -26.0% |
| PusulaV2NoBeSqueeze | ENJ/USDT:USDT | 3 | 4.77 | 14.31 | -83.5% |
| PusulaV2NoBeSqueeze | ZEC/USDT:USDT | 11 | 0.01 | 0.11 | 3815.4% |
| PusulaV2NoBeSqueeze | DASH/USDT:USDT | 10 | -0.37 | -3.69 | -19.1% |
| PusulaV2NoBeSqueeze | NEO/USDT:USDT | 14 | 0.85 | 11.87 | -65.8% |
| PusulaV2NoBeSqueeze | IOTA/USDT:USDT | 7 | 0.50 | 3.47 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeSqueeze_sermaye.png](PusulaV2NoBeSqueeze_sermaye.png)
![PusulaV2NoBeSqueeze_R_dagilimi.png](PusulaV2NoBeSqueeze_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
