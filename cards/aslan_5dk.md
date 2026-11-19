# aslan_5dk — Aslan'ın 5 dakikalık yapı kırılımı kuralı (araştırma, 2026-11-19)
Rapor: [`results/2026-11-19_aslan_5dk/README.md`](../results/2026-11-19_aslan_5dk/README.md) ·
Kod: [`research/aslan_5dk/run.py`](../research/aslan_5dk/run.py) · İş akışı: `.github/workflows/aslan_5dk.yml`

## Hipotez
Aslan'ın 2026-11-16/17 tarihli 4 gerçek işlemi ve cevapları: 5 dk grafikte trend (tepe-dip dizisi) bozulunca, son dibi/tepeyi
kıran mumun kapanışında gir; stop son ucun iğnesinde; hedef en yakın alınmamış likidite. Planın 3. (son) Nasdaq fikri.

## Yön
İkisi de; yön filtresi yok. Long ve short ayrı yargılandı.

## Koşullar (ana ayar, short; long simetrik)
- [trend_up] "5 dk'da son iki tepe ve son iki dip yükseliyor."
- [msp_break] "Bir mum son dibin altında kapattı."
- [window] "Saat TR 09:00 - 22:00, New York açılışının ilk 15 dakikası değil."
- [near_liquidity] "Girişin ~30 puan yakınında alınmamış ters seviye yok."
- [htf_obstacle] "1 sa / 4 sa ters FVG veya 4 sa alınmamış seviye yakınsa 5 dk FVG/iFVG onayı var."
- Stop: son tepenin iğnesi. Hedef: girişin altındaki en yakın alınmamış seviye (önceki gün, Asya, Londra, 1 sa dip), en az ~20 puan uzakta.

## Durum: reddedildi (2026-11-19) — long ve short geçmedi, kâğıt takip yok
- Long: gel. -0.033R (1295), doğ. -0.015R (305); short: gel. -0.109R (1450), doğ. -0.007R (386).
- Rastgele girişten farksız (p 0.56 / 0.68). Masrafsız da sıfır civarı.
- Aslan'ın göz kararı seçimi kodlanamadı; avantaj varsa orada. Ölçmenin yolu: Aslan'ın kendi işlemlerinin ileriye dönük kaydı.

## Tekrar edilmez
Nasdaq 5 dk saf yapı kırılımı (MSS/MSP) + seviye hedefi; 1/1.5/2R sabit hedefli halleri; sadece NY saatleri.
