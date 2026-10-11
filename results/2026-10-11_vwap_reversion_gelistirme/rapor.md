# vwap_reversion — ilk eleme (geliştirme 2022-2024, BTC/ETH/SOL, 5m) — 2026-10-11

## GUO'ya not
- **Kârlı mı?** Hayır, açık ara zararda. Normal masrafla (komisyon + kayma + funding) işlem başına ortalama **-0.65R** (her işlem ortalama riskin üçte ikisini kaybediyor); PF **0.32**. %1 riskle 10000 USDT'lik kasa **2022 Nisan'da %90 erimiş**, Eylül 2022'de bitmiş durumda.
- **Masrafsız bile eksi:** Hiç komisyon ve kayma olmasa da -0.07R. Yani sorun sadece masraf değil; 5 dakikalık grafikte bu dönüş kurallarının kendisinde avantaj yok. Masraf da işlem başına ~0.5R yiyor (stoplar çok yakın, ortalama %0.4).
- **Günde kaç işlem?** Kasa hiç bitmeseydi (sabit risk, teşhis) BTC/ETH/SOL'de günde **~3.4 işlem** — senin hedefin olan ~3'e uyuyor. Ama 3 yılın her birinde, 3 coinin her birinde, long'da da short'ta da eksi.
- **Sonraki adım:** Devam etmeyi önermiyoruz. Strateji ilk elemeyi geçemedi; emekliye ayırma önerisi senin onayına sunuluyor. Doğrulama ve kasa verisine bakılmadı.

