# Çıkarma turu 5 — "BTC dönünce long'u kapat" kuralı kaldırıldı — 2026-10-13 (temel: PusulaV2NoBe)

## GUO'ya not
- Bitcoin'in günlük puanı -1 veya altına düşünce açık long'ları kapatan kuralı çıkardım (`PusulaV2NoBeNoBtcExit`). Long artık sadece stopta veya günlük kapanış 20 günlük ortalamanın altına inince kapanıyor.
- Önemli yan etki: bu kural aynı zamanda **girişi de engelliyordu** (Freqtrade, çıkış sinyali olan mumda işleme girmiyor). BTC giriş filtresi tur 1'de zaten çıkarılmıştı; yani bu kural gidince BTC puanı -1/-3 iken de long açılıyor. Değişikliğin çoğu bu yeni girişlerden geliyor (eski 16'da 75 yeni işlemin 73'ü, yeni 20'de 35 yeni işlemin 35'i BTC puanı ≤ -1 iken açıldı).
- Eski 16'da **kötüleşti**: +1.35R → +1.01R, toplam 311.3R → 279.0R (DD daha iyi: %23.7 → %18.0).
- Yeni 20'de kâğıt üstünde çok iyi (+0.61R → +1.31R), ama DD %22.6 → **%38.6** ve kazancın tamamı **tek işlemden**: ZEC 2025-09 → 2025-11, +186R. Bu işlem olmasa yeni 20'de de kötüleşme var.
- Karar: **red**. Kural kalıyor. Temel hâlâ `PusulaV2NoBe`. Kuyruktaki çıkarma listesi bitti.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBe (temel) | 230 | +1.35R | 311.26 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | BTC-dönüş çıkışı yok | 276 | **+1.01R** | **278.99** | 1.95 | %18.0 | +%723.4 |
| Yeni 20 | PusulaV2NoBe (temel) | 193 | +0.61R | 117.72 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | BTC-dönüş çıkışı yok | 220 | +1.31R | 287.71 | 2.59 | **%38.6** | +%483.9 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6). Yeni 20'de yeni sürüm al-tutun üstünde (+%483.9), ama bu tek ZEC işleminden.
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: red.** Eski 16'da hem ortalama R hem toplam R düştü (kabul kuralı iki listede de "aynı ya da daha iyi" istiyor). Yeni 20'de DD 16 puan arttı ve %25 sınırını açıkça aştı (`docs/metrics.md`).

