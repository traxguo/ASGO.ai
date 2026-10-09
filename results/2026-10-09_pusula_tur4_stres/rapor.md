# Pusula 4. tur — stres testleri — 2026-10-09

## GUO'ya not
- **Durum: iyi gidiyoruz.** Stratejiyi zorlaştıran 6 farklı testin hepsinde hâlâ kârda.
- En iyi 3 coini çıkarsak da, işleme 4 saat geç girsek de, masraf iki katına çıksa da, 1 saatlik grafikte kullansak da kârlı.
- **Bulunan açık:** 2024 Mart - 2025 Temmuz arasında 26 işlem üst üste zararla kapandı. Kasa en fazla %26 eridi. Bu stratejide uzun kayıp dönemleri olacak, sabır gerekecek.
- Bu açığı kapatmak için bir deneme yaptım, fark çok küçük çıktı. Gereksiz karmaşa olmasın diye eklemedim.

## Ayarlar
- `PusulaTrendLong` (ana sürüm), en fazla 3 açık işlem, 4h + 1h detay, 2020-01-01 → 2026-03-31 (kasa dönemi dahil değil).
- 16 coin: `config/pairs_wide16.json`. Maliyet %0.1/emir + funding (aksi yazmıyorsa).
- Bu dönemin tamamı daha önce görüldü (geliştirme + doğrulama + yeni coin testleri). Bu yüzden buradaki testler "kural seçmek" için değil, "bozuluyor mu" diye bakmak için.

## Sonuçlar
| Test | İşlem | Ortalama R | Net getiri | Max DD |
|---|---|---|---|---|
| Ana sürüm (16 coin) | 195 | +1.02 | +%387 | %26.1 |
| Maliyet x2 | 195 | — | +%351 | %28.3 |
| Her sinyal 1 mum (4 saat) geç | 198 | — | +%688 | %20.9 |
| BTC çıkarılırsa | 188 | +0.93 | +%298 | %30.3 |
| ETC çıkarılırsa | 197 | +0.73 | +%227 | %26.1 |
| BNB çıkarılırsa | 174 | +1.03 | +%330 | %21.6 |
| BTC + ETC + BNB (en kârlı 3 coin) çıkarılırsa | 170 | +0.50 | +%104 | %25.5 |
| Aynı kurallar 1h grafikte (`PusulaTrendLong1h`) | 378 | +0.80 | +%759 | %28.1 |
| BTC de güçlü yükselişte olmalı (`PusulaTrendLongStrictBTC`) | 179 | +1.10 | +%388 | %23.4 |

`PusulaTrendLongStrictBTC` 6 coinde +0.81R (ana +0.74R), yeni 10 coinde +1.12R ama DD %17.3 (ana %15.1). Toplam R neredeyse aynı, DD bir listede iyi bir listede kötü.

## Yorum
- Strateji tek bir coine, giriş zamanlamasına, masrafa veya zaman dilimine bağlı değil. "Güçlü trendde kırılımı al, trend bozulunca çık" fikri farklı koşullarda da çalışıyor.
- Geç giriş testinin daha iyi çıkması "geç girmek daha iyi" demek değil: büyük kazançlar birkaç işleme bağlı olduğu için küçük değişiklikler sonucu çok oynatıyor. Önemli olan bozulmaması.
- En büyük zayıflık uzun kayıp serileri: 16 coinde 26 kayıp üst üste (2024-03 → 2025-07). Trend zirve yaptıktan sonra günlük rejim haftalarca "yükseliş" kalıyor ve kırılımlar başarısız oluyor.
- BTC şartını sıkılaştırmak bu seriyi belirgin şekilde düzeltmedi.

## Karar
- Ana sürüm değişmedi. `PusulaTrendLongLate`, `PusulaTrendLong1h`, `PusulaTrendLongStrictBTC` sadece stres testi, aday değil.
- Kasa sınavından önce bilinmesi gereken: canlıda 20+ kayıp serisi normal kabul edilmeli; kill switch eşiği buna göre konmalı.
