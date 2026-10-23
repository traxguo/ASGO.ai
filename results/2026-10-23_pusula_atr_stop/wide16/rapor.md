# PusulaV2NoBe vs PusulaV2NoBeAtrStop — atr_stop — 2026-10-23

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeAtrStop**: 371 işlem, işlem başına ortalama **1.53R** (maliyet ve funding dahil), net getiri 3266.4%, en büyük düşüş 43.8%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeAtrStop | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 3266.4% | 931.5% |
| Max drawdown | 23.7% | 43.8% | 89.2% |
| Profit factor | 2.06 | 1.64 | — |
| Ortalama R | 1.35 | 1.53 | — |
| İşlem sayısı | 230 | 371 | — |
| Winrate | 32.2% | 21.6% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeAtrStop | long | 371 | 1.53 | 568.10 | 1.64 |
| PusulaV2NoBeAtrStop | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeAtrStop | 73.6% | 0.5% | 0.0% | 0.0% | 25.9% | 5.6% | -65812.17 |

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
| PusulaV2NoBeAtrStop | BTC/USDT:USDT | 49 | 2.66 | 130.15 | 841.1% |
| PusulaV2NoBeAtrStop | ETH/USDT:USDT | 46 | 0.99 | 45.34 | 1027.8% |
| PusulaV2NoBeAtrStop | SOL/USDT:USDT | 28 | 8.11 | 227.07 | 3424.0% |
| PusulaV2NoBeAtrStop | XRP/USDT:USDT | 16 | -0.42 | -6.75 | 531.4% |
| PusulaV2NoBeAtrStop | BNB/USDT:USDT | 46 | 2.84 | 130.77 | 3739.0% |
| PusulaV2NoBeAtrStop | DOGE/USDT:USDT | 19 | 1.45 | 27.57 | 2460.3% |
| PusulaV2NoBeAtrStop | ADA/USDT:USDT | 12 | 1.28 | 15.42 | 409.9% |
| PusulaV2NoBeAtrStop | LINK/USDT:USDT | 22 | 0.15 | 3.27 | 224.4% |
| PusulaV2NoBeAtrStop | LTC/USDT:USDT | 23 | -0.36 | -8.34 | 11.3% |
| PusulaV2NoBeAtrStop | DOT/USDT:USDT | 8 | -0.48 | -3.85 | -63.4% |
| PusulaV2NoBeAtrStop | AVAX/USDT:USDT | 11 | -0.90 | -9.94 | 171.8% |
| PusulaV2NoBeAtrStop | TRX/USDT:USDT | 37 | 1.27 | 47.16 | 1881.6% |
| PusulaV2NoBeAtrStop | ATOM/USDT:USDT | 9 | -0.70 | -6.34 | -51.5% |
| PusulaV2NoBeAtrStop | BCH/USDT:USDT | 22 | -0.38 | -8.34 | -7.2% |
| PusulaV2NoBeAtrStop | ETC/USDT:USDT | 10 | -0.91 | -9.08 | 14.6% |
| PusulaV2NoBeAtrStop | XLM/USDT:USDT | 13 | -0.46 | -6.02 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeAtrStop_sermaye.png](PusulaV2NoBeAtrStop_sermaye.png)
![PusulaV2NoBeAtrStop_R_dagilimi.png](PusulaV2NoBeAtrStop_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
