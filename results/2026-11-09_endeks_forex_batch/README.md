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

**Ek (2026-11-09, proje sahibinin kararı, getiriler hesaplanmadan önce):** 5. madde (kazanma oranı ≥ %50) kaldırıldı;
kazanma oranı sadece bilgi olarak raporlanır. Yerine yeni 5. madde:
5. Test edilen büyüklükte en büyük düşüş (max drawdown) **≤ %25, hem geliştirmede hem doğrulamada**.
   Test edilen büyüklük: kasa fikrin enstrümanlarına eşit bölünür (k enstrüman → her işlem kasanın 1/k'sı kadar pozisyon,
   kaldıraçsız; DAX–NAS için bir bacak = kasanın tamamı). İşlemler çıkış zamanı sırasıyla bileşik toplanır:
   kasa × (1 + net getiri / k). Düşüş, bu kasa eğrisinin zirveden en büyük yüzde düşüşüdür (yön başına, dönem başına, 1x masraf).

Her fikir için kazanma oranı, long ve short ayrı, enstrüman kırılımı ve al-tut kıyası raporlanır.
Geçen her fikir için kâğıt takip (gerçek emir yok) kurulur. Kötü sonuç gizlenmez.

Kod: `research/endeks_forex/` (veri: `fetch.py`, test: `batch.py`). İş akışı: `.github/workflows/endeks_forex_batch.yml`
(GitHub sunucusunda çalışır, sonuç CSV'lerini bu klasöre commit'ler).

---

## 2. Sonuç (ön kayıttan sonra hesaplandı, 2026-11-09)

**Kısa cevap: 8 fikrin 15 yön satırından hiçbiri geçmedi (0/15). Kâğıt takip kurulmadı, ASGO Portföy'e ekleme yok.**
En yakın olan, günlük RSI(2) long (NAS/SPX): iki dönemde artı, PF 1.9 / 1.3, 2x masrafta artı, düşüş küçük — ama
**rastgele long girişten ayırt edilemiyor** (p = 0.16). 2020-2026'da endeksler çok yükseldiği için birkaç gün tutulan
herhangi bir long da kazandırdı; kural bunun üstüne anlamlı bir şey eklemiyor. Üst üste 3 düşüş günü long da aynı durumda (p = 0.10).

Ön kayıt commit'leri: 01af554 (kurallar), 289113a (çıta eki: düşüş ≤ %25). Kod `research/endeks_forex/batch.py`,
çalıştırma GitHub iş akışı `endeks_forex_batch.yml` (çalışma 42579437334). Ham çıktı: `run_log.txt`.

### Ana ayarlar (masraf + swap dahil, işlem başı net %, fikrin enstrümanları birlikte)
"p" = geliştirmede rastgele giriş kontrolü (aynı yön, aynı tutma süresi). "Düşüş" = test edilen büyüklükte en büyük düşüş.

