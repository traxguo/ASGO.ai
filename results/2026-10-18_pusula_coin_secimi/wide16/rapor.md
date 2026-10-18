# PusulaV2NoBe vs PusulaV2NoBeRank vs PusulaV2NoBeRankProbe — coin_secimi — 2026-10-18

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeRank**: 233 işlem, işlem başına ortalama **1.32R** (maliyet ve funding dahil), net getiri 797.0%, en büyük düşüş 25.1%.
- **PusulaV2NoBeRankProbe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeRank | PusulaV2NoBeRankProbe | Al-tut |
|---|---|---|---|---|
| Net getiri | 827.3% | 797.0% | 827.3% | 931.5% |
| Max drawdown | 23.7% | 25.1% | 23.7% | 89.2% |
| Profit factor | 2.06 | 2.03 | 2.06 | — |
| Ortalama R | 1.35 | 1.32 | 1.35 | — |
| İşlem sayısı | 230 | 233 | 230 | — |
| Winrate | 32.2% | 31.3% | 32.2% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeRank | long | 233 | 1.32 | 307.96 | 2.03 |
| PusulaV2NoBeRank | short | 0 | — | 0.00 | — |
| PusulaV2NoBeRankProbe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBeRankProbe | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeRank | 41.6% | 0.0% | 0.0% | 0.0% | 58.4% | 6.0% | -13751.24 |
| PusulaV2NoBeRankProbe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |

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
| PusulaV2NoBeRank | BTC/USDT:USDT | 39 | 1.51 | 59.04 | 841.1% |
| PusulaV2NoBeRank | ETH/USDT:USDT | 30 | 0.67 | 20.24 | 1027.8% |
| PusulaV2NoBeRank | SOL/USDT:USDT | 12 | 4.66 | 55.89 | 3424.0% |
| PusulaV2NoBeRank | XRP/USDT:USDT | 10 | 1.21 | 12.05 | 531.4% |
| PusulaV2NoBeRank | BNB/USDT:USDT | 39 | 1.06 | 41.18 | 3739.0% |
| PusulaV2NoBeRank | DOGE/USDT:USDT | 3 | -1.05 | -3.14 | 2460.3% |
| PusulaV2NoBeRank | ADA/USDT:USDT | 7 | 1.04 | 7.29 | 409.9% |
| PusulaV2NoBeRank | LINK/USDT:USDT | 9 | 0.14 | 1.29 | 224.4% |
| PusulaV2NoBeRank | LTC/USDT:USDT | 15 | -0.26 | -3.84 | 11.3% |
| PusulaV2NoBeRank | DOT/USDT:USDT | 2 | -1.07 | -2.15 | -63.4% |
| PusulaV2NoBeRank | AVAX/USDT:USDT | 4 | 0.31 | 1.23 | 171.8% |
| PusulaV2NoBeRank | TRX/USDT:USDT | 34 | 0.78 | 26.68 | 1881.6% |
| PusulaV2NoBeRank | ATOM/USDT:USDT | 5 | -0.00 | -0.00 | -51.5% |
| PusulaV2NoBeRank | BCH/USDT:USDT | 11 | -0.00 | -0.04 | -7.2% |
| PusulaV2NoBeRank | ETC/USDT:USDT | 5 | 19.42 | 97.11 | 14.6% |
| PusulaV2NoBeRank | XLM/USDT:USDT | 8 | -0.61 | -4.86 | 289.8% |
| PusulaV2NoBeRankProbe | BTC/USDT:USDT | 42 | 1.39 | 58.58 | 841.1% |
| PusulaV2NoBeRankProbe | ETH/USDT:USDT | 32 | 0.58 | 18.52 | 1027.8% |
| PusulaV2NoBeRankProbe | SOL/USDT:USDT | 12 | 4.96 | 59.49 | 3424.0% |
| PusulaV2NoBeRankProbe | XRP/USDT:USDT | 11 | 1.00 | 10.98 | 531.4% |
| PusulaV2NoBeRankProbe | BNB/USDT:USDT | 37 | 1.02 | 37.62 | 3739.0% |
| PusulaV2NoBeRankProbe | DOGE/USDT:USDT | 2 | -1.05 | -2.10 | 2460.3% |
| PusulaV2NoBeRankProbe | ADA/USDT:USDT | 7 | 1.04 | 7.29 | 409.9% |
| PusulaV2NoBeRankProbe | LINK/USDT:USDT | 9 | 0.14 | 1.28 | 224.4% |
| PusulaV2NoBeRankProbe | LTC/USDT:USDT | 13 | -0.19 | -2.53 | 11.3% |
| PusulaV2NoBeRankProbe | DOT/USDT:USDT | 2 | -1.07 | -2.15 | -63.4% |
| PusulaV2NoBeRankProbe | AVAX/USDT:USDT | 4 | 0.42 | 1.67 | 171.8% |
| PusulaV2NoBeRankProbe | TRX/USDT:USDT | 33 | 0.86 | 28.32 | 1881.6% |
| PusulaV2NoBeRankProbe | ATOM/USDT:USDT | 5 | -0.02 | -0.11 | -51.5% |
| PusulaV2NoBeRankProbe | BCH/USDT:USDT | 11 | -0.00 | -0.04 | -7.2% |
| PusulaV2NoBeRankProbe | ETC/USDT:USDT | 5 | 19.42 | 97.11 | 14.6% |
| PusulaV2NoBeRankProbe | XLM/USDT:USDT | 5 | -0.53 | -2.66 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeRank_sermaye.png](PusulaV2NoBeRank_sermaye.png)
![PusulaV2NoBeRank_R_dagilimi.png](PusulaV2NoBeRank_R_dagilimi.png)
![PusulaV2NoBeRankProbe_sermaye.png](PusulaV2NoBeRankProbe_sermaye.png)
![PusulaV2NoBeRankProbe_R_dagilimi.png](PusulaV2NoBeRankProbe_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
