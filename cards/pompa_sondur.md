# Pompa Söndür (aşırı yükselen coini shortlamak) — ARAŞTIRMA

**Durum:** REDDEDİLDİ (2026-11-04). Kasa kullanılmadı.

## Fikir (sade Türkçe)
3 günde %40-60 uçan ve funding'i (long'ların ödediği ücret) yüksek olan bir coin aşırı ısınmıştır; ertesi gün shortlayıp 1-5 gün tutarsak geri çekilmeyi kazanırız.

## Kurallar (önceden sabitlenen ana kural + küçük komşu ızgara)
- Evren: tüm USDT vadeli coinler (680, silinenler dahil), en az 30 günlük, günlük hacim ≥ 10M $.
- [pump] 3 günlük getiri ilk kez ≥ X (ana %50; %40/%60) | "Coin 3 günde %{r3} yükseldi."
- [crowded] son 3 günün ortalama günlük funding'i ≥ %0.06 (normalin 2 katı) (ana; filtresiz versiyon da) | "Long tarafı kalabalık."
- Ertesi gün açılışta short, stop %25 (%15/%35), H = 3 gün (1/5). En fazla 5 açık işlem. Masraf %0.20 + stop kayması %0.3 + funding.
- Kod: `research/shortside/b_pump_fade.py`.

## Sonuç
- Ana kural (X50, funding filtresi, H3, S25): geliştirme **−0.155R** (PF 0.63, DD 36%), doğrulama +0.06R (PF 1.14).
- 108 ayarın **hiçbiri geliştirmede artı değil**. Doğrulamada bazıları hafif artı ama bu yeterli değil.
- Neden: pompalanan coinler çoğu zaman yükselmeye devam ediyor (momentum), stoplar sık vuruluyor.

**Sonuç:** elendi.
