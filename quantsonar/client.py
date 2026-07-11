"""QuantSonar API 客户端。

    import quantsonar as qs
    qs.set_token("qs_你的密钥")            # 或环境变量 QUANTSONAR_TOKEN
    df = qs.daily(symbol="600519.SH", start_date="20260101")

所有方法返回 pandas.DataFrame；参数与 https://quantsonar.com/docs 一一对应。
"""
from __future__ import annotations

import os

import pandas as pd
import requests

from ._endpoints import ENDPOINTS

DEFAULT_BASE_URL = "https://quantsonar.com"
_ENV_TOKEN = "QUANTSONAR_TOKEN"


class QuantSonarError(RuntimeError):
    """API 返回错误。message 为服务端中文说明，status 为 HTTP 状态码。"""

    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status


class RateLimitError(QuantSonarError):
    """超出限速（429）。retry_after 为建议等待秒数（突发超限时有值）。"""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message, status=429)
        self.retry_after = retry_after


class QuantSonar:
    """API 客户端。每个数据接口都是同名方法：qs.daily(...) / qs.income(...) 等。"""

    def __init__(self, token: str | None = None,
                 base_url: str = DEFAULT_BASE_URL, timeout: float = 30):
        token = token or os.environ.get(_ENV_TOKEN, "")
        if not token:
            raise ValueError(
                f"缺少 API Key：传入 token 参数或设置环境变量 {_ENV_TOKEN}。"
                f"免费获取：{DEFAULT_BASE_URL}/register"
            )
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["X-API-Key"] = token

    def query(self, path: str, **params) -> pd.DataFrame:
        """按原始路径调用任意端点（named 方法覆盖不到时的逃生口）。"""
        clean = {k: v for k, v in params.items() if v is not None}
        resp = self._session.get(self._base_url + path, params=clean,
                                 timeout=self._timeout)
        if resp.status_code == 429:
            retry = resp.headers.get("Retry-After")
            detail = _detail(resp)
            raise RateLimitError(detail, int(retry) if retry else None)
        if resp.status_code != 200:
            raise QuantSonarError(_detail(resp), resp.status_code)
        return pd.DataFrame(resp.json())

    def __getattr__(self, name: str):
        meta = ENDPOINTS.get(name)
        if meta is None:
            raise AttributeError(
                f"QuantSonar 没有接口 {name!r}，可用接口见 quantsonar.endpoints()")

        def _call(**params) -> pd.DataFrame:
            return self.query(meta["path"], **params)

        _call.__name__ = name
        _call.__doc__ = f"{meta['summary']}（GET {meta['path']}）"
        return _call

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(ENDPOINTS))


def _detail(resp) -> str:
    try:
        return resp.json().get("detail") or resp.json().get("error") or resp.text[:200]
    except Exception:
        return f"HTTP {resp.status_code}"


def endpoints() -> pd.DataFrame:
    """全部可用接口一览（方法名 / 路径 / 说明）。"""
    return pd.DataFrame(
        [{"method": k, "path": v["path"], "summary": v["summary"]}
         for k, v in ENDPOINTS.items()]
    )
