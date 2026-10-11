# fvg_ob — 15 dk MSS + Order Block + 3 dk FVG geri dönüşü (limit emir)

Kod: [`strategies/candidates/fvg_ob.py`](../strategies/candidates/fvg_ob.py)

**Bu kart 2026-10-11'de, hiçbir backtest çalıştırılmadan önce yazıldı.** Koşullar, parametreler, varyant ve geçme şartı sonuçlara bakmadan sabitlendi.

## Hipotez
Proje sahibinin (GUO) getirdiği SMC/ICT fikri. 15 dakikalıkta fiyat son onaylı tepenin üstünde **gövdeyle** kapanırsa (yapı kırılımı, MSS) alıcılar kontrolü almıştır. Bu hareketi başlatan son ters renkli 15 dk mumu (Order Block, OB) kurumsal emirlerin bölgesidir. Hareket sırasında 3 dakikalıkta OB bölgesinin içinde bir boşluk (FVG) kalmışsa, fiyatın düşük hacimle bu boşluğa geri dönmesi iyi bir giriş verir; hedef karşı taraftaki likidite (en yakın alınmamış 15 dk tepe). Short tarafı aynası.

Bu test **ilk elemedir** ("bu fikir bir şansı hak ediyor mu?"). Sadece geliştirme verisi (2022-01-01 → 2024-12-31).

Aslan'ın stratejileriyle ilişkisi: Aslan'ın likidite alımı → MSS → FVG kuralları (`cards/aslan_liquidity.md`, `cards/ams_liquidity_mss.md`) 26+ varyantta denendi, masraf öncesi ~0R çıktı. Bu strateji aynı aileden ama farklı: likidite alımı (sweep) şartı **yok**; giriş bölgesi OB ile çakışan FVG'nin **ortası**; hacim şartı var; hedef sabit R değil, karşı taraftaki 15 dk likidite (en az 2R); giriş 3 dakikalıkta. Fraktal tanımı (`pivots`, iki yanda 2 mum) Aslan kodundan alındı.

## Yön
İkisi de (long ve short ayrı raporlanır).

## Tanımlar
- **Giriş zaman dilimi:** 3 dk (ana). 3 dk mumlar data.binance.vision 1 dk mumlarından üretildi (1 dk → 3 dk birleştirme, sola etiketli).
- **15 dk mumlar:** strateji içinde 3 dk mumlardan üretilir (5 adet 3 dk mum = 1 adet 15 dk mum; eksik grup kullanılmaz). Bir 15 dk mum ancak son 3 dk mumu (xx:12, :27, :42, :57) kapandığında görülür → geleceği görme yok.
- **15 dk swing (fraktal):** solundaki 2 ve sağındaki 2 mumdan yüksek tepe / alçak dip. Sağdaki 2 mum kapanınca onaylanır.
- **MSS (long):** bir 15 dk mumun **kapanışı**, en son onaylanmış 15 dk swing tepesinin üstünde. Her swing tepesi bir kez kırılır (kullanıldı sayılır). Daha önceki trendin düşüş olması şartı aranmaz (kaynak tanımı: "son onaylı swing'in gövdeyle kırılması"). Short: kapanış en son onaylı swing dibinin altında.
- **Hareketin başlangıcı (long):** kırılan swing tepesinden sonra MSS mumuna kadar (MSS dahil) en düşük dibi yapan 15 dk mum.
- **Order Block (long):** bu başlangıç mumunda veya ondan önce (kırılan tepeden sonra) oluşan **son kırmızı** (kapanış < açılış) 15 dk mum. OB bölgesi = o mumun dibi–tepesi (iğneler dahil). Kırmızı mum yoksa kurulum yok. Short: son yeşil mum.
- **Genişleme (expansion) mumları:** OB'den sonraki ilk 3 dk mumdan MSS 15 dk mumunun son 3 dk mumuna kadarki 3 dk mumlar.
- **FVG (long, 3 dk):** üç ardışık 3 dk mumda 3. mumun dibi > 1. mumun tepesi; boşluk = [1. mumun tepesi, 3. mumun dibi]. Üç mum da OB mumunun açılışı ile MSS mumunun kapanışı arasında olmalı ve boşluk OB bölgesiyle **kesişmeli**. Birden fazla varsa en yenisi. Short: 3. mumun tepesi < 1. mumun dibi.
- **Karşı likidite (long hedef):** son 400 adet 15 dk mum içinde, oluştuktan sonra fiyatın hiç üstüne çıkmadığı (alınmamış) **en yeni** onaylı 15 dk swing tepesi. Short: alınmamış en yeni swing dibi.

