# Coin fikir paketi (8 yeni fikir) — günlük, long ve short

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı ve commit edildi, 2026-11-09)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı ve sonradan değiştirilmez. Sonuçlar 2. bölüme eklenir.

**Amaç:** Sistem daha sık işlem yapsın diye çok sayıda kârlı strateji (long ve short) bulmak. 8 yeni fikir aynı
disiplinle test edilir. Daha önce reddedilen fikirler (Fitil short aynası, pompa söndürme, başarısız tepki, Göreli Güç,
yeni coin short 7g, olay/silinme short, `cards/ayi_short.md` H1-H8, ≤3 saatlik scalp fikirleri, market-nötr çiftler /
ETH-BTC / artık dönüşü / funding carry, Nabız, Kinetik) tekrar edilmez.

### Ortak ayarlar (8 fikrin hepsi)

- **Veri:** Binance USDⓈ-M perpetual. Kapanış + hacim: `user_data/data/xsec_all_1d.feather` (680 sembol, silinenler dahil).
  OHLC gereken fikirde (F3): `user_data/data/binance/futures/*-1d-futures.feather`. Funding: gerçek oranlar
  (`binance/futures/*-1h-funding_rate.feather`, yoksa `binance_vision_raw/fundingRate/`). Yükleme anında
  **2026-04-01 ve sonrası kesilir; kasa hiç okunmaz.**
- **Dönemler:** geliştirme (gel.) 2020-01-01 → 2024-12-31, doğrulama (doğ.) 2025-01-01 → 2026-03-31. Bir işlem
  **giriş tarihine** göre döneme yazılır. Doğrulamada 2026-03-31'i aşacak işlem o günün kapanışında kapatılır.
- **PIT evren:** `research/xsec/top36_yearly.json` (her yıl başında en çok işlem gören 36 USDT perp, silinenler dahil).
  Coin sadece listede olduğu yıl işlem açabilir. Verisi biten coin son kapanışında çıkar.
- **Zamanlama:** karar günlük kapanışta (UTC) verilir; giriş o kapanışta (F3 hariç). İleriye bakma yok: göstergeler
  sadece o güne kadarki kapanışları kullanır.
- **Masraf:** gidiş-dönüş %0.2 (BTC/ETH için taraf başı %0.1; altcoinler gidiş-dönüş %0.2) — işlem nominali üzerinden.
  **Funding:** gerçek oranlar; pozisyonun tuttuğu her gün t için (t 00:00, t+1 00:00] arasındaki funding'ler, yöne göre
  ödenir/alınır (`research/tsmom/tsmom.py` ile aynı kural).
- **İşlem getirisi:** `boyut × (yön × (çıkış/giriş − 1) − yön × funding toplamı − %0.2)`. Boyut 1x, aksi yazmadıkça.
  Aynı coinde aynı yönde açık işlem varken yeni giriş yok.
- **Rastgele giriş kontrolü (her fikir, her yön):** her gerçek işlem için aynı coin (sepet fikirlerinde aynı sepet), aynı
  yön, aynı tutma süresi (gün), aynı dönem içinden rastgele bir giriş günü (evren kuralı aynı) seçilir; boyut kuralı aynı.
  1000 tekrar. p = (1 + rastgele ortalamanın gerçek ortalamaya eşit/üstünde olduğu tekrar sayısı) / 1001. F3'te rastgele
  giriş = rastgele bir günün açılışı.
- **Al-tut kıyası:** BTC 1x long ve PIT evren eşit ağırlık 1x long (funding dahil), her dönem.

### Geçme çıtası (her fikrin ANA ayarı, **long ve short ayrı ayrı**; hepsi gerekli)
1. İşlem başı net ortalama getiri > 0, hem gel. hem doğ.
2. Profit factor (kazanç toplamı / kayıp toplamı) ≥ 1.2, hem gel. hem doğ.
3. Rastgele giriş kontrolünü geçer: gel. p < 0.05.
4. 2x masrafta (%0.4 gidiş-dönüş) işlem başı ortalama > 0, hem gel. hem doğ.
5. Doğrulamada ≥ 30 işlem (az ise nedeni yazılır; sayı yetmiyorsa "geçti" denmez, "az örnek" diye işaretlenir).
6. **Kazanma oranı ≥ %50, hem gel. hem doğ.** (Proje sahibinin kararı, 2026-11-09; bu ön kayıt commit edilmeden ve hiçbir
   getiri hesaplanmadan önce eklendi.)

