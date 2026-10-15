# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-10-12 06:51 UTC. Son veri mumu: 2026-10-10 20:00 UTC.
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


## Haftalık ek kontroller (2026-10-12)

**Veri:** Bu hafta 16 coinin verisi data.binance.vision'dan güncellendi; son mum 2026-10-10 23:00 UTC (11 Ekim'in günlük arşivi henüz yayınlanmadı). 5-10 Ekim arasında yeni işlem açılmadı; geçen haftaya göre değişiklik yok.

**Demo dolum fiyatı ile gerçek fiyat:** Bu hafta Bitget demo hesabında Pusula işlemi olmadı (dalga botu 12 Ekim'de ALGO sinyalini "demo hesapta listelenmiyor" diye atladı). Tek dolum, 10 Ekim 13:50 UTC'deki NEAR deneme işlemi (strateji işlemi değil): demo dolum 5,471, demo'nun kendi anlık fiyatı 5,444, aynı dakikada gerçek Binance fiyatı yaklaşık 5,351 (1 dakikalık mum 5,345-5,362). Fark: demo dolum gerçek fiyattan **%+2,2** yüksek (demo'nun kendi fiyatına göre %+0,5). Tek örnek; demo fiyatları gerçek piyasadan sapabilir, bu yüzden demo sonuçları kâğıt takibinin yerini tutmaz.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 3 işlem: her iki sürüm de **-3,04R** (normal hesapta -3,14R). Fark işlem başına yaklaşık 0,03R; sonucu değiştiren şey komisyon değil, üç stop.

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 81.711,0, günlük 50 ortalama 79.620,4, 90 günlük değişim %27. Son 4 saatlik kapanış 82.941,0.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (83.299,8) altında. Üstüne çıkınca tetik devreye girer.

ETH (4s): kararsız (+1/3).  
Son günlük kapanış 2.474,0, günlük 50 ortalama 2.501,5, 90 günlük değişim %38. Son 4 saatlik kapanış 2.504,9.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

SOL (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 109,57, günlük 50 ortalama 107,15, 90 günlük değişim %40. Son 4 saatlik kapanış 110,04.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (115,62) altında. Üstüne çıkınca tetik devreye girer.

XRP (4s): kararsız (+1/3).  
Son günlük kapanış 1,379, günlük 50 ortalama 1,398, 90 günlük değişim %25. Son 4 saatlik kapanış 1,402.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

BNB (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 735,77, günlük 50 ortalama 732,55, 90 günlük değişim %28. Son 4 saatlik kapanış 750,32.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (765,75) altında. Üstüne çıkınca tetik devreye girer.

DOGE (4s): kararsız (+1/3).  
Son günlük kapanış 0,08401, günlük 50 ortalama 0,08822, 90 günlük değişim %13. Son 4 saatlik kapanış 0,08573.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ADA (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 0,232, günlük 50 ortalama 0,2273, 90 günlük değişim %39. Son 4 saatlik kapanış 0,2491.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (0,2445) altında. Üstüne çıkınca tetik devreye girer.

LINK (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 12,7, günlük 50 ortalama 12,38, 90 günlük değişim %59. Son 4 saatlik kapanış 13.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (13,45) altında. Üstüne çıkınca tetik devreye girer.

LTC (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 63,13, günlük 50 ortalama 59,75, 90 günlük değişim %41. Son 4 saatlik kapanış 63,98.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (65,7) altında. Üstüne çıkınca tetik devreye girer.

DOT (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 1,089, günlük 50 ortalama 1,07, 90 günlük değişim %24. Son 4 saatlik kapanış 1,258.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (1,152) altında. Üstüne çıkınca tetik devreye girer.

AVAX (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 10,07, günlük 50 ortalama 9,266, 90 günlük değişim %50. Son 4 saatlik kapanış 10,36.  
Bitcoin puanı +3/3.  
Şimdilik long yok: günlük kapanış 20 günlük ortalamanın (10,46) altında. Üstüne çıkınca tetik devreye girer.

TRX (4s): kararsız (+1/3).  
Son günlük kapanış 0,3325, günlük 50 ortalama 0,3355, 90 günlük değişim %1. Son 4 saatlik kapanış 0,3306.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ATOM (4s): güçlü yükseliş (+3/3).  
Son günlük kapanış 1,76, günlük 50 ortalama 1,668, 90 günlük değişim %11. Son 4 saatlik kapanış 1,95.  
Bitcoin puanı +3/3.  
LONG tetiği 2,076: 4 saatlik mum bunun üstünde kapanırsa giriş 2,058 - 2,076, stop 1,637, hedef yok: günlük kapanış 20 günlük ortalamanın altına inince çıkılır, fiyat 2R lehte gidince stop girişe çekilir (yaklaşık; kesin rakamlar kırılım mumunun kapanışından).  
Short yok: trende karşı işlem açmıyorum.

BCH (4s): kararsız (+1/3).  
Son günlük kapanış 270,98, günlük 50 ortalama 277,14, 90 günlük değişim %11. Son 4 saatlik kapanış 279,95.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

ETC (4s): kararsız (+1/3).  
Son günlük kapanış 8,042, günlük 50 ortalama 8,223, 90 günlük değişim %14. Son 4 saatlik kapanış 8,409.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.

XLM (4s): kararsız (+1/3).  
Son günlük kapanış 0,1919, günlük 50 ortalama 0,1986, 90 günlük değişim %1. Son 4 saatlik kapanış 0,1965.  
Bitcoin puanı +3/3.  
İşlem önermiyorum: trend yönü belli değil. Long için puanın +3, short için -3 olması gerekir.
