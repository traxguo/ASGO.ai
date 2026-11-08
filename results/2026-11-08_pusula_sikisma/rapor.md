# Kuyruk 31 — oynaklık sıkışması giriş şartı — 2026-11-08 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** Kırılıma sadece coin "sakinken" (son 30 güne göre oynaklığı düşükken, yani sıkışmadan çıkarken) girsek daha iyi olur muyduk? Genel bilgi: sıkışmadan çıkan kırılım daha uzun sürer.
- **Cevap: hayır, red.** İki listede de toplam R ve net getiri düştü, düşüş (DD) iki listede de %25 sınırını aştı.
  - Eski 16: işlem 230 → **215**, ortalama +1.35R → +1.42R (tuttu), toplam 311.3R → **305.5R**, net +%827 → **+%741**, DD %23.7 → **%30.8**.
  - Yeni 20: işlem 193 → **172**, ortalama +0.610R → **+0.608R**, toplam 117.7R → **104.5R**, net +%134 → **+%122**, DD %22.6 → **%28.9**.
- **Neden:**
  - Şart kırılımların üçte birini (%34 / %29) eliyor, ama elenen işlemler toplamda artıydı: eski 16'da 78 işlem +4.9R, yeni 20'de 47 işlem **+37.0R** (ALGO 2024-11 +34.5R, FIL 2024-11 +10.6R, DASH 2024-11 +9.1R). Dört önceki giriş filtresinde olduğu gibi yine öncü bir büyük işlem kesildi.
  - Boşalan yerlere giren işlemler eski 16'da -1.9R (67 işlem), yeni 20'de +23.9R (26 işlem; ama +36.8R'si iki işlem: MANA ve ENJ 2024-11, aynı yükselişte ALGO'nun yerine girdi).
  - DD'yi artıran, iki listede de düşüş dönemlerinde boşalan yerlere giren zayıf işlemler (eski 16'da 2024-25 düşüşünde 15 işlem -12.4R; yeni 20'de 2021-23'te 11 işlem -10.8R).
- Eski 16'nın en büyük 5 işleminin hepsi şartı geçiyor; yeni 20'de en büyüğü (ALGO 2024-11) geçmiyor. Yani şart büyük trendleri ayırt etmiyor.
- 2025-26: eski 16'da +12.4R → +4.4R (kötü), yeni 20'de -15.5R → -12.9R (biraz iyi).
- İleriye bakma yok (veri kesme testi 0 fark). Temel `PusulaV2NoBe` değişmedi, temel rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeSqueeze(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `atr_ratio_squeeze`):
- Long girişine tek şart (`atr_squeeze`): sinyal (kırılım) 4h mumunda **ATR(14) / kapanış ≤ önceki 180 mumun (30 gün) aynı oranının ortancası**. Sinyal mumu ortanca penceresinde değil (`shift(1)`); ortanca 180 mum dolmadan hesaplanmaz (şart yanlış, giriş yok).
- ATR, stop ve giriş bölgesinin zaten kullandığı aynı 4h ATR(14) sütunu (`atr`); yeniden hesaplanmadı, değişmedi.
- Kırılım hâlâ "önceki 20 mumun tepesinin üstünde ilk 4h kapanış": şartı geçmeyen kırılım atlanır, ertelenmez.
- Aynı kalanlar: günlük puan ≥ +1, günlük kapanış EMA20 üstü, stop (1.5 ATR / 10 mum dibi, %8 sınırı), giriş bölgesi, çıkışlar (günlük EMA20, BTC-dönüş, sabit stop), %1 risk, en fazla 3 işlem, short yok.
- Eşikler sabit (ATR 14, 180 mum, ortanca), tarama yok.
- Isınma: `startup_candle_count = 400` (değişmedi) ≥ 180 + 14 = 194. Yeni listelenen coinlerde de ek engel yok: günlük puanın 90 günlük getirisi (≈ 540 adet 4h mum) zaten daha uzun ısınma istiyor.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Birim testi
`tests/test_pusula.py`, `test_v2_no_be_squeeze_needs_atr_ratio_at_or_below_previous_180_candle_median`:
- bayrak, düz bir döngüyle hesaplanan "önceki 180 oranın ortancası" (mumun kendisi hariç) ile her mumda aynı; ilk 193 mumda (ATR ısınması + 180) hiç doğru değil;
- önceki 180 oran 0.01 iken sinyal oranı 0.01 (eşit) ve 0.0078 girer, 0.0108 girmez; temel her durumda girer;
- sonraki mumun çok yüksek ATR'si sinyal mumunun kararını değiştirmiyor; 180'den az geçmişte giriş yok; short yok;
- stop, çıkış, büyüklük, kaldıraç, bölge fonksiyonları temelden miras (aynı nesne). 233 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Stopla biten | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | %41.7 | -14077 | 11.3 | +%931.5 |
| Eski 16 | **sıkışma** | 215 | **+1.421** | **305.52** | +1.407 / 302.5 | **+%741.0** | **%30.80** | 1.89 | %28.4 | %47.0 | -13273 | 10.2 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | %54.4 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | **sıkışma** | 172 | **+0.608** | **104.53** | +0.604 / 103.8 | **+%121.9** | **%28.94** | 1.53 | %22.7 | %54.1 | -3766 | 7.6 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü. R'ler komisyon + kayma + funding dahil.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). İki sürüm de iki listede al-tutun altında.

