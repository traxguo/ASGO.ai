# Veri doğrulama raporu — 2026-10-04

Veri klasörü: `user_data/data/binance`

Sorunlar sadece raporlanır, veri sessizce düzeltilmez.

## Fiyat mumları (futures)

| Coin | TF | Başlangıç | Bitiş | Mum | Eksik | Tekrar | Sıfır hacim | Aşırı sıçrama |
|---|---|---|---|---|---|---|---|---|
| BTC/USDT:USDT | 1h | 2020-01-01 | 2026-09-30 | 59160 | 0 | 0 | 1 | 3 |
| BTC/USDT:USDT | 4h | 2020-01-01 | 2026-09-30 | 14790 | 0 | 0 | 0 | 0 |
| ETH/USDT:USDT | 1h | 2020-01-01 | 2026-09-30 | 59160 | 0 | 0 | 1 | 3 |
| ETH/USDT:USDT | 4h | 2020-01-01 | 2026-09-30 | 14790 | 0 | 0 | 0 | 0 |
| SOL/USDT:USDT | 1h | 2020-09-14 | 2026-09-30 | 52985 | 0 | 0 | 1 | 12 |
| SOL/USDT:USDT | 4h | 2020-09-14 | 2026-09-30 | 13247 | 0 | 0 | 0 | 3 |
| XRP/USDT:USDT | 1h | 2020-01-06 | 2026-09-30 | 59032 | 0 | 0 | 1 | 12 |
| XRP/USDT:USDT | 4h | 2020-01-06 | 2026-09-30 | 14758 | 0 | 0 | 0 | 5 |
| BNB/USDT:USDT | 1h | 2020-02-10 | 2026-09-30 | 58192 | 0 | 0 | 1 | 5 |
| BNB/USDT:USDT | 4h | 2020-02-10 | 2026-09-30 | 14548 | 0 | 0 | 0 | 0 |
| DOGE/USDT:USDT | 1h | 2020-07-10 | 2026-09-30 | 54567 | 0 | 0 | 1 | 33 |
| DOGE/USDT:USDT | 4h | 2020-07-10 | 2026-09-30 | 13642 | 0 | 0 | 0 | 16 |

## Funding oranı ve mark price

| Coin | Funding başlangıç | Funding satır | 8 saatten uzun boşluk | En büyük boşluk | Mark price başlangıç | Mark mum |
|---|---|---|---|---|---|---|
| BTC/USDT:USDT | 2020-01-01 | 7395 | 0 | 0 days 08:00:00 | 2020-01-01 | 59160 |
| ETH/USDT:USDT | 2020-01-01 | 7395 | 0 | 0 days 08:00:00 | 2020-01-01 | 59160 |
| SOL/USDT:USDT | 2020-09-13 | 6700 | 0 | 0 days 08:00:00 | 2020-09-13 | 53005 |
| XRP/USDT:USDT | 2020-01-06 | 7379 | 0 | 0 days 08:00:00 | 2020-01-06 | 59037 |
| BNB/USDT:USDT | 2020-02-10 | 7274 | 0 | 0 days 08:00:00 | 2020-02-01 | 58416 |
| DOGE/USDT:USDT | 2020-07-10 | 6821 | 0 | 0 days 08:00:00 | 2020-07-10 | 54573 |

## Ayrıntılar
- BTC/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2020-03-12 10:00:00+00:00 (5981.07)', '2020-03-12 23:00:00+00:00 (4764.65)', '2020-03-13 02:00:00+00:00 (4723.95)']
- ETH/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2020-03-12 10:00:00+00:00 (131.74)', '2020-03-12 23:00:00+00:00 (106.71)', '2020-03-13 02:00:00+00:00 (110.8)']
- SOL/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2021-01-07 00:00:00+00:00 (2.1868)', '2021-01-07 12:00:00+00:00 (2.5669)', '2021-01-08 12:00:00+00:00 (3.6569)']
- SOL/USDT:USDT 4h: eksik örnekleri [], sıçrama örnekleri ['2021-01-08 08:00:00+00:00 (3.1504)', '2021-02-22 16:00:00+00:00 (13.2878)', '2022-11-09 12:00:00+00:00 (12.9)']
- XRP/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2020-03-12 10:00:00+00:00 (0.1579)', '2020-12-24 22:00:00+00:00 (0.3261)', '2020-12-29 17:00:00+00:00 (0.2321)']
- XRP/USDT:USDT 4h: eksik örnekleri [], sıçrama örnekleri ['2020-12-24 20:00:00+00:00 (0.3394)', '2021-01-07 08:00:00+00:00 (0.3614)', '2021-02-01 12:00:00+00:00 (0.4234)']
- BNB/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2020-03-12 10:00:00+00:00 (11.459)', '2020-03-12 23:00:00+00:00 (9.277)', '2020-03-13 01:00:00+00:00 (7.716)']
- DOGE/USDT:USDT 1h: eksik örnekleri [], sıçrama örnekleri ['2020-12-20 09:00:00+00:00 (0.004649)', '2021-01-02 04:00:00+00:00 (0.007731)', '2021-01-02 20:00:00+00:00 (0.009114)']
- DOGE/USDT:USDT 4h: eksik örnekleri [], sıçrama örnekleri ['2021-01-02 16:00:00+00:00 (0.011731)', '2021-01-28 04:00:00+00:00 (0.010828)', '2021-01-28 12:00:00+00:00 (0.018061)']

**Sonuç:** 9 kalemde dikkat edilmesi gereken durum var.
