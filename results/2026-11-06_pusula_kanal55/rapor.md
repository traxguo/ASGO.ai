# Kuyruk 29 — 55 mumluk 4h kırılım kanalı — 2026-11-06 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** Long tetiği "4h kapanış önceki **20** mumun tepesinin üstünde" yerine "önceki **55** mumun (≈ 9 gün) tepesinin üstünde" olsa daha iyi olur muyduk? Fikir: sadece daha büyük hareketleri seçmek.
- **Cevap: hayır, red.** İki listede de ortalama R, toplam R ve net getiri düştü; yeni 20'de düşüş (DD) de %25 sınırını aştı.
  - Eski 16: işlem 230 → **201**, ortalama +1.35R → **+1.01R**, toplam 311.3R → **203.6R**, net +%827 → **+%355**, DD %23.7 → %23.0.
  - Yeni 20: işlem 193 → **127**, ortalama +0.61R → **+0.55R**, toplam 117.7R → **69.8R**, net +%134 → **+%60**, DD %22.6 → **%27.9** (sınır %25).
- **Neden kötü:** 55 mumluk kırılım neredeyse her zaman 20 mumluk kırılımla **aynı mumda** geliyor (%94). Yani yeni kural çoğunlukla geç girmiyor, sadece 20 mumluk kırılımların bir kısmını atıyor: fiyat daha büyük bir aralığın içindeyken gelen kırılımları. Ama temelin büyük kazançlarından bazıları tam olarak bunlardı (SOL 2023-10 +58.6R, FIL 2021-03 +33.0R, THETA 2020-12 +24.1R, TRX 2021-03 +14.1R, VET 2020-06 +14.4R). 55 mumluk tepe birkaç mum sonra aşıldığında fiyat 10 mumluk dipten çok uzaklaşmış oluyor ve stop %8'i aşıp sinyal düşüyor (kuyruk 28'deki aynı mekanizma).
- Elenen kırılımlar "sahte" değildi: kaybedilen 142 / 120 işlemin ortalaması +1.43R / +0.69R, yerine gelen 113 / 54 yeni işlemin ortalaması +0.84R / +0.65R. Stopla biten işlem oranı da azalmadı, arttı (%41.7 → %51.2 / %54.4 → %61.4).
- Doğrulama + kasa dönemi (2025-26): eski 16'da +12.4R → +1.0R (kötü), yeni 20'de -15.5R → -6.2R (daha az kayıp, ama daha az işlemden).
- Temel `PusulaV2NoBe` değişmedi, baseline rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeChannel55(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Long kırılım şartı (`breakout_up`): 4h kapanış, önceki **55** mumun en yüksek seviyesinin (o mum hariç) üstünde ve bir önceki mumda böyle bir kapanış yoktu (ilk kapanış). Temelde 20 mum.
- Aynı kalanlar: günlük puan ≥ +1, günlük kapanış EMA20 üstü, giriş bölgesi, stop (1.5 ATR / 10 mum dibi, hangisi genişse), stop > %8 ise sinyal yok, %1 risk, en fazla 3 işlem, çıkışlar (günlük EMA20, BTC-dönüş, sabit stop), emir 3 mum geçerli, short yok.
- Eşik sabit (55), tarama yok. Madde 28'den ayrı (günlük tetik yok).
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Nasıl kodlandı (20 başka bir yere bağlı mı?)
- Sınıf sadece `channel = 55` ayarlıyor; başka bir fonksiyonu değiştirmiyor. Birim testi bunu kontrol ediyor.
- Kodda 20 mumluk kanal (`CHANNEL`) sadece `dc_upper` (long tetik) ve `dc_lower` (short tetik) sütunlarını besliyor. İkisi de 55 oldu; short kapalı olduğu için `dc_lower` sonucu etkilemiyor.
- **Stop bağlı değil:** stop = 1.5 ATR(14) ile **10** mumluk dip (`swing_lookback = 10`) arasından geniş olanı. Değişmedi.
- **Giriş bölgesi bağlı değil:** sinyal mumunun kapanışı ve ATR'den hesaplanıyor. Değişmedi.
- **Çıkış bağlı değil:** günlük EMA20 çıkışındaki 20, günlük ortalamanın uzunluğu (`EMA_FAST`), kanal değil. Değişmedi.
- Yorum modülü (`commentary`) tetik seviyesini stratejinin kendi `dc_upper` sütunundan okuyor; bu sınıfla kullanılsaydı 55 mumluk seviyeyi yazardı. `research/forward/pusula_paper.py` dondurulmuş sürüm için kendi 20 mumluk kanalını hesaplıyor; bu testte kullanılmadı.
- Isınma: `startup_candle_count` = 400 mum (55'ten fazla; günlük puan zaten 400'e ihtiyaç duyuyor), değişmedi. Bu yüzden temel ve yeni sürüm aynı tarihten başlıyor.
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_channel55_breaks_out_above_55_candle_high_with_same_stop_inputs`. Kontrol edilenler:
  - `dc_upper` = önceki 55 mumun tepesi; temelde 20;
  - stop, giriş bölgesi, 10 mumluk dip, ATR ve `plan_ok` her mumda temelle birebir aynı;
  - dip sonrası toparlanmada temel 20 mumluk tepeyi geçince, yeni sürüm ancak eski 55 mumluk zirve aşılınca sinyal veriyor;
  - veri sinyal mumunda kesilince aynı sinyal; short yok; diğer bütün fonksiyonlar temelden miras.
  231 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.3 | +%931.5 |
| Eski 16 | **kanal 55** | 201 | **+1.013** | **203.61** | +1.003 / 201.7 | **+%355.3** | %23.03 | 1.78 | %24.4 | -7547 | 10.7 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | **kanal 55** | 127 | **+0.550** | **69.81** | +0.538 / 68.3 | **+%60.5** | **%27.87** | 1.59 | %22.0 | -1271 | 8.3 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). İki sürüm de al-tutun altında; yeni sürüm çok daha altında.

**Karar: red.**
- Eski 16: ortalama R (+1.353 → +1.013), toplam R (311.26 → 203.61) ve net (+%827.3 → +%355.3) **tutmadı**. DD (%23.03) tamam.
- Yeni 20: ortalama R (+0.610 → +0.550), toplam R (117.72 → 69.81), net (+%134.2 → +%60.5) ve DD (**%27.87** > %25) **hiçbiri tutmadı**.
- Yeni 20'deki düşüş çok uzun: 2020-06'daki zirveden 2024-01'e kadar (3.5 yıl) hesap zirvenin altında kaldı. Temelde en büyük düşüş 2024-12 → 2026-09 arasıydı.

## Sinyaller nereye gitti
İlk kapanış kırılımları (puan ≥ +1 ve günlük EMA20 üstü şartlarıyla, 2020-01 → 2026-09):

| | Eski 16 temel | Eski 16 kanal 55 | Yeni 20 temel | Yeni 20 kanal 55 |
|---|---|---|---|---|
| İlk kapanış kırılımı | 3663 | 2723 | 3297 | 2416 |
| Stop > %8 (sinyal yok) | 2042 (%55.7) | 1683 (**%61.8**) | 2442 (%74.1) | 1927 (**%79.8**) |
| Stop ortancası | %8.7 | %9.5 | %11.1 | %12.1 |
| Sinyal | 1621 | 1040 | 855 | 489 |
| — işlem açıldı | 225 | 198 | 192 | 126 |
| — 3 yer doluydu | 736 | 401 | 432 | 242 |
| — coinde zaten işlem açıktı | 446 | 278 | 147 | 77 |
| — emir dolmadı / iptal / aynı mumda çıkış | 214 | 163 | 84 | 44 |

- ("İşlem açıldı" sinyal sayımından; backtest 230 / 201 / 193 / 127 işlem. Fark 2020-03 başlangıcından önceki birkaç sinyal ve aynı mumdaki eşleşmeler.)
- 55 mumluk kırılımlar daha geniş stoplu: oran %55.7 → %61.8 ve %74.1 → %79.8. Kırılım daha yüksek bir seviyede olduğu için fiyat 10 mumluk dipten daha uzakta.
- 3 yer daha seyrek doluyor (fikrin beklediği): yer yok günleri %24.3 → %17.3 / %12.5 → %7.8; ortalama açık işlem 1.07 → 0.88 / 0.63 → 0.43. Ama boşalan yer daha iyi işlemle dolmadı.

## Giriş zamanı: 55 mumluk kırılım 20 mumluktan ne kadar sonra geliyor?
Her 55 mumluk ilk kapanış, 20 mumluk tepenin üstünde kapanan bir mum serisinin içinde (55 mumluk tepe hep 20 mumluktan yüksek ya da eşit). Bu serinin ilk mumuna (temelin tetiği) göre:

| | Eski 16 | Yeni 20 |
|---|---|---|
| 55 mumluk ilk kapanış | 2723 | 2416 |
| Temelin 20 mumluk ilk kapanışıyla **aynı mumda** | 2573 (%94.5) | 2278 (%94.3) |
| 1-24 saat sonra | 150 | 138 |
| 24 saatten sonra | 0 | 0 |

- Yani yeni kural neredeyse hiç "aynı kırılıma daha geç giren" bir kural değil. Asıl etkisi **elemek**: temelin 20 mumluk ilk kapanışlarının yaklaşık %30'u (3663'ün 1090'ı / 3297'nin 1019'u) fiyat önceki 55 mumun tepesinin altındayken geliyor ve yeni sürümde sinyal değil.
- Bu elenen kırılımlardan sonra fiyat yükselmeye devam edip 55 mumluk tepeyi de geçerse, 55 mumluk kırılım ya aynı serinin içinde 1-6 mum sonra (yukarıdaki 150 / 138) ya da fiyat kısa bir geri çekilmeden sonra yeni bir 20 mumluk seri başlatınca geliyor. İki durumda da fiyat daha yüksek ve stop çoğunlukla %8'i aşıyor.

### Aynı trendde: giriş zamanı ve fiyatı (kuyruğun istediği rapor)
Aynı coinde, açık kaldığı süreler çakışan bir temel işlemi ile bir yeni işlem "aynı trend" sayıldı (her yeni işlem için en yakın açılışlı temel işlemi).

| | Eski 16 | Yeni 20 |
|---|---|---|
| Aynı trende giren çift | 142 | 87 |
| Aynı saat / yeni sürüm daha geç / daha erken | 87 / 49 / 6 | 72 / 13 / 2 |
| **Geç girenler (20 mumluk kırılım önce geldi)** | | |
| — gecikme ortancası | 52 saat | 44 saat |
| — giriş fiyatı farkı (yeni / temel - 1), ortanca | **+%3.35** | **+%3.63** |
| — bu çiftlerin R'si: temel → yeni | +171.2 → **+92.7** | +18.6 → **+3.6** |
| Erken girenlerin R'si: temel → yeni | -4.0 → +15.6 | +1.4 → +2.6 |
| Bütün çiftlerin stop mesafesi: temel → yeni | %5.37 → %5.47 | %6.32 → %6.47 |

- Geç giriş, temelin önceki bir 20 mumluk kırılımda zaten girdiği trendlerde oluyor; yeni sürüm o trende ancak sonraki, daha yüksek bir kırılımda (55 mumluk tepe aşılınca) katılıyor.
- Geç ve pahalı giriş her zaman R kaybettirdi. Örnekler: BTC 2023-10 +22.6 → +4.2R (7 gün sonra, %13 pahalı), ETC 2021-03 +94.1 → +90.3R (28 saat, %3.6), ETH 2020-12 +9.5 → +4.9R (7 gün, %19), IOTA 2020-07 +7.9 → -1.1R (64 saat, %11). Tek istisna BTC 2020-12 +6.9 → +17.9R.

## Temelle ortaklık (işlem eşleştirme)
Birebir eşleşme (coin + açılış saati):

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Ortak işlemler (R birebir aynı) | 88 | 0.00 fark | 73 | 0.00 fark |
| Yeni girişler (temelde olmayan) | 113 | **+94.84** (ort. +0.839, kazanma %19.5) | 54 | **+35.26** (ort. +0.653, kazanma %25.9) |
| Kaybedilen girişler (temelin aldığı, yeninin almadığı) | 142 | **+202.50** (ort. +1.426, kazanma %33.1) | 120 | **+83.18** (ort. +0.693, kazanma %25.8) |
| **Toplam fark** | 230 → 201 | **-107.66** | 193 → 127 | **-47.92** |

- **Temel işlemi olmayan trendler:** yeni sürümün 57 / 39 işlemi temelin hiç girmediği trendlerde: **-12.4R** / +25.2R (yeni 20'de en iyileri NEAR 2023-12 +16.4, NEAR 2024-02 +14.4; eski 16'da XRP 2020-11 +12.3, LINK 2023-10 +9.3).
- Temelin 86 / 106 işlemi yeni sürümün hiç girmediği trendlerde: +36.0 / +62.2R. Bunların 78 / 102'sinde 55 mumluk sinyal yoktu (+42.9 / +44.0R), 8 / 4'ünde yeni sürümün yerleri doluydu.

### En büyük kaybedilen işlemler neden kaçtı
| İşlem (temel) | Temel R | Temelin sinyal mumunda fiyat, 55 mumluk tepeye göre | 55 mumluk ilk kapanış geldiğinde stop |
|---|---|---|---|
| SOL 2023-10 (eski 16) | +58.6 | %5.8 altında | 3.5 gün sonra, stop %8.2 → sinyal yok |
| FIL 2021-03 (yeni 20) | +33.0 | %10.4 altında | 2 mum sonra, stop %15.0 → sinyal yok |
| THETA 2020-12 (yeni 20) | +24.1 | %8.9 altında | 3 gün sonra, stop %12.7 → sinyal yok |
| VET 2020-06 (yeni 20) | +14.4 | %3.3 altında | 3 mum sonra, stop %11.1 → sinyal yok |
| TRX 2021-03 (eski 16) | +14.1 | %0.5 altında | 1 mum sonra, stop %9.9 → sinyal yok |

- Hepsinde trend gerçekten büyüdü ve 55 mumluk tepe kısa süre sonra aşıldı; ama o anda stop %8'i geçtiği için yeni sürüm hiç girmedi. Daha uzun kanal büyük hareketi "seçmedi", sadece girişi stop sınırının dışına itti.

## Stopla biten işlemler ve kazananlar
| | Eski 16 temel | Eski 16 kanal 55 | Yeni 20 temel | Yeni 20 kanal 55 |
|---|---|---|---|---|
| Stopla biten oran | %41.7 | **%51.2** | %54.4 | **%61.4** |
| Kazanma oranı | %32.2 | %24.4 | %23.3 | %22.0 |
| Kazananların ortalama R'si | +6.00 | +6.95 | +5.59 | +5.72 |
| Kazananların ortalama süresi (gün) | 24.9 | 27.8 | 22.0 | 21.8 |

- Uzun kanal sahte kırılımı azaltmadı; stop oranı arttı. Kazananlar biraz daha büyük ama sayıları çok daha az.
- Kuyruğun öngördüğü "kazananlar kısalır" riski görülmedi (süre aynı ya da uzun); asıl sorun kazanan sayısı.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 kanal 55 | 20 temel | 20 kanal 55 |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +35.1 (37) | +31.5 (29) | **-2.8** (16) |
| 2021 | +164.3 (32) | +147.1 (25) | +41.7 (27) | **-9.0** (18) |
| 2022 | -6.6 (7) | -5.6 (6) | -3.0 (6) | -2.0 (5) |
| 2023 | +86.7 (38) | **+4.9** (41) | -1.9 (39) | +4.3 (30) |
| 2024 | +10.0 (57) | +21.0 (47) | +64.9 (36) | **+85.5** (23) |
| 2025 | +15.5 (31) | +3.5 (29) | -19.8 (41) | -14.6 (25) |
| 2026 | -3.1 (19) | -2.5 (16) | +4.3 (15) | +8.3 (10) |

- Geliştirme dönemi (2020-2024): 16'da +298.8R (180) → +202.5R (156); 20'de +133.2R (137) → +76.0R (92).
- **Doğrulama + kasa dönemi (2025-2026):** 16'da +12.4R (50 işlem, ort. +0.25) → **+1.0R** (45, ort. +0.02); 20'de -15.5R (56, ort. -0.28) → **-6.2R** (35, ort. -0.18). Yeni 20'de kayıp azaldı, eski 16'da kazanç neredeyse sıfırlandı. İki liste ters yönde; tutarlı bir iyileşme yok.
- Eski 16'da 2023 çöktü (+86.7 → +4.9R): SOL 2023-10 +58.6R ve BTC 2023-10'un erken girişi (+22.6 → +4.2R) kayıp. Yeni 20'de 2020-21 eksiye döndü (FIL, THETA, VET kayıp); tek iyi yıl 2024 (+85.5R).

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplamdaki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | kanal 55 | ETC 2021-03 +90.3 | **%44** | +0.567 | +0.045 | +0.561 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | kanal 55 | ALGO 2024-11 +34.5 | **%49** | +0.280 | **-0.264** | +0.273 |

- Yeni sürümün en büyük 5'i: eski 16 ETC 2021-03 +90.3, BNB 2021-01 +53.0, BTC 2024-01 +20.8, BTC 2020-12 +17.9, BTC 2020-10 +12.8; yeni 20 ALGO 2024-11 +34.5, UNI 2024-02 +26.1, NEAR 2023-12 +16.4, NEAR 2024-02 +14.4, FIL 2024-11 +10.6.
- Yeni sürüm tek işleme daha bağımlı (%44 / %49). Yeni 20'de en büyük 5 hariç ortalama -0.26R: geri kalan işlemler para kaybettiriyor.

## İleriye bakma kontrolü
- Yeni kural temelle aynı yapıda: 55 mumluk tepe bir mum kaydırılmış (sinyal mumunu içermiyor), sadece kapanmış 4h mumlar.
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 150 rastgele 4h an + 150 "sinyal" anı (sinyal mumunun kapanışı). Her anda her coin için tam veri ile o anda kesilmiş 4h ve günlük veri karşılaştırıldı (giriş, çıkış, `dc_upper`, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4728 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5686 kontrol, **0 fark**.
- Ortak işlemler (88 / 73) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor (fark 0.0000R).

## Uyarılar
- Fikir önceden yazılmış genel bir kuraldı (Turtle "System 2" uzunluğu), bir önceki turun işlemlerinden seçilmedi; veri madenciliği riski düşük. Sonuç yine de kötü.
- Üç tur üst üste (27, 28, 29) kırılım tetiğiyle oynandı: tetiği sıklaştırmak (27) neredeyse hiçbir şey değiştirmedi, yavaşlatmak (28) ve büyütmek (29) iki listede de kötü. 20 mumluk ilk kapanış tetiği iki yönde de yerel bir iyi nokta gibi görünüyor; kuyruğa tetikle ilgili yeni madde eklenmedi.
- Dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeChannel55 --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/ch55_<liste>`.
- Isınma: 400 mum (sınıf ayarı), iki sürümde aynı; 55 mumluk kanal için yeterli.
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu (funding, çıkış türleri, coin tablosu, grafikler).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Analiz betikleri repo dışında (`/home/user/asgo_scratch/ch55/`).
