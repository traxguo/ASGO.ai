# vwap_reversion — VWAP/EMA20'den aşırı uzaklaşan fiyatın geri dönüşü (5m)

Kod: [`strategies/candidates/vwap_reversion.py`](../strategies/candidates/vwap_reversion.py)

**Bu kart ilk backtest'ten ÖNCE yazıldı (2026-10-11).** Koşullar, parametreler, varyantlar ve ilk eleme şartı test öncesi sabitlendi; sonuca bakıp değiştirilmez.

## Hipotez
Proje sahibinin (GUO) getirdiği "ortalamaya dönüş" fikri. Fiyat gün içinde hem günlük VWAP'ın hem de EMA20'nin belirgin şekilde altına (üstüne) sarkar ve RSI aşırı satım (alım) bölgesine girerse, ardından gelen bir dönüş mumu (pinbar, yutan mum, sabah/akşam yıldızı) fiyatın ortalamaya (önce EMA20, sonra VWAP) doğru geri dönmesinin başlangıcı olabilir.

Bu test **ilk elemedir**: "bu fikir bir şansı hak ediyor mu?" sorusuna cevap arar. Sadece geliştirme verisi (2022-2024) kullanılır.

## Yön
ikisi de (long ve short ayrı raporlanır)

## Zaman dilimi notu
Kaynak 3 dakikalık grafik istiyor. Binance vadeli için elimizde 3m veri yok (data.binance.vision'da 3m vadeli mum arşivi bu projede indirilmedi; Freqtrade backtest'i de 5m ile hazır). **Test 5m ile yapılır.** Bu bir yaklaşıklıktır; 3m'de sonuç farklı olabilir.

## Göstergeler (5m, kapanmış mum)
- `vwap`: günlük oturum VWAP'ı. Her UTC günü 00:00'da sıfırlanır. `vwap = Σ(tipik fiyat × hacim) / Σ(hacim)`, tipik fiyat = (high + low + close) / 3, toplam o günün 00:00 mumundan bu muma kadar (bu mum dahil).
- `ema20`: kapanışların 20'lik üssel ortalaması.
- `rsi14`: 14'lük RSI (Wilder ortalaması).
- Mum ölçüleri: `body = |close - open|`, `range = high - low`, `lower_wick = min(open, close) - low`, `upper_wick = high - max(open, close)`.

## Giriş koşulları (test öncesi sabitlendi, 2026-10-11)
Sinyal mumu = dönüş mumu (i). Long için ikisi de doğru olmalı:

