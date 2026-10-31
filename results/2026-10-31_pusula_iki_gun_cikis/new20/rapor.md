# PusulaV2NoBe vs PusulaV2NoBeExit2d — iki_gun_cikis — 2026-10-31

## Özet
- **PusulaV2NoBe**: 193 işlem, işlem başına ortalama **0.61R** (maliyet ve funding dahil), net getiri 134.2%, en büyük düşüş 22.6%.
- **PusulaV2NoBeExit2d**: 176 işlem, işlem başına ortalama **0.65R** (maliyet ve funding dahil), net getiri 127.4%, en büyük düşüş 25.5%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeExit2d | Al-tut |
|---|---|---|---|
| Net getiri | 134.2% | 127.4% | 194.7% |
| Max drawdown | 22.6% | 25.5% | 97.6% |
| Profit factor | 1.53 | 1.50 | — |
| Ortalama R | 0.61 | 0.65 | — |
| İşlem sayısı | 193 | 176 | — |
| Winrate | 23.3% | 23.3% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 193 | 0.61 | 117.72 | 1.53 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeExit2d | long | 176 | 0.65 | 114.53 | 1.50 |
| PusulaV2NoBeExit2d | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 53.9% | 0.5% | 0.0% | 0.0% | 45.6% | 6.3% | -3768.94 |
| PusulaV2NoBeExit2d | 67.6% | 0.6% | 0.0% | 0.0% | 31.8% | 5.4% | -4018.71 |

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
| PusulaV2NoBeExit2d | FIL/USDT:USDT | 6 | 6.44 | 38.63 | -97.9% |
| PusulaV2NoBeExit2d | UNI/USDT:USDT | 19 | 1.04 | 19.80 | 62.4% |
| PusulaV2NoBeExit2d | AAVE/USDT:USDT | 13 | -0.70 | -9.15 | 286.5% |
| PusulaV2NoBeExit2d | NEAR/USDT:USDT | 10 | 1.04 | 10.36 | 373.4% |
| PusulaV2NoBeExit2d | ALGO/USDT:USDT | 11 | 1.86 | 20.50 | -47.9% |
| PusulaV2NoBeExit2d | XTZ/USDT:USDT | 13 | 0.35 | 4.53 | -84.3% |
| PusulaV2NoBeExit2d | THETA/USDT:USDT | 8 | 2.68 | 21.46 | -48.0% |
| PusulaV2NoBeExit2d | VET/USDT:USDT | 11 | 1.84 | 20.20 | 139.2% |
| PusulaV2NoBeExit2d | ICP/USDT:USDT | 4 | 0.25 | 0.99 | -99.3% |
| PusulaV2NoBeExit2d | SAND/USDT:USDT | 4 | -1.07 | -4.26 | -54.0% |
| PusulaV2NoBeExit2d | MANA/USDT:USDT | 7 | -0.57 | -3.99 | -91.4% |
| PusulaV2NoBeExit2d | AXS/USDT:USDT | 2 | 2.61 | 5.22 | 136.4% |
| PusulaV2NoBeExit2d | EGLD/USDT:USDT | 8 | -0.51 | -4.06 | -65.7% |
| PusulaV2NoBeExit2d | HBAR/USDT:USDT | 6 | -0.64 | -3.86 | -68.6% |
| PusulaV2NoBeExit2d | CHZ/USDT:USDT | 6 | -0.68 | -4.11 | -26.0% |
| PusulaV2NoBeExit2d | ENJ/USDT:USDT | 4 | -0.07 | -0.28 | -83.5% |
| PusulaV2NoBeExit2d | ZEC/USDT:USDT | 11 | -0.02 | -0.25 | 3815.4% |
| PusulaV2NoBeExit2d | DASH/USDT:USDT | 15 | -0.69 | -10.35 | -19.1% |
| PusulaV2NoBeExit2d | NEO/USDT:USDT | 11 | 0.76 | 8.33 | -65.8% |
| PusulaV2NoBeExit2d | IOTA/USDT:USDT | 7 | 0.69 | 4.85 | -66.9% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeExit2d_sermaye.png](PusulaV2NoBeExit2d_sermaye.png)
![PusulaV2NoBeExit2d_R_dagilimi.png](PusulaV2NoBeExit2d_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
