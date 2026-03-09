"""Tests for TushareSource adapter.

Covers symbol conversion, date conversion, and all fetch_* methods with mocked Tushare API.
"""
import os
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from src.data.sources.tushare_source import (
    TushareSource,
    _to_tushare_code,
    _to_tushare_date,
    _from_tushare_date,
)


# ── Symbol conversion tests ──────────────────────────────────────────────────


class TestToTushareCode:
    """Unit tests for _to_tushare_code symbol conversion."""

    def test_shenzhen_stock_0_prefix(self):
        assert _to_tushare_code("000001") == "000001.SZ"

    def test_shenzhen_stock_3_prefix(self):
        assert _to_tushare_code("300750") == "300750.SZ"

    def test_shanghai_stock_6_prefix(self):
        assert _to_tushare_code("600000") == "600000.SH"

    def test_shanghai_stock_9_prefix(self):
        assert _to_tushare_code("900001") == "900001.SH"

    def test_already_tushare_format(self):
        assert _to_tushare_code("000001.SZ") == "000001.SZ"

    def test_empty_string_defaults_to_sz(self):
        assert _to_tushare_code("") == ".SZ"


# ── Date conversion tests ────────────────────────────────────────────────────


class TestDateConversion:
    """Unit tests for date format conversion helpers."""

    def test_to_tushare_date(self):
        assert _to_tushare_date("2025-01-15") == "20250115"

    def test_to_tushare_date_no_hyphens(self):
        assert _to_tushare_date("20250115") == "20250115"

    def test_from_tushare_date(self):
        result = _from_tushare_date("20250115")
        assert result == pd.Timestamp("2025-01-15")

    def test_from_tushare_date_type(self):
        result = _from_tushare_date("20240301")
        assert isinstance(result, pd.Timestamp)


# ── Token loading tests ──────────────────────────────────────────────────────


class TestTokenLoading:
    """Tests for token loading and validation."""

    def test_missing_token_raises_error(self):
        """Missing TUSHARE_TOKEN raises ValueError with clear message."""
        env = os.environ.copy()
        env.pop("TUSHARE_TOKEN", None)
        env.pop("TEST_TUSHARE_TOKEN", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="TEST_TUSHARE_TOKEN.*not set"):
                TushareSource(token_env="TEST_TUSHARE_TOKEN")

    @patch("tushare.pro_api")
    @patch("tushare.set_token")
    def test_token_from_env(self, mock_set, mock_api):
        """Token is loaded from environment variable."""
        mock_pro = MagicMock()
        mock_pro.trade_cal.return_value = pd.DataFrame({"cal_date": ["20250101"]})
        mock_api.return_value = mock_pro

        with patch.dict(os.environ, {"MY_TOKEN": "test123"}):
            source = TushareSource(token_env="MY_TOKEN")
            assert source._token == "test123"

    @patch("tushare.pro_api")
    @patch("tushare.set_token")
    def test_token_validation_failure(self, mock_set, mock_api):
        """Invalid token raises ConnectionError."""
        mock_pro = MagicMock()
        mock_pro.trade_cal.side_effect = Exception("Unauthorized")
        mock_api.return_value = mock_pro

        with patch.dict(os.environ, {"MY_TOKEN": "bad_token"}):
            with pytest.raises(ConnectionError, match="token validation failed"):
                TushareSource(token_env="MY_TOKEN")


# ── Retry behavior tests ─────────────────────────────────────────────────────


class TestRetryBehavior:
    """R2-UC1-E1: Retry on transient failure, succeed on subsequent attempt."""

    @patch("time.sleep")
    def test_retry_then_succeed(self, mock_sleep):
        """API call fails first, succeeds on retry — returns successful result."""
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 1  # Allow 1 retry

        call_count = 0
        def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Transient failure")
            return pd.DataFrame({
                "ts_code": ["000001.SZ"],
                "trade_date": ["20250101"],
                "open": [10.0], "high": [10.5], "low": [9.8],
                "close": [10.2], "vol": [100000], "amount": [1000000],
            })

        source._pro.daily.side_effect = side_effect
        result = source.fetch_stock_daily("000001", "2025-01-01", "2025-01-01")
        assert not result.empty
        assert call_count == 2  # First call failed, second succeeded


# ── fetch_stock_daily tests ──────────────────────────────────────────────────


