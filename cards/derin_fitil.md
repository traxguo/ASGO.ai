# derin_fitil — düşen coinlerde çok derin panik fitilini al, 3 saat tut (ADAY, 2026-10-17)

Kod: [`research/scans/wick_catcher_downtrend.py`](../research/scans/wick_catcher_downtrend.py) (araştırma),
canlı demo: [`scripts/bitget_fitil.py`](../scripts/bitget_fitil.py) (Fitil Avcısı ile aynı bot, `DEEP_DEPTH`).

## Neden
Bütün botlar sadece yükselen piyasada çalışıyordu; 7 Ekim 2026'dan beri piyasa düşüyor ve hiç işlem yok.
Önce Fitil'in short aynası denendi (düşen coinde saat açılışının %3-5 üstüne satış limiti): **battı**
(doğrulama 2025-01 → 2026-03: -%30 ile -%46). Düşen coinlerde ani yükselişler (short squeeze) geri dönmüyor.
Tersine, düşen coinlerde **çok derin** (%6-10) panik fitilleri geri dönüyor.

## Kurallar (2026-10-17, kasa testinden önce donduruldu)
- Coin: `config/pairs_all36.json` (demo: Bitget'te listelenen 15'i).
- Günlük puan ≤ -1 ve son kapanmış günlük kapanış EMA(20) altı (düşüş trendi).
- Her saat başında: alış limit emri = saat açılışı × **0.92**, bir saat bekler. Dolum: 15m dip limitin %0.1 altına inerse.
- BTC aynı saatte açılışından %3+ düştüyse girilmez (Fitil'in koruması).
- Stop yok; dolumdan 3 saat sonra piyasa emriyle çıkış. Aynı anda en fazla 5 işlem, her biri kasa/5.
- Masraf: giriş %0.02 (maker), çıkış %0.06 + %0.05 kayma.

## Sonuçlar (işlem başı net, portföy en fazla 5 açık)
| Derinlik | Dönem | İşlem/gün (portföy) | İşlem başı | Kasa getirisi | En kötü düşüş |
|---|---|---|---|---|---|
| %6 | 2022-01 → 2024-12 | 0.23 | +0.52% | +28.3% | -14.9% |
| %6 | 2025-01 → 2026-03 | 0.23 | +2.19% | +54.9% | -2.1% |
| **%8** | 2022-01 → 2024-12 | 0.09 | +3.16% | +87.3% | -5.7% |
| **%8** | 2025-01 → 2026-03 | 0.08 | +3.33% | +26.7% | -1.1% |
| %10 | 2022-01 → 2024-12 | 0.05 | +4.20% | +50.6% | -3.1% |
| %10 | 2025-01 → 2026-03 | 0.06 | +7.77% | +47.2% | -0.7% |
| %8 | **kasa 2026-04 → 2026-09 (bir kez), 36 coin** | 0.02 (4 işlem) | +2.12% | +1.7% | -0.7% |
| %8 | **kasa, 45 hiç bakılmamış coin** | 0.18 (33 işlem) | +1.03% | +6.8% | -3.3% |

Üç derinliğin hepsi iki dönemde de artı: seçilen %8 tek şanslı nokta değil.

## Zayıf yanlar (gizlenmez)
- **Seyrek ve toplu:** işlemler çöküş günlerinde toplu gelir (2022-24'te 41 gün, 2025-26 Mart'ta 16 gün; ayda ~1 olay).
  En yoğun 3 gün çıkarılınca da artı (+3.9% / +3.3% işlem başı), ama günde 2-3 işlem hedefini tek başına çözmez.
- Sonucun bir kısmı büyük çöküş günlerinden (ör. 10 Ekim 2025: 15 işlem, ortalama +12%).
- Kasa örneği küçük (4 ve 33 işlem).
- 2023'te işlem başı ortalama eksi (-1.0%); kasa getirisi yine artı.

## Durum
2026-10-17: Bitget demoda Fitil Avcısı botunun içinde çalışıyor (yükselen coin: %5 limit, düşen coin: %8 limit).