- [stretched_down] Teknik: (mum i VEYA mum i-1, `close < vwap` ve `close < ema20` ile kapandı) VE (mum i, i-1, i-2'den en az birinde `rsi14 < 30`). | Açıklama: "Fiyat günlük VWAP'ın ({vwap}) ve EMA20'nin ({ema20}) altına sarktı, RSI 30'un altına indi ({rsi_min})."
- [bullish_reversal] Teknik: aşağıdaki üç mum kalıbından en az biri mum i'de oluştu: | Açıklama: "Dönüş mumu oluştu: {pattern}."
  - [pinbar_bull] alt fitil ≥ 2 × gövde, kapanış mumun üst yarısında (`close ≥ (high + low)/2`), `range > 0` ve alt fitil > 0. (Renk şartı yok.) | "Uzun alt fitilli mum (pinbar)."
  - [engulfing_bull] mum i-1 kırmızı (`close < open`), mum i yeşil, `close_i ≥ open_{i-1}`, `open_i ≤ close_{i-1}` ve gövde_i > gövde_{i-1}. | "Yutan boğa mumu."
  - [morning_star] mum i-2 kırmızı ve gövdesi kendi boyunun en az yarısı; mum i-1 küçük gövdeli (gövde ≤ 0.3 × gövde_{i-2}); mum i yeşil ve `close_i ≥ (open_{i-2} + close_{i-2})/2`. Kripto 7/24 işlem gördüğü için kaynaktaki "boşluk (gap)" şartı aranmaz. | "Sabah yıldızı (3 mum)."

Short (aynası):
- [stretched_up] Teknik: (mum i VEYA i-1, `close > vwap` ve `close > ema20`) VE (i, i-1, i-2'den en az birinde `rsi14 > 70`). | Açıklama: "Fiyat günlük VWAP'ın ({vwap}) ve EMA20'nin ({ema20}) üstüne taştı, RSI 70'in üstüne çıktı ({rsi_max})."
- [bearish_reversal] Teknik: [pinbar_bear] üst fitil ≥ 2 × gövde ve kapanış alt yarıda; [engulfing_bear] i-1 yeşil, i kırmızı, `close_i ≤ open_{i-1}`, `open_i ≥ close_{i-1}`, gövde_i > gövde_{i-1}; [evening_star] i-2 yeşil (gövde ≥ yarı boy), i-1 gövde ≤ 0.3 × gövde_{i-2}, i kırmızı ve `close_i ≤ (open_{i-2}+close_{i-2})/2`. | Açıklama: "Dönüş mumu oluştu: {pattern}."

Plan şartları (sinyal üretilmesi için, ikisi de):
- [targets_ok] Her iki hedef (EMA20 ve VWAP, sinyal mumundaki değerleri) girişin kâr tarafında ve girişten en az **0.3R** uzakta. Biri yanlış tarafta veya 0.3R'den yakınsa işlem yok. | "Hedefler: EMA20 {tp1}, VWAP {tp2}."
- [size_ok] 1R risk için gereken pozisyon 10x kaldıraçla açılabiliyor (aşağıda). Açılamıyorsa işlem yok.

## İşlem yönetimi
Ortak modülün (`strategies/common/freqtrade_mixin.py`, `ManagedStrategy`) iskeletini kullanır (limit giriş, TP emirleri, kısmi çıkış, stop'u başa çekme, pozisyon boyu), ama seviyeler bu kartın kurallarından gelir (ortak modülün ATR bölgesi ve R-katlı TP'leri kullanılmaz; TP'ler 1R'den küçük olabilir — proje kuralıyla çelişki aşağıda varyant olarak ölçülür).

- **Giriş:** dönüş mumunun kapanış fiyatına **limit emir**. Freqtrade sinyal mumu kapandıktan sonra emri bir sonraki mumun açılışında verir; emir **1 mum** geçerlidir (sonraki mum içinde dolmazsa iptal; fiyat dolmadan stop'a değerse de iptal). Kripto 5m'de bir sonraki açılış neredeyse hep kapanışa eşit olduğu için bu "kapanışta giriş" kuralına en yakın dürüst karşılıktır.
- **Stop:** long: son 10 mumun (sinyal mumu dahil) en düşük dibi × (1 − 0.0005). Short: son 10 mumun en yüksek tepesi × (1 + 0.0005). 1R = |giriş − stop|.
- **TP1 (%50):** EMA20'nin sinyal mumundaki değeri. TP1 dolunca kalan yarının stop'u **tam giriş fiyatına** çekilir (kaynakta "başa baş"; ortak modülün %0.15 tamponu kullanılmaz).
- **TP2 (kalan %50):** VWAP'ın sinyal mumundaki değeri.
- **Hedef sırası:** TP1 = EMA20, TP2 = VWAP. VWAP EMA20'den daha yakınsa (önce o gelir) sıra değişir: TP1 = yakın olan (VWAP), TP2 = uzak olan (EMA20). Bu durumun kaç işlemde olduğu raporlanır. (Önceden kararlaştırıldı: yarım çıkış her zaman ilk ulaşılan hedefte.)
- TP'ler mum içinde dinlenen limit emirlerdir. Aynı mumda stop ve hedef görülürse Freqtrade önce stop'u sayar (kötümser).
- Başka çıkış yok (süre sınırı, çıkış sinyali yok).
- **Risk:** işlem başına kasanın %1'i (stop olursa kayıp = kasanın %1'i + masraf). Pozisyon = kasa × %1 / stop mesafesi (%).
- **Kaldıraç:** tasfiye fiyatı stop mesafesinin en az 2 katı uzakta olacak şekilde en yüksek tam sayı kaldıraç, **en fazla 10x** (GUO'nun kuralı; proje kuralı `docs/rules.md` en fazla 3x diyor — bu çelişki not edilir; 3x'i aşan işlem sayısı raporlanır). Gereken pozisyon 10x ile serbest kasaya sığmıyorsa (stop çok dar, ≈ %0.1'den az) işlem atlanır; risk sessizce küçültülmez.
- **En fazla 1 açık işlem** (tüm coinler toplamı). Aynı mumda birden çok coinde sinyal varsa Freqtrade listedeki sıraya göre ilkini alır (bu yüzden sıralama testi yapılır).
- **3 kayıp kuralı:** art arda 3 kaybeden işlem (net kâr < 0, masraf + funding dahil; TP1 alıp başa başta kapanan işlem net sonucuna göre sayılır) olursa 3. kaybın kapanışından itibaren **24 saat** yeni işlem açılmaz. Duraklama sonrası sayaç sıfırdan başlar. `confirm_trade_entry` içinde uygulanır.
- Sinyal geçerlilik süresi: 1 mum.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Not |
|---|---|---|
| Zaman dilimi | 5m | kaynak 3m (veri yok) |
| VWAP | günlük, UTC 00:00 sıfırlama | sabit |
| EMA | 20 | sabit |
| RSI | 14, eşik 30 / 70 | sabit |
| Uzama penceresi | kapanış: i veya i-1; RSI: i..i-2 | sabit |
| Pinbar fitil/gövde | ≥ 2 | sabit |
| Sabah/akşam yıldızı | ilk mum gövde ≥ 0.5 boy, orta gövde ≤ 0.3 × ilk gövde, son kapanış ilk gövdenin ortasını geçer | sabit |
| Stop | son 10 mum uç + %0.05 tampon | sabit |
| En yakın hedef | ≥ 0.3R | sabit |
| Risk | %1 | sabit |
| Kaldıraç sınırı | 10x (tasfiye ≥ 2 × stop) | sabit |
| En fazla açık işlem | 1 | sabit |
| 3 kayıp duraklaması | 24 saat | sabit |
| Başlangıç kasası | 10000 USDT | sabit |

## Varyantlar (önceden belirlendi, en fazla 2; karar sadece ana sürüme göre)
- `VwapReversion`: ana sürüm, karar buna göre.
- `VwapReversionTp1R`: aynı, ama ilk hedef (TP1) girişten en az **1R** uzakta olmalı (projenin "TP1 ≥ 1R" kuralı, `CLAUDE.md`). Bu kuralın kaç sinyali eleyeceği ve sonuca etkisi raporlanır. Teşhis.

## Test planı (önceden)
- Ana evren: BTC, ETH, SOL (USDT vadeli), 5m, en fazla 1 açık işlem, kasa 10000, maliyet emir başına %0.1 (%0.05 komisyon + %0.05 kayma; kısmi çıkış ayrı emir), funding geçmiş veriden.
- Önce hile testi (lookahead-analysis), 3 coin, kısa dönem.
- Geliştirme 2022-01-01 → 2024-12-31 (`--timerange 20220101-20250101`). Doğrulama (2025+) ve kasa (2026-04+) bu turda YAPILMAZ.
- Koşular: (1) ana, normal masraf `--fee 0.001`; (2) masraf x2 `--fee 0.002`; (3) düşük masraf / limit emir borsası `--fee 0.0003` (teşhis); (4) masrafsız `--fee 0` (teşhis); (5) dayanıklılık: 16 coin (`config/pairs_wide16.json`) 1 yuva ve 16 yuva (teşhis); (6) sıralama testi: ana koşu, coin sırası ters (SOL, ETH, BTC).
- Raporda: R (masraf + funding dahil), long/short ayrı, yıl yıl, coin coin, günde işlem, al-tut kıyası.
- **İlk eleme şartı ("şansı hak ediyor mu")**, normal masrafla, ana sürüm, BTC/ETH/SOL: ortalama R > 0, PF ≥ 1.1, max DD ≤ %35, coinlerin en az yarısı artıda (≥ 2/3), 3 yılın en az 2'sinde artı. GUO'nun hedefi günde ~3 işlem; günde işlem sayısı dürüstçe raporlanır (şart değil).
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Durum: candidate (2026-10-11, test öncesi)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
