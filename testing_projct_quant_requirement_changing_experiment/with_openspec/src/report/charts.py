"""Chart generation for performance reports using Plotly and Matplotlib."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def create_nav_chart(
    nav_series: pd.Series,
    benchmark: pd.Series | None = None,
    title: str = "策略净值曲线",
) -> "go.Figure":
    """Create NAV curve chart (strategy vs benchmark)."""
    import plotly.graph_objects as go

    fig = go.Figure()

    # Strategy NAV (normalized to 1.0)
    if not nav_series.empty:
        norm_nav = nav_series / nav_series.iloc[0]
        fig.add_trace(go.Scatter(
            x=nav_series.index,
            y=norm_nav,
            mode="lines",
            name="策略净值",
            line=dict(color="rgb(31, 119, 180)", width=2),
        ))

    # Benchmark
    if benchmark is not None and not benchmark.empty:
        norm_bench = benchmark / benchmark.iloc[0]
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=norm_bench,
            mode="lines",
            name="基准指数",
            line=dict(color="rgb(255, 127, 14)", width=1.5, dash="dash"),
        ))

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="净值",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


def create_drawdown_chart(
    nav_series: pd.Series,
    title: str = "回撤曲线",
) -> "go.Figure":
    """Create drawdown underwater chart with filled area."""
    import plotly.graph_objects as go

    if nav_series.empty:
        return go.Figure()

    nav = nav_series.values
    peak = np.maximum.accumulate(nav)
    drawdown = (nav - peak) / peak

    # Find worst drawdown period
    worst_idx = np.argmin(drawdown)
    worst_start = np.argmax(nav[:worst_idx + 1]) if worst_idx > 0 else 0

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=nav_series.index,
        y=drawdown,
        fill="tozeroy",
        mode="lines",
        name="回撤",
        line=dict(color="rgb(214, 39, 40)", width=1),
        fillcolor="rgba(214, 39, 40, 0.3)",
    ))

    # Highlight worst drawdown
    if worst_idx > worst_start:
        fig.add_vrect(
            x0=nav_series.index[worst_start],
            x1=nav_series.index[worst_idx],
            fillcolor="rgba(255, 0, 0, 0.1)",
            line_width=0,
            annotation_text=f"最大回撤: {drawdown[worst_idx]:.2%}",
        )

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="回撤比例",
        yaxis=dict(tickformat=".1%"),
        template="plotly_white",
    )

    return fig


def create_holdings_overview(
    holdings: dict,
    title: str = "当前持仓概览",
) -> tuple:
    """Create holdings table and sub-sector pie chart.

    Returns (table_fig, pie_fig).
    """
    import plotly.graph_objects as go

    if not holdings:
        empty = go.Figure()
        empty.add_annotation(text="无持仓", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty, empty

    # Pie chart by sub-sector
    subsector_weights: dict[str, float] = {}
    for sym, info in holdings.items():
        ss = info.get("subsector", "other")
        w = info.get("weight", 0.0)
        subsector_weights[ss] = subsector_weights.get(ss, 0.0) + w

    pie = go.Figure(data=[go.Pie(
        labels=list(subsector_weights.keys()),
        values=list(subsector_weights.values()),
        hole=0.4,
    )])
    pie.update_layout(title="子板块权重分布")

    # Table
    symbols = list(holdings.keys())
    table = go.Figure(data=[go.Table(
        header=dict(values=["股票", "子板块", "股数", "成本价", "当前价", "权重"]),
        cells=dict(values=[
            symbols,
            [holdings[s].get("subsector", "") for s in symbols],
            [holdings[s].get("shares", 0) for s in symbols],
            [f"{holdings[s].get('entry_price', 0):.2f}" for s in symbols],
            [f"{holdings[s].get('peak_price', 0):.2f}" for s in symbols],
            [f"{holdings[s].get('weight', 0):.2%}" for s in symbols],
        ]),
    )])
    table.update_layout(title=title)

    return table, pie


def create_factor_heatmap(
    factor_matrix: pd.DataFrame,
    title: str = "因子暴露热力图",
) -> "go.Figure":
    """Create stocks x factors heatmap colored by Z-Score."""
    import plotly.graph_objects as go

    if factor_matrix.empty:
        fig = go.Figure()
        fig.add_annotation(text="无因子数据", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    fig = go.Figure(data=go.Heatmap(
        z=factor_matrix.values,
        x=factor_matrix.columns,
        y=factor_matrix.index,
        colorscale="RdYlGn",
        zmid=0,
        colorbar=dict(title="Z-Score"),
    ))

    fig.update_layout(
        title=title,
        xaxis_title="因子",
        yaxis_title="股票",
        template="plotly_white",
    )

    return fig


def create_ic_tracking_chart(
    ic_history: pd.DataFrame,
    title: str = "因子IC跟踪",
) -> "go.Figure":
    """Create rolling IC tracking chart with reference line at 0.03."""
    import plotly.graph_objects as go

    if ic_history.empty:
        fig = go.Figure()
        fig.add_annotation(text="无IC数据", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    fig = go.Figure()

    for col in ic_history.columns:
        fig.add_trace(go.Scatter(
            x=ic_history.index,
            y=ic_history[col],
            mode="lines",
            name=col,
        ))

    # Reference line at 0.03
    fig.add_hline(y=0.03, line_dash="dash", line_color="gray",
                  annotation_text="IC=0.03 参考线")
    fig.add_hline(y=0, line_color="black", line_width=0.5)

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="Rank IC",
        template="plotly_white",
        hovermode="x unified",
    )

    return fig
