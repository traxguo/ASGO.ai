# pusula_hizli — Hızlı Pusula: gevşek günlük rejim + 4 saatlik kırılım + sabit hedef

Kod: [`strategies/retired/pusula_hizli.py`](../strategies/retired/pusula_hizli.py) (emekli)

## Hipotez
Pusula'nın fikri (günlük trend yönünde, Bitcoin de aynı taraftayken 4 saatlik kırılımda gir) doğru ama çok yavaş: 36 coinde ayda ~3 işlem, çünkü trend işlemleri haftalarca sürüyor ve 3 işlem sınırı hep dolu. Proje sahibi günde 1-3 işlem istiyor. Hızlı Pusula aynı kırılım tetiğini kullanır, ama (1) günlük rejimi gevşetir (3 işaretin 2'si yeterli), (2) trend çıkışı yerine sabit hedefle (2R / 4R) çıkar, böylece işlemler kısa sürer, (3) aynı anda 5 işleme izin verir. Böylece daha çok coin ve daha çok an işlem için uygun olur.

Bilinen risk (testten önce yazıldı): Pusula'nın sabit hedefli ilk sürümü (`Pusula_B`, puan ±3, 6 coin) geliştirmede sadece +0.08R, DD %35 verdi. Gevşek rejim ve sabit hedef bu zayıflığı büyütebilir. Test bunu ölçmek için.

## Yön
ikisi de (long ve short ayrı raporlanır; karar ikisinin toplamına göre verilir, sonuca bakıp "sadece long"a geçilmez)

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Pusula'dakiyle birebir aynı puan (`strategies/candidates/pusula.py` → `regime_score`): kapanış EMA(50) üstü/altı, EMA(20) EMA(50) üstü/altı, 90 günlük getiri artı/eksi. Toplam -3 ile +3 arası. Bitcoin puanı da aynı şekilde.

## Giriş koşulları (4h, test öncesi sabitlendi, 2026-10-10)
Long (hepsi):
- [regime_up] Teknik: coinin günlük puanı ≥ +2 | Açıklama: "Günlük trend yukarı ({score_1d}/3)."
- [market_up] Teknik: BTC'nin günlük puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [breakout_up] Teknik: 4h kapanış önceki 20 mumun tepesinin üstünde, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun tepesini ({dc_upper}) kırdı."

Short (hepsi):
- [regime_down] Teknik: coinin günlük puanı ≤ -2 | Açıklama: "Günlük trend aşağı ({score_1d}/3)."
- [market_down] Teknik: BTC'nin günlük puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [breakout_down] Teknik: 4h kapanış önceki 20 mumun dibinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun dibini ({dc_lower}) kırdı."

Puan -1, 0, +1 iken (kararsız) işlem yok.

## İşlem yönetimi
Ortak modül (`strategies/common/`), değişiklik yok:
- Giriş bölgesi: kırılım mumu kapanışı ile 0.25 ATR geri çekilme arası, limit emir bölgenin ortasında.
- Stop: 1.5 ATR veya son 10 mumun dip/tepesi + 0.1 ATR (uzak olan). Stop fiyatın %8'inden uzaksa sinyal yok.
- TP modeli: **Model B** (TP1 2R'de yarısı kapanır + stop girişe çekilir, TP2 4R'de kalanı). Trend çıkışı yok.
- Sinyal geçerlilik süresi: 3 mum (12 saat); fiyat önce stopa giderse iptal.
- Kaldıraç en fazla 3x, likidasyon stopun en az 2 katı uzakta; işlem başı %1 risk.
- **Süre stopu yok:** ortak modülde süre stopu tanımlı değil. Yeni bir kural eklemek yerine bu turda kullanılmadı.
- Aynı anda en fazla **5** açık işlem.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 4h | sabit |
| Rejim zaman dilimi | 1d | sabit |
| EMA hızlı / yavaş, momentum | 20 / 50, 90 gün (Pusula) | sabit |
| Rejim eşiği | ±2 | ±2 / ±3 |
| Piyasa filtresi | BTC puanı ≥ +1 / ≤ -1 | sabit |
| Kanal | 20 mum | 15-30 |
| En fazla açık işlem | 5 | 5-8 |
| Coinler | 36 (`config/pairs_all36.json`) | sabit |

