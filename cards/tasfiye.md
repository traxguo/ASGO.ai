# tasfiye — sert düşüşte zorla kapatılan longlardan sonra al, 3 saat tut (ADAY, araştırma aşaması)

Araştırma kodu: [`research/scans/oi_flush.py`](../research/scans/oi_flush.py) (tarama: [`research/scans/oi_scan.py`](../research/scans/oi_scan.py)). Veri: Binance 5 dakikalık açık pozisyon (`research/data/fetch_metrics.py`, 2022-01 → 2026-03).

## Hipotez
Bir coinde 1 saat içinde fiyat sert düşerken açık pozisyon (open interest) da hızla azalıyorsa, kaldıraçlı longlar zorla kapatılıyor (tasfiye). Zorla satış bitince fiyat birkaç saat içinde kısmen geri döner.

## Yön
sadece long

## Giriş koşulları (15m mum kapanışı)
- [oi_flush] Teknik: açık pozisyon son 1 saatte en az %5 azaldı | Açıklama: "Son 1 saatte açık pozisyonların %{oi} kadarı kapandı (zorla kapatma)."
- [price_drop] Teknik: fiyat son 1 saatte en az %2 düştü | Açıklama: "Fiyat 1 saatte %{drop} düştü."
- Giriş: sonraki 15m mumun açılışı. Açık pozisyon verisi mum kapanışından 5 dakika önceki son kayıttan alınır (ileriyi görme yok).

## Çıkış (şimdilik)
- 3 saat sonra kapanış. Stop henüz yok; sıradaki test stop, aynı anda en fazla işlem ve kasa düşüşü.

## Test geçmişi (masraf %0.2 dahil, işlem başı % getiri, 3 saat tutma)
| Coinler | Eşik (OI / fiyat) | Dönem | İşlem | Ortalama | Ortanca | Kazanan | En iyi 5 hariç |
|---|---|---|---|---|---|---|---|
| 8 coin (ilk bakılan) | %5 / %2 | 2022–2024 | 388 | +0.49 | +0.28 | %55 | +0.34 |
| 8 coin | %5 / %2 | 2025-01 → 2026-03 | 50 | +2.37 | +0.37 | %58 | +0.40 |
| 28 coin (hiç bakılmamış) | %5 / %2 | 2022–2024 | 1 354 | +0.27 | +0.26 | %56 | +0.22 |
| 28 coin | %5 / %2 | 2025-01 → 2026-03 | 281 | +1.32 | +0.47 | %57 | +0.75 |
| 28 coin | %4 / %1.5 | 2022–2024 | 2 648 | +0.16 | +0.13 | %53 | +0.13 |
| 28 coin | %4 / %1.5 | 2025-01 → 2026-03 | 511 | +0.78 | +0.24 | %53 | +0.48 |

- Zayıf yıl: 2022 (ayı piyasası) yaklaşık -0.1% işlem başı.
- En büyük katkı 10 Ekim 2025 çöküşünden; onsuz da iki dönem artıda.
- Eşikler 8 coinde 3 deneme ile seçildi, 28 coin bu seçimden sonra ilk kez test edildi.
- Sıklık: 36 coinde %5/%2 ile günde ~1.3, %4/%1.5 ile ~2.2 işlem.

## Canlı için açık soru
Binance verisine bulut/GitHub sunucularından erişim engelli olabilir; canlıda açık pozisyon Bitget'ten her 15 dakikada kaydedilerek hesaplanmalı (Bitget sadece anlık değeri veriyor).

## Durum: aday (araştırma), demo yok
