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
