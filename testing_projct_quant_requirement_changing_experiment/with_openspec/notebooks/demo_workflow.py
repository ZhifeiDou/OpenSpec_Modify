"""
A股有色金属多因子量化系统 — 完整工作流演示

Usage:
    python notebooks/demo_workflow.py

This script demonstrates the full pipeline:
    1. Data update
    2. Universe generation
    3. Factor calculation
    4. Signal generation
    5. Backtest
    6. Report
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml
import pandas as pd


def load_config():
    config_path = project_root / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def demo_pipeline():
    config = load_config()
    print("=" * 60)
    print("A股有色金属多因子量化系统 — 工作流演示")
    print("=" * 60)

    # Step 1: Data Update
    print("\n[Step 1] 数据更新")
    print("-" * 40)
    from src.data.pipeline import DataPipeline
    pipeline = DataPipeline(config)
    print("  数据管道已初始化")
    print("  提示: 运行 pipeline.run() 拉取实际数据")
    print("  跳过实际API调用（演示模式）")

    # Step 2: Universe
    print("\n[Step 2] 股票池构建")
    print("-" * 40)
    from src.universe.classifier import get_universe
    print("  有色金属行业代码: 801050 (申万)")
    print("  过滤条件: 排除ST、停牌、上市<60天、日成交<500万")
    print("  子板块映射: copper→cu, aluminum→al, gold→au, lithium→LC")

    # Step 3: Factor Calculation
    print("\n[Step 3] 因子计算")
    print("-" * 40)
    print("  因子类别与权重:")
    weights = config["factors"]["weights"]
    for cat, w in weights.items():
        print(f"    {cat:15s}: {w:.0%}")
    print("  标准化: MAD去极值(3倍) + Z-Score标准化")

    # Step 4: Scoring & Signal
    print("\n[Step 4] 打分与信号生成")
    print("-" * 40)
    strategy = config["strategy"]
    print(f"  打分模式: {config['factors']['scoring_mode']}")
    print(f"  最大持仓: {strategy['max_stocks']} 只")
    print(f"  单票上限: {strategy['max_single_weight']:.0%}")
    print(f"  子板块上限: {strategy['max_subsector_weight']:.0%}")
    print(f"  调仓频率: {strategy['rebalance_freq']}")

    # Step 5: Risk Management
    print("\n[Step 5] 风控规则")
    print("-" * 40)
    risk = config["risk"]
    print(f"  硬止损: {risk['hard_stop_atr_multiple']}x ATR")
    print(f"  移动止损: 盈利>{risk['trailing_stop_activation']:.0%}后激活, "
          f"回落>{risk['trailing_stop_drop']:.0%}触发")
    print(f"  回撤减仓: {risk['max_drawdown_reduce']:.0%}")
    print(f"  回撤清仓: {risk['max_drawdown_liquidate']:.0%}")

    # Step 6: Backtest
    print("\n[Step 6] 回测配置")
    print("-" * 40)
    bt = config["backtest"]
    print(f"  初始资金: ¥{bt['initial_capital']:,.0f}")
    print(f"  印花税: {bt['stamp_tax']:.2%} (卖出)")
    print(f"  佣金: {bt['commission']:.2%} (双边)")
    print(f"  滑点: {bt['slippage']:.2%}")
    print(f"  无风险利率: {bt['risk_free_rate']:.1%}")

    # Step 7: Report
    print("\n[Step 7] 报告输出")
    print("-" * 40)
    report = config["report"]
    print(f"  格式: {report['format']}")
    print(f"  输出目录: {report['output_dir']}")
    print("  包含: 净值曲线、回撤图、持仓表、因子热力图、IC跟踪")

    print("\n" + "=" * 60)
    print("演示完成! 实际使用请运行:")
    print("  python main.py update       # 更新数据")
    print("  python main.py universe     # 查看股票池")
    print("  python main.py factors      # 计算因子")
    print("  python main.py signal       # 生成信号")
    print("  python main.py backtest --start 2023-01-01 --end 2024-12-31")
    print("  python main.py report       # 生成报告")
    print("=" * 60)


if __name__ == "__main__":
    demo_pipeline()
