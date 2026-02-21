"""配置中心 — 因子权重、回测参数、风控参数"""

import os

# ── 数据库路径 ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "quant.db")

# ── 有色金属板块股票池（申万二级行业：工业金属、贵金属、稀有金属、能源金属） ──
# 这里列出代表性标的，data_fetcher 会尝试从 AKShare 动态获取完整列表
DEFAULT_STOCK_POOL = [
    "601899",  # 紫金矿业
    "603993",  # 洛阳钼业
    "600489",  # 中金黄金
    "002460",  # 赣锋锂业
    "300750",  # 宁德时代（锂电龙头，关联）
    "600362",  # 江西铜业
    "601600",  # 中国铝业
    "000630",  # 铜陵有色
    "600547",  # 山东黄金
    "002466",  # 天齐锂业
    "600111",  # 北方稀土
    "000831",  # 五矿稀土
    "002340",  # 格林美
    "600259",  # 广晟有色
    "002171",  # 楚江新材
]

# ── 因子权重（各大类） ──
FACTOR_WEIGHTS = {
    "momentum": 0.20,
    "technical": 0.25,
    "value": 0.20,
    "quality": 0.15,
    "money_flow": 0.20,
}

# ── 子因子权重 ──
SUB_FACTOR_WEIGHTS = {
    # 动量因子
    "ret_5d": 0.30,
    "ret_20d": 0.40,
    "ret_60d": 0.20,
    "volume_change": 0.10,
    # 技术因子
    "macd": 0.20,
    "rsi": 0.20,
    "boll_position": 0.15,
    "ma_alignment": 0.25,
    "kdj": 0.20,
    # 价值因子
    "pe_percentile": 0.35,
    "pb_percentile": 0.35,
    "dividend_yield": 0.30,
    # 质量因子
    "roe": 0.40,
    "revenue_growth": 0.30,
    "profit_growth": 0.30,
    # 资金流向因子
    "main_net_inflow": 0.60,
    "north_inflow": 0.40,
}

# ── 策略参数 ──
STRATEGY = {
    "buy_threshold": 0.6,       # 综合评分 > 此值 → 买入
    "sell_threshold": -0.3,     # 综合评分 < 此值 → 卖出
    "max_positions": 5,         # 最大持仓数
    "position_method": "equal", # 等权分配
}

# ── 回测参数 ──
BACKTEST = {
    "start_date": "20240101",
    "end_date": "20250101",
    "initial_capital": 1_000_000,
    "commission_rate": 0.00025,  # 万2.5
    "stamp_tax": 0.001,         # 印花税千1（卖出时收取）
    "slippage": 0.001,          # 滑点 0.1%
}

# ── 风控参数 ──
RISK = {
    "stop_loss": -0.08,         # 个股止损线 -8%
    "max_drawdown_alert": -0.15, # 组合最大回撤预警 -15%
}
