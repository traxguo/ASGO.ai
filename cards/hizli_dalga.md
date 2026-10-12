# hizli_dalga — Dalga'nın 15 dakikalık hızlı sürümü (REDDEDİLDİ, 2026-10-12)

Kod: [`research/scans/fast_dalga.py`](../research/scans/fast_dalga.py) (araştırma taraması, strateji dosyası yok)

## Fikir
GUO: "Ya düzelt ya yenisini yap". Demoda çalışan Dalga'nın mantığı (günlük trend yukarıyken tepe kırılımında al) 15 dakikalık grafikte, birkaç saat tutarak denendi.

## Kurallar
- Coinin günlük puanı ≥ +1 (veya +3) ve son günlük kapanış EMA(20) üstünde (son kapanmış gün).
- 15m kapanış son N mumun tepesini ilk kez kırar → sonraki 15m açılışta long.
- Çıkış: H saat sonra; isteğe bağlı stop K × ATR(15m). Masraf %0.2 gidiş-dönüş. 36 coin.

## Sonuçlar (işlem başı %, masraf dahil)
| N (mum) | Tutma | Stop | Puan | Dönem | İşlem/gün | Ort. | Ortanca |
|---|---|---|---|---|---|---|---|
| 24 (6 saat) | 3 saat | yok | ≥1 | 2020–2024 | 20.2 | -0.20 | -0.33 |
| 24 | 3 saat | 2 ATR | ≥1 | 2020–2024 | 20.9 | -0.22 | -0.63 |
| 96 (1 gün) | 6 saat | yok | ≥1 | 2020–2024 | 7.9 | -0.06 | -0.37 |
| 96 | 6 saat | yok | 3 | 2020–2024 | 6.2 | 0.00 | -0.34 |
| 192 (2 gün) | 12 saat | yok | 3 | 2020–2024 | 3.6 | +0.39 | -0.28 |
| 192 | 24 saat | yok | 3 | 2020–2024 | 2.8 | +0.94 | -0.24 |
| 192 | 24 saat | yok | 3 | 2025-01 → 2026-03 | 1.7 | -0.18 | -0.32 |
| 192 | 12 saat | yok | 3 | 2025-01 → 2026-03 | 2.2 | -0.21 | -0.32 |

- Saatlerce tutmada brüt avantaj yok: sonuç ≈ masraf kadar eksi.
- 12-24 saat tutmada geliştirme artı, ama bunun çoğu boğa yıllarında trende binmek (aynı rejimde rastgele giriş 24 saatte +0.42%). Doğrulamada eksi.

## Durum: reddedildi
