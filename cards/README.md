# Strateji kartları

Her stratejinin **kodlanmadan önce** bir kartı olur. Kart, stratejinin "kimlik belgesi"dir:

- **Hipotez:** Neden çalışmalı, piyasada hangi davranışı yakalıyor?
- **Yön:** long, short veya ikisi
- **Giriş koşulları:** Her koşulun teknik tanımı ve sinyal mesajında kullanılacak **Türkçe açıklama cümlesi**
- **İşlem yönetimi:** Giriş bölgesi, stop kuralı, TP modeli, sinyal geçerlilik süresi
- **Parametreler** ve makul aralıkları
- **Durum:** `candidate` (test ediliyor), `active` (testi geçti, sinyal üretebilir), `retired` (elendi)
- **Test geçmişi** ve **öğrenilenler**

## Kartlar

| Kart | Durum | Ne yapar (tek cümle) |
|---|---|---|
| [trend_ma](trend_ma.md) | candidate | Kısa ve orta hareketli ortalama kesişince, uzun vadeli trend yönünde işleme girer. |
| [nabiz](nabiz.md) | retired | Günlük trend güçlüyken 1 saatlik geri çekilmenin bitişinde trend yönünde girer (hızlı aday, elendi). |
| [kirilim1s](kirilim1s.md) | retired | Günlük trend güçlüyken 1 saatlik grafikte son 24 saatin tepesi/dibi kırılınca girer (hızlı aday, elendi). |
| [pusula_hizli](pusula_hizli.md) | retired | Pusula 4 saatlikte, gevşek trend şartı ve sabit 2R/4R hedefle (hızlı aday, elendi). |
| [kirilim1s_limit](kirilim1s_limit.md) | retired | Kırılım1s sinyali, limit (maker) emirle kırılan seviyeye geri dönüşte girer (hızlı aday, elendi). |
| [momentum_5m](momentum_5m.md) | beklemede | Proje sahibinin getirdiği 5 dakikalık momentum + kırılım + oynaklık filtresi, %1.5 stop / %3 hedef (ilk aşamayı normal masrafla geçemedi). |
| [fvg_ob](fvg_ob.md) | candidate (emeklilik önerildi) | 15 dk yapı kırılımı + Order Block, 3 dk FVG'nin ortasına limit emir, hedef karşı likidite (ilk elemede başarısız, masrafsız bile eksi). |
| [sfp_sweep](sfp_sweep.md) | candidate (emeklilik önerildi) | 5 dk mum 15 dk tepe/dibi iğneyle delip geri kapanınca ters yöne girer (ilk elemede başarısız, masrafsız bile eksi). |
| [vwap_reversion](vwap_reversion.md) | candidate (emeklilik önerildi) | 5 dk fiyat VWAP ve EMA20'den uzaklaşıp RSI aşırıyken dönüş mumuyla geri döner (ilk elemede başarısız, masrafsız bile eksi). |

## Strateji eklemek
1. `_SABLON.md` dosyasını kopyala, `cards/<strateji_adi>.md` olarak kaydet ve doldur (ya da Claude'a "şu fikirle yeni bir strateji kartı aç" de).
2. Kart onaylanınca kod `strategies/candidates/` altına yazılır; koşul kimlikleri (`[trend_up]` gibi) kodla birebir aynıdır.
3. Strateji test hattından geçer, sonuçlar kartın **Test geçmişi** tablosuna eklenir.

## Strateji çıkarmak
Stratejiler **silinmez**. Kartın durumu `retired` yapılır, **Emeklilik gerekçesi** yazılır, kod `strategies/retired/` altına taşınır. Böylece neyin neden işe yaramadığı kayıtlı kalır.

## Bir stratejiyi kapatmak / açmak
Sadece `active` durumdaki stratejiler sinyal üretebilir. Bir stratejiyi geçici olarak durdurmak için kartta durumu ve gerekçeyi yazıp Claude'a söylemen yeterli.
