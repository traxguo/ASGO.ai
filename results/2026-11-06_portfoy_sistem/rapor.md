# ASGO Portföy sistemi — risk seviyesi, coin yaşı kuralı, kâğıt takip (2026-11-06)

Ön kayıt: `README.md` (bu klasör, testlerden önce ayrı commit ile kaydedildi). Temel: PR #58 portföy testi (`results/2026-11-05_portfoy/`). Strateji kuralları ve demo botlar değişmedi.
Kod: `research/portfolio/system.py` (testler), `scripts/paper_portfoy.py` (kâğıt takip). Ham sonuçlar: `summary.json`, `equity_*.csv`.

## GUO'ya not
- **Risk seviyesi: işlem başı %0.25.** Doğrulama döneminde (2025-01 → 2026-03) en büyük düşüş -%12.0, sınır (%15) içinde. %0.20'de düşüş -%9.8 ama kâr da azalıyor; %0.25 sınırı karşılayan en yüksek seviye.
- **Coin yaşı kuralı ("180 günden genç coinde işlem yok") portföye EKLENMEDİ.** Doğrulamada işe yaradı (+%41.8 → +%45.2, düşüş aynı), ama geliştirmede getiriyi düşürdü (+%1.884 → +%1.102). Önceden yazılan şart "iki dönemde de daha iyi" idi; tutmadı.
- **Yeni: "ASGO Portföy" kâğıt takibi.** Beş stratejinin canlı kayıtları tek bir 10.000 USDT kasada, %0.25 riskle toplanıyor; her saat güncelleniyor ve canlı panelin en üstünde büyük çizgi olarak görünüyor. Emir yok. Bugünkü durum: 9.809 USDT (-%1.9), 18 kapanan işlem.

## 1. Risk seviyesi (aynı işlemler, normal masraf, PR #58 portföyü)
| Risk / işlem | Dönem | Getiri | Yıllık | En büyük düşüş | Sharpe | En kötü ay |
|---|---|---|---|---|---|---|
| **%0.25** | Geliştirme 2020-24 | +%1.884 | +%82 | -%39.6 | 1.85 | -%13.7 (2024-04) |
| **%0.25** | **Doğrulama 2025-01 → 2026-03** | **+%41.8** | +%32 | **-%12.0** | 1.23 | -%2.6 (2025-04) |
| %0.25 | Kasa 2026-04 → 09 (daha önce görüldü) | +%20.2 | +%44 | -%18.8 | 1.41 | -%6.3 (2026-07) |
| %0.20 | Geliştirme 2020-24 | +%1.134 | +%65 | -%33.8 | 1.82 | -%11.2 (2024-04) |
| %0.20 | Doğrulama 2025-01 → 2026-03 | +%33.2 | +%26 | -%9.8 | 1.22 | -%2.0 (2025-04) |
| %0.20 | Kasa 2026-04 → 09 (daha önce görüldü) | +%16.5 | +%36 | -%15.3 | 1.41 | -%5.1 (2026-07) |

- Seçim kuralı (önceden yazıldı): doğrulama düşüşü ≤ ~%15 olan en yüksek seviye → **%0.25**. Kasa satırı seçimi etkilemedi; zaten PR #58'de görülmüştü.
- En yüksek toplam pozisyon: %0.25'te kasanın 3.0 katı, %0.20'de 2.4 katı.
- Dikkat: geliştirme dönemindeki düşüş (-%40 / -%34) sınırın çok üstünde. Kaynağı Dalga'nın 2021-23 ayı piyasası ve 2024 düşüşü. Sınır doğrulamaya göre konuldu; yatırımcıya gösterilirken geliştirme düşüşü de söylenmeli.

## 2. Coin yaşı kuralı (tek kural, ön kayıtlı)
Kural: Binance futures'ta 180 günden kısa süredir listelenen coinde işlem açılmaz (Fitil, Derin Fitil, Dalga, PusulaV2; Aslan etkilenmez). Risk %0.25. Kasa dönemi yüklenmedi.

| | Geliştirme getiri / düşüş / Sharpe / en kötü ay | Doğrulama getiri / düşüş / Sharpe / en kötü ay |
|---|---|---|
| Kuralsız | +%1.884 / -%39.6 / 1.85 / -%13.7 | +%41.8 / -%12.0 / 1.23 / -%2.6 |
| 180 gün kuralı | +%1.102 / **-%38.4** / 1.63 / -%12.2 | **+%45.2** / -%12.0 / 1.32 / -%2.0 |
| Kabul şartı | getiri ↑ **tutmadı**, düşüş tuttu | getiri ↑ tuttu, düşüş eşit (tuttu) |

