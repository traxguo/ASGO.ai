# Pusula araştırma kuyruğu (arka planda sürekli test)

Proje sahibi 2026-10-10'da "backtest arkada hep devam edecek" dedi. Her turda bu listeden sıradaki iş yapılır, sonucu buraya ve ilgili karta yazılır.
Her tur bir **geliştirme** içerir (proje sahibi: "yerinde saymayalım, sürekli müdahale ile geliştirelim"). Bir değişiklik ancak hem eski 16 coinde hem de hiç görülmemiş 20 yeni coinde (`config/pairs_new20.json`) daha iyiyse kabul edilir; sadece eski coinlerde iyi olan değişiklik reddedilir.
Kural: dondurulmuş `PusulaTrendLong` kağıt takipte değişmez; her yeni fikir ayrı sınıf veya ayrı test olur. Sonuca bakıp kural değiştirilmez.

## Sırada
1. [ ] PusulaV2'yi kağıt takibe dondurulmuş sürümün yanına ekle (ikisi paralel izlensin).
2b. [ ] Kalabalık 20 yeni coinde (funding verisi gerekiyor).
3. [ ] Batmış / listeden çıkmış coinler testi (LUNA, FTT vb.): bugün listede olan coinleri seçmenin yarattığı iyimserliği ölçmek.
4. [ ] Pusula + Kalabalık birlikte, tek kasada: düşüşler birbirini dengeliyor mu?
5. [ ] Güçlü/zayıf coin sepeti: önce kart, kurallar sabitlenir, sonra test.
6. [ ] Geliştirme: kazanan işlemde pozisyon büyütme yok, ama aynı coinde trend sürerken ikinci kırılımda yeniden giriş.
7. [ ] Geliştirme: coin seçimi. Aynı anda 3'ten fazla sinyal varsa en güçlü 90 günlük getiriye sahip olanı seç.
8. [ ] Geliştirme: stop mesafesine göre işlem atlama (çok geniş stoplu kırılımlar).
10. [ ] Pusula'nın haftalık grafikte rejim okuma versiyonu (daha yavaş, daha az işlem).

## Yapıldı
- 2026-10-10 tur 2a: Bitcoin skoru ≤ -1 olunca long'u kapat (`PusulaTrendLongBtcExit`). **Kabul** (16: +0.95→+1.20R, 20: +0.44→+0.46R; sadece 10 işlem değişti, 9'u iyileşti). `PusulaV2`'ye girdi.
- 2026-10-10 tur 2b: long sadece Bitcoin'den güçlü coinde (`PusulaTrendLongRS`). **Red** (16: +0.72R, 20: +0.27R).
- 2026-10-10 tur 1: short sadece Bitcoin'den zayıf coinlerde (`PusulaTrendRS`). **Red**: eski 16'da +0.57R → +0.52R, yeni 20'de +0.27R → +0.26R. Şart neredeyse hiç işlem değiştirmedi. `results/2026-10-10_pusula_gelistirme1_rs_ozet.md`
- 2026-10-10: Pusula 20 yeni coinde. Sadece long +0.44R (150 işlem, DD %25), long+short +0.27R. En iyi 10 işlem dışında eksi. 9/20 coin artıda. Rapor: `results/2026-10-10_pusula_yeni20coin/rapor.md`. Yeni fikir eklendi (madde 2).
