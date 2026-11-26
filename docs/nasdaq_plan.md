# Nasdaq planı (2026-11-10)

## GUO'ya not
- Proje tek piyasaya iniyor: **Nasdaq (US100)**. Long da short da açabilir, ama short zorla açılmaz.
- Hedef "çok kâr" değil, **genelde artı kapatmak**.
- Kripto demo botları durdu. Kripto kâğıt takipleri 30 Kasım'a kadar dokunulmadan çalışır, yeni kripto fikri yok.
- İşlemler XM'de açılacak. Bot sinyali Telegram'a yazar, işlemi ilk aşamada sen elle açarsın.
- Hüküm takvimle değil, **30 canlı işlemle** verilir.

## Elimizdeki aday
- **Aslan Nasdaq (donuk kural)**: geliştirme +0.07R (368 işlem), doğrulama +0.15R (107), kasa +0.15R (46). Short: -0.13R / +0.25R / +0.24R.
  Aynı kural S&P, DAX, FTSE ve Nikkei'de tutmadı, yani kısmen şans olabilir. Kanıt değil, aday.
- Yanında iki gevşek versiyon (GEVŞEK 1: yön filtresi yok, GEVŞEK 2: aynı anda 2 işlem) kâğıt takipte.
- Kâğıt takip: `forward/paper_aslan_nas*`, 2026-11-05'ten beri. İlk değerlendirme 2026-11-30, sonra ayda bir.

## Yeni fikirden önce yapılacaklar (sırayla)
1. **Saat.** Kâğıt takip her saat zamanında çalışmalı (Cloudflare saati; bkz. journal 2026-11-10).
2. **XM koşulları.** US100 için gerçek spread, gecelik swap, en küçük lot ve işlem saatleri XM demo hesabından ölçülür.
   Testlerdeki masraf varsayımı (gidiş-dönüş %0.01) buna göre doğrulanır veya düzeltilir.
3. **Fiyat farkı.** Kâğıt takip Yahoo NQ=F (vadeli) fiyatını kullanıyor, XM US100 nakit CFD. Seviyeler XM fiyatına
   çevrilerek gönderilmeli; fark ölçülür.
4. **Sinyal mesajı.** Giriş, stop, hedef ve Türkçe gerekçe; hepsi test edilmiş kuralın çıktısı (CLAUDE.md kuralı).

## Yeni fikirler: en fazla 3
Kurallar testten **önce** yazılır ve commit edilir. Çıta: `docs/decisions.md` 2026-11-09 (net > 0 ve PF ≥ 1.2 iki dönemde,
rastgele giriş kontrolü p < 0.05, 2x masrafta artı, doğrulamada ≥ 30 işlem, düşüş ≤ %25). Long ve short ayrı raporlanır.

**Nasdaq'ta daha önce denenip elenenler (tekrar edilmez):** açılış aralığı kırılımı, limit ile ters işlem, RSI(2) (5 dk ve
günlük), Donchian / EMA kesişimi / 4s geri çekilme trendi, gece kayması, ay dönümü, açılış boşluğu doldurma, üst üste 3 gün,
Londra kırılımı, haber sonrası ilk tepkiyi takip, ilk yarım saat → son yarım saat momentumu, 5 dk saf yapı kırılımı (Aslan 5 dk), Aslan kuralının diğer endeksleri ve birleşik gevşetmesi.

**Henüz denenmemiş, Nasdaq'a özgü bir sebebi olan alanlar (öneri; GUO/Aslan onayından sonra ön kayıt yazılır):**
1. Büyük haber günleri (Fed kararı, enflasyon, istihdam): haber sonrası ilk yönün devamı veya dönüşü. Takvim: `strategies/common/news_calendar.py`.
2. Oynaklık rejimi: sakin ve gergin dönemlerde ayrı davranış (ör. sadece gergin dönemde short'a izin).
3. Aslan'ın getireceği tek somut kural.

**Durum (2026-11-11):** 1 ve 2 test edildi, ikisi de geçmedi (`results/2026-11-11_nasdaq_batch/README.md`). Kalan tek hak 3. madde.
**Durum (2026-11-19):** 3. madde (Aslan'ın 5 dk kuralı) test edildi, geçmedi (`results/2026-11-19_aslan_5dk/README.md`). Üç hak bitti. Proje sahibi 4. bir hak açtı (Aslan sıkışma kırılımı): o da geçmedi (`results/2026-11-19_aslan_sikisma/README.md`). 5. ve son hak (Aslan bant kırılımı) da geçmedi (`results/2026-11-19_aslan_bant/README.md`). Yeni fikir hakkı yok.
**Durum (2026-11-21):** Proje sahibi yöntemi değiştirdi: kural tahmin etmek yerine önce ölçüm. 5 dk "harita" 400 hücrede aday bulmadı (`results/2026-11-21_nasdaq_harita/README.md`). 2026-11-26: öğrenen model, FVG ızgarası (288 çeşit) ve uyum puanı da geçmedi (`results/2026-11-26_nasdaq_*`).
Adım 2 (XM koşulları) ertelendi: demo hesap açılamadı; ölçüm gerçek para kararından hemen önce yapılır. Adım 3 (fiyat farkı) tamam:
grafik ve Telegram seviyeleri US100 (nakit) karşılığıyla gösterir.

Üç fikir de elenirse dördüncüsü aranmaz; Aslan Nasdaq hattının canlı sonucu beklenir.

## Sonra
Nasdaq hattı 30 canlı işlemde artıysa ve düşüş test sınırındaysa: küçük gerçek para kararı (GUO'nun ayrı onayı). Başka
piyasa ancak ondan sonra eklenir.
