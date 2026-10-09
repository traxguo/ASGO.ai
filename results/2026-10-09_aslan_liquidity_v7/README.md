# aslan_liquidity v7 — likidite alımı → 5 dk MSS → 1 dk giriş — geliştirme verisi (2020-2024)

Kod: `AslanLiq7_1m`, `AslanLiq7_1m_Retest` ([`strategies/candidates/aslan_liquidity_v7.py`](../../strategies/candidates/aslan_liquidity_v7.py)). Kart: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md).

## Kurallar (Aslan'ın grafik 3, 4, 5 notları, 2026-10-09)
1. Likidite alımı (seviyeler v3 ile aynı). Stop alımı yapan tepe/dibin %0.1 ötesi, hedef 1R, 4 saatlik trend filtresi, haber filtresi.
2. **5 dk'da MSS şart**: bir 5 dk mumu son tepenin/dibin ötesinde kapanmalı.
3. Giriş iki türlü test edildi:
   - `AslanLiq7_1m` (grafik 4-5 notu): MSS'ten **sonra** 1 dk'da oluşan FVG veya iFVG mumunun kapanışında giriş (en fazla 1 saat beklenir).
   - `AslanLiq7_1m_Retest` (grafik 3 notu): MSS mumunun bıraktığı 5 dk FVG'ye fiyat geri gelince giriş (boşluğun yakın kenarına limit emir, 1 saat geçerli, önce stop görülürse iptal).

## Sonuç: geçemedi
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Ortanca stop |
|---|---|---|---|---|---|
| 1 dk FVG/iFVG girişi | 1945 | -0.21R | -0.03R | %48.2 | %1.43 |
| FVG'ye geri dönüş girişi | 1148 | -0.22R | -0.02R | %48.7 | %1.28 |

Long ve short ayrı ayrı eksi (-0.21 / -0.20R ve -0.22 / -0.21R). 5 coinin hepsi ve her yıl eksi.
Not: 1 dk testleri bellek yüzünden coin coin ayrı çalıştırıldı (her coin kendi test hesabıyla); R sonuçları bundan etkilenmez, bu yüzden sermaye grafiği yerine işlem listeleri (`*_trades.csv`) konuldu. Al-tut kıyası için aynı dönem: [v6 raporu](../2026-10-09_aslan_liquidity_v6/1m/rapor.md) (eşit ağırlık al-tut +%2358).

## v1-v7 toplamı
7 versiyon, 26 varyant; maliyet öncesi hepsi -0.07R ile +0.03R arası, maliyetle hepsi eksi. Doğrulama ve kasa verisi kullanılmadı.
