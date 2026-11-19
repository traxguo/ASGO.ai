# aslan_sikisma — Aslan'ın sıkışma kırılımı (araştırma, 2026-11-19)
Rapor: [`results/2026-11-19_aslan_sikisma/README.md`](../results/2026-11-19_aslan_sikisma/README.md) ·
Kod: [`research/aslan_5dk/sikisma.py`](../research/aslan_5dk/sikisma.py) · İş akışı: `.github/workflows/aslan_sikisma.yml`

## Hipotez
Aslan: fiyat iki bant arasında sıkışıp git-gel yapınca, bandı kıran hareketten sonra iFVG ve ardından MSP kırılımı
iyi giriştir. Proje sahibinin onayıyla (2026-11-19, "Yaptır") 4. fikir hakkı.

## Yön
İkisi de; long ve short ayrı yargılandı.

## Koşullar (ana ayar, long; short simetrik)
- [range] "Son 12-48 mum, genişliği fiyatın %0.22'sini geçmeyen bir bantta; tepeye ve dibe en az ikişer dokunuş."
- [breakout] "Bir mum bant tepesinin üstünde kapattı."
- [ifvg] "Sonraki 2 saat içinde kırılımdan sonra oluşan ters bir 5 dk / 15 dk FVG'nin üstünde kapanış oldu."
- [msp] "Kırılımdan sonraki son 5 dk tepenin üstünde kapanış; giriş bu mumun kapanışı."
- Stop: kırılımdan girişe kadarki en düşük iğne. Hedef, saat, NY açılışı, büyük zaman dilimi: `aslan_5dk` ile aynı.

## Durum: reddedildi (2026-11-19) — kâğıt takip yok
- Long: gel. -0.097R (476), doğ. -0.206R (128); short: gel. -0.196R (496), doğ. +0.082R (142).
- Rastgele girişten kötü (p 0.69 / 0.90). Bilgi ızgarasının hiçbir hali iki dönemde artı değil.
- Sonradan Aslan girişin kırılım mumunun kapanışı olduğunu, iFVG'nin kırılımdan önce bant içinde geldiğini yazdı;
  bu sıra test edilmedi.

## Tekrar edilmez
Kırılım → geri çekilme iFVG → MSP sırası; bant genişliği %0.15-%0.30, 12-48 mum; sabit 2R hedefli hali.