## Ne test edildi
- Kural: proje sahibinin VWAP + EMA20 + RSI "ortalamaya dönüş" kuralları (kart: [`cards/vwap_reversion.md`](../../cards/vwap_reversion.md), testten önce yazıldı). Kod: [`strategies/candidates/vwap_reversion.py`](../../strategies/candidates/vwap_reversion.py).
  - Long: dönüş mumu veya önceki mum günlük VWAP'ın ve EMA20'nin altında kapanmış, son 3 mumda RSI14 < 30, ve dönüş mumu = pinbar (alt fitil ≥ 2 × gövde, kapanış üst yarıda) veya yutan boğa mumu veya sabah yıldızı. Short aynası (RSI > 70).
  - Giriş: dönüş mumunun kapanışına limit emir, 1 mum geçerli. Stop: son 10 mumun en düşük dibi (short: en yüksek tepesi) + %0.05 tampon.
  - TP1 %50: EMA20 (sinyal anındaki değer), sonra stop tam giriş fiyatına. TP2: VWAP (sinyal anındaki). Yakın olan hedef TP1 olur (sinyallerin %13'ünde VWAP daha yakındı). Hedeflerden biri yanlış tarafta veya 0.3R'den yakınsa işlem yok.
  - Risk %1 (stop olursa kasanın %1'i + masraf), kaldıraç en fazla 10x, en fazla 1 açık işlem, art arda 3 kayıptan sonra 24 saat ara.
- **Yaklaşıklıklar:** (1) Kaynak 3m grafik istiyor, 3m veri yok → 5m. (2) "Kapanışta giriş" = Freqtrade'de sonraki mumda kapanış fiyatına limit emir (5m kriptoda sonraki açılış ≈ kapanış). (3) Kaldıraç sınırı 10x (GUO); proje kuralı en fazla 3x — işlemlerin ~%38'i 1R için 3x'ten fazla kaldıraç istiyor. (4) Stop çok dar olup (< ~%0.1) 1R pozisyon 10x'e sığmıyorsa işlem atlanır (BTC/ETH/SOL'de 3 yılda 83 sinyal).
- Dönem: 2022-01-01 → 2024-12-31 (`--timerange 20220101-20250101`), 5m. Kasa 10000 USDT. Maliyet emir başına %0.1 (%0.05 komisyon + %0.05 kayma), kısmi çıkış ayrı emir; funding geçmiş veriden.
- Hile testi (lookahead-analysis, BTC/ETH/SOL, 2023-01, 30 sinyal): `VwapReversion` ve `VwapReversionTp1R` için **geleceği görme yok**. (Not: lookahead-analysis pozisyon boyunu 10000'e sabitleyip kasayı 1 milyar yaptığı için %1 risk boyu hiç sığmıyor ve 0 işlem çıkıyordu; hile testi, sadece boyu ve 3 kayıp kuralını kapatan bir sarmalayıcıyla yapıldı, sinyaller aynı.)
- 3 kayıp kuralı kontrolü: tüm ana koşularda duraklama içinde açılan işlem **0** (16 yuvalı teşhis koşusunda aynı mum içi sıralamadan 3 işlem).

## Önemli: kasa erken bittiği için iki türlü sonuç
Ana koşu (%1 risk, güncel kasa üzerinden, bileşik) kasayı 2022'de bitiriyor: kasa 25 Ocak 2022'de yarıya, 10 Nisan 2022'de %90 aşağıya iniyor. Sonrasında işlemler borsanın en küçük miktarında açılıyor, kısmi çıkışlar en küçük miktarın altında kaldığı için yapılamıyor ve sonuçlar bozuluyor (ör. 2024'te tek bir artık işlem +229R). Bu yüzden 2023-2024 ve yıllık şartlar ana koşuda anlamsız.

Kuralların 3 yılın tamamında ne yaptığını görmek için **plan dışı bir teşhis koşusu** eklendi (sonuçlar görüldükten sonra, karar için değil): **sabit risk** — her işlemin riski 10000'in %1'i = 100 USDT, bileşik değil, kasa hiç bitmiyor. Sinyaller, seviyeler, çıkışlar ve 3 kayıp kuralı aynı. Aşağıdaki R rakamları için asıl okunması gereken budur. (Önce kasayı 10 milyon yapan bir deneme de yapıldı; o da %1 bileşik riskle eridi, kullanılmadı.)

## Özet tablo
| Koşu | İşlem | Günde | Kazanan | Ort. R | PF | Max DD | Long R | Short R | Artı coin | Artı yıl |
|---|---|---|---|---|---|---|---|---|---|---|
| **Ana: normal masraf, %1 bileşik** | 916 | 0.84 | 28.8% | **-0.429** | **0.31** | **99.8%** | -0.154 | -0.709 | 0/3 | 1/3* |
| Masraf x2 (bileşik) | 816 | 0.74 | 13.7% | -0.995 | 0.13 | 100% | -0.453 | -1.489 | 0/3 | 1/3* |
| Düşük masraf %0.03 (bileşik, teşhis) | 2044 | 1.86 | 38.8% | -0.122 | 0.58 | 99.7% | +0.042* | -0.292 | 1/3 | 1/3* |
| Masrafsız (bileşik, teşhis) | 3972 | 3.62 | 41.6% | -0.072 | 0.79 | 96.6% | -0.081 | -0.063 | 0/3 | 1/3 |
| Ters coin sırası (bileşik) | 1274 | 1.16 | 24.3% | -0.797 | 0.34 | 100% | -0.811 | -0.784 | 0/3 | 0/3 |
| **Sabit risk, normal masraf (teşhis)** | **3683** | **3.36** | 30.7% | **-0.648** | **0.32** | 2388R | -0.627 | -0.669 | 0/3 | 0/3 |
| Sabit risk, masraf x2 | 3070 | 2.80 | 20.4% | -1.207 | 0.14 | 3707R | -1.144 | -1.271 | 0/3 | 0/3 |
| Sabit risk, düşük masraf %0.03 | 4251 | 3.88 | 40.2% | -0.247 | 0.64 | 1051R | -0.241 | -0.252 | 0/3 | 0/3 |
| Sabit risk, masrafsız | 4314 | 3.94 | 41.6% | -0.069 | 0.88 | 325R | -0.073 | -0.065 | 0/3 | 1/3 (2024 +0.002) |
| Sabit risk, ters coin sırası | 3715 | 3.39 | 31.1% | -0.625 | 0.34 | 2321R | -0.606 | -0.643 | 0/3 | 0/3 |

\* Bileşik koşularda kasa 2022'de bittiği için tek tük "artı" yıllar/rakamlar en küçük miktarlı artık işlemlerden geliyor (ör. 2024'te 1 işlem +229R / +324R); gerçek bir artı değil.
Max DD: bileşik koşularda kasa düşüşü (%); sabit risk koşularında zirveden en büyük düşüş R cinsinden (100 USDT = 1R; 10000'lik kasa için 100R = kasanın tamamı).

### Long / short (sabit risk, normal masraf)
| Taraf | İşlem | Günde | Kazanan | Ort. R | PF | Toplam R | Funding (USDT) |
|---|---|---|---|---|---|---|---|
| Long | 1812 | 1.65 | 31.1% | -0.627 | 0.33 | -1136 | -519 |
| Short | 1871 | 1.71 | 30.3% | -0.669 | 0.32 | -1252 | +563 |

### Yıllara göre (ortalama R)
| Yıl | Sabit risk toplam | Long | Short | Ana koşu (bileşik) | Al-tut BTC/ETH/SOL (eşit ağırlık) |
|---|---|---|---|---|---|
| 2022 | -0.616 (1259 işlem) | -0.59 | -0.64 | -0.665 (840 işlem) | -75.5% |
| 2023 | -0.742 (1143) | -0.76 | -0.73 | -0.846 (75; kasa bitmiş) | +389.1% |
| 2024 | -0.597 (1281) | -0.54 | -0.64 | 1 artık işlem | +83.6% |

### Coin bazında (sabit risk, normal masraf, ortalama R)
BTC -0.73, ETH -0.65, SOL -0.54. 16 coin (1 yuva, sabit risk): 4625 işlem (günde 4.2), -0.650R, **0/16 coin artıda**.

### Sonuç türleri (sabit risk, normal masraf)
| Taraf | Stop | TP1 sonra başa baş | TP2 |
|---|---|---|---|
| Long | 1043 (%58), ort. -1.55R | 399 (%22), +0.03R | 370 (%20), +1.27R |
| Short | 1108 (%59), ort. -1.62R | 386 (%21), +0.04R | 377 (%20), +1.39R |

İşlemlerin ~%58'i stopla bitiyor ve stop masrafla -1.55R ediyor (stop mesafesi medyan %0.4; giriş + çıkış masrafı %0.2 = ~0.5R). Hedefler (EMA20/VWAP) yakın: TP2'ye ulaşanlar bile ortalama +1.3R. Masrafsızken bile kazanç/kayıp dengesi tutmuyor (-0.07R).

Dönüş mumu türüne göre (sabit risk): pinbar boğa -0.62R (1263), pinbar ayı -0.69R (1254), yutan boğa -0.68R (469), yutan ayı -0.62R (525), sabah yıldızı -0.45R (80), akşam yıldızı -0.62R (92). Hiçbiri artıda değil.

### Önceden belirlenen varyant: `VwapReversionTp1R` (TP1 ≥ 1R, projenin kuralı)
- Sinyal düzeyinde: ana sürümün geçerli 21608 sinyalinin **8143'ünü (%37.7)** eler (13465 kalır). Ham sinyal (uzama + dönüş mumu) 23509; 0.3R kuralı bunların 1901'ini eler.
- Sonuç (sabit risk, normal masraf): 3198 işlem (günde 2.9), **-0.695R**, PF 0.35, long -0.668 / short -0.719, 0/3 coin, 0/3 yıl. Ana koşu (bileşik): 1142 işlem, -0.765R, PF 0.31, kasa %100 eridi. TP1 ≥ 1R kuralı sonucu düzeltmiyor.

### Dayanıklılık (teşhis, normal masraf, bileşik)
- 16 coin, 1 yuva: 1401 işlem, -0.249R (kasa bittikten sonraki artık işlemler ortalamayı bozuyor; 2022: -0.636R), PF 0.40, DD %100, 1/16 coin.
- 16 coin, 16 yuva: 1883 işlem, -0.450R, PF 0.43, DD %100, 2/16 coin.
- Sabit risk, 16 coin 1 yuva: -0.650R, 0/16 coin (yukarıda).

### Sıralama testi
Coin listesi ters (SOL, ETH, BTC): bileşik -0.797R (ana -0.429R; fark kasanın erime hızından ve artık işlemlerden), sabit risk -0.625R (ana -0.648R). Sabit risk koşularında sıra sonucu değiştirmiyor; momentum_5m'deki gibi bir sıralama etkisi yok — her iki sırada da açıkça eksi.

### Al-tut kıyası
BTC/ETH/SOL'ü 2022 başında alıp 2024 sonuna kadar tutmak (eşit ağırlık): **+%34.5** (BTC +%102, ETH -%9.5, SOL +%11; coin başına ortalama en büyük düşüş %80). 16 coin: +%20.3. Strateji kasayı 2022'de bitiriyor; al-tut'un çok gerisinde.

## İlk eleme şartları (normal masraf, ana sürüm, BTC/ETH/SOL)
| Şart | Eşik | Ana koşu (bileşik) | Sabit risk (teşhis) | Geçti mi? |
|---|---|---|---|---|
| Ortalama R | > 0 | -0.429 | -0.648 | **hayır** |
| Profit factor | ≥ 1.1 | 0.31 | 0.32 | **hayır** |
| Max drawdown | ≤ %35 | %99.8 | 2388R | **hayır** |
| Artıda biten coin | ≥ 2/3 | 0/3 | 0/3 | **hayır** |
| Artı yıl | ≥ 2/3 | (kasa 2022'de bitti) | 0/3 | **hayır** |
| (bilgi) Günde işlem | GUO hedefi ~3 | 0.84 (kasa bittiği için) | 3.36 | — |
| (bilgi) Masraf x2 | > 0R | -0.995 | -1.207 | kırılgan |

**Sonuç: ilk elemeyi hiçbir şartta geçemedi.** Masrafsız ve düşük masraflı varsayımlarda da eksi. Öneri: emekliye ayırmak (`strategies/retired/`), karar proje sahibinin. Doğrulama (2025+) yapılmadı, kasa verisine (2026-04 sonrası) dokunulmadı.

## Nasıl çalıştırıldı
```
P3="BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT"
# hile testi (boy ve 3-kayıp kuralını kapatan sarmalayıcı ile; sinyaller aynı)
FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh lookahead-analysis --strategy-path <scratch> --strategy-list VwapReversionLook VwapReversionTp1RLook \
    --timeframe 5m --timerange 20230101-20230201 --pairs $P3 --minimum-trade-amount 10 --targeted-trade-amount 30
# ana koşu
FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --strategy-list VwapReversion VwapReversionTp1R --pairs $P3 --max-open-trades 1 \
    --fee 0.001 --timeframe 5m --timerange 20220101-20250101 --cache none --export trades --breakdown year
# aynı komut --strategy VwapReversion ile: --fee 0.002 / --fee 0.0003 / --fee 0 / --pairs SOL ETH BTC (ters sıra)
# 16 coin: -c config/pairs_wide16.json --max-open-trades 1 ve 16
# sabit risk (teşhis): custom_stake_amount'u 10000 sabit kasaya göre hesaplayan sarmalayıcı (VwapReversionFixed),
#   --dry-run-wallet 1000000, diğer her şey aynı
python research/reports/vwap_reversion_analysis.py --out results/2026-10-11_vwap_reversion_gelistirme --run normal=... ...
```
Ayrıntılı tablolar (her koşu: yıl, coin, sonuç türü, mum türü, masraf R'si, kaldıraç ihtiyacı, duraklama sayısı, grafikler): [`analiz_tablolari.md`](analiz_tablolari.md). Ham sayılar: `ozet.json`.
