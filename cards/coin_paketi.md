# coin_paketi — 8 günlük coin fikri (long ve short), toplu test

**Durum: REDDEDİLDİ (2026-11-09).** 8 fikrin hiçbiri ön kayıtlı çıtayı geçmedi (0/8). Kâğıt takip kurulmadı.
Kurallar getiri hesaplanmadan önce commit edildi (07cb358, ek: b3940c0). Kasa kullanılmadı.

Kod: [`research/coin_batch/batch.py`](../research/coin_batch/batch.py) · Rapor: [`results/2026-11-09_coin_batch/README.md`](../results/2026-11-09_coin_batch/README.md)

## Amaç (sade Türkçe)
Sistem daha sık işlem yapsın diye, daha önce denenmemiş 8 tanınmış fikir aynı kurallarla sınandı: günlük mumlar,
masraf (gidiş-dönüş %0.2) ve gerçek funding dahil, her fikre "rastgele günde aynı işlemi açsaydık" kontrolü.

## Fikirler ve sonuç (ana ayar)
| Fikir | Ne yapıyor | Sonuç |
|---|---|---|
| F1 BTC/ETH trend, long ya da nakit | Fiyat 120 günlük ortalamanın üstündeyse long, altındaysa nakit | Geliştirmede çok iyi, doğrulamada küçük artı; rastgele kontrol p 0.067 ve doğrulamada sadece 12 işlem → geçmedi |
| F2 Coin trend (36 büyük coin) | Son 60 günde yükselen coin long, düşen short | Long geliştirmede iyi doğrulamada eksi, short tam tersi → geçmedi |
| F3 Günlük volatilite kırılımı (BTC/ETH/SOL) | Gün açılışının 0.5 ATR üstü kırılırsa long, altı kırılırsa short, gün sonu çıkış | Ön kayıtlı kural "geçti" göründü ama kuralda ileriye bakma hatası vardı; düzeltilince ikisi de eksi → geçmedi |
| F4 Aşırı düşüş gününü al (10 büyük coin) | Coin bir günde 2.5 standart sapma düştüyse kapanışta al, 3 gün tut | İki dönemde artı ama geliştirmede PF 1.19 ve rastgeleden farkı anlamsız (p 0.32) → geçmedi |
| F5 Haftanın günü (BTC) | Pazartesi long, hafta sonu short | Masraf etkiyi yiyor → geçmedi |
| F6 52 hafta zirvesine yakın coin | Zirvesinin %5 yakınındaki coini al, 14 gün tut | Doğrulamada eksi → geçmedi |
| F7 BTC hakimiyet rejimi | Altcoin sepeti BTC'ye göre güçlüyse sepet, değilse BTC | Doğrulamada eksi, düşüş çok büyük → geçmedi |
| F8 Günlük funding aşırılığı | Funding aşırı yüksek + fiyat dönüyorsa short (tersi long), 5 gün | Short iki dönemde artı ama PF 1.13 (çıta 1.2) → geçmedi |

Rakamların tamamı (geliştirme/doğrulama ortalaması, PF, kazanma oranı, işlem sayısı, düşüş, p değeri) raporda.

## Öğrenilenler
- **İleriye bakma tuzağı:** "Aynı gün iki seviye de değerse işlem yok" kuralı günün geri kalanını bilmeyi gerektiriyor ve
  kaybeden günleri siliyor. F3'ün görünen kârının neredeyse tamamı buradan geliyordu. Gün içi seviyeli kurallarda bundan
  sonra her yön tek başına (seviye değince giriş) test edilecek.
- Altcoin trend takibi (F2) ve 52 hafta zirvesi (F6) 2020-2024 boğasında çok iyi, 2025-2026 düşüşünde eksi: rejime bağlı.
- %0.2 masraf, günlük tutmalı küçük etkileri (haftanın günü, funding) siliyor.
- İzlenecek ama aday olmayan: F4 (aşırı düşüş al) ızgarada 9 ayarın 6'sı iki dönemde artı, z2.0/3 gün komşusu tüm şartları
  sağlıyor; F8 short 6 ayarın hepsinde iki dönemde artı (PF düşük). Bunlar ancak **yeni bir ön kayıtla** ve ileriye dönük
  veriyle (kasa artık geliştirmede kullanılamaz) yeniden sınanabilir; sonuç görüldükten sonra komşu seçilmez.

## Emeklilik gerekçesi
Ön kayıtlı çıtanın (net > 0 ve PF ≥ 1.2 iki dönemde, rastgele kontrol p < 0.05, 2x masrafta artı, doğrulamada ≥ 30 işlem,
düşüş ≤ %25) hiçbir fikrin ana ayarında tamamı sağlanmadı. Kod ve sonuçlar saklanıyor.

## Geçmiş
- 2026-11-09: ön kayıt (07cb358), çıta eki (b3940c0: kazanma oranı ≥ %50 şartı geri alındı, düşüş ≤ %25 eklendi), test: 0/8.
