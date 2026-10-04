# PROJECT BRIEF — Kripto Futures Strateji Araştırma ve Sinyal Sistemi

> Bu doküman Claude Code için yazıldı. Projenin tamamını, kurallarını ve yol haritasını tarif eder.
> Claude Code: Bu dosyayı baştan sona oku. İlk görevin, bölüm 14'teki adımları uygulamak.

---

## 0. Senin rolün

Sen bu projenin geliştiricisi ve araştırmacısısın. Görevlerin:

- Sistemi kurmak ve sürdürmek
- Strateji fikirlerini koda dökmek ve test etmek
- Sonuçları **dürüstçe** yorumlamak. Kötü sonucu güzel göstermek yasak.
- Her oturumda öğrenilenleri repoya yazmak (bölüm 4)

Proje sahibi yazılım geçmişi olmayan biri. Teknik kararlarını kısa ve sade Türkçeyle açıkla, kod içi isimlendirme ve yorumlar İngilizce olsun.

---

## 1. Proje özeti

Binance USDⓈ-M perpetual futures piyasasında al-sat (long ve short) stratejilerini bilimsel bir test hattından geçiren, sonuçlarını ve öğrendiklerini kendi GitHub reposunda biriktiren bir **araştırma sistemi**. Son aşamada, testten geçmiş stratejiler canlı piyasayı izler ve proje sahibine kişisel Telegram üzerinden **"giriş bölgesi / stop / TP1-TP2"** formatında, gerekçesi açıklanmış ve görselleştirilmiş sinyaller gönderir.

**Bu sistem gerçek işlem yapmaz.** Sadece geçmiş veride test (backtest) ve canlı veride sanal işlem (forward test / dry-run) yapar. Sinyalleri değerlendirmek ve elle işleme girip girmemek proje sahibinin kararıdır.

### Değişmez kurallar

1. **Gerçek emir yok.** Freqtrade her zaman `dry_run: true` ile çalışır. Bunu kontrol eden bir script yazılacak ve her çalıştırmadan önce çalışacak.
2. **İşlem yetkili API key yok.** Veri herkese açık kaynaklardan çekilir. Gerekli tüm token ve key'ler (ör. Telegram bot token) `.env` içinde durur, `.gitignore`'dadır, repoya asla girmez.
3. **Sinyaldeki her rakam test edilmiş kuralların çıktısıdır.** Giriş bölgesi, stop, TP'ler, kısmi çıkış ve break even kuralları stratejinin kodunda tanımlıdır ve backtest'te birebir aynı şekilde simüle edilir. Hiçbir seviye sonradan "yorumla" üretilmez veya değiştirilmez.
4. **Dürüstlük.** Başarısız stratejiler silinmez, `strategies/retired/` altına gerekçesiyle taşınır.
5. **Kasa verisine dokunma.** Bölüm 8'deki "holdout" dönemi geliştirme sırasında asla kullanılmaz.
6. **Al-tut kıyası zorunlu.** Her raporda strateji, aynı dönemde ilgili coini "al ve tut" sonucuyla kıyaslanır.
7. **Sinyaller sadece proje sahibine gider.** Telegram botu yalnızca proje sahibinin kişisel sohbet ID'sine mesaj atar; grup veya kanal desteği eklenmez.

---

## 2. Teknoloji yığını

| Parça | Seçim | Not |
|---|---|---|
| Dil | Python 3.11+ | |
| Ana motor | Freqtrade (`trading_mode: futures`, `margin_mode: isolated`) | Backtest, dry-run, long/short, kısmi çıkış, özel stop yönetimi, funding hesabı, lookahead kontrolleri |
| Ek analiz | pandas, numpy, vectorbt (gerekirse) | Walk-forward, Monte Carlo, parametre testleri |
| Sinyal görseli | mplfinance veya plotly (+ kaleido) | Mum grafiği üzerine seviyeler + açıklama paneli, PNG |
| Bildirim | Telegram Bot API | Freqtrade webhook → sinyal servisi → kişisel sohbet |
| Veri | Binance USDⓈ-M futures public endpoint'leri + data.binance.vision futures arşivi | Key gerekmez |
| Çalışma ortamı | Docker (Freqtrade resmi imajı) | |

