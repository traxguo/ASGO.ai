# aslan_liquidity — Likidite alımı + MSS / iFVG (Aslan'ın stratejisi)

Kod: [`strategies/candidates/aslan_liquidity.py`](../strategies/candidates/aslan_liquidity.py)
Haber takvimi: [`strategies/common/news_calendar.py`](../strategies/common/news_calendar.py)

## Hipotez
Aslan'ın stratejisi (2026-10-08, sohbette anlattı). Büyük grafiklerdeki (1 günlük, 4 saatlik) belirgin tepe ve diplerin hemen ötesinde stop emirleri birikir (likidite). Fiyat bu seviyeyi alıp (iğne atıp) küçük grafikte geri dönerse, dönüş yönünde güçlü bir hareket gelir. Sadece günlük yön (daily bias) tarafında işlem açılır: akıntıya karşı yüzülmez.

## Yön
İkisi de (long ve short), ama her an sadece günlük yönün izin verdiği tarafta.

## Giriş koşulları
Koşul kimlikleri koddakiyle aynıdır. Hepsi aynı mumda doğru olmalı.

**Long**
- [bias_up] Teknik: son kapanmış günlük mum, son onaylı günlük tepenin üstünde kapattı (ve sonra son onaylı günlük dibin altında kapanış olmadı) | Açıklama: "Günlük yön yukarı: günlük mum son tepenin üstünde kapattı."
- [liquidity_swept_low] Teknik: fiyat, 1d veya 4h grafikteki onaylı bir dibin ya da bir önceki günün dibinin altına indi; bu son `setup_window` mum içinde oldu | Açıklama: "Fiyat {seviye} altındaki likiditeyi aldı."
- [reversal_mss_or_ifvg] Teknik: giriş grafiğinde (1h veya 15m) ya **MSS** = kapanış, likidite alımındaki en dip mumdan önceki son küçük tepenin üstünde; ya da **iFVG** = alım hareketi sırasında oluşan aşağı yönlü bir boşluğun (bearish FVG) üst kenarının üstünde ilk kapanış | Açıklama: "Fiyat likiditeyi aldıktan sonra yön değiştirdi (MSS / iFVG)."
- [no_news] Teknik: sinyal anı, önemli ABD haberinin (FOMC, CPI, NFP) 1 saat öncesi ile 1 saat sonrası arasında değil | Açıklama: "Yakında önemli ABD haberi yok."

**Short:** tam tersi — [bias_down], [liquidity_swept_high] (tepe likiditesi alındı), [reversal_mss_or_ifvg] (son küçük dibin altında kapanış ya da yukarı yönlü boşluğun alt kenarının altında kapanış), [no_news].

Tanımlar:
- **Tepe / dip (swing):** solundaki 2 ve sağındaki 2 mumdan daha yüksek tepesi (veya daha alçak dibi) olan mum. Sağdaki 2 mum kapanınca onaylanır; ondan önce kullanılmaz.
- **Bir likidite seviyesi bir kez kullanılır.** Alındıktan sonra listeden düşer.
- Her likidite alımından en fazla bir işlem çıkar.

