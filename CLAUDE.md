# CLAUDE.md — ASGO.ai

## Proje özeti (10 satır)
1. Binance USDⓈ-M perpetual futures için long/short strateji araştırma sistemi. Repo kökü = proje kökü.
2. Motor: Freqtrade (futures, isolated, **her zaman dry_run: true**). Gerçek emir, işlem yetkili key yok.
3. Her strateji önce `cards/<ad>.md` kartını alır (koşullar + Türkçe açıklama cümleleri), sonra kodlanır.
4. Tüm stratejiler işlem yönetimini `strategies/common/` modülünden alır (giriş bölgesi, stop, 2 TP, BE, kaldıraç).
5. Backtest, dry-run ve gönderilen sinyal aynı kuralları çalıştırır; sinyaldeki her rakam test edilmiş kuralın çıktısıdır.
6. Test hattı: lookahead → ilk backtest → TP model seçimi → doğrulama → dayanıklılık → kasa (bir kez) → dry-run.
7. Sonuçlar R cinsinden, komisyon + kayma + funding dahil, al-tut kıyasıyla `results/` altına rapor olur.
8. Seviyeler: 0 altyapı → 1 sabit liste → 2 dinamik evren → 3 Telegram metin sinyali → 4 görsel sinyal.
9. Proje sahibi yazılımcı değil: ona sade Türkçe yaz; kod, isimler ve kod yorumları İngilizce.
10. Kaynak tarif: `PROJECT_BRIEF.md`. Kurallar: `docs/rules.md`. Eşikler: `docs/metrics.md`.

## Oturum başı
1. Bu dosyayı oku.
2. `docs/roadmap.md`'den mevcut seviyeyi ve sıradaki işi bul.
3. Son 2-3 `journal/` girdisini oku.
4. Üzerinde çalışılacak stratejinin kartını (`cards/`) oku.

## Oturum sonu
1. `journal/YYYY-MM-DD.md` yaz (şablon: `journal/README.md`).
2. Etkilenen strateji kartlarını güncelle.
3. Önemli kararları `docs/decisions.md`'ye ekle (tarih + karar + gerekçe).
4. `docs/roadmap.md`'yi güncelle.
5. Anlamlı bir mesajla commit at.

## Değişmez kurallar (kısa)
- Gerçek emir yok; `dry_run: true` (tek istisna: Binance demo hesabı, `config/demo.json` + `scripts/demo_freqtrade.py`, bkz. `docs/decisions.md` 2026-10-10). Her Freqtrade komutu `scripts/ft.sh` ile (önce `safety_check.py` çalışır).
- Key/token/şifre repoya girmez; `.env` (gitignore'da). `.env.example` boş şablondur.
- Sinyal seviyeleri sadece test edilmiş kurallardan gelir; sonradan yorumla değiştirilmez. TP1 ≥ 1R.
- Başarısız strateji silinmez, `strategies/retired/` + kartında emeklilik gerekçesi.
- Kasa (holdout, son 6 ay) geliştirmede kullanılmaz; "active" öncesi bir kez.
- Her raporda al-tut kıyası; long ve short ayrı raporlanır; funding dahil.
- Sinyal sadece proje sahibinin kişisel Telegram sohbetine ve `.env`'de seçtiği tek gruba gider.
- Seviye atlanmaz. TP ızgarası genişletilmez. Kötü sonuç gizlenmez.

## Pratik notlar
- Bulut ortamında Binance API'si HTTP 451 veriyor (coğrafi engel), `data.binance.vision` açık. Veri: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/download_data.sh`. Freqtrade komutları: `FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh ...` (sabit market listesi, `scripts/offline_freqtrade.py`).
- Tarih sınırları: geliştirme 2020-01-01 → 2024-12-31 (`--timerange 20200101-20250101`), doğrulama 2025-01-01 → 2026-03-31, kasa 2026-04-01 → 2026-09-30 (bkz. `docs/decisions.md`).
- Binance'e hiç erişilemeyen ortamda: `tests/smoke/` altındaki sentetik veri + çevrimdışı Freqtrade ile sadece **boru hattı** testi yapılabilir; bunun sonuçları araştırma sonucu değildir ve `results/`'a konmaz.
- Testler: `python -m pytest -q tests`.
