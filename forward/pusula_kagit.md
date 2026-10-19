# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-10-19 06:53 UTC. Son veri mumu: 2026-10-17 20:00 UTC.
16 coin, en fazla 3 işlem, başlangıç 2026-10-01. Dondurulmuş `PusulaTrendLong` hiç değişmez; `PusulaV2` arka plan turlarında kabul edilen geliştirmeleri taşır.

## GUO'ya not
- **Dondurulmuş Pusula:** 3 işlem kapandı, 0 açık. Kapananların toplamı **-3.14R** (yaklaşık %-3.1).
- **Pusula v2 (geliştirilmiş aday):** 3 işlem kapandı, 0 açık. Kapananların toplamı **-3.14R** (yaklaşık %-3.1).
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

### Pusula v2 (geliştirilmiş aday) (`PusulaV2`)

| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |
|---|---|---|---|---|---|
| BNB | 2026-10-03 20:00 | 789.24 | 2026-10-07 02:00 | stop | -1.05 |
| BTC | 2026-10-02 08:00 | 85947.4 | 2026-10-07 13:00 | stop | -1.06 |
| LTC | 2026-10-02 08:00 | 70.02 | 2026-10-07 21:00 | stop | -1.03 |


## Haftalık ek kontroller (2026-10-19)

**Veri:** Bu hafta 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-10-17 23:00 UTC, son kapanmış 4 saatlik mum 2026-10-17 20:00 UTC (18 Ekim'in günlük arşivi henüz yayınlanmadı). 11-17 Ekim arasında iki sürümde de yeni işlem açılmadı; toplam geçen haftayla aynı (-3,14R). Şu an tetiğe yakın bekleyen coinler DOT (1,213 üstü) ve ATOM (1,81 üstü).

**Demo dolum fiyatı ile gerçek fiyat:** 12 Ekim'den bu yana Bitget demo hesabında Pusula işlemi yok; Pusula botunun kayıt dosyasında (`forward/bitget_demo/events.csv`) son satır hâlâ 10 Ekim'deki NEAR deneme işlemi. Bu yüzden bu hafta karşılaştırılacak dolum yok. (Aynı hesaptaki Dalga botu bu hafta ATOM, ALGO ve FIL sinyallerini "demo hesapta listelenmiyor" diye atladı; bunlar Pusula işlemi değil.) Geçen haftaki tek örnek geçerliliğini koruyor: demo dolum gerçek Binance fiyatından %+2,2 yüksekti.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 3 işlem: her iki sürüm de **-3,04R** (normal hesapta -3,14R). Fark işlem başına yaklaşık 0,03R; sonucu belirleyen komisyon değil, üç stop.

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 81.578,3, günlük 50 ortalama 80.169,2, 90 günlük değişim %28. Son 4 saatlik kapanış 81.455,9.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (82.783,6) altında. Üstüne çıkınca tetik devreye girer.

ETH (4s): kararsız (+1/3).  
Son günlük kapanış 2.422,5, günlük 50 ortalama 2.491,3, 90 günlük değişim %30. Son 4 saatlik kapanış 2.401,6.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): kararsız (+1/3).  
Son günlük kapanış 104,39, günlük 50 ortalama 106,90, 90 günlük değişim %39. Son 4 saatlik kapanış 103,42.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XRP (4s): kararsız (+1/3).  
Son günlük kapanış 1,311, günlük 50 ortalama 1,387, 90 günlük değişim %21. Son 4 saatlik kapanış 1,294.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): kararsız (+1/3).  
Son günlük kapanış 721,88, günlük 50 ortalama 732,90, 90 günlük değişim %26. Son 4 saatlik kapanış 718,54.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOGE (4s): kararsız (+1/3).  
Son günlük kapanış 0,0809, günlük 50 ortalama 0,08702, 90 günlük değişim %12. Son 4 saatlik kapanış 0,07931.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ADA (4s): kararsız (+1/3).  
Son günlük kapanış 0,2256, günlük 50 ortalama 0,2286, 90 günlük değişim %40. Son 4 saatlik kapanış 0,2194.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LINK (4s): kararsız (+1/3).  
Son günlük kapanış 12,34, günlük 50 ortalama 12,42, 90 günlük değişim %48. Son 4 saatlik kapanış 11,98.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LTC (4s): kararsız (+1/3).  
Son günlük kapanış 59,69, günlük 50 ortalama 60, 90 günlük değişim %33. Son 4 saatlik kapanış 58,8.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOT (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 1,184, günlük 50 ortalama 1,093, 90 günlük değişim %38. Son 4 saatlik kapanış 1,115.  
Bitcoin puanı +3/3.  
LONG tetiği 1,213: 4 saatlik mum bunun üstünde kapanırsa giriş 1,202 - 1,213, stop 1,086, hedef yok: günlük kapanış 20 günlük ortalamanın altına inince çıkılır, fiyat 2R lehte gidince stop girişe çekilir (yaklaşık; kesin rakamlar kırılım mumunun kapanışından).  
Short yok: trende karşı işlem açmıyorum.

AVAX (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 9,953, günlük 50 ortalama 9,446, 90 günlük değişim %53. Son 4 saatlik kapanış 9,761.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (10,3) altında. Üstüne çıkınca tetik devreye girer.

TRX (4s): kararsız (+1/3).  
Son günlük kapanış 0,3354, günlük 50 ortalama 0,3346, 90 günlük değişim %4. Son 4 saatlik kapanış 0,3337.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ATOM (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 1,772, günlük 50 ortalama 1,698, 90 günlük değişim %17. Son 4 saatlik kapanış 1,7.  
Bitcoin puanı +3/3.  
LONG tetiği 1,81: 4 saatlik mum bunun üstünde kapanırsa giriş 1,798 - 1,81, stop 1,657, hedef yok: günlük kapanış 20 günlük ortalamanın altına inince çıkılır, fiyat 2R lehte gidince stop girişe çekilir (yaklaşık; kesin rakamlar kırılım mumunun kapanışından).  
Short yok: trende karşı işlem açmıyorum.

BCH (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 277,23, günlük 50 ortalama 276,45, 90 günlük değişim %25. Son 4 saatlik kapanış 275,39.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (287,70) altında. Üstüne çıkınca tetik devreye girer.

ETC (4s): kararsız (+1/3).  
Son günlük kapanış 7,967, günlük 50 ortalama 8,191, 90 günlük değişim %15. Son 4 saatlik kapanış 7,8.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): kararsız (-1/3).  
Son günlük kapanış 0,1813, günlük 50 ortalama 0,1962, 90 günlük değişim %-2. Son 4 saatlik kapanış 0,177.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.
