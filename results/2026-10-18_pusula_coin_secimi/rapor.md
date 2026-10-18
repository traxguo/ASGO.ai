# Kuyruk 7 — coin seçimi (90 günlük getiriye göre sıralama) — 2026-10-18 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: aynı 4 saatlik mumda boş yerden (en fazla 3 işlem) daha çok coin sinyal verirse, temel sürüm (`PusulaV2NoBe`) Freqtrade'in coin sırasına göre alıyor. Bunun yerine son 90 günde en çok yükselen coini seçmek daha iyi mi?
- Önce ne kadar sık olduğunu ölçtüm: **seyrek**. 6.5 yılda eski 16'da 23 mum, yeni 20'de 16 mum (yılda 2-4 kez). Sıralamanın farklı coin seçtiği an: 16'da 14, 20'de 13. Yani bu kural en fazla birkaç işlemi değiştirebilir.
- Sonuç: eski 16'da biraz **kötü** (+1.35R → +1.32R, toplam 311.3R → 308.0R, DD %23.7 → %25.1, sınırın biraz üstünde), yeni 20'de biraz **iyi** (+0.61R → +0.66R, toplam 117.7R → 128.2R), ama 20'deki kazancın neredeyse hepsi tek bir seçimden (2024-11-08: FIL yerine MANA).
- Karar: **red**. Temel `PusulaV2NoBe` değişmedi.
- Yan bulgu: coin sırasını ters çevirmek (hiçbir kural değişmeden) eski 16'da toplamı 311.3R → 371.4R yapıyor; bunun +66.5R'si tek bir DOGE işleminden (2024-10-14). Yani bugün sonuçlarda "hangi coin listede önce" şansı kabaca ±60R oynatabiliyor; sıralama kuralının etkisi (±10R) bunun çok altında.

