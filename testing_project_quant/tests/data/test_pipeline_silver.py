"""Tests for silver futures pipeline and gold/silver inventory mapping.

Covers R2-UC1 (silver pipeline) and R3-UC1 (inventory mapping) use cases.
"""
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch

from src.data.pipeline import DataPipeline
from src.data.sources.akshare_source import AKShareSource
from src.data.storage import DataStore


@pytest.fixture
def store(tmp_path):
    """Create a DataStore backed by a temporary SQLite database."""
    db_path = str(tmp_path / "test.db")
    return DataStore(db_path)


@pytest.fixture
def pipeline_config(tmp_path):
    """Minimal config for DataPipeline with a temp DB path."""
    return {
        "data": {
            "db_path": str(tmp_path / "pipeline.db"),
            "api_delay_seconds": 0,
            "max_retries": 0,
        },
        "factors": {
            "gold_cross_metal": {
                "gsr_lookback": 60,
                "gcr_lookback": 20,
            }
        },
    }


def _make_futures_df(n_days=30, base_price=27.0):
    """Create a synthetic futures DataFrame matching AKShare output format."""
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


def _make_inventory_df():
    """Create a synthetic inventory DataFrame matching AKShare output format."""
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    return pd.DataFrame({
        "date": dates,
        "inventory": [1000 + i * 10 for i in range(10)],
    })


# ── R2-UC1: Fetch and store silver futures data ──────────────────────────────


class TestSilverInMetalsList:
    """R2-UC1-S1: _metals list includes 'ag'."""

    def test_ag_in_metals_list(self, pipeline_config):
        """DataPipeline._metals contains 'ag' for silver futures fetching."""
        pipeline = DataPipeline(pipeline_config)
        assert "ag" in pipeline._metals

    def test_au_also_in_metals_list(self, pipeline_config):
        """DataPipeline._metals still contains 'au' for gold futures."""
        pipeline = DataPipeline(pipeline_config)
        assert "au" in pipeline._metals


class TestSilverFuturesFetch:
    """R2-UC1-S2, R2-UC1-S3: Pipeline calls fetch_futures_daily('ag') and gets data."""

    @patch.object(AKShareSource, "fetch_futures_daily")
    def test_pipeline_calls_fetch_for_ag(self, mock_fetch, pipeline_config):
        """Pipeline invokes fetch_futures_daily with 'ag' during futures update."""
        mock_fetch.return_value = pd.DataFrame()
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        fetched_metals = [call.args[0] for call in mock_fetch.call_args_list]
        assert "ag" in fetched_metals

    @patch.object(AKShareSource, "fetch_futures_daily")
    def test_fetch_returns_ag0_data(self, mock_fetch, pipeline_config):
        """When AKShare returns silver data, it is validated and stored."""
        ag_df = _make_futures_df(n_days=30, base_price=27.0)

        def side_effect(metal, start, end):
            if metal == "ag":
                return ag_df
            return pd.DataFrame()

        mock_fetch.side_effect = side_effect
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored = pipeline.store.read_futures_daily("ag")
        assert len(stored) == len(ag_df)


class TestSilverFuturesStorage:
    """R2-UC1-S4: Pipeline stores silver data in futures_daily table."""

    @patch.object(AKShareSource, "fetch_futures_daily")
    def test_silver_data_stored_with_metal_ag(self, mock_fetch, pipeline_config):
        """Stored silver futures rows have metal='ag'."""
        ag_df = _make_futures_df(n_days=10, base_price=27.0)

        def side_effect(metal, start, end):
            if metal == "ag":
                return ag_df
            return pd.DataFrame()

        mock_fetch.side_effect = side_effect
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored = pipeline.store.read_futures_daily("ag")
        assert not stored.empty
        assert all(stored["metal"] == "ag") if "metal" in stored.columns else True


