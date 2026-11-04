# Kuyruk 27 — her kırılım mumu sinyal ("ilk kapanış" şartı yok) — 2026-11-04 (temel: PusulaV2NoBe)

## GUO'ya not
- **Soru:** 4h kırılımda sadece **ilk** kapanışı değil, fiyat önceki 20 mumun tepesinin üstünde kapandığı **her** mumu sinyal saysak daha iyi olur muyduk? Fikir: bir kırılım kaçarsa (yer dolu, emir dolmadı), bir sonraki mumda ikinci şans olsun.
- **Cevap: hayır, red.** Yeni 20'de üç şart da tutmadı. Eski 16'daki iyileşme neredeyse tamamen tek işlemden.
  - Eski 16: ortalama +1.35R → +1.53R, toplam 311.3R → 354.5R, net +%827 → +%1216, DD %23.7 → %15.8. Dört şart tuttu, ama +43.3R'nin +42.7R'si **tek işlem**: XLM 2024-11. O hariç ortalama +1.356R (temel +1.353R), yani fark yok.
  - Yeni 20: ortalama +0.61R → **+0.59R**, toplam 117.7R → **116.0R**, net +%134 → **+%130**, DD %22.6 → %22.6. **Ortalama R, toplam R ve net tutmadı.**
- **Değişiklik çok az işlem değiştirdi:** 231 / 196 işlemden 218 / 184'ü temelle birebir aynı. Sadece 13 / 12 yeni giriş var.
  - Ek sinyal mumu çok (558 / 255), ama çoğu işe yaramıyor: coinde zaten işlem açık, 3 yer dolu, ya da aynı mumda çıkış sinyali var.
  - Fikrin beklediği "ikinci şans" (yer dolu ya da emir dolmadı diye kaçan kırılım) neredeyse hiç olmadı: 25 yeni girişten sadece 4'ü.
  - Yeni girişlerin çoğu başka bir yerden geldi: kırılım günün ortasında başladı, günlük şartlar (puan ≥ +1, çıkış sinyali yok) ise ancak gün kapanınca sağlandı. Temel bu durumda giremiyor, yeni sürüm bir sonraki mumda giriyor. XLM 2024-11 de böyle.
- Temel `PusulaV2NoBe` değişmedi, baseline rakamları birebir aynı (230 / 193 işlem; 311.26R / 117.72R).

---

