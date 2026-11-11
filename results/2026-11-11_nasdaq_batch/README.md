# Nasdaq fikir paketi (2 yeni fikir): haber günü yönü, gergin dönemde gün içi momentum

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı ve commit edildi, 2026-11-11)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı; sonradan değiştirilmez. Sonuçlar 2. bölüme eklenir.

**Amaç:** Proje 2026-11-10'da tek piyasaya (Nasdaq / US100, long + short) odaklandı (`docs/nasdaq_plan.md`). Plan en fazla
3 yeni fikre izin veriyor; bu paket ilk ikisi. Üçüncü hak Aslan'dan gelecek somut bir kural için saklı.
Daha önce Nasdaq'ta denenip elenenler tekrar edilmez (liste `docs/nasdaq_plan.md`).

**Veri:** HistData NAS100 (nsxusd) 1 dk → 5 dk mumlar, sadece alış fiyatı, GitHub sunucusunda indirilir
(`research/endeks_forex/fetch.py`, aynı önbellek). Temizlik ve fiyat okuma `research/endeks_forex/batch.py` ile aynı
(`load`, `px`, `px_open`). İndirme 2026-03 ile biter: **kasa (2026-04 → 2026-09) indirilmez, yüklenmez.**

**Dönemler:** geliştirme 2020-01-01 → 2024-12-31, doğrulama 2025-01-01 → 2026-03-31; işlem giriş tarihine göre yazılır.

**Masraf:** gidiş-dönüş %0.010; iki fikir de gün içinde kapanır, gecelik swap yok. Her şey bir de **2 kat masraf** ile.
Stop yok (saatli çıkış), sonuçlar işlem başı **% getiri**. Pozisyon 1x (kasanın tamamı, kaldıraçsız).

**Fiyat kuralı (ileriye bakma yok):** bir T anındaki "fiyat" = T'de biten 5 dk mumun kapanışı. Sinyal T anındaki fiyatla
hesaplanır, giriş **T'de başlayan mumun açılışından** yapılır. Çıkış = New York 16:00'da biten mumun kapanışı.
Gereken mumlardan biri yoksa o gün işlem yok.

### N1 — Haber günü yönü
- **Mantık:** büyük ABD verisi (Fed kararı, enflasyon, istihdam) geldiğinde ilk tepki günün geri kalanında sürer mi?
- **Takvim:** `strategies/common/news_calendar.py` (FOMC 14:00, CPI ve NFP 08:30 New York). Tarihler elle girilmiş,
  resmî takvimle doğrulanmamıştır; yanlış tarih etkiyi sulandırır. 2020-03-15 acil toplantısı (pazar) hariç.
- **CPI / NFP günü:** P0 = 08:25 fiyatı, P1 = 09:35 fiyatı. **FOMC günü:** P0 = 14:00, P1 = 14:30.
- **ANA AYAR:** |P1/P0 − 1| ≥ %0.20 ise P1 yönünde gir (yukarıysa long, aşağıysa short), giriş P1 anında başlayan mumun
  açılışı, çıkış 16:00. Aynı gün iki olay varsa sadece sabahki işlem (aynı anda tek pozisyon).
- **Izgara (sadece bilgi, seçim yapılmaz):** eşik %0 / %0.20 / %0.40; ters yön (ilk tepkiye karşı).
- **Rastgele kontrol:** her gerçek işlem için aynı dönemden, olay günü olmayan rastgele bir iş günü; aynı giriş saati,
  16:00 çıkış, aynı yön. 2000 set; p = (1 + rastgele ortalamanın gerçek ortalamaya eşit/üstünde olduğu set) / 2001.
- **Yargı birimi:** yılda en fazla ~32 olay olduğu için yön başına doğrulamada 30 işlem yapısal olarak çıkmaz. Bu yüzden
  N1 **iki yön birlikte** yargılanır; ek şart: geliştirmede long ve short net ortalaması **ayrı ayrı > 0**.
  Long ve short yine ayrı raporlanır.

### N2 — Gergin dönemde gün içi momentum
- **Mantık:** literatürde bilinen "ilk yarım saat son yarım saati haber verir" etkisi; oynaklığın yüksek olduğu dönemlerde
  daha güçlü olduğu söylenir. Nasdaq'ta ve masraf sonrası tutuyor mu?
- **Seans:** New York 09:30–16:00. Günlük kapanış C = 16:00 fiyatı.
- **Sinyal:** r = (10:00 fiyatı) / (önceki seans günü C) − 1. r > 0 ise long, r < 0 ise short.
- **Rejim (sadece düne kadarki veri):** RV20 = son 20 günlük kapanış-kapanış getirisinin standart sapması (dünle biter).
  "Gergin" = RV20, kendisinin önceki 250 günlük medyanından büyük (medyan da dünle biter). Isınma günlerinde işlem yok.
- **ANA AYAR:** sadece gergin günlerde; 15:30'da başlayan mumun açılışından gir, 16:00'da çık.
- **Izgara (sadece bilgi):** rejim filtresi yok; sadece sakin günler; sinyal = önceki kapanış → 15:30 getirisi.
- **Rastgele kontrol:** her gerçek işlem için aynı dönemden rastgele bir seans günü, aynı yön, aynı 15:30 → 16:00.
- **Yargı birimi:** long ve short **ayrı ayrı**.

