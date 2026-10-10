# Pusula'yı Binance demo hesabında çalıştırma (oyun parası)

Bu rehber, Pusula'nın senin bilgisayarından **Binance demo hesabında** (gerçek para değil) işlem açması içindir. İşlemleri hem demo.binance.com'da hem de bilgisayarındaki küçük bir ekranda görürsün.

> Gerçek hesap anahtarını **asla** kullanma. Sadece demo.binance.com'da oluşturulan anahtar. Program, bağlandığı adresin demo sunucusu olduğunu her açılışta kontrol eder; değilse emir göndermeden durur.

## Bilmen gerekenler
- Demo hesap Binance'in **ayrı** bir piyasası. Fiyatlar gerçek piyasaya çok yakın ama birebir aynı değil. Bu yüzden demo sonuçları kağıt takipten biraz farklı çıkabilir.
- Pusula ayda 2-3 işlem açar, bir işlem ortalama 11 gün sürer. Bilgisayar ve program açık kalmalı; kapalıyken yeni işlem açılmaz (açık işlemlerin stopu Binance'te durur).
- Çalışan sürüm: **Pusula v2** (arka plan turlarında kabul edilen geliştirmeler dahil).

## 1. Demo API anahtarı al
1. https://demo.binance.com adresine git, Binance hesabınla giriş yap.
2. Sağ üstten profil → **API Management** (API Yönetimi).
3. **Create API** → "System generated" seç, bir isim ver (ör. `pusula-demo`).
4. Çıkan **API Key** ve **Secret Key**'i kopyala. Secret bir daha gösterilmez.
5. İzinlerde **Enable Futures** açık olsun. Para çekme izni olmasın.
6. Demo futures cüzdanında USDT olduğundan emin ol (demo hesap başlangıçta oyun parası verir).
7. Futures ayarlarında pozisyon modu **One-way** (tek yönlü) olsun.

## 2. Programı indir
1. Bu değişiklikler PR #10'da. PR'ı yeşil butonla birleştir (merge).
2. GitHub'dan projeyi yeniden ZIP olarak indir ve eski klasörün üstüne çıkart. `.env` dosyan kalır.

## 3. Freqtrade'i kur (bir kez)
Telegram botunun çalıştığı klasörde bir komut penceresi (cmd) aç:
```
cd C:\Users\GUO\Desktop\ASGO\ASGO.ai-main\ASGO.ai-main
py -m pip install freqtrade
py -m freqtrade install-ui
```
Kurulum birkaç dakika sürebilir. Hata çıkarsa ekran görüntüsünü bana gönder.

## 4. Anahtarları .env dosyasına yaz
`.env` dosyasını Not Defteri ile aç, en alta ekle:
```
BINANCE_DEMO_API_KEY=buraya_demo_api_key
BINANCE_DEMO_API_SECRET=buraya_demo_secret_key
FREQTRADE_API_USERNAME=guo
FREQTRADE_API_PASSWORD=kendi_sectigin_bir_sifre
```
Şifre en az 8 karakter olsun. Bu dosyayı kimseyle paylaşma, sohbete yapıştırma.

## 5. Başlat
```
py scripts\demo_freqtrade.py
```
Pencerede "Demo trading enabled" ve "Bot heartbeat" satırlarını görmelisin. Pencereyi kapatma.

## 6. Takip et
- **Binance'te:** demo.binance.com → Futures → Positions / Order History.
- **Bilgisayarında:** tarayıcıda http://127.0.0.1:8080 aç, `.env`'deki kullanıcı adı ve şifreyle gir. Açık işlemler, kâr/zarar ve geçmiş burada.
- Ben de buradaki haftalık raporda demo sonuçlarını kağıt takiple yan yana koyacağım (ekran görüntüsü veya "Trades" sekmesindeki tabloyu gönderirsen).

## Durdurmak
Komut penceresinde `Ctrl + C`. Açık işlemler Binance demo hesabında kalır; demo.binance.com'dan elle kapatabilirsin.
