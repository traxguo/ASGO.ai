# Kuyruk 12 — çıkarma: 4h kırılım tetiği kaldırıldı — 2026-10-21 (temel: PusulaV2NoBe)

## Kural (testten önce yazıldı)
`PusulaV2NoBeNoBreakout(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Temelin long şartlarından sadece **4h kırılım** (`breakout_up`: 4h kapanış önceki 20 mumun tepesinin üstünde, ilk mum) çıkarıldı.
- Kalan şartlar aynı: son kapanmış günlük puan ≥ +1 (`regime_up`), son kapanmış günlük kapanış günlük EMA20'nin üstünde (`daily_above_ema20`), ortak modülün plan kontrolü (stop mesafesi ≤ %8). Çıkış sinyali varken (günlük kapanış EMA20 altı veya BTC günlük puanı ≤ -1) giriş yok, temelde olduğu gibi.
- Giriş sinyali artık bu şartların sağlandığı **her** 4h mumda var: şartların ilk sağlandığı 4h mum ve şartlar sürerken o coinde açık işlem yoksa sonraki herhangi bir 4h mum (ör. stop sonrası hemen, ya da yer boşalınca). Coin başına tek işlem, ekleme yok (aynı).
- **Stop ve 1R aynı**: temelde stop zaten kırılım seviyesine bağlı değil. Stop = giriş ortası − 1.5 ATR ile son 10 mumun dibinin (tampon dahil) daha geniş olanı; giriş ortası = sinyal mumu kapanışı − 0.125 ATR (0.25 ATR'lik giriş bölgesinin ortası). Hepsi sinyal mumundan. Bu yüzden 1R'nin anlamı temelle birebir aynı.
- Çıkışlar aynı: sabit stop, günlük EMA20 çıkışı, BTC-dönüş çıkışı. Sadece long, en fazla 3 işlem, işlem başına %1 risk.
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R ve toplam R aynı ya da daha iyi, DD belirgin kötü değil ve `docs/metrics.md` sınırı (%25) içinde → **kabul** (kırılım kuralı çıkar); aksi halde **red**. Tek işlem / tek coin yoğunlaşması önceki turlar gibi kontrol edilir.
- Not: stopun tanımı aynı, ama giriş artık kırılım anında değil, trendin herhangi bir yerinde olduğu için stop mesafeleri farklı dağılıyor (eski 16 ortalama %5.4 → %4.1, yeni 20 %6.3 → %5.1).

## GUO'ya not
- Soru: Pusula'nın kârını 4 saatlik kırılım mı getiriyor, yoksa sadece günlük yükseliş trendinde bulunmak mı?
- Cevap: **kırılım getiriyor.** Kırılımı kaldırıp "günlük trend yukarıdaysa her an gir" deyince işlem sayısı 3 katından fazla arttı, ama işlem başına kazanç çöktü, düşüş sınırın çok üstüne çıktı. Eski 16'da hesap +%827 yerine +%177, düşüş %24 yerine %49; yeni 20'de +%134 yerine **-%9**, düşüş %23 yerine **%83**.
- **Karar: red.** Kırılım kuralı kalıyor; temel `PusulaV2NoBe` değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | PF | Max DD | Net | Funding (USDT) |
|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel (kırılımlı) | 230 | +1.35R | 311.26 | +1.34 / 308.7 | 2.06 | %23.7 | +%827.3 | -14077 |
| Eski 16 | kırılımsız | 654 | **-0.78R** | -510.28 | +0.32 / 210.2 | 1.22 | **%48.6** | +%177.4 | -8969 |
| Yeni 20 | temel (kırılımlı) | 193 | +0.61R | 117.72 | +0.60 / 115.8 | 1.53 | %22.6 | +%134.2 | -3769 |
| Yeni 20 | kırılımsız | 737 | **-0.23R** | -171.23 | +0.09 / 66.5 | 0.99 | **%82.9** | **-%8.7** | -8154 |

- Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5, yeni 20 +%194.7.
- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R).
- **Ölçüm uyarısı (R):** kırılımsız sürümde eski 16'da 19, yeni 20'de 20 işlem, stop vurulduktan sonra **aynı 4h sinyal mumuyla** 1 saatlik detayda hemen yeniden açıldı ve dolum fiyatı planlanan stopun üstünde ≤ %0.2 ya da altındaydı. Bu işlemlerde giriş − stop farkı neredeyse sıfır olduğu için `make_report.py`'nin R hesabı (kâr / (miktar × |dolum − stop|)) çok büyük eksi R üretiyor (ör. LTC 2020-06 -584R, gerçek kayıp 68 USDT). Bunlar USDT olarak küçük (16: -2539 USDT, 20: -1638 USDT) ama R toplamını 16'da -698R, 20'de -213R bozuyor. Bu yüzden iki sağlam ölçü de verildi:
  - **Hesap-R**: kâr / (işlem açılırken sermayenin %1'i). Temelde R ile neredeyse aynı (1.34 vs 1.35, 0.60 vs 0.61).
  - Bu işlemler hariç R: eski 16 635 işlem **+0.30R** (187.4R), yeni 20 717 işlem **+0.06R** (41.4R).
  - Hangi ölçüyle bakılırsa bakılsın kırılımsız sürüm iki listede de çok kötü; karar ölçüme bağlı değil. Hesap düzeyi rakamlar (net, DD) bu sorundan etkilenmiyor.
  - Bu davranış kuralın kendisinden geliyor (sinyal sürerken boş coinde hemen giriş), sonradan düzeltilmedi.

**Karar: red.** Kabul kuralı iki listede de ortalama R ve toplam R'nin aynı ya da iyi olmasını, DD'nin sınır (%25) içinde kalmasını istiyor. İki listede de ortalama R, toplam R (hangi ölçüyle olursa olsun) ve net getiri belirgin düştü; DD 16'da %48.6, 20'de %82.9 (sınırın çok üstü).

## Yoğunlaşma (tek işlem / coin)
- Eski 16: kırılımsız sürümün en büyük işlemi SOL 2023-10-16 +145.5R (hesap-R +143.9); sorunlu dolumlar hariç toplam 187.4R'nin %78'i. O da hariç ≈ +0.07R/işlem. Coin bazında (hesap-R) 7 coin iyi, 9 kötü; en büyük kayıplar ETC -102.6 (temelin ETC 2021-03 +94R işlemi kaçtı), BNB -81.0, BTC -19.3; en büyük iyileşme SOL +84.5 (tek işlem). Yıllara göre 2021 162.6 → 58.3, 2022 -6.6 → -45.1, 2023 85.4 → 145.9 (SOL).
- Yeni 20: en büyük işlem UNI 2020-12-29 +61.6R; sorunlu dolumlar hariç toplam 41.4R, en büyük işlem de hariç ≈ -0.03R/işlem. Coin bazında 6 coin iyi, 14 kötü (ALGO -32.7, THETA -25.6, FIL -24.7); iyileşme UNI +40.6, NEAR +34.9, VET +23.4. Yıllara göre 2020 31.3 → 113.2 (boğa başı, her an girmek işe yaradı), sonra 2022 -28.2, 2023 -52.4, 2025 -52.4.
- Yorum: trendde herhangi bir anda girince stopla biten işlem payı eski 16'da %41.7 → %51.7 (yeni 20'de %53.9 → %54.0), kazanma oranı %32 → %21 (16), %23 → %18 (20); işlemler de daha kısa (ortalama süre 16'da 11.4 → 5.4 gün, 20'de 8.1 → 4.0 gün). Kırılım, trendin "şimdi hızlanıyor" anını seçiyor; kâr bu seçimden geliyor. Tek iyi sonuç 2020-21 boğasında ve tek işlemlerde.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeNoBreakout --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --backtest-directory user_data/backtest_results/nobrk_<liste>`. Rapor `scripts/make_report.py --results <zip> --test kirilimsiz --out results/2026-10-21_pusula_kirilimsiz/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`. Not: alt raporlardaki "Ortalama R" yukarıdaki ölçüm uyarısındaki sorunu içerir.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x. Hile testi gerekmedi: yeni sınıf sadece bir giriş şartını siliyor, yeni gösterge yok.
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
