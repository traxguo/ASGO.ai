# Kuyruk 6 — aynı coinde yeniden giriş — 2026-10-17 (temel: PusulaV2NoBe)

## GUO'ya not
- Kuyruktaki fikir: "aynı coinde trend sürerken ikinci kırılımda yeniden gir." Kodu okuyunca gördüm ki temel sürüm (`PusulaV2NoBe`) **bunu zaten yapıyor**: bir işlem stopta ya da çıkış kuralıyla kapanınca, aynı coinde bir sonraki yeni 4 saatlik kırılımda (bütün giriş şartları yine sağlanıyorsa) tekrar giriyor. Bekleme süresi ya da "trend başına bir işlem" sınırı yok. Açık işlem varken aynı coine ekleme yapmıyor.
- Bu yüzden "yeniden giriş ekle" testi temelle aynı olurdu. Bunun yerine tersini test ettim: **yeniden girişi kaldırmak** (`PusulaV2NoBeNoReentry`, her coinde günlük trend başına en fazla bir işlem). Yani bu tur aslında bir çıkarma testi: yeniden girişler işe yarıyor mu?
- Sonuç: yeniden girişleri kaldırmak **iki listede de kötü**. Eski 16: +1.35R → +1.03R, toplam 311.3R → 199.2R. Yeni 20: +0.61R → +0.55R, toplam 117.7R → 89.6R.
- Karar: **red**. Yeniden giriş kalıyor, temel `PusulaV2NoBe` değişmedi. Yeniden girişler ortalamada ilk girişlerden daha iyi (eski 16: +2.50R'ye karşı +0.53R; yeni 20: +0.95R'ye karşı +0.51R), ama bu fark birkaç büyük işleme bağlı (aşağıda).

## Kural (testten önce yazıldı)
Temelin bugünkü davranışı (kod: `strategies/candidates/pusula.py`, `ManagedStrategy.populate_entry_trend` + `PusulaBase.signal_conditions`):
- Giriş sinyali her 4 saatlik mumda yeniden hesaplanıyor: günlük puan ≥ +1, günlük kapanış EMA20 üstünde, ve `first_true(close > önceki 20 mumun tepesi)`, yani kapanış kanalın üstüne **yeni** çıkıyor (önceki mum üstünde değildi). Aynı mumda çıkış sinyali varsa Freqtrade girmiyor.
- İşlem açıkken aynı coinde ikinci işlem açılmıyor (Freqtrade coin başına tek işlem), `adjust_trade_position` hiçbir emir vermiyor (pozisyon büyütme yok).
- İşlem kapanınca hiçbir kilit yok (bekleme/koruma ayarı yok): bir sonraki yeni kırılım mumu yeni işlem açar. İstenen "çıkıştan sonra ilk yeni kırılımda, rejim hâlâ long iken yeniden gir" kuralı bu yüzden temelle aynı.

Test edilen farklı sürüm, `PusulaV2NoBeNoReentry(PusulaV2NoBe)`:
- Bir "trend" = coinin son kapanmış günlük puanının kesintisiz ≥ +1 kaldığı dönem.
- Bir coinde işlem kapandıktan sonra, aynı trend içinde o coinde yeni long **açılmaz**. Puan en az bir kez +1'in altına (yani -1 veya -3'e) inip yeni bir trend başlayınca giriş yine serbest.
- Başka hiçbir şey değişmedi (giriş şartları, stop, EMA20 ve BTC çıkışları aynı). Uygulama: `confirm_trade_entry` coinin son kapanan işlemine bakar; o işlemin sinyalinden bu yana kapanan günlük mumlarda puan hiç +1'in altına inmediyse girişi reddeder.
- Uygulama notu: ilk denemede kontrol 4 saatlik analiz tablosundan yapılıyordu; backtestte bu tablo sadece son 1000 mumu (~166 gün) tuttuğu için çok uzun trendlerde 5 işlem kuraldan kaçtı (eski 16). Kontrol günlük veriye taşındı, test baştan koşuldu; aşağıdaki rakamlar düzeltilmiş sürümden. Kontrol: düzeltilmiş sürümde aynı trend içinde ikinci işlem sayısı **0** (iki listede de).

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBe (temel) | 230 | +1.35R | 311.26 | 2.06 | %23.7 | +%827.3 |
| Eski 16 | Trend başına tek işlem | 194 | **+1.03R** | **199.23** | 2.02 | %17.1 | +%308.5 |
| Yeni 20 | PusulaV2NoBe (temel) | 193 | +0.61R | 117.72 | 1.53 | %22.6 | +%134.2 |
| Yeni 20 | Trend başına tek işlem | 164 | **+0.55R** | **89.56** | 1.47 | %23.4 | +%86.5 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6). İki sürüm de getiride al-tutun altında, düşüşte çok daha iyi.
Çıkış türleri: eski 16 stop %41.7 → %52.6; yeni 20 stop %53.9 → %58.5. Funding (USDT): eski 16 -14.1k → -4.6k, yeni 20 -3.8k → -2.7k (daha az ve daha kısa işlem).
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: red.** Kabul kuralı iki listede de daha iyi ortalama R ve toplam R istiyor; ikisinde de ikisi düştü. DD eski 16'da iyileşti (%23.7 → %17.1), yeni 20'de biraz kötüleşti (%22.6 → %23.4, sınır %25 içinde). Yeniden giriş kuralı temelde kalıyor.

