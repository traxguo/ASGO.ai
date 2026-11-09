# Kuyruk 32 — temelin dayanıklılık teşhisi (eşik komşuluğu + başlangıç tarihi) — 2026-11-09 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** Pusula'nın araştırma temeli (`PusulaV2NoBe`) şans eseri tutturulmuş tek bir ayar mı, yoksa ayarlar biraz oynatılınca da çalışan sağlam bir kural mı? Bir de: 2020-21'in büyük yükselişini dışarıda bırakıp daha geç başlasaydık ne olurdu?
- **Cevap 1 (ayarlar): sağlam bir düzlük, sivri tepe değil.** Beş ayarın her birini önceden belirlenmiş iki değere çektik (10 komşu, iki coin listesi = 20 koşu). **20 koşunun hepsi artıda**; hiçbir komşu sonucu eksiye çevirmedi. En kötü komşu ortalaması eski 16'da +0.55R, yeni 20'de +0.34R (temel +1.35R / +0.61R).
- **Ama büyüklük ayara duyarlı:** toplam kâr komşular arasında yaklaşık 2 kat oynuyor (eski 16'da 151R – 390R, yeni 20'de 56R – 142R). En duyarlı ayar günlük hızlı EMA (20 yerine 15: eski 16'da kâr yarıya iniyor) ve dip stopu penceresi (10 yerine 12: yeni 20'de kâr yarıya iniyor). Yeni 20'de 10 komşunun 6'sında düşüş (DD) %25'i, 3'ünde %30'u aşıyor; yani "DD ≤ %25" sınırı temelde kıl payı tutuyor.
- **Cevap 2 (başlangıç): geç başlayınca da artıda, ama çok daha küçük.** 2022 veya 2023'ten başlayınca eski 16'da +103R / +109R (net +%97 / +%111), yeni 20'de +45R / +48R (net +%28 / +%32). 2023 başlangıcında iki listede de **al-tutun altında** (al-tut +%197 / +%186), ama düşüş al-tutun dörtte biri (%24 / %23 yerine %76 / %90). Geç başlangıçta kârın yarıdan fazlası tek bir işlemden geliyor (SOL 2023-10 veya ALGO 2024-11); en büyük 5 işlem dışında ortalama eksi.
- **Hangi işlemlerin alındığı başlangıca bağlı değil:** 3 yer sınırına rağmen geç başlayan koşular, tam koşunun aynı dönemdeki işlemlerinin birebir aynısını aldı (tek fark: eski 16'da 2021'in ilk iki gününde 3 ek işlem, +2.3R).
- **2026-11-10 "hazır mıyız" toplantısı için anlamı:**
  - İyi haber: kural rastgele bir ayar kazası değil. Ayarlar ±%25 oynayınca da para kazandırıyor; sonuç birkaç sivri ayara bağlı değil.
  - Dikkat: kâr az sayıda büyük trendden geliyor ve 2022 sonrası beklenti küçük (eski 16'da işlem başına ≈ +0.7R, yeni 20'de ≈ +0.3R; 2025'te yeni 20 -19.8R). Gerçek parada ilk aylar büyük olasılıkla küçük kayıplar ve beklemeyle geçer; kazanç, yakalanırsa birkaç büyük trendden gelir.
  - Bu test gerçek para için tek başına "hazırız" demek için yeterli değil; karar `docs/decisions.md`'deki demo şartlarına (komisyon + funding sonrası artı, DD sınırı, dolum fiyatı, ≥ 30 işlem) bağlı kalır. Not: demoda çalışan `PusulaV2` (BTC giriş filtresi, puan +3, 2R'de başabaş), bu test temel `PusulaV2NoBe` için yapıldı.
- **Hiçbir kural değişmedi.** Bazı komşular temelden daha iyi görünüyor (ör. dip stopu 8 mum iki listede de daha iyi). **Bunlardan birini seçmek veri madenciliği olur** (20 koşu içinden en iyisini sonradan seçmek); temel aynen kalıyor. Bu bir teşhis, kabul / red kararı yok.

---

## Ne yapıldı (testten önce sabit)
- **(a) Komşuluk.** Her seferinde tek ayar değişti, diğer her şey `PusulaV2NoBe` ile aynı. Değerler kuyrukta önceden yazılı (≈ ±%25), tarama yok:

