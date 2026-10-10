# Yol haritası

Seviyeler sırayla ilerler. Bir seviyenin çıkış şartı sağlanmadan sonrakine geçilmez.

**Şu anki seviye: 1 — Sabit liste** (son güncelleme: 2026-10-04)

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
0. (2026-10-10) Pusula (`PusulaTrendLong`, donduruldu) ileriye dönük kağıt takipte: `research/forward/pusula_paper.py`, rapor `forward/pusula_kagit.md`, her pazartesi güncellenir. Yan strateji Kalabalık (funding tersine) geliştirme + doğrulamayı geçti, kasada başa baş (+0.05R); aylık kağıt takibe alınacak. Sıradaki yan fikir: güçlü/zayıf coin sepeti.
1. (2026-10-09) Pusula 2. tur: `PusulaTrend` ve `PusulaTrendLong` geliştirme ve doğrulamayı büyük ölçüde geçti (`cards/pusula.md`). Proje sahibi kasa testine girecek versiyonu seçecek; kasa testi geçerse Seviye 1 çıkış şartı sağlanır.
