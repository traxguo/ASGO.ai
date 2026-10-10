# aslan_liquidity — ilk backtest (geliştirme verisi) — 2026-10-08

Strateji kartı: [cards/aslan_liquidity.md](../../cards/aslan_liquidity.md)

## Kısa sonuç
Strateji, kurallar karttaki haliyle, **geliştirme verisinde (2020-01 → 2024-12) para kaybettirdi**. Hiçbir giriş grafiğinde, hiçbir coinde, hiçbir yılda ve ne long ne short tarafında artı sonuç yok. Test hattının 2. aşamasında (ilk backtest) elendi. Doğrulama verisi ve kasa (son 6 ay) **kullanılmadı**, düzeltilmiş bir versiyon için temiz duruyor.

| Test | İşlem | Ortalama R (maliyet dahil) | Maliyet hariç R | Winrate | Profit factor | Rapor |
|---|---|---|---|---|---|---|
| 1 saatlik giriş, %1 risk | 2266 | **-0.21R** | -0.05R | %30.6 | 0.72 | [1h/rapor.md](1h/rapor.md) |
| 1 saatlik giriş, haber filtresi yok | 2302 | -0.21R | -0.04R | %30.7 | 0.71 | [1h/rapor.md](1h/rapor.md) |
| 15 dakikalık giriş, %1 risk | 3143 | **-0.28R** | -0.01R | %31.7 | 0.63 | [15m/rapor.md](15m/rapor.md) |
| 1 saatlik giriş, %3 risk (Aslan'ın riski) | 1369 | -0.22R | -0.07R | %30.0 | 0.62 | [1h_risk3/rapor.md](1h_risk3/rapor.md) |

Eşikler (`docs/metrics.md`): ortalama R > 0, profit factor ≥ 1.2, max drawdown ≤ %25. Hiçbiri sağlanmadı.

**%3 risk notu:** Aslan'ın %3 riskiyle test hesabı 2023 başında sıfırlandı (-%100); bu yüzden 2023-2024 işlemleri açılamadı. Bütün dönemi ölçebilmek için asıl rakamlar %1 riskle alındı (kurallar aynı, sadece pozisyon küçük). R sonuçları riskten bağımsızdır.

## Neden kaybediyor (rakamlarla)
1. **Kenar (edge) yok:** 2R hedefle başa baş için ~%33 kazanma oranı gerekir. Sinyaller %30-32 kazanıyor. Komisyon ve kayma hiç olmasa bile sonuç yaklaşık 0R (1h: -0.05R, 15m: -0.01R). Yani giriş kuralı rastgele bir girişten belirgin şekilde iyi değil.
2. **Dar stoplar maliyeti büyütüyor:** Stop iğnenin ucunda olduğu için çok yakın (1h'de ortanca %1.8, 15m'de %1.1). Her işlem giriş + çıkışta toplam ~%0.2 maliyet ödüyor; stop %0.6 ise bu tek başına 0.33R demek. En dar stoplu çeyrek: 1h -0.44R, 15m -0.66R.
3. **MSS ve iFVG ikisi de eksi:** 1h'de iFVG -0.20R (1893 işlem), MSS -0.29R (373 işlem). 15m'de iFVG -0.29R, MSS -0.20R.
4. **Haber filtresi neredeyse hiçbir şey değiştirmedi** (-0.21R ile -0.21R). Sadece işlemlerin ~%1.5'ini eliyor.
5. **Coin ve yıl:** 5 coinin 5'i de eksi (-0.15R ile -0.26R arası), 2020-2024'ün her yılı eksi.

## Önemli uyarı
Bu sonuç, Aslan'ın stratejisinin **bizim karta yazdığımız kurallarla** test edilmiş halidir. Kartta "varsayımlar" bölümünde 6 madde var (likidite seviyesi, günlük yön, MSS tanımı, iFVG tanımı, fitil kuralı, haber listesi). Aslan'ın gerçekte yaptığı bunlardan farklıysa sonuç da farklı olabilir. Aslan'ın grafikte gözle yaptığı seçim ("önemli" likidite, "net" MSS) bilgisayarın her seviyeyi saymasından daha seçici olabilir.

## Sınırlar
- Haber takvimi çevrimdışı hazırlandı (ForexFactory'ye erişilemedi); filtre zaten sonucu değiştirmediği için etkisi küçük.
- Stop ve hedef aynı mumdaysa stop önce sayıldı (kötümser). 15m'de bu nadir.
- Maliyet: emir başına %0.1 (komisyon %0.05 + kayma %0.05), funding dahil.