| Ayar | Temel | Komşular | Neyi etkiliyor |
|---|---|---|---|
| 4h kırılım kanalı | 20 mum | 15 / 25 | sadece giriş tetiği (`dc_upper`) |
| Dip stopu penceresi | 10 mum | 8 / 12 | stop (son N mumun dibi − 0.1 ATR), dolayısıyla 1R ve pozisyon büyüklüğü, %8 sınırı |
| ATR stop çarpanı | 1.5 | 1.25 / 1.75 | stop (bölge ortası − k × ATR); stop ikisinden geniş olanı |
| Günlük hızlı EMA | 20 | 15 / 25 | puan (EMA hızlı > EMA50), "günlük kapanış EMA üstü" giriş şartı ve EMA çıkışı birlikte; BTC puanı da (BTC-dönüş çıkışı) |
| Momentum | 90 gün | 60 / 120 | puanın getiri parçası (coin ve BTC) |

- Kod: araştırma modülü `research/robustness/pusula_v2nobe_neighbours.py` (sınıflar `PusulaV2NoBeNb*`, `PusulaV2NoBeNbBase` = değişmemiş temel). `strategies/` altına sınıf eklenmedi, mevcut sınıflara dokunulmadı. Freqtrade strateji klasöründeki bütün dosyaları yüklediği için modül, repo dışında tek başına bir klasöre bağlanarak (`FT_STRATEGY_DIR`) çalıştırıldı.
- **(b) Başlangıç tarihi.** Aynı temel, başlangıç 2021-01-01, 2022-01-01, 2023-01-01; bitiş aynı. Isınma aynı (400 mum; günlük veri her durumda 2020-01'den başlıyor, yani günlük EMA'lar aynı).
- Ayarlar: 4h mum, 1h detay, en fazla 3 işlem, %1 risk, maliyet (komisyon + kayma) ve funding dahil, sadece long. Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades`.
- **Bitiş notu (yeni 20):** Bu oturumda veri yeniden indirildi ve artık Ekim 2026'yı da içeriyor. Önceki turlarda yeni 20'nin verisi 2026-09-30'da bitiyordu, eski 16'nınki 2026-10-01 00:00 mumunu içeriyordu. Temeli birebir tutturmak için yeni 20 koşularında bitiş 2026-09-30 23:00 UTC (`--timerange 20200101-1790809200`) kullanıldı. 20261001 ile fark sadece dönem sonunda zorla kapanan 3 işlemde (VET, MANA, ICP): temel 117.78R, net +%134.3 (aşağıdaki tablo: 117.72R, +%134.2). Komşuların hepsinde fark ≤ 0.6R.
- Temel birebir aynı: eski 16 **230 işlem / 311.26R**, yeni 20 **193 işlem / 117.72R**.
- Not: dönem kasa aralığını (2026-04 → 2026-09) da içeriyor; önceki kuyruk turları gibi. Bu sadece teşhis, kasa testi değil.

## (a) Komşuluk sonuçları (2020-03 / 2020-04 → 2026-09)
"En büyük payı" = en büyük tek işlemin toplam R içindeki payı. "En büyük 5 hariç" = en büyük 5 işlem çıkarılınca kalanların ortalama R'si. "Şart" = ortalama R temelin en az yarısı **ve** DD ≤ %30.

### Eski 16
| Sürüm | İşlem | Ortalama R | Toplam R | Net | Max DD | En büyük işlem (payı) | En büyük 5 hariç | Şart |
|---|---|---|---|---|---|---|---|---|
| **temel** | 230 | **+1.353** | **311.26** | **+%827.3** | **%23.75** | ETC 2021-03 +94.1 (%30) | +0.276 | — |
| kanal 15 | 256 | +1.188 | 304.22 | +%730.5 | %24.67 | ETC +94.1 (%31) | +0.220 | evet |
| kanal 25 | 226 | +1.261 | 285.05 | +%692.4 | %23.14 | ETC +94.1 (%33) | +0.163 | evet |
| dip 8 | 246 | +1.586 | 390.12 | +%1210.0 | %23.82 | ETC +94.1 (%24) | +0.300 | evet |
| dip 12 | 224 | +1.311 | 293.69 | +%691.8 | %24.96 | ETC +94.1 (%32) | +0.212 | evet |
| ATR 1.25 | 230 | +1.353 | 311.26 | +%827.3 | %23.75 | ETC +94.1 (%30) | +0.276 | evet |
| ATR 1.75 | 230 | +1.353 | 311.27 | +%827.3 | %23.74 | ETC +94.1 (%30) | +0.276 | evet |
| EMA 15 | 276 | **+0.547** | **150.88** | +%235.6 | %24.34 | BNB 2021-01 +44.8 (%30) | +0.130 | **hayır** (ort. < yarı) |
| EMA 25 | 214 | +1.201 | 256.98 | +%574.1 | %26.67 | ETC +85.3 (%33) | +0.288 | evet |
| mom 60 | 241 | +1.308 | 315.23 | +%1097.4 | %23.20 | SOL 2023-10 +58.6 (%19) | +0.503 | evet |
| mom 120 | 242 | +1.508 | 364.83 | +%1357.6 | %23.27 | ETC +94.1 (%26) | +0.394 | evet |

- Şartı geçen komşu: **9 / 10**. Toplam R aralığı 151 – 390R; 10 komşudan 8'i temelin ±%25'i içinde (EMA 15 -%52, dip 8 +%25).

### Yeni 20
| Sürüm | İşlem | Ortalama R | Toplam R | Net | Max DD | En büyük işlem (payı) | En büyük 5 hariç | Şart |
|---|---|---|---|---|---|---|---|---|
| **temel** | 193 | **+0.610** | **117.72** | **+%134.2** | **%22.61** | ALGO 2024-11 +34.5 (%29) | -0.076 | — |
| kanal 15 | 214 | +0.662 | 141.59 | +%159.7 | **%36.50** | EGLD 2021-01 +36.6 (%26) | -0.060 | **hayır** (DD) |
| kanal 25 | 187 | +0.562 | 105.08 | +%108.3 | %24.66 | ALGO +34.5 (%33) | -0.150 | evet |
| dip 8 | 222 | +0.629 | 139.55 | +%178.2 | %28.71 | FIL 2021-03 +34.9 (%25) | -0.034 | evet |
| dip 12 | 166 | **+0.335** | **55.57** | +%40.3 | %27.26 | ALGO +31.7 (%57) | -0.216 | evet (sınırda) |
| ATR 1.25 | 193 | +0.610 | 117.71 | +%134.2 | %22.61 | ALGO +34.5 (%29) | -0.076 | evet |
| ATR 1.75 | 194 | +0.597 | 115.75 | +%130.8 | %22.61 | ALGO +34.5 (%30) | -0.086 | evet |
| EMA 15 | 215 | +0.513 | 110.19 | +%116.7 | %22.76 | ALGO +41.8 (%38) | -0.162 | evet |
| EMA 25 | 180 | +0.632 | 113.73 | +%126.1 | %25.35 | ALGO +34.5 (%30) | -0.083 | evet |
| mom 60 | 205 | +0.476 | 97.59 | +%104.9 | **%31.28** | FIL +33.0 (%34) | -0.036 | **hayır** (DD) |
| mom 120 | 187 | +0.371 | 69.31 | +%61.9 | **%31.99** | FIL +33.0 (%48) | -0.199 | **hayır** (DD) |

- Şartı geçen komşu: **7 / 10** (üç başarısızlığın üçü de DD > %30; ortalama R'si yarının altına düşen yok). Toplam R aralığı 56 – 142R; 10 komşudan 6'sı temelin ±%25'i içinde.
- DD: 10 komşudan 6'sı %25'i aşıyor (kanal 15, dip 8, dip 12, EMA 25, mom 60, mom 120; %25.35 – %36.50). Temelin %22.61'i komşuların alt ucunda.

### En büyük 5 işlem komşular arasında ne kadar ortak
- Eski 16: temelin en büyük 5'i (ETC 2021-03, SOL 2023-10, BNB 2021-01, BTC 2023-10, BTC 2024-01). Komşularla ortak sayısı: kanal 15/25, ATR 1.25/1.75: 5/5; dip 8/12, mom 60/120: 4/5; EMA 15: 3/5; EMA 25: 2/5. ETC 2021-03 ve BNB 2021-01 11 koşunun 11'inde, SOL 2023-10 ve BTC 2023-10 9'unda en büyük 5 içinde.
- Yeni 20: temelin en büyük 5'i (ALGO 2024-11, FIL 2021-03, UNI 2024-02, THETA 2020-12, VET 2020-06). Ortak: ATR 1.25/1.75: 5/5; kanal 15/25, dip 8, EMA 15/25: 4/5; dip 12, mom 60/120: 3/5. FIL 2021-03 ve UNI 2024-02 11 koşunun 10'unda, ALGO 2024-11 ve THETA 2020-12 9'unda.
- Yani hangi ayar seçilirse seçilsin aynı birkaç büyük trend yakalanıyor; sonucun farkını büyük ölçüde bu trendlerin ne kadar uzun tutulduğu (EMA 15 daha erken çıkıyor: ETC 2021-03 +94.1 → +20.3R) ve küçük işlemler belirliyor.

### Ayar ayar okuma
- **ATR çarpanı pratikte etkisiz.** Stop "ATR stopu ile dip stopundan geniş olanı"; temel işlemlerinde dip stopu bölge ortasından ortanca 2.8 / 2.6 ATR uzakta, 1.5 ATR'den yakın olan işlem 0 / 1, 1.75'ten yakın olan 2 / 12. Bu yüzden 1.25 ve 1.5 birebir aynı sonucu, 1.75 neredeyse aynısını veriyor. Stopu belirleyen dip penceresi.
- **Dip penceresi:** 8 mum iki listede de daha iyi, 12 mum iki listede de kötü (yeni 20'de kâr yarıya iniyor). Pencere uzayınca stop uzaklaşıyor; muhtemelen %8 sınırını aşan sinyal artıyor (12 mumda yeni 20'de 193 → 166 işlem; ayrıca ölçülmedi) ve büyük trendlerin bir kısmı kaçıyor (FIL 2021-03, THETA 2020-12 en büyük 5'ten çıkıyor).
- **Günlük hızlı EMA:** 15 eski 16'da kârı yarıya indiriyor (çıkış daha erken: büyük trendler kısa kesiliyor), yeni 20'de hafif kötü. 25 eski 16'da -%17, yeni 20'de neredeyse aynı ama DD %25.35.
- **Momentum:** eski 16'da iki yönde de iyi ya da aynı; yeni 20'de iki yönde de kötü ve DD %31-32. Liste arasında ters yön: ayarın "doğru" değeri yok, gürültü.
- **Kanal:** iki yönde de küçük kayıp; tek istisna yeni 20'de 15 mum (ortalama ve toplam daha iyi ama DD %36.5).
- İki listede de her ölçüde (ortalama, toplam, net, DD) temelden iyi olan komşu yok. En yakını dip 8: iki listede ortalama, toplam ve net daha iyi, ama yeni 20'de DD %22.6 → %28.7. Kural değişmez (aşağıya bakın).

## (b) Başlangıç tarihi (bitiş aynı, temel aynı)
| Liste | Başlangıç | İşlem | Ortalama R | Toplam R | Net | Max DD | En büyük işlem (payı) | En büyük 5 hariç | Al-tut (DD) |
|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | 2020-03 (tam) | 230 | +1.353 | 311.26 | +%827.3 | %23.75 | ETC 2021-03 +94.1 (%30) | +0.276 | +%931.5 (%89) |
| Eski 16 | 2021-01-01 | 187 | +1.439 | 269.12 | +%532.8 | %23.75 | ETC 2021-03 +94.1 (%35) | +0.110 | +%842.3 (%89) |
| Eski 16 | 2022-01-01 | 152 | +0.674 | 102.52 | +%97.3 | %23.72 | SOL 2023-10 +58.6 (%57) | -0.127 | **-%6.9** (%81) |
| Eski 16 | 2023-01-01 | 145 | +0.753 | 109.15 | +%110.8 | %23.71 | SOL 2023-10 +58.6 (%54) | -0.086 | **+%196.8** (%76) |
| Yeni 20 | 2020-04 (tam) | 193 | +0.610 | 117.72 | +%134.2 | %22.61 | ALGO 2024-11 +34.5 (%29) | -0.076 | +%194.7 (%98) |
| Yeni 20 | 2021-01-01 | 164 | +0.526 | 86.19 | +%79.1 | %22.61 | ALGO +34.5 (%40) | -0.174 | +%76.8 (%98) |
| Yeni 20 | 2022-01-01 | 137 | +0.325 | 44.52 | +%28.0 | %22.61 | ALGO +34.5 (%77) | -0.330 | **-%36.2** (%95) |
| Yeni 20 | 2023-01-01 | 131 | +0.363 | 47.51 | +%31.8 | %22.61 | ALGO +34.5 (%73) | -0.322 | **+%185.6** (%90) |

- Al-tut: eşit ağırlık, aynı dönem, aynı coinler; parantezde coin başına ortalama en büyük düşüş.
- **Altı koşunun hepsi artıda.** 2021 başlangıcında iki listede de al-tuta yakın ya da üstünde (yeni 20: +%79 / +%77); 2022 başlangıcında (2022 ayı piyasası dahil) iki listede de al-tutun çok üstünde; 2023 başlangıcında iki listede de al-tutun altında (+%111 / +%197, +%32 / +%186), ama düşüş %24 / %23 (al-tutta %76 / %90).
- Max DD değişmiyor: temelin en büyük düşüşü zaten 2024-26'da (eski 16: 2024-03 → 2025-01; yeni 20: 2024-12 → 2026-09).
- Yıllara göre R (başlangıçtan bağımsız, tam koşuyla aynı): eski 16 2021 +164.3 (2021 başlangıcında +166.6), 2022 -6.6, 2023 +86.7, 2024 +10.0, 2025 +15.5, 2026 -3.1; yeni 20 2021 +41.7, 2022 -3.0, 2023 -1.9, 2024 +64.9, 2025 -19.8, 2026 +4.3.
- **3 yer sınırında işlem seçimi başlangıca bağlı değil.** Geç başlayan her koşunun işlemleri, tam koşunun aynı tarihten sonraki işlemleriyle (coin + açılış saati) karşılaştırıldı:
  - Eski 16, 2021: tam koşunun 184 işleminin hepsi ortak (R aynı); başlangıç koşusunda 3 ek işlem, hepsi 2021-01-02 / 2021-01-03'te (tam koşuda o anda yerler 2020'den kalan işlemlerle doluydu), +2.28R. Sonrası birebir aynı.
  - Eski 16 2022 / 2023 ve yeni 20'nin üç başlangıcı: işlemler birebir aynı (152 / 145; 164 / 137 / 131 işlem, 0 fark).
  - Yani başlangıç tarihi sadece hangi yılların sayıldığını değiştiriyor; "yer dolu olduğu için başka işlem alındı" etkisi ihmal edilebilir.
- **Yoğunlaşma geç başlangıçta artıyor:** 2022 / 2023 başlangıcında kârın %54-57'si (eski 16, SOL 2023-10) ve %73-77'si (yeni 20, ALGO 2024-11) tek işlem; en büyük 5 hariç ortalama iki listede eksi. 2022 sonrası bu kural, çoğu küçük kayıp olan işlemlerle birkaç büyük trendi bekleyen bir kural.

## Hüküm (teşhis; kabul / red yok)
- **Düzlük mü, sivri tepe mi?** Düzlük. 20 komşu koşunun hepsi artıda, en kötüsü +0.34R ortalama; şart (ortalama ≥ temelin yarısı ve DD ≤ %30) 9 / 10 ve 7 / 10 komşuda tuttu. Temel komşuların ortasında, tepesinde değil: bazı komşular daha iyi, bazıları kötü. Sivri bir nokta olsaydı komşuların çoğu çökerdi; çökmüyor.
- **Tek bir komşu sonucu eksiye çeviriyor mu?** Hayır. Hiçbir komşu iki listenin hiçbirinde eksiye düşmedi. En büyük düşüşler: eski 16'da EMA 15 (311 → 151R), yeni 20'de dip 12 (118 → 56R).
- **Zayıf yanları:** (1) büyüklük ayara yaklaşık 2 kat duyarlı; (2) yeni 20'de DD %25 sınırı 10 komşunun 6'sında aşılıyor, temelin %22.6'sı şanslı uçta; (3) kâr aynı birkaç büyük trende bağlı (ETC 2021-03, BNB 2021-01, SOL 2023-10; FIL 2021-03, UNI 2024-02, ALGO 2024-11), en büyük 5 hariç yeni 20'de ortalama eksi.
- **Geç başlangıç artıda kalıyor mu?** Evet, altı koşunun hepsi artıda; ama 2022 ve sonrası ortalama +0.3 – +0.75R, 2023 başlangıcında iki listede de al-tutun altında (düşüş çok daha küçük).
- **Kural değişmez.** Dip 8 iki listede de daha iyi, mom 120 eski 16'da, kanal 15 yeni 20'de daha iyi görünüyor. Bunlardan birini seçmek, 20 koşunun sonucuna bakıp en iyisini almak olur: **veri madenciliği**. Aynı tarama başka bir dönemde başka bir "en iyi" verir. Temel `PusulaV2NoBe` aynen kalıyor; bu turdan yeni kural maddesi de çıkarılmadı.

## Dosyalar
- Kod: `research/robustness/pusula_v2nobe_neighbours.py`.
- Ham sonuçlar (repoda değil, `user_data/backtest_results/`): komşular eski 16 `backtest-result-2026-11-09_07-05-21`, yeni 20 `..._07-17-40` (bitiş 2026-09-30 23:00, tablodaki) ve `..._07-01-46` (bitiş 2026-10-01); başlangıç koşuları eski 16 `..._07-06-21` (2021), `..._07-07-41` (2022), `..._07-08-52` (2023); yeni 20 `..._07-18-29`, `..._07-19-03`, `..._07-19-33` (bitiş 2026-09-30 23:00; 20261001 bitişli eşleri `..._07-07-00`, `..._07-08-13`, `..._07-09-21`, fark ≤ 0.06R). `--backtest-filename` bu sürümde dikkate alınmıyor, adlar Freqtrade'in varsayılanı.
