# signals/dispatcher — Telegram botu

Bot sadece **senin kişisel Telegram sohbetine** yazar ve sadece sana cevap verir. Başka biri botu bulup yazsa bile cevap almaz. Grup veya kanal desteği yoktur.

## Bot şu an ne yapar?
| Yazdığın | Bot ne der |
|---|---|
| `btc`, `/eth`, `btc'ye bak`, `ethere bak` | O coinin güncel fiyatı (sadece bilgi) + testi geçmiş stratejilerin o coin için kayıtlı son sinyali |
| `/durum` | Proje hangi seviyede, kaç strateji aktif, sinyal gönderimi açık mı |
| `/liste` | Takip edilen coinler |
| `/yardim` | Komut listesi |

**Önemli:** Bot kendi kafasına göre "şuradan al, stop şurası" demez. Alım bölgesi, stop ve TP'ler sadece testi geçmiş (aktif) stratejilerin kurallarından gelir. Şu an aktif strateji olmadığı için `btc'ye bak` dediğinde fiyatı ve "henüz test edilmiş strateji yok" cevabını alırsın. Otomatik sinyal mesajları Seviye 3'te açılır.

## Kurulum (bir kez)

### 1. Botu oluştur
1. Telegram'da **@BotFather**'ı aç (mavi tikli olan).
2. `/newbot` yaz.
3. Bota bir isim ver (ör. `ASGO Sinyal`).
4. Bir kullanıcı adı ver; sonu `bot` ile bitmeli (ör. `asgo_guo_bot`).
5. BotFather sana uzun bir **token** verir (`123456789:AA...` gibi). Bu botun şifresidir.
   - **Bu token'ı hiçbir sohbete, Claude'a, GitHub'a yapıştırma.** Sadece `.env` dosyasına yazılır.
6. Telegram'da kendi botunu aç ve **Başlat**'a bas (ya da "merhaba" yaz). Bot sana ancak sen ona önce yazdıktan sonra yazabilir.

### 2. `.env` dosyasını hazırla (botun çalışacağı bilgisayarda)
1. Repo klasöründe `.env.example` dosyasını kopyalayıp adını `.env` yap.
2. `TELEGRAM_BOT_TOKEN=` satırının sonuna token'ı yapıştır.
3. Chat ID'ni bul: `python3 -m signals.dispatcher.bot chatid` çalıştır. Ekrana `Chat ID: 12345...` yazar. Bu sayıyı `TELEGRAM_CHAT_ID=` satırına yaz.
   (Alternatif: Telegram'da **@userinfobot**'a yaz, sana "Id" numaranı söyler.)

`.env` `.gitignore`'dadır, repoya asla girmez. `scripts/safety_check.py` de repoda token görürse durdurur.

### 3. Dene
```
python3 -m signals.dispatcher.bot test
```
Telegram'a "ASGO botu bağlandı" mesajı gelmeli.

### 4. Sürekli çalıştır
- Docker ile: `docker compose up -d telegram-bot` (bilgisayar yeniden başlasa da kendisi açılır)
- Docker'sız: `python3 -m signals.dispatcher.bot run` (pencere açık kaldıkça çalışır)

Bot dışarıya port açmaz; Telegram'a kendisi sorar ("bana mesaj var mı?"). Ekstra kütüphane gerekmez.

## Nerede çalışmalı?
Bot, açık kaldığı sürece çalışır. Seçenekler:
1. **Küçük bir sanal sunucu (VPS)** — önerilen. Aylık birkaç dolar/euro. 7/24 açık; Seviye 3'te Freqtrade dry-run da zaten 7/24 çalışmak zorunda, ikisi aynı yerde durur.
2. **Kendi bilgisayarın** — denemek için en kolayı, ama bilgisayar kapanınca bot da susar.
3. Claude'un çalıştığı bulut oturumu **uygun değil**: geçicidir, bir süre sonra kapanır.

## Dosyalar
- `telegram_client.py`: Telegram'la konuşan küçük istemci; sadece `.env`'deki sohbete mesaj atabilir.
- `commands.py`: Komutlara cevaplar (seviye uydurmaz; sadece aktif stratejiler ve `signals/log/` kaydı).
- `bot.py`: `chatid`, `test`, `run` komutları.
