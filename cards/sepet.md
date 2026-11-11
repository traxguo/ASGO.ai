# sepet — güçlü / zayıf coin sepeti (haftalık göreli güç rotasyonu)

Kod: henüz yok (kart 2026-11-11'de yazıldı, kurallar test öncesi sabitlendi; test kuyruk 35).

## Hipotez
Son birkaç ayda listenin geri kalanından daha çok yükselen coinler, sonraki haftalarda da listeden iyi gitmeye devam etme eğiliminde (kesitsel momentum: hisse senetlerinde uzun süredir bilinen, kriptoda da sık raporlanan bir davranış). Strateji her hafta aynı listedeki coinleri son 3 ayın getirisine göre sıralar, en güçlü 3 coinde long tutar; sıralamadan düşen coinden çıkar. Son 1 hafta sıralamaya katılmaz, çünkü çok kısa vadede sert yükselen coinler sık sık geri verir (kısa vade gürültüsü).

Pusula'dan farkı: Pusula her coine **kendi** trendine bakarak karar verir ve 4 saatlik **kırılım** anını bekler. Sepet coinleri **birbirine göre** sıralar, kırılım beklemez, sadece haftada bir ve sadece sıralama değişince işlem yapar. Pusula'nın filtresi değildir, ayrı ve bağımsız bir stratejidir; Pusula'nın kodu, sınıfları ve kağıt takibi değişmez.

## Yön
ikisi de, **ayrı ayrı** test edilir ve ayrı raporlanır:
- `SepetLong` (ana): en güçlü 3 coinde long.
- `SepetShort` (ayrı varyant): en zayıf 3 coinde short. Kendi başına geçmek zorundadır; long'un sonucuyla birleştirilip "toplamda artı" denmez.

## Sıralama (her hafta, son **kapanmış** günlük mumlar)
- Sıralama anı `t`: pazar günlük mumunun kapanışı (pazartesi 00:00 UTC). Sadece `t` anına kadar kapanmış günlük mumlar kullanılır.
- Puan: `mom_skip = close_1d[t-7] / close_1d[t-97] - 1` → "7 gün öncesinde biten 90 günlük getiri" (son 7 gün hariç).
- Sıralamaya giren coin: o listede (`pairs_wide16.json` veya `pairs_new20.json`) olan ve `t` anında en az 97 kapanmış günlük mumu olan coin. Verisi yetmeyen coin sayılmaz.
- Uygun coin sayısı 6'dan azsa o hafta sepet kurulmaz (long ve short sepet asla çakışmasın diye).
- Eşit puan (çok nadir): sembol adına göre alfabetik.
- Her liste kendi içinde sıralanır; iki liste ayrı ayrı test edilir (kuyruktaki kabul kuralı: iki listede de geçmeli).

## Giriş koşulları (sinyal mumu: pazar 20:00 UTC'de açılan 4h mum, pazartesi 00:00'da kapanır)
Long (hepsi):
- [rebalance_time] Teknik: sinyal 4h mumu pazar 20:00 UTC'de açılan mum (günlük pazar mumu onunla birlikte kapanır) | Açıklama: "Haftalık sıralama günü (pazartesi 00:00 UTC)."
- [in_top_basket] Teknik: coinin `mom_skip` sırası listede ilk 3 içinde | Açıklama: "Coin, son 90 günün getirisinde (son 7 gün hariç) listedeki {n_coins} coin arasında {rank}. sırada (%{mom_skip})."
- [abs_mom_up] Teknik: `mom_skip > 0` | Açıklama: "Coinin 90 günlük getirisi artıda (%{mom_skip})."
- [btc_above_ema50] Teknik: BTC'nin son kapanmış günlük kapanışı günlük EMA(50) üstünde | Açıklama: "Bitcoin 50 günlük ortalamasının üstünde ({btc_close_1d} > {btc_ema50_1d})."
- [no_open_trade] Teknik: coinde açık long yok (açık işlem varsa o işlem devam eder, yeni emir ya da büyütme yok) | Açıklama: yok (sinyal mesajına yazılmaz).

Short (hepsi, `SepetShort`):
- [rebalance_time] (aynı)
- [in_bottom_basket] Teknik: coinin `mom_skip` sırası listede son 3 içinde | Açıklama: "Coin, son 90 günün getirisinde (son 7 gün hariç) listedeki {n_coins} coin arasında sondan {rank_from_bottom}. sırada (%{mom_skip})."
- [abs_mom_down] Teknik: `mom_skip < 0` | Açıklama: "Coinin 90 günlük getirisi eksi (%{mom_skip})."
- [btc_below_ema50] Teknik: BTC'nin son kapanmış günlük kapanışı günlük EMA(50) altında | Açıklama: "Bitcoin 50 günlük ortalamasının altında ({btc_close_1d} < {btc_ema50_1d})."
- [no_open_trade] (aynı, short için)

Sepetteki bir coin stop > %8 veya likidasyon kuralı yüzünden sinyal alamazsa yeri **boş kalır**; 4. sıradaki coin yerine girmez (kural basit kalsın, sonradan seçme olmasın). Kaç kez olduğu raporlanır.

## Çıkış koşulları (sabit stop ve TP'lere ek olarak)
Sadece sıralama gününde (aynı sinyal mumunda) kontrol edilir; çıkış pazartesi 00:00 mumunun açılışında yapılır.
- [left_basket] Teknik: long için coin artık ilk 3'te değil (short için son 3'te değil) | Açıklama: "Coin güçlü sepetten düştü ({rank}. sıraya indi), işlem kapatılıyor." / "Coin zayıf sepetten çıktı, işlem kapatılıyor."
- [abs_mom_lost] Teknik: long için `mom_skip ≤ 0` (short için `≥ 0`) | Açıklama: "Coinin 90 günlük getirisi artık artıda değil, işlem kapatılıyor."
- [market_off] Teknik: long için BTC günlük kapanışı EMA(50) altında (short için üstünde) | Açıklama: "Bitcoin 50 günlük ortalamanın altına indi, sepet kapatılıyor."