| Fikir | Yön | Gel. işlem | Gel. ort. | Gel. PF | Gel. kazanma | Doğ. işlem | Doğ. ort. | Doğ. PF | Doğ. kazanma | 2x masraf gel./doğ. | p (gel.) | Düşüş gel./doğ. | Sonuç | Düşüren şart |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| I1 Gece kayması | long (gece) | 2317 | −0.005% | 0.98 | 51.5% | 610 | −0.005% | 0.98 | 51.8% | −0.035 / −0.035 | 0.89 | 29.5 / 16.7% | GEÇMEDİ | net, PF, kontrol, 2x, düşüş |
| I1 Gece kayması | short (gün içi) | 2354 | −0.048% | 0.89 | 44.7% | 616 | −0.026% | 0.93 | 47.7% | −0.058 / −0.036 | 0.92 | 48.6 / 21.1% | GEÇMEDİ | net, PF, kontrol, 2x, düşüş |
| I2 Ay dönümü | long | 129 | +0.170% | 1.18 | 51.9% | 42 | −0.031% | 0.96 | 47.6% | +0.075 / −0.126 | 0.49 | 9.0 / 3.3% | GEÇMEDİ | PF, doğ. eksi, kontrol |
| I3 RSI(2) | long | 71 | +0.448% | 1.94 | 66.2% | 34 | +0.229% | 1.35 | 73.5% | +0.368 / +0.143 | 0.16 | 4.5 / 5.1% | GEÇMEDİ | kontrol (p ≥ 0.05) |
| I3 RSI(2) | short | 23 | +0.563% | 1.98 | 65.2% | 4 | +0.215% | 1.37 | 75.0% | +0.512 / +0.175 | 0.069 | 2.6 / 0.8% | GEÇMEDİ | kontrol, doğ. 4 işlem |
| I4 Boşluk doldurma | long | 669 | +0.018% | 1.05 | 63.7% | 170 | +0.071% | 1.21 | 64.1% | +0.008 / +0.061 | 0.47 | 9.2 / 4.9% | GEÇMEDİ | gel. PF, kontrol |
| I4 Boşluk doldurma | short | 831 | −0.040% | 0.89 | 56.2% | 210 | +0.053% | 1.23 | 61.0% | −0.050 / +0.043 | 0.59 | 19.7 / 2.8% | GEÇMEDİ | gel. eksi, kontrol |
| I5 3 gün | long | 147 | +0.254% | 1.44 | 66.7% | 51 | +0.849% | 6.41 | 80.4% | +0.209 / +0.809 | 0.10 | 11.3 / 1.0% | GEÇMEDİ | kontrol (p ≥ 0.05) |
| I5 3 gün | short | 215 | −0.044% | 0.92 | 54.9% | 67 | +0.017% | 1.04 | 59.7% | −0.075 / −0.014 | 0.21 | 14.8 / 2.5% | GEÇMEDİ | gel. eksi, PF, kontrol |
| I6 Altın–DXY | long | 8 | +0.468% | 2.85 | 62.5% | 3 | +0.592% | 1.27 | 66.7% | +0.376 / +0.500 | 0.34 | 1.6 / 6.5% | GEÇMEDİ | kontrol, çok az işlem |
| I6 Altın–DXY | short | 16 | −0.634% | 0.56 | 31.3% | 9 | −0.065% | 0.97 | 33.3% | −0.688 / −0.119 | 0.72 | 14.5 / 19.6% | GEÇMEDİ | eksi, az işlem |
| I7 DAX–NAS farkı | long | 12 | −0.416% | 0.80 | 58.3% | 8 | −0.366% | 0.72 | 37.5% | −0.656 / −0.635 | 0.39 | 14.2 / 8.9% | GEÇMEDİ | eksi, az işlem |
| I7 DAX–NAS farkı | short | 4 | +0.014% | 1.03 | 50.0% | 5 | −1.808% | 0.31 | 40.0% | −0.310 / −2.087 | 0.57 | 1.1 / 12.7% | GEÇMEDİ | eksi, az işlem |
| I8 Londra kırılımı | long | 1006 | −0.012% | 0.90 | 43.7% | 240 | +0.002% | 1.02 | 46.7% | −0.022 / −0.008 | 0.35 | 10.6 / 2.6% | GEÇMEDİ | net, PF, kontrol, 2x |
| I8 Londra kırılımı | short | 1063 | −0.008% | 0.94 | 41.8% | 225 | −0.025% | 0.80 | 40.4% | −0.018 / −0.035 | 0.69 | 10.3 / 4.7% | GEÇMEDİ | net, PF, kontrol, 2x |

Doğrulamada 30'dan az işlem: I3 short (4; 2025-26'da endeksler SMA200'ün altında çok az kaldı), I6 (3 ve 9; |z| > 2
seyrek ve 5 gün tutuluyor), I7 (8 ve 5; DAX verisi eksik, aşağıya bakın). Bu satırlar zaten başka şartlardan da düşüyor.

### Enstrüman kırılımı (ana ayar, net ort. % gel. / doğ.)
- I3 RSI(2) long: NAS +0.50 / +0.57 (31 / 12 işlem), SPX +0.52 / +0.69 (33 / 10), DAX −0.10 / −0.50 (7 / 12).
- I5 3 gün long: NAS +0.50 / +1.33, SPX +0.28 / +0.98, DAX −0.68 / +0.41. Doğrulamadaki toplam +43 puanın ~14'ü Nisan 2025, ~13'ü Mart 2026 düşüş-dönüşlerinden (3 + 8 işlem).
- I4 boşluk doldurma long: NAS +0.002 / +0.05, SPX +0.04 / +0.09 — masraftan sonra sıfıra yakın.
- I1 gece long: NAS −0.000 / +0.005, SPX −0.009 / −0.016. Masrafsız gece getirisi küçük artı; günlük masraf + gecelik swap (%5/yıl) bunu siliyor.
- Tam tablo `summary.csv` (her ayar × yön × dönem × masraf × enstrüman), yıllar `yearly_primary.csv`, işlemler `trades_primary.csv`.

