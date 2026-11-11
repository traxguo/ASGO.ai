# nasdaq_paketi — Nasdaq: 2 yeni fikir (araştırma, 2026-11-11)
Rapor: [`results/2026-11-11_nasdaq_batch/README.md`](../results/2026-11-11_nasdaq_batch/README.md) ·
Kod: [`research/nasdaq_batch/batch.py`](../research/nasdaq_batch/batch.py) · İş akışı: `.github/workflows/nasdaq_batch.yml`

## Hipotez
Proje 2026-11-10'da Nasdaq'a (US100) odaklandı; plan en fazla 3 yeni ön kayıtlı fikre izin veriyor. Bu paket ilk ikisi.

## Yön
İkisi de; long ve short ayrı raporlandı.

## Fikirler (ana ayar)
- **N1 Haber günü yönü:** [n1] "Büyük ABD verisinden (Fed, enflasyon, istihdam) sonra ilk tepki %0.20'yi geçtiyse o yöne gir, New York kapanışında çık."
- **N2 Gergin dönemde gün içi momentum:** [n2] "Oynaklık yüksekken, ilk yarım saat yukarıysa son yarım saatte long, aşağıysa short; kapanışta çık."

Masraf gidiş-dönüş %0.010, gün içi (swap yok), her şey 2x masrafla da. Stop yok, saatli çıkış.

## Geçme şartı (ön kayıtlı)
Net > 0 ve PF ≥ 1.2 geliştirmede ve doğrulamada; rastgele girişten iyi (p < 0.05, geliştirme); 2x masrafta artı;
doğrulamada ≥ 30 işlem; düşüş ≤ %25.

## Durum: reddedildi (2026-11-11) — ikisi de geçmedi, kâğıt takip yok
- **N1:** geliştirme 92 işlem, -%0.237 / PF 0.64; doğrulama 24 işlem, -%0.361 / PF 0.43; rastgele kontrol p 0.98.
- **N2 long:** geliştirme +%0.023 / PF 1.19, doğrulama -%0.031 / PF 0.70 (p 0.26). **N2 short:** geliştirme -%0.027, doğrulama +%0.022 / PF 1.23 (p 0.59).
- Not (aday değil): N1'in tersi (ilk tepkiye karşı) bilgi ızgarasında iki dönemde artı göründü. Sonuç görüldükten sonra
  fark edildi; ön kayıt gereği benimsenmedi. Denenecekse yeni ön kayıt + doğrulanmış takvim + görülmemiş veri gerekir.

## Tekrar edilmez
Haber sonrası ilk tepkiyi takip (N1) ve ilk yarım saat → son yarım saat momentumu (N2), Nasdaq'ta.
