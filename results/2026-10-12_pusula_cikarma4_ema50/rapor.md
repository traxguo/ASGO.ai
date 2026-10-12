# Çıkarma turu 4 — trend çıkışı EMA20 yerine EMA50 — 2026-10-12 (temel: PusulaV2NoBe)

## GUO'ya not
- Trend çıkışını yavaşlattım (`PusulaV2NoBeEma50`): long, günlük kapanış 20 günlük ortalamanın değil **50 günlük ortalamanın** altına inince kapanıyor. Stop ve BTC-dönüş çıkışı aynı.
- Kâğıt üstünde işlem başına sonuç çok arttı: eski 16'da +1.35R → +3.18R, yeni 20'de +0.61R → +1.30R. Toplam R ikisinde de yüksek.
- Ama yeni 20'de en büyük düşüş %22.6 → **%27.8** (%25 sınırının üstüne çıktı) ve PF aynı (1.53 → 1.52). Yeni 20'deki kazancın tamamı **tek işlemden**: THETA 2020-12 → 2021-04 (+135R fark). Bu işlem olmasa yeni 20'de EMA50 daha kötü; 20 coinin 10'u kötüleşti, 6'sı iyileşti.
- Karar: **red**. Kural aynı kalıyor (EMA20 çıkışı). Temel hâlâ `PusulaV2NoBe`.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBe (temel) | 230 | +1.35R | 311.26 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | EMA50 çıkışı | 158 | **+3.18R** | 503.03 | 2.25 | %21.5 | +%1237.3 |
| Yeni 20 | PusulaV2NoBe (temel) | 193 | +0.61R | 117.72 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | EMA50 çıkışı | 166 | **+1.30R** | 215.80 | 1.52 | **%27.8** | +%174.8 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6). Yeni 20'de EMA50 sürümü bile al-tutun gerisinde (+%174.8 vs +%194.7).
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: red.** Ortalama R ve toplam R iki listede de daha iyi, ama yeni 20'de DD 5.2 puan arttı ve %25 sınırını aştı (`docs/metrics.md`); bu "belirgin kötüleşme". Ayrıca yeni 20'deki iyileşme tek bir işleme bağlı (aşağıda).

## Ne değişti
`PusulaV2NoBeEma50(PusulaV2NoBe)`: sadece `populate_exit_trend` değişti; long çıkışı günlük kapanış < günlük EMA50 (önce EMA20). BTC-dönüş çıkışı (BTC puanı ≤ -1) ve sabit stop aynı. Giriş koşulları kod olarak aynı (günlük kapanış EMA20 üstünde, puan ≥ +1, kırılım); ancak Freqtrade aynı mumda çıkış sinyali varken girmediği için günlük kapanış EMA50 altındayken artık giriş olmuyor (önceden de "çıkış kuralı doğruyken girme" ilkesi böyle işliyordu). `PusulaTrendLong`, `PusulaV2`, `PusulaV2NoBe` ve önceki sınıflar değişmedi.

Çıkış türleri: eski 16'da stop %41.7 → %60.1, trend çıkışı %58.3 → %39.9. Yeni 20'de stop %53.9 → %66.9, trend çıkışı %45.6 → %32.5. İşlemler daha uzun açık kalıyor (3 işlem sınırı daha sık dolu → eski 16'da -72, yeni 20'de -27 işlem). Funding maliyeti de arttı (eski 16: -14.1k → -24.4k USDT; yeni 20: -3.8k → -9.5k USDT).

## Ayarlar (tur 1-3 ile aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeEma50 --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades`, rapor `scripts/make_report.py`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2NoBe) rakamları tur 3 raporuyla birebir aynı çıktı (230 / 193 işlem, 311.26R / 117.72R, DD %23.7 / %22.6), yani ayarlar doğru kopyalandı.
- Not: bu dönem kasayı (2026-04 → 2026-09) da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Coin bazında dağılım
Coin bazında toplam R farkı (yeni − temel):
- Eski 16: 8 coin daha iyi, 5 coin daha kötü, 3 coin aynı. Toplam fark +191.8R. En iyi: BNB +104.8R, BTC +38.6R, LINK +29.8R, LTC +16.9R, TRX +12.4R. En kötü: XRP -14.3R, ETC -5.2R, AVAX -3.8R. BNB tek başına farkın yarısından fazlası (tek işlem: 2021-01-29 → 2021-05-15, EMA20 ile 2021-03-25'te kapanmıştı).
- Yeni 20: 6 coin daha iyi, 10 coin daha kötü, 4 coin aynı. Toplam fark +98.1R. THETA tek başına +135.2R (tek işlem: 2020-12-13 → 2021-04-23; EMA20 ile 2021-01-22'de kapanmıştı); THETA hariç fark **-37.1R**. En kötü: ALGO -14.1R, FIL -11.4R, DASH -9.7R, UNI -9.6R.
- En büyük tek işlem çıkarılınca (masrafsız kaba hesap, R = fiyat hareketi / stop mesafesi): yeni 20'de temel ≈111R, EMA50 ≈93R; yani tek işlem dışında EMA50 daha kötü.
- Yorum: EMA50 çıkışı 2020-2021 boğasında birkaç dev trendi daha uzun tutuyor; diğer zamanlarda kazancı geri veriyor ve DD büyüyor. Bu "birkaç işlem ezberi" riskinin ta kendisi; kabul kuralının DD şartı bunu yakaladı.
