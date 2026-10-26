# Kuyruk 17 — ekleme: yüksek funding'de long'a girme — 2026-10-26 (temel: PusulaV2NoBe)

## Kural (testten önce yazıldı)
`PusulaV2NoBeFunding(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `funding_annualised`):
- Long girişine **tek** şart eklendi (`funding_ok`): coinin **son 3 günlük yıllık funding oranı %50'nin üstünde değil** (≤ %50 ise girilir).
- Karar anı: sinyal 4h mumunun kapanışı (emrin verildiği an). Sadece bu andan **önce** ödenmiş funding'ler sayılır (tam bu anda ödenen dahil değil); pencere: karar anından önceki 72 saat.
- Yıllığa çevirme: pencerede ödenen oranların toplamı / bu ödemelerin kapsadığı saat × 8760 (= saatlik ortalama oran × yıldaki saat). Her ödemenin kapsadığı süre bir önceki ödemeden bu yana geçen süre (veri boşluğu uzun sayılmasın diye en fazla 8 saat). 8 saatlik ödemede bu, son 9 oranın ortalaması × 3 × 365 (%50 / yıl ≈ ödeme başına %0.0457). Bazı coinler 4 saatliğe (AXS, ENJ, XTZ, kısa süre 1 saatliğe) geçti; o zaman aynı formül 6 (ya da 24) ödeme/gün sayar, karışık pencere de doğru hesaplanır.
- Pencerede hiç ödeme yoksa (coinin arşivdeki ilk funding'inden önce, ör. ICP 2022-09 öncesi) bilgi yok sayılır ve **giriş temeldeki gibi serbest**.
- Eşik sabit (%50 / yıl), **tarama yok**. Başka her şey aynı (kırılım, puan ≥ +1, EMA20 üstü, stop, çıkışlar, %1 risk, en fazla 3 işlem, sadece long).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R, toplam R ve hesap net getirisi daha iyi; DD belirgin kötü değil ve `docs/metrics.md` sınırında (%25) → **kabul**; aksi halde **red**. Tek işlem yoğunlaşması önceki turlardaki gibi raporlanır.
- İleriye bakma testi: `tests/test_pusula.py` (karar anında ve sonrasında ödenen oran değiştirilince sonuç değişmiyor; 8 saat / 4 saat aralık; veri yoksa serbest).

## GUO'ya not
- Soru: funding çok yüksekken (long tutmak yıllık %50'den pahalıyken, yani herkes long'dayken) girmesek daha mı iyi?
- Cevap: **çok nadir oluyor ve sonucu değiştirmiyor.** Bu şart 6.5 yılda temelin sadece 12 (eski 16) ve 5 (yeni 20) girişini engelledi, hepsi 2020-2021 boğa döneminde. Eski 16'da engellenenler toplamda eksiydi (-3.9R), yeni 20'de artıydı (+5.5R; NEO 2021-02 +5.7R, ZEC 2020-07 +2.4R). Funding masrafı biraz düştü (16: -14077 → -13817 USDT, 20: -3769 → -3217 USDT) ama kazanç değişmedi.
- **Karar: red.** Yeni 20'de ortalama R, toplam R ve net getiri kötüleşti. Temel `PusulaV2NoBe` değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | funding filtresi | 220 | +1.42R | 313.01 | +1.41 / 309.9 | +%844.0 | %23.7 | 2.07 | %32.7 | -13817 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | funding filtresi | 189 | **+0.59R** | **111.69** | +0.58 / 109.8 | **+%122.0** | %22.6 | 1.51 | %22.8 | -3217 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü (iki listede de değişmedi).
- Al-tut: eşit ağırlık, aynı dönem.

**Karar: red.** Eski 16'da dört şart da sağlandı ama fark küçük (+1.7R, net +17 puan, DD aynı). Yeni 20'de ortalama R (+0.61 → +0.59), toplam R (-6.0R) ve net (-12 puan) kötü. Kural "iki listede de daha iyi" istiyor.

## Engellenen temel girişler (filtre değeri temelin kendi sinyal mumunda hesaplandı)
| Liste | Engellenen | Kazanan | Toplam R | Hesap-R | Bu işlemlerin funding'i (USDT) | Boşalan yere giren | Onların R'si |
|---|---|---|---|---|---|---|---|
| Eski 16 | 12 | 2 | -3.85 (ort. -0.32) | -3.15 | -531 | 2 (LTC 2020-05, BNB 2020-08) | -2.10 |
| Yeni 20 | 5 | 2 | **+5.48** (ort. +1.10) | +5.42 | -412 | 1 (NEO 2021-03) | -0.56 |

- Eski 16'da engellenenler: 10 stop (her biri ≈ -1R; BTC 2021-04, BCH 2020-07 / 2020-08, XRP 2021-03, SOL 2021-03 vb.) ve 2 kazanan (ETC 2021-02 +3.3R, BTC 2021-02 +3.1R). Yeni 20'de: 3 kayıp (VET 2021-05, XTZ 2020-05, ALGO 2021-03) ve 2 kazanan (NEO 2021-02 **+5.7R**, ZEC 2020-07 +2.4R).
- Engellenen girişlerin yıllık funding'i %51-%126. Temelin girişlerinin yarısı yıllık ≈ %8-11'de (taban oran %0.01 / 8 saat = %11), %95'i %48'in altında: eşik sadece uç boğa anlarına dokunuyor. Engellenen 17 girişin hepsi 2020-05 → 2021-05 arası; 2022'den sonra hiç tetiklenmedi.
- Temeldeki diğer bütün girişler yeni sürümde de aynen var (ortak 218 / 188 işlem); fark sadece engellenenler ve boşalan yerlere girenler.
- Funding tasarrufu küçük: 16'da +260 USDT, 20'de +552 USDT. Engellenen işlemlerin ödediği funding (-531 / -412) toplam funding'in %4 / %11'i. Funding masrafının asıl kaynağı yüksek funding anında girmek değil, normal oranda uzun tutmak.

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1; o hariç ortalama +0.94 → +0.99, en büyük 5 hariç +0.28 → +0.29. Fark birkaç ≈ -1R stopun atlanmasından (coin bazında BCH +1.5, SOL +1.2, ATOM / XLM / XRP +1.1; ETC -3.3, BNB -1.0).
- Yeni 20: en büyük işlem iki sürümde de ALGO 2024-11-08 +33.9; o hariç +0.43 → +0.40, en büyük 5 hariç -0.08 → -0.11. Kaybın çoğu tek işlem: NEO 2021-02 +5.7R atlandı (coin farkı -6.2), ZEC -2.4.
- Kısaca: iki listedeki fark da birkaç işlemden ve iki yönde; filtrenin tutarlı bir etkisi yok.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeFunding --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/funding_<liste>`. Rapor `scripts/make_report.py --results <zip> --test funding_filtre --out results/2026-10-26_pusula_funding_filtre/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Funding verisi: `user_data/data/binance/futures/<coin>-1h-funding_rate.feather` (Kalabalık'ın kullandığı dosyalar, data.binance.vision arşivi). Bu listelerde 4 saatliğe geçen coinler AXS, ENJ, XTZ (kısa süre 1 saatlik ödeme de var); formül bunları ödeme aralığına göre yıllığa çeviriyor. Bu turda engellenen bütün girişler 8 saatlik dönemdeydi.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Hata notu: ilk çalıştırmada funding dosyalarının zaman birimi (milisaniye) ile mum zamanları (nanosaniye) karıştı, filtre hiç değer üretmedi ve iki sürüm aynı çıktı. Düzeltildi (iki taraf aynı birime çevriliyor), birim testine milisaniyeli veri kontrolü eklendi, iki liste yeniden çalıştırıldı; yukarıdaki rakamlar düzeltilmiş çalıştırmadan. Kural değişmedi.
- İleriye bakma: karar anı sinyal mumunun kapanışı, sadece ondan önce ödenmiş oranlar; birim testi karar anında ve sonrasındaki oranları değiştirince sonucun değişmediğini kontrol ediyor. Yeni sürümün girişlerinde en yüksek yıllık funding %49 (kural uygulanıyor).
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
