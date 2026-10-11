# sfp_sweep — ilk eleme (geliştirme 2022-2024, BTC/ETH/SOL, 5m) — 2026-10-11

## GUO'ya not
- **Kârlı mı?** Hayır. Normal masrafla işlem başına ortalama **-0.65R**; 10000 dolarlık test kasası **2022'nin ilk 5 ayında %90 eridi**, yıl sonunda bitti. Masrafsız hesapta bile işlem başına **-0.07R** (yani kuralın kendisinde de avantaj yok).
- **Neden?** Stop iğnenin hemen ucunda, ortalama fiyatın sadece **%0.35-0.4'ü** kadar uzakta. Giriş + çıkış masrafı (%0.2) tek başına işlem başına **~0.5-0.6R** ediyor. İşlemlerin ~%55'i stopla kapanıyor.
- **Günde kaç işlem?** 3 coinde günde **~2 işlem** (en fazla 1 açık işlem kuralıyla; kasa batmasaydı). Kurala uyan sinyal 3 coinde günde ~5.8 tane.
- **Devam edelim mi?** Hayır. İlk elemenin hiçbir şartı tutmadı; 1 saatlik varyant da aynı (-0.55R ile -0.58R). Emekliye ayırmayı öneriyorum. Doğrulama ve kasa verisine bakılmadı.

## Ne test edildi
- Kart: [`cards/sfp_sweep.md`](../../cards/sfp_sweep.md) (test öncesi yazıldı). Kod: [`strategies/candidates/sfp_sweep.py`](../../strategies/candidates/sfp_sweep.py), test: [`tests/test_sfp_sweep.py`](../../tests/test_sfp_sweep.py), analiz: [`research/reports/sfp_sweep_analysis.py`](../../research/reports/sfp_sweep_analysis.py).
- Kural (proje sahibinin tarifi birebir):
  - Bağlam: 15 dk tepe/dipleri (5 dk mumlardan strateji içinde yeniden örneklendi), sol 3 / sağ 3 mum; tepe ancak sağdaki 3. mum kapandıktan sonra açılan mumlarda kullanılır.
  - Short: 5 dk mumu son onaylı tepenin üstüne iğne atar (seviyenin üstüne çıkan **ilk** mum), tepenin altında kapanır, üst iğne ≥ mumun %50'si. Long aynası.
  - Giriş: sinyal mumunun kapanışı → Freqtrade'de sonraki mumun açılışı. Stop iğne ucunun %0.1 ötesi.
  - TP1 %50 EQ'da (güncel tepe ile dibin ortası), sonra stop tam giriş fiyatına; TP2 karşı seviyede. EQ girişin yanlış tarafındaysa işlem yok.
  - Genel kurallar: işlem başına %1 risk (kaldıraç en fazla 10x), en fazla 1 açık işlem (`--max-open-trades 1`), üst üste 3 kayıp → 24 saat işlem yok. Kasa 10000 USDT.
