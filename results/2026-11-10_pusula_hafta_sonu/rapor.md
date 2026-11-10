# Kuyruk 33 — hafta sonu kırılımı yok — 2026-11-10 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** Cumartesi ve pazar gelen kırılımlara hiç girmesek daha iyi olur muyduk? Genel bilgi: hafta sonu piyasa ince, sahte kırılım daha kolay.
- **Cevap: hayır, red.** İki listede de ortalama R, toplam R ve net getiri düştü; eski 16'da düşüş (DD) %25 sınırını da aştı.
  - Eski 16: işlem 230 → **217**, ortalama +1.35R → **+1.25R**, toplam 311.3R → **271.2R**, net +%827 → **+%578**, DD %23.7 → **%27.4**.
  - Yeni 20: işlem 193 → **163**, ortalama +0.610R → **+0.442R**, toplam 117.7R → **72.1R**, net +%134 → **+%67**, DD %22.6 → %22.7.
- **Neden:**
  - Hafta sonu kırılımları kötü değil: temelde bunlar eski 16'da 63 işlem **+64.1R** (ort. +1.02R), yeni 20'de 62 işlem **+31.9R** (ort. +0.52R). Hafta içi kırılımlardan biraz zayıf (+1.48R / +0.66R), ama artı. Şart artı getirili işlemleri atıyor.
  - Kesilenler arasında büyük işlemler var: eski 16'da BTC 2023-10 +22.6R ve BTC 2024-01 +20.8R (en büyük 5'in ikisi), yeni 20'de THETA 2020-12 +24.1R.
  - Boşalan yerlere giren işlemler kaybı kapatmadı: eski 16'da 55 işlem +29.3R (kesilen +64.1R'nin yarısı), yeni 20'de 33 işlem **-14.8R**.
- Cumartesi ve pazar arasında tutarlı fark yok: eski 16'da pazar daha iyi (+40.5R / +23.6R), yeni 20'de cumartesi (+18.5R / +13.4R).
- 2025-26 iki listede kötüleşti: +12.4R → +1.4R / -15.5R → -23.5R.
- İleriye bakma yok (veri kesme testi 0 fark). Temel `PusulaV2NoBe` değişmedi, temel rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Bu, PusulaV2NoBe üzerinde ≈ 30. kural denemesi; giriş, çıkış ve yer değişikliklerinin hiçbiri tutmadı, dayanıklılık testi (kuyruk 32) düzlük gösterdi. Kuyrukta sadece madde 5 (güçlü / zayıf coin sepeti, önce kart) kaldı.

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeNoWeekend(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `weekday_candle`):
- Long girişine tek şart (`weekday`): sinyal (kırılım) 4h mumu **cumartesi veya pazar UTC'de açılmamış** olsun. Cumartesi 00:00 – pazar 20:00 arası 12 mum engelli; pazartesi 00:00 mumu serbest. Freqtrade'de `date` mumun açılış saati.
- Kırılım hâlâ "önceki 20 mumun tepesinin üstünde ilk 4h kapanış": hafta sonu gelen kırılım atlanır, pazartesiye ertelenmez.
- Aynı kalanlar: günlük puan ≥ +1, günlük kapanış EMA20 üstü, stop (1.5 ATR / 10 mum dibi, %8 sınırı), giriş bölgesi, çıkışlar (günlük EMA20, BTC-dönüş, sabit stop), %1 risk, en fazla 3 işlem, ısınma (400 mum), short yok.
- Eşik yok (takvim), tarama yok.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Birim testi
`tests/test_pusula.py`, `test_v2_no_be_no_weekend_skips_breakouts_on_saturday_and_sunday_utc_candles`:
- bayrak cuma 16:00 – pazartesi 04:00 arası her 4h mumda doğru: cumartesi 00:00 – pazar 20:00 yanlış, pazartesi 00:00 doğru;
- cuma 20:00 kırılımında iki sınıf da girer; cumartesi 00:00 ve pazar 20:00 kırılımında temel girer, yeni sınıf girmez ve sonraki mumlarda da girmez (erteleme yok); pazartesi 00:00 kırılımında ikisi de girer, stop sütunu aynı;
- stop, çıkış, büyüklük, kaldıraç, bölge fonksiyonları temelden miras (aynı nesne); short yok. 234 test geçti.

