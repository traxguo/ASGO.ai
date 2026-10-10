# Pusula araştırma kuyruğu (arka planda sürekli test)

Proje sahibi 2026-10-10'da "backtest arkada hep devam edecek" dedi. Her turda bu listeden sıradaki iş yapılır, sonucu buraya ve ilgili karta yazılır.
Her tur bir **geliştirme** içerir (proje sahibi: "yerinde saymayalım, sürekli müdahale ile geliştirelim"). Bir değişiklik ancak hem eski 16 coinde hem de hiç görülmemiş 20 yeni coinde (`config/pairs_new20.json`) daha iyiyse kabul edilir; sadece eski coinlerde iyi olan değişiklik reddedilir.
Kural: dondurulmuş `PusulaTrendLong` kağıt takipte değişmez; her yeni fikir ayrı sınıf veya ayrı test olur. Sonuca bakıp kural değiştirilmez.

## Sırada
2. [ ] Geliştirme: short'u sadece Bitcoin'e göre zayıf coinlerde aç (20 yeni coinde short'lar +0.12R, eski coinlerde eksi; fark coinin Bitcoin'e göre gücü olabilir).
2b. [ ] Kalabalık 20 yeni coinde (funding verisi gerekiyor).
3. [ ] Batmış / listeden çıkmış coinler testi (LUNA, FTT vb.): bugün listede olan coinleri seçmenin yarattığı iyimserliği ölçmek.
4. [ ] Pusula + Kalabalık birlikte, tek kasada: düşüşler birbirini dengeliyor mu?
5. [ ] Güçlü/zayıf coin sepeti: önce kart, kurallar sabitlenir, sonra test.
6. [ ] Geliştirme: kazanan işlemde pozisyon büyütme yok, ama aynı coinde trend sürerken ikinci kırılımda yeniden giriş.
7. [ ] Geliştirme: coin seçimi. Aynı anda 3'ten fazla sinyal varsa en güçlü 90 günlük getiriye sahip olanı seç.
8. [ ] Geliştirme: stop mesafesine göre işlem atlama (çok geniş stoplu kırılımlar).
9. [ ] Geliştirme: Bitcoin düşüş rejimindeyken bekleyen long'ları kapatma.
10. [ ] Pusula'nın haftalık grafikte rejim okuma versiyonu (daha yavaş, daha az işlem).

## Yapıldı
- 2026-10-10: Pusula 20 yeni coinde. Sadece long +0.44R (150 işlem, DD %25), long+short +0.27R. En iyi 10 işlem dışında eksi. 9/20 coin artıda. Rapor: `results/2026-10-10_pusula_yeni20coin/rapor.md`. Yeni fikir eklendi (madde 2).
