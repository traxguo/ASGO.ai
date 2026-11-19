# Aslan 5 dk kuralı (Nasdaq'ta son fikir hakkı)

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı ve commit edildi, 2026-11-19)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı; sonradan değiştirilmez. Sonuçlar 2. bölüme eklenir.

**Kaynak:** Aslan'ın 2026-11-16/17 tarihli 4 gerçek işleminin ekran görüntüleri (2 kazanç, 2 kayıp) ve proje sahibi
üzerinden verdiği cevaplar (2026-11-19, proje konusu). Kural Türkçe olarak proje sahibine yazıldı (7 madde); bu
dosya onun bilgisayar için kesin halidir. Planın (`docs/nasdaq_plan.md`) **3. ve son** fikir hakkıdır.
Daha önce denenen Aslan kuralları (1 sa / 15 dk / 1 dk, likidite alımı + MSS, günlük yön filtresi) tekrar değildir:
bu kuralda likidite alımı ve yön filtresi yok, giriş saf 5 dk yapı kırılımı, hedef bir seviye.

**Veri:** HistData NAS100 (nsxusd) 5 dk mumlar, sadece alış fiyatı (`research/endeks_forex/fetch.py`,
`research/endeks_forex/batch.py::load` ile aynı temizlik). Hacim yok. **Kasa (2026-04 → 2026-09) yüklenmez.**

**Dönemler:** geliştirme 2020-01-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31 (giriş zamanına göre).

**Puan → yüzde:** Aslan puanla konuşuyor (fiyat ~27.000 iken). Fiyat 2020'de ~9.000 olduğu için eşikler yüzde ile
sabitlenir: 20 puan ≈ %0.075, 30 puan ≈ %0.11, 5 puan ≈ %0.02, 10 puan ≈ %0.04.

### Kural (short; long tam simetrik)
1. **Salınım (tepe/dip):** 5 dk mum i, solundaki 2 ve sağındaki 2 mumdan kesin yüksek tepeye sahipse tepe
   (kesin alçak dipse dip). i+2 mumu kapanınca onaylanır; ondan önce kullanılmaz.
2. **Trend:** k mumu kapandığında onaylı son iki tepe yükseliyor (T2 > T1) ve onaylı son iki dip yükseliyor (D2 > D1).
3. **Tetik (MSP):** k mumu son onaylı dibin (D2) **altında kapatır** ve k-1 mumu D2'nin altında kapatmamıştır.
4. **Saat:** k mumunun kapanışı TR 09:00 - 22:00 arasında (UTC 06:00 - 19:00, sabit).
5. **Giriş:** k mumunun kapanış fiyatı.
6. **Stop:** T2 mumundan k mumuna kadar en yüksek iğne (son tepenin iğne ucu; onaylanmamış daha yüksek bir iğne
   varsa o). Risk = stop − giriş; risk %0.04'ten küçük veya %0.6'dan büyükse işlem yok.
7. **Hedef (en yakın alınmamış seviye):** girişin altındaki adaylar, k anında **alınmamış** olanlar:
   önceki işlem gününün dibi (işlem günü New York 17:00 → 17:00), bugünün Asya seansı dibi (TR 02:00 - 09:00,
   seans bittiyse), bugünün Londra seansı dibi (TR 10:00 - 15:00, seans bittiyse), son 5 günün 1 saatlik onaylı dipleri
   (1 sa mumlar, 2/2 salınım). "Alınmamış" = oluştuğu andan k'ya kadar hiçbir mumun iğnesi o seviyeye değmemiş.
   Girişten en az %0.075 aşağıdaki adaylardan **en yakını** seçilir. Kâr al emri o seviyenin %0.02 önüne konur
   (short'ta seviyenin biraz üstü). Aday yoksa işlem yok. R'ye bakılmaz.
8. **Girmez:** (a) k mumunun kapanışı New York 09:30 - 09:45 (dahil) arasında; (b) girişin %0.11 **üstünde veya
   daha yakınında** alınmamış bir yukarı seviye varsa (7. maddedeki adayların tepe karşılıkları: önceki gün tepesi,
   Asya tepesi, Londra tepesi, 1 sa tepeler). Long'ta: girişin %0.11 altında alınmamış dip varsa girmez.
9. **Çıkış:** her 5 dk mumda önce stop, sonra hedef kontrol edilir (aynı mumda ikisi de değerse stop). Stop
   boşlukla geçilirse mumun açılışından çıkılır. 24 saat içinde ikisi de olmazsa o mumun kapanışından çıkılır.
10. **Aynı anda tek işlem.** İşlem kapanınca sonraki mumdan itibaren yeniden aranır. Long ve short aynı mumda
    tetiklenirse o mumda işlem yok.

**Masraf:** gidiş-dönüş %0.010 + New York 17:00'yi geçen her gece için gecelik finansman (long yıllık %5, short
yıllık %2.5, `research/endeks_forex/batch.py` ile aynı). Her şey bir de 2 kat masrafla. Sonuç **R** cinsinden
(net getiri / risk yüzdesi); düşüş işlem başı %1 risk ile bileşik hesaplanır.

