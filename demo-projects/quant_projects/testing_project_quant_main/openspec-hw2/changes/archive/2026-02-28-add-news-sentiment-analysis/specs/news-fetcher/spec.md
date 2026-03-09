## ADDED Requirements

### Requirement: 系统 SHALL 从 AKShare 获取有色金属板块新闻

系统 SHALL 调用 AKShare 财经新闻接口，按配置的关键词（默认"有色金属"）获取板块相关新闻列表。系统 SHALL 提取每条新闻的标题、摘要、发布时间、来源字段。

#### Scenario: 正常获取板块新闻
- **WHEN** 系统触发新闻采集，且网络可用、AKShare 接口正常
- **THEN** 系统返回新闻列表，每条新闻包含 title、summary、published_at、source 字段

#### Scenario: AKShare 接口请求失败
- **WHEN** 系统调用 AKShare 接口时发生网络错误或接口异常
- **THEN** 系统记录 WARNING 级别日志，返回空新闻列表，不中断调用方流程

#### Scenario: 接口返回空数据
- **WHEN** AKShare 接口正常但无相关新闻
- **THEN** 系统记录 INFO 级别日志，返回空新闻列表

### Requirement: 系统 SHALL 将新闻与个股关联

系统 SHALL 根据股票池中个股的名称和代码，对每条新闻进行关联匹配。匹配规则为：新闻标题或摘要中包含个股名称或代码时，将该新闻关联到对应个股。

#### Scenario: 新闻匹配到具体个股
- **WHEN** 一条新闻的标题包含股票池中某只股票的名称（如"紫金矿业"）
- **THEN** 该新闻的 related_symbols 字段包含对应的股票代码

#### Scenario: 新闻匹配到多只个股
- **WHEN** 一条新闻同时提及多只个股
- **THEN** 该新闻的 related_symbols 字段包含所有匹配到的股票代码

#### Scenario: 新闻无法匹配到具体个股
- **WHEN** 一条新闻为板块级新闻（如"有色金属板块全线上涨"），未匹配到任何具体个股
- **THEN** 该新闻的 related_symbols 为空列表，标记 scope 为 "sector"

### Requirement: 系统 SHALL 对新闻去重

系统 SHALL 基于新闻标题和发布时间进行去重。已存在于数据库中的新闻 SHALL NOT 重复存储。

#### Scenario: 新闻已存在
- **WHEN** 采集到的新闻与数据库中已有新闻的标题和发布时间完全相同
- **THEN** 系统跳过该新闻，不重复写入

#### Scenario: 新闻不存在
- **WHEN** 采集到的新闻在数据库中不存在
- **THEN** 系统将该新闻写入 news 表

### Requirement: 系统 SHALL 将新闻持久化到 SQLite

系统 SHALL 将采集到的新闻存入本地 SQLite 数据库的 news 表。news 表 SHALL 包含字段：id (INTEGER PRIMARY KEY)、title (TEXT)、summary (TEXT)、published_at (TEXT ISO 8601)、source (TEXT)、related_symbols (TEXT JSON array)、scope (TEXT: "stock" 或 "sector")、fetched_at (TEXT ISO 8601)。

#### Scenario: 新闻写入数据库
- **WHEN** 系统完成一次新闻采集，获得 N 条新增新闻
- **THEN** news 表新增 N 条记录，每条记录的 fetched_at 为当前时间

### Requirement: 系统 SHALL 支持配置新闻采集参数

系统 SHALL 从 config/settings.yaml 的 news 配置段读取以下参数：keywords（搜索关键词列表，默认 ["有色金属"]）、lookback_hours（回溯时间窗口，默认 24）、max_articles（单次最大采集数，默认 50）。

#### Scenario: 使用默认配置
- **WHEN** settings.yaml 中未定义 news 配置段
- **THEN** 系统使用默认值：keywords=["有色金属"]、lookback_hours=24、max_articles=50

#### Scenario: 使用自定义配置
- **WHEN** settings.yaml 定义 news.lookback_hours=48
- **THEN** 系统采集最近 48 小时内的新闻

### Requirement: 系统 SHALL 遵守 API 频率限制

系统 SHALL 在连续 API 请求之间等待配置的延迟时间（复用现有 data.api_delay_seconds 配置，默认 0.5 秒）。

#### Scenario: 请求间隔控制
- **WHEN** 系统需要连续发送多个新闻接口请求
- **THEN** 每次请求之间至少等待 api_delay_seconds 秒