## Giriş koşulları (MSS 15 dk mumunun kapandığı 3 dk mumda kontrol edilir)
Long (hepsi):
- [mss_up_15m] Teknik: 15 dk kapanış > en son onaylı 15 dk swing tepesi (ilk kırılım) | Açıklama: "15 dakikalıkta fiyat son tepenin ({swing_high}) üstünde gövdeyle kapandı (yapı kırılımı)."
- [order_block] Teknik: hareketten önceki son kırmızı 15 dk mum bulundu | Açıklama: "Yükselişi başlatan son kırmızı 15 dk mum (Order Block): {ob_low}–{ob_high}."
- [fvg_in_ob] Teknik: genişleme sırasında OB bölgesiyle kesişen yukarı yönlü 3 dk FVG var ve sinyal anına kadar fiyat giriş seviyesine geri dönmemiş | Açıklama: "3 dakikalıkta Order Block içinde boşluk (FVG) kaldı: {fvg_low}–{fvg_high}."
- [rr_ge_2] Teknik: (hedef − giriş) / (giriş − stop) ≥ 2 ve stop < giriş < hedef | Açıklama: "Hedef karşı taraftaki likidite ({tp}); kazanç/risk oranı {rr}."

Short: aynası (MSS aşağı, son yeşil 15 dk mum OB, aşağı yönlü FVG, hedef alınmamış en yeni swing dibi).

Giriş anındaki ek koşul (emir dolarken kontrol edilir):
- [pullback_volume_lower] Teknik: geri çekilme mumlarının ortalama hacmi < genişleme mumlarının ortalama hacmi. Geri çekilme mumları = genişlemenin başından beri görülen en yüksek tepeden (short: en düşük dipten) sonraki, **kapanmış** 3 dk mumlar, emrin dolduğu mumdan önceki muma kadar. En az 1 kapanmış geri çekilme mumu gerekir. Şart sağlanmıyorsa o mumda emir dolmaz (canlıda: her mum kapanışında şart bozuksa emir geri çekilir, sağlanınca tekrar konur) | Açıklama: "Fiyat düşük hacimle geri çekildi (geri çekilme ort. hacmi {pb_vol} < hareket ort. hacmi {exp_vol})."