- Dönem 2022-01-01 → 2024-12-31 (`--timerange 20220101-20250101`), veri 2021-12'den (ısınma).
- Maliyet: emir başına %0.1 (komisyon + kayma), kısmi çıkış ayrı emir; funding geçmiş veriden.
- 1R = giriş miktarı × |gerçek giriş fiyatı − stop|. R = net kâr (masraf + funding + kısmi çıkış dahil) / 1R.
- **Hile testi (lookahead-analysis, 2023-01, 30 sinyal):** 3 kayıp duraklaması kapalıyken `SfpSweep` ve `SfpSweep1h` için **geleceği görme yok**. Duraklama açıkken araç "bias" diyor, çünkü her sinyali **tek coinle** yeniden çalıştırıyor, duraklama ise 3 coinin ortak işlem geçmişine bakıyor (sadece geçmiş kapanmış işlemler). Duraklama açık, tek coinlik testlerde (BTC, ETH, SOL ayrı ayrı, 2023-01/02, 20'şer sinyal) bias yok. Not: araç kasayı 10k sabit stake'e çektiği için %1 risk boyutlandırması işlemleri atlıyordu; hile testi için sadece boyutlandırmayı kapatan bir alt sınıf kullanıldı (sinyaller aynı).

## Özet tablo (ana sürüm `SfpSweep`, BTC/ETH/SOL, 1 yuva)
| Koşu | İşlem | Günde | Kazanan | Ort. R | Long R | Short R | PF | Max DD | Artı coin | Artı yıl |
|---|---|---|---|---|---|---|---|---|---|---|
| **Normal masraf (%0.1/emir), 10k kasa** | 1024 | 0.93* | 25.9% | **-0.649*** | -0.657 | -0.643 | **0.35** | **99.9%** | 0/3 | 0/3* |
| Masraf x2 (%0.2/emir) | 636 | 0.58* | 16.5% | -1.178* | -1.196 | -1.162 | 0.16 | 99.9% | 0/3 | 0/3 |
| Düşük masraf %0.03/emir (teşhis) | 1993 | 1.82* | 41.3% | -0.241* | -0.242 | -0.241 | 0.57 | 99.3% | 0/3 | 0/3 |
| Masrafsız (teşhis) | 3355 | 3.06 | 45.5% | -0.070 | -0.082 | -0.058 | 0.85 | 93.6% | 0/3 | 0/3 |
| Büyük kasa, normal masraf (teşhis) | 2213 | 2.02 | 23.3% | -0.732* | -0.721 | -0.744 | 0.37 | — | 0/3 | 0/3 |
| Büyük kasa, masrafsız (teşhis) | 2882 | 2.63 | 46.2% | -0.080 | -0.091 | -0.067 | 0.83 | — | 0/3 | 0/3 |

\* 10k kasa 2022'de erimiş olduğu için (aşağıda) bu koşularda işlemler 2023'te çok küçüldü ve son işlem veri sonuna kadar açık kaldı: kasa birkaç dolara inince TP1 kısmi çıkışı borsanın en küçük emir sınırının altında kaldı, TP emirleri hiç konamadı ve 1 yuva o işlemle **2023-03'ten 2024 sonuna kadar dolu** kaldı (BTC long, 2024 sonunda +1046R gibi anlamsız bir R ile zorla kapandı). Bu tek işlem ortalamaları bozduğu için tablodaki "Ort. R" ve long/short R, veri sonunda zorla kapatılan işlem **hariç** verildi (dahil: normal +0.37R, masraf x2 +2.55R — bunlar tek işlemin sanal etkisidir). İşlem sayısı ve "günde" de bu yüzden düşük. Kural davranışını 3 yıl boyunca görmek için aynı koşu 100 milyon dolarlık kasayla da çalıştırıldı ("büyük kasa", teşhis): orada kasa da sürekli eriyor (%1 risk, işlem başına -0.7R) ama boyutlar 2024 sonuna kadar en küçük emir sınırının üstünde kalıyor; sonuç **-0.73R, her yıl ve her coin eksi**. Büyük kasada da son işlem veri sonunda zorla kapandı (ortalamadan çıkarıldı).

Kasa erimesi (10k, normal masraf): %50 kayıp 2022-02-22'de, %90 kayıp 2022-06-01'de, %99 kayıp 2022-11-18'de. Düşük masrafta (%0.03) %90'a 2022-11'de, masrafsızda 2024-06'da iniyor. 3 kayıp → 24 saat duraklaması normal koşuda 184 kez devreye girdi (184 gün işlemsiz).

### Masraf etkisi
- Stop mesafesi ortancası **%0.35-0.39** (çeyrekler ~%0.26-%0.57). Normal masrafta giriş + çıkış = %0.2 → ortanca **0.51-0.59R** işlem başına; TP1 kısmi çıkışlı işlemlerde 3 emir olduğu için daha da fazla.
- Masrafsız -0.07/-0.08R → kuralın masraf öncesi de hafif eksi. Masraf eklenince -0.65/-0.73R. Masraf x2'de -1.18R.

### Önceden belirlenen varyant: `SfpSweep1h` (1 saatlik tepe/dipler, teşhis)
| Koşu | İşlem | Günde | Ort. R | Long R | Short R | PF | Max DD | Yıllar (ort. R) |
|---|---|---|---|---|---|---|---|---|
| Normal masraf, 10k kasa | 999 | 0.91 | -0.578 | -0.545 | -0.612 | 0.59 | 99.6% | 2022 -0.43, 2023 -0.53, 2024 -0.91 |
| Büyük kasa | 1105 | 1.01 | -0.551 | -0.506 | -0.597 | 0.55 | — | 2022 -0.40, 2023 -0.54, 2024 -0.70 |

Stoplar biraz daha geniş (ortanca %0.49), TP1 daha uzak (ortanca 1.9R), yine de her yıl ve her coin eksi.

### Yıllara göre (büyük kasa, normal masraf, ortalama R)
| Yıl | İşlem | Ort. R | Al-tut (BTC/ETH/SOL eşit ağırlık) |
|---|---|---|---|
| 2022 | 839 | -0.601 | -75.5% |
| 2023 | 875 | -0.732 | +389.1% |
| 2024 | 499 | -0.570 | +83.6% |

10k kasalı normal koşuda: 2022 882 işlem -0.61R, 2023 141 işlem -0.90R (sonra yuva kilitlendi).

### Coinler (büyük kasa, normal masraf)
| Coin | İşlem | Ort. R | Long R | Short R |
|---|---|---|---|---|
| BTC | 878 | -0.636 | -0.453 | -0.817 |
| ETH | 811 | -0.652 | -0.669 | -0.636 |
| SOL | 524 | -0.654 | -0.525 | -0.793 |

(BTC long ortalamasına veri sonunda zorla kapatılan tek işlem dahil.) BTC, ETH, SOL üçü de her koşuda eksi (artıda coin: 0/3).

### TP1 < 1R sayımı (projenin kuralı TP1 ≥ 1R; sinyaller elenmedi, sadece sayıldı)
- Tüm kurala uyan sinyaller (2022-2024, 3 coin): 15 dk'da **6337 sinyalin 2642'si (%42)** TP1 < 1R; 1 saatlikte 1784'ün 384'ü (%22). (`sinyal_sayilari.csv`)
- Alınan işlemler (veri sonunda zorla kapatılan hariç): normal koşuda **1023'ün 401'i (%39)**: TP1 < 1R olanlar -0.64R, TP1 ≥ 1R olanlar -0.65R. Büyük kasada 2212'nin 937'si (%42): -0.72R / -0.74R. Yani sadece TP1 ≥ 1R olan sinyaller alınsaydı da sonuç aynı ölçüde eksi kalırdı.

### Coin sırası kontrolü (en fazla 1 yuva)
| Koşu | İşlem | Ort. R | Long R | Short R |
|---|---|---|---|---|
| Normal sıra (BTC, ETH, SOL), 10k | 1024 | -0.649 | -0.657 | -0.643 |
| Ters sıra (SOL, ETH, BTC), 10k | 1374 | -0.689 | -0.550 | -0.826 |
| Normal sıra, büyük kasa | 2213 | -0.732 | -0.721 | -0.744 |
| Ters sıra, büyük kasa | 2333 | -0.744 | -0.708 | -0.782 |

Sıra sonucu değiştirmiyor (hepsi -0.65 ile -0.75R arası). 10k kasada işlem sayısı farkı, normal sırada yuvanın 2023'te kilitlenmesinden.

### Dayanıklılık: 16 coin (teşhis, normal masraf, 10k kasa)
| Koşu | İşlem | Ort. R | Long R | Short R | PF | Artı coin |
|---|---|---|---|---|---|---|
| 16 coin, 1 yuva | 1455 | -0.686 | -0.637 | -0.728 | 0.38 | 2/16 |
| 16 coin, 16 yuva | 1419 | -0.513 | -0.413 | -0.608 | 0.33 | 0/16 |

İkisinde de kasa 2022'de bitti (2023'te sadece 200 / 14 işlem). 16 yuvada %1 risk + 10x kaldıraçla bir işlem kasanın ~%25'i kadar teminat istediği için aynı anda en fazla ~4 işlem açılabiliyor.

