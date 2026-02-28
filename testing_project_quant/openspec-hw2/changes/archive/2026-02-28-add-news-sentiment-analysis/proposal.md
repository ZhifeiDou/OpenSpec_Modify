## Why

当前量化系统仅依赖价量和基本面因子（commodity/fundamental/technical/flow/macro）进行选股打分，无法感知市场新闻事件。有色金属板块受政策（限产、环保、关税）、供需（矿难、罢工、库存）、国际形势等突发新闻影响极大，纯量化因子存在信息滞后。引入新闻采集 + 大模型情绪分析，可以在事件发生后第一时间将利多/利空信号融入多因子打分，提升策略时效性。

## What Changes

- 新增新闻数据采集模块，从财经数据源（AKShare 财经新闻接口、东方财富等）抓取有色金属板块及个股相关新闻
- 新增 LLM 情绪分析模块，调用大语言模型 API 对新闻标题和摘要进行利多/利空/中性判断，输出结构化情绪分数
- 新增 sentiment 因子，将 LLM 输出的情绪分数聚合、标准化后接入现有多因子打分框架（scorer.py）
- 在 `config/settings.yaml` 中新增 news、llm、sentiment 相关配置段

## Capabilities

### New Capabilities

- `news-fetcher`: 有色金属新闻数据采集能力，支持从 AKShare 等数据源抓取板块及个股新闻，包含去重、缓存、频率控制
- `llm-sentiment-analyzer`: 大模型情绪分析能力，调用 LLM API 对新闻文本进行利多/利空/中性分类并输出情绪分数（-1 到 +1）
- `sentiment-factor`: 情绪因子计算能力，将个股维度的 LLM 情绪分数聚合为时间衰减加权的情绪因子值，经标准化后参与多因子打分

### Modified Capabilities

_(无需修改现有 spec。sentiment 因子将作为新的因子类别注册到现有 factor registry，通过 config weights 配置权重，不改变现有因子的行为)_

## Impact

- **代码影响**: `src/` 下新增 `news/` 和 `sentiment/` 模块，`src/factors/` 下新增 sentiment factor 注册，`src/strategy/signal.py` 的 `generate_signals` 流程中加入新闻获取步骤
- **配置影响**: `config/settings.yaml` 新增 `news`、`llm`、`sentiment` 配置段；`factors.weights` 中新增 `sentiment` 权重
- **依赖影响**: 新增 `requests`（HTTP 请求）、`openai` 或 `anthropic`（LLM API）、`beautifulsoup4`（可选，网页解析）
- **外部服务**: 需要 LLM API key（通过环境变量配置），需要网络访问财经数据源
- **成本影响**: LLM API 按量计费，需设计缓存策略（同一新闻不重复分析）控制成本
- **数据库影响**: `data/quant.db` 新增 news 和 sentiment_cache 表
