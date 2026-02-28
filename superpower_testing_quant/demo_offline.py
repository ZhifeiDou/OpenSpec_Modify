"""
A股有色金属多因子量化机器人 - 离线Demo
使用模拟数据演示完整流程，无需网络连接
"""
import sys
import io
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Fix Windows encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from quant_bot.factors.momentum import MomentumFactor
from quant_bot.factors.value import ValueFactor
from quant_bot.factors.volatility import VolatilityFactor
from quant_bot.factors.quality import QualityFactor
from quant_bot.strategy.multi_factor import MultiFactorStrategy
from quant_bot.backtest.engine import BacktestEngine
from quant_bot.risk.manager import RiskManager
from quant_bot.signal.generator import SignalGenerator


# ============================================================
# 1. 生成模拟的有色金属板块股票数据
# ============================================================
STOCKS = {
    "601899": {"name": "紫金矿业", "base_price": 18.0, "volatility": 0.03, "trend": 0.0005},
    "600489": {"name": "中金黄金", "base_price": 12.0, "volatility": 0.025, "trend": 0.0003},
    "603799": {"name": "华友钴业", "base_price": 35.0, "volatility": 0.04, "trend": -0.0002},
    "002460": {"name": "赣锋锂业", "base_price": 45.0, "volatility": 0.045, "trend": 0.0001},
    "600362": {"name": "江西铜业", "base_price": 22.0, "volatility": 0.028, "trend": 0.0004},
    "000878": {"name": "云南铜业", "base_price": 14.0, "volatility": 0.032, "trend": -0.0001},
    "600547": {"name": "山东黄金", "base_price": 28.0, "volatility": 0.022, "trend": 0.0006},
    "002466": {"name": "天齐锂业", "base_price": 55.0, "volatility": 0.05, "trend": -0.0003},
    "600459": {"name": "贵研铂业", "base_price": 16.0, "volatility": 0.035, "trend": 0.0002},
    "002171": {"name": "楚江新材", "base_price": 8.0,  "volatility": 0.038, "trend": 0.0001},
}

def generate_stock_data(code, info, start="2024-01-02", periods=300):
    """Generate realistic synthetic daily data for one stock."""
    np.random.seed(hash(code) % 2**31)
    dates = pd.bdate_range(start, periods=periods)

    # Price simulation with trend + mean reversion + random walk
    returns = np.random.normal(info["trend"], info["volatility"], periods)
    prices = info["base_price"] * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "open": prices * (1 + np.random.uniform(-0.01, 0.01, periods)),
        "close": prices,
        "high": prices * (1 + np.abs(np.random.normal(0, 0.015, periods))),
        "low": prices * (1 - np.abs(np.random.normal(0, 0.015, periods))),
        "volume": np.random.randint(50000, 500000, periods),
        "pe_ttm": np.random.uniform(10, 40, periods),
        "pb": np.random.uniform(1.0, 5.0, periods),
        "dividend_yield_ttm": np.random.uniform(0.5, 3.0, periods),
        "roe": np.random.uniform(5, 25, periods),
        "gross_margin": np.random.uniform(10, 40, periods),
    })
    return df


print("=" * 60)
print("  A股有色金属多因子量化机器人 - 离线Demo")
print("=" * 60)

# ============================================================
# 2. 生成所有股票数据
# ============================================================
print("\n[1/5] 生成模拟数据...")
stocks_data = {}
stock_names = {}
for code, info in STOCKS.items():
    stocks_data[code] = generate_stock_data(code, info)
    stock_names[code] = info["name"]
    print(f"  {code} {info['name']:6s} | {len(stocks_data[code])} 交易日 | "
          f"价格区间: {stocks_data[code]['close'].min():.2f} - {stocks_data[code]['close'].max():.2f}")

# ============================================================
# 3. 因子计算演示
# ============================================================
print("\n[2/5] 计算多因子...")
factors = {
    "momentum": MomentumFactor(lookback=20),
    "value": ValueFactor(),
    "volatility": VolatilityFactor(lookback=20),
    "quality": QualityFactor(),
}

# Show factor values for one stock
demo_code = "601899"
demo_df = stocks_data[demo_code].copy()
for f in factors.values():
    demo_df = f.calculate(demo_df)

print(f"\n  紫金矿业(601899) 最新因子值:")
last = demo_df.iloc[-1]
print(f"    动量因子:  return_20d={last.get('return_n', 0):.4f}  RSI={last.get('rsi', 0):.1f}  价格位置={last.get('price_position', 0):.2f}")
print(f"    价值因子:  EP={last.get('ep_ratio', 0):.4f}  BP={last.get('bp_ratio', 0):.4f}  股息率={last.get('div_yield', 0):.2f}%")
print(f"    波动因子:  历史波动率={last.get('hist_volatility', 0):.4f}  ATR={last.get('atr', 0):.4f}")
print(f"    质量因子:  ROE={last.get('roe_score', 0):.1f}%  毛利率={last.get('gross_margin_score', 0):.1f}%")

