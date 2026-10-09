# aslan_liquidity v4 — videodaki yöntem — geliştirme verisi (2020-2024)

Strateji kartı: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md) (bölüm "v4"). Kod: `strategies/candidates/aslan_liquidity_v4.py`.

## Kurallar (videodaki kontrol listesinden)
1. **Günlük yön:** günlük grafikte HH+HL → yukarı, LH+LL → aşağı.
2. **Trend:** 4 saatlikte aynı yön.
3. **Bölge (POI):** 1 saatlik FVG, order block (boşluktan önceki son ters mum) veya iFVG. Bir kez kullanılır, ötesinde kapanırsa veya 5 gün geçerse silinir.
4. **Giriş:** fiyat bölgeye dönünce, 5 dk veya 15 dk grafikte son mini tepeyi (dibi) kıran **engulf** mumu. Giriş o mumun kapanışı, stop dönüşün en uç noktası (iğne en fazla gövdenin %175'i), hedef 1R (Aslan) veya 2R.

## Sonuç: geçemedi
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Profit factor | Max DD (%1 risk) |
|---|---|---|---|---|---|---|
| 15 dk, 1R | 643 | -0.24R | 0.00R | %48.2 | 0.64 | %78.5 |
| 15 dk, 2R | 621 | -0.25R | -0.01R | %32.2 | 0.73 | %81.0 |
| 5 dk, 1R | 1692 | -0.33R | -0.01R | %47.2 | 0.55 | %99.6 |
| 5 dk, 2R | 1588 | -0.32R | 0.00R | %32.2 | 0.72 | %99.4 |

Raporlar: [15m/rapor.md](15m/rapor.md), [5m/rapor.md](5m/rapor.md). Bu sefer hesaplar dönem sonuna kadar yaşadı; 5 yılın her yılı eksi (2020 hariç ~0).

- FVG, iFVG ve order block bölgelerinin hiçbiri maliyet hariç anlamlı artı değil (en iyisi 15 dk 2R FVG: +0.08R maliyet hariç, -0.13R maliyet dahil).
- Kazanma oranları tam olarak yazı-tura beklentisinde: 1R'de %47-48, 2R'de %32.

## v1-v4 toplamı
4 versiyon, 18 varyant. Maliyet öncesi hepsi -0.05R ile +0.01R arasında; maliyetle hepsi eksi. Kurala dökülen hiçbir halinin bu 5 coinde kenarı yok. Doğrulama ve kasa verisi kullanılmadı.
