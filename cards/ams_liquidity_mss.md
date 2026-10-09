# ams_liquidity_mss — Algoritmik likidite + MSS (Gemini'nin "V27" kuralları)

Kod: [`strategies/candidates/ams_liquidity_mss.py`](../strategies/candidates/ams_liquidity_mss.py)
Haber takvimi: [`strategies/common/news_calendar.py`](../strategies/common/news_calendar.py)

## Hipotez
Proje sahibi 2026-10-09'da Gemini'den aldı (Aslan stratejisinin 26 başarısız denemesinden sonra). İddia: SMC'yi botta çalıştırmanın yolu "önemli" gibi yoruma açık sözleri atıp her şeyi mum sayımına bağlamak, sadece hacimli saatlerde (killzone) ve 1 saatlik 200 EMA yönünde işlem açmak. Bu iddia test edilmedi; bu kart onu test etmek için var.

## Yön
İkisi de. 1 saatlik kapanış 200 EMA'nın üstündeyse sadece long (dip likiditesi alımı), altındaysa sadece short.

## Tanımlar (15 dk grafik, saatler UTC; Türkiye = UTC+3)
- **Fraktal:** solunda ve sağında 2'şer mumdan yüksek tepe (veya alçak dip). Sağdaki 2 mum kapanınca onaylanır.
- **Likidite seviyeleri (sadece bunlar):** Asya seansı (Türkiye 00:00-08:00) en yüksek fraktal tepesi / en düşük fraktal dibi; bir önceki günün tepesi/dibi (UTC günü); eşit tepeler/dipler (100 mum içinde, %0.05'ten yakın iki fraktal). Bir seviye 1 gün geçerli, bir kez kullanılır.
- **Killzone:** Londra 10:00-12:00, New York 15:30-18:00 (Türkiye saati).

## Giriş koşulları
**Long**
- [ema200_1h_above] Teknik: son kapanmış 1 saatlik mum 200 EMA'nın üstünde | Açıklama: "1 saatlik grafikte fiyat 200 EMA'nın üstünde."
- [sweep_low_then_mss_in_killzone] Teknik: killzone içinde fiyat bir dip likiditesinin altına iğne attı ve o mum ya da bir sonraki mum seviyenin üstünde kapandı (iki kapanış altında = kırılım, iptal); aynı killzone içinde bir 15 dk mumu, alımdaki en dip mumdan önceki son fraktal tepenin üstünde kapandı (MSS) | Açıklama: "{seviye} likiditesi alındı ve 15 dakikalıkta yapı yukarı kırıldı."
- [fvg_below_price] Teknik: alım ile MSS arasındaki harekette, sonradan hiç iğne girmemiş en yeni yukarı FVG var; limit emir boşluğun uzak kenarında (1. mumun tepesi), fiyatın altında; stop bunun altında | Açıklama: "MSS dalgasında boşluk (FVG) kaldı, oraya limit emir."
- [no_news] Teknik: önemli ABD haberinin 2.5 saat öncesi ile 15 dk sonrası arasında sinyal yok (emir 2 saat geçerli olduğu için haberden 30 dk önce emir kalmasın diye) | Açıklama: "Yakında önemli ABD haberi yok."

**Short:** tam tersi (200 EMA altı, tepe likiditesi alımı, son fraktal dibin altında kapanış, aşağı FVG'nin uzak kenarı = 1. mumun dibi).

## İşlem yönetimi
- Giriş: FVG kenarına limit emir, 8 mum (2 saat) geçerli; önce stop görülürse iptal.
- Stop: alım hareketinin uç noktasının %0.1 ötesi.
- TP1 1.5R'de %50 kapat, stop girişe çekilir; TP2 3R'de kalan kapanır (sabit TP ızgarasındaki modellerden biri).
- Risk işlem başına %1, kaldıraç en fazla 20 (likidasyon stopun en az 2 katı uzakta).

## Varsayımlar (kurallarda yazmıyordu, benim seçimim)
- Emrin geçerlilik süresi 2 saat.
- Birden fazla temiz FVG varsa en yenisi.
- "Önceki gün" UTC günü (Binance günlük mumu).
- Gemini'nin yazdığı örnek işlemler (EUR/USD, tarih yok) gerçek veri değil; test edilemedi.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-09 | Lookahead kontrolü (BTC 15 dk, 15 kesim noktası) | Geleceği görme yok (`research/robustness/ams_lookahead_check.py`). | — |
| 2026-10-09 | İlk backtest, geliştirme (2020-01 → 2024-12) | 95 işlem, -0.48R, PF 0.42, DD %38. Long -0.40R, short -0.55R. Sinyallerin %57'si dolmadı. Doğrulama ve kasa kullanılmadı. | [results/2026-10-09_ams_liquidity_mss_ilk_backtest](../results/2026-10-09_ams_liquidity_mss_ilk_backtest/rapor.md) |

## Durum
candidate — ilk backtest'te başarısız
