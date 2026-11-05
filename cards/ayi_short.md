# Ayı Short ailesi (düşüş piyasasında coin short) — ÖN KAYIT

**Durum:** ÖN KAYIT (2026-11-05). Kurallar test ÖNCESİ yazıldı ve bu haliyle commit edildi. Sonuç gördükten sonra ana kural değiştirilmez; komşu ayarlar sadece sağlamlık için raporlanır. Kasa (2026-04 → 2026-09) kullanılmaz; ancak denetleyici onay verirse bir kez.

## Amaç (sade Türkçe)
Piyasa düşerken para kazanan, coinleri açığa satan (short) bir kural bulmak. Daha önce denenip elenen fikirler tekrar edilmez: Fitil short aynası, Pompa Söndür, Başarısız Tepki, Göreli Güç, Yeni Coin Short (7g), market-nötr fikirler, 16+ hızlı (scalp) fikir.

## Ortak ayarlar (hepsi için aynı)
- **Veri:** Binance USDT vadeli, silinen coinler dahil 680 coin, günlük mum + funding (`user_data/data/allc_1d.feather`). Hayatta kalan coin yanılgısı yok.
- **Evren U:** o gün en az 180 günlük geçmişi olan ve son 30 günlük ortalama hacme göre en büyük 50 coin.
- **Ayı rejimi BEAR:** BTC günlük kapanış < BTC EMA50 ve EMA50, 5 gün öncekinden düşük.
- **Giriş:** sinyal gününden sonraki günün açılışı (00:00 UTC), short.
- **Masraf:** gidiş-dönüş %0.20 + stop kayması %0.30 + gerçek funding. 2x masraf testi: %0.40.
- **Risk:** işlem başı sermayenin %1'i (R), en fazla 10 açık işlem, aynı coinde aynı anda tek işlem.
- **Dönemler:** geliştirme 2020-01-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31.

## Hipotezler (her birinin ANA kuralı + sağlamlık komşuları)

### H1 — Kırılım Short
Fikir: düşüş piyasasında 20 günün en düşük kapanışını kıran coin düşmeye devam eder (trend takibi, aşağı yönde).
- [bear] BEAR rejimi | "BTC düşüş trendinde."
- [breakdown] kapanış < önceki 20 günün en düşük kapanışı ve kapanış < EMA50 | "{symbol} son 20 günün en düşük kapanışını kırdı."
- Stop: sinyal kapanışı + 2×ATR14 (giriş fiyatına göre %3-%25 arası değilse işlem yok).
- Çıkış: kapanış > önceki 10 günün en yüksek kapanışı, ya da 40 gün.
- Komşular: kırılım N = 10/20/40, çıkış = 5/10/20 gün.

### H2 — BTC Kırılım Sepeti
Fikir: BTC kırılınca en "BTC'ye duyarlı" (yüksek beta) altcoinler daha sert düşer.
- [btc_breakdown] BEAR ve BTC kapanış < önceki 20 günün en düşük BTC kapanışı | "BTC son 20 günün dibini kırdı."
- [high_beta] U içinden son 90 günde BTC'ye betası en yüksek K = 10 coin (BTC hariç).
- Stop: %15 sabit. Çıkış: BTC kapanış > önceki 10 günün en yüksek BTC kapanışı, ya da 20 gün.
- Komşular: K = 5/10/20, stop = %10/%15/%25.

### H3 — Zombi Coin
Fikir: ilgisi ölen (hacmi çöken), uzun vadede çok düşmüş coinler erimeye devam eder; bunların bir kısmı sonradan listeden silinir.
- Evren farklı: en az 365 günlük, 30 günlük ortalama hacim ≥ 2M $ (işlem yapılabilir olsun). BTC rejimi şartı yok.
- [dead] kapanış < SMA200 ve 180 günlük getiri ≤ −%60 ve (30g ort. hacim / 365g ort. hacim) ≤ 0.4 | "{symbol} 6 ayda %{r180} düştü, hacmi yıllık ortalamanın %{qvr}'ine indi."
- Stop %30, 30 gün tut. Öncelik: hacim oranı en düşük olan.
- Komşular: getiri eşiği −%40/−%60/−%80, tutma 14/30/60 gün.

### H4 — Funding Tuzağı
Fikir: fiyat düşerken long'lar hâlâ yüksek funding ödüyorsa, inatçı long'lar sıkışmıştır; pes ettikçe fiyat düşer.
- [own_downtrend] kapanış < EMA20 < EMA50 ve 7 günlük getiri ≤ −%10 (coin U içinde).
- [longs_paying] son 3 günün ortalama günlük funding'i ≥ %0.05 (normal %0.03) | "Fiyat düşerken long'lar hâlâ funding ödüyor."
- Stop: sinyal kapanışı + 2×ATR14 (%3-%25). 7 gün tut.
- Komşular: funding eşiği %0.03/%0.05/%0.08, tutma 3/7/14 gün.

### H5 — Hacimli Çöküş Devamı
Fikir: düşüş piyasasında rekor hacimle sert düşen ve günün dibine yakın kapatan coin, ertesi günlerde de satılır.
- [bear] BEAR rejimi.
- [crash] günlük getiri ≤ −%8, hacim ≥ 3 × önceki 30 gün ortalaması, kapanış günün aralığının alt %25'inde.
- Stop: o günün en yükseği +%1 (%3-%25). 5 gün tut.
- Komşular: düşüş eşiği −%5/−%8/−%12, tutma 2/5/10 gün.

