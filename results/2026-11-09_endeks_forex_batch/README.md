# Endeks + forex: 8 yeni fikir (toplu test) — long ve short

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı, 2026-11-09)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı ve commit'lendi; sonradan değiştirilmez.
Sonuçlar aşağıda ayrı bir bölüm olarak eklenir.

**Amaç:** GUO daha sık işlem yapan, long ve short tarafta kâr eden çok sayıda strateji istiyor. Bu toplu test,
literatürde yıllardır bilinen 8 basit endeks/forex kuralını aynı disiplinle sınar. Daha önce reddedilen işler
tekrar edilmez: forex_tarama (limit fitil, açılış aralığı kırılımı, 5 dk RSI2), forex_trend (Donchian, EMA kesişimi,
4s geri çekilme), Aslan likidite kurallarının başka endekslerde denenmesi.

**Veri:** HistData.com 1 dakikalık mumlar (ücretsiz, sadece alış fiyatı), GitHub sunucusunda indirilir, 5 dakikalık
mumlara çevrilir (repoya girmez). Saatler EST (yaz saati yok, UTC−5) → UTC. Semboller: NAS100 (nsxusd), SPX500 (spxusd),
GER40 = DAX (grxeur), EURUSD, GBPUSD, XAUUSD (altın), dolar endeksi için USDJPY, USDCAD, USDSEK, USDCHF.
İndirme 2026-03 ile biter: **kasa (2026-04 → 2026-09) indirilmez, yüklenmez.**

**Dönemler:** geliştirme 2020-01-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31. Bir işlem giriş tarihine göre
döneme yazılır. 200 günlük ortalama gibi uzun göstergeler 2020'nin ilk aylarında ısınır; o günlerde sinyal yok.

**Seans saatleri (yerel saat, yaz saati dahil):** NAS/SPX nakit seans New York 09:30–16:00; DAX Frankfurt 09:00–17:30;
Londra saati Europe/London. "Kapanış fiyatı" = seans kapanışındaki son 5 dk mumun kapanışı. Kapanışa göre sinyal veren
kurallar **kapanıştan 10 dakika sonra** girer/çıkar (NAS/SPX 16:10 NY, DAX 17:40 Frankfurt; CFD/vadeli bu saatte işlem görür),
böylece sinyal ile giriş aynı fiyattan yapılmaz (ileriye bakma yok). Gün listesi: hafta içi, açılış ve kapanış mumu olan günler
(yarım gün tatiller otomatik düşer).

**Masraf (gidiş-dönüş, getiriden düşülür):** NAS/SPX/DAX %0.010, EURUSD/GBPUSD %0.010, altın %0.015.
İki bacaklı işlemde (DAX–NAS) iki bacağın masrafı. **Gecelik finansman (swap), tahmini, yıllık %, kötümser:**
endeks long 5 / short 2.5, altın long 4 / short 2, forex 1.5 / 1.5; New York 17:00'yi geçen her takvim gecesi için
(hafta sonu 3 gece). Her şey bir de **2 kat masraf + 2 kat swap** ile çalıştırılır.
Sonuçlar işlem başı **% getiri** (pozisyon büyüklüğüne göre; çoğu kuralda stop yok, bu yüzden R yerine %).

### Fikirler (her biri için ANA ayar kalın; ızgara sadece dayanıklılık için raporlanır)

Ana ayar, literatürdeki standart haline en yakın olandır ve geçme kararı **sadece ana ayarla** verilir.
Izgaradaki başka bir ayar geçse bile bu "geçti" sayılmaz (ayar seçme yanlılığı), sadece not edilir.

1. **I1 Gece kayması (overnight drift)**, NAS + SPX.
   - Long: nakit kapanışta (16:00) al, ertesi işlem günü açılışta (09:30) sat. Her gün.
   - Short: açılışta (09:30) sat, aynı gün kapanışta (16:00) kapat (gün içi short). Her gün.
   - Izgara: **filtresiz** / 200 günlük ortalama filtresi (long sadece kapanış > SMA200 iken, short sadece < SMA200 iken).
2. **I2 Ay dönümü (turn of month)**, NAS + SPX + DAX, sadece long.
   - Ayın sondan ikinci işlem gününün kapanışında (+10 dk) al, yeni ayın 3. işlem gününün kapanışında (+10 dk) sat.
   - Izgara: giriş {**sondan 2.**, son işlem günü} × çıkış {1., **3.** işlem günü}.
