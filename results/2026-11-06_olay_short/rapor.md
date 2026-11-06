# Olay Short — Binance silme / izleme etiketi duyurularından sonra short (2026-11-06)

## GUO'ya not
- Yeni fikir: Binance bir coini listeden çıkaracağını ya da riskli diye etiketleyeceğini duyurunca o coini short'luyoruz.
- Son 15 ayda (2025-01 → 2026-03) çok iyi çalışmış: 89 işlem, işlem başı ortalama +0.32R (yaklaşık %+9.5 net), rastgele short'tan açıkça iyi.
- Ama 2020-2024'te zayıf: hafif artı, o da çoğunlukla tek bir olaydan (LUNA çöküşü). Önceden koyduğumuz geçme şartını (iki dönemde de rastgeleden iyi olmak) bu yüzden **geçemedi**.
- Yani: umut veren bir ipucu, ama henüz "kanıtlanmış strateji" değil. Kasa testi (son 6 ay) yapılmadı, onu denetleyici onaylarsa bir kez yapabiliriz.

## Kural (ön kayıt: cards/olay_short.md, commit b4e83be — getiriler görülmeden önce)
- Olaylar: E1 spot silme duyurusu, E2 izleme etiketi eklendi, E3 vadeli kontrat silme duyurusu (başlık + metinden coin adı). Aynı coinde 30 gün içinde tek olay.
- Duyurudan sonraki 2. saatlik mumun açılışında short, stop %30 (1s en yükseğe göre), 7 gün sonra çık (veri biterse son kapanış).
- Masraf %0.20 + stop kayması %0.30 + gerçek funding; risk %1/işlem, en fazla 10 açık işlem.
- Veri: Binance duyuru başlıkları/metinleri GitHub sunucusundan çekildi (`research/events/binance_announcements*.csv`); 1s fiyat silinenler dahil 680 coin.

## Sonuç (ana kural)
| | Dev 2020-24 | Val 2025-01..2026-03 |
|---|---|---|
| İşlem | 61 | 89 |
| Ortalama R | +0.029 | **+0.318** |
| Medyan R | +0.091 | +0.253 |
| PF | 1.12 | 2.24 |
| Kasa getirisi (%1 risk) | +1.6% | +32.1% |
| En büyük düşüş | 5.1% | 7.3% |
| 2x masraf R | +0.022 | +0.312 |
| En iyi 3 olay çıkınca R | −0.064 | +0.233 |
| Rastgele tarih kontrolü (aynı coinler) p | 0.174 ✗ | 0.000 ✓ |

Türlere göre val: E1 +0.32R (25), E2 +0.22R (31), E3 +0.41R (33). Yıllara göre: 2022 +0.13 (17), 2023 −0.12 (5), 2024 +0.06 (37), 2025 +0.22 (63), 2026 Q1 +0.56 (26).
Komşular (gecikme 1/2/24s × tutma 3/7/14/30g × stop %20/30/50): 36'dan 15'i iki dönemde artı. 24 saat gecikmede kazanç çoğunlukla kayboluyor.

## Değerlendirme
- Ön kayıtlı şart 2 (rastgele kontrolü iki dönemde %95'te geçmek) dev'de sağlanmadı → **GEÇMEDİ**.
- Doğrulama sonucu güçlü ve geniş tabanlı (üç türde de artı, en iyi 3 çıkınca da artı). Etkinin 2025'ten sonra güçlendiği görülüyor (Binance silme/izleme etiketlerini sıklaştırdı).
- Bağımsız test olarak kasa (2026-04 → 2026-09) kalıyor; sadece denetleyici onayıyla, bu kuralla, bir kez.

## Kasa testi (2026-04 → 2026-09) — denetleyici onayıyla bir kez — GEÇMEDİ
- GUO'ya not: son 6 ayın verisiyle yapılan bağımsız testte kural çok az kâr etti (+0.04R) ve bu kâr sadece en iyi 3 işlemden geliyor. Doğrulamadaki güçlü sonuç tekrar etmedi. Bu fikir de elendi.
- 58 işlem, +0.042R, PF 1.14, 2x masraf +0.035R, rastgele kontrol p 0.047, en iyi 3 çıkınca −0.037R (şart: artı kalmalı).
- Türler: E1 +0.13R (19), E2 +0.07R (26), E3 −0.14R (13).
- Reduce-only kontrolü: 2026 E3 girişlerinin hiçbiri yasak pencereye düşmüyor; ama 2026-10'dan beri Binance bazı silmelerde yeni pozisyonu duyuru anında kapatıyor, yani E3 canlıda artık uygulanamaz.
