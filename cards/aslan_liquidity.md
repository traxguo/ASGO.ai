# aslan_liquidity — Likidite alımı + MSS / iFVG (Aslan'ın stratejisi)

Kod: [`strategies/candidates/aslan_liquidity.py`](../strategies/candidates/aslan_liquidity.py)
Haber takvimi: [`strategies/common/news_calendar.py`](../strategies/common/news_calendar.py)

## Hipotez
Aslan'ın stratejisi (2026-10-08, sohbette anlattı). Büyük grafiklerdeki (1 günlük, 4 saatlik) belirgin tepe ve diplerin hemen ötesinde stop emirleri birikir (likidite). Fiyat bu seviyeyi alıp (iğne atıp) küçük grafikte geri dönerse, dönüş yönünde güçlü bir hareket gelir. Sadece günlük yön (daily bias) tarafında işlem açılır: akıntıya karşı yüzülmez.

## Yön
İkisi de (long ve short), ama her an sadece günlük yönün izin verdiği tarafta.

## Giriş koşulları
Koşul kimlikleri koddakiyle aynıdır. Hepsi aynı mumda doğru olmalı.

**Long**
- [bias_up] Teknik: son kapanmış günlük mum, son onaylı günlük tepenin üstünde kapattı (ve sonra son onaylı günlük dibin altında kapanış olmadı) | Açıklama: "Günlük yön yukarı: günlük mum son tepenin üstünde kapattı."
- [liquidity_swept_low] Teknik: fiyat, 1d veya 4h grafikteki onaylı bir dibin ya da bir önceki günün dibinin altına indi; bu son `setup_window` mum içinde oldu | Açıklama: "Fiyat {seviye} altındaki likiditeyi aldı."
- [reversal_mss_or_ifvg] Teknik: giriş grafiğinde (1h veya 15m) ya **MSS** = kapanış, likidite alımındaki en dip mumdan önceki son küçük tepenin üstünde; ya da **iFVG** = alım hareketi sırasında oluşan aşağı yönlü bir boşluğun (bearish FVG) üst kenarının üstünde ilk kapanış | Açıklama: "Fiyat likiditeyi aldıktan sonra yön değiştirdi (MSS / iFVG)."
- [no_news] Teknik: sinyal anı, önemli ABD haberinin (FOMC, CPI, NFP) 1 saat öncesi ile 1 saat sonrası arasında değil | Açıklama: "Yakında önemli ABD haberi yok."

**Short:** tam tersi — [bias_down], [liquidity_swept_high] (tepe likiditesi alındı), [reversal_mss_or_ifvg] (son küçük dibin altında kapanış ya da yukarı yönlü boşluğun alt kenarının altında kapanış), [no_news].

Tanımlar:
- **Tepe / dip (swing):** solundaki 2 ve sağındaki 2 mumdan daha yüksek tepesi (veya daha alçak dibi) olan mum. Sağdaki 2 mum kapanınca onaylanır; ondan önce kullanılmaz.
- **Bir likidite seviyesi bir kez kullanılır.** Alındıktan sonra listeden düşer.
- Her likidite alımından en fazla bir işlem çıkar.

