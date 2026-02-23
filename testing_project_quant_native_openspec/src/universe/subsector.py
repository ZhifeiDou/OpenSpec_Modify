"""Sub-sector classification mapping for non-ferrous metals."""

from typing import Dict, List


SUBSECTOR_KEYWORDS: Dict[str, List[str]] = {
    "copper": ["铜", "紫金", "江西铜"],
    "aluminum": ["铝", "中铝", "南山铝", "云铝"],
    "gold": ["黄金", "金矿", "山东黄金", "紫金矿业", "中金"],
    "lithium": ["锂", "天齐", "赣锋", "融捷"],
    "cobalt": ["钴", "华友钴", "寒锐钴"],
    "zinc": ["锌", "驰宏锌锗", "株冶"],
    "rare_earth": ["稀土", "北方稀土", "五矿稀土", "广晟"],
}


def classify_subsector(stock_name: str, keywords: Dict[str, List[str]] = None) -> str:
    """Classify a stock into a sub-sector based on its name."""
    if keywords is None:
        keywords = SUBSECTOR_KEYWORDS
    for sector, kws in keywords.items():
        for kw in kws:
            if kw in stock_name:
                return sector
    return "other"


def classify_universe(stocks: list[dict], keywords: Dict[str, List[str]] = None) -> list[dict]:
    """Add sub-sector classification to a list of stocks."""
    for stock in stocks:
        stock["subsector"] = classify_subsector(stock.get("name", ""), keywords)
    return stocks
