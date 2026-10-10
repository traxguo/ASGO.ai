# Telegram'dan demo hesabı yönetme (Cloudflare, ücretsiz)

Bu kurulumdan sonra Telegram'da botuna yazdığında cevap **anında** gelir. Bilgisayarın kapalı olabilir. Kart, ücret yok.

Komutlar:
- `/durum`: bakiye, açık işlemler, kâr/zarar
- `/gecmis`: son kapanan 10 işlem
- `/fiyat BTC`: güncel fiyat (bilgi amaçlı, sinyal değil)
- `/kapat NEAR`: o coindeki demo işlemini hemen kapatır (sadece senin özel sohbetinden)
- `/yardim`: komut listesi

Bunlara ek olarak Pusula işlem açınca/kapatınca bot sana kendiliğinden mesaj atar (4 saatte bir çalışan bot gönderir).

> Not: Bu kurulumdan sonra bilgisayardaki eski Telegram botunu (`py -m signals.dispatcher.bot run`) çalıştırmana gerek yok. İkisi aynı anda çalışamaz.

## 1. Cloudflare hesabı aç (telefondan da olur)
1. https://dash.cloudflare.com/sign-up adresine git, e-posta ve şifreyle kaydol. Kart istemez. E-postana gelen onay linkine tıkla.
2. Sol menüde **Compute (Workers)** → **Workers & Pages**'e bir kez gir. İlk girişte senin için `....workers.dev` adresi açılır. Bir isim sorarsa (ör. `asgo`) yaz ve onayla.
3. **Account ID**: aynı sayfada sağda "Account ID" yazan kodu kopyala (yoksa sol üstte hesap adının yanındaki menüde "Copy account ID").

## 2. Cloudflare anahtarı (API token) oluştur
1. Sağ üstte profil simgesi → **My Profile** → **API Tokens** → **Create Token**.
2. **Edit Cloudflare Workers** şablonunun yanındaki **Use template**'e bas.
3. "Account Resources" kısmında kendi hesabını seç, "Zone Resources" kısmında **All zones** kalsın.
4. **Continue to summary** → **Create Token**. Çıkan anahtarı kopyala (bir daha gösterilmez).

## 3. GitHub'a gizli olarak gir
GitHub → `traxguo/asgo.ai` → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:
- `CLOUDFLARE_API_TOKEN` → 2. adımdaki anahtar
- `CLOUDFLARE_ACCOUNT_ID` → 1. adımdaki Account ID
- `TELEGRAM_BOT_TOKEN` → bilgisayarındaki `.env` dosyasındaki `TELEGRAM_BOT_TOKEN` değeri
- `TELEGRAM_CHAT_ID` → `.env` dosyasındaki `TELEGRAM_CHAT_ID` değeri

Bitget anahtarları zaten orada; tekrar girme. Hiçbir anahtarı sohbete yapıştırma.

## 4. Çalıştır
GitHub → **Actions** → solda **Telegram bot (Cloudflare)** → **Run workflow**. Bir iki dakika sonra yeşil tik çıkınca Telegram'da botuna `/durum` yaz.

Kırmızı çarpı çıkarsa ekran görüntüsünü bana gönder.

## Grupta da çalışsın (isteğe bağlı)

1. Botu gruba ekle (zaten ekliyse geç).
2. Grupta `/grupid` yaz. Bot sadece sana, grubun numarasını söyler (eksiyle başlar, ör. -100...).
3. GitHub → Settings → Secrets and variables → Actions → New repository secret: ad `TELEGRAM_GROUP_ID`, değer o numara.
4. Actions → **Telegram bot (Cloudflare)** → Run workflow.

Grupta herkes /durum, /gecmis, /fiyat kullanabilir; /kapat'ı sadece sen kullanabilirsin.

## Bitget'e GitHub üzerinden sorma (GH_DISPATCH_TOKEN)

Bitget, Cloudflare sunucularından gelen istekleri engelliyor. Bu yüzden bot /durum, /gecmis,
/fiyat ve /kapat komutlarını GitHub'a iletiyor; cevabı GitHub'daki küçük bir iş ("Telegram komutu")
Bitget'e sorup Telegram'a yolluyor (yaklaşık 30 saniye). Bunun için bir kerelik bir GitHub anahtarı gerekir:

1. github.com/settings/personal-access-tokens/new adresini aç (Fine-grained token).
2. Token name: `asgo-telegram`. Expiration: 1 yıl (ya da en uzun seçenek).
3. Repository access: **Only select repositories** → **ASGO.ai**.
4. Permissions → Repository permissions → **Actions: Read and write**. Başka hiçbir şey seçme.
5. **Generate token**, çıkan değeri kopyala (bir kez gösterilir).
6. ASGO.ai → Settings → Secrets and variables → Actions → New repository secret:
   ad `GH_DISPATCH_TOKEN`, değer o token.
7. Actions → **Telegram bot (Cloudflare)** → Run workflow.

Bu anahtar sadece "Telegram komutu" işini başlatabilir; koda veya ayarlara dokunamaz.