## Geçme şartı (ANA kural için, hepsi birden)
1. Ortalama net R > 0 hem geliştirmede hem doğrulamada, her dönemde en az 30 işlem.
2. **Rastgele giriş kontrolü:** aynı evrenden, aynı sayıda, aynı stop/çıkış kurallarıyla rastgele günlerde açılan short'lar 300 kez simüle edilir (kontrol A: rejim/tetik yok). Ana kuralın ortalama R'si kontrolün %95'lik dilimini her iki dönemde geçmeli. Kontrol B (sadece BEAR günlerinde rastgele) bilgi için raporlanır: tetik mi kazandırıyor, rejim mi, bunu gösterir.
3. 2x masrafta ortalama R > 0 her iki dönemde.
4. Bilgi için: komşu ayarların kaçı iki dönemde de artı, yıllara göre dağılım, en iyi %5 işlem çıkınca sonuç, BTC short-tut kıyası.

Geçen olursa kasa testi için denetleyiciye (ASGO stratejisi (devam)) onay sorulur. Geçen olmazsa günlük veride aile kapanır; 1 saatlik veriyle ikinci tur ayrıca ön kayıtla yazılır.

## Kod
`research/bear_short/` (yazılacak). Rapor: `results/2026-11-0X_ayi_short/`.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|

## 1. tur sonucu (günlük veri, 2026-11-05) — HİÇBİRİ GEÇMEDİ
| Ana kural | Geliştirme | Doğrulama | 2x masraf | Rastgele kontrolü geçti mi |
|---|---|---|---|---|
| H1 Kırılım N20 X10 | −0.037R (353 işlem) | +0.007R (127) | eksi | hayır (p 0.79 / 0.69) |
| H2 BTC Kırılım Sepeti K10 S15 | −0.193R | −0.194R | eksi | hayır |
| H3 Zombi R−60 H30 | −0.157R | +0.021R | eksi/artı | hayır |
| H4 Funding Tuzağı F0.05 H7 | −0.015R (53) | +0.418R (3 işlem) | — | hayır, çok az işlem |
| H5 Hacimli Çöküş X−8 H5 | −0.119R (35) | +0.118R (11) | — | hayır |

- Ayrıntı: `research/bear_short/out_grid.csv`, `out_controls.csv`, `out_yearly.csv`.
- Not (sonradan görülen, KABUL EDİLMEDİ): H4'ün komşusu F0.03 iki dönemde artı (dev +0.12R 267 işlem, val +0.27R ama sadece 25 işlem). Sonuç gördükten sonra seçmek olur; doğrulamada işlem çok az.
- Genel ders: günlük kırılım/trend short'u, silinen coinler dahil evrende rastgele short'tan iyi değil. Düşüşte short kazancı çoğunlukla rejimin kendisinden geliyor, tetikten değil.

## 2. tur ön kaydı (1 saatlik veri, 2026-11-05) — test ÖNCESİ yazıldı
Veri: 1. turdaki U evrenine bir gün bile girmiş 260 coinin (silinenler dahil) 1 saatlik mumları (data.binance.vision). U ve BEAR bir önceki günün kapanışıyla hesaplanır (ileriye bakma yok). Masraf %0.20 gidiş-dönüş + stop kayması %0.10 + funding (gün içi: geçilen her funding saati için günlük funding'in 1/3'ü). 2x masraf: %0.40. Risk %1, en fazla 10 açık işlem.

### H6 — Gün Dibi Kırılımı
- [bear] dünkü kapanışta BEAR; coin dün U içinde ve dünkü kapanış < günlük EMA20.
- [day_low_break] 00:00-19:00 UTC arasında, 1 saatlik kapanış ilk kez dünkü günlük en düşüğün altına iniyor | "{symbol} dünün dibini ({prev_low}) kırdı."
- Giriş: sonraki saat açılışı. Stop: son 3 saatin en yükseği +%0.2 (girişten %1-%6 uzak değilse işlem yok). Çıkış: günün son saatinin kapanışı (23:00 mumu).
- Komşular: çıkış = gün sonu / 6 saat / 24 saat; stop tampon = %0.2 / %0.5.

### H7 — Saat Penceresi (iki aşamalı)
- [bear] dünkü kapanışta BEAR. U içindeki coinler (BTC hariç) eşit ağırlık sepet short.
- Aday pencereler: her başlangıç saati (0-23) × uzunluk 4/6/8/12 saat = 96 pencere. Sadece GELİŞTİRME verisinde masraf sonrası en iyi pencere seçilir; doğrulamada sadece o tek pencere test edilir. Stop yok (sepet).
- Geçme: seçilen pencere doğrulamada masraf sonrası artı, 2x masrafta artı, ve rastgele pencere kontrolünü (aynı uzunlukta, BEAR günlerinde rastgele başlangıç) %95'te geçmeli.

### H8 — BTC Şoku Gecikmesi
- [bear] dünkü kapanışta BEAR.
- [btc_shock] BTC 1 saatlik getirisi ≤ −%1.5.
- [laggard] U içindeki coinin aynı saatteki getirisi ≥ BTC getirisi + %1 (henüz düşmemiş) | "BTC sert düştü, {symbol} henüz düşmedi."
- Giriş: sonraki saat açılışı. Stop %3. Çıkış: 4 saat sonra kapanış. Komşular: tutma 1/4/12 saat, stop %2/%3/%5.

Geçme şartı 1. turdakiyle aynı (iki dönem artı, en az 30 işlem/dönem, rastgele kontrol A %95, 2x masraf artı).
