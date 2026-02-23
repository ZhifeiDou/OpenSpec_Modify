# A股有色金属多因子量化交易系统

A-share non-ferrous metals multi-factor quantitative trading system.

## 系统架构

```
src/
├── data/           # 数据层：数据源适配器、本地存储、数据管道
├── universe/       # 股票池：行业分类、过滤、子板块映射
├── factors/        # 因子引擎：16个因子 (基本面/技术/商品/宏观/资金流)
├── strategy/       # 策略层：多因子打分、仓位分配、择时、信号生成
├── risk/           # 风控：止损、回撤监控、仓位管理、预警
├── backtest/       # 回测引擎：事件驱动、A股规则模拟、绩效评估
└── report/         # 报告：Plotly交互式图表、HTML/PNG导出
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 更新数据

```bash
python main.py update                    # 全量更新
python main.py update --categories stock futures  # 指定类别
python main.py update --force            # 强制全量刷新
```

### 3. 查看股票池

```bash
python main.py universe                  # 概览
python main.py universe --detail         # 详细列表
```

### 4. 计算因子

```bash
python main.py factors                   # 最新因子
python main.py factors --date 2024-06-30 --detail
```

### 5. 生成交易信号

```bash
python main.py signal                    # 当前信号
```

### 6. 运行回测

```bash
python main.py backtest --start 2023-01-01 --end 2024-12-31
```

### 7. 生成报告

```bash
python main.py report                    # HTML报告
```

## 因子体系

| 类别 | 权重 | 因子 |
|------|------|------|
| 商品 | 35% | 金属价格动量60d、期货基差、库存周变化 |
| 基本面 | 25% | PB百分位3y、毛利率环比、ROE_TTM、EV/EBITDA |
| 技术面 | 20% | 动量60d(skip5)、反转5d、换手率20d、已实现波动率20d |
| 资金流 | 15% | 融资余额变化5d、北向资金净买入10d |
| 宏观 | 5% | PMI方向、美元指数动量、M1增速方向 |

## 风控规则

- **硬止损**: 亏损 > 2x ATR 触发卖出 (T+1生效)
- **移动止损**: 盈利 > 10% 后激活，从高点回落 8% 触发
- **回撤减仓**: 组合回撤 > 15% → 减仓至50%
- **回撤清仓**: 组合回撤 > 20% → 建议全部清仓
- **金属急跌预警**: 单日跌幅 > 3% → 预警受影响持仓

## A股交易规则模拟

- T+1：买入当日不可卖出
- 涨跌停：涨停不买入，跌停不卖出 (±10%)
- 停牌：成交量为0时冻结持仓
- 交易成本：印花税0.05%(卖出) + 佣金0.03%(双边,最低5元) + 滑点0.15%

## 配置

所有参数在 `config/settings.yaml` 中配置，包括：
- 数据源优先级和API延迟
- 股票池过滤条件
- 因子权重和打分模式
- 持仓约束 (单票上限10%，子板块上限25%)
- 调仓频率和择时参数
- 风控阈值
- 回测成本参数

## 数据源

| 来源 | 用途 | 费用 |
|------|------|------|
| AKShare | 主要数据源 (行情/财务/期货/宏观/资金流) | 免费 |
| BaoStock | 备用 (历史日线) | 免费 |
| Tushare | 补充 (需token) | 免费/付费 |

## 测试

```bash
pytest                       # 运行所有测试
pytest tests/factors/        # 运行因子测试
pytest tests/backtest/       # 运行回测测试
pytest -v                    # 详细输出
```

## 项目结构

```
testing_project_quant/
├── config/settings.yaml     # 配置文件
├── main.py                  # CLI入口
├── requirements.txt         # Python依赖
├── src/                     # 源代码
├── tests/                   # 测试
├── notebooks/               # 演示脚本
├── data/                    # SQLite数据库 (自动生成)
└── reports/                 # 输出报告 (自动生成)
```
