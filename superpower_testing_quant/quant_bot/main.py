"""
A股有色金属多因子量化交易机器人 - 主入口

Usage:
    python -m quant_bot.main --mode backtest
    python -m quant_bot.main --mode simulate
    python -m quant_bot.main --mode signal
"""
import argparse
import logging
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from quant_bot.utils.helpers import load_config, setup_logging
from quant_bot.data.fetcher import DataFetcher
from quant_bot.data.cache import DataCache
from quant_bot.data.processor import DataProcessor
from quant_bot.factors.momentum import MomentumFactor
from quant_bot.factors.value import ValueFactor
from quant_bot.factors.volatility import VolatilityFactor
from quant_bot.factors.quality import QualityFactor
from quant_bot.strategy.multi_factor import MultiFactorStrategy
from quant_bot.backtest.engine import BacktestEngine
from quant_bot.risk.manager import RiskManager
from quant_bot.signal.generator import SignalGenerator

logger = logging.getLogger(__name__)


def fetch_all_data(config):
    """Fetch and cache data for all sector stocks."""
    fetcher = DataFetcher()
    cache = DataCache(config.get("paths", {}).get("data_cache", "data_cache"))
    processor = DataProcessor()

    sector = config["stock_pool"]["sector"]
    logger.info(f"Fetching stock list for sector: {sector}")
    stocks_df = fetcher.get_sector_stocks(sector)
    stock_codes = stocks_df["code"].tolist()
    stock_names = dict(zip(stocks_df["code"], stocks_df["name"]))

    start = config["backtest"]["start_date"].replace("-", "")
    end = config["backtest"]["end_date"].replace("-", "")

    stocks_data = {}
    for code in stock_codes:
        try:
            if cache.is_cached(code, "daily"):
                daily_df = cache.load(code, "daily")
            else:
                daily_df = fetcher.get_stock_daily(code, start, end)
                cache.save(code, "daily", daily_df)

            if cache.is_cached(code, "valuation"):
                val_df = cache.load(code, "valuation")
            else:
                val_df = fetcher.get_stock_valuation(code)
                cache.save(code, "valuation", val_df)

            daily_df = processor.clean_daily_data(daily_df)
            merged = processor.merge_stock_data(daily_df, val_df)

            if len(merged) > 30:
                stocks_data[code] = merged
                logger.info(f"Loaded {code} ({stock_names.get(code, '')}): {len(merged)} rows")

        except Exception as e:
            logger.warning(f"Skipping {code}: {e}")
            continue

    logger.info(f"Successfully loaded {len(stocks_data)} / {len(stock_codes)} stocks")
    return stocks_data, stock_names


def run_backtest(config):
    """Run full backtest."""
    logger.info("=== Starting Backtest ===")
    stocks_data, stock_names = fetch_all_data(config)

    if not stocks_data:
        logger.error("No stock data loaded, aborting backtest")
        return

    engine = BacktestEngine(config)
    result = engine.run(stocks_data, stock_names)

    print("\n" + "=" * 50)
    print("回测结果")
    print("=" * 50)
    metrics = result["metrics"]
    print(f"总收益率:     {metrics['total_return']:.2%}")
    print(f"年化收益率:   {metrics['annual_return']:.2%}")
    print(f"最大回撤:     {metrics['max_drawdown']:.2%}")
    print(f"夏普比率:     {metrics['sharpe_ratio']:.4f}")
    print(f"胜率:         {metrics['win_rate']:.2%}")
    print(f"交易天数:     {metrics['total_trades']}")
    print("=" * 50)

    output_dir = config.get("paths", {}).get("output", "output")
    os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)

    pv = result["portfolio_values"]
    dates = [p["date"] for p in pv]
    values = [p["value"] for p in pv]

    plt.figure(figsize=(14, 6))
    plt.plot(dates, values, label="Portfolio", linewidth=1.5)
    plt.axhline(y=config["backtest"]["initial_capital"], color="gray", linestyle="--", label="Initial Capital")
    plt.title("有色金属多因子策略 - 回测净值曲线")
    plt.xlabel("日期")
    plt.ylabel("组合价值 (元)")
    plt.legend()
    plt.xticks(rotation=45)
    step = max(len(dates) // 10, 1)
    plt.xticks(range(0, len(dates), step), [dates[i] for i in range(0, len(dates), step)])
    plt.tight_layout()

    chart_path = os.path.join(output_dir, "reports", "backtest_result.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"\n净值曲线已保存: {chart_path}")


def run_signal(config):
    """Generate today's trading signals."""
    logger.info("=== Generating Trading Signals ===")
    stocks_data, stock_names = fetch_all_data(config)

    if not stocks_data:
        logger.error("No stock data loaded")
        return

    factors = {
        "momentum": MomentumFactor(config["factors"].get("momentum", {}).get("lookback", 20)),
        "value": ValueFactor(),
        "volatility": VolatilityFactor(config["factors"].get("volatility", {}).get("lookback", 20)),
        "quality": QualityFactor(),
    }

    latest_factors = {}
    for code, df in stocks_data.items():
        result = df.copy()
        for factor in factors.values():
            result = factor.calculate(result)
        if not result.empty:
            last_row = result.iloc[-1].to_dict()
            if pd.notna(last_row.get("return_n")):
                latest_factors[code] = last_row

    strategy = MultiFactorStrategy(config)
    scores = strategy.score_stocks(latest_factors)
    selected = strategy.select_top_n(scores)
    target_positions = strategy.generate_target_positions(selected)

    risk_mgr = RiskManager(config)
    target_positions = risk_mgr.check_position_limits(target_positions)

    sig_gen = SignalGenerator(
        os.path.join(config.get("paths", {}).get("output", "output"), "signals")
    )
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    signals = sig_gen.generate_signals(
        date=today,
        current_holdings={},
        target_positions=target_positions,
        stock_names=stock_names,
        scores=scores,
    )
    sig_gen.save_to_csv(signals, today)

    print("\n" + "=" * 50)
    print(f"今日交易信号 ({today})")
    print("=" * 50)
    for s in signals:
        print(f"  {s['code']} {s['name']:10s} | {s['action']:4s} | "
              f"目标仓位: {s['target_weight']:.2%} | 得分: {s['score']:.4f}")
    print("=" * 50)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n因子得分 Top 10:")
    for code, score in sorted_scores:
        name = stock_names.get(code, code)
        print(f"  {code} {name:10s} | 得分: {score:.4f}")


def main():
    import io, sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="A-share Non-ferrous Metals Quant Bot")
    parser.add_argument("--mode", choices=["backtest", "simulate", "signal"],
                        default="signal", help="Run mode: backtest/simulate/signal")
    parser.add_argument("--config", default=None, help="Config file path")
    args = parser.parse_args()

    setup_logging()
    config = load_config(args.config)

    if args.mode == "backtest":
        run_backtest(config)
    elif args.mode == "signal":
        run_signal(config)
    elif args.mode == "simulate":
        run_signal(config)
        print("\n模拟盘模式：请设置定时任务每日运行此命令")


if __name__ == "__main__":
    main()
