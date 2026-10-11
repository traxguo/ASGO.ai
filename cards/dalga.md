# dalga — Claude'un hızlı stratejisi: güçlü coinde 1 saatlik kırılım, trend bitene kadar tut

Kod: [`strategies/candidates/dalga.py`](../strategies/candidates/dalga.py)

## Hipotez
Şimdiye kadarki testlerden çıkan dersler:
- **İşe yarayan:** günlük trend yukarıyken trend yönündeki kırılımla long girmek ve işlemi günlük trend bozulana kadar tutmak (Pusula; aynı kural 1 saatlik grafikte de +0.80R, tur 4 stres testi).
- **İşe yaramayan:** dar stoplu 5m/3m scalp (masraf işlem başına 0.5-0.8R), geri çekilmeden alım (Nabız), sabit 2R/4R hedef (Kırılım1s: kazananları erken kesiyor), limit emirle kırılıma girmek, short taraf (her testte zayıf).
- **Çıkarma turlarında kabul edilen:** BTC giriş filtresi gereksiz, rejim eşiği +1 yeterli, 2R'de stopu girişe çekmek gereksiz (PusulaV2NoBe).

Dalga bunları birleştirir: Pusula V2NoBe'nin kuralları, giriş 1 saatlik grafikte (stop ~%2-3, masraf ~0.1R), 36 coin ve **8 işlem yuvası**. Pusula'daki işlem azlığının ana sebebi 3 yuvanın hep dolu olmasıydı; işlem başı risk küçültülüp (ortalama ~%0.5, trendin gücüne göre) yuva 8'e çıkarılır. Beklenti: günde ~0.5-1 işlem, işlem başına masraf sonrası artı.

## Yön
sadece long (short her testte zayıftı)

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Pusula'dakiyle aynı puan (`daily_regime_frame`): kapanış EMA(50) üstü, EMA(20) EMA(50) üstü, 90 günlük getiri artı. -3 ile +3 arası.

## Giriş koşulları (1h, kapanmış mum, test öncesi sabitlendi, 2026-10-11)
- [regime_up] Teknik: coinin günlük puanı ≥ +1 | Açıklama: "Günlük trend çoğunlukla yukarı ({score_1d}/3)."
- [breakout_up] Teknik: 1h kapanış önceki 24 mumun en yükseğinin üstünde, serinin ilk mumu (`first_true`) | Açıklama: "Fiyat ({close}) son 24 saatin tepesini ({dc_upper}) kırdı."
- [daily_above_ema20] Teknik: son kapanmış günlük kapanış günlük EMA(20) üstünde | Açıklama: "Günlük kapanış 20 günlük ortalamanın üstünde."

## İşlem yönetimi
- Giriş bölgesi: ortak modül (kırılım kapanışı ile 0.25 ATR geri arası, limit emir ortada), geçerlilik 3 mum.
- Stop: ortak modül, 1.5 ATR(1h) veya son 10 mumun dibi, hangisi uzaksa; stop %8'den uzaksa sinyal yok. Stop hiç taşınmaz.
- Çıkış (TP emri yok): son kapanmış günlük mum EMA(20) altında kapanırsa **veya** BTC'nin günlük puanı ≤ -1 olursa işlem kapanır.
- İşlem başı risk **duruma göre değişir** (proje sahibinin isteği, 2026-10-11, test öncesi sabitlendi):
  - Günlük puan +3 (trend çok güçlü): kasanın **%0.75**'i. Puan +1 (trend zayıf): **%0.35**.
  - Kasa en yüksek değerinden %10 veya daha fazla düşükse risk yarıya, %20 veya daha fazla düşükse dörtte bire iner. Kasa yeni zirve yapınca normale döner.
  - Örnek, 10.000$ kasa, stop %2: güçlü trendde stop olursa 75$ kayıp (işlem büyüklüğü 3.750$), zayıf trendde 35$ (1.750$).
- En fazla 3x kaldıraç, aynı anda en fazla **8 açık işlem**.
- Not: sabit TP yok; proje özetindeki "2 TP'li sinyal" biçiminden sapar (Pusula'daki gibi, `docs/decisions.md`). "active" olmadan önce sahip onayı gerekir.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 1h | sabit |
| Kanal | 24 mum | 12-48 |
| Rejim eşiği | +1 | +1 / +3 |
| Yuva / risk | 8 / %0.35-0.75 (düşüşte azalır) | 5-10 / %0.3-1 |
| Coinler | `config/pairs_all36.json` | — |

## Varyantlar (önceden belirlendi; karar sadece ana sürüme göre)
- `DalgaFixed` (teşhis): her işlemde sabit %0.5 risk. Değişken büyüklüğün işe yarayıp yaramadığını görmek için.

## Test planı (önceden)
Geliştirme 2020-01-01 → 2024-12-31, 36 coin, normal masraf (%0.1/emir + funding), masraf x2, al-tut kıyası, long raporu.
İlk eleme şartları: ortalama > 0R, PF ≥ 1.2, en büyük düşüş ≤ %25, masraf x2'de > 0R, günde ≥ 0.5 işlem.
Dürüstlük notu: 2020-2024 ve 2025-2026 verisi Pusula ailesinde çok kullanıldı; Dalga'nın kuralları bu bilgiyle seçildi. Gerçek sınav ileriye dönük kağıt takip olur.

## Durum: candidate — Bitget demoda (2026-10-11, Pusula ile birlikte)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-11 | Geliştirme 2020-2024, 36 coin, 8 yuva | 859 işlem (günde 0.47), ort. +1.13R, PF 1.52, DD %26.2; masraf x2 +1.07R DD %28; en iyi 10 işlem hariç +0.44R; 2022 -0.85R (46 işlem), diğer yıllar artı. Sabit %0.5 risk: aynı R, DD %43.6 | [rapor](../results/2026-10-11_dalga_gelistirme_36coin/rapor.md) |
| 2026-10-11 | Doğrulama 2025-01 → 2026-03, 36 coin (kurallar değişmedi) | 160 işlem (günde 0.35), ort. +0.44R, PF 1.40, DD %16, kasa +%24 (al-tut -%51); en iyi 5 işlem hariç -0.25R; 2026 Q1 5 işlem -1.1R | [rapor](../results/2026-10-11_dalga_dogrulama_36coin/rapor.md) |

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
