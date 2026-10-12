# kivilcim — DENEME: güçlü trendde 1 saatlik geri çekilmede al, en fazla 3 saat tut

Kod: [`strategies/candidates/kivilcim.py`](../strategies/candidates/kivilcim.py)

> **Uyarı:** Bu kural testi GEÇMEDİ. Maliyet sonrası geliştirme döneminde işlem başı yaklaşık -0.08R, doğrulama döneminde -0.12R verdi. Demoda sadece proje sahibinin isteğiyle (2026-10-11) çalışıyor: kısa işlem botunun canlıda nasıl giriş/çıkış yaptığını görmek ve gerçek dolum verisi toplamak için. Gerçek paraya aday değildir. Sinyal olarak gönderilmez, sadece demo işlem mesajı gider.

## Hipotez
Günlük trendi çok güçlü (+3/3) bir coin, saatlik grafikte geçici olarak aşırı satılınca (RSI < 35) birkaç saat içinde toparlanır. Test, bu toparlanmanın maliyeti (komisyon + kayma, işlem başı yaklaşık 0.13R) karşılamadığını gösterdi.

## Yön
sadece long

## Piyasa durumu (rejim), günlük, son **kapanmış** günlük mum
Pusula/Dalga ile aynı puan: kapanış EMA(50) üstü, EMA(20) EMA(50) üstü, 90 günlük getiri artı.

## Giriş koşulları (1h, kapanmış mum, 2026-10-11)
- [regime_strong] Teknik: coinin günlük puanı = +3 | Açıklama: "Günlük trend çok güçlü (3/3)."
- [rsi_pullback] Teknik: 1h RSI(14) < 35 | Açıklama: "Saatlik grafikte geçici düşüş var (RSI {rsi})."
- [enough_move] (v2, 2026-10-11) Teknik: ATR(14, 1h) fiyatın en az %1.5'i | Açıklama: "Coin yeterince hareketli (saatlik ortalama hareket %{atr_pct}), masraf küçük kalıyor."

## İşlem yönetimi
- Giriş: 1h mum kapandıktan sonra piyasa emri (mum kapanışından en geç 40 dakika sonra; daha geç kalırsa sinyal atlanır).
- Stop: giriş − 1.5 ATR(14, 1h). Kâr al: giriş + 1.5 ATR(14, 1h). İkisi de borsada emir olarak durur.
- Süre: 3 saat dolunca ikisi de olmadıysa piyasadan kapatılır.
- Risk: işlem başı kasanın %0.2'si. En fazla 2 açık işlem, UTC gününde en fazla 3 yeni işlem. Pusula/Dalga'nın tuttuğu coine girmez.

## Zaman dilimi ve parametreler
| Parametre | Değer |
|---|---|
| Zaman dilimi | 1h |
| RSI eşiği | 35 |
| Stop / kâr al | 1.5 / 1.5 ATR |
| En uzun süre | 3 saat |
| Coin listesi | `config/pairs_kivilcim76.json` (2026-10-12'den beri: 81 coinlik test listesinden Bitget'te hiç olmayan 5 coin çıkarıldı; demoda olmayan coin atlanır) |

## Durum: deneme (demo), aday değil

## Test geçmişi
Araç: `research/scans/short_trade_grid.py` (S2_pullback), 1h mumla olay simülasyonu, aynı mumda stop ve hedef ikisi de varsa stop sayılır, maliyet %0.2.

| Tarih | Dönem | Coin | İşlem | Günde | Ortalama R | Not |
|---|---|---|---|---|---|---|
| 2026-10-11 | 2020-01 → 2024-12 | 81 | 25 162 | 13.8 | -0.084 | sl 1.5 / tp 1.5 ATR, 3 saat |
| 2026-10-11 | 2025-01 → 2026-03 | 36 | 2 612 | 5.7 | -0.124 | aynı |
| 2026-10-11 | 2020-01 → 2024-12 | 81 | 17 581 | 9.6 | -0.044 | v2: ATR ≥ %1.5 |
| 2026-10-11 | 2025-01 → 2026-03 | 36 | 1 151 | 2.5 | -0.085 | v2: ATR ≥ %1.5 |

### Geliştirme turu (2026-10-11 gece, `research/scans/kivilcim_lab.py`)
- İşlemlerin brüt sonucu (masraf öncesi) sıfıra çok yakın: geliştirmede -0.004R, doğrulamada -0.01R. Kaybın tamamı masraftan geliyor; işlemlerin %63'ü 3 saat dolunca kapanıyor.
- **Kabul (v2):** Sakin coinleri atla (saatlik ATR fiyatın %1.5'inden az). Masraf R olarak küçülüyor; iki dönemde de iyileşti (geliştirme -0.084 → -0.044R, doğrulama -0.124 → -0.085R), günde ~2.5 işlem kalıyor. Mekanik bir iyileştirme, avantaj yaratmıyor.
- **Reddedildi:** "Bütün piyasa düşerken güçlü coini al" (BTC 3 saatte -%1.5/-2 veya 24 saatte -%5): geliştirmede ~0R'a çıktı ama doğrulamada -0.07..-0.19R. Daha geniş hedef / daha uzun süre (6-12 saat): fark yok. RSI derinliği, saat, hacim: tutarlı fark yok.
- ATR ≥ %2 doğrulamada +0.01R verdi ama günde ~1 işleme düşüyor ve geliştirmede hâlâ eksi; seçilmedi.

### Demo coin listesi (2026-10-12)
Bitget demo hesabında 36 coinin sadece 15'i var (AAVE, ALGO, ATOM, ETC, FIL, XLM, ZEC ve 14 coin daha yok). Sabah hiç işlem açılmadı. Kıvılcım'ın geliştirme testi zaten 81 coinle yapılmıştı, bu yüzden demoda 81 coinlik listeye geçti. Demoda olmayan coin sessizce atlanır. Kural değişmedi.

Aynı gece denenen diğer kısa kurallar (24 saatlik kırılım, hacimli büyük mum, sert düşüş sonrası alım) ve 6-24 saatlik tutmalar da sıfırın altında kaldı. Kural koddaki sinyalle birebir aynı (SOL 2025: 256/256 sinyal eşleşti).