**Karar: red.**
- Eski 16: ortalama R tuttu; **toplam R, net ve DD tutmadı**. Düşüş 2024-03-17 → 2025-01-19 (temelin en büyük düşüşüyle aynı dönem, %23.75 → %30.80). Bu pencerede kapanan yeni sürüm işlemleri 54 işlem -7.5R (-10021 USDT), temelde 55 işlem +2.7R (-1625 USDT).
- Yeni 20: **dört şartın hiçbiri tutmadı** (ortalama R çok az düştü, hesap-R ortalaması çok az arttı: +0.600 → +0.604). Düşüş 2021-04-25 → 2023-11-28 (temelin en büyüğü 2024-12 → 2026-09); bu pencerede kapanan yeni sürüm işlemleri -24.9R, temelde -21.2R.

## Şart ne kadar kırılım eliyor
| | Eski 16 | Yeni 20 |
|---|---|---|
| Temelin etkili sinyal mumu (giriş var, aynı mumda çıkış yok) | 1423 | 792 |
| — şartı geçen | 932 (%65.5) | 563 (%71.1) |
| — elenen | 491 (%34.5) | 229 (%28.9) |
| Temel işlemlerinde oran / ortanca ("göreli oynaklık") ortancası: geçen / elenen | 0.82 / 1.18 | 0.80 / 1.18 |

- Kırılımların üçte ikisi şartı geçiyor; şart kırılımların çoğunu değil, son 30 güne göre oynak anlarda gelenleri eliyor.

## Engellenen temel girişler (temeldeki R'leri)
| | Eski 16 | Yeni 20 |
|---|---|---|
| Temel işlemi, şartı geçen | 152 (ort. **+2.016R**, toplam +306.4R, kazanma %32.2, stop %41.4) | 146 (ort. **+0.553R**, toplam +80.7R, kazanma %24.0, stop %51.4) |
| Temel işlemi, **engellenen** | 78 (%34; 25 kazanan; toplam **+4.88R**, ort. +0.063R, kazanma %32.1, stop %42.3) | 47 (%24; 10 kazanan; toplam **+37.04R**, ort. **+0.788R**, kazanma %21.3, stop %63.8) |
| Engellenenlerin en büyükleri | ETH 2020-12 +9.5, XRP 2020-07 +6.9, ETH 2021-04 +6.4, BTC 2024-11 +5.0, ATOM 2020-07 +4.2 | **ALGO 2024-11 +34.5**, FIL 2024-11 +10.6, DASH 2024-11 +9.1, ENJ 2024-02 +5.7, VET 2026-09 +5.3 |
| En büyük 2 hariç engellenenler | -11.54R | -8.03R |
| Yıllara göre engellenen (R) | 2020 +13.8, 2021 +4.8, 2022 -3.1, 2023 -5.8, 2024 -1.2, 2025 -3.9, 2026 +0.3 | 2020 -5.2, 2022 -2.1, 2023 -5.1, **2024 +55.3**, 2025 -6.8, 2026 +0.9 |

- İki listede tutarlı değil: eski 16'da engellenenler zayıf (ort. +0.06R, geçenler +2.02R), yeni 20'de engellenenler geçenlerden **iyi** (+0.79R vs +0.55R).
- Yeni 20'deki engellenenlerin kazancı 2024-11 yükselişinin öncü coinlerinden (ALGO, FIL, DASH); kuyruk 15, 18, 19, 29'daki gibi şart yine öncü büyük kırılımları kesti. Büyük bir yükselişin başında oynaklık zaten artmaya başlamış oluyor.
- En büyük 2 hariç engellenenler iki listede eksi: şart küçük işlemleri doğru eliyor, ama birkaç büyük işlem kaçınca toplam kötüleşiyor.

