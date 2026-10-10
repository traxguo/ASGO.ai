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

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | 20 yeni coin (hiç görülmemiş), 2020-01 → 2026-09 | Long +0.44R (150), DD %24.7, 9/20 coin artıda, en iyi 10 işlem dışında eksi. Long+short +0.27R (short +0.12R). | `results/2026-10-10_pusula_yeni20coin/rapor.md` |
| 2026-10-09 | Birim testleri (rejim puanı sadece geçmiş veriyi kullanıyor) + ilk backtest (geliştirme 2020-03 → 2024-12) | Pusula_B +0.08R, PF 1.07, DD %35.0, 269 işlem (long +21.3R, short -0.1R). Kârın tamamı 2020 long'ları; 2021-2024 ≈ -1.6R. BTC filtresiz: +0.06R, DD %38.2. Geçemedi; doğrulamaya bakılmadı. | [results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme](../results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme/rapor.md) |
| 2026-10-09 | 2. tur geliştirme (en fazla 3 işlem) | **PusulaTrend** +0.43R, PF 1.40, DD %31.0, 214 işlem (long +109.5R her yıl artıda, short -17.8R). Aynı girişlerle sabit TP: +0.11R. 5 işlemle +0.49R DD %33.7. Maliyet x2: +0.39R. Hile testi temiz. | [tur2_gelistirme_max3](../results/2026-10-09_PusulaTrend_Pusula_B_tur2_gelistirme_max3/rapor.md) |
| 2026-10-09 | PusulaTrendLong (sonradan eklendi) geliştirme + ±%20 | +0.83R, PF 1.87, DD %20.2, 132 işlem. 8 parametre komşusunun hepsi +0.72R ile +1.45R. | [sadece_long](../results/2026-10-09_PusulaTrendLong_tur2_gelistirme_sadece_long/rapor.md), [dayanıklılık](../results/2026-10-09_pusula_trend_long_dayaniklilik/parametre_komsulari.md) |
| 2026-10-09 | **Doğrulama, bir kez** (2025-01 → 2026-03) | PusulaTrend +0.16R, PF 1.27, DD %12.7, 64 işlem (short +0.04R). PusulaTrendLong +0.28R, PF 1.50, DD %7.7, 31 işlem. Al-tut -%40. | [tur2_dogrulama](../results/2026-10-09_PusulaTrend_PusulaTrendLong_tur2_dogrulama/rapor.md) |
| 2026-10-10 | **Kasa, bir kez** (2026-04 → 2026-09, 16 coin, en fazla 3 işlem) | PusulaTrendLong -0.02R, PF 0.94, DD %6.2, 15 işlem (3 işlem dönem sonunda kârda açıktı). Long+short -0.07R. 6 coin -0.68R. Al-tut +%15.9. Geçemedi (> 0R şartı). | [kasa_16coin](../results/2026-10-10_pusula_kasa_16coin/rapor.md), [kasa_6coin_bilgi](../results/2026-10-10_pusula_kasa_6coin_bilgi/rapor.md) |

## Notlar / öğrenilenler
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
