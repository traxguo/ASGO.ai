# pusula — Claude'un ana stratejisi: günlük rejim + 4 saatlik kırılım

Kod: [`strategies/candidates/pusula.py`](../strategies/candidates/pusula.py)

## Hipotez
Bugüne kadarki tek gerçek artı, günlük trend yönünde 4 saatlik kırılımdı (long tarafı). Short'lar zayıf düşüşleri gerçek düşüş sandığı için kaybetti. Pusula trendi üç ayrı ölçüyle sorar ve sadece üçü de aynı yönü gösterirken, Bitcoin de aynı taraftayken işlem açar. Kararsız piyasada işlem açmaz, sadece yorum yapar. Bu yüzden her coin için her an bir görüş verebilir.

## Yön
ikisi de

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Puan = üç işaretin toplamı (-3 ile +3 arası).
- [a] Kapanış EMA(50)'nin üstünde (+1) / altında (-1) | "Fiyat ({close_1d}) 50 günlük ortalamanın ({ema_slow_1d}) üstünde/altında."
- [b] EMA(20) EMA(50)'nin üstünde (+1) / altında (-1) | "Kısa vadeli ortalama uzun vadelinin üstünde/altında."
- [c] 90 günlük getiri artı (+1) / eksi (-1) | "Fiyat 90 gün öncesine göre %{mom_1d} değişti."
- +3 = güçlü yükseliş, -3 = güçlü düşüş, diğerleri = kararsız.

## Giriş koşulları (4h)
Long (hepsi):
- [regime_up] Teknik: coinin puanı = +3 | Açıklama: "Günlük trend güçlü yukarı (3/3)."
- [market_up] Teknik: BTC'nin puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [breakout_up] Teknik: 4h kapanış önceki 20 mumun tepesinin üstünde, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun tepesini ({dc_upper}) kırdı."

Short (hepsi):
- [regime_down] Teknik: coinin puanı = -3 | Açıklama: "Günlük trend güçlü aşağı (3/3)."
- [market_down] Teknik: BTC'nin puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [breakout_down] Teknik: 4h kapanış önceki 20 mumun dibinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun dibini ({dc_lower}) kırdı."

Kararsız rejimde işlem yok.

