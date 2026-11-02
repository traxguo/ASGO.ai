# PusulaV2NoBe vs PusulaV2NoBeHalfEma50 — yarim_cikis — 2026-11-02

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeHalfEma50**: 158 işlem, işlem başına ortalama **2.31R** (maliyet ve funding dahil), net getiri 732.9%, en büyük düşüş 19.9%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeHalfEma50 | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 732.9% | 931.5% |
| Max drawdown | 23.7% | 19.9% | 89.2% |
| Profit factor | 2.06 | 2.21 | — |
| Ortalama R | 1.35 | 2.31 | — |
| İşlem sayısı | 230 | 158 | — |
| Winrate | 32.2% | 26.6% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeHalfEma50 | long | 158 | 2.31 | 364.75 | 2.21 |
| PusulaV2NoBeHalfEma50 | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeHalfEma50 | 60.1% | 0.0% | 0.0% | 0.0% | 39.9% | 5.4% | -12490.04 |

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
| PusulaV2NoBeHalfEma50 | BTC/USDT:USDT | 28 | 2.22 | 62.09 | 841.1% |
| PusulaV2NoBeHalfEma50 | ETH/USDT:USDT | 18 | 0.70 | 12.61 | 1027.8% |
| PusulaV2NoBeHalfEma50 | SOL/USDT:USDT | 11 | 5.34 | 58.77 | 3424.0% |
| PusulaV2NoBeHalfEma50 | XRP/USDT:USDT | 8 | -0.20 | -1.60 | 531.4% |
| PusulaV2NoBeHalfEma50 | BNB/USDT:USDT | 23 | 4.01 | 92.18 | 3739.0% |
| PusulaV2NoBeHalfEma50 | DOGE/USDT:USDT | 2 | -1.05 | -2.10 | 2460.3% |
| PusulaV2NoBeHalfEma50 | ADA/USDT:USDT | 4 | 1.79 | 7.16 | 409.9% |
| PusulaV2NoBeHalfEma50 | LINK/USDT:USDT | 7 | 2.80 | 19.58 | 224.4% |
| PusulaV2NoBeHalfEma50 | LTC/USDT:USDT | 10 | 0.57 | 5.65 | 11.3% |
| PusulaV2NoBeHalfEma50 | DOT/USDT:USDT | 3 | -0.97 | -2.91 | -63.4% |
| PusulaV2NoBeHalfEma50 | AVAX/USDT:USDT | 2 | -0.93 | -1.87 | 171.8% |
| PusulaV2NoBeHalfEma50 | TRX/USDT:USDT | 23 | 1.16 | 26.75 | 1881.6% |
| PusulaV2NoBeHalfEma50 | ATOM/USDT:USDT | 3 | -1.09 | -3.28 | -51.5% |
| PusulaV2NoBeHalfEma50 | BCH/USDT:USDT | 9 | 0.10 | 0.86 | -7.2% |
| PusulaV2NoBeHalfEma50 | ETC/USDT:USDT | 3 | 30.90 | 92.69 | 14.6% |
| PusulaV2NoBeHalfEma50 | XLM/USDT:USDT | 4 | -0.46 | -1.82 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeHalfEma50_sermaye.png](PusulaV2NoBeHalfEma50_sermaye.png)
![PusulaV2NoBeHalfEma50_R_dagilimi.png](PusulaV2NoBeHalfEma50_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
