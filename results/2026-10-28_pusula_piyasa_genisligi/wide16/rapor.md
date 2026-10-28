# PusulaV2NoBe vs PusulaV2NoBeBreadth — piyasa_genisligi — 2026-10-28

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeBreadth**: 208 işlem, işlem başına ortalama **1.08R** (maliyet ve funding dahil), net getiri 399.2%, en büyük düşüş 28.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeBreadth | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 399.2% | 931.5% |
| Max drawdown | 23.7% | 28.9% | 89.2% |
| Profit factor | 2.06 | 1.73 | — |
| Ortalama R | 1.35 | 1.08 | — |
| İşlem sayısı | 230 | 208 | — |
| Winrate | 32.2% | 31.7% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeBreadth | long | 208 | 1.08 | 224.58 | 1.73 |
| PusulaV2NoBeBreadth | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeBreadth | 49.0% | 0.0% | 0.0% | 0.0% | 51.0% | 6.7% | -10395.87 |

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
| PusulaV2NoBeBreadth | BTC/USDT:USDT | 36 | 0.68 | 24.50 | 841.1% |
| PusulaV2NoBeBreadth | ETH/USDT:USDT | 28 | 0.63 | 17.54 | 1027.8% |
| PusulaV2NoBeBreadth | SOL/USDT:USDT | 9 | -0.12 | -1.12 | 3424.0% |
| PusulaV2NoBeBreadth | XRP/USDT:USDT | 11 | 2.24 | 24.62 | 531.4% |
| PusulaV2NoBeBreadth | BNB/USDT:USDT | 33 | 1.27 | 41.77 | 3739.0% |
| PusulaV2NoBeBreadth | DOGE/USDT:USDT | 5 | -0.49 | -2.43 | 2460.3% |
| PusulaV2NoBeBreadth | ADA/USDT:USDT | 7 | 0.95 | 6.64 | 409.9% |
| PusulaV2NoBeBreadth | LINK/USDT:USDT | 9 | 0.58 | 5.18 | 224.4% |
| PusulaV2NoBeBreadth | LTC/USDT:USDT | 15 | -0.33 | -5.01 | 11.3% |
| PusulaV2NoBeBreadth | DOT/USDT:USDT | 2 | -1.07 | -2.15 | -63.4% |
| PusulaV2NoBeBreadth | AVAX/USDT:USDT | 5 | 0.12 | 0.61 | 171.8% |
| PusulaV2NoBeBreadth | TRX/USDT:USDT | 25 | 0.99 | 24.83 | 1881.6% |
| PusulaV2NoBeBreadth | ATOM/USDT:USDT | 5 | -0.02 | -0.11 | -51.5% |
| PusulaV2NoBeBreadth | BCH/USDT:USDT | 9 | -0.81 | -7.32 | -7.2% |
| PusulaV2NoBeBreadth | ETC/USDT:USDT | 6 | 16.33 | 97.96 | 14.6% |
| PusulaV2NoBeBreadth | XLM/USDT:USDT | 3 | -0.31 | -0.92 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeBreadth_sermaye.png](PusulaV2NoBeBreadth_sermaye.png)
![PusulaV2NoBeBreadth_R_dagilimi.png](PusulaV2NoBeBreadth_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
