# endeks_forex_paketi — Endeks + forex: 8 bilinen fikir (araştırma, 2026-11-09)
Rapor: [`results/2026-11-09_endeks_forex_batch/README.md`](../results/2026-11-09_endeks_forex_batch/README.md) ·
Kod: [`research/endeks_forex/batch.py`](../research/endeks_forex/batch.py) · İş akışı: `.github/workflows/endeks_forex_batch.yml`
(HistData verisi GitHub sunucusunda indirilir; sonuç CSV'leri repoya commit'lenir)

## Hipotez
GUO daha sık işlem yapan, long ve short tarafta kâr eden çok sayıda strateji istiyor. Literatürde yıllardır bilinen
8 basit endeks/forex kuralı (Nasdaq, S&P 500, DAX, EUR/USD, GBP/USD, altın) aynı disiplinle test edildi.
Daha önce reddedilenler tekrar edilmedi (forex_tarama, forex_trend, Aslan kurallarının başka endekslerde denenmesi).

## Yön
İkisi de; long ve short ayrı raporlandı.

## Fikirler (ana ayar)
- **I1 Gece kayması:** [i1_long] "Kapanışta al, ertesi açılışta sat." · [i1_short] "Açılışta sat, kapanışta kapat."
- **I2 Ay dönümü:** [i2] "Ayın sondan 2. işlem günü kapanışta al, yeni ayın 3. işlem günü sat."
- **I3 RSI(2):** [i3] "Fiyat 200 günlük ortalamanın üstünde ve 2 günlük RSI 10'un altında: al; 5 günlük ortalamanın üstüne çıkınca sat." (short tersi)
- **I4 Boşluk doldurma:** [i4] "Açılış önceki kapanıştan %0.25'ten fazla uzakta: ters yöne gir, boşluk dolunca veya kapanışta çık."
- **I5 Üst üste 3 gün:** [i5] "3 gün üst üste düştü: al; ilk yükseliş gününde sat (en çok 5 gün)." (short tersi)
- **I6 Altın – dolar endeksi:** [i6] "Altın, dolardaki harekete göre fazla düştü (z < −2): al, 5 gün tut." (short tersi)
- **I7 DAX – Nasdaq farkı:** [i7] "DAX Nasdaq'a göre fazla geride (z < −2): DAX al + Nasdaq sat; fark kapanınca çık."
- **I8 Londra kırılımı:** [i8] "Asya seansı aralığı Londra sabahı kırıldı: kırılım yönüne gir, stop aralığın öbür ucu, 16:00'da çık."

Masraf (gidiş-dönüş): endeksler ve EUR/USD, GBP/USD %0.010, altın %0.015; gecelik swap tahmini; her şey 2x masrafla da.

## Geçme şartı (ön kayıtlı)
Net > 0 ve PF ≥ 1.2 geliştirmede ve doğrulamada; rastgele girişten iyi (p < 0.05, geliştirme); 2x masrafta artı;
doğrulamada ≥ 30 işlem; düşüş ≤ %25. Kazanma oranı sadece bilgi.

## Durum: reddedildi (2026-11-09) — 0/15 yön satırı geçti, kâğıt takip yok
- En yakın: **I3 RSI(2) long** (NAS/SPX): gel. +0.45% / PF 1.94 / %66 kazanma (71 işlem), doğ. +0.23% / PF 1.35 / %74 (34 işlem),
  2x masrafta artı, düşüş %5 — ama rastgele long girişten ayırt edilemiyor (p = 0.16). **I5 3 gün long** aynı (p = 0.10).
  2020-2026 boğa piyasasında birkaç gün tutulan herhangi bir long kazandırdı; kural buna anlamlı bir şey eklemiyor.
- Short tarafı hiçbir fikirde iki dönemde birden tutmadı.
- Gece kayması, boşluk doldurma, Londra kırılımı: masraftan sonra sıfır civarı veya eksi.
- Altın–DXY ve DAX–Nasdaq: çok az işlem, artı değil.

## Veri uyarısı
HistData "grxeur" (DAX) 2020-06-15 → 2023-12-01 arası DAX değil (Euro Stoxx 50 seviyesinde fiyat). Bu dönem eksik sayıldı.
Önceki Aslan GER40 testi (`results/2026-11-05_aslan_endeksler`) de bu bozuk veriyi kullanmış olmalı.

## Öğrenilenler
- Endeks long kurallarında rastgele giriş kontrolü şart: yükselen piyasada "kazanan" kural çoğu zaman sadece piyasanın yükselişi.
- Short için endeks ve forex'te basit fiyat kuralıyla avantaj bulunamadı (forex_trend ile aynı sonuç).
