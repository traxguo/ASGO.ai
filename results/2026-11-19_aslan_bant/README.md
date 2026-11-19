# Aslan bant kırılımı (Nasdaq 5 dk) — ön kayıt ve sonuç

Proje sahibinin onayıyla 5. ve **son** Nasdaq fikri (2026-11-19). Önceki "sıkışma" testi (`results/2026-11-19_aslan_sikisma/`)
MSP'yi kırılımdan sonraki küçük 5 dk tepe olarak almıştı; Aslan bunun yanlış olduğunu, **MSP'nin bandın kendi direnci /
desteği** olduğunu söyledi (1. örnek grafik üzerine yorum). Kural Türkçe yazılıp proje sahibine gösterildi; bant süresi
düzeltmesi (12-48 mum) dışında itiraz gelmedi.

## 1. Ön kayıt (sonuç görülmeden yazıldı)

Veri, maliyet, dönemler, rastgele kontrol ve geçme çıtası `results/2026-11-19_aslan_5dk/README.md` ile aynı. Kasa
(2026-04 → 09) yüklenmez. Puanlar ~24000 seviyesine göre yüzdeye çevrildi (eski yıllarda fiyat düşüktü):
40 puan = %0.17, 60 = %0.25, 80 = %0.33, 100 = %0.42, 150 = %0.62.

Long (short tam tersi):
1. **Bant:** B mumundan önceki son N mum (N = 12-48; koşulları sağlayan en uzun N). Direnç = en yüksek iğne, destek =
   en düşük iğne, genişlik %0.17 - %0.62. Dirence en az 2, desteğe en az 2 dokunuş (genişliğin %15'i yakınında), aynı
   tarafın ilk ve son dokunuşu arasında en az 3 mum.
2. **Giriş (MSP):** B mumu direncin üstünde kapatır; giriş B'nin kapanışı. FVG / iFVG şart değil. Aynı yönde son
   tetikten sonraki 12 mum içinde yeni tetik yok.
3. **Stop:** kırılım bacağında (desteğe son dokunuştan B'ye kadar) oluşmuş, alt kenarı girişin altında olan en yakın
   (en yüksek) yükseliş 5 dk FVG'sinin alt kenarının ~5 puan altı. FVG yoksa bant içindeki son onaylı 5 dk dibin ~5 puan
   altı. Risk %0.04'ten küçük veya %0.42'den (100 puan) büyükse işlem yok.
4. **Hedef:** girişin %0.17 - %0.33 (40-80 puan) yukarısındaki en yakın alınmamış seviye (önceki gün, Asya, Londra,
   1 sa tepe; `aslan_5dk` ile aynı liste), ~5 puan önce. Bu aralıkta seviye yoksa sabit %0.25 (60 puan).
5. **Saat:** B kapanışı TR 09:00 - 22:00; NY açılışının ilk 15 dakikası değil. Yakın ters likidite (8b) ve büyük zaman
   dilimi engeli (8c) `aslan_5dk` ile aynı (8c onayı kırılım bacağının başlangıcından aranır). Çıkış (stop / hedef /
   24 saat), aynı anda tek işlem: aynı.

**Yargı:** long ve short ayrı. Çıta: net > 0 ve PF ≥ 1.2 iki dönemde, rastgele kontrol p < 0.05 (gel.), 2x masrafta artı,
doğrulamada ≥ 30 işlem, %1 riskle düşüş ≤ %25.

### Bilgi ızgarası (sadece bilgi, seçim yapılmaz)
8c kuralı yok; hedef hep 60 puan; bant en az 24 mum; bant en fazla %0.30; stop bandın öbür ucunda.

Geçerse: kâğıt takip (gerçek emir yok), 30 canlı işlemde hüküm. Geçmezse: kodlanmış Aslan ailesi kapanır; öneri
Aslan'ın kendi işlemlerini giriş anında kaydetmesi.

Kod: `research/aslan_5dk/bant.py`. İş akışı: `.github/workflows/aslan_bant.yml`.

---
