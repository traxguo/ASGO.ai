# Kuyruk 18 — ekleme: güçlü kapanışlı kırılım — 2026-10-27 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: 4 saatlik kırılım mumu tepesine yakın kapanmazsa (uzun üst fitil, zayıf kapanış = alıcı tükenmiş olabilir) girmesek daha mı iyi?
- Cevap: **hayır, tersine.** Kırılımların yaklaşık %80'i zaten güçlü kapanıyor. Zayıf kapananlar (16'da 46, 20'de 42 giriş) kötü değildi, ortalamada güçlü kapananlardan **daha iyiydi** (16: +1.43R'ye karşı +1.33R; 20: +1.45R'ye karşı +0.38R). Bu şart iki listede de büyük kazançları kesti (BTC 2023-10 +22.6R, BTC 2024-01 +20.8R, FIL 2021-03 +33.0R, THETA 2020-12 +24.1R).
- **Karar: red.** İki listede de ortalama R, toplam R ve net getiri kötüleşti (16: net +%827 → +%584; 20: +%134 → +%42). Temel `PusulaV2NoBe` değişmedi.

## Kural (testten önce yazıldı)
`PusulaV2NoBeStrongClose(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `close_location`):
- Long girişine **tek** şart eklendi (`strong_close`): 4h kırılım (sinyal) mumunda `(close - low) / (high - low) ≥ 2/3`, yani kapanış mumun en düşük–en yüksek aralığının üst üçte birinde.
- `high == low` (aralığı olmayan mum) → giriş engellenir.
- Kırılım tanımı aynı ("20 mumluk tepenin üstünde **ilk** 4h kapanış"), yani zayıf kapanan ilk kırılım mumu **atlanır**, sonraki muma kaydırılmaz.
- Eşik sabit (2/3), **tarama yok**. Başka her şey aynı (puan ≥ +1, EMA20 üstü, stop, çıkışlar, %1 risk, en fazla 3 işlem, sadece long).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → **kabul**; aksi halde **red**. Engellenen girişlerin R'si ayrıca raporlanır.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | güçlü kapanış | 224 | **+1.18R** | **263.97** | +1.17 / 261.1 | **+%583.7** | %22.7 | 2.04 | %32.1 | -9224 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | güçlü kapanış | 180 | **+0.30R** | **54.16** | +0.29 / 52.8 | **+%41.7** | %20.1 | 1.26 | %22.8 | -2685 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem.

**Karar: red.** DD iki listede de biraz düştü, ama ortalama R, toplam R ve net iki listede de belirgin kötü. Kural "iki listede de daha iyi" istiyor; dört şarttan üçü iki listede de bozuldu.

## Engellenen temel girişler (şart temelin kendi sinyal mumunda hesaplandı)
| Liste | Engellenen | Kazanan | Toplam R | Hesap-R | Bu işlemlerin funding'i (USDT) | Boşalan yere giren | Onların R'si |
|---|---|---|---|---|---|---|---|
| Eski 16 | 46 (%20) | 16 | **+65.90** (ort. +1.43) | +65.33 | -4258 | 47 | +22.64 |
| Yeni 20 | 42 (%22) | 11 | **+60.77** (ort. +1.45) | +60.22 | -804 | 31 | -4.87 |

- Kıyas: güçlü kapanan (kalan) temel girişler 16'da 184 işlem ort. **+1.33R**, 20'de 151 işlem ort. **+0.38R**. Zayıf kapananlar iki listede de daha iyi.
- En büyük katkılar (engellenen, R): eski 16'da BTC 2023-10-16 **+22.6** (kapanış yeri 0.31), BTC 2024-01-28 **+20.8** (0.26), TRX 2021-03-31 +14.1, XRP 2020-07-18 +6.9, TRX 2023-10-20 +5.0. Yeni 20'de FIL 2021-03-03 **+33.0** (0.65), THETA 2020-12-13 **+24.1** (0.65), DASH 2024-11-23 +9.1, IOTA 2020-07-20 +7.9, VET 2026-09-05 +5.3.
- En büyük iki işlem hariç bile engellenenler eksi değil: 16'da 44 işlem +22.5R (ort. +0.51), 20'de 40 işlem +3.7R (ort. +0.09). Yani şart zararlı işlemleri seçip atmıyor; kayıplar ve kazançlar aynı oranda gidiyor.
- Kapanış yerine göre temel (16 / 20): 0-1/3 → 2 işlem +43.5R / 2 işlem +8.1R; 1/3-2/3 → 44 işlem +0.51R ort. / 40 işlem +1.32R ort.; ≥ 2/3 → 184 işlem +1.33R ort. / 151 işlem +0.38R ort. Tutarlı bir "zayıf kapanış kötü" ilişkisi yok.
- Yıllara göre engellenenler: 16'da 2020 +13.5, 2021 +11.1, 2023 +29.8, 2024 +16.3R; 20'de 2020 +31.8, 2021 +29.7R, sonraki yıllar ≈ 0. Kayıp tek döneme bağlı değil.
- Boşalan yerler: 16'da yeni sürüm 47 farklı işleme girdi (+22.6R; BNB 2024-02 +12.3, AVAX 2024-11 +9.5) ve 7 temel işlemi yer kaymasıyla kaçırdı (+4.2R, ETH 2024-02 +8.9 dahil). 20'de boşalan yere girenler -4.9R. Ortak işlemlerde R aynı (16: 241.2 → 241.3R, 20: 59.0 → 59.0R).
- Funding: 16'da -14077 → -9224 USDT, 20'de -3769 → -2685 USDT. Tasarrufun çoğu kesilen büyük ve uzun BTC / TRX işlemlerinin funding'i; kazanç kaybının yanında küçük.

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1; o hariç ortalama +0.94 → +0.75, en büyük 5 hariç +0.28 → +0.15. Temelin en büyük 5 işleminden ikisi (BTC 2023-10 +22.4, BTC 2024-01 +20.6) engellenenler arasında.
- Yeni 20: en büyük işlem iki sürümde de ALGO 2024-11-08 +33.9; o hariç +0.43 → +0.11, en büyük 5 hariç -0.08 → -0.24. Temelin en büyük 5 işleminden ikisi (FIL 2021-03 +32.6, THETA 2020-12 +23.8) engellendi.
- Coin bazında fark (R, yeni − temel): 16'da BTC -29.9, TRX -26.4, ETH -12.6, XRP -7.0 (BNB +15.6, AVAX +10.6); 20'de FIL -32.0, THETA -24.7, DASH -6.8, ICP -5.4 (NEO +7.4).
- Kısaca: kayıp birkaç büyük işlemden geliyor, ama en büyükleri dışarıda bırakınca da yeni sürüm iki listede kötü.

## İleriye bakma kontrolü
- Şart sadece sinyal mumunun kendi değerlerini (high, low, close) kullanıyor; sinyal mumu emir verilmeden önce kapanmış mum (Freqtrade emri bir sonraki mumda veriyor). Sonraki mumlar kullanılmıyor.
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_strong_close_needs_top_third_close_on_signal_candle`): 2/3 sınırında giriş var, altında yok, `high == low` engelliyor; sinyal mumundan sonra çok yükselen bir mum eklenince sinyal mumunun kararı değişmiyor.
- Backtest çıktısıyla kontrol: her işlem için sinyal mumu = dolumdan önce kapanmış, en fazla 3 mum (emir geçerlilik süresi) geride, "ilk kırılım" olan mum. 454 (16) ve 373 (20) işlemin hepsinde böyle bir mum bulundu (21 işlemde iki aday vardı; hepsinde iki aday 2/3'ün aynı tarafında ya da işlem yeni sürümde de var, sınıflandırma değişmiyor). Yeni sürümün bütün girişlerinde bu mumun kapanış yeri ≥ 2/3 (en düşük 0.6667, tam sınır); engellenen 88 temel girişin hiçbiri yeni sürümde yok.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeStrongClose --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/strongclose_<liste>`. Rapor `scripts/make_report.py --results <zip> --test guclu_kapanis --out results/2026-10-27_pusula_guclu_kapanis/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
