# Kuyruk 23 — giriş emri: sinyalden sonraki mumun açılışında piyasa emri — 2026-11-01 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: kırılım sinyalinden sonra fiyatın biraz geri gelmesini (limit emir) beklemek yerine, bir sonraki 4 saatlik mum açılır açılmaz piyasa emriyle girsek, kaçan güçlü kırılımları yakalayıp daha çok kazanır mıyız?
- Cevap: **hayır.** Eski 16'da sonuç neredeyse aynı, yeni 20'de daha kötü.
  - Eski 16: ortalama +1.35R → +1.36R, toplam 311.3R → **307.2R**, net +%827 → +%832, DD %23.7 → %23.0.
  - Yeni 20: ortalama +0.61R → **+0.54R**, toplam 117.7R → **103.7R**, net +%134 → **+%115**, DD %22.6 → %21.9.
- Ne oluyor, üç etki var:
  1. **Kazanılan:** temelde dolmadan iptal olan sinyaller (14 / 12 tane) artık doluyor. Bunlar gerçekten iyi: +24.1R / +36.9R (ör. LINK 2020-06 +14.7R, ICP 2023-12 +28.4R).
  2. **Kaybedilen:** her işlemde giriş biraz daha pahalı (ortalama %0.23 / %0.31). Her iki sürümün de aldığı işlemlerde bu toplam -19.6R / -12.3R ediyor. Neredeyse tamamı büyük kazananlardan geliyor (ETC 2021-03 +94.1 → +90.2R gibi).
  3. **Kaybedilen:** açılış fiyatı daha yukarıda olduğu için stop mesafesi bazen %8 sınırını aşıyor, o sinyal alınmıyor (10 / 23 sinyal). Temel bunların 8 / 21'ini almıştı: +60.0R / +50.0R (BNB 2021-01 +53.0R, FIL 2021-03 +33.0R).
- **Karar: red.** Yeni 20'de üç şart da kötü, eski 16'da toplam R kötü. Temel `PusulaV2NoBe` değişmedi, limit emir kalıyor.

