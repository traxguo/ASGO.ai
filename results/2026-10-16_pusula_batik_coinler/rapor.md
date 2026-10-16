# Batmış / listeden çıkmış coinler testi (kuyruk 3) — 2026-10-16

Teşhis testi: kural değişikliği yok. `PusulaV2NoBe` (araştırma temeli) ve dondurulmuş `PusulaTrendLong` aynen çalıştırıldı.

## GUO'ya not
- Soru: Pusula'yı hep **bugün hâlâ listede olan** coinlerde test ettik. 2020'de seçim yapan biri, sonradan batan coinleri de seçebilirdi. Bu, sonuçları ne kadar iyi gösteriyor?
- 2020-2024 arasında batan veya Binance vadeliden çıkarılan 12 coinde Pusula **para kazanmadı**: `PusulaV2NoBe` 47 işlem, ortalama **-0.02R**, toplam -1.0R, PF 0.96, DD %12.1. Dondurulmuş `PusulaTrendLong` 38 işlem, **-0.79R**, toplam -30.0R, DD %25.7.
- İyi haber: **LUNA (Mayıs 2022) ve FTT (Kasım 2022) çöküşlerine Pusula hiç yakalanmadı.** Çöküş anında hiçbir işlem açık değildi; günlük trend çöküşten haftalar önce bozulmuştu. Kayıplar hep normal stoplar (-1R), felaket kaybı yok.
- Kötü haber: bu coinlerde trend kırılımları çalışmıyor; işlemlerin %83'ü zararla kapandı. Bugünkü listeden seçmek sonuçları **belirgin şekilde iyimser** gösteriyor (aşağıda tahmin).
- Eski 16'ya bu 12 coin eklenince toplam: +1.35R → **+1.22R** (`PusulaV2NoBe`), +0.95R → **+0.84R** (`PusulaTrendLong`); DD aynı (%23.7 / %26.1).

## Seçilen coinler (backtestten ÖNCE sabitlendi)
`config/pairs_delisted.json` sonuçlara bakmadan yazıldı. Kural: 2020-2024'te Binance USDⓈ-M'den çıkarılmış veya bilinen bir çöküşte %90+ değer kaybetmiş USDT perp'leri; data.binance.vision'da aylık 1h mum + funding arşivi olan ve en az 6 ay verisi olanlar.

