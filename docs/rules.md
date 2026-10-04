# Kurallar

Bu kurallar PROJECT_BRIEF.md'den alınmıştır ve değişmez. Değiştirmek için proje sahibinin açık kararı gerekir; değişiklik `decisions.md`'ye yazılır.

## Değişmez kurallar
1. **Gerçek emir yok.** Freqtrade her zaman `dry_run: true` ile çalışır. `scripts/safety_check.py` her Freqtrade komutundan önce çalışır (`scripts/ft.sh`) ve aksi durumda durdurur.
2. **İşlem yetkili API key yok.** Veri herkese açık kaynaklardan gelir. Telegram token gibi değerler sadece `.env` içinde durur; `.env` repoya asla girmez.
3. **Sinyaldeki her rakam test edilmiş kuralların çıktısıdır.** Giriş bölgesi, stop, TP'ler, kısmi çıkış ve break even kuralları stratejinin kodunda tanımlıdır ve backtest'te birebir aynı simüle edilir.
4. **Dürüstlük.** Başarısız stratejiler silinmez; `strategies/retired/` altına gerekçesiyle taşınır.
5. **Kasa verisine dokunma.** Son 6 ay (holdout) geliştirme sırasında kullanılmaz; "active" olmadan önce tek seferlik son test içindir.
6. **Al-tut kıyası zorunlu.** Her rapor stratejiyi aynı dönemde coin(ler)i al-tut ile kıyaslar.
7. **Sinyaller sadece proje sahibine gider.** Telegram botu yalnızca proje sahibinin kişisel sohbet ID'sine mesaj atar.

## Risk kuralları (simülasyonda da geçerli)
- Her stratejide stop zorunlu.
- İşlem başına sermayenin %1'i riske edilir; pozisyon büyüklüğü stop mesafesine göre hesaplanır.
- İzole marjin, en fazla 3x kaldıraç. Likidasyon fiyatı stop mesafesinin en az 2 katı uzakta olmalı; değilse kaldıraç düşer ya da sinyal üretilmez.
- Aynı anda açık işlem sayısı sınırlı (`max_open_trades`); aynı coinde aynı anda hem long hem short yok.
- **Kill switch:** Dry-run'da drawdown eşiği aşılırsa strateji durur, sinyal kesilir, günlüğe yazılır, proje sahibine bildirim gider.

## Maliyet modeli (bilerek kötümser)
- Komisyon: her giriş ve çıkış emri için taker %0.05 (kısmi çıkışlar ayrı emir sayılır).
- Kayma: ek %0.05. Toplam emir başına %0.1 (`config/base.json` → `fee: 0.001`).
- Funding: pozisyon açıkken geçmiş funding verisinden hesaplanır.
- Aynı test maliyet x2 ile de çalıştırılır (`--fee 0.002`). Maliyet ikiye katlanınca kârsız olan strateji kırılgandır.

## Yapılmayacaklar
- Gerçek emir göndermek veya `dry_run: false`
- Key, token, şifre veya kişisel bilgiyi repoya koymak
- Kasa verisini geliştirmede kullanmak
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