### Al-tut kıyası
BTC/ETH/SOL'u 2022-01-01'de alıp 2024 sonuna kadar tutmak (eşit ağırlık): **+%34.5** (BTC +%102, ETH -%9.5, SOL +%11), coin başına ortalama en büyük düşüş %80. Strateji aynı dönemde kasayı sıfırladı (-%98.6). 16 coinde al-tut +%20.3.

### Sonuç türleri (büyük kasa, normal masraf)
Stop %56, TP1 sonrası başa baş %30, TP2 %14. Stoplanan işlem ortalama **-1.6R** (1R + masraf), TP1 sonrası başa baş -0.1R (TP1 kazancını masraf yiyor), TP2 +1.4/+1.5R. Masrafsız koşuda aynı oranlar: stop -1.0R, TP1 sonrası BE +0.5R, TP2 +2.1R → yine hafif eksi.

## İlk eleme kararı (normal masraf, ana sürüm)
| Şart | Gereken | Sonuç | |
|---|---|---|---|
| Ortalama R | > 0 | -0.649 (büyük kasa -0.732) | ✗ |
| PF | ≥ 1.1 | 0.35 | ✗ |
| Max DD | ≤ %35 | %99.9 | ✗ |
| Artıda coin | ≥ 2/3 | 0/3 | ✗ |
| Artı yıl | ≥ 2/3 | 0/3 | ✗ |

**Geçmedi.** Öneri: emekliye ayır (`strategies/retired/`), karar proje sahibinin.

