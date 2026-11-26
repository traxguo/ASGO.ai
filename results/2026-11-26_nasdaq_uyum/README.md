# Nasdaq uyum puanı — birçok kriter aynı yönü gösterince işlem (ön kayıt ve sonuç)

Proje sahibi (2026-11-26): "Sadece FVG değil; FVG, likidite, trend yönü, destek direnç… hepsi uyuyorsa işlem al ki
başarı oranı artsın; long ve short."

## 1. Ön kayıt (sonuç görülmeden yazıldı)

**Veri:** HistData NAS100 5 dk; geliştirme 2020-2024, doğrulama 2025-01 → 2026-03; kasa yüklenmez.

**Aday an:** 5 dk mum kapanışında taze bir olay (dünün/seansın tepe-dibinin süpürülüp geri dönülmesi, 5 dk FVG'ye
dokunup dönme, bant kırılımı; harita testindeki tanımlar). İki yön aynı anda aday olursa an atılır.

**7 kriter (long için; short tam tersi), her biri 1 puan:**
1. `trend_d`: günlük trend yukarı (dünkü kapanış 20 günlük ortalamanın üstünde).
2. `trend_4h`: fiyat son ~20 adet 4 saatlik dönemin (960 adet 5 dk) ortalamasının üstünde.
3. `htf_fvg`: altta bozulmamış 1 sa / 4 sa yükseliş FVG'si var ve fiyat onun içinde veya en fazla 0.3 günlük ATR üstünde.
4. `sweep`: son 1 saatte dünün veya son seansın dibi süpürülüp üstünde kapanılmış.
5. `swing_held`: son onaylı 1 sa dip son 1 saatte test edilmiş (0.05 ATR yakınına gelinmiş) ve fiyat üstünde.
6. `fvg_respect`: son 3 mumda 5 dk yükseliş FVG'sine dokunup üstünde kapanış.
7. `band_break`: son 1 saatte 1-4 saatlik bant yukarı kırılmış.

**Ana kural:** puan ≥ 4 → işlem. Bilgi: puan ≥ 3, ≥ 5, ≥ 6 (seçim yapılmaz).

**İşlem:** giriş aday mumun kapanışı; stop 0.30 günlük ATR, hedef 0.60 günlük ATR (2R); en fazla 24 saat; TR 09:00-22:00,
NY açılışının ilk 15 dakikası değil; aynı anda tek işlem; masraf gidiş-dönüş %0.01 + swap (`aslan_5dk` ile aynı).

**Geçme çıtası (long ve short ayrı):** net > 0 ve PF ≥ 1.2 iki dönemde, rastgele giriş kontrolü p < 0.05 (gel.),
2x masrafta artı, doğrulamada ≥ 30 işlem, %1 riskle düşüş ≤ %25.

**Sahte veri kontrolü (sonuçtan önce):** saf rastgele yürüyüşte ana kural geçmedi (long -0.03R p 0.31, short +0.04R
p 0.29; kazanma ~%36, 2R hedefle beklenen ~%33).

Kod: `research/uyum/score.py`. İş akışı: `.github/workflows/nasdaq_uyum.yml`.

---
