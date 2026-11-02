# Kuyruk 24 + 25 — stop mesafesi teşhisi ve yarım çıkış — 2026-11-02 (temel: PusulaV2NoBe)

## GUO'ya not
- **Kuyruk 25 sorusu:** trend bozulunca (günlük kapanış EMA20 altı) pozisyonun hepsini değil **yarısını** kapatsak, kalan yarıyı daha yavaş çizgiye (EMA50) kadar taşısak daha iyi olur muyduk?
- **Cevap: hayır, red.** İşlem başına R iki listede de arttı, ama hesabın getirisi eski 16'da düştü.
  - Eski 16: ortalama +1.35R → +2.31R, toplam 311.3R → 364.8R, ama net **+%827 → +%733**, DD %23.7 → %19.9.
  - Yeni 20: ortalama +0.61R → +0.91R, toplam 117.7R → 151.2R, net +%134 → +%140, DD %22.6 → %22.5. Dört şart da tuttu, ama kazancın tamamı tek işlemden (THETA 2020-12: +24.1R → +92.2R). Bu işlem hariç yeni sürüm daha kötü.
- **Neden R arttı ama para azaldı:**
  - Kalan yarı uzun süre açık kalıyor (ortalama 18 gün, en uzun 130 gün). Bu sırada kârı hesaba geçmiyor. Yeni işlemler kapanmış bakiyeden boyutlanıyor, yani daha küçük açılıyor.
  - Yarım kalan işlem yeri de tutuyor: eski 16'da temelin 79 girişi kaçtı (+101.9R).
  - Bakiyenin en büyük olduğu 2024'te sonuç kötüleşti: +10.0R → -5.7R.
- **Kuyruk 24 (sadece teşhis, kural değişmedi):** stop mesafesi geniş olan işlemler iki listede aynı yönde davranmıyor.
  - Eski 16'da en iyi grup %6-8 (ortalama +1.82R), ama bu iki işlemden geliyor (ETC 2021-03, BNB 2021-01).
  - Yeni 20'de %6-8 en zayıf gruplardan (+0.41R).
  - Stop %8'i geçtiği için hiç sinyal olmayan 4h mum sayısı izin verilen sinyallerden bile fazla: 1907 / 2219 mum (izin verilen sinyal 1621 / 855).
  - Bu mumlardan sonraki 30 gündeki en yüksek fiyat, stopa göre normal sinyallerden **daha az R** ediyor (ortanca 2.0 / 2.2R, normal sinyallerde 3.0 / 3.2R).
  - **%8 sınırı PROJECT_BRIEF kuralı. Bu tur onu değiştirmeyi önermiyor; değiştirmek proje sahibinin kararı.**
- Temel `PusulaV2NoBe` değişmedi. Kuyruğa iki yeni fikir eklendi (madde 26, 27).

---

# Bölüm A — Kuyruk 24: stop mesafesine göre teşhis (kural değişikliği yok)

## Ne yapıldı
- Temelin (`PusulaV2NoBe`) bu turdaki backtestinden (230 / 193 işlem; önceki turlarla birebir aynı) her işlemin stop mesafesi hesaplandı: (gerçek giriş fiyatı − stop) / gerçek giriş fiyatı.
- Gruplar testten önce sabitti: **< %4, %4-6, %6-8**. Hiçbir işlem %8'in üstünde değil. Plan bölge ortasına göre %8'le sınırlı, gerçek dolum ya aynı ya daha aşağıda. Yeni 20'deki bir işlemde dolum stopun altındaydı (fiyat boşlukla aşağı açıldı); o işlem "< %4" grubunda.

## Gruplar (R maliyet + funding dahil)
| Liste | Stop mesafesi | İşlem | Ortalama R | Toplam R | En iyi işlem hariç ort. | Kazanma | Stopla biten | En iyi işlem |
|---|---|---|---|---|---|---|---|---|
| Eski 16 | < %4 | 56 | +0.61 | +33.9 | +0.20 | %25.0 | %46 | BTC 2023-10 +22.6 |
| Eski 16 | %4-6 | 76 | +1.30 | +98.8 | +0.54 | %35.5 | %39 | SOL 2023-10 +58.6 |
| Eski 16 | %6-8 | 98 | **+1.82** | +178.6 | +0.87 | %33.7 | %41 | ETC 2021-03 +94.1 |
| Yeni 20 | < %4 | 8 | +2.78 | +22.2 | **-0.55** | %37.5 | %63 | UNI 2024-02 +26.1 |
| Yeni 20 | %4-6 | 62 | +0.72 | +44.7 | +0.17 | %24.2 | %55 | ALGO 2024-11 +34.5 |
| Yeni 20 | %6-8 | 123 | **+0.41** | +50.8 | +0.15 | %22.0 | %53 | FIL 2021-03 +33.0 |

