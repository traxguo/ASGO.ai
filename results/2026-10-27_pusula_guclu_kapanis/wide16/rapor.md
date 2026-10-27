# PusulaV2NoBe vs PusulaV2NoBeStrongClose — guclu_kapanis — 2026-10-27

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeStrongClose**: 224 işlem, işlem başına ortalama **1.18R** (maliyet ve funding dahil), net getiri 583.7%, en büyük düşüş 22.7%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeStrongClose | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 583.7% | 931.5% |
| Max drawdown | 23.7% | 22.7% | 89.2% |
| Profit factor | 2.06 | 2.04 | — |
| Ortalama R | 1.35 | 1.18 | — |
| İşlem sayısı | 230 | 224 | — |
| Winrate | 32.2% | 32.1% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeStrongClose | long | 224 | 1.18 | 263.97 | 2.04 |
| PusulaV2NoBeStrongClose | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeStrongClose | 39.7% | 0.0% | 0.0% | 0.0% | 60.3% | 5.9% | -9224.38 |

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
| PusulaV2NoBeStrongClose | BTC/USDT:USDT | 38 | 0.76 | 28.70 | 841.1% |
| PusulaV2NoBeStrongClose | ETH/USDT:USDT | 34 | 0.17 | 5.92 | 1027.8% |
| PusulaV2NoBeStrongClose | SOL/USDT:USDT | 12 | 4.61 | 55.27 | 3424.0% |
| PusulaV2NoBeStrongClose | XRP/USDT:USDT | 9 | 0.44 | 3.97 | 531.4% |
| PusulaV2NoBeStrongClose | BNB/USDT:USDT | 36 | 1.48 | 53.24 | 3739.0% |
| PusulaV2NoBeStrongClose | DOGE/USDT:USDT | 3 | -1.12 | -3.35 | 2460.3% |
| PusulaV2NoBeStrongClose | ADA/USDT:USDT | 6 | 1.62 | 9.73 | 409.9% |
| PusulaV2NoBeStrongClose | LINK/USDT:USDT | 9 | 0.61 | 5.46 | 224.4% |
| PusulaV2NoBeStrongClose | LTC/USDT:USDT | 16 | -0.18 | -2.90 | 11.3% |
| PusulaV2NoBeStrongClose | DOT/USDT:USDT | 3 | -1.04 | -3.11 | -63.4% |
| PusulaV2NoBeStrongClose | AVAX/USDT:USDT | 4 | 3.06 | 12.25 | 171.8% |
| PusulaV2NoBeStrongClose | TRX/USDT:USDT | 31 | 0.06 | 1.92 | 1881.6% |
| PusulaV2NoBeStrongClose | ATOM/USDT:USDT | 3 | -1.05 | -3.15 | -51.5% |
| PusulaV2NoBeStrongClose | BCH/USDT:USDT | 9 | 0.25 | 2.28 | -7.2% |
| PusulaV2NoBeStrongClose | ETC/USDT:USDT | 5 | 20.16 | 100.78 | 14.6% |
| PusulaV2NoBeStrongClose | XLM/USDT:USDT | 6 | -0.50 | -3.02 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeStrongClose_sermaye.png](PusulaV2NoBeStrongClose_sermaye.png)
![PusulaV2NoBeStrongClose_R_dagilimi.png](PusulaV2NoBeStrongClose_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
