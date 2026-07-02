import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_qr", ROOT / "generate_qr.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_uses_public_url_when_provided():
    assert module.resolve_network_url(explicit_url="https://example.com") == "https://example.com"


def test_uses_environment_url_when_present(monkeypatch):
    monkeypatch.setenv("NETWORK_URL", "https://portal.example.com")
    assert module.resolve_network_url() == "https://portal.example.com"
