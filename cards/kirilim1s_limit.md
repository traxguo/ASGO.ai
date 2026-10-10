# kirilim1s_limit — Hızlı aday 3: Kırılım1s sinyalleri, limit (maker) emirle giriş

Kod: [`strategies/retired/kirilim1s_limit.py`](../strategies/retired/kirilim1s_limit.py) (emekli)

## Hipotez
Kırılım1s'in (`cards/kirilim1s.md`) sinyallerinde masraf öncesi küçük bir avantaj var (+0.12R), ama masraf ve funding bunun yarısını yiyor (+0.06R). Aynı sinyallere **limit emirle** (maker) girersek giriş komisyonu taker'ın üçte birine iner ve kayma olmaz. Ayrıca limit fiyatı kırılan seviyenin kendisine (eski 24 saatlik tepe/dip) konursa, fiyat seviyeyi geri test ettiğinde daha iyi fiyattan girilir. Risk: limit emir en çok kötü giden işlemlerde dolar (fiyat geri döndüğü için dolar), iyi giden kırılımlar hiç geri gelmeden kaçar ("ters seçim"). Bu test ikisinin toplamını ölçer.

## Yön
ikisi de (long ve short ayrı raporlanır)

## Bugünkü maliyet modeli (bu test öncesi durum, 2026-10-10)
- `config/base.json` → `fee: 0.001`: **her emir** (giriş, TP1, TP2, stop) için %0.05 Binance taker komisyonu + %0.05 kayma = %0.1. Emir tipine bakılmaz.
- Not: Kırılım1s_B de aslında limit emirle giriyordu (ortak modül, bölgenin ortası, kapanış − 0.125 ATR), TP'ler de limit emirdi; ama hepsine taker + kayma ücreti yazıldı. Yani "limit emir" yeni değil; yeni olan **emir tipine göre ücret** ve **limit fiyatının kırılan seviyeye konması**.

## Bu kartta kullanılan maliyet (Bitget USDT-M, yayımlanan standart oranlar, VIP 0)
| Emir | Tip | Komisyon | Kayma | Toplam |
|---|---|---|---|---|
| Giriş (limit, piyasanın altında/üstünde bekler) | maker | %0.02 | 0 | **%0.02** |
| Giriş, emir konduğu anda fiyat limiti zaten geçmişse (hemen dolar) | taker | %0.06 | %0.05 | **%0.11** |
| TP1 / TP2 (bekleyen limit emir) | maker | %0.02 | 0 | **%0.02** |
| Stop (piyasa emri) | taker | %0.06 | %0.05 | **%0.11** |
- Funding: Freqtrade'in geçmiş funding + mark verisinden (Binance), değişiklik yok.
- Masraf x2 testi: tüm oranlar iki katı (maker %0.04, stop %0.22).
- Limit emirlerde kayma yok sayılır, çünkü dolum fiyatı limit fiyatıdır; onun yerine aşağıdaki "içinden geçme" şartı kullanılır.
- Teknik not: Freqtrade bir işlemde tek giriş ve tek çıkış ücret oranı tutar. TP1 (maker) sonrası stop (taker) gelirse, çıkış ücreti iki emrin tutarlarıyla ağırlıklı ortalama yazılır; toplam ücret birebir doğru çıkar.

## Dolum (fill) nasıl karar verilir (iyimser dolumdan kaçınmak için)
- Freqtrade'in gerçek limit emir backtest mekaniği kullanılır: emir, sinyal mumundan sonraki mumun açılışında `custom_entry_price` fiyatıyla konur, `unfilledtimeout` ile N mum sonra iptal olur, fiyat stopa önce değerse (`check_entry_timeout`) iptal olur.
- Freqtrade normalde fiyat limite **dokununca** doldurur (mumun en düşüğü ≤ limit). Bu iyimserdir: sırada bekleyen emir dokunuşta dolmayabilir.
- Bu kartta daha sıkı kural: long alış limiti ancak mumun en düşüğü **limitin en az 1 tick ve en az fiyatın %0.02'si kadar altına** inerse dolar (short için en yüksek, limitin o kadar üstüne çıkmalı). Dolum fiyatı yine limit fiyatıdır. Aynı kural TP limit emirlerine de uygulanır. Stop emirleri piyasa emridir, bu kural onlara uygulanmaz.
- Emir konduğu anda fiyat limiti zaten geçmişse (long için mumun açılışı ≤ limit), Freqtrade limit fiyatından doldurur (gerçekte açılıştan, daha iyi fiyattan dolardı: kötümser), ücret taker + kayma yazılır.
- Dolmayan emir **işlem sayılmaz**, iptal sayılır. Dolma oranı = dolan / (dolan + süresi dolan + önce stopa değdiği için iptal edilen).

