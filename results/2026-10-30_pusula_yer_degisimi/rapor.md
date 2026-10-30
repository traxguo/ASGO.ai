# Kuyruk 21 — yer yönetimi: dolu yerde kötü işlemi yeni sinyale bırak — 2026-10-30 (temel: PusulaV2NoBe)

## GUO'ya not
- Soru: 3 yer doluyken yeni bir kırılım sinyali gelirse, en az 10 gündür açık ve o an zararda (0R altı) olan en kötü işlemi kapatıp yeri yeni sinyale vermek sonucu iyileştirir mi?
- Cevap: **neredeyse hiç olmuyor.** 6.5 yılda eski 16'da **tek bir** değişim oldu, yeni 20'de **hiç** olmadı. Sebep: 20 günlük ortalama çıkışı zararda kalan işlemi zaten çabuk kapatıyor; "dolu yer + yeni sinyal" anlarında 10 günden yaşlı işlemlerin neredeyse hepsi kârda (sadece %1-2'si +0.5R'nin altında).
- Tek değişim de kötü sonuçlandı: BTC 2023-07 işlemi -0.59R'de kapandı (temelde -0.73R'de bitecekti, +0.14R kazanç), yerine giren LTC ertesi gün stop oldu (-1.04R). Net **-0.89R**.
- **Karar: red** (eski 16'da ortalama R, toplam R ve net biraz kötü; yeni 20'de birebir aynı, yani daha iyi değil). Temel `PusulaV2NoBe` değişmedi.
- Ders: "hangi işlem yer tutuyor" sorunu, yaşlı ve zararda işlemlerden kaynaklanmıyor; yer kayması, aynı gün gelen kırılımlar arasında kimin önce girdiğinden geliyor (kuyruk 7, 19, 20).

## Kural (testten önce yazıldı)
`PusulaV2NoBeSlotSwap(PusulaV2NoBe)` (kod: `strategies/candidates/pusula.py`):
- 3 yer doluyken geçerli yeni bir long sinyali varsa, açık işlemlerden **en az 10 gündür (60 adet 4h mum) açık ve o anki sonucu 0R'nin altında** olanların en kötüsü (en düşük anlık R) o mumda kapatılır, yeni sinyal girer.
- Uygun açık işlem yoksa hiçbir şey değişmez. Mum başına en fazla bir değişim. Stop, çıkışlar (günlük EMA20, BTC-dönüş), %1 risk, en fazla 3 işlem: aynı. Eşikler (10 gün, 0R) sabit, tarama yok.
- **Kabul kuralı** (önceden): iki listede de ortalama R, toplam R ve hesap net getirisi daha iyi ve DD ≤ %25 → kabul; aksi halde red.

