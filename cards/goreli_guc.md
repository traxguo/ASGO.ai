# Göreli Güç (haftalık coin sıralaması, long + short) — ARAŞTIRMA

**Durum:** ilk tarama umut verici (2026-11-03). Strateji değil, aday. Kasa (holdout) kullanılmadı.

## Fikir (sade Türkçe)
Coinleri zamana göre değil, birbirine göre karşılaştırırız. Her 2-3 haftada bir, son 14 günde en çok yükselen birkaç coini **alırız** (long), en çok düşen birkaç coini **satarız** (short). Para iki tarafa eşit bölünür. Piyasa toptan düşse de çıksa da önemli olan "güçlü olan zayıftan iyi gidiyor mu?" sorusudur. Bu yüzden bot düşüş piyasasında da çalışır.

## Kurallar (taranan)
- Evren: 81 coin (`config/pairs_wide81.json`), sadece o tarihte verisi olan coinler.
- Her R günde bir (10/14/21), günlük kapanışta: son L gün (10/14/21) getirisine göre sırala.
- En iyi K coin long, en kötü K coin short (K = 3/5/8), eşit ağırlık, R gün tut.
- Masraf: her bacak, her yeniden dengelemede %0.20 (2x masraf testi: %0.40). Funding dahil.
- Kod: `research/xsec/weekly_xsmom.py`, sağlamlık: `research/xsec/xsmom_robust.py`.

## Sonuç (işlem başına değil, dönem başına ortalama net getiri)
- 81 coin: momentum (güçlüyü al, zayıfı sat) komşu 27 ayarın **27'si** hem geliştirmede (2020-2024) hem doğrulamada (2025-2026/03) artı. Başlangıç gününü kaydırınca da çoğu artı kalıyor.
- Örnek L14 K3 R21: dönem başı dev +1.6%, val +2.4%.
- 2x masrafta da artı (L14 K5 R21: dev +1.5%, val +1.6%).
- Tersi (zayıfı al, güçlüyü sat) her yerde eksi.
- **Zayıflıklar:** düşüşler büyük (kasa %23-70 geriliyor). 15 demo coinde doğrulamada eksi (az coin yetmiyor). Long tek başına 2025'te, short tek başına 2020-24'te kötü; ikisi birlikte çalışıyor. Bugün listede olan coinlerle test edildi (sonradan silinen coinler yok, sonucu güzelleştirebilir).

## Sıradaki
1. Kasa düşüşünü azaltan basit yollar (boyut, daha çok coin) — kural eklemeden önce.
2. Silinen coin etkisinin kaba tahmini.
3. Sonra kasa testi (bir kez), geçerse 76 coinde kâğıt takip (Bitget demo sadece 15 coin listeliyor).
