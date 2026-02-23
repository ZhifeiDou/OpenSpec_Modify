"""Tests for factor calculations and normalization."""

import pytest
import numpy as np
import pandas as pd
from src.factors.technical import momentum, mean_reversion, turnover_ratio, realized_volatility
from src.factors.normalize import zscore_normalize, winsorize, normalize_factors
from src.factors.macro import pmi_direction, m1_growth_direction


class TestTechnicalFactors:
    def test_momentum_basic(self):
        prices = pd.Series(list(range(1, 71)))  # 1 to 70
        result = momentum(prices, window=60, skip=5)
        assert result > 0

    def test_momentum_insufficient_data(self):
        prices = pd.Series([1, 2, 3])
        assert np.isnan(momentum(prices, window=60, skip=5))

    def test_mean_reversion(self):
        prices = pd.Series([10, 11, 12, 13, 14])  # rising prices
        result = mean_reversion(prices, window=5)
        assert result < 0  # negative of positive return

    def test_turnover_ratio(self):
        volume = pd.Series([1000] * 25)
        result = turnover_ratio(volume, window=20)
        assert result == 1000

    def test_realized_volatility(self):
        np.random.seed(42)
        prices = pd.Series(100 + np.random.randn(100).cumsum())
        vol = realized_volatility(prices, window=20)
        assert vol > 0


class TestNormalization:
    def test_zscore(self):
        s = pd.Series([1, 2, 3, 4, 5])
        result = zscore_normalize(s)
        assert abs(result.mean()) < 1e-10
        assert abs(result.std() - 1.0) < 0.2  # close to 1

    def test_winsorize(self):
        s = pd.Series([-5, -1, 0, 1, 5])
        result = winsorize(s, n_std=3.0)
        assert result.max() <= 3.0
        assert result.min() >= -3.0

    def test_normalize_factors(self):
        df = pd.DataFrame({
            "factor_a": [1, 2, 3, 4, 100],  # outlier
            "factor_b": [10, 20, 30, 40, 50],
        })
        result = normalize_factors(df)
        assert result["factor_a"].max() <= 3.0


class TestMacroFactors:
    def test_pmi_expansion(self):
        pmi = pd.Series([51.0])
        assert pmi_direction(pmi) == 1.0

    def test_pmi_contraction(self):
        pmi = pd.Series([49.0])
        assert pmi_direction(pmi) == -1.0

    def test_m1_positive(self):
        m1 = pd.Series([5.0])
        assert m1_growth_direction(m1) == 1.0

    def test_m1_negative(self):
        m1 = pd.Series([-2.0])
        assert m1_growth_direction(m1) == -1.0
