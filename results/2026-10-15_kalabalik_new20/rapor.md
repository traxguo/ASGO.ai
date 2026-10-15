# Kalabalik_B — 20 yeni coinde dışarıdan kontrol — 2026-10-15

Kuyruk maddesi 2b. Dondurulmuş `Kalabalik_B` (funding aşırılığı + dönüş) hiç görmediği 20 coinde (`config/pairs_new20.json`) çalıştırıldı. **Hiçbir kural değişmedi**; bu bir ayar turu değil, sadece "kenar yeni coinlerde de var mı?" sorusu.

## GUO'ya not
- 16 coinde kârlı görünen Kalabalık, 20 yeni coinde **kâr etmedi**: 187 işlem, işlem başına **-0.02R**, net **-%5.9**, en büyük düşüş **%27.3** (16 coinde %9 idi).
- Long tarafı zar zor artıda (+0.09R, PF 1.13), short tarafı açıkça eksi (-0.32R, PF 0.55). 16 coinde de short zayıftı; burada zarara döndü.
- Coinlerin sadece **8/20**'si artıda. En iyi 10 işlem +30.5R, geri kalan 177 işlem -33.6R.
- Üç dönemden sadece **kasa** (2026-04 → 09, 11 işlem) artıda; geliştirme ve doğrulama eksi.
- Masraf iki katına çıkınca -0.05R.
- **Karar: tutmuyor.** Kalabalık'ın 16 coindeki sonucu büyük ihtimalle o coinlere özgü ya da şans. Kart "candidate" kalıyor ama "kenar genellenmiyor" notu düşüldü; emeklilik sahibin kararı.

## Sonuç tablosu (maliyet + funding dahil, R cinsinden)
Her dönem ayrı backtest (dönem başında boş kasa, `--timerange` o dönem). PF `make_report.py`'nin USDT kâr/zararından hesapladığı değer.

| Dönem | İşlem | Ortalama R | Toplam R | PF | Max DD | Net | Long (n / ort R / PF) | Short (n / ort R / PF) | Al-tut (eşit ağırlık) |
|---|---|---|---|---|---|---|---|---|---|
| Tam 2020-01 → 2026-09 | 187 | **-0.02** | -3.13 | 0.95 | %27.3 | -%5.9 | 137 / +0.09 / 1.13 | 50 / -0.32 / 0.55 | +%194.7 (ort. düşüş %97.6) |
| Geliştirme 2020-01 → 2024-12 | 138 | -0.08 | -11.42 | 0.86 | %24.1 | -%12.4 | 91 / +0.04 / 1.06 | 47 / -0.32 / 0.56 | +%231.1 (%95.7) |
| Doğrulama 2025-01 → 2026-03 | 38 | -0.03 | -1.04 | 0.93 | %8.5 | -%1.7 | 38 / -0.03 / 0.93 | 0 / — / — | -%54.0 (%83.8) |
| Kasa 2026-04 → 2026-09 | 11 | +0.61 | +6.70 | 2.05 | %1.9 | +%6.6 | 8 / +0.96 / 2.87 | 3 / -0.33 / 0.50 | +%63.8 (%51.2) |
| Tam, masraf x2 (`--fee 0.002`) | 187 | -0.05 | -9.56 | 0.90 | %29.0 | -%11.6 | 137 / +0.06 / 1.08 | 50 / -0.35 / 0.53 | +%194.7 |

Tam dönem çalıştırmasının içinden dönem dilimleri (işlem açılış tarihine göre) aynı yönü gösteriyor: geliştirme 138 işlem -0.08R, doğrulama 38 işlem +0.04R (ayrı çalıştırmada -0.03R; fark dönem başında açık işlem / 3 işlem sınırından), kasa 11 işlem +0.61R.

Kıyas, eski 16 coin (kart): geliştirme 123 işlem +0.28R PF 1.46 DD %9.3; doğrulama 26 işlem +0.29R; kasa 13 işlem +0.05R.

## Önceden konan "tutuyor" şartı
| Şart | Sonuç | Geçti mi |
|---|---|---|
| Tam dönem ortalama R > 0 | -0.02R | hayır |
| Tam dönem PF ≥ 1.1 | 0.95 | hayır |
| 3 dönemden en az 2'si artıda | sadece kasa artıda (1/3) | hayır |
| Coinlerin en az yarısı artıda | 8/20 | hayır |

**Sonuç: tutmuyor.** Dört şartın dördü de kaldı.

## Yıllara göre (tam dönem çalıştırması, açılış yılı)
| Yıl | Long n | Long ort R | Long toplam R | Short n | Short ort R | Short toplam R |
|---|---|---|---|---|---|---|
| 2021 | 26 | +0.02 | +0.39 | 2 | -0.88 | -1.76 |
| 2022 | 23 | +0.09 | +2.09 | 2 | +0.85 | +1.70 |
| 2023 | 15 | +0.60 | +9.07 | 28 | -0.20 | -5.74 |
| 2024 | 27 | -0.30 | -8.12 | 15 | -0.60 | -9.05 |
| 2025 | 26 | -0.10 | -2.48 | 0 | — | — |
| 2026 | 20 | +0.59 | +11.78 | 3 | -0.33 | -1.00 |

