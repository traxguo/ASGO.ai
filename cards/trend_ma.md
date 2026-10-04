# trend_ma — Hareketli ortalama kesişimi + trend filtresi

Kod: [`strategies/candidates/trend_ma.py`](../strategies/candidates/trend_ma.py) (`TrendMA_B` = Model B, `TrendMA_A` = Model A)

## Hipotez
Fiyat güçlü bir yöne gittiğinde (trend), bir süre o yönde gitmeye devam etme eğilimindedir. Kısa vadeli ortalama orta vadeli ortalamayı kestiğinde yeni bir hareket başlıyor olabilir; bunu sadece uzun vadeli trendle aynı yöndeyse alırız ki ters yöndeki gürültüye girmeyelim.

## Yön
İkisi de (long ve short simetrik). Long ve short sonuçları her zaman ayrı raporlanır; bir taraf zarar ettiriyorsa o taraf kapatılabilir.

## Giriş koşulları

**Long** (hepsi aynı anda doğru olmalı):
- [trend_up] Teknik: `close > EMA(200)` | Açıklama: "{tf} trend yukarı (fiyat {close}, EMA200 {ema_trend} üzerinde)."
- [ma_cross_up] Teknik: `EMA(20)` bu mumda `EMA(50)`'yi aşağıdan yukarı kesti | Açıklama: "Kısa vadeli ortalama EMA20 ({ema_fast}), orta vadeli EMA50'yi ({ema_slow}) yukarı kesti."

**Short** (hepsi aynı anda doğru olmalı):
- [trend_down] Teknik: `close < EMA(200)` | Açıklama: "{tf} trend aşağı (fiyat {close}, EMA200 {ema_trend} altında)."
- [ma_cross_down] Teknik: `EMA(20)` bu mumda `EMA(50)`'yi yukarıdan aşağı kesti | Açıklama: "Kısa vadeli ortalama EMA20 ({ema_fast}), orta vadeli EMA50'yi ({ema_slow}) aşağı kesti."

## Neye bakıyor? (bildiği şeyler)
- Sadece kapanmış mumların fiyatı (açılış, en yüksek, en düşük, kapanış)
- EMA20, EMA50, EMA200 (üstel hareketli ortalamalar)
- ATR(14): son 14 mumun ortalama hareket genişliği (stop ve giriş bölgesi için)
- Son 10 mumun en düşük / en yüksek seviyesi (yapısal stop için)
- Bilmedikleri: haber, hacim, funding, diğer coinler. Bunlar ileride ayrı filtre olarak test edilebilir.

## İşlem yönetimi
- **Giriş bölgesi:** Sinyal mumunun kapanışı ile kapanış ∓ 0.25 ATR arası (long için altı, short için üstü). Backtest'te emir bölgenin ortasına limit olarak konur.
- **Stop:** 1.5 ATR stop ile yapısal stop (long: son 10 mumun dibi − 0.1 ATR; short: son 10 mumun tepesi + 0.1 ATR) arasından **daha geniş** olanı. Stop fiyatın %8'inden uzaksa sinyal üretilmez.
- **TP modeli:** İkisi de test edilir. Model B (varsayılan): TP1 = 2R'de %50 kapat, stop girişe; TP2 = 4R. Model A: tamamı 4R'de, 2R'ye gelince stop girişe.
- **Sinyal geçerlilik süresi:** 3 mum. Fiyat 3 mum içinde bölgeye gelmezse veya önce stop seviyesine değerse sinyal iptal.
- **Kaldıraç:** en fazla 3x, likidasyon stop mesafesinin en az 2 katı uzakta.

## Zaman dilimi ve parametreler
| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 4h | 1h, 4h |
| EMA hızlı | 20 | 10-30 |
| EMA yavaş | 50 | 40-60 |
| EMA trend | 200 | 150-250 |
| ATR periyodu | 14 | sabit |
| Isınma (startup) | 1000 mum | EMA200'ün oturması için |

## Durum: candidate — ilk backtest başarısız, **emeklilik önerildi** (proje sahibinin onayı bekleniyor)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-04 | Boru hattı testi (**sentetik veri**) | Kod uçtan uca çalışıyor; lookahead yok. Rakamlar anlamsız (rastgele veri). | [tests/smoke/ornek_rapor_SENTETIK](../tests/smoke/ornek_rapor_SENTETIK/rapor.md) |
| 2026-10-04 | Lookahead + recursive (gerçek veri, 4h) | 60 sinyalde bias yok; 1000 mum ısınma yeterli (EMA200 sapması %0). | — |
| 2026-10-04 | İlk backtest, A vs B (gerçek veri, geliştirme 2020-06 → 2024-12, 6 coin) | A: -0.06R/işlem, PF 0.91, DD %47. B: -0.06R/işlem, PF 0.92, DD %43. 2020-2022 kârlı, 2023-2024 long ve short zararda. Eşikleri geçmedi. | [results/2026-10-04_trend_ma_ilk_backtest](../results/2026-10-04_trend_ma_ilk_backtest/rapor.md) |

## Notlar / öğrenilenler
- `recursive-analysis`: EMA200 için 250 mumluk ısınma yetersizdi (~%2 sapma), 1000'e çıkarıldı.
- `recursive-analysis` gerçek veride tekrarlandı: 1000 mumla sapma yok.
- Gerçek veride işlem yönetimi beklendiği gibi: stop ortalama -1.05R, TP2 ortalama +3.9R (maliyet + funding dahil). Kaybın sebebi girişler.
- Sadece short'u bırakmak cazip görünüyor (PF 1.15) ama short kârının hepsi 2021-2022 düşüş piyasasından; 2023-2024'te short da zararda. Sonuca bakıp yön seçmek aşırı uyum olur, yapılmadı.

## Emeklilik gerekçesi (varsa)
—
