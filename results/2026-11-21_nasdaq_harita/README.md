# Nasdaq 5 dk "harita" — hangi durumdan sonra fiyat tek yöne gidiyor? (ön kayıt ve sonuç)

Proje sahibinin yönlendirmesi (2026-11-21): Aslan'ı birebir kopyalamak yerine, onun fikirlerini not olarak kullanıp en iyi
senaryoyu aramak. Tahmin edip kural test etmek yerine önce **ölçüyoruz**; kural ancak ölçümden sonra yazılır.

## 1. Ön kayıt (sonuç görülmeden yazıldı)

**Veri:** HistData NAS100 5 dk, geliştirme 2020-01 → 2024-12, doğrulama 2025-01 → 2026-03. Kasa (2026-04 → 09) yüklenmez.

**Olaylar** (k mumunun kapanışında, sadece k ve öncesi kullanılır; yön = beklenen hareket):
1. `band_1_4h`: 12-48 mumluk bant (genişlik %0.17-%0.62, iki uca ≥2 dokunuş) kapanışla kırıldı → kırılım yönü.
2. `band_4_8h`: aynısı 49-96 mumluk bant.
3. `pd_fade`: gün içinde ilk kez dünün tepesi aşıldı ama mum altında kapattı → short (dip için tersi).
4. `pd_break`: gün içinde ilk kez dünün tepesinin üstünde kapanış → long (dip için tersi).
5. `sess_fade` / 6. `sess_break`: aynısı, son biten Asya veya Londra seansının tepe/dibi için.
7. `fvg_respect`: son 24 mumda oluşmuş 5 dk FVG'ye ilk dokunuşta mum FVG'nin dışında kapattı → FVG yönü.
8. `ifvg`: son 24 mumda oluşmuş 5 dk FVG'nin ters tarafında kapanış → kapanış yönü.

**Koşullar:** seans (NY saatiyle Asya 18-03, Londra 03-09:30, NY sabah 09:30-12, NY öğleden sonra 12-17); günlük trend
(dünkü kapanış 20 günlük ortalamanın üstü/altı; olay yönüyle "aynı" / "ters"); oynaklık (14 günlük ATR, son 100 günün
medyanının üstü/altı).

**Hücreler:** her olay × {hepsi, 4 seans, 2 trend, 2 oynaklık, 16 seans×trend×oynaklık} × 2 ufuk (1 saat, 4 saat)
= 400 hücre.

**Ölçü:** k kapanışından H mum sonraki fiyat farkı, günlük ATR cinsinden, olay yönüyle çarpılmış; aynı yarım saatlik
dilimin geliştirme dönemi ortalaması çıkarılır (saat etkisi ve genel yükseliş eğilimi ayıklanır). **Her gün için o
hücredeki ilk olay** alınır (bir günde birden çok olayın ortalaması geleceğe bakan bir ağırlık yaratır; rastgele yürüyüş
verisinde görüldü ve düzeltildi).

**Geliştirmede eleme (hepsi):** en az 200 gün; |t| ≥ 3.7 (400 test için Bonferroni ~%5); 5 yılın en az 4'ünde aynı
işaret; |ortalama| ≥ 0.02 ATR (masrafın birkaç katı). Ortalama eksi çıkarsa ters yön aday olur.

**Doğrulama** (sadece elemeden geçenler için hesaplanır): aynı yönde t ≥ 2.0, en az 30 gün, ve 2x masraf düşülünce
ham getiri ortalaması > 0.

**Sahte veri kontrolü (kod yazılırken):** aynı kod saf rastgele yürüyüş verisinde 400 hücrede 0 eleme geçen verdi
(t'lerin standart sapması 1.06).

**Sonra:** doğrulamayı geçen hücre varsa, o hücre stoplu/hedefli bir işlem kuralına çevrilir ve ayrı ön kayıtla, bugünkü
geçme çıtasıyla (PF ≥ 1.2 iki dönemde, rastgele kontrol, 2x masraf, düşüş ≤ %25) test edilir. Hiçbiri geçmezse sonuç:
"bu tip 5 dk fiyat durumları Nasdaq'ta rastgeleden ayırt edilemiyor" ve öneri daha yavaş zaman dilimine geçmek.

Kod: `research/harita/scan.py`. İş akışı: `.github/workflows/nasdaq_harita.yml`.

---