## Giriş koşulları (1h, Kırılım1s_B ile birebir aynı, test öncesi sabitlendi 2026-10-10)
Long (hepsi):
- [regime_up] Teknik: coinin günlük Pusula puanı = +3 (son kapanmış gün) | Açıklama: "Günlük trend güçlü yukarı (3/3)."
- [market_up] Teknik: BTC'nin günlük puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [breakout_up] Teknik: 1h kapanış önceki 24 mumun en yüksek değerinin üstünde, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 24 saatin tepesini ({dc_upper}) kırdı."

Short (hepsi):
- [regime_down] Teknik: coinin günlük puanı = -3 | Açıklama: "Günlük trend güçlü aşağı (3/3)."
- [market_down] Teknik: BTC'nin günlük puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [breakout_down] Teknik: 1h kapanış önceki 24 mumun en düşük değerinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 24 saatin dibini ({dc_lower}) kırdı."

## İşlem yönetimi
Ortak modül (`strategies/common/`) fonksiyonları; sadece giriş fiyatının yeri değişir:
- **Giriş (ana sürüm):** tek fiyatlı limit emir, **kırılan seviyenin kendisinde**: long `dc_upper` (kırılan 24 saatlik tepe), short `dc_lower` (kırılan 24 saatlik dip). Yani fiyatın seviyeyi geri test etmesi beklenir. Bölge genişliği 0 (bölgenin altı = üstü = limit).
  Açıklama cümlesi: "Giriş: kırılan seviyeye ({long_entry}) limit emir, 3 saat geçerli; geri gelmezse işlem yok."
- Stop: ortak kural, girişe göre: 1.5 ATR (1h ATR14) veya son 10 mumun dip/tepesi ± 0.1 ATR, hangisi uzaksa. Stop fiyatın %8'inden uzaksa sinyal yok.
- R = limit fiyatı ile stop arası. TP modeli **Model B**: TP1 2R'de yarısı (limit), stop girişe (+%0.15 tampon), TP2 4R (limit).
- Sinyal geçerlilik süresi: **3 mum (3 saat)**; dolmazsa iptal; dolmadan önce stopa değerse iptal.
- En fazla 3x kaldıraç (likidasyon stopun en az 2 katı uzakta), işlem başı %1 risk, aynı anda en fazla **3 açık işlem** (bekleyen limit emir de bir yuva tutar).

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 1h | sabit |
| Rejim | günlük Pusula puanı ±3, BTC ±1 | sabit (Kırılım1s) |
| Kırılım kanalı | 24 mum | sabit (Kırılım1s) |
| Limit fiyatı | kırılan seviye (`dc_upper` / `dc_lower`) | sabit |
| Limit geçerlilik (N) | 3 mum | 3-6 (varyant 6) |
| İçinden geçme şartı | max(1 tick, %0.02) | sabit |
| Maker / taker / stop kayması | %0.02 / %0.06 / %0.05 | sabit (Bitget VIP 0) |
| En fazla açık işlem | 3 | sabit |

