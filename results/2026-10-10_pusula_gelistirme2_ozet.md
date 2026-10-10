# Geliştirme turu 2 — 2026-10-10

## GUO'ya not
- **Bir geliştirme kabul edildi.** Bitcoin düşüşe dönünce açık long'ları kapatmak, iki coin grubunda da sonucu iyileştirdi. Pusula v2'nin ilk parçası bu.
- Eski 16 coinde işlem başı kazanç +0.95R'den +1.20R'ye çıktı. Yeni 20 coinde +0.44R'den +0.46R'ye çıktı. Kasanın en çok eridiği an değişmedi.
- **Dikkat:** Bu kural sadece 10 işlemi değiştirdi, 9'u iyileşti. Kazancın çoğu tek bir büyük ETC işleminden (2021) geliyor. Az örnek, o yüzden ileriye dönük takipte de izlenecek.
- İkinci fikir ("sadece Bitcoin'den güçlü coinde long") **reddedildi**. İki grupta da kötüleştirdi, çünkü en büyük kazançları kaçırıyor.

## Sonuç (2020-01 → 2026-09, sadece long, en fazla 3 işlem, 4h + 1h detay)
| Liste | Sürüm | İşlem | İşlem başı | Net | Max DD | En iyi 10 işlem dışında |
|---|---|---|---|---|---|---|
| Eski 16 | PusulaTrendLong (temel) | 210 | +0.95R | +%386 | %26.1 | +0.4R |
| Eski 16 | BtcExit (2a) | 210 | +1.20R | +%561 | %26.1 | +8.2R |
| Eski 16 | RS (2b) | 170 | +0.72R | +%167 | %20.3 | -23.0R |
| Yeni 20 | PusulaTrendLong (temel) | 150 | +0.44R | +%65 | %24.7 | -64.1R |
| Yeni 20 | BtcExit (2a) | 150 | +0.46R | +%68 | %24.6 | -62.1R |
| Yeni 20 | RS (2b) | 104 | +0.27R | +%24 | %18.2 | -58.2R |

- 2a, eski 16'da 8 işlemin, yeni 20'de 2 işlemin çıkışını değiştirdi. 10 işlemin 9'u iyileşti. En büyük fark ETC 2021-03 işleminde.
- **Karar:** 2a kabul, `PusulaV2` adayına girdi. 2b red.
- Ayrıntılı raporlar: `results/2026-10-10_pusula_gelistirme2_wide16/` ve `results/2026-10-10_pusula_gelistirme2_new20/`.
