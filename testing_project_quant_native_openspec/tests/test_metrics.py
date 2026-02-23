"""Tests for performance metrics calculation."""

import pytest
import pandas as pd
from src.report.metrics import (
    total_return, annualized_return, max_drawdown,
    sharpe_ratio, calmar_ratio
)


class TestMetrics:
    def test_total_return(self):
        nav = pd.Series([100, 110, 105, 120])
        assert abs(total_return(nav) - 0.20) < 0.01

    def test_annualized_return(self):
        nav = pd.Series([100] + [110] * 251)  # ~1 year, 10% return
        ann = annualized_return(nav, trading_days=252)
        assert abs(ann - 0.10) < 0.02

    def test_max_drawdown(self):
        nav = pd.Series([100, 110, 90, 95, 85])
        mdd = max_drawdown(nav)
        # Peak=110, trough=85, drawdown = 25/110 = 22.7%
        assert abs(mdd - 0.227) < 0.01

    def test_sharpe_ratio_positive(self):
        nav = pd.Series(range(100, 200))  # steady uptrend
        sr = sharpe_ratio(nav)
        assert sr > 0

    def test_calmar_ratio(self):
        nav = pd.Series([100, 105, 103, 110, 108, 115])
        cr = calmar_ratio(nav)
        assert cr > 0