## Sonuç (2020-03 / 2020-04 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Net | Max DD | PF | Kazanma | Stopla biten | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +%827.3 | %23.75 | 2.06 | %32.2 | %41.7 | -14081 | +%931.5 |
| Eski 16 | **hafta sonu yok** | 217 | **+1.250** | **271.17** | **+%577.8** | **%27.41** | 1.85 | %30.4 | %47.0 | -11103 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +%134.2 | %22.61 | 1.53 | %23.3 | %53.9 | -3769 | +%194.7 |
| Yeni 20 | **hafta sonu yok** | 163 | **+0.442** | **72.07** | **+%66.6** | %22.68 | 1.39 | %20.9 | %54.6 | -2535 | +%194.7 |

- R'ler komisyon + kayma + funding dahil. Max DD Freqtrade'in hesap düşüşü. Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). İki sürüm de iki listede al-tutun altında.

**Karar: red.**
- Eski 16: **dört şartın hiçbiri tutmadı**. Düşüş aynı tarihte başlıyor (2024-03-20) ama 2024-12-18 yerine 2025-07-15'e kadar sürüyor: temelde düşüşü kapatan 2024 sonu / 2025 işlemlerinin bir kısmı hafta sonu kırılımıydı (2024: +10.0R → -0.6R, 2025: +15.5R → +5.1R).
- Yeni 20: ortalama R, toplam R ve net tutmadı; DD neredeyse aynı (%22.61 → %22.68, sınırın altında ama temelden de kötü).

## Engellenen temel girişler (temeldeki R'leri)
Sinyal mumu = girişin açıldığı mumdan bir önceki 4h mum (emir sinyal mumu kapanınca verilir).

| | Eski 16 | Yeni 20 |
|---|---|---|
| Temel işlemi, hafta içi sinyal | 167 (ort. **+1.480R**, toplam +247.1R, kazanma %32.9) | 131 (ort. **+0.655R**, toplam +85.8R, kazanma %22.1) |
| Temel işlemi, **engellenen** (hafta sonu sinyal) | 63 (%27.4; toplam **+64.12R**, ort. +1.018R, kazanma %30.2, stop %38.1) | 62 (%32.1; toplam **+31.94R**, ort. +0.515R, kazanma %25.8, stop %56.5) |
| — cumartesi | 26 işlem, **+23.60R** (ort. +0.91, kazanma %34.6) | 28 işlem, **+18.52R** (ort. +0.66, kazanma %32.1) |
| — cumartesi en büyükleri | TRX 2025-06 +10.3, ETH 2020-12 +9.5, XRP 2020-07 +6.9, TRX 2020-08 +4.8, XRP 2025-01 +2.6 | DASH 2024-11 +9.1, ALGO 2023-11 +6.8, ENJ 2024-02 +5.7, VET 2026-09 +5.3, ZEC 2021-10 +4.1 |
| — pazar | 37 işlem, **+40.52R** (ort. +1.10, kazanma %27.0) | 34 işlem, **+13.42R** (ort. +0.39, kazanma %20.6) |
| — pazar en büyükleri | **BTC 2023-10 +22.6**, **BTC 2024-01 +20.8**, BTC 2020-12 +6.9, BCH 2025-06 +5.8, ATOM 2020-07 +4.2 | **THETA 2020-12 +24.1**, NEO 2021-03 +9.7, XTZ 2021-03 +2.0, DASH 2026-05 +1.7, XTZ 2023-10 +0.5 |
| En büyük 2 hariç engellenenler | +20.67R | -1.81R |
| Yıllara göre engellenen (R) | 2020 +23.5, 2021 -4.9, 2022 -1.8, 2023 +16.2, 2024 +12.6, 2025 +18.4, 2026 +0.1 | 2020 +20.4, 2021 +11.4, 2022 -3.2, 2023 -1.3, 2024 +3.7, 2025 -8.5, 2026 +9.6 |