**Rastgele kontrol:** her gerçek işlem için aynı dönemden, TR 09:00 - 22:00 içinde rastgele bir 5 dk mum kapanışı;
aynı yön, aynı stop ve hedef uzaklığı (yüzde), aynı çıkış kuralları. 2000 set;
p = (1 + rastgele ortalama R'nin gerçek ortalamaya eşit/üstünde olduğu set) / 2001.

**Yargı birimi:** long ve short **ayrı ayrı**.

### Ek (2026-11-19 17:14 UTC, Aslan'ın ek kuralı; hiçbir sonuç görülmeden eklendi)
İlk test çalıştırması bu ek geldiği için iptal edildi (17:16 UTC); hiçbir sonuç dosyası oluşmadı ve okunmadı.
Aslan: "büyük zaman dilimindeki destek/direnç veya FVG'lere dikkat; 1 sa / 4 sa önemli seviyelerde FVG/iFVG onayı ve
MSP olmalı; yoksa 4 sa FVG'ye iğne atıp döner, ters köşede kalırız." Ana ayara eklenen madde:

8. (c) **Büyük zaman dilimi engeli → 5 dk onay şart.** Engel = (i) 1 sa veya 4 sa grafikte son 10 günde oluşmuş,
   henüz kapatılmamış **ters yönlü FVG** (long için düşüş FVG'si, short için yükseliş FVG'si), ya da (ii) 4 sa grafikte
   onaylı, alınmamış bir **tepe** (long için) / **dip** (short için). Girişin bu engelin içinde olması veya engelin
   yakın kenarının işlem yönünde girişe %0.11'den yakın olması durumunda işlem **sadece 5 dk onay varsa** açılır.
   5 dk onay = stop mumundan k mumuna kadarki dönüş hareketinde işlem yönünde bir 5 dk FVG oluşmuş olması, **veya**
   ters yönlü bir 5 dk FVG'nin (stop mumundan en fazla 20 mum önce ile k arasında oluşmuş) üstünde (short'ta altında)
   kapanış (iFVG). Onay yoksa işlem yok.
   Tanımlar: yükseliş FVG = 3 mumda üçüncünün dibi birincinin tepesinden yüksek (bölge arası boşluk); düşüş FVG tersi.
   FVG, bir 5 dk mum uzak kenarının ötesinde kapatınca "kapatılmış" sayılır. 4 sa mumlar New York 17:00'den başlar
   (17-21-01-05-09-13), 1 sa mumlar saat başı. Büyük zaman dilimi FVG'si ve tepesi, ilgili mumlar kapandıktan sonra
   kullanılır.

### Bilgi ızgarası (sadece bilgi, seçim yapılmaz)
Sabit hedef 1R / 1.5R / 2R (7. madde yerine); 8(b) filtresi kapalı; 8(c) kapalı (ekten önceki kural);
sadece New York saatleri (TR 16:30 - 22:00).

### Geçme çıtası (`docs/decisions.md` 2026-11-09; ana ayar, yargı birimi başına, hepsi gerekli)
1. Net ortalama R > 0 ve kâr faktörü (PF) ≥ 1.2, hem geliştirmede hem doğrulamada.
2. Geliştirmede rastgele kontrolden iyi: p < 0.05.
3. 2 kat masrafla net ortalama R > 0, hem geliştirmede hem doğrulamada.
4. Doğrulamada ≥ 30 işlem.
5. İşlem başı %1 riskle en büyük düşüş ≤ %25, hem geliştirmede hem doğrulamada.

Kazanma oranı sadece bilgi. Al-tut kıyası raporlanır. Geçerse kâğıt takibe alınır (gerçek emir yok); Aslan Nasdaq
1 sa hattının yerine geçmez, yanına eklenir. Geçmezse dördüncü fikir aranmaz (plan). Kötü sonuç gizlenmez.

**Bilinen sınır:** Aslan'ın "seviyenin gücü", "hacim çok fazla", "manipülasyona müsait" gibi göz kararı yargıları
kodlanamaz; 7 ve 8. maddeler bunların sade yaklaşığıdır. Kural geçmezse bu "Aslan'ın yöntemi çalışmıyor" değil,
"yöntemin yazılabilen kısmı tek başına yetmiyor" demektir.