Bulunulan konumdan Binance futures endpoint'lerine erişim engelliyse: önce data.binance.vision arşivini dene, o da olmazsa durumu proje sahibine bildir ve `docs/decisions.md`'ye yaz.

---

## 3. Repo yapısı

```
quant-lab/
├── CLAUDE.md                  # Senin için kısa özet + oturum protokolü
├── PROJECT_BRIEF.md           # Bu dosya
├── README.md
├── .env.example               # Boş şablon (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID vb.)
├── .gitignore
├── docker-compose.yml
│
├── config/
│   ├── base.json              # dry_run: true, trading_mode: futures, fee, stake vb.
│   ├── pairs_level1.json
│   └── pairs_level2/          # Dönemsel coin evrenleri (tarihli)
│
├── strategies/
│   ├── common/                # Ortak işlem yönetimi modülü (bölüm 7)
│   ├── active/
│   ├── candidates/
│   └── retired/
│
├── cards/                     # Strateji kartları
│
├── signals/
│   ├── schema.py              # Sinyal veri yapısı (bölüm 7.7)
│   ├── explainer/             # Koşul → Türkçe açıklama şablonları
│   ├── renderer/              # Görsel üretimi
│   ├── templates/             # Mesaj ve görsel şablonları, tasarım referansları
│   ├── dispatcher/            # Webhook'u dinleyip Telegram'a gönderen servis
│   └── log/                   # Gönderilen tüm sinyallerin JSON kaydı
│
├── manual_trades/
│   └── trades.csv             # Proje sahibinin elle girdiği işlemler (bölüm 7.11)
│
├── research/
│   ├── data/
│   ├── robustness/
│   ├── universe/
│   └── reports/
│
├── results/
│   └── YYYY-MM-DD_<strateji>_<test>/
│
├── journal/
│   └── YYYY-MM-DD.md
│
├── docs/
│   ├── rules.md
│   ├── decisions.md
│   ├── metrics.md
│   └── roadmap.md
│
└── scripts/
    ├── safety_check.py
    └── ...
```

---

## 4. Hafıza sistemi

Repo, senin oturumlar arası hafızandır. Bir sonraki oturumdaki sen, bu dosyalardan başka hiçbir şey hatırlamayacak.

### Oturum başı
1. `CLAUDE.md`'yi oku
2. `docs/roadmap.md`'den şu anki seviyeyi ve sıradaki işi bul
3. Son 2-3 `journal/` girdisini oku
4. Üzerinde çalışılacak stratejinin kartını oku

### Oturum sonu
1. `journal/YYYY-MM-DD.md` yaz
2. Etkilenen strateji kartlarını güncelle
3. Önemli kararları `docs/decisions.md`'ye ekle (tarih + karar + gerekçe)
4. `docs/roadmap.md`'yi güncelle
5. Anlamlı bir commit mesajıyla commit at

### Günlük şablonu
```markdown
# YYYY-MM-DD
## Yapılanlar
## Bulgular (rakamlarla)
## Başarısız olan / elenen
## Açık sorular
## Sıradaki adım
```

---

## 5. Veri katmanı

- **Kaynak:** Binance USDⓈ-M perpetual futures, USDT pariteleri
- **Veri türleri:** Fiyat mumları (OHLCV), **funding rate geçmişi** ve **mark price** mumları. Freqtrade futures modunda bunları indirir; eksiksiz indirildiğini doğrula.
- **Zaman dilimleri:** Başlangıçta `1h` ve `4h`. Daha kısa periyotlar Seviye 1 kanıtlanmadan açılmaz.
- **Dönem:** Futures verisinin mümkün olan en eski tarihinden bugüne; en az bir tam boğa ve bir tam ayı dönemi (ör. 2022) içerilmeli. Bazı coinlerin futures geçmişi kısa olabilir; her coin için başlangıç tarihi raporlanır.
- **Doğrulama scripti** (`research/data/validate.py`): eksik mumlar, tekrar eden kayıtlar, sıfır hacimli dönemler, aşırı sıçramalar, funding verisinde boşluklar. Sorunlar raporlanır, sessizce düzeltilmez.
- **Seviye 2 için:** Delist olmuş futures kontratlarının verisi de mümkün olduğunca toplanmalı. Ne kadarının bulunduğunu doğrula, sınırlamayı `docs/decisions.md`'ye yaz.

