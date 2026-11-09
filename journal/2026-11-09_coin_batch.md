# 2026-11-09 — Coin fikir paketi
## Yapılanlar
- 8 yeni günlük coin fikri ön kayıtla test edildi (`results/2026-11-09_coin_batch/README.md`, ön kayıt 07cb358, çıta eki b3940c0).
- Kod `research/coin_batch/batch.py`; kart `cards/coin_paketi.md`; karar `docs/decisions.md`.
## Bulgular (rakamlarla)
- 0/8 geçti. F1 trend long/nakit: gel. +11.3%/işlem PF 11.3, doğ. +0.65% PF 1.79 ama p 0.067 ve doğ. 12 işlem.
- F4 aşırı düşüş al (z2.5, 3 gün): gel. +0.69% PF 1.19 p 0.32; doğ. +2.85% PF 2.73 (48 işlem).
- F8 funding aşırılığı short: gel. +0.48% PF 1.13; doğ. +1.84% PF 1.41 (32 işlem).
## Başarısız olan / elenen
- F3 volatilite kırılımı: ön kayıtlı kural "geçti" (long gel. +0.71% PF 1.84, doğ. +0.38% PF 1.49) ama "iki seviye aynı gün değerse işlem yok" kuralı ileriye bakıyordu; düzeltilince long doğ. −0.07%, short iki dönemde eksi.
- F2, F5, F6, F7 doğrulamada eksi veya çıtanın altında.
## Açık sorular
- F4 ve F8 short yeni bir ön kayıtla ileriye dönük test edilsin mi? (Kasa artık geliştirmede kullanılamaz.)
## Sıradaki adım
- Proje sahibi isterse F4 / F8 short için yeni ön kayıt + ileriye dönük kâğıt gözlem (karar onun).
