# signals/dispatcher — Telegram botu

Bot sadece **senin kişisel Telegram sohbetine** ve istersen **senin seçtiğin tek bir gruba** yazar. Başka biri botu bulup yazsa ya da botu başka bir gruba eklese bile cevap almaz.

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

## Windows'ta (kendi bilgisayarında) çalıştırma
1. **Python kur:** Microsoft Store'u aç, `Python 3.12` ara, **Yükle**'ye bas.
2. **Projeyi indir:** GitHub'da repo sayfasında yeşil **Code** → **Download ZIP**. ZIP'i ör. `C:\asgo` klasörüne çıkar (içinde `signals`, `docs` gibi klasörler görünmeli).
3. **`.env` dosyası:** Not Defteri'ni aç, şu iki satırı yaz (kendi bilgilerinle):
   ```
   TELEGRAM_BOT_TOKEN=buraya_token
   TELEGRAM_CHAT_ID=buraya_chat_id
   ```
   **Farklı Kaydet** → klasör: `C:\asgo` → Dosya adı: `".env"` (tırnaklarla birlikte) → Kayıt türü: **Tüm Dosyalar** → Kaydet.
4. **Komut penceresi:** `C:\asgo` klasörünü aç, üstteki adres çubuğuna tıkla, `cmd` yaz, Enter.
5. **Dene:** `python -m signals.dispatcher.bot test` → Telegram'a deneme mesajı gelir.
6. **Çalıştır:** `python -m signals.dispatcher.bot run` → pencere açık kaldıkça bot cevap verir. Kapatmak için pencereyi kapat.

## Grup kurulumu (isteğe bağlı, tek grup)
1. Bot çalışıyorsa önce durdur (`run` penceresini kapat).
2. Telegram'da arkadaşınla bir grup aç (ya da mevcut grubu kullan) ve botu gruba **üye olarak ekle**.
3. Grupta `/start` yaz.
4. Bilgisayarda şunu çalıştır: `py -m signals.dispatcher.bot chatid`. Ekranda `grup: ...` yazan satırdaki eksi işaretli sayıyı kopyala.
5. `.env` dosyasına yeni bir satır ekle: `TELEGRAM_GROUP_ID=-100...` (o sayı).
6. `py -m signals.dispatcher.bot test` → deneme mesajı hem sana hem gruba gelir. Sonra `run` ile çalıştır.

Grupta bot sadece `/` ile başlayan komutlara (`/btc`, `/eth`, `/durum`, `/sor ...`) ve kendi mesajına verilen yanıtlara cevap verir. Normal sohbete karışmaz.

## Yapay zekâ ile sohbet (isteğe bağlı, ücretsiz)
Açıksa bota özelden düz yazı yazabilirsin ("ne yaptın ne ettin", "btc ne olur"). Grupta `/sor <soru>` yazılır ya da botun mesajına yanıt verilir.

**Kural:** Yapay zekâ sadece sohbet eder. Fiyat tahmini, alım/stop/hedef vermez; sadece sistemin kendi bilgilerine (durum, sıradaki işler, coin raporu) dayanır. Cevabında bu bilgilerde olmayan bir rakam (3+ basamak) varsa cevap atılır, bot sadece normal rapor verir.

Kurulum:
1. **aistudio.google.com** adresine Google hesabınla gir (kart istemez).
2. **Get API key** → **Create API key**. Çıkan uzun anahtarı kopyala. **Bunu hiçbir sohbete yapıştırma.**
3. `.env` dosyasına yeni satır ekle: `AI_API_KEY=anahtar`
4. Botu yeniden başlat (`run`). Pencerede `AI chat on` yazmalı.

Not: Ücretsiz kullanımda Google, gönderilen mesajları kendi ürünlerini geliştirmek için kullanabilir; bota kişisel bilgi yazma. Ücretsiz kotanın günlük sınırı var; dolarsa bot sadece normal cevaplara döner.

## Nerede çalışmalı?
Bot, açık kaldığı sürece çalışır. Seçenekler:
1. **Küçük bir sanal sunucu (VPS)** — önerilen. Aylık birkaç dolar/euro. 7/24 açık; Seviye 3'te Freqtrade dry-run da zaten 7/24 çalışmak zorunda, ikisi aynı yerde durur.
2. **Kendi bilgisayarın** — denemek için en kolayı, ama bilgisayar kapanınca bot da susar.
3. Claude'un çalıştığı bulut oturumu **uygun değil**: geçicidir, bir süre sonra kapanır.

## Dosyalar
- `telegram_client.py`: Telegram'la konuşan küçük istemci; sadece `.env`'deki sohbete mesaj atabilir.
- `commands.py`: Komutlara cevaplar (seviye uydurmaz; sadece aktif stratejiler ve `signals/log/` kaydı).
- `chat_ai.py`: İsteğe bağlı yapay zekâ sohbeti (seviye üretmez, rakam kontrolü var).
- `bot.py`: `chatid`, `test`, `run` komutları.
