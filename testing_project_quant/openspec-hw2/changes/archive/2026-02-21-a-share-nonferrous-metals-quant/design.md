## Context

本项目从零构建一个 A 股有色金属多因子量化系统。目标用户是量化投资初学者，因此系统优先考虑易用性、可理解性和可调试性，而非极致性能。系统运行在本地 Python 环境中，不涉及实盘交易接口对接，仅输出交易信号和回测结果。

当前状态：空项目，无已有代码。
约束条件：仅使用免费数据源（AKShare 为主），Python 3.10+，本地运行。

## Goals / Non-Goals

**Goals:**
- 提供完整的"数据采集 → 因子计算 → 信号生成 → 回测验证 → 报告展示"全链路
- 模块化设计，各组件可独立测试和替换
- 严格模拟 A 股交易规则（T+1、涨跌停、交易成本）
- 代码结构清晰，初学者可读懂和修改
- 支持月度调仓策略，也为未来更高频策略预留扩展空间

**Non-Goals:**
- 不对接实盘券商 API（不执行真实交易）
- 不支持日内/高频策略（不处理 tick 级数据）
- 不提供 Web UI（命令行 + 本地 HTML 报告即可）
- 不做机器学习因子挖掘（初始版本仅支持规则因子）
- 不支持多市场（仅 A 股）

## Decisions

### Decision 1: 项目结构 — 分层模块化架构

采用以下目录结构：

```
a-share-nonferrous-metals-quant/
├── config/
│   └── settings.yaml          # 全局配置（数据源、因子权重、风控阈值）
├── src/
│   ├── data/
│   │   ├── sources/           # 数据源适配器（akshare_source.py, baostock_source.py）
│   │   ├── storage.py         # 本地存储层（SQLite/Parquet 抽象）
│   │   ├── pipeline.py        # 数据采集管道（增量更新逻辑）
│   │   └── validators.py      # 数据质量校验
│   ├── universe/
│   │   ├── classifier.py      # 申万行业分类与子板块映射
│   │   └── filter.py          # 股票池过滤（ST/停牌/流动性）
│   ├── factors/
│   │   ├── base.py            # Factor 基类与注册机制
│   │   ├── fundamental.py     # 基本面因子
│   │   ├── technical.py       # 技术面因子
│   │   ├── commodity.py       # 商品因子
│   │   ├── macro.py           # 宏观因子
│   │   ├── flow.py            # 资金流因子
│   │   └── standardizer.py    # 截面标准化（MAD + Z-Score）
│   ├── strategy/
│   │   ├── scorer.py          # 多因子打分（等权/IC加权）
│   │   ├── timing.py          # 商品动量择时
│   │   ├── allocator.py       # 仓位分配（含子板块约束）
│   │   └── signal.py          # 交易信号生成
│   ├── risk/
│   │   ├── stop_loss.py       # 止损（硬止损 + 移动止损）
│   │   ├── drawdown.py        # 回撤监控与分层响应
│   │   ├── position_sizer.py  # 波动率仓位管理
│   │   └── alerts.py          # 金属价格急跌预警
│   ├── backtest/
│   │   ├── engine.py          # 回测引擎主循环
│   │   ├── broker.py          # 模拟经纪商（T+1、涨跌停、成本）
│   │   ├── portfolio.py       # 组合状态管理
│   │   └── metrics.py         # 绩效指标计算
│   └── report/
│       ├── charts.py          # 图表生成（Plotly/Matplotlib）
│       └── exporter.py        # HTML/PNG 导出
├── tests/                     # 单元测试与集成测试
├── notebooks/                 # Jupyter 探索笔记本
├── main.py                    # CLI 入口
└── requirements.txt
```

**Rationale:** 分层架构使每个模块只关注单一职责。data 层不知道 factor 层，factor 层不知道 strategy 层。这让初学者可以逐个模块理解和修改，而不需要理解整个系统。

**Alternative considered:** 单文件脚本。虽然更简单，但 8 个 capability 涉及 2000+ 行代码，单文件不可维护。

### Decision 2: 数据存储 — SQLite 为默认，Parquet 为可选

