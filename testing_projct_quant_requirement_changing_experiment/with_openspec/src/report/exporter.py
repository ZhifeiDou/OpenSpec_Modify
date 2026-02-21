"""Report exporter: HTML (Plotly) and PNG (Matplotlib fallback)."""
from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.report.charts import (
    create_nav_chart,
    create_drawdown_chart,
    create_factor_heatmap,
)

logger = logging.getLogger(__name__)


def export_report(
    config: dict,
    nav_series: pd.Series | None = None,
    trade_log: pd.DataFrame | None = None,
    metrics: dict | None = None,
    factor_matrix: pd.DataFrame | None = None,
    source: str = "backtest",
) -> str:
    """Generate and export performance report.

    Args:
        config: Settings dict.
        nav_series: NAV time series.
        trade_log: Trade log DataFrame.
        metrics: Performance metrics dict.
        factor_matrix: Current factor matrix for heatmap.
        source: "backtest" or "live".

    Returns:
        Output file path.
    """
    report_cfg = config.get("report", {})
    fmt = report_cfg.get("format", "html")
    output_dir = Path(report_cfg.get("output_dir", "reports"))
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "html":
        return _export_html(
            output_dir, timestamp, nav_series, trade_log, metrics, factor_matrix
        )
    else:
        return _export_png(
            output_dir, timestamp, nav_series, metrics
        )


def _export_html(
    output_dir: Path,
    timestamp: str,
    nav_series: pd.Series | None,
    trade_log: pd.DataFrame | None,
    metrics: dict | None,
    factor_matrix: pd.DataFrame | None,
) -> str:
    """Export interactive HTML report with embedded Plotly charts."""
    output_path = output_dir / f"report_{timestamp}.html"

    html_parts = [
        "<!DOCTYPE html>",
        "<html><head>",
        '<meta charset="utf-8">',
        "<title>A股有色金属量化策略报告</title>",
        '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>',
        "<style>",
        "body { font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: #f5f5f5; }",
        ".container { max-width: 1200px; margin: auto; }",
        ".card { background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
        ".metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }",
        ".metric { text-align: center; padding: 10px; }",
        ".metric-value { font-size: 24px; font-weight: bold; }",
        ".metric-label { color: #666; font-size: 12px; }",
        ".positive { color: #d32f2f; }",  # Red for positive in Chinese convention
        ".negative { color: #388e3c; }",
        "table { width: 100%; border-collapse: collapse; }",
        "th, td { padding: 8px 12px; text-align: right; border-bottom: 1px solid #eee; }",
        "th { background: #f0f0f0; }",
        "</style>",
        "</head><body>",
        '<div class="container">',
        "<h1>A股有色金属多因子量化策略报告</h1>",
        f"<p>生成时间: {timestamp}</p>",
    ]

    # Metrics summary
    if metrics:
        html_parts.append('<div class="card"><h2>绩效概览</h2>')
        html_parts.append('<div class="metrics-grid">')
        metric_items = [
            ("年化收益", f"{metrics.get('annual_return', 0):.2%}", metrics.get('annual_return', 0)),
            ("夏普比率", f"{metrics.get('sharpe_ratio', 0):.2f}", metrics.get('sharpe_ratio', 0)),
            ("最大回撤", f"{metrics.get('max_drawdown', 0):.2%}", -1),
            ("卡尔玛比率", f"{metrics.get('calmar_ratio', 0):.2f}", metrics.get('calmar_ratio', 0)),
            ("年化波动率", f"{metrics.get('annual_volatility', 0):.2%}", -1),
            ("胜率", f"{metrics.get('win_rate', 0):.1%}", metrics.get('win_rate', 0)),
            ("盈亏比", f"{metrics.get('profit_loss_ratio', 0):.2f}", metrics.get('profit_loss_ratio', 0)),
            ("总交易成本", f"¥{metrics.get('total_costs', 0):,.0f}", -1),
        ]
        for label, value, indicator in metric_items:
            css_class = "positive" if indicator > 0 else "negative" if indicator < 0 else ""
            html_parts.append(
                f'<div class="metric"><div class="metric-value {css_class}">{value}</div>'
                f'<div class="metric-label">{label}</div></div>'
            )
        html_parts.append("</div></div>")

    # NAV chart
    if nav_series is not None and not nav_series.empty:
        nav_fig = create_nav_chart(nav_series)
        html_parts.append('<div class="card">')
        html_parts.append(nav_fig.to_html(full_html=False, include_plotlyjs=False))
        html_parts.append("</div>")

        # Drawdown chart
        dd_fig = create_drawdown_chart(nav_series)
        html_parts.append('<div class="card">')
        html_parts.append(dd_fig.to_html(full_html=False, include_plotlyjs=False))
        html_parts.append("</div>")

    # Factor heatmap
    if factor_matrix is not None and not factor_matrix.empty:
        heatmap_fig = create_factor_heatmap(factor_matrix)
        html_parts.append('<div class="card">')
        html_parts.append(heatmap_fig.to_html(full_html=False, include_plotlyjs=False))
        html_parts.append("</div>")

    # Trade log
    if trade_log is not None and not trade_log.empty:
        html_parts.append('<div class="card"><h2>交易记录</h2>')
        html_parts.append(trade_log.to_html(index=False, classes="trade-log"))
        html_parts.append("</div>")

    html_parts.extend(["</div></body></html>"])

    output_path.write_text("\n".join(html_parts), encoding="utf-8")
    logger.info("HTML report exported to %s", output_path)
    return str(output_path)


def _export_png(
    output_dir: Path,
    timestamp: str,
    nav_series: pd.Series | None,
    metrics: dict | None,
) -> str:
    """Export static PNG report using Matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # Try to use Chinese font
    _setup_chinese_font()

    output_path = output_dir / f"report_{timestamp}.png"

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [2, 1]})

    if nav_series is not None and not nav_series.empty:
        nav = nav_series.values
        dates = range(len(nav))

        # NAV curve
        norm_nav = nav / nav[0]
        axes[0].plot(dates, norm_nav, color="steelblue", linewidth=1.5)
        axes[0].set_title("策略净值曲线")
        axes[0].set_ylabel("净值")
        axes[0].grid(True, alpha=0.3)

        # Drawdown
        peak = np.maximum.accumulate(nav)
        dd = (nav - peak) / peak
        axes[1].fill_between(dates, dd, 0, color="indianred", alpha=0.5)
        axes[1].set_title("回撤")
        axes[1].set_ylabel("回撤比例")
        axes[1].grid(True, alpha=0.3)

    # Add metrics text
    if metrics:
        text = (
            f"年化收益: {metrics.get('annual_return', 0):.2%}  "
            f"夏普: {metrics.get('sharpe_ratio', 0):.2f}  "
            f"最大回撤: {metrics.get('max_drawdown', 0):.2%}"
        )
        fig.suptitle(text, fontsize=10, y=0.98)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    logger.info("PNG report exported to %s", output_path)
    return str(output_path)


def _setup_chinese_font():
    """Try to set up Chinese font for Matplotlib."""
    import matplotlib.pyplot as plt
    try:
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass
