# Kararlar

Her karar: tarih + karar + gerekçe. En yeni en üstte.

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
