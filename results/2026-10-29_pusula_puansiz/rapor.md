# Kuyruk 20 — çıkarma: günlük puan şartı — 2026-10-29 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: long girişinden "coinin günlük trend puanı en az +1" şartını tamamen kaldırsak, sadece 4 saatlik kırılım + günlük kapanış 20 günlük ortalamanın üstünde yeter mi? Fikir: puan gecikmeli bir teyit, öncü coinlerin erken kırılımlarını kaçırıyor olabilir.
- Cevap: **iki listede tutarlı bir iyileşme yok.** Eski 16'da sonuç belirgin iyi (+1.35R → +1.53R, net +%827 → +%1696), ama en büyük düşüş %23.7 → **%25.5** ile %25 sınırını aştı. Yeni 20'de toplam ve net arttı (117.7R → 139.8R, +%134 → +%192), ama işlem başına ortalama **düştü** (+0.61R → +0.57R).
- Puan şartı olmadan gelen yeni girişlerin kârı yine birkaç büyük işlemde: eski 16'da XLM 2024-11 **+43.1R** ve BCH 2023-06 +18.4R (geri kalan 62 işlem toplam +7.0R), yeni 20'de HBAR 2024-11 **+50.3R** (geri kalan 119 işlem +36.4R). Yeni 20'de bunlara yer açmak için ALGO 2024-11 (+34.5R) ve UNI 2024-02 (+26.1R) kaçtı.
- Korkulan 2022 ayı yılı kötüleşmedi: o yıl puanı düşük kırılımların ≈ %90'ı zaten "BTC puanı ≤ -1" çıkış kuralı yüzünden girişe dönüşmüyor.
- **Karar: red** (eski 16'da DD %25.5 > %25; yeni 20'de ortalama R kötü). Temel `PusulaV2NoBe` değişmedi.

