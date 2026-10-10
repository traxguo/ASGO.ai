# Pusula araştırma kuyruğu (arka planda sürekli test)

Proje sahibi 2026-10-10'da "backtest arkada hep devam edecek" dedi. Her turda bu listeden sıradaki iş yapılır, sonucu buraya ve ilgili karta yazılır.
Her tur bir **geliştirme** içerir (proje sahibi: "yerinde saymayalım, sürekli müdahale ile geliştirelim"). Bir değişiklik ancak hem eski 16 coinde hem de hiç görülmemiş 20 yeni coinde (`config/pairs_new20.json`) daha iyiyse kabul edilir; sadece eski coinlerde iyi olan değişiklik reddedilir.
Proje sahibi 2026-10-10: "geliştirme sadece ekleme olmasın, yanlış yerleri de çıkarsın." Her geliştirme turunda ekleme kadar **çıkarma** da denenir; aynı kabul kuralı geçerli.
Kural: dondurulmuş `PusulaTrendLong` kağıt takipte değişmez; her yeni fikir ayrı sınıf veya ayrı test olur. Sonuca bakıp kural değiştirilmez.

## Sırada
1. [x] **Öncelik (GUO 2026-10-10: "daha çok scalp tarafındayız, sürekli işlem ve sürekli analiz edilebilecek data")**: hızlı strateji adayı. 1 saatlik mumda, 36 coinde (`config/pairs_all36.json`) günde yaklaşık 1 işlem hedefi. Önce kart (`cards/`), kurallar sabitlenir, maliyet + funding dahil geliştirme dönemi testi. Geçerse doğrulama, sonra Bitget demoya Pusula'nın yanına ayrı sınıf olarak eklenir. Sınırlar: GitHub ücretsiz sunucusu en sık 5 dakikada bir ve gecikmeli çalışır, aylık 2000 dakika; 1 saatlik çalışma sığar, 1-5 dakikalık scalp sığmaz. Daha önceki 5m/1m denemeleri (Aslan v1-v7, Gemini) masraftan önce bile ~0R'di: dar stopta masraf işlem başına 0.2-0.4R yiyor.
   → 2026-10-10 yapıldı: `Nabiz` (1h RSI geri çekilme, günlük trend yönünde). **Elendi**, bkz. Yapıldı.
1b. [ ] **Hızlı aday 2 (Nabız elendikten sonra eklendi):** geri çekilme yerine **kırılım**. Günlük Pusula puanı +3/-3 ve BTC aynı tarafta iken, 1 saatlik kapanış önceki 24 mumun (1 gün) tepesini/dibini ilk kez geçince trend yönünde gir; ortak modül, Model B (sabit 2R/4R), en fazla 3 işlem, 36 coin. Gerekçe: Pusula'nın aynı kırılım tetiği 1h grafikte de kârlıydı (tur 4 stres: 378 işlem, +0.80R, ama trend çıkışıyla ve az işlemle); sabit hedef işlem sıklığını artırır. Nabız masrafsız bile ≈0R'di, yani geri çekilmeden almak işe yaramıyor; kırılım farklı bir davranış. Önce kart, kurallar sabit; long ve short ayrı.
2. [ ] **Çıkarma testleri (GUO 2026-10-10):** PusulaV2'nin her kuralını tek tek kaldırıp dene: BTC filtresi, günlük puan eşiği (+3 yerine +2), 2R'de başabaş, EMA20 çıkışı yerine EMA50, BTC-düşüşte-kapat. Kural kaldırılınca iki coin listesinde de sonuç aynı ya da daha iyiyse kural çıkarılır (daha az kural = daha az ezber). Her tur bir kural.
2b. [ ] Kalabalık 20 yeni coinde (funding verisi gerekiyor).
3. [ ] Batmış / listeden çıkmış coinler testi (LUNA, FTT vb.): bugün listede olan coinleri seçmenin yarattığı iyimserliği ölçmek.
4. [ ] Pusula + Kalabalık birlikte, tek kasada: düşüşler birbirini dengeliyor mu?
5. [ ] Güçlü/zayıf coin sepeti: önce kart, kurallar sabitlenir, sonra test.
6. [ ] Geliştirme: kazanan işlemde pozisyon büyütme yok, ama aynı coinde trend sürerken ikinci kırılımda yeniden giriş.
7. [ ] Geliştirme: coin seçimi. Aynı anda 3'ten fazla sinyal varsa en güçlü 90 günlük getiriye sahip olanı seç.
10. [ ] Pusula'nın haftalık grafikte rejim okuma versiyonu (daha yavaş, daha az işlem).

## Yapıldı
- 2026-10-10 kuyruk 1: hızlı aday `Nabiz` (1h RSI(14) 35/65 dönüşü, günlük Pusula puanı ±3 + BTC filtresi, Model B, 36 coin, en fazla 3 işlem). Geliştirme 2020-2024: 2509 işlem (günde 1.4), **-0.09R**, PF 0.93, DD %97; long -0.07R, short -0.11R; masraf x2 -0.15R; masrafsız ≈0R. **Elendi** (`strategies/retired/nabiz.py`), doğrulamaya bakılmadı. Rapor: `results/2026-10-10_nabiz_gelistirme_36coin/rapor.md`. Yeni fikir eklendi (madde 1b).
- 2026-10-10: PusulaV2 36 coinde birlikte (`config/pairs_all36.json`, en fazla 3 işlem): 233 işlem, +0.86R, DD %30.5. Eski 16'da 210 işlem, +1.20R, DD %26. **Demo 16 coinde kalıyor**: 3 işlem sınırı dolu olduğu için coin eklemek işlem sayısını neredeyse artırmıyor (ayda ~3), sonucu kötüleştiriyor.
- 2026-10-10 tur 3a: hacim onayı 1.5x (`PusulaV2Vol`). **Red**: yeni 20'de +0.46→+0.76R, ama eski 16'da +1.20→+1.17R ve DD %26→%33.
- 2026-10-10 tur 3b: 10 günde 1R'ye ulaşmayan işlemi kapat (`PusulaV2Time`). **Red**: iki listede de kötü.
- 2026-10-10: `PusulaV2` kağıt takibe dondurulmuş sürümün yanına eklendi (`research/forward/pusula_paper.py`).
- 2026-10-10 tur 2a: Bitcoin skoru ≤ -1 olunca long'u kapat (`PusulaTrendLongBtcExit`). **Kabul** (16: +0.95→+1.20R, 20: +0.44→+0.46R; sadece 10 işlem değişti, 9'u iyileşti). `PusulaV2`'ye girdi.
- 2026-10-10 tur 2b: long sadece Bitcoin'den güçlü coinde (`PusulaTrendLongRS`). **Red** (16: +0.72R, 20: +0.27R).
- 2026-10-10 tur 1: short sadece Bitcoin'den zayıf coinlerde (`PusulaTrendRS`). **Red**: eski 16'da +0.57R → +0.52R, yeni 20'de +0.27R → +0.26R. Şart neredeyse hiç işlem değiştirmedi. `results/2026-10-10_pusula_gelistirme1_rs_ozet.md`
- 2026-10-10: Pusula 20 yeni coinde. Sadece long +0.44R (150 işlem, DD %25), long+short +0.27R. En iyi 10 işlem dışında eksi. 9/20 coin artıda. Rapor: `results/2026-10-10_pusula_yeni20coin/rapor.md`. Yeni fikir eklendi (madde 2).