## İşlem yönetimi
- Giriş: sinyal mumunun kapanış fiyatına limit emir, 2 mum içinde dolmazsa iptal (önce stop'a değerse de iptal).
- Stop (v2, Aslan 2026-10-08, `AslanLiq2_*`): iğne en fazla gövdenin %175'i kadar olabilir; daha uzunsa stop gövde ucundan 1.75 gövde uzağa konur. Günlük yön filtresi kapalı versiyon (`*_NoBias`) her iki yönde de işlem arar.
- Stop (v1, karşılaştırma için): likiditeyi alan en uç mumun iğnesi (long'da en dip mumun dibi). **O mumun iğnesi gövdesinden uzunsa** stop iğneye değil gövdenin ucuna konur (Aslan: "abartı fitil varsa mumun kapanışını al"). Tampon yok. Stop fiyatın %8'inden uzaksa sinyal yok.
- Hedef: tek hedef **2R**, kısmi çıkış yok, stop başa çekilmez (`MODEL_ASLAN`, 1R stop / 2R hedef). Projenin standart A/B modellerinden farklıdır, çünkü stratejinin sahibi böyle kullanıyor.
- Risk: işlem başına kasanın **%3**'ü (Aslan %3-5 diyor). Kaldıraç en fazla 20x, likidasyon her zaman stop mesafesinin en az 2 katı uzakta.
- Saat filtresi yok ("her zaman girebilir"), sadece haber filtresi var.

## Zaman dilimi ve parametreler
Test öncesi sabitlendi; Aslan düzeltirse kart ve kod birlikte değişir.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Likidite grafikleri | 1d + 4h (+ önceki gün tepe/dip) | sabit |
| Giriş grafiği | `AslanLiq_1h`: 1h, `AslanLiq_15m`: 15m | 15m, 1h |
| Swing tanımı | 2 mum sol / 2 mum sağ | 2-3 |
| Alımdan sonra dönüş bekleme süresi | 12 saat (1h'de 12 mum, 15m'de 48 mum) | 6-24 saat |
| FVG arama geriye | alımdan 10 mum önce | 5-20 |
| Haber penceresi | 1 saat önce → 1 saat sonra | 30 dk - 2 saat |
| Hedef | 2R | Aslan'ın kuralı |
| Risk | %3 | %3-5 |

## Varsayımlar (Aslan onaylamadı, kendisi düzeltebilir)
1. Likidite seviyesi tanımı (2+2 mum swing, önceki gün tepe/dip).
2. Günlük yön tanımı (son günlük tepe/dibin ötesinde kapanış).
3. MSS'nin hangi tepeye göre ölçüldüğü (alım dibinden önceki son küçük tepe).
4. iFVG: alımdan 10 mum öncesinden itibaren oluşan boşluk, ilk kapanışla ters çevrilmesi.
5. "Mum boyutu" = mumun gövdesi.
6. Haber listesi çevrimdışı hazırlandı (ForexFactory'ye bu ortamdan erişilemiyor): FOMC tarihleri, CPI tarihleri ve NFP tarih kuralı. Tarihler resmi takvimle doğrulanmadı.


## v3 — Aslan'ın 2026-10-09 düzeltmeleri
Kod: [`strategies/candidates/aslan_liquidity_v3.py`](../strategies/candidates/aslan_liquidity_v3.py)

- **Likidite seviyeleri:** 1h, 4h ve 1d tepe/dipleri, önceki gün tepe/dibi, seans tepe/dipleri (UTC: Asya 00-07, Londra 07-13, New York 13-21; seans bitince kullanılır).
- **İki tür kurulum:**
  - [liquidity_taken] **Alım (sweep):** fiyat seviyeyi iğneyle geçip içeride kapatırsa ters yönde işlem (dip alındı → long, tepe alındı → short). | "Fiyat {seviye} likiditesini alıp geri döndü."
  - [liquidity_taken] **Kırılım (break):** bir mum seviyenin ötesinde kapatırsa kırılım yönünde işlem (tepe kırıldı → long, dip kırıldı → short). Önce alım sayılan seviye 12 saat içinde gövdeyle kırılırsa kırılıma dönüşür. | "Fiyat {seviye} seviyesini mum kapanışıyla kırdı."
- [reversal_mss_or_ifvg] **Giriş onayı:** işlem yönünde MSS veya iFVG, giriş grafiğinde (`AslanLiq3_15m`: 15 dk, `AslanLiq3_5m`: 5 dk), 12 saat içinde.
- [trend_up] / [trend_down] **Trend (daily bias):** son onaylı tepe ve dip bir öncekinden yüksekse (HH + HL) yukarı, alçaksa (LH + LL) aşağı, karışıksa nötr. Ana versiyon 4 saatlik trende bakar; `_Trend2` 4 saatlik ve 1 saatlik ikisinin de aynı yönde olmasını ister; `_NoTrend` filtre kullanmaz.
- **Hedef:** tek hedef **1R** (`MODEL_1R`). **Stop:** v2 kuralı (iğne en fazla gövdenin %175'i).
- Haber filtresi, giriş fiyatı, 2 mum geçerlilik aynı. Risk testte %1 (hesap tüm dönem boyunca yaşasın diye; R sonuçları riskten bağımsız).

## v4 — videodaki kontrol listesi (2026-10-09)
Kod: [`strategies/candidates/aslan_liquidity_v4.py`](../strategies/candidates/aslan_liquidity_v4.py)
- [bias_up]/[bias_down] günlük HH+HL / LH+LL; [trend_up]/[trend_down] 4 saatlik aynı yön.
- [poi_touched] fiyat 1 saatlik bir FVG, order block veya iFVG bölgesine döndü | "Fiyat {bölge} bölgesine geri çekildi."
- [mini_structure_engulf] 5 dk / 15 dk'da son mini tepeyi (1+1 mum) kıran engulf mumu | "Küçük grafikte yapı kırıldı ve engulf mumu geldi."
- Stop: dönüşün uç noktası (iğne en fazla gövdenin %175'i). Hedef 1R (`AslanLiq4_*`) veya 2R (`*_2R`).
 candidate — ilk backtest'te başarısız, Aslan'ın kural düzeltmesi bekleniyor
## v6 — teyit sadece likidite alımından sonra (2026-10-09)
Kod: `AslanLiq6_5m`, `AslanLiq6_1m` ([`aslan_liquidity_v3.py`](../strategies/candidates/aslan_liquidity_v3.py), `post_sweep=True`)
- v5 ile aynı (sadece alım, stop uç noktanın %0.1 ötesi, 4 saatlik trend, 1R). Fark: teyit alımdan sonra oluşmalı.
- [reversal_mss_or_ifvg] alımdan sonra işlem yönünde yeni FVG, alımdan sonra oluşmuş boşluğun ters kırılması (iFVG) veya MSS; 5 dk veya 1 dk | "Likidite alındı, ardından {FVG/iFVG/MSS} oluştu."
- İşlem denetimi grafikleri: `research/audit/aslan_trade_audit.py` (20 rastgele işlem, Aslan "alırdım / almazdım" diye işaretler).

## v7 — alım, sonra 5 dk MSS, sonra 1 dk giriş (2026-10-09)
Kod: [`aslan_liquidity_v7.py`](../strategies/candidates/aslan_liquidity_v7.py)
- [sweep_then_mss_5m] likidite alındı ve 5 dk mumu son tepe/dibin ötesinde kapandı | "Likidite alındı, 5 dakikalıkta yapı kırıldı (MSS)."
- [fvg_or_ifvg_1m] MSS'ten sonra 1 dk'da FVG/iFVG (`AslanLiq7_1m`) | "1 dakikalıkta FVG oluştu, giriş."
- Seçenek (`AslanLiq7_1m_Retest`): MSS mumunun bıraktığı 5 dk FVG'ye geri dönüşte limit giriş | "Fiyat MSS boşluğuna geri geldi, giriş."
- Stop alım uç noktasının %0.1 ötesi, hedef 1R.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-08 | Lookahead kontrolü (BTC 1h ve 15m, 50 kesim noktası) | Geleceği görme yok (`research/robustness/aslan_lookahead_check.py`). | — |
| 2026-10-08 | İlk backtest, geliştirme (2020-01 → 2024-12) | 1h: -0.21R, PF 0.72, 2266 işlem. 15m: -0.28R, PF 0.63, 3143 işlem. Maliyet hariç ~0R. %3 riskle hesap 2023'te sıfırlandı. Haber filtresi etkisiz. Doğrulama ve kasa kullanılmadı. | [results/2026-10-08_aslan_liquidity_ilk_backtest](../results/2026-10-08_aslan_liquidity_ilk_backtest/README.md) |
| 2026-10-08 | v2: iğne en fazla gövdenin %175'i (Aslan), yön filtresi açık/kapalı | 1h: -0.16R (filtre açık), -0.14R (kapalı). 15m: -0.20R / -0.16R. İyileşti ama hâlâ eksi; maliyet hariç ~0R. Yön filtresi faydasız. | [results/2026-10-08_aslan_liquidity_v2](../results/2026-10-08_aslan_liquidity_v2/README.md) |
| 2026-10-09 | v3: 1R, seans seviyeleri, kırılım, HH/HL trend, 15 dk ve 5 dk (6 varyant) | 15 dk: -0.32 ile -0.39R; 5 dk: -0.46 ile -0.58R. Maliyet hariç hepsi ~0R. Test hesapları erken sıfırlandı. | [results/2026-10-09_aslan_liquidity_v3](../results/2026-10-09_aslan_liquidity_v3/README.md) |
| 2026-10-09 | v4: videodaki yöntem (günlük+4s trend, 1s FVG/OB/iFVG bölgesine dönüş, mini yapı kırılımı + engulf; 5 dk/15 dk, 1R/2R) | -0.24R ile -0.33R; maliyet hariç ~0R; winrate yazı-tura beklentisinde. | [results/2026-10-09_aslan_liquidity_v4](../results/2026-10-09_aslan_liquidity_v4/README.md) |
| 2026-10-09 | v5: sadece likidite alımı, 5/15 dk OB/iFVG/MSS onayı, stop alım uç noktasının %0.1 ötesi, 1R/2R | -0.24R ile -0.27R; maliyet hariç ~0R. | [results/2026-10-09_aslan_liquidity_v5](../results/2026-10-09_aslan_liquidity_v5/README.md) |
| 2026-10-09 | v6: teyit sadece alımdan sonra oluşan FVG/iFVG/MSS, 5 dk ve 1 dk, 1R | 5 dk: -0.25R (3022 işlem); 1 dk: -0.37R (2508 işlem, hesap 11.2024'te bitti). Maliyet hariç ~0R. | [results/2026-10-09_aslan_liquidity_v6](../results/2026-10-09_aslan_liquidity_v6/README.md) |
| 2026-10-09 | v7: alım → 5 dk MSS → 1 dk FVG/iFVG ya da MSS boşluğuna geri dönüş | -0.21R (1945 işlem) / -0.22R (1148 işlem); maliyet hariç ~-0.03R. | [results/2026-10-09_aslan_liquidity_v7](../results/2026-10-09_aslan_liquidity_v7/README.md) |

## Notlar / öğrenilenler
- Kazanma oranı %30-32; 2R hedefle başa baş için ~%33 gerekiyor. Maliyetsiz bile sonuç ~0R: giriş kuralının kenarı yok.
- Stop iğnenin ucunda olduğu için çok dar (1h ortanca %1.8, 15m %1.1); işlem başı ~%0.2 maliyet R'nin büyük kısmını yiyor. En dar stoplu işlemler en kötüsü.
- MSS ve iFVG ayrı ayrı da eksi. Long ve short, 5 coinin hepsi, 2020-2024'ün her yılı eksi.
- Aslan'ın gözle yaptığı seçim kartın varsayımlarından farklıysa (özellikle "önemli likidite" ve günlük yön), düzeltilmiş kurallarla yeniden test edilecek. Doğrulama verisi bunun için temiz duruyor.

## Emeklilik gerekçesi (varsa)

## 4 saatlik test (2026-10-16, Gemini önerisi)
Kod: `AslanLiq4h`, `AslanLiq4h_NoBias` (`strategies/candidates/aslan_liquidity.py`). v2 kuralları (iğne %175, 2R, %1 risk), giriş 4h, likidite günlük + haftalık tepe/dipler ve önceki gün/hafta, bekleme 24 saat.
Geliştirme (2020-2024, 5 coin): yön filtresi açık 868 işlem **-0.15R**, kapalı 1279 işlem **-0.08R**, düşüş %79. Kazanma %30-32 (2R'de başa baş %33.3), yani maliyetsiz bile eksi. Komisyonu küçültmek sonucu kurtarmadı. Rapor: `results/2026-10-16_aslan_liquidity_4h/rapor.md`.

## Nasdaq testi (2026-11-05) — kriptodan mı tutmuyor, yoksa hiç mi kenarı yok?
GUO'nun sorusu: kriptoda 30 versiyonun hepsi eksiydi. Sebep kriptonun oynaklığı/masrafı mı, yoksa stratejinin kendisi mi? Aynı kod (v2 ve v7, hiçbir ayar değişmeden) Nasdaq'ta (NAS100), ikinci olarak EURUSD ve altında, long ve short ayrı ayrı denendi. Ayrıntı ve tüm tablolar: [results/2026-11-05_aslan_nasdaq](../results/2026-11-05_aslan_nasdaq/README.md). Kod: `research/aslan_nasdaq/` (PR #53).

Nasıl: GitHub sunucusunda HistData 1 dakikalık veri; günlük ve 4 saatlik mumlar gerçek işlem gününe göre (New York 17:00 → 17:00), hafta sonu boşlukları dahil. Masraf Nasdaq %0.010 (kriptoda %0.2'ydi), ayrıca 2 kat masrafla. Simülatör önce BTC'de eski Freqtrade sonuçlarını tekrar üretti (v7: 435 işlemin 435'i, aynı sonuç). Ek kontrol: her işlem rastgele bir zamanda aynı stop ve hedefle açılsaydı ne olurdu ("rastgele giriş"), çünkü Nasdaq 2020-2024'te çok yükseldi ve long'lar sadece bu yüzden kârlı görünebilir.

### Nasdaq, işlem başı ortalama R (maliyet öncesi / rastgele giriş / maliyet sonrası)
| Versiyon | Geliştirme 2020-24 | Doğrulama 2025-26/03 | Long / short (geliştirme, maliyet öncesi) |
|---|---|---|---|
| v2 1h yön filtreli | 368 işlem, **+0.09** / -0.01 / **+0.07**, PF 1.10 | 107 işlem, **+0.17** / -0.04 / **+0.15**, PF 1.24 | +0.22 / -0.11 |
| v2 1h filtresiz | 645 işlem, **+0.07** / -0.04 / **+0.04**, PF 1.06 | 180 işlem, **+0.20** / -0.06 / **+0.17**, PF 1.28 | +0.21 / -0.05 |
| v2 15m filtreli | 666, 0.00 / +0.01 / -0.04 | 178, +0.07 / -0.03 / +0.03 | +0.06 / -0.10 |
| v2 15m filtresiz | 1384, -0.02 / -0.01 / -0.05 | 345, +0.04 / -0.03 / -0.01 | +0.03 / -0.05 |
| v7 1 dk | 229, +0.05 / 0.00 / +0.03 | 54, -0.15 / +0.01 / -0.18 | +0.12 / -0.04 |
| v7 geri dönüş | 149, +0.11 / +0.02 / +0.09 | 34, -0.18 / 0.00 / -0.20 | +0.36 / -0.20 |

2 kat masrafla v2 1h hâlâ artı (geliştirme +0.05 / +0.02, doğrulama +0.13 / +0.15). Düşüş (DD, %1 risk): geliştirmede %21-30, doğrulamada %8-10.

### EURUSD ve altın (aynı kod)
- **EURUSD:** her versiyon maliyet öncesi -0.02 ile +0.08R arası, rastgele girişten farksız; maliyetle neredeyse hepsi eksi. Kenar yok.
- **Altın:** long'lar artı ama rastgele giriş de aynı kadar artı (2025 altın yükselişi): v2 1h filtresiz doğrulama long +0.39R, rastgele +0.32R. Short'lar her yerde eksi. Kenar yok, sadece piyasanın yönü.

### Kripto ile kıyas
Kriptoda (5 coin, geliştirme) maliyet öncesi -0.04 ile +0.03R arasıydı; BTC'de v2 1h +0.03R, rastgele giriş -0.00R. Nasdaq'ta sadece **v2 1 saatlik** versiyon iki dönemde de hem artı hem rastgele girişin üstünde (geliştirmede ~+0.1R, doğrulamada ~+0.2R fazla). 15 dk ve 1 dk versiyonlar Nasdaq'ta da ~0R.

### Sonuç
- Kriptoda kaybettiren şeyin büyük kısmı **masraftı**: dar stopta %0.2 masraf işlem başına 0.1-0.4R yiyordu. Nasdaq'ta masraf 0.02-0.05R'ye düşüyor.
- Ama kural masrafsız da çoğunlukla ~0R: 6 versiyon × 3 piyasa = 18 denemenin sadece biri (Nasdaq v2 1h) iki dönemde de rastgelenin belirgin üstünde. 18 denemede bir tanesinin şansla böyle çıkması mümkün; örnek küçük (doğrulamada 107-180 işlem, ortalamanın belirsizliği ±0.13R civarı).
- Long/short tutarsız: geliştirmede kâr long'lardan, short'lar eksi; doğrulamada kâr short'lardan. Sağlam bir kenar her iki tarafta da benzer davranırdı.
- **Karar önerisi:** "Hiç umut yok" değil ama "kanıtlandı" da değil. Nasdaq v2 1h, kurallar dondurulup kağıt üzerinde takip edilebilir veya kasa döneminde (2026-04 → 09) bir kez denenebilir; para için yeterli değil. Kripto için yeni Aslan versiyonu önerilmez.

## Kasa testi (holdout, 2026-04-01 → 2026-09-30) — bir kez, kurallar PR #53'teki gibi donduruldu
Denetçi (ana konu) 2026-11-05'te bir kez onayladı. Kod: `sim.py --holdout`, iş akışı `aslan_nasdaq_holdout.yml` (elle, bir kez çalıştırıldı, PR #54). Değerlendirilen: **Nasdaq v2 1h yön filtreli** (kartın orijinali); filtresiz yanında rapor edildi.
Geçme şartı (testten önce yazıldı): maliyet sonrası R > 0 ve PF > 1.05 (1 kat masraf), 2 kat masrafta R ≥ 0, maliyet öncesi R rastgele girişin üstünde.

| Versiyon | Yön | İşlem | Kazanma | Maliyet öncesi R | Rastgele giriş | Maliyet sonrası R | PF | 2 kat masraf R | DD |
|---|---|---|---|---|---|---|---|---|---|
| **v2 1h yön filtreli** | long | 27 | %37.0 | +0.111 | -0.018 | +0.095 | 1.15 | +0.079 | %9 |
| | short | 19 | %42.1 | +0.263 | +0.003 | +0.238 | 1.40 | +0.214 | %4 |
| | **hepsi** | **46** | %39.1 | **+0.174** | -0.010 | **+0.154** | **1.25** | **+0.135** | %7 |
| v2 1h filtresiz | long | 36 | %41.7 | +0.250 | -0.004 | +0.236 | 1.40 | +0.221 | %6 |
| | short | 41 | %31.7 | -0.049 | -0.043 | -0.080 | 0.89 | -0.111 | %10 |
| | hepsi | 77 | %36.4 | +0.091 | -0.025 | +0.068 | 1.10 | +0.044 | %8 |

**Sonuç: GEÇTİ** (yön filtreli versiyon dört şartın hepsini sağladı; long ve short ikisi de artı). Üç dönemde de artı: geliştirme +0.07R (368 işlem), doğrulama +0.15R (107), kasa +0.15R (46).
Dikkat: kasada sadece 46 işlem var (ayda ~8), tek başına ortalamanın belirsizliği ±0.2R civarı. Bu bir "kanıt" değil, "elenmedi" demektir. Kasa artık kullanıldı; bu kurallar için tekrar kullanılamaz.

**Öneri (henüz yapılmadı, GUO onayı bekliyor):** Nasdaq v2 1h yön filtreli için kağıt üzerinde takip (sinyal + sonuç kaydı, emir yok). Gerekenler: canlı Nasdaq 1 dk/1 saat veri kaynağı (HistData sadece geçmiş verir; seçenekler: broker demo API'si, ör. OANDA/Capital.com/IG, veya ücretsiz gecikmeli veri), saatlik çalışan GitHub Actions işi, `forward/paper_aslan_nas/` kaydı ve haftalık rapor. Kurallar dondurulmuş haliyle; ayda ~8 sinyal beklenir, anlamlı bir karar için en az 3-6 ay gerekir.

## Kağıt takip (2026-11-05'ten itibaren) — Nasdaq v2 1h yön filtreli
Denetçi kararı (2026-11-05): kasa testini geçen kural gerçek para olmadan, kağıt üzerinde takip edilir. Kod: [`scripts/paper_aslan_nas.py`](../scripts/paper_aslan_nas.py), iş akışı `paper_aslan_nas.yml` (her saat başından birkaç dakika sonra), kayıt `forward/paper_aslan_nas/` (`state.json`, `trades.csv`). Telegram'a "KÂĞIT Aslan Nasdaq" başlığıyla yeni sinyal, giriş, kapanış ve iptal mesajı gider (özel sohbet + seçili grup). Kurallar dondurulmuş: backtest'teki kodun aynısı (`sim.signals_v2` + `sim.replay`). Değerlendirme diğer botlarla 2026-11-30'da, sonra ayda bir.

**Backtest'ten farklar:**
- **Fiyat:** backtest HistData NAS100 CFD (endeks, sadece bid) idi; canlıda ücretsiz Yahoo **NQ=F** (Nasdaq-100 vadeli, sürekli ön ay) 1 saatlik mumları. Vadeli fiyat endeksten faiz farkı kadar (genelde %0.5-2) yukarıda; seviyeler hep aynı seriden hesaplandığı için kurallar aynı çalışır, ama rakamlar bir CFD ekranındaki rakamlarla bire bir aynı değildir.
- **Vade geçişi:** NQ=F her çeyrekte (Mart, Haziran, Eylül, Aralık) yeni kontrata geçer; o gün grafikte yapay bir sıçrama olur ve seviyeleri/stopları bozabilir. Vade haftalarındaki sinyaller raporda ayrıca işaretlenecek.
- **Seans:** günlük ve 4 saatlik mumlar yine New York 17:00 → 17:00 işlem gününe göre, ama 1 dakikalık değil 1 saatlik mumlardan kuruluyor. Vadelinin 17:00-18:00 arası ve hafta sonu da backtest'teki CFD ile aynı.
- **Geçmiş:** Yahoo en fazla ~2 yıl 1 saatlik veri veriyor (backtest 2020'den beri). Çok eski, hiç alınmamış uzak seviyeler eksik olabilir; yakın seviyeler aynı.
- **Gecikme:** iş her saatten birkaç dakika sonra çalışır; GitHub bazen gecikir. Emirler zaten bir sonraki mumdan itibaren geçerli olduğu için kurallar değişmez, ama mesaj birkaç dakika geç gelebilir.
- Maliyet backtest'teki gibi %0.010 gidiş-dönüş varsayılır. Funding/swap yok.

## Diğer endeksler (2026-11-05) — aynı kurallar, ayar yok
Denetçinin isteği: daha çok işlem için Nasdaq'ta geçen kural (v2 1h yön filtreli) aynen S&P 500, DAX, FTSE 100 ve Nikkei 225'te denendi (HistData; Dow verisi HistData'da yok). Masraf: S&P ve DAX %0.010, FTSE %0.015, Nikkei %0.025 (tipik CFD makası). Bu endeksler için kasa dönemi (2026-04 → 09) ilk kez kullanıldı. Ayrıntı: [results/2026-11-05_aslan_endeksler](../results/2026-11-05_aslan_endeksler/README.md), PR #57.

| Endeks | Geliştirme (net R, işlem) | Doğrulama | Kasa | Rastgeleden iyi mi? | Sonuç |
|---|---|---|---|---|---|
| Nasdaq (referans) | +0.07 (368) | +0.15 (107) | +0.15 (46) | üçünde de evet | GEÇTİ |
| S&P 500 | -0.04 (365) | -0.07 (108) | +0.07 (41) | sadece kasada | KALDI |
| DAX | +0.06 (339) | -0.08 (104) | +0.39 (19) | doğrulamada hayır | KALDI |
| FTSE 100 | -0.09 (409) | +0.01 (94) | -0.29 (44) | hiçbirinde | KALDI |
| Nikkei 225 | -0.08 (393) | +0.08 (83) | +0.03 (54) | geliştirmede hayır | KALDI |

- Dört endeksin hiçbiri geçmedi; hepsinde ayda ~6-7 işlem olurdu ama kenar yok.
- **Önemli uyarı:** S&P 500, Nasdaq'a en çok benzeyen piyasa (işlem günlerinin %56'sı ortak, günlük sonuç korelasyonu +0.48), ama orada kural geliştirme ve doğrulamada eksi. Gerçek bir kenar olsaydı S&P'de de görünmesi beklenirdi. Bu, Nasdaq sonucunun şans olma ihtimalini artırıyor. Nasdaq kağıt takibi sürüyor; karar 2026-11-30 ve sonrasındaki kağıt sonuçlarına göre.
- Kağıt takibine yeni endeks eklenmedi.
