# momentum_5m — 5 dakikalık momentum + kırılım (oynaklık filtresiyle)

Kod: [`strategies/candidates/momentum_5m.py`](../strategies/candidates/momentum_5m.py)

## Hipotez
Proje sahibinin (GUO) bir videodan getirdiği scalp fikri. Mumların boyu büyümeye başladığında (oynaklık artıyor), fiyat 20 mum öncesinden yüksekte ve son 20 mumun en yüksek kapanışını yeşil bir mumla geçiyorsa hareketin kısa süre devam etmesi beklenir. Short tarafı bunun aynasıdır. Hedef 5 dakikalık grafikte sık ve kısa işlem.

Bu test **ilk elemedir**: "bu fikir bir şansı hak ediyor mu?" sorusuna cevap arar. Sadece geliştirme verisi (2022-2024) kullanılır.

## Yön
ikisi de (long ve short ayrı raporlanır)

## Giriş koşulları (5m, kapanmış mum, test öncesi sabitlendi, 2026-10-10)
`range = high - low` (mumun boyu).

Long (hepsi):
- [vol_expanding] Teknik: SMA(range, 10) > SMA(range, 50) | Açıklama: "Mumlar büyüyor: son 10 mumun ortalama boyu son 50 mumunkinden büyük."
- [momentum_up] Teknik: close > close 20 mum önce | Açıklama: "Fiyat ({close}) 20 mum öncesinden ({close_20}) yüksekte."
- [breakout_up] Teknik: close > önceki 20 mumun (bu mum hariç) en yüksek kapanışı | Açıklama: "Fiyat son 20 mumun en yüksek kapanışını ({hh_close_20}) geçti."
- [green_candle] Teknik: close > open | Açıklama: "Mum yeşil kapandı."

Short (hepsi):
- [vol_expanding] Teknik: SMA(range, 10) > SMA(range, 50) | Açıklama: "Mumlar büyüyor."
- [momentum_down] Teknik: close < close 20 mum önce | Açıklama: "Fiyat ({close}) 20 mum öncesinden ({close_20}) düşükte."
- [breakout_down] Teknik: close < önceki 20 mumun (bu mum hariç) en düşük kapanışı | Açıklama: "Fiyat son 20 mumun en düşük kapanışının ({ll_close_20}) altına indi."
- [red_candle] Teknik: close < open | Açıklama: "Mum kırmızı kapandı."

**Seçim notu:** Kaynak long için "en yüksek kapanış", short için "en düşük dip (low)" diyor. Simetri için ana sürümde short da **kapanışları** kullanır. Kaynaktaki "dip" hali önceden bir varyant olarak tanımlandı (aşağıda).

