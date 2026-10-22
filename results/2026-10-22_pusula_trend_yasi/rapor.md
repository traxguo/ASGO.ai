# Kuyruk 13 — teşhis: trendin yaşı — 2026-10-22 (temel: PusulaV2NoBe)

**Kural değişikliği yok.** Sadece temelin mevcut işlemleri gruplara ayrıldı.

## Soru ve yöntem (önceden yazıldı, kuyruk 13)
- Her temel işlem için: giriş anında coinin günlük puanı kaç gündür kesintisiz ≥ +1 (stratejinin kullandığı `regime_score`, aynı hesap)?
- Sadece girişten **önce kapanmış** günlük mumlar sayılır (D tarihli günlük mum, D + 1 gün ≤ giriş zamanı ise sayılır). Geleceğe bakış yok.
- Gruplar (önceden sabit): 0-10, 11-30, 31-90, 90+ gün. Her grup için işlem, kazanma oranı, ortalama R, medyan R, toplam R ve **en iyi tek işlem hariç ortalama R**.
- Karar ölçütü (önceden): iki listede de tutarlı kötü (ya da iyi) olan ve en iyi işlem çıkınca da öyle kalan bir grup var mı?
- Veri: 2026-10-21 turunun temel çıktıları (`user_data/backtest_results/nobrk_wide16-2026-10-21_06-22-11.zip`, `nobrk_new20-2026-10-21_06-21-35.zip`, sınıf `PusulaV2NoBe`). Temel rakamlar birebir aynı: 230 / 193 işlem, 311.26R / 117.72R.
- Script: `python research/robustness/pusula_trend_age.py <zip> [<zip> ...]`.

## GUO'ya not
- Soru: Pusula trendin başında mı, ortasında mı, geç mi girince iyi kazanıyor?
- Cevap: **trendin ilk 10 gününde açılan işlemler en zayıf grup, iki listede de.** İşlemlerin %40-48'i bu grupta, kazanma oranı en düşük, en iyi tek işlem çıkınca ortalama sıfır ya da eksi. Daha olgun trendlerdeki (10 günden uzun) işlemler iki listede de belirgin daha iyi.
- Bu bir test değil, sadece bir gözlem. Kural değişmedi. Bundan bir fikir çıktı (kuyruk 15): "trend en az 11 günlük değilse girme". Ayrı turda, önceden yazılmış kabul kuralıyla test edilecek.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
### Eski 16 (`config/pairs_wide16.json`)
| Trend yaşı (gün) | İşlem | Kazanma | Ort. R | Medyan R | Toplam R | Ort. R (en iyi hariç) | En iyi işlem |
|---|---|---|---|---|---|---|---|
| 0-10 | 87 | %24.1 | +0.25 | -0.91 | +21.96 | **-0.01** | +22.6 |
| 11-30 | 42 | %33.3 | +1.37 | -1.03 | +57.48 | -0.03 | +58.6 |
| 31-90 | 67 | %34.3 | +2.87 | -0.44 | +192.51 | +1.49 | +94.1 |
| 90+ | 34 | %47.1 | +1.16 | -0.14 | +39.31 | +0.56 | +20.8 |
| Hepsi | 230 | %32.2 | +1.35 | -0.63 | +311.26 | +0.95 | +94.1 |

### Yeni 20 (`config/pairs_new20.json`)
| Trend yaşı (gün) | İşlem | Kazanma | Ort. R | Medyan R | Toplam R | Ort. R (en iyi hariç) | En iyi işlem |
|---|---|---|---|---|---|---|---|
| 0-10 | 93 | %17.2 | +0.23 | -1.04 | +21.12 | **-0.15** | +34.5 |
| 11-30 | 52 | %36.5 | +1.28 | -0.79 | +66.43 | +0.66 | +33.0 |
| 31-90 | 36 | %22.2 | +0.29 | -0.69 | +10.41 | +0.02 | +9.7 |
| 90+ | 12 | %16.7 | +1.65 | -0.94 | +19.76 | -0.39 | +24.1 |
| Hepsi | 193 | %23.3 | +0.61 | -1.03 | +117.72 | +0.43 | +34.5 |

