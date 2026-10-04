# Sinyal sistemi

Seviye 3 ve 4'te devreye girer. Şu an sadece veri yapısı hazır.

| Parça | Ne yapar | Durum |
|---|---|---|
| `schema.py` | Her sinyalin veri yapısı (giriş bölgesi, stop, TP'ler, tetikleyen koşullar...). Kurallara uymayan sinyali (ör. TP1 < 1R, uydurma seviye) reddeder. | Hazır |
| `explainer/` | Tetiklenen koşulları strateji kartındaki Türkçe cümlelere çevirir ("Neden / Stop / TP'ler / Yönetim"). | Seviye 3 |
| `templates/` | Telegram mesaj şablonları; `templates/design/` görsel tasarım referansları. | Seviye 3-4 |
| `renderer/` | Sinyal görseli (mum grafiği + seviyeler + açıklama paneli). | Seviye 4 |
| `dispatcher/` | Freqtrade'den gelen sinyali alır, kaydeder, sadece senin Telegram sohbetine gönderir. | Seviye 3 |
| `log/` | Gönderilen her sinyalin kaydı (JSON). Repoya girmez. | — |

Kural: Mesajdaki her rakam test edilmiş kuralın çıktısıdır; açıklamalar şablondan gelir, bir dil modeli canlıda seviye veya gerekçe uydurmaz.