## İşlem yönetimi
- Giriş: sinyal mumunun kapanış fiyatına limit emir, 2 mum içinde dolmazsa iptal (önce stop'a değerse de iptal).
- Stop (v2, Aslan 2026-10-08, `AslanLiq2_*`): iğne en fazla gövdenin %175'i kadar olabilir; daha uzunsa stop gövde ucundan 1.75 gövde uzağa konur. Günlük yön filtresi kapalı versiyon (`*_NoBias`) her iki yönde de işlem arar.
- Stop (v1, karşılaştırma için): likiditeyi alan en uç mumun iğnesi (long'da en dip mumun dibi). **O mumun iğnesi gövdesinden uzunsa** stop iğneye değil gövdenin ucuna konur (Aslan: "abartı fitil varsa mumun kapanışını al"). Tampon yok. Stop fiyatın %8'inden uzaksa sinyal yok.
- Hedef: tek hedef **2R**, kısmi çıkış yok, stop başa çekilmez (`MODEL_ASLAN`, 1R stop / 2R hedef). Projenin standart A/B modellerinden farklıdır, çünkü stratejinin sahibi böyle kullanıyor.
- Risk: işlem başına kasanın **%3**'ü (Aslan %3-5 diyor). Kaldıraç en fazla 20x, likidasyon her zaman stop mesafesinin en az 2 katı uzakta.
- Saat filtresi yok ("her zaman girebilir"), sadece haber filtresi var.

## Zaman dilimi ve parametreler
Test öncesi sabitlendi; Aslan düzeltirse kart ve kod birlikte değişir.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Likidite grafikleri | 1d + 4h (+ önceki gün tepe/dip) | sabit |
| Giriş grafiği | `AslanLiq_1h`: 1h, `AslanLiq_15m`: 15m | 15m, 1h |
| Swing tanımı | 2 mum sol / 2 mum sağ | 2-3 |
| Alımdan sonra dönüş bekleme süresi | 12 saat (1h'de 12 mum, 15m'de 48 mum) | 6-24 saat |
| FVG arama geriye | alımdan 10 mum önce | 5-20 |
| Haber penceresi | 1 saat önce → 1 saat sonra | 30 dk - 2 saat |
| Hedef | 2R | Aslan'ın kuralı |
| Risk | %3 | %3-5 |

## Varsayımlar (Aslan onaylamadı, kendisi düzeltebilir)
1. Likidite seviyesi tanımı (2+2 mum swing, önceki gün tepe/dip).
2. Günlük yön tanımı (son günlük tepe/dibin ötesinde kapanış).
3. MSS'nin hangi tepeye göre ölçüldüğü (alım dibinden önceki son küçük tepe).
4. iFVG: alımdan 10 mum öncesinden itibaren oluşan boşluk, ilk kapanışla ters çevrilmesi.
5. "Mum boyutu" = mumun gövdesi.
6. Haber listesi çevrimdışı hazırlandı (ForexFactory'ye bu ortamdan erişilemiyor): FOMC tarihleri, CPI tarihleri ve NFP tarih kuralı. Tarihler resmi takvimle doğrulanmadı.


## v3 — Aslan'ın 2026-10-09 düzeltmeleri
Kod: [`strategies/candidates/aslan_liquidity_v3.py`](../strategies/candidates/aslan_liquidity_v3.py)

- **Likidite seviyeleri:** 1h, 4h ve 1d tepe/dipleri, önceki gün tepe/dibi, seans tepe/dipleri (UTC: Asya 00-07, Londra 07-13, New York 13-21; seans bitince kullanılır).
- **İki tür kurulum:**
  - [liquidity_taken] **Alım (sweep):** fiyat seviyeyi iğneyle geçip içeride kapatırsa ters yönde işlem (dip alındı → long, tepe alındı → short). | "Fiyat {seviye} likiditesini alıp geri döndü."
  - [liquidity_taken] **Kırılım (break):** bir mum seviyenin ötesinde kapatırsa kırılım yönünde işlem (tepe kırıldı → long, dip kırıldı → short). Önce alım sayılan seviye 12 saat içinde gövdeyle kırılırsa kırılıma dönüşür. | "Fiyat {seviye} seviyesini mum kapanışıyla kırdı."
- [reversal_mss_or_ifvg] **Giriş onayı:** işlem yönünde MSS veya iFVG, giriş grafiğinde (`AslanLiq3_15m`: 15 dk, `AslanLiq3_5m`: 5 dk), 12 saat içinde.
- [trend_up] / [trend_down] **Trend (daily bias):** son onaylı tepe ve dip bir öncekinden yüksekse (HH + HL) yukarı, alçaksa (LH + LL) aşağı, karışıksa nötr. Ana versiyon 4 saatlik trende bakar; `_Trend2` 4 saatlik ve 1 saatlik ikisinin de aynı yönde olmasını ister; `_NoTrend` filtre kullanmaz.
- **Hedef:** tek hedef **1R** (`MODEL_1R`). **Stop:** v2 kuralı (iğne en fazla gövdenin %175'i).
- Haber filtresi, giriş fiyatı, 2 mum geçerlilik aynı. Risk testte %1 (hesap tüm dönem boyunca yaşasın diye; R sonuçları riskten bağımsız).

## v4 — videodaki kontrol listesi (2026-10-09)
Kod: [`strategies/candidates/aslan_liquidity_v4.py`](../strategies/candidates/aslan_liquidity_v4.py)
- [bias_up]/[bias_down] günlük HH+HL / LH+LL; [trend_up]/[trend_down] 4 saatlik aynı yön.
- [poi_touched] fiyat 1 saatlik bir FVG, order block veya iFVG bölgesine döndü | "Fiyat {bölge} bölgesine geri çekildi."
- [mini_structure_engulf] 5 dk / 15 dk'da son mini tepeyi (1+1 mum) kıran engulf mumu | "Küçük grafikte yapı kırıldı ve engulf mumu geldi."
- Stop: dönüşün uç noktası (iğne en fazla gövdenin %175'i). Hedef 1R (`AslanLiq4_*`) veya 2R (`*_2R`).
 candidate — ilk backtest'te başarısız, Aslan'ın kural düzeltmesi bekleniyor

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-08 | Lookahead kontrolü (BTC 1h ve 15m, 50 kesim noktası) | Geleceği görme yok (`research/robustness/aslan_lookahead_check.py`). | — |
| 2026-10-08 | İlk backtest, geliştirme (2020-01 → 2024-12) | 1h: -0.21R, PF 0.72, 2266 işlem. 15m: -0.28R, PF 0.63, 3143 işlem. Maliyet hariç ~0R. %3 riskle hesap 2023'te sıfırlandı. Haber filtresi etkisiz. Doğrulama ve kasa kullanılmadı. | [results/2026-10-08_aslan_liquidity_ilk_backtest](../results/2026-10-08_aslan_liquidity_ilk_backtest/README.md) |
| 2026-10-08 | v2: iğne en fazla gövdenin %175'i (Aslan), yön filtresi açık/kapalı | 1h: -0.16R (filtre açık), -0.14R (kapalı). 15m: -0.20R / -0.16R. İyileşti ama hâlâ eksi; maliyet hariç ~0R. Yön filtresi faydasız. | [results/2026-10-08_aslan_liquidity_v2](../results/2026-10-08_aslan_liquidity_v2/README.md) |
| 2026-10-09 | v3: 1R, seans seviyeleri, kırılım, HH/HL trend, 15 dk ve 5 dk (6 varyant) | 15 dk: -0.32 ile -0.39R; 5 dk: -0.46 ile -0.58R. Maliyet hariç hepsi ~0R. Test hesapları erken sıfırlandı. | [results/2026-10-09_aslan_liquidity_v3](../results/2026-10-09_aslan_liquidity_v3/README.md) |
| 2026-10-09 | v4: videodaki yöntem (günlük+4s trend, 1s FVG/OB/iFVG bölgesine dönüş, mini yapı kırılımı + engulf; 5 dk/15 dk, 1R/2R) | -0.24R ile -0.33R; maliyet hariç ~0R; winrate yazı-tura beklentisinde. | [results/2026-10-09_aslan_liquidity_v4](../results/2026-10-09_aslan_liquidity_v4/README.md) |
| 2026-10-09 | v5: sadece likidite alımı, 5/15 dk OB/iFVG/MSS onayı, stop alım uç noktasının %0.1 ötesi, 1R/2R | -0.24R ile -0.27R; maliyet hariç ~0R. | [results/2026-10-09_aslan_liquidity_v5](../results/2026-10-09_aslan_liquidity_v5/README.md) |

## Notlar / öğrenilenler
- Kazanma oranı %30-32; 2R hedefle başa baş için ~%33 gerekiyor. Maliyetsiz bile sonuç ~0R: giriş kuralının kenarı yok.
- Stop iğnenin ucunda olduğu için çok dar (1h ortanca %1.8, 15m %1.1); işlem başı ~%0.2 maliyet R'nin büyük kısmını yiyor. En dar stoplu işlemler en kötüsü.
- MSS ve iFVG ayrı ayrı da eksi. Long ve short, 5 coinin hepsi, 2020-2024'ün her yılı eksi.
- Aslan'ın gözle yaptığı seçim kartın varsayımlarından farklıysa (özellikle "önemli likidite" ve günlük yön), düzeltilmiş kurallarla yeniden test edilecek. Doğrulama verisi bunun için temiz duruyor.

## Emeklilik gerekçesi (varsa)