class TestFetchStockDaily:
    """Tests for fetch_stock_daily with mocked Tushare responses."""

    def _make_source(self):
        """Create a TushareSource without real API connection."""
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 0
        return source

    @patch("time.sleep")
    def test_fetch_stock_daily_success(self, mock_sleep):
        source = self._make_source()
        source._pro.daily.return_value = pd.DataFrame({
            "ts_code": ["000001.SZ"] * 3,
            "trade_date": ["20250101", "20250102", "20250103"],
            "open": [10.0, 10.1, 10.2],
            "high": [10.5, 10.6, 10.7],
            "low": [9.8, 9.9, 10.0],
            "close": [10.2, 10.3, 10.4],
            "vol": [100000, 110000, 120000],
            "amount": [1000000, 1100000, 1200000],
        })

        result = source.fetch_stock_daily("000001", "2025-01-01", "2025-01-03")
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume", "amount"]
        assert len(result) == 3
        source._pro.daily.assert_called_once_with(
            ts_code="000001.SZ", start_date="20250101", end_date="20250103"
        )

    @patch("time.sleep")
    def test_fetch_stock_daily_empty(self, mock_sleep):
        source = self._make_source()
        source._pro.daily.return_value = pd.DataFrame()
        result = source.fetch_stock_daily("000001", "2025-01-01", "2025-01-03")
        assert result.empty


# ── fetch_futures_daily tests ────────────────────────────────────────────────


class TestFetchFuturesDaily:
    """Tests for fetch_futures_daily with mocked Tushare responses."""

    def _make_source(self):
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 0
        return source

    @patch("time.sleep")
    def test_fetch_copper_futures(self, mock_sleep):
        source = self._make_source()
        source._pro.fut_daily.return_value = pd.DataFrame({
            "ts_code": ["CU0.SHF"] * 3,
            "trade_date": ["20250101", "20250102", "20250103"],
            "open": [70000, 70100, 70200],
            "high": [70500, 70600, 70700],
            "low": [69800, 69900, 70000],
            "close": [70200, 70300, 70400],
            "settle": [70250, 70350, 70450],
            "vol": [50000, 51000, 52000],
            "oi": [300000, 310000, 320000],
        })

        result = source.fetch_futures_daily("cu", "2025-01-01", "2025-01-03")
        assert "open_interest" in result.columns
        assert "volume" in result.columns
        assert len(result) == 3

    @patch("time.sleep")
    def test_unmapped_metal_returns_empty(self, mock_sleep):
        source = self._make_source()
        result = source.fetch_futures_daily("unknown_metal", "2025-01-01", "2025-01-03")
        assert result.empty


# ── fetch_macro tests ────────────────────────────────────────────────────────


class TestFetchMacro:
    """Tests for fetch_macro with mocked Tushare responses."""

    def _make_source(self):
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 0
        return source

    @patch("time.sleep")
    def test_fetch_pmi(self, mock_sleep):
        source = self._make_source()
        source._pro.cn_pmi.return_value = pd.DataFrame({
            "month": ["202401", "202402", "202403"],
            "pmi010000": [50.1, 49.8, 50.5],
        })

        result = source.fetch_macro("pmi")
        assert list(result.columns) == ["date", "value"]
        assert len(result) == 3

    @patch("time.sleep")
    def test_fetch_m1(self, mock_sleep):
        source = self._make_source()
        source._pro.cn_m.return_value = pd.DataFrame({
            "month": ["202401", "202402"],
            "m1_yoy": [1.5, 1.8],
        })

        result = source.fetch_macro("m1")
        assert len(result) == 2
        assert result["value"].iloc[0] == 1.5

    @patch("time.sleep")
    def test_fetch_cpi(self, mock_sleep):
        source = self._make_source()
        source._pro.cn_cpi.return_value = pd.DataFrame({
            "month": ["202401", "202402"],
            "nt_yoy": [0.8, 0.7],
        })
        result = source.fetch_macro("cpi")
        assert list(result.columns) == ["date", "value"]
        assert len(result) == 2
        assert result["value"].iloc[0] == 0.8

    @patch("time.sleep")
    def test_fetch_ppi(self, mock_sleep):
        source = self._make_source()
        source._pro.cn_ppi.return_value = pd.DataFrame({
            "month": ["202401", "202402"],
            "ppi_yoy": [-2.5, -2.3],
        })
        result = source.fetch_macro("ppi")
        assert len(result) == 2

    @patch("time.sleep")
    def test_monthly_date_normalized_to_first_of_month(self, mock_sleep):
        """R4-UC1-E2: Monthly YYYYMM dates converted to YYYY-MM-01."""
        source = self._make_source()
        source._pro.cn_pmi.return_value = pd.DataFrame({
            "month": ["202403"],
            "pmi010000": [50.3],
        })
        result = source.fetch_macro("pmi")
        assert result["date"].iloc[0].day == 1
        assert result["date"].iloc[0].month == 3

    @patch("time.sleep")
    def test_fetch_unsupported_indicator(self, mock_sleep):
        source = self._make_source()
        result = source.fetch_macro("unknown_indicator")
        assert result.empty


