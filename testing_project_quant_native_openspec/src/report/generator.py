"""HTML report assembly and export."""

import os
import plotly.io as pio
from src.report.metrics import calculate_all_metrics
from src.report.charts import create_nav_chart, create_drawdown_chart, create_position_chart


def generate_html_report(nav_history: list[dict],
                          trade_log: list[dict],
                          output_path: str = "reports/backtest_report.html",
                          benchmark: list[dict] = None) -> str:
    """Generate interactive HTML backtest report.

    Args:
        nav_history: List of daily NAV records.
        trade_log: List of trade records.
        output_path: Path to save the HTML report.
        benchmark: Optional benchmark NAV history.

    Returns:
        Path to generated report.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    metrics = calculate_all_metrics(nav_history, trade_log)

    nav_chart = create_nav_chart(nav_history, benchmark)
    dd_chart = create_drawdown_chart(nav_history)
    pos_chart = create_position_chart(nav_history)

    metrics_html = f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 20px 0;">
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">总收益率</div>
            <div style="font-size: 24px; font-weight: bold; color: {'green' if metrics['total_return'] > 0 else 'red'};">
                {metrics['total_return']:.2%}
            </div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">年化收益率</div>
            <div style="font-size: 24px; font-weight: bold;">{metrics['annualized_return']:.2%}</div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">最大回撤</div>
            <div style="font-size: 24px; font-weight: bold; color: red;">{metrics['max_drawdown']:.2%}</div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">Sharpe Ratio</div>
            <div style="font-size: 24px; font-weight: bold;">{metrics['sharpe_ratio']:.2f}</div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">Calmar Ratio</div>
            <div style="font-size: 24px; font-weight: bold;">{metrics['calmar_ratio']:.2f}</div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">胜率</div>
            <div style="font-size: 24px; font-weight: bold;">{metrics['win_rate']:.2%}</div>
        </div>
        <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; text-align: center;">
            <div style="font-size: 14px; color: #666;">盈亏比</div>
            <div style="font-size: 24px; font-weight: bold;">{metrics['profit_loss_ratio']:.2f}</div>
        </div>
    </div>
    """

    trade_rows = ""
    for t in trade_log[-50:]:  # last 50 trades
        color = "green" if t["direction"] == "buy" else "red"
        trade_rows += f"""
        <tr>
            <td>{t['date']}</td>
            <td>{t['code']}</td>
            <td style="color: {color};">{t['direction']}</td>
            <td>{t['price']:.2f}</td>
            <td>{t['shares']}</td>
            <td>{t['cost']:.2f}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>量化回测报告</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>A股有色金属多因子量化交易 — 回测报告</h1>
        {metrics_html}
        {pio.to_html(nav_chart, full_html=False, include_plotlyjs=False)}
        {pio.to_html(dd_chart, full_html=False, include_plotlyjs=False)}
        {pio.to_html(pos_chart, full_html=False, include_plotlyjs=False)}
        <h2>交易记录 (最近50笔)</h2>
        <table>
            <tr><th>日期</th><th>股票</th><th>方向</th><th>价格</th><th>数量</th><th>费用</th></tr>
            {trade_rows}
        </table>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def export_png(nav_history: list[dict], output_dir: str = "reports/"):
    """Export charts as PNG images."""
    os.makedirs(output_dir, exist_ok=True)
    nav_chart = create_nav_chart(nav_history)
    dd_chart = create_drawdown_chart(nav_history)

    try:
        pio.write_image(nav_chart, os.path.join(output_dir, "nav_curve.png"))
        pio.write_image(dd_chart, os.path.join(output_dir, "drawdown.png"))
    except Exception as e:
        print(f"PNG export requires kaleido: {e}")
