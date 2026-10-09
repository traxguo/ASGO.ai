# aslan_liquidity v3 — Aslan'ın 2026-10-09 kuralları — geliştirme verisi

Strateji kartı: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md) (bölüm "v3"). Önceki testler: [v1](../2026-10-08_aslan_liquidity_ilk_backtest/README.md), [v2](../2026-10-08_aslan_liquidity_v2/README.md)

## Kurallar (kısaca)
1R hedef / 1R stop; likidite: 1h-4h-1d tepe/dipleri, önceki gün, seans (Asya/Londra/New York) tepe/dipleri; iğneyle alıp dönerse dönüş yönünde, mumla kırarsa kırılım yönünde; giriş 15 dk veya 5 dk MSS/iFVG; trend HH+HL / LH+LL (4h, 4h+1h veya filtresiz); stop iğne (en fazla gövdenin %175'i); haber filtresi; risk %1.

## Sonuç: geçemedi, v2'den kötü
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Profit factor |
|---|---|---|---|---|---|
| 15 dk, 4h trend | 3200 | -0.32R | +0.01R | %46.2 | 0.47 |
| 15 dk, 4h+1h trend | 2701 | -0.34R | -0.04R | %45.3 | 0.56 |
| 15 dk, filtresiz | 2743 | -0.39R | -0.01R | %44.0 | 0.50 |
| 5 dk, 4h trend | 1838 | -0.58R | 0.00R | %41.2 | 0.33 |
| 5 dk, 4h+1h trend | 2211 | -0.46R | -0.03R | %44.1 | 0.35 |
| 5 dk, filtresiz | 2172 | -0.48R | -0.01R | %43.3 | 0.34 |

Raporlar: [15m/rapor.md](15m/rapor.md), [5m/rapor.md](5m/rapor.md).

**Dikkat:** Test hesapları %1 riskle bile erken sıfırlandı (çoğu 2020-2022 arasında), bu yüzden sonraki yılların işlemleri açılamadı. İşlem başı R değerleri yine de geçerli (binlerce işlem).

## Neden
- **Maliyet hariç her versiyon ~0R.** 1R hedefle başa baş için %50 kazanma lazım; sinyaller %41-46 kazanıyor. Yani giriş kuralları yazı-tura ile aynı.
- **Stoplar çok dar, maliyet R'yi yiyor:** ortanca stop 15 dk'da %0.9, 5 dk'da %0.5. İşlem başı ~%0.2 maliyet = 0.2-0.4R. En dar stoplu çeyrek -0.7R ile -0.9R.
- Kırılım (break) ve alım (sweep) ikisi de maliyet hariç ~0R. Trend filtresi fark yaratmıyor.

## Üç versiyonun ortak sonucu
v1 (2R), v2 (%175 iğne), v3 (1R, seanslar, kırılım, 5 dk) dahil denenen 14 varyantın **hiçbiri maliyet öncesi bile anlamlı bir artı üretmedi**. Kurala dökülen haliyle bu stratejinin bu 5 coinde kenarı yok. Doğrulama ve kasa verisi kullanılmadı.
