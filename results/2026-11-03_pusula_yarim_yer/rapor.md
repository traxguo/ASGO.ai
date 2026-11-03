# Kuyruk 26 — yarım kalan işlem yarım yer sayılır — 2026-11-03 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** kuyruk 25'teki yarım çıkışta (EMA20'de yarısı satılır, kalan yarı EMA50'ye kadar taşınır) yarısı satılmış işlem bir yerin **yarısını** tutsa daha iyi olur muyduk? Yani tam işlem 1, yarım kalan 0.5 sayılır; yeni giriş için toplam + 1 ≤ 3 olmalı.
- **Cevap: hayır, red.** Eski 16'da dört şart da tuttu, yeni 20'de net getiri temelin altında kaldı.
  - Eski 16: ortalama +1.35R → **+2.32R**, toplam 311.3R → **427.4R**, net +%827 → **+%867**, DD %23.7 → %21.1. Dört şart tuttu.
  - Yeni 20: ortalama +0.61R → +0.83R, toplam 117.7R → 145.1R, ama net **+%134 → +%127**, DD %22.6 → %23.2. **Net getiri tutmadı.** Kuyruk 25'e göre de kötü (+0.91R, 151.2R, +%140).
- **Neden:** yarım yer kuralı iki listede çok farklı işledi.
  - Eski 16'da kuyruk 25'e göre +62.7R: kazancın 2/3'ü **tek işlemden**. BNB 2020-12-14'te üç yer de yarım kalan işlemlerle doluydu; yeni kural girişe izin verdi, işlem +139.3R yaptı. Kuyruk 25 aynı trende 2021-01-29'da girip +97.8R yapmıştı. Bu tek değişim +41.5R.
  - Yeni 20'de açılan 8 ek giriş toplam -6.1R yaptı (çoğu 2020'de stop). Kaybedilen giriş yok. Sonuç kuyruk 25'ten biraz kötü.
- **Risk:** açıkken toplam risk hep ≈ %3'te kaldı (en fazla %3.04; temelde de %3.03-3.04). Ağırlıklı sayı en fazla 3.0. Aynı anda fiziksel en fazla 5 (eski 16) / 4 (yeni 20) işlem açık oldu.
- Temel `PusulaV2NoBe` değişmedi, baseline rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeHalfSlot(PusulaV2NoBeHalfEma50)` (kod: `strategies/candidates/pusula.py`):
- Kuyruk 25 aynen: EMA20 çıkışında yarısı satılır (Freqtrade kısmi çıkışı), kalan yarı son kapanmış günlük kapanış EMA50 altında, BTC-dönüşte ya da sabit stopta kapanır. Kısmi çıkıştan sonra stopun kaymaması için kuyruk 25'teki düzeltme (`custom_stoploss`) aynen miras alındı.
- **Tek fark, yer sayımı:**
  - Açık işlemin ağırlığı: tam pozisyon (bekleyen giriş emri de) **1**, yarısı satılmışsa **0.5**.
  - Yeni giriş sadece **ağırlık toplamı + 1 ≤ 3** ise alınır. Fiziksel en fazla 6 işlem (6 yarım).
  - Eşikler sabit (0.5, 3), tarama yok.
- Aynı kalanlar: girişler, stop seviyesi, %1 risk (kapanmış bakiyeden), coin başına tek işlem.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Nasıl kodlandı
- Ağırlıklı sınır `confirm_trade_entry` içinde. Freqtrade bu fonksiyonu yeni işlem açmadan hemen önce çağırıyor (backtestte kendi `max_open_trades` kontrolünden sonra; canlı / dry-run'da da girişten önce).
  - Onaylanan işlem henüz açık işlemler listesinde değil. Bu yüzden kontrol "açık ağırlık + 1 ≤ 3".
  - Bir işlemin ağırlığı girişten sonra sadece düşebilir (1 → 0.5 → 0). Yani sınır her an geçerli.
- Freqtrade'in kendi sınırı (`max_open_trades`) bu sınıf için **6** olmalı. Yoksa Freqtrade'in fiziksel sınırı ağırlıklı sınırdan önce devreye girer. 6 ile hiç devreye girmez: ağırlık ≤ 3 ise en fazla 6 işlem var.
- Bu yüzden iki ayrı çalıştırma yapıldı. Temel ve kuyruk 25 `--max-open-trades 3` ile, yeni sınıf `--max-open-trades 6` ile. Temel rakamları değişmedi.
- Reddedilen girişler isteğe bağlı bir dosyaya yazılıyor (`PUSULA_SLOT_LOG`). Freqtrade `--timeframe-detail 1h` ile bir 4h sinyali o mumun her saatinde yeniden deniyor. Bu yüzden 2946 / 1782 ret çağrısı, 739 / 446 ayrı coin-4h mum demek.
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_half_slot_counts_half_trades_as_half_a_slot`. Kontrol edilenler:
  - kuyruk 25'in çıkış, stop ve yarım satış kodu aynen miras;
  - ağırlık 0 / 2 / 2.0 (1 tam + 2 yarım) / 2.0 (4 yarım) / 1.5 / 1.5 iken giriş var;
  - ağırlık 3 / 2.5 / 2.5 / 2.5 / 3 / 3 iken giriş yok.
  228 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel (3 yer) | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.3 | +%931.5 |
