# QuantSonar Python SDK

[![tests](https://github.com/QuantSonar/quantsonar-python/actions/workflows/tests.yml/badge.svg)](https://github.com/QuantSonar/quantsonar-python/actions/workflows/tests.yml) [![PyPI](https://img.shields.io/pypi/v/quantsonar)](https://pypi.org/project/quantsonar/)

[QuantSonar](https://quantsonar.com) 官方 Python SDK —— A 股行情、财务、资金流、筹码、龙虎榜，38 个数据接口，一个 API Key 全部拿到。

## 安装

```bash
pip install quantsonar
```

## 快速开始

```python
import quantsonar as qs

qs.set_token("qs_你的密钥")   # 免费注册: https://quantsonar.com/register

# 贵州茅台 2026 年以来的日线（返回 pandas.DataFrame）
df = qs.daily(symbol="600519.SH", start_date="20260101")

# 每日指标 / 财务 / 资金流 / 龙虎榜……全部同一姿势
qs.fundamentals(symbol="600519.SH", trade_date="20260710")
qs.income(symbol="600519.SH", period="20251231")
qs.moneyflow(trade_date="20260710")
qs.top_list(trade_date="20260710")

# 指数与外汇（命名对齐 Tushare 习惯）
qs.index_daily(symbol="000300.SH", start_date="20260101")
qs.fx_daily(start_date="20260101")

# 实时行情与快讯
qs.realtime(symbol="600519.SH,300750.SZ")
qs.news_flash(source="cls")
```

- Key 也可以放环境变量 `QUANTSONAR_TOKEN`，省去 `set_token`
- 全部接口一览：`qs.endpoints()`（方法名 / 路径 / 中文说明）
- 参数与返回字段和 [在线文档](https://quantsonar.com/docs) 一一对应；日期统一 `YYYYMMDD`，证券代码带交易所后缀（`600519.SH`）

## 错误处理

```python
from quantsonar import QuantSonarError, RateLimitError

try:
    df = qs.daily(symbol="600519.SH")
except RateLimitError as e:      # 超出限速（429）
    print(e, "建议等待:", e.retry_after, "秒")
except QuantSonarError as e:     # 其他错误，中文说明
    print(e.status, e)
```

## 多账号 / 自定义

```python
from quantsonar import QuantSonar

client = QuantSonar(token="qs_另一把密钥", timeout=60)
df = client.daily(symbol="000001.SZ", start_date="20260101")
```

## 定价

免费 100 次/天，无需信用卡。付费档全部数据不分级，只按调用量计费 —— [定价页](https://quantsonar.com/pricing)。
