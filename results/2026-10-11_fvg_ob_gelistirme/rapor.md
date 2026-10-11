# fvg_ob — ilk eleme (geliştirme 2022-2024, BTC/ETH/SOL, 3m) — 2026-10-11

## GUO'ya not
- **Şansı hak ediyor mu?** Hayır. Normal masrafla işlem başına ortalama **-0.95R**, kâr/zarar oranı (PF) **0.37**; test hesabı 2022'de sıfırlandı. İlk eleme şartlarının hiçbiri tutmadı.
- **Masraf olmasa?** Masrafsız hesapta bile **-0.20R** (PF 0.73), her yıl, her coin, hem long hem short eksi. Yani sorun sadece masraf değil: giriş kuralının kendisinde avantaj yok. Stoplar çok dar (ortanca %0.3) olduğu için masraf işlem başına ayrıca ~0.7R yiyor.
- **Günde kaç işlem?** Günde **~0.9 işlem** (3 coin, tek pozisyon). Kural günde ~12 sinyal üretiyor ama tek pozisyon kuralı, emrin 60 dk beklemesi ve 3 kayıp → 24 saat mola yüzünden çoğu alınamıyor. Hedef olan günde 3 işleme ulaşmıyor.
- **Sonraki adım:** Devam önerilmiyor; emekliye ayırma önerisi (karar senin). Doğrulama ve kasa verisine bakılmadı.

