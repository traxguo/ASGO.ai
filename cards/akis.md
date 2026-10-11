# akis — kalabalığa karşı 4 saatlik işlemler (açık pozisyon, long/short oranı, alıcı-satıcı akışı)

Kod: henüz Freqtrade stratejisi yok; araştırma `research/scans/oi_flow_scan.py`, canlı veri toplama `research/live/collect_bitget_metrics.py`.

## Hipotez
Kısa vadede fiyat grafiği tek başına masrafı aşan avantaj vermedi (scalp denemelerinin hepsi). Vadeli işlem piyasasının kendi verisi ise kalabalığın nerede yığıldığını gösterir: küçük yatırımcıların çoğu long'dayken ve satıcılar baskınken fiyat sonraki saatlerde düşme eğiliminde; sert yükselişe yeni para (açık pozisyon artışı) eşlik ediyor ve kalabalık henüz long'a yığılmamışsa yükseliş birkaç saat sürüyor.

## Yön
ikisi de (long ve short ayrı raporlanır)

## Giriş koşulları (1h kapanmış mum, eşikler 2022-2024 Binance verisinden, 2026-10-11 sabitlendi)
Short (hepsi):
- [sellers_dominate] Teknik: son 4 saatin ortalama taker alış/satış hacim oranı ≤ 0.975 | Açıklama: "Son 4 saatte satıcılar baskın."
- [crowd_long] Teknik: genel hesap long/short oranının 30 günlük z-skoru ≥ 1.15 | Açıklama: "Küçük yatırımcıların çoğu long'da, kalabalık bir tarafa yığılmış."
Long (hepsi):
- [surge] Teknik: 4 saatlik getiri ≥ %2.3 | Açıklama: "Fiyat son 4 saatte sert yükseldi."
- [new_money] Teknik: açık pozisyon 4 saatte ≥ %1.9 arttı | Açıklama: "Yükselişe yeni para giriyor."
- [crowd_not_long] Teknik: long/short z-skoru < 1.15 | Açıklama: "Kalabalık henüz long'a yığılmadı."

## İşlem yönetimi
- Giriş: sinyal mumundan sonraki açılış (araştırmada). Canlıda limit emir hedefleniyor (masraf belirleyici).
- Stop: 1.5 ATR(14, 1h). Hedef yok; 4 saat sonra kapanır. Coin başına aynı anda 1 işlem.
- Not: TP yok, TP1 ≥ 1R kuralından sapar; "active" öncesi sahip onayı gerekir.

## Zaman dilimi ve parametreler
1h; 12 coin (BTC ETH SOL XRP BNB DOGE ADA LINK AVAX LTC DOT TRX).

## Durum: retired (2026-10-11)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-10-11 | Binance metrics, basit simülasyon (sonraki açılış, 1.5 ATR stop, 4 saat) | Dev 2022-2024: 3542 işlem günde 4.9, +0.11R (%0.05 masrafla +0.17R). Doğrulama 2025-01 → 2026-03: 2047 işlem, +0.13R (eşik seçiminde görüldü). Kasa 2026-04 → 09 (bir kez): 460 işlem günde 2.5, +0.02R (%0.05 masrafla +0.10R). | `journal/2026-10-11.md` |

## Notlar / öğrenilenler
- Avantaj ince; masraf %0.1/emirden %0.05'e inince kasa dönemi +0.02R → +0.10R. Limit emir şart.
- Bitget'in long/short oranı Binance'tekinden farklı seviyede (ör. SOL ~4.8); z-skor bu yüzden kullanılıyor ama eşiklerin Bitget'te aynı davrandığı henüz doğrulanmadı.

## Emeklilik gerekçesi (varsa)
2026-10-11: İlk taramada bir zaman hatası vardı: saatlik açık pozisyon, long/short ve alıcı-satıcı verisi bir saat erkene kaydırılmıştı, yani her sinyal ~55 dakika sonrasını görüyordu. Hata, Binance metrics alıcı/satıcı oranının 5 dakikalık mumla birebir aynı olduğu (bir mum kayık) kontrol edilirken bulundu. Düzeltilince: geliştirme -0.08R, doğrulama -0.09R, kasa dönemi -0.22R (normal masraf); düşük masrafta da eksi. Avantaj yok. Toplama ve kağıt takip işleri kaldırıldı (PR'a girmeden).
