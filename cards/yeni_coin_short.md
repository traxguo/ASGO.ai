# Yeni Coin Short (yeni listelenen coinleri kısa süre satmak) — ARAŞTIRMA

**Durum:** KASADA KALDI (2026-11-04). Geliştirme + doğrulama geçti, ama denetleyicinin onayıyla bir kez yapılan kasa testinde (2026-04 → 2026-09) değerlendirilen 7 günlük kural eksi çıktı. Demo botlara eklenmedi. Kasa artık kullanıldı; bu kural ailesi için tekrar kasa testi yapılmaz.

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

## Kasa testi (tek sefer, 2026-11-04)
Geçme şartı önceden belirlendi: ortalama R > 0, PF > 1.1, DD < %20. Değerlendirilen kural: K1 H7 S40. Aynı çalıştırmada önceden sabitlenen H14 de raporlandı. Kod: `research/shortside/a_holdout.py`.

| Kural | İşlem | Ort. R | PF | İşlem başı net | Kasa getirisi | Max DD | 2x masraf | %5 stop kayması |
|---|---|---|---|---|---|---|---|---|
| **K1 H7 S40 (değerlendirilen)** | 163 | **−0.010** | **0.93** | −0.4% | −1.8% | 4.6% | −0.015R, PF 0.90 | −0.020R, PF 0.87 |
| K1 H14 S40 (önceden sabitlenen) | 103 | +0.058 | 1.35 | +2.3% | +6.0% | 4.6% | +0.053R, PF 1.31 | +0.039R, PF 1.21 |

- BTC al-tut aynı dönemde +24.6% (DD 28.7%).
- 7 günlük kural 6 ayın 4'ünde eksi. **Sonuç: değerlendirilen kural kasada geçemedi.**
- 14 günlük ana kural kasada geçti, ama geliştirmede çok zayıftı (PF 1.04). Sonradan "14 gün daha iyiymiş" diyerek ona geçmek, kasayı seçim için kullanmak olur; bu yüzden kabul edilmedi. Üç dönemin üçünde de artı olan tek sürüm H14, ancak geliştirmedeki zayıflık yüzünden bunu güçlü kanıt saymıyoruz.

## Sıradaki adım (önceki öneri, kasa öncesi)
1. Denetleyici onayıyla kasa (2026-04 → 2026-09) bir kez: K1 H7 S40, değiştirmeden.
2. Geçerse kâğıt takip: Binance yeni listeleme duyurularına göre, demo botlara dokunmadan.

## Bitget'te uygulanabilir mi? (2026-11-04, GitHub runner)
Kod: `research/shortside/bitget_listings.py` (workflow `bitget_listings.yml`), karşılaştırma `research/shortside/out_bitget_vs_binance_2026.csv`.
- Bitget API'si `launchTime` vermedi; listeleme günü olarak Bitget'teki ilk günlük mum alındı. Sadece bugün listede olan Bitget coinleri görülebiliyor (Bitget'ten silinenler yok). Bu canlı Bitget; demo listesi daha dar olabilir (daha önce demo 36 coinin sadece 15'ini listeliyordu).
- Bitget 2026'da ayda yeni USDT vadeli coin: Oca 16, Şub 9, Mar 23, Nis 28, May 49, Haz 91, Tem 55, Ağu 47, Eyl 49, Eki 59.
- Binance'in 2026'da listelediği 281 coinin 256'sı bugün Bitget'te var (25'i yok).
- Bitget, Binance'e göre ortanca **2 gün önce** listeliyor. 213 coin aynı gün ya da daha önce, 5'i 1 gün sonra, 20'si 2-7 gün sonra, 16'sı 7 günden fazla sonra listelendi.
- Kuralın giriş günü (Binance listelemesinden 1 gün sonra) itibarıyla Bitget'te işlem görebilen: 218 / 281 (~%78).
