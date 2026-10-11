# kirilim1s — Hızlı aday 2: günlük trend yönünde 1 saatlik kırılım

Kod: [`strategies/retired/kirilim1s.py`](../strategies/retired/kirilim1s.py) (emekli)

## Hipotez
Pusula'nın gösterdiği sağlam şey: günlük trend güçlüyken (+3/-3) trend yönündeki kırılımlar işe yarıyor. Pusula'nın aynı kırılım tetiği 1 saatlik grafikte de kârlıydı (tur 4 stres testi: 378 işlem, +0.80R), ama orada çıkış günlük trend bozulunca yapılıyordu ve işlem azdı. Kırılım1s aynı günlük rejimi kullanır, girişi 1 saatlik grafikte son 24 saatin (1 gün) tepesinin/dibinin kırılmasında arar ve işlemi sabit hedeflerle (2R/4R) kapatır. Sabit hedef işlemleri kısa tutar, 3 işlem yuvası daha sık boşalır; bu yüzden 36 coinde günde 1-3 işlem beklenir. Nabız'dan (geri çekilmeden alım, masrafsız bile ≈0R) farkı: fiyat zayıflarken değil, güçlenirken girmek.

## Yön
ikisi de (long ve short ayrı raporlanır)

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Pusula'dakiyle birebir aynı puan (`strategies/candidates/pusula.py` → `regime_score`, `daily_regime_frame`): kapanış EMA(50) üstü/altı, EMA(20) EMA(50) üstü/altı, 90 günlük getiri artı/eksi. Toplam -3 ile +3 arası. Bitcoin'in puanı da aynı şekilde hesaplanır.

## Giriş koşulları (1h, test öncesi sabitlendi, 2026-10-10)
Long (hepsi):
- [regime_up] Teknik: coinin günlük puanı = +3 | Açıklama: "Günlük trend güçlü yukarı (3/3)."
- [market_up] Teknik: BTC'nin günlük puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [breakout_up] Teknik: 1h kapanış önceki 24 mumun (bu mum hariç) en yüksek değerinin üstünde ve bir önceki mum böyle kapanmamış (serinin ilk mumu, Pusula'daki `first_true` ile aynı) | Açıklama: "Fiyat ({close}) son 24 saatin tepesini ({dc_upper}) kırdı."

Short (hepsi):
- [regime_down] Teknik: coinin günlük puanı = -3 | Açıklama: "Günlük trend güçlü aşağı (3/3)."
- [market_down] Teknik: BTC'nin günlük puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [breakout_down] Teknik: 1h kapanış önceki 24 mumun en düşük değerinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 24 saatin dibini ({dc_lower}) kırdı."

Kararsız rejimde işlem yok. "İlk kez" tanımı Pusula'yla aynıdır: kapanışlar kanalın dışında art arda devam ederken tekrar giriş sinyali çıkmaz; fiyat en az bir mum kanalın içinde kapanıp tekrar kırarsa yeni sinyal olur.