- **Eski 16:** stop genişledikçe sonuç iyileşiyor. Ama %6-8 grubunun kârı neredeyse tamamen %7-8 aralığından geliyor (49 işlem +179.1R, içinde ETC 2021-03 +94.1R ve BNB 2021-01 +53.0R). %6-7 aralığındaki 49 işlem toplam -0.5R. (Bu alt aralık sabit gruplardan değil, sadece bilgi.)
- **Yeni 20:** sıra tersine yakın. %6-8 grubu en kalabalık (işlemlerin %64'ü) ve ortalaması en düşük. %7-8 aralığı 65 işlem +44.7R (ort. +0.69R). "< %4" grubu tek işlem (UNI) hariç eksi.
- **Sonuç:** iki listede tutarlı bir sıra yok. "Sınıra yakın geniş stoplu kırılımlar daha iyi" fikri sadece eski 16'da ve orada da iki işleme dayanıyor.

### Yıllara göre (R; parantezde işlem)
| Yıl | 16: < %4 | 16: %4-6 | 16: %6-8 | 20: < %4 | 20: %4-6 | 20: %6-8 |
|---|---|---|---|---|---|---|
| 2020 | -4.3 (4) | +20.1 (13) | +28.7 (29) | -0.4 (2) | +5.4 (6) | +26.5 (21) |
| 2021 | -1.8 (2) | +10.9 (9) | +155.3 (21) | 0 (0) | -3.1 (3) | +44.8 (24) |
| 2022 | -2.2 (2) | -1.4 (2) | -3.1 (3) | 0 (0) | -2.1 (2) | -0.9 (4) |
| 2023 | +27.9 (12) | +59.3 (11) | -0.5 (15) | -0.2 (2) | -0.5 (14) | -1.2 (23) |
| 2024 | +12.3 (16) | +4.6 (25) | -7.0 (16) | +23.9 (3) | +45.5 (19) | -4.6 (14) |
| 2025 | +6.0 (11) | +6.0 (11) | +3.5 (9) | -1.1 (1) | -2.5 (11) | -16.3 (29) |
| 2026 | -4.1 (9) | -0.8 (5) | +1.8 (5) | 0 (0) | +1.9 (7) | +2.4 (8) |

- Geniş stoplu grubun kazancı 2020-2021 boğasından. 2023'ten beri iki listede de %6-8 grubu eksi ya da sıfıra yakın; 2023-2026 kârı daha dar stoplu işlemlerden geliyor.

## Stop > %8 olduğu için sinyal olmayan 4h mumlar
Tanım: diğer bütün long şartları doğru (günlük puan ≥ +1, günlük kapanış EMA20 üstü, 20 mumluk tepenin üstünde ilk 4h kapanış), sadece `long_plan_ok` yanlış, çünkü bölge ortasına göre stop %8'den uzak. Aynı dönem (2020-03-07 → 2026-10-01). Mumda çıkış sinyali varsa (BTC-dönüş) Freqtrade zaten girmezdi; bu mumlar (135 / 223) ayrı sayıldı ve aşağıdaki tabloya alınmadı.

| Liste | Bu mumlar | Ayrı coin-gün / coin-hafta | Stop ortancası | Karşılaştırma: izin verilen sinyal mumları |
|---|---|---|---|---|
| Eski 16 | **1907** | 1626 / 972 | %12.3 (aralık %8.0-80.8) | 1621 |
| Yeni 20 | **2219** | 1931 / 1115 | %13.1 (aralık %8.0-70.7) | 855 |

- Sınırın hemen üstü (%8-9) 271 / 274 mum. Çoğunluk çok daha geniş: %15'in üstü 623 / 837 mum.
- Aynı trendde ardışık mumlar çok, bu yüzden sayı "kaçan fırsat" sayısı değil.

### Yıllara göre
| Yıl | 16: mum | 16: stop ortancası | 16: 30 gün en yüksek, R ortancası | 16: ≥ 3R | 20: mum | 20: stop ortancası | 20: 30 gün en yüksek, R ortancası | 20: ≥ 3R |
|---|---|---|---|---|---|---|---|---|
| 2020 | 319 | %11.8 | 2.57 | 144 | 165 | %12.2 | 3.36 | 90 |
| 2021 | 731 | %14.3 | 2.77 | 344 | 789 | %15.7 | 3.08 | 402 |
| 2022 | 22 | %11.4 | 0.76 | 0 | 35 | %11.5 | 0.64 | 1 |
| 2023 | 225 | %11.4 | 1.37 | 43 | 355 | %11.3 | 1.73 | 93 |
| 2024 | 332 | %12.4 | 2.03 | 130 | 446 | %13.6 | 2.46 | 191 |
| 2025 | 207 | %10.7 | 0.94 | 20 | 252 | %10.7 | 1.01 | 40 |
| 2026 | 71 | %11.4 | 1.24 | 7 | 177 | %12.1 | 1.89 | 58 |

### Sonraki 30 gündeki en yüksek fiyat, stopa göre kaç R (sadece bilgi, işlem değil)
R = (sonraki 180 adet 4h mumun en yüksek fiyatı − bölge ortası) / (bölge ortası − stop). Bu bir **üst sınır**: stopa önce değip değmediğine ve gerçek bir çıkış kuralına bakılmıyor.

| Liste | Grup | Mum | R ortanca / ortalama | ≥ 3R payı | En yüksek fiyat, % ortanca |
|---|---|---|---|---|---|
| Eski 16 | stop > %8 | 1907 | 2.03 / 4.19 | %36.1 | +%25.1 |
| Eski 16 | izin verilen sinyaller (stop ≤ %8) | 1621 | 2.95 / 5.57 | %49.5 | +%13.8 |
| Yeni 20 | stop > %8 | 2219 | 2.18 / 4.09 | %39.4 | +%29.7 |
| Yeni 20 | izin verilen sinyaller (stop ≤ %8) | 855 | 3.19 / 6.69 | %51.3 | +%19.9 |

- Stop > %8 olan kırılımlarda fiyat yüzde olarak daha çok gidiyor (en oynak anlar), ama stop da çok uzak olduğu için R olarak **daha az** ediyor. Stop genişledikçe R ortancası düşüyor: %8-9'da 2.24 / 2.69, %15 üstünde 1.82 / 1.74.
- En büyükleri: DOGE 2021-01-01 (stop %10.1, +166R), DOGE 2021-04-11 (%8.1), ETC 2021-04-10, BNB 2021-02-01, XLM 2024-11-11 (16'da); SAND 2021-10-26 (%8.4, +104R), MANA 2021-10, HBAR 2024-11-11, EGLD 2021-01, ALGO 2024-11-08 (%8.5) (20'de). Çoğu 2021 boğasında.
- Coin dağılımı geniş (16'da en çok SOL 175, LINK 169; 20'de NEAR 159, VET 154). Tek bir coine özgü değil.

## Bölüm A sonucu
- Sınırın yanındaki grup (%6-8) eski 16'da iyi, yeni 20'de zayıf. İki listede tutarlı bir bulgu yok.
- Sınır üstü kırılımlar sayıca çok, ama R ölçüsüyle normal sinyallerden daha zayıf görünüyor. Bunun en uç örnekleri 2021 boğasından.
- **%8 sınırı (PROJECT_BRIEF 7.2) bu turda değişmedi ve değiştirilmesi önerilmiyor.** Bu sadece teşhis. Sınırı değiştirmek (ya da geniş stopta yarım pozisyon gibi bir fikir) **proje sahibinin kararıdır**; istenirse önce ona sorulup ayrı turda yazılır.

---

# Bölüm B — Kuyruk 25: yarım çıkış (EMA20'de yarısı, EMA50'de kalanı)

## Kural (testten önce yazıldı)
`PusulaV2NoBeHalfEma50(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- **EMA20'de yarısı:** son kapanmış günlük kapanış EMA20'nin altına inince pozisyonun **yarısı** satılır. Bu, temelin tam çıkış yaptığı an ve kural. İşlem başına bir kez.
- **Kalan yarı** şu üç şeyden biriyle kapanır:
  - son kapanmış günlük kapanış **EMA50** altında (`ema50`);
  - BTC-dönüş çıkışı, yani BTC'nin son kapanmış günlük puanı ≤ -1 (`btc_turn`);
  - sabit stop.
- Aynı kalanlar: girişler, stop seviyesi (hiç kımıldamaz), %1 risk, en fazla 3 işlem. Yarım kalan işlem açık işlem sayılır, yeri tutar. Oranlar sabit (%50, EMA50), tarama yok.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25.

## Nasıl kodlandı
- **Yarım satış Freqtrade'in kısmi çıkışıyla:** `adjust_trade_position` negatif tutar döndürüyor (mevcut tutarın %50'si, etiket `ema20_half`). `position_adjustment_enable` ortak modülde zaten açık.
  - Karar, analiz tablosunun son **kapanmış** 4h satırından veriliyor. Bu, temelin çıkış sinyalinin kullandığı satırın aynısı.
  - Bir kısmi çıkıştan sonra bir daha satmıyor.
- **EMA50 ve BTC-dönüş normal çıkış sinyali** (`populate_exit_trend`). Çıkış sinyali kalan miktarın tamamını satıyor. Yarım satış ile EMA50 / BTC çıkışı aynı muma denk gelirse önce yarım satış, sonra kalanı aynı fiyattan satılıyor; sonuç tam çıkışla aynı.
- **Girişler değişmiyor:** giriş "puan ≥ +1 ve günlük kapanış EMA20 üstü" istiyor. Bu iki şart doğruyken kapanış EMA50 altında olamaz. Yani EMA50 çıkışı hiçbir girişi engellemiyor, BTC-dönüş aynı mumları engelliyor. Giriş mumları temelle aynı. Değişen tek şey: yarım kalan işlem coini ve yeri meşgul tutuyor.
- **R tüm pozisyon için:**
  - Freqtrade işlemin `profit_abs` değerine kısmi çıkışın kârını da ekliyor. `scripts/make_report.py` R'yi kâr / (tam giriş miktarı × |giriş − stop|) olarak hesaplıyor. Bu, iki yarının ağırlıklı toplamı demek (komisyon ve funding dahil).
  - Kontrol: her işlem için iki yarı emirlerden ayrı ayrı hesaplandı (yarı 1 + yarı 2 + funding = R). En büyük hata 1e-10. `make_report.py`'de değişiklik gerekmedi.
  - Not: alt raporlardaki "Stop" oranı, son parçası stopla kapanan işlemleri sayıyor. Buna yarısı EMA20'de satılıp kalanı stopla kapanan 25 / 19 işlem de dahil.
- **Önemli bulgu: Freqtrade kısmi çıkıştan sonra stopu kaydırıyordu.** İlk çalıştırmada görüldü, düzeltildi.
  - Freqtrade kısmi çıkıştan sonra işlemin son stop **oranını** ortalama giriş fiyatına yeniden uyguluyor. Stop sadece yukarı gidebiliyor.
  - Oran yarım satış fiyatına göre ayarlandığı için, yarı girişin altında satıldıysa stop yukarı kayıyordu (BTC 2020-05: plan 8601, olan 8804). Bu, "stop kımıldamaz" kuralına aykırı.
  - Düzeltme: yeni sınıfın `custom_stoploss`'u, kısmi çıkış dolumunda oranı max(dolum fiyatı, giriş fiyatı) üzerinden veriyor. Backtestte yeniden hesap bu çağrıdan sonra geliyor. Canlıda sıra ters, orada normal oran kullanılıyor.
  - Kontrol: yeni sürümde stopla biten 95 / 112 işlemin hepsinde son fiyat planlanan stop. Fark en fazla %0.084, temeldeki fiyat yuvarlamasıyla aynı.
  - Yan etki: Freqtrade bu stopu "trailing" diye işaretliyor, çıkış adı `trailing_stop_loss` oluyor. Aynı sabit stop.
  - Düzeltilmemiş ilk sürümün sonucu (farklı bir kural, sadece bilgi):
    - eski 16'da 162 işlem, +2.19R, 353.9R, net +%673.3, DD %19.6 (yine red);
    - yeni 20'de 168 işlem, +0.94R, 158.1R, net +%153.3, DD %22.5.
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_half_ema50_sells_half_at_ema20_once_and_rest_below_ema50`. Kontrol edilenler:
  - çıkış sinyali sadece EMA50 ve BTC-dönüşte;
  - EMA20'de yarım satış, işlem başına bir kez;
  - açık emir ya da short varken satış yok;
  - kısmi çıkıştan sonra stop, yarı giriş fiyatının altında, üstünde ya da aynı seviyede satılsa da plan seviyesinde kalıyor (backtest ve canlı çağrı sırası).
  227 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT / R) | Ort. süre (gün; kazanan / kaybeden) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 / -43.4 | 11.4 (24.9 / 4.9) | +%931.5 |