## Kural (testten önce yazıldı)
`PusulaV2NoBeNoScore(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Long şartlarından **sadece** `regime_up` (coinin son kapanmış günlük puanı ≥ +1) silindi. Kalan şartlar: 4h kırılım (önceki 20 mumun tepesinin üstünde ilk kapanış), son kapanmış günlük kapanış günlük EMA20 üstünde, ortak plan kontrolü (stop mesafesi sınırda).
- Stop (giriş ortası − 1.5 ATR ile 10 mum dibinin geniş olanı, sabit), %1 risk, en fazla 3 işlem, sadece long: aynı. Eşik yok, tarama yok.
- **Puanın çıkışlarda kullanımı (kontrol edildi, değişmedi):**
  - EMA20 çıkışı puan kullanmıyor.
  - BTC-dönüş çıkışı **BTC'nin** günlük puanını kullanıyor (`mkt_score_1d ≤ -1`), coinin kendi puanını değil. Aynen kaldı. Freqtrade aynı mumda çıkış sinyali varsa giriş sinyalini yok sayıyor (`backtesting.py`: `enter_long and not exit_long`); yani BTC puanı ≤ -1 iken long girişi temelde olduğu gibi yine engelli. Bu bir giriş şartı gibi çalışıyor ama çıkış kuralının yan etkisi, ona dokunulmadı.
  - Sonuç: sadece giriş şartı değişti. Ortak işlemlerin R'si iki sürümde birebir aynı (16: 173 işlem 300.44R, 20: 120 işlem 57.38R).
- Yan etki (ayrı bir kural değil): puan için EMA50 + 90 günlük geçmiş gerekiyordu, EMA20 için 20 gün yetiyor. Bu yüzden yeni listelenen bir coin daha erken işlem alabiliyor. Bu tür (puanı henüz hesaplanamayan) giriş: 16'da 2 işlem (-0.53R), 20'de 4 işlem (-2.45R).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → **kabul**; aksi halde **red**.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | puansız | 255 | +1.53R | 388.94 | +1.51 / 385.7 | +%1695.5 | **%25.5** | 2.45 | %33.7 | -16499 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | puansız | 246 | **+0.57R** | 139.82 | +0.57 / 140.4 | +%192.5 | %23.8 | 1.53 | %24.0 | -5531 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü (16: %25.46).
- Al-tut: eşit ağırlık, aynı dönem.
- En büyük düşüş dönemi: eski 16'da iki sürümde de 2024-03 → 2024-12 (aynı dönem, yenide daha derin); yeni 20'de temel 2024-12 → 2026-09, yeni 2024-12 → 2025-10.

**Karar: red.** Eski 16'da ortalama R, toplam R ve net iyi, ama DD %25.46 > %25. Yeni 20'de toplam R, net iyi ve DD %23.8 ≤ %25, ama ortalama R +0.61 → +0.57 kötü. Kural "iki listede de dördü birden" istiyor.

## Yeni girişler (temelin alamadığı, sinyal anında puan < +1)
Sinyal mumu her işlem için yeniden bulundu (dolumdan önce kapanmış, en fazla 3 mum geride, ilk kırılım + EMA20 üstü mum); puan o mumun gördüğü son kapanmış günlük mumdan.

| Liste | Yeni giriş | Kazanan | Toplam R | Ort. R | Hesap-R | Funding (USDT) | En büyük 2 hariç |
|---|---|---|---|---|---|---|---|
| Eski 16 | 64 | 21 | **+68.50** | +1.07 | +67.8 | -2554 | 62 işlem +6.99R (ort. +0.11) |
| Yeni 20 | 120 | 29 | **+86.74** | +0.72 | +88.4 | -2570 | 118 işlem +24.01R (ort. +0.20) |

- Yıllara göre (işlem, R): eski 16'da 2020 4 / -2.0, 2021 7 / +9.2, **2022 3 / -2.1**, 2023 10 / +24.1, 2024 24 / +32.5, 2025 9 / +8.6, 2026 7 / -1.9. Yeni 20'de 2020 13 / +6.1, 2021 9 / +15.7, **2022 5 / -1.6**, 2023 36 / **-9.9**, 2024 30 / **+79.0**, 2025 21 / -3.0, 2026 6 / +0.6.
- En büyükler: eski 16'da XLM 2024-11-07 **+43.1** (puan -1), BCH 2023-06-21 +18.4 (-3), XLM 2025-07-07 +10.0, ATOM 2021-08-06 +8.1, LINK 2023-07-10 +5.9. Yeni 20'de HBAR 2024-11-08 **+50.3** (puan -3), VET 2024-02-08 +12.4, DASH 2024-11-07 +12.1, ALGO 2024-02-08 +7.6, DASH 2025-10-01 +7.3.
- Puana göre (yeni sürümün tüm işlemleri, sinyal anı): eski 16'da +3: 151 işlem +1.51R, +1: 40 işlem +2.30R, -1: 38 işlem +1.19R, -3: 24 işlem +0.99R. Yeni 20'de +3: 86 işlem +0.91R, +1: 40 işlem **-0.62R**, -1: 62 işlem +0.42R, -3: 54 işlem +1.17R. Puan grupları arasında iki listede tutarlı bir sıra yok; puan kırılımın kalitesini ayırmıyor gibi, ama düşük puanlı girişlerin kârı da birkaç işleme bağlı.
- Ayrıca puanı ≥ +1 olan ama temelde yer olmadığı için girilemeyen 18 (16) / 6 (20) yer kayması girişi oldu: +20.0R (BNB 2024-02 +12.3, BCH 2024-02 +12.0) / -4.3R.

## Yerini kaybeden temel işlemler
| Liste | Kaybolan temel işlem | Kazanan | Toplam R | Ort. R | En büyük 2 | En büyük 2 hariç |
|---|---|---|---|---|---|---|
| Eski 16 | 57 | 15 | +10.82 | +0.19 | BTC 2024-01-28 +20.8, ETH 2024-02-07 +8.9 | 55 işlem **-18.92R** |
| Yeni 20 | 73 | 16 | **+60.34** | +0.83 | ALGO 2024-11-08 **+34.5**, UNI 2024-02-09 **+26.1** | 71 işlem -0.21R |

- Bunlar 3 yer dolu olduğu (ya da aynı coinde yeni sürümün başka bir işlemi açık olduğu) için alınamayan temel işlemler; temel sinyallerin hepsi yeni sürümde de sinyal.
- Net etki: eski 16'da +68.5 + 20.0 − 10.8 = **+77.7R**; yeni 20'de +86.7 − 4.3 − 60.3 = **+22.1R**.
- Yeni 20'de 2024-11: puansızda DASH 2024-11-07 (puan -3, +12.1) bir gün önce, HBAR 2024-11-08 (puan -3, +50.3) AXS ile aynı mumda girdi ve 3 yer doldu; temelin aynı gün aldığı ALGO (+34.5) ve FIL (+10.6) kaçtı. 2024-02: VET, MANA, ALGO 02-08'de (puan -1; +12.4 / +7.0 / +7.6) yerleri doldurdu; temelin 02-09'da aldığı XTZ (+3.8), ICP ve UNI (+26.1) kaçtı. Kuyruk 7 ve 19'daki ders yine geçerli: 3 yer sınırında sonucu çoğu zaman "hangi coin önce yeri aldı" belirliyor.

## Yıllara göre (R; parantezde işlem sayısı)
| Yıl | Eski 16 temel | Eski 16 puansız | Yeni 20 temel | Yeni 20 puansız |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +43.4 (46) | +31.5 (29) | +46.2 (31) |
| 2021 | +164.3 (32) | +174.0 (36) | +41.7 (27) | +54.9 (28) |
| **2022** | **-6.6 (7)** | **-4.9 (6)** | **-3.0 (6)** | **-2.7 (6)** |
| 2023 | +86.7 (38) | +110.8 (44) | -1.9 (39) | -4.5 (61) |
| 2024 | +10.0 (57) | +43.6 (71) | +64.9 (36) | +60.9 (52) |
| 2025 | +15.5 (31) | +19.8 (35) | -19.8 (41) | -19.5 (50) |
| 2026 | -3.1 (19) | +2.1 (17) | +4.3 (15) | +4.5 (18) |

- **2022 (ayı yılı):** beklenen "daha çok stop" olmadı; iki listede de 2022 biraz daha az kötü. Sebep: kırılım + EMA20 üstü olup puanı < +1 olan 4h mumların 2022'de **%91.5'i (16; 402 mumun 368'i)** ve **%88.2'si (20; 431 mumun 380'i)** BTC puanı ≤ -1 iken geldi, yani BTC-dönüş çıkış kuralı onları girişe çevirmedi. Puan şartı yokken ayı piyasası koruması tamamen BTC kuralına kalıyor (eski 16'da bu oran 2020'de %27, 2021'de %46, 2026'da %74).
- Yeni 20'de 2023 (+22 işlem, -2.6R) ve 2025 (+9 işlem) daha kalabalık ama sonuç değişmiyor; kazanç 2020-2021'de (+27.9R) ve tek HBAR işleminde.

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1. En büyük hariç ortalama +0.94 → +1.15, en büyük 5 hariç +0.28 → +0.47. Yeni sürümün 4. büyük işlemi yeni giriş XLM 2024-11-07 (+42.6). XLM ve BCH 2023-06 çıkarılırsa yeni girişler 62 işlemde sadece +7.0R.
- Yeni 20: yeni sürümün en büyük işlemi yeni giriş HBAR 2024-11-08 (+49.8; temelde en büyük ALGO 2024-11-08 +33.9 kaçtı). En büyük hariç ortalama +0.43 → **+0.37**, en büyük 5 hariç -0.08 → +0.03. HBAR olmasa toplam ≈ 89.5R (temel 117.7R).
- Coin bazında fark (R, yeni − temel): 16'da XLM **+52.7**, BCH +30.3, BNB +12.7, LINK +12.4 (BTC **-21.6**, XRP -6.4, SOL -5.4); 20'de HBAR **+56.2**, DASH +23.0, VET +15.9 (ALGO **-27.9**, UNI **-23.7**, XTZ -15.0, FIL -10.7).

## İleriye bakma kontrolü
- Değişiklik bir şartı silmek; yeni bir veri kullanılmıyor. Kalan şartlar temelde de vardı (kırılım sinyal mumunun kendi kapanışı ve önceki 20 mum; EMA20 `merge_informative_pair` ile sadece kapanmış günlük mumdan).
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_no_score_drops_only_the_daily_score_entry_condition`): puan -1 / -3 iken ilk kırılım girişe dönüyor, temel girmiyor; EMA20 hazır değilse (NaN) ve günlük kapanış EMA20 altındaysa giriş yok; stop kolonu temelle aynı; stop ve çıkış metodları temelinkiyle aynı nesne; çıkış EMA20 altında ve BTC puanı ≤ -1'de, coin puanından bağımsız.
- Veri kesme testi: her listede 300 an (yarısı gerçek giriş sinyali, 150 / 152), stratejinin kendi `populate_indicators` + giriş + çıkış kodu tam veriyle ve o anda kesilmiş veriyle (4h mumlar o ana kadar, günlük mumlar o mumun kapanışına kadar kapanmış olanlar) çalıştırıldı; giriş, çıkış ve stop: **0 fark**.
- Backtest çıktısıyla kontrol: her iki sürümün bütün işlemlerinde sinyal mumu bulundu (0 bulunamayan; 9-14 / 6-7 işlemde iki aday, en yeni kullanıldı). Temelin hiçbir işlemi puan < +1 sinyalden gelmiyor (yeniden kurulumun doğruluğu); ortak işlemlerin R'si birebir aynı.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeNoScore --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/noscore_<liste>`. Rapor `scripts/make_report.py --results <zip> --test puansiz --out results/2026-10-29_pusula_puansiz/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