## Ne değişti
`PusulaV2NoBeNoBtcExit(PusulaV2NoBe)`: sadece `populate_exit_trend` değişti; BTC-dönüş çıkışı (tur 2a: son kapanmış günlük BTC puanı ≤ -1 ise long'u kapat) kaldırıldı. Günlük EMA20 trend çıkışı ve sabit stop aynı. Giriş koşulları kod olarak aynı (günlük kapanış EMA20 üstünde, puan ≥ +1, kırılım).

**Girişlere etkisi:** Freqtrade aynı mumda çıkış sinyali varken girmez. Temel sürümde BTC puanı ≤ -1 olan her mumda çıkış sinyali vardı, bu yüzden o günlerde hiç long açılmadı (kontrol: temelde BTC puanı ≤ -1 iken açılan işlem sayısı **0**, iki listede de). BTC giriş filtresi tur 1'de çıkarıldığı için, bu çıkış gidince BTC zayıfken de long açılıyor:
- Eski 16: yeni sürümde 75 işlem temelde yok; 73'ü BTC puanı ≤ -1 iken açıldı; bu 73 işlemin toplamı **+0.9R** (yani sıfır civarı, sadece kasayı meşgul ediyor).
- Yeni 20: 35 işlem temelde yok; 35'i de BTC puanı ≤ -1 iken açıldı; toplam +166.0R, ama bunun +186.4R'si tek ZEC işlemi; ZEC hariç bu 34 işlem **-20.4R**.

Yani bu tur aslında iki şeyi birlikte test etti: "BTC dönünce kapat" çıkışı ve (dolaylı olarak) "BTC zayıfken girme". İkisi birlikte çıkınca iki listede de tutarlı bir iyileşme yok.

Çıkış türleri: eski 16'da stop %41.7 → %41.7, sinyal çıkışı %58.3 → %58.3 (oranlar aynı, işlem sayısı arttı). Yeni 20'de stop %53.9 → %55.0. Funding maliyeti azaldı (eski 16: -14.1k → -11.3k USDT; yeni 20: -3.8k → -1.8k USDT).

## Ayarlar (tur 1-4 ile aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeNoBtcExit --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades`, rapor `scripts/make_report.py`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2NoBe) rakamları tur 3/4 raporlarıyla birebir aynı çıktı (230 / 193 işlem, 311.26R / 117.72R, DD %23.7 / %22.6), yani ayarlar doğru kopyalandı.
- Not: bu dönem kasayı (2026-04 → 2026-09) da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
- BTC puanı kontrolü: işlem açılış zamanından bir gün önceki (son kapanmış) günlük BTC mumunun Pusula puanı; temelde bu yöntemle 0 işlem bulunması hizalamanın doğru olduğunu gösteriyor.

## Coin bazında dağılım
Coin bazında toplam R farkı (yeni − temel):
- Eski 16: 8 coin daha iyi, 8 coin daha kötü. Toplam fark -32.3R. En kötü: ETC **-46.0R** (tek işlem: 2021-03-30 açılış; temelde BTC dönünce 2021-05-15'te +94.1R ile kapandı, yeni sürümde EMA20'yi beklerken 2021-05-19 çöküşüne yakalandı ve 2021-05-20'de +47.5R ile kapandı), XRP -4.8R, XLM -3.8R, BCH -3.5R. En iyi: LINK +7.2R (çoğu 2026-08 tek işlem, BTC puanı -3 iken açıldı), TRX +7.1R, LTC +3.8R, SOL +3.5R. ETC hariç fark +13.7R; yani bu listede kural en büyük çöküşte bir kez çok işe yaradı, diğer zamanlarda hafif maliyetli.
- Yeni 20: 4 coin daha iyi, 10 coin daha kötü, 6 coin aynı. Toplam fark +170.0R. ZEC tek başına **+184.6R** (tek işlem: 2025-09-02 → 2025-11-22, +186.4R; BTC puanı -1 iken açıldı, yani temelde hiç açılamazdı). ZEC hariç fark **-14.6R**. En kötü: AAVE -7.1R, NEAR -4.2R, DASH -4.2R. Diğerleri CHZ +4.4R dışında küçük.
- Her sürümün kendi en büyük tek işlemi çıkarılınca: eski 16'da temel 217.2R (ETC hariç), yeni 220.4R (SOL hariç), fark yok; yeni 20'de temel 83.2R (ALGO hariç), yeni 101.3R (ZEC hariç). Coin bazında doğrudan karşılaştırma (ZEC hariç -14.6R) daha adil: aynı coinler, aynı işlemler.
- Yıllara göre (yeni − temel): yeni 20'de 2025 +189.0R (ZEC), 2022 -12.9R, 2023 -2.5R, 2024 -3.5R; eski 16'da 2021 -53.6R (ETC), 2022 -13.6R, 2023 +13.9R, 2024 +9.8R, 2026 +13.7R.
- Not: ZEC işlemi doğrulama dönemi (2025-01 → 2026-03) içinde. Bu, geliştirme sırasında doğrulama verisini de gördüğümüz anlamına gelir; önceki turlar da aynı aralığı kullandığı için yeni bir ihlal değil, ama kararı değiştirmeye kullanılmadı.
- Yorum: kuralı çıkarmak iki listede tutarlı bir şey kazandırmıyor; kazanç ve kayıp birer dev işleme bağlı (eski 16'da ETC kaybı, yeni 20'de ZEC kazancı). BTC zayıfken açılan ek işlemler ZEC hariç sıfır ya da eksi. Kural kalıyor.