## Aslan'ın likidite stratejileriyle kıyas
- `aslan_liquidity` (v1-v7) ve `ams_liquidity_mss` da "likidite alındı, geri döndü" fikrini test etti; masraflı sonuçlar -0.11R ile -0.58R arası, **masrafsız ~0R** idi.
- Farklar: burada ayrıca MSS/FVG teyidi yok (tek mum: iğne + geri kapanış + iğne ≥ %50), yön filtresi yok, hedefler sabit R katı değil yapısal (EQ ve karşı seviye), bağlam 15 dk / 1 saat (Aslan'da 1 gün / 4 saat).
- Sonuç **aynı yönde**: masrafsız -0.07R (~0R, hatta hafif eksi), masrafla daha da kötü (-0.65R), çünkü stop iğne ucunda ve çok dar (Aslan'da da "en dar stoplu işlemler en kötüsü" bulunmuştu). Yani likidite alımı + geri dönüş fikrinin bu verilerde ve bu zaman dilimlerinde kenarı görünmüyor; 5 dk'lık dar stopla masraf işi bitiriyor.

## Uygulama notları / yaklaşıklıklar
- **Giriş:** kural "kapanışta giriş" diyor; Freqtrade sonraki mumun açılışında girer (açılış fiyatına emir, hemen dolar). Giriş anında fiyat EQ'yu ya da stopu geçmişse işlem açılmaz. "Limit emir tercih" kuralı yerine bu seçildi; düşük masraf koşusu limit emirli borsayı temsil eder.
- **İlk dokunuş:** bir tepe/dip seviyesinden en fazla bir deneme (seviyeyi geçen ilk 5 dk mumu). Kart test öncesi böyle sabitledi.
- **Başa baş:** TP1'den sonra stop tam giriş fiyatına (ortak modüldeki %0.15 tampon kullanılmadı, kural "breakeven" dediği için).
- **Kaldıraç:** en fazla 10x (`docs/rules.md` 3x diyor; %0.35'lik stoplarda %1 risk 3x'e sığmaz). Ortalama kaldıraç 10x. Likidasyon her zaman stopun en az 2 katı uzakta.
- **3 kayıp kuralı:** kayıp = masraf + funding dahil net kâr < 0; duraklamadan sonra sayaç sıfırlanır; tüm coinler ortak.
- Aynı mumda hem TP hem stop görülürse Freqtrade'in sırası geçerli.
- Kasa erimesinin ardından en küçük emir sınırı yüzünden TP emirlerinin konamaması (yuva kilidi) yukarıda açıklandı; "büyük kasa" koşuları bu etkiden arınmış teşhistir.

## Komutlar
```
FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh lookahead-analysis -c config/pairs_btc_eth_sol.json --strategy-list <SfpSweep/SfpSweep1h, boyutlandırması kapalı alt sınıf> \
    --timeframe 5m --timerange 20230101-20230201 --minimum-trade-amount 10 --targeted-trade-amount 30
FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting -c config/pairs_btc_eth_sol.json --strategy-list SfpSweep SfpSweep1h \
    --timeframe 5m --timerange 20220101-20250101 --max-open-trades 1 --cache none --export trades --breakdown year
# aynı komut --strategy SfpSweep ile: --fee 0.002 / --fee 0.0003 / --fee 0 / -c config/pairs_btc_eth_sol_reversed.json /
# -c config/pairs_wide16.json (--max-open-trades 1 ve 16) / --dry-run-wallet 100000000 (büyük kasa; normal, --fee 0, ters sıra)
python research/reports/sfp_sweep_analysis.py --out results/2026-10-11_sfp_sweep_gelistirme --run normal=... --run masraf_x2=... ...
python research/reports/sfp_sweep_analysis.py --out results/2026-10-11_sfp_sweep_gelistirme --pairs config/pairs_wide16.json \
    --tables analiz_tablolari_16coin.md --run 16coin_1yuva=... --run 16coin_16yuva=...
```

## Dosyalar
- `analiz_tablolari.md` / `.json`: BTC/ETH/SOL koşularının tüm tabloları (taraf, yıl, coin, sonuç türü, TP1 < 1R, stop mesafesi) + al-tut.
- `analiz_tablolari_16coin.md` / `.json`: 16 coin koşuları.
- `ozet.csv`: koşu başına ana rakamlar. `sinyal_sayilari.csv`: kurala uyan tüm sinyaller ve TP1 < 1R sayısı (coin/taraf/zaman dilimi).
- `*_sermaye.png`, `*_R_dagilimi.png`: sermaye eğrileri ve R dağılımları. (Büyük kasa koşularında kasa DD'si 10k'ya göre hesaplandığı için anlamsızdır; R'ye bakın.)
- Ham backtest dosyaları repoya konmadı.
