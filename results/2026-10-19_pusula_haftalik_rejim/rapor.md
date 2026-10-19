# Kuyruk 10 — Pusula rejimi haftalık grafikten — 2026-10-19 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: Pusula trendi günlük grafik yerine **haftalık** grafikten okusa (daha yavaş, daha az işlem) daha iyi olur mu?
- Sonuç: **red**. Eski 16'da açıkça kötü (+1.35R → +0.86R, toplam 311.3R → 179.5R). Yeni 20'de rakam çok iyi görünüyor (+0.61R → +2.41R, toplam 117.7R → 243.6R) ama bunun neredeyse tamamı **tek bir ZEC işleminden** (2025-09-02 → 2025-11-17, +237.1R); o işlem hariç yeni 20'de kalan 100 işlem toplam +6.5R (≈0R). Ayrıca yeni 20'de en büyük düşüş %22.6 → %31.8 (sınır %25).
- Neden ZEC: haftalık sürümde BTC çıkışı da haftalık puana geçti; BTC günlük puanı 2025-09-02'de -1 olup girişi engellerken haftalık puanı +3'tü. Temelde BTC günlük puanı 2025-09-22 ve 2025-10-10'da yine -1'e düşüp işlemi kapatırdı; haftalık BTC puanı 2025-11-10 haftasına kadar ≥ +1 kaldı. Aynı ZEC işlemi 2026-10-13 turunda (BTC çıkışı kaldırılınca) de ortaya çıkmıştı. Yani bu "haftalık rejim" kazancı değil, aynı tek trendin tekrar yakalanması.
- Temel `PusulaV2NoBe` değişmedi. Hile testi temiz.