## İşlem yönetimi
**Ortak modülden (`strategies/common/`) sadece şunlar kullanılır:** %1 risk ile pozisyon büyüklüğü, güvenli kaldıraç hesabı (likidasyon stopun en az 2 katı uzakta), planın sinyal mumundan okunması. Giriş fiyatı, stop ve hedef bu kartın kurallarıdır (ortak modülün ATR bölgesi ve A/B TP modelleri kullanılmaz).
- **Giriş (ana sürüm `FvgOb`):** FVG'nin **%50 seviyesine** limit emir. Sinyal mumundan sonraki 3 dk mumun açılışında konur, **20 adet 3 dk mum (60 dk)** geçerli. Fiyat emir dolmadan hedefe değerse (bir 3 dk mumun tepesi hedefe ulaşırsa) emir iptal edilir (bir sonraki mumun başında; aynı mumda hem giriş hem hedef görülürse işlem açılmış sayılır ve o mumda hedef sayılmaz — kötümser).
- **Limit dolum kuralı (iyimser dolumlara karşı):** Freqtrade limit emri fiyat sadece değince doldurur. Burada limit emir (giriş ve hedef) ancak fiyat seviyenin **en az %0.02 ötesine (ve en az 1 tick)** geçerse dolar; dolum fiyatı limit fiyatın kendisidir. (`strategies/retired/kirilim1s_limit.py`'deki `fill_through_pct` yaklaşımı; burada sadece dolum kuralı alınır, masraf modeli alınmaz.)
- **Stop:** OB'nin uç noktasının %0.05 ötesi (long: OB dibi × 0.9995; short: OB tepesi × 1.0005). Piyasa emri, mum içinde kontrol edilir. Break even yok.
- **Hedef:** tek hedef = karşı likidite (yukarıdaki tanım), dinlenen limit emir; kısmi çıkış yok. Giriş mumunda hedef sayılmaz (sıralama belirsiz), stop sayılır (kötümser). Aynı mumda hem stop hem hedef: önce stop.
- **R:** 1R = |giriş − stop|. İşlem sonucu R = net kâr (masraf + funding dahil) / (miktar × |giriş − stop|).
- **Risk:** işlem başına kasanın **%1**'i (pozisyon = kasa × %1 / stop mesafesi). Kaldıraç gerektiği kadar, **en fazla 10x** (GUO'nun bu aile için genel kuralı; `docs/rules.md`'deki 3x sınırının bilinçli istisnası, sadece bu ilk eleme için). Likidasyon stopun en az 2 katı uzakta olmalı. 10x ile %1 risk sağlanamıyorsa (stop çok dar, yaklaşık < %0.1) sinyal atlanır.
- **Aynı anda en fazla 1 pozisyon** (`--max-open-trades 1`). Bekleyen limit emir de yuvayı tutar.
- **3 kayıp kuralı:** üst üste 3 zararlı işlemden (net kâr < 0) sonra, 3. işlemin kapanışından itibaren **24 saat** yeni işlem yok; sonra sayaç sıfırlanır. Tüm coinler için ortak.
- **Masraf:** emir başına %0.1 (komisyon + kayma, `--fee 0.001`), limit emirler dahil her emre aynı oran (kötümser). Funding geçmiş veriden.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Not |
|---|---|---|
| Giriş zaman dilimi | 3m | 1m sadece teşhis (`--timeframe-detail 1m`, mum içi sıra) |
| Yapı zaman dilimi | 15m (3m'den) | |
| Fraktal | 2 mum sol / 2 mum sağ | Aslan/AMS koduyla aynı |
| Hedef swing arama penceresi | 400 adet 15 dk mum | |
| Giriş | FVG %50 | varyant: FVG kenarı |
| Emir geçerliliği | 20 adet 3 dk mum | |
| Stop tamponu | %0.05 | |
| En düşük R/R | 2 | |
| Dolum için fiyatın geçmesi | %0.02 (≥ 1 tick) | |
| Risk | %1 | |
| Kaldıraç tavanı | 10x | |
| En fazla açık işlem | 1 | |
| 3 kayıp → bekleme | 24 saat | |

## Varyantlar (önceden belirlendi; karar sadece ana sürüme göre)
- `FvgOb`: ana sürüm, FVG %50 seviyesine limit.
- `FvgObEdge`: FVG'nin **yakın kenarına** limit (fiyatın geri dönüşte ilk değdiği kenar: long'da boşluğun üstü = 3. mumun dibi, short'ta boşluğun altı = 3. mumun tepesi). Diğer her şey aynı. Teşhis.

## Test planı (önceden)
- Coinler: BTC, ETH, SOL (USDT perpetual). 3m mum. Kasa 10000 USDT. Dönem `--timerange 20220101-20250101` (ısınma için veri 2021-12'den).
- Önce hile testi (lookahead-analysis, 3 coin, kısa dönem).
- Koşular: (1) ana, normal masraf `--fee 0.001`; (2) masraf x2 `--fee 0.002`; (3) düşük masraf `--fee 0.0003` (teşhis); (4) masrafsız `--fee 0` (teşhis); (5) coin sırası testi: ana koşu, coin listesi ters sırada; (6) mum içi sıra teşhisi: ana koşu `--timeframe-detail 1m`; (7) `FvgObEdge` normal masraf.
- Dayanıklılık 16 coinde (wide16) **yapılmaz**: 1m/3m veri sadece BTC/ETH/SOL için indirildi (görev tanımı: wide16 sadece 5m'ye düşülürse).
- **İlk eleme şartı** (normal masraf, ana sürüm): ortalama R > 0, PF ≥ 1.1, max DD ≤ %35, coinlerin en az yarısı (≥ 2/3) artıda, 3 yılın en az 2'sinde artı. GUO'nun hedefi günde ~3 işlem; günlük işlem sayısı dürüstçe raporlanır.
- Doğrulama (2025+) ve kasa (2026-04+) bu turda kullanılmaz. Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Yaklaşımlar / sınırlar (Freqtrade'de birebir mümkün olmayanlar)
- Hacim şartı ve "fiyatın geçmesi" dolum kuralı backtest motorunda emir dolum kontrolüne eklenen küçük bir sarmalayıcıyla uygulanır (sadece bu stratejide etkilidir). Dry-run'da hacim şartı her mum kapanışında emri geri çekme/yeniden koyma olarak uygulanmalıdır (bu turda dry-run yok).
- 3 dk mum içindeki sıra bilinmez: aynı mumda hem giriş hem hedef → işlem açılır, hedef o mumda sayılmaz; stop sayılır. 1 dk detaylı koşu bunun etkisini ölçer.
- `FvgObLookahead` sınıfı varyant değildir; sadece Freqtrade lookahead-analysis aracı için (araç kasayı 1 milyar yaptığından %1 riskli boyut borsa sınırını aşıyor; aynı sinyaller, sabit boyut). Test sonrası eklendi, kurallara dokunmaz.
- Bekleyen emir yuvayı tuttuğu için, tek yuvayla başka bir coinin sinyali kaçabilir (gerçek tek-pozisyon kuralıyla aynı).

## Durum: candidate — ilk elemede başarısız, emeklilik önerildi (2026-10-11)
Normal masrafla -0.95R, masrafsız bile -0.20R; her yıl, her coin, iki yön de eksi. Emekliye ayırma kararı proje sahibinin; kod şimdilik `strategies/candidates/` altında.

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-11 | Hile testi: kendi kesme testi (3 coin × 15 kesim × 2 mod) + Freqtrade lookahead-analysis (`FvgObLookahead`, 2023-01 → 02, 30 işlem) | Sinyal sütunlarında fark yok. Standart araç limit dolumlarını "bias" sayıyor (18/30); kontrol verisi dolumdan 2 mum sonra bitince (`research/robustness/lookahead_limit_fill.py`) 0/30, geleceği görme yok. | — |
| 2026-10-11 | Geliştirme 2022-2024, BTC/ETH/SOL, 3m, 1 pozisyon, normal masraf | 1011 işlem (günde 0.92), kazanan %17.5, **-0.946R**, PF 0.37, DD %100 (hesap 2022'de sıfırlandı). Long -1.033R, short -0.867R. 0/3 coin, 0/3 yıl artı. Ortanca stop %0.31, masraf 0.73R/işlem. Al-tut +%34.5. **İlk eleme: hiçbir şart tutmadı.** | `results/2026-10-11_fvg_ob_gelistirme/rapor.md` |
| 2026-10-11 | Masraf x2 / %0.03 / masrafsız (teşhis) | -1.641R / -0.389R / **-0.198R** (PF 0.73). Masrafsız da her yıl ve her coinde eksi. | aynı rapor |
| 2026-10-11 | Ters coin sırası; 1 dk detaylı mum içi sıra (teşhis) | -0.914R; -0.936R. Sıra etkisi yok. | aynı rapor |
| 2026-10-11 | `FvgObEdge` (FVG yakın kenarı) | 993 işlem, -0.801R, PF 0.45, DD %100. | aynı rapor |

## Notlar / öğrenilenler
- Kural günde ~12 sinyal üretiyor (3 coin); tek pozisyon, 60 dk bekleyen emir ve 3 kayıp → 24 saat mola yüzünden günde ~1 işlem alınıyor.
- Kazanma oranı %18; masrafsız başa baş ~%23 (kazanan +3.4R, kaybeden -1R). FVG ortasına dönen fiyat çoğu zaman OB'nin ötesine (stopa) de gidiyor.
- Dar stop (ortanca %0.31) yüzünden %0.2 masraf işlem başına ~0.73R.
- Aslan/AMS ailesiyle uyumlu: masraf öncesi avantaj yok (orada ~0R, burada -0.20R).

## Emeklilik gerekçesi (varsa)
