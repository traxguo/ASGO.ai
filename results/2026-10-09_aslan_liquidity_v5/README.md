# aslan_liquidity v5 — sadece likidite alımı + OB/iFVG/MSS — geliştirme verisi (2020-2024)

Kod: `AslanLiq5_*` (`strategies/candidates/aslan_liquidity_v3.py`, 2R varyantları `aslan_liquidity_v4.py`). Kart: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md).

## Kurallar
Likidite seviyeleri v3 ile aynı (1h/4h/1d, önceki gün, seanslar). **Sadece alım (iğneyle alıp geri dönüş)**, kırılımda işlem yok. Onay: 5 dk veya 15 dk'da order block (alımdaki son ters mumun ötesinde kapanış), iFVG veya MSS. **Stop: alımı yapan tepenin/dibin %0.1 ötesi.** 4 saatlik trend filtresi. Hedef 1R veya 2R.

## Sonuç: geçemedi
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate |
|---|---|---|---|---|
| 15 dk, 1R | 1658 | -0.24R | -0.05R | %46.8 |
| 15 dk, 2R | 1625 | -0.24R | -0.05R | %31.1 |
| 5 dk, 1R | 1878 | -0.27R | -0.01R | %49.0 |
| 5 dk, 2R | 1851 | -0.27R | -0.01R | %32.6 |

Raporlar: [15m/rapor.md](15m/rapor.md), [5m/rapor.md](5m/rapor.md). Her yıl eksi. Order block onayı neredeyse hiç tek başına tetiklenmedi (iFVG/MSS hep önce geldi).

## v1-v5 toplamı
5 versiyon, 22 varyant; maliyet öncesi hepsi -0.05R ile +0.01R arası, maliyetle hepsi eksi. Doğrulama ve kasa verisi kullanılmadı.
