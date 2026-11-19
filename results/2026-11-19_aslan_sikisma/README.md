# Aslan sıkışma kırılımı (Nasdaq, 4. ve son fikir hakkı)

## 1. Ön kayıt (getiriler hesaplanmadan ÖNCE yazıldı ve commit edildi, 2026-11-19)

Bu bölüm hiçbir getiri hesaplanmadan önce yazıldı; sonradan değiştirilmez. Sonuçlar 2. bölüme eklenir.

**Neden 4. hak:** planın 3 hakkı bitti (`docs/nasdaq_plan.md`). Aslan 5 dk kuralı (`results/2026-11-19_aslan_5dk`)
geçmedikten sonra Aslan, asıl aradığı kurulumun **sıkışma bölgesinden kırılım** olduğunu söyledi (testteki kural her
yerde giriş arıyordu). Proje sahibi bunu tek seferlik test etmeye karar verdi (karar kartı, 2026-11-19 17:50 UTC:
"Yaptır"). **Bu ailenin son testidir: geçmezse Aslan kurallarının kodlanmış testi kapanır.**

**Uyarı (dürüstlük):** fikir, bir önceki testin sonucu görüldükten sonra geldi. Aynı geliştirme + doğrulama verisi
üçüncü kez kullanılıyor. Bu yüzden geçse bile kâğıt takipte 30 işlem görülmeden aday sayılmaz.

**Veri, dönemler, masraf, rastgele kontrol, R hesabı, düşüş:** `results/2026-11-19_aslan_5dk/README.md` ile aynı
(HistData NAS100 5 dk, kasa yok; gel. 2020-01 → 2024-12, doğ. 2025-01 → 2026-03; gidiş-dönüş %0.010 + gecelik
finansman; 2x masraf; 2000 setlik rastgele giriş kontrolü; işlem başı %1 risk ile düşüş).

