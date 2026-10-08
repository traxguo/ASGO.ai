"""build_dashboard reads repo files and never invents numbers."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_dashboard", ROOT / "scripts/build_dashboard.py")
bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bd)

REPORT = """# X_B — dogrulama — 2026-10-08

## Ayarlar
- Dönem: 2025-01-01 00:00:00 → 2026-04-01 00:00:00

## Metrikler
| Metrik | X_B | Al-tut |
|---|---|---|
| Net getiri | 2.2% | -40.1% |
| Max drawdown | 13.5% | 64.5% |
| Profit factor | 1.04 | — |
| Ortalama R | 0.06 | — |
| İşlem sayısı | 88 | — |
| Winrate | 34.1% | — |

## Karar: devam / düzelt / emekli
**Geçemedi.**
"""


def make_repo(tmp: Path) -> Path:
    (tmp / "docs").mkdir()
    (tmp / "cards").mkdir()
    (tmp / "journal").mkdir()
    (tmp / "strategies/active").mkdir(parents=True)
    (tmp / "results/2026-10-08_x_dogrulama").mkdir(parents=True)
    (tmp / "CLAUDE.md").write_text("6. Test hattı: lookahead → ilk backtest → doğrulama.\n", encoding="utf-8")
    (tmp / "docs/roadmap.md").write_text(
        "**Şu anki seviye: 1 — Sabit liste** (x)\n\n## Seviye 0 — Altyapı\n## Seviye 1 — Sabit liste\n"
        "## Sıradaki adım\n1. Karar bekleniyor.\n", encoding="utf-8")
    (tmp / "docs/metrics.md").write_text(
        "## Geçme eşikleri\n| Ölçüt | Eşik |\n|---|---|\n| Doğrulama verisinde profit factor | ≥ 1.2 |\n"
        "| Max drawdown | ≤ %25 |\n| Toplam işlem sayısı | ≥ 100 |\n", encoding="utf-8")
    (tmp / "cards/x.md").write_text(
        "# x — Deneme\n\n## Hipotez\nFikir.\n\n## Durum: elendi — aşama 3 geçilemedi\n\n"
        "## Notlar / öğrenilenler\n- Ders bir.\n", encoding="utf-8")
    (tmp / "journal/2026-10-08.md").write_text("# 2026-10-08\n## Bulgular\n- Bulgu.\n", encoding="utf-8")
    (tmp / "results/2026-10-08_x_dogrulama/rapor.md").write_text(REPORT, encoding="utf-8")
    return tmp


def test_page_shows_repo_numbers(tmp_path):
    page = bd.render(make_repo(tmp_path))
    assert "ASGO TAKİP" in page
    assert "0.06" in page and "-40.1%" in page  # metrics copied from the report
    assert "Ders bir." in page and "Bulgu." in page and "Karar bekleniyor." in page
    assert "Henüz hiçbiri testleri geçmedi" in page  # strategies/active is empty
    assert "1.04 (gereken ≥ 1.2)" in page  # threshold from docs/metrics.md


def test_status_kind():
    assert bd.card_status_kind("elendi — aşama 4 (kod şimdilik candidates/'ta)") == "retired"
    assert bd.card_status_kind("DonchianATR: en iyi aday ... RSIReversionATR: elendi") == "candidate"
    assert bd.card_status_kind("retired (2026-10-04)") == "retired"
    assert bd.card_status_kind("active") == "active"


def test_runs_on_this_repo():
    assert "ASGO TAKİP" in bd.render(ROOT)
