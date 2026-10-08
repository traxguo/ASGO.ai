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
- Stop: likiditeyi alan en uç mumun iğnesi (long'da en dip mumun dibi). **O mumun iğnesi gövdesinden uzunsa** stop iğneye değil gövdenin ucuna konur (Aslan: "abartı fitil varsa mumun kapanışını al"). Tampon yok. Stop fiyatın %8'inden uzaksa sinyal yok.
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

## Durum: candidate

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
