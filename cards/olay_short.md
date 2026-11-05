# Olay Short (Binance duyurularına göre coin short) — GEÇMEDİ (kasa testi de geçmedi)

**Durum:** REDDEDİLDİ (2026-11-06). Geliştirmede rastgele kontrolü geçemedi (p 0.17), doğrulamada güçlüydü (+0.32R). Denetleyici onayıyla kasa (2026-04 → 2026-09) bir kez çalıştırıldı: +0.042R ama en iyi 3 işlem çıkınca eksi (−0.037R) → kasa şartı da GEÇMEDİ. Kasa artık kullanıldı; bu kural ailesi için tekrar kasa yapılmaz. Not: kasa geçseydi bile en fazla kâğıt takip olacaktı (dev şartı sağlanmadığı için). Ön kayıt 2026-11-05. Kurallar, duyuru listesi ve fiyat getirileri görülmeden ÖNCE yazıldı ve commit edildi. Denetleyici onayı: fiyat dışı olay verisi turu (Ayı Short ailesi kapandıktan sonra, bkz. `cards/ayi_short.md`). Kasa (2026-04 → 2026-09) sadece denetleyici onayıyla bir kez.

## Fikir (sade Türkçe)
Binance bir coini listeden çıkaracağını ya da "izleme etiketi" (Monitoring Tag: "bu coin riskli, silinebilir") koyacağını duyurduğunda, o coin genelde günlerce değer kaybeder: borsalar ve yatırımcılar çıkar, likidite azalır. Duyurudan sonra o coinin vadeli kontratını short'larsak bu düşüşten pay alabiliriz. Fiyat grafiğine değil, gerçek bir olaya dayanır.

## Veri
- Duyurular: Binance duyuru sitesi (CMS API) başlıkları, GitHub sunucusundan çekilir (`research/events/binance_announcements.py`, iş akışı `binance_announcements.yml`). Katalog 161 (Delisting), 49 (Latest News).
- Coin adı başlıktan çıkarılır (ör. "Binance Will Delist ABC, DEF and GHI on 2024-05-10"); sadece Binance USDT vadeli kontratı olan coinler.
- Fiyat: 1 saatlik vadeli mumlar, silinenler dahil (data.binance.vision); funding: `allc_funding.feather`.

## Olay türleri
- **E1 Spot silme duyurusu:** başlık "Delist" içeriyor; "Futures", "Perpetual", "Margin", "Trading Pair", "Earn", "Convert" içermiyor.
- **E2 İzleme etiketi eklendi:** başlık "Monitoring Tag" içeriyor; "Remove" içermiyor.
- **E3 Vadeli kontrat silme duyurusu:** başlık "Delist" + ("Futures" ya da "Perpetual" ya da "USDⓈ-M") içeriyor.
- Aynı coin için önceki olaydan 30 gün içindeki ikinci olay yeni işlem açmaz (ilk olay sayılır; türler arası da geçerli, birleşik kuralda).

## İşlem kuralı (ANA)
- Giriş: duyuru zamanından sonraki **2. saatlik mumun açılışı** (1-2 saat gecikme; ilk dakikaların boşluğu kazanç sayılmaz). Short.
- Stop: girişin %30 üstü, 1 saatlik en yüksek fiyata göre (stop kayması %0.30).
- Çıkış: **7 gün** sonra kapanış; kontratın verisi biterse (vadeli silme/settlement) son mevcut kapanış.
- Risk: işlem başı %1 (R = stop mesafesi %30), en fazla 10 açık işlem.
- Masraf: %0.20 gidiş-dönüş + gerçek funding. 2x masraf: %0.40.
- Komşular (sadece sağlamlık): gecikme 1/2/24 saat; tutma 3/7/14/30 gün; stop %20/%30/%50.

## Kontrol
- **Rastgele tarih kontrolü:** aynı coinler, aynı dönemde (dev/val), kendi olaylarından en az 30 gün uzak rastgele saatlerde aynı kuralla short. 2000 bootstrap. Ana kural %95'lik dilimi geçmeli.

## Geçme şartı
1. Ana (birleşik E1+E2+E3) kural ortalama net R > 0 hem geliştirmede (2020-2024) hem doğrulamada (2025-01 → 2026-03), her dönemde en az 30 işlem. Türler ayrıca raporlanır.
2. Rastgele tarih kontrolünü %95'te geçmeli (iki dönemde de).
3. 2x masrafta artı.
4. Olay sayısı ve en büyük 3 olay çıkarılınca sonuç ayrıca raporlanır (az olay = şans riski).

## Kod / rapor
`research/events/`; rapor `results/2026-11-0X_olay_short/`.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-11-06 | Ana kural (gecikme 2s, 7 gün, stop %30), 237 olay (E1 79, E2 64, E3 94) | Dev +0.029R (61 işlem), val +0.318R (89). 2x masraf: +0.022 / +0.312. Rastgele kontrol: dev p 0.17 (GEÇMEDİ), val p 0.000. En iyi 3 çıkınca: dev −0.064R, val +0.233R. Komşular 36'dan 15'i iki dönemde artı. | `results/2026-11-06_olay_short/rapor.md` |

## Notlar
- Geliştirme döneminde olay az (61 işlem, çoğu 2022-2024; izleme etiketi 2023-08'de başladı, dev'de sadece 3 E2 işlemi). Dev kârı büyük ölçüde LUNA (2022-05) işleminden.
- Kazanç 2025-2026'da belirgin: 2025 +0.22R (63 işlem), 2026 Q1 +0.56R (26 işlem). En güçlü tür E3 (vadeli kontrat silme).
- Gecikme 24 saat olunca kazanç büyük ölçüde kayboluyor: hareketin çoğu ilk gün.
- Gerçek hayat notu: vadeli kontrat silinirken Binance son saatlerde yeni pozisyonu kısıtlar ve settlement fiyatıyla kapatır; test son 1s kapanışı kullanıyor.

## Kasa testi (2026-11-06, denetleyici onayıyla, bir kez, donmuş ana kural)
| | Kasa 2026-04 → 2026-09 |
|---|---|
| İşlem | 58 (E1 19, E2 26, E3 13) |
| Ortalama R | +0.042 (medyan +0.188, PF 1.14) |
| 2x masraf | +0.035 |
| Rastgele kontrol p | 0.047 (sınırda geçti) |
| En iyi 3 çıkınca | **−0.037** ✗ |
| Kasa getirisi / düşüş | +2.3% / 6.2% |
| Türler | E1 +0.13R, E2 +0.07R, E3 −0.14R |
Aylar: nisan ~0, mayıs +0.58R, haziran-ağustos eksi, eylül +0.40R (3 işlem). Şart "en iyi 3 işleme bağlı olmamak" sağlanmadı → **GEÇMEDİ**. Doğrulamadaki güçlü sonuç kasada tekrar etmedi.

Pratik kontroller:
- (b) Vadeli kontrat silme (E3): 2026'daki duyurularda "yeni pozisyon açılamaz" penceresi settlement'tan ~30 dk önce başlıyor; metinden okunabilen 14 işlemin 0'ında giriş bu pencereye düşmüyor. 2022-2025 duyurularının metni farklı, okunamadı. DİKKAT: 2026-10'dan itibaren bazı duyurularda kısıtlama duyuru anında başlıyor (ör. 2026-10-21 PTB/MITO) → E3 artık Binance'te uygulanamaz.
- (a) Bitget'te short edilebilirlik: kural kasada geçmediği için kontrol edilmedi.
Kod: `HOLDOUT=1 python research/events/event_short.py`, `research/events/reduce_only_check.py`.
