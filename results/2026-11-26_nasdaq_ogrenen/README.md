# Nasdaq öğrenen model testi — ön kayıt ve sonuç

Proje sahibinin önerisi (2026-11-26): "Reinforcement learning / yapay sinir ağı gibi sürekli denesin, önemli FVG'yi,
desteği, direnci kendisi öğrensin, bütün stratejileri birlikte kullansın." Piyasada tek bir geçmiş olduğu için, aynı
yılları tekrar tekrar oynayan bir model tesadüfleri ezberler. Bu yüzden dürüst hali kuruldu: model **sınandığı yılı hiç
görmez**.

## 1. Ön kayıt (sonuç görülmeden yazıldı)

**Veri:** HistData NAS100 5 dk; geliştirme 2020-2024, doğrulama 2025-01 → 2026-03; kasa yüklenmez.

**Örnek:** TR 09:00-22:00 arası her 15 dakikada bir an. **Hedef:** sonraki 1 saatte fiyat yukarı mı (evet/hayır).

**Girdiler (hepsi o ana kadar bilinen):** son 5 dk - 8 saat hareketleri (günlük ATR cinsinden); son 2 ve 4 saatlik
aralıktaki konum ve genişlik; gün tepesi/dibi, dünün tepesi/dibi, son Asya/Londra seansı tepe/dibine uzaklık; kısa/uzun
oynaklık oranı; günlük trend, oynaklık rejimi, seans, saat dilimi, haftanın günü; son 3 ve 12 mumda olay olup olmadığı ve
yönü (bant kırılımı, dünün ve seansın tepe/dip süpürmesi ve kırılımı, FVG dokunuşu, iFVG); **FVG/seviye kimliği:** en yakın
bozulmamış 1 sa/4 sa destek ve direnç FVG'sinin uzaklığı, büyüklüğü, yaşı ve sayısı; yukarıda/aşağıda alınmamış likidite
sayısı ve en yakınının uzaklığı; son 5 dk FVG'lerin büyüklüğü ve yaşı.

**Model (sabit, ayar aranmaz):** gradyan artırmalı karar ağaçları (scikit-learn HistGradientBoosting; derinlik 3,
öğrenme hızı 0.05, 200 ağaç, yaprakta en az 200 örnek, L2 1.0, sabit tohum).

**İşlem:** modelin "yukarı" olasılığı eğitim verisindeki tahminlerin en üst %10'undaysa long, en alt %10'undaysa short;
giriş o anın kapanışı, çıkış 1 saat sonra; aynı anda tek işlem; masraf gidiş-dönüş %0.01 (2x ile de bakılır).

**Yıl yıl sınav (geliştirme içinde):** 2020-2021 ile eğit → 2022'de sına; 2020-2022 → 2023; 2020-2023 → 2024.

**Geçme (long ve short ayrı):** üç sınav yılı birlikte en az 100 işlem, 2x masrafla ortalama > 0, t ≥ 2.5, üç yılın en
az ikisinde 2x masrafla artı. Geçen taraf için model 2020-2024 ile eğitilip doğrulamada **bir kez** sınanır: en az 30
işlem, 2x masrafla ortalama > 0, t ≥ 2.0.

**Sahte veri kontrolü (sonuçtan önce):** aynı kod saf rastgele yürüyüş verisinde geçmedi: long 2x masrafla -0.009 ATR (t -2.8), short -0.002 ATR (t -0.6), işlemlerin %49'u kazançlı.

**Sonra:** geçerse stoplu/hedefli bir işlem kuralına çevrilip kâğıt takibe alınır (gerçek emir yok), 30 canlı işlemde
hüküm. Geçmezse: Nasdaq 5 dk'da fiyat ve seviye bilgisinin birleşimi de masrafı karşılayacak yön bilgisi taşımıyor;
sıradaki adım fiyat dışı bilgi (VIX, haber günleri) ve uzun günlük geçmiş.

Kod: `research/ogrenen/ml.py`. İş akışı: `.github/workflows/nasdaq_ogrenen.yml`.

---
