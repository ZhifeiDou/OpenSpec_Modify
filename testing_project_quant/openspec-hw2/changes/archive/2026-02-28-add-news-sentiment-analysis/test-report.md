# Test Report: add-news-sentiment-analysis
Generated: 2026-02-28

## Use Case Coverage Summary

| Use Case | Happy Path | Extensions | Overall |
|----------|-----------|------------|---------|
| R1-UC1 获取有色金属板块最新新闻 | ✅ 6/6 | ✅ 3/3 | 100% |
| R2-UC1 分析新闻情绪（利多/利空判断） | ✅ 6/6 | ✅ 6/6 | 100% |
| R3-UC1 生成包含情绪因子的交易信号 | ✅ 3/3 | ✅ 6/6 | 100% |

**Overall: 39/39 requirements covered (100%)**

- 3 Integration (Flow) tests
- 35 Unit tests
- 1 Component test

## Covered Requirements

### R1-UC1: 获取有色金属板块最新新闻

#### Main Scenario (6/6)
- ✅ **R1-UC1-S1**: 根据配置确定新闻源和时间范围 (`tests/test_news_fetcher.py::TestConfig` — 3 tests)
- ✅ **R1-UC1-S2**: 调用 AKShare 接口获取新闻 (`tests/test_news_fetcher.py::TestAKShareFetch::test_fetch_from_akshare_success`)
- ✅ **R1-UC1-S3**: 提取标题、摘要、发布时间字段 (`tests/test_news_fetcher.py::TestAKShareFetch::test_field_extraction`)
- ✅ **R1-UC1-S4**: 新闻与个股关联 (`tests/test_news_fetcher.py::TestStockMatching` — 2 tests)
- ✅ **R1-UC1-S5**: 去重过滤 (`tests/test_news_fetcher.py::TestDeduplication` — 2 tests)
- ✅ **R1-UC1-S6**: 写入 SQLite (`tests/test_news_fetcher.py::TestPersistence::test_save_and_read`)

#### Extensions (3/3)
- ✅ **R1-UC1-E2a**: AKShare 请求失败 → 优雅降级 (`tests/test_news_fetcher.py::TestAKShareFetch::test_akshare_api_failure`)
- ✅ **R1-UC1-E2b**: 返回空数据 (`tests/test_news_fetcher.py::TestAKShareFetch::test_akshare_returns_empty`)
- ✅ **R1-UC1-E4a**: 无法关联个股 → 板块级新闻 (`tests/test_news_fetcher.py::TestStockMatching::test_no_match_returns_empty`)

#### Full Flow (1/1)
- ✅ **R1-UC1**: 新闻采集完整流程 (`tests/test_news_fetcher.py::TestFetchAndStore::test_fetch_and_store_full_flow`)

---

### R2-UC1: 分析新闻情绪（利多/利空判断）

#### Main Scenario (6/6)
- ✅ **R2-UC1-S1**: 查询未分析的新闻 (`tests/test_sentiment_analyzer.py::TestCaching::test_already_cached_skipped`)
- ✅ **R2-UC1-S2**: 批量组织 prompt (`tests/test_sentiment_analyzer.py::TestPromptBuilding::test_build_prompt_format`)
- ✅ **R2-UC1-S3**: 调用 LLM API (`tests/test_sentiment_analyzer.py::TestLLMCall::test_call_openai_success`)
- ✅ **R2-UC1-S4**: LLM 返回分类和置信度 (`tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_bullish`)
- ✅ **R2-UC1-S5**: 解析为标准化情绪分数 (`tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_bearish`)
- ✅ **R2-UC1-S6**: 写入 sentiment_cache 表 (`tests/test_sentiment_analyzer.py::TestCacheSave::test_results_saved_to_cache`)

#### Extensions (6/6)
- ✅ **R2-UC1-E3a**: API 调用失败 → 重试成功 (`tests/test_sentiment_analyzer.py::TestLLMCall::test_api_retry_on_failure`)
- ✅ **R2-UC1-E3a**: 所有重试失败 (`tests/test_sentiment_analyzer.py::TestLLMCall::test_all_retries_fail`)
- ✅ **R2-UC1-E3b**: API key 未配置 → 跳过 (`tests/test_sentiment_analyzer.py::TestGracefulDegradation::test_no_api_key`)
- ✅ **R2-UC1-E4a**: 返回非法 JSON → 中性 (`tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_invalid_json`)
- ✅ **R2-UC1-E4a**: 缺失字段 → 中性 (`tests/test_sentiment_analyzer.py::TestResponseParsing::test_parse_missing_fields`)
- ✅ **R2-UC1-E1a**: 无待分析新闻 → 跳过 (`tests/test_sentiment_analyzer.py::TestAnalyzePending::test_no_pending_news_skips`)

#### Full Flow (1/1)
- ✅ **R2-UC1**: 情绪分析完整流程 (`tests/test_sentiment_analyzer.py::TestAnalyzePending::test_analyze_pending_full_flow`)

---

### R3-UC1: 生成包含情绪因子的交易信号

#### Main Scenario (3/3)
- ✅ **R3-UC1-S5**: 时间衰减加权 (`tests/test_sentiment_factor.py::TestTimeDecay` — 2 tests)
- ✅ **R3-UC1-S6**: 注册到多因子框架 (`tests/test_sentiment_factor.py::TestFactorRegistration` — 2 tests)
- ✅ **R3-UC1-S8**: 输出情绪标签 (`tests/test_sentiment_factor.py::TestSignalIntegration::test_sentiment_labels_output`)

#### Extensions (6/6)
- ✅ **R3-UC1-E3a**: 新闻采集失败 → 因子返回 0 (`tests/test_sentiment_factor.py::TestSignalIntegration::test_news_fetch_failure_graceful`)
- ✅ **R3-UC1-E4a**: LLM 分析失败 → 使用缓存 (`tests/test_sentiment_factor.py::TestSignalIntegration::test_llm_failure_uses_cache`)
- ✅ **R3-UC1-E5a**: 无相关新闻 → 分数 0 (`tests/test_sentiment_factor.py::TestNoNews::test_no_news_returns_zero`)
- ✅ **R3-UC1-E5a**: 板块级新闻 → 所有个股 (`tests/test_sentiment_factor.py::TestSectorNews::test_sector_news_applies_to_all_stocks`)
- ✅ **R3-UC1-E6a**: 权重为 0 → 跳过打分 (`tests/test_sentiment_factor.py::TestZeroWeight::test_zero_weight_skips_pipeline`)
- ✅ **R3-UC1-E6a**: 权重为 0 → 管线跳过 (`tests/test_sentiment_factor.py::TestSignalIntegration::test_zero_weight_skips_news_pipeline`)

#### Full Flow (1/1)
- ✅ **R3-UC1**: 信号生成含情绪因子 (`tests/test_sentiment_factor.py::TestSignalIntegration::test_signal_pipeline_with_sentiment`)

## Uncovered Requirements

None — all use case steps and extensions are covered.

## Test Run Results

```
39 passed in 2.76s
0 failed
0 skipped
0 errors
```

All tests passed successfully. No failures detected.
