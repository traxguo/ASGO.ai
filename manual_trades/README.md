# Elle işlem kaydı

Sinyallere göre kendi hesabında elle işlem yaparsan buraya kaydedilir (`trades.csv`). Haftalık raporda sistemin sanal sonucu ile senin gerçek sonuçların karşılaştırılır (gecikme, atlanan sinyal, erken çıkış etkisi).

Sütunlar: `signal_id`, giriş zamanı/fiyatı, çıkış 1 ve çıkış 2 (zaman/fiyat/yüzde), kaldıraç, notlar. Kayıt komutu (`scripts/log_trade.py`) Seviye 3'te eklenecek.