Hafta içinde stop veya TP2 ile kapanan coine o hafta yeniden girilmez; sonraki sıralama gününde hâlâ sepetteyse yeni sinyal alır.

## İşlem yönetimi (ortak modülden, `strategies/common/`)
- Giriş bölgesi kuralı: varsayılan, sinyal mumunun kapanışı etrafında 0.25 ATR(14, 4h) genişliğinde bölge, bölge ortasına limit emir.
- Stop kuralı: varsayılan "geniş olan": bölge ortasından 1.5 ATR(14, 4h) veya son 10 adet 4h mumun dibi − 0.1 ATR (short'ta tepesi + 0.1 ATR), hangisi uzaksa. Stop fiyatın %8'inden uzaksa sinyal yok. Stop sabittir; TP1'den sonra başabaşa çekilir (Model B), başka hareket etmez.
- TP modeli: **Model B** (varsayılan, değiştirilmez): TP1 = 2R'de pozisyonun yarısı kapanır ve stop girişe (+%0.15 tampon) çekilir; TP2 = 4R'de kalan yarı kapanır. TP1 ≥ 1R şartı sağlanıyor. TP'ye gelmeden sıralama günü gelirse yukarıdaki çıkış koşulları geçerli.
- Sinyal geçerlilik süresi: 3 mum (12 saat). Dolmazsa sinyal iptal olur, coin o hafta işlemsiz kalır.
- Risk: işlem başına sermayenin %1'i, pozisyon büyüklüğü stop mesafesinden. İzole marjin, en fazla 3x kaldıraç; likidasyon fiyatı stop mesafesinin en az 2 katı uzakta değilse kaldıraç düşer ya da sinyal yok.
- Aynı anda en fazla **3** açık işlem (her bacak kendi koşusunda; long ve short aynı hesapta birleştirilmez). Aynı coinde aynı anda long ve short yok (ayrı koşular olduğu için zaten olmaz).
- Maliyet: emir başına %0.1 (komisyon + kayma), kısmi çıkış ayrı emir; funding geçmiş veriden. Maliyet x2 (`--fee 0.002`) ayrıca.

## Zaman dilimi ve parametreler (test öncesi sabitlendi, tarama yok)
| Parametre | Değer | Gerekçe | Komşuluk (sadece dayanıklılık aşamasında) |
|---|---|---|---|
| İşlem zaman dilimi | 4h (detay 1h) | Pusula ile aynı altyapı; giriş bölgesi ve stop 4h ATR ile | sabit |
| Sıralama zaman dilimi | 1d | haftalık karar için günlük kapanış yeterli | sabit |
| Getiri penceresi | 90 gün | projede zaten kullanılan momentum uzunluğu (Pusula); bu strateji için seçilmedi | 72 / 108 |
| Atlanan son dönem | 7 gün | çok kısa vadeli geri dönüş gürültüsünü dışarıda bırakmak; bir haftalık tutma süresine eşit | 5 / 9 |
| Sepet büyüklüğü | 3 | projenin 3 yer × %1 = %3 toplam açık risk düzeniyle aynı; 16 coinin ≈ beşte biri | 2 / 4 |
| Sıralama günü / saati | pazar günlük kapanışı = pazartesi 00:00 UTC | haftalık mumun kapanışı; kağıt takip rutini de pazartesi | sabit |
| Mutlak momentum şartı | long `> 0`, short `< 0` | düşen coini "en az düşen" diye almamak | sabit |
| Piyasa filtresi | BTC günlük kapanış EMA(50) üstü (short: altı) | kesitsel momentum ayı piyasasında ve sert dönüşlerde çöker; Pusula'daki EMA50 ile aynı | sabit |
| Stop | 1.5 ATR(4h) / 10 mum dibi − 0.1 ATR, geniş olan, en fazla %8 | ortak modül varsayılanı | sabit (ortak modül) |
| TP | Model B (2R yarı + BE, 4R) | ortak modül varsayılanı | ızgara genişletilmez |
| En fazla açık işlem | 3 | sepet büyüklüğü | sabit |
| Kaldıraç | en fazla 3x, likidasyon ≥ 2 × stop | kurallar | sabit |

## Varyantlar (önceden belirlendi; karar sadece ana sınıflarla verilir)
- `SepetLong`: **ana**, long kararı buna göre.
- `SepetShort`: **ana**, short kararı buna göre (ayrı rapor).
- `SepetLongNoBtc`: BTC filtresi olmadan (giriş ve `market_off` çıkışı yok). Sadece filtrenin katkısını görmek için; daha iyi çıksa bile ana sınıf olmaz.
- `SepetLongNoTp`: TP yok, sadece stop + sıralama çıkışları (Pusula'daki "sabit TP yerine trend çıkışı" gibi). Sadece bilgi; brief 7.3'teki 2 TP yapısından sapma olduğu için seçilmesi proje sahibinin kararı ister.

## Kabul kuralı (test öncesi sabit)
Dönemler: geliştirme 2020-01-01 → 2024-12-31 (`--timerange 20200101-20250101`; ilk sıralama için 97 günlük ısınma gerekir, ilk işlemler en erken 2020 nisanında), doğrulama 2025-01-01 → 2026-03-31. **Kasa (2026-04-01 → 2026-09-30) bu stratejide kullanılmaz**; sadece "active" öncesi bir kez.
1. Geliştirme, iki listede ayrı ayrı (wide16, new20), long ve short ayrı. Her bacak için `docs/metrics.md` eşikleri: maliyet + funding sonrası ortalama > 0R, PF ≥ 1.2, max DD ≤ %25, en az 100 işlem, coinlerin en az yarısı artıda, maliyet x2'de hâlâ > 0R (değilse "kırılgan"), al-tut kıyası (aynı listenin eşit ağırlıklı al-tutu ve BTC al-tut): daha yüksek getiri ya da benzer getiriyle belirgin daha düşük DD. Bir bacak **iki listede de** geçmezse o bacak elenir; doğrulamaya bakılmaz.
2. Geliştirmeyi geçen bacak doğrulamada **bir kez**, aynı kurallarla ve aynı eşiklerle (doğrulama PF ≥ 1.2). Sonuca bakıp kural değişmez.
3. İkisini de geçerse dayanıklılık: yukarıdaki komşuluk sütunu (tek ayar değişir, önceden sabit), ortalama R hepsinde artıda olmalı.
4. Raporda ayrıca: ileriye bakma kontrolü (veri kesme testi), haftalık dönüşüm (sepet değişimi) ve masrafa etkisi, sepetten boş kalan yerler (stop > %8 / likidasyon), en büyük 5 işlemin payı ve onlar hariç ortalama, yıllara göre R, toplam funding, stop / BE / TP1 sonrası BE / TP2 / sıralama çıkışı oranları, varyantlar.

## Veri madenciliği uyarısı
- Göreli güç fikri bu projede daha önce **Pusula'nın içinde** denendi ve tutmadı: "short sadece BTC'den zayıf coinde" (geliştirme 1), "long sadece BTC'den güçlü coinde" (geliştirme 2b), aynı anda çok sinyal varsa 90 günlük getirisi yüksek olanı seç (kuyruk 7, `PusulaV2NoBeRank`). Sepet bunlardan farklıdır (kırılım beklemez, sıralamanın kendisi sinyaldir), ama sonuç iyi çıkarsa bu geçmiş akılda tutulmalı.
- Kuyruk 12'de Pusula'da kırılım beklemeden "trendde olmak" kötü çıktı (stoptan hemen sonra tekrar giriş). Sepet bunu haftada bir karar ve hafta içi yeniden giriş yasağıyla sınırlar; yine de benzer risk var.
- 90 gün, EMA50 ve Model B projede zaten var olan değerler; bu strateji için seçilmediler ama aynı veride daha önce görüldüler. 2020-01 → 2026-09 verisinin tamamı başka stratejilerde (Pusula, Kalabalık) görüldü; bu strateji için doğrulama ve kasa dönemleri yine de ilk kez açılacak.
- Coin listeleri bugün hâlâ listede olan coinlerden oluşuyor (seçim iyimserliği, kuyruk 3'te ortalama R'de ≈ %10-20 ölçüldü). Kesitsel stratejide bu etki daha büyük olabilir: batan coinler sıralamada zaten yok.
- Test başına tek ana koşu, tarama yok. Kötü çıkarsa ayar değiştirilip tekrar denenmez; kart `retired` olur.

## Ortak modülle uyum ve gerilim (dürüst not)
- Sıralama tabanlı haftalık rotasyon doğası gereği "elde tut, sıralamadan düşünce sat" stratejisidir; 2 TP'li yapıya tam oturmaz. Kart bunu ortak modüle uyduruyor: giriş bölgesi, stop, Model B ve kaldıraç kuralları aynen ortak modülden; sıralama çıkışı ek bir çıkış olarak eklenir (Pusula'nın EMA20 çıkışı gibi `populate_exit_trend` ile). TP1 = 2R ≥ 1R.
- Gerilim 1: Model B, sepette kalmaya devam eden güçlü coini 4R'de satar; rotasyonun kârının bir kısmı burada kesilebilir. Bunu görmek için `SepetLongNoTp` sadece bilgi olarak koşar.
- Gerilim 2: stop 4h ATR ile (aynı stop Pusula'da ortalama %5.4 / %6.3 uzaklıkta, kuyruk 14), tutma süresi bir hafta ve üstü. Haftalık tutuşta günlük ATR daha doğal olurdu ama altcoinlerde %8 stop sınırını çoğu zaman aşar. Pusula'da kazanan işlemler aynı 4h stopla ortalama ≈ 13 gün sürüyordu, bu yüzden uyumlu sayıldı; çok sık stop olursa raporda görünür, kural değiştirilmez.
- Gerilim 3: stop > %8 olan coin sepette olduğu halde işlemsiz kalır ve yerine başkası girmez; oynak dönemlerde sepet 3'ten az coinle çalışabilir.
- Uygulama notu: Freqtrade her coini ayrı işler; sıralama için listedeki tüm coinlerin günlük verisi `DataProvider` ile okunur (kuyruk 19'daki piyasa genişliği sınıfında olduğu gibi), sadece kapanmış mumlar.

## Durum: candidate (kod yok, test kuyruk 35)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|
| 2026-11-11 | Kart yazıldı, kurallar test öncesi sabitlendi (kuyruk 34) | Test yok | — |

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
