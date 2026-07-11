"""QuantSonar —— A 股量化数据 API 官方 Python SDK。

    import quantsonar as qs
    qs.set_token("qs_你的密钥")
    df = qs.daily(symbol="600519.SH", start_date="20260101")

文档：https://quantsonar.com/docs
"""
from ._endpoints import ENDPOINTS
from .client import (DEFAULT_BASE_URL, QuantSonar, QuantSonarError,
                     RateLimitError, endpoints)

__version__ = "0.1.0"
__all__ = ["QuantSonar", "QuantSonarError", "RateLimitError",
           "set_token", "endpoints", "ENDPOINTS"]

_default_client: QuantSonar | None = None


def set_token(token: str, base_url: str = DEFAULT_BASE_URL) -> QuantSonar:
    """设置默认 Key，之后可直接 qs.daily(...) 调用模块级方法。"""
    global _default_client
    _default_client = QuantSonar(token=token, base_url=base_url)
    return _default_client


def _require_client() -> QuantSonar:
    global _default_client
    if _default_client is None:
        # 未显式 set_token 时尝试环境变量（QuantSonar() 内部处理）
        _default_client = QuantSonar()
    return _default_client


def __getattr__(name: str):
    """模块级转发：qs.daily(...) == qs 默认客户端的 daily(...)。"""
    if name in ENDPOINTS or name == "query":
        return getattr(_require_client(), name)
    raise AttributeError(f"module 'quantsonar' has no attribute {name!r}")


def __dir__():
    return sorted(list(globals()) + list(ENDPOINTS) + ["query"])
