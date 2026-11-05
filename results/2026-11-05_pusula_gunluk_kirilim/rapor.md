# Kuyruk 28 — günlük kapanışla kırılım (20 günlük tepe) — 2026-11-05 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** Long tetiğini 4 saatlik kapanış yerine **günlük kapanışa** bağlasak (gün, önceki 20 günün en yüksek seviyesinin üstünde ilk kez kapanınca) daha iyi olur muyduk? Fikir: gün içi sahte kırılımları elemek.
- **Cevap: hayır, red.** İki listede de toplam R ve net getiri çok düştü. Eski 16'da ortalama R de düştü.
  - Eski 16: işlem 230 → **130**, ortalama +1.35R → **+0.87R**, toplam 311.3R → **112.9R**, net +%827 → **+%157**, DD %23.7 → %14.8.
  - Yeni 20: işlem 193 → **70**, ortalama +0.61R → +0.96R (daha iyi), toplam 117.7R → **67.4R**, net +%134 → **+%73**, DD %22.6 → %18.9.
- **Neden kötü:** Günlük tetik çok daha seyrek ve geç. Temelin en büyük kazançlarının çoğu (ETC 2021-03 +94R, SOL 2023-10 +59R, BNB 2021-01 +53R, ALGO 2024-11 +35R, FIL 2021-03 +33R) yeni sürümde hiç yok. Günlük kırılım geldiğinde fiyat çoğu zaman 4h dibinden çok uzakta, stop %8'i aşıyor ve sinyal düşüyor (günlük sinyallerin %63 / %80'i).
- **Veri madenciliği uyarısı:** Bu fikir bir önceki turun (kuyruk 27) sonuçlarına bakılarak yazıldı (oradaki en iyi kaçan işlemler günlük kapanışta açılmıştı). Yani fikir test edilecek verinin kendisinden seçildi; iyi çıksaydı bile şüpheyle bakmak gerekirdi. Nitekim eski 16'daki en büyük yeni işlem yine aynı **XLM 2024-11 (+42.7R)**: yeni sürümün toplamının %38'i. Bu işlem hariç eski 16 toplamı 70.2R.
- Temel `PusulaV2NoBe` değişmedi, baseline rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeDailyBreakout(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Long kırılım şartı (`breakout_up`): son **kapanmış** günlük mumun kapanışı, önceki 20 günlük mumun en yüksek seviyesinin (o gün hariç) üstünde, ve bir önceki gün böyle bir kapanış yoktu (ilk günlük kapanış).
- Sinyal, o günlük mumla aynı anda kapanan 4h mumda (20:00 UTC mumu, 00:00 UTC'de kapanır) verilir. Limit emir bir sonraki mumda (00:00 UTC) konur.
- Aynı kalanlar (aynı günlük mumdan okunur): coinin günlük puanı ≥ +1 ve günlük kapanış EMA20 üstünde. Giriş bölgesi, stop (1.5 ATR / 10 mum dibi, 4h, hangisi genişse), stop > %8 ise sinyal yok, %1 risk, en fazla 3 işlem, çıkışlar (günlük EMA20, BTC-dönüş, sabit stop), emir 3 mum geçerli, short yok.
- Eşikler sabit (20 gün, ilk kapanış), tarama yok.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Nasıl kodlandı
- Yeni yardımcılar: `daily_breakout_first` (günlük veride ilk kapanış kırılımı) ve `add_daily_breakout` (bunu 4h tabloya koyar). Sınıf `populate_indicators`'a bu sütunu ekliyor ve `signal_conditions`'ta `breakout_up`'ı onunla değiştiriyor. Diğer her şey temelden miras.
- **Zaman hizalama (ileriye bakma yok):**
  - Günlük veri 4h tabloya Freqtrade'in `merge_informative_pair`'i ile giriyor: bir 4h satır sadece o satırın kapanışında ya da öncesinde **kapanmış** günlük mumu görür. 20:00 mumu ile günlük mum aynı anda (00:00) kapandığı için o satır o günü görür.
  - İşaret sadece "4h mumun kapanışı = gördüğü günlük mumun kapanışı" olan satırda. Ertesi günün diğer 4h satırları aynı günlük mumu görmeye devam eder ama işaret almaz (sinyal tekrar etmez).
  - Zamanlar karşılaştırmadan önce aynı birime (ns) çevriliyor; ms / ns karışması (2026-10-26 funding turundaki hata) burada sonucu bozamaz.
  - Yeni veri sadece günlük dosyadan (`dp.get_pair_dataframe`) alınıyor; backtestte son 1000 mumu tutan 4h analiz tablosu kullanılmıyor (2026-10-17 turundaki hata).
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_daily_breakout_signals_on_the_4h_candle_closing_with_the_first_daily_breakout`. Kontrol edilenler:
  - sinyal sadece kırılım gününün 20:00 mumunda; ikinci kırılım günü (ilk değil) ve ertesi günün diğer mumları sinyalsiz; aynı günün önceki 4h mumlarında sinyal yok;
  - veri o mumun kapanışında kesilince aynı sinyal, bir mum önce kesilince sinyal yok;
  - günlük dosyanın zamanı ms olunca da aynı sonuç;
  - temelle aynı fonksiyonlar miras, short yok.
  230 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.3 | +%931.5 |
| Eski 16 | **günlük kırılım** | 130 | **+0.869** | **112.94** | +0.860 / 111.8 | **+%156.7** | %14.83 | 2.07 | %30.8 | -2896 | 11.4 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | **günlük kırılım** | 70 | +0.963 | **67.38** | +0.952 / 66.7 | **+%73.1** | %18.91 | 2.30 | %31.4 | -1215 | 11.0 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). İki sürüm de al-tutun altında; yeni sürüm çok daha altında.

**Karar: red.**
- Eski 16: ortalama R (+1.353 → +0.869), toplam R (311.26 → 112.94) ve net (+%827.3 → +%156.7) **tutmadı**. DD (%14.83) tamam.
- Yeni 20: ortalama R tuttu (+0.610 → +0.963). Toplam R (117.72 → 67.38) ve net (+%134.2 → +%73.1) **tutmadı**. DD (%18.91) tamam.
- Düşük DD bir iyileşme değil: işlem sayısı ve açık işlem çok az (ortalama açık işlem 1.07 → 0.63 / 0.63 → 0.33).

## Sinyaller nereye gitti
Dönem içindeki günlük "ilk kapanış" kırılımları (2020-01 → 2026-09):

| | Eski 16 | Yeni 20 |
|---|---|---|
| Günlük ilk kapanış kırılımı | 1406 | 1438 |
| + puan ≥ +1 ve EMA20 üstü | 1037 | 956 |
| Bunlardan stop > %8 (sinyal yok) | **654 (%63)** | **769 (%80)** |
| Sinyal (stop ≤ %8) | 383 | 187 |
| — işlem açıldı | 130 | 70 |
| — 3 yer doluydu | 93 | 79 |
| — coinde zaten işlem açıktı | 74 | 21 |
| — emir dolmadı / iptal / aynı mumda çıkış sinyali | 86 | 17 |

- **Stop > %8 yüzünden kaçan günlük sinyaller (kuyruğun istediği rapor):** 654 / 769. Yıllara göre eski 16: 2020 110, 2021 228, 2022 34, 2023 89, 2024 112, 2025 53, 2026 28; yeni 20: 50, 225, 45, 131, 171, 70, 77. Bu sinyallerin stop ortancası %12.8 / %14.2.
  - Karşılaştırma: temelin 4h ilk kapanış kırılımlarında (aynı puan / EMA20 şartlarıyla) stop > %8 oranı %55.7 / %74.1. Günlük kırılımda oran daha yüksek (%63.1 / %80.4): gün boyu yükselen fiyat 10 mumluk 4h dibinden uzaklaşıyor. Kuyruğun öngördüğü risk ("stop %8'i daha sık aşar") gerçekleşti.
- "3 yer doluydu" 93 / 79 sinyalin 75 / 73'ünde yerler o geceden önce zaten doluydu. Günlük sinyaller aynı gecelerde toplanıyor (eski 16'da 258 sinyal gecesinin 15'inde, yeni 20'de 122 gecenin 8'inde 3'ten fazla sinyal; en çok 8 / 10).
- Bütün yeni girişler 00:00 UTC'de açıldı (130 / 70). Temelde girişler günün altı 4h mumuna dağılıyordu.

## Temelle ortaklık (işlem eşleştirme)
Birebir eşleşme (coin + açılış saati):

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Ortak işlemler (R birebir aynı) | 9 | 0.00 fark | 5 | 0.00 fark |
| Yeni girişler (temelde olmayan) | 121 | **+117.01** (ort. +0.967) | 65 | **+72.58** (ort. +1.117) |
| Kaybedilen girişler (temelin aldığı, yeninin almadığı) | 221 | **+315.34** (ort. +1.427) | 188 | **+122.92** (ort. +0.654) |
| **Toplam fark** | 230 → 130 | **-198.33** | 193 → 70 | **-50.34** |

- Neredeyse bütün işlemler değişti: ortak işlem sadece 9 / 5. Temelle aynı saatte açılanlar, temelin 4h kırılım sinyalinin de 20:00 mumunda geldiği (günlük kırılımla aynı mum) işlemler.
- En büyük yeni giriş hariç: yeni girişler +74.3 / +46.8R. En büyük kayıp hariç: kaybedilenler +221.3 / +88.5R. Fark büyük kazançlardan bağımsız olarak temel lehine.

### Aynı trendde: giriş fiyatı farkı (kuyruğun istediği rapor)
Aynı coinde, açık kaldığı süreler çakışan bir temel işlemi ile bir yeni işlem "aynı trend" sayıldı (her yeni işlem için en yakın açılışlı temel işlemi).

| | Eski 16 | Yeni 20 |
|---|---|---|
| Aynı trende giren çift | 70 | 30 |
| Yeni sürüm daha geç / daha erken / aynı saat | 52 / 11 / 7 | 22 / 3 / 5 |
| Gecikme ortancası | 30 saat | 18 saat |
| Giriş fiyatı farkı (yeni / temel - 1), ortanca | **+%1.67** | **+%1.35** |
| Sadece geç girenlerde ortanca | +%4.23 | +%2.35 |
| Bu çiftlerin R'si: temel → yeni | +111.6 → **+80.5** | +56.1 → **+25.6** |
| Stop mesafesi ortalaması: temel → yeni | %5.33 → %5.39 | %6.08 → %6.31 |

- Aynı trendde yeni sürüm genelde daha geç ve daha pahalı giriyor ve daha az R alıyor. Örnek: BTC 2024-01 temel +20.8R, yeni sürüm 15 gün sonra %14 daha pahalı +10.3R; UNI 2024-02 +26.1 → +14.2R (12 saat sonra, %2.3 pahalı); IOTA 2020-07 +7.9 → -1.1R.
- Yeni sürümün daha erken girdiği az sayıda durum var (ör. TRX 2021-03, ADA 2023-11, DASH 2024-11): günlük kırılım temelin 4h girişinden günler önce geldi; bunlar iyi (+15.7 / +10.0 / +11.5R).
- **Temel işlemi olmayan trendler:** yeni sürümün 60 / 40 işlemi temelin hiç girmediği trendlerde (+32.4 / +41.8R; en iyileri XLM 2024-11 +42.7, NEAR 2023-10 +25.8). Temelin 160 / 163 işlemi yeni sürümün hiç girmediği trendlerde (+199.7 / +61.6R); bunların 153 / 160'ında günlük sinyal hiç yoktu (yer dolu olan sadece 7 / 3). Bu grupta temelin en büyükleri: ETC 2021-03 +94.1, SOL 2023-10 +58.6, BNB 2021-01 +53.0, BTC 2023-10 +22.6 / ALGO 2024-11 +34.5, FIL 2021-03 +33.0, THETA 2020-12 +24.1.

### Kuyruk 27'deki örnekler bu sürümde
- XLM 2024-11 (eski 16): yeni sürümde var, **+42.7R** (kuyruk 27 ile aynı işlem, aynı saat).
- IOTA 2020-07 (yeni 20): 3 işlem (-0.2, -1.1, +3.5R), toplam +2.3R (kuyruk 27'de +9.8R).
- ZEC 2021-10: +1.2R (kuyruk 27'de +4.8R). XTZ 2024-02: yeni sürümde işlem yok.
- Yani fikri doğuran 4 örnekten sadece biri (XLM) bu kuralla aynı sonucu verdi.

## Stopla biten işlemler
- Stopla biten oran: eski 16 %41.7 → %49.2, yeni 20 %54.4 → %57.1. Günlük kapanış gün içi sahte kırılımları azaltmadı; tersine stop oranı biraz arttı (giriş daha geç, gün içi geri çekilme stopa daha yakın).

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 günlük | 20 temel | 20 günlük |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +28.3 (21) | +31.5 (29) | +5.9 (6) |
| 2021 | +164.3 (32) | **+14.9** (19) | +41.7 (27) | -5.5 (12) |
| 2022 | -6.6 (7) | -5.4 (6) | -3.0 (6) | -4.2 (4) |
| 2023 | +86.7 (38) | +8.6 (27) | -1.9 (39) | **+23.8** (17) |
| 2024 | +10.0 (57) | **+64.7** (25) | +64.9 (36) | +51.5 (13) |
| 2025 | +15.5 (31) | +8.8 (20) | -19.8 (41) | -4.0 (8) |
| 2026 | -3.1 (19) | -6.9 (12) | +4.3 (15) | -0.2 (10) |

- Geliştirme dönemi (2020-2024): 16'da +298.8R (180) → +111.1R (98); 20'de +133.2R (137) → +71.6R (52).
- **Doğrulama + kasa dönemi (2025-2026):** 16'da +12.4R (50 işlem) → **+1.8R** (32); 20'de -15.5R (56) → **-4.2R** (18). Yeni 20'de kayıp daha az, ama bu daha az işlemden (ortalama -0.28 → -0.23R, neredeyse aynı). Eski 16'da kötüleşti.
- Eski 16'da sadece 2024 iyileşti; bunun +42.7R'si XLM 2024-11. 2021'de (temelin en iyi yılı) 164 → 15R.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplamdaki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | günlük kırılım | **XLM 2024-11 +42.7** | **%38** | +0.544 | +0.072 | +0.539 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | günlük kırılım | NEAR 2023-10 +25.8 | **%38** | +0.603 | -0.055 | +0.598 |

- Yeni sürümün en büyük 5'i: eski 16 XLM 2024-11 +42.7, BNB 2024-02 +19.4, TRX 2021-03 +15.7, BTC 2020-10 +15.1, XLM 2025-07 +10.9; yeni 20 NEAR 2023-10 +25.8, UNI 2024-02 +14.2, XTZ 2024-11 +12.4, DASH 2024-11 +11.5, HBAR 2024-02 +7.1.
- Yeni sürüm tek işleme daha bağımlı (%38 / %38). Yeni 20'deki ortalama R iyileşmesi en büyük 5 hariç kayboluyor (-0.076 → -0.055, ikisi de sıfır civarı).

## İleriye bakma kontrolü
- Yeni kural sadece kapanmış günlük mumları kullanıyor: 20 günlük tepe bir gün kaydırılmış (o günü içermiyor), işaret sadece günlük mumla aynı anda kapanan 4h satırında.
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 150 rastgele 4h an + 150 "günlük kırılım sinyali" anı (sinyal mumunun kapanışı). Her anda her coin için tam veri ile o anda kesilmiş 4h ve günlük veri karşılaştırıldı (giriş, çıkış, günlük kırılım işareti, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4746 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5801 kontrol, **0 fark**.
- Ortak işlemler (9 / 5) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor (fark 0.0000R).
- Backtestte bütün girişler 00:00 UTC'de: sinyal 20:00 mumunda, emir sonraki mumda. Hiçbir giriş günlük mum kapanmadan açılmadı.

## Uyarılar
- **Veri madenciliği riski:** fikir kuyruk 27'nin kaybedilen / kazanılan işlemlerine bakılarak üretildi (aynı veri, aynı dönem). Bu tür "sonuca bakıp kural yazma" iyi sonuç verse bile güvenilmez olurdu. Burada sonuç kötü çıktı; fikri doğuran XLM 2024-11 işlemi yine yeni sürümün en büyük işlemi, ama geri kalan işlemler temelin çok altında.
- Yeni 20'de ortalama R'nin yükselmesi (+0.61 → +0.96) az işlemle (70) ve tek işleme %38 bağımlılıkla geldi; toplam ve net yarı yarıya düştü.
- Dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeDailyBreakout --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/daily_<liste>`.
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu (funding, çıkış türleri, coin tablosu, grafikler).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Analiz betikleri repo dışında (`/home/user/asgo_scratch/daily/`).
