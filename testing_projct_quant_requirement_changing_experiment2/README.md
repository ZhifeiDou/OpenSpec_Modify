# 需求变更对比实验：OpenSpec vs 直接编码

## 实验目的

验证在**需求变更**场景下，使用 OpenSpec 规格驱动工作流与传统"拿到需求直接写代码"方式的差异。

量化交易系统已有初始版本的 OpenSpec vs 非 OpenSpec 对比，本实验聚焦于**迭代维护阶段**——当产品经理提出需求变更时，两种方式在影响分析、需求覆盖、代码质量、可追溯性等维度的表现差异。

## 实验背景

**场景**：客户反馈在 2024 年有色金属市场剧烈波动期间（如铜价暴涨暴跌），系统的固定参数风控策略反应太迟钝，多次在大幅回撤后才触发止损。产品经理提出三项需求变更（详见 `requirement_change.md`）。

## 目录结构

```
testing_projct_quant_requirement_changing_experiment/
├── README.md                    # 本文件
├── requirement_change.md        # 统一的需求变更文档（两边使用同一份）
├── with_openspec/               # OpenSpec 版：使用规格驱动工作流实现变更
│   ├── src/、tests/、config/ ...
│   └── openspec/
│       ├── specs/               # 已有的8个主规格
│       └── changes/
│           └── volatility-adaptive-risk/  # 本次变更的全部 artifacts
├── without_openspec/            # 非 OpenSpec 版：直接编码实现变更
│   └── [所有项目文件，直接修改]
└── comparison/
    └── result.md                # 综合对比分析报告
```

## 实验方法

### OpenSpec 版（with_openspec/）
使用 OpenSpec 的变更工作流：
1. 创建变更（new）→ 生成 proposal.md
2. 分析用例 → 生成 usecases.md（含边界场景、异常流程）
3. 生成 delta specs（标注 MODIFIED/ADDED 的规格变更）
4. 技术设计 → 生成 design.md
5. 任务分解 → 生成 tasks.md
6. 按 tasks 逐项实现代码变更

### 非 OpenSpec 版（without_openspec/）
直接给 AI 同样的需求文档，让它直接编码实现。不使用任何规格框架。

## 对比维度

| 维度 | 说明 |
|------|------|
| 影响分析准确性 | 是否准确识别了所有受影响的模块？ |
| 需求覆盖完整性 | 3个需求是否全部实现？边界情况是否覆盖？ |
| 代码变更范围 | 修改了多少文件？新增了多少行？改动是否集中？ |
| 测试覆盖 | 新增了多少测试？覆盖了哪些场景？ |
| 文档/可追溯性 | 6个月后能否理解为什么做了这些改动？ |
| 回归风险 | 变更是否影响了不相关的现有功能？ |
| 可复现性 | 如果换一个开发者/AI继续迭代，能否快速理解上下文？ |

## 预期结论

OpenSpec 版将在影响分析、需求完整性、可追溯性、代码模块化和测试覆盖方面显著优于非 OpenSpec 版。详细对比见 `comparison/result.md`。