## Kural (testten önce yazıldı)
`PusulaV2NoBeWeekly(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- **Haftalık mum**: günlük mumlardan üretilir. Hafta pazartesi 00:00 UTC başlar, bir sonraki pazartesi 00:00 UTC kapanır. Sadece 7 günlük mumu tam olan haftalar kullanılır (süren hafta hiç görünmez). 4 saatlik mum, ancak kendi kapanışına kadar kapanmış haftaları görür (pazar 20:00 mumu, kapanışı pazartesi 00:00 olduğu için biten haftayı ilk gören mumdur).
- **Haftalık puan** (formül aynı, mumlar haftalık): haftalık kapanış haftalık EMA50'nin üstü/altı, haftalık EMA20 haftalık EMA50'nin üstü/altı, 13 haftalık (91 gün, 90 günlük getirinin haftalık karşılığı) getiri artı/eksi. Toplam -3..+3. EMA50 için en az 50 hafta veri gerekir; öncesinde puan yok, işlem yok.
- **Giriş**: coinin son kapanmış **haftalık** puanı ≥ +1 (temelde günlük puan ≥ +1). 4h kırılım (önceki 20 mumun tepesi ilk kez geçilir) ve "günlük kapanış günlük EMA20 üstünde" şartı aynı.
- **Çıkışlar**: temelde iki çıkış var. (1) Günlük kapanış günlük EMA20 altı: bu bir rejim puanı değil, 4h işlemin trend çıkışı; **aynı kalır** (günlük). (2) BTC dönüş çıkışı: BTC'nin günlük rejim puanı ≤ -1 → long kapanır. Bu çıkış rejim puanını kullanıyor; **haftalık BTC puanı ≤ -1'e çevrildi**. Neden: bu sürümün fikri rejimi haftalık okumak; coin haftalık, BTC günlük okunursa iki ayrı rejim saati karışır. Ayrıca bu çıkış girişi de engelliyor (çıkış sinyali varken giriş yapılmaz), yani BTC günlük puanı ≤ -1 iken giriş yasağı da haftalık BTC puanına geçer. Sabit stop aynı.
- Başka her şey `PusulaV2NoBe`: sadece long, ortak modül, Model B planı, sabit stop, en fazla 3 işlem.
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R **ve** toplam R daha iyi, DD belirgin kötü değil ve `docs/metrics.md` sınırı (%25) içinde → kabul; aksi halde red. Karar tam dönem (2020-01 → 2026-09) rakamlarıyla verilir.
- Önceden bilinen dezavantaj: veri 2020-01'de başlıyor; haftalık EMA50 için 50 hafta gerektiğinden haftalık puan en erken 2020-12'de (BTC/ETH), geç listelenen coinlerde 2021 ortasında hazır olur. 2020 ve 2021 başı boğasının bir kısmını bu yüzden kaçırması bekleniyor. Bilgi amaçlı, karar için değil: aynı karşılaştırma her coinde haftalık puanın hazır olduğu tarihten sonra açılan işlemlerle de verilecek.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBe (temel) | 230 | +1.35R | 311.26 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | Haftalık rejim | 209 | **+0.86R** | **179.54** | 1.73 | %21.9 | +%308.3 |
| Yeni 20 | PusulaV2NoBe (temel) | 193 | +0.61R | 117.72 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | Haftalık rejim | 101 | +2.41R | 243.60 | 3.61 | **%31.8** | +%252.2 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6). Funding toplamı: eski 16 temel -14077 / haftalık -5874 USDT, yeni 20 temel -3769 / haftalık -1046 USDT. Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R).
Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.

**Karar: red.** Kabul kuralı iki listede de daha iyi ortalama R ve toplam R istiyor. Eski 16'da ikisi de belirgin düştü. Yeni 20'de ikisi de arttı ama DD %31.8 ile %25 sınırını aştı ve kazanç tek işleme bağlı.

## Yoğunlaşma (tek işlem / coin)
- Eski 16: en büyük işlem temelde ETC 2021-03 +94.1R (haftalıkta aynı işlem +47.5R, daha erken çıktı), haftalıkta BNB 2021-01 +53.0R (iki sürümde aynı). En büyük işlem hariç: temel 217.2R (+0.95R), haftalık 126.6R (+0.61R). Coin bazında 6 coin daha iyi, 10 daha kötü; en kötü SOL -62.5R (2023-10 SOL +58.6R işlemi kaçtı), ETC -47.3R, BTC -27.9R, XRP -17.9R; en iyi BNB +21.0R, BCH +10.6R, XLM +9.5R. 100 işlem iki sürümde ortak.
- Yeni 20: haftalığın en büyük işlemi ZEC 2025-09-02 +237.1R (temelde yok); hariç 100 işlem toplam +6.5R, ortalama +0.07R. ZEC coini hariç: temel 119.9R, haftalık 5.9R. Coin bazında 11 coin daha iyi, 9 daha kötü, ama iyileşmelerin ZEC dışındakiler küçük (NEO +12.6R, VET +9.1R); kötüleşmeler büyük (ALGO -40.1R, FIL -38.9R, UNI -29.2R, THETA -28.3R). Temelin en büyük işlemi ALGO 2024-11 +34.5R haftalıkta yok. 51 işlem ortak.
- Yıllara göre (haftalık − temel, toplam R): eski 16 2020 -32.4, 2021 -42.4, 2023 -64.2, 2024 +7.5; yeni 20 2020 -31.5 (haftalık puan hazır değil), 2021 -27.1, 2024 -62.5, 2025 +236.7 (ZEC).

## Haftalık puanın hazır olduğu dönemde (bilgi, karar için değil)
Haftalık EMA50 için 50 hafta gerektiğinden haftalık puan eski 16'da 2020-12-21 ile 2021-09-13, yeni 20'de 2021-01-25 ile 2022-05-02 arasında hazır oldu. Temelin, her coinde haftalık puan hazır olduktan sonra açılan işlemleri:
- Eski 16: temel 184 işlem, +1.51R, toplam 277.4R (hazır olmadan önceki 46 işlem 33.9R) — haftalık 209 işlem, +0.86R, 179.5R. Isınma süresi farkı açıklamıyor; haftalık bu dönemde de kötü.
- Yeni 20: temel 155 işlem, +0.40R, 61.7R (önceki 38 işlem 56.1R) — haftalık 101 işlem, +2.41R, 243.6R; ZEC 2025-09 hariç haftalık +6.5R. Sonuç yine tek işleme bağlı.

## Çıkış türleri
- Eski 16: temel 131 trend/BTC çıkışı (+408.0R), 96 stop (-103.3R), 3 dönem sonu; haftalık 121 trend/BTC çıkışı (+271.7R), 85 stop (-91.0R), 3 dönem sonu.
- Yeni 20: temel 85 trend/BTC çıkışı (+217.8R), 104 stop (-110.4R), 4 diğer; haftalık 43 trend/BTC çıkışı (+305.7R, ZEC dahil), 58 stop (-62.1R).
- Yorum: haftalık rejim daha az işlem açıyor ama girişleri seçmiyor; büyük kazananları (SOL 2023, ALGO 2024, ETC 2021 erken çıkış) kaçırıyor. Haftalık BTC çıkışı daha geç bozulduğu için BTC düşüşünde açık kalan/açılan işlemler var; bunlardan biri ZEC.

## Hile testi
`lookahead-analysis`, BTC/ETH/SOL, 2023-01 → 2024-06, 4h + 1h detay, 15 sinyal: `PusulaV2NoBeWeekly` için **geleceği görme yok** (0 yanlı giriş, 0 yanlı çıkış, 0 yanlı gösterge). Birim testi (`tests/test_pusula.py`): haftalar pazartesi başlıyor, süren hafta atılıyor, pazar 16:00 mumu önceki haftayı, pazar 20:00 mumu (kapanışı pazartesi 00:00) biten haftayı görüyor; veri hafta ortasında kesilince daha önce görünen puanlar değişmiyor.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeWeekly --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --backtest-directory user_data/backtest_results/weekly_<liste>`. Rapor `scripts/make_report.py --results user_data/backtest_results/weekly_<liste>-<zaman>.zip --test haftalik_rejim --out results/2026-10-19_pusula_haftalik_rejim/<liste>`.
- Hile testi: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh lookahead-analysis -c config/pairs_btc_eth_sol.json --strategy-list PusulaV2NoBeWeekly --timeframe 4h --timeframe-detail 1h --timerange 20230101-20240601 --minimum-trade-amount 5 --targeted-trade-amount 15`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
