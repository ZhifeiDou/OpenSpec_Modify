"""Tests for silver futures pipeline (migrated to Tushare).

Covers R2-UC1 (silver pipeline) use cases.
"""
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from src.data.sources.tushare_source import TushareSource


@pytest.fixture
def pipeline_config(tmp_path):
    """Minimal config for DataPipeline with a temp DB path."""
    return {
        "data": {
            "db_path": str(tmp_path / "pipeline.db"),
            "api_delay_seconds": 0,
            "max_retries": 0,
            "tushare_token_env": "TUSHARE_TOKEN",
        },
        "factors": {
            "gold_cross_metal": {
                "gsr_lookback": 60,
                "gcr_lookback": 20,
            }
        },
    }


def _make_futures_df(n_days=30, base_price=27.0):
    """Create a synthetic futures DataFrame matching Tushare output format."""
    dates = pd.date_range("2024-01-02", periods=n_days, freq="B")
    np.random.seed(42)
    close = base_price + np.cumsum(np.random.randn(n_days) * 0.5)
    return pd.DataFrame({
        "date": dates,
        "open": close + 0.1,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": 10000,
    })


# ── R2-UC1: Fetch and store silver futures data ──────────────────────────────


class TestSilverInMetalsList:
    """R2-UC1-S1: _metals list includes 'ag'."""

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    def test_ag_in_metals_list(self, pipeline_config):
        """DataPipeline._metals contains 'ag' for silver futures fetching."""
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        assert "ag" in pipeline._metals

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    def test_au_also_in_metals_list(self, pipeline_config):
        """DataPipeline._metals still contains 'au' for gold futures."""
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        assert "au" in pipeline._metals


class TestSilverFuturesFetch:
    """R2-UC1-S2, R2-UC1-S3: Pipeline calls fetch_futures_daily('ag') and gets data."""

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    @patch.object(TushareSource, "fetch_futures_daily")
    def test_pipeline_calls_fetch_for_ag(self, mock_fetch, pipeline_config):
        """Pipeline invokes fetch_futures_daily with 'ag' during futures update."""
        mock_fetch.return_value = pd.DataFrame()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        fetched_metals = [call.args[0] for call in mock_fetch.call_args_list]
        assert "ag" in fetched_metals

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    @patch.object(TushareSource, "fetch_futures_daily")
    def test_fetch_returns_ag_data(self, mock_fetch, pipeline_config):
        """When Tushare returns silver data, it is validated and stored."""
        ag_df = _make_futures_df(n_days=30, base_price=27.0)

        def side_effect(metal, start, end):
            if metal == "ag":
                return ag_df
            return pd.DataFrame()

        mock_fetch.side_effect = side_effect
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored = pipeline.store.read_futures_daily("ag")
        assert len(stored) == len(ag_df)


class TestSilverEmptyData:
    """R2-UC1-E1: Tushare returns empty data for AG0.SHF."""

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    @patch.object(TushareSource, "fetch_futures_daily")
    def test_empty_ag_data_no_crash(self, mock_fetch, pipeline_config):
        """Pipeline handles empty silver data without error."""
        mock_fetch.return_value = pd.DataFrame()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        result = pipeline._update_futures("2024-01-01", "2024-06-30", force=False)
        assert isinstance(result, str)


class TestSilverApiFail:
    """R2-UC1-E2: API call fails after retries."""

    @patch.object(TushareSource, "__init__", lambda self, **kw: setattr(self, '_pro', MagicMock()) or None)
    @patch.object(TushareSource, "fetch_futures_daily")
    def test_ag_fetch_exception_continues(self, mock_fetch, pipeline_config):
        """Pipeline continues to other metals when silver fetch raises an exception."""
        cu_df = _make_futures_df(n_days=10, base_price=70000.0)

        def side_effect(metal, start, end):
            if metal == "ag":
                raise ConnectionError("API timeout")
            if metal == "cu":
                return cu_df
            return pd.DataFrame()

        mock_fetch.side_effect = side_effect
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored_cu = pipeline.store.read_futures_daily("cu")
        assert not stored_cu.empty
        stored_ag = pipeline.store.read_futures_daily("ag")
        assert stored_ag.empty


# ── R3-UC1: Inventory returns empty for Tushare ──────────────────────────────


class TestInventoryTushare:
    """Tushare adapter returns empty DataFrame for inventory (not supported)."""

    @patch("time.sleep")
    def test_inventory_returns_empty(self, mock_sleep):
        """fetch_inventory always returns empty DataFrame with Tushare."""
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source.delay = 0
        source.max_retries = 0
        result = source.fetch_inventory("au")
        assert result.empty

    @patch("time.sleep")
    def test_inventory_ag_returns_empty(self, mock_sleep):
        """fetch_inventory('ag') returns empty DataFrame with Tushare."""
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source.delay = 0
        source.max_retries = 0
        result = source.fetch_inventory("ag")
        assert result.empty
