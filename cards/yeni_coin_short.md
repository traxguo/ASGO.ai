# Yeni Coin Short (yeni listelenen coinleri kısa süre satmak) — ARAŞTIRMA

**Durum:** candidate (geliştirme + doğrulama geçti, 2026-11-04). Kasa (holdout) KULLANILMADI; ne zaman kullanılacağına denetleyici karar verir. Demo botlara eklenmedi.

## Hipotez
Binance'te yeni listelenen bir vadeli coin ilk günlerde genelde değer kaybeder: airdrop ve erken yatırımcılar satar, ilk heyecan söner. Coin listelendikten sonraki gün açığa satıp (short) bir hafta tutarsak bu düşüşten pay alırız. Bu fikir coin "seçmez", listelenen HER coine uygulanır; bu yüzden "bugün hâlâ yaşayan coinler" yanılgısı (survivorship) yoktur.

## Yön
short

## Giriş koşulları
- [new_listing] Teknik: coinin Binance USDT vadeli piyasadaki ilk günlük mumu kapandı (ilk gün = listeleme günü) | Açıklama: "{symbol} dün listelendi; yeni coinler ilk haftada genelde satış baskısı görür."
- Giriş: listelemeden sonraki 2. günün açılışında (00:00 UTC) piyasa emriyle short.

## İşlem yönetimi
- Stop: giriş fiyatının %40 üstü (yeni coinler çok oynak; dar stop hep vurulur).
- Çıkış: 7. günün kapanışında (H7), stop vurulmazsa.
- Risk: işlem başı sermayenin %1'i (stop %40 olduğu için pozisyon büyüklüğü sermayenin ~%2.5'i). En fazla 10 açık işlem.
- TP yok (zaman çıkışı).

## Zaman dilimi ve parametreler
| Parametre | Ana kural (önceden sabitlenen) | En dengeli komşu | Taranan |
|---|---|---|---|
| Giriş günü K | 1 (listelemeden sonraki gün) | 1 | 1 / 3 / 7 |
| Tutma H | 14 gün | 7 gün | 7 / 14 / 30 |
| Stop S | %40 | %40 | %25 / %40 / %60 |

## Test (2026-11-04)
- Evren: data.binance.vision'daki **tüm** USDT vadeli coinler (680, silinenler dahil). 2020-01-15 sonrası 674 listeleme (geliştirme 390, doğrulama 284).
- Masraf: işlem başı %0.20 + stopta ek %0.3 kayma + gerçek funding. 2x masraf testi yapıldı.
- Kod: `research/shortside/a_new_listing.py`, `a_checks.py`, `a_checks2.py`, motor `lib.py`, veri `fetch_all.py`.

| Kural | Dönem | İşlem | Ort. R | PF | İşlem başı net | Kasa getirisi (%1 risk) | Max DD |
|---|---|---|---|---|---|---|---|
| K1 H14 S40 (ana) | Geliştirme 2020-24 | 382 | +0.014 | 1.04 | +0.6% | +4% | 15% |
| K1 H14 S40 (ana) | Doğrulama 2025-26/03 | 261 | +0.112 | 1.31 | +4.5% | +32% | 12% |
| K1 H7 S40 | Geliştirme | 390 | +0.066 | 1.28 | +2.6% | +28% | 7.5% |
| K1 H7 S40 | Doğrulama | 283 | +0.089 | 1.29 | +3.6% | +27% | 15% |

- 27 komşu ayarın **27'si doğrulamada, 25'i geliştirmede artı**. 2x masrafta: doğrulamada 27/27, geliştirmede 22/27 artı.
- K1 H7 S40 **her yıl artı** (2020…2026/03). Ana kural (H14) 2021, 2023, 2024'te hafif eksi.
- Stopta %2 kayma: H7 hâlâ PF 1.22 / 1.22. %5 kayma: 1.13 / 1.12.
- Aynı günlerde eski büyük 50 coini shortlamak: geliştirmede −1.9%, doğrulamada +1.6% (yeni coin short +3.0% / +5.1%). Yani kâr "piyasa düştü"den değil, yeni coin etkisinden geliyor.
- Al-tut: BTC geliştirmede +1214% (DD 77%), doğrulamada −28% (DD 50%). Strateji çok daha düşük düşüşle çalışıyor, ama boğa döneminde BTC'nin getirisine yaklaşmıyor (risk %1 iken).
- Sıklık: doğrulamada ayda ~19 işlem, geliştirmede ~6.5 (Binance son yıllarda çok daha fazla coin listeliyor).

## Zayıf yanlar (gizlenmez)
- Kâr birkaç büyük düşüşten geliyor: en iyi %5 işlem çıkarılınca sonuç ~0. Yani tek tek işlemler yazı-tura gibi, kâr sepetten geliyor; çok sayıda işlem gerekir.
- Ana kural (H14) geliştirmede çok zayıf (PF 1.04). En iyi görünen H7'yi sonradan seçtik; bu küçük bir seçim yanlılığı.
- Yeni listelenen coinlerde funding shortların aleyhine (doğrulamada işlem başı −1.4%) — sonuçlara dahil.
- Günlük mumla test: gün içi sıkışmalarda (short squeeze) stop çok daha kötü dolabilir. %5 kaymaya kadar test edildi.
- Bitget demo yeni coinleri listelemeyebilir veya geç listeleyebilir; pozisyon limitleri düşük olabilir. Canlıda uygulanabilirlik ayrıca kontrol edilmeli.

## Sıradaki adım (önerilen)
1. Denetleyici onayıyla kasa (2026-04 → 2026-09) bir kez: K1 H7 S40, değiştirmeden.
2. Geçerse kâğıt takip: Binance yeni listeleme duyurularına göre, demo botlara dokunmadan.
