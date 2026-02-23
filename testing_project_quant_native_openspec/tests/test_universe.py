"""Tests for universe filtering and sub-sector classification."""

import pytest
from src.universe.subsector import classify_subsector, classify_universe


class TestSubsectorClassification:
    def test_copper_classification(self):
        assert classify_subsector("紫金矿业") == "copper"
        assert classify_subsector("江西铜业") == "copper"

    def test_aluminum_classification(self):
        assert classify_subsector("中铝国际") == "aluminum"
        assert classify_subsector("南山铝业") == "aluminum"

    def test_gold_classification(self):
        assert classify_subsector("山东黄金") == "gold"
        assert classify_subsector("中金黄金") == "gold"

    def test_lithium_classification(self):
        assert classify_subsector("天齐锂业") == "lithium"
        assert classify_subsector("赣锋锂业") == "lithium"

    def test_cobalt_classification(self):
        assert classify_subsector("华友钴业") == "cobalt"

    def test_zinc_classification(self):
        assert classify_subsector("驰宏锌锗") == "zinc"

    def test_rare_earth_classification(self):
        assert classify_subsector("北方稀土") == "rare_earth"

    def test_unknown_classification(self):
        assert classify_subsector("某某科技") == "other"

    def test_classify_universe(self):
        stocks = [
            {"name": "紫金矿业", "code": "601899"},
            {"name": "天齐锂业", "code": "002466"},
            {"name": "某某公司", "code": "000001"},
        ]
        result = classify_universe(stocks)
        assert result[0]["subsector"] == "copper"
        assert result[1]["subsector"] == "lithium"
        assert result[2]["subsector"] == "other"