Kod: `research/aslan_5dk/run.py`. İş akışı: `.github/workflows/aslan_5dk.yml` (GitHub sunucusunda çalışır, sonuç
CSV'lerini bu klasöre commit'ler).

---

## 2. Sonuçlar (2026-11-19, gerçek veri, GitHub sunucusunda çalıştı)

### GUO'ya not
- Aslan'ın 5 dakikalık kuralı, bilgisayarın yazabildiği haliyle, **geçmedi**. Long da short da sıfırın biraz altında.
- Kural rastgele zamanlarda aynı stop ve hedefle açılan işlemlerden **daha iyi değil**. Yani giriş anı bir avantaj taşımıyor.
- Bu, "Aslan kötü trader" demek değil. Aslan'ın göz kararı seçimi (hangi kurulumu atlayacağı, seviyenin gücü) koda tam
  geçmiyor. Bilgisayar ayda ~45 işlem açtı. Aslan bunların çok küçük bir kısmını seçiyordur.
- Planın 3 fikir hakkı bitti, üçü de geçmedi. Plan gereği dördüncü fikir aranmaz. Aslan Nasdaq (1 sa) canlı takibi sürüyor.

### Ana ayar (yargılanan satırlar)

| Yön | Geliştirme: işlem / ort. R / PF / kazanma | Doğrulama: işlem / ort. R / PF / kazanma | 2x masraf (gel. / doğ.) | Rastgele kontrol (gel.) | Düşüş %1 risk (gel. / doğ.) | Sonuç |
|---|---|---|---|---|---|---|
| Long | 1295 / -0.033 / 0.95 / %41 | 305 / -0.015 / 0.98 / %39 | -0.090 / -0.079 | -0.027R, p 0.56 | %60 / %30 | **geçmedi** |
| Short | 1450 / -0.109 / 0.85 / %34 | 386 / -0.007 / 0.99 / %36 | -0.172 / -0.080 | -0.089R, p 0.68 | %90 / %44 | **geçmedi** |

Ortalama stop %0.25 (bugünkü fiyatla ~65 puan), ortalama hedef 2.7R. Ayda ~45 işlem (iki yön). Çıkış: 2134 stop
(-1.09R), 1227 hedef (+1.65R), 75 süre doldu. Al-tut (NAS100): geliştirme +%142 (düşüş %38), doğrulama +%9 (düşüş %26).

Yıllara göre (toplam R, short / long): 2020 +33 / +15, 2021 -59 / -4, 2022 -26 / -12, 2023 -64 / +9, 2024 -43 / -51,
2025 -32 / -17, 2026 Q1 +30 / +12. Tutarlı bir artı yıl dizisi yok.

### Filtrelerin etkisi (huni, ana ayar)
12.288 yapı kırılımı → saat dışı 4.759, NY açılışı 352, stop çok dar/geniş 676, yakın likidite (8b) 164, hedef yok 375,
büyük zaman dilimi engeli + onay yok (8c) 114, açık işlem varken 2.412 → **3.436 işlem**. 8c'de engel 1.574 kez çıktı;
1.460'ında 5 dk FVG/iFVG onayı vardı. Yani onay neredeyse her zaman var ve filtre pek bir şey elemiyor.

### Bilgi ızgarası (seçim yapılmaz)
Hiçbir hücre iki dönemde birden artı değil. En iyi görünen sabit 2R long (gel. +0.041, doğ. -0.014) ve 8b kapalı long
(gel. -0.031, doğ. +0.015): ikisi de sıfır civarı. Sadece New York saatleri (TR 16:30 - 22:00) en kötüsü (gel. -0.16R).
8c'nin (büyük zaman dilimi kuralı) olduğu ve olmadığı hal neredeyse aynı (gel. -0.073 / -0.065).

### Ne öğrendik
- Saf 5 dk yapı kırılımı (tepe-dip dizisi bozulunca gir, stop son uçta), masraftan önce bile sıfır civarı:
  masrafsız ortalama yaklaşık geliştirmede -0.03R, doğrulamada +0.03R. Masraf işlem başına ~0.04R.
- Kural rastgele girişle aynı sonucu veriyor (p 0.56 / 0.68). Avantaj, eğer varsa, Aslan'ın kodlanamayan seçiminde.
- Bunu ölçmenin tek dürüst yolu: Aslan'ın **kendi** işlemlerini ileriye dönük, giriş anında kaydetmesi (ekran görüntüsü +
  giriş/stop/hedef, kazanan ve kaybeden hepsi). 30 işlemlik böyle bir kayıt, bir backtest'in söyleyemediğini söyler.

Dosyalar: `summary.csv`, `pass.csv`, `funnel.csv`, `yearly.csv`, `trades_main.csv`, `buy_hold.csv`, `run_log.txt`.
