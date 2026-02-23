"""
A股有色金属多因子量化交易系统
CLI entry point
"""
import argparse
import sys
from pathlib import Path

import yaml


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_update(args, config):
    """Update market data from data sources."""
    from src.data.pipeline import DataPipeline
    from src.universe.classifier import get_universe

    pipeline = DataPipeline(config)

    # Auto-resolve symbols from universe when updating stock/flow data
    symbols = None
    cats = args.categories if args.categories else None
    need_symbols = cats is None or "stock" in cats or "flow" in cats
    if need_symbols:
        try:
            universe = get_universe(config)
            symbols = universe["symbol"].tolist() if not universe.empty else None
        except Exception as e:
            print(f"Warning: could not load universe for symbols: {e}")

    pipeline.run(
        symbols=symbols,
        categories=cats,
        force_refresh=args.force,
    )


def cmd_universe(args, config):
    """Show current stock universe."""
    from src.universe.classifier import get_universe

    date = args.date
    universe = get_universe(config, date=date)
    print(f"\n有色金属股票池 ({date or '最新'}):")
    print(f"  总计: {len(universe)} 只股票")
    for subsector, stocks in universe.groupby("subsector"):
        print(f"  {subsector}: {len(stocks)} 只")
    if args.detail:
        print(universe.to_string(index=False))


def cmd_factors(args, config):
    """Calculate factor values for current universe."""
    from src.factors.base import compute_all_factors

    date = args.date
    factor_matrix = compute_all_factors(config, date=date)
    print(f"\n因子矩阵: {factor_matrix.shape[0]} 只股票 x {factor_matrix.shape[1]} 个因子")
    if args.detail:
        print(factor_matrix.round(3).to_string())


def cmd_signal(args, config):
    """Generate trading signals."""
    from src.strategy.signal import generate_signals

    signals = generate_signals(config, date=args.date)
    print("\n交易信号:")
    for sig in signals:
        print(f"  {sig['action']:6s} {sig['symbol']} ({sig['name']}) "
              f"目标权重: {sig['target_weight']:.1%}")


def cmd_risk_check(args, config):
    """Run daily risk check."""
    from src.risk.alerts import run_daily_risk_check

    report = run_daily_risk_check(config)
    print("\n风控检查报告:")
    print(f"  组合回撤: {report['drawdown']:.2%}")
    print(f"  止损预警: {len(report['stop_loss_alerts'])} 只")
    print(f"  金属急跌: {len(report['metal_crash_alerts'])} 个品种")


def cmd_backtest(args, config):
    """Run strategy backtest."""
    import json
    from src.backtest.engine import BacktestEngine

    engine = BacktestEngine(config)
    result = engine.run(
        start_date=args.start,
        end_date=args.end,
    )
    metrics = result.metrics
    print("\n回测结果:")
    print(f"  年化收益: {metrics['annual_return']:.2%}")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"  胜率:     {metrics['win_rate']:.2%}")
    print(f"  总交易成本: {metrics['total_costs']:.0f} 元")

    # Save results for report command
    output_dir = Path(config.get("report", {}).get("output_dir", "reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    result.nav_series.to_csv(output_dir / "last_nav.csv")
    if not result.trade_log.empty:
        result.trade_log.to_csv(output_dir / "last_trades.csv", index=False)
    with open(output_dir / "last_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n结果已保存至 {output_dir}/")


def cmd_report(args, config):
    """Generate performance report."""
    import json
    import pandas as pd
    from src.report.exporter import export_report

    report_dir = Path(config.get("report", {}).get("output_dir", "reports"))

    # Load saved backtest results
    nav_series = None
    trade_log = None
    metrics = None

    nav_path = report_dir / "last_nav.csv"
    if nav_path.exists():
        df = pd.read_csv(nav_path, index_col=0)
        nav_series = df.iloc[:, 0]

    trades_path = report_dir / "last_trades.csv"
    if trades_path.exists():
        trade_log = pd.read_csv(trades_path)

    metrics_path = report_dir / "last_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics = json.load(f)

    output_path = export_report(
        config, nav_series=nav_series, trade_log=trade_log, metrics=metrics
    )
    print(f"\n报告已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="A股有色金属多因子量化系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", default="config/settings.yaml", help="配置文件路径"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # update
    p_update = subparsers.add_parser("update", help="更新市场数据")
    p_update.add_argument("--categories", nargs="*", help="指定数据类别 (stock futures macro flow)")
    p_update.add_argument("--force", action="store_true", help="强制全量刷新")

    # universe
    p_universe = subparsers.add_parser("universe", help="查看股票池")
    p_universe.add_argument("--date", default=None, help="查询日期 (YYYY-MM-DD)")
    p_universe.add_argument("--detail", action="store_true", help="显示详细列表")

    # factors
    p_factors = subparsers.add_parser("factors", help="计算因子")
    p_factors.add_argument("--date", default=None, help="计算日期")
    p_factors.add_argument("--detail", action="store_true", help="显示因子矩阵")

    # signal
    p_signal = subparsers.add_parser("signal", help="生成交易信号")
    p_signal.add_argument("--date", default=None, help="信号日期")

    # risk-check
    p_risk = subparsers.add_parser("risk-check", help="风控检查")

    # backtest
    p_bt = subparsers.add_parser("backtest", help="运行回测")
    p_bt.add_argument("--start", required=True, help="开始日期 (YYYY-MM-DD)")
    p_bt.add_argument("--end", required=True, help="结束日期 (YYYY-MM-DD)")

    # report
    p_report = subparsers.add_parser("report", help="生成报告")
    p_report.add_argument("--source", default="backtest", choices=["backtest", "live"], help="数据来源")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)

    commands = {
        "update": cmd_update,
        "universe": cmd_universe,
        "factors": cmd_factors,
        "signal": cmd_signal,
        "risk-check": cmd_risk_check,
        "backtest": cmd_backtest,
        "report": cmd_report,
    }
    commands[args.command](args, config)


if __name__ == "__main__":
    main()