Kazanma oranı her fikir için raporlanır. Long ve short ayrı raporlanır. Karar sadece **ANA ayardan** verilir; ızgaranın
geri kalanı dayanıklılık bilgisidir (ızgarada en iyiyi seçmek yok). 8 fikir × 2 yön ≈ 14 test yapıldığı için bir
tanesinin şansla p < 0.05 çıkması beklenebilir; bu raporda yazılır. Geçen yön için kâğıt takip kurulur; geçmeyen
fikirlerin kodu ve sonucu saklanır.

### Fikirler (ANA ayar **kalın**)

**F1 — BTC/ETH Trend: long ya da nakit.** (`research/tsmom` fikrinin short bacağı nakitle değiştirildi.)
BTC ve ETH ayrı ayrı. Kapanış > SMA(N) olduğu ilk kapanışta long girilir; kapanış ≤ SMA(N) olduğu ilk kapanışta çıkılır.
Boyut girişte sabitlenir: min(%20 / 30 günlük gerçekleşmiş oynaklık (günlük log getiri std × √365), 3). Sadece long.
Izgara: N ∈ {60, **120**, 200}. Not: doğrulamada 30 işlem beklenmez (yılda birkaç yön değişimi).

**F2 — Coin zaman serisi momentumu (PIT top-36), long + short.**
Her coin için kapanışta son L günlük getiri > 0 → long, < 0 → short. Coin ≥ L+30 gün geçmişe sahip olmalı. İşaret
değiştiği kapanışta çıkılır ve (evrendeyse) ters yöne girilir. Coin yeni yılın listesinde yoksa 31 Aralık kapanışında çıkar.
Boyut girişte sabitlenir: min(%50 / 30 günlük oynaklık, 2). Izgara: L ∈ {20, **60**, 120}.

**F3 — Günlük volatilite kırılımı (BTC, ETH, SOL), long + short.**
ATR = önceki 14 günün gerçek aralık (TR) ortalaması (bugün hariç). Gün içinde yüksek ≥ açılış + k·ATR → o seviyeden long;
düşük ≤ açılış − k·ATR → o seviyeden short. Aynı gün ikisi de değerse o gün işlem yok (sıra bilinmiyor). Çıkış: H'inci
günün kapanışı (H=1: aynı günün kapanışı). Funding: girdiği günden çıkış gününe kadar her günün funding'i tam yazılır.
Izgara: k ∈ {0.3, **0.5**, 0.8} × H ∈ {**1**, 3}.

