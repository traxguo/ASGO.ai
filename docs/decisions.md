# Kararlar

Her karar: tarih + karar + gerekçe. En yeni en üstte.

## 2026-10-08 — "Önce günlük trend" stratejileri (mtf_trend) test edildi
- **Durum:** Proje sahibinin isteğiyle popüler fikirler günlük trend filtresiyle (günlük kapanış > / < günlük EMA50) denendi: Donchian kırılımı, RSI geri çekilme, Supertrend, sıkışma kırılımı ve en iyi adayın (DonchianATR) günlük trendli hali. Günlük veri (1d) indirme ve doğrulamaya eklendi.
- **Sonuç:** Sadece `MTFDonchian_B` geçen kısımlar gösterdi: geliştirmede +0.10R / PF 1.11 / DD %37, doğrulamada +0.10R / PF 1.09 / DD %16, 6 coinin 4'ü pozitif. Diğerleri aşama 2'de elendi.
- **Karar:** Hiçbir strateji active olmadı (PF < 1.2; geliştirme DD > %25). En iyi iki aday: `DonchianATR_B` (geliştirmede güçlü, doğrulamada zayıf) ve `MTFDonchian_B` (iki dönemde tutarlı ama zayıf, yüksek drawdown). Kasa kullanılmadı.
- **Not:** Drawdown büyük ölçüde işlem başına %1 risk ve aynı anda 5'e kadar açık işlemden geliyor; riski düşürmek drawdown'u kabaca orantılı küçültür, ama bu kurallarda (bölüm 10) değişiklik olur ve proje sahibinin kararıdır. Yapılmadı.

## 2026-10-08 — Seviye 1 strateji ailesi tamamlandı: active olacak strateji yok
- **Durum:** Brief'teki dört ailenin hepsi test edildi (trend_ma, donchian_breakout, rsi_reversion, üçünün ATR filtreli versiyonları). Hiçbiri aşama 1-4'ü eşiklerle geçemedi. En iyi aday `DonchianATR_B`: geliştirmede +0.16R / PF 1.22 / DD %17; doğrulamada +0.06R / PF 1.04 (eşik 1.2) / DD %13.5, 6 coinin 2'si pozitif (eşik %50).
- **Karar:** Hiçbir strateji `active/`'e alınmadı, kasa (holdout) kullanılmadı. Eşikler değiştirilmedi. Nasıl devam edileceği proje sahibine soruldu.
- **Gerekçe:** Kurallar ("kötü sonuç gizlenmez", eşikler) ve doğrulamadaki +0.06R'nin 88 işlemle sıfırdan ayırt edilememesi.

## 2026-10-08 — rsi_reversion lookahead uyarısı yanlış alarm sayıldı
- **Durum:** `lookahead-analysis` 45 işlemin 1'inde bias işaretledi (ETH 2023-08-30 04:00), gösterge sapması yoktu.
- **Kontrol:** Aynı strateji veri 04:00'te, 08:00'de ve 12:00'de kesilerek çalıştırıldı. Veri 08:00 ve 12:00'de kesilince işlem aynı fiyat ve stopla açıldı; 04:00'te kesilince hiç açılmadı, çünkü o mumun verisi yoktu. Gelecek veriye bakan bir hesap yok.
- **Karar:** Yanlış alarm; strateji zaten ilk backtest'te elendiği için ek önlem alınmadı.

## 2026-10-08 — TP model seçim kuralı (aşama 3)
- **Karar:** Sabit ızgaradan (16 kombinasyon; aynı sonucu veren modeller çıkınca 12) geliştirme verisinde **en yüksek ortalama R** seçilir. Hem donchian_breakout hem DonchianATR'de seçilen model varsayılan Model B oldu (varsayılandan sapma gerekmedi).

