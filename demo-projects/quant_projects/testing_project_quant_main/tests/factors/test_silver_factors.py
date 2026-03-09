"""Tests for silver cross-metal ratio factors and subsector classification."""
import numpy as np
import pandas as pd
import pytest

from src.data.storage import DataStore
from src.factors.commodity import SilverGoldRatioFactor, SilverCopperRatioFactor
from src.factors.base import get_registered_factors
from src.universe.classifier import classify_subsector, SUBSECTOR_METAL_MAP


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
            "silver_cross_metal": {
                "sgr_lookback": 60,
                "scr_lookback": 20,
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


class TestSilverSubsectorClassification:
    """4.7, 4.8: Silver subsector keywords and metal map."""

    def test_classify_bayin_keyword(self):
        """R1-UC2-S2: Classifier returns 'silver' for stock name containing '白银'."""
        assert classify_subsector("某某白银股份") == "silver"

    def test_classify_english_keyword(self):
        """R1-UC2-S2: Classifier returns 'silver' for stock name containing 'silver'."""
        assert classify_subsector("Silver Mining Co") == "silver"

    def test_classify_yinkuang_keyword(self):
        """R1-UC2-S2: Classifier returns 'silver' for stock name containing '银矿'."""
        assert classify_subsector("大型银矿集团") == "silver"

    def test_metal_map_silver(self):
        """R1-UC2-S4: SUBSECTOR_METAL_MAP['silver'] equals 'ag'."""
        assert SUBSECTOR_METAL_MAP["silver"] == "ag"

    def test_no_silver_keyword_returns_other(self):
        """R1-UC2-E2: No silver keyword → classified as 'other'."""
        assert classify_subsector("某某科技有限公司") == "other"

    def test_dual_silver_gold_keywords_returns_first_match(self):
        """R1-UC2-E1: Stock with both silver and gold keywords returns whichever matches first."""
        result = classify_subsector("白银黄金矿业集团")
        # Should match one of the two; the important thing is no crash and a valid subsector
        assert result in ("silver", "gold")


class TestSilverFactorRegistration:
    """Silver factors are auto-discovered via @register_factor."""

    def test_silver_gold_ratio_registered(self):
        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        assert "silver_gold_ratio" in registry
        assert registry["silver_gold_ratio"].category == "commodity"

    def test_silver_copper_ratio_registered(self):
        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        assert "silver_copper_ratio" in registry
        assert registry["silver_copper_ratio"].category == "commodity"


class TestSilverGoldRatioFactor:
    def test_correct_ratio_deviation(self, store, config):
        """4.2: Verify silver-gold ratio deviation is computed correctly."""
        n = 70
        ag_close = _seed_futures(store, "ag", n, 27.0)
        au_close = _seed_futures(store, "au", n, 2300.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["SILVER01"], "2024-04-30", store, config)

        assert not np.isnan(result["SILVER01"])
        # Manually compute expected value
        ag_tail = ag_close[-61:]
        au_tail = au_close[-61:]
        ratios = ag_tail / au_tail
        expected = (ratios[-1] - ratios[:-1].mean()) / ratios[:-1].mean()
        assert abs(result["SILVER01"] - expected) < 1e-6

    def test_nan_for_non_silver_stocks(self, store, config):
        """4.4: Silver-gold ratio returns NaN for non-silver subsector stocks."""
        _seed_futures(store, "ag", 70, 27.0)
        _seed_futures(store, "au", 70, 2300.0)
        _seed_universe_cache(store, {"COPPER01": "copper", "SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["COPPER01", "SILVER01"], "2024-04-30", store, config)

        assert np.isnan(result["COPPER01"])
        assert not np.isnan(result["SILVER01"])

    def test_nan_with_insufficient_data(self, store, config):
        """4.5: Returns NaN when fewer than lookback+1 days of data."""
        _seed_futures(store, "ag", 30, 27.0)  # Only 30 days, need 61
        _seed_futures(store, "au", 30, 2300.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["SILVER01"], "2024-02-15", store, config)

        assert np.isnan(result["SILVER01"])

    def test_zero_price_no_exception(self, store, config):
        """4.6: Zero prices produce NaN without raising exceptions."""
        n = 70
        dates = pd.date_range("2024-01-02", periods=n, freq="B")
        # All-zero ag prices
        df_ag = pd.DataFrame({
            "metal": "ag",
            "date": dates.strftime("%Y-%m-%d"),
            "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0,
        })
        store.save_dataframe("futures_daily", df_ag)
        _seed_futures(store, "au", n, 2300.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["SILVER01"], "2024-04-30", store, config)

        assert np.isnan(result["SILVER01"])


class TestSilverCopperRatioFactor:
    def test_correct_rate_of_change(self, store, config):
        """4.3: Verify silver-copper ratio rate-of-change is computed correctly."""
        n = 30
        ag_close = _seed_futures(store, "ag", n, 27.0)
        cu_close = _seed_futures(store, "cu", n, 70.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverCopperRatioFactor()
        result = factor.compute(["SILVER01"], "2024-02-15", store, config)

        assert not np.isnan(result["SILVER01"])
        # Manually compute expected value
        ratio_today = ag_close[-1] / cu_close[-1]
        ratio_past = ag_close[-21] / cu_close[-21]
        expected = (ratio_today - ratio_past) / ratio_past
        assert abs(result["SILVER01"] - expected) < 1e-6

    def test_nan_for_non_silver_stocks(self, store, config):
        """4.4: Silver-copper ratio returns NaN for non-silver subsector stocks."""
        _seed_futures(store, "ag", 30, 27.0)
        _seed_futures(store, "cu", 30, 70.0)
        _seed_universe_cache(store, {"ZINC01": "zinc_lead", "SILVER01": "silver"})

        factor = SilverCopperRatioFactor()
        result = factor.compute(["ZINC01", "SILVER01"], "2024-02-15", store, config)

        assert np.isnan(result["ZINC01"])
        assert not np.isnan(result["SILVER01"])

    def test_nan_with_insufficient_data(self, store, config):
        """4.5: Returns NaN when fewer than lookback+1 days of data."""
        _seed_futures(store, "ag", 10, 27.0)  # Only 10 days, need 21
        _seed_futures(store, "cu", 10, 70.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverCopperRatioFactor()
        result = factor.compute(["SILVER01"], "2024-01-16", store, config)

        assert np.isnan(result["SILVER01"])

    def test_zero_price_no_exception(self, store, config):
        """4.6: Zero prices produce NaN without raising exceptions."""
        n = 30
        dates = pd.date_range("2024-01-02", periods=n, freq="B")
        df_ag = pd.DataFrame({
            "metal": "ag",
            "date": dates.strftime("%Y-%m-%d"),
            "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0,
        })
        store.save_dataframe("futures_daily", df_ag)
        _seed_futures(store, "cu", n, 70.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverCopperRatioFactor()
        result = factor.compute(["SILVER01"], "2024-02-15", store, config)

        assert np.isnan(result["SILVER01"])


class TestOneMetalMissing:
    """R1-UC1-E2: One metal has data but the other does not."""

    def test_sgr_only_ag_data_no_au(self, store, config):
        """R1-UC1-E2: SilverGoldRatio returns NaN when au data is missing."""
        _seed_futures(store, "ag", 70, 27.0)
        # No au data seeded
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["SILVER01"], "2024-04-30", store, config)

        assert np.isnan(result["SILVER01"])

    def test_scr_only_ag_data_no_cu(self, store, config):
        """R1-UC1-E2: SilverCopperRatio returns NaN when cu data is missing."""
        _seed_futures(store, "ag", 30, 27.0)
        # No cu data seeded
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverCopperRatioFactor()
        result = factor.compute(["SILVER01"], "2024-02-15", store, config)

        assert np.isnan(result["SILVER01"])


class TestCustomLookbackConfig:
    """R1-UC3: Configure silver factor lookback windows."""

    def test_sgr_custom_lookback_90(self, store):
        """R1-UC3-S1/S3: SilverGoldRatioFactor uses custom sgr_lookback=90 from config."""
        custom_config = {
            "factors": {
                "silver_cross_metal": {
                    "sgr_lookback": 90,
                    "scr_lookback": 20,
                }
            }
        }
        n = 100  # Need at least 91 days for lookback=90
        ag_close = _seed_futures(store, "ag", n, 27.0)
        au_close = _seed_futures(store, "au", n, 2300.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        factor = SilverGoldRatioFactor()
        result = factor.compute(["SILVER01"], "2024-06-15", store, custom_config)

        assert not np.isnan(result["SILVER01"])
        # Manually compute with 90-day lookback
        ag_tail = ag_close[-91:]
        au_tail = au_close[-91:]
        ratios = ag_tail / au_tail
        expected = (ratios[-1] - ratios[:-1].mean()) / ratios[:-1].mean()
        assert abs(result["SILVER01"] - expected) < 1e-6

    def test_config_section_missing_uses_defaults(self, store):
        """R1-UC3-E1: When silver_cross_metal section is absent, factors use defaults."""
        empty_config = {"factors": {}}  # No silver_cross_metal section
        n = 70
        ag_close = _seed_futures(store, "ag", n, 27.0)
        au_close = _seed_futures(store, "au", n, 2300.0)
        _seed_futures(store, "cu", n, 70.0)
        _seed_universe_cache(store, {"SILVER01": "silver"})

        sgr = SilverGoldRatioFactor()
        sgr_result = sgr.compute(["SILVER01"], "2024-04-30", store, empty_config)
        # Default sgr_lookback=60, with 70 days of data this should work
        assert not np.isnan(sgr_result["SILVER01"])

        scr = SilverCopperRatioFactor()
        scr_result = scr.compute(["SILVER01"], "2024-04-30", store, empty_config)
        # Default scr_lookback=20, with 70 days of data this should work
        assert not np.isnan(scr_result["SILVER01"])


class TestSilverScoringIntegration:
    """R1-UC1, R1-UC1-S8: Both silver factors appear in the scoring matrix."""

    def test_silver_factors_in_scoring_model(self, store, config):
        """R1-UC1-S8: Silver factors merge into the factor matrix alongside existing factors."""
        _seed_futures(store, "ag", 70, 27.0)
        _seed_futures(store, "au", 70, 2300.0)
        _seed_futures(store, "cu", 70, 70.0)
        _seed_futures(store, "al", 70, 18000.0)
        _seed_futures(store, "zn", 70, 22000.0)
        _seed_futures(store, "ni", 70, 130000.0)
        _seed_universe_cache(store, {"SILVER01": "silver", "COPPER01": "copper"})

        import src.factors.commodity  # noqa: F401
        registry = get_registered_factors()
        commodity_factors = {n: cls for n, cls in registry.items() if cls.category == "commodity"}

        results = {}
        universe = ["SILVER01", "COPPER01"]
        for name, cls in commodity_factors.items():
            factor = cls()
            results[name] = factor.compute(universe, "2024-04-30", store, config)

        factor_matrix = pd.DataFrame(results, index=universe)

        # Silver factors should be present as columns
        assert "silver_gold_ratio" in factor_matrix.columns
        assert "silver_copper_ratio" in factor_matrix.columns
        # Existing commodity factors should also be present
        assert "metal_price_mom_60d" in factor_matrix.columns
        assert "futures_basis" in factor_matrix.columns
        # Silver stock should have numeric values for silver factors
        assert not np.isnan(factor_matrix.loc["SILVER01", "silver_gold_ratio"])
        assert not np.isnan(factor_matrix.loc["SILVER01", "silver_copper_ratio"])
        # Copper stock should have NaN for silver factors
        assert np.isnan(factor_matrix.loc["COPPER01", "silver_gold_ratio"])
        assert np.isnan(factor_matrix.loc["COPPER01", "silver_copper_ratio"])