默认使用 SQLite，原因：
- 零配置，单文件数据库
- 支持 SQL 查询，方便调试和数据探查
- pandas 原生支持 `read_sql` / `to_sql`
- 适合中等数据量（有色金属约100只股票，5年日线约120,000条记录）

SQLite 表设计：
- `stock_daily` — 日线行情（symbol, date, open, high, low, close, volume, amount）
- `financials` — 财务数据（symbol, report_date, pb, roe, gross_margin, ...）
- `futures_daily` — 期货日线（metal, date, open, high, low, close, settle, volume, inventory）
- `macro` — 宏观指标（indicator, date, value）
- `fund_flow` — 资金流（symbol, date, margin_balance, northbound_net_buy）
- `meta` — 元数据（data_category, last_updated）

**Alternative considered:** Parquet 文件。读写更快，但缺少 SQL 查询能力，调试不便。保留为可选配置项。

### Decision 3: 数据源适配器模式

每个数据源实现统一的 `DataSource` 接口：

```python
class DataSource(Protocol):
    def fetch_stock_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame: ...
    def fetch_financials(self, symbol: str) -> pd.DataFrame: ...
    def fetch_futures_daily(self, metal: str, start: str, end: str) -> pd.DataFrame: ...
    def fetch_macro(self, indicator: str) -> pd.DataFrame: ...
    def fetch_fund_flow(self, symbol: str, start: str, end: str) -> pd.DataFrame: ...
```

`pipeline.py` 依赖接口而非具体实现，切换数据源只需更改配置。API 失败时自动按优先级回退（AKShare → BaoStock → Tushare）。每次 API 调用之间加 0.5 秒延迟以避免限速。

**Rationale:** AKShare 基于爬虫，稳定性不如专业 API。适配器模式使系统对数据源变更具有韧性。

### Decision 4: 因子计算 — 注册机制 + 向量化

每个因子继承 `BaseFactor` 并通过装饰器注册：

```python
class BaseFactor:
    name: str
    category: str  # fundamental, technical, commodity, macro, flow
    def compute(self, universe: list[str], date: str, data: DataStore) -> pd.Series: ...

@register_factor
class PBPercentileFactor(BaseFactor):
    name = "pb_percentile"
    category = "fundamental"
```

因子计算全部使用 pandas 向量化操作，避免逐股票 for 循环。截面标准化在所有因子计算完成后统一执行。

**Rationale:** 注册机制使新增因子只需写一个类文件，不需改动打分逻辑。向量化确保 100 只股票的因子计算在秒级完成。

### Decision 5: 回测引擎 — 事件驱动逐日推进

回测主循环按交易日推进，每日执行：
1. 更新当日行情到 Portfolio
2. 检查止损 / 风控条件，生成紧急卖出信号
3. 执行前一日生成的订单（模拟 T+1）
4. 若为调仓日，运行因子计算 → 打分 → 信号生成
5. 记录当日 NAV

模拟经纪商 `Broker` 负责处理 A 股特殊规则：
- T+1：买入日记录为 `buy_date`，卖出订单 `earliest_sell = buy_date + 1`
- 涨跌停：买入时检查收盘涨幅 ≥ 9.5% 则拒绝，卖出时检查跌幅 ≤ -9.5% 则拒绝
- 停牌：通过检查成交量是否为 0 判断，停牌期间冻结持仓
- 成本：卖出扣印花税 0.05% + 双边佣金 0.03%（最低5元）+ 滑点 0.15%

**Alternative considered:** Backtrader 框架。功能完善但学习曲线陡峭且自定义困难。自研引擎虽然工作量大，但对 A 股规则的模拟更精确，代码更透明。

### Decision 6: 配置管理 — YAML 单文件

所有策略参数集中在 `config/settings.yaml`：