| Eski 16 | kuyruk 25 (3 yer) | 158 | +2.309 | 364.75 | +2.488 / 393.1 | +%732.9 | %19.85 | 2.21 | %26.6 | -12490 | 19.5 | +%931.5 |
| Eski 16 | **yarım yer** | 184 | **+2.323** | **427.40** | +2.391 / 440.0 | **+%866.5** | %21.12 | 2.16 | %26.6 | -18566 | 19.0 | +%931.5 |
| Yeni 20 | temel (3 yer) | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | kuyruk 25 (3 yer) | 166 | +0.911 | 151.18 | +0.937 / 155.5 | +%139.9 | %22.49 | 1.53 | %21.1 | -5928 | 11.5 | +%194.7 |
| Yeni 20 | **yarım yer** | 174 | **+0.834** | **145.12** | +0.858 / 149.2 | **+%126.6** | %23.25 | 1.49 | %21.3 | -5967 | 11.5 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). Üç sürüm de al-tutun altında.

**Karar: red.**
- Eski 16: dört şart tuttu (+1.353 → +2.323R; 311.26 → 427.40R; +%827.3 → +%866.5; DD %21.12).
- Yeni 20: ortalama R (+0.834) ve toplam R (145.12) temelden iyi, DD (%23.25) tamam, ama **net getiri tutmadı** (+%134.2 → +%126.6).

