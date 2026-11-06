# BTC + ETH zaman serisi momentumu (trend takibi) — volatilite hedefli, long + short

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı, 2026-11-06)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı ve sonradan değiştirilmez.

**Fikir:** Klasik "zaman serisi momentumu": fiyat son N günde yükseldiyse long, düştüyse short.
Pozisyon büyüklüğü, coinin son 30 günlük oynaklığına göre ayarlanır (sakin piyasada büyük, fırtınalı piyasada küçük).

**Veri:** Binance USDⓈ-M perpetual, BTCUSDT ve ETHUSDT, günlük mumlar (`user_data/data/binance/futures/*-1d-futures.feather`,
kaynağı data.binance.vision) ve gerçek funding geçmişi (`user_data/data/binance_vision_raw/fundingRate/`, data.binance.vision
`futures/um/monthly/fundingRate/`). Veri yüklenirken 2026-04-01 ve sonrası kesilir; kasa (holdout) hiç okunmaz.

**Dönemler:** geliştirme 2020-01-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31.
Geliştirme ölçümü, en uzun bakış süresinin (120 gün) ısınması bittikten sonra, tüm ayarlar için aynı gün olan **2020-05-01**'den başlar.
Doğrulama dönemindeki sinyaller, önceki günlerin (geliştirme dönemi dahil) fiyatlarını kullanabilir; bu ileriye bakma değildir.

**Kurallar (her coin için ayrı):**
- Sinyal (bir önceki kapanışla hesaplanır, ileriye bakma yok):
  - `ret`: son N günlük getiri > 0 ise long (+1), < 0 ise short (−1).
  - `sma`: kapanış > SMA(N) ise long, < ise short.