**F4 — Aşırı düşüş gününü satın al (büyük coinler), sadece long.**
Evren: o gün 30 günlük ortalama hacme göre en büyük 10 USDT perp (stabil coinler hariç: USDC, BUSD, TUSD, USDP, FDUSD,
DAI). Günlük getiri ≤ −z·σ (σ = önceki 60 günün günlük getiri std'si, bugün hariç) → kapanışta long, H gün sonra kapanışta çıkış.
Izgara: z ∈ {2.0, **2.5**, 3.0} × H ∈ {1, **3**, 5}.

**F5 — Haftanın günü etkisi (BTC), long + short.**
Long: Pazartesi tutulur (Pazar kapanışı → Pazartesi kapanışı; literatür: BTC'de pazartesi getirisi yüksek).
Short: hafta sonu tutulur (Cuma kapanışı → Pazar kapanışı). Bilgi için 7 günün hepsi iki yönde de raporlanır
(karar sadece ana kurallardan).

**F6 — 52 hafta zirvesine yakınlık (PIT top-36), sadece long.** (George & Hwang 2004.)
Her Pazar kapanışında: oran = kapanış / önceki 365 günün (bugün dahil) en yüksek kapanışı. ≥ 365 gün geçmiş gerekli.
Oran ≥ X olan evren coinleri long, H gün sonra kapanışta çıkış. Izgara: X ∈ {0.90, **0.95**} × H ∈ {7, **14**, 28}.

**F7 — BTC hakimiyet rejimi (altcoin sepeti mi BTC mi), sadece long.**
Alt sepeti = o yılın PIT listesindeki BTC dışı coinler, eşit ağırlık, günlük yeniden dengelenen endeks (günlük getiri =
o gün iki kapanışı da olan coinlerin ortalaması; funding de ortalama). Oran = alt endeksi / BTC. Oran > SMA(N) → alt
sepeti long; değilse BTC long. Rejim değişince çıkış + diğerine giriş (her rejim dönemi bir işlem; sepet işlemi tek işlem
sayılır, masraf %0.2). Izgara: N ∈ {20, **50**, 100}. Long tek yön; alt ve BTC bacakları ayrıca raporlanır.

**F8 — Günlük funding aşırılığı + dönüş (PIT top-36), long + short.** (`cards/kalabalik.md` fikrinin günlük kuralı.)
Günlük funding = o günün funding'lerinin ortalaması. Eşik: önceki 365 günün (≥ 180 gün gerekli) yüzdelikleri.
Short: funding ≥ üst %p ve > 0 VE kapanış < önceki 5 günün en düşük kapanışı. Long: funding ≤ alt %p VE kapanış >
önceki 5 günün en yüksek kapanışı. H gün sonra kapanışta çıkış. Izgara: p ∈ {**5**, 10} × H ∈ {3, **5**, 10}.

Kod: `research/coin_batch/batch.py` (ön kayıttan sonra çalıştırılır).

### Ek (2026-11-09, proje sahibinin kararı; hiçbir getiri hesaplanmadan önce yazıldı ve commit edildi)

Çıtadaki 6. madde (**kazanma oranı ≥ %50**) proje sahibi tarafından **geri alındı**; kazanma oranı sadece bilgi olarak raporlanır.
Yerine yeni 6. madde:

6. **En büyük düşüş (max drawdown), test edilen boyutta, hem gel. hem doğ. %25'ten kötü değil.**
   Ölçüm (her fikir, her yön, ayrı): tek kasa 1.0 ile başlar; her işlemin kârı = girişteki kasa × (1/K) × işlem getirisi
   (işlem getirisi yukarıdaki gibi, kendi boyutu dahil). Olaylar zamana göre sıralanır (aynı anda önce çıkışlar), kasa
   işlem kapanınca güncellenir (`scripts/paper_portfoy.py` ile aynı mantık). Düşüş, bu kapanış bazlı kasa eğrisinin
   tepeden en derin düşüşüdür; her dönem kendi kasasıyla (1.0'dan) ölçülür.
   K (kasanın kaç dilime bölündüğü, fikrin evren büyüklüğü): F1 = 2 (BTC, ETH yarım kasa), F2 = 36, F3 = 3, F4 = 10,
   F5 = 1, F6 = 36, F7 = 1, F8 = 36.

Son çıta (hepsi gerekli, ANA ayar, long ve short ayrı): net ortalama > 0 ve PF ≥ 1.2 (gel. + doğ.), rastgele kontrol
gel. p < 0.05, 2x masrafta ortalama > 0 (gel. + doğ.), doğ. ≥ 30 işlem (ya da nedeni), düşüş ≤ %25 (gel. + doğ.).

---

## 2. Sonuç (ön kayıttan sonra hesaplandı, 2026-11-09)

**Kısa cevap: 8 fikrin hiçbiri geçmedi (0/8). Kâğıt takip kurulmadı.**
Ön kayıtlı kuralla tek "geçen" F3 long (günlük volatilite kırılımı) çıktı, ama bu sonuç **ileriye bakma hatasından** geliyor
(aşağıda); hata düzeltilince F3 de düşüyor. Kötü sonuç gizlenmedi; çıta yumuşatılmadı; ızgarada en iyi ayar seçilmedi.

Çalıştırma: `/home/user/ftenv/bin/python -I research/coin_batch/batch.py` (≈10 sn). Veri 2020-01-01 → 2026-03-31; kasa
yüklenmedi. Dosyalar: `all_configs.csv` (tüm ızgara, yön, dönem), `pass_fail.csv`, `main_trades.csv` (ana ayarların
tüm işlemleri), `buy_hold.csv`.

### Ana ayarlar (karar bunlardan)
Ort = işlem başı net getiri (masraf %0.2 + funding dahil, kendi boyutunda). PF = profit factor. Kaz = kazanma oranı
(sadece bilgi). 2x = %0.4 masrafta ortalama. DD = ön kayıttaki kapanış bazlı kasa düşüşü. p = rastgele giriş kontrolü (gel.).

| Fikir (ana ayar) | Yön | Gel. ort | Gel. PF | Gel. kaz | Gel. işlem | Gel. 2x | Gel. DD | Doğ. ort | Doğ. PF | Doğ. kaz | Doğ. işlem | Doğ. 2x | Doğ. DD | p (gel.) | Sonuç |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 BTC/ETH trend long/nakit (N120) | long | +11.34% | 11.26 | %27 | 41 | +11.26% | %10 | +0.65% | 1.79 | %33 | 12 | +0.57% | %3 | 0.067 | GEÇMEDİ (p, doğ. 12 işlem) |
| F2 Coin TSMOM (L60) | long | +4.95% | 2.61 | %29 | 1523 | +4.83% | %33 | −1.56% | 0.50 | %28 | 369 | −1.68% | %15 | 0.001 | GEÇMEDİ (doğ. eksi, gel. DD) |
| F2 Coin TSMOM (L60) | short | −0.08% | 0.97 | %37 | 1540 | −0.20% | %26 | +2.38% | 1.82 | %45 | 408 | +2.27% | %16 | 0.001* | GEÇMEDİ (gel. eksi) |
| F3 Vol. kırılımı (k0.5 H1), ön kayıtlı | long | +0.71% | 1.84 | %51 | 1650 | +0.51% | %19 | +0.38% | 1.49 | %47 | 418 | +0.18% | %11 | 0.001 | ~~geçti~~ → **GEÇMEDİ (ileriye bakma)** |
| F3 Vol. kırılımı (k0.5 H1), ön kayıtlı | short | +0.25% | 1.24 | %46 | 1612 | +0.05% | %25.3 | +0.34% | 1.44 | %48 | 446 | +0.14% | %17 | 0.001 | GEÇMEDİ (DD + ileriye bakma) |
| F3 Vol. kırılımı (k0.5 H1), **düzeltilmiş** | long | +0.22% | 1.18 | %47 | 1980 | +0.02% | %66 | −0.07% | 0.94 | %43 | 496 | −0.27% | %33 | 0.120 | GEÇMEDİ |
| F3 Vol. kırılımı (k0.5 H1), **düzeltilmiş** | short | −0.59% | 0.66 | %41 | 1942 | −0.79% | %99 | −0.24% | 0.81 | %43 | 524 | −0.44% | %43 | 0.863 | GEÇMEDİ |
| F4 Aşırı düşüş günü al (z2.5 H3) | long | +0.69% | 1.19 | %51 | 139 | +0.49% | %16 | +2.85% | 2.73 | %65 | 48 | +2.65% | %4 | 0.316 | GEÇMEDİ (gel. PF 1.19, p) |
| F5 Haftanın günü (Pzt long) | long | +0.25% | 1.18 | %49 | 261 | +0.05% | %51 | +0.05% | 1.07 | %54 | 65 | −0.15% | %19 | 0.102 | GEÇMEDİ |
| F5 Haftanın günü (hafta sonu short) | short | −0.28% | 0.76 | %43 | 261 | −0.48% | %70 | −0.02% | 0.98 | %43 | 65 | −0.22% | %28 | 0.214 | GEÇMEDİ |
| F6 52 hafta zirvesi (X0.95 H14) | long | +1.28% | 1.12 | %46 | 134 | +1.08% | %14 | −4.60% | 0.36 | %32 | 19 | −4.80% | %2 | 0.595 | GEÇMEDİ |
| F7 BTC hakimiyet rejimi (N50) | long | +2.16% | 1.61 | %51 | 118 | +1.96% | %81 | −1.47% | 0.54 | %44 | 32 | −1.67% | %55 | 0.574 | GEÇMEDİ |
| F8 Günlük funding aşırılığı (p5 H5) | long | −0.70% | 0.85 | %44 | 290 | −0.90% | %9 | +2.82% | 1.60 | %44 | 86 | +2.62% | %3 | 0.925 | GEÇMEDİ |
| F8 Günlük funding aşırılığı (p5 H5) | short | +0.48% | 1.13 | %55 | 490 | +0.28% | %14 | +1.84% | 1.41 | %53 | 32 | +1.64% | %2 | 0.017 | GEÇMEDİ (gel. PF 1.13) |

\* F2 short'ta p küçük çünkü rastgele altcoin short'ları (yükselen 2020-2021'de) daha da kötü; kendi ortalaması yine eksi.

Al-tut (funding dahil): BTC 1x long gel. +%535 (CAGR %44.7, düşüş −%78.9), doğ. −%30.9 (düşüş −%50.3).
PIT top-36 eşit ağırlık 1x long gel. +%88 (düşüş −%90.6), doğ. −%73.4 (düşüş −%79.3).

### F3'teki ileriye bakma hatası (önemli)
Ön kayıtlı F3 kuralı "aynı gün iki seviye de değerse o gün işlem yok" diyordu. Bu, gün içinde **sonradan** ne olacağını
bilmeyi gerektirir: sabah long seviyesi kırılıp giriş yapıldığında, akşama doğru fiyatın düşüp short seviyesine de
ineceği bilinemez. Kural, tam da bu kaybeden günleri (önce yukarı kırıp sonra çöken günleri) sonuçtan siliyordu.
Gerçekte tek başına çalışan bir long kuralı, seviye değdiği an (stop emriyle) girer ve gün sonu kapanışında çıkar;
günün geri kalanı önemsizdir. Bu "düzeltilmiş" versiyon (`*_real` satırları) ızgaranın 12 satırının hiçbirinde iki dönemde
birden çıtayı geçmiyor; ana ayarda long doğrulamada eksi (−0.07%), short iki dönemde de eksi. Yani F3'ün görünen kârı
(+0.71%/işlem, PF 1.84) **neredeyse tamamen bu hatadan** geliyordu. Karar: F3 GEÇMEDİ. Bu düzeltme çıtayı sıkılaştırır,
gevşetmez; ön kayıtlı kural metni değiştirilmedi, iki sonuç da tabloda.

### Izgara (sadece bilgi, karar ana ayardan)
- **F1:** N60 ve N200 de gel. çok güçlü (PF 5.5 / 25), doğ. artı ama küçük (PF 1.6 / 1.4); doğ. 12-20 işlem.
  Long-ya-da-nakit kuralı düşen 2025'te kasayı korudu (doğ. düşüş %2-6, al-tut −%50), ama yılda birkaç işlemle çıta
  ölçülemiyor. `cards/btc_eth_trend.md` kâğıt takibi (long+short) bunu zaten izliyor.
- **F2:** üç bakış süresinde de aynı resim: long gel.'de çok iyi, doğ.'da eksi; short tam tersi. Rejime bağlı, kalıcı avantaj yok.
- **F4:** 9 ayarın 6'sı iki dönemde artı. **z2.0 H3** komşusu tüm şartları sağlıyor (gel. +1.32% PF 1.45 p 0.047; doğ.
  +1.69% PF 1.71, 85 işlem; DD %13/%7) ve z3.0 H1 de güçlü; ama ana ayar (z2.5 H3) gel. PF 1.19 ve p 0.32 ile düştü.
  Sonuç gördükten sonra komşuyu seçmek olmaz. H5 ayarları üç eşikte de doğ.'da eksi. Bu yüzden "aday değil, izlenecek fikir".
- **F5:** 7 günün hiçbiri, iki yönde de, iki dönemde birden PF ≥ 1.2 değil. %0.2 masraf günlük etkiyi yiyor.
- **F6:** gel. güçlü (H7, H28), doğ.'da tüm ayarlar eksi ve 15-43 işlem.
- **F7:** tüm N'lerde doğ. eksi; tam kasa tek pozisyon olduğu için düşüş %55-83.
- **F8:** short tarafı 6 ayarın hepsinde iki dönemde artı (gel. +0.26..+0.74%), ama gel. PF 1.05-1.15 (hiçbiri 1.2 değil);
  kalabalık-long'a karşı short'un küçük bir avantajı var, masrafla birlikte çıtaya yetmiyor. Long tarafı gel.'de eksi.

### Notlar
- 8 fikir × yönler = 14 ana test. Gel. p < 0.05 çıkan 5 testin 3'ü (F2 long/short, F8 short) diğer şartlarda düştü.
- F4'te 10 büyük coin içinde funding dosyası olmayan 4 coin var (CFX, LINA, PEOPLE, UNFI; 187 işlemin 5'i, hepsi gel.,
  3 günlük tutma): bunlara funding 0 yazıldı. Etkisi ihmal edilebilir. Evrende altın/gümüş perp'i (XAU/XAG) de olabilirdi
  (ön kayıtta sadece stabil coinler hariçti); ana ayarda bunlardan işlem yok.
- F7'de sepetin günlük yeniden dengeleme masrafı hesaba katılmadı (sonucu sadece iyileştirirdi; yine de geçmedi).
- Kasa (2026-04 → 2026-09) hiçbir fikirde kullanılmadı.
