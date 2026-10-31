# Kuyruk 22 — çıkış gevşetme: EMA20 çıkışı için 2 gün üst üste kapanış — 2026-10-31 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: işlemi, günlük kapanış 20 günlük ortalamanın (EMA20) altına **bir kez** inince değil, **iki gün üst üste** inince kapatsak, uzun trendleri daha iyi taşır mıyız?
- Cevap: **eski 16'da evet, yeni 20'de hayır.**
  - Eski 16: ortalama +1.35R → +1.93R, toplam 311.3R → 366.3R, net +%827 → +%1161, DD %23.7 → %24.9. Kazancın neredeyse tamamı 2020 yılından (LINK, ADA, ETH trendleri).
  - Yeni 20: ortalama +0.61R → +0.65R, ama toplam 117.7R → **114.5R**, net +%134 → **+%127**, DD %22.6 → **%25.5** (sınır %25).
- Ne oluyor: 1 günlük düşüşten sonra trend devam ederse kazanç büyük (eski 16'da birkaç işlem +20R ile +50R arası büyüdü). Ama çoğu işlemde ikinci gün de düşüş geliyor ve işlem daha geç, daha kötü fiyattan kapanıyor; bir kısmı stopa gidiyor. Yeni 20'de bu iki etki birbirini götürdü, düşüş derinleşti.
- **Karar: red** (yeni 20'de toplam R, net ve DD şartı tutmadı). Temel `PusulaV2NoBe` değişmedi.

## Kural (testten önce yazıldı)
`PusulaV2NoBeExit2d(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Günlük EMA20 çıkışı: long, **2 gün üst üste kapanmış** günlük kapanış EMA20 altında olunca kapanır (temelde: son kapanmış günlük kapanış EMA20 altında olunca). Sadece kapanmış günlük mumlar sayılır.
- Aynı kalanlar: BTC-dönüş çıkışı (BTC'nin son kapanmış günlük puanı ≤ -1), sabit stop, girişler, %1 risk, en fazla 3 işlem. Eşik (2 gün) sabit, tarama yok.
- **Kabul kuralı** (önceden): iki listede de ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → kabul; aksi halde red.

## Nasıl kodlandı
- `below_ema_run`: her günlük mum için "kaç gündür üst üste kapanış EMA20 altında" sayacı. EMA temeldekiyle aynı hesap (20 günlük, aynı başlangıç). EMA henüz yoksa "altında değil" sayılır (temeldeki gibi).
- `add_below_ema_run`: sayaç 4h tabloya, o 4h mumun gördüğü son **kapanmış** günlük mumdan eklenir (`date_1d` ile; kuyruk 15'teki trend yaşıyla aynı yöntem). Böylece çıkış, temeldeki çıkışla aynı anda değerlendirilir; sadece eşik 1 yerine 2.
- `populate_exit_trend`: `below_ema_days_1d >= 2` ise `exit_long`, ayrıca temeldeki BTC-dönüş çıkışı birebir aynı.
- **Girişi engelleme etkisi (Freqtrade, çıkış sinyali olan mumda girmez):** değişiklik girişleri etkilemiyor.
  - Long girişi zaten "son kapanmış günlük kapanış EMA20 üstü" şartını istiyor. Giriş sinyali olan mumda sayaç 0, yani ne eski ne yeni EMA20 çıkışı orada doğru olabilir. EMA20 çıkışı temelde de hiçbir girişi engellemiyordu.
  - EMA20 altındaki ilk günde çıkış artık yok, ama giriş kendi EMA20 şartı yüzünden yine kapalı.
  - BTC-dönüş çıkışı aynı, aynı mumlarda girişi engelliyor.
  - Sonuç: giriş sinyali olan mumlar temelle aynı. Değişen tek şey açık işlemin daha uzun tutulabilmesi. Bu da 3 yer sınırı ve "coinde zaten açık işlem var" yüzünden sonraki girişleri kaydırabiliyor (aşağıda).
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_exit_2d_needs_two_closed_daily_closes_below_ema20`). Kontrol edilenler:
  - sayaç düz bir döngüyle birebir aynı;
  - 4h satır son kapanmış günlük mumun sayacını görüyor;
  - veri kesilince görünen değerler değişmiyor;
  - çıkış temelde 1. günde, yeni sınıfta 2. günde geliyor; BTC-dönüş çıkışı ikisinde de var;
  - stop ve giriş metodları temelinkiyle aynı.
  225 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.4 | +%931.5 |
| Eski 16 | 2 gün çıkış | 190 | **+1.93R** | **366.32** | +1.91 / 362.8 | **+%1160.9** | %24.86 | 2.06 | %31.6 | -22770 | 15.1 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | 2 gün çıkış | 176 | +0.65R | **114.53** | +0.64 / 112.5 | **+%127.4** | **%25.45** | 1.50 | %23.3 | -4019 | 9.8 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem. İki sürüm de eski 16'da al-tutun biraz altında, yeni 20'de belirgin altında (ama DD %24-25'e karşı al-tut %89 / %98).
- Ortalama süre: kazananlar 16'da 24.9 → 35.2 gün, 20'de 22.0 → 27.1 gün; kaybedenler 4.9 → 5.9 / 3.8 → 4.5 gün.
- Çıkış türleri: 16'da EMA/BTC çıkışı 131 → 83, stop 96 → 104; 20'de 85 → 53, stop 104 → 119.
- En büyük düşüş iki sürümde aynı dönemde: 16'da 2024-03 → 2024-12, 20'de 2024-12 → 2026-09. Yeni 20'de bu düşüş %22.6'dan %25.5'e derinleşti.

**Karar: red.**
- Eski 16'da dört şart da tuttu: ortalama R, toplam R, net daha iyi, DD %24.86 ≤ %25.
- Yeni 20'de üç şart tutmadı: toplam R 117.72 → 114.53, net +%134.2 → +%127.4, DD %25.45 > %25. Sadece ortalama R daha iyi (+0.610 → +0.651), o da işlem sayısı azaldığı için.

## Etkilenen işlemler
İşlemler coin + açılış zamanıyla eşleştirildi.

| Liste | Aynı kalan | Çıkışı değişen | Temelde olup yeni sürümde olmayan | Yeni sürümde olup temelde olmayan | Etkilenen toplam |
|---|---|---|---|---|---|
| Eski 16 | 90 | 97 (95'i daha geç kapandı, 2'si aynı anda farklı sebeple) | 43 | 3 | 143 / 230 |
| Yeni 20 | 103 | 71 (67'si daha geç, 4'ü aynı anda farklı sebeple) | 19 | 2 | 92 / 193 |

- Aynı kalan işlemlerde R birebir aynı (fark 0.0000). Hiçbir işlem daha erken kapanmadı.

### Çıkışı değişen işlemler (temel R → yeni R)
| Liste | Grup | İşlem | Temel R | Yeni R | Fark | Ort. süre (gün) | Not |
|---|---|---|---|---|---|---|---|
| Eski 16 | koşusu uzayıp kazanan (fark > 0) | 38 | 56.33 | 248.11 | **+191.78** | 16.0 → 33.5 | 9'u temelde zarardaydı, artıya döndü |
| Eski 16 | daha çok kaybeden (fark ≤ 0) | 59 | 136.11 | 90.74 | **-45.38** | 16.2 → 18.4 | 26'sı stopla bitti; 6 kazanan zarara döndü |
| Eski 16 | toplam | 97 | 192.45 | 338.85 | +146.41 | 16.1 → 24.3 | |
| Yeni 20 | koşusu uzayıp kazanan | 19 | 67.50 | 109.43 | **+41.93** | 19.2 → 32.7 | 7'si zarardan artıya döndü |
| Yeni 20 | daha çok kaybeden | 52 | 96.89 | 65.09 | **-31.81** | 10.1 → 12.5 | 25'i stopla bitti; 5 kazanan zarara döndü |
| Yeni 20 | toplam | 71 | 164.39 | 174.51 | +10.12 | 12.6 → 17.9 | |

- Çoğunluk kaybediyor: değişen işlemlerin %61'i (16) ve %73'ü (20) daha kötü bitti. Kazanç birkaç büyük işlemden:
  - Eski 16: BNB 2021-01 -0.6 → +52.4R, LINK 2020-06 -0.3 → +36.9R, ADA 2020-05 -0.1 → +22.1R, ETH 2020-12 -0.0 → +21.9R, BTC 2023-10 +22.6 → +38.2R, BTC 2024-10 +1.4 → +13.8R.
  - Yeni 20: VET 2023-10 -0.2 → +10.1R, AXS 2024-11 -0.4 → +6.2R, IOTA 2020-07 -0.2 → +6.1R.
- En kötüler: TRX 2021-03 +14.1 → +10.1R, SOL 2023-10 +58.6 → +54.8R, ETH 2024-02 +8.9 → +5.6R (16); ALGO 2024-11 +34.5 → +29.3R, ENJ 2024-02 +5.7 → +3.5R, UNI 2025-06 +1.6 → -0.2R (20). Büyük trendin sonunda bir gün daha beklemek kârın bir kısmını geri veriyor.
- Değişen işlemlerin en büyük 2'si hariç fark: 16'da +56.2R, 20'de **-6.8R**.

### Yer etkisi (boşalan / kaybedilen yerler)
| Liste | Temelde olup yeni sürümde olmayan | R | Yeni sürümde olup temelde olmayan | R |
|---|---|---|---|---|
| Eski 16 | 20 işlem: aynı coinde işlem hâlâ açık (yeniden giriş yok) | +85.93 | 2 işlem: coin boştaydı | +0.92 |
| Eski 16 | 23 işlem: 3 yer dolu | +6.21 | 1 işlem: yer boştaydı | -0.12 |
| Yeni 20 | 6 işlem: aynı coinde işlem hâlâ açık | +15.96 | 1 işlem (VET 2020-07) | +12.14 |
| Yeni 20 | 13 işlem: 3 yer dolu | **+22.93** | 1 işlem (NEAR 2023-12) | +13.44 |

- Eski 16'daki "aynı coinde açık" grubunun çoğu, aynı trendin temeldeki yeniden girişi. Örnek: temelde BNB 2021-01-25 işlemi -0.6R'de kapandı, 2021-01-29'da yeniden girip +53.0R yaptı. Yeni sürümde ilk işlem hiç kapanmadı, +52.4R yaptı. Bu yüzden coin bazında bakmak daha doğru (aşağıda).
- Net hesap: eski 16: +146.41 (değişen) - 92.15 (kaybedilen) + 0.80 (yeni) = **+55.06R**. Yeni 20: +10.12 - 38.89 + 25.58 = **-3.19R**.
- Yeni 20'de uzayan işlemler 13 yerde dolu yer yüzünden toplam +22.9R'lik girişleri kaçırdı. Kazanç (+10.1R) bunu karşılamadı.

### Coin bazında R farkı
- Eski 16: 9 coin iyi, 5 kötü, 2 aynı. En iyi: LINK +30.4, BTC +19.0, ADA +18.0, ETH +13.0. En kötü: TRX -8.3, XRP -7.8, SOL -7.2, ATOM -4.2. En iyi coin (LINK) hariç fark +24.7R.
- Yeni 20: 10 iyi, 10 kötü. En iyi: NEAR +12.1 (temelde olmayan bir giriş), AXS +6.6. En kötü: ALGO -14.5, DASH -11.7. En iyi coin hariç fark -15.3R.

### Kuyruğun istediği ek ölçümler
- **1 günlük dipten dönüp devam eden trendler:** yeni sürümde açık işlem sırasında "1 gün EMA20 altında kapanış, ertesi gün tekrar üstü" olan an sayısı:
  - Eski 16: 60 an, 38 işlem. Bunların 37'si temelde de var: 20'si daha iyi, 17'si daha kötü bitti; toplam fark +171.6R. 14 işlem temelden en az 1R daha iyi bitti.
  - Yeni 20: 30 an, 27 işlem, hepsi temelde de var: 11'i daha iyi, 16'sı daha kötü; toplam fark +21.9R. 6 işlem en az 1R daha iyi.
  - Not: dipten dönen işlemin sonradan ikinci bir dipte (2 gün) kapanıp temelden kötü bitmesi de mümkün. "Dipten dönmek" tek başına kazanç demek değil.
- **Coin başına yeniden giriş:** aynı coinde, günlük puan arada +1'in altına inmeden açılan yeni işlem sayısı 16'da 96 → 65, 20'de 44 → 37. Toplam işlem 16'da -40 (BNB -8, ETH -6, TRX -6, BTC -4), 20'de -17 (AAVE -4, XTZ -3). Uzun tutulan işlem, temelin "çık, ertesi kırılımda tekrar gir" döngüsünün yerini alıyor.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | Eski 16 temel | Eski 16 2 gün | Yeni 20 temel | Yeni 20 2 gün |
|---|---|---|---|---|
| 2020 | +44.4 (46) | **+106.4** (28) | +31.5 (29) | +32.5 (25) |
| 2021 | +164.3 (32) | +155.3 (27) | +41.7 (27) | +39.0 (25) |
| 2022 | -6.6 (7) | -6.9 (7) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +93.1 (34) | -1.9 (39) | +8.6 (34) |
| 2024 | +10.0 (57) | +16.1 (46) | +64.9 (36) | +56.7 (33) |
| 2025 | +15.5 (31) | +5.5 (30) | -19.8 (41) | -20.8 (38) |
| 2026 | -3.1 (19) | -3.2 (18) | +4.3 (15) | +1.5 (15) |

- Eski 16'daki kazancın tamamı 2020'den: 2020 farkı +62.0R, toplam fark +55.1R. Diğer yıllar toplamda -6.9R (2021 -9.0, 2025 -10.0; 2023 +6.4, 2024 +6.1).
- Yeni 20'de sadece 2023 belirgin iyi (+10.5R, VET 2023-10 ve NEAR 2023-12). 2024 -8.2R (ALGO 2024-11 erken değil geç çıktı).
- Doğrulama + kasa dönemi (2025-2026) iki listede de biraz kötü: 16'da +12.4 → +2.3R, 20'de -15.5 → -19.3R.

## Yoğunlaşma (tek işlem)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 (+94.1R, hesap-R +93.1). En büyük hariç hesap-R ortalaması +0.941 → +1.427, en büyük 5 hariç +0.277 → +0.483. En büyük 5: ETC 2021-03 +94.1, SOL 2023-10 +54.8, BNB 2021-01 +52.4, BTC 2023-10 +38.2, LINK 2020-06 +36.9.
- Yeni 20: en büyük temelde ALGO 2024-11 +34.5R, yenide FIL 2021-03 +32.5R. En büyük hariç +0.426 → +0.459, en büyük 5 hariç **-0.078 → -0.099**.
- Eski 16'daki iyileşme tek işleme değil, 2020'deki birkaç trende bağlı (LINK, ADA, ETH, BNB). Yeni 20'de en büyük 5 işlem hariç iki sürüm de eksi, yeni sürüm biraz daha eksi.

## İleriye bakma kontrolü
- Çıkış sadece kapanmış günlük mumları okur: sayaç günlük tabloda hesaplanır ve 4h satıra `date_1d` (o satırın gördüğü son kapanmış günlük mum) ile eklenir. Birim testi bunu ve veri kesince değişmemeyi doğruluyor.
- Veri kesme testi: her listede 300 an (150 rastgele 4h mum, 150 tanesi bir çıkış sinyalinin yeni başladığı mum). Her anda her coin için stratejinin kendi `populate_indicators` + giriş + çıkış kodu iki kez çalıştırıldı: tam veriyle ve o anda kesilmiş veriyle (4h mumlar o ana kadar kapanmış olanlar, günlük mumlar ve BTC günlükleri kapanışı o ana kadar olanlar). Giriş sinyali, çıkış sinyali ve sayaç karşılaştırıldı.
  - Eski 16: 300 an, 4734 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5677 kontrol, **0 fark**.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeExit2d --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/exit2d_<liste>`. Rapor `scripts/make_report.py --results <zip> --test iki_gun_cikis --out results/2026-10-31_pusula_iki_gun_cikis/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
