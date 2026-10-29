# PusulaV2NoBe vs PusulaV2NoBeNoScore — puansiz — 2026-10-29

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeNoScore**: 255 işlem, işlem başına ortalama **1.53R** (maliyet ve funding dahil), net getiri 1695.5%, en büyük düşüş 25.5%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeNoScore | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 1695.5% | 931.5% |
| Max drawdown | 23.7% | 25.5% | 89.2% |
| Profit factor | 2.06 | 2.45 | — |
| Ortalama R | 1.35 | 1.53 | — |
| İşlem sayısı | 230 | 255 | — |
| Winrate | 32.2% | 33.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeNoScore | long | 255 | 1.53 | 388.93 | 2.45 |
| PusulaV2NoBeNoScore | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeNoScore | 37.3% | 0.0% | 0.0% | 0.0% | 62.7% | 7.6% | -16499.24 |

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
| PusulaV2NoBeNoScore | BTC/USDT:USDT | 40 | 0.92 | 36.97 | 841.1% |
| PusulaV2NoBeNoScore | ETH/USDT:USDT | 29 | 0.58 | 16.86 | 1027.8% |
| PusulaV2NoBeNoScore | SOL/USDT:USDT | 10 | 5.41 | 54.08 | 3424.0% |
| PusulaV2NoBeNoScore | XRP/USDT:USDT | 14 | 0.33 | 4.56 | 531.4% |
| PusulaV2NoBeNoScore | BNB/USDT:USDT | 38 | 1.32 | 50.29 | 3739.0% |
| PusulaV2NoBeNoScore | DOGE/USDT:USDT | 5 | -0.33 | -1.63 | 2460.3% |
| PusulaV2NoBeNoScore | ADA/USDT:USDT | 10 | 0.39 | 3.95 | 409.9% |
| PusulaV2NoBeNoScore | LINK/USDT:USDT | 8 | 1.71 | 13.65 | 224.4% |
| PusulaV2NoBeNoScore | LTC/USDT:USDT | 16 | -0.13 | -2.04 | 11.3% |
| PusulaV2NoBeNoScore | DOT/USDT:USDT | 4 | -0.09 | -0.38 | -63.4% |
| PusulaV2NoBeNoScore | AVAX/USDT:USDT | 2 | 1.92 | 3.84 | 171.8% |
| PusulaV2NoBeNoScore | TRX/USDT:USDT | 38 | 0.76 | 28.70 | 1881.6% |
| PusulaV2NoBeNoScore | ATOM/USDT:USDT | 9 | 0.70 | 6.32 | -51.5% |
| PusulaV2NoBeNoScore | BCH/USDT:USDT | 13 | 2.33 | 30.30 | -7.2% |
| PusulaV2NoBeNoScore | ETC/USDT:USDT | 10 | 9.34 | 93.44 | 14.6% |
| PusulaV2NoBeNoScore | XLM/USDT:USDT | 9 | 5.56 | 50.03 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeNoScore_sermaye.png](PusulaV2NoBeNoScore_sermaye.png)
![PusulaV2NoBeNoScore_R_dagilimi.png](PusulaV2NoBeNoScore_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
