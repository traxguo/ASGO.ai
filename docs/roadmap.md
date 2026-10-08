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
1. Seviye 1'deki dört aile test edildi (2026-10-08), hiçbiri eşikleri geçmedi; en iyi aday `DonchianATR_B` doğrulamada zayıf (PF 1.04). Proje sahibinin nasıl devam edileceğine kararı bekleniyor (`decisions.md`).
2. Elenen stratejilerin kodu `strategies/retired/`'e taşınacak (`atr_filtered.py` diğerlerini içe aktardığı için birlikte, karar sonrası).
3. Seviye 1 coin listesini son 90 günlük hacimle kontrol et (arşivdeki hacim verisiyle).
