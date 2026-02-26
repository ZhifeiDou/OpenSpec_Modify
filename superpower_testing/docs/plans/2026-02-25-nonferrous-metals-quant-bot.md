# A股有色金属多因子量化交易机器人 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a modular quantitative trading bot for A-share non-ferrous metals sector with multi-factor stock selection, backtesting, and daily signal generation.

**Architecture:** Modular Python package with separated data/factor/strategy/backtest/risk/signal layers. Config-driven via YAML. AKShare for data, Pandas for computation, Matplotlib for visualization.

**Tech Stack:** Python 3.10+, AKShare, Pandas, NumPy, PyYAML, Matplotlib, pytest

---

### Task 1: Project Scaffolding & Configuration

**Files:**
- Create: `requirements.txt`
- Create: `config/config.yaml`
- Create: `quant_bot/__init__.py`
- Create: `quant_bot/data/__init__.py`
- Create: `quant_bot/factors/__init__.py`
- Create: `quant_bot/strategy/__init__.py`
- Create: `quant_bot/backtest/__init__.py`
- Create: `quant_bot/risk/__init__.py`
- Create: `quant_bot/signal/__init__.py`
- Create: `quant_bot/utils/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```
akshare>=1.12.0
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0
matplotlib>=3.7.0
pytest>=7.0.0
```

**Step 2: Create config/config.yaml**

```yaml
stock_pool:
  sector: "有色金属"

factors:
  momentum:
    weight: 0.3
    lookback: 20
  value:
    weight: 0.3
  volatility:
    weight: 0.2
  quality:
    weight: 0.2

strategy:
  top_n: 5
  rebalance: "daily"

backtest:
  start_date: "2023-01-01"
  end_date: "2025-12-31"
  initial_capital: 1000000
  commission: 0.001
  slippage: 0.002

risk:
  max_position_pct: 0.3
  stop_loss_pct: 0.08
  take_profit_pct: 0.20

paths:
  data_cache: "data_cache"
  output: "output"
```

**Step 3: Create all __init__.py files**

All `__init__.py` files are empty initially.

**Step 4: Create directory structure**

```bash
mkdir -p data_cache output/signals output/reports tests
```

**Step 5: Install dependencies**

Run: `pip install -r requirements.txt`

**Step 6: Commit**

```bash
git add requirements.txt config/ quant_bot/ tests/
git commit -m "feat: project scaffolding with config and package structure"
```

---

### Task 2: Utils & Config Loader

**Files:**
- Create: `quant_bot/utils/helpers.py`
- Create: `tests/test_utils.py`

**Step 1: Write the failing test**

```python
# tests/test_utils.py
import os
import pytest
from quant_bot.utils.helpers import load_config, get_trade_dates


def test_load_config():
    config = load_config()
    assert "stock_pool" in config
    assert "factors" in config
    assert config["stock_pool"]["sector"] == "有色金属"
    assert config["strategy"]["top_n"] == 5


def test_load_config_custom_path():
    config = load_config("config/config.yaml")
    assert config["backtest"]["initial_capital"] == 1000000


def test_get_trade_dates():
    dates = get_trade_dates("2024-01-01", "2024-01-10")
    assert isinstance(dates, list)
    assert len(dates) > 0
    # All dates should be strings in YYYY-MM-DD format
    for d in dates:
        assert len(d) == 10
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_utils.py -v`
Expected: FAIL with ImportError

**Step 3: Write minimal implementation**

```python
# quant_bot/utils/helpers.py
import os
import logging
import yaml
import pandas as pd

logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load YAML configuration file."""
    if config_path is None:
        # Look for config relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, "config", "config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_trade_dates(start_date, end_date):
    """Get list of A-share trading dates between start and end."""
    import akshare as ak
    trade_cal = ak.tool_trade_date_hist_sina()
    trade_cal["trade_date"] = pd.to_datetime(trade_cal["trade_date"])
    mask = (trade_cal["trade_date"] >= start_date) & (trade_cal["trade_date"] <= end_date)
    dates = trade_cal.loc[mask, "trade_date"].dt.strftime("%Y-%m-%d").tolist()
    return dates


def setup_logging(level=logging.INFO):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_utils.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/utils/helpers.py tests/test_utils.py
git commit -m "feat: add config loader and utility functions"
```

---

### Task 3: Data Fetcher

**Files:**
- Create: `quant_bot/data/fetcher.py`
- Create: `tests/test_data_fetcher.py`

**Step 1: Write the failing test**

```python
# tests/test_data_fetcher.py
import pytest
import pandas as pd
from quant_bot.data.fetcher import DataFetcher


@pytest.fixture
def fetcher():
    return DataFetcher()


def test_get_sector_stocks(fetcher):
    """Test fetching non-ferrous metals sector stock list."""
    stocks = fetcher.get_sector_stocks("有色金属")
    assert isinstance(stocks, pd.DataFrame)
    assert len(stocks) > 0
    assert "code" in stocks.columns
    assert "name" in stocks.columns


def test_get_stock_daily(fetcher):
    """Test fetching daily kline data for a stock."""
    # 紫金矿业
    df = fetcher.get_stock_daily("601899", "20240101", "20240201")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in ["date", "open", "high", "low", "close", "volume"]:
        assert col in df.columns


def test_get_stock_valuation(fetcher):
    """Test fetching valuation data (PE, PB)."""
    df = fetcher.get_stock_valuation("601899")
    assert isinstance(df, pd.DataFrame)
    # Should have some valuation fields
    assert len(df.columns) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_data_fetcher.py -v`
Expected: FAIL with ImportError

**Step 3: Write minimal implementation**

```python
# quant_bot/data/fetcher.py
import logging
import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch A-share data from AKShare."""

    def get_sector_stocks(self, sector_name="有色金属"):
        """Get stock list for a sector (板块成分股)."""
        try:
            df = ak.stock_board_industry_cons_em(symbol=sector_name)
            result = df[["代码", "名称"]].copy()
            result.columns = ["code", "name"]
            logger.info(f"Fetched {len(result)} stocks for sector: {sector_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch sector stocks: {e}")
            raise

    def get_stock_daily(self, stock_code, start_date, end_date):
        """Get daily kline data for a stock."""
        try:
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",  # 前复权
            )
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "换手率": "turnover",
            })
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            logger.info(f"Fetched {len(df)} daily bars for {stock_code}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch daily data for {stock_code}: {e}")
            raise

    def get_stock_valuation(self, stock_code):
        """Get valuation indicators (PE, PB, etc.) for a stock."""
        try:
            df = ak.stock_a_indicator_lg(symbol=stock_code)
            df = df.rename(columns={
                "trade_date": "date",
                "pe": "pe",
                "pe_ttm": "pe_ttm",
                "pb": "pb",
                "ps": "ps",
                "ps_ttm": "ps_ttm",
                "dv_ratio": "dividend_yield",
                "dv_ttm": "dividend_yield_ttm",
                "total_mv": "total_mv",
            })
            logger.info(f"Fetched valuation data for {stock_code}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch valuation for {stock_code}: {e}")
            raise
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_data_fetcher.py -v`
Expected: PASS (requires network access to AKShare)

**Step 5: Commit**

```bash
git add quant_bot/data/fetcher.py tests/test_data_fetcher.py
git commit -m "feat: add AKShare data fetcher for sector stocks, klines, and valuations"
```

---

### Task 4: Data Cache

**Files:**
- Create: `quant_bot/data/cache.py`
- Create: `tests/test_cache.py`

**Step 1: Write the failing test**

```python
# tests/test_cache.py
import os
import pytest
import pandas as pd
from quant_bot.data.cache import DataCache


