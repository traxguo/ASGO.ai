# pusula — Claude'un ana stratejisi: günlük rejim + 4 saatlik kırılım

Kod: [`strategies/candidates/pusula.py`](../strategies/candidates/pusula.py)

## Hipotez
Bugüne kadarki tek gerçek artı, günlük trend yönünde 4 saatlik kırılımdı (long tarafı). Short'lar zayıf düşüşleri gerçek düşüş sandığı için kaybetti. Pusula trendi üç ayrı ölçüyle sorar ve sadece üçü de aynı yönü gösterirken, Bitcoin de aynı taraftayken işlem açar. Kararsız piyasada işlem açmaz, sadece yorum yapar. Bu yüzden her coin için her an bir görüş verebilir.

## Yön
ikisi de

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Puan = üç işaretin toplamı (-3 ile +3 arası).
- [a] Kapanış EMA(50)'nin üstünde (+1) / altında (-1) | "Fiyat ({close_1d}) 50 günlük ortalamanın ({ema_slow_1d}) üstünde/altında."
- [b] EMA(20) EMA(50)'nin üstünde (+1) / altında (-1) | "Kısa vadeli ortalama uzun vadelinin üstünde/altında."
- [c] 90 günlük getiri artı (+1) / eksi (-1) | "Fiyat 90 gün öncesine göre %{mom_1d} değişti."
- +3 = güçlü yükseliş, -3 = güçlü düşüş, diğerleri = kararsız.

## Giriş koşulları (4h)
Long (hepsi):
- [regime_up] Teknik: coinin puanı = +3 | Açıklama: "Günlük trend güçlü yukarı (3/3)."
- [market_up] Teknik: BTC'nin puanı ≥ +1 | Açıklama: "Bitcoin de çoğunlukla yukarı ({mkt_score_1d}/3)."
- [breakout_up] Teknik: 4h kapanış önceki 20 mumun tepesinin üstünde, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun tepesini ({dc_upper}) kırdı."

Short (hepsi):
- [regime_down] Teknik: coinin puanı = -3 | Açıklama: "Günlük trend güçlü aşağı (3/3)."
- [market_down] Teknik: BTC'nin puanı ≤ -1 | Açıklama: "Bitcoin de çoğunlukla aşağı ({mkt_score_1d}/3)."
- [breakout_down] Teknik: 4h kapanış önceki 20 mumun dibinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 20 mumun dibini ({dc_lower}) kırdı."

Kararsız rejimde işlem yok.

## İşlem yönetimi
Ortak modülden (`strategies/common/`): giriş bölgesi 0.25 ATR, stop 1.5 ATR veya son 10 mumun dip/tepesi (uzak olan), Model B (TP1 2R'de yarısı + BE, TP2 4R), 3 mum geçerlilik, en fazla 3x, işlem başı %1 risk.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 4h | sabit |
| Rejim zaman dilimi | 1d | sabit |
| EMA hızlı / yavaş | 20 / 50 | 15-25 / 40-60 |
| Momentum | 90 gün | 60-120 |
| Kanal | 20 mum | 15-30 |
| Piyasa filtresi | BTC puanı ≥ +1 / ≤ -1 | sabit |

## Varyantlar (önceden belirlendi)
- `Pusula_B`: ana strateji, karar buna göre verilir.
- `PusulaNoBTC_B`: Bitcoin filtresi olmadan, sadece filtrenin katkısını görmek için.

## Durum: candidate (ilk backtest'i geçemedi, sonraki adım için proje sahibinin kararı bekleniyor)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-09 | Birim testleri (rejim puanı sadece geçmiş veriyi kullanıyor) + ilk backtest (geliştirme 2020-03 → 2024-12) | Pusula_B +0.08R, PF 1.07, DD %35.0, 269 işlem (long +21.3R, short -0.1R). Kârın tamamı 2020 long'ları; 2021-2024 ≈ -1.6R. BTC filtresiz: +0.06R, DD %38.2. Geçemedi; doğrulamaya bakılmadı. | [results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme](../results/2026-10-09_Pusula_B_PusulaNoBTC_B_ilk_backtest_gelistirme/rapor.md) |

## Notlar / öğrenilenler
- Üç ölçünün de aynı yönü göstermesi short'ları kurtarmadı: 2022'de 63 short, ortalama -0.02R.
- Rejim ölçümü (araştırma): güçlü yükseliş günlerinden sonraki 7 gün ortalama %+4.8, güçlü düşüşten sonra %+1.2, tüm günler %+2.8. Düşüş rejimi bu dönemde short avantajı vermiyor.
- Kazanan işlemler ortalama 13 gün sürüyor. Sabit 2R/4R hedef, trendin büyük kısmını kaçırıyor olabilir (test edilmedi).
- Yorum modülü (`commentary`) her coin için her an rejim + tetik seviyesi + plan yazabiliyor; strateji geçmediği için çıktısı sinyal sayılmaz.
- Doğrulama dönemi (2025-01 → 2026-03) daha önce benzer Donchian stratejilerinde kullanıldı; bu strateji için tamamen temiz değil. Temiz test kasa testidir.

## Emeklilik gerekçesi (varsa)
