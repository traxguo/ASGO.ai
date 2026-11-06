# Aslan Nasdaq: reddedilen kurulumlar hunisi ve tek tek filtre gevşetme — 2026-11-06

Kod: [`research/aslan_nasdaq/funnel.py`](../../research/aslan_nasdaq/funnel.py) (huni), [`research/aslan_nasdaq/ablation.py`](../../research/aslan_nasdaq/ablation.py) (gevşetme). Kart: `cards/aslan_liquidity.md` ("Huni ve gevşetme testi").
Neden: Aslan "ayda 10 işlem çok ağır kural demek, esnetilebilir, çok takıyor" dedi. Soru: kurulumlar hangi filtrede ölüyor, ve tek bir filtreyi gevşetmek daha çok VE daha iyi işlem verir mi?

## Ön kayıt (testten ÖNCE yazıldı ve commit edildi; sonradan değiştirilmez)

Veri: NAS100 1 dakikalık HistData, sadece geliştirme 2020-01..2024-12 ve doğrulama 2025-01..2026-03. Kasa (2026-04..09) daha önce bir kez kullanıldı, bu testte yüklenmez.
Başlangıç: dondurulmuş AslanLiq2_1h, günlük yön filtreli, hedef 2R, maliyet %0.010 (gidiş-dönüş).

Her deneme SADECE BİR filtreyi gevşetir/kaldırır, geri kalan her şey dondurulmuş kuraldaki gibi:

| Kod | Filtre | Dondurulmuş | Deneme |
|---|---|---|---|
| A | Teyit penceresi (likidite alındıktan sonra MSS/iFVG beklenen süre) | 12 mum (12 saat) | 24 mum |
| B | Günlük yön filtresi | yön aynıysa | filtre yok |
| C | Haber filtresi (FOMC / CPI / NFP ±1 saat) | var | yok |
| D | En fazla stop mesafesi | %8 | sınır yok |
| E | En az stop mesafesi (20x kaldıraçta %1 risk) | %0.05 | sınır yok |
| F | Aynı anda açık işlem / emir | 1 | 2 |
| G | Limit emrin geçerlilik süresi | 2 mum | 4 mum |
| Birleşik | Tek başına geçen BÜTÜN denemeler birlikte (en az 2 geçen varsa) | | |

Gevşetilmeyenler: "stop kapanışın yanlış tarafında" (geçerli işlem yok) ve "aynı mumda hem long hem short" (tek işlem hakkı ikisini alamaz).

Geçme şartı (dondurulmuş kurala göre, HEM geliştirme HEM doğrulamada hepsi):
1. ayda daha çok işlem,
2. normal maliyette toplam net R daha yüksek,
3. 2 kat maliyette ortalama net R > 0,
4. maliyet öncesi ortalama R rastgele giriş kontrolünün üstünde.

Geçen bir sürüm dondurulmuş kuralın YERİNE geçmez; kağıt takipte onun yanına ayrı satır olarak eklenir (kasa harcandığı için başka sınav yok).

## Sonuç
(çalıştırmadan sonra eklenecek)
