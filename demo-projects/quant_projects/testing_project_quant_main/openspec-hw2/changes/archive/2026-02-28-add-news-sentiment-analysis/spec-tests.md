# Spec-Test Mapping: add-news-sentiment-analysis
Generated: 2026-02-28

## Use Case ID Mapping

| ID | Use Case |
|----|----------|
| R1-UC1 | 获取有色金属板块最新新闻 |
| R2-UC1 | 分析新闻情绪（利多/利空判断） |
| R3-UC1 | 生成包含情绪因子的交易信号 |

## Requirement Traceability Matrix

| ID | Requirement | Type | Test Type | Test Case | Status |
|----|-------------|------|-----------|-----------|--------|
| R1-UC1 | 新闻采集完整流程 | Flow | Integration | `tests/test_news_fetcher.py::TestFetchAndStore::test_fetch_and_store_full_flow` | ✅ |
| R1-UC1-S1 | 根据配置确定新闻源和时间范围 | Step | Unit | `tests/test_news_fetcher.py::TestConfig::test_config_keywords_and_lookback` | ✅ |
| R1-UC1-S1 | 配置默认值验证 | Step | Unit | `tests/test_news_fetcher.py::TestConfig::test_config_defaults_when_missing` | ✅ |
| R1-UC1-S1 | 自定义配置值 | Step | Unit | `tests/test_news_fetcher.py::TestConfig::test_config_custom_values` | ✅ |
| R1-UC1-S2 | 调用 AKShare 接口获取新闻 | Step | Unit | `tests/test_news_fetcher.py::TestAKShareFetch::test_fetch_from_akshare_success` | ✅ |
| R1-UC1-S3 | 提取标题、摘要、发布时间等字段 | Step | Unit | `tests/test_news_fetcher.py::TestAKShareFetch::test_field_extraction` | ✅ |
| R1-UC1-S4 | 将新闻与个股关联（单股） | Step | Unit | `tests/test_news_fetcher.py::TestStockMatching::test_match_single_stock` | ✅ |
| R1-UC1-S4 | 将新闻与个股关联（多股） | Step | Unit | `tests/test_news_fetcher.py::TestStockMatching::test_match_multiple_stocks` | ✅ |
| R1-UC1-S5 | 去重 — 新文章通过 | Step | Unit | `tests/test_news_fetcher.py::TestDeduplication::test_new_article_passes` | ✅ |
| R1-UC1-S5 | 去重 — 已存在文章过滤 | Step | Unit | `tests/test_news_fetcher.py::TestDeduplication::test_existing_article_filtered` | ✅ |
| R1-UC1-S6 | 写入 SQLite news 表 | Step | Unit | `tests/test_news_fetcher.py::TestPersistence::test_save_and_read` | ✅ |
| R1-UC1-E2a | AKShare 接口请求失败 → 优雅降级 | Extension | Unit | `tests/test_news_fetcher.py::TestAKShareFetch::test_akshare_api_failure` | ✅ |
| R1-UC1-E2b | 接口返回空数据 | Extension | Unit | `tests/test_news_fetcher.py::TestAKShareFetch::test_akshare_returns_empty` | ✅ |
| R1-UC1-E4a | 无法关联到个股 → 板块级新闻 | Extension | Unit | `tests/test_news_fetcher.py::TestStockMatching::test_no_match_returns_empty` | ✅ |
| R2-UC1 | 情绪分析完整流程 | Flow | Integration | `tests/test_sentiment_analyzer.py::TestAnalyzePending::test_analyze_pending_full_flow` | ✅ |
| R2-UC1-S1 | 查询未分析的新闻（缓存跳过） | Step | Unit | `tests/test_sentiment_analyzer.py::TestCaching::test_already_cached_skipped` | ✅ |
| R2-UC1-S2 | 批量组织 prompt | Step | Unit | `tests/test_sentiment_analyzer.py::TestPromptBuilding::test_build_prompt_format` | ✅ |
| R2-UC1-S3 | 调用 LLM API（OpenAI） | Step | Unit | `tests/test_sentiment_analyzer.py::TestLLMCall::test_call_openai_success` | ✅ |
| R2-UC1-S4 | LLM 返回利多分类和置信度 | Step | Unit | `tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_bullish` | ✅ |
| R2-UC1-S5 | 解析利空为负分数 | Step | Unit | `tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_bearish` | ✅ |
| R2-UC1-S6 | 写入 sentiment_cache 表 | Step | Unit | `tests/test_sentiment_analyzer.py::TestCacheSave::test_results_saved_to_cache` | ✅ |
| R2-UC1-E3a | LLM API 调用失败 → 重试成功 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestLLMCall::test_api_retry_on_failure` | ✅ |
| R2-UC1-E3a | LLM API 所有重试失败 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestLLMCall::test_all_retries_fail` | ✅ |
| R2-UC1-E3b | API key 未配置 → 跳过分析 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestGracefulDegradation::test_no_api_key` | ✅ |
| R2-UC1-E4a | 返回非法 JSON → 中性 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_invalid_json` | ✅ |
| R2-UC1-E4a | 返回缺失字段 → 中性 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_missing_fields` | ✅ |
| R2-UC1-E1a | 无待分析新闻 → 跳过 | Extension | Unit | `tests/test_sentiment_analyzer.py::TestAnalyzePending::test_no_pending_news_skips` | ✅ |
| R3-UC1 | 信号生成完整流程（含情绪因子） | Flow | Integration | `tests/test_sentiment_factor.py::TestSignalIntegration::test_signal_pipeline_with_sentiment` | ✅ |
| R3-UC1-S5 | 时间衰减加权 — 近期新闻权重更高 | Step | Unit | `tests/test_sentiment_factor.py::TestTimeDecay::test_recent_news_weighted_higher` | ✅ |
| R3-UC1-S5 | 时间衰减公式验证 | Step | Unit | `tests/test_sentiment_factor.py::TestTimeDecay::test_decay_formula` | ✅ |
| R3-UC1-S6 | 情绪因子注册到 factor registry | Step | Unit | `tests/test_sentiment_factor.py::TestFactorRegistration::test_registered_in_registry` | ✅ |
| R3-UC1-S6 | 因子 category 为 sentiment | Step | Unit | `tests/test_sentiment_factor.py::TestFactorRegistration::test_category_is_sentiment` | ✅ |
| R3-UC1-S8 | 输出情绪标签和新闻摘要 | Step | Unit | `tests/test_sentiment_factor.py::TestSignalIntegration::test_sentiment_labels_output` | ✅ |
| R3-UC1-E3a | 新闻采集失败 → 因子返回 0 | Extension | Unit | `tests/test_sentiment_factor.py::TestSignalIntegration::test_news_fetch_failure_graceful` | ✅ |
| R3-UC1-E4a | LLM 分析失败 → 使用缓存 | Extension | Unit | `tests/test_sentiment_factor.py::TestSignalIntegration::test_llm_failure_uses_cache` | ✅ |
| R3-UC1-E5a | 无相关新闻 → 分数设为 0 | Extension | Unit | `tests/test_sentiment_factor.py::TestNoNews::test_no_news_returns_zero` | ✅ |
| R3-UC1-E5a | 板块级新闻应用于所有个股 | Extension | Unit | `tests/test_sentiment_factor.py::TestSectorNews::test_sector_news_applies_to_all_stocks` | ✅ |
| R3-UC1-E6a | sentiment 权重为 0 → 跳过打分 | Extension | Unit | `tests/test_sentiment_factor.py::TestZeroWeight::test_zero_weight_skips_pipeline` | ✅ |
| R3-UC1-E6a | sentiment 权重为 0 → 管线实际跳过 | Extension | Component | `tests/test_sentiment_factor.py::TestSignalIntegration::test_zero_weight_skips_news_pipeline` | ✅ |

## Use Case Details

### Use Case: 获取有色金属板块最新新闻 (R1-UC1)

#### Main Scenario
- **R1-UC1-S1**: 根据配置确定新闻源和时间范围
  - `tests/test_news_fetcher.py:38` test_config_keywords_and_lookback (Unit)
  - `tests/test_news_fetcher.py:44` test_config_defaults_when_missing (Unit)
  - `tests/test_news_fetcher.py:52` test_config_custom_values (Unit)
- **R1-UC1-S2**: 调用 AKShare 接口获取新闻
  - `tests/test_news_fetcher.py:66` test_fetch_from_akshare_success (Unit)
- **R1-UC1-S3**: 提取标题、摘要、发布时间字段
  - `tests/test_news_fetcher.py:80` test_field_extraction (Unit)
- **R1-UC1-S4**: 新闻与个股关联
  - `tests/test_news_fetcher.py:102` test_match_single_stock (Unit)
  - `tests/test_news_fetcher.py:110` test_match_multiple_stocks (Unit)
- **R1-UC1-S5**: 去重过滤
  - `tests/test_news_fetcher.py:126` test_new_article_passes (Unit)
  - `tests/test_news_fetcher.py:133` test_existing_article_filtered (Unit)
- **R1-UC1-S6**: 写入 SQLite
  - `tests/test_news_fetcher.py:148` test_save_and_read (Unit)

#### Extensions
- **R1-UC1-E2a**: AKShare 请求失败 → `tests/test_news_fetcher.py:96` test_akshare_api_failure (Unit)
- **R1-UC1-E2b**: 返回空数据 → `tests/test_news_fetcher.py:104` test_akshare_returns_empty (Unit)
- **R1-UC1-E4a**: 无法关联个股 → `tests/test_news_fetcher.py:118` test_no_match_returns_empty (Unit)

#### Full Flow Tests
- `R1-UC1` — "新闻采集完整流程" → `tests/test_news_fetcher.py:165` test_fetch_and_store_full_flow (Integration)

---

### Use Case: 分析新闻情绪 (R2-UC1)

#### Main Scenario
- **R2-UC1-S1**: 查询未分析的新闻
  - `tests/test_sentiment_analyzer.py` TestCaching::test_already_cached_skipped (Unit)
- **R2-UC1-S2**: 批量组织 prompt
  - `tests/test_sentiment_analyzer.py` TestPromptBuilding::test_build_prompt_format (Unit)
- **R2-UC1-S3**: 调用 LLM API
  - `tests/test_sentiment_analyzer.py` TestLLMCall::test_call_openai_success (Unit)
- **R2-UC1-S4**: LLM 返回分类和置信度
  - `tests/test_sentiment_analyzer.py` TestResponseParsing::test_parse_bullish (Unit)
- **R2-UC1-S5**: 解析为标准化情绪分数
  - `tests/test_sentiment_analyzer.py` TestResponseParsing::test_parse_bearish (Unit)
- **R2-UC1-S6**: 写入 sentiment_cache 表
  - `tests/test_sentiment_analyzer.py` TestCacheSave::test_results_saved_to_cache (Unit)

#### Extensions
- **R2-UC1-E3a**: API 调用失败重试成功 → `tests/test_sentiment_analyzer.py` TestLLMCall::test_api_retry_on_failure (Unit)
- **R2-UC1-E3a**: 所有重试失败 → `tests/test_sentiment_analyzer.py` TestLLMCall::test_all_retries_fail (Unit)
- **R2-UC1-E3b**: API key 未配置 → `tests/test_sentiment_analyzer.py` TestGracefulDegradation::test_no_api_key (Unit)
- **R2-UC1-E4a**: 返回非法 JSON → `tests/test_sentiment_analyzer.py` TestResponseParsing::test_parse_invalid_json (Unit)
- **R2-UC1-E4a**: 缺失字段 → `tests/test_sentiment_analyzer.py` TestResponseParsing::test_parse_missing_fields (Unit)
- **R2-UC1-E1a**: 无待分析新闻 → `tests/test_sentiment_analyzer.py` TestAnalyzePending::test_no_pending_news_skips (Unit)

#### Full Flow Tests
- `R2-UC1` — "情绪分析完整流程" → `tests/test_sentiment_analyzer.py` TestAnalyzePending::test_analyze_pending_full_flow (Integration)

---

### Use Case: 生成包含情绪因子的交易信号 (R3-UC1)

#### Main Scenario
- **R3-UC1-S5**: 时间衰减加权
  - `tests/test_sentiment_factor.py` TestTimeDecay::test_recent_news_weighted_higher (Unit)
  - `tests/test_sentiment_factor.py` TestTimeDecay::test_decay_formula (Unit)
- **R3-UC1-S6**: 注册到多因子框架
  - `tests/test_sentiment_factor.py` TestFactorRegistration::test_registered_in_registry (Unit)
  - `tests/test_sentiment_factor.py` TestFactorRegistration::test_category_is_sentiment (Unit)
- **R3-UC1-S8**: 输出情绪标签
  - `tests/test_sentiment_factor.py` TestSignalIntegration::test_sentiment_labels_output (Unit)

#### Extensions
- **R3-UC1-E3a**: 新闻采集失败 → `tests/test_sentiment_factor.py` TestSignalIntegration::test_news_fetch_failure_graceful (Unit)
- **R3-UC1-E4a**: LLM 分析失败 → `tests/test_sentiment_factor.py` TestSignalIntegration::test_llm_failure_uses_cache (Unit)
- **R3-UC1-E5a**: 无相关新闻 → `tests/test_sentiment_factor.py` TestNoNews::test_no_news_returns_zero (Unit)
- **R3-UC1-E5a**: 板块级新闻 → `tests/test_sentiment_factor.py` TestSectorNews::test_sector_news_applies_to_all_stocks (Unit)
- **R3-UC1-E6a**: 权重为 0 跳过打分 → `tests/test_sentiment_factor.py` TestZeroWeight::test_zero_weight_skips_pipeline (Unit)
- **R3-UC1-E6a**: 权重为 0 管线跳过 → `tests/test_sentiment_factor.py` TestSignalIntegration::test_zero_weight_skips_news_pipeline (Component)

#### Full Flow Tests
- `R3-UC1` — "信号生成含情绪因子" → `tests/test_sentiment_factor.py` TestSignalIntegration::test_signal_pipeline_with_sentiment (Integration)
