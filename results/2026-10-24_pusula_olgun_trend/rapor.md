# Kuyruk 15 — ekleme: "olgun trend" şartı (trend yaşı ≥ 11 gün) — 2026-10-24 (temel: PusulaV2NoBe)

## Kural (testten önce yazıldı)
`PusulaV2NoBeMature(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcılar `trend_age`, `add_trend_age`):
- Long girişine **tek** şart eklendi (`trend_mature`): coinin günlük puanı, giriş mumundan önce kapanmış son günlük mum dahil, **en az 11 kapanmış günlük mumdur kesintisiz ≥ +1**.
- Tanım kuyruk 13 scriptiyle aynı (`research/robustness/pusula_trend_age.py`): sinyal 4h mumu sadece kapanışından önce kapanmış günlük mumları görür (ortak `merge_informative_pair` ile aynı gecikme), yani ileriye bakma yok. Testte doğrulandı: günlük veri ileride kesilince görünen değerler değişmiyor (`tests/test_pusula.py`).
- Eşik 11, kuyruk 13 raporunun önceden sabitlenmiş gruplarından (0-10 gün en zayıf grup); **tarama yapılmadı**. Başka her şey aynı (kırılım, puan ≥ +1, EMA20 üstü, stop, çıkışlar, %1 risk, en fazla 3 işlem, sadece long).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) ortalama R, toplam R ve hesap net getirisi daha iyi; DD belirgin kötü değil ve `docs/metrics.md` sınırında (%25) → **kabul**; aksi halde **red**. Batmış 12 coin ek, sadece teşhis (karara girmez).
- **Geriye dönük bakış uyarısı:** bu fikir **bu aynı işlemlere bakılarak** çıktı (kuyruk 13). Geriye dönük iyi görünmesi beklenir; "kabul" çıksa bile ileriye dönük (kağıt / demo) doğrulama gerekirdi.

## GUO'ya not
- Soru: trend yeni başlamışken (ilk 10 gün) gelen kırılımları atlasak daha mı iyi?
- Cevap: **eski 16 coinde biraz daha iyi, yeni 20 coinde kötü, batmış coinlerde çok kötü.** Kuyruk 13'te zayıf görünen "genç trend" işlemleri atlanınca, boşalan yerlere başka (olgun trend) işlemler girdi; yeni 20'de bu yeni işlemler toplamda -17.5R getirdi ve atlanan genç trend işlemleri arasında iki büyük kazanç vardı (ALGO 2024-11 +33.9R, UNI 2024-02 +25.7R; trend 1 ve 3 günlüktü).
- **Karar: red.** Yeni 20'de toplam R 117.7 → 80.3, net getiri +%134 → +%90. Temel `PusulaV2NoBe` değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | olgun trend | 200 | +1.57R | 314.97 | +1.56 / 311.7 | +%891.6 | %20.1 | 2.21 | %33.0 | -14426 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | olgun trend | 130 | +0.62R | **80.32** | +0.61 / 79.7 | **+%89.5** | %23.2 | 1.54 | %24.6 | -3526 | +%194.7 |
| Batmış 12 (teşhis) | temel | 47 | -0.02R | -1.05 | -0.02 / -0.7 | -%1.5 | %12.1 | 0.96 | %17.0 | -497 | -%23.5 |
| Batmış 12 (teşhis) | olgun trend | 32 | **-0.42R** | -13.54 | -0.41 / -13.2 | -%12.9 | %15.8 | 0.50 | %9.4 | -215 | -%23.5 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 / 47 işlem; 311.26R / 117.72R / -1.05R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). 1R'nin anlamı değişmedi (stop aynı), R ile hesap-R neredeyse aynı. Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem. Strateji iki listede de al-tutun altında getiri, çok daha düşük düşüşle (al-tut ortalama en büyük düşüş %89 / %98).

**Karar: red.** Eski 16'da dört şart da sağlandı (ort. R, toplam R, net daha iyi, DD %23.7 → %20.1). Yeni 20'de ortalama R fiilen aynı (+0.61 → +0.62) ama toplam R (-37.4R) ve net getiri (-45 puan) belirgin kötü; DD %22.6 → %23.2. Kural "iki listede de daha iyi" istiyor. Batmış 12'de de belirgin kötü (-0.02R → -0.42R).

## Neden kuyruk 13'teki tablo tutmadı (yer etkisi)
| Liste | Ortak işlem | Sadece temelde (atlananlar) | Sadece yeni sürümde (boşalan yere girenler) |
|---|---|---|---|
| Eski 16 | 132 | 98 işlem, +11.3R (87'si genç trend) | 68 işlem, +15.0R |
| Yeni 20 | 97 | 96 işlem, +19.9R (93'ü genç trend) | 33 işlem, **-17.5R** |
| Batmış 12 | 29 | 18 işlem, +9.3R (hepsi genç trend) | 3 işlem, -3.2R |

- Kuyruk 13 genç trend işlemlerini "en zayıf grup" buldu ama toplamları artıdaydı (16: +22.0R, 20: +21.1R). Onları atlamak bu kârı da atıyor; karşılığında boşalan yerlere giren işlemler eski 16'da biraz daha iyi, yeni 20'de ve batmış 12'de eksi.
- Yani kazanç "zayıf işlemi atmak"tan değil, "yer kimde kalıyor" şansından geliyor; bu şans iki listede ters yöne gitti (kuyruk 7 ve 11'deki coin sırası dersiyle aynı).

## Yoğunlaşma (tek işlem / coin, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1; o hariç ortalama +0.94 → +1.10, en büyük 5 hariç +0.28 → +0.36. Toplamdaki fark küçük (+3.0 hesap-R) ve birkaç işlemden: atlanan BTC 2023-10 +22.4 ve BTC 2020-10 +12.7, eklenen DOGE 2020-12 +17.0, BTC 2020-10-19 +13.0, LINK 2023-10 +9.2. Coin bazında 10 iyi / 6 kötü (en çok DOGE +16.8, LINK +12.7; XRP -15.1, BTC -13.3). Yıllara göre 2020 +44.6 → +64.5, 2023 +85.4 → +64.2.
- Yeni 20: en büyük işlem temelde ALGO 2024-11-08 +33.9 (yeni sürümde yok), yenide FIL 2021-03 +32.6; en iyi hariç ortalama +0.43 → +0.36, en büyük 5 hariç -0.08 → -0.08. Kaybın çoğu iki atlanan işlem: ALGO 2024-11 (coin farkı -33.6) ve UNI 2024-02 (coin farkı -23.6). Coin bazında 11 iyi / 9 kötü, ama iyileşmeler küçük (en büyük NEO +6.7, CHZ +5.5). Yıllara göre 2024 +64.0 → +6.4.
- Batmış 12: atlanan genç trend işlemleri artıdaydı (AUDIO 2024-02 +6.3, WAVES 2021-08 +6.1, HNT 2021-08 +5.5); WAVES -6.7, AUDIO -6.3.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`, `config/pairs_delisted.json` (batmış 12, sadece teşhis).
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeMature --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/mature_<liste>`. Rapor `scripts/make_report.py --results <zip> --test olgun_trend --out results/2026-10-24_pusula_olgun_trend/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`, `delisted/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Hile testi: yeni sütun mevcut günlük birleştirmenin `date_1d` sütunundan (son kapanmış günlük mum) okunuyor; birim testi günlük veri kesilince geçmiş değerlerin değişmediğini ve 4h mumun günlük mumu ancak o gün kapandıktan sonra gördüğünü kontrol ediyor. Yeni sürümde en küçük giriş trend yaşı 11 (kural uygulanıyor); temelin en küçüğü 1.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
