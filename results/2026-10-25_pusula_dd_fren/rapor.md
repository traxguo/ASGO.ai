# Kuyruk 16 — risk: hesap düşüş freni — 2026-10-25 (temel: PusulaV2NoBe)

## Kural (testten önce yazıldı)
`PusulaV2NoBeDdBrake(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`, yardımcı `dd_brake_risk`):
- Sermaye ölçüsü: **kapanmış işlemlerle hesap bakiyesi** (başlangıç + kapanmış işlemlerin net kârı; komisyon, kayma, funding dahil, açık işlemlerin kâğıt üstü kârı/zararı yok). Neden: temel pozisyon büyüklüğünü zaten bu sayıdan hesaplıyor ve giriş anında kesin bilinen tek sayı bu; ileriye bakma olmaz.
- Zirve: o girişe kadar görülen en yüksek kapanmış bakiye (başlangıç bakiyesi ve o girişten önce kapanmış her işlemden sonraki bakiye).
- Her yeni girişte: bakiye zirvenin **%15 veya daha fazla altındaysa** işlem riski **%0.5**, değilse **%1** (temel). Fren, düşüş %15'in altına inince kendiliğinden kalkar (yeni zirve şart değil).
- Eşikler sabit (%15, %0.5), **tarama yok**. Girişler, stop, kaldıraç sınırı, çıkışlar, en fazla 3 işlem, "marj yetmezse atla" kuralı aynı.
- **Kabul kuralı** (önceden, hesap düzeyinde): iki listede de (eski 16, yeni 20) max DD belirgin düşük **ve** net getiri / max DD oranı kötü değil → **kabul**; aksi halde **red**. Tek işlem yoğunlaşması önceki turlardaki gibi raporlanır.

## GUO'ya not
- Soru: hesap zirvesinden %15 düşünce riski yarıya indirsek düşüş daha mı küçük kalır, kazanca göre daha mı iyi olur?
- Cevap: **düşüş biraz küçüldü ama kazanç çok daha fazla küçüldü.** Fren açıkken açılan işlemler (eski 16'da 85, yeni 20'de 78) toplamda çok kârlıydı (+99R / +91R): düşüşten çıkışı sağlayan işlemleri yarım boyla almış olduk. Bu yüzden toparlanma da uzadı.
- **Karar: red.** Net getiri / DD oranı iki listede de kötüleşti (34.8 → 29.6, 5.9 → 3.3). Temel `PusulaV2NoBe` değişmedi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem)
| Liste | Sürüm | İşlem | %0.5 riskli giriş | Toplam R | Hesap-R ort. / toplam | Net | Max DD (Freqtrade) | Max DD (kapanmış bakiye) | Net / DD | En uzun su altı | PF | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | 0 | 311.26 | +1.34 / 308.7 | +%827.3 | %23.7 | %23.7 | 34.8 | 925 gün (2024-03 → sona kadar, hâlâ zirve altında) | 2.06 | -14077 | +%931.5 |
| Eski 16 | düşüş freni | 230 | 85 | 311.26 | +1.13 / 259.1 | **+%583.1** | %19.7 | %19.7 | **29.6** | 967 gün (2021-05 → 2024-01) | 2.14 | -10878 | +%931.5 |
| Yeni 20 | temel | 193 | 0 | 117.72 | +0.60 / 115.8 | +%134.2 | %22.6 | %27.4 | 5.9 | 1057 gün (2021-04 → 2024-03) | 1.53 | -3769 | +%194.7 |
| Yeni 20 | düşüş freni | 193 | 78 | 117.72 | +0.37 / 71.3 | **+%71.0** | %21.6 | %21.6 | **3.3** | 1334 gün (2021-04 → 2024-12) | 1.38 | -3073 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R). İki sürüm **aynı işlemleri** açtı (girişler değişmedi); sadece boyut değişti, bu yüzden işlem R'si ve toplam R aynı.
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Freni açık bir işlem +2R yaparsa hesap-R +1 sayılır; frenin maliyeti burada görünüyor.
- "%0.5 riskli giriş": aynı işlemin iki sürümdeki risk/sermaye oranı karşılaştırılarak sayıldı (oran 0.49-0.50 olanlar).
- Max DD (Freqtrade): önceki turlarda kullanılan ölçü (en büyük USDT düşüşünün o zamanki zirveye oranı). Kapanmış bakiye DD: kapanmış işlem bakiyesinin zirveden en büyük yüzde düşüşü (frenin baktığı ölçü). Yeni 20 temelde iki ölçü farklı (%22.6 / %27.4) çünkü Freqtrade en büyük USDT düşüşünü seçiyor.
- Net / DD = net getiri (%) / Freqtrade max DD (%). En uzun su altı = kapanmış bakiyenin bir zirveden o zirveyi tekrar geçene kadar (ya da dönem sonuna kadar) geçen en uzun süre.

**Karar: red.** Şart 1 (DD iki listede belirgin düşük): eski 16'da evet (%23.7 → %19.7), yeni 20'de Freqtrade ölçüsüyle zayıf (%22.6 → %21.6; kapanmış bakiyeyle %27.4 → %21.6). Şart 2 (net / DD kötü değil): **iki listede de kötü** (34.8 → 29.6; 5.9 → 3.3). En uzun su altı süresi de iki listede uzadı.

## Neden tutmadı
- Fren açıkken açılan işlemler toplamda çok iyiydi: eski 16'da 85 işlem +99.2R, yeni 20'de 78 işlem +90.8R (işlem başına ≈ +1.2R, ortalamanın üstü). Bu strateji düşüşten birkaç büyük trend işlemiyle çıkıyor; fren bu işlemleri yarım boyla aldırıyor.
- Fren genelde 2023'ten sonra açık kaldı (16: 2023'te 19, 2024'te 24, 2025'te 23, 2026'da 19 giriş; 20: 2023'te 32, 2024'te 17, 2025'te 14, 2026'da 15). 2021 zirvesinden sonra bakiye uzun süre %15+ altında kaldığı için fren yıllarca açık; DD'yi kesmekten çok toparlanmayı yavaşlattı.
- Yıllara göre hesap-R: eski 16'da 2023 +85.4 → +42.0, 2025 +15.5 → +4.8; yeni 20'de 2024 +64.0 → +23.8 (ALGO 2024-11 ve UNI 2024-02 frenli alındı).

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1 (fren kapalıydı). En iyi hariç ortalama +0.94 → +0.73, en büyük 5 hariç +0.28 → +0.22.
- Yeni 20: en büyük işlem temelde ALGO 2024-11-08 +33.9 (frenli sürümde yarıya indi), frenli sürümde FIL 2021-03-03 +32.6. En iyi hariç +0.43 → +0.20, en büyük 5 hariç -0.08 → -0.16.
- Kayıp tek işlemden değil: frenli dönemdeki işlemlerin genelinden.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long. Risk: temel %1; frenli sürüm %1 veya %0.5 (yukarıdaki kural).
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeDdBrake --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/ddbrake_<liste>`. Rapor `scripts/make_report.py --results <zip> --test dd_fren --out results/2026-10-25_pusula_dd_fren/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`. Not: alt raporlarda "Risk: %1" satırı sabit metindir; frenli sürüm %1 / %0.5 kullandı.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- İleriye bakma yok: boyut, girişin emri verildiği anda kapanmış işlemlerle (Freqtrade cüzdanı + kapanmış işlem listesi) hesaplanıyor; açık işlemlerin kârı/zararı kullanılmıyor. Birim testi (`tests/test_pusula.py`) eşiği (%15 tam sınırda fren açık), frenin kalkmasını ve yarım boyu kontrol ediyor.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
