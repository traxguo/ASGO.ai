# Market-nötr long+short fikirler (beyin fırtınası) — ARAŞTIRMA

**Durum:** 6 fikir test edildi (2026-11-04). 5'i elendi, 1'i ("Yeni Coin Short") zayıf aday olarak ayrı kartta: `cards/yeni_coin_short_btc_hedge.md`. Kasa (holdout, 2026-04..09) kullanılmadı. Canlı demo botlarına dokunulmadı.

Rapor ve ham çıktılar: `results/2026-11-04_market_notr/`. Kod: `research/neutral/`.

## Ortak kurallar (her testte aynı)
- **Evren (hayatta kalan coin hatası yok):** Binance'te bugüne kadar listelenmiş 680 USDT vadeli coin, sonradan silinenler dahil (`research/xsec/fetch_all_daily.py`). Her gün o günün en çok işlem gören 50 coini (30 günlük ortalama hacim), en az 180 günlük geçmişi olanlar.
- **Funding dahil:** aynı coinlerin funding geçmişi indirildi (`research/neutral/fetch_funding_daily.py`).
- **Masraf:** her bacak için gidiş-dönüş %0.20; ayrıca %0.40 ile (2 kat) kontrol.
- **Dönemler:** geliştirme 2020-01..2024-12, doğrulama 2025-01..2026-03. Günlük kapanış verisiyle karar, o kapanışta işlem.
- **Kıyas:** BTC al-tut geliştirmede **+%1200** (en büyük düşüş %77), doğrulamada **-%28** (düşüş %50). ETH: +%2454 / -%37.
- Kurallar testten önce yazıldı, sadece küçük komşu ayar ızgarası denendi.

## Fikir listesi (beyin fırtınası)
| # | Fikir (sade Türkçe) | Test? | Sonuç |
|---|---|---|---|
| a | **Coin çiftleri:** birlikte hareket eden iki coinin arası açılınca pahalı olanı sat, ucuz olanı al, ara kapanınca çık | Evet | ELENDİ |
| b1 | **ETH/BTC oranı, geri dönüş:** oran çok sapınca ortalamaya döner diye ters işlem | Evet | ELENDİ |
| b2 | **ETH/BTC oranı, trend:** oran yükseliyorsa ETH al BTC sat, düşüyorsa tersi | Evet | ELENDİ (tutarsız) |
| c | **Piyasadan arındırılmış geri dönüş:** son 1-3 günde BTC'ye göre en çok düşeni al, en çok çıkanı sat | Evet | ELENDİ |
| d | **Funding carry (kendi fikrim):** funding'i en eksi coinleri al, en artı coinleri sat; funding'i topla | Evet | ELENDİ (kırılgan) |
| e | **Yeni Coin Short (kendi fikrim):** yeni listelenen coini 1 hafta sonra sat, karşılığında BTC al, 1 ay tut | Evet | **ZAYIF ADAY** → `cards/yeni_coin_short_btc_hedge.md` |
| f | **Sakin coin al, oynak coin sat (kendi fikrim):** BTC'ye göre risk eşitlenmiş | Evet | ELENDİ (tutarsız) |
| g | Dalga/Fitil long'larını BTC short ile korumak (piyasa riskini sil, sadece coin seçme becerisi kalsın) | Hayır | Canlı botlar dondurulmuş; 2026-11-30 sonrası araştırılabilir |
| h | Spot al + vadeli sat (nakit-carry), sadece funding toplamak | Hayır | Spot hesabı gerekir; BTC funding yıllık brüt ~%17 (2020), %31 (2021), %4-12 (2022-24), %5 (2025). Masraf sonrası mevduata yakın, "işlem stratejisi" değil |
| i | BTC hareketinden sonra geç kalan altcoini yakalamak (dakikalık gecikme) | Hayır | Kısa vadeli 20+ fikir masrafa takıldı (`cards/kalabalik.md`, short_trade_grid); aynı sonuç beklenir |
| j | Sektör sepetleri (L1, DeFi, meme) arası güç | Hayır | `cards/goreli_guc.md` ile aynı sorun (silinen coinlerde kâr kayboldu) |
| k | Hafta sonu / saat etkisi long-short | Hayır | Funding saati etkisi daha önce elendi |
| l | Coin çiftleri saatlik veride | Hayır | Günlükte masrafsız bile ~0; saatlikte masraf daha ağır |

