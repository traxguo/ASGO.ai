# aslan_liquidity v6 — teyit sadece likidite alımından SONRA oluşursa — geliştirme verisi (2020-2024)

Kod: `AslanLiq6_5m`, `AslanLiq6_1m` (`strategies/candidates/aslan_liquidity_v3.py`, `post_sweep=True`). Kart: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md).

## Kurallar (Aslan, 2026-10-09)
v5 ile aynı (sadece likidite alımı, stop alımı yapan tepe/dibin %0.1 ötesi, 4 saatlik trend, hedef 1R), tek fark teyit:
- **Alımdan sonra oluşan yeni FVG** (işlem yönünde boşluk), **alımdan sonra oluşan bir boşluğun ters kırılması (iFVG)** veya **MSS**.
- Alımdan önce oluşmuş boşluklar artık sayılmıyor (v5'te sayılıyordu). Order block çıkarıldı.
- Giriş grafiği 5 dk veya 1 dk.

## Sonuç: geçemedi
| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Ortalama stop |
|---|---|---|---|---|---|
| 5 dk, 1R | 3022 | -0.25R | -0.01R | %49.2 | %0.98 |
| 1 dk, 1R | 2508 | -0.37R | +0.00R | %49.2 | %0.60 |

Raporlar: [5m/rapor.md](5m/rapor.md), [1m/rapor.md](1m/rapor.md). Long ve short ikisi de eksi, her yıl eksi. 1 dk testinde %1 riskle hesap Kasım 2024'te bitti (son işlem 05.11.2024).
Teyitlerin %80'i "alım sonrası yeni FVG". Stop ne kadar darsa maliyet o kadar ağır: en dar çeyrekte -0.70R.

## v1-v6 toplamı
6 versiyon, 24 varyant; maliyet öncesi hepsi -0.07R ile +0.03R arası (yani yazı-tura), maliyetle hepsi eksi. Doğrulama ve kasa verisi kullanılmadı.
