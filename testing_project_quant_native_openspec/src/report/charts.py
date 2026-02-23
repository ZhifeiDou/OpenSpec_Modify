"""Plotly interactive charts for backtest reporting."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_nav_chart(nav_history: list[dict],
                      benchmark: list[dict] = None) -> go.Figure:
    """Create NAV curve chart."""
    dates = [h["date"] for h in nav_history]
    navs = [h["nav"] for h in nav_history]

    # Normalize to 1.0
    initial = navs[0] if navs else 1
    norm_navs = [n / initial for n in navs]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=norm_navs, mode="lines",
        name="Portfolio", line=dict(color="blue", width=2)
    ))

    if benchmark:
        bench_dates = [b["date"] for b in benchmark]
        bench_vals = [b["nav"] for b in benchmark]
        bench_initial = bench_vals[0] if bench_vals else 1
        norm_bench = [v / bench_initial for v in bench_vals]
        fig.add_trace(go.Scatter(
            x=bench_dates, y=norm_bench, mode="lines",
            name="Benchmark", line=dict(color="gray", width=1, dash="dash")
        ))

    fig.update_layout(
        title="净值曲线 (NAV Curve)",
        xaxis_title="日期", yaxis_title="净值 (归一化)",
        template="plotly_white"
    )
    return fig


def create_drawdown_chart(nav_history: list[dict]) -> go.Figure:
    """Create drawdown chart."""
    dates = [h["date"] for h in nav_history]
    navs = pd.Series([h["nav"] for h in nav_history])
    peak = navs.expanding().max()
    drawdown = (navs - peak) / peak

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=drawdown.values, fill="tozeroy",
        name="Drawdown", line=dict(color="red")
    ))
    fig.update_layout(
        title="回撤曲线 (Drawdown)",
        xaxis_title="日期", yaxis_title="回撤",
        template="plotly_white"
    )
    return fig


def create_position_chart(nav_history: list[dict]) -> go.Figure:
    """Create position count over time."""
    dates = [h["date"] for h in nav_history]
    positions = [h.get("n_positions", 0) for h in nav_history]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates, y=positions, name="持仓数量"
    ))
    fig.update_layout(
        title="持仓数量变化",
        xaxis_title="日期", yaxis_title="股票数量",
        template="plotly_white"
    )
    return fig
