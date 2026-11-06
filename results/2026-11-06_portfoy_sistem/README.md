# ASGO Portföy sistemi — ön kayıt (2026-11-06)

Bu dosya **hiçbir test çalıştırılmadan önce** yazıldı ve ayrı bir commit ile kaydedildi. Sonuçlar `rapor.md`'de.
Temel: PR #58 portföy testi (`results/2026-11-05_portfoy/`, kod `research/portfolio/`). Strateji kuralları donuk; burada sadece kasa ayarı ve bir coin filtresi test edilir.

## 1. Risk seviyesi (işlem başı)
- Ölçüt: **doğrulama dönemi (2025-01-01 → 2026-03-31) en büyük düşüşü en fazla ~%15** olan en yüksek seviye seçilir.
- Raporlanan seviyeler: **%0.25** ve bir alt seviye **%0.20**. Her biri için geliştirme ve doğrulama: getiri / düşüş / Sharpe / en kötü ay.
- Kasa (2026-04 → 09) rakamları sadece "daha önce görüldü" etiketiyle gösterilir, seçimi etkilemez.
- PR #58'e göre %0.25'te doğrulama düşüşü -%12.0; yeniden hesapta da ≤ %15 çıkarsa seçim %0.25 olur, çıkmazsa %0.20.

## 2. Coin yaşı kuralı (tek kural, önceden kayıtlı)
- **Kural:** Binance futures'ta listelenmesinin üzerinden **180 günden az** geçmiş coinde işlem açılmaz.
- **Kapsam:** portföydeki tüm kripto işlemleri (Fitil, Derin Fitil, Dalga, PusulaV2). Aslan NAS (Nasdaq) etkilenmez.
- **Yaş ölçümü:** işlem girişi (`t_in`) − coinin Binance USDⓈ-M futures'taki ilk günlük mumu (`user_data/data/xsec_all_1d.feather`, data.binance.vision; bu dosya 2026-03-30'da bitiyor). Veri 2020-01-01'de başladığı için BTC, ETH, BCH'nin ilk mumu 2020-01-01 görünür (gerçek listeleme 2019); onlar için de 2020-01-01 kullanılır (kural onları en fazla 2020 Haziran sonuna kadar dışarıda tutar). Bu yaklaşım önceden bilinerek kabul edildi.
- **Test edilen veri:** sadece geliştirme (2020-01-01 → 2024-12-31) ve doğrulama (2025-01-01 → 2026-03-31). Girişi 2026-04-01 ve sonrası olan işlemler okunur okunmaz atılır; kasa dönemi yüklenmez ve raporlanmaz.
- **Kıyas:** aynı risk seviyesinde (bölüm 1'de seçilen), aynı yuva sınırlarıyla, kuralsız portföy ↔ kurallı portföy. Masraf normal.
- **Kabul ölçütü:** kural portföye **ancak** hem geliştirmede hem doğrulamada (a) toplam getiri daha yüksek **ve** (b) en büyük düşüş daha kötü değilse (eşit ya da daha küçük) eklenir. Biri bile tutmazsa kural eklenmez. Sonuç her iki durumda da raporlanır.
- Başka eşik (90 gün, 365 gün vb.) denenmez; kural sonradan değiştirilmez.

## 3. Kâğıt takip "ASGO Portföy"
- `scripts/paper_portfoy.py`: canlı ileri-test kayıtlarını (Fitil + Derin Fitil, Dalga, Pusula, Aslan NAS donuk hat) tek bir 10.000 USDT kasada, seçilen risk seviyesiyle birleştirir. Sadece kaydedilmiş işlemleri toplar; emir göndermez.
