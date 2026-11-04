# Fitil Avcısı + Derin Fitil — silinen coinler dahil kontrol (2026-11-04)

Kod: `research/scans/wick_catcher_pit.py` (kurallar `wick_catcher.py` / `wick_catcher_downtrend.py` ile aynı),
veri: `research/xsec/fetch_klines_15m.py` (data.binance.vision, 120 coin 15dk, silinenler dahil). Ham çıktılar: `runs.jsonl`.

## Yöntem
- **PIT evren:** her yıl başında o günün en çok işlem gören 36 USDT perp'i (`research/xsec/top36_yearly.json`, Dalga'nın 2026-11-03 kontrolüyle aynı liste; 119 coin birleşimi, LUNA, FTT, USTC, UXLINK gibi çöken/silinenler dahil). Coin sadece listede olduğu yıl işlem açabilir.
- **Eski evren:** `config/pairs_all36.json` (bugün hâlâ işlem gören 36 coin). Bu veriyle eski kart rakamları birebir tekrar çıktı (Fitil geliştirme 1.21/gün +%1.18, doğrulama 0.55/gün +%1.39, kasa +%95).
- Kurallar değişmedi: 15dk dolum (limitin %0.1 altı), BTC %3 koruması, stop yok, 3 saat sonra piyasa çıkışı, en fazla 5 açık, her biri kasa/5 (toplam 1x). Sadece long.
- Masraf: toplam gidiş-dönüş %0.13 (eski), **%0.20 (ana)**, %0.40 (x2). Funding: her 00/08/16 UTC geçişinde %0.01 (long öder varsayımı).
- Günlük mumlar 15dk veriden üretildi (UTC).
- Geliştirme 2020-03-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31. Kasa dönemine dokunulmadı.

## Sonuçlar (masraf %0.20 + funding)
| Strateji | Evren | Dönem | İşlem (gün) | Ort. % | Ortanca % | Kazanan | PF | Kasa | En büyük düşüş | En kötü gün | En iyi 5 gün hariç ort. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fitil | eski 36 | geliştirme | 2135 (1.21) | +1.11 | +1.18 | %62 | 1.88 | çok yüksek* | -13.1% | -10.3% | +0.99 |
| Fitil | **PIT** | geliştirme | 2234 (1.26) | **+1.01** | +0.97 | %61 | 1.85 | çok yüksek* | **-11.2%** | -7.5% | +0.92 |
| Fitil | eski 36 | doğrulama | 250 (0.55) | +1.32 | +1.20 | %63 | 2.15 | +88.6% | -6.5% | -6.5% | +0.43 |
| Fitil | **PIT** | doğrulama | 346 (0.76) | **+0.51** | +0.67 | %59 | 1.32 | **+38.2%** | **-10.1%** | -8.6% | +0.10 |
| Derin Fitil | eski 36 | geliştirme | 133 (0.08) | +2.68 | +2.76 | %71 | 2.75 | +97.7% | -5.7% | -5.7% | +1.07 |
| Derin Fitil | **PIT** | geliştirme | 228 (0.13) | **-0.70** | +1.77 | %65 | 0.82 | **-38.8%** | **-60.8%** | **-33.4%** | -1.37 |
| Derin Fitil | eski 36 | doğrulama | 37 (0.08) | +3.21 | +4.52 | %78 | 3.67 | +25.6% | -1.1% | -3.1% | +0.54 |
| Derin Fitil | **PIT** | doğrulama | 155 (0.34) | **+0.35** | +2.66 | %61 | 1.11 | **+5.6%** | **-23.6%** | -9.5% | -1.14 |
*2021 boğasında bileşik kasa abartılı büyüyor (binlerce %); işlem başı ortalama ve düşüş daha anlamlı.

Al-tut (BTC): geliştirme +%1001 (en büyük düşüş -%77), doğrulama -%27 (düşüş -%52).

### Masraf x2 (%0.40) — PIT
| Strateji | Dönem | Ort. % | Kasa | Düşüş |
|---|---|---|---|---|
| Fitil | geliştirme | +0.81 | çok yüksek | -12.4% |
| Fitil | doğrulama | +0.31 | +20.4% | -11.6% |
| Derin Fitil | geliştirme | -0.90 | -44.4% | -61.6% |
| Derin Fitil | doğrulama | +0.15 | -0.7% | -25.1% |

### Yıllara göre kasa (PIT, %0.20)
- Fitil: 2020 +68.5, 2021 +235, 2022 +9.8, 2023 +22.8, 2024 +116, 2025 +35.2, 2026 Q1 -0.3. Her yıl artı ya da başa baş.
- Derin Fitil: 2020 +6.1, 2021 +2.8, **2022 -42.8**, 2023 +9.1, 2024 -7.0, 2025 +28.8, **2026 Q1 -18.1**.

## Kayıp nereden geliyor
- **Derin Fitil, geliştirme:** LUNA çöküşü (10-12 Mayıs 2022) tek başına 15 işlem, toplam -454 puan (tek işlemde -%84). LUNA çıkarılınca kalan 213 işlem ortalama ≈ +%1.4. Kural "düşen coinde %8'lik panik fitilini al, stop yok" — ama gerçekten ölen bir coinde fitil geri dönmüyor, her saat yeniden alıyor.
- **Derin Fitil, doğrulama:** eski listede olmayan coinler (148 işlem) ortalama +%0.16; zarar UXLINK (hack, Eylül 2025, tek işlemde -%53), ACT, PIPPIN, AIA gibi memecoin çöküşlerinden.
- **Fitil, doğrulama:** eski 36'da olmayan coinler 302 işlem ortalama +%0.41 (eski 36 içindekiler +%1.13). Zayıflama gerçek ama yine artı; en kötü coin PIPPIN (37 işlem, -61 puan).

## Teşhis (canlı kural DEĞİL)
Derin Fitil'e "aynı coine 24 saat yeniden girme" eklenince (LUNA'yı gördükten sonra seçildi, yani bağımsız değil):
geliştirme +%74 (DD -11.6%), doğrulama +%23 (DD -18.1%), ama en iyi 5 gün çıkarılınca iki dönemde de eksi (-0.03 / -0.89), 2026 Q1 yine -15%. Kurtarmaya yetmiyor; sadece LUNA tipi zincirleme alımı keser.

## Sonuç
- **Fitil Avcısı sağlam:** silinen coinler dahil de geliştirmede neredeyse aynı (+%1.0/işlem), doğrulamada beklenti yarıdan fazla düşüyor (+%1.3 → +%0.5/işlem, kasa +%89 → +%38), masraf x2'de de artı. Demo botunun beklentisi "eskisinin yarısı kadar ama artı" olarak düşürülmeli.
- **Derin Fitil kırılgan:** eski testin parlak sonucu büyük ölçüde coin seçiminden geliyordu. Gerçekçi evrende geliştirme -%39 (DD -%61), doğrulama +%5.6 (DD -%24, masraf x2'de eksi). Stop olmadığı için bir LUNA/UXLINK olayı yılların kârını siliyor.
- Demo şu an sadece Bitget'teki 15 büyük coinde çalışıyor; bu coinlerde LUNA tipi risk düşük ama sıfır değil (stop yok). Kurallar 2026-11-30'a kadar donuk; karar yöneticide.
