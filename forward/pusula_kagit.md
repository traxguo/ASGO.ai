# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-10-26 06:58 UTC. Son veri mumu: 2026-10-24 20:00 UTC.
16 coin, en fazla 3 işlem, başlangıç 2026-10-01. Dondurulmuş `PusulaTrendLong` hiç değişmez; `PusulaV2` arka plan turlarında kabul edilen geliştirmeleri taşır.

## GUO'ya not
- **Dondurulmuş Pusula:** 4 işlem kapandı, 0 açık. Kapananların toplamı **-4.21R** (yaklaşık %-4.2).
- **Pusula v2 (geliştirilmiş aday):** 4 işlem kapandı, 0 açık. Kapananların toplamı **-4.21R** (yaklaşık %-4.2).
- Bitcoin'in günlük skoru şu an +3. -1 veya altına inerse v2 açık long'ları kapatır.
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

### Pusula v2 (geliştirilmiş aday) (`PusulaV2`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.05 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.03 |
| BTC | 2026-10-21 12:00 | 83365.8 | 2026-10-22 16:00 | stop | -1.07 |


## Haftalık ek kontroller (2026-10-26)

**Veri:** 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-10-24 23:00 UTC, son kapanmış 4 saatlik mum 2026-10-24 20:00 UTC (25 Ekim'in günlük arşivi henüz yayınlanmadı). Bu hafta bir veri sorunu bulundu ve düzeltildi: indirici, daha önce "henüz yok" cevabı aldığı günleri (9, 11 ve 18 Ekim) kalıcı olarak "yok" diye işaretlemişti; bu yüzden o üç günün saatlik verisi eksikti ve ilk denemede günlük veri de güncellenmemişti. İşaretler silinip veri yeniden indirildi; artık Ekim'de eksik mum yok (tek istisna: LINK'in 18 Ekim "mark price" arşivi Binance'te gerçekten yok, işlem sonucunu etkilemiyor). Düzeltme önceki üç işlemi değiştirmedi. Strateji kodu değişmedi.

**Bu hafta:** İki sürümde de 1 yeni işlem açıldı ve kapandı: BTC long, giriş 21 Ekim 12:00 (83.365,8), 22 Ekim 16:00'da stop, -1,07R. Toplam -3,14R'den **-4,21R**'ye indi (4 işlem, dördü de stop). Şu an açık işlem yok. Tetiğe en yakın coinler: BNB ve BCH (puan +3, günlük kapanış 20 günlük ortalamanın yaklaşık %0,3 altında; ortalamanın üstüne kapanırlarsa kırılım tetiği devreye girer), ardından BTC (ortalamanın %1,6 altında).

**Demo dolum fiyatı ile gerçek fiyat:** 19 Ekim'den bu yana Bitget demo hesabında Pusula dolumu yok; `forward/bitget_demo/events.csv` hem bu dalda hem `origin/main`'de hâlâ 10 Ekim'deki NEAR deneme işlemiyle bitiyor. Sebep: GitHub Actions'taki bütün demo botları (Pusula, Dalga, Fitil) 20 Ekim 13:30 UTC'den beri her çalışmada 3-4 saniyede hata verip duruyor (kayıt bile oluşmuyor; hesap/kullanım limiti gibi bir GitHub sorunu olabilir). Yani kâğıtta açılan 21 Ekim BTC işlemi demo hesapta açılmadı. Karşılaştırılacak dolum yok; geçen haftaki tek örnek (%+2,2 yüksek dolum) geçerli.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 4 işlem: her iki sürüm de **-4,06R** (normal hesapta -4,21R). İşlem başına fark yaklaşık 0,02-0,05R; sonucu belirleyen komisyon değil, dört stop. Ekim funding verisi ay sonunda gelecek (şu an 0).

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 81.160,0, günlük 50 ortalama 80.813,8, 90 günlük değişim %26. Son 4 saatlik kapanış 80.843,7.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (82.451,2) altında. Üstüne çıkınca tetik devreye girer.

ETH (4s): kararsız (+1/3).  
Son günlük kapanış 2.386,6, günlük 50 ortalama 2.473,4, 90 günlük değişim %27. Son 4 saatlik kapanış 2.357,6.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): kararsız (+1/3).  
Son günlük kapanış 102,79, günlük 50 ortalama 106,48, 90 günlük değişim %38. Son 4 saatlik kapanış 102,33.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XRP (4s): kararsız (-1/3).  
Son günlük kapanış 1,294, günlük 50 ortalama 1,37, 90 günlük değişim %18. Son 4 saatlik kapanış 1,299.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 739,76, günlük 50 ortalama 733,91, 90 günlük değişim %30. Son 4 saatlik kapanış 740,19.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (742,06) altında. Üstüne çıkınca tetik devreye girer.

DOGE (4s): kararsız (-1/3).  
Son günlük kapanış 0,07859, günlük 50 ortalama 0,08519, 90 günlük değişim %10. Son 4 saatlik kapanış 0,07762.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ADA (4s): kararsız (+1/3).  
Son günlük kapanış 0,2107, günlük 50 ortalama 0,227, 90 günlük değişim %28. Son 4 saatlik kapanış 0,2079.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LINK (4s): kararsız (+1/3).  
Son günlük kapanış 11,82, günlük 50 ortalama 12,38, 90 günlük değişim %41. Son 4 saatlik kapanış 11,62.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LTC (4s): kararsız (+1/3).  
Son günlük kapanış 57,24, günlük 50 ortalama 60,08, 90 günlük değişim %23. Son 4 saatlik kapanış 57.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOT (4s): kararsız (+1/3).  
Son günlük kapanış 1,085, günlük 50 ortalama 1,108, 90 günlük değişim %33. Son 4 saatlik kapanış 1,048.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

AVAX (4s): kararsız (+1/3).  
Son günlük kapanış 9,055, günlük 50 ortalama 9,526, 90 günlük değişim %34. Son 4 saatlik kapanış 8,988.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

TRX (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,33, günlük 50 ortalama 0,3335, 90 günlük değişim %-0. Son 4 saatlik kapanış 0,3291.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ATOM (4s): kararsız (+1/3).  
Son günlük kapanış 1,706, günlük 50 ortalama 1,719, 90 günlük değişim %23. Son 4 saatlik kapanış 1,64.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BCH (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 282,23, günlük 50 ortalama 277,50, 90 günlük değişim %35. Son 4 saatlik kapanış 277,54.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (283,03) altında. Üstüne çıkınca tetik devreye girer.

ETC (4s): kararsız (-1/3).  
Son günlük kapanış 7,761, günlük 50 ortalama 8,113, 90 günlük değişim %16. Son 4 saatlik kapanış 7,676.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1732, günlük 50 ortalama 0,1917, 90 günlük değişim %-3. Son 4 saatlik kapanış 0,1714.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).
