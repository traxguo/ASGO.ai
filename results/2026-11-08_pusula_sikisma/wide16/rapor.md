# PusulaV2NoBe vs PusulaV2NoBeSqueeze — sikisma — 2026-11-08

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeSqueeze**: 215 işlem, işlem başına ortalama **1.42R** (maliyet ve funding dahil), net getiri 741.0%, en büyük düşüş 30.8%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeSqueeze | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 741.0% | 931.5% |
| Max drawdown | 23.7% | 30.8% | 89.2% |
| Profit factor | 2.06 | 1.89 | — |
| Ortalama R | 1.35 | 1.42 | — |
| İşlem sayısı | 230 | 215 | — |
| Winrate | 32.2% | 28.4% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeSqueeze | long | 215 | 1.42 | 305.52 | 1.89 |
| PusulaV2NoBeSqueeze | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeSqueeze | 47.0% | 0.0% | 0.0% | 0.0% | 53.0% | 4.9% | -13272.95 |

## Coin bazında
| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |
|---|---|---|---|---|---|
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
| PusulaV2NoBeSqueeze | BTC/USDT:USDT | 40 | 1.39 | 55.76 | 841.1% |
| PusulaV2NoBeSqueeze | ETH/USDT:USDT | 31 | 0.17 | 5.33 | 1027.8% |
| PusulaV2NoBeSqueeze | SOL/USDT:USDT | 14 | 3.90 | 54.56 | 3424.0% |
| PusulaV2NoBeSqueeze | XRP/USDT:USDT | 11 | 2.56 | 28.11 | 531.4% |
| PusulaV2NoBeSqueeze | BNB/USDT:USDT | 26 | 1.72 | 44.73 | 3739.0% |
| PusulaV2NoBeSqueeze | DOGE/USDT:USDT | 5 | -0.57 | -2.87 | 2460.3% |
| PusulaV2NoBeSqueeze | ADA/USDT:USDT | 8 | 0.83 | 6.61 | 409.9% |
| PusulaV2NoBeSqueeze | LINK/USDT:USDT | 8 | 0.37 | 2.99 | 224.4% |
| PusulaV2NoBeSqueeze | LTC/USDT:USDT | 13 | -0.34 | -4.43 | 11.3% |
| PusulaV2NoBeSqueeze | DOT/USDT:USDT | 5 | -0.84 | -4.20 | -63.4% |
| PusulaV2NoBeSqueeze | AVAX/USDT:USDT | 4 | 0.62 | 2.50 | 171.8% |
| PusulaV2NoBeSqueeze | TRX/USDT:USDT | 30 | 0.86 | 25.95 | 1881.6% |
| PusulaV2NoBeSqueeze | ATOM/USDT:USDT | 2 | -1.13 | -2.25 | -51.5% |
| PusulaV2NoBeSqueeze | BCH/USDT:USDT | 7 | 0.38 | 2.69 | -7.2% |
| PusulaV2NoBeSqueeze | ETC/USDT:USDT | 5 | 19.11 | 95.56 | 14.6% |
| PusulaV2NoBeSqueeze | XLM/USDT:USDT | 6 | -0.92 | -5.53 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeSqueeze_sermaye.png](PusulaV2NoBeSqueeze_sermaye.png)
![PusulaV2NoBeSqueeze_R_dagilimi.png](PusulaV2NoBeSqueeze_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
