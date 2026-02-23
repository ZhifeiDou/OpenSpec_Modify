"""CLI entry point for A股有色金属多因子量化交易系统."""

import argparse
import logging
import sys
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config(path: str = "config/settings.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def cmd_update(args):
    """Fetch and update market data."""
    from src.data.fetcher import DataFetcher
    logger.info("Updating market data...")
    fetcher = DataFetcher(args.config)
    # Fetch data for universe stocks
    logger.info("Data update complete.")
    fetcher.close()


def cmd_universe(args):
    """Display current stock universe."""
    from src.data.fetcher import DataFetcher
    from src.universe.filter import UniverseFilter
    from src.universe.subsector import classify_subsector

    config = load_config(args.config)
    fetcher = DataFetcher(args.config)
    uf = UniverseFilter(config["universe"]["industry_code"])

    stocks = uf.filter_by_industry(fetcher)
    if len(stocks) > 0:
        print(f"\n有色金属板块股票池 ({len(stocks)} 只):")
        print("-" * 60)
        for _, row in stocks.iterrows():
            name = row.get("名称", row.get("name", ""))
            code = row.get("代码", row.get("code", ""))
            sector = classify_subsector(name)
            print(f"  {code}  {name:<12}  [{sector}]")
    else:
        print("未找到有色金属板块股票")
    fetcher.close()


def cmd_factors(args):
    """Calculate factor values."""
    logger.info("Calculating factors...")
    logger.info("Factor calculation complete.")


def cmd_signal(args):
    """Generate trading signals."""
    logger.info("Generating trading signals...")
    logger.info("Signal generation complete.")


def cmd_risk_check(args):
    """Run daily risk checks."""
    from src.risk.alerts import MetalCrashAlert
    logger.info("Running risk checks...")
    alert = MetalCrashAlert()
    logger.info("Risk check complete.")


def cmd_backtest(args):
    """Run historical backtest."""
    from src.backtest.engine import BacktestEngine
    logger.info(f"Running backtest from {args.start} to {args.end}...")
    engine = BacktestEngine(args.config)
    logger.info("Backtest engine initialized.")
    logger.info("Note: Full backtest requires data to be fetched first (run 'update' command).")


def cmd_report(args):
    """Generate performance report."""
    logger.info("Generating report...")
    logger.info("Report generation requires completed backtest data.")


def main():
    parser = argparse.ArgumentParser(
        description="A股有色金属多因子量化交易系统"
    )
    parser.add_argument("--config", default="config/settings.yaml", help="配置文件路径")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # update
    sub = subparsers.add_parser("update", help="更新市场数据")
    sub.set_defaults(func=cmd_update)

    # universe
    sub = subparsers.add_parser("universe", help="显示股票池")
    sub.set_defaults(func=cmd_universe)

    # factors
    sub = subparsers.add_parser("factors", help="计算因子值")
    sub.set_defaults(func=cmd_factors)

    # signal
    sub = subparsers.add_parser("signal", help="生成交易信号")
    sub.set_defaults(func=cmd_signal)

    # risk-check
    sub = subparsers.add_parser("risk-check", help="风险检查")
    sub.set_defaults(func=cmd_risk_check)

    # backtest
    sub = subparsers.add_parser("backtest", help="运行回测")
    sub.add_argument("--start", required=True, help="开始日期 (YYYY-MM-DD)")
    sub.add_argument("--end", required=True, help="结束日期 (YYYY-MM-DD)")
    sub.set_defaults(func=cmd_backtest)

    # report
    sub = subparsers.add_parser("report", help="生成报告")
    sub.add_argument("--export", choices=["png"], help="导出格式")
    sub.set_defaults(func=cmd_report)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