## Kural (testten önce yazıldı)
`PusulaV2NoBeEveryBreakout(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- Long kırılım şartı `first_true(close > önceki 20 mumun tepesi)` yerine sadece `close > önceki 20 mumun tepesi`. Yani tepenin üstünde kapanan **her** 4h mum sinyal.
- Aynı kalanlar: coinin günlük puanı ≥ +1, giriş bölgesi ortasında limit emir (3 mum geçerli), stop, çıkışlar (günlük EMA20, BTC-dönüş, sabit stop), %1 risk, en fazla 3 işlem, short yok.
- Coinde açık işlem (ya da bekleyen giriş emri) varken yeni giriş yok. Bu Freqtrade'in kendi kuralı (coin başına bir işlem); değiştirilmedi.
- Eşik yok, tarama yok.
- **Kabul kuralı (önceden):** iki listede de ortalama R, toplam R ve hesap net getirisi temelden iyi ve DD ≤ %25.

## Nasıl kodlandı
- Yeni sınıf sadece `signal_conditions`'ı değiştiriyor: `breakout_up` şartını ilk-mum kısıtı olmadan yeniden yazıyor. Diğer bütün fonksiyonlar (göstergeler, plan, stop, çıkış, büyüklük, kaldıraç, emir iptali) temelden miras.
- Birim testi: `tests/test_pusula.py`, `test_v2_no_be_every_breakout_signals_on_every_close_above_the_channel`. Kontrol edilenler:
  - temelle aynı fonksiyonlar miras, ek `confirm_trade_entry` yok;
  - üst üste 2 mum tepenin üstünde kapanınca temel sadece ilkinde, yeni sürüm ikisinde de sinyal veriyor;
  - puan -1 olan mumda sinyal yok;
  - sonradan eklenen bir mum eski kararları değiştirmiyor;
  - short yok.
  229 test geçti.

## Sonuç (2020-03 → 2026-09, sadece long, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Ort. süre (gün) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.353 | 311.26 | +1.342 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | 11.3 | +%931.5 |
| Eski 16 | **her kırılım** | 231 | **+1.535** | **354.53** | +1.522 / 351.5 | **+%1215.9** | **%15.81** | 2.36 | %32.9 | -15387 | 11.5 | +%931.5 |
| Yeni 20 | temel | 193 | +0.610 | 117.72 | +0.600 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | 8.1 | +%194.7 |
| Yeni 20 | **her kırılım** | 196 | **+0.592** | **116.00** | +0.582 / 114.1 | **+%129.5** | %22.63 | 1.51 | %23.5 | -3871 | 8.0 | +%194.7 |

- Hesap-R = kâr / (işlem açılırken, kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem (al-tut DD %89 / %98). İki sürüm de al-tutun altında; eski 16'da yeni sürüm al-tutu geçiyor (+%1216 > +%931), ama bu tek işlemden (aşağıda).

**Karar: red.**
- Eski 16: dört şart tuttu (+1.353 → +1.535R; 311.26 → 354.53R; +%827.3 → +%1215.9; DD %15.81).
- Yeni 20: ortalama R (+0.610 → +0.592), toplam R (117.72 → 116.00) ve net (+%134.2 → +%129.5) **tutmadı**. DD (%22.63) tamam.

## Eski 16'daki iyileşme nereden
- XLM 2024-11-08 girişi **+42.7R**, tek başına +36.2k USDT. Net farkın (+38.9k USDT) %93'ü.
- XLM hariç: toplam 311.8R, ortalama +1.356R. Temel: 311.3R, +1.353R. Yani fark yok.
- DD de bu işlemden düştü: temelin en büyük düşüşü 2024-03 → 2024-12 arasıydı; XLM'in kârı (2024-12-10'da kapandı) o düşüşü erken bitirdi. Yeni sürümün en büyük düşüşü 2025-08 → 2026-09 (%15.8).
- Bu XLM işlemi kuyruk 20'de de (puan şartı yok) çıkmıştı (+43.1R). İki deneme aynı trende farklı kapılardan girdi.

## Yeni girişler: kırılımdan kaç mum sonra
"Yaş" = sinyal mumu, tepenin üstündeki kesintisiz kapanış serisinin kaçıncı mumu (1 = ilk kapanış, temelin tek girdiği yer).

| Liste | Yaş | İşlem | Ortalama R | Toplam R | Kazanma |
|---|---|---|---|---|---|
| Eski 16 | 1 (ilk kapanış) | 218 | +1.432 | 312.27 | %33.0 |
| Eski 16 | 2-5 | 13 | +3.251 | 42.27 | %30.8 |
| Eski 16 | 6+ | 0 | — | 0 | — |
| Yeni 20 | 1 (ilk kapanış) | 185 | +0.545 | 100.79 | %22.7 |
| Yeni 20 | 2-5 | 11 | +1.383 | 15.22 | %36.4 |
| Yeni 20 | 6+ | 0 | — | 0 | — |

- Yaşı 2-5 olan girişlerin hepsi temelde yok. Eski 16'da XLM hariç ortalamaları **-0.04R** (12 işlem). Yeni 20'de en iyisi IOTA 2020-07 +9.8R; o hariç +0.56R.
- 6 ve üstü yaşta hiç giriş olmadı: o mumlarda coin ya zaten işlemdeydi ya da 3 yer doluydu.
- Yaş dağılımı: yeni girişlerin 9 / 9'u yaş 2 (bir mum sonra). 13 girişin 12'si (eski 16) ve 12 girişin 9'u (yeni 20) 00:00 UTC'de açıldı, yani sinyal mumu günün son 4h mumu ve günlük mum onunla birlikte kapandı.

### Temel bu kırılımları neden kaçırmıştı
Her yeni (temelde olmayan) giriş için kırılım serisinin ilk mumuna bakıldı:

| Neden (ilk kapanışta) | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Coinin günlük puanı henüz -1 idi | 5 | **+41.66** (XLM +42.7 dahil) | 3 | +3.07 |
| Aynı mumda çıkış sinyali vardı (günlük kapanış EMA20 altı) | 2 | -2.13 | 5 | **+15.35** |
| Stop %8'den uzaktı (`plan_ok` yok) | 4 | +4.85 | 2 | -2.08 |
| Temelin emri dolmadı | 2 | -2.11 | 1 | -1.13 |
| Temelde 3 yer doluydu | 0 | 0 | 1 | +0.76 (FIL 2023-12, yaş 1) |
| **Toplam** | 13 | **+42.27** | 12 | **+15.97** |

- Kuyruğun beklediği iki durum (emir dolmadı, yer dolu) toplam 3 + 1 işlem ve **-2.5R**. Kuyruk 23'te dolmadan iptal olan iyi sinyaller burada geri gelmedi: emir dolmayınca fiyat genelde yükselmeye devam ediyor, sonraki mumların giriş bölgesi daha yukarıda kalıyor ya da stop %8'i aşıyor.
- Asıl yeni girişler "gecikmeli onay": 4h kırılım gün içinde geldi, ama günlük şart (puan ≥ +1 ya da EMA20 üstü kapanış) ancak o gün kapanınca sağlandı. Günlük veri 4h tabloya gün kapanınca giriyor (ileriye bakma yok); temel o anda ilk mumda olmadığı için giremiyordu.

### Ek sinyal mumları neden çoğunlukla işlem olmadı
Yeni sürümde tepenin üstünde ama ilk olmayan sinyal mumu 558 (eski 16) / 255 (yeni 20); ilk kapanış sinyali 1621 / 855. Ek mumlarda o anki durum:

| Durum | Eski 16 | Yeni 20 |
|---|---|---|
| Yeni işlem açıldı | 13 | 12 |
| Coinde zaten işlem açıktı (genelde aynı kırılımın ilk mumunda açılan) | 218 | 85 |
| 3 yer doluydu | 229 | 139 |
| Aynı mumda çıkış sinyali (Freqtrade girişi yok sayar) | 82 | 11 |
| Emir verildi, dolmadı / iptal | 16 | 8 |

## Aynı trendde yeniden giriş
- **Aynı kırılım serisinde** (işlem kapandıktan sonra fiyat hâlâ tepenin üstündeyken tekrar giriş): iki listede de **0**. İşlem stopla ya da EMA20 çıkışıyla kapandığında fiyat neredeyse hiç 20 mumluk tepenin üstünde değil; olsa da aynı mumda çıkış sinyali girişi engelliyor.
- **Aynı günlük trendde** (önceki işlem kapandıktan sonra coinin puanı hiç +1'in altına inmeden yeni giriş):
  - Eski 16: temel 93 işlem +243.6R (ort. +2.62); yeni 96 işlem +235.9R (+2.46).
  - Yeni 20: temel 43 işlem +40.9R (+0.95); yeni 46 işlem +43.7R (+0.95).
  - Yani yeniden giriş davranışı neredeyse değişmedi. Coin başına en çok işlem 42 → 44 / 20 → 22.

## Yer etkisi
İşlemler coin + açılış zamanıyla eşleştirildi.

| Parça | Eski 16 işlem | Eski 16 R | Yeni 20 işlem | Yeni 20 R |
|---|---|---|---|---|
| Ortak işlemler (R birebir aynı) | 218 | 0.00 | 184 | 0.00 |
| Yeni girişler (temelde olmayan) | +13 | **+42.27** | +12 | **+15.97** |
| Kaybedilen girişler (temelin aldığı, yeni sürümün alamadığı) | -12 | **-1.00** | -9 | **+17.69** |
| **Toplam fark** | 230 → 231 | **+43.27** | 193 → 196 | **-1.72** |

- **Kaybedilen girişler, neden:**
  - Eski 16: 9'u 3 yer dolu (-5.6R; SOL 2024-11-08 +1.8R, XLM yerini aldı), 3'ü coin meşgul (+4.6R; ETH 2021-04 aynı hareketin 12 saat önceki girişi).
  - Yeni 20: 6'sı 3 yer dolu (+1.9R; ALGO 2023-11 +6.8R dahil), 3'ü coin meşgul (+15.8R).
- **Yeni 20'deki "coin meşgul" üçlüsü aynı hareketin daha erken girişi:** IOTA 2020-07 (+7.9 → +9.8R), ZEC 2021-10 (+4.1 → +4.8R), XTZ 2024-02 (+3.8 → +5.8R). Bu üçü yeni sürüme toplam +4.7R kazandırdı. Diğer 9 yeni giriş -4.6R, yer kayması -1.9R. Net -1.7R.
- 3 yerin dolu olduğu gün oranı: eski 16'da %24.3 → %25.1, yeni 20'de %12.5 → %12.5. Ortalama açık işlem 1.07 → 1.08 / 0.63 → 0.64.

## Yıllara göre (R, açılış yılına göre; parantezde işlem sayısı)
| Yıl | 16 temel | 16 her kırılım | 20 temel | 20 her kırılım |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +43.3 (47) | +31.5 (29) | +33.7 (29) |
| 2021 | +164.3 (32) | +163.5 (33) | +41.7 (27) | +42.3 (27) |
| 2022 | -6.6 (7) | -6.6 (7) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +88.5 (38) | -1.9 (39) | **-7.8** (41) |
| 2024 | +10.0 (57) | **+55.2** (54) | +64.9 (36) | +66.2 (37) |
| 2025 | +15.5 (31) | +14.8 (32) | -19.8 (41) | -19.8 (41) |
| 2026 | -3.1 (19) | -4.1 (20) | +4.3 (15) | +4.3 (15) |

- Eski 16'daki farkın tamamı 2024'te (XLM 2024-11). Diğer yıllar ±2R.
- Yeni 20'de 2023 kötüleşti (-5.9R): ALGO 2023-11 (+6.8R) yer kaybından girilemedi; 3 ek giriş (DASH, FIL, THETA) toplam sadece +0.9R.
- Doğrulama + kasa dönemi (2025-2026): 16'da +12.4 → +10.7R, 20'de -15.5 → -15.5R. Yeni sürüm bu dönemde iyileştirmedi.

## Yoğunlaşma (tek işlem)
| Liste | Sürüm | En büyük işlem | Toplamdaki payı | En büyük hariç ort. R | En büyük 5 hariç ort. R | En büyük hariç hesap-R ort. |
|---|---|---|---|---|---|---|
| Eski 16 | temel | ETC 2021-03 +94.1 | %30 | +0.948 | +0.276 | +0.941 |
| Eski 16 | her kırılım | ETC 2021-03 +94.1 | %27 | +1.132 | +0.370 | +1.124 |
| Yeni 20 | temel | ALGO 2024-11 +34.5 | %29 | +0.434 | -0.076 | +0.426 |
| Yeni 20 | her kırılım | ALGO 2024-11 +34.5 | %30 | **+0.418** | **-0.084** | +0.411 |

- Eski 16'nın en büyük 5'i: temel ETC 2021-03 +94.1, SOL 2023-10 +58.6, BNB 2021-01 +53.0, BTC 2023-10 +22.6, BTC 2024-01 +20.8. Yeni sürümde XLM 2024-11 +42.7 dördüncü sıraya giriyor, BTC 2024-01 çıkıyor. En büyük hariç ortalamalardaki iyileşme XLM'den: ETC ve XLM'in büyük işlemleri hariç ortalama +0.948R → +0.951R.
- Yeni 20'nin en büyük 5'i iki sürümde aynı (ALGO 2024-11, FIL 2021-03, UNI 2024-02, THETA 2020-12, VET 2020-06).

## İleriye bakma kontrolü
- Yeni kural yeni veri kullanmıyor: aynı 20 mumluk tepe (`dc_upper`, bir mum kaydırılmış, sinyal mumunu içermiyor) ve aynı kapanmış günlük mumlar. Sadece ilk-mum kısıtı yok.
- Veri kesme testi bu sınıfla çalıştırıldı: her listede 300 an (150 rastgele 4h mum, 150 "ilk olmayan kırılım mumunda sinyal" anı). Her anda her coin için tam veri ile o anda kesilmiş veri karşılaştırıldı (giriş, çıkış, ilk-olmayan sinyal işareti, `long_stop`, `long_plan_ok`).
  - Eski 16: 300 an, 4728 coin-an kontrolü, **0 fark**.
  - Yeni 20: 300 an, 5676 kontrol, **0 fark**.
- Ortak işlemler (218 / 184) temelle aynı saatte açılıp kapanıyor ve birebir aynı R'yi veriyor (fark 0.0000R).

## Uyarılar
- Eski 16'daki büyük net ve DD iyileşmesi tek işlemin (XLM 2024-11) hesabın en büyük olduğu dönemde gelmesinden. Bu bir şans faktörü; kural iki listede tutarlı fark yaratmadı.
- Yeni girişlerin çoğu "kırılım + günlük onay aynı gün içinde, farklı mumlarda" durumu. Bu ayrı bir fikir olarak (ör. günlük kapanışla kırılım) kuyruğa yazıldı (madde 28); bu turdaki sonuçla seçilmiş bir eşik yok.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeEveryBreakout --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/every_<liste>`.
- Alt raporlar (`wide16/rapor.md`, `new20/rapor.md`): `scripts/make_report.py`'nin `build_report` fonksiyonu (funding, çıkış türleri, coin tablosu, grafikler).
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor. Önceki turlar da aynı aralığı kullandı; yeni bir kasa kullanımı yok.
