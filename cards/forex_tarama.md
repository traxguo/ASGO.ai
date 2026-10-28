# forex_tarama — Forex'te kısa vadeli işlem taraması (araştırma, 2026-10-28)
Kod: [`research/forex/scan.py`](../research/forex/scan.py), veri: [`research/forex/fetch_dukascopy.py`](../research/forex/fetch_dukascopy.py) (GitHub sunucusunda çalışır)

## Fikir
GUO: kriptoda masraflar scalp'ı öldürdü; forex'te (EUR/USD, altın, Nasdaq) makas çok daha düşük, kısa vadeli işlem daha kolay olabilir. Bot sadece sinyal/tavsiye verir, işlem açmaz.
Bu ilk tarama, kriptoda denenen en iyi üç kısa vadeli fikrin forex karşılığıdır. Kurallar ilk çalıştırmadan önce yazıldı.

## Veri ve masraf
- Dukascopy 1 dakikalık alış (bid) ve satış (ask) mumları, 5 dakikalık mumlara çevrilir. 2020-01 → 2026-09.
- Gerçek makas: piyasa alışı ask'tan, piyasa satışı bid'den. Limit emir sadece karşı taraf limitin içinden geçerse dolar.
- EUR/USD'de ayrıca işlem başına %0.0035 komisyon (her yön). Altın ve Nasdaq'ta sadece makas.
- Dönemler: geliştirme 2020-2024, doğrulama 2025-01 → 2026-03. Kasa (2026-04 → 09) kullanılmaz.

## Kurallar
Günlük trend: son kapanmış UTC günü; puan (kapanış EMA50 üstü, EMA20 EMA50 üstü, 90 günlük getiri artı) ≥ +1 ve kapanış EMA20 üstü = yukarı; tersi = aşağı.
- **A, Limit fitil:** her saat başında trend yönüne limit emir, saat açılışından k × ATR(1 saat, 14) uzakta (k = 1 / 1.5 / 2). Bir saat bekler. Dolarsa 1 veya 3 saat sonra piyasa emriyle kapanır. Long ve short.
- **B, Açılış aralığı kırılımı:** seansın ilk saatinin tepe/dip aralığı (Londra 08:00, Nasdaq New York 09:30). Sonraki 5 dakikalık kapanış aralığın dışına çıkarsa o yönde gir. Stop aralığın öbür ucu, hedef 1R veya 2R, seans sonunda (Londra 13:00, New York 12:00) kapat. Günde en fazla 1 işlem. Trend filtresiyle ve filtresiz.
- **C, RSI(2) geri dönüş:** 15 dakikalık RSI(2) trend yönünde aşırı (yukarı trendde < 5 → al, aşağı trendde > 95 → sat). RSI 70'i (short için 30'u) geçince veya 2 / 4 saat sonra çık.

## Geçme şartı (ilk eleme)
Masraf sonrası işlem başı ortalama > 0 hem geliştirmede hem doğrulamada, günde ≥ 0.5 işlem (sembol başına ya da üç sembol toplamında), en az 3 geliştirme yılında artı.

## Sonuçlar
(ilk çalıştırmadan sonra eklenecek)