# ── fetch_fund_flow tests ────────────────────────────────────────────────────


class TestFetchFundFlow:
    """Tests for fetch_fund_flow with mocked Tushare responses."""

    def _make_source(self):
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 0
        return source

    @patch("time.sleep")
    def test_fetch_fund_flow_with_both_sources(self, mock_sleep):
        source = self._make_source()
        source._pro.margin_detail.return_value = pd.DataFrame({
            "trade_date": ["20250101", "20250102"],
            "ts_code": ["000001.SZ", "000001.SZ"],
            "rzrqye": [1e9, 1.1e9],
        })
        source._pro.moneyflow_hsgt.return_value = pd.DataFrame({
            "trade_date": ["20250101", "20250102"],
            "north_money": [5e8, 6e8],
        })

        result = source.fetch_fund_flow("000001", "2025-01-01", "2025-01-02")
        assert "margin_balance" in result.columns
        assert "northbound_net_buy" in result.columns
        assert len(result) == 2

    @patch("time.sleep")
    def test_fetch_fund_flow_no_margin(self, mock_sleep):
        source = self._make_source()
        source._pro.margin_detail.return_value = pd.DataFrame()
        source._pro.moneyflow_hsgt.return_value = pd.DataFrame({
            "trade_date": ["20250101"],
            "north_money": [5e8],
        })

        result = source.fetch_fund_flow("000001", "2025-01-01", "2025-01-01")
        assert not result.empty
        assert pd.isna(result["margin_balance"].iloc[0])

    @patch("time.sleep")
    def test_fetch_fund_flow_only_trading_days(self, mock_sleep):
        """R5-UC1-E2: HSGT data only has trading days — weekends are absent."""
        source = self._make_source()
        # Tushare only returns trading day data, no weekend dates
        source._pro.margin_detail.return_value = pd.DataFrame({
            "trade_date": ["20250103", "20250106"],  # Fri and Mon, no Sat/Sun
            "ts_code": ["000001.SZ", "000001.SZ"],
            "rzrqye": [1e9, 1.05e9],
        })
        source._pro.moneyflow_hsgt.return_value = pd.DataFrame({
            "trade_date": ["20250103", "20250106"],  # Only trading days
            "north_money": [5e8, 6e8],
        })

        # Request range includes the weekend (Jan 4-5)
        result = source.fetch_fund_flow("000001", "2025-01-03", "2025-01-06")
        assert len(result) == 2  # Only 2 trading days, weekend skipped
        dates = result["date"].tolist()
        assert pd.Timestamp("2025-01-04") not in dates  # Saturday absent
        assert pd.Timestamp("2025-01-05") not in dates  # Sunday absent


# ── fetch_industry_stocks tests ──────────────────────────────────────────────


class TestFetchIndustryStocks:
    """Tests for fetch_industry_stocks with mocked Tushare responses."""

    def _make_source(self):
        source = TushareSource.__new__(TushareSource)
        source._pro = MagicMock()
        source._token = "test"
        source.delay = 0
        source.max_retries = 0
        return source

    @patch("time.sleep")
    def test_fetch_via_index_member(self, mock_sleep):
        """R6-UC1-S1: Direct call to index_member succeeds."""
        source = self._make_source()
        source._pro.index_member.return_value = pd.DataFrame({
            "con_code": ["601899.SH", "603993.SH"],
            "name": ["紫金矿业", "洛阳钼业"],
        })
        result = source.fetch_industry_stocks("801050")
        assert len(result) == 2
        assert "symbol" in result.columns
        assert result["symbol"].iloc[0] == "601899"

    @patch("time.sleep")
    def test_fetch_via_stock_basic_fallback(self, mock_sleep):
        source = self._make_source()
        source._pro.index_member.side_effect = Exception("Not available")
        source._pro.stock_basic.return_value = pd.DataFrame({
            "ts_code": ["000001.SZ", "600000.SH"],
            "name": ["平安银行", "紫金矿业"],
            "industry": ["银行", "有色金属"],
        })

        result = source.fetch_industry_stocks("801050")
        assert len(result) == 1  # Only 有色金属
        assert result["name"].iloc[0] == "紫金矿业"
        assert result["symbol"].iloc[0] == "600000"  # Stripped .SH
