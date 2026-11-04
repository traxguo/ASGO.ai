# forex_trend — Forex/altın/Nasdaq günlük ve 4 saatlik trend takibi (araştırma, 2026-11-04)
Kod: [`research/forex_trend/trend.py`](../research/forex_trend/trend.py), iş akışı: `.github/workflows/forex_trend.yml` (veri GitHub sunucusunda indirilir, repoya girmez)

## Hipotez
GUO: hem düşüşte hem yükselişte kazanmak istiyor, forex dahil. Kısa vadeli (scalp) forex taraması başarısız oldu ([forex_tarama](forex_tarama.md)). Fiyat günlerce/haftalarca aynı yöne gidiyorsa (trend), trende binen basit bir kural hem long hem short tarafında kazanabilir. Bu, fonların yıllardır kullandığı "trend takibi" fikrinin en sade halidir.

## Yön
İkisi de. Long ve short ayrı ayrı hesaplanır ve ayrı raporlanır.

## Piyasalar ve masraf
- EUR/USD, altın (XAUUSD), Nasdaq 100 (NAS100). HistData 1 dakikalık veriden günlük (UTC günü) ve 4 saatlik mumlar.
- Masraf (gidiş-dönüş): EUR/USD %0.010, altın %0.015, Nasdaq %0.010.
- Swap (gecelik finansman, tahmini, yıllık %): EUR/USD long 1.5 / short 1.5, altın long 4 / short 2, Nasdaq long 5 / short 2.5. Pozisyonun açık kaldığı her takvim günü için ödenir. Bilerek kötümser: bazı aracı kurumların bazı yönlerde ödediği artı swap hiç sayılmaz.
- Her şey bir de **2 kat masraf ve 2 kat swap** ile çalıştırılır.
- Dönemler: geliştirme 2020-2024, doğrulama 2025-01 → 2026-03. Kasa (2026-04 → 09) kullanılmaz. (Uyarı: EMA200 gibi uzun göstergeler 2020'nin ilk aylarında henüz oturmamıştır.)

## Kurallar (ilk çalıştırmadan önce yazıldı)
Sinyal mum kapanışında oluşur, giriş bir sonraki mumun açılışında. Stop mumun en yüksek/en düşüğüne değerse stop fiyatından (boşlukla geçerse açılıştan) çıkılır. Aynı mumda hem stop hem hedef varsa önce stop sayılır. Her piyasa ve yön için aynı anda tek işlem. R = giriş ile ilk stop arası mesafe.

- **T1, Donchian kırılımı** (günlük ve 4 saatlik, N = 20 / 50 / 100 mum)
  - [t1_breakout] Teknik: kapanış önceki N mumun en yükseğinin üstünde → long (en düşüğünün altında → short) | Açıklama: "Fiyat son N mumun zirvesini kırdı."
  - Stop: girişte 2 × ATR(20). Çıkış: kapanış ters yöndeki N/2 mumluk kanalın dışına çıkınca (long için N/2 mumun dibinin altı).
- **T2, Hareketli ortalama kesişimi** (günlük ve 4 saatlik, EMA 10/50, 20/100, 50/200)
  - [t2_cross] Teknik: hızlı EMA yavaşı yukarı keser → long (aşağı keser → short) | Açıklama: "Kısa vadeli ortalama uzun vadeliyi yukarı kesti, trend yukarı döndü."
  - Stop: girişte 3 × ATR(20), sonra en iyi kapanıştan 3 × ATR geride takip eden stop. Ters kesişimde çık. Stop olursa bir sonraki kesişime kadar yeniden girilmez.
- **T3, Trend içinde geri çekilme** (4 saatlik, hedef 1.5R / 2R / 3R)
  - [t3_daily_trend] Teknik: son kapanmış günde kapanış > EMA100 ve EMA50 > EMA100 (short için tersi) | Açıklama: "Günlük trend yukarı."
  - [t3_pullback] Teknik: 4 saatlik kapanış EMA20'nin altındayken tekrar üstüne çıktı (short için tersi) | Açıklama: "Fiyat geri çekildi ve trend yönüne döndü."
  - Stop: son 6 mumun dibi − 0.5 × ATR (short: tepe + 0.5 ATR). Hedef: sabit R. Günlük trend bozulursa veya 60 mum (10 gün) dolunca çık.

Toplam 15 ayar × 3 piyasa × 2 yön = 90 deneme.

## Geçme şartı (ilk çalıştırmadan önce sabitlendi)
1. Geliştirmede ≥ 30, doğrulamada ≥ 8 işlem.
2. Masraf + swap sonrası işlem başı ortalama R > 0 hem geliştirmede hem doğrulamada.
3. Geliştirmede kâr faktörü ≥ 1.15 ve 5 geliştirme yılının en az 3'ü artı.
4. **2 kat masrafla** da 1-3 tutmalı.
5. **Şans kontrolü:** 90 deneme çok fazla; bazıları şansla geçer. Aynı tarama, günlerin sırası rastgele karıştırılmış veride 20 kez çalıştırılır (oynaklık aynı, ama günler arası trend yok). Gerçek veride geçen sayı, karıştırılmış veride geçen sayıdan açıkça fazla değilse sonuç şans sayılır. Tek tek geçen ayarın karıştırılmış veride ne sıklıkla geçtiği de yazılır.
6. Komşu ayarlar da (aynı kuraldan bir üst/alt N) artı olmalı; tek başına parlayan ayar sayılmaz.
7. Long sonucu al-tut ile kıyaslanır: altın ve Nasdaq 2020-2026'da çok yükseldi; long kuralı al-tuttan çok daha az kazanıyorsa sadece yükselişi yakalamış demektir.

## Durum: reddedildi (2026-11-04)
Short tarafında hiçbir kural geçmedi. Long tarafında altında 5, Nasdaq'ta 1 ayar geçti ama bu, rastgele karıştırılmış veride de aynı sıklıkla oluyor: kazanç "trend yakalama becerisi" değil, 2020-2026'daki büyük yükselişin (altın +72% ve +76%, Nasdaq +137%) bir kısmını almak. Al-tuttan daha az kazandırıyor.

## Sonuçlar (2026-11-04, ilk çalıştırma, PR #45 "Forex trend" iş kaydı)
R = işlem başı risk (stop mesafesi). Masraf + tahmini swap dahil. İşlem başı %1 riskle "toplam R" yaklaşık % getiriye eşittir.

**Şans kontrolü (en önemli satır):** gerçek veride 90 ayardan **6** geçti; günleri karıştırılmış veride (trend yok, ama genel yükseliş aynı) ortalama **6.6** geçti (20 deneme, en çok 10). 2 kat masrafta gerçek 4, karıştırılmış ortalama 4.8. Yani gerçek veri, rastgeleden iyi değil.

Geçen 6 ayar (hepsi long):
| Piyasa | Ayar | Geliştirme | Doğrulama | Karıştırılmış veride de geçti | 2x masraf |
|---|---|---|---|---|---|
| Altın | T1 Donchian 4s 50 | +0.29R, 70 işlem, PF 1.43, DD 14.6R | +2.43R, 17 işlem | 15/20 | geçer |
| Altın | T1 Donchian 4s 100 | +0.81R, 39 işlem, PF 2.11, DD 7.7R | +3.10R, 11 işlem | 12/20 | geçer |
| Altın | T2 EMA 4s 10/50 | +0.11R, 106 işlem, PF 1.35 | +0.42R, 21 işlem | 12/20 | geçer |
| Altın | T2 EMA 4s 20/100 | +0.21R, 53 işlem, PF 1.57 | +0.86R, 10 işlem | 10/20 | geçer |
| Altın | T3 geri çekilme 3R | +0.15R, 107 işlem, PF 1.26 | +0.61R, 40 işlem | 8/20 | kalmaz |
| Nasdaq | T1 Donchian 4s 100 | +0.70R, 46 işlem, PF 2.13 | +0.06R, 10 işlem | 4/20 | kalmaz |

Al-tut kıyası (long): altın Donchian 4s 100 geliştirmede toplam +31.7R (≈ +%32, %1 riskle) ↔ al-tut +%72; doğrulamada +34R ↔ al-tut +%76. Nasdaq Donchian 4s 100 geliştirme +32R ↔ al-tut +%137; doğrulama +0.6R ↔ +%13.

Short tarafı (piyasa piyasa):
- **EUR/USD:** 15 short ayarın hiçbiri iki dönemde birden artı değil. En iyisi EMA 4s 10/50 short: geliştirme +0.13R (102 işlem), doğrulama −0.05R. Long tarafında da her şey geliştirmede eksi ya da sıfır.
- **Altın:** short her yerde eksi (Donchian 4s 100 short: −0.61R geliştirme). Doğrulamada (2025-26) altın sadece yükseldi; T3 short hiç işlem açmadı.
- **Nasdaq:** short her yerde eksi (Donchian 4s 20: −0.21R / −0.46R). Tek istisna T3 geri çekilme short 3R: +0.18R (31 işlem) / +0.21R (5 işlem); doğrulamada işlem çok az, 1.5R ve 2R komşuları zayıf; geçme şartını sağlamıyor.
- Günlük (1d) ayarların çoğu dönemde 1-25 işlem veriyor; karar vermek için çok az.

## Notlar / öğrenilenler
- Altın ve Nasdaq'ta "long trend takibi artı" görünmesi beceri değil, piyasanın yükselişi. Aynı yükselişi taşıyan ama günleri karışık veride de aynı kurallar aynı sıklıkla kazanıyor. Bu kontrol yapılmasaydı 6 "geçen" ayar umut verici görünürdü.
- Short tarafı 3 piyasada da tutmadı; düşüşten kazanmayı fiyat-trend kurallarıyla bu piyasalarda bulamadık.
- Swap kötümser tahmin; gerçek bir hesapta short swap'ı bazen artıdır, ama short brüt sonuçları da (masrafsız) eksi, yani swap sonucu değiştirmez.
