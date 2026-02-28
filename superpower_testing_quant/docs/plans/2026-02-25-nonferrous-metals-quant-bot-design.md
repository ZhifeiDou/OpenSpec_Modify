# A股有色金属多因子量化交易机器人 - 设计文档

## 概述

基于 AKShare 数据源的 A 股有色金属板块多因子量化交易系统，支持回测、模拟盘和日度信号生成。

## 技术栈

- Python 3.10+
- AKShare: A股数据获取
- Pandas/NumPy: 数据处理与因子计算
- PyYAML: 配置管理
- Matplotlib: 回测报告可视化

## 项目结构

```
superpower_testing/
├── config/
│   └── config.yaml
├── quant_bot/
│   ├── __init__.py
│   ├── main.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   ├── cache.py
│   │   └── processor.py
│   ├── factors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── momentum.py
│   │   ├── value.py
│   │   ├── volatility.py
│   │   └── quality.py
│   ├── strategy/
│   │   ├── __init__.py
│   │   └── multi_factor.py
│   ├── backtest/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── signal/
│   │   ├── __init__.py
│   │   └── generator.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── output/
├── data_cache/
├── requirements.txt
└── README.md
```

## 数据层

- **fetcher.py**: AKShare 获取有色金属板块成分股列表、日K线、基本面数据
- **cache.py**: CSV 本地缓存，按股票代码+日期命名，避免重复请求
- **processor.py**: 数据清洗（停牌、涨跌停、缺失值），输出统一 DataFrame

## 因子库

所有因子继承 BaseFactor，实现 `calculate(df) -> Series` 接口：

- **动量因子**: N日收益率、RSI、价格位置
- **价值因子**: PE倒数、PB倒数、股息率
- **波动率因子**: 历史波动率、ATR
- **质量因子**: ROE、毛利率

## 策略引擎

1. 计算全部因子值
2. 截面 z-score 标准化
3. 加权综合打分（权重配置化）
4. 按得分降序选取前N只股票
5. 等权分配资金

## 回测引擎

- 按日迭代，每日收盘后运行策略
- 模拟交易：比较当前持仓与目标持仓，生成买卖订单
- 扣除手续费(0.1%)和滑点(0.2%)
- 计算组合净值，对比有色金属板块指数基准
- 输出：年化收益率、最大回撤、夏普比率、胜率、盈亏比

## 风控模块

- 单股最大持仓 30%
- 个股止损 8%、止盈 20%
- 最大回撤熔断（可选）

## 信号输出

- CSV 格式：日期、代码、名称、操作、目标仓位、综合得分
- 控制台日志
- 保存到 output/signals/

## 运行模式

```bash
python -m quant_bot.main --mode backtest    # 回测
python -m quant_bot.main --mode simulate    # 模拟盘
python -m quant_bot.main --mode signal      # 查看最新信号
```

## 配置文件

```yaml
stock_pool:
  sector: "有色金属"

factors:
  momentum: { weight: 0.3, lookback: 20 }
  value: { weight: 0.3 }
  volatility: { weight: 0.2 }
  quality: { weight: 0.2 }

strategy:
  top_n: 5
  rebalance: "daily"

backtest:
  start_date: "2023-01-01"
  end_date: "2025-12-31"
  initial_capital: 1000000
  commission: 0.001
  slippage: 0.002

risk:
  max_position_pct: 0.3
  stop_loss_pct: 0.08
  take_profit_pct: 0.20
```