## Kural (testten önce yazıldı)
`PusulaV2NoBeMarketEntry(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Giriş, sinyal mumundan sonraki 4h mumun **açılışında piyasa emri**. Temelde giriş, giriş bölgesinin ortasında (kapanış − 0.125 ATR) bekleyen limit emirdi; 3 mum içinde dolmazsa ya da önce stop gelirse iptal oluyordu.
- Stop seviyesi aynı (sinyal mumunda hesaplanan, `enter_tag` içindeki stop). R gerçek giriş fiyatından hesaplanıyor.
- Gerçek girişe göre stop mesafesi %8'i aşarsa (ya da fiyat zaten stopun altındaysa) giriş yok.
- Aynı kalanlar: sinyaller, çıkışlar (günlük EMA20, BTC-dönüş), %1 risk, en fazla 3 işlem, emir başına %0.1 maliyet. Eşik yok, tarama yok.
- **Kabul kuralı** (önceden): iki listede de ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → kabul; aksi halde red.

## Nasıl kodlandı
- **Ortak modül (`strategies/common/`) nasıl çalışıyor:** sinyal mumunda plan sütunları yazılıyor: `long_entry` (bölge ortası), `long_stop` (bölge ortası − 1.5 ATR ile 10 mum dibi − 0.1 ATR'den daha aşağıda olanı), `long_plan_ok` (bölge ortasına göre stop ≤ %8). Kaldıraç ve pozisyon büyüklüğü temelde **bölge ortasından** hesaplanıyor. Stop `custom_stoploss`'ta plandan okunuyor.
- **Yeni sınıfta değişen:**
  - `order_types["entry"] = "market"`.
  - Kaldıraç (`leverage`) ve büyüklük (`custom_stake_amount`) Freqtrade'in verdiği **gerçek fiyattan** (`current_rate`) hesaplanıyor. Backtestte bu, sinyalden sonraki mumun açılışı, yani dolum fiyatı. Büyüklük = sermaye × %1 / ((giriş − stop) / giriş). Böylece stop vurulursa yine sermayenin %1'i kaybediliyor.
  - Aynı yerde stop mesafesi gerçek girişe göre yeniden kontrol ediliyor: %8'den fazlaysa veya giriş ≤ stop ise büyüklük 0, Freqtrade sinyali atlıyor. Atlananlar bir dosyaya yazılıyor (`PUSULA_SKIP_LOG`).
  - Sinyal mumları birebir aynı: aynı plan sütunları ve aynı `plan_ok` süzgeci kullanılıyor, stop seviyesi temeldeki seviyenin aynısı.
- **R:** `scripts/make_report.py` R'yi kâr / (giriş miktarı × |gerçek giriş fiyatı − stop|) olarak hesaplıyor; yani zaten gerçek dolumdan. Ortak modülde değişiklik gerekmedi.
- **Dolum anı:** Freqtrade backtestte sinyali bir mum kaydırıyor. Piyasa emrinin fiyatı o mumun açılışı (`custom_entry_price` sadece limit emirde çağrılıyor) ve açılış mumun aralığında olduğu için hemen doluyor. Kontrol: yeni sürümün 226 / 192 işleminin hepsinde dolum fiyatı = sinyalden sonraki 4h mumun açılışı, dolum zamanı = mumun başlangıcı, sinyal bir önceki mumda ve stop o mumdaki `long_stop` ile aynı (0 hata).
- **Önemli bulgu (ilk çalıştırmada görüldü, düzeltildi):** Freqtrade bir 4h sinyali o mum boyunca geçerli sayıyor ve `--timeframe-detail 1h` ile her saat yeniden girmeyi deniyor (canlıda her döngüde). İlk çalıştırmada bu yüzden:
  - stop sınırı yüzünden atlanan BNB 2021-01-29 sinyali 3 saat sonra, fiyat biraz geri gelince alındı;
  - yer açılınca bazı girişler mumun ortasında oldu.
  Bu "açılışta piyasa emri" kuralı değil. Düzeltme: `ignore_buying_expired_candle_after = 1800` (giriş sadece mumun ilk 30 dakikasında; backtestte sadece ilk 1 saatlik detay mumu, onun açılışı da 4h açılışı). Açılışta girilemeyen sinyal (yer dolu, coinde açık işlem, stop > %8) düşüyor. Temelin limit emri ise mumun ortasında da verilebiliyor (temelde 5 / 1 işlem böyle).
  - İlk (düzeltilmemiş) sürümün sonucu da reddediliyordu: 16'da 230 işlem, +1.34R, 307.4R, net +%831.0, DD %23.9; 20'de 197 işlem, +0.57R, 111.7R, net +%129.5, DD %23.3.
- **Ayar:** Freqtrade piyasa giriş emrinde `entry_pricing.price_side = "other"` istiyor. Bunun için `config/entry_market.json` eklendi ve iki strateji aynı komutla çalıştı. Backtest fiyatı mumdan aldığı için bu ayar temeli değiştirmiyor (temel birebir aynı çıktı).
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_market_entry_sizes_from_fill_and_skips_wide_stop`). Kontrol edilenler:
  - giriş emri piyasa, temelinki limit; sinyal, stop, çıkış metodları temelinkiyle aynı;
  - büyüklük gerçek dolumdan: stop vurulursa kayıp tam %1;
  - stop %8'den uzaksa ya da fiyat stopun altındaysa giriş yok;
  - giriş sadece sinyalden sonraki mumun ilk saatinde.
  226 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel (limit) | 230 | +1.353R | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.4 | +%931.5 |
