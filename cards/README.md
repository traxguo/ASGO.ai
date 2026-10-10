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

## Strateji eklemek
1. `_SABLON.md` dosyasını kopyala, `cards/<strateji_adi>.md` olarak kaydet ve doldur (ya da Claude'a "şu fikirle yeni bir strateji kartı aç" de).
2. Kart onaylanınca kod `strategies/candidates/` altına yazılır; koşul kimlikleri (`[trend_up]` gibi) kodla birebir aynıdır.
3. Strateji test hattından geçer, sonuçlar kartın **Test geçmişi** tablosuna eklenir.

## Strateji çıkarmak
Stratejiler **silinmez**. Kartın durumu `retired` yapılır, **Emeklilik gerekçesi** yazılır, kod `strategies/retired/` altına taşınır. Böylece neyin neden işe yaramadığı kayıtlı kalır.

## Bir stratejiyi kapatmak / açmak
Sadece `active` durumdaki stratejiler sinyal üretebilir. Bir stratejiyi geçici olarak durdurmak için kartta durumu ve gerekçeyi yazıp Claude'a söylemen yeterli.
