# Yol haritası

Seviyeler sırayla ilerler. Bir seviyenin çıkış şartı sağlanmadan sonrakine geçilmez.

**Şu anki seviye: 1 — Sabit liste** (son güncelleme: 2026-11-10)

> **2026-11-10 yön değişikliği:** proje tek piyasaya, Nasdaq'a (US100, long + short, XM) odaklandı. Kripto demo botları durdu, kripto kâğıt takipleri 2026-11-30'a kadar sürüyor, yeni kripto fikri aranmıyor. Güncel plan: `docs/nasdaq_plan.md`. Aşağıdaki kripto seviyeleri geçmiş kayıt olarak duruyor.

## Seviye 0 — Altyapı
- [x] Repo yapısı, `.gitignore`, `.env.example`
- [x] `scripts/safety_check.py` ve `scripts/ft.sh` (her Freqtrade komutundan önce güvenlik kontrolü)
- [x] Docker kurulumu (`Dockerfile`, `docker-compose.yml`)
- [x] Hafıza dosyaları (`CLAUDE.md`, `docs/`, `journal/`)
- [x] Ortak işlem yönetimi modülü (`strategies/common/`, Model A ve B) + `signals/schema.py`
- [x] Örnek strateji (`trend_ma`) + kartı
- [x] Rapor üretici (`scripts/make_report.py`) ve veri doğrulama (`research/data/validate.py`)
- [x] Uçtan uca boru hattı testi (sentetik veriyle; lookahead/recursive analizleri dahil)
- [x] Gerçek veriyi indir (OHLCV 1h/4h + funding + mark, 2020-01 → 2026-09) ve doğrula (data.binance.vision arşivi, bkz. `decisions.md`)
- [x] Gerçek veriyle `trend_ma` Model A vs B ilk backtest + rapor (`results/2026-10-04_trend_ma_ilk_backtest/`)
- [x] Geliştirme / doğrulama / kasa tarih sınırlarını belirle (`decisions.md`)

Seviye 0 çıkış şartı sağlandı (2026-10-04).

**Çıkış şartı:** Tek komutla veri indirilip, bir strateji bölüm 7'deki yönetimle (Model A ve B) test edilip, rapor üretilebiliyor.

## Seviye 1 — Sabit liste: "Bu strateji çalışıyor mu?"
- Coin listesi: BTC, ETH, SOL, XRP, BNB, DOGE (`config/pairs_level1.json`)
- Strateji ailesi: trend takibi, kırılım (Donchian), ortalamaya dönüş (RSI), ATR volatilite filtreli versiyonlar
- TP model seçimi (sabit ızgara), doğrulama, dayanıklılık araçları (walk-forward, ±%20, Monte Carlo)

**Çıkış şartı:** En az bir strateji test hattının 1-6. aşamalarını geçmiş ve `active/` klasöründe.

## Seviye 2 — Dinamik evren
- Hacme göre dönemsel coin listeleri (hayatta kalma yanılgısına karşı o tarihteki veriden)
- Aktif stratejiler bu evrende yeniden test edilir

**Çıkış şartı:** Aktif strateji(ler) dinamik evrende de eşikleri geçiyor.

## Seviye 3 — Canlı tarayıcı ve metin sinyalleri
- [x] Telegram botu altyapısı (erken kuruldu, sinyal göndermez; bkz. `decisions.md` 2026-10-04)
- Freqtrade dry-run, sinyal servisi, Telegram mesajları + Türkçe açıklamalar, kill switch, elle işlem kaydı, haftalık rapor
- Proje sahibinden gerekecek: Telegram bot token ve kişisel chat ID (`.env`) — adımlar `signals/dispatcher/README.md`

**Çıkış şartı:** Mesajlar eksiksiz ve doğru; dry-run sonuçları backtest beklentisiyle tutarlı.

## Seviye 4 — Görsel sinyaller
- Tasarım proje sahibiyle belirlenir, renderer yazılır

**Çıkış şartı:** Her giriş sinyali tasarıma uygun görselle birkaç saniye içinde geliyor.

