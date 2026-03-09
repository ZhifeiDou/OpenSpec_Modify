## Context

当前系统使用 5 类量化因子（commodity/fundamental/technical/flow/macro）通过 `BaseFactor` + `@register_factor` 装饰器注册到全局 `_FACTOR_REGISTRY`，在 `compute_all_factors()` 中统一计算并经截面标准化后输入 `score_stocks()` 打分。所有数据存储在 SQLite（`data/quant.db`），通过 `DataStore` 类统一访问。

新闻情绪分析需要引入两个外部依赖：财经新闻数据源（AKShare 已有）和 LLM API（新增）。核心挑战是将非结构化的文本信号转换为可与现有因子体系融合的标准化数值因子。

## Goals / Non-Goals

**Goals:**
- 新闻采集、LLM 分析、情绪因子计算三个模块解耦，各自可独立测试
- 完全复用现有因子框架（`BaseFactor` + `@register_factor` + `cross_sectional_standardize`），无需修改框架本身
- LLM 或新闻服务不可用时，系统优雅降级到纯量化因子模式
- LLM 调用成本可控：通过缓存 + 批量请求最小化 API 调用次数

**Non-Goals:**
- 不做实时流式新闻监控（仅在信号生成时批量采集）
- 不做自然语言处理的本地模型部署（只调用云端 LLM API）
- 不做新闻源的爬虫开发（仅使用 AKShare 已有接口）
- 不修改回测引擎以支持历史新闻回测（未来可扩展）

## Decisions

### D1: 新闻模块放在 `src/news/` 独立目录

**选择**: 在 `src/` 下新建 `news/` 模块，包含 `fetcher.py`（采集）和 `__init__.py`。

**理由**: 新闻采集是独立的数据获取逻辑，不属于现有的 `data/sources/` 体系（那里是行情数据源）。独立目录使职责清晰，未来可扩展多个新闻源。

**备选**: 放在 `src/data/sources/news_source.py` — 但新闻和行情数据的采集频率、缓存策略、数据结构差异较大，混在一起会增加复杂度。

### D2: LLM 分析模块放在 `src/sentiment/` 目录

**选择**: 新建 `src/sentiment/` 模块，包含 `analyzer.py`（LLM 调用）和 `factor.py`（情绪因子计算）。

**理由**: 情绪分析和因子计算紧密相关但职责不同。`analyzer.py` 负责 LLM 交互和结果缓存，`factor.py` 负责将原始分数聚合为因子值并注册到 factor registry。

### D3: 使用 OpenAI SDK 作为默认 LLM 客户端，支持 Anthropic 切换

**选择**: 默认使用 `openai` Python SDK（兼容 OpenAI API），通过配置 `llm.provider` 切换到 `anthropic` SDK。

**理由**: OpenAI 的 structured output (JSON mode) 成熟，`gpt-4o-mini` 成本低且速度快，适合批量新闻分析。Anthropic Claude 作为备选。两个 SDK 通过简单的 adapter pattern 封装，只需实现一个 `call_llm(messages) -> str` 接口。

**备选**: 使用 `requests` 直接调 HTTP API — 但 SDK 提供了重试、流控、类型安全等开箱即用的能力。

### D4: 情绪因子通过 `@register_factor` 装饰器注册

**选择**: 创建 `SentimentFactor(BaseFactor)` 类并用 `@register_factor` 装饰器注册，category 设为 `"sentiment"`。在 `compute_all_factors()` 中通过 lazy import `src.factors.sentiment` 触发注册。

**理由**: 完全复用现有框架，零侵入。情绪因子和其他因子统一走标准化、打分流程。通过 `factors.weights.sentiment` 配置权重。

### D5: 新闻采集在 `generate_signals()` 流程中触发

**选择**: 在 `src/strategy/signal.py` 的 `generate_signals()` 函数开头，调用新闻采集和 LLM 分析。这样情绪因子在 `compute_all_factors()` 被调用时已有数据可用。

**理由**: 信号生成是系统的主入口，在此触发确保每次生成信号前新闻数据是最新的。也可通过 `python main.py update --categories news` 单独触发。

**备选**: 在 `DataPipeline.run()` 中触发 — 但新闻采集的时效性要求与行情数据不同（行情日更新，新闻需分钟级），放在 signal 流程更合理。

### D6: SQLite 新增 news 和 sentiment_cache 两张表

**选择**: 在 `DataStore._TABLE_SCHEMAS` 中新增 `news` 和 `sentiment_cache` 表定义，复用现有的 `_init_tables()` 机制自动建表。

**理由**: 复用现有存储层，不引入新的存储依赖。去重通过 `INSERT OR IGNORE` + UNIQUE 约束实现。

### D7: LLM prompt 使用 JSON mode 要求结构化输出

**选择**: prompt 明确要求 LLM 以 JSON 数组格式返回结果，每条包含 `news_index`、`classification`、`confidence` 字段。对 OpenAI 使用 `response_format={"type": "json_object"}`，对 Anthropic 在 prompt 中约束输出格式。

**理由**: 结构化输出减少解析错误，降低容错复杂度。

## Risks / Trade-offs

- **[LLM 成本不可控]** → 通过 sentiment_cache 表严格缓存，同一新闻永不重复分析；通过 batch_size 减少 API 调用次数；默认使用低成本模型（gpt-4o-mini）
- **[AKShare 新闻接口不稳定]** → 采集失败时优雅降级，不中断信号生成；系统正常运行不依赖新闻数据
- **[LLM 判断准确性]** → 情绪因子默认权重仅 10%，即使判断有误也不会主导选股结果；可通过调低权重或设为 0 完全关闭
- **[新增依赖包]** → `openai` 和 `anthropic` SDK 是纯 Python 包，无系统级依赖，安装风险低
- **[新闻与个股关联不准]** → 基于文本匹配的关联可能存在误匹配（如"金"匹配到非有色金属公司），通过限定在股票池内匹配来降低风险
