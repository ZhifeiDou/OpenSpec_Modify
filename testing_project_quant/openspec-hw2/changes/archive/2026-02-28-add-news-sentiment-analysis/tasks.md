## 1. 数据库与存储层

- [x] 1.1 在 `src/data/storage.py` 的 `_TABLE_SCHEMAS` 中新增 `news` 表定义（id, title, summary, published_at, source, related_symbols, scope, fetched_at）
- [x] 1.2 在 `src/data/storage.py` 的 `_TABLE_SCHEMAS` 中新增 `sentiment_cache` 表定义（news_id, classification, confidence, sentiment_score, model_name, analyzed_at）
- [x] 1.3 在 `DataStore` 中添加 `read_news()` 和 `read_sentiment_cache()` 便捷查询方法

## 2. 新闻采集模块

- [x] 2.1 创建 `src/news/__init__.py`
- [x] 2.2 创建 `src/news/fetcher.py`，实现 `NewsFetcher` 类：调用 AKShare 财经新闻接口按关键词获取新闻列表
- [x] 2.3 实现新闻字段提取：title、summary、published_at、source
- [x] 2.4 实现新闻与个股关联逻辑：基于股票池名称/代码匹配，设置 related_symbols 和 scope 字段
- [x] 2.5 实现新闻去重逻辑：基于 title + published_at 检查数据库中是否已存在
- [x] 2.6 实现新闻持久化：将新增新闻写入 SQLite news 表
- [x] 2.7 实现 API 频率控制：请求间隔复用 `data.api_delay_seconds` 配置
- [x] 2.8 实现采集失败时的优雅降级：捕获异常，记录 WARNING 日志，返回空列表

## 3. LLM 情绪分析模块

- [x] 3.1 创建 `src/sentiment/__init__.py`
- [x] 3.2 创建 `src/sentiment/analyzer.py`，实现 `SentimentAnalyzer` 类
- [x] 3.3 实现 LLM prompt 构造：发送新闻标题和摘要，要求 JSON 格式返回 classification + confidence
- [x] 3.4 实现 OpenAI adapter：使用 `openai` SDK 调用 API，启用 JSON mode
- [x] 3.5 实现 Anthropic adapter：使用 `anthropic` SDK 调用 API，prompt 中约束 JSON 输出
- [x] 3.6 实现批量分析：按 `llm.batch_size` 分批发送新闻
- [x] 3.7 实现结果解析：将 LLM 返回的 JSON 解析为 classification/confidence/sentiment_score
- [x] 3.8 实现结果缓存：分析结果写入 sentiment_cache 表，已缓存新闻跳过 LLM 调用
- [x] 3.9 实现错误处理：API 调用失败时指数退避重试（最多 `llm.max_retries` 次）
- [x] 3.10 实现 JSON 格式异常容错：解析失败时标记为中性（score=0）
- [x] 3.11 实现 API key 未配置时的优雅降级：检查环境变量，未配置时跳过分析并记录 WARNING

## 4. 情绪因子

- [x] 4.1 创建 `src/factors/sentiment.py`，实现 `SentimentFactor(BaseFactor)` 类
- [x] 4.2 使用 `@register_factor` 装饰器注册，设置 `name="sentiment_score"`、`category="sentiment"`
- [x] 4.3 实现 `compute()` 方法：查询个股关联新闻的情绪分数，按时间衰减加权求和
- [x] 4.4 实现时间衰减函数：`exp(-ln(2) * hours / half_life)`，参数从 `sentiment.half_life_hours` 读取
- [x] 4.5 实现板块级新闻的分摊逻辑：scope="sector" 的新闻对所有个股生效
- [x] 4.6 实现无新闻时的默认值：返回 0（中性）
- [x] 4.7 在 `src/factors/base.py` 的 `compute_all_factors()` 中添加 `import src.factors.sentiment` lazy import

## 5. 配置与集成

- [x] 5.1 在 `config/settings.yaml` 中新增 `news` 配置段：keywords、lookback_hours、max_articles
- [x] 5.2 在 `config/settings.yaml` 中新增 `llm` 配置段：provider、model、api_key_env、batch_size、max_retries、temperature
- [x] 5.3 在 `config/settings.yaml` 中新增 `sentiment` 配置段：lookback_hours、half_life_hours、min_news_count
- [x] 5.4 在 `config/settings.yaml` 的 `factors.weights` 中添加 `sentiment: 0.10`
- [x] 5.5 在 `requirements.txt` 中添加 `openai>=1.0.0` 和 `anthropic>=0.20.0`
- [x] 5.6 修改 `src/strategy/signal.py` 的 `generate_signals()`：在因子计算前触发新闻采集和 LLM 分析
- [x] 5.7 在 `main.py` 的 `cmd_update()` 中支持 `--categories news` 单独触发新闻采集

## 6. 信号输出增强

- [x] 6.1 修改信号输出格式：在每只股票的信号中附带情绪标签（利多/利空/中性 + 最近新闻标题）
- [x] 6.2 修改 `main.py` 的 `cmd_signal()` 打印逻辑：显示情绪标签列

## 7. 测试

- [x] 7.1 编写 `tests/test_news_fetcher.py`：测试新闻采集、去重、个股关联逻辑
- [x] 7.2 编写 `tests/test_sentiment_analyzer.py`：测试 LLM 调用、批量分析、缓存、错误处理
- [x] 7.3 编写 `tests/test_sentiment_factor.py`：测试时间衰减计算、截面标准化、因子注册
- [x] 7.4 编写集成测试：验证 sentiment 权重为 0 时系统行为不变