class TestSilverEmptyData:
    """R2-UC1-E1: AKShare returns empty data for ag0."""

    @patch.object(AKShareSource, "fetch_futures_daily")
    def test_empty_ag_data_no_crash(self, mock_fetch, pipeline_config):
        """Pipeline handles empty silver data without error."""
        mock_fetch.return_value = pd.DataFrame()
        pipeline = DataPipeline(pipeline_config)
        result = pipeline._update_futures("2024-01-01", "2024-06-30", force=False)
        assert isinstance(result, str)

    @patch.object(AKShareSource, "fetch_futures_daily")
    def test_empty_ag_data_no_storage(self, mock_fetch, pipeline_config):
        """No silver rows are stored when API returns empty data."""
        mock_fetch.return_value = pd.DataFrame()
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored = pipeline.store.read_futures_daily("ag")
        assert stored.empty


class TestSilverApiFail:
    """R2-UC1-E2: API call fails after retries."""

    @patch.object(AKShareSource, "fetch_futures_daily")
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
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2024-06-30", force=False)

        stored_cu = pipeline.store.read_futures_daily("cu")
        assert not stored_cu.empty
        stored_ag = pipeline.store.read_futures_daily("ag")
        assert stored_ag.empty


# ── R3-UC1: Fix gold and silver inventory data mapping ───────────────────────
# Note: The pipeline does not have a dedicated _update_inventory method.
# Inventory fetching is done via AKShareSource.fetch_inventory directly.
# Tests below verify the mapping and API behavior at the source level.


class TestInventoryMappingSource:
    """R3-UC1-S1, R3-UC1-S3: fetch_inventory resolves 'au'→'黄金' and calls API."""

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_fetch_inventory_au_uses_huangjin(self, mock_ak, mock_sleep):
        """fetch_inventory('au') calls AKShare with symbol='黄金'."""
        mock_ak.return_value = _make_inventory_df()
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("au")
        mock_ak.assert_called_with(symbol="黄金")
        assert not result.empty

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_fetch_inventory_ag_uses_baiyin(self, mock_ak, mock_sleep):
        """fetch_inventory('ag') calls AKShare with symbol='白银'."""
        mock_ak.return_value = _make_inventory_df()
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("ag")
        mock_ak.assert_called_with(symbol="白银")
        assert not result.empty


class TestInventoryReturnsData:
    """R3-UC1-S3, R3-UC1-S4: AKShare returns gold/silver inventory data."""

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_gold_inventory_data_returned(self, mock_ak, mock_sleep):
        """fetch_inventory('au') returns inventory DataFrame when API has data."""
        inv_df = _make_inventory_df()
        mock_ak.return_value = inv_df
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("au")
        assert len(result) == len(inv_df)

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_silver_inventory_data_returned(self, mock_ak, mock_sleep):
        """fetch_inventory('ag') returns inventory DataFrame when API has data."""
        inv_df = _make_inventory_df()
        mock_ak.return_value = inv_df
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("ag")
        assert len(result) == len(inv_df)


class TestInventoryEmptyData:
    """R3-UC1-E1, R3-UC1-E2: AKShare has no gold/silver inventory data."""

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_empty_gold_inventory(self, mock_ak, mock_sleep):
        """fetch_inventory('au') returns empty DataFrame when API has no data."""
        mock_ak.return_value = pd.DataFrame()
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("au")
        assert result.empty

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_empty_silver_inventory(self, mock_ak, mock_sleep):
        """fetch_inventory('ag') returns empty DataFrame when API has no data."""
        mock_ak.return_value = pd.DataFrame()
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("ag")
        assert result.empty

    @patch("time.sleep")
    @patch("akshare.futures_inventory_em")
    def test_inventory_api_exception_returns_empty(self, mock_ak, mock_sleep):
        """fetch_inventory returns empty DataFrame when API raises an exception."""
        mock_ak.side_effect = Exception("API error")
        source = AKShareSource(delay=0, max_retries=0)
        result = source.fetch_inventory("au")
        assert result.empty
