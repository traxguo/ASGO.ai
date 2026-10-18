# fitil_avcisi — panik fitillerini derin limit emirle yakala, 3 saat tut (ADAY, 2026-10-12)

Kod: [`research/scans/wick_catcher.py`](../research/scans/wick_catcher.py) (araştırma simülasyonu; demo kodu henüz yok)

## Neden bu fikir (GUO: "tüm eksileri topla, onları köreltecek kendi stratejinle gel")
Bugüne kadar 30'a yakın kısa işlem fikrinin batma sebepleri ve bu stratejinin cevabı:
| Eksi (neden battı) | Fitil Avcısı'nın cevabı |
|---|---|
| Masraf (%0.2) kısa işlemin küçük kârını yiyor | Giriş limit (maker, %0.02) emirle ve fiyatın %5 altından: tek dolum = büyük indirim |
| Limit emirler fiyata yakınken hep "kötü" anlarda doluyor | Sadece derin seviye (%5 aşağı), sadece günlük trendi yukarı coinlerde: panik fitilleri geri dönüyor |
| Dar stoplar gürültüde patlıyor, dönüşü kaçırıyor | İşlem içinde stop yok, 3 saat sonra çık (test: stoplar her durumda sonucu kötüleştirdi) |
| Büyük çöküşlerde (ör. 10 Ekim 2025) tüm coinler birlikte düşmeye devam ediyor | BTC de aynı saatte %3+ düştüyse girme (piyasa çapında çöküş koruması) |
| Short taraf hep zayıf | Sadece long |
| Fiyat tahmini birkaç saatte rastgele | Tahmin yok: sadece aşırı fiyat sapmasının geri dönüşünü alıyor |

## Kurallar (2026-10-12, kasa testinden önce donduruldu)
- Coin: `config/pairs_all36.json`. Günlük puan ≥ +1 ve son kapanmış günlük kapanış EMA(20) üstü.
- Her saat başında: alış limit emri = saat açılışı × 0.95, bir saat bekler.
- Dolum: 15m dip, limitin %0.1 altına inerse dolmuş sayılır (temkinli).
- O saat içinde BTC, saat açılışından %3 veya daha fazla düştüyse işlem alınmaz.
- Çıkış: dolumdan 3 saat sonra piyasa emriyle. Stop yok.
- Aynı anda en fazla 5 işlem, her biri kasanın 1/5'i (toplamda kaldıraçsız). Coin başına bir işlem.
- Masraf: giriş %0.02, çıkış %0.06 + %0.05 kayma.

## Test geçmişi
| Coinler | Dönem | İşlem/gün | Ort. % | Ortanca % | Kazanan | Kasa | En büyük düşüş | En kötü gün |
|---|---|---|---|---|---|---|---|---|
| 36 | 2020-03 → 2024 (geliştirme) | 1.21 | +1.16 | +1.27 | %64 | çok yüksek* | -12.6% | -10.4% |
| 45 hiç bakılmamış | 2020-03 → 2024 | 1.29 | +0.78 | +1.05 | %61 | çok yüksek* | -21.4% | -13.1% |
| 36 | 2025-01 → 2026-03 (doğrulama) | 0.55 | +1.38 | +0.86 | %61 | +94.7% | -6.4% | -6.4% |
| 45 hiç bakılmamış | 2025-01 → 2026-03 | 0.42 | +0.36 | +0.42 | %56 | +12.4% | -9.9% | -9.7% |
| 36 | **2026-04 → 2026-09 (kasa, bir kez)** | 0.58 | +0.39 | +0.55 | %61 | +8.1% | -5.3% | -4.8% |
| 45 hiç bakılmamış | **2026-04 → 2026-09 (kasa, bir kez)** | 1.33 | +0.44 | +0.25 | %52 | +16.8% | -14.5% | -6.8% |
*Bileşik kasa rakamları 2021 boğasında abartılı büyüyor; işlem başı ortalama ve düşüş daha anlamlı.

## Dürüstlük notları
- Çöküş koruması (BTC %3) korumasız sürümün doğrulamada küçük coinlerde 10 Ekim 2025'te çakılması GÖRÜLDÜKTEN sonra eklendi; geliştirmede de en iyi seçenekti ama doğrulama artık tam bağımsız değil. Son hakem kasa testi.
- Stop denemeleri (%8, %12) geliştirmede sonucu kötüleştirdi; korumasız sürümün en kötü günü -%31.6 idi (küçük coinler).
- Küçük coinlerde en iyi 5 gün çıkarılınca doğrulama eksiye dönüyor: kırılgan. Ana liste 36 coin.
- Doluma güven: dip limitin %0.1 altına inmeden dolum sayılmıyor; yine de gerçek dolum demoda ölçülmeli.

## Kasa testi yorumu
- İki listede de artıda, ortanca artı, düşüş sınırlı. Kasa testini geçti.
- Ama işlem başı kazanç önceki yıllardan küçük (+0.3..+0.4%) ve en iyi 5 gün çıkarılınca eksi: kazancın önemli kısmı birkaç sert fitil gününden geliyor.
- 81 coin birlikte günde ~2 işlem eder; GUO'nun istediği sıklığa en yakın sonuç.

## Demo (Bitget, gerçek para yok)
- Kod: `scripts/bitget_fitil.py`, iş akışı `.github/workflows/bitget_demo_fitil.yml`, Cloudflare saati her 15 dakikada başlatır.
- Her saat başı ilk çalışmada limit emirler konur, bir saat sonra dolmayanlar iptal edilir. Dolumdan 3 saat sonra piyasa emriyle satılır.
- BTC koruması canlıda: o saat BTC %3 düştüyse yeni emir yok, bekleyen emirler iptal, o saatte dolan işlem hemen kapatılır (testte o işlem hiç alınmıyordu; canlıda küçük bir fark).
- Kaldıraç 3x sadece teminat için; her işlem kasanın 1/5'i, toplam risk testtekiyle aynı (yaklaşık 1x).
- Bitget demo 36 coinin 15'ini listeliyor; diğerleri atlanır.
- Dalga ve Pusula, Fitil'in tuttuğu coine girmez; Fitil de onlarınkine girmez.

## Durum: aday — kasa testini geçti (zayıf), Bitget demoda

## 2026-10-18 geliştirme turu (kurallar değişmedi)
36 coin, portföy en fazla 5, geliştirme 2022-24 / doğrulama 2025-01 → 2026-03:
| Deneme | Geliştirme kasa | Doğrulama kasa | Karar |
|---|---|---|---|
| Mevcut kural (%5, 3 saat) | +207.6% | +94.7% | kalıyor |
| Derinlik = ATR × 0.8 / 1.0 / 1.3 | +92 / +62 / +62% | +44 / +26 / +28% | red (daha az işlem, daha az kâr) |
| Kâr al %2 / %3 (3 saat) | +168 / +225% | +56 / +61% | red (doğrulamada geride) |
| Kâr al %3, 6 saat | +286% | +49% | red |
| 6 saat / 2 saat tutma | +247 / +191% | +29 / +75% | red |

**Asıl bulgu: coin sayısı.** Aynı kural 81 coinde (`config/pairs_wide81.json`): portföy 1.23 işlem/gün, +301% (DD 19%) / doğrulama 0.88 işlem/gün, +106% (DD 10.5%).
Derin Fitil 81 coinde: 0.20-0.25 işlem/gün, +90% / +54%. Bitget demo sadece 15 coin listelediği için demoda bu sıklık görülmüyor (15 coinde 2025: ~0.1 işlem/gün).