@pytest.fixture
def cache(tmp_path):
    return DataCache(cache_dir=str(tmp_path))


def test_save_and_load(cache):
    df = pd.DataFrame({"date": ["2024-01-02", "2024-01-03"], "close": [10.0, 11.0]})
    cache.save("test_stock", "daily", df)
    loaded = cache.load("test_stock", "daily")
    assert loaded is not None
    assert len(loaded) == 2
    assert loaded["close"].iloc[0] == 10.0


def test_load_missing(cache):
    result = cache.load("nonexistent", "daily")
    assert result is None


def test_is_cached(cache):
    df = pd.DataFrame({"a": [1]})
    assert not cache.is_cached("x", "daily")
    cache.save("x", "daily", df)
    assert cache.is_cached("x", "daily")
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_cache.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/data/cache.py
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataCache:
    """Local CSV cache for market data."""

    def __init__(self, cache_dir="data_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_path(self, key, data_type):
        return os.path.join(self.cache_dir, f"{key}_{data_type}.csv")

    def is_cached(self, key, data_type):
        return os.path.exists(self._get_path(key, data_type))

    def save(self, key, data_type, df):
        path = self._get_path(key, data_type)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        logger.debug(f"Cached {key}/{data_type} -> {path}")

    def load(self, key, data_type):
        path = self._get_path(key, data_type)
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, encoding="utf-8-sig")
        logger.debug(f"Loaded cache {key}/{data_type} from {path}")
        return df
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_cache.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/data/cache.py tests/test_cache.py
git commit -m "feat: add local CSV data cache"
```

---

### Task 5: Data Processor

**Files:**
- Create: `quant_bot/data/processor.py`
- Create: `tests/test_processor.py`

**Step 1: Write the failing test**

```python
# tests/test_processor.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.data.processor import DataProcessor


@pytest.fixture
def processor():
    return DataProcessor()


def test_clean_daily_data(processor):
    df = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "open": [10.0, np.nan, 12.0, 13.0],
        "close": [10.5, 11.0, 12.5, 13.5],
        "high": [11.0, 11.5, 13.0, 14.0],
        "low": [9.5, 10.5, 12.0, 13.0],
        "volume": [1000, 0, 1500, 2000],  # volume=0 means suspended
    })
    cleaned = processor.clean_daily_data(df)
    # Suspended day (volume=0) should be removed
    assert len(cleaned) == 3
    # NaN should be forward-filled or removed
    assert not cleaned["open"].isna().any()


def test_merge_stock_data(processor):
    daily = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03"],
        "close": [10.0, 11.0],
    })
    valuation = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03"],
        "pe_ttm": [15.0, 16.0],
        "pb": [2.0, 2.1],
    })
    merged = processor.merge_stock_data(daily, valuation)
    assert "close" in merged.columns
    assert "pe_ttm" in merged.columns
    assert len(merged) == 2
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_processor.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/data/processor.py
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataProcessor:
    """Clean and preprocess market data."""

    def clean_daily_data(self, df):
        """Remove suspended days and handle missing values."""
        df = df.copy()
        # Remove rows where volume is 0 (suspended)
        if "volume" in df.columns:
            df = df[df["volume"] > 0]
        # Forward-fill then back-fill remaining NaN
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].ffill().bfill()
        # Drop any remaining rows with NaN
        df = df.dropna(subset=["close"])
        df = df.reset_index(drop=True)
        logger.debug(f"Cleaned data: {len(df)} rows remaining")
        return df

    def merge_stock_data(self, daily_df, valuation_df):
        """Merge daily price data with valuation data on date."""
        daily_df = daily_df.copy()
        valuation_df = valuation_df.copy()
        daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.strftime("%Y-%m-%d")
        valuation_df["date"] = pd.to_datetime(valuation_df["date"]).dt.strftime("%Y-%m-%d")
        merged = pd.merge(daily_df, valuation_df, on="date", how="left", suffixes=("", "_val"))
        merged = merged.ffill()
        logger.debug(f"Merged data: {len(merged)} rows")
        return merged
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_processor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/data/processor.py tests/test_processor.py
git commit -m "feat: add data processor for cleaning and merging"
```

---

### Task 6: Factor Base Class & Momentum Factor

**Files:**
- Create: `quant_bot/factors/base.py`
- Create: `quant_bot/factors/momentum.py`
- Create: `tests/test_factors_momentum.py`

**Step 1: Write the failing test**

```python
# tests/test_factors_momentum.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor
from quant_bot.factors.momentum import MomentumFactor


def make_price_df(n=30):
    """Create sample price DataFrame."""
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    np.random.seed(42)
    prices = 10 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "close": prices,
        "high": prices + 0.5,
        "low": prices - 0.5,
    })


def test_base_factor_interface():
    """BaseFactor should require calculate() implementation."""
    with pytest.raises(TypeError):
        BaseFactor()


def test_return_n(make_df=make_price_df):
    df = make_df(30)
    factor = MomentumFactor(lookback=20)
    result = factor.calculate(df)
    assert "return_n" in result.columns
    assert len(result) == len(df)
    # First `lookback` values should be NaN
    assert result["return_n"].iloc[:20].isna().all()
    # Later values should be numeric
    assert not result["return_n"].iloc[20:].isna().any()


