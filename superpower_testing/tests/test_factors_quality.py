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
    df = pd.DataFrame({
        "date": ["2024-01-02"],
        "close": [10],
    })
    factor = QualityFactor()
    result = factor.calculate(df)
    assert "roe_score" in result.columns
    assert result["roe_score"].iloc[0] == 0