3. **I3 Günlük RSI(2) geri dönüş (Connors)**, NAS + SPX + DAX.
   - Long: kapanış > SMA200 ve RSI(2) < **10** → al. Short: kapanış < SMA200 ve RSI(2) > **90** → sat.
   - Çıkış: kapanış SMA5'in üstüne çıkınca (short: altına inince) veya en geç 10 işlem günü.
   - Izgara: eşik {5/95, **10/90**, 25/75} × çıkış {**SMA5**, RSI(2) 70/30'u geçince}. RSI Wilder yumuşatmalı.
4. **I4 Açılış boşluğu doldurma (gap fade)**, NAS + SPX.
   - Boşluk = açılış (09:30) / önceki kapanış (16:00) − 1. Boşluk > **+%0.25** → açılışta sat; < −%0.25 → açılışta al.
   - Çıkış: fiyat önceki kapanışa dönerse orada (boşluk doldu), yoksa 16:00 kapanışta. Stop yok. Günde en fazla 1 işlem.
   - Izgara: eşik {%0.15, **%0.25**, %0.50} × çıkış {**boşluk dolunca veya kapanış**, sadece kapanış}.
5. **I5 Üst üste 3 gün**, NAS + SPX + DAX.
   - Üst üste 3 düşüş kapanışı → al (kapanış +10 dk). Üst üste 3 yükseliş kapanışı → sat.
   - Çıkış: ilk lehte kapanışta (long için yükseliş kapanışı) veya en geç 5 işlem günü.
   - Izgara: çıkış {**ilk lehte kapanış (en çok 5 gün)**, 1 gün sabit, 5 gün sabit}.
6. **I6 Altın – dolar endeksi göreli geri dönüş**, işlem sadece altında (XAUUSD).
   - Günlük anlık fiyat New York 16:00. Dolar endeksi (DXY) ICE formülüyle 6 kurdan hesaplanır:
     50.14348112 × EURUSD^−0.576 × USDJPY^0.136 × GBPUSD^−0.119 × USDCAD^0.091 × USDSEK^0.042 × USDCHF^0.036.
   - β = son 60 günde altın günlük log getirisinin DXY günlük log getirisine regresyon eğimi (sadece geçmiş veri).
   - Göreli 5 günlük hareket e = (altın 5 g. log getirisi) − β × (DXY 5 g. log getirisi);
     z = e / (son 60 günün günlük artık std'si × √5).
   - z < **−2** → altın al (dolara göre fazla düştü); z > +2 → altın sat. Giriş anlık fiyattan 10 dk sonra.
     Çıkış: **5** işlem günü sonra. Aynı anda tek işlem.
   - Izgara: eşik {1.5, **2**, 2.5} × tutma {3, **5**, 10} gün.
7. **I7 DAX – Nasdaq fark geri dönüşü**, iki bacak.
   - Günlük anlık fiyat New York 11:00 (iki nakit seans da açık), giriş/çıkış 10 dk sonra.
     s = log(DAX) − log(NAS); z = (s − 20 g. ortalama) / 20 g. std.
   - z < **−2** → "long": DAX al + NAS sat (eşit büyüklük). z > +2 → "short": DAX sat + NAS al.
   - Getiri = DAX bacağı − NAS bacağı (bir bacak büyüklüğüne göre %). Çıkış: z sıfırı geçince veya en geç 10 işlem günü.
   - Izgara: eşik {1.5, **2**, 2.5} × bakış {**20**, 60} gün.
8. **I8 Londra kırılımı (Asya aralığı)**, EURUSD + GBPUSD, 1 saatlik.
   - Asya aralığı: Londra 00:00–07:00 arası en yüksek/en düşük.
   - 07:00–11:00 arasında bir 1 saatlik kapanış aralığın üstünde → long, altında → short (kapanış fiyatından giriş).
   - Stop: aralığın öbür ucu (5 dk mumlarla kontrol; boşlukla geçerse mum açılışından). Çıkış: **Londra 16:00** veya stop.
     Aynı 5 dk mumda hem stop hem hedef varsa önce stop sayılır. Günde ve parite başına en fazla 1 işlem.
   - Izgara: hedef {**yok (16:00)**, 1R, 2R}.

**Seçilmeyenler ve neden:** (6) forex carry: elde faiz oranı geçmişi yok, tahmini faiz tablosu uydurmak sonucu kurgu yapar.
(10) tatil öncesi / FOMC günü: yılda ~17 gün, doğrulamada ≥30 işlem şartını karşılamaz.

### Rastgele giriş kontrolü (her fikir, her yön, ana ayar)
Gerçek işlemlerin her biri için aynı enstrüman, aynı yön ve **aynı tutma süresi** ile rastgele bir giriş seçilir;
masraf ve swap aynı hesaplanır. Rastgele giriş havuzu:
- Kapanışa dayalı günlük kurallar (I2, I3, I5, I6, I7): aynı dönemdeki tüm günlük giriş anları; tutma = aynı işlem günü sayısı.
- I1: aynı dönemdeki işlem günlerinin herhangi bir 5 dk anı; tutma = gerçek işlemin takvim süresi (gece mi gündüz mü sorusu).
- I4: aynı dönemdeki tüm 09:30 açılışlar; I8: aynı dönemdeki tüm 08:00–11:00 Londra saat kapanışları; tutma = aynı dakika süresi.
2000 rastgele işlem seti; p = (1 + rastgele ortalamanın gerçek ortalamaya eşit/üstünde olduğu set sayısı) / 2001.

### Geçme şartı (yön başına, ana ayar, fikrin enstrümanları birlikte)
1. Net ortalama getiri > 0 ve kâr faktörü (PF) ≥ 1.2, **hem geliştirmede hem doğrulamada**.
2. Geliştirmede rastgele kontrolden iyi: p < 0.05.
3. 2 kat masraf + swap ile net ortalama > 0, hem geliştirmede hem doğrulamada.
4. Doğrulamada ≥ 30 işlem (değilse nedeni yazılır ve geçmez sayılır).
5. Kazanma oranı (net getirisi > 0 olan işlemlerin payı) ≥ %50, **hem geliştirmede hem doğrulamada**
   (2026-11-09, proje sahibinin kararı; ön kayıt commit'lenmeden ve getiri hesaplanmadan önce eklendi).

Her fikir için kazanma oranı, long ve short ayrı, enstrüman kırılımı ve al-tut kıyası raporlanır.
Geçen her fikir için kâğıt takip (gerçek emir yok) kurulur. Kötü sonuç gizlenmez.

Kod: `research/endeks_forex/` (veri: `fetch.py`, test: `batch.py`). İş akışı: `.github/workflows/endeks_forex_batch.yml`
(GitHub sunucusunda çalışır, sonuç CSV'lerini bu klasöre commit'ler).
