"""Tests for backtest engine: T+1, limit-up/down, costs."""

import pytest
import pandas as pd
from src.backtest.costs import TransactionCosts
from src.backtest.order import OrderQueue
from src.backtest.portfolio import Portfolio


class TestTransactionCosts:
    def test_buy_cost(self):
        costs = TransactionCosts(stamp_tax=0.0005, commission=0.0003,
                                  commission_min=5.0, slippage=0.0015)
        result = costs.calculate_buy_cost(100_000)
        # commission = max(30, 5) = 30, slippage = 150
        assert abs(result - 180) < 0.01

    def test_sell_cost(self):
        costs = TransactionCosts(stamp_tax=0.0005, commission=0.0003,
                                  commission_min=5.0, slippage=0.0015)
        result = costs.calculate_sell_cost(100_000)
        # stamp = 50, commission = max(30, 5) = 30, slippage = 150
        assert abs(result - 230) < 0.01

    def test_minimum_commission(self):
        costs = TransactionCosts(commission=0.0003, commission_min=5.0, slippage=0)
        result = costs.calculate_buy_cost(1_000)  # commission = max(0.3, 5) = 5
        assert result == 5.0


class TestOrderQueue:
    def test_t_plus_1_blocking(self):
        oq = OrderQueue()
        oq.add_order("600000", "sell", 100, "2024-01-02")
        executable, deferred = oq.process_orders(
            "2024-01-02",
            prices={"600000": 10.0},
            prev_closes={"600000": 9.5},
            volumes={"600000": 1000},
            buy_dates={"600000": "2024-01-02"},  # bought today
        )
        assert len(executable) == 0
        assert len(deferred) == 1

    def test_t_plus_1_next_day_allowed(self):
        oq = OrderQueue()
        oq.add_order("600000", "sell", 100, "2024-01-02")
        executable, deferred = oq.process_orders(
            "2024-01-03",
            prices={"600000": 10.0},
            prev_closes={"600000": 9.5},
            volumes={"600000": 1000},
            buy_dates={"600000": "2024-01-02"},  # bought yesterday
        )
        assert len(executable) == 1

    def test_limit_up_blocks_buy(self):
        oq = OrderQueue(price_limit=0.10)
        oq.add_order("600000", "buy", 100, "2024-01-02")
        executable, deferred = oq.process_orders(
            "2024-01-02",
            prices={"600000": 11.0},   # +10% limit up
            prev_closes={"600000": 10.0},
            volumes={"600000": 1000},
            buy_dates={},
        )
        assert len(executable) == 0
        assert len(deferred) == 1

    def test_limit_down_blocks_sell(self):
        oq = OrderQueue(price_limit=0.10)
        oq.add_order("600000", "sell", 100, "2024-01-02")
        executable, deferred = oq.process_orders(
            "2024-01-02",
            prices={"600000": 9.0},   # -10% limit down
            prev_closes={"600000": 10.0},
            volumes={"600000": 1000},
            buy_dates={"600000": "2024-01-01"},
        )
        assert len(executable) == 0

    def test_suspended_stock(self):
        oq = OrderQueue()
        oq.add_order("600000", "buy", 100, "2024-01-02")
        executable, deferred = oq.process_orders(
            "2024-01-02",
            prices={"600000": 10.0},
            prev_closes={"600000": 10.0},
            volumes={"600000": 0},  # suspended
            buy_dates={},
        )
        assert len(executable) == 0
        assert len(deferred) == 1


class TestPortfolio:
    def test_buy_and_nav(self):
        p = Portfolio(initial_capital=100_000)
        p.buy("600000", 100, 10.0, 5.0, "2024-01-01")
        assert p.cash == 100_000 - 100 * 10 - 5
        p.update_prices({"600000": 11.0})
        assert p.nav == p.cash + 100 * 11.0

    def test_sell(self):
        p = Portfolio(initial_capital=100_000)
        p.buy("600000", 100, 10.0, 5.0, "2024-01-01")
        p.sell("600000", 100, 11.0, 5.0, "2024-01-02")
        assert "600000" not in p.positions
        assert p.cash > 100_000 - 10  # profit after costs

    def test_record_nav(self):
        p = Portfolio(initial_capital=100_000)
        p.record_nav("2024-01-01")
        assert len(p.nav_history) == 1
        assert p.nav_history[0]["nav"] == 100_000