```yaml
data:
  primary_source: akshare
  storage_backend: sqlite
  db_path: data/quant.db
  api_delay_seconds: 0.5

universe:
  min_listing_days: 60
  min_daily_turnover: 5000000
  exclude_st: true

factors:
  weights:
    commodity: 0.35
    fundamental: 0.25
    technical: 0.20
    flow: 0.15
    macro: 0.05
  scoring_mode: equal_weight  # or ic_weight

strategy:
  max_stocks: 10
  max_single_weight: 0.10
  max_subsector_weight: 0.25
  rebalance_freq: monthly

risk:
  hard_stop_atr_multiple: 2.0
  trailing_stop_activation: 0.10
  trailing_stop_drop: 0.08
  max_drawdown_reduce: 0.15
  max_drawdown_liquidate: 0.20

backtest:
  stamp_tax: 0.0005
  commission: 0.0003
  min_commission: 5
  slippage: 0.0015
  risk_free_rate: 0.02
```

**Rationale:** YAML 可读性好，修改参数不需要改代码。单文件配置避免分散在多处。参数变更通过 git diff 可追踪。

### Decision 7: 可视化 — Plotly 为主，Matplotlib 备选

优先使用 Plotly 生成交互式 HTML 报告。原因：
- 支持缩放、悬停显示数值，适合金融数据探查
- 单 HTML 文件即可分享，无需额外环境
- Plotly Express 语法简洁

Matplotlib 保留用于静态 PNG 导出场景（如嵌入文档）。

### Decision 8: 股票-金属映射

在 `config/settings.yaml` 或 `universe/classifier.py` 中维护子板块到对应期货品种的映射表：

```python
SUBSECTOR_METAL_MAP = {
    "copper": "cu",      # SHFE copper
    "aluminum": "al",    # SHFE aluminum
    "gold": "au",        # SHFE gold
    "rare_earth": None,  # No liquid futures, use sector index
    "lithium": "LC",     # Guangzhou Futures Exchange lithium carbonate
    "cobalt_nickel": "ni",  # SHFE nickel
    "zinc_lead": "zn",   # SHFE zinc
}
```

当某子板块无对应期货品种（如稀土）时，商品因子使用该子板块指数收益率替代。

## Risks / Trade-offs

### [Risk] AKShare API 不稳定 → 数据采集中断
**Mitigation:** 多数据源回退机制（AKShare → BaoStock → Tushare）。本地缓存确保已有数据不受影响。关键数据增加手动导入入口（CSV 文件）。

### [Risk] 因子过拟合 → 回测虚高实盘失效
**Mitigation:** 使用 Walk-Forward 验证（训练集 / 测试集按时间切分，非随机）。因子数量控制在 10 个以内。提供因子 IC 跟踪报告，让用户监控因子衰减。

### [Risk] 幸存者偏差 → 回测收益虚高
**Mitigation:** 使用历史时点的行业分类数据。AKShare/聚宽提供包含已退市股票的数据。在回测报告中标注是否使用了 point-in-time 数据。

### [Risk] 有色金属板块股票数量少（~80-120只）→ 统计显著性不足
**Mitigation:** 截面标准化时当样本 < 10 只股票发出警告。因子 IC 检验使用 bootstrap 方法提高置信度。避免使用需要大样本的复杂模型。

### [Risk] SQLite 并发写入性能差 → 多数据源同时写入冲突
**Mitigation:** 数据采集按数据类别串行执行（先行情，再财务，再期货...），不并发写入。未来如需并行，可切换至 PostgreSQL。

### [Trade-off] 自研回测引擎 vs 使用 Backtrader
选择自研。代价是开发周期更长（估计多 2-3 周），收益是对 A 股规则的精确模拟和代码透明度。初学者更容易理解自研代码而非框架内部机制。

### [Trade-off] 月度调仓 vs 更高频率
选择月度。代价是可能错过短期机会，收益是大幅降低交易成本和实现复杂度。月频年化换手约 200-400%，交易成本约 1-1.5%。周频会使成本翻倍。

## Open Questions

- 是否需要支持模拟盘实时运行（每日自动拉取数据 + 发送信号通知）？如需要，需增加定时任务调度模块。
- IC 加权模式需要至少 12 个月数据才有意义，是否在数据不足时完全禁用并强制等权？
- 是否需要支持用户自定义因子（通过配置或插件机制）？
- 报告是否需要支持中文图表标签和注释？（Plotly 中文字体需要额外配置）
