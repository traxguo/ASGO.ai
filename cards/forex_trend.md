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

## Durum: test ediliyor (2026-11-04)

## Sonuçlar
(ilk çalıştırmadan sonra eklenecek)
