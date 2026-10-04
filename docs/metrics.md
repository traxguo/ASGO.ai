# Metrikler ve geçme eşikleri

Bir stratejinin "active" olabilmesi için test hattının 1-6. aşamalarını geçmesi ve aşağıdaki eşikleri sağlaması gerekir. Eşikler başlangıç önerisidir; değişiklik `decisions.md`'ye yazılır.

## Geçme eşikleri
| Ölçüt | Eşik |
|---|---|
| Maliyet ve funding sonrası ortalama sonuç (expectancy) | > 0R |
| Doğrulama verisinde profit factor | ≥ 1.2 |
| Max drawdown | ≤ %25 |
| Toplam işlem sayısı | ≥ 100 |
| Seviye 1 listesinde pozitif sonuç veren coin oranı | ≥ %50 |
| Parametre (±%20) ve TP varyantı komşuları | onlarda da pozitif |
| Al-tut kıyası | daha yüksek getiri, ya da benzer getiriyle belirgin daha düşük drawdown |
| Maliyet x2 testi | hâlâ > 0R (değilse "kırılgan" notu) |

**Winrate tek başına başarı ölçütü değildir.**

## Tanımlar
- **R (risk birimi):** Giriş bölgesinin ortası ile stop arasındaki mesafe. Bir stop-out ≈ −1R.
- **İşlem sonucu (R):** `net kâr/zarar (komisyon + kayma + funding dahil) / (giriş miktarı × |giriş − stop|)`. `scripts/make_report.py` hesaplar.
- **Expectancy (ortalama R):** Tüm işlemlerin R ortalaması.
- **Profit factor:** Toplam kazanç / toplam kayıp (USDT).
- **Max drawdown:** Sermayenin zirveden en büyük yüzde düşüşü.
- **İptal oranı:** Bölgeye gelmeyen veya önce stop'a giden sinyaller / tüm sinyaller.

## Veri bölümleri
| Bölüm | Kullanım |
|---|---|
| Geliştirme (in-sample) | Strateji geliştirme, TP model seçimi, optimizasyon |
| Doğrulama (out-of-sample) | Geliştirmede görülmemiş veride test |
| **Kasa (holdout)** | **Son 6 ay. Sadece "active" öncesi son test, bir kez.** |

Tarih sınırları veri indirildiğinde `decisions.md`'ye yazılacak.

## Raporlarda gösterilenler
- Net getiri, max drawdown, profit factor, ortalama R, işlem sayısı, winrate — strateji vs al-tut
- Long ve short ayrı
- Stop / BE / TP1 sonrası BE / TP2 ile kapanma oranları, iptal oranı
- Toplam funding maliyeti/geliri
- Coin bazında sonuçlar
- Sermaye eğrisi, drawdown ve R dağılımı grafikleri
