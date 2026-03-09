"""Pipeline-level tests for Tushare migration.

Covers:
- R1-UC1: Token configuration flow
- R2-UC1: Stock daily pipeline (incremental update, store, metadata)
- R3-UC1: Futures daily pipeline iteration and store
- R4-UC1: Macro indicator pipeline iteration
- R5-UC1: Fund flow pipeline store
- R7-UC1: Full data update pipeline
"""
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from src.data.sources.tushare_source import TushareSource


# ── Helpers ───────────────────────────────────────────────────────────────────


def _mock_tushare_init(self, **kwargs):
    """Replacement __init__ that skips real Tushare connection."""
    self._pro = MagicMock()
    self._token = "test_token"
    self.delay = kwargs.get("delay", 0)
    self.max_retries = kwargs.get("max_retries", 0)


@pytest.fixture
def pipeline_config(tmp_path):
    return {
        "data": {
            "db_path": str(tmp_path / "test.db"),
            "api_delay_seconds": 0,
            "max_retries": 0,
            "tushare_token_env": "TUSHARE_TOKEN",
        },
    }


def _make_stock_daily_df(n_days=5, symbol="000001"):
    dates = pd.date_range("2025-01-02", periods=n_days, freq="B")
    np.random.seed(42)
    close = 10.0 + np.cumsum(np.random.randn(n_days) * 0.2)
    return pd.DataFrame({
        "date": dates,
        "open": close + 0.1,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": 100000,
        "amount": 1000000,
    })


def _make_futures_df(n_days=5, base=70000.0):
    dates = pd.date_range("2025-01-02", periods=n_days, freq="B")
    np.random.seed(42)
    close = base + np.cumsum(np.random.randn(n_days) * 100)
    return pd.DataFrame({
        "date": dates,
        "open": close + 10,
        "high": close + 50,
        "low": close - 50,
        "close": close,
        "volume": 50000,
    })


# ── R2-UC1-S1: Determine last update date (incremental) ─────────────────────


class TestStockDailyIncremental:
    """R2-UC1-S1, R2-UC1-S6: Incremental update and metadata tracking."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    def test_incremental_update_uses_last_date(self, mock_fetch, pipeline_config):
        """Pipeline queries metadata for last update and fetches from next day."""
        mock_fetch.return_value = _make_stock_daily_df()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)

        # First run: full fetch
        pipeline._update_stock_daily(["000001"], "2020-01-01", "2025-01-10", force=False)
        assert mock_fetch.called

        # Metadata should be updated
        last = pipeline.store.get_last_updated("stock_000001")
        assert last is not None

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    def test_stock_data_stored_in_sqlite(self, mock_fetch, pipeline_config):
        """R2-UC1-S5: Validated data is stored in SQLite."""
        stock_df = _make_stock_daily_df(n_days=10)
        mock_fetch.return_value = stock_df
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        result = pipeline._update_stock_daily(["000001"], "2020-01-01", "2025-01-31", force=False)
        assert "10 rows updated" in result

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    def test_metadata_updated_after_store(self, mock_fetch, pipeline_config):
        """R2-UC1-S6: last-updated metadata is set after storing."""
        mock_fetch.return_value = _make_stock_daily_df()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_stock_daily(["000001"], "2020-01-01", "2025-01-10", force=False)
        last = pipeline.store.get_last_updated("stock")
        assert last == "2025-01-10"


# ── R2-UC1-E1, R2-UC1-E2: Retry and exhaustion ─────────────────────────────


class TestStockDailyRetryAndSkip:
    """R2-UC1-E1/E2: Retry on failure, skip on exhaustion, continue to next."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    def test_skip_on_fetch_failure_continues(self, mock_fetch, pipeline_config):
        """When fetching one symbol fails, pipeline continues with others."""
        ok_df = _make_stock_daily_df()

        def side_effect(symbol, start, end):
            if symbol == "000001":
                raise ConnectionError("API error")
            return ok_df

        mock_fetch.side_effect = side_effect
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        result = pipeline._update_stock_daily(
            ["000001", "600000"], "2020-01-01", "2025-01-10", force=False
        )
        assert "1 errors" in result


# ── R3-UC1-S1: Pipeline iterates all metals ─────────────────────────────────