## Boşalan yerlerin etkisi (3 işlem sınırı)
| | Eski 16 | Yeni 20 |
|---|---|---|
| Ortak işlem (aynı coin, aynı açılış; R birebir aynı, fark 0.0000R) | 148 | 146 |
| Temelde olup yeni sürümde olmayan | 82: engellenen 78 (+4.88R) + şartı geçtiği halde yer / coin meşgul yüzünden açılamayan 4 (-1.01R) | 47: hepsi engellenen (+37.04R) |
| Yeni sürümde olup temelde olmayan (boşalan yerlere girenler) | 67 işlem, **-1.88R** (13 kazanan, ort. -0.03R) | 26 işlem, **+23.86R** (4 kazanan, ort. +0.92R) |
| Boşalan yerlere girenlerin en büyükleri | XRP 2020-11 +17.4, XRP 2020-07 +7.6, ETH 2021-05 +7.6, BTC 2020-07 +6.6 | MANA 2024-11 +20.2, ENJ 2024-11 +16.6, NEO 2020-08 +4.5, ZEC 2020-07 +3.0 |
| Boşalan yerlere girenler yıllara göre (R) | 2020 +24.8, 2021 +0.6, 2023 -4.3, 2024 **-11.3**, 2025 -6.4, 2026 -5.2 | 2020 +4.7, 2023 **-10.8**, 2024 +33.2, 2025 -1.0, 2026 -2.2 |
| Ortalama açık işlem | 1.07 → 0.89 | 0.63 → 0.53 |
| Yer yok günleri (3 yer dolu) | %24.3 → %19.2 | %12.5 → %8.8 |
| Toplam R farkı = − engellenen − açılamayan + boşalan yer | -5.75 = -4.88 + 1.01 - 1.88 | -13.19 = -37.04 + 23.86 |

- Yeni 20'deki boşalan yer kazancının +36.8R'si iki işlem (MANA, ENJ 2024-11): ALGO'nun engellendiği aynı yükselişte bir gün sonra girdiler. Kuyruk 19'daki "yer kayması" tablosunun aynısı; şansa bağlı.
- DD'yi artıran da boşalan yerler: eski 16'da 2024-03 → 2025-01 düşüşünde boşalan yerlere giren 15 işlem -12.4R (engellenen 14 işlem +0.4R, aralarında BTC 2024-11 +5.0R, düşüşü kapatan işlemlerden biri); yeni 20'de 2021-04 → 2023-11'de boşalan yerlere giren 11 işlem -10.8R (engellenen 15 işlem -7.2R).

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 sıkışma | 20 temel | 20 sıkışma |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +55.4 (41) | +31.5 (29) | +41.5 (24) |
| 2021 | +164.3 (32) | +160.1 (32) | +41.7 (27) | +41.7 (27) |
| 2022 | -6.6 (7) | -3.5 (4) | -3.0 (6) | -0.9 (4) |
| 2023 | +86.7 (38) | +87.1 (35) | -1.9 (39) | -7.6 (37) |
| 2024 | +10.0 (57) | **+2.0** (52) | +64.9 (36) | **+42.8** (33) |
| 2025 | +15.5 (31) | +13.0 (31) | -19.8 (41) | -14.1 (35) |
| 2026 | -3.1 (19) | -8.6 (20) | +4.3 (15) | +1.2 (12) |

- Geliştirme dönemi (2020-2024): 16'da +298.8R (180, ort. +1.66) → +301.1R (164, ort. +1.84); 20'de +133.2R (137, ort. +0.97) → +117.4R (125, ort. +0.94).
- **Doğrulama + kasa dönemi (2025-2026):** 16'da +12.4R (50, ort. +0.25) → **+4.4R** (51, ort. +0.09); 20'de -15.5R (56, ort. -0.28) → **-12.9R** (47, ort. -0.27). Eski 16'da kötü (boşalan yerlere giren 18 işlem -11.6R), yeni 20'de toplam biraz iyi ama ortalama aynı (daha az işlem).
- 2024 iki listede de belirgin kötü (-8.0R / -22.1R): 2024-11 yükselişinde öncü kırılımlar şarta takıldı.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplam R'deki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | sıkışma | ETC 2021-03 +94.1 | %31 | +0.988 | +0.269 | +0.979 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | sıkışma | FIL 2021-03 +33.0 | %32 | +0.418 | **-0.092** | +0.417 |

