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

## 2. Sonuç (2026-11-21, GitHub runner)

**GUO'ya not:** Net bir sonuç çıktı: ölçtüğümüz 8 durumun (bant kırılımı, dünün/seansın tepe-dibinin alınması, FVG,
iFVG) hiçbiri, hiçbir seans/trend/oynaklık koşulunda, sonrasında fiyatı tek yöne götürmüyor. Gerçek Nasdaq 5 dk bu
açıdan rastgele yürüyüşten ayırt edilemiyor. Bu yüzden kurala geçilecek aday yok.

- 400 hücre ölçüldü; geliştirmede eleme geçen **0**, doğrulamaya giden 0.
- t değerlerinin dağılımı tam şans dağılımı: standart sapma 0.93 (rastgele verideki 1.06'ya benzer), |t| > 2 olan 13
  hücre (şansla ~20 beklenir), en büyük |t| 3.04 ve o hücrede sadece 33 gün var.
- Olay sayıları (2020-2026 Mart): bant 1-4 sa 14794, bant 4-8 sa 6457, dünün tepe/dip süpürmesi 664, kırılımı 1723,
  seans süpürmesi 1838, kırılımı 3915, FVG dokunuşu 37875, iFVG 54445.
- Ayrıntı: `cells.csv` (her hücre), `run_log.txt` (en büyük 25 |t|).

**Yorum:** Bu, önceki 25'ten fazla 5 dk kural testinin neden hep sıfır civarında çıktığını açıklıyor: Nasdaq'ın 5 dk
fiyat kalıplarında, masrafı karşılayacak bir yön bilgisi yok. Kodlanmış Aslan kurallarının tutmaması kuralların yanlış
yazılmasından değil, bu bilginin fiyat grafiğinde bulunmamasından.

**Karar:** 5 dk fiyat kalıplarıyla yeni kural aranmaz. Sonraki adım için öneri: fiyat dışı bilgi (oynaklık endeksi VIX
ve vade yapısı, Fed/enflasyon günleri, ay sonu, haftanın günü) ve çok daha uzun geçmiş (günlük veri, 20+ yıl) ile aynı
"önce ölç" yöntemi.