---

## 6. Strateji standardı

Her strateji, kodlanmadan önce bir **strateji kartı** alır: `cards/<strateji_adi>.md`

```markdown
# <Strateji adı>

## Hipotez
Bu strateji neden çalışmalı? Hangi piyasa davranışını yakalıyor? (1-3 cümle)

## Yön
long / short / ikisi de

## Giriş koşulları
Her koşul: teknik tanım + sinyal açıklamasında kullanılacak Türkçe cümle
- [koşul_id] Teknik: ... | Açıklama: "..."

## İşlem yönetimi
- Giriş bölgesi kuralı:
- Stop kuralı:
- TP modeli (bölüm 7.3'teki varyantlardan hangisi):
- Sinyal geçerlilik süresi:

## Zaman dilimi ve parametreler (makul aralıklarıyla)

## Durum: candidate / active / retired

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |

## Notlar / öğrenilenler
## Emeklilik gerekçesi (varsa)
```

### Başlangıç strateji ailesi
1. **Trend takibi:** Hareketli ortalama kesişimi + trend filtresi (long ve short simetrik)
2. **Kırılım:** Donchian kanalı kırılımı (yukarı → long, aşağı → short)
3. **Ortalamaya dönüş:** RSI aşırı satım/alım + trend filtresi
4. **Volatilite filtresi:** Yukarıdakilerin ATR tabanlı "piyasa uygun mu" filtresi eklenmiş versiyonları

Her strateji az parametreli olmalı (ideal: 2-4). Seviye 1'de karmaşık yapay zeka modelleri yok. **Long ve short tarafları her zaman ayrı ayrı da raporlanır;** bir taraf zarar ettiriyorsa strateji o tarafta kapatılabilir.

---

## 7. İşlem yönetimi ve sinyal standardı

Bu bölüm, sistemin ürettiği her sinyalin nasıl hesaplandığını tanımlar. Tüm stratejiler bu yönetimi `strategies/common/` altındaki **ortak modülden** kullanır; böylece backtest, dry-run ve gönderilen mesaj aynı kodu çalıştırır. Kurallar long ve short için simetriktir.

### 7.1 Giriş bölgesi
- Strateji sinyal verdiğinde tek bir fiyat değil, bir **giriş bölgesi** hesaplanır (ör. sinyal mumunun kapanışı ile kapanış ∓ 0.25 ATR arası, veya stratejinin tanımladığı destek/direnç seviyesi etrafı). Kural strateji kartında yazılıdır.
- Giriş, bölge içinde limit emir varsayımıyla simüle edilir (Freqtrade `custom_entry_price` + emir zaman aşımı).
- **Geçerlilik süresi:** Fiyat N mum içinde bölgeye gelmezse sinyal iptal edilir.
- Fiyat bölgeye girmeden stop seviyesine ulaşırsa sinyal iptal edilir.
- İptaller de mesajla bildirilir ve loglanır.

