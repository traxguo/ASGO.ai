# Parametre kararlılığı (±%20) — Kalabalik_B — 20200101-20250101

Her seferinde tek parametre değişti. Maliyet + funding dahil.

| Varyant | İşlem | Ortalama R | Profit factor | Net getiri % | Max DD % |
|---|---|---|---|---|---|
| base | 123 | +0.277 | 1.46 | +37.0 | 9.3 |
| channel=8 | 154 | +0.199 | 1.34 | +32.0 | 12.3 |
| channel=12 | 103 | +0.145 | 1.21 | +14.4 | 10.0 |
| extreme=0.04 | 98 | +0.253 | 1.42 | +25.8 | 7.7 |
| extreme=0.06 | 148 | +0.109 | 1.15 | +14.6 | 11.1 |
| funding_prints=2 | 122 | +0.196 | 1.33 | +24.0 | 10.6 |
| funding_prints=4 | 125 | +0.142 | 1.22 | +16.9 | 11.6 |

## Diğer dayanıklılık testleri (2020-2024, 16 coin, en fazla 3 işlem)
| Test | Sonuç |
|---|---|
| Masraf x2 (`--fee 0.002`) | 123 işlem, +0.23R, DD %10.0. Hâlâ artı. |
| Hile (lookahead) testi, 2022-2023 | 20 sinyal, sapma yok. Not: funding dosyası doğrudan okunduğu için bu araç funding tarafını sınayamaz; o taraf `tests/test_pusula.py` içindeki "sadece geçmiş" testiyle korunuyor. |
| Pozitif coin oranı | 16 coinin 11'i artıda (≥ %50 şartı geçti). |

Not: altı komşunun hepsi artıda ama hepsi temel ayardan zayıf. Temel ayar test öncesi sabitlendi, sonuca göre seçilmedi.