### Geçme çıtası (`docs/decisions.md` 2026-11-09; ana ayar, yargı birimi başına, hepsi gerekli)
1. Net ortalama getiri > 0 ve kâr faktörü (PF) ≥ 1.2, hem geliştirmede hem doğrulamada.
2. Geliştirmede rastgele kontrolden iyi: p < 0.05.
3. 2 kat masrafla net ortalama > 0, hem geliştirmede hem doğrulamada.
4. Doğrulamada ≥ 30 işlem (değilse "az örnek", geçmez).
5. 1x pozisyonda en büyük düşüş ≤ %25, hem geliştirmede hem doğrulamada (işlemler çıkış sırasıyla bileşik).

Kazanma oranı sadece bilgi. Al-tut kıyası (NAS100, dönem başı → sonu) raporlanır. Geçen fikir kâğıt takibe alınır,
gerçek emir yok. Kötü sonuç gizlenmez.

Kod: `research/nasdaq_batch/batch.py`. İş akışı: `.github/workflows/nasdaq_batch.yml` (GitHub sunucusunda çalışır,
sonuç CSV'lerini bu klasöre commit'ler).

---

## 2. Sonuçlar (2026-11-11, gerçek veri, GitHub sunucusunda çalıştı)

### GUO'ya not
- İki yeni Nasdaq fikri de **geçmedi**. İkisi de para kaybettirdi veya rastgele girişten ayırt edilemedi.
- Haber günü fikri (ilk tepkinin yönüne gir) açıkça zararlı: işlem başı yaklaşık -%0.24.
- Gün sonu momentum fikri sıfır civarı; masrafı çıkarmıyor.
- Kâğıt takibe yeni bir şey eklenmedi. Elimizdeki tek aday hâlâ Aslan Nasdaq.
- 3 fikir hakkının 2'si kullanıldı. Üçüncüsü Aslan'ın getireceği somut kural için duruyor.

### Ana ayarlar (yargılanan satırlar)

| Fikir | Yön | Geliştirme: işlem / ort. / PF | Doğrulama: işlem / ort. / PF | 2x masraf (gel. / doğ.) | Rastgele kontrol p | Sonuç |
|---|---|---|---|---|---|---|
| N1 haber günü yönü | ikisi | 92 / -%0.237 / 0.64 | 24 / -%0.361 / 0.43 | -%0.247 / -%0.371 | 0.98 | **geçmedi** |
| N1 (bilgi) | long | 52 / -%0.266 / 0.59 | 18 / -%0.323 / 0.51 | | | |
| N1 (bilgi) | short | 40 / -%0.199 / 0.70 | 6 / -%0.477 / 0.13 | | | |
| N2 gergin dönem momentum | long | 135 / +%0.023 / 1.19 | 70 / -%0.031 / 0.70 | +%0.013 / -%0.041 | 0.26 | **geçmedi** |
| N2 gergin dönem momentum | short | 152 / -%0.027 / 0.84 | 78 / +%0.022 / 1.23 | -%0.037 / +%0.012 | 0.59 | **geçmedi** |

Al-tut (NAS100): geliştirme +%137 (düşüş %36), doğrulama +%13 (düşüş %22).
En büyük düşüş hiçbir satırda sınırı (%25) aşmadı (N1 geliştirme %24.4); elenme sebebi düşüş değil, getirinin eksi olması.

### Ne gördük
- **N1:** haber sonrası ilk tepkiyi takip etmek her eşikte (%0 / %0.20 / %0.40), iki dönemde de eksi. Rastgele günlerde aynı
  saatte aynı yöne girmek daha iyi sonuç verdi (p 0.98). Türüne göre: CPI/NFP sabahları 98 işlem, ortalama -%0.33;
  FOMC 18 işlem, ortalama +%0.10 (çok az örnek).
- **N2:** long geliştirmede hafif artı, doğrulamada eksi; short tam tersi. Yani tutarlı bir etki yok. Rejim filtresi
  olmadan ve sakin günlerde de aynı tablo.
- N2'de 2020 ve 2023'te işlem yok: 2020 ısınma dönemi (270 gün veri gerekir), 2023 kurala göre "sakin" yıl.

### Dikkat: ters yön (ilk tepkiye karşı işlem) artı göründü, ama bu bir sonuç DEĞİL
Bilgi ızgarasında N1'in tersi (ilk tepkinin aksine gir) her hücrede artı: eşik %0.20'de geliştirme +%0.217 / PF 1.50
(92 işlem), doğrulama +%0.341 / PF 2.24 (24 işlem). Bu, ana ayarın aynadaki görüntüsüdür (eksi masraf); ön kayıtta
"ızgara sadece bilgi, seçim yapılmaz" yazıyor. Sonucu gördükten sonra yön çevirip "geçti" demek kendimizi kandırmaktır.
Ayrıca doğrulamada 24 işlem var (çıta 30) ve haber takvimi resmî kaynakla doğrulanmadı.
Bu yüzden: **aday değil, sadece not.** Denenmek istenirse yeni bir ön kayıt, doğrulanmış takvim ve henüz görülmemiş
veri (kasa dönemi veya ileriye dönük kâğıt takip) gerekir; ve bu, planın 3 fikir hakkından birini harcar.

Dosyalar: `summary.csv` (tüm hücreler), `pass.csv` (çıta kontrolü), `yearly.csv`, `trades_primary.csv`, `buy_hold.csv`, `run_log.txt`.