def test_rsi(make_df=make_price_df):
    df = make_df(30)
    factor = MomentumFactor(lookback=14)
    result = factor.calculate(df)
    assert "rsi" in result.columns
    # RSI should be between 0 and 100
    valid_rsi = result["rsi"].dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_factors_momentum.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/factors/base.py
from abc import ABC, abstractmethod
import pandas as pd


class BaseFactor(ABC):
    """Abstract base class for all factors."""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate factor values. Returns DataFrame with factor columns added."""
        pass

    @staticmethod
    def zscore_normalize(series: pd.Series) -> pd.Series:
        """Cross-sectional z-score normalization."""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return series * 0
        return (series - mean) / std
```

```python
# quant_bot/factors/momentum.py
import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class MomentumFactor(BaseFactor):
    """Momentum factors: N-day return, RSI, price position."""

    def __init__(self, lookback=20):
        self.lookback = lookback

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        close = result["close"]

        # N-day return
        result["return_n"] = close.pct_change(self.lookback)

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.lookback, min_periods=self.lookback).mean()
        avg_loss = loss.rolling(window=self.lookback, min_periods=self.lookback).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        result["rsi"] = 100 - (100 / (1 + rs))

        # Price position: where current price sits in N-day range [0, 1]
        rolling_high = result["high"].rolling(window=self.lookback, min_periods=self.lookback).max()
        rolling_low = result["low"].rolling(window=self.lookback, min_periods=self.lookback).min()
        denom = rolling_high - rolling_low
        result["price_position"] = (close - rolling_low) / denom.replace(0, np.nan)

        return result
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_factors_momentum.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/factors/base.py quant_bot/factors/momentum.py tests/test_factors_momentum.py
git commit -m "feat: add factor base class and momentum factor"
```

---

### Task 7: Value Factor

**Files:**
- Create: `quant_bot/factors/value.py`
- Create: `tests/test_factors_value.py`

**Step 1: Write the failing test**

```python
# tests/test_factors_value.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.value import ValueFactor


def test_value_factor():
    df = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "close": [10, 11, 12],
        "pe_ttm": [15.0, 20.0, 10.0],
        "pb": [2.0, 3.0, 1.5],
        "dividend_yield_ttm": [2.5, 1.0, 3.0],
    })
    factor = ValueFactor()
    result = factor.calculate(df)
    assert "ep_ratio" in result.columns  # earnings/price = 1/PE
    assert "bp_ratio" in result.columns  # book/price = 1/PB
    assert "div_yield" in result.columns
    # Lower PE -> higher ep_ratio
    assert result["ep_ratio"].iloc[2] > result["ep_ratio"].iloc[1]


def test_value_factor_handles_zero_pe():
    df = pd.DataFrame({
        "date": ["2024-01-02"],
        "close": [10],
        "pe_ttm": [0.0],
        "pb": [2.0],
        "dividend_yield_ttm": [1.0],
    })
    factor = ValueFactor()
    result = factor.calculate(df)
    # Should handle zero PE gracefully
    assert not np.isinf(result["ep_ratio"].iloc[0])
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_factors_value.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/factors/value.py
import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class ValueFactor(BaseFactor):
    """Value factors: EP ratio (1/PE), BP ratio (1/PB), dividend yield."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()

        # Earnings/Price ratio (inverse of PE, higher is cheaper)
        pe = result.get("pe_ttm", pd.Series(dtype=float))
        result["ep_ratio"] = np.where(pe != 0, 1.0 / pe.replace(0, np.nan), 0)
        result["ep_ratio"] = result["ep_ratio"].fillna(0)

        # Book/Price ratio (inverse of PB)
        pb = result.get("pb", pd.Series(dtype=float))
        result["bp_ratio"] = np.where(pb != 0, 1.0 / pb.replace(0, np.nan), 0)
        result["bp_ratio"] = result["bp_ratio"].fillna(0)

        # Dividend yield
        result["div_yield"] = result.get("dividend_yield_ttm", pd.Series(0, index=result.index)).fillna(0)

        return result
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_factors_value.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/factors/value.py tests/test_factors_value.py
git commit -m "feat: add value factor (EP, BP, dividend yield)"
```

---

### Task 8: Volatility Factor

**Files:**
- Create: `quant_bot/factors/volatility.py`
- Create: `tests/test_factors_volatility.py`

**Step 1: Write the failing test**

```python
# tests/test_factors_volatility.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.volatility import VolatilityFactor


def make_price_df(n=30):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    np.random.seed(42)
    prices = 10 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "close": prices,
        "high": prices + abs(np.random.randn(n) * 0.3),
        "low": prices - abs(np.random.randn(n) * 0.3),
    })


def test_hist_volatility():
    df = make_price_df(30)
    factor = VolatilityFactor(lookback=20)
    result = factor.calculate(df)
    assert "hist_volatility" in result.columns
    valid = result["hist_volatility"].dropna()
    assert len(valid) > 0
    assert (valid >= 0).all()


def test_atr():
    df = make_price_df(30)
    factor = VolatilityFactor(lookback=14)
    result = factor.calculate(df)
    assert "atr" in result.columns
    valid = result["atr"].dropna()
    assert len(valid) > 0
    assert (valid >= 0).all()
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_factors_volatility.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/factors/volatility.py
import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class VolatilityFactor(BaseFactor):
    """Volatility factors: historical volatility, ATR. Lower volatility scores higher."""

    def __init__(self, lookback=20):
        self.lookback = lookback

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        close = result["close"]

        # Historical volatility (annualized std of log returns)
        log_ret = np.log(close / close.shift(1))
        result["hist_volatility"] = log_ret.rolling(window=self.lookback, min_periods=self.lookback).std() * np.sqrt(252)

        # ATR (Average True Range)
        high = result["high"]
        low = result["low"]
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        result["atr"] = tr.rolling(window=self.lookback, min_periods=self.lookback).mean()

        return result
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_factors_volatility.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/factors/volatility.py tests/test_factors_volatility.py
git commit -m "feat: add volatility factor (historical vol, ATR)"
```

---

### Task 9: Quality Factor

**Files:**
- Create: `quant_bot/factors/quality.py`
- Create: `tests/test_factors_quality.py`

**Step 1: Write the failing test**

```python
# tests/test_factors_quality.py
import pytest
import pandas as pd
from quant_bot.factors.quality import QualityFactor


