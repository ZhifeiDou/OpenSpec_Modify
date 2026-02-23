## Why

A股有色金属板块受大宗商品价格、宏观经济周期与资金流向多重因素驱动，适合采用多因子模型进行系统化、纪律化的量化投资。当前缺乏针对该板块的专用量化交易系统，需要构建一套从数据获取到回测验证的完整量化交易平台，严格遵守A股T+1交易规则与涨跌停限制。

## What Changes

- 构建多数据源数据管道，支持 AKShare（主）、BaoStock、Tushare 自动切换与本地 SQLite 缓存
- 实现有色金属板块股票池自动筛选，覆盖铜、铝、黄金、锂、钴、锌、稀土等子行业分类
- 开发 16 因子引擎，涵盖商品（35%）、基本面（25%）、技术（20%）、资金流（15%）、宏观（5%）五大类
- 实现多因子综合评分策略，支持等权加权和 IC 加权两种打分模式
- 构建完整风险管理体系：硬止损（2x ATR）、追踪止损（峰值回撤 8%）、组合回撤分级控制（15% 减仓 / 20% 清仓）、单股与子行业仓位上限
- 开发事件驱动日频回测引擎，模拟 A 股真实交易规则（T+1、涨跌停板、停牌处理、交易成本）
- 生成基于 Plotly 的交互式 HTML 回测报告
- 实现市场择时信号模块（黄金对冲、PMI 方向等）

## Capabilities

### New Capabilities

- `data-pipeline`: 多数据源数据获取、智能切换、本地 SQLite 缓存与增量更新
- `stock-universe`: 有色金属板块股票池筛选、子行业分类映射与动态更新
- `factor-engine`: 16 因子计算引擎，涵盖五大类因子的标准化、去极值与因子值输出
- `scoring-strategy`: 多因子综合评分、股票排序选择与仓位分配策略
- `risk-management`: 止损体系、组合回撤监控、仓位限制与金属价格预警
- `backtest-engine`: 事件驱动日频回测引擎，完整模拟 A 股交易规则
- `report-dashboard`: Plotly 交互式回测绩效报告与可视化导出
- `market-timing`: 市场择时信号生成（黄金对冲信号、PMI 方向信号等）

### Modified Capabilities

（无，本次为全新系统构建）

## Impact

- **新增模块**: `src/data/`, `src/universe/`, `src/factors/`, `src/strategy/`, `src/risk/`, `src/backtest/`, `src/report/`, `src/timing/`
- **配置文件**: `config/settings.yaml` — 数据源优先级、因子权重、风控阈值、回测参数
- **CLI 入口**: `main.py` — 提供 update / universe / factors / signal / risk-check / backtest / report 七个子命令
- **外部依赖**: akshare, baostock, tushare, pandas, numpy, scipy, plotly, pandas-ta, pytest
- **本地存储**: SQLite 数据库用于行情与基本面数据缓存