| Coin | Veri (son işlem gören saat) | Olay |
|---|---|---|
| LUNA (eski LUNAUSDT) | 2021-01 → 2022-05-12 (son fiyat 0.008) | Terra çöküşü, Mayıs 2022 |
| FTT | 2022-04 → 2022-11-14 | FTX çöküşü, Kasım 2022 |
| SRM | 2020-09 → 2022-11-15 | FTX ile birlikte çöktü, çıkarıldı |
| HNT | 2020-09 → 2023-03-20 | çıkarıldı (Solana'ya göç) |
| BTS | 2021-02 → 2022-08-18 | çıkarıldı |
| TOMO | 2020-10 → 2023-11-14 | çıkarıldı (VIC'e dönüştü) |
| BTT (eski) | 2021-04 → 2022-01-14 | çıkarıldı (yeniden adlandırma) |
| BZRX | 2020-09 → 2021-12-19 | çıkarıldı |
| KEEP | 2021-06 → 2022-02-15 | çıkarıldı (T'ye birleşti) |
| YFII | 2020-09 → 2022-04-12 | çıkarıldı |
| WAVES | 2020-08 → 2024-06-11 | USDN çöküşü 2022, çıkarıldı 2024 |
| AUDIO | 2021-08 → 2024-05-16 | çıkarıldı |

Dışarıda kalanlar: ANC (sadece 3 ay veri). CVC, SC, RAY, DGB vb. hâlâ işlem görüyor, "batmış" sayılmadı.

## Sonuç
| Liste | Strateji | İşlem | Ortalama R | Toplam R | PF | Max DD | Net | Al-tut |
|---|---|---|---|---|---|---|---|---|
| Batmış 12 | PusulaV2NoBe | 47 | **-0.02** | -1.05 | 0.96 | %12.1 | -%1.5 | -%23.5 |
| Batmış 12 | PusulaTrendLong | 38 | **-0.79** | -29.96 | 0.04 | %25.7 | -%25.7 | -%23.5 |
| Eski 16 | PusulaV2NoBe | 230 | +1.35 | 311.26 | 2.06 | %23.7 | +%827.3 | +%931.5 |
| Eski 16 | PusulaTrendLong | 210 | +0.95 | 198.71 | 1.97 | %26.1 | +%386.2 | +%931.5 |
| Eski 16 + batmış 12 | PusulaV2NoBe | 243 | +1.22 | 297.66 | 1.96 | %23.7 | +%720.9 | ayrıntı alt raporda |
| Eski 16 + batmış 12 | PusulaTrendLong | 223 | +0.84 | 186.74 | 1.84 | %26.1 | +%336.1 | ayrıntı alt raporda |
| Yeni 20 | PusulaV2NoBe | 193 | +0.61 | 117.72 | 1.53 | %22.6 | +%134.2 | +%194.7 |
| Yeni 20 | PusulaTrendLong | 150 | +0.44 | 66.50 | 1.39 | %24.7 | +%64.5 | +%194.7 |

Hepsi sadece long (short 0). Eski 16 ve yeni 20 rakamları önceki raporlarla birebir aynı çıktı (230 / 193 / 150 işlem), yani ayarlar doğru. Batmış 12'de kazanan işlem oranı %17 (V2NoBe) ve %5 (TrendLong); ortanca işlem -1.04R.
Ayrıntılı raporlar: `delisted/rapor.md`, `wide16_delisted/rapor.md`.

## Coin bazında (batmış 12)
| Coin | V2NoBe işlem | V2NoBe toplam R | TrendLong işlem | TrendLong toplam R |
|---|---|---|---|---|
| LUNA | 4 | -3.47 | 4 | -2.26 |
| FTT | 1 | -1.04 | 0 | 0 |
| SRM | 0 | 0 | 0 | 0 |
| HNT | 3 | **+16.03** | 3 | -1.14 |
| BTS | 4 | -4.62 | 4 | -4.36 |
| TOMO | 10 | -9.08 | 9 | -9.44 |
| BTT | 1 | -1.10 | 1 | -1.09 |
| BZRX | 0 | 0 | 0 | 0 |
| KEEP | 0 | 0 | 0 | 0 |
| YFII | 3 | -3.17 | 2 | -2.11 |
| WAVES | 14 | -0.84 | 9 | -7.98 |
| AUDIO | 7 | +6.23 | 6 | -1.58 |

V2NoBe'de kârın tamamı tek işlemden: HNT 2021-10-26 → +11.5R. Bu işlem olmasa 46 işlem -12.6R (-0.27R). TrendLong'da hiçbir coin artıda değil. SRM, BZRX, KEEP'te hiç giriş olmadı.

## Çöküş anları: Pusula batan coine girdi mi?
- **LUNA (Mayıs 2022):** Çöküş anında açık işlem **yok**. Son LUNA işlemi 2022-03-28 → 2022-04-09, günlük trend bozulunca kapandı (V2NoBe -0.10R; TrendLong 2R sonrası başabaş stopla +0.05R). Diğer LUNA işlemleri 2021'de normal stoplar (-1.05 ile -1.23R).
- **FTT (Kasım 2022):** Çöküş anında açık işlem **yok**. Tek FTT işlemi 2022-09-13, aynı gün stop (-1.04R). TrendLong FTT'ye hiç girmedi.
- **SRM (Kasım 2022):** hiç işlem yok.
- **WAVES (2022 çöküşü):** 2022'de işlem yok; işlemler 2020-2021 ve 2023-2024'te (çıkarılmadan önceki son yıl), çoğu -1R stop, iki büyük kazanç (+6.2R 2021-08, +4.1R 2024-02).
- **Delist anında açık kalan işlem:** **hiç yok** (çıkış nedenleri sadece stop ve trend çıkışı; `force_exit` 0). Yani "coin kapandı, işlem son fiyattan zorla kapatıldı" en kötü senaryosu bu testte hiç yaşanmadı. Yaşansaydı: Freqtrade, verisi biten coindeki işlemi backtest sonuna kadar açık tutar (bir işlem yuvası boşa dolu kalır) ve coinin son fiyatından kapatır; gerçekte borsa da delist günü son fiyattan kapatır.
- Birleşik listede FTX haftasında (2022-11-04 → 2022-11-08) BTC, ETH, BNB long'ları birer -1R stopla kapandı; bunlar eski 16'da da aynı (piyasa geneli düşüş, batmış coinlerle ilgisi yok).
- Neden kaçtı: Pusula long için günlük kapanışın EMA20 üstünde ve trend puanının artı olmasını istiyor. LUNA ve FTT çöküşten önce zaten düşüş trendindeydi; çöküş günlerinde giriş şartı sağlanmıyordu.

## Bugünün listesinden seçmenin iyimserliği (tahmin)
Batmış coinlerin verisi 2020-2024'te; adil kıyas için aynı yıllarda kapanan işlemler:

| Liste (2020-2024) | V2NoBe işlem | V2NoBe ort. R | TrendLong işlem | TrendLong ort. R |
|---|---|---|---|---|
| Eski 16 | 179 | +1.67 | 162 | +1.12 |
| Yeni 20 | 137 | +0.97 | 110 | +0.77 |
| Batmış 12 | 47 | **-0.02** | 38 | **-0.79** |
| Eski 16 + batmış 12 (tek kasa) | 192 | +1.49 | 175 | +0.97 |

- İşlem başına fark: batmış coinlerde ortalama, bugünkü coinlere göre V2NoBe'de 1.0-1.7R, TrendLong'da 1.6-1.9R daha düşük.
- Toplam etkisi: 2020'de seçilebilecek evrenin yaklaşık üçte biri sonradan batmış/çıkarılmış olsaydı (16'ya 12 eklemek gibi), 3 işlem sınırı nedeniyle batmış coinlere giden işlem az (V2NoBe 14, TrendLong 15) ama hepsi kötü: V2NoBe'de bu 14 işlem -7.7R, TrendLong'da 15 işlem -14.0R. Ortalama R: +1.35 → +1.22 (V2NoBe, yaklaşık **%10 düşüş**), +0.95 → +0.84 (TrendLong, yaklaşık **%12 düşüş**). DD değişmedi.
- Kaba üst sınır: yeni 20 + batmış 12 işlemleri birlikte sayılırsa (aynı kasada çalıştırılmadı) V2NoBe 240 işlem, ortalama +0.61R → yaklaşık +0.49R (%20 düşüş).
- Sonuç: bugünkü listeden seçim, Pusula'nın ortalama R'sini kabaca **%10-20 iyimser** gösteriyor. Strateji batan coinlerde patlamıyor (çöküşlere yakalanmıyor) ama bu coinlerde kazanç da yok. Ortalama R'nin büyük kısmı, sonradan büyüyen coinlerdeki birkaç büyük trend işleminden geliyor (ETC, SOL, BNB, FIL, ALGO); hangi coinin büyüyeceğini önceden bilmek mümkün değil.
- Not: 12 coin ve 47 işlem küçük bir örnek; rakamlar yönü gösteriyor, kesin oranı değil.

## Ayarlar
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long; `--cache none`, her liste kendi sonuç klasörüne.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBe PusulaTrendLong --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades --cache none --backtest-directory user_data/backtest_results/batik_<liste>`. Listeler: `delisted`, `wide16_delisted` (yeni dosya `config/pairs_wide16_delisted.json` = eski 16 + batmış 12), karşılaştırma için `wide16`, `new20`. Rapor `scripts/make_report.py`.
- Maliyet: emir başına %0.1, funding geçmiş veriden; işlem başı %1 risk, en fazla 3x.
- Veri: `research/data/fetch_binance_vision.py` ile 1h/4h/1d mum + 1h mark + funding (ham zip'ler ayrı klasörde `user_data/data/binance_vision_raw_delisted/`, `python -I`).
- **Önemli veri düzeltmesi:** Binance arşivi delist sonrası aylarda coinin son fiyatıyla **hacimsiz düz mumlar** yayınlamaya devam ediyor (örn. FTT 2022-11'den 2026-09'a kadar 34 bin saat, hacim 0). Bunlar gerçek işlem değil; her coinin verisi son hacimli mumda kesildi (mum, mark ve funding dosyaları). Kesmeden önce hacim 0 olan mum sadece bu kuyrukta vardı (öncesinde boşluk yok).
- `scripts/offline_freqtrade.py`: 12 coin sabit market listesine eklendi (genel hassasiyet). Freqtrade'in kaldıraç kademe dosyasında 10'u yoktu (FTT ve WAVES vardı); bunlar ZIL'in kademesini ödünç alıyor (sadece bu 10 coin, en fazla 3x'te yalnızca likidasyon fiyatını etkiler).
- Kasa (2026-04 → 2026-09) bu dönem aralığında var ama batmış coinlerin o döneme verisi yok; eski 16/yeni 20 rakamları önceki turlarla aynı, yeni kasa kullanımı yok.

## Veri boşlukları
- ANC: sadece 3 ay arşiv, listeye alınmadı.
- FTT vadeli arşivi 2022-04'te başlıyor (öncesi yok); bu yüzden 2021 FTT boğası test dışı.
- LUNA: eski LUNAUSDT 2021-01'de başlıyor; 2020 yok.
- Funding: tüm coinlerde aylık arşiv var; delist ayının son günleri kısmi.
