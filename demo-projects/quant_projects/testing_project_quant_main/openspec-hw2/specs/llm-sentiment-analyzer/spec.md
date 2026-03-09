# Capability: llm-sentiment-analyzer

## Purpose

TBD - LLM 情绪分析模块，负责调用 LLM API 对新闻进行情绪分析，支持批量处理、结果缓存和错误容错。

## Requirements

### Requirement: 系统 SHALL 调用 LLM API 分析新闻情绪

系统 SHALL 将新闻标题和摘要发送给 LLM API，要求 LLM 判断该新闻对有色金属板块/个股的影响方向。LLM SHALL 返回情绪分类（bullish/bearish/neutral）和置信度分数（0.0 到 1.0）。系统 SHALL 将结果转换为情绪分数：bullish → +confidence、bearish → -confidence、neutral → 0。

#### Scenario: 利多新闻分析
- **WHEN** 系统发送新闻"紫金矿业发现大型铜矿资源"给 LLM
- **THEN** LLM 返回 classification="bullish"、confidence=0.85，系统转换为情绪分数 +0.85

#### Scenario: 利空新闻分析
- **WHEN** 系统发送新闻"铜价暴跌创年内新低"给 LLM
- **THEN** LLM 返回 classification="bearish"、confidence=0.90，系统转换为情绪分数 -0.90

#### Scenario: 中性新闻分析
- **WHEN** 系统发送新闻"有色金属行业协会召开年度会议"给 LLM
- **THEN** LLM 返回 classification="neutral"、confidence=0.70，系统转换为情绪分数 0

### Requirement: 系统 SHALL 支持批量分析新闻

系统 SHALL 将多条新闻组织为一个批次发送给 LLM，以减少 API 调用次数。每批次的新闻数量 SHALL 由配置 llm.batch_size 控制（默认 10）。LLM 的 prompt SHALL 要求以 JSON 数组格式返回每条新闻的分析结果。

#### Scenario: 批量分析多条新闻
- **WHEN** 系统有 15 条待分析新闻，batch_size=10
- **THEN** 系统分 2 批发送（第一批 10 条，第二批 5 条），每批一次 API 调用

#### Scenario: 待分析新闻数小于 batch_size
- **WHEN** 系统有 3 条待分析新闻，batch_size=10
- **THEN** 系统一次 API 调用即完成分析

### Requirement: 系统 SHALL 缓存 LLM 分析结果

系统 SHALL 将 LLM 分析结果存入 SQLite 的 sentiment_cache 表。sentiment_cache 表 SHALL 包含字段：news_id (INTEGER FOREIGN KEY)、classification (TEXT)、confidence (REAL)、sentiment_score (REAL)、model_name (TEXT)、analyzed_at (TEXT ISO 8601)。系统 SHALL NOT 对已有缓存的新闻重复调用 LLM。

#### Scenario: 新闻已有缓存
- **WHEN** 系统查询到某条新闻已存在 sentiment_cache 记录
- **THEN** 系统跳过该新闻，不调用 LLM

#### Scenario: 分析结果写入缓存
- **WHEN** LLM 返回一条新闻的分析结果
- **THEN** 系统将 classification、confidence、sentiment_score、model_name、analyzed_at 写入 sentiment_cache 表

### Requirement: 系统 SHALL 处理 LLM API 调用失败

系统 SHALL 在 LLM API 调用失败时进行重试（最多重试 llm.max_retries 次，默认 2）。重试间隔 SHALL 使用指数退避（1 秒、2 秒、4 秒）。所有重试均失败后，系统 SHALL 记录 WARNING 日志并跳过该批次新闻。

#### Scenario: API 调用首次失败后重试成功
- **WHEN** LLM API 首次调用返回网络错误，第二次调用成功
- **THEN** 系统使用第二次调用的结果，流程正常继续

#### Scenario: 所有重试均失败
- **WHEN** LLM API 连续 3 次调用失败（1 次 + 2 次重试）
- **THEN** 系统记录 WARNING 日志，该批次新闻不产生情绪分数，流程继续

### Requirement: 系统 SHALL 处理 LLM 返回格式异常

系统 SHALL 对 LLM 返回的 JSON 进行结构校验。无法解析的返回结果 SHALL 被标记为中性（sentiment_score=0，classification="neutral"，confidence=0）。

#### Scenario: LLM 返回非法 JSON
- **WHEN** LLM 返回的文本无法解析为有效 JSON
- **THEN** 该批次所有新闻的情绪分数设为 0，记录 WARNING 日志

#### Scenario: LLM 返回缺少必要字段
- **WHEN** LLM 返回的 JSON 中某条新闻缺少 classification 字段
- **THEN** 该条新闻的情绪分数设为 0，其他新闻正常处理

### Requirement: 系统 SHALL 在 LLM API key 未配置时优雅降级

系统 SHALL 在启动时检查 LLM API key 环境变量。如果未配置，系统 SHALL 记录 WARNING 日志并跳过整个情绪分析步骤，不中断信号生成流程。

#### Scenario: API key 未配置
- **WHEN** 环境变量中未设置 LLM API key
- **THEN** 系统记录 WARNING "LLM API key not configured, sentiment analysis disabled"，情绪分析模块返回空结果

### Requirement: 系统 SHALL 支持配置 LLM 参数

系统 SHALL 从 config/settings.yaml 的 llm 配置段读取以下参数：provider（"openai" 或 "anthropic"，默认 "openai"）、model（模型名称，默认 "gpt-4o-mini"）、api_key_env（API key 环境变量名，默认 "OPENAI_API_KEY"）、batch_size（每批新闻数，默认 10）、max_retries（最大重试次数，默认 2）、temperature（生成温度，默认 0.1）。

#### Scenario: 使用 OpenAI 配置
- **WHEN** settings.yaml 定义 llm.provider="openai"、llm.model="gpt-4o-mini"
- **THEN** 系统使用 OpenAI SDK 调用 gpt-4o-mini 模型

#### Scenario: 使用 Anthropic 配置
- **WHEN** settings.yaml 定义 llm.provider="anthropic"、llm.model="claude-sonnet-4-6"、llm.api_key_env="ANTHROPIC_API_KEY"
- **THEN** 系统使用 Anthropic SDK 调用 Claude 模型