### 7.2 Stop (zarar kes)
- Varsayılan kural: **yapısal stop** (long için son anlamlı dip altı, short için son anlamlı tepe üstü + küçük tampon) ile **ATR tabanlı stop** (ör. 1.5 ATR) hesaplanır; strateji kartı hangisinin veya hangi kombinasyonun kullanılacağını belirtir.
- **Risk birimi (R)** = giriş bölgesinin ortası ile stop arasındaki mesafe.
- Stop mesafesi belirlenen üst sınırı aşıyorsa (ör. fiyatın %X'i) sinyal **üretilmez**.

### 7.3 Hedefler (TP) — 2 TP modeli

Sistem **2 TP** kullanır. TP mesafeleri R katı olarak tanımlanır. **TP1 hiçbir zaman 1R'den küçük olamaz.**

**Varsayılan model (Model B — kısmi çıkışlı):**
- **TP1 = 2R** → pozisyonun **%50'si** kapatılır
- **TP1 gelince stop girişe çekilir (break even)**
- **TP2 = 4R** → kalan %50 kapatılır

Olası sonuçlar (maliyet hariç): stop → **−1R** | TP1 sonrası break even → **+1R** | TP2 → **+3R**

**Karşılaştırma modeli (Model A — tek çıkışlı):**
- Pozisyonun tamamı **TP = 4R**'de kapatılır
- Fiyat **2R kâra geçince stop girişe çekilir** (break even), kısmi çıkış yok

Olası sonuçlar: stop → **−1R** | break even → **0R** | TP → **+4R**

**Test edilecek varyant ızgarası (sınırlı tutulur, ezberden kaçınmak için genişletilmez):**
| Parametre | Değerler |
|---|---|
| TP1 | 1.5R, 2R |
| TP2 | 3R, 4R |
| TP1'deki kısmi çıkış | %0 (Model A), %50 (Model B) |
| Break even tetikleyicisi | TP1 / 2R kâr |

**Seçim kuralı:** Model, winrate'e göre değil **maliyet sonrası ortalama R (expectancy), max drawdown ve komşu varyantlarda kararlılık** ölçütlerine göre seçilir. Tek bir varyant parlıyor ama komşuları kötüyse seçilmez. Seçim gerekçesi strateji kartına ve `docs/decisions.md`'ye yazılır. Trend ve kırılım stratejileri ile ortalamaya dönüş stratejileri için farklı modellerin kazanması normaldir.

### 7.4 Kısmi çıkış
- Freqtrade `adjust_trade_position` ile uygulanır.
- Backtest ile mesaj her zaman aynı oranları kullanır.

### 7.5 Break even
- Stop giriş seviyesine çekilirken komisyonu ve birikmiş funding'i karşılayacak küçük bir tampon eklenir.
- Freqtrade `custom_stoploss` ile uygulanır.
- Takip eden stop (trailing) gibi alternatif kurallar ileride test edilebilir, ancak testten geçmeden kullanılmaz.

### 7.6 Kaldıraç ve likidasyon
- Pozisyon büyüklüğü **R'ye göre** hesaplanır (bölüm 10); kaldıraç sadece teminat verimliliği içindir ve riski artırmaz.
- Simülasyonda **izole marjin, düşük kaldıraç** (varsayılan en fazla 3x) kullanılır.
- **Likidasyon fiyatı, stop mesafesinin en az 2 katı uzakta olmalıdır.** Bu şart sağlanmıyorsa kaldıraç düşürülür veya sinyal üretilmez.

### 7.7 Sinyal veri yapısı
Her sinyal, mesaj ve görsel üretilmeden önce bu yapıya yazılır ve `signals/log/` altına kaydedilir:

```json
{
  "signal_id": "2026-10-02T14:00Z_ETHUSDT_trend_ma_v2",
  "timestamp": "2026-10-02T14:00:00Z",
  "pair": "ETH/USDT:USDT",
  "timeframe": "4h",
  "strategy": "trend_ma_v2",
  "side": "long",
  "entry_zone": {"high": 3420.0, "low": 3405.0},
  "stop": 3360.0,
  "risk_R": 52.5,
  "targets": [
    {"level": "TP1", "price": 3517.5, "R": 2.0, "close_pct": 50},
    {"level": "TP2", "price": 3622.5, "R": 4.0, "close_pct": 50}
  ],
  "management": {
    "model": "B",
    "breakeven_trigger": "TP1",
    "valid_for_candles": 3
  },
  "leverage": 3,
  "liquidation_price_est": 2340.0,
  "funding_rate_at_signal": 0.0001,
  "triggered_conditions": [
    {"id": "trend_up", "value": "close 3418 > EMA200 3210"},
    {"id": "pullback", "value": "price touched EMA50 3402"},
    {"id": "rsi_turn", "value": "RSI 36 -> 42"}
  ],
  "stop_reason": "below_swing_low",
  "status": "open"
}
```

Durum değerleri: `pending` (bölgeye girilmedi), `open`, `tp1_hit`, `breakeven`, `closed`, `cancelled`.

### 7.8 Mesaj formatları
Mesajlar `signals/templates/` altındaki şablonlardan, sinyal veri yapısıyla doldurulur.

**Long giriş:**
```
📈 ETH/USDT LONG — ALIM BÖLGESİ: 3420 - 3405
🛑 Zarar Kes: 3360
✅ TP 1: 3517 (2R) — %50 kapat, stop girişe
✅ TP 2: 3622 (4R)
⏳ Geçerlilik: 3 mum (4h)

⚠️ Bu sinyal otomatik sistem tarafından üretilmiştir. Yatırım tavsiyesi değildir, risk yönetimini kendiniz uygulayın.
```

**Short giriş:**
```
📉 SOL/USDT SHORT — SATIŞ BÖLGESİ: 182.4 - 183.6
🛑 Zarar Kes: 186.0
✅ TP 1: 175.8 (2R) — %50 kapat, stop girişe
✅ TP 2: 168.6 (4R)
⏳ Geçerlilik: 3 mum (1h)
```

**Güncelleme mesajları:**
```
🎯 ETH/USDT TP1 geldi (3517) — %50 kapatıldı, stop girişe çekildi (break even)
🏁 ETH/USDT kapandı — Sebep: TP2 | Sonuç: +3.0R | Süre: 2g 6s
⚖️ ETH/USDT break even'da kapandı — Sonuç: +1.0R (TP1 kârı)
❌ ETH/USDT stop oldu — Sonuç: -1R
🚫 ETH/USDT sinyali iptal — fiyat geçerlilik süresinde bölgeye gelmedi
```
Sonuçlar R cinsinden, funding ve komisyon dahil verilir.

### 7.9 Açıklama üretimi
Her giriş mesajına ve görseline şu dört başlıkta açıklama eklenir:

1. **Neden bu işlem:** `triggered_conditions` içindeki her koşulun strateji kartındaki Türkçe açıklama cümlesi, gerçek değerleriyle
2. **Stop neye göre:** `stop_reason` + hesap (ör. "Son dip 3372'nin altına 12 puan tampon")
3. **TP'ler nasıl hesaplandı:** R tanımı ve katları (ör. "Risk 52.5 puan; TP1 = 2R, TP2 = 4R")
4. **İşlem yönetimi:** Kısmi çıkış ve break even kuralı

**Kural:** Açıklamalar **şablon tabanlıdır**, sadece gerçekten tetiklenmiş koşullar ve gerçek değerler kullanılır. Canlı akışta bir dil modeli seviyeleri veya gerekçeyi yeniden yazmaz/uydurmaz. Açıklama metinlerinin kalitesini Claude Code geliştirme sırasında şablonlar üzerinden iyileştirir.

Örnek çıktı:
```
🧠 Neden: 4h trend yukarı (fiyat 3418, EMA200 3210 üzerinde). Fiyat EMA50'ye (3402) geri çekildi ve RSI 36'dan 42'ye döndü.
🛑 Stop: Son dip 3372'nin altı, 12 puan tampon.
🎯 TP'ler: Risk 52.5 puan (1R). TP1 = 2R, TP2 = 4R.
🔁 Yönetim: TP1'de pozisyonun yarısı kapanır, stop girişe çekilir.
```

### 7.10 Görsel şablon
- Her giriş sinyalinde bir PNG üretilir (mobil için dikey, ör. 1080×1350).
- **Üst kısım:** Son ~100 mumluk grafik; giriş bölgesi gölgeli alan, stop kırmızı çizgi, TP1-TP2 yeşil çizgiler, tetikleyen indikatörler (ör. EMA'lar) çizili. Long/short yönü net görünür.
- **Alt kısım:** Seviyeler tablosu + bölüm 7.9'daki dört başlıklı açıklama paneli.
- Tasarım (renkler, yazı tipleri, yerleşim) proje sahibiyle ayrıca belirlenecek; referans görseller `signals/templates/design/` altına konacak ve renderer bu referansa göre şablonlanacak. Kod her sinyalde şablonu otomatik doldurur.
- Güncelleme mesajları varsayılan olarak metin olur; görsel isteğe bağlıdır.

### 7.11 Elle işlem kaydı
Proje sahibi sinyallere göre elle işlem yapabilir. Bunları sistemin sanal sonuçlarından ayrı izlemek için:
- `manual_trades/trades.csv`: signal_id, gerçek giriş fiyatı/zamanı, gerçek çıkışlar, kaldıraç, notlar
- Kayıt için basit bir komut (ör. `python scripts/log_trade.py ...`) veya Telegram komutu
- Haftalık raporda **sistemin sanal sonucu vs. elle işlemlerin sonucu** karşılaştırılır (gecikme, atlanan sinyal, erken çıkış etkisi)

---

## 8. Test hattı

Her strateji bu aşamalardan sırayla geçer. **Tüm testler bölüm 7'deki işlem yönetimiyle (giriş bölgesi, 2 TP modeli, kısmi çıkış, break even, funding) yapılır.** Basitleştirilmiş bir yönetimle test edilip farklı bir yönetimle sinyal üretmek yasaktır.

### Veri bölümü
| Bölüm | Kullanım |
|---|---|
| Geliştirme (in-sample) | Strateji geliştirme, TP model seçimi ve optimizasyon |
| Doğrulama (out-of-sample) | Geliştirmede görülmemiş veride test |
| **Kasa (holdout)** | **Son 6 ay. Sadece "active" olmadan önceki son test için, bir kez kullanılır.** |

### Aşamalar
1. **Kod doğruluğu:** Freqtrade `lookahead-analysis` ve `recursive-analysis`
2. **İlk backtest:** Geliştirme verisi, Seviye 1 listesi, maliyetler ve funding dahil
3. **TP model seçimi:** Bölüm 7.3'teki ızgara, sadece geliştirme verisinde
4. **Doğrulama testi:** Seçilen modelle, görmediği veride
5. **Dayanıklılık testleri:** walk-forward (ör. 12 ay optimize / 3 ay test), parametre kararlılığı (±%20), çoklu coin, Monte Carlo
6. **Kasa testi:** Tek seferlik
7. **İleri test (dry-run):** Canlı veride sanal işlem; sonuçlar backtest beklentisiyle karşılaştırılır

### Geçme eşikleri (başlangıç önerisi — `docs/metrics.md`'de tutulur)
- **Maliyet ve funding sonrası ortalama sonuç > 0R** (expectancy)
- Doğrulama verisinde profit factor ≥ 1.2
- Max drawdown ≤ %25
- Toplam en az 100 işlem
- Seviye 1 listesindeki coinlerin en az yarısında pozitif sonuç
- Parametre ve TP varyantı komşularında da pozitif sonuç
- Al-tut ile kıyasta: daha yüksek getiri, ya da benzer getiriyle belirgin şekilde düşük drawdown

### Raporlarda ayrıca gösterilecek sinyal istatistikleri
- Stop / break even / TP1 / TP2 ile kapanma oranları
- Ortalama R ve R dağılımı
- Long ve short ayrı sonuçlar
- Toplam funding maliyeti/geliri
- İptal edilen sinyal oranı (bölgeye gelmeyen)

**Winrate tek başına bir başarı kriteri değildir.**

---

## 9. Maliyet modeli

**Bilerek kötümser ol.**
- Komisyon: her giriş ve çıkış için taker oranı varsayılır (başlangıç: %0.05; Binance'in güncel futures ücretlerini doğrula). Kısmi çıkışların her biri ayrı işlem sayılır.
- Kayma: ek %0.05
- **Funding:** Pozisyon açıkken gerçekleşen funding ödemeleri geçmiş funding verisinden hesaplanır ve sonuca dahil edilir.
- Aynı test maliyet x2 ile de çalıştırılır. Maliyet ikiye katlanınca kârsız hale gelen strateji kırılgandır.

---

## 10. Risk kuralları (simülasyonda da geçerli)

- Her stratejide stop zorunlu
- İşlem başına sermayenin sabit ve küçük bir yüzdesi (ör. %1) riske edilir; pozisyon büyüklüğü stop mesafesine (R) göre hesaplanır
- İzole marjin, varsayılan en fazla 3x kaldıraç, likidasyon kuralı (bölüm 7.6)
- Aynı anda açık işlem sayısı sınırlı (`max_open_trades`); aynı coinde aynı anda hem long hem short yok
- **Kill switch:** Dry-run'da drawdown eşiği aşılırsa strateji durdurulur, sinyal gönderimi kesilir, durum günlüğe yazılır ve proje sahibine bildirim gider

---

## 11. Raporlama

Her test `results/YYYY-MM-DD_<strateji>_<test>/rapor.md` üretir:

```markdown
# <Strateji> — <Test türü> — <Tarih>
## Özet (3 cümle, sade Türkçe)
## Ayarlar (dönem, coinler, zaman dilimi, yön, TP modeli, kaldıraç, maliyet varsayımı)
## Metrikler
| Metrik | Strateji | Al-tut |
|---|---|---|
| Net getiri | | |
| Max drawdown | | |
| Profit factor | | — |
| Ortalama R | | — |
| İşlem sayısı | | — |
| Winrate | | — |
## Long / short ayrımı
## Sinyal istatistikleri (stop/BE/TP1/TP2/iptal oranları, funding)
## Grafikler (sermaye eğrisi, drawdown, R dağılımı)
## Yorum: güçlü yanlar / şüpheli noktalar
## Karar: devam / düzelt / emekli
```

---

## 12. Yol haritası

Seviyeler sırayla ilerler. Bir seviyenin çıkış şartı sağlanmadan sonrakine geçilmez.

### Seviye 0 — Altyapı
- Repo yapısı, Docker, Freqtrade futures kurulumu, `safety_check.py`
- Veri indirme (OHLCV + funding + mark price) ve doğrulama
- Hafıza dosyaları
- **Ortak işlem yönetimi modülü** (`strategies/common/`, bölüm 7.1-7.6) ve sinyal veri yapısı (`signals/schema.py`)
- Bir örnek stratejiyle uçtan uca test + rapor

**Çıkış şartı:** Tek komutla veri indirilip, bir strateji bölüm 7'deki yönetimle (Model A ve B) test edilip, rapor üretilebiliyor.

### Seviye 1 — Sabit liste: "Bu strateji çalışıyor mu?"
- Coin listesi: BTC, ETH + hacmi yüksek 3-5 futures paritesi (seçim gerekçesi `decisions.md`'de)
- Strateji ailesi test hattından geçirilir, TP modeli her strateji için seçilir
- Dayanıklılık araçları yazılır
- Çoğu stratejinin elenmesi normaldir

**Çıkış şartı:** En az bir strateji test hattının 1-6. aşamalarını geçmiş ve `active/` klasöründe.

### Seviye 2 — Dinamik evren: "Daha geniş havuzda da çalışıyor mu?"
- Hacme göre filtrelenmiş dinamik liste (ör. son 30 günde hacmi en yüksek 20 futures paritesi, haftalık güncellenir)
- Filtreler: minimum hacim, minimum listelenme süresi, aşırı funding oranına sahip pariteleri dışlama
- **Hayatta kalma yanılgısına karşı:** Her dönemin evreni *o tarihte* mevcut veriden hesaplanır (`research/universe/`), dönemsel sabit listeler olarak kaydedilir (`config/pairs_level2/`). Freqtrade'in dinamik pair listeleri backtest'te desteklenmediği için bu yöntem kullanılır.
- Aktif stratejiler bu evrende yeniden test edilir

**Çıkış şartı:** Aktif strateji(ler) dinamik evrende de eşikleri geçiyor.

### Seviye 3 — Canlı tarayıcı ve metin sinyalleri
- Freqtrade dry-run (futures), Seviye 2 filtreleriyle canlı dinamik liste
- Sinyal servisi (`signals/dispatcher/`): Freqtrade webhook'larını dinler, sinyal veri yapısını oluşturur, loglar ve Telegram'a gönderir
- Bölüm 7.8 mesaj formatları + bölüm 7.9 açıklamaları (metin olarak)
- Kill switch aktif
- Elle işlem kaydı (bölüm 7.11)
- Haftalık otomatik rapor: dry-run vs. backtest beklentisi, sistem vs. elle işlemler

**Çıkış şartı:** Mesajlar eksiksiz ve doğru geliyor; yeterli süre ve işlem sayısında dry-run sonuçları backtest beklentisiyle tutarlı.

### Seviye 4 — Görsel sinyaller
- Görsel tasarımı proje sahibiyle belirlenir, referans `signals/templates/design/`'a konur
- Renderer (bölüm 7.10) yazılır, sinyal servisine bağlanır
- Her giriş sinyali görsel + açıklama paneliyle gönderilir

**Çıkış şartı:** Her giriş sinyali tasarım referansına uygun görselle, birkaç saniye içinde geliyor.

---

## 13. Yapılmayacaklar

- Gerçek emir göndermek veya `dry_run: false` ayarı
- Key, token, şifre veya kişisel bilgiyi repoya koymak
- Kasa (holdout) verisini geliştirme sırasında kullanmak
- Stratejiyi veya TP modelini tek bir iyi sonuç için tekrar tekrar optimize etmek; TP ızgarasını genişletmek
- Kötü sonuçları silmek ya da raporda gizlemek
- Seviye atlamak
- Düşük hacimli paritelerdeki "harika" sonuçlara güvenmek
- Funding'i hesaba katmadan sonuç raporlamak
- Likidasyon fiyatı stop'a yakın olan sinyal üretmek
- Sinyal seviyelerini test edilmiş kurallar dışında üretmek veya değiştirmek
- TP1'i 1R'den küçük tutmak
- Tetiklenmemiş koşulları veya uydurma gerekçeleri açıklamaya yazmak
- Sinyalleri proje sahibinin kişisel sohbeti dışında bir yere göndermek

---

## 14. İlk oturum görevleri

1. Bu dosyayı oku, belirsiz bir nokta varsa proje sahibine sor
2. Bölüm 3'teki repo yapısını oluştur
3. `.gitignore` ve `.env.example` dosyalarını oluştur
4. `scripts/safety_check.py` yaz: config'te `dry_run: true` değilse veya repoda key/token benzeri bir dize varsa hata verip dursun
5. `docs/rules.md`, `docs/metrics.md`, `docs/roadmap.md`, `docs/decisions.md` dosyalarını bu brief'ten oluştur
6. `CLAUDE.md` yaz: 10 satırlık proje özeti + oturum protokolleri + değişmez kurallar
7. Docker ile Freqtrade'i futures modunda kur, Seviye 1 listesi için 1h ve 4h OHLCV, funding ve mark price verisini indir, doğrulama scriptini çalıştır
8. `strategies/common/` altında ortak işlem yönetimi modülünün ilk versiyonunu (Model A ve Model B dahil) ve `signals/schema.py`'yi yaz
9. Basit bir trend takip stratejisiyle (long + short), iki TP modeliyle uçtan uca ilk backtest + karşılaştırmalı rapor
10. İlk journal girdisini yaz, commit at
