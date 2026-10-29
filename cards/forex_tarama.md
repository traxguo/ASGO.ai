# forex_tarama — Forex'te kısa vadeli işlem taraması (araştırma, 2026-10-28)
Kod: [`research/forex/scan.py`](../research/forex/scan.py), veri: [`research/forex/fetch_dukascopy.py`](../research/forex/fetch_dukascopy.py) (GitHub sunucusunda çalışır)

## Fikir
GUO: kriptoda masraflar scalp'ı öldürdü; forex'te (EUR/USD, altın, Nasdaq) makas çok daha düşük, kısa vadeli işlem daha kolay olabilir. Bot sadece sinyal/tavsiye verir, işlem açmaz.
Bu ilk tarama, kriptoda denenen en iyi üç kısa vadeli fikrin forex karşılığıdır. Kurallar ilk çalıştırmadan önce yazıldı.

## Veri ve masraf
- HistData.com 1 dakikalık mumlar (ücretsiz, sadece alış fiyatı), 5 dakikalık mumlara çevrilir. 2020-01 → 2026-03. (Dukascopy denendi; GitHub sunucusunu yavaşlatıp engelledi.)
- Masraf (makas + komisyon, gidiş-dönüş, tipik ECN hesap): EUR/USD %0.010, altın %0.015, Nasdaq %0.010. Satış fiyatına bu kadar eklenip "ask" yapılır: piyasa alışı ask'tan, satışı bid'den; limit emir sadece karşı taraf limitin içinden geçerse dolar. Her şey bir de **2 kat masrafla** çalıştırılır.
- Dönemler: geliştirme 2020-2024, doğrulama 2025-01 → 2026-03. Kasa (2026-04 → 09) kullanılmaz.

## Kurallar
Günlük trend: son kapanmış UTC günü; puan (kapanış EMA50 üstü, EMA20 EMA50 üstü, 90 günlük getiri artı) ≥ +1 ve kapanış EMA20 üstü = yukarı; tersi = aşağı.
- **A, Limit fitil:** her saat başında trend yönüne limit emir, saat açılışından k × ATR(1 saat, 14) uzakta (k = 1 / 1.5 / 2). Bir saat bekler. Dolarsa 1 veya 3 saat sonra piyasa emriyle kapanır. Long ve short.
- **B, Açılış aralığı kırılımı:** seansın ilk saatinin tepe/dip aralığı (Londra 08:00, Nasdaq New York 09:30). Sonraki 5 dakikalık kapanış aralığın dışına çıkarsa o yönde gir. Stop aralığın öbür ucu, hedef 1R veya 2R, seans sonunda (Londra 13:00, New York 12:00) kapat. Günde en fazla 1 işlem. Trend filtresiyle ve filtresiz.
- **C, RSI(2) geri dönüş:** 15 dakikalık RSI(2) trend yönünde aşırı (yukarı trendde < 5 → al, aşağı trendde > 95 → sat). RSI 70'i (short için 30'u) geçince veya 2 / 4 saat sonra çık.

## Geçme şartı (ilk eleme)
Masraf sonrası işlem başı ortalama > 0 hem geliştirmede hem doğrulamada, günde ≥ 0.5 işlem (sembol başına ya da üç sembol toplamında), en az 3 geliştirme yılında artı.

## Sonuçlar (2026-10-29, ilk çalıştırma, masraf dahil işlem başı ortalama %)
36 ayar (3 piyasa × 12). **Hiçbiri geçmedi.** Masrafsız ("brüt") sonuç neredeyse her yerde sıfır: sorun sadece masraf değil, bu basit kısa vadeli kurallarda avantaj yok.

| Piyasa | En iyi ayar | Geliştirme 2020-24 | Doğrulama 2025-26/03 | Not |
|---|---|---|---|---|
| EUR/USD | B açılış kırılımı 1R, trend filtreli | +0.001% (0.23/gün) | +0.006% | sıfır; 2 kat masrafta eksi. Diğer 11 ayar geliştirmede eksi |
| Altın | A limit k2, 3 saat | -0.006% (0.28/gün) | +0.104% | geliştirmede eksi; doğrulamadaki artı 2025 altın yükselişi (long +0.11, short -0.09) |
| Altın | C RSI(2) 4 saat | -0.012% (1.22/gün) | +0.020% | geliştirmede eksi |
| Nasdaq | B açılış kırılımı 2R, trend filtreli | +0.021% (0.22/gün) | -0.037% | doğrulamada eksi |

- En sık işlem (A k1, C RSI2) günde 1.2-1.5 işlem verir ama her piyasada geliştirmede eksi.
- 2 kat masrafla her şey daha kötü; sadece altın A k2 doğrulamada artı kalıyor (geliştirmede eksi).
- Ham çıktı: PR #43'ün "Forex scan" iş kaydı.

## Durum: ilk tarama reddedildi (2026-10-29)