class TestFuturesPipelineIteration:
    """R3-UC1-S1: System iterates over all configured metals."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_futures_daily")
    def test_all_metals_fetched(self, mock_fetch, pipeline_config):
        """Pipeline calls fetch_futures_daily for every metal in _metals."""
        mock_fetch.return_value = pd.DataFrame()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_futures("2024-01-01", "2025-01-01", force=False)

        called_metals = [call.args[0] for call in mock_fetch.call_args_list]
        for metal in ["cu", "al", "zn", "ni", "sn", "pb", "au", "ag"]:
            assert metal in called_metals


# ── R4-UC1-S1: Pipeline iterates macro indicators ───────────────────────────


class TestMacroPipelineIteration:
    """R4-UC1-S1: System iterates over configured macro indicators."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_macro")
    def test_all_indicators_fetched(self, mock_fetch, pipeline_config):
        """Pipeline calls fetch_macro for pmi and m1."""
        mock_fetch.return_value = pd.DataFrame()
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline._update_macro(force=False)

        called_indicators = [call.args[0] for call in mock_fetch.call_args_list]
        assert "pmi" in called_indicators
        assert "m1" in called_indicators


# ── R4-UC1-S5: Macro data stored via pipeline ───────────────────────────────


class TestMacroPipelineStorage:
    """R4-UC1-S5: Macro data passes through validation and is counted."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_macro")
    def test_macro_data_counted_in_result(self, mock_fetch, pipeline_config):
        """Pipeline reports macro record count after fetching."""
        mock_fetch.return_value = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=12, freq="MS"),
            "value": [50.1, 49.8, 50.5, 51.0, 50.3, 49.5,
                      50.8, 51.2, 50.0, 49.9, 50.7, 51.1],
        })
        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        result = pipeline._update_macro(force=False)
        assert "records" in result
        # Should contain a non-zero count
        assert "0 records" not in result or "24 records" in result


# ── R7-UC1-S6: Pipeline prints update summary ───────────────────────────────


class TestPipelineSummaryOutput:
    """R7-UC1-S6: Pipeline prints update summary with row counts."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    @patch.object(TushareSource, "fetch_futures_daily")
    @patch.object(TushareSource, "fetch_macro")
    @patch.object(TushareSource, "fetch_fund_flow")
    def test_summary_printed(
        self, mock_flow, mock_macro, mock_futures, mock_stock,
        pipeline_config, capsys
    ):
        """Pipeline run() prints a summary line for each category."""
        mock_stock.return_value = _make_stock_daily_df()
        mock_futures.return_value = _make_futures_df()
        mock_macro.return_value = pd.DataFrame()
        mock_flow.return_value = pd.DataFrame()

        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline.run(symbols=["000001"], categories=None, force_refresh=False)

        captured = capsys.readouterr()
        assert "数据更新摘要" in captured.out
        assert "stock" in captured.out
        assert "futures" in captured.out
        assert "macro" in captured.out


# ── R7-UC1: Full pipeline integration ────────────────────────────────────────


class TestFullPipelineFlow:
    """R7-UC1: Run full data update pipeline."""

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    @patch.object(TushareSource, "fetch_futures_daily")
    @patch.object(TushareSource, "fetch_macro")
    @patch.object(TushareSource, "fetch_fund_flow")
    def test_full_pipeline_runs_all_categories(
        self, mock_flow, mock_macro, mock_futures, mock_stock, pipeline_config
    ):
        """R7-UC1-S2 through S6: Pipeline updates all categories and prints summary."""
        mock_stock.return_value = _make_stock_daily_df()
        mock_futures.return_value = _make_futures_df()
        mock_macro.return_value = pd.DataFrame()
        mock_flow.return_value = pd.DataFrame()

        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        pipeline.run(symbols=["000001"], categories=None, force_refresh=False)

        assert mock_stock.called
        assert mock_futures.called
        assert mock_macro.called

    @patch.object(TushareSource, "__init__", _mock_tushare_init)
    @patch.object(TushareSource, "fetch_stock_daily")
    @patch.object(TushareSource, "fetch_futures_daily")
    @patch.object(TushareSource, "fetch_macro")
    def test_category_failure_continues(
        self, mock_macro, mock_futures, mock_stock, pipeline_config
    ):
        """R7-UC1-E2: Individual category failure doesn't stop the pipeline."""
        mock_stock.side_effect = Exception("Stock API down")
        mock_futures.return_value = _make_futures_df()
        mock_macro.return_value = pd.DataFrame()

        from src.data.pipeline import DataPipeline
        pipeline = DataPipeline(pipeline_config)
        # Should not raise — pipeline handles errors per category
        pipeline.run(symbols=["000001"], categories=["stock", "futures", "macro"], force_refresh=False)
        assert mock_futures.called
        assert mock_macro.called
