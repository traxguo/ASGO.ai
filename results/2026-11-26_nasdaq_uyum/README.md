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

## 2. Sonuç (2026-11-26, GitHub runner)

**GUO'ya not:** Uyum puanı **geçmedi**. Kriter sayısını artırmak başarı oranını artırmadı: 4 kriter uyunca da, 6 kriter
uyunca da işlemlerin kabaca %30-40'ı kazandı (2R hedefle başa baş için %33-34 gerekir). Sonuç rastgele girişle aynı.

| Birim (ana: puan ≥ 4) | Gel. işlem | Gel. R/işlem | Gel. PF | Gel. kazanan % | Doğ. işlem | Doğ. R/işlem | Kontrol p | Sonuç |
|---|---|---|---|---|---|---|---|---|
| Long | 1266 | +0.029 | 1.05 | 39.3 | 282 | -0.055 | 0.52 | geçmedi |
| Short | 897 | -0.065 | 0.90 | 32.6 | 255 | -0.014 | 0.52 | geçmedi |

- Rastgele girişin ortalaması long +0.031R, short -0.063R: kural rastgeleyle **aynı** (p 0.52). Long'daki küçük artı
  Nasdaq'ın genel yükselişinden geliyor, kriterlerden değil.
- Puan eşiği (bilgi): ≥ 3 long +0.011 / -0.094R, ≥ 5 long +0.026 / -0.115R, ≥ 6 long +0.066 / -0.378R (gel. / doğ.).
  Puan arttıkça doğrulama kötüleşiyor; "daha çok uyum = daha iyi" görülmüyor.
- Yıllar (`yearly.csv`): long 2020-2022 artı, 2023-2026 eksi; short çoğu yıl eksi.
- Kriterlerin ne sıklıkla uyduğu: `criteria_share.csv`.

**Karar:** reddedildi; kâğıt takip yok. Elle yazılmış uyum kuralı, öğrenen modelle (2026-11-26) aynı sonucu verdi.