| Eski 16 | açılışta piyasa | 226 | **+1.359R** | **307.21** | +1.345 / 303.9 | **+%831.7** | %23.03 | 2.12 | %33.2 | -13739 | 11.5 | +%931.5 |
| Yeni 20 | temel (limit) | 193 | +0.610R | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | açılışta piyasa | 192 | **+0.540R** | **103.74** | +0.535 / 102.8 | **+%115.5** | %21.87 | 1.52 | %23.4 | -3209 | 8.0 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R; +%827.3 / +%134.2).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem. Eski 16'da iki sürüm de al-tutun biraz altında, yeni 20'de belirgin altında (ama DD %22-24'e karşı al-tut %89 / %98).
- Ortalama stop mesafesi (gerçek girişe göre) 16'da %5.37 → %5.48, 20'de %6.28 → %6.39. Kaldıraç ortalaması iki sürümde de 3x.
- Eski 16'da net biraz yükseldi ama toplam R ve hesap-R toplamı düştü: kazanç sırası değişti (BNB 2021-01 işlemi bir gün sonra, daha büyük bir hesapla açıldı), toplam R'de bir iyileşme yok.

**Karar: red.**
- Eski 16: ortalama R (+1.353 → +1.359), net (+%827.3 → +%831.7) ve DD (%23.03) tuttu. Toplam R tutmadı (311.26 → 307.21).
- Yeni 20: ortalama R (+0.610 → +0.540), toplam R (117.72 → 103.74), net (+%134.2 → +%115.5) üçü de kötü. Sadece DD şartı tuttu (%21.87).

## Fark nereden geliyor (toplam R farkının parçaları)
İşlemler coin + açılış zamanıyla eşleştirildi.

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| İkisinin de aldığı işlemler (sadece giriş fiyatı farklı) | 202 | **-19.64** | 162 | **-12.30** |
| Temelde dolmadan iptal olan, şimdi dolan sinyaller | +14 | **+24.15** | +12 | **+36.91** |
| Stop > %8 yüzünden alınmayan sinyaller (temeldeki R) | -8 | **-60.04** | -21 | **-49.99** |
| Yer etkisi: temelde coinde açık işlem vardı, şimdi girildi | +6 | +51.35 | +5 | +11.83 |
| Yer etkisi: temelde 3 yer doluydu, şimdi girildi | +4 | +0.04 | +13 | +3.85 |
| Yer etkisi: şimdi coinde açık işlem var, temeldeki giriş yok | -8 | -9.32 | -4 | +0.81 |
| Yer etkisi: şimdi 3 yer dolu, temeldeki giriş yok | -7 | +6.10 | -5 | -4.24 |
| Temelin mum ortasında verdiği emirler (yeni sürümde yok) | -5 | +3.32 | -1 | -0.84 |
| **Toplam fark** | 230 → 226 | **-4.05** | 193 → 192 | **-13.98** |

(Kaybedilen satırlarda işaret, toplam R'ye etkisi: temelde +60.04R yapan işlemlerin kaybı -60.04R.)

### Temelde iptal olan sinyallerin yeni sürümdeki R'si
- Temelde süresi dolup iptal olan giriş emri: 14 / 13 (Freqtrade sayacı). Sinyallerin ≈ %6'sı (kuyruktaki %5.7 / %6.3 ile aynı).
- Bunlardan yeni sürümde girilen: **14 işlem +24.15R** (ort. +1.73R) / **12 işlem +36.91R** (ort. +3.08R). İki listede de ortalamanın üstünde. Kuyruğun tahmini doğru: geri çekilmeden giden kırılımlar iyi.
  - Eski 16: LINK 2020-06-22 +14.7, TRX 2026-05-02 +5.6, TRX 2023-10-16 +3.4, BTC 2020-04-29 +3.3; 7'si eksi bitti (4'ü stopla).
  - Yeni 20: ICP 2023-12-01 +28.4, DASH 2021-02-03 +10.3, CHZ 2024-01-15 +1.8; 7'si eksi bitti (2'si stopla).
- 1 saatlik veriyle bağımsız kontrol: bu sinyallerin 13 / 12'sinde fiyat 3 mum boyunca bölge ortasına hiç inmedi. Eski 16'daki 1 tanesi (TRX 2021-08-16) bu basit kontrolde dolmuş görünüyor; temelde neden alınmadığı ayrıca çözülmedi (-1.03R, sonuca etkisi küçük).
- Ama bu kazanç, aşağıdaki iki kayıptan küçük.