## Nasıl kodlandı (Freqtrade'de hazır "yer değişimi" yok)
- `populate_exit_trend` her coin için üç şeyi kaydeder: geçerli long sinyali olan 4h mumlar (giriş var, çıkış yok; Freqtrade'in kendi kuralı), açık işlemi kendi çıkış sinyaliyle kapatacak mumlar ve her mumun kapanışı.
- `custom_exit` her açık işlem için çağrılır. 4 saatlik mumun başında (backtestte ilk 1 saatlik detay mumu, canlıda mumun ilk saati) karar **sadece az önce kapanmış mumdan** kurulur:
  - aday = o mumda geçerli sinyali olan, açık işlemi veya bekleyen emri olmayan, bu mum içinde işlemi kapanmamış coin;
  - yer dolu = açık işlem (bekleyen giriş emri dahil) − kendi çıkış sinyaliyle bu mum çıkacak işlem ≥ 3;
  - uygun = kalan işlemlerden en az 10 gündür açık olan ve anlık R < 0 olan; anlık R = (kapanmış mumun kapanışı − giriş fiyatı) / (giriş fiyatı − planlanan stop), masrafsız;
  - seçilen = en düşük anlık R (eşitlikte en eski).
  Sadece seçilen işlemin `custom_exit`'i `slot_swap` döndürür; işlem 4h mumun açılışından kapanır.
- Freqtrade her zaman adımında önce açık işlemli coinleri, sonra diğerlerini işler. Bu yüzden boşalan yer, aynı adımda aday coinin giriş sinyaline kalır; adaylar temeldeki gibi liste sırasıyla girer. Yeni giriş ortak modülün normal limit emridir; 3 mum içinde dolmazsa yer boş kalır (değişim geri alınmaz).
- **Yeni girişin boşalan yeri aldığının kontrolü:**
  - Gerçek testte (eski 16) tek değişim: BTC 2023-07-13 08:00'de `slot_swap` ile kapandı, LTC aynı mumda (2023-07-13 08:00) girdi, açık işlem sayısı 3'te kaldı.
  - Mekanik deneme (sadece kontrol amaçlı, aday değil, repoya konmadı): eşikler gevşetilmiş kopya (1 gün, her R), eski 16, 2020-2021. 82 değişim oldu. 82'sinin hepsinde işlem o mumun açılışında kapandı ve aynı mumda bir aday için giriş emri verildi. Bunların 75'i doldu, 7 limit emir süresi içinde dolmadı. Aynı anda en fazla 3 işlem vardı.
- İlk çalıştırmada bir hata vardı: Freqtrade backtestte aynı işlem için farklı Python nesneleri veriyor, nesne kimliğiyle karşılaştırma hiç eşleşmedi ve 0 değişim çıktı. Karşılaştırma coin + açılış zamanı + işlem no ile düzeltildi, iki liste yeniden çalıştırıldı. Birim testine bu durum eklendi.

## Sonuç (2020-03 → 2026-09, sadece long, en fazla 3 işlem, %1 risk)
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | Hesap-R ort. / toplam | Net | Max DD | PF | Kazanma | Funding (USDT) | Al-tut |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Eski 16 | temel | 230 | +1.35R | 311.26 | +1.34 / 308.7 | +%827.3 | %23.75 | 2.06 | %32.2 | -14077 | +%931.5 |
| Eski 16 | yer değişimi | 231 | **+1.34R** | **310.37** | +1.33 / 307.8 | **+%819.4** | %23.74 | 2.05 | %32.0 | -14001 | +%931.5 |
| Yeni 20 | temel | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | +%194.7 |
| Yeni 20 | yer değişimi | 193 | +0.61R | 117.72 | +0.60 / 115.8 | +%134.2 | %22.61 | 1.53 | %23.3 | -3769 | +%194.7 |

- Temel rakamları önceki turlarla birebir aynı (230 / 193 işlem; 311.26R / 117.72R).
- Hesap-R = kâr / (işlem açılırken kapanmış işlemlerle hesaplanan sermayenin %1'i). Max DD Freqtrade'in hesap düşüşü.
- Al-tut: eşit ağırlık, aynı dönem.

**Karar: red.** Eski 16'da ortalama R (+1.353 → +1.344), toplam R (311.26 → 310.37) ve net (+%827.3 → +%819.4) kötü. Yeni 20'de hiçbir şey değişmedi; kural "iki listede de daha iyi" istiyor.

## Değişimler
| Liste | Değişim | Kapatılan işlem | Anlık R (karar) | Kapanış R (değişimde) | Temelde aynı işlem | Yerine giren | Yerine girenin R'si |
|---|---|---|---|---|---|---|---|
| Eski 16 | 2023-07-13 08:00 | BTC, açılış 2023-06-23 16:00 (19.7 gün) | -0.47 | **-0.59** | -0.73 (2023-07-18 EMA20 çıkışı) | LTC 2023-07-13 08:00 (tek aday) | **-1.04** (2023-07-14 stop) |
| Yeni 20 | yok | — | — | — | — | — | — |

- Kapatılan işlemler toplam: değişimde -0.59R, temelde -0.73R (**+0.14R** kazanç).
- Yerine girenler toplam: **-1.04R** (1 işlem, temelde yok).
- Net etki: eski 16 -0.89R. Ortak 230 işlemin R'si 311.26 → 311.41 (sadece BTC farkı); başka bir işlem kaymadı. LTC stop olunca (07-14) yeni sürümde bir yer boşaldı, temelde BTC çıkınca (07-18) boşaldı; ama iki sürümde de bir sonraki giriş 2023-07-29'daki DOGE oldu, arada yeni sinyal girmedi.
- Kapanış R'si karar anındaki R'den kötü (-0.47 → -0.59), çünkü masraf ve funding dahil ve çıkış bir sonraki mumun açılışından.

## Neden bu kadar az? (teşhis, kural değişikliği yok)
Temel ile aynı davranan bir teşhis kopyası (hiç işlem kapatmıyor, sadece kaydediyor) bütün dönemde her "3 yer dolu + yeni geçerli sinyal" anını kaydetti:

| Liste | Dolu yer + yeni sinyal anı (4h mum) | Bu anlarda açık işlem | ≥ 10 gün açık | ≥ 10 gün ve +0.5R altında | ≥ 10 gün ve 0R altında (uygun) | 10 günden yaşlı işlemlerin en düşük R'si |
|---|---|---|---|---|---|---|
| Eski 16 | 455 | 1365 | 642 | 10 (%1.6) | 2 (aynı BTC işlemi, 2 mum) | -0.47 |
| Yeni 20 | 242 | 726 | 234 | 3 (%1.3) | 0 | +0.16 |

- Bu anlarda zararda olan açık işlemler genç: yaşlarının ortası 52 saat (16) / 50 saat (20). %90'ı 7.4 / 6.1 günden genç.
- Temelin tüm işlemlerinden 88 / 48'i 10 günden uzun sürdü. Bunlardan 19 / 5'i 10. günden sonra bir 4h kapanışta 0R'nin altına indi, ama bu anlar sadece bir kez (BTC 2023-07) "dolu yer + yeni sinyal" ile çakıştı. Örnek: 2025-09-11'de DOT, DOGE ve BTC üçü birden 10 günden yaşlı ve zarardaydı, ama o sırada yeni sinyal yoktu (zayıf piyasa).
- Yani 10 gün + 0R eşiği, EMA20 çıkışının zaten yaptığı işi tekrar ediyor. Zararda işlem günlük kapanış EMA20 altına inince çıkıyor; 10 gün sonra hâlâ açık olan işlem neredeyse her zaman trendin içinde ve kârda.

## Yıllara göre (R; parantezde işlem sayısı)
| Yıl | Eski 16 temel | Eski 16 yer değişimi | Yeni 20 temel | Yeni 20 yer değişimi |
|---|---|---|---|---|
| 2020 | +44.4 (46) | +44.4 (46) | +31.5 (29) | +31.5 (29) |
| 2021 | +164.3 (32) | +164.3 (32) | +41.7 (27) | +41.7 (27) |
| 2022 | -6.6 (7) | -6.6 (7) | -3.0 (6) | -3.0 (6) |
| 2023 | +86.7 (38) | +85.8 (39) | -1.9 (39) | -1.9 (39) |
| 2024 | +10.0 (57) | +10.0 (57) | +64.9 (36) | +64.9 (36) |
| 2025 | +15.5 (31) | +15.5 (31) | -19.8 (41) | -19.8 (41) |
| 2026 | -3.1 (19) | -3.1 (19) | +4.3 (15) | +4.3 (15) |

## Yoğunlaşma (tek işlem, hesap-R)
- Eski 16: en büyük işlem iki sürümde de ETC 2021-03-30 +93.1. En büyük hariç ortalama +0.941 → +0.933, en büyük 5 hariç +0.277 → +0.272.
- Yeni 20: aynı (ALGO 2024-11-08 +33.9; en büyük hariç +0.426, en büyük 5 hariç -0.078).
- Fark tek bir küçük işlemden (LTC -1.04R); sonuç hiçbir büyük işleme bağlı değil.

## İleriye bakma kontrolü
- Karar sadece az önce kapanmış 4h mumun kaydına bakar (sinyal mumu = mevcut mum başı − 4 saat). Daha yeni bir tarih hiç okunmaz. Kayıttaki giriş ve çıkış sinyalleri temelin kendi sinyalleri. Anlık R o mumun kapanışından, stop işlem açılırken sabitlenen plandan.
- Birim testi (`tests/test_pusula.py`, `test_v2_no_be_slot_swap_closes_worst_old_losing_trade_only_when_slots_are_full`) şunları doğruluyor:
  - en kötü R'li uygun işlem seçiliyor; 10 günden genç işlem (5 gün, -2R) ve 59 mumluk işlem seçilmiyor;
  - 0R ve üstündeki işlem seçilmiyor;
  - değişim sadece mumun ilk saatinde ve mum başına bir kez oluyor;
  - boş yer varsa ya da bir işlem kendi çıkış sinyaliyle zaten çıkıyorsa değişim yok; sinyal yoksa değişim yok;
  - gelecekteki bir sinyal görülmüyor;
  - Freqtrade'in aynı işlem için verdiği farklı nesne de eşleşiyor;
  - stop ve giriş metodları temelinkiyle aynı.
- Veri kesme testi: her listede değişim anları + 300 rastgele an (yarısı gerçek sinyal mumundan hemen sonra). Her anda her coin için stratejinin kendi `populate_indicators` + giriş + çıkış kodu iki kez çalıştırıldı: tam veriyle ve o anda kesilmiş veriyle (4h mumlar o ana kadar kapanmış olanlar, günlük mumlar kapanışı o ana kadar olanlar). Kararın okuduğu üç bilgi (geçerli sinyal, çıkış sinyali, kapanış) karşılaştırıldı. Eski 16: 298 an (değişim anı dahil), 4768 coin-an kontrolü. Yeni 20: 299 an, 5980 kontrol. Sonuç: **0 fark.** Eski 16'da ilk çalıştırmada 1 fark çıktı (AVAX 2020-09-24, listelenmesinin ertesi günü). Sebebi test betiğinin kısayoluydu (30 mumdan az veride hesap yapılmıyordu); kısayol olmadan iki taraf birebir aynı.

## Ayarlar (önceki turlarla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, `--max-open-trades 3`, sadece long, işlem başına %1 risk.
- Listeler: `config/pairs_wide16.json`, `config/pairs_new20.json`.
- Komut: `PUSULA_SWAP_LOG=<dosya> FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeSlotSwap --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/slotswap_<liste>`. Rapor `scripts/make_report.py --results <zip> --test yer_degisimi --out results/2026-10-30_pusula_yer_degisimi/<liste>`.
- Ayrıntılı raporlar (funding, çıkış türleri, coin tablosu, grafikler): `wide16/rapor.md`, `new20/rapor.md`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. Kaldıraç en fazla 3x.
- Not: dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