- Boyut: hedef yıllık oynaklık / (30 günlük gerçekleşmiş oynaklık; günlük log getirilerin std'si × √365), en fazla 3x kaldıraç.
- Portföy: BTC ve ETH eşit ağırlık (sermayenin yarısı her birine; her yarının kaldıracı en fazla 3x).
- Her gün kapanışta hedef ağırlığa yeniden dengelenir.
- Maliyet: işlem gören nominalin %0.1'i (komisyon + kayma). Funding: gerçek oranlar, pozisyon yönüne göre ödenir/alınır
  (o günün tuttuğu pozisyona 08:00, 16:00 ve ertesi 00:00 UTC funding'leri yazılır).

**Izgara (12 ayar):** bakış N ∈ {20, 60, 120} gün × sinyal ∈ {ret, sma} × hedef oynaklık ∈ {%20, %40}.

**Kontroller:**
- (a) Karıştırılmış veri: geliştirme dönemi günlük getirileri (ve funding'leri) 20 günlük bloklar halinde karıştırılır
  (BTC ve ETH aynı permütasyonla, aralarındaki ilişki korunur), 200 tekrar; gerçek Sharpe'ın bu dağılımdaki yüzdeliği raporlanır.
- (b) Al-tut: BTC, ETH ve 50/50 (1x long perp, funding dahil).
- (c) 2x maliyet (%0.2) çalıştırması.

**Raporlanacaklar (her ayar, geliştirme ve doğrulama):** CAGR, max drawdown, Sharpe (günlük net getiri, √365),
işlem/yıl (yön değişimi sayısı), long günlerinin ve short günlerinin P&L katkısı ayrı ayrı (günlük net katkıların toplamı, sermayenin yüzdesi).

**Geçme çıtası (bir ayarın geçmesi için hepsi gerekli):**
1. Net Sharpe > 0 hem geliştirmede hem doğrulamada.
2. Short tarafının P&L'i tek başına pozitif hem geliştirmede hem doğrulamada.
3. Geliştirmede gerçek Sharpe, karıştırılmış verinin 90. yüzdeliğinin üstünde.
4. 2x maliyette net Sharpe > 0 hem geliştirmede hem doğrulamada.

**Izgara dayanıklılığı:** 12 ayardan kaçının geçtiği raporlanır. Tek bir ayarın geçmesi, komşuları geçmiyorsa "şans olabilir" diye not edilir.
Kötü sonuç gizlenmez; hiçbir ayar geçmezse bu açıkça yazılır.

---

## 2. Sonuç (ön kayıttan sonra hesaplandı)

**Kısa cevap: 12 ayardan hiçbiri geçmedi (0/12).** Hepsini düşüren aynı kural: **short tarafı geliştirme döneminde (2020-05 → 2024) kendi başına para kaybettiriyor.**
Long tarafı güçlü; trend takibi bu iki coinde aslında "yükselişte long kal, düşüşte küçül/çık" olarak işe yarıyor, short ise geliştirmede yük.

Çalıştırma: `/home/user/ftenv/bin/python -I research/tsmom/tsmom.py` ve `research/tsmom/extras.py`. Veri 2020-01-01 → 2026-03-31 (2282 gün, eksik gün yok); 2026-04-01 ve sonrası yüklenmedi.

### 12 ayar (geliştirme = 2020-05-01 → 2024-12-31, doğrulama = 2025-01-01 → 2026-03-31)
Long/short P&L: o yöndeki günlerin günlük net katkılarının toplamı (sermayenin oranı, maliyet + funding dahil). "Karışık %": gerçek geliştirme Sharpe'ının 200 karıştırılmış veri çalıştırmasındaki yüzdeliği.

| Ayar | Gel. CAGR | Gel. MaxDD | Gel. Sharpe | Gel. işlem/yıl | Gel. long | Gel. short | Doğ. CAGR | Doğ. MaxDD | Doğ. Sharpe | Doğ. işlem/yıl | Doğ. long | Doğ. short | 2x maliyet Sharpe (gel./doğ.) | Karışık % | Sonuç |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N20 ret %20 | 6.0% | -32.1% | 0.40 | 78 | +0.72 | **-0.36** | 0.7% | -14.5% | 0.13 | 95 | -0.04 | +0.07 | 0.24 / **-0.10** | 72.5 | GEÇMEDİ |
| N20 ret %40 | 8.2% | -55.0% | 0.40 | 78 | +1.45 | **-0.73** | -2.1% | -27.2% | 0.13 | 95 | -0.07 | +0.13 | 0.23 / **-0.10** | 72.5 | GEÇMEDİ |
| N20 sma %20 | 3.9% | -27.3% | 0.29 | 83 | +0.68 | **-0.41** | -3.9% | -14.7% | **-0.11** | 83 | -0.06 | +0.04 | 0.12 / **-0.31** | 53.5 | GEÇMEDİ |
| N20 sma %40 | 3.8% | -50.0% | 0.29 | 83 | +1.35 | **-0.82** | -11.1% | -29.2% | **-0.12** | 83 | -0.13 | +0.07 | 0.11 / **-0.32** | 53.5 | GEÇMEDİ |
| N60 ret %20 | 14.6% | -30.2% | 0.79 | 34 | +0.91 | **-0.18** | 10.6% | -15.4% | 0.60 | 21 | +0.03 | +0.13 | 0.70 / 0.53 | 92.0 | GEÇMEDİ (short) |
| N60 ret %40 | 26.3% | -53.9% | 0.79 | 34 | +1.81 | **-0.36** | 17.4% | -29.8% | 0.60 | 21 | +0.05 | +0.25 | 0.70 / 0.53 | 92.0 | GEÇMEDİ (short) |
| N60 sma %20 | 15.0% | -24.5% | 0.81 | 35 | +0.92 | **-0.17** | 17.6% | -10.6% | 0.93 | 33 | +0.06 | +0.16 | 0.72 / 0.83 | 91.5 | GEÇMEDİ (short) |
| N60 sma %40 | 27.2% | -44.3% | 0.81 | 35 | +1.83 | **-0.34** | 33.1% | -20.6% | 0.93 | 33 | +0.13 | +0.32 | 0.72 / 0.83 | 91.5 | GEÇMEDİ (short) |
| N120 ret %20 | 23.0% | -18.6% | 1.15 | 18 | +1.07 | **-0.01** | 2.9% | -20.6% | 0.25 | 21 | -0.02 | +0.08 | 1.08 / 0.18 | 97.5 | GEÇMEDİ (short) |
| N120 ret %40 | 45.4% | -35.6% | 1.14 | 18 | +2.14 | **-0.03** | 2.0% | -37.8% | 0.24 | 21 | -0.04 | +0.16 | 1.08 / 0.18 | 97.5 | GEÇMEDİ (short) |
| N120 sma %20 | 20.9% | -18.8% | 1.09 | 17 | +1.03 | **-0.06** | 14.9% | -16.7% | 0.79 | 21 | +0.05 | +0.15 | 1.03 / 0.72 | 97.5 | GEÇMEDİ (short) |
| N120 sma %40 | 41.0% | -36.4% | 1.09 | 17 | +2.06 | **-0.11** | 26.7% | -31.3% | 0.79 | 21 | +0.10 | +0.30 | 1.03 / 0.71 | 97.5 | GEÇMEDİ (short) |

Kalın = çıtayı bozan değer. Tam sayılar: `configs_dev_val.csv`, kural kural: `pass_fail.csv`.

### Kural kural kaç ayar geçti
| Kural | Geçen |
|---|---|
| 1. Sharpe > 0 (gel. ve doğ.) | 10/12 (N20 sma ikisi düştü) |
| 2. Short P&L > 0 (gel. ve doğ.) | **0/12** — doğrulamada 12/12 pozitif, geliştirmede 0/12 |
| 3. Karışık verinin 90. yüzdeliği üstü (gel.) | 8/12 (N60: 91.5–92, sınırda; N120: 97.5) |
| 4. 2x maliyette Sharpe > 0 | 8/12 (N20'lerin hepsi düştü) |
| **Hepsi** | **0/12** |

### Al-tut kıyası (1x long perp, funding dahil)
| | Gel. CAGR | Gel. MaxDD | Gel. Sharpe | Doğ. CAGR | Doğ. MaxDD | Doğ. Sharpe |
|---|---|---|---|---|---|---|
| BTC | 44.7% | -78.9% | 0.91 | -25.7% | -50.3% | -0.42 |
| ETH | 54.2% | -80.0% | 0.94 | -33.6% | -62.9% | -0.17 |
| 50/50 | 53.6% | -77.2% | 0.98 | -28.0% | -56.3% | -0.27 |

Geliştirmede al-tut getirisi her ayardan yüksek, ama düşüşü %77-80. En iyi trend ayarları (N120, %20) Sharpe'ta al-tutu geçiyor (1.09-1.15 vs 0.98) ve düşüşü dörtte bire indiriyor (%19).
Doğrulamada (düşen piyasa) al-tut %28/yıl kaybederken N60/N120 sma ayarları kazandı.

### Short tarafı neden düştü (yıl yıl, iki coin toplamı, N120 sma %20)
2020: -0.01, 2021: -0.03, **2022: +0.17**, 2023: -0.12, 2024: -0.07, 2025: +0.05, 2026 Q1: +0.10 (`yearly_long_short_by_asset.csv`).
Short sadece net ayı yıllarında (2022, 2025-26) kazanıyor; yükseliş yıllarındaki sahte düşüşlerde kaybettikleri geliştirmede bu kazancı siliyor.
Doğrulamadaki pozitif short sonucu tek bir düşüş dönemine dayanıyor; bu, short'un genel bir avantajı olduğunu göstermiyor.

### Dürüst değerlendirme
- Ön kayıtlı çıtaya göre **hiçbir ayar geçmedi.** Sonradan çıtayı yumuşatmıyoruz.
- Yine de not: N60/N120 sinyalleri ızgarada tutarlı (8 ayarın 8'i kural 1, 3, 4'ü geçti; doğrulamada Sharpe 0.24-0.93), yani long tarafı + "düşüşte küçülme" gerçek görünüyor.
  "Long-only veya long + nakit" versiyonu ayrı bir ön kayıtla ayrı test olarak sınanabilir; bu raporda o test **yapılmadı** ve bu sonuçlar ona kanıt sayılmaz.
- Kaldıraç sadece ölçeği değiştirir: %20 ve %40 hedeflerin Sharpe'ı neredeyse aynı, düşüş yaklaşık iki katı.
- Karışık veri kontrolünde N60 sadece sınırda (91.5-92. yüzdelik); N120 daha net (97.5).
- Funding, tüm ayarlarda net maliyet (geliştirmede long ağırlıklı olduğu için, sermayenin %12-34'ü).

## Dosyalar
- `configs_dev_val.csv` — 12 ayar × 2 dönem, tüm ölçüler
- `pass_fail.csv` — ayar başına kural kural geçti/kaldı
- `buy_hold.csv` — al-tut kıyası
- `shuffle_control_dev.csv` — 200 karıştırılmış çalıştırma × 12 ayar Sharpe
- `yearly_long_short_by_asset.csv` — yıl ve coin bazında long/short P&L
- `daily_returns_all_configs.csv` — günlük net portföy getirileri
- `equity_curves.png` — sermaye eğrileri (log) ve al-tut
- Kod: `research/tsmom/tsmom.py`, `research/tsmom/extras.py`