## İşlem yönetimi
Ortak modül (`strategies/common/`), değişiklik yok:
- Giriş bölgesi: kırılım mumunun kapanışı ile 0.25 ATR (1h ATR14) geri arası; limit emir bölgenin ortasında.
- Stop: 1.5 ATR veya son 10 mumun (10 saat) dip/tepesi + 0.1 ATR, hangisi uzaksa. Stop fiyatın %8'inden uzaksa sinyal yok.
- TP modeli: **Model B** (TP1 2R'de yarısı kapanır + stop girişe, TP2 4R). Nabız'la aynı.
- Sinyal geçerlilik süresi: 3 mum (3 saat); bölgeye gelmeden önce stop görülürse iptal.
- En fazla 3x kaldıraç (likidasyon stopun en az 2 katı uzakta), işlem başı %1 risk.
- Aynı anda en fazla **3 açık işlem**.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 1h | sabit |
| Rejim zaman dilimi | 1d | sabit |
| EMA hızlı / yavaş, momentum | 20 / 50, 90 gün (Pusula) | sabit |
| Kırılım kanalı | 24 mum (1 gün) | 12-36 |
| Piyasa filtresi | BTC puanı ≥ +1 / ≤ -1 | sabit |
| Stop ATR katı | 1.5 (ortak) | sabit |
| En fazla açık işlem | 3 | sabit |

## Varyantlar (önceden belirlendi, hepsi raporlanır; karar sadece ana sürüme göre)
- `Kirilim1s_B`: ana sürüm, karar buna göre verilir.
- `Kirilim1s12_B`: kanal 24 yerine 12 mum (yarım gün). Amaç: daha kısa kanal daha çok işlem veriyor mu, kârı bozuyor mu. Teşhis; iyi çıksa bile bu turda ana sürüm yerine geçmez.
- `Kirilim1sNoBTC_B`: Bitcoin filtresi yok. Amaç: BTC filtresinin katkısını görmek. Teşhis; ana sürüm yerine geçmez.
- Ana sürüm ayrıca masraf x2 ile (`--fee 0.002`) ve teşhis için masrafsız (`--fee 0`) çalıştırılır.

## Test planı (önceden)
- 36 coin (`config/pairs_all36.json`), en fazla 3 işlem, 1h mum, maliyet %0.1/emir (komisyon + kayma), funding Freqtrade'in geçmiş funding + mark verisinden.
- Önce hile testi (lookahead-analysis).
- Geliştirme 2020-01 → 2024-12 (`--timerange 20200101-20250101`).
- İşlem sıklığı hedefi: günde 1-3 işlem (5 yılda ≥ ~1500). Hedef tutmazsa bu raporlanır; kurallar ona göre değiştirilmez.
- Geçme şartı (docs/metrics.md): maliyet ve funding sonrası > 0R, PF ≥ 1.2, DD ≤ %25, ≥ 100 işlem, coinlerin en az yarısı artıda, al-tut kıyası. Masraf x2'de hâlâ > 0R değilse "kırılgan".
- Geçerse doğrulama 2025-01 → 2026-03 bir kez. Kasaya (2026-04 sonrası) dokunulmaz.
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Durum: retired (2026-10-10)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Hile testi (lookahead-analysis, BTC/ETH/SOL/DOGE, 2021, 30 sinyal) | Geleceği görme yok. | — |
| 2026-10-10 | Geliştirme 2020-2024, 36 coin, max 3, `Kirilim1s_B` | 1112 işlem (günde 0.6), +0.06R, PF 1.04, DD %48.2, net +%53. Long +0.12R (694, PF 1.11), short -0.04R (418, PF 0.93). 26/36 coin artıda. Al-tut +%815. **Eşikleri geçemedi** (PF, DD). | `results/2026-10-10_kirilim1s_gelistirme_36coin/rapor.md` |
| 2026-10-10 | Masraf x2 (`Kirilim1s_B`) | 1112 işlem, +0.006R, PF 0.98, net -%17, DD %65. Kırılgan. | aynı rapor |
| 2026-10-10 | Masrafsız (teşhis) | +0.12R, PF 1.11, DD %38 (funding dahil). | aynı rapor |
| 2026-10-10 | `Kirilim1s12_B` (kanal 12, teşhis) | 1270 işlem (günde 0.7), +0.12R, PF 1.12, DD %51. Long +0.15R, short +0.09R. 22/36 coin artıda. | aynı rapor |
| 2026-10-10 | `Kirilim1sNoBTC_B` (BTC filtresi yok, teşhis) | 1180 işlem, +0.06R, PF 1.06, DD %36. Long +0.10R, short +0.01R. | aynı rapor |

## Notlar / öğrenilenler
- 1 saatlik grafikte trend yönünde kırılımın masraf öncesi küçük bir avantajı var (+0.12R; Nabız'ın geri çekilme tetiğinde ≈0R). Ama masraf (~0.06R) ve funding sonrası avantaj çok ince.
- Günde 1-3 işlem hedefi tutmadı (0.6/gün). Sinyal az değil: 3 işlem sınırı dolu olduğu için binlerce sinyal alınamadı. İşlemler ortalama 3.5 gün sürüyor; 3 yuva ile günde en fazla ~0.85 işlem mümkün.
- Kâr 2020-2021'den geliyor, 2024'te eksi. Short tarafı eksi; long'lar 5 yılda ≈4100 USDT funding ödedi.
- Doğrulama yapılmadı (geçme şartı sağlanmadı), kasaya dokunulmadı.

## Emeklilik gerekçesi (varsa)
2026-10-10: Geliştirme döneminde (2020-2024, 36 coin) maliyet ve funding sonrası +0.06R ama PF 1.04 (eşik 1.2), DD %48 (eşik %25), masraf x2'de PF 0.98 ve net eksi (kırılgan), al-tutun çok gerisinde; işlem sıklığı da hedefin altında (günde 0.6). Önceden konan eşikler sağlanmadı. Kod `strategies/retired/kirilim1s.py`.