### İkisinin de aldığı işlemler: giriş fiyatı ve R farkı
| Liste | İşlem | Giriş fiyatı farkı (ort. / ortanca) | Stop mesafesi | R farkı (toplam / ort.) | Kazananlarda | Kaybedenlerde |
|---|---|---|---|---|---|---|
| Eski 16 | 202 | +%0.234 / +%0.226 | %5.25 → %5.47 | **-19.64 / -0.097** | 65 işlem -18.73R | 137 işlem -0.91R |
| Yeni 20 | 162 | +%0.312 / +%0.299 | %6.12 → %6.42 | **-12.30 / -0.076** | 35 işlem -11.74R | 127 işlem -0.56R |

- Çıkışların hepsi aynı anda ve aynı sebeple. Fark sadece giriş fiyatından.
- Stopla biten işlem yine ≈ -1.07R (risk gerçek girişe göre ayarlandığı için). Kayıp kazananlarda: aynı fiyat hareketi, daha geniş R ile bölününce daha az R ediyor.
- En büyük farklar: ETC 2021-03 +94.1 → +90.2R, SOL 2023-10 +58.6 → +56.4R, BTC 2023-10 +22.6 → +21.2R (16); ALGO 2024-11 +34.5 → +32.0R, UNI 2024-02 +26.1 → +24.6R, THETA 2020-12 +24.1 → +22.4R (20).

### Stop mesafesi yüzünden alınmayan girişler
- Eski 16: **10** sinyal atlandı (açılışa göre stop %8.05 - %8.30). Temel bunların 8'ini almıştı: **+60.04R**.
  - BNB 2021-01-29 +53.0R (yeni sürüm aynı trende bir gün sonra yeniden kırılımda girdi: +56.9R; yer etkisi satırında).
  - Diğer 7: +7.0R (AVAX 2026-09 +4.4, ETC 2021-02 +3.3, ETH 2021-08 +1.7; 3'ü eksi).
- Yeni 20: **23** sinyal atlandı (%8.03 - %8.36). Temel bunların 21'ini almıştı: **+49.99R**.
  - FIL 2021-03-03 +33.0R, VET 2020-06-08 +14.4R (yeni sürüm VET'e 2020-07'de girdi, +11.1R), NEO 2021-02 +5.7R, EGLD 2023-11 +3.3R. 14'ü eksi bitmişti (10'u stopla); kazanç birkaç büyük işlemden.
- Hepsi sınırın hemen üstünde: temelde bölge ortasına göre stop ≤ %8'di, açılış ortalama %0.2-0.3 yukarıda olunca %8'i geçti. Bu sinyaller en oynak anlardaki kırılımlar ve bazıları en büyük trendlerin başı.

### Yer etkisi (boşalan / kaybedilen yerler)
- Eski 16: net +51.5R (mum ortası emirler dahil). Neredeyse tamamı BNB 2021-01: aynı trendde temel 01-29'da girdi (+53.0R), yeni sürüm o sinyali atladı ve 01-30'daki yeniden kırılımda girdi (+56.9R). İkisi birlikte: +3.9R.
- Yeni 20: net +11.4R (mum ortası emirler dahil; VET 2020-07 +11.1R, VET 2021-04 +9.2R girdi; VET 2023-12 +7.8R kaçtı).
- Yer etkisinin işareti iki listede de rastlantısal (önceki turlardaki gibi). Asıl fark yukarıdaki iki kayıp.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | Eski 16 temel | Eski 16 piyasa | Yeni 20 temel | Yeni 20 piyasa |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +54.2 (44) | +31.5 (29) | +28.8 (26) |
| 2021 | +164.3 (32) | +150.7 (36) | +41.7 (27) | **+21.2** (28) |
| 2022 | -6.6 (7) | -6.6 (7) | -3.0 (6) | -5.2 (5) |
| 2023 | +86.7 (38) | +82.6 (37) | -1.9 (39) | **+13.1** (41) |
| 2024 | +10.0 (57) | +11.9 (54) | +64.9 (36) | +62.4 (37) |
| 2025 | +15.5 (31) | +14.7 (30) | -19.8 (41) | -18.7 (40) |
| 2026 | -3.1 (19) | -0.2 (18) | +4.3 (15) | +2.2 (15) |

