# aslan_liquidity v2 — Aslan'ın düzeltmeleri — geliştirme verisi — 2026-10-08

Strateji kartı: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md). İlk test: [../2026-10-08_aslan_liquidity_ilk_backtest](../2026-10-08_aslan_liquidity_ilk_backtest/README.md)

## Değişenler (Aslan, 2026-10-08)
1. **Stop:** iğne gövdeden uzun olabilir ama en fazla gövdenin %175'i kadar. Daha uzunsa stop gövdenin ucundan 1.75 gövde uzağa konur.
2. **Short'lar:** günlük yön yukarıyken de short aranmalı. İki versiyon test edildi: günlük yön filtresi **açık** (`AslanLiq2_*`) ve **kapalı**, yani iki yön de her zaman aranıyor (`AslanLiq2_*_NoBias`).

Diğer her şey ilk testle aynı (likidite seviyeleri, MSS/iFVG, 2R hedef, haber filtresi, %1 risk).

## Sonuç: hâlâ geçemedi, ama daha iyi
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Profit factor | İlk test |
|---|---|---|---|---|---|---|
| 1h, yön filtresi açık | 2222 | -0.16R | -0.04R | %31.5 | 0.80 | -0.21R |
| **1h, yön filtresi kapalı** | 3256 | **-0.14R** | -0.04R | %31.8 | 0.82 | — |
| 15m, yön filtresi açık | 3851 | -0.20R | -0.01R | %32.5 | 0.73 | -0.28R |
| 15m, yön filtresi kapalı | 5260 | -0.16R | +0.01R | %33.0 | 0.75 | — |

Raporlar: [1h/rapor.md](1h/rapor.md), [15m/rapor.md](15m/rapor.md). 15m'de test hesabı 2024 başında bitti (%1 riskle bile), bu yüzden 2024 işlemleri eksik.

## Gözlemler
- %175 iğne kuralı her versiyonda sonucu iyileştirdi (stoplar biraz genişledi, 1h ortanca %1.8 → %2.3).
- Günlük yön filtresini kapatmak sonucu bozmadı, hafifçe iyileştirdi. Yani karttaki günlük yön tanımı işe yaramıyor.
- Maliyet hariç sonuç hâlâ ~0R: girişlerin ~%32'si 2R'ye ulaşıyor, başa baş için ~%33 lazım, maliyetler (%0.2/işlem) de üstüne biniyor.
- 15m'de MSS girişleri maliyet hariç hafif artı (+0.03R), iFVG girişleri ~0R. 1h yön filtresiz MSS: -0.05R (maliyet dahil), en iyi alt grup.
- Hiçbir versiyon eşikleri (ortalama R > 0, PF ≥ 1.2, DD ≤ %25) sağlamadı. Doğrulama ve kasa verisi hâlâ kullanılmadı.