İlk işlem 2021-02 (funding'in 1 yıllık geçmişi birikmeden işlem yok). Artı yıllar 2023 long ve 2026 long; 2024 iki tarafta da eksi. Short'lar 2023-2024'teki aşırı-pozitif funding dönemlerinde yoğunlaşıyor ve kaybediyor.

## Coin bazında (tam dönem)
| Coin | İşlem | Toplam R | Al-tut |
|---|---|---|---|
| ALGO | 23 | +9.95 | -%47.9 |
| XTZ | 11 | +6.70 | -%84.3 |
| THETA | 9 | +4.79 | -%48.0 |
| EGLD | 9 | +4.67 | -%65.7 |
| MANA | 5 | +3.02 | -%91.4 |
| VET | 10 | +2.01 | +%139.2 |
| CHZ | 4 | +1.94 | -%26.0 |
| ENJ | 8 | +0.17 | -%83.5 |
| UNI | 10 | -0.06 | +%62.4 |
| AAVE | 6 | -0.20 | +%286.5 |
| NEO | 7 | -0.99 | -%65.8 |
| FIL | 2 | -2.03 | -%97.9 |
| SAND | 5 | -3.02 | -%54.0 |
| HBAR | 7 | -3.10 | -%68.6 |
| IOTA | 15 | -3.12 | -%66.9 |
| DASH | 19 | -3.98 | -%19.1 |
| ICP | 4 | -4.07 | -%99.3 |
| AXS | 8 | -4.40 | +%136.4 |
| NEAR | 7 | -5.07 | +%373.4 |
| ZEC | 18 | -6.36 | +%3815.4 |

8/20 coin artıda. Dönem bazında coin listeleri: `gelistirme/rapor.md`, `dogrulama/rapor.md`, `kasa/rapor.md`.

## Kâr yoğunluğu
- En iyi 10 işlem +30.5R; kalan 177 işlem -33.6R. Yani 16 coindeki gibi kâr birkaç TP2'ye bağlı, ama burada geri kalan işlemlerin kaybını karşılamıyor.
- Bootstrap (5000 tekrar, işlemleri yeniden örnekleme): P(ortalama ≤ 0) = %57. 16 coinde %3 idi.
- Çıkışlar: stop %66.3, TP1 sonrası BE %17.1, TP2 %16.6 (16 coinde TP2 %24.4).

## Ayarlar (orijinal Kalabalık raporuyla aynı)
- Komut (dönem başına `--timerange` değişir):
  `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_new20.json --strategy-list Kalabalik_B --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades`
  Dönemler: `20200101-20250101`, `20250101-20260401`, `20260401-20261001`; masraf x2 için `--fee 0.002` eklendi. Rapor `scripts/make_report.py`.
- Maliyet: emir başına %0.1 (komisyon %0.05 + kayma %0.05), funding geçmiş veriden. Risk işlem başına %1, kaldıraç en fazla 3x, en fazla 3 açık işlem.
- Ayar kontrolü: aynı komut eski 16 coinde (`config/pairs_wide16.json`, 20200101-20250101) tekrar çalıştırıldı, orijinal raporla birebir aynı çıktı (123 işlem, +%36.98, DD %9.34).
- Bu coinler hiç görülmediği için kasa dönemine bakmak yeni bir kasa ihlali değil; Kalabalık'ın kuralları bu sonuçtan sonra değiştirilmeyecek.

## Veri notları
- Funding dosyaları (`user_data/data/binance/futures/*-1h-funding_rate.feather`) 20 coinin hepsinde zaten vardı, yeni indirme gerekmedi. 8 saatlik ödemelerde boşluk yok, hepsi 2026-09-30'a kadar.
- **ICP:** Binance arşivinde (data.binance.vision) ICPUSDT funding verisi 2022-09'dan önce yok (2021-06 ve 2022-08 aylık dosyaları 404). Fiyat 2021-05'te başlıyor; ICP'de ilk işlem 2024-02 (1 yıllık geçmiş birikince). Sonucu değiştirecek büyüklükte değil (4 işlem).
- **Funding aralığı değişen coinler:** XTZ (2025-07'den), AXS (2026-01'den), ENJ (2026-03'ten) 4 saatlik funding'e geçmiş. Kural "son 3 ödeme" ve "son 365×3 ödeme" diye kodlandığı için bu coinlerde değişiklikten sonra pencere fiilen 12 saat / ~6 ay oluyor. Etkilenen işlem sayısı çok az (XTZ 1 işlem +2.9R, ENJ 2 işlem +0.03R, AXS 0), sonucu değiştirmiyor. Kural dondurulduğu için düzeltilmedi; canlıya geçecekse kartta ele alınmalı.
- Al-tut sütunu bugün listede olan coinleri içerir (hayatta kalan iyimserliği; FIL, ICP gibi -%98'lik düşüşler dahil).

## Karar
**Tutmuyor.** Kalabalık'ın 16 coindeki avantajı 20 yeni coinde görülmüyor: ortalama -0.02R, PF 0.95, DD %27, sadece 8/20 coin artıda, sadece kasa dönemi artıda. Long tarafı başa baş (+0.09R), short tarafı açıkça eksi. Kurallar değiştirilmedi. Kuyruk 4 (Pusula + Kalabalık birlikte) için bu sonuç önemli: Kalabalık'ı ikinci bacak olarak eklemenin gerekçesi zayıfladı. Emeklilik kararı proje sahibinin.
