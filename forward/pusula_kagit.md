# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-11-09 07:29 UTC. Son veri mumu: 2026-11-07 20:00 UTC.
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


## Haftalık ek kontroller (2026-11-09)

**Veri:** 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-11-07 23:00 UTC, son kapanmış 4 saatlik mum 2026-11-07 20:00 UTC (8 Kasım'ın günlük arşivi henüz yayınlanmadı). Geçen haftanın Ekim/Kasım "henüz yok" işaretleri silinip yeniden indirildi. Ekim'in aylık arşivi artık yayında (fiyat, mark price ve funding), o yüzden bu hafta günlük-günlük yardımcıya gerek kalmadı. **28 Ekim boşluğu hâlâ dolmadı:** Binance Ekim'in aylık arşivini de 28 Ekim olmadan yayınladı (16 coinin hepsi, saatlik/4 saatlik/günlük); 28 Ekim'in günlük dosyası hâlâ yok. Mark price'ta 28 ve 29 Ekim eksik. Bu boşluk Binance tarafında kalıcı olabilir. Strateji kodu değişmedi.

**Toplam neden -5,29R'den -5,35R'ye indi:** Bu hafta yeni işlem açılmadı ve kapanmadı. Fark, Ekim funding verisinin gelmesinden: geçen hafta funding 0 sayılıyordu, şimdi gerçek ödemeler dahil. BNB (3 Ekim) -1,05 → -1,07R, LTC -1,03 → -1,04R, BNB (27 Ekim) -1,08 → -1,10R; iki BTC işlemi aynı. İki sürüm de aynı: 5 işlem, beşi de stop, **-5,35R**. Şu an açık işlem yok.

**BNB işlemi (27 Ekim, 749,67):** Giriş, stop (731,87) ve çıkış zamanı (29 Ekim 20:00) değişmedi; sadece funding yüzünden -1,08R → -1,10R oldu. 28 Ekim verisi hâlâ olmadığı için test bu günü göremiyor. Teşhis için Binance'in spot (vadeli değil) BNB verisine baktım: 28 Ekim'de spot en düşük 742,0, en yüksek 762,2. Bu stop'un (731,87) yaklaşık %1,4 üstünde ve 2R seviyesinin (yaklaşık 785) çok altında; yani o gün büyük ihtimalle ne stop ne başka bir şey tetiklendi, sonuç büyük ihtimalle doğru. Kesin değil: vadeli fiyat spot'tan biraz farklı olabilir ve boşluk günü başka bir coinde giriş olup olmadığını bilemiyoruz.

**Tetiğe en yakın coinler:** Şu an hiçbir coin long'a yakın değil. Bitcoin puanı +1'den -1'e indi (günlük kapanış 50 günlük ortalamanın yaklaşık %5 altında); kural gereği Bitcoin tekrar +1 veya üstüne çıkmadan hiçbir coinde long açılmaz. +3 coin yok. En yakınlar: BNB (-1, kapanış ortalamanın %4,3 altında) ve BTC (-1, %5,0 altında); ikisinde de 90 günlük değişim artıda, ama +3 için hem kapanışın 50 günlük ortalamanın üstüne çıkması hem 20 günlük ortalamanın 50 günlüğü yukarı kesmesi gerekir. BCH +1'e indi (geçen hafta +3'tü; kapanış ortalamanın %5 altında, son 4 saatlik kapanış 249,49). ADA, TRX ve XLM -3'te (güçlü düşüş), ama bu sürüm short açmıyor.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 5 işlem: her iki sürüm de **-5,13R** (normal hesapta -5,35R). İşlem başına fark yaklaşık 0,02-0,06R; sonucu belirleyen yine komisyon değil, beş stop.

**Bitget demo:** Demo hesapta hâlâ hiç Pusula dolumu yok. `forward/bitget_demo/events.csv` hem bu dalda hem `origin/main`'de 10 Ekim'deki NEAR deneme işlemiyle bitiyor; `dashboard/canli/demo_gercek_kontrol.csv`'de de Pusula satırı yok (sadece Fitil). Pusula demo botu 29 Ekim'den beri her çalışmada başarılı (son 100 çalışmanın hepsi başarılı, en sonuncusu 9 Kasım 06:00 UTC). 29 Ekim'den beri kâğıt testte de yeni Pusula girişi olmadığı için botun açmadığı bir işlem yok; karşılaştırılacak dolum yok.

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): kararsız (-1/3).  
Son günlük kapanış 75.810,1, günlük 50 ortalama 79.773,3, 90 günlük değişim %17. Son 4 saatlik kapanış 75.836,0.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETH (4s): kararsız (-1/3).  
Son günlük kapanış 2.237,6, günlük 50 ortalama 2.399,1, 90 günlük değişim %17. Son 4 saatlik kapanış 2.239,0.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): kararsız (-1/3).  
Son günlük kapanış 90,1, günlük 50 ortalama 101,98, 90 günlük değişim %22. Son 4 saatlik kapanış 89,77.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XRP (4s): kararsız (-1/3).  
Son günlük kapanış 1,179, günlük 50 ortalama 1,326, 90 günlük değişim %15. Son 4 saatlik kapanış 1,163.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): kararsız (-1/3).  
Son günlük kapanış 694,08, günlük 50 ortalama 725,20, 90 günlük değişim %17. Son 4 saatlik kapanış 696,77.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOGE (4s): kararsız (-1/3).  
Son günlük kapanış 0,07238, günlük 50 ortalama 0,08122, 90 günlük değişim %4. Son 4 saatlik kapanış 0,0716.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ADA (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,184, günlük 50 ortalama 0,2136, 90 günlük değişim %-8. Son 4 saatlik kapanış 0,1816.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

LINK (4s): kararsız (-1/3).  
Son günlük kapanış 10,85, günlük 50 ortalama 11,91, 90 günlük değişim %33. Son 4 saatlik kapanış 10,83.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

LTC (4s): kararsız (-1/3).  
Son günlük kapanış 52,59, günlük 50 ortalama 58,04, 90 günlük değişim %16. Son 4 saatlik kapanış 52,16.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

DOT (4s): kararsız (-1/3).  
Son günlük kapanış 0,913, günlük 50 ortalama 1,047, 90 günlük değişim %12. Son 4 saatlik kapanış 0,8978.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

AVAX (4s): kararsız (-1/3).  
Son günlük kapanış 8,339, günlük 50 ortalama 9,147, 90 günlük değişim %30. Son 4 saatlik kapanış 8,226.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

TRX (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,318, günlük 50 ortalama 0,3294, 90 günlük değişim %-3. Son 4 saatlik kapanış 0,3198.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ATOM (4s): kararsız (-1/3).  
Son günlük kapanış 1,387, günlük 50 ortalama 1,628, 90 günlük değişim %2. Son 4 saatlik kapanış 1,374.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BCH (4s): kararsız (+1/3).  
Son günlük kapanış 263,66, günlük 50 ortalama 278,21, 90 günlük değişim %23. Son 4 saatlik kapanış 249,49.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETC (4s): kararsız (-1/3).  
Son günlük kapanış 7,019, günlük 50 ortalama 7,749, 90 günlük değişim %8. Son 4 saatlik kapanış 6,911.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1533, günlük 50 ortalama 0,1808, 90 günlük değişim %-5. Son 4 saatlik kapanış 0,1512.  
Bitcoin puanı -1/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).
