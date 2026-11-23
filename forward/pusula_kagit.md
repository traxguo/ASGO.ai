# Pusula kâğıt takibi (para yok, emir yok)

Güncelleme: 2026-11-23 06:53 UTC. Son veri mumu: 2026-11-21 20:00 UTC.
16 coin, en fazla 3 işlem, başlangıç 2026-10-01. Dondurulmuş `PusulaTrendLong` hiç değişmez; `PusulaV2` arka plan turlarında kabul edilen geliştirmeleri taşır.

## GUO'ya not
- **Dondurulmuş Pusula:** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.35R** (yaklaşık %-5.3).
- **Pusula v2 (geliştirilmiş aday):** 5 işlem kapandı, 0 açık. Kapananların toplamı **-5.35R** (yaklaşık %-5.3).
- Bitcoin'in günlük skoru şu an -3. -1 veya altına inerse v2 açık long'ları kapatır.
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


## Haftalık ek kontroller (2026-11-23)

**Veri:** 16 coinin verisi data.binance.vision'dan güncellendi; son saatlik mum 2026-11-21 23:00 UTC, son kapanmış 4 saatlik mum 2026-11-21 20:00 UTC (22 Kasım'ın günlük arşivi henüz yayınlanmadı). Geçen haftanın 15 Kasım "henüz yok" işaretleri (64 adet) silinip yeniden indirildi; 15-21 Kasım arası eksiksiz geldi. Bilinen boşluklar aynı: 28 Ekim fiyat verisi 16 coinin hepsinde yok, mark price'ta 28 ve 29 Ekim yok. Bunların dışında 1 Ekim'den beri saatlik ve 4 saatlik veride boşluk yok. Strateji kodu değişmedi.

**Sonuç:** Bu hafta da yeni işlem açılmadı ve kapanmadı; şu an açık işlem yok. İki sürüm de aynı: 5 işlem, beşi de stop, toplam **-5,35R** (geçen hafta da -5,35R). Son işlem 29 Ekim'de kapandı. Kasım'ın funding verisi ay bitince gelecek; bu ay işlem olmadığı için toplam değişmeyecek.

**Piyasa:** Düşüş sürdü ama geçen haftadan daha yavaş. Bitcoin'in son 4 saatlik kapanışı 60.191,0 (geçen hafta 64.130,5, yaklaşık %-6). Coinlerin çoğu %3-10 arası düştü (en çok LTC %-10,5; DOT, AVAX, ATOM %-7); SOL, XRP, TRX ve BCH yatay kaldı. Bitcoin'in 90 günlük değişimi eksiye geçti (%-25), bu yüzden Bitcoin puanı -1'den **-3**'e indi.

**Tetiğe en yakın coinler:** Hiçbir coin long'a yakın değil; geçen haftadan da uzak. Testin kullandığı son günlük mumda (20 Kasım) 16 coinin hepsi -3'te: hepsinde kapanış 50 günlük ortalamanın altında, 20 günlük ortalama 50 günlüğün altında ve 90 günlük değişim eksi. Kural gereği Bitcoin +1 veya üstüne çıkmadan hiçbir coinde long açılmaz; Bitcoin'in kapanışı ortalamanın %20,9 altında. Ortalamaya en yakın coin TRX (kapanış ortalamanın %6 altında, 90 günlük değişim %-12); geri kalanların hepsi %18-29 altında. 21 Kasım'ın günlük kapanışı (test bunu 22 Kasım'dan itibaren görür) tabloyu değiştirmiyor: yine 16 coin -3, Bitcoin ortalamanın %18,6 altında. Bu sürüm short açmadığı için -3 coinlerde işlem yok.

**Düşük komisyon senaryosu (sadece teşhis):** Emir başına %0,1 yerine %0,03 maliyetle aynı 5 işlem: her iki sürüm de **-5,13R** (normal hesapta -5,35R), geçen haftayla aynı. Sonucu belirleyen yine komisyon değil, beş stop.

**Demo:** Kripto demo botları 2026-11-10'da kapatıldı; proje Nasdaq'a geçti. Bu yüzden demo karşılaştırması artık yapılmıyor. Pusula kâğıt takibi 2026-11-30'a kadar sessizce devam ediyor; bir sonraki kontrol son haftalık kontrol olacak.

## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)

BTC (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 58.915,0, günlük 50 ortalama 74.497,2, 90 günlük değişim %-25. Son 4 saatlik kapanış 60.191,0.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ETH (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 1.622,0, günlük 50 ortalama 2.184,6, 90 günlük değişim %-36. Son 4 saatlik kapanış 1.684,9.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

SOL (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 68,82, günlük 50 ortalama 91,36, 90 günlük değişim %-27. Son 4 saatlik kapanış 70,26.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

XRP (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,9101, günlük 50 ortalama 1,188, 90 günlük değişim %-37. Son 4 saatlik kapanış 0,9316.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

BNB (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 540,95, günlük 50 ortalama 680,33, 90 günlük değişim %-21. Son 4 saatlik kapanış 548,68.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

DOGE (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,05436, günlük 50 ortalama 0,07314, 90 günlük değişim %-41. Son 4 saatlik kapanış 0,05526.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ADA (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1431, günlük 50 ortalama 0,1912, 90 günlük değişim %-38. Son 4 saatlik kapanış 0,1443.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

LINK (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 8,54, günlük 50 ortalama 10,91, 90 günlük değişim %-29. Son 4 saatlik kapanış 8,607.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

LTC (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 40,62, günlük 50 ortalama 53,15, 90 günlük değişim %-24. Son 4 saatlik kapanış 39,78.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

DOT (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,6622, günlük 50 ortalama 0,9294, 90 günlük değişim %-30. Son 4 saatlik kapanış 0,654.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

AVAX (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 6,516, günlük 50 ortalama 8,48, 90 günlük değişim %-17. Son 4 saatlik kapanış 6,58.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

TRX (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,3021, günlük 50 ortalama 0,3215, 90 günlük değişim %-12. Son 4 saatlik kapanış 0,3053.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ATOM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 1,225, günlük 50 ortalama 1,499, 90 günlük değişim %-23. Son 4 saatlik kapanış 1,17.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

BCH (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 194,57, günlük 50 ortalama 252,09, 90 günlük değişim %-33. Son 4 saatlik kapanış 199,60.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

ETC (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 5,47, günlük 50 ortalama 7,084, 90 günlük değişim %-35. Son 4 saatlik kapanış 5,491.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).

XLM (4s): güçlü düşüş (-3/3).  
Son günlük kapanış 0,1274, günlük 50 ortalama 0,1636, 90 günlük değişim %-37. Son 4 saatlik kapanış 0,129.  
Bitcoin puanı -3/3.  
İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).