def test_quality_factor():
    df = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "close": [10, 11, 12],
        "roe": [15.0, 20.0, 10.0],
        "gross_margin": [30.0, 25.0, 35.0],
    })
    factor = QualityFactor()
    result = factor.calculate(df)
    assert "roe_score" in result.columns
    assert "gross_margin_score" in result.columns


def test_quality_factor_missing_columns():
    """Should handle missing fundamental columns gracefully."""
    df = pd.DataFrame({
        "date": ["2024-01-02"],
        "close": [10],
    })
    factor = QualityFactor()
    result = factor.calculate(df)
    assert "roe_score" in result.columns
    assert result["roe_score"].iloc[0] == 0
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_factors_quality.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/factors/quality.py
import pandas as pd
from quant_bot.factors.base import BaseFactor


class QualityFactor(BaseFactor):
    """Quality factors: ROE, gross margin."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["roe_score"] = result.get("roe", pd.Series(0, index=result.index)).fillna(0)
        result["gross_margin_score"] = result.get("gross_margin", pd.Series(0, index=result.index)).fillna(0)
        return result
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_factors_quality.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/factors/quality.py tests/test_factors_quality.py
git commit -m "feat: add quality factor (ROE, gross margin)"
```

---

### Task 10: Multi-Factor Strategy Engine

**Files:**
- Create: `quant_bot/strategy/multi_factor.py`
- Create: `tests/test_strategy.py`

**Step 1: Write the failing test**

```python
# tests/test_strategy.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.strategy.multi_factor import MultiFactorStrategy


@pytest.fixture
def config():
    return {
        "factors": {
            "momentum": {"weight": 0.3, "lookback": 20},
            "value": {"weight": 0.3},
            "volatility": {"weight": 0.2},
            "quality": {"weight": 0.2},
        },
        "strategy": {"top_n": 2, "rebalance": "daily"},
    }


def test_score_stocks(config):
    """Test cross-sectional scoring of stocks."""
    # Simulate factor data for 3 stocks on one date
    stocks_data = {
        "stock_A": {"return_n": 0.1, "ep_ratio": 0.05, "hist_volatility": 0.2, "roe_score": 15},
        "stock_B": {"return_n": 0.2, "ep_ratio": 0.08, "hist_volatility": 0.3, "roe_score": 20},
        "stock_C": {"return_n": -0.05, "ep_ratio": 0.03, "hist_volatility": 0.15, "roe_score": 10},
    }
    strategy = MultiFactorStrategy(config)
    scores = strategy.score_stocks(stocks_data)
    assert isinstance(scores, dict)
    assert len(scores) == 3
    # All scores should be numeric
    for s in scores.values():
        assert isinstance(s, (int, float))


def test_select_top_n(config):
    strategy = MultiFactorStrategy(config)
    scores = {"A": 0.8, "B": 0.5, "C": 0.9, "D": 0.3}
    selected = strategy.select_top_n(scores)
    assert len(selected) == 2  # top_n=2
    assert "C" in selected
    assert "A" in selected


def test_generate_target_positions(config):
    strategy = MultiFactorStrategy(config)
    selected = ["A", "B"]
    positions = strategy.generate_target_positions(selected)
    assert len(positions) == 2
    assert abs(sum(positions.values()) - 1.0) < 1e-6  # equal weight sums to 1
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_strategy.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/strategy/multi_factor.py
import logging
import numpy as np
from quant_bot.factors.base import BaseFactor

logger = logging.getLogger(__name__)


class MultiFactorStrategy:
    """Multi-factor stock selection strategy with cross-sectional scoring."""

    # Map factor group -> (factor columns, direction)
    # direction=1 means higher is better, -1 means lower is better
    FACTOR_COLUMNS = {
        "momentum": ([("return_n", 1), ("rsi", -1), ("price_position", 1)]),
        "value": ([("ep_ratio", 1), ("bp_ratio", 1), ("div_yield", 1)]),
        "volatility": ([("hist_volatility", -1), ("atr", -1)]),
        "quality": ([("roe_score", 1), ("gross_margin_score", 1)]),
    }

    def __init__(self, config):
        self.factor_weights = {k: v.get("weight", 0.25) for k, v in config["factors"].items()}
        self.top_n = config["strategy"]["top_n"]

    def score_stocks(self, stocks_data):
        """Score stocks cross-sectionally using multi-factor model.

        Args:
            stocks_data: dict of {stock_code: {factor_col: value, ...}}

        Returns:
            dict of {stock_code: composite_score}
        """
        codes = list(stocks_data.keys())
        if not codes:
            return {}

        # Collect all factor values per group, z-score normalize, then weight
        composite_scores = {code: 0.0 for code in codes}

        for group_name, factor_cols in self.FACTOR_COLUMNS.items():
            group_weight = self.factor_weights.get(group_name, 0)
            if group_weight == 0:
                continue

            for col_name, direction in factor_cols:
                values = []
                for code in codes:
                    val = stocks_data[code].get(col_name)
                    values.append(val if val is not None else np.nan)

                values = np.array(values, dtype=float)
                valid_mask = ~np.isnan(values)

                if valid_mask.sum() < 2:
                    continue

                # Z-score normalize
                mean = np.nanmean(values)
                std = np.nanstd(values)
                if std == 0:
                    continue
                z_scores = (values - mean) / std * direction

                # Weight by group weight, divided evenly among columns in group
                col_weight = group_weight / len(factor_cols)
                for i, code in enumerate(codes):
                    if valid_mask[i]:
                        composite_scores[code] += z_scores[i] * col_weight

        return composite_scores

    def select_top_n(self, scores):
        """Select top N stocks by composite score."""
        sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected = [code for code, _ in sorted_stocks[:self.top_n]]
        logger.info(f"Selected top {self.top_n}: {selected}")
        return selected

    def generate_target_positions(self, selected_stocks):
        """Generate equal-weight target positions."""
        if not selected_stocks:
            return {}
        weight = 1.0 / len(selected_stocks)
        return {code: weight for code in selected_stocks}
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_strategy.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/strategy/multi_factor.py tests/test_strategy.py
git commit -m "feat: add multi-factor strategy engine with scoring and selection"
```

---

### Task 11: Risk Manager

**Files:**
- Create: `quant_bot/risk/manager.py`
- Create: `tests/test_risk.py`

**Step 1: Write the failing test**

```python
# tests/test_risk.py
import pytest
from quant_bot.risk.manager import RiskManager


@pytest.fixture
def risk_config():
    return {
        "risk": {
            "max_position_pct": 0.3,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.20,
        }
    }


def test_check_position_limit(risk_config):
    rm = RiskManager(risk_config)
    positions = {"A": 0.5, "B": 0.3, "C": 0.2}
    adjusted = rm.check_position_limits(positions)
    # A exceeds 30% limit, should be capped
    assert adjusted["A"] <= 0.3


def test_check_stop_loss(risk_config):
    rm = RiskManager(risk_config)
    # Stock dropped 10% from buy price
    holdings = {"A": {"buy_price": 10.0, "current_price": 9.0}}
    signals = rm.check_stop_loss(holdings)
    assert "A" in signals  # should trigger stop loss


def test_no_stop_loss_if_within_threshold(risk_config):
    rm = RiskManager(risk_config)
    holdings = {"A": {"buy_price": 10.0, "current_price": 9.5}}
    signals = rm.check_stop_loss(holdings)
    assert "A" not in signals  # 5% loss, below 8% threshold


def test_check_take_profit(risk_config):
    rm = RiskManager(risk_config)
    holdings = {"A": {"buy_price": 10.0, "current_price": 12.5}}
    signals = rm.check_take_profit(holdings)
    assert "A" in signals  # 25% gain, above 20% threshold
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_risk.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/risk/manager.py
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Portfolio risk management: position limits, stop-loss, take-profit."""

    def __init__(self, config):
        risk_cfg = config.get("risk", {})
        self.max_position_pct = risk_cfg.get("max_position_pct", 0.3)
        self.stop_loss_pct = risk_cfg.get("stop_loss_pct", 0.08)
        self.take_profit_pct = risk_cfg.get("take_profit_pct", 0.20)

    def check_position_limits(self, target_positions):
        """Cap any position exceeding max_position_pct, redistribute excess equally."""
        adjusted = dict(target_positions)
        excess = 0.0
        uncapped = []

        for code, weight in adjusted.items():
            if weight > self.max_position_pct:
                excess += weight - self.max_position_pct
                adjusted[code] = self.max_position_pct
            else:
                uncapped.append(code)

        # Redistribute excess to uncapped positions
        if uncapped and excess > 0:
            extra_per = excess / len(uncapped)
            for code in uncapped:
                adjusted[code] = min(adjusted[code] + extra_per, self.max_position_pct)

        logger.debug(f"Position limits applied: {adjusted}")
        return adjusted

    def check_stop_loss(self, holdings):
        """Return set of stock codes that trigger stop-loss."""
        triggered = set()
        for code, info in holdings.items():
            buy_price = info["buy_price"]
            current_price = info["current_price"]
            loss_pct = (buy_price - current_price) / buy_price
            if loss_pct >= self.stop_loss_pct:
                logger.warning(f"Stop-loss triggered for {code}: loss={loss_pct:.2%}")
                triggered.add(code)
        return triggered

    def check_take_profit(self, holdings):
        """Return set of stock codes that trigger take-profit."""
        triggered = set()
        for code, info in holdings.items():
            buy_price = info["buy_price"]
            current_price = info["current_price"]
            gain_pct = (current_price - buy_price) / buy_price
            if gain_pct >= self.take_profit_pct:
                logger.info(f"Take-profit triggered for {code}: gain={gain_pct:.2%}")
                triggered.add(code)
        return triggered
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_risk.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/risk/manager.py tests/test_risk.py
git commit -m "feat: add risk manager with position limits, stop-loss, take-profit"
```

---

### Task 12: Signal Generator

**Files:**
- Create: `quant_bot/signal/generator.py`
- Create: `tests/test_signal.py`

**Step 1: Write the failing test**

```python
# tests/test_signal.py
import os
import pytest
from quant_bot.signal.generator import SignalGenerator