| Eski 16 | yarım çıkış | 158 | **+2.309** | **364.75** | +2.488 / 393.1 | **+%732.9** | %19.85 | 2.21 | %26.6 | -12490 / -50.2 | 19.5 (55.3 / 6.5) | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 / -25.0 | 8.1 (22.0 / 3.8) | +%194.7 |
| Yeni 20 | yarım çıkış | 166 | **+0.911** | **151.18** | +0.937 / 155.5 | **+%139.9** | %22.49 | 1.53 | %21.1 | -5928 / -45.4 | 11.5 (37.3 / 4.6) | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R; +%827.3 / +%134.2).
- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem. İki sürüm de al-tutun altında, ama DD %20-24'e karşı al-tut %89 / %98.

**Karar: red.**
- Eski 16: ortalama R (+1.353 → +2.309), toplam R (311.26 → 364.75) ve DD (%19.85) tuttu. **Net getiri tutmadı** (+%827.3 → +%732.9).
- Yeni 20: dört şart da tuttu (+0.610 → +0.911R; 117.72 → 151.18R; +%134.2 → +%139.9; DD %22.49). Ama tek işleme bağlı (aşağıda "Yoğunlaşma").

## İki yarı ayrı ayrı (yarım satış olan işlemler)
| Liste | Yarım satış olan işlem | 1. yarı R (EMA20'de satılan) | 2. yarı R (funding hariç) | Bu işlemlerin funding'i (R) | Toplam R | 2. yarının 1. yarıdan iyi olduğu işlem |
|---|---|---|---|---|---|---|
| Eski 16 | 76 | +105.6 (ort. +1.39) | **+274.3** (ort. +3.61) | -45.0 | +334.9 | 22 / 76 |
| Yeni 20 | 64 | +91.9 (ort. +1.44) | **+186.0** (ort. +2.91) | -42.6 | +235.3 | 12 / 64 |

- Kalan yarı çoğu işlemde EMA20'de satılan yarıdan **daha kötü** kapanıyor (54 / 76 ve 52 / 64). Ama birkaç büyük trendde çok daha iyi:
  - Eski 16: BNB 2021-01 (2. yarı +81.5R), BTC 2020-10 (+42.7R), SOL 2023-10 (+26.3R), BTC 2023-10 (+20.1R), ETH 2020-10 (+19.9R).
  - Yeni 20: THETA 2020-12 (2. yarı +100.9R), NEO 2021-02 (+20.9R), ALGO 2024-11 (+15.2R), FIL 2021-03 (+15.1R).
- Kalan yarı nasıl bitti:
  - EMA50 çıkışı: 42 işlem +174.5R / 43 işlem +175.1R.
  - BTC-dönüş: 8 işlem +107.6R / 2 işlem +20.7R.
  - Stop: 25 işlem -13.1R / 19 işlem -9.8R.
- Yarım satışa hiç gelmeyen işlemler (önce stop ya da BTC-dönüş): 82 işlem +29.9R / 102 işlem -84.1R. Bunlar temelle aynı.
- İkisinin de aldığı ve yarım satışı olan 70 / 63 işlemin **hepsinde** yarım satış, temelin tam çıkışıyla aynı saatte ve aynı fiyatta.

## Fark nereden geliyor (toplam R farkının parçaları)
İşlemler coin + açılış zamanıyla eşleştirildi.

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Ortak, değişmeyen işlemler (yarım satış yok, çıkış aynı) | 80 | 0.00 | 99 | 0.00 |
| Ortak, kalan yarı daha uzun tutulan işlemler | 71 | **+121.69** | 65 | **+65.00** |
| — bunlardan daha iyi bitenler | 24 | +140.57 | 12 | +91.33 |
| — bunlardan daha kötü bitenler | 47 | -18.88 | 53 | -26.33 |
| Kaybedilen girişler (temelin aldığı, yeni sürümün alamadığı) | -79 | **-101.92** | -29 | **-41.84** |
| Yeni girişler (temelin alamadığı) | +7 | +33.72 | +2 | +10.30 |
| **Toplam fark** | 230 → 158 | **+53.49** | 193 → 166 | **+33.46** |

(Kaybedilen satırında işaret, toplam R'ye etkisi: temelde +101.92R yapan işlemlerin kaybı -101.92R.)

## Yer etkisi (yarım kalan işlemin tuttuğu yer)
- Eski 16'da 79 giriş kaçtı (+101.9R):
  - 31'i, o coinde yarım kalan işlem açık olduğu için (+33.0R; ör. ETH 2020-12 +9.5R, BTC 2020-12 +6.9R);
  - 48'i 3 yer dolu olduğu için ve hepsinde en az bir yer yarım kalan işlemdeydi (+68.9R; ör. BTC 2024-01 +20.8R, TRX 2021-03 +14.1R, ETH 2024-02 +8.9R). 19'unda üç yer de yarım kalan işlemdeydi.
- Yeni 20'de 29 giriş kaçtı (+41.8R): 8'i coin meşgul (+17.2R; NEO 2021-03 +9.7R, IOTA 2020-07 +7.9R), 21'i yer dolu (+24.6R; VET 2020-06 +14.4R, DASH 2024-11 +9.1R).
- Yeni girişler 7 / 2 (+33.7 / +10.3R; LINK 2020-07 +25.3R, VET 2020-07 +11.5R).
- Net yer etkisi -68.2R / -31.5R. Uzun tutmanın kazancının (+121.7 / +65.0R) yarısından fazlasını yiyor.
- Ortalama açık işlem 1.07 → 1.27 / 0.63 → 0.79; bunun 0.58 / 0.28'i yarım kalan işlem. 3 yerin dolu olduğu günler %24.3 → %32.4 / %12.5 → %16.6.
- Kalan yarının açık kaldığı süre: ortalama 18.2 / 10.4 gün, ortanca 4.2 / 2.2 gün, en uzun 130 / 91 gün. Girişten yarım satışa ortalama 16.7 / 13.5 gün.

## Neden eski 16'da R arttı ama net düştü
- Freqtrade pozisyonu **kapanmış** bakiyeden boyutluyor. Kalan yarı aylarca açık kalınca kazancı bakiyeye geç giriyor. Örnekler: BTC 2020-10 → 2021-04 (192 gün), BNB 2021-01 → 2021-05. Bu sırada açılan işlemler daha küçük bakiyeyle açılıyor.
- Kazancın geldiği yıllar ile bakiyenin büyük olduğu yıllar farklı:
  - 2020: +44.4R → +93.8R, ama o zaman hesap küçük (USDT kâr +4980 → +10919).
  - 2021: +164.3R → +187.1R olmasına rağmen USDT kâr +31965 → +28787 (düştü).
  - 2024: hesap en büyükken +10.0R → -5.7R (USDT +4071 → -5369). 2024-01-01'de bakiye 53.8k → 44.3k USDT.
- Toplam R ve hesap-R toplamı artsa da paranın büyümesi (bileşik etki) daha kötü.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | Eski 16 temel | Eski 16 yarım | Yeni 20 temel | Yeni 20 yarım |
|---|---|---|---|---|
| 2020 | +44.4 (46) | **+93.8** (19) | +31.5 (29) | **+93.8** (20) |
| 2021 | +164.3 (32) | +187.1 (21) | +41.7 (27) | +41.8 (21) |
| 2022 | -6.6 (7) | -7.0 (7) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +89.0 (34) | -1.9 (39) | -8.6 (36) |
| 2024 | +10.0 (57) | **-5.7** (38) | +64.9 (36) | **+42.5** (33) |
| 2025 | +15.5 (31) | +9.6 (23) | -19.8 (41) | -17.6 (35) |
| 2026 | -3.1 (19) | -2.0 (16) | +4.3 (15) | +2.3 (15) |

- İki listede de kazancın çoğu 2020'den. Yeni 20'deki 2020 farkı (+62.3R) neredeyse tamamen THETA 2020-12 işlemi.
- 2024'te iki listede de kötüleşme (-15.7R / -22.4R). Kaybedilen girişler bu yılda yoğun (BTC 2024-01, ETH 2024-02, DASH 2024-11), UNI / ALGO / FIL'in kalan yarıları EMA20'de satılan yarıdan kötü bitti.
- Doğrulama + kasa dönemi (2025-2026): 16'da +12.4 → +7.6R, 20'de -15.5 → -15.3R.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | +0.948 | +0.276 | +0.941 |
| Eski 16 | yarım | BNB 2021-01 +97.8 (ETC 2021-03 +94.1 ikinci) | +1.700 | +0.330 | +1.751 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | yarım | THETA 2020-12 +92.2 | **+0.357** | **-0.272** | **+0.389** |

- Yeni sürümün en büyük 5'i:
  - Eski 16: BNB 2021-01 +97.8, ETC 2021-03 +94.1, SOL 2023-10 +54.1, BTC 2020-10 +38.9, BTC 2023-10 +29.4.
  - Yeni 20: THETA 2020-12 +92.2, ALGO 2024-11 +31.9, FIL 2021-03 +29.0, UNI 2024-02 +22.4, NEO 2021-02 +19.3.
- **Yeni 20'deki kabul, tek bir işleme bağlı.** THETA 2020-12'nin kalan yarısı 2021-04'e kadar taşındı: işlem temelde +24.1R, burada +92.2R. Bu işlem hariç ortalama R +0.434 → +0.357, en büyük 5 hariç -0.076 → -0.272 (daha kötü).
- Eski 16'daki iyileşme (en büyük hariç) daha geniş tabanlı: BNB, BTC 2020-10, ETH 2020-10, TRX 2020-06, ADA 2020-05. Ama hepsi 2020-2021 boğasından.

## İleriye bakma kontrolü
- Yarım satış kararı son kapanmış 4h satırındaki son kapanmış günlük kapanış ile EMA20'den veriliyor. EMA50 ve BTC-dönüş de kapanmış günlük mumlardan (`merge_informative_pair`). Karar anında bilinmeyen bir şey kullanılmıyor.
- **Veri kesme testi:** her listede 300 an (150 rastgele 4h mum, 150 tanesi "günlük kapanış EMA20 altına indi" anı). Her anda her coin için stratejinin kendi `populate_indicators` + giriş + çıkış kodu iki kez çalıştırıldı: tam veriyle ve o anda kesilmiş veriyle. Giriş, çıkış, yarım satış şartı, `long_stop`, `long_plan_ok` karşılaştırıldı.
  - Eski 16: 300 an, 4700 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5729 kontrol, **0 fark**.
- **Zaman kontrolü (backtest işlemlerinden):** ortak işlemlerde yarım satış 70 / 70 ve 63 / 63 kez temelin EMA20 çıkışıyla aynı saatte ve fiyatta. Yani bir mum erken ya da geç değil.
- **Stop kontrolü:** stopla biten 95 / 112 işlemin hepsi planlanan stopta (fark ≤ %0.084, temelde de aynı; fiyat yuvarlaması).

## Uyarılar
- Kalan yarının kazancı birkaç büyük boğa trendinden geliyor (2020-2021). Bunlar bir daha aynı şekilde olmayabilir.
- Canlıda kısmi çıkış ayrı bir emir. Freqtrade'in kısmi çıkıştan sonra stopu yeniden hesaplaması canlıda farklı sırayla oluyor; kod iki sırayı da ele alıyor, ama canlıda hiç denenmedi. Sınıf kabul edilmediği için demoya gitmiyor.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeHalfEma50 --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/half_<liste>`.
- Rapor: `scripts/make_report.py --results <zip> --test yarim_cikis --out results/2026-11-02_pusula_yarim_cikis/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma; kısmi çıkış da bir emir), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor. Önceki turlar da aynı aralığı kullandı; yeni bir kasa kullanımı yok.