## Ne test edildi
- Kural: proje sahibinin tarifi birebir (kart: [`cards/fvg_ob.md`](../../cards/fvg_ob.md), test öncesi yazıldı). Kod: `strategies/candidates/fvg_ob.py`.
  - 15 dk (3 dk mumlardan, geleceği görmeden): son onaylı swing'in gövdeyle kırılması (MSS). Hareketi başlatan son ters renkli 15 dk mum = Order Block.
  - 3 dk: hareket sırasında OB bölgesiyle kesişen FVG; **FVG'nin %50'sine limit emir**, 20 mum (60 dk) geçerli, fiyat önce hedefe giderse iptal. Emir ancak geri çekilme mumlarının ortalama hacmi hareket mumlarınınkinden düşükse dolar.
  - Stop: OB ucunun %0.05 ötesi. Hedef: karşı taraftaki alınmamış en yeni 15 dk swing (likidite); kazanç/risk ≥ 2 değilse işlem yok. Tek hedef, kısmi çıkış ve break even yok.
  - Limit emir (giriş ve hedef) ancak fiyat seviyeyi **%0.02 (≥ 1 tick) geçerse** dolar (iyimser dolumlara karşı; `kirilim1s_limit`'teki yaklaşım). Giriş mumunda hedef sayılmaz, stop sayılır.
  - Risk işlem başına %1, kaldıraç en fazla 10x (likidasyon stopun ≥ 2 katı uzakta), **en fazla 1 açık pozisyon**, üst üste 3 zarardan sonra 24 saat yeni işlem yok.
- Coinler BTC, ETH, SOL; dönem 2022-01-01 → 2024-12-31; kasa 10000 USDT; maliyet emir başına %0.1 (`--fee 0.001`, limit emirler dahil); funding geçmiş veriden.
- 1R = |giriş − stop|. R = net kâr (masraf + funding dahil) / (miktar × |giriş − stop|).
- **Veri:** data.binance.vision'dan 1 dk USDⓈ-M mumları (BTC/ETH/SOL, 2021-12 → 2024-12; ham zipler ayrı klasörde `user_data/data/binance_vision_1m_raw/`), Freqtrade formatına çevrildi ve 3 dk'ya birleştirildi. Her coinde 1 622 880 adet 1 dk mum, eksik gün yok. Funding/mark verisi zaten vardı. 5 dk'ya düşmeye gerek kalmadı.
- **Hile testi:** (1) Kendi kesme testi (`research/robustness/fvg_ob_lookahead_check.py`, 3 coin × 15 kesim noktası × 2 giriş modu): sinyal sütunlarında fark yok. (2) Freqtrade `lookahead-analysis` (`FvgObLookahead`, 3 coin, 2023-01 → 2023-02, 30 işlem): standart araç limit emir, emrin verildiği mumdan sonra dolunca bunu "bias" sayıyor (18/30, göstergelerde bias yok). Kontrol verisi dolum mumundan 2 mum sonra bitecek şekilde çalıştırınca (`research/robustness/lookahead_limit_fill.py`) **0/30, bias yok**. (`FvgObLookahead` sadece bu araç için: araç kasayı 1 milyar yaptığı için %1 riskli boyut borsa sınırlarını aşıyor; boyut sabit, sinyaller aynı.)

## Özet tablo (ana sürüm `FvgOb`, 1 pozisyon)
| Koşu | İşlem | Günde | Kazanan | Ort. R | PF | Max DD | Masraf (R/işlem) | Long R | Short R | Artı coin | Artı yıl |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Normal masraf (%0.1/emir)** | 1011 | 0.92 | 17.5% | **-0.946** | **0.37** | **100%** | 0.73 | -1.033 | -0.867 | 0/3 | 0/3 |
| Masraf x2 (%0.2/emir) | 624 | 0.57 | 16.7% | -1.641 | 0.22 | 100% | 1.42 | -1.666 | -1.619 | 0/3 | 0/3 |
| Düşük masraf %0.03/emir (teşhis) | 1260 | 1.15 | 18.5% | -0.389 | 0.57 | 99% | 0.21 | -0.399 | -0.379 | 0/3 | 0/3 |
| Masrafsız (teşhis) | 1274 | 1.16 | 18.1% | -0.198 | 0.73 | 94% | 0 | -0.217 | -0.181 | 0/3 | 0/3 |
| Ters coin sırası (teşhis, normal masraf) | 1024 | 0.93 | 17.2% | -0.914 | 0.38 | 100% | 0.68 | -1.034 | -0.810 | 0/3 | 0/3 |
| 1 dk detaylı mum içi sıra (teşhis, normal masraf) | 1008 | 0.92 | 17.5% | -0.936 | 0.36 | 100% | 0.72 | -0.997 | -0.882 | 0/3 | 0/3 |
| Varyant `FvgObEdge` (FVG kenarı, normal masraf) | 993 | 0.91 | 19.9% | -0.801 | 0.45 | 100% | 0.67 | -0.797 | -0.804 | 0/3 | 0/3 |

Max DD kapanan işlemlerden kurulan kasa eğrisidir. Hesap 2022'de sıfıra yaklaştığı için sonraki yıllarda işlemler çok küçük (USDT net rakamları anlamsızlaşıyor); karar R üzerinden. İşlem sayısı koşular arasında biraz değişiyor çünkü 3 kayıp → 24 saat kuralı ve tek yuva, işlemlerin sonucuna (masrafa) bağlı.

### Yıllara göre (ortalama R)
| Yıl | Normal: toplam | Long | Short | Masrafsız: toplam | Long | Short | Al-tut (eşit ağırlık) |
|---|---|---|---|---|---|---|---|
| 2022 | -0.809 | -0.833 | -0.788 | -0.225 | -0.244 | -0.209 | -75.5% |
| 2023 | -1.018 | -1.184 | -0.864 | -0.141 | -0.265 | -0.022 | +389.1% |
| 2024 | -1.089 | -1.145 | -1.039 | -0.227 | -0.139 | -0.299 | +83.6% |

### Coinlere göre (ortalama R)
| Coin | Normal | Long | Short | Masrafsız |
|---|---|---|---|---|
| BTC | -1.119 | -1.138 | -1.099 | -0.259 |
| ETH | -0.987 | -1.083 | -0.902 | -0.167 |
| SOL | -0.662 | -0.797 | -0.552 | -0.157 |

### Al-tut kıyası
Aynı 3 coini 2022-01-01'de alıp 2024 sonuna kadar tutmak (eşit ağırlık): **+%34.5** (BTC +%102, ETH -%9.5, SOL +%11; coin başına ortalama en büyük düşüş %80). Strateji hesabı sıfırladı (-%100).

### Neden kaybediyor?
- **Kazanma oranı çok düşük:** %17.5. Masrafsız hesapta kazanan işlem ortalama +3.4R, kaybeden -1.0R; başa baş için ~%23 kazanma gerekirdi, %18'de kalıyor. Fiyat FVG'nin ortasına döndüğünde çoğu zaman OB'nin altına (stopa) da gidiyor; hedefe (karşı likidite) ulaşma oranı düşük.
- **Stop çok dar:** ortanca %0.31 (çeyrekler %0.21 / %0.45). Giriş + çıkış %0.2 masraf işlem başına ortalama **0.73R** ediyor; normal masrafla kazanan işlem +2.75R'ye düşüyor, kaybeden -1.73R'ye çıkıyor ve başa baş kazanma oranı ~%39'a fırlıyor.
- **Mum içi sıra etkisi yok:** 1 dk detaylı koşu (-0.94R) 3 dk koşuyla (-0.95R) aynı; sonuç 3 dk mum içinde sıranın varsayımından gelmiyor.
- **Coin sırası etkisi yok:** ters sıra -0.91R (momentum_5m'deki sıra etkisi burada görülmüyor).
- **Sinyal/işlem:** 3 coinde 3 yılda 13 233 sinyal (günde ~12); alınan ~1000 işlem. 3850 emir 60 dk içinde dolmadı ya da hedef önce görüldüğü için iptal edildi (Freqtrade ikisini birlikte sayıyor); 2509 sinyal yuva doluyken geldi.

## İlk eleme şartları (normal masraf, ana sürüm)
| Şart | Eşik | Sonuç | Geçti mi? |
|---|---|---|---|
| Ortalama R | > 0 | -0.946R | **hayır** |
| Profit factor | ≥ 1.1 | 0.37 | **hayır** |
| Max drawdown | ≤ %35 | %100 | **hayır** |
| Artıda biten coin | ≥ 2/3 | 0/3 | **hayır** |
| Artı yıl | ≥ 2/3 | 0/3 | **hayır** |
| (bilgi) Masraf x2 | > 0R | -1.641R | kırılgan |

**Sonuç: ilk elemeyi geçemedi.** Masrafsız bile eksi olduğu için emekliye ayırma önerilir (karar proje sahibinin; kod şimdilik `strategies/candidates/` altında). Doğrulama (2025+) yapılmadı, kasaya (2026-04+) dokunulmadı. 16 coin dayanıklılık testi yapılmadı (1m/3m veri sadece BTC/ETH/SOL için indirildi; kart böyle planladı).

## Aslan stratejileriyle karşılaştırma
- **Benzer:** 15 dk MSS + FVG'ye limit geri dönüş; fraktal kodu Aslan'dan (`pivots`, iki yanda 2 mum).
- **Farklı:** likidite alımı (sweep) şartı yok; giriş OB ile çakışan 3 dk FVG'nin ortası; geri çekilmede hacim düşmeli; hedef sabit R değil, karşı likidite (ortalama kazanan 3.4R); stop OB'nin ötesinde, 3 dk seviyesinde → Aslan'dan da dar stoplar.
- **Sonuçlar uyumlu:** Aslan'ın 26+ varyantı ve AMS masraf öncesi ~0R ile -0.03R arasındaydı; bu kural masraf öncesi **-0.20R**, yani daha da kötü. Hiçbir SMC tarifi (sweep → MSS → FVG/OB) bu coinlerde ve bu dönemde masraf öncesi pozitif avantaj göstermedi. Dar stoplu kısa vadeli girişlerde masraf ayrıca belirleyici.

## Yaklaşımlar / sınırlar
- Hacim şartı ve "fiyat geçmeli" dolum kuralı, backtest motorunda emrin dolum kontrolüne eklenen küçük bir sarmalayıcıyla uygulandı (sadece bu stratejide etkin). Dry-run'da hacim şartı her mum kapanışında emri çekip yeniden koyarak uygulanmalı (bu turda dry-run yok).
- Kaldıraç tavanı 10x (GUO'nun aile kuralı; `docs/rules.md`'deki 3x'in bu ilk eleme için istisnası). %1 risk 10x ile sağlanamıyorsa (stop ≲ %0.1) sinyal atlandı.
- Tablolardaki "trailing_stop_loss" çıkışları da plan stopudur (Freqtrade, custom stop fonksiyonundan gelen stopu bazen böyle etiketliyor).
- Bekleyen limit emir tek yuvayı tutar (tek pozisyon kuralının doğal sonucu).

## Dosyalar
- `analiz_tablolari.md` (tüm koşuların ayrıntılı tabloları), `ozet.json`, grafikler (`*_sermaye.png`, `*_R_dagilimi.png`), işlem listeleri `islemler_FvgOb_normal.csv`, `islemler_FvgOb_masrafsiz.csv`.
- Analiz: `python research/reports/fvg_ob_analysis.py --out results/2026-10-11_fvg_ob_gelistirme --pairs BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT --run normal=<backtest klasörü> ...`
- Backtest komutu (ana): `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --strategy FvgOb --timeframe 3m --timerange 20220101-20250101 -p BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT --max-open-trades 1 --fee 0.001 --export trades`. Diğerleri: `--fee 0.002 / 0.0003 / 0`, coin listesi ters, `--strategy FvgObEdge`, `--timeframe-detail 1m`. Backtest zipleri repoya konmadı.
