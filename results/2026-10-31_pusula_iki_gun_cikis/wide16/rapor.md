# PusulaV2NoBe vs PusulaV2NoBeExit2d — iki_gun_cikis — 2026-10-31

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeExit2d**: 190 işlem, işlem başına ortalama **1.93R** (maliyet ve funding dahil), net getiri 1160.9%, en büyük düşüş 24.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeExit2d | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 1160.9% | 931.5% |
| Max drawdown | 23.7% | 24.9% | 89.2% |
| Profit factor | 2.06 | 2.05 | — |
| Ortalama R | 1.35 | 1.93 | — |
| İşlem sayısı | 230 | 190 | — |
| Winrate | 32.2% | 31.6% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeExit2d | long | 190 | 1.93 | 366.32 | 2.05 |
| PusulaV2NoBeExit2d | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeExit2d | 54.7% | 0.0% | 0.0% | 0.0% | 45.3% | 4.5% | -22769.74 |

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
| PusulaV2NoBeExit2d | BTC/USDT:USDT | 38 | 2.04 | 77.59 | 841.1% |
| PusulaV2NoBeExit2d | ETH/USDT:USDT | 26 | 1.21 | 31.47 | 1027.8% |
| PusulaV2NoBeExit2d | SOL/USDT:USDT | 11 | 4.75 | 52.29 | 3424.0% |
| PusulaV2NoBeExit2d | XRP/USDT:USDT | 10 | 0.32 | 3.22 | 531.4% |
| PusulaV2NoBeExit2d | BNB/USDT:USDT | 29 | 1.44 | 41.80 | 3739.0% |
| PusulaV2NoBeExit2d | DOGE/USDT:USDT | 2 | -1.05 | -2.10 | 2460.3% |
| PusulaV2NoBeExit2d | ADA/USDT:USDT | 5 | 5.06 | 25.30 | 409.9% |
| PusulaV2NoBeExit2d | LINK/USDT:USDT | 6 | 5.28 | 31.69 | 224.4% |
| PusulaV2NoBeExit2d | LTC/USDT:USDT | 11 | -0.22 | -2.45 | 11.3% |
| PusulaV2NoBeExit2d | DOT/USDT:USDT | 2 | -1.07 | -2.15 | -63.4% |
| PusulaV2NoBeExit2d | AVAX/USDT:USDT | 3 | 0.75 | 2.25 | 171.8% |
| PusulaV2NoBeExit2d | TRX/USDT:USDT | 27 | 0.74 | 20.01 | 1881.6% |
| PusulaV2NoBeExit2d | ATOM/USDT:USDT | 4 | -1.08 | -4.31 | -51.5% |
| PusulaV2NoBeExit2d | BCH/USDT:USDT | 9 | 0.06 | 0.55 | -7.2% |
| PusulaV2NoBeExit2d | ETC/USDT:USDT | 3 | 31.16 | 93.48 | 14.6% |
| PusulaV2NoBeExit2d | XLM/USDT:USDT | 4 | -0.59 | -2.34 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeExit2d_sermaye.png](PusulaV2NoBeExit2d_sermaye.png)
![PusulaV2NoBeExit2d_R_dagilimi.png](PusulaV2NoBeExit2d_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