@pytest.fixture
def generator(tmp_path):
    return SignalGenerator(output_dir=str(tmp_path))


def test_generate_signals(generator):
    current_holdings = {"601899": 0.5}
    target_positions = {"601899": 0.3, "600489": 0.35, "603799": 0.35}
    stock_names = {"601899": "紫金矿业", "600489": "中金黄金", "603799": "华友钴业"}
    scores = {"601899": 0.7, "600489": 0.9, "603799": 0.8}

    signals = generator.generate_signals(
        date="2024-06-01",
        current_holdings=current_holdings,
        target_positions=target_positions,
        stock_names=stock_names,
        scores=scores,
    )
    assert len(signals) == 3
    # 601899: reduce position (0.5 -> 0.3) = "减仓"
    s_601899 = [s for s in signals if s["code"] == "601899"][0]
    assert s_601899["action"] in ["减仓", "卖出"]
    # 600489: new position = "买入"
    s_600489 = [s for s in signals if s["code"] == "600489"][0]
    assert s_600489["action"] == "买入"


def test_save_signals_to_csv(generator):
    signals = [
        {"date": "2024-06-01", "code": "601899", "name": "紫金矿业",
         "action": "买入", "target_weight": 0.5, "score": 0.8},
    ]
    generator.save_to_csv(signals, "2024-06-01")
    files = os.listdir(generator.output_dir)
    assert any("2024-06-01" in f for f in files)
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_signal.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/signal/generator.py
import os
import csv
import logging

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generate and output trading signals."""

    def __init__(self, output_dir="output/signals"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_signals(self, date, current_holdings, target_positions, stock_names, scores):
        """Compare current vs target positions to generate buy/sell signals."""
        signals = []
        all_codes = set(list(current_holdings.keys()) + list(target_positions.keys()))

        for code in all_codes:
            current_w = current_holdings.get(code, 0)
            target_w = target_positions.get(code, 0)
            name = stock_names.get(code, code)
            score = scores.get(code, 0)

            if target_w > 0 and current_w == 0:
                action = "买入"
            elif target_w == 0 and current_w > 0:
                action = "卖出"
            elif target_w > current_w:
                action = "加仓"
            elif target_w < current_w:
                action = "减仓"
            else:
                action = "持有"

            signals.append({
                "date": date,
                "code": code,
                "name": name,
                "action": action,
                "target_weight": round(target_w, 4),
                "score": round(score, 4),
            })

        # Log signals
        for s in signals:
            logger.info(f"[{s['date']}] {s['code']} {s['name']} -> {s['action']} "
                        f"(target: {s['target_weight']:.2%}, score: {s['score']:.4f})")

        return signals

    def save_to_csv(self, signals, date):
        """Save signals to CSV file."""
        filename = os.path.join(self.output_dir, f"signals_{date}.csv")
        fieldnames = ["date", "code", "name", "action", "target_weight", "score"]
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(signals)
        logger.info(f"Signals saved to {filename}")
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_signal.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/signal/generator.py tests/test_signal.py
git commit -m "feat: add signal generator with CSV output"
```

---

### Task 13: Backtest Engine

**Files:**
- Create: `quant_bot/backtest/engine.py`
- Create: `tests/test_backtest.py`

**Step 1: Write the failing test**

```python
# tests/test_backtest.py
import pytest
import pandas as pd
import numpy as np
from quant_bot.backtest.engine import BacktestEngine


@pytest.fixture
def config():
    return {
        "factors": {
            "momentum": {"weight": 0.3, "lookback": 5},
            "value": {"weight": 0.3},
            "volatility": {"weight": 0.2},
            "quality": {"weight": 0.2},
        },
        "strategy": {"top_n": 2, "rebalance": "daily"},
        "backtest": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "initial_capital": 1000000,
            "commission": 0.001,
            "slippage": 0.002,
        },
        "risk": {
            "max_position_pct": 0.5,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.20,
        },
    }


def make_mock_stock_data():
    """Create mock daily data for 3 stocks over 20 days."""
    dates = pd.date_range("2024-01-02", periods=20, freq="B")
    np.random.seed(42)
    stocks = {}
    for code in ["STOCK_A", "STOCK_B", "STOCK_C"]:
        prices = 10 + np.cumsum(np.random.randn(20) * 0.3)
        stocks[code] = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "open": prices + np.random.randn(20) * 0.1,
            "close": prices,
            "high": prices + abs(np.random.randn(20) * 0.2),
            "low": prices - abs(np.random.randn(20) * 0.2),
            "volume": np.random.randint(1000, 10000, 20),
            "pe_ttm": np.random.uniform(8, 25, 20),
            "pb": np.random.uniform(1, 4, 20),
            "dividend_yield_ttm": np.random.uniform(0, 3, 20),
            "roe": np.random.uniform(5, 25, 20),
            "gross_margin": np.random.uniform(15, 40, 20),
        })
    return stocks


def test_backtest_runs(config):
    engine = BacktestEngine(config)
    stocks_data = make_mock_stock_data()
    stock_names = {"STOCK_A": "A", "STOCK_B": "B", "STOCK_C": "C"}
    result = engine.run(stocks_data, stock_names)
    assert "portfolio_values" in result
    assert "metrics" in result
    assert len(result["portfolio_values"]) > 0


def test_backtest_metrics(config):
    engine = BacktestEngine(config)
    stocks_data = make_mock_stock_data()
    stock_names = {"STOCK_A": "A", "STOCK_B": "B", "STOCK_C": "C"}
    result = engine.run(stocks_data, stock_names)
    metrics = result["metrics"]
    assert "annual_return" in metrics
    assert "max_drawdown" in metrics
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
```

**Step 2: Run test to verify it fails**

Run: `cd superpower_testing && python -m pytest tests/test_backtest.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# quant_bot/backtest/engine.py
import logging
import numpy as np
import pandas as pd
from quant_bot.factors.momentum import MomentumFactor
from quant_bot.factors.value import ValueFactor
from quant_bot.factors.volatility import VolatilityFactor
from quant_bot.factors.quality import QualityFactor
from quant_bot.strategy.multi_factor import MultiFactorStrategy
from quant_bot.risk.manager import RiskManager

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtesting engine: iterate over trading days, simulate portfolio."""

    def __init__(self, config):
        self.config = config
        self.initial_capital = config["backtest"]["initial_capital"]
        self.commission = config["backtest"]["commission"]
        self.slippage = config["backtest"]["slippage"]
        self.strategy = MultiFactorStrategy(config)
        self.risk_manager = RiskManager(config)

        lookback_m = config["factors"].get("momentum", {}).get("lookback", 20)
        lookback_v = config["factors"].get("volatility", {}).get("lookback", 20)
        self.factors = {
            "momentum": MomentumFactor(lookback=lookback_m),
            "value": ValueFactor(),
            "volatility": VolatilityFactor(lookback=lookback_v),
            "quality": QualityFactor(),
        }

    def _compute_factors_for_stock(self, df):
        """Apply all factors to a stock's DataFrame, return latest factor values."""
        result = df.copy()
        for factor in self.factors.values():
            result = factor.calculate(result)
        return result

    def run(self, stocks_data, stock_names):
        """Run backtest.

        Args:
            stocks_data: dict of {stock_code: DataFrame with columns date,open,close,high,low,volume,...}
            stock_names: dict of {stock_code: stock_name}

        Returns:
            dict with portfolio_values (list), trades (list), metrics (dict)
        """
        # Compute factors for all stocks
        factor_data = {}
        for code, df in stocks_data.items():
            factor_data[code] = self._compute_factors_for_stock(df)

        # Get common trading dates
        all_dates = set()
        for df in factor_data.values():
            all_dates.update(df["date"].tolist())
        dates = sorted(all_dates)

        # Portfolio state
        cash = self.initial_capital
        holdings = {}  # {code: {"shares": int, "buy_price": float}}
        portfolio_values = []
        trades = []
        daily_returns = []

        for i, date in enumerate(dates):
            # Get current prices
            current_prices = {}
            for code, df in factor_data.items():
                row = df[df["date"] == date]
                if not row.empty:
                    current_prices[code] = row["close"].values[0]

            # Calculate portfolio value
            holdings_value = sum(
                holdings[c]["shares"] * current_prices.get(c, 0)
                for c in holdings if c in current_prices
            )
            total_value = cash + holdings_value
            portfolio_values.append({"date": date, "value": total_value})

            if len(portfolio_values) > 1:
                prev_val = portfolio_values[-2]["value"]
                daily_ret = (total_value - prev_val) / prev_val if prev_val > 0 else 0
                daily_returns.append(daily_ret)

            # Risk checks: stop-loss / take-profit
            if holdings:
                risk_holdings = {
                    c: {"buy_price": h["buy_price"], "current_price": current_prices.get(c, h["buy_price"])}
                    for c, h in holdings.items() if c in current_prices
                }
                stop_loss_codes = self.risk_manager.check_stop_loss(risk_holdings)
                take_profit_codes = self.risk_manager.check_take_profit(risk_holdings)
                force_sell = stop_loss_codes | take_profit_codes

                for code in force_sell:
                    if code in holdings and code in current_prices:
                        sell_price = current_prices[code] * (1 - self.slippage)
                        proceeds = holdings[code]["shares"] * sell_price
                        proceeds -= proceeds * self.commission
                        cash += proceeds
                        trades.append({"date": date, "code": code, "action": "止损/止盈卖出",
                                       "price": sell_price, "shares": holdings[code]["shares"]})
                        del holdings[code]

            # Strategy: score and select stocks
            stocks_factor_snapshot = {}
            for code, df in factor_data.items():
                row = df[df["date"] == date]
                if row.empty:
                    continue
                row_dict = row.iloc[0].to_dict()
                # Check if we have enough factor data (not all NaN)
                if pd.notna(row_dict.get("return_n")):
                    stocks_factor_snapshot[code] = row_dict

            if len(stocks_factor_snapshot) < 2:
                continue

            scores = self.strategy.score_stocks(stocks_factor_snapshot)
            selected = self.strategy.select_top_n(scores)
            target_positions = self.strategy.generate_target_positions(selected)
            target_positions = self.risk_manager.check_position_limits(target_positions)

            # Rebalance: sell positions not in target
            for code in list(holdings.keys()):
                if code not in target_positions and code in current_prices:
                    sell_price = current_prices[code] * (1 - self.slippage)
                    proceeds = holdings[code]["shares"] * sell_price
                    proceeds -= proceeds * self.commission
                    cash += proceeds
                    trades.append({"date": date, "code": code, "action": "卖出",
                                   "price": sell_price, "shares": holdings[code]["shares"]})
                    del holdings[code]

            # Buy target positions
            for code, weight in target_positions.items():
                if code not in current_prices:
                    continue
                target_value = total_value * weight
                current_value = holdings.get(code, {}).get("shares", 0) * current_prices[code]
                diff = target_value - current_value

                if diff > current_prices[code]:  # Buy
                    buy_price = current_prices[code] * (1 + self.slippage)
                    shares_to_buy = int(diff / buy_price / 100) * 100  # Round to 100 shares
                    if shares_to_buy > 0:
                        cost = shares_to_buy * buy_price * (1 + self.commission)
                        if cost <= cash:
                            cash -= cost
                            existing_shares = holdings.get(code, {}).get("shares", 0)
                            holdings[code] = {
                                "shares": existing_shares + shares_to_buy,
                                "buy_price": buy_price,
                            }
                            trades.append({"date": date, "code": code, "action": "买入",
                                           "price": buy_price, "shares": shares_to_buy})

        # Calculate metrics
        metrics = self._calculate_metrics(portfolio_values, daily_returns)

        return {
            "portfolio_values": portfolio_values,
            "trades": trades,
            "metrics": metrics,
        }

    def _calculate_metrics(self, portfolio_values, daily_returns):
        """Calculate backtest performance metrics."""
        if len(portfolio_values) < 2:
            return {"annual_return": 0, "max_drawdown": 0, "sharpe_ratio": 0, "win_rate": 0}

        values = [pv["value"] for pv in portfolio_values]
        total_return = (values[-1] - values[0]) / values[0]
        n_days = len(values)
        annual_return = (1 + total_return) ** (252 / max(n_days, 1)) - 1

        # Max drawdown
        peak = values[0]
        max_dd = 0
        for v in values:
            peak = max(peak, v)
            dd = (peak - v) / peak
            max_dd = max(max_dd, dd)

        # Sharpe ratio (annualized)
        if daily_returns:
            avg_ret = np.mean(daily_returns)
            std_ret = np.std(daily_returns)
            sharpe = (avg_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0
        else:
            sharpe = 0

        # Win rate (% of positive daily returns)
        if daily_returns:
            win_rate = sum(1 for r in daily_returns if r > 0) / len(daily_returns)
        else:
            win_rate = 0

        metrics = {
            "total_return": round(total_return, 4),
            "annual_return": round(annual_return, 4),
            "max_drawdown": round(max_dd, 4),
            "sharpe_ratio": round(sharpe, 4),
            "win_rate": round(win_rate, 4),
            "total_trades": len(daily_returns),
        }
        logger.info(f"Backtest metrics: {metrics}")
        return metrics
```

**Step 4: Run test to verify it passes**

Run: `cd superpower_testing && python -m pytest tests/test_backtest.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add quant_bot/backtest/engine.py tests/test_backtest.py
git commit -m "feat: add backtest engine with portfolio simulation and metrics"
```

---

### Task 14: Main Entry Point

**Files:**
- Create: `quant_bot/main.py`

**Step 1: Write the main entry point**

```python
# quant_bot/main.py
"""
A股有色金属多因子量化交易机器人 - 主入口

Usage:
    python -m quant_bot.main --mode backtest
    python -m quant_bot.main --mode simulate
    python -m quant_bot.main --mode signal
"""
import argparse
import logging
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from quant_bot.utils.helpers import load_config, setup_logging
from quant_bot.data.fetcher import DataFetcher
from quant_bot.data.cache import DataCache
from quant_bot.data.processor import DataProcessor
from quant_bot.factors.momentum import MomentumFactor
from quant_bot.factors.value import ValueFactor
from quant_bot.factors.volatility import VolatilityFactor
from quant_bot.factors.quality import QualityFactor
from quant_bot.strategy.multi_factor import MultiFactorStrategy
from quant_bot.backtest.engine import BacktestEngine
from quant_bot.risk.manager import RiskManager
from quant_bot.signal.generator import SignalGenerator

logger = logging.getLogger(__name__)


def fetch_all_data(config):
    """Fetch and cache data for all sector stocks."""
    fetcher = DataFetcher()
    cache = DataCache(config.get("paths", {}).get("data_cache", "data_cache"))
    processor = DataProcessor()

    sector = config["stock_pool"]["sector"]
    logger.info(f"Fetching stock list for sector: {sector}")
    stocks_df = fetcher.get_sector_stocks(sector)
    stock_codes = stocks_df["code"].tolist()
    stock_names = dict(zip(stocks_df["code"], stocks_df["name"]))

    start = config["backtest"]["start_date"].replace("-", "")
    end = config["backtest"]["end_date"].replace("-", "")

    stocks_data = {}
    for code in stock_codes:
        try:
            # Fetch daily kline
            if cache.is_cached(code, "daily"):
                daily_df = cache.load(code, "daily")
            else:
                daily_df = fetcher.get_stock_daily(code, start, end)
                cache.save(code, "daily", daily_df)

            # Fetch valuation
            if cache.is_cached(code, "valuation"):
                val_df = cache.load(code, "valuation")
            else:
                val_df = fetcher.get_stock_valuation(code)
                cache.save(code, "valuation", val_df)

            # Clean and merge
            daily_df = processor.clean_daily_data(daily_df)
            merged = processor.merge_stock_data(daily_df, val_df)

            if len(merged) > 30:  # Need enough data for factor calculation
                stocks_data[code] = merged
                logger.info(f"Loaded {code} ({stock_names.get(code, '')}): {len(merged)} rows")

        except Exception as e:
            logger.warning(f"Skipping {code}: {e}")
            continue

    logger.info(f"Successfully loaded {len(stocks_data)} / {len(stock_codes)} stocks")
    return stocks_data, stock_names


def run_backtest(config):
    """Run full backtest."""
    logger.info("=== Starting Backtest ===")
    stocks_data, stock_names = fetch_all_data(config)

    if not stocks_data:
        logger.error("No stock data loaded, aborting backtest")
        return

    engine = BacktestEngine(config)
    result = engine.run(stocks_data, stock_names)

    # Print metrics
    print("\n" + "=" * 50)
    print("回测结果")
    print("=" * 50)
    metrics = result["metrics"]
    print(f"总收益率:     {metrics['total_return']:.2%}")
    print(f"年化收益率:   {metrics['annual_return']:.2%}")
    print(f"最大回撤:     {metrics['max_drawdown']:.2%}")
    print(f"夏普比率:     {metrics['sharpe_ratio']:.4f}")
    print(f"胜率:         {metrics['win_rate']:.2%}")
    print(f"交易天数:     {metrics['total_trades']}")
    print("=" * 50)

    # Plot portfolio value
    output_dir = config.get("paths", {}).get("output", "output")
    os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)

    pv = result["portfolio_values"]
    dates = [p["date"] for p in pv]
    values = [p["value"] for p in pv]

    plt.figure(figsize=(14, 6))
    plt.plot(dates, values, label="Portfolio", linewidth=1.5)
    plt.axhline(y=config["backtest"]["initial_capital"], color="gray", linestyle="--", label="Initial Capital")
    plt.title("有色金属多因子策略 - 回测净值曲线")
    plt.xlabel("日期")
    plt.ylabel("组合价值 (元)")
    plt.legend()
    plt.xticks(rotation=45)
    # Show fewer x-axis labels
    step = max(len(dates) // 10, 1)
    plt.xticks(range(0, len(dates), step), [dates[i] for i in range(0, len(dates), step)])
    plt.tight_layout()

    chart_path = os.path.join(output_dir, "reports", "backtest_result.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"\n净值曲线已保存: {chart_path}")


def run_signal(config):
    """Generate today's trading signals."""
    logger.info("=== Generating Trading Signals ===")
    stocks_data, stock_names = fetch_all_data(config)

    if not stocks_data:
        logger.error("No stock data loaded")
        return

    # Compute factors and score
    factors = {
        "momentum": MomentumFactor(config["factors"].get("momentum", {}).get("lookback", 20)),
        "value": ValueFactor(),
        "volatility": VolatilityFactor(config["factors"].get("volatility", {}).get("lookback", 20)),
        "quality": QualityFactor(),
    }

    latest_factors = {}
    for code, df in stocks_data.items():
        result = df.copy()
        for factor in factors.values():
            result = factor.calculate(result)
        if not result.empty:
            last_row = result.iloc[-1].to_dict()
            if pd.notna(last_row.get("return_n")):
                latest_factors[code] = last_row

    strategy = MultiFactorStrategy(config)
    scores = strategy.score_stocks(latest_factors)
    selected = strategy.select_top_n(scores)
    target_positions = strategy.generate_target_positions(selected)

    risk_mgr = RiskManager(config)
    target_positions = risk_mgr.check_position_limits(target_positions)

    # Generate signals (assuming no current holdings for fresh signal)
    sig_gen = SignalGenerator(
        os.path.join(config.get("paths", {}).get("output", "output"), "signals")
    )
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    signals = sig_gen.generate_signals(
        date=today,
        current_holdings={},
        target_positions=target_positions,
        stock_names=stock_names,
        scores=scores,
    )
    sig_gen.save_to_csv(signals, today)

    print("\n" + "=" * 50)
    print(f"今日交易信号 ({today})")
    print("=" * 50)
    for s in signals:
        print(f"  {s['code']} {s['name']:10s} | {s['action']:4s} | "
              f"目标仓位: {s['target_weight']:.2%} | 得分: {s['score']:.4f}")
    print("=" * 50)

    # Print top 10 scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n因子得分 Top 10:")
    for code, score in sorted_scores:
        name = stock_names.get(code, code)
        print(f"  {code} {name:10s} | 得分: {score:.4f}")


def main():
    parser = argparse.ArgumentParser(description="A股有色金属多因子量化交易机器人")
    parser.add_argument("--mode", choices=["backtest", "simulate", "signal"],
                        default="signal", help="运行模式")
    parser.add_argument("--config", default=None, help="配置文件路径")
    args = parser.parse_args()

    setup_logging()
    config = load_config(args.config)

    if args.mode == "backtest":
        run_backtest(config)
    elif args.mode == "signal":
        run_signal(config)
    elif args.mode == "simulate":
        # Simulate mode is same as signal but runs continuously
        run_signal(config)
        print("\n模拟盘模式：请设置定时任务每日运行此命令")


if __name__ == "__main__":
    main()
```

**Step 2: Test it runs**

Run: `cd superpower_testing && python -m quant_bot.main --help`
Expected: Shows help text with usage

**Step 3: Commit**

```bash
git add quant_bot/main.py
git commit -m "feat: add main entry point with backtest, simulate, and signal modes"
```

---

### Task 15: Integration Test & Final Verification

**Step 1: Run all unit tests**

Run: `cd superpower_testing && python -m pytest tests/ -v`
Expected: All tests PASS

**Step 2: Run a quick signal generation (requires network)**

Run: `cd superpower_testing && python -m quant_bot.main --mode signal`
Expected: Outputs today's trading signals for non-ferrous metals stocks

**Step 3: Run backtest (requires network)**

Run: `cd superpower_testing && python -m quant_bot.main --mode backtest`
Expected: Prints backtest metrics and saves chart to output/reports/

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete A-share non-ferrous metals multi-factor quant bot"
```
