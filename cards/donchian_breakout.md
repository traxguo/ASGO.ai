# donchian_breakout — Donchian kanalı kırılımı

Kod: [`strategies/candidates/donchian_breakout.py`](../strategies/candidates/donchian_breakout.py) (`DonchianBreakout_B` = Model B, `DonchianBreakout_A` = Model A)

## Hipotez
Fiyat uzun süredir gidemediği bir seviyeyi (son 20 mumun en yükseği veya en düşüğü) kapanışla geçtiğinde, yeni bir hareket başlıyor olabilir. Bu klasik "kaplumbağa" (turtle) kırılım fikridir: büyük trendler hep bir kırılımla başlar, yanlış kırılımlarda küçük kayıp, gerçeklerinde büyük kazanç beklenir. trend_ma'dan farkı: ortalamalara değil, doğrudan fiyat seviyesine bakar ve trend filtresi kullanmaz.

## Yön
İkisi de (long ve short simetrik). Long ve short sonuçları ayrı raporlanır.

## Giriş koşulları

**Long** (hepsi aynı anda doğru olmalı):
- [breakout_up] Teknik: `close > max(high, önceki 20 mum)` ve bir önceki mumda bu koşul yoktu (ilk kırılım) | Açıklama: "{tf} fiyat ({close}) son 20 mumun en yükseğini ({dc_upper}) kapanışla yukarı kırdı."

**Short** (hepsi aynı anda doğru olmalı):
- [breakout_down] Teknik: `close < min(low, önceki 20 mum)` ve bir önceki mumda bu koşul yoktu (ilk kırılım) | Açıklama: "{tf} fiyat ({close}) son 20 mumun en düşüğünü ({dc_lower}) kapanışla aşağı kırdı."

## Neye bakıyor? (bildiği şeyler)
- Sadece kapanmış mumların fiyatı (açılış, en yüksek, en düşük, kapanış)
- Donchian kanalı: sinyal mumundan **önceki** 20 mumun en yükseği / en düşüğü
- ATR(14) (stop ve giriş bölgesi için), son 10 mumun en düşük / en yüksek seviyesi (yapısal stop için)
- Bilmedikleri: trend yönü, hacim, funding, haber, diğer coinler.

## İşlem yönetimi
- **Giriş bölgesi:** Sinyal mumunun kapanışı ile kapanış ∓ 0.25 ATR arası. Backtest'te emir bölgenin ortasına limit.
- **Stop:** 1.5 ATR stop ile yapısal stop (long: son 10 mumun dibi − 0.1 ATR; short: son 10 mumun tepesi + 0.1 ATR) arasından **daha geniş** olanı. Stop fiyatın %8'inden uzaksa sinyal üretilmez.
- **TP modeli:** İkisi de test edilir. Model B: TP1 = 2R'de %50 kapat, stop girişe; TP2 = 4R. Model A: tamamı 4R'de, 2R'ye gelince stop girişe.
- **Sinyal geçerlilik süresi:** 3 mum.
- **Kaldıraç:** en fazla 3x, likidasyon stop mesafesinin en az 2 katı uzakta.

(Hepsi ortak modülden, trend_ma ile aynı.)

## Zaman dilimi ve parametreler
Parametreler test öncesi sabitlendi, geliştirme sonucuna göre değiştirilmeyecek.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 4h | 1h, 4h |
| Kanal uzunluğu | 20 mum | 15-55 |
| ATR periyodu | 14 | sabit |
| Yapısal stop bakışı | 10 mum | sabit |
| Isınma (startup) | 300 mum | ATR sapması ~%0 (recursive-analysis) |

## Durum: candidate

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-04 | Lookahead + recursive (4h) | 60 sinyalde bias yok; ATR için 300 mum ısınma. | — |
| 2026-10-04 | İlk backtest, A vs B (geliştirme 2020-02 → 2024-12, 6 coin) | A: +0.06R/işlem, PF 1.04, DD %41.6. B: +0.09R/işlem, PF 1.10, DD %38.4. Long taşıyor (+46.7R), short ~0. Maliyet x2'de B +0.05R. Pozitif ama DD eşiğin çok üstünde. | [results/2026-10-04_donchian_breakout_ilk_backtest](../results/2026-10-04_donchian_breakout_ilk_backtest/rapor.md) |

## Notlar / öğrenilenler
- Kârın büyük kısmı SOL ve DOGE'nin büyük trendlerinden; XRP ve BNB negatif.
- En büyük sorun drawdown: aynı anda açık işlemler birlikte kaybediyor.
- Model B, A'dan her ölçüde iyi.

## Emeklilik gerekçesi (varsa)
—