# ============================================================
# 4. 运行回测
# ============================================================
print("\n[3/5] 运行回测...")
config = {
    "factors": {
        "momentum": {"weight": 0.3, "lookback": 20},
        "value": {"weight": 0.3},
        "volatility": {"weight": 0.2},
        "quality": {"weight": 0.2},
    },
    "strategy": {"top_n": 5, "rebalance": "daily"},
    "backtest": {
        "start_date": "2024-01-01",
        "end_date": "2025-03-01",
        "initial_capital": 1000000,
        "commission": 0.001,
        "slippage": 0.002,
    },
    "risk": {
        "max_position_pct": 0.3,
        "stop_loss_pct": 0.08,
        "take_profit_pct": 0.20,
    },
}

engine = BacktestEngine(config)
result = engine.run(stocks_data, stock_names)

metrics = result["metrics"]
print(f"\n  {'=' * 40}")
print(f"  回测结果 (初始资金: 100万)")
print(f"  {'=' * 40}")
print(f"  总收益率:     {metrics['total_return']:>10.2%}")
print(f"  年化收益率:   {metrics['annual_return']:>10.2%}")
print(f"  最大回撤:     {metrics['max_drawdown']:>10.2%}")
print(f"  夏普比率:     {metrics['sharpe_ratio']:>10.4f}")
print(f"  胜率:         {metrics['win_rate']:>10.2%}")
print(f"  交易天数:     {metrics['total_trades']:>10d}")
print(f"  最终资产:     {result['portfolio_values'][-1]['value']:>10,.0f} 元")
print(f"  {'=' * 40}")

# ============================================================
# 5. 生成今日信号
# ============================================================
print("\n[4/5] 生成交易信号...")

# Score all stocks using latest data
latest_factors = {}
for code, df in stocks_data.items():
    result_df = df.copy()
    for f in factors.values():
        result_df = f.calculate(result_df)
    last_row = result_df.iloc[-1].to_dict()
    if pd.notna(last_row.get("return_n")):
        latest_factors[code] = last_row

strategy = MultiFactorStrategy(config)
scores = strategy.score_stocks(latest_factors)
selected = strategy.select_top_n(scores)
target_positions = strategy.generate_target_positions(selected)

risk_mgr = RiskManager(config)
target_positions = risk_mgr.check_position_limits(target_positions)

os.makedirs("output/signals", exist_ok=True)
sig_gen = SignalGenerator("output/signals")
signals = sig_gen.generate_signals(
    date="2025-02-26",
    current_holdings={},
    target_positions=target_positions,
    stock_names=stock_names,
    scores=scores,
)
sig_gen.save_to_csv(signals, "2025-02-26")

print(f"\n  今日交易信号 (2025-02-26)")
print(f"  {'─' * 55}")
print(f"  {'代码':8s} {'名称':8s} {'操作':6s} {'目标仓位':>10s} {'综合得分':>10s}")
print(f"  {'─' * 55}")
for s in sorted(signals, key=lambda x: x["score"], reverse=True):
    print(f"  {s['code']:8s} {s['name']:8s} {s['action']:6s} {s['target_weight']:>10.2%} {s['score']:>10.4f}")
print(f"  {'─' * 55}")

print(f"\n  因子得分排名 (全部{len(scores)}只):")
for i, (code, score) in enumerate(sorted(scores.items(), key=lambda x: x[1], reverse=True)):
    marker = " ***" if code in selected else ""
    print(f"  {i+1:>3}. {code} {stock_names[code]:8s} | 得分: {score:>8.4f}{marker}")

# ============================================================
# 6. 画图
# ============================================================
print("\n[5/5] 生成回测净值曲线图...")

os.makedirs("output/reports", exist_ok=True)
pv = result["portfolio_values"]
dates = [p["date"] for p in pv]
values = [p["value"] for p in pv]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]})

# Portfolio value
ax1.plot(range(len(dates)), values, label="Portfolio", linewidth=1.5, color="#2196F3")
ax1.axhline(y=1000000, color="gray", linestyle="--", alpha=0.5, label="Initial Capital")
ax1.fill_between(range(len(dates)), 1000000, values,
                 where=[v >= 1000000 for v in values], alpha=0.15, color="green")
ax1.fill_between(range(len(dates)), 1000000, values,
                 where=[v < 1000000 for v in values], alpha=0.15, color="red")
ax1.set_title("Non-ferrous Metals Multi-Factor Strategy - Portfolio Value", fontsize=14)
ax1.set_ylabel("Portfolio Value (CNY)")
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.3)
step = max(len(dates) // 8, 1)
ax1.set_xticks(range(0, len(dates), step))
ax1.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)

# Drawdown
peak_values = pd.Series(values).cummax()
drawdown = (pd.Series(values) - peak_values) / peak_values
ax2.fill_between(range(len(dates)), 0, drawdown, color="red", alpha=0.4)
ax2.set_title("Drawdown", fontsize=12)
ax2.set_ylabel("Drawdown %")
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(0, len(dates), step))
ax2.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)

plt.tight_layout()
chart_path = "output/reports/demo_backtest.png"
plt.savefig(chart_path, dpi=150)
plt.close()

print(f"\n  净值曲线图已保存: {chart_path}")
print(f"  信号文件已保存: output/signals/signals_2025-02-26.csv")
print(f"\n{'=' * 60}")
print("  Demo 完成! 网络恢复后可用 --mode signal 获取实时数据")
print("=" * 60)