## Kural (testten önce yazıldı)
`PusulaV2NoBeRank(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- **Aday**: listede, son kapanan 4h mumda geçerli long sinyali olan (tüm giriş şartları doğru ve aynı mumda çıkış sinyali yok, yani Freqtrade'in gerçekten işleyeceği sinyal), o coinde açık işlem ya da bekleyen giriş emri olmayan, ve o coinde bu 4h mum içinde kapanmış işlem olmayan (Freqtrade böyle coini o mum atlıyor) her coin.
- **Boş yer** = en fazla işlem (3) − açık işlem (bekleyen giriş emri de sayılır).
- Aday sayısı boş yerden fazlaysa sadece **90 günlük getirisi en yüksek** `boş yer` kadar aday girebilir. 90 günlük getiri = son kapanan günlük kapanış / 90 gün önceki günlük kapanış − 1 (rejim puanında kullanılan `mom` değeri). Eşitlikte liste sırası. Aksi halde hiçbir şey değişmez; başka her şey `PusulaV2NoBe`.
- Uygulama: Freqtrade backtestte coinleri sırayla işliyor, bu yüzden kontrol `confirm_trade_entry` içinde: sıra bir coine geldiğinde, aynı mumdaki daha güçlü bir aday yer kapacaksa bu coin reddediliyor; daha güçlü coin sırası gelince giriyor. Kontrol Freqtrade'in giriş deneyeceği her an çalışıyor (1h detay mumunda bir yer boşaldığında da). Sinyaller `populate_exit_trend` içinde bir "sinyal defterine" yazılıyor; kontrol sadece az önce kapanan mumu okuyor, sonraki mumlara bakmıyor.
- Kontrol sınıfı: `PusulaV2NoBeRankProbe` aynı kodla ama sıralamayı kapatıp sadece çakışmaları kaydediyor. İki listede de temel ile **birebir aynı** işlemleri verdi (230 / 193), yani sayım temelin gerçek davranışını ölçüyor.

## Çakışma sayısı (temel, 2020-03 → 2026-09)
| Liste | Çakışma olan 4h mum | Kayıtlı an | Sıralamanın farklı seçeceği an | Yıllara göre (mum) |
|---|---|---|---|---|
| Eski 16 | 23 | 32 | 14 | 2020: 2, 2021: 3, 2022: 1, 2023: 4, 2024: 7, 2025: 4, 2026: 2 |
| Yeni 20 | 16 | 23 | 13 | 2020: 5, 2021: 1, 2023: 5, 2024: 2, 2025: 3 |

Çoğu çakışma "1 boş yer, 2 aday" (16'da 14/23, 20'de 6/16). Sinyaller trend başında birçok coinde birden geliyor ama işlemler günlerce sürdüğü için yerler genelde dolu; dolu iken Freqtrade sinyali hiç denemiyor, o yüzden sıralama da devreye girmiyor.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBe (temel) | 230 | +1.35R | 311.26 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | 90 günlük getiriye göre seçim | 233 | **+1.32R** | **307.96** | 2.03 | **%25.1** | +%797.0 |
| Eski 16 | Temel, coin sırası ters | 230 | +1.61R | 371.36 | 2.51 | %24.2 | +%1380.7 |
| Yeni 20 | PusulaV2NoBe (temel) | 193 | +0.61R | 117.72 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | 90 günlük getiriye göre seçim | 194 | **+0.66R** | **128.16** | 1.57 | %23.3 | +%149.7 |
| Yeni 20 | Temel, coin sırası ters | 193 | +0.64R | 122.57 | 1.53 | %23.8 | +%137.4 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6). Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R).
Ayrıntılı raporlar (funding ve çıkış türleri dahil): `wide16/rapor.md`, `new20/rapor.md`, ters sıra: `wide16_ters_sira/rapor.md`, `new20_ters_sira/rapor.md`. `PusulaV2NoBeRankProbe` sütunu kontrol sınıfıdır (temelle aynı).

**Karar: red.** Kabul kuralı iki listede de daha iyi ortalama R ve toplam R istiyor. Eski 16'da ikisi de düştü (+1.35 → +1.32R, 311.3 → 308.0R) ve DD %25 sınırını aştı (%25.1). Yeni 20'de iyi, ama tek seçime bağlı (aşağıda).

## Coin bazında dağılım (seçim − temel, toplam R)
- Eski 16: 5 coin daha iyi, 6 daha kötü, 5 aynı; toplam -3.3R. Temelden düşen 14 işlem -5.3R, yeni gelen 17 işlem -8.6R, 216 işlem ortak. En kötü SOL -3.6R, XLM -2.2R, TRX -1.6R; en iyi BNB +3.6R, ETH +1.7R, XRP +1.1R. Tek büyük işlem yok; en büyük işlem iki sürümde de aynı (ETC 2021-03 +94.1R). Yıllara göre fark küçük (2023 -1.7R, 2024 -1.7R, 2025 +0.7R).
- Yeni 20: 6 coin daha iyi, 5 daha kötü, 9 aynı; toplam +10.4R. Düşen 13 işlem +4.0R, gelen 14 işlem +14.5R. Farkın kaynağı tek an: 2024-11-08 16:00'da sıralama FIL yerine MANA'yı aldı (MANA +20.2R, FIL +10.6R): MANA +19.3R, FIL -10.6R. Bu tek değişim hariç fark ≈ +0.8R. 2024 yılı +9.6R, diğer yıllar ≈0.
- Her sürümün en büyük işlemi çıkarılınca: eski 16 temel 217.2R, seçim 213.9R; yeni 20 temel 83.2R, seçim 93.7R (ikisinde de en büyük ALGO 2024-11 +34.5R).
- Yorum: 90 günlük getiri, çakışan coinler arasında sistematik bir üstünlük göstermiyor; birkaç çakışmada sonucu belirleyen şans.

## Coin sırası ne kadar etkili (ters sıra kontrolü)
- Eski 16: ters sırada 30 işlem farklı. Temelde olup terste olmayan 30 işlem -8.3R, terste gelen 30 işlem +51.8R; bunun +66.5R'si tek DOGE 2024-10-14 işlemi. Ortak işlemler aynı.
- Yeni 20: 19 işlem farklı, fark +4.9R; en büyüğü yine 2024-11-08 MANA (+20.2R) yerine temelde FIL (+10.6R).
- Yani 3 işlem sınırı varken hangi coinin alındığı, birkaç büyük trendin yakalanıp kaçırılmasına bağlı ve toplamı belirgin oynatabiliyor (16'da ≈+60R). Bu bir kural kazancı değil, şans; raporlarda temelin toplam R'sinin bu kadar belirsiz olduğunu akılda tutmak gerekir.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`; ters sıra: aynı listeler tersten (geçici config, sadece `pair_whitelist` sırası farklı).
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeRank PusulaV2NoBeRankProbe --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --backtest-directory user_data/backtest_results/rank_<liste>` (çakışma kaydı: `PUSULA_COLLISION_LOG=<dosya>`); ters sıra `--strategy-list PusulaV2NoBe`, `--backtest-directory user_data/backtest_results/rank_<liste>_rev`. Rapor `scripts/make_report.py --test coin_secimi`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
