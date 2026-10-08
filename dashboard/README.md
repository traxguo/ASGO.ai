# ASGO TAKİP

`asgo_takip.html`: araştırmanın durumunu tek sayfada gösterir (seviye, test hattı, denenen stratejiler, başarı rakamları, öğrenilenler, son notlar ve kararlar).

- Dosyayı tarayıcıda açman yeterli (çift tıkla).
- Sayfa elle yazılmaz; `python scripts/build_dashboard.py` komutu repodaki dosyalardan yeniden üretir. Yeni bir test veya günlük eklenince bu komut tekrar çalıştırılır.
- Henüz canlı işlem yok; "Son işlemler" bölümü backtest (geçmiş veri testi) bilgisini gösterir. Bir rapor klasörüne `islemler.csv` eklenirse işlemler tek tek listelenir.
