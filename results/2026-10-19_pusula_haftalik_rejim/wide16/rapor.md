# PusulaV2NoBe vs PusulaV2NoBeWeekly — haftalik_rejim — 2026-10-19

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeWeekly**: 209 işlem, işlem başına ortalama **0.86R** (maliyet ve funding dahil), net getiri 308.3%, en büyük düşüş 21.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeWeekly | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 308.3% | 931.5% |
| Max drawdown | 23.7% | 21.9% | 89.2% |
| Profit factor | 2.06 | 1.73 | — |
| Ortalama R | 1.35 | 0.86 | — |
| İşlem sayısı | 230 | 209 | — |
| Winrate | 32.2% | 30.1% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeWeekly | long | 209 | 0.86 | 179.54 | 1.73 |
| PusulaV2NoBeWeekly | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeWeekly | 40.7% | 0.0% | 0.0% | 0.0% | 59.3% | 5.9% | -5873.75 |

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
| PusulaV2NoBeWeekly | BTC/USDT:USDT | 40 | 0.77 | 30.64 | 841.1% |
| PusulaV2NoBeWeekly | ETH/USDT:USDT | 25 | 0.32 | 8.02 | 1027.8% |
| PusulaV2NoBeWeekly | SOL/USDT:USDT | 18 | -0.17 | -3.06 | 3424.0% |
| PusulaV2NoBeWeekly | XRP/USDT:USDT | 10 | -0.69 | -6.94 | 531.4% |
| PusulaV2NoBeWeekly | BNB/USDT:USDT | 35 | 1.67 | 58.59 | 3739.0% |
| PusulaV2NoBeWeekly | DOGE/USDT:USDT | 1 | 1.51 | 1.51 | 2460.3% |
| PusulaV2NoBeWeekly | ADA/USDT:USDT | 6 | -0.01 | -0.08 | 409.9% |
| PusulaV2NoBeWeekly | LINK/USDT:USDT | 4 | 0.17 | 0.68 | 224.4% |
| PusulaV2NoBeWeekly | LTC/USDT:USDT | 11 | -0.40 | -4.35 | 11.3% |
| PusulaV2NoBeWeekly | DOT/USDT:USDT | 0 | — | 0.00 | -63.4% |
| PusulaV2NoBeWeekly | AVAX/USDT:USDT | 2 | -1.04 | -2.07 | 171.8% |
| PusulaV2NoBeWeekly | TRX/USDT:USDT | 36 | 0.85 | 30.52 | 1881.6% |
| PusulaV2NoBeWeekly | ATOM/USDT:USDT | 1 | -1.15 | -1.15 | -51.5% |
| PusulaV2NoBeWeekly | BCH/USDT:USDT | 11 | 0.96 | 10.54 | -7.2% |
| PusulaV2NoBeWeekly | ETC/USDT:USDT | 5 | 9.97 | 49.85 | 14.6% |
| PusulaV2NoBeWeekly | XLM/USDT:USDT | 4 | 1.71 | 6.83 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeWeekly_sermaye.png](PusulaV2NoBeWeekly_sermaye.png)
![PusulaV2NoBeWeekly_R_dagilimi.png](PusulaV2NoBeWeekly_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
