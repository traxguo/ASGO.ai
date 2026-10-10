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


def _check(tmp_path, monkeypatch, rel, data):
    import json
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config" / "base.json").write_text(json.dumps({"dry_run": True}))
    (tmp_path / rel).write_text(json.dumps(data))
    monkeypatch.setattr(sc, "REPO", tmp_path)
    errors = []
    sc.check_configs(errors)
    return errors


def test_demo_config_may_disable_dry_run(tmp_path, monkeypatch):
    data = {"dry_run": False, "exchange": {"name": "binance", "demo_trading": True}}
    assert _check(tmp_path, monkeypatch, "config/demo.json", data) == []


def test_demo_config_without_demo_flag_fails(tmp_path, monkeypatch):
    data = {"dry_run": False, "exchange": {"name": "binance"}}
    assert _check(tmp_path, monkeypatch, "config/demo.json", data)


def test_other_config_with_demo_flag_fails(tmp_path, monkeypatch):
    data = {"dry_run": False, "exchange": {"name": "binance", "demo_trading": True}}
    assert _check(tmp_path, monkeypatch, "config/live.json", data)


def test_demo_hosts_guard():
    import importlib.util

    import ccxt
    import pytest
    spec = importlib.util.spec_from_file_location(
        "demo_freqtrade", Path(__file__).resolve().parents[1] / "scripts" / "demo_freqtrade.py")
    df = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(df)
    api = ccxt.binanceusdm()
    with pytest.raises(SystemExit):
        df.assert_demo_hosts(api)
    api.enable_demo_trading(True)
    df.assert_demo_hosts(api)