## 2026-10-04 — donchian_breakout ilk backtest: devam
- **Karar:** Aşama 3'e (TP model ızgarası, geliştirme verisi) devam.
- **Gerekçe:** Maliyet ve funding sonrası beklenti pozitif (B: +0.09R, 567 işlem, 6 coinin 4'ü pozitif). Drawdown (%38) ve PF (1.10) active eşiklerinin altında; aşama 4'te de böyle kalırsa bu kart değiştirilmez, filtreli yeni kart açılır veya emekli edilir. Rapor: `results/2026-10-04_donchian_breakout_ilk_backtest/rapor.md`.

## 2026-10-04 — Ortak modül düzeltmesi (Model A break even kontrolü)
- **Durum:** Model A'da girişten hemen sonraki ilk `custom_stoploss` çağrısında `max_rate/min_rate` henüz boştu ve hata veriyordu; o mumda planlanan stop kurulmuyordu.
- **Karar:** Boşsa giriş fiyatı kullanılıyor. trend_ma raporu yeniden üretildi (A net -19.5% → -18.6%); emeklilik kararı değişmedi. Model B etkilenmedi.

## 2026-10-04 — trend_ma emekliye ayrıldı
- **Karar (proje sahibi onayladı):** `trend_ma` emekliye ayrıldı (`strategies/retired/`), Seviye 1'deki diğer strateji ailelerine geçiliyor.
- **Gerekçe:** Geliştirme döneminde (2020-06 → 2024-12, 6 coin) iki TP modelinde de işlem başına -0.06R, profit factor 0.91-0.92, drawdown %43-47. Eşikler: PF ≥ 1.2, DD ≤ %25. Parametre veya yön ayarı geliştirme verisine uydurma olurdu. Rapor: `results/2026-10-04_trend_ma_ilk_backtest/rapor.md`.

## 2026-10-04 — Geliştirme / doğrulama / kasa tarih sınırları
- **Karar:** Geliştirme 2020-01-01 → 2024-12-31 (`--timerange 20200101-20250101`); doğrulama 2025-01-01 → 2026-03-31 (`20250101-20260401`); kasa (holdout) 2026-04-01 → 2026-09-30 (`20260401-20261001`).
- **Gerekçe:** Veri 2020-01'den 2026-09 sonuna kadar (arşivde ay bitince eklenir). Kasa = son 6 ay (kural). Kalan ~5 yılın son 15 ayı doğrulama, öncesi geliştirme: geliştirmede hem yükseliş (2020-21, 2023-24) hem düşüş (2022) piyasası var. Sınırlar sabit kalır; yeni ay verisi eklense de kaydırılmaz (kasa ileride tekrar kullanılırsa ayrıca karar yazılır).

## 2026-10-04 — Veri kaynağı: data.binance.vision arşivi
- **Durum:** Ağ izni açıldı ama `fapi.binance.com` / `api.binance.com` bu sunucuya HTTP 451 veriyor (Binance'in ülke engeli). `data.binance.vision` çalışıyor.
- **Karar:** Seviye 1 verisi (1h/4h futures OHLCV, 1h mark, funding) aylık arşivden indiriliyor (`FT_LOCAL=1 FT_OFFLINE=1 ./scripts/download_data.sh`). Aylık arşivde eksik günler (SOL ve XRP: 2022-02-26 → 28 ve 2022-04-01 → 02) günlük arşivden tamamlanıyor. Freqtrade market listesini API'den alamadığı için `scripts/offline_freqtrade.py` sabit liste veriyor (Binance tick/lot değerleri, 2026-10 itibarıyla, API'den doğrulanamadı; sadece yuvarlamayı etkiler).
- **Veri doğrulama düzeltmesi:** `validate.py` daha önce eksik mumları göremiyordu, çünkü Freqtrade okurken boşlukları sıfır hacimli mumla dolduruyor. Artık `fill_missing=False` ile okuyor.
- **Kalan uyarılar (gerçek piyasa olayları, düzeltilmedi):** her coinde 1 adet sıfır hacimli 1h mum; aşırı sıçramalar (ör. 2020-03-12 çöküşü, 2021 DOGE yükselişi).
- **Eski not:** Aşağıdaki "Binance verisine bu çalışma ortamından erişilemiyor" kararı bununla çözüldü.

## 2026-10-04 — Bot tek bir gruba da yazabilir (kural 7 değişti)
- **Karar:** Proje sahibi, botun arkadaşıyla olan bir gruba da yazmasını istedi. Kural 7 güncellendi: kişisel sohbet + `.env`'deki `TELEGRAM_GROUP_ID` ile seçilen **tek** grup. Kanal veya ikinci grup yok.
- **Nasıl:** Grup ID'si boşsa bot eskisi gibi sadece kişisel sohbete yazar. Grupta sadece `/` ile başlayan komutlara cevap verir (normal sohbete karışmaz). Başka gruplar yok sayılır. Seviye 3'te otomatik sinyaller de bu iki sohbete gidecek.
- **Not:** Grup üyeleri de sinyalleri görür; mesajlardaki "yatırım tavsiyesi değildir" uyarısı kalır.

## 2026-10-04 — Telegram botu Seviye 3'ten önce kuruldu (sadece altyapı)
- **Karar:** Proje sahibinin isteğiyle Telegram botu şimdi kuruldu: deneme mesajı, `/durum`, `/liste` ve coin sorgusu (`btc'ye bak`). Otomatik sinyal gönderimi **açılmadı**; o Seviye 3'te, testi geçen strateji çıkınca açılır.
- **Seviye atlama sayılmaz çünkü:** Bot hiçbir seviye (alım/stop/TP) üretmez. Coin sorgusu sadece (1) güncel fiyat ve 24s değişim ("sadece bilgi" etiketiyle), (2) aktif strateji listesi, (3) `signals/log/`'daki kayıtlı son sinyali olduğu gibi gösterir. Aktif strateji yoksa bunu açıkça söyler.
- **Güvenlik:** Bot sadece `.env`'deki `TELEGRAM_CHAT_ID`'ye yazar; başka sohbete gönderme kodda engelli. Grup/kanal ID'leri (negatif sayılar) reddedilir. Başka sohbetlerden gelen mesajlara cevap verilmez. Token sadece `.env`'de.
- **Çalışma yeri:** Bulut oturumu geçici olduğu için uygun değil. Öneri: küçük bir VPS (Seviye 3'te Freqtrade dry-run da 7/24 orada çalışacak). Denemek için proje sahibinin bilgisayarı da olur.
- **Teknik:** Ek kütüphane yok (Python standart kütüphanesi, long polling, açık port yok). Docker servisi: `telegram-bot`.

## 2026-10-04 — Binance verisine bu çalışma ortamından erişilemiyor
- **Durum:** Bu oturumun çalıştığı bulut ortamının ağ politikası `fapi.binance.com`, `api.binance.com` ve `data.binance.vision` adreslerini engelliyor (HTTP 403, proxy reddi). Brief'teki yedek yol (data.binance.vision arşivi) da engelli. Docker daemon da bu ortamda başlatılamıyor.
- **Karar:** Veri indirme ve doğrulama araçları yazıldı ama gerçek veri indirilemedi. Sistem, **sentetik (rastgele üretilmiş) veri** ve çevrimdışı market listesiyle uçtan uca test edildi (`tests/smoke/`). Bu testin rakamları araştırma sonucu değildir ve `results/` klasörüne konmadı.
- **Çözüm yolları:** (a) Proje ortamının ağ ayarlarında bu üç adrese izin vermek, (b) veriyi proje sahibinin bilgisayarında `./scripts/download_data.sh` ile indirmek. İkisinden biri olunca ilk gerçek backtest yapılacak.

## 2026-10-04 — Repo düzeni
- **Karar:** Brief'teki `quant-lab/` yapısı doğrudan repo köküne kuruldu (ayrı alt klasör yok). Her ana klasörde ne olduğunu anlatan Türkçe bir `README.md` var.
- **Gerekçe:** Proje sahibinin isteği; klasörleri GitHub'da Türkçe açıklamalarıyla gezebilmek ve strateji kartlarını elle kontrol edebilmek.

## 2026-10-04 — Seviye 1 coin listesi
- **Karar:** BTC, ETH, SOL, XRP, BNB, DOGE (USDT perpetual).
- **Gerekçe:** Binance USDⓈ-M'de genelde en yüksek hacimli ve en uzun geçmişe sahip pariteler. **Not:** Bu seçim genel bilgiye dayanıyor; canlı hacim verisi erişim engeli nedeniyle doğrulanamadı. Veri erişimi açılınca son 90 günlük hacimle kontrol edilecek, gerekirse güncellenecek.

## 2026-10-04 — Maliyet varsayımı
- **Karar:** Emir başına %0.1 (taker %0.05 + kayma %0.05), `config/base.json` → `fee: 0.001`. Kısmi çıkışlar ayrı emir olarak ücretlendirilir (Freqtrade böyle yapar).
- **Gerekçe:** Brief bölüm 9. Binance'in güncel futures taker ücreti (VIP0, %0.05) bilinen değer; erişim engeli yüzünden canlı ücret sayfası doğrulanamadı.

## 2026-10-04 — İşlem yönetiminin Freqtrade'de uygulanış şekli
- **Giriş:** Giriş bölgesinin **ortasına** limit emir. R da bölge ortasından ölçüldüğü için sonuçlar R'de tutarlı. Emir `valid_for_candles` mum (varsayılan 3) içinde dolmazsa iptal; dolmadan fiyat stop'a değerse iptal (`check_entry_timeout`).
- **Stop:** `custom_stoploss` ile planlanan seviyeye mutlak olarak konur. Varsayılan kural: ATR stop (1.5 ATR) ile yapısal stop (son 10 mum dibi/tepesi ± 0.1 ATR) arasından **daha geniş** olanı.
- **TP'ler:** `adjust_trade_position` ile TP1 (kısmi) ve TP2 seviyelerinde bekleyen limit emirler. Model B'de TP1 dolunca stop girişe (+%0.15 tampon: komisyon ve funding için) çekilir. Model A'da fiyat 2R'ye ulaşınca stop girişe çekilir.
- **Aynı mum belirsizliği:** Backtest'te stop ve hedef aynı mumun içindeyse **stop önce** sayılır (kötümser). Model A'da 2R'ye değip aynı mumda geri dönen fiyat da break even ile kapanmış sayılır. İleride `--timeframe-detail 5m` ile daha hassas test planlanabilir.
- **Pozisyon büyüklüğü:** Stop olursa sermayenin %1'i kaybedilecek şekilde. Yeterli serbest teminat yoksa işlem açılmaz (farklı riskle işleme girilmez).
- **Kaldıraç:** 3x'ten başlar; likidasyon tahmini stop mesafesinin 2 katından yakınsa 2x, 1x'e düşer; 1x de yetmezse sinyal üretilmez. Stop fiyatın %8'inden uzaksa sinyal üretilmez.
- **R hesabı:** Planlanan stop işlemin `enter_tag` alanında saklanır (`long stop=...`), rapor scripti R'yi buradan kesin hesaplar.
- **Açık nokta (Seviye 3'te doğrulanacak):** Canlı dry-run'da bekleyen TP limit emri varken stop'un nasıl tetiklendiği Freqtrade'in canlı modunda ayrıca test edilmeli.

## 2026-10-04 — trend_ma için ısınma süresi
- **Karar:** `startup_candle_count = 1000`.
- **Gerekçe:** `recursive-analysis` EMA200'ün 250 mumla ~%2 saptığını, 1000 mumla ~%0 saptığını gösterdi (sentetik veriyle; gerçek veriyle tekrar edilecek).

## 2026-10-09 — Pusula 2. tur: sabit TP yerine trend çıkışı test edildi
- **Karar:** `PusulaTrend` ve `PusulaTrendLong` sabit TP kullanmıyor: işlem, günlük kapanış EMA(20)'nin aleyhine geçince kapanır; stop aynı, 2R'de girişe çekilir. Aynı anda en fazla 3 açık işlem (`--max-open-trades 3`).
- **Gerekçe:** Brief 7.5 "takip eden stop gibi alternatif kurallar test edilebilir, testten geçmeden kullanılmaz". Proje sahibi "teste devam, açıkları kapat" dedi. İlk turda kazananlar ortalama 13 gün sürüyordu, sabit 2R/4R onları erken kesiyordu.
- **Sonuç:** Geliştirmede aynı girişlerle +0.11R → +0.43R (long+short) / +0.83R (sadece long). Doğrulamada +0.16R / +0.28R. Ayrıntı: `cards/pusula.md`.
- **Not:** Sinyal mesajında TP1/TP2 yerine "trend bozulunca çıkış" yazacak. Bu, brief bölüm 7.3'teki iki TP'li yapıdan bir sapmadır; strateji "active" olmadan önce proje sahibinin onayı gerekir.

## 2026-10-10 — Pusula kasa testi
- **Sonuç:** PusulaTrendLong (16 coin) kasa döneminde -0.02R, DD %6.2, 15 işlem. Geçme şartı > 0R olduğu için geçemedi; "active" olmadı.
- **Karar:** Kurallar kasa sonucuna göre değiştirilmeyecek. Strateji `candidates/` altında kalıyor. 2020-01 → 2026-09 verisinin tamamı artık görüldü; bu stratejiyi yargılamanın tek temiz yolu yeni (ileriye dönük) veri.

## 2026-10-10 — Kalabalık (funding tersine) yan strateji
- **Sonuç:** Önceden sabitlenen tek varyant `Kalabalik_B` geliştirmede eşikleri geçti (+0.28R, DD %9.3, 123 işlem) ve doğrulamada da artıda (+0.29R, 26 işlem, hepsi long).
- **Kasa (bir kez):** +0.05R, 13 işlem, DD %4.1. Eşiği kâğıt üstünde geçti ama başa baş. Dayanıklılık: komşular, masraf x2 ve hile testi geçti.
- **Karar:** "active" yapılmıyor, `candidates/` altında kalıyor, kurallar değişmiyor. 2026-04..09 kasasında ikinci strateji de başa baş: bu dönemde iki farklı fikir de kazanamadı. Yargı ileriye dönük kağıt takiple (aylık, funding arşivi ay sonunda çıkıyor).

## 2026-10-10 — Binance demo hesabında işlem (proje sahibi kararı)
- **Karar:** Proje sahibi Pusula'yı Binance demo hesabında (demo.binance.com, oyun parası) takip etmek istedi ("şart") ve "hiç emir yok" kuralının kaldırılmasına onay verdi. Uygulanan: sadece `config/demo.json` dry_run'ı kapatabilir, o da `exchange.demo_trading: true` ile. Başlatma yalnızca `scripts/demo_freqtrade.py` ile; program tüm Binance API adreslerinin `demo-*` olduğunu kontrol etmeden başlamaz. Anahtarlar sadece proje sahibinin bilgisayarındaki `.env` dosyasında.
- **Gerçek para:** Proje sahibi kuralın "hepten" kaldırılmasını istedi. Gerçek hesapta işlem açmak bu değişiklikle hâlâ mümkün değil. Bu ayrı ve geri alınamaz bir adım; demo sonuçları görülmeden ve strateji "active" olmadan yapılmaması önerildi.
- **Not:** Binance demo ayrı bir piyasadır (kendi emir defteri); sonuçlar kağıt takipten biraz farklı çıkabilir. Bulut ortamı Binance'e (demo dahil) bağlanamadığı için bot proje sahibinin bilgisayarında çalışır.

## 2026-10-10 — Bilgisayardan bağımsız demo: GitHub sunucusunda Bitget demo (proje sahibi kararı)
- **İstek:** Proje sahibi botun kendi bilgisayarından bağımsız, ücretsiz ve kart istemeyen bir sunucuda çalışmasını istedi. Demo işlemler kağıt takip gibi analiz edilip sistem geliştirilmeye devam edecek. Kart isteyen seçenekleri (Oracle, ücretli VPS) reddetti.
- **Ölçüm:** GitHub'ın ücretsiz sunucuları (ABD) Binance ve Binance demo'ya (451), Bybit demo'ya (403) bağlanamıyor. Bitget ve OKX açık. Kraken'in demo futures'ı kapanmış görünüyor.
- **Karar:** Proje sahibi karar kartında "Evet, Bitget" seçti. `scripts/bitget_demo.py` + `.github/workflows/bitget_demo.yml` her 4 saatlik mum kapanışından sonra GitHub'ın ücretsiz sunucusunda bir kez çalışır. PusulaV2'nin kendi kodunu Bitget'in gerçek piyasa mumlarında çalıştırır ve Bitget **demo** hesabında emir verir. Stop emri girişle birlikte borsaya konur. Kayıtlar `forward/bitget_demo/` altına yazılır ve projeye kaydedilir.
- **Güvenlik:** Anahtarlar sadece GitHub Secrets'ta. Program `PAPTRADING: 1` demo başlığını taşımayan hiçbir imzalı isteği göndermez. Demo anahtarı gerçek hesapta çalışmaz. Gerçek para hâlâ kapalı.
- **Farklar (analizde hesaba katılır):** Çıkışlar piyasa emriyle yapılır. Stopun girişe çekilmesi en fazla 4 saat gecikebilir. Bitget demo fiyatları gerçek piyasadan biraz farklı olabilir.

## 2026-10-10 — Telegram komutları Cloudflare Workers'ta (proje sahibi kararı)
- Karar: Telegram komutları (/durum, /gecmis, /fiyat, /kapat) ücretsiz Cloudflare Workers'ta çalışır, cevap anında gelir. Pusula'nın işlem mesajları 4 saatlik GitHub botundan gider.
- Gerekçe: GitHub'ın ücretsiz süresi (ayda 2.000 dakika) sık komut kontrolüne yetmiyor; Cloudflare kart istemiyor. Proje sahibi karar kartında "Cloudflare"ı seçti.
- Sınırlar: Bot sadece sahibin özel sohbetine cevap verir. Sadece Bitget demo hesabına bağlanır (her istekte `paptrading: 1`). `/kapat` sadece demo işlemini kapatır. Bot seviye üretmez.

## 2026-10-10 — Telegram hesap komutları GitHub üzerinden cevaplanır
- Karar: Cloudflare botu sadece kimin sorduğunu kontrol eder ve yardım mesajını kendisi verir. /durum, /gecmis, /fiyat ve /kapat komutlarını GitHub'daki "Telegram komutu" işine iletir. O iş Bitget demo hesabına sorup cevabı Telegram'a yollar (yaklaşık 30 saniye).
- Gerekçe: Bitget, Cloudflare sunucularından gelen istekleri engelliyor (HTTP 403, Cloudflare block). GitHub sunucularına ise cevap veriyor. Her komut yaklaşık yarım dakika GitHub süresi harcıyor, aylık 2.000 dakika buna yetiyor.
- Sınırlar: Bitget anahtarları artık Cloudflare'de tutulmaz, sadece GitHub Secrets'ta durur. GitHub anahtarı (GH_DISPATCH_TOKEN) sadece bu depoda ve sadece "Actions" iznine sahiptir. Demo başlığı (`paptrading: 1`) her istekte zorunludur. /kapat'ı sadece sahip kullanabilir.

## 2026-10-10 — Gerçek paraya "hazırız" şartları (proje sahibi kararı)
- Karar: Demo hesapta **1 ay** çalıştıktan sonra (2026-11-10 civarı) Claude net bir karar raporu verir: "hazırız" ya da "hazır değiliz, neden". "Hazırız" demek için şunlar gerekir: komisyon ve funding sonrası ortalama sonuç artıda olacak, en büyük düşüş testlerdeki sınırı aşmayacak, demodaki dolum fiyatları beklenene yakın olacak ve işlem sayısı karar vermeye yetecek (hedef ≥ 30). İşlem sayısı yetmezse karar "henüz erken" olur ve süre uzar.
- Gerekçe: Proje sahibi 3 ayı uzun buldu, 1 ay istedi. Not: Pusula ayda yaklaşık 3 işlem açıyor; 1 ayda tek başına 30 işleme ulaşamaz. Bu yüzden daha sık işlem açan bir yan strateji (kuyruk 1b) bu süreyi kısaltmanın asıl yolu.
- Sınırlar: "Hazırız" kararından sonra bile gerçek para ayrı ve açık bir sahip onayı ister, çok küçük tutarla başlar. Geliştirme turları ekleme kadar kural çıkarmayı da dener.

## 2026-10-11 — Üç scalp stratejisi emekli, Pusula turu günde 1 (proje sahibi kararı)
- Karar: SFP sweep, FVG+OB ve VWAP+EMA20 `strategies/retired/` altına alındı. Otomatik Pusula geliştirme turu 6 saatte birden günde bire (İstanbul 09:13) indirildi.
- Gerekçe: Üçü de masrafsız bile eksi. Aslan'ın "bu kadar kötü olması normal değil" itirazı üzerine SFP, Freqtrade kullanmadan sıfırdan yazılmış ayrı bir simülasyonla BTC 2022-2024'te yeniden ölçüldü: masrafsız -0.05/-0.07R, Freqtrade sonucuyla aynı → uygulama hatası yok. Asıl sorun aritmetik: 5m'de stop ~%0.3, gidiş-dönüş masraf %0.2 → işlem başına ~0.6R masraf. Tur sıklığı kullanım hakkını korumak için azaltıldı.
- Ders: Yeni hızlı strateji arayışında stop mesafesi en az ~%1 olmalı (masraf ≤ 0.2R) ya da beklenen kazanç masraftan belirgin büyük olmalı.

## 2026-10-11 — Dalga demoya ikinci bot olarak ekleniyor (proje sahibi kararı)
- Karar: Dalga (1h, 36 coin, 8 yuva, değişken risk) Bitget demo hesabında Pusula'nın yanında saatlik çalışır (`.github/workflows/bitget_demo_dalga.yml`, `DEMO_BOT=dalga`). Bir bot diğerinin tuttuğu coine girmez. Pusula'nın kuralları değişmedi.
- Gerekçe: Pusula'nın kendi test ettiği coinlerde ve dönemde (2020-01 → 2026-09, 3 yuva) Dalga her iki listede daha fazla toplam R ve daha düşük düşüş verdi: eski 16 coin Dalga 402 işlem toplam 337.8R DD %16.6 / Pusula V2NoBe 230 işlem 311.3R DD %23.7; yeni 20 coin Dalga 409 işlem 469.3R DD %20.0 / Pusula 193 işlem 117.7R DD %22.6. Proje sahibi "Dalga Pusula'yı geçiyorsa hemen demoya ekle" dedi.
- Not: İkisi aynı aileden (aynı rejim ve çıkış), işlemleri çoğunlukla aynı yönde; birlikte çalışınca toplam risk artar. Bir ay sonra (2026-11-10 civarı) ikisi ayrı ayrı değerlendirilir. Değişken riskin "kasa zirvesi" ortak demo hesabının bakiyesine göre hesaplanır.

## 2026-10-11 — Kıvılcım: testi geçmeyen kısa işlem kuralı demoda DENEME olarak çalışıyor
- **Karar:** Proje sahibi sabah demoda günde ~3 işleme girip birkaç saatte çıkan bir bot görmek istedi. Gece denenen hiçbir kısa işlem kuralı maliyetten sonra artı çıkmadı. En az kötü olan (güçlü trendde 1h geri çekilme, 1.5 ATR stop/hedef, 3 saat; doğrulama -0.12R) "Kıvılcım - DENEME" adıyla Bitget demoya eklendi: işlem başı %0.2 risk, en fazla 2 açık, günde en fazla 3 yeni işlem. İşlem mesajları sahibin sohbetine ve seçtiği gruba gider (üç bot için de grup eklendi).
- **Gerekçe:** Demo parası gerçek değil; amaç kısa işlem altyapısını (piyasa emri, borsada kâr al + stop, süre dolunca kapatma) canlıda çalışır görmek ve gerçek dolum verisi toplamak. Kural sinyal olarak yayınlanmaz ve gerçek paraya aday değildir; kartında testi geçmediği yazılı. Pusula ve Dalga'nın kuralları değişmedi.

## 2026-10-12 — Demo botlarını Cloudflare saati başlatıyor (proje sahibi onayı)
- **Karar:** Cloudflare Telegram botuna (telegram_worker) 15 dakikalık bir saat eklendi; her turda zamanı gelen demo işlerini GitHub'da başlatır: Kıvılcım her 15 dakikada, Dalga her saat başı, Pusula 4 saatte bir. GitHub'ın kendi zamanlayıcıları yedek olarak kalıyor.
- **Gerekçe:** GitHub'ın zamanlayıcısı turların çoğunu atladı (2026-10-11: Dalga 3 saat hiç çalışmadı, Kıvılcım hiç başlamadı, Pusula düzensiz). Cloudflare saati ücretsiz ve dakikasında çalışır; mevcut GH_DISPATCH_TOKEN ile sadece iş başlatır, demo dışına çıkamaz.

## 2026-10-12 — Kıvılcım demoda 81 coinlik listeye geçti
- Karar: Kıvılcım DENEME botu `config/pairs_kivilcim76.json` (81 coinlik test listesi eksi Bitget'in hiç listelemediği 5 coin) ile çalışır; Dalga ve Pusula test edildikleri listede kalır.
- Gerekçe: Bitget demo hesabında 36 coinin sadece 15'i işlem görüyor (log: "demo contracts: 15/36"). Kıvılcım'ın geliştirme testi zaten 81 coinle yapıldı. Proje sahibi demoda gerçekten işlem görmek istiyor (gerçek para yok; 2026-10-12 kararı: demoda kalınacak).

## 2026-10-12 — Kıvılcım emekliye ayrıldı, demodan kaldırıldı
- Karar: Kıvılcım DENEME botu durduruldu; kod `strategies/retired/kivilcim.py`, GitHub iş akışı silindi, Cloudflare saati artık sadece Dalga ve Pusula'yı başlatıyor.
- Gerekçe: proje sahibi "emekli et" dedi ve "Kapat" seçti. Kural iki dönemde de zararda, brüt avantajı yok. Aynı gün denenen yeni kısa işlem fikirleri (saat etkisi, BTC öncülüğü, onay mumu, Kinetik Geri Çekilme) da masrafı karşılamadı.

## 2026-10-12 — Tasfiye kasa testinde başarısız, demoya çıkmıyor
- Karar: Tasfiye (OI tasfiye sonrası long, 3 saat) demoya konmayacak; kart "kasa testinde başarısız".
- Gerekçe: geliştirme ve doğrulamada artıdaydı, ama dokunulmamış kasa döneminde (2026-04..09) dondurulmuş kural zararda (18-33 işlem, -0.6..-1.6% işlem başı). Kural kasaya göre değiştirilmez.

## 2026-10-12 — Fitil Avcısı kasa testini geçti, demoya hazırlanıyor
- Karar: Fitil Avcısı (derin limit emirle panik fitili yakalama, 3 saat) aday oldu; sıradaki adım Bitget demo (gerçek para yok).
- Gerekçe: geliştirme, hiç bakılmamış 45 coin, doğrulama ve bir kez kullanılan kasa döneminde artıda. Çöküş koruması doğrulama görüldükten sonra eklendi (kartta yazılı). Kazanç birkaç sert güne bağlı; demo dolumları gerçekçilik açısından ölçülecek.