### Izgara (sadece bilgi; geçme kararı ana ayarla, ızgaradan seçim yapılmadı)
- I3 long'un tüm 6 komşusu geliştirmede artı (PF 1.9–4.2); 25/75 eşiği daha çok işlem verir (gel. 154, doğ. 74, ort. +0.40% / +0.24%).
  Bu ayarlar için rastgele kontrol çalıştırılmadı; ana ayarın kontrolü (p = 0.16) aynı nedenle muhtemelen onlarda da zayıf olur.
- I4 boşluk doldurma "sadece kapanışta çık" doğrulamada daha iyi (long +0.21%, short +0.17%) ama geliştirmede short eksi, long PF 1.10.
- I8 hedefli (1R/2R) sürümler de iki yönde eksi. I1 SMA200 filtresi sıfır civarı.

### Al-tut kıyası (dönem başı → sonu)
| | NAS100 | SPX500 | DAX | EURUSD | GBPUSD | Altın |
|---|---|---|---|---|---|---|
| Geliştirme 2020-24 | +140% | +82% | (veri eksik) | −8% | −6% | +73% |
| Doğrulama 2025-26/03 | +13% | +11% | +16% | +12% | +6% | +78% |

Long kurallarının hepsi al-tuttan çok daha az kazandırıyor (örneğin I3 long geliştirmede 71 işlem × +0.45% ≈ +32%, kasa
üçe bölünmüş olarak ≈ +%11; NAS al-tut +%140). Short kuralları yükselen piyasada genelde eksi.

### Veri sorunları ve düzeltmeler (şeffaflık için)
1. **İlk çalıştırma (veri hatası, CSV `run1_pass_data_error.csv`):** DAX gün listesi katı saat eşleşmesi yüzünden aylarca eksikti,
   işlemler aylarca açık kaldı; bir de +%278'lik sahte işlem vardı. Kurallar değiştirilmeden veri okuma düzeltildi:
   gün = açılış ve kapanışta taze (≤ 30 dk) fiyat; komşu 25 mumun medyanından %5'ten fazla sapan tekil mumlar atıldı;
   hiçbir günlük işlem 5 günden uzun veri boşluğunu aşamaz (rastgele kontrolde de).
2. **HistData "grxeur" (DAX) 2020-06-15 → 2023-12-01 arası DAX değil:** fiyat 3000–4400 (Euro Stoxx 50 seviyesi), 2023-12-01'de
   4424'ten 16429'a atlıyor (`diag/daily_GER40.csv`). Bu dönem eksik veri sayıldı. DAX geliştirmede sadece 2020-01 → 06 ve
   2023-12 → 2024-12 var; I2/I3/I5'in DAX kısmı ve I7 (DAX–NAS) bu yüzden az işlemli. **Not:** önceki
   `results/2026-11-05_aslan_endeksler` GER40 testi de aynı bozuk veriyi kullanmış olmalı; o sonuç güvenilir değil.
3. Açılış fiyatı = nakit açılış saatinde başlayan ilk 5 dk mumun açılışı (README'deki "açılış (09:30)" tanımı; ilk kod sürümü bir önceki mumun kapanışını alıyordu, yaz aylarında DAX açılışını bulamıyordu).
4. NAS/SPX 2023-03 → 07 arası HistData'da günde ~16 saat veri var; 2023'te ~60 gün düştü (`data_check.csv`).
5. Bilinen küçük kusur: saat-bazlı rastgele kontrolde (I1, I4, I8) çıkış anında fiyat yoksa (hafta sonu vb.) rastgele işlem 0 sayıldı;
   bu rastgele ortalamayı sıfıra çeker. Bu üç fikir zaten geliştirmede net/PF şartından düştüğü için karar değişmez.

### Öğrenilenler
- 2020-2026 boğa piyasasında "birkaç gün long tut" kuralları rastgele long girişle aynı kazancı veriyor; geri dönüş (RSI2, 3 gün) fikirleri
  burada ölçülebilir bir avantaj göstermedi (p 0.10–0.16). Short tarafı hiçbir fikirde iki dönemde birden tutmadı.
- Gece kayması (overnight drift) masrafsız bile çok küçük; gecelik swap ve masraf bunu tamamen siliyor.
- Londra kırılımı forex'te sıfır avantaj (forex_tarama'daki açılış aralığı kırılımı sonucu ile aynı).
