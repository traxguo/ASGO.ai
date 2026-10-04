# Kararlar

Her karar: tarih + karar + gerekçe. En yeni en üstte.

## 2026-10-04 — Botta isteğe bağlı yapay zekâ sohbeti
- **Karar:** Proje sahibinin isteğiyle bota serbest sohbet eklendi (Google Gemini API ücretsiz katmanı, `.env`'de `AI_API_KEY` varsa açılır).
- **Kural 1.3 ve 7.9 ile uyum:** Yapay zekâ seviye veya gerekçe üretmez. Komut cevapları ve coin raporu şablondan, olduğu gibi gelir; yapay zekâ en fazla altına "💬" ile kısa bir sohbet cümlesi ekler. Sadece sistemin verdiği bilgileri (durum, sıradaki işler, coin raporu) görür. Cevapta bu bilgilerde olmayan 3+ basamaklı bir sayı varsa cevap atılır.
- **Grupta:** sadece `/sor` ve botun mesajına verilen yanıtlar. Normal grup sohbetine karışmaz.
- **Gizlilik:** Ücretsiz katmanda mesajlar Google tarafından ürün geliştirme için kullanılabilir; kişisel bilgi yazılmamalı.
- **Doğrulanmadı:** Varsayılan model adı (`gemini-2.5-flash`) bu ortamdan anahtarsız denenemedi; gerekirse `.env`'de `AI_MODEL` ile değiştirilir.

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
