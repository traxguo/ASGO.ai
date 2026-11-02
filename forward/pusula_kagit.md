# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-11-02 06:57 UTC. Son veri mumu: 2026-10-31 20:00 UTC.
16 coin, en fazla 3 işlem, başlangıç 2026-10-01. Dondurulmuş `PusulaTrendLong` hiç değişmez; `PusulaV2` arka plan turlarında kabul edilen geliştirmeleri taşır.

## GUO'ya not
- **Dondurulmuş Pusula:** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.29R** (yaklaşık %-5.3).
- **Pusula v2 (geliştirilmiş aday):** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.29R** (yaklaşık %-5.3).
- Bitcoin'in günlük skoru şu an +1. -1 veya altına inerse v2 açık long'ları kapatır.
- Bu strateji ayda 2-3 işlem açar; birkaç haftalık sonuç bir şey söylemez. Anlamlı karar için en az 2-3 ay gerekir.
- İçinde bulunulan ayın funding verisi ay bitince gelir; o yüzden bu ayın rakamları geçicidir.

## İşlemler

### Dondurulmuş Pusula (`PusulaTrendLong`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.05 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.03 |
| BTC | 2026-10-21 12:00 | 83365.8 | 2026-10-22 16:00 | stop | -1.07 |
| BNB | 2026-10-27 16:00 | 749.67 | 2026-10-29 20:00 | stop | -1.08 |

### Pusula v2 (geliştirilmiş aday) (`PusulaV2`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.05 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.03 |
| BTC | 2026-10-21 12:00 | 83365.8 | 2026-10-22 16:00 | stop | -1.07 |
| BNB | 2026-10-27 16:00 | 749.67 | 2026-10-29 20:00 | stop | -1.08 |


## Haftalık ek kontroller (2026-11-02)

**Veri:** 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-10-31 23:00 UTC, son kapanmış 4 saatlik mum 2026-10-31 20:00 UTC (1 Kasım'ın günlük arşivi ve Ekim'in aylık arşivi henüz yayınlanmadı). Geçen haftaki "henüz yok" işaretleri silinip yeniden indirildi. **Bir veri boşluğu var:** 28 Ekim'in bütün günü (16 coinin hepsi, saatlik/4 saatlik/günlük) Binance arşivinde henüz yok; "mark price" verisinde 28 ve 29 Ekim eksik. Bu boşluk aşağıdaki BNB işleminin içine düşüyor, o yüzden bu işlemin sonucu Ekim'in aylık arşivi gelince yeniden kontrol edilmeli. İndirici bu hafta, aylık arşiv yokken Ekim'i günlük arşivlerden alacak şekilde (kod değiştirilmeden, dışarıdan) çalıştırıldı; yoksa Ekim verisi tamamen düşecekti. Strateji kodu değişmedi.

**Bu hafta:** İki sürümde de 1 yeni işlem açıldı ve kapandı: BNB long, giriş 27 Ekim 16:00 (749,67), 29 Ekim 20:00'da stop (731,87; o saatte BNB 677,76'ya kadar sert bir iğne yaptı), -1,08R. Toplam -4,21R'den **-5,29R**'ye indi (5 işlem, beşi de stop). Şu an açık işlem yok. Tetiğe en yakın coin: BCH (puan +3, long tetiği 297,85; son 4 saatlik kapanış 285,09, yaklaşık %4,5 aşağıda). Başka +3 coin yok; BTC, BNB ve AVAX +1'de (günlük kapanış 50 günlük ortalamanın %4-9 altında), long için önce puanın +3'e dönmesi gerekir. Bitcoin puanı +3'ten +1'e indi.

