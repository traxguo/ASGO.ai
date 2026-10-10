# 2026-10-10 — Pusula kağıt takip başladı, Kalabalık yan stratejisi

## Ne yapıldı
- Pusula kasa testi: -0.02R (15 işlem), kıl payı geçemedi. Proje sahibi "ikisi birden" dedi: kağıt takip + yan strateji araştırması.
- `PusulaTrendLong` donduruldu. `research/forward/pusula_paper.py` 2026-10-01'den itibaren yeni veriyle aynı kuralları çalıştırıyor; `fetch_binance_vision.py --current-month` içinde bulunulan ayı günlük arşivlerden ekliyor. İlk hafta: 3 işlem, üçü stop, -3.14R.
- Haftalık kontrol: her pazartesi 09:47 (İstanbul).
- Kalabalık (funding tersine): kurallar test öncesi kartta sabitlendi. Geliştirme +0.28R (123 işlem, DD %9.3), doğrulama +0.29R (26 işlem), kasa +0.05R (13 işlem). Dayanıklılık: komşular artıda, masraf x2 +0.23R, hile testi temiz.

## Öğrenilen
- 2026-04..09 döneminde iki farklı fikir (trend takibi ve kalabalığın tersi) de başa baş. Bu dönem yatay/kararsız bir piyasa.
- Kalabalık'ın short tarafı hep zayıf; kâr long tarafından ve birkaç büyük TP2'den geliyor.
- Sıra hatası: Kalabalık'ın kasa testi dayanıklılık testlerinden önce koşuldu.

## Sıradaki
- Pazartesi kağıt takip raporu. Kalabalık için aylık kağıt takip (funding arşivi ay sonunda).
- Güçlü/zayıf coin sepeti fikri (önce kart).

## Öğleden sonra: yeni coinler ve arka plan turları
- Proje sahibi: "backtest arkada hep devam edecek", "sürekli müdahale ile geliştirelim". Her 6 saatte bir geliştirme turu (routine) ve kuyruk dosyası `research/queue/pusula_kuyruk.md` kuruldu. Kabul şartı: hem eski 16 hem yeni 20 coinde daha iyi.
- 20 yeni coin (`config/pairs_new20.json`): PusulaTrendLong +0.44R, PusulaTrend +0.27R (short +0.12R).
- Tur 1, `PusulaTrendRS` (short sadece BTC'den zayıf coinde): red.
