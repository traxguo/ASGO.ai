# btc_eth_trend — BTC + ETH trend takibi (zaman serisi momentumu), long + short, oynaklık hedefli

**Durum: KÂĞIT TAKİP (çıtayı geçmedi, kurallar donduruldu)**
**Gözden geçirme tarihi: 2026-11-30**

Araştırma kodu: [`research/tsmom/tsmom.py`](../research/tsmom/tsmom.py) · Rapor: [`results/2026-11-06_btc_eth_trend/README.md`](../results/2026-11-06_btc_eth_trend/README.md)
Kâğıt takip: [`scripts/paper_btc_eth_trend.py`](../scripts/paper_btc_eth_trend.py) · Kayıt: `forward/paper_btc_eth_trend/` (`state.json`, `daily.csv`)

## Fikir
Fiyat uzun süredir yükseliyorsa yükselmeye, düşüyorsa düşmeye devam etme eğilimindedir. BTC ve ETH için her gün bakılır: fiyat son 120 günün ortalamasının üstündeyse long, altındaysa short. Pozisyonun büyüklüğü piyasanın sakinliğine göre ayarlanır: sakin piyasada büyük, fırtınalı piyasada küçük.

## Kurallar (donduruldu, değiştirilmez)
Takip edilen tek ayar: **N120 sma, hedef oynaklık %20** (12 ayarlık ızgaradan biri; denetçi kararı 2026-11-06).

- **Sinyal (her coin ayrı):** günlük kapanış (UTC) > son 120 günlük kapanış ortalaması (SMA 120) ise **long**, altındaysa **short**. Karar o günün kapanışında verilir, ertesi gün boyunca tutulur (ileriye bakma yok).
  Açıklama cümlesi: "BTC fiyatı 120 günlük ortalamasının üstünde: trend yukarı, long."
- **Büyüklük:** %20 / (son 30 günün gerçekleşmiş oynaklığı; günlük log getirilerin standart sapması × √365). Her coinin kaldıracı kendi yarısında **en fazla 3x**.
  Açıklama cümlesi: "Piyasa sakin olduğu için pozisyon büyük / fırtınalı olduğu için küçük."
- **Portföy:** sermayenin yarısı BTC'ye, yarısı ETH'ye (eşit ağırlık).
- **Yeniden dengeleme:** her gün kapanışta hedef büyüklüğe getirilir.
- **Maliyet:** işlem gören tutarın %0.1'i (komisyon + kayma). **Funding:** gerçek oranlar; pozisyon yönüne göre ödenir ya da alınır.
- Stop, TP, kısmi çıkış yok: çıkış sadece sinyalin yön değiştirmesiyle olur. (Projenin standart 2 TP'li işlem yönetimini kullanmaz; bu yüzden sadece kâğıt takipte, sinyal kanalına konmaz.)

## Test sonucu (ön kayıtlı, 2026-11-06)
Geliştirme 2020-05-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31. Kasa (2026-04 sonrası) hiç kullanılmadı.

**12 ayardan hiçbiri ön kayıtlı çıtayı geçmedi (0/12).** Sebep hepsinde aynı: short tarafı geliştirme döneminde tek başına para kaybettirdi.

Takip edilen ayar (N120 sma %20):

| | Geliştirme | Doğrulama |
|---|---|---|
| Yıllık getiri (CAGR) | %20.9 | %14.9 |
| En büyük düşüş | -%18.8 | -%16.7 |
| Sharpe | 1.09 | 0.79 |
| Yön değişimi / yıl | 17 | 21 |
| Long tarafı P&L (sermayenin oranı) | +1.03 | +0.05 |
| Short tarafı P&L | **-0.06** | +0.15 |
| 2x maliyette Sharpe | 1.03 | 0.72 |
| Karıştırılmış veri yüzdeliği | 97.5 | — |
| Sonuç | **GEÇMEDİ (short)** | |

Al-tut kıyası (BTC+ETH 50/50, 1x long, funding dahil): geliştirmede CAGR %53.6 / düşüş -%77.2 / Sharpe 0.98; doğrulamada CAGR -%28.0 / düşüş -%56.3 / Sharpe -0.27.

Kural kural (12 ayar): Sharpe > 0 → 10/12 · short P&L > 0 → **0/12** · karışık veri 90. yüzdelik üstü → 8/12 · 2x maliyette Sharpe > 0 → 8/12 · hepsi → **0/12**.

Short tarafı yıl yıl (iki coin toplamı, bu ayar): 2020 -0.01, 2021 -0.03, 2022 +0.17, 2023 -0.12, 2024 -0.07, 2025 +0.05, 2026 Ç1 +0.10. Short sadece net ayı yıllarında kazanıyor.

## Neden yine de kâğıtta takip ediliyor
Çıtayı geçmedi; bu değişmedi ve çıta yumuşatılmadı. Ama N60/N120 ayarları ızgarada tutarlı (Sharpe, 2x maliyet ve karışık veri kontrollerini geçtiler) ve düşen doğrulama döneminde al-tut %28/yıl kaybederken kazandı. Denetçi, tek bir ayarı **hiç değiştirmeden** ileriye dönük kâğıtta izlemeye karar verdi (2026-11-06). Bu takip bir "geçti" kararı değildir; gerçek para veya sinyal kanalı yok.

## Kâğıt takip nasıl çalışıyor
- GitHub'da her gün 00:20 UTC'de (günlük mum kapandıktan sonra) çalışır: `.github/workflows/paper_btc_eth_trend.yml`.
- Veri: Binance vadeli herkese açık API'si (günlük mum + funding, anahtar yok). Binance GitHub sunucusunu reddederse (HTTP 451) Bitget'in herkese açık günlük (UTC) mumları ve funding'i kullanılır; hangi kaynağın kullanıldığı `daily.csv`'de yazar. Bitget fiyatı ve funding'i Binance'tan biraz farklı olabilir.
- Sinyal kodu araştırmayla birebir aynıdır (`tsmom.py`'deki `signals` ve `run` içe aktarılır, kopyalanmaz).
- 10.000 USDT'lik kâğıt kasa ilk çalıştırmada açılır; ilk gün giriş maliyetinin tamamı ödenir. Her gün fiyat getirisi + funding − maliyet kasaya eklenir ve `daily.csv`'ye bir kez yazılır.
- Telegram ("KÂĞIT BTC/ETH Trend"): sadece bir coinin yönü değiştiğinde ve pazartesi günleri bir kez kısa not.
- Emir yok, işlem anahtarı yok.

## Gözden geçirme (2026-11-30)
Kâğıt sonuç, al-tut ve backtest beklentisiyle (günlük Sharpe ~0.8-1.1, düşüş ~%19) karşılaştırılır. Kurallar o tarihte de değiştirilmez; sadece takibe devam / durdurma kararı verilir. Long-only versiyon ayrı bir ön kayıtla ayrı test olarak sınanabilir.

## Geçmiş
- 2026-11-06: ön kayıt + test (0/12 geçti). Denetçi kararıyla N120 sma %20 kâğıt takibe alındı, kurallar donduruldu.
