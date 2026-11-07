# Kuyruk 30 — günlük 10 gün dibi çıkışı — 2026-11-07 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** İşlemden "günlük kapanış 20 günlük ortalamanın (EMA20) altına inince" çıkmak yerine "günlük kapanış **önceki 10 günün en düşük seviyesinin** altına inince" çıksak daha iyi olur muyduk? Fikir: ortalama değil gerçek bir dip kırılınca çıkmak.
- **Cevap: hayır, red.** Ortalama R ve toplam R iki listede de arttı, ama düşüş (DD) iki listede de %25 sınırını aştı.
  - Eski 16: işlem 230 → **172**, ortalama +1.35R → **+2.33R**, toplam 311.3R → **400.3R**, net +%827 → **+%1211**, DD %23.7 → **%28.8** (sınır %25).
  - Yeni 20: işlem 193 → **172**, ortalama +0.61R → **+1.07R**, toplam 117.7R → **184.3R**, net +%134 → **+%137**, DD %22.6 → **%31.0** (sınır %25).
- **Neden reddedildi (DD dışında da):**
  - Kazancın neredeyse tamamı **2020'de açılan birkaç işlemden** geliyor (eski 16: BTC 2020-10 +12.8 → +63.6R, LINK, ETH, ADA 2020; yeni 20: THETA 2020-12 +24.1 → **+136.1R**). 2020 dışında çıkışı değişen işlemler iki listede de **eksi** (-7.8R / -15.2R).
  - Yeni 20'de THETA tek başına toplam R'nin %74'ü, net kârın %94'ü. THETA hariç toplam 93.7R → 48.2R (temelden kötü).
  - Doğrulama + kasa dönemi (2025-26) iki listede de **kötüleşti**: +12.4R → +6.9R ve -15.5R → -22.8R.
  - Daha uzun tutulan işlemler yer kapatıyor: temelin 64 / 22 işlemi (toplam +61.4R / +39.7R) hiç açılamadı.
