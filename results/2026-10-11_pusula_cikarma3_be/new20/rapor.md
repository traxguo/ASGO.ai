# PusulaV2NoBtcScore1 vs PusulaV2NoBe — cikarma3_new20 — 2026-10-11

## Özet
- **PusulaV2NoBtcScore1**: 201 işlem, işlem başına ortalama **0.52R** (maliyet ve funding dahil), net getiri 115.3%, en büyük düşüş 22.2%.
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
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
| Metrik | PusulaV2NoBtcScore1 | PusulaV2NoBe | Al-tut |
|---|---|---|---|
| Net getiri | 115.3% | 134.2% | 194.7% |
| Max drawdown | 22.2% | 22.6% | 97.6% |
| Profit factor | 1.47 | 1.53 | — |
| Ortalama R | 0.52 | 0.61 | — |
| İşlem sayısı | 201 | 193 | — |
| Winrate | 20.9% | 23.3% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBtcScore1 | long | 201 | 0.52 | 104.81 | 1.47 |
| PusulaV2NoBtcScore1 | short | 0 | — | 0.00 | — |
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBtcScore1 | 47.8% | 14.4% | 0.0% | 0.0% | 37.8% | 6.1% | -3762.08 |
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
| PusulaV2NoBtcScore1 | FIL/USDT:USDT | 7 | 4.03 | 28.21 | -97.9% |
| PusulaV2NoBtcScore1 | UNI/USDT:USDT | 22 | 0.87 | 19.14 | 62.4% |
| PusulaV2NoBtcScore1 | AAVE/USDT:USDT | 17 | -0.64 | -10.93 | 286.5% |
| PusulaV2NoBtcScore1 | NEAR/USDT:USDT | 11 | -0.21 | -2.28 | 373.4% |
| PusulaV2NoBtcScore1 | ALGO/USDT:USDT | 12 | 2.92 | 35.08 | -47.9% |
| PusulaV2NoBtcScore1 | XTZ/USDT:USDT | 16 | 0.18 | 2.91 | -84.3% |
| PusulaV2NoBtcScore1 | THETA/USDT:USDT | 8 | 2.45 | 19.59 | -48.0% |
| PusulaV2NoBtcScore1 | VET/USDT:USDT | 13 | 1.07 | 13.92 | 139.2% |
| PusulaV2NoBtcScore1 | ICP/USDT:USDT | 4 | -0.30 | -1.20 | -99.3% |
| PusulaV2NoBtcScore1 | SAND/USDT:USDT | 4 | -0.69 | -2.76 | -54.0% |
| PusulaV2NoBtcScore1 | MANA/USDT:USDT | 7 | -0.55 | -3.84 | -91.4% |
| PusulaV2NoBtcScore1 | AXS/USDT:USDT | 2 | -0.49 | -0.98 | 136.4% |
| PusulaV2NoBtcScore1 | EGLD/USDT:USDT | 8 | -0.48 | -3.86 | -65.7% |
| PusulaV2NoBtcScore1 | HBAR/USDT:USDT | 6 | -0.66 | -3.96 | -68.6% |
| PusulaV2NoBtcScore1 | CHZ/USDT:USDT | 6 | -0.68 | -4.10 | -26.0% |
| PusulaV2NoBtcScore1 | ENJ/USDT:USDT | 4 | 0.99 | 3.97 | -83.5% |
| PusulaV2NoBtcScore1 | ZEC/USDT:USDT | 13 | -0.09 | -1.13 | 3815.4% |
| PusulaV2NoBtcScore1 | DASH/USDT:USDT | 17 | 0.32 | 5.46 | -19.1% |
| PusulaV2NoBtcScore1 | NEO/USDT:USDT | 15 | 0.49 | 7.39 | -65.8% |
| PusulaV2NoBtcScore1 | IOTA/USDT:USDT | 9 | 0.46 | 4.16 | -66.9% |
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

## Grafikler
![PusulaV2NoBtcScore1_sermaye.png](PusulaV2NoBtcScore1_sermaye.png)
![PusulaV2NoBtcScore1_R_dagilimi.png](PusulaV2NoBtcScore1_R_dagilimi.png)
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
