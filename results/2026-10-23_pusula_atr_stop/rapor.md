# Kuyruk 14 — çıkarma: yapısal (10 mum dibi) stop kaldırıldı, sadece 1.5 ATR stop — 2026-10-23 (temel: PusulaV2NoBe)

## Kural (testten önce yazıldı)
`PusulaV2NoBeAtrStop(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Temelin stopu: giriş ortası − 1.5 ATR ile son 10 mumun dibi − 0.1 ATR tampondan **daha geniş olanı**. Yeni sürümde sadece **giriş ortası − 1.5 ATR** (ortak modül `stop_method = "atr"`); giriş ortası = sinyal mumu kapanışı − 0.125 ATR. Hepsi sinyal mumundan; stop hiç kıpırdamaz (temelde olduğu gibi).
- Sonuçları (ortak kurallar aynı, başka hiçbir şey değişmedi): stop hiçbir zaman temelin stopundan uzak değil, yani 1R (stop mesafesi) aynı ya da daha küçük, pozisyon (sermayenin %1 riski) aynı ya da daha büyük; kaldıraç yine en fazla 3x, güvenli kademeden. Plan kontrolü (stop mesafesi ≤ fiyatın %8'i) bu stopla yapılır: temelin sadece dip stopu %8'den uzak olduğu için atladığı sinyaller artık alınabilir. Teminat boş bakiyeye sığmazsa işlem atlanır (kural aynı).
- Girişler (4h kırılım, günlük puan ≥ +1, günlük kapanış EMA20 üstü) ve çıkışlar (sabit stop, günlük EMA20 çıkışı, BTC-dönüş çıkışı) aynı. Sadece long, en fazla 3 işlem, işlem başına %1 risk.
- **1R'nin anlamı değişiyor** (stop mesafesi), bu yüzden işlem başı R yanında **hesap düzeyi** karşılaştırılır: net getiri %, en büyük düşüş (DD) %, hesap-R (kâr / işlem açılırken sermayenin %1'i).
- **Kabul kuralı** (önceden): iki listede de (eski 16, yeni 20) hesap düzeyinde aynı ya da daha iyi (net getiri ve hesap-R ortalaması), DD belirgin kötü değil ve `docs/metrics.md` sınırı (%25) içinde → **kabul** (daha basit stop); aksi halde **red**. Tek işlem yoğunlaşması önceki turlar gibi kontrol edilir.

## GUO'ya not
- Soru: stopu "1.5 ATR ile son 10 mumun dibinden uzak olanı" yerine sadece 1.5 ATR koysak (daha basit kural) daha mı iyi?
- Cevap: **getiri arttı ama düşüş sınırın çok üstüne çıktı.** Stop ortalama %5.4 → %3.5 (eski 16) ve %6.3 → %4.6 (yeni 20) yakınlaştı; pozisyonlar büyüdü, çok daha sık stop olundu (stopla biten işlem %42 → %74 ve %54 → %79), boşalan yerlere yeni işlemler girdi. Hesap: eski 16 +%827 → +%3266, yeni 20 +%134 → +%423; ama en büyük düşüş eski 16'da %24 → **%44**, yeni 20'de %23 → **%68**. Üst üste kayıp 26 → 52 ve 18 → 36 işleme çıktı.
- **Karar: red.** Kabul kuralı DD'nin belirgin kötüleşmemesini ve %25 sınırında kalmasını istiyor; iki listede de çok aştı. Dip stopu kalıyor; temel `PusulaV2NoBe` değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | Ort. stop mesafesi (medyan) | Stopla biten | Kazanma | Funding (USDT) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel (geniş stop) | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | %5.37 (%5.58) | %41.7 | %32.2 | -14077 |
| Eski 16 | sadece 1.5 ATR | 371 | +1.53R | 568.10 | +1.54 / 572.7 | +%3266.4 | **%43.8** | %3.49 (%3.31) | %73.6 | %21.6 | -65812 |
| Yeni 20 | temel (geniş stop) | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | %6.29 (%6.43) | %53.9 | %23.3 | -3769 |
| Yeni 20 | sadece 1.5 ATR | 412 | +0.72R | 296.25 | +0.74 / 303.1 | +%423.4 | **%68.3** | %4.59 (%4.35) | %79.1 | %15.8 | -12790 |

- Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5, yeni 20 +%194.7.
- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). R ile hesap-R iki sürümde de neredeyse aynı (stop dibinde yeniden açılan işlem sorunu bu turda yok). Max DD Freqtrade'in hesap düşüşü. Kaldıraç iki sürümde de ortalama 3x.
- İşlem sayısı neden arttı: yakın stop daha sık vuruluyor, yer erken boşalıyor, sonraki kırılımlar alınıyor; ayrıca dip stopu %8'den uzak olduğu için atlanan sinyaller artık geçiyor. Aynı coin + aynı 4h mumda açılan ortak işlem: eski 16'da 137 (sadece ATR'de 224, sadece temelde 92), yeni 20'de 93 (302 / 99). Yani karşılaştırma büyük ölçüde farklı işlemlerin karşılaştırması.

**Karar: red.** Hesap düzeyinde net getiri ve hesap-R ortalaması iki listede de daha iyi, ama DD iki listede de belirgin kötü ve `docs/metrics.md` sınırının (%25) çok üstünde (%43.8, %68.3). Kabul kuralı DD şartını da istiyor.

## Yoğunlaşma (tek işlem / coin, hesap-R)
- Eski 16: en büyük işlem SOL 2023-10-16 +128.6 (temelde ETC 2021-03 +93.1); o hariç ortalama +1.20 (temel +0.94). En büyük 5 işlem hariç +0.55 (temel +0.28). Coin bazında 8 iyi / 8 kötü: SOL +165.9, BNB +92.3, BTC +70.8; ETC -105.0 (temelin ETC 2021-03 işlemi kaçtı). Yıllara göre 2021 163 → 274, 2023 85 → 158, 2025 16 → 1.
- Yeni 20: en büyük işlem EGLD 2020-12-15 +66.0 (temelde ALGO 2024-11 +33.9); o hariç ortalama +0.58 (temel +0.43). En büyük 5 hariç +0.19 (temel -0.08). Coin bazında 9 iyi / 11 kötü: EGLD +67.1, ZEC +60.7, VET +49.1; NEO -32.2, ALGO -27.5. Yıllara göre 2020 31 → 161, 2026 4 → 104, ama 2023 -2 → -19, 2024 64 → 16.
- Yorum: kazanç tek işlemden değil (en iyi işlem hariç de iki listede iyi), ama kazanma oranı düşük (%22 / %16) ve 50'ye varan kayıp serileri var; büyük pozisyonla bu seriler düşüşü %44-68'e çıkarıyor. Getiri yüksek riskle alınmış: risk-ayarlı bakınca (net / DD) eski 16'da 35 → 75, yeni 20'de 5.9 → 6.2; yeni 20'de neredeyse fark yok. %1 risk kuralıyla bu sürüm kullanılamaz. Ayrı bir fikir (daha düşük işlem riskiyle 1.5 ATR stop) kuyruğa yazılmadı; karar verilmedi.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeAtrStop --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --backtest-directory user_data/backtest_results/atrstop_<liste>`. Rapor `scripts/make_report.py --results <zip> --test atr_stop --out results/2026-10-23_pusula_atr_stop/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x. Hile testi gerekmedi: yeni sınıf sadece ortak modülün mevcut stop seçeneğini değiştiriyor, yeni gösterge yok.
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
