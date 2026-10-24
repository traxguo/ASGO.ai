# PusulaV2NoBe vs PusulaV2NoBeMature — olgun_trend — 2026-10-24

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeMature**: 200 işlem, işlem başına ortalama **1.57R** (maliyet ve funding dahil), net getiri 891.6%, en büyük düşüş 20.1%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeMature | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 891.6% | 931.5% |
| Max drawdown | 23.7% | 20.1% | 89.2% |
| Profit factor | 2.06 | 2.21 | — |
| Ortalama R | 1.35 | 1.57 | — |
| İşlem sayısı | 230 | 200 | — |
| Winrate | 32.2% | 33.0% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeMature | long | 200 | 1.57 | 314.97 | 2.21 |
| PusulaV2NoBeMature | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeMature | 41.5% | 0.0% | 0.0% | 0.0% | 58.5% | 5.2% | -14425.89 |

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
| PusulaV2NoBeMature | BTC/USDT:USDT | 34 | 1.35 | 45.83 | 841.1% |
| PusulaV2NoBeMature | ETH/USDT:USDT | 34 | 0.65 | 21.99 | 1027.8% |
| PusulaV2NoBeMature | SOL/USDT:USDT | 13 | 4.06 | 52.74 | 3424.0% |
| PusulaV2NoBeMature | XRP/USDT:USDT | 8 | -0.54 | -4.29 | 531.4% |
| PusulaV2NoBeMature | BNB/USDT:USDT | 35 | 1.14 | 39.76 | 3739.0% |
| PusulaV2NoBeMature | DOGE/USDT:USDT | 3 | 4.95 | 14.86 | 2460.3% |
| PusulaV2NoBeMature | ADA/USDT:USDT | 8 | 0.96 | 7.64 | 409.9% |
| PusulaV2NoBeMature | LINK/USDT:USDT | 7 | 2.02 | 14.16 | 224.4% |
| PusulaV2NoBeMature | LTC/USDT:USDT | 9 | 0.13 | 1.20 | 11.3% |
| PusulaV2NoBeMature | DOT/USDT:USDT | 1 | -1.04 | -1.04 | -63.4% |
| PusulaV2NoBeMature | AVAX/USDT:USDT | 3 | 0.76 | 2.27 | 171.8% |
| PusulaV2NoBeMature | TRX/USDT:USDT | 32 | 0.92 | 29.45 | 1881.6% |
| PusulaV2NoBeMature | ATOM/USDT:USDT | 3 | -0.81 | -2.44 | -51.5% |
| PusulaV2NoBeMature | BCH/USDT:USDT | 6 | -0.48 | -2.90 | -7.2% |
| PusulaV2NoBeMature | ETC/USDT:USDT | 3 | 32.26 | 96.79 | 14.6% |
| PusulaV2NoBeMature | XLM/USDT:USDT | 1 | -1.05 | -1.05 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeMature_sermaye.png](PusulaV2NoBeMature_sermaye.png)
![PusulaV2NoBeMature_R_dagilimi.png](PusulaV2NoBeMature_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
