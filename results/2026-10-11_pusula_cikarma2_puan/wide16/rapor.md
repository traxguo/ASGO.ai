# PusulaV2NoBtcFilter vs PusulaV2NoBtcScore1 — cikarma2_wide16 — 2026-10-11

## Özet
- **PusulaV2NoBtcFilter**: 210 işlem, işlem başına ortalama **1.20R** (maliyet ve funding dahil), net getiri 560.2%, en büyük düşüş 26.1%.
- **PusulaV2NoBtcScore1**: 238 işlem, işlem başına ortalama **1.30R** (maliyet ve funding dahil), net getiri 824.2%, en büyük düşüş 21.5%.
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
| Metrik | PusulaV2NoBtcFilter | PusulaV2NoBtcScore1 | Al-tut |
|---|---|---|---|
| Net getiri | 560.2% | 824.2% | 931.5% |
| Max drawdown | 26.1% | 21.5% | 89.2% |
| Profit factor | 2.07 | 2.21 | — |
| Ortalama R | 1.20 | 1.30 | — |
| İşlem sayısı | 210 | 238 | — |
| Winrate | 30.0% | 28.2% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBtcFilter | long | 210 | 1.20 | 252.90 | 2.07 |
| PusulaV2NoBtcFilter | short | 0 | — | 0.00 | — |
| PusulaV2NoBtcScore1 | long | 238 | 1.30 | 309.88 | 2.21 |
| PusulaV2NoBtcScore1 | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBtcFilter | 37.6% | 11.9% | 0.0% | 0.0% | 50.5% | 5.8% | -10419.59 |
| PusulaV2NoBtcScore1 | 37.4% | 12.2% | 0.0% | 0.0% | 50.4% | 5.9% | -13293.22 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
| PusulaV2NoBtcFilter | BTC/USDT:USDT | 36 | 1.47 | 52.88 | 841.1% |
| PusulaV2NoBtcFilter | ETH/USDT:USDT | 30 | 0.88 | 26.30 | 1027.8% |
| PusulaV2NoBtcFilter | SOL/USDT:USDT | 8 | -0.37 | -2.98 | 3424.0% |
| PusulaV2NoBtcFilter | XRP/USDT:USDT | 7 | 0.20 | 1.38 | 531.4% |
| PusulaV2NoBtcFilter | BNB/USDT:USDT | 41 | 0.95 | 38.90 | 3739.0% |
| PusulaV2NoBtcFilter | DOGE/USDT:USDT | 4 | -0.04 | -0.17 | 2460.3% |
| PusulaV2NoBtcFilter | ADA/USDT:USDT | 5 | 2.72 | 13.58 | 409.9% |
| PusulaV2NoBtcFilter | LINK/USDT:USDT | 7 | 0.49 | 3.42 | 224.4% |
| PusulaV2NoBtcFilter | LTC/USDT:USDT | 14 | -0.28 | -3.92 | 11.3% |
| PusulaV2NoBtcFilter | DOT/USDT:USDT | 2 | -0.54 | -1.08 | -63.4% |
| PusulaV2NoBtcFilter | AVAX/USDT:USDT | 5 | 0.03 | 0.17 | 171.8% |
| PusulaV2NoBtcFilter | TRX/USDT:USDT | 34 | 0.84 | 28.39 | 1881.6% |
| PusulaV2NoBtcFilter | ATOM/USDT:USDT | 2 | -1.04 | -2.07 | -51.5% |
| PusulaV2NoBtcFilter | BCH/USDT:USDT | 8 | 0.35 | 2.80 | -7.2% |
| PusulaV2NoBtcFilter | ETC/USDT:USDT | 3 | 32.63 | 97.89 | 14.6% |
| PusulaV2NoBtcFilter | XLM/USDT:USDT | 4 | -0.65 | -2.59 | 289.8% |
| PusulaV2NoBtcScore1 | BTC/USDT:USDT | 42 | 1.46 | 61.37 | 841.1% |
| PusulaV2NoBtcScore1 | ETH/USDT:USDT | 32 | 0.56 | 18.00 | 1027.8% |
| PusulaV2NoBtcScore1 | SOL/USDT:USDT | 12 | 4.89 | 58.74 | 3424.0% |
| PusulaV2NoBtcScore1 | XRP/USDT:USDT | 11 | 1.02 | 11.20 | 531.4% |
| PusulaV2NoBtcScore1 | BNB/USDT:USDT | 40 | 0.84 | 33.78 | 3739.0% |
| PusulaV2NoBtcScore1 | DOGE/USDT:USDT | 2 | -0.54 | -1.08 | 2460.3% |
| PusulaV2NoBtcScore1 | ADA/USDT:USDT | 7 | 1.19 | 8.31 | 409.9% |
| PusulaV2NoBtcScore1 | LINK/USDT:USDT | 11 | -0.08 | -0.90 | 224.4% |
| PusulaV2NoBtcScore1 | LTC/USDT:USDT | 13 | -0.19 | -2.53 | 11.3% |
| PusulaV2NoBtcScore1 | DOT/USDT:USDT | 3 | -0.71 | -2.13 | -63.4% |
| PusulaV2NoBtcScore1 | AVAX/USDT:USDT | 4 | 0.42 | 1.67 | 171.8% |
| PusulaV2NoBtcScore1 | TRX/USDT:USDT | 34 | 0.83 | 28.32 | 1881.6% |
| PusulaV2NoBtcScore1 | ATOM/USDT:USDT | 5 | -0.02 | -0.11 | -51.5% |
| PusulaV2NoBtcScore1 | BCH/USDT:USDT | 11 | 0.10 | 1.14 | -7.2% |
| PusulaV2NoBtcScore1 | ETC/USDT:USDT | 6 | 15.95 | 95.71 | 14.6% |
| PusulaV2NoBtcScore1 | XLM/USDT:USDT | 5 | -0.33 | -1.63 | 289.8% |

## Grafikler
![PusulaV2NoBtcFilter_sermaye.png](PusulaV2NoBtcFilter_sermaye.png)
![PusulaV2NoBtcFilter_R_dagilimi.png](PusulaV2NoBtcFilter_R_dagilimi.png)
![PusulaV2NoBtcScore1_sermaye.png](PusulaV2NoBtcScore1_sermaye.png)
![PusulaV2NoBtcScore1_R_dagilimi.png](PusulaV2NoBtcScore1_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