## Varyantlar (önceden belirlendi, en fazla 2; hepsi raporlanır; karar sadece ana sürüme göre)
- `Kirilim1sLimit_B`: **ana sürüm**, karar buna göre.
- `Kirilim1sLimit6_B`: aynı, limit 6 mum (6 saat) geçerli. Amaç: daha uzun bekleme dolma oranını artırıyor mu, ters seçimi kötüleştiriyor mu.
- `Kirilim1sLimitZone_B`: limit fiyatı Kırılım1s_B'nin kendi giriş fiyatı (ortak bölgenin ortası, kapanış ∓ 0.125 ATR), 3 mum. Amaç: sadece ücret modelinin (maker/taker ayrımı + içinden geçme şartı) etkisini ayırmak; Kırılım1s_B ile aynı girişler, farklı ücret.
- Teşhis (varyant değil, önceden yazıldı): ana sürüm **masraf x2** ve **masrafsız** (komisyon ve kayma 0, funding ve içinden geçme şartı duruyor). Senaryo (karar için kullanılmaz; 2026-10-10'da sonuçlara bakılmadan, ana oturumun isteğiyle eklendi): `Kirilim1sLimitLowFee_B`, "düşük ücretli borsa" (bir arkadaşın MEXC'de 6000 USD'lik işlemde ~1 USD ödediği bildirildi): her emir sabit %0.03 (%0.02 komisyon + %0.01 kayma), `--fee 0.0003`. Ayrıca kod dışı bir teşhis: kısıtsız (yuva sınırı olmadan) tüm sinyallerde, seviyeye konan limit emrin dolup dolmamasına göre Kırılım1s_B girişinin masrafsız sonucu ayrı ayrı hesaplanır (ters seçim ölçümü).

## Test planı (önceden)
- 36 coin (`config/pairs_all36.json`), en fazla 3 işlem, 1h, maliyet yukarıdaki tablo, funding dahil.
- Önce hile testi (lookahead-analysis, BTC/ETH/SOL/DOGE, 2021).
- Geliştirme 2020-01 → 2024-12 (`--timerange 20200101-20250101`).
- Raporda long/short ayrı: günde işlem, dolma oranı, ortalama R, PF, max DD, masraf x2, al-tut kıyası.
- Geçme şartı (docs/metrics.md): maliyet + funding sonrası > 0R, PF ≥ 1.2, DD ≤ %25, ≥ 100 işlem, coinlerin en az yarısı artıda, al-tut kıyası. Masraf x2'de > 0R değilse "kırılgan".
- Sadece ana sürüm geçerse doğrulama 2025-01 → 2026-03 bir kez. Kasaya (2026-04 sonrası) dokunulmaz.
- Sonuca bakıp kural, eşik, oran veya varyant değiştirilmez.

## Durum: retired (2026-10-10)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Hile testi (lookahead-analysis, BTC/ETH/SOL/DOGE, 2021, 30 sinyal) | Geleceği görme yok. | — |
| 2026-10-10 | Geliştirme 2020-2024, 36 coin, max 3, `Kirilim1sLimit_B` (Bitget ücretleri) | 1183 işlem (günde 0.65), dolma oranı %70 (1183/1687), **+0.018R**, PF 1.00, DD %61.2, net -%5. Long +0.044R (746, PF 1.03), short -0.026R (437, PF 0.95). 16/36 coin artıda. Al-tut +%815. **Eşikleri geçemedi.** | `results/2026-10-10_kirilim1s_limit_gelistirme_36coin/rapor.md` |
| 2026-10-10 | Masraf x2 (`Kirilim1sLimitCost2x_B`) | -0.016R, PF 0.96, net -%36, DD %70. Kırılgan. | aynı rapor |
| 2026-10-10 | Masrafsız teşhis (`Kirilim1sLimitCost0_B`, funding dahil) | +0.052R, PF 1.03, DD %50. Masraf işlem başına ≈0.034R (Kırılım1s_B'de ≈0.06R). | aynı rapor |
| 2026-10-10 | Düşük ücretli borsa senaryosu (`Kirilim1sLimitLowFee_B`, her emir %0.03; karar dışı) | +0.033R, PF 1.01, net +%13, DD %56. | aynı rapor |
| 2026-10-10 | `Kirilim1sLimit6_B` (6 saat geçerli) | 1216 işlem, dolma %76, +0.079R, PF 1.06, DD %40. Long +0.12R, short +0.01R. | aynı rapor |
| 2026-10-10 | `Kirilim1sLimitZone_B` (Kırılım1s_B girişi, yeni ücret) | 1102 işlem, dolma %90, +0.077R, PF 1.06, DD %43. Long +0.13R, short -0.01R. | aynı rapor |
| 2026-10-10 | Ters seçim teşhisi (kısıtsız, tüm sinyaller, masraf öncesi) | Seviyedeki limit dolan sinyallerde Kırılım1s_B girişi +0.01R, dolmayanlarda +0.37R. Dolma oranı long %72, short %65 (6 saatte %78 / %73). | aynı rapor |

## Notlar / öğrenilenler
- Emir tipine göre ücret (maker giriş/TP, taker stop) masrafı yaklaşık yarıya indiriyor (işlem başına ~0.06R → ~0.03R).
- Ama limit fiyatı kırılan seviyeye koymak ters seçim yaratıyor. Fiyatın geri test ettiği kırılımlar ≈0R, geri dönmeden gidenler en kârlıları (+0.37-0.44R). Limit en iyi işlemleri kaçırıyor. Masraf öncesi avantaj +0.12R'den +0.05R'ye düştü.
- Düşük ücretli borsa (%0.03/emir) bile yetmiyor: sorun ücretten çok sinyalin avantajının küçük olması.
- Bekleyen limit emir de 3 yuvadan birini tutuyor. İşlem sıklığı yine günde ~0.65.
- Teknik: Freqtrade strateji geri çağrılarına işlemin kopyasını veriyor, bu yüzden ücret orada değiştirilemiyor. Ücret ve "içinden geçme" kuralı Freqtrade'in dolum kararına sarmalayıcıyla eklendi; sadece `fill_through_pct` olan stratejiye etki ediyor.

## Emeklilik gerekçesi (varsa)
2026-10-10: Geliştirme döneminde (2020-2024, 36 coin) Bitget ücretleriyle, maliyet ve funding sonrası +0.018R. PF 1.00 (eşik 1.2), DD %61 (eşik %25), coinlerin %44'ü artıda (eşik %50), masraf x2'de eksi (kırılgan), al-tutun çok gerisinde. Önceden konan eşikler sağlanmadı. Doğrulama ve kasa kullanılmadı. Kod `strategies/retired/kirilim1s_limit.py`.
