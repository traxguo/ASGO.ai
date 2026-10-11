# sfp_sweep — Swing Failure Pattern (SFP): tepe/dip likiditesi alınıp geri dönülmesi

Kod: [`strategies/candidates/sfp_sweep.py`](../strategies/candidates/sfp_sweep.py)

**Bu kart ilk testten ÖNCE yazıldı (2026-10-11).** Kurallar, parametreler, varyant ve geçme şartı sonuçlar görülmeden sabitlendi; sonuca bakıp değiştirilmez.

## Hipotez
Proje sahibinin (GUO) getirdiği kural. Üst zaman dilimindeki (15 dk) son tepenin hemen üstünde stop emirleri birikir. 5 dakikalık bir mum bu tepenin üstüne iğne atıp (stopları alıp) tekrar tepenin altında kapanırsa ve üst iğnesi mumun en az yarısıysa, "kırılım başarısız oldu" (swing failure) demektir; fiyatın aralığın ortasına (EQ) ve sonra karşı uca dönmesi beklenir. Long tarafı bunun aynasıdır (dibin altına iğne, dibin üstünde kapanış, alt iğne ≥ %50).

Bu test **ilk elemedir**: "bu fikir bir şansı hak ediyor mu?" sorusuna cevap arar. Sadece geliştirme verisi (2022-2024) kullanılır.

**Aslan'ın stratejilerinden farkı** (`aslan_liquidity`, `ams_liquidity_mss`, ikisi de ~0R / masrafla eksi çıktı): orada likidite seviyesi alındıktan sonra ayrıca bir yapı kırılımı (MSS) ya da FVG/iFVG teyidi bekleniyor, hedef sabit R katı (1R/2R ya da 1.5R/3R) ve günlük/EMA yön filtresi vardı. Burada teyit **tek mumdur** (iğne atıp geri kapanma + iğne ≥ %50), yön filtresi yoktur, hedefler **yapısaldır** (aralığın ortası ve karşı uç) ve TP1 R katı değildir.

## Yön
İkisi de (long ve short ayrı raporlanır).

## Tanımlar
- **Üst zaman dilimi (bağlam):** 15 dk (ana sürüm). 5 dk mumlardan strateji içinde yeniden örneklenir (`date` 15 dk'ya yuvarlanır; 3 mumu eksiksiz olmayan 15 dk mumu kullanılmaz).
- **Tepe (swing high):** solundaki 3 ve sağındaki 3 adet 15 dk mumdan daha yüksek tepesi olan 15 dk mumu (sol: kesin büyük, sağ: büyük-eşit). **Dip** aynası. Sağdaki 3 mum kapanınca onaylanır ve ancak **onaydan sonra açılan** 5 dk mumlarında kullanılır (geleceği görme yok).
- **Güncel tepe / dip:** o ana kadar onaylanmış en son tepe / en son dip.
- **İlk dokunuş kuralı (yorum, test öncesi sabitlendi):** bir tepe seviyesi, onaylandıktan sonra o seviyenin üstüne çıkan **ilk** 5 dk mumunda test edilir. O mum SFP şartlarını sağlamazsa (örneğin seviyenin üstünde kapanırsa) seviye harcanmış olur; aynı tepeden ikinci sinyal çıkmaz. Daha yeni bir tepe onaylanınca eskisi bırakılır. Dip için aynısı.

## Giriş koşulları (5 dk, kapanmış mum)
Short (hepsi):
- [sweep_swing_high] Teknik: high > güncel 15 dk tepesi, ve bu, tepe onaylandıktan sonra seviyenin üstüne çıkan ilk 5 dk mumu | Açıklama: "Fiyat 15 dakikalık tepenin ({swing_high}) üstündeki likiditeyi aldı."
- [close_back_below] Teknik: close < güncel 15 dk tepesi | Açıklama: "Mum tekrar tepenin altında kapandı (başarısız kırılım)."
- [upper_wick_50] Teknik: high − max(open, close) ≥ 0.5 × (high − low) | Açıklama: "Üst iğne mumun en az yarısı."
- [eq_below_entry] Teknik: EQ = (güncel tepe + güncel dip)/2 < close (EQ girişin yanlış tarafındaysa işlem yok) | Açıklama: "Aralığın ortası ({eq}) fiyatın altında."

Long (hepsi): aynası — [sweep_swing_low] low < güncel 15 dk dibi (ilk dokunuş), [close_back_above] close > güncel dip, [lower_wick_50] min(open, close) − low ≥ 0.5 × (high − low), [eq_above_entry] EQ > close.

## İşlem yönetimi
**Ortak modülün (`strategies/common/`) Freqtrade iskeleti (`ManagedStrategy`: stop, kısmi TP emirleri, kaldıraç, %1 risk) kullanılır; seviyeler ise proje sahibinin kuralından gelir (R katı değil).**
- **Giriş:** kural "sinyal mumunun kapanışında" diyor. Freqtrade sinyali mum kapanınca görür, bu yüzden giriş **bir sonraki mumun açılışında piyasa emriyle** (pratikte kapanış fiyatına çok yakın). Not: genel kural "limit emir tercih" diyor; kapanışta giriş kuralına en yakın dürüst karşılık sonraki açılış olduğu için piyasa emri seçildi. Düşük masraf koşusu (%0.03/emir) limit emirli bir borsayı temsil eden teşhistir.
- Giriş anında fiyat EQ'nun yanlış tarafına ya da stopun ötesine geçmişse işlem açılmaz (`confirm_trade_entry`).
- **Stop:** iğnenin ucunun **%0.1 ötesi** (short: high × 1.001, long: low × 0.999). Mum içinde kontrol edilir.
- **TP1:** pozisyonun **%50'si EQ'da** (güncel tepe ile güncel dibin ortası), limit emir. TP1 dolunca **stop girişe (başa baş) çekilir** — tam giriş fiyatı, ek tampon yok (kural "breakeven" diyor; masraf yüzünden başa baş çıkış küçük bir eksidir).
- **TP2:** kalan %50 **karşı seviyede** (short: güncel dip, long: güncel tepe), limit emir.
- Başka çıkış yok (çıkış sinyali yok, süre sınırı yok).
- **TP1 < 1R notu:** projenin kuralı TP1 ≥ 1R. Bu kural yapısal TP1 kullandığı için TP1 1R'den yakın olabilir. Kurala sadık kalmak için bu sinyaller **elenmez**; raporda TP1 < 1R olan işlem sayısı ve sonuçları ayrıca verilir (varyant değildir). Kart "active" olmadan önce bu çelişki proje sahibiyle çözülmelidir.
- **Risk:** işlem başına kasanın **%1'i** (pozisyon = kasa × %1 / stop mesafesi, `custom_stake_amount`). Stop çok darsa kaldıraç yükselir; **kaldıraç en fazla 10x** (genel kural için kararlaştırılan üst sınır; `docs/rules.md` 3x diyor, 5 dk'lık dar stoplarda %1 risk 3x ile çoğu zaman sığmaz — not edildi). Likidasyon her zaman stop mesafesinin en az 2 katı uzakta (ortak modül). Gerekli marj kasada yoksa işlem atlanır (farklı risk alınmaz).
- **En fazla 1 açık işlem** (tüm coinlerde toplam; `--max-open-trades 1`).
- **3 kayıp kuralı:** üst üste 3 kayıplı işlem (masraf + funding dahil net kâr < 0) kapanırsa, 3. kaybın kapanışından itibaren **24 saat yeni işlem yok**. Duraklamadan sonra sayaç sıfırdan başlar (yeniden 3 kayıp gerekir). Tüm coinler için ortak (`confirm_trade_entry`).
- Kasa 10000 USDT (`dry_run_wallet`).
- Sinyal geçerlilik süresi: 1 mum (sonraki açılış).
- **1R** = gerçek giriş fiyatı ile stop arasındaki mesafe × pozisyon miktarı. İşlem sonucu R = net kâr (masraf + funding dahil, kısmi çıkışlar dahil) / 1R.

