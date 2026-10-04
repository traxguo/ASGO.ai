import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "safety_check", Path(__file__).resolve().parents[1] / "scripts" / "safety_check.py"
)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def hits(line):
    return [n for n, p in sc.SECRET_PATTERNS.items() if p.search(line)]


def test_detects_telegram_token():
    assert "telegram_bot_token" in hits("TOKEN=123456789:AAH" + "x" * 32)


def test_detects_assignment():
    assert "secret_assignment" in hits('"api_secret": "abcd1234efgh5678"')


def test_allows_empty_placeholders():
    assert hits("TELEGRAM_BOT_TOKEN=") == []
    assert hits('"key": "",') == []


def test_dry_run_values_found_nested():
    vals = list(sc.iter_dry_run_values({"a": {"dry_run": False}, "dry_run": True}))
    assert ("a.dry_run", False) in vals and ("dry_run", True) in vals


def test_repo_passes():
    assert sc.main() == 0
