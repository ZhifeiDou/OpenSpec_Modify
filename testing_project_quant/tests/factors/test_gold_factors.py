"""Tests for gold cross-metal ratio factors and inventory mapping fix."""
import numpy as np
import pandas as pd
import pytest

from src.data.storage import DataStore
from src.factors.commodity import GoldSilverRatioFactor, GoldCopperRatioFactor
from src.factors.base import get_registered_factors


@pytest.fixture
def store(tmp_path):
    """Create an in-memory DataStore with futures data."""
    db_path = str(tmp_path / "test.db")
    s = DataStore(db_path)
    return s


@pytest.fixture
def config():
    return {
        "factors": {
            "gold_cross_metal": {
                "gsr_lookback": 60,
                "gcr_lookback": 20,
            }
        }
    }


def _seed_futures(store, metal, n_days, base_price):
    """Insert n_days of synthetic futures data for a metal."""
    dates = pd.date_range("2024-01-02", periods=n_days, freq="B")
    np.random.seed(hash(metal) % 2**31)
    close = base_price + np.cumsum(np.random.randn(n_days) * 0.5)
    df = pd.DataFrame({
        "metal": metal,
        "date": dates.strftime("%Y-%m-%d"),
        "open": close,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": 10000,
    })
    store.save_dataframe("futures_daily", df)
    return close


def _seed_universe_cache(store, symbols_subsectors):
    """Insert universe cache entries mapping symbols to subsectors."""
    import sqlite3
    with store._get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS universe_cache "
            "(symbol TEXT PRIMARY KEY, name TEXT, subsector TEXT)"
        )
        for symbol, subsector in symbols_subsectors.items():
            conn.execute(
                "INSERT OR REPLACE INTO universe_cache (symbol, name, subsector) VALUES (?, ?, ?)",
                (symbol, symbol, subsector),
            )


class TestFactorRegistration:
    """R1-UC1-S1, R1-UC1-S5: Both gold factors are registered in the factor registry."""

    def test_gold_silver_ratio_registered(self):
        """GoldSilverRatioFactor appears in the factor registry."""
        # Trigger registration by importing
        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        assert "gold_silver_ratio" in registry
        assert registry["gold_silver_ratio"].category == "commodity"

    def test_gold_copper_ratio_registered(self):
        """GoldCopperRatioFactor appears in the factor registry."""
        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        assert "gold_copper_ratio" in registry
        assert registry["gold_copper_ratio"].category == "commodity"


class TestNoGoldStocksInUniverse:
    """R1-UC1-E3: No stocks classified under gold subsector."""

    def test_no_gold_stocks_returns_nan_for_all(self, store, config):
        """When no gold stocks exist, both factors return NaN for all stocks."""
        _seed_futures(store, "au", 70, 2300.0)
        _seed_futures(store, "ag", 70, 27.0)
        _seed_futures(store, "cu", 70, 70.0)
        _seed_universe_cache(store, {"COPPER01": "copper", "ZINC01": "zinc_lead"})

        gsr = GoldSilverRatioFactor()
        gcr = GoldCopperRatioFactor()
        gsr_result = gsr.compute(["COPPER01", "ZINC01"], "2024-04-30", store, config)
        gcr_result = gcr.compute(["COPPER01", "ZINC01"], "2024-04-30", store, config)

        assert all(np.isnan(v) for v in gsr_result.values)
        assert all(np.isnan(v) for v in gcr_result.values)


class TestScoringIntegration:
    """R1-UC1-S8: Gold factors combine with existing commodity factors in scoring."""

    def test_gold_factors_in_scoring_model(self, store, config):
        """Both gold factors are included in factor matrix alongside existing commodity factors."""
        _seed_futures(store, "au", 70, 2300.0)
        _seed_futures(store, "ag", 70, 27.0)
        _seed_futures(store, "cu", 70, 70.0)
        _seed_futures(store, "al", 70, 18000.0)
        _seed_futures(store, "zn", 70, 22000.0)
        _seed_futures(store, "ni", 70, 130000.0)
        _seed_universe_cache(store, {"GOLD01": "gold", "COPPER01": "copper"})

        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        commodity_factors = {n: cls for n, cls in registry.items() if cls.category == "commodity"}

        # Compute all commodity factors
        results = {}
        universe = ["GOLD01", "COPPER01"]
        for name, cls in commodity_factors.items():
            factor = cls()
            results[name] = factor.compute(universe, "2024-04-30", store, config)

        factor_matrix = pd.DataFrame(results, index=universe)

        # Gold factors should be present as columns
        assert "gold_silver_ratio" in factor_matrix.columns
        assert "gold_copper_ratio" in factor_matrix.columns
        # Existing commodity factors should also be present
        assert "metal_price_mom_60d" in factor_matrix.columns
        assert "futures_basis" in factor_matrix.columns
        # Gold stock should have numeric values for gold factors
        assert not np.isnan(factor_matrix.loc["GOLD01", "gold_silver_ratio"])
        # Copper stock should have NaN for gold factors
        assert np.isnan(factor_matrix.loc["COPPER01", "gold_silver_ratio"])


