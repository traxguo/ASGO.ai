# ASGO.ai — Kripto Futures Strateji Araştırma ve Sinyal Sistemi

Binance USDⓈ-M perpetual futures piyasasında **long ve short** stratejileri bilimsel bir test hattından geçiren bir araştırma sistemi. Son aşamada testi geçen stratejiler canlı piyasayı izler ve proje sahibine kişisel Telegram'dan **"giriş bölgesi / stop / TP1-TP2"** sinyali gönderir.

> **Bu sistem gerçek işlem yapmaz.** Sadece geçmiş veride test (backtest) ve canlı veride sanal işlem (dry-run) yapar. Elle işleme girip girmemek her zaman proje sahibinin kararıdır.

Projenin tam tarifi: [PROJECT_BRIEF.md](PROJECT_BRIEF.md). Değişmez kurallar: [docs/rules.md](docs/rules.md).

## Şu an neredeyiz?

**Seviye 0 (Altyapı).** Ayrıntı ve sıradaki işler: [docs/roadmap.md](docs/roadmap.md). Son çalışma günlüğü: [journal/](journal/).

## Klasörler (her birinin içinde Türkçe bir README var)

| Klasör | Ne var? |
|---|---|
| [`cards/`](cards/) | **Strateji kartları.** Her stratejinin ne yaptığı, neye baktığı, hangi koşullarla girdiği. Strateji eklemek/çıkarmak buradan başlar. |
| [`strategies/`](strategies/) | Stratejilerin kodu. `candidates/` (test ediliyor), `active/` (testi geçti), `retired/` (elendi, gerekçesiyle saklanır), `common/` (hepsinin kullandığı ortak işlem yönetimi). |
| [`config/`](config/) | Ayarlar: `base.json` (her zaman `dry_run: true`), coin listeleri. |
| [`signals/`](signals/) | Sinyal sistemi: veri yapısı, Türkçe açıklama şablonları, görsel, Telegram gönderici, sinyal kayıtları. |
| [`research/`](research/) | Veri indirme ve doğrulama, dayanıklılık testleri, coin evreni. |
| [`results/`](results/) | Her testin Türkçe raporu (`rapor.md`). Kötü sonuçlar da silinmez. |
| [`journal/`](journal/) | Her çalışma gününün günlüğü: ne yapıldı, ne bulundu, sırada ne var. |
| [`docs/`](docs/) | Kurallar, kararlar, geçme eşikleri, yol haritası. |
| [`manual_trades/`](manual_trades/) | Senin sinyallere göre elle yaptığın işlemlerin kaydı. |
| [`scripts/`](scripts/) | Yardımcı komutlar: güvenlik kontrolü, veri indirme, rapor üretme. |
| [`tests/`](tests/) | Kodun doğru çalıştığını kontrol eden testler. |

## Nasıl çalıştırılır? (teknik)

Gereken: Docker. Tüm Freqtrade komutları `scripts/ft.sh` üzerinden çalışır; bu script her seferinde önce güvenlik kontrolünü (`scripts/safety_check.py`) çalıştırır.

```bash
docker compose build                       # bir kere
./scripts/download_data.sh                 # Seviye 1 verisini indir + doğrula
FT_STRATEGY_DIR=strategies/retired ./scripts/ft.sh backtesting --strategy-list TrendMA_A TrendMA_B --timeframe 4h --timerange 20200101-20250101   # örnek: emekli trend_ma
python scripts/make_report.py --test ilk_backtest   # results/ altına Türkçe rapor
```

Docker yerine yerel kurulum için: `pip install -r requirements.txt` ve komutların başına `FT_LOCAL=1` ekle.
