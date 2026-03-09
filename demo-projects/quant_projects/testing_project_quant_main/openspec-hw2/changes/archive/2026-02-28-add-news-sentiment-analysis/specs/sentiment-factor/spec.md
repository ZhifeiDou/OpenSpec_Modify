## ADDED Requirements

### Requirement: 系统 SHALL 计算个股情绪因子分数

系统 SHALL 为股票池中每只股票计算情绪因子分数。计算方法：查询该股票在时间窗口内（由 sentiment.lookback_hours 控制，默认 72 小时）所有关联新闻的情绪分数，按时间衰减加权求和。时间衰减函数为指数衰减：weight = exp(-ln(2) * hours_since_publish / half_life)，半衰期由 sentiment.half_life_hours 控制（默认 24 小时）。

#### Scenario: 股票有多条关联新闻
- **WHEN** 某股票在 72 小时内有 3 条关联新闻，情绪分数分别为 +0.8（2 小时前）、-0.5（12 小时前）、+0.3（48 小时前）
- **THEN** 系统按时间衰减加权求和，近期新闻权重更高，得到综合情绪因子分数

#### Scenario: 股票无关联新闻
- **WHEN** 某股票在时间窗口内无任何关联新闻
- **THEN** 该股票的情绪因子分数为 0（中性）

#### Scenario: 股票仅有板块级新闻
- **WHEN** 某股票无个股级新闻，但有 2 条板块级新闻
- **THEN** 系统使用板块级新闻的情绪分数计算该股票的情绪因子，板块级新闻对所有个股生效

### Requirement: 系统 SHALL 将情绪因子注册到因子框架

系统 SHALL 将情绪因子注册到现有的 factor registry，类别为 "sentiment"。情绪因子 SHALL 与其他因子类别（commodity/fundamental/technical/flow/macro）一样参与多因子打分。情绪因子的类别权重 SHALL 通过 config/settings.yaml 的 factors.weights.sentiment 配置（默认 0.10）。

#### Scenario: 情绪因子参与打分
- **WHEN** factors.weights 配置中 sentiment=0.10
- **THEN** 情绪因子以 10% 的权重参与多因子综合得分计算

#### Scenario: 情绪因子权重为 0
- **WHEN** factors.weights.sentiment=0 或未配置
- **THEN** 情绪因子不参与打分，系统行为与未安装情绪分析模块时一致

### Requirement: 系统 SHALL 对情绪因子进行截面标准化

系统 SHALL 对情绪因子分数进行截面标准化（cross-sectional Z-score），与其他因子的标准化方式一致。标准化后的情绪因子值 SHALL 经过 MAD winsorize 处理（复用现有 factors.winsorize_mad_multiple 配置）。

#### Scenario: 截面标准化
- **WHEN** 股票池中 30 只股票都有情绪因子分数
- **THEN** 系统计算截面均值和标准差，将每只股票的情绪因子分数转换为 Z-score

#### Scenario: 有效值不足
- **WHEN** 股票池中仅 1 只股票有非零情绪因子分数
- **THEN** 系统跳过情绪因子的标准化，所有股票的标准化后情绪因子值为 0

### Requirement: 系统 SHALL 支持配置情绪因子参数

系统 SHALL 从 config/settings.yaml 的 sentiment 配置段读取以下参数：lookback_hours（回溯时间窗口，默认 72）、half_life_hours（时间衰减半衰期，默认 24）、min_news_count（最少新闻数阈值，低于此值时情绪因子设为 0，默认 1）。

#### Scenario: 使用默认配置
- **WHEN** settings.yaml 未定义 sentiment 配置段
- **THEN** 系统使用 lookback_hours=72、half_life_hours=24、min_news_count=1

#### Scenario: 自定义衰减参数
- **WHEN** settings.yaml 定义 sentiment.half_life_hours=12
- **THEN** 新闻情绪分数的衰减速度加快，12 小时前的新闻权重降为 50%

### Requirement: 系统 SHALL 在信号输出中包含情绪标签

系统 SHALL 在交易信号的输出中附带每只股票的情绪标签。情绪标签格式为：情绪方向（利多/利空/中性）+ 关键新闻标题（最多 1 条最近的新闻）。

#### Scenario: 信号附带利多情绪标签
- **WHEN** 某只股票的情绪因子分数为正，且最近新闻为"紫金矿业发现大型铜矿"
- **THEN** 信号输出中该股票附带标签 "利多: 紫金矿业发现大型铜矿"

#### Scenario: 无相关新闻
- **WHEN** 某只股票无关联新闻
- **THEN** 信号输出中该股票的情绪标签为 "中性: 无相关新闻"
