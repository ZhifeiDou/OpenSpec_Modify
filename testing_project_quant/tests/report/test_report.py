"""Tests for report generation."""
import numpy as np
import pandas as pd
import pytest


def test_create_nav_chart():
    from src.report.charts import create_nav_chart
    nav = pd.Series(
        np.linspace(100_000, 110_000, 50),
        index=[f"2024-01-{i+1:02d}" for i in range(50)],
    )
    fig = create_nav_chart(nav)
    assert fig is not None
    assert len(fig.data) >= 1  # At least strategy line


def test_create_drawdown_chart():
    from src.report.charts import create_drawdown_chart
    nav = pd.Series(
        [100, 110, 105, 95, 100, 108],
        index=["2024-01-01", "2024-01-02", "2024-01-03",
               "2024-01-04", "2024-01-05", "2024-01-06"],
    )
    fig = create_drawdown_chart(nav)
    assert fig is not None


def test_create_factor_heatmap():
    from src.report.charts import create_factor_heatmap
    fm = pd.DataFrame({
        "f1": [0.5, -0.3, 1.2],
        "f2": [-0.1, 0.8, 0.2],
    }, index=["A", "B", "C"])
    fig = create_factor_heatmap(fm)
    assert fig is not None


def test_create_ic_tracking():
    from src.report.charts import create_ic_tracking_chart
    ic = pd.DataFrame({
        "factor_a": [0.05, 0.03, 0.04],
        "factor_b": [0.02, 0.01, -0.01],
    }, index=["2024-01", "2024-02", "2024-03"])
    fig = create_ic_tracking_chart(ic)
    assert fig is not None


def test_export_html(tmp_path):
    from src.report.exporter import export_report
    nav = pd.Series(
        np.linspace(100_000, 110_000, 20),
        index=[f"2024-01-{i+1:02d}" for i in range(20)],
    )
    metrics = {
        "annual_return": 0.15,
        "sharpe_ratio": 1.2,
        "max_drawdown": 0.08,
        "calmar_ratio": 1.5,
        "annual_volatility": 0.12,
        "win_rate": 0.6,
        "profit_loss_ratio": 1.8,
        "total_costs": 5000,
    }
    config = {"report": {"format": "html", "output_dir": str(tmp_path)}}
    path = export_report(config, nav_series=nav, metrics=metrics)
    assert path.endswith(".html")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "15.00%" in content
    assert "绩效概览" in content


def test_empty_nav_chart():
    from src.report.charts import create_nav_chart
    nav = pd.Series(dtype=float)
    fig = create_nav_chart(nav)
    assert fig is not None  # Should not crash