## Yer etkisi: kuyruk 25'e göre ne değişti
İşlemler coin + açılış zamanıyla eşleştirildi.

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Ortak işlemler (R aynı; fark yuvarlama) | 153 | +0.01 | 166 | +0.01 |
| Yeni girişler (kuyruk 25'in alamadığı) | +31 | **+199.06** | +8 | **-6.07** |
| Kaybedilen girişler (kuyruk 25'in aldığı, yeni sürümün alamadığı) | -5 | **-136.43** | 0 | 0.00 |
| **Toplam fark** | 158 → 184 | **+62.65** | 166 → 174 | **-6.06** |

- **Eski 16, yeni girişler** (açıldığı anda açık işlemlere göre):
  - 3 yer yarım kalan işlemlerle doluyken: 4 işlem **+160.9R**. İçinde BNB 2020-12-14 **+139.3R** (o anda BTC 2020-10, ETH 2020-10, LTC 2020-11'in kalan yarıları açıktı).
  - 3 işlem açık, 2'si yarım: 14 işlem +29.0R.
  - 4 işlem açık, hepsi yarım: 7 işlem -6.3R.
  - Diğer: 6 işlem +15.5R.
  - En iyileri: BNB 2020-12 +139.3, BTC 2024-01 +19.6, LINK 2020-06 +18.3, TRX 2021-03 +13.8, ETH 2024-02 +7.2.
- **Eski 16, kaybedilen girişler** (5): BNB 2021-01-29 +97.8R ve LINK 2020-07-01 +25.3R, çünkü aynı coinde daha erken giren yeni işlem hâlâ açıktı (BNB 2020-12, LINK 2020-06). Diğer üçü (BNB 2023-12 +9.7, TRX 2024-01 +4.3, LTC 2024-01 -0.8) yer kayması.
- **BNB değişimi tek başına +41.5R** (+139.3 - 97.8). Bu hariç fark +21.2R.
- **Yeni 20:** 8 yeni giriş, hepsi küçük: 6'sı 2020-2021'de (DASH ×3, XTZ, EGLD stopta; IOTA +0.5), 2'si 2025'te (ICP 0, AAVE -1.0). Toplam -6.1R. Kaybedilen giriş yok.
- Yer doluluğu (günlük örnek, "yeni giriş için yer yok" günleri):
  - Eski 16: temel %24.3, kuyruk 25 %32.4, yarım yer **%28.2**.
  - Yeni 20: temel %12.5, kuyruk 25 %16.6, yarım yer **%15.0**.
  - Yani yarım yer kuralı kuyruk 25'in kestiği yerin yaklaşık yarısını geri verdi.
- Ortalama açık işlem: eski 16'da 1.07 / 1.27 / 1.45 (ağırlıklı 1.07 / 0.98 / 1.12); yeni 20'de 0.63 / 0.79 / 0.82.

### Geri kazanılan temel girişler
Kuyruk 25 temelin 79 / 29 girişini kaçırmıştı (temelde +101.9R / +41.8R).
- Eski 16: bunlardan 25'i yeni sürümde geri geldi. Temelde +49.5R, yeni sürümde **+203.7R** (BNB 2020-12 temelde +3.3R, burada +139.3R). BNB hariç: temelde +46.1R, burada +64.5R.
- Yeni 20: 8'i geri geldi. Temelde -6.5R, yeni sürümde -6.1R. Temelin bu listedeki büyük kaçan girişleri (VET 2020-06 +14.4R, DASH 2024-11 +9.1R, NEO / IOTA coin meşgul) geri gelmedi.
- Ağırlıklı sınırın reddettiği girişler arasında temelin aldığı 26 / 13 işlem var (temelde +11.4R / **+31.2R**); kuyruk 25'in aldığı 6 / 0 işlem (+5.9R / 0).

## Açıkken en yüksek toplam risk
Her olaydan hemen sonra (giriş, yarım satış, kapanış) açık işlemler sayıldı. Stopta risk = kalan miktar × (giriş − plan stop). Bakiye = kapanmış işlemler + açık işlemlerin satılmış yarılarının kârı (Freqtrade büyüklüğü bundan hesaplıyor).

| Liste | Sürüm | En yüksek ağırlıklı sayı | En yüksek fiziksel sayı | En yüksek risk (R) | En yüksek risk (bakiyenin %'si) | Fiziksel dağılım (olay sayısı: 3 / 4 / 5 işlem) |
|---|---|---|---|---|---|---|
| Eski 16 | temel | 3.0 | 3 | 3.00 | %3.03 | 100 / 0 / 0 |
| Eski 16 | kuyruk 25 | 3.0 | 3 | 3.00 | %3.03 | 109 / 0 / 0 |
| Eski 16 | yarım yer | **3.0** | **5** | **3.00** | **%3.03** | 119 / 38 / 7 |
| Yeni 20 | temel | 3.0 | 3 | 3.00 | %3.04 | 63 / 0 / 0 |
| Yeni 20 | kuyruk 25 | 3.0 | 3 | 3.00 | %3.04 | 72 / 0 / 0 |
| Yeni 20 | yarım yer | **3.0** | **4** | **3.00** | **%3.04** | 78 / 11 / 0 |

- Ağırlıklı sayı hiç 3'ü geçmedi. Risk R olarak en fazla 3.004 (yarım satışta miktar yuvarlaması; kalan pay 0.5'ten biraz fazla).
- Risk %3'ü biraz geçiyor (%3.03-3.04), çünkü her işlem kendi açılışındaki bakiyenin %1'iyle açılıyor; sonra bir işlem zararla kapanınca bakiye düşüyor. Temelde de aynı.
- İşlem başına açılıştaki risk: bakiyenin en fazla %0.99'u (yeni 20'de %1.01; temelle aynı).
- 6 fiziksel işlem hiç olmadı. 4-5 işlem eski 16'da günlerin %13.4'ünde, yeni 20'de %3.0'ünde.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 kuyruk 25 | 16 yarım yer | 20 temel | 20 kuyruk 25 | 20 yarım yer |
|---|---|---|---|---|---|---|
| 2020 | +44.4 (46) | +93.8 (19) | **+225.9** (29) | +31.5 (29) | +93.8 (20) | +89.3 (24) |
| 2021 | +164.3 (32) | +187.1 (21) | **+102.2** (25) | +41.7 (27) | +41.8 (21) | +41.3 (23) |
| 2022 | -6.6 (7) | -7.0 (7) | -7.0 (7) | -3.0 (6) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +89.0 (34) | +83.8 (34) | -1.9 (39) | -8.6 (36) | -8.6 (36) |
| 2024 | +10.0 (57) | -5.7 (38) | +18.5 (45) | +64.9 (36) | +42.5 (33) | +42.5 (33) |
| 2025 | +15.5 (31) | +9.6 (23) | +6.0 (28) | -19.8 (41) | -17.6 (35) | -18.6 (37) |
| 2026 | -3.1 (19) | -2.0 (16) | -2.0 (16) | +4.3 (15) | +2.3 (15) | +2.3 (15) |

- Eski 16'daki 2020 / 2021 kayması BNB'den: kuyruk 25'te 2021-01'de açılan +97.8R'lik işlem, burada 2020-12'de açılan +139.3R'lik işlem oldu.
- Eski 16'da 2024 düzeldi (-5.7 → +18.5R): BTC 2024-01 (+19.6R) ve ETH 2024-02 (+7.2R) geri geldi. Hesap en büyükken bu yıl; USDT kâr kuyruk 25'te +31.4k, burada +45.9k (kapanış yılına göre).
- Yeni 20'de 2023-2026 kuyruk 25 ile neredeyse aynı. Fark sadece 2020-2021'deki küçük kayıplar.
- Doğrulama + kasa dönemi (2025-2026): 16'da +12.4 / +7.6 / +4.0R, 20'de -15.5 / -15.3 / -16.3R. Yeni sürüm bu dönemde iki listede de en zayıf.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplamdaki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | kuyruk 25 | BNB 2021-01 +97.8 | %27 | +1.700 | +0.330 | +1.751 |
| Eski 16 | yarım yer | BNB 2020-12 +139.3 | **%33** | +1.575 | +0.401 | +1.603 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | kuyruk 25 | THETA 2020-12 +92.2 | %61 | +0.357 | -0.272 | +0.389 |
| Yeni 20 | yarım yer | THETA 2020-12 +92.2 | **%64** | **+0.306** | **-0.295** | +0.334 |

- Yeni sürümün en büyük 5'i:
  - Eski 16: BNB 2020-12 +139.3, ETC 2021-03 +94.1, SOL 2023-10 +54.1, BTC 2020-10 +38.9, BTC 2023-10 +29.4.
  - Yeni 20: THETA 2020-12 +92.2, ALGO 2024-11 +31.9, FIL 2021-03 +29.0, UNI 2024-02 +22.4, NEO 2021-02 +19.3 (kuyruk 25 ile aynı).
- Eski 16'da en büyük işlem hariç ortalama yine temelden iyi (+0.948 → +1.575), ama kuyruk 25'ten kötü (+1.700). En büyük 5 hariç en iyisi bu sürüm (+0.401).
- Yeni 20'de en büyük işlem hariç ortalama temelden de kuyruk 25'ten de kötü.

## İleriye bakma kontrolü
- Yeni kural veri kullanmıyor: sadece karar anındaki açık işlemleri ve her birinin yarım satışının dolup dolmadığını sayıyor. Bu bilgi karar anında biliniyor.
- Göstergeler, giriş ve çıkış kodu kuyruk 25 ile aynı (miras; birim testi kontrol ediyor). Yine de veri kesme testi bu sınıfla yeniden çalıştırıldı: her listede 300 an (150 rastgele 4h mum, 150 "günlük kapanış EMA20 altına indi" anı); her anda her coin için tam veri ile o anda kesilmiş veri karşılaştırıldı (giriş, çıkış, yarım satış şartı, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4702 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5729 kontrol, **0 fark**.
- Ortak işlemler (153 / 166) kuyruk 25 ile aynı saatte açılıp kapanıyor ve aynı R'yi veriyor (fark toplamı +0.01R; yuvarlama).

## Uyarılar
- Eski 16'daki iyileşmenin 2/3'ü tek işlemin daha erken girişi (BNB 2020-12). Bu bir şans faktörü: yarım kalan üç işlemin yanında aynı coinin daha erken kırılımı yakalandı.
- Büyüklük hâlâ kapanmış bakiyeden; kalan yarıların kârı bakiyeye geç giriyor (kuyruk 25'teki ikinci etki). Yeni 20'de net getiri bu yüzden ve 2020'deki ek kayıplar yüzünden düştü.
- Canlıda kısmi çıkış ayrı bir emir; sınıf kabul edilmediği için demoya gitmiyor.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Temel + kuyruk 25 (3 yer): `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeHalfEma50 --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/slot3_<liste>`.
- Yarım yer: aynı komut, `--strategy-list PusulaV2NoBeHalfSlot --max-open-trades 6 --backtest-directory user_data/backtest_results/slot6_<liste>` (ağırlıklı sınır 3 strateji içinde).
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu, iki sonuç dosyası tek tabloda birleştirilerek (funding, çıkış türleri, coin tablosu, grafikler).
- Maliyet: emir başına %0.1 (komisyon + kayma; kısmi çıkış da bir emir), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor. Önceki turlar da aynı aralığı kullandı; yeni bir kasa kullanımı yok.
