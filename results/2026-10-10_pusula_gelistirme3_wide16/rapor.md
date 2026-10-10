# PusulaV2 vs PusulaV2Vol vs PusulaV2Time — tur3_wide16 — 2026-10-10

## Özet
- **PusulaV2**: 210 işlem, işlem başına ortalama **1.20R** (maliyet ve funding dahil), net getiri 561.0%, en büyük düşüş 26.1%.
- **PusulaV2Vol**: 192 işlem, işlem başına ortalama **1.17R** (maliyet ve funding dahil), net getiri 425.6%, en büyük düşüş 32.9%.
- **PusulaV2Time**: 216 işlem, işlem başına ortalama **1.15R** (maliyet ve funding dahil), net getiri 537.4%, en büyük düşüş 26.3%.
- Aynı dönemde coinleri al-tut (eşit ağırlık): getiri 931.5%, ortalama en büyük düşüş 89.2%.

## Ayarlar
- Dönem: 2020-03-07 16:00:00 → 2026-10-01 00:00:00
- Coinler: BTC/USDT:USDT, ETH/USDT:USDT, SOL/USDT:USDT, XRP/USDT:USDT, BNB/USDT:USDT, DOGE/USDT:USDT, ADA/USDT:USDT, LINK/USDT:USDT, LTC/USDT:USDT, DOT/USDT:USDT, AVAX/USDT:USDT, TRX/USDT:USDT, ATOM/USDT:USDT, BCH/USDT:USDT, ETC/USDT:USDT, XLM/USDT:USDT
- Zaman dilimi: 4h
- Yön: long + short
- Mod: futures / isolated
- Kaldıraç: en fazla 3x, likidasyon stop mesafesinin en az 2 katı uzakta (bölüm 7.6)
- Risk: işlem başına sermayenin %1'i (pozisyon büyüklüğü stop mesafesine göre)
- Maliyet: her emir için %0.05 komisyon + %0.05 kayma (= %0.1), funding geçmiş veriden
- Başlangıç sermayesi: 10000 USDT

