# aslan_bant — Aslan'ın bant kırılımı (araştırma, 2026-11-19)
Rapor: [`results/2026-11-19_aslan_bant/README.md`](../results/2026-11-19_aslan_bant/README.md) ·
Kod: [`research/aslan_5dk/bant.py`](../research/aslan_5dk/bant.py) · İş akışı: `.github/workflows/aslan_bant.yml`

## Hipotez
Aslan: fiyat 1-4 saat iki seviye arasında sıkışır; MSP bandın direnci/desteğidir; gövdeyle kırınca girilir.
FVG/iFVG şart değil. Hedef 40-80 puan. Proje sahibinin onayıyla 5. ve son Nasdaq fikri.

## Yön
İkisi de; long ve short ayrı yargılandı.

## Koşullar (ana ayar, long; short simetrik)
- [band] "Son 12-48 mum 40-150 puanlık bir bantta; dirence ve desteğe en az ikişer dokunuş."
- [msp_break] "5 dk mum direncin üstünde kapattı; giriş bu kapanış."
- [window] "Saat TR 09:00 - 22:00, NY açılışının ilk 15 dakikası değil."
- Stop: kırılım bacağındaki en yakın FVG'nin ~5 puan altı (yoksa bant içindeki son dip), en fazla 100 puan.
- Hedef: 40-80 puan uzaktaki en yakın alınmamış seviye, yoksa 60 puan.

## Durum: reddedildi (2026-11-19) — kâğıt takip yok
- Long: gel. -0.081R (2685), doğ. -0.117R (695); short: gel. -0.066R (2206), doğ. -0.049R (588).
- Rastgele girişten farksız (p 0.76 / 0.12); 2020-2026 her yıl iki yönde eksi.

## Tekrar edilmez
Nasdaq 5 dk bant kırılımı (kapanışta giriş), bant 12-48 mum, %0.17-%0.62; sabit 60 puan hedefli ve stop bant ucunda
halleri. Kodlanmış Aslan ailesi kapandı.