## Sıradaki adım
00. (2026-11-10) Nasdaq planı: `docs/nasdaq_plan.md`. Önce saat (Cloudflare) ve XM koşulları, sonra en fazla 3 ön kayıtlı fikir. Aslan Nasdaq kâğıt takibi sürüyor (değerlendirme 2026-11-30).
0a. (2026-10-10) Hızlı adaylar `Nabiz`, `Kirilim1s`, `PusulaHizli` geliştirme döneminde elendi (en iyisi günde 0.6 işlem, +0.06R, DD %48; masraf avantajın yarısını yiyor). Sıradaki hızlı aday: limit emirli (maker) giriş ile masrafı düşürmek (kuyruk 1c). 1 aylık demo sonrası (≈2026-11-10) "hazır mıyız" raporu (`docs/decisions.md`).
0. (2026-10-10) Pusula (`PusulaTrendLong`, donduruldu) ileriye dönük kağıt takipte: `research/forward/pusula_paper.py`, rapor `forward/pusula_kagit.md`, her pazartesi güncellenir. Yan strateji Kalabalık (funding tersine) geliştirme + doğrulamayı geçti, kasada başa baş (+0.05R); aylık kağıt takibe alınacak. Sıradaki yan fikir: güçlü/zayıf coin sepeti.
1. (2026-10-09) Pusula 2. tur: `PusulaTrend` ve `PusulaTrendLong` geliştirme ve doğrulamayı büyük ölçüde geçti (`cards/pusula.md`). Proje sahibi kasa testine girecek versiyonu seçecek; kasa testi geçerse Seviye 1 çıkış şartı sağlanır.
- (2026-11-04) Silinen coin kontrolü: Fitil Avcısı sağlam (doğrulama +%0.5/işlem, eskiden +%1.3 sanılıyordu); Derin Fitil kırılgan (geliştirme -%39, LUNA). Rapor `results/2026-11-04_fitil_pit/rapor.md`. Botlar değişmedi.
- (2026-11-05) Portföy testi: geçen 5 strateji tek kasada, kurallar donuk. Üç dönemde artı (masraf x2 dahil), ama sabit %0.5 riskte düşüş -%21..-%60. Rapor `results/2026-11-05_portfoy/rapor.md`.
- (2026-11-06) ASGO Portföy sistemi: risk %0.25 (doğrulama düşüşü -%12.0), 180 gün coin yaşı kuralı eklenmedi (geliştirmede kötüleştirdi). Kâğıt takip `forward/paper_portfoy/` saatlik, panelin en üst çizgisi. Rapor `results/2026-11-06_portfoy_sistem/rapor.md`.
- (2026-11-09) Coin fikir paketi: 8 yeni günlük fikir (long+short) ön kayıtla test edildi, 0/8 geçti; kâğıt takip yok. Volatilite kırılımının görünen kârı ileriye bakma hatasıydı. İzlenecek (aday değil): aşırı düşüş günü al, funding aşırılığı short. Rapor `results/2026-11-09_coin_batch/README.md`, kart `cards/coin_paketi.md`.
- (2026-11-09) Endeks + forex fikir paketi: 8 bilinen fikir (NAS/SPX/DAX, EUR/USD, GBP/USD, altın; long+short) ön kayıtla test edildi, 0/15 yön geçti; kâğıt takip yok. En yakın RSI(2) long rastgele long girişten ayırt edilemedi (p 0.16). HistData DAX verisi 2020-06 → 2023-11 bozuk (başka endeks). Rapor `results/2026-11-09_endeks_forex_batch/README.md`, kart `cards/endeks_forex_paketi.md`.
- (2026-11-04) Market-nötr long+short: 6 fikirden 5'i elendi; "Yeni Coin Short" (yeni coini 1 hafta sonra sat + BTC al, 30 gün) zayıf aday: geliştirme +%109, doğrulama +%32, düşüş %22-27 (`cards/yeni_coin_short_btc_hedge.md`, `results/2026-11-04_market_notr/rapor.md`). Kasa yok (aile kasayı gördü); kâğıt takipte, değerlendirme 2026-11-30.
