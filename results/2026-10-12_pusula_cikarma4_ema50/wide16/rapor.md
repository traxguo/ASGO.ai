# PusulaV2NoBe vs PusulaV2NoBeEma50 — cikarma4_wide16 — 2026-10-12

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeEma50**: 158 işlem, işlem başına ortalama **3.18R** (maliyet ve funding dahil), net getiri 1237.3%, en büyük düşüş 21.5%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeEma50 | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 1237.3% | 931.5% |
| Max drawdown | 23.7% | 21.5% | 89.2% |
| Profit factor | 2.06 | 2.25 | — |
| Ortalama R | 1.35 | 3.18 | — |
| İşlem sayısı | 230 | 158 | — |
| Winrate | 32.2% | 24.1% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeEma50 | long | 158 | 3.18 | 503.03 | 2.25 |
| PusulaV2NoBeEma50 | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeEma50 | 60.1% | 0.0% | 0.0% | 0.0% | 39.9% | 5.4% | -24360.06 |

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
| PusulaV2NoBeEma50 | BTC/USDT:USDT | 28 | 3.47 | 97.20 | 841.1% |
| PusulaV2NoBeEma50 | ETH/USDT:USDT | 18 | 1.46 | 26.22 | 1027.8% |
| PusulaV2NoBeEma50 | SOL/USDT:USDT | 11 | 5.44 | 59.81 | 3424.0% |
| PusulaV2NoBeEma50 | XRP/USDT:USDT | 8 | -0.41 | -3.28 | 531.4% |
| PusulaV2NoBeEma50 | BNB/USDT:USDT | 23 | 6.19 | 142.45 | 3739.0% |
| PusulaV2NoBeEma50 | DOGE/USDT:USDT | 2 | -1.05 | -2.10 | 2460.3% |
| PusulaV2NoBeEma50 | ADA/USDT:USDT | 4 | 3.72 | 14.89 | 409.9% |
| PusulaV2NoBeEma50 | LINK/USDT:USDT | 7 | 4.43 | 31.03 | 224.4% |
| PusulaV2NoBeEma50 | LTC/USDT:USDT | 10 | 1.43 | 14.32 | 11.3% |
| PusulaV2NoBeEma50 | DOT/USDT:USDT | 3 | -0.97 | -2.91 | -63.4% |
| PusulaV2NoBeEma50 | AVAX/USDT:USDT | 2 | -1.05 | -2.10 | 171.8% |
| PusulaV2NoBeEma50 | TRX/USDT:USDT | 23 | 1.77 | 40.76 | 1881.6% |
| PusulaV2NoBeEma50 | ATOM/USDT:USDT | 3 | -1.09 | -3.28 | -51.5% |
| PusulaV2NoBeEma50 | BCH/USDT:USDT | 9 | 0.02 | 0.21 | -7.2% |
| PusulaV2NoBeEma50 | ETC/USDT:USDT | 3 | 30.63 | 91.88 | 14.6% |
| PusulaV2NoBeEma50 | XLM/USDT:USDT | 4 | -0.52 | -2.07 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeEma50_sermaye.png](PusulaV2NoBeEma50_sermaye.png)
![PusulaV2NoBeEma50_R_dagilimi.png](PusulaV2NoBeEma50_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