class TestGoldSilverRatioFactor:
    def test_correct_ratio_deviation(self, store, config):
        """Verify gold-silver ratio deviation is computed correctly."""
        # Seed 70 days of data (enough for 60-day lookback + 1)
        n = 70
        au_close = _seed_futures(store, "au", n, 2300.0)
        ag_close = _seed_futures(store, "ag", n, 27.0)

        _seed_universe_cache(store, {"GOLD01": "gold"})

        factor = GoldSilverRatioFactor()
        result = factor.compute(["GOLD01"], "2024-04-30", store, config)

        assert not np.isnan(result["GOLD01"])
        # Manually compute expected value
        au_tail = au_close[-61:]
        ag_tail = ag_close[-61:]
        ratios = au_tail / ag_tail
        expected = (ratios[-1] - ratios[:-1].mean()) / ratios[:-1].mean()
        assert abs(result["GOLD01"] - expected) < 1e-6

    def test_nan_for_non_gold_stocks(self, store, config):
        """Gold-silver ratio returns NaN for non-gold subsector stocks."""
        _seed_futures(store, "au", 70, 2300.0)
        _seed_futures(store, "ag", 70, 27.0)
        _seed_universe_cache(store, {"COPPER01": "copper", "GOLD01": "gold"})

        factor = GoldSilverRatioFactor()
        result = factor.compute(["COPPER01", "GOLD01"], "2024-04-30", store, config)

        assert np.isnan(result["COPPER01"])
        assert not np.isnan(result["GOLD01"])

    def test_nan_with_insufficient_data(self, store, config):
        """Returns NaN when fewer than lookback+1 days of data are available."""
        _seed_futures(store, "au", 30, 2300.0)  # Only 30 days, need 61
        _seed_futures(store, "ag", 30, 27.0)
        _seed_universe_cache(store, {"GOLD01": "gold"})

        factor = GoldSilverRatioFactor()
        result = factor.compute(["GOLD01"], "2024-02-15", store, config)

        assert np.isnan(result["GOLD01"])


class TestGoldCopperRatioFactor:
    def test_correct_rate_of_change(self, store, config):
        """Verify gold-copper ratio rate-of-change is computed correctly."""
        n = 30
        au_close = _seed_futures(store, "au", n, 2300.0)
        cu_close = _seed_futures(store, "cu", n, 70.0)
        _seed_universe_cache(store, {"GOLD01": "gold"})

        factor = GoldCopperRatioFactor()
        result = factor.compute(["GOLD01"], "2024-02-15", store, config)

        assert not np.isnan(result["GOLD01"])
        # Manually compute expected value
        ratio_today = au_close[-1] / cu_close[-1]
        ratio_past = au_close[-21] / cu_close[-21]
        expected = (ratio_today - ratio_past) / ratio_past
        assert abs(result["GOLD01"] - expected) < 1e-6

    def test_nan_for_non_gold_stocks(self, store, config):
        """Gold-copper ratio returns NaN for non-gold subsector stocks."""
        _seed_futures(store, "au", 30, 2300.0)
        _seed_futures(store, "cu", 30, 70.0)
        _seed_universe_cache(store, {"ZINC01": "zinc_lead", "GOLD01": "gold"})

        factor = GoldCopperRatioFactor()
        result = factor.compute(["ZINC01", "GOLD01"], "2024-02-15", store, config)

        assert np.isnan(result["ZINC01"])
        assert not np.isnan(result["GOLD01"])

    def test_nan_with_insufficient_data(self, store, config):
        """Returns NaN when fewer than lookback+1 days of data are available."""
        _seed_futures(store, "au", 10, 2300.0)  # Only 10 days, need 21
        _seed_futures(store, "cu", 10, 70.0)
        _seed_universe_cache(store, {"GOLD01": "gold"})

        factor = GoldCopperRatioFactor()
        result = factor.compute(["GOLD01"], "2024-01-16", store, config)

        assert np.isnan(result["GOLD01"])


class TestInventoryMapping:
    def test_gold_inventory_mapping(self):
        """fetch_inventory correctly maps 'au' to '黄金'."""
        from src.data.sources.akshare_source import AKShareSource
        source = AKShareSource()
        # We can't call the actual API, but we can verify the mapping exists
        # by checking the metal_names dict inside fetch_inventory
        import inspect
        source_code = inspect.getsource(source.fetch_inventory.__wrapped__)
        assert '"au": "黄金"' in source_code or "'au': '黄金'" in source_code

    def test_silver_inventory_mapping(self):
        """fetch_inventory correctly maps 'ag' to '白银'."""
        from src.data.sources.akshare_source import AKShareSource
        source = AKShareSource()
        import inspect
        source_code = inspect.getsource(source.fetch_inventory.__wrapped__)
        assert '"ag": "白银"' in source_code or "'ag': '白银'" in source_code
