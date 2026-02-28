## Why

当前系统的商品因子（commodity factors）对所有金属采用相同的三个通用因子（价格动量、期货基差、库存变化），缺乏针对黄金的跨品种比价因子。金银比（Au/Ag）和金铜比（Au/Cu）是业界广泛使用的宏观风险指标，能有效捕捉避险情绪和经济周期信号，从而提升黄金子板块股票的选股精度。此外，当前数据管线未获取白银（ag）期货数据，且黄金库存数据映射缺失，需一并补齐。

## What Changes

- 新增白银（ag）期货数据获取，加入 `_metals` 列表和库存映射
- 修复 `fetch_inventory` 中缺少黄金（au）和白银（ag）的中文名映射
- 新增 `GoldSilverRatioFactor`（金银比因子）：计算 Au/Ag 价格比率的偏离度，高金银比看多黄金股
- 新增 `GoldCopperRatioFactor`（金铜比因子）：计算 Au/Cu 价格比率的变化率，金铜比上升反映避险情绪升温
- 在 `config/settings.yaml` 中为新因子添加可配置参数

## Capabilities

### New Capabilities
- `gold-cross-metal-factors`: 黄金跨品种比价因子（金银比、金铜比），包括因子计算逻辑、数据依赖和配置参数

### Modified Capabilities
- `data-pipeline`: 新增白银期货数据获取，修复黄金/白银库存数据映射
- `factor-engine`: 因子注册表需包含新的黄金跨品种因子

## Impact

- `src/factors/commodity.py` — 新增两个因子类
- `src/data/pipeline.py` — `_metals` 列表添加 `"ag"`
- `src/data/sources/akshare_source.py` — `fetch_inventory` 的 `metal_names` 添加 `"au"` 和 `"ag"` 映射
- `config/settings.yaml` — 新增金银比/金铜比相关配置参数
- `tests/` — 对应的单元测试
