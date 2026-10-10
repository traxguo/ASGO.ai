# rsi_reversion — RSI ortalamaya dönüş + trend filtresi

Kod: [`strategies/candidates/rsi_reversion.py`](../strategies/candidates/rsi_reversion.py) (`RSIReversion_B` = Model B, `RSIReversion_A` = Model A)

## Hipotez
Ana trend yukarıyken gelen sert düşüşler çoğu zaman geçicidir; fiyat "aşırı satılmış" bölgeden çıkarken trend yönünde almak, düşüşün sonunu yakalamaya çalışır. Short tarafı simetrik: ana trend aşağıyken "aşırı alınmış" bölgeden dönüşte satmak. Kırılım ve kesişim stratejilerinden farkı: trende geç değil, trend içindeki geri çekilmenin sonunda girer.

## Yön
İkisi de (long ve short simetrik). Long ve short ayrı raporlanır.

## Giriş koşulları

**Long** (hepsi aynı anda doğru olmalı):
- [trend_up] Teknik: `close > EMA(200)` | Açıklama: "{tf} ana trend yukarı (fiyat {close}, EMA200 {ema_trend} üzerinde)."
- [rsi_exit_oversold] Teknik: `RSI(14)` bu mumda 30'un üstüne çıktı (önceki mum ≤ 30) | Açıklama: "RSI ({rsi}) aşırı satım bölgesinden (30) yukarı döndü."

**Short** (hepsi aynı anda doğru olmalı):
- [trend_down] Teknik: `close < EMA(200)` | Açıklama: "{tf} ana trend aşağı (fiyat {close}, EMA200 {ema_trend} altında)."
- [rsi_exit_overbought] Teknik: `RSI(14)` bu mumda 70'in altına indi (önceki mum ≥ 70) | Açıklama: "RSI ({rsi}) aşırı alım bölgesinden (70) aşağı döndü."

## Neye bakıyor? (bildiği şeyler)
- Sadece kapanmış mumların fiyatı
- EMA200 (ana trend), RSI(14)
- ATR(14) ve son 10 mumun dibi/tepesi (stop ve giriş bölgesi için)
- Bilmedikleri: hacim, funding, haber, diğer coinler.

## İşlem yönetimi
Ortak modülden (trend_ma ve donchian_breakout ile aynı): giriş bölgesi kapanış ∓ 0.25 ATR, stop 1.5 ATR ile yapısal stop arasından geniş olanı (en fazla %8), Model A ve B, 3 mum geçerlilik, en fazla 3x kaldıraç.

## Zaman dilimi ve parametreler
Test öncesi sabitlendi.

| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 4h | 1h, 4h |
| RSI periyodu | 14 | 7-21 |
| Aşırı satım / alım | 30 / 70 | 20-35 / 65-80 |
| EMA trend | 200 | 150-250 |
| Isınma (startup) | 1000 mum | EMA200 için (trend_ma'da ölçüldü) |

## Durum: elendi — aşama 2 (ilk backtest) geçilemedi

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-08 | Lookahead + recursive (4h) | 45 işlemde 1 "bias" işareti: incelendi, yanlış alarm (aynı giriş ve stop farklı kesimlerde de oluşuyor; ayrıntı raporda). 1000 mum ısınmada sapma yok. | — |
| 2026-10-08 | İlk backtest, A vs B (geliştirme 2020-06 → 2024-12) | A: -0.03R, PF 0.94, DD %16.8. B: +0.01R, PF 1.00, DD %12.0. 116 işlem. Başa baş. | [results/2026-10-08_rsi_reversion_ilk_backtest](../results/2026-10-08_rsi_reversion_ilk_backtest/rapor.md) |

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
2026-10-08: ilk backtest'te beklenti sıfırdan ayırt edilemedi (B +0.01R, PF 1.00). ATR filtreli versiyonu daha da kötü (-0.32R).
