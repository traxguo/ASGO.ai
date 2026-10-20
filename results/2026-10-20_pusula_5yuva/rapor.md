# Kuyruk 11 — 5 yer, işlem başına daha küçük risk — 2026-10-20 (temel: PusulaV2NoBe)

## Temel nasıl boyutlandırıyor
- `PusulaV2NoBe` pozisyonu **riske göre** açar (ortak modül `strategies/common`, `custom_stake_amount` + `position_notional`): stop vurulursa toplam sermayenin **%1'i** kaybedilir (`risk_per_trade = 0.01`). Pozisyon büyüklüğü = sermaye × %1 / stop mesafesi (%); kaldıraç en fazla 3x ve tasfiye fiyatı stopun en az 2 katı uzakta kalacak şekilde seçilir. Boş teminat yetmezse işlem açılmaz (farklı riskle açılmaz).
- En fazla 3 işlem → aynı anda en fazla %3 sermaye riskte.

## Kural (testten önce yazıldı)
`PusulaV2NoBe5(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- En fazla **5** açık işlem (`--max-open-trades 5`).
- İşlem başına risk **%1 × 3 / 5 = %0.6** (stop vurulursa sermayenin %0.6'sı kaybedilir). Aynı anda en fazla 5 × %0.6 = **%3** riskte, yani toplam açık risk temelle aynı.
- Başka her şey `PusulaV2NoBe`: giriş, sabit stop, EMA20 ve BTC-dönüş çıkışı, kaldıraç sınırı, sadece long.
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) hesap düzeyinde daha iyi: net getiri % ve ortalama R kötü değil, DD belirgin kötü değil ve `docs/metrics.md` sınırı (%25) içinde, **ve** coin sırası duyarlılığı (|toplam R normal sıra − toplam R ters sıra|) belirgin küçük → kabul; aksi halde red.
- Not: R işlem başına kendi riskiyle ölçülür. 5 yerde 1R = sermayenin %0.6'sı, temelde %1'i; bu yüzden toplam R iki sürüm arasında doğrudan kıyaslanmaz, hesap düzeyi (net %, DD %) ana ölçüdür. Toplam R'yi hesap karşılığına çevirmek için 5 yerin toplam R'si × 0.6.

## GUO'ya not
- Soru: en fazla 3 işlem yerine en fazla 5 işlem açsak, ama her işlemde daha az risk alsak (%1 yerine %0.6; aynı anda riskteki toplam para yine en fazla %3), "hangi coin yeri kaptı" şansı azalır mı, sonuç iyileşir mi?
- Sonuç: **red**. İki listede de hesap getirisi **düştü** (eski 16: +%827 → +%621; yeni 20: +%134 → +%105). Düşüş biraz azaldı (DD %23.7 → %22.1 ve %22.6 → %21.4), ortalama R aynı ya da biraz düşük.
- Coin sırası şansı: eski 16'da belirgin küçüldü (ters sıra farkı 60R → 10R), ama yeni 20'de **büyüdü** (5R → 23R). Yani şansı her iki listede azaltmıyor.
- Neden getiri düştü: ek 2 yer gerçekten ek işlem getiriyor (16'da +135 işlem, 20'de +72), ama bunlar zaten açılan işlemleri %40 küçültmenin kaybını karşılamıyor. Temel `PusulaV2NoBe` (3 yer, %1) değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long)
| Liste | Sürüm | Coin sırası | İşlem | Ortalama R | Toplam R | Hesap karşılığı (temel R) | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | 3 yer, %1 (temel) | normal | 230 | +1.35R | 311.26 | 311.3 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | 3 yer, %1 (temel) | ters | 230 | +1.61R | 371.36 | 371.4 | 2.51 | %24.2 | +%1380.7 |
| Eski 16 | 5 yer, %0.6 | normal | 354 | **+1.20R** | 423.94 | 254.4 | 2.23 | %22.1 | **+%621.2** |
| Eski 16 | 5 yer, %0.6 | ters | 363 | +1.14R | 413.92 | 248.4 | 2.15 | %22.3 | +%583.3 |
| Yeni 20 | 3 yer, %1 (temel) | normal | 193 | +0.61R | 117.72 | 117.7 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | 3 yer, %1 (temel) | ters | 193 | +0.64R | 122.57 | 122.6 | 1.53 | %23.8 | +%137.4 |
| Yeni 20 | 5 yer, %0.6 | normal | 264 | **+0.60R** | 159.06 | 95.4 | 1.58 | %21.4 | **+%104.6** |
| Yeni 20 | 5 yer, %0.6 | ters | 266 | +0.51R | 135.98 | 81.6 | 1.48 | %21.6 | +%82.7 |

- R her işlemin kendi riskiyle ölçülür: 5 yerde 1R = sermayenin %0.6'sı. "Hesap karşılığı" = toplam R × 0.6 (5 yer) — hesaba etkisini temelin R'siyle kıyaslamak için. Net getiri bileşik büyüme içerdiğinden hesap karşılığı ile birebir orantılı değil.
- Max DD: Freqtrade'in hesap düşüşü (önceki turlarla aynı ölçü). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5, yeni 20 +%194.7. Funding toplamı: eski 16 temel -14077 / 5 yer -9007 USDT, yeni 20 temel -3769 / 5 yer -2655 USDT.
- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R; ters sıra 371.36R / 122.57R, kuyruk 7 ile aynı).

**Karar: red.** Kabul kuralı iki listede de hesap düzeyinde iyileşme istiyor: net getiri iki listede de düştü (16: -%206 puan, 20: -%30 puan), ortalama R 16'da düştü (+1.35 → +1.20R), 20'de aynı (+0.61 → +0.60R). DD iki listede de biraz iyi ve sınır içinde, ama bu tek başına yetmiyor. Ayrıca coin sırası duyarlılığı yeni 20'de büyüdü.

## Coin sırası duyarlılığı (|toplam normal − toplam ters|)
| Liste | 3 yer, %1 | 5 yer, %0.6 (R) | 5 yer, hesap karşılığı (×0.6) | Net getiri farkı 3 yer → 5 yer |
|---|---|---|---|---|
| Eski 16 | 60.1R | 10.0R | 6.0R | %553 puan → %38 puan |
| Yeni 20 | 4.9R | 23.1R | 13.8R | %3 puan → %22 puan |

- Eski 16: 3 yerde farkı neredeyse tamamen tek DOGE 2024-10-14 işlemi (+66.5R) yapıyordu; 5 yerde o işlem iki sırada da alınıyor (5 yerin en büyük 2. işlemi). Bu yüzden fark çöktü.
- Yeni 20: 3 yerde iki sıra neredeyse aynıydı; 5 yerde ters sıra 23R daha kötü. Daha çok yer sırayı belirleyici olmaktan çıkarmadı, sadece hangi işlemlerin şansla değiştiğini değiştirdi.
- Yorum: duyarlılık eski 16'da küçüldü, yeni 20'de büyüdü; "belirgin küçük" şartı iki listede sağlanmadı.

## Yoğunlaşma (tek işlem / coin)
- Eski 16: 219 işlem ortak; temelde olup 5 yerde olmayan 11 işlem -8.2R, sadece 5 yerde olan 135 işlem +104.4R (0.6% riskle, hesap karşılığı ≈ +63R); ortak işlemler %40 küçük olduğu için ≈ -128 temel-R kaybettirdi. En büyük işlem iki sürümde de ETC 2021-03 +94.1R (5 yerde toplam kârın %30'u, temelde %29). En büyük hariç: temel 217.2R (+0.95R), 5 yer 329.9R (+0.93R). Coin bazında (toplam R) 7 coin daha iyi, 8 daha kötü, 1 aynı; iyileşmenin çoğu DOGE +97.9R (2024-10 işlemi), sonra BCH +14.6R, AVAX +10.9R; en kötü TRX -7.8R, LTC -6.7R, ETC -6.2R. Yıllara göre fark (R) 2024'te +93.7R (DOGE), diğer yıllar ±15R.
- Yeni 20: 192 işlem ortak; temelin 1 işlemi (+2.4R) yok, 5 yerde 72 yeni işlem +43.8R (hesap karşılığı ≈ +26R). En büyük işlem iki sürümde de ALGO 2024-11 +34.5R; en büyük hariç: temel 83.2R (+0.43R), 5 yer 124.6R (+0.47R). Coin bazında 7 coin daha iyi, 12 daha kötü, 1 aynı; iyileşme birkaç coinde (NEAR +24.5R, MANA +18.0R, ENJ +15.8R), kötüleşmeler küçük ve yaygın (XTZ, THETA, CHZ ≈ -4R).
- Yorum: R olarak toplam artıyor çünkü işlem sayısı artıyor; ama ek işlemlerin ortalaması (16: +0.77R, 20: +0.61R) hesaba ancak %0.6 ağırlıkla giriyor ve tüm işlemlerin küçülmesini telafi etmiyor.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, sadece long. Temel `--max-open-trades 3`, yeni sınıf `--max-open-trades 5`.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`; ters sıra: aynı listeler tersten (geçici config, sadece `pair_whitelist` sırası farklı, kuyruk 7'deki yöntem).
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy <PusulaV2NoBe|PusulaV2NoBe5> --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades <3|5> --export trades --backtest-directory user_data/backtest_results/slot5_<liste>_<base|5>[_rev]`. Rapor `scripts/make_report.py --results <zip> --test 5yuva --out results/2026-10-20_pusula_5yuva/<liste>_<3|5>yuva[_ters_sira] --risk-pct <1|0.6>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16_3yuva/`, `wide16_5yuva/`, `wide16_3yuva_ters_sira/`, `wide16_5yuva_ters_sira/`, `new20_3yuva/`, `new20_5yuva/`, `new20_3yuva_ters_sira/`, `new20_5yuva_ters_sira/` (`rapor.md`).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x. Hile testi gerekmedi: yeni sınıf sadece risk yüzdesini ve yer sayısını değiştiriyor, sinyal kodu aynı.
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
