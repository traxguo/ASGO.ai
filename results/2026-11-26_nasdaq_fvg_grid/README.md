# Nasdaq FVG ızgarası — tüm FVG çeşitleri bir arada (ön kayıt ve sonuç)

Proje sahibi (2026-11-26): "Teste devam, kriterleri değiştir, genişlet, farklı yöntemden FVG'leri ara." Kriteri her
seferinde değiştirip tutana kadar denemek şansla bir şey buldurur. Bu yüzden bütün çeşitler **bir kerede** denenir ve
çıta deneme sayısına göre yükseltilir.

## 1. Ön kayıt (sonuç görülmeden yazıldı)

**Veri:** HistData NAS100 5 dk; geliştirme 2020-2024, doğrulama 2025-01 → 2026-03; kasa yüklenmez.

**Çeşitler (4 × 3 × 3 × 2 × 2 × 2 = 288 hücre):**
- Zaman dilimi: 5 dk, 15 dk, 1 saat, 4 saat (FVG o zaman diliminin mumlarından; mum kapanınca bilinir).
- Büyüklük: hepsi / en az 0.10 günlük ATR / en az 0.25 günlük ATR.
- Giriş (5 dk mum kapanışında, FVG'ye ilk dokunuş): `respect` = FVG'nin yakın kenarına değip dışında kapanış
  (FVG yönünde); `mid` = FVG'nin ortasına değip ortanın dışında kapanış (FVG yönünde); `inverse` = FVG'nin öbür
  tarafında kapanış (iFVG, ters yönde).
- Yaş: en fazla 6 veya 24 mum (o zaman diliminin mumu).
- Trend: filtre yok / sadece günlük trend yönünde.
- Ufuk: 1 saat / 4 saat.

**Ölçü ve çıta:** harita testiyle aynı (`results/2026-11-21_nasdaq_harita/README.md`): günlük ATR cinsinden hareket,
yarım saatlik dilim ortalaması düşülür, her gün ilk olay. Geliştirme: en az 200 gün, |t| ≥ 3.7, 5 yılın en az 4'ünde aynı
işaret, |ortalama| ≥ 0.02 ATR. Doğrulama (sadece geçenler): t ≥ 2.0, en az 30 gün, 2x masraf sonrası ham ortalama > 0.

**Sahte veri kontrolü (sonuçtan önce):** saf rastgele yürüyüşte 288 hücrede 0 geçen (t'lerin standart sapması 1.07).

**Sonra:** geçen olursa stoplu/hedefli işlem kuralına çevrilip ayrı ön kayıtla geçme çıtasına sokulur. Geçmezse FVG
ailesi (tüm zaman dilimleri) kapanır; aynı ızgara kriter değiştirilerek tekrar çalıştırılmaz.

Kod: `research/harita/fvg_grid.py`. İş akışı: `.github/workflows/nasdaq_fvg_grid.yml`.

---
