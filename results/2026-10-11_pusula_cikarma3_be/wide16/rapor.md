# PusulaV2NoBtcScore1 vs PusulaV2NoBe — cikarma3_wide16 — 2026-10-11

## Özet
- **PusulaV2NoBtcScore1**: 238 işlem, işlem başına ortalama **1.30R** (maliyet ve funding dahil), net getiri 824.2%, en büyük düşüş 21.5%.
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
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
| Metrik | PusulaV2NoBtcScore1 | PusulaV2NoBe | Al-tut |
|---|---|---|---|
| Net getiri | 824.2% | 827.3% | 931.5% |
| Max drawdown | 21.5% | 23.7% | 89.2% |
| Profit factor | 2.21 | 2.06 | — |
| Ortalama R | 1.30 | 1.35 | — |
| İşlem sayısı | 238 | 230 | — |
| Winrate | 28.2% | 32.2% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBtcScore1 | long | 238 | 1.30 | 309.88 | 2.21 |
| PusulaV2NoBtcScore1 | short | 0 | — | 0.00 | — |
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBtcScore1 | 37.4% | 12.2% | 0.0% | 0.0% | 50.4% | 5.9% | -13293.22 |
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
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
| PusulaV2NoBe | BTC/USDT:USDT | 42 | 1.39 | 58.58 | 841.1% |
| PusulaV2NoBe | ETH/USDT:USDT | 32 | 0.58 | 18.52 | 1027.8% |
| PusulaV2NoBe | SOL/USDT:USDT | 12 | 4.96 | 59.49 | 3424.0% |
| PusulaV2NoBe | XRP/USDT:USDT | 11 | 1.00 | 10.98 | 531.4% |
| PusulaV2NoBe | BNB/USDT:USDT | 37 | 1.02 | 37.62 | 3739.0% |
| PusulaV2NoBe | DOGE/USDT:USDT | 2 | -1.05 | -2.10 | 2460.3% |
| PusulaV2NoBe | ADA/USDT:USDT | 7 | 1.04 | 7.29 | 409.9% |
| PusulaV2NoBe | LINK/USDT:USDT | 9 | 0.14 | 1.28 | 224.4% |
| PusulaV2NoBe | LTC/USDT:USDT | 13 | -0.19 | -2.53 | 11.3% |
| PusulaV2NoBe | DOT/USDT:USDT | 2 | -1.07 | -2.15 | -63.4% |
| PusulaV2NoBe | AVAX/USDT:USDT | 4 | 0.42 | 1.67 | 171.8% |
| PusulaV2NoBe | TRX/USDT:USDT | 33 | 0.86 | 28.32 | 1881.6% |
| PusulaV2NoBe | ATOM/USDT:USDT | 5 | -0.02 | -0.11 | -51.5% |
| PusulaV2NoBe | BCH/USDT:USDT | 11 | -0.00 | -0.04 | -7.2% |
| PusulaV2NoBe | ETC/USDT:USDT | 5 | 19.42 | 97.11 | 14.6% |
| PusulaV2NoBe | XLM/USDT:USDT | 5 | -0.53 | -2.66 | 289.8% |

## Grafikler
![PusulaV2NoBtcScore1_sermaye.png](PusulaV2NoBtcScore1_sermaye.png)
![PusulaV2NoBtcScore1_R_dagilimi.png](PusulaV2NoBtcScore1_R_dagilimi.png)
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
