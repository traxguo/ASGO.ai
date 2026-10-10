# nabiz — Hızlı aday: günlük trend yönünde 1 saatlik geri çekilmeden dönüş

Kod: [`strategies/retired/nabiz.py`](../strategies/retired/nabiz.py) (emekli)

## Hipotez
Pusula'nın gösterdiği tek sağlam şey: günlük trend güçlüyken (+3/-3) trend yönünde işlem açmak işe yarıyor. Pusula bunu 4 saatlik kırılımla ve az işlemle yapıyor. Nabız aynı günlük rejimi kullanır ama girişi 1 saatlik grafikte, kısa bir geri çekilmenin bitişinde arar: güçlü yükselişte 1 saatlik RSI aşırı satıma inip geri döndüğünde long, güçlü düşüşte aşırı alıma çıkıp geri döndüğünde short. Geri çekilmeler 1 saatlik grafikte sık olur, bu yüzden 36 coinde günde yaklaşık 1 işlem beklenir. Stop, geri çekilmenin dibinin (tepesinin) ötesine konur; bu doğal bir yapı seviyesidir. 5m/1m likidite denemelerinden (Aslan, AMS) farkı: tek, basit tetik ve 1 saatlik mumda daha geniş stop (masrafın R içindeki payı daha küçük).

## Yön
ikisi de

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Pusula'dakiyle birebir aynı puan (`strategies/candidates/pusula.py` → `regime_score`): kapanış EMA(50) üstü/altı, EMA(20) EMA(50) üstü/altı, 90 günlük getiri artı/eksi. Toplam -3 ile +3 arası.

## Giriş koşulları (1h, test öncesi sabitlendi, 2026-10-10)
Long (hepsi):
- [regime_up] Teknik: coinin günlük puanı = +3 | Açıklama: "Günlük trend güçlü yukarı (3/3)."
- [market_up] Teknik: BTC'nin günlük puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [pullback_end_up] Teknik: 1h RSI(14) bir önceki mumda 35'in altında, bu mumda 35 veya üstünde (aşağıdan yukarı kesme) | Açıklama: "1 saatlik grafikte geri çekilme bitti: RSI aşırı satımdan ({rsi}) yukarı döndü."

Short (hepsi):
- [regime_down] Teknik: coinin günlük puanı = -3 | Açıklama: "Günlük trend güçlü aşağı (3/3)."
- [market_down] Teknik: BTC'nin günlük puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [pullback_end_down] Teknik: 1h RSI(14) bir önceki mumda 65'in üstünde, bu mumda 65 veya altında (yukarıdan aşağı kesme) | Açıklama: "1 saatlik grafikte tepki yükselişi bitti: RSI aşırı alımdan ({rsi}) aşağı döndü."

Kararsız rejimde işlem yok.

