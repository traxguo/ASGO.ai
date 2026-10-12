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

## Kasa testi (36 coin, eşik %5 / %2, 3 saat, `research/scans/oi_flush_portfolio.py`)
Her işleme kasanın 1/N'i (N = aynı anda en fazla işlem), sinyaller sırayla alınır.
| Stop | En fazla işlem | Dönem | İşlem/gün | Ort. % | Kasa | En büyük düşüş | En kötü gün |
|---|---|---|---|---|---|---|---|
| yok | 5 | 2022–2024 | 1.07 | +0.11 | +25.3% | -13.7% | -7.2% |
| yok | 5 | 2025-01 → 2026-03 | 0.54 | +0.60 | +30.3% | -7.8% | -4.3% |
| yok | 3 | 2022–2024 | 0.91 | +0.08 | +19.8% | -21.3% | -12.1% |
| yok | 3 | 2025-01 → 2026-03 | 0.51 | +0.50 | +39.7% | -11.3% | -7.1% |
| %3 | 5 | 2022–2024 | 1.21 | -0.15 | -35.4% | -38.4% | -7.9% |
| %3 | 5 | 2025-01 → 2026-03 | 0.59 | +0.45 | +23.8% | -8.5% | -2.2% |
| %5 | 5 | 2022–2024 | 1.15 | -0.06 | -18.4% | -21.9% | -8.7% |
| %5 | 5 | 2025-01 → 2026-03 | 0.56 | +0.71 | +35.7% | -11.1% | -3.0% |

- Sabit stop geliştirme döneminde sonucu bozuyor: düşüş devam ederken stop olup sonra dönüşü kaçırıyor.
- Stopsuz ve en fazla 5 işlemle iki dönem de artıda ama işlem başı geliştirmede sadece +%0.11; masraf %0.25'e çıkarsa yarıya iner. Kırılgan.
- Aynı çöküşte birçok coin birden sinyal veriyor; işlem sınırı ilk gelenleri alıyor, bunlar daha zayıf.
- Sıradaki: daha akıllı stop (tasfiye dibinin altı), çöküşte en çok düşen coini seçmek, BTC ile birlikte filtre.

## Değişken denemeleri (36 coin, stopsuz, en fazla 5 işlem; önce sadece geliştirmede, seçilen bir kez doğrulamada)
| Değişken | Dönem | İşlem/gün | Ort. % | Ortanca % | Kasa | En büyük düşüş | En iyi gün hariç kasa |
|---|---|---|---|---|---|---|---|
| filtre yok | 2022–2024 | 1.07 | +0.11 | +0.11 | +25.3% | -13.7% | +12.4% |
| filtre yok | 2025-01 → 2026-03 | 0.54 | +0.60 | +0.08 | +30.3% | -7.8% | +6.5% |
| BTC sakinken (BTC 1s > -%1) | 2022–2024 | | -0.06 | | | | |
| coin günlük trendi yukarı | 2022–2024 | | -0.04 | | | | |
| stop: tasfiye dibinin %1 altı | 2022–2024 | | -0.07 | | | | |
| stop: tasfiye dibinin %3 altı | 2022–2024 | | -0.03 | | | | |
| **BTC de düşüyorken (BTC 1s ≤ -%1)** | 2022–2024 | 0.59 | +0.22 | +0.25 | +28.6% | -12.8% | +21.1% |
| **BTC de düşüyorken** | 2025-01 → 2026-03 | 0.22 | +1.84 | +0.03 | +37.5% | -5.6% | +5.3% |

- Masraf %0.25 olursa: BTC filtreli geliştirme +0.17%/işlem, kasa +20.5%; doğrulama +36.2%. Filtresiz geliştirme +11.4%'e iner.
- Yorum: tek coin değil, piyasanın topluca tasfiye olduğu anlar çalışıyor. BTC filtresi geliştirmede işlem başı getiriyi ikiye katladı ve en iyi gün olmadan da artıda.
- Zayıf yanlar: doğrulamada sadece 98 işlem, ortanca ~0, kazancın çoğu 10-11 Ekim 2025 çöküşünden. Sıklık günde ~0.2-0.6; GUO'nun istediği günde 2-3 işlemden uzak. Bu nadir olay stratejisi, sık scalp değil.
- Doğrulama dönemi artık bu seçim için kullanıldı; kasa (2026-04..09) hâlâ dokunulmadı.

## Saatte bir kontrol (canlıya uygun basit hali)
Sinyal sadece her saat başında bakılırsa (BTC filtresiyle): 2022–2024 günde 0.34 işlem, işlem başı +%0.23, ortanca +%0.39, kasa +17.3%, en büyük düşüş -11.2%. 2025-01 → 2026-03: 44 işlem, +%1.43, kasa +12.8%. Daha az işlem ama işlem başı aynı kalite.

## Canlı veri kaydı (2026-10-12'den itibaren)
Saatlik Dalga çalışmasında Bitget'in açık pozisyon ve fiyatı 36 coin için `forward/oi/bitget_oi.csv` dosyasına kaydediliyor (`scripts/record_oi.py`, anahtar yok, emir yok). Birkaç hafta birikince Bitget verisinde %5 eşiğinin Binance ile aynı davranıp davranmadığı kontrol edilecek.

## Canlı için açık soru
Binance verisine bulut/GitHub sunucularından erişim engelli olabilir; canlıda açık pozisyon Bitget'ten her 15 dakikada kaydedilerek hesaplanmalı (Bitget sadece anlık değeri veriyor).

## Durum: aday (araştırma), demo yok