## Varyantlar (önceden belirlendi, en fazla 2, hepsi raporlanır)
- `PusulaHizli_B`: ana sürüm, karar buna göre verilir.
- Varyant 1, `PusulaHizli3_B`: rejim eşiği ±3 (Pusula'nın sıkı rejimi), başka her şey aynı. Amaç: gevşetmenin işlem sayısına ve kalitesine etkisini ayırmak.
- Varyant 2: ana sürüm, aynı anda en fazla **8** işlem (`--max-open-trades 8`). Amaç: işlem sınırının etkisini görmek.
- Varyantlar ana sürümden iyi çıksa bile bu turda ana sürümün yerine geçmez; ancak ayrı bir turda, yeni veride ele alınabilir.
- Ana sürüm ayrıca masraf x2 ile (`--fee 0.002`) ve teşhis için masrafsız (`--fee 0`) çalıştırılır.

## Test planı (önceden)
- Önce hile testi (lookahead-analysis).
- Geliştirme 2020-01 → 2024-12 (`--timerange 20200101-20250101`), 36 coin, 4h + günlük, maliyet %0.1/emir, funding geçmiş veriden.
- İşlem sıklığı hedefi: günde 1-3 işlem (5 yılda ≥ ~1500).
- Geçme şartı (docs/metrics.md): maliyet ve funding sonrası > 0R, PF ≥ 1.2, DD ≤ %25, ≥ 100 işlem, coinlerin en az yarısı artıda, al-tut kıyası. Masraf x2'de hâlâ > 0R değilse "kırılgan".
- Geçerse doğrulama 2025-01 → 2026-03 bir kez. Kasaya (2026-04 sonrası) dokunulmaz.
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Düzeltme turu (2026-10-10, ilk sonuçtan sonra ama düzeltilmiş sürüm çalıştırılmadan önce yazıldı)
**Tanım hatası bulundu:** puan üç tane ±1 işaretin toplamı, yani normalde sadece -3, -1, +1, +3 olabilir (+2 sadece bir işaret tam sıfırsa olur, pratikte hiç). Bu yüzden yukarıdaki "puan ≥ +2" şartı Pusula'nın "puan = +3" şartıyla **birebir aynı** çıktı: ana sürüm ile varyant 1 aynı işlemleri verdi (36 coinde 2020-2024: 524 işlem, günde 0.3). Rejim hiç gevşemedi.
Hipotezdeki niyet ("3 işaretin 2'si yeterli") puan ≥ +1 / ≤ -1 demek. Düzeltme:
- `PusulaHizli1_B` (yeni ana sürüm, karar buna göre): [regime_up] coinin günlük puanı ≥ +1 (üç işaretin en az ikisi yukarı) | Açıklama: "Günlük trend çoğunlukla yukarı ({score_1d}/3)." Short için [regime_down] ≤ -1. Diğer her şey aynı (BTC ≥ +1 / ≤ -1, 4h kırılım, Model B, en fazla 5 işlem, 36 coin).
- Varyant 1 (sıkı rejim ±3) = ilk turun sonucu, yeniden çalıştırılmaz.
- Varyant 2 (en fazla 8 işlem), masraf x2 ve masrafsız teşhis düzeltilmiş ana sürümle çalışır.
- Başka hiçbir kural, eşik veya varyant değiştirilmez. Düzeltilmiş sürüm geçmezse ±3 sürümüne "daha iyiydi" diye dönülmez; o da kendi başına geçemedi (aşağıda).
- `PusulaHizli_B` ve `PusulaHizli3_B` kayıt için kodda kalır.

## Durum: retired (2026-10-10)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Hile testi (lookahead-analysis, BTC/ETH/SOL/DOGE/ADA, 2021, 30 sinyal), `PusulaHizli_B` ve `PusulaHizli1_B` | Geleceği görme yok. | — |
| 2026-10-10 | İlk tur: geliştirme 2020-2024, 36 coin, en fazla 5, `PusulaHizli_B` (±2) ve `PusulaHizli3_B` (±3) | İkisi birebir aynı (puan hep tek sayı, ±2 = ±3): 524 işlem (günde 0.30), +0.23R, PF 1.24, DD %25.9, net +%173. Long +0.21R (310, PF 1.13), short +0.25R (214, PF 1.39). 2023 +0.07R, 2024 ≈0R. Geçemedi (DD, işlem sıklığı). | `results/2026-10-10_pusula_hizli_gelistirme_36coin/rapor.md` |
| 2026-10-10 | Düzeltme turu: `PusulaHizli1_B` (±1), aynı dönem | 599 işlem (günde 0.34), +0.09R, PF 1.07, DD %46.2, net +%45. Long +0.09R (376, PF 1.03), short +0.10R (223, PF 1.14). 22/36 coin artıda. Al-tut +%821. **Geçemedi.** | aynı rapor |
| 2026-10-10 | Masraf x2 / masrafsız (`PusulaHizli1_B`) | x2: +0.06R, PF 1.03, DD %52.5 (long PF 0.99). Masrafsız: +0.13R, PF 1.12, DD %39.1. | aynı rapor |
| 2026-10-10 | Varyant 2: en fazla 8 işlem (`PusulaHizli1_B`) | 901 işlem (günde 0.51), +0.11R, PF 1.08, DD %54.1. | aynı rapor |

## Notlar / öğrenilenler
- Pusula puanı üç ±1 işaretin toplamı, hep tek sayı (-3, -1, +1, +3). "≥ +2" eşiği "= +3" ile aynıdır. Bundan sonra eşikler ±1 veya ±3 olarak yazılmalı.
- Rejimi ±1'e gevşetmek işlem sayısını sadece %14 artırdı ama kaliteyi bozdu (+0.23R → +0.09R, DD %26 → %46).
- 4h kırılımda işlem sıklığını kısıtlayan rejim değil: ham sinyal günde 5.6, ama %65'inde stop (1.5 ATR / 10 mum dibi, uzak olan) fiyatın %8'inden uzak, kural gereği sinyal yok. Kalanların %56'sı aynı mumda 5+ coinde birden geliyor. İşlemler ortalama 8.6 gün sürüyor (Model B ile bile).
- 4h + sabit hedefle günde 1-3 işlem, bu ortak kurallarla mümkün görünmüyor (8 slotla bile günde 0.5).
- Doğrulamaya bakılmadı, kasaya dokunulmadı.

## Emeklilik gerekçesi (varsa)
2026-10-10: Geliştirme döneminde (2020-2024, 36 coin, en fazla 5 işlem) ana sürüm `PusulaHizli1_B` maliyet ve funding sonrası +0.09R ama PF 1.07 (< 1.2), DD %46 (> %25), al-tutun çok gerisinde, masraf x2'de long kârsız. İşlem sıklığı hedefi tutmadı: günde 0.34 (≥ ~1500 hedefine karşı 599 işlem). Önceden tanımlı varyantlar da geçmedi (±3: DD %25.9, günde 0.30; 8 işlem: DD %54). İlk turdaki "≥ ±2" tanım hatası kartta açıkça yazıldı. Kod `strategies/retired/pusula_hizli.py`.
