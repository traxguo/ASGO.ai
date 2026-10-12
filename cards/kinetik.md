# kinetik — Kinetik Geri Çekilme (proje sahibinin getirdiği kural, 2026-10-12): REDDEDİLDİ

Kod (araştırma simülasyonu): [`research/scans/kinetic_pullback.py`](../research/scans/kinetic_pullback.py)

## Hipotez
1 saatlik grafikte güçlü trend varken 15 dakikalık grafikte EMA50'ye geri çekilme ve StochRSI dönüşü, 2-4 saatlik bir dalganın başıdır.

## Koşullar (long; short tam tersi)
- 1h (son kapanmış mum): kapanış > EMA50 > EMA200, ADX(14) > 25.
- 15m: son 5 mumda fiyat EMA50'ye değmiş (en fazla %0.2 uzakta), StochRSI K son 3 mumda 20'nin altına inmiş ve şimdi D'yi yukarı kesiyor, RSI 40-55, hacim önceki kırmızı mumdan büyük veya 20 mum ortalamasının üstünde.
- Giriş: sonraki 15m mumun açılışı.

## Çıkış
- Stop: giriş − 2.5 ATR(15m) (en fazla %5).
- İzleyen stop: kâr %1.5'e ulaşınca, en iyi fiyatın %0.5 gerisinden takip.
- Ölü işlem: 16 mum (4 saat) sonra kâr %0–0.5 arasındaysa kapat.
- Momentum kaybı: kâr ≥ %1.5 iken RSI 70'i görüp 60'ın altına inerse kapat.
- Panik: kapanış hacimli şekilde EMA50'nin altına inerse kapat (zarar %1'den küçükse).

## Test (36 coin, maliyet %0.2, 15m veri)
| Dönem | Yön | Değişken | İşlem | Günde | Kazanan | Brüt R | Net R | Ort. süre |
|---|---|---|---|---|---|---|---|---|
| 2020–2024 | long | tam kural | 10 766 | 5.9 | %39 | -0.007 | -0.137 | 1.2 sa |
| 2020–2024 | short | tam kural | 16 948 | 9.3 | %35 | +0.016 | -0.135 | 1.2 sa |
| 2020–2024 | long | panik çıkışı yok | 10 025 | 5.5 | %52 | -0.011 | -0.138 | 2.8 sa |
| 2020–2024 | short | panik çıkışı yok | 15 156 | 8.3 | %51 | +0.040 | -0.107 | 3.5 sa |
| 2025-01 → 2026-03 | long | tam kural | 2 639 | 5.8 | %33 | +0.007 | -0.152 | 1.5 sa |
| 2025-01 → 2026-03 | short | tam kural | 4 372 | 9.6 | %34 | +0.030 | -0.114 | 1.5 sa |
| 2025-01 → 2026-03 | long | panik çıkışı yok | 2 424 | 5.3 | %47 | -0.008 | -0.163 | 3.2 sa |
| 2025-01 → 2026-03 | short | panik çıkışı yok | 3 917 | 8.6 | %51 | +0.060 | -0.082 | 3.5 sa |

## Durum: reddedildi (2026-10-12)
Masraf öncesi sonuç sıfıra çok yakın; masraf işlem başı 0.13–0.16R. Short tarafında iki dönemde de küçük bir brüt artı var (+0.04 / +0.06R) ama masrafın üçte biri bile değil. Panik çıkışı işlemlerin yarısını girişten hemen sonra kapatıyor (giriş zaten EMA50'nin yanında).

### Limit emirle (düşük masraf) deneme, 2026-10-12 (`research/scans/kinetic_maker.py`, 2020–2024)
Giriş sinyal kapanışına limit emirle (en fazla 4 mum bekler, fiyat limiti %0.02 geçerse dolmuş sayılır), masraf: limit %0.02, piyasa çıkışı %0.06 + %0.03 kayma.
| Değişken | Long net R | Short net R | Short kazanan |
|---|---|---|---|
| Orijinal çıkışlar (izleyen stop) | -0.096 | -0.060 | %55 |
| Sabit limit hedef 1.5 ATR | -0.097 | -0.071 | %59 |
| Sabit limit hedef 2.5 ATR | -0.096 | -0.064 | %53 |
| Hedef 1.5 ATR, limit %0.2 daha iyi fiyattan | -0.073 | -0.057 | %61 |
Masraf yarıdan aza indi ama limit emir sadece fiyat aleyhe giderken doluyor; brüt sonuç da kötüleşti. Reddedildi, doğrulama dönemine bakılmadı.