- Yeni 20'deki büyük kayıp 2021 (-20.5R; FIL 2021-03 +33.0R stop sınırı yüzünden kaçtı). 2023 iyileşmesi (+15.0R) neredeyse tek işlemden: ICP 2023-12 +28.4R (temelde dolmamıştı).
- Eski 16'da 2020 +9.8R (LINK 2020-06 doldu), 2021 -13.6R (giriş fiyatı farkı ETC / TRX'te ve BNB kayması).
- Doğrulama + kasa dönemi (2025-2026): 16'da +12.4 → +14.5R, 20'de -15.5 → -16.5R. Bir yönde net bir fark yok.

## Yoğunlaşma (tek işlem)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 (+94.1 → +90.2R, hesap-R +93.1 → +89.3). En büyük hariç hesap-R ortalaması +0.941 → +0.954, en büyük 5 hariç +0.277 → +0.282. Yeni sürümün en büyük 5'i: ETC 2021-03 +90.2, BNB 2021-01 +56.9, SOL 2023-10 +56.4, BTC 2023-10 +21.2, BTC 2024-01 +19.5.
- Yeni 20: en büyük iki sürümde de ALGO 2024-11 (+34.5 → +32.0R). En büyük hariç +0.426 → **+0.372**, en büyük 5 hariç -0.078 → -0.078. Yeni sürümün en büyük 5'i: ALGO 2024-11 +32.0, ICP 2023-12 +28.4, UNI 2024-02 +24.6, THETA 2020-12 +22.4, VET 2020-07 +11.1.
- Eski 16'daki küçük "ortalama R iyi" sonucu tek işleme bağlı değil ama çok küçük (+0.006R). Yeni 20'deki kötüleşme de tek işlemden değil: en büyük işlem hariç de kötü.

## İleriye bakma kontrolü
- Sinyal ve stop sinyal mumunun kapanışında belli; giriş fiyatı bir sonraki mumun açılışı. Karar anında bilinmeyen bir şey kullanılmıyor.
- Veri kesme testi: her listede 300 an (150 rastgele 4h mum, 150 tanesi giriş sinyali olan mum). Her anda her coin için stratejinin kendi `populate_indicators` + giriş + çıkış kodu iki kez çalıştırıldı: tam veriyle ve o anda kesilmiş veriyle. Giriş sinyali, çıkış sinyali, `long_stop`, `long_entry`, `long_plan_ok` karşılaştırıldı.
  - Eski 16: 300 an, 4728 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5656 kontrol, **0 fark**.
- Dolum kontrolü (backtest işlemlerinden): 226 / 192 işlemin hepsinde sinyal bir önceki 4h mumda, stop o mumun `long_stop`'u, dolum fiyatı giriş mumunun açılışı. 0 hata.

## Uyarılar
- Maliyet iki sürümde de emir başına %0.1 (kuyruğun istediği gibi). Gerçekte piyasa emri "taker" ücreti öder, limit emir çoğu zaman daha ucuz "maker" ücreti. Yani gerçek hayatta yeni sürüm biraz daha da kötü olurdu.
- Canlıda (GitHub Actions gecikmeli çalışıyor) "açılışta" girmek her zaman mümkün değil; 30 dakika sınırı bu yüzden canlıda bazı sinyalleri düşürebilir. Backtest bunu görmez.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`. Ek: `config/entry_market.json` (sadece `entry_pricing.price_side = "other"`).
- Komut: `PUSULA_SKIP_LOG=<dosya> FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --config config/entry_market.json --strategy-list PusulaV2NoBe PusulaV2NoBeMarketEntry --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/mktentry_<liste>`. Rapor `scripts/make_report.py --results <zip> --test acilista_giris --out results/2026-11-01_pusula_acilista_giris/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