### Kural (long; short tam simetrik)
1. **Sıkışma:** bir B mumundan önceki son N mum (N en az 12, en çok 48; koşulu sağlayan en uzun N alınır) için
   bant tepesi = en yüksek iğne, bant dibi = en düşük iğne, genişlik ≤ fiyatın %0.22'si (~60 puan). Banda dokunuş:
   tepesi bant tepesinin genişliğin %15'i kadar yakınında olan mumlar ve dibi bant dibine o kadar yakın olan mumlar;
   tepeye en az 2, dibe en az 2 dokunuş, aynı tarafın iki dokunuşu arasında en az 2 mum. (Aslan: "12 mum ideal, daha
   fazla da olabilir"; genişlik ve dokunuş sayısı varsayılan, Aslan söylemedi.)
2. **Kırılım:** B mumu bant tepesinin **üstünde kapatır** (bant B'den önceki mumlardan hesaplanır).
3. **Geri çekilme + iFVG:** B'den sonraki en fazla 24 mum (2 saat) içinde: B'den sonra oluşmuş bir **düşüş FVG'si**
   (5 dk veya 15 dk) bir mum tarafından üst kenarının üstünde kapanarak **iFVG** olur. 15 dk mumlar UTC çeyrek saat
   bloklarından, kapanmış olanlar kullanılır.
4. **MSP ve giriş:** iFVG oluştuktan sonra (veya aynı mumda), bir k mumu B'den sonra oluşmuş son onaylı 5 dk tepenin
   (2/2 salınım) **üstünde kapatır**. Giriş k mumunun kapanışı. B'den sonra onaylı tepe yoksa giriş yok.
5. **Geçersizlik:** B'den sonra bir mum bant dibinin altında kapatırsa veya 24 mum dolarsa kurulum iptal.
   Her kırılımdan en fazla bir işlem.
6. **Stop:** B'den k'ya kadarki en düşük iğne (geri çekilmenin dibi). Risk %0.04 - %0.6 arası değilse işlem yok.
7. **Hedef, saat, NY açılışı, yakın likidite (8b), büyük zaman dilimi engeli (8c), çıkış, tek işlem:**
   `results/2026-11-19_aslan_5dk/README.md` 4, 7, 8, 9, 10. maddeleri ve ek 8(c) ile aynı. Saat = k mumunun kapanışı
   TR 09:00 - 22:00.

**Yargı birimi:** long ve short ayrı ayrı. **Geçme çıtası:** aynı (net > 0 ve PF ≥ 1.2 iki dönemde, rastgele kontrol
p < 0.05 gel., 2x masrafta artı, doğrulamada ≥ 30 işlem, %1 riskle düşüş ≤ %25).

### Bilgi ızgarası (sadece bilgi, seçim yapılmaz)
iFVG şartı yok (sadece kırılım + MSP); sıkışma en az 24 mum; genişlik %0.15 / %0.30; sabit hedef 2R.

Geçerse: kâğıt takibe alınır (gerçek emir yok), aday sayılması için 30 canlı işlem gerekir. Geçmezse: Aslan'ın
yöntemi için öneri, Aslan'ın kendi işlemlerini giriş anında kaydetmesidir (koda geçmeyen yargıyı ölçmek için).

Kod: `research/aslan_5dk/sikisma.py`. İş akışı: `.github/workflows/aslan_sikisma.yml`.

---

## 2. Sonuç (2026-11-19, GitHub runner, dev + doğrulama; kasa yüklenmedi)

**GUO'ya not:** Sıkışma kırılımı geçmedi. Long da short da eski yıllarda zararda, rastgele girişten kötü.
Önceki 5 dk testinden de kötü. Aslan sonradan, girişi kırılım mumunun kendisinde yaptığını (geri çekilmeyi
beklemediğini) yazdı; yani bu test onun sırasını ölçmedi (aşağıda not).

| Birim | Gel. işlem | Gel. R/işlem | Gel. PF | Doğ. işlem | Doğ. R/işlem | Doğ. PF | Kontrol p | Sonuç |
|---|---|---|---|---|---|---|---|---|
| Long | 472 | -0.078 | 0.88 | 128 | -0.217 | 0.65 | 0.60 | geçmedi |
| Short | 494 | -0.191 | 0.72 | 142 | +0.079 | 1.14 | 0.88 | geçmedi |

- Ayda ~16 işlem (long + short). %1 riskle gel. düşüşü long %40, short %65.
- Rastgele girişin ortalaması long -0.059R, short -0.101R; gerçek kural ikisinde de daha kötü.
- Tekrarlanabilirlik düzeltmesi: ilk iki çalıştırma, aynı mumda iki tetik olduğunda sıralama runner işlemcisine göre değiştiği için biraz farklı çıktı (long -0.097 / -0.080R). Sıralama kararlı yapıldı (aynı mumda önce gelen kırılım); tablo son, tekrarlanabilir çalıştırma. Karar her üçünde aynı.
- Bilgi ızgarası (seçim yapılmaz): iFVG şartını kaldırmak, sıkışmayı 24 muma çıkarmak, genişliği %0.15 / %0.30
  yapmak veya hedefi sabit 2R yapmak hiçbir birimi iki dönemde birden artıya getirmedi (`summary.csv`).
- Huni (`funnel.csv`): 13034 kırılım, 4303 giriş tetiği, 1242 işlem (en büyük eleme saat penceresi ve aynı anda
  tek işlem).
- Yıllar (`yearly.csv`): short 2020, 2021, 2023, 2024 zararda; long sadece 2022 açıkça artıda.

**Karar:** reddedildi; kâğıt takip yok.

**Sonradan gelen not (sonuçtan sonra, kuralı değiştirmez):** Aslan 1. örnek grafik için şunu yazdı: iFVG'ler bandın
içinde kırılımdan önce oluşur, giriş direnci gövdeyle kıran mumun kapanışıdır; stop girişin altındaki en yakın FVG'nin
biraz altıdır; o örnekteki bant ~100 puan ve ~4 saatti. Bu sıra burada test edilmedi. Test edilecekse yeni ön kayıtla,
Aslan'ın yazılı onayıyla ve proje sahibinin onayıyla, son deneme olarak yapılır.