## Sonuçlar (masraf %0.20 + funding, toplam getiri; parantezde en büyük düşüş)

### (a) Coin çiftleri — ELENDİ
Her ay: 50 coin içinden son 180 günde en çok birlikte hareket eden P çift (her coin en fazla 2 çiftte). Fark = log(A) − b·log(B). Z-skor ±GİRİŞ'te gir, 0'da çık, ±4'te stop, en fazla 20 gün. Izgara: giriş 1.5/2/2.5, pencere 20/30/60 gün, P 10/20 (18 ayar).
- Doğrulamada **18 ayarın 18'i eksi** (-%7 ile -%17). Masrafsız bile doğrulamada hepsi eksi.
- Geliştirmede en iyisi (giriş 2.5, pencere 30, P10) +%19 (düşüş %12), işlem başına +%0.44; ama doğrulamada -%8.5.
- Kazanma oranı %50-65 ama kaybedenler büyük: arası açılan coinler genelde geri dönmüyor (biri haber alıyor/çöküyor).

### (b) ETH/BTC oranı — ELENDİ
- Geri dönüş (9 ayar): hepsi her iki dönemde eksi (-%10 ile -%62).
- Trend (6 ayar): geliştirmede 20 günlük artı (+%30), 50/100 günlük eksi (-%12, -%26); doğrulamada 50/100 günlük artı (+%50, +%18), 20 günlük düz versiyon hariç. Aynı ayar iki dönemde birden çalışmıyor. ETH/BTC 2025'te tek yönlü düştüğü için doğrulama trend lehine.

### (c) Piyasadan arındırılmış geri dönüş — ELENDİ
60 günlük BTC betası ile coinin "kendi" hareketi; son L günün en çok düşen K coinini al, en çok çıkan K coinini sat, H gün tut. Izgara L 1/2/3, H 1/2/3, K 5/10 (18 ayar).
- Masrafsız geliştirmede çoğu ~0; masrafla **18'in 18'i geliştirmede eksi** (-%37 ile -%98). Günlük dönüş çok yüksek, masraf her şeyi yiyor.

### (d) Funding carry — ELENDİ (kırılgan)
Son LB günün funding toplamına göre en eksi K coin long, en artı K coin short, H gün tut. Izgara LB 3/7/14, K 5/10, H 1/7.
- K=5: geliştirmede çok iyi (+%140..+%230) ama doğrulamada 6'nın 5'i eksi, düşüş %45 → elendi.
- K=10: geliştirme +%30..+%136 (düşüş %24-34), doğrulama 6'nın 5'i artı (-%15..+%36). 
- **Neden elendi:** kârın tamamı toplanan funding'den. Doğrulamada fiyat tarafı her ayarda kaybettiriyor ( -%25..-%48): funding'i eksi olan coin gerçekten düşüyor, artı olan çıkıyor. Doğrulamada en iyi 5 gün çıkarılınca hepsi eksi (-%16..-%43). En az 365 gün geçmişi olan coinlerle doğrulama ~0 (-%6..+%17). 2x masrafta doğrulama ~0.

### (f) Sakin coin al / oynak coin sat — ELENDİ (tutarsız)
Her 7 günde 30 günlük oynaklığa göre en sakin K coin long, en oynak K coin short. Beta eşitlenmiş: K5 geliştirme +%64 (düşüş %56), doğrulama +%14 (düşüş %56); K10 geliştirme +%9, doğrulama +%54. Dolar eşit versiyon geliştirmede eksi. Düşüşler çok büyük, ayarlar arası tutarsız.

### (e) Yeni Coin Short — ZAYIF ADAY
Ayrıntı: `cards/yeni_coin_short_btc_hedge.md`.

## Öğrenilenler
- Market-nötr fikirlerde "kâr" kolayca **hayatta kalan coin hatasından** ya da **günlük yeniden dengeleme yanılgısından** gelebiliyor. Yeni Coin Short ilk hesapta (her gün eşit ağırlığa döndürme) doğrulamada +%87 görünüyordu; gerçek pozisyonlarla (eşitleme yok, izole marjin) +%23'e düştü. Short pozisyon fiyat çıktıkça büyür; her gün küçültmek gerçek hayatta ek işlem ve masraftır.
- Kısa vadeli (1-3 gün) coin içi geri dönüş fikirleri masrafı geçemiyor; sonuç önceki kısa vade taramalarıyla aynı.
