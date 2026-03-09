## Context

构建一个 Rust CLI 量化交易系统，目标是 A 股有色金属板块的多因子选股策略。系统覆盖数据采集、股票池管理、因子计算、信号生成、风控和回测全流程。项目以本地 CLI 工具形式运行，数据存储在本地 CSV 文件中，不依赖数据库。

现有项目结构位于 `demo-projects/quant_projects/rust-testing-quant/`，使用 Rust 2021 edition，依赖 polars (DataFrame)、reqwest (HTTP)、clap (CLI)、chrono (日期)、serde/toml (配置) 等库。

## Goals / Non-Goals

**Goals:**
- 提供端到端的量化投资工作流：数据获取 → 股票池 → 因子 → 信号 → 风控 → 回测 → 报告
- 支持 6 类因子（商品、基本面、技术、资金流、宏观、跨金属比价），共 18+ 个因子
- 提供灵活的 config.toml 配置，无需修改代码即可调整参数
- 支持完整的回测引擎，含交易成本建模
- 模块化设计，新因子/策略可通过 trait 扩展

**Non-Goals:**
- 不做实时交易（live trading）或券商接口对接
- 不做 Web UI 或 dashboard
- 不做分布式计算或高频策略
- 不做数据库集成（本地 CSV 即可）
- 不做机器学习模型集成（纯规则因子）

## Decisions

### D1: 项目结构 — 模块化 Rust workspace

采用单 crate 多模块结构（非 workspace），模块划分为：

```
src/
  main.rs          # CLI 入口 (clap)
  config.rs        # 配置加载 (toml → Config struct)
  data/            # 数据采集模块
    mod.rs         # run_fetch() 入口
    fetcher.rs     # HTTP 请求封装
    parser.rs      # CSV 解析
  universe/        # 股票池管理
    mod.rs         # run_universe() 入口
    filter.rs      # 过滤逻辑
    subsector.rs   # 子行业分类
  factors/         # 因子计算引擎
    mod.rs         # run_calc_factors() + 注册所有 calculators
    traits.rs      # FactorCalculator trait
    fundamental.rs # PB分位、毛利率、ROE
    technical.rs   # 动量、反转、换手、波动率
    commodity.rs   # 金属动量、基差、库存
    macro_factor.rs # PMI、美元
    flow.rs        # 融资余额、北向
    cross_metal.rs # GSR、GCR、SCR、SGR
    standardizer.rs # 截面标准化
  strategy/        # 信号生成
    mod.rs         # run_signal() 入口
    scorer.rs      # 综合评分
    allocator.rs   # 仓位分配（含约束）
    timing.rs      # 择时信号
    signal.rs      # 交易信号输出
  risk/            # 风控模块
    mod.rs         # run_risk_check() 入口
  backtest/        # 回测引擎
    mod.rs         # run_backtest() 入口
  report/          # 报告输出
    mod.rs         # run_report() 入口
```

**理由**: 单 crate 多模块在此规模下足够，避免 workspace 的编译复杂性。模块边界清晰，每个子命令对应一个模块。

### D2: 数据存储 — 本地 CSV 文件

所有数据以 CSV 格式存储在 `data/` 目录下，按类别分子目录：
- `data/stock/` — 个股行情（一个文件一只股票或一个日期一个文件）
- `data/commodity/` — 商品期货价格
- `data/macro/` — 宏观指标
- `data/flow/` — 资金流向

输出存储在 `output/` 目录。

**理由**: CSV + polars 提供足够的查询性能，避免引入 SQLite/PostgreSQL 的复杂性。polars 支持 lazy evaluation 和列式处理。

**替代方案**: SQLite 提供更好的查询灵活性，但增加依赖和迁移负担；对于本项目的数据规模（数百只股票 × 数年日频），CSV 完全足够。

### D3: 因子系统 — Trait + 注册模式

```rust
pub trait FactorCalculator: Send + Sync {
    fn name(&self) -> &str;
    fn category(&self) -> FactorCategory;
    fn calculate(&self, universe: &DataFrame, date: NaiveDate) -> Result<Series>;
}
```

所有因子实现此 trait，在 `factors/mod.rs` 中统一注册到 `Vec<Box<dyn FactorCalculator>>`。新增因子只需：1) 实现 trait，2) 加入注册列表。

**理由**: Trait object 支持运行时多态，注册模式使新增因子的成本最低。因子之间互不依赖，可以独立开发和测试。

### D4: 回测引擎 — 事件循环模式

```
for each trading_day in date_range:
    if is_rebalance_day:
        compute factors → generate signals → execute trades
    mark_to_market(portfolio)
    apply_risk_checks(portfolio)
    record_nav(portfolio)
```

**理由**: 简单的日级循环足够支持月度/周度再平衡，避免复杂的事件驱动架构。风控在每日收盘后执行，止损在下一交易日开盘执行。

### D5: CLI 设计 — clap derive 子命令

使用 clap 4 的 derive 宏生成 CLI，每个功能对应一个子命令：
`fetch-data`, `universe`, `calc-factors`, `signal`, `risk-check`, `backtest`, `report`, `config`

全局参数 `--config` 指定配置文件路径，默认 `config.toml`。

### D6: 错误处理 — thiserror + Box<dyn Error>

模块内部使用 `thiserror` 定义领域错误类型，模块间通过 `Box<dyn std::error::Error>` 传递。CLI 层统一捕获并打印。

**理由**: 对于 CLI 工具，`Box<dyn Error>` 足够灵活。避免 `anyhow` 的额外依赖（虽然影响很小）。

## Risks / Trade-offs

- **[数据源依赖]** → 系统依赖外部 API 获取数据。当 API 不可用时因子计算和回测无法运行。**缓解**: 数据缓存到本地，只有首次获取和增量更新需要 API；支持 `--force` 重下载。
- **[因子失效]** → 量化因子可能在特定市场环境下失效。**缓解**: 配置化权重允许快速调整；多因子组合降低单因子失效风险。
- **[回测过拟合]** → 参数优化可能导致过拟合历史数据。**缓解**: 设计上不提供自动参数搜索，所有参数需手动设置，鼓励样本外验证。
- **[小样本问题]** → 有色金属板块股票数量有限（约 80-100 只），过滤后可能不足 50 只。**缓解**: 截面标准化在 N < 10 时发出警告；空 universe 时回退到持现金。
- **[性能]** → polars DataFrame 操作在数百只股票规模下性能充裕，但大规模历史回测（多年日频）可能需要数分钟。**缓解**: 可接受的运行时间；未来可考虑 lazy evaluation 优化。