## Temelde yeniden girişler ne getiriyor
Temelin işlemleri "aynı trendde coinin ikinci (veya sonraki) işlemi" ve "trendin ilk işlemi" diye ayrıldı (sinyal anında bilinen son günlük puana göre):
| Liste | Yeniden giriş | Ortalama | Toplam | Trendin ilk işlemi | Ortalama |
|---|---|---|---|---|---|
| Eski 16 | 96 işlem | +2.50R | +240.4R | 134 işlem | +0.53R |
| Yeni 20 | 44 işlem | +0.95R | +41.7R | 149 işlem | +0.51R |

- Eski 16: yeniden girişlerin 40/96'sı kârlı. En büyüğü ETC 2021-03-30 → 2021-05-15 **+94.1R** (temelin en büyük işlemi), sonra BNB 2021-01 +53.0R, BTC 2024-01 +20.8R. En büyük 1 işlem hariç +146.3R, en büyük 3 hariç +72.5R. Yani tek işlem çıkınca da artıda.
- Yeni 20: 14/44 kârlı. En büyüğü THETA 2020-12 +24.1R, sonra NEO 2021-03 +9.7R, IOTA 2020-07 +7.9R. En büyük 1 hariç +17.7R, **en büyük 3 hariç +0.1R**. Yani yeni 20'de yeniden girişlerin artısı üç işleme bağlı; geri kalanı başa baş.
- Mantık: trendin ilk kırılımı çoğu zaman sahte çıkıyor ve stopta bitiyor; trend gerçekten başlamışsa ikinci kırılım büyük hareketin içinde oluyor.

## Coin bazında dağılım
Coin bazında toplam R farkı (yeni − temel):
- Eski 16: 5 coin daha iyi, 11 coin daha kötü. Toplam fark -112.0R. En kötü: ETC **-98.6R** (tek ETC 2021 yeniden giriş işlemi kayboldu), TRX -34.7R, BTC -34.1R, BNB -32.1R, ETH -22.0R. En iyi: DOGE **+101.7R** (boşalan kasa yeriyle açılan yeni işlemler; çoğu tek DOGE 2024-10-14 işlemi +66.5R), XRP +15.7R, AVAX +12.6R. ETC ve DOGE ikisi birden hariç fark yine -115.1R; yani sonuç tek işleme bağlı değil, 11 coinde kötüleşme var.
- Yeni 20: 5 coin daha iyi, 11 coin daha kötü, 4 coin aynı. Toplam fark -28.2R. En kötü: THETA -23.0R (2020-12 yeniden giriş işlemi), NEO -10.2R, VET -7.7R, IOTA -7.4R. En iyi: NEAR +17.0R, FIL +8.8R, AAVE +5.2R. THETA hariç fark -5.1R; yani yeni 20'deki fark büyük ölçüde tek THETA işleminden.
- Temelden düşen işlemler: eski 16'da 110 (96'sı yeniden giriş, toplam +228.9R); yeni sürümde boşalan yerle açılan 74 yeni işlem +116.9R. Yeni 20'de 46 işlem düştü (44'ü yeniden giriş, +41.9R), 17 yeni işlem +13.8R.
- Her sürümün kendi en büyük tek işlemi çıkarılınca: eski 16'da temel 217.2R (ETC hariç), yeni 132.7R (DOGE hariç); yeni 20'de temel 83.2R, yeni 55.1R (ikisinde de en büyük ALGO 2024-11 +34.5R, aynı işlem).
- Yıllara göre (yeni − temel): eski 16'da 2021 **-164.2R**, 2024 +70.0R (DOGE), 2025 -17.1R, diğer yıllar ≈0; yeni 20'de 2020 -30.5R (THETA, IOTA), 2021 -9.1R, 2023 +7.8R, 2024 +9.3R, 2026 -5.2R.
- Yorum: yeniden girişler en çok güçlü boğa yıllarında (2020-2021) para kazandırıyor. Yeni 20'de bu kazanç birkaç işleme bağlı; ama kaldırınca iki listede de toplam ve ortalama düşüyor. Kural kalıyor.

## Ayarlar (çıkarma turlarıyla aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaV2NoBeNoReentry --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --backtest-directory user_data/backtest_results/reentry_<liste>`, rapor `scripts/make_report.py --test yeniden_giris`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2NoBe) rakamları önceki turlarla birebir aynı (230 / 193 işlem, 311.26R / 117.72R, DD %23.7 / %22.6).
- Not: bu dönem doğrulama ve kasa aralığını da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.
