"""SDK 单测：不触网（mock requests.Session.get）。"""
from pathlib import Path

import pandas as pd
import pytest

import quantsonar
from quantsonar import QuantSonar, QuantSonarError, RateLimitError
from quantsonar._endpoints import ENDPOINTS


def test_public_pypi_copy_uses_product_native_language():
    root = Path(__file__).resolve().parents[1]
    public_files = [root / "README.md", root / "pyproject.toml"]
    public_files.extend((root / "quantsonar").glob("*.py"))
    forbidden = ("tu" + "share", "命名" + "对齐")

    for path in public_files:
        content = path.read_text(encoding="utf-8").casefold()
        for phrase in forbidden:
            assert phrase.casefold() not in content, f"{phrase!r} found in {path.name}"


class FakeResp:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.headers = headers or {}
        self.text = str(self._payload)

    def json(self):
        return self._payload


@pytest.fixture
def client(monkeypatch):
    c = QuantSonar(token="qs_test")
    c._calls = []

    def fake_get(url, params=None, timeout=None):
        c._calls.append((url, params))
        return c._next_resp

    monkeypatch.setattr(c._session, "get", fake_get)
    return c


def test_requires_token(monkeypatch):
    monkeypatch.delenv("QUANTSONAR_TOKEN", raising=False)
    with pytest.raises(ValueError):
        QuantSonar()


def test_env_token(monkeypatch):
    monkeypatch.setenv("QUANTSONAR_TOKEN", "qs_env")
    assert QuantSonar()._token == "qs_env"


def test_daily_returns_dataframe(client):
    client._next_resp = FakeResp(payload=[
        {"symbol": "600519.SH", "trade_date": "20260710", "close": 1204.98},
    ])
    df = client.daily(symbol="600519.SH", start_date="20260101")
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["close"] == 1204.98
    url, params = client._calls[0]
    assert url.endswith("/v1/market/daily")
    assert params == {"symbol": "600519.SH", "start_date": "20260101"}


def test_none_params_dropped(client):
    client._next_resp = FakeResp(payload=[])
    client.daily(symbol="600519.SH", start_date=None)
    assert client._calls[0][1] == {"symbol": "600519.SH"}


def test_rate_limit_error(client):
    client._next_resp = FakeResp(429, {"detail": "超出突发限速"}, {"Retry-After": "12"})
    with pytest.raises(RateLimitError) as e:
        client.daily(symbol="600519.SH")
    assert e.value.retry_after == 12
    assert "超出" in str(e.value)


def test_api_error(client):
    client._next_resp = FakeResp(422, {"detail": "证券代码需带交易所后缀"})
    with pytest.raises(QuantSonarError) as e:
        client.daily(symbol="600519")
    assert e.value.status == 422


def test_unknown_endpoint_raises(client):
    with pytest.raises(AttributeError):
        client.no_such_endpoint


def test_all_endpoints_are_callable(client):
    client._next_resp = FakeResp(payload=[])
    for name in ENDPOINTS:
        assert callable(getattr(client, name)), name


def test_module_level_endpoints_listing():
    df = quantsonar.endpoints()
    assert len(df) == len(ENDPOINTS) >= 38
    assert {"method", "path", "summary"} <= set(df.columns)
