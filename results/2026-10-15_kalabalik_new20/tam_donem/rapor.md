# Kalabalik_B — tam_donem_new20 — 2026-10-15

## Özet
- **Kalabalik_B**: 187 işlem, işlem başına ortalama **-0.02R** (maliyet ve funding dahil), net getiri -5.9%, en büyük düşüş 27.3%.
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
| Metrik | Kalabalik_B | Al-tut |
|---|---|---|
| Net getiri | -5.9% | 194.7% |
| Max drawdown | 27.3% | 97.6% |
| Profit factor | 0.95 | — |
| Ortalama R | -0.02 | — |
| İşlem sayısı | 187 | — |
| Winrate | 33.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| Kalabalik_B | long | 137 | 0.09 | 12.73 | 1.13 |
| Kalabalik_B | short | 50 | -0.32 | -15.86 | 0.55 |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| Kalabalik_B | 66.3% | 0.0% | 17.1% | 16.6% | 0.0% | 9.7% | 160.99 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
| Kalabalik_B | FIL/USDT:USDT | 2 | -1.01 | -2.03 | -97.9% |
| Kalabalik_B | UNI/USDT:USDT | 10 | -0.01 | -0.06 | 62.4% |
| Kalabalik_B | AAVE/USDT:USDT | 6 | -0.03 | -0.20 | 286.5% |
| Kalabalik_B | NEAR/USDT:USDT | 7 | -0.72 | -5.07 | 373.4% |
| Kalabalik_B | ALGO/USDT:USDT | 23 | 0.43 | 9.95 | -47.9% |
| Kalabalik_B | XTZ/USDT:USDT | 11 | 0.61 | 6.70 | -84.3% |
| Kalabalik_B | THETA/USDT:USDT | 9 | 0.53 | 4.79 | -48.0% |
| Kalabalik_B | VET/USDT:USDT | 10 | 0.20 | 2.01 | 139.2% |
| Kalabalik_B | ICP/USDT:USDT | 4 | -1.02 | -4.07 | -99.3% |
| Kalabalik_B | SAND/USDT:USDT | 5 | -0.60 | -3.02 | -54.0% |
| Kalabalik_B | MANA/USDT:USDT | 5 | 0.60 | 3.02 | -91.4% |
| Kalabalik_B | AXS/USDT:USDT | 8 | -0.55 | -4.40 | 136.4% |
| Kalabalik_B | EGLD/USDT:USDT | 9 | 0.52 | 4.67 | -65.7% |
| Kalabalik_B | HBAR/USDT:USDT | 7 | -0.44 | -3.10 | -68.6% |
| Kalabalik_B | CHZ/USDT:USDT | 4 | 0.49 | 1.94 | -26.0% |
| Kalabalik_B | ENJ/USDT:USDT | 8 | 0.02 | 0.17 | -83.5% |
| Kalabalik_B | ZEC/USDT:USDT | 18 | -0.35 | -6.36 | 3815.4% |
| Kalabalik_B | DASH/USDT:USDT | 19 | -0.21 | -3.98 | -19.1% |
| Kalabalik_B | NEO/USDT:USDT | 7 | -0.14 | -0.99 | -65.8% |
| Kalabalik_B | IOTA/USDT:USDT | 15 | -0.21 | -3.12 | -66.9% |

## Grafikler
![Kalabalik_B_sermaye.png](Kalabalik_B_sermaye.png)
![Kalabalik_B_R_dagilimi.png](Kalabalik_B_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
