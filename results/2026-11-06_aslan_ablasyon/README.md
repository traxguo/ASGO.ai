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

## Sonuç (Actions run 42200460420, PR #63)

### Huni (dondurulmuş kural, 2020-01 .. 2026-03)
Setups (liquidity sweeps that opened a setup): 1670 in 75 months (22.3/month); re-sweeps inside an open setup are not counted again.

| Stage killed at | Setups | Share | Per month | Left after this stage | Long / short |
|---|---|---|---|---|---|
| no confirmation (12 saat içinde MSS / iFVG teyidi gelmedi) | 365 | 21.9% | 4.9 | 1305 | 164 / 201 |
| stop invalid (stop, sinyal kapanışının yanlış tarafında) | 2 | 0.1% | 0.0 | 1303 | 1 / 1 |
| stop too wide (stop %8'den uzak) | 0 | 0.0% | 0.0 | 1303 | 0 / 0 |
| bias neutral (günlük yön nötr (ne yukarı ne aşağı)) | 16 | 1.0% | 0.2 | 1287 | 7 / 9 |
| bias opposite (günlük yön ters) | 728 | 43.6% | 9.7 | 559 | 228 / 500 |
| news (1 saat içinde önemli ABD haberi) | 5 | 0.3% | 0.1 | 554 | 2 / 3 |
| long+short same candle (aynı mumda hem long hem short sinyali) | 0 | 0.0% | 0.0 | 554 | 0 / 0 |
| stop too small (stop çok dar (%0.05 altı)) | 0 | 0.0% | 0.0 | 554 | 0 / 0 |
| already in a trade (zaten açık işlem / bekleyen emir var) | 68 | 4.1% | 0.9 | 486 | 50 / 18 |
| stop before fill (emir dolmadan önce stop'a değdi) | 0 | 0.0% | 0.0 | 486 | 0 / 0 |
| not filled (limit emir 2 mumda dolmadı) | 11 | 0.7% | 0.1 | 475 | 8 / 3 |
| trade (işleme girildi) | 475 | 28.4% | 6.3 | 475 | 273 / 202 |

By year (setups / trades / main killers):

- 2020: 268 setups, 66 trades; bias opposite 123, trade 66, no confirmation 54
- 2021: 276 setups, 73 trades; bias opposite 125, trade 73, no confirmation 56
- 2022: 270 setups, 72 trades; bias opposite 110, trade 72, no confirmation 70
- 2023: 257 setups, 84 trades; bias opposite 119, trade 84, no confirmation 47
- 2024: 256 setups, 73 trades; bias opposite 106, trade 73, no confirmation 66
- 2025: 278 setups, 80 trades; bias opposite 116, trade 80, no confirmation 65
- 2026: 65 setups, 27 trades; bias opposite 29, trade 27, no confirmation 7

Confirmed setups by daily bias (before the bias filter):

- long: 569 confirmed; bias up 334, neutral 7, down 228
- short: 736 confirmed; bias up 500, neutral 9, down 227

Sweeps by level type:

- 4 saatlik dip: 98 setups, 35 trades
- 4 saatlik tepe: 181 setups, 37 trades
- günlük dip: 45 setups, 8 trades
- günlük tepe: 58 setups, 4 trades
- önceki gün dibi: 590 setups, 230 trades
- önceki gün tepesi: 698 setups, 161 trades

trades from sim.replay (dev+val): 475

Aylık döküm: run'ın `aslan-funnel` çıktısındaki `monthly.csv`.

### Tek tek gevşetme
| Variant | Period | Trades | Per month | Long / short | Gross R | Random R | Avg net R | Total net R | Avg net R 2x cost | Total net R 2x cost |
|---|---|---|---|---|---|---|---|---|---|---|
| frozen | dev | 368 | 6.1 | 222 / 146 | +0.086 | -0.010 | +0.066 | +24.3 | +0.046 | +17.0 |
| frozen | val | 107 | 7.1 | 51 / 56 | +0.171 | -0.039 | +0.151 | +16.1 | +0.131 | +14.0 |
| A window24 | dev | 413 | 6.9 | 247 / 166 | +0.062 | +0.008 | +0.042 | +17.5 | +0.023 | +9.6 |
| A window24 | val | 112 | 7.5 | 53 / 59 | +0.092 | -0.019 | +0.073 | +8.2 | +0.054 | +6.1 |
| B nobias | dev | 645 | 10.8 | 285 / 360 | +0.066 | -0.036 | +0.043 | +27.6 | +0.020 | +12.7 |
| B nobias | val | 180 | 12.0 | 78 / 102 | +0.196 | -0.055 | +0.173 | +31.1 | +0.150 | +26.9 |
| C nonews | dev | 372 | 6.2 | 223 / 149 | +0.074 | -0.010 | +0.055 | +20.3 | +0.035 | +12.9 |
| C nonews | val | 108 | 7.2 | 52 / 56 | +0.160 | -0.022 | +0.140 | +15.1 | +0.120 | +13.0 |
| D nomaxstop | dev | 368 | 6.1 | 222 / 146 | +0.086 | -0.010 | +0.066 | +24.3 | +0.046 | +17.0 |
| D nomaxstop | val | 107 | 7.1 | 51 / 56 | +0.171 | -0.039 | +0.151 | +16.1 | +0.131 | +14.0 |
| E nominstop | dev | 368 | 6.1 | 222 / 146 | +0.086 | -0.010 | +0.066 | +24.3 | +0.046 | +17.0 |
| E nominstop | val | 107 | 7.1 | 51 / 56 | +0.171 | -0.039 | +0.151 | +16.1 | +0.131 | +14.0 |
| F maxopen2 | dev | 412 | 6.9 | 251 / 161 | +0.108 | -0.003 | +0.089 | +36.5 | +0.069 | +28.4 |
| F maxopen2 | val | 121 | 8.1 | 63 / 58 | +0.236 | +0.023 | +0.215 | +26.1 | +0.195 | +23.6 |
| G valid4 | dev | 367 | 6.1 | 223 / 144 | +0.089 | -0.007 | +0.069 | +25.3 | +0.049 | +18.0 |
| G valid4 | val | 107 | 7.1 | 51 / 56 | +0.171 | -0.050 | +0.151 | +16.1 | +0.131 | +14.0 |
| combined | dev | 947 | 15.8 | 415 / 532 | +0.030 | -0.023 | +0.006 | +6.0 | -0.017 | -16.1 |
| combined | val | 244 | 16.3 | 103 / 141 | +0.138 | -0.012 | +0.114 | +27.8 | +0.090 | +21.9 |

## Verdict (pass: more trades/month, higher total net R, avg R > 0 at 2x cost, gross above random; all in both dev and val)

- A window24: FAIL (dev: total net R not higher (+17.5 vs +24.3); val: total net R not higher (+8.2 vs +16.1))
- B nobias: PASS
- C nonews: FAIL (dev: total net R not higher (+20.3 vs +24.3); val: total net R not higher (+15.1 vs +16.1))
- D nomaxstop: FAIL (dev: no more trades; dev: total net R not higher (+24.3 vs +24.3); val: no more trades; val: total net R not higher (+16.1 vs +16.1))
- E nominstop: FAIL (dev: no more trades; dev: total net R not higher (+24.3 vs +24.3); val: no more trades; val: total net R not higher (+16.1 vs +16.1))
- F maxopen2: PASS
- G valid4: FAIL (dev: no more trades; val: no more trades; val: total net R not higher (+16.1 vs +16.1))
- combined: FAIL (dev: total net R not higher (+6.0 vs +24.3); dev: avg R at 2x cost -0.017 <= 0)

### Okuma
- Kurulumların en çok öldüğü yer **günlük yön filtresi** (%44, ayda ~10) ve **12 saatte teyit gelmemesi** (%22, ayda ~5). Diğer filtreler neredeyse hiç kurulum öldürmüyor (haber 5, %8 stop 0, küçük stop 0, emir dolmadı 11 kurulum / 75 ay).
- Geçen 2 deneme: **B yön filtresi yok** (ayda 6.1→10.8 / 7.1→12.0 işlem, toplam R dev +24→+28, val +16→+31) ve **F aynı anda 2 işlem** (ayda 6.1→6.9 / 7.1→8.1, toplam R dev +24→+37, val +16→+26).
- B'de işlem başı R dev'de düşüyor (+0.066→+0.043; 2x maliyette +0.020); fazladan gelen ters-yön işlemler zayıf. Short tarafı dev'de eksi (yön filtresiz: -0.076R). Ayrıca B, 2026-11-05'teki kasa çalıştırmasında yanında raporlanmıştı (kasa: 77 işlem, +0.068R, toplam ~+5.2R; dondurulmuş: 46 işlem, +0.154R, ~+7.1R). Kasa ölçüt değildi ama B'nin orada toplamda geride kaldığı bilinmeli.
- F'de aynı anda 2 işlem = aynı anda 2 kat risk (2 x %1). Toplam R artışı kısmen bu ek riskten gelir.
- Birleşik (B + F) geçmedi: dev'de toplam R +6, 2x maliyette eksi. Eklenmez.
- A (24 saat pencere), C (haber yok) toplamı düşürdü; D, E, G neredeyse hiçbir şey değiştirmedi.
- 7 deneme yapıldı; 2 geçiş tesadüf de olabilir. Bu yüzden ikisi sadece kağıt takibe, dondurulmuş kuralın yanına ayrı satır olarak eklendi (forward/paper_aslan_nas_nobias/, forward/paper_aslan_nas_maxopen2/).