## Zaman dilimi ve parametreler (test öncesi sabitlendi)
| Parametre | Değer | Makul aralık |
|---|---|---|
| Giriş zaman dilimi | 5m | sabit |
| Bağlam zaman dilimi | 15m (varyant: 1h) | sabit |
| Tepe/dip gücü | sol 3 / sağ 3 mum | sabit |
| İğne oranı | ≥ %50 | sabit |
| Stop tamponu | %0.1 | sabit |
| TP1 / TP2 | EQ %50 / karşı seviye %50 | sabit |
| Başa baş | TP1 sonrası, tam giriş fiyatı | sabit |
| Risk | %1 | sabit |
| Kaldıraç üst sınırı | 10x | sabit |
| En fazla açık işlem | 1 | sabit |
| Kayıp duraklaması | 3 kayıp → 24 saat | sabit |

## Varyantlar (önceden belirlendi; karar sadece ana sürüme göre)
- `SfpSweep`: ana sürüm (15 dk bağlam). Karar buna göre.
- `SfpSweep1h`: aynı kurallar, tepe/dipler 1 saatlik mumlardan (sol 3 / sağ 3). Teşhis.

## Test planı (önceden)
- Ana evren BTC/ETH/SOL (`config/pairs_btc_eth_sol.json`), 5m mum, `--max-open-trades 1`, maliyet emir başına %0.1 (%0.05 komisyon + %0.05 kayma; kısmi çıkış ayrı emir), funding geçmiş veriden.
- Önce hile testi (lookahead-analysis), 3 coin, kısa dönem.
- Geliştirme 2022-01-01 → 2024-12-31 (`--timerange 20220101-20250101`).
- Ek koşular: masraf x2 (`--fee 0.002`); düşük masraflı / limit emirli borsa (`--fee 0.0003`, teşhis); masrafsız (`--fee 0`, teşhis); 16 coin (`config/pairs_wide16.json`) 1 yuva ve 16 yuva (teşhis); coin sırası kontrolü (ana koşu, coin listesi ters sırada).
- **İlk eleme şartı ("şansı hak ediyor mu")**, normal masrafla, ana sürüm: ortalama R > 0, PF ≥ 1.1, max DD ≤ %35, coinlerin en az yarısı artıda, 3 yılın en az 2'sinde artı. GUO'nun hedefi günde ~3 işlem; gerçek sayı dürüstçe raporlanır.
- Doğrulama (2025+) bu turda YAPILMAZ. Kasaya (2026-04 sonrası) dokunulmaz.
- Sonuca bakıp kural, eşik veya varyant değiştirilmez.

## Durum: candidate (test bekliyor)

## Test geçmişi
| Tarih | Test | Sonuç özeti | Rapor linki |
|---|---|---|---|

## Notlar / öğrenilenler

## Emeklilik gerekçesi (varsa)
