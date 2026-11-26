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

## 2. Sonuç (2026-11-26, GitHub runner)

**GUO'ya not:** 288 FVG çeşidinin hiçbiri şans çıtasını geçmedi. En umut verici olan **1 saatlik FVG**: fiyat 1 saatlik
FVG'nin ortasına kadar gelip geri dönünce, sonraki 1 saatte hafif bir şekilde FVG yönünde gidiyor. Ama bu etki
şansla açıklanabilecek kadar küçük.

- Geliştirmede geçen: **0** / 288. t dağılımı şans dağılımına yakın (standart sapma 1.03; |t| > 2 olan 13 hücre, şansla
  ~13 beklenir).
- En güçlü hücreler 1 saatlik FVG'lerde ve **tutarlı**: "ortaya değip dönme" artı (t 3.2, 2.8, 2.6), aynı FVG'lerin
  ters kırılması (iFVG) eksi (t -2.5, -2.5, -2.3). Yani 1 sa FVG'ler hafifçe "saygı görüyor". Ama en büyük t 3.2, çıta 3.7.
- Ayrıntı: `cells.csv`, `run_log.txt`.

**Ek (sonuçtan sonra açıkça eklendi, ön kayıtta yoktu):** en güçlü geliştirme hücresi (1 sa FVG, tüm büyüklükler, ortaya
değip dönme, 24 saate kadar yaş, trend filtresi yok, 1 saat ufuk) hiç bakılmamış doğrulama döneminde **tek bir kez**
sınanır (`research/harita/fvg_val.py`): t ≥ 2.0 ve 2x masraf sonrası ortalama > 0 gerekir. Geçse bile sadece "aday"
sayılır; işlem kuralı yazılıp ayrı test ve kâğıt takipten geçmesi gerekir. Başka hücre bu şekilde sınanmaz.
