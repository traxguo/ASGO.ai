# Göreli Güç (haftalık coin sıralaması, long + short) — ARAŞTIRMA

**Durum:** REDDEDİLDİ (2026-11-03, aynı gün). Kasa (holdout) kullanılmadı.

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

## Silinen coin kontrolü (2026-11-03) — eleme nedeni
- data.binance.vision'dan bugüne kadar listelenmiş **tüm** USDT vadeli coinlerin (680, silinenler dahil) günlük verisi indirildi (`research/xsec/fetch_all_daily.py`).
- Her yeniden dengelemede o günün en çok işlem gören 80 coini evren alındı (`research/xsec/xsmom_allcoins.py`, funding hariç).
- Yeni listelenen coinler dahil: short bacağı patlayan yeni coinlerde çöküyor, kasa düşüşü %60-140, birleşik getiri çoğu ayarda eksi.
- En az 180 gün geçmişi olan coinler: ortalama hafif artı ama birleşik toplam ~0 (-35%..+26%), düşüş %42-76.
- En az 365 gün geçmişi olan coinler: neredeyse her ayar hem geliştirmede hem doğrulamada eksi.
- Aynı kod sadece bizim 81 coinle eski sonucu veriyor (kod hatası değil).

**Sonuç:** 81 coinlik listedeki kâr, listenin bugün hâlâ işlem gören "hayatta kalan" coinlerden oluşmasından geliyor. Gerçek hayatta hangi coinin hayatta kalacağını önceden bilemeyiz. Strateji elendi.

**Ders:** coin sıralaması yapan her fikir silinen coinler dahil evrende test edilmeli (`user_data/data/xsec_all_1d.feather`).
