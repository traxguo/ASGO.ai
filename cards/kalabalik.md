# kalabalik — Kalabalık tarafa karşı işlem (funding aşırılığı + dönüş)

Kod: [`strategies/candidates/kalabalik.py`](../strategies/candidates/kalabalik.py)

## Hipotez
Funding oranı, kaldıraçlı long'ların mı short'ların mı daha kalabalık olduğunu gösterir. Herkes aynı tarafa yığıldığında (funding kendi son bir yılına göre aşırı) fiyat ters yöne dönmeye başlarsa, kalabalık taraf pozisyon kapatmak zorunda kalır ve hareket hızlanır. Pusula'nın yapamadığı short tarafını ve yatay/tepe dönemlerini hedefler. Pusula trend takip eder; bu strateji kalabalığın tersine işlem açar.

## Yön
ikisi de

## Giriş koşulları (4h, test öncesi sabitlendi, 2026-10-10)
Funding: son 3 funding ödemesinin ortalaması (24 saat), 4h mumun açılış zamanından önce ilan edilmiş olanlar.
Short (hepsi):
- [crowded_long] Teknik: 24 saatlik ortalama funding, önceki 365 günün değerlerinin en üst %5'inde ve > 0 | Açıklama: "Long tarafı çok kalabalık: funding %{funding_24h} (son bir yılın en yüksek %5'i)."
- [turn_down] Teknik: 4h kapanış önceki 10 mumun dibinin altında, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 10 mumun dibini ({low10}) kırdı, dönüş başladı."

Long (hepsi):
- [crowded_short] Teknik: 24 saatlik ortalama funding, önceki 365 günün en alt %5'inde | Açıklama: "Short tarafı çok kalabalık: funding %{funding_24h} (son bir yılın en düşük %5'i)."
- [turn_up] Teknik: 4h kapanış önceki 10 mumun tepesinin üstünde, serinin ilk mumu | Açıklama: "Fiyat ({close}) son 10 mumun tepesini ({high10}) kırdı, dönüş başladı."

## İşlem yönetimi
Ortak modül, değişiklik yok: giriş bölgesi 0.25 ATR, stop 1.5 ATR veya son 10 mumun dip/tepesi (uzak olan), Model B (TP1 2R'de yarısı + BE, TP2 4R), 3 mum geçerlilik, en fazla 3x, işlem başı %1 risk. Kalabalık tersine işlemler kısa sürer; sabit hedef buna uygun.

## Zaman dilimi ve parametreler
| Parametre | Değer | Makul aralık |
|---|---|---|
| Zaman dilimi | 4h | sabit |
| Funding ortalaması | son 3 ödeme (24 saat) | 1-6 ödeme |
| Aşırılık eşiği | son 365 günün %5 / %95'i | %2-10 |
| Dönüş kanalı | 10 mum | 6-20 |

## Test planı (önceden)
- 16 coin (`config/pairs_wide16.json`), en fazla 3 işlem, 4h + 1h detay.
- Geliştirme 2020-01 → 2024-12. Geçerse (> 0R, DD ≤ %25, ≥ 100 işlem) doğrulama 2025-01 → 2026-03 bir kez.
- Tek varyant: `Kalabalik_B`. Long ve short ayrı raporlanır; asıl merak edilen short tarafı.
- Not: funding verisi araştırma için doğrudan feather dosyasından okunuyor; canlıda başka kaynak gerekecek.

## Durum: candidate

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-10 | Geliştirme 2020-2024, 16 coin, max 3 | 123 işlem, +0.28R, PF 1.46, DD %9.3. Long +0.38R (78), short +0.09R (45). En iyi 10 işlem çıkınca +3.1R. Bootstrap P(ort ≤ 0) %3. **Eşikleri geçti.** | `results/2026-10-10_kalabalik_ilk_backtest_gelistirme/rapor.md` |
| 2026-10-10 | Doğrulama 2025-01 → 2026-03 (bir kez) | 26 işlem (hepsi long), +0.29R, PF 1.54, DD %3.2. Al-tut -%46. Örnek küçük: bootstrap P(ort ≤ 0) %15. | `results/2026-10-10_kalabalik_dogrulama/rapor.md` |
| 2026-10-10 | Kasa 2026-04 → 2026-09 (bir kez) | 13 işlem, +0.05R, DD %4.1, net +%0.5. Long +0.18R (10), short -0.38R (3). Al-tut +%17. Eşiği (> 0R) kâğıt üstünde geçti ama sonuç başa baş, örnek çok küçük. | `results/2026-10-10_kalabalik_kasa/rapor.md` |
| 2026-10-10 | Dayanıklılık (geliştirme) | ±%20 komşuların 6'sı da artıda (+0.11..+0.25R), masraf x2 +0.23R, hile testi temiz, 11/16 coin artıda. | `results/2026-10-10_kalabalik_dayaniklilik/parametre_komsulari.md` |

## Notlar / öğrenilenler
- İlk 1 yıl funding geçmişi birikirken işlem yok; geliştirmede ilk işlem 2021'de.
- Doğrulamada hiç short yok: 2025'te funding, önceki 365 günün en üst %5'ine hiç çıkmadı (2024'teki aşırı funding eşiği yükseltti).
- Kâr birkaç büyük TP2'ye bağlı (geliştirmede en iyi 10 işlem +31R / toplam +34R). Yıl bazında 2022 long'ları eksi (yaklaşık -3R), kârın çoğu 2023-2024.
- Sıra hatası: kasa testi dayanıklılık testlerinden önce koşuldu. Dayanıklılık sonuçları kasa sonucunu bilmeden değerlendirilemezdi ama kurallar hiçbir aşamada değişmedi.
- Kağıt takip: içinde bulunulan ayın funding verisi Binance arşivinde ay bitmeden yayınlanmıyor, bu yüzden Kalabalık ancak ay sonunda güncellenebilir.
- Pusula'dan farklı bir kaynaktan besleniyor (kalabalığın tersine dönüş, trend değil); ikisini birlikte çalıştırma ileride ayrıca test edilebilir.

## Emeklilik gerekçesi (varsa)
