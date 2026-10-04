# Stratejiler (kod)

| Klasör | Anlamı |
|---|---|
| `common/` | **Ortak işlem yönetimi.** Giriş bölgesi, stop, TP1/TP2, kısmi çıkış, break even, kaldıraç ve pozisyon büyüklüğü kuralları burada, tek yerde. Tüm stratejiler bunu kullanır; böylece backtest, dry-run ve Telegram mesajı aynı rakamları üretir. |
| `candidates/` | Test edilen stratejiler. |
| `active/` | Test hattını geçmiş, sinyal üretmesine izin verilen stratejiler. |
| `retired/` | Elenen stratejiler. Silinmez; neden elendiği kartında yazılı. |

Her stratejinin Türkçe açıklaması `cards/` klasöründeki kartındadır. Koddaki koşul isimleri (`trend_up` gibi) kartla birebir aynıdır.

`common/` içindeki dosyalar:
- `trade_management.py` — kuralların kendisi (Freqtrade'den bağımsız, testli: `tests/test_trade_management.py`)
- `freqtrade_mixin.py` — bu kuralları Freqtrade'e bağlayan ortak strateji sınıfı (`ManagedStrategy`)