## Metrikler
| Metrik | PusulaV2 | PusulaV2Vol | PusulaV2Time | Al-tut |
|---|---|---|---|---|
| Net getiri | 561.0% | 425.6% | 537.4% | 931.5% |
| Max drawdown | 26.1% | 32.9% | 26.3% | 89.2% |
| Profit factor | 2.07 | 1.88 | 2.03 | — |
| Ortalama R | 1.20 | 1.17 | 1.15 | — |
| İşlem sayısı | 210 | 192 | 216 | — |
| Winrate | 30.5% | 24.0% | 29.6% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2 | long | 210 | 1.20 | 253.04 | 2.07 |
| PusulaV2 | short | 0 | — | 0.00 | — |
| PusulaV2Vol | long | 192 | 1.17 | 225.53 | 1.88 |
| PusulaV2Vol | short | 0 | — | 0.00 | — |
| PusulaV2Time | long | 216 | 1.15 | 249.29 | 2.03 |
| PusulaV2Time | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2 | 37.6% | 11.9% | 0.0% | 0.0% | 50.5% | 5.8% | -10431.51 |
| PusulaV2Vol | 45.3% | 10.4% | 0.0% | 0.0% | 44.3% | 7.2% | -9513.43 |
| PusulaV2Time | 38.9% | 11.6% | 0.0% | 0.0% | 49.5% | 5.7% | -10237.97 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
| PusulaV2 | BTC/USDT:USDT | 36 | 1.47 | 52.88 | 841.1% |
| PusulaV2 | ETH/USDT:USDT | 30 | 0.88 | 26.30 | 1027.8% |
| PusulaV2 | SOL/USDT:USDT | 8 | -0.37 | -2.98 | 3424.0% |
| PusulaV2 | XRP/USDT:USDT | 7 | 0.20 | 1.38 | 531.4% |
| PusulaV2 | BNB/USDT:USDT | 41 | 0.95 | 39.04 | 3739.0% |
| PusulaV2 | DOGE/USDT:USDT | 4 | -0.04 | -0.17 | 2460.3% |
| PusulaV2 | ADA/USDT:USDT | 5 | 2.72 | 13.58 | 409.9% |
| PusulaV2 | LINK/USDT:USDT | 7 | 0.49 | 3.42 | 224.4% |
| PusulaV2 | LTC/USDT:USDT | 14 | -0.28 | -3.92 | 11.3% |
| PusulaV2 | DOT/USDT:USDT | 2 | -0.54 | -1.08 | -63.4% |
| PusulaV2 | AVAX/USDT:USDT | 5 | 0.03 | 0.17 | 171.8% |
| PusulaV2 | TRX/USDT:USDT | 34 | 0.84 | 28.39 | 1881.6% |
| PusulaV2 | ATOM/USDT:USDT | 2 | -1.04 | -2.07 | -51.5% |
| PusulaV2 | BCH/USDT:USDT | 8 | 0.35 | 2.80 | -7.2% |
| PusulaV2 | ETC/USDT:USDT | 3 | 32.63 | 97.89 | 14.6% |
| PusulaV2 | XLM/USDT:USDT | 4 | -0.65 | -2.59 | 289.8% |
| PusulaV2Vol | BTC/USDT:USDT | 40 | 1.02 | 40.81 | 841.1% |
| PusulaV2Vol | ETH/USDT:USDT | 32 | 0.43 | 13.81 | 1027.8% |
| PusulaV2Vol | SOL/USDT:USDT | 7 | -0.65 | -4.55 | 3424.0% |
| PusulaV2Vol | XRP/USDT:USDT | 7 | -0.53 | -3.71 | 531.4% |
| PusulaV2Vol | BNB/USDT:USDT | 31 | 1.30 | 40.30 | 3739.0% |
| PusulaV2Vol | DOGE/USDT:USDT | 4 | 4.19 | 16.77 | 2460.3% |
| PusulaV2Vol | ADA/USDT:USDT | 3 | 2.62 | 7.87 | 409.9% |
| PusulaV2Vol | LINK/USDT:USDT | 5 | 1.10 | 5.49 | 224.4% |
| PusulaV2Vol | LTC/USDT:USDT | 11 | 0.15 | 1.63 | 11.3% |
| PusulaV2Vol | DOT/USDT:USDT | 2 | -1.00 | -2.00 | -63.4% |
| PusulaV2Vol | AVAX/USDT:USDT | 6 | 0.18 | 1.08 | 171.8% |
| PusulaV2Vol | TRX/USDT:USDT | 26 | 0.91 | 23.64 | 1881.6% |
| PusulaV2Vol | ATOM/USDT:USDT | 2 | -1.09 | -2.19 | -51.5% |
| PusulaV2Vol | BCH/USDT:USDT | 8 | -0.32 | -2.57 | -7.2% |
| PusulaV2Vol | ETC/USDT:USDT | 3 | 30.85 | 92.54 | 14.6% |
| PusulaV2Vol | XLM/USDT:USDT | 5 | -0.68 | -3.39 | 289.8% |
| PusulaV2Time | BTC/USDT:USDT | 39 | 1.31 | 50.90 | 841.1% |
| PusulaV2Time | ETH/USDT:USDT | 31 | 0.81 | 25.24 | 1027.8% |
| PusulaV2Time | SOL/USDT:USDT | 8 | -0.37 | -2.98 | 3424.0% |
| PusulaV2Time | XRP/USDT:USDT | 7 | 0.20 | 1.38 | 531.4% |
| PusulaV2Time | BNB/USDT:USDT | 41 | 0.96 | 39.32 | 3739.0% |
| PusulaV2Time | DOGE/USDT:USDT | 4 | -0.04 | -0.17 | 2460.3% |
| PusulaV2Time | ADA/USDT:USDT | 6 | 2.26 | 13.54 | 409.9% |
| PusulaV2Time | LINK/USDT:USDT | 7 | 0.49 | 3.42 | 224.4% |
| PusulaV2Time | LTC/USDT:USDT | 14 | -0.28 | -3.92 | 11.3% |
| PusulaV2Time | DOT/USDT:USDT | 2 | -0.54 | -1.08 | -63.4% |
| PusulaV2Time | AVAX/USDT:USDT | 5 | 0.03 | 0.17 | 171.8% |
| PusulaV2Time | TRX/USDT:USDT | 34 | 0.84 | 28.50 | 1881.6% |
| PusulaV2Time | ATOM/USDT:USDT | 2 | -1.04 | -2.07 | -51.5% |
| PusulaV2Time | BCH/USDT:USDT | 8 | 0.35 | 2.80 | -7.2% |
| PusulaV2Time | ETC/USDT:USDT | 4 | 24.21 | 96.83 | 14.6% |
| PusulaV2Time | XLM/USDT:USDT | 4 | -0.65 | -2.59 | 289.8% |

## Grafikler
![PusulaV2_sermaye.png](PusulaV2_sermaye.png)
![PusulaV2_R_dagilimi.png](PusulaV2_R_dagilimi.png)
![PusulaV2Vol_sermaye.png](PusulaV2Vol_sermaye.png)
![PusulaV2Vol_R_dagilimi.png](PusulaV2Vol_R_dagilimi.png)
![PusulaV2Time_sermaye.png](PusulaV2Time_sermaye.png)
![PusulaV2Time_R_dagilimi.png](PusulaV2Time_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