**Demo dolum fiyatı ile gerçek fiyat:** Bitget demo hesabında hâlâ Pusula dolumu yok; `forward/bitget_demo/events.csv` hem bu dalda hem `origin/main`'de 10 Ekim'deki NEAR deneme işlemiyle bitiyor. GitHub Actions botları geri döndü: Fitil ve Dalga 28 Ekim 19:20 UTC'den beri her saat kayıt yazıyor, Pusula demo botu 29 Ekim 00:02 UTC'den beri her 4 saatte başarıyla çalışıyor (öncesinde 28 Ekim 20:56'ya kadar hepsi hata veriyordu). BNB işlemi 27 Ekim'de, bot kapalıyken açıldığı için demo hesapta açılmadı. Karşılaştırılacak yeni dolum yok.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 5 işlem: her iki sürüm de **-5,09R** (normal hesapta -5,29R). İşlem başına fark yaklaşık 0,02-0,06R; sonucu belirleyen komisyon değil, beş stop. Ekim funding verisi henüz yayınlanmadı (şu an 0).

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): kararsız (+1/3).  
Son günlük kapanış 77.312,6, günlük 50 ortalama 80.524,4, 90 günlük değişim %23. Son 4 saatlik kapanış 77.522,6.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETH (4s): kararsız (-1/3).  
Son günlük kapanış 2.243,6, günlük 50 ortalama 2.437,8, 90 günlük değişim %21. Son 4 saatlik kapanış 2.254,5.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): kararsız (-1/3).  
Son günlük kapanış 96,3, günlük 50 ortalama 104,99, 90 günlük değişim %32. Son 4 saatlik kapanış 95,44.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XRP (4s): kararsız (-1/3).  
Son günlük kapanış 1,256, günlük 50 ortalama 1,352, 90 günlük değişim %18. Son 4 saatlik kapanış 1,251.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): kararsız (+1/3).  
Son günlük kapanış 704,37, günlük 50 ortalama 732,51, 90 günlük değişim %20. Son 4 saatlik kapanış 704,17.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOGE (4s): kararsız (-1/3).  
Son günlük kapanış 0,07593, günlük 50 ortalama 0,08344, 90 günlük değişim %9. Son 4 saatlik kapanış 0,07559.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ADA (4s): kararsız (-1/3).  
Son günlük kapanış 0,1952, günlük 50 ortalama 0,2215, 90 günlük değişim %16. Son 4 saatlik kapanış 0,1928.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LINK (4s): kararsız (-1/3).  
Son günlük kapanış 11,45, günlük 50 ortalama 12,15, 90 günlük değişim %40. Son 4 saatlik kapanış 11,65.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LTC (4s): kararsız (-1/3).  
Son günlük kapanış 55,96, günlük 50 ortalama 59,29, 90 günlük değişim %26. Son 4 saatlik kapanış 55,73.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOT (4s): kararsız (-1/3).  
Son günlük kapanış 0,9734, günlük 50 ortalama 1,084, 90 günlük değişim %28. Son 4 saatlik kapanış 0,9456.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

AVAX (4s): kararsız (+1/3).  
Son günlük kapanış 8,541, günlük 50 ortalama 9,363, 90 günlük değişim %34. Son 4 saatlik kapanış 8,565.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

TRX (4s): kararsız (-1/3).  
Son günlük kapanış 0,3288, günlük 50 ortalama 0,3336, 90 günlük değişim %1. Son 4 saatlik kapanış 0,3035.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ATOM (4s): kararsız (-1/3).  
Son günlük kapanış 1,551, günlük 50 ortalama 1,693, 90 günlük değişim %26. Son 4 saatlik kapanış 1,496.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BCH (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 293,77, günlük 50 ortalama 278,82, 90 günlük değişim %40. Son 4 saatlik kapanış 285,09.  
Bitcoin puanı +1/3.  
LONG tetiği 297,85: 4 saatlik mum bunun üstünde kapanırsa giriş 295,95 - 297,85, stop 277,78, hedef yok: günlük kapanış 20 günlük ortalamanın altına inince çıkılır, fiyat 2R lehte gidince stop girişe çekilir (yaklaşık; kesin rakamlar kırılım mumunun kapanışından).  
Short yok: trende karşı işlem açmıyorum.

ETC (4s): kararsız (-1/3).  
Son günlük kapanış 7,224, günlük 50 ortalama 7,971, 90 günlük değişim %9. Son 4 saatlik kapanış 7,095.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1708, günlük 50 ortalama 0,1868, 90 günlük değişim %-1. Son 4 saatlik kapanış 0,1695.  
Bitcoin puanı +1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).
