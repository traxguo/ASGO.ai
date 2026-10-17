# PusulaV2NoBe vs PusulaV2NoBeNoReentry — yeniden_giris — 2026-10-17

## Özet
- **PusulaV2NoBe**: 230 işlem, işlem başına ortalama **1.35R** (maliyet ve funding dahil), net getiri 827.3%, en büyük düşüş 23.7%.
- **PusulaV2NoBeNoReentry**: 194 işlem, işlem başına ortalama **1.03R** (maliyet ve funding dahil), net getiri 308.5%, en büyük düşüş 17.1%.
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
| Metrik | PusulaV2NoBe | PusulaV2NoBeNoReentry | Al-tut |
|---|---|---|---|
| Net getiri | 827.3% | 308.5% | 931.5% |
| Max drawdown | 23.7% | 17.1% | 89.2% |
| Profit factor | 2.06 | 2.02 | — |
| Ortalama R | 1.35 | 1.03 | — |
| İşlem sayısı | 230 | 194 | — |
| Winrate | 32.2% | 25.8% | — |

Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.

## Long / short ayrımı
| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |
|---|---|---|---|---|---|
| PusulaV2NoBe | long | 230 | 1.35 | 311.26 | 2.06 |
| PusulaV2NoBe | short | 0 | — | 0.00 | — |
| PusulaV2NoBeNoReentry | long | 194 | 1.03 | 199.23 | 2.02 |
| PusulaV2NoBeNoReentry | short | 0 | — | 0.00 | — |

## Sinyal istatistikleri
| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |
|---|---|---|---|---|---|---|---|
| PusulaV2NoBe | 41.7% | 0.0% | 0.0% | 0.0% | 58.3% | 5.7% | -14077.15 |
| PusulaV2NoBeNoReentry | 52.6% | 0.0% | 0.0% | 0.0% | 47.4% | 3.5% | -4563.84 |

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
| PusulaV2NoBeNoReentry | BTC/USDT:USDT | 20 | 1.22 | 24.49 | 841.1% |
| PusulaV2NoBeNoReentry | ETH/USDT:USDT | 16 | -0.22 | -3.45 | 1027.8% |
| PusulaV2NoBeNoReentry | SOL/USDT:USDT | 11 | 5.33 | 58.68 | 3424.0% |
| PusulaV2NoBeNoReentry | XRP/USDT:USDT | 15 | 1.78 | 26.64 | 531.4% |
| PusulaV2NoBeNoReentry | BNB/USDT:USDT | 15 | 0.37 | 5.55 | 3739.0% |
| PusulaV2NoBeNoReentry | DOGE/USDT:USDT | 8 | 12.44 | 99.55 | 2460.3% |
| PusulaV2NoBeNoReentry | ADA/USDT:USDT | 8 | -0.06 | -0.50 | 409.9% |
| PusulaV2NoBeNoReentry | LINK/USDT:USDT | 13 | -0.47 | -6.11 | 224.4% |
| PusulaV2NoBeNoReentry | LTC/USDT:USDT | 15 | -0.13 | -1.98 | 11.3% |
| PusulaV2NoBeNoReentry | DOT/USDT:USDT | 5 | -1.06 | -5.31 | -63.4% |
| PusulaV2NoBeNoReentry | AVAX/USDT:USDT | 10 | 1.43 | 14.29 | 171.8% |
| PusulaV2NoBeNoReentry | TRX/USDT:USDT | 16 | -0.40 | -6.38 | 1881.6% |
| PusulaV2NoBeNoReentry | ATOM/USDT:USDT | 10 | -0.55 | -5.52 | -51.5% |
| PusulaV2NoBeNoReentry | BCH/USDT:USDT | 12 | 0.43 | 5.18 | -7.2% |
| PusulaV2NoBeNoReentry | ETC/USDT:USDT | 10 | -0.15 | -1.51 | 14.6% |
| PusulaV2NoBeNoReentry | XLM/USDT:USDT | 10 | -0.44 | -4.38 | 289.8% |

## Grafikler
![PusulaV2NoBe_sermaye.png](PusulaV2NoBe_sermaye.png)
![PusulaV2NoBe_R_dagilimi.png](PusulaV2NoBe_R_dagilimi.png)
![PusulaV2NoBeNoReentry_sermaye.png](PusulaV2NoBeNoReentry_sermaye.png)
![PusulaV2NoBeNoReentry_R_dagilimi.png](PusulaV2NoBeNoReentry_R_dagilimi.png)

## Yorum: güçlü yanlar / şüpheli noktalar
_(Claude tarafından rakamlara bakılarak yazılır.)_

## Karar: devam / düzelt / emekli
_(Claude tarafından yazılır, gerekçesiyle.)_
