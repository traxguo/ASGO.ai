# Çıkarma turu 1 — BTC giriş filtresi — 2026-10-10 (temel: PusulaV2)

## GUO'ya not
- PusulaV2'den "Bitcoin de yükselişte olmalı" giriş kuralını çıkardım (`PusulaV2NoBtcFilter`).
- Sonuç iki coin grubunda da **aynı**: aynı işlemler, aynı ortalama R, aynı düşüş. Eski 16'da tek bir işlem 4 saat geç kapandı (-0.14R toplamda), yeni 20'de hiçbir şey değişmedi.
- Karar: **kabul**. Kural iş yapmıyor, çünkü "Bitcoin dönünce kapat" kuralı (tur 2a) aynı işi zaten yapıyor. Daha az kural, daha az ezber.
- Bir uyarı: kural Pusula'nın bir sonraki sürümünden çıkarılırsa Bitget demo programı da "çıkış sinyali varken girme" kuralını açıkça uygulamalı (aşağıda).

## Ne değişti
`PusulaV2NoBtcFilter(PusulaV2)`: sadece long girişindeki `market_up` (BTC günlük puanı ≥ +1) şartı kaldırıldı. BTC günlük verisi hâlâ yükleniyor, çünkü kabul edilmiş BTC-dönüş çıkışı (BTC puanı ≤ -1 → long kapat) onu kullanıyor. `PusulaV2` ve `PusulaTrendLong` değişmedi.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2) rakamları tur 3 raporuyla birebir aynı çıktı (210 / 150 işlem), yani ayarlar doğru kopyalandı.
- Not: bu dönem kasayı (2026-04 → 2026-09) da içeriyor; önceki geliştirme turları da aynı aralığı kullandı, burada yeni bir kasa kullanımı yok.

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net | Long | Short |
|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2 (temel) | 210 | +1.20R | 253.04 | 2.07 | %26.1 | +%561.0 | 210 / +1.20R | 0 |
| Eski 16 | BTC filtresi yok | 210 | +1.20R | 252.90 | 2.07 | %26.1 | +%560.2 | 210 / +1.20R | 0 |
| Yeni 20 | PusulaV2 (temel) | 150 | +0.46R | 68.51 | 1.41 | %24.6 | +%67.8 | 150 / +0.46R | 0 |
| Yeni 20 | BTC filtresi yok | 150 | +0.46R | 68.51 | 1.41 | %24.6 | +%67.8 | 150 / +0.46R | 0 |

Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6).
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: kabul** (iki listede de sonuç aynı; DD aynı). Kabul kuralı "aynı ya da daha iyi".

## Neden hiçbir şey değişmedi
- Pusula puanı sadece -3, -1, +1, +3 olabilir. Yani "BTC puanı ≥ +1" ile "BTC puanı ≤ -1 değil" aynı şey.
- PusulaV2'de BTC puanı ≤ -1 olan her mumda çıkış sinyali var. Freqtrade aynı mumda hem giriş hem çıkış sinyali varsa girmez. Bu yüzden BTC filtresinin engellediği her giriş zaten çıkış kuralı tarafından da engelleniyor.
- Tek fark (eski 16, BNB 2020-09-30 girişli işlem): filtre yokken çıkış mumunda bir giriş sinyali de vardı, Freqtrade çıkış sinyalini bir mum (4 saat) sonra uyguladı: +15 USDT yerine -2 USDT. Sonraki işlemler bileşik büyüklükten dolayı birkaç dolar farklı.

## Uyarı: demo programı
`scripts/bitget_demo.py` girişte sadece `enter_long`'a bakıyor, `exit_long`'a bakmıyor. Bugün bu sorun değil, çünkü PusulaV2'de BTC filtresi aynı mumda girişi zaten kapatıyor. Kural bir sonraki sürümden çıkarılırsa demo programı "aynı mumda çıkış sinyali varsa girme" şartını eklemeli; yoksa demo, BTC düşüşteyken işlem açıp bir sonraki mumda kapatır ve backtest ile aynı kuralı çalıştırmaz.
