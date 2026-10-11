# Çıkarma turu 3 — 2R'de başabaş kuralı kaldırıldı — 2026-10-11 (temel: PusulaV2NoBtcScore1)

## GUO'ya not
- "Fiyat 2R lehte gidince stopu girişe çek" kuralını çıkardım (`PusulaV2NoBe`). Stop artık hiç oynamıyor; işlem ya ilk stopta, ya günlük EMA20 çıkışında, ya da BTC-dönüş çıkışında kapanıyor.
- İki coin grubunda da işlem başına sonuç biraz daha iyi: eski 16'da +1.30R → +1.35R, yeni 20'de +0.52R → +0.61R. Toplam R de ikisinde daha yüksek (eski 16'da sadece +1.4R, yani neredeyse aynı).
- Bedeli: eski 16'da en büyük düşüş %21.5 → %23.7 (hâlâ %25 sınırının altında), PF 2.21 → 2.06. Yeni 20'de DD %22.2 → %22.6.
- Karar: **kabul** (daha az kural, sonuç aynı ya da biraz daha iyi). Uyarı: eski 16'da kazanç çok ince; yeni 20'deki kazancın yarısından fazlası tek coinden (FIL +10.7R).

## Sonuç
| Liste | Sürüm | İşlem | Ortalama R | Toplam R | PF | Max DD | Net |
|---|---|---|---|---|---|---|---|
| Eski 16 | PusulaV2NoBtcScore1 (temel) | 238 | +1.30R | 309.88 | 2.21 | %21.5 | +%824.2 |
| Eski 16 | Başabaş yok | 230 | **+1.35R** | 311.26 | 2.06 | %23.7 | +%827.3 |
| Yeni 20 | PusulaV2NoBtcScore1 (temel) | 201 | +0.52R | 104.81 | 1.47 | %22.2 | +%115.3 |
| Yeni 20 | Başabaş yok | 193 | **+0.61R** | 117.72 | 1.53 | %22.6 | +%134.2 |

Hepsi sadece long (short 0 işlem). Al-tut (eşit ağırlık, aynı dönem): eski 16 +%931.5 (ortalama düşüş %89.2), yeni 20 +%194.7 (ortalama düşüş %97.6).
Ayrıntılı raporlar: `wide16/rapor.md`, `new20/rapor.md`.

**Karar: kabul** (iki listede de ortalama R ve toplam R daha iyi; DD eski 16'da 2.2 puan arttı ama %25 sınırının altında, yeni 20'de neredeyse aynı). İşlem sayısı: eski 16'da -8, yeni 20'de -8 (stop girişte değil, ilk yerinde kaldığı için bazı işlemler daha uzun açık kalıyor, 3 işlem sınırı daha sık dolu).

## Ne değişti
`PusulaV2NoBe(PusulaV2NoBtcScore1)`: sadece `custom_stoploss` değişti; her zaman planlanan ilk stopu döndürüyor (2R'de girişe çekme yok). Giriş, kırılım, BTC-dönüş çıkışı, EMA20 çıkışı aynı. `PusulaTrendLong`, `PusulaV2` ve önceki sınıflar değişmedi.

Çıkış türleri: eski 16'da "BE" (başabaşta kapanan) %12.2 → %0, stop %37.4 → %41.7, trend çıkışı %50.4 → %58.3. Yeni 20'de BE %14.4 → %0.5, stop %47.8 → %53.9, trend çıkışı %37.8 → %45.6. Yani başabaşta kapanan işlemlerin bir kısmı ilk stopa kadar düştü, ama daha fazlası trend çıkışına kadar dayanıp kazandı.

## Ayarlar (tur 1-2 ile aynı)
- `--timerange 20200101-20261001`, 4h, `--timeframe-detail 1h`, en fazla 3 işlem, sadece long.
- Eski 16: `config/pairs_wide16.json`; yeni 20: `config/pairs_new20.json`.
- Komut: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting --config config/pairs_<liste>.json --strategy-list PusulaV2NoBtcScore1 PusulaV2NoBe --timerange 20200101-20261001 --timeframe 4h --timeframe-detail 1h --max-open-trades 3 --export trades`, rapor `scripts/make_report.py`.
- Maliyet: emir başına %0.1 (komisyon + kayma), funding geçmiş veriden. İşlem başına risk %1, kaldıraç en fazla 3x.
- Temel (PusulaV2NoBtcScore1) rakamları tur 2 raporuyla birebir aynı çıktı (238 / 201 işlem, 309.88R / 104.81R), yani ayarlar doğru kopyalandı.
- Not: bu dönem kasayı (2026-04 → 2026-09) da içeriyor; önceki turlar da aynı aralığı kullandı, yeni bir kasa kullanımı yok.

## Coin bazında dağılım
Coin bazında toplam R farkı (yeni − temel):
- Eski 16: 5 coin daha iyi, 7 coin daha kötü, 4 coin aynı. Toplam fark +1.4R. En iyi: BNB +3.8R, LINK +2.2R, ETC +1.4R. En kötü: BTC -2.8R, BCH -1.2R, XLM/ADA/DOGE ≈ -1.0R. Yani eski 16'da fiilen fark yok.
- Yeni 20: 8 coin daha iyi, 7 coin daha kötü, 5 coin aynı. Toplam fark +12.9R. FIL tek başına +10.7R, VET +5.3R; bu ikisi hariç fark ≈ -3.0R. En kötü: DASH -4.1R, AAVE -1.9R.
- Yorum: kazanç tur 2 kadar tek coine yığılmış değil ama yine birkaç coinden geliyor. Kuralın kendisi işe yarıyor demek zor; daha doğru okuma: "2R'de başabaş kuralı bir şey kazandırmıyor", bu yüzden çıkarılması (daha az kural) kabul.
