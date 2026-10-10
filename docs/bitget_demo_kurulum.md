# Pusula'yı bilgisayarın kapalıyken de çalıştırma (Bitget demo, ücretsiz)

Bu rehberle Pusula, GitHub'ın ücretsiz sunucusunda **4 saatte bir** kendi kendine çalışır ve Bitget **demo** hesabında (oyun parası) işlem açar. Bilgisayarının açık olması gerekmez. Kart, ücret, sunucu kiralama yok.

> Sadece Bitget'in **demo** modunda oluşturulan anahtarı kullan. Gerçek hesap anahtarı demo'da çalışmaz; program da her istekte demo işaretini kontrol eder, yoksa hiçbir şey göndermeden durur.

## Bilmen gerekenler
- Program her 4 saatlik mum kapanışından birkaç dakika sonra çalışır (Türkiye saatiyle yaklaşık 03:07, 07:07, 11:07, 15:07, 19:07, 23:07). GitHub bazen 10-20 dakika geç başlatır, bu normal.
- Stop emri, giriş emriyle birlikte Bitget'e konur. Yani zarar sınırı her zaman borsada durur.
- Çalışan sürüm: **Pusula v2**. Ayda 2-3 işlem açar, bir işlem ortalama 11 gün sürer. Sabırlı olmak gerekiyor.
- Her işlem `forward/bitget_demo/` klasörüne yazılır. Ben bunları kağıt takip gibi inceleyip haftalık raporda sana anlatırım.

## 1. Bitget demo anahtarı al
> **Önce kimlik doğrulaması (KYC) gerekir.** Bitget, demo API anahtarını sadece kimliği doğrulanmış hesaplara verir. KYC yoksa API sayfası sadece **gerçek hesap** anahtarı oluşturur; o anahtarla program "demo anahtarı değil" deyip durur (Bitget hata 40099). Önce Identity verification adımını tamamla.

1. https://www.bitget.com adresinde hesabına gir (hesabın yoksa e-posta ile aç).
2. Üstte **Futures** (Vadeli) sayfasına geç, sağ üstte **Demo trading** (Demo işlem) moduna geç. Demo hesapta oyun parası (SUSDT/USDT) olduğunu gör.
3. Demo modundayken profil → **API Key Management** (API Yönetimi) → **Create Demo API Key** (Demo API anahtarı oluştur).
4. Bir isim ver (ör. `pusula-demo`) ve bir **passphrase** (parola cümlesi) belirle. Bunu bir yere not et.
5. İzinler: **Futures → Read/Write (Okuma ve İşlem)** açık. **Withdraw (Para çekme) kapalı.**
6. Çıkan **API Key** ve **Secret Key**'i kopyala. Secret bir daha gösterilmez.

## 2. Anahtarları GitHub'a gizli olarak gir
Bu anahtarlar projeye (dosyalara) **girmez**; GitHub'ın kasasında saklanır, kimse göremez.
1. GitHub'da `traxguo/asgo.ai` projesini aç.
2. **Settings** (Ayarlar) → solda **Secrets and variables** → **Actions**.
3. **New repository secret** ile üç tane ekle (isimler birebir böyle olsun):
   - `BITGET_DEMO_API_KEY` → API Key
   - `BITGET_DEMO_API_SECRET` → Secret Key
   - `BITGET_DEMO_API_PASSPHRASE` → 1. adımda belirlediğin passphrase
4. Anahtarları sohbete yapıştırma.

## 3. Bir kez elle dene
1. GitHub'da projede üstte **Actions** sekmesine gir.
2. Solda **Pusula Bitget demo** → sağda **Run workflow** → yeşil **Run workflow**.
3. Bir iki dakika sonra yeşil tik görmelisin. Kırmızı çarpı çıkarsa ekran görüntüsünü bana gönder.

Bundan sonra kendisi 4 saatte bir çalışır. Hiçbir şey yapmana gerek yok.

## 4. Takip et
- **Bitget'te:** uygulamada ya da sitede Demo moduna geç → Futures → Positions (Pozisyonlar) ve Order history (Emir geçmişi).
- **Raporda:** her pazartesi kağıt takip raporunda demo sonuçlarını da yazarım.

## Durdurmak
GitHub → Actions → **Pusula Bitget demo** → sağ üstte **⋯** → **Disable workflow**. Açık işlemler Bitget demo hesabında kalır; oradan elle kapatabilirsin.

## Neden Binance değil?
GitHub'ın ücretsiz sunucuları ABD'de. Binance (demo dahil) ve Bybit demo ABD'den bağlantıyı engelliyor; Bitget engellemiyor. Bilgisayarındaki Binance demo botu istersen çalışmaya devam edebilir, ikisi birbirini etkilemez.
