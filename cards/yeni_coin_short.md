# Yeni Coin Short (yeni listelenen coini sat, BTC al) — ARAŞTIRMA

**Durum:** ZAYIF ADAY (2026-11-04). Geliştirme ve doğrulamada artı, ama düşüşler büyük ve 2026'nın ilk çeyreği eksi. Kasa (holdout) kullanılmadı; kasa testine girip girmeyeceğine yönetici oturum ve GUO karar verir. Canlı demo botlarına dokunulmadı.

Beyin fırtınası listesi: `cards/market_notr.md`. Rapor: `results/2026-11-04_market_notr/rapor.md`.

## Hipotez
Binance'e yeni gelen coinler ilk haftalarda heyecanla alınır, sonra erken yatırımcıların ve airdrop alanların satışı başlar. Bu yüzden yeni coin, ilk aylarında BTC'den kötü gider. Coini satıp aynı büyüklükte BTC alırsak piyasanın genel yönünden korunuruz; kazanç sadece "yeni coin BTC'den kötü gitti mi?" sorusundan gelir. Piyasa düşerken de çıkarken de çalışabilir.

## Yön
İkisi de: her işlemde coin **short** + BTC **long** (eşit tutar).

## Giriş koşulları
- [yeni_listeleme] Teknik: coinin Binance USDⓈ-M vadeli piyasasındaki ilk işlem gününden 7 gün sonra, günlük kapanışta | Açıklama: "Bu coin 1 hafta önce listelendi; yeni coinler ilk aylarında genelde BTC'den zayıf gider."
- [hacim] Teknik: o gün 30 günlük ortalama hacimde ilk 100 coin içinde | Açıklama: "Coin yeterince işlem görüyor."
- [yer_var] Teknik: açık işlem sayısı 20'den az | Açıklama: "Risk sınırı dolmadı."

## İşlem yönetimi
- Büyüklük: kasanın %5'i coin short (izole, 1x) + kasanın %5'i BTC long.
- Stop: coin fiyatı giriş fiyatının %30 üstüne çıkarsa (saatlik veride kontrol, kayma eklenerek) iki bacak birden kapanır.
- Süre: en fazla 30 gün; coin listeden çıkarsa son fiyattan kapanır.
- TP yok (süre sonunda çıkış). Not: proje kuralı "TP1 ≥ 1R" sinyal kartları içindir; bu araştırma aşamasında sadece süre/stop çıkışı test edildi.

## Zaman dilimi ve parametreler
Günlük karar, saatlik stop. Komşu ızgara: bekleme 5/7/10/14 gün, süre 20/30/45 gün, stop %30/%60 (24 ayar).

## Sonuçlar (masraf her emirde %0.10 = gidiş-dönüş %0.20, iki bacakta; funding dahil; silinen coinler dahil)
Kart kuralı (7 gün bekle, 30 gün tut, %30 stop, saatlik stop):

| Dönem | Toplam | En büyük düşüş | 2x masraf | İşlem | İşlem başı | BTC al-tut |
|---|---|---|---|---|---|---|
| Geliştirme 2020-24 | **+%109** | %22 | +%97 | 307 (ayda 5) | +%2.7 | +%1200 (düşüş %77) |
| Doğrulama 2025-26/03 | **+%32** | %27 | +%26 | 216 (ayda 14) | +%1.8 | -%28 (düşüş %50) |

- Yıllar: 2020 +%68, 2021 **-%16**, 2022 +%6, 2023 +%16, 2024 +%22, 2025 +%55, 2026 Q1 **-%15**.
- Bacaklar ayrı (işlem başı, bacağın kendi tutarına göre): geliştirmede coin short +%1.7, BTC long +%4.1; doğrulamada coin short +%5.7, BTC long -%1.8. İki dönemde de yeni coin BTC'den %4-6 kötü gitti; asıl kazanç bu fark.
- Kazanma oranı %51-54, işlemlerin %44-47'si stopla kapanıyor. En kötü işlem -%29, en iyi +%46.
- Komşu ayarlar (saatlik stop): geliştirmede **24'ün 24'ü artı** (+%48..+%494). Doğrulamada **24'ün 18'i artı**; %30 stoplu 12 ayarın 12'si artı (+%1..+%33), %60 stoplu ayarlar zayıf. 45 günlük tutma doğrulamada ~0 veya eksi.
- Daha önceki iki hesap (öğretici): her gün eşit ağırlığa döndürülen hesap doğrulamada +%87 gösterdi (gerçekçi değil); stop sadece günlük kapanışta kontrol edilince doğrulamada +%23 ve 5 likidasyon (ör. COAI bir günde 6 katına çıktı). Saatlik stop likidasyonları sıfırladı.

## Zayıflıklar
- Düşüşler büyük (%22-27, komşu ayarlarda %50'ye kadar). 2021 boğasında ve 2026 başında kaybetti.
- 2025'te listeleme sayısı 3 katına çıktı (ayda 14 işlem, aynı anda ~12 açık işlem): kasanın yarısından fazlası short + yarısı BTC long olabiliyor.
- Yeni coinlerde gerçek kayma %0.10'dan büyük olabilir; ani sıkışmalarda stop daha kötü dolabilir (saatlik veri tavan fiyatı göremez).
- Bitget demo sadece ~15 coin listeliyor; yeni coinlerin çoğu orada yok. Canlı denenecekse borsa seçimi ayrıca konuşulmalı.

## Sıradaki adım (önerilen)
1. Yönetici oturum/GUO isterse kasa (2026-04..09) **bir kez** çalıştırılır, kural değiştirilmeden.
2. Kasa artıysa: kağıt üzerinde ileriye dönük takip (gerçek para yok).

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-11-04 | Silinen coinler dahil, günlük + saatlik stop, 24 komşu ayar | Geliştirme +%109, doğrulama +%32, düşüş %22-27 | `results/2026-11-04_market_notr/rapor.md` |

## Kod
- `research/neutral/fetch_newlist_1h.py` (yeni coinlerin ilk ~75 gününün saatlik verisi)
- `research/neutral/newlist_portfolio.py intra` (ızgara), `... intra card` (kart kuralı ayrıntısı)