**Karar: kural eklenmedi** (iki dönemde birden şart sağlanmadı).

Kuralın attığı sinyaller (giriş dönemine göre):
| Strateji | Geliştirme | Doğrulama |
|---|---|---|
| Fitil | 414 | 22 |
| Derin Fitil | 6 | 52 |
| Dalga | 118 | 1 |
| PusulaV2 | 11 | 0 |

Strateji katkısı (kasa %, işlem anındaki kasaya göre toplam): geliştirmede Dalga +%194 → +%136, Fitil +%140 → +%115; doğrulamada Derin Fitil +%7.9 → +%11.8, Fitil +%9.3 → +%7.4.
Okuma: geliştirmede atılan 549 sinyalin 427'si 2020-21'de. Dalga ve Pusula'nın attıkları çoğunlukla 2020 başında listelenen büyük coinler (LINK, TRX, ETH, XRP): Binance futures o yıl listeyi yeni kuruyordu ve veri 2020-01'de başladığı için 2020 ilk yarısında neredeyse her coin "genç" sayılıyor (ön kayıtta yazıldı). Dalga'nın 2020 yaz yükselişindeki işlemleri bu yüzden kesildi. Fitil'in attıkları gerçekten genç coinler (AVAX, 1000BONK, SUSHI, CRV); geliştirmede bunlar kârlıydı. Doğrulamada kural Derin Fitil'in genç coinlerdeki kayıplarını kesti. Fitil'in 2026 yaz kaybı kasa döneminde olduğu için bu testte görülmedi ve görülmemeliydi. Kural sonradan değiştirilmez (ör. 2020'yi hariç tutmak ön kayıtta yoktu).

## 3. Kâğıt takip "ASGO Portföy"
- `scripts/paper_portfoy.py`, her saat `ASGO Portfoy paper tracking` işiyle (`.github/workflows/paper_portfoy.yml`) çalışır, `forward/paper_portfoy/` (state.json, trades.csv, ozet.md) yazar.
- Kaynaklar: Fitil + Derin Fitil kâğıt (`forward/paper_fitil`, gerçek fiyat), Dalga demo (`forward/bitget_demo_dalga`), Pusula v2 kâğıt (`forward/pusula_kagit.json`), Aslan Nasdaq donuk hat (`forward/paper_aslan_nas`, gevşek sürümler hariç).
- Kasa: 10.000 USDT, 2026-10-01 başlangıç. R ile ölçülen işlem: kâr = girişteki kasa × %0.25 × R. Fitil/Derin (stopsuz): pozisyon = kasa × %0.25 / %4 (backtest ile aynı). Açık işlemler kapanınca yazılır.
- Sınırlar: Dalga demo botu "coin demo hesapta yok" diye atladığı sinyallerin fiyatını kaydetmiyor, o sinyaller portföyde de yok. Dalga demo fiyatlarıyla çalışıyor (gerçek fiyat kontrolü yok). Fitil kâğıt takibi masrafı %0.13 sayıyor (backtest %0.20).
- Bugün (2026-11-06): 9.809 USDT, -%1.9, en büyük düşüş %2.0, 18 kapanan (5 kazanan), 1 açık. Pusula v2 -133, Fitil -107, Derin +49 USDT; Dalga ve Aslan'da henüz kapanan işlem yok. 5 haftalık kayıt bir şey kanıtlamaz.
- Canlı panel (`/panel`): en üstte "ASGO Portföy" kutusu ve kasa grafiği. Panel GitHub'daki main dalını okuduğu için bu değişiklik main'e girince görünür.

## Zayıf yanlar (gizlenmez)
- %0.25'te bile geliştirme düşüşü -%40. Doğrulama sınırı sağlanıyor ama uzun ayı piyasası yaşanırsa düşüş büyür.
- Coin listeleme tarihi veri dosyasının ilk mumundan alındı; BTC, ETH, BCH için 2019 tarihi yerine 2020-01-01 kullanıldı.
- Kâğıt portföy farklı ortamları birleştiriyor (kâğıt + demo); tek ortak ölçü R ve aynı risk kuralı.