## İşlem yönetimi
Ortak modül, değişiklik yok (ana sürüm): giriş bölgesi 0.25 ATR (1h ATR), stop 1.5 ATR veya son 10 mumun (10 saat) dip/tepesi + 0.1 ATR (uzak olan), Model B (TP1 2R'de yarısı + stop girişe, TP2 4R), sinyal 3 mum (3 saat) geçerli, en fazla 3x, işlem başı %1 risk. Aynı anda en fazla 3 açık işlem (Pusula ve demo ile aynı).

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 1h | sabit |
| Rejim zaman dilimi | 1d | sabit |
| EMA hızlı / yavaş, momentum | 20 / 50, 90 gün (Pusula) | sabit |
| RSI periyodu | 14 | 10-20 |
| RSI eşiği | 35 / 65 | 30-40 / 60-70 |
| Stop ATR katı | 1.5 (ortak) | 1.5-3 |
| En fazla açık işlem | 3 | sabit |

## Varyantlar (önceden belirlendi, hepsi raporlanır)
- `Nabiz_B`: ana sürüm, karar buna göre verilir.
- `NabizWide_B`: aynı girişler, stop 3 ATR (ortak modülün `stop_atr` değeri 1.5 → 3.0, başka değişiklik yok). Amaç teşhis: dar stopta masrafın R'yi ne kadar yediğini görmek. Bu varyant iyi çıksa bile bu turda ana sürüm yerine geçmez; ancak ayrı bir turda, yeni coinlerde de kontrol edilerek ele alınabilir.
- Ana sürüm ayrıca masraf x2 ile (`--fee 0.002`) çalıştırılır.

## Test planı (önceden)
- 36 coin (`config/pairs_all36.json`), en fazla 3 işlem, 1h mum, maliyet %0.1/emir, funding Freqtrade'in geçmiş funding + mark verisinden.
- Önce hile testi (lookahead-analysis).
- Geliştirme 2020-01 → 2024-12 (`--timerange 20200101-20250101`).
- Geçme şartı (docs/metrics.md): maliyet ve funding sonrası > 0R, DD ≤ %25, ≥ 100 işlem, coinlerin en az yarısı artıda, al-tut kıyası. Masraf x2'de hâlâ > 0R değilse "kırılgan".
- Geçerse doğrulama 2025-01 → 2026-03 bir kez (PF ≥ 1.2). Kasaya dokunulmaz.
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Durum: retired (2026-10-10)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Hile testi (lookahead-analysis, BTC/ETH/SOL/DOGE, 2021, 30 sinyal) | Geleceği görme yok. | — |
| 2026-10-10 | Geliştirme 2020-2024, 36 coin, max 3, `Nabiz_B` | 2509 işlem (günde 1.4), -0.09R, PF 0.93, DD %96.8, net -%93. Long -0.07R (1405, PF 0.99), short -0.11R (1104, PF 0.86). 12/36 coin artıda. Al-tut +%815. **Eşikleri geçemedi.** | `results/2026-10-10_nabiz_gelistirme_36coin/rapor.md` |
| 2026-10-10 | Aynı, `NabizWide_B` (stop 3 ATR, teşhis) | 980 işlem (günde 0.5), -0.07R, PF 0.91, DD %76. Long -0.11R, short +0.01R. 14/36 coin artıda. | aynı rapor |
| 2026-10-10 | Masraf x2 (`Nabiz_B`) | 2234 işlem, -0.15R, DD %99. | aynı rapor |
| 2026-10-10 | Masrafsız (teşhis, kartta önceden yoktu) | 2523 işlem, +0.01R (≈0), net -%27 (funding dahil). Tetikte avantaj yok. | aynı rapor |

## Notlar / öğrenilenler
- Günde ~1 işlem hedefi tuttu (36 coinde 1.4/gün), ama 1 saatlik RSI geri çekilme tetiği masraf öncesinde bile ≈0R. Masraf (~0.09R/işlem) ve funding bunu eksiye çeviriyor.
- Sonuç her yıl kötüleşti: 2020 +0.05R → 2024 -0.23R.
- Long'lar trend yönünde, yani kalabalıkla aynı tarafta açıldığı için 5 yılda ≈3000 USDT funding ödedi.
- Stopu genişletmek masrafın payını yarıya indirdi ama sonucu kurtarmadı: sorun masraftan önce, girişin kendisinde.
- Doğrulama yapılmadı (geçme şartı sağlanmadı), kasaya dokunulmadı.

## Emeklilik gerekçesi (varsa)
2026-10-10: Geliştirme döneminde (2020-2024, 36 coin) maliyet ve funding sonrası -0.09R, DD %97, coinlerin sadece üçte biri artıda, al-tutun çok gerisinde, masraf x2'de -0.15R. Masrafsız bile ≈0R: 1 saatlik geri çekilme tetiğinde avantaj yok. Önceden konan eşiklerin hiçbiri sağlanmadı. Kod `strategies/retired/nabiz.py`.
