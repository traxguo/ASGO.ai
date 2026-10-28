# Kuyruk 19 — ekleme: piyasa genişliği — 2026-10-28 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: bir coinde long'a girmeden önce "listedeki coinlerin en az yarısı da yükseliş trendinde mi?" diye baksak (piyasa genişliği), yalnız yükselen coinlerdeki kötü kırılımları eleyebilir miyiz?
- Cevap: **hayır.** Kapı zamanın yarısından fazlasında kapalı (16'da %55, 20'de %64) ve en büyük kazançların bazıları tam da piyasa henüz uyanmadan, öncü coinde başlıyor: SOL 2023-10 **+58.6R** ve BTC 2023-10 **+22.6R** (o anda 16 coinden sadece 4'ü trendde), ALGO 2024-11 **+34.5R**, UNI 2024-02 **+26.1R**. Şart bunları kesti.
- Yeni 20'de sonuç daha iyi göründü (net +%134 → +%240, DD %22.6 → %16.9), ama bu kazancın çoğu aynı yükselişte bir gün sonra boşalan yerlere giren başka coinlerden geldi (yer şansı). Eski 16'da her şey kötüleşti ve DD %25 sınırını aştı (%28.9).
- **Karar: red.** Temel `PusulaV2NoBe` değişmedi.

## Kural (testten önce yazıldı)
`PusulaV2NoBeBreadth(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `breadth_share`):
- Long girişine **tek** şart eklendi (`breadth_ok`): aktif coin listesindeki (`dp.current_whitelist()`, yani hangi liste ile çalışırsa onun coinleri) coinlerin **en az %50'sinin** son kapanmış günlük puanı ≥ +1.
- Karar anı: sinyal 4h mumunun kapanışı (mum tarihi + 4 saat). Her coin için o ana kadar kapanmış son günlük mum kullanılır (açılışı = karar gününün başı − 1 gün). Coinin kendi puanıyla aynı görünürlük (`merge_informative_pair`).
- O günlük mumu olmayan ya da puanı henüz hesaplanamayan (veri yok, ısınma, verisi bitmiş) coin **ne paya ne paydaya** sayılır. Hiç puanlı coin yoksa giriş yok.
- Genişlik her coinin **günlük** verisinden hesaplanır, diğer coinlerin 4h tablosundan değil (backtestte o tablolar sadece son 1000 mumu tutuyor). Zaman birimleri (ms / ns) hesapta eşitleniyor.
- Eşik sabit (%50), **tarama yok**. Başka her şey aynı (puan ≥ +1, EMA20 üstü, kırılım, stop, çıkışlar, %1 risk, en fazla 3 işlem, sadece long).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → **kabul**; aksi halde **red**.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | genişlik | 208 | **+1.08R** | **224.58** | +1.07 / 222.8 | **+%399.2** | **%28.9** | 1.73 | %31.7 | -10396 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | genişlik | 146 | +1.06R | 155.14 | +1.05 / 152.9 | +%240.0 | %16.9 | 2.11 | %24.7 | -3752 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem.

**Karar: red.** Eski 16'da dört şartın dördü de bozuldu (ortalama R, toplam R, net kötü; DD %28.9 > %25). Yeni 20'de dördü de iyi, ama kural "iki listede de" istiyor.

## Engellenen temel girişler (şart temelin kendi sinyal mumunda hesaplandı)
| Liste | Engellenen | Kazanan | Toplam R | Hesap-R | Bu işlemlerin funding'i (USDT) | En büyük 2 hariç | Boşalan yere giren | Onların R'si | Yer kayması ile kaçan temel |
|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | 70 (%30) | 20 | **+99.68** (ort. +1.42) | +98.71 | -3125 | 68 işlem +18.46R (ort. +0.27) | 49 | +13.44 | 1 işlem, +0.45R |
| Yeni 20 | 70 (%36) | 16 | **+39.28** (ort. +0.56) | +38.63 | -1213 | 68 işlem **-21.27R** (ort. -0.31) | 28 | **+96.15** | 5 işlem, +19.45R |

- Kıyas: kapı açıkken gelen (kalan) temel girişler 16'da 160 işlem ort. **+1.32R**, 20'de 123 işlem ort. **+0.64R**. Engellenenler 16'da daha iyi (+1.42R), 20'de daha kötü (+0.56R).
- En büyük katkılar (engellenen, R; parantezde o andaki genişlik): eski 16'da SOL 2023-10-16 **+58.6** (4/16), BTC 2023-10-16 **+22.6** (4/16), BTC 2020-10-09 +12.8 (4/13), TRX 2025-06-28 +10.3 (5/16), BCH 2025-06-08 +5.8 (6/16). Yeni 20'de ALGO 2024-11-08 **+34.5** (9/20), UNI 2024-02-09 **+26.1** (5/20), FIL 2024-11-08 +10.6 (9/20), UNI 2025-07-08 +4.2 (2/20), XTZ 2024-02-09 +3.8 (5/20).
- Yıllara göre engellenenler: 16'da 2023 11 işlem **+88.2R**, 2025 13 işlem +21.3R, 2024 24 işlem -12.5R; 20'de 2024 24 işlem **+58.7R**, 2023 16 işlem -7.3R. Yani engellenen kazancın çoğu birkaç büyük "öncü coin" işlemi.
- Genişliğe göre temel (16 / 20): < %25 → 14 işlem ort. +5.77R / 30 işlem +0.68R; %25-50 → 56 işlem +0.34R / 40 işlem +0.47R; %50-75 → 73 işlem +0.71R / 36 işlem +0.42R; ≥ %75 → 87 işlem +1.84R / 87 işlem +0.73R. Tutarlı bir "dar piyasada kırılım kötü" ilişkisi yok; 16'da en dar grup en iyisi.

## Boşalan yer etkisi
- Ortak işlemler iki sürümde aynı R'yi verdi (16: 159 işlem 211.14R, 20: 118 işlem 58.99R), fark tamamen engellenen ve yerine girilen işlemlerden.
- Eski 16: boşalan yerlere 49 yeni işlem girdi (+13.4R, ort. +0.27; XRP 2020-11-14 +17.4, TRX 2025-07-04 +7.8, BTC 2020-10-10 +7.7). Engellenen +99.7R'nin yanında küçük.
- Yeni 20: boşalan yerlere 28 yeni işlem girdi, **+96.2R** (ort. +3.43): NEAR 2023-10-30 +25.8, XTZ 2024-11-10 +17.7, ENJ 2024-11-09 +16.6, MANA 2024-11-09 +14.4, UNI 2024-02-10 +12.1, FIL 2024-02-10 +8.8. Bunların çoğu, ALGO / FIL / UNI'nin engellendiği **aynı yükselişin bir gün sonrası** (genişlik %45 → %50+ olunca): 2024-11-08'de ALGO ve FIL engellendi, 2024-11-09/10'da ENJ, MANA, XTZ girdi; 2024-02-09'da UNI engellendi, ertesi gün UNI (daha geç, +12.1 yerine +26.1 kaçtı), FIL ve VET girdi. Yer kayması ile 5 temel işlem kaçırıldı (+19.5R; DASH 2024-11-23 +9.1, ALGO 2023-11-25 +6.8).
- Kısaca: yeni 20'deki kazanç "genişlik kötü işlemi eledi" değil, "aynı yükselişte 3 yere hangi coinlerin girdiği değişti" etkisi. Kuyruk 7'deki ders (3 yer sınırında coin sırası toplamı ±60R oynatıyor) burada da geçerli.

## Kapının kapalı olduğu zaman
- 4h karar anlarının **%54.5'inde (16)** ve **%64.0'ünde (20)** genişlik %50'nin altında (ya da hiç puanlı coin yok, dönemin ≈ %1'i, başlangıç ısınması).
- Yıllara göre kapalı payı: 16'da 2020 %33, 2021 %32, 2022 %91, 2023 %44, 2024 %47, 2025 %58, 2026 %79; 20'de 2020 %38, 2021 %35, 2022 %95, 2023 %64, 2024 %59, 2025 %75, 2026 %80.
- Temel girişlerin %30'u (16) ve %36'sı (20) kapı kapalıyken geldi. 2022'de kapı neredeyse hep kapalı ama orada engellenen temel giriş az (16'da 3 işlem -2.5R, 20'de 5 işlem -2.0R): coinin kendi günlük puanı ayı piyasasını zaten büyük ölçüde dışarıda tutuyor.

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1; o hariç ortalama +0.94 → +0.63, en büyük 5 hariç +0.28 → +0.13. Temelin 2. büyük işlemi SOL 2023-10 (+57.8) ve 4. büyük BTC 2023-10 (+22.4) engellendi.
- Yeni 20: temelde en büyük ALGO 2024-11-08 +33.9 (engellendi), yenide FIL 2021-03-03 +32.6; en büyük hariç +0.43 → +0.83, en büyük 5 hariç -0.08 → +0.26. Yeni 20'de iyileşme tek işlemden değil, ama 2024-02 ve 2024-11'deki iki yükselişte yer değişiminden.
- Coin bazında fark (R, yeni − temel): 16'da SOL **-60.6**, BTC **-34.1**, BCH -7.3, TRX -3.5 (XRP +13.6, BNB +4.1, LINK +3.9); 20'de ALGO **-37.8**, UNI **-19.4**, DASH -9.7 (NEAR +33.9, MANA +16.4, ENJ +12.7, XTZ +12.4, VET +11.1).

## İleriye bakma kontrolü
- Şart her coinin sadece karar anından (sinyal mumunun kapanışı) önce ya da tam o anda kapanmış günlük mumunu kullanıyor; coinin kendi puanı ile aynı kural. Günlük mumu tam o gün olmayan coin sayılmıyor (eski veri ileri taşınmıyor).
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_breadth_counts_closed_daily_scores_of_listed_coins_only`): 20:00 mumu (gece yarısı kapanan) o günün günlük mumunu, 16:00 mumu bir önceki günü görüyor; ısınmadaki ve verisi bitmiş coin sayılmıyor; ms ve ns zaman birimi aynı sonucu veriyor; her coinin verisi karar gününden sonra kesilince sonuç değişmiyor; liste `dp.current_whitelist()`'ten; %49 engelliyor, %50 geçiyor, NaN engelliyor.
- Veriyle kontrol: her iki listede rastgele 300 karar anında, her coinin günlük verisi son kapanmış mumda kesilip genişlik yeniden hesaplandı: **0 fark**.
- Backtest çıktısıyla kontrol: her işlem için sinyal mumu = dolumdan önce kapanmış, en fazla 3 mum geride, "ilk kırılım" olan mum (438 / 339 işlemin hepsinde bulundu; 11 / 9 işlemde iki aday vardı, en yeni aday kullanıldı, sınıflandırma çelişkisi yok). Yeni sürümün bütün girişlerinde genişlik ≥ %50 (en düşük tam %50); engellenen 140 temel girişin hiçbiri yeni sürümde yok.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`. Genişlik her listede kendi coinlerinden (16 / 20 coin) hesaplandı; yeni 20'de BTC yok.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeBreadth --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/breadth_<liste>`. Rapor `scripts/make_report.py --results <zip> --test piyasa_genisligi --out results/2026-10-28_pusula_piyasa_genisligi/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