- Hafta sonu kırılımları hafta içinden biraz zayıf (ortalama farkı -0.46R / -0.14R), ama **artı**. Eski 16'da en büyük 2 hariç bile +20.7R; yani kesilen sadece birkaç şanslı işlem değil.
- Pazar 20:00 mumu (günlük mumla birlikte pazartesi 00:00'da kapanan) eski 16'da 13 işlem +16.1R, yeni 20'de 8 işlem -6.2R; tutarlı değil.
- Cumartesi / pazar sırası iki listede ters (eski 16'da pazar, yeni 20'de cumartesi daha iyi). Hafta sonunda tutarlı bir "kötü gün" yok.
- Teşhis notu (kural önerisi değil): temel işlemleri sinyal gününe göre ayırınca iki listede de en iyi gün cuma (+1.61 / +2.37R ort.), salı / perşembe zayıf; ama sıra iki listede aynı değil (pazartesi eski 16'da +3.44R, yeni 20'de +0.19R). Bu turun işlemlerinden gün seçmek veri madenciliği olur; yeni madde yazılmadı.

## Boşalan yerlerin etkisi (3 işlem sınırı)
| | Eski 16 | Yeni 20 |
|---|---|---|
| Ortak işlem (aynı coin, aynı açılış; R birebir aynı, fark 0.0000R) | 162 | 130 |
| Temelde olup yeni sürümde olmayan | 68: engellenen 63 (+64.12R) + hafta içi olduğu halde yer / coin meşgul yüzünden açılamayan 5 (+5.26R; ETH 2024-02 +8.9) | 63: engellenen 62 (+31.94R) + açılamayan 1 (-1.12R) |
| Yeni sürümde olup temelde olmayan (boşalan yerlere girenler) | 55 işlem, **+29.29R** (12 kazanan, ort. +0.53R) | 33 işlem, **-14.83R** (5 kazanan, ort. -0.45R) |
| Boşalan yerlere girenlerin en büyükleri | BTC 2020-12 +17.9, TRX 2025-06 +13.2, BNB 2024-02 +12.3, BTC 2023-10 +7.1, BTC 2020-07 +6.6 | NEAR 2023-12 +8.1, FIL 2023-10 +1.3, ZEC 2021-10 +1.0, ICP 2023-04 +0.8 |
| Boşalan yerlere girenler yıllara göre (R) | 2020 +17.7, 2021 -4.6, 2022 -1.9, 2023 +0.7, 2024 +10.9, 2025 +7.0, 2026 -0.5 | 2020 -2.7, 2021 -3.9, 2023 +4.0, 2024 -5.3, 2025 -3.6, 2026 -3.4 |
| Ortalama açık işlem | 1.09 → 0.99 | 0.66 → 0.55 |
| 3 yerin dolu olduğu zaman oranı | %25.2 → %21.8 | %13.2 → %8.8 |
| Toplam R farkı = − engellenen − açılamayan + boşalan yer | -40.09 = -64.12 - 5.26 + 29.29 | -45.65 = -31.94 + 1.12 - 14.83 |

- Eski 16'daki boşalan yer kazancının çoğu aynı trende saatler / günler sonra gelen hafta içi kırılımı: BTC 2020-12-15 04:00 (+17.9R; temelde BTC 2020-12-13 pazar kırılımı +6.9R), TRX 2025-06-30 (+13.2R; temelde 2025-06-28 cumartesi +10.3R), BTC 2023-10-16 08:00 (+7.1R; temelde aynı trendin pazar 20:00 kırılımı +22.6R). Bazen daha iyi, bazen çok daha kötü; BTC 2024-01-28 (+20.8R) trendine ise hiç girilemedi (sadece 2024-02-26 +5.5R). Yani şart trendi her zaman atlatmıyor, ama girişin yerini şansa bırakıyor.
- Yeni 20'de boşalan yerlere girenler net eksi: kesilen THETA 2020-12'nin (+24.1R) yerine gelen bir şey yok.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 hafta sonu yok | 20 temel | 20 hafta sonu yok |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +40.2 (40) | +31.5 (29) | **+8.4** (26) |
| 2021 | +164.3 (32) | +164.6 (28) | +41.7 (27) | +26.4 (22) |
| 2022 | -6.6 (7) | -6.7 (7) | -3.0 (6) | +0.2 (3) |
| 2023 | +86.7 (38) | +72.3 (32) | -1.9 (39) | +4.5 (34) |
| 2024 | +10.0 (57) | **-0.6** (55) | +64.9 (36) | +56.0 (28) |
| 2025 | +15.5 (31) | +5.1 (36) | -19.8 (41) | -14.8 (35) |
| 2026 | -3.1 (19) | -3.7 (19) | +4.3 (15) | -8.6 (15) |

- Geliştirme dönemi (2020-2024): 16'da +298.8R (180, ort. +1.66) → +269.8R (162, ort. +1.67); 20'de +133.2R (137, ort. +0.97) → +95.5R (113, ort. +0.85).
- **Doğrulama + kasa dönemi (2025-2026):** 16'da +12.4R (50, ort. +0.25) → **+1.4R** (55, ort. +0.03); 20'de -15.5R (56, ort. -0.28) → **-23.5R** (50, ort. -0.47). İki listede de kötü.
- Kayıp yıllara yayılmış; tek bir yıla bağlı değil. Yeni 20'de 2022-23'te biraz iyi (+9.1R), ama 2020'deki THETA tek başına bunu siliyor.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplam R'deki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R |
|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 |
| Eski 16 | hafta sonu yok | ETC 2021-03 +94.1 | **%35** | +0.820 | **+0.158** |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 |
| Yeni 20 | hafta sonu yok | ALGO 2024-11 +34.5 | **%48** | +0.232 | **-0.294** |

- **En büyük 5 temel işlemin şartı geçip geçmediği:** eski 16 ETC 2021-03, SOL 2023-10, BNB 2021-01 geçiyor; **BTC 2023-10 (+22.6R) ve BTC 2024-01 (+20.8R) geçmiyor** (ikisi de pazar sinyali). Yeni 20 ALGO 2024-11, FIL 2021-03, UNI 2024-02, VET 2020-06 geçiyor; **THETA 2020-12 (+24.1R) geçmiyor** (pazar).
- Yeni sürümün en büyük 5'i: eski 16 ETC 2021-03 +94.1, SOL 2023-10 +58.6, BNB 2021-01 +53.0, BTC 2020-12 +17.9 (boşalan yerden), TRX 2021-03 +14.1; yeni 20 ALGO 2024-11 +34.5, FIL 2021-03 +33.0, UNI 2024-02 +26.1, VET 2020-06 +14.4, FIL 2024-11 +10.6.
- Yoğunlaşma iki listede de arttı: yeni 20'de kârın yarısı tek işlem, en büyük 5 hariç ortalama -0.29R.

## İleriye bakma kontrolü
- Yeni şart sadece sinyal mumunun kendi açılış saatini kullanıyor (takvim); başka veri yok. Sinyal mumu emir verilmeden önce kapanmış oluyor.
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 150 rastgele 4h an + yeni sınıfın giriş sinyali anları (141-150) + 50 rastgele hafta sonu anı. Her anda her coin için tam veri ile o ana kadar kesilmiş 4h ve günlük veri (sadece o 4h mumun kapanışında kapanmış günlük mumlar, BTC dahil) karşılaştırıldı (giriş, çıkış, hafta içi bayrağı, `long_stop`, `long_plan_ok`).
  - Eski 16: 350 an, 5327 coin-an kontrolü, **0 fark**.
  - Yeni 20: 341 an, 6092 kontrol, **0 fark**.
- Yeni sürümün bütün işlemleri hafta içi sinyal mumundan; ortak işlemler (162 / 130) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor.

## Uyarılar
- Fikir önceden yazılmış genel piyasa bilgisiydi (hafta sonu ince piyasa), bir önceki turun işlemlerinden seçilmedi. Kuyruğun öngördüğü risk gerçekleşti: şart kırılımların %27 / %32'sini kesti, kesilenler artıydı ve aralarında en büyük işlemler vardı.
- Altı giriş filtresi (kuyruk 15 trend yaşı, 17 funding, 18 güçlü kapanış, 19 genişlik, 31 sıkışma, 33 hafta sonu) aynı tabloyu verdi. Bu sefer kesilenler küçük işlemler bile değildi; hafta sonu kırılımları da kâr getiriyor.
- Dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Ayarlar
- 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk, `--cache none`.
- Eski 16: `config/pairs_wide16.json`, `--timerange 20200101-20261001`. Yeni 20: `config/pairs_new20.json`, `--timerange 20200101-1790809200` (2026-09-30 23:00; veri artık Ekim'i de içeriyor, bu bitişle temel birebir aynı, bkz. `results/2026-11-09_pusula_saglamlik/rapor.md`).
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting -c config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeNoWeekend --timerange <aralık> --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none`. İki liste art arda çalıştırıldı. Sonuç dosyaları `user_data/backtest_results/backtest-result-2026-11-10_06-22-43` (eski 16) ve `backtest-result-2026-11-10_06-23-53` (yeni 20).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Analiz betikleri repo dışında (`/home/user/asgo_scratch/weekend/`: `analyse.py`, `trunc_check.py`).