- 10 günlük dip çıkışı pratikte EMA20 çıkışının **daha geç** bir hâli: dip kırıldığı günlerin %99.6'sinde kapanış zaten EMA20'nin altında. Yeni kural hiçbir işlemi daha erken kapatmadı; girişler birebir aynı (çıkış hiçbir girişi engellemedi).
- Önceki iki "yavaş çıkış" denemesiyle (EMA50, iki gün teyit) aynı tablo: eski 16'da büyük kazanç, yeni 20'de DD sınırı aşılıyor ve kazanç tek bir THETA işlemine bağlı.
- Temel `PusulaV2NoBe` değişmedi, baseline rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeExitLow10(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Long çıkışı: son kapanmış günlük kapanış, **önceki 10 günlük mumun en düşük seviyesinin** (o gün hariç) altında. Temelde: son kapanmış günlük kapanış günlük EMA20 altında.
- Aynı kalanlar: BTC-dönüş çıkışı (BTC'nin son kapanmış günlük puanı ≤ -1), sabit stop (hiç kıpırdamaz), girişler (4h ilk kapanış kırılımı, günlük puan ≥ +1, günlük kapanış EMA20 üstü, stop ≤ %8), %1 risk, en fazla 3 işlem, short yok.
- Eşik sabit (10 gün), tarama yok. Sadece kapanmış günlük mumlar.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Nasıl kodlandı (giriş çıkışa bağlı mı?)
- Bayrak günlük dosyadan hesaplanıyor (`daily_close_below_prior_low`: kapanış < önceki 10 günün en düşüğü) ve 4h mumlara `date_1d` üzerinden taşınıyor (`add_closed_daily_flag`). `date_1d`, `merge_informative_pair`'in verdiği "4h mum kapanırken kapanmış son günlük mum". Temel EMA20 çıkışı da aynı anı kullanıyor.
- Zaman damgaları tek birimde (ns) karşılaştırılıyor; günlük dosya ms olsa da sonuç aynı (birim testi bunu kontrol ediyor). Yeni veri hep günlük dosyadan, 4h analiz tablosundan değil (1000 mum sınırı sorunu yok).
- **Girişe bağlantı:** EMA20 hâlâ hesaplanıyor ve girişte ("günlük kapanış EMA20 üstü") ile günlük puanda kullanılıyor; sadece çıkış artık onu kullanmıyor.
- Freqtrade, çıkış sinyali olan mumda girişi atlar. Temelde EMA20 çıkışı (kapanış < EMA20) ile giriş şartı (kapanış > EMA20) aynı anda doğru olamaz; yani eski çıkış hiçbir girişi engellemiyordu. Yeni çıkış, kapanış hâlâ EMA20 üstündeyken de doğru olabilir (uzun yükselişten sonra sert bir gün), bu yüzden teorik olarak bir girişi engelleyebilir. **Ölçüldü: 0 giriş engellendi** (iki listede de; giriş sütunu temelle birebir aynı, etkili girişler de aynı).
- Ters yönde: EMA20 altında ama 10 günlük dibin üstünde olan günlerde artık çıkış sinyali yok, ama giriş orada kendi "EMA20 üstü" şartıyla zaten kapalı. Yeni giriş doğmuyor.
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_exit_low10_exits_on_closed_daily_close_below_previous_10_day_low`. Kontrol edilenler:
  - bayrak, düz bir döngüyle hesaplanan "önceki 10 günün dibi" ile her gün aynı;
  - kapanış EMA20 üstündeyken 10 günlük dibi kıran günde çıkış sadece o günlük mumla birlikte kapanan 4h mumdan (20:00 UTC) itibaren; aynı günün önceki 4h mumlarında yok; temelde o gün çıkış yok;
  - veri o mumun kapanışında kesilince aynı çıkış, bir mum önce kesilince çıkış yok;
  - günlük dosya ms olsa da aynı sonuç; EMA20 altı tek başına artık çıkış değil, BTC-dönüş çıkışı aynı; giriş, stop ve diğer fonksiyonlar temelden miras.
  232 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.3 | +%931.5 |
| Eski 16 | **dip 10** | 172 | **+2.327** | **400.28** | +2.304 / 396.3 | **+%1211.3** | **%28.79** | 2.09 | %26.7 | -25617 | 17.6 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | **dip 10** | 172 | **+1.072** | **184.35** | +1.057 / 181.7 | **+%137.2** | **%30.99** | 1.43 | %19.2 | -9181 | 11.0 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü. R'ler komisyon + kayma + funding dahil.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). Eski 16'da yeni sürüm al-tutun üstünde (+%1211 / +%932), temel altında; yeni 20'de ikisi de al-tutun altında.

**Karar: red.**
- Eski 16: ortalama R, toplam R ve net tuttu; **DD %28.79 > %25 tutmadı**. Düşüş 2024-03-20 → 2024-11-06 (temelin en büyük düşüşüyle aynı dönem, %23.75 → %28.79). Bu pencerede kapanan 39 işlem -5.0R (temelde 42 işlem +10.3R).
- Yeni 20: ortalama R ve toplam R tuttu, net çok az (+%134.2 → +%137.2); **DD %30.99 > %25 tutmadı**. Düşüş 2021-05-15 → 2023-11-28: THETA ve NEO 2021 başındaki büyük kazancın ardından hesap 2.5 yıl zirvenin altında kaldı (temelin en büyük düşüşü 2024-12 → 2026-09).

## Çıkışı değişen işlemler (temelle aynı saatte açılan işlemler)
| | Eski 16 | Yeni 20 |
|---|---|---|
| Ortak işlem (aynı coin, aynı açılış) | 166 | 171 |
| — çıkışı aynı (R birebir aynı) | 98 | 115 |
| — çıkışı değişti | 68 | 56 |
| — bunların daha geç kapananı / daha erken kapananı | 66 / **0** | 52 / **0** |
| Değişenlerin R'si: temel → yeni | +193.9 → +338.0 (**+144.2**) | +107.9 → +202.7 (**+94.8**) |
| Değişenlerin ortalama süresi | 15.0 → 31.2 gün | 10.2 → 20.8 gün |
| Değişenlerin çıkışı yeni sürümde: sinyal / stop / dönem sonu | 34 / **33** / 1 | 22 / **34** / 0 |

(Kalan 4 / 2 işlem aynı saatte kapandı ama çıkış nedeni farklı. Hiçbir işlem daha erken kapanmadı: 10 günlük dip kırıldığı günlerin 2100 / 2107'sinde (eski 16) ve 2876 / 2887'sinde (yeni 20) kapanış zaten EMA20 altında; EMA20 altında ama dibin üstünde olan gün 18060 / 22956.)

### Daha uzun koşan kazananlar ve daha çok kaybedenler
| Grup | Eski 16 işlem | Eski 16 R: temel → yeni | Yeni 20 işlem | Yeni 20 R: temel → yeni |
|---|---|---|---|---|
| **Daha iyi bitenler (hepsi daha geç çıktı)** | 19 | +47.7 → +245.7 (**+198.0**) | 8 | +28.1 → +181.1 (**+153.0**) |
| — temelde kazanan, daha da büyüdü | 13 | +49.8 → +157.9 (+108.0), süre 24 → 67 gün | 3 | +30.8 → +173.7 (+143.0), süre 29 → 108 gün |
| — temelde kaybeden/sıfır, kazanca döndü | 6 | -2.2 → +87.8 (+90.0), süre 5 → 70 gün | 5 | -2.6 → +7.4 (+10.0), süre 6 → 31 gün |
| **Daha kötü bitenler** | 49 | +146.2 → +92.4 (**-53.9**) | 48 | +79.8 → +21.5 (**-58.3**) |
| — temelde kazanan, kârın bir kısmını geri verdi | 19 | +163.6 → +124.0 (-39.6) | 15 | +98.2 → +58.2 (-39.9) |
| — temelde küçük kayıp/kâr, daha çok kaybetti (çoğu sabit stopa kadar düştü) | 30 | -17.4 → -31.6 (-14.3) | 33 | -18.4 → -36.7 (-18.3) |

- Değişen işlemlerin %72 / %86'sı daha kötü bitti; kazanç az sayıda çok büyük işlemden geliyor.
- En büyük iyileşmeler: eski 16 BTC 2020-10 +12.8 → +63.6R (62 → 167 gün), LINK 2020-06 -0.3 → +37.0R, ETH 2020-10 -0.5 → +34.3R, ADA 2020-05 -0.1 → +14.4R, BTC 2023-10 +22.6 → +34.9R, BTC 2024-10 +1.4 → +13.3R; yeni 20 THETA 2020-12 +24.1 → +136.1R (39 → 150 gün), NEO 2021-02 +5.7 → +33.0R, IOTA 2020-07 -0.2 → +5.1R.
- En büyük kötüleşmeler (geri verilen kâr): eski 16 SOL 2023-10 +58.6 → +49.6R, BNB 2021-01 +53.0 → +48.7R, TRX 2021-03 +14.1 → +10.1R, BTC 2024-01 +20.8 → +17.3R; yeni 20 FIL 2021-03 +33.0 → +22.2R, FIL 2024-11 +10.6 → +5.0R, ALGO 2024-11 +34.5 → +29.3R, ZEC 2020-07 -0.3 → -3.0R.
- Kuyruğun öngördüğü risk görüldü: dik yükselişten sonra 10 günlük dip uzak kalıyor ve büyük kazananlar kârın bir kısmını geri veriyor; küçük işlemler ise toparlanmayı beklerken stopa kadar düşüyor.
- **Açılış yılına göre değişen işlemlerin farkı:** eski 16 2020 **+152.0R**, diğer yıllar toplam -7.8R; yeni 20 2020 **+109.9R**, diğer yıllar toplam -15.2R. Çıkış değişikliğinin kazancı 2020'nin uzun boğa trendlerinden.

## Süreler
| | Eski 16 temel | Eski 16 dip 10 | Yeni 20 temel | Yeni 20 dip 10 |
|---|---|---|---|---|
| Ortalama süre (gün) | 11.3 | 17.6 | 8.1 | 11.0 |
| Ortanca süre (gün) | 6.6 | 7.8 | 3.5 | 4.0 |
| En uzun işlem (gün) | 83 | 166 | 50 | 150 |
| Kazananların ortalama süresi | 24.9 | 47.2 | 22.0 | 33.2 |
| Kaybedenlerin ortalama süresi | 4.9 | 6.7 | 3.8 | 5.7 |
| Kazananların ortalama R'si | +6.00 | +11.40 | +5.59 | +9.95 |
| Stopla biten oran | %41.7 | **%62.8** | %54.4 | **%75.0** |

- Ortanca süre az değişiyor: çoğu işlem zaten birkaç günde stopla bitiyor. Fark uzun kazananlarda.

## Funding
| | Eski 16 temel | Eski 16 dip 10 | Yeni 20 temel | Yeni 20 dip 10 |
|---|---|---|---|---|
| Toplam funding (USDT) | -14077 | **-25617** | -3769 | **-9181** |
| Hesap-R cinsinden (funding / işlem açılışındaki sermayenin %1'i) | -42.9 | **-70.9** | -24.8 | **-79.0** |
| İşlem-günü başına (USDT) | -5.4 | -8.5 | -2.4 | -4.9 |

- Uzun tutmak funding maliyetini artırıyor (yeni 20'de üç katı). R'ler zaten funding dahil; yukarıdaki kazanç bu maliyetten sonra.

## Yer etkisi (3 işlem sınırı)
| | Eski 16 | Yeni 20 |
|---|---|---|
| Temelin açıp yeni sürümün açamadığı işlem | 64 (**+61.4R**, ort. +0.96) | 22 (**+39.7R**, ort. +1.81) |
| Yeni sürümün açıp temelin açmadığı işlem | 6 (+6.3R) | 1 (+11.6R, VET 2020-07) |
| Ortalama açık işlem | 1.07 → 1.25 | 0.63 → 0.78 |
| Yer yok günleri (3 yer dolu) | %24.3 → **%32.6** | %12.5 → **%17.3** |

- Kaybedilen işlemlerin büyükleri: eski 16 ETH 2020-12 +9.5, ETH 2024-02 +8.9, LINK 2020-06 +7.8, XRP 2020-07 +6.9, BTC 2020-12 +6.9; yeni 20 VET 2020-06 +14.4, NEO 2021-03 +9.7, DASH 2024-11 +9.1, IOTA 2020-07 +7.9, ALGO 2023-11 +6.8. Neden açılamadı: eski 16'da 37'sinde (+23.3R) yeni sürümün 3 yeri doluydu, 27'sinde (+38.2R) aynı coin hâlâ eski işlemdeydi (21'inde yerler de doluydu); yeni 20'de 15'inde (+22.1R) yerler doluydu, 7'sinde (+17.6R) coin hâlâ işlemdeydi.
- Net etki: çıkış değişikliği +144.2 / +94.8R, yer kaybı -55.1 / -28.1R.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 dip 10 | 20 temel | 20 dip 10 |
|---|---|---|---|---|
| 2020 | +44.4 (46) | **+153.8** (21) | +31.5 (29) | **+130.8** (25) |
| 2021 | +164.3 (32) | +148.8 (24) | +41.7 (27) | +46.6 (21) |
| 2022 | -6.6 (7) | -7.0 (7) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +84.1 (33) | -1.9 (39) | -9.0 (34) |
| 2024 | +10.0 (57) | +13.6 (45) | +64.9 (36) | +41.8 (33) |
| 2025 | +15.5 (31) | +6.0 (25) | -19.8 (41) | -23.0 (38) |
| 2026 | -3.1 (19) | +0.9 (17) | +4.3 (15) | +0.3 (15) |

- Geliştirme dönemi (2020-2024): 16'da +298.8R (180, ort. +1.66) → +393.4R (130, ort. +3.03); 20'de +133.2R (137, ort. +0.97) → +207.1R (119, ort. +1.74).
- **Doğrulama + kasa dönemi (2025-2026):** 16'da +12.4R (50, ort. +0.25) → **+6.9R** (42, ort. +0.16); 20'de -15.5R (56, ort. -0.28) → **-22.8R** (53, ort. -0.43). İki listede de kötü.
- 2020 hariç: 16'da +266.9R (184) → +246.5R (151); 20'de +86.2R (164) → +53.6R (147). 2020'yi çıkarınca yeni sürüm iki listede de temelden kötü.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplam R'deki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | dip 10 | ETC 2021-03 +94.1 | %24 | **+1.791** | **+0.642** | +1.773 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | dip 10 | THETA 2020-12 +136.1 | **%74** | **+0.282** | **-0.373** | +0.274 |

- Yeni sürümün en büyük 5'i: eski 16 ETC 2021-03 +94.1, BTC 2020-10 +63.6, SOL 2023-10 +49.6, BNB 2021-01 +48.7, LINK 2020-06 +36.9; yeni 20 THETA 2020-12 +136.1, NEO 2021-02 +33.0, ALGO 2024-11 +29.3, UNI 2024-02 +26.1, FIL 2021-03 +22.2.
- Eski 16'da kazanç birkaç işleme yayılmış (en büyük 5 hariç bile ortalama arttı). Yeni 20'de tersi: THETA hariç ortalama düştü, en büyük 5 hariç -0.37R. Net kârın %94'ü THETA'dan (12957 / 13724 USDT); THETA hesap küçükken (≈ 9600 USDT) açıldı, sonraki kayıplar daha büyük hesapta oldu, bu yüzden R artışı nete neredeyse yansımadı.

## İleriye bakma kontrolü
- Yeni kural sadece kapanmış günlük mumları kullanıyor: 10 günlük dip bir gün kaydırılmış (o gün dahil değil), bayrak `date_1d` (kapanmış son günlük mum) üzerinden okunuyor.
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 150 rastgele 4h an + 150 "çıkış başlangıcı" anı (çıkış sinyalinin açıldığı mumun kapanışı). Her anda her coin için tam veri ile o anda kesilmiş 4h ve günlük veri (BTC dahil) karşılaştırıldı (giriş, çıkış, dip bayrağı, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4733 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5752 kontrol, **0 fark**.
- Çıkışı değişmeyen ortak işlemler (98 / 115) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor (fark 0.0000R).

## Uyarılar
- Fikir önceden yazılmış genel bir kuraldı (Turtle "System 1" çıkışı), bir önceki turun işlemlerinden seçilmedi.
- Dört "yavaş çıkış" denemesi (kuyruk 2 tur 4 EMA50, 22 iki gün teyit, 25 yarım çıkış, 30 10 gün dibi) aynı sonucu verdi: eski 16'da toplam R artıyor, ama kazanç 2020-21'in birkaç uzun trendinden (BTC 2020-10, BNB 2021-01, THETA 2020-12) geliyor; yeni 20'de DD %25'i aşıyor veya kazanç tek işleme bağlı kalıyor; 2025-26'da iyileşme yok. Çıkışı yavaşlatmanın genel bir avantajı görünmüyor; EMA20 çıkışı kalıyor.
- Dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeExitLow10 --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/low10_<liste>`.
- Isınma: 400 mum (sınıf ayarı), iki sürümde aynı; 10 günlük dip için yeterli.
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu (funding, çıkış türleri, coin tablosu, grafikler). Alt raporlardaki "Yön: long + short" satırı şablon metni; short işlem yok (tabloda 0).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Analiz betikleri repo dışında (`/home/user/asgo_scratch/low10/`).
