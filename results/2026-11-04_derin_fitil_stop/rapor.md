# Derin Fitil stoplu sürüm — gerçekçi evren (2026-11-04)

GUO isteği: "stoplu sürümü test et". Varyantlar test ÖNCESİ sabitlendi (yönetici): fiyat stopu girişin %4 / %6 / %8 altı
+ aynı coine 24 saatte en fazla 1 giriş. Geçme şartı: geliştirme ve doğrulamada artı, masraf x2'de artı, geliştirme düşüşü %61'in açıkça altında.

Kod: `research/scans/wick_catcher_pit.py down` (`SL=`, `COOLDOWN=24`). Evren: her yılın en çok işlem gören 36 coini, silinenler dahil
(`research/xsec/top36_yearly.json`). Masraf %0.20 gidiş-dönüş + funding (%0.01 / 8 saat); x2 = %0.40. Stop: dolum mumu stopun altında
kapanırsa o kapanıştan, sonra 15dk diplerle kontrol; fiyat boşlukla geçerse mum açılışından çıkar (masraf zaman çıkışıyla aynı).
Diğer kurallar canlı botla aynı. Ham çıktı: `runs.jsonl`.

## Ana sonuçlar (masraf %0.20)
| Sürüm | Dönem | İşlem (gün) | Stop yiyen | Ort. % | Kazanan | PF | Kasa | En büyük düşüş | En kötü gün | En iyi 5 gün hariç |
|---|---|---|---|---|---|---|---|---|---|---|
| Canlı kural (stopsuz) | geliştirme | 228 (0.13) | — | -0.70 | %65 | 0.82 | -38.8% | -60.8% | -33.4% | -1.37 |
| Stop %4 + 24s | geliştirme | 194 (0.11) | 63 | +1.36 | %61 | 1.82 | +65.5% | **-10.0%** | -5.8% | -0.72 |
| Stop %6 + 24s | geliştirme | 193 (0.11) | 49 | +1.18 | %64 | 1.64 | +54.0% | -14.1% | -6.3% | -0.55 |
| Stop %8 + 24s | geliştirme | 193 (0.11) | 36 | +1.22 | %67 | 1.64 | +56.4% | -11.1% | -8.2% | -0.55 |
| Canlı kural (stopsuz) | doğrulama | 155 (0.34) | — | +0.35 | %61 | 1.11 | +5.6% | -23.6% | -9.5% | -1.14 |
| Stop %4 + 24s | doğrulama | 127 (0.28) | 43 | +1.23 | %56 | 1.61 | +32.7% | **-11.8%** | -7.9% | -0.42 |
| Stop %6 + 24s | doğrulama | 127 (0.28) | 33 | +1.15 | %59 | 1.52 | +29.8% | -13.2% | -8.3% | -0.64 |
| Stop %8 + 24s | doğrulama | 127 (0.28) | 23 | +1.19 | %62 | 1.52 | +31.2% | -13.5% | -7.8% | -0.69 |

## Masraf x2 (%0.40)
| Sürüm | Geliştirme kasa / DD | Doğrulama kasa / DD |
|---|---|---|
| Canlı kural (stopsuz) | -44.4% / -61.6% | -0.7% / -25.1% |
| Stop %4 + 24s | +53.2% / -11.5% | +26.3% / -12.3% |
| Stop %6 + 24s | +42.6% / -15.5% | +23.5% / -13.7% |
| Stop %8 + 24s | +44.8% / -12.3% | +24.8% / -14.4% |

Al-tut (BTC): geliştirme +%1001 (DD -%77), doğrulama -%27 (DD -%52).

## Yıllara göre kasa (masraf %0.20)
| Sürüm | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 Q1 |
|---|---|---|---|---|---|---|---|
| Stop %4 + 24s | +0.4 | -2.5 | +45.0 | +12.9 | -3.2 | +38.9 | -7.6 |
| Stop %6 + 24s | +1.2 | +2.5 | +37.3 | +12.0 | -7.5 | +37.0 | -7.8 |
| Stop %8 + 24s | +0.8 | +2.1 | +37.4 | +10.6 | -3.7 | +42.3 | -12.0 |

## Teşhis (karar için değil)
- Sadece 24 saat kuralı (stopsuz): geliştirme +%74 / DD -%11.6, doğrulama +%23 / DD -%18.1. LUNA zincirini asıl kesen 24 saat kuralı; stop doğrulamadaki düşüşü -%18'den -%12..-13'e indiriyor.
- Sadece stop (24 saat kuralı yok): geliştirme +%4..+%17, DD -%21..-23. Tek başına yetmiyor.

## Sonuç
- **Üç stoplu sürüm de şartları geçti:** iki dönemde artı, masraf x2'de artı, geliştirme düşüşü -%61'den -%10..-14'e indi. Üçü birbirine yakın: tek şanslı nokta değil.
- **Zayıf yanlar (gizlenmez):**
  - En iyi 5 gün çıkarılınca hepsi eksi (-%0.4..-0.7 / işlem): kâr hâlâ birkaç çöküş gününden geliyor.
  - Geliştirme kârının çoğu 2022'de; 2024 ve 2026 Q1 eksi.
  - 24 saat kuralı LUNA görüldükten sonra önerildi; geliştirme dönemi bu açıdan tam bağımsız değil.
  - Seyrek: portföyde günde ~0.1-0.3 işlem.
- En düşük düşüş: stop %4 + 24 saat. Botlara dokunulmadı; karar yönetici ve GUO'da. Kasa dönemi kullanılmadı.
