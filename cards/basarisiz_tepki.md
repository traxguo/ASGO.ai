# Başarısız Tepki (BTC düşüşteyken EMA20'den dönen coini shortlamak) — ARAŞTIRMA

**Durum:** REDDEDİLDİ (2026-11-04). Kasa kullanılmadı. Not: 10 günlük tutma bir ipucu olarak kaydedildi, ayrı test edilmedi.

## Fikir (sade Türkçe)
BTC günlük grafikte düşüş trendindeyken, bir coin günlük 20 ortalamasına (EMA20) kadar tepki verip altında kapatırsa satıcılar hâlâ güçlüdür; ertesi gün short.
Aynası (long): BTC yükselişteyken EMA20'ye düşüp üstünde kapatan coin alınır.

## Kurallar (önceden sabitlenen)
- [btc_down] BTC kapanış < EMA50 ve EMA50, 5 gün öncesinden düşük.
- Evren: o günün 30 günlük hacmine göre en büyük 30 coin (10/60 komşu), en az 90 günlük — tüm coinler (silinenler dahil).
- [below_trend] coin kapanış < EMA50, dünkü kapanış < EMA20.
- [rejected] bugün en yüksek ≥ EMA20 ve kapanış < EMA20 | "Fiyat EMA20'ye ({ema20}) kadar çıktı ama altında kapattı."
- Ertesi gün açılışta short; stop o günün tepesinin %1 üstü (en az %2 uzak); çıkış: kapanış EMA20 üstüne çıkarsa ya da H = 5 gün (3/10). En fazla 5 açık işlem.
- Kod: `research/shortside/c_failed_bounce.py`.

## Sonuç
| Ayar | Geliştirme | Doğrulama |
|---|---|---|
| SHORT top30 H5 (ana) | +0.02R, PF 1.03, DD **48%** | +0.06R, PF 1.12 |
| LONG top30 H5 (ayna) | +0.04R, PF 1.06, DD 69% | −0.04R, PF 0.94 |
| SHORT top30 H10 | +0.17R, PF 1.28, DD 46% | +0.18R, PF 1.30 |
| SHORT top60 H5 | −0.05R | +0.20R |

- Ana kural eşikleri geçmiyor (PF < 1.2, düşüş %48). Komşular tutarsız (top60 geliştirmede eksi).
- Long aynası doğrulamada eksi.
- 10 gün tutma iki dönemde de artı ama düşüş %46; sonuç gördükten sonra seçmek olacağı için kabul edilmedi.

**Sonuç:** elendi.