## İşlem yönetimi
Ortak modülden (`strategies/common/`): giriş bölgesi 0.25 ATR, stop 1.5 ATR veya son 10 mumun dip/tepesi (uzak olan), Model B (TP1 2R'de yarısı + BE, TP2 4R), 3 mum geçerlilik, en fazla 3x, işlem başı %1 risk.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 4h | sabit |
| Rejim zaman dilimi | 1d | sabit |
| EMA hızlı / yavaş | 20 / 50 | 15-25 / 40-60 |
| Momentum | 90 gün | 60-120 |
| Kanal | 20 mum | 15-30 |
| Piyasa filtresi | BTC puanı ≥ +1 / ≤ -1 | sabit |

## Varyantlar (önceden belirlendi)
- `Pusula_B`: ana strateji, karar buna göre verilir.
- `PusulaNoBTC_B`: Bitcoin filtresi olmadan, sadece filtrenin katkısını görmek için.

## 2. tur (2026-10-09, test öncesi yazıldı; proje sahibi "teste devam, açıkları kapat" dedi)
İlk turda iki açık vardı: düşüş %35 (sınır %25) ve kârın tek yıla (2020) bağlı olması. Kazananlar ortalama 13 gün sürüyordu, sabit 2R/4R hedef trendi erken kesiyor olabilir.

`PusulaTrend` (ana karar buna göre):
- Girişler aynı + [daily_above_ema20] long için son günlük kapanış EMA(20) üstünde / [daily_below_ema20] short için altında (çıkış kuralı zaten doğruyken işleme girmemek için).
- **Sabit TP yok.** Çıkış: son kapanmış günlük mum EMA(20)'nin altında kapanırsa long kapanır (short için üstünde). Açıklama: "Günlük trend bozuldu (kapanış {close_1d}, EMA20 {ema_fast_1d} altında), işlem kapatılıyor."
- Stop aynı (1.5 ATR / son 10 mum). Fiyat 2R lehimize gidince stop girişe çekilir.
- Aynı anda en fazla **3 açık işlem** (önceden 5). Coinler birlikte hareket ettiği için aynı yöndeki çok sayıda işlem düşüşü büyütüyordu.
- Brief 7.5: "takip eden stop gibi alternatif kurallar test edilebilir, testten geçmeden kullanılmaz." Bu o testtir.

Karşılaştırma (sadece etkileri ayırmak için): `Pusula_B` en fazla 3 işlemle (sadece işlem sınırının etkisi) ve `PusulaTrend` en fazla 5 işlemle (sadece çıkışın etkisi).

Geçme şartı (değişmedi): maliyet ve funding sonrası > 0R, düşüş ≤ %25, en az 100 işlem, coinlerin en az yarısı pozitif. Geçerse doğrulama verisinde bir kez kontrol.

## 3. tur (2026-10-09): ters köşeden açık arama
Proje sahibi: "her defasında açık bularak geliştir, farklı açılardan vur." Kurallar değiştirilmeden önce açıklar ölçüldü:
- **Şans testi** (`research/robustness/pusula_trade_anatomy.py`): 6 coinde en iyi 5 işlem toplam kârdan büyük; tek BNB işlemi +53R. En iyi 10 işlem çıkarılınca -42.8R.
- **Geri verilen kâr:** trend çıkışında ortalama 6.7R açık kârın 3.7R'si geri veriliyor.

Denenen çözümler (geliştirme verisi, sonra yeni coinler):
| Deneme | Sınıf | Geliştirme (6 coin) | 10 yeni coin | Karar |
|---|---|---|---|---|
| 2026-10-16 | Kuyruk 3 (teşhis): batmış/çıkarılmış 12 coin (LUNA, FTT, SRM, HNT, BTS, TOMO, BTT, BZRX, KEEP, YFII, WAVES, AUDIO; liste testten önce sabit), 2020-01 → 2026-09 | Batmış 12: V2NoBe 47 işlem -0.02R, PF 0.96, DD %12.1 (HNT tek işlem +11.5R hariç -0.27R); TrendLong 38 işlem -0.79R, DD %25.7. LUNA/FTT çöküşünde açık işlem yok, delistte açık kalan yok. Eski 16 + batmış 12: V2NoBe +1.35→+1.22R, TrendLong +0.95→+0.84R. Bugünkü listeden seçim ortalama R'yi ~%10-20 iyimser gösteriyor. Kural değişmedi. | `results/2026-10-16_pusula_batik_coinler/rapor.md` |
| Ana sürüm | `PusulaTrendLong` | +0.83R, DD %20.2 | **+1.05R, PF 2.38, DD %15.1** | Devam |
| İki vitesli çıkış (4R sonrası 4h kanal) | `PusulaTrendLong2` | +0.69R, DD %20.9 | — | Elendi |
| Kapanıştan giriş | `PusulaTrendLongClose` | +1.44R (tek DOGE işlemi +79R) | +0.92R | Elendi |
| 1R'de BE | `PusulaTrendLongBE1` | +0.83R, DD %17.0 | +0.41R | Elendi |
| Long + short | `PusulaTrend` | +0.43R, DD %31.0 | +0.49R, DD %20.0, short -0.05R | Short avantajı yok |
| 16 coin birlikte, en fazla 3 işlem | `PusulaTrendLong` | — | 2020-01 → 2026-03: +1.02R, DD %26.1, en iyi 10 hariç ≈ 0R | Geniş liste daha sağlıklı |

## 4. tur (2026-10-09): stres testleri
16 coin, 2020-01 → 2026-03, en fazla 3 işlem. Rapor: [tur4_stres](../results/2026-10-09_pusula_tur4_stres/rapor.md).
- Maliyet x2, 1 mum geç giriş, en kârlı coinleri çıkarma (tek tek ve üçü birden), 1h grafik: hepsinde artıda.
- Açık: en uzun kayıp serisi 26 işlem (2024-03 → 2025-07), DD %26.
- `PusulaTrendLongStrictBTC` (BTC puanı +3 şartı): toplam R aynı, DD bir listede iyi bir listede kötü; eklenmedi.

## Kasa testi planı (2026-10-10, test öncesi yazıldı)
Proje sahibi "devam" dedi; önerilen "sadece long" seçeneğiyle ilerleniyor.
- **Ana karar:** `PusulaTrendLong`, 16 coin (`config/pairs_wide16.json`), en fazla 3 işlem, 4h + 1h detay, 2026-04-01 → 2026-09-30. Ayarlar 4. turdaki haliyle, hiçbir değişiklik yok.
- **Geçme şartı:** maliyet ve funding sonrası ortalama > 0R ve düşüş ≤ %25. 6 ayda işlem sayısı az olacağı için (tahmini 10-20) "en az 100 işlem" şartı burada uygulanamaz; sonuç küçük örnek olarak yorumlanır.
- **Sadece bilgi için, aynı tek kullanımda:** `PusulaTrend` (long+short, 16 coin) ve `PusulaTrendLong` (6 coin). Karar bunlara göre verilmez.
- Kasa sonucu ne olursa olsun kurallar bu veriye göre değiştirilmez.

## Durum: candidate
- `Pusula_B` (sabit TP): geçemedi.
- `PusulaTrend` (long+short): doğrulamayı geçti, geliştirmede DD %31 > %25.
- `PusulaTrendLong`: iki dönemde de eşikleri geçti ve hiç görmediği 10 coinde de artıda (+1.05R). **Kasa testi (2026-04 → 2026-09, 16 coin): -0.02R, DD %6.2, 15 işlem, kıl payı geçemedi.** Active olamaz; emekli de edilmedi. Sonraki sınav yeni veri (dry-run kâğıt testi), proje sahibinin kararı bekleniyor.
- `PusulaTrendLong2`, `PusulaTrendLongClose`, `PusulaTrendLongBE1`: 3. turda elendi.
- **PusulaV2'nin bir sonraki sürümü BTC giriş filtresini (`market_up`) çıkarmalı** (çıkarma turu 1 kabul). Bunu yaparken `scripts/bitget_demo.py` aynı mumda `exit_long` varsa girmemeli (Freqtrade böyle davranıyor). PusulaV2'nin kendisi değişmedi; karar ana oturumda.
- Çıkarma turları sonrası araştırma temeli: `PusulaV2NoBe` (BTC giriş filtresi yok, long puanı ≥ +1, 2R'de başabaş yok; turlar 1-3 kabul, 4 (EMA50) ve 5 (BTC-dönüş çıkışını kaldırma) red; çıkarma listesi bitti). Temel aynı coinde çıkıştan sonra her yeni kırılımda tekrar girer; bu yeniden girişi kaldırmak (kuyruk 6, 2026-10-17) red. Çakışan sinyallerde 90 günlük getiriye göre coin seçimi (kuyruk 7, 2026-10-18) red. Rejimi haftalık grafikten okumak (kuyruk 10, 2026-10-19) red. PusulaV2 demo sürümü değişmedi; karar ana oturumda.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-23 | Kuyruk 14, çıkarma: stop sadece giriş ortası − 1.5 ATR (10 mum dibi kısmı kaldırıldı, `PusulaV2NoBeAtrStop`, temel PusulaV2NoBe) | **Red**: stop ort. %5.4→%3.5 (16), %6.3→%4.6 (20). 16: 230→371 işlem, +1.35→+1.53R, hesap-R +1.34→+1.54, net +%827→+%3266, DD %23.7→%43.8; 20: 193→412 işlem, +0.61→+0.72R, hesap-R +0.60→+0.74, net +%134→+%423, DD %22.6→%68.3. Stopla biten %42→%74 / %54→%79, kayıp serisi 52 / 36 işlem. Getiri yüksek riskle; dip stopu kalıyor. | `results/2026-10-23_pusula_atr_stop/rapor.md` |
| 2026-10-24 | Kuyruk 15, ekleme: long girişine trend yaşı ≥ 11 gün şartı (günlük puan en az 11 kapanmış gündür ≥ +1, `PusulaV2NoBeMature`, temel PusulaV2NoBe) | **Red**: 16: 230→200 işlem, +1.35→+1.57R, toplam 311.3→315.0R, net +%827→+%892, DD %23.7→%20.1; 20: 193→130 işlem, +0.61→+0.62R, toplam 117.7→80.3R, net +%134→+%90, DD %22.6→%23.2; batmış 12: -0.02→-0.42R. Atlanan genç trend işlemleri toplamda artıdaydı, boşalan yerlere girenler 20'de -17.5R. Fikir aynı işlemlerden (geriye dönük bakış). | `results/2026-10-24_pusula_olgun_trend/rapor.md` |
| 2026-10-25 | Kuyruk 16, risk: hesap düşüş freni (kapanmış bakiye zirveden ≥ %15 aşağıdayken işlem riski %0.5, değilse %1, `PusulaV2NoBeDdBrake`, temel PusulaV2NoBe) | **Red**: aynı işlemler; 16: 85 giriş %0.5, net +%827→+%583, DD %23.7→%19.7, net/DD 34.8→29.6, su altı 925→967 gün; 20: 78 giriş %0.5, net +%134→+%71, DD %22.6→%21.6, net/DD 5.9→3.3, su altı 1057→1334 gün. Frenli girişler +99R / +91R; fren toparlanmayı yavaşlattı. | `results/2026-10-25_pusula_dd_fren/rapor.md` |
| 2026-10-26 | Kuyruk 17, ekleme: long girişine funding şartı (son 3 günlük yıllık funding ≤ %50, sadece girişten önce ödenmiş oranlar, 8h/4h aralığa göre; `PusulaV2NoBeFunding`, temel PusulaV2NoBe) | **Red**: 16: 230→220 işlem, +1.35→+1.42R, 311.3→313.0R, net +%827→+%844, DD %23.7 aynı; 20: 193→189, +0.61→+0.59R, 117.7→111.7R, net +%134→+%122, DD %22.6 aynı. Engellenen 12 / 5 giriş (hepsi 2020-05 → 2021-05): -3.9R / +5.5R. Funding -14077→-13817 / -3769→-3217 USDT. | `results/2026-10-26_pusula_funding_filtre/rapor.md` |
| 2026-10-27 | Kuyruk 18, ekleme: long kırılım mumu güçlü kapansın (`(close - low) / (high - low) ≥ 2/3` sinyal mumunda, `high == low` ise yok; `PusulaV2NoBeStrongClose`, temel PusulaV2NoBe) | **Red**: 16: 230→224 işlem, +1.35→+1.18R, 311.3→264.0R, net +%827→+%584, DD %23.7→%22.7; 20: 193→180, +0.61→+0.30R, 117.7→54.2R, net +%134→+%42, DD %22.6→%20.1. Engellenen 46 / 42 zayıf kapanışlı giriş +65.9R / +60.8R (ort. +1.43 / +1.45R; güçlü kapananlar +1.33 / +0.38R): BTC 2023-10, BTC 2024-01, FIL 2021-03, THETA 2020-12 kesildi. | `results/2026-10-27_pusula_guclu_kapanis/rapor.md` |
| 2026-10-28 | Kuyruk 19, ekleme: piyasa genişliği (aktif listedeki coinlerin en az %50'sinin son kapanmış günlük puanı ≥ +1; puanı olmayan coin sayılmaz; `PusulaV2NoBeBreadth`, temel PusulaV2NoBe) | **Red**: 16: 230→208 işlem, +1.35→+1.08R, 311.3→224.6R, net +%827→+%399, DD %23.7→%28.9 (> %25); 20: 193→146, +0.61→+1.06R, 117.7→155.1R, net +%134→+%240, DD %22.6→%16.9. Kapı zamanın %55 / %64'ünde kapalı. Engellenen 70 / 70 giriş +99.7R / +39.3R (SOL 2023-10 +58.6, BTC 2023-10 +22.6, ALGO 2024-11 +34.5, UNI 2024-02 +26.1); yeni 20'deki kazanç boşalan yerlere aynı yükselişte girenlerden (+96.2R). | `results/2026-10-28_pusula_piyasa_genisligi/rapor.md` |
| 2026-10-29 | Kuyruk 20, çıkarma: long girişinden coinin günlük puan ≥ +1 şartı kaldırıldı (kalan: 4h ilk kırılım + günlük kapanış EMA20 üstü; BTC-dönüş çıkışı BTC puanıyla aynı; `PusulaV2NoBeNoScore`, temel PusulaV2NoBe) | **Red**: 16: 230→255 işlem, +1.35→+1.53R, 311.3→388.9R, net +%827→+%1696, DD %23.7→%25.5 (> %25); 20: 193→246, +0.61→+0.57R, 117.7→139.8R, net +%134→+%192, DD %22.6→%23.8. Puan < +1 yeni girişler 64 / 120 işlem +68.5R / +86.7R, ama XLM 2024-11 +43.1, BCH 2023-06 +18.4, HBAR 2024-11 +50.3 hariç küçük; yeni 20'de yer kaybeden ALGO 2024-11 +34.5, UNI 2024-02 +26.1. 2022 kötüleşmedi (BTC kuralı engelliyor). | `results/2026-10-29_pusula_puansiz/rapor.md` |
| 2026-10-30 | Kuyruk 21, yer yönetimi: 3 yer doluyken yeni geçerli sinyal gelirse, ≥ 10 gün (60 mum) açık ve anlık R < 0 olan en kötü işlem o mumda kapanır, yeni sinyal girer; mum başına en fazla bir (`PusulaV2NoBeSlotSwap`, temel PusulaV2NoBe) | **Red**: 6.5 yılda eski 16'da tek değişim (BTC 2023-07-13 -0.59R kapandı, temelde -0.73R; yerine LTC -1.04R stop), yeni 20'de hiç yok. 16: 230→231 işlem, +1.35→+1.34R, 311.26→310.37R, net +%827.3→+%819.4, DD %23.75→%23.74; 20: birebir aynı (193, 117.72R, +%134.2, DD %22.61). EMA20 çıkışı zarardaki işlemleri zaten çabuk kesiyor: dolu yer + sinyal anlarında 10 günden yaşlı işlemlerin %98'i +0.5R üstünde. | `results/2026-10-30_pusula_yer_degisimi/rapor.md` |
| 2026-10-22 | Kuyruk 13, teşhis (kural değişikliği yok): temel işlemleri giriş anındaki günlük trend yaşına göre (puan kaç kapanmış gündür ≥ +1: 0-10, 11-30, 31-90, 90+) | 0-10 gün iki listede de en zayıf: 16: 87 işlem +0.25R (en iyi hariç -0.01R), 20: 93 işlem +0.23R (-0.15R); >10 gün 16: +2.02R, 20: +0.97R. Diğer gruplar listeye göre değişiyor, tutarlı iyi grup yok. Fikir: trend yaşı ≥ 11 gün şartı (kuyruk 15, test edilmedi). | `results/2026-10-22_pusula_trend_yasi/rapor.md` |
| 2026-10-21 | Kuyruk 12, çıkarma: 4h kırılım tetiği kaldırıldı; günlük puan ≥ +1 ve günlük kapanış EMA20 üstü olan her 4h mumda giriş (coinde açık işlem yoksa), stop ve çıkışlar aynı (`PusulaV2NoBeNoBreakout`, temel PusulaV2NoBe) | **Red**: 16: 230→654 işlem, +1.35→-0.78R (stop dibinde yeniden açılan 19 işlem hariç +0.30R), net +%827→+%177, DD %23.7→%48.6; 20: 193→737 işlem, +0.61→-0.23R (20 işlem hariç +0.06R), net +%134→-%9, DD %22.6→%82.9. Kalan kâr tek işlemlerde (SOL 2023-10, UNI 2020-12). Kârı kırılım getiriyor, kural kalıyor. | `results/2026-10-21_pusula_kirilimsiz/rapor.md` |
| 2026-10-20 | Kuyruk 11, 5 yer küçük risk: en fazla 5 işlem, işlem başına %0.6 risk (temel 3 işlem × %1; toplam açık risk aynı %3) (`PusulaV2NoBe5`, temel PusulaV2NoBe) | **Red**: 16: 230→354 işlem, +1.35→+1.20R, net +%827→+%621, DD %23.7→%22.1; 20: 193→264 işlem, +0.61→+0.60R, net +%134→+%105, DD %22.6→%21.4. Coin sırası farkı (normal − ters, toplam R) 16'da 60.1→10.0R, 20'de 4.9→23.1R. Ek işlemler artıda ama hepsinin küçülmesini karşılamıyor. | `results/2026-10-20_pusula_5yuva/rapor.md` |
| 2026-10-19 | Kuyruk 10, haftalık rejim: puan günlükten üretilen kapanmış haftalık mumlardan (haftalık EMA20/EMA50 + 13 hafta getiri), giriş haftalık puan ≥ +1, BTC-dönüş çıkışı haftalık BTC puanıyla, günlük EMA20 çıkışı aynı (`PusulaV2NoBeWeekly`, temel PusulaV2NoBe) | **Red**: 16: 230→209 işlem, +1.35→+0.86R, toplam 311.3→179.5R, DD %23.7→%21.9; 20: 193→101 işlem, +0.61→+2.41R, toplam 117.7→243.6R, DD %22.6→%31.8 (> %25), +237.1R tek ZEC 2025-09 işleminden (hariç +6.5R). ZEC'i haftalık BTC çıkışı açtı (günlük BTC -1, haftalık +3). Hile testi temiz. | `results/2026-10-19_pusula_haftalik_rejim/rapor.md` |
| 2026-10-18 | Kuyruk 7, coin seçimi: aynı mumda boş yerden çok sinyal varsa 90 günlük getirisi en yüksek coinler girer (`PusulaV2NoBeRank`, temel PusulaV2NoBe) | **Red**: çakışma seyrek (16'da 23 mum, 20'de 16 mum / 6.5 yıl). 16: 230→233 işlem, +1.35→+1.32R, toplam 311.3→308.0R, DD %23.7→%25.1; 20: 193→194 işlem, +0.61→+0.66R, toplam 117.7→128.2R, DD %22.6→%23.3 (fark tek seçimden: 2024-11 FIL yerine MANA). Ters coin sırası 16'da 371.4R (tek DOGE işlemi +66.5R): coin sırası şansı kural etkisinden büyük. | `results/2026-10-18_pusula_coin_secimi/rapor.md` |
| 2026-10-17 | Kuyruk 6, yeniden giriş: temel zaten her yeni kırılımda aynı coine tekrar giriyor; tersi test edildi, günlük trend başına tek işlem (`PusulaV2NoBeNoReentry`, temel PusulaV2NoBe) | **Red**: 16: 230→194 işlem, +1.35→+1.03R, toplam 311.3→199.2R, DD %23.7→%17.1; 20: 193→164 işlem, +0.61→+0.55R, toplam 117.7→89.6R, DD %22.6→%23.4. Yeniden girişler temelde ilk girişlerden iyi (16: +2.50R vs +0.53R; 20: +0.95R vs +0.51R, 20'de en büyük 3 işlem hariç ≈0). Yeniden giriş kalıyor, temel `PusulaV2NoBe`. | `results/2026-10-17_pusula_yeniden_giris/rapor.md` |
| 2026-10-13 | Çıkarma 5: BTC-dönüş çıkışı kaldırıldı (`PusulaV2NoBeNoBtcExit`, temel PusulaV2NoBe; EMA20 çıkışı aynı) | **Red**: 16: 230→276 işlem, +1.35→+1.01R, toplam 311.3→279.0R, DD %23.7→%18.0; 20: 193→220 işlem, +0.61→+1.31R, toplam 117.7→287.7R, PF 1.53→2.59, DD %22.6→%38.6 (> %25). Çıkış girişi de engelliyordu: yeni işlemler BTC puanı ≤ -1 iken açıldı (16'da ≈0R, 20'de ZEC 2025-09 tek işlem +186R, ZEC hariç -20R). 16'da ETC 2021 -46R. Kural kalıyor; çıkarma listesi bitti, temel `PusulaV2NoBe`. | `results/2026-10-13_pusula_cikarma5_btccikis/rapor.md` |
| 2026-10-12 | Çıkarma 4: trend çıkışı EMA20 yerine EMA50 (`PusulaV2NoBeEma50`, temel PusulaV2NoBe) | **Red**: 16: 230→158 işlem, +1.35→+3.18R, toplam 311.3→503.0R, DD %23.7→%21.5; 20: 193→166 işlem, +0.61→+1.30R, toplam 117.7→215.8R, PF 1.53→1.52, DD %22.6→%27.8 (> %25). Kazanç tek işlemlere bağlı (16'da BNB 2021, 20'de THETA 2020-21 +135R; THETA hariç 20'de -37R). EMA20 çıkışı kalıyor, temel `PusulaV2NoBe`. | `results/2026-10-12_pusula_cikarma4_ema50/rapor.md` |
| 2026-10-11 | Çıkarma 3: 2R'de stopu girişe çekme kaldırıldı (`PusulaV2NoBe`, temel PusulaV2NoBtcScore1) | **Kabul**: 16: 238→230 işlem, +1.30→+1.35R, toplam 309.9→311.3R, DD %21.5→%23.7; 20: 201→193 işlem, +0.52→+0.61R, toplam 104.8→117.7R, DD %22.2→%22.6. Eski 16'da fark fiilen yok; yeni 20'de kazanç çoğunlukla FIL+VET. Temel artık `PusulaV2NoBe`. | `results/2026-10-11_pusula_cikarma3_be/rapor.md` |
| 2026-10-11 | Çıkarma 2: long için günlük puan eşiği +3 → +1 (`PusulaV2NoBtcScore1`, temel PusulaV2NoBtcFilter) | **Kabul**: 16: 210→238 işlem, +1.20→+1.30R, DD %26.1→%21.5; 20: 150→201 işlem, +0.46→+0.52R, DD %24.6→%22.2. Kazanç birkaç coinde (SOL; ALGO+UNI). | `results/2026-10-11_pusula_cikarma2_puan/rapor.md` |
| 2026-10-10 | Çıkarma 1: BTC giriş filtresi kaldırıldı (`PusulaV2NoBtcFilter`, temel PusulaV2) | **Kabul**: iki listede de aynı (16: 210 işlem +1.20R DD %26.1; 20: 150 işlem +0.46R DD %24.6). Filtre gereksiz: BTC-dönüş çıkışı aynı mumlarda girişi zaten engelliyor. | `results/2026-10-10_pusula_cikarma1_btcfiltre/rapor.md` |
| 2026-10-10 | Geliştirme 3a: hacim onayı 1.5x; 3b: 10 günlük süre stopu (temel PusulaV2) | İkisi de red. 3a yeni 20'de iyi (+0.76R) ama eski 16'da kötü (DD %33). | `results/2026-10-10_pusula_gelistirme3_ozet.md` |
| 2026-10-10 | Geliştirme 2a: BTC skoru ≤ -1 olunca long çıkışı; 2b: long sadece BTC'den güçlü coinde | 2a kabul (16: +0.95→+1.20R, 20: +0.44→+0.46R, 10 işlem değişti) → `PusulaV2`. 2b red. | `results/2026-10-10_pusula_gelistirme2_ozet.md` |
| 2026-10-10 | Geliştirme 1: short sadece BTC'den zayıf coinde (`PusulaTrendRS`), 16 + 20 coin | Red: iki listede de temelden kötü (+0.57→+0.52R, +0.27→+0.26R). | `results/2026-10-10_pusula_gelistirme1_rs_ozet.md` |
| 2026-10-10 | 20 yeni coin (hiç görülmemiş), 2020-01 → 2026-09 | Long +0.44R (150), DD %24.7, 9/20 coin artıda, en iyi 10 işlem dışında eksi. Long+short +0.27R (short +0.12R). | `results/2026-10-10_pusula_yeni20coin/rapor.md` |
| 2026-10-09 | Birim testleri (rejim puanı sadece geçmiş veriyi kullanıyor) + ilk backtest (geliştirme 2020-03 → 2024-12) | Pusula_B +0.08R, PF 1.07, DD %35.0, 269 işlem (long +21.3R, short -0.1R). Kârın tamamı 2020 long'ları; 2021-2024 ≈ -1.6R. BTC filtresiz: +0.06R, DD %38.2. Geçemedi; doğrulamaya bakılmadı. | [results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme](../results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme/rapor.md) |
| 2026-10-09 | 2. tur geliştirme (en fazla 3 işlem) | **PusulaTrend** +0.43R, PF 1.40, DD %31.0, 214 işlem (long +109.5R her yıl artıda, short -17.8R). Aynı girişlerle sabit TP: +0.11R. 5 işlemle +0.49R DD %33.7. Maliyet x2: +0.39R. Hile testi temiz. | [tur2_gelistirme_max3](../results/2026-10-09_PusulaTrend_Pusula_B_tur2_gelistirme_max3/rapor.md) |
| 2026-10-09 | PusulaTrendLong (sonradan eklendi) geliştirme + ±%20 | +0.83R, PF 1.87, DD %20.2, 132 işlem. 8 parametre komşusunun hepsi +0.72R ile +1.45R. | [sadece_long](../results/2026-10-09_PusulaTrendLong_tur2_gelistirme_sadece_long/rapor.md), [dayanıklılık](../results/2026-10-09_pusula_trend_long_dayaniklilik/parametre_komsulari.md) |
| 2026-10-09 | **Doğrulama, bir kez** (2025-01 → 2026-03) | PusulaTrend +0.16R, PF 1.27, DD %12.7, 64 işlem (short +0.04R). PusulaTrendLong +0.28R, PF 1.50, DD %7.7, 31 işlem. Al-tut -%40. | [tur2_dogrulama](../results/2026-10-09_PusulaTrend_PusulaTrendLong_tur2_dogrulama/rapor.md) |
| 2026-10-10 | **Kasa, bir kez** (2026-04 → 2026-09, 16 coin, en fazla 3 işlem) | PusulaTrendLong -0.02R, PF 0.94, DD %6.2, 15 işlem (3 işlem dönem sonunda kârda açıktı). Long+short -0.07R. 6 coin -0.68R. Al-tut +%15.9. Geçemedi (> 0R şartı). | [kasa_16coin](../results/2026-10-10_pusula_kasa_16coin/rapor.md), [kasa_6coin_bilgi](../results/2026-10-10_pusula_kasa_6coin_bilgi/rapor.md) |

## Notlar / öğrenilenler
- Yer yönetimi (2026-10-30): "dolu yerde 10 günden yaşlı zarardaki işlemi kapat" kuralı neredeyse hiç devreye girmedi (16'da 1, 20'de 0 kez). Zararda kalan işlemi günlük EMA20 çıkışı genelde ilk 2-7 günde kapatıyor; 10 gün yaşayan işlem neredeyse her zaman kârda. Yer kayması yaşlı kötü işlemlerden değil, aynı gün gelen kırılımlar arasında kimin önce girdiğinden geliyor.
- Günlük puan şartı (2026-10-29): kaldırınca eski 16 çok iyileşti ama DD %25'i aştı, yeni 20'de ortalama R düştü. Puan grupları (-3 / -1 / +1 / +3) arasında iki listede tutarlı bir sıra yok, yani puan kırılım kalitesini pek ayırmıyor; asıl ayı piyasası koruması BTC-dönüş kuralı (2022'de puanı düşük kırılımların ≈ %90'ı BTC puanı ≤ -1 iken). Fark yine birkaç büyük işlem ve 3 yer sınırındaki yer kaymasından (XLM / HBAR 2024-11 girdi, ALGO 2024-11 / UNI 2024-02 kaçtı).
- Piyasa genişliği (2026-10-28): "listenin yarısı trendde mi" şartı öncü coinlerin erken kırılımlarını kesiyor (SOL / BTC 2023-10 o anda 16 coinden sadece 4'ü trenddeyken başladı). Dört giriş filtresi (trend yaşı, funding, mum şekli, genişlik) aynı sebeple tutmadı: kâr, trend herkesçe görülmeden başlayan birkaç büyük işlemden geliyor. Filtrelerin bir listedeki iyi görünmesi çoğunlukla 3 yer sınırındaki yer kaymasından.
- Güçlü kapanış (2026-10-27): 4h kırılımların ≈ %80'i zaten mumun üst üçte birinde kapanıyor; zayıf kapanan kırılımlar daha kötü değil (iki listede de ortalaması daha yüksek) ve en büyük trend işlemlerinden bazıları (BTC 2023-10, FIL 2021-03) zayıf kapanışla başladı. Mum şekli bu stratejide giriş kalitesini ayırmıyor.
- Funding filtresi (2026-10-26): yıllık %50 üstü funding girişlerde çok nadir (%5, sadece 2020-2021 boğası) ve o işlemler ne iyi ne kötü. Funding masrafı uç anlarda girmekten değil, normal oranda (≈ %11 / yıl) uzun tutmaktan geliyor; giriş filtresi bunu azaltmıyor.
- Dip stopu (2026-10-23): sadece 1.5 ATR stop getiriyi artırdı ama %1 riskle düşüşü %44 / %68'e çıkardı (sık stop, uzun kayıp serileri, büyük pozisyon). Geniş stop düşüşü sınırda tutuyor; kalıyor.
- Düşüş freni (2026-10-25): zirveden %15 aşağıdayken riski yarıya indirmek net/DD oranını iki listede de bozdu. Bu strateji düşüşten birkaç büyük trend işlemiyle çıkıyor; o işlemleri küçük almak düşüşü az, kazancı çok kesiyor.
- Trend yaşı (2026-10-24): genç trendde (ilk 10 gün) gelen kırılımları atlamak tutmadı; o işlemler zayıf ama toplamda artı, ve 3 yer sınırında boşalan yere giren işlem daha iyi olmuyor. Teşhiste zayıf görünen grubu çıkarmak, yer etkisi yüzünden backtestte aynı kazancı vermiyor.
- Trendin yaşı (2026-10-22, teşhis): günlük trendin ilk 10 gününde açılan işlemler (%40-48'i) iki listede de kazançsız (en iyi tek işlem hariç ≈0R); olgun trenddeki kırılımlar daha iyi. Kural değişmedi; kuyruk 15'te test edilecek.
- Kırılımın değeri (2026-10-21): günlük trend yukarıyken her an girmek iki listede de çok kötü (DD %49 / %83). Kâr günlük trendde bulunmaktan değil, 4h kırılımın seçtiği andan geliyor.
- Hayatta kalan coin yanılgısı (2026-10-16): sonradan batan 12 coinde Pusula ≈0R (V2NoBe) / -0.79R (TrendLong). Çöküşlere yakalanmıyor (günlük trend çöküşten önce bozuluyor), ama bu coinlerde kazanç da yok. Bugünkü listeyle yapılan her test ortalama R'yi kabaca %10-20 iyimser gösteriyor; beklentiler buna göre indirilmeli.
- Geliştirmede iyi görünen üç ek değişiklik (BE 1R, kapanıştan giriş, iki vitesli çıkış) yeni coinlerde tutmadı. Basit sürüm kazandı.
- Kâr birkaç büyük trende bağlı; daha çok coin bu bağımlılığı azaltıyor (16 coinde en iyi 10 işlem hariç ≈ 0R, 6 coinde -42.8R).
- Sabit 2R/4R hedef yerine trend bozulunca çıkmak, aynı girişlerde ortalamayı +0.11R'den +0.43R'ye çıkardı. Asıl açık çıkış kuralıydı.
- Short tarafı iki turda da geliştirmede zararda, doğrulamada başa baş. Bu coinlerde trend takipli short avantajı yok gibi.
- Üç ölçünün de aynı yönü göstermesi short'ları kurtarmadı: 2022'de 63 short, ortalama -0.02R.
- Rejim ölçümü (araştırma): güçlü yükseliş günlerinden sonraki 7 gün ortalama %+4.8, güçlü düşüşten sonra %+1.2, tüm günler %+2.8. Düşüş rejimi bu dönemde short avantajı vermiyor.
- Kazanan işlemler ortalama 13 gün sürüyor. Sabit 2R/4R hedef, trendin büyük kısmını kaçırıyor olabilir (test edilmedi).
- Yorum modülü (`commentary`) her coin için her an rejim + tetik seviyesi + plan yazabiliyor; strateji geçmediği için çıktısı sinyal sayılmaz.
- Doğrulama dönemi (2025-01 → 2026-03) daha önce benzer Donchian stratejilerinde kullanıldı; bu strateji için tamamen temiz değil. Temiz test kasa testidir.

## Emeklilik gerekçesi (varsa)