### Ek kontroller
- **0-10 gün ile 10 günden uzun** (ort. R): eski 16 +0.25 (87) vs +2.02 (143; en iyi işlem hariç +1.37); yeni 20 +0.23 (93) vs +0.97 (100; en iyi hariç +0.64).
- En iyi 3 işlem hariç ort. R, 0-10 grubu: eski 16 -0.24, yeni 20 -0.56. Coin bazında 0-10 grubunda artıda olan coin: 16'da 5/16, 20'de 5/20.
- Dönem ikiye bölününce (2020-22 / 2023-26) 0-10 grubu: eski 16 +0.47 / +0.15, yeni 20 -0.57 / +0.55. Yani her alt dönemde eksi değil; zayıflık "kazanç yok" düzeyinde, "büyük kayıp" düzeyinde değil.
- Diğer gruplar tutarsız: 31-90 eski 16'da en iyi grup (+2.87R, ama 2020-22'deki büyük boğa işlemleri; 2023-26'da +0.16R), yeni 20'de zayıf (+0.29R, en iyi hariç +0.02). 11-30 yeni 20'de iyi, eski 16'da en iyi işlem hariç -0.03. 90+ az işlem (34 / 12), yönü listeye göre değişiyor.
- Trend yaşı en az 1 gün (tüm girişlerde son kapanmış günlük puan ≥ +1, beklendiği gibi). Medyan yaş 15 gün, en uzun 220 gün.

## Yorum
- **Tutarlı olan tek grup 0-10 gün:** iki listede de ortalama R en düşük (+0.25 / +0.23), medyan en kötü ya da ona yakın, kazanma oranı düşük, en iyi tek işlem çıkınca ≈ 0 / eksi (-0.01 / -0.15). Yani trendin ilk 10 gününde açılan işlemlerin toplam kazancı tek bir şanslı işleme bağlı.
- **Tutarlı iyi grup yok.** Olgun trendler (>10 gün) iki listede de daha iyi, ama hangi olgun grubun iyi olduğu listeye göre değişiyor.
- Bu, kuyruk 12'nin bulgusuyla uyumlu: rejim yeni başladığında açılan kırılımlar sık sık sahte çıkıyor (günlük trend hemen geri dönüyor, EMA20 / stop çıkışı).
- Uyarı: bu teşhis aynı işlemlere bakarak yapıldı. 0-10 grubunu çıkarmak geriye dönük olarak iyi görünecek; gerçek etki (3 yer sınırında boşalan yerlere başka işlemlerin girmesi, DD) ancak ayrı bir backtest turunda ölçülür. Sınır (10 gün) kuyruk 13'te sonuçtan önce yazılmıştı.
- Not: verinin başında (ilk 90 gün + EMA50 ısınması) puan hesaplanamıyor; o dönemde başlayan ilk trendin yaşı kısa sayılır. Strateji de o dönemde işlem açamıyor, etkisi küçük.

## Sonraki adım (yeni kuyruk maddesi 15, test edilmedi)
Long girişine bir şart: son kapanmış günlük puan en az **11 gündür kesintisiz ≥ +1** olmalı (yani trend yaşı ≥ 11 gün). Başka her şey aynı (ayrı sınıf, ör. `PusulaV2NoBeMature`). Aynı kabul kuralı: iki listede de ortalama R ve toplam R aynı ya da iyi, DD %25 içinde; tek işlem yoğunlaşması kontrol edilir. Eşik bu raporun gruplarından sabit; ızgara/eşik taraması yapılmaz.

## Ayarlar
- Backtest: `--timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3`, sadece long, işlem başına %1 risk (2026-10-21 turunun çıktısı, yeniden çalıştırılmadı).
- Maliyet: emir başına %0.1, funding dahil (backtestte). Al-tut (aynı dönem, eşit ağırlık): eski 16 +%931.5, yeni 20 +%194.7 (bu teşhis rakamları değiştirmiyor).
- R hesabı `scripts/make_report.py` `trade_r` ile aynı.
