# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-11-16 06:55 UTC. Son veri mumu: 2026-11-14 20:00 UTC.
16 coin, en fazla 3 işlem, başlangıç 2026-10-01. Dondurulmuş `PusulaTrendLong` hiç değişmez; `PusulaV2` arka plan turlarında kabul edilen geliştirmeleri taşır.

## GUO'ya not
- **Dondurulmuş Pusula:** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.35R** (yaklaşık %-5.3).
- **Pusula v2 (geliştirilmiş aday):** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.35R** (yaklaşık %-5.3).
- Bitcoin'in günlük skoru şu an -1. -1 veya altına inerse v2 açık long'ları kapatır.
- Bu strateji ayda 2-3 işlem açar; birkaç haftalık sonuç bir şey söylemez. Anlamlı karar için en az 2-3 ay gerekir.
- İçinde bulunulan ayın funding verisi ay bitince gelir; o yüzden bu ayın rakamları geçicidir.

## İşlemler

### Dondurulmuş Pusula (`PusulaTrendLong`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.07 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.04 |
| BTC | 2026-10-21 12:00 | 83365.8 | 2026-10-22 16:00 | stop | -1.07 |
| BNB | 2026-10-27 16:00 | 749.67 | 2026-10-29 20:00 | stop | -1.10 |

### Pusula v2 (geliştirilmiş aday) (`PusulaV2`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.07 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.04 |
| BTC | 2026-10-21 12:00 | 83365.8 | 2026-10-22 16:00 | stop | -1.07 |
| BNB | 2026-10-27 16:00 | 749.67 | 2026-10-29 20:00 | stop | -1.10 |


## Haftalık ek kontroller (2026-11-16)

**Veri:** 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-11-14 23:00 UTC, son kapanmış 4 saatlik mum 2026-11-14 20:00 UTC (15 Kasım'ın günlük arşivi henüz yayınlanmadı). Geçen haftanın 8 Kasım "henüz yok" işaretleri silinip yeniden indirildi; 8-14 Kasım arası eksiksiz geldi. Bilinen boşluklar aynı: 28 Ekim fiyat verisi 16 coinin hepsinde yok, mark price'ta 28 ve 29 Ekim yok. Bunların dışında 1 Ekim'den beri saatlik veride boşluk yok. Strateji kodu değişmedi.

**Sonuç:** Bu hafta yeni işlem açılmadı ve kapanmadı; şu an açık işlem yok. İki sürüm de aynı: 5 işlem, beşi de stop, toplam **-5,35R** (geçen hafta da -5,35R). Kasım'ın funding verisi ay bitince gelecek; bu ay işlem olmadığı için toplam değişmeyecek.

**Piyasa:** Hafta sert düşüşle geçti. Bitcoin'in son 4 saatlik kapanışı 64.130,5 (geçen hafta 75.836,0, yaklaşık %-15). Diğer coinler de %10-20 arası düştü.

**Tetiğe en yakın coinler:** Hiçbir coin long'a yakın değil; geçen haftadan daha uzak. Bitcoin puanı -1'de kaldı (günlük kapanış 50 günlük ortalamanın %12,6 altında); kural gereği Bitcoin +1 veya üstüne çıkmadan hiçbir coinde long açılmaz. +3 veya +1 coin yok. Testin kullandığı son günlük mumda (13 Kasım) 11 coin -1'de, 5 coin -3'te (DOGE, ADA, TRX, ATOM, XLM). Ortalamaya en yakın olanlar AVAX (-1, kapanış ortalamanın %8 altında, 90 günlük değişim +%27), BNB (-1, %11,5 altında) ve LTC (-1, %12,2 altında). 14 Kasım'ın günlük kapanışı (test bunu 15 Kasım'dan itibaren görür) daha da kötü: 13 coin -3'e indi, sadece BTC, LTC ve AVAX -1'de kaldı; hepsi ortalamanın %17-20 altında. Bitcoin'in 90 günlük değişimi +%2'ye indi; eksiye geçerse Bitcoin puanı -3 olur. Bu sürüm short açmadığı için -3 coinlerde işlem yok.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 5 işlem: her iki sürüm de **-5,13R** (normal hesapta -5,35R), geçen haftayla aynı. İşlem başına fark yaklaşık 0,02-0,06R; sonucu belirleyen yine komisyon değil, beş stop.

**Demo:** Kripto demo botları 2026-11-10'da kapatıldı; proje Nasdaq'a geçti. Bu yüzden demo karşılaştırması artık yapılmıyor. Pusula kâğıt takibi 2026-11-30'a kadar sessizce devam ediyor. Botların kapandığı tarihe kadar kâğıt testte 29 Ekim'den sonra yeni Pusula girişi olmadığı için botun kaçırdığı bir işlem de yoktu.

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): kararsız (-1/3).  
Son günlük kapanış 68.279,8, günlük 50 ortalama 78.160,2, 90 günlük değişim %8. Son 4 saatlik kapanış 64.130,5.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETH (4s): kararsız (-1/3).  
Son günlük kapanış 1.929,2, günlük 50 ortalama 2.319,3, 90 günlük değişim %3. Son 4 saatlik kapanış 1.768,4.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): kararsız (-1/3).  
Son günlük kapanış 78,17, günlük 50 ortalama 97,57, 90 günlük değişim %4. Son 4 saatlik kapanış 70,23.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XRP (4s): kararsız (-1/3).  
Son günlük kapanış 1,011, günlük 50 ortalama 1,264, 90 günlük değişim %1. Son 4 saatlik kapanış 0,9136.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): kararsız (-1/3).  
Son günlük kapanış 630,67, günlük 50 ortalama 712,49, 90 günlük değişim %4. Son 4 saatlik kapanış 582,12.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOGE (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,0645, günlük 50 ortalama 0,07799, 90 günlük değişim %-8. Son 4 saatlik kapanış 0,05735.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ADA (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1685, günlük 50 ortalama 0,2041, 90 günlük değişim %-6. Son 4 saatlik kapanış 0,1476.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

LINK (4s): kararsız (-1/3).  
Son günlük kapanış 9,852, günlük 50 ortalama 11,52, 90 günlük değişim %10. Son 4 saatlik kapanış 8,879.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LTC (4s): kararsız (-1/3).  
Son günlük kapanış 49,35, günlük 50 ortalama 56,2, 90 günlük değişim %13. Son 4 saatlik kapanış 44,47.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOT (4s): kararsız (-1/3).  
Son günlük kapanış 0,8182, günlük 50 ortalama 0,9986, 90 günlük değişim %7. Son 4 saatlik kapanış 0,7062.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

AVAX (4s): kararsız (-1/3).  
Son günlük kapanış 8,23, günlük 50 ortalama 8,947, 90 günlük değişim %27. Son 4 saatlik kapanış 7,097.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

TRX (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,3118, günlük 50 ortalama 0,3263, 90 günlük değişim %-6. Son 4 saatlik kapanış 0,3066.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ATOM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 1,373, günlük 50 ortalama 1,567, 90 günlük değişim %-9. Son 4 saatlik kapanış 1,259.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

BCH (4s): kararsız (-1/3).  
Son günlük kapanış 221,42, günlük 50 ortalama 267,05, 90 günlük değişim %8. Son 4 saatlik kapanış 201,20.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETC (4s): kararsız (-1/3).  
Son günlük kapanış 6,456, günlük 50 ortalama 7,487, 90 günlük değişim %4. Son 4 saatlik kapanış 5,803.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1461, günlük 50 ortalama 0,1726, 90 günlük değişim %-8. Son 4 saatlik kapanış 0,1354.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).