Giriş: sinyal mumu kapandıktan sonra bir sonraki mumun açılışında (Freqtrade'in normal davranışı, piyasa emri).

## İşlem yönetimi
**Bu strateji projenin ortak işlem yönetimi modülünü (`strategies/common/`) KULLANMAZ.** Proje sahibinin kurallarının birebir testidir:
- Giriş bölgesi kuralı: yok, sonraki mumun açılışında giriş.
- Stop kuralı: girişten sabit **%1.5** (Freqtrade `stoploss = -0.015`, kaldıraç 1x). Mum içinde kontrol edilir.
- Kâr al: girişten sabit **%3** fiyat hareketi. Mum içinde kontrol edilir. Freqtrade'in `minimal_roi` değeri masraf düşülmüş net kâra göre çalıştığı için (%3 net = fiyatın ~%3.2 hareketi), birebir %3 fiyat hedefi için `custom_roi` ile hedef fiyat tam giriş ×1.03 (short: ×0.97) yapılır. `minimal_roi` devre dışı.
- Aynı mumda hem stop hem hedef görülürse **önce stop** sayılır (Freqtrade'in sırası: stop, sonra ROI; kötümser).
- Başka çıkış yok (çıkış sinyali yok, süre sınırı yok, BE yok).
- Kaldıraç 1x. Her coinde aynı anda en fazla 1 işlem.
- 1R = %1.5 (stop mesafesi). Hedef 2R. İşlem sonucu R = net kâr (masraf + funding dahil) / (işlem büyüklüğü × %1.5).
- Pozisyon büyüklüğü: Freqtrade `stake_amount: unlimited` → kasanın 1/(en fazla açık işlem) kadarı. Ana sürümde 5 yuva, yani her işlem kasanın ~%20'si; bir stop kasanın ~%0.3'ü. (Projenin "%1 risk" kuralı burada uygulanmaz; ilk eleme kural testidir.)
- Sinyal geçerlilik süresi: 1 mum (sonraki açılış).

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 5m | sabit |
| Oynaklık SMA kısa / uzun | 10 / 50 | sabit (bu turda) |
| Momentum geri bakış | 20 mum | sabit |
| Kırılım kanalı | önceki 20 mum kapanışı | sabit |
| Stop | %1.5 | sabit |
| Hedef | %3 | sabit |
| Kaldıraç | 1x | sabit |
| En fazla açık işlem | 5 | sabit |

## Varyantlar (önceden belirlendi, en fazla 2; karar sadece ana sürüme göre)
- `Momentum5m`: ana sürüm, karar buna göre.
- `Momentum5mLows`: short kırılımı kapanışlar yerine kaynaktaki gibi önceki 20 mumun **en düşük dibi (low)**. Teşhis.
- Sınırsız işlem: ana sürüm `--max-open-trades 16` ile (16 coin, coin başına 1 işlem olduğu için bu fiilen sınırsızdır; her işlem kasanın 1/16'sı). Teşhis.

## Test planı (önceden)
- 16 coin (`config/pairs_wide16.json`), 5m mum, maliyet emir başına %0.1 (%0.05 komisyon + %0.05 kayma), funding geçmiş veriden.
- Önce hile testi (lookahead-analysis), 3 coin, kısa dönem.
- Geliştirme 2022-01-01 → 2024-12-31 (`--timerange 20220101-20250101`).
- Ek koşular: masraf x2 (`--fee 0.002`); "düşük masraflı borsa" (`--fee 0.0003`, sadece teşhis); masrafsız (`--fee 0`, teşhis).
- **İlk eleme şartı ("şansı hak ediyor mu")**, normal masrafla, ana sürüm: ortalama R > 0, PF ≥ 1.1, max DD ≤ %35, coinlerin en az yarısı artıda, 3 yılın en az 2'sinde artı. Hepsi sağlanırsa ileride ileri kâğıt üstü test (paper trading) ve tam eşikler (`docs/metrics.md`) gelir.
- Doğrulama (2025+) bu turda YAPILMAZ. Kasaya (2026-04 sonrası) dokunulmaz.
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Durum: candidate — beklemede (2026-10-10)
Beklemede: normal masrafla ilk elemeyi geçemedi (PF 1.01, DD %54); sadece düşük komisyonlu borsa varsayımında (%0.03/emir) ilk aşama şartlarını geçiyor. Devam edip etmemek proje sahibinin kararı. Kod `strategies/candidates/` altında kalıyor (emekliye ayrılmadı, karar bekleniyor).

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Hile testi (lookahead-analysis, BTC/ETH/SOL, 2023-01, 30 sinyal, ana + Lows) | Geleceği görme yok. | — |
| 2026-10-10 | Geliştirme 2022-2024, 16 coin, 5 yuva, normal masraf | 16700 işlem (günde 15.2), +0.010R, PF 1.01, DD %54.2, net +%17.6. Long -0.047R (PF 0.94), short +0.060R (PF 1.07). 10/16 coin artıda. Yıllar: 2022 -0.009R, 2023 +0.032R, 2024 +0.020R. Al-tut +%20.3. **İlk eleme: PF ve DD şartı tutmadı.** | `results/2026-10-10_momentum_5m_gelistirme_16coin/rapor.md` |
| 2026-10-10 | Masraf x2 | -0.129R, PF 0.78, net -%99.8, 0/16 coin. Kırılgan. | aynı rapor |
| 2026-10-10 | Düşük masraf %0.03/emir (teşhis) | +0.103R, PF 1.15, DD %27, 14/16 coin, 3/3 yıl artı. Long +0.047R, short +0.154R. | aynı rapor |
| 2026-10-10 | Masrafsız (teşhis) | +0.143R, PF 1.20, DD %23. | aynı rapor |
| 2026-10-10 | `Momentum5mLows` (teşhis) | 16373 işlem, -0.047R, PF 0.90, DD %93, 2/16 coin. | aynı rapor |
| 2026-10-10 | Sınırsız, 16 yuva (teşhis) | 48335 işlem (günde 44), -0.110R, PF 0.85, DD %99. | aynı rapor |
| 2026-10-10 | Sıralama testi: ana sürüm, coin listesi ters sırada (teşhis, plan dışı ek koşu, proje yöneticisinin sorusu üzerine) | 17851 işlem, -0.003R, PF 0.98, DD %70.5, 5/16 coin. Ana sürümdeki +0.010R sıralama etkisi. | aynı rapor |

## Notlar / öğrenilenler
- İşlem başına masraf (%0.2 = 0.133R) masraf öncesi avantajın (+0.14R) neredeyse tamamını yiyor. Dar stop/hedefli 5m kurallarında masraf belirleyici.
- Short tarafı 3 yılın hepsinde artıda, long tarafı 2022 ve 2024'te eksi.
- Sinyal çok bol; 5 yuva neredeyse hep dolu. 16 yuvada (tüm sinyaller) sonuç -0.11R; coin listesi ters sıralanınca 5 yuvada bile -0.003R. Ana sürümdeki küçük artı "ilk gelen alır" sıralama etkisi: hareketin ilk sinyalleri eksi (-0.12R), yuva dolu olduğu için geç alınan sinyaller hafif artı (+0.05R).
- Ortalama işlem süresi ~7.5 saat; pratikte scalp değil.
- Doğrulama yapılmadı, kasaya dokunulmadı.

## Emeklilik gerekçesi (varsa)