- **En büyük 5 temel işlemin şartı geçip geçmediği:** eski 16 ETC 2021-03, SOL 2023-10, BNB 2021-01, BTC 2023-10, BTC 2024-01: **hepsi geçiyor** (yeni sürümde aynı işlemler, aynı R). Yeni 20 FIL 2021-03, UNI 2024-02, THETA 2020-12, VET 2020-06 geçiyor; **ALGO 2024-11 (+34.5R) geçmiyor** (göreli oynaklık 1.18).
- Yeni sürümün en büyük 5'i: yeni 20 FIL 2021-03 +33.0, UNI 2024-02 +26.1, THETA 2020-12 +24.1, MANA 2024-11 +20.2, ENJ 2024-11 +16.6 (son ikisi boşalan yerden).
- Eski 16'daki ortalama R artışı küçük işlemlerden: en büyük 5 hariç ortalama değişmiyor (+0.276 → +0.269). Yoğunlaşma iki listede de biraz arttı.

## Teşhis notu (kural önerisi değil)
Temel işlemleri giriş anındaki göreli oynaklığa (sinyal mumu ATR/kapanış ÷ önceki 180 mumun ortancası) göre ayırınca:

| Göreli oynaklık | Eski 16: işlem / toplam R / ort. | Yeni 20: işlem / toplam R / ort. |
|---|---|---|
| ≤ 0.8 | 63 / +270.7 / **+4.30** | 72 / +62.0 / **+0.86** |
| 0.8-1.0 | 89 / +35.7 / +0.40 | 74 / +18.7 / +0.25 |
| 1.0-1.2 | 41 / +7.3 / +0.18 | 27 / +28.2 / +1.05 |
| 1.2-1.5 | 23 / +6.1 / +0.27 | 14 / -4.6 / -0.33 |
| > 1.5 | 14 / -8.5 / -0.61 | 6 / +13.4 / +2.23 |

- En sakin grup (≤ 0.8) iki listede de en iyi ortalamada; ama eski 16'daki +270.7R'nin çoğu birkaç büyük işlem (ETC, SOL, BNB) ve yeni 20'de 1.0 üstündeki gruplar sıralı değil (1.0-1.2 ve > 1.5 iyi). Bu grupları bu turun işlemlerine bakarak seçmek veri madenciliği olur; daha sıkı bir eşik (ör. 0.8) yeni kuyruk maddesi olarak **önerilmedi**.

## İleriye bakma kontrolü
- Yeni şart sadece sinyal mumunu ve ondan önceki mumları kullanıyor: ATR(14) geçmiş mumlardan (Wilder), ortanca `shift(1)` ile bir mum kaydırılmış 180 mumluk pencereden. Sinyal mumu emir verilmeden önce kapanmış oluyor (emir bir sonraki mumda).
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 150 rastgele 4h an + 150 yeni sınıfın giriş sinyali anı (sinyal mumunun kapanışı). Her anda her coin için tam veri ile o anda kesilmiş 4h ve günlük veri (BTC dahil) karşılaştırıldı (giriş, çıkış, sıkışma bayrağı, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4742 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5727 kontrol, **0 fark**.
- Yeni sürümün bütün işlemleri (215 / 172) sinyal mumunda şartı geçiyor; ortak işlemler (148 / 146) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor.

## Uyarılar
- Fikir önceden yazılmış genel bir kırılım bilgisiydi (sıkışmadan çıkan kırılım), bir önceki turun işlemlerinden seçilmedi. Kuyruğun öngördüğü risk gerçekleşti: öncü coinlerin erken kırılımları (ALGO / FIL / DASH 2024-11) kesildi.
- Beş giriş filtresi (kuyruk 15 trend yaşı, 17 funding, 18 güçlü kapanış, 19 genişlik, 31 sıkışma) aynı tabloyu verdi: eledikleri işlemlerin çoğu küçük ve zayıf, ama aralarındaki birkaç büyük öncü işlem kaçınca ve boşalan yerlere rastgele işlemler girince toplam kötüleşiyor, DD artıyor.
- Dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeSqueeze --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none`. Sonuç dosyaları `user_data/backtest_results/backtest-result-2026-11-08_06-18-32` (eski 16) ve `backtest-result-2026-11-08_06-17-55` (yeni 20).
- Isınma: 400 mum (sınıf ayarı), iki sürümde aynı; 180 + 14 = 194 mum için yeterli.
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu (funding, çıkış türleri, coin tablosu, grafikler). Alt raporlardaki "Yön: long + short" satırı şablon metni; short işlem yok (tabloda 0).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Analiz betikleri repo dışında (`/home/user/asgo_scratch/squeeze/`).
